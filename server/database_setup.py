from pyrebase import pyrebase
from dotenv import load_dotenv
import os


file_path = ".env.dev"

load_dotenv(f"server/{file_path}")
apikey = os.getenv("API_KEY")
authDomain = os.getenv("AUTH_DOMAIN")
databaseURL = os.getenv("DATABASE_URL")
projectId = os.getenv("PROJECT_ID")
storageBucket = os.getenv("STORAGE_BUCKET")
messagingSenderId = os.getenv("MESSAGING_SENDER_ID")
appId = os.getenv("APP_ID")
measurementId = os.getenv("MEASUREMENT_ID")


def database_authentication():
    firebaseConfig = {
  "apiKey": f"{apikey}",
  "authDomain": f"{authDomain}",
  "databaseURL": f"{databaseURL}",
 "projectId": f"{projectId}",
  "storageBucket": f"{storageBucket}",
  "messagingSenderId": f"{messagingSenderId}",
  "appId": f"{appId}",
  "measurementId": f"{measurementId}"
}


    # Initialize Firebase
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
    storage = firebase.storage()

    access=[auth, db, storage]

    return access