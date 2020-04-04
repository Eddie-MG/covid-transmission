import random
import simulate.congif as cgf


class Dude:
    def __init__(self, occupation, age, name, state=cgf.states[0], underlying_conditions=False, network=[]):
        self.job = occupation
        self.name = name
        self.age = age
        self.state = state
        self.under_cond = underlying_conditions
        self.network = network
        self.elapsed_infected = 0
        self.r_time = random.randint(4, 14)

    def __str__(self):
        return "Job: {} Age: {} State: {}".format(self.job, self.age, self.state)

    def __repr__(self):
        return "Job: {} Age: {} State: {}".format(self.job, self.age, self.state)

    def infect(self):
        # The person is more likely to be symptomatic (but this is assumed).
        self.elapsed_infected = 0
        self.state = cgf.states[random.choices([1, 2], [1, 3])[0]]
        return self

    def uninfect(self):
        # The person was not actually infected
        self.state = cgf.states[0]
        return self

    def recover(self, val):
        # The person was infected but has now recovered
        self.state = cgf.states[val]
        self.elapsed_infected = 0
        return self


def get_person(p_list, name):
    for p in p_list:
        if p.name == name:
            return p
    print('No person with this name')
    return None
