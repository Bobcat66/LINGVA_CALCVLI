import math

def to_RomNum(n: int) -> str:
    if n == 0:
        return "NVLLA"
    out = ""
    for i in range(n // 1000):
        out += "M"
    n %= 1000
    if n >= 900:
        out += "CM"
        n -= 900
    if n >= 500:
        out += "D"
        n -= 500
    if n >= 400:
        out += "CD"
        n -= 400
    for i in range(n // 100):
        out += "C"
    n %= 100
    if n >= 90:
        out += "XC"
        n -= 90
    if n >= 50:
        out += "L"
        n -= 50
    if n >= 40:
        out += "XL"
        n -= 40
    for i in range(n // 10):
        out += "X"
    n %= 10
    if n >= 9:
        out += "IX"
        n -= 9
    if n >= 5:
        out += "V"
        n -= 5
    n %= 5
    for i in range(n):
        out += "I"
    return out

def to_decimal(n: str) -> int:
    if n == "NVLLA":
        return 0
    out = 0
    while len(n) > 1:
        first = n[0]
        second = n[1]
        match (first,second):
            case ('M',*other):
                out += 1000
                n = n[1:]
            case ('D',*other):
                out += 500
                n = n[1:]
            case ('C','M'):
                out += 900
                n = n[2:]
            case ('C','D'):
                out += 400
                n = n[2:]
            case ('C',*other):
                out += 100
                n = n[1:]
            case ('L',*other):
                out += 50
                n = n[1:]
            case ('X','C'):
                out += 90
                n = n[2:]
            case ('X','L'):
                out += 40
                n = n[2:]
            case ('X',*other):
                out += 10
                n = n[1:]
            case ('V',*other):
                out += 5
                n = n[1:]
            case ('I','X'):
                out += 9
                n = n[2:]
            case ('I','V'):
                out += 4
                n = n[2:]
            case ('I',*other):
                out += 1
                n = n[1:]
    if len(n) == 1:
        match (n[0]):
            case 'M':
                out += 1000
            case 'D':
                out += 500
            case 'C':
                out += 100
            case 'L':
                out += 50
            case 'X':
                out += 10
            case 'V':
                out += 5
            case 'I':
                out += 1
    return out

if __name__ == "__main__":
    print(to_RomNum(2023))
    print(to_decimal("MDCCCXLIX"))
    

    