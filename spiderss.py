import feedparser
from readability import Document
import requests
import html2text
import re
import os
import time
from time import mktime
from datetime import datetime, timedelta
from config import base_directory, update_interval, max_age, verbose, feeds
import logging
import sys, getopt


'''
Output functions
'''

def log(text):
    if verbose:
        #logging.info(text)
        print('{} - {}'.format(datetime.now().strftime('%d.%m %H:%M'), text))


def error(text):
    #logging.error(text)
    print('{} - ERROR: {}'.format(datetime.now().strftime('%d.%m %H:%M'), text))


def print_logo():
    logo = '''
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
###### ###### ## #####  ###### ###### ###### ###### ######
##     ##  ## ## ##  ## ##     ##  ## ##  ## ##     ##
###### ###### ## ##  ## #####  ###### ###### ###### ######
    ## ##     ## ##  ## ##     ## ##  ## ##      ##     ##
###### ##     ## #####  ###### ##  ## ##  ## ###### ######
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    '''

    print(logo)

'''
Utility functions
'''

# Get content of a webpage
def get_html_content(url):
    response = requests.get(url)
    doc = Document(response.text)
    return doc.summary()


def html_to_markdown(html):
    return html2text.html2text(html)


# Get articles of a feed 
def get_articles(feed):
    try:
        feed = feedparser.parse(feed[2])
        return feed.entries
    except Exception as e:
        error('failed to get feed "{}: {}"'.format(feed[1], e.msg))
        return []


def write_to_file(filename, text):
    file = open(filename, 'w')
    file.write(text)
    file.close()


# Get filename from feedparser article
def get_filename(date, title):

    # Get date as single block
    date = date.strftime('%Y%m%d%H%M')

    # Get title as lowercase words concatenated with underscores
    title = re.sub('[^A-Za-z0-9 ]+', '', title.lower())
    title = re.sub(' ', '_', title)
    
    return '{}_{}.md'.format(date, title)


# Update feed
def update_feed(feed):

    category = feed[0]
    name = feed[1]

    log('updating feed "{}"'.format(name))

    feedpath_new = os.path.join(base_directory, category, name, 'new')
    feedpath_read = os.path.join(base_directory, category, name, 'read')
    if not os.path.exists(feedpath_new):
        os.makedirs(feedpath_new)
    if not os.path.exists(feedpath_read):
        os.makedirs(feedpath_read)

    articles = get_articles(feed)
    threshold_date = datetime.now() - timedelta(days = max_age)
    for a in articles:
        date = datetime.fromtimestamp(mktime(a.published_parsed))
        if date > threshold_date:
            filename = get_filename(date, a.title)
            if not os.path.exists(os.path.join(feedpath_new, filename)) and not os.path.exists(os.path.join(feedpath_read, filename)):
               text = html_to_markdown(get_html_content(a.link))
               write_to_file(os.path.join(feedpath_new, filename), text)


# Delete articles older than max_age
def delete_old_articles():

    threshold_date = datetime.now() - timedelta(days = max_age)
    for subdir, dirs, files in os.walk(base_directory):

        # Skip 'loved' directory
        if not os.path.join(base_directory, 'loved') in subdir:
            for file in files:
                 date = datetime.strptime(file[:12], '%Y%m%d%H%M')
                 if threshold_date > date:
                     os.remove(os.path.join(subdir, file))
    log('deleted old articles')


def initialize():

    # Create 'loved' directory if not existent
    lovedpath = os.path.join(base_directory, 'loved')
    if not os.path.exists(lovedpath):
        os.makedirs(lovedpath)


def crawl():

    # Main loop
    while True:
        for feed in feeds:
            update_feed(feed)
        delete_old_articles()
        time.sleep(update_interval * 60)

def get_help_message():
    return 'spiderrss.py | run'

def main(argv):

    print_logo()

    ## Get arguments
    #try:
    #    opts, args = getopt,getopt(argv, 'h', ['ifile=', 'ofile='])
    #except:
    #    print('spiderrss.py [ run | create_config <file> ]')

    #for opt, arg in opts:
    #    if opt == '-h':
    #        print('spiderrss.py [ run | create_config <file> ]')
        

    #initialize()
    #crawl()



if __name__ == '__main__':
    main(sys.argv[1:])

