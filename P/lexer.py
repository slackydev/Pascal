'''
  1x horrible looking lexer/tokenizer that does the job... barely
'''
import re
import sys
from misc import *
from errors import *
from rpython.rlib.nonconst import NonConstant

class Token(object):
    def __init__(self, symbol,token,docpos):
        self.symbol = symbol
        self.token = token
        self.docpos = docpos
      
    def symbol_eq(self, v):
        return v == self.symbol.lower()

    def token_eq(self, v):
        return v == self.token

    def __repr__(self):
        ''' NOT RPYTHON '''
        return '('+str(self.symbol)+', '+str(self.token)+')'


EToken = DummySet([
  'tk_eof',
  'tk_unknown',
  'tk_ident',
  'tk_comment',
  'tk_directive',
  'tk_whitespace',
  'tk_newline',
  'tk_reserved',
  
  'tk_typ_char',
  'tk_typ_string',
  'tk_typ_bool',
  'tk_typ_int',
  'tk_typ_hexint',
  'tk_typ_float',

  'tk_op_assign',
  'tk_op_assign_add',
  'tk_op_assign_sub',
  'tk_op_assign_mul',
  'tk_op_assign_div',

  'tk_op_deref',
  'tk_op_divide',
  'tk_op_minus',
  'tk_op_modulo',
  'tk_op_multiply',
  'tk_op_plus',
  'tk_op_ref',
  'tk_op_power',
  'tk_op_inv', 
  
  'tk_op_band',
  'tk_op_bor',
  'tk_op_bxor',

  'tk_cmp_eq',
  'tk_cmp_gt',
  'tk_cmp_gte',
  'tk_cmp_lt',
  'tk_cmp_lte',
  'tk_cmp_ne',
  
  'tk_sym_bslash',
  'tk_sym_comma',
  'tk_sym_colon',
  'tk_sym_dot',
  'tk_sym_dotdot',
  'tk_sym_semicolon',
  'tk_sym_lparen',
  'tk_sym_rparen',
  'tk_sym_lbrace',
  'tk_sym_rbrace',
  'tk_sym_lsquare',
  'tk_sym_rsquare'
])


reserved = DummySet([
  'and',
  'array',
  'begin',
  'break',
  'case',
  'const',
  'continue',
  'div',
  'do',
  'else',  
  'downto',
  'end',
  'exit',
  'for',
  'function',
  'goto',
  'if', 
  'in',
  'label',
  'not',
  'object',
  'of',
  'or',
  'pass',
  'print',
  'ref',
  'repeat',
  'then',
  'to',
  'type',
  'record',
  'set',
  'shl',
  'shr',
  'until',
  'var',
  'while',
  'xor'
])

#MAX_OP_SIZE = 2;
OP_RANGE = [2,1]
op_tokens = {
  ':=':    EToken['tk_op_assign'],
  '+=':    EToken['tk_op_assign_add'],
  '-=':    EToken['tk_op_assign_sub'],
  '*=':    EToken['tk_op_assign_mul'],
  '/=':    EToken['tk_op_assign_div'],
  
  '<=':    EToken['tk_cmp_lte'],
  '>=':    EToken['tk_cmp_gte'],
  '!=':    EToken['tk_cmp_ne'],
  '<':     EToken['tk_cmp_lt'],
  '>':     EToken['tk_cmp_gt'],
  '=':     EToken['tk_cmp_eq'],

  '^':     EToken['tk_op_bxor'],
  '&':     EToken['tk_op_band'],
  '|':     EToken['tk_op_bor'],

  '**':    EToken['tk_op_power'],
  '/':     EToken['tk_op_divide'],
  '-':     EToken['tk_op_minus'],
  '%':     EToken['tk_op_modulo'],
  '*':     EToken['tk_op_multiply'],
  '+':     EToken['tk_op_plus'],
  '@':     EToken['tk_op_ref'],
  '~':     EToken['tk_op_inv'],

  ':':     EToken['tk_sym_colon'],
  ';':     EToken['tk_sym_semicolon'],
  '(':     EToken['tk_sym_lparen'],
  ')':     EToken['tk_sym_rparen'],
  '[':     EToken['tk_sym_lsquare'],
  ']':     EToken['tk_sym_rsquare'],
  '}':     EToken['tk_sym_lbrace'],
  '{':     EToken['tk_sym_rbrace'], 
  '..':    EToken['tk_sym_dotdot'],
  '.':     EToken['tk_sym_dot'],
  ',':     EToken['tk_sym_comma']
}


NULL_TOKEN = Token('', EToken['tk_unknown'], DocPos(0,0,''))
NUMBERS = list('0123456789')
HEXNUMBERS = list('0123456789ABCDEF')
ALPHA   = list('_abcdefghijklmnopqrstuvwxyz')
ALPHANUM = list('_abcdefghijklmnopqrstuvwxyz0123456789')


def keyword(x):
    x = x.lower();
    if x in reserved: 
      return EToken['tk_reserved']

    elif x in ['true','false']: 
      return EToken['tk_typ_bool']

    else:
      return EToken['tk_ident']
    

def startswith(text, options):
    if NonConstant(0): options = ['foo'] #pypy typing
    best = ''
    for val in options:
      tmp = text[:len(val)]
      if tmp.lower() == val.lower():
        if len(val) > len(best):
          best = tmp
    return best
  

class Lexer(object):
    def __init__(self, code, filename, ignore_tokens=[]):
        self.code = code + '\0'
        self.tokens = []
        self.filename = filename
        self.ignore = ignore_tokens
        
        self.pos = self.colstart = 0
        self.line = 1

    def next(self, fw=1):
        self.pos += fw
        if self.pos == len(self.code):
          return None
        return self.code[self.pos]

    def peek(self):
        return self.code[self.pos+1]
      
    def match(self, alt, next=True):
        if NonConstant(0): alt = ['foo'] #rpython hack
        l = 0
        for i in alt: 
          if len(i) > l: 
            l = len(i)
        text = self.code[self.pos:self.pos+l]
        tmp = startswith(text, alt)
        if next: 
          self.pos += len(tmp)
        return tmp != ''
        
    def get_op(self):
        for i in OP_RANGE:#reversed(range(1,MAX_OP_SIZE+1)):
          data = self.code[self.pos:self.pos+i]
          if data in op_tokens: 
            self.pos += len(data)
            return op_tokens[data]
        return None
        
    def nextline(self):
        self.line += 1;
        self.colstart = self.pos;

    def lex(self):
        case = self.match
        UNDEF = '';
        
        while self.pos < len(self.code):
          docpos = DocPos(self.line, self.pos-self.colstart, self.filename);
          token = Token(UNDEF, EToken['tk_unknown'], docpos)
          prev = self.pos
          
          if case(['\0']):
            break
          elif case(['\n']): 
            token = Token(r'\n', EToken['tk_newline'], docpos)
            self.nextline()
          
          elif case([' ','\t','\r','\f']):
            while case([' ','\t','\r','\f']): pass
            token = Token(UNDEF, EToken['tk_whitespace'], docpos)
          
          elif case(['//']):
            while not(case(['\n','\r','\0'],False)): self.next()
            token = Token(UNDEF, EToken['tk_comment'], docpos)

          elif case(['{']):
            if self.code[self.pos] == '$': tokentype = EToken['tk_directive']
            else: tokentype = EToken['tk_comment']
            while not(self.next() == '}'): pass
            token = Token(UNDEF, tokentype, docpos)
            self.next() #eat }

          elif case(['(*']):
            while not case(['*)']): self.next()
            token = Token(UNDEF, EToken['tk_comment'], docpos)

          elif case(["'"]):
            while not case(["'"]): self.next()
            symbol = self.code[prev:self.pos]
            if len(symbol) == 3:
              token = Token(symbol, EToken['tk_typ_char'], docpos)
            else:
              token = Token(symbol, EToken['tk_typ_string'], docpos)
            
          elif case(['"']):
            while not case(['"']): self.next()
            symbol = self.code[prev:self.pos]
            if len(symbol) == 3:
              token = Token(symbol, EToken['tk_typ_char'], docpos)
            else:
              token = Token(symbol, EToken['tk_typ_string'], docpos)
          
          elif case(['#']):
            while case(NUMBERS): pass
            char = self.code[prev:self.pos]
            token = Token(char, EToken['tk_typ_char'], docpos)

          elif case(['$']):
            while case(HEXNUMBERS): pass
            number = self.code[prev:self.pos]
            token = Token(number, EToken['tk_typ_hexint'], docpos)

          elif case(ALPHA):
            while case(ALPHANUM): pass
            value = self.code[prev:self.pos]
            token = Token(value.lower(), keyword(self.code[prev:self.pos]), docpos)
            
          elif case(NUMBERS):
            while case(NUMBERS): pass
            if self.code[self.pos] == '.':
              self.next()
              while case(NUMBERS): pass
              token = Token(UNDEF, EToken['tk_typ_float'], docpos)
            else:
              token = Token(UNDEF, EToken['tk_typ_int'], docpos)

          else:
            # check if it's an operator
            operator = self.get_op()
            if operator is not None: 
                token = Token(self.code[prev:self.pos], operator, docpos)
            # it must be undefined
            else:
              raise CompilationError('Undefined token("%s") at %s' % (self.code[self.pos], docpos.str()))
          
          # store the token if it's not ignored
          if not(token.token in self.ignore):
            if token.symbol == UNDEF:
              symbol = self.code[prev:self.pos]
              token = Token(symbol, token.token, token.docpos)
            self.tokens.append(token)

        self.tokens.append(Token(UNDEF, EToken['tk_eof'], DocPos(self.line+1, 0, self.filename)))
        return self.tokens
  

def tokenize(code, filename='__main__'):
  ignore = [EToken['tk_whitespace'], EToken['tk_comment']]
  Lex = Lexer(code, filename, ignore)
  return Lex.lex()
  

if __name__ == '__main__':
  test = '''
  var
    a,b,c:Int32;
  begin
    a := 1;
    b := 1;
    c := 1000000;
    
    while a < 1000 do
      a := a + b;
    
    print '123';
  end.
  '''
  tok = tokenize(test)
  for t in tok: print t
  
  
  
  
  