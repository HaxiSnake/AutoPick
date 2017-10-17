import os
class Parameter:
    def __init__(self,para=[],paraName=[],configFile=""):
        self.para = para
        self.paraName = paraName
        self.configFile = configFile
        self.readPara = []
        self.readName = []
    def WriteConfig(self):
        try:
            fp=open(self.configFile,'w')
        except IOError as e:
            print(e)
            exit()
        try:
            for value,name in zip(self.para,self.paraName):
                string = name + ":"+str(value)+"\n"
                fp.write(string)
        finally:
            fp.close()
            print "Write Config Done!"
    def ReadConfig(self):
        self.readPara = []
        try:
            fp = open(self.configFile,'r')
        except IOError as e:
            print(e)
            exit()
        try:
            lines = fp.readlines()
        finally:
            fp.close()
        for line in lines:
            line_list = line.split(':')
            self.readName.append(line_list[0])
            self.readPara.append(int(line_list[1]))
        print "Read Config Done!"
        return self.readName,self.readPara


        

        
if __name__ ==  '__main__':
    para     = [1,23,456]
    paraName = ["aa","bb","cc"]
    readPara = []
    readName = []
    print ("WriteConfig:")
    print("writeName:",paraName)
    print("writeConfig:",para)
    parameter = Parameter(para,paraName,"./Config/config.txt")
    parameter.WriteConfig()
    print ("ReadConfig:")
    readName,readPara = parameter.ReadConfig()
    print("readName:",readName)
    print("readConfig:",readPara)