import numpy as np
import time
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
        self.open_networks = []
        self.peeps = []
        self.networks = []
        self.cumulative_cases = {'day': [0, 0, 0], 'cases': [0, 0, 0], 'type': ['total', 'infected-a', 'infected-s']}
        self.total_cases = 0
        self.total_asymp = 0
        self.total_symp = 0
        self.total_deaths = 0
        self.total_recoveries = 0
        self.built = False

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

        # Number of outer circles, dependent on inner circle count
        ocircle_count = int(len(self.peeps) * 0.0675)
        sze = 0

        for i in range(0, ocircle_count):
            # Randomly create a large or small group
            if round(random.random()) == 1:
                # Lower rates for larger outer circles
                rate = random.uniform(0.01, 0.4)
                size = int(random.gauss(40, 30))
            else:
                rate = random.uniform(0.2, 0.65)
                size = int(random.gauss(15, 12))
            grp = Group(size, rate, i, 'outer')
            self.outer_circles.append(grp)
            sze += size
        # print(sze)
        self.open_networks = self.outer_circles.copy()

        for pepe in self.peeps:
            if len(self.open_networks) <= 3:
                break
            nets = random.sample(self.open_networks, random.randint(1, 3))

            for net in nets:
                cnt = 0
                solo = False
                # If network is full, find another one!
                while len(net.members) >= net.size:
                    # print(net.code)
                    # print(len(self.open_networks))
                    self.open_networks.remove(net)
                    cnt += 1
                    if cnt > len(self.open_networks):  # This needs to be verified as could try multiple times
                        solo = True
                        break
                    else:
                        net = random.choice(self.open_networks)
                if solo:
                    break
                else:
                    net.members.append(pepe)
                    pepe.network.append(net)

        return self.outer_circles

    def get_open_networks(self):
        circles = [net for net in self.outer_circles if len(net.members) < net.size]
        # for net in self.outer_circles:
        #     if len(net.members) < net.size:
        #         circles.append(net)

        return circles

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

    def remove_network(self, person, networks):
        # Remove person from networks and networks from person

        person.network = [net for net in person.network if net not in networks]
        for net in networks:
            net.members = [mem for mem in net.members if mem != person]

    def isolate_phase_one(self):
        # First set of isolation and social distancing
        print("\n-----------SELF ISOLATION PHASE ONE-----------\n")

        total_members = 0
        for net in self.outer_circles:
            total_members += len(net.members)
        print("Original Average Network Size:", total_members / len(self.outer_circles))

        for person in self.peeps:
            if len(person.network) == 0:
                print("Do nothing")
                break
            elif len(person.network) <= 2:
                isolated_networks = [person.network.pop(-1)]
            else:
                isolated_networks = [person.network.pop(-1), person.network.pop(-1)]
            self.remove_network(person, isolated_networks)

        total_members = 0
        for net in self.outer_circles:
            total_members += len(net.members)
        print("New Average Network Size: {}\n".format(total_members / len(self.outer_circles)))

    def setup(self):
        # Create Houses
        print("Creating dwellings and populating them")
        start = time.time()
        houses, peeps = self.genesis()
        d = time.time() - start
        if d > 60:
            print("Houses populated. It took {:.2f}mins".format(d/60))
        else:
            print("Houses populated. It took {:.1f}seconds".format(d))

        # Create Outer Circles
        start = time.time()
        outer_circles = self.outer_circle_gen()
        self.networks = houses + outer_circles
        d = time.time() - start
        if d > 60:
            print("Total Population Size: {} Total Outer Networks: {}. Time taken: {:.2f}mins".format(len(self.peeps), len(self.outer_circles), (time.time()-start)/60))
        else:
            print("Total Population Size: {} Total Outer Networks: {}. Time taken: {:.1f}secs".format(len(self.peeps), len(self.outer_circles), time.time()-start))
        self.built = True

    def day_iterate(self, duration):

        # Simulate daily transmissions for a month
        for i in range(0, duration):
            print("Day", i)
            if i == 0:
                self.begin_sim()
            else:
                if i == int(duration*0.75):
                    # When we reach the half was mark begin basic self isolation
                    self.isolate_phase_one()

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

    def run_simulation(self, duration):

        if not self.built:
            self.setup()

        print("Running simulation!!\n")
        self.day_iterate(duration)

    def report(self):
        fig = px.line(pd.DataFrame(self.cumulative_cases), x='day', y='cases', color='type')
        fig.show()
