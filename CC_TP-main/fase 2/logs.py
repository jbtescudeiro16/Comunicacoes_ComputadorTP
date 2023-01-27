
from datetime import datetime
import os

now = datetime.now()
current_time = str(str(now.day)+":"+str(now.month)+":"+str(now.year)+ "."+ str(now.hour)+":"+ str(now.minute)+":"+ str(now.second)+":"+ str(now.microsecond))

dir = os.getcwd()
fileDir = dir + "/" #"/files/"

#serverLog será igual a "SS" ou "SP".

#foi recebida uma query do endereço indicado
def logQR(serverLog, fromIP, pdu, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "QR" + " " + str(fromIP) + " " + str(pdu) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "QR" + " " + str(fromIP) + " " + str(pdu) + '\n')

    f.close() 

#foi enviada uma query para o endereço indicado
def logQE(serverLog, sentIP, pdu, debug):
    filePath = fileDir + serverLog    
    f=open(filePath,"a")
    f.write(current_time + " " + "QE" + " " + str(sentIP) + " " + str(pdu) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "QE" + " " + str(sentIP) + " " + str(pdu) + '\n')

    f.close() 

#foi enviada uma resposta a uma query para o endereço indicado
def logRP(serverLog, sentIP, pdu, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "RP" + " " + str(sentIP) + " " + str(pdu) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "RP" + " " + str(sentIP) + " " + str(pdu) + '\n')

    f.close() 

#foi recebida uma resposta a uma query do endereço indicado
def logRR(serverLog, fromIP, pdu, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "RR" + " " + str(fromIP) + " " + str(pdu) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "RR" + " " + str(fromIP) + " " + str(pdu) + '\n')

    f.close() 

# foi iniciado e concluído corretamente um processo de transferência de zona
def logZT(serverLog, targetServer, serverRole, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "ZT" + " " + str(targetServer) + " " + str(serverRole) + '\n') 
    
    if(debug == "S" or debug == "s"):
        print(current_time + " " + "ZT" + " " + str(targetServer) + " " + str(serverRole) + '\n')

    f.close() 


# foi detetado um evento/atividade interna no componente
def logEV(serverLog, event, path, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "EV" + " " + "127.0.0.1" + " " + str(event) + " " + str(path) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "EV" + " " + "127.0.0.1" + " " + str(event) + " " + str(path) + '\n')

    f.close()   


# foi recebido um PDU do endereço indicado que não foi possível descodificar corretamente
def logER(serverLog, IP, info, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "ER" + " " + str(IP) + " " + str(info) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "ER" + " " + str(IP) + " " + str(info) + '\n')

    f.close()

# foi detetado um erro num processo de transferência de zona que não foi concluída corretamente
def logEZ(serverLog, targetServer, serverRole, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "EZ" + " " + str(targetServer) + " " + str(serverRole) + '\n')
    
    if(debug == "S" or debug == "s"):
        print(current_time + " " + "EZ" + " " + str(targetServer) + " " + str(serverRole) + '\n')

    f.close()

# foi detetado um erro no funcionamento interno do componente
def logFL(serverLog, info, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "FL" + " " + "127.0.0.1" + " " + str(info) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "FL" + " " + "127.0.0.1" + " " + str(info) + '\n')

    f.close()


# foi detetado um timeout na interação com o servidor no endereço indicado
def logTO(serverLog, IP, type, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "TO" + " " + str(IP) + " " + str(type) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "TO" + " " + str(IP) + " " + str(type) + '\n')

    f.close()

# a execução do componente foi parada
def logSP(serverLog, reason, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "SP" + " " + "127.0.0.1" + " " + str(reason) + '\n')

    if(debug == "S" or debug == "s"):
        print(current_time + " " + "SP" + " " + "127.0.0.1" + " " + str(reason) + '\n')

    f.close()

# a execução do componente foi iniciada
def logST(serverLog, port, timeout, mode, debug):
    filePath = fileDir + serverLog
    f=open(filePath,"a")
    f.write(current_time + " " + "ST" + " " + "127.0.0.1" + " " + str(port) + " " + str(timeout) + " " + str(mode) + '\n')
    
    if(debug == "S" or debug == "s"):
        print(current_time + " " + "ST" + " " + "127.0.0.1" + " " + str(port) + " " + str(timeout) + " " + str(mode) + '\n')
    
    f.close()
