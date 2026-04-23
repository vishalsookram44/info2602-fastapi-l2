import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

cli = typer.Typer()

@cli.command()
def initialize():
    with get_session() as db: # Get a connection to the database
        drop_all() # delete all tables
        create_db_and_tables() #recreate all tables
        bob = User(username='bob', email='bob@mail.com', password='bobpass') # Create a new user (in memory)
        db.add(bob) # Tell the database about this new data
        db.commit() # Tell the database persist the data
        db.refresh(bob) # Update the user (we use this to get the ID from the db)
        print("Database Initialized")

@cli.command()
def get_user(username:str):
    # The code for task 5.1 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found!")
            return
        print(user)

@cli.command()
def get_all_users():
    # The code for task 5.2 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)


@cli.command()
def change_email(username: str, new_email:str):
    # The code for task 6 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found! Unable to update email.")
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")



@cli.command()
def create_user(username: str, email:str, password: str):
    # The code for task 7 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        new_user = User(username=username,email=email, password=password)
        try:
            db.add(new_user)
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print("Username or email already taken!")
            return
        print(new_user)

@cli.command()
def delete_user(username: str):
    # The code for task 8 goes here. Once implemented, remove the line below that says "pass"
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f"{username} not found! Unable to delete user")
            return
        db.delete(user)
        db.commit()
        print(f"{username} deleted")

@cli.command()
def partial_search(key: str):
    with get_session() as db:
        users = db.exec(select(User)).all()
        if not users:
            print("No users found")
            return
        for user in users:
            if key in user.username:
                print(user)
                continue
            elif key in user.email:
                print(user)
        
@cli.command()
def list_users(limit:int = typer.Argument(default = 10),  offset:int = typer.Argument(default = 0)):
    with get_session() as db:
        users = db.exec(select(User)).all()
        if not users:
            print("No users found")
            return
        elif offset < 0 or limit < 0:
            print("Offset or limit cannot be negative!")
            return
        elif(limit > len(users)):
            print(f"Not enough users for the required limit({limit}), limit changed to {len(users)}")
            limit = len(users)

        if(offset > limit):
            print("Offset greater than limit!")

        print(users[offset:limit+1])

if __name__ == "__main__":
    cli()
