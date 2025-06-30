"""

Purpose of this file is to take a '.vm' file as input and generate a hack '.asm' file as output
Optional argument is test file to compare asm result file

"""

import sys
from helper import *

def main(filePath):
    # read in raw line by line input
    raw_input = readRawInputFile(filePath)
    # print(raw_input)

    # clean raw input to remove empty lines & comments
    cleaned_input = cleanRawInput(raw_input)
    print(cleaned_input)    

    # go through cleaned input and translare to asm
    translated_asm = []
    VmLookupObj = VmCmdLookup()
    for i, line in enumerate(cleaned_input):
        if isComment(line):
            continue
        else:
            asm_eqv = []
            command = '// ' + str(line)
            asm_eqv.append(command)

            split_cmd = line.split(' ')
            tmp = translateVMtoASM(split_cmd, VmLookupObj, i)
            asm_eqv.extend(tmp)
            translated_asm.append(asm_eqv)

    # flatten asm
    flattened_asm = flattenArr(translated_asm)
    # print(flattened_asm)
    
    # write array to file line by line
    ogFileName = filePath.split('/')[-1]
    # print(ogFileName)
    outputFileName = str(ogFileName.split('.')[0])+ '.' + 'asm'
    # outputFileName = "test.asm"
    # print(outputFileName)
    writeListToFile(flattened_asm, outputFileName)

    return outputFileName

if __name__ == "__main__":
    created_asm_file = main(sys.argv[1])
    if len(sys.argv) == 3:
        result = check_answer(sys.argv[2], created_asm_file)
        print(result)