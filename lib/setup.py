
import os
import re

from setuptools import setup, find_packages

readme_filename = "README.md"
current_directory = os.path.dirname(__file__)
readme_path = os.path.join(current_directory, readme_filename)

readme = ""
try:
    with open(readme_path, 'r') as f:
        readme = f.read()
except Exception as e:
    print(e)
    print("Failed to open %s" % readme_path)

try:
    import pypandoc
    readme = pypandoc.convert(readme, to='rst', format='md')
except Exception as e:
    print(e)
    print("Failed to convert %s from Markdown to reStructuredText" % readme_filename)

with open('gtfparse/__init__.py', 'r') as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        f.read(),
        re.MULTILINE).group(1)

if __name__ == '__main__':
    setup(
        name='simVCF',
        packages=find_packages(),
        version=version,
        description="Somatic VCF simualtion",
        long_description=readme,
        url="https://github.com/evanbiederstedt/simVCF",
        author="Evan Biederstedt",
        license="https://github.com/evanbiederstedt/simVCF/blob/master/LICENSE",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
        install_requires=[
            'pandas>=0.20',
        ],
    )
