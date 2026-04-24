import os
import sys

try:
    path = "static/img/estampados/ejercito/pañoleta/Escudos"
    files = os.listdir(path)
    with open("out_files.txt", "w", encoding='utf-8') as f:
        for fi in files:
            f.write(fi + "\n")
except Exception as e:
    with open("out_files.txt", "w", encoding='utf-8') as f:
        f.write(str(e))

