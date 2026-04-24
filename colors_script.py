import os
try:
    from PIL import Image
    import numpy as np
    path = 'static/img/estampados/ejercito/pañoleta/Escudos'
    with open('colors.txt', 'w') as f:
        for file in os.listdir(path):
            if file.endswith('.png'):
                img = Image.open(os.path.join(path, file)).convert('RGBA')
                arr = np.array(img)
                mask = arr[:,:,3] > 0
                if mask.any():
                    avg = arr[mask].mean(axis=0)[:3]
                    f.write(f'{file}: {avg.tolist()}\n')
except Exception as e:
    with open('colors.txt', 'w') as f:
        f.write(str(e))
