#!/usr/bin/env python3

## retrieve numbers and categories of variants from csv
## grab these numbers, check REF, and create ALT
## write info into a VCF

## inputs:
## --- hg annotation 
## --- corresponding hg reference
## --- # of mutations & type of variant

### type 1 *csv --- gene, number, variant_type (default nothing)

##     gene  number variant_type
## 0  BRCA2       3          SNP
## 1   KRAS       4          SNP
## 2  BRCA1       5          SNP


## type 2 *csv --- chr, position, variant_type

##     chr   position1  position2   variant_type   (if it's a DEL/INS, require position 2)
## 0   21    12345       (blank)     SNP
## 1   19    45668        45668      SNP
## 2   4     33425                   SNP






class VariantConverter:
	"""Given a certain annotation and corresponding reference, 
	convert the position of intended variants into genomic coordinates"""


