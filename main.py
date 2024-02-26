from LINGVA_CALCVLI_EXECVTER import executer

file = "test1.txt"

f = open(file)
executer.execute(f.read())
f.close()