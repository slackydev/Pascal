from P.dtypes import *
import P.native
from rpython.rlib.rrandom import Random
from rpython.rlib.rarithmetic import intmask
from time import time,sleep

class rand(object):
    def seed(self, seed):
        self.r = Random(seed)
    def random(self):
        return self.r.random()
    def randint(self, a, b):
        r32 = intmask(self.r.genrand32())
        r = a + r32 % (b - a)
        return intmask(r)

random = rand()
random.seed(int(time()*1000))

def Int(args):  
  x = args[0]
  if isinstance(x, TChar): return TInt(native.Int(int(x.val)))
  return TInt(native.Int(x.asInt()))
  
def Int32(args):
  x = args[0]
  if isinstance(x, TChar): return TInt32(native.Int32(int(x.val)))
  return TInt32(native.Int32(x.asInt32()))
  
def Int64(args):
  x = args[0]
  if isinstance(x, TChar): return TInt64(native.Int64(int(x.val)))
  return TInt64(native.Int64(x.asInt64()))
  
def Float(args):
  x = args[0]
  if isinstance(x, TChar): return TFloat(float(int(x.val)))
  return TFloat(x.asFloat())
  
def Bool(args): 
  return TBool(args[0].asBool())

def String(args): 
  return TString([TChar(x) for x in args[0].printable()])
  
# -------------------------------------
def Length(args):
  arr = args[0]
  assert isinstance(arr, TArray)
  return TInt(native.Int(arr.len()))

def High(args):
  arr = args[0]
  assert isinstance(arr, TArray)
  return TInt(native.Int(arr.len()-1))
  
def SetLength(args):
  arr = args[0]
  size = args[1].asInt()
  assert size >= 0,'Size < 0'
  assert isinstance(arr, TArray),'Expected array'
  if size > len(arr.val):
    arr.val.extend([None]*(size-arr.len())) #XXX!!!
  else:
    del arr.val[size:]
  
def Append(args): 
  arr = args[0]
  item= args[1]
  assert isinstance(arr, TArray),'Expected array'
  arr.val.append(item.softcopy())

def Insert(args):
  arr = args[0]
  idx = args[1].asInt()
  item= args[2]
  assert isinstance(arr, TArray),'Expected array'
  assert idx >= 0,'Index < 0'
  arr.val.insert(idx,item.softcopy())
  
def Extend(args): 
  arr = args[0]
  item= args[1]
  assert isinstance(arr, TArray)
  assert isinstance(item, TArray)
  arr.val.extend(item.val[:])
  
def Remove(args): 
  arr = args[0]
  item= args[1]
  assert isinstance(arr, TArray),'Expected array'
  for i in range(arr.len()):
    if arr.findex(i).EQ(item).asBool():
      del arr.val[i]
      return
      
def Delete(args): 
  arr = args[0]
  idx = args[1]
  assert isinstance(arr, TArray),'Expected array'
  del arr.val[idx.asInt()]
  
def Copy(args):
  arg = args[0]
  return arg.softcopy()

def _sort(arr, left, right):
  i = left
  j = right
  pivot = arr.findex((left+right) >> 1)
  while True:
    while pivot.GT(arr.findex(i)).asBool(): i+=1;
    while pivot.LT(arr.findex(j)).asBool(): j-=1;
    if i<=j:
      tmp = arr.val[i]
      arr.val[i] = arr.val[j]
      arr.val[j] = tmp
      j-=1
      i+=1
    if (i>j): break;

  if (left < j): _sort(arr, left, j);
  if (i < right): _sort(arr, i, right);   
  
def Sort(args):
  arr = args[0]
  assert isinstance(arr, TArray),'Expected array'
  _sort(arr, 0,arr.len()-1)
  
# -------------------------------------  
def RandInt(args): 
  return TInt(native.Int(random.randint(args[0].asInt(), args[1].asInt())))

def Random(args): 
  return TFloat(random.random())

# -------------------------------------  
def Time(args): 
  return TInt64(native.Int64(time()*1000))  
  
def Wait(args): 
  return sleep(args[0].asFloat()/1000.0)
  
exports = [
  NATIVE_FUNC('Int',  [OBJECT()], INT(),   Int),
  NATIVE_FUNC('Int32',[OBJECT()], INT32(), Int32),
  NATIVE_FUNC('Int64',[OBJECT()], INT64(), Int64),
  NATIVE_FUNC('Float',[OBJECT()], FLOAT(), Float),
  NATIVE_FUNC('Bool', [OBJECT()], BOOL(), Bool),
  NATIVE_FUNC('String', [OBJECT()], STRING(), String),
  NATIVE_FUNC('Length', [OBJECT()], INT(), Length),
  NATIVE_FUNC('High', [OBJECT()], INT(), High),
  NATIVE_FUNC('SetLength', [OBJECT(), INT()], VOID(), SetLength),
  NATIVE_FUNC('Insert', [OBJECT(), OBJECT(), OBJECT()], VOID(), Insert),
  NATIVE_FUNC('Append', [OBJECT(), OBJECT()], VOID(), Append),
  NATIVE_FUNC('Extend', [OBJECT(), OBJECT()], VOID(), Extend),
  NATIVE_FUNC('Remove', [OBJECT(), OBJECT()], VOID(), Remove),
  NATIVE_FUNC('Delete', [OBJECT(), INT()], VOID(), Delete),
  NATIVE_FUNC('Copy', [OBJECT()], OBJECT(), Copy),
  NATIVE_FUNC('Sort', [OBJECT()], VOID(), Sort),
  NATIVE_FUNC('RandInt', [INT(), INT()], INT(), RandInt),
  NATIVE_FUNC('Random', [], FLOAT(), Random),
  NATIVE_FUNC('Time', [], INT64(), Time),
  NATIVE_FUNC('Wait', [INT()], VOID(), Wait)
]
