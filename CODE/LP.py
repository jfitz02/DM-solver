class Tableu:           #tableu is the data structure used to solve a linear programming problem

    def __init__(self, grid, variables):    #grid is the initial tableu before any iterations have occurred
                                            #variables is an integer defining how many different variables their are                                          
        self.grid = grid
        self.iterations = 0
        self.results = []
        self.variables = variables
        self.answer = {}

    def generate_results(self):           #this function generates an array which holds the result
        for value in self.results:
            if value[1] == 0:
                self.answer["Cost"] = value[2]      #uses a dictionary to store the results as the values need to be identified to what they represent
            elif value[0]<=self.variables:
                self.answer["X{}".format(value[0])] = round(value[2],2)
            else:
                self.answer["S{}".format(value[0]-self.variables)] = round(value[2],2)


    def solve(self):        #this procedure performs iterations until the top row (objective row) hsa no negatives
        while min(self.grid[0])<0 and self.iterations < 25:     #an extra constraint of limiting the max iterations is also applied
                                                                #this is due to some problems have no answer (possibly because of an incorrect user input)
                                                                #if there were no caps on the amount of iterations then the program would just run forever
                                                                #also there is no problem in the AQA A level Further Mathematics spec that would require 25 or more
                                                                #iterations to solve.
            self.iteration()    #performs an iteration
            self.iterations += 1        #iteration count is incremented

        if self.iterations < 25:
            self.set_results()
            self.generate_results()

    def get_cols(self):         #returns the values in each column (as an array) this is done as knowing the values in the columns allows us to get the answers            
        cols = []
        for j in range(len(self.grid[0])):
            temp = []
            for i in range(len(self.grid)):
                temp.append(self.grid[i][j])
            cols.append(temp)

        return cols             #returns the values
    
    def set_results(self):      #sets the results to a variable self.results
        cols = self.get_cols()      #gets the columns

        for j, col in enumerate(cols):      #loops through the cols
            could_be_valued = True
            first = True
            for i, val in enumerate(col):   #loops through the col looking for more than 1 one or a value that isnt 1 or 0
                if val == 1:
                    if first:
                        row = i
                        first = False
                    else:
                        could_be_valued = False
                elif val != 0 and val!=1:   #if one of such is found then this column doesnt not have a value
                    could_be_valued = False

            if could_be_valued:         #if the column can be values the row in which the 1 is found is matched to the row in the value column of the tableu
                self.results.append((j, row, self.grid[row][-1]))


        self.results.sort()     #sorts the results in order of columns
        
    def iteration(self):        #defines what happens in an iteration
        usable_cols = [(i, pos) for pos, i in enumerate(self.grid[0]) if i<0]   #gets columns which have a negative coefficient in the objective row
        pivot_col = min(usable_cols)[1]     #pivot row is the row with the most negative coeeficient
        usable_rows = [(i[pivot_col], pos) for pos, i in enumerate(self.grid) if i[pivot_col]>0 and i!=0]   #if the pivot column in the row has a value less
                                                                                                            #than 0 it cant be used
        val_div_piv = [(self.grid[pos][-1]/self.grid[pos][pivot_col], pos) for i, pos in usable_rows]   #for each usable row the value is divided
                                                                                                        #by the pivot value
        pivot_row = min(val_div_piv)[1]         #the row index of the minimum val/piv value is used as the pivot row
        original_row = []               
        for val in self.grid[pivot_row]:
            original_row.append(val)        #creates a new array representing the original pivot row

        for i, val in enumerate(self.grid[pivot_row]):  #loops through the pivot row
            new_val = val/original_row[pivot_col]       #divides each value in the pivot row by the value in its pivot col
            self.grid[pivot_row][i] = new_val
        for i, row in enumerate(self.grid):     #loops through each row
            if row != self.grid[pivot_row]:     #checks to ensure the row isnt the pivot row
                multiplier = row[pivot_col]/original_row[pivot_col]    #calculates the multiplier needed to adjust each row correctly
                for j, val in enumerate(row):           #adjusts each value in the row
                    new_val = val-original_row[j]*multiplier
                    row[j] = new_val
                self.grid[i] = row

