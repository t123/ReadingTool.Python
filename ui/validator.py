import re
from PyQt4 import QtCore, QtGui, Qt

Ok = "#96D899"
Failed = "#FBE3E4"

class FormValidator(QtGui.QValidator):
    def __init__(self, parent=None):
        QtGui.QValidator.__init__(self, parent)
        
    def setBackground(self, color):
        if self.parent() is None:
            return
        
        p = Qt.QPalette()
        p.setColor(QtGui.QPalette.Base, QtGui.QColor(color))
        self.parent().setPalette(p)
        
class RegexValidator(FormValidator):
    def __init__(self, parent=None):
        FormValidator.__init__(self, parent)
        
    def validate(self, input, pos):
        try:
            re.compile(input)
            self.setBackground(Ok)
            return (QtGui.QValidator.Acceptable, input, pos)
        except:
            pass            
        
        self.setBackground(Failed)
        return (QtGui.QValidator.Intermediate, input, pos)
        
class RequiredValidator(FormValidator):
    def __init__(self, parent=None):
        FormValidator.__init__(self, parent)
        
    def validate(self, input, pos):
        if len(input.strip())>0:
            self.setBackground(Ok)
            return (QtGui.QValidator.Acceptable, input, pos)
        
        self.setBackground(Failed)
        return (QtGui.QValidator.Intermediate, input, pos)
    