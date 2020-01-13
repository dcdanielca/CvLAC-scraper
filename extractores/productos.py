def extraer(doc):
    """
    <table id="obras_productos">
        ...
        <blockquote>
            <i>Nombre del producto:</i>
            Perdon,
            <i>Disciplina:</i>
            Humanidades -- Arte -- Música y musicología,
            <i>Fecha de creación:</i>
            Mayo de 2018
            <br />
            <h5>INSTANCIAS DE VALORACIÓN DE LA OBRA</h5>
            <ul>
                <li>
                    Nombre del espacio o evento:
                    Festival Internacional de la Imagen,
                    Fecha de presentación:
                    2019-05-09,
                    Entidad convocante 1:
                    UNIVERSIDAD DE CALDAS
                </li>
                <li>
                    Nombre del espacio o evento:
                    Festival Internacional de la Imagen,
                    Fecha de presentación:
                    2019-05-09,
                    Entidad convocante 1:
                    Universidad de Caldas
                </li>
            </ul>
    </blockquote>
    """
    e_obras_productos = doc.find(id='obras_productos')
    if e_obras_productos is None:
        return []
    productos = []
    for bq in e_obras_productos.find_all('blockquote'):
        i_nombre = bq.find('i', string='Nombre del producto:')
        i_disciplina = bq.find('i', string='Disciplina:')
        i_fecha = bq.find('i', string='Fecha de creación:')
        nombre_instancia, fecha_instancia, entidad_instancia = (
            _extraer_nombre_fecha_entidad_instancia_producto(bq))
        productos.append({
            'nombre': i_nombre.next_sibling.strip().rstrip(','),
            'discplina': i_disciplina.next_sibling.strip().rstrip(','),
            'fecha': i_fecha.next_sibling.strip(),
            'nombre_instancia': nombre_instancia,
            'fecha_instancia': fecha_instancia,
            'entidad_instancia': entidad_instancia,
        })
    return productos
