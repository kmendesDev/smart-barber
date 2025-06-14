import firebase_admin
from firebase_admin import credentials, firestore, auth
import json
import streamlit as st

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("smart-barber-firebase.json")
        firebase_admin.initialize_app(cred)

    return firestore.client()
