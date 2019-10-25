import json
from urllib.request import urlopen

from bs4 import BeautifulSoup


def parsear(cod_rh):
    url = f'http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh={cod_rh}'
    with urlopen(url) as respuesta:
        # TODO: usar un parser más rápido
        soup = BeautifulSoup(respuesta, 'html.parser')
        return {
            #'formacion_academica': parsear_formacion_academica(soup),
            #'reconocimientos': parsear_reconocimientos(soup),
            #'eventos': parsear_eventos(soup),
            #'articulos': parsear_articulos(soup),
            'publicaciones': parsear_publicaciones(soup),
        }


def parsear_formacion_academica(soup):
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
    for b in (soup.find(attrs={'name': 'formacion_acad'})
                  .find_next_sibling('table')
                  .find_all('b')):
        strs = list(b.parent.stripped_strings)
        """strs = [
            0: 'Doctorado',
            1: 'UNIVERSIDAD DE CALDAS',
            2: 'Doctorado en Diseño y Creación',
            3: 'Juliode2011 - Agostode 2017',
            4?: 'Interfaz Cerebro Ordenador para la Creación a través del...',
        ]"""
        formacion_acad.append({
            'titulo': strs[2],
            'institucion': strs[1],
            'periodo': strs[3],
            'trabajo_grado': strs[4] if len(strs) >= 5 else None,
        })
    return formacion_acad


def parsear_reconocimientos(soup):
    """
    <table>
        <tr><td><h3>Reconocimientos</h3></td></tr>
        <tr><td><li>Gran premio,Festival Mono Nuñez - de 1993</li></td></tr>
        <tr><td><li>Primer puesto conjunto instrumental,...<li></td></tr>
        ...
    """
    return [li.get_text() for li in (soup.find('h3', string='Reconocimientos')
                                         .find_parent('table')
                                         .find_all('li'))]


def parsear_eventos(soup):
    eventos = []
    """
    <a name="evento"></a>
    <table>
        <table>
            <tr><td>
                <img>
                <b>57</b>&nbsp;<i><b>Nombre del evento:&nbsp;</b></i>II
                Festival Internacional de la Imagen&nbsp;
                <i>Tipo de evento: </i>Seminario&nbsp;
                <i>&Aacute;mbito: </i>Internacional&nbsp;
                <i>Realizado el:1998-01-01 00:00:00.0,&nbsp;
                   1998-04-15 00:00:00.0 &nbsp;
                   en MANIZALES &nbsp; - Fondo Cultural del Café &nbsp;
            </td></tr>
            <tr><td>
                <b>Productos asociados</b><br>
                <ul>
                    <li>
                        <i>Nombre del producto:</i>Diseño de indicadores...
                        <i>Tipo de producto:</i>Producción bibliográfica...
                    </li>
                </ul>
            </td></tr>
            <tr><td>
                <b>Instituciones asociadas</b><br>
                <ul>
                    <li>
                        <i>Nombre de la instituci&oacute;n:</i>UNIVERSIDAD...
                        <i>Tipo de vinculaci&oacute;n</i>Patrocinadora
                    </li>
                </ul>
            </td></tr>
            <tr><td>
                <b>Participantes</b><br>
                <ul>
                    <li>
                        <i>Nombre: </i>FELIPE CESAR LONDONO LOPEZ
                        <i>Rol en el evento: </i>Organizador , Ponente
                    </li>
                </ul>
            </td></tr>
        </table>
            ...
        </table>
        ...
    """
    for table in (soup.find(attrs={'name': 'evento'})
                      .find_next_sibling('table')
                      .find_all('table')):
        fecha, lugar = _parsear_fecha_lugar_evento(table)
        i_producto_asoc = table.find('i', string='Nombre del producto:')
        i_institucion_asoc = table.find('i',string='Nombre de la institución:')
        eventos.append({
            'nombre': table.find('b', string='Nombre del evento:\xa0')
                           .parent
                           .next_sibling
                           .strip(),
            'fecha': fecha,  # de inicio, a veces hay también de fin
            'lugar' : lugar,
            'producto_asoc': i_producto_asoc.next_sibling.strip()
                             if i_producto_asoc else None,
            'institucion_asoc': i_institucion_asoc.next_sibling.strip()
                                if i_institucion_asoc else None,
        })
    return eventos


def _parsear_fecha_lugar_evento(table):
    prefijo_fecha = 'Realizado el:'
    fecha_lugar = (
        table.find('i', string=(lambda s: s.startswith(prefijo_fecha)))
             .string.strip())
    # fecha_lugar = 'Realizado el:2013-11-27 00:00:00.0, ...'
    #               ' 2013-11-29 00:00:00.0 ...'
    #               ' en MADRID \xa0 - Central de Diseño, Matadero Madrid.'
    fecha = fecha_lugar[len(prefijo_fecha) : len(prefijo_fecha)
                                             + len('AAAA-MM-DD')]
    lugar = (fecha_lugar[fecha_lugar.index(' en ') + len(' en ') :]
                        .replace(' \xa0', ''))
    return (fecha, lugar) if lugar != ' -' else (fecha, None)


def parsear_articulos(soup):
    articulos = []
    """
    <a name="articulos"></a>
    <table>
        ...
        <blockquote>
            FELIPE CESAR LONDONO LOPEZ,
            ...
        </blockquote>
        ...
        <blockquote>
            ...
    """
    for bq in (soup.find(attrs={'name': 'articulos'})
                   .find_next_sibling('table')
                   .find_all('blockquote')):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'FELIPE CESAR LONDONO LOPEZ,',
            'JOSEP MARIA MONGUET F,',
            'CARLOS ANDRES CORDOBA CELY,',
            '"Análisis de Cocitación de Autor en el Modelo de Aceptación..."',
            '. En: España',
            'Revista Espanola de Documentacion Cientifica',
            'ISSN:\xa00210-0614',
            'ed:\xa0Consejo superior de investigaciones científicas de Madrid',
            'v.35',
            'fasc.2',
            'p.238',
            '- 261',
            ',2012,',
            'DOI:\xa010.3989/redc.2012.2.864',
            'Palabras:',
            'Modelo de aceptación tecnológico,',
            'visualización de dominios de conocimiento,',
            'redes Pathfinder,'
        ]"""
        i_titulo, titulo = _parsear_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = _parsear_campo(lineas, prefijo='. En: ',con_indice=True)
        revista = (lineas[i_pais + 1]
                   if not lineas[i_pais + 1].startswith('ISSN:') else None)
        pags, año = _parsear_pags_año(
            lineas, prefijo_pags0='p.', año_vacio=',,')
        articulos.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais,
            'revista': revista,
            'ISSN': _parsear_campo(lineas, prefijo='ISSN:'),
            'editorial': _parsear_campo(lineas, prefijo='ed:'),
            'version': _parsear_version_articulo(lineas),
            'paginas': pags,
            'año': año,
            'DOI': _parsear_campo(lineas, prefijo='DOI:'),
        })
    return articulos


def _split_strip_lines(str_):
    return list(filter(None, (linea.strip() for linea in str_.splitlines())))


def _parsear_campo(lineas, prefijo, con_indice=False):
    indice, campo = next(
        (i, (linea[len(prefijo):].lstrip() or None))
        for (i, linea) in enumerate(lineas) if linea.startswith(prefijo))
    return (indice, campo) if con_indice else campo


def _parsear_version_articulo(lineas):
    return 'v.{} fasc.{}'.format(
        _parsear_campo(lineas, prefijo='v.') or 'N/A',
        _parsear_campo(lineas, prefijo='fasc.') or 'N/A')


def parsear_publicaciones(soup):
    return {
        #'libros': parsear_libros(soup),
        #'capitulos_libros': parsear_capitulos_libros(soup),
        #'demas_trabajos': parsear_demas_trabajos(soup),
        'textos_pubs_no_cientificas': parsear_textos_pubs_no_cientificas(soup),
    }


def parsear_libros(soup):
    libros = []
    """
    <a name="libros"></a>
    <table>
        ...
        <blockquote>
            HECTOR FABIO TORRES CARDONA,
            ...
        </blockquote>
        ...
        <blockquote>
            ...
    """
    for bq in (soup.find(attrs={'name': 'libros'})
                   .find_next_sibling('table')
                   .find_all('blockquote')):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'HECTOR FABIO TORRES CARDONA,',
            '"Cuerdas Típicas Colombianas"',
            'En: Colombia',
            '2005.',
            'ed:Centre Editorial Universidad De Caldas',
            'ISBN:\xa0958-8231-44-2',
            'v. 0',
            'pags.\xa0474',
            'Palabras:',
            'música colombiana,',
            'cuerdas típicas,',
            'Areas:',
            'Humanidades -- Arte -- Teatro, dramaturgia o artes escénicas,',
            'Sectores:',
            'Edición, impresión, reproducción y grabación industriales de...',
            'Productos y servicios de recreación,culturales, artísticos y...'
        ]"""
        i_titulo, titulo = _parsear_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = _parsear_campo(lineas, prefijo='En: ', con_indice=True)
        str_pags = _parsear_campo(lineas, prefijo='pags.')
        libros.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais,
            'año': int(lineas[i_pais + 1].rstrip('.')),
            'editorial': _parsear_campo(lineas, prefijo='ed:'),
            'ISBN': _parsear_campo(lineas, prefijo='ISBN:'),
            # TODO: convertir a número?
            'version': _parsear_campo(lineas, prefijo='v.'),
            'paginas': int(str_pags) if str_pags else None,
        })
    return libros


def parsear_capitulos_libros(soup):
    capitulos = []
    """
    <a name="capitulos"></a>
    <table>
        ...
        <blockquote>
            Tipo: Capítulo de libro<br>
            ...
        </blockquote>
        ...
        <blockquote>
            ...
    """
    for bq in (soup.find(attrs={'name': 'capitulos'})
                   .find_next_sibling('table')
                   .find_all('blockquote')):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'Tipo: Otro capítulo de libro publicado',
            'FELIPE CESAR LONDONO LOPEZ,',
            'Tipo: Otro capítulo de libro publicado',
            'ADRIANA GOMEZ A,',
            'Tipo: Otro capítulo de libro publicado',
            'MARIO H VALENCIA G,',
            '"Interacción, espacio público y nuevas tecnologías"',
            'Diseño + Segundo Encuentro Nacional De Investigacion En Diseño',
            '. En: Colombia',
            'ISBN:\xa0958-9279-85-6',
            'ed:\xa0Universidad Icesi',
            ', v.1',
            ', p.',
            '-',
            '1',
            ',2006',
            'Palabras:',
            'Interacción y diseño,',
            'Diseño Visual,',
            'Ciudad,',
            'Espacio Público,',
            'Nuavas tecnologías,',
            'Areas:',
            'Ciencias Sociales -- Ciencias de la Educación -- Educación...',
            'Humanidades -- Idiomas y Literatura -- Lingüística,',
            'Ciencias Sociales -- Periodismo y Comunicaciones -- Medios y...'
        ]"""
        i_titulo_capitulo, titulo_capitulo = _parsear_campo(
            lineas, prefijo='"', con_indice=True)
        pags, año = _parsear_pags_año(
            lineas, prefijo_pags0=', p.', año_vacio=',')
        capitulos.append({
            'autores': _parsear_autores_capitulos(lineas, i_titulo_capitulo),
            'titulo_capitulo': titulo_capitulo.strip('"'),
            'titulo_libro': lineas[i_titulo_capitulo + 1],
            'pais': _parsear_campo(lineas, prefijo='. En:'),
            'ISBN': _parsear_campo(lineas, prefijo='ISBN:'),
            'editorial': _parsear_campo(lineas, prefijo='ed:'),
            # TODO: convertir a número?
            'version': _parsear_campo(lineas, prefijo=', v.'),
            'paginas': pags,
            'año': año,
        })
    return capitulos


def _parsear_autores_capitulos(lineas, i_titulo_capitulo):
    # TODO: dejar como lista?
    return (''.join(linea for linea in lineas[:i_titulo_capitulo]
                    if not linea.startswith('Tipo:'))
              .rstrip(','))


def _parsear_pags_año(lineas, prefijo_pags0, año_vacio):
    """Para artículos y capítulos de libros."""
    i_pags0, pags0 = _parsear_campo(lineas, prefijo_pags0, con_indice=True)
    i_pags1, i_año = ((i_pags0 + 1, i_pags0 + 2)
                      if lineas[i_pags0 + 2].startswith(',')
                      else (i_pags0 + 2, i_pags0 + 3))
    pags = f'{pags0 or ""} - {lineas[i_pags1].lstrip("- ")}'
    año = int(lineas[i_año].strip(',')) if lineas[i_año] != año_vacio else None
    return pags, año


def parsear_demas_trabajos(soup):
    return []


def parsear_textos_pubs_no_cientificas(soup):
    textos = []
    """
    <table>
        <tr><td><h3 id="textos"></h3></td></tr>
        ...
        <tr><td><blockquote>
            FELIPE CESAR LONDONO LOPEZ,
            ...
        </blockquote></td></tr>
        ...
    """
    for bq in (soup.find('h3', id='textos')
                   .find_parent('table')
                   .find_all('blockquote')):
        lineas = _split_strip_lines(bq.get_text())
        """
        lineas = [
            'FELIPE CESAR LONDONO LOPEZ,',
            '"Diseño, arte y tecnología"',
            'En: Colombia.',
            '2010.',
            'Facultad Para Educar.',
            'ISSN:\xa01794-9858',
            'p.4',
            '- 9',
            'v.18',
            'Palabras:',
            'Diseño,',
            'Tecnologías,',
            'Arte Digital,',
            'Arte y nuevos medios,',
            'Areas:',
            'Humanidades -- Otras Humanidades -- Otras Humanidades,'
        ]"""
        i_titulo, titulo = _parsear_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = _parsear_campo(lineas, prefijo='En: ', con_indice=True)
        i_pags0, pags0 = _parsear_campo(lineas, prefijo='p.', con_indice=True)
        textos.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais.rstrip('.'),
            'año': int(lineas[i_pais + 1].rstrip('.')),
            'revista': lineas[i_pais + 2].rstrip('.'),
            'ISSN': _parsear_campo(lineas, prefijo='ISSN:'),
            'paginas': f'{pags0 or ""} - {lineas[i_pags0 + 1].lstrip("- ")}',
            # TODO: convertir a número?
            'version': _parsear_campo(lineas, prefijo='v.'),
        })
    return textos


if __name__ == '__main__':
    cods_rh = ['0000419109', '0000189758']
    curriculums = {cod_rh: parsear(cod_rh) for cod_rh in cods_rh}
    with open('curriculums.json', 'wt') as f:
        json.dump(curriculums, f)
