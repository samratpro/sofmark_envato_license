import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def check_or_create_code(code, device_id):
    doc_ref = db.collection("purchase_codes").document(code)
    doc = doc_ref.get()
    if doc.exists:
        return {
            "status": "already_exists",
        }
    else:
        doc_ref.set({
            "used": True,
        })
        return {
            "status": "created",
        }

def delete_code(code):
    db.collection("purchase_codes").document(code).delete()
    if db.collection("purchase_codes").document(code).get().exists:
        return {"status": "not_deleted"}    
    return {"status": "deleted"}

# Example Usage
if __name__ == "__main__":
    device_id = "DEVICE-XYZ-123"
    purchase_code = "86781236-23d0-4b3c-7dfa-c1c147e0dec"

    # Check or Create
    print(check_or_create_code(purchase_code, device_id))

    # Optional: Delete if needed
    print(delete_code(purchase_code))
