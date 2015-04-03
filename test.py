from P import (
  interpreter,
  bytecode,
  parser,
  lexer
)

if __name__ == '__main__':
  code = '''
print 123;
  '''

  tokens = lexer.tokenize(code, '__main__')
  parser = parser.Parser(tokens)
  ast = parser.parse_program()
  #print ast

  compiler = bytecode.CompilerContext()
  bytecode.register_basetypes(compiler)
  bytecode.register_internals(compiler)

  ast.compile(compiler)
  bc = compiler.create_bytecode()
  #print bc.dump()
  machine = interpreter.Interpreter(bc)
  
  print '--| exec |-------------->'
  machine.run()