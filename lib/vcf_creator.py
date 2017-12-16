


from Bio import SeqIO
import re
import pandas as pd
import pickle
import numpy as np
import random
from collections import defaultdict
import datetime

inputFASTA = "/Users/ebiederstedt/Desktop/GENCODE_hg19_reference_annotation/UCSC/hg19_small.fa"
inputVARIANTS = "/Users/ebiederstedt/Downloads/gene_muts.csv"
outputVCF = "/Users/ebiederstedt/Desktop/GENCODE_hg19_reference_annotation/myfile.VCF"
annotation_file = pickle.load(open("/Users/ebiederstedt/Desktop/GENCODE_hg19_reference_annotation/unique_genes_hg19.p", "rb" ))


def retrieve_variant_positions(column):
    """Retrieve 'number' positions between 'start' and 'end' """
    return np.random.choice(np.arange(column.start, column.end+1), column.number).tolist() 


def read_fasta(input_fasta):
    """ Read in human genome reference FASTA"""
    genome = {}
    for seq_record in SeqIO.parse(input_fasta, "fasta"):
        genome[seq_record.id] = seq_record.upper().seq.tomutable()
    ## remove all 'useless' chromosomes, i.e. must match chrX, chrY or "^[a-z]{3}\d{1,2}$"
    genome = {k: v for k, v in genome.items() 
                    if re.match('^[a-z]{3}\d{1,2}$', k, re.IGNORECASE) or k in ["chrX", "chrY", "chrx", "chry"] or k in ["X", "Y", "x", "y"]}  
    return genome


def get_reference_bases(my_list):
	""" Convert REF base to ALT base such that REF != ALT""" 
    bases = set('ATCG')
    legend = {base:list(bases - set(base)) for base in bases}  ## key-value legend, `{'C': ['T', 'A', 'G'], ...`
    
    new_list = [random.choice(legend[base]) for base in my_list]
    return new_list[0]


def read_variant_inputs(variants_csv):
    """ Read csv of variants for VCF, outputs dictionary of all positions.
        If only gene names provided, randomly draw N variants between gene_start and gene_end"""
    variants = pd.read_csv(variants_csv)
    variants.columns = [x.lower() for x in variants.columns]  ## format into all lowercase
    ## check both mandatory column pairs exist
    col_pairs = [['gene', 'number'], ['chr', 'position']]
    for pair in col_pairs:
        if any(col in variants for col in pair) and all(col in variants for col in pair):
            break
        else:
            raise ValueError('Input variant *csv is formatted incorrectly. Mandatory columns must be included. See README for formatting requirements.')
    ## if "variant_type" left empty, fill with "SNP" by default
    if 'variant_type' not in variants:   
    	variants['variant_type'] = 'SNP'
    else:
    	variants['variant_type'].fillna('SNP', inplace=True)
    ## if "position" exists, fill NA in "length" with 1
    if 'position' in variants.columns:
        if 'length' not in variants:   ## if "length" left empty, fill with 1 by default
            variants['length'] = 1
        else:
    	    variants['length'].fillna(1, inplace=True)
    ## assume only SNP for now	    
    if 'length' in variants.columns:
        variants['end'] = variants['position']
    ### Adopt consistent name convention
    if 'gene' in variants.columns:
        variants = variants.rename(columns={'gene': 'gene_name'})   ## or re-write the annotation convention for 'gene' instead of 'gene_name'
    elif 'position' in variants.columns:
    	variants = variants.rename(columns={'chr': 'seqnames', 'position':'start'})  ## or re-write the annotation convertion for `chromosome` instead of `seqnames`
    ## subset annotation file to include chrom, start, end, and gene name at that position
    annotation = annotation[['seqname', 'start', 'end', 'gene_name']]   
    ## If gene, then find gene name and get N numbers between (start, end)
    if 'gene_name' in variants.columns:
        match = variants.merge(annotation, on='gene_name', how='left')
        ## randomly get N positions between (start, end)
        match['new_variant_positions'] = match.apply(retrieve_variant_positions, axis=1)
        ## convert df to dictionary
        variants_dict = match.groupby('seqname')['new_variant_positions'].apply(sum).to_dict()

    else:
    	match = variants  ## if user didn't provide gene_names, the annotation isn't useful/needed
    	### must convert to variant dictionary
    	### every `chr` must become the key, and every position a value in the key
    	variants_dict = match.groupby('start').agg(lambda x: x.values.tolist()).T

    return variants_dict


def create_ref_alt_dict(var_dict, reference):
    """ Input dictionary of variant positions and return dictionary of positions w/ REF and ALT"""
    sorted_dict = {key: sorted(val) for key, val in var_dict.items()} ## sort dict values, which are lists
    ## del var_dict
    d = defaultdict(list)
    for key, val in sorted_dict.items():
    	for position in val:
    		ref = reference[key][position]
    		alt = get_reference_bases(ref)
    		d[key][position].append(ref)    ## make `position` the key, REF first, ALT second
            d[key][position].append(alt)

    ## del sorted_dict
    return d

    

def write_vcf(ref_alt_dict, outputVCF):
    """Write VCF from dictionary of positions/REF/variants"""
    df = pd.DataFrame.from_records([[i, j] + ref_alt_dict[i][j] for i in ref_alt_dict for j in ref_alt_dict[i]])
    df.columns = ['CHROM', 'POS', 'REF', 'ALT']

    df['ID'] = 'SNP'  ## must change for more variants
    df['QUAL'] = 40
    df['FILTER'] = 'PASS'
    df['INFO'] = 'simulated'

    df = df[['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']] 

	now = datetime.datetime.now()

    header = '''##fileformat=VCFv4.1
    ##fileDate=''' + str(now.year) + str(now.day) + str(now.month) + '''
    ##source=myImputationProgramV3.1
    ##reference=file:///seq/references/ 
    #CHROM POS ID REF ALT QUAL FILTER INFO
    '''

    with open(outputVCF, 'w') as vcf:
        vcf.write(header)

    df.to_csv(outputVCF, sep='\t', mode='a', index=False)  ##  'a' appends to the end of the header above


