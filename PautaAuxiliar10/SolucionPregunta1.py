# coding=utf-8
"""Simulates a block sliding down a plane that is inclined"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import ode_resolver as edo

__author__ = "Nelson Marambio"
__license__ = "MIT"

# Definicion de variables fisicas
gravedad = 9.8
angulo_plano_inclinado = np.pi/9
coef_roce = 0.01
delta_roce = 0.1
delta_gravedad = 10

# Variables para la aproximación

posicion_ini = 1.0
velocidad_ini = 0
h = 0.0001

# Formateo para usar las funciones
z0 = [posicion_ini, velocidad_ini]
last_z_rk4 = z0
last_z_euler = z0


# Definicion de la función f para aproximar la edo


def on_key(window, key, scancode, action, mods):
    global angulo_plano_inclinado
    global coef_roce
    global gravedad
    global last_z_rk4
    global last_z_euler
    global z0

    if action != glfw.PRESS:
        return

    elif key == glfw.KEY_ENTER:
        last_z_rk4 = z0
        last_z_euler = z0
        print("Reset")

    elif key == glfw.KEY_RIGHT:
        coef_roce += delta_roce
        print("Aumentando roce", coef_roce)

    elif key == glfw.KEY_LEFT:
        coef_roce -= delta_roce
        if coef_roce < 0.0:
            coef_roce = 0.0
        print("Disminuyendo roce", coef_roce)

    elif key == glfw.KEY_UP:
        gravedad += delta_gravedad
        print("Aumentando gravedad", gravedad)

    elif key == glfw.KEY_DOWN:
        gravedad -= delta_gravedad
        print("Disminuyendo gravedad", gravedad)

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    #con estas teclas se modifica en tiempo real el angulo del plano inclinado en base a pi/9
    elif key == glfw.KEY_A:
        angulo_plano_inclinado += np.pi/9
        print('cambio de angulo', angulo_plano_inclinado)
    elif key == glfw.KEY_D:
        angulo_plano_inclinado -= np.pi/9
        print('cambio de angulo', angulo_plano_inclinado)

    else:
        print('Unknown key')

def f_roce(t, z):
    # Nos entrega el vector f con todas las funciones del sistema
    f = np.array([z[1], gravedad*(coef_roce*np.cos(angulo_plano_inclinado)- np.sin(angulo_plano_inclinado))])
    return f
# Creacion de la escena del plano inclinado
def create_scene(angulo_plano_inclinado):
    # Creación del cuadrado que tendra la aprox de RK4
    quad_rk4 = bs.createColorQuad(1, 0, 0)
    gpuQuadRK4 = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuadRK4)
    gpuQuadRK4.fillBuffers(quad_rk4.vertices, quad_rk4.indices, GL_STATIC_DRAW)

    # Creación del cuadrado que tendra la aprox de euler
    quad_euler = bs.createColorQuad(0, 0, 1)
    gpuQuadEuler = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuadEuler)
    gpuQuadEuler.fillBuffers(quad_euler.vertices, quad_euler.indices, GL_STATIC_DRAW)

    plane = bs.createColorQuad(0, 0, 0)
    gpuPlane = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuPlane)
    gpuPlane.fillBuffers(plane.vertices, plane.indices, GL_STATIC_DRAW)

    quad_rk4_scene = sg.SceneGraphNode('cuadrado_rk4')
    quad_rk4_scene.childs = [gpuQuadRK4]
    quad_rk4_scene.transform = [tr.uniformScale(0.3)]

    quad_euler_scene = sg.SceneGraphNode('cuadrado_euler')
    quad_euler_scene.childs = [gpuQuadEuler]
    quad_euler_scene.transform = [tr.uniformScale(0.3)]

    plane_scene = sg.SceneGraphNode('plano')
    plane_scene.childs = [gpuPlane]
    plane_scene.transform = tr.matmul([tr.translate(0, -0.2, 0), tr.scale(10, 0.1, 0)]) 

    scene = sg.SceneGraphNode('escena')
    scene.childs = [quad_euler_scene, quad_rk4_scene, plane_scene]
    scene.transform = tr.rotationZ(angulo_plano_inclinado)

    return scene


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit(1)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Plano inclinado", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Creating shapes on GPU memory
    scene = create_scene(angulo_plano_inclinado)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Creamos el arreglo donde iremos dejando el ultimo paso del calculo de la aproximación, y dejamos las condiciones iniciales
    last_time = 0

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Calculamos un paso de la aproximación
        time = last_time + h
        last_time = time

        next_value_rk4 = edo.RK4_step(f_roce, h, time, last_z_rk4)
        last_z_rk4 = next_value_rk4

        next_value_euler = edo.euler_step(f_roce, h, time, last_z_euler)
        last_z_euler = next_value_euler

        #print("Velocidad actual: " + str(last_z_rk4[1]))

        # Descomentar para ver la diferencia en las posiciones (spoiler: es muy baja)
        #print("Posición actual RK4: " + str(last_z_rk4[0]))
        #print("Posición actual euler: " + str(last_z_euler[0]))
        #print(angulo_plano_inclinado)
        # Modificamos la posición de los cuadrados con las aproximaciones calculadas
        quad_rk4 = sg.findNode(scene, "cuadrado_rk4")
        quad_rk4.transform = tr.matmul([tr.translate(last_z_rk4[0], 0, 0), tr.uniformScale(0.3)])

        quad_euler = sg.findNode(scene, "cuadrado_euler")
        quad_euler.transform = tr.matmul([tr.translate(last_z_euler[0], 0, 0), tr.uniformScale(0.3)])
        scene.transform = tr.rotationZ(angulo_plano_inclinado)
        # Drawing the Scene
        sg.drawSceneGraphNode(scene, pipeline, "transform")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()