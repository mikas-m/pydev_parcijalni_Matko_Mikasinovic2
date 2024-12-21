import random
import requests
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
        date = input("Datum do kada zadatak mora biti ispunjen (u formatu YYYY-MM-DD): ")
        random_priority = random.choice(["Nizak", "Srednji", "Visok"])

        task = Task(name=name, date=date, priority=random_priority)

        if not add_to_db(engine, task, "Želiš dodati još jedan zadatak? da/ne: "):
            break


def show_tasks(engine):
    while True:
        user_choice_of_sort = input("Želiš li sortirati po [1] datumu dospijeća ili [2] prioritetu? ")
        if user_choice_of_sort == "1":
            show_task(engine, Task.date)
        elif user_choice_of_sort == "2":
            show_task(engine, Task.priority)
        else:
            if input("Želiš li probati opet? da/ne ") != "da":
                break


def change_task(engine):
    show_task(engine, Task.id)

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
    show_task(engine, Task.id)

    id_task_to_delete = input("ID zadatka kojega želiš izbrisati? ")

    with Session(engine) as session:
        select_task = select(Task).where(Task.id == id_task_to_delete)
        task_to_delete = session.exec(select_task).first()
        session.delete(task_to_delete)
        session.commit()

def synch():
    URL = "https://jsonplaceholder.typicode.com/todos"
    try:
        response = requests.get(URL)
        response.raise_for_status()

        data = response.json()
        print(data["fact"])
    except HTTPError as e:
        print(e)



def add_to_db(engine, to_do, message):
    with Session(engine) as session:
        session.add(to_do)
        session.commit()
        
        if input(message) != "da":
            False
        True

def show_task(engine, db_table):
    with Session(engine) as session:
        select_all = select(Task).order_by(db_table)
        tasks = session.exec(select_all).all()
        for task in tasks:
            print(f"ID -> {task.id}, Task to do -> {task.name}, Date to do it -> {task.date}, Priority -> {task.priority}")





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
            show_tasks(engine)
        elif choice == "3":
            change_task(engine)
        elif choice == "4":
            delete_task(engine)
        elif choice == "5":
            sync(engine)
        elif choice == "6":
            break
        else:
            print("Krivi izbor. Pokusajte ponovno.")


if __name__ == "__main__":

    main()
