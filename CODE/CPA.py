class Activity:         #Activity class. Represents the 

    def __init__(self, duration, predecessor_names, name):       #duration is the time the activity takes to complete
                                                            #predecessor_names are the names of the activities that need to be completed before the current activity can start
                                                            #name is the character which represents this activity.
        self.duration = duration
        self.earliest_start = 0
        self.latest_finish = 0      #intitially the earliest start and latest finish are set to 0
        self.predecessor_names = predecessor_names
        self.followers = []
        self.predecessors = []
        self.name = name
        
    def __str__(self):      #this function means that if the object is turned into a string it will show the name of the activity
        return self.name

    def find_predecessors(self, activities):        #this function takes the name of the activities predecessors and finds the object in which they represent
                                                    #activities is the list of the Activity objects
        for act in activities:      #loops through all activities
            if str(act) in self.predecessor_names:  #if the string of the act (ie its name) is in the current activities predecessor_names then...
                self.predecessors.append(act)       #it is appended as a predecessor
                act.followers.append(self)          #and the act appends this activity as one of its followers



class Network:      #Network class. This class is made up of many activities and performs the operations to solve the problem

    def __init__(self, activities, durations, predecessors):    #activities is a list of the activity names
                                                                #durations is a list of the duration of each activity
                                                                #predecessors is a list made up of lists of each activities predecessors
                                                                #the lists are ordered the same so activities[i], durations[i] and predecessors[i]
                                                                #are combined the information for 1 activity
        self.activities = []        #empty array to store all of the activity classes
        for i in range(len(activities)):        #loops through each activity name to create an object for that activity
            self.activities.append(Activity(durations[i], predecessors[i], activities[i]))
        for act in self.activities:             #loops throuvh all the objects to run the Activity.find_predecssors(activities)
            act.find_predecessors(self.activities)

    def test_validity(self):
        valid = True
        for act in self.activities:
            if act.earliest_start>act.latest_finish:
                valid = False

        return valid
    
    def forward_pass(self):             #forward pass is used to find the earliest start time of each activity
        for act in self.activities:     #loops through all activities
            for fol in act.followers:   #loops through the activities following activities
                if act.earliest_start + act.duration > fol.earliest_start:      #if the activities earliest start + its duration is greater than the followers earliest start
                    fol.earliest_start = act.earliest_start + act.duration      #then the following earliest start = activities earliest_start + duration

    def backward_pass(self):        #backward pass is used to find the latest finish times
        project_finish = 0          #set to 0 but is meant to represent the finish time of the project
        for act in self.activities:     #loops through activities
            if act.earliest_start+act.duration>project_finish:  #if the activities earliest start time + its duration > project finish time
                project_finish = act.earliest_start+act.duration        #the project finish now = earliest start + duration

        for act in self.activities:     #loops back through all activities to set all activities latest finish to the project finish time
            act.latest_finish = project_finish

        for act in reversed(self.activities):   #loops through activities in reverse order
            for pre in act.predecessors:        #loops through the activities predecessors
                if act.latest_finish-act.duration<pre.latest_finish:    #if the activities latest finish - its duration < predecessors latest finish
                    pre.latest_finish = act.latest_finish-act.duration      #then predecessors latest finish = activities latest finish - duration

    def output_network(self):       #this function returns a string representing the answer of the problem
        if self.test_validity():
            outputs = []
            for act in self.activities:
                #outputs.append(str("Earliest Start: "+str(act.earliest_start)+"  Duration: "+str(act.duration)+ "  Latest Finish: "+str(act.latest_finish)))
                outputs.append((round(act.earliest_start,2), round(act.duration,2), round(act.latest_finish,2)))
            return outputs
        else:
            return False
                
