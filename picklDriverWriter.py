import pickle
from space import *

# #import pdb; pdb.set_trace()

# #x = dispatch["room"]("ROOM")


import pdb; pdb.set_trace()


xx = population()
xx.populate(typ=person, num=100)
# #
xx.populate(typ=dispatch["bar"], num=8)
xx.setInfPct(.1)  # #default 25s%
xx.connectTypes("person", "bar")
xx.showPaths()
xx.prune()

output = open('driver.pkl', 'wb')

pickle.dump(xx, output, -1)
pickle.dump(cng, output, -1)
output.close()
print("Pre-pickling output")
xx.showPaths()
xx.showInfState()
xx.step(5, follow=True)

import pdb; pdb.set_trace()
print("Finished")
