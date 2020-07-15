#!/usr/bin/env python

from setuptools import setup, find_packages
import ite8291r3_ctl

with open("README.md") as f:
	long_description = f.read()


setup(
	name='ite8291r3-ctl',
	version=ite8291r3_ctl.__version__,
	description='ITE 8291 (rev 0.03) userspace driver',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/pobrn/ite8291r3-ctl',
	license='GPLv2',
	
	author='Barnabás Pőcze',
	author_email='pobrn@protonmail.com',
	
	keywords=['ITE', 'ITE8291', 'RGB', 'keyboard', 'backlight', 'linux'],
	
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
		'Natural Language :: English',
		'Operating System :: POSIX :: Linux',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.6',
		'Topic :: System :: Hardware :: Hardware Drivers',
		'Topic :: Utilities',
	],
	
	entry_points={
		'console_scripts': ['ite8291r3-ctl = ite8291r3_ctl.__main__:main'],
	},
	
	
	packages=find_packages(),
	
	python_requires='>=3.6',
	
	install_requires=[
		'pyusb',
	],
	
	extras_require={
		'mode-screen': ['python-xlib', 'Pillow'],
	},
	
	project_urls={
		'Source': 'https://github.com/pobrn/ite8291r3-ctl',
		'Bug Reports': 'https://github.com/pobrn/ite8291r3-ctl/issues',
	}
)
