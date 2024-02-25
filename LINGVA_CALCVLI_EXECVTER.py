from LINGVA_CALCVLI_PARSER import parser

class compiler():
    def __init__(self) -> None:
        self.parser = parser
    def compile(self,code):
        parsedCode = self.parser.parse(code)
        for statement in parsedCode:
            print(statement)

compiler = compiler()

compiler.compile()