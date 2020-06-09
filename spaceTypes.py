from space import *

class room(node):
    def __init__(self, name):
        node.__init__(self, name )



class bar(node):
    def __init__(self, name):
        node.__init__(self, name )


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

class building(composite):
    def __init__(self, address, shape=[1, 8, 1, 8]):
        self.roomsPerApt = shape[0]
        self.aptPerFl = shape[1]
        self.numElevators = shape[2]
        self.numFloors = shape[3]





dispatch = { "room": room, "person": person, "bar": bar, "restaurant": restaurant, "store": store, "medical":  medical, "bus": bus, "car": car, "carriage": carriage, "platform": platform, "busstop": busstop, "elevator":  elevator, "stairway": stairway, "street": street, "composite": composite }

x=dispatch["room"]("ROOM")
print(x)
