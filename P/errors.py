class PException(Exception):
    def __init__(self, msg=''):
        self.msg = msg

    def error(self):
        return "Exception: %s" % self.msg

    def __str__(self):
        ''' NOT RPYTHON '''
        return "%s" % self.msg 
        
class RuntimeError(PException):
    def error(self):
        return "RuntimeError: %s" % self.msg
 
class NameError(PException):
    def error(self):
        return "NameError: %s" % self.msg
 
class CompilationError(PException):
    def error(self):
        return "CompilationError: %s" % self.msg
        
class FileError(PException):
    def error(self):
        return "FileError: %s" % self.msg
        
class InternalError(PException):
    def error(self):
        return "InternalError: %s" % self.msg
        
class NotImplementedError(PException):
    def error(self):
        return "NotImplementedError: %s" % self.msg
        
class AssertionError(PException):
    def error(self):
        return "AssertionError: %s" % self.msg