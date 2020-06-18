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
xx.showPaths()
xx.showInfState()
import pdb; pdb.set_trace()
xx.step(5, follow=True)


print("Finished")
