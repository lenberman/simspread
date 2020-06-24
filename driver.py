from space import *

# #import pdb; pdb.set_trace()

# #x = dispatch["room"]("ROOM")


import pdb; pdb.set_trace()
yy = population()
# #default bldg shape [1, 8, 1, 8]
bldg = building(yy)
# #adds 8 people to one apt of bldg
yy.populate(num=8, pathIn=[1, 1])
# #adds minimal depth tree of bars
yy.populate(typ=dispatch["bar"], num=8)
yy.connectTypes("person", "bar", 1)
levels = yy.findLevels()
#yy.showPaths()
yy.prune()
yy.showPaths()
import pdb; pdb.set_trace()


for i in range(0,5):
    yy.setInfPct(.1)  # #default 25s%
    print("Disease dose: " + str(yy.cng.disease.dose))
    yy.step(500, follow=False)
    pdb.set_trace()
    yy.cng.disease.dose *= 2
    yy.cng.disease.diseaseRecord = {}




#
#xx = population()
#xx.populate(typ=person, num=100)
## #
#xx.populate(typ=dispatch["bar"], num=8)
#xx.setInfPct(.1)  # #default 25s%
#xx.connectTypes("person", "bar")
#xx.findLevels()
#xx.showPaths()
#xx.prune()
#xx.showPaths()
#xx.showInfState()
import pdb; pdb.set_trace()
#xx.step(5, follow=True)


print("Finished")
