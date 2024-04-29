import math
import fractions
from decimal import Decimal

def to_RomNum(n: int) -> str:
    #
    if n == 0:
        return "NVLLA"
    
    if isinstance(n,float):
        frac = fractions.Fraction(repr(n)) #Because RATIO's __str__() function calles to_RomNum on itself, calling repr() on n is necessary to prevent an infinite recursion
        out = "PARS "
        out += to_RomNum(frac.numerator)
        out += " "
        out += to_RomNum(frac.denominator)
        return out
    
    outList = []
    while n > 0:
        temp = n % 10000
        if temp > 3999:
            #3999 is the largest number that can be expressed with normal Roman numerals
            temp %= 1000
            outList.append(romnum_inner(temp))
            n //= 1000
        else:
            outList.append(romnum_inner(temp))
            n -= temp
            n //= 1000

    out = ""
    for i in range(len(outList)-1,0,-1):
        out += outList[i]
        out += "|"
    out += outList[0]
    return out

def romnum_inner(n):
    out = "M"*(n // 1000)
    n %= 1000
    #Hundreds
    if n >= 900:
        out += "CM"
        n -= 900
    if n >= 500:
        out += "D"
        n -= 500
    if n >= 400:
        out += "CD"
        n -= 400
    out += "C" * (n // 100)
    n %= 100
    #Tens
    if n >= 90:
        out += "XC"
        n -= 90
    if n >= 50:
        out += "L"
        n -= 50
    if n >= 40:
        out += "XL"
        n -= 40
    out += "X" * (n // 10)
    n %= 10
    #Ones
    if n >= 9:
        out += "IX"
        n -= 9
    if n >= 5:
        out += "V"
        n -= 5
    if n >= 4:
        out += "IV"
        n -= 4
    out += "I" * n
    return out

def to_decimal(n: str) -> int:
    if n == "NVLLA":
        return 0
    
    if n[0:4] == "PARS":
        temp = n.split( )
        return(to_decimal(temp[1])/to_decimal(temp[2]))
    
    nList = n.split('|')
    p = 0
    out = 0
    for i in range(len(nList)-1,-1,-1):
        temp = decimal_inner(nList[i])
        out += (temp * (1000 ** p))
        p += 1
    return out

def decimal_inner(n):
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
    print(to_RomNum(19356))
    print(to_decimal('MCCXXXIV|DLXVII|DCCCXC'))


    

    