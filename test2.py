# Certainly! Below is a Python script that demonstrates how to write user details to a text file with an auto-generated ID and includes basic user validation. The script will prompt the user for their details, validate the input, and then write the details to a file.

import os

def generate_user_id():
    """Generate a new user ID based on the existing IDs in the file."""
    if not os.path.exists('user_details.txt'):
        return 1
    with open('user_details.txt', 'r') as file:
        lines = file.readlines()
        if not lines:
            return 1
        last_line = lines[-1]
        last_id = int(last_line.split(',')[0])
        return last_id + 1

def validate_user_details(name, age, email):
    """Validate the user details."""
    if not name.isalpha():
        print("Name should contain only alphabets.")
        return False
    if not age.isdigit() or not (0 < int(age) < 120):
        print("Age should be a number between 1 and 119.")
        return False
    if '@' not in email or '.' not in email:
        print("Invalid email format.")
        return False
    return True

def get_user_details():
    """Prompt the user for their details and validate them."""
    while True:
        name = input("Enter your name: ")
        age = input("Enter your age: ")
        email = input("Enter your email: ")
        if validate_user_details(name, age, email):
            return name, age, email

def write_user_details_to_file(user_id, name, age, email):
    """Write the user details to a text file."""
    with open('user_details.txt', 'a') as file:
        file.write(f"{user_id},{name},{age},{email}\n")
    print("User details saved successfully.")

def main():
    """Main function to handle the user input and file writing."""
    user_id = generate_user_id()
    name, age, email = get_user_details()
    write_user_details_to_file(user_id, name, age, email)

if __name__ == "__main__":
    main()

# Explanation:
# generate_user_id(): This function reads the user_details.txt file to find the last user ID and increments it by one. If the file does not exist or is empty, it starts with ID 1.
# validate_user_details(): This function checks if the name contains only alphabets, the age is a number between 1 and 119, and the email contains '@' and '.'.
# get_user_details(): This function prompts the user for their name, age, and email, and validates the input using validate_user_details(). It keeps prompting until valid details are provided.
# write_user_details_to_file(): This function appends the user details to user_details.txt in a comma-separated format.
# main(): This function orchestrates the process by generating a user ID, getting validated user details, and writing them to the file.

# This script ensures that user details are validated and stored with a unique auto-generated ID. Feel free to customize the validation rules or file handling as needed!