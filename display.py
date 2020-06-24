from space import *
from graphics import *

#import pdb; pdb.set_trace()


def xSpan(data):  # # assuming data monotonic in 1st two coor.
    return [data[0][0], data[len(data)-1][1]]


def ySpan(data, j=3):
    # #j=3->field,=4->exposure,5(person)infected,
    mm = [2**20, -2**20]
    for i in range(0, len(data)):
        mm[0] = min(mm[0], data[i][j])
        mm[1] = max(mm[1], data[i][j])
    return mm


def colorVertices(poly, dis, color="red"):
    vs = []
    for pt in poly.getPoints():
        cir = Circle(pt, 5)
        cir.setWidth(5)
        cir.setFill(color)
        cir.draw(dis)
        vs.append(cir)
    return vs

        
def getIthData(data, i):
    if len(data) <= i:
        return None
    return data[i]


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

    def __init__(self, pop, title="DataDisplay", height=600, width=800):
        self.pop = pop
        self.win = GraphWin(title, width, height)
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

    def rData(self):
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
            if path._id not in self.pathData.keys():
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

    def createPolys(self, id, theClass, jth, rng=[0, 2**20]):
        # #returns [vertices of values, enclosing rectangle]
        
        data = self._getData(id, theClass)
        xRange = xSpan(data)
        xRange = [max(rng[0], xRange[0]), min(rng[1], xRange[1])]
        yRange = ySpan(data, jth)

        numMeasurements = len(data)
        # #arrays of  polygon points for field (& exposure if person or path)
        fieldA = []
        for i in range(0, numMeasurements):
            ithData = getIthData(data, i)
            fieldA.append([ithData[0], ithData[jth]])
        return [fieldA, [xRange, yRange]]

    def showGraph(self, polyRec, place=None, lineWidth=5, color="red", type=Polygon):
        polyV = polyRec[0]
        width = self.win.getWidth()
        height = self.win.getHeight()
        pointA = []
        [[x0, xm], [y0, ym]] = polyRec[1]
        dx = xm - x0 * 1.0
        dy = ym - y0 * 1.0
        if dx == 0.0 or dy == 0.0:
            return None
        xScale = width / dx
        yScale = height / dy
        if type == Polygon:
            for pts in polyV:
                pointA.append(Point(((pts[0] - x0) * xScale), height - ((pts[1] - y0) * yScale)))
            pointA.append(Point(((pts[0] - x0) * xScale), height))
            poly = Polygon(pointA)
            poly.setWidth(lineWidth)
            poly.setFill(color)
            if place is not None:
                poly.move(place[0], place[1])
            poly.draw(self.win)
            return poly
        elif type == Rectangle:
            for i in range(0,len(polyV) - 1):
                rect = Rectangle(Point(polyV[i][0] * xScale, 50), Point(polyV[i+1][0] * xScale, 0))
                yFrac = 255*(polyV[i][1] - y0) / dy
                aColor = color_rgb(int(yFrac % 255),
                                   int((255 - yFrac) % 255),
                                   int((128 + yFrac) % 255))
                rect.setFill(aColor)
                rect.setWidth(lineWidth)
                pointA.append(rect)
                if place is not None:
                    rect.move(place[0], place[1])
                rect.draw(self.win)
            return graphObj(pointA)
        elif type ==  Line:
            for i in range(0,len(polyV) - 1):
                line = Line(Point(polyV[i][0] * xScale, 0), Point(polyV[i+1][0] * xScale, 0))
                yFrac = 255*(polyV[i][1] - y0) / dy
                aColor = color_rgb(int(yFrac % 255),
                                   int((255 - yFrac) % 255),
                                   int((128 + yFrac) % 255))
                line.setFill(aColor)
                line.setWidth(lineWidth)
                pointA.append(line)
                if place is not None:
                    line.move(place[0], place[1])
                line.draw(self.win)
            return graphObj(pointA)
        return None
        


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
dis = yy.step(5, follow=True, display=display)

for nd in yy.cng.names.values():
    if not isinstance(nd, person):
        polys = dis.createPolys(nd.name, node, 2)
        polygon = dis.showGraph(polys)  # #default display uses Polygon
        if polygon is not None:
            clickPoint = dis.win.getMouse()
            polygon.undraw()

for pth in yy.paths["person"]:
    polys = dis.createPolys(pth._id, path, 3)  # #exposure
    polygon = dis.showGraph(polys, type=Line)
    if polygon is not None:
        clickPoint = dis.win.getMouse()
        polygon.undraw()

for pers in yy.cng.persons:
    if (pers._exposure != 0):
        polys = dis.createPolys(pers.name, person, 3)  # #exposure
        polygon = dis.showGraph(polys, type=Rectangle)
        if polygon is not None:
            clickPoint = dis.win.getMouse()
            polygon.undraw()

dis.win.close()

# #rect is [rectangles] to be used for display, returned if not furnished
# #origin is point1 of first returned rectangle
