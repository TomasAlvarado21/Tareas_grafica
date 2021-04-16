# coding=utf-8
"""Drawing 4 shapes with different transformations"""
import math
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import basic_shapes as bs
import easy_shaders as es
import transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4

class Shape:
    def __init__(self, vertices, indices, textureFileName=None):
        self.vertices = vertices
        self.indices = indices
        self.textureFileName = textureFileName

# A class to store the application control
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

def drawCall2(self, gpuShape, mode=GL_LINES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)
        
        # Unbind the current VAO
        glBindVertexArray(0)

def createTrayectoria(N):

    # First vertex at the center, white color
    vertices = []
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  0.9,       0.9, 0.9]

        # A triangle is created using the center, this and the next vertex
        indices += [i,i+1, i+1]

    

    return Shape(vertices, indices)

def createBorder(N):
    dtheta = 2 * math.pi / N
    # First vertex at the center, white color
    vertices = [0.5 * math.cos(dtheta), 0.5 * math.sin(dtheta), 0,0.9,       0.9, 0.9]
    indices = []

    

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  1.0,       0, 0]

        # A triangle is created using the center, this and the next vertex
        indices += [i,i+1]
    indices += [1, N-1]
    

    return Shape(vertices, indices)

def createLuna(N):

    # First vertex at the center, white color
    vertices = [0.5, 0.5, 0, 1.0, 1.0, 1.0]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta)+0.5, 0.5 * math.sin(theta)+0.5, 0,

            # color generates varying between 0 and 1
                  0.9,       0.9, 0.9]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return Shape(vertices, indices)

def createSol(N):

    # First vertex at the center, white color
    vertices = [0, 0, 0, 0.8, 0.8, 0.6]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  0.9,       0.8, 0]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return Shape(vertices, indices)


def createTierra(N):

    # First vertex at the center, white color
    vertices = [0, 0, 0, 0, 0.9, 0]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  0.1,       0.2, 0.8]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return Shape(vertices, indices)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Displaying multiple shapes - Modern OpenGL", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    pipeline2 = es.LINEAS()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0, 0, 0, 1.0)
    
    # Creating shapes on GPU memory
    shapeTrayectoria = createTrayectoria(100)
    gpuTrayectoria = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTrayectoria)
    gpuTrayectoria.fillBuffers(shapeTrayectoria.vertices, shapeTrayectoria.indices, GL_STATIC_DRAW)

    shapeBorder = createBorder(100)
    gpuBorder = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBorder)
    gpuBorder.fillBuffers(shapeBorder.vertices, shapeBorder.indices, GL_STATIC_DRAW)

    shapeCircle = bs.createRainbowCircle(100)
    gpuCircle = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCircle)
    gpuCircle.fillBuffers(shapeCircle.vertices, shapeCircle.indices, GL_STATIC_DRAW)

    shapeSol = createSol(100)
    gpuSol = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSol)
    gpuSol.fillBuffers(shapeSol.vertices, shapeSol.indices, GL_STATIC_DRAW)

    shapeTierra = createTierra(100)
    gpuTierra = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTierra)
    gpuTierra.fillBuffers(shapeTierra.vertices, shapeTierra.indices, GL_STATIC_DRAW)

    shapeLuna = createLuna(20)
    gpuLuna = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuLuna)
    gpuLuna.fillBuffers(shapeLuna.vertices, shapeLuna.indices, GL_STATIC_DRAW)

    

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Using the time as the theta parameter
        
        theta = glfw.get_time()
        
        #Borde/silueta sol
        BorderSolTransform = tr.matmul([
            tr.uniformScale(0.505)
        ])

        #updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, BorderSolTransform)

        pipeline2.drawCall(gpuBorder)
        
        #Borde/silueta Tierra
        BorderTierraTransform = tr.matmul([
            tr.translate(np.cos(theta*0.8)*0.6, np.sin(theta*0.8)*0.6, 0),
            tr.rotationZ(0),
            tr.uniformScale(0.252)
        ])

        #updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, BorderTierraTransform)

        pipeline2.drawCall(gpuBorder)
        
        
        trTierraTransform = tr.matmul([
            tr.uniformScale(1.2)
        ])

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, trTierraTransform)

        pipeline2.drawCall(gpuTrayectoria)

        trLunaTransform = tr.matmul([
            tr.translate(np.cos(theta*0.8)*0.6, np.sin(theta*0.8)*0.6, 0),
            tr.rotationZ(0),
            tr.uniformScale(0.5)
        ])

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, trLunaTransform)

        pipeline2.drawCall(gpuTrayectoria)

        # Luna
        LunaTransform = tr.matmul([
            tr.translate(np.cos(theta*0.8)*0.6 + np.cos(2*theta)*0.2, np.sin(theta*0.8)*0.6 + np.sin(2*theta)*0.2, 0),
            tr.rotationZ(2 * theta),
            tr.uniformScale(0.1)
        ])

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, LunaTransform)

        # drawing function
        pipeline.drawCall(gpuLuna)

        # Another instance of the Tierra
        TierraTransform2 = tr.matmul([
            tr.translate(np.cos(theta*0.8)*0.6, np.sin(theta*0.8)*0.6, 0),
            tr.rotationZ(theta),
            tr.uniformScale(0.25)])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, TierraTransform2)
        pipeline.drawCall(gpuTierra)

        # Sol
        SolTransform = tr.matmul([
            
            tr.rotationZ(-theta/10),
            tr.uniformScale(0.5)
        ])

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, SolTransform)

        # drawing function
        pipeline.drawCall(gpuSol)
        

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
        
    
    gpuCircle.clear()
    gpuSol.clear()
    gpuTierra.clear()
    gpuLuna.clear()

    glfw.terminate()