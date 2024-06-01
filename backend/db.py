from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId
import os

mongodb_rw_host = os.environ.get("MONGODB_RW_HOST", "localhost")
mongodb_ro_host = os.environ.get("MONGODB_RO_HOST", "localhost")

rw_connection_string = f"mongodb://root:example@{mongodb_rw_host}"
ro_connection_string = f"mongodb://root:example@{mongodb_ro_host}"

rw_client = MongoClient(rw_connection_string)
ro_client = MongoClient(ro_connection_string)

print(f"Connecting to RW DB on URL: {rw_connection_string}")
print(f"Connecting to RO DB on URL: {ro_connection_string}")

rw_db = rw_client["devops_db"]
ro_db = ro_client["devops_db"]

users_rw = rw_db.users
users_ro = ro_db.users

def get_users():
    users_cursor = users_ro.find({})
    users_list = []
    for user in users_cursor:
        user['_id'] = str(user['_id'])
        del user['password']
        users_list.append(user)
    return users_list

def create_user(user_data):
    if users_rw.count_documents({"$or": [{"email": user_data["email"]}]}):
        return "User with this email already exists."

    return str(users_rw.insert_one(user_data).inserted_id)

def read_user(email=None, user_id=None):
    if email:
        user = users_ro.find_one({"email": email})
    else:
        user = users_ro.find_one({"_id": ObjectId(user_id)})

    if user:
        user['_id'] = str(user['_id'])
    return user

def update_user(user_id, new_user_data):
    user = users_rw.find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": new_user_data},
        return_document=ReturnDocument.AFTER
    )
    if user:
        user['_id'] = str(user['_id'])
    return user

def delete_user(user_id):
    return users_rw.delete_one({"_id": ObjectId(user_id)})

if __name__ == "__main__":

    user_data = {
        "email": "user@example.com",
        "name": "Name",
        "surname": "Surname",
        "password": "password",
        "roles": ["admin"]
    }

    user_id = create_user(user_data)
    print(f"User created with ID: {user_id}")

    user = read_user("user@example.com")
    print(f"User details by email: {user}")


    updated_user = update_user(user_id, {"email": "newemail@example.com"})
    print(f"Updated user details: {updated_user}")


    # delete_user(user_id)
    user = read_user(user_id=user_id)
    # print(f"User after deletion: {user}")
