from tkinter import *               #tkinter is used for GUI
from tkinter import messagebox      #messagebox used for error boxes or for showing important information
from functools import partial       #used for TKinter buttons as the commands called can't take parameters without partial
import password_hasher as ph        #Used to Hash passwords and create salts
import os                           #Used to check whether the database has been created already.                    
import sqlite3 as sql               #Used to interact with database
import admin_page                   #Personally made Python file which contains the code to create the admin page
import main_menu                    #Personally made Python file which contains the code to create the main menu
from password_decorator import password_decorator as pd

def create_database(first):     #This function creates the database and its tables
                                #It is only run if the database has not already been created
    
    db = sql.connect("DM_database.db")

    c = db.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Admin(AdminID INTEGER PRIMARY KEY,
                                                    Username TEXT,
                                                    Password TEXT,
                                                    Salt TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS Classes(Class_name TEXT PRIMARY KEY,
                                                    AdminID INTEGER,
                                                    FOREIGN KEY(AdminID) REFERENCES Admin(AdminID))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Users(UserID INTEGER PRIMARY KEY,
                                                    Username TEXT,
                                                    Password TEXT,
                                                    Salt TEXT,
                                                    First BOOLEAN,
                                                    Class_name TEXT,
                                                    FOREIGN KEY(Class_name) REFERENCES Classes(Class_name))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Solvers(SolverID INTEGER PRIMARY KEY,
                                                    SolverName TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS AvailableSolvers(UserSolverID INTEGER PRIMARY KEY,
                                                                Access BOOLEAN,
                                                                SolverID INTEGER,
                                                                Class_name TEXT,
                                                                FOREIGN KEY(SolverID) REFERENCES Solvers(SolverID),
                                                                FOREIGN KEY(Class_name) REFERENCES Classes(Class_name))''')

    c.execute('''CREATE TABLE IF NOT EXISTS SuccessRates(UserSuccessID INTEGER PRIMARY KEY,
                                                            Questions_answered INTEGER,
                                                            Correct_questions INTEGER,
                                                            UserID INTEGER,
                                                            SolverID INTEGER,
                                                            FOREIGN KEY(SolverID) REFERENCES Solvers(SolverID),
                                                            FOREIGN KEY(UserID) REFERENCES Users(UserID))''')

    c.execute('''CREATE TABLE IF NOT EXISTS Questions(QuestionID INTEGER PRIMARY KEY,
                                                        question TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS RecentQuestions(UserQuestionID INTEGER PRIMARY KEY,
                                                            QuestionNumber INTEGER,
                                                            UserID INTGER,
                                                            QuestionID INTEGER,
                                                            FOREIGN KEY(QuestionID) REFERENCES Questions(QuestionID),
                                                            FOREIGN KEY(UserID) REFERENCES Users(UserID))''')
                         #It is possible for the database to have been created but For no Admin account to have been created
    if first:            #This check is used for if this is Actually the first time the database is created
                         #If so it inserts the solvers into the solvers table
        c.execute('''INSERT INTO Solvers(SolverID, SolverName) VALUES(0, "Minimum Spanning Tree")''')
        c.execute('''INSERT INTO Solvers(SolverID, SolverName) VALUES(1, "Critical Path Analysis")''')
        c.execute('''INSERT INTO Solvers(SolverID, SolverName) VALUES(2, "Linear Programming")''')
        c.execute('''INSERT INTO Solvers(SolverID, SolverName) VALUES(3, "Route Inspection")''')
        c.execute('''INSERT INTO Solvers(SolverID, SolverName) VALUES(4, "Travelling Salesman Problem")''')
    db.commit()

class LogonWindow:                       #This is the Logon Window
    def __init__(self, master):     #master is the Tkinter root
        self.master = master
        self.master.title("Login Menu")
        self.frame = Frame(master)  #creates a Frame as it is a new window
        self.draw_window()

    def refresh_window(self):                   #removes all widgets and redraws them. Is used when changes are made to update the window
        widgets = self.master.grid_slaves()
        for w in widgets:
            w.destroy()

        self.draw_window()

    def logon(self):        #This funciton takes the inputted username and password in the Tkinter Entries
                            #and tests against user and admin accounts in the database to test whether they have
                            #inputted a correct username password combination
        db = sql.connect("DM_database.db")  #Connecting to database
        c = db.cursor()
        inputted_password = self.svar_2.get()
        try:            #try is used to check the line "salt = c.fetchall()[0][0]"
                        #If this line creates an error it means there is no such user
                        #can also be triggered by the raised exception if password is incorrect

            #This section checks whether the inputted credentials matches a USER
            c.execute('SELECT Salt FROM Users WHERE Username="{}"'.format(self.svar_1.get()))
            salt = c.fetchall()[0][0]               #fetches salt
            hashed_password = ph.hash_password(salt, inputted_password)         #uses password hashing file to hash the password+salt combination
            c.execute('SELECT Password FROM Users WHERE Username="{}"'.format(self.svar_1.get()))
            
            password = c.fetchall()[0][0]           #gets password from database
            if hashed_password == password:         #tests inputted password against password in database
                c.execute('SELECT First FROM Users WHERE Username="{}"'.format(self.svar_1.get()))
                first_time_user = c.fetchall()[0][0]        #finds out whether the user has accessed the program before
                if first_time_user == 1:                    #if so displays first time user screen
                    self.display_first()
                else:                                       #else opens the normal main menu for users
                    self.display()
            else:
                raise Exception("Incorrect")                #if the password doesnt match an Exception is raised to run trigger the except command

        except Exception as e:                  #This except then checks whether the inputted credentials match an ADMIN
            print(e, "1")
            try:
                c.execute('SELECT Salt FROM Admin WHERE Username="{}"'.format(self.svar_1.get()))
                salt = c.fetchall()[0][0]           #fetches salt
                hashed_password = ph.hash_password(salt, inputted_password)     #hashes password
                c.execute('SELECT Password FROM Admin WHERE Username="{}"'.format(self.svar_1.get()))
                password = c.fetchall()[0][0]       #gets password from database
                db.commit()                         #closes database
                if hashed_password == password:     #if inputted password matches password in database
                    self.admin_display()            #open admin window
                else:
                    raise Exception('Incorrect')    #else rais incorrect exception to trigger except state
            except Exception as e:
                print(e, "2")
                messagebox.showinfo("Tk", "Incorrect Username or Password")     #displays a generic reason for failure to login
                    
    def draw_window(self):      #This Function is called in __init__ and is used to generate the GUI of the login menu
        Label(text="Login").grid(row = 0, column = 1)
        Label(text="Username").grid(row=1, column=0)
        Label(text="Password").grid(row=1, column=2)        #Strings stating what is meant ot be inputted
        self.svar_1 = StringVar()                           #StringVar's are used to store the data inputted by users.
        entry_1 = Entry(self.master, textvariable = self.svar_1)    #Entry for username
        entry_1.grid(row = 2, column = 0, padx=5)   
        self.svar_2 = StringVar()
        entry_2 = Entry(self.master, textvariable = self.svar_2, show="*")      #Entry for password
        entry_2.grid(row = 2, column = 2, padx=5)

        button_1 = Button(self.master, text="Login", command = self.logon).grid(row = 3, column = 1)        #button to login

    def display_first(self):                #Changes window to first time opening window
        newLevel = Toplevel(self.master)
        win = FirstLogon(newLevel, self.svar_1.get(), self)

    def display(self):                      #changes window to User's main menu
        db = sql.connect("DM_database.db")
        c = db.cursor()

        c.execute('''SELECT Class_name FROM Users WHERE Username="{}"'''.format(self.svar_1.get()))
        class_name = c.fetchall()[0][0]
        c.execute('''SELECT UserID FROM Users WHERE Username="{}"'''.format(self.svar_1.get()))
        user_id = c.fetchall()[0][0]                                            #Collects Class name and UserID as it is required for the window that is being opened
        main_menu.create_window(self.master, class_name, user_id)
    def admin_display(self):                #changes window to Admin Page
        db = sql.connect("DM_database.db")
        c = db.cursor()
        c.execute('''SELECT AdminID FROM Admin WHERE Username="{}"'''.format(self.svar_1.get()))
        admin_id = c.fetchall()[0][0]                       #Collects AdminID as it is required for the window that is being opened
        admin_page.create_window(self.master, admin_id)

class FirstWindow:          #FirstWindow Class for ADMINS
                            #Template for GUI of the menu displayed first time a USER logs on

    def __init__(self, master, first=True):     #master is the Tkinter root, first boolean determines whether it is the first time the program is being run
        self.master = master
        self.frame = Frame(self.master)
        create_database(first)                  #if first is true then the needed information is put into the database                
        self.draw_window()

    def draw_window(self):
        Label(self.master, text="Create Account").grid(row=0, column=0, columnspan=2)
        Label(self.master, text="Username: ").grid(row=1, column=0)
        Label(self.master, text="Password: ").grid(row=2, column=0)                     #Labels show text so user knows where to input information
        password = StringVar()
        username = StringVar()
        Entry(self.master, textvariable=username).grid(row=1, column=1)
        Entry(self.master, textvariable=password, show="*").grid(row=2, column=1)       #Entry's to input wanted username and password
        Button(self.master, text="Create Account", command=partial(self.create_admin,password , username)).grid(row=3, column=0, columnspan=2)  #button to create the account

    @pd
    def create_admin(self, password, username):         #Inputs Admins information into database
        db = sql.connect("DM_database.db")
        c = db.cursor()

        if len(username.get()) != 0:

            salt = ph.generate_salt()           #generates salt for admins password
            hashed_password = ph.hash_password(salt, password.get())        #hashes admins password and salt together

            c.execute('''INSERT INTO Admin(AdminID, Username, Password, Salt) VALUES(1, "{}","{}","{}")'''.format(username.get(), hashed_password, salt))
                                        #Inserts Admins credentials into database
            db.commit()                 #closes database
            messagebox.showinfo("Tk", "Acceptable log on details")    #Information message to inform user to restart program
            self.run()
        else:
            messagebox.showinfo("Invalid Username", "A Username can not be an empty String")

    def run(self):
        self.master.destroy()           #destroys window
        root = Tk()
        win = LogonWindow(root)
        root.mainloop()
        

class FirstLogon:       #FirstLogon Class for USERS     

    def __init__(self, master, name, main):           #master is the tkinter root, name is Username
        self.user = name
        self.master = master
        self.frame = Frame(self.master)
        self.main = main
        self.draw_window()

    def draw_window(self):              #draws the GUI onto the tkinter window
        
        password = StringVar()
        Label(self.master, text="Welcome {}! Please Change your password".format(self.user)).grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        Label(self.master, text="New Password:").grid(row=1, column=0, pady=5)      #informs users to change password
        Entry(self.master, textvariable=password, show="*").grid(row=1, column=1)      #entry for user to change password
        Button(self.master, text="Enter", command=partial(self.change_password, password)).grid(row=2, column=0, columnspan=2)     #button to confirm changes

    @pd
    def change_password(self, password):              #command run from tkinter button in draw_window()
        db = sql.connect("DM_database.db")
        c = db.cursor()                     #opens database

        c.execute('''SELECT Salt FROM Users WHERE Username="{}"'''.format(self.user))
        salt = c.fetchall()[0][0]           #fetches salt

        hashed_password = ph.hash_password(salt, password.get())       #hashes combination of inputted password and salt

        c.execute('''UPDATE Users SET Password="{}" WHERE Username="{}"'''.format(hashed_password, self.user))  #inputs new password into database
        c.execute('''UPDATE Users SET First=0 WHERE Username="{}"'''.format(self.user))             #sets firs time use to 0
        db.commit()     #closes database

        messagebox.showinfo("Tk", "Please relogin to launch program")           #Information message to inform user to restart program
        self.master.destroy()               #closes window
        self.main.refresh_window()
        

def main():             #main function used to intiate the program
    root = Tk()         #creates a Tkinter base
    if os.path.isfile("DM_database.db"):        #if the database exists
        db = sql.connect("DM_database.db")
        c = db.cursor()         
        c.execute('''SELECT * FROM Admin''')    #connect to the database and test whether there is an admin
        try:
            c.fetchall()[0][0]          #error will raise if there are no admins
            app = LogonWindow(root)          #if no error thrown then there is a database and admin so the normal login menu can be shown
        except IndexError:
            app = FirstWindow(root, first=False)        #no admins means the FirstWindow must be shown but the database inputs shouldn't be re inputted
    else:
        app = FirstWindow(root)         #if the database doesnt exist the FirstWindow must be shown and data should be inputted to database
    root.mainloop()                     #runs tkinter loop to display GUI

main()
