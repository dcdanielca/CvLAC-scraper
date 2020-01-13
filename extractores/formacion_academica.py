from .utils import hallar_tabla_al_lado_de_etiqueta


def extraer(doc):
    """
    ::

        <a name="formacion_acad"></a>
        <table>
            ...
            <td>
                <b>Doctorado</b>
                UNIVERSIDAD DE CALDAS<br />
                ...
            </td>
            <td>
                ...
    """
    table = hallar_tabla_al_lado_de_etiqueta(doc, attrs={'name': 'formacion_acad'})
    if table is None:
        return []
    formacion_acad = []
    for b in table.find_all('b'):
        strs = [str_.strip() or None for str_ in b.parent.strings]
        """strs = [
            0: 'Doctorado',
            1: 'UNIVERSIDAD DE CALDAS',
            2: 'Doctorado en Diseño y Creación',  # opcional si no es edu sup
            3: 'Juliode2011 - Agostode 2017',  # [sic]
            4: 'Interfaz Cerebro Ordenador para la Creación a...'  # opcional
        ]"""
        if strs[2] is None:  # no es educación superior
            continue
        formacion_acad.append({
            'titulo': strs[2],
            'institucion': strs[1],
            'periodo': _extraer_periodo(strs[3]),
            'trabajo_grado': strs[4],
        })
    return formacion_acad


def _extraer_periodo(str_):
    # str_ = 'Juliode2011 - Agostode 2017'
    fecha_inicio, fecha_fin = str_.split(' - ') # 'Juliode2011','Agostode 2017'
    mes_inicio = fecha_inicio[: -len('deAAAA')]  # Julio←|de2011
    año_inicio = fecha_inicio[-len('AAAA') :]    # Juliode|→2011 
    fecha_inicio = f'{mes_inicio} de {año_inicio}'
    mes_fin = fecha_fin[: -len('de AAAA')] # Agosto←|de 2017,puede no haber mes
    año_fin = fecha_fin[-len('AAAA') :]    # Agostode |→2017
    fecha_fin = (f'{mes_fin} de {año_fin}') if mes_fin else (f'de {año_fin}')
    return f'{fecha_inicio} - {fecha_fin}'
