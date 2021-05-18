import math
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import text_renderer as tx
import grafica.performance_monitor as pm
import shapes as sh
import glfw


SIZE_IN_BYTES = 4
t = input("file")
f = open("input.csv", "r")


#T = input(T)

class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')

def lector(f):
        l = []
        for i in f:
            i = i.split(",")
            for q in i:
                w = int(q)
                l.append(w)
            print(l)
        for i in lector(f):
            sh.createNodos(i,0,0,pipeline)

def mouse_look_clb(window, xpos, ypos):
    global lastX, lastY

    if first_mouse:
        lastX = xpos
        lastY = ypos

    xoffset = xpos - lastX
    yoffset = lastY - ypos

    lastX = xpos
    lastY = ypos



#clase arbol
class Nodoe:
    def __init__(self, info=""):
        self.info=info

class Nodoi:
    def __init__(self, izq, info, der, pos):
        self.izq=izq
        self.info=info
        self.der=der
        self.pos=pos

class Arbol:
    def __init__(self,raiz=Nodoe()):
        self.raiz=raiz        



if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Creating a glfw window
    width = 800
    height = 800
    title = "Tarea AB"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    
    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    #pipeline2 = es.LINEAS()
    pipeline = es.SimpleTransformShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()
    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.75, 0.75, 0.75, 1.0)
    
    #texto = "4"
    #textoCharSize = 0.1
    #textoShape = tx.textToShape(texto,textoCharSize,textoCharSize)
    gputexto = es.GPUShape().initBuffers()
    #textPipeline.setupVAO(gputexto)
    #gputexto.fillBuffers(textoShape.vertices, textoShape.indices, GL_STATIC_DRAW)
    #gputexto.texture = gpuText3DTexture
    #textoTransform = tr.matmul([
    #    tr.translate(0.9, 0.5, 0)
    #])
    


    color = [1.0,1.0,1.0]
    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    # Application loop
    while not glfw.window_should_close(window):
        # Variables de tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


        


        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Dibujamos el nodo del auto
        #glUseProgram(textPipeline.shaderProgram)
        #glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 0,0,0,1)
        #glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 1,1,1,0)
        #glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, textoTransform)
        #textPipeline.drawCall(gputexto)
        
        #for i in lector(f):
        #    sh.createNodos(i,0,0,pipeline)


        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gputexto.clear()
    
    
    glfw.terminate()
