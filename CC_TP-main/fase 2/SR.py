import random
import socket
from parseDB import *
from parseConfig import *
from parseFstMsg import *
from parseCache import *
import sys
import threading
import signal

def debugParseConfig(c):
    print("config:\n get_dominio:",c.get_dominio(), 
    "\n get_items:", c.get_items(),
    "\n get_allLg:", c.getallLG(),
    "\n get_db:", c.getDB(),
    "\n get_ipPorta:", c.getIp_Porta(),
    "\n get_Lgdom:", c.getLGdom(),
    "\n get_valuebytipo:", c.getvaluebytipo("SP"))

def debugParseQuery(clientQuery):
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("get_messageID:", clientQuery.getmessageID())
    print("get_flags:", clientQuery.getflags())
    print("get_responseCode:", clientQuery.getresponseCode())
    print("get_nrOfreponsevalues:", clientQuery.get_nr_of_values())
    print("get_nrOfAuthorities:", clientQuery.get_nr_of_authorities())
    print("get_nrOfextraValues:", clientQuery.get_nr_of_extra_values())
    print("get_querieName:", clientQuery.getquerieName())
    print("get_querieType:", clientQuery.getquerieType())
    print("get_responseValues:", clientQuery.getresponseValues())
    print("get_authoritiesValues:", clientQuery.getauthoritiesValues())
    print("get_extraValues:", clientQuery.getextra_values())
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n")


#Funçao que trata da conexão UDP entre Cliente e servidor.
def UDP_Connection(localIP,localPort,c, escolhaDebug,cache):
    while True:
        bufferSize = 1024

        #Criação do Socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Função para fechar socket UDP caso haja um ctrl+c
        def signal_handler(signal, frame):
            # close the socket here
            UDPServerSocket.close()
            #print("\nUDP Socket closed!")
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


        
        #Parse da mensagem do cliente
        clientQuery=FstMsg()


        #caso onde o response code é 3
        if clientQuery.fillSP(clientMsg) == False:
            #("CODE3 msg:",message.decode())

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
            UDPServerSocket.sendto(bytesToSend, address)
            UDPServerSocket.sendto(bytesToSend, responseAddress)

            logER(c.getLGdom(),address ,"Error decoding message", escolhaDebug)
        else:

            usouCache = 0
            #forward da mensagem
            if (clientQuery.getflags() == "Q"):

                isInCache = cache.ProcRespostas(clientQuery.querie_type, clientQuery.querieName)

                if len(isInCache) != 0:

                    usouCache += 1

                    aux = isInCache.split(";")

                    clientQuery.setresponseCode(aux[1])

                    clientQuery.setresponseValues(aux[2])
                    rv = aux[2].split(",")
                    if rv[0]=="":
                        nr_of_rv=0
                    else:
                        nr_of_rv = len(rv)
                    clientQuery.set_nr_of_values(nr_of_rv)

                    clientQuery.setauthoritiesValues(aux[3])
                    av=aux[3].split(",")
                    if av[0]=="":
                        nr_of_av=0
                    else:
                        nr_of_av = len(av)
                    clientQuery.set_nr_of_authorities(nr_of_av)

                    clientQuery.setextra_values(aux[4])
                    ev = aux[4].split(",")
                    if ev[0] == "":
                        nr_of_ev = 0
                    else:
                        nr_of_ev = len(ev)
                    clientQuery.set_nr_of_extra_values(nr_of_ev)
                    clientQuery.setflags("")

                    msg = clientQuery.buildmsg4()
                    bytesToSend = msg.encode()

                    UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                    UDPResponseSocket.sendto(bytesToSend, address)
                    logRP(c.getLGdom(), address, message, escolhaDebug)

                else:
                    #print("fwrd msg:",message.decode())
                    logQR(c.getLGdom(), address, message, escolhaDebug)

                    queryMessage = message.decode()
                    clientAddress = address

                    bytesToSend = message
                    addressListST = c.getvaluebytipo("SP")

                    UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                    endereco = (addressListST[0],5555)
                    UDPResponseSocket.sendto(bytesToSend, endereco)
                    logQE(c.getLGdom(), endereco, message, escolhaDebug)
            else:
                if(clientQuery.getresponseCode() == ""):
                    logRR(c.getLGdom(), address, message, escolhaDebug)
                    clientQuery.fillSR(clientMsg)
                    #debugParseQuery(clientQuery)

                    nextIP = clientQuery.getresponseValues()
                    bytesToSend = queryMessage.encode()
                    endereco = (nextIP, 5555)

                    UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                    UDPResponseSocket.sendto(bytesToSend,endereco)
                    logQE(c.getLGdom(), endereco, message, escolhaDebug)
                else:
                    if(clientQuery.getresponseCode() == "0"):

                        cMsg = FstMsg()
                        cMsg.fillSR(clientMsg)

                        linecache = Line_cache()
                        linecache.setParametro(cMsg.getquerieType())
                        linecache.setPergunta(cMsg.getquerieName())
                        linecache.setResposta(
                            ";" + cMsg.getresponseCode() + ";" + cMsg.getresponseValues() + ";" + cMsg.getauthoritiesValues() + ";" + cMsg.getextra_values() + ";")
                        linecache.setRespValue(cMsg.getresponseCode())
                        aux = int(cMsg.get_nr_of_values())
                        if(cMsg.getquerieType()=="A" and aux>0):
                            linecache.setTTL(cMsg.getresponseValues())
                        else:
                            linecache.setTTL(cMsg.getextra_values())

                        print("")
                        print("_____________________  New-Line-cache _____________________")
                        print(linecache.toString())
                        cache.add_arr(linecache)
                        print("___________________________________________________________")
                        print("")


                        logRR(c.getLGdom(), address, message, escolhaDebug)
                        bytesToSend = message

                        UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

                        UDPResponseSocket.sendto(bytesToSend, clientAddress)
                        logRP(c.getLGdom(), clientAddress, message, escolhaDebug)

                    elif (clientQuery.getresponseCode() == "1"):
                        cMsg = FstMsg()
                        cMsg.fillSR(clientMsg)
                        #debugParseQuery(cMsg)

                        linecache = Line_cache()
                        linecache.setParametro(cMsg.getquerieType())
                        linecache.setPergunta(cMsg.getquerieName())
                        linecache.setResposta(
                            ";" + cMsg.getresponseCode() + ";" + cMsg.getresponseValues() + ";" + cMsg.getauthoritiesValues() + ";" + cMsg.getextra_values() + ";")
                        linecache.setRespValue(cMsg.getresponseCode())
                        linecache.setTTL(cMsg.getextra_values())

                        print("")
                        print("_____________________  New-Line-cache _____________________")
                        print(linecache.toString())
                        cache.add_arr(linecache)
                        print("___________________________________________________________")
                        print("")


                        bytesToSend = message
                        UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                        UDPResponseSocket.sendto(bytesToSend, clientAddress)
                        logER(c.getLGdom(), clientAddress, "NAME exists but not found any info", escolhaDebug)

                    else:
                        # Response code = 2

                        cMsg = FstMsg()
                        cMsg.fillSR(clientMsg)
                        #debugParseQuery(cMsg)

                        linecache = Line_cache()
                        linecache.setParametro(cMsg.getquerieType())
                        linecache.setPergunta(cMsg.getquerieName())
                        linecache.setResposta(
                            ";" + cMsg.getresponseCode() + ";" + cMsg.getresponseValues() + ";" + cMsg.getauthoritiesValues() + ";" + cMsg.getextra_values() + ";")
                        linecache.setRespValue(cMsg.getresponseCode())
                        linecache.setTTL(cMsg.getextra_values())

                        print("")
                        print("_____________________  New-Line-cache _____________________")
                        print(linecache.toString())
                        cache.add_arr(linecache)
                        print("___________________________________________________________")
                        print("")


                        bytesToSend = message
                        UDPResponseSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                        UDPResponseSocket.sendto(bytesToSend, clientAddress)
                        logER(c.getLGdom(), clientAddress, "NAME doesn't exist", escolhaDebug)



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
    cache = Cache()

    print("----------------------")
    print("Configs Carregados")
    print(c.getLGdom())
    logEV(c.getLGdom(), "conf-file-read", config_path, escolhaDebug)

    #debugParseConfig(c)

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
    UDP_Connection(localIP, localPort, c, escolhaDebug,cache)


if __name__ == "__main__":
    main()