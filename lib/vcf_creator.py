import re
import numpy as np
import pandas as pd
import pickle
import random
import datetime
import argparse
import warnings
from collections import defaultdict
from Bio import SeqIO


def retrieve_variant_positions(column):
    """Retrieve 'number' positions between 'start' and 'end' """
    if int(column.number <= abs(int(column.end + 1) - int(column.start)):
        choice = np.random.choice(np.arange(column.start, column.end+1), column.number).tolist() 
    else:
        raise ValueError('Input variant *csv is formatted incorrectly. Number of variants exceeds area to place them.')

    return choice

def read_fasta(input_fasta):
    """ Read in human genome reference FASTA"""
    genome = {}
    for seq_record in SeqIO.parse(input_fasta, "fasta"):
        genome[seq_record.id] = seq_record.upper().seq.tomutable()
    ## remove all 'useless' chromosomes, i.e. must match chrX, chrY or "^[a-z]{3}\d{1,2}$"
    genome = {k: v for k, v in genome.items() 
                    if re.match('^[a-z]{3}\d{1,2}$', k, re.IGNORECASE) or k in ['chrX', 'chrY', 'chrx', 'chry'] or k in ['X', 'Y', 'x', 'y']}  
    return genome


def get_reference_bases(my_list):
	""" Convert REF base to ALT base such that REF != ALT""" 
    bases = set('ATCG')
    legend = {base:list(bases - set(base)) for base in bases}  ## key-value legend, `{'C': ['T', 'A', 'G'], ...`
    
    new_list = [random.choice(legend[base]) for base in my_list]
    return new_list[0]


def read_variant_inputs(variants_csv, annotation_file):
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
    ## check elements in "variant_type" are valid
    if not set(['SNP', 'DEL', 'INS', 'DUP', 'INV', 'CNV', 'DUP:TANDEM', 'DEL:ME', 'INS:ME']).issubset(variants['variant_type']):
        raise ValueError('Input variant *csv is formatted incorrectly. The "variant_type" column must contain correctly labeled variants. See README for formatting requirements.')
    if set(['DEL:ME']).issubset(variants['variant_type']):
        warnings.warn("Warning: DEL:ME denotes a deletion of mobile element relative to the reference. This needs to be implemented by the user.")
    if set(['INS:ME']).issubset(variants['variant_type']):
        warnings.warn("Warning: INS:ME denotes an insertion of mobile element relative to the reference. This needs to be implemented by the user.")

    ## if "position" exists, fill NA in "length" with 1
    if 'position' in variants.columns:
        if 'length' not in variants:   ## if "length" left empty, fill with 1 by default
            variants['length'] = 1
        else:
    	    variants['length'].fillna(1, inplace=True)

    if variants['position'].max() > 2.49e8:
        raise ValueError('Input variant *csv is formatted incorrectly. Value in `position` column greater than 2.49e8 bp, longer than the largest chromosome in the human reference. See README for formatting requirements.')

    ## check for required `length` column for insertions and deletions
    if ((variants['variant_type'] == 'INS') or (variants['variant_type'] == 'DEL')).any():
    	if 'length' not in variants:
    		raise ValueError('Input variant *csv is formatted incorrectly. Mandatory `length` column must be included for INS and DEL. See README for formatting requirements.')
    ## assume only SNP for now	
    ## this appears unnecessary    
    ## if 'length' in variants.columns:
    ##    variants['end'] = variants['position']
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

    del sorted_dict
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



def main(args):
    ## read in annotation of variants
    if args['annotation']=='GENCODE':
        annotation_gencode = pd.read_csv('../data/GENCODE_annotation_unique_gene_names.csv')
        vars = read_variant_inputs(args['input_variants'], annotation_gencode)
    elif args['annotation']=='Ensembl':
        annotation_ensembl = pd.read_csv('../data/ENSEMBL_Homo_sapiens.GRCh37.75_unique_gene_names.csv')
        vars = read_variant_inputs(args['input_variants'], annotation_ensembl)
    else:
        raise NotImplementedError('Only GENCODE and Ensembl annotations implemented.') 
    ref_alts = create_ref_alt_dict(vars, args['input_fasta'])
    write_vcf(ref_alts, args['output_vcf'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulate VCF of somatic variants')
    parser.add_argument('-a','--annotation', 
                        choices=['GENCODE', 'Ensembl'], 
                        type=str.lower,
                        help='annotation flag corresonding to input_fasta')
    parser.add_argument('-i','--input_fasta', 
                        default='../data/subsampled_hg38.fa',
                        help='file path for the input (default genome) fasta')
    parser.add_argument('-v', '--input_variants',
                        default='../data/somatic_variants.csv',
                        help='file path for the input *csv of variants')
    parser.add_argument('-o', '--output_vcf',
                        default = 'outputs/somatic.VCF',
                        help='file path for the output VCF of somatic variants')
    args = vars(parser.parse_args())
    main(args)



