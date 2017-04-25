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

class SmallestCombining(SeatingAlgorithm):
    ''' I am so sorry to anyone who might look at this in the future '''

    def __init__(self, tables, max_hold):
        self.tables_dict = {t[0] : [t[1:4], -1] for t in tables}
        self.party_to_tables = {}
        self.largest_table = max([t[1] for t in tables])
        self.tables_held = {t[0] : -1 for t in tables}
        pass

    def find_seats(self, to_seat, tables, t):
        seatable_tables = set([t[0] for t in tables])

        table_sizes = {i : [] for i in range(self.largest_table + 1)}
        for t in tables:
            table_sizes[t[1]].append(t)

        pairings = []

        i = 0
        next_party = True
        while i < len(to_seat) and next_party:
            party = to_seat[i]
            seated = False
            size = party[1]
            # first we try to seat them at a single table
            while not seated and size <= self.largest_table:
                for table in table_sizes[size]:
                    if table[0] in seatable_tables:
                        pairings.append(([table[0]], party))
                        seatable_tables.remove(table[0])
                        seated = True
                        break
                size += 1

            # if we can't seat them at a single table, let's try at two
            while not seated and size > 0:
                size -= 1
                t_idx = -1
                while not seated and t_idx < len(table_sizes[size]) - 1:
                    t_idx += 1
                    table = table_sizes[size][t_idx]

                    # we are holding the table for some party
                    if self.tables_dict[table[0]][1] not in [-1, party[0]]:
                        continue

                    for neighbor in table[2]:
                        if neighbor in seatable_tables and table[0] in seatable_tables and \
                                (self.tables_dict[neighbor][0][0] + table[1] >= party[1]):
                            if neighbor in seatable_tables:
                                pairings.append(([table[0], neighbor], party))
                                seatable_tables.remove(neighbor)
                                seatable_tables.remove(table[0])
                                seated = True
                                break
                            # this needs to be something about holding tables
                            else:
                                pass
                                #self.party_to_tables[party[self.tables_dict[neighbor]

            # and lastly let's try moving three tables together
            # we can just try combinations of two neighbors, obviously

            size = self.largest_table
            while not seated and size > 0:
                size -= 1
                t_idx = -1
                while not seated and t_idx < len(table_sizes[size]) - 1:
                    t_idx += 1
                    table = table_sizes[size][t_idx]

                    # we are holding the table for some party
                    if self.tables_dict[table[0]][1] not in [-1, party[0]]:
                        continue

                    n_idx = -1
                    while not seated and n_idx < len(table[2]) - 1:
                        n_idx += 1
                        neighbor = table[2][n_idx]

                        for o_neighbor in table[2]:
                            if o_neighbor == neighbor:
                                continue

                            capacity = table[1]
                            capacity += self.tables_dict[neighbor][0][0]
                            capacity += self.tables_dict[o_neighbor][0][0]

                            if neighbor in seatable_tables and o_neighbor in seatable_tables and table[0] in seatable_tables and \
                                    capacity >= party[1]:

                                pairings.append(([table[0], neighbor, o_neighbor], party))
                                seatable_tables.remove(neighbor)
                                seatable_tables.remove(table[0])
                                seatable_tables.remove(o_neighbor)
                                seated = True
                                break
                            # this needs to be something about holding tables
                            else:
                                pass

            if seated:
                #clean up
                if party[0] in self.party_to_tables:
                    for t in self.party_to_tables[party[0]]:
                        self.tables_dict[t][1] = -1

                    del(self.party_to_tables[party[0]])

            i += 1

        return pairings
