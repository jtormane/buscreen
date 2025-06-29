from flask import Flask, jsonify, render_template
app = Flask(__name__)

from lxml import etree
from io import StringIO
import requests
import time
from datetime import datetime
import json

class Arrival:
    def __init__(self, line, destination, time):
     self.line = line
     self.destination = destination
     self.time = time

def get_arrivals(id):
  arrivals = []
  parser = etree.HTMLParser()

  url = f"https://reittiopas.osl.fi/pysakit/OULU%3A{id}?locale=en"
  start = time.time()
  response = requests.get(url)
  end = time.time()
  print(f"Kesti {end - start:.2f} sekuntia")

  status_code = response.status_code
  if status_code != 200:
    print(f"Error: Received status code {status_code} for URL {url}")
    return (None, None)

  html = response.content.decode('utf-8')
  tree = etree.parse(StringIO(html), parser)

  daterow = tree.xpath('//div[contains(@class, "date-row border-bottom")]')
  date = daterow[0].text if daterow else None

  rows = tree.xpath('//tr[contains(@class, "departure-row bus")]')
  for row in rows:
    cells = row.xpath('.//td/div/text()')
    times = row.xpath('.//td[@class="time-cell"]/span/text()')
    if len(cells) < 2 or not times:
        continue

    new_arrival = Arrival(cells[0] if cells else None, cells[1] if cells else None, times[0] if times else None)
    arrivals.append(new_arrival)

  arrivals = arrivals[:10]

  return (date, arrivals)



(date, arrivals) = get_arrivals("120545")
now = datetime.now()
print(f"{now.strftime('%H:%M:%S')}")
for arrival in arrivals:
    print(f"{arrival.line} -> {arrival.destination}  {arrival.time}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/arrivals/<stop_id>')
def arrivals_api(stop_id):
    date, arrivals = get_arrivals(stop_id)
    return jsonify({
        "date": date,
        "arrivals": [
            {
                "line": a.line,
                "destination": a.destination,
                "time": a.time
                } for a in arrivals
            ]
        })

if __name__ == '__main__':
    app.run(debug = True)

