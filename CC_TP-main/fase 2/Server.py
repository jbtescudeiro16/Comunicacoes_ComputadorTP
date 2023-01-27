import random
import socket
from parseDB import *
from parseConfig import *
from parseFstMsg import *
import sys
import threading

def UDP_Querie(UDPServerSocket,bufferSize,c,bancodeDados, escolhaDebug,bytesAddressPair):

    # Separa a mensagem do cliente
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]


    responseIP = bytesAddressPair[1][0]
    responseAddress = (responseIP, 5555)

    clientMsg = "{}".format(message)


    # Parse da mensagem do cliente
    clientQuery = FstMsg()

    # caso onde o response code é 3
    if clientQuery.fillSP(clientMsg) == False:
        clQuerieError = FstMsg()
        clQuerieError.setmessageID(random.randint(1, 65535))
        clQuerieError.setflags("")
        clQuerieError.setresponseCode(3)
        clQuerieError.set_nr_of_values(0)
        clQuerieError.set_nr_of_authorities(0)
        clQuerieError.set_nr_of_extra_values(0)
        clQuerieError.setquerieName("")
        clQuerieError.setquerieType("Error decode message")
        clQuerieError.setresponseValues("")
        clQuerieError.setauthoritiesValues("")
        clQuerieError.setextra_values("")

        msgFromServer = clQuerieError.buildmsg2()
        bytesToSend = str.encode(msgFromServer)
        UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        UDPResponseSocket.sendto(bytesToSend, responseAddress)
        logER(c.getLGdom(),responseAddress ,"Error decoding message", escolhaDebug)
        socket.close

    dominio = bancodeDados.getDomain()

    # Resposta à query "A"
    if ((clientQuery.getquerieType() == "A") | (clientQuery.getquerieType() == "a")):
        flag = 0
        flagDominio = 0
        queryIP = ""
        ttl = ""


        #bancodeDados.print()
        for x in bancodeDados.get_responseValues("A"):

            #print("x=",x)
            x = x.split(" ")
            #print("x[0]:",x[0])

            #print("dominio:",dominio)
            #print("queryname=",clientQuery.getquerieName())
            #if (x[0] == clientQuery.getquerieName()):
            if (clientQuery.getquerieName() in x[0]):
                clientQuery.setresponseValues(x[2])
                clientQuery.set_nr_of_values(1)
                clientQuery.setflags("")
                clientQuery.setresponseCode(0)
                queryIP = x[2]
                ttl = x[3]

                flag = 1    # Flag = 1, match direto com a query.
                break
                
                #bancodeDados.print()

        dominioQueryList=clientQuery.getquerieName().split(".")
        dominioQueryList.pop(0)          

        separator = "."
        dominioQuery = separator.join(dominioQueryList)

        if(dominioQuery == dominio):
            flagDominio = 1

        if (flag == 0) & (flagDominio == 0):
            dominioList=clientQuery.getquerieName().split(".")
            #print("dominioList:",dominioList)
            dominioList.pop(0)          
            i = len(dominioList)-1
            
            separator = "."
            dominio = separator.join(dominioList)
            #print("dominio:",dominio)


            while( (i>0) & (flag == 0) & (flagDominio == 0)):
                    #print("dominio:",dominio)
                    #print("dominioList:",dominioList)
                    for x in bancodeDados.get_responseValues("A"):
                        #print("x:",x)
                        if dominio in x:
                            #print("x=",x)
                            x = x.split(" ")
                            flag = 2    #Flag = 2, encontrei subdominios.
                            clientQuery.setresponseValues(x[2])
                            clientQuery.set_nr_of_values(1)

                            arrayExtraValues = bancodeDados.getarrayExtravalues2()
                            clientQuery.setflags("")
                            clientQuery.setresponseCode("")

                            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
                            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

                            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
                            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

                            break

                    dominioList.pop(0)
                    dominio = separator.join(dominioList)
                    i = i-1

        if (flag == 0) & (flagDominio == 1):
            flag = 3    #Flag = 3, estou no ultimo dominio. Parar recursividade.

            clientQuery.setresponseValues("")
            clientQuery.set_nr_of_values(0)

            arrayExtraValues = bancodeDados.getarrayExtravalues2()
            clientQuery.setflags("")
            clientQuery.setresponseCode(0)

            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))


        if (flag == 0):
            arrayExtraValues = bancodeDados.getarrayExtravalues2()

            clientQuery.setflags("")
            clientQuery.setresponseCode(2)
            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

            msgFromServer = clientQuery.buildmsg2()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logER(c.getLGdom(), responseAddress, "NAME doesn't exist", escolhaDebug)
            socket.close
        else:

            if flagDominio:
                clientQuery.setresponseValues(queryIP+" "+ttl)

            # preenche com a mensagem do Servidor ,cria o Socket e envia para o respetivo endereço
            msgFromServer = clientQuery.buildmsg3()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
            socket.close
    
    # Se não for querie A:
    elif (dominio == clientQuery.getquerieName() or clientQuery.getquerieType()=="PTR"):

        # caso onde o response code é 0
        if (len(bancodeDados.get_responseValues(clientQuery.getquerieType())) > 0):

            arrayExtraValues = bancodeDados.getarrayExtravalues(clientQuery.getquerieType())

            # preenche com a resposta do servidor os diferentes campos

            clientQuery.setresponseValues(bancodeDados.get_responseValues(clientQuery.getquerieType()))
            clientQuery.set_nr_of_values(len(clientQuery.getresponseValues()))
            clientQuery.setflags("")
            clientQuery.setresponseCode(0)

            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

            # preenche com a mensagem do Servidor ,cria o Socket e envia para o respetivo endereço
            msgFromServer = clientQuery.buildmsg2()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
            socket.close

        # caso onde o response code é 1
        else:
            arrayExtraValues = bancodeDados.getarrayExtravalues2()

            clientQuery.setflags("")
            clientQuery.setresponseCode(1)
            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

            msgFromServer = clientQuery.buildmsg2()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logER(c.getLGdom(), responseAddress, "NAME exists but not found any value with the current TYPE OF VALUE", escolhaDebug)
            socket.close

    # Se não estiver no dominio correto, enviar o IP do dominio em questao
    else:
        flag = 0
        for x in bancodeDados.get_responseValues("A"):
            #print("x:",x)
            if clientQuery.getquerieName() in x:
                x = x.split(" ")
                flag = 2    #Flag = 2, encontrei subdominios.
                clientQuery.setresponseValues(x[2])
                clientQuery.set_nr_of_values(1)

                arrayExtraValues = bancodeDados.getarrayExtravalues2()
                clientQuery.setflags("")
                clientQuery.setresponseCode("")

                clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
                clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

                clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
                clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

                break

        if(flag == 0):
            # nao encontrou informacao, dominio nao existe
            arrayExtraValues = bancodeDados.getarrayExtravalues2()

            clientQuery.setflags("")
            clientQuery.setresponseCode(2)
            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

            msgFromServer = clientQuery.buildmsg2()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logER(c.getLGdom(), responseAddress, "NAME doesn't exist", escolhaDebug)
            socket.close
        else:
            # preenche com a mensagem do Servidor ,cria o Socket e envia para o respetivo endereço
            msgFromServer = clientQuery.buildmsg3()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
            socket.close




def TCP_Querie(buffer, bancodeDados, escolhaDebug, c, client, address):
    received_msg = FstMsg()
    received_msg.fillSP(buffer)

    # trata a mensagem recebida caso seja pedido a versão da base de dados
    if received_msg.getquerieName() == "SOASERIAL?":
        soaSerial = bancodeDados.ProcTipo("SOASERIAL")
        dominio = ""  # apaga a flag dominio
        received_msg.setflags("")
        received_msg.setquerieName("")
        received_msg.setquerieType("")
        received_msg.setresponseValues(soaSerial)
        mensagem2 = received_msg.buildmsg()
        client.send(bytes(mensagem2, "utf-8"))

    # caso o SS envie a mensagem com o domínio a validar
    dominio = c.get_dominio()
    if received_msg.getquerieName() == "Dominio":

        # Se o dominio da mensagem do SS for igual ao do SP
        if dominio == received_msg.getquerieType():
            received_msg.setflags("")
            received_msg.setquerieName("")
            received_msg.setquerieType("")
            received_msg.setresponseValues(bancodeDados.nr_linhas())
            # print("nrlinhas:" + str(received_msg.getresponseValues()))
            mensagem2 = received_msg.buildmsg()
            client.send(bytes(mensagem2, "utf-8"))
        # Se o dominio da mensagem do SS for diferente do do SP
        else:
            dominio = ""
            mensagem2 = "Dominio Invalido"
            client.send(bytes(mensagem2, "utf-8"))
            print("Dominio Invalido")
            logEZ(c.getLGdom(), address, "SP", escolhaDebug)
    # Se a mensagem for a solicitar o número de linahs
    if received_msg.getquerieName() == "nrLinhas":
        if dominio.__len__() > 0:  # verifica se a msg para autorizaçao ja foi validada
            received_msg.setflags("")
            received_msg.setquerieName("")
            received_msg.setquerieType("")
            arrayValues = []
            for i in bancodeDados.lista:
                arrayValues.append(i)
            for i in bancodeDados.listausers:
                arrayValues.append(i)
            for i in bancodeDados.listaCname:
                arrayValues.append(i)
            i = 0
            while i < bancodeDados.nr_linhas():
                received_msg.setresponseValues(str(i) + ";" + str(arrayValues[i]))
                mensagem2 = received_msg.buildmsg() + "\n"
                client.send(bytes(str(mensagem2), "utf-8"))
                i += 1
            logZT(c.getLGdom(), address, "SP", escolhaDebug)
        else:
            print("Dominio ainda nao foi validado")
            mensagem = "Dominio nao validado" + "\n"
            client.send(bytes(str(mensagem), "utf-8"))
            logEZ(c.getLGdom(), address, "SP", escolhaDebug)



#Funçao que trata da conexão UDP entre Cliente e servidor.
def UDP_Connection(bancodeDados, escolhaDebug, c, UDPServerSocket , bufferSize):
    while True:

        print("UDP server up and listening")
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize) #faz com que a função fique á espera de um pedido para criar uma thread

        thread = threading.Thread(target=UDP_Querie, args=(UDPServerSocket, bufferSize, c, bancodeDados, escolhaDebug, bytesAddressPair))
        thread.start()



#Funçao que trata da conexão TCP entre Servidores:SP e SS.
def TCP_Connection(server,bancodeDados, escolhaDebug,c):
    while True:

        print("TCP server up and listening")

        client, address = server.accept()

        # recebe a mensagem do servidor
        buffer = client.recv(1024)
        buffer = buffer.decode("utf-8")

        # imprime e faz o parse  a mensagem recebida
        print("Mensagem Recebida: " + buffer)
        print("----------------------")

        thread = threading.Thread(target=TCP_Querie, args=(buffer, bancodeDados, escolhaDebug, c, client, address))
        thread.start()




def main():

    debugFlag = 0
    escolhaDebug = ""

    while(debugFlag == 0):

        escolhaDebug = input("Modo debug? (S/N)")

        print("escolha:",escolhaDebug)
        if(escolhaDebug != "S" and escolhaDebug != "s" and escolhaDebug != "N" and escolhaDebug != "n"):
            print("Resposta inválida. Escolha Sim (S) para executar em modo debug ou Não (N) para executar em modo normal.")
        else:
            debugFlag = 1

    config_path = sys.argv[1]
    c = ConfigValues()
    c.preenche(config_path)
    print("----------------------")
    print("Configs Carregados")
    print(c.getLGdom())
    logEV(c.getLGdom(), "conf-file-read", config_path, escolhaDebug)

    bd = c.getDB()
    bancodeDados=DataBase()
    bancodeDados.preenche(bd)
    print("Base de Dados Carregada")
    print("----------------------")
    logEV(c.getLGdom(), "db-file-read", bd, escolhaDebug)

    #bancodeDados.print()


    #Qual o ip e a porta do servidor
    ip_Porta = c.getIp_Porta()
    arr_aux = str(ip_Porta).split(":")

    localIP = arr_aux[0]
    print("IP: "+localIP)

    localPort = int(arr_aux[1])
    print("Porta: "+str(localPort))

    print("----------------------")

    serverTimeout = 2000 # mudar mais tarde caso necessário
    if(escolhaDebug == "S" or escolhaDebug == "s"):
        logST(c.getLGdom(), localPort, serverTimeout, "debug", escolhaDebug)
    else:
        logST(c.getLGdom(), localPort, serverTimeout, "normal", escolhaDebug)
        

    #TCP connection
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((localIP, localPort))
    server.listen(10)# nr de ligaçoes simultaneas ao servidor

    #TCP connection
    threadTCP = threading.Thread(target=TCP_Connection, args=(server, bancodeDados, escolhaDebug, c, ))

    #UDP connection

    bufferSize = 1024
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    threadUDP = threading.Thread(target=UDP_Connection, args=(bancodeDados, escolhaDebug, c, UDPServerSocket, bufferSize))


    threadTCP.start()
    threadUDP.start()

    logSP(c.getLGdom(), "Server closed connection", escolhaDebug)



if __name__ == "__main__":
    main()


