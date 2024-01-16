import bcrypt

def hash_password(password):
    # Generate a random salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def verify_password(input_password, hashed_password):
    # Verify the input password against the stored hashed password
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)