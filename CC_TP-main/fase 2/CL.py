import random
import socket
import sys
from parseFstMsg import *


#Função que constrói a mensagem a enviar
def build_message(message_id, flags, response_code, nr_of_values, nr_of_authorities, nr_of_extra_values, querie_name, querie_type):
    mensagem = str(message_id)+","+flags+","+str(response_code)+","+str(nr_of_values)+","+str(nr_of_authorities)+","+str(nr_of_extra_values)+";"+querie_name+","+querie_type+";"+""+","+""+","+""
    print("----------------------")
    print("Mensagem Enviada: "+mensagem)
    print("----------------------")

    return mensagem


def main():
#Parse do Ip e da Porta do servidor
    ip_server_porta = sys.argv[1]
    array_aux = str(ip_server_porta).split(":")
    ip_server = array_aux[0]
    if len(array_aux) > 1:
        porta_server = int(array_aux[1])
    else:
        porta_server = 5555

#Inicialização dos parâmetros passados posteriormente na build_message
    message_id = random.randint(1, 65535)
    flags = "Q"
    response_code = 0
    nr_of_values = 0
    nr_of_authorities = 0
    nr_of_extra_values = 0
    querie_name = sys.argv[2]
    querie_type = sys.argv[3]
    recursivo = sys.argv[4]

    if recursivo.startswith("R"):
        flags = "Q+R"

#Criação do UDP Socket

    SERVER_ADRESS_PORT = (ip_server, porta_server)

    mensagem = build_message(message_id, flags, response_code, nr_of_values, nr_of_authorities, nr_of_extra_values, querie_name, querie_type)
    #mensagem = "Estupidez!"

    bytesToSend = str.encode(mensagem)

    buffersize = 1024

    UDPClienteSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#Envia a mensagem ao servidor
    UDPClienteSocket.sendto(bytesToSend, SERVER_ADRESS_PORT)
#Recebe a mensagem do servidor
    mgsFromServer = UDPClienteSocket.recvfrom(buffersize)
#Fecha o Socket
    UDPClienteSocket.close()
#Mostra a resposta no STDout
    msg = mgsFromServer[0].decode()
    #print("debug",msg)

    cMsg = FstMsg()
    cMsg.fillSR(msg)

    rv = cMsg.responseValues.split(",")
    av = cMsg.authoritiesValues.split(",")
    ev = cMsg.extra_values.split(",")




    print("___________________________________________________")
    print("")
    print("º MessageID:", cMsg.getmessageID())
    print("º Flags:", cMsg.getflags())
    print("º ResponseCode:", cMsg.getresponseCode())
    print("º Nr_Of_Reponsevalues:", cMsg.get_nr_of_values())
    print("º Nr_Of_Authorities:", cMsg.get_nr_of_authorities())
    print("º Nr_Of_ExtraValues:", cMsg.get_nr_of_extra_values())
    print("º QuerieName:", cMsg.getquerieName())
    print("º QuerieType:", cMsg.getquerieType())

    print("")
    print("º ResponseValues:")
    i=0
    while i < len(rv):
        nr_rv = int(cMsg.get_nr_of_values())
        if nr_rv>0:
            print("->",rv[i])
        i+=1
    print("")

    print("º AuthoritiesValues:")
    i = 0
    while i < len(av):
        nr_av = int(cMsg.get_nr_of_authorities())
        if nr_av>0:
            print("->", av[i])
        i += 1
    print("")

    print("º ExtraValues:")
    i = 0
    while i < len(ev):
        nr_ev = int(cMsg.get_nr_of_extra_values())
        if nr_ev>0:
            print("->", ev[i])
        i += 1



    print("___________________________________________________")


if __name__ == "__main__":
    main()












