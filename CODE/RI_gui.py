from tkinter import *               #tkinter is used for GUI
from tkinter import messagebox      #messagebox used for error boxes or for showing important information
from RI import RI                   #Personally made Class which solve the Route Inspection problem
from graph import Window            #Personnaly made Parent Class to the graph related GUI's
import question_string as qs

class Ri_window(Window):        #window for the route inspection solver

    def __init__(self, master, user, solverid):
        Window.__init__(self, master, user, solverid)
        self.master.title("Route Inspection Solver")

    def make_inputs(self):      #creates the inputs which the user will use to input the problem
        Window.make_inputs(self)
        size=self.master.grid_size()
        self.solve_label = Label(self.master, text="Minimum Distance: ")
        self.solve_label.grid(row=size[1], column=0, columnspan=size[0])

    def solve_problem(self, output, answer = False):        #solves the problem
        network = RI(output)
        self.answer = network.solve()
        data = []
        for row in output:
            for val in row:
                data.append(val)
        database_string = qs.generate_string("RI", data)

        if answer == False:
            self.input_to_database(database_string)     #only inputs question into database here if the user is solving the problem not answering it
            
        try:
            self.solve_label.configure(text="Minimum Distance: {}".format(self.answer))     #try and change solve label
        except:
            pass

class Ri_answer(Ri_window):     #answer window for route inspection solver
    def __init__(self, master, user, solverid):
        Ri_window.__init__(self, master, user, solverid)
        self.master.title("Route Inspection: Test Your Answers")

    def make_inputs(self):              #makes the inputs (including addtional answer entry widget)
        Ri_window.make_inputs(self)
        self.solve_label.destroy()
        self.solve_button.destroy()
        self.answer_string = StringVar()
        size = self.master.grid_size()
        Label(self.master, text="Minimum Distance: ").grid(row=size[1], column=0, columnspan=size[0])
        Entry(self.master, textvariable=self.answer_string).grid(row=size[1]+1, column=0, columnspan=size[0])
        Button(self.master, text="answer", command=self.test_answer).grid(row=size[1]+2, column=0, columnspan=size[0])

    def test_answer(self):      #takes the inputed answer and tests it against the actual answer
        self.get_inputs(answer = True)

        data = []
        for row in self.matrix:
            for val in row:
                data.append(val.get())

        if str(self.answer) == str(self.answer_string.get()):
            self.process_correct("RI", data)
        else:
            self.change_success_rate(False)
            messagebox.showinfo("Tk", "Incorrect")

class Ri_algorithm:         #window that displays the step by step instructions to perform the algorithm
    def __init__(self, master):
        self.master = master
        self.master.title("Route Inspection Algorithm")
        self.img = PhotoImage(file="RI.PNG")
        canvas = Canvas(self.master, width=self.img.width(), height=self.img.height())
        canvas.grid(row=0, column=0)
        canvas.create_image(0,0, image=self.img, anchor=NW)

def create_window(master, user, solverid, solver=True): #####CREATE NEW FRAME FOR NEW WINDOW#####
    new_window = Toplevel(master)
    if solver:
        mst_window = Ri_window(new_window, user, solverid)
    else:
        mst_window = Ri_answer(new_window, user, solverid)
    new_window.mainloop()

def show_algorithm(master):
    new_window = Toplevel(master)
    ri_window = Ri_algorithm(new_window)
    new_window.mainloop()
