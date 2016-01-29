import requests
import re


conference = 'focs'
year = '2000'

url = 'http://dblp.uni-trier.de/rec/bibtex/conf/' + conference + '/' + year

print(url)
result = requests.get(url)
result = result.text

start_entry = result.find("@proceedings")
info = result[start_entry:]

end_entry = info.find('</pre>')
entry = info[:end_entry]

parts = entry.split(',')
for part in parts:
    if 'editor' in part:
        new = part.split('=')
        length = len(new[1])
        s = new[1][2:length-2]
        editor = re.sub("\s+", " ", s)
print(editor)