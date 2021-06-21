import sys                  #Used to make the largest possible integer
from Matrix import Matrix   #Personally made class representing the Matrix datatype

def all_pairs(lst):         #returns a permutation of all possible pairings of nodes
    if len(lst) < 2:
        yield []
        return
    if len(lst) % 2 == 1:
        for i in range(len(lst)):
            for result in all_pairs(lst[:i] + lst[i+1:]):
                yield result
    else:
        a = lst[0]
        for i in range(1,len(lst)):
            pair = (a,lst[i])
            for rest in all_pairs(lst[1:i]+lst[i+1:]):
                yield [pair] + rest
            
class RI(Matrix):       #route inspection class that solves the problem

    def __init__(self, matrix):
        Matrix.__init__(self, matrix)
        self.completed_matrix = self.complete_matrix()      #creates a completed matrix

    def solve(self):            #solves the problem and returns the distance
        odd_rows = self.get_odd_row_indexes()
        dist = self.min_distance(odd_rows)
        dist+=self.total_distance()

        return dist

    def get_odd_row_indexes(self):      #finds all nodes with an odd degree
        rows = []
        for index, row in enumerate(self.matrix):
            counter = 0
            for val in row:
                if val > 0:
                    counter += 1

            if counter%2 != 0:
                rows.append(index)

        return rows

    def total_distance(self):       #calculates the total distance of the graph (without added arcs)
        total = 0
        for row in self.matrix:
            for value in row:
                if value>0:
                    total+=value
        

        return int(total/2)

        
    def min_distance(self, rows):       #finds the minimum distance between all arrangements of pairs of nodes
        perms = list(all_pairs(rows))
        min_dist = sys.maxsize
        for perm in perms:
            dist = 0
            for pair in perm:
                dist += self.completed_matrix[pair[0]][pair[1]]
            if dist<min_dist:
                min_dist = dist

        return min_dist


