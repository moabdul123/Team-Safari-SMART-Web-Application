import streamlit as st 
from streamlit_chat import message
import openai


#-------------PAGE CONFIG-------------
page_title = "SMART T1D Variant Catalogue"
layout = "centered"
st.set_page_config(page_title=page_title, layout = layout)
#--------------------------------------

# -------------PAGE TITLE--------------
st.title(page_title)
st.markdown('')
st.markdown('')
# -------------------------------------

# ------------CONTACT US FORM-----------
st.subheader(":mailbox: Get in touch with us!")
contact_form = """
<form action="https://formsubmit.co/r.maurya@se22.qmul.ac.uk" method="POST">
	 <input type="hidden" name="_captcha" value="false">
	 <input type="text" name="name" placeholder="Your name" required>
	 <input type="email" name="email" placeholder="Your email" required>
	 <textarea name="message" placeholder="Your message here"></textarea>
	 <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

# Use local CSS file
def local_css(file_name):
	with open(file_name) as f:
		st.markdown(f"<style>{f.read()}<style>", unsafe_allow_html=True)

local_css("style/style.css")
# ---------------------------------------


# ---------------LINKEDIN BADGE----------------
linkedin_badge = """
[![LinkedIn](https://img.shields.io/badge/-LinkedIn-blue?style=flat&logo=Linkedin&logoColor=white&link=https://www.linkedin.com/in/school-of-biological-and-behavioural-sciences-queen-mary-186711a9/)](https://www.linkedin.com/in/school-of-biological-and-behavioural-sciences-queen-mary-186711a9/)
"""
# -------------------------------------------- 

# ---------------TWITTER BADGE----------------
twitter_badge = """
<a href="https://twitter.com/QM_SBBS">
	<img src="https://img.shields.io/twitter/follow/QM_SBBS?style=social&logo=twitter" alt="Follow me on Twitter">
</a>
"""
# --------------------------------------------


# -----DISPLAYING CONNECT WITH US SECTION------

st.markdown("-------------")
st.subheader("Connect with us on :wave:")
onecol, twocol,threecol, fourcol, fivecol, sixcol, sevcol = st.columns(7)
onecol.markdown(linkedin_badge, unsafe_allow_html=True)
twocol.markdown(twitter_badge, unsafe_allow_html=True)
# --------------------------------------------

# -------------CHATBOT SECTION----------------
st.markdown("-------------")
botone, bottwo = st.columns(2)
with botone:

	openai.api_key = st.secrets['api_secret']


	def generate_response(prompt):

		'''
		This function uses the OpenAI Completion API to generate a 
		response based on the given prompt. The temperature parameter controls 
		the randomness of the generated response. A higher temperature will result 
		in more random responses, 
		while a lower temperature will result in more predictable responses.
		'''

		completions = openai.Completion.create (
			engine="text-davinci-003",
			prompt=prompt,
			max_tokens=1024,
			n=1,
			stop=None,
			temperature=0.5,
		)

		message = completions.choices[0].text
		return message


	st.subheader(":speech_balloon: ChatBot")
	st.caption("Chat about anything! We do not store your conversations. Once you exit the website or refresh, entire data is wiped out")


	if 'generated' not in st.session_state:
		st.session_state['generated'] = []

	if 'past' not in st.session_state:
		st.session_state['past'] = []


	def get_text():
		input_text = st.text_input("You: ", key="input")
		return input_text 


	user_input = get_text()

	if user_input:
		output = generate_response(user_input)
		st.session_state.past.append(user_input)
		st.session_state.generated.append(output)

	if st.session_state['generated']:

		for i in range(len(st.session_state['generated'])-1, -1, -1):
			message(st.session_state["generated"][i], key=str(i), avatar_style = "adventurer", seed = 180)  #good seed values : 150,170,2,180
			message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style = "adventurer", seed = 2)
# --------------------------------------------