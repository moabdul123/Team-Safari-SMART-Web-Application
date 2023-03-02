import pandas as pd
import csv

### import GWAS dataset
gwas = pd.read_csv('E:/testgwas.tsv', sep='\t')

### filter for chromosome 6
gwaschr6 = gwas[gwas['CHR_ID'] == '6']

### remove duplicate SNPS, keeping the lowest p-value 
gwasp = gwaschr6.sort_values(by='P-VALUE') # sort the dataframe by p_value in ascending order
gwaspd = gwasp[gwasp.duplicated(subset='SNPS', keep=False) | (gwasp['STRONGEST SNP-RISK ALLELE'] != '?')] # keep only the rows where the rs_id is duplicated or the risk_allele is not "?"
gwaspdd = gwaspd.drop_duplicates(subset='SNPS', keep='first') # keep only the first row for each rs_id, which has the lowest p_value
gwaspdd = gwaspdd.sort_index(inplace=False) #returns original order of variants

### delete columns that are not needed
columns1 = ['INITIAL SAMPLE SIZE', 'REPLICATION SAMPLE SIZE', 'REGION', 'CHR_ID', 'CHR_POS', 'REPORTED GENE(S)', 'MAPPED_GENE', 'UPSTREAM_GENE_DISTANCE', 'DOWNSTREAM_GENE_DISTANCE', 'STRONGEST SNP-RISK ALLELE', 'SNPS', 'RISK ALLELE FREQUENCY', 'P-VALUE', 'PVALUE_MLOG', '95% CI (TEXT)']
gwasfinal = gwaspdd[columns1]

### save finalized CHR6 GWAS dataset
gwasfinal.to_csv("E:/GWAS_CHR6.tsv", sep="\t", index=False)

### import the Variant Effect Predictor (VEP) dataset
vep = pd.read_csv('E:/filteredgwasVEP.tsv', sep='\t')

### filter for chromosome 6
chr6vep = vep[vep['Location'].str.startswith('6:')]

### delete columns that are not needed
columns2 = ['#Uploaded_variation', 'Location', 'Allele', 'Consequence', 'BIOTYPE', 'DISTANCE', 'SIFT', 'PolyPhen', 'AF', 'AFR_AF', 'AMR_AF', 'EAS_AF', 'EUR_AF', 'SAS_AF', 'CLIN_SIG', 'CADD_PHRED', 'CADD_RAW', 'GO']
chr6vep = chr6vep[columns2]

### rename the #Uploaded_variation column to SNPS
chr6vep = chr6vep.rename(columns={'#Uploaded_variation': 'SNPS'})

### save the VEP dataset
chr6vep.to_csv("E:/CHR6_EXTRA_INFORMATION.tsv", sep="\t", index=False)