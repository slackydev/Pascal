# -*- coding: utf-8 -*- 
from math import pow
from array import array
from rpython.rtyper.lltypesystem import lltype
from rpython.rtyper.lltypesystem.lloperation import llop
import native
from errors import *

#temporary hack - meh
castlist = {
  'VOID':  {},
  'OBJECT':{'OBJECT':100},
  'BOOL':  {'BOOL':0},
  'CHAR':  {'CHAR':0},
  'INT32': {'BOOL':5,  'INT32':0, 'INT64':6},
  'INT64': {'BOOL':9,  'INT32':4, 'INT64':0},
  'FLOAT': {'BOOL':10, 'INT32':5, 'INT64':3, 'FLOAT':0},
  'STRING':{'STRING':0,'CHAR':5},
  'ARRAY': {},
  'RECORD': {}
}

def castable(arg,param):
  return (arg in castlist[param]) or ('OBJECT' in castlist[param]) or (arg == 'OBJECT')

def castvalue(arg,param):
  if arg in castlist[param]:
    return castlist[param][arg]
  elif 'OBJECT' in castlist[param]:
    return castlist[param]['OBJECT']
  elif arg == 'OBJECT':
    return castlist['OBJECT']['OBJECT']
  else:
    return 0xFFFF
  
def fdiv(x,y):
  if y == 0: raise RuntimeError('Division by Zero')
  return x/y
  
# root object -----------------------------------------------------
class TObject(object):
    def __init__(self): pass
    
    # --| basics |--------------------------------------------
    def copy(self): raise NotImplementedError()
    def softcopy(self): raise NotImplementedError()
    
    # --| .... |--
    def asInt(self):   raise RuntimeError("%s can't be converted to Int" % self.__class__.__name__)
    def asInt32(self): raise RuntimeError("%s can't be converted to Int32" % self.__class__.__name__)
    def asInt64(self): raise RuntimeError("%s can't be converted to Int64" % self.__class__.__name__)
    def asFloat(self): raise RuntimeError("%s can't be converted to Float" % self.__class__.__name__)
    def asBool(self):  raise RuntimeError("%s can't be converted to Bool" % self.__class__.__name__)
    def asString(self):raise RuntimeError("%s can't be converted to String" % self.__class__.__name__)
    def asChar(self):  raise RuntimeError("%s can't be converted to Char" % self.__class__.__name__)
    def asArray(self): raise RuntimeError("%s can't be converted to Array" % self.__class__.__name__)
    
    # --| .... |--
    def index(self, index): raise RuntimeError('%s does not support indexing' % self.__class__.__name__)
    
    # --| .... |--
    @staticmethod
    def new(extra=None): return TObject()
    def printable(self): return ''
    def __repr__(self):  return ''
    
    
    # --| assignment |----------------------------------------
    def ASGN(self,right):     raise PException("%s doesn't support assignment-operations" % self.__class__.__name__)
    def ASGN_ADD(self,right): raise PException("%s doesn't support assignment-operations" % self.__class__.__name__)
    def ASGN_SUB(self,right): raise PException("%s doesn't support assignment-operations" % self.__class__.__name__)
    def ASGN_MUL(self,right): raise PException("%s doesn't support assignment-operations" % self.__class__.__name__)
    def ASGN_DIV(self,right): raise PException("%s doesn't support assignment-operations" % self.__class__.__name__)
    
    # --| arithmetic |----------------------------------------
    def ADD(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TFloat(self.asFloat() + right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() + right.asInt64())
      elif isinstance(self, TInt32) or isinstance(right, TInt32):
        return TInt(self.asInt32() + right.asInt32())
      else:
        return TString(self.asString() + right.asString())
        
    def SUB(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TFloat(self.asFloat() - right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() - right.asInt64())
      else:
        return TInt32(self.asInt32() - right.asInt32())
        
    def MUL(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TFloat(self.asFloat() * right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() * right.asInt64())
      else:
        return TInt32(self.asInt32() * right.asInt32())
        
    def DIV(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TFloat(fdiv(self.asFloat(), right.asFloat()))
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(native.Int64(fdiv(self.asFloat(), right.asFloat())))
      else:
        return TInt32(native.Int32(fdiv(self.asFloat(), right.asFloat())))
        
    def FDIV(self,right):
      r = right.asFloat()
      if r == 0: raise RuntimeError('Division by Zero')
      return TFloat(self.asFloat() / right.asFloat())
      
    def MOD(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        a = self.asFloat()
        b = right.asFloat()
        return TFloat(a - int(a / b) * b)
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        a = self.asInt64()
        b = right.asInt64()
        return TInt64(a - native.Int64(a / b) * b)
      else:
        a = self.asInt32()
        b = right.asInt32()
        return TInt(a - native.Int32(a / b) * b)

    def POW(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        v0 = self.asFloat()
        v1 = right.asFloat()
        if v1 == 2: return TFloat(v0*v0)
        elif v1 == 3: return TFloat(v0*v0*v0)
        return TFloat(pow(v0, v1))
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        v0 = self.asInt64()
        v1 = right.asInt64()
        if v1 == 2: return TInt64(v0*v0)
        elif v1 == 3: return TInt64(v0*v0*v0)
        return TInt64(native.Int64(pow(v0, v1)))
      else:
        v0 = self.asInt32()
        v1 = right.asInt32()
        if v1 == 2: return TInt32(v0*v0)
        elif v1 == 3: return TInt32(v0*v0*v0)
        return TInt64(native.Int32(pow(v0, v1)))
      
    def SHR(self,right):
      if isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() >> right.asInt64())
      else:
        return TInt32(self.asInt32() >> right.asInt32())
        
    def SHL(self,right):
      if isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() << right.asInt64())
      else:
        return TInt32(self.asInt32() << right.asInt32())
        
    def BAND(self,right):
      if isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() & right.asInt64())
      else:
        return TInt32(self.asInt32() & right.asInt32())
        
    def BOR(self,right):
      if isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() | right.asInt64())
      else:
        return TInt32(self.asInt32() | right.asInt32())
        
    def BXOR(self,right):
      if isinstance(self, TInt64) or isinstance(right, TInt64):
        return TInt64(self.asInt64() ^ right.asInt64())
      else:
        return TInt32(self.asInt32() ^ right.asInt32())
        
      
    # --| comparable |----------------------------------------
    def EQ(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TBool(self.asFloat() == right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TBool(self.asInt64() == right.asInt64())
      else:
        return TBool(self.asInt32() == right.asInt32())
    
    def NEQ(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TBool(self.asFloat() != right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TBool(self.asInt64() != right.asInt64())
      else:
        return TBool(self.asInt32() != right.asInt32())
      
    def LT(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TBool(self.asFloat() < right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TBool(self.asInt64() < right.asInt64())
      else:
        return TBool(self.asInt32() < right.asInt32())
      
    def GT(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TBool(self.asFloat() > right.asFloat())
      elif isinstance(self, TInt) or isinstance(right, TInt):
        return TBool(self.asInt64() > right.asInt64())
      else:
        return TBool(self.asInt32() > right.asInt32())
        
    def LTE(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TBool(self.asFloat() <= right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TBool(self.asInt64() <= right.asInt64())
      else:
        return TBool(self.asInt32() <= right.asInt32())
      
    def GTE(self,right):
      if isinstance(self, TFloat) or isinstance(right, TFloat):
        return TBool(self.asFloat() >= right.asFloat())
      elif isinstance(self, TInt64) or isinstance(right, TInt64):
        return TBool(self.asInt64() >= right.asInt64())
      else:
        return TBool(self.asInt32() >= right.asInt32())


    # --| chaining |------------------------------------------
    def AND(self,right):
      return TBool(self.asBool() and right.asBool())
      
    def OR(self,right):
      return TBool(self.asBool() or right.asBool())

    def XOR(self,right):
      return TBool(self.asBool() ^ right.asBool())
      
      
    # --| other |---------------------------------------------
    def UADD(self):
      return self.softcopy()

    def USUB(self):
      if isinstance(self, TFloat):
        return TFloat(-self.asFloat())
      elif isinstance(self, TInt32):
        return TInt32(-self.asInt32())
      elif isinstance(self, TInt64):
        return TInt64(-self.asInt64())
      raise NotImplementedError

    def NOT(self):
      return TBool(not self.asBool())
  
  
# void object ----------------------------------------------
class Void(TObject):
    def copy(self): return Void()
    def softcopy(self): return Void()

    # --| .... |--
    @staticmethod
    def new(extra=None): return Void()
    def printable(self): raise PException("%s doesn't support printing" % self.__class__.__name__)
    def __repr__(self): return 'void'
    

# numeric base object --------------------------------------    
class Numeric(TObject):
  def __init__(self): pass
  def asFloat(self): return 0.0  
    

# boolean object -------------------------------------------
class TBool(TObject):
    def __init__(self, val):
      assert isinstance(val,bool)
      self.val = val

    def copy(self): return TBool(self.val)
    def softcopy(self): return TBool(self.val)
    
    # --| .... |--
    def asInt(self):   return native.Int(self.val)
    def asInt32(self): return native.Int32(self.val)
    def asInt64(self): return native.Int64(self.val)
    def asFloat(self): return float(self.val)
    def asBool(self):  return self.val
    
    # --| .... |--
    def ASGN(self,other):
      self.val = other.asBool()

    # --| .... |--
    @staticmethod
    def new(extra=None): return TBool(False)
    def printable(self): return 'False' if self.val == 0 else 'True'
    def __repr__(self): return 'bool('+str(self.val != 0)+')'
  

# char object -----------------------------------------------------
class TChar(TObject):
    def __init__(self, val):
      assert isinstance(val,str)
      self.val = val

    def copy(self): return TChar(self.val)
    def softcopy(self): return TChar(self.val)
    
    # --| .... |--
    def asBool(self):  return ord(self.val) != 0
    def asString(self):return TString.fromStr(str(self.val))
    def asChar(self):  return self.val
    
    # --| .... |--
    def ASGN(self,other):
      self.val = other.asChar()

    # --| .... |--
    @staticmethod
    def new(extra=None): return TChar(chr(0))
    def printable(self): return self.val
    def __repr__(self): return 'char('+self.val+')'


# integer object (32 bit) -----------------------------------------------------
class TInt32(Numeric):
    def __init__(self, val):
      assert isinstance(val, native.Int32)
      self.val = val

    def copy(self): return TInt32(self.val)
    def softcopy(self): return TInt32(self.val)
    
    # --| .... |--
    def asInt(self):   return native.Int(self.val)
    def asInt32(self): return self.val
    def asInt64(self): return native.Int64(self.val)
    def asFloat(self): return float(self.val)
    def asBool(self):  return self.val != 0
    def asString(self):return TString.fromStr(str(self.val))
    def asChar(self):  return chr(self.val) if 0 <= self.val <= 255 else '\0'
    
    # --| .... |--
    def ASGN(self,other): self.val = other.asInt32()
    def ASGN_ADD(self,other): self.val += other.asInt32()
    def ASGN_SUB(self,other): self.val -= other.asInt32()
    def ASGN_MUL(self,other): self.val *= other.asInt32()
    def ASGN_DIV(self,other): self.val = native.Int32(float(self.val) / other.asFloat())
    
    # --| .... |--
    @staticmethod
    def new(extra=None): return TInt32(native.Int32(0))
    def printable(self): return str(self.val)
    def __repr__(self): return 'int32('+str(self.val)+')'




# integer object (64 bit) -----------------------------------------------------
class TInt64(Numeric):
    def __init__(self, val):
      assert isinstance(val, native.Int64)
      self.val = val

    def copy(self): return TInt64(self.val)
    def softcopy(self): return TInt64(self.val)
    
    # --| .... |--
    def asInt(self):   return native.Int(self.val)
    def asInt32(self): return native.Int32(self.val)
    def asInt64(self): return self.val
    def asFloat(self): return float(self.val)
    def asBool(self):  return self.val != 0
    def asString(self):return TString.fromStr(str(self.val))
    def asChar(self):  return chr(self.val) if 0 <= self.val <= 255 else '\0'
    
    # --| .... |--
    def ASGN(self,other): self.val = other.asInt64()
    def ASGN_ADD(self,other): self.val += other.asInt64()
    def ASGN_SUB(self,other): self.val -= other.asInt64()
    def ASGN_MUL(self,other): self.val *= other.asInt64()
    def ASGN_DIV(self,other): self.val = native.Int64(float(self.val) / other.asFloat())
    
    # --| .... |--
    @staticmethod
    def new(extra=None): return TInt64(native.Int64(0))
    def printable(self): return str(self.val)
    def __repr__(self): return 'int64('+str(self.val)+')'
   

if native.native_size == 32:
  TInt = TInt32
else:
  TInt = TInt64



# float object -----------------------------------------------------
class TFloat(Numeric):
    def __init__(self, val):
      assert isinstance(val, float)
      self.val = val

    def copy(self): return TFloat(self.val)
    def softcopy(self): return TFloat(self.val)
    
    # --| .... |--
    def asFloat(self): return self.val
    def asBool(self):  return self.val != 0
    
    # --| .... |--
    def ASGN(self,other): self.val = other.asFloat()
    def ASGN_ADD(self,other): self.val += other.asFloat()
    def ASGN_SUB(self,other): self.val -= other.asFloat()
    def ASGN_MUL(self,other): self.val *= other.asFloat()
    def ASGN_DIV(self,other): self.val /= other.asFloat()
    
    # --| .... |--
    @staticmethod
    def new(extra=None): return TFloat(0.0)
    def printable(self): return str(self.val)
    def __repr__(self): return 'float('+str(self.val)+')'



# string object -----------------------------------------------------
class TString(TObject):
    def __init__(self, val):
      assert isinstance(val, list)
      self.val = val
      
    def len(self): 
      return len(self.val)
      
    def copy(self):
      return TString([char.copy() for char in self.val])
    
    def softcopy(self):
      return TString(self.val[:])
    
    # --| .... |--
    def asBool(self):  return len(self.val) != 0
    def asString(self):return self.val
    def asChar(self): 
      if len(self.val) == 1: 
        return self.val[0].val
      else:
        raise PException("Strings longer then 1 character can't be converted to a Char" % self.__class__.__name__)
    
    # --| .... |--
    def ASGN(self,other):
      self.val = other.asString()

    def EQ(self,other):
      assert isinstance(other, TString)
      if self.len() != other.len(): 
        return TBool(False)
      for i in range(self.len()):
        if self.val[i].val != other.val[i].val: return TBool(False)
      return TBool(True)

    def NEQ(self,other):
      return TBool(not self.EQ(other).val)

    def index(self, index):
      i = index.asInt()
      if (i >= len(self.val)) or (i < 0): 
        raise RuntimeError('Index out of range: Index: %d, Size: %d'% (i, len(self.val)))
      return self.val[i]
    
    # --| .... |--
    @staticmethod
    def new(extra=None): return TString([])
    def printable(self): 
      str = ''
      for x in self.val: str += x.val
      return str
    def __repr__(self): return 'str('+self.printable()+')'
    
    @staticmethod
    def fromStr(str):
      return [TChar(x) for x in str]


# record object -----------------------------------------------------
class TRecord(TObject):
    def __init__(self, fields):
      assert isinstance(fields, list)
      self.fields = fields
      
    def copy(self):
      return TRecord([field.copy() for field in self.fields])
    
    def softcopy(self):
      return TRecord([field.softcopy() for field in self.fields])
    
    # --| .... |--
    def ASGN(self,other): 
      #XXX compatibility should be checked at compile-time
      assert isinstance(other, TRecord)
      if len(other.fields) == len(self.fields): #dummy check - fix me
        self.fields = other.softcopy().fields
      else:
        raise RuntimeError("Can't assign "+other.printable()+" to "+self.printable())
     
    # --| .... |--
    def get_field(self, id):
      return self.fields[id]
    
    # --| .... |--
    @staticmethod
    def new(extra=None):
      if isinstance(extra, TRecord):
        return extra.softcopy()
      raise NotImplementedError
      
    def printable(self): 
      str = '['
      for i,field in enumerate(self.fields):
        str += field.printable()
        if i != len(self.fields)-1: str += ', '
      return str + ']'

    def __repr__(self): 
      return 'record('+', '.join([x.printable() for x in self.fields])+')'


# array object -----------------------------------------------------
class TArray(TObject):
    def __init__(self, val, dtype):
      assert isinstance(val, list)
      self.val = val
      self.dtype = dtype
      
    def len(self): 
      return len(self.val)
      
    def copy(self):
      return TArray([v.copy() for v in self.val], self.dtype)
    
    def softcopy(self):
      return TArray(self.val[:], self.dtype) #XXX - shit slow
    
    # --| .... |--
    def asBool(self):  return len(self.val) != 0
    def asArray(self): return self.val
    
    # --| .... |--
    def ASGN(self,other):
      self.val = other.asArray()

    def index(self, index):
      idx = index.asInt()
      if (idx >= len(self.val)) or (idx < 0): 
        raise RuntimeError('Index out of range: Index: %d, Size: %d'% (idx, len(self.val)))
      
      #if not yet initialized; initialize it now
      if self.val[idx] is None:
        if isinstance(self.dtype, TArray): 
          self.val[idx] = self.dtype.new(self.dtype.dtype)
        elif isinstance(self.dtype, TRecord): 
          self.val[idx] = self.dtype.new(self.dtype)
        else:
          self.val[idx] = self.dtype.new(None)

      return self.val[idx]
      
    def findex(self, index):
      #if not yet initialized; initialize it now
      if self.val[index] is None:
        if isinstance(self.dtype, TArray): 
          self.val[index] = self.dtype.new(self.dtype.dtype)
        elif isinstance(self.dtype, TRecord): 
          self.val[index] = self.dtype.new(self.dtype)
        else:
          self.val[index] = self.dtype.new(None)

      return self.val[index]
    
    # --| .... |--
    @staticmethod
    def new(extra=None): return TArray([], extra)

    def printable(self): 
      data = '['
      for i,x in enumerate(self.val): 
        if x is None:
          data += 'Null'
        else:
          data += x.printable()
        if i < len(self.val)-1: data += ', '
      return data+']'
      
    def __repr__(self): 
      return 'array('+self.printable()+','+str(self.dtype)+')'
      

# function base -----------------------------------------------------
class Function(TObject):
    def call(): return TObject() 
    def add_argv(self, obj): pass


# NativeFunction -----------------
class NativeFunction(Function):
    def __init__(self, func, n_args):
      self.func = func
      self.n_args = n_args

    def copy(self): return NativeFunction(self.func, self.n_args)
    def softcopy(self): return NativeFunction(self.func, self.n_args)
    
    def call(self, arguments):
      return self.func(arguments)

    @staticmethod
    def new(extra=None): 
      raise NotImplementedError

    def printable(self):
      return 'function()'
    
    def __repr__(self):
      return 'NativeFunction()'
    
    
class ScriptFunction(Function):
    def __init__(self, program, n_args, passby):
      self.program = program
      self.n_args = n_args
      self.passby = passby
      
    def copy(self): return ScriptFunction(self.program, self.n_args, self.passby)
    def softcopy(self): return ScriptFunction(self.program, self.n_args, self.passby)
    
    def call(self, arguments):
      raise NotImplementedError

    @staticmethod
    def new(extra=None): 
      raise NotImplementedError

    def printable(self):
      return 'function()'
    
    def __repr__(self):
      return 'ScriptFunction()'
    
    
    
    
#---------------------------------------------------------------------
#-----------------------------------------------------------------------
#---------------------------------------------------------------------
class OBJECT(object):
    def __init__(self): pass
    def emit(self): return TObject()
    def get_field(self,field): raise InternalError('OBJECT has no attribute "%s"' %field)
    def get_field_id(self,field): raise InternalError('OBJECT has no attribute "%s"' %field)
    def type(self): return self.__class__.__name__
    def equal(self, other): return self.type() == other.type()
    def printable(self): return self.__class__.__name__.lower()
    
    
class VOID(OBJECT):
    def emit(self): return Void()
    def equal(self, other): return False
    
class BOOL(OBJECT):
    def __init__(self,val=False): self.val = val
    def emit(self): return TBool(self.val)
    
class CHAR(OBJECT):
    def __init__(self,val='\0'): self.val = val
    def emit(self): return TChar(self.val)
    
class INT32(OBJECT):
    def __init__(self,val=0): self.val = val
    def emit(self): return TInt32(native.Int32(self.val))
        
class INT64(OBJECT):
    def __init__(self,val=0): self.val = val
    def emit(self): return TInt64(native.Int64(self.val))
   
if native.native_size == 32:
  INT = INT32
else:
  INT = INT64
    
class FLOAT(OBJECT):
    def __init__(self,val=0.0): self.val = val
    def emit(self): return TFloat(float(self.val))
    
class STRING(OBJECT):
    def __init__(self,val=''): self.val = val
    def emit(self): return TString(TString.fromStr(self.val))
    
class ARRAY(OBJECT):
    def __init__(self,val=[], dtype=OBJECT(), name=''): 
      self.val = val
      self.dtype = dtype
      self.name  = name

    def type(self):
      return self.name.upper()
    
    def emit(self): 
      return TArray(self.val[:], self.dtype.emit())
    
    def equal(self, other): 
      if not isinstance(other, ARRAY): return False
      return self.dtype.equal(other.dtype)
      
    def printable(self):
      return 'array of %s' % self.dtype.printable()
    
class RECORD(OBJECT):
    def __init__(self, fields, names):
      assert isinstance(names, list)
      assert isinstance(fields, list)
      self.names = names
      self.fields = fields
    
    def emit(self):
      return TRecord([f.emit() for f in self.fields])
    
    def get_field(self,field):
      for i,n in enumerate(self.names):
        if n.lower() == field:
          return self.fields[i]
      raise CompilationError('Record [%s] has no attribute `%s`' % (','.join(self.names), field));

    def get_field_id(self,field):
      for i,n in enumerate(self.names):
        if n.lower() == field:
          return i
      raise CompilationError('Record [%s] has no attribute `%s`' % (','.join(self.names), field));
      
    def equal(self, other):
      if not(isinstance(other,RECORD)) or (len(other.names) != len(self.names)): 
        return False

      for i in range(len(self.names)):
        if (not self.names[i] == other.names[i]) or \
           (not self.fields[i].equal(other.fields[i])): 
            return False
      return True
      
    def printable(self):
      l = ['%s:%s' % (self.names[i], self.fields[i].printable()) for i in range(len(self.names))]
      return 'record(%s)' % '; '.join(l)
      
class NATIVE_FUNC(OBJECT):
    def __init__(self, name, argtypes, restype, method, overload=False): 
      assert isinstance(name, str)
      assert isinstance(argtypes, list)
      assert isinstance(restype, OBJECT)
      
      self.name = name
      self.argtypes = argtypes
      self.restype  = restype
      self.method = method
      self.overload = overload
      
    def emit(self):
      return NativeFunction(self.method, len(self.argtypes))
      

class FUNCTION(OBJECT):
    def __init__(self, name, argtypes, restype, passby, program, overload=False): 
      assert isinstance(name, str)
      assert isinstance(restype, OBJECT)
      
      self.name = name
      self.argtypes = argtypes
      self.restype  = restype
      self.passby   = passby
      self.program  = program
      self.overload = overload
      
    def emit(self):
      return ScriptFunction(self.program, len(self.argtypes), self.passby)

