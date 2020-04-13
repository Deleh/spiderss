import feedparser
from readability import Document
import requests
import html2text
import re
import os
from time import mktime
from datetime import datetime, timedelta

feeds = [('News', 'Tagesschau', 'https://www.tagesschau.de/xml/rss2'),
         ('Linux', 'NixOS', 'https://nixos.org/blogs.xml'),
         ('News', 'Vice', 'https://www.vice.com/de/rss')
         ]

out_directory = './out'
delta = 365


# Get content of a webpage
def get_html_content(url):
    response = requests.get(url)
    doc = Document(response.text)
    return doc.summary()


def html_to_markdown(html):
    return html2text.html2text(html)


# Get articles of a RSS feed 
def get_articles(url):
    feed = feedparser.parse(url)
    return feed.entries


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
    url = feed[2]

    feedpath_new = os.path.join(out_directory, category, name, 'new')
    feedpath_read = os.path.join(out_directory, category, name, 'read')
    if not os.path.exists(feedpath_new):
        os.makedirs(feedpath_new)
    if not os.path.exists(feedpath_read):
        os.makedirs(feedpath_read)

    articles = get_articles(url)
    threshold_date = datetime.now() - timedelta(days = delta)
    for a in articles:
        date = datetime.fromtimestamp(mktime(a.published_parsed))
        if date > threshold_date:
            filename = get_filename(date, a.title)
            if not os.path.exists(os.path.join(feedpath_new, filename)) and not os.path.exists(os.path.join(feedpath_read, filename)):
               text = html_to_markdown(get_html_content(a.link))
               write_to_file(os.path.join(feedpath_new, filename), text)


# Delete articles older than day delta
def delete_old_articles():

    threshold_date = datetime.now() - timedelta(days = delta)
    for subdir, dirs, files in os.walk(out_directory):

        # Skip 'loved' directory
        if not os.path.join(out_directory, 'loved') in subdir:
            for file in files:
                 date = datetime.strptime(file[:12], '%Y%m%d%H%M')
                 if threshold_date > date:
                     os.remove(os.path.join(subdir, file))



def main():
    lovedpath = os.path.join(out_directory, 'loved')
    if not os.path.exists(lovedpath):
        os.makedirs(lovedpath)
    for feed in feeds:
        update_feed(feed)
    delete_old_articles()



if __name__ == '__main__':
    main()

