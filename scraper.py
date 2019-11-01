import json
import sys
from urllib.request import urlopen

from bs4 import BeautifulSoup

try:
    from tqdm import tqdm
except ImportError:
    tqdm = iter


def extraer_curriculum(cod_rh):
    url = f'http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh={cod_rh}'
    with urlopen(url) as respuesta:
        # Se podría usar un parser más rápido:
        soup = BeautifulSoup(respuesta, 'html.parser')
        return {
            'formacion_academica': extraer_formacion_academica(soup),
            'reconocimientos': extraer_reconocimientos(soup),
            'eventos_cientificos': extraer_eventos_cientificos(soup),
            'articulos': extraer_articulos(soup),
            'libros': extraer_libros(soup),
            'capitulos_libros': extraer_capitulos_libros(soup),
            'demas_trabajos': extraer_demas_trabajos(soup),
            'textos_pubs_no_cientificas': extraer_textos_pubs_no_cientificas(soup),
            'softwares': extraer_softwares(soup),
            'obras_productos': extraer_obras_productos(soup),
            'proyectos': extraer_proyectos(soup),
        }


def extraer_formacion_academica(soup):
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
    table = _find_table_next_to_tag(soup, attrs={'name': 'formacion_acad'})
    if table is None:
        return []
    formacion_acad = []
    for b in table.find_all('b'):
        strs = list(b.parent.stripped_strings)
        """strs = [
            0: 'Doctorado',
            1: 'UNIVERSIDAD DE CALDAS',
            2: 'Doctorado en Diseño y Creación',
            3: 'Juliode2011 - Agostode 2017',
            4?: 'Interfaz Cerebro Ordenador para la Creación a...',
        ] | [
            0: 'Secundario',
            1: 'Instituto Nacional Los Fundadores',
            2: 'Enerode1973 - de 1978'
        ]"""
        if len(strs) != 3:  # nos interesan son los títulos de edu superior
            formacion_acad.append({
                'titulo': strs[2],
                'institucion': strs[1],
                'periodo': strs[3],
                'trabajo_grado': strs[4] if len(strs) >= 5 else None,
            })
    return formacion_acad


def _find_table_next_to_tag(soup, **kwargs):
    tag = soup.find(**kwargs)
    return None if tag is None else tag.find_next_sibling('table')


def extraer_reconocimientos(soup):
    """
    <table>
        <tr><td><h3>Reconocimientos</h3></td></tr>
        <tr><td><li>Gran premio,Festival Mono Nuñez...</li></td></tr>
        <tr><td><li>Primer puesto conjunto...<li></td></tr>
        ...
    """
    e_reconocimientos = soup.find('h3', string='Reconocimientos')
    if e_reconocimientos is None:
        return []
    return [li.get_text() for li in (
               e_reconocimientos.find_parent('table').find_all('li'))]

def extraer_eventos_cientificos(soup):
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
                        <i>Nombre del producto:</i>Diseño de...
                        <i>Tipo de producto:</i>Producción...
                    </li>
                </ul>
            </td></tr>
            <tr><td>
                <b>Instituciones asociadas</b><br>
                <ul>
                    <li>
                        <i>Nombre de la instituci&oacute;n:</i>UNIVER...
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
    table = _find_table_next_to_tag(soup, attrs={'name': 'evento'})
    if table is None:
        return []
    eventos = []
    for table in table.find_all('table'):
        fecha, lugar = _extraer_fecha_lugar_evento(table)
        i_producto_asoc = table.find('i', string='Nombre del producto:')
        i_institucion_asoc = table.find('i',string='Nombre de la institución:')
        eventos.append({
            'nombre': table.find('b', string='Nombre del evento:\xa0')
                           .parent
                           .next_sibling
                           .strip(),
            'fecha': fecha,  # de inicio; a veces hay también de fin
            'lugar' : lugar,
            'producto_asoc': i_producto_asoc.next_sibling.strip()
                             if i_producto_asoc else None,
            'institucion_asoc': i_institucion_asoc.next_sibling.strip()
                                if i_institucion_asoc else None,
        })
    return eventos


def _extraer_fecha_lugar_evento(table):
    prefijo_fecha = 'Realizado el:'
    fecha_lugar = (
        table.find('i', string=(lambda s: s.startswith(prefijo_fecha)))
             .string.strip())
    # fecha_lugar = 'Realizado el:2013-11-27 00:00:00.0, ...'
    #               ' 2013-11-29 00:00:00.0 ...'
    #               ' en MADRID \xa0 - Central de Diseño, Matadero Madrid.'
    fecha = fecha_lugar[
        len(prefijo_fecha) : len(prefijo_fecha) + len('AAAA-MM-DD')]
    lugar = (fecha_lugar[fecha_lugar.index(' en ') + len(' en ') :]
                 .replace(' \xa0', ''))
    return (fecha, lugar) if lugar != ' -' else (fecha, None)


def extraer_articulos(soup):
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
    table = _find_table_next_to_tag(soup, attrs={'name': 'articulos'})
    if table is None:
        return []
    articulos = []
    for bq in table.find_all('blockquote'):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'FELIPE CESAR LONDONO LOPEZ,',
            'JOSEP MARIA MONGUET F,',
            'CARLOS ANDRES CORDOBA CELY,',
            '"Análisis de Cocitación de Autor en el Modelo de..."',
            '. En: España',
            'Revista Espanola de Documentacion Cientifica',
            'ISSN:\xa00210-0614',
            'ed:\xa0Consejo superior de investigaciones científicas...',
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
        i_titulo, titulo = _extraer_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = _extraer_campo(lineas, prefijo='. En:',con_indice=True)
        revista = (lineas[i_pais + 1]
                   if not lineas[i_pais + 1].startswith('ISSN:') else None)
        pags, año = _extraer_pags_año(
            lineas, prefijo_pags0='p.', año_vacio=',,')
        articulos.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais,
            'revista': revista,
            'ISSN': _extraer_campo(lineas, prefijo='ISSN:'),
            'editorial': _extraer_campo(lineas, prefijo='ed:'),
            'version': _extraer_version_articulo(lineas),
            'paginas': pags,
            'año': año,
            'DOI': _extraer_campo(lineas, prefijo='DOI:'),
        })
    return articulos


def _split_strip_lines(str_):
    return list(filter(None, (linea.strip() for linea in str_.splitlines())))


def _extraer_campo(lineas, prefijo, con_indice=False):
    indice, campo = next(
        (i, (linea[len(prefijo):].lstrip().rstrip(',.') or None))
        for (i, linea) in enumerate(lineas) if linea.startswith(prefijo))
    return (indice, campo) if con_indice else campo


def _extraer_version_articulo(lineas):
    return 'v.{} fasc.{}'.format(
        _extraer_campo(lineas, prefijo='v.') or 'N/A',
        _extraer_campo(lineas, prefijo='fasc.') or 'N/A')


def extraer_libros(soup):
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
    table = _find_table_next_to_tag(soup, attrs={'name': 'libros'})
    if table is None:
        return []
    libros = []
    for bq in table.find_all('blockquote'):
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
            'Humanidades -- Arte -- Teatro, dramaturgia o artes...,',
            'Sectores:',
            'Edición, impresión, reproducción y grabación...',
            'Productos y servicios de recreación,culturales, ...'
        ]"""
        i_titulo, titulo = _extraer_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = _extraer_campo(lineas, prefijo='En:', con_indice=True)
        str_pags = _extraer_campo(lineas, prefijo='pags.')
        libros.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais,
            'año': int(lineas[i_pais + 1].rstrip('.')),
            'editorial': _extraer_campo(lineas, prefijo='ed:'),
            'ISBN': _extraer_campo(lineas, prefijo='ISBN:'),
            # TODO: convertir a número?
            'version': _extraer_campo(lineas, prefijo='v.'),
            'paginas': int(str_pags) if str_pags else None,
        })
    return libros


def extraer_capitulos_libros(soup):
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
    table = _find_table_next_to_tag(soup, attrs={'name': 'capitulos'})
    if table is None:
        return []
    capitulos = []
    for bq in table.find_all('blockquote'):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'Tipo: Otro capítulo de libro publicado',
            'FELIPE CESAR LONDONO LOPEZ,',
            'Tipo: Otro capítulo de libro publicado',
            'ADRIANA GOMEZ A,',
            'Tipo: Otro capítulo de libro publicado',
            'MARIO H VALENCIA G,',
            '"Interacción, espacio público y nuevas tecnologías"',
            'Diseño + Segundo Encuentro Nacional De Investigacion...',
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
            'Ciencias Sociales -- Ciencias de la Educación...',
            'Humanidades -- Idiomas y Literatura -- Lingüística,',
            'Ciencias Sociales -- Periodismo y Comunicaciones...'
        ]"""
        i_titulo_capitulo, titulo_capitulo = _extraer_campo(
            lineas, prefijo='"', con_indice=True)
        pags, año = _extraer_pags_año(
            lineas, prefijo_pags0=', p.', año_vacio=',')
        capitulos.append({
            'autores': _extraer_autores_capitulos(lineas, i_titulo_capitulo),
            'titulo_capitulo': titulo_capitulo.strip('"'),
            'titulo_libro': lineas[i_titulo_capitulo + 1],
            'pais': _extraer_campo(lineas, prefijo='. En:'),
            'ISBN': _extraer_campo(lineas, prefijo='ISBN:'),
            'editorial': _extraer_campo(lineas, prefijo='ed:'),
            # TODO: convertir a número?
            'version': _extraer_campo(lineas, prefijo=', v.'),
            'paginas': pags,
            'año': año,
        })
    return capitulos


def _extraer_autores_capitulos(lineas, i_titulo_capitulo):
    # TODO: dejar como lista?
    return (''.join(linea for linea in lineas[:i_titulo_capitulo]
                    if not linea.startswith('Tipo:'))
              .rstrip(','))


def _extraer_pags_año(lineas, prefijo_pags0, año_vacio):
    """Para artículos y capítulos de libros."""
    i_pags0, pags0 = _extraer_campo(lineas, prefijo_pags0, con_indice=True)
    i_pags1, i_año = ((i_pags0 + 1, i_pags0 + 2)
                      if lineas[i_pags0 + 2].startswith(',')
                      else (i_pags0 + 2, i_pags0 + 3))
    pags = f'{pags0 or ""} - {lineas[i_pags1].lstrip("- ")}'
    año = int(lineas[i_año].strip(',')) if lineas[i_año] != año_vacio else None
    return pags, año


def extraer_demas_trabajos(soup):
    """
    <td>
        <a name="demas_trabajos"></a>
        <table>
            ...
            <blockquote>
                HECTOR FABIO TORRES CARDONA,
                ...
            </blockquote>
        ...
    """
    e_trabajos = soup.find(attrs={'name': 'demas_trabajos'})
    if e_trabajos is None:
        return []
    trabajos = []
    for bq in (e_trabajos
                   .parent
                   .find_all('blockquote')):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'HECTOR FABIO TORRES CARDONA,',
            'CD: ARS NOVA',
            '. En: Colombia,',
            ',2002,',
            'finalidad: Difusión del trabajo en cuerdas típicas...',
            'Areas:',
            'Humanidades -- Arte -- Teatro, dramaturgia o artes...,',
            'Sectores:',
            'Edición, impresión, reproducción y grabación industriales...'
        ]"""
        i_pais, pais = _extraer_campo(lineas, prefijo='. En:', con_indice=True)
        str_año = lineas[i_pais + 1].strip(',')
        trabajos.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[: i_pais - 1]).rstrip(','),
            'titulo': lineas[i_pais - 1],
            'pais': pais,
            'año': int(str_año) if str_año else None,
            'finalidad': _extraer_campo(lineas, prefijo='finalidad:'),
        })
    return trabajos


def extraer_textos_pubs_no_cientificas(soup):
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
    e_textos = soup.find(id='textos')
    if e_textos is None:
        return []
    textos = []
    for bq in (e_textos
                   .find_parent('table')
                   .find_all('blockquote')):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
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
        i_titulo, titulo = _extraer_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = _extraer_campo(lineas, prefijo='En:', con_indice=True)
        revista = (lineas[i_pais + 2]
                   if not lineas[i_pais + 2].startswith('ISSN:') else None)
        i_pags0, pags0 = _extraer_campo(lineas, prefijo='p.', con_indice=True)
        textos.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais,
            'año': int(lineas[i_pais + 1].rstrip('.')),
            'revista': revista.rstrip('.') or None,
            'ISSN': _extraer_campo(lineas, prefijo='ISSN:'),
            'paginas': f'{pags0 or ""} - {lineas[i_pags0 + 1].lstrip("- ")}',
            # TODO: convertir a número?
            'version': _extraer_campo(lineas, prefijo='v.'),
        })
    return textos


def extraer_softwares(soup):
    """
    <a name="software"></a>
    <table>
        ...
        <blockquote>
            FELIPE CESAR LONDONO LOPEZ,
            ...
        </blockquote>
        ...
    """
    table = _find_table_next_to_tag(soup, attrs={'name': 'software'})
    if table is None:
        return []
    softwares = []
    for bq in table.find_all('blockquote'):
        lineas = _split_strip_lines(bq.get_text())
        """lineas = [
            'FELIPE CESAR LONDONO LOPEZ,',
            'MARIO HUMBERTO VALENCIA G,',
            'Diseño Digital. Metodologías, aplicación y... .,',
            'Nombre comercial: ,',
            'contrato/registro: ,',
            '. En: Colombia,',
            ',2004,',
            '.plataforma: CD ROM PC,',
            '.ambiente: PC,',
            'Palabras:',
            'Diseño Digital,',
            'Interacción,',
            'Tecnologías Multimedia,',
            'Areas:',
            'Ciencias Sociales -- Ciencias de la Educación...',
            'Ciencias Naturales -- Computación y Ciencias de la...',
            'Sectores:',
            'Educación,'
        ]"""
        i_nombre_com, _ = _extraer_campo(
            lineas, prefijo='Nombre comercial:', con_indice=True)
        i_pais, pais = _extraer_campo(lineas, prefijo='. En:', con_indice=True)
        str_año = lineas[i_pais + 1].strip(',')
        softwares.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[: i_nombre_com - 1]).rstrip(','),
            'nombre': lineas[i_nombre_com - 1].rstrip('.,'),
            'registro': _extraer_campo(lineas, prefijo='contrato/registro:'),
            'pais': pais,
            'año': int(str_año) if str_año else None,
            'plataforma': _extraer_campo(lineas, prefijo='.plataforma:'),
        })
    return softwares


def extraer_obras_productos(soup):
    """
    <table id="obras_productos">
        ...
        <blockquote>
            <i>Nombre del producto:</i>
            Perdon,
            <i>Disciplina:</i>
            Humanidades -- Arte -- Música y musicología,
            <i>Fecha de creación:</i>
            Mayo de 2018
            <br />
            <h5>INSTANCIAS DE VALORACIÓN DE LA OBRA</h5>
            <ul>
                <li>
                    Nombre del espacio o evento:
                    Festival Internacional de la Imagen,
                    Fecha de presentación:
                    2019-05-09,
                    Entidad convocante 1:
                    UNIVERSIDAD DE CALDAS
                </li>
                <li>
                    Nombre del espacio o evento:
                    Festival Internacional de la Imagen,
                    Fecha de presentación:
                    2019-05-09,
                    Entidad convocante 1:
                    Universidad de Caldas
                </li>
            </ul>
    </blockquote>
    """
    e_obras_productos = soup.find(id='obras_productos')
    if e_obras_productos is None:
        return []
    productos = []
    for bq in e_obras_productos.find_all('blockquote'):
        i_nombre = bq.find('i', string='Nombre del producto:')
        i_disciplina = bq.find('i', string='Disciplina:')
        i_fecha = bq.find('i', string='Fecha de creación:')
        nombre_instancia, fecha_instancia, entidad_instancia = (
            _extraer_nombre_fecha_entidad_instancia_producto(bq))
        productos.append({
            'nombre': i_nombre.next_sibling.strip().rstrip(','),
            'discplina': i_disciplina.next_sibling.strip().rstrip(','),
            'fecha': i_fecha.next_sibling.strip(),
            'nombre_instancia': nombre_instancia,
            'fecha_instancia': fecha_instancia,
            'entidad_instancia': entidad_instancia,
        })
    return productos


def _extraer_nombre_fecha_entidad_instancia_producto(bq):
    li_instancia = bq.find('li')
    lineas = _split_strip_lines(li_instancia.get_text())
    """lineas = [
        0: 'Nombre del espacio o evento:',
        1: 'Festival Internacional de la Imagen,',
        2: 'Fecha de presentación:',
        3: '2019-05-09,',
        4: 'Entidad convocante 1:',
        5?: 'UNIVERSIDAD DE CALDAS'
    ]"""
    nombre = lineas[1].rstrip(',') or None
    fecha = lineas[3].rstrip(',') or None
    entidad = lineas[5] if len(lineas) >= 6 else None
    return nombre, fecha, entidad


def extraer_proyectos(soup):
    """
    <table>
        ...
        <td id="proyectos">
        ...
        <blockquote>
            <i>Tipo de proyecto:&nbsp;</i>Investigaci&oacute;n y
            desarrollo&nbsp;<br>
            DISEÑO DE UN ESPACIO PÚBLICO DIGITAL PARA LA GENERACIÓN...
            DE
            CONVIVENCIA EN GRUPOS MINORITARIOS EN ZONAS URBANAS...<br>
            <i>Inicio:&nbsp;</i>Enero&nbsp;
            2009
            <i>Fin proyectado:&nbsp;</i>Junio&nbsp;
            2010
            <i>Duraci&oacute;n&nbsp;</i>18<br>
            <b>Resumen</b>
            <p class="test1">
                ...<br>
            </p>
        </blockquote>
        ...
    """
    table = _find_table_next_to_tag(soup, id='proyectos')
    if table is None:
        return []
    proyectos = []
    for bq in table.find_all('blockquote'):
        i_tipo = bq.find('i', string='Tipo de proyecto:\xa0')
        proyectos.append({
            'tipo': i_tipo.next_sibling.rstrip(),
            'titulo': (i_tipo.find_next_sibling('br').next_sibling
                             .strip().rstrip('.')),
            'periodo': _extraer_periodo_proyecto(bq),
        })
    return proyectos


def _extraer_periodo_proyecto(bq):
    rm_whitespace = lambda s: ' '.join(s.split())
    i_inicio = bq.find('i', string='Inicio:\xa0')
    inicio = rm_whitespace(i_inicio.next_sibling)
    i_fin = (i_inicio.find_next_sibling('i', string='Fin:\xa0')
             or i_inicio.find_next_sibling(
                 'i', string=(lambda s: s.startswith('Fin'))))
    fin = rm_whitespace(i_fin.next_sibling) if i_fin is not None else ''
    return f'{inicio} - {fin}'


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python scraper.py <cods_rh_infile> <json_outfile>')
        print(f'  {"<cods_rh_infile>":18}árchivo con cods_rh de los investigadores en cada línea')
        print(f'  {"<json_outfile>":18}árchivo en el que se escribirá el json resultante')
    else:
        cods_rh_infile, json_outfile = sys.argv[1:]
        with open(cods_rh_infile) as f:
            cods_rh = [linea.strip() for linea in f if linea]
        curriculums = {cod_rh: extraer_curriculum(cod_rh)
                       for cod_rh in tqdm(cods_rh)}
        with open(json_outfile, 'wt') as f:
            json.dump(curriculums, f)
