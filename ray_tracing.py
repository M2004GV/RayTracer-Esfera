import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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


def intensidade_phong(ponto_intersecao, normal, direcao_camera, modo='completo'):
    """
    Calcula a intensidade de iluminação Phong no ponto de interseção.
    
    Modelo Phong: I = I_ambiente + I_difusa + I_especular
    
    Parâmetros:
    - ponto_intersecao: ponto na superfície da esfera
    - normal: vetor normal à superfície no ponto
    - direcao_camera: direção do raio (da câmera ao ponto)
    - modo: 'ambiente', 'difuso', 'especular' ou 'completo'
    
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
    
    # ========== SOMBREAMENTO: COMPONENTE AMBIENTE ==========
    # Iluminação base constante (não depende de posição da luz)
    I_ambiente = k_ambiente
    
    # ========== SOMBREAMENTO: COMPONENTE DIFUSA ==========
    # Vetor da superfície à luz (L)
    L = normalize(luz_pos - ponto_intersecao)
    
    # Componente difusa: I_d = k_d * (N · L)
    # Depende do ângulo entre a normal e a direção da luz
    NdotL = max(0, np.dot(normal, L))
    I_difusa = k_difusa * luz_intensidade * NdotL
    
    # ========== SOMBREAMENTO: COMPONENTE ESPECULAR ==========
    # Vetor de visão (V) - direção da câmera (oposta à direção do raio)
    V = normalize(-direcao_camera)
    
    # Vetor de reflexão (R) = 2(N·L)N - L
    R = 2 * np.dot(normal, L) * normal - L
    R = normalize(R)
    
    # I_s = k_s * (R · V)^n
    # Cria o brilho especular (highlight)
    RdotV = max(0, np.dot(R, V))
    I_especular = k_especular * luz_intensidade * (RdotV ** n_brilho)
    
    # Retorna componente específica ou todas combinadas
    if modo == 'ambiente':
        intensidade = I_ambiente
    elif modo == 'difuso':
        intensidade = I_ambiente + I_difusa
    elif modo == 'especular':
        intensidade = I_ambiente + I_especular
    else:  # 'completo'
        intensidade = I_ambiente + I_difusa + I_especular
    
    # Limita o valor entre 0 e 1
    return min(1.0, max(0.0, intensidade))

def gerar_planilha_calculos():
    print("\n" + "="*60)
    print("GERANDO PLANILHA COM CÁLCULOS DETALHADOS...")
    print("="*60)
    
    dados = []
        
    # Para cada pixel da imagem
    for i in range(height):
        for j in range(width):
            pixel_info = {
                'Pixel_Row': i,
                'Pixel_Col': j,
                'Pixel_Index': i * width + j + 1
            }
                
            # ========== ETAPA 1: GERAÇÃO DOS RAIOS ==========
            pixel_y = -half + (j + 0.5) * pixel_size_y
            pixel_z = half - (i + 0.5) * pixel_size_z
            pixel_pos = np.array([eye[0] + df, pixel_y, pixel_z])
            direcao_raio = normalize(pixel_pos - eye)
                
            pixel_info['Pixel_X'] = pixel_pos[0]
            pixel_info['Pixel_Y'] = pixel_pos[1]
            pixel_info['Pixel_Z'] = pixel_pos[2]
            pixel_info['Raio_Dir_X'] = direcao_raio[0]
            pixel_info['Raio_Dir_Y'] = direcao_raio[1]
            pixel_info['Raio_Dir_Z'] = direcao_raio[2]
                
            # ========== ETAPA 2: INTERSEÇÃO RAIO-OBJETO ==========
            oc = eye - centro_esfera
            a = np.dot(direcao_raio, direcao_raio)
            b = 2.0 * np.dot(direcao_raio, oc)
            c = np.dot(oc, oc) - raio_esfera**2
            delta = b**2 - 4*a*c
                
            pixel_info['Coef_a'] = a
            pixel_info['Coef_b'] = b
            pixel_info['Coef_c'] = c
            pixel_info['Delta'] = delta
                
            # Calcula t (distância de interseção)
            if delta < 0:
                t = None
                pixel_info['Intersecao'] = 'Não'
                pixel_info['t'] = 'N/A'
                pixel_info['Ponto_X'] = 'N/A'
                pixel_info['Ponto_Y'] = 'N/A'
                pixel_info['Ponto_Z'] = 'N/A'
                pixel_info['Normal_X'] = 'N/A'
                pixel_info['Normal_Y'] = 'N/A'
                pixel_info['Normal_Z'] = 'N/A'
                pixel_info['I_Ambiente'] = 0.0
                pixel_info['I_Difusa'] = 0.0
                pixel_info['I_Especular'] = 0.0
                pixel_info['I_Total'] = 0.0
                pixel_info['Luz_X'] = 'N/A'
                pixel_info['Luz_Y'] = 'N/A'
                pixel_info['Luz_Z'] = 'N/A'
                pixel_info['L_X'] = 'N/A'
                pixel_info['L_Y'] = 'N/A'
                pixel_info['L_Z'] = 'N/A'
                pixel_info['NdotL'] = 'N/A'
                pixel_info['V_X'] = 'N/A'
                pixel_info['V_Y'] = 'N/A'
                pixel_info['V_Z'] = 'N/A'
                pixel_info['R_X'] = 'N/A'
                pixel_info['R_Y'] = 'N/A'
                pixel_info['R_Z'] = 'N/A'
                pixel_info['RdotV'] = 'N/A'
                pixel_info['RdotV_elevado'] = 'N/A'
            else:
                sqrt_delta = np.sqrt(delta)
                t1 = (-b - sqrt_delta) / (2*a)
                t2 = (-b + sqrt_delta) / (2*a)
                    
                if t1 > 0:
                    t = t1
                elif t2 > 0:
                    t = t2
                else:
                    t = None
                    
                if t is not None:
                    pixel_info['Intersecao'] = 'Sim'
                    pixel_info['t'] = t
                        
                    # Ponto de interseção
                    ponto = eye + t * direcao_raio
                    pixel_info['Ponto_X'] = ponto[0]
                    pixel_info['Ponto_Y'] = ponto[1]
                    pixel_info['Ponto_Z'] = ponto[2]
                        
                    # Normal
                    normal = normalize(ponto - centro_esfera)
                    pixel_info['Normal_X'] = normal[0]
                    pixel_info['Normal_Y'] = normal[1]
                    pixel_info['Normal_Z'] = normal[2]
                        
                    # ========== ETAPA 3: SOMBREAMENTO ==========
                    luz_pos = np.array([-5.0, 5.0, 5.0])
                    luz_intensidade = 1.0
                    k_ambiente = 0.1
                    k_difusa = 0.6
                    k_especular = 0.3
                    n_brilho = 32
                        
                    # Componente Ambiente (iluminação base constante)
                    I_ambiente = k_ambiente
                    
                    # Componente Difusa (baseada no ângulo entre normal e luz)
                    L = normalize(luz_pos - ponto)
                    NdotL = max(0, np.dot(normal, L))
                    I_difusa = k_difusa * luz_intensidade * NdotL
                    
                    # Componente Especular (reflexo brilhante)
                    V = normalize(-direcao_raio)
                    R = 2 * np.dot(normal, L) * normal - L
                    R = normalize(R)
                    RdotV = max(0, np.dot(R, V))
                    I_especular = k_especular * luz_intensidade * (RdotV ** n_brilho)
                    
                    # Intensidade total
                    I_total = I_ambiente + I_difusa + I_especular
                    
                    # Salva as componentes INDIVIDUAIS
                    pixel_info['I_Ambiente'] = I_ambiente
                    pixel_info['I_Difusa'] = I_difusa
                    pixel_info['I_Especular'] = I_especular
                    pixel_info['I_Total'] = min(1.0, I_total)
                    
                    # Cálculos intermediários adicionais
                    pixel_info['Luz_X'] = luz_pos[0]
                    pixel_info['Luz_Y'] = luz_pos[1]
                    pixel_info['Luz_Z'] = luz_pos[2]
                    pixel_info['L_X'] = L[0]
                    pixel_info['L_Y'] = L[1]
                    pixel_info['L_Z'] = L[2]
                    pixel_info['NdotL'] = NdotL
                    pixel_info['V_X'] = V[0]
                    pixel_info['V_Y'] = V[1]
                    pixel_info['V_Z'] = V[2]
                    pixel_info['R_X'] = R[0]
                    pixel_info['R_Y'] = R[1]
                    pixel_info['R_Z'] = R[2]
                    pixel_info['RdotV'] = RdotV
                    pixel_info['RdotV_elevado'] = RdotV ** n_brilho
                else:
                    pixel_info['Intersecao'] = 'Não'
                    pixel_info['t'] = 'N/A'
                    pixel_info['Ponto_X'] = 'N/A'
                    pixel_info['Ponto_Y'] = 'N/A'
                    pixel_info['Ponto_Z'] = 'N/A'
                    pixel_info['Normal_X'] = 'N/A'
                    pixel_info['Normal_Y'] = 'N/A'
                    pixel_info['Normal_Z'] = 'N/A'
                    pixel_info['I_Ambiente'] = 0.0
                    pixel_info['I_Difusa'] = 0.0
                    pixel_info['I_Especular'] = 0.0
                    pixel_info['I_Total'] = 0.0
                    pixel_info['Luz_X'] = 'N/A'
                    pixel_info['Luz_Y'] = 'N/A'
                    pixel_info['Luz_Z'] = 'N/A'
                    pixel_info['L_X'] = 'N/A'
                    pixel_info['L_Y'] = 'N/A'
                    pixel_info['L_Z'] = 'N/A'
                    pixel_info['NdotL'] = 'N/A'
                    pixel_info['V_X'] = 'N/A'
                    pixel_info['V_Y'] = 'N/A'
                    pixel_info['V_Z'] = 'N/A'
                    pixel_info['R_X'] = 'N/A'
                    pixel_info['R_Y'] = 'N/A'
                    pixel_info['R_Z'] = 'N/A'
                    pixel_info['RdotV'] = 'N/A'
                    pixel_info['RdotV_elevado'] = 'N/A'
                
            dados.append(pixel_info)
        
    # Cria DataFrame
    dataframe = pd.DataFrame(dados)
        
    # Reorganiza as colunas para melhor visualização
    colunas_ordenadas = [
        'Pixel_Index', 'Pixel_Row', 'Pixel_Col',
        'Pixel_X', 'Pixel_Y', 'Pixel_Z',
        'Raio_Dir_X', 'Raio_Dir_Y', 'Raio_Dir_Z',
        'Coef_a', 'Coef_b', 'Coef_c', 'Delta',
        'Intersecao', 't',
        'Ponto_X', 'Ponto_Y', 'Ponto_Z',
        'Normal_X', 'Normal_Y', 'Normal_Z',
        'Luz_X', 'Luz_Y', 'Luz_Z',
        'L_X', 'L_Y', 'L_Z', 'NdotL',
        'V_X', 'V_Y', 'V_Z',
        'R_X', 'R_Y', 'R_Z', 'RdotV', 'RdotV_elevado',
        'I_Ambiente', 'I_Difusa', 'I_Especular', 'I_Total'
    ]
    dataframe = dataframe[colunas_ordenadas]
        
    # Salva em Excel com nome único para evitar conflito de arquivo aberto
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f'raytracing_calculos_detalhados_{timestamp}.xlsx'
        
    with pd.ExcelWriter(nome_arquivo, engine='openpyxl') as writer:
        dataframe.to_excel(writer, sheet_name='Cálculos Completos', index=False)
            
        # Cria uma planilha resumida apenas com pixels que intersectam
        df_intersecoes = dataframe[dataframe['Intersecao'] == 'Sim'].copy()
        df_intersecoes.to_excel(writer, sheet_name='Apenas Interseções', index=False)
            
        # Cria planilha com resumo estatístico
        resumo = {
            'Total de Pixels': [len(dataframe)],
            'Pixels com Interseção': [len(df_intersecoes)],
            'Pixels sem Interseção': [len(dataframe) - len(df_intersecoes)],
            'Intensidade Média': [df_intersecoes['I_Total'].mean() if len(df_intersecoes) > 0 else 0],
            'Intensidade Mínima': [df_intersecoes['I_Total'].min() if len(df_intersecoes) > 0 else 0],
            'Intensidade Máxima': [df_intersecoes['I_Total'].max() if len(df_intersecoes) > 0 else 0]
        }
        df_resumo = pd.DataFrame(resumo)
        df_resumo.to_excel(writer, sheet_name='Resumo', index=False)
        
    print(f"✓ Planilha salva: {nome_arquivo}")
    print(f"✓ Total de pixels analisados: {len(dataframe)}")
    print(f"✓ Pixels com interseção: {len(df_intersecoes)}")
    print(f"✓ Planilhas criadas:")
    print("="*60)
        
    return dataframe

def renderizar(modo='completo'):
    """
    Renderiza a cena completa, gerando uma imagem do plano de projeção.

    Parâmetros:
    - modo: tipo de sombreamento ('ambiente', 'difuso', 'especular', 'completo')
    """
    # Cria a imagem (matriz de pixels)
    imagem = np.zeros((height, width))
    
    # Para cada pixel da imagem
    for i in range(height):
        for j in range(width):
            # ========== ETAPA 1: GERAÇÃO DOS RAIOS ==========
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
            
            # Direção do raio: da câmera ao pixel (normalizado)
            direcao_raio = normalize(pixel_pos - eye)
            
            # ========== ETAPA 2: INTERSEÇÃO RAIO-OBJETO ==========
            # Verifica interseção com a esfera
            t = intersect_esfera(eye, direcao_raio, centro_esfera, raio_esfera)
            
            if t is not None:
                # Ponto de interseção
                ponto = eye + t * direcao_raio
                
                # Normal à superfície (aponta para fora da esfera)
                normal = normalize(ponto - centro_esfera)
                
                # ========== ETAPA 3: SOMBREAMENTO ==========
                # Calcula a intensidade usando modelo Phong
                intensidade = intensidade_phong(ponto, normal, direcao_raio, modo)
                
                # Armazena o valor do pixel
                imagem[i, j] = intensidade
            else:
                # Sem interseção - pixel preto (fundo)
                imagem[i, j] = 0.0
    
    return imagem


if __name__ == "__main__":
    print("="*60)
    print("RAY TRACING - RENDERIZANDO ESFERA COM ILUMINAÇÃO PHONG")
    print("="*60)
    print(f"Resolução: {width}x{height} pixels")
    print(f"Câmera em: {eye}")
    print(f"Distância focal: {df}")
    print(f"FOV: {fov_deg}°")
    print(f"Esfera: centro={centro_esfera}, raio={raio_esfera}")
    print()
    
    # Renderiza as 3 componentes do sombreamento + completo
    imagem_ambiente = renderizar(modo='ambiente')
    imagem_difuso = renderizar(modo='difuso')
    imagem_especular = renderizar(modo='especular')
    imagem_completo = renderizar(modo='completo')
    
    # GERA A PLANILHA COM OS CÁLCULOS DETALHADOS
    df_calculos = gerar_planilha_calculos()

    # Cria figura com 4 subplots (3 componentes + completo)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Componente Ambiente
    axes[0, 0].imshow(imagem_ambiente, cmap='gray', vmin=0, vmax=1)
    axes[0, 0].set_title('Ambiente\n(Iluminação Base)', fontsize=10, fontweight='bold')
    axes[0, 0].axis('off')
    
    # Componente Difuso
    axes[0, 1].imshow(imagem_difuso, cmap='gray', vmin=0, vmax=1)
    axes[0, 1].set_title('Difuso\n(Ambiente + Difusa)', fontsize=10, fontweight='bold')
    axes[0, 1].axis('off')
    
    # Componente Especular
    axes[1, 0].imshow(imagem_especular, cmap='gray', vmin=0, vmax=1)
    axes[1, 0].set_title('Especular\n(Ambiente + Especular)', fontsize=10, fontweight='bold')
    axes[1, 0].axis('off')
    
    # Phong Completo
    axes[1, 1].imshow(imagem_completo, cmap='gray', vmin=0, vmax=1)
    axes[1, 1].set_title('Phong Completo\n(Ambiente + Difusa + Especular)', fontsize=10, fontweight='bold')
    axes[1, 1].axis('off')
    
    plt.suptitle(f'Ray Tracing - Modelo de Iluminação Phong\nResolução: {width}x{height}, FOV: {fov_deg}°, df: {df}', 
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    # Salva a imagem comparativa
    plt.savefig('raytracing_phong_completo.png', dpi=150, bbox_inches='tight')
    
    # Salvar apenas a imagem completa
    # plt.figure(figsize=(8, 8))
    # plt.imshow(imagem_completo, cmap='gray', vmin=0, vmax=1)
    # plt.title(f'Ray Tracing - Esfera (Phong Completo)\nResolução: {width}x{height}, FOV: {fov_deg}°, df: {df}')
    # plt.colorbar(label='Intensidade')
    # plt.axis('off')
    # plt.tight_layout()
    # plt.savefig('raytracing_esfera.png', dpi=150, bbox_inches='tight') # Salva imagem
    
    # Mostra as imagens
    plt.show()
    
    print("\n" + "="*60)
    print("ETAPAS DO RAY TRACING IMPLEMENTADAS:")
    print("="*60)
    print("1. GERAÇÃO DOS RAIOS:")
    print("   - Calcula posição de cada pixel no plano de projeção")
    print("   - Cria raio da câmera passando pelo pixel")
    print()
    print("2. INTERSEÇÃO RAIO-OBJETO:")
    print("   - Resolve equação quadrática raio-esfera")
    print("   - Encontra ponto de interseção mais próximo")
    print()
    print("3. SOMBREAMENTO (Modelo Phong):")
    print("   - Componente Ambiente: iluminação base constante")
    print("   - Componente Difusa: depende do ângulo luz-normal")
    print("   - Componente Especular: cria reflexo brilhante")
    print("="*60)