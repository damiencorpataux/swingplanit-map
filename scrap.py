from bs4 import BeautifulSoup
import geocoder
import requests
import csv
import re

MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'September',
    'October',
    'November',
    'December'
]


# Get events summary

html = requests.get('https://www.swingplanit.com/').text
soup = BeautifulSoup(html, 'html.parser')

elements = soup.select('a[class="maintitles"]')
events = [{
        'name': element.select('[class="maintitle2"]')[0].getText(),
        'url': element.get('href'),
        'date': {
            'day': int(re.findall('^[0-9]+', element.select('[class="daycalendar"]')[0].getText())[0]),
            'month': 1+MONTHS.index(element.parent.parent.previous.previous.split(' ')[0]),
            'year': int(element.parent.parent.previous.previous.split(' ')[1])
        }
} for element in elements]

for event in events:
    print(event)
print(f'{len(events)} events')


# Get events detail

MONTHS_SHORT = [m[:3] for m in MONTHS]

events_detail = []
for i, event in enumerate(events):
    url = event['url']
    print (f'\n{i+1}/{len(events)} Getting {url}')
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')
    detail = {
        'name': soup.find('h2').text.strip(),
        'when': soup.find('span', string='When?').next.next.strip(),  
        'town': soup.find('span', string='Town:').next.next.strip(),
        'country': soup.find('span', string='Country:').next.next.strip(),
        'styles': soup.find('span', string='Styles:').next.next.strip(),  # FIXME: make a list
        'teachers': soup.find('span', string='Teachers:').next.next.next.text.strip(),
        'description': soup.select('div[class="scroll-pane2"]')[0].p.text,
        'url': soup.find('span', string='Website:').next.next.next.get('href')
    }

    # Add parsed date from/to
    date_from, date_to = re.findall('(\d+)\w+\s(\w+)\s(\d+)', detail['when']) # '10th Feb 2023 - 12th Feb 2023' to [('10', 'Feb', '2023'), ('12', 'Feb', '2023')]
    detail.update({
        'date-from': '-'.join(map(lambda v:str(v).zfill(2), [date_from[2], 1+MONTHS_SHORT.index(date_from[1]), date_from[0]])),
        'date-to': '-'.join(map(lambda v:str(v).zfill(2), [date_to[2], 1+MONTHS_SHORT.index(date_from[1]), date_to[0]]))
    })

    print(detail)
    events_detail.append(detail)

print(f'{len(events_detail)} events processed')


# Write events detail to csv

filename = 'events.csv'
print(f'\nWriting {len(events_detail)} events detail to csv file: {filename}')
with open(filename, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=list(events_detail[0].keys()))
    writer.writeheader()
    for detail in events_detail:
        writer.writerow(detail)
