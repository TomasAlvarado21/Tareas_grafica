"""P5) [Efectos con Shaders] Realice un par de shaders, donde el primero solo dibuje los píxeles con un tono verde
 y el segundo represente un modo atardecer. Además agregue la funcionalidad de que se puedan alternar entre los shaders
apretando teclas. Con [Q] activa el primer efecto, y con [W] activa el segundo ejemplo"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from gpu_shape import GPUShape, SIZE_IN_BYTES

# A class to store the application control
class Controller:
    fillPolygon = True
    effect1 = False
    effect2 = False


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

    elif key == glfw.KEY_Q:
        controller.effect1 = not controller.effect1

    elif key == glfw.KEY_W:
        controller.effect2 = not controller.effect2

    else:
        print('Unknown key')
    
# A simple class container to store vertices and indices that define a shape
class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

class SimpleShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {
                outColor = vec4(newColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class GreenShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                vec3 newpos = vec3(position[0]-0.3, position[1]+0.2, position[2]);
                gl_Position = vec4(newpos, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {   
                vec3 finalColor = vec3((newColor.r + 0.2) , newColor.g - 0.1, newColor.b - 0.1);
                outColor = vec4(finalColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

class NightShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 130

            in vec3 position;
            in vec3 color;

            out vec3 newColor;
            void main()
            {
                 gl_Position = vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 130
            in vec3 newColor;

            out vec4 outColor;
            void main()
            {   
                vec3 finalColor = vec3((newColor.r * 0.2) , newColor.g * 0.3, newColor.b * 0.3 );
                outColor = vec4(finalColor, 1.0f);
            }
            """

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)

def create_circle(N):

    # First vertex at the center, white color
    vertices = [0, 0, 0, 1.0, 1.0, 1.0]
    indices = []

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * math.cos(theta), 0.5 * math.sin(theta), 0,

            # color generates varying between 0 and 1
                  math.sin(theta),       math.cos(theta), 0]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return Shape(vertices, indices)

def create_sky(y0, y1):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -1.0, y0, 0.0,  0.0, 1.0, 1.0,
         1.0, y0, 0.0,  0.0, 1.0, 1.0,
         1.0, y1, 0.0,  0.8, 1.0, 1.0,
        -1.0, y1, 0.0,  0.8, 1.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                2, 3, 0]

    return Shape(vertices, indices)


def create_island(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions                           colors
         x0, 0.0 + y0, 0.0, 0.0, 0.3, 0.0,
         x0, -1.0, 0.0, 0.0, 0.4, 0.0,
         -x0, 0.0 + y0, 0.0, 0.0, 0.3, 0.0,

         -x0, 0.0 + y0, 0.0, 0.0, 0.3, 0.0,
         -x0, -1.0, 0.0, 0.0, 0.4, 0.0,
         x0, -1.0, 0.0, 0.0, 0.4, 0.0]

    indices = [0, 1, 2,
                3, 4, 5]

    return Shape(vertices, indices)

def create_volcano(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
         x0, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.8, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.4, y0 + height, 0.0,  0.6, 0.31, 0.17,

         x0 + width*0.2, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width, y0, 0.0,  0.3, 0.15, 0.1,
         x0 + width*0.6, y0 + height, 0.0, 0.6, 0.31, 0.17]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                3, 4, 5]

    return Shape(vertices, indices)
def create_lava(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
         
         #lava
         x0 + 0.337, y0 + height - 0.03, 0.0, 0.3, 0.0, 0.0,
         x0 + width*0.5, y0 + height - 0.13, 0.0, 0.8, 0.0, 0.0,
         x0 + width*0.6 - 0.016, y0 + height - 0.03, 0.0, 0.3, 0.0, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return Shape(vertices, indices)

def create_sol(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
            
            #sol
            0.5, 0.5, 0.0, 0.8, 1.0, 0.2,
            0.7, 0.5, 0.0, 0.8, 1.0, 0.2,
            0.5, 0.7, 0.0, 0.8, 1.0, 0.2,
            0.7, 0.7, 0.0, 0.8, 1.0, 0.2]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                1, 2, 3]

    return Shape(vertices, indices)

def create_luna(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
            
            #luna
            0.5, 0.5, 0.0, 1.0, 1.0, 1.0,
            0.7, 0.5, 0.0, 1.0, 1.0, 1.0,
            0.5, 0.7, 0.0, 1.0, 1.0, 1.0,
            0.7, 0.7, 0.0, 1.0, 1.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                1, 2, 3]

    return Shape(vertices, indices)

def create_arbol(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
         #Arbol 1
         #Tronco
         -0.2, -0.5, 0.0, 0.5, 0.3, 0.0,
         -0.2, -0.6, 0.0, 0.5, 0.3, 0.0,
         -0.25, -0.6, 0.0, 0.5, 0.3, 0.0,
         -0.25, -0.5, 0.0, 0.5, 0.3, 0.0,
         #Hojas
         -0.27, -0.5, 0.0, 0.0, 0.8, 0.0,
         -0.27, -0.4, 0.0, 0.0, 0.8, 0.0,
         -0.18, -0.5, 0.0, 0.0, 0.8, 0.0,
         -0.18, -0.4, 0.0, 0.0, 0.8, 0.0,
         #Arbol 2
         #Tronco
         -0.2 + 0.5, -0.5, 0.0, 0.5, 0.3, 0.0,
         -0.2 + 0.5, -0.6, 0.0, 0.5, 0.3, 0.0,
         -0.25 + 0.5, -0.6, 0.0, 0.5, 0.3, 0.0,
         -0.25 + 0.5, -0.5, 0.0, 0.5, 0.3, 0.0,
         #Hojas
         -0.27 + 0.5, -0.5, 0.0, 0.0, 0.8, 0.0,
         -0.27 + 0.5, -0.4, 0.0, 0.0, 0.8, 0.0,
         -0.18 + 0.5, -0.5, 0.0, 0.0, 0.8, 0.0,
         -0.18 + 0.5, -0.4, 0.0, 0.0, 0.8, 0.0,
        
         #Arbol 3
         #Tronco
         -0.2 - 0.2, -0.5 + 0.1, 0.0, 0.5, 0.3, 0.0,
         -0.2 - 0.2, -0.6 + 0.1, 0.0, 0.5, 0.3, 0.0,
         -0.25 - 0.2, -0.6 + 0.1, 0.0, 0.5, 0.3, 0.0,
         -0.25 - 0.2, -0.5 + 0.1, 0.0, 0.5, 0.3, 0.0,
         #Hojas
         -0.27 - 0.2, -0.5 + 0.1, 0.0, 0.0, 0.8, 0.0,
         -0.27 - 0.2, -0.4 + 0.1, 0.0, 0.0, 0.8, 0.0,
         -0.18 - 0.2, -0.5 + 0.1, 0.0, 0.0, 0.8, 0.0,
         -0.18 - 0.2, -0.4 + 0.1, 0.0, 0.0, 0.8, 0.0,
         
         #Arbol 3
         #Tronco
         -0.2*0.8 +0.6, -0.5*0.8 + 0.3, 0.0, 0.5, 0.3, 0.0,
         -0.2*0.8 +0.6, -0.6*0.8 + 0.3, 0.0, 0.5, 0.3, 0.0,
         -0.25*0.8 +0.6, -0.6*0.8 + 0.3, 0.0, 0.5, 0.3, 0.0,
         -0.25*0.8 +0.6, -0.5*0.8 + 0.3, 0.0, 0.5, 0.3, 0.0,
         #Hojas
         -0.27*0.8 +0.6, -0.5*0.8 + 0.3, 0.0, 0.0, 0.8, 0.0,
         -0.27*0.8 +0.6, -0.4*0.8 + 0.3, 0.0, 0.0, 0.8, 0.0,
         -0.18*0.8 +0.6, -0.5*0.8 + 0.3, 0.0, 0.0, 0.8, 0.0,
         -0.18*0.8 +0.6, -0.4*0.8 + 0.3, 0.0, 0.0, 0.8, 0.0,
         
         #Arbol 4
         #Tronco
         -0.2*0.7 -0.1, -0.5*0.7 + 0.2, 0.0, 0.5, 0.3, 0.0,
         -0.2*0.7 -0.1, -0.6*0.7 + 0.2, 0.0, 0.5, 0.3, 0.0,
         -0.25*0.7 -0.1, -0.6*0.7 + 0.2, 0.0, 0.5, 0.3, 0.0,
         -0.25*0.7 -0.1, -0.5*0.7 + 0.2, 0.0, 0.5, 0.3, 0.0,
         #Hojas
         -0.27*0.7 -0.1, -0.5*0.7 + 0.2, 0.0, 0.0, 0.8, 0.0,
         -0.27*0.7 -0.1, -0.4*0.7 + 0.2, 0.0, 0.0, 0.8, 0.0,
         -0.18*0.7 -0.1, -0.5*0.7 + 0.2, 0.0, 0.0, 0.8, 0.0,
         -0.18*0.7 -0.1, -0.4*0.7 + 0.2, 0.0, 0.0, 0.8, 0.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,#Arbol 1
                2, 3, 0,

                4, 5, 6,
                5, 6, 7,
                
                #Arbol 2
                8, 9, 10,
                10, 11, 8,

                12, 13, 14,
                13, 14, 15,
                
                #Arbol 3
                16, 17, 18,
                18, 19, 16,
                
                20, 21, 22,
                21, 22, 23,
                
                #Arbol 4
                24, 25, 26,
                26, 27, 24,
                
                28, 29, 30,
                29, 30, 31,
                
                #Arbol 5
                32, 33, 34,
                34, 35, 32,
                
                36, 37, 38,
                37, 38, 39]

    return Shape(vertices, indices)

def create_river(x0, y0, width, height):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        #Lago
         0.2, 0.1, 0.0, 0.0, 0.0, 0.6,
         0.13, -0.1, 0.0, 0.0, 0.0, 0.8,
         -0.1, 0.1, 0.0, 0.0, 0.0, 0.6,
         -0.05, -0.1, 0.0, 0.0, 0.0, 0.8,
         #Rio
        0.1, -0.1, 0.0, 0.0, 0.0, 0.8,
        0.0, -0.1, 0.0, 0.0, 0.0, 0.8,
        0.0, -0.5, 0.0, 0.0, 0.0, 1.0]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2,
                1, 2, 3,
                4, 5, 6]

    return Shape(vertices, indices)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800

    window = glfw.create_window(width, height, "Ejercicio 2", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    simplePipeline = SimpleShaderProgram()
    greenPipeline = GreenShaderProgram()
    nightPipeline = NightShaderProgram()

    # Creating shapes on GPU memory
    sky_shape = create_sky(y0=0.2, y1=1.0)
    gpu_sky = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_sky)
    greenPipeline.setupVAO(gpu_sky)
    nightPipeline.setupVAO(gpu_sky)
    gpu_sky.fillBuffers(sky_shape.vertices, sky_shape.indices, GL_STATIC_DRAW)


    island_shape = create_island(x0=-1.0, y0=0.2, width=1.6, height=0.8)
    gpu_island = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_island)
    greenPipeline.setupVAO(gpu_island)
    nightPipeline.setupVAO(gpu_island)
    gpu_island.fillBuffers(island_shape.vertices, island_shape.indices, GL_STATIC_DRAW)

    volcano_shape = create_volcano(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_volcano = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_volcano)
    greenPipeline.setupVAO(gpu_volcano)
    nightPipeline.setupVAO(gpu_volcano)
    gpu_volcano.fillBuffers(volcano_shape.vertices, volcano_shape.indices, GL_STATIC_DRAW)

    arbol_shape = create_arbol(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_arbol = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_arbol)
    greenPipeline.setupVAO(gpu_arbol)
    nightPipeline.setupVAO(gpu_arbol)
    gpu_arbol.fillBuffers(arbol_shape.vertices, arbol_shape.indices, GL_STATIC_DRAW)
    
    river_shape = create_river(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_river = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_river)
    greenPipeline.setupVAO(gpu_river)
    nightPipeline.setupVAO(gpu_river)
    gpu_river.fillBuffers(river_shape.vertices, river_shape.indices, GL_STATIC_DRAW)

    lava_shape = create_lava(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_lava = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_lava)
    greenPipeline.setupVAO(gpu_lava)
    nightPipeline.setupVAO(gpu_lava)
    gpu_lava.fillBuffers(lava_shape.vertices, lava_shape.indices, GL_STATIC_DRAW)

    sol_shape = create_sol(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_sol = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_sol)
    greenPipeline.setupVAO(gpu_sol)
    nightPipeline.setupVAO(gpu_sol)
    gpu_sol.fillBuffers(sol_shape.vertices, sol_shape.indices, GL_STATIC_DRAW)

    luna_shape = create_luna(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_luna = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_luna)
    greenPipeline.setupVAO(gpu_luna)
    nightPipeline.setupVAO(gpu_luna)
    gpu_luna.fillBuffers(luna_shape.vertices, luna_shape.indices, GL_STATIC_DRAW)
    
    circulo_shape = create_circle(x0=-0.35, y0=0.1, width=0.8, height=0.5)
    gpu_circulo = GPUShape().initBuffers()
    simplePipeline.setupVAO(gpu_circulo)
    greenPipeline.setupVAO(gpu_circulo)
    nightPipeline.setupVAO(gpu_circulo)
    gpu_circulo.fillBuffers(circulo_shape.vertices, circulo_shape.indices, GL_STATIC_DRAW)


    # Setting up the clear screen color
    glClearColor(0.2, 0.2, 0.2, 1.0)

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

        if (controller.effect1):
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_island)
            simplePipeline.drawCall(gpu_volcano)
            simplePipeline.drawCall(gpu_arbol)
            simplePipeline.drawCall(gpu_river)
            simplePipeline.drawCall(gpu_lava)
            simplePipeline.drawCall(gpu_circulo)
            glUseProgram(greenPipeline.shaderProgram)
            greenPipeline.drawCall(gpu_sol)
        elif (controller.effect2):
            glUseProgram(nightPipeline.shaderProgram)
            nightPipeline.drawCall(gpu_sky)
            nightPipeline.drawCall(gpu_island)
            nightPipeline.drawCall(gpu_volcano)
            nightPipeline.drawCall(gpu_arbol)
            nightPipeline.drawCall(gpu_river)
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_lava)
            simplePipeline.drawCall(gpu_luna)
        else:
            glUseProgram(simplePipeline.shaderProgram)
            simplePipeline.drawCall(gpu_sky)
            simplePipeline.drawCall(gpu_island)
            simplePipeline.drawCall(gpu_volcano)
            simplePipeline.drawCall(gpu_arbol)
            simplePipeline.drawCall(gpu_river)
            simplePipeline.drawCall(gpu_lava)
            simplePipeline.drawCall(gpu_sol)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpu_sky.clear()
    gpu_island.clear()
    gpu_volcano.clear()
    gpu_arbol.clear()
    gpu_river.clear()
    gpu_lava.clear()
    gpu_sol.clear()
    gpu_luna.clear()

    glfw.terminate()