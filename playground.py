from typing import Annotated

def QuerypParamneterConstraint(min_length: int = 0, max_length: int =50):
    return {"min_length": min_length, "max_length": max_length}


def my_function(value):
    print(value)