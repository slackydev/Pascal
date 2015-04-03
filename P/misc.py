# -*- coding: utf-8 -*-

def DummySet(list):
  result = {}
  for x in list:
    result[x] = x
  return result
        
class DocPos():
  def __init__(self, line,col,file):
    self.line = line 
    self.col  = col;
    self.file = file;

  def __repr__(self):
    return 'DocPos(%d, %d, %s)' % (self.line, self.col, self.file)
    
  def str(self):
    return 'line %d, col %d, file %s' % (self.line, self.col, self.file)