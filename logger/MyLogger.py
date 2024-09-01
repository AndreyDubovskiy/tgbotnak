import datetime

class Logger:
    def __init__(self, filename:str, add_time:bool = True, write_in_file:bool = True, write_in_console:bool = False, autosave:bool = False):
        self.created_time = str(datetime.datetime.now()).replace(":", "-")
        self.filename = filename
        self.add_time = add_time
        self.write_in_file = write_in_file
        self.write_in_console = write_in_console
        self.autosave = autosave

        self.rows = []

    def log(self, level:str,  *args):
        text: str = f"[{level}]\t"
        if self.add_time:
            text = f"[{str(datetime.datetime.now())}]" + text

        for i in args:
            text+= "\t" + str(i)
        if self.write_in_console:
            print(text)
        if self.write_in_file:
            self.rows.append(text)
        if self.autosave:
            self.save()

    def save(self):
        if self.write_in_file:
            with open(f"logger/log/{self.created_time}{self.filename}.txt", "a") as file:
                for i in self.rows:
                    file.write(i+"\n")
            self.rows = []