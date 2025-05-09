"""
UNICOM TIC Banking System 
----------------------------------------------
Developed By: Abdul Baasith

This program is a basic terminal-based banking system built using Python.
It supports user and admin login, account creation, balance check,
deposits, withdrawals, transfers, and automatic interest calculation 
for savings accounts.

The system stores data in text files .

- AccountDetails.txt        - Stores account number, customer name, and balance
- CustomerProfiles.txt      - Stores full customer details including NIC and status
- transactions.txt          - Stores all deposit, withdrawal, transfer, and interest transactions
- credentials.txt           - Stores usernames, hashed passwords, and roles (admin/user)
- change_log.txt            - Keeps a log of any updates made to customer details
- deactivation_log.txt      - Logs when accounts are marked inactive and why
- interestlog.txt           - Records when monthly interest was given to which account

Python Modules 
- pwinput   - Hides the password when typing in the terminal
- bcrypt    - Hashes passwords securely so they are not saved in plain text
- datetime  - Handles date and time (used for DOB, transactions, interest dates)
- os        - Allows clearing the terminal screen based on OS
- re        - Used for pattern matching (e.g., validating NIC, email, phone)
- tabulate  - Prints data in neat table format ( customer profile, transactions)
- colorama  - Adds color to terminal text to highlight errors, success, etc.

"""


import pwinput
import bcrypt
from tabulate import tabulate
import datetime
import os
import re
from colorama import Fore, Style, init
init(autoreset=True)

'''
This function converts a user's plain password into a hashed version using bcrypt,
 which adds a salt to protect against rainbow table attacks.
It ensures stored passwords are not readable even if the file is exposed.
'''
def hash_password(password):

    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


'''
Uses bcrypt to compare the user’s entered password with the stored hash.
 This prevents exposing plain passwords and ensures authentication security.
'''
def check_password(password, hashed):

    return bcrypt.checkpw(password.encode(), hashed.encode())


'''
Clears the console screen for both Windows and Unix systems 
to keep the UI clean and readable after each operation.
'''
def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')


'''
Reads the CustomerProfiles.txt file and 
returns True if the account’s status is marked as 'Inactive', 
which is used to block operations on closed accounts.
'''
def accountInactive(accNo):
    try:
        with open('CustomerProfiles.txt', 'r') as f:
            for line in f:
                if line.startswith(accNo + "|"):
                    parts = line.strip().split('|')
                    return parts[-1] == "Inactive"
    except FileNotFoundError:
        return False
    return False




'''
Loads all account basic details into a dictionary 
so in-memory operations (like deposit/withdraw) 
can be handled efficiently.
'''
def firstGetAccountsInfo():
    accounts = {}
    try:
        with open('AccountDetails.txt', 'r') as f:
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
    except FileNotFoundError:
        return {} # File doesn't exist — returning the empty dict
    except Exception as e:
        print(f"⚠️ Error reading AccountDetails.txt: {e}")
        return {}
    return accounts


'''
Attaches each transaction string to its corresponding account in memory,
 using account numbers as keys
'''
def firstGetTransactionsInto(accounts):
    try:
        with open('transactions.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) != 2:
                    continue  # Skip malformed lines
                accNo, txn = parts
                if accNo in accounts:
                    accounts[accNo]['transactions'].append(txn)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"⚠️ Error reading transactions.txt: {e}")


'''
Combines account info and transactions to prepare 
the system for real-time usage after login.
'''
def firstReadAllData():
    try:
        accounts = firstGetAccountsInfo()
        firstGetTransactionsInto(accounts)
        return accounts
    except Exception as e:
        print(f"⚠️ Failed to load account data: {e}")
        return {}



'''
Finds the highest existing account number in the file 
and increments it by 1 to ensure each new account is unique.
'''
def generateAccountNumber():
    highest = 2003  

    try:
        with open("AccountDetails.txt", 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 1:
                    accNo = parts[0]
                    if accNo.isdigit():
                        accNo_int = int(accNo)
                        if accNo_int > highest:
                            highest = accNo_int
    except FileNotFoundError:
        pass  
    except Exception as e:
        print(Fore.RED + "⚠️ Error reading account file: " + str(e))

    next_acc_no = highest + 1
    return str(next_acc_no)






'''
Writes the account number, name, and balance to the AccountDetails.txt file,
ensuring persistent storage of new accounts or updated balances.
'''
def writeAccountDetails(accNo, name, balance):
    try:
        with open("AccountDetails.txt", 'a') as f:
            f.write(accNo + '|' + name + '|' + str(balance) + '\n')
    except Exception as e:
        print(f"❌ Error writing account details for {accNo}: {e}")



'''
Saves each transaction message with the account number to maintain a permanent audit trail.
'''
def writeTransaction(accNo, txn):
    try:
        with open("transactions.txt", 'a') as f:
            f.write(accNo + '|' + txn + '\n')
    except Exception as e:
        print(Fore.RED + f"❌ Failed to write transaction: {e}")



'''
Parses the credentials.txt file and stores the data 
in a dictionary for fast username lookup during login
'''
def readCredentials():
    credentials = {}
    try:
        with open("credentials.txt", 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 3:
                    username, password, role = parts
                    credentials[username] = {'password': password, 'role': role}
    except FileNotFoundError:
        print(Fore.YELLOW + f"⚠️ Credentials file '{"credentials.txt"}' not found. Proceeding with empty credentials.")
    except Exception as e:
        print(Fore.RED + f"❌ Error reading credentials: {e}")
    return credentials



'''
Authenticates users by matching entered credentials, determines their role,
 and returns account number if user is not an admin.
'''
def login(credentials):
    print(Fore.GREEN+"\t___________________________________________________________________________________")
    print(Fore.GREEN+"\t|                                                                                  |")
    print(Fore.GREEN+"\t|          ================= Welcom To Unicom Tic Bank  ==================         |")
    print(Fore.GREEN+"\t|                                                                                  |")
    print(Fore.GREEN+"\t___________________________________________________________________________________")
    print("")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|                 ==================== LOGIN ====================                  |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|___________________________________________________________________________________")
    print("")
    username = input("\t\t\t\tUsername: ").strip()
    password = pwinput.pwinput("\t\t\t\tPassword: ").strip()

    if username in credentials and check_password(password, credentials[username]['password']):
        role = credentials[username]['role']

        if role == 'user':
            accNo = username.replace('user', '')
            try:
                with open('CustomerProfiles.txt', 'r') as f:
                    for line in f:
                        if line.startswith(accNo + "|"):
                            parts = line.strip().split('|')
                            if len(parts) == 9:
                                parts.append("Active")  
                            if parts[-1] == "Inactive":
                                print(Fore.RED + "❌ Your account is inactive. Contact the bank.")
                                return None
                            break
            except FileNotFoundError:
                print(Fore.RED + f"\n❌ Customer file '{'CustomerProfiles.txt'}' not found.")
                return None
            except Exception as e:
                print(Fore.RED + f"\n❌ Error accessing customer file: {e}")
                return None

            print(Fore.GREEN + f"\nLogin successful! Logged in as User.")
            return role, accNo

        print(Fore.GREEN + f"\nLogin successful! Logged in as Admin.")
        return role, None
    else:
        print(Fore.RED + "\nLogin failed. Invalid username or password.")
        return None





'''
Analyzes the NIC number (old or new format) to calculate date of birth and determine gender 
using logic based on day-of-year encoding.
'''
def getDobFromNic(nic):
    try:
        if re.match(r'^\d{9}[VvXx]$', nic):  # Old NIC
            year = 1900 + int(nic[:2])
            day_of_year = int(nic[2:5])
        elif re.match(r'^\d{12}$', nic):  # New NIC
            year = int(nic[:4])
            day_of_year = int(nic[4:7])
        else:
            return None, None

        gender = "Female" if day_of_year > 500 else "Male"
        if day_of_year > 500:
            day_of_year -= 500
        if day_of_year > 0:
            day_of_year -= 2

        is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        month_days = [31, 29 if is_leap else 28, 31, 30, 31, 30,
                      31, 31, 30, 31, 30, 31]

        total = 0
        i = 0
        while i < len(month_days):
            if day_of_year < total + month_days[i]:
                month = i + 1
                day = day_of_year - total + 1
                dob = datetime.date(year, month, day)
                return dob, gender
            total += month_days[i]
            i += 1

        return None, None

    except Exception as e:
        
        print(f"[Error] Failed to parse NIC: {nic}, reason: {e}")
        return None, None


'''
Checks if input values match required formats (NIC, phone, email). 
If not, it prompts user to enter valid data again

'''
def getValidatedInput(prompt, fieldName, validationType=None):
    while True:
        value = input(prompt).strip()

        if value == "":
            print(Fore.RED + f"{fieldName} is required. Please enter again.")
            continue

        try:
            if validationType == "nic":
                old_nic = re.fullmatch(r'\d{9}[VvXx]', value)
                new_nic = re.fullmatch(r'\d{12}', value)

                if type(old_nic) != re.Match and type(new_nic) != re.Match:
                    raise ValueError("Invalid NIC format. Use 9 digits + V/X or 12-digit number.")

            elif validationType == "dob":
                
                datetime.datetime.strptime(value, "%Y-%m-%d")

            elif validationType == "phone":
                phone_check = re.fullmatch(r'\d{10}', value)
                if type(phone_check) != re.Match:
                    raise ValueError("Phone number must be exactly 10 digits.")

            elif validationType == "email":
                email_check = re.fullmatch(r'^[\w\.-]+@[\w\.-]+\.\w+$', value)
                if type(email_check) != re.Match:
                    raise ValueError("Invalid email format.")

            return value  

        except ValueError as ve:
            print(Fore.RED + f"❌ {ve}")
        except Exception as e:
            print(Fore.RED + f"⚠️ Unexpected error during validation: {e}")



'''
Shows all collected account data to the user 
and confirms if they want to proceed with saving it to files.
'''
def confirmBeforeSaving(summaryData):
    try:
        print(Fore.CYAN + "\n📋 Confirm Details Before Saving:")
        for label, value in summaryData.items():
            print(f"{label}: {value}")

        while True:
            confirm = input("\nDo you want to save this account? (Y/N): ").strip().lower()
            if confirm == "y" or confirm == "yes":
                return True
            elif confirm == "n" or confirm == "no":
                print(Fore.RED + "❌ Account creation cancelled by user.")
                return False
            else:
                print(Fore.YELLOW + "⚠️ Please enter 'Y' or 'N' only.")
    except Exception as e:
        print(Fore.RED + f"⚠️ Unexpected error occurred during confirmation: {e}")
        return False


'''
Scans the CustomerProfiles.txt for a matching NIC or phone number 
and displays associated customer details
'''
def searchCustomerBy(field, value):
    try:
        found = False
        with open('CustomerProfiles.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('|')

                if field == "nic":
                    if parts[2] == value:
                        print(Fore.CYAN + "\n📋 Customer Found:")
                        print("Account No  :", parts[0])
                        print("Name        :", parts[1])
                        print("NIC         :", parts[2])
                        print("Phone       :", parts[4])
                        print("Email       :", parts[5])
                        print("Account Type:", parts[8])
                        print("Status      :", parts[9])
                        found = True

                if field == "phone":
                    if parts[4] == value:
                        print(Fore.CYAN + "\n📋 Customer Found:")
                        print("Account No  :", parts[0])
                        print("Name        :", parts[1])
                        print("NIC         :", parts[2])
                        print("Phone       :", parts[4])
                        print("Email       :", parts[5])
                        print("Account Type:", parts[8])
                        print("Status      :", parts[9])
                        found = True

        if found == False:
            print(Fore.RED + "❌ No matching customer found.")
    except FileNotFoundError:
        print(Fore.RED + "❌ Customer data file not found.")
    except IndexError:
        print(Fore.RED + "⚠️ Data format issue in customer file.")
    except Exception as e:
        print(Fore.RED + f"⚠️ Unexpected error occurred: {e}")


'''
Prompts the user to choose an account type, 
which determines whether interest will be applied.
'''
def AccountType():
    while True:
        try:
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
        except Exception as e:
            print(Fore.RED + f"⚠️ An unexpected error occurred: {e}")


'''
Collects user details, validates input, extracts DOB from NIC, 
writes all account and profile info to respective files, 
and generates credentials.
'''
def createAccount(accounts):
    clearScreen()
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t|          ================= Create New Bank Account ==================            |")
    print(Fore.CYAN+"\t|                                                                                  |")
    print(Fore.CYAN+"\t___________________________________________________________________________________")
    print("")

    try:
        name = getValidatedInput("\t\t\t\tFull Name: ", "Name").upper()
        nic = getValidatedInput("\t\t\t\tNIC/Passport No: ", "NIC/Passport Number", "nic")

        dob, gender = getDobFromNic(nic)

        if dob == None:
            print(Fore.RED + "⚠️ Unable to extract DOB from NIC. Please check the format.")
            return

        print(Fore.CYAN + f"\t\t\t\t✔️ Extracted DOB from NIC: {dob} ({gender})")

        phone = getValidatedInput("\t\t\t\tPhone Number: ", "Phone Number", "phone")
        email = getValidatedInput("\t\t\t\tEmail Address: ", "Email", "email")
        address = getValidatedInput("\t\t\t\tResidential Address: ", "Residential Address")
        accountType = AccountType()

        while True:
            try:
                balance = float(input("Initial Deposit Amount (>=0): "))
                if balance < 0:
                    print(Fore.RED + "Deposit amount must be 0 or more.")
                else:
                    break
            except ValueError:
                print(Fore.RED + "Invalid input. Please enter a numeric amount.")

        summary = {
            "Name": name,
            "NIC": nic,
            "DOB": dob,
            "Phone": phone,
            "Email": email,
            "Address": address,
            "Initial Balance": balance
        }

        confirm = confirmBeforeSaving(summary)
        if confirm == False:
            print(Fore.RED + "❌ Account creation cancelled.")
            return

        accNo = generateAccountNumber()
        while accNo in accounts:
            accNo = str(int(accNo) + 1)

        username = "user" + accNo
        password = "pass" + accNo

        try:
            with open("credentials.txt", 'a') as f:
                f.write(f"{username}:{hash_password(password)}:user\n")

            accounts[accNo] = {
                'name': name,
                'balance': balance,
                'transactions': [f"Account opened with Rs.{balance}"]
            }

            writeAccountDetails(accNo, name, balance)
            writeTransaction(accNo, f"Account opened with Rs.{balance}")

            with open('CustomerProfiles.txt', 'a') as f:
                f.write(f"{accNo}|{name}|{nic}|{dob}|{phone}|{email}|{address}|{gender}|{accountType}|Active\n")

        except Exception as e:
            print(Fore.RED + f"❌ Failed to save account: {e}")
            return

        print(Fore.GREEN + "\n✅ Account Created Successfully!")
        print(Fore.GREEN + "Account Number :", accNo)
        print(Fore.GREEN + "Username       :", username)
        print(Fore.GREEN + "Password       :", password)
        print(Fore.GREEN + "Date of Birth  :", dob)
        print(Fore.GREEN + "Gender         :", gender)
        print(Fore.GREEN + "Account Type   :", accountType)

    except Exception as e:
        print(Fore.RED + f"❌ Unexpected error occurred: {e}")


'''
Reads the CustomerProfiles.txt 
and formats the matched customer record using a styled table output.
'''
def readCustomer(role, acc_no=None):
    accNo = input(Fore.CYAN + "Enter Account Number to View: ").strip()

    if role != 'admin' and accNo != acc_no:
        print(Fore.RED + "❌ You can only view your own profile.")
        return

    if accountInactive(accNo) == True:
        print(Fore.RED + "❌ Cannot access an inactive account.")
        return

    found = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + "❌ Customer profile file not found.")
        return
    except Exception as e:
        print(Fore.RED + f"❌ Error reading customer file: {e}")
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        status = parts[9]
                        if status == "Inactive":
                            print(Fore.RED + "⚠️ This customer is inactive.")
                            f.write(line + "\n")
                            return

                        print(Fore.CYAN + "\n📋 Customer Profile")
                        print(tabulate([
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
                        ], headers=["Name", "Value"], tablefmt="fancy_grid"))

                        found = True

                f.write(line + "\n")

        if found == False:
            print(Fore.RED + "❌ Customer not found.")

    except Exception as e:
        print(Fore.RED + f"❌ Failed to display customer profile: {e}")


'''
Changes the status of an 'Inactive' account to 
'Active' and logs the reactivation.
'''
def restoreCustomer():
    accNo = input(Fore.CYAN + "Enter Account Number to Restore: ").strip()
    restored = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + "❌ Customer profile file not found.")
        return
    except Exception as e:
        print(Fore.RED + f"❌ Error reading file: {e}")
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        status = parts[9]
                        if status == "Active":
                            print(Fore.GREEN + "✅ Customer already active.")
                            f.write(line + "\n")
                        else:
                            parts[9] = "Active"

                            updatedLine = parts[0]
                            index = 1
                            while index < len(parts):
                                updatedLine = updatedLine + "|" + parts[index]
                                index = index + 1

                            f.write(updatedLine + "\n")
                            restored = True
                            print(Fore.GREEN + "✅ Customer restored.")
                    else:
                        f.write(line + "\n")
                else:
                    f.write(line + "\n")

        if restored == False:
            print(Fore.RED + "❌ Account not found or already active.")
    except Exception as e:
        print(Fore.RED + f"❌ Error updating file: {e}")


'''
Lets admin update phone, email, address, name, or NIC.
 Changes are logged in change_log.txt for tracking.
'''
def updateCustomer():
    accNo = input(Fore.CYAN + "Enter Account Number to Update: ").strip()

    if accountInactive(accNo) == True:
        print(Fore.RED + "❌ Cannot update an inactive account.")
        return

    updated = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + "❌ Customer profile file not found.")
        return
    except Exception as e:
        print(Fore.RED + "❌ Error reading file: " + str(e))
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f, open('change_log.txt', 'a') as log:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        print("\n📋 Current Details:")
                        print("1. Phone   : " + parts[4])
                        print("2. Email   : " + parts[5])
                        print("3. Address : " + parts[6])
                        print("4. Name    : " + parts[1])
                        print("5. NIC     : " + parts[2])
                        print("0. Cancel Update")

                        choice = input("\nWhich field do you want to update? (1-5): ").strip()

                        if choice == "1":
                            old = parts[4]
                            parts[4] = getValidatedInput("New Phone Number: ", "Phone", "phone")
                            log.write(accNo + " - Phone changed from " + old + " to " + parts[4] + "\n")

                        elif choice == "2":
                            old = parts[5]
                            parts[5] = getValidatedInput("New Email: ", "Email", "email")
                            log.write(accNo + " - Email changed from " + old + " to " + parts[5] + "\n")

                        elif choice == "3":
                            old = parts[6]
                            parts[6] = getValidatedInput("New Address: ", "Address")
                            log.write(accNo + " - Address changed from " + old + " to " + parts[6] + "\n")

                        elif choice == "4":
                            old = parts[1]
                            parts[1] = getValidatedInput("New Full Name: ", "Name")
                            parts[1] = parts[1].upper()
                            log.write(accNo + " - Name changed from " + old + " to " + parts[1] + "\n")

                        elif choice == "5":
                            oldNic = parts[2]
                            newNic = getValidatedInput("New NIC: ", "NIC", "nic")
                            result = getDobFromNic(newNic)
                            newDob = result[0]
                            newGender = result[1]

                            if newDob == None:
                                print(Fore.RED + "⚠️ Invalid NIC. Could not extract DOB.")
                                line_to_write = parts[0]
                                for i in range(1, len(parts)):
                                    line_to_write = line_to_write + "|" + parts[i]
                                f.write(line_to_write + "\n")
                            else:
                                parts[2] = newNic
                                parts[3] = str(newDob)
                                parts[7] = newGender
                                log.write(accNo + " - NIC changed from " + oldNic + " to " + newNic + ", DOB and Gender recalculated.\n")
                                print("✔️ DOB and Gender updated from NIC.")

                        elif choice == "0":
                            print(Fore.RED + "Update cancelled.")
                            line_to_write = parts[0]
                            index = 1
                            while index < len(parts):
                                line_to_write = line_to_write + "|" + parts[index]
                                index = index + 1
                            f.write(line_to_write + "\n")
                        else:
                            print(Fore.RED + "Invalid choice. Skipping update.")
                            line_to_write = parts[0]
                            index = 1
                            while index < len(parts):
                                line_to_write = line_to_write + "|" + parts[index]
                                index = index + 1
                            f.write(line_to_write + "\n")

                        if choice in ["1", "2", "3", "4", "5"]:
                            line_to_write = parts[0]
                            index = 1
                            while index < len(parts):
                                line_to_write = line_to_write + "|" + parts[index]
                                index = index + 1
                            f.write(line_to_write + "\n")
                            updated = True

                    else:
                        f.write(line + "\n")
                else:
                    f.write(line + "\n")

        if updated == False:
            print(Fore.RED + "❌ Account not found.")
    except Exception as e:
        print(Fore.RED + "❌ Error updating file: " + str(e))


'''
Changes customer status to 'Inactive' instead of deleting and logs
 the reason in deactivation_log.txt
'''
def softDeleteCustomer(accNo=None):
    confirmed = input("Are you sure you want to mark this customer as inactive? (Y/N): ").strip()
    confirmed = confirmed.lower()

    if confirmed != "y" or confirmed != "yes" :
        print(Fore.RED + "❌ Deletion cancelled.")
        return

    reason = input(Fore.CYAN + "Enter reason for deactivation: ").strip()
    deleted = False

    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.RED + "❌ Customer file not found.")
        return
    except Exception as e:
        print(Fore.RED + "❌ Error reading customer file: " + str(e))
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f, open('deactivation_log.txt', 'a') as log:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    acc_from_file = parts[0]

                    if acc_from_file == accNo:
                        status = parts[9]

                        if status == "Inactive":
                            print(Fore.RED + "⚠️ Already inactive.")
                            rebuilt_line = parts[0]
                            i = 1
                            while i < len(parts):
                                rebuilt_line = rebuilt_line + "|" + parts[i]
                                i = i + 1
                            f.write(rebuilt_line + "\n")
                        else:
                            parts[9] = "Inactive"

                            rebuilt_line = parts[0]
                            i = 1
                            while i < len(parts):
                                rebuilt_line = rebuilt_line + "|" + parts[i]
                                i = i + 1
                            f.write(rebuilt_line + "\n")

                            log.write(accNo + " | Deactivated on " + str(datetime.datetime.now()) + " | Reason: " + reason + "\n")
                            deleted = True
                            print(Fore.CYAN + "🟡 Customer marked as Inactive.")
                    else:
                        f.write(line + "\n")
                else:
                    f.write(line + "\n")

        if deleted == False:
            print(Fore.RED + "❌ Account not found.")

    except Exception as e:
        print(Fore.RED + "❌ Error updating customer file: " + str(e))



'''
Validates access, ensures account is active, 
updates in-memory balance, and logs transaction.
'''
def deposit(accounts, role, acc_no=None):
    entered = input(Fore.CYAN + "Enter account number: ").strip()

    if role != "admin":
        if entered != acc_no:
            print(Fore.RED + "❌ You can only deposit into your own account.")
            return

    if accountInactive(entered) == True:
        print(Fore.RED + "❌ Cannot deposit to an inactive account.")
        return

    found = False
    for key in accounts:
        if key == entered:
            found = True

    if found == False:
        print(Fore.RED + "❌ Account not found.")
        return

    try:
        amount_input = input(Fore.CYAN + "Amount to deposit: ").strip()
        amount = float(amount_input)

        if amount <= 0:
            print(Fore.RED + "❌ Deposit amount must be greater than 0.")
            return

    except ValueError:
        print(Fore.RED + "❌ Invalid amount. Please enter a valid number.")
        return

    try:
        accounts[entered]["balance"] = accounts[entered]["balance"] + amount

        now = datetime.datetime.now()
        txn = "Deposited Rs." + str(amount) + " on " + str(now)

        accounts[entered]["transactions"].append(txn)
        writeTransaction(entered, txn)

        print(Fore.GREEN + "✅ Rs." + str(amount) + " successfully deposited into account " + entered + ".")

    except Exception as e:
        print(Fore.RED + "❌ Failed to process deposit: " + str(e))



'''
Checks for sufficient balance, 
then deducts amount and logs the transaction.
'''
def withdraw(accounts, role, acc_no=None):
    entered = input(Fore.CYAN + "Enter account number: ").strip()

    if role != "admin":
        if entered != acc_no:
            print(Fore.RED + "❌ You can only withdraw from your own account.")
            return

    if accountInactive(entered) == True:
        print(Fore.RED + "❌ Cannot withdraw from an inactive account.")
        return

    found = False
    for key in accounts:
        if key == entered:
            found = True

    if found == False:
        print(Fore.RED + "❌ Account not found.")
        return

    try:
        amount_input = input(Fore.CYAN + "Amount to withdraw: ").strip()
        amount = float(amount_input)

        if amount <= 0:
            print(Fore.RED + "❌ Withdrawal amount must be greater than 0.")
            return

    except ValueError:
        print(Fore.RED + "❌ Invalid amount. Please enter a numeric value.")
        return

    current_balance = accounts[entered]["balance"]

    if amount > current_balance:
        print(Fore.RED + "❌ Insufficient funds for this withdrawal.")
        return

    try:
        accounts[entered]["balance"] = current_balance - amount

        now = datetime.datetime.now()
        txn = "Withdrew Rs." + str(amount) + " on " + str(now)

        accounts[entered]["transactions"].append(txn)
        writeTransaction(entered, txn)

        print(Fore.GREEN + "✅ Rs." + str(amount) + " withdrawn successfully from account " + entered + ".")

    except Exception as e:
        print(Fore.RED + "❌ Withdrawal failed due to an error: " + str(e))


'''
Shows the current balance for the account entered, 
with permission check for users.
'''
def checkBalance(accounts, role, acc_no=None):
    try:
        entered = input(Fore.CYAN + "Enter account number: ").strip()

        if role != "admin":
            if entered != acc_no:
                print(Fore.RED + "❌ You can only check your own balance.")
                return

        if accountInactive(entered) == True:
            print(Fore.RED + "❌ Cannot check balance for an inactive account.")
            return

        found = False
        for key in accounts:
            if key == entered:
                found = True

        if found == False:
            print(Fore.RED + "❌ Account not found.")
            return

        balance = accounts[entered]["balance"]
        formatted = "Rs. " + format(balance, ".2f")
        print(Fore.GREEN + "✅ Your current balance is: " + formatted)

    except Exception as e:
        print(Fore.RED + "❌ Failed to retrieve balance due to an error: " + str(e))

'''
Displays all transaction logs from memory 
using tabulate for nice formatting.
'''
def viewTransactions(accounts, role, acc_no=None):
    try:
        entered = input(Fore.CYAN + "Enter account number: ").strip()

        if role != "admin":
            if entered != acc_no:
                print(Fore.RED + "❌ You can only view your own transactions.")
                return

        if accountInactive(entered) == True:
            print(Fore.RED + "❌ Cannot view transactions for an inactive account.")
            return

        found = False
        for key in accounts:
            if key == entered:
                found = True

        if found == False:
            print(Fore.RED + "❌ Account not found.")
            return

        transactions = accounts[entered]["transactions"]
        print(Fore.CYAN + "\n📄 Transaction History for Account " + entered + ":\n")

        if len(transactions) == 0:
            print(Fore.YELLOW + "⚠️ No transactions recorded for this account.")
            return

        table = []
        index = 1
        for txn in transactions:
            row = [index, txn]
            table.append(row)
            index = index + 1

        print(tabulate(table, headers=["No", "Transaction Details"], tablefmt="fancy_grid"))

    except Exception as e:
        print(Fore.RED + "❌ Error retrieving transactions: " + str(e))


'''
Checks both sender and receiver accounts,
 then updates balances and logs transactions for both sides.
'''
def transferMoney(accounts, role, acc_no=None):
    try:
        fromAcc = input(Fore.CYAN + "Sender Account Number: ").strip()

        if role == "user":
            if fromAcc != acc_no:
                print(Fore.RED + "⚠️ You can only transfer from your own account.")
                return

        if accountInactive(fromAcc) == True:
            print(Fore.RED + "❌ Sender account is inactive.")
            return

        toAcc = input(Fore.CYAN + "Receiver Account Number: ").strip()

        if accountInactive(toAcc) == True:
            print(Fore.RED + "❌ Receiver account is inactive.")
            return

        sender_found = False
        receiver_found = False

        for key in accounts:
            if key == fromAcc:
                sender_found = True
            if key == toAcc:
                receiver_found = True

        if sender_found == False:
            print(Fore.RED + "❌ Sender account not found.")
            return

        if receiver_found == False:
            print(Fore.RED + "❌ Receiver account not found.")
            return

        amount_input = input(Fore.CYAN + "Amount to transfer: ").strip()
        amount = float(amount_input)

        if amount <= 0:
            print(Fore.RED + "❌ Transfer amount must be greater than 0.")
            return

        if amount > accounts[fromAcc]["balance"]:
            print(Fore.RED + "❌ Insufficient balance for the transfer.")
            return

        # Perform transfer
        old_balance_sender = accounts[fromAcc]["balance"]
        old_balance_receiver = accounts[toAcc]["balance"]

        accounts[fromAcc]["balance"] = old_balance_sender - amount
        accounts[toAcc]["balance"] = old_balance_receiver + amount

        now = datetime.datetime.now()
        t1 = "Transferred Rs." + str(amount) + " to " + toAcc + " on " + str(now)
        t2 = "Received Rs." + str(amount) + " from " + fromAcc + " on " + str(now)

        accounts[fromAcc]["transactions"].append(t1)
        accounts[toAcc]["transactions"].append(t2)

        writeTransaction(fromAcc, t1)
        writeTransaction(toAcc, t2)

        print(Fore.GREEN + "✅ Transfer completed successfully.")

    except ValueError:
        print(Fore.RED + "❌ Please enter a valid numeric amount.")
    except Exception as e:
        print(Fore.RED + "❌ An error occurred: " + str(e))


'''
Calculates monthly interest if it hasn’t been applied yet 
for the month and updates account balances.
'''
def applyMonthlyInterest(accounts):
    interestRateAnnual = 0.03
    interestRateMonthly = interestRateAnnual / 12
    today = datetime.date.today()
    alreadyApplied = []

    
    try:
        with open('interestlog.txt', 'r') as log:
            for line in log:
                try:
                    parts = line.strip().split('|')
                    accNo = parts[0]
                    dateStr = parts[1]
                    dateObj = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()

                    if dateObj.month == today.month:
                        if dateObj.year == today.year:
                            alreadyApplied.append(accNo)
                except:
                    pass
    except FileNotFoundError:
        pass

    
    try:
        with open('CustomerProfiles.txt', 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(Fore.YELLOW + "⚠️ No customer file found.")
        return

    try:
        with open('CustomerProfiles.txt', 'w') as f_out, open('interestlog.txt', 'a') as log:
            for line in lines:
                line = line.strip()
                parts = line.split('|')

                if len(parts) >= 10:
                    accNo = parts[0]
                    name = parts[1]
                    accountType = parts[8]
                    status = parts[9]

                    isEligible = False

                    
                    accountExists = False
                    for key in accounts:
                        if key == accNo:
                            accountExists = True

                    alreadyCredited = False
                    for a in alreadyApplied:
                        if a == accNo:
                            alreadyCredited = True

                    if accountType == "Savings":
                        if status == "Active":
                            if accountExists == True:
                                if alreadyCredited == False:
                                    isEligible = True

                    if isEligible == True:
                        balance = accounts[accNo]["balance"]
                        interestAmount = balance * interestRateMonthly
                        interestAmount = round(interestAmount, 2)

                        accounts[accNo]["balance"] = balance + interestAmount

                        txn = "Monthly Interest Rs." + str(interestAmount) + " on " + str(today)
                        accounts[accNo]["transactions"].append(txn)

                        writeTransaction(accNo, txn)
                        writeAccountDetails(accNo, name, accounts[accNo]["balance"])

                        log.write(accNo + "|" + str(today) + "|" + str(interestAmount) + "|" + str(round(interestRateMonthly * 100, 2)) + "%" + "\n")

                
                rebuilt = parts[0]
                i = 1
                while i < len(parts):
                    rebuilt = rebuilt + "|" + parts[i]
                    i = i + 1
                f_out.write(rebuilt + "\n")

        print(Fore.GREEN + "✅ Monthly interest applied where eligible.")

    except Exception as e:
        print(Fore.RED + "❌ Failed to apply interest: " + str(e))




'''
Reads interestlog.txt and displays
 account, date, amount, and interest rate in a table.
'''
def viewInterestHistory(accounts):
    interestRecords = []

    try:
        with open('interestlog.txt', 'r') as log:
            for line in log:
                line = line.strip()
                parts = line.split('|')

                if len(parts) == 4:
                    accNo = parts[0]
                    date = parts[1]
                    amount = parts[2]
                    rate = parts[3]

                    formattedAmount = "Rs." + amount
                    row = [accNo, date, formattedAmount, rate]
                    interestRecords.append(row)

    except FileNotFoundError:
        print(Fore.YELLOW + "⚠️ No interest records found.")
        return
    except Exception as e:
        print(Fore.RED + "❌ Error reading interest log: " + str(e))
        return

    if len(interestRecords) > 0:
        print(Fore.GREEN + "\n📋 Interest Applied History:")
        print(tabulate(interestRecords, headers=["Account No", "Date", "Interest Amount", "Rate"], tablefmt="fancy_grid"))
    else:
        print(Fore.YELLOW + "⚠️ No interest entries to display.")


'''
Displays menu options for 
creating, editing, and managing accounts, transactions, and logs.
'''
def adminMenu(accounts, role):
    while True:
        input(Fore.YELLOW + "\nPress Enter to Enter to menu...")
        clearScreen()
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t|                 ================= Admin Menu ==================                  |")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print("")
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
            ["12", "Search Customer by NIC/Phone"],
            ["0", "Logout"]
        ]
        table = tabulate(menu, headers=["Option", "Description"], tablefmt="fancy_grid")

        for i in table.split('\n'):
            print("\t\t\t\t"+ i)
        

        try:
            choice = input(Fore.YELLOW + "\t\t\t\tSelect an Option (0–11): ").strip()
        except Exception as e:
            print(Fore.RED + f"❌ Input error: {e}")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            continue

        if choice == '1':
            createAccount(accounts)
        elif choice == '2':
            readCustomer(role)
        elif choice == '3':
            updateCustomer()
        elif choice == '4':
            accNo = input(Fore.CYAN + "Enter Account Number to Deactivate: ").strip()
            softDeleteCustomer(accNo)
        elif choice == '5':
            deposit(accounts, role)
        elif choice == '6':
            withdraw(accounts, role)
        elif choice == '7':
            checkBalance(accounts, role)
        elif choice == '8':
            viewTransactions(accounts, role)
        elif choice == '9':
            transferMoney(accounts, role)
        elif choice == '10':
            restoreCustomer()
        elif choice == '11':
            viewInterestHistory(accounts)
        elif choice == '12':
            print(Fore.CYAN + "\n🔍 Search Customer")
            print("1. By NIC")
            print("2. By Phone")
            search_choice = input("Select an option (1/2): ").strip()
            
            if search_choice == "1":
                nic = input("Enter NIC: ").strip()
                searchCustomerBy("nic", nic)
            elif search_choice == "2":
                phone = input("Enter Phone Number: ").strip()
                searchCustomerBy("phone", phone)
            else:
                print(Fore.RED + "Invalid selection.")

        elif choice == '0':
            print(Fore.CYAN + "✅ Logging out of Admin Menu.")
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Please select from 0 to 11.")

        input(Fore.YELLOW + "\nPress Enter to return to menu...")


'''
Allows logged-in customers to manage their own account 
operations like deposits, transfers, etc.
'''
def userMenu(accounts, role, acc_no):
    while True:
        clearScreen()
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t|                 ================= User  Menu ==================                  |")
        print(Fore.CYAN+"\t|                                                                                  |")
        print(Fore.CYAN+"\t___________________________________________________________________________________")
        print("")
        menu = [
            ["1", "User Profile"],
            ["2", "Deposit"],
            ["3", "Withdraw"],
            ["4", "Check Balance"],
            ["5", "Transaction History"],
            ["6", "Transfer Money"],
            ["0", "Logout"]
        ]
        table = tabulate(menu, headers=["Option", "Description"], tablefmt="fancy_grid")

        for i in table.split("\n"):
            print("\t\t\t\t"+i)

        try:
            choice = input(Fore.YELLOW + "\t\t\t\tSelect an option (0–6): ").strip()
        except Exception as e:
            print(Fore.RED + f"❌ Input error: {e}")
            input(Fore.YELLOW + "\nPress Enter to continue...")
            continue

        if choice == '1':
            readCustomer(role, acc_no)
        elif choice == '2':
            deposit(accounts, role, acc_no)
        elif choice == '3':
            withdraw(accounts, role, acc_no)
        elif choice == '4':
            checkBalance(accounts, role, acc_no)
        elif choice == '5':
            viewTransactions(accounts, role, acc_no)
        elif choice == '6':
            transferMoney(accounts, role, acc_no)
        elif choice == '0':
            print(Fore.CYAN + "✅ Logging out of User Menu.")
            break
        else:
            print(Fore.RED + "❌ Invalid choice. Please select from 0 to 6.")

        input(Fore.YELLOW + "\nPress Enter to return to menu...")


'''
Initializes accounts, reads credentials, handles login, then
 redirects to appropriate menu based on user role.
'''
def startMenu():
    while True:
        try:
            input(Fore.YELLOW + "\nPress Enter to continue...")
            clearScreen()

            accounts = firstReadAllData()  
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

            print(Fore.RED + "\n🔒 You have been logged out.")
            choice = input(Fore.CYAN + "Press ENTER to login again or type 0 to exit: ").strip()

            if choice == '0':
                print(Fore.CYAN+"\t___________________________________________________________________________________")
                print(Fore.CYAN+"\t|                                                                                  |")
                print(Fore.CYAN+"\t|  ============ Thank you for using Unicom Banking App. Goodbye!  ============     |")
                print(Fore.CYAN+"\t|                                                                                  |")
                print(Fore.CYAN+"\t___________________________________________________________________________________")
                print("")
                break

        except KeyboardInterrupt:
            print(Fore.RED + "\n⚠️ Interrupted. Exiting application.")
            break
        except Exception as e:
            print(Fore.RED + f"❌ An error occurred: {e}")
            input(Fore.YELLOW + "Press Enter to try again...")


startMenu()
