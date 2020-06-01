ROLES = ["???", "PERSON", "PPE", "ROOM", "HOSPITAL", "ELEVATYOR",
         "APT", "STREET", "BAR", "RESTAURANT", "STORE", "ESSENTIAL",
         "MEDICAL", "BUS", "CAR", "CARRIAGE", "PLATFORM", "BUSSTOP",
         "STAIRWAY", "REGION"]

# ##import pdb; pdb.set_trace()


class future:
    events = {}
    currentTime = 0
    maxTime = 0

    def __str__(self):
        rv = "Current " + str(self.currentTime) + ", max " + str(self.maxTime)
        rv += str(self.events)
        return rv

    def scheduleAt(self, nd, time):  # #reschedule if necessary
        assert(time >= self.currentTime)  # #don't schedule in past
        print("\nSchedule " + str(nd) + " at " + str(time))
        if isinstance(nd, node):
            nodeCurrentSchedule = nd.scheduledAt
            if time > nd.scheduledAt:
                nd.scheduledAt = time
        else:#  #could be a path end
            nodeCurrentSchedule = -1
        self.maxTime = max(self.maxTime, time, nodeCurrentSchedule)
        if nodeCurrentSchedule >= 0:
            if nodeCurrentSchedule > time:
                return
            else:  # # == move to end of this time, 
                ct = self.events[nodeCurrentSchedule]
                ct.remove(nd)
        ct = self.events.get(time)
        if ct is None:
            ct = []
            self.events[time] = ct
        ct.append(nd)
        print(self)
        
    def initSim(self):
        self.currentTime += 1
        self.maxTime = max(self.maxTime, self.currentTime)
        assert(self == node.time)
        for ii in node.persons:
            ii.reset()  # # reset
            self.scheduleAt(ii, self.currentTime)

    def popNextNode(self):  # # returns null only when finished
        nn = self.events.get(self.currentTime)
        if nn is None or len(nn) == 0:
            self.currentTime += 1
            if self.currentTime > self.maxTime:
                return None
            else:  # #clock incremented
                return self.popNextNode()
        if len(nn) > 0:
            rv = nn[0]
            nn = nn[1:]
            self.events[self.currentTime] = nn
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

    def finish(self):  # #simulate all currently scheduled nodes
        while self.currentTime <= self.maxTime:
            nd = self.processNextNode()
            if nd is None:
                print("Completed DEPTH: " + str(self.currentTime))
                print("\t:maxTime:" + str(self.maxTime))
                return True
        return False

    
class node:
    names = {}
    persons = []
    time = future()

    def __init__(self, name, role=ROLES[0], field=0, sqM=1):
        self.name = name
        if name in node.names:
            raise Exception("Duplicate name:" + name)
        node.names[name] = self
        self._role = role
        self._field = field  # #infectivity
        self._fieldTime = node.time.currentTime
        self.lastTime = node.time.currentTime
        self.scheduledAt = -1
        self.scheduleInterval = 2
        self._exposure = 0  # #time integral of field
        self._sqM = sqM
        self.delay = 1
        self.crowdFactor = 1
        self.inReady = [[], []]  # #paths & field connections

    def reset(self):
        self.lastTime = self._fieldTime
        self._fieldTime = node.time.currentTime

    def __str__(self):
        val = self.name + "(" + self._role + ", field=" + str(self._field) + \
              ", fieldTime=" + str(self._fieldTime) + ", lastTime" + \
              str(self.lastTime) + ")"
        return val

    def process(self):
        if (True):
            print("\nProcessing(" + str(self.name) + "):\t" +
                  str(self.inReady[0]))
        import pdb; pdb.set_trace()
        self.field = self.calculate(self.field, self.inReady)
        valA = self.inReady[0]
        pathA = self.inReady[1]
        v = []
        p = []
        for i in range(len(pathA)):
            tPath = pathA[i]
            # #values furnished by inReady have path curLoc at source
            assert(self == tPath.nodes[tPath.curLoc+tPath.forward])
            prevNode = tPath.nodes[tPath.curLoc]
            if prevNode._fieldTime + prevNode.delay <= self._fieldTime and \
               prevNode._fieldTime + prevNode.delay > self.lastTime:
                # #value from this path processed
                tPath.curLoc += tPath.forward
                tPath.process()
            else:
                # #value from this path saved for next periodic activation
                # ##import pdb; pdb.set_trace()
                v.extend([valA[i]])
                p.extend([pathA[i]])
        self.inReady = [v, p]
        
        return self

    def calculate(self, cField, a):
        valA = a[0]
        pathA = a[1]
        total = 0.0
        sq = 0.0
        assert(len(valA) == len(pathA))
        for i in range(0, len(valA)):
            path = pathA[i]
            val = valA[i]
            cNode = path.nodes[path.curLoc]
            assert(cNode.field == val)
            total += val * cNode._sqM
            sq += cNode._sqM
        if sq != 0.0:
            rv = ((total / sq) + .5 * cField) * 2/3
        else:
            rv = cField
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
        self._field = val
        self.lastTime = self._fieldTime
        self._fieldTime = node.time.currentTime

    class path:
        def __init__(self, array):
            self.nodes = []
            self.nodes.extend(array)
            self.curLoc = 0
            self.forward = -1

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
                import pdb; pdb.set_trace()
                self.forward *= -1
            targetNode = self.nodes[self.curLoc+self.forward]
            targetNode.ready(srcField, self)
            t1 = max(node.time.currentTime, srcNode._fieldTime) + srcNode.delay
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
        self._infectedTime = -1
        node.persons.append(self)
        self.paths = []
        self.nextPath = None

    def process(self):  # #THIS BEGINS A JOURNEY ALONG A PATH
        if (self.infected):
            self.field = 1   # #assignment overloaded in node
        node.process(self)
        tPath = self.paths[self.nextPath]
        tPath.forward *= -1
        # #assert(tPath.nodes[tPath.curLoc] == self)
        # #forward huskies
        tPath.process()
        return self

    @property
    def infected(self):
        return self._infected

    @infected.setter
    def infected(self, val):
        self._infected = val
        self._infectedTime = node.time.currentTime
        print("at " + str(node.time.currentTime) + "INFECTING " + self.name)

    def addPath(self, ndA):
        if (self.nextPath is None):
            self.nextPath = 0
        assert(ndA[0] == self)
        for i in ndA:
            if isinstance(i, PPE):
                i.prsn = self
        self.paths.append(node.path(ndA))
        

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

    def calculate(self, cField, a):
        assert(len(a[0]) == 1)   # #push value along paths
        return self.pFactor*a[0][0]


lb = person("len")
sarah = person("sarah")
gerry = person("gerry")
lb.infected = True
test = node("task", role=ROLES[3])
gerry.addPath([gerry, test])
lb.addPath([lb, test])
sarah.addPath([sarah, PPE(person=sarah), test])
node.time.initSim()
node.time.finish()
print("\nNode processed:\t"+str(node.time.processNextNode()))
# ##print("\nNode processed:\t"+str(node.time.processNextNode()))
# #node.time.finish()
print(node.time)
