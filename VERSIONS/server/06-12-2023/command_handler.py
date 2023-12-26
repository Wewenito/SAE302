def CHandler(command):
    case = None

    first_space_index = command.find(' ')

    if command.startswith('/'):
        case = 1
    else:
        case = 2


    if case == 1: #If a command is sent
        if first_space_index != -1: #If command is a command keyword + string (ex : /join Salon1 or /broadcast this is a global broadcast)
            split = [command[:first_space_index], command[first_space_index + 1:]]

            match split[0]:
                    case "/broadcast":
                        return ["BROADCAST", split[1]]
                    case _:
                        return ["SINGLE KEYWORD", None]
        else: #if command is just a single keyword (ex : /bye  or /logout)
            split = [command]
            match split[0]:
                case "/bye":
                    return ["BYE", None]
                case _:
                    return ["UNKNOWN", None]
    elif case == 2: #If only a random string is sent
        return ["UNKNOWN_CASE_2", None]
    else:
        return ["UNKNOWN", None]
