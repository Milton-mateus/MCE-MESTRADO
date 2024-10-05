# -*- coding: utf-8 -*-
import numpy as np
import DataReader
import os
from Classes import Node, Elem, Material, Section
from PrintStructure import plotStructure

class Truss2D:
    def __init__(self, data):
        self.type = "Truss2D"
        self.GLpE = 2
        self.defineNodes(data["nodes"])
        self.defineNodalLoads(data["nodalLoads"])
        self.defineRestrictions(data["restrictions"])
        self.defineMaterials(data["material"])
        self.defineSections(data["sectionProp"])
        self.defineElements(data["elements"])

    def defineNodes(self, Nodes):
        """
        Define os nós da treliça
        """
        # Cria a lista vazia
        self.nodes: list[Node] = []
        # Percorre a lista de nós
        for node in Nodes:
            # Cria um nó
            self.nodes.append(Node(node["id"],node["coordenadas"]))
        # Número total de nós
        self.nNodes = len(self.nodes)
        # Número total de graus de liberdade
        self.nGL = self.nNodes*2

    def defineRestrictions(self, Restrictions):
        """
        Define as ações nodais na estrutura
        """
        # Número total de restrições
        self.nRestrictions = 0

        # Adiciona restrições aos nós
        for restrict in Restrictions:
            self.nodes[restrict["no"]-1].restrictions = restrict["restricoes"]  # Atribui as restrições ao nó
            self.nodes[restrict["no"]-1].typeRestrictions = restrict["types"]   # Especifica o tipo de restrição
            self.nodes[restrict["no"]-1].flagRestrictions = True                # Flag de apoios
            contPresc = 0;  contFlex = 0
            for i,type in enumerate(self.nodes[restrict["no"]-1].typeRestrictions):
                if self.nodes[restrict["no"]-1].restrictions[i] == 1:
                    if type == "prescrible":
                        self.nodes[restrict["no"]-1].prescDisp.append(restrict["prescrible"][contPresc])
                        contPresc += 1
                    elif type == "flexible":
                        self.nodes[restrict["no"]-1].flexibleSupports.append(restrict["flexible"][contFlex])
                        contFlex += 1
            self.nRestrictions += np.sum(restrict["restricoes"])                # Adiciona um GL ao contador
            
    def defineNodalLoads(self, NodalLoads):
        """
        Define as ações nodais na estrutura
        """
        # Adiciona as ações nodais aos nós
        for load in NodalLoads:                                     # Percorre os carregamentos definidos
            self.nodes[load["no"]-1].nodalLoads = load["forcas"]    # Vincula os carregamentos às forças

    def defineMaterials(self, Materials):
        """
        Define os materiais da estrutura
        """
        # Cria a lista vazia
        self.materials: list[Material] = []
        # Percorre a lista de materiais
        for material in Materials:
            # Cria um material
            self.materials.append(Material(material["id"], material["modulo_elasticidade"]))
        self.nMat = len(self.materials)                 # Número de materiais definidos
        
    def defineSections(self, Sections):
        """
        Define as seções transversais de elementos da estrutura
        """
        # Cria a lista vazia
        self.sections: list[Section] = []
        # Percorre a lista de materiais
        for section in Sections:
            # Cria um material
            self.sections.append(Section(section["id"], section["area"]))
        self.nSec = len(self.sections)                  # Número de seções definidas

    def defineElements(self, Elements):
        """
        Define os elementos da estrutura
        """
        # Cria a lista vazia
        self.elements: list[Elem] = []
        # Percorre a lista de elementos
        for element in Elements:
            # Cria um elemento
            self.elements.append(Elem(element["id"], self.nodes[element["NI"]-1], self.nodes[element["NF"]-1]
                                      , self.materials[element["material"]-1], self.sections[element["sectionProp"]-1], self.type))
        self.nElem = len(self.elements)                 # Número de nelementos

    def calculateKGS_Singular(self):
        """
        Define a matriz de rigidez global singular da estrutura (pura)
        """
        # Cria a matriz vazia
        self.KGS_Singular = np.zeros((self.nGL, self.nGL))
        # Calcula a matriz de rigidez global da estrutura (pura ou singular)
        for element in self.elements:                   # Percorre os elementos
            element.calculateKGE(self.nGL)              # Calcula a matriz de rigidez global do elemento
            self.KGS_Singular += element.KGE                     # Adiciona a contribuição da KGE do elemento para a KGS

    # def calculateKGS(self):
    #     """
    #     Define a matriz de rigidez global (considerando possíveis apoios flexíveis)
    #     """
    #     # Calcula a matriz de rigidez singular da estrutura
    #     self.defineKGS_Singular()
    #     # Replica a matriz de rigidez da estrutura
    #     self.KGS = self.KGS_Singular.copy()
    #     # Aplica as rigidezes dos apoios flexíveis
    #     for i, node in enumerate(self.nodes):                       # Percorre o nó
    #         if node.flagRestrictions == True:
    #             contFlex = 0
    #             for j in range(self.GLpE):                              # Percorre os graus de liberdade dos nós
    #                 if node.typeRestrictions[j] == "flexible":          # Verifica a existência de apoios flexíveis
    #                     self.KGS[self.GLpE*i+j, self.GLpE*i+j] += node.flexibleSupports[contFlex]   # Adiciona a rigidez do apoio flexível
    #                     contFlex += 1
    
    
    def defineGlobalForces(self):
        """
        Define o vetor de forças nodais global
        """
        # Cria o vetor de forças nodais global
        self.GForcesV = np.zeros(self.nGL)
        # Percorre os nós da estrutura
        for i, node in enumerate(self.nodes):
            if node.nodalLoads != None:
                for j in range(self.GLpE):
                    self.GForcesV[self.GLpE*i+j] = node.nodalLoads[j]    # Atribui a ação nodal

    def calcStruture(self):
        """
        Calcula a estrutura definindo a matriz de rigidez global da estrutura e o vetor de ações nodais aplicados nas condições de contorno e utilizando o método das penalidades
        """
        # Replica a matriz de rigidez da estrutura
        self.KGS_CC = self.KGS_Singular.copy()

        # Replica o vetor de forças nodais da estrutura
        self.GForcesV_CC = self.GForcesV.copy()

        # Aplica as condições de contorno
        for i, node in enumerate(self.nodes):                                               # Percorre os nós
            if node.flagRestrictions == True:                                                     # Verifica se há restrições
                for j in range(self.GLpE):                                                  # Percorre os Graus de Liberdade do nó 
                    contPresc = 0;  contFlex = 0                                            # Contadores de prescrições de nós e apoios flexíveis
                    if node.restrictions[j] == 1:                                           # Se houver apoio no grau de liberdade 
                        # Modifica o vetor de forças globais segundo as restrições
                        # Verifica se o nó é fixo
                        if node.typeRestrictions[j] == "fix":                                   
                            self.KGS_CC[self.GLpE*i+j, :] = 0                                   # Zera a linha da KGS
                            self.KGS_CC[:, self.GLpE*i+j] = 0                                   # Zera a coluna da KGS
                            self.KGS_CC[self.GLpE*i+j, self.GLpE*i+j] = 1                       # Torna unitário o elemento da diagonal principal da KGS
                            self.GForcesV_CC[self.GLpE*i+j] = 0                                 # Zera a força no GL (deslocamento nulo)
                        
                        # Verifica se o nó é prescrito
                        elif node.typeRestrictions[j] == "prescrible":  
                            self.KGS_CC[self.GLpE*i+j, :] = 0                                   # Zera a linha da KGS
                            self.KGS_CC[self.GLpE*i+j, self.GLpE*i+j] = 1                       # Torna unitário o elemento da diagonal principal da KGS                        
                            self.GForcesV_CC[self.GLpE*i+j] = node.prescDisp[contPresc]         # aplica o deslocamento prescrito
                            contPresc += 1

                        # Verifica se o nó é flexivel
                        elif node.typeRestrictions[j] == "flexible": 
                            self.KGS_CC[self.GLpE*i+j, self.GLpE*i+j] += node.flexibleSupports[contFlex]   # Adiciona a rigidez da mola no elemento da diagonal principal                        
                            self.GForcesV_CC[self.GLpE*i+j] = self.GForcesV[self.GLpE*i+j]                 # Define a ação nodal aplicada ao nó (mantém a aplicada e remove a componente da mola)
                            contPresc += 1

        
        # Resolve a estrutura
        self.nodalDisp = np.linalg.solve(self.KGS_CC,self.GForcesV_CC)

    def calcEIS(self):
        """
        Calcula os esforços internos solicitantes
        """
        for element in self.elements:
            element.calcInternalForces(self.nodalDisp)

    def calcReactions(self):
        """
        Calcula as forças globais nodais da estrutura e reações de apoio da estrutura
        """
        # Cria o vetor de forças nodais global
        self.GlobalForces = np.zeros(self.nGL)
 
        # Calcula as forças internas dos elementos nas coordenadas globais

        # calcula as forças globais aplicadas
        for i, element in enumerate(self.elements):
            self.elements[i].calcLocalnGlobalForces()
            self.GlobalForces += self.elements[i].globalForces

        # especifica a reação de apoio em cada GL
        for i, node in enumerate(self.nodes):
            if node.restrictions != []:
                self.nodes[i].ReactForces = np.zeros(self.GLpE)
                for j in range(self.GLpE):
                    if node.restrictions[j] == 1:
                        if self.nodes[i].nodalLoads != None:
                            self.nodes[i].ReactForces[j] = self.GlobalForces[self.GLpE*i+j] - self.nodes[i].nodalLoads[j]
                        else:
                            self.nodes[i].ReactForces[j] = self.GlobalForces[self.GLpE*i+j]

    def solveStructure(self):
        """
        Resolve a estrutura calculando os deslocamentos
        """
        # Calcula a matriz de rigidez global da estrutura
        self.calculateKGS_Singular()

        # Calcula o vetor de ações nodais da estrutura
        self.defineGlobalForces()

        # Resolve a estrutura (calcula os deslocamentos nos Graus de Liberdade)
        self.calcStruture()

        # Calcula os esforços internos solicitantes dos elementos
        self.calcEIS()

        # Calcula as reações de apoio
        self.calcReactions()
    

    def displayMatriz(self, matriz):
        # Exibindo a matriz com formatação personalizada
        for linha in matriz:
            for elemento in linha:
                print(f"{elemento:>4}", end=" ")

    def displayVetor(self, vetor):
        # Exibindo a matriz com formatação personalizada
        for elemento in vetor:
            print(f"{elemento:>4}", end=" ")

    def displayResults(self):
        """
        Apresenta resumidamente os resultados
        """
        # Apresenta a matriz de rigidez da estrutura sem as condições de contorno
        print("\n\nMatriz de Rigidez Global da Estrutura (antes das CC):")
        self.displayMatriz(self.KGS)
        
        # Apresenta os vetores de forças nodais sem as condições de contorno
        print("\n\n\nVetor de forças nodais (antes das CC):")
        self.displayVetor(self.GForcesV)

        # Apresenta a matriz de rigidez da estrutura com as condições de contorno
        print("\n\nMatriz de Rigidez Global da Estrutura (com as CC):")
        self.displayMatriz(self.KGS_CC)

        # Apresenta os vetores de forças nodais com as condições de contorno
        print("\n\nVetor de forças nodais (com as CC):")
        self.displayVetor(self.GForcesV_CC)
    
        # Apresenta os vetores de deslocamentos nodais
        print("\n\nDeslocamentos nodais:\n")
        self.displayVetor(self.nodalDisp)
    
    def outputResults(self):
        """
        Cria o dicionário de saída com os resultados da estrutura
        """
        # Cria o dicionário de saída
        self.output = {}

        # Adiciona as matrizes e vetores do problema
        self.output["KGS"] = self.KGS_Singular.tolist()                   # Matriz de rigidez global da estrutura
        self.output["KGS_CC"] = self.KGS_CC.tolist()             # Matriz de rigidez global da estrutura aplicada às CC
        self.output["GForcesV"] = self.GForcesV.tolist()         # Vetor de forças globais da estrutura
        self.output["GForcesV_CC"] = self.GForcesV_CC.tolist()   # Vetor de forças globais da estrutura aplicado às CC

        # Adiciona os deslocamentos nodais
        self.output["NodalDisplacements"] = self.nodalDisp.tolist() # Deslocamentos nodais nas referências globais

        # Adiciona os elementos
        self.output["Elements"] = []
        for elemento in self.elements:
            self.output["Elements"].append({"id": elemento.id, "Normal [kN]": elemento.internalForcesRef[0].tolist()})

        # Adiciona as reações de apoio
        self.output["Reactions"] = []
        for node in self.nodes:
            if node.restrictions != []:
                self.output["Reactions"].append({"id": node.id, "Reactions": node.ReactForces.tolist()})

        return self.output


class SAG:
    """
    Gerencia a análise estrutural do modelo de entrada
    """
    def __init__(self, dir: str):
        self.dir = dir
        self.data = DataReader.ReadData(dir)

        if self.data is None:
            del self
        
        self.type = self.data["typeStructure"]
        self.definetype()
    
    def definetype(self):
        """
        Define o tipo de estrutura a ser analisada
        """
        if self.type == "Truss2D":
            self.Structure = Truss2D(self.data)

    def solveStructure(self):
        """
        Resolve a estrutura
        """
        self.Structure.solveStructure()

    def displayResults(self):
        """
        Plota os resultados
        """
        self.Structure.displayResults()

    def outputResults(self):
        """
        Cria o arquivo de saída em JSON
        """
        # Cria o dicionário com a saída de dados
        output = self.Structure.outputResults()

        # Cria o diretório do novo arquivo
        dirPaste = os.path.splitext(self.dir)[0]
        os.makedirs(dirPaste, exist_ok = True)
        dirOut = dirPaste + '\\results' + os.path.splitext(self.dir)[1]
        
        # Escreve o arquivo JSON
        DataReader.WriteData(dirOut, output)

        # Plotagem
        plotStructure(dirPaste, self.Structure)



# caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Examples', 'Truss01.json')  # os.getcwd()
