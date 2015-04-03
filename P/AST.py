'''
  1x Messy Abstract Syntax Tree
'''
from dtypes import *
from errors import *
import bytecode
import native

type_weight = {'BOOL':0,'INT32':1,'INT64':2,'FLOAT':3}

class Node(object):
    """ The abstract AST node
    """
    def __init__(self):
      self.dtype = ''
      self.varname = ''
      self.parent = None
      
    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return OBJECT()
    
    def field(self,ctx,field): raise NotImplementedError
    def field_id(self,ctx,field): raise NotImplementedError
    
    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.__dict__ == other.__dict__)

    def __str__(self):
        ''' NOT RPYTHON '''
        return self.__class__.__name__+'()'

    def __ne__(self, other):
        return not self == other   
        
class Constant(Node):
    pass;

class Block(Node):
    """ A list of statements
    """
    def __init__(self, stmts):
        self.stmts = stmts

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(stmt) for stmt in self.stmts]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        breaks = []
        conts = []
        for stmt in self.stmts:
          if isinstance(stmt, Pass): break;
          elif isinstance(stmt, Break): breaks.append(len(ctx.data)+1)
          elif isinstance(stmt, Continue): conts.append(len(ctx.data)+1)
          data = stmt.compile(ctx)

          if data is not None:
            if data[0] is not None: breaks.extend(data[0])
            if data[1] is not None: conts.extend(data[1])
            
        return [breaks,conts]
        
class ExprStatement(Node):
    """ A single statement
    """
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.expr)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        self.expr.compile(ctx)
        ctx.emit(bytecode.DISCARD_TOP)
        
class DeclareTypes(Node):
    """ type definitions
    """
    def __init__(self, typedefs, docpos):
        self.typedefs = typedefs
        self.docpos   = docpos

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(dtype) for dtype in self.typedefs]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        for t in self.typedefs:
          type = t.vtype(ctx)
          ctx.register_type(t.dtype, type, t.docpos)
          
class DeclareVariables(Node):
    """ Variable definition
    """
    def __init__(self, varlist, initialize=True):
        self.declarations = varlist
        self.initialize = initialize

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(var)+':'+str(dtype) for var,dtype in self.declarations]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        for var,dtype in self.declarations:
          type = dtype.vtype(ctx)
          idx = ctx.register_var(var, type, dtype.docpos)
          if self.initialize:
            ctx.emit(bytecode.LOAD_CONST, ctx.register_const(type.emit()))
            ctx.emit(bytecode.STORE_COPY, idx)

class TypeAlias(Node):
    """ Datatype alias
    """
    def __init__(self, dtype, aliasof, pos):
        self.dtype = dtype
        self.aliasof = aliasof
        self.docpos = pos
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.dtype),str(self.aliasof)]
        fields = ':'.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self, ctx): return self.dtype.upper();
    def vtype(self,ctx): return ctx.resolve_type(self.aliasof, self.docpos)
    
    def compile(self, ctx):
        pass

class DataType(Node):
    """ Represent a datatype
    """
    def __init__(self, dtype, definition, pos):
        self.dtype = dtype.upper();
        self.definition = definition
        self.docpos = pos
        
    def __str__(self):
        ''' NOT RPYTHON '''
        if self.definition is not None:
          struct = []
          for f,t in self.definition:
            if t.dtype != '':
              struct.append('(%s:%s)' % (str(f),t.dtype))
            else:
              struct.append('(%s:%s)' % (str(f),'...'))
          data = [str(self.dtype),', '.join(struct)]
        else:
          data = [str(self.dtype)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self, ctx): return self.dtype
    def vtype(self,ctx): 
        if self.dtype != '':
          try: return ctx.resolve_type(self.dtype, self.docpos)
          except: pass
        
        if self.definition is not None:
          fields = []
          types  = []
          for f,t in self.definition:
            if f in fields:
              raise PException('Field "%s" is already declared at %s' % (f, self.docpos.str()))
            fields.append(f)
            types.append(t.vtype(ctx))
          return RECORD(types,fields)
        
    def compile(self, ctx):
        raise Exception()
        pass


class ArrayType(Node):
    """ Represent a datatype
    """
    def __init__(self, dtype, definition, pos):
        self.dtype = dtype.upper()
        self.definition = definition
        self.docpos = pos
        
    def __str__(self):
        ''' NOT RPYTHON '''
        return 'Array(...)'

    def type(self, ctx): return self.dtype
    def vtype(self,ctx): 
        p = self.definition.vtype(ctx)
        return ARRAY([], p, 'ARRAY')
      
    def compile(self, ctx):
        pass
        

class ConstantBool(Constant):
    """ Represent a constant
    """
    def __init__(self, val):
        self.val = True if val.lower() == 'true' else False
        self.dtype = 'BOOL'
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.val)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return BOOL() 
        
    def compile(self, ctx):
        w = TBool(self.val)
        ctx.emit(bytecode.LOAD_CONST, ctx.register_const(w))


class ConstantInt(Constant):
    """ Represent a constant
    """
    def __init__(self, val):
        self.val = native.StrToInt64(val)
        self.isInt32 = (self.val >= -0x7FFFFFFF) and (self.val <= 0x7FFFFFFF);
        self.dtype = 'INT32' if self.isInt32 else 'INT64'
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.val)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return INT() if self.isInt32 else INT64()
        
    def compile(self, ctx):
        if not(self.isInt32):
          w = TInt64(self.val)
        else:
          w = TInt(native.Int(self.val))
        ctx.emit(bytecode.LOAD_CONST, ctx.register_const(w))


class ConstantFloat(Constant):
    """ Represent a constant
    """
    def __init__(self, val):
        self.val = float(val)
        self.dtype = 'FLOAT'
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.val)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return FLOAT()
    
    def compile(self, ctx):
        w = TFloat(self.val)
        ctx.emit(bytecode.LOAD_CONST, ctx.register_const(w))


class ConstantChar(Constant):
    """ Represent a constant
    """
    def __init__(self, val):
        self.val = native.Char(val)
        self.dtype = 'CHAR'
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.val)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return CHAR()
    
    def compile(self, ctx):
        w = TChar(self.val)
        ctx.emit(bytecode.LOAD_CONST, ctx.register_const(w))


class ConstantString(Constant):
    """ Represent a constant
    """
    def __init__(self, val):
        self.val = [TChar(c) for c in val]
        self.dtype = 'STRING'
        
    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return STRING()
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [x.val for x in self.val]
        fields = ''.join(data)
        return self.__class__.__name__+'("'+fields+'")'

    def compile(self, ctx):
        w = TString(self.val)
        ctx.emit(bytecode.LOAD_CONST, ctx.register_const(w))

        
class ConstantArray(Constant):
    """ Represent a constant
    """
    def __init__(self, val):
        self.val = val
        self.dtype = 'ARRAY'
    def type(self,ctx): return self.dtype
    def vtype(self,ctx): return ARRAY()
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(x.val) for x in self.val]
        fields = ''.join(data)
        return self.__class__.__name__+'("'+fields+'")'

    def compile(self, ctx):
        raise PException('')
        #for v in self.val:
        #  v.compile()
        #  
        #w = TArray(self.val)
        #ctx.emit(bytecode.LOAD_CONST, ctx.register_const(w))


class Variable(Node):
    """ Variable reference
    """
    def __init__(self, varname, docpos=None):
        self.varname = varname
        self.docpos  = docpos

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.varname)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx):
        id,scope = ctx.get_var(self.varname, self.docpos)
        obj = ctx.locals[id] if scope == 'local' else ctx.globals[id]
        if isinstance(obj, CHAR):  return 'CHAR'
        elif isinstance(obj, BOOL):  return 'BOOL'
        elif isinstance(obj, INT32): return 'INT32'
        elif isinstance(obj, INT64): return 'INT64'
        elif isinstance(obj, FLOAT): return 'FLOAT'
        elif isinstance(obj, STRING):return 'STRING'
        elif isinstance(obj, RECORD):return 'RECORD'
        elif isinstance(obj, ARRAY): return 'ARRAY'
        elif isinstance(obj, VOID):  return 'VOID'
        return ''
    
    def vtype(self,ctx): 
        id,scope = ctx.get_var(self.varname, self.docpos)
        obj = ctx.locals[id] if scope == 'local' else ctx.globals[id]
        return obj
    
    def arraytype(self,ctx):
        return self.vtype(ctx).name.upper() 
        
    def field(self,ctx,field):
        return self.vtype(ctx).get_field(field)
        
    def field_id(self,ctx,field):
        return self.vtype(ctx).get_field_id(field)
      
    def compile(self, ctx):
        var, scope = ctx.get_var(self.varname, self.docpos)
        if scope == 'local': 
          ctx.emit(bytecode.LOAD_VAR, var)
        else:
          ctx.emit(bytecode.LOAD_GLOBAL, var)

     
class Function(Node):
    """ Function declaration
    """
    def __init__(self, name, params, passmethod, restype, program):
        self.name = name
        self.params  = params
        self.restype = restype
        self.program = program
        self.passby  = passmethod

    def __str__(self):
        ' NOT RPYTHON '
        data = [str(self.name)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'
    
    def type(self, ctx): return 'VOID' if (self.restype is None) else self.restype.type(ctx)
    def vtype(self,ctx): return self.restype.vtype(ctx)
     
    def compile(self, ctx):
        '''
          XXX: fix globals
        '''
        if self.restype is None:
          result_type = ctx.resolve_type('VOID')
        else:
          result_type = self.restype.vtype(ctx)
        
        arg_types = []
        if self.params is not None:
          for v,t in self.params.declarations:
            arg_types.append( ctx.resolve_type(t.type(ctx)) )
            
        method = FUNCTION(
          name=self.name, 
          argtypes=arg_types, 
          restype=result_type,
          passby = self.passby,
          program=None
        )
        ctx.register_function(method)
        
        ctx2 = bytecode.CompilerContext()
        ctx2.datatypes  = ctx.datatypes
        ctx2.functions  = ctx.functions[:]
        ctx2.function_id= ctx.function_id 
        ctx2.globals    = ctx.locals
        ctx2.globals_id = ctx.locals_id

        if self.restype is not None:
          #--| result variable |----------------------------
          ctx2.register_var('result', result_type)
          ctx2.emit(bytecode.LOAD_CONST, ctx2.register_const(result_type.emit()))
          ctx2.emit(bytecode.STORE_COPY, ctx2.get_var('result')[0])
        else:
          ctx2.register_var(':void:', result_type)
        
        if self.params is not None:
          self.params.compile(ctx2)
          
        #-------------------------------------------------
        self.program.compile(ctx2)
        method.program = ctx2.create_bytecode()
        #hack
        method.program.functions[-1].program = method.program
    
    
class BinOp(Node):
    """ A binary operation
    """
    def __init__(self, op, left, right, docpos=None):
        self.op = op
        self.left = left
        self.right = right
        self.docpos = docpos
      
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.op), str(self.left), str(self.right)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self, ctx):
        return self.vtype(ctx).type()
    
    def vtype(self,ctx): 
        ltyp = self.left.vtype(ctx)
        rtyp = self.right.vtype(ctx)
        if (ltyp is None) or (rtyp is None): #XXX
          if self.docpos is None: raise PException('Void does not support any operations')
          else: raise PException('Void does not support any operations. Error at %s' % self.docpos.str())
        
        if self.op in ['+','-','*','div','**','%','mod','shr','shl','|','&','^']:
          if (self.op == '+') and (ltyp.type() in ['CHAR','STRING']) or (rtyp.type() in ['CHAR','STRING']):
            return STRING()
          elif type_weight.get(ltyp.type(),-1) > type_weight.get(rtyp.type(),-1):
            return ltyp
          return rtyp
          
        elif self.op in ['=','<','>','<=','>=','!=','and','or','xor']:
          return BOOL()
        elif self.op == '/':
          return FLOAT()
        else:
          if self.docpos is None: raise PException('Unknown binary operator')
          else: raise PException('Unknown binary operator at %s' % self.docpos.str())
    
    def compile(self, ctx):
        self.left.compile(ctx)

        if self.op == 'and': ctx.emit(bytecode.JMP_IF_FALSE_NO_POP, 0)
        elif self.op == 'or': ctx.emit(bytecode.JMP_IF_NO_POP, 0)
        shrtcirc = len(ctx.data)-1
        
        self.right.compile(ctx)
        ctx.emit(bytecode.BINOP[self.op])
        
        if self.op in ['and','or']: ctx.data[shrtcirc] = len(ctx.data)
   

class UnaryOp(Node):
    """ A unary operation
    """
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.op), str(self.operand)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self, ctx):
        if self.op == 'not': return 'BOOL'
        return self.operand.type(ctx)
     
    def vtype(self,ctx): 
        if self.op == 'not': return BOOL()
        return self.operand.vtype(ctx)
    
    def compile(self, ctx):
        self.operand.compile(ctx)
        ctx.emit(bytecode.UNOP[self.op])
      
        
class Index(Node):
    """ Index operation
    """
    def __init__(self, expr, index_expr, docpos):
        self.expr = expr
        self.index_expr = index_expr
        self.docpos = docpos
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.expr), str(self.index_expr)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx):
        return self.vtype(ctx).type()

    def vtype(self,ctx): 
        tmp = self.expr.vtype(ctx)
        if isinstance(tmp, STRING): return CHAR()
        elif isinstance(tmp, ARRAY): return tmp.dtype
        raise PException('%s does not support indexing' % tmp.type())
        
    def field(self,ctx,field): #XXX
        tmp = self.expr.vtype(ctx).dtype
        if isinstance(tmp, RECORD): return tmp.get_field(field)
        raise PException('Expected a record at %s' % self.docpos.str());
        
    def field_id(self,ctx,field): #XXX
        tmp = self.expr.vtype(ctx).dtype
        if isinstance(tmp, RECORD): return tmp.get_field_id(field)
        raise PException('Expected a record at %s' % self.docpos.str());
        
    def compile(self, ctx):
        self.expr.compile(ctx);
        self.index_expr.compile(ctx)
        ctx.emit(bytecode.INDEX)

     
class Field(Node):
    """ Variable reference
    """
    def __init__(self, parent, field, docpos):
        self.parent = parent
        self.varname = field.varname
        self.docpos = docpos

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.parent), str(self.varname)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx):
        tmp = self.parent.vtype(ctx)
        if isinstance(tmp, RECORD): return tmp.get_field(self.varname).type()
        raise PException('Expected a record at %s' % self.docpos.str());
      
    def vtype(self,ctx):
        tmp = self.parent.vtype(ctx)
        if isinstance(tmp, RECORD): return tmp.get_field(self.varname)
        raise PException('Expected a record at %s' % self.docpos.str());
     
    def field(self,ctx,field):
        obj = self.parent.field(ctx, self.varname)
        return obj.get_field(field)
        
    def field_id(self,ctx,field):
        obj = self.parent.field(ctx, self.varname)
        return obj.get_field_id(field)
        
    def compile(self, ctx):
        self.parent.compile(ctx)
        id = self.parent.field_id(ctx,self.varname)
        ctx.emit(bytecode.LOAD_FIELD, id)
        

class Assignment(Node):
    """ Assign to a variable
    """
    def __init__(self, op, left, right):
        self.op   = op;
        self.left = left
        self.right = right
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [self.op, str(self.left), str(self.right)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'
        
    def type(self,ctx): return self.left.type(ctx)
    def vtype(self,ctx): return self.left.vtype(ctx)
    
    def compile(self, ctx):
        self.left.compile(ctx)
        self.right.compile(ctx)
        ctx.emit(bytecode.ASSIGN, bytecode.ASGNOP[self.op])


class DeclAssignment(Node):
    """ Declare a variable and assign a value to it.
    """
    def __init__(self, varname, expr, docpos):
        self.varname = varname
        self.docpos = docpos
        self.expr = expr
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.varname), str(self.expr)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def type(self,ctx): return self.expr.type(ctx)
    def vtype(self,ctx): return self.expr.vtype(ctx)
    
    def compile(self, ctx):
        self.expr.compile(ctx)
        id = ctx.register_var(self.varname, self.vtype(ctx), self.docpos)
        ctx.emit(bytecode.STORE_COPY, id)


class Pass(Node):
    """ Continue statement """
    def compile(self, ctx): pass
        
class Continue(Node):
    """ Continue statement """
    def compile(self, ctx): 
      ctx.emit(bytecode.JMP_BACK, 0)
    
class Break(Node):
    """ Break statement """
    def compile(self, ctx): 
      ctx.emit(bytecode.JMP_FORWARD, 0)


class While(Node):
    """ Simple loop
    """
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.cond), str(self.body)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        start = len(ctx.data)
        #while ->
        self.cond.compile(ctx)
        ctx.emit(bytecode.JMP_IF_FALSE, 0)
        stop = len(ctx.data) - 1
        #<-
        breaks,conts = self.body.compile(ctx)
        ctx.emit(bytecode.JMP_BACK, start)
        ctx.patch(stop) #patch loop
        for i in breaks: ctx.patch(i) #patch break
        for i in conts: ctx.patch(i,start) #patch continue
        
class Repeat(Node):
    """ Simple loop
    """
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.cond), str(self.body)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        start = len(ctx.data)
        breaks,conts = self.body.compile(ctx)
        #until ->
        self.cond.compile(ctx)
        ctx.emit(bytecode.JMP_IF, 0)
        stop = len(ctx.data) - 1
        ctx.emit(bytecode.JMP_BACK, start)
        #<-
        ctx.patch(stop) #patch loop
        for i in breaks: ctx.patch(i) #patch breaks
        for i in conts: ctx.patch(i,start) #patch continue
        

class For(Node):
    """ A simple for-loop
    """
    def __init__(self, low, high, body, downUp):
        self.low  = low
        self.high = high
        self.body = body
        self.downUp = downUp;
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.low), str(self.high), str(self.body), str(self.downUp)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
      ONE = ctx.register_const(TInt(native.Int(1)))
      
      scope = 'local'
      self.low.compile(ctx)
      if isinstance(self.low, DeclAssignment):
        iterator,scope = ctx.get_var(self.low.varname)
      else:
        iterator,scope = ctx.get_var(self.low.left.varname);
        ctx.emit(bytecode.DISCARD_TOP)
      code = bytecode.LOAD_VAR if scope == 'local' else bytecode.LOAD_GLOBAL
      
      #compare
      start = len(ctx.data)
      ctx.emit(code, iterator)
      self.high.compile(ctx)
      if self.downUp:
        ctx.emit(bytecode.BIN_LT)
      else:
        ctx.emit(bytecode.BIN_GT)
      
      ctx.emit(bytecode.JMP_IF_FALSE, 0)
      end_jmp = len(ctx.data) - 1
      
      breaks,conts = self.body.compile(ctx)
      incpos = len(ctx.data) #jump here if continue
      
      #increase/decrease iterator
      ctx.emit(code, iterator)
      ctx.emit(bytecode.LOAD_CONST, ONE)
      if self.downUp:
        ctx.emit(bytecode.ASSIGN, bytecode.ASGNOP['+='])
      else:
        ctx.emit(bytecode.ASSIGN, bytecode.ASGNOP['-='])
      ctx.emit(bytecode.DISCARD_TOP)
      
      ctx.emit(bytecode.JMP_BACK, start)
      ctx.patch(end_jmp) #patch loop
      for i in breaks: ctx.patch(i) #patch breaks
      for i in conts: ctx.modify(i-1, bytecode.JMP_FORWARD, incpos) #patch continue
      
      
class If(Node):
    """ if <cond> then <stmts> {else <stmts>} 
    """
    def __init__(self, cond, body, elsebody=None):
        self.cond = cond
        self.body = body
        self.elsebody = elsebody

    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(self.cond), str(self.body), str(self.elsebody)]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+fields+')'

    def compile(self, ctx):
        self.cond.compile(ctx)
        ctx.emit(bytecode.JMP_IF_FALSE, 0)
        after_if = len(ctx.data) - 1
        extra = self.body.compile(ctx)
        
        ctx.emit(bytecode.JMP_FORWARD, 0)
        after_else = len(ctx.data) - 1
        ctx.patch(after_if) #jump here if false
        if not(self.elsebody is None):
          els = self.elsebody.compile(ctx)
          extra[0].extend(els[0])
          extra[1].extend(els[1])

        ctx.patch(after_else) #jump here to skip else
        return extra
       

class Print(Node):
    def __init__(self, args, docpos=None):
        self.args = []
        for arg in args:
          self.args.insert(0,arg)
        self.docpos = docpos

    def __str__(self):
        ''' NOT RPYTHON '''
        args = ', '.join([str(x) for x in self.args])
        return self.__class__.__name__+'('+args+')'

    def compile(self, ctx):
        for expr in self.args:
          if expr.type(ctx) == 'VOID':
            if self.docpos is None: raise PException('Void does not support any operations')
            else: raise PException('Void does not support any operations. Error at %s' % self.docpos.str())
          
          expr.compile(ctx)
          ctx.emit(bytecode.NARG)
        ctx.emit(bytecode.PRINT, len(self.args))


class Call(Node):
    def __init__(self, func, args, docpos):
        self.func  = func
        self.args = []
        for arg in args: self.args.insert(0,arg)
        self.docpos = docpos
        
    def __str__(self):
        ''' NOT RPYTHON '''
        data = [str(x) for x in self.args]
        fields = ', '.join(data)
        return self.__class__.__name__+'('+self.func+', '+fields+')'

    def type(self, ctx):
        return self.vtype(ctx).type()
      
    def vtype(self, ctx):
        arguments = [expr.type(ctx) for expr in self.args]
        _, method = ctx.resolve_function(self.func, arguments, self.docpos)
        return method.restype
    
    def compile(self, ctx):
        argtypes = [expr.vtype(ctx) for expr in self.args]
        
        id, method = ctx.resolve_function(self.func, [x.type() for x in argtypes], self.docpos)
        numargs = len(method.argtypes)
        if numargs != len(self.args):
          raise PException(
                  self.func+' expects %d arguments got %d at %s' % 
                  (numargs, len(self.args), self.docpos.str())
                )
          
        for i,expr in enumerate(self.args):
          idx = numargs-i-1
          if not isinstance(method,NATIVE_FUNC):
            p = method.passby[idx]
            if p == bytecode.BYREF:
              assert not isinstance(expr, Constant),'`%s` expects argument `%d` to be Variable at %s' % (self.func,idx,self.docpos.str())
              
          param = method.argtypes[idx]
          argument = argtypes[i]
          if not param.equal(argument) and \
             not castable(argument.type(), param.type()):
            raise PException(
              '`%s` expects argument `%d` to be `%s` got `%s` at %s' % 
              (self.func, idx, param.printable(), argument.printable(), self.docpos.str())
            )
          
          expr.compile(ctx)
          ctx.emit(bytecode.NARG)
        ctx.emit(bytecode.CALL, id)


class Return(Node):
    def __init__(self, arg=None):
        self.arg = arg
        
    def __str__(self):
        ''' NOT RPYTHON '''
        return self.__class__.__name__+'(%s)' % str(self.arg)

    def compile(self, ctx): 
        if self.arg is not None:
          resvar,scope = ctx.get_var('result');
          assert scope == 'local'
          ctx.emit(bytecode.LOAD_VAR, resvar)
          self.arg.compile(ctx)
          ctx.emit(bytecode.ASSIGN, bytecode.ASGNOP[':='])
        ctx.emit(bytecode.RET)
        
        