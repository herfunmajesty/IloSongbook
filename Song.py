class Song:
    def __init__(self, title, artist, level, s_link, y_link, lyrics, ch_list, duration, sticky):
        self.Title = title
        self.Artist = artist
        self.Level = level
        self.s_link = s_link
        self.y_link = y_link
        self.lyrics = lyrics
        self.ch_list = ch_list
        self.Duration = duration  # na potrzeby autoscrolla
        self.Sticky = sticky   # na potrzeby floatującego okna
        self.l_tr = self.convert_level(level)  # na potrzeby zmyślnego wyświetlania leveli
        self.new = '🔥' in title  # create an attribute 'new' if  🔥 is in the title
        self.html_name = self.convert_name(title)  # bo link umi być legitny
        self.Number = None

    @staticmethod
    def convert_name(title):  # converting title of the song for proper link creation
        html_title = title.replace(' ', '-')
        return html_title

    @staticmethod
    def convert_level(level):  # translating type of level to another variable just for clear visualisation
        if level == "Easy":
            l_tr = "success"
        elif level == "Medium":
            l_tr = "warning"
        elif level == "Hard":
            l_tr = "danger"
        else:
            l_tr = None
        return l_tr