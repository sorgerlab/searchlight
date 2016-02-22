import time
import numpy as np
from searchlight import *


ut1 = np.loadtxt('ut1.tsv')
t1 = np.loadtxt('t1.tsv')
pdf = np.loadtxt('pdf.tsv')

start = time.time()
print 's1_opt', searchlight1_opt(ut1, t1, pdf), time.time() - start
