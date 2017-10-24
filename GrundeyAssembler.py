# Python Assemebler
# Colin Grundey
# October 2017

import sys
import os
import re

if len(sys.argv) != 2:
    print(sys.argv)
    sys.exit('Wrong number of arguments: ' + str(len(sys.argv) - 1) + '\nUsage: <input assembly file> <output object file>\n')

inFileName = sys.argv[1]

if not os.path.isfile(inFileName) or (inFileName[inFileName.find('.'):] != '.s' and inFileName[inFileName.find('.'):] != '.asm'):
    print(inFileName)
    sys.exit('Input file does not exist: ' + inFileName)

outFileName = os.path.basename(inFileName)
outFileName = outFileName[:outFileName.find('.')] + '.obj'

# Keep track of instruction to branch to later
instructionCount = 0

rTypeFuncts = {'add': '100000', 'addu': '100001', 'and': '100100', 'nor': '100111', 'or': '100101', 'slt': '101010',
               'sltu': '101011', 'sll': '000000', 'srl': '000010', 'sub': '100010', 'subu': '100011'}
iTypeOps = {'addi': '001000', 'addiu': '001001', 'andi': '001100', 'beq': '000100', 'bne': '000101', 'lbu': '100100',
            'lhu': '100101', 'll': '110000', 'lui': '001111', 'lw': '100011', 'ori': '001101', 'slti': '001010',
            'sltiu': '001011', 'sb': '101000', 'sc': '111000', 'sh': '101001', 'sw': '101011'}
regs = {'$zero': '00000', '$at': '00001', '$v0': '00010', '$v1': '00011', '$a0': '00100', '$a1': '00101',
        '$a2': '00110', '$a3': '00111', '$t0': '01000', '$t1': '01001', '$t2': '01010', '$t3': '01011', '$t4': '01100',
        '$t5': '01101', '$t6': '01110', '$t7': '01111', '$s0': '10000', '$s1': '10001', '$s2': '10010', '$s3': '10011',
        '$s4': '10100', '$s5': '10101', '$s6': '10110', '$s7': '10111', '$t8': '11000', '$t9': '11001', '$k0': '11010',
        '$k1': '11011', '$gp': '11100', '$sp': '11101', '$fp': '11110', '$ra': '11111'}

# Branch labels and locations are stored in a dictionary
labels = dict()
# Final instructions recorded in hex are stored in a list
hexInstructions = list()

# Parsing labels
with open(inFileName, 'r') as assemblyFile:
    lineCount = 1
    n = 0
    for line in assemblyFile:
        if ':' in line:
            labels.update({line[:line.find(':')]: lineCount - n})
            n += 1
        lineCount += 1

linenum = 0  # for error output

# Parsing instructions
with open(inFileName, 'r') as assemblyFile:
    for line in assemblyFile:
        linenum += 1
        if ':' not in line:
            instructionCount += 1
            line = line[1:]
            instruction = line[:line.find("\t") + 1].rstrip("\t")
            line = line[line.find("\t") + 1:]
            operands = line.rstrip("\n").split(", ")

            # R-Type instructions
            if instruction in rTypeFuncts:
                if len(operands) != 3:
                    sys.exit('Incorrect format at line [' + linenum + ']')
                if operands[0] not in regs or operands[1] not in regs:
                    sys.exit('Invalid register given at line [' + linenum + ']');

                opcode = '000000'
                functCode = rTypeFuncts[instruction]
                rd = regs[operands[0]]
                # Shift instructions
                if instruction == 'srl' or instruction == 'sll':
                    rt = regs[operands[1]]
                    rs = '00000'
                    shamt = str(bin(int(operands[2]))[2:].zfill(5))
                # Other R-Type instructions
                else:
                    if operands[2] not in regs:
                        sys.exit('Invalid register given at line [' + linenum + ']');

                    rs = regs[operands[1]]
                    rt = regs[operands[2]]
                    shamt = '00000'
                result = opcode + rs + rt + rd + shamt + functCode
                hexInstructions.append(hex(int(result, 2))[2:].zfill(8))

            # I-Type instructions
            elif instruction in iTypeOps:
                opcode = iTypeOps[instruction]
                # Load & Store Word
                if instruction == 'lw' or instruction == 'sw':
                    if len(operands) != 2:
                        sys.exit('Incorrect format at line [' + linenum + ']')
                    if operands[0] not in regs or operands[1][operands[1].find('(') + 1:operands[1].find(')')] not in regs:
                        sys.exit('Incorrect format at line [' + linenum + ']')

                    rt = regs[operands[0]]
                    rs = regs[operands[1][operands[1].find('(') + 1:operands[1].find(')')]]
                    imm = operands[1][:operands[1].find('(')]
                else:
                    if len(operands) != 3:
                        sys.exit('Incorrect format at line [' + linenum + ']')
                    if operands[0] not in regs or operands[1] not in regs:
                        sys.exit('Incorrect format at line [' + linenum + ']')

                    rt = regs[operands[0]]
                    rs = regs[operands[1]]
                    imm = operands[2]
                    if instruction == 'beq' or instruction == 'bne':
                        if imm in labels:
                            rs = regs[operands[0]]
                            rt = regs[operands[1]]
                            imm = str(labels[imm] - instructionCount - 1)
                        else:
                            sys.exit('Label does not exist at line [' + linenum + ']')

                if int(imm) < 0:
                    imm = bin(int(imm) & 0xffff)[2:]
                else:
                    imm = bin(int(imm))[2:].zfill(16)
                result = opcode + rs + rt + imm
                hexInstructions.append(hex(int(result, 2))[2:].zfill(8))

            else:
                sys.exit('Instruction not supported at line [' + linenum + ']')

# Output hex instructions to object file
with open(outFileName, 'w') as f:
    for i in hexInstructions:
        f.write(str(i) + '\n')  # writes as string to object file
        # f.write(bytes(i))
        # f.write(b'\n')
