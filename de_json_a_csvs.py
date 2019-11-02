import csv
import json
import sys

from collections import defaultdict
from tempfile import TemporaryDirectory
from shutil import make_archive


def de_no_relacional_a_relacional(curriculums):
    tablas = defaultdict(list)
    for cod_rh, curriculum in curriculums.items():
        for nombre_seccion, seccion in curriculum.items():
            if nombre_seccion == 'reconocimientos':
                seccion = [{
                    'cod_rh': cod_rh,
                    'reconocimiento': reconocimiento
                } for reconocimiento in seccion]
            else:
                for elemento in seccion:
                    elemento['cod_rh'] = cod_rh
            tablas[nombre_seccion].extend(seccion)
    return tablas


def exportar_a_csvs(tablas, nombre_archivo='tablas'):
    with TemporaryDirectory() as carpeta_tmp:
        for nombre_tabla, tabla in tablas.items():
            with (open(f'{carpeta_tmp}/{nombre_tabla}.csv', mode='w',
                       encoding='utf-8', newline='')
                 ) as archivo_csv:
                if not tabla:
                    continue
                fieldnames = list(tabla[0].keys())
                escritor_tabla = csv.DictWriter(archivo_csv, fieldnames)
                escritor_tabla.writeheader()
                escritor_tabla.writerows(tabla)
        make_archive(nombre_archivo, 'zip', carpeta_tmp)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python de_json_a_csvs.py <json> [<outfile>]')
        print('  json     con los curriculums')
        print('  outfile  que almacenará los csvs, sin extensión, "tablas" por defecto')
    else:
        with open(sys.argv[1]) as archivo_json:
            curriculums = json.load(archivo_json)
        tablas = de_no_relacional_a_relacional(curriculums)
        exportar_a_csvs(tablas)
