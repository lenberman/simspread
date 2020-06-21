from space import *
from graphics import *

import pdb; pdb.set_trace()

class display:

    def __init(self, pop):
        self.pop = pop
        self.data = GraphWin()
        # #{} of arrays of [lastStep, fieldStep, field, infected, exposure]
        self.pData = {}  # #indexed by name, ordered (by step)
        # #array of [step, field, exposure]
        self.npData = {}  # # non-person nodes and paths
        self.pathData = {}
        self.displayStep = 0

    def rData(self, show=True):
        for nd in self.pop.cng.persons.values():
            if nd.name not in self.pData.keys():
                self.pData[nd.name] = []
            self.pData[nd.name].append([nd.lastStep, nd._fieldStep,
                                        nd._field, nd.infected, nd.exposure])
        for nd in self.pop.cng.names.values():
            if isinstance(nd, person):
                next
            if nd.name not in self.npData.keys():
                self.npData[nd.name] = []
            self.npData[nd.name].append([nd.lastStep, nd._fieldStep, nd._field])
        for path in self.pop.paths["person"]:
            if path not in self.pathData.keys():
                self.pathData[path._id] = []
            srcNode = path.getSrc()
            srcNodeAvailableTime = srcNode._fieldStep + srcNode.delay
            self.pathData[path._id].append(
                [self.pop.cng.future.currentStep,
                 srcNodeAvailableTime,
                 srcNode._field, path.getTarget()._field,
                 path._exposure])

win=GraphWin()
