"""P1) [Esquema directo de Colores] 
Dibuje una escena simple de un auto, indicando directamente un color RGB en cada componente de la matriz a visualizar."""

import numpy as np
import sira

def draw_rectangle(matrix, x, y, width, height, rgb):
    matrix[x:x + width, y:y + height] = np.array(rgb, dtype=np.uint8)

if __name__ == "__main__":
    
    S = 14
    W = 60
    H = 40
    windowSize = (W*S, H*S)

    # Se crea la matriz
    imgData = np.zeros((W, H, 3), dtype=np.uint8)

    # Se pinta la matriz completa con el color del fondo
    imgData[:, :] = np.array([0,255,255], dtype=np.uint8)
    # Se pinta el suelo
    draw_rectangle(imgData, x=0, y=28, width=60, height=12, rgb=[120,120,120])
    # Se pinta la primera parte de la carroceria
    draw_rectangle(imgData, x=12, y=25, width=37, height=8, rgb=[255,0,0])
    # Se pinta la segunda parte de la carroceria
    draw_rectangle(imgData, x=20, y=17, width=21, height=8, rgb=[255,0,0])
    # Se pinta la primera rueda
    draw_rectangle(imgData, x=18, y=30, width=7, height=7, rgb=[50,50,50])
    # Se pinta la segunda rueda
    draw_rectangle(imgData, x=36, y=30, width=7, height=7, rgb=[50,50,50])
    # Se pinta la primera ventana
    draw_rectangle(imgData, x=32, y=19, width=9, height=6, rgb=[0,150,255])
    
    display = sira.DirectRGBRasterDisplay(windowSize, imgData.shape, "P1: Esquema directo de colores")
    display.setMatrix(imgData)
    display.draw()
