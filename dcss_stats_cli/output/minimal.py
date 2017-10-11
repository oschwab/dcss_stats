class Minimal:
    def write_header(self,msg,level=1):
        return msg
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
        return ("-" * 50)

    def write_line(self,msg):
        pass
    def complete(self):
        pass

    def start(self):
        pass
