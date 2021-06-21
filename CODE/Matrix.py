import sys          #Used to make the largest possible integer
import copy         #Used to deep copy so a 2D array is copied to a new memory location
                    #Rather than just referencing the original array.

class Matrix:           #class used to represent a distance matrix for graph problems

    def __init__(self, matrix):     #it is passed a 2d array which represents the values in the matrix
        self.matrix = matrix

    #1: from here until 2 creates a completed nearest distance matrix
    #Uses Djikstra's Algorithm to find minimum distances between nodes
    #As Djikstra's algorithm is not a part of the A-Level Further Mathematics Course
    #A version of it was copied from: https://www.geeksforgeeks.org/python-program-for-dijkstras-shortest-path-algorithm-greedy-algo-7/


    def complete_matrix(self):          #this function is public so other classes can use this funciton to create a complete nearest distance matrix
        matrix = [[0 for i in range(len(self.matrix))] for j in range(len(self.matrix))]    #creates an empty matrix

        for i in range(len(matrix)):        #loops through the rows of the empty matrix
            distances = self._djikstra_algorithm(i) #performs djikstras algorithm on the current row
            if type(distances) != type(False):      #if distances is a boolean False then return False
                for j in range(i, len(matrix)):     #otherwise loop through the current row
                    if distances[j] != 0:       #if the distance from row i to j does not = 0
                        matrix[i][j] = distances[j]
                        matrix[j][i] = distances[j]         #sets the values in the matrix to the nearest distance between the 2 nodes
                    else:   
                        matrix[i][i] = -1       #otherwise set the current row/column to -1
            else:
                return False

        return matrix

    def _minimum_distance(self, dist, sptSet):      #this function finds the minimum distance 
        minimum = sys.maxsize

        for v in range(len(self.matrix)):
            if dist[v] < minimum and sptSet[v] == False:
                minimum = dist[v]
                min_index = v
        try:
            return min_index
        except NameError as e:
            return False
    
    def _djikstra_algorithm(self, start):           #this funciton performs the djikstra algorithm
        distance = [sys.maxsize]*len(self.matrix)
        distance[start] = 0
        sptSet = [False]*len(self.matrix)

        for _ in range(len(self.matrix)):
            u = self._minimum_distance(distance, sptSet)
            if type(u) != type(False):
                sptSet[u] = True

                for v in range(len(self.matrix)):
                    if self.matrix[u][v] > 0 and sptSet[v] == False and distance[v] > distance[u] + self.matrix[u][v]: 
                        distance[v] = distance[u] + self.matrix[u][v]
            else:
                return False
        return distance

    #2: From here removes a node from the matrix

    def remove_row(self, c_row):            #takes a row number as an argument
        new_matrix = copy.deepcopy(self.matrix)     #deepcopies the matrix to ensure no overwriting occurs
        for row in new_matrix:      #pops the chosen row from each column of the matrix
            row.pop(c_row)
        new_matrix.pop(c_row)       #pops the row from the matrix
        return new_matrix           #returns the new matrix
