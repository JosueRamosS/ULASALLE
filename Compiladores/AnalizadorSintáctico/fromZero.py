# nonTerminals = ["PROGRAM", "FUNCTION'", "PARAMETERS", "MORE_PARAMETERS", "PARAMETER", "MAIN'"]
# terminals = ["DATATYPE", "IDENTIFIER", "OPAR", "CPAR", "OKEY", "STATEMENTS", "LOOPS", "IFELSES", "CKEY", "COMMA", "MAIN"]

# print(nonTerminals[3])
# print(terminals)

filename = 'fromZeroGrammar.txt'
with open(filename, 'r') as file:
    lines = file.readlines()
# print(lines)

def getNonTerminals(lines):
    nonTerminals = []
    for line in lines:
        parts = line.strip().split(' ->') # Parte la línea por '->' y elimina espacios en blanco a los lados
        if parts and parts[0].strip():  # Asegura que el elemento no esté vacío
            element = parts[0].strip()
            if element not in nonTerminals:
                nonTerminals.append(element)
    return nonTerminals

nonTerminals = getNonTerminals(lines)
# print(nonTerminals)

def getTerminals(lines, nonTerminals):
    terminals = []
    for line in lines:
        parts = line.strip().split(' ->')
        if len(parts) > 1:  # Asegura que exista una parte derecha después de '->'

            for term in parts[1].strip().split():
                if term != "''" and term and term not in nonTerminals and term not in terminals: # Asegura que el término no sea un string vacío o un literal que represente vacío, no esté en nonTerminals y no está ya en terminals
                    terminals.append(term)
    return terminals

terminals = getTerminals(lines, nonTerminals)
# print(terminals)


def getFirsts(lines, nonTerminals, terminals):
    # Crear un diccionario donde cada no terminal tiene una lista vacía asociada
    firsts = {nonTerminal: [] for nonTerminal in nonTerminals}
    print(firsts)
    return firsts

getFirsts(lines, nonTerminals, terminals)