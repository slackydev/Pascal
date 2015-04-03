from dtypes import *
from errors import *
import native

bytecodes = [
  'LOAD_CONST', 
  'LOAD_VAR',
  'LOAD_GLOBAL',
  'STORE_COPY', 
  'STORE_FAST',
  'DISCARD_TOP', 
  'JMP_IF', 
  'JMP_IF_FALSE', 
  'JMP_IF_FALSE_NO_POP',
  'JMP_IF_NO_POP',
  'JMP_BACK', 
  'JMP_FORWARD',
  'ASSIGN',
  'LOAD_FIELD',
  'INDEX',
  
  'BIN_ADD', 
  'BIN_SUB', 
  'BIN_MUL', 
  'BIN_FDIV',
  'BIN_IDIV',
  'BIN_MOD', 
  'BIN_POW',
  'BIN_EQ', 
  'BIN_NEQ', 
  'BIN_LT', 
  'BIN_GT', 
  'BIN_LTE', 
  'BIN_GTE',
  'BIN_AND', 
  'BIN_OR', 
  'BIN_XOR', 

  'BIT_SHL', 
  'BIT_SHR', 
  'BIT_XOR', 
  'BIT_AND', 
  'BIT_OR', 

  'UNARY_NOT',
  'UNARY_ADD',
  'UNARY_SUB',
  'UNARY_INV',

  'PRINT',
  'NARG',
  'CALL', 
  'RET'
]

BYVAL = 0
BYREF = 1

for i, bytecode in enumerate(bytecodes):
    globals()[bytecode] = i

BINOP = {
  '+':BIN_ADD, '-':BIN_SUB, '*':BIN_MUL, '/':BIN_FDIV, 'div':BIN_IDIV,  '%':BIN_MOD, '**':BIN_POW,
  '=':BIN_EQ, '<':BIN_LT, '>':BIN_GT, '<=':BIN_LTE, '>=':BIN_GTE, '!=':BIN_NEQ,
  'and':BIN_AND, 'or':BIN_OR, 'xor':BIN_XOR, 
  'shl':BIT_SHL, 'shr':BIT_SHR, '^':BIT_XOR, '&':BIT_AND, '|':BIT_OR 
}

UNOP = {
  '+':UNARY_ADD, '-':UNARY_SUB, 'not':UNARY_NOT, '~':UNARY_INV
}

ASGNOP = {
  ':=':0, '+=':1, '-=':2, '*=':3, '/=':4
}


def register_basetypes(ctx):
  ctx.register_type('Void',   VOID())
  ctx.register_type('Bool',   BOOL())
  ctx.register_type('Int32',  INT32())
  ctx.register_type('Int64',  INT64())
  ctx.register_type('Float',  FLOAT())
  ctx.register_type('Char',   CHAR())
  ctx.register_type('String', STRING())
  
  if native.native_size == 32:
    ctx.register_type('Int', ctx.resolve_type('Int32'))
  else:
    ctx.register_type('Int', ctx.resolve_type('Int64'))
  
  ctx.register_type('Integer', ctx.resolve_type('Int'))
  ctx.register_type('Boolean', ctx.resolve_type('Bool'))
  

def register_internals(ctx):
  import modules._math
  for func in modules._math.exports:
    ctx.register_function(func)

  import modules._system
  for func in modules._system.exports:
    ctx.register_function(func)
    
    
class CompilerContext(object):
    UNDEFINED = OBJECT()
    def __init__(self):
        self.data = []
        self.constants = []

        self.globals_id = {}
        self.globals = []
        
        self.locals_id = {}
        self.locals = []
        
        self.datatypes = {}

        self.functions = []
        self.function_id = {}
        
    #----------------------------------------------------------------------------------
    def register_const(self, v):
        if isinstance(v, TBool): 
          for i,const in enumerate(self.constants):
            if isinstance(const,TBool) and const.val == v.val: return i
        elif isinstance(v, TChar): 
          for i,const in enumerate(self.constants):
            if isinstance(const,TChar) and const.val == v.val: return i
        elif isinstance(v, TInt32): 
          for i,const in enumerate(self.constants):
            if isinstance(const,TInt32) and const.val == v.val: return i
        elif isinstance(v, TInt64): 
          for i,const in enumerate(self.constants):
            if isinstance(const,TInt64) and const.val == v.val: return i
        elif isinstance(v, TFloat): 
          for i,const in enumerate(self.constants):
            if isinstance(const,TFloat) and const.val == v.val: return i
        
        #constants of TString, TRecord or TArray MUST yield duplicates.
        
        self.constants.append(v)
        return len(self.constants) - 1

    #----------------------------------------------------------------------------------
    def register_var(self, name, obj=UNDEFINED, docpos=None):
        if name in self.locals_id:
          if docpos is None:
            raise NameError('Variable `'+name+'` is already defined')
          else:
            raise NameError('Variable `'+name+'` is already defined at '+docpos.str())
            
        self.locals_id[name] = len(self.locals)
        self.locals.append(obj)
        return len(self.locals) - 1
    
    def get_var(self, name, docpos=None):
        if name in self.locals_id:
          return (self.locals_id[name],'local')
        elif name in self.globals_id:
          return (self.globals_id[name],'global')
        else:
          if docpos is None:
            raise NameError('Variable `'+name+'` is not defined')
          else:
            raise NameError('Variable `'+name+'` is not defined at '+docpos.str())
 
    #----------------------------------------------------------------------------------
    def register_type(self, tname, obj, docpos=None):
        if tname.lower() in self.datatypes:
          if docpos is None:
            raise NameError('Type `%s` is already defined' % tname)
          else:
            raise NameError('Type `%s` is already defined at %s' % (tname, docpos.str()))
            
        self.datatypes[tname.lower()] = obj;

    def resolve_type(self, tname, docpos=None):
        try:
          return self.datatypes[tname.lower()]
        except KeyError:
          if docpos is None:
            raise NameError('Type `'+tname+'` is not defined')
          else:
            raise NameError('Type `'+tname+'` is not defined at '+docpos.str())

    #----------------------------------------------------------------------------------
    def register_function(self, func, docpos=None):
        name = func.name.lower()
        if name in self.function_id:
          if func.overload:
            self.function_id[name].append(len(self.functions))
            self.functions.append(func)
            return len(self.functions) - 1
          else:
            if docpos is None:
              raise NameError('Function `%s` is already defined' % func)
            else:
              raise NameError('Function `%s` is already defined at %s' % (func, docpos.str()))
        else:
          self.function_id[name] = [len(self.functions)]
          self.functions.append(func)
          return len(self.functions) - 1

    def resolve_function(self, name, argtypes, docpos=None):
        name = name.lower()
        try:
          ids = self.function_id[name]
          if len(ids) == 1: 
            return (ids[0], self.functions[ids[0]])
          
          #if it's an overload method, find the one with best matching args.
          match = False
          result = (0xFFFFFFF,0,None)
          for id in ids:
            sum = 0
            method = self.functions[id]
            can_cast = False
            for i,param in enumerate(method.argtypes): 
              can_cast = castable(argtypes[i], param.type())
              if can_cast: 
                sum += castvalue(argtypes[i], param.type())
              else:
                break
            if can_cast and sum < result[0]:
              result = (sum, id, method)
          
          #return it
          if result[0] != 0xFFFFFFF:
            return (result[1], result[2])
          else:  
            raise CompilationError('None of the overloads of `%s` matches the given arguments at %s' % (name, docpos.str()))
        
        except KeyError:
          if docpos is None:
            raise NameError('Function `'+name+'` is not defined')
          else:
            raise NameError('Function `'+name+'` is not defined at '+docpos.str())

    #----------------------------------------------------------------------------------
    def emit(self, bc, arg=0):
        self.data.append(bc)
        self.data.append(arg)

    def patch(self, id, new_arg=-1):
        if new_arg == -1:
          self.data[id] = len(self.data)
        else:
          self.data[id] = new_arg
          
    def modify(self, id, bc, arg=0):
        self.data[id]   = bc
        self.data[id+1] = arg

    def create_bytecode(self):
        functions = [obj.emit() for obj in self.functions]
        return ByteCode(self.data[:], self.constants[:], functions, len(self.locals))


class ByteCode(object):
    _immutable_fields_ = ['code[*]', 'constants[*]', 'functions[*]', 'n_vars']
    
    def __init__(self, code, constants, functions, n_vars):
        self.code = code
        self.constants = constants
        self.functions = functions
        self.n_vars  = n_vars
        self.globals = []

    def dump(self):
        lines = []
        i = 0
        for i in range(0, len(self.code), 2):
            c = self.code[i]
            c2 = self.code[i + 1]
            lines.append(str(bytecodes[c]) + " " + str(c2))
        return '\n'.join(lines)


