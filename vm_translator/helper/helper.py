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
output: array without empty lines and with comments/whitespace removed
"""
def cleanRawInput(raw_input_arr):
    cleaned_input = []
    for line in raw_input_arr:        
        line = line.strip()
        if not line or isComment(line):
            continue
        # check for inline comments and remove
        # remove tabs
        line = line.replace('\t', '')
        # remove anything after comment symbol
        line = line.split('/')[0]
        # remove trailing spaces
        line = line.rstrip()
        # append cleaned line
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

# object that holds looks up a vm vommand and returns the asm code
class VmCmdLookup:
    def __init__(self):
        self._ASM_translation = {
            "push": [
                # sets A to the segment + seg_idx address
                '@segment', 'D=M', '@seg_idx', 'D=D+A', 'A=D',
                # grabs value at that segment index's address, stores in D, then puts on top of stack
                'D=M', '@SP', 'A=M', 'M=D',
                # SP++
                '@SP', 'M=M+1',
            ],
            "pop": [
                # sets addr to segment base addr + segment_idx value
                '@segment', 'D=M', '@seg_idx', 'D=D+A', '@R15', 'M=D',
                # SP--
                '@SP', 'M=M-1',
                # *addr = *SP
                'A=M', 'D=M', '@R15', 'A=M', 'M=D'
            ],
            "add": [
                # select top value in stack (store in D):
                '@SP', 'M=M-1', 'A=M',
                # Move down one more stack posn, add prev to current and replace
                'D=M', 'A=A-1', 'D=D+M', 'M=D'
                ],
            "sub": [
                # STACK = [x, y, __], where SP points to __  where sub is x - y
                # select top value in stack (store in D), D = y
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Move down one more stack posn
                'A=A-1', 
                # here M = x, so M-D == x-y, result is put in to M
                'M=M-D',
                ],
            "neg": [
                # select top value in stack
                '@SP', 'A=M', 'A=A-1', 
                # negate selected value
                'M=-M'
            ],
            "eq": [
                # STACK = [x, y, __], where SP points to __  where eq is x == y
                # D = y, SP--
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Set D = y - x
                'A=A-1', 'D=D-M',
                # jump to is True part of code if y - x == 0
                '@T_N', 'D;JEQ',
                # if False (x-y <= 0), set D to false, jump to end
                'D=0', '@END_N', '0;JMP',
                # If True, set D = -1, then jump to end
                '(T_N)', '@T_N', 'D=-1', '@END_N', '0;JMP',
                # at 'END_N' want to set top val in stack to D (now holds result) 
                '(END_N)', '@END_N', '@SP', 'A=M', 'A=A-1', 'M=D'
            ],
            "gt": [
                # STACK = [x, y, __], where SP points to __  where eq is x > y 
                # D = y, SP--
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Set D = x - y
                'A=A-1', 'D=M-D',
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
                # STACK = [x, y, __], where SP points to __  where eq is x < y
                # D = y, SP--
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # Set D = y - x
                'A=A-1', 'D=D-M',
                # jump to is True part of code if y - x > 0
                '@T_N', 'D;JGT',
                # if False (x-y <= 0), set D to false, jump to end
                'D=0', '@END_N', '0;JMP',
                # If True, set D = -1, then jump to end
                '(T_N)', '@T_N', 'D=-1', '@END_N', '0;JMP',
                # at 'END_N' want to set top val in stack to D (now holds result) 
                '(END_N)', '@END_N', '@SP', 'A=M', 'A=A-1', 'M=D'
            ],
            "and": [
                # select top value in stack (move SP down 1 in advance)
                '@SP', 'M=M-1', 'A=M',
                # store top val in D, move down one more
                'D=M', 'A=A-1',
                # boolean AND
                'M=D&M'
            ],
            "or": [
                # select top value in stack (move SP down 1 in advance)
                '@SP', 'M=M-1', 'A=M',
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
            "label": [
                '(LABEL)'
            ],
            "goto": [
                # jump to LABEL
                '@_NAME', '0;JMP'
            ],
            "if-goto": [
                # Pop value from stack into D
                '@SP', 'M=M-1', 'A=M', 'D=M',
                # if D != 0, jump
                '@_LABEL', 'D;JNE'
            ],
            "return": [
                # get return value and return to caller at expected address
                # 'endFrame = LCL'
                # R13 = endFrame, R14 = returnAddr
                '@LCL', 'D=M', '@R13', 'M=D',
                # returnAddr = *(endFrame - 5)
                '@5', 'D=A', '@R13', 'D=M-D', 'A=D', 'D=M', '@R14', 'M=D',
                # *ARG = pop()
                '@SP', 'A=M', 'A=A-1', 'D=M',
                '@ARG', 'A=M', 'M=D',

                # Reposition Stack pointer
                # SP = ARG + 1
                '@ARG', 'D=M+1', '@SP', 'M=D',

                # restore segment pointers
                # THAT = *(endFrame - 1)
                '@1', 'D=A', '@R13', 'D=M-D', 'A=D', 'D=M', '@THAT', 'M=D',
                # THIS = *(endFrame - 2)
                '@2', 'D=A', '@R13', 'D=M-D', 'A=D', 'D=M', '@THIS', 'M=D',
                # ARG = *(endFrame - 3)
                '@3', 'D=A', '@R13', 'D=M-D', 'A=D', 'D=M', '@ARG', 'M=D',
                # LCL = *(endFrame - 4)
                '@4', 'D=A', '@R13', 'D=M-D', 'A=D', 'D=M', '@LCL', 'M=D',
                
                # go to return address
                # goto retAddr
                '@R14', 'A=M', '0;JMP',
            ],
        }
    
    def lookup_vm_cmd(self, command):
        return self._ASM_translation[command]
    

"""
purpose: translare vm input (line by line) to hack asm output
input: input array
output
"""
def translateVMtoASM(input, Vmlookup, label_cnt, lastFuncLabel, callCounter, fileName):
    ret = ["// something went wrong - default"]
    if len(input) == 1:
        # arithmetic/boolean stack operation & return
        ret = Vmlookup.lookup_vm_cmd(input[0]).copy()
        for i in range(len(ret)):
            if ret[i] == '@T_N':
                ret[i] = str(f'@T_{label_cnt}')
            if ret[i] == '@END_N':
                ret[i] = str(f'@END_{label_cnt}')
            if ret[i] == '(T_N)':
                ret[i] = str(f'(T_{label_cnt})')
            if ret[i] == '(END_N)':
                ret[i] = str(f'(END_{label_cnt})')
            # if ret[i] == '@returnAddr':
            #     ret[i] = str(f'@returnAddr_{lastFuncLabel}')
            # if ret[i] == '@endFrame':
            #     ret[i] = str(f'@endFrame_{lastFuncLabel}')
    elif len(input) == 2:
        ret = Vmlookup.lookup_vm_cmd(input[0]).copy()
        for i in range(len(ret)):
            if ret[i] == '(LABEL)':
                ret[i] = f'({input[1]})'
            elif ret[i] == '@_LABEL':
                ret[i] = f'@{input[1]}'
            elif ret[i] == '@_NAME':
                ret[i] = f'@{input[1]}'

        pass
    elif len(input) == 3:
        # push segment i, pop segment i, function funcName nVars, call funcName nArgs
        # special cases are constant, static, and pointer
        if input[0] == 'pop' or input[0] == 'push':
            segment_name_keyword = {
                'local': 'LCL',
                # 'temp': '5',
                'argument': 'ARG',
                'this': 'THIS',
                'that': 'THAT',
            }

            if input[1] in segment_name_keyword:
                tmp = Vmlookup.lookup_vm_cmd(input[0]).copy()

                # loop through returned arr, if any arr[i] in kwd_lookup, replace: arr[i] = kwd_l[arr[i]]
                for i in range(len(tmp)):
                    if tmp[i] == '@segment':
                        tmp[i] = '@' + segment_name_keyword[input[1]]
                    if tmp[i] == '@seg_idx':
                        tmp[i] = '@' + input[2]
            elif input[1] == 'temp':
                if input[0] == 'pop':
                    tmp = [
                        # sets addr to segment base addr + segment_idx value
                        '@5', 'D=A', f'@{input[2]}', 'D=D+A', '@R15', 'M=D',
                        # SP--
                        '@SP', 'M=M-1',
                        # *addr = *SP
                        'A=M', 'D=M', '@R15', 'A=M', 'M=D'
                    ]
                if input[0] == 'push':
                    tmp = [
                        # sets addr to segment base addr + segment_idx value
                        '@5', 'D=A', f'@{input[2]}', 'D=D+A', 'A=D',
                        # grabs value at that segment index's address, stores in D, then puts on top of stack
                        'D=M', '@SP', 'A=M', 'M=D',
                        # SP++
                        '@SP', 'M=M+1',
                    ]
            elif input[1] == 'constant':
                # is special push
                tmp = [
                    # sets D to const value
                    f'@{input[2]}', 'D=A',
                    # pushes D value to stack
                    '@SP', 'A=M', 'M=D',
                    # SP++
                    '@SP', 'M=M+1'
                ]     
            elif input[1] == 'static':
                if input[0] == 'pop':
                    tmp = [
                        '@SP', 'M=M-1', 'A=M', 'D=M',
                        f'@{fileName}.{input[2]}', 'M=D'
                    ]
                if input[0] == 'push':
                    tmp = [
                        f'@{fileName}.{input[2]}', 'D=M',
                        '@SP', 'A=M', 'M=D',
                        '@SP', 'M=M+1'
                    ]
            elif input[1] == 'pointer':
                tmp = ['// error ' ]
                if input[2] == '0':
                    # THIS
                    if input[0] == 'pop':
                        tmp = [
                            # select value at top of stack, SP--
                            '@SP', 'M=M-1', 'A=M', 'D=M',
                            # go to THAT, and store D there
                            '@THIS', 'M=D'

                        ]
                    if input[0] == 'push':
                        tmp = [
                            # grab value in THAT
                            '@THIS', 'D=M',
                            # push to top of stack
                            '@SP', 'A=M', 'M=D',
                            # SP++
                            '@SP', 'M=M+1'
                        ]
                elif input[2] == '1':
                    # THAT
                    if input[0] == 'pop':
                        tmp = [
                            # select value at top of stack, SP--
                            '@SP', 'M=M-1', 'A=M', 'D=M',
                            # go to THAT, and store D there
                            '@THAT', 'M=D'

                        ]
                    if input[0] == 'push':
                        tmp = [
                            # grab value in THAT
                            '@THAT', 'D=M',
                            # push to top of stack
                            '@SP', 'A=M', 'M=D',
                            # SP++
                            '@SP', 'M=M+1'
                        ]
        elif input[0] == 'function':
            """
                function funcName, nVars
                1. injectt entry point label
                2. initialize local segment of the callee
            """

            tmp = ['// error: function asm']
            funcName, nVars = input[1:3]

            # 1. inject entry point label
            tmp = [
                f'({funcName})'
            ]

            # 2. intialize local segment of callee (push 0 nVars number of times)
            for _ in range(int(nVars)):
                tmp.extend([
                        '@0', 'D=A',
                        # go to top of stack and push D
                        '@SP', 'A=M', 'M=D',
                        # SP++
                        '@SP', 'M=M+1'
                    ])
            

        elif input[0] == 'call':
            """
                call funcName nArgs
                function call template:
                1. push retAddrLabel
                2. push LCL, ARG, THIS, THAT
                3. reposition ARG & LCL
                4. transfer control to callee
                5. injects retAddrLabel
            """
            tmp = ['// error: call asm']
            funcName, nArgs = input[1:3]

            # 1. push retAddrLabel
            tmp = [
                f'@retAddr_{fileName}_{callCounter}',
                'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
            ]
            
            # 2. push LCL, ARG, THIS, THAT -> save stack Frame
            stackFrameElements = ['LCL', 'ARG', 'THIS', 'THAT']
            for segName in stackFrameElements:
                asm_code = [
                        # get caller address for stack frame element (memory segment base addr)
                        f'@{segName}', 'D=M',
                        # go to top of stack and push D
                        '@SP', 'A=M', 'M=D',
                        # SP++
                        '@SP', 'M=M+1'
                    ]
                tmp.extend(asm_code.copy())
            
            # 3. reposition ARG & LCL
            tmp.extend([
                    # ARG = SP - 5 - nArgs
                    f'@{nArgs}', 'D=A', '@5', 'D=D+A', 
                    '@SP', 'D=M-D', '@ARG', 'M=D',
                    # LCL = SP
                    '@SP', 'D=M', '@LCL', 'M=D',
                ])

            # 4. transfer control to callee
            tmp.extend([
                        f'@{funcName}', '0;JMP'
                    ])
            
            # 5. injects retAddrLabel
            tmp.extend([
                f'(retAddr_{fileName}_{callCounter})'
            ])

            # print(tmp)
        else:
            tmp = ['// error ']     

        ret = tmp
    else:
        ret = ["// command too long"]
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
# inputNumber is the count of arrays already written to the file
# this is used to tell this to add a new line before the data or not
# anything >=1 will add '\n' at the beginning
def writeListToFile(data, fileName, inputNumber):
    with open(fileName, 'a+') as f:
        if inputNumber > 0:
            f.write('\n')
        for i in range(len(data)):
            if i < len(data)-1:
                f.write(data[i] + '\n')
            else:
                f.write(data[i])

def writeBoostrapASM():
    tmp = [
        # SP = 256; setting stack pointer
        '// Boostrap: set SP to 256', '@256', 'D=A', '@SP', 'M=D',
    ]

    # call sys init:
    # 1. push retAddrLabel
    tmp.extend([
        f'@retAddr_bootstrap_sys_init',
        'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
    ])
    
    # 2. push LCL, ARG, THIS, THAT -> save stack Frame
    stackFrameElements = ['LCL', 'ARG', 'THIS', 'THAT']
    for segName in stackFrameElements:
        asm_code = [
                # get caller address for stack frame element (memory segment base addr)
                f'@{segName}', 'D=M',
                # go to top of stack and push D
                '@SP', 'A=M', 'M=D',
                # SP++
                '@SP', 'M=M+1'
            ]
        tmp.extend(asm_code.copy())
    
    # 3. reposition ARG & LCL
    tmp.extend([
            # ARG = SP - 5 - nArgs
            f'@0', 'D=A', '@5', 'D=D+A', 
            '@SP', 'D=M-D', '@ARG', 'M=D',
            # LCL = SP
            '@SP', 'D=M', '@LCL', 'M=D',
        ])

    # 4. transfer control to callee
    tmp.extend([
                f'@Sys.init', '0;JMP'
            ])
    
    # 5. injects retAddrLabel
    tmp.extend([
        f'(retAddr_bootstrap_sys_init)'
    ])
    
    return tmp

