
class SSMSG:
    def __init__(self):

        self.messageID=""
        self.flags = ""
        self.responseCode = ""
        self.nr_of_values = ""
        self.nr_of_authorities = ""
        self.nr_of_extra_values = ""
        self.querieName = ""
        self.querie_type = ""
        self.recursivo=""


    def getmessageID(self):
        return self.messageID
    def getflags(self):
        return self.flags
    def getresponseCode(self):
        return  self.responseCode
    def get_nr_of_values(self):
        return  self.nr_of_values
    def get_nr_of_authorities(self):
        return self.nr_of_authorities
    def get_nr_of_extra_values(self):
        return  self.nr_of_extra_values
    def getquerieName(self):
        return  self.querieName
    def getquerieType(self):
        return self.querie_type
    def getrecursivo(self):
        return self.recursivo

    def setmessageID(self,msgid):
        self.messageID = msgid
    def setflags(self,flg):
        self.flags = flg
    def setresponseCode(self,rc):
        self.responseCode=rc
    def set_nr_of_values(self,nr):
        self.nr_of_values=nr
    def set_nr_of_authorities(self,na):
        self.nr_of_authorities=na
    def set_nr_of_extra_values(self,ne):
        self.nr_of_extra_values=ne
    def setquerieName(self,qn):
        self.querieName=qn
    def setquerieType(self,qt):
        self.querie_type=qt
    def setrecursivo(self,r):
        self.recursivo=r

    def build_message(self):
        mensagem = str(self.messageID) + "," + str(self.flags) + "," + str(self.responseCode) + "," + str(self.nr_of_values) + "," + str(
            self.nr_of_authorities) + "," + str(self.nr_of_extra_values) + ";" + str(self.querieName) + "," + str(
            self.querie_type) + ";" + str(self.recursivo)
        print("----------------------")
        print("Mensagem Enviada: " + mensagem)
        print("----------------------")
        return mensagem