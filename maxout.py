#!/usr/bin/env python3

import pyrebase
import datetime
import pandas as pd
import matplotlib.pyplot as plt

#Firebase's configuration set up
config = {
    "apiKey": "AIzaSyDG_-uWwn1SGC3PAsw6y5YCtk1eXM0nMfA",
  "authDomain": "maxout-beb8c.firebaseapp.com",
  "databaseURL": "https://maxout-beb8c-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "maxout-beb8c",
  "storageBucket": "maxout-beb8c.appspot.com",
  "messagingSenderId": "113683607705",
  "appId": "1:113683607705:web:896673d71e48b08c3e4808",
  "measurementId": "G-Z4V7TMD4DP"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
today = str(datetime.date.today().strftime("%d-%m-%y"))
maxout = True
today_tasks = db.child(today).get()
tasks = today_tasks.val()
if tasks is None:
    tasks = {}

def main():
    #Some functions accept words + an argument to skip asking for an input again.
    while maxout is True:
        response = input("What do you wanna do? ('Add', 'Remove', 'Update', 'Check', 'Status', 'Graph', 'Exit')\n")
        if response.strip().lower() == 'add' or response.strip().lower()[:3] == 'add':
            print(AddTask(tasks, response.strip()))
        elif response.strip().lower() == 'update' or response.strip().lower()[:6] == 'update':
            print(UpdateTask(tasks, response.strip()))
        elif response.strip().lower() == 'remove' or response.strip().lower()[:6] == 'remove':
            print(RemoveTask(tasks, response.strip()))
        elif response.strip().lower() == 'status':
            print(TaskStatus(tasks))
        elif response.strip().lower() == 'exit':
            print(ExitMaxout(tasks))
        elif response.strip().lower() == 'check' or response.strip().lower()[:5] == 'check':
            print(CheckTasks(tasks, response.strip()))
        elif response.strip().lower() == 'graph':
            MakeGraph(tasks)
        else:
            print("Wrong command, try again...")

def AddTask(tasks, response):
    if len(response) == 3:
        task = input("What's the name of the task you want to add?\n")
        if task not in tasks:
            tasks[task] = 0
            return "Task added succesfully..."
        else:
            return "Task already in the list..."
    else:
        task = " ".join(response.split()[1:])
        if task not in tasks:
            tasks[task] = 0
            return "Task added succesfully..."
        else:
            return "Task already in the list..."

def UpdateTask(tasks, response):
    if len(tasks) == 0:
        return "The task list is empty..."
    if len(response) == 6:
        task = input("What's the name of the task you want to update?\n")
        if task not in tasks:
            return "Task name is incorrect, going back..."
        else:
            status = input("Have you completed this task? ('Yes' for completion, 'No' to go back)\n")
            if status.strip().lower() == 'yes':
                tasks[task] = 1
                return "Task completion updated..."
            else:
                return "Going back..."
    else:
        task = " ".join(response.split()[1:])
        if task not in tasks:
            return "Task name is incorrect, going back..."
        else:
            status = input("Have you completed this task? ('Yes' for completion, 'No' to go back)\n")
            if status.strip().lower() == 'yes':
                tasks[task] = 1
                return "Task completion updated..."
            else:
                return "Going back..."        

def RemoveTask(tasks, response):
    if len(tasks) == 0:
        return "The task list is empty..."
    if len(response) == 6:
        task = input("What's the name of the task you wanna remove?\n")
        if task not in tasks:
            return "Task name not in list, going back..."
        else:
            tasks.pop(task)
            db.child(today).child(task).remove()
            return "Task removed from the list..."
    else:
        task = " ".join(response.split()[1:])
        if task not in tasks:
            return "Task name not in list, going back..."
        else:
            tasks.pop(task)
            db.child(today).child(task).remove()
            return "Task removed from the list..."

def TaskStatus(tasks):
    if len(tasks) == 0:
        return "The task list is empty..."
    num_of_completed_tasks = 0
    tasks_completed = []
    for task in tasks:
        if tasks[task] == 0:
            print(task + " not completed yet...")
        else:
            num_of_completed_tasks += 1
            tasks_completed.append(task)
    if num_of_completed_tasks > 0:
        return "You have completed the following tasks: " + ", ".join(tasks_completed) + ".\nYour completion rate is: " + str((num_of_completed_tasks / len(tasks)) * 100) + "%"
    else:
        return "You have not completed any tasks yet, get onto it!"

def CheckTasks(tasks, response):
    if len(tasks) == 0:
        return "The task list is empty..."
    if len(response) == 5:
        return "These are the tasks on the list: " + ", ".join(tasks)
    else:
        task = task = " ".join(response.split()[1:])
        if tasks[task] == 0:
            return task + " not completed yet..."
        else:
            return task + " was completed..."       

def ExitMaxout(tasks):
    global maxout
    if today_tasks.val() is None:
        db.child(today).set(tasks)
    else:
        db.child(today).update(tasks)
    maxout = False
    return "Tasks updated succesfully"

def MakeGraph(tasks):
    date_range = input("For what timeframe do you want a graph? ('Today', 'Weekly', 'Monthly')\n")
    if date_range.strip().lower() == "today":
        completion_rate = round((sum(value == 1 for value in tasks.values()) / len(tasks)) * 100)
        df = pd.DataFrame({"Completion rate %":[completion_rate]}, index = ["Today"])
        df.plot.bar()
        plt.title("Daily stats")
        plt.ylim(0, 100)
        plt.show()
    elif date_range.strip().lower() == "weekly":
        todays_weekday = datetime.date.today().weekday()
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        list_of_completion_rates = []
        current_day_in_the_loop = int(today[0:2]) - todays_weekday
        #This loop goes from the start of the week until the end of it.
        while current_day_in_the_loop <= int(today[0:2]) - todays_weekday + 6:
            current_date_in_the_loop = (str(current_day_in_the_loop) + today[2:])
            current_date_in_the_loops_tasks = db.child(current_date_in_the_loop).get().val()
            if current_date_in_the_loops_tasks is None:
                list_of_completion_rates.append(0)
            else:
                list_of_completion_rates.append(round((sum(value == 1 for value in current_date_in_the_loops_tasks.values()) / len(current_date_in_the_loops_tasks)) * 100))
            current_day_in_the_loop += 1
        df = pd.DataFrame({"Completion rate %":list_of_completion_rates}, index = weekdays)
        df.plot.bar() 
        plt.title("Weekly stats")
        plt.ylim(0, 100)
        plt.show()
    elif date_range.strip().lower() == "monthly":
        days_of_the_month = []
        list_of_completion_rates = []
        this_month = int(today[3:5])
        #Caclulates how many days are in this month.
        days_to_go = (datetime.date(2022, this_month + 1, 1) - datetime.date(2022, this_month, 1)).days
        current_day_in_the_loop = 1
        while current_day_in_the_loop <= days_to_go:
            current_date_in_the_loop = (str(current_day_in_the_loop) + today[2:])
            current_date_in_the_loops_tasks = db.child(current_date_in_the_loop).get().val()
            days_of_the_month.append(current_date_in_the_loop[:5])
            if current_date_in_the_loops_tasks is None:
                list_of_completion_rates.append(0)
            else:
                list_of_completion_rates.append(round((sum(value == 1 for value in current_date_in_the_loops_tasks.values()) / len(current_date_in_the_loops_tasks)) * 100))
            current_day_in_the_loop += 1
        df = pd.DataFrame({"Completion rate %":list_of_completion_rates}, index = days_of_the_month)
        df.plot.bar()
        plt.title("Monthly stats")
        plt.ylim(0, 100)
        plt.show()

if __name__ == '__main__':
    main()