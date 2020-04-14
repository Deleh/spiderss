# spiderss

![spiderss logo](images/logo.png)

__spiderss__ is a plaintext RSS reader / crawler.
Articles are stored as Markdown files on the filesystem.

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
