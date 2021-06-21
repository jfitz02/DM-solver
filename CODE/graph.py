from tkinter import *           #tkinter is used for GUI
from functools import partial   #used for TKinter buttons as the commands called can't take parameters without partial
import question_string as qs    #Used to transform the inputs to a uniquely identifiable string
import sqlite3 as sql           #Used to interact with database



def get_next_id(tablename, table_id, where=None):
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

###THIS CLASS ACTS AS A SUPERCLASS TO ALL GUIS REPRESENTING A GRAPH DATASTRUCTURE###


class Window:   

    def __init__(self, master, user, solverid, starting_node=None): #master is the tkinter root
                                                                    #user is the user accessing the solver
                                                                    #solverid is the current solver being used
                                                                    #starting node is only used in the TSP hence it is set to None
                                                                    #but it represent the node of which the algorithm should start
        self.master = master

        self.user = user
        self.id = solverid

        if starting_node != None:
            self.starting_node = starting_node
        
        self.nodes = IntVar()           
        self.nodes.set(5)               #used in a dropdown menu to change the number of nodes in the graph
        
        self.refresh_window()           #refreshes the window

    def refresh_window(self):           #deletes all widgets then redraws them using self.make_inputs()
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.make_inputs()
        
    def get_inputs(self, answer = False):       #the answer bool is used to determine whether the question is being checked as an answer (user in "Test Answer" section)
                                                #or if the question is just being asked for an answer (User in solver section)

        try:
            output = []         #empty array which will hold all the values inputted by the user
            for i, row in enumerate(self.matrix):       #loops through the rows of entry boxes in the graph grid
                temp = []                               #temp used to store information on the current row being iterated through
                for j,val in enumerate(row):            #loops through the entry boxes on the current row
                    value = val.get()                   #retrieves the values from the entry box
                    self.matrix[j][i].set(value)        #sets the values diagonally opposite to the same value
                    if value == "":
                        value = -1                      #if there is nothing in the box then the value is set to 0
                    temp.append(int(value))             #appends value to temp

                output.append(temp)         #appends temp to the output
            self.solve_problem(output, answer=answer)       #calls the solver problem function and passes the output ans that answer=answer
        except ValueError:
            messagebox.showinfo("Invalid entry", "Integers must be inputted not characters")
        except UnboundLocalError:
            messagebox.showinfo("Invalid Entry", "The graph you have inputted can not be answered using this algorithm")

    def solve_problem(self, output, answer=False):  #in the superclass solve_problem just passes as each subclass will use this function differently (Overwrite)
                                                    #the graph class on its own has no use for this function so nothing needs to be done in this function currently

        pass

    def process_correct(self, qtype, data):                  #this function is run if the user answers a question correctly
        database_string = qs.generate_string(qtype, data)   #makes the unique string that will be stored in the database

        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={}'''.format(self.user))
        question_ids = c.fetchall()             #gets all recent questions which the user has asked

        new_question = True                     #assumes the question is new until shown otherwise
        for question_id in question_ids:
            c.execute('''SELECT question FROM Questions WHERE QuestionID={}'''.format(question_id[0]))     #gets the question string of recently asked questions
            question = c.fetchall()[0][0]

            if question == database_string:
                new_question = False        #if the inputted question is the same as a recently asked question set new_question to False
        db.commit()

        if new_question:                    #if it is a new question input that question to the database and increment success rate
            self.input_to_database(database_string)
            self.change_success_rate(True)
            messagebox.showinfo("Tk","Correct")
        else:
            messagebox.showinfo("Tk","This Question has already been checked so will not affect your success rate") #otherwise display that the user has recently checked that question
                                                                                                                    #so success rate will not be increased

    def input_to_database(self, string):            #inputs question inputted to the database. string is the question string representing the question answered
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
            db.commit()
            next_id = get_next_id("RecentQuestions", "UserQuestionID")      #gets the next userquestionID available

            db = sql.connect("DM_database.db")
            c = db.cursor()

            c.execute('''SELECT MAX(QuestionNumber) FROM RecentQuestions WHERE UserID={}'''.format(self.user))      #gets the highest question number of the user answering a question
            max_question = c.fetchall()[0][0]
            if not max_question:        #if thers is no max_question then set it ot 0
                max_question = 0
            
            if max_question >=10:       #if max_question is greater than 10 then the oldest recent question must be removed from the database
                                        #everything inside this if statement is used to delete the oldest question
                c.execute('''SELECT MIN(QuestionNumber) FROM RecentQuestions WHERE UserID={}'''.format(self.user))
                minimum_question = c.fetchall()[0][0]
                c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={} AND QuestionNumber={}'''.format(self.user, minimum_question))
                question_id = c.fetchall()[0][0]
                c.execute('''DELETE FROM RecentQuestions WHERE QuestionNumber={} and UserID={}'''.format(minimum_question, self.user))
                c.execute('''DELETE FROM Questions WHERE QuestionID={}'''.format(question_id))
                db.commit()

            db = sql.connect("DM_database.db")
            c = db.cursor()
            question_id = get_next_id("Questions", "QuestionID")            #gets the next available quesitonID
            c.execute('''INSERT INTO Questions(QuestionID, question) VALUES({},"{}")'''.format(question_id, string))        #inserts new question into database
            c.execute('''INSERT INTO RecentQuestions(UserQuestionID, QuestionNumber, UserID, QuestionID) VALUES({},{},{},{})'''.format(next_id, max_question+1, self.user, question_id))
                                                                                                #inserts new question as a recent question
            db.commit()

    def change_success_rate(self, result):          #changes the success rate after a question has been attempted
                                                    #result is a boolean showing whether the question was answered corectly
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT Questions_answered, Correct_questions FROM SuccessRates WHERE UserID={} AND SolverID={}'''.format(self.user, self.id))
        questions, correct = c.fetchall()[0]                                                #retrieves data on the users success rate on the solver being used

        if result:          #if the user answered the question correctly
            correct += 1    #increment correct value
        questions+=1        #alwasy increment questions value

        c.execute('''UPDATE SuccessRates SET Questions_answered={}, Correct_questions={} WHERE UserID={} AND SolverID={}'''.format(questions, correct, self.user, self.id))
                                                                #update database with new questions answered and correct questions
        db.commit()

    def make_inputs(self):              #makes the GUI used for this solver, is overwritten in subclasses to make the GUI more solver specific

        for i in range(self.nodes.get()):
            Label(self.master, text = "{}".format(chr(i+65))).grid(row = 2, column = i+1)
            Label(self.master, text = "{}".format(chr(i+65))).grid(row = i+3, column = 0)

        self.matrix = []
        for i in range(self.nodes.get()):
            row = []
            for j in range(self.nodes.get()):
                temp = StringVar()
                row.append(temp)
                if j > i:
                    Entry(self.master, textvariable = temp, background="white").grid(row = i+3, column = j + 1)
                else:
                    Entry(self.master, textvariable = temp, state = DISABLED, disabledbackground="grey").grid(row = i+3, column = j + 1)
            self.matrix.append(row)
            
        size = self.master.grid_size()
        self.title = Label(self.master, text = "")
        self.title.grid(row=0, columnspan = size[1], column = 0)
        Label(self.master, text = "Nodes").grid(row = 1, column = 0)
        OptionMenu(self.master, self.nodes, *[i+2 for i in range(10)]).grid(row = 1, column = 1)
        Button(self.master, text = "update table", command=self.refresh_window).grid(row = 1, column = size[0]-1)
        self.solve_button = Button(self.master, text = "solve", command=self.get_inputs)
        self.solve_button.grid(row = size[1], column = (size[0]//2))
