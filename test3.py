nic = input("Enter Your Nic Number : ").strip().lower()
length = len(nic)

if length == 12:
    return nic
elif length ==10:
    if nic[-1] == 'v':
        print
    else:
        print("Enter The Correct Nic Number: ")
else:
    print("Enter the Correct Nic Number...")