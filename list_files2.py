import os

base = r"static\img\estampados\ejercito"
pañ_dir = [d for d in os.listdir(base) if 'pa' in d and 'oleta' in d][0]
folder = os.path.join(base, pañ_dir, "Escudos")
files = [f for f in os.listdir(folder) if f.endswith('.png')]
with open("list_files.txt", "w") as f:
    for file in files:
        f.write(file + "\n")
