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
import grafica.ex_curves as cv


############################################################################

def CurvaTobogan(N):
    
    P0 = np.array([[-1.3, -0.4, 0]]).T
    P1 = np.array([[-1.1, -0.299, 0]]).T
    P2 = np.array([[-0.341, -0.129, 0]]).T
    P3 = np.array([[0.121, -0.313, 0]]).T
    P4 = np.array([[0.55, -0.36, 0]]).T
    P5 = np.array([[1.12, -0.39, 0]]).T
    P6 = np.array([[1.44, -0.51, 0]]).T
    P7 = np.array([[1.93, -0.31, 0]]).T
    P8 = np.array([[2.33, -0.43, 0]]).T
    P9 = np.array([[2.46, -0.22, 0]]).T
    
    CM1 = cv.CatmullMatrix(P0, P1, P2, P3)
    CM2 = cv.CatmullMatrix(P1, P2, P3, P4)
    CM3 = cv.CatmullMatrix(P2, P3, P4, P5)
    CM4 = cv.CatmullMatrix(P3, P4, P5, P6)
    CM5 = cv.CatmullMatrix(P4, P5, P6, P7)
    CM6 = cv.CatmullMatrix(P5, P6, P7, P8)
    CM7 = cv.CatmullMatrix(P6, P7, P8, P9)

    ts = np.linspace(0.0, 1.0, N//7)
    offset = N//7
    
    curve = np.ndarray(shape=(len(ts) * 7, 3), dtype=float)
    
    for i in range(len(ts)):
        T = cv.generateT(ts[i])
        curve[i, 0:3] = np.matmul(CM1, T).T
        curve[i + offset, 0:3] = np.matmul(CM2, T).T
        curve[i + 2*offset, 0:3] = np.matmul(CM3, T).T
        curve[i + 3*offset, 0:3] = np.matmul(CM4, T).T
        curve[i + 4*offset, 0:3] = np.matmul(CM5, T).T
        curve[i + 5*offset, 0:3] = np.matmul(CM6, T).T
        curve[i + 6*offset, 0:3] = np.matmul(CM7, T).T
          
    return curve


def tobogan(N):
    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    R = 0.5
    rho = 0.2
    c = 0

    for i in range(N):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [(R+rho*np.cos(phi))*np.cos(theta), (R+rho*np.cos(phi))*np.sin(theta), rho*np.sin(phi)]
            v1 = [(R+rho*np.cos(phi1))*np.cos(theta), (R+rho*np.cos(phi1))*np.sin(theta), rho*np.sin(phi1)]
            v2 = [(R+rho*np.cos(phi))*np.cos(theta1), (R+rho*np.cos(phi))*np.sin(theta1), rho*np.sin(phi)]
            v3 = [(R+rho*np.cos(phi1))*np.cos(theta1), (R+rho*np.cos(phi1))*np.sin(theta1), rho*np.sin(phi1)]
            n0 = [np.cos(theta)*np.cos(phi), np.sin(theta)*np.cos(phi), np.sin(theta)]
            n1 = [np.cos(theta)*np.cos(phi1), np.sin(theta)*np.cos(phi1), np.sin(theta)]
            n2 = [np.cos(theta1)*np.cos(phi), np.sin(theta1)*np.cos(phi), np.sin(theta1)]
            n3 = [np.cos(theta1)*np.cos(phi1), np.sin(theta1)*np.cos(phi1), np.sin(theta1)]

            vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 1, c + 2, c + 3 ]
            c += 4

    return bs.Shape(vertices, indices)


def create_skybox(pipeline):
    shapeSky = bs.createTextureCube('paisaje.jfif')
    gpuSky = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSky)
    gpuSky.fillBuffers(shapeSky.vertices, shapeSky.indices, GL_STATIC_DRAW)
    gpuSky.texture = es.textureSimpleSetup(
        getAssetPath("paisaje2.jfif"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    skybox = sg.SceneGraphNode("skybox")
    skybox.transform = tr.matmul([tr.translate(0, 0, 0.3), tr.uniformScale(2)])
    skybox.childs += [gpuSky]

    return skybox

def create_floor(pipeline):
    shapeFloor = bs.createTextureQuad(8, 8)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.texture = es.textureSimpleSetup(
        getAssetPath("grass.jfif"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, 0),tr.scale(2, 2, 1)])
    floor.childs += [gpuFloor]

    return floor



def dibujo_de_rio(pipeline):
    gpuRio = create_rio(pipeline)

    rioNode = sg.SceneGraphNode("rio")
    rioNode.transform = tr.identity()
    rioNode.childs = [gpuRio]

    EscenaRioNode = sg.SceneGraphNode("EscenaRio")
    EscenaRioNode.transform = tr.identity()
    EscenaRioNode.childs = [rioNode]

    return EscenaRioNode    




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

    window = glfw.create_window(width, height, "Dice", None, None)

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
    escena_tobogan = dibujo_de_tobogan(colorShaderProgram)
    barco_mov = create_barco(colorShaderProgram)

    coor_curva = CurvaTobogan(686)
    
    mov_boat = sg.findNode(barco_mov, "barco")
    
    movimiento_barco = Movimientodelbarco(0.1)
    movimiento_barco.set_curva(coor_curva)
    movimiento_barco.set_model(mov_boat)
    movimiento_barco.set_controller(controller)


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

        movimiento_barco.update()

###########################################################################

        at_x = controller.eye[0] + np.cos(controller.theta)
        at_y = controller.eye[1] + np.sin(controller.theta)
        controller.at = np.array([at_x, at_y, controller.at[2]])
        view = tr.lookAt(controller.eye, controller.at, controller.up)

###########################################################################

          

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
