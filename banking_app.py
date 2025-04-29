UserBalance = 55000

def getInputFromUser():
    amount = float(input("Enter The Amount : "))

    if amount 


# def createAccount():

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




