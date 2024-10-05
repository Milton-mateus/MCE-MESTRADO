import json
import os
import time

def ReadData(dir: str):
    """
    Lê um arquivo JSON e retorna os dados como um objeto Python.

    :param dir: Caminho para o arquivo JSON.
    :return: Dados do arquivo JSON como um dicionário ou lista.
    """
    # Read data from a file
    try:
        try:
            with open(dir, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            with open((os.path.join(os.path.dirname(os.path.abspath(__file__)), dir)), 'r') as file:
                data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Erro: o arquivo '{dir}' não foi encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: o arquivo '{dir}' não possui extensão JSON válida.")
    except Exception as e:
        print(f"Erro: {e}")
        return None

def WriteData(dirOut: str, output: dict):
    """
    Cria o arquivo de saída de dados
    """
    with open(dirOut, 'w') as outfile:
        json.dump(output, outfile, indent=4)
