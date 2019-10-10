import json
import unicodedata

from bs4 import BeautifulSoup
from pprint import pprint
from urllib.request import urlopen


def parse(url):
    with urlopen(url) as response:
        soup = BeautifulSoup(response, 'html.parser')
        return {
            'formacion_acad': parse_formacion_acad(soup),
            'reconocimientos': parse_reconocimientos(soup),
            'eventos': parse_eventos(soup),
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
    return [li.get_text() for li in (
                soup.find(string='Reconocimientos').find_parent('table').find_all('li'))]


def parse_eventos(soup):
    """
    <td>
        <a name="evento"></a>
        <table>
            <table>
                <tr><td>
                    <b>1</b>&nbsp;<i><b>Nombre del evento:&nbsp;</b></i>Congreso
                    Internacional de Musicología, 200 años de Música en América Latina y el
                    Caribe&nbsp;
                    <i>Tipo de evento: </i>Congreso&nbsp;
                    <i>&Aacute;mbito: </i>&nbsp;
                    <i>Realizado el:2010-10-01 00:00:00.0,&nbsp;
                        &nbsp;
                        en &nbsp; - &nbsp;
                </td></tr>
                <tr><td>
                    <b>Productos asociados</b><br>
                    <ul>
                        <li><i>Nombre del producto:</i>Ópera Expandida en Colombia, de la
                            Narrativa Sonora a la Exploración Postmedial
                            <i>Tipo de producto:</i>Producción bibliográfica - Trabajos en
                            eventos (Capítulos de memoria) - Resumen
                        </li>
                    </ul>
                </td></tr>
                <tr><td></td></tr>
                <tr><td>
                    <b>Participantes</b><br>
                    <ul>
                        <li><i>Nombre: </i>HECTOR FABIO TORRES CARDONA
                            <i>Rol en el evento: </i>Asistente
                        </li>
                    </ul>
                </td></tr>
            </table>
            <table>
                <tr><td>
                    <b>2</b>
                    ...
    """
    eventos = []
    for table in soup.find(attrs={'name': 'evento'}).parent.find('table').find_all('table'):
        strs = list(table.stripped_strings)

        prefijo_fecha = 'Realizado el:'
        fecha_hora_lugar = next(str_ for str_ in strs if str_.startswith(prefijo_fecha))
        fecha = fecha_hora_lugar[len(prefijo_fecha) : len(prefijo_fecha) + len('AAAA-MM-DD')]

        eventos.append({
            'nombre': strs[strs.index('Nombre del evento:') + 1],
            'fecha': fecha,
            # Normalize to remove &nbsp;
            'lugar' : unicodedata.normalize(
                'NFKC', fecha_hora_lugar[fecha_hora_lugar.index('en ') + len('en '):]),
            'producto_asoc': (strs[strs.index('Nombre del producto:') + 1]
                              if 'Productos asociados' in strs else None),
            'institucion_asoc': (strs[strs.index('Nombre de la institución:') + 1]
                              if 'Instituciones asociadas' in strs else None),
        })
    return eventos


cods_rh = ['0000419109', '0000189758']
url = 'http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh={}'
curriculums = {cod_rh: parse(url.format(cod_rh)) for cod_rh in cods_rh}
pprint(curriculums)

with open('curriculums.json', 'wt') as f:
    json.dump(curriculums, f)
