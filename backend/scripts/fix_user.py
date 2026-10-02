import bcrypt
from pymongo import MongoClient

def fix_user():
    # Connect to MongoDB
    client = MongoClient("mongodb://database:27017")
    db = client["phishing_detection_db"]
    users_col = db["users"]
    
    # Hash the new correct password
    plain_password = "bhavin252006"
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")
    
    # Find the user by the typo'd email and update both email and password
    result = users_col.update_one(
        {"email": "bhavink0225@gmail.com"},
        {"$set": {
            "email": "bhavin0225@gmail.com",
            "password_hash": hashed_pwd
        }}
    )
    
    print(f"Matched {result.matched_count} document(s) and modified {result.modified_count} document(s).")
    
if __name__ == "__main__":
    fix_user()
