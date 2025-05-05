# to create the Random 10 Numbers

# import random

# minimum = pow(10, 10-1)
# maximum = pow(10, 10) - 1
# print(random.randint(minimum, maximum)) 

import bcrypt

raw_password = "admin"
hashed = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

print("Hashed Password:", hashed)
