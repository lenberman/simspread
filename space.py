ROLES = ["???", "PERSON", "PPE", "ROOM", "HOSPITAL", "ELEVATYOR",
         "APT", "STREET", "BAR", "RESTAURANT", "STORE", "ESSENTIAL",
         "MEDICAL", "BUS", "CAR", "CARRIAGE", "PLATFORM", "BUSSTOP",
         "STAIRWAY", "REGION"]

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
    names = {}
    persons = []
    time = future()

    def reset(self):  # #for next step
        self.lastStep = self._fieldStep
        self._fieldStep = node.time.currentStep

    def __init__(self, name, role=ROLES[0], field=0, sqM=1):
        self.name = name
        if name in node.names:
            raise Exception("Duplicate name:" + name)
        node.names[name] = self
        self._role = role
        self._field = field  # #infectivity
        self._fieldStep = node.time.currentStep
        self.lastStep = node.time.currentStep
        self.scheduledAt = -1
        self.scheduleInterval = 2
        self._sqM = sqM
        self.delay = 1
        self.crowdFactor = 1
        self.inReady = [[], []]  # #paths & field connections

    def __str__(self):
        val = self.name + "(" + self._role + ", field=" + str(self._field) + \
              ", fieldStep=" + str(self._fieldStep) + ", lastStep=" + \
              str(self.lastStep) + ")" + str(self.inReady[0])
        return val

    def process(self):
        if (True):
            print("\nProcessing(" + str(self.name) + ") in:\t" +
                  str(self.inReady[0]))
        #import pdb; pdb.set_trace()
        self.field = self.calculate()
        valA = self.inReady[0]
        pathA = self.inReady[1]
        v = []
        p = []
        for i in range(len(pathA)):
            tPath = pathA[i]
            #  #values furnished by inReady have path curLoc at source
            #  #assert(self == tPath.nodes[tPath.curLoc+tPath.forward])
            prevNode = tPath.nodes[tPath.curLoc]
            if prevNode._fieldStep + prevNode.delay <= self._fieldStep and \
               prevNode._fieldStep + prevNode.delay > self.lastStep:
                # #value from this path processed
                tPath.curLoc += tPath.forward
                tPath.process()
            else:
                # #value this path next periodic activation
                v.extend([valA[i]])
                p.extend([pathA[i]])
        self.inReady = [v, p]
        
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
            total += val * thisVDFM2
        rv = (total / self._sqM)
        return rv

    def ready(self, field, path):
        conn = self.inReady
        conn[0].append(field)
        conn[1].append(path)

    @property
    def field(self):
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
        def __init__(self, array):
            self.nodes = []
            self.nodes.extend(array)
            self.curLoc = 0
            self.forward = -1
            self._exposure = 0

        def __str__(self):
            rv = []
            for i in self.nodes:
                if i == self.nodes[self.curLoc]:
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
            if not isinstance(srcNode, PPE):
                self._exposure += srcField * srcNode.delay
            else:
                self._exposure *= srcNode.pFactor
            targetNode.ready(srcField, self)
            t1 = max(node.time.currentStep, srcNode._fieldStep) + srcNode.delay
            node.time.scheduleAt(targetNode, t1)
            return self

        def augmentPath(self, arr):
            if len(self.nodes) == 0:
                self.nodes.extend(arr)
                return
            if (arr[0] == self.nodes[len(self.nodes) - 1]):
                self.nodes.append(arr[1:])
            else:
                self.nodes.append(arr)


class person(node):
    def __init__(self, name):
        node.__init__(self, name, ROLES[1], 0, 1)
        self._infected = False
        self._infectedStep = -1
        node.persons.append(self)
        self.paths = []
        self.nextPath = None
        self._exposure = 0  # #time integral of field
        self.pNum = 0

    def reset(self):  # #for next step
        node.reset(self)
        #  #self.lastStep = self._fieldStep
        #  #self._fieldStep = node.time.currentStep
        self.pNum = 0

    def process(self):  # #ALONG A PATH
        if (self.infected):
            self.field = 1   # #assignment overloaded in node
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

    def addPath(self, ndA):
        if (self.nextPath is None):
            self.nextPath = 0
        assert(ndA[0] == self)
        for i in ndA:
            if isinstance(i, PPE):
                i.prsn = self
        self.paths.append(node.path(ndA))

    def calculate(self):
        if self.infected:
            return 1.0
        return self.field


class PPE(node):
    cnt = 0

    def __init__(self, person=None):
        if person is None:
            node.__init__(self, name="ppe."+str(PPE.cnt), role=ROLES[2])
        else:
            node.__init__(self, person.name + ".ppe", role=ROLES[2])
        PPE.cnt += 1
        self.prsn = person
        self.pFactor = .1

    def calculate(self):
        if len(self.inReady[0]) == 1:   # #push value along paths
            return self.pFactor*self.inReady[0][0]
        else:
            return self.field


lb = person("len")
sarah = person("sarah")
gerry = person("gerry")
lb.infected = True
test = node("task", role=ROLES[3])
gerry.addPath([gerry, test])
lb.addPath([lb, test])
sarah.addPath([sarah, PPE(person=sarah), test])
node.time.initSim()
node.time.step()
# #print("\nNode processed:\t"+str(node.time.processNextNode()))
# ##print("\nNode processed:\t"+str(node.time.processNextNode()))
# #node.time.finish()
print(node.time)
