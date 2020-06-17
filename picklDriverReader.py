import pickle
from space import *

# #import pdb; pdb.set_trace()

import pdb; pdb.set_trace()

pkl_file = open('driver.pkl', 'rb')

yy = pickle.load(pkl_file)
cng = yy.cng

print("Pickled output")
yy.showPaths()
yy.showInfState()
yy.step(5, follow=True)

import pdb; pdb.set_trace()
print("Finished")
