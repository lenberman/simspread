from space import *
from graphics import *

#import pdb; pdb.set_trace()


def colorVertices(poly, dis, color="red"):
    vs = []
    for pt in poly.getPoints():
        cir = Circle(pt, 5)
        cir.setWidth(5)
        cir.setFill(color)
        cir.draw(dis)
        vs.append(cir)
    return vs


class graphObj:

    def __init__(self, array):
        self.array = array

    def undraw(self):
        for i in self.array:
            i.undraw()

    def draw(self, win):
        for i in self.array:
            i.draw(win)


class display:

    def __init__(self, title="DataDisplay", height=600, width=800):
        self.win = GraphWin(title, width, height)

    def __str__(self):
        return "Display(" + self.win.getWidth() + ", " + self.win.getHeight() + ")"

    def __del__(self):
        self.win.close()


#win=GraphWin()


yy = population()
# #default bldg shape [1, 8, 1, 8]
bldg = building(yy)

# #adds minimal depth tree of bars
yy.populate(typ=dispatch["bar"], num=8)

# #adds 8 people to one apt.
yy.populate(num=8, pathIn=[1, 1])

yy.setInfPct(.1)  # #default 25s%

yy.connectTypes("person", "bar", 2)

#levels = yy.findLevels()
#yy.showPaths()
yy.prune()
yy.showPaths()
yy.showInfState()
import pdb; pdb.set_trace()
rec = yy.step(5, follow=True, display=record)

for nd in yy.cng.names.values():
    if not isinstance(nd, person):
        polys = dis.createPolys(nd.name, node, 3) #3 now 'best"
        grafObj = dis.showGraph(polys)  # #default display uses GrafObj
        if grafObj is not None:
            clickPoint = dis.win.getMouse()
            grafObj.undraw()

for pth in yy.paths["person"]:
    polys = dis.createPolys(pth._id, path, 3)  # #exposure
    grafObj = dis.showGraph(polys, type=Line)
    if grafObj is not None:
        clickPoint = dis.win.getMouse()
        grafObj.undraw()

for pers in yy.cng.persons:
    if (pers._exposure != 0):
        polys = dis.createPolys(pers.name, person, 3)  # #exposure
        grafObj = dis.showGraph(polys, type=Rectangle)
        if grafObj is not None:
            clickPoint = dis.win.getMouse()
            grafObj.undraw()

dis.win.close()

# #rect is [rectangles] to be used for display, returned if not furnished
# #origin is point1 of first returned rectangle
