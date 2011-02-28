iupac={'A':'A',
       'C':'C',
       'G':'G',
       'T':'T',
       'R':['A','G'],
       'Y':['C','T'],
       'S':['G','C'],
       'W':['A','T'],
       'K':['G','T'],
       'M':['A','C'],
       'B':['C','G','T'],
       'D':['A','G','T'],
       'H':['A','C','T'],
       'V':['A','C','T'],
       'N':['A','C','T','G']}

def iupac2base(word):
    try:
        return(iupac[word])
    except KeyError:
        return(word)

if __name__ == "__main__":
    import sys
    for i in sys.argv[1]:
        try:
            print i,iupac2base(i)
        except:
            print i
       
       
