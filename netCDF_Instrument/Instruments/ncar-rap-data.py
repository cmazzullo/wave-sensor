from urllib.request import urlopen
import re
# 4-letter ICAO id
station_ids = 'KROA padk'

ids = station_ids.upper().split(' ')

hours = 10

if hours == 0:
    timestring = 'most+recent+only'
else:
    s = 'past+%d+hour'
    timestring = s if hours == 1 else s + 's'
    timestring = timestring % hours
idlist = '+'.join(ids)
url = ('http://weather.rap.ucar.edu/surface/index.php?metarIds=%s&'
       'hoursStr=%s&std_trans=standard&num_metars=number&'
       'submit_metars=Retrieve' % (idlist, timestring))

print(url)

pattern = '%s|%s' % tuple(ids)
print('pattern = %s' % pattern)

for line in urlopen(url):
    line = line.decode('utf-8')  # Decoding the binary data to text.
    if re.match(pattern, line):
        print(line.replace('<BR>', ''))
