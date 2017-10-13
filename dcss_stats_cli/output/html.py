import os
import output.lib.html

class Html():
    filename = ""
    body = None
    output=[]
    link_number=1
    def __init__(self,filename="game_stats.html"):
        self.filename = filename
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def write_title(self, title):
        img = 'https://crawl.develz.org/logo.png'
        self.body.a(' ',href='https://crawl.develz.org/').img(' ',src=img)
        self.body.h1(title)
        self.body.hr()
        self.body.h2("Table of contents").br()

        self.toc = self.body.div(' ',klass="toc")


    def write_header(self,msg,level=1):
        link_id="#" + str(self.link_number)
        self.toc.span(' ' ,style="margin-left:" + str((level-1) *30) + "px;")
        self.toc.a(msg,href=link_id).br()

        msg = level * '    ' + msg
        if level==1:
            self.body.h1(msg,id=str(self.link_number))
        if level==2:
            self.body.h2(msg,id=str(self.link_number))
        if level==3:
            self.body.h3(msg,id=str(self.link_number))
        self.link_number = self.link_number + 1
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
        self.toc.hr()
        f = str(self.html)
        file.write(f)
        file.close()

    def start(self):
        self.html = output.lib.html.HTML('html')
        self.html.head(' ').link(rel="stylesheet", href="style.css")
        self.body = self.html.body(' ')


