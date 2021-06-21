from tkinter import *           #tkinter is used for GUI
from MST import MST             #Personnaly made class used to solve the Minimum Spanning Tree Problem
from graph import Window        #Personnaly made Parent Class to the graph related GUI's
import question_string as qs
import sqlite3 as sql           #Used to interact with database


class Mst_window(Window):

    def __init__(self, master, user, solverid):
        Window.__init__(self, master, user, solverid)       #initialises the super class Window
        self.user = user
        self.master.title("Minimum Spanning Tree Solver")

    def make_inputs(self):      #makes the GUI inputs, Overwrites the make_inputs function in Window
        Window.make_inputs(self)        #initialises generic inputs for all Graph based problems
        size = self.master.grid_size()
        self.solve_label = Label(self.master, text="Minimum Distance: ")
        self.solve_label.grid(row=size[1], column=0, columnspan=size[0])        #all additions specific for MST

    def solve_problem(self, output, answer=False):      #overwritten function from Window
        network = MST(output)
        network.solve()
        self.answer= str(network)       #creates and solve the problem using the MST class
        data = []
        for i in self.matrix:
            for j in i:
                data.append(j.get())
        database_string = qs.generate_string("MST", data)      #creates the string that will be stored into the database

        if answer == False:         
            self.input_to_database(database_string)     #will store the question into the database if the user is not attempting to answer it
            self.solve_label.configure(text="Minimum Distance: {}".format(self.answer))     #tries configuring the solve label

class Mst_answer(Mst_window):       #Subclass of Mst_window
    def __init__(self, master, user, solverid):
        Mst_window.__init__(self, master, user, solverid)       #intialises super class Mst_window
        self.master.title("Minimum Spanning Tree: Test Your Answer")

    def make_inputs(self):      #overwritten from super class
        Mst_window.make_inputs(self)        #initially makes the super classes window
        self.solve_label.destroy()
        self.solve_button.destroy()     #removes solve label and button
        self.answer_string = StringVar()
        size=self.master.grid_size()
        Label(self.master, text="Minimum Distance: ").grid(row=size[1], column=0, columnspan=size[0])
        Entry(self.master, textvariable=self.answer_string).grid(row=size[1]+1, column=0, columnspan=size[0])
        Button(self.master, text="Answer", command = self.test_answer).grid(row=size[1]+2, column=0, columnspan=size[0])        #adds in widgets for users to put their
                                                                                                                                #answers in



    def test_answer(self):          #test answer will solve the problem they have inputted and test it against their answer
        self.get_inputs(answer = True)

        if self.answer != False:

            data = []
            for i in self.matrix:
                for j in i:
                    data.append(j.get())

            if self.answer == self.answer_string.get():
                self.process_correct("MST", data)          #procedure written in Window superclass
            else:
                self.change_success_rate(False)     #procedure written in Window superclass
                messagebox.showinfo("Tk", "Incorrect")

        
        
class Mst_algorithm:        #class which is used to show the algorithm used to the user to revise from
    def __init__(self, master):
        self.master = master
        self.frame = Frame(self.master)
        self.master.title("Minimum Spanning Tree Algorithm")
        self.img = PhotoImage(file="MST.PNG")
        canvas = Canvas(self.master, width=self.img.width(), height=self.img.height())
        canvas.grid(row=0, column=0)
        canvas.create_image(0,0,image=self.img, anchor = NW)

def create_window(master, user, solverid, solver=True): #####CREATE NEW FRAME FOR NEW WINDOW#####
    new_window = Toplevel(master)
    if solver:
        mst_window = Mst_window(new_window, user, solverid)
    else:
        mst_window = Mst_answer(new_window, user, solverid)
    new_window.mainloop()

def show_algorithm(master):
    new_window = Toplevel(master)
    mst_window = Mst_algorithm(new_window)
    new_window.mainloop()

