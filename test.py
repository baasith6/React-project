#Certainly! Here's a simple Python script that takes user input details and writes them to a text file with an auto-generated ID. The ID will increment each time a new user is added.

import os

def get_next_id(file_path):
    if not os.path.exists(file_path):
        return 1
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if not lines:
            return 1
        last_line = lines[-1]
        last_id = int(last_line.split(',')[0])
        return last_id + 1

def write_user_details(file_path, user_details):
    user_id = get_next_id(file_path)
    with open(file_path, 'a') as file:
        file.write(f"{user_id},{user_details['name']},{user_details['email']},{user_details['age']}\n")

def main():
    user_details = {}
    user_details['name'] = input("Enter your name: ")
    user_details['email'] = input("Enter your email: ")
    user_details['age'] = input("Enter your age: ")

    file_path = 'user_details.txt'
    write_user_details(file_path, user_details)
    print("User details saved successfully!")


main()

# Explanation:
# get_next_id(file_path): This function checks if the file exists and reads the last line to determine the last used ID. It then increments this ID by 1 for the new entry.
# write_user_details(file_path, user_details): This function writes the user details to the file, appending a new line with the auto-generated ID.
# main(): This function collects user input and calls the write_user_details function to save the details.

# This script ensures that each user entry in the text file has a unique, auto-incremented ID. Feel free to customize the fields and file path as needed!