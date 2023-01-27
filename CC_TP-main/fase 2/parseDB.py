# This is a sample Python script.

class Val_Parse:
    def __init__(self, parametro , tipo , valor , tempo , prioridade):
        self.param = parametro
        self.tipo = tipo
        self.valor = valor
        self.tempo = tempo
        self.prioridade = prioridade

    def setParam(self,param2):
        self.param=param2

    def setTipo(self,tipo2):
        self.tipo=tipo2
    def setValor(self,valor2):
        self.valor=valor2
    def setTempo(self,tempo2):
        self.tempo=tempo2
    def setPrioridade(self,prioridade2):
        self.prioridade=prioridade2
    def setTTL(self,TTL):
        self.TTL=TTL


    def getParam(self):
         return self.param

    def getTipo(self):
        return self.tipo

    def getValor(self):
        return self.valor

    def getTempo(self):
        return self.tempo

    def getTTL(self):
        return self.TTL

    def getPrioridade(self):
        return self.prioridade
    def __str__(self):
        return (self.param   + " " + self.tipo + " " + self.valor + " " + self.tempo + " " + self.prioridade)


    def toString(self):
        resposta=""
        resposta+self.param
        resposta+self.tipo
        resposta+self.valor
        resposta+self.tempo
        resposta+self.prioridade

        return resposta



class DataBase():
    def __init__(self):
        self.domain=""
        self.TTL=""
        self.lista=[]
        self.listausers=[]
        self.listaCname=[]

    def add_lista(self, newitem):
        self.lista.append(newitem)
    def add_listausers(self, newitem):
        self.listausers.append(newitem)
    def add_listaCname(self, newitem):
        self.listaCname.append(newitem)
    def setDomain(self,domain):
        self.domain=domain

    def setsubdomains(self, subdomains):
        self.subdomains = subdomains

    def getDomain(self):
        return self.domain

    def preenche(self, file):

        f = open(file)
        for line in f:
            self.parserarr(line)

        f.close()

    def parserarr(self, line):
        TTL = ""
        part = line.split(" ")
        if  line.strip() and not (line.startswith("#")):
            if "Smaller" in part[0]:
                parameter = (line.split(" ").__getitem__(0)).strip("\n")
                type = line.split(" ").__getitem__(1).strip("\n")
                val = line.split(" ").__getitem__(2).strip("\n")
                time = ""
                priority = ""
                self.add_lista(Val_Parse(parameter, type, val, time, priority))
            if line.startswith("TTL"):
                self.TTL = part[2].strip("\n")
                parameter = (line.split(" ").__getitem__(0)).strip("\n")
                type = line.split(" ").__getitem__(1).strip("\n")
                val = line.split(" ").__getitem__(2).strip("\n")
                time = ""
                priority = ""
                self.add_lista(Val_Parse(parameter, type, val, time, priority))

            if line.startswith("@"):
                priority = ""
                time = " "
                if (part[1]=="DEFAULT"):
                    #print("part2:", part[2])
                    self.setDomain(part[2].strip("\n"))
                if (len(part) == 3):
                    parameter = (line.split(" ").__getitem__(0).strip("\n"))
                    type = line.split(" ").__getitem__(1).strip("\n")
                    val = line.split(" ").__getitem__(2).strip("\n")
                    time = ""
                    self.add_lista(Val_Parse(parameter, type, val, time, priority))
                else:

                    parameter = (line.split(" ").__getitem__(0).strip("\n"))
                    type = line.split(" ").__getitem__(1).strip("\n")
                    val = line.split(" ").__getitem__(2).strip("\n")
                    time = line.split(" ").__getitem__(3).strip("\n")
                    #if (type=="SOASP"):
                    #    p=val.split(".")
                    #    domi_junto=p[1]+"."+p[2]+"."
                    #    print("domi_junto:", domi_junto)
                        #if (self.getDomain()=="" or self.domain!=domi_junto):
                        #    self.setDomain(domi_junto)



                    if (len(part) == 5):
                        priority = line.split(" ").__getitem__(4).strip("\n")
                        if( priority!=""):
                            if int(priority)>=256 :
                                priority="255"

                    self.add_lista(Val_Parse(parameter, type, val, time, priority))

            if not (line.startswith("@")) :
                # hash_table.set_val(line.split(" ").__getitem__(0), line)

                k = line.split(" ")
                flag = 0
                prioridade = ""
                if "CNAME" in k:
                    param = k.__getitem__(0).strip("\n")
                    tipo = k.__getitem__(1).strip("\n")
                    valor = k.__getitem__(2).strip("\n")
                    tempo = " "
                    self.add_listaCname(Val_Parse(param, tipo, valor, tempo, prioridade))
                else:
                    if len(k) > 3:
                        flag = 1
                        param = k.__getitem__(0).strip("\n")
                        tipo = k.__getitem__(1).strip("\n")
                        valor = k.__getitem__(2).strip("\n")
                        tempo = k.__getitem__(3).strip("\n")
                    if len(k) == 5:
                        prioridade = k.__getitem__(4).strip("\n")
                        if (prioridade != ""):
                            if int(prioridade) >= 256:
                                prioridade = "255"
                    if flag:
                        dom = self.getDomain()
                        self.add_listausers(Val_Parse(param + "." + dom, tipo, valor, tempo, prioridade))



    def print(self):
        print("Dominio : " + self.getDomain())
        print("-----------------------Lista----------------")
        for i in self.lista:
            print(str(i))
        print("------------------ListaUser----------------")
        for k in self.listausers:
            print(str(k))
        print("------------------ListaCname----------------")
        for pos in self.listaCname:
            print(str(pos))


    def ProcTipo2(self,valor,param):
        result = None
        for obj in self.listausers:
            #print("obj",obj)
            if obj.tipo == valor and obj.param == param:
                result=obj

        if (result):
            #print("Tipo",result.valor,"Parametro",result.param)
            return result.valor.strip("\n")


    def ProcTipo(self,tipo,):
        result = next(
            (obj for obj in self.lista if obj.tipo == tipo),
            None
        )
        if (result):
            # print( line + " valor: "+ result.valor)
            return result.valor.strip("\n")


    def nr_linhas(self):
        cont = 0
        for i in self.lista:
            cont += 1
        for i in self.listausers:
            cont += 1
        for i in self.listaCname:
            cont += 1
        return cont


    def get_responseValues(self,querieType):

        arr_reposta = []
        if querieType == "MX" or querieType =="NS" :
            for i in self.lista:
                if i.getTipo() == querieType:
                    str_response = ""
                    str_response = str(self.domain)+" "+str(i.getTipo())+" "+str(i.getValor())+" "+str(self.TTL)+" "+str(i.getPrioridade())
                    arr_reposta.append(str_response)
            return arr_reposta
        elif querieType=="A"or querieType == "PTR":
            for i in self.listausers:
                if i.getTipo()=="A":
                    str_response=str(i.getParam())+" "+str(i.getTipo())+" "+str(i.getValor())+" "+str(self.TTL)+" "+str(i.getPrioridade())
                    arr_reposta.append(str_response)

        return arr_reposta



    def get_authoritiesValues(self):
        arr_reposta = []
        for i in self.lista:
            if i.getTipo() == "NS":

                str_response = ""
                str_response = str(self.domain)+" "+str(i.getTipo())+" "+str(i.getValor())+" "+str(self.TTL)
                arr_reposta.append(str_response)

        return arr_reposta

    def getarrayExtravalues(self, tipo):
        arr_reposta = []
        for i in self.lista:

            if tipo != "NS":
                if i.getTipo() == tipo:
                    arr_reposta.append(i.getValor())
                if i.getTipo() == "NS":
                    arr_reposta.append(i.getValor())
            else:
                if i.getTipo() == tipo:
                    arr_reposta.append(i.getValor())

        return arr_reposta

    def getarrayExtravalues2(self):
        arr_reposta = []
        for i in self.lista:
            if i.getTipo() == "NS":
                arr_reposta.append(i.getValor())


        return arr_reposta


    def get_extraValues(self, array):
        arr_reposta = []

        for i in array:
            for j in self.listausers:
                if j.getParam() == i:
                    str_response = str(i)+" "+str(j.getTipo())+" "+str(j.getValor())+" "+str(self.TTL)
                    arr_reposta.append(str_response)
        return arr_reposta



