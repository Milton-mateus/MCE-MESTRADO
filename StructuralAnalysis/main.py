import sys
from SAG import SAG


if __name__ == '__main__':
    while(True):
        print("Insira o diretório do arquivo em extensão JSON:")
        caminho_arquivo = input()

        try:
            Structure = SAG(caminho_arquivo)    # Entra com o arquivo para o gerenciador de análises
            
            # Verificando se a estrutura é hipostática
            if Structure.Structure.verifyRestrictions() == True:
                Structure.solveStructure()          # Resolve a estrutura
                Structure.outputResults()           # Gera os arquivos de saída
                print("\nEstrutura analisada com sucesso!")

            else:
                print("\nNão é possível analisar a estrutura pois esta não é isostática!\n")
        except:
            print("\nErro ao realizar a análise!\n")
            
        print("\nDeseja inserir um novo arquivo? (Sim -> S / Não -> qualquer tecla)")

        tecla = input("Tecla de entrada: ")
        if tecla == "S" or tecla == "s":
            print("\n")
            continue
        else:
            print("\nRecomenda-se fazer a visualização do arquivo de resultados no site:"
                + "\nhttps://jsonviewer.stack.hu/")
            print("\nFechando o programa!")
            break
    
