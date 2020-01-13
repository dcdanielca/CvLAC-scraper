from .utils import hallar_tabla_al_lado_de_etiqueta


def extraer(doc):
    """
    ::

        <a name="evento"></a>
        <table>
            ...
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
    table = hallar_tabla_al_lado_de_etiqueta(doc, attrs={'name': 'evento'})
    if table is None:
        return []
    eventos = []
    for table in table.find_all('table'):
        fecha_inicio, lugar = _extraer_fechainicio_lugar(table)
        i_producto_asoc = table.find('i', string='Nombre del producto:')
        i_institucion_asoc = table.find('i',string='Nombre de la institución:')
        eventos.append({
            'nombre': _extraer_nombre(table),
            'fecha': fecha_inicio,
            'lugar' : lugar,
            'producto_asoc': i_producto_asoc.next_sibling.strip()
                             if i_producto_asoc else None,
            'institucion_asoc': i_institucion_asoc.next_sibling.strip()
                                if i_institucion_asoc else None,
        })
    return eventos


def _extraer_nombre(table):
    """
    ::

        <table>
            ...
            <i><b>Nombre del evento:&nbsp;</b></i>
            II Festival Internacional de la Imagen&nbsp;
    """
    return (table.find('b', string='Nombre del evento:\xa0')
                 .parent
                 .next_sibling
                 .strip())


def _extraer_fechainicio_lugar(table):
    """
    ::

        <table>
            ...
            <i>Realizado el:1998-01-01 00:00:00.0,&nbsp;
            1998-04-15 00:00:00.0 &nbsp;
            en MANIZALES &nbsp; - Fondo Cultural del Café &nbsp;
    """
    prefijo_fecha = 'Realizado el:'
    empieza_con_prefijo_fecha = lambda s: s.startswith(prefijo_fecha)
    i_fecha_lugar = table.find('i', string=empieza_con_prefijo_fecha)
    lineas = [linea.strip() for linea in i_fecha_lugar.string.splitlines()]
    """lineas = [
        0: 'Realizado el:2013-08-16 00:00:00.0,',
        1: '2013-08-16 00:00:00.0',
        2: 'en MANIZALES \xa0 - Manizales' | 'en  \xa0 -',
        3: ''
    ]"""
    fecha_inicio = lineas[0][
        # 'Realizado el:|→2013-08-16←| 00:00:00.0,'
        len(prefijo_fecha) : len(prefijo_fecha) + len('AAAA-MM-DD')]
    lugar = lineas[2][len('en ') :].replace(' \xa0', '')  # 'en |→( \xa0) -'
    if lugar == ' -': lugar = None
    return fecha_inicio, lugar
