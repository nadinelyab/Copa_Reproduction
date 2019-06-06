from setuptools import setup

setup(name='Pantheon Reproduction',
      version='0.1',
      description='Reproduce Pantheon Results',
      url= 'https://github.com/nadinelyab/Copa_Reproduction',
      author='Sawyer Birnbaum, Nadin El-Yabroudi',
      author_email='nadinelyab@gmail.com',
      license='MIT',
      packages=['pantheon-reproduction'],
      install_requires=[
	'pdfminer',
	'argparse',
	'pandas',
      'matplotlib',
      'ast'
      ],
      zip_safe=False)

