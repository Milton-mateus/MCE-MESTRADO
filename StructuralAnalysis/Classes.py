# -*- coding: utf-8 -*-
import numpy as np
import DataReader
import os

class Node:
    def __init__(self, id, coords):
        self.id = id
        self.coords = np.array(coords)
        self.flagRestrictions = False
        self.restrictions = list()
        self.typeRestrictions = list()
        self.prescDisp = list()
        self.flexibleSupports = list()
        self.nodalLoads = None
        self.ReactForces = None
        self.incidElems = 0

    def defineRestrictions(self, restrict):
        self.restrictions = restrict
    
    def defineNodalLoads(self, nodalLoads):
        self.nodalLoads = nodalLoads

    def definePrescribedDisplacements(self, prescribleDisplaces):
        self.prescDisp = prescribleDisplaces
    
    def ElemIncidence(self, Elems):
        pass

class Material:
    """
    Define as propriedades de um material
    """
    def __init__(self, id, E):
        """
        E: Módulo de Elasticidade
        """
        self.id = id
        self.E = E
    
    # def __init__(self, id, E, poisson):
    #     """
    #     E: Módulo de Elasticidade
    #     poisson: Módulo de poisson
    #     """
    #     self.id = id
    #     self.E = E
    #     self.poisson = poisson
    
    # def __init__(self, id, E, poisson, shear):
    #     """
    #     E: Módulo de Elasticidade
    #     poisson: Módulo de poisson
    #     shear: Módulo de cisalhamento
    #     """
    #     self.id = id
    #     self.E = E
    #     self.poisson = poisson
    #     self.shear = shear
        
    # def __init__(self, id, E, poisson, shear, thermExp):
    #     """
    #     E: Módulo de Elasticidade
    #     poisson: Módulo de poisson
    #     shear: Módulo de cisalhamento
    #     thermExp: Coeficiente de expansão térmica
    #     """
    #     self.id = id
    #     self.E = E
    #     self.poisson = poisson
    #     self.shear = shear
    #     self.thermExp = thermExp

class Section:
    """
    Define as propriedades geométricas de uma seção transversal 
    """        
    def __init__(self, id, Ax):
        """
        Ax: Área da seção transversal
        Iy: Momento de inércia em relação ao eixo y
        """
        self.id = id
        self.Ax = Ax

class Elem:
    def __init__(self, id, initNode: Node, finalNode: Node, mat: Material, sec: Section, TypeAn: str):
        """
        Define as propriedades de um elemento
        """
        self.nGLpN = 2                          # Número de graus de liberdade por nó
        self.id = id                            # Define a ID do elemento
        self.initNode: Node = initNode          # Define o nó inicial
        self.finalNode: Node = finalNode        # Define o nó final
        self.material: Material = mat           # Define o material
        self.section: Section = sec             # Define as propriedades da seção transversal
        self.L = self.defineLength()            # Define o comprimento da barra e os cossenos diretores

        self.TypeAn = TypeAn                    # Define o tipo de análise na qual o elemento será utilizado
        if TypeAn == "Truss2D":
            self.Cossines2D()                   # Define os cossenos diretores em 2D
        elif TypeAn == "Truss3D":
            self.Cossines3D()                   # Define os cossenos diretores em 3D

        self.defineKint()                       # Define a matriz de rigidez interna do elemento
        self.defineRotMatrix()                  # Define a matriz de rotação do sistema interno ao local
        self.defineKlocal()                     # Define a matriz de rigidez local do elemento
            

    def defineLength(self):
        """
        define o comprimento do elemento
        """
        return np.linalg.norm(self.finalNode.coords-self.initNode.coords)
    
    def Cossines2D(self):
        """
        define os cossenos diretores em 2D
        """
        self.cossineX = (self.finalNode.coords[0]-self.initNode.coords[0])/self.L
        self.cossineY = (self.finalNode.coords[1]-self.initNode.coords[1])/self.L
        
    def Cossines3D(self):
        """
        define os cossenos diretores em 3D
        """
        self.cossineX = (self.finalNode.coords[0]-self.initNode.coords[0])/self.L
        self.cossineY = (self.finalNode.coords[1]-self.initNode.coords[1])/self.L
        self.cossineY = (self.finalNode.coords[2]-self.initNode.coords[2])/self.L

    def defineKint(self):
        """
        Define a matriz de rigidez interna do elemento
        """
        # Cria a matriz vazia
        self.Kint = np.zeros([4,4])                  

        # Coeficiente de rigidez     
        k = (self.material.E*self.section.Ax) / self.L 

        # Atualiza os coeficientes  
        self.Kint[0,0] = k;     self.Kint[0,2] = -k              
        self.Kint[2,0] = -k;    self.Kint[2,2] = k


    def defineRotMatrix(self):
        """
        Define a matriz de rotação do sistema interno ao local
        """
        # Cria a matriz vazia
        self.rotMatrix: np.array = np.zeros([4,4])

        # Atualiza os coeficientes
        self.rotMatrix[0,0] = self.cossineX;    self.rotMatrix[0,1] = self.cossineY
        self.rotMatrix[1,0] = -self.cossineY;   self.rotMatrix[1,1] = self.cossineX
        self.rotMatrix[2,2] = self.cossineX;    self.rotMatrix[2,3] = self.cossineY
        self.rotMatrix[3,2] = -self.cossineY;   self.rotMatrix[3,3] = self.cossineX
        
    def defineKlocal(self):
        """
        Define a matriz de rigidez local do elemento
        """
        self.Klocal = self.rotMatrix.T @ self.Kint @ self.rotMatrix

    def defineKinematicIncidenteMatrix(self,nGLE: int):
        """
        Define a matriz de incidência cinemática da estrutura
        """
        # Cria a matriz vazia 
        self.KinIncMatrix = np.zeros([4,nGLE])
        
        # define a incidência cinemática
        for i in range(self.nGLpN):
            self.KinIncMatrix[i,(self.initNode.id-1)*2 + i] = 1
        for i in range(self.nGLpN):
            self.KinIncMatrix[self.nGLpN+i,(self.finalNode.id-1)*2 + i] = 1



    def defineKglobalElement(self):
        """
        Define a matriz de rigidez global do elemento
        """
        self.KGE = self.KinIncMatrix.T @ self.Klocal @ self.KinIncMatrix

    def calculateKGE(self, nGLE: int):
        """
        Calcula as matrizes de incidência cinemática e a matriz de rigidez global do elemento
        """
        self.defineKinematicIncidenteMatrix(nGLE)    # Matriz de incidência cinemática
        self.defineKglobalElement()                  # Matriz de rigidez global do elemento
        return self.KGE

    def calcInternalForces(self, NodalDisp: np.ndarray):
        """
        Calcula o esforço interno solicitante do elemento estrutural
        """

        # Calcula os esforços internos nodais do elemento 
        self.internalForces: np.ndarray = self.Kint @ self.rotMatrix @ self.KinIncMatrix @ NodalDisp
        
        # Cria o vetor de EIS de acordo com a convenção
        self.internalForcesRef = self.internalForces.copy()
        
        # Aplica a convenção de EIS
        self.internalForcesRef[0] = -self.internalForces[0]
        self.internalForcesRef[3] = -self.internalForces[3]
    
    def calcLocalnGlobalForces(self):
        """
        Calcula os vetores de forças local e global da estrutura
        """
        # Calcula as forças locais do elemento
        self.localForces: np.ndarray =  self.rotMatrix.T @ self.internalForces
        
        # Calcula as forças globais do elemento
        self.globalForces: np.ndarray =  self.KinIncMatrix.T @ self.localForces

