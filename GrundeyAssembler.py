# Python Assemebler

# Keep track of what instruction to be able to jump later
instructionCount = 0

# Parsing File
with open('test cases/test_case2.s', 'r') as assemblyFile:
    for line in assemblyFile:
        if (line[0] == '\t'):
            instructionCount += 1
            line = line[1:]
            instruction = line[:line.find("\t")+1]
            print(instruction)
            line = line[line.find("\t")+1:]
            operands = line.rstrip("\n").split(",")
            print(operands)


