from rpython.rlib.rarithmetic import build_int, _get_bitsize

native_size = _get_bitsize('P') #I assume this works..

Int = build_int('Int', True, native_size)
Int32  = build_int('Int32', True, 32)
UInt32 = build_int('UInt32', False, 32)
Int64  = build_int('Int64', True, 64)
UInt64 = build_int('UInt64', False, 64)

def Char(c='\0'):
    assert isinstance(c, str)
    return c

def StrToInt64(x):
    '''
      A simple conversion from string to Int64.
      Supports base16 hex-string by appending "$" to the beginning of 
      the string.
    '''
    int_digits = '0123456789'
    hex_digits = '0123456789ABCDEF'
    i = 0;
    sign = 1;
    if (x[i] == '-'):
        sign = -1;
        i += 1;
    elif (x[i] == '+'):
        i += 1;
      
    value = Int64(0);
    if x[i] == '$':
      i += 1;
      for i in range(i,len(x)):
        if not(x[i] in hex_digits): return 0
        diff = 0
        if x[i] in 'ABCDEF': diff = ord('A') - ord('9') - 1
        value = Int64(value * 16 + (ord(x[i]) - ord('0') - diff));
    else:
      for i in range(i,len(x)):
        if not(x[i] in int_digits): return 0
        value = Int64(value * 10 + (ord(x[i]) - ord('0')));
 
    return Int64(sign * value);
   