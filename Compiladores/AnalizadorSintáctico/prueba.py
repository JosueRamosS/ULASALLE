import csv

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

# Uso de la función
# input_string = "int * int + ( int + int ) $"
input_string = "MAIN OKEY STATEMENTS LOOPS IFELSES $"
terminals = ['DATATYPE', 'IDENTIFIER', 'OPAR', 'CPAR', 'OKEY', 'STATEMENTS', 'LOOPS', 'IFELSES', 'CKEY', 'COMMA', 'MAIN']
nonTerminals = ['PROGRAM', "FUNCTION'", 'PARAMETERS', 'MORE_PARAMETERS', 'PARAMETER', "MAIN'"]
table_path = 'table.csv'
print(traceParsing(input_string, terminals, nonTerminals, table_path))
