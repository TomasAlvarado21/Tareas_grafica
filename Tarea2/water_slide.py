from shapes3d import createToboganNode
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
import grafica.lighting_shaders as ls
import openmesh as om 
import ej6
import random
############################################################################

def CurvaTobogan(N):
    
    P0 = np.array([[-1.3, -0.4, 3]]).T
    P1 = np.array([[-1.1, -0.299, 2.7]]).T
    P2 = np.array([[-0.341, -0.129, 2.83]]).T
    P3 = np.array([[0.121, -0.313, 2.6]]).T
    P4 = np.array([[0.55, -0.36, 2.7]]).T
    P5 = np.array([[1.12, -0.39, 2.77]]).T
    P6 = np.array([[1.44, -0.51, 2.5]]).T
    P7 = np.array([[1.93, -0.31, 2.44]]).T
    P8 = np.array([[2.33, -0.43, 2.3]]).T
    P9 = np.array([[2.46, -0.22, 2.2]]).T
    
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


def tobogan(N,n):
    curva = CurvaTobogan(N)
    mesh = om.TriMesh()
    r = 0.3
    n = 77
    f = 2 * np.pi / 7
    
    vertices= []

    for i in range(n):
        for j in range(7):
            x = 0
            z = np.cos(j*f) * r
            y = np.sin(j*f) * r
            vertices.append([x,y,z])

    for i in range(len(vertices)):
        #vertices[i][0] += curva[i][0]
        #vertices[i][1] += curva[i][1]
        #vertices[i][2] += curva[i][2]
        mesh.add_vertex([vertices[i][0],vertices[i][1],vertices[i][2]])
    

    def ind(i,j):
        x = (i*7) + j
        return x
    print(len(mesh.points()))
    for i in range(len(curva)-1):
        print(i)
        for j in range(6):

            indice1 = ind(i,j)
            indice2 = ind(i,j+1)
            indice3 = ind(i+1,j)
            indice4 = ind(i+1,j+1)

            vertexs = list(mesh.vertices())

            mesh.add_face(vertexs[indice1], vertexs[indice2], vertexs[indice3])
            mesh.add_face(vertexs[indice3], vertexs[indice4], vertexs[indice1])

    return mesh

def get_vertex_and_indexes(mesh):
    faces = mesh.faces()

    vertices = []

    for i in mesh.points():
        print(i)
        vertices += i.tolist()
        vertices += [random.uniform(0,1),random.uniform(0,1),random.uniform(0,1)]
    
    
    indices = []
    
    for i in faces:
        
        indexes_faces = mesh.fv(i)

        for j in indexes_faces:

            indices += [j.idx()]
    return vertices , indices





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



def dibujoTobogan(pipeline):
    gpuRio = tobogan(pipeline)

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
    pipeline = es.SimpleModelViewProjectionShaderProgram()
    phongPipeline = ls.SimplePhongShaderProgram()
    #Tobogan = createToboganNode(0.5,0.5,0.5,phongPipeline)
    
    skybox = create_skybox(textureShaderProgram)
    floor = create_floor(textureShaderProgram)
    #escena_tobogan = dibujo_de_tobogan(colorShaderProgram)
    #barco_mov = ej6.create_barco(colorShaderProgram)

    #coor_curva = CurvaTobogan(686)
    
    #mov_boat = sg.findNode(barco_mov, "barco")
    
    #movimiento_barco = ej6.Movimientodelbarco(0.1)
    #movimiento_barco.set_curva(coor_curva)
    #movimiento_barco.set_model(mov_boat)
    #movimiento_barco.set_controller(controller)

    mesh = tobogan(81, 74)
    mesh_vertex , mesh_indx = get_vertex_and_indexes(mesh)
    gpumesh = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpumesh)
    gpumesh.fillBuffers(mesh_vertex,mesh_indx,GL_STATIC_DRAW)
###########################################################################################
    glUseProgram(pipeline.shaderProgram)
    # View and projection
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    print('ok')
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
        
        #at_x = controller.eye[0] + np.cos(controller.theta)
        #at_y = controller.eye[1] + np.sin(controller.theta)
        #controller.at = np.array([at_x, at_y, controller.at[2]])
        #view = tr.lookAt(1, controller.at, controller.up)
        view = tr.lookAt(
            [1,1,1],
            np.array([1.12, -0.39, 2.77]),
            np.array([0,0,1])
        )
        
###########################################################################
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.uniformScale(1))
        pipeline.drawCall(gpumesh)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    glfw.terminate()
