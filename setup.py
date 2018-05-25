import setuptools

setuptools.setup(
    name="dcss_stats",
    version="0.0.7",
    url="https://github.com/oschwab/dcss_stats",

    author="OSchwab",
    author_email="olivier.schwab72@gmail.com",

    description="Statistics tool for Dungeon Crawl Stone Soup",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
