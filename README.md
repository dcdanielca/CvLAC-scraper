# CvLAC-scraper
Web scraper del currículo de un investigador registrado en CvLAC.

## Instalar
Clonar el repositorio en el área de trabajo e instalar las dependencias con `pip install -r requirements.txt`.

## Ejemplos
* Como módulo de Python:
```python
import cvlac_scraper
print(cvlac_scaper.extraer_curriculo(cod_rh='0000000000'))
```
* En la línea de comandos:
```cmd
python cvlac_scraper.py --cod_rh 00000000
```
* Para varios investigadores:
```cmd
python cvlac_scraper.py -e cods_rh.txt -s curriculums.json
```
