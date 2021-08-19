import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path

from numpy.lib.function_base import delete
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.scene_graph as sg
import grafica.performance_monitor as pm
from grafica.assets_path import getAssetPath
import random


############################################################################
thisFilePath = os.path.abspath(__file__)
thisFolderPath = os.path.dirname(thisFilePath)
PoolDirectory = os.path.join(thisFolderPath, "assets")

CIRCLE_DISCRETIZATION = 40
RADIUS = 0.05
VELOCIDAD_GOLPE= 8
COEF_RESTITUCION = 0.95

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape
def createTextureGPUShape(shape, pipeline, path):
    # Funcion Conveniente para facilitar la inicializacion de un GPUShape con texturas
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        path, GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)
    return gpuShape

def create_skybox(pipeline):
    shapeSky = bs.createTextureCube('paisaje.jfif')
    gpuSky = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuSky)
    gpuSky.fillBuffers(shapeSky.vertices, shapeSky.indices, GL_STATIC_DRAW)
    gpuSky.texture = es.textureSimpleSetup(
        getAssetPath("bar1.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    
    skybox = sg.SceneGraphNode("skybox")
    skybox.transform = tr.matmul([tr.translate(0, 0, 1), tr.uniformScale(6)])
    skybox.childs += [gpuSky]

    return skybox
    


def create_floor(pipeline):
    shapeFloor = bs.createTextureQuadNormal(1, 1)
    gpuFloor = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuFloor)
    gpuFloor.texture = es.textureSimpleSetup(getAssetPath('pano_mesa.jpg'), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    gpuFloor.fillBuffers(shapeFloor.vertices, shapeFloor.indices, GL_STATIC_DRAW)

    floor = sg.SceneGraphNode("floor")
    floor.transform = tr.matmul([tr.translate(0, 0, 0),tr.scale(2, 4, 1)])
    floor.childs += [gpuFloor]

    return floor


def createMesaNodeNormals(texborde,texmadera,texhoyo,pipeline,radio_bola):

    mesaNode = sg.SceneGraphNode('bordeMesa')

    gpumarco = createGPUShape(pipeline, bs.createTextureNormalsCube(texmadera))
    gpumarco.texture = texmadera
    gpuborde = createGPUShape(pipeline, bs.createTextureNormalsCube(texborde))
    gpuborde.texture = texborde

    bordetopCNode = sg.SceneGraphNode('bordeTopCompleto')
    bordetopNode = sg.SceneGraphNode('bordeTop')
    marco_tNode = sg.SceneGraphNode('marcotop')
    marco_tNode.childs.append(gpumarco)
    
    bordetopNode.childs.append(gpuborde)
    bordetopNode.transform = tr.matmul([tr.translate(0,2+radio_bola,0), tr.scale( (1-2*radio_bola)/0.5, radio_bola/0.5, radio_bola/0.5 )])
    marco_tNode.transform = tr.matmul([tr.translate(0,2+3*radio_bola,0), tr.scale( (1+4*radio_bola)/0.5, radio_bola/0.5, radio_bola/0.5 )])
    bordetopCNode.childs = [bordetopNode, marco_tNode]

    bordebottomCNode = sg.SceneGraphNode('bordebottomCompleto')
    bordebottomNode = sg.SceneGraphNode('bordebottom')
    marco_bNode = sg.SceneGraphNode('marcotop')
    marco_bNode.childs.append(gpumarco)
    
    bordebottomNode.childs.append(gpuborde)
    bordebottomNode.transform = tr.matmul([tr.translate(0,-2-radio_bola,0), tr.scale( (1-2*radio_bola)/0.5, radio_bola/0.5, radio_bola/0.5 )])
    marco_bNode.transform = tr.matmul([tr.translate(0,-2-3*radio_bola,0), tr.scale( (1+4*radio_bola)/0.5, radio_bola/0.5, radio_bola/0.5 )])
    bordebottomCNode.childs = [bordebottomNode, marco_bNode]

    borderightNode = sg.SceneGraphNode('borderight')
    NodoBorde = sg.SceneGraphNode('borde_r1')
    Nodo2Borde = sg.SceneGraphNode('borde_r2')
    marco_rNode = sg.SceneGraphNode('marcoRight')
    marco_rNode.childs.append(gpumarco)
    
    NodoBorde.childs.append(gpuborde)
    Nodo2Borde.childs.append(gpuborde)
    NodoBorde.transform = tr.matmul([tr.translate(1+radio_bola,1,0), tr.scale( radio_bola/0.5,(1-2*radio_bola)/0.5, radio_bola/0.5 )])
    Nodo2Borde.transform = tr.matmul([tr.translate(1+radio_bola,-1,0), tr.scale( radio_bola/0.5,(1-2*radio_bola)/0.5, radio_bola/0.5 )])
    marco_rNode.transform = tr.matmul([tr.translate(1+3*radio_bola,0,0), tr.scale( radio_bola/0.5,(2+4*radio_bola)/0.5, radio_bola/0.5 )])
    borderightNode.childs = [NodoBorde, Nodo2Borde, marco_rNode]
    
    bordeleftNode = sg.SceneGraphNode('bordeleft')
    bordelNode1 = sg.SceneGraphNode('borde_l1')
    bordelNode2 = sg.SceneGraphNode('borde_l2')
    marco_lNode = sg.SceneGraphNode('marcoLeft')
    marco_lNode.childs.append(gpumarco)
    
    bordelNode1.childs.append(gpuborde)
    bordelNode2.childs.append(gpuborde)
    bordelNode1.transform = tr.matmul([tr.translate(-1-radio_bola,1,0), tr.scale( radio_bola/0.5,(1-2*radio_bola)/0.5, radio_bola/0.5 )])
    bordelNode2.transform = tr.matmul([tr.translate(-1-radio_bola,-1,0), tr.scale( radio_bola/0.5,(1-2*radio_bola)/0.5, radio_bola/0.5 )])
    marco_lNode.transform = tr.matmul([tr.translate(-1-3*radio_bola,0,0), tr.scale( radio_bola/0.5,(2+4*radio_bola)/0.5, radio_bola/0.5 )])
    bordeleftNode.childs = [bordelNode1, bordelNode2, marco_lNode]

    HoyosNode = sg.SceneGraphNode('Hoyos')
    gpuhoyo = createGPUShape(pipeline, bs.createTextureQuadNormal(1,1))
    gpuhoyo.texture = texhoyo
    gpuh= createGPUShape(pipeline, bs.createTextureQuadNormal(0.25,0.25))
    gpuh.texture = texborde


    hoyo1 = sg.SceneGraphNode('Hoyo1')
    hoyo1.childs.append(gpuh)
    hoyo1.transform = tr.matmul([tr.translate(1+radio_bola,0,0.0001-radio_bola), tr.uniformScale(2*radio_bola/0.5)])
    hoyo2 = sg.SceneGraphNode('Hoyo2')
    hoyo2.childs.append(gpuh)
    hoyo2.transform = tr.matmul([tr.translate(-1-radio_bola,0,0.0001-radio_bola), tr.uniformScale(2*radio_bola/0.5)])
    hoyo3 = sg.SceneGraphNode('Hoyo3')
    hoyo3.childs.append(gpuh)
    hoyo3.transform = tr.matmul([tr.translate(1,2,0.0001-radio_bola), tr.uniformScale(2*radio_bola/0.5)])
    hoyo4 = sg.SceneGraphNode('Hoyo4')
    hoyo4.childs.append(gpuh)
    hoyo4.transform = tr.matmul([tr.translate(-1,2,0.0001-radio_bola), tr.uniformScale(2*radio_bola/0.5)])
    hoyo5 = sg.SceneGraphNode('Hoyo5')
    hoyo5.childs.append(gpuh)
    hoyo5.transform = tr.matmul([tr.translate(1,-2,0.0001-radio_bola), tr.uniformScale(2*radio_bola/0.5)])
    hoyo6 = sg.SceneGraphNode('Hoyo6')
    hoyo6.childs.append(gpuh)
    hoyo6.transform = tr.matmul([tr.translate(-1,-2,0.0001-radio_bola), tr.uniformScale(2*radio_bola/0.5)])
    HoyosNode.childs = [hoyo1,hoyo2,hoyo3,hoyo4,hoyo5,hoyo6]

    patasNode = sg.SceneGraphNode('PatasMesa')
    p1node = sg.SceneGraphNode('p1')
    p2node = sg.SceneGraphNode('p2')
    p3node = sg.SceneGraphNode('p3')
    p4node = sg.SceneGraphNode('p4')
    p1node.childs.append(gpumarco)
    p2node.childs.append(gpumarco)
    p3node.childs.append(gpumarco)
    p4node.childs.append(gpumarco)
    p1node.transform = tr.matmul([tr.translate(1+3*radio_bola,2+3*radio_bola,-1), tr.scale(radio_bola/0.5,radio_bola/0.5,2)])
    p2node.transform = tr.matmul([tr.translate(-1-3*radio_bola,2+3*radio_bola,-1), tr.scale(radio_bola/0.5,radio_bola/0.5,2)])
    p3node.transform = tr.matmul([tr.translate(1+3*radio_bola,-2-3*radio_bola,-1), tr.scale(radio_bola/0.5,radio_bola/0.5,2)])
    p4node.transform = tr.matmul([tr.translate(-1-3*radio_bola,-2-3*radio_bola,-1), tr.scale(radio_bola/0.5,radio_bola/0.5,2)])
    patasNode.childs = [p1node,p2node,p3node,p4node]

    mesaNode.childs = [bordebottomCNode,bordeleftNode,bordetopCNode,borderightNode,HoyosNode,patasNode] 
    return mesaNode



def createColorNormalSphere(N, r, g, b):

    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.05
    c = 0

    for i in range(N - 1):
        theta = i * dTheta
        theta1 = (i + 1) * dTheta
        for j in range(N):
            phi = j*dPhi
            phi1 = (j+1)*dPhi
            v0 = [r*np.sin(theta)*np.cos(phi), r*np.sin(theta)*np.sin(phi), r*np.cos(theta)]
            v1 = [r*np.sin(theta1)*np.cos(phi), r*np.sin(theta1)*np.sin(phi), r*np.cos(theta1)]
            v2 = [r*np.sin(theta1)*np.cos(phi1), r*np.sin(theta1)*np.sin(phi1), r*np.cos(theta1)]
            v3 = [r*np.sin(theta)*np.cos(phi1), r*np.sin(theta)*np.sin(phi1), r*np.cos(theta)]
            n0 = [np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)]
            n1 = [np.sin(theta1)*np.cos(phi), np.sin(theta1)*np.sin(phi), np.cos(theta1)]
            n2 = [np.sin(theta1)*np.cos(phi1), np.sin(theta1)*np.sin(phi1), np.cos(theta1)]
            n3 = [np.sin(theta)*np.cos(phi1), np.sin(theta)*np.sin(phi1), np.cos(theta)]


            # Creamos los quad superiores
            if i == 0:
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)
lista_hoyos = [[1.05, 0], [-1.05, 0], [1, 2], [-1, 2], [1, -2], [-1, -2]]
def delete_bola(lista_hoyos, circle, circles):
    for i in lista_hoyos:
        difference = np.array(circle.position) - i
        distance = np.linalg.norm(difference)
        collisionDistance = circle.radius + 0.05
        if distance < collisionDistance:
            circle.delete(circles)

def getIJ(index, N, M):
    # we are inside the grid.
    assert(index < N * M)
    col = 0
    while index >= N:
        col += 1
        index -= N
    row = index % N
    return row, col

class Player:
    def __init__(self, pipeline, shadow_pip, position, controller):

        self.pipeline = pipeline
        self.nodo = sg.SceneGraphNode("sphere")
        self.gpuShape = createGPUShape(pipeline, createColorNormalSphere(CIRCLE_DISCRETIZATION, 0,0,0))#createGPUShape(pipeline, createColorNormalSphere(40, 0.9,0.9,0.9)) # Shape de la esfera
        self.sombra = createGPUShape(shadow_pip,bs.createColorCircle(20,0.0,0.1,0.1))
        self.nodo.childs.append(self.gpuShape)
        self.position = position
        self.radius = RADIUS
        self.direccion = [0.0 , 0.0]
       
        self.velocity = np.array([0.0,0.0],dtype=np.float64)
        self.controller = controller

    def action(self, acceleration, deltaTime, direccion_golpe):
        if self.controller.is_enter_pressed and (self.velocity[0] == 0.0 and self.velocity[1] == 0.0):
            potencia = 1 #self.controller.potencia * 0.1 
            self.velocity = (VELOCIDAD_GOLPE*potencia)*direccion_golpe
            #self.controller.potencia = 0
            print('disparrau', direccion_golpe)
        
        if self.controller.is_enter_pressed:
            print('oki')
        if  np.abs(self.velocity[0])>0.001 or np.abs(self.velocity[1])>0.001:
            # Euler
            direccion = np.array(self.velocity/np.linalg.norm(self.velocity),dtype=np.float64)
            self.velocity[0] += deltaTime * acceleration * (-direccion[0])
            self.velocity[1] += deltaTime * acceleration * (-direccion[1])
            self.position += self.velocity * deltaTime
            

        if 0<np.abs(self.velocity[0])<=0.001 and 0<np.abs(self.velocity[1])<=0.001:
            self.velocity = np.array([0.0,0.0],dtype=np.float64)

    
    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "model"), 1, GL_TRUE,
            tr.matmul([tr.translate(self.position[0], self.position[1], 0.05)])
        )
        self.pipeline.drawCall(self.gpuShape)
    def draw_sombra(self, pip):
        glUniformMatrix4fv(glGetUniformLocation(pip.shaderProgram, "model"), 1, GL_TRUE,
            tr.matmul([tr.translate(self.position[0], self.position[1], 0.0001), tr.uniformScale(0.1)])
        )
        pip.drawCall(self.sombra)

class Circle:
    def __init__(self, pipeline, shadow_pip, position, velocity, r, g, b):
        sphere = createGPUShape(pipeline, createColorNormalSphere(CIRCLE_DISCRETIZATION, r,g,b))
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 0.05
        self.sombra = createGPUShape(shadow_pip,bs.createColorCircle(CIRCLE_DISCRETIZATION,0.0,0.1,0.1))
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(pipeline, createColorNormalSphere(CIRCLE_DISCRETIZATION, r,g,b))#createGPUShape(self.pipeline, shape)
        self.position = position
        self.radius = 0.05
        self.velocity = velocity
        

    def action(self, aceleracion, deltaTime):
        # Euler integration
        if np.abs(self.velocity[0])>0.001 or np.abs(self.velocity[1])>0.001:
            direccion = np.array(self.velocity/np.linalg.norm(self.velocity),dtype=np.float64)
            self.velocity[0] += deltaTime * aceleracion * (-direccion[0])
            self.velocity[1] += deltaTime * aceleracion * (-direccion[1])
            self.position += self.velocity * deltaTime
            
             

        if np.abs(self.velocity[0])<=0.001 and np.abs(self.velocity[1])<=0.001:
            self.velocity = np.array([0.0,0.0],dtype=np.float64)  
            
    def golpe(self, direccion, impulso):
        self.velocity = np.array([direccion[0]*impulso, direccion[1]*impulso])

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "model"), 1, GL_TRUE,
            tr.matmul([tr.translate(self.position[0], self.position[1], 0.05)])
        )
        self.pipeline.drawCall(self.gpuShape)
        
    def draw_sombra(self, pip):
        glUniformMatrix4fv(glGetUniformLocation(pip.shaderProgram, "model"), 1, GL_TRUE,
            tr.matmul([tr.translate(self.position[0], self.position[1], 0.0001), tr.uniformScale(0.1)])
        )
        pip.drawCall(self.sombra)

    def delete(self,lista_circles):
        lista_circles.remove(self)



def rotate2D(vector, theta):
    """
    Direct application of a 2D rotation
    """
    sin_theta = np.sin(theta)
    cos_theta = np.cos(theta)

    return np.array([
        cos_theta * vector[0] - sin_theta * vector[1],
        sin_theta * vector[0] + cos_theta * vector[1]
    ], dtype = np.float32)


def collide(circle1, circle2,C):
    """
    If there are a collision between the circles, it modifies the velocity of
    both circles in a way that preserves energy and momentum.
    """
    

    normal = np.array(circle2.position) - np.array(circle1.position)
    normal /= np.linalg.norm(normal)

    circle1MovingToNormal = np.dot(circle2.velocity, normal) > 0.0
    circle2MovingToNormal = np.dot(circle1.velocity, normal) < 0.0

    if not (circle1MovingToNormal and circle2MovingToNormal):

        # obtaining the tangent direction
        tangent = rotate2D(normal, np.pi/2.0)

        # Projecting the velocity vector over the normal and tangent directions
        # for both circles, 1 and 2.
        v1n = np.dot(circle1.velocity, normal) * normal
        v1t = np.dot(circle1.velocity, tangent) * tangent

        v2n = np.dot(circle2.velocity, normal) * normal
        v2t = np.dot(circle2.velocity, tangent) * tangent

        # swaping the normal components...
        # this means that we applying energy and momentum conservation
        circle1.velocity = v2n + v1t
        circle2.velocity = v1n + v2t

def posicion_camara(player_position, parametrizacion):
    f = 2 * np.pi / parametrizacion
    r = 1.2
    camara = []
    for i in range(parametrizacion):
        camara.append([np.sin(f*i)*r + player_position[0], np.cos(f*i)*r + player_position[1], 0.6])
    
    return camara

def areColliding(circle1, circle2):

    difference = np.array(circle2.position) - np.array(circle1.position)
    distance = np.linalg.norm(difference)
    collisionDistance = circle2.radius + circle1.radius
    return distance < collisionDistance


def collideWithBorder(circle):

    # Right
    if circle.position[0] + circle.radius > 1.0 and (2.0 - 1.75*circle.radius)> abs(circle.position[1]) > 1.75*circle.radius:
        circle.velocity[0] = -abs(circle.velocity[0])

    # Left
    if circle.position[0] < -1.0 + circle.radius and (2.0 - 1.75*circle.radius)> abs(circle.position[1]) > 1.75*circle.radius:
        circle.velocity[0] = abs(circle.velocity[0])

    # Top
    if circle.position[1] > 2.0 - circle.radius and (1.0 - 1.75*circle.radius)> abs(circle.position[0]):
        circle.velocity[1] = -abs(circle.velocity[1])
        
    # Bottom
    if circle.position[1] < -2.0 + circle.radius and (1.0 - 1.75*circle.radius)> abs(circle.position[0]):
        circle.velocity[1] = abs(circle.velocity[1])

############################################################################

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
###########################################################
        self.theta = np.pi
        self.pos_curva = 125 
        self.is_enter_pressed = False
###########################################################


# global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS and action != glfw.REPEAT and action!= glfw.RELEASE:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ENTER:
        if action ==glfw.PRESS:
            controller.is_enter_pressed = True
        elif action == glfw.RELEASE:
            controller.is_enter_pressed = False

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    
###########################################################

    elif key == glfw.KEY_D:
        controller.pos_curva -= 0.75
    elif key == glfw.KEY_A:
        controller.pos_curva += 0.75

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
    texlightShaderProgram = es.SimpleTexturePhongShaderProgram()
    lightShaderProgram = es.SimplePhongShaderProgram()
    pipeline = lightShaderProgram
    texpipeline = texlightShaderProgram
    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

###########################################################################################
    # Creating shapes on GPU memory

    skybox = create_skybox(texpipeline)
    floor = create_floor(texpipeline)
    texture1 = es.textureSimpleSetup(
        getAssetPath("Piso.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    #text_mesa = es.textureSimpleSetup(
        #getAssetPath("pano_mesa.jpg"), GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)
    #text_mesa = create_mesa_pool(pipeline)
    #mesa = sg.findNode(text_mesa, "Escena")
    player = Player(pipeline, colorShaderProgram,np.array([0.0,0.0]), controller)
    bordes_mesa = createMesaNodeNormals(texture1,texture1,texture1,texpipeline,0.05)
    
    circles = []
    for i in range(5):
        position = np.linspace(-0.25,0.25,5)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, colorShaderProgram, [position[i],1.5], velocity, r, g, b)
        circles += [circle]

    for i in range(4):
        position = np.linspace(-0.2,0.2,4)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, colorShaderProgram, [position[i],1.4], velocity, r, g, b)
        circles += [circle]
    
    for i in range(3):
        position = np.linspace(-0.125,0.125,3)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, colorShaderProgram, [position[i],1.3], velocity, r, g, b)
        circles += [circle]

    for i in range(2):
        position = np.linspace(-0.075,0.075,2)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, colorShaderProgram, [position[i],1.2], velocity, r, g, b)
        circles += [circle]

    for i in range(1):
        position = np.linspace(0.0,0.0,1)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, colorShaderProgram, [0,1.1], velocity, r, g, b)
        circles += [circle]
###########################################################################################

    # View and projection
    #projection = tr.perspective(60, float(width)/float(height), 0.1, 100)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        perfMonitor.update(glfw.get_time())
        dtime = perfMonitor.getDeltaTime()
        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        

###########################################################################

        parametrizacion = 250 
        camara_pos = posicion_camara(player.position, parametrizacion)
        rotacion_camara = int(controller.pos_curva)%parametrizacion
        velocidad_total = 0
        for i in circles:
            velocidad_total += abs(i.velocity[0]) + abs(i.velocity[1])
            collideWithBorder(i)
            i.action(1,dtime)
            delete_bola(lista_hoyos, i, circles)
        velocidad_total += abs(player.velocity[0]) + abs(player.velocity[1])
        
        collideWithBorder(player)

        for i in range(len(circles)):
                for j in range(i+1, len(circles)):
                    if areColliding(circles[i], circles[j]):
                        collide(circles[i], circles[j], COEF_RESTITUCION)
                if areColliding(circles[i], player):
                    collide(circles[i], player, COEF_RESTITUCION)
        
        if velocidad_total == 0:
            view = tr.lookAt(
                np.array(camara_pos[rotacion_camara]),
                np.array([player.position[0],player.position[1],0]),
                np.array([0,0,1])
            )
            viewPosition = camara_pos[rotacion_camara]
        else:
            view = tr.lookAt(
                np.array([1.8,0,1.5]),
                np.array([0,0,0]),
                np.array([0,0,1])
            ) 
            viewPosition = np.array([1.8,0,1.5])

        projection = tr.perspective(110, float(width)/float(height), 0.015, 7.5)


        #calculamos el vector que da la direccion del golpe segun la poscion en que esta eye

        direccion_golpe = np.array(player.position)-np.array([camara_pos[rotacion_camara][0],camara_pos[rotacion_camara][1]])

        direccion_golpe /= np.linalg.norm(direccion_golpe)
        player.action(1,dtime,direccion_golpe)
###########################################################################
       
        
        
        # Drawing dice (with texture, another shader program)
        #glUseProgram(textureShaderProgram.shaderProgram)
        #glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        #glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        

        #sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")
        #sg.drawSceneGraphNode(floor, textureShaderProgram, "model")
        #sg.drawSceneGraphNode(bordes_mesa, textureShaderProgram, "model")       
        
        #glUseProgram(pipeline.shaderProgram)
        #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        #glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        #for circle in circles:
        #    circle.draw()
        #player.draw()
        
        light_position = np.array([0,0,1.5])
        (r,g,b) = (0.7,0.7,0.7)
        glUseProgram(texpipeline.shaderProgram)
        # Entregar a los shaders los coeficientes de iluminacion ambiente, difuso y especular
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "La"), r, g, b)
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "Ld"), r, g, b)
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "Ls"), r, g, b)

        # Entregar a los shaders los coeficientes de reflexion de los objetos ambiente, difuso y especular
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "Ka"), 0.3, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "Ks"), 0.5, 0.5, 0.5)

        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "lightPosition"), light_position[0], light_position[1], light_position[2])
        glUniform3f(glGetUniformLocation(texpipeline.shaderProgram, "viewPosition"), viewPosition[0], viewPosition[1], viewPosition[2])
        glUniform1ui(glGetUniformLocation(texpipeline.shaderProgram, "shininess"), 10)
        
        # Entregar valores a los shaders los coeficientes de atenuacion
        glUniform1f(glGetUniformLocation(texpipeline.shaderProgram, "constantAttenuation"), 0.2)
        glUniform1f(glGetUniformLocation(texpipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(texpipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(texpipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(texpipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        #sg.drawSceneGraphNode(skybox, texpipeline, "model")
        sg.drawSceneGraphNode(floor, texpipeline, "model")
        sg.drawSceneGraphNode(bordes_mesa, texpipeline, "model") 


        glUseProgram(pipeline.shaderProgram)
        # Entregar a los shaders los coeficientes de iluminacion ambiente, difuso y especular
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), r, g, b)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), r, g, b)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), r, g, b)

        # Entregar a los shaders los coeficientes de reflexion de los objetos ambiente, difuso y especular
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.1, 0.1, 0.1)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 0.9, 0.9, 0.9)

        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), light_position[0], light_position[1], light_position[2])
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPosition[0], viewPosition[1], viewPosition[2])
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 20)
        
        # Entregar valores a los shaders los coeficientes de atenuacion
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.05)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

        for circle in circles:
            circle.draw()
        player.draw()


        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        for circle in circles:
            circle.draw_sombra(colorShaderProgram)
        player.draw_sombra(colorShaderProgram)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)
    for circle in circles:
        circle.gpuShape.clear()
    glfw.terminate()