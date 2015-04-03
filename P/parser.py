# -*- coding: utf-8 -*- 
'''
  1x ugly parser
'''
from AST import *
from errors import *
import lexer
from lexer import EToken
from time import sleep
from bytecode import BINOP,UNOP,ASGNOP

#---------------------------------------------------------------
#---------------------------------------------------------------

UNARY_OP_PRECEDENCE = {
  '+' :  7, '-' :  7, '~' :  7, 'not': 1
}

OPERATOR_PRECEDENCE = {
  ':=': 1,
  '+=': 1,
  '-=': 1,
  '*=': 1,
  '/=': 1,

  'and': 2,
  'or' : 2,
  'xor': 2,

  '=' : 3,
  '!=': 3,
  '<' : 4,
  '>' : 4,
  '>=': 4,
  '<=': 4,

  '|': 5,
  '&': 5,
  '^': 5,

  '+'  : 6,
  '-'  : 6,
  'div': 7,
  '/'  : 7,
  '*'  : 7,
  '%'  : 7,
  'shl': 7,
  'shr': 7,
  '**' : 8,
  '.'  : 9,
}

OPERATOR_ASSOCIATIVITY = {
  ':=': -1,
  '+=': -1,
  '-=': -1,
  '*=': -1,
  '/=': -1,
  'and': 1,
  'or' : 1,
  'xor': 1,
  '=' : 1,
  '!=': 1,
  '<' : 1,
  '>' : 1,
  '>=': 1,
  '<=': 1,
  '|': 1,
  '&': 1,
  '^': 1,
  '+'  : 1,
  '-'  : 1,
  'div': 1,
  '/'  : 1,
  '*'  : 1,
  '%'  : 1,
  'shl': 1,
  'shr': 1,
  '**' : 1,
  '['  : 1,
  '.'  : 1
}

EXPR_OP = ['~','not',':=','+=','-=','*=','and','or' ,'xor','=','!=','<' ,'>' ,'>=','<=',
           '|','&','^','+','-','div','/','*','%','shl','shr','**','[','.',]

BLOCKWORDS = ['begin','procedure','function','var','const','type','end']

# --------------------------------------------------------
#
UNDEF = 'tk_unknown'
EOF   = 'tk_eof'
SEMICOLON = 'tk_sym_semicolon'
COLON   = 'tk_sym_colon'
DOT     = 'tk_sym_dot'
EQUAL   = 'tk_cmp_eq'
COMMA   = 'tk_sym_comma'
LPAREN  = 'tk_sym_lparen'
RPAREN  = 'tk_sym_rparen'
LSQUARE = 'tk_sym_lsquare'
RSQUARE = 'tk_sym_rsquare'


IDENTIFIER = 'tk_ident'
TYPE_INT   = 'tk_typ_int'
TYPE_HEXINT= 'tk_typ_hexint'
TYPE_FLOAT = 'tk_typ_float'
TYPE_BOOL  = 'tk_typ_bool'
TYPE_CHAR  = 'tk_typ_char'
TYPE_STR   = 'tk_typ_string'
ATOM = [IDENTIFIER, TYPE_HEXINT, TYPE_INT, TYPE_FLOAT, TYPE_BOOL, TYPE_CHAR, TYPE_STR]
EXPRESSION = ATOM+['tk_ident','tk_op_plus','tk_op_minus','tk_sym_lparen','tk_sym_lsquare']


def is_operator(token):
    if token.token == 'tk_reserved': return True
    tok_type = lexer.op_tokens.get(token.symbol,None)
    return (tok_type is not None) and (tok_type == token.token)

def Expected(expected, token):
    return 'Expected "'+str(expected)+'" got "'+ token.token +'('+ token.symbol +')" at '+ token.docpos.str()

def Expected2(expected, token):
    return 'Expected "'+str(expected)+'" at '+ token.docpos.str()

def sprint(*args):
    ''' NOT RPYTHON '''
    args = [str(arg) for arg in args]
    print ' '.join(args)
    sleep(0.015)


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0;
        self.sym    = tokens[0];
        self.looping= 0;
        
    def next(self, nojunk=False):
        self.pos += 1   
        if nojunk:
          while self.tokens[self.pos].token == 'tk_newline':
            self.pos += 1
        assert self.pos < len(self.tokens)
        self.sym = self.tokens[self.pos];
        return self.sym;
      
    def prev(self):
        self.pos -= 1;
        assert self.pos > -1
        self.sym = self.tokens[self.pos];
        return self.sym;
    
    def peek(self, forward=1):
        return self.tokens[self.pos+forward];

    def docstr(self):
      return self.sym.docpos.str()    
        
    # --------------------------------------------------------
    # @param -> expected: token
    def expect(self, token, next=True, skipnl=False):
        if (self.sym.token == token):   
          res = self.sym
          if next: self.next()
          if skipnl: self.parse_end(False);
          return res
        else:
          raise CompilationError(Expected(str(token), self.sym));
     
    # @param -> expected: array of tokens      
    def expect_any(self, tokens, next=True, skipnl=False):
        if (self.sym.token in tokens):   
          res = self.sym
          if next: self.next()
          if skipnl: self.parse_end(False);
          return res
        else:
          raise CompilationError(Expected(str(tokens), self.sym));
      
    # @param -> expected: string        
    def expect_keyword(self, keyword, next=True, skipnl=False): #expect_symbol
        if self.sym.symbol_eq(keyword):   
          res = self.sym
          if next: self.next()
          if skipnl: self.parse_end(False);
          return res
        else:
          raise CompilationError(Expected(str(keyword), self.sym));
   
    # @param -> expected: array of string        
    def expect_symbols(self, kws, next=True, skipnl=False): #expect_symbols
        if (self.sym.symbol in kws):
          res = self.sym
          if next: self.next()
          if skipnl: self.parse_end(False);
          return res
        else:
          raise CompilationError(Expected(str(kws), self.sym));

    # --------------------------------------------------------
    # @param -> accepted: token
    def accept(self, token, lk=0, next=True, skipnl=False):
        tok = self.peek(lk);
        if (tok.token == token):   
          if next: self.next(skipnl)  
          return tok
        else:
          return None

    # @param -> accepted: array of tokens      
    def accept_any(self, tokens, lk=0, next=True, skipnl=False):
        tok = self.peek(lk);
        if (tok.token in tokens):   
          if next: self.next(skipnl)
          return tok
        else:
          return None

    # @param -> accepted: string        
    def accept_keyword(self, keyword, lk=0, next=True, skipnl=False):
        tok = self.peek(lk);
        if tok.symbol_eq(keyword):   
          if next: self.next(skipnl)  
          return tok
        else:
          return None

    # @param -> accepted: array of string        
    def accept_symbols(self, kws, lk=0, next=True, skipnl=False):
        tok = self.peek(lk);
        if (tok.symbol in kws):   
          if next: self.next(skipnl)  
          return tok
        else:
          return None
      

    # --------------------------------------------------------
    def get_op_precedence(self, unary=False):
        if not is_operator(self.sym): return -1
        if unary: return UNARY_OP_PRECEDENCE.get(self.sym.symbol, -1)
        return OPERATOR_PRECEDENCE.get(self.sym.symbol, -1)

    def get_op_assoc(self, unary=False):
        if not is_operator(self.sym): raise CompilationError('Expected operator at %s' % self.docstr())
        return OPERATOR_ASSOCIATIVITY.get(self.sym.symbol, -1) 
        
    #-----------------------------------------------------------------------------------------------------
    #-----------------------------------------------------------------------------------------------------
    def is_blockend(self):
        if self.sym.token_eq(EOF) or (self.sym.symbol in BLOCKWORDS):
          return True
        return False

    def parse_end(self, required=False, after=True):
        if required: 
          self.expect_any(['tk_newline', 'tk_sym_semicolon'])
        while self.accept_any(['tk_newline', 'tk_sym_semicolon']):
          pass
        if not after: self.prev()

    #-----------------------------------------------------------------------------------------------------
    def parse_identlist(self):
        idents = []
        while True:
          var = self.expect(IDENTIFIER)
          idents.append(var.symbol)
          if self.sym.token <> COMMA:
            break;
          else:
            self.next()
        return idents

    def type_definition(self,name=''):
        definition = None;
        self.parse_end(False)
                
        if self.accept(IDENTIFIER, next=False):
          if name == '':
            definition = DataType(self.sym.symbol,None, self.sym.docpos)
          else:
            definition = TypeAlias(name, self.sym.symbol, self.sym.docpos)

          self.next(nojunk=True)
          return definition
               
        elif self.accept_keyword('record'):
          self.parse_end(False)
          struct = []
          while self.sym.symbol != 'end':
            idents = self.parse_identlist()
            self.expect(COLON)
            dtype = self.type_definition()
            self.parse_end(False)
            for ident in idents:
              struct.append((ident, dtype))
            if name != '':
              definition = DataType(name, struct, self.sym.docpos)
            else:
              definition = DataType('', struct, self.sym.docpos)
          
          self.next(nojunk=True)
          return definition
            
        elif self.accept_keyword('array'):
          self.expect_keyword('of')
          arrtype = self.type_definition()
          if name != '':
            return ArrayType(name, arrtype, self.sym.docpos)
          else:
            return ArrayType('', arrtype, self.sym.docpos)
        
        raise PException('hmm')

    def parse_vars(self): 
        res = []
        self.expect(IDENTIFIER,next=False)
        idents = self.parse_identlist()
        self.expect(COLON)
        dtype = self.type_definition()
        self.parse_end(False)
        for ident in idents:
          res.append((ident, dtype))
        return res
        
    def parse_varblock(self):
        declarations = []
        while self.accept(IDENTIFIER,next=False):
          declarations.extend(self.parse_vars())
          if self.is_blockend(): 
            break
        return DeclareVariables(declarations)


    def parse_typeblock(self):
        typedefs = []
        docpos = self.sym.docpos
        while True:
          ident = self.expect(IDENTIFIER)
          self.expect(EQUAL)
          dtype = self.type_definition(ident.symbol)
          typedefs.append(dtype)
          self.parse_end(False) #self.accept(SEMICOLON)
          if self.is_blockend(): 
            break
        return DeclareTypes(typedefs, docpos)


    def parse_function(self):
        #function <name>\(<params>\):<type> [separator] <sub-program>
        #function <name>:<type> [separator] <sub-program>
        docpos = self.sym.docpos
        name = self.expect(IDENTIFIER)
        params = []
        passmethod = []
        if self.accept(LPAREN):
          while True:
            ref = self.accept_keyword('ref')
            if self.accept(IDENTIFIER,next=False):
              vars = self.parse_vars()
              params.extend(vars)
            else:
              self.expect(RPAREN)
              break;
            
            for i in range(len(vars)):
              passmethod.append(1 if ref else 0)
            if self.accept(RPAREN): 
              break;
              
        if self.accept(COLON):
          restype = self.type_definition()
        else:
          restype = None
        
        self.parse_end(False)
        program = []
        while not self.accept_keyword('begin', next=False, skipnl=True):
          while self.accept_keyword('type', skipnl=True):
            program.append( self.parse_typeblock() ) 

          while self.accept_keyword('var', skipnl=True):
            program.append( self.parse_varblock() ) 
          
          while self.accept_keyword('function', skipnl=True):
            raise PException('local function is not supported. Error at %s' % self.docstr())

        program.extend(self.parse_statements())
        program.append(Return())
        return Function(name.symbol,DeclareVariables(params,False),passmethod,restype,Block(program))

    
    def parse_atom(self):
        atom = self.expect_any(ATOM)
        result = None
        
        if atom.token == IDENTIFIER:
          if self.accept(LPAREN, next=False):
            result = self.parse_call(atom)
          else:
            result = Variable(atom.symbol, atom.docpos)
          
          if self.accept(LSQUARE, next=False): 
            result = self.parse_index_expr(result)
         
        elif atom.token == TYPE_BOOL:
          result = ConstantBool(atom.symbol)

        elif atom.token == TYPE_INT:
          result = ConstantInt(atom.symbol)

        elif atom.token == TYPE_HEXINT:
          result = ConstantInt(atom.symbol)

        elif atom.token == TYPE_FLOAT:
          result = ConstantFloat(atom.symbol)

        elif atom.token == TYPE_CHAR:
          if atom.symbol[0] == '#': 
          	data = chr(int(atom.symbol[1:]))
          else: 
          	data = atom.symbol[1]
          result = ConstantChar(data)

        elif atom.token == TYPE_STR:
          end = len(atom.symbol)-1;
          assert end > 0;
          result = ConstantString(atom.symbol[1:end])
          if self.accept(LSQUARE, next=False): 
            result = self.parse_index_expr(result)
        
        if result is None: 
          raise PException("Impossible error at %s" % self.docstr())
        return result
   
    
    def print_stmt(self):
        self.expect_keyword('print')
        pos = self.sym.docpos
        
        ignore_nl = False;
        if self.accept(LPAREN): 
            ignore_nl = True
            self.parse_end(False)

        expr_to_print = []
        while True:
          expr_to_print.append(self.parse_expression(ignore_nl=ignore_nl))
          if ignore_nl: self.parse_end(False)
          if not self.accept(COMMA,skipnl=ignore_nl): break

        if ignore_nl: self.expect(RPAREN)
        self.parse_end(True)
        return Print(expr_to_print, pos)
    
      
    def return_stmt(self):
        self.next(True)
        if self.accept(LPAREN,skipnl=True):
          if not self.accept(RPAREN):
            result = self.parse_expression(ignore_nl=True)
            self.parse_end(False)
            self.expect(RPAREN)
            return Return(result)
        return Return()
    
    def pass_stmt(self):
        self.next()
        self.parse_end(True)
        return Pass()
    
    def continue_stmt(self):
        self.next()
        self.parse_end(True)
        return Continue()
        
    def break_stmt(self):
        self.next()
        self.parse_end(True)
        return Break()
      
    
    def while_stmt(self):
        self.looping += 1
        self.expect_keyword('while')
        cond = self.parse_expression()
        self.expect_keyword('do')
        body = Block(self.parse_statements())
        self.looping -= 1
        return While(cond, body)


    def repeat_stmt(self):
        self.expect_keyword('repeat',skipnl=True)
        self.looping += 1
        stmts = []
        while not self.accept_keyword('until', next=False):
          stmts.append( self.parse_primary() )
        body = Block(stmts)
        self.expect_keyword('until')
        cond = self.parse_expression()
        self.looping -= 1
        return Repeat(cond, body)
      
    
    def for_stmt(self):
        self.expect_keyword('for')
        self.looping += 1
        if self.accept(IDENTIFIER, next=False):
          ident = self.expect(IDENTIFIER)
          self.expect('tk_op_assign')
          left = Variable(ident.symbol, ident.docpos)
          low = Assignment(':=', left, self.parse_expression())
        elif self.accept_keyword('var', next=False):
          low = self.vardecl_expr(False)
        else:
          raise CompilationError(Expected2("assignment", self.sym));
 
        kw = self.expect_symbols(['to','downto'])
        high = self.parse_expression()
        self.expect_keyword('do')
        body = Block(self.parse_statements())
        self.looping -= 1
        return For(low, high, body, kw.symbol_eq('to'))

      
    def if_stmt(self):
        self.expect_keyword('if')
        cond = self.parse_expression()
        self.expect_keyword('then')
        body = Block(self.parse_statements())
        else_body = None;
        if self.accept_keyword('else'):
          else_body = Block(self.parse_statements())
        return If(cond, body, else_body)

    
    def __operation(self,op,left,right):
        if op.token == DOT:
          res = Field(left, right, self.sym.docpos)
        elif op.symbol in ASGNOP:
          res = Assignment(op.symbol, left, right)
        else:
          res = BinOp(op.symbol, left, right, self.sym.docpos)
        return res

    def parse_simple_expr(self):
        # (+|-|~|not)IDENT
        if self.sym.symbol in UNOP:
          operator =self.sym.symbol
          self.next()
          return UnaryOp(operator, self.parse_simple_expr())
        # ATOM
        if self.accept_any(ATOM, next=False):
          return self.parse_atom()

        if self.accept(LPAREN, next=False):
          return self.parse_parenthesis()

        if self.accept(LSQUARE, next=False):
          return self.parse_array()
          
        raise CompilationError('Unexpected `%s("%s")` at %s' % (self.sym.token, self.sym.symbol, self.docstr()))
        
    def parse_RHS_expr(self, left, left_precedence, ignore_nl=False):
        # If this is a binary operator, find its precedence.
        while True:
          if ignore_nl: self.parse_end(False)
          precedence = self.get_op_precedence()
          # If this is a binary operator that binds at least as tightly as the
          # current one, consume it; otherwise we are done.
          if precedence < left_precedence:
            return left
 
          operator = self.sym
          self.next(ignore_nl)
 
          # Parse the unary expression after the binary operator.
          right = self.parse_simple_expr()
         
          # If `operator` binds less tightly with right than the operator after
          # right, let the pending operator take right as its left.
          next_precedence = self.get_op_precedence()
          if precedence < next_precedence:
              right = self.parse_RHS_expr(right, precedence+1)
          
          # Else if operators binds equally, let the associativity decide the order.  
          elif precedence == next_precedence:
            assoc = precedence + self.get_op_assoc()
            right = self.parse_RHS_expr(right, assoc, ignore_nl)
          
          # Join left and right.
          left = self.__operation(operator, left, right)

        return left

    def parse_expression(self, expect_end=False, ignore_nl=False):
        left = self.parse_simple_expr()
        right = self.parse_RHS_expr(left, 0, ignore_nl)
        if expect_end: self.parse_end(True)
        return right
    

    def parse_parenthesis(self):
        self.next(nojunk=True)  # eat '(' and newline
        contents = self.parse_expression(ignore_nl=True)
        self.parse_end(False)
        self.expect(RPAREN)
        return contents

    def parse_array(self):
        self.next(nojunk=True)  # eat '[' and newline
        items = []
        while not self.accept(RSQUARE):
          items.append( self.parse_expression(ignore_nl=True) )
          self.accept(COMMA)
          self.parse_end(False)
        if len(items) == 0:
          raise CompilationError('Empty constant array found at %s' % self.docstr())
        return ConstantArray(items)

    def parse_call(self,fname):
        self.expect(LPAREN)
        arguments = []
        while not self.accept(RPAREN):
          expr = self.parse_expression()
          arguments.append(expr)
          if not self.accept(COMMA):
            self.expect(RPAREN,next=False)

        return Call(fname.symbol, arguments, self.sym.docpos);


    def parse_index_expr(self, left):
        self.expect(LSQUARE)
        while True:
          _pos = self.sym.docpos
          left = Index(left, self.parse_expression(),_pos)
          if not self.accept(COMMA):
            break;
        self.expect(RSQUARE)
        return left


    def parse_field_expr(self, left):
        self.expect(DOT)
        right = self.expect(IDENTIFIER)
        return Field(left, Variable(right.symbol, right.docpos))


    def vardecl_expr(self, exp_end=True):
        self.next()
        ident = self.expect(IDENTIFIER)
        self.expect('tk_op_assign')
        expr = self.parse_expression(exp_end)
        return DeclAssignment(ident.symbol, expr, self.sym.docpos);


    def parse_primary(self):
        result = None
        # expression
        if self.accept_any(EXPRESSION, next=False):
          result = ExprStatement(self.parse_expression(True))

        # var declaration
        elif self.accept_keyword('var', next=False):
          result = self.vardecl_expr()
        
        elif self.accept_keyword('if', next=False):
          result = self.if_stmt()
          
        elif self.accept_keyword('continue', next=False):
          if self.looping == False:
            raise CompilationError('`Continue` is not allowed outside a loop. Error at %s' % self.docstr())
          result = self.continue_stmt()
          
        elif self.accept_keyword('break', next=False):
          if self.looping == False:
            raise CompilationError('`Break` is not allowed outside a loop. Error at %s' % self.docstr())
          result = self.break_stmt()
          
        elif self.accept_keyword('pass', next=False):
          result = self.pass_stmt()
        
        elif self.accept_keyword('exit', next=False):
          result = self.return_stmt()
          
        elif self.accept_keyword('while', next=False):
          result = self.while_stmt()

        elif self.accept_keyword('repeat', next=False):
          result = self.repeat_stmt()
        
        elif self.accept_keyword('for', next=False):
          result = self.for_stmt()
          
        elif self.accept_keyword('print', next=False):
          result = self.print_stmt()

        if result is not None:
          self.parse_end(False)
          return result

        elif self.is_blockend():
          return None;

        raise CompilationError('Unexpected operation `'+ self.sym.token +'` at '+ self.docstr())
    

    def parse_statements(self):
        result = []
        self.parse_end(False)
        if self.accept_keyword('begin',skipnl=True):
          while not self.accept_keyword('end'):
            prim = self.parse_primary()
            if prim is not None: result.append( prim )
          self.parse_end(False)
        else:
          prim = self.parse_primary()
          if prim is not None: result.append( prim )

        return result
    
    
    def parse_program(self):
        ''' PROGRAM = TYPE* | VAR* | STATEMENTS+ '''
        program = []
        while not(self.sym.token_eq(DOT) or self.sym.token_eq(EOF)):
          self.parse_end(False)
          #parse typeblock
          if self.accept_keyword('type', skipnl=True):
            program.append( self.parse_typeblock() ) 
            self.accept_keyword('end',skipnl=True)
            continue;

          #parse varblock
          if self.accept_keyword('var', skipnl=True):
            program.append( self.parse_varblock() ) 
            self.accept_keyword('end',skipnl=True)
            continue;

          #parse function
          if self.accept_keyword('function', skipnl=True):
            program.append( self.parse_function() )
            continue;

          #parse statements
          stmts = self.parse_statements()
          if stmts != []:
            program.extend(stmts)
        
        program.append(Return())
        return Block(program)
