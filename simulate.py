import numpy as np
import random
import pandas as pd
import congif as cgf
from people import Dude
from networks import Group
from tools import build_df
import plotly.express as px


class Simulate:
    def __init__(self, comm_size):
        self.comm_size = comm_size
        self.houses = []
        self.outer_circles = []
        self.peeps = []
        self.networks = []
        self.cumulative_cases = {'day': [0, 0, 0], 'cases': [0, 0, 0], 'type': ['total', 'infected-a', 'infected-s']}
        self.total_cases = 0
        self.total_asymp = 0
        self.total_symp = 0
        self.total_deaths = 0
        self.total_recoveries = 0

    def create_houses(self):

        for i in range(0, self.comm_size):
            rate = random.random()
            size = random.randint(1, 4)
            grp = Group(size, rate, i, 'inner')
            self.houses.append(grp)
        return self.houses

    def init_peeps(self):

        for i in range(0, len(self.houses)):
            job = random.choice(cgf.job_type)
            age = random.randint(18, 80)
            person = Dude(job, age, i, network=[self.houses[i]])
            self.houses[i].members.append(person)
            self.peeps.append(person)

        return self.peeps

    def populate_houses(self):
        pep_cnt = len(self.peeps)

        for house in self.houses:
            job = house.members[0].job

            for new_member in range(0, house.size - 1):
                age = abs(house.members[0].age + random.randint(-5, 5))
                person = Dude(job, age, pep_cnt, network=[house])
                house.members.append(person)
                self.peeps.append(person)
                pep_cnt += 1

        return

    def genesis(self):
        self.houses = self.create_houses()

        self.peeps = self.init_peeps()

        self.populate_houses()

        return self.houses, self.peeps

    def outer_circle_gen(self):

        # Size of outer circles, dependent on populaiton size
        ocircle_size = int(len(self.peeps) * 0.008 + random.randint(-5, 5))

        # Number of outer circles, dependent on inner circle count
        ocircle_count = int((len(self.peeps) / ocircle_size) * 0.95)

        for i in range(0, ocircle_count):
            # Lower rates for outr circles
            rate = random.uniform(0, 0.5)
            size = int(len(self.peeps) * random.uniform(0.0001, 0.0008) + random.randint(-5, 5))
            grp = Group(size, rate, i, 'outer')
            self.outer_circles.append(grp)

        for pepe in self.peeps:
            nets = random.sample(self.outer_circles, random.randint(1, 3))
            for net in nets:
                net.members.append(pepe)
                pepe.network.append(net)

        return self.outer_circles

    def begin_sim(self):
        # Begin by infecting one person
        r_pep = random.choice(self.peeps)
        print("Person {} was infected first\n".format(r_pep.name))
        r_pep.infect()

    def day(self):
        # Iterate over all people and decide whether they will transmit to their repsective groups
        # And if they have reached their recovery time what whill happen to them.
        for person in self.peeps:
            if (person.state == cgf.states[1]) or (person.state == cgf.states[2]):
                person.elapsed_infected += 1
                for net in person.network:
                    net.plastic()
                if person.elapsed_infected >= person.r_time:
                    person.recover(np.random.choice([3, 4], p=[0.95, 0.05]))

        # Using the new infected count of each Group transmit it accordingly
        new_cases = 0
        for n in self.networks:
            new_cases += n.infected_count
            if n.infected_count > 0:
                n.transmit()

        ss = build_df([self.peeps], 'p')['state'].value_counts()
        for s in cgf.states:
            if s not in ss:
                ss[s] = 0

        self.total_cases += new_cases
        self.total_asymp += ss['infected-a']
        self.total_symp += ss['infected-s']

        print("----------Virus Report----------\n")
        print("Today's new cases: {}".format(new_cases))
        prop = ((ss['infected-s'] + ss['infected-a']) / len(self.peeps)) * 100
        print("Total Infected: {} ({:.1f}%)".format(ss['infected-s'] + ss['infected-a'], prop))
        print("Asymptomatic Cases:", ss['infected-a'])
        print("Symptomatic Cases:", ss['infected-s'])
        print("Total Recoveries:", ss['recovered'])
        print("Total Deaths:", ss['dead'])
        print("Stay Home, Save Lives\n")

    def isolate_phase_one(self):
        # First set of isolation and social distancing

        for person in self.peeps:
            print(person)

    def run_simulation(self, duration):

        # Create Houses
        print("Creating dwellings and populating them")
        houses, peeps = self.genesis()
        print("Houses populated")

        # Create Outer Circles

        outer_circles = self.outer_circle_gen()
        self.networks = houses + outer_circles
        print("Total Population Size: {} Total Outer Networks: {}".format(len(self.peeps), len(self.outer_circles)))
        print("Running simulation!!\n")

        # Simulate daily transmissions for a month
        for i in range(0, duration):
            print("Day", i)
            if i == 0:
                self.begin_sim()
            else:
                self.day()
                # Add cumulative stats
                # Total
                self.cumulative_cases['day'].append(i)
                self.cumulative_cases['cases'].append(self.total_cases)
                self.cumulative_cases['type'].append('total')

                # Asymptomatic
                self.cumulative_cases['day'].append(i)
                self.cumulative_cases['cases'].append(self.total_asymp)
                self.cumulative_cases['type'].append('infected-a')

                # Symptomatic
                self.cumulative_cases['day'].append(i)
                self.cumulative_cases['cases'].append(self.total_symp)
                self.cumulative_cases['type'].append('infected-s')

    def report(self):
        fig = px.line(pd.DataFrame(self.cumulative_cases), x='day', y='cases', color='type')
        fig.show()


