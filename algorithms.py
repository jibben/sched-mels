import random

# These are all of the algorithm classes for seating
# we have to do it as a class becuase sometimes we need to keep track of state

class SeatingAlgorithm(object):
    ''' Abstract class '''

    def __init__(self, tables):
        pass

    def find_seats(self, to_seat, tables, t):
        raise NotImplemented('Must implement find_seats!')


class SeatWherever(SeatingAlgorithm):

    def __init__(self):
        pass

    def find_seats(self, to_seat, tables, t):
        tables_used = set()
        pairings = []

        table_order = list(range(len(tables)))
        random.shuffle(table_order)

        for party in to_seat:
            for t in table_order:
                if tables[t][1] >= party[1] and tables[t][0] not in tables_used:
                    pairings.append(([tables[t][0]], party))
                    tables_used.add(tables[t][0])
                    break

        return pairings


class TightSeating(SeatingAlgorithm):

    def __init__(self):
        pass

    def find_seats(self, to_seat, tables, t):
        tables_used = set()
        pairings = []
        for party in to_seat:
            for table in tables:
                if table[1] >= party[1] and \
                        (table[1] <= party[1] + 1 or table[1] > 6) and \
                        table[0] not in tables_used:
                    pairings.append(([table[0]], party))
                    tables_used.add(table[0])
                    break

        return pairings


class SmallestAvailable(SeatingAlgorithm):

    def __init__(self):
        pass

    def find_seats(self, to_seat, tables, t):
        tables_used = set()
        pairings = []

        table_sizes = {}
        for t in tables:
            if t[1] not in table_sizes:
                table_sizes[t[1]] = []

            table_sizes[t[1]].append(t)

        sizes = sorted(list(table_sizes.keys()))

        table_sizes = {s : [t for t in tables if t[1] == s] for s in range(20)}

        for party in to_seat:
            seated = False
            s_pos = 0
            while not seated and s_pos < len(sizes):
                if sizes[s_pos] >= party[1]:
                    for table in table_sizes[sizes[s_pos]]:
                        if table[0] not in tables_used:
                            pairings.append(([table[0]], party))
                            tables_used.add(table[0])
                            seated = True
                            break
                s_pos += 1

        return pairings


class RoundRobin(SeatingAlgorithm):

    def __init__(self, tables):
        self.max_section = 0
        self.last_section = self.max_section

        for t in tables:
            if t[3] > self.max_section:
                self.max_section = t[3]

        self.max_section += 1

    def find_seats(self, to_seat, tables, t):
        table_section = {s : [] for s in range(self.max_section)}
        for t in tables:
            table_section[t[3]].append(t)

        tables_used = set()
        pairings = []

        for party in to_seat:
            seated = False
            section = (self.last_section + 1) % (self.max_section)
            while not seated and section != self.last_section:
                for table in table_section[section]:
                    if table[1] >= party[1] and table[0] not in tables_used:
                        pairings.append(([table[0]], party))
                        tables_used.add(table[0])
                        seated = True
                        self.last_section = section
                        break
                section = (section + 1) % (self.max_section)

        return pairings


class SmallParties(SeatingAlgorithm):

    def __init__(self):
        pass

    def find_seats(self, to_seat, tables, t):
        tables_used = set()
        pairings = []
        for party in to_seat:
            for table in tables:
                if table[1] >= party[1] and \
                        party[1] <=5 and \
                        table[0] not in tables_used:
                    pairings.append(([table[0]], party))
                    tables_used.add(table[0])
                    break

        return pairings


class FewestPeople(SeatingAlgorithm):

    def __init__(self, tables):
        self.sections = []

        section_set = set()
        for t in tables:
            if t[3] not in section_set:
                self.sections.append([t[3], 0])
                section_set.add(t[3])

    def find_seats(self, to_seat, tables, t):
        # we will organize tables by section
        tables_section = {s[0] : [t for t in tables if t[3] == s[0]] for s in self.sections}
        tables_used = set()
        pairings = []

        for party in to_seat:
            seated = False
            s_pos = 0
            while not seated and s_pos < len(self.sections):
                section = self.sections[s_pos]
                for table in tables_section[section[0]]:
                    if table[1] >= party[1] and table[0] not in tables_used:
                        pairings.append(([table[0]], party))
                        tables_used.add(table[0])
                        seated = True
                        section[1] += party[0]
                        self.sections.sort(key = lambda x : x[1])
                        break
                s_pos += 1

        return pairings
