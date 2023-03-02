import requests
import streamlit as st  
from streamlit_lottie import st_lottie


#-------------PAGE CONFIG-------------
page_title = "SMART T1D Variant Catalogue"
layout = "centered"
st.set_page_config(page_title=page_title, layout = layout)
#--------------------------------------

header = st.container()
with header:
	st.title(page_title)
	st.markdown('')
	des_col, gif_col = st.columns([2,3])
	des_col.markdown('')
	des_col.markdown('')
	des_col.write("The link to the documentation is [here](https://teams.microsoft.com/_#/apps/d7958adf-f419-46fa-941b-1b946497ef84/sections/MyNotebook)")

	# ----FUNCTION FOR INCLUDING GIF-------
	def load_lottieurl(url):
		r = requests.get(url)
		if r.status_code != 200:
			return None
		return r.json()
	# --------------------------------------


	# ----------DISPLAYING GIF---------------
	with gif_col:
		lottie_coding = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_Rtp8YQKEWg.json")
		st_lottie(lottie_coding,height = 300, key = "Swimm's documentation tool")
	# --------------------------------------
