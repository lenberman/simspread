ROLES = ["unassigned","PERSON", "PPE", "ROOM","HOSPITAL" ,"ELEVATYOR" ,"APT" ,"STREET" ,"BAR" , "RESTAURANT" ,"STORE" ,"ESSENTIAL" ,"MEDICAL" ,"BUS" ,"CAR" ,"CARRIAGE" ,"PLATFORM" ,"BUSSTOP" ,"STAIRWAY" ,"REGION" ] 


class future:
    events = {}
    currentTime = 0
    maxTime = 0

    def scheduleAt(self, node, time):
        assert(time >= self.currentTime)
        ct = future.events.get(time)
        if ct is None:
            ct = []
            future.events[time] = ct
        
    def initSim(self):
        for i in node.persons:
            self.scheduleAt(i,self.currentTime)

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

        self_lastTime = 0 
        self._exposure = 0 # #time integral of field
        self._sqM = sqM
        self.connect = [] # #paths to/from
        self.delay = 1 #
        self.crowdFactor = 1
    @property
    def field(self):
        return self._field
    @field.setter
    def field(self,val):
        self._field = val


    class path:
        def __init__(self):
            self.nodes = []
            self.curLoc = -1
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
    @property
    def infected(self):
        return self._infected
    @infected.setter
    def infected(self,val):
        assert(val==True or val==False)
        self._infected = val
        print("INFECTING " + self.name)
    def addPath(self, path):
        assert(path[0]==self)
        for i in path:
            if isinstance(i,PPE):
                i.prsn = self
        self.paths.append(path)
        

class PPE(node):
    cnt = 0
    def __init__(self,role=ROLES[2], prsn=None):
        node.__init__(self,name="ppe."+str(PPE.cnt),role=role)
        PPE.cnt += 1
        self.prsn = prsn
        self.pFactor = .1
    
        
lb=person("len")
sarah=person("sarah")
gerry=person("gerry")
lb.infected=True
test=node("lask")
gerry.addPath([gerry,test])
lb.addPath([lb,test])
sarah.addPath([sarah,PPE(),test])
node.time.initSim()
