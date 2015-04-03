from rpython.rlib import jit

ARGSTACK_MIN = 32
class Frame(object):
    _virtualizable_ = [
      'stack[*]', 
      'stack_pos',
      'vars[*]',
      'arg_pos',
      'argstack_size'
    ]
    
    def __init__(self, bc, stacksize):
        self = jit.hint(self, fresh_virtualizable=True, access_directly=True)
        self.stack = [None] * stacksize
        self.stack_pos = 0
        self.globs = bc.globals
        self.vars  = [None] * bc.n_vars
        
        #resizeable stack for function args -->
        self.arg_pos = 0
        self.argstack_size = ARGSTACK_MIN
        self.argstack = [None] * ARGSTACK_MIN 

    def push(self, v):
        pos = jit.hint(self.stack_pos, promote=True)
        assert pos >= 0, 'Stack underflow'
        self.stack[pos] = v
        self.stack_pos = pos + 1
    
    def pop(self):
        pos = jit.hint(self.stack_pos, promote=True)
        new_pos = pos - 1
        assert new_pos >= 0, 'Stack underflow'
        v = self.stack[new_pos]
        self.stack_pos = new_pos
        return v
        
    def top(self):
        pos = jit.hint(self.stack_pos, promote=True)
        tmp = pos - 1
        assert tmp >= 0, 'Stack underflow'
        return self.stack[tmp]
        
    # function arguments - resizeable stack
    # -------------------------------------------------------------
    def push_arg(self, v):
        argpos = jit.hint(self.arg_pos, promote=True)
        assert argpos >= 0, 'Argstack underflow'
        self.argstack[argpos] = v
        
        #if upsize
        if argpos == self.argstack_size:
          self.argstack.extend([None]*self.argstack_size)
          self.argstack_size = self.argstack_size << 1
        
        self.arg_pos = argpos + 1
    
    def pop_arg(self):
        argpos = jit.hint(self.arg_pos, promote=True)
        new_pos = argpos - 1
        assert new_pos >= 0, 'Argstack underflow'
        result = self.argstack[new_pos]
        self.arg_pos = new_pos
        
        #if downsize
        size = jit.hint(self.argstack_size, promote=True)
        hsize = size >> 1
        if (hsize >= ARGSTACK_MIN) and (self.arg_pos < hsize):
          self.argstack = self.argstack[:hsize]
          self.argstack_size = hsize
        
        return result
        