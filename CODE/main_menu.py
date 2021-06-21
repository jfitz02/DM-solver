from tkinter import *                               #tkinter is used for GUI
from functools import partial                       #used for TKinter buttons as the commands called can't take parameters without partial
import MST_gui, LP_gui, RI_gui, TSP_gui, CPA_gui    #personally made python files. Each containing code for their corresponding solver
import sqlite3 as sql                               #Used to interact with database

class Menu:

    NAMES =  {"Minimum Spanning Tree":MST_gui, "Linear Programming":LP_gui, "Route Inspection":RI_gui, "Travelling Salesman Problem":TSP_gui, "Critical Path Analysis":CPA_gui}
                        #dictionary of all available solvers and their corresponding libraries

    def __init__(self, master, classn, user):       #master is the tkinter root, classn is the class name the user is in, user is the currently logged in user
        self.master = master
        self.frame = Frame(master)
        self.master.title("Main Menu")
        self.classname = classn
        self.user = user
        self.draw_window()

    def refresh_window(self):           #clears all widgets and redraws them
        widgets = root.grid_slaves()
        for w in widgets:
            w.destroy()

        self.draw_window()

    def turn_into_names(self, ids):
        db = sql.connect("DM_database.db")
        c = db.cursor()
        names = []
        for val in ids:
            c.execute('''SELECT SolverName FROM Solvers WHERE SolverID={}'''.format(val))
            names.append(c.fetchall()[0][0])

        return names
            

    def get_available(self):
        db = sql.connect("DM_database.db")
        c = db.cursor()
        c.execute('''SELECT SolverID, Access FROM AvailableSolvers WHERE Class_name="{}"'''.format(self.classname))
        data = c.fetchall()
        db.commit()

        solver_ids = []
        access = []
        for vals in data:
            solver_ids.append(vals[0])
            access.append(vals[1])

        solver_names = self.turn_into_names(solver_ids)

        return solver_names, access
        
    def draw_window(self):
        Label(text="Discrete Mathematics Helper").grid(row = 0, column = 1)
        buttons = []
        solvers, available = self.get_available()
        for i, solver in enumerate(solvers):
            if available[i] == 1:
                buttons.append(Button(self.master, text=solver, command=partial(self.NAMES[solver].create_window, self.master, self.user, i)))
            else:
                buttons.append(Button(self.master, state=DISABLED, text=solver, command=partial(self.NAMES[solver].create_window, self.master, self.user, i)))
            buttons.append(Button(self.master, text="Test Your Answers", command=partial(self.NAMES[solver].create_window, self.master, self.user, i, solver=False)))
            buttons.append(Button(self.master, text="Algorithm", command=partial(self.NAMES[solver].show_algorithm, self.master)))
            buttons[i*3].grid(row = i+2, column = 0, pady=10)
            buttons[(i*3)+1].grid(row = i+2, column = 1, pady=10)
            buttons[(i*3)+2].grid(row = i+2, column = 2, pady=10)
            buttons[i*3].update()
            buttons[(i*3)+1].update()
            buttons[(i*3)+2].update()

        for button in buttons:
            button.config(width = max([len(i) for i in self.NAMES]))


def create_window(master, classn, user):
    master.destroy()
    root = Tk()
    window = Menu(root, classn, user)
    root.mainloop()
