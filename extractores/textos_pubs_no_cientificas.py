from .utils import separar_en_lineas_recortadas, extraer_campo


def extraer(doc):
    """
    ::

        <table>
            <tr><td><h3 id="textos"></h3></td></tr>
            ...
            <tr><td><blockquote>
                FELIPE CESAR LONDONO LOPEZ,
                ...
            </blockquote></td></tr>
            ...
            <tr><td><blockquote>
                ...
    """
    e_textos = doc.find(id='textos')
    if e_textos is None:
        return []
    textos = []
    for bq in (e_textos
                   .find_parent('table')
                   .find_all('blockquote')):
        lineas = separar_en_lineas_recortadas(bq.get_text())
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
        i_titulo, titulo = extraer_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = extraer_campo(lineas, prefijo='En:', con_indice=True)
        str_año = lineas[i_pais + 1].rstrip('.')
        textos.append({
            # autores: list = [linea.rstrip(',') for linea in lineas[:i_titulo]]
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo.strip('"'),
            'pais': pais,
            'año': int(str_año) if str_año else None,
            'revista': _extraer_revista(lineas, i_pais),
            'issn': extraer_campo(lineas, prefijo='ISSN:'),
            'paginas': _extraer_paginas(lineas),
            'version': extraer_campo(lineas, prefijo='v.'),
        })
    return textos


def _extraer_revista(lineas, i_pais):
    return (None if lineas[i_pais + 2].startswith('ISSN:')
            else (lineas[i_pais + 2].rstrip('.') or None))


def _extraer_paginas(lineas):
    i_pags0, pags0 = extraer_campo(lineas, prefijo='p.', con_indice=True)
    if not pags0: pags0 = ''
    pags1 = lineas[i_pags0 + 1].lstrip('- ')
    return None if not (pags0 or pags1) else f'{pags0} - {pags1}'
