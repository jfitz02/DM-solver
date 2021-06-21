from tkinter import *               #tkinter is used for GUI
from tkinter import messagebox      #messagebox used for error boxes or for showing important information
from LP import Tableu               #personally made class used to solve the Linear Programming problem
import sqlite3 as sql               #Used to interact with database
import question_string as qs        #Used to transform the inputs to a uniquely identifiable string

def get_next_id(tablename, table_id, where=None):       #gets next available id from a specified table
    db = sql.connect("DM_database.db")
    c = db.cursor()
    if not where:
        c.execute('''SELECT MAX({}) FROM {}'''.format(table_id, tablename))
    else:
        c.execute('''SELECT MAX({}) FROM {} WHERE {}={}'''.format(tabled_id, tablename, where[0], where[1]))
    maximum = c.fetchall()
    db.commit()
    try:
        return(maximum[0][0]+1)
    except TypeError:
        return 0

class Lp_window:        #class which displays the GUI for the LP solver

    def __init__(self, master, user, solverid): #master is the tkinter root, user is the currently logged in user
                                                #solverid is the solverid for linear programming
        self.master = master
        self.master.title("Linear Programming Solver")
        self.user = user
        self.id = solverid

        self.variables = IntVar()
        self.constraints = IntVar()
        self.equality = StringVar()
        self.answers=None
        self.variables.set(3)
        self.constraints.set(3)     #initially set for number of variables and constraints to = 3

        self.make_inputs()
    def solve_problem(self):        #procedure which solves the problem
        self.get_inputs()

    def input_to_database(self, string):        #inputs the database string into the database
        db = sql.connect("DM_database.db")
        c = db.cursor()
        c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={}'''.format(self.user))
        question_ids = c.fetchall()
        new_question = True
        for question_id in question_ids:
            c.execute('''SELECT question FROM Questions WHERE QuestionID={}'''.format(question_id[0]))     #gets the question string of recently asked questions
            question = c.fetchall()[0][0]

            if question == string:
                new_question = False        #if the inputted question is the same as a recently asked question set new_question to False
        db.commit()

        if new_question:
            next_id = get_next_id("RecentQuestions", "UserQuestionID")

            db = sql.connect("DM_database.db")
            c = db.cursor()

            c.execute('''SELECT MAX(QuestionNumber) FROM RecentQuestions WHERE UserID={}'''.format(self.user))
            max_question = c.fetchall()[0][0]
            if not max_question:
                max_question = 0
            
            
            if max_question>=10:
                c.execute('''SELECT MIN(QuestionNumber) FROM RecentQuestions WHERE UserID={}'''.format(self.user))
                minimum_question = c.fetchall()[0][0]
                c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={} AND QuestionNumber={}'''.format(self.user, minimum_question))
                question_id = c.fetchall()[0][0]
                c.execute('''DELETE FROM RecentQuestions WHERE QuestionNumber={} and UserID={}'''.format(minimum_question, self.user))
                c.execute('''DELETE FROM Questions WHERE QuestionID={}'''.format(question_id))
                db.commit()

                
            db = sql.connect("DM_database.db")
            c = db.cursor()
            question_id = get_next_id("Questions", "QuestionID")
            c.execute('''INSERT INTO Questions(QuestionID, question) VALUES({},"{}")'''.format(question_id, string))
            c.execute('''INSERT INTO RecentQuestions(UserQuestionID, QuestionNumber, UserID, QuestionID) VALUES({},{},{},{})'''.format(next_id, max_question+1, self.user, question_id))
            db.commit()

    def get_inputs(self, answer=False):     #gets the question which has been inputted by the user
        cost_function = self.get_cost()     #gets the cost function inputted by the user
        constraints = self.get_constraints()        #gets the constraints
        constraints_list = []
        if cost_function != False and constraints != False: #if there are no errors in the user input
            for row in constraints:
                for val in row:
                    constraints_list.append(val)
            database_string = qs.generate_string("LP", constraints_list, cost_function, self.option_var.get())      #creates the database string from the inputs by the user

            
            tableu = []         #creates an array which will be passed into the Tableu class from the import LP
            tableu.append(cost_function)
            for constraint in constraints:
                tableu.append(constraint)

            try:        #try is used as if any errors occur the problem inputted by the user won't have a solution
                tableu = Tableu(tableu, self.variables.get())       #creates the tableu
                tableu.solve()          #solves the problem with the inputted tableu
                self.answers = tableu.answer        #gets the answers from the tableu
                keys = list(self.answers.keys())    #gets the keys in the answer
                answer_string = ""
                for key in keys:
                    answer_string += (key+" = "+str(self.answers[key])+"\n")    #creates the answer string which will be outputted to the user
                if answer == False:
                    self.input_to_database(database_string)     #if the user is not attempting to answer the question then the question is
                                                                #inputted into the databases
                    
                    self.answer.configure(text=answer_string)       #displays the answer
            except ValueError as e:
                self.answers = False
                messagebox.showinfo("Tk", "There is no solution to this problem")       #if an error occurs then there is no solution to the problem
                
            
        else:
            messagebox.showinfo("Tk", "All values must be Real numbers\nor\nYou have missed out a constant. If a constant is meant to be 0 please enter 0.") #if there are errors in the inputs it is displayed so

        

    def get_cost(self):     #gets the cost function from the users inputs
        cost = [1]      #the first value in the cost row of the tableu is always 1
        for i, val in enumerate(self.cost):
            new_val = val.get()
            try:
                new_val = float(new_val)
            except ValueError:
                return False
            if self.option_var.get() == "Maximise":
                new_val = -int(eval(self.cost_negative[i].get()+str(new_val)))
            else:
                new_val = int(eval(self.cost_negative[i].get()+str(new_val)))
            cost.append(new_val)
        for _ in range(self.constraints.get()+1):
            cost.append(0)                          #appends all values inputted as the cost function by the user correctly into the cost array

        return cost                 #returns the array

    def get_constraints(self):#gets the constraints from the users inputs
        constraints  = []
        for i, constraint in enumerate(self.constraint_list):   #loops through all constraints
            temp = [0]      #for each row of constraints the first value is always 0 in the tableu
            for j, val in enumerate(constraint):        #loops through each value in a constraint
                new_val = val.get()     #gets the values
                try:
                    new_val = float(new_val)        #tries turning it into a float
                except ValueError:
                    return False            #if theres an error then returns False
                if j == len(constraint)-1:
                    for k in range(self.constraints.get()):
                        if k == i:
                            temp.append(1)
                        else:
                            temp.append(0)              #appends the slack variables to the temp array
                if j < len(constraint)-1:
                    new_val = int(eval(self.negatives[i][j].get()+str(new_val)))
                if self.equalities[i].get() == ">=":
                    new_val *= -1               #adjusts values according to innequality
                temp.append(new_val)
            constraints.append(temp)        #creates the constraints array

        return constraints          #returns the array

        
                

    def refresh_window(self):       #destroys all widgets then redraws them
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.make_inputs()

        
    def make_inputs(self):      #makes the GUI for the solver window
        options = ["Minimise", "Maximise"]      #options for the problem to either maximise or minimise
        Label(self.master, text="Cost = ").grid(row = 2, column = 0)
        self.cost = []
        temp = StringVar()
        temp.set("+")
        self.cost_negative = [temp]
        OptionMenu(self.master, temp, *["+", "-"]).grid(row = 2, column = 1)
        for i in range(self.variables.get()):
            temp = StringVar()
            self.cost.append(temp)
            Entry(self.master, textvariable = temp).grid(row = 2, column = 2 + 3*i)
            Label(self.master, text="x{}".format(i+1)).grid(row = 2, column = 3 +3*i)
            if i != self.variables.get()-1:
                temp = StringVar()
                self.cost_negative.append(temp)
                temp.set("+")
                OptionMenu(self.master, temp, *["+", "-"]).grid(row = 2, column = 4 +(i*3))         #adds in the inputs for the cost function
        self.equalities = []    
        self.constraint_list = []
        self.negatives = []
        for i in range(self.constraints.get()):
            temp_equality = StringVar()
            self.equalities.append(temp_equality)
            temp_equality.set("<=")
            constraints = []
            temp = StringVar()
            temp.set("+")
            negatives = [temp]
            OptionMenu(self.master, temp, *["+", "-"]).grid(row = 3+i, column = 1)
            for j in range(self.variables.get()):
                temp = StringVar()
                constraints.append(temp)
                Entry(self.master, textvariable=temp).grid(row=3+i, column = 2 + j*3)
                Label(self.master, text = "x{}".format(j+1)).grid(row = 3+i, column = 3 + (j*3))
                if j!=self.variables.get()-1:
                    temp = StringVar()
                    negatives.append(temp)
                    temp.set("+")
                    OptionMenu(self.master, temp, *["+", "-"]).grid(row = 3+i, column = 4 +(j*3))           #adds in inputs for the constraints
            OptionMenu(self.master, temp_equality, *["<=", ">="]).grid(row = 3+i, column = (j*3)+5)
            temp = StringVar()
            constraints.append(temp)
            Entry(self.master, textvariable=temp).grid(row = 3+i, column = (j*3)+6)
            self.constraint_list.append(constraints)
            self.negatives.append(negatives)

        size = self.master.grid_size()
        self.option_var = StringVar()
        self.option_var.set("Minimise")     #dropwdown menu to decide whether to minimise or maximise
        Label(self.master, text="Linear Programming").grid(row = 0, column = size[0]//2)
        Label(self.master, text = "Variables:").grid(row=1, column = 0)
        OptionMenu(self.master, self.variables, *[i for i in range(1,10)]).grid(row = 1, column = 1)        #dropdown menu to set number of variables
        Label(self.master, text = "Constraints:").grid(row=1, column = (size[0]//2))
        OptionMenu(self.master, self.constraints, *[i for i in range(1,10)]).grid(row = 1, column = (size[0]//2)+1)
        OptionMenu(self.master, self.option_var, *options).grid(row=0, column = 0)                          #dropwdown menu to set number of constraints
        Button(self.master, text="update table", command=self.refresh_window).grid(row=1, column=size[0]-1)
        self.solve_button = Button(self.master, text="Solve", command=self.solve_problem)
        self.solve_button.grid(row=size[1], column=0, columnspan=size[0])               #solve button when pressed solves the problem
        self.answer = Label(self.master, text="")
        self.answer.grid(row=size[1]+1, column=0, columnspan=size[0])               #Label that will show the solution when the solve button is pressed

class Lp_answer(Lp_window):                 #subclass of Lp_window that is used when the user is testing their worked answer.
    def __init__(self, master, user, solverid):
        Lp_window.__init__(self, master, user, solverid)        #init method is not changed
        self.master.title("Linear Programming: Test Your Answers")

    def make_inputs(self):              #make inputs is changed slightly so that instead of a label being used to display the answer there are
                                        #Entry boxes for the user to input what they think the answer is
        Lp_window.make_inputs(self)
        self.solve_button.destroy()
        size=self.master.grid_size()
        answers = ["x{}".format(i+1) for i in range(self.variables.get())]
        for i in range(self.constraints.get()):
            answers.append("S{}".format(i+1))

        self.entered_answers = {}
        
        temp = StringVar()
        Label(self.master, text="Value: ").grid(row=size[1], column=(size[0]//2)-1)
        Entry(self.master, textvariable = temp).grid(row=size[1], column = size[0]//2)
        self.entered_answers["Cost"] = temp
        for i in range(self.constraints.get()+self.variables.get()):
            temp = StringVar()
            Label(self.master, text=answers[i]).grid(row=size[1]+i+2, column=(size[0]//2)-1)
            Entry(self.master, textvariable=temp).grid(row=size[1]+i+2, column=(size[0]//2))
            if i<self.variables.get():
                self.entered_answers["X{}".format(i+1)]=temp
            else:
                self.entered_answers["S{}".format(i+1-self.variables.get())]=temp

        size = self.master.grid_size()
        Button(self.master, text="Answer", command=self.test_answer).grid(row=size[1], column=0, columnspan=size[0])

    def test_answer(self):              #test answer tests the inputted answer against the actual solution worked out by the LP import
        self.get_inputs(answer = True)      #works out the actual answer

        if self.answers != False:
            
            keys = list(self.entered_answers.keys())        #gets the keys from the entered_answers dictionary

            self.answer_values = {}
            for key in keys:
                if float(self.entered_answers[key].get())!=0:
                    self.answer_values[key] = float(self.entered_answers[key].get())        #changes the stringvars into the float value that has been inputted
                                                                                            #by the user
            if self.answers == self.answer_values:      #if the ansers are correct
                self.process_correct()                  #performs the operations required for a correct answer
                
            else:                                       #otherwise
                self.change_success_rate(False)         #update success rate
                messagebox.showinfo("Tk", "Incorrect")  #show the answer was incorrect

    def change_success_rate(self, result):      #changes success rate dependant on whether they answered it correctly or not
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT Questions_answered, Correct_questions FROM SuccessRates WHERE UserID={} AND SolverID={}'''.format(self.user, self.id))#
        questions, correct = c.fetchall()[0]

        if result:          #if they answered it correctly
            correct += 1    #increment correct questions
        questions+=1 

        c.execute('''UPDATE SuccessRates SET Questions_answered={}, Correct_questions={} WHERE UserID={} AND SolverID={}'''.format(questions, correct, self.user, self.id))

        db.commit()
        

    def process_correct(self):      #process undertaken if the answer the user inputted was correct
        cost = self.get_cost()
        data = self.get_constraints()
        adjusted_data = []
        for row in data:
            for val in row:
                adjusted_data.append(val)
        database_string = qs.generate_string("LP", adjusted_data, cost=cost, max_min = self.option_var.get())     #generates the database string
        db = sql.connect("DM_database.db")
        c = db.cursor()
        c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={}'''.format(self.user))
        question_ids = c.fetchall()  

        new_question = True
        for question_id in question_ids:
            c.execute('''SELECT question FROM Questions WHERE QuestionID=?''',question_id)
            question = c.fetchall()[0][0]

            if question == database_string:
                new_question = False                        #checks whether the question the user has asked is a new question
        db.commit()

        if new_question:            #if it is a new question
            self.input_to_database(database_string)     #inputs the question into the database
            self.change_success_rate(True)              #increments success rate
            messagebox.showinfo("Tk","Correct")         #displays to the user they got the question correct
        else:
            messagebox.showinfo("Tk","This Question has already been checked so will not affect your success rate")
                                                                                #otherwise displays that the question has recently been asked
            



class Lp_algorithm:             #class which represents the GUI which shows the user the algorithm used to solve the LP problem
    def __init__(self, master):
        self.master = master
        self.master.title("Linear Programming Algorithm")
        self.img = PhotoImage(file="Simplex.PNG")           #loads image
        canvas = Canvas(self.master, width=self.img.width(), height=self.img.height())
        canvas.grid(row=1, column=1)
        canvas.create_image(0,0, anchor=NW, image=self.img)         #displays image



    
def create_window(master, user, solverid, solver=True):         #creates the desired window
    new_window = Toplevel(master)
    if solver:
        lp_window = Lp_window(new_window, user, solverid)
    else:
        lp_window = Lp_answer(new_window, user, solverid)
    new_window.mainloop()

def show_algorithm(master):
    new_window = Toplevel(master)
    lp_window = Lp_algorithm(new_window)
    new_window.mainloop()
