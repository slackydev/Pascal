# Pascal
A very simple interpreter for a pascal-derived language, written simply to learn the RPython compiler and toolchain. 
The interpreter is still lacking a lot of core features, and contains a lot of bugs.

To execute just run: `pascal.exe <path/to/myfile.pas>`
Compile-instructions are found in `main.py`, you will need the RPython-source.


Features
--------
- [x] Functions (needs more work)
- [x] Variables
- [x] If, Else, For, While, Repeat
- [x] Continue, Break, Exit, Pass
- [ ] Named constants
- [ ] Try, Except, Finally
- [ ] Case
- [ ] Directives


Basetypes [1]
---------
- [x] Int/Integer (native integer)
- [x] Int32
- [x] Int64
- [x] Float (64bit)
- [x] Char
- [x] String
- [x] Dynamic Arrays (iffy implementation)
- [x] Record (still needs some work)
- [ ] Enums
- [ ] "Variants"/dynamic datatype(?)

[1]: Implementation of these types are objects, but they store the specified datatype. 
