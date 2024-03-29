"""Funciones para crear distintas figuras y escenas en 3D """

import numpy as np
import math
from OpenGL.GL import *
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.scene_graph as sg

# Convenience function to ease initialization
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

def createScene(pipeline):

    gpuRedCube = createGPUShape(pipeline, bs.createColorNormalsCube(1, 0, 0))
    gpuGreenCube = createGPUShape(pipeline, bs.createColorNormalsCube(0, 1, 0))
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.7, 0.7, 0.7))
    gpuWhiteCube = createGPUShape(pipeline, bs.createColorNormalsCube(1, 1, 1))

    redCubeNode = sg.SceneGraphNode("redCube")
    redCubeNode.childs = [gpuRedCube]

    greenCubeNode = sg.SceneGraphNode("greenCube")
    greenCubeNode.childs = [gpuGreenCube]

    grayCubeNode = sg.SceneGraphNode("grayCube")
    grayCubeNode.childs = [gpuGrayCube]

    whiteCubeNode = sg.SceneGraphNode("whiteCube")
    whiteCubeNode.childs = [gpuWhiteCube]

    rightWallNode = sg.SceneGraphNode("rightWall")
    rightWallNode.transform = tr.translate(1, 0, 0)
    rightWallNode.childs = [redCubeNode]

    leftWallNode = sg.SceneGraphNode("leftWall")
    leftWallNode.transform = tr.translate(-1, 0, 0)
    leftWallNode.childs = [greenCubeNode]

    backWallNode = sg.SceneGraphNode("backWall")
    backWallNode.transform = tr.translate(0,-1, 0)
    backWallNode.childs = [grayCubeNode]

    lightNode = sg.SceneGraphNode("lightSource")
    lightNode.transform = tr.matmul([tr.translate(0, 0, -0.4), tr.scale(0.12, 0.12, 0.12)])
    lightNode.childs = [grayCubeNode]

    ceilNode = sg.SceneGraphNode("ceil")
    ceilNode.transform = tr.translate(0, 0, 1)
    ceilNode.childs = [grayCubeNode, lightNode]

    floorNode = sg.SceneGraphNode("floor")
    floorNode.transform = tr.translate(0, 0, -1)
    floorNode.childs = [grayCubeNode]

    sceneNode = sg.SceneGraphNode("scene")
    sceneNode.transform = tr.matmul([tr.translate(0, 0, 0), tr.scale(5, 5, 5)])
    sceneNode.childs = [rightWallNode, leftWallNode, backWallNode, ceilNode, floorNode]

    trSceneNode = sg.SceneGraphNode("tr_scene")
    trSceneNode.childs = [sceneNode]

    return trSceneNode

def createCube1(pipeline):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.5, 0.5, 0.5))

    grayCubeNode = sg.SceneGraphNode("grayCube")
    grayCubeNode.childs = [gpuGrayCube]

    objectNode = sg.SceneGraphNode("object1")
    objectNode.transform = tr.matmul([
        tr.translate(0.25,-0.15,-0.25),
        tr.rotationZ(np.pi*0.15),
        tr.scale(0.2,0.2,0.5)
    ])
    objectNode.childs = [grayCubeNode]

    scaledObject = sg.SceneGraphNode("object1")
    scaledObject.transform = tr.scale(5, 5, 5)
    scaledObject.childs = [objectNode]

    return scaledObject

def createCube2(pipeline):
    gpuGrayCube = createGPUShape(pipeline, bs.createColorNormalsCube(0.5, 0.5, 0.5))

    grayCubeNode = sg.SceneGraphNode("grayCube")
    grayCubeNode.childs = [gpuGrayCube]

    objectNode = sg.SceneGraphNode("object1")
    objectNode.transform = tr.matmul([
        tr.translate(-0.25,-0.15,-0.35),
        tr.rotationZ(np.pi*-0.2),
        tr.scale(0.3,0.3,0.3)
    ])
    objectNode.childs = [grayCubeNode]

    scaledObject = sg.SceneGraphNode("object1")
    scaledObject.transform = tr.scale(5, 5, 5)
    scaledObject.childs = [objectNode]

    return scaledObject

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

def createTextureNormalSphere(N):
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
                vertices += [v0[0], v0[1], v0[2], 0, 1, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 1, 1, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 0.5, 0, n2[0], n2[1], n2[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            # Creamos los quads inferiores
            elif i == (N-2):
                vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0.5, 1, n1[0], n1[1], n1[2]]
                vertices += [v3[0], v3[1], v3[2], 1, 0, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                c += 3
            
            # Creamos los quads intermedios
            else: 
                vertices += [v0[0], v0[1], v0[2], 0, 0, n0[0], n0[1], n0[2]]
                vertices += [v1[0], v1[1], v1[2], 0, 1, n1[0], n1[1], n1[2]]
                vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
                vertices += [v3[0], v3[1], v3[2], 0, 1, n3[0], n3[1], n3[2]]
                indices += [ c + 0, c + 1, c +2 ]
                indices += [ c + 2, c + 3, c + 0 ]
                c += 4
    return bs.Shape(vertices, indices)


def createSphereNode(r, g, b, pipeline):
    sphere = createGPUShape(pipeline, createColorNormalSphere(20, r,g,b))

    sphereNode = sg.SceneGraphNode("sphere")
    sphereNode.transform =tr.matmul([
        tr.translate(0.25,0.15,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    sphereNode.childs = [sphere]

    scaledSphere = sg.SceneGraphNode("sc_sphere")
    scaledSphere.transform = tr.scale(5, 5, 5)
    scaledSphere.childs = [sphereNode]

    return scaledSphere

def createTexSphereNode(pipeline):
    sphere = createTextureGPUShape(createTextureNormalSphere(20), pipeline, "sprites/madera.jpg")

    sphereNode = sg.SceneGraphNode("sphere")
    sphereNode.transform =tr.matmul([
        tr.translate(-0.25,0.25,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    sphereNode.childs = [sphere]

    scaledSphere = sg.SceneGraphNode("sc_sphere")
    scaledSphere.transform = tr.scale(5, 5, 5)
    scaledSphere.childs = [sphereNode]

    return scaledSphere

def createToroide(N, r, g, b):
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
def createTexToroide(N):
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

            vertices += [v0[0], v0[1], v0[2], 0, 1, n0[0], n0[1], n0[2]]
            vertices += [v1[0], v1[1], v1[2], 0, 0, n1[0], n1[1], n1[2]]
            vertices += [v2[0], v2[1], v2[2], 1, 1, n2[0], n2[1], n2[2]]
            vertices += [v3[0], v3[1], v3[2], 1, 0, n3[0], n3[1], n3[2]]
            indices += [ c + 0, c + 1, c +2 ]
            indices += [ c + 1, c + 2, c + 3 ]
            c += 4

    return bs.Shape(vertices, indices)



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


def tobogan(N,r,g,b):
    curva = CurvaTobogan(N)
    vertices = []
    indices = []
    dTheta = 2 * np.pi /N
    dPhi = 2 * np.pi /N
    R = 0.5
    rho = 0.2
    c = 0

    for i in curva:
        punto1 = i
        punto2 = i+1
        theta = i * dTheta
        theta1 = (i + 1) * dTheta

    
        
        v0 = [i*np.cos(theta), i*np.sin(theta), rho]
        v1 = [(i*np.cos(theta))*np.cos(theta), (i*np.cos(theta))*np.sin(theta),  rho]
        v2 = [(i*np.cos(theta))*np.cos(theta1), (i*np.cos(theta))*np.sin(theta1), rho]
        v3 = [(i*np.cos(theta))*np.cos(theta1), (i*np.cos(theta))*np.sin(theta1), rho]
        n0 = [np.cos(theta)*np.cos(theta), np.sin(theta)*np.cos(theta), 0.5]
        n1 = [np.cos(theta)*np.cos(theta), np.sin(theta)*np.cos(theta), 0.5]
        n2 = [np.cos(theta1)*np.cos(theta), np.sin(theta1)*np.cos(theta), 0.5]
        n3 = [np.cos(theta1)*np.cos(theta), np.sin(theta1)*np.cos(theta), 0.5]

        vertices += [v0[0], v0[1], v0[2], r, g, b, n0[0], n0[1], n0[2]]
        vertices += [v1[0], v1[1], v1[2], r, g, b, n1[0], n1[1], n1[2]]
        vertices += [v2[0], v2[1], v2[2], r, g, b, n2[0], n2[1], n2[2]]
        vertices += [v3[0], v3[1], v3[2], r, g, b, n3[0], n3[1], n3[2]]
        indices += [ c + 0, c + 1, c +2 ]
        indices += [ c + 1, c + 2, c + 3 ]
        c += 4

    return bs.Shape(vertices, indices)

def createToboganNode(r, g, b, pipeline):
    Toroide = createGPUShape(pipeline, Tobogan(20, r,g,b))

    ToboganNode = sg.SceneGraphNode("Tobogan")
    ToboganNode.transform =tr.matmul([
        tr.translate(0.25,0.3,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    ToboganNode.childs = [Tobogan]

    scaledTobogan = sg.SceneGraphNode("sc_Tobogan")
    scaledTobogan.transform = tr.scale(5, 5, 5)
    scaledTobogan.childs = [ToboganNode]

    return scaledTobogan

def createTexToroideNode(pipeline):
    toroide = createTextureGPUShape(createTexToroide(20), pipeline, "sprites/madera.jpg")

    toroideNode = sg.SceneGraphNode("toroide")
    toroideNode.transform =tr.matmul([
        tr.translate(-0.25,0.25,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    toroideNode.childs = [toroide]

    scaledToroide = sg.SceneGraphNode("sc_Toroide")
    scaledToroide.transform = tr.scale(5, 5, 5)
    scaledToroide.childs = [toroideNode]


    return scaledToroide
def createToroideNode2(r, g, b, pipeline):
    Toroide2 = createGPUShape(pipeline, createToroide(20, r,g,b))

    ToroideNode2 = sg.SceneGraphNode("Toroide2")
    ToroideNode2.transform =tr.matmul([
        tr.translate(-0.25,-0.15,-0.35),
        tr.scale(0.3,0.3,0.3)
    ])
    ToroideNode2.childs = [Toroide2]

    scaledToroide = sg.SceneGraphNode("sc_Toroide2")
    scaledToroide.transform = tr.scale(5, 5, 5)
    scaledToroide.childs = [ToroideNode2]

    return scaledToroide