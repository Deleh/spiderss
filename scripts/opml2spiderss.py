#!/usr/bin/env python

import argparse
import opml
import os
import sys

# Prints elements recursively for all outlines
def print_outline(outline, category):
    if len(outline) > 0:
        for o in outline:
            print_outline(o, os.path.join(category, outline.text))
    else:
        print('[[feed]]')
        print('category = \'{}\''.format(category))
        print('name = \'{}\''.format(outline.text))
        print('url = \'{}\''.format(outline.xmlUrl))
        print('scrape = false')
        print('') 

'''
Main
'''

def main():

    parser = argparse.ArgumentParser(description = 'Read an OPML file and print spiderss TOML format to stdout.')
    parser.add_argument('file', help = 'OPML input file')
    args = parser.parse_args()

    file = args.file

    try:
        outline = opml.parse(file)
        for o in outline:
            print_outline(o, '')
    except Exception as e:
        print('ERROR: {}'.format(e))
        sys.exit(1)
    

if __name__ == '__main__':
    main()
