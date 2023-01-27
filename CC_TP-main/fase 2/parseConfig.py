from logs import *

#classe que serve de apoio ao parser do ficheiro de configs
class configLines:
    def __init__(self, parametro, tipo, valor):
        self.param = parametro
        self.tipo = tipo
        self.valor = valor

    def setParam(self, param2):
        self.param = param2

    def setTipo(self, tipo2):
        self.tipo = tipo2

    def setValor(self, valor2):
        self.valor = valor2

    def getParam(self):
        return self.param

    def getTipo(self):
        return self.tipo

    def getValor(self):
        return self.valor


    def __str__(self):
        return (self.param + " " + self.tipo + " " + self.valor )

class errors:
    def __init__(self, dominio, tempo, logs,desc):
        self.dominio = dominio
        self.tempo = tempo
        self.logs = logs
        self.desc=desc

    def setDominio(self, dominio):
        self.dominio = dominio

    def setTempo(self, tempo):
        self.tempo = tempo

    def setlogs(self, logs):
        self.logs = logs

    def setDesc(self,desc):
        self.desc = desc

    def getDom(self):
        return self.dominio

    def getTempo(self):
        return self.tempo

    def getLogs(self):
        return self.logs

    def getDesc(self):
        return self.desc


    def __str__(self):
        return (self.dominio + " " + self.tempo + " " + self.logs )


class ConfigValues:
    def __init__(self):
        self.items=[]
        self.errors=[]

    def add_item(self,newitem):
        self.items.append(newitem)
    def add_error(self,newitem):
        self.errors.append(newitem)
    def get_items(self):
        return self.items

    def testavalues(self,value):
        possiblevalues = ["DD", "SP", "SS", "DB", "ST", "LG", "IP"]
        for i in possiblevalues:
            if value == i : return True
        return False
    def fillLista(self, line):

        # print(line)
        k = line.split(" ")
        if line.strip() and not line.startswith("#")and self.testavalues(k[1]) :
            if len(k) <3:
                if (k[1] == "ST") and (k[0] != "root"):
                    #self.add_error(errors(k[0],,s))
                    print("erro")
                    #ERROS
            elif len(k)==3:
                    parameter = (k.__getitem__(0).strip("\n"))
                    type = k.__getitem__(1).strip("\n")
                    # if type not in possiblevalues:
                    #   writelog(getlogDomain(),"FL","Error/reading/Config/invalid/parameter")
                    val = k.__getitem__(2).strip("\n")
                    self.add_item(configLines(parameter, type, val))

    def preenche (self,filepath):
        f= open(filepath)
        for line in f:
            self.fillLista(line)
        f.close()

    def getvaluebytipo(self, tipo):
            result=[]
            for i in self.items:
                if (i.getTipo() == tipo):
                    result.append(i.getValor())
            return result

    def get_dominio(self):
        for i in self.items:
            return i.getParam()

    def getIp_Porta(self):
        for i in self.items:
            if (i.getTipo() == "IP"):
                return (i.getValor().strip("\n"))


    def getDB(self):
        for i in self.items:
            if (i.getTipo() == "DB"):
                return (i.getValor().strip("\n"))

    def print(self):
        for k in self.items:
            print(str(k))

    def getallLG(self):
        for i in self.items:
            if (i.getTipo() == "LG") and i.getParam()=="all":
                return (i.getValor().strip("\n"))

    def getLGdom(self):
        for i in self.items:
            if (i.getTipo() == "LG") and i.getParam()!="all":
                return (i.getValor().strip("\n"))