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
        #Rebondissement
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
        if self.a != Vector2(0, 0):
            self.v = self.a     # On fait ça car bug: tous les body ont le même v
        if self.v.length() > self.vmax:
            self.v.scale_to_length(self.vmax)
        self.a = Vector2(0, 0)
        self.position += self.v


class Agent:
    def __init__(self, body, status="sain"):
        self.uuid = random.randint(0, 1000000)
        self.body = body
        self.listPerception = []
        self.status = status
        self.previousStatus = status
        self.start = True
        self.duree = 0

    def filtrePerception(self):
        voisins = []
        for p in self.listPerception:
            voisins.append(p)
        return voisins

    def doDecision(self):
        if self.start:
            self.start = False
            self.body.a = Vector2(random.randint(-5, 5), random.randint(-5, 5))
        self.duree += 1
        if self.status != self.previousStatus:
            self.duree = 0
            self.previousStatus = self.status
        if self.status == "mort":
            self.body.a = Vector2(0, 0)
            self.body.v = Vector2(0, 0)

    def show(self):
        match self.status:
            case "sain":
                couleur = (0, 255, 0)
            case "infecté":
                couleur = (255, 0, 0)
            case "mort":
                couleur = (100, 100, 100)
            case "quarantaine":
                couleur = (0, 0, 255)
            case _:
                couleur = (0, 0, 0)
        core.Draw.circle(couleur, self.body.position, self.body.size)


class Epidemie:
    def __init__(self, dico):
        self.dico = dico


class Environnement:
    def __init__(self):
        self.L = core.WINDOW_SIZE[0]
        self.H = core.WINDOW_SIZE[1]
        self.listAgent = []
        self.listItem = []
        self.epidemie = None

    def computePerception(self):
        for agent in self.listAgent:
            agent.listPerception = []
            for a in self.listAgent:
                if agent.body.fustrum.inside(a.body.position) and a.uuid != agent.uuid:
                    agent.listPerception.append(a)

    def computeDecision(self):
        for agent in self.listAgent:
            agent.doDecision()

    def applyDecision(self):
        for agent in self.listAgent:
            agent.body.applyDecision()

    def update(self):
        dico = self.epidemie.dico
        for a1 in self.listAgent:
            if a1.status == "infecté":
                for a2 in self.listAgent:
                    if a1.uuid != a2.uuid and a2.status == "sain":
                        if a1.body.position.distance_to(a2.body.position) < a1.body.size + a2.body.size + dico["distContagion"]:
                            if dico["pContagion"] > random.random() and a1.duree > dico["dContagion"]:
                                a2.status = "infecté"
                                break
                if a1.duree > dico["dDeces"]:
                    if dico["pDeces"] > random.random():
                        a1.status = "mort"
                        continue




    def show(self):
        s, i, d = 0, 0, 0
        for agent in self.listAgent:
            agent.show()
            if agent.status == "sain":
                s += 1
            elif agent.status == "infecté":
                i += 1
            elif agent.status == "mort":
                d += 1
        n = len(self.listAgent)
        print("Sain: ", s/n*100, "%", "Infecté: ", i/n*100, "%", "Mort: ", d/n*100, "%")


    def addAgent(self, agent):
        self.listAgent.append(agent)

    def addRandomAgents(self, n):
        size = 10
        for i in range(n):
            a = Agent(Body(Vector2(random.randint(size, self.L-size), random.randint(size, self.H-size)), size))
            self.listAgent.append(a)

    def delAgent(self, agent):
        self.listAgent.remove(agent)


def setup():
    core.fps = 30
    core.WINDOW_SIZE = [800, 600]

    env = Environnement()
    core.memory("env", env)

    env.epidemie = Epidemie({"dIncubation": 0, "dContagion": 50, "pContagion": 0.8,
                             "dDeces": 100, "pDeces": 0.2, "distContagion": 20})
    env.addRandomAgents(30)

def run():
    core.cleanScreen()

    env: Environnement = core.memory("env")
    env.show()

    env.computePerception()
    env.computeDecision()
    env.applyDecision()
    env.update()

    click = core.getMouseLeftClick()
    if click:
        pos = click
        max = 1000
        amax = None
        for a in env.listAgent:
            dist = a.body.position.distance_to(pos)
            if dist < max:
                max = dist
                amax = a
        amax.status = "infecté"




core.main(setup, run)
