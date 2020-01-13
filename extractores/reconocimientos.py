def extraer(doc):
    """
    ::

        <table>
            <tr><td><h3>Reconocimientos</h3></td></tr>
            <tr><td><li>Gran premio,Festival Mono Nuñez...</li></td></tr>
            <tr><td><li>...
    """
    e_reconocimientos = doc.find('h3', string='Reconocimientos')
    if e_reconocimientos is None:
        return []
    # TODO: extraer los datos de los reconocimientos.
    return [li.get_text() for li in (
               e_reconocimientos.find_parent('table').find_all('li'))]
