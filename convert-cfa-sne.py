#!/usr/local/bin/python2.7

import csv
import glob
import os
import re
import urllib2
from BeautifulSoup import BeautifulSoup

eventnames = []

# First import the CfA data.
for file in sorted(glob.glob("cfa-input/*.dat"), key=lambda s: s.lower()):
	tsvin = open(file,'rb')
	tsvin = csv.reader(tsvin, delimiter=' ', skipinitialspace=True)
	csv_data = []
	for r, row in enumerate(tsvin):
		new = []
		for item in row:
			new.extend(item.split("\t"))
		csv_data.append(new)

	for r, row in enumerate(csv_data):
		for c, col in enumerate(row):
			csv_data[r][c] = col.strip()
		csv_data[r] = filter(None, csv_data[r])

	eventname = os.path.basename(os.path.splitext(file)[0])

	eventparts = eventname.split('_')
	eventname = (eventparts[0]).upper()
	eventbands = list(eventparts[1])

	if (eventname in eventnames):
		outfile = open(eventname + '.dat', 'a')
		csvout = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL, delimiter="\t")
	else:
		eventnames.append(eventname)
		outfile = open(eventname + '.dat', 'wb')
		csvout = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL, delimiter="\t")

		csvout.writerow(['name', eventname])

	tu = 'MJD'
	jdoffset = 0.
	for rc, row in enumerate(csv_data):
		if len(row) > 0 and row[0][0] == "#":
			if len(row[0]) > 2 and row[0][:3] == "#JD":
				tu = 'JD'
				rowparts = row[0].split('-')
				jdoffset = float(rowparts[1])
			elif len(row) > 1 and row[1] == "HJD":
				tu = "HJD"
			continue
		elif len(row) > 0:
			mjd = row[0]
			for v, val in enumerate(row):
				if v == 0:
					if tu == 'JD':
						mjd = float(val) + jdoffset - 2400000.5
						tuout = 'MJD'
					elif tu == 'HJD':
						mjd = float(val) - 2400000.5
						tuout = 'MJD'
					else:
						mjd = val
						tuout = tu
				elif v % 2 != 0:
					if float(row[v]) < 90.0:
						csvout.writerow(['photometry', tuout, mjd, eventbands[(v-1)/2], '', row[v], row[v+1], 0])

	outfile.close()

# Now import the UCB SNDB
for file in sorted(glob.glob("SNDB/*.dat"), key=lambda s: s.lower()):
	tsvin = open(file,'rb')
	tsvin = csv.reader(tsvin, delimiter=' ', skipinitialspace=True)

	eventname = os.path.basename(os.path.splitext(file)[0])

	eventparts = eventname.split('.')
	eventname = eventparts[0].replace(' ', '').upper()

	if (eventname in eventnames):
		outfile = open(eventname + '.dat', 'a')
		csvout = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL, delimiter="\t")
	else:
		eventnames.append(eventname)
		outfile = open(eventname + '.dat', 'wb')
		csvout = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL, delimiter="\t")

		csvout.writerow(['name', eventname])

	for r, row in enumerate(tsvin):
		if len(row) > 0 and row[0] == "#":
			continue
		mjd = row[0]
		abmag = row[1]
		aberr = row[2]
		band = row[4]
		instrument = row[5]
		csvout.writerow(['photometry', 'MJD', mjd, band, instrument, abmag, aberr, 0])

# Now import the Asiago catalog
response = urllib2.urlopen('http://graspa.oapd.inaf.it/cgi-bin/sncat.php')
html = response.read()
html = html.replace('\r', '')

soup = BeautifulSoup(html)
table = soup.find("table")

records = []
for r, row in enumerate(table.findAll('tr')):
	if r == 0:
		continue

	col = row.findAll('td')
	records.append([x.renderContents() for x in col])

for record in records:
	if len(record) > 1 and record[1] != '':
		eventname = "SN" + record[1].replace(' ', '').upper()
		hostname = record[2]
		claimedtype = record[17]

		if (eventname in eventnames):
			outfile = open(eventname + '.dat', 'a')
			csvout = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL, delimiter="\t")
		else:
			eventnames.append(eventname)
			outfile = open(eventname + '.dat', 'wb')
			csvout = csv.writer(outfile, quotechar='"', quoting=csv.QUOTE_ALL, delimiter="\t")

			csvout.writerow(['name', eventname])

		if (hostname != ''):
			csvout.writerow(['host', hostname])
		if (claimedtype != ''):
			csvout.writerow(['claimedtype', claimedtype])
