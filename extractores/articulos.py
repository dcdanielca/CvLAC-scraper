from .utils import (hallar_tabla_al_lado_de_etiqueta, extraer_campo,
                    separar_en_lineas_recortadas, extraer_pags_año)


def extraer(doc):
    """
    ::

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
    table = hallar_tabla_al_lado_de_etiqueta(doc, attrs={'name': 'articulos'})
    if table is None:
        return []
    articulos = []
    for bq in table.find_all('blockquote'):
        lineas = separar_en_lineas_recortadas(bq.get_text())
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
        i_titulo, titulo = extraer_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = extraer_campo(lineas, prefijo='. En:', con_indice=True)
        revista = (lineas[i_pais + 1]
                   if not lineas[i_pais + 1].startswith('ISSN:') else None)
        pags, año = extraer_pags_año(lineas, prefijo_pags='p.')
        articulos.append({
            # autores: list = [linea.rstrip(',') for linea in lineas[:i_titulo]]
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo,
            'pais': pais,
            'revista': revista,
            'issn': extraer_campo(lineas, prefijo='ISSN:'),
            'editorial': extraer_campo(lineas, prefijo='ed:'),
            'version': _extraer_version(lineas),
            'paginas': pags,
            'año': año,
            'doi': extraer_campo(lineas, prefijo='DOI:'),
        })
    return articulos


def _extraer_version(lineas):
    return 'v.{} fasc.{}'.format(
        extraer_campo(lineas, prefijo='v.') or 'N/A',
        extraer_campo(lineas, prefijo='fasc.') or 'N/A')
