UserBalance = 55000


def getInputName():
    name =input("Enter Your Full Name : ").strip().upper()

def getInputNic():
    nic = input("Enter Your Nic Number : ").strip().lower()

    length = len(nic)
    while True:
        
        if length == 12:
            return nic
            break
        elif length ==10:
            if nic[-1] == 'v':
                return nic
                break
            else:
                print("Enter The Correct Nic Number: ")
                
        else:
            print("Enter The Correct Nic Number: ")
            
    

def getInputDob():
    dob = input("Enter Your Your Date Of Birth (YYYY-MM-DD) : ").strip()
    return dob



def getInputFromUser():
    amount = float(input("Enter The Amount : "))

    if amount > 0:


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

    except Nullpoint       
        

        

def depositMoney():
    global userbalance
    try:
        withAmount = int(input("Enter The Withdraw Amount : "))
        if withAmount <= userbalance:
            with 
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

def main():

    attempt =0
    while attempt < 3:
        print("\t\t========== Welcom to Unicom Tic Bank ==========")

        userInput = input("1.Do You Have An Account (y/n):").lower().strip()

        if userInput == "y" or userInput == "yes":
            login()
        elif userInput == "n" or userInput == "no":
            createAccount()
        else:
            print("Enter The Correct Input...",f"Remaining Chance Is {2-attempt}")
            attempt +=1

    if attempt == 3 :
        print("User Chance Are Finished ...")   


def menu():
    while True:
        print("====== Welcom To Unicom Tic Bank Menu ========")
        print("1. Create Account ",)
        print("2.Deposit Money ")
        print("3.Withdraw Money ")
        print("4.Check Balance ")
        print("5.Transaction History ")
        print("6.Exit")
        
        choice = input("Select Your Activity(1-6): ").strip()

        if choice =='1':
            createAccount()
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

def login():
    userName = "user"
    userPassword = "1234"

    userNameInput = input("Enter Your UserName : ").strip()
    userPasswordInput = input("Enter The Password : ").strip()

    attempt = 0
    while attempt <3:
        if userName == userNameInput and userPassword==userPasswordInput:
            menu()
        else:
            print("Enter The Correct User Name ,Password ...",f"Remaining Chance Is {2-attempt}")
            attempt +=1

    if attempt == 3 :
        print("User Your Login Chance is Finished")
        main()
      




main()




