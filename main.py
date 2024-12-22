import random
import requests
import datetime
import json
from sqlmodel import SQLModel, Field, create_engine, Session, Relationship, select
from datetime import date
from requests.models import HTTPError


class Task(SQLModel, table=True):
        id: int=Field(default=None, primary_key=True)
        name: str
        date: str
        priority: str

    
def add_task(engine):
    while True:
        name = input("Unesi naziv zadatka: ")
        date_for_task = random_date()
        random_priority = random.choice(["Nizak", "Srednji", "Visok"])

        task = Task(name=name, date=date_for_task, priority=random_priority)

        if not add_to_db(engine, task, "Želiš dodati još jedan zadatak? da/ne: "):
            break

def random_date():
    now = datetime.datetime.now()
    future_dates = [now + datetime.timedelta(days=i) for i in range(1, 36500)]
    random_future_date = random.choice(future_dates)
    date_for_task = random_future_date.strftime("%Y-%m-%d %H:%M:%S")
    return date_for_task

def show_sorted_tasks(engine):
    while True:
        user_choice_of_sort = input("Želiš li sortirati po [1] datumu dospijeća ili [2] prioritetu? ")
        if user_choice_of_sort == "1":
            show_sorted_task(engine, Task.date)
        elif user_choice_of_sort == "2":
            show_sorted_task(engine, Task.priority)
        else:
            print("Odabrao si broj koji se ne koristi.")
        if input("Želiš li probati opet? da/ne ") != "da":
            break


def change_task(engine):
    show_sorted_task(engine, Task.id)

    id_task_to_change = input("ID zadatka kojega želiš promijeniti ")

    new_name = input("Koji je novi naziv zadatka? ")
    new_date = input("Koji je novi datum dovršavanja zadatka? ")
    new_priority = input("Koji je novi prioritet zadatka? ")

    with Session(engine) as session:
        select_task = select(Task).where(Task.id == id_task_to_change)
        task_to_change = session.exec(select_task).first()

        task_to_change.name = new_name
        task_to_change.date = new_date
        task_to_change.priority = new_priority

        session.commit()


def delete_task(engine):
    show_sorted_task(engine, Task.id)

    id_task_to_delete = input("ID zadatka kojega želiš izbrisati? ")

    with Session(engine) as session:
        select_task = select(Task).where(Task.id == id_task_to_delete)
        task_to_delete = session.exec(select_task).first()
        session.delete(task_to_delete)
        session.commit()


def synch(engine):
    URL = "https://jsonplaceholder.typicode.com/todos?_limit=200"
    try:
        response = requests.get(URL)
        response.raise_for_status()

        datas = response.json()
        print(len(datas))
        for data in datas:
            name = data["title"]
            date_for_task = random_date()
            random_priority = random.choice(["Nizak", "Srednji", "Visok"])
            
            task = Task(name=name, date=date_for_task, priority=random_priority)
            with Session(engine) as session:
                session.add(task)
                session.commit()
            
    except HTTPError as e:
        print(e)



#POMOĆNE FUNKCIJE
def add_to_db(engine, to_do, message):
    with Session(engine) as session:
        session.add(to_do)
        session.commit()
        
        if input(message) != "da":
            False
        True

def show_sorted_task(engine, db_table):
    with Session(engine) as session:
        select_all = select(Task).order_by(db_table)
        tasks = session.exec(select_all).all()
        for task in tasks:
            print(f"ID -> {task.id}, Zadatak za napraviti -> {task.name}, Datum za napraviti -> {task.date}, Prioritet -> {task.priority}")


def main():
    engine = create_engine("sqlite:///parcijalni2.db")
    SQLModel.metadata.create_all(engine)

    while True:
        print("\n--- ToDo Aplikacija ---:")
        print("1. Dodaj novi zadatak")
        print("2. Prikaži sve podatke")
        print("3. Uredi zadatak")
        print("4. Obriši zadatak")
        print("5. Sinkroniziraj zadatke s Interneta")
        print("6. Izlaz")
        choice = input("Odaberite opciju: ")

        if choice == "1":
            add_task(engine)
        elif choice == "2":
            show_sorted_tasks(engine)
        elif choice == "3":
            change_task(engine)
        elif choice == "4":
            delete_task(engine)
        elif choice == "5":
            synch(engine)
        elif choice == "6":
            break
        else:
            print("Krivi izbor. Pokusajte ponovno.")


if __name__ == "__main__":

    main()
