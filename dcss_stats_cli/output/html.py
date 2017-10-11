import os
import output.lib.html

class Html():
    filename = ""
    h = output.lib.html.HTML()
    output=[]
    def __init__(self,filename="game_stats.html"):
        self.filename = filename
        if os.path.isfile(self.filename):
            os.remove(self.filename)


    def write_header(self,msg,level=1):
        output=msg
        if level==1:
            output=  self.h.h1(msg)
        if level==2:
            output = self.h.h2(msg)
        if level==3:
            output = self.h.h3(msg)

        self.write_line(output)
    def write_footer(self, msg):
        return msg

    def get_bold(self,msg):
        return self.h.b(msg)

    def get_italic(self,msg):
        return self.h.i(msg)

    def get_underlined(self,msg):
        return self.h.u(msg)

    def get_hyperlink(self,link,text):
        return self.h.link( text ,link)

    def write_separator(self):
        self.write_line(self.h.hr())

    def write_line(self,msg):
        """
        this function write data to file
        :param data:
        :return:
        """



        self.output.append(str(msg))
        self.output.append(str(self.h.br()))


    def complete(self):
        # Write the array to disk
        file = open(self.filename, 'w')
        file.write(os.linesep.join(self.output))
        file.close()

    def start(self):
        self.h = self.h.head(self.h.link('rel="stylesheet" href="style.css"'))