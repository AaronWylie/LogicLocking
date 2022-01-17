####### Outline of writing locked verilog circuit from old circuit ###########
import os
import secrets
import sys


############## get inputs/outputs ################
def readfile(origfile):
  fp = open(origfile,'r')
  data = fp.readlines()
  eof = len(data)
  fp.close()
  inputs = data[2].strip().split(',')
  outputs = data[3].strip().split(',')
  return inputs, outputs
############################################################


def add_locked_output(outputs,modifiedSignal):
    newoutputs = [w.replace(modifiedSignal, modifiedSignal+'') for w in outputs]
    return newoutputs

def makeKeys(associatedInputs):
    keys = []
    for i in range(len(associatedInputs)):
        keys.append('keyinput_'+str(i))
    return keys

def lock_file(origfile,inputs,newoutputs, keys, modifiedSignal, associatedInputs):
  fp = open(origfile,'r')
  data = fp.readlines()
  eof = len(data)
  fp.close()
  origfilenamepath = os.path.basename(origfile)
  origfilename = os.path.splitext(origfilenamepath)[0]
  num = 0
  data[num] = data[num].lstrip()
  while(num<eof):
    line = data[num].strip().replace(' ','')
####################################################### based on code by Zhaokun
    if len(line)==0 or line.find('//')!=-1 or line.find('/*')!=-1:
        num+=1
        continue
    elif line.find('module')==-1 and line.find('input')==-1 and line.find('output')==-1 and\
            line.find('wire')==-1 and line.find('assign')==-1 and line.find('endmodule')==-1:
        if data[num-1].find('wire')!=-1:
          line1 = data[num].strip().replace(' ','')
          while line1.find(';')==-1:
            num += 1
            line1 = data[num].strip().replace(' ','')
          data.insert(num+1,'wire '+modifiedSignal+'_orig, '+modifiedSignal+'_fsc, '+'w_perturb, w_restore;\n')
          num += 2
          eof += 1
          
        else:
          del data[num]
        continue
    elif line.find(origfilename)!=-1:
      data[num] = 'module ' + origfilename + '_sfll(' + ','.join(inputs) +','+ ','.join(keys) + ',' + ','.join(newoutputs) + ');\n'
    elif line.find('input')!=-1:
      data[num] = 'input '+ ','.join(inputs) + ',' + ','.join(keys) + ';\n'
    elif line.find('output')!=-1:
        data[num] = 'output '+','.join(newoutputs)+';\n'
    elif line.find(modifiedSignal+'=',6,line.find('=')+1)!=-1:
        data[num] = 'assign '+modifiedSignal+'_orig '+line[line.find(modifiedSignal)+len(modifiedSignal):line.find(';')+1]+'\n'
    elif line.find('endmodule')!=-1:
        restoreLogic = '~('
        key = bin(secrets.randbelow(pow(2, len(associatedInputs))))[2:].zfill(len(associatedInputs))
        new = open(os.path.splitext(origfile)[0] + '_key.txt', 'w')
        new.writelines(key[key.find('b')+1:])
        new.close()
        for j in range(len(associatedInputs)-1):
            restoreLogic = restoreLogic + '('+str(keys[j])+'^'+str(associatedInputs[j])+') | '
        restoreLogic = restoreLogic + '('+str(keys[-1])+'^'+str(associatedInputs[-1])+'));'

        lock = 'assign w_perturb = ('
        for j in range(len(associatedInputs)):
            if key[j] == '1':
                lock = lock + associatedInputs[j]
            else:
                lock = lock + '~' + associatedInputs[j]
            if j != len(associatedInputs)-1:
                lock = lock + ' & '
            else:
                lock = lock + ');\n'
        data.insert(num, lock)
        data.insert(num+1, 'assign '+modifiedSignal+'_fsc = ('+str(modifiedSignal)+'_orig ^ w_perturb);\n')
        data.insert(num+2, 'assign w_restore = '''+str(restoreLogic)+'\n')
        data.insert(num+3, 'assign '+str(modifiedSignal)+' = ('+str(modifiedSignal)+'_fsc ^ w_restore);\n')
        num += 3
        eof += 3
        break
    num += 1
  make_new_file(data,os.path.splitext(origfile)[0])

def make_new_file(data,origfilename):
    new = open(origfilename+'_sfll.v','w')
    new.writelines(data)
    new.close()

def main():
    origfile = sys.argv[1]
    perturbme = sys.argv[2]
    gates = open(perturbme,'r')
    data = gates.readlines()
    modifiedSignal = data[0].strip().replace(' ','')
    associatedInputs = [item.strip() for item in data[1].split(',')]
    inputs, outputs = readfile(perturbme)
    newoutputs = add_locked_output(outputs, modifiedSignal)
    keys = makeKeys(associatedInputs)
    lock_file(origfile, inputs, newoutputs, keys, modifiedSignal, associatedInputs)

main()
