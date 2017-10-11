import os

class Console():

    def write_header(self,msg,level=1):
        output=msg
        if level==1:
            output= "*" * 50 + "\n" + "*" * 50 + "\n" + "    " + msg + "\n" + "*" * 50 + "\n" + "*" * 50 + "\n"
        if level==2:
            output= "*" * 50 + "\n" + "    " + msg + "\n" +  "*" * 50 + "\n"
        if level==3:
            output = msg + "\n" + "-" * len(msg)
        print(output)
    def write_footer(self, msg):
        return msg

    def get_bold(self,msg):
        return msg

    def get_italic(self,msg):
        return msg

    def get_underlined(self,msg):
        return msg

    def get_hyperlink(self,link,text):
        return text + "("+link+")"

    def write_separator(self):
        print("-" * 50)

    def write_line(self,msg):
        print(msg)

    def completed(self):
        pass

    def start(self):
        pass
