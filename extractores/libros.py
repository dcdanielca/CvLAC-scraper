from .utils import (hallar_tabla_al_lado_de_etiqueta, extraer_campo,
                    separar_en_lineas_recortadas)


def extraer(doc):
    """
    ::

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
    table = hallar_tabla_al_lado_de_etiqueta(doc, attrs={'name': 'libros'})
    if table is None:
        return []
    libros = []
    for bq in table.find_all('blockquote'):
        lineas = separar_en_lineas_recortadas(bq.get_text())
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
        i_titulo, titulo = extraer_campo(lineas, prefijo='"', con_indice=True)
        i_pais, pais = extraer_campo(lineas, prefijo='En:', con_indice=True)
        str_año = lineas[i_pais + 1].rstrip('.')
        str_pags = extraer_campo(lineas, prefijo='pags.')
        libros.append({
            # autores: list = [linea.rstrip(',') for linea in lineas[:i_titulo]]
            'autores': ''.join(lineas[:i_titulo]).rstrip(','),
            'titulo': titulo,
            'pais': pais,
            'año': int(str_año) if str_año else None,
            'editorial': extraer_campo(lineas, prefijo='ed:'),
            'isbn': extraer_campo(lineas, prefijo='ISBN:'),
            'version': extraer_campo(lineas, prefijo='v.'),
            'paginas': int(str_pags) if str_pags else None,
        })
    return libros
