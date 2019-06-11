class Parser:
    def __init__(self):
        pass
    
    def apply(self, string):
        str = string.split(' ')
        for s in str[::-1]:
            text = self.getAction(s) 
            if text is not None:
                return text
        return None

    def getAction(self, word):
        if word == 'thoat':
            return 'quit'
        elif word == 'tien':
            return 'tien'
        elif word == 'lui':
            return 'lui'
        elif word == 'trai':
            return 'quaytrai'
        elif word == 'phai':
            return 'quayphai'
        elif word == 'len':
            return 'nhinlen'
        elif word == 'xuong':
            return 'nhinxuong'
        elif word == 'dung':
            return 'dung'
        else:
            return None