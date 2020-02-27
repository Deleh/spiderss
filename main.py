import bs4
import feedparser
import urllib.request

# Get content of a webpage
def get_content(url):
    page = urllib.request.Request(url, headers = {'User-Agent': 'Mozilla/5.0'})
    infile = urllib.request.urlopen(page).read()
    data = infile.decode('ISO-8859-1')
    soup = bs4.BeautifulSoup(data,features = 'html.parser')
    return soup

# Get entries of a RSS feed 
def get_entries(url):
    feed = feedparser.parse(url)
    return feed.entries

def main():
    entries = get_entries("https://nixos.org/blogs.xml")
    for e in entries:
        print(e.title)
    print(get_content(entries[0].link))



if __name__ == '__main__':
    main()

