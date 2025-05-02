import getpass
import datetime
import os

#---------------- File names------------------
ACCOUNTS_FILE = 'AccountDetails.txt'
TRANSACTION_FILE = 'transactions.txt'
CREDENTIALS_FILE = 'credentials.txt'
ACCOUNT_NUM_FILE = 'account_numbers.txt'

# -----------------Global Dictionary to keep account info in memory-------------
accounts = {}

# --------------------Load account and transaction data-------------------
def load_data():
    if os.path.exists(ACCOUNTS_FILE):
        f = open(ACCOUNTS_FILE, 'r')
        for line in f:
            parts = line.strip().split('|')
            acc_no = parts[0]
            name = parts[1]
            balance = float(parts[2])
            accounts[acc_no] = {'name': name, 'balance': balance, 'transactions': []}
        f.close()

    if os.path.exists(TRANSACTION_FILE):
        f = open(TRANSACTION_FILE, 'r')
        for line in f:
            acc_no, txn = line.strip().split('|')
            if acc_no in accounts:
                accounts[acc_no]['transactions'].append(txn)
        f.close()

# ------------------------------Make new account number-----------------------
def generate_account_number():
    if not os.path.exists(ACCOUNT_NUM_FILE):
        f = open(ACCOUNT_NUM_FILE, 'w')
        f.write('1001')
        f.close()

    f = open(ACCOUNT_NUM_FILE, 'r+')
    current = int(f.read().strip())
    new = current + 1
    f.seek(0)
    f.write(str(new))
    f.close()
    return str(current)

#----------- Save new account details--------------------
def write_account_details(acc_no, name, balance):
    f = open(ACCOUNTS_FILE, 'a')
    f.write(acc_no + '|' + name + '|' + str(balance) + '\n')
    f.close()

# --------------Save transaction log--------------------
def write_transaction(acc_no, txn):
    f = open(TRANSACTION_FILE, 'a')
    f.write(acc_no + '|' + txn + '\n')
    f.close()

# ------------Admin creates user account----------------------
def createAccount():
    name = input("Enter Your Full Name : ").strip().upper()
    if name == '':
        print("Name cannot be empty.......")
        return

    try:
        balance = float(input("Enter Initial Balance: "))
        if balance < 0:
            print("Balance must be 0 or more.....")
            return
    except:
        print("Invalid input......")
        return

    acc_no = generate_account_number()
    username = "user" + acc_no
    password = "pass" + acc_no

    f = open(CREDENTIALS_FILE, 'a')
    f.write(username + ':' + password + ':user\n')
    f.close()

    accounts[acc_no] = {
        'name': name,
        'balance': balance,
        'transactions': [f"Account opened with Rs.{balance}"]
    }

    write_account_details(acc_no, name, balance)
    write_transaction(acc_no, f"Account opened with Rs.{balance}")
    print("Account Created Successfully......")
    print("Account Number:", acc_no)
    print("Username:", username)
    print("Password:", password)

# ------------------------Deposit function---------------------
def depositMoney():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.")
        return
    try:
        amount = float(input("Enter amount to deposit: "))
        if amount <= 0:
            print("Amount must be greater than 0.......")
            return
    except:
        print("Invalid input.......")
        return

    accounts[acc_no]['balance'] += amount
    txn = f"Deposited Rs.{amount} on {datetime.datetime.now()}"
    accounts[acc_no]['transactions'].append(txn)
    write_transaction(acc_no, txn)
    print("Deposit Successful.......")

# W------------------ithdraw function--------------------------
def withdrawMoney():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.")
        return
    try:
        amount = float(input("Enter amount to withdraw: "))
        if amount <= 0:
            print("Invalid amount......")
            return
    except:
        print("Wrong input.....")
        return

    if amount > accounts[acc_no]['balance']:
        print("Not enough balance.......")
        return

    accounts[acc_no]['balance'] -= amount
    txn = f"Withdrew Rs.{amount} on {datetime.datetime.now()}"
    accounts[acc_no]['transactions'].append(txn)
    write_transaction(acc_no, txn)
    print("Withdraw Successful!.....")

# ------------------------Check balance--------------------------------
def checkBalance():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.......")
        return
    print("Your Balance is Rs.", accounts[acc_no]['balance'])

# ----------------------------Show transactions------------------------------
def transactionHistory():
    acc_no = input("Enter Account Number: ").strip()
    if acc_no not in accounts:
        print("Account not found.......")
        return
    print("Transaction History:")
    for t in accounts[acc_no]['transactions']:
        print("-", t)

#---------------------------- Read login credentials----------------------------
def read_credentials():
    creds = {}
    if os.path.exists(CREDENTIALS_FILE):
        f = open(CREDENTIALS_FILE, 'r')
        for line in f:
            line = line.strip()
            if line == '':
                continue
            username, password, role = line.split(':')
            creds[username] = {'password': password, 'role': role}
        f.close()
    return creds

#---------------------------------- Login system-----------------------------------
def login(creds):
    username = input("Enter username: ")
    password = getpass.getpass("Enter your password: ")

    if username in creds and creds[username]['password'] == password:
        role = creds[username]['role']
        print("Login successful! You are a", role)
        if role == 'admin':
            adminMenu()
        elif role == 'user':
            userMenu()
    else:
        print("Login failed. Wrong credentials.........")

#---------------------------------------- Admin dashboard-------------------------------------
def adminMenu():
    while True:
        print("\nAdmin Menu")
        print("1. Create New Account")
        print("2. Logout")
        ch = input("Enter your choice: ")
        if ch == '1':
            createAccount()
        elif ch == '2':
            break
        else:
            print("Invalid option........")

#------------------------------------------------ User dashboard-------------------------------------
def userMenu():
    while True:
        print("\nUser Menu")
        print("1. Deposit")
        print("2. Withdraw")
        print("3. Check Balance")
        print("4. View Transactions")
        print("5. Logout")
        ch = input("Enter your choice: ")
        if ch == '1':
            depositMoney()
        elif ch == '2':
            withdrawMoney()
        elif ch == '3':
            checkBalance()
        elif ch == '4':
            transactionHistory()
        elif ch == '5':
            break
        else:
            print("Invalid option.......")

# ---------------To Start the program----------------------------------------
def main():
    load_data()
    creds = read_credentials()
    login(creds)

main()
