# CIT3002 Operating Systems  
# Group Programming Assignment
#   NonPre-emptive Priority Scheduling with Concurrency on 2 Cores
# Group Members: Joel Wisdom - 2005295 , Bradley Miller - 0600952, Chevaun Bartley - 2004491 , Kymani Bucknor - 2102280

# Import Python modules and packages that are needed
from random import randint
from prettytable import PrettyTable

# Data structure to represent a Process
class Process:
    def __init__(self, id) -> None:
        # initialize the mandatory process attributes
        self.id = id
        self.task = randint(1,4)
        self.priority = randint(1,5)
        self.arrival_time = randint(0,29)
        self.blocked_time = 0
        self.burst_time = randint(1,5)

        # additional attributes to help track process execution
        self.start_time = 0
        self.end_time = 0
        self.remaining_time = self.burst_time
        self.result = ""
        self.started = False
        self.finished = False
        self.core_used = 0

    def execute(self):
        # this function carries out the process task, saving the result to the result attribute
        index = randint(1,20)
        value = randint(1,100)
        global resources
        if self.task == 1: # Add RECORD
            resources[index] = value
            self.result = f"Process{self.id}| Updated R:{index} to V:{value}"
        elif self.task == 2: # Remove RECORD
            resources[index] = 0
            self.result = f"Process {self.id}| Reset R:{index} to V:0"
        elif self.task == 3: # Read RECORD
            self.result = f"Process {self.id}| R:{index} is {resources[index]}"
        elif self.task == 4: # Sum of RECORDS
            self.result = f"Process {self.id}| Sum: {sum(resources.values())}"
        print(self.result)
        # append to the process result to the log file
        with open('log.txt', 'a') as log:
            log.write(f"{self.result}\n")

# Data structure to represent a CPU Core
class Core:
    def __init__(self, id) -> None:
        self.id = id
        self.process_queue = []
        self.has_lock = False
        self.current_process = None
    
    def get_busy_time(self):
        # this function checks the cores process queue for the total burst time
        timer = 0
        if len(self.process_queue) != 0:
            timer = 0
            for process in self.process_queue:
                timer = timer + process.burst_time
            return timer
        else: return 0

    def run(self, process=None):
        # this function runs a process at a given clock time (decreasing the remaining time by a unit of 1)
        
        global clock # references the system clock variable
        
        if self.current_process == None: # if no current process exists check the queue to see if one has arrived
            if self.process_queue[0].arrival_time <= clock:
                # if a process has arrived then set it as the current process and set the start time
                self.current_process = self.process_queue[0]
                self.current_process.started = True
                self.current_process.core_used = self.id
                self.current_process.start_time = clock
        if self.current_process != None:
            # check whether the process is modifying, if it is then set the resource lock to TRUE
            if self.current_process.task in [1,2]:
                self.has_lock = True
            self.current_process.remaining_time -= 1
            self.block() # if any processes came in while the current process is running, block them
            if self.current_process.remaining_time == 0: # check if the process is done
                # check if the process was modifying, if yes, the resource lock is set to FALSE
                if self.current_process.task in [1,2]:
                    self.has_lock = False
                # update the process attributes and execute the process
                self.current_process.finished = True
                print("\n\n")
                self.current_process.execute()
                self.current_process.end_time = self.current_process.start_time + self.current_process.burst_time
                system_status()
                self.process_queue.pop(0)
                # reset the current process variable to a NoneType for next process to run
                self.current_process = None

    def block(self, process=None):
        # this function increments the block time by 1 for all processes in the queue that have arrives but not started yet
        for process in self.process_queue:
            if (process.arrival_time <= clock) and process.started == False:
                process.blocked_time += 1

# Initialize the CPU cores
core1 = Core(1)
core2 = Core(2)

# Create and initialize the resource list
resources = {}
for i in range(1,21):
    resources[i] = 0

# Create the 20 processes 
processes = []
for i in range(1,21):
    processes.append(Process(i))
processes.sort(key=lambda x: (x.arrival_time, x.priority))

# Add processes to individual core queues
for process in processes:
    if core1.get_busy_time() <= core2.get_busy_time():
        core1.process_queue.append(process)
    else:
        core2.process_queue.append(process)

# Initialize the system clock to zero
clock = 0

# create/clear log that we will append subsequent process data and system status to
open("log.txt", 'w').close()

# The system_status() function outputs the details of the resource list, and all started processes
def system_status():
    table = [["Core", "PId", "Task", "Priority", "ArrivalTime", "BurstTime", "StartTime", "EndTime", "BlockedTime", "RemainingTime"]]

    for p in processes:
        if p.started:
            table.append([f"Core {p.core_used}", p.id, p.task, p.priority, p.arrival_time, p.burst_time, p.start_time, p.end_time, p.blocked_time, p.remaining_time])
    while len(table) < 20:
        table.append(["-", "-", "-", "-", "-", "-", "-", "-", "-", "-"])

    tab = PrettyTable(table[0])
    tab.add_rows(table[1:])
    max_clock = 0
    for p in processes:
        if p.finished:
            if p.end_time > max_clock:
                max_clock = p.end_time
    c_time = f"Current Time is : {max_clock}"
    print(c_time)
    print(resources)
    print(tab)
    with open("log.txt", 'a') as log:
        log.write(f"{c_time}\n")
        log.write(f"{resources}\n")
        log.write(f"{tab}\n\n")

# main function to run the whole system
def run_system():
    global clock # reference the global clock so that subsequent reassignment will update the original variable

    while True:
        cores = [core1, core2]
        # loop through a list of cores
        for core in cores:
            # this first if else block tracks the which core is the next
            # if the two cores have been iterated then increment the clock
            if core.id == 1:
                next = 2
            else: 
                next = 1
                clock += 1

            # this if else block handles the running and blocking of processes
            if cores[next-1].has_lock: # if the process on the next/other core has locked the resource then block the processes on the current core 
                core.block()
                continue
            else: # otherwise run the current cores processes
                if len(core.process_queue) > 0:
                    core.run()

        # loop through all processes and check if all are finished
        finished = 0
        for process in processes:
            if process.finished:
                finished += 1
        # if all processes have executed then exit the while loop, ending the program
        if finished == 20:
            break

run_system() # Call the starting function