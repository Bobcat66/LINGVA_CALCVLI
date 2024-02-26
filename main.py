from LINGVA_CALCVLI_EXECVTER import executer

file = "test1.spqr"

f = open(file)
executer.printCode(f.read())
executer.execute(f.read())
f.close()