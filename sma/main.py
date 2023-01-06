import random
from pygame.math import Vector2
import core


class Fustrum:
    def __init__(self, rayon, parent):
        self.rayon = rayon
        self.parent = parent

    def inside(self, position):
        if isinstance(position, Vector2):
            return position.distance_to(self.parent.position) < self.rayon


class Body:
    def __init__(self, position, size, v=Vector2(0, 0), vmax=5, a=Vector2(0, 0), amax=5):
        self.position = position
        self.size = size
        self.v = v
        self.vmax = vmax
        self.a = a
        self.amax = amax
        self.fustrum = Fustrum(100, self)

    def applyDecision(self):
        # Pour le rebondissement
        if self.position[0]-self.size <= 0:
            self.position[0] = self.size
            self.v[0] *= -1
            self.a[0] *= -1
        if self.position[0] + self.size > core.WINDOW_SIZE[0]:
            self.position[0] = core.WINDOW_SIZE[0] - self.size
            self.v[0] *= -1
            self.a[0] *= -1

        if self.position[1]-self.size <= 0:
            self.position[1] = self.size
            self.v[1] *= -1
            self.a[1] *= -1
        if self.position[1] + self.size > core.WINDOW_SIZE[1]:
            self.position[1] = core.WINDOW_SIZE[1] - self.size
            self.v[1] *= -1
            self.a[1] *= -1

        # Décision
        if self.a.length() > self.amax:
            self.a.scale_to_length(self.amax)
        self.v += self.a
        if self.v.length() > self.vmax:
            self.v.scale_to_length(self.vmax)
        self.position += self.v

    def show(self):
        core.Draw.circle((0, 0, 255), self.position, self.size)
        core.Draw.line((255, 255, 255), self.position, self.position + self.v)


class Agent:
    def __init__(self, body):
        self.uuid = random.randint(0, 1000000)
        self.body = body
        self.listPerception = []

    def filtrePerception(self, listPerception):
        target = None
        dtarget = 1000000
        voisins = []
        dangers = []

        for p in listPerception:
            if isinstance(p, Item):
                distance = self.body.position.distance_to(p.position)
                if p.type == "creep":
                    if distance < dtarget:
                        dtarget = distance
                        target = p
                else:
                    dangers.append(p)
            else:
                voisins.append(p)
        return voisins, target, dangers

    def doDecision(self):
        voisins, target, dangers = self.filtrePerception(self.listPerception)
        rep = Vector2(0, 0)
        att = Vector2(0, 0)
        if target is None and self.body.v.length() == 0:
            att += Vector2(random.randint(-5, 5), random.randint(-5, 5))
        else:
            for v in voisins:
                if v.body.size > self.body.size:
                    rep += self.body.position - v.body.position
                else:
                    att += v.body.position - self.body.position
            if len(voisins) != 0:
                rep /= len(voisins)
                att /= len(voisins)

            if target is not None:
                att += target.position - self.body.position

        for danger in dangers:
            d = self.body.position - danger.position
            rep += d
        self.body.a = rep + att

    def show(self):
        self.body.show()


class Item:
    def __init__(self, position, type):
        self.position = position
        self.type = type
        if self.type == "obstacle":
            self.size = 20
        elif self.type == "creep":
            self.size = 3

    def show(self):
        if self.type == "obstacle":
            core.Draw.circle((0, 255, 0), self.position, self.size)
        elif self.type == "creep":
            core.Draw.circle((255, 0, 0), self.position, self.size)


class Environnement:
    def __init__(self):
        self.L = core.WINDOW_SIZE[0]
        self.H = core.WINDOW_SIZE[1]
        self.listAgent = []
        self.listItem = []

    def computePerception(self):
        for agent in self.listAgent:
            agent.listPerception = []
            for item in self.listItem:
                if agent.body.fustrum.inside(item.position):
                    agent.listPerception.append(item)
            for a in self.listAgent:
                if agent.body.fustrum.inside(a.body.position) and a.uuid != agent.uuid:
                    agent.listPerception.append(a)

    def computeDecision(self):
        for agent in self.listAgent:
            agent.doDecision()

    def applyDecision(self):
        for agent in self.listAgent:
            agent.body.applyDecision()
            for item in self.listItem:
                if agent.body.position.distance_to(item.position) < agent.body.size + item.size:
                    if item.type == "creep":
                        self.delItem(item)
                        agent.body.size += 1
                        agent.body.vmax -= 0.1
                    else:
                        self.delAgent(agent)

    def show(self):
        for agent in self.listAgent:
            agent.show()
        for item in self.listItem:
            item.show()

    def addAgent(self, agent):
        self.listAgent.append(agent)

    def addItem(self, item):
        self.listItem.append(item)

    def addRandomAgents(self, n):
        size = 10
        for i in range(n):
            a = Agent(Body(Vector2(random.randint(size, self.L-size), random.randint(size, self.H-size)), size))
            self.listAgent.append(a)

    def addRandomObstacles(self, n):
        size = 20
        for i in range(n):
            o = Item(Vector2(random.randint(size, self.L-size), random.randint(size, self.H-size)), "obstacle")
            self.listItem.append(o)

    def addRandomCreeps(self, n):
        size = 3
        for i in range(n):
            c = Item(Vector2(random.randint(size, self.L-size), random.randint(size, self.H-size)), "creep")
            self.listItem.append(c)
            for item in self.listItem:
                if c.position.distance_to(item.position) < c.size + item.size and item != c:
                    self.delItem(c)
                    n += 1
                    break

    def delAgent(self, agent):
        self.listAgent.remove(agent)

    def delItem(self, item):
        self.listItem.remove(item)


def setup():
    core.fps = 30
    core.WINDOW_SIZE = [800, 600]

    env = Environnement()
    core.memory("env", env)

    env.addRandomAgents(1)
    env.addRandomCreeps(50)
    env.addRandomObstacles(5)


def run():
    core.cleanScreen()

    env: Environnement = core.memory("env")
    env.show()

    env.computePerception()
    env.computeDecision()
    env.applyDecision()


core.main(setup, run)
