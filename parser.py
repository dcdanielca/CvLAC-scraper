import json

from bs4 import BeautifulSoup
from pprint import pprint
from urllib.request import urlopen


def parse(url):
    with urlopen(url) as response:
        soup = BeautifulSoup(response, 'html.parser')
        return {
            'formacion_acad': parse_formacion_acad(soup),
            'reconocimientos': parse_reconocimientos(soup)
        }


def parse_formacion_acad(soup):
    formacion_acad = []
    """
    <td>
        <a name="formacion_acad"></a>
        <table>
            ...
            <td>
                <b>Doctorado</b>
                UNIVERSIDAD DE CALDAS<br />
                ...
    """
    for b in soup.find(attrs={'name': 'formacion_acad'}).parent.find_all('b'):
        strs = list(b.parent.stripped_strings)
        """strs = [
            0: 'Doctorado',
            1: 'UNIVERSIDAD DE CALDAS',
            2: 'Doctorado en Diseño y Creación',
            3: 'Juliode2011 - Agostode 2017',
            4?: 'Interfaz Cerebro Ordenador para la Creación a través del Diseño...'
        ]"""
        formacion_acad.append({
            'titulo': strs[2],
            'institucion': strs[1],
            'periodo': strs[3],
            'trabajo_grado': strs[4] if len(strs) >= 5 else None
        })
    return formacion_acad


def parse_reconocimientos(soup):
    """
    <table>
        <tr><td><h3>Reconocimientos</h3></td></tr>
        <tr><td><li>Gran premio,Festival Mono Nuñez - de 1993</li></td></tr>
        <tr><td><li>Primer puesto conjunto instrumental,Festival Mono Nuñez - de 1985</li></td></tr>
        ...
    """
    return [
        li.get_text() for li in (
            soup.find(string='Reconocimientos').find_parent('table').find_all('li')
        )
    ]


cods_rh = ['0000419109']
url = 'http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh={}'
curriculums = {cod_rh: parse(url.format(cod_rh)) for cod_rh in cods_rh}
pprint(curriculums)

with open('curriculums.json', 'wt') as f:
    json.dump(curriculums, f)
