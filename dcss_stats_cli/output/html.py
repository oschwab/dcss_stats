import os
import output.lib.html

class Html():
    filename = ""
    body = None
    output=[]
    def __init__(self,filename="game_stats.html"):
        self.filename = filename
        if os.path.isfile(self.filename):
            os.remove(self.filename)


    def write_header(self,msg,level=1):
        output=msg
        if level==1:
            self.body.h1(msg)
        if level==2:
            self.body.h2(msg)
        if level==3:
            self.body.h3(msg)

        #self.write_line(output)

    def write_footer(self, msg):
        return msg

    def get_bold(self,msg):
        h2 = output.lib.html.HTML()
        return h2.b(msg)

    def get_italic(self,msg):
        h2 = output.lib.html.HTML()
        return h2.i(msg)

    def get_underlined(self,msg):
        h2 = output.lib.html.HTML()
        return h2.u(msg)

    def get_hyperlink(self,link,text):
        h2 = output.lib.html.HTML()
        return h2.link( text ,link)

    def write_separator(self):
        self.body.hr()

    def write_line(self,msg):
        """
        this function write data to file
        :param data:
        :return:
        """
        self.body += str(msg)
        self.body.br()



    def complete(self):
        # Write the array to disk
        file = open(self.filename, 'w')

        f = str(self.html)
        file.write(f)
        file.close()

    def start(self):
        self.html = output.lib.html.HTML('html')
        self.html.head(' ').link(rel="stylesheet", href="style.css")
        self.body = self.html.body(' ')

