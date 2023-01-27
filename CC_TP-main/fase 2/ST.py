import random
import socket
from parseDB import *
from parseConfig import *
from parseFstMsg import *
import sys
import threading
import signal
import time

def debugParseConfig(c):
    print("config:\n get_dominio:",c.get_dominio(), 
    "\n get_items:", c.get_items(),
    "\n get_allLg:", c.getallLG(),
    "\n get_db:", c.getDB(),
    "\n get_ipPorta:", c.getIp_Porta(),
    "\n get_Lgdom:", c.getLGdom(),
    "\n get_valuebytipo:", c.getvaluebytipo("SP"))

def debugParseBD(bancodeDados):
    print("base de dados:\n get_authoritiesValues:",bancodeDados.get_authoritiesValues(), 
    "\n get_extraValues:", bancodeDados.get_extraValues(bancodeDados.getarrayExtravalues2()),
    "\n get_responseValues:", bancodeDados.get_responseValues("A"),
    "\n get_getarrayExtravalues:", bancodeDados.getarrayExtravalues("A"),
    "\n get_getarrayExtravalues2:", bancodeDados.getarrayExtravalues2(),
    "\n get_domain:", bancodeDados.getDomain())



#Funçao que trata da conexão UDP entre Cliente e servidor.
def UDP_Connection(localIP,localPort,bancodeDados, escolhaDebug,c):
    while True:

        bufferSize = 1024
        flag = 0
        flagEnvio = 0

        #Criação do Socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Função para fechar socket UDP caso haja um ctrl+c
        def signal_handler(signal, frame):
            # close the socket here
            UDPServerSocket.close()
            print("\nUDP Socket closed!")
            sys.exit(0)
            # END OF PROGRAM !!!
        signal.signal(signal.SIGINT, signal_handler)

        #Bind do ip e porta
        UDPServerSocket.bind((localIP, localPort))
        print("UDP server up and listening")
        
        #Separa a mensagem do cliente 
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0]
        address = bytesAddressPair[1]

        responseIP = bytesAddressPair[1][0]
        responseAddress = (responseIP, 5555)

        clientMsg = "{}".format(message)
        clientIP = "Client IP Address:{}".format(address)
        #print(clientIP)

        #Parse da mensagem do cliente 
        clientQuery=FstMsg()

        dominio = bancodeDados.getDomain()

        #caso onde o response code é 3
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
            time.sleep(0.05)
            UDPServerSocket.sendto(bytesToSend, responseAddress)
            logER(c.getLGdom(), responseAddress, "Error decoding message", escolhaDebug)
            continue

        elif ((clientQuery.getquerieType() == "PTR")):

            clientQuery.setflags("")
            clientQuery.setresponseCode("")

            ipReverse = bancodeDados.ProcTipo2("A", "sp.reverse.Fifa.")
            clientQuery.setresponseValues(ipReverse)

            msgFromServer = clientQuery.buildmsg4()

            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            bytesToSend = str.encode(msgFromServer)
            time.sleep(0.05)#debug
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            socket.close
            continue

        elif((clientQuery.getquerieType() == "A") | (clientQuery.getquerieType() == "a")):
            # Resposta à query "A"
            flag = 0
            flagDominio = 0

            dominioQueryList=clientQuery.getquerieName().split(".")
            dominioQueryList.pop(0)

            separator = "."
            dominioQuery = separator.join(dominioQueryList)

            if(dominioQuery == dominio):
                flagDominio = 1

            for x in bancodeDados.get_responseValues("A"):
                #print("x=",x)
                x = x.split(" ")
                if (x[0] == clientQuery.getquerieName()):
                    #print("entrei")
                    clientQuery.setresponseValues(x[2])
                    clientQuery.set_nr_of_values(1)
                    clientQuery.setflags("")
                    clientQuery.setresponseCode(0)
                    flag = 1
                    break

            #clientQuery.buildmsg()
            if (flag == 0) & (flagDominio == 0):

                dominioList=clientQuery.getquerieName().split(".")
                dominioList.pop(0)
                i = len(dominioList)-1

                separator = "."
                dominio = separator.join(dominioList)

                while( (i>0) & (flag == 0)):
                    #print("dominio:",dominio)
                    #print("dominioList:",dominioList)
                    for x in bancodeDados.get_responseValues("A"):
                        #print("x:",x)
                        if dominio in x:
                            #print("x=",x)
                            x = x.split(" ")
                            flag = 2

                            clientQuery.setresponseValues(x[2])
                            clientQuery.set_nr_of_values(1)

                            arrayExtraValues = bancodeDados.getarrayExtravalues2()
                            clientQuery.setflags("")
                            clientQuery.setresponseCode("")

                            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
                            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

                            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
                            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

                            logER(c.getLGdom(), address, "NAME exists but not found any info", escolhaDebug)
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

            if flag == 0:
                arrayExtraValues = bancodeDados.getarrayExtravalues2()

                clientQuery.setflags("")
                clientQuery.setresponseCode(2)
                clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
                clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

                clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
                clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

                msgFromServer = clientQuery.buildmsg2()
                #print("msg:",msgFromServer)

                UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                bytesToSend = str.encode(msgFromServer)
                time.sleep(0.05)
                UDPResponseSocket.sendto(bytesToSend, responseAddress)
                logER(c.getLGdom(), responseAddress, "NAME doesn't exist", escolhaDebug)
                flagEnvio = 1
            else:

                # preenche com a mensagem do Servidor ,cria o Socket e envia para o respetivo endereço
                msgFromServer = clientQuery.buildmsg3()

                UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                bytesToSend = str.encode(msgFromServer)
                time.sleep(0.05)
                UDPResponseSocket.sendto(bytesToSend, responseAddress)
                logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
                socket.close
                flagEnvio = 1

        elif (dominio == clientQuery.getquerieName()):
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

                UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                bytesToSend = str.encode(msgFromServer)
                time.sleep(0.05)
                UDPResponseSocket.sendto(bytesToSend, responseAddress)
                logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
                socket.close
                flagEnvio = 1

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

                UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                bytesToSend = str.encode(msgFromServer)
                time.sleep(0.05)
                UDPResponseSocket.sendto(bytesToSend, responseAddress)
                logER(c.getLGdom(), responseAddress, "NAME exists but not found any value with the current TYPE OF VALUE", escolhaDebug)
                socket.close
                flagEnvio = 1

        # Se não estiver no dominio correto, enviar o IP do dominio em questao.
        else:
            flag = 0
            dominioList=clientQuery.getquerieName().split(".")
            #dominioList.pop(0)
            i = len(dominioList)-1

            separator = "."
            dominio = separator.join(dominioList)

            while( (i>0) & (flag == 0)):
                #print("dominio:",dominio)
                #print("dominioList:",dominioList)
                for x in bancodeDados.get_responseValues("A"):
                    #print("x:",x)
                    if dominio in x:
                        #print("entrei")
                        #print("x=",x)
                        x = x.split(" ")
                        flag = 2

                        clientQuery.setresponseValues(x[2])
                        clientQuery.set_nr_of_values(1)

                        arrayExtraValues = bancodeDados.getarrayExtravalues2()
                        clientQuery.setflags("")
                        clientQuery.setresponseCode("")

                        clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
                        clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

                        clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
                        clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

                        logER(c.getLGdom(), address, "NAME exists but not found any info", escolhaDebug)
                        break

                dominioList.pop(0)
                dominio = separator.join(dominioList)
                i = i-1


        if flag == 0:
            arrayExtraValues = bancodeDados.getarrayExtravalues2()

            clientQuery.setflags("")
            clientQuery.setresponseCode(2)
            clientQuery.setauthoritiesValues(bancodeDados.get_authoritiesValues())
            clientQuery.set_nr_of_authorities(len(clientQuery.getauthoritiesValues()))

            clientQuery.setextra_values(bancodeDados.get_extraValues(arrayExtraValues))
            clientQuery.set_nr_of_extra_values(len(clientQuery.getextra_values()))

            msgFromServer = clientQuery.buildmsg2()
            #print("msg:",msgFromServer)

            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            bytesToSend = str.encode(msgFromServer)
            time.sleep(0.05)
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logER(c.getLGdom(), responseAddress, "NAME doesn't exist", escolhaDebug)
            socket.close
            flagEnvio = 1
        elif (flagEnvio == 0):
            
            # preenche com a mensagem do Servidor ,cria o Socket e envia para o respetivo endereço
            msgFromServer = clientQuery.buildmsg3()

            UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

            bytesToSend = str.encode(msgFromServer)
            time.sleep(0.05)#debug
            UDPResponseSocket.sendto(bytesToSend, responseAddress)
            logQR(c.getLGdom(), responseAddress, message, escolhaDebug)
            socket.close



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

    #debugParseConfig(c)

    bd = c.getDB()
    bancodeDados=DataBase()
    bancodeDados.preenche(bd)
    print("Base de Dados Carregada")
    print("----------------------")
    logEV(c.getLGdom(), "db-file-read", bd, escolhaDebug)

    #debugParseBD(bancodeDados)

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



    #UDP connection
    UDP_Connection(localIP, localPort,bancodeDados, escolhaDebug, c)






if __name__ == "__main__":
    main()