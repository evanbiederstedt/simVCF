#!/usr/bin/env python3

## retrieve numbers and categories of variants from csv
## grab these numbers, check REF, and create ALT
## write info into a VCF

## inputs:
## --- hg annotation 
## --- corresponding hg reference
## --- # of mutations & type of variant


class VariantConverter:
	"""Given a certain annotation and corresponding reference, 
	convert the position of intended variants into genomic coordinates"""
