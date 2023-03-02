import pickle
from pathlib import Path
import requests
import streamlit as st  
from streamlit_lottie import st_lottie
import streamlit_authenticator as stauth 
from datetime import datetime
import time
import pandas as pd 
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import openai
from getpass import getpass
import sys
import sqlite3
import json
from pandas import json_normalize  
from pandas import DataFrame, to_numeric
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
import itertools
import io

#-------------PAGE CONFIG-------------
page_title = "SMART T1D Variant Catalogue"
layout = "centered"
st.set_page_config(page_title=page_title, layout = layout)
st.title(page_title)
st.sidebar.info('''Note:
	Use the following username and password to login:-
	''')
st.sidebar.info("Username- safari")
st.sidebar.info("Password- 2345")
#--------------------------------------


# -------USER AUTHENTICATION-----------
names = ["Anyone"]
username = ["safari"]

#Load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
	hashed_passwords = pickle.load(file)

authenticator = stauth.Authenticate(names,username,hashed_passwords,"type1_diabetes","abcdef", cookie_expiry_days=60)

name, authentication_status, username = authenticator.login("Login","main")   # Create login form
# --------------------------------------


if authentication_status == False:         # Error message if user entered incorrect username or password
	st.error("Username/password is incorrect")

if authentication_status == None:          # Warning to enter username and password once the website is opened
	st.warning("Please enter your username and password")

if authentication_status:            # Implement the following codes if login was successful
	# st.sidebar.title(f"Welcome to {page_title}")      # Welcome message in sidebar just after login to the website
	
	# current_date = datetime.now().date()            # Getting current date
	# st.sidebar.caption(f"Today's date (w.r.t. London) : {current_date}") 
	st.success("Login Successful!")
	authenticator.logout("Logout","sidebar")         # Logout button
	st.sidebar.markdown("--------------") 