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

    def getGraphObj(self, polyRec, place=None, lineWidth=5, color="red", type=Polygon,
                    width=800, height=600):
        polyV = polyRec[0]
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
                pointA.append(Point(((pts[0] - x0) * xScale),
                                    height - ((pts[1] - y0) * yScale)))
            pointA.append(Point(((pts[0] - x0) * xScale), height))
            poly = Polygon(pointA)
            poly.setWidth(lineWidth)
            poly.setFill(color)
            if place is not None:
                poly.move(place[0], place[1])
            return graphObj([poly])
        elif type == Rectangle:
            for i in range(0, len(polyV) - 1):
                rect = Rectangle(Point(polyV[i][0] * xScale, 50),
                                 Point(polyV[i+1][0] * xScale, 0))
                yFrac = 255*(polyV[i][1] - y0) / dy
                aColor = color_rgb(int(yFrac % 255),
                                   int((255 - yFrac) % 255),
                                   int((128 + yFrac) % 255))
                rect.setFill(aColor)
                rect.setWidth(lineWidth)
                pointA.append(rect)
                if place is not None:
                    rect.move(place[0], place[1])
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
            return graphObj(pointA)
        return None

        

#win=GraphWin()
from space import *


yy = population()
# #default bldg shape [1, 8, 1, 8]
bldg = building(yy)

# #adds minimal depth tree of bars
yy.populate(typ=dispatch["bar"], num=8)

# #adds 8 people to one apt.
yy.populate(num=8, pathIn=[1, 1])

yy.setInfPct(.1)  # #default 25s%

yy.connectTypes("person", "bar", 2)

import pdb; pdb.set_trace()
#levels = yy.findLevels()
#yy.showPaths()
yy.prune()
yy.showPaths()
yy.showInfState()

rec = yy.step(5, follow=True, display=record)
personGraphData = rec.graphData(person)
pathGraphData = rec.graphData(path)
nodeGraphData = rec.graphData(node, building)
dis = display()

for i in range(0,len(pathGraphData[0])):
    pth_id = pathGraphData[0][i]
    polyRec = pathGraphData[1][i]
    grafObj = dis.getGraphObj(polyRec, type=Line)
    if grafObj is not None:
        grafObj.draw(dis.win)
        clickPoint = dis.win.getMouse()
        grafObj.undraw()
        next
    assert(False)

for pers in yy.cng.persons:
    if (pers._exposure != 0):
        polys = rec.createPolys(pers.name, person, 3)  # #exposure
        grafObj = dis.showGraph(polys, type=Rectangle)
        if grafObj is not None:
            grafObj.draw(dis.win)
            clickPoint = dis.win.getMouse()
            grafObj.undraw()

for nd in yy.cng.names.values():
    if not isinstance(nd, person):
        polys = rec.createPolys(nd.name, node) #3 now 'best"
        grafObj = rec.showGraph(polys)  # #default display uses GrafObj
        if grafObj is not None:
            grafObj.draw(dis.win)
            clickPoint = dis.win.getMouse()
            grafObj.undraw()

dis.win.close()

# #rect is [rectangles] to be used for display, returned if not furnished
# #origin is point1 of first returned rectangle
