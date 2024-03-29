import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.performance_monitor as pm
import grafica.lighting_shaders as ls
import grafica.scene_graph as sg
from shapes3d import *

import imgui
from imgui.integrations.glfw import GlfwRenderer

class PolarCamera:
    def __init__(self):
        self.center = np.array([0.0, 0.0, -0.5])
        self.theta = 0
        self.rho = 5
        self.eye = np.array([0.0, 0.0, 0.0])
        self.height = 0.5
        self.up = np.array([0, 0, 1])
        self.viewMatrix = None

    def set_theta(self, delta):
        self.theta = (self.theta + delta) % (np.pi * 2)

    def set_rho(self, delta):
        if ((self.rho + delta) > 0.1):
            self.rho += delta

    def update_view(self):
        self.eye[0] = self.rho * np.sin(self.theta) + self.center[0]
        self.eye[1] = self.rho * np.cos(self.theta) + self.center[1]
        self.eye[2] = self.height + self.center[2]

        viewMatrix = tr.lookAt(
            self.eye,
            self.center,
            self.up
        )
        return viewMatrix

class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True

        self.is_up_pressed = False
        self.is_down_pressed = False
        self.is_left_pressed = False
        self.is_right_pressed = False

        self.polar_camera = PolarCamera()

    def get_camera(self):
        return self.polar_camera

    def on_key(self, window, key, scancode, action, mods):

        if key == glfw.KEY_UP:
            if action == glfw.PRESS:
                self.is_up_pressed = True
            elif action == glfw.RELEASE:
                self.is_up_pressed = False

        if key == glfw.KEY_DOWN:
            if action == glfw.PRESS:
                self.is_down_pressed = True
            elif action == glfw.RELEASE:
                self.is_down_pressed = False

        if key == glfw.KEY_RIGHT:
            if action == glfw.PRESS:
                self.is_right_pressed = True
            elif action == glfw.RELEASE:
                self.is_right_pressed = False

        if key == glfw.KEY_LEFT:
            if action == glfw.PRESS:
                self.is_left_pressed = True
            elif action == glfw.RELEASE:
                self.is_left_pressed = False
        
        if key == glfw.KEY_SPACE:
            if action == glfw.PRESS:
                self.fillPolygon = not self.fillPolygon

        if key == glfw.KEY_ESCAPE:
            if action == glfw.PRESS:
                glfw.set_window_should_close(window, True)

        elif key == glfw.KEY_LEFT_CONTROL:
            if action == glfw.PRESS:
                self.showAxis = not self.showAxis


    #Funcion que recibe el input para manejar la camara
    def update_camera(self, delta):
        if self.is_left_pressed:
            self.polar_camera.set_theta(-2 * delta)

        if self.is_right_pressed:
            self.polar_camera.set_theta( 2 * delta)

        if self.is_up_pressed:
            self.polar_camera.set_rho(-5 * delta)

        if self.is_down_pressed:
            self.polar_camera.set_rho(5 * delta)

def transformGuiOverlay(lightPos, ka, kd, ks):

    # start new frame context
    imgui.new_frame()

    # open new window context
    imgui.begin("Material control", False, imgui.WINDOW_ALWAYS_AUTO_RESIZE)

    # draw text label inside of current window
    imgui.text("Configuration sliders")

    edited, lightPos[0] = imgui.slider_float("light position X", lightPos[0], -2.3, 2.3)
    edited, lightPos[1] = imgui.slider_float("light position Y", lightPos[1], -2.3, 2.3)
    edited, lightPos[2] = imgui.slider_float("light position Z", lightPos[2], -2.3, 2.3)
    
    edited, ka = imgui.color_edit3("ka", ka[0], ka[1], ka[2])
    if imgui.button("clean ka"):
        ka = (1.0, 1.0, 1.0)
    edited, kd = imgui.color_edit3("kd", kd[0], kd[1], kd[2])
    if imgui.button("clean kd"):
        kd = (1.0, 1.0, 1.0)
    edited, ks = imgui.color_edit3("ks", ks[0], ks[1], ks[2])
    if imgui.button("clean ks"):
        ks = (1.0, 1.0, 1.0)

    # close current window context
    imgui.end()

    # pass all drawing comands to the rendering pipeline
    # and close frame context
    imgui.render()
    imgui.end_frame()

    return lightPos, ka, kd, ks

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "P0 - Scene"

    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    controller = Controller()
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)

     # Different shader programs for different lighting strategies
    phongPipeline = ls.SimplePhongShaderProgram()
    phongTexPipeline = ls.SimpleTexturePhongShaderProgram()

    # This shader program does not consider lighting
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(mvpPipeline, bs.createAxis(4))

    gpuRedCube = createGPUShape(phongPipeline, bs.createColorNormalsCube(1,0,0))

    scene = createScene(phongPipeline)
    cube1 = createCube1(phongPipeline)
    cube2 = createToroideNode2(0.3, 0.3, 0.3, phongPipeline)
    sphere = createToroideNode(0.3, 0.3, 0.3, phongPipeline)
    tex_sphere   = createTexToroideNode(phongTexPipeline)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)
    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)
    t0 = glfw.get_time()

    # initilize imgui context (see documentation)
    imgui.create_context()
    impl = GlfwRenderer(window)

    controller = Controller()
    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controller.on_key)
    #standar
    lightPos = [0, 0, 2.3]
    ka = [0.2, 0.2, 0.2] 
    kd = [0.5, 0.5, 0.5]
    ks = [1.0, 1.0, 1.0] 
    #oro pulido
    kaO = [0.24725, 0.1995, 0.0645] 
    kdO = [0.34615, 0.3143, 0.0903]
    ksO = [0.797357, 0.723991, 0.208006]
    #obsidiana
    kaS = [0.05375, 0.05, 0.06625] 
    kdS = [0.18275, 0.17, 0.22525]
    ksS = [0.332741, 0.328634, 0.346435]

    # Application loop
    while not glfw.window_should_close(window):
        # Variables del tiempo
        t1 = glfw.get_time()
        delta = t1 -t0
        t0 = t1

        
        impl.process_inputs()
        # Using GLFW to check for input events
        glfw.poll_events()

        controller.update_camera(delta)
        camera = controller.get_camera()
        viewMatrix = camera.update_view()

        # Setting up the projection transform
        projection = tr.perspective(60, float(width) / float(height), 0.1, 100)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

         # imgui function

        lightPos, ka, kd, ks = \
            transformGuiOverlay(lightPos, ka, kd, ks)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawCall(gpuAxis, GL_LINES)

        lightingPipeline = phongPipeline
        #lightposition = [1*np.cos(t1), 1*np.sin(t1), 2.3]
        if int(t1%3) == 0:
            r = 1
            g = 1
            b = 1
        if int(t1%3) == 1:
            r = 0.5
            g = 0.5
            b = 0.5
        if int(t1%3) == 2:
            r = 0.1
            g = 0.1
            b = 0.1
        #r = np.abs(((0.5*t1+0.00) % 2)-1)
        #g = np.abs(((0.5*t1+0.33) % 2)-1)
        #b = np.abs(((0.5*t1+0.66) % 2)-1)

        # Setting all uniform shader variables
        
        glUseProgram(lightingPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "La"), r, g, b)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ld"), r, g, b)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ls"), r, g, b)

        # Object is barely visible at only ambient. Diffuse behavior is slightly red. Sparkles are white
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1], lightPos[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 38)
        
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(lightingPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        # Drawing
        sg.drawSceneGraphNode(scene, lightingPipeline, "model")

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), kaS[0], kaS[1], kaS[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), kdS[0], kdS[1], kdS[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), ksS[0], ksS[1], ksS[2])

        
        sg.drawSceneGraphNode(sphere, lightingPipeline, "model")
        
        glUniform1ui(glGetUniformLocation(lightingPipeline.shaderProgram, "shininess"), 83)

        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ka"), kaO[0], kaO[1], kaO[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Kd"), kdO[0], kdO[1], kdO[2])
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "Ks"), ksO[0], ksO[1], ksO[2])
        
        sg.drawSceneGraphNode(cube1, lightingPipeline, "model")
        sg.drawSceneGraphNode(cube2, lightingPipeline, "model")
        glUseProgram(phongTexPipeline.shaderProgram)
        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "La"), 0.25, 0.25, 0.25)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ld"), 0.5, 0.5, 0.5)
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "lightPosition"), lightPos[0], lightPos[1], lightPos[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
        glUniform1ui(glGetUniformLocation(phongTexPipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "constantAttenuation"), 0.001)
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(phongTexPipeline.shaderProgram, "quadraticAttenuation"), 0.01)
        
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ka"), ka[0], ka[1], ka[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Kd"), kd[0], kd[1], kd[2])
        glUniform3f(glGetUniformLocation(phongTexPipeline.shaderProgram, "Ks"), ks[0], ks[1], ks[2])

        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "view"), 1, GL_TRUE, viewMatrix)
        glUniformMatrix4fv(glGetUniformLocation(phongTexPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

        sg.drawSceneGraphNode(tex_sphere, phongTexPipeline, "model")
        
        # Drawing the imgui texture over our drawing
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        impl.render(imgui.get_draw_data())

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    gpuAxis.clear()
    impl.shutdown()
    scene.clear()
    cube1.clear()
    cube2.clear()

    glfw.terminate()