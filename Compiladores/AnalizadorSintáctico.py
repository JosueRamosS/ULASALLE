import csv
import webbrowser
import os

from AnalizadorLéxico import token_types
from AnalizadorLéxico import listaCodFuente
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
    parse_table = {}  # Carga la tabla de análisis sintáctico desde el archivo CSV
    with open(table_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            non_terminal = row['Nonterminal']
            parse_table[non_terminal] = {t: row[t] for t in terminals + ['$']}
    stack = ['$']  # Inicializa el stack y la entrada
    stack.append(next(iter(nonTerminals)))  # Supone que el primer no terminal es el símbolo de inicio
    input_tokens = input_string.split() + ['$']
    trace = []
    accepted = False  # Variable para controlar si la entrada fue aceptada
    idx = 0
    while stack:  # Proceso de análisis
        top = stack[-1]
        current_input = input_tokens[idx]
        trace.append((stack.copy(), input_tokens[idx:], "Terminal"))
        if top == current_input:
            if top == '$':
                trace[-1] = (trace[-1][0], trace[-1][1], "Accept")
                accepted = True
                break
            else:
                stack.pop()
                idx += 1
        elif top in nonTerminals:
            rule = parse_table[top][current_input]
            if rule:
                stack.pop()
                if rule != 'ε':  # Si la regla no es épsilon, añade los símbolos al stack
                    stack.extend(reversed(rule.split()))
                trace[-1] = (trace[-1][0], trace[-1][1], top + " -> " + rule)
            else:
                trace[-1] = (trace[-1][0], trace[-1][1], "Error: No rule")
                break
        else:
            trace[-1] = (trace[-1][0], trace[-1][1], "Error: Mismatch")
            break
    with open('parse.csv', 'w', newline='', encoding='utf-8') as file:  # Exportar el trace a CSV
        writer = csv.writer(file)
        writer.writerow(["Stack", "Input", "Action"])
        for tr in trace:
            writer.writerow([' '.join(tr[0]), ' '.join(tr[1]), tr[2]])
    if accepted:  # Imprime en consola si la entrada fue aceptada o no
        print("\n" + "\033[32mEntrada aceptada !!!\033[0m")
    else:
        print("\n" + "\033[31mEntrada no aceptada !!!\033[0m")
    return  "Parseo hecho"

class ASTNode:
    def __init__(self, symbol, is_root=False):
        self.symbol = symbol
        self.children = []
        self.is_root = is_root  # Indicar si es un nodo raíz para manejar correctamente los nombres en Graphviz
    def add_child(self, node):
        self.children.append(node)

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

def create_graphviz_ast(node, terminal_symbols, source_code):
    graph = Digraph()
    graph.attr(rankdir='TB')  # Top to Bottom direction

    # Invertir la lista del código fuente
    source_code = list(reversed(source_code))
    terminal_idx = 0

    def add_nodes_edges(node, graph, parent=None):
        nonlocal terminal_idx
        node_id = node.symbol + str(id(node)) if not node.is_root else node.symbol  # Unique ID for each node
        graph.node(node_id, node.symbol)

        if parent:
            graph.edge(parent, node_id)

        # If the node is a terminal, add the corresponding source code character
        if node.symbol in terminal_symbols and terminal_idx < len(source_code):
            child_id = source_code[terminal_idx] + str(id(node))  # Unique ID for each terminal node
            graph.node(child_id, source_code[terminal_idx])
            graph.edge(node_id, child_id)
            terminal_idx += 1

        # Recursively add child nodes
        for child in node.children:
            add_nodes_edges(child, graph, node_id)
    
    add_nodes_edges(node, graph)
    return node, graph

def create_graphviz_ast1(node):
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

def get_leaf_nodes(node):
    leaf_nodes = []
    
    def dfs(current_node):
        if not current_node.children:  # Si el nodo no tiene hijos, es una hoja
            if current_node.symbol != 'ε':  # Omitir el símbolo ε
                leaf_nodes.append(current_node.symbol)
        for child in current_node.children:
            dfs(child)
    
    dfs(node)
    leaf_nodes.reverse()  # Revertir el orden de la lista
    # leaf_nodes_str = ' '.join(leaf_nodes)  # Convertir la lista a una cadena de caracteres
    return leaf_nodes

def modify_ast(tree, listaCodFuente):
    listaCodFuente = list(reversed(listaCodFuente))
    def process_node(node):
        if node.symbol == 'ε':
            return
        if not node.children:  # Si es una hoja
            if listaCodFuente:
                hijo = listaCodFuente.pop(0)
                node.add_child(ASTNode(hijo))
        else:
            for child in node.children:
                process_node(child)

    process_node(tree)
    return tree

# def print_ast(node, indent="", last='updown'):
#     nb_children = lambda node: sum(nb_children(child) for child in node.children) + 1
#     size_branch = {child: nb_children(child) for child in node.children}

#     """ Creation of balanced lists for "up" branch and "down" branch. """
#     up = sorted(node.children, key=lambda child: nb_children(child))
#     down = []
#     while up and sum(size_branch[n] for n in down) < sum(size_branch[n] for n in up):
#         down.append(up.pop())

#     """ Printing of "up" branch. """
#     for child in up:     
#         next_last = 'up' if up.index(child) == 0 else ''
#         next_indent = '{0}{1}{2}'.format(indent, '│   ' if 'up' in last else '    ', ' ' * (len(node.symbol) + 2))
#         print_ast(child, next_indent, next_last)

#     """ Printing of current node. """
#     if last == 'up': start_shape = '┌'
#     elif last == 'down': start_shape = '└'
#     elif last == 'updown': start_shape = ' '
#     else: start_shape = '├'

#     if len(node.children) > 0:
#         end_shape = '┤'
#     else:
#         end_shape = ''
        
#     print('{0}{1}{2} {3}'.format(indent, start_shape, node.symbol, end_shape))

#     """ Printing of "down" branch. """
#     for child in down:    
#         next_last = 'down' if down.index(child) == len(down) - 1 else ''
#         next_indent = '{0}{1}{2}'.format(indent, '│   ' if 'down' in last else '    ', ' ' * (len(node.symbol) + 2))
#         print_ast(child, next_indent, next_last)

def create_symbol_table(tree):
    symbol_table = [["Nombre", "Tipo", "Valor", "Var o Fun", "Scope"]]

    def find_leaf_value(node):
        if not node.children:
            return node.symbol
        return find_leaf_value(node.children[0])

    def process_global_assignment(node):
        entry = ["", "", "", "var", "global"]
        datatype_node = find_child_node(node, "DATATYPE")
        identifier_node = find_child_node(node, "IDENTIFIER")
        expression_node = find_child_node(node, "EXPRESSION")

        if datatype_node:
            entry[1] = find_leaf_value(datatype_node)
        if identifier_node:
            entry[0] = find_leaf_value(identifier_node)
        if expression_node:
            entry[2] = find_expression_value(expression_node)

        if entry[0] and entry[1]:
            symbol_table.append(entry)

    def process_function(node):
        entry = ["", "", "null", "fun", "global"]
        datatype_node = find_child_node(node, "DATATYPE")
        identifier_node = find_child_node(node, "IDENTIFIER")

        if datatype_node:
            entry[1] = find_leaf_value(datatype_node)
        if identifier_node:
            entry[0] = find_leaf_value(identifier_node)

        function_name = entry[0]

        if function_name and entry[1]:
            symbol_table.append(entry)

            parameters_node = find_child_node(node, "PARAMETERS")
            if parameters_node:
                process_parameters(parameters_node, function_name)

            statements_node = find_child_node(node, "STATEMENTS")
            if statements_node:
                process_statements(statements_node, function_name)

    def process_main(node):
        statements_node = find_child_node(node, "STATEMENTS")
        if statements_node:
            process_statements(statements_node, "MAIN")

    def process_parameters(node, function_name):
        for child in node.children:
            if child.symbol == "PARAMETER":
                datatype_node = find_child_node(child, "DATATYPE")
                identifier_node = find_child_node(child, "IDENTIFIER")
                entry = ["", "", "null", "var", function_name]
                if datatype_node:
                    entry[1] = find_leaf_value(datatype_node)
                if identifier_node:
                    entry[0] = find_leaf_value(identifier_node)
                if entry[0] and entry[1]:
                    symbol_table.append(entry)
            else:
                process_parameters(child, function_name)

    def process_statements(node, scope):
        for child in node.children:
            if child.symbol == "ASSIGNMENT":
                process_assignment(child, scope)
            else:
                process_statements(child, scope)

    def process_assignment(node, scope):
        entry = ["", "", "", "var", scope]
        datatype_node = find_child_node(node, "DATATYPE")
        identifier_node = find_child_node(node, "IDENTIFIER")
        expression_node = find_child_node(node, "EXPRESSION")

        if datatype_node:
            entry[1] = find_leaf_value(datatype_node)
        if identifier_node:
            entry[0] = find_leaf_value(identifier_node)
        if expression_node:
            entry[2] = find_expression_value(expression_node)

        if entry[0] and entry[1]:
            symbol_table.append(entry)

    def find_child_node(node, symbol):
        for child in node.children:
            if child.symbol == symbol:
                return child
        return None

    def find_expression_value(node):
        for child in node.children:
            if child.symbol in ["VINTEGER", "VFLOAT", "VSTRING", "VCHAR", "VTRUE", "VFALSE", "IDENTIFIER"]:
                return find_leaf_value(child)
            elif child.symbol in ["EXPRESSION", "TERM", "FACTOR", "DVORID"]:
                value = find_expression_value(child)
                if value:
                    return value
        return None

    def traverse_tree(node):
        if node.symbol == "GLOBALASSIGNMENT":
            process_global_assignment(node)
        elif node.symbol == "FUNCTION'":
            process_function(node)
        elif node.symbol == "MAIN'":
            process_main(node)
        for child in node.children:
            traverse_tree(child)

    traverse_tree(tree)
    return symbol_table

def print_symbol_table(symbol_table):
    # Calcula el ancho máximo para cada columna
    col_widths = [max(len(str(item)) for item in col) for col in zip(*symbol_table)]
    # Imprime la tabla alineada
    for row in symbol_table:
        print("  ".join(f"{item:<{col_widths[i]}}" for i, item in enumerate(row)))


#GENERAR TABLA SINTÁCTICA
parse_table = fillParseTable(lines, nonTerminals, terminals, firsts, follows)
# print(parse_table)

# #TABLA SINTÁCTICA EN HTML PARA UNA MEJOR VISUALIZACIÓN
# output_message = generateHTMLTable(nonTerminals, terminals, firsts, follows, parse_table)
# # print(output_message)

#TABLA SINTÁCTICA EN CSV PARA EL PARSEO
output_message_csv = generateCSVTable(nonTerminals, terminals, firsts, follows, parse_table)
# print(output_message_csv)
table_path = 'table.csv'

#PARSING DE LA ENTRADA QUE SE OBTIENE DEL ANALIZADOR LÉXICO
output_message_parsing = traceParsingTable(input, terminals, nonTerminals, table_path)
print("\033[38;5;19m"+ output_message_parsing +"\033[0m")

accepted, ast = traceParsingArbol(input, terminals, nonTerminals, table_path)
nodosHijos = get_leaf_nodes(ast)
modified_tree = modify_ast(ast, listaCodFuente)

# Generar el árbol con las asociaciones
if accepted:
    graph1 = create_graphviz_ast1(modified_tree)
    graph1.render('AST', format='png', view=True)
    # ast1, graph = create_graphviz_ast(ast, nodosHijos, listaCodFuente)
    # graph.render('AST', format='png', view=True)
    print("\033[32mÁrbol generado !!!\033[0m" + "\n")
else:
    print("\033[31mÁrbol no generado !!!\033[0m" + "\n")

# print(token_types)
# print(nodosHijos)
# print(listaCodFuente)
# create_graphviz_ast1(modified_tree)
# print_ast(modified_tree)


# Crear la tabla de símbolos
symbol_table = create_symbol_table(modified_tree)

# Imprimir la tabla de símbolos
print_symbol_table(symbol_table)