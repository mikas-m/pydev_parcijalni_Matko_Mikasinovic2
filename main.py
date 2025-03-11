import os
import random
import requests
import datetime
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select
from datetime import date
from requests.models import HTTPError

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    date: str
    priority: str


def add_task(engine: str) -> str:
    while True:
        name = input("Insert task: ")
        date_for_task = random_date()
        random_priority = random.choice(["Low", "Medium", "High"])

        task = Task(name=name, date=date_for_task, priority=random_priority)
        work_with_session(engine, "add", task)

        if input("You wand to add another task? yes/no ") != "yes":
                os.system('cls' if os.name == 'nt' else 'clear')
                break



def show_tasks(engine: str) -> list:
    while True:
        user_choice_of_sort = input("Do you want to sort by [1] date or [2] priority? ")
        if user_choice_of_sort == "1":
            show_sorted_task(engine, Task.date)
        elif user_choice_of_sort == "2":
            show_sorted_task(engine, Task.priority)
        else:
            print("That option does not exist.")
        if input("Do you want to try again? yes/no ") != "da":
            os.system('cls' if os.name == 'nt' else 'clear')
            break



def change_task(engine: str) -> str:

    show_sorted_task(engine, Task.id)

    while True:
        id_to_change = check_id_in_table(engine)
        new_name = input("What is the new name of the task? ")
        new_date = validate_date()
        new_priority = validate_priority()
        change_task_parameters(engine, id_to_change, new_name, new_date, new_priority)
        
        if input("Do you want to change another task? ") != "yes":
            os.system('cls' if os.name == 'nt' else 'clear')
            break



def delete_task(engine: str) -> str:
    show_sorted_task(engine, Task.id)
    while True:
        id_task_to_delete = check_id_in_table(engine)

        task_to_delete = work_with_session(engine, "select_first", id_task_to_delete)
        work_with_session(engine, "delete", task_to_delete)

        if input("Task deleted. Do you want to delete another one? yes/no ") != "yes":
            os.system('cls' if os.name == 'nt' else 'clear')
            break



def synch(engine: str) -> str:
    while True:
        URL = input("Insert URL - ")

        try:
            response = requests.get(URL)
            response.raise_for_status()

            datas = response.json()
            for data in datas:
                name = data["title"]
                date_for_task = random_date()
                random_priority = random.choice(["Low", "Medium", "High"])
                
                task = Task(name=name, date=date_for_task, priority=random_priority)
                work_with_session(engine, "add", task)
                
            if input("Do you want to add tasks from another site? yes/no ") != "yes":
                os.system('cls' if os.name == 'nt' else 'clear')
                break
        except Exception as e:
            print(e)

########
def random_date():
    now = datetime.datetime.now()
    future_dates = [now + datetime.timedelta(days=i) for i in range(1, 36500)]
    random_future_date = random.choice(future_dates)
    date_for_task = random_future_date.strftime("%Y-%m-%d")
    return date_for_task

def get_int_input(prompt):
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Input has to be integer. Try again.")


def check_id_in_table(engine):
    while True:
        id_task_to_change = get_int_input("ID of the task to change ")

        if id_task_to_change not in list_ids(engine):
            print("ID unknown. Try again.")
        else:
            return id_task_to_change
        


def validate_date():
    while True:
        new_date = input("What is the new deadline? (format it as YYYY-MM-DD) ")
        
        try:
            now = datetime.datetime.now().date()
            date = datetime.datetime.strptime(new_date, '%Y-%m-%d').date()
    
            if now < date <= now + datetime.timedelta(days=365):
                return new_date
            else:
                print("Date unknown. Try again.")
        except ValueError:
            print("Wrong date format. Try again.")



def validate_priority():
    list_priority = ["Low", "Medium", "High"]
    while True:
        new_priority = input("What is the new task priority? ")
        if new_priority.title() not in list_priority:
            print("It has to be Low, Medium or High. ")
        else:
            return new_priority

#########

def list_ids(engine):
    with Session(engine) as session:
        select_all = select(Task.id)
        ids = session.exec(select_all).all()
        return ids
    

def show_sorted_task(engine, table_column):
    try:
        with Session(engine) as session:
            select_all = select(Task).order_by(table_column)
            tasks = session.exec(select_all).all()
            for task in tasks:
                print(f"ID -> {task.id}, Task -> {task.name}, Deadline -> {task.date}, Priority -> {task.priority}")
    except Exception as e:
        print(f"Error -> {e}")


def work_with_session(engine, to_do, what):
    try:
        with Session(engine) as session:
            if to_do == "add":
                session.add(what)
                session.commit()
            elif to_do == "delete":
                session.delete(what)
                session.commit()
            elif to_do == "select_first":
                select_task = select(Task).where(Task.id == what)
                task_to_change = session.exec(select_task).first()
                return task_to_change
    except Exception as e:
        session.rollback()
        print(f"Error -> {e}")


def change_task_parameters(engine, id_to_change, new_name, new_date, new_priority):
    try:
        with Session(engine) as session:
            select_task = select(Task).where(Task.id == id_to_change)
            task_to_change = session.exec(select_task).first()

            task_to_change.name = new_name
            task_to_change.date = new_date
            task_to_change.priority = new_priority

            session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error -> {e}")



#########

def main():
    engine = create_engine("sqlite:///parcijalni2.db")
    SQLModel.metadata.create_all(engine)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n--- ToDo App ---:")
        print("1. Add new task")
        print("2. Show all tasks")
        print("3. Change the task")
        print("4. Delete the task")
        print("5. Synchronize tasks from the website")
        print("6. Exit")
        choice = input("Choose: ")

        if choice == "1":
            add_task(engine)
        elif choice == "2":
            show_tasks(engine)
        elif choice == "3":
            change_task(engine)
        elif choice == "4":
            delete_task(engine)
        elif choice == "5":
            synch(engine)
        elif choice == "6":
            break
        else:
            print("Try again.")


if __name__ == "__main__":

    main()
