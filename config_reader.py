with open('config.txt', 'r') as file:
    #Set options from config.txt
    options_list = dict()

    for line in file:
        line_name = line[:line.find(':')]
        line_value = line[line.find(':') + 2:].rstrip('\n')
        options_list[line_name] = line_value
    
    token = options_list.get('token')
    db_pass = options_list.get('db_password')
    db_host = options_list.get('db_host')
    db_name = options_list.get('db_name')
    db_user = options_list.get('db_user')