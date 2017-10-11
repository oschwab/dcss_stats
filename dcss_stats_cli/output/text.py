import os

class Text():
    filename = ""
    def __init__(self,filename="game_stats.txt"):
        self.filename = filename
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def write_header(self,msg,level=1):
        output=msg
        if level==1:
            output= "*" * 50 + "\n" + "*" * 50 + "\n" + "    " + msg + "\n" + "*" * 50 + "\n" + "*" * 50 + "\n"
        if level==2:
            output= "*" * 50 + "\n" + "    " + msg + "\n" +  "*" * 50 + "\n"
        if level==3:
            output = msg + "\n" + "-" * len(msg)
        self.write_line(output)
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
        self.write_line("-" * 50)

    def write_line(self,msg):
        """
        this function write data to file
        :param data:
        :return:
        """

        with open(self.filename, 'a') as x_file:
            x_file.write(msg + "\n")

    def complete(self):
        pass


    def start(self):
        pass