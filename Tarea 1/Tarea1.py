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


SIZE_IN_BYTES = 4


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



def createBorder(N):
    dtheta = 2 * math.pi / N
    # First vertex at the center, white color
    vertices = [0.5 * math.cos(dtheta), 0.5 * math.sin(dtheta), 0, 0.9,       0.9, 0.9]
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
