import sys
import os

#These make properly formated strings given triples of variables.

def make_AND_statement(output,input1,input2):
    return  "{} := {} AND {}".format(output, input1, input2)

def make_OR_statement(output,input1,input2):
    return  "{} := {} OR {}".format(output, input1, input2)

def make_XOR_statement(output,input1,input2):
    return  "{} := {} XOR {}".format(output, input1, input2)

def make_NAND_statement(output,input1,input2):
    return  "{} := {} NAND {}".format(output, input1, input2)


'''
Takes a file object f and a NAND line,
and writes a NAND line to the file with a newline character
'''
def write_NAND_line(f,line):
    f.write("%s\n" % line)

"""
Writes NAND triple (not line) to file
"""
def write_NAND_triple(f,output,x1,x2):
    line = make_NAND_statement(output,x1,x2)
    print(line)
    write_NAND_line(f,line)

'''
Writes any kind of line to file
'''
def write_DEBUG_line(f,line):
    f.write("%s\n" % line)


'''
Returns vars from OR line
'''
def parse_OR(line):
    # ASSUMES SPACING!
    vars = line.split()
    output = vars[0]
    input1 = vars[2]
    input2 = vars[4]
    return output, input1, input2


"""
Returns vars from XOR line
"""
def parse_XOR(line):
    # ASSUMES SPACING!
    # SAME FUNCTION AS parse_OR()
    vars = line.split()
    output = vars[0]
    input1 = vars[2]
    input2 = vars[4]
    return output, input1, input2

"""
Returns vars from AND line
"""
def parse_AND(line):
    # ASSUMES SPACING!
    # SAME FUNCTION AS parse_OR()
    vars = line.split()
    output = vars[0]
    input1 = vars[2]
    input2 = vars[4]
    return output, input1, input2

"""
Returns vars from NAND line
"""
def parse_NAND(line):
  vars = line.split()
  output = vars[0]
  input1 = vars[2]
  input2 = vars[4]
  return output, input1, input2

"""
Returns vars from MAJ line
"""
def parse_MAJ(line):
    words = line.split()
    output = words[0]
    variables = words[2].split(',')
    index = variables[0].index('(')
    input1 = variables[0][index+1:]
    input2 = variables[1]
    input3 = variables[2][:len(variables[2]) - 1]
    return output, input1, input2, input3


def get_var_name(counter):
    counter += 1
    return ("u_" + str(counter))

def get_var_name_special(counter):
    counter += 1
    return ("u_" + str(counter), counter)

"""
Takes an AND line and writes a series of NAND lines to file
"""
def write_AND_as_NAND(f, line, counter):
    output, x_0, x_1 = parse_AND(line)
    write_AND_triple_as_NAND(f, output,x_0,x_1,counter)
    return counter

"""
Takes an AND triple and writes a series of NAND lines to file
"""

def write_AND_triple_as_NAND(f, output,input1,input2,counter):
    temp = get_var_name(counter)
    write_NAND_triple(f, temp,input1,input2)
    write_NAND_triple(f, output,temp,temp)
    return counter + 1


"""
Takes an XOR line and writes a series of NAND lines to file
"""

def write_XOR_as_NAND(f, line, counter):
    output, x_0, x_1 = parse_XOR(line)
    temp1 = get_var_name(counter)
    temp2 = get_var_name(counter+1)
    temp3 = get_var_name(counter+2)
    write_NAND_triple(f,temp1, x_0, x_1)
    write_NAND_triple(f,temp2, x_0, temp1)
    write_NAND_triple(f,temp3, x_1, temp1)
    write_NAND_triple(f,output, temp2, temp3)
    return counter + 3


"""
Takes a MAJ line and writes a series of NAND lines to file
"""
def write_MAJ_as_NAND(f, line,counter):
  output, input1, input2, input3 = parse_MAJ(line)
  temp0 = get_var_name(counter)
  temp1 = get_var_name(counter+1)
  temp2 = get_var_name(counter+2)
  temp3 = get_var_name(counter+3)
  not3 = get_var_name(counter+4)
  write_NAND_triple(f,temp0, input1, input2)
  write_NAND_triple(f,temp1, input1, input3)
  write_NAND_triple(f,temp2,input2, input3)
  write_NAND_triple(f,temp3, temp2, temp1)
  write_NAND_triple(f,not3, temp3, temp3)
  write_NAND_triple(f,output, not3, temp0)
  return counter + 5
    # TODO

def NANDify(f,prog):
    counter = 0
    for line in prog:
        if "XOR" in line:
            counter = write_XOR_as_NAND(f, line, counter)
        elif "MAJ" in line:
            counter = write_MAJ_as_NAND(f, line, counter)
        else:
            write_NAND_line(f,line)



'''
multiply one binary number by each bit in another and store individual result
in a table with correct shift
'''

def multiply(f, n, num_a, num_b,counter):
    storage_array = []
    index_counter = 0
    for bit_a in num_a:
        temp_array = []
        for shift in range(index_counter):
            temp_array.append("z") # unitialised variable should always be 0
        index_counter += 1 #shifting function
        for bit_b in num_b:
            (temp_output_var, counter)  = get_var_name_special(counter)
            write_AND_triple_as_NAND(f, temp_output_var, bit_a, bit_b, counter)
            temp_array.append(temp_output_var)

        #temp_array.reverse()
        filler = (2*n - len(temp_array))
        zero = ["z"] * filler
        temp_array = temp_array + zero
        storage_array.append(temp_array)
        #temp_array.reverse()

    return (storage_array, counter)


'''
add all rows of table together
'''

def add(f,n, storage, counter):
    for l in range(0,len(storage) - 1):
        carry_variable = "z"
        temp_array = []

        for (a,b) in zip(storage[l], storage[l+1]):

            (first_xor_v, counter) = get_var_name_special(counter)

            counter = write_XOR_as_NAND(f, (str(first_xor_v) + " = " + str(a) + " xor " + str(b)), counter)
            (second_xor_v, counter) = get_var_name_special(counter)
            counter = write_XOR_as_NAND(f, (str(second_xor_v) + " = " + str(first_xor_v) + " xor " + str(carry_variable)), counter)
            temp_array.append(second_xor_v)

            (live_carry_variable, counter) = get_var_name_special(counter)
            #calculating carry
            counter = write_MAJ_as_NAND(f, (str(live_carry_variable) + " = maj(" + str(carry_variable) + "," + str(a)+ "," + str(b) + ")"), counter)
            carry_variable = live_carry_variable

        storage[l+1] = temp_array

        print(storage[len(storage) - 1])
    return(storage[len(storage) - 1], counter)

def get_output_var_name(counter_y):
    counter_y  += 1
    return ("y_" + str(counter_y), counter_y)

def get_input_var_name(counter_x):
    counter_x  += 1
    return ("x_" + str(counter_x), counter_x)

def create_input_lists(counter_x):
    list1 = []
    for i in range(512):
        (temp, counter_x) = get_input_var_name(counter_x)
        list1.append(temp)
    print(str(list1))
    return list1

'''
write out solution in correct form so nand code can output
'''

def parser(f,list, counter):
    counter_y = -1
    for i in list:
        (output_var, counter_y) = get_output_var_name(counter_y)
        (useless_var, counter) = get_var_name_special(counter)
        write_NAND_triple(f,useless_var,i,i)
        write_NAND_triple(f,output_var,useless_var,useless_var)



def main():
  outfile = open('converted.nand','w')
  (storage, counter) = multiply(outfile,512, (create_input_lists(-1)) ,(create_input_lists(511)),0)
  (flist, counter)  = add(outfile,512, storage, counter)
  parser(outfile,flist, counter)
  outfile.close()

if __name__ == "__main__":
    main()
