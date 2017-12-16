## simVCF

generate germline and somatic variants in VCF format


https://www.gencodegenes.org/releases/19.html

Annotation downloaded via GENCODE
ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.chr_patch_hapl_scaff.annotation.gtf.gz

GENCODE reference:
ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/GRCh37.p13.genome.fa.gz



Dependencies: (create requirements.txt)

> pip install -r requirements.txt







This should work:
https://github.com/hammerlab/gtfparse

pre-process annotation files

    fname = ".../gencode.v19.chr_patch_hapl_scaff.annotation.gtf"
    from gtfparse import read_gtf_as_dataframe
    df = read_gtf_as_dataframe(fname)

    df = df.gene_name.unique() 

    foo = {"gene": ["BRCA2", "KRAS", "BRCA1", "TP53",], "variant_type": ["SNP", "SNP", "SNP", "SNP"], "number": [3, 4, 5, 1]  }
    df = pd.DataFrame(foo)


gene  number variant_type
0  BRCA2       3          SNP
1   KRAS       4          SNP
2  BRCA1       5          SNP
