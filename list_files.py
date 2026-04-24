import os

folder = r"static\img\estampados\ejercito\pañoleta\Escudos"
files = [f for f in os.listdir(folder) if f.endswith('.png')]
with open("list_files.txt", "w") as f:
    for file in files:
        f.write(file + "\n")
