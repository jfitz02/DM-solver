from tkinter import *               #tkinter is used for GUI
from tkinter import messagebox      #messagebox used for error boxes or for showing important information
from functools import partial       #used for TKinter buttons as the commands called can't take parameters without partial
import sqlite3 as sql               #Used to interact with database
import string                       #Used to generate a list of all characters and digits
import password_hasher as ph        #Used to Hash passwords and create salts
import random                       #used to generate random passwords
from password_decorator import password_decorator as pd

###PLEASE NOTE "class" = A class in a school
###            class = A class used in the oop programming paradigm
        

def get_class(chosen):          #function used to retrieve "class" name
    db = sql.connect("DM_database.db")
    c = db.cursor()
    c.execute('''SELECT UserID, Username FROM Users WHERE Class_name="{}"'''.format(chosen))
    class_data = c.fetchall()
    db.commit()
    
    
    return class_data

def get_next_id(tablename, table_id):           #function used to retrieve the next available ID for a certain table
        db = sql.connect("DM_database.db")
        c = db.cursor()                     #connects to database

        c.execute('''SELECT MAX({}) FROM {}'''.format(table_id, tablename))         #gets maximum id
        maximum = c.fetchall()
        db.commit()
        try:
            return(maximum[0][0]+1)         #returns +1 of the maximum for next ID
        except TypeError:
            return 0                        #if an error occurs then there is nothing currently in the table
                                            #so 0 is returned as the initial ID

class AdminMainMenu:                   #First window used for an Admin to select which "class" they want to view or create a class

    def __init__(self, master, admin):  #master is the Tkinter root and admin is the AdminID of the admin logged in
        self.master = master
        self.frame = Frame(master)
        self.master.title("Admin Menu")
        self.admin_id = admin
        self.selected_class = StringVar()
        self.selected_class.set("Please select a class")        #intialises the drop down menu to be set to "Please select a class"
        db = sql.connect("DM_database.db")
        c = db.cursor()
        c.execute('''SELECT Username FROM Admin WHERE AdminID={}'''.format(self.admin_id))
        self.admin = c.fetchall()[0][0]         #gets admin name to display.
        self.draw_window()
        

    def get_classes(self):          #function returns all "classes" of which the logged in Admin has control over
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute("SELECT Class_name FROM Classes WHERE AdminID={}".format(self.admin_id))
        classes = c.fetchall()
        db.commit()
        classes = [i for i in classes]

        return classes

    def refresh_window(self):                   #removes all widgets and redraws them. Is used when changes are made to update the window
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.draw_window()

    def draw_window(self):                      #draws the GUI components to the window
        self.classes = self.get_classes()
        Label(self.master, text = "Hello {}".format(self.admin)).grid(row = 0, column = 0, padx = 50, pady=20)
        try:                #If there are no "classes" then an error will raise tripping the except state
            OptionMenu(self.master, self.selected_class, *self.classes).grid(row=1, column=0)
            Button(self.master, text="open class", command = self.open_class).grid(row=2, column=0) #Button to open a "class". Links to ViewClassWindow
        except:         #if except state is tripped then nothing happens so the Admin can not does not have the option to open a "class"
                        #as they do not have a "class" to open
            pass
        Button(self.master, text="Create Admin", command = self.create_admin).grid(row=3, column=0, pady=20)
        Button(self.master, text="create class", command = self.create_class).grid(row=4, column =0)   #Button to create a "class". Links to CreateClassWindow

    def create_class(self):         #opens new window (CreateClassWindow) which is used to create a new "class"
        newlevel = Toplevel(self.master)
        win = CreateClassWindow(newlevel, self)

    def create_admin(self):
        newlevel = Toplevel(self.master)
        win = AdminCreationScreen(newlevel, self)
        

    def open_class(self):           #opens a "class" in a new window to be able to review and make changes to the "class"
        if self.selected_class.get() != "Please select a class":        #tests to see if the admin has selected a "class"
            newlevel = Toplevel(self.master)
            win = ViewClassWindow(newlevel, self.selected_class.get()[2:-3])


class CreateClassWindow:              #class which is used to create the GUI for creating a new "class"

    def __init__(self,master, main):        #master is the Tkinter root, main is the previous Window object
        self.master = master
        self.admin = main.admin_id          #gets the Admin ID from the previous object
        self.frame = Frame(self.master)
        self.master.title("New Class")
        self.main = main
        self.draw_window()
        
    def insert_into_database(self, classname):         #Inserts the new "class" into the database
        if len(classname.get()) != 0:
            db = sql.connect("DM_database.db")
            c = db.cursor()

            max_solver_id = get_next_id("AvailableSolvers", "UserSolverID")     #gets the next available UserSolverID (used to link classes to their available solvers)
            classname = classname.get()      #gets the inputted "class" name
            if self.test_uniqueness(classname):    #tests whether that "class" exsists
                c.execute('''INSERT INTO Classes(Class_name, AdminID) VALUES("{}",{})'''.format(classname, self.admin))
                for i in range(max_solver_id, max_solver_id+5):
                    c.execute('''INSERT INTO AvailableSolvers(UserSolverID, Access, SolverID, Class_name) VALUES({}, 1, {}, "{}")'''.format(i, i-max_solver_id, classname))
                                                #inputs all necessary data that is required for that "class"
                                                #including its name, admin and its available solvers
            else:
                messagebox.showinfo("Tk", "This class already exists")      #if the "class" does exist then this message is displayed.
            db.commit()
            self.main.refresh_window()      #refreshes the main window (the object passed as an object to this class)
            self.master.destroy()           #destroys this window
        else:
            messagebox.showinfo("Invalid Class name", "A Class Name must not be an empty string")
        
    def draw_window(self):              #draws the GUI
        classname = StringVar()
        Label(self.master, text="Class Name: ").grid(row=0, column=0)
        Entry(self.master, textvariable=classname).grid(row=0, column=1)
        Button(self.master, text="save", command=partial(self.insert_into_database, classname)).grid(row=1, column=0, pady=20, padx=20, columnspan=2)

    def test_uniqueness(self, classname):  
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT Class_name FROM Classes WHERE Class_name="{}"'''.format(classname))    #retrieves all classes with the same Class_name

        if len(c.fetchall()) == 0:          #if their is no classes with that name
            return True                     #return True
        else:                               #else
            return False                    #return False
        

class ViewClassWindow:          #class which is used to create the GUI for viewing a "class"

    Solvers = ["Minimum Spanning Tree", "Critical Path Analysis", "Linear Programming", "Route Inspection", "Travelling Salesman Problem"]  #solvers that are available in this program

    def __init__(self, master, chosen_class):   #master is the Tkinter root and chosen_class is the class which was selected in the
                                                #dropdown box in the previos window
        self.master = master
        self.frame = Frame(self.master)
        self.master.title(chosen_class)
        self.chosen_class = chosen_class
        self.draw_window()

    def refresh_window(self):               #removes all widgets and redraws them. Is used when changes are made to update the window
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.draw_window()

    def draw_window(self):                  #draws the GUI
        self.data = get_class(self.chosen_class)
        Label(self.master, text=self.chosen_class).grid(row=0, column=2)
        Label(self.master, text="Student ID",).grid(row=1, column=0, pady=10)
        Label(self.master, text="Name").grid(row=1, column=1)
        Label(self.master, text="Success Rate").grid(row=1, column=2)           #Titles for the columns to represent what is shown beneath them
        for i, student in enumerate(self.data):                                 #iterates through each student to show display them
            Label(self.master, text=student[0]).grid(row=i+2, column=0)
            Label(self.master, text=student[1]).grid(row=i+2, column=1)
            Button(self.master, text="Open", command=partial(self.open_success_window, student)).grid(row=i+2, column=2)    #button to open the students success rates
            Button(self.master, text="Delete Student", command=partial(self.delete_student, student)).grid(row=i+2, column=3)   #button to delete student

        Label(self.master, text="Avaiblable Solvers").grid(row=0, column=4)     #Title to show which solvers are available
        self.variables = [IntVar() for _ in range(5)]       #IntVar used to store the value 1 or 0 to determine whether the solver is avaibale or not

        locked_solvers = self.get_solver_data()             #gets data for which solvers are available
        
        for i, variable in enumerate(self.variables):       #loops throw the IntVar's in self.variables to set each to 1 or 0 depending whether they're available or not
            variable.set(locked_solvers[i][0])
        for i, solver in enumerate(self.Solvers):
            Checkbutton(self.master, text=solver, var= self.variables[i]).grid(row=i+1, column=4, padx=20, sticky=W)        #displays the check box button for each solver

        size = self.master.grid_size()
        Button(self.master, text="Add Student", command=self.open_usercreate_screen).grid(row=size[1]+1, column=size[0]//2) #button to add a student
        Button(self.master, text="save", command=self.save).grid(row=size[1]+2, column=size[0]//2)                          #button to save changes

    def save(self):         #saves changes when the "save" button is pressed in the draw_window() procedure
        db = sql.connect("DM_database.db")
        c = db.cursor()
        
        for i, var in enumerate(self.variables):    #loops through the solvers
            solver_id = i
            locked = var.get()                      #retrieves whether the solver is available or not determined by the check boxes
            c.execute('''UPDATE AvailableSolvers SET Access={} WHERE SolverID={} AND Class_name="{}"'''.format(locked, solver_id, self.chosen_class))   #inputs data into database
        db.commit()

    def get_solver_data(self):              #gets whether solvers are available or not
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT Access FROM AvailableSolvers WHERE Class_name="{}"'''.format(self.chosen_class))

        access = c.fetchall()

        return access

    def open_success_window(self, student):     #opens window to display a students success rate
        newLevel = Toplevel(self.master)
        win = SuccessRateViewer(newLevel, student)

    def open_usercreate_screen(self):           #opens window to create a new student
        newLevel = Toplevel(self.master)
        win = UserCreationScreen(newLevel, self)
        
    def delete_student(self, student):          #procedure to delete a student
        sure = messagebox.askquestion("Delete Student", "are you sure you want to delete {}".format(student[1]))
        if sure == "yes":
            db = sql.connect("DM_database.db")
            c = db.cursor()

            c.execute('''DELETE FROM Users WHERE UserID = {}'''.format(student[0]))     #deletes the User FROM the Users table
            c.execute('''DELETE FROM SuccessRates WHERE UserID={}'''.format(student[0]))    #deletes the Users success rates
            c.execute('''SELECT QuestionID FROM RecentQuestions WHERE UserID={}'''.format(student[0]))      #selects all of the questionID's in the users recent questions
            question_id = c.fetchall()

            for question in question_id:
                c.execute('''DELETE FROM Questions WHERE QuestionID={}'''.format(question[0]))     #deletes all recent questions that user has asked from the Questions table
            c.execute('''DELETE FROM RecentQuestions WHERE UserID={}'''.format(student[0]))     #deletes all recent questions that user has asked from the RecentQuestions table
            db.commit()
            self.refresh_window()                   #refreshes window
        

class AdminCreationScreen:          #screen used to create an admin

    def __init__(self,master, main):
        self.master = master
        self.frame = Frame(self.master)
        self.master.title("Create User")
        self.main = main
        self.draw_window()
        
    @pd
    def insert_into_database(self, password, username):     #inserts admin into database
        db = sql.connect("DM_database.db")
        c = db.cursor()
        c.execute('''SELECT UserID FROM Users WHERE Username = "{}"'''.format(username.get()))
        users = c.fetchall()
        c.execute('''SELECT AdminID FROM Admin WHERE Username = "{}"'''.format(username.get()))
        admins = c.fetchall()
        db.commit()

        if len(username.get()) != 0:

            if len(users) == 0 and len(admins) == 0:        #if the length of either of these strings != 0 then an account with that username already exists
                salt = ph.generate_salt()                           #generates salt which is appended to the password before hashing for extra security
                hashed_password = ph.hash_password(salt, password.get())      #hashes the password salt combination

                next_solver_id = get_next_id("SuccessRates","UserSuccessID")        #retrieves the next UserSuccessID from SuccessRates. This will be used for this user
                db = sql.connect("DM_database.db")
                c = db.cursor()
                c.execute('''INSERT INTO Admin(AdminID, Username, Password, Salt) VALUES({},"{}","{}","{}")'''.format(self.next_admin_id, username.get(), hashed_password, salt))
                                            #Inserts the User along with their information into the User table. As they have not actually logged on yet First is set to 1.
                messagebox.showinfo("Admin Created", "Admin Created")
                db.commit()
                self.master.destroy()                   #destroys the current window
            else:
                messagebox.showinfo("Account Creation Error", "User with that Username already exists")     #if an account with the inputted username already exists then this message
                                                                                        #is displayed to the user
        else:
            messagebox.showinfo("Invalid Username", "A Username can not be an empty String")

    def draw_window(self):          #draws the window. Which consists of 2 entries and a button to enter the credentials
        self.next_admin_id = get_next_id("Admin", "AdminID")
        username = StringVar()
        password = StringVar()
        
        Label(self.master, text="Create New Admin").grid(row=0, column=0, pady=10, padx=5)
        Label(self.master, text="Admin ID: {}".format(self.next_admin_id)).grid(row=2, column=0, pady=10, padx=5)
        Label(self.master, text="New Username").grid(row=3, column=0, pady=10, padx=5)
        Entry(self.master, textvariable=username).grid(row=3, column=1, pady=10, padx=5)
        Label(self.master, text="New Password").grid(row=4, column=0, pady=10, padx=5)
        Entry(self.master, textvariable=password, show="*").grid(row=4, column=1, pady=10, padx=5)
        Button(self.master, text="Enter", command=partial(self.insert_into_database, password, username)).grid(row=5, column=0, pady=10, padx=5)     #inserts the data into the database

        

class UserCreationScreen:           #class used to add a new student to the "class"

    def __init__(self, master, main):     #master is the Tkinter root, chosen_class is the class in which the student is going to be in
                                                        #main is the previous window object
        self.chosen_class = main.chosen_class
        self.master = master
        self.frame = Frame(self.master)
        self.master.title("Create User")
        self.main = main
        self.draw_window()

    def insert_into_database(self, username):         #procedure used to input new student into the database
        if len(username.get()) != 0:
            db = sql.connect("DM_database.db")
            c = db.cursor()
            c.execute('''SELECT UserID FROM Users WHERE Username = "{}"'''.format(username.get()))
            users = c.fetchall()
            c.execute('''SELECT AdminID FROM Admin WHERE Username = "{}"'''.format(username.get()))
            admins = c.fetchall()
            db.commit()

            if len(users) == 0 and len(admins) == 0:        #if the length of either of these strings != 0 then an account with that username already exists
                letters = string.ascii_letters+string.digits    #creates a string of all available characters for the temporary password
                password = ''.join([random.choice(letters) for i in range(10)])     #creates the temporary passwoed
                salt = ph.generate_salt()                           #generates salt which is appended to the password before hashing for extra security
                hashed_password = ph.hash_password(salt, password)      #hashes the password salt combination

                next_solver_id = get_next_id("SuccessRates","UserSuccessID")        #retrieves the next UserSuccessID from SuccessRates. This will be used for this user
                db = sql.connect("DM_database.db")
                c = db.cursor()
                c.execute('''INSERT INTO Users(UserID, Username, Password, Salt, First, Class_name) VALUES({},"{}","{}","{}",1,"{}")'''.format(self.next_user_id, username.get(), hashed_password, salt, self.chosen_class))
                                            #Inserts the User along with their information into the User table. As they have not actually logged on yet First is set to 1.
                for i in range(next_solver_id, next_solver_id+5):
                    c.execute('''INSERT INTO SuccessRates(UserSuccessID, Questions_answered, Correct_questions, UserID, SolverID)
                                    VALUES({},0,0,{},{})'''.format(i, self.next_user_id, i-next_solver_id))     #loops through all solvers available setting their intial Questions answered
                                                                                                                #and correct questions to 0
                db.commit()
                messagebox.showinfo("tk", "Password: {}".format(password))      #displays the Users temporary password
                self.master.destroy()                   #destroys the current window
                self.main.refresh_window()              #updates the previous window object passed into this class
            else:
                messagebox.showinfo("Tk", "User with that Username already exists")     #if an account with the inputted username already exists then this message
                                                                                        #is displayed to the user
        else:
            messagebox.showinfo("Invalid Username", "A Username can not be an empty String")
    def draw_window(self):          #draws the GUI for this window

        self.next_user_id = get_next_id("Users", "UserID")
        username = StringVar()
        
        Label(self.master, text="Create New User").grid(row=0, column=0, pady=10, padx=5)
        Label(self.master, text="User ID: {}".format(self.next_user_id)).grid(row=2, column=0, pady=10, padx=5)
        Label(self.master, text="New Username").grid(row=3, column=0, pady=10, padx=5)
        Entry(self.master, textvariable=username).grid(row=4, column=0, pady=10, padx=5)
        Button(self.master, text="Enter", command=partial(self.insert_into_database, username)).grid(row=5, column=0, pady=10, padx=5)     #inserts the data into the database


class SuccessRateViewer:            #class used to view the success rates of a user

    def __init__(self, master, user):           #master is the tkinter root, user is a tuple containing the username and userID of the user.
        self.master = master
        self.frame = Frame(self.master)
        self.master.title(user[1]+"'s Success rates")
        self.user = user
        self.solver_success = self.get_user_data()      #gets data on the users questions_answered and correct_questions
        self.draw_window()

    def get_user_data(self):
        user_id = self.user[0]          #gets the userID from the user tuple
        db = sql.connect("DM_database.db")  
        c = db.cursor()
        c.execute('''SELECT Questions_answered, Correct_questions FROM SuccessRates WHERE UserID = {}'''.format(user_id))   #collect data on questions answered and correct questions from database
        data = c.fetchall()
        db.commit()
        success_rates= []           #empty array which we will store the percentage success rate in
        for i, j in data:           #loops through each solver
            try:                #try used as if questions answered = 0 then a division by zero error occurs. As you can't divide by 0
                success_rates.append(round(100*(j/i),1))            #if there has been a question answered then this line runs correctly
                                                                    #and calculates the percentage success rate for the user on the solver
            except ZeroDivisionError:
                success_rates.append(0)                             #if there is a zero error then no question has been attempted so the success
                                                                    #rate is set intially at 0
        
        return success_rates        #returns the array of success rates

    def draw_window(self):  #displays the solvers and the users success rates to the Admin
        solvers = ["Minimum Spanning Tree", "Critical Path Analysis", "Linear Programming", "Route Inspection", "Travelling Salesman Problem"]
        Label(self.master, text=str(self.user[1])+"'s Success Rates").grid(row=0, column=0, columnspan=2)
        for i, val in enumerate(self.solver_success):
            Label(self.master, text=solvers[i]).grid(row=i+1, column=0, padx=5, pady=10)
            Label(self.master, text=str(val)+"%").grid(row=i+1, column=1, padx=5)

        size = self.master.grid_size()
        Button(self.master, text="Change Password", command=self.change_password).grid(row=size[1], column=0, columnspan=size[0])

    def change_password(self):
        newLevel = Toplevel(self.master)
        win = ChangePasswordWindow(newLevel, self.user)

class ChangePasswordWindow:

    def __init__(self, master, user):
        self.master = master
        self.Frame = Frame(self.master)
        self.user = user
        self.draw_window()

    def draw_window(self):
        Label(self.master, text="Please input new password").grid(row=0, column=0)
        password = StringVar()
        Entry(self.master, textvariable=password, show="*").grid(row=1, column=0)
        Button(self.master, text="Enter", command=partial(self.change_password, password)).grid(row=2, column=0)

    @pd
    def change_password(self, password):              #command run from tkinter button in draw_window()
        db = sql.connect("DM_database.db")
        c = db.cursor()                     #opens database

        salt = ph.generate_salt()

        hashed_password = ph.hash_password(salt, password.get())       #hashes combination of inputted password and salt

        c.execute('''UPDATE Users SET Password="{}", Salt="{}" WHERE UserID="{}"'''.format(hashed_password,salt, self.user[0]))  #inputs new password into database
        db.commit()     #closes database

        self.master.destroy()               #closes window
        
def create_window(master, admin): #creates the intial admin window to select a "class" to open or create a new "class"
                                  #master is the previous window
                                  #admin is the adminID of the currently logged in admin
    master.destroy()        #destroys the previous window
    master = Tk()           #creates new window
    admin_menu = AdminMainMenu(master, admin)      #draws the window modelled in the "Window" Class
    master.mainloop()                       #runs the tkinter mainloop to run the GUI

