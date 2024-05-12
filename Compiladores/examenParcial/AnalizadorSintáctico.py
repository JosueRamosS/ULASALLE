import csv
from AnalizadorLéxico import token_types
from graphviz import Digraph

inputTokens = token_types
# print(inputTokens)

def ignoreComments(code_string):
    # Ignorar los tokens correspondientes a los comentarios
    code_string = code_string.replace("ILCOMM ", "") 
    code_string = code_string.replace("MLCOMM ", "")
    return code_string

input = ignoreComments(inputTokens)
# print(input)

filename = 'Gramática.txt'
with open(filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()
# print(lines)

def getNonTerminals(lines):
    nonTerminals = []
    for line in lines:
        parts = line.strip().split(' ->') # Parte la línea por '->' y elimina espacios en blanco a los lados
        if parts and parts[0].strip():
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
                for line in lines:  # Procesar recursivamente las líneas para buscar los primeros de este no terminal
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
    follows[next(iter(nonTerminals))].add('$')  # Añadir el símbolo de final de cadena al símbolo inicial si es necesario y upone que el primer no terminal es el símbolo de inicio
    changed = True
    while changed: # Iterar hasta que no hayan cambios en los conjuntos FOLLOW
        changed = False
        for line in lines:
            parts = line.split('->')
            if len(parts) == 2:
                lhs = parts[0].strip()
                rhs = parts[1].strip().split()
                for i in range(len(rhs)): # Buscar todo lo que pueda comenzar después del no terminal actual
                    if rhs[i] in nonTerminals: 
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
    parseTable = {nt: {t: '' for t in terminals + ['$']} for nt in nonTerminals} # Crear una tabla vacía con no terminales como filas y terminales más el símbolo $ como columnas
    for line in lines:     # Procesar cada línea de producción
        parts = line.split('->')
        if len(parts) == 2:
            lhs = parts[0].strip()
            rhs_parts = parts[1].strip().split()
            if rhs_parts[0] == "''":  # Producción vacía
                for follow in follows[lhs]: 
                    parseTable[lhs][follow] = 'ε' # Agregar la producción vacía a todas las entradas de FOLLOW(lhs)
            else:
                first_symbol = rhs_parts[0]
                if first_symbol in nonTerminals: # Si el primer símbolo es un no terminal, agrega la producción a todas las entradas de FIRST
                    for first in firsts[first_symbol]:
                        if first != 'ε':
                            parseTable[lhs][first] = ' '.join(rhs_parts)
                        else: # Si 'ε' está en FIRST(first_symbol), también usar FOLLOW(lhs)
                            for follow in follows[lhs]:
                                parseTable[lhs][follow] = 'ε'
                elif first_symbol in terminals: # Si el primer símbolo es un terminal, solo agrega a esa entrada específica
                    parseTable[lhs][first_symbol] = ' '.join(rhs_parts)
    return parseTable

def generateHTMLTable(nonTerminals, terminals, firsts, follows, parseTable):
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
    for terminal in terminals + ['$']: # Añadir cabeceras para cada terminal y la columna final con el símbolo $
        html += f"<th>{terminal}</th>"
    html += "</tr>"
    for nt in nonTerminals:    # Añadir los datos de cada no terminal
        firsts_str = ", ".join(firsts.get(nt, []))
        follows_str = ", ".join(follows.get(nt, []))
        html += f"""
            <tr>
                <td>{firsts_str}</td>
                <td>{follows_str}</td>
                <td>{nt}</td>
        """
        for terminal in terminals + ['$']:
            production_str = parseTable[nt].get(terminal, '')
            html += f"<td>{production_str}</td>"
        
        html += "</tr>"
    
    html += """
        </table>
    </body>
    </html>
    """
    with open('table.html', 'w', encoding='utf-8') as file: # Escribir la tabla HTML a un archivo
        file.write(html)
    return "Tabla sintáctica generada"

def generateCSVTable(nonTerminals, terminals, firsts, follows, parseTable):
    with open('table.csv', 'w', newline='', encoding='utf-8') as file: # Abrir un archivo CSV para escribir
        writer = csv.writer(file)
        header = ['FIRST', 'FOLLOW', 'Nonterminal'] + terminals + ['$'] # Escribir la cabecera
        writer.writerow(header)
        for nt in nonTerminals: # Escribir las filas para cada no terminal
            row = [
                ", ".join(firsts.get(nt, [])),  # Datos de FIRST
                ", ".join(follows.get(nt, [])),  # Datos de FOLLOW
                nt  # El no terminal
            ]
            row.extend(parseTable[nt].get(terminal, '') for terminal in terminals + ['$']) # Añadir la producción gramatical para cada terminal en la fila
            writer.writerow(row)
    return "Tabla sintáctica generada en CSV"

def traceParsingTable(input_string, terminals, nonTerminals, table_path):
    parse_table = {} # Carga la tabla de análisis sintáctico desde el archivo CSV
    with open(table_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            non_terminal = row['Nonterminal']
            parse_table[non_terminal] = {t: row[t] for t in terminals + ['$']}
    stack = ['$'] # Inicializa el stack y la entrada
    stack.append(next(iter(nonTerminals)))  # Supone que el primer no terminal es el símbolo de inicio
    input_tokens = input_string.split() + ['$']
    trace = []
    accepted = False  # Variable para controlar si la entrada fue aceptada
    idx = 0
    while stack: # Proceso de análisis
        top = stack[-1]
        current_input = input_tokens[idx]
        trace.append((stack.copy(), input_tokens[idx:]))
        if top == current_input:
            if top == '$':
                trace.append(("Accept", ""))
                accepted = True
                break
            else:
                stack.pop()
                idx += 1
        elif top in nonTerminals:
            rule = parse_table[top][current_input]
            if rule:
                stack.pop()
                if rule != 'ε': # Si la regla no es épsilon, añade los símbolos al stack
                    stack.extend(reversed(rule.split()))
                trace.append(("Apply rule", top + " -> " + rule))
            else:
                trace.append(("Error", "No rule"))
                break
        else:
            trace.append(("Error", "Mismatch"))
            break
    with open('tableParse.csv', 'w', newline='', encoding='utf-8') as file: # Exportar el trace a CSV
        writer = csv.writer(file)
        writer.writerow(["Stack", "Input", "Action"])
        for tr in trace:
            if isinstance(tr[0], list):
                writer.writerow([' '.join(tr[0]), ' '.join(tr[1]), ""])
            else:
                writer.writerow(['', '', tr[0] + ": " + tr[1]])
    if accepted: # Imprime en consola si la entrada fue aceptada o no
        print("\033[32mEntrada aceptada !!!\033[0m")
    else:
        print("\033[31mEntrada aceptada !!!\033[0m")
    return "Trace parsing generado en 'tableParse.csv'"

class ASTNode:
    def __init__(self, symbol, is_root=False):
        self.symbol = symbol
        self.children = []
        self.is_root = is_root  # Indicar si es un nodo raíz para manejar correctamente los nombres en Graphviz
    def add_child(self, node):
        self.children.append(node)

import csv

class ASTNode:
    def __init__(self, symbol, is_root=False):
        self.symbol = symbol
        self.children = []
        self.is_root = is_root
    
    def add_child(self, child):
        self.children.append(child)

def traceParsingArbol(input_string, terminals, nonTerminals, table_path):
    parse_table = {}
    with open(table_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            non_terminal = row['Nonterminal']
            parse_table[non_terminal] = {t: row[t] for t in terminals + ['$']}
    
    stack = ['$']
    root_symbol = next(iter(nonTerminals))
    root = ASTNode(root_symbol, is_root=True)
    stack.append(root_symbol)
    node_stack = [root]
    input_tokens = input_string.split() + ['$']
    idx = 0
    
    while stack:
        top = stack[-1]
        current_input = input_tokens[idx]
        if top == current_input:
            if top == '$':
                return True, root
            else:
                stack.pop()
                node_stack.pop()
                idx += 1
        elif top in nonTerminals:
            rule = parse_table[top].get(current_input)
            if rule:
                stack.pop()
                current_node = node_stack.pop()
                rule_symbols = rule.split() if rule != 'ε' else ['ε']
                for symbol in reversed(rule_symbols):
                    new_node = ASTNode(symbol)
                    current_node.add_child(new_node)
                    if symbol != 'ε':
                        stack.append(symbol)
                        node_stack.append(new_node)
            else:
                return False, None
        else:
            return False, None
    
    return False, None

def create_graphviz_ast(node):
    graph = Digraph()
    graph.attr(rankdir='TB')  # Left to Right direction

    def add_nodes_edges(node, graph, parent=None):
        node_id = node.symbol + str(id(node)) if not node.is_root else node.symbol  # Unique ID for each node
        graph.node(node_id, node.symbol)
        if parent:
            graph.edge(parent, node_id)
        for child in node.children:
            add_nodes_edges(child, graph, node_id)
    
    add_nodes_edges(node, graph)
    return graph


#GENERAR TABLA SINTÁCTICA
parse_table = fillParseTable(lines, nonTerminals, terminals, firsts, follows)
# print(parse_table)

#TABLA SINTÁCTICA EN HTML PARA UNA MEJOR VISUALIZACIÓN
output_message = generateHTMLTable(nonTerminals, terminals, firsts, follows, parse_table)
# print(output_message)

#TABLA SINTÁCTICA EN CSV PARA EL PARSEO
output_message_csv = generateCSVTable(nonTerminals, terminals, firsts, follows, parse_table)
# print(output_message_csv)
table_path = 'table.csv'

#PARSING DE LA ENTRADA
output_message_parsing = traceParsingTable(input, terminals, nonTerminals, table_path)
#print(output_message_parsing)

accepted, ast = traceParsingArbol(input, terminals, nonTerminals, table_path)
if accepted:
    graph = create_graphviz_ast(ast)
    graph.render('AST', format='png', view=True)
    print("\033[32mÁrbol generado !!!\033[0m")
else:
    print("\033[31mÁrbol no generado !!!\033[0m")