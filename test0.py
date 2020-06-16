from space import *

import pdb; pdb.set_trace()

lb = person("len")
sarah = person("sarah")
lb.infected = True
test = composite("task", 0)
# #gerry = person("gerry")
# #gerry.addPath([gerry, test])
# #lb.addPath([lb, test])
sarah.protect(.8)
pt = test.pathTo([1, 2], lb)
lb.addPath(pt)
sarah.addPath(node.path([sarah, test]))
cng.time.reset()
cng.time.step()
# #print("\nNode procesed:\t"+str(cng.time.processNextNode()))
# ##print("\nNode processed:\t"+str(cng.time.processNextNode()))
# #cng.time.finish()
print(cng.time)
