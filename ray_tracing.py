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

# função utilitária
def normalize(v):
    n = np.linalg.norm(v) # calcula a norma do vetor [sqrt(x**x+y**y+z**z)]
    return (v/n) if n > 0 else v


# funções principais


# Interseção raio-esfera
# (d*d)t^2 + 2(d*(e-c))t + ((e-c)*(e-c)-r^2) = 0

# – Se Δ < 0, não há interseção (pixel = preto).
# – Se Δ ≥ 0, calcule as raízes e pegue a menor positiva t.
def intersect_esfera(origem, direcao, centro, raio):
    """
    Calcula a interseção entre um raio e uma esfera.
    
    Parâmetros:
    - origem: ponto de origem do raio (e)
    - direcao: direção do raio (d) - já normalizada
    - centro: centro da esfera (c)
    - raio: raio da esfera (r)
    
    Retorna:
    - t (float): distância ao ponto de interseção (ou None se não houver)
    """
    # Vetor da origem ao centro: (e - c)
    oc = origem - centro
    
    # Coeficientes da equação quadrática: at² + bt + c = 0
    # a = d·d (produto escalar de d com d)
    a = np.dot(direcao, direcao)
    
    # b = 2(d·(e-c))
    b = 2.0 * np.dot(direcao, oc)
    
    # c = (e-c)·(e-c) - r²
    c = np.dot(oc, oc) - raio**2
    
    # Discriminante Δ = b² - 4ac
    delta = b**2 - 4*a*c
    
    # Se Δ < 0, não há interseção
    if delta < 0:
        return None
    
    # Calcula as duas raízes
    sqrt_delta = np.sqrt(delta)
    t1 = (-b - sqrt_delta) / (2*a)
    t2 = (-b + sqrt_delta) / (2*a)
    
    # Retorna a menor raiz positiva (ponto mais próximo na frente da câmera)
    if t1 > 0:
        return t1
    elif t2 > 0:
        return t2
    else:
        return None


def intensidade_phong(ponto_intersecao, normal, direcao_camera):
    """
    Calcula a intensidade de iluminação Phong no ponto de interseção.
    
    Modelo Phong: I = I_ambiente + I_difusa + I_especular
    
    Parâmetros:
    - ponto_intersecao: ponto na superfície da esfera
    - normal: vetor normal à superfície no ponto
    - direcao_camera: direção do raio (da câmera ao ponto)
    
    Retorna:
    - intensidade (float): valor entre 0 e 1
    """
    # Fonte de luz (posição)
    luz_pos = np.array([-5.0, 5.0, 5.0])
    luz_intensidade = 1.0
    
    # Componentes do material
    k_ambiente = 0.1    # coeficiente ambiente
    k_difusa = 0.6      # coeficiente difuso
    k_especular = 0.3   # coeficiente especular
    n_brilho = 32       # expoente de brilho especular
    
    # Componente ambiente
    I_ambiente = k_ambiente
    
    # Vetor da superfície à luz (L)
    L = normalize(luz_pos - ponto_intersecao)
    
    # Componente difusa: I_d = k_d * (N · L)
    NdotL = max(0, np.dot(normal, L))
    I_difusa = k_difusa * luz_intensidade * NdotL
    
    # Componente especular (reflexão)
    # Vetor de visão (V) - direção da câmera (oposta à direção do raio)
    V = normalize(-direcao_camera)
    
    # Vetor de reflexão (R) = 2(N·L)N - L
    R = 2 * np.dot(normal, L) * normal - L
    R = normalize(R)
    
    # I_s = k_s * (R · V)^n
    RdotV = max(0, np.dot(R, V))
    I_especular = k_especular * luz_intensidade * (RdotV ** n_brilho)
    
    # Intensidade total
    intensidade = I_ambiente + I_difusa + I_especular
    
    # Limita o valor entre 0 e 1
    return min(1.0, max(0.0, intensidade))


def renderizar():
    """
    Renderiza a cena completa, gerando uma imagem do plano de projeção.
    
    Para cada pixel:
    1. Calcula a posição do pixel no plano de projeção
    2. Cria um raio da câmera passando pelo pixel
    3. Verifica interseção com a esfera
    4. Calcula a iluminação Phong se houver interseção
    5. Armazena a cor do pixel
    """
    # Cria a imagem (matriz de pixels)
    imagem = np.zeros((height, width))
    
    print("Renderizando cena...")
    print(f"Resolução: {width}x{height} pixels")
    print(f"Câmera em: {eye}")
    print(f"Distância focal: {df}")
    print(f"FOV: {fov_deg}°")
    print(f"Esfera: centro={centro_esfera}, raio={raio_esfera}")
    print()
    
    # Para cada pixel da imagem
    for i in range(height):
        for j in range(width):
            # Calcula a posição do pixel no plano de projeção
            # Plano de projeção está em x = eye_x + df = 0
            # Centro do plano está em (0, 0, 0)
            
            # Coordenadas do pixel (centralizadas)
            # y varia de -half a +half
            # z varia de -half a +half
            pixel_y = -half + (j + 0.5) * pixel_size_y
            pixel_z = half - (i + 0.5) * pixel_size_z
            
            # Ponto no plano de projeção
            pixel_pos = np.array([eye[0] + df, pixel_y, pixel_z])
            
            # Direção do raio: da câmera ao pixel
            direcao_raio = normalize(pixel_pos - eye)
            
            # Verifica interseção com a esfera
            t = intersect_esfera(eye, direcao_raio, centro_esfera, raio_esfera)
            
            if t is not None:
                # Ponto de interseção
                ponto = eye + t * direcao_raio
                
                # Normal à superfície (aponta para fora da esfera)
                normal = normalize(ponto - centro_esfera)
                
                # Calcula a intensidade usando Phong
                intensidade = intensidade_phong(ponto, normal, direcao_raio)
                
                # Armazena o valor do pixel
                imagem[i, j] = intensidade
            else:
                # Sem interseção - pixel preto (fundo)
                imagem[i, j] = 0.0
    
    print("Renderização concluída!")
    return imagem


if __name__ == "__main__":
    # Renderiza a cena
    imagem = renderizar()
    
    # Exibe a imagem
    plt.figure(figsize=(8, 8))
    plt.imshow(imagem, cmap='gray', vmin=0, vmax=1)
    plt.title(f'Ray Tracing - Esfera\nResolução: {width}x{height}, FOV: {fov_deg}°, Distância Focal: {df}')
    plt.colorbar(label='Intensidade')
    plt.xlabel('X (pixels)')
    plt.ylabel('Y (pixels)')
    plt.tight_layout()
    
    # Salva a imagem
    plt.savefig('raytracing_esfera.png', dpi=150, bbox_inches='tight')
    print("\nImagem salva como 'raytracing_esfera.png'")
    
    # Mostra a imagem
    plt.show()
    
    print("\n" + "="*60)
    print("EXERCÍCIO - Experimente alterar os parâmetros:")
    print("="*60)
    print("a) Distância focal (df): Altere o valor na linha 12")
    print("   - df menor = objeto parece maior")
    print("   - df maior = objeto parece menor")
    print()
    print("b) Campo de visão (fov_deg): Altere o valor na linha 13")
    print("   - FOV menor = zoom (visão mais estreita)")
    print("   - FOV maior = wide angle (visão mais ampla)")
    print()
    print("Sugestões para testar:")
    print("  - df = 5.0 ou df = 20.0")
    print("  - fov_deg = 45.0 ou fov_deg = 120.0")
    print("  - width, height = 100, 100 (para imagem maior)")
    print("="*60)