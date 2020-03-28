import random
import numpy as np


class Group:
    def __init__(self, size, rate, code, type_):
        self.code = code
        self.type = type_
        self.transmission_rate = rate
        self.demographics = [0, 0, 0]
        self.infected_count = 0
        self.transmissions = 0
        self.size = size
        self.members = []

    def __str__(self):
        return "Size: {} Infected: {}".format(self.size, self.infected_count)

    def __repr__(self):
        return "Code: {} Size: {} Infected: {} T-rate: {:.2f}".format(self.code, self.size, self.infected_count,
                                                                      self.transmission_rate)

    def display(self):
        print("Code: {} Size: {} Infected: {}".format(self.code, self.size, self.infected_count))
        return

    def get_members(self):
        return self.members

    def plastic(self):
        self.infected_count += np.random.choice([1, 0], p=[self.transmission_rate, 1 - self.transmission_rate])

    def transmit(self):
        mems = random.sample(self.members, self.infected_count)
        for mem in mems:
            mem.infect()
        self.infected_count = 0


def get_group(g_list, code):
    for grp in g_list:
        if grp.code == code:
            return grp
