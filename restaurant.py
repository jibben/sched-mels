import heapq

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
                "Cannot seat party of size {} at tables {}".format(party[1], tids)

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
