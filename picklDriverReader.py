import pickle
from space import *

# #import pdb; pdb.set_trace()

import pdb; pdb.set_trace()

pkl_file = open('driver.pkl', 'rb')

yy = pickle.load(pkl_file)


print("Pickled output")
yy.showPaths()
yy.showInfState()
yy.step(50, follow=True)

import pdb; pdb.set_trace()
print("Finished")
