def extraer(doc):
    """
    ::

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
            <blockquote>
                ...
    """
    e_proyectos = doc.find(id='proyectos')
    if e_proyectos is None:
        return []
    proyectos = []
    for bq in (e_proyectos
                   .find_parent('table')
                   .find_all('blockquote')):
        i_tipo = bq.find('i', string='Tipo de proyecto:\xa0')
        proyectos.append({
            'tipo': i_tipo.next_sibling.rstrip(),
            'titulo': (i_tipo.find_next_sibling('br').next_sibling
                             .strip().rstrip('.')),
            'periodo': _extraer_periodo(bq),
        })
    return proyectos


def _extraer_periodo(bq):
    """
    ::

        <i>Inicio:&nbsp;</i>Enero&nbsp;
        2009
        <i>Fin proyectado:&nbsp;</i>Junio&nbsp;
        2010
    """
    i_inicio = bq.find('i', string='Inicio:\xa0')
    inicio = _reducir_espacios_en_blanco(i_inicio.next_sibling)
    empieza_con_fin = lambda s: s.startswith('Fin')
    i_fin = (i_inicio.find_next_sibling('i', string='Fin:\xa0')
             or i_inicio.find_next_sibling('i', string=empieza_con_fin))
    fin = ('' if i_fin is None
           else _reducir_espacios_en_blanco(i_fin.next_sibling))
    return None if not (inicio or fin) else f'{inicio} - {fin}'


def _reducir_espacios_en_blanco(s):
    return ' '.join(s.split())
