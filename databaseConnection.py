def getCredentials():
    file = open("db_connection.txt", "r")
    myHost = file.readline().strip()
    myUser = file.readline().strip()
    myPasswd = file.readline().strip()
    myDatabase = file.readline().strip()
    port = int(file.readline().strip())
    file.close()
    return myHost, myUser, myPasswd, myDatabase, port