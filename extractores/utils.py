def hallar_tabla_al_lado_de_etiqueta(doc, *args, **kwargs):
    tag = doc.find(*args, **kwargs)
    #      tag?.find_next_sibling('table')
    return tag and tag.find_next_sibling('table')


def separar_en_lineas_recortadas(s):
    """Recortadas se refiere a que a las líneas se les removieron los espacios
    en blanco al inicio y al final.
    """
    return [linea.strip() for linea in s.splitlines() if linea.strip()]


def extraer_campo(lineas, prefijo, con_indice=False):
    indice, campo = next(
        (i, (linea[len(prefijo) :].strip().strip('",.') or None))
        for (i, linea) in enumerate(lineas) if linea.startswith(prefijo))
    return (indice, campo) if con_indice else campo


def extraer_pags_año(lineas, prefijo_pags):
    """De artículos y capítulos de libros."""
    """lineas = [
        ...,
         i_pags0:      'p.[[ ]<pág0>[-]]',
         i_pags0 + 1:  '-'      | '-[ <pág1>]',
         i_pags0 + 2:  '<pág1>' | ',<año>',
        [i_pags0 + 3:  ruido como '[V. ]<núm>', 'Educ', 'N/A',]
         i_pags0 + 3+: ',<año>[,]',
        ...
    ]"""
    i_pags0, pags0 = extraer_campo(lineas, prefijo_pags, con_indice=True)
    pags0 = pags0.strip(' -') if pags0 else ''
    if lineas[i_pags0 + 1] == '-' and not lineas[i_pags0 + 2].startswith(','):
        pags1 = lineas[i_pags0 + 2]
        i_año = i_pags0 + 3
    else:
        pags1 = lineas[i_pags0 + 1].strip('- ')
        i_año = i_pags0 + 2
    while not lineas[i_año].startswith(','):
        i_año += 1
    pags = None if not (pags0 or pags1) else f'{pags0} - {pags1}'
    año = lineas[i_año].strip(',')
    año = int(año) if año else None
    return pags, año
