## 📚 Sobre o Projeto

Este projeto é uma implementação prática dos conceitos de Ray Tracing, desenvolvida como parte da avaliação da disciplina de Computação Gráfica do curso de Ciência da Computação da **UERN - Universidade do Estado do Rio Grande do Norte**, ministrada pela Profa. Adriana Takahashi.

O objetivo é construir um renderizador simples capaz de simular o trajeto da luz em uma cena virtual para gerar uma imagem 2D. A cena é composta por uma câmera, uma fonte de luz e um objeto (uma esfera).

##  Funcionalidades 

- **Câmera Virtual**: Posição e orientação da câmera no espaço 3D.
- **Plano de Projeção**: Geração de uma grade de pixels para a imagem final.
- **Geração de Raios**: Cálculo da direção de cada raio partindo da câmera através do plano de projeção.
- **Interseção Raio-Esfera**: Detecção matemática da colisão de um raio com a superfície de uma esfera.
- **Modelo de Iluminação de Phong**: Cálculo da cor de cada pixel com base nos componentes de iluminação ambiente, difusa e especular.
- **Renderização de Imagem**: Geração e exibição da imagem final a partir da matriz de pixels calculada.

