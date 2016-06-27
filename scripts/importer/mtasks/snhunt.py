"""General data import tasks.
"""
import os
import re

from bs4 import BeautifulSoup
from scripts import PATH
from scripts.utils import pbar

from .. import Events
from ..funcs import load_cached_url


def do_snhunt(events, stubs, args, tasks, task_obj, log):
    current_task = task_obj.current_task(args)
    snh_url = 'http://nesssi.cacr.caltech.edu/catalina/current.html'
    html = load_cached_url(args, current_task, snh_url, os.path.join(
        PATH.REPO_EXTERNAL, 'SNhunt/current.html'))
    if not html:
        return events
    text = html.splitlines()
    findtable = False
    for ri, row in enumerate(text):
        if 'Supernova Discoveries' in row:
            findtable = True
        if findtable and '<table' in row:
            tstart = ri + 1
        if findtable and '</table>' in row:
            tend = ri - 1
    tablestr = '<html><body><table>'
    for row in text[tstart:tend]:
        if row[:3] == 'tr>':
            tablestr = tablestr + '<tr>' + row[3:]
        else:
            tablestr = tablestr + row
    tablestr = tablestr + '</table></body></html>'
    bs = BeautifulSoup(tablestr, 'html5lib')
    trs = bs.find('table').findAll('tr')
    for tr in pbar(trs, current_task):
        cols = [str(xx.text) for xx in tr.findAll('td')]
        if not cols:
            continue
        name = re.sub('<[^<]+?>', '', cols[4]
                      ).strip().replace(' ', '').replace('SNHunt', 'SNhunt')
        events, name = Events.add_event(tasks, args, events, name, log)
        source = events[name].add_source(srcname='Supernova Hunt', url=snh_url)
        events[name].add_quantity('alias', name, source)
        host = re.sub('<[^<]+?>', '', cols[1]).strip().replace('_', ' ')
        events[name].add_quantity('host', host, source)
        events[name].add_quantity('ra', cols[2], source, unit='floatdegrees')
        events[name].add_quantity('dec', cols[3], source, unit='floatdegrees')
        dd = cols[0]
        discoverdate = dd[:4] + '/' + dd[4:6] + '/' + dd[6:8]
        events[name].add_quantity('discoverdate', discoverdate, source)
        discoverers = cols[5].split('/')
        for discoverer in discoverers:
            events[name].add_quantity('discoverer', 'CRTS', source)
            events[name].add_quantity('discoverer', discoverer, source)
        if args.update:
            events, stubs = Events.journal_events(
                tasks, args, events, stubs, log)

    events, stubs = Events.journal_events(tasks, args, events, stubs, log)
    return events