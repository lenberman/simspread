from space import *
from graphics import *

#import pdb; pdb.set_trace()

def stepSpan(data):
    return [data[0][0], data[len(data)-1][1]]

def getIthData(data, i):
    if len(data) <= i:
        return None
    return data[i]

    


class display(GraphWin):

    def __init__(self, pop, title="DataDisplay", width=800, height=600):
        GraphWin.__init__(self, title, width, height)
        self.pop = pop
        # #self.win = GraphWin(width=800, height=600)
        # #{} of arrays of [lastStep, fieldStep, field, infected, exposure]
        self.pData = {}  # #indexed by name, ordered (by step)
        # #array of [lastStep, _fieldStep, scheduledAt, field]
        self.npData = {}  # # non-person nodes and paths
        # # path._id:array [currentStep, srcFieldAvailableTime, src.field,target.field, exposure]
        self.pathData = {} 
        self.displayStep = 0

    def __str__(self):
        return "Display " + pop.name + "("+ self.getWidth() +", " + self.getHeight() +")"

    def __del__(self):
        self.win.close()

    def rData(self, show=True):
        for nd in self.pop.cng.persons:
            if nd.name not in self.pData.keys():
                self.pData[nd.name] = []
            self.pData[nd.name].append([nd.lastStep, nd._fieldStep,
                                        nd._field, nd._exposure, nd.infected])
        for nd in self.pop.cng.names.values():
            if isinstance(nd, person):
                next
            if nd.name not in self.npData.keys():
                self.npData[nd.name] = []
            self.npData[nd.name].append([nd.lastStep, nd._fieldStep, nd._field,
                                         nd.scheduledAt])
        for path in self.pop.paths["person"]:
            if path not in self.pathData.keys():
                self.pathData[path._id] = []
            srcNode = path.getSrc()
            srcNodeAvailableTime = srcNode._fieldStep + srcNode.delay
            self.pathData[path._id].append(
                [self.pop.cng.time.currentStep, srcNodeAvailableTime,
                 srcNode._field, path._exposure, path.getTarget()._field])

    def _getData(self, id, theClass):
        if theClass == person:
            data = self.pData[id]
            return data
        if issubclass(theClass, node):
            data = self.npData[id]
            return data
        data = self.pathData[id]
        return data

    def createPolys(self, id, theClass, rng=[0, 2**20], width=3):
        # #rect is [rectangles] to be used for display, returned if not furnished
        # #origin is point1 of first returned rectangle
        # #returns array of rectangles which have been 
        
        data = self._getData(id, theClass)
        stepRange = stepSpan(data)
        stepRange = [max(rng[0], stepRange[0]), min(rng[1], stepRange[1])]
        numMeasurements = len(data)
        # #arrays of  polygon points for field (& exposure if person or path)
        fieldA = []
        exposureA = []
        exPoly = None
        for i in range(0,numMeasurements):
            ithData = getIthData(data, i)
            fieldA.append(Point(ithData[0], ithData[2]))
            if (theClass is person or theClass is path):
                exposureA.append(Point(ithData[0], ithData[2]))
        fieldA.append(Point(ithData[1], ithData[2]))
        if (theClass is person or theClass is path):
            exposureA.append(Point(ithData[1], ithData[2]))
        fieldPoly = Polygon(fieldA)
        if len(exposureA) > 0:
            exPoly = Polygon(exposureA)
            exPoly.setWidth(width)
        fieldPoly.setWidth(width)
        return [fieldPoly, exPoly]

    def showGraph(self, poly, place=None):
        if place is not None:
            poly.move(place[0], place[1])
        poly.draw(self)

            

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
#import pdb; pdb.set_trace()
dis = yy.step(5, follow=True, display=display)
[x, y] = [50, 50]
for pers in yy.cng.persons:
    if (pers._exposure != 0):
        polys = dis.createPolys(pers.name, person)
        dis.showGraph(polys[1], [x, y])
        y += 50
        dis.showGraph(polys[0], [x, y])
        y += 50
for nd in yy.cng.names.values():
    if not isinstance(nd, person):
        polys = dis.createPolys(nd.name, node)
        y += 50
        dis.showGraph(polys[1], [x, y])
        y += 50
        dis.showGraph(polys[0], [x, y])
