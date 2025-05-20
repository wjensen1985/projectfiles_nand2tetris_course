import sys

def main(file):
    # read in raw text line by line from asm file in sys arg
    raw_input = []
    with open(file, "r") as f:
        for line in f:
            raw_input.append(line.rstrip('\n'))
    
    # comp bits:
    comp_dict = {
        "0": "101010",
        "1": "111111",
        "-1": "111010",
        "D": "001100",
        "A": "110000",
        "M": "110000",
        "!D": "001101",
        "!A": "110001",
        "!M": "110001",
        "-D": "001111",
        "-A": "110011",
        "-M": "110011",
        "D+1": "011111",
        "A+1": "110111",
        "M+1": "110111",
        "D-1": "001110",
        "A-1": "110010",
        "M-1": "110010",
        "D+A": "000010",
        "D+M": "000010",
        "D-A": "010011",
        "D-M": "010011",
        "A-D": "000111",
        "M-D": "000111",
        "D&A": "000000",
        "D&M": "000000",
        "D|A": "010101",
        "D|M": "010101"
    }

    # dest bits:
    dest_dict = {
        'null': '000',
        'M': '001',
        'D': '010',
        'MD': '011',
        'A': '100',
        'AM': '101',
        'AD': '110',
        'AMD': '111',
    }

    # jump bits:
    jump_dict = {
        'null': '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111',
    }

    # process symbols:
    # variables, label, pre-defined
    symbols = {
        'SP': '0',
        'LCL': '1',
        'ARG': '2',
        'THIS': '3',
        'THAT': '4',
        'R0': '0',
        'R1': '1',
        'R2': '2',
        'R3': '3',
        'R4': '4',
        'R5': '5',
        'R6': '6',
        'R7': '7',
        'R8': '8',
        'R9': '9',
        'R10': '10',
        'R11': '11',
        'R12': '12',
        'R13': '13',
        'R14': '14',
        'R15': '15',
        'SCREEN': '16384',
        'KDB': '24576'
    }

    # find all symbols, labels, and variables to add to symbol table
    instruction_count = 0
    for line in raw_input:
        line = line.strip()
        if not line or line[0] == '/':
            # skip comments and whitespace
            continue
        
        # is label
        if '(' in line and ')' in line:
            label = (line.split('(')[1]).split(')')[0]
            symbols[label] = str(instruction_count)
            continue

        instruction_count += 1
    

    # process without symbols to hack binary format
    translation = []
    last_used_addr = 15
    for line in raw_input:
        # need to delete spaces/comments
        line = line.strip()
        if not line or line[0] == '/':
            continue
        
        # is label:
        if '(' in line:
            continue
        
        if line[0] == '@':
            # is A instruction
            # resolve variables/symbols:
            raw = line[1:]

            # if is variable vs. address:
            if ord(raw[0]) >= 48 and ord(raw[0]) <= 57:
                # is raw address 
                binOfAddress = bin(int(raw)).split('b')[-1]
            else:
                # is variable/symbol
                if raw in symbols:
                    # is label symbol
                    binOfAddress = bin(int(symbols[raw])).split('b')[-1]
                else:
                    # is variable symbol -> assign first available memory address
                    symbols[raw] = last_used_addr + 1
                    binOfAddress = bin(int(symbols[raw])).split('b')[-1]
                    last_used_addr += 1
            padding_zeros = (16 - 1 - len(binOfAddress)) * "0"
            processed_line = "0" + padding_zeros + binOfAddress
        else:
            # is C instruction - will need to add condition here to filter out/handle symbols/comments
            # syntax: dest = comp; jump
            # need to break into dest, comp, and jump, then look up each part for correlating bits, then combine
            
            if "=" in line:
                dest, comp = line.split("=")
                jump = "null"
            elif ";" in line:
                comp, jump = line.split(";")
                dest = "null"
            else:
                print(line)
                print("error no operation?")
            if "M" in comp:
                a = "1"
            else:
                a = "0"

            processed_line = "111" + a + comp_dict[comp] + dest_dict[dest] + jump_dict[jump]

            # c-instruction starts with "111"
            # full breakdown: 1, 1, 1, a, c1, c2, c3, c4, c5, c6, d1, d2, d3, j1, j2, j3
        
        translation.append(processed_line)
    
    hack_file_name = str(file).split('.')[0] + "_answer" + ".hack"
    with open(hack_file_name, "w") as f:
        for i, line in enumerate(translation):
            if i < len(translation)-1:
                f.write(line + '\n')
            else:
                f.write(line)
    
    return hack_file_name

def check_answer(answer_file, file_to_check):
    created_file_output = []
    with open(file_to_check, "r") as f:
        for line in f:
            created_file_output.append(line)

    answer = []
    with open(answer_file, "r") as f:
        for line in f:
            answer.append(line)
    
    line_number = 0
    matches = True
    errors = []
    while line_number < len(answer) and line_number < len(created_file_output):
        if answer[line_number] != created_file_output[line_number]:
            matches = False
            errors.append("error on line: " + str(line_number+1))
        line_number += 1
    
    if line_number > len(answer):
        errors.append("output is too long")
        matches = False
    if line_number < len(answer):
        errors.append("output is too short")
        matches = False
    
    return [matches, errors]

if __name__ == "__main__":
    created_hack_file = main(sys.argv[1])
    if len(sys.argv) == 3:
        result = check_answer(sys.argv[2], created_hack_file)
        print(result)

                