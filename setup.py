# TODO
# Find a better distribution tool. I HATE PYTHON ALREADY.

'''
# Based on setup.py from https://github.com/pypa/sampleproject

from setuptools import setup, find_packages

setup(
    name="nsaway",
    version="0.1.0",
    description="NSAway.",
    long_description="For a detailed description, see https://github.com/TheZ3ro/nsaway.",
    url="https://github.com/TheZ3ro/nsaway",
    author="TheZero",
    author_email="io@thezero.org",
    license="GPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="ids intrusion detection system",
    packages=find_packages(),
    data_files=[('/etc/nsaway.ini', ['config/nsaway.ini']),
                ('/usr/share/pixmaps/nsaway/', ['icons/nsaway_large.png','icons/nsaway_mini.png','icons/nsaway.png'])],
    entry_points={
        "console_scripts": [
            "nsaway = nsaway.nsaway:main",
        ],
    },
)
'''
