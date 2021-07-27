import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
from grafica.assets_path import getAssetPath



############################################################################



def create_skybox(pipeline):
    shapeSky = bs.createTextureCube('paisaje.jfif')
    gpuSky = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSky)
    gpuSky.fillBuffers(shapeSky.vertices, shapeSky.indices, GL_STATIC_DRAW)
    gpuSky.texture = es.textureSimpleSetup(
        getAssetPath("bar1.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    skybox = sg.SceneGraphNode("skybox")
    skybox.transform = tr.matmul([tr.translate(0, 0, 0.3), tr.uniformScale(2)])
    skybox.childs += [gpuSky]

    return skybox

def create_floor(pipeline):
    shapeFloor = bs.createTextureQuad(8, 8)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.texture = es.textureSimpleSetup(
        getAssetPath("Piso.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, 0),tr.scale(2, 2, 1)])
    floor.childs += [gpuFloor]

    return floor

def create_mesa(pipeline):
    shapeMesa = bs.createTextureQuad(1, 1)
    gpuMesa = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuMesa)
    gpuMesa.texture = es.textureSimpleSetup(
        getAssetPath("mesaPool.png"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuMesa.fillBuffers(shapeMesa.vertices, shapeMesa.indices, GL_STATIC_DRAW)
    mesa = sg.SceneGraphNode("mesa")
    mesa.transform = tr.matmul([tr.translate(0, 0, 0.05),tr.scale(0.75,0.5,0)])
    print(shapeMesa.vertices)
    mesa.childs += [gpuMesa]

    return mesa

def create_pata(pipeline):
    pata = bs.createColorQuad(1,0,0.5)
    gpuPata = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuPata)
    gpuPata.fillBuffers(pata.vertices, pata.indices, GL_STATIC_DRAW)

    return pata

def create_patas(pipeline):
    pata1 = create_pata(pipeline)
    pata1.transform = tr.translate(0.5,0,0)

    pata2 = create_pata(pipeline)
    pata2.transform = tr.translate(0.5,0.5,0)

    patas = sg.SceneGraphNode("patas")
    patas.transform = tr.identity()
    patas.childs += [pata1, pata2]

    return patas

############################################################################

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
###########################################################
        self.theta = np.pi
        self.eye = [0, 0, 0.1]
        self.at = [0, 1, 0.1]
        self.up = [0, 0, 1]
        self.is_h_pressed = False
###########################################################


# global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS and action != glfw.REPEAT:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_H:
        if action ==glfw.PRESS:
            controller.is_h_pressed = True
        elif action == glfw.RELEASE:
            controller.is_h_pressed = False

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    
###########################################################

    elif key == glfw.KEY_W:
        controller.eye += (controller.at - controller.eye) * 0.05
        controller.at += (controller.at - controller.eye) * 0.05
    elif key == glfw.KEY_S:
        controller.eye -= (controller.at - controller.eye) * 0.05
        controller.at -= (controller.at - controller.eye) * 0.05
    elif key == glfw.KEY_D:
        controller.theta -= np.pi*0.05
    elif key == glfw.KEY_A:
        controller.theta += np.pi*0.05

###########################################################
    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Pool", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs for textures and for colors
    textureShaderProgram = es.SimpleTextureModelViewProjectionShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

###########################################################################################
    # Creating shapes on GPU memory

    skybox = create_skybox(textureShaderProgram)
    floor = create_floor(textureShaderProgram)
    mesa = create_mesa(textureShaderProgram)
    patas_mesa = create_patas(colorShaderProgram)
    
    


###########################################################################################

    # View and projection
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        

###########################################################################

        at_x = controller.eye[0] + np.cos(controller.theta)
        at_y = controller.eye[1] + np.sin(controller.theta)
        controller.at = np.array([at_x, at_y, controller.at[2]])
        view = tr.lookAt(controller.eye, controller.at, controller.up)

###########################################################################
       
        

        # Drawing dice (with texture, another shader program)
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        

        sg.drawSceneGraphNode(patas_mesa, colorShaderProgram, "model")


        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        

        sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")
        sg.drawSceneGraphNode(floor, textureShaderProgram, "model")
        sg.drawSceneGraphNode(mesa, textureShaderProgram, "model")       

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()