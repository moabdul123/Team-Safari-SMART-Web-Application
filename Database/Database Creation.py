import sqlite3
import csv
import pandas as pd

### create new database: Database.db
conn = sqlite3.connect("Database.db")

### create table for GWAS_CHR6 and CHR6_EXTRA_INFORMATION
cursor = conn.cursor()
conn.execute('''
CREATE TABLE IF NOT EXISTS GWAS_CHR6 (
    "INITIAL SAMPLE SIZE" INTEGER,
    "REPLICATION SAMPLE SIZE" INTEGER,
    "REGION" TEXT,
    "CHR_ID" TEXT,
    "CHR_POS" INTEGER,
    "REPORTED GENE(S)" TEXT,
    "MAPPED_GENE" TEXT,
    "UPSTREAM_GENE_DISTANCE" INTEGER,
    "DOWNSTREAM_GENE_DISTANCE" INTEGER,
    "STRONGEST SNP-RISK ALLELE" TEXT,
    "SNPS" TEXT PRIMARY KEY,
    "RISK ALLELE FREQUENCY" REAL,
    "P-VALUE" REAL,
    "PVALUE_MLOG" REAL,
    "95% CI (TEXT)" TEXT
)
''')

conn.execute('''
CREATE TABLE IF NOT EXISTS CHR6_EXTRA_INFORMATION (
    SNPS TEXT,
    Location TEXT,
    Allele TEXT,
    Consequence TEXT,
    BIOTYPE TEXT,
    DISTANCE INTEGER,
    SIFT TEXT,
    PolyPhen TEXT,
    AF REAL,
    AFR_AF REAL,
    AMR_AF REAL,
    EAS_AF REAL,
    EUR_AF REAL,
    SAS_AF REAL,
    CLIN_SIG TEXT,
    CADD_PHRED REAL,
    CADD_RAW REAL,
    GO TEXT,
    FOREIGN KEY (SNPS)
       REFERENCES GWAS_CHR6 (SNPS)
)
''')

### import GWAS_CHR6 dataset
GWASCHR6 = pd.read_csv('E:/GWAS_CHR6.tsv', header = 0, sep="\t")
GWASCHR6.to_sql('GWAS_CHR6', if_exists='append', index=False, con=conn)

### import CHR6_EXTRA_INFORMATION dataset
CHR6_EXTRA_INFORMATION = pd.read_csv('E:/CHR6_EXTRA_INFORMATION.tsv', header = 0, sep="\t")
CHR6_EXTRA_INFORMATION.to_sql('CHR6_EXTRA_INFORMATION', if_exists='append', index=False, con=conn)

conn.close()