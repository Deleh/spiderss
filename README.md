# spiderss - a plaintext RSS crawler

![spiderss logo](images/logo.png)

__spiderss__ is a plaintext RSS crawler, based on [feedparser](https://github.com/kurtmckee/feedparser), [python-readability](https://github.com/buriy/python-readability) and [html2text](https://github.com/Alir3z4/html2text)
Articles are parsed as Markdown files from the original article web page and stored on the filesystem.

## Features

- Categories
- Delete articles after a few days
- Distinguish _new_ from _read_ articles
- Store _loved_ articles forever
- OPML import

## Installation

### NixOS

Just call `nix-shell` in the project directory.

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

The config file is written in TOML and has the following variables:

__base_dir__: The base directory where your articles are stored.

__max_age__: The amount of days, your articles are kept on the filesystem. Articles in the __loved__ folder are skipped.

__[[feed]]__: Is a feed element. It has the following attributes:\
__category__: Category of the feed.\
__name__: Name of the feed.\
__url__: URL of the feed.

## Why?

Because plaintext is God.

## How can I read the articles?

Use your favourite Markdown viewer, or just the console.
__spiderss__ integrates nice with the [ranger](https://github.com/ranger/ranger) filemanager to browse categories.

## How does it work?

Edit the `config.toml` file to your liking and run the script.
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
