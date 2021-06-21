def generate_string(question_type, data, cost=None, max_min = None):        #generates the unique string to be stored into the database
    print(data, "data")

                                                            #represents the question inputted by the user
    string = question_type      #the start of the string is the question type e.g. MST
    if question_type == "LP":   #if the problem is a LP problem then there are 2 parts the Cost (represented by "C")
                                #and the rest of the data (represented by "D")
        if cost != False:
            string += max_min
            string+="C"
            for vals in cost:       #loops through the values in the cost function
                string+="/"         #appends a "/" to seperate each value
                string+=str(round(vals, 2))     #appends the value to the string
            string += "D"       #appends a "D" to represent the start of the Data section
        else:
            return False
    if data != False:
        for i in data:      #loops through the data (which is a 2D array)
            string+="/"     #appends a "/" to seperate each value
            try:
                i = round(float(i), 2)
                string += str(i)
            except ValueError:
                if question_type != "CPA":
                    string += "0.0"
                else:
                    string += i
            
    else:
        return False
                
    return string       #returns the string

