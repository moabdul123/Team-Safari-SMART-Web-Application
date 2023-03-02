import pickle
from pathlib import Path
import streamlit_authenticator as stauth

names = ["Anyone"]
username = ["safari"]
password = ["XXX"]

hashed_passwords = stauth.Hasher(password).generate()

file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("wb") as file:
	pickle.dump(hashed_passwords, file)