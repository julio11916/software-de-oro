import os
path = r"static\img\estampados\ejercito\pañoleta\Escudos"
files = [f for f in os.listdir(path) if f.endswith('.png')]
print("Files:", files)
try:
    from PIL import Image
    import numpy as np
    colors = {}
    for f in files:
        img = Image.open(os.path.join(path, f)).convert("RGBA")
        arr = np.array(img)
        mask = arr[:,:,3] > 0
        if mask.any():
            avg = arr[mask].mean(axis=0)[:3]
            colors[f] = [int(x) for x in avg]
    import json
    with open("colors_out.json", "w") as f:
        json.dump(colors, f)
except Exception as e:
    with open("colors_err.txt", "w") as f:
        f.write(str(e))
