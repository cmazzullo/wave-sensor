from numpy import f2py

with open("wspro88.f") as sourcefile:
    sourcecode = sourcefile.read()
    
f2py.compile(sourcecode)
# import wspro