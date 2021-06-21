from tkinter import *               #tkinter is used for GUI
from tkinter import messagebox      #messagebox used for error boxes or for showing important information
from CPA import Network, Activity   #Personally made classes are used to solve the actual problem with given inputs
import sqlite3 as sql               #Used to interact with database
import question_string as qs        #Used to transform the inputs to a uniquely identifiable string

numbers = [i for i in range(20)]        #this is an array of availabel numbers for number of activities

def get_next_id(tablename, table_id, where=None):       #gets the next available id from a table and can be done to a condition
    db = sql.connect("DM_database.db")
    c = db.cursor()
    if not where:
        c.execute('''SELECT MAX({}) FROM {}'''.format(table_id, tablename))     #sql if there is no condition to be met
    else:
        c.execute('''SELECT MAX({}) FROM {} WHERE {}={}'''.format(tabled_id, tablename, where[0], where[1]))    #sql for if there is a condition to be met
    maximum = c.fetchall()
    db.commit()
    try:        #tries returning a maximum
        return(maximum[0][0]+1)
    except TypeError:
        return 0        #if an error occurs then there is no record in that table, so a 0 is the next available ID

class Cpa_window:   #class which represents the GUI for the CPA window.

    def __init__(self, master, user, solverid): #master is the tkinter root, user is the logged in user, solverid is the CPA's solverid
        self.master = master
        self.master.title("Critical Path Analysis Solver")
        self.user = user
        self.id = solverid

        self.NRows = IntVar()
        self.NRows.set(6)       #Integer variable used in the dropdown menu for selecting how many activities there are

        self.make_inputs()      #makes the GUI display
        self.append_labels()    #addition to the GUI

    def refresh_window(self):       #removes all widgets then redraws them
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.make_inputs()
        self.append_labels()

    def display_answer(self):       #changes all of the solve labels to show activity letter followed by the string returned from the solver class in CPA
        if self.answer != False:
            for i, result in enumerate(self.answer):
                string = "Earliest Start: "+str(result[0])+"  Duration: "+str(result[1])+"  Latest Finish: "+str(result[2])
                self.solve_labels[i].configure(text=chr(i+65)+" "+str(string))

    def input_to_database(self, string):        #inputs the unique question string into the database
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
            next_id = get_next_id("RecentQuestions", "UserQuestionID")      #gets next userquestion ID

            db = sql.connect("DM_database.db")
            c = db.cursor()

            c.execute('''SELECT MAX(QuestionNumber) FROM RecentQuestions WHERE UserID={}'''.format(self.user))      #gets the maximum question number for that user
            max_question = c.fetchall()[0][0]
            if not max_question:
                max_question = 0        #if there are no questions set max_question to 0
            
            if max_question >=10:       #if max_questionis greater than 10 then we need to delete the oldest question from the database
                c.execute('''SELECT MIN(QuestionNumber) FROM RecentQuestions WHERE UserID={}'''.format(self.user))
                minimum_question = c.fetchall()[0][0]
                c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={} AND QuestionNumber={}'''.format(self.user, minimum_question))
                question_id = c.fetchall()[0][0]
                c.execute('''DELETE FROM RecentQuestions WHERE QuestionNumber={} and UserID={}'''.format(minimum_question, self.user))
                c.execute('''DELETE FROM Questions WHERE QuestionID={}'''.format(question_id))
                db.commit()

            db = sql.connect("DM_database.db")
            c = db.cursor()
            question_id = get_next_id("Questions", "QuestionID")        #gets next questionID
            c.execute('''INSERT INTO Questions(QuestionID, question) VALUES({},"{}")'''.format(question_id, string))
            c.execute('''INSERT INTO RecentQuestions(UserQuestionID, QuestionNumber, UserID, QuestionID) VALUES({},{},{},{})'''.format(next_id, max_question+1, self.user, question_id))
                                                            #inserts question into Questions and RecentQuestions table
            db.commit()

    def make_database_string(self):     #makes database string
        string = ""
        for i in range(len(self.activities)):
            string += self.activities[i].get()
            string += self.durations[i].get()
            pre = self.predecessors[i].get().split(",")
            if pre[0] == "":
                string += "-"
            for j in pre:
                string += j    #creates a string of all the activities, durations and predecessors

        string = qs.generate_string("CPA", string)      #uses question string generator function from import question_string

        return string           #returns the string

    def get_inputs(self, answer=False):     #retrieves the inputs made by the user. called when the solve/answer button is pressed
                                            #answer refers to whether the question is being asked or whether an answer is being tested
        activities = []
        durations = []
        predecessors = []       #empty arrays to store the user inputs

        available_values = [val.get() for val in self.activities]
        valid = True
        for i in range(len(self.activities)):       #loops through the number of activities and appends the user inputs to the arrays
            activities.append(self.activities[i].get())
            try:
                durations.append(float(self.durations[i].get()))
            except ValueError:
                messagebox.showinfo("Invalid Entry", "Durations must be an integer or float")
                return
            pres = self.predecessors[i].get().split(",")
            for val in pres:
                
                if (val not in available_values) and val!="":
                    valid = False
            predecessors.append(self.predecessors[i].get().split(","))

        database_string = self.make_database_string()       #makes the database string to be saved into the database

        net = Network(activities, durations, predecessors)  #creates a CPA network using hte Network class from the CPA import
        net.forward_pass()
        net.backward_pass()     #solves the problem
        if answer == False and net.test_validity():
            self.input_to_database(database_string) #if answer = True then the user is not attempting to answer the question
                                                    #so the question string is stored into the database.
        if valid:  
            self.answer = net.output_network()      #the asnwer is retrieved from the network
        else:
            self.answer = True
            messagebox.showinfo("Invalid Entry", "You predecessor name must be one of the activities")
            
        if self.answer == False:
            messagebox.showinfo("Invalid Problem", "This problem can not be solved using this algorithm")
        else:
            self.display_answer()           #displays answer

    def append_labels(self):            #function adds labels that displays the answer
        size = self.master.grid_size()
        self.answer = Button(self.master, text="Solve", command=self.get_inputs)    #button which activates get_inputs to solve the problem inputted
        self.answer.grid(row=size[1], column=0, columnspan=size[0])
        
        self.solve_labels = []      #empty array to hold all of the labels which will display the answer
        for i in range(self.NRows.get()):
            temp = Label(self.master, text=chr(i+65)+": ")      #creates a Label temporarily assigns it to "temp"
            temp.grid(row=size[1]+1+i, column=0, columnspan=size[0])        #grids the label to the window
            self.solve_labels.append(temp)          #appends the Label to the solve_labels array

    def make_inputs(self):      #this procedure draws The GUI where the user inputs their question
        self.activities = []
        self.durations = []
        self.predecessors = []      #empty arrays which will store the StringVar's to be used when getting inputs

        Label(self.master, text="Critical Path Analysis").grid(row = 0, column = 1)
        Label(self.master, text = "Activity").grid(row=2, column=0)
        Label(self.master, text = "Duration").grid(row=2, column=1)
        Label(self.master, text = "Predecessors").grid(row=2, column=2)

        OptionMenu(self.master, self.NRows, *numbers).grid(row=1, column=0)
        Button(self.master, text="update table", command=self.refresh_window).grid(row=1, column=2)

        for i in range(self.NRows.get()):       #loops through the number of activities
            for j in range(3):
                output = StringVar()
                if j == 0:
                    output.set(chr(65+i))
                    self.activities.append(output)
                if j == 1:
                    self.durations.append(output)
                if j == 2:
                    self.predecessors.append(output)        #appends values to empty arrays defined at start of procedure
                input_box = Entry(self.master, textvariable = output, justify="center")
                input_box.grid(row = i+3, column = j)

            

class Cpa_solver(Cpa_window):       #This is a subclass of Cpa_window
                                    #has a very similar functionality however allows the user to enter their answer
                                    #they have worked out by hand to test whether they get it correct or not

    def __init__(self, master, user, solverid):
        Cpa_window.__init__(self, master, user, solverid)   #init method has no changes to the superclass
        self.master.title("Critical Path Analysis: Test your answers")

    def display_answer(self):       #this subclass will not display an answer so the function is overwritten to just pass
        pass

    def make_inputs(self):      #make_inputs class has no changes from the superclass
        Cpa_window.make_inputs(self)

    def refresh_window(self):       #clears all widgets then redraws them
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.make_inputs()
        self.append_labels()

    def get_guess(self):        #get guess retrieves the values entered by the user as their answer
        result = []
        for i, act in enumerate(self.earliest_starts):
            answer_string = (round(float(act.get()), 2), round(float(self.durations[i].get()), 2), round(float(self.latest_finishes[i].get()), 2))
                                #creates a string in the same form the answer will be saved as to test against to check whether the answer is correct
            result.append(answer_string)
        return result       #returns the inputted answer string
    
    def append_labels(self):        #altered from the superclass as the labels are no longer for displaying an answer
                                    #but instead for getting an input from the user as to what they think the answer is
        frame = Frame(self.master)
        self.earliest_starts = []
        self.latest_finishes = []       #arrays used to store the users answers
        Label(frame, text="Activity").grid(row=0, column=0)
        Label(frame, text="Earliest Start").grid(row=0, column=1)
        Label(frame, text="Latest Finish").grid(row=0, column=2)
        for i in range(self.NRows.get()):
            Label(frame, text=chr(i+65)+": ").grid(row=i+1, column=0)
            earliest_start = StringVar()
            latest_finish = StringVar()
            self.earliest_starts.append(earliest_start)
            self.latest_finishes.append(latest_finish)
            Entry(frame, textvariable=earliest_start).grid(row=i+1, column=1)
            Entry(frame, textvariable=latest_finish).grid(row=i+1, column=2)

        size = frame.grid_size()
        Button(frame, text="Answer", command=self.test_answer).grid(row=size[1], column = 0, columnspan=size[0])

        size = self.master.grid_size()
        frame.grid(row = size[1], column = 0,  columnspan=size[0])

    def change_success_rate(self, result):      #updates the success rate when a question has been attempted
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT Questions_answered, Correct_questions FROM SuccessRates WHERE UserID={} AND SolverID={}'''.format(self.user, self.id))#
        questions, correct = c.fetchall()[0]

        if result:          #if they answer it correctly the correct variable is increased by 1
            correct += 1
        questions+=1        #as a question has been answered the quesitons variable is always incremented 

        c.execute('''UPDATE SuccessRates SET Questions_answered={}, Correct_questions={} WHERE UserID={} AND SolverID={}'''.format(questions, correct, self.user, self.id))
                                                #updates the database with new Questions_answered and Correct_questions values
        db.commit()

    def process_correct(self):          #procedure which completes the actions necessary if a question is answered correctly
        database_string = self.make_database_string()

        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={}'''.format(self.user))
        question_ids = c.fetchall()         #retrieves all recently asked questions the user has made

        new_question = True                                                                 ####
        for question_id in question_ids:                                                       #
            c.execute('''SELECT question FROM Questions WHERE QuestionID=?''',question_id)     #
            question = c.fetchall()[0][0]                                                      ##Tests whether the question has been asked recently
                                                                                               ##Is done to ensure no cheating is used to increase a students
            if question == database_string:                                                    ##Success rate
                new_question = False                                                        ####
        db.commit()

        if new_question:                #if the question asked is a new question then
            self.input_to_database(database_string)     #it is inputted into the database
            self.change_success_rate(True)              #success rate is increased
            messagebox.showinfo("Tk","Correct")         #displays to the user that they got the question right
        else:
            messagebox.showinfo("Tk","This Question has already been checked so will not affect your success rate") #otherwise it is displayed that
                                                                                                                    #the question they inputted has recently
                                                                                                                    #been asked by them so their success rate
                                                                                                                    #won't be affected

    def test_answer(self):              #this function is called by the "Answer" Button in append_labels
        self.get_inputs(answer=True)    #solves the problem (passing answer=True so the program knows not to store the question into the database yet)

        guesses = self.get_guess()      #retrieves the attempt inputted by the user at answering the question

        if self.answer != True and self.answer != False:
            if guesses == self.answer:      #if their guess is equal to the answer
                self.process_correct()      #then process correct

            else:
                self.change_success_rate(False) #else update success rate passing False as the attempt was incorrect
                messagebox.showinfo("Tk", "Incorrect")      #display their attempt was incorrect

        
            

class Cpa_algorithm:            #this window simply displays a PNG of the algorithm which is used to solve
                                #the problem by hand
    def __init__(self, master):
        self.master = master
        self.master.title("Critical Path Analysis Algorithm")
        self.img = PhotoImage(file="Cpa.PNG")           #loads the image
        canvas = Canvas(self.master, width=self.img.width(), height=self.img.height())      #creates a canvas to display the image
        canvas.grid(row=0, column=0)                    #grids the canvas onto the window
        canvas.create_image(0,0, anchor=NW, image=self.img)         #draws the image onto the canvas



def create_window(master, user, solverid, solver=True): #creates new frame for new window
    new_window = Toplevel(master)
    if solver:              #if the solver button on the main menu is clicked then the Cpa_window is run
        cpa_window = Cpa_window(new_window, user, solverid)
    else:
        cpa_window = Cpa_solver(new_window, user, solverid) #else the solver window is run
    new_window.mainloop()

def show_algorithm(master):         #this function is called if the algorithm button is pressed
    new_window = Toplevel(master)
    cpa_window = Cpa_algorithm(new_window)
    new_window.mainloop()
