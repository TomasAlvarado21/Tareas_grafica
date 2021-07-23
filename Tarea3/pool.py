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

class Movimientodelbarco():
    def __init__(self, size):
        self.pos = [0, 0]
        self.vel = 1
        self.model = None # Referencia al grafo de escena asociado
        self.controller = None # Referencia del controlador, para acceder a sus variables
        self.size = size # Escala a aplicar al nodo 
        self.radio = 0.1 # distancia para realiozar los calculos de colision
        self.curva = []
        self.delta = 0
        #self.pos_x = []

    def set_curva(self, new_curva):
        self.curva = new_curva
        self.pos = [new_curva[0][0], new_curva[0][1]]
        self.delta = 2/(len(self.curva))
        #self.pos_x = range(len(self.curva)-1)

    def set_model(self, new_model):
        # Se obtiene una referencia a uno nodo
        self.model = new_model

    def set_controller(self, new_controller):
        # Se obtiene la referncia al controller
        self.controller = new_controller

    def update(self):
        if self.vel > len(self.curva)-1:
            self.vel = 1 

        if self.controller.is_h_pressed == True:
            self.pos = [-1 + self.delta*self.vel, self.curva[self.vel][1] - 0.05]
            self.vel += 1
        
        
        if self.controller.is_h_pressed == False:
            self.pos = [-1 + self.delta*self.vel, self.curva[self.vel][1] - 0.05]
        
        self.model.transform = tr.matmul([tr.translate(self.pos[0], self.pos[1], 0.02), tr.scale(self.size, self.size, self.size)])

############################################################################

def CurvaRio(N):
    
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

def createRio(r,g,b):
    
    vertices = []
    indices = []

    curve = CurvaRio(84)
    delta = 2/(len(curve))
    counter = 0
    for i in range(len(curve)-1):
        y_0 = curve[i]
        y_1 = curve[i+1]
        x_0 = -1.0 + delta*i
        x_1 = -1.0 + delta*(i+1)
        vertices += [x_0, y_0[1], 0.0, r, g, b]
        vertices += [x_1, y_1[1], 0.0, r, g, b]
        vertices += [x_0, y_0[1] - 0.1, 0.001, r, g , b]
        vertices += [x_1, y_1[1] - 0.1, 0.001, r, g , b]
        indices += [counter, counter+1, counter+2]
        indices += [counter+1, counter+2, counter+3]
        counter += 4

    return bs.Shape(vertices, indices)

def create_rio(pipeline):
    # Piramide verde
    rio = createRio(0, 0.1, 1)
    gpurio = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpurio)
    gpurio.fillBuffers(rio.vertices, rio.indices, GL_STATIC_DRAW)
    
    return gpurio


def createColorPyramid(r, g ,b):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #    positions         colors
        -0.5, 0.5,  0,  r, g, b,
         0.5, -0.5, 0,  r, g, b,
         0.5, 0.5,  0,  r, g, b,
        -0.5, -0.5, 0,  r, g, b,
         0, 0,  0.5,  r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
         0, 1, 2,
         0, 1, 3,
         0, 2, 4,
         2, 4, 1,
         3, 4, 1,
         0, 4, 3]

    return bs.Shape(vertices, indices)


def reflexionX():
    return np.array([
        [-1,0,0,0],
        [0,1,0,0],
        [0,0,1,0],
        [0,0,0,1]], dtype = np.float32)


def create_proa_barco(r, g, b):

    vertices = [
    #    positions         colors
         0.0, 0.5, -0.5,  r, g, b,
         0.0, -0.5, -0.5,  r, g, b,
         0.0, -0.5, 0.5,  r, g, b,
         0.0, 0.5, 0.5,  r, g, b,
         0.5, 0.0,  0.5,  r, g, b]

    indices = [
         0, 1, 2,
         0, 2, 3,
         0, 1, 4,
         1, 2, 4,
         2, 3, 4,
         0, 3, 4]

    return bs.Shape(vertices, indices)

def create_barco(pipeline):


    base = bs.createColorCube(0.75, 0.54, 0.33)
    gpubase = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpubase)
    gpubase.fillBuffers(base.vertices, base.indices, GL_STATIC_DRAW)

    baseNodo = sg.SceneGraphNode("base")
    baseNodo.transform = tr.matmul([tr.translate(0, 0, 0.01), tr.scale(0.7, 0.5, 0.3)])
    baseNodo.childs = [gpubase]

    BarcoNodo = sg.SceneGraphNode("barco")
    BarcoNodo.transform = tr.matmul([
        tr.translate(0, 0, 0), 
        tr.scale(0.7, 0.7, 0.3)
        ])
    BarcoNodo.childs = [baseNodo]

    return BarcoNodo







def create_tree(pipeline):
    # Piramide verde
    green_pyramid = createColorPyramid(0, 1, 0)
    gpuGreenPyramid = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuGreenPyramid)
    gpuGreenPyramid.fillBuffers(green_pyramid.vertices, green_pyramid.indices, GL_STATIC_DRAW)

    # Cubo cafe
    brown_quad = bs.createColorCube(139/255, 69/255, 19/255)
    gpuBrownQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownQuad)
    gpuBrownQuad.fillBuffers(brown_quad.vertices, brown_quad.indices, GL_STATIC_DRAW)

    # Tronco
    tronco = sg.SceneGraphNode("tronco")
    tronco.transform = tr.scale(0.05, 0.05, 0.2)
    tronco.childs += [gpuBrownQuad]

    # Hojas
    hojas = sg.SceneGraphNode("hojas")
    hojas.transform = tr.matmul([tr.translate(0, 0, 0.1), tr.uniformScale(0.25)])
    hojas.childs += [gpuGreenPyramid]

    # Arbol
    tree = sg.SceneGraphNode("arbol")
    tree.transform = tr.identity()
    tree.childs += [tronco, hojas]

    return tree


def create_house(pipeline):
    # Piramide cafe
    brown_pyramid = createColorPyramid(166/255, 112/255, 49/255)
    gpuBrownPyramid = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownPyramid)
    gpuBrownPyramid.fillBuffers(brown_pyramid.vertices, brown_pyramid.indices, GL_STATIC_DRAW)

    # Cubo rojo
    red_cube = bs.createColorCube(1, 0, 0)
    gpuRedCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuRedCube)
    gpuRedCube.fillBuffers(red_cube.vertices, red_cube.indices, GL_STATIC_DRAW)

    # Cubo cafe
    brown_cube = bs.createColorCube(166/255, 112/255, 49/255)
    gpuBrownCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBrownCube)
    gpuBrownCube.fillBuffers(brown_cube.vertices, brown_cube.indices, GL_STATIC_DRAW)

    # Techo
    techo = sg.SceneGraphNode("techo")
    techo.transform = tr.matmul([
        tr.translate(0, 0, 0.1), tr.scale(0.2, 0.4, 0.2)])
    techo.childs += [gpuBrownPyramid]

    # Base
    base = sg.SceneGraphNode("base")
    base.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(0.2, 0.4, 0.2)])
    base.childs += [gpuRedCube]

    # Puerta
    puerta = sg.SceneGraphNode("puerta")
    puerta.transform = tr.matmul([tr.translate(0, -0.2, 0), tr.scale(0.05, 0.001, 0.1)])
    puerta.childs += [gpuBrownCube]

    # Casa
    casa = sg.SceneGraphNode("house")
    casa.transform = tr.identity()
    casa.childs += [techo, base, puerta]

    return casa

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

def create_decorations(pipeline):
    tree1 = create_tree(pipeline)
    tree1.transform = tr.translate(0.5, 0, 0)

    tree2 = create_tree(pipeline)
    tree2.transform = tr.translate(-0.5, 0, 0)

    tree3 = create_tree(pipeline)
    tree3.transform = tr.translate(0.5, 0.5, 0)

    tree4 = create_tree(pipeline)
    tree4.transform = tr.translate(-0.2, 0.5, 0)

    tree5 = create_tree(pipeline)
    tree5.transform = tr.translate(0.2, 0.5, 0)

    house = create_house(pipeline)
    house.transform = tr.translate(0, 0.5, 0)

    decorations = sg.SceneGraphNode("decorations")
    decorations.transform = tr.identity()
    decorations.childs += [tree1, tree2, tree3, tree4, tree5, house]    

    return decorations

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

    decorations = create_decorations(colorShaderProgram)
    skybox = create_skybox(textureShaderProgram)
    floor = create_floor(textureShaderProgram)
    escena_rio = dibujo_de_rio(colorShaderProgram)
    barco_mov = create_barco(colorShaderProgram)

    coor_curva = CurvaRio(686)
    
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

        # Drawing (no texture)
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        

        sg.drawSceneGraphNode(decorations, colorShaderProgram, "model")
        
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        
        sg.drawSceneGraphNode(escena_rio, colorShaderProgram, "model")

        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        
        sg.drawSceneGraphNode(movimiento_barco.model, colorShaderProgram, "model")

        # Drawing dice (with texture, another shader program)
        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        

        sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")
        sg.drawSceneGraphNode(floor, textureShaderProgram, "model")       

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()