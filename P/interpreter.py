# -*- coding: utf-8 -*- 
from dtypes import *
from bytecode import *
from errors import *
'''
  This little thingy executes our "bytecode".
'''
from rpython.rlib import jit
from sys import stdout
from frame import Frame

driver = jit.JitDriver(greens = ['pc', 'code', 'bc'],
                       reds = ['frame'],
                       virtualizables=['frame'])


class Interpreter(object):
  def __init__(self, bytecode, stacksize=6):
    self.bc    = bytecode
    self.frame = Frame(bytecode, stacksize)
  
  def run(self):
    bc    = self.bc
    frame = self.frame
    code  = self.bc.code
    pc = 0;

    while True: 
      # jit hint -> top of opcode dispatch
      driver.jit_merge_point(pc=pc, code=code, bc=bc, frame=frame)
      assert pc >= 0
      instr = code[pc]
      arg   = code[pc+1]
      assert arg >= 0
      pc += 2
      
      if instr == LOAD_VAR:      frame.push(frame.vars[arg])
      elif instr == LOAD_GLOBAL: frame.push(frame.globs[arg])
      elif instr == LOAD_CONST:  frame.push(bc.constants[arg])
      elif instr == STORE_COPY:  frame.vars[arg] = frame.pop().softcopy()
      elif instr == STORE_FAST:  frame.vars[arg] = frame.pop() #no copy
      elif instr == DISCARD_TOP: frame.pop();
      
      elif instr == JMP_IF_FALSE:
        if not frame.pop().asBool(): 
          pc = arg;
      elif instr == JMP_IF:
        if frame.pop().asBool(): 
          pc = arg;
      elif instr == JMP_BACK:
        pc = arg;
        # jit hint -> end of a loop
        driver.can_enter_jit(pc=pc, code=code, bc=bc, frame=frame)
      elif instr == JMP_FORWARD:
        pc = arg;
      elif instr == JMP_IF_NO_POP:
        if frame.top().asBool(): 
          pc = arg;
      elif instr == JMP_IF_FALSE_NO_POP:
        if not frame.top().asBool(): 
          pc = arg;

      elif instr == ASSIGN:
        right = frame.pop()
        left  = frame.pop()
        if   arg == 0: left.ASGN(right)
        elif arg == 1: left.ASGN_ADD(right)
        elif arg == 2: left.ASGN_SUB(right)
        elif arg == 3: left.ASGN_MUL(right)
        elif arg == 4: left.ASGN_DIV(right)
        frame.push( left )
      
      #binary
      elif instr == BIN_ADD:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.ADD(right) )
      elif instr == BIN_SUB:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.SUB(right) )
      elif instr == BIN_MUL:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.MUL(right) )
      elif instr == BIN_IDIV:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.DIV(right) )
      elif instr == BIN_FDIV:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.FDIV(right) )
      elif instr == BIN_MOD:
        right = frame.pop();
        left  = frame.pop();
        frame.push( left.MOD(right) );
      elif instr == BIN_POW:
        right = frame.pop();
        left  = frame.pop();
        frame.push( left.POW(right) );
      
      #comparison/equality
      elif instr == BIN_EQ:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.EQ(right) )
      elif instr == BIN_NEQ:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.NEQ(right) )
      elif instr == BIN_LT:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.LT(right) )
      elif instr == BIN_GT:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.GT(right) )
      elif instr == BIN_LTE:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.LTE(right) )
      elif instr == BIN_GTE:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.GTE(right) )
        
      #bitwise
      elif instr == BIT_SHL:
        right, left = frame.pop(), frame.pop()
        frame.push( left.SHL(right) )
      elif instr == BIT_SHR:
        right, left = frame.pop(), frame.pop()
        frame.push( left.SHR(right) )
      elif instr == BIT_AND:
        right, left = frame.pop(), frame.pop()
        frame.push( left.BAND(right) )
      elif instr == BIT_OR:
        right, left = frame.pop(), frame.pop()
        frame.push( left.BOR(right) )
      elif instr == BIT_XOR:
        right, left = frame.pop(), frame.pop()
        frame.push( left.BXOR(right) )
      
      #logical chain
      elif instr == BIN_AND:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.AND(right) )
      elif instr == BIN_OR:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.OR(right) )
      elif instr == BIN_XOR:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.XOR(right) )
  
      #unary
      elif instr == UNARY_ADD:
        left  = frame.pop()
        frame.push( left.UADD() )
      elif instr == UNARY_SUB:
        left  = frame.pop()
        frame.push( left.USUB() )
      elif instr == UNARY_NOT:
        left  = frame.pop()
        frame.push( left.NOT() )

      #other
      elif instr == INDEX:
        right = frame.pop()
        left  = frame.pop()
        frame.push( left.index(right) )
      elif instr == LOAD_FIELD:
        left  = frame.pop()
        frame.push( left.get_field(arg) )

      elif instr == NARG: #XXX
        frame.push_arg(frame.pop()) #push to the argument-stack
        
      elif instr == CALL:
        method = bc.functions[arg]
        if isinstance(method, NativeFunction):
          args = [frame.pop_arg() for x in range(method.n_args)]
          res = method.call(args)
          frame.push(res)
          
        elif isinstance(method, ScriptFunction):
          method.program.globals = [None]*bc.n_vars  #XXX
          program = Interpreter(method.program)
          for i in range(method.n_args):
            if method.passby[i] == BYVAL:
              program.frame.vars[i+1] = frame.pop_arg().softcopy()
            elif method.passby[i] == BYREF:
              program.frame.vars[i+1] = frame.pop_arg()
          
          res = program.run()
          frame.push(res)
        else:
          raise RuntimeError("Go away :(")
          
      elif instr == PRINT:
        text = [frame.pop_arg().printable() for x in range(arg)]
        print ' '.join(text)
          
      elif instr == RET:
        if len(frame.vars) > 0:
          return frame.vars[0]
        else:
          return None
      else:
        raise RuntimeError("Instruction * is not implemented")
  
  