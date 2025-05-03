import getpass
import datetime
import os
import re

# ---------------- File Names ------------------
accountsFile = 'AccountDetails.txt'
transactionsFile = 'transactions.txt'
credentialsFile = 'credentials.txt'
accountNumFile = 'account_numbers.txt'
customerDetailsFile = 'CustomerProfiles.txt'

# ---------------- Load Data ------------------
def loadData():
    accounts = {}
    if os.path.exists(accountsFile):
        with open(accountsFile, 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                accNo = parts[0]
                name = parts[1]
                balance = float(parts[2])
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
    print("\n=== Login ===")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")

    if username in credentials and credentials[username]['password'] == password:
        role = credentials[username]['role']

        if role == 'user':
            accNo = username.replace('user', '')
            if os.path.exists(customerDetailsFile):
                with open(customerDetailsFile, 'r') as f:
                    for line in f:
                        if line.startswith(accNo + "|"):
                            parts = line.strip().split('|')
                            if len(parts) == 8:
                                parts.append("Active")
                            if parts[-1] == "Inactive":
                                print("❌ Your account is inactive. Contact the bank.")
                                return None
                            break

        print(f"Login successful! Logged in as {role.capitalize()}.")
        return role
    else:
        print("Login failed. Invalid username or password.")
        return None


# ---------------- Create Account ------------------

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
                print("Invalid NIC format. Use 9 digits + V/X (e.g., 820149894V) or 12-digit number (e.g., 200012301234).")
                continue

        elif validationType == "dob":
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                print("Invalid date format. Use YYYY-MM-DD.")
                continue

        elif validationType == "phone":
            if not re.match(r'^\d{10}$', value):
                print("Phone number must be 10 digits.")
                continue

        elif validationType == "email":
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
                print("Invalid email format.")
                continue

        return value


def createAccount(accounts):
    print("\n--- Create New Bank Account ---")

    name = getValidatedInput("Full Name: ", "Name").upper()
    nic = getValidatedInput("NIC/Passport No: ", "NIC/Passport Number", "nic")

    dob, gender = getDobFromNic(nic)
    if not dob:
        print("⚠️ Unable to extract DOB from NIC. Please check the format.")
        return

    print(f"✔️ Extracted DOB from NIC: {dob} ({gender})")

    phone = getValidatedInput("Phone Number: ", "Phone Number", "phone")
    email = getValidatedInput("Email Address: ", "Email", "email")
    address = getValidatedInput("Residential Address: ", "Residential Address")

    while True:
        try:
            balance = float(input("Initial Deposit Amount (>=0): "))
            if balance < 0:
                print("Deposit amount must be 0 or more.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a numeric amount.")

    accNo = generateAccountNumber()
    while accNo in accounts:
        accNo = str(int(accNo) + 1)

    username = "user" + accNo
    password = "pass" + accNo

    with open(credentialsFile, 'a') as f:
        f.write(username + ':' + password + ':user\n')

    accounts[accNo] = {
        'name': name,
        'balance': balance,
        'transactions': [f"Account opened with Rs.{balance}"]
    }

    writeAccountDetails(accNo, name, balance)
    writeTransaction(accNo, f"Account opened with Rs.{balance}")

    with open(customerDetailsFile, 'a') as f:
        f.write(f"{accNo}|{name}|{nic}|{dob}|{phone}|{email}|{address}|{gender}|Active\n")

    print("\n✅ Account Created Successfully!")
    print("Account Number :", accNo)
    print("Username       :", username)
    print("Password       :", password)
    print("Date of Birth  :", dob)
    print("Gender         :", gender)

def readCustomer():
    accNo = input("Enter Account Number to View: ").strip()
    found = False
    updatedLines = []

    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            lines = f.readlines()

        with open(customerDetailsFile, 'w') as f:
            for line in lines:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')

                    if len(parts) == 8:
                        parts.append("Active")
                        line = '|'.join(parts) + '\n'

                    if parts[-1] == "Inactive":
                        print("⚠️ This customer is inactive.")
                        f.write(line)
                        return

                    print("\n📋 Customer Profile")
                    print(f"Account No     : {parts[0]}")
                    print(f"Name           : {parts[1]}")
                    print(f"NIC            : {parts[2]}")
                    print(f"Date of Birth  : {parts[3]}")
                    print(f"Phone          : {parts[4]}")
                    print(f"Email          : {parts[5]}")
                    print(f"Address        : {parts[6]}")
                    print(f"Gender         : {parts[7]}")
                    print(f"Status         : {parts[8]}")
                    found = True

                f.write(line)

    if not found:
        print("❌ Customer not found.")

def restoreCustomer():
    accNo = input("Enter Account Number to Restore: ").strip()
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
                        print("✅ Customer already active.")
                        f.write(line)
                        continue

                    parts[-1] = "Active"
                    updatedLine = '|'.join(parts) + '\n'
                    f.write(updatedLine)
                    restored = True
                    print("✅ Customer restored.")
                else:
                    f.write(line)

    if not restored:
        print("❌ Account not found or already active.")

def updateCustomer():
    accNo = input("Enter Account Number to Update: ").strip()
    updated = False
    lines = []

    if os.path.exists(customerDetailsFile):
        with open(customerDetailsFile, 'r') as f:
            lines = f.readlines()

        with open(customerDetailsFile, 'w') as f, open("change_log.txt", 'a') as log:
            for line in lines:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')

                    # Ensure old data gets status
                    if len(parts) == 8:
                        parts.append("Active")

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
                            print("⚠️ Invalid NIC. Could not extract DOB.")
                            f.write(line)
                            continue
                        parts[2] = newNic
                        parts[3] = str(newDob)
                        parts[7] = newGender
                        log.write(f"{accNo} - NIC changed from {oldNic} to {newNic}, DOB and Gender recalculated.\n")
                        print("✔️ DOB and Gender updated from NIC.")
                    elif choice == '0':
                        print("Update cancelled.")
                        f.write(line)
                        continue
                    else:
                        print("Invalid choice. Skipping update.")
                        f.write(line)
                        continue

                    updatedLine = '|'.join(parts) + '\n'
                    f.write(updatedLine)
                    updated = True
                    print("✅ Customer updated successfully.")
                else:
                    f.write(line)

    if not updated:
        print("❌ Account not found.")

def deleteCustomer():
    accNo = input("Enter Account Number to Inactive: ").strip()
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
                        print("⚠️ Customer already inactive.")
                        f.write(line)
                        continue

                    parts[-1] = "Inactive"  # Replace status
                    updatedLine = '|'.join(parts) + '\n'
                    f.write(updatedLine)
                    deleted = True
                    print("🟡 Customer marked as Inactive.")
                else:
                    f.write(line)

    if not deleted:
        print("❌ Account not found.")


# ---------------- Deposit ------------------
def deposit(accounts):
    accNo = input("Enter account number: ").strip()
    if accNo not in accounts:
        print("Account not found.")
        return

    try:
        amount = float(input("Amount to deposit: "))
        if amount <= 0:
            print("Deposit must be more than 0.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    accounts[accNo]["balance"] += amount
    txn = f"Deposited Rs.{amount} on {datetime.datetime.now()}"
    accounts[accNo]["transactions"].append(txn)
    writeTransaction(accNo, txn)
    print(f"Rs.{amount} successfully deposited into account {accNo}.")

# ---------------- Withdraw ------------------
def withdraw(accounts):
    accNo = input("Enter account number: ").strip()
    if accNo not in accounts:
        print("Account not found.")
        return

    try:
        amount = float(input("Amount to withdraw: "))
        if amount <= 0:
            print("Invalid amount.")
            return
    except ValueError:
        print("Please enter a number.")
        return

    if amount > accounts[accNo]["balance"]:
        print("Not enough balance.")
        return

    accounts[accNo]["balance"] -= amount
    txn = f"Withdrew Rs.{amount} on {datetime.datetime.now()}"
    accounts[accNo]["transactions"].append(txn)
    writeTransaction(accNo, txn)
    print("Withdrawal successful!")

# ---------------- Check Balance ------------------
def checkBalance(accounts):
    accNo = input("Enter account number: ").strip()
    if accNo in accounts:
        print("Your balance is: Rs.", accounts[accNo]["balance"])
    else:
        print("Account not found.")

# ---------------- Transaction History ------------------
def viewTransactions(accounts):
    accNo = input("Enter account number: ").strip()
    if accNo in accounts:
        print("Transaction History:")
        for txn in accounts[accNo]["transactions"]:
            print("-", txn)
    else:
        print("Account not found.")

# ---------------- Transfer Money ------------------
def transferMoney(accounts):
    fromAcc = input("Sender Account Number: ").strip()
    toAcc = input("Receiver Account Number: ").strip()
    if fromAcc not in accounts or toAcc not in accounts:
        print("One or both accounts not found.")
        return
    try:
        amount = float(input("Amount to transfer: "))
        if amount <= 0 or amount > accounts[fromAcc]['balance']:
            print("Invalid amount.")
            return
    except:
        print("Invalid input.")
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

# ---------------- Admin Menu ------------------
def adminMenu(accounts):
    while True:
        print("\n--- Admin Menu ---")
        print("1. Create Account")
        print("2. View Customer Profile")
        print("3. Update Customer Details")
        print("4. Delete Customer")
        print("5. Deposit")
        print("6. Withdraw")
        print("7. Check Balance")
        print("8. Transaction History")
        print("9. Transfer Money")
        print("10. Restore Soft-Deleted Customer")
        print("0. Logout")

        choice = input("Choice: ")
        if choice == '1':
            createAccount(accounts)
        elif choice == '2':
            readCustomer()
        elif choice == '3':
            updateCustomer()
        elif choice == '4':
            deleteCustomer()
        elif choice == '5':
            deposit(accounts)
        elif choice == '6':
            withdraw(accounts)
        elif choice == '7':
            checkBalance(accounts)
        elif choice == '8':
            viewTransactions(accounts)
        elif choice == '9':
            transferMoney(accounts)
        elif choice == '10':
            restoreCustomer()
        elif choice == '0':
            break
        else:
            print("Invalid choice.")


# ---------------- User Menu ------------------
def userMenu(accounts):
    while True:
        print("\n--- User Menu ---")
        print("1. User Profile")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Check Balance")
        print("5. Transaction History")
        print("6. Transfer Money")
        print("0. Logout")

        choice = input("Choice: ")
        if choice == '1':
            readCustomer()
        elif choice == '2':
            deposit(accounts)
        elif choice == '3':
            withdraw(accounts)
        elif choice == '4':
            checkBalance(accounts)
        elif choice == '5':
            viewTransactions(accounts)
        elif choice == '6':
            transferMoney(accounts)
        elif choice == '0':
            break
        else:
            print("Invalid choice.")

# ---------------- Start Application ------------------
def startMenu():
    while True:
        accounts = loadData()
        credentials = readCredentials()
        role = login(credentials)

        if role == 'admin':
            adminMenu(accounts)
        elif role == 'user':
            userMenu(accounts)
        else:
            print("Access denied.")

        print("\n🔒 You have been logged out.")
        print("Press ENTER to login again or type 0 to exit.")
        choice = input(">> ").strip()
        if choice == '0':
            print("Thank you for using Mini Banking App. Goodbye!")
            break

startMenu()
