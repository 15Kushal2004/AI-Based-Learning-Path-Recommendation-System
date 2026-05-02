"""Firebase configuration and initialization."""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth as admin_auth
import pyrebase

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_FILE = os.path.join(BASE_DIR, "firebase_credentials.json")

# ── Firebase Admin SDK (Firestore + User Management) ─────────
if not firebase_admin._apps:
    cred = credentials.Certificate(CRED_FILE)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# ── Pyrebase (Client-side Authentication) ─────────────────────
FIREBASE_CONFIG = {
    "apiKey": "AIzaSyBqwlPVtjc0WmBbSc5R4NrC3od2Toq6BWg",
    "authDomain": "ai-learning-path2004.firebaseapp.com",
    "projectId": "ai-learning-path2004",
    "storageBucket": "ai-learning-path2004.firebasestorage.app",
    "messagingSenderId": "908839309816",
    "appId": "1:908839309816:web:787851c6ab06d4f76dc60d",
    "databaseURL": "https://ai-learning-path2004-default-rtdb.firebaseio.com",  # Required by Pyrebase even if not using RTDB
}

firebase_client = pyrebase.initialize_app(FIREBASE_CONFIG)
pyrebase_auth = firebase_client.auth()
