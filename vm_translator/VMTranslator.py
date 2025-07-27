"""

Purpose of this file is to take a '.vm' file as input and generate a hack '.asm' file as output
Optional argument is test file to compare asm result file

"""

import sys
import os
from helper import *

def translateFile(filePath):
    # read in raw line by line input
    raw_input = readRawInputFile(filePath)
    # print(raw_input)

    # clean raw input to remove empty lines & comments
    cleaned_input = cleanRawInput(raw_input)
    # print(cleaned_input)    

    # go through cleaned input and translare to asm
    translated_asm = []
    VmLookupObj = VmCmdLookup()
    funcLabel = None
    call_counter = 0
    fileName = os.path.basename(filePath).split(".")[0]
    # print(fileName)
    for i, line in enumerate(cleaned_input):
        if isComment(line):
            continue
        else:
            asm_eqv = []
            command = '// ' + str(line)
            asm_eqv.append(command)

            split_cmd = line.split(' ')

            # save/create function label here? and pass to obj?
            if split_cmd[0] == 'function':
                funcLabel = f'{split_cmd[1]}$ret{i}'
                # print(funcLabel)
            if split_cmd[0] == 'call':
                call_counter += 1

            tmp = translateVMtoASM(split_cmd, VmLookupObj, i, funcLabel, call_counter, fileName)
            asm_eqv.extend(tmp)
            translated_asm.append(asm_eqv)
    # print(translated_asm)
    # flatten asm
    flattened_asm = flattenArr(translated_asm)
    # print(flattened_asm)
    
    return flattened_asm

if __name__ == "__main__":
    inputPath = sys.argv[1]
    
    bootstrap_arr = writeBoostrapASM()

    if os.path.isfile(inputPath):
        # translate single file to asm string arr
        # each item is single line of asm translation
        asm_arr = translateFile(inputPath)

        # write array to file line by line
        ogFileName = os.path.basename(inputPath)
        outputFileName = str(ogFileName.split('.')[0])+ '.' + 'asm'
        # write .vm translated .asm data to file
        writeListToFile(asm_arr, outputFileName, 0)

        if len(sys.argv) == 3:
            result = check_answer(sys.argv[2], outputFileName)
            print(result)
    elif os.path.isdir(inputPath): 
        # translate directory and compile
        asm_arrs = []
        for i, fileName in enumerate(os.listdir(inputPath)):
            if fileName.endswith(".vm"):
                filePath = os.path.join(inputPath, fileName)
                print(f'Translating file at: {filePath}')
                asm_arrs.append(translateFile(filePath))
                print(f'Done Translating file at: {filePath}')
        
        dirNameStr = os.path.basename(os.path.normpath(inputPath))
        # print(dirNameStr)
        # print(inputPath)
        outputFileName = f'{dirNameStr}.asm'
        # fullOutputPath = f'{inputPath}{outputFileName}'
        fullOutputPath = os.path.join(inputPath, outputFileName)
        print(f'Writing results to file: {fullOutputPath}')
        
        # write bootstrap to file:
        writeListToFile(bootstrap_arr, fullOutputPath, 0)
        for idx, arr in enumerate(asm_arrs):
            writeListToFile(arr, fullOutputPath, idx+1)
        print(f'Done writing results to file: {fullOutputPath}')
    else:
        print("input args error")
