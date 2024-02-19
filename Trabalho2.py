import cv2
import math
import csv

#Rotaciona a imagem através de uma linha encontrada na parte de baixo do gabarito
def Rotacionar(prova):
    x = prova.shape[0]-1

    y1 = int(prova.shape[1]/8)
    y2 = int(prova.shape[1]*7/8)

    altura1 = 0
    altura2 = 0

    while x > 0:
        if prova[x][y1][0] < 80 and altura1 == 0:
            altura1 = x
            prova[x][y1] = [0,255,0]
            if altura2 != 0: break

        if prova[x][y2][0] < 80 and altura2 == 0:
            altura2 = x
            prova[x][y2] = [0,255,0]
            if altura1 != 0: break

        x -= 1

    angulo = (altura1-altura2)/int(prova.shape[1]*6/8)

    return cv2.warpAffine(prova, cv2.getRotationMatrix2D((altura1, y1), -math.atan(angulo)*180/math.pi, 1.0), prova.shape[1::-1],  flags=cv2.INTER_LINEAR)


#Recorta a imagem a partir das linhas (baixo e esqueda) que formam o quadrado das questões
def Recortar(prova):
    x = int(prova.shape[0]/2)
    y = 0

    travaSegura = 0

    if prova[x][y][0] < 150:
        travaSegura = 1 

    while 1:
        if travaSegura and prova[x][y][0] > 150:
            travaSegura = 0
        
        if travaSegura == 0 and prova[x][y][0] < 150:
            lateral = y
            break

        y += 1

    #print(lateral)

    x = prova.shape[0]-1
    y = int(prova.shape[1]/2)

    travaSegura = 0

    if prova[x][y][0] < 150:
        travaSegura = 1 

    while 1:
        if travaSegura and prova[x][y][0] > 150:
            travaSegura = 0
        
        if travaSegura == 0 and prova[x][y][0] < 150:
            altura = x
            break

        x -= 1

    #print(altura)

    return prova[0:altura, lateral:prova.shape[1]]

#Calcula a quantidade de luminosidade média de uma área e verifica se está dentro do escolhido (<150)
def VerificarCirculo(prova, posicao, tamanho):
    x = 0
    total = 0

    while x < tamanho:
        y = 0
        while y < tamanho:
            if (prova.shape[0]-posicao[0]+x) >= prova.shape[0]:
                break
            total += prova[prova.shape[0]-posicao[0]+x][posicao[1]+y][2]
            prova[prova.shape[0]-posicao[0]+x][posicao[1]+y] = [0,255,0]
            y += 1
        x += 1

    #print(total/(tamanho*tamanho))

    if total/(tamanho*tamanho) < 150:
        return 1
    return 0

#verifica qual resposta está marcada na caixa de respostas
def VerificarResposta(prova, posicao, tamanhoCirculo, respostaFinal, pulo, aceitarZero=1):

    #Comportamento da variavel "resposta"
    #0 = Sem resposta
    #1 = A
    #2 = B
    #3 = C
    #4 = D
    #5 = E
    #-1 = Duas marcadas

    y = 0

    while y < totalQuestoes:

        resposta = 0

        x = 0
        while x < numeroOpcoes:
            if VerificarCirculo(prova, [int(posicao[0]-(y*pulo[0])),posicao[1]+(x*pulo[1])], tamanhoCirculo):
                if resposta != 0:
                    resposta = -1
                    break

                resposta = x+1

            x += 1
        
        if aceitarZero == 0 and resposta == 0: break
        respostaFinal.append(resposta)
        
        y += 1

    return respostaFinal

def ResultadoAluno(gabarito, respostaAluno):
    acerto = 0
    erros = []

    for x in range(len(gabarito)):
        if gabarito[x] == respostaAluno[x]:
            acerto += 1
        else:
            erros.append(x)

    #print(acerto, round((acerto/len(gabarito))*100,2), erros)
    return (acerto, round((acerto/len(gabarito))*100,2), erros)



caminhoAluno = "./gabarito alunos/scan"
tipo = ".jpg"
numero = ["0000", "0001", "0002", "0003", "0004", "0005", "0006", "0007", "0008", "0009", "0010", "0011", "0012", "0013", "0014", "0015", "0016", "0017", "0018"]
TipoProvaPos = [[1076,41], [1076,282], [1076,517], [1076, 760], [1076, 1000]]
TipoProva = [0,0,0,0,0]

posicaoQuestoes = [[868, 128], [868,420], [868, 710]]
tamanhoCirculoTipo = 24
tamanhoCirculoQuestoes = 30

numeroOpcoes = 5

totalQuestoes = 25

caminhoGabarito = "./gabaritoCorretoJpg/"
nomeGabarito = ["A", "B", "C", "D", "E"]
posicaoQuestoesGabarito = [[923,148], [923, 460], [923, 770]]
tamanhoCirculoQuestoesGabarito = 14

respostaGabarito = []

input("Pressione Enter para começar...")

arquivoCsv = csv.writer(open("./notas/ResultadosDosAlunos.csv", 'w', newline=''))
arquivoCsv.writerow(["Aluno", "Acertos", "% Acerto", "Questoes Erradas"])

for a in range(len(nomeGabarito)):
    gabarito = cv2.imread(caminhoGabarito+nomeGabarito[a]+tipo)
    gabarito = Recortar(gabarito)

    respostaAuxiliar = []
    for x in range(len(posicaoQuestoes)):
        respostaAuxiliar = VerificarResposta(gabarito, posicaoQuestoesGabarito[x], tamanhoCirculoQuestoesGabarito, respostaAuxiliar, [37.4,32], 0)

    respostaGabarito.append(respostaAuxiliar)

    cv2.imwrite("./processados/"+nomeGabarito[a]+tipo, gabarito)

#print(respostaGabarito)


for n in range(len(numero)):
    provaAluno = cv2.imread(caminhoAluno+numero[n]+tipo)


    provaAluno = Rotacionar(provaAluno)

    provaAluno = Recortar(provaAluno)

    for x in range(len(TipoProvaPos)):
        TipoProva[x] = VerificarCirculo(provaAluno, TipoProvaPos[x], tamanhoCirculoTipo)
    
    #print(TipoProva)

    respostaAluno = []
    for x in range(len(posicaoQuestoes)):
        respostaAluno = VerificarResposta(provaAluno, posicaoQuestoes[x], tamanhoCirculoQuestoes, respostaAluno, [34.8,tamanhoCirculoQuestoes])
    
    #print(respostaAluno)

    for x in range(5):
        if TipoProva[x]: 
            arquivoCsv.writerow([numero[n], * ResultadoAluno(respostaGabarito[x], respostaAluno)])
            break


    cv2.imwrite("./processados/"+numero[n]+tipo, provaAluno)
