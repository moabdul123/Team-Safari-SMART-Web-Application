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
#--------------------------------------


# ---------SIDEBAR-----------------
st.sidebar.title(f"Welcome to {page_title}")      # Welcome message in sidebar just after login to the website

current_date = datetime.now().date()            # Getting current date
st.sidebar.caption(f"Today's date (w.r.t. London) : {current_date}")     # Showing current date on the sidebar

current_time = datetime.now().time()            # Getting current time
st.sidebar.caption(f"Current time (GMT) : {current_time}")          # Showing current time on the sidebar

# authenticator.logout("Logout","sidebar")         # Logout button
st.sidebar.markdown("--------------")

# -----------CHAT-Safari-------------
openai.api_key = st.secrets['api_secret']      # Setting up the OpenAI API key   
st.sidebar.header("CHAT-Safari")
chatbot = st.sidebar.text_input("Ask anything", key = "input")

if st.sidebar.button("Submit"):
	res_box = st.sidebar.empty()        # Creating an empty container for the response
	if chatbot:
		report = []                # Creating an empty list to store the responses
		for resp in openai.Completion.create(model='text-davinci-003',        # Generating a response using OpenAI's Completion API
											prompt=chatbot,
											max_tokens=500, 
											temperature = 0.5,
											stream = True):
			report.append(resp.choices[0].text)               # Joining the responses and removing new lines
			result = "".join(report).strip()
			result = result.replace("\n", "")
			res_box.markdown(f'*{result}*') 	            # Displaying the result in a markdown format
# ------------------------------------


# ----FUNCTION FOR INCLUDING GIF-------
def load_lottieurl(url):
	"""Displays a GIF when it's URL is given as argument .

	Args:
		url

	Returns:
		JSON response if the request was successful
	"""
	r = requests.get(url)
	if r.status_code != 200:
		return None
	return r.json()
# --------------------------------------


# -----DISPLAYING DECRIPTION AND GIF-----
des_col, gif_col = st.columns([2,3])      # Creating two columns with different ratios 
des_col.markdown('')          
des_col.markdown('')
des_col.markdown('')
des_col.markdown('This website can retrieve genomic information of variants from all known associations to **Type 1 Diabetes** in chromosome 6 of _Homo Sapiens_, and integrate them with population and functional information. It is capable of producing Manhattan plots and Linkage Disequilibrium analysis in this regard as well!')

with gif_col:       # Getting and displaying the gif
	lottie_coding = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_pc68hnwh.json")
	st_lottie(lottie_coding,height = 300, key = "geneticist")
# ---------------------------------------


# -----FRAMEWORK FOR GETTING AND STORING PRIMARY USER INPUT FOR TABULAR RESULT & OTHER ANALYSIS------
st.markdown('To get started, select the type of genomic information for which you want to retrive the information, from selection box below -')
st.markdown('')
selection = st.selectbox("label",("","rs value of SNP (eg - rs9273368, rs118124843)","Gene name (eg - HLA-DQA1, TRIM31)", "Genomic coordinates (chromosome, start and end). For eg 31110838, 90248512", "Region (eg - 6q22.31, 6q25.8, 6q27"), label_visibility = "collapsed")#, on_change = selection_function
sel_value = st.text_input("Enter the input/value for your above selection", value="")

# ---------------------------------------



# ------------TABLE FUNCTION-------------
def aggrid_interactive_table(df: pd.DataFrame):
	"""Creates an st-aggrid interactive table based on a dataframe.

	Args:
		df (pd.DataFrame]): Source dataframe

	Returns:
		dict: The selected row 
	"""
	options = GridOptionsBuilder.from_dataframe(
		df, enableRowGroup=True, enableValue=True, enablePivot=True
	)

	options.configure_side_bar()
	options.configure_pagination(paginationAutoPageSize=True)
	options.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children")
	
	selection = AgGrid(
		df,
		enable_enterprise_modules=True,
		gridOptions=options.build(),
		theme="streamlit",
		update_mode=GridUpdateMode.MODEL_CHANGED,
		allow_unsafe_jscode=True,
	)
	return selection
# --------------------------------------


# ------DATAFRAME TO CSV FUNCTION-------
@st.cache    # Caching the conversion to prevent computation on every rerun
def convert_df_to_csv(df):
	return df.to_csv().encode('utf-8')
# --------------------------------------


# -----DATAFRAME TO STRING FUNCTION-----
@st.cache
def convert_df_to_string(df):
	return df.to_string().encode('utf-8')
# --------------------------------------

# ----INFORMATION FOR LD CALCULATION----

african_populations = [
	"1000GENOMES:phase_3:ACB",
	"1000GENOMES:phase_3:ASW",
	"1000GENOMES:phase_3:ESN",
	"1000GENOMES:phase_3:GWD",
	"1000GENOMES:phase_3:LWK",
	"1000GENOMES:phase_3:MSL",
	"1000GENOMES:phase_3:YRI"
]

asian_populations = [
	"1000GENOMES:phase_3:BEB",
	"1000GENOMES:phase_3:CDX",
	"1000GENOMES:phase_3:CHB",
	"1000GENOMES:phase_3:CHS",
	"1000GENOMES:phase_3:GIH",
	"1000GENOMES:phase_3:ITU",
	"1000GENOMES:phase_3:JPT",
	"1000GENOMES:phase_3:KHV",
	"1000GENOMES:phase_3:PJL",
	"1000GENOMES:phase_3:STU"
]

european_populations = [
	"1000GENOMES:phase_3:CEU",
	"1000GENOMES:phase_3:FIN",
	"1000GENOMES:phase_3:GBR",
	"1000GENOMES:phase_3:IBS",
	"1000GENOMES:phase_3:TSI"
]
# ---------------------------------------

# --------LD RELATED FUNCTIONS--------

def map_population_to_ensembl_populations(population: str) -> list:
	'''Description:
	Maps population string to all ensembl populations with that ancestry.
	'''
	population = population.lower()
	if "asian" in population:
		return asian_populations
	elif "african" in population:
		return african_populations
	elif "european" in population:
		return european_populations
	

def calculate_ld_for_pair(rs_value_1: str, rs_value_2: str, population: str) -> tuple:

	'''Description: 
	Calculates r2 and d_prime for given rs values in a specified population.
	Population options are: european, african and asian.
	To increase the number of non-'NaN' responses we get, we go through every possible ancestry that coresponds
	to the given population iteratively, until we get a valid response.
	'''

	ensembl_populations = map_population_to_ensembl_populations(population)
	server = "https://rest.ensembl.org"
	ext = f"/ld/human/pairwise/{rs_value_1}/{rs_value_2}?population_name="

	# Try for each of the possible e_populations from the given list.
	for e_population in ensembl_populations:
		r = requests.get(server+ext+e_population, headers={ "Content-Type" : "application/json"})
		
		if not r.ok:
			# raise an error if the request fails
			r.raise_for_status()
		
		decoded = r.json()
		if decoded:
			response = decoded[0]
			return (float(response['r2']), float(response['d_prime']))
	
	# If we haven't received a result by now it means that ensembl doesn't contain the necessary information for this 
	# rs pair and we return NaN.
	return ("NaN", "NaN")


def calculate_pairwise_ld_for_list(rs_values, population):
	''' Description:
	Calculates pairwise rs values for given population for given list of rs_values. Displays tabular LD results,
	with the option to download them. Creates a heatmap of LD for all rs values with the option to download it.

	Args:
		Population options are: european, african and asian.
		Also accepts a single string as a population.
	Returns:
		None
	'''

	if isinstance(population, str):
		population = [population]

	possible_pairs = list(itertools.combinations(rs_values, 2))

	results = []
	for (rs1, rs2) in possible_pairs:
		for pop in population:
			(r2, d_prime) = calculate_ld_for_pair(rs1, rs2, pop)
			results.append([rs1, rs2, pop, r2, d_prime])
	
	df = pd.DataFrame(results, columns = ['SNP_1', 'SNP_2', 'Population', 'r\u00B2' , 'D\u0027']) #str(100) + 'cm' + '\u00B2'

	LD_download = convert_df_to_string(df)

	col1, col2, col3= st.columns(3)          # Creating and displaying download button for LD results
	col3.download_button(
	label="Download result",
	data = LD_download,
	file_name='LD result.txt',
	mime='text/plain',
	help = 'txt format',
	)

	st.dataframe(df)     # Displaying LD results in dataframe

	df['r\u00B2'] = df['r\u00B2'].astype(float)
	matrix = df.pivot(index='SNP_1', columns='SNP_2', values='r\u00B2')
	matrix = matrix.reindex(index=rs_values, columns=rs_values, fill_value=0)
	matrix = matrix.fillna(0)

	fig, ax = plt.subplots()

	im = ax.imshow(matrix, cmap="Reds") #Reds #YlOrRd

	# add colorbar
	cbar = ax.figure.colorbar(im, ax=ax)

	# set ticks and labels
	ax.set_xticks(np.arange(len(matrix.columns)))
	ax.set_yticks(np.arange(len(matrix.index)))
	ax.set_xticklabels(matrix.columns, rotation=90)
	ax.set_yticklabels(matrix.index)
	ax.set_title("Linkage Disequilibrium Heatmap")

	# Loop over data dimensions and create text annotations.
	for i in range(len(matrix.index)):
		for j in range(len(matrix.columns)):
			text = ax.text(j, i, round(matrix.iloc[i, j],2),
						   ha="center", va="center", color="black")

	plt.tight_layout()

	# Display the plot in Streamlit
	st.markdown("")
	st.markdown("Linkage Disequilibrium Heatmap for all $r^2$ values -") 		

	fn = 'LD_plot.png'     
	img = io.BytesIO()
	plt.savefig(img, format='png')
	 
	col1, col2, col3= st.columns(3)    # Creating and displaying download button for LD heatmap
	col3.download_button(
	   label="Download plot as png",
	   data=img,
	   file_name=fn,
	   mime="image/png",
	   help = 'png format'
	)

	st.pyplot(fig)
# --------------------------------------


# -------MANHATTAN PLOT FUNCTIONS-------

def map_populations_for_manhattan_plot(input_value: str) -> str:
	"""
	Maps `INITIAL SAMPLE SIZE` string to a population string.
	"""
	if "Asian" in input_value or "Japanese" in input_value or "Chinese" in input_value:
		return "Asian"
	elif "African" in input_value:
		return "African"
	elif "European" in input_value:
		return "European"
	else:
		# This shouldn't ever happen but just in case.
		return "Other"


def create_manhattan_plot(df: DataFrame):
	'''
	Creates and displays a Manhattan plot using mattplotlib based on the given data frame.
	The dataframe should contain pvalue, position and population columns.
	The postion column is used for the x_axis of the manhattan plot, whereas the population is used for grouping.
	'''
	population_column = "INITIAL SAMPLE SIZE"
	position_column = "CHR_POS"
	minus_log_10p_value = 'minuslog10pvalue'

	df[population_column] = df[population_column].map(lambda x: map_populations_for_manhattan_plot(x))
	df['P-VALUE'] = df['P-VALUE'].astype(float)
	df[minus_log_10p_value] = -np.log10(df['P-VALUE']) 
	# sort by position
	df = df.sort_values(position_column)

	# grouping allows us to separate the populations by color
	df_grouped = df.groupby(("INITIAL SAMPLE SIZE"))

	fig = plt.figure(figsize=(20,6))
	ax = fig.add_subplot()

	colors = ['#2176F0', '#FF42AB', '#76DB3E']

	legend_elements = []
	for num, (name, group) in enumerate(df_grouped):
		legend_elements.append(Line2D([0], [0], marker='o', color='w', label=name, markerfacecolor=colors[num], markersize=10))
		group.plot(kind='scatter', x=position_column, y=minus_log_10p_value, color=colors[num], ax=ax, s=50, alpha =0.5)
	
	ax.xaxis.set_major_locator(plt.MaxNLocator(15))
	# Bon Ferucci line
	plt.axhline(7.92, color='#AC94F5')
	ax.set_ybound(lower=0, upper=25)
	ax.legend(handles = legend_elements)
	ax.set_xlabel("Position within Chromosome 6")
	ax.set_ylabel("-log10 P-Value")
	ax.set_title('P-values by Chromosome Position')

	# Add minor grids
	ax.grid(b=True, which='minor', linestyle=':', alpha = 0.2, linewidth='2', color='gray')
	# Add major grids
	ax.grid(b=True, which='major', linestyle='-', alpha = 0.5, linewidth='1', color='gray')
	
	st.pyplot(fig)       # Displaying heatmap for LD

	fn = 'Manhattan_plot.png'   
	img = io.BytesIO()
	plt.savefig(img, format='png')
	 
	col1, col2, col3= st.columns(3)      # Creating and displaying download button for LD heatmap
	col3.download_button(
	   label="Download plot as png",
	   data=img,
	   file_name=fn,
	   mime="image/png",
	   help = 'png format'
	)

	
# --------------------------------------


# -----------RSVALUE FUNCTION-----------
def show_rsvalue(rsvalue):
	"""Fetches data from database for rs value given as argument, shows in an interactive tabular format
		which can be downloaded.

	Args:
		str: rs value of one SNP

	Returns:
		None
	"""

	# Connecting to database
	conn = sqlite3.connect('Database.db')

	# Creating cursor
	c = conn.cursor()
	# getting the required data from the vcfgb.db database
	c.execute(""" SELECT SNPS, REGION, CHR_POS, MAPPED_GENE, "P-VALUE", AF, EUR_AF, AFR_AF, SAS_AF, EAS_AF, AMR_AF, CADD_PHRED, GO   
				  FROM GWAS_CHR6 JOIN CHR6_EXTRA_INFORMATION
				  ON GWAS_CHR6.SNPS = CHR6_EXTRA_INFORMATION.SNPS1
				  WHERE SNPS = (?) """, (rsvalue,))

	items = c.fetchall()

	# If input from user (rs:ID) doesn't match data in the database, the below prompt is presented
	if items:
		headers = ["SNPS", "REGION", "CHR_POS", "MAPPED_GENE", "P-VALUE", "AF", "EUR_AF", "AFR_AF", "SAS_AF","EAS_AF", "AMR_AF", "CADD_PHRED", "GENE ONTOLOGY"]
		df = pd.DataFrame(items, columns=headers)
		st.write("Data for rsvalue: " + rsvalue + ":")

		csv = convert_df_to_csv(df)
		col1, col2, col3= st.columns(3)
		col3.download_button(
			label="Download table as CSV",
			data= csv,
			file_name='Table.csv',
			mime='csv',
			help = 'csv format'
			)

		selection_rsvalue = aggrid_interactive_table(df=df)

		if selection_rsvalue:
			st.write("You selected:")
			selected_rows = selection_rsvalue["selected_rows"]
			st.json(selected_rows)

	else:
		st.write("No matching rs ID found or incorrect input, please check your input and try again.")

	# Commiting command 
	conn.commit()

	# Closing connection
	conn.close()
# ---------------------------------------



# ----------GENE NAME FUNCTION-----------
def gene_name(gene):
	"""Fetches data from database for gene name given as argument, shows in an interactive tabular format
		which can be downloaded. If multiple SNPs are returned, user can select the SNPs of interest from the table,
		calculate linkage disequilibrium (LD) for each pair of SNPs, separately for each population, and plot their values.
		The results and plots can be downloaded.

	Args:
		str: gene name

	Returns:
		None
	"""

	#Connecting to the database
	conn = sqlite3.connect('Database.db')

	#Creating cursor
	c = conn.cursor()
	## getting the required data from the vcfgb.db database
	c.execute("""SELECT SNPS, REGION, CHR_POS, MAPPED_GENE, "P-VALUE", AF, EUR_AF, AFR_AF, SAS_AF, EAS_AF, AMR_AF, CADD_PHRED, GO     
				 FROM GWAS_CHR6 JOIN CHR6_EXTRA_INFORMATION
				 ON GWAS_CHR6.SNPS = CHR6_EXTRA_INFORMATION.SNPS1
				 WHERE MAPPED_GENE LIKE ? """, ('%' + gene + '%',))

	items = c.fetchall()

	if len(items) > 0:
		headers = ["SNPS", "REGION", "CHR_POS", "MAPPED_GENE", "P-VALUE", "AF", "EUR_AF", "AFR_AF", "SAS_AF","EAS_AF", "AMR_AF", "CADD_PHRED", "GENE ONTOLOGY"]
		df = pd.DataFrame(items, columns=headers)
		st.write("Data for gene name: " + gene + ":")

		csv = convert_df_to_csv(df)
		col1, col2, col3= st.columns(3)
		col3.download_button(
			label="Download table as CSV",
			data= csv,
			file_name='Table.csv',
			mime='csv',
			help = 'csv format'
			)

		selection_rsvalue = aggrid_interactive_table(df=df)

		if selection_rsvalue:
			st.write("You selected:")
			selected_rows = selection_rsvalue["selected_rows"]
			st.json(selected_rows)
			if len(selected_rows) > 1:
				df_selected = pd.DataFrame(selected_rows)
				selected_rsvalues = df_selected["SNPS"].tolist()


	if len(items) > 1:
		st.markdown("------------")
		st.markdown("**Linkage Disequilibrium(LD) calculator**")
		st.markdown("To calculate LD between SNPs and population of your choice - ") 
		st.markdown("- First, select the rows from the table above, which correspond to the SNPs of your choice")
		st.markdown("- Secondly, select the population of your choice from the selection box below")
		st.markdown('''
		<style>
		[data-testid="stMarkdownContainer"] ul{
			padding-left:40px;
		}
		</style>
		''', unsafe_allow_html=True)
		population_options = st.selectbox("Select the population",("","european_populations","asian_populations", "african_populations"))#, on_change = selection_function
		if selection_rsvalue and population_options:
			st.markdown("")
			st.markdown("Results for Linkage Disequilibrium:")
			LD = calculate_pairwise_ld_for_list(selected_rsvalues, population_options)

		else:
			st.warning("To calculate LD please select atleast two SNPs and one population")


	else:
		st.write("No matching gene name found, please check your input and try again.")

	#Commiting command 
	conn.commit()

	#Closing connection
	conn.close()
# --------------------------------------


# ------------REGION FUNCTION-----------
def show_region(region1, region2=None):
	"""Fetches data from database chromosome region/s given as argument, shows in an interactive tabular format
		which can be downloaded. If multiple SNPs are returned, user can select the SNPs of interest from the table,
		calculate linkage disequilibrium (LD) for each pair of SNPs, separately for each population, and plot their values.
		The results and plots can be downloaded.

	Args:
		str: chromosome region one and/or chromosome region two

	Returns:
		None
	"""

	# Connecting to database
	conn = sqlite3.connect('Database.db')
	
	# Creating cursor
	c = conn.cursor()
	
	# If region2 is None, assume that only one region was provided
	## getting the required data from the vcfgb.db database
	if region2 is None:
		query = """SELECT SNPS, REGION, CHR_POS, MAPPED_GENE, "P-VALUE", AF, EUR_AF, AFR_AF, SAS_AF, EAS_AF, AMR_AF, CADD_PHRED, GO      
				   FROM GWAS_CHR6 JOIN CHR6_EXTRA_INFORMATION
				   ON GWAS_CHR6.SNPS = CHR6_EXTRA_INFORMATION.SNPS1
				   WHERE REGION = ? """
		c.execute(query, (region1,))
	else:
		query = """SELECT SNPS, REGION, CHR_POS, MAPPED_GENE, "P-VALUE", AF, EUR_AF, AFR_AF, SAS_AF, EAS_AF, AMR_AF, CADD_PHRED, GO     
				   FROM GWAS_CHR6 JOIN CHR6_EXTRA_INFORMATION
				   ON GWAS_CHR6.SNPS = CHR6_EXTRA_INFORMATION.SNPS1
				   WHERE REGION BETWEEN ? AND ? """
		c.execute(query, (region1, region2))
		

	items = c.fetchall()
	
	st.write("Fetched", len(items), "items from the database.")
	
	# Ensuring data is present. If input from user doesn't match data in the database, the below prompt is presented
	if len(items) > 0:
		headers = ["SNPS", "REGION", "CHR_POS", "MAPPED_GENE", "P-VALUE", "AF", "EUR_AF", "AFR_AF", "SAS_AF","EAS_AF", "AMR_AF", "CADD_PHRED", "GENE ONTOLOGY"]
		st.write(f"Displaying data for region(s): {region1} - {region2}")
		df = pd.DataFrame(items, columns=headers)

		csv = convert_df_to_csv(df)
		col1, col2, col3= st.columns(3)
		col3.download_button(
			label="Download table as CSV",
			data= csv,
			file_name='Table.csv',
			mime='csv',
			help = 'csv format'
			)

		selection_rsvalue = aggrid_interactive_table(df=df)

		if selection_rsvalue:
			st.write("You selected:")
			selected_rows = selection_rsvalue["selected_rows"]
			st.json(selected_rows)
			if len(selected_rows) > 1:
				df_selected = pd.DataFrame(selected_rows)
				selected_rsvalues = df_selected["SNPS"].tolist()


	if len(items) > 1:
		st.markdown("------------")
		st.markdown("**Linkage Disequilibrium(LD) calculator**")
		st.markdown("To calculate LD between SNPs and population of your choice - ") 
		st.markdown("- First, select the rows from the table above, which correspond to the SNPs of your choice")
		st.markdown("- Secondly, select the population of your choice from the selection box below")
		st.markdown('''
		<style>
		[data-testid="stMarkdownContainer"] ul{
			padding-left:40px;
		}
		</style>
		''', unsafe_allow_html=True)
		population_options = st.selectbox("Select the population",("","european_populations","asian_populations", "african_populations"))#, on_change = selection_function
		if selection_rsvalue and population_options:
			st.markdown("")
			st.markdown("Results for Linkage Disequilibrium:")
			LD = calculate_pairwise_ld_for_list(selected_rsvalues, population_options)

		else:
			st.warning("To calculate LD please select atleast two SNPs and one population")

	else:
		st.write("No matching region found, please check your input and try again.")

	# Commiting command 
	conn.commit()
		
	# Closing connection
	conn.close()
# -----------------------------------------



# -------GENOMIC COORDINATES FUNCTION------

def chrpos(chrpos1, chrpos2=None):
	"""Fetches data from database chromosome region/s given as argument, shows in an interactive tabular format
		which can be downloaded. If multiple SNPs are returned, user can select the SNPs of interest from the table,
		calculate linkage disequilibrium (LD) for each pair of SNPs, separately for each population, and plot their values.
		The results and plots can be downloaded. If multiple SNPs are returned, a Manhattan plot of p-values is provided,
		which can be downloaded as well

	Args:
		str: genomic coordinate one and/or genomic coordinate two

	Returns:
		None
	"""

	#Connecting to database
	conn = sqlite3.connect('Database.db')

	#Creating cursor
	c = conn.cursor()


	#Swap values if chrpos2 is entered and chrpos1 is greater than chrpos2
	if chrpos2 is not None and chrpos1 > chrpos2:
		chrpos1, chrpos2 = chrpos2, chrpos1

	## getting the required data from the vcfgb.db database
	if chrpos2 is None:
		query = """SELECT SNPS, REGION, CHR_POS, MAPPED_GENE, "P-VALUE", AF, EUR_AF, AFR_AF, SAS_AF, EAS_AF, AMR_AF, CADD_PHRED, GO,"INITIAL SAMPLE SIZE" 
				   FROM GWAS_CHR6 JOIN CHR6_EXTRA_INFORMATION
				   ON GWAS_CHR6.SNPS = CHR6_EXTRA_INFORMATION.SNPS1
				   WHERE CHR_POS = ? 
				   ORDER BY CHR_POS ASC """
		c.execute(query, int(chrpos1),) # that extra ',' is important!
	else:
		query = """SELECT SNPS, REGION, CHR_POS, MAPPED_GENE, "P-VALUE", AF, EUR_AF, AFR_AF, SAS_AF, EAS_AF, AMR_AF, CADD_PHRED, GO,"INITIAL SAMPLE SIZE"   
				   FROM GWAS_CHR6 JOIN CHR6_EXTRA_INFORMATION
				   ON GWAS_CHR6.SNPS = CHR6_EXTRA_INFORMATION.SNPS1
				   WHERE CHR_POS BETWEEN ? AND ? 
				   ORDER BY CHR_POS ASC"""
		c.execute(query, (int(chrpos1), int(chrpos2),))


	items = c.fetchall()
	
	st.write("Fetched", len(items), "items from the database.")
	
	# Ensuring data is present and if it is data presented in a lovely table. If input from user doesn't match data in the database, 
	# the below prompt is presented

	if len(items) > 1:
		headers = ["SNPS", "REGION", "CHR_POS", "MAPPED_GENE", "P-VALUE", "AF", "EUR_AF", "AFR_AF", "SAS_AF","EAS_AF", "AMR_AF", "CADD_PHRED", "GENE ONTOLOGY", "INITIAL SAMPLE SIZE"]
		st.write(f"Displaying data for chromosome position(s): {chrpos1} - {chrpos2}")
		df = pd.DataFrame(items, columns=headers)
		df[["CHR_POS"]] = df[["CHR_POS"]].astype(str)
		subdf = df[["CHR_POS","P-VALUE","INITIAL SAMPLE SIZE"]]

		csv = convert_df_to_csv(df)
		col1, col2, col3= st.columns(3)
		col3.download_button(
			label="Download table as CSV",
			data= csv,
			file_name='Table.csv',
			mime='csv',
			help = 'csv format'
			)

		selection_rsvalue = aggrid_interactive_table(df=df)


		if selection_rsvalue:
			st.write("You selected:")
			selected_rows = selection_rsvalue["selected_rows"]
			st.json(selected_rows)
			if len(selected_rows) > 1:
				df_selected = pd.DataFrame(selected_rows)
				selected_rsvalues = df_selected["SNPS"].tolist()


	if len(items) > 1:
		st.markdown("------------")
		st.markdown("**Manhattan Plot**")
		st.markdown(f"Manhattan Plot for all the SNPs between genomic coordinates: {chrpos1}, {chrpos2}")
		manhattan_plot = create_manhattan_plot(subdf)


		st.markdown("------------")
		st.markdown("**Linkage Disequilibrium(LD) calculator**")
		st.markdown("To calculate LD between SNPs and population of your choice - ") 
		st.markdown("- First, select the rows from the table above, which correspond to the SNPs of your choice")
		st.markdown("- Secondly, select the population of your choice from the selection box below")
		st.markdown('''
		<style>
		[data-testid="stMarkdownContainer"] ul{
			padding-left:40px;
		}
		</style>
		''', unsafe_allow_html=True)
		population_options = st.selectbox("Select the population",("","european_populations","asian_populations", "african_populations"))#, on_change = selection_function
		if selection_rsvalue and population_options:
			st.markdown("")
			st.markdown("Results for Linkage Disequilibrium:")
			LD = calculate_pairwise_ld_for_list(selected_rsvalues, population_options)

		else:
			st.warning("To calculate LD please select atleast two SNPs and one population")

	else:
		st.write("No matching chromosome position(s) found or incorrect input, please check your input and try again.")


	#Commiting command 
	conn.commit()

	#Closing connection
	conn.close()
# ----------------------------------------



# --------PRIMARY USER INPUT FUNCTION WHICH CALLS ALL OTHER FUNCTIONS-------
def selection_function(selection,sel_value):
	"""Primary user input function which calls all other functions to display different functionalities on the website

	Args:
		str: selection of the type of query (eg - SNPS(rs value), gene name, genomic coordinates or SNP region)
		str: value for the type of query (eg, if SNPS is the type of query; rs9273368 can be it's value)

	Returns:
		Calls relevant functions to create and display a table/calculate LD/produce heatmap/display manhattan plot
	"""
	if selection == "rs value of SNP (eg - rs9273368, rs118124843)" and sel_value:
		return show_rsvalue(sel_value)

	if selection == "Gene name (eg - HLA-DQA1, TRIM31)" and sel_value:
		return gene_name(sel_value)

	if selection == "Genomic coordinates (chromosome, start and end). For eg 31110838, 90248512" and sel_value:
		chrpos1 = ''
		chrpos2 = None
		if ',' in sel_value:
			chrpos_parts = sel_value.split(',')
			chrpos1 = chrpos_parts[0].strip()
			chrpos2 = chrpos_parts[1].strip() if len(chrpos_parts) > 1 else None  #none if there is no comma
		else:
			chrpos_parts = sel_value.split("-")
			chrpos1 = chrpos_parts[0].strip()
		# ensuring that if the value is entered as an int it's converted to a float doing float(XXX) doesn't work
		# if chrpos1[-1:] != ".":
		# 	chrpos1+= ".0"
		# if chrpos2 is not None:
		# 	if chrpos2 [-1:] != ".":
		# 		chrpos2+= ".0"


		if chrpos2 is not None:
			return chrpos(chrpos1, chrpos2)
		else:
			return chrpos(chrpos1)

	if selection == "Region (eg - 6q22.31, 6q25.8, 6q27" and sel_value:
		region1 = ''
		region2 = None
		if ',' in sel_value:
			region_parts = sel_value.split(',')
			region1 = region_parts[0].strip()
			region2 = region_parts[1].strip() if len(region_parts) > 1 else None
		else:
			region_parts = sel_value.split("-")
			region1 = region_parts[0].strip()

		if region2:
			return show_region(region1, region2)
		else:
			return show_region(region1)

selection_function(selection,sel_value)
# ----------------------------------------



	













