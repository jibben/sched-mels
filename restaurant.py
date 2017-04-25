import random
import heapq
from pprint import pprint

# in minutes
AVG_ARRIVAL_INTERVAL = 15

SIZE_TO_SEATED = { # in hours
        2 : (1.1, 0.15),
        3 : (1.2, 0.2),
        4 : (1.25, 0.23),
        5 : (1.4, 0.24),
        6 : (1.6, 0.28),
        7 : (1.65, 0.3),
        8 : (2, 0.35),
}


ARRIVAL_TO_SIZE = {
        0 : 0.0,
        1 : 0.0,
        2 : 0.19,
        3 : 0.46,
        4 : 0.70,
        5 : 0.80,
        6 : 0.90,
        7 : 0.96,
        8 : 1.0,
}

TABLES = [
    # table 0 can seat 4 people, is next to table 1, and in section 0
    [0, 4, [1], 0],
    [1, 4, [0,2], 1],
    [2, 8, [1], 2]
]


def get_size(u):
    assert 0.0 <= u and u <= 1.0, 'u must be between 0 and 1!'
    for i in range(9):
        if u <= ARRIVAL_TO_SIZE[i]:
            return i

def sample_seated_time(size):
    mu, sigma = SIZE_TO_SEATED[size]
    return random.normalvariate(mu, sigma) * 60


def arrival_func(t):
    u = random.random()
    size = get_size(u)

    time = random.expovariate(1.0 / AVG_ARRIVAL_INTERVAL)

    return (size, time + t)


# These are all of the algorithm classes for seating
# we have to do it as a class becuase sometimes we need to keep track of state

class SeatingAlgorithm(object):
    ''' Abstract class '''

    def __init__(self):
        pass

    def find_seats(self, to_seat, tables, t):
        raise NotImplemented('Must implement find_seats!')


class SeatWherever(object):

    def __init__(self):
        pass

    def find_seats(self, to_seat, tables, t):
        tables_used = set()
        pairings = []
        for party in to_seat:
            for table in tables:
                if table[1] >= party[1] and table[0] not in tables_used:
                    pairings.append(([table[0]], party))
                    tables_used.add(table[0])
                    break

        return pairings


class RoundRobin(object):

    def __init__(self):
        self.last_section = 0

    def find_seats(self, to_seat, tables, t):
        pass


class Restaurant(object):
    ''' Restaurant object to keep track of tables'''

    def __init__(self, tables=None, only_neighbors=False):
        if tables:
            self.tables = {t[0] : t[1:] + [False, None] for t in tables}
        else:
            self.tables = {}
        self.only_neighbors = only_neighbors

        self.table_heap = []

    def check_neighbors(self, tids):
        full_set = set(tids[1:])
        neighbor_set = set([tids[0]])
        added = 1

        while len(neighbor_set) < len(tids) and added:
            added = 0
            to_remove = set()
            for t in full_set:
                for n in self.tables[t][1]:
                    if n in neighbor_set:
                        added += 1
                        to_remove.add(t)
                        neighbor_set.add(t)
                        break

            full_set -= to_remove

        if full_set:
            return False, [t for t in full_set]
        else:
            return True, []

    def is_empty(self):
        return not self.table_heap

    def add_table(self, tid, capacity, neighbors, section):
        self.tables[tid] = [capacity, neighbors, section, False, None]

    def get_available_tables(self):
        return [[tid,] + self.tables[tid][0:3] for tid in self.tables if not self.tables[tid][3]]

    def add_party(self, tids, party, t):
        assert sum([self.tables[tid][0] for tid in tids]) >= party[1], \
                "Cannot seat party of size {} at tables {}".format(tids, party[1])

        assert all([not self.tables[tid][3] for tid in tids]), \
                "Not all tables are available!"

        if self.only_neighbors:
            res, tbls = self.check_neighbors(tids)
            assert res, "Tables cannot be combined! {} not neighbor".format(tbls)

        for tid in tids:
            self.tables[tid][3] = True
            self.tables[tid][4] = party
            heapq.heappush(self.table_heap, (party[2] + t, tid, party))

        return self.table_heap[0][0]

    def get_next_departure(self):
        if len(self.table_heap) > 0:
            return self.table_heap[0][0]
        else:
            return float('inf')

    def do_departure(self):
        t, tid, party = heapq.heappop(self.table_heap)
        self.tables[tid][3] = False
        self.tables[tid][4] = None

        while self.table_heap and self.table_heap[0][2][0] == party[0]:
            t, tid, party = heapq.heappop(self.table_heap)
            self.tables[tid][3] = False
            self.tables[tid][4] = None

        return party



def sim_night(restaurant, seater, arrival_func, seated_time_func, t_max):
    next_arrival = arrival_func(0)
    next_departure = restaurant.get_next_departure()
    to_seat = []

    party_log = {}

    t = 0
    pid = 0

    while t_max > next_arrival[1]:
        # if the next event is an arrival
        if next_arrival[1] <= next_departure:
            # update time
            t = next_arrival[1]
            to_seat.append((pid, next_arrival[0], seated_time_func(next_arrival[0])))
            party_log[pid] = {
                'party_size' : next_arrival[0],
                'a_time' : t,
                's_time' : -1,
                'd_time' : -1,
            }
            pid += 1
            # get next arrival
            next_arrival = arrival_func(t)

            # process people who coculd be seated
            pairings = seater.find_seats(to_seat, restaurant.get_available_tables(), t)

            # seat parties and remove them from to_seat
            seated = set()
            for tid, party in pairings:
                seated.add(party[0])
                party_log[party[0]]['s_time'] = t
                restaurant.add_party(tid, party,t)

            next_departure = restaurant.get_next_departure()
            to_seat = [p for p in to_seat if p[0] not in seated]

        # if the next event is a departure
        else:
            # update time
            t = next_departure

            # process departure and log info
            party = restaurant.do_departure()

            party_log[party[0]]['d_time'] = t

            # process people who coculd be seated
            pairings = seater.find_seats(to_seat, restaurant.get_available_tables(), t)

            # and we will try to seat parties and remove then from to_seat
            seated = set()
            for tid, party in pairings:
                seated.add(party[0])
                party_log[party[0]]['s_time'] = t
                restaurant.add_party(tid, party, t)

            # update time of next departure
            next_departure = restaurant.get_next_departure()

            to_seat = [p for p in to_seat if p[0] not in seated]

    # once the restaurant closes, we let everyone finish eating
    while not restaurant.is_empty():
        # update time
        t = next_departure

        # process departure and log info
        party = restaurant.do_departure()
        party_log[party[0]]['d_time'] = t

        if to_seat:
            # process people who coculd be seated
            pairings = seater.find_seats(to_seat, restaurant.get_available_tables(), t)

            # and we will try to seat parties and remove then from to_seat
            seated = set()
            for tid, party in pairings:
                seated.add(party[0])
                party_log[party[0]]['s_time'] = t
                restaurant.add_party(tid, party, t)

            to_seat = [p for p in to_seat if p[0] not in seated]

        # update time of next departure
        next_departure = restaurant.get_next_departure()

    return party_log

def main():
    # to try a different algorithm, just repleace this seater with another
    # class - the class will only be called by seater.find_seats
    seater = SeatWherever()
    restaurant = Restaurant(TABLES)

    results = sim_night(restaurant, seater, arrival_func, sample_seated_time, 120)

    pprint(results)


if __name__ == '__main__':
    main()
