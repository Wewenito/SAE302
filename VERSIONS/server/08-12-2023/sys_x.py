import os, random, string

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

# now, to clear the screen


def display_error(error, error_message):
    cls()
    print("-------------------------AN ERROR OCCURED---------------------------\n")
    print(error)
    print(error_message)
    print("--------------------------------------------------------------------\n\n")


def generate_uid():
    characters = string.ascii_uppercase + string.digits
    uid = ''.join(random.choice(characters) for _ in range(4))
    return uid