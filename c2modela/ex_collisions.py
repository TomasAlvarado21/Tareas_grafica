# coding=utf-8
"""Circles, collisions and gravity"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import random
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm


__author__ = "Daniel Calderon"
__license__ = "MIT"

# Example parameters

NUMBER_OF_CIRCLES = 10
CIRCLE_DISCRETIZATION = 20
RADIUS = 0.08
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

# Convenience function to ease initialization
def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

class Circle:
    def __init__(self, pipeline, position, r, g, b):
        shape = bs.createColorCircle(CIRCLE_DISCRETIZATION, r, g, b)
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 2 * RADIUS
        bs.scaleVertices(shape, 6, (scaleFactor, scaleFactor, 1.0))
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
        self.position = position
        self.radius = RADIUS
        
    
    def draw(self):
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE,
            tr.translate(self.position[0], self.position[1], 0.0)
        )
        self.pipeline.drawCall(self.gpuShape)

class player:
    def __init__(self, pipeline, controller, velocity, r, g, b):
        shape = bs.createColorQuad(r, g, b)
        # addapting the size of the circle's vertices to have a circle
        # with the desired radius
        scaleFactor = 0.25
        bs.scaleVertices(shape, 6, (scaleFactor, scaleFactor, 1.0))
        self.pos = [0,-0.65] # Posicion en el escenario
        self.vel = [1,0] # Velocidad de desplazamiento
        self.model = None # Referencia al grafo de escena asociado
        self.controller = controller # Referencia del controlador, para acceder a sus variables
        self.size = 1 # Escala a aplicar al nodo 
        self.radio = 0.12 # distancia para realiozar los calculos de colision
        self.pipeline = pipeline
        self.gpuShape = createGPUShape(self.pipeline, shape)
    
    def colision(self, circles):
        
        for circle in circles:
            x, y = circle.position
            if abs(x-self.pos[0])<self.radio + circle.radius and abs(y-self.pos[1])<self.radio + circle.radius:
                circles.remove(circle)
                
            

    def action(self, gravityAceleration, deltaTime):
        # Euler integration
        if self.pos[1] < -0.65:
            self.vel[1] = 0
            self.pos[1] = -0.65
        elif self.pos[1] == -0.65 and controller.is_space_pressed:
            print(self.pos)
            self.vel[1] += 0.9
            self.vel[1] += deltaTime * gravityAceleration[1]
            self.pos[1] += self.vel[1] * deltaTime
        elif self.pos[1] > -0.65:
            self.vel[1] += deltaTime * gravityAceleration[1]
            self.pos[1] += self.vel[1] * deltaTime



    def update(self, deltatime):
        # Se actualiza la posicion del auto

        # Si detecta la tecla [D] presionada se mueve hacia la derecha
        if self.controller.is_d_pressed:
            self.pos[0] += self.vel[0] * deltatime
        # Si detecta la tecla [A] presionada se mueve hacia la izquierda
        if self.controller.is_a_pressed:
            self.pos[0] -= self.vel[0] * deltatime
        
        # Se le aplica la transformacion de traslado segun la posicion actual
        
        

    def draw(self):
        
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE,
            tr.translate(self.pos[0], self.pos[1], 0.0)
        )
        self.pipeline.drawCall(self.gpuShape)
        

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


def collide(circle1, player):
    """
    If there are a collision between the circles, it modifies the velocity of
    both circles in a way that preserves energy and momentum.
    """
    
    assert isinstance(circle1, Circle)
    #assert isinstance(circle2, Circle)

    normal = player.pos - circle1.position
    normal /= np.linalg.norm(normal)

    circle1MovingToNormal = np.dot(player.vel, normal) > 0.0
    playerMovingToNormal = np.dot(0, normal) < 0.0

    if not (circle1MovingToNormal and playerMovingToNormal):

        # obtaining the tangent direction
        tangent = rotate2D(normal, np.pi/2.0)

        # Projecting the velocity vector over the normal and tangent directions
        # for both circles, 1 and 2.
        v1n = np.dot(0, normal) * normal
        v1t = np.dot(0, tangent) * tangent

        v2n = np.dot(player.vel, normal) * normal
        v2t = np.dot(player.vel, tangent) * tangent

        # swaping the normal components...
        # this means that we applying energy and momentum conservation
        circle1.velocity = v2n + v1t
        player.vel = v1n + v2t


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


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.circleCollisions = False
        self.useGravity = False
        self.is_w_pressed = False
        self.is_s_pressed = False
        self.is_a_pressed = False
        self.is_d_pressed = False
        self.is_space_pressed = False

# we will use the global controller as communication with the callback function
controller = Controller()


# This function will be executed whenever a key is pressed or released
def on_key(window, key, scancode, action, mods):

    
    global controller

    if key == glfw.KEY_SPACE:
        if action ==glfw.PRESS:
            controller.is_space_pressed = True
        elif action == glfw.RELEASE:
            controller.is_space_pressed = False
        #player.action(gravityAcceleration,deltaTime)

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_1:
        controller.circleCollisions = not controller.circleCollisions
        print("Collisions among circles?", controller.circleCollisions)

    elif key == glfw.KEY_2:
        controller.useGravity = not controller.useGravity
        print("Gravity?", controller.useGravity)
    elif key == glfw.KEY_A:
        if action ==glfw.PRESS:
            controller.is_a_pressed = True
        elif action == glfw.RELEASE:
            controller.is_a_pressed = False

    # Caso de detectar la tecla [D], actualiza estado de variable
    elif key == glfw.KEY_D:
        if action ==glfw.PRESS:
            controller.is_d_pressed = True
        elif action == glfw.RELEASE:
            controller.is_d_pressed = False
    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit(1)

    # Creating a glfw window
    title = "Circles, collisions and gravity"
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Creating shapes on GPU memory
    circles = []
    for i in range(NUMBER_OF_CIRCLES):
        position = np.array([
            random.uniform(-1.0 + RADIUS, 1.0 - RADIUS),
            random.uniform(-1.0 + RADIUS, 1.0 - RADIUS)
        ])
        velocity = np.array([
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0)
        ])
        r, g, b = 0.25, 0.23, 0
        circle = Circle(pipeline, position,  r, g, b)
        circles += [circle]
    quad = player(pipeline, controller,1, 0, 0,1)
    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    gravityAcceleration = np.array([0.0, -1.0], dtype=np.float32)
    noGravityAcceleration = np.array([0.0, 0.0], dtype=np.float32)
    
   


    # Application loop
    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Using the time as the theta parameter
        theta = glfw.get_time()
        deltaTime = perfMonitor.getDeltaTime()

        if controller.useGravity:
            acceleration = gravityAcceleration
        else:
            acceleration = noGravityAcceleration
        quad.update(deltaTime)
        quad.action(gravityAcceleration,deltaTime)
        quad.colision(circles)
        #if KEY_SPACE:
        #    if action ==glfw.PRESS:
        #        controller.is_a_pressed = True
        #        quad.action(gravityAcceleration,deltaTime)
        #    elif action == glfw.RELEASE:
        #        controller.is_a_pressed = False
        
        # Physics!
        for circle in circles:
            # moving each circle
            #circle.action(acceleration, deltaTime)

            # checking and processing collisions against the border
            collideWithBorder(circle)
        
        
        # checking and processing collisions among circles
        #if controller.circleCollisions:
        #    for i in range(len(circles)):
        #        for j in range(i+1, len(circles)):
        #            if areColliding(circles[i], circles[j]):
        #                collide(circles[i], circles[j])
        
        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # drawing all the circles
        for circle in circles:
            circle.draw()

        
        quad.draw()
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    for circle in circles:
        circle.gpuShape.clear()
    quad.gpuShape.clear()
    glfw.terminate()
