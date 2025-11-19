## 📚 Sobre o Projeto

Este projeto é uma implementação prática dos conceitos de Ray Tracing, desenvolvida como parte da avaliação da disciplina de Computação Gráfica do curso de Ciência da Computação da **UERN - Universidade do Estado do Rio Grande do Norte**, ministrada pela Profa. Adriana Takahashi.

O objetivo é construir um renderizador simples capaz de simular o trajeto da luz em uma cena virtual para gerar uma imagem 2D. A cena é composta por uma câmera, uma fonte de luz e um objeto (uma esfera).

## 🔧 Funcionalidades 

- **Câmera Virtual**: Posição e orientação da câmera no espaço 3D.
- **Plano de Projeção**: Geração de uma grade de pixels para a imagem final.
- **Geração de Raios**: Cálculo da direção de cada raio partindo da câmera através do plano de projeção.
- **Interseção Raio-Esfera**: Detecção matemática da colisão de um raio com a superfície de uma esfera.
- **Modelo de Iluminação de Phong**: Cálculo da cor de cada pixel com base nos componentes de iluminação ambiente, difusa e especular.
- **Renderização de Imagem**: Geração e exibição da imagem final a partir da matriz de pixels calculada.
- **Geração de Planilha**: Exportação detalhada de todos os cálculos realizados para análise em Excel.

---

## ⚙️ Parâmetros de Configuração

### Cenário Utilizado
- **Câmera**: Posicionada em `(-10.0, 0.0, 0.0)`
- **Distância Focal (df)**: `10.0` unidades
- **Campo de Visão (FOV)**: `90°`
- **Plano de Projeção**: `20x20` unidades (em x=0)
- **Esfera**: Centro em `(5.0, 0.0, 0.0)`, raio `2.0` unidades
- **Fonte de Luz**: Posicionada em `(-5.0, 5.0, 5.0)`

### Coeficientes de Iluminação Phong
- **Ambiente (k_ambiente)**: `0.1` (10% de iluminação base)
- **Difusa (k_difusa)**: `0.6` (60% de contribuição difusa)
- **Especular (k_especular)**: `0.3` (30% de contribuição especular)
- **Expoente de Brilho (n)**: `32`

---

## 📊 Resultados dos Testes

### **Teste 1: Resolução Baixa (5x5 pixels)**

#### Parâmetros
```python
width, height = 5, 5
```

#### Objetivo
Este teste demonstra o funcionamento básico do ray tracing com uma resolução muito baixa, permitindo análise detalhada de cada pixel individualmente.

#### Resultados Visuais
![Renderização 5x5](/Testes/Figure_20251020_172504.png)

Como observado na imagem, com apenas **25 pixels** totais:
- A esfera é representada por **apenas 1 pixel** central
- Não é possível visualizar a forma esférica
- Componentes de iluminação Phong são aplicadas apenas no pixel com interseção

#### Análise Detalhada dos Cálculos

**Dados Gerais:**
- **Total de Pixels**: 25
- **Pixels com Interseção**: 1 (pixel central na posição [2, 2])
- **Pixels sem Interseção**: 24 (fundo preto)

**Pixel com Interseção (Pixel #13):**

| Parâmetro | Valor |
|-----------|-------|
| **Posição no Plano** | (0.0, 0.0, 0.0) |
| **Direção do Raio** | (0.832, 0.0, 0.0) normalizado |
| **Coeficientes da Equação** | a=1.0, b=-24.98, c=221.0 |
| **Delta (Δ)** | 39.92 (positivo → há interseção) |
| **Distância t** | ~12.37 unidades |
| **Ponto de Interseção** | (~3.0, 0.0, 0.0) |
| **Normal** | (-1.0, 0.0, 0.0) normalizada |
| **Vetor Luz (L)** | Normalizado de ponto → luz |
| **N·L (NdotL)** | Produto escalar para iluminação difusa |
| **Vetor Visão (V)** | Oposto à direção do raio |
| **Vetor Reflexão (R)** | Calculado: 2(N·L)N - L |
| **R·V (RdotV)** | Produto escalar para especular |
| **I_Ambiente** | 0.1 |
| **I_Difusa** | Variável (depende do ângulo) |
| **I_Especular** | Variável (depende da reflexão) |
| **I_Total** | Soma das componentes |

**Pixels sem Interseção (24 pixels):**
- Todas as colunas de interseção marcadas como `N/A`
- Intensidades: `I_Ambiente = 0.0`, `I_Difusa = 0.0`, `I_Especular = 0.0`, `I_Total = 0.0`
- Representam o fundo preto da cena

**Arquivo Gerado:** `raytracing_calculos_detalhados_20251020_172504.xlsx` com 3 abas:
1. **Cálculos Completos**: Todos os 25 pixels com 39 colunas de dados
2. **Apenas Interseções**: Somente o pixel que acerta a esfera
3. **Resumo**: Estatísticas gerais da renderização

---

### **Teste 2: Resolução Alta (500x500 pixels)**

#### Parâmetros
```python
width, height = 500, 500
```

#### Objetivo
Demonstrar a qualidade visual do ray tracing com alta resolução, permitindo visualização clara da forma esférica e gradientes de iluminação.

#### Resultados Visuais
![Renderização 500x500](/Testes/Figure_20251020_171556.png)

Com **250.000 pixels** totais, a diferença é notável:
- A esfera é claramente visível com forma circular bem definida
- Gradientes de iluminação suaves e realistas
- Componente especular cria um brilho destacado (highlight)
- Transição suave entre as componentes ambiente, difusa e especular

#### Estatísticas da Renderização

| Métrica | Valor |
|---------|-------|
| **Total de Pixels** | 250.000 |
| **Pixels com Interseção** | 3.560 (~1,4% da imagem) |
| **Pixels sem Interseção** | 246.440 (fundo preto) |
| **Intensidade Média** | 0,413761347 |
| **Intensidade Mínima** | 0,1 (apenas componente ambiente) |
| **Intensidade Máxima** | 0,96194244 (regiões com forte especular) |

#### Observações
- Cada pixel representa apenas **0,04x0,04** unidades do plano (vs. **4x4** unidades no teste 1)
- A esfera ocupa aproximadamente **3.560 pixels**, formando um círculo perfeito
- A distribuição de intensidades mostra o gradiente de iluminação Phong funcionando corretamente
- O ponto mais brilhante (0,96) ocorre onde há alinhamento ideal entre visão, normal e reflexão da luz

---

## 📈 Comparação Entre Resoluções

| Aspecto | 5x5 pixels | 500x500 pixels |
|---------|-----------|----------------|
| **Total de Pixels** | 25 | 250.000 |
| **Tamanho do Pixel** | 4x4 unidades | 0,04x0,04 unidades |
| **Pixels na Esfera** | 1 | 3.560 |
| **Visualização** | Imperceptível | Clara e detalhada |
| **Gradientes** | Não visíveis | Suaves e realistas |
| **Tempo de Cálculo** | Instantâneo | ~ 3 minutos |
| **Tamanho da Planilha** | 25 linhas | 250.000 linhas |

---

## 🔬 Testes de Parâmetros da Câmera

### **Teste 3: Aproximação da Câmera (eye = 0, 0, 0) com FOV = 90°**

#### Parâmetros
```python
eye = np.array([0.0, 0.0, 0.0])
df = 10.0
fov_deg = 90.0
width, height = 500, 500
```

#### Objetivo
Demonstrar o efeito de aproximar a câmera do objeto, movendo-a de `(-10, 0, 0)` para `(0, 0, 0)`.

#### Resultados Visuais
![Câmera em (0, 0, 0) - FOV 90°](/Testes/Figure_eye_000.png)

**Efeito observado:**
- A esfera mantém tamanho similar ao Teste 2
- Distância câmera→esfera reduzida de **15 unidades** para **5 unidades**
- O plano de projeção agora está em `x = 10` (atrás da esfera!)
- Visualização mantém proporção devido ao FOV constante

#### Estatísticas da Renderização

| Métrica | Valor |
|---------|-------|
| **Total de Pixels** | 250.000 |
| **Pixels com Interseção** | 3.560 (~1,4% da imagem) |
| **Pixels sem Interseção** | 246.440 (fundo preto) |
| **Intensidade Média** | 0,413761347 |
| **Intensidade Mínima** | 0,1 (componente ambiente) |
| **Intensidade Máxima** | 0,96194244 |

**Comparação com Teste 2:**
- **Mesmo número de pixels** com interseção (3.560)
- Intensidades praticamente idênticas
- A esfera ocupa **1,4%** da imagem (igual ao Teste 2)
- Posição da câmera não afeta proporção devido ao sistema FOV vinculado

---

### **Teste 4: Zoom com FOV Reduzido (eye = 0, 0, 0 + FOV = 60°)**

#### Parâmetros
```python
eye = np.array([0.0, 0.0, 0.0])
df = 10.0
fov_deg = 60.0  # REDUZIDO de 90° para 60°
width, height = 500, 500
```

#### Objetivo
Demonstrar o efeito de "zoom" ao reduzir o campo de visão (FOV), mantendo a câmera na mesma posição.

#### Resultados Visuais
![Câmera em (0, 0, 0) - FOV 60°](/Testes/Figure_eye_000_fov_60.png)

**Efeito observado:**
- A esfera **ocupa quase metade da imagem** (~45% da área)
- FOV menor = campo de visão mais estreito = efeito de "zoom in"
- Com FOV=60°, o plano é menor (~11,5x11,5 vs 20x20 com FOV=90°)
- Esfera aparece muito maior e detalhada

#### Estatísticas da Renderização

| Métrica | Valor |
|---------|-------|
| **Total de Pixels** | 250.000 |
| **Pixels com Interseção** | 112.224 (~45% da imagem) |
| **Pixels sem Interseção** | 137.776 (fundo preto) |
| **Intensidade Média** | 0,461705987 |
| **Intensidade Mínima** | 0,1 (componente ambiente) |
| **Intensidade Máxima** | 0,947330796 |

**Comparação com Teste 3:**
- **31,5x mais pixels** com interseção (112.224 vs 3.560)
- Intensidade média **11,5% maior** (0,46 vs 0,41)
- Esfera ocupa **45%** da imagem vs **1,4%** no Teste 3
- Efeito dramático de zoom apenas alterando FOV!

---

## 🎛️ Efeito da Distância Focal (df)

### Por que alterar `df` não produz diferença visual aparente?

Ao modificar a distância focal mantendo o FOV vinculado, ocorre um fenômeno de compensação:

#### **O que acontece matematicamente:**

**Com `df = 10.0`:**
- `half = 10 × tan(45°) = 10.0`
- Plano em `x = -10 + 10 = 0`
- Tamanho do plano: **20×20** unidades

**Com `df = 5.0`:**
- `half = 5 × tan(45°) = 5.0`
- Plano em `x = -10 + 5 = -5`
- Tamanho do plano: **10×10** unidades

**Com `df = 15.0`:**
- `half = 15 × tan(45°) = 15.0`
- Plano em `x = -10 + 15 = 5`
- Tamanho do plano: **30×30** unidades

#### **Por que não vemos diferença visual?**

Embora o plano mude de posição e tamanho, a esfera é capturada proporcionalmente porque:

1. **O campo de visão (FOV) está vinculado ao `df`** pela fórmula: `half = df × tan(FOV/2)`
2. **Quando `df` diminui**: o plano fica menor, **mas também mais próximo**
3. **Quando `df` aumenta**: o plano fica maior, **mas também mais distante**
4. **A proporção angular se mantém similar!**

**Conclusão**: No sistema atual, **alterar a posição da câmera (`eye`)** ou **alterar o FOV** produz efeitos visuais mais evidentes do que alterar apenas `df`.

---

## 🎯 Conclusões

O projeto demonstra com sucesso os princípios fundamentais do ray tracing:

1. **Geração de Raios**: Cada pixel gera um raio da câmera através do plano de projeção
2. **Interseção Raio-Objeto**: Resolução da equação quadrática detecta colisões com a esfera
3. **Sombreamento Phong**: Combina componentes ambiente, difusa e especular para iluminação realista

A diferença entre as resoluções evidencia a importância da densidade de pixels para qualidade visual, ao mesmo tempo que permite análise detalhada dos cálculos em resoluções baixas para fins didáticos.

