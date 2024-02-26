from LINGVA_CALCVLI_EXECVTER import executer

file = "test1.spqr"

f = open(file)
executer.execute(f.read(),verbose=True)
f.close()