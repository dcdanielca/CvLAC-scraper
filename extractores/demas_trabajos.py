from .utils import separar_en_lineas_recortadas, extraer_campo


def extraer(doc):
    """
    ::

        <td>
            <a name="demas_trabajos"></a>
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
    e_trabajos = doc.find(attrs={'name': 'demas_trabajos'})
    if e_trabajos is None:
        return []
    trabajos = []
    for bq in (e_trabajos
                   .parent  # <td>
                   .find_all('blockquote')):
        lineas = separar_en_lineas_recortadas(bq.get_text())
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
        i_pais, pais = extraer_campo(lineas, prefijo='. En:', con_indice=True)
        str_año = lineas[i_pais + 1].strip(',')
        trabajos.append({
            # autores: list = [linea.rstrip(',') for linea in lineas[: i_pais - 1]]
            'autores': ''.join(lineas[: i_pais - 1]).rstrip(','),
            'titulo': lineas[i_pais - 1],
            'pais': pais,
            'año': int(str_año) if str_año else None,
            'finalidad': extraer_campo(lineas, prefijo='finalidad:'),
        })
    return trabajos
