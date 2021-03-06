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

def retrieve_snp_positions(column):
    """For SNPs, retrieve 'number' positions between 'start' and 'end' """
    if int(column.number <= abs(int(column.end + 1) - int(column.start)):
        choice = np.random.choice(np.arange(column.start, column.end+1), column.number).tolist() 
    else:
        raise ValueError('Input variant *csv is formatted incorrectly. Number of SNPs exceeds area to place them. Check input *csv columns "number", "length" or "position" ')

    return choice

def retrieve_del_positions(column):
    """For DELs, retrieve bases from reference length 'length', /times 'number' """
    ## retrieve random starts, such that these ared placed within 'length'+1
    arr = column.end - column.start - (column.number - 1) * column.length
    if arr <= 0:
         raise ValueError('Input variant *csv is formatted incorrectly. Deletions cannot fit in the interval (start, end). Either "number" &/or "length" are too large, or the interval too short.')
    elif arr > column.number:
        raise ValueError('Input variant *csv is formatted incorrectly. There are too many deletions requested within the interval (start, end). Either "number" &/or "length" are too large, or the interval too short.')
    choice = np.random.choice(column.end - column.start - (column.number - 1) * column.length, column.number, replace=False) ## draw N==number amount of unique choices
    idx = np.argsort(choice)  ## return indices that sort the above
    ## now add the "spacing" from 'length' after the draws, to make sure deletions do not clash with each other
    choice[idx] += np.arange(column.start, column.start + column.length * column.number, column.length)
    return choice
  





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
    if set(['DUP']).issubset(variants['variant_type']):
        warnings.warn("Warning: DUP is implemented as an insertion of a nearby sequence of length=length.")

    ## if "position" exists, fill NA in "length" with 1
    if 'position' in variants.columns:
        if 'length' not in variants:   ## if "length" left empty, fill with 1 by default
            variants['length'] = 1
        else:
    	    variants['length'].fillna(1, inplace=True)
    

   
    if variants['position'].max() > 2.49e8:
        raise ValueError('Input variant *csv is formatted incorrectly. Value in `position` column greater than 2.49e8 bp, longer than the largest chromosome in the human reference. See README for formatting requirements.')

    ## check for required `length` column for insertions and deletions
    if set(['DEL', 'INS', 'DUP', 'INV', 'CNV', 'DUP:TANDEM', 'DEL:ME', 'INS:ME']).issubset(variants['variant_type']):
    	if 'length' not in variants:
    		variants['length'] = 1
        else:
            variants['length'].fillna(1, inplace=True)
    ## end = position if variant == SNP, else end = start + length
    variants['end'] = np.where(variants['variant_type']=='SNP', df['position'], df['start'] + df['length'])
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
        #CODE     match['new_variant_positions'] = match.query('variant_type == "SNP"').apply(retrieve_snp_positions, axis=1)
        ## convert df to dictionary
        #CODE     variants_dict = match.groupby('seqname')['new_variant_positions'].apply(sum).to_dict()
    else:
    	match = variants  ## if user didn't provide gene_names, the annotation isn't useful/needed
    	### must convert to variant dictionary
    	### every `chr` must become the key, and every position a value in the key
    	#CODE     variants_dict = match.groupby('start').agg(lambda x: x.values.tolist()).T
    return match


def generate_snps_dict(match_df):
    """Generate SNPs from match DataFrame, output variants_dict"""
    match_df['new_variant_positions'] = match_df.query('variant_type == "SNP"').apply(retrieve_snp_positions, axis=1)
    snps_only = match_df[match_df.variant_type == 'SNP']
    if 'gene_name' in snps_only.columns:
        variants_dict = snps_only.groupby('seqname')['new_variant_positions'].apply(sum).to_dict()
    else:
        variants_dict = match_df.groupby('start').agg(lambda x: x.values.tolist()).T
    return variants_dicts

def generate_del_dict(match_df):
    """Generate DELs from match DataFrame, output variants_dict"""


























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


def set_random_seed(seed_number):
    """Set numpy.random.seed for reproducible variant placements"""
    try:
        seed_input = int(seed_number)
    except:
        raise TypeError("Input must be a number!")
    return np.random.seed(seed=seed_input)


def main(args):
    ## check if seed set
    if args['seed'] is not None:
        set_random_seed(args['seed'])
    ## read in annotation of variants
    if args['reference']=='hg19' or args['reference']=='GRCh37':
        if args['annotation']=='GENCODE':
            annotation_gencode = pd.read_csv('../data/GENCODE_hg19_annotation_unique_gene_names.csv')
            vars = read_variant_inputs(args['input_variants'], annotation_gencode)
        elif args['annotation']=='Ensembl':
            annotation_ensembl = pd.read_csv('../data/ENSEMBL_Homo_sapiens.GRCh37.75_unique_gene_names.csv')
            vars = read_variant_inputs(args['input_variants'], annotation_ensembl)
        else:
            raise NotImplementedError('Error: "annotation" invalid. Only GENCODE and Ensembl annotations implemented.') 
    elif args['reference']=='hg38' or args['reference']=='GRCh38':
        if args['annotation']=='GENCODE':
            annotation_gencode = pd.read_csv('../data/GENCODE_annotation_unique_gene_names.csv')
            vars = read_variant_inputs(args['input_variants'], annotation_gencode)
        elif args['annotation']=='Ensembl':
            annotation_ensembl = pd.read_csv('../data/ENSEMBL_Homo_sapiens.GRCh37.75_unique_gene_names.csv')
            vars = read_variant_inputs(args['input_variants'], annotation_ensembl)
        else:
            raise NotImplementedError('Error: "annotation" invalid. Only GENCODE and Ensembl annotations implemented.') 
    else:
        raise NotImplementedError('Error: "reference" invalid. Only implemented with human genome reference hg19/GRCh37 or hg38/GRCh38.') 
    ref_alts = create_ref_alt_dict(vars, args['input_fasta'])
    write_vcf(ref_alts, args['output_vcf'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simulate VCF of somatic variants')
    parser.add_argument('-r','--reference', 
                        choices=['hg19', 'GRCh37', 'hg38', 'GRCh38'], 
                        type=str.lower,
                        default='hg19',
                        help='reference assembly; default hg19')
    parser.add_argument('-a','--annotation', 
                        choices=['GENCODE', 'Ensembl'], 
                        type=str.lower,
                        default='GENCODE',
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
    parser.add_argument('-s', '--seed',
                        help='set seed for numpy.random.seed()')
    args = vars(parser.parse_args())
    main(args)



