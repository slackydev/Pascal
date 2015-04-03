""" 
  Execute:
    main-c.exe <filename>
  
  Build:
    pypy C:\PyPy23_Src\rpython\bin\rpython -Ojit main.py
  
  JIT-trace:
    set PYPYLOG=jit-log-opt:jit.txt
"""
import sys
from P import (
  interpreter,
  bytecode,
  parser
)
from P.errors import *
from P.lexer import tokenize
from time import time
from rpython.rlib.streamio import open_file_as_stream


def read_file(f):
  err = 0
  code = ''
  try:
    file = open_file_as_stream(f)
    code = file.readall()
    file.close()
  except Exception:
    print 'Exception: Could not open file "%s"' % f
    err = 1
  return code,err

    
def compile(script, filename):
  machine = None
  err = 0
  try:
    tokens = tokenize(script, filename)
    
    compiler = bytecode.CompilerContext()
    bytecode.register_basetypes(compiler)
    bytecode.register_internals(compiler)

    ast = parser.Parser(tokens).parse_program()
    ast.compile(compiler)
    
    bc = compiler.create_bytecode()
    machine = interpreter.Interpreter(bc)  
  except PException as e:
    print e.error()
    err = 1
  return machine,err
  

def run(machine):
  try:
    machine.run()
  except PException as e:
    print e.error()
    return 1
  return 0
  
def main(argv):
  if len(argv) < 2:
    print 'interpreter <file>'
    return 1
  
  code,err = read_file(argv[1])
  if err == 1: return err
    
  time_now = time()
  print '[Compiling...]'
  machine,err = compile(code, argv[1])
  if err == 1:
    print '[Compiling failed]'
    return err
  print '[Compiled in '+ str(time() - time_now) + ' sec]'

  time_now = time()
  print '\n[Executing...]'
  err = run(machine)
  if err == 1:
    print '[Execution failed]'  
    return 1
  print '[Executed in '+ str(time() - time_now) + ' sec]'  
  
  return 0
  

def target(*args):
  return main, None
  
  
if __name__ == '__main__':
  main(sys.argv)