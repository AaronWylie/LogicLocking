import sys
import os
import random

def readbench(benchfile):
  fp = open(benchfile,'r')
  data = fp.readlines()
  eof = len(data)
  fp.close()
  inputs = []
  outputs = []
  gates = []
  nodes = []
  num = 0
  while(num<eof):
    line = data[num].strip().replace(' ','')
    num += 1
    if len(line)==0 or line[0]=='#':
      continue
    elif line.find('INPUT(')!=-1:
      inputs.append(line[line.find('(')+1:line.find(')')])
    elif line.find('OUTPUT(')!=-1:
      outputs.append(line[line.find('(')+1:line.find(')')])
    elif line.find('=')!=-1:
      gates.append(line)
  nodes += inputs
  for gate in gates:
    node = gate[:gate.find('=')]
    nodes.append(node)
  return inputs, outputs, gates, nodes  
  
circuitgraph={}

def bckgates(item):
  if (circuitgraph['type'][item]=='PI'):
    result=[]
  else:
    if (circuitgraph['processed_bck'][item]==1):
      result=circuitgraph['bck_gates'][item]
    else:
      a=circuitgraph['inputs'][item]
      result=[]
      for i in range(0,len(a)):
        item0=a[i]        
        if (circuitgraph['processed_bck'][item]==0):
          result+=[item0]
          result+=bckgates(item0)
  result=list(set(result))
  circuitgraph['processed_bck'][item]=1
  circuitgraph['bck_gates'][item]=result
  return result                              # result is the bacgates' list

def fwdgates(item):
  if (circuitgraph['type'][item]=='PO'):
    result=[]
  else:
    if (circuitgraph['processed'][item]==1):
      result=circuitgraph['fwd_gates'][item]    
    else:
      a=circuitgraph['fanout'][item]
      result=[]
      for i in range(0,len(a)):
        item0=a[i]
        result+=[item0]
        result+=fwdgates(item0)    
  result=list(set(result))
  circuitgraph['processed'][item]=1
  circuitgraph['fwd_gates'][item]=result
  return result

def findPO(item):
  result=[]
  a=circuitgraph['fwd_gates'][item]
  for i in range(0,len(a)):
    item0=a[i]
    if (circuitgraph['type'][item0]=='PO'):
      result+=[item0]
  return result

def findPI(item):
  result=[]
  a=circuitgraph['bck_gates'][item]
  for i in range(0,len(a)):
    item0=a[i]
    if (circuitgraph['type'][item0]=='PI'):
      result+=[item0]
  return result    

def createcircuitgraph(inputs, outputs, gates, nodes):
  circuitgraph['name']={}
  circuitgraph['inputs']={}
  circuitgraph['type']={}
  circuitgraph['func']={}
  circuitgraph['processed']={}
  circuitgraph['processed_bck']={}
  circuitgraph['bck_gates']={}
  circuitgraph['fwd_gates']={}
  circuitgraph['fanout']={}
  circuitgraph['fwd_PO']={}               # just select PO from the list of fwd_gates
  circuitgraph['bck_PI']={}               # just select PI from the list of bck_gates

  for i in range(0,len(nodes)):
    item=nodes[i]
    circuitgraph['fanout'][item]=[]
  
  for i in range(0, len(inputs)):
    item=inputs[i]
    circuitgraph['name'][item]=item
    circuitgraph['inputs'][item]=[]
    circuitgraph['type'][item]="PI"
    circuitgraph['func'][item]="" 
      
  for i in range(0,len(gates)):
    item = gates[i]
    index1 = item.find('=')
    index2 = item.find('(')
    index3 = item.find(')')
    item1 = item[0:index1]                 # gate_name
    item2 = item[index1+1:index2]          # gate_function
    item3 = item[index2+1:index3]          # inputs
    circuitgraph['name'][item1]=item1
    circuitgraph['func'][item1]=item2
    if item1 in outputs:
      circuitgraph['type'][item1]="PO"
    else:
      circuitgraph['type'][item1]='internal'   
    b=item3.split(',')
    circuitgraph['inputs'][item1]=b
    for j in range(0,len(b)):
      c=b[j]
      circuitgraph['fanout'][c]+=[item1]           
  for i in range(0, len(nodes)):
    item=nodes[i]
    circuitgraph['processed'][item]=0
    circuitgraph['processed_bck'][item]=0
  for i in range(0,len(nodes)):    
    item=nodes[i]
    circuitgraph['bck_gates'][item]=bckgates(item)
    circuitgraph['fwd_gates'][item]=fwdgates(item)  
  for i in range(0,len(nodes)):
    item=nodes[i]
    circuitgraph['fwd_PO'][item]=findPO(item)
    circuitgraph['bck_PI'][item]=findPI(item)

  return circuitgraph

def build_cone(out, bm_name, inputs):
	fp = open(bm_name+'_'+out+'.bench','w')
	for in1 in inputs:
		fp.write('INPUT('+in1+')\n')
	fp.write('OUTPUT('+out+')\n')
	for gate_output in circuitgraph['bck_gates'][out]+[out]:
		if circuitgraph['type'][gate_output]=='PI':
			continue
		gate = gate_output + '=' + circuitgraph['func'][gate_output]+'('
		for in1 in circuitgraph['inputs'][gate_output]:
			gate += in1+','
		gate+='#'
		gate = gate.replace(',#',')')
		fp.write(gate + '\n')
	fp.close()

def main():
  circuitbench = sys.argv[1]
  bm_name = circuitbench.replace('.bench','') 
  inputs, outputs, gates, nodes = readbench(circuitbench)
  createcircuitgraph(inputs, outputs, gates, nodes)
  print len(inputs)
  for out in outputs:
	  print out, len(circuitgraph['bck_PI'][out])
	  build_cone(out, bm_name, inputs) 
  
main()
