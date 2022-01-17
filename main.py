### Top Level Script to run Logic Locking on Bench Circuit Files ###
#
#  Scripts to include in current path when running main()
#    
#      bench_2.py
#      VerilogLocking.py
#      netlistToBench.py
#
#      abc
#      .tcl files of specific bench being locked
#      original .bench file*******
#
#  *********Bench files must have capitalized gate names in the file (i.e. NAND, NOR, XOR)
#
#  
#
#                Example:  python3 main.py specifyBenchCircuit.bench
#
#
#
#    RTL.TCL FILES MUST BE MODIFIED FOR SPECIFIC GATES AND BENCH FILES (ORIGINAL AND LOCKED)






import os
import time
import sys

bfile = sys.argv[1]
os.system(str("python3 bench_2.py " + bfile))
origfilenamepath = os.path.basename(bfile)
base = os.path.splitext(origfilenamepath)[0]
os.system("~/abc -c \"read_bench " + bfile + "; write_verilog " + base + ".v\"")
time.sleep(1)
os.system(str("python3 VerilogLocking.py " + base + ".v " + base + "_perturb_me.txt"))
os.system("source /opt/coe/synopsys/syn/P-2019.03-SP3/setup.syn.sh")
os.system("dc_shell -f " + base + "_rtl.tcl")
os.system("dc_shell -f " + base + "_sfll_rtl.tcl")
os.system("python3 netlistToBench.py " + base + "_sfll_netlist.v")

print('\n')
###### Time #########
fp = open(base+"_time.rpt", 'r')
data = fp.readlines()
fp.close()
oldtime = float((data[-4][data[-4].find(')')+1:].strip()))
fp = open(base+"_sfll_time.rpt", 'r')
data = fp.readlines()
fp.close()
newtime = float((data[-4][data[-4].find(')')+1:].strip()))
print("Time overhead: ", "{:.2f}".format(((oldtime-newtime)/oldtime)*100, '\n'), "% ")
######################

###### Power #########
fp = open(base+"_power.rpt", 'r')
data = fp.readlines()
fp.close()
oldpower = float(data[-2].split()[7])
fp = open(base+"_sfll_power.rpt", 'r')
data = fp.readlines()
fp.close()
newpower = float(data[-2].split()[7])
print("Power overhead: ", "{:.4f}".format(((newpower-oldpower)/oldpower)*100, " ",  data[-2].split()[8], '\n'), "%")
######################

###### Area #########
fp = open(base+"_area.rpt", 'r')
data = fp.readlines()
fp.close()
oldarea = float(data[-3].split()[3])
fp = open(base+"_sfll_area.rpt", 'r')
data = fp.readlines()
fp.close()
newarea = float(data[-3].split()[3])
print("Area overhead: ", "{:.4f}".format(((newarea-oldarea)/oldarea)*100, '\n'), "% ")
######################