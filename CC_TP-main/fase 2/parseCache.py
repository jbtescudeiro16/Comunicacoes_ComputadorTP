from datetime import datetime
import threading

class Line_cache:
    def __init__(self):
        self.parametro = ""
        self.pergunta = ""
        self.resposta = ""
        self.ttl = ""
        self.responseCode = ""

    def setParametro(self,param):
        self.parametro = param


    def setPergunta(self, pergunta):
        self.pergunta = pergunta


    def setResposta(self, resposta):
        self.resposta=resposta


    def setTTL(self, rv):
        #print("debug",rv)
        arrline = rv.split(",")
        line=arrline[0]

        arrcoisas = line.split(" ")

        if len(arrcoisas)>1:
            ttl = arrcoisas[len(arrcoisas)-1]

            now = datetime.now()
            ts = datetime.timestamp(now)

            ttl = float(ttl)

            resposta = ttl+ts
            resposta= str(resposta)
            self.ttl = resposta






    def setRespValue(self, rc):
        self.responseCode = rc


    def getParametro(self):
         return self.parametro

    def getPergunta(self):
         return self.pergunta


    def getResposta(self):
         return self.resposta

    def getTTL(self):
         return self.ttl

    def getRespValue(self):
         return self.responseCode


    def toString(self):
        resposta=""
        resposta+=self.parametro+" "
        resposta+=self.pergunta
        resposta+=self.resposta
        resposta+=self.ttl
        resposta+=self.responseCode

        return resposta




class Cache:


    def __init__(self):
        self.cacheArr=[]

    def add_arr(self, newline):
        lock = threading.Lock()

        lock.acquire()
        self.cacheArr.append(newline)
        lock.release()

    def ProcRespostas(self, parametro, pergunta):
        lock = threading.Lock()
        lock.acquire()
        resp = ""
        for i in self.cacheArr:

            #print("parametro a comparar:",parametro)
            #print("parametro da cache:", i.getParametro())
            #print("pergunta a comparar:", pergunta)
            #print("pergunta da cache:", i.getPergunta())

            if i.getParametro() == parametro and i.getPergunta() == pergunta:
                if not self.checkTTL(i):
                    resp = i.getResposta()
                else:
                    self.cacheArr.remove(i)
        lock.release()

        return resp


    def checkTTL(self,item):
        now = datetime.now()
        ts = datetime.timestamp(now)

        #print("TTL =",item.getTTL())

        ttl=float(item.getTTL())

        if ttl < ts:
            return True

        return False








