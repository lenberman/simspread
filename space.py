#!/usr/bin/python3
# ##import pdb; pdb.set_trace()
import random
import statistics
import math
import sys

class disease:
    def __init__(self,
                 minutesPerStep=6,
                 asym=7200,  # #7200 minutes ~ 5 days asymptomatic
                 symp=10800,  # # 7.5 days of symtoms
                 psym=0,  # #contagious for this long after symptoms clear
                 abt=14400,  # # post-symtom appeearance of antibodies(min)
                 vdfHalfLifeMinutes=7200  #
):
        self.minutesPerStep = minutesPerStep
        # time(minutes) from exposure until onset of symptoms
        self.asym = asym
        # #duration of symptoms
        self.symp = symp
        # #contagious after symptoms
        self.psym = psym
        # #time from symptom onset to antibody
        self.serioconversion = abt
        # #how rapidly does vdf disperse.
        self.vdfDecayPerStepExp = \
            math.log(2.0)/(vdfHalfLifeMinutes/minutesPerStep)

    def infectivity(prsn):
        pass

    def antibody(prsn, nStep):
        pass


class future:

    def __init__(self):
        self.events = {}
        self.currentStep = 0
        self.maxStep = 0
        self.minutesPerStep = 6
        
    def __str__(self):
        rv = "Current " + str(self.currentStep) + ", max " + str(self.maxStep)
        rv += str(self.events)
        return rv

    def scheduleAt(self, nd, time):  # #reschedule if necessary
        assert(time >= self.currentStep)  # #don't schedule in past
        # #print("\nSchedule " + str(nd) + " at " + str(time))
        if isinstance(nd, node):
            nodeCurrentSchedule = nd.scheduledAt
            if nodeCurrentSchedule > time:
                return
        else:  # #could be a path end
            import pdb; pdb.set_trace()  
            nodeCurrentSchedule = -1
        self.maxStep = max(self.maxStep, time, nodeCurrentSchedule)
        if isinstance(nd, node):
            if nodeCurrentSchedule == time:
                ct = self.events.get(nodeCurrentSchedule)
                if ct is not None:
                    ct.remove(nd)
        ct = self.events.get(time)
        if ct is None:
            ct = []
            self.events[time] = ct
        nd.scheduledAt = time
        ct.append(nd)
        # #print(self)

    def initSim(self):
        self.currentStep += 1
        self.maxStep = max(self.maxStep, self.currentStep+1)
        assert(self == currentNodeGroup.time)
        for ii in currentNodeGroup.names.values():
            ii.reset()  # # reset
            if isinstance(ii, person) and ii.nextPath is not None:
                self.scheduleAt(ii, self.currentStep)
                pth = ii.paths[ii.nextPath]
                if pth.curLoc is None:
                    pth.curLoc = 0

    def popNextNode(self):  # #null when events array is empty
        nn = self.events.get(self.currentStep)
        if nn is None:
            while nn is None:
                if self.currentStep < self.maxStep:
                    self.currentStep += 1
                else:
                    return None
                nn = self.events.get(self.currentStep)
        if len(nn) == 0:
            # #increment clock
            self.events.pop(self.currentStep, None)
            self.currentStep += 1
            self.maxStep = max(self.maxStep, self.currentStep)
            return self.popNextNode()
        else:
            rv = nn[0]
            nn = nn[1:]
            self.events[self.currentStep] = nn
            assert(isinstance(rv, node) or isinstance(rv, node.path))
            if isinstance(rv, node):
                rv.scheduledAt = -1
            return rv

    def processNextNode(self):
        nd = self.popNextNode()
        if(nd is None):
            return None
        assert(isinstance(nd, node) or isinstance(nd, node.path))
        return nd.process()

    def step(self):  # #step(s) must be preceded by initSim
        self.finish()
        return "Done at time = " + str(self.currentStep)

    def finish(self, mStep=10000):  # #simulate currently scheduled nodes
        while self.currentStep <= max(self.maxStep, mStep):
            nd = self.processNextNode()
            if nd is None:
                # #print("\n\nCompleted DEPTH: " + str(self.currentStep))
                # #print("\t:maxStep:" + str(self.maxStep)+"\n")
                print(".", sep=' ', end='', file=sys.stdout, flush=False)
                return True
        return False

currentNodeGroup = None

class nodeGroup:
    def __init__(self):
        self.names = {}
        self.persons = []
        self.stepsPerDay = 1000
        self.time = future()
        self.seed = random.getstate()
        self.disease = disease()
        
currentNodeGroup = nodeGroup()

def getCurrentNodeGroup():
    return currentNodeGroup


class node:
    TYPES = ["ROOM", "PERSON", "BAR", "RESTAURANT", "STORE",  "MEDICAL", "BUS",
             "CAR", "CARRIAGE", "PLATFORM", "BUSSTOP",  "ELEVATOR", "STAIRWAY",
             "STREET", "COMPOSITE"]

    def reset(self):  # #for next step
        self.lastStep = self._fieldStep
        self._fieldStep = currentNodeGroup.time.currentStep

    def __init__(self, name, sqM=1, role=TYPES[0], field=0):
        self.name = name

        if name in currentNodeGroup.names:
            print("Recreating " + str(name))
        currentNodeGroup.names[name] = self
        self._field = field  # #infectivity
        self._fieldStep = currentNodeGroup.time.currentStep
        self._role = role
        self._sqM = sqM
        self.crowdFactor = 1
        self.delay = 1  # #steps ascribed to passage thru
        self.inReady = [[], [], []]  # #paths & field connections
        self.lastStep = currentNodeGroup.time.currentStep
        self.maxInReady = 2  # #stores available values 
        self.processInterval = 5
        self.scheduledAt = -1

    def __str__(self):
        nm = self.name
        if isinstance(self, person) and self._infected:
            nm = "<*" + self.name + "*>"
        val = nm + "(" + self._role
        val += ", field=" + str(self._field)
        val += ", lastStep=" + str(self.lastStep) + ")"
        val += str(self.inReady[0]) + ":" + str(self.inReady[1])
        return val

    def reschedule(self):
        currentNodeGroup.time.scheduleAt(
            self, currentNodeGroup.time.currentStep + self.processInterval)


        
    def process(self):
        # calculates new field value from InReady
        self.field = self.calculate()
        if (False):
            print("\nProcessing(" + str(self.name) + ") in:\t" +
                  str(self.inReady[0]) + ", field=" + str(self.field))
        #import pdb; pdb.set_trace()
        valA = self.inReady[0]
        stepA = self.inReady[1]
        pathA = self.inReady[2]
        v = []
        s = []
        p = []
        nProcessed = 0
        for i in range(len(pathA)):
            tPath = pathA[i]
            #  #values furnished by inReady have path curLoc at source
            #  #assert(self == tPath.nodes[tPath.curLoc+tPath.forward])
            prevNode = tPath.nodes[tPath.curLoc]
            pAvail = prevNode._fieldStep + prevNode.delay
            if pAvail <= self._fieldStep and nProcessed < self.maxInReady:
                #  #and pAvail > self.lastStep and 
                # #value from this path processed.  Respect maxInReady!
                tPath.curLoc += tPath.forward
                tPath.process()
                nProcessed += 1
            else:
                # #value this path next periodic activation
                v.extend([valA[i]])
                s.extend([stepA[i]])
                p.extend([pathA[i]])
        self.inReady = [v, s, p]
        if len(v) > 0:
            #  #import pdb; pdb.set_trace()
            self.reschedule()
        return self

    def calculate(self):  # #area weighted field of inputs
        valA = self.inReady[0]
        stepA = self.inReady[1]
        pathA = self.inReady[2]
        rv = 0
        total = 0.0
        assert(len(valA) == len(pathA))
        for i in range(0, len(valA)):
            path = pathA[i]
            step = stepA[i]
            dt = currentNodeGroup.time.currentStep - step
            if dt <0:
                continue
            assert(dt >= 0)
            factor = math.exp(currentNodeGroup.disease.vdfDecayPerStepExp * dt)
            val = valA[i]
            cNode = path.nodes[path.curLoc]
            thisVDFM2 = cNode._sqM
            total += (val * thisVDFM2 * factor)
        rv = (total / self._sqM)
        return rv

    def ready(self, field, stepNum, path):
        conn = self.inReady
        conn[0].append(field)
        conn[1].append(stepNum)
        conn[2].append(path)

    @property
    def field(self):
        if isinstance(self, person) and self.infected:
            return 1.0
        return self._field

    @field.setter
    def field(self, val):
        if not isinstance(self, person):
            self._field = (self._field + val)/2.0
        else:
            self._field = val
        self.lastStep = self._fieldStep
        self._fieldStep = currentNodeGroup.time.currentStep

    class path:
        # #path:  ONE  person node (may occur at start or end)
        def __init__(self, array=[]):
            self.nodes = []
            self.to(array)
            self.curLoc = None
            if len(array) > 0:
                self.curLoc = 0
            self.forward = -1
            self._exposure = 0

        def to(self, a):
            for i in a:
                if isinstance(i,int):
                    import pdb; pdb.set_trace()
                    print("Unexpected int")
            self.nodes.extend(a)

        def frm(self, a):
            self.nodes = [a].extend(self.nodes)
            self.curLoc = None

        def adjoin(self, path):
            assert(path.nodes[0] == self.nodes[len(self.nodes) - 1])
            self.nodes.extend(arr[1:])

        def extendPath(self, extension):
            import pdb; pdb.set_trace()
            self.paths.append(extension.nodes[1:])



        def __str__(self):
            rv = []
            if self.forward:
                direction = "==>>>>"
            else:
                direction = "<<<<=="
            for i in self.nodes:
                if (self.curLoc is not None) and i == self.nodes[self.curLoc]:
                    rv.append("*" + i.name + "*")
                else:
                    rv.append(i.name)
            return direction + str(rv)

        def process(self):  # #one step at a time
            # #determine src and dest for this step 
            srcNode = self.nodes[self.curLoc]
            srcField = srcNode.field
            srcFieldAvailableTime = srcNode._fieldStep + srcNode.delay
            if self.curLoc + self.forward < 0 or \
               self.curLoc + self.forward >= len(self. nodes):
                # #reverse path at current node
                # #curLoc is end of this path
                # import pdb; pdb.set_trace()
                self.forward *= -1
            targetNode = self.nodes[self.curLoc+self.forward]
            if not isinstance(srcNode, person):
                self._exposure\
                    += srcField * srcNode.delay
            else:
                 self._exposure\
                    += (1 - srcNode.pFactor) * srcField * srcNode.delay
            targetNode.ready(srcField, srcFieldAvailableTime, self)
            t1 = max(currentNodeGroup.time.currentStep, srcFieldAvailableTime)
            currentNodeGroup.time.scheduleAt(targetNode, t1)
            return self



#import spaceTypes
class room(node):
    def __init__(self, name):
        node.__init__(self, name )



class bar(node):
    def __init__(self, name):
        node.__init__(self, name )
        self.sqM = 20
        self.maxInReady = 20
        self.processInterval = 5
        self.delay = 100   # #time spent in the bar



class restaurant(node):
    def __init__(self, name):
        node.__init__(self, name )


class store(node):
    def __init__(self, name):
        node.__init__(self, name )


class medical(node):
    def __init__(self, name):
        node.__init__(self, name )


class bus(node):
    def __init__(self, name):
        node.__init__(self, name )


class car(node):
    def __init__(self, name):
        node.__init__(self, name )


class carriage(node):
    def __init__(self, name):
        node.__init__(self, name )


class platform(node):
    def __init__(self, name):
        node.__init__(self, name )


class busstop(node):
    def __init__(self, name):
        node.__init__(self, name )


class elevator(node):
    def __init__(self, name):
        node.__init__(self, name )


class stairway(node):
    def __init__(self, name):
        node.__init__(self, name )


class street(node):
    def __init__(self, name):
        node.__init__(self, name )



class person(node):
    def __init__(self, name):
        node.__init__(self, name, role="PERSON")
        self._infected = False
        self._infectedStep = -1
        currentNodeGroup.persons.append(self)
        self.paths = []
        self.nextPath = None
        self._exposure = 0  # #time integral of field
        self.pFactor = 0.0  # #protection of PPE
        self.pNum = 0

    def reset(self):  # #for next step
        node.reset(self)
        if not len(self.paths) > 0:
            print("person with no paths reset")
            print(self)
            return
        self.pNum = 0
        if self.nextPath is None:
            self.nextPath = 0

    def protect(self, amt=1.0):
        self.pFactor = amt

    def process(self):  # #ALONG A PATH
        if (self.infected):
            self._field = 1   # #assignment overloaded in node
        tPath = self.paths[self.nextPath]
        if self.pNum < 2:
            self.pNum += 1
        else:
            self._exposure += tPath._exposure
            self.inReady = [[], [], []]
            return True
        node.process(self)
        tPath.forward *= -1
        # #assert(tPath.nodes[tPath.curLoc] == self)
        # #forward huskies
        if (self.pNum < 2):
            tPath.process()
        self.inReady = [[], [], []]
        return self

    @property
    def infected(self):
        return self._infected

    @infected.setter
    def infected(self, val):
        self._infected = val
        self._infectedStep = currentNodeGroup.time.currentStep

    def addPath(self, path):
        if (self.nextPath is None):
            self.nextPath = 0
        assert(path.nodes[0] == self)
        self.paths.append(path)

    def removePath(self, pth):
        q = None
        if self.nextPath is not None:
            q = self.paths[self.nextPath]
        self.paths.remove(pth)
        if self.paths.count(q) > 0:
            self.nextPath = self.paths.index(q)
        elif len(self.paths) > 0:
            self.nextPath = 0
        else:
            self.nextPath = None

    def calculate(self):
        val = self._field
        if self.infected:
            val = 1.0
        if len(self.inReady[0]) == 1:   # #value path end
            return (1-self.pFactor)*(val+self.inReady[0][0])
        else:
            return val


class composite(node):
    #  #spaces with different characteristics
    COMPOSITES = {0:     ["ROOM", 1, None],
                  1:     ["APT", 1, None],
                  6:     ["WARD", 1, None],
                  2:     ["FLOOR", 1, None],
                  3:     ["BUILDING", 1, None],
                  7:     ["BLOCK", 1, None],
                  4:     ["HOSPITAL", 1, None],
                  8:     ["ELEVATOR", 1, None],
                  5:     ["REGION", 1, None]}

    def __init__(self, name, level=0, role=COMPOSITES[0][0], nds=[]):
        xx = composite.COMPOSITES[level]
        self.level = level
        node.__init__(self, name, role=role, sqM=xx[1])
        self.children = {}
        self.addChildren(nds)

    def addChildren(self, cArray):
        j = len(self.children.values()) - 1
        for i in cArray:
            j += 1
            assert(isinstance(i, composite))
            self.children[j] = i

    # #returns path through composite to bNode
    def pathTo(self, pathA, bNode=None, tp=person):
        # #path to person through children
        self.level = max(self.level, len(pathA))
        assert(len(pathA) != 0)
        cComposite = self
        q = [cComposite]
        for j in range(0, len(pathA) - 1):
            nName = cComposite.name + "." + str(pathA[j])
            nd = currentNodeGroup.names.get(nName)
            if (nd is None):
                nd = composite(nName, self.level-j-1)
                self.children[pathA[j]] = nd
            q.append(nd)
        if bNode is None:
            bNode = tp(self.name + "." +
                       str(len(currentNodeGroup.names.values())))
        q.append(bNode)
        q.reverse()
        rv = node.path(q)
        assert(rv is not None)
        return rv

    # #returns path through composite to bNode
    def pathTo1(self, pathA, bNode=None, tp=person):
        # #path to person through children
        self.level = max(self.level, len(pathA))
        if len(pathA) > 0:
            cName = self.name + "." + str(pathA[0])
            nd = currentNodeGroup.names.get(cName)
            if (nd is None):
                nd = composite(cName, self.level-1)
                self.children[pathA[0]] = nd
            endPath = nd.pathTo1(pathA[1:], bNode)
            endPath.to([self])
            return endPath
        else:
            if bNode is None:
                bNode = tp(self.name + "." +
                           str(len(currentNodeGroup.names.values())))
            return node.path([bNode, self])


class building(composite):
    def __init__(self, address, shape=[1, 8, 1, 8]):
        self.roomsPerApt = shape[0]
        self.aptPerFl = shape[1]
        self.numElevators = shape[2]
        self.numFloors = shape[3]

        
dispatch = {"bar": bar, "bus": bus, "busstop": busstop, "car": car,
            "carriage": carriage, "composite": composite,
            "elevator":  elevator, "medical":  medical, "person": person,
            "platform": platform, "restaurant": restaurant, "room": room,
            "stairway": stairway, "store": store, "street": street}

class population:
    class accum:
        acc = {"nInf": 0, "pField": [], "nPerson": 0, "vField": [], "ndNum": 0}

        def __init__(self):
            self.acc = population.accum.acc.copy()

        def __str__(self):
            return str(self.acc)

    def __init__(self, name=None):
        self.pctInf = 0
        self.acc = population.accum()
        if name is None:
            name = "P_" + str(len(currentNodeGroup.names.keys()))
        self.composite = composite(name)
        self.paths = {}   # #arranged by start type
        for nm in dispatch.keys():
            self.paths[nm] = []
        self.nodeGroup = currentNodeGroup

    def prune(self):
        for i in dispatch.keys():  # #for each type
            paths_SrcType = self.paths[i]
            if len(paths_SrcType) > 0:  # #if something is there
                newPathList = []
                for pth in paths_SrcType:
                    if pth is None or pth.nodes[0] is None:
                        import pdb; pdb.set_trace()
                        print("None")
                    elif pth.nodes[len(pth.nodes) - 1] == self.composite:
                        print("\nRemoving " + str(pth))
                        if i == "person":
                            pth.nodes[0].removePath(pth)
                    else:
                        print("\nretaining: " + str(pth))
                        newPathList.append(pth)
                self.paths[i] = newPathList

    def showPaths(self):
        print("Population(" + self.composite.name + ")")
        for i in dispatch.keys():  # #for each type
            paths_SrcType = self.paths[i]
            if len(paths_SrcType) > 0:  # #if something is there
                print("Paths from type:" + i)
                for j in paths_SrcType:
                    if j is None or j.nodes[0] is None:
                        import pdb; pdb.set_trace()
                        print(">>>>>unexpected None:" + str(j))
                    else:
                        print(str(j.nodes[0].field)+"\t"+j.__str__())

    def showInfState(self, all=False, dx=.1):
        self.calcState()
        pData = self.acc.acc["pField"]
        vData = self.acc.acc["vField"]
        lpData = []
        lvData = []
        for i in range(0, len(pData)):
            if pData[i] == 0:
                lpData.append(2**-35)
            else:
                lpData.append(math.log(pData[i]))
        for i in range(0, len(vData)):
            if vData[i] == 0:
                lvData.append(2**-35)
            else:
                lvData.append(math.log(vData[i]))
                
        print("\nPersons(#,#inf,ln(field)): (" +
              str(self.acc.acc["nPerson"]) + ", " +
              str(self.acc.acc["nInf"]) + ", " +
              str(statistics.mean(pData)) + "+/-" +
              str(statistics.stdev(lpData)) + ")")
        print("\nNodes(#, ln(field)): (" +
              str(self.acc.acc["ndNum"]) + ", " +
              str(statistics.mean(vData)) + "+/-" +
              str(statistics.stdev(lvData)) + ")")

    def calcState(self):
        self.acc = population.accum()
        for nd in currentNodeGroup.names.values():
            field = nd.field
            self.acc.acc["ndNum"] += 1
            self.acc.acc["vField"].append(field)
            if isinstance(nd, person):
                if nd.infected:
                    self.acc.acc["nInf"] += 1
                self.acc.acc["pField"].append(field)
                self.acc.acc["nPerson"] += 1
        return self.acc

    def setInfPct(self, val=.25):
        self.pctInf = val
        for prsn in currentNodeGroup.persons:
            if random.uniform(0, 1) < val:
                prsn.infected = True
            else:
                prsn.infected = False

    def initSim(self):
        currentNodeGroup = self.nodeGroup
        currentNodeGroup.time.initSim()

    def finish(self):
        currentNodeGroup = self.nodeGroup
        currentNodeGroup.time.finish()

    def step(self, numIter=5, follow=True):
        currentNodeGroup = self.nodeGroup
        for i in range(0, numIter):
            currentNodeGroup.time.step()
            if follow:
                self.showInfState()
        if not follow:
            self.showInfState()

    def splice(self, path1, path2):   # #minimal path connecting endpts
        l1 = len(path1.nodes)
        l2 = len(path2.nodes)
        assert(path2.nodes[l2 - 1] == path1.nodes[l1 - 1])
        for j in range(1, min(l1, l2)):
            if path2.nodes[l2 - j] != path1.nodes[l1 - j]:
                start = path1.nodes[:l1 - j + 1].copy()
                end = path2.nodes[:l2 - j + 1].copy()
                end.reverse()
                start.extend(end)
                return node.path(start)
        return node.path([path1.nodes[0], path2.nodes[0]])

    def populate(self, typ=dispatch["person"], num=10, maxLevel=0, shape=[1,8,2,12,4]):
        # #maxLevel to control distributions of nonCompos
        for ii in dispatch.keys():
            if dispatch[ii] == typ:
                typeName = ii
                break
        for i in range(0, num):
            pathA = []
            for j in range(0, len(shape) - 1):
                pathA.append(random.randint(0, shape[j]-1))
            nodeName = typeName + str(len(currentNodeGroup.names.values()))
            ithPath = self.composite.pathTo(pathA, typ(nodeName))
            ithNode = ithPath.nodes[ithPath.curLoc]
            if ithPath is None:
                import pdb; pdb.set_trace()
                print 
            else:
                self.paths[typeName].append(ithPath)
            if (typeName == "person"):
                ithNode . addPath(ithPath)

    def connectTypes(self, t1, t2, ctl=0):
        startSegmentPaths = self.paths[t1]
        endSegmentPaths = self.paths[t2]
        l1 = len(startSegmentPaths)
        l2 = len(endSegmentPaths)
        assert(len(startSegmentPaths) != 0 and len(endSegmentPaths) != 0)
        for i in range(0, max(l1, l2)):
            start = startSegmentPaths[i % l1]
            end = endSegmentPaths[i % l2]
            splice = self.splice(start, end)
            if (splice is not None):
                startSegmentPaths.append(splice)


import pdb; pdb.set_trace()

x = dispatch["room"]("ROOM")





xx = population()
xx.populate(typ=person, num=15)
# #
xx.populate(typ=dispatch["bar"], num=5)
xx.setInfPct()  # #default 10%
xx.connectTypes("person", "bar")
xx.showPaths()
xx.prune()
xx.showPaths()
xx.showInfState()
xx.initSim()
xx.step(50, follow=False)

