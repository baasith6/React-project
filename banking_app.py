UserBalance = 55000

def userDetailsInputValidation(name,nic,dob,email):
    
    length = len(nic)
    if len(name) > 0 and name.isalpha():
        return True
    else:
        print("Input is null.")

    if length == 12:
        return nic
    elif length ==10:
        if nic[-1] == 'v':
            return nic
        else:
            print("Enter The Correct Nic Number: ")
            
    else:
        print("Enter The Correct Nic Number: ")
    try:
        # Define the expected date format
        dob = datetime.strptime(dob_str, "%Y-%m-%d")
        
        # Check if the date is in the past
        if dob >= datetime.now():
            return False, "Date of birth cannot be in the future."
        
        return True, "Valid date of birth."
    except ValueError:
        return False, "Invalid date format. Please use YYYY-MM-DD."

def getInputUserDetails():
    while True:
        name =input("Enter Your Full Name : ").strip().upper()
        nic = input("Enter Your Nic Number : ").strip().lower()
        dob = input("Enter Your Your Date Of Birth (YYYY-MM-DD) : ").strip()
        email = input("Enter Your Email :  ")

        if userDetailsInputValidation(name,nic,dob,email):
            return (name,nic,dob,email)



# def getInputFromUser():
#     amount = float(input("Enter The Amount : "))

#     if amount > 0:


def WriteUserDetails():
    getInputName()
    getInputNic()
    getInputDob()
    file = open('AccountDetails.txt','a')
    file.write('\t')
    file.write()


def createAccount():
    try:

        while True:
            print ("Which Account Do You Want to Open ")
            print("1.Current Account ")
            print("2.Saving Account ")
            
            acOption = input("Select Your Account (1-2): ").strip()

            if acOption == '1':
                print("You Selected Current Account...")
                print("Can You Enter Your Personal Details...")
                WriteUserDetails()
                break

            elif acOption =='2':
                print("You Selected Savings Account ")
                print("Can You Enter Your Personal Details...")
                WriteUserDetails()
                break
            else:
                print("Select The Correct Account...")

    except ValueError :
        print ("Enter the Correct Value ...")       
        

        

def depositMoney():
    global userbalance
    try:
        withAmount = int(input("Enter The Withdraw Amount : "))
        if withAmount <= userbalance: 
            userbalance -= withAmount
            print("The withdrawal is Successful")
        else:
            print("Insufficient balance. Try again.")

    except ValueError:
        print("Please Enter a Valid Number...")
    print("==========================")

# def withdrawMoney():

# def checkBalance():

# def transactionHistory():



def adminMenu():
    print("========= Welcome To Admin Dashboard ===============")
    print("1. Create Account ")
    print("2.Account Details ")
    print("3.Exit")

    choice = input("Select Your Activity(1-6): ").strip()

    while True:
        if choice =='1':
            createAccount()
        elif choice =='2':
            totalAcDetails()
        elif choice=='3':
            exit()
        else:
            print("Enter the correct Activity...")

def userMenu():
    while True:
        print("====== Welcom To Unicom Tic Bank Menu ========")
        print("1.Account Details ")
        print("2.Deposit Money ")
        print("3.Withdraw Money ")
        print("4.Check Balance ")
        print("5.Transaction History ")
        print("6.Exit")
        
        choice = input("Select Your Activity(1-6): ").strip()

        if choice =='1':
            userAcDetails()
        elif choice =='2':
            depositMoney()
        elif choice=='3':
            withdrawMoney()
        elif choice =='4':
            checkBalance()
        elif choice =='5':
            transactionHistory()
        elif choice == '6':
            exit()
        else:
            print("Enter the correct Activity...")



def read_credentials():
    file_path ='credentials.txt'
    credentials = {}
    with open(file_path, 'r') as file:
        for line in file:
            username, password, role = line.strip().split(':')
            credentials[username] = {'password': password, 'role': role}
    return credentials


def login(credentials):
    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in credentials and credentials[username]['password'] == password:
        role = credentials[username]['role']
        print(f"Login successful! Welcome, {role}.")
        if role == 'admin':
            adminMenu()
        elif role == 'user':
            userMenu()
    else:
        print("Invalid username or password.")
        return None
      


def main():
    credentials = read_credentials()
    role = login(credentials)


main()




