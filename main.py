from random import randint
from prettytable import PrettyTable

class Process:
    def __init__(self, id) -> None:
        self.id = id
        self.task = randint(1,4)
        self.priority = randint(1,5)
        self.arrival_time = randint(0,29)
        self.blocked_time = 0
        self.burst_time = randint(1,5)

        self.start_time = 0
        self.end_time = 0
        self.remaining_time = self.burst_time
        self.result = ""
        self.started = False
        self.finished = False
        self.core_used = 0

    def execute(self):
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
        with open('log.txt', 'a') as log:
            log.write(f"{self.result}\n")

class Core:
    def __init__(self, id) -> None:
        self.id = id
        self.process_queue = []
        self.has_lock = False
        self.current_process = None
    
    def get_busy_time(self):
        timer = 0
        if len(self.process_queue) != 0:
            timer = 0
            for process in self.process_queue:
                timer = timer + process.burst_time
            return timer
        else: return 0

    def run(self, process=None):
        global clock
        if self.current_process == None:
            if self.process_queue[0].arrival_time <= clock:
                self.current_process = self.process_queue[0]
                self.current_process.started = True
                self.current_process.core_used = self.id
                self.current_process.start_time = clock
        if self.current_process != None:
            if self.current_process.task in [1,2]:
                self.has_lock = True
            self.current_process.remaining_time -= 1
            # system_status()
            self.block()
            if self.current_process.remaining_time == 0:
                if self.current_process.task in [1,2]:
                    self.has_lock = False
                self.current_process.finished = True
                print("\n\n")
                self.current_process.execute()
                self.current_process.end_time = self.current_process.start_time + self.current_process.burst_time
                system_status()
                self.process_queue.pop(0)
                self.current_process = None

    def block(self, process=None):
        for process in self.process_queue:
            if (process.arrival_time <= clock) and process.started == False:
                process.blocked_time += 1

core1 = Core(1)
core2 = Core(2)

resources = {}
for i in range(1,21):
    resources[i] = randint(1,100)
resource_lock = False

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

clock = 0

# create/clear log
open("log.txt", 'w').close()

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

def run_system():
    global clock

    while True:
        cores = [core1, core2]
        for core in cores:
            if core.id == 1:
                next = 2
            else: 
                next = 1
                clock += 1

            if cores[next-1].has_lock:
                core.block()
                continue
            else: 
                if len(core.process_queue) > 0:
                    core.run()

        finished = 0
        for process in processes:
            if process.finished:
                finished += 1
        
        if finished == 20:
            break

run_system()