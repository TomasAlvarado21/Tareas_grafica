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
import random


############################################################################


CIRCLE_DISCRETIZATION = 20

def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

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
    
def f_roce(t, z):
    # Nos entrega el vector f con todas las funciones del sistema
    f = np.array([z[1], - velocidad_ini])
    return f

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

    return gpuPata

def createColorNormalSphere(N, r, g, b):

    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    r = 0.5
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

    

def getIJ(index, N, M):
    # we are inside the grid.
    assert(index < N * M)
    col = 0
    while index >= N:
        col += 1
        index -= N
    row = index % N
    return row, col


        
class Circle:
    def __init__(self, pipeline, position, velocity, r, g, b):
        shape = bs.createColorCircle(CIRCLE_DISCRETIZATION, r, g, b)
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 2 * 0.05
        bs.scaleVertices(shape, 6, (scaleFactor, scaleFactor, 1.0))
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
        self.position = position
        self.radius = 0.05
        self.velocity = velocity

    def action(self, gravityAceleration, deltaTime):
        # Euler integration
        self.velocity += deltaTime * gravityAceleration
        self.position += self.velocity * deltaTime

    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE,
            tr.translate(self.position[0], self.position[1], 0.0)
        )
        self.pipeline.drawCall(self.gpuShape)

def createSpheres():
    N = 1
    M = 1
    D = 1
    mu, sigma = D * 0.5, D * 0.1 # mean and standard deviation
    radios = np.random.normal(mu, sigma, N*M)
    angleSpeeds = np.random.normal(mu, sigma * 2, N*M)
    spheres = []

    # Hacemos un plano y ubicamos cada esfera a una distancia D de la próxima    
    x = np.arange(-D * N / 2, D * N / 2, D)
    y = np.arange(-D * M / 2, D * M / 2, D)

    for index in range(N*M):
        i, j = getIJ(index, N, M)
        posX, posY = x[i], y[j]
        spheres.append(Circle(posX, posY, radios[index], angleSpeeds[index]))
    
    return spheres

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


def collide(circle1, circle2):
    """
    If there are a collision between the circles, it modifies the velocity of
    both circles in a way that preserves energy and momentum.
    """
    
    assert isinstance(circle1, Sphere)
    assert isinstance(circle2, Sphere)

    normal = circle2.position - circle1.position
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


def areColliding(circle1, circle2):
    assert isinstance(circle1, Circle)
    assert isinstance(circle2, Circle)

    difference = circle2.position - circle1.position
    distance = np.linalg.norm(difference)
    collisionDistance = circle2.radius + circle1.radius
    return distance < collisionDistance


def collideWithBorder(circle):

    # Right
    if circle.position[0] + circle.radius > 1.0:
        circle.velocity[0] = -abs(circle.velocity[0])

    # Left
    if circle.position[0] < -1.0 + circle.radius:
        circle.velocity[0] = abs(circle.velocity[0])

    # Top
    if circle.position[1] > 1.0 - circle.radius:
        circle.velocity[1] = -abs(circle.velocity[1])

    # Bottom
    if circle.position[1] < -1.0 + circle.radius:
        circle.velocity[1] = abs(circle.velocity[1])

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
    pipeline = colorShaderProgram
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
    
    pata1 = create_pata(colorShaderProgram)
    pata1.transform = tr.translate(0.5,0,0.5)
    pata1.transform = tr.uniformScale(1.1)

    pata2 = create_pata(colorShaderProgram)
    pata2.transform = tr.translate(0.5,0.5,0.5)
    
    circles = []
    for i in range(5):
        position = np.linspace(-0.5,0.5,5)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, position, velocity, r, g, b)
        circles += [circle]

    for i in range(4):
        position = np.linspace(-0.3,0.3,4)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, position, velocity, r, g, b)
        circles += [circle]
    
    for i in range(3):
        position = np.linspace(-0.2,0.2,4)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, position, velocity, r, g, b)
        circles += [circle]

    for i in range(2):
        position = np.linspace(-0.1,0.1,4)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, position, velocity, r, g, b)
        circles += [circle]

    for i in range(1):
        position = np.linspace(0.0,0.0,4)
        velocity = np.array([0,0])
        r, g, b = random.uniform(0,1), random.uniform(0,1), random.uniform(0,1)
        circle = Circle(pipeline, position, velocity, r, g, b)
        circles += [circle]
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
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.translate(0.5, 0.5, 0.5),
            tr.uniformScale(1)]))
        pipeline.drawCall(pata2)

        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, projection)
        pipeline.drawCall(pata1)


        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        

        sg.drawSceneGraphNode(skybox, textureShaderProgram, "model")
        sg.drawSceneGraphNode(floor, textureShaderProgram, "model")
        sg.drawSceneGraphNode(mesa, textureShaderProgram, "model")       

        for circle in circles:
            circle.draw()
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)
    for circle in circles:
        circle.gpuShape.clear()
    glfw.terminate()