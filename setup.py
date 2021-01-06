import os
from setuptools import setup, find_packages

requires = ['aiohttp==3.6.3',
            'async-timeout==3.0.1',
            'attrs==20.3.0',
            'beautifulsoup4==4.8.2',
            'certifi==2020.12.5',
            'chardet==3.0.4',
            'cycler==0.10.0',
            'discord.py==1.5.1',
            'idna==2.10',
            'kiwisolver==1.3.1',
            'lxml==4.6.2',
            'matplotlib==3.3.3',
            'multidict==4.7.6',
            'numpy==1.19.4',
            'pyparsing==2.4.7',
            'python-dateutil==2.8.1',
            'six==1.15.0',
            'soupsieve==2.0.1',
            'typing-extensions==3.7.4.3',
            'wincertstore==0.2',
            'yarl==1.5.1',
            'progressbar==2.5',
            'SQLAlchemy==1.3.22',
            'mypy==0.790',
            'flake8==3.8.4']

with open('bodega_bot/version.py') as in_file:
    exec(in_file.read())

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name='bodega-bot',
      version=__version__,
      description=("bodega-bot is a Discord bot that can be configured to monitor and produce"
                   " humorous analytics for Discord channels."),
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/UltimoBodega/discord_analytics',
      author='Ultimo Bodega',
      author_email='ultimobodega@gmail.com',
      license='Public domain',
      packages=find_packages(exclude=['tests']),
      install_requires=requires,
      entry_points={'console_scripts': ['bodega-bot=bodega_bot.bodega_bot:main'],},
      zip_safe=False,
      keywords=['Discord', 'bot', 'monitor', 'analytics', 'humorous', 'quotes', 'channel'])