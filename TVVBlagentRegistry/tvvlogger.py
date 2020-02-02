class TVVLogger():
    WHEREAMI = None
    LEVEL = None
    DEBUG = None
    def __init__(self, whereami, level=None, debug=True):
        self.WHEREAMI = whereami
        self.LEVEL = level
        self.DEBUG = debug
    def log(self, what):
        if True == self.DEBUG:
            msg = "DEFAULT:{} - {}".format(self.WHEREAMI, what)
            if None != self.LEVEL:
                msg = "{}:{} - {}".format(self.LEVEL, self.WHEREAMI, what)
            print(msg)
        else:
            if None != self.LEVEL:
                import logging
                logging.log(self.LEVEL, msg)
        