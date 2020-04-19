#!/usr/bin/env python

import argparse
import feedparser
import html2text
import os
import re
import requests
import subprocess
import sys
import time
import toml
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from readability import Document
from time import mktime
from urllib.parse import urlsplit, urlunsplit

'''
Output functions
'''

# Print log message
def log(text, force = False):
    if verbose or force:
        print('{} | {}'.format(datetime.now().strftime('%d.%m %H:%M'), text))


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

# Get articles of a feed 
def get_articles(feed):
    feed = feedparser.parse(feed['url'])
    return feed.entries


# Write text to file
def write_to_file(filepath, text):

    file = open(filepath, 'w')
    file.write(text)
    file.close()


# Get filename postfix from a title
def get_filename_postfix(title):

    # Get title as lowercase words concatenated with underscores
    title = re.sub('[^A-Za-z0-9 ]+', '', title.lower())
    title = re.sub(' ', '_', title)
    
    return '{}.{}'.format(title, fileending)


# Get HTML image snippet from the first image url in a text
def get_image_snippet(text):
    
    try:
        image_url = re.search('(?P<image>https?://\S+(\.png|\.jpg|\.jpeg))', text, re.IGNORECASE).group('image')
        return '<img src="{}" alt="Image">\n\n'.format(image_url)
    except:
        return ''


# Get HTML summary snippet from a HTML text 
def get_summary_snippet(text):

    try:
        h = html2text.HTML2Text()
        h.unicode_snob = True
        h.ignore_links = True
        h.ignore_images = True
        h.body_width = 0
        summary = h.handle(text).split('\n\n')[0].strip()
        return '<p><b>{}</b></p>\n\n'.format(summary)
    except:
        return ''


# Get article body either from web or its content
def get_article_body(article, scrape):

    body = ''

    # If scrape, get article with readability
    if scrape:

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'}
        response = requests.get(article.link, headers = headers)
        doc = Document(response.text)
        body = doc.summary()

        # Replace relative site links with absolute ones, using beautifulsoup
        splitted_url = urlsplit(article.link)
        soup = BeautifulSoup(body, features = 'lxml')
        for img in soup.find_all('img', src = True):
            src = img.get('src')
            splitted_src = urlsplit(src)
            constructed_src = [splitted_src.scheme, splitted_src.netloc, splitted_src.path, splitted_src.query, splitted_src.fragment]
            if constructed_src[0] == '':
                constructed_src[0] = splitted_url.scheme
            if constructed_src[1] == '':
                constructed_src[1] = splitted_url.netloc
            new_src = urlunsplit(constructed_src)
            if new_src.startswith('http'):
                body = body.replace('"{}"'.format(src), '"{}"'.format(new_src), 1)
            
        for a in soup.find_all('a', href = True):
            href = a.get('href')
            splitted_href = urlsplit(href)
            constructed_href = [splitted_href.scheme, splitted_href.netloc, splitted_href.path, splitted_href.query, splitted_href.fragment]
            if constructed_href[0] == '':
                constructed_href[0] = splitted_url.scheme
            if constructed_href[1] == '':
                constructed_href[1] = splitted_url.netloc
            new_href = urlunsplit(constructed_href)
            if new_href.startswith('http'):
                body = body.replace('"{}"'.format(href), '"{}"'.format(new_href), 1)
            

    # Else construct from article content
    else:
        
        if hasattr(article, 'content'):
            for c in article.content:
                if c.type == 'text/html':
                    body += c.value

    return body


# Postprocess HTML
def postprocess(text):

    try:
        processor = subprocess.Popen(postprocessor.split(' '), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        (output, err) = processor.communicate(input = text.encode())
        if err:
            raise Exception(err.decode().strip())
    except Exception as e:
        error('    while postprocessing: {}'.format(e))
        sys.exit(1)

    return output.decode().strip()


# Get constructed article
def get_article(article, scrape):

    # Get body of article
    body = get_article_body(article, scrape)

    # Construct head of article
    image = get_image_snippet(str(article))
    if image == '':
        image = get_image_snippet(body)
    summary = get_summary_snippet(article.summary)
    if summary == '':
        summary = get_summary_snippet(body)
    try:
        date = datetime.fromtimestamp(mktime(article.published_parsed)).strftime(datetime_format)
    except:
        date = datetime.now().strftime(datetime_format)
    head = '<h1>{}</h1>\n\n{}{}<p>{} - <a href={}>Link</a></p>'.format(article.title, image, summary, date, article.link)

    # Postprocess article
    article_text = postprocess('{}\n\n<hr>\n\n{}'.format(head, body)).strip()

    return article_text


# Update feed
def update_feed(feed):

    log('  updating feed "{}"'.format(feed['name']))

    # Set feedpaths
    feedpath_new = os.path.join(base_directory, feed['category'], feed['name'], 'new')
    feedpath_read = os.path.join(base_directory, feed['category'], feed['name'], 'read')
    
    if not os.path.exists(feedpath_new):
        os.makedirs(feedpath_new)
        
    if not os.path.exists(feedpath_read):
        os.makedirs(feedpath_read)

    # Get exisiting articles
    existing_articles = os.listdir(feedpath_new) + os.listdir(feedpath_read) + os.listdir(lovedpath)

    # Update articles
    articles = get_articles(feed)
    threshold_date = datetime.now() - timedelta(days = max_age)
    
    for a in articles:
        
        try:

            # Set fallback if no parseable date found
            fallback = False
            try:
                date = datetime.fromtimestamp(mktime(a.published_parsed))
            except:
                date = datetime.now()
                fallback = True
            
            if date > threshold_date:

                # Construct filename
                filename_prefix = date.strftime('%Y%m%d%H%M')
                filename_postfix = get_filename_postfix(a.title)
                filename = '{}_{}'.format(filename_prefix, filename_postfix)

                # Check if article exists
                article_exists = False
                if fallback:
                    existing_articles_fallback = [a[13:] for a in existing_articles]
                    if filename_postfix in existing_articles_fallback:
                        article_exists = True
                elif filename in existing_articles:
                    article_exists = True

                if not article_exists:
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

    global base_directory, max_age, datetime_format, postprocessor, fileending, feeds

    try:
        config = toml.load(filepath)
        base_directory = config['base_directory']
        max_age = config['max_age']
        datetime_format = config['datetime_format']
        postprocessor = config['postprocessor']
        fileending = config['fileending']
        feeds = config['feed']
    except Exception as e:
        error('while parsing config: {}'.format(e))
        sys.exit(1)


# Initialize spiderss
def initialize():

    global lovedpath

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
