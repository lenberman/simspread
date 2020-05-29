ROLES = ["unassigned","PERSON", "PPE", "ROOM","HOSPITAL" ,"ELEVATYOR" ,"APT" ,"STREET" ,"BAR" , "RESTAURANT" ,"STORE" ,"ESSENTIAL" ,"MEDICAL" ,"BUS" ,"CAR" ,"CARRIAGE" ,"PLATFORM" ,"BUSSTOP" ,"STAIRWAY" ,"REGION" ] 


class future:
    events = {}
    currentTime = 0
    maxTime = 0

    def scheduleAt(self, node, time): # #reschedule if necessary
        assert(time >= self.currentTime)
        nodeCurrentSchedule = node.scheduledAt
        self.maxTime = max(self.maxTime,time,nodeCurrentSchedule)
        if nodeCurrentSchedule >= 0:
            if nodeCurrentSchedule >= time:
                return
            else: # #less than requested time, 
                ct = future.events[nodeScheduledTime]
                ct . remove( node )
        ct = future.events.get(time)
        if ct is None:
            ct = []
            future.events[time] = ct
        ct.append(node)
        node.scheduledAt = time
        
        
    def initSim(self):
        for i in node.persons:
            self.scheduleAt(i,self.currentTime)

    def popNextNode(self): # # AT CURRENT TIME or increment currentTime if None
        nn = self.events.get(self.currentTime)
        if nn is None or len(nn) == 0:
            self.currentTime += 1
            return None
        if len(nn) > 0:
            rv = nn[0]
            nn = nn[1:]
            self.events[self.currentTime] = nn
            assert(isinstance(rv,node))
            return rv

    def processNextNode(self): #   # returns processed node
        nd = self.popNextNode()
        while(nd is None):
            if  self.currentTime <= self.maxTime:
                nd = self.popNextNode()
                if ( nd is None):
                    self.currentTime += 1
            else:
                return None
        assert(isinstance(nd,node))
        return nd . process()

    def finish(self): # #simulate all currently scheduled nodes
        endTime = self.maxTime
        while True and self.currentTime <= endTime:
            nd = self.processNextNode()
            if nd is None:
                print("Completed DEPTH: " + str(self.currentTime))
                return True
        

    
class node:
    names = {}
    persons= []
    time = future()

    def __init__(self, name, role=ROLES[0], field=0, sqM=1):
        self.name = name
        if name in node.names:
            raise Exception("Duplicate name:" + name)
        node.names[name] = self
        self._role = role
        self._field = field # #infectivity
        self._fieldTime = future.currentTime # 

        self.scheduledAt = -1
        self._exposure = 0 # #time integral of field
        self._sqM = sqM
        self.delay = 1 #
        self.crowdFactor = 1
        self.inReady = [[],[]]  # #paths & field connections
    def process(self):
        self.field = self.calculate(self.inReady)
        
        for i in range(0,len(self.inReady[1])-1):
            tPath = self.inReady[1][i]
            assert(self == tPath.nodes[tPath.curLoc+tPath.forward])
            tPath.process()
        self.inReady[0] = []
        self.inReady[1] = []
        return self

    def calculate(self, a ):
        valA = a[0]
        pathA = a[1]
        total = 0.0
        sq = 0.0
        assert(len(valA)==len(pathA))
        for i in range(0,len(valA)):
            path = pathA[i]
            val = valA[i]
            cNode = path.nodes[path.curLoc]
            assert(cNode.field==val)
            total += val * cNode._sqM
            sq += cNode._sqM
        rv = total / sq
        return rv
    def ready(self, field, path):
        conn =self.inReady
        conn[0].append(field)
        conn[1].append(path)
        
    @property
    def field(self):
        return self._field
    @field.setter
    def field(self,val):
        self._field = val
        self._fieldTime = future.currentTime

    class path:
        def __init__(self, array):
            self.nodes = []
            self.nodes.extend(array)
            self.curLoc = 0
            self.forward = 1
        def process(self): # #one step at a time
            srcNode = self.nodes[self.curLoc]
            targetNode = self.nodes[self.curLoc+self.forward]
            # # 4 steps:addValue/schedule targetNode, Note: path direction available to targetNode
            targetNode.ready(srcNode.field,self)
            node.time.scheduleAt(targetNode,future.currentTime+srcNode.delay)
        def augmentPath(self, arr):
            if len(nodes) == 0:
                self.nodes.extend(arr)
                return
            if (arr[0] == self.nodes[len(nodes)-1]) :
                self.nodes.append(arr[1:])
            else:
                self.nodes.append(arr)


class person(node):
    def __init__(self, name):
        node.__init__(self,name,ROLES[1],0,1)
        self._infected = False
        self._infectedTime = -1
        node.persons.append(self)
        self.paths = []
        self.nextPath = None
    def process(self): # #THIS BEGINS A JOURNEY ALONG A PATH
        if ( self.infected ):
            self.field += 1   # #assignment overloaded in node
        tPath = self.paths[self.nextPath]
        tPath.forward *= -1
        assert(tPath.nodes[tPath.curLoc]==self)
        # #continue processing along the path
        tPath.process()
        return self
    @property
    def infected(self):
        return self._infected
    @infected.setter
    def infected(self,val):
        assert(val==True or val==False)
        self._infected = val
        if self.infected:
            self.field += 1
        print("INFECTING " + self.name)
    def addPath(self, ndA):
        if (self.nextPath is None):
            self.nextPath = 0
        assert(ndA[0]==self)
        for i in ndA:
            if isinstance(i,PPE):
                i.prsn = self
        self.paths.append(node.path(ndA))
        

class PPE(node):
    cnt = 0
    def __init__(self,role=ROLES[2], prsn=None):
        node.__init__(self,name="ppe."+str(PPE.cnt),role=role)
        PPE.cnt += 1
        self.prsn = prsn
        self.pFactor = .1
    def calculate(self, a):
        assert(len(a)==1)  #push value along paths
        return self.pFactor*a[0]
    
        
lb=person("len")
sarah=person("sarah")
gerry=person("gerry")
lb.infected=True
test=node("task")
gerry.addPath([gerry,test])
lb.addPath([lb,test])
sarah.addPath([sarah,PPE(),test])
node.time.initSim()
node.time.finish()
