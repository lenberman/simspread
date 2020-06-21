from space import *

# #import pdb; pdb.set_trace()

# #x = dispatch["room"]("ROOM")


import pdb; pdb.set_trace()

yy = population()
# #default bldg shape [1, 8, 1, 8]
bldg = building(yy)

# #adds minimal depth tree of bars
yy.populate(typ=dispatch["bar"], num=8)

# #adds 8 people to one apt.
yy.populate(num=8, pathIn=[1, 1])

yy.setInfPct(.1)  # #default 25s%
yy.connectTypes("person", "bar", 2)
levels = yy.findLevels()
yy.showPaths()
yy.prune()
yy.showPaths()
yy.showInfState()
import pdb; pdb.set_trace()
yy.step(5, follow=True)





xx = population()
xx.populate(typ=person, num=100)
# #
xx.populate(typ=dispatch["bar"], num=8)
xx.setInfPct(.1)  # #default 25s%
xx.connectTypes("person", "bar")
xx.findLevels()
xx.showPaths()
xx.prune()
xx.showPaths()
xx.showInfState()
import pdb; pdb.set_trace()
xx.step(5, follow=True)


print("Finished")
