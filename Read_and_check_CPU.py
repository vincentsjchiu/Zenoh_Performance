import sys
import time
import datetime
import glob
import os
import time
import math
import matplotlib.pyplot as plt
import numpy as np
y=[]
cal=[]
for index in range(8):
  dir_name = 'C:\\data\\'+str(index)+'\\'
# Get list of all files only in the given directory
  list_of_files = filter( os.path.isfile,
                        glob.glob(dir_name + '*') )
# Sort list of files based on last modification time in ascending order
  list_of_files = sorted( list_of_files,
                       key = os.path.getmtime)

  for i in range(len(list_of_files)):
    list_of_files = filter( os.path.isfile,glob.glob(dir_name + 'CPU_*') )
# Sort list of files based on last modification time in ascending order
    list_of_files = sorted( list_of_files,key = os.path.getmtime)
  
  #y.append(np.loadtxt(list_of_files[0]))
  y.append(list_of_files[0])
  print(y)

for pindex in range(8):
  plt.plot(range(0,len(y[pindex])),y[pindex])

plt.xlabel("Index ",fontsize=13)
plt.ylabel("CPU Usage (%)",fontsize=13)
plt.title('CPU Usage of Each Publisher')
plt.show()
'''
