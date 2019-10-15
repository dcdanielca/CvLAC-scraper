import json

from bs4 import BeautifulSoup
from pprint import pprint
from urllib.request import urlopen


def parsear(url):
    with urlopen(url) as respuesta:
        soup = BeautifulSoup(respuesta, 'html.parser')
        return {
            'formacion_acad': parsear_formacion_acad(soup),
            'reconocimientos': parsear_reconocimientos(soup),
            'eventos': parsear_eventos(soup),
            'articulos': parsear_articulos(soup),
        }


def parsear_formacion_acad(soup):
    formacion_acad = []
    """
    <a name="formacion_acad"></a>
    <table>
        ...
        <td>
            <b>Doctorado</b>
            UNIVERSIDAD DE CALDAS<br />
            ...
        </td>
        <td>
            <b>Maestría/Magister</b>
            UNIVERSIDAD DE CALDAS<br />
            ...
        </td>
        ...
    """
    for b in soup.find(attrs={'name': 'formacion_acad'}).find_next_sibling('table').find_all('b'):
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
            'periodo': strs[3],  # TODO: convertir de string a dos fechas?
            'trabajo_grado': strs[4] if len(strs) >= 5 else None,
        })
    return formacion_acad


def parsear_reconocimientos(soup):
    """
    <table>
        <tr><td><h3>Reconocimientos</h3></td></tr>
        <tr><td><li>Gran premio,Festival Mono Nuñez - de 1993</li></td></tr>
        <tr><td><li>Primer puesto conjunto instrumental,Festival Mono Nuñez - de...</li></td></tr>
        ...
    """
    return [li.get_text() for li in (
                soup.find(string='Reconocimientos').find_parent('table').find_all('li'))]


def _parsear_fecha_lugar_evento(strs):
    prefijo_fecha = 'Realizado el:'
    fecha_hora_lugar = next(str_ for str_ in strs if str_.startswith(prefijo_fecha))
    fecha = fecha_hora_lugar[len(prefijo_fecha) : len(prefijo_fecha) + len('AAAA-MM-DD')]
    lugar = fecha_hora_lugar[fecha_hora_lugar.index('en ') + len('en ') :].replace(' \xa0', '')
    return (fecha, lugar) if lugar != ' -' else (fecha, None)


def parsear_eventos(soup):
    """
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
            ...
        </table>
        ...
    """
    eventos = []
    for table in soup.find(attrs={'name': 'evento'}).find_next_sibling('table').find_all('table'):
        strs = list(table.stripped_strings)
        """strs = [
            '1',
            'Nombre del evento:',
            'Congreso Internacional de Musicología, 200 años de Música en América Latina y el...',
            'Tipo de evento:',
            'Congreso',
            'Ámbito:',
            'Realizado el:2010-10-01 00:00:00.0,\xa0\r\n...\xa0\r\n...en  \xa0 -',
            'Productos asociados',
            'Nombre del producto:',
            'Ópera Expandida en Colombia, de la Narrativa Sonora a la Exploración Postmedial',
            'Tipo de producto:',
            'Producción bibliográfica - Trabajos en eventos (Capítulos de memoria) - Resumen',
            'Participantes',
            'Nombre:',
            'HECTOR FABIO TORRES CARDONA',
            'Rol en el evento:',
            'Asistente'
        ]"""
        fecha, lugar = _parsear_fecha_lugar_evento(strs)
        eventos.append({
            'nombre': strs[strs.index('Nombre del evento:') + 1],
            'fecha': fecha,  # TODO: convertir de string a fecha?
            'lugar' : lugar,
            'producto_asoc': (strs[strs.index('Nombre del producto:') + 1]
                              if 'Productos asociados' in strs else None),
            'institucion_asoc': (strs[strs.index('Nombre de la institución:') + 1]
                              if 'Instituciones asociadas' in strs else None),
        })
    return eventos


"""
def _parsear_campo(lineas, prefijo):
    return next((i, linea[len(prefijo):]) for (i, linea) in enumerate(lineas)
                if linea.startswith(prefijo))
"""


def parsear_articulos(soup):
    articulos = []
    """
    <a name="articulos"></a>
    <table>
        ...
        <blockquote>
            HECTOR FABIO TORRES CARDONA,
            "DIABÓLICO"
            . En: Colombia&nbsp;<br>
            Aleph&nbsp;
            <i>ISSN:</i>&nbsp;0120-0216&nbsp;
            <i>ed:</i>&nbsp;Universidad Nacional de Colombia<br>
            <i>v.</i>96
            <i>fasc.</i>43
            p.31
            - 34
            ,1996,
            <i>&nbsp;DOI:&nbsp;</i>
            <br><b>Palabras: </b><br>
            Aleph 96,
            <br><b>Sectores: </b><br>
            Otros sectores - Otro,
        </blockquote>
        ...
        <blockquote>
            ...
    """
    for bq in soup.find(attrs={'name': 'articulos'}).find_next_sibling('table').find_all('blockquote'):
        lineas = list(filter(None, (linea.strip() for linea in bq.get_text().splitlines())))
        """lineas = [
            'HECTOR FABIO TORRES CARDONA,',
            i_titulo: '"DIABÓLICO"',
            '. En: Colombia',
            'Aleph',
            'ISSN:\xa00120-0216',
            'ed:\xa0Universidad Nacional de Colombia',
            'v.96',
            'fasc.43',
            'p.31',
            '- 34',
            ',1996,',
            'DOI:',
            'Palabras:',
            'Aleph 96,',
            'Sectores:',
            'Otros sectores - Otro,'
        ]"""
        i_titulo = next(i for (i, line) in enumerate(lineas) if line.startswith('"'))
        # TODO: buscar por prefijos en vez de índices para que no sea tan frágil?
        articulos.append({
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),  # TODO: convertir a lista?
            'titulo': lineas[i_titulo].strip('"'),
            'pais': lineas[i_titulo + 1][len('. En: '):],
            'revista': lineas[i_titulo + 2],
            'ISSN': lineas[i_titulo + 3][len('ISSN:\xa0'):],
            'editorial': lineas[i_titulo + 4][len('ed:\xa0'):] or None,
            'version': f"{lineas[i_titulo + 5]} {lineas[i_titulo + 6]}",  # con fasc.
            'paginas': f"{lineas[i_titulo + 7][len('p.'):]} {lineas[i_titulo + 8]}",
            'año': int(lineas[i_titulo + 9].strip(',')),
            'DOI': lineas[i_titulo + 10][len('DOI:'):].lstrip('\xa0') or None,
        })
    return articulos


if __name__ == '__main__':
    cods_rh = ['0000419109', '0000189758']
    url = 'http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh={}'
    curriculums = {cod_rh: parsear(url.format(cod_rh)) for cod_rh in cods_rh}
    #pprint(curriculums)
    with open('curriculums.json', 'wt') as f:
        json.dump(curriculums, f)
