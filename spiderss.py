#!/usr/bin/env python

import argparse
import feedparser
import html2text
import os
import re
import requests
import sys
import time
import toml
from datetime import datetime, timedelta
from readability import Document
from time import mktime

'''
Output functions
'''

# Print log message
def log(text, force = False):
    if verbose or force:
        print('{} - {}'.format(datetime.now().strftime('%d.%m %H:%M'), text))


# Print error message and exit
def error(text):
    print('{} E {}'.format(datetime.now().strftime('%d.%m %H:%M'), text))


# Print spiderss logo
def print_logo():
    logo = '''
                          ;:                                                    
                         .N' ,K:                                                
         ,O                  .0MWx'                               lk         0; 
    ,kl;';O  lx. .xc    :k,    .kMMXl.c    .:x.   .xl .dl    :kl,'oo   .xd:,,O. 
  kNOokOWc  ;WMKccXMX  .WMX.  :XM,,OMMl  oXMcNMd 'oMMk:XW:.OWddO0N,  cKNlkONk   
  MMo  0c    KMK  :MM'  XMO   oMM.  MMl  cMM. ON: .MMl    'MM, .K'   OMX  oO    
  WMWxOWMN:  KMK  ;MM'  XMO   oMM.  MMl  cMM:c;   .MMl    .WMXx0MMX. xMMOkNMWk  
   'X; .MMo  KMK  ;MM'  XMO   oMM.  MMl  cMM,     .MMl      :X. ;MM,  .0d  0MX  
  .Kdc:'MMo.oNMNl;lMW. .WM0   KMMk:'MMl  dMM:  .. cMMk.'   ,Xlc;cMM,  xOl:'KMX  
 ;kddkNKl.   XMNkWk,    :N0;  .'cOW0c.   ,lOW0;   .:0Nl.  okddOW0:. .kdoxXNd,   
             WMX                                                                
            ;..cc                                                               
    '''

    print(logo)

'''
Utility functions
'''

# Get readable HTML of a webpage
def get_readable_html(url):
    response = requests.get(url)
    doc = Document(response.text)
    return doc.summary()


# Convert HTML to Markdown
def html_to_markdown(html):
    h = html2text.HTML2Text()
    h.unicode_snob = True
    h.ignore_links = True
    h.ignore_images = False
    #h.ignore_anchors = True
    #h.skip_internal_links = True
    #h.protect_links = True
    #h.use_automatic_links = True
    h.body_width = 0
    return h.handle(html).strip()


# Get articles of a feed 
def get_articles(feed_url):
    feed = feedparser.parse(feed_url)
    return feed.entries


# Write text to file
def write_to_file(filename, text):
    file = open(filename, 'w')
    file.write(text)
    file.close()


# Get filename from a date and a title
def get_filename(date, title):

    # Get date as single block
    date = date.strftime('%Y%m%d%H%M')

    # Get title as lowercase words concatenated with underscores
    title = re.sub('[^A-Za-z0-9 ]+', '', title.lower())
    title = re.sub(' ', '_', title)
    
    return '{}_{}.md'.format(date, title)


# Get summary snippet for an article
def get_article_summary(article):
    try:
        h = html2text.HTML2Text()
        h.unicode_snob = True
        h.ignore_links = True
        h.ignore_images = True
        #h.ignore_anchors = True
        #h.skip_internal_links = True
        h.body_width = 0
        summary = h.handle(article.summary).split('\n\n')[0].strip()
        return '**{}**\n\n'.format(summary)
    except:
        return ''


# Get image snippet for an article
def get_article_image(article):
    try:
        image_url = re.search('(?P<image>https?://\S+(\.png|\.jpg|\.jpeg))', str(article), re.IGNORECASE).group('image')
        return '![Image]({})\n\n'.format(image_url)
    except:
        return ''


# Get text from an article
def get_article(article, scrape):

    # Construct head of article
    image_url = get_article_image(article)
    date = datetime.fromtimestamp(mktime(article.published_parsed)).strftime(datetime_format)
    head = '# {}\n\n{}{}{} - [Link]({})'.format(article.title, image_url, get_article_summary(article), date, article.link)

    # Get body of article
    if scrape:
        body_html = get_readable_html(article.link)
    else:
        body_html = ''
        if hasattr(article, 'content'):
            for c in article.content:
                if c.type == 'text/html':
                    body_html += c.value

    body = html_to_markdown(body_html)

    return '{}\n\n---\n\n{}'.format(head, body)
    

# Update feed
def update_feed(feed):

    log('  updating feed "{}"'.format(feed['name']))

    feedpath_new = os.path.join(base_directory, feed['category'], feed['name'], 'new')
    feedpath_read = os.path.join(base_directory, feed['category'], feed['name'], 'read')
    if not os.path.exists(feedpath_new):
        os.makedirs(feedpath_new)
    if not os.path.exists(feedpath_read):
        os.makedirs(feedpath_read)

    articles = get_articles(feed['url'])
    threshold_date = datetime.now() - timedelta(days = max_age)
    for a in articles:
        try:
            date = datetime.fromtimestamp(mktime(a.published_parsed))
            if date > threshold_date:
                filename = get_filename(date, a.title)
                if not os.path.exists(os.path.join(feedpath_new, filename)) and not os.path.exists(os.path.join(feedpath_read, filename)):
                    text = get_article(a, feed['scrape'])
                    write_to_file(os.path.join(feedpath_new, filename), text)
                    log('    added article "{}"'.format(a.title))
        except Exception as e:
            error('while parsing feed article "{}" from feed "{}": {}'.format(a.title, feed['name'], e))


# Delete articles older than max_age
def remove_old_articles():

    threshold_date = datetime.now() - timedelta(days = max_age)
    count = 0
    
    for subdir, dirs, files in os.walk(base_directory):

        # Skip 'loved' directory
        if not os.path.join(base_directory, 'loved') in subdir:
            for file in files:
                 date = datetime.strptime(file[:12], '%Y%m%d%H%M')
                 if threshold_date > date:
                     os.remove(os.path.join(subdir, file))
                     count += 1

    log('  removed {} articles'.format(count))

# Parse config file
def load_config(filepath):

    global base_directory, max_age, datetime_format, feeds

    try:
        config = toml.load(filepath)
        base_directory = config['base_directory']
        max_age = config['max_age']
        datetime_format = config['datetime_format']
        feeds = config['feed']
    except Exception as e:
        error('while parsing config: {}'.format(e))
        sys.exit(1)


# Initialize spiderss
def initialize():

    # Create 'loved' directory if not existent
    lovedpath = os.path.join(base_directory, 'loved')
    if not os.path.exists(lovedpath):
        os.makedirs(lovedpath)


# Update all feeds and delete old messages
def crawl():

    log('crawling feeds', True)
    for feed in feeds:
        update_feed(feed)

    log('removing old articles', True)
    remove_old_articles()

'''
Main
'''

def main():

    global verbose

    # Initialize parser
    parser = argparse.ArgumentParser(description = 'Crawl RSS feeds and store articles as Markdown files.')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'verbose output')
    parser.add_argument('-c', '--config', default = './config.toml', help = 'config file (default: ./config.toml)')

    # Get args
    args = parser.parse_args()
    verbose = args.verbose
    config = args.config

    # Main routine
    print_logo()
    load_config(config)
    initialize()
    crawl()


if __name__ == '__main__':
    main()
