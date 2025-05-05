import pwinput
import bcrypt
from tabulate import tabulate
import datetime
import os
import re
from colorama import Fore, Style, init
init(autoreset=True)


# ---------------- File Names ------------------
accountsFile = 'AccountDetails.txt'
transactionsFile = 'transactions.txt'
credentialsFile = 'credentials.txt'
accountNumFile = 'account_numbers.txt'
customerDetailsFile = 'CustomerProfiles.txt'
changeLogFile = 'change_log.txt'
deactivationLogFile = 'deactivation_log.txt'
#--------------------------------------------------
# ------------------ Secure Password Handling ------------------
def hash_password(password):

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):

    return bcrypt.checkpw(password.encode(), hashed.encode())

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def accountInactive(accNo):
    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            for line in f:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')
                    return parts[-1] == "Inactive"
    return False


# ---------------- Load Data ------------------
def loadData():
    accounts = {}
    if os.path.exists(accountsFile):
        with open(accountsFile, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) < 3:
                    continue
                accNo = parts[0]
                name = parts[1]
                try:
                    balance = float(parts[2])
                except ValueError:
                    balance = 0.0
                accounts[accNo] = {'name': name, 'balance': balance, 'transactions': []}

    if os.path.exists(transactionsFile):
        with open(transactionsFile, 'r') as f:
            for line in f:
                accNo, txn = line.strip().split('|')
                if accNo in accounts:
                    accounts[accNo]['transactions'].append(txn)
    return accounts

# ---------------- Generate Account Number ------------------
def generateAccountNumber():
    if not os.path.exists(accountNumFile):
        with open(accountNumFile, 'w') as f:
            f.write('1001')

    with open(accountNumFile, 'r+') as f:
        content = f.read().strip()
        if not content.isdigit():
            current = 1001
        else:
            current = int(content)
        new = current + 1
        f.seek(0)
        f.write(str(new))
        f.truncate()
    return str(current)


# ---------------- Write Account and Transaction ------------------
def writeAccountDetails(accNo, name, balance):
    with open(accountsFile, 'a') as f:
        f.write(accNo + '|' + name + '|' + str(balance) + '\n')

def writeTransaction(accNo, txn):
    with open(transactionsFile, 'a') as f:
        f.write(accNo + '|' + txn + '\n')

# ---------------- Read Credentials ------------------
def readCredentials():
    credentials = {}
    if os.path.exists(credentialsFile):
        with open(credentialsFile, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 3:
                    username, password, role = parts
                    credentials[username] = {'password': password, 'role': role}
    return credentials

# ---------------- Login ------------------
def login(credentials):
    print(Fore.CYAN + "\n=== Login ===")
    username = input("Username: ").strip()
    password = pwinput.pwinput("Password: ").strip()

    if username in credentials and check_password(password, credentials[username]['password']):
        role = credentials[username]['role']

        if role == 'user':
            accNo = username.replace('user', '')
            if os.path.exists(customerDetailsFile):
                with open(customerDetailsFile, 'r') as f:
                    for line in f:
                        if line.startswith(accNo + "|"):
                            parts = line.strip().split('|')
                            if len(parts) == 9:
                                parts.append("Active")
                            if parts[-1] == "Inactive":
                                print(Fore.RED+"❌ Your account is inactive. Contact the bank.")
                                return None
                            break
            print(Fore.GREEN + f"Login successful! Logged in as User.")
            return role, accNo

        print(Fore.GREEN + f"Login successful! Logged in as Admin.")
        return role, None
    else:
        print(Fore.RED +"Login failed. Invalid username or password.")
        return None


# ---------------- Create Account ------------------
def is_duplicate_nic(nic):
    if not os.path.exists(customerDetailsFile):
        return False
    with open(customerDetailsFile, 'r') as f:
        for line in f:
            if nic in line.split('|'):
                return True
    return False
def getDobFromNic(nic):
    if re.match(r'^\d{9}[VvXx]$', nic):  # Old NIC
        year = 1900 + int(nic[:2])
        dayOfYear = int(nic[2:5])
    elif re.match(r'^\d{12}$', nic):  # New NIC
        year = int(nic[:4])
        dayOfYear = int(nic[4:7])
    else:
        return None, None  # Invalid NIC

    gender = "Female" if dayOfYear > 500 else "Male"
    if dayOfYear > 500:
        dayOfYear -= 500

    if dayOfYear > 0:
        dayOfYear -= 1

    try:
        dob = datetime.datetime.strptime(f"{year} {dayOfYear}", "%Y %j").date()
        return dob, gender
    except ValueError:
        return None, None

def getValidatedInput(prompt, fieldName, validationType=None):
    while True:
        value = input(prompt).strip()

        if not value:
            print(f"{fieldName} is required. Please enter again.")
            continue

        # Apply validation
        if validationType == "nic":
            if not (
                re.match(r'^\d{9}[VvXx]$', value) or  # Old format: 9 digits + V/X
                re.match(r'^\d{12}$', value)          # New format: 12 digits
            ):
                print(Fore.RED +"Invalid NIC format. Use 9 digits + V/X (e.g., 820149894V) or 12-digit number (e.g., 200012301234).")
                continue

        elif validationType == "dob":
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                print(Fore.RED +"Invalid date format. Use YYYY-MM-DD.")
                continue

        elif validationType == "phone":
            if not re.match(r'^\d{10}$', value):
                print(Fore.RED +"Phone number must be 10 digits.")
                continue

        elif validationType == "email":
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                print(Fore.RED +"Invalid email format.")
                continue

        return value

def confirm_before_saving(summary_data):
    print(Fore.CYAN + "\n📋 Confirm Details Before Saving:")
    for label, value in summary_data.items():
        print(f"{label}: {value}")
    confirm = input("\nDo you want to save this account? (Y/N): ").strip().lower()
    return confirm == 'y'

def search_customer_by(field, value):
    if not os.path.exists(customerDetailsFile):
        print(Fore.RED +"❌ No customer data found.")
        return
    found = False
    with open(customerDetailsFile, 'r') as f:
        for line in f:
            parts = line.strip().split('|')
            if (field == 'nic' and parts[2] == value) or (field == 'phone' and parts[4] == value):
                print(Fore.CYAN + "\n📋 Customer Found:")
                print("Account No :", parts[0])
                print("Name       :", parts[1])
                print("NIC        :", parts[2])
                print("Phone      :", parts[4])
                print("Email      :", parts[5])
                print("Account Type :", parts[8])
                print("Status     :", parts[9] )
                found = True
    if not found:
        print(Fore.RED +"❌ No matching customer found.")
def AccountType():
    while True:
        print(Fore.CYAN + "Select Account Type:")
        print("1. Savings (Interest Eligible)")
        print("2. Current (No Interest)")
        choice = input("Enter 1 or 2: ").strip()
        if choice == '1':
            return "Savings"
        elif choice == '2':
            return "Current"
        else:
            print(Fore.RED + "Invalid selection. Please enter 1 or 2.")
def createAccount(accounts):
    clearScreen()
    print(Fore.CYAN + "\n--- Create New Bank Account ---")

    name = getValidatedInput("Full Name: ", "Name").upper()
    nic = getValidatedInput("NIC/Passport No: ", "NIC/Passport Number", "nic")

    dob, gender = getDobFromNic(nic)
    if not dob:
        print(Fore.RED +"⚠️ Unable to extract DOB from NIC. Please check the format.")
        return

    print(Fore.CYAN + f"✔️ Extracted DOB from NIC: {dob} ({gender})")

    phone = getValidatedInput("Phone Number: ", "Phone Number", "phone")
    email = getValidatedInput("Email Address: ", "Email", "email")
    address = getValidatedInput("Residential Address: ", "Residential Address")
    accountType = AccountType()

    while True:
        try:
            balance = float(input("Initial Deposit Amount (>=0): "))
            if balance < 0:
                print(Fore.RED +"Deposit amount must be 0 or more.")
            else:
                break
        except ValueError:
            print(Fore.RED +"Invalid input. Please enter a numeric amount.")
    summary = {
    "Name": name,
    "NIC": nic,
    "DOB": dob,
    "Phone": phone,
    "Email": email,
    "Address": address,
    "Initial Balance": balance
}
    if not confirm_before_saving(summary):
        print(Fore.RED +"❌ Account creation cancelled.")
        return

    accNo = generateAccountNumber()
    while accNo in accounts:
        accNo = str(int(accNo) + 1)

    username = "user" + accNo
    password = "pass" + accNo

    with open(credentialsFile, 'a') as f:
        f.write(f"{username}:{hash_password(password)}:user\n")

    accounts[accNo] = {
        'name': name,
        'balance': balance,
        'transactions': [f"Account opened with Rs.{balance}"]
    }

    writeAccountDetails(accNo, name, balance)
    writeTransaction(accNo, f"Account opened with Rs.{balance}")

    with open(customerDetailsFile, 'a') as f:
        f.write(f"{accNo}|{name}|{nic}|{dob}|{phone}|{email}|{address}|{gender}|{accountType}|Active\n")

    print(Fore.GREEN +"\n✅ Account Created Successfully!")
    print(Fore.GREEN +"Account Number :", accNo)
    print(Fore.GREEN +"Username       :", username)
    print(Fore.GREEN +"Password       :", password)
    print(Fore.GREEN +"Date of Birth  :", dob)
    print(Fore.GREEN +"Gender         :", gender)
    print(Fore.GREEN + "Account Type   :", accountType)

def readCustomer(role, acc_no=None):
    accNo = input(Fore.CYAN + "Enter Account Number to View: ").strip()
    if role != 'admin' and accNo != acc_no:
        print(Fore.RED + "❌ You can only view your own profile.")
        return
    if accountInactive(accNo):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    found = False
    updatedLines = []

    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            lines = f.readlines()

        with open(customerDetailsFile, 'w') as f:
            for line in lines:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')

                    if parts[-1] == "Inactive":
                        print(Fore.RED +"⚠️ This customer is inactive.")
                        f.write(line)
                        return

                    headers = ["Name", "Value"]
                    data = [
                        ["Account No", parts[0]],
                        ["Name", parts[1]],
                        ["NIC", parts[2]],
                        ["Date of Birth", parts[3]],
                        ["Phone", parts[4]],
                        ["Email", parts[5]],
                        ["Address", parts[6]],
                        ["Gender", parts[7]],
                        ["Account Type", parts[8]],
                        ["Status", parts[9]]
                    ]
                    print(Fore.CYAN + "\n📋 Customer Profile")
                    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
                    found = True

                f.write(line)

    if not found:
        print(Fore.RED +"❌ Customer not found.")

def restoreCustomer():
    accNo = input(Fore.CYAN + "Enter Account Number to Restore: ").strip()
    restored = False
    lines = []

    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            lines = f.readlines()

        with open(customerDetailsFile, 'w') as f:
            for line in lines:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')
                    if parts[-1] == "Active":
                        print(Fore.GREEN +"✅ Customer already active.")
                        f.write(line)
                        continue

                    parts[-1] = "Active"
                    updatedLine = '|'.join(parts) + '\n'
                    f.write(updatedLine)
                    restored = True
                    print(Fore.GREEN +"✅ Customer restored.")
                else:
                    f.write(line)

    if not restored:
        print(Fore.RED +"❌ Account not found or already active.")

def updateCustomer():
    accNo = input(Fore.CYAN + "Enter Account Number to Update: ").strip()
    if accountInactive(accNo):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    updated = False
    lines = []

    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            lines = f.readlines()

        with open(customerDetailsFile, 'w') as f, open("change_log.txt", 'a') as log:
            for line in lines:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')

                    
                    

                    print("\n📋 Current Details:")
                    print("1. Phone   :", parts[4])
                    print("2. Email   :", parts[5])
                    print("3. Address :", parts[6])
                    print("4. Name    :", parts[1])
                    print("5. NIC     :", parts[2])
                    print("0. Cancel Update")

                    choice = input("\nWhich field do you want to update? (1-5): ").strip()

                    if choice == '1':
                        old = parts[4]
                        parts[4] = getValidatedInput("New Phone Number: ", "Phone", "phone")
                        log.write(f"{accNo} - Phone changed from {old} to {parts[4]}\n")
                    elif choice == '2':
                        old = parts[5]
                        parts[5] = getValidatedInput("New Email: ", "Email", "email")
                        log.write(f"{accNo} - Email changed from {old} to {parts[5]}\n")
                    elif choice == '3':
                        old = parts[6]
                        parts[6] = getValidatedInput("New Address: ", "Address")
                        log.write(f"{accNo} - Address changed from {old} to {parts[6]}\n")
                    elif choice == '4':
                        old = parts[1]
                        parts[1] = getValidatedInput("New Full Name: ", "Name").upper()
                        log.write(f"{accNo} - Name changed from {old} to {parts[1]}\n")
                    elif choice == '5':
                        oldNic = parts[2]
                        newNic = getValidatedInput("New NIC: ", "NIC", "nic")
                        newDob, newGender = getDobFromNic(newNic)
                        if not newDob:
                            print(Fore.RED +"⚠️ Invalid NIC. Could not extract DOB.")
                            f.write(line)
                            continue
                        parts[2] = newNic
                        parts[3] = str(newDob)
                        parts[7] = newGender
                        log.write(f"{accNo} - NIC changed from {oldNic} to {newNic}, DOB and Gender recalculated.\n")
                        print("✔️ DOB and Gender updated from NIC.")
                    elif choice == '0':
                        print(Fore.RED +"Update cancelled.")
                        f.write(line)
                        continue
                    else:
                        print(Fore.RED +"Invalid choice. Skipping update.")
                        f.write(line)
                        continue

                    updatedLine = '|'.join(parts) + '\n'
                    f.write(updatedLine)
                    updated = True
                    print(Fore.GREEN +"✅ Customer updated successfully.")
                else:
                    f.write(line)

    if not updated:
        print(Fore.RED +"❌ Account not found.")

def update_multiple_fields(accNo, updates):
    updated = False
    if not os.path.exists(customerDetailsFile):
        print(Fore.RED +"❌ File not found.")
        return
    with open(customerDetailsFile, 'r') as f:
        lines = f.readlines()

    with open(customerDetailsFile, 'w') as f, open(changeLogFile, 'a') as log:
        for line in lines:
            if line.startswith(accNo + "|"):
                parts = line.strip().split('|')
                if parts[-1] == "Inactive":
                    print(Fore.RED +"⚠️ This customer is inactive.")
                    f.write(line)
                    return
                for field, new_value in updates.items():
                    index = field  # e.g. {'1': Phone, '2': Email} -> match index
                    old = parts[int(index)]
                    parts[int(index)] = new_value
                    log.write(f"{accNo} | Field[{index}] changed from {old} to {new_value} at {datetime.datetime.now()}\n")
                f.write('|'.join(parts) + '\n')
                updated = True
            else:
                f.write(line)
    if updated:
        print(Fore.GREEN +"✅ Customer details updated.")
    else:
        print(Fore.RED +"❌ Account not found.")
def soft_delete_customer(accNo):
    confirmed = input("Are you sure you want to mark this customer as inactive? (Y/N): ").strip().lower()
    if confirmed != 'y':
        print(Fore.RED +"❌ Deletion cancelled.")
        return

    reason = input(Fore.CYAN + "Enter reason for deactivation: ").strip()
    deleted = False
    with open(customerDetailsFile, 'r') as f:
        lines = f.readlines()

    with open(customerDetailsFile, 'w') as f, open(deactivationLogFile, 'a') as log:
        for line in lines:
            if line.startswith(accNo + "|"):
                parts = line.strip().split('|')
                if parts[-1] == "Inactive":
                    print(Fore.RED +"⚠️ Already inactive.")
                    f.write(line)
                    continue
                parts[-1] = "Inactive"
                f.write('|'.join(parts) + '\n')
                log.write(f"{accNo} | Deactivated on {datetime.datetime.now()} | Reason: {reason}\n")
                deleted = True
                print(Fore.CYAN + "🟡 Customer marked as Inactive.")
            else:
                f.write(line)
    if not deleted:
        print(Fore.RED +"❌ Account not found.")

def deleteCustomer():
    accNo = input(Fore.CYAN + "Enter Account Number to Inactive: ").strip()
    deleted = False
    lines = []

    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            lines = f.readlines()

        with open(customerDetailsFile, 'w') as f:
            for line in lines:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')
                    if parts[-1] == "Inactive":
                        print(Fore.RED +"⚠️ Customer already inactive.")
                        f.write(line)
                        continue

                    parts[-1] = "Inactive"  # Replace status
                    updatedLine = '|'.join(parts) + '\n'
                    f.write(updatedLine)
                    deleted = True
                    print(Fore.CYAN + "🟡 Customer marked as Inactive.")
                else:
                    f.write(line)

    if not deleted:
        print(Fore.RED +"❌ Account not found.")


# ---------------- Deposit ------------------
def deposit(accounts, role, acc_no=None):
    entered = input(Fore.CYAN + "Enter account number: ").strip()
    if role != 'admin' and entered != acc_no:
        print(Fore.RED + "❌ You can only deposit into your own account.")
        return
    if accountInactive(entered):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    if entered not in accounts:
        print(Fore.RED + "Account not found.")
        return

    try:
        amount = float(input(Fore.CYAN + "Amount to deposit: "))
        if amount <= 0:
            print(Fore.RED +"Deposit must be more than 0.")
            return
    except ValueError:
        print(Fore.RED +"Invalid amount.")
        return

    accounts[entered]["balance"] += amount
    txn = f"Deposited Rs.{amount} on {datetime.datetime.now()}"
    accounts[entered]["transactions"].append(txn)
    writeTransaction(entered, txn)
    print(f"Rs.{amount} successfully deposited into account {entered}.")

# ---------------- Withdraw ------------------
def withdraw(accounts, role, acc_no=None):
    entered = input(Fore.CYAN + "Enter account number: ").strip()
    if role != 'admin' and entered != acc_no:
        print(Fore.RED + "❌ You can only withdraw from your own account.")
        return
    if accountInactive(entered):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    if entered not in accounts:
        print(Fore.RED + "Account not found.")
        return

    try:
        amount = float(input(Fore.CYAN + "Amount to withdraw: "))
        if amount <= 0:
            print(Fore.RED +"Invalid amount.")
            return
    except ValueError:
        print(Fore.RED +"Please enter a number.")
        return

    if amount > accounts[entered]["balance"]:
        print(Fore.RED +"Not enough balance.")
        return

    accounts[entered]["balance"] -= amount
    txn = f"Withdrew Rs.{amount} on {datetime.datetime.now()}"
    accounts[entered]["transactions"].append(txn)
    writeTransaction(entered, txn)
    print("Withdrawal successful!")

# ---------------- Check Balance ------------------
def checkBalance(accounts, role, acc_no=None):
    entered = input(Fore.CYAN + "Enter account number: ").strip()
    if role != 'admin' and entered != acc_no:
        print(Fore.RED + "❌ You can only check your own balance.")
        return
    if accountInactive(entered):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    if entered in accounts:
        print(Fore.GREEN + "Your balance is: Rs.", accounts[entered]["balance"])
    else:
        print(Fore.RED + "Account not found.")

# ---------------- Transaction History ------------------
def viewTransactions(accounts, role, acc_no=None):
    entered = input(Fore.CYAN + "Enter account number: ").strip()
    if role != 'admin' and entered != acc_no:
        print(Fore.RED + "❌ You can only view your own transactions.")
        return
    if accountInactive(entered):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return

    if entered in accounts:
        print(Fore.CYAN + f"\n📄 Transaction History for Account {entered}:\n")
        transactions = accounts[entered]["transactions"]
        if not transactions:
            print(Fore.RED +"No transactions found.")
            return
        table = []
        for idx, txn in enumerate(transactions, 1):
            table.append([idx, txn])

        print(tabulate(table, headers=["No", "Transaction Details"], tablefmt="fancy_grid"))
    else:
        print(Fore.RED +"❌ Account not found.")

# ---------------- Transfer Money ------------------
def transferMoney(accounts, role, acc_no=None):
    fromAcc = input(Fore.CYAN + "Sender Account Number: ").strip()
    if role == "user" and fromAcc != acc_no:
        print(Fore.RED + "⚠️ You are only allowed to transfer from your own account.")
        return
    if accountInactive(fromAcc):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    toAcc = input(Fore.CYAN + "Receiver Account Number: ").strip()
    if accountInactive(toAcc):
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return
    if fromAcc not in accounts or toAcc not in accounts:
        print(Fore.RED +"One or both accounts not found.")
        return
    try:
        amount = float(input(Fore.CYAN + "Amount to transfer: "))
        if amount <= 0 or amount > accounts[fromAcc]['balance']:
            print(Fore.RED +"Invalid amount.")
            return
    except:
        print(Fore.RED +"Invalid input.")
        return

    accounts[fromAcc]['balance'] -= amount
    accounts[toAcc]['balance'] += amount
    t1 = f"Transferred Rs.{amount} to {toAcc} on {datetime.datetime.now()}"
    t2 = f"Received Rs.{amount} from {fromAcc} on {datetime.datetime.now()}"
    accounts[fromAcc]['transactions'].append(t1)
    accounts[toAcc]['transactions'].append(t2)
    writeTransaction(fromAcc, t1)
    writeTransaction(toAcc, t2)
    print("Transfer complete.")


def applyMonthlyInterest(accounts):
    interestRateAnnual = 0.03
    interestRateMonthly = interestRateAnnual / 12
    today = datetime.date.today()
    logFile = 'interestlog.txt'
    alreadyApplied = set()

    # Load applied interest log
    if os.path.exists(logFile):
        with open(logFile, 'r') as log:
            for line in log:
                accNo, dateStr, *_ = line.strip().split('|')
                dateObj = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
                if dateObj.month == today.month and dateObj.year == today.year:
                    alreadyApplied.add(accNo)

    if not os.path.exists(customerDetailsFile):
        return

    with open(customerDetailsFile, 'r') as customerFile:
        lines = customerFile.readlines()

    with open(customerDetailsFile, 'w') as customerFile:
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) < 10:
                customerFile.write(line)
                continue

            accNo, name, accountType, status = parts[0], parts[1], parts[8], parts[9]

            if accountType == "Savings" and status == "Active" and accNo in accounts and accNo not in alreadyApplied:
                balance = accounts[accNo]['balance']
                interestAmount = round(balance * interestRateMonthly, 2)
                accounts[accNo]['balance'] += interestAmount

                updatedLine = '|'.join(parts) + '\n'
                customerFile.write(updatedLine)

                writeAccountDetails(accNo, name, accounts[accNo]['balance'])

                transactionMessage = f"Monthly Interest Rs.{interestAmount} on {today}"
                accounts[accNo]['transactions'].append(transactionMessage)
                writeTransaction(accNo, transactionMessage)

                with open(logFile, 'a') as log:
                    log.write(f"{accNo}|{today}|{interestAmount}|{interestRateMonthly * 100:.2f}%\n")
            else:
                customerFile.write(line)



def viewInterestHistory():
    logFile = 'interestlog.txt'
    if not os.path.exists(logFile):
        print(Fore.YELLOW + "⚠️ No interest records found.")
        return

    interestRecords = []
    with open(logFile, 'r') as log:
        for line in log:
            parts = line.strip().split('|')
            if len(parts) == 4:
                accNo, date, amount, rate = parts
                interestRecords.append([accNo, date, f"Rs.{amount}", rate])

    if interestRecords:
        print(Fore.GREEN + "\n📋 Interest Applied History:")
        print(tabulate(interestRecords, headers=["Account No", "Date", "Interest Amount", "Rate"], tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "⚠️ No interest entries to display.")

# ---------------- Admin Menu ------------------
def adminMenu(accounts, role):
    input(Fore.YELLOW + "\nPress Enter to continue...")
    while True:
        clearScreen()
        menu = [
            ["1", "Create Account"],
            ["2", "View Customer Profile"],
            ["3", "Update Customer Details"],
            ["4", "Delete Customer"],
            ["5", "Deposit"],
            ["6", "Withdraw"],
            ["7", "Check Balance"],
            ["8", "Transaction History"],
            ["9", "Transfer Money"],
            ["10", "Restore Inactive Customer"],
            ["11", "View Interest History"],
            ["0", "Logout"]
        ]
        print(Fore.CYAN + "\n--- Admin Menu ---")
        print(tabulate(menu, headers=["Option", "Description"], tablefmt="fancy_grid"))
        choice = input("Selec an Option(0-10): ")
        if choice == '1':
            createAccount(accounts)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '2':
            readCustomer(role)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '3':
            updateCustomer()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '4':
            deleteCustomer()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '5':
            deposit(accounts, role)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '6':
            withdraw(accounts, role)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '7':
            checkBalance(accounts, role)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '8':
            viewTransactions(accounts, role)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '9':
            transferMoney(accounts, role)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '10':
            restoreCustomer()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '11':
            viewInterestHistory()
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '0':
            break
        else:
            print("Invalid choice.")
            input(Fore.YELLOW + "\nPress Enter to continue...")


# ---------------- User Menu ------------------
def userMenu(accounts, role, acc_no):
    input(Fore.YELLOW + "\nPress Enter to continue...")

    while True:
        clearScreen()
        menu = [
            ["1", "User Profile"],
            ["2", "Deposit"],
            ["3", "Withdraw"],
            ["4", "Check Balance"],
            ["5", "Transaction History"],
            ["6", "Transfer Money"],
            ["0", "Logout"]
        ]
        print(Fore.CYAN + "\n=== User Menu ===")
        print(tabulate(menu, headers=["Option", "Description"], tablefmt="fancy_grid"))
        
        choice = input("Select an option(0-6): ")
        if choice == '1':
            readCustomer(role, acc_no)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '2':
            deposit(accounts, role, acc_no)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '3':
            withdraw(accounts, role, acc_no)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '4':
            checkBalance(accounts, role, acc_no)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '5':
            viewTransactions(accounts, role, acc_no)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '6':
            transferMoney(accounts, role, acc_no)
            input(Fore.YELLOW + "\nPress Enter to continue...")
        elif choice == '0':
            break
        else:
            print("Invalid choice.")
            input(Fore.YELLOW + "\nPress Enter to continue...")

# ---------------- Start Application ------------------
def startMenu():
    
    while True:
        input(Fore.YELLOW + "\nPress Enter to continue...")
        clearScreen()
        accounts = loadData()
        applyMonthlyInterest(accounts)
        credentials = readCredentials()
        result = login(credentials)

        if result:
            role, acc_no = result
            if role == 'admin':
                adminMenu(accounts, role)
            elif role == 'user':
                userMenu(accounts, role, acc_no)
        else:
            print(Fore.RED + "Access denied.")

        print(Fore.RED +"\n🔒 You have been logged out.")
        print(Fore.CYAN + "Press ENTER to login again or type 0 to exit.")
        choice = input(">> ").strip()
        if choice == '0':
            print(Fore.CYAN + "Thank you for using Mini Banking App. Goodbye!")
            break

startMenu()
