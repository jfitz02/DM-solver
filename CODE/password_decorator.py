from tkinter import messagebox

def password_decorator(func):           #decorator, takes the function as an argument

    def check(*args):       #takes the arguments of the function
        password = args[1].get()        #checks the password inputted is greater than 8 characters
        print(password)
        if len(password)<8:
            messagebox.showinfo("Password Error", "Password should be 8 or more characters")
        else:
            func(*args)

    return check
