# This defines the base directory for the feeds relative to this config file
base_directory = '/home/denis/spiderrss'

# Update interval in minutes
update_interval = 15

# Articles older than max_age will be deleted and not be added
max_age = 365

# Enable verbose output
verbose = True

# Feeds in the form (category, name, url) - the category can be empty ('')
feeds = [
    ('News', 'Tagesschau', 'https://www.tagesschau.de/xml/rss2'),
    ('News', 'Vice', 'https://www.vice.com/de/rss'),
]
