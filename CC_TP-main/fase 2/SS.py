import random
import socket
import sys
import time
import threading

from parseConfig import *
from parseDB import *
from datetime import datetime
from parseSSMsg import *
from parseFstMsg import *

def transfZona (ip_SP, porta_SP, escolhaDebug, c):
    while True:
        bancodeDados = DataBase()
        bd = c.getDB()
        bancodeDados.preenche(bd)
        flag=0
        bEnd=0
        # Criaçao do socket

        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.settimeout(5)
            server.connect((ip_SP, porta_SP))


            # Pergunta qual a versão da BD atual do SP
            message_send = SSMSG()
            message_send.setmessageID(random.randint(1, 65535))
            message_send.setflags("Q")
            message_send.setresponseCode(0)
            message_send.set_nr_of_values(0)
            message_send.set_nr_of_extra_values(0)
            message_send.set_nr_of_authorities(0)
            message_send.setquerieName("SOASERIAL?")
            message_send.setquerieType("")
            message_send.setrecursivo("")
            message = message_send.build_message()
            server.send(bytes(message, "utf-8"))
            bRetry = 0
        except:
            print("Connection with SP fail")
            flag = 1

        if not flag:
            # Recebe resposta com a versao da BD
            try:
                buffer = server.recv(1024)
                buffer = buffer.decode("utf-8")

                # Parse da mensagem recebida
                mensagem_do_SP = FstMsg()
                mensagem_do_SP.fillSS(buffer)

                # Envia o domínio para o qual pertende obter a BD
                if int(bancodeDados.ProcTipo("SOASERIAL")) < int(mensagem_do_SP.getresponseValues()):
                    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server.settimeout(5)
                    server.connect((ip_SP, porta_SP))

                    message_send2 = SSMSG()
                    message_send2.setmessageID(random.randint(1, 65535))
                    message_send2.setflags("Q")
                    message_send2.setresponseCode(0)
                    message_send2.set_nr_of_values(0)
                    message_send2.set_nr_of_extra_values(0)
                    message_send2.set_nr_of_authorities(0)
                    message_send2.setquerieName("Dominio")
                    message_send2.setquerieType(c.get_dominio())
                    message_send2.setrecursivo("")
                    message = message_send2.build_message()
                    server.send(bytes(message, "utf-8"))
                else:
                    print("A versão da BD já é a mais atual")
                    bRetry = 1
            except socket.timeout:
                print("DB version not received")

            # Recebe a resposta com o nr de linhas da BD
            if not bRetry:
                try:
                    buffer = server.recv(1024)
                    buffer = buffer.decode("utf-8")

                    if buffer != "Dominio Invalido":
                        mensagem_do_SP2 = FstMsg()
                        mensagem_do_SP2.fillSS(buffer)
                        nr_de_linhas = int(mensagem_do_SP2.getresponseValues())
                        print("nr de linhas:" + str(nr_de_linhas))
                        # Envia o nr de linhas de volta se verificar as condições
                        if nr_de_linhas < 65535:
                            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            server.settimeout(5)
                            server.connect((ip_SP, porta_SP))

                            message_send3 = SSMSG()
                            message_send3.setmessageID(random.randint(1, 65535))
                            message_send3.setflags("Q")
                            message_send3.setresponseCode(0)
                            message_send3.set_nr_of_values(0)
                            message_send3.set_nr_of_extra_values(0)
                            message_send3.set_nr_of_authorities(0)
                            message_send3.setquerieName("nrLinhas")
                            message_send3.setquerieType(nr_de_linhas)
                            message_send3.setrecursivo("")
                            message = message_send3.build_message()
                            server.send(bytes(message, "utf-8"))
                        else:
                            print("Nr de linhas inválido")
                            bRetry = 1
                    else:
                        print("Dominio Invalido")
                        logEZ(c.getLGdom(), ip_SP, "SS", escolhaDebug)

                        bRetry = 1
                except socket.timeout:
                    print("Nr of lines DB not received")

            # recebe as linhas da BD
            timeout = 20  # timeout é o tempo maximo para receber as N linhas do SP
            dtStart = datetime.now()
            bTimeout = False
            bEnd = False
            nLinhas = 0
            recursivo = ""

            if not bRetry:
                while not bTimeout and not bEnd:
                    try:
                        line = server.makefile()
                        newBDArr = []
                        for i in range(0, nr_de_linhas):
                            msg = line.readline()
                            if (msg != "Dominio nao validado"):
                                array_MSG = msg.split(";")
                                header_fields_arr = array_MSG[0]
                                querie_info_arr = array_MSG[1]
                                lines_resposta = array_MSG[2]
                                data_fields_arr = array_MSG[3]

                                header_fields = header_fields_arr.split(",")
                                querie_info = querie_info_arr.split(",")
                                data_fields = data_fields_arr.split(",")

                                messageID = header_fields[0]
                                flags = header_fields[1]
                                responseCode = header_fields[2]
                                nr_of_values = header_fields[3]
                                nr_of_authorities = header_fields[4]
                                nr_of_extra_values = header_fields[5]
                                querieName = querie_info[0]
                                querie_type = querie_info[1]
                                lines = lines_resposta
                                respondeValues = data_fields[0]
                                authoritiesValues = data_fields[1]
                                extra_values = data_fields[2]

                                newBDArr.append(respondeValues + "\n")

                                nLinhas += 1
                            else:
                                print("Dominio nao foi validado")
                                logEZ(c.getLGdom(), ip_SP, "SS", escolhaDebug)
                                break

                        if nLinhas >= nr_de_linhas:
                            bEnd = True
                            print("Recebi as linhas da BD e vou atualizar")
                            logZT(c.getLGdom(), ip_SP, "SS", escolhaDebug)


                    except socket.timeout:
                        dtNow = datetime.now()
                        diferenca = dtNow - dtStart
                        if (diferenca.seconds >= timeout):
                            bTimeout = True

            # Fecha o Socket
            server.close()

            lock = threading.Lock()

        # Atualiza a BD
        if bEnd and not flag:

            lock.acquire()
            deleteData = open(c.getDB(), 'w')
            deleteData.close()
            f = open(c.getDB(), "a")
            for i in newBDArr:
                f.write(i)
            f.close()
            lock.release()

            time.sleep(int(bancodeDados.ProcTipo("SOAREFRESH")))
        else:
            time.sleep(int(bancodeDados.ProcTipo("SOARETRY")))
            logER(c.getLGdom(), "db-file-updated", c.getDB(), escolhaDebug)


def UDP_Querie(UDPServerSocket, bufferSize, c, bancodeDados, escolhaDebug, bytesAddressPair):
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
        logER(c.getLGdom(), responseAddress, "Error decoding message", escolhaDebug)
        socket.close

    dominio = bancodeDados.getDomain()

    # Resposta à query "A"
    if ((clientQuery.getquerieType() == "A") | (clientQuery.getquerieType() == "a")):
        flag = 0
        flagDominio = 0
        queryIP = ""
        ttl = ""

        # bancodeDados.print()
        for x in bancodeDados.get_responseValues("A"):

            # print("x=",x)
            x = x.split(" ")
            # print("x[0]:",x[0])

            # print("dominio:",dominio)
            # print("queryname=",clientQuery.getquerieName())
            # if (x[0] == clientQuery.getquerieName()):
            if (clientQuery.getquerieName() in x[0]):
                clientQuery.setresponseValues(x[2])
                clientQuery.set_nr_of_values(1)
                clientQuery.setflags("")
                clientQuery.setresponseCode(0)
                queryIP = x[2]
                ttl = x[3]

                flag = 1  # Flag = 1, match direto com a query.
                break

                # bancodeDados.print()

        dominioQueryList = clientQuery.getquerieName().split(".")
        dominioQueryList.pop(0)

        separator = "."
        dominioQuery = separator.join(dominioQueryList)

        if (dominioQuery == dominio):
            flagDominio = 1

        if (flag == 0) & (flagDominio == 0):
            dominioList = clientQuery.getquerieName().split(".")
            # print("dominioList:",dominioList)
            dominioList.pop(0)
            i = len(dominioList) - 1

            separator = "."
            dominio = separator.join(dominioList)
            # print("dominio:",dominio)

            while ((i > 0) & (flag == 0) & (flagDominio == 0)):
                # print("dominio:",dominio)
                # print("dominioList:",dominioList)
                for x in bancodeDados.get_responseValues("A"):
                    # print("x:",x)
                    if dominio in x:
                        # print("x=",x)
                        x = x.split(" ")
                        flag = 2  # Flag = 2, encontrei subdominios.
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
                i = i - 1

        if (flag == 0) & (flagDominio == 1):
            flag = 3  # Flag = 3, estou no ultimo dominio. Parar recursividade.

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
                clientQuery.setresponseValues(queryIP + " " + ttl)

            # preenche com a mensagem do Servidor ,cria o Socket e envia para o respetivo endereço
            msgFromServer = clientQuery.buildmsg3()
            bytesToSend = str.encode(msgFromServer)
            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
            socket.close

    # Se não for querie A:
    elif (dominio == clientQuery.getquerieName() or clientQuery.getquerieType() == "PTR"):

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
            logER(c.getLGdom(), responseAddress, "NAME exists but not found any value with the current TYPE OF VALUE",
                  escolhaDebug)
            socket.close

    # Se não estiver no dominio correto, enviar o IP do dominio em questao
    else:
        flag = 0
        for x in bancodeDados.get_responseValues("A"):
            # print("x:",x)
            if clientQuery.getquerieName() in x:
                x = x.split(" ")
                flag = 2  # Flag = 2, encontrei subdominios.
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

        if (flag == 0):
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




def UDP_Connection(bancodeDados, escolhaDebug, c, UDPServerSocket , bufferSize):
    while True:

        print("UDP server up and listening")
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize) #faz com que a função fique á espera de um pedido para criar uma thread

        thread = threading.Thread(target=UDP_Querie, args=(UDPServerSocket, bufferSize, c, bancodeDados, escolhaDebug, bytesAddressPair))
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

#Parse do Ficheiro Configs
    config_path = sys.argv[1]
    c = ConfigValues()
    c.preenche(config_path)
    bd = c.getDB()
    bRetry=0
    logEV(c.getLGdom(), "conf-file-read", config_path, escolhaDebug)

#Parse da Base de Dados
    bancodeDados=DataBase()
    bancodeDados.preenche(bd)
    logEV(c.getLGdom(), "db-file-read", bd, escolhaDebug)


#Obter o ip e a porta para qual vai enviar a msg, através do Ficheiro de Configs
    ip_SP = c.getvaluebytipo("SP")[0]
    porta_SP = 5555

    threadTCP = threading.Thread(target=transfZona, args=(ip_SP, porta_SP, escolhaDebug, c))
    threadTCP.start()
    #transfZona(ip_SP,porta_SP,bancodeDados,escolhaDebug,c)


    #Qual o ip e a porta do servidor
    ip_Porta = c.getIp_Porta()
    arr_aux = str(ip_Porta).split(":")

    localIP = arr_aux[0]
    print("IP: "+localIP)

    localPort = int(arr_aux[1])
    print("Porta: "+str(localPort))

    serverTimeout = 2000 # mudar caso necessário
    if(escolhaDebug == "S" or escolhaDebug == "s"):
        logST(c.getLGdom(), localPort, serverTimeout, "debug", escolhaDebug)
    else:
        logST(c.getLGdom(), localPort, serverTimeout, "normal", escolhaDebug)


    bufferSize = 1024
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    threadUDP = threading.Thread(target=UDP_Connection, args=(bancodeDados, escolhaDebug, c, UDPServerSocket, bufferSize))
    threadUDP.start()



if __name__ == "__main__":
    main()