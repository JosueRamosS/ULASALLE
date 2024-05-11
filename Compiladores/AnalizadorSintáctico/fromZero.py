
from prettytable import PrettyTable

filename = 'fromZeroGrammar.txt'
with open(filename, 'r', encoding='utf-8') as file:
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
    firsts = {nonTerminal: [] for nonTerminal in nonTerminals}
    in_process = set()  # Para evitar la recursión infinita por ciclos en la gramática

    def addFirsts(nt, first_candidate):
        if first_candidate in terminals or first_candidate == 'ε':
            if first_candidate not in firsts[nt]:
                firsts[nt].append(first_candidate)
        elif first_candidate in nonTerminals:
            if (nt, first_candidate) not in in_process:  # Verificar si ya se está procesando esta combinación
                in_process.add((nt, first_candidate))  # Marcar como en proceso
                # Procesar recursivamente las líneas para buscar los primeros de este no terminal
                for line in lines:
                    if line.strip().startswith(first_candidate + ' ->'):
                        new_right_side = line.split('->')[1].strip().split()
                        if not new_right_side or new_right_side[0] == "''":
                            addFirsts(nt, 'ε')
                        else:
                            addFirsts(nt, new_right_side[0])
                in_process.remove((nt, first_candidate))  # Quitar marca de proceso
    
    for line in lines:
        if '->' in line:  # Asegurar que la línea contiene una producción válida
            parts = line.split('->')
            left_side = parts[0].strip()
            right_side = parts[1].strip().split()
        
            if not right_side or right_side[0] == "''":
                addFirsts(left_side, 'ε')
            else:
                addFirsts(left_side, right_side[0])

    return firsts

firsts = getFirsts(lines, nonTerminals, terminals)
# print(firsts)

def getFollows(nonTerminals, terminals, firsts, lines):
    follows = {nt: set() for nt in nonTerminals}
    # Añadir el símbolo de final de cadena al símbolo inicial si es necesario
    follows[next(iter(nonTerminals))].add('$')  # Supone que el primer no terminal es el símbolo de inicio

    # Iterar hasta que no hayan cambios en los conjuntos FOLLOW
    changed = True
    while changed:
        changed = False
        for line in lines:
            parts = line.split('->')
            if len(parts) == 2:
                lhs = parts[0].strip()
                rhs = parts[1].strip().split()

                for i in range(len(rhs)):
                    if rhs[i] in nonTerminals:
                        # Buscar todo lo que pueda comenzar después del no terminal actual
                        next_firsts = set()
                        if i + 1 < len(rhs):
                            for symbol in rhs[i+1:]:
                                if symbol in terminals:
                                    next_firsts.add(symbol)
                                    break
                                else:
                                    next_firsts.update(firsts[symbol])
                                    if 'ε' not in firsts[symbol]:
                                        break
                            else:  # Si llega al final y todo puede ser vacío
                                next_firsts.update(follows[lhs])
                        else:
                            next_firsts.update(follows[lhs])

                        if 'ε' in next_firsts:
                            next_firsts.remove('ε')
                            next_firsts.update(follows[lhs])

                        old_size = len(follows[rhs[i]])
                        follows[rhs[i]].update(next_firsts)
                        if len(follows[rhs[i]]) > old_size:
                            changed = True

    return follows

# Suponiendo que tienes 'firsts' y las otras variables definidas correctamente
follows = getFollows(nonTerminals, terminals, firsts, lines)
# print(follows)


def generateHTMLTable(nonTerminals, terminals, firsts, follows):
    # Comenzar el documento HTML
    html = """
    <html>
    <head>
        <style>
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <table>
            <tr>
                <th>FIRST</th>
                <th>FOLLOW</th>
                <th>Nonterminal</th>
    """
    
    # Añadir cabeceras para cada terminal
    for terminal in terminals:
        html += f"<th>{terminal}</th>"
    
    html += "</tr>"
    
    # Añadir los datos de cada no terminal
    for nt in nonTerminals:
        firsts_str = ", ".join(firsts.get(nt, []))
        follows_str = ", ".join(follows.get(nt, []))  # Simula una función para obtener los FOLLOWs
        html += f"""
            <tr>
                <td>{firsts_str}</td>
                <td>{follows_str}</td>
                <td>{nt}</td>
        """
        
        # Simular datos de producción gramatical para cada terminal en la fila
        for terminal in terminals:
            production_str = " "  # Simula que obtienes la producción adecuada
            html += f"<td>{production_str}</td>"
        
        html += "</tr>"
    
    html += """
        </table>
    </body>
    </html>
    """
    
    # Escribir la tabla HTML a un archivo
    with open('table.html', 'w', encoding='utf-8') as file:
        file.write(html)

# Usar esta función pasando los diccionarios firsts y un diccionario simulado de follows
generateHTMLTable(nonTerminals, terminals, firsts, follows)



