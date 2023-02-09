import geocoder
import csv
import re

def clean(string):
    string = re.sub('\(.*$', '', string).strip()  # remove anything after "("
    string = re.sub(',.*$', '', string).strip()  # remove anything after ","
    string = re.sub('^.* - ', '', string)  # remove anything before " - "
    return string

with open('events.csv') as f:
    events = csv.DictReader(f)
    events = list(events)

errors = []
for i, event in enumerate(events):
    # Add location (osm geocoding)

    place = f"{clean(event['town'])}, {clean(event['country'])}"
    print(f'{i+1}/{len(events)} Geocoding: {place}... ', end='')
    r = geocoder.osm(place)
    if not r.json:
        print(f'ERROR: {r.status_code}: {r}... ', end='')
        location = {
            'lat': 0,
            'lng': 0,
            'latlng': '0,0'
        }
        errors.append((place, event['town'], event['country'], r))
    else:
        r = r.json
        location = {
            'lat': r['lat'],
            'lng': r['lng'],
            'latlng': '{lat},{lng}'.format(**r)
        }
    print(f'{location}\n')

    event.update(location)

print(f'{len(events)} events geocoded')
print(f'{len(errors)} geocoding errors:')
for error in errors:
    print(error)


# Write geocoded events to csv

filename = 'events-geocoded.csv'
print(f'\nWriting {len(events)} events detail to csv file: {filename}')
with open(filename, 'w') as f:
    writer = csv.DictWriter(f, fieldnames=list(events[0].keys()))
    writer.writeheader()
    for detail in events:
        writer.writerow(detail)