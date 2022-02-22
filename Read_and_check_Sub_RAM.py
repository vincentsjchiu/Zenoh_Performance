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
for index in range(1):
  dir_name = 'C:\\data\\Sub\\'+str(index)+'\\'
# Get list of all files only in the given directory
  list_of_files = filter( os.path.isfile,
                        glob.glob(dir_name + '*') )
# Sort list of files based on last modification time in ascending order
  list_of_files = sorted( list_of_files,
                       key = os.path.getmtime)

  for i in range(len(list_of_files)):
    list_of_files = filter( os.path.isfile,glob.glob(dir_name + 'Sub_RAM_*') )
# Sort list of files based on last modification time in ascending order
    list_of_files = sorted( list_of_files,key = os.path.getmtime)
  
  y.append(np.loadtxt(list_of_files[0]))
  #y.append(list_of_files[0])


for pindex in range(1):
  plt.plot((10/3600)*np.arange(0,len(y[pindex])),y[pindex])

plt.xlabel("Time (hours) ",fontsize=13)
plt.xlim(0,5.5)
plt.ylabel("Memory Usage (MB)",fontsize=13)
plt.title('Memory Usage of Subscriber')
plt.show()
