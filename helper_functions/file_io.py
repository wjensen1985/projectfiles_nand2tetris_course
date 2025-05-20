def readRawInputFile(input_file):
    raw_input = []
    with open(input_file, "r") as f:
        for line in f:
            raw_input.append(line)
    
    return raw_input

def cleanRawInput(raw_input_arr):
    cleaned_input = []
    for line in raw_input_arr:        
        line = line.strip()
        if not line or line[0] == '/':
            continue
        cleaned_input.append(line)

    return cleaned_input

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