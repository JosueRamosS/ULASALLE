import csv

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

follows = getFollows(nonTerminals, terminals, firsts, lines)
# print(follows)

def fillParseTable(lines, nonTerminals, terminals, firsts, follows):
    # Crear una tabla vacía con no terminales como filas y terminales más el símbolo $ como columnas
    parseTable = {nt: {t: '' for t in terminals + ['$']} for nt in nonTerminals}

    # Procesar cada línea de producción
    for line in lines:
        parts = line.split('->')
        if len(parts) == 2:
            lhs = parts[0].strip()
            rhs_parts = parts[1].strip().split()

            if rhs_parts[0] == "''":  # Producción vacía
                # Agregar la producción vacía a todas las entradas de FOLLOW(lhs)
                for follow in follows[lhs]:
                    parseTable[lhs][follow] = 'ε'
            else:
                first_symbol = rhs_parts[0]
                if first_symbol in nonTerminals:
                    # Si el primer símbolo es un no terminal, agrega la producción a todas las entradas de FIRST(first_symbol)
                    for first in firsts[first_symbol]:
                        if first != 'ε':
                            parseTable[lhs][first] = ' '.join(rhs_parts)
                        else:
                            # Si 'ε' está en FIRST(first_symbol), también usar FOLLOW(lhs)
                            for follow in follows[lhs]:
                                parseTable[lhs][follow] = 'ε'
                elif first_symbol in terminals:
                    # Si el primer símbolo es un terminal, solo agrega a esa entrada específica
                    parseTable[lhs][first_symbol] = ' '.join(rhs_parts)

    return parseTable

parse_table = fillParseTable(lines, nonTerminals, terminals, firsts, follows)
# print(parse_table)

def generateHTMLTable(nonTerminals, terminals, firsts, follows, parseTable):
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
    
    # Añadir cabeceras para cada terminal y la columna final con el símbolo $
    for terminal in terminals + ['$']:
        html += f"<th>{terminal}</th>"
    
    html += "</tr>"
    
    # Añadir los datos de cada no terminal
    for nt in nonTerminals:
        firsts_str = ", ".join(firsts.get(nt, []))
        follows_str = ", ".join(follows.get(nt, []))
        html += f"""
            <tr>
                <td>{firsts_str}</td>
                <td>{follows_str}</td>
                <td>{nt}</td>
        """
        
        # Añadir la producción gramatical para cada terminal en la fila
        for terminal in terminals + ['$']:
            production_str = parseTable[nt].get(terminal, '')
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
    return "Tabla sintáctica generada"

output_message = generateHTMLTable(nonTerminals, terminals, firsts, follows, parse_table)
print(output_message)

def generateCSVTable(nonTerminals, terminals, firsts, follows, parseTable):
    # Abrir un archivo CSV para escribir
    with open('table.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Escribir la cabecera
        header = ['FIRST', 'FOLLOW', 'Nonterminal'] + terminals + ['$']
        writer.writerow(header)

        # Escribir las filas para cada no terminal
        for nt in nonTerminals:
            row = [
                ", ".join(firsts.get(nt, [])),  # Datos de FIRST
                ", ".join(follows.get(nt, [])),  # Datos de FOLLOW
                nt  # El no terminal
            ]
            # Añadir la producción gramatical para cada terminal en la fila
            row.extend(parseTable[nt].get(terminal, '') for terminal in terminals + ['$'])
            writer.writerow(row)

    return "Tabla sintáctica generada en CSV"

output_message_csv = generateCSVTable(nonTerminals, terminals, firsts, follows, parse_table)
print(output_message_csv)

def traceParsing(input_string, terminals, nonTerminals, table_path):
    # Carga la tabla de análisis sintáctico desde el archivo CSV
    parse_table = {}
    with open(table_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            non_terminal = row['Nonterminal']
            parse_table[non_terminal] = {t: row[t] for t in terminals + ['$']}

    # Inicializa el stack y la entrada
    stack = ['$']
    stack.append(next(iter(nonTerminals)))  # Supone que el primer no terminal es el símbolo de inicio
    input_tokens = input_string.split() + ['$']
    
    # Trace
    trace = []
    
    # Proceso de análisis
    idx = 0
    while stack:
        top = stack[-1]
        current_input = input_tokens[idx]
        trace.append((stack.copy(), input_tokens[idx:]))
        
        if top == current_input:
            if top == '$':
                trace.append(("Accept", ""))
                break
            else:
                stack.pop()
                idx += 1
        elif top in nonTerminals:
            rule = parse_table[top][current_input]
            if rule:
                stack.pop()
                # Si la regla no es épsilon, añade los símbolos al stack
                if rule != 'ε':
                    stack.extend(reversed(rule.split()))
                trace.append(("Apply rule", top + " -> " + rule))
            else:
                trace.append(("Error", "No rule"))
                break
        else:
            trace.append(("Error", "Mismatch"))
            break
    
    # Exportar el trace a CSV
    with open('trace_parsing.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Stack", "Input", "Action"])
        for tr in trace:
            if isinstance(tr[0], list):
                writer.writerow([' '.join(tr[0]), ' '.join(tr[1]), ""])
            else:
                writer.writerow(['', '', tr[0] + ": " + tr[1]])

    return "Trace parsing generado en 'trace_parsing.csv'"


input_string = "MAIN OKEY FOR OPAR DTINTEGER IDENTIFIER ASSIGN VINTEGER PLUS VINTEGER DOTCOMMA VFLOAT EQUAL VFLOAT DOTCOMMA IDENTIFIER PLUS PLUS CPAR OKEY DTINTEGER IDENTIFIER ASSIGN EXPRESSION DOTCOMMA FOR OPAR DTINTEGER IDENTIFIER ASSIGN VINTEGER PLUS VINTEGER DOTCOMMA VFLOAT MULT VFLOAT DOTCOMMA IDENTIFIER PLUS PLUS CPAR OKEY CKEY CKEY"
table_path = 'table.csv'
print(traceParsing(input_string, terminals, nonTerminals, table_path))