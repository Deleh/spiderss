# spiderss - a plaintext RSS crawler

![spiderss logo](images/logo.png)

__spiderss__ is a plaintext RSS crawler, based on [feedparser](https://github.com/kurtmckee/feedparser), [python-readability](https://github.com/buriy/python-readability) and [html2text](https://github.com/Alir3z4/html2text).
Actually, it's just a python script.

Read the news you want, the way you want it.
Without advertisements, clickbait and trackers.
Drop unresponsive web interfaces and stop accepting cookies, because plaintext is God.

Articles are parsed as Markdown files from the original article web page and stored on the filesystem.

__Note:__ This script is under development and far from being complete.
Until now it works for the most feeds I read.
Use at your own risk!

## Features

- Store articles in categories
- Delete articles after a few days
- Distinguish __new__ from __read__ articles
- Store __loved__ articles forever
- OPML import

## Installation

Until now there is no install method, just ways to call the script.

### NixOS

Call `nix-shell` in the project directory. This will drop you into a python environment with all necessary requirements.

### Legacy OS

Install the requirements with `pip install -r requirements.txt`.

## Usage

```
./spiderss.py [-h] [-V] [-v] [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show version and exit
  -v, --verbose         verbose output
  -c CONFIG, --config CONFIG
                        config file (default: ./config.toml)
```

### Config

The config file is written in TOML.
Edit it to your liking before calling the script.

```
# This defines the base directory for the feeds. Please use an absolute path.
base_directory = '/home/<user>/rss'

# Articles older than max_age will be deleted and not be added
max_age = 30

# Feeds
# The category can be empty (''). The feed fill then be stored in the base_directory.
# The category can also be a path, which will result in subdirectories (e.g. 'technology/hardware').
# The name can also be empty (''). feeds with the same category will then be stored in the same directory.

[[feed]]
category = 'News'
name = 'Newssite'
url = 'https://example.org/feed'

[[feed]]
category = 'News'
name = 'Newssite 2'
url = 'https://example.org/feed'
```

### OPML import

Use the `opml2spiderss.py` script in the `script/` folder.
It prints the TOML format of the feeds to stdout.
You can append the feeds to your config e.g. the following way:

```
./opml2spiderss.py <your_feeds>.opml >> <your_config>.toml
```

### Keep articles up to date

Just create a cron job or a systemd.service, which calls the script every now and then. 

## How to read articles

Use your favourite Markdown viewer, or just the console.
__spiderss__ integrates nice with the [ranger](https://github.com/ranger/ranger) filemanager which eases navigating through complex folder structures.

## The folder structure

The script creates a folder structure the following way:

```
base_directory
| - category
    | - feedname
        | - new
        | - read
    | - another feedname
        | - new
        | - read
| - another category
    | - a third feedname
        | - new
        | - read
| - loved
```

Every feed gets a __new__ and a __read__ subfolder.
Article files are stored in the __new__ folder.
Move them to the __read__ folder if you're done reading them.
You can do this easily e.g. by setting a keybinding in ranger.

A special folder, called __loved__, is created on startup in the base_directory.
It is intended for articles, you want to keep.
Articles inside are never deleted, even if they expire the max_age.

Articles are stored in files with the name `YYYYMMDDHHmm_article_name.md`.
Thus articles are sorted by publishing date automatically.
