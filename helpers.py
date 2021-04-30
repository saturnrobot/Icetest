import os
import random
import string

def clearView():
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')

def ran_string(size):
    return ''.join(random.choice(string.ascii_letters + string.punctuation) for x in range(size))