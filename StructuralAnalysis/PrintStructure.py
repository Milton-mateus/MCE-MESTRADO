import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
from Classes import Elem
import os

def plotStructure(dir, Structure):
    # Configuração do gráfico
    fig, ax = plt.subplots()

    # Plotando elementos
    for element in Structure.elements:
        xi = element.initNode.coords[0] 
        yi = element.initNode.coords[1]
        xf = element.finalNode.coords[0]
        yf = element.finalNode.coords[1]
    
        # Criando o gráfico
        plt.plot(np.array([xi,xf]), np.array([yi,yf]), color='blue')
    
    x: list[float] = [];    y: list[float] = []
    for node in Structure.nodes:
        x.append(float(node.coords[0]))
        y.append(float(node.coords[1]))
    ax.scatter(x, y, color='blue', s = 100)  # zorder para garantir que os pontos fiquem sobre os círculos

    # Configurações adicionais do gráfico
    ax.set_title("Estrutura")
    ax.set_xlabel("Eixo X")
    ax.set_ylabel("Eixo Y")
    ax.grid(True)

    # salvando o gráfico
    plt.savefig((dir + '\\Structure.png'), dpi=600)

    # Mantendo o gráfico aberto
    plt.ioff()

    # Exibindo o gráfico
    plt.show()