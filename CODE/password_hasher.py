import hashlib, uuid #Hashlib used to hash passwords, uuid used to create a random string to be used as a salt

def generate_salt():            #generates salt
    return uuid.uuid4().hex

def hash_password(salt, password):  #hashes the combination of password and salt
    combination = password+salt

    return hashlib.sha256(combination.encode("utf-8")).hexdigest()

