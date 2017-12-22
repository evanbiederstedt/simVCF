# simVCF

A python package that generates germline and somatic variants in VCF format

Dependencies: found in `requirements.txt`, please be sure to have them installed on your system.  The software package is written in Python and contained in the [lib folder](https://github.com/evanbiederstedt/simVCF/tree/master/lib). 

Please make sure that you are using the correct annotation for the input FASTA. 

## Installation

```
> pip install -r requirements.txt
```

## Usage
The user can provide their reference genome in FASTA format as input file to `vcf_creator.py`. Please use the appropriate annotation file, either `GENCODE` or `ENSEMBL`.

```
> cd lib
> python vcf_creator.py [-flags] <path/to/input_file>
```

To view the help options, type `-h`:
```
> python simuate_endToEnd.py -h
Usage: simulate_endToEnd.py [-h] [--reference REFERENCE_ASSEMBLY]
                            [--input_fasta INPUT_FASTA]
                            [--input_variants INPUT_VARIANTS]
                            [--output_vcf OUTPUT_VCF]
                            [--seed RANDOM_SEED]
                            
Simulate VCF of somatic variants

optional arguments:
  -h, --help            show this help message and exit
  --reference REFERENCE_ASSEMBLY
                        reference assembly; default hg19
  --input_fasta INPUT_FASTA
                        file path for the input (default genome) fasta
  --input_variants INPUT_VARIANTS
                        file path for the input *csv of variants
  --output_vcf OUTPUT_VCF
                        file path for the output VCF of somatic variants
  --seed RANDOM_SEED
                        set seed for numpy.random.seed()                       
```

[![Build Status](https://travis-ci.org/evanbiederstedt/simVCF.png?branch=master)](https://travis-ci.org/evanbiederstedt/simVCF)


