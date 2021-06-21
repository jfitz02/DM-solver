import sys                  #Used to make the largest possible integer
from Matrix import Matrix   #Personally made class representing the Matrix datatype
from MST import MST         #Used to find a minimum spanning tree of a subgraph (To solve Lower bound)

class TSP(Matrix):

    def __init__(self, matrix):
        Matrix.__init__(self, matrix)
        self.matrix = self.complete_matrix()
        self.upper = sys.maxsize
        self.lower = 0

    
    def lower_bound(self, node):        #algorithm to find the lower bound of the problem
        node = ord(node)-65         
        values = [i for i in self.matrix[node] if i!=-1]    #takes the row of the starting node gets all values
        values.sort()
        p = values[0]
        q = values[1]       #finds the 2 smallest values in the values array
        new_matrix = self.remove_row(node)      #creates a new matrix removing the node "node"
        net = MST(new_matrix)       
        net.solve() #solves the MST of the new matrix

        return p + q + int(str(net))        #returns weights of new MST  + p + q

    def upper_bound(self, node):        #algorithm to find the upper bound of the problem
        node = ord(node)-65
        start = node
        weight = 0      #initialises the current node, start node and weight
        unvisited_nodes = [i for i in range(len(self.matrix))]      #finds all unvisited nodes
        while len(unvisited_nodes)!=0:      #while there are unvisited nodes
            if len(unvisited_nodes) > 2:    #if there are more than 2 nodes left to visit
                unvisited_nodes.remove(node)        #remove the node we are at from unvisited nodes
                adjacent_nodes = [(val, i) for i, val in enumerate(self.matrix[node]) if val>0 and i in unvisited_nodes]    #find adjacent nodes
                next_node = min(adjacent_nodes)[1]      #locate next node
                weight += min(adjacent_nodes)[0]        #add weight of arc to next node to weight
                node = next_node            #set the node to be the next node
            else:
                unvisited_nodes.remove(node)        #remove the current node
                weight += self.matrix[node][unvisited_nodes[0]] #weight += distance to the last unvisited node
                node = unvisited_nodes[0]
                unvisited_nodes.remove(unvisited_nodes[0])
                weight += self.matrix[node][start]      #adds weight to get back to start
        return weight       #returns the weight
            
