import os

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# now, to clear the screen


def display_error(error, error_message):
    cls()
    print("-------------------------AN ERROR OCCURED---------------------------\n")
    print(error)
    print(error_message)
    print("--------------------------------------------------------------------\n\n")