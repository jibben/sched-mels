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
        for party in to_seat:
            for table in tables:
                if table[1] >= party[1] and table[0] not in tables_used:
                    pairings.append(([table[0]], party))
                    tables_used.add(table[0])
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
                        table[1] <= party[1] + 1 and \
                        table[0] not in tables_used:
                    pairings.append(([table[0]], party))
                    tables_used.add(table[0])
                    break

        return pairings


class RoundRobin(SeatingAlgorithm):

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
                        section[1] += 1
                        self.sections.sort(key = lambda x : x[1])
                        break
                s_pos += 1

        return pairings
