# Firebase Firestore Setup for License System

This guide helps you set up Firebase Firestore to use it as a secure backend for your Envato license verification system.

---

## 🔧 Step-by-Step Setup

### 1. Create Firebase Project
- Go to [Firebase Console](https://console.firebase.google.com/)
- Click **"Add project"**
- Enter a project name (e.g., `CheckEnvatoLicense`)
- Disable Google Analytics (optional)
- Click **"Create Project"**

### 2. Enable Firestore Database
- Visit: [Firestore Setup](https://console.cloud.google.com/datastore/setup)
- Select your project (e.g., `checkenvatolicense`)
- Choose:
  - **Production mode** (recommended)
  - **Location** (e.g., `us-central`)
- Click **"Create Database"**

### 3. Create Service Account Key
- Visit [Google Cloud Console - IAM & Admin](https://console.cloud.google.com/iam-admin/serviceaccounts)
- Choose your Firebase project
- Click **"Create Service Account"**
  - Give it a name (e.g., `LicenseChecker`)
  - Click **"Create"**
- In the next steps, grant it the **"Editor"** role (or **"Cloud Datastore User"** for least privilege)
- Click **"Done"**
- Now select the service account from the list
  - Click **"Add Key" → "Create new key" → JSON**
  - Save the downloaded `serviceAccountKey.json` file securely

### 4. Install Required Python Packages

```bash
pip install google-cloud-firestore
```

### 5. Python Code Example

```python
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Example: Check a purchase code
def check_purchase_code(code):
    doc_ref = db.collection("licenses").document(code)
    doc = doc_ref.get()
    if doc.exists:
        return "✅ Already Used"
    else:
        return "❌ Not Used"

print(check_purchase_code("86781236-23d0-4b3c-7dfa-c1c147e0dece"))
```

---

## ✅ Done!
You are now ready to use Firebase Firestore as a production-level backend for your Envato license verification.

