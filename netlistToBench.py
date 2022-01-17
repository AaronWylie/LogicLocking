####### Writing bench file from dc_shell netlist of locked verilog circuit ###########
import os
import sys
#from tkinter import Tk     # from tkinter import Tk for Python 3.x
#from tkinter.filedialog import askopenfilename
#Tk().withdraw()


############## take inputs and outputs ################
def readfile(origfile):
  fp = open(origfile,'r')
  data = fp.readlines()
  eof = len(data)
  fp.close()
  inputs = ''
  outputs = ''
  num = 0
  while(num<eof):
    line = data[num].strip().replace(' ','')
    num += 1
    if len(line)==0 or line[0:1]=='//':
      continue
    elif line.find('input',0,5)!=-1:
        if line.find(';')!=-1:
            inputs=inputs+str(line[5:line.find(';')])
        else:
            inputs=inputs+(line[5:])
            nextline = num
            subline = data[nextline]
            while subline.find(';')==-1:
                inputs = inputs+subline.strip()
                nextline += 1
                subline = data[nextline]
            inputs = inputs+subline[0:-2]
        inputs = [x.strip() for x in inputs.split(',')]
    elif line.find('output')!=-1:
        if line.find(';')!=-1:
            outputs=outputs+str(line[6:line.find(';')])
        else:
            outputs=outputs+(line[6:])
            nextline = num
            subline = data[nextline]
            while subline.find(';')==-1:
                outputs=outputs+subline.strip()
                nextline += 1
                subline = data[nextline]
            outputs = outputs+subline[0:-2]
        outputs = [x.strip() for x in outputs.split(',')]
  return inputs, outputs

############################ create gates and print it into new file ################################
#                                                               Currently supports INV, AND2, OR2   #
def make_new_data(inputs, outputs, origfile):
    newData = []
    for i in inputs:
        newData.append('INPUT('+i+')\n')
    for i in outputs:
        newData.append('OUTPUT('+i+')\n')
    # write logic gates
    fp = open(origfile, 'r')
    data = fp.readlines()
    eof = len(data)
    fp.close()
    origfilenamepath = os.path.basename(origfile)
    origfilename = os.path.splitext(origfilenamepath)[0]
    num = 0
    data[num] = data[num].lstrip()

    while num < eof:
        line = data[num].strip().replace(' ','')
        num += 1
        if len(line) == 0 or line[0:1] == '//':
            continue
        # not
        elif line.find('INV_X1')!=-1:
            newData.append(str(line[line.find('.ZN')+4:-3]+'=NOT('+line[line.find('.A')+3:line.find(',')]+'\n'))  
        #xnor
        elif line.find('XNOR')!=-1:
            newData.append(
                str(line[line.find('.ZN') + 4:-3] + '=XNOR(' + line[line.find('.A') + 3:line.find(',')-1]
                    + ','+ line[line.find('.B(')+ 3:line.find(',',line.find(',')+1)]+'\n'))      
          #nor
        elif line.find('NOR2_')!=-1:
            newData.append(
                str(line[line.find('.ZN') + 4:-3] + '=NOR(' + line[line.find('.A1') + 4:line.find(',')-1]+','
                    + line[line.find('.A2(')+4:line.find(',',line.find(',')+1)]+'\n'))
        #xor
        elif line.find('XOR2_X1')!=-1:
            newData.append(
                str(line[line.find('.Z') + 3:-3] + '=XOR(' + line[line.find('.A') + 3:line.find(',')-1]
                    + ','+ line[line.find('.B(')+ 3:line.find(',',line.find(',')+1)]+'\n')) 
          #or
        elif line.find('OR2_X1')!=-1:
            newData.append(
                str(line[line.find('.ZN') + 4:-3] + '=OR(' + line[line.find('.A1') + 4:line.find(',')-1]+','
                    + line[line.find('.A2(')+4:line.find(',',line.find(',')+1)]+'\n'))
          #nand
        elif line.find('NAND2_')!=-1:
            newData.append(
                str(line[line.find('.ZN') + 4:-3] + '=NAND(' + line[line.find('.A1') + 4:line.find(',')-1]+','
                    + line[line.find('.A2(')+4:line.find(',',line.find(',')+1)]+'\n'))
            #and
        elif line.find('AND2_X1')!=-1:
            newData.append(
                str(line[line.find('.ZN') + 4:-3] + '=AND(' + line[line.find('.A1') + 4:line.find(',')-1]+','
                    + line[line.find('.A2(')+4:line.find(',',line.find(',')+1)]+'\n'))  
            #buf
        elif line.find('assign')!=-1:
            line = data[num-1].strip()
            e = line[:-1].split(' ')
            newData.append(str(e[1] + '=BUF(' + e[3] + ')\n'))
                    
                    
    make_new_file(newData, os.path.splitext(origfile)[0])


def make_new_file(newData,origfilename):
    new = open(origfilename[0:-8]+'.bench','w')
    new.writelines(newData)
    new.close()

def main():
    origfile = sys.argv[1]
    inputs, outputs = readfile(origfile)
    make_new_data(inputs, outputs, origfile)

main()