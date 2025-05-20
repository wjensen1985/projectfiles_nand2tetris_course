from enum import Enum

"""
purpose: read in text from file line by line -> put in array
input: file name
output: array containing each line of input file
"""
def readRawInputFile(input_file):
    raw_input = []
    with open(input_file, "r") as f:
        for line in f:
            raw_input.append(line)
    
    return raw_input


"""
purpose: remove empty lines
input: array of raw line by line text from file
output: array without empty lines 
"""
def cleanRawInput(raw_input_arr):
    cleaned_input = []
    for line in raw_input_arr:        
        line = line.strip()
        if not line:
            continue
        cleaned_input.append(line)

    return cleaned_input


"""
purpose: compare two files and note differences
input: two files
output: List [isMatching, [any errors/differences]]

"""
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

# returns true if line is a comment
def isComment(line):
    if line[0] == '/':
        return True
    else:
        return False

class VmCmdLookup:
    def __init__(self):
        self._ASM_translation = {
            "push": [
                # sets addr to segment base addr + segment_idx value
                '@segment', 'D=M', '@seg_idx', 'D=D+A', '@addr', 'M=D',
                # *addr = *SP
                'A=M', 'D=M', '@addr', 'M=D',
                # SP++
                '@SP', 'M=M+1',
            ],
            "pop": [
                # sets addr to segment base addr + segment_idx value
                '@segment', 'D=M', '@seg_idx', 'D=D+A', '@addr', 'M=D',
                # SP--
                '@SP', 'M=M-1',
                # *addr = *SP
                'A=M', 'D=M', '@addr', 'M=D'
            ],
            "add": [
                # select top value in stack (store in D):
                '@SP', 'A=M', 'A=A-1', 'D=M',
                # Move down one more stack posn, add prev to current and replace
                'A=A-1', 'D=D+M', 'M=D', 
                # reset stack pointer to first open
                'D=A+1', '@SP', 'M=D'
                ],
            "sub": [
                # select top value in stack (store in D):
                '@SP', 'A=M', 'A=A-1', 'D=M',
                # Move down one more stack posn, subtract prev to current and replace
                'A=A-1', 'D=D-M', 'M=D', 
                # reset stack pointer to first open
                'D=A+1', '@SP', 'M=D'
                ],
            "neg": [
                # select top value in stack
                '@SP', 'A=M', 'A=A-1', 
                # negate selected value
                'M=-M'
            ],
            "eq": [
                # STACK = [y, x, __] where SP points to __
                # D = x, SP--
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Set D = x - y
                'A=A-1', 'D=D-M',
                # jump to is True part of code if x - y > 0
                '@T_N', 'D;JEQ',
                # if False (x-y <= 0), set D to false, jump to end
                'D=0', '@END_N', '0;JMP',
                # If True, set D = -1, then jump to end
                '(T_N)', '@T_N', 'D=-1', '@END_N', '0;JMP',
                # at 'END_N' want to set top val in stack to D (now holds result) 
                '(END_N)', '@END_N', '@SP', 'A=M', 'A=A-1', 'M=D'
            ],
            "gt": [
                # STACK = [y, x, __] where SP points to __
                # D = x, SP--
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Set D = x - y
                'A=A-1', 'D=D-M',
                # jump to is True part of code if x - y > 0
                '@T_N', 'D;JGT',
                # if False (x-y <= 0), set D to false, jump to end
                'D=0', '@END_N', '0;JMP',
                # If True, set D = -1, then jump to end
                '(T_N)', '@T_N', 'D=-1', '@END_N', '0;JMP',
                # at 'END_N' want to set top val in stack to D (now holds result) 
                '(END_N)', '@END_N', '@SP', 'A=M', 'A=A-1', 'M=D'
            ],
            "lt": [
                # STACK = [y, x, __] where SP points to __
                # D = x, SP--
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Set D = x - y
                'A=A-1', 'D=D-M',
                # jump to is True part of code if x - y > 0
                '@T_N', 'D;JLT',
                # if False (x-y <= 0), set D to false, jump to end
                'D=0', '@END_N', '0;JMP',
                # If True, set D = -1, then jump to end
                '(T_N)', '@T_N', 'D=-1', '@END_N', '0;JMP',
                # at 'END_N' want to set top val in stack to D (now holds result) 
                '(END_N)', '@END_N', '@SP', 'A=M', 'A=A-1', 'M=D'
            ],
            "and": [
                # select top value in stack
                '@SP', 'A=M', 'A=A-1',
                # store top val in D, move down one more
                'D=M', 'A=A-1',
                # boolean AND
                'M=D&M'
            ],
            "or": [
                # select top value in stack
                '@SP', 'A=M', 'A=A-1',
                # store top val in D, move down one more
                'D=M', 'A=A-1',
                # boolean OR
                'M=D|M'
            ],
            "not": [
                # select top value in stack
                '@SP', 'A=M', 'A=A-1',
                # boolean NOT
                'M=!M'
            ],
            "label": [],
            "goto": [],
            "ifgoto": [],
        }
    
    def lookup_vm_cmd(self, command):
        return self._ASM_translation[command]
    

"""
purpose: translare vm input (line by line) to hack asm output
input: input array
output
"""
def translateVMtoASM(input, Vmlookup, label_cnt):
    ret = ["// something went wrong - default"]
    if len(input) == 1:
        # arithmetic/boolean stack operation
        ret = Vmlookup.lookup_vm_cmd(input[0])
        for i in range(len(ret)):
            if ret[i] == '@T_N':
                ret[i] = str(f'@T_{label_cnt}')
            if ret[i] == '@END_N':
                ret[i] = str(f'@END_{label_cnt}')
            if ret[i] == '(T_N)':
                ret[i] = str(f'(T_{label_cnt})')
            if ret[i] == '(END_N)':
                ret[i] = str(f'(END_{label_cnt})')

    elif len(input) == 2:
        # skip for now, label/func
        pass
    elif len(input) == 3:
        # special cases are constant, static, and pointer
        segment_name_keyword = {
            'local': 'LCL',
            'temp': 'Temp',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT',
        }

        if input[1] in segment_name_keyword:
            tmp = Vmlookup.lookup_vm_cmd(input[0])

            # loop through returned arr, if any arr[i] in kwd_lookup, replace: arr[i] = kwd_l[arr[i]]
            for i in range(len(tmp)):
                if tmp[i] == '@segment':
                    tmp[i] = '@' + segment_name_keyword[input[1]]
                if tmp[i] == '@seg_idx':
                    tmp[i] = '@' + input[2]
        elif input[1] == 'constant':
            # is special push
            tmp = [
                # sets D to const value
                f'@{input[2]}', 'D=A',
                # pushes D value to stakc
                '@SP', 'A=M', 'M=D',
                # SP++
                '@SP', 'M=M+1'
            ]     
        elif input[1] == 'static':
            tmp = '// error '     
            pass
        elif input[1] == 'pointer':
            tmp = '// error '     
            pass
        else:
            tmp = '// error '     

        ret = tmp
    else:
        ret = ["// command to long"]
    return ret

# flattens list (depth 1level), ex: 
# input = [1,[2,4],[123,12,2,]]
# output = [1, 2, 4, 123, 12, 2]
def flattenArr(arr):
    ret = []
    for item in arr:
        ret.extend(item)
    return ret

# writes 1D list to file line by line
def writeListToFile(data, fileName):
    with open(fileName, 'w') as f:
        for i in range(len(data)):
            if i < len(data)-1:
                f.write(data[i] + '\n')
            else:
                f.write(data[i])