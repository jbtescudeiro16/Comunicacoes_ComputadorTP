

class FstMsg :
    def __init__(self):

        self.messageID = ""
        self.flags = ""
        self.responseCode = ""
        self.nr_of_values = ""
        self.nr_of_authorities = ""
        self.nr_of_extra_values = ""
        self.querieName = ""
        self.querie_type = ""
        self.responseValues = ""
        self.authoritiesValues = ""
        self.extra_values = ""

    def fillSP(self, buffer):
        array_MSG = buffer.split(";")
        if len(array_MSG) < 2:
            return False
        
        header_fields_arr = array_MSG[0]
        querie_info_arr = array_MSG[1]
        
        header_fields = header_fields_arr.split(",")
        if len(header_fields) < 6:
            return False
        
        querie_info = querie_info_arr.split(",")
        if len(querie_info) < 2:
            return False
    
        self.messageID = header_fields[0].replace("b'","")
        self.flags = header_fields[1]
        self.responseCode = header_fields[2]
        self.nr_of_values = header_fields[3]
        self.nr_of_authorities = header_fields[4]
        self.nr_of_extra_values = header_fields[5]
        self.querieName = querie_info[0]
        self.querie_type = querie_info[1]
        self.responseValues = ""
        self.authoritiesValues = ""
        self.extra_values = ""
        return True

    def fillSS(self, buffer):
        array_MSG = buffer.split(";")
        header_fields_arr = array_MSG[0]
        querie_info_arr = array_MSG[1]
        data_fields_arr = array_MSG[2]

        header_fields = header_fields_arr.split(",")
        querie_info = querie_info_arr.split(",")
        data_fields = data_fields_arr.split(",")

        self.messageID = header_fields[0]
        self.flags = header_fields[1]
        self.responseCode = header_fields[2]
        self.nr_of_values = header_fields[3]
        self.nr_of_authorities = header_fields[4]
        self.nr_of_extra_values = header_fields[5]
        self.querieName = querie_info[0]
        self.querie_type = querie_info[1]
        self.responseValues = data_fields[0]
        self.authoritiesValues = data_fields[1]
        self.extra_values = data_fields[2]


    def fillSR(self, buffer):
        array_MSG = buffer.split(";")
        header_fields_arr = array_MSG[0]
        querie_info_arr = array_MSG[1]
        rv = array_MSG[2]
        av = array_MSG[3]
        ev = array_MSG[4]

        header_fields = header_fields_arr.split(",")
        querie_info = querie_info_arr.split(",")

        self.messageID = header_fields[0].replace("b'","")
        self.flags = header_fields[1]
        self.responseCode = header_fields[2]
        self.nr_of_values = header_fields[3]
        self.nr_of_authorities = header_fields[4]
        self.nr_of_extra_values = header_fields[5]
        self.querieName = querie_info[0]
        self.querie_type = querie_info[1]
        self.responseValues = rv
        self.authoritiesValues = av
        self.extra_values = ev.replace("'","")




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
    def getresponseValues(self):
        return  self.responseValues
    def getauthoritiesValues(self):
        return  self.authoritiesValues
    def getextra_values(self):
        return self.extra_values

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
    def setresponseValues(self,rv):
        self.responseValues=rv
    def setauthoritiesValues(self,av):
        self.authoritiesValues=av
    def setextra_values(self,ev):
        self.extra_values=ev

    def buildmsg(self):
        mensagem = str(self.messageID) + "," + self.flags + "," + str(self.responseCode) + "," + str(self.nr_of_values) + "," + str(
                self.nr_of_authorities) + "," + str(self.nr_of_extra_values) + ";" + self.querieName + "," + self.querie_type + ";" + str(
                self.responseValues) + "," + str(self.authoritiesValues) + "," + str(self.extra_values)
        #print("Mensagem Enviada1: " + mensagem)
        #print("----------------------")
        return mensagem


    def buildmsg2(self):

        a = ""
        b = ""
        c = ""

        for i in self.responseValues:
            a += str(i)+","
        a = a[:-1]

        for j in self.authoritiesValues:
            b += str(j)+","
        b = b[:-1]

        for y in self.extra_values:
            c += str(y)+","
        c = c[:-1]


        mensagem = str(self.messageID) + "," + self.flags + "," + str(self.responseCode) + "," + str(
            self.nr_of_values) + "," + str(
            self.nr_of_authorities) + "," + str(
            self.nr_of_extra_values) + ";" + self.querieName + "," + self.querie_type+";" + a + ";" + b + ";" + c
        #print("----------------------")
        #print("Mensagem Enviada2: " + mensagem)
        #print("----------------------")
        return mensagem



    def buildmsg3(self):

        a = ""
        b = ""
        c = ""

        for j in self.authoritiesValues:
            b += str(j)+","
        b = b[:-1]

        for y in self.extra_values:
            c += str(y)+","
        c = c[:-1]


        mensagem = str(self.messageID) + "," + self.flags + "," + str(self.responseCode) + "," + str(
            self.nr_of_values) + "," + str(
            self.nr_of_authorities) + "," + str(
            self.nr_of_extra_values) + ";" + self.querieName + "," + self.querie_type+";" + self.responseValues + ";" + b + ";" + c
        #print("----------------------")
        #print("Mensagem Enviada3: " + mensagem)
        #print("----------------------")
        return mensagem


    def buildmsg4(self):
        mensagem = str(self.messageID) + "," + self.flags + "," + str(self.responseCode) + "," + str(self.nr_of_values) + "," + str(
                self.nr_of_authorities) + "," + str(self.nr_of_extra_values) + ";" + self.querieName + "," + self.querie_type + ";" + str(
                self.responseValues) + ";" + str(self.authoritiesValues) + ";" + str(self.extra_values)
        #print("Mensagem Enviada4: " + mensagem)
        #print("----------------------")
        return mensagem

