import sys
from SAG import SAG


if __name__ == '__main__':
    while(True):
        print("Insira o diretório do arquivo em extensão JSON:")
        caminho_arquivo = input()

        Structure = SAG(caminho_arquivo)    # Entra com o arquivo para o gerenciador de análises
        Structure.solveStructure()          # Resolve a estrutura
        # Structure.displayResults()          # Apresenta os resultados na linha de comando
        Structure.outputResults()           # Gera os arquivos de saída
        try:

            print("\nEstrutura analisada com sucesso! Deseja realizar uma nova análise? (Sim -> S / N -> qualquer tecla)")
        except:
            print("\nDeseja inserir um novo arquivo? (Sim -> S / N -> qualquer tecla)")
        tecla = input("Tecla de entrada: ")
        if tecla == "S" or tecla == "s":
            print("\n")
            continue
        else:
            print("\nFechando o programa!")
            break
    
