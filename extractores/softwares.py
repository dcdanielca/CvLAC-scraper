from .utils import (hallar_tabla_al_lado_de_etiqueta, extraer_campo,
                    separar_en_lineas_recortadas)


def extraer(doc):
    """
    ::

        <a name="software"></a>
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
    table = hallar_tabla_al_lado_de_etiqueta(doc, attrs={'name': 'software'})
    if table is None:
        return []
    softwares = []
    for bq in table.find_all('blockquote'):
        lineas = separar_en_lineas_recortadas(bq.get_text())
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
        i_nombre_com, _ = extraer_campo(
            lineas, prefijo='Nombre comercial:', con_indice=True)
        i_pais, pais = extraer_campo(lineas, prefijo='. En:', con_indice=True)
        str_año = lineas[i_pais + 1].strip(',')
        softwares.append({
            # TODO: dejar como lista?
            'autores': ''.join(lineas[: i_nombre_com - 1]).rstrip(','),
            'nombre': lineas[i_nombre_com - 1].rstrip('.,'),
            'registro': extraer_campo(lineas, prefijo='contrato/registro:'),
            'pais': pais,
            'año': int(str_año) if str_año else None,
            'plataforma': extraer_campo(lineas, prefijo='.plataforma:'),
        })
    return softwares
