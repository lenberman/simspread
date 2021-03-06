#!/usr/bin/python3
import random
import statistics
import math
import sys
import pdb; pdb.set_trace()

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
            -math.log(2.0)/(vdfHalfLifeMinutes/minutesPerStep)
        self.pathFactor = .5  # #accumulation along paths
        self.infectiousPeriod = symp + asym
        self.dose = 100  # # how much exposure results in infection
        self.diseaseRecord = {}

    def recordInfection(self, exposure, tm, nm):
        if tm not in self.diseaseRecord:
            self.diseaseRecord[tm] = []
        self.diseaseRecord[tm].append([True, nm, exposure])

    def recordRecovery(self, tm, nm):
        if tm not in self.diseaseRecord:
            self.diseaseRecord[tm] = []
        self.diseaseRecord[tm].append([False, nm])

    def infectivity(prsn):
        pass

    def antibody(prsn, nStep):
        pass

    def dFactor(self, nSteps, cng):
        return math.exp(cng.disease.vdfDecayPerStepExp * nSteps)

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

    def reset(self, cng):
        self.currentStep += 1
        self.maxStep = max(self.maxStep, self.currentStep+1)
        cng.personDone = 0
        for ii in cng.names.values():
            ii.reset(cng)  # # reset
            if isinstance(ii, person) and ii.nextPath is not None:
                self.scheduleAt(ii, self.currentStep)
                cng.personDone -= 1
                pth = ii.paths[ii.nextPath]
                if pth.curLoc is None:
                    pth.curLoc = 0
        assert(cng.personDone == - len(cng.persons))

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
            assert(isinstance(rv, node) or isinstance(rv, path))
            if isinstance(rv, node):
                rv.scheduledAt = -1
            return rv

    def processNextNode(self, cng):
        nd = self.popNextNode()
        if(nd is None):
            return None
        assert(isinstance(nd, node) or isinstance(nd, path))
        return nd.process(cng)

    def step(self, cng):  # #step(s) must be preceded by initSim
        while cng.personDone < 0:
            nd = self.processNextNode(cng)
            if nd is None:
                # #print("\n\nCompleted DEPTH: " + str(self.currentStep))
                # #print("\t:maxStep:" + str(self.maxStep)+"\n")
                print(".", sep=" ", end=" ", file=sys.stdout, flush=False)
                return True
        return


class nodeGroup:
    def __init__(self):
        self.names = {}
        self.persons = []
        self.stepsPerDay = 1000
        self.time = future()
        self.seed = random.getstate()
        self.disease = disease()
        self.personDone = 0



class node:
    SPACE_TYPES = ["ROOM", "PERSON", "BAR", "RESTAURANT", "STORE",
                   "MEDICAL", "BUS", "CAR", "CARRIAGE", "PLATFORM",
                   "BUSSTOP",  "ELEVATOR", "STAIRWAY", "STREET", "COMPOSITE"]

    def reset(self, cng):  # #for next step
        self.lastStep = self._fieldStep
        self._fieldStep = cng.time.currentStep

    def __init__(self, cng, name=None, sqM=1, role=SPACE_TYPES[0]):
        if name is None:
            name = Node+str(len(cng.names.keys()))
        self.name = name
        if name in cng.names:
            print("Recreating " + str(name))
        cng.names[name] = self
        self._field = 0  # #infectivity
        self._fieldStep = cng.time.currentStep
        self._role = role
        self._sqM = sqM
        self.crowdFactor = 1
        self.delay = 1  # #steps ascribed to passage thru
        self.inReady = [[], [], []]  # #paths & field connections
        self.lastStep = cng.time.currentStep
        self.maxInReady = 2  # #stores available values
        self.processInterval = 5
        self.scheduledAt = -1

    def __str__(self):
        nm = self.name
        if isinstance(self, person) and self.infected:
            nm = "<*" + self.name + "*>"
        val = nm + "(" + self._role
        val += ", field=" + str(self._field)
        val += ", lastStep=" + str(self.lastStep) + ")"
        val += str(self.inReady[0]) + ":" + str(self.inReady[1])
        return val

    def reschedule(self, cng):
        cng.time.scheduleAt(
            self, cng.time.currentStep + self.processInterval)



    def process(self, cng):
        # calculates new field value from InReady
        self.setField(self.calculate(cng), cng)
        if (False and isinstance(self, person)):
            print("\n" + str(self.name) + " @ " + str(self._fieldStep) +
                  ":\t" + str(self.inReady[0]) + ", field=\t" + str(self.field))
        #import pdb; pdb.set_trace()
        valA = self.inReady[0]
        stepA = self.inReady[1]
        pathA = self.inReady[2]
        v = []
        s = []
        p = []
        pAvail = 0
        for i in range(len(pathA)):
            tPath = pathA[i]
            #  #values furnished by inReady have path curLoc at source
            #  #assert(self == tPath.nodes[tPath.curLoc+tPath.forward])
            prevNode = tPath.nodes[tPath.curLoc]
            pAvail = prevNode._fieldStep + prevNode.delay
            if pAvail <= self._fieldStep:
                #  #and pAvail > self.lastStep and
                # #value from this path processed.  Respect maxInReady!
                tPath.curLoc += tPath.forward
                tPath.process(cng)
            else:
                # #value this path next periodic activation
                v.extend([valA[i]])
                s.extend([stepA[i]])
                p.extend([pathA[i]])
        self.inReady = [v, s, p]
        if len(v) > 0:
            #  #import pdb; pdb.set_trace()
            self.reschedule(cng)
        return self

    def calculate(self, cng):  # #area weighted field of inputs
        valA = self.inReady[0]
        stepA = self.inReady[1]
        pathA = self.inReady[2]
        rv = 0
        total = 0.0
        assert(len(valA) == len(pathA))
        for i in range(0, len(valA)):
            path = pathA[i]
            step = stepA[i]
            dt = cng.time.currentStep - step
            if dt < 0:
                continue
            assert(dt >= 0)
            factor = cng.disease.dFactor(dt, cng)
            val = valA[i]**.5
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

    def setField(self, val, cng):
        dt = self._fieldStep - self.lastStep
        factor = cng.disease.dFactor(dt, cng)
        if not isinstance(self, person):
            self._field = (self._field * factor + val)/2.0
        else:
            self._field = val
        self.lastStep = self._fieldStep
        self._fieldStep = cng.time.currentStep



class path:
    # #path:  ONE  person node (may occur at start or end)
    p_counter = 0
    
    def __init__(self, array=[]):
        self._id = path.p_counter
        path.p_counter += 1
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

    def splice(self, path2):   # #minimal path connecting endpts
        l1 = len(self.nodes)
        l2 = len(path2.nodes)
        assert(path2.nodes[l2 - 1] == self.nodes[l1 - 1])
        for j in range(1, min(l1, l2)):
            if path2.nodes[l2 - j] != self.nodes[l1 - j]:
                start = self.nodes[:l1 - j + 1].copy()
                end = path2.nodes[:l2 - j + 1].copy()
                end.reverse()
                start.extend(end)
                return path(start)
        return path([self.nodes[0], path2.nodes[0]])



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

    def getSrc(self):
        return self.nodes[self.curLoc]

    def getTarget(self):
        forward = self.forward
        if self.curLoc + self.forward < 0 or \
           self.curLoc + self.forward >= len(self. nodes):
            # #reverse path at current node
            # #curLoc is end of this path
            # import pdb; pdb.set_trace()
            forward *= -1
        return self.nodes[self.curLoc+forward]


    def process(self, cng):  # #one step at a time
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
        factor = cng.disease.dFactor(srcNode.delay, cng)
        srcNodeContribution = srcField * factor * cng.disease.pathFactor
        # srcNode pFactor for PPE and reset at path start
        if isinstance(srcNode, person):
            self._exposure = 0
            srcNodeContribution *= (1 - srcNode.pFactor)
        self._exposure = srcNodeContribution + (1 - cng.disease.pathFactor) * self._exposure
        targetNode.ready(srcField, srcFieldAvailableTime, self)
        t1 = max(cng.time.currentStep, srcFieldAvailableTime)
        cng.time.scheduleAt(targetNode, t1)
        return self



#import spaceTypes
class room(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)



class bar(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)
        self._sqM = 20
        self.maxInReady = 20
        self.processInterval = 5
        self.delay = 100   # #time spent in the bar



class restaurant(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class store(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class medical(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class bus(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class car(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class carriage(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class platform(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class busstop(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class elevator(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class stairway(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)


class street(node):
    def __init__(self, cng, name=None):
        node.__init__(self, cng, name)



class person(node):
    def __init__(self, cng, name=""):
        if name == "":
            name = "person." + str(len(cng.names.values()))
        node.__init__(self, cng, name, role="PERSON")
        self.setInfected(False, cng)
        cng.persons.append(self)
        self.paths = []
        self.nextPath = None
        self._exposure = 0  # #time integral of field
        self.pFactor = 0.0  # #protection of PPE
        self.observable = True

    def reset(self, cng):  # #for next step
        node.reset(self, cng)
        if len(self.paths) == 0:
            print("person without paths:" + str((self)))
            return
        self.observable = True
        if self.nextPath is None:  # #cycle through available paths
            self.nextPath = 0
        elif self.nextPath + 1 < len(self.paths):
            self.nextPath += 1
        else:
            self.nextPath = 0
            # #determine whether infected has changed
        if self.infected and self.recovered(cng):
            self.setInfected(False, cng)
            cng.disease.recordRecovery(cng.time.currentStep, self.name)
        elif not self.infected and self._exposure > cng.disease.dose:
            cng.disease.recordInfection(self._exposure, cng.time.currentStep, self.name)
            self.setInfected(True, cng)
        
    def recovered(self, cng):
        if self._infectedStep >= 0:
            return cng.time.currentStep >\
                cng.disease.infectiousPeriod + self._infectedStep
        return False

    def protect(self, amt=1.0):
        self.pFactor = amt

    def process(self, cng):  # #ALONG A PATH
        self.observable = not self.observable
        tPath = self.paths[self.nextPath]
        if self.observable:
            dt = cng.time.currentStep - self._fieldStep
            assert(dt > 0)
            factor = cng.disease.dFactor(dt, cng)
            if self.infected:
                self._exposure = 0
            else:
                self._exposure = (tPath._exposure + self._exposure * factor)/(1 + factor)
                # #move reset exposure along path to process of path
            if (False):
                print("\n" + str(self.name) + " @ " + str(self._fieldStep) +
                      ":\t" + str(self.inReady[0]) + ", field=\t" +
                      str(self.field) + ", exposure=\t" + str(self._exposure))
            self.inReady = [[], [], []]
            cng.personDone += 1
            return True
        if (self.infected):
            self._field = 1   # #assignment overloaded in node
        node.process(self, cng)
        tPath.forward *= -1
        # #assert(tPath.nodes[tPath.curLoc] == self)
        # #forward huskies
        if (not self.observable):
            tPath.process(cng)
        self.inReady = [[], [], []]
        return self

    @property
    def infected(self):
        return self._infected

    @infected.setter
    def infected(self, x):
        assert(False)

    def setInfected(self, val, cng):
        self._infected = val
        if not val:
            self._infectedStep = -1
        else:
            self._infectedStep = cng.time.currentStep
        self._exposure = 0

    def addPath(self, path):
        if (self.nextPath is None):
            self.nextPath = 0
        if (path.nodes[0] != self):
            assert(False)  # #reverse path and add.
        else:
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
            import pdb; pdb.set_trace()
            self.nextPath = None

    def calculate(self, cng):
        val = self._field
        if self.infected:
            val = 1.0
        if len(self.inReady[0]) == 1:   # #value path end
            return (1-self.pFactor)*(val+self.inReady[0][0])/2.0
        else:
            return val


class composite(node):
    #  #spaces with different characteristics
    COMPOSITE_TYPES = {0:     ["ROOM", 1, None],
                       1:     ["APT", 1, None],
                       6:     ["WARD", 1, None],
                       2:     ["FLOOR", 1, None],
                       3:     ["BUILDING", 1, None],
                       7:     ["BLOCK", 1, None],
                       4:     ["HOSPITAL", 1, None],
                       8:     ["ELEVATOR", 1, None],
                       5:     ["REGION", 1, None]}

    def __init__(self, cng, name, role=COMPOSITE_TYPES[0][0]):
        node.__init__(self, cng, name, role=role, sqM=5)
        self.children = {}

    def addChildren(self, cArray):
        j = len(self.children.values()) - 1
        for i in cArray:
            j += 1
            assert(isinstance(i, composite))
            self.children[j] = i

    # #returns path through composite to bNode
    def pathTo(self, pathA, cng, bNode=None, tp=person):
        # #path to person through children
        assert(len(pathA) != 0)
        cComposite = self
        q = [cComposite]
        typeName = list(dispatch.keys())[list(dispatch.values()).index(tp)]
        nName = cComposite.name + ":"
        for j in range(0, len(pathA) - 1):
            nName = nName + "." + str(pathA[j])
            nd = cng.names.get(nName)
            if (nd is None):
                nd = composite(cng, nName)
                self.children[pathA[j]] = nd
            q.append(nd)
        if bNode is None:
            bNode = tp(cng, typeName[0:3] + "." +
                       str(len(cng.names.values())))
        q.append(bNode)
        q.reverse()
        rv = path(q)
        if isinstance(bNode, person):
            bNode.addPath(rv)
        assert(rv is not None)
        return rv

    def fullTree(self, shape, pop, num=0, collapse=True, theType=person):
        # #num>0, means add  num leaves, 0 (all), <0 add prod(shape)-num
        # #shape is 4D, shape[i]==1 collapse'd if True
        cubed = 0
        if num <= 0:
            cubed = 1
            for i in range(0, 4):
                cubed *= shape[i]
        num = cubed + num
        pathA = []
        ps = {}
        typeName = list(dispatch.keys())[list(dispatch.values()).index(theType)]
        assert(num > 0)
        for nf in range(0, shape[3]):  # #floors
            for ne in range(0, shape[2]):  # #elevators
                for na in range(0, shape[1]):  # #apts
                    for nr in range(0, shape[0]):  # #rooms
                        tpp = []
                        if collapse and (shape[3] != 1):
                            tpp = [nf]
                        if collapse and (shape[2] != 1):
                            tpp.append(ne)
                        if collapse and (shape[1] != 1):
                            tpp.append(na)
                        if collapse and (shape[0] != 1):
                            tpp.append(nr)
                        nm = str(tpp)
                        if nm not in ps:  # #required for collapsing
                            pathA.append(tpp)
                        else:
                            continue
                        if num == 0:
                            return
                        num -= 1
                        ps[nm] = True
                        ithPath = self.pathTo(tpp, pop.getCNG(), tp=theType)
                        ithNode = ithPath.nodes[ithPath.curLoc]
                        # #
                        assert(ithPath.nodes[0] == ithNode)
                        pop.paths[typeName].append(ithPath)


class building(composite):  # # shape[0] is [#rooms,#people] per apt
    def __init__(self, pop, address=None, shape=[1, 8, 1, 8]):
        if address is None:
            address = "bg-" + str(len(pop.getCNG().names.values()))
        composite.__init__(self, pop.getCNG(), address,
                           composite.COMPOSITE_TYPES[4][0])
        self.roomsPerApt = shape[0]
        self.aptPerFl = shape[1]
        self.numElevators = shape[2]
        self.numFloors = shape[3]
        pop.setComposite(self)
        self.fullTree(shape, pop)


dispatch = {"bar": bar, "bus": bus, "busstop": busstop, "car": car,
            "carriage": carriage, "composite": composite,
            "elevator":  elevator, "medical":  medical, "person": person,
            "platform": platform, "restaurant": restaurant, "room": room,
            "stairway": stairway, "store": store, "street": street}

class accum:
    def __init__(self):
        self.acc = {"nInf": 0, "exposure": [], "nPerson": 0,
                    "field": [], "ndNum": 0}
        
    def __str__(self):
        return str(self.acc)


class population:

    def __init__(self, name=None, root=None, cng=None):
        if cng is None:
            self.cng = nodeGroup()
        else:
            self.cng = cng
        self.pctInf = 0
        self.acc = accum()
        self.composite = root
        if root is not None:
            self.name = "P_" + root.name
        else:
            if name is None:
                self.name = "P_" + str(len(self.cng.names.keys()))
            else:
                self.name = name
        self.paths = {}   # #arranged by start type
        self.levels = {}
        for nm in dispatch.keys():
            self.paths[nm] = []

    def setComposite(self, composite):  # #called updates self.paths[]
        assert(self.composite is None)
        if composite not in self.cng.names.values():
            assert(False)
        self.composite = composite
        # #insure paths[typeName] is updated
        # #for psn in composite.children.values():
        # #   self.paths[typeName].append(ithPath)

    def getCNG(self):
        return self.cng
        
    def setCNG(self, cng):
        self.cng = cng
        
    def findLevels(self):
        done = []
        finished = False
        for i in range(0, len(self.cng.names.keys())):
            finished = True
            self.levels[i] = []
            for path in self.paths["person"]:
                if len(path.nodes) <= i:
                    continue
                node = path.nodes[i]
                if node in done:
                    continue
                finished = False
                done.append(node)
                self.levels[i].append(node)
            if finished:
                break
        return self.levels

    def prune(self):
        for i in dispatch.keys():  # #for each type
            paths_SrcType_I = self.paths[i]
            if len(paths_SrcType_I) > 0:  # #if something is there
                newPathList = []
                for pth in paths_SrcType_I:
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
        if self.composite is None:
            self.composite = composite(self.cng, self.name)
        print("Population(" + self.composite.name + ")")
        for i in dispatch.keys():  # #for each type
            paths_SrcType_I = self.paths[i]
            if len(paths_SrcType_I) > 0:  # #if something is there
                print("Paths from type:" + i)
                for j in paths_SrcType_I:
                    if j is None or j.nodes[0] is None:
                        import pdb; pdb.set_trace()
                        print(">>>>>unexpected None:" + str(j))
                    else:
                        print(str(j.nodes[0].field)+"\t"+j.__str__())

    def showInfState(self, all=False, dx=.1):
        self.calcState()
        pData = self.acc.acc["exposure"]
        vData = self.acc.acc["field"]
        lpData = []
        lvData = []
        for i in range(0, len(pData)):
            if pData[i] == 0:
                lpData.append(-35)
            else:
                lpData.append(math.log(pData[i]))
        for i in range(0, len(vData)):
            if vData[i] == 0:
                lvData.append(-35)
            else:
                lvData.append(math.log(vData[i]))

        print("\nPersons(#,#inf,ln(exposure)): (" +
              str(self.acc.acc["nPerson"]) + ", " +
              str(self.acc.acc["nInf"]) + ", " +
              str(statistics.mean(lpData)) + " +/- " +
              str(statistics.stdev(lpData)) + ")")
        if len(lpData) < 20:
            print("exposure: ", lpData)
        print("Nodes(#, ln(field)): (" +
              str(self.acc.acc["ndNum"]) + ", " +
              str(statistics.mean(lvData)) + " +/- " +
              str(statistics.stdev(lvData)) + ")")
        if len(lpData) < 20:
            print(lvData)

    def calcState(self):
        self.acc = accum()
        for nd in self.cng.names.values():
            if isinstance(nd, person):
                if nd.infected:
                    self.acc.acc["nInf"] += 1
                self.acc.acc["exposure"].append(nd._exposure)
                self.acc.acc["nPerson"] += 1
            else:
                self.acc.acc["ndNum"] += 1
                self.acc.acc["field"].append(nd.field)
        return self.acc

    def setInfPct(self, val=.25):
        self.pctInf = val
        for prsn in self.cng.persons:
            if random.uniform(0, 1) < val:
                prsn.setInfected(True, self.cng)
            else:
                prsn.setInfected(False, self.cng)

    def step(self, numIter=5, follow=True, display=None, quiet=False):
        self.cng.time.reset(self.cng)
        if display is not None:  # #display object reads current data
            dis = display(self)
            dis.rData()
        else:
            dis = None
        for i in range(0, numIter):
            if i == 0 and not quiet:
                print("Initial state")
                self.showInfState()
            self.cng.time.step(self.cng)
            if i < numIter - 1:
                self.cng.time.reset(self.cng)
            if display is not None:  # #display object reads current data
                dis.rData()
            if follow:
                print("Step" + str(i))
                self.showInfState()
        if not follow and not quiet:
            self.showInfState()
        return dis

    def absorb(self, pop, cut1=[], cut2=[]):
        pass


    def populate(self,
                 typ=dispatch["person"],
                 num=10,
                 maxLevel=0,
                 pathIn=None):
        # #pathIn not None:path to composite where num nodes of typ are attached
        # #pathIn None: fullTree with maxLevel depth, limited by num as above
        # # if self.composite != None, add no new paths
        if self.composite is None:
            self.composite = composite(self.cng, self.name)
        # #maxLevel to control distributions of nonCompos
        typeName = list(dispatch.keys())[list(dispatch.values()).index(typ)]
        for i in range(0, num):
            if pathIn is None:
                # #go about choosing how to distribute num new nodes
                shape = []
                j = 1
                while 2**j < num:
                    j = j + 1
                    shape.append(2)
                while len(shape) < 4:
                    shape.append(1)
                self.composite.fullTree(shape, self, num, theType=typ)
                return
            pathA = pathIn
            nodeName = typeName[0:3] + "." + str(len(self.cng.names.values()))
            ithPath = self.composite.pathTo(pathA,
                                            self.cng,
                                            typ(self.cng, nodeName))
            ithNode = ithPath.nodes[ithPath.curLoc]
            if ithPath is None:
                import pdb; pdb.set_trace()
                print
            else:
                self.paths[typeName].append(ithPath)
            if (typeName == "person"):   # #connection now made in pathTo
                assert(ithNode in ithPath.nodes)

    def connectTypes(self, t1, t2, ctl=0):
        startSegmentPaths = self.paths[t1]
        endSegmentPaths = self.paths[t2]
        l1 = len(startSegmentPaths)
        l2 = len(endSegmentPaths)
        assert(len(startSegmentPaths) != 0 and len(endSegmentPaths) != 0)
        for i in range(0, max(l1, l2)):
            for j in range(0, ctl):
                start = startSegmentPaths[(i * (j + 1)) % l1]
                end = endSegmentPaths[(i * (j + 1)) % l2]
                splice = start.splice(end)
                assert (splice is not None)
                startSegmentPaths.append(splice)
                if (t1 == "person"):
                    splice.nodes[0].addPath(splice)
                    if (t2 == "person"):
                        lt2 = len(splice.nodes)
                        splice.nodes[lt2 - 1].addPath(splice)



        
def getIthData(data, i):
    if len(data) <= i:
        return None
    return data[i]


def xSpan(data):  # # assuming data monotonic in 1st two coor.
    return [data[0][0], data[len(data)-1][1]]


def ySpan(data, j=3):
    # #j=3->field,=4->exposure,5(person)infected,
    mm = [2**20, -2**20]
    for i in range(0, len(data)):
        mm[0] = min(mm[0], data[i][j])
        mm[1] = max(mm[1], data[i][j])
    return mm


class record:

    def __init__(self, pop):
        self.pop = pop
        # #self.win = GraphWin(width=800, height=600)
        # #{} of arrays of [lastStep, fieldStep, field, infected, exposure]
        self.pData = {}  # #indexed by name, ordered (by step)
        # #array of [lastStep, _fieldStep, scheduledAt, field]
        self.npData = {}  # # non-person nodes and paths
        # # path._id:array [currentStep,srcFieldAvailableTime,src.field,target.field,exposure]
        self.pathData = {}
        self.graphs = {}
        self.displayStep = 0


    def rData(self):  # most interesting data in location: [ptx , pty, ?, val, ??]
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
            self.npData[nd.name].append([nd.lastStep, nd._fieldStep,
                                         nd.scheduledAt, nd._field])
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

    def createPolys(self, id, theClass, jth=3, rng=[0, 2**20]):
        # #returns [points on graph, enclosing rectangle]
        
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

    # #returns [ idArray, [ polys  ]  graphObj's draw and undraw.
    def graphData(self, dataType, nodeFilter=None):
        idA  = []
        if dataType == person:
            for nm in self.pData.keys():
                if (nodeFilter is None or
                    isinstance(self.pop.cng.names[nm], nodeFilter)):
                    idA.append(nm)
        elif dataType == path:
            for pth in self.pop.paths["person"]:
                idA.append(pth._id)
        else:
            for nm in self.npData.keys():
                if (nodeFilter is None or
                    isinstance(self.pop.cng.names[nm], nodeFilter)):
                    idA.append(nm)
        if len(idA) == 0:
            return None
        
        polyRecA = []
        for id in idA:
            if id not in self.graphs.keys():
                self.graphs[id] = []
            polyRec = self.createPolys(id, dataType)
            self.graphs[id].append(polyRec)
            polyRecA.append(polyRec)
        return [idA, polyRecA]


