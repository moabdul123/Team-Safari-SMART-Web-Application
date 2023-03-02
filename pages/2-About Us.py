import streamlit as st  
from PIL import Image


#-------------PAGE CONFIG-------------
page_title = "SMART T1D Variant Catalogue"
layout = "centered"
st.set_page_config(page_title=page_title, layout = layout)
#--------------------------------------

header = st.container()
description = st.container()
images = st.container()
with header:
	st.title(page_title)

with description:
	st.markdown("")
	st.markdown("")
	st.markdown("Hello! We are a team of 5 classmates, studying Msc Bioinformatics at Queen Mary University of London. Each one of us has contributed to the making of this functional website!")
	st.markdown("")
	st.markdown("")

with images:

	col4, col5 , col6 = st.columns(3)

	with col4:
		image = Image.open('images/me.jpg')
		st.image(image, caption='Rashmi Maurya')
		linkedin_badge = """
		[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/rashmi-maurya/)](https://www.linkedin.com/in/rashmi-maurya/)
		"""
		st.markdown(linkedin_badge, unsafe_allow_html=True)

	with col5:
		image = Image.open('images/ahmad.jpg')
		st.image(image, caption='Ahmad Arnaout')
		linkedin_badge = """
		[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/ahmad-arnaout-bbb90b196/)](https://www.linkedin.com/in/ahmad-arnaout-bbb90b196/)
		"""		
		st.markdown(linkedin_badge, unsafe_allow_html=True)    #make columns below columns for images to try center aligning the badges

	with col6:
		image = Image.open('images/shukrii.jpg')
		st.image(image, caption='Shukri Xalane')
		linkedin_badge = """
		[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/shukrixalane/)](https://www.linkedin.com/in/shukrixalane/)
		"""
		st.markdown(linkedin_badge, unsafe_allow_html=True)
		
	st.markdown("")
	st.markdown("")

	col1, col2, col3 = st.columns(3)

	with col1:
		image = Image.open('images/Tedy.jpg')
		st.image(image, caption='Teodora Borilova')
		linkedin_badge = """
		[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/teodora-borilova/)](https://www.linkedin.com/in/teodora-borilova/)
		"""
		st.markdown(linkedin_badge, unsafe_allow_html=True)

		
	with col2:
		image = Image.open('images/Jahed.jpg')
		st.image(image, caption='Mohammed Jahed Abdul')
		linkedin_badge = """
		[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/school-of-biological-and-behavioural-sciences-queen-mary-186711a9/)](https://www.linkedin.com/in/school-of-biological-and-behavioural-sciences-queen-mary-186711a9/)
		"""
		st.markdown(linkedin_badge, unsafe_allow_html=True)
	st.markdown(
	    """
	    <style>
	    img {
	        cursor: pointer;
	        transition: all .2s ease-in-out;
	    }
	    img:hover {
	        transform: scale(1.1);
	    }
	    </style>
	    """,
	    unsafe_allow_html=True,
	)

