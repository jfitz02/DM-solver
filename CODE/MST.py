from Matrix import Matrix   #Personally made class representing the Matrix datatype

class MST(Matrix):      #subclass of matrix which performs the operations to solve
                        #the Minimum Spanning Tree problem

    def __init__(self, matrix):     #matrix is the 2d array passed into the class
        Matrix.__init__(self, matrix)   #initialises the Matrix superclass
        self.rows_got = [0]     #array of rows that have been chosen
        self.size = 0       #size of the MST

    def __str__(self):      #When the string of this class is asked for it will return the MST size
                            #rather than the object itself
        return str(self.size)

    def _iteration(self):        #an iteration will solve 1 row
        for i in self.rows_got:     #loops through the already solved rows
            row = self.matrix[i]        #gets the values in that row
            values = [(num,pos) for pos, num in enumerate(row) if num>0 and pos not in self.rows_got]   #gets all values in the row array that aren't 0
                                                                                                        #and aren't already solved
            if values:          #if there are values which are true for the above conditions
                next_value = min(values, key = lambda t: t[0])  #minimum value based off of the 1st value in each tuple
                try:            #try used to catch whether min_value has been assigned already
                    if next_value[0] < min_value[0]:        #if the next value is less than the minimum value
                        min_value = next_value          #change the minimum value

                except NameError:
                    min_value = next_value      #if there is no min_value variable then create it and set it to next_value

        new_pos = min_value[1]      #new position is the position of the min_value
        self.rows_got.append(new_pos)       #append this new_position to rows_got
        self.size += min_value[0]       #change the size according to the value in min_value[0]

    def solve(self):        #solve is a public class that can be accessed by other classes to solve the problem
        while len(self.rows_got) < len(self.matrix):
            self._iteration()


