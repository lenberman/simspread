#!/usr/bin/python3
# ##import pdb; pdb.set_trace()


class disease:
    def __init__(self, mps=6, asym=1000, sym=1500,
                 psym=1500, abt=6000):
        self.minutesPerStep = mps
        self.asym = asym
        self.sym = sym
        self.psym = psym
        self.antibody = abt

    def infectivity(prsn):
        pass

    def antibody(prsn, nStep):
        pass


class future:
    events = {}
    currentStep = 0
    maxStep = 0
    minutesPerStep = 6

    def __str__(self):
        rv = "Current " + str(self.currentStep) + ", max " + str(self.maxStep)
        rv += str(self.events)
        return rv

    def scheduleAt(self, nd, time):  # #reschedule if necessary
        assert(time >= self.currentStep)  # #don't schedule in past
        # #print("\nSchedule " + str(nd) + " at " + str(time))
        if isinstance(nd, node):
            nodeCurrentSchedule = nd.scheduledAt
            if time > nd.scheduledAt:
                nd.scheduledAt = time
        else:  # #could be a path end
            nodeCurrentSchedule = -1
        self.maxStep = max(self.maxStep, time, nodeCurrentSchedule)
        if isinstance(nd, node):
            if nodeCurrentSchedule > time:
                return
            else:  # # == move to end of this time,
                ct = self.events.get(nodeCurrentSchedule)
                if ct is not None:
                    ct.remove(nd)
        ct = self.events.get(time)
        if ct is None:
            ct = []
            self.events[time] = ct
        ct.append(nd)
        # #print(self)

    def initSim(self):
        self.currentStep += 1
        self.maxStep = max(self.maxStep, self.currentStep+1)
        assert(self == node.time)
        for ii in node.names.values():
            ii.reset()  # # reset
            if isinstance(ii,person):
                self.scheduleAt(ii, self.currentStep)
                pth = ii.paths[ii.nextPath]
                if pth.curLoc is None:
                    pth.curLoc = 0

    def step(self):  # #step(s) must be preceded by initSim
        self.finish()  # #paths have ONE or TWO person nodes.
        return "Done at time = " + str(self.currentStep)

    def popNextNode(self):  # #null when events array is empty
        nn = self.events.get(self.currentStep)
        if nn is None:
            keys = self.events.keys()
            if len(keys) == 0:
                return None
            else:
                self.currentStep = keys[0]
                return self.popNextNode()
        elif len(nn) == 0:
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

    def finish(self, mStep=10000):  # #simulate all currently scheduled nodes
        while self.currentStep <= max(self.maxStep, mStep):
            nd = self.processNextNode()
            if nd is None:
                print("\n\nCompleted DEPTH: " + str(self.currentStep))
                print("\t:maxStep:" + str(self.maxStep)+"\n")
                return True
        return False

    
class node:
    TYPES = ["ROOM", "PERSON", "BAR", "RESTAURANT", "STORE",  "MEDICAL", "BUS",
             "CAR", "CARRIAGE", "PLATFORM", "BUSSTOP",  "ELEVATOR", "STAIRWAY",
             "STREET", "COMPOSITE"]
    names = {}
    persons = []
    time = future()

    def reset(self):  # #for next step
        self.lastStep = self._fieldStep
        self._fieldStep = node.time.currentStep

    def __init__(self, name, sqM=1, role=TYPES[0], field=0):
        self.name = name
        if name in node.names:
            raise Exception("Duplicate name:" + name)
        node.names[name] = self
        self._role = role
        self._field = field  # #infectivity
        self._fieldStep = node.time.currentStep
        self.lastStep = node.time.currentStep
        self.scheduledAt = -1
        self.processInterval = 5
        self._sqM = sqM
        self.maxInReady = 2  # #
        self.delay = 1
        self.crowdFactor = 1
        self.inReady = [[], []]  # #paths & field connections

    def __str__(self):
        nm = self.name
        if isinstance(self, person) and self._infected:
            nm = "<*" + self.name + "*>"
        val = nm + "(" + self._role
        val += ", field=" + str(self._field)
        val += ", lastStep=" + str(self.lastStep) + ")"
        val += str(self.inReady[0])
        return val

    def process(self):
        self.field = self.calculate()
        if (True):
            print("\nProcessing(" + str(self.name) + ") in:\t" +
                  str(self.inReady[0]) + ", field=" + str(self.field))
        #import pdb; pdb.set_trace()
        valA = self.inReady[0]
        pathA = self.inReady[1]
        v = []
        p = []
        nProcessed = 0
        for i in range(len(pathA)):
            tPath = pathA[i]
            #  #values furnished by inReady have path curLoc at source
            #  #assert(self == tPath.nodes[tPath.curLoc+tPath.forward])
            prevNode = tPath.nodes[tPath.curLoc]
            if prevNode._fieldStep + prevNode.delay <= self._fieldStep and \
               prevNode._fieldStep + prevNode.delay > self.lastStep and \
               nProcessed < self.maxInReady:
                # #value from this path processed.  Respect maxInReady!
                tPath.curLoc += tPath.forward
                tPath.process()
                nProcessed += 1
            else:
                # #value this path next periodic activation
                v.extend([valA[i]])
                p.extend([pathA[i]])
        self.inReady = [v, p]
        if len(v) > 0:
            self.reschedule()
        return self

    def calculate(self):  # #area weighted field of inputs
        valA = self.inReady[0]
        pathA = self.inReady[1]
        rv = 0
        total = 0.0
        assert(len(valA) == len(pathA))
        for i in range(0, len(valA)):
            path = pathA[i]
            val = valA[i]
            cNode = path.nodes[path.curLoc]
            thisVDFM2 = cNode._sqM
            total += (val * thisVDFM2)
        rv = (total / self._sqM)
        return rv

    def ready(self, field, path):
        conn = self.inReady
        conn[0].append(field)
        conn[1].append(path)

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
        self._fieldStep = node.time.currentStep

    class path:
        def __init__(self, array=[]):
            self.nodes = []
            self.to(array)
            self.curLoc = None
            self.forward = -1
            self._exposure = 0

        def to(self, a):
           self.nodes.extend(a)

        def frm(self, a):
            self.nodes = [a].extend(self.nodes)
            self.curLoc = None

        def adjoin(self, path):
            assert(path.nodes[0] == self.nodes[len(self.nodes) - 1])
            self.nodes.extend(arr[1:])

        def extendPath(self, extension):
            if extension is None or len(extension.nodes) == 0 or len(self.nodes) == 0:
                print(self)
                import pdb; pdb.set_trace()
            if not self.nodes[len(self.nodes) - 1] == extension.nodes[0]:
                import pdb; pdb.set_trace()
            self.paths.append(extension.nodes[1:])



        def __str__(self):
            rv = []
            for i in self.nodes:
                if (self.curLoc is not None) and i == self.nodes[self.curLoc]:
                    rv.append("*" + i.name + "*")
                else:
                    rv.append(i.name)
            return str(rv)

        def process(self):  # #one step at a time
            srcNode = self.nodes[self.curLoc]
            srcField = srcNode.field
            if self.curLoc+self.forward < 0 or \
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
            targetNode.ready(srcField, self)
            t1 = max(node.time.currentStep, srcNode._fieldStep) + srcNode.delay
            node.time.scheduleAt(targetNode, t1)
            return self


class person(node):
    def __init__(self, name):
        node.__init__(self, name, role="PERSON")
        self._infected = False
        self._infectedStep = -1
        node.persons.append(self)
        self.paths = []
        self.nextPath = None
        self._exposure = 0  # #time integral of field
        self.pFactor = 0.0  # #protection of PPE
        self.pNum = 0

    def reset(self):  # #for next step
        node.reset(self)
        #  #self.lastStep = self._fieldStep
        #  #self._fieldStep = node.time.currentStep
        self.pNum = 0

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
            return True
        node.process(self)
        tPath.forward *= -1
        # #assert(tPath.nodes[tPath.curLoc] == self)
        # #forward huskies
        if (self.pNum < 2):
            tPath.process()
        # #next required to 
        self.inReady = [[], []]
        return self

    @property
    def infected(self):
        return self._infected

    @infected.setter
    def infected(self, val):
        self._infected = val
        self._infectedStep = node.time.currentStep
        print("at " + str(node.time.currentStep) + "INFECTING " + self.name)

    def addPath(self, path):
        if (self.nextPath is None):
            self.nextPath = 0
        assert(path.nodes[0] == self)
        self.paths.append(path)

        
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
    
    cNum = 0

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

    # #returns array of nodes

    def pathTo(self, pathA=[], bNode=None):  # #path to person through children
        self.level = max(self.level, len(pathA))
        if len(pathA) > 0:
            cName = self.name + "." + str(pathA[0])
            nd = node.names.get(cName)
            if (nd is None):
                nd = composite(cName, self.level-1)
                self.children[pathA[0]] = nd
            endPath = nd.pathTo(pathA[1:], bNode)
            endPath.to([self])
            return endPath
        else:
            if bNode is None:
                bNode = person(self.name + ".PERSON" + str(composite.cNum))
                composite.cNum += 1
            return node.path([bNode, self])





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
node.time.initSim()
node.time.step()
# #print("\nNode procesed:\t"+str(node.time.processNextNode()))
# ##print("\nNode processed:\t"+str(node.time.processNextNode()))
# #node.time.finish()
print(node.time)
