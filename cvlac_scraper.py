"""Web scraper del currículo de un investigador registrado en CvLAC.

Ejemplos de uso:
================

- Como módulo::

    import cvlac_scraper
    print(cvlac_scaper.extraer_curriculo(cod_rh='0000000000'))

- En la línea de comandos::

    > python cvlac_scraper.py --cod_rh 00000000

- Para más de un investigador::

    > python cvlac_scraper.py -e cods_rh.txt -s curriculums.json
"""

import argparse
import json
import sys
import warnings
from multiprocessing import Pool
from urllib.request import urlopen

from bs4 import BeautifulSoup

from extractores import *

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iter(iterable)


def extraer_curriculum(cod_rh):
    url = f'http://scienti.colciencias.gov.co:8081/cvlac/visualizador/generarCurriculoCv.do?cod_rh={cod_rh}'
    with urlopen(url) as respuesta:
        """Si no se especifica el parser se usa el mejor disponible, por lo que
        el árbol resultante podría variar y por tanto se genera una
        advertencia. Esto no parece ser un problema para el scraper por tanto
        se ignora la advertencia.
        """
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', category=UserWarning)
            doc = BeautifulSoup(respuesta)
        return {
            'formacion_academica': formacion_academica.extraer(doc),
            'reconocimientos': reconocimientos.extraer(doc),
            'eventos_cientificos': eventos_cientificos.extraer(doc),
            'articulos': articulos.extraer(doc),
            'libros': libros.extraer(doc),
            'capitulos_libros': capitulos_libros.extraer(doc),
            'demas_trabajos': demas_trabajos.extraer(doc),
            'textos_pubs_no_cientificas': textos_pubs_no_cientificas.extraer(doc),
            'softwares': softwares.extraer(doc),
            'obras_productos': obras_productos.extraer(doc),
            'proyectos': proyectos.extraer(doc),
        }


_EJEMPLOS = """
Ejemplos:
    python cvlac_scraper.py --cod_rh 00000000
    python cvlac_scraper.py -e cods_rh.txt -s curriculums.json
"""


def _parse_args():
    # usage: cvlac_scraper.py [-h] (--cod_rh COD_RH | --cods_rh CODS_RH) [-o OUTFILE]
    parser = argparse.ArgumentParser(
        description='Web scraper del currículo de un investigador registrado en CvLAC.',
        epilog=_EJEMPLOS, formatter_class=argparse.RawTextHelpFormatter)
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument('--cod_rh', help='cod_rh del investigador')
    grupo.add_argument(
        '-e', '--entrada',
        help='árchivo con cods_rh de los investigadores en cada línea')
    parser.add_argument(
        '-s', '--salida',
        help='árchivo en el que se escribirá el json resultante')
    parser.add_argument(
        '-m', '--multiprocesamiento', action='store_true',
        help='usar multiprocesamiento para acelerar las extracciones, podría fallar')
    return parser.parse_args()


def _extraer_curriculums_mp(cods_rh):
    with Pool() as pool:
        it_curriculums = tqdm(pool.imap(extraer_curriculum, cods_rh),
                              total=len(cods_rh))
        return dict(zip(cods_rh, it_curriculums))


def _escribir_resultado(resultado, ruta_archivo):
    if ruta_archivo:
        with open(ruta_archivo, 'w') as archivo:
            json.dump(resultado, archivo, indent=4)
    else:
        json.dump(resultado, sys.stdout, indent=4)


if __name__ == '__main__':
    args = _parse_args()
    if args.cod_rh:
        resultado = extraer_curriculum(args.cod_rh)
    else:
        with open(args.entrada) as archivo:
            cods_rh = [linea.strip() for linea in archivo if linea.strip()]
        if args.multiprocesamiento:
            resultado = _extraer_curriculums_mp(cods_rh)
        else:
            resultado = {cod_rh: extraer_curriculum(cod_rh) for cod_rh in tqdm(cods_rh)}
    _escribir_resultado(resultado, args.salida)
