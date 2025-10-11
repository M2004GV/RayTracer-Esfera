import numpy as np
import matplotlib.pyplot as plt


## Configuração do cenário
# Imagem
width, height = 5, 5
aspect = width / height  

# Câmera 
eye = np.array([-10.0, 0.0, 0.0])
df = 10.0                   # distância focal
fov_deg = 90.0
half = df * np.tan(np.deg2rad(fov_deg * 0.5))  # 10.0
plane_size_y = 2 * half  # 20.0 (largura em y)
plane_size_z = 2 * half  # 20.0 (altura em z)
pixel_size_y = plane_size_y / width   # 4.0
pixel_size_z = plane_size_z / height  # 4.0


# Objeto: esfera
centro_esfera = np.array([5.0, 0.0, 0.0])
raio_esfera = 2.0


