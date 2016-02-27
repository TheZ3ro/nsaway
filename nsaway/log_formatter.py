from logging import Formatter

class NsaFormatter(Formatter):
    width = 24
    datefmt='%Y-%m-%d %H:%M:%S'

    def format(self, record):
        cpath = '%s:%s:%s' % (record.module, record.funcName, record.lineno)
        cpath = cpath[-self.width:].ljust(self.width)
        record.message = record.getMessage()
        if "|" in record.message:
            record.message.replace("|","/")
        # Level is max 7 char
        s = "%-7s | [%s] | %s | %s" % (record.levelname, self.formatTime(record, self.datefmt), record.getMessage(), cpath)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        # Logging format example
        #### INFO    | [2016-02-27 13:18:44,820] | Started patrolling on module: [] every 3.0 seconds | nsaway:loop:126
        # Awk-grep friendly
        # ex. Print all WARNING message
        #### cat /var/log/nsaway.log | grep WARNING | awk -F'|' '{print $3}'
        return s
