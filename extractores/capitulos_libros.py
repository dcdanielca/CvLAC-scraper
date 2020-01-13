from .utils import (hallar_tabla_al_lado_de_etiqueta, extraer_campo,
                    separar_en_lineas_recortadas, extraer_pags_año)


def extraer(doc):
    """
    ::

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
    table = hallar_tabla_al_lado_de_etiqueta(doc, attrs={'name': 'capitulos'})
    if table is None:
        return []
    capitulos = []
    for bq in table.find_all('blockquote'):
        lineas = separar_en_lineas_recortadas(bq.get_text())
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
        i_titulo_capitulo, titulo_capitulo = extraer_campo(
            lineas, prefijo='"', con_indice=True)
        pags, año = extraer_pags_año(lineas, prefijo_pags=', p.')
        capitulos.append({
            'autores': _extraer_autores(lineas, i_titulo_capitulo),
            'titulo_capitulo': titulo_capitulo,
            'titulo_libro': lineas[i_titulo_capitulo + 1],
            'pais': extraer_campo(lineas, prefijo='. En:'),
            'isbn': extraer_campo(lineas, prefijo='ISBN:'),
            'editorial': extraer_campo(lineas, prefijo='ed:'),
            'version': extraer_campo(lineas, prefijo=', v.'),
            'paginas': pags,
            'año': año,
        })
    return capitulos


def _extraer_autores(lineas, i_titulo_capitulo):
    # autores: list = [linea.rstrip(',') for linea in lineas[:i_titulo_capitulo]
    #                  if not linea.startswith('Tipo:')]
    return (''.join(linea for linea in lineas[:i_titulo_capitulo]
                    if not linea.startswith('Tipo:'))
              .rstrip(','))
