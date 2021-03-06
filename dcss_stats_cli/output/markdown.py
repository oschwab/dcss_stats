import os

class MarkDown():
    filename = ""
    def __init__(self,filename="game_stats.md"):
        self.filename = filename
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def write_title(self, title):
        self.write_header(title, 1)

    def write_header(self,msg,level=1):
        output=level * "#" + " " + msg
        self.write_line(output)
    def write_footer(self, msg):
        return msg

    def get_bold(self,msg):
        return '**'+ msg + '**'

    def get_italic(self,msg):
        return '*'+msg+'*'

    def get_underlined(self,msg):
        return msg

    def get_hyperlink(self,link,text):
        return "["+text + "]("+link+")"

    def write_separator(self):
        self.write_line("***")

    def write_line(self,msg):
        """
        this function write data to file
        :param data:
        :return:
        """

        mdmsg = msg.replace("\n", "\n\n")
        if not mdmsg[:-1]=="\n":
            mdmsg=mdmsg+"\n"
        with open(self.filename, 'a') as x_file:
            x_file.write(mdmsg + "\n")


    def complete(self):
        pass

    def start(self):
        pass