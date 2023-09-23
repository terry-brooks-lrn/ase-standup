from typer import Typer
import os

app = Typer()

@app.command()
def go_up():
    print("Hello.")

@app.command()
def bye(name: str):
    print(f"Bye {name}")
