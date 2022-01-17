# Aaron Wylie
import re
import sys
import os
# Script to parse through bench and receive relevant inputs

# The specific string I am looking for
input_text = "INPUT("
output_text = "OUTPUT("

filename = sys.argv[1]

file = open(filename, "r")

# Get input/output gates and put in array
input_array = []
output_array = []
for line in file:
    if input_text in line:
        input_array.append(line[line.find("(") + 1:line.find(")")])
    elif output_text in line:
        output_array.append(line[line.find("(") + 1:line.find(")")])
file.close()

print("INPUT GATES --> ", input_array)
print("OUTPUT GATES --> ", output_array)
print("*********************************************")
# ******************************************************************************************

file = open(filename, "r")

def parse(node):
    wire = []
    relevant_inputs = []
    file.seek(0, 0)
    for file_line in file:
        if node + ' = ' in file_line:
            gate_inputs = (str(re.findall(r'\(.*?\)', file_line))).split(',')
            for i in range(len(gate_inputs)):
                gate_inputs[i] = gate_inputs[i].replace("['(", "").replace(")']", "").replace(" ", "")
            for j in gate_inputs:
                if j in input_array:
                    relevant_inputs.append(j)
                else:
                    wire.append(j)
    while wire:
        for i in wire:
            file.seek(0, 0)
            # Right here gets each node 10,69,16
            for file_line in file:
                if i + " = " in file_line:
                    gate_inputs = (str(re.findall(r'\(.*?\)', file_line))).split(',')
                    for c in range(len(gate_inputs)):
                        gate_inputs[c] = gate_inputs[c].replace("['(", "").replace(")']", "").replace(" ", "")
                    for j in gate_inputs:
                        if j in input_array:
                            if j not in relevant_inputs:
                                relevant_inputs.append(j)
                        else:
                            wire.append(j)
            wire.remove(i)
    return(relevant_inputs)


largest_output = 0
max_out_name = ''
max_out_inputs = []
for node in output_array:
    if len(parse(node)) > largest_output:
        largest_output = len(parse(node))
        max_out_name = node
        max_out_inputs = parse(node)

print('Output ', max_out_name, '\n', largest_output, ' inputs -->', max_out_inputs)
lines = [str(max_out_name) + '\n', ', '.join(max_out_inputs) + '\n' + ', '.join(input_array) + '\n' + ', '.join(output_array)]
origfilenamepath = os.path.basename(sys.argv[1])
origfilename = os.path.splitext(origfilenamepath)[0]
new = open(origfilename+'_perturb_me.txt', 'w')
new.writelines(lines)
new.close()
