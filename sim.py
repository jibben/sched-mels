import random
from pprint import pprint

from constants import AVG_ARRIVAL_INTERVAL, TABLES, SIZE_TO_SEATED, ARRIVAL_TO_SIZE
from algorithms import SeatWherever, TightSeating, RoundRobin
from restaurant import Restaurant

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
    rr_seater = RoundRobin(TABLES)
    restaurant = Restaurant(TABLES)

    #results = sim_night(restaurant, seater, arrival_func, sample_seated_time, 120)
    results = sim_night(restaurant, rr_seater, arrival_func, sample_seated_time, 120)

    pprint(results)


if __name__ == '__main__':
    main()
