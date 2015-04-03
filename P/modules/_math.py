import math
from P.dtypes import *
import P.native

def min(x,y): return x if x < y else y
def max(x,y): return x if x > y else y

def w_absI32(args): 
  return TInt32(native.Int32(abs(args[0].asInt32())))
  
def w_absI64(args): 
  return TInt64(native.Int64(abs(args[0].asInt64())))
  
def w_absF(args): 
  return TFloat(abs(args[0].asFloat()))
  
def w_ceil(args):
  return TInt64(native.Int64(math.ceil(args[0].asFloat())))
  
def w_floor(args):
  return TInt64(native.Int64(math.floor(args[0].asFloat())))
  
def w_round(args):
  return TInt64(native.Int64(math.floor(args[0].asFloat()+0.5)))
  
def w_trunc(args):
  return TInt64(native.Int64(args[0].asFloat()))
  
def w_sqrt(args):
  return TFloat(math.sqrt(args[0].asFloat()))
  
def w_pow(args):
  return TInt64(native.Int64(math.pow(args[0].asInt64(),args[1].asInt64())))
  
def w_powF(args):
  return TFloat(math.pow(args[0].asFloat(),args[1].asFloat()))
  
def w_minI32(args):
  return TInt32(native.Int32(min(args[0].asInt32(),args[1].asInt32())))
  
def w_minI64(args):
  return TInt64(native.Int64(min(args[0].asInt64(),args[1].asInt64())))
  
def w_minF(args):
  return TFloat(min(args[0].asFloat(),args[1].asFloat()))
  
def w_maxI32(args):
  return TInt32(native.Int32(max(args[0].asInt32(),args[1].asInt32())))
  
def w_maxI64(args):
  return TInt64(native.Int64(max(args[0].asInt64(),args[1].asInt64())))
  
def w_maxF(args): 
  return TFloat(max(args[0].asFloat(),args[1].asFloat()))

def w_sqrI32(args): 
  return TInt32(native.Int32(args[0].asInt32()*args[0].asInt32()))

def w_sqrI64(args): 
  return TInt64(native.Int64(args[0].asInt64()*args[0].asInt64()))
  
def w_sqrF(args): 
  return TFloat(args[0].asFloat()*args[0].asFloat())

exports = [
  NATIVE_FUNC('Abs',  [INT32()], INT32(), w_absI32),
  NATIVE_FUNC('Abs',  [INT64()], INT64(), w_absI64, overload=True),
  NATIVE_FUNC('Abs',  [FLOAT()], FLOAT(), w_absF,   overload=True),
  NATIVE_FUNC('Ceil', [FLOAT()], INT64(), w_ceil),
  NATIVE_FUNC('Floor',[FLOAT()], INT64(), w_floor),
  NATIVE_FUNC('Round',[FLOAT()], INT64(), w_round),
  NATIVE_FUNC('Trunc',[FLOAT()], INT64(), w_trunc),
  NATIVE_FUNC('Sqrt', [FLOAT()], FLOAT(), w_sqrt),
  NATIVE_FUNC('Pow',  [INT64(), INT64()], INT64(), w_pow),
  NATIVE_FUNC('Pow',  [FLOAT(), FLOAT()], FLOAT(), w_powF, overload=True),
  NATIVE_FUNC('Min',  [FLOAT(), FLOAT()], FLOAT(), w_minF),
  NATIVE_FUNC('Min',  [INT32(), INT32()], INT32(), w_minI32, overload=True),
  NATIVE_FUNC('Min',  [INT64(), INT64()], INT64(), w_minI64, overload=True),
  NATIVE_FUNC('Max',  [FLOAT(), FLOAT()], FLOAT(), w_maxF),
  NATIVE_FUNC('Max',  [INT32(), INT32()], INT32(), w_maxI32, overload=True),
  NATIVE_FUNC('Max',  [INT64(), INT64()], INT64(), w_maxI64, overload=True),
  NATIVE_FUNC('Sqr',  [INT32()], INT32(), w_sqrI32),
  NATIVE_FUNC('Sqr',  [INT64()], INT64(), w_sqrI64, overload=True),
  NATIVE_FUNC('Sqr',  [FLOAT()], FLOAT(), w_sqrF,   overload=True),
]