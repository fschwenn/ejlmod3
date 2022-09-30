# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest ASP books
# FS 2019-06-21
# FS 2022-09-29

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

publisher = 'Astronomical Society of the Pacific'
bookid = sys.argv[1]

jnlfilename = 'aspcs%s' % (bookid)
if len(sys.argv) > 2:
    jnlfilename += '.' + sys.argv[2] 
jnlname = 'ASP Conf.Ser.'
typecode = 'C'

urltrunk = "http://aspbooks.org/a/volumes"
tocurl = "%s/table_of_contents/?book_id=%s" % (urltrunk,bookid)
tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl))
print("read table of contents...")

#global metadata
for table in tocpage.find_all('table', attrs = {'id' : 'volumeDetails'}):
    for tr in table.find_all('tr'):
        for span in tr.find_all('span'):
            if re.search('Year:', span.text, re.IGNORECASE):
                for td in tr.find_all('td'):
                    #volume
                    if re.search('View this Volume on ADS', td.text, re.IGNORECASE):
                        for a in td.find_all('a'):
                            vol = re.sub('.*olume=(\d+).*', r'\1', a['href'])
                    #year
                    elif re.search('[12]\d\d\d', td.text):
                        year = re.sub(' *([12]\d\d\d) *', r'\1', re.sub('[\n\t\r]', '', td.text.strip()))
            elif re.search('Title:', span.text, re.IGNORECASE):
                for td in tr.find_all('td', attrs = {'colspan' : '4'}):
                    #note
                    note1 = td.text.strip()

#find article linkes
recs = []
note2 = False
for table in tocpage.find_all('table', attrs = {'cellspacing' : '3'}):
    for tr in table.find_all('tr'):
        for b in tr.find_all('b'):
            note2 = b.text.strip()
        for a in tr.find_all('a'):
            rec = {'jnl' : jnlname, 'note' : [note1], 'tc' : typecode, 'vol' : vol, 'year' : year}
            if note2:
                rec['note'].append(note2)
            if len(sys.argv) > 2:
                rec['cnum'] = sys.argv[2] 
            rec['link'] = urltrunk + re.sub('.*a.volumes', '', a['href'])
            if not a.text.strip() in ['Volume Cover', 'Front Matter', 'Back Matter']:
                recs.append(rec)

#check individual articles
i = 0
for rec in recs:
    i += 1
    print('---{ %i/%i }---{ %s }---' % (i, len(recs), rec['link']))
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
    for table in artpage.find_all('table', attrs = {'cellspacing' : '3'}):
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2:
                if tds[0].text.strip() == 'Paper:':
                    rec['tit'] = tds[1].text.strip()
                elif tds[0].text.strip() == 'Page:':
                    rec['p1'] = tds[1].text.strip()
                elif tds[0].text.strip() == 'Authors:':
                    rec['auts'] = re.split(' *; *', tds[1].text.strip())
                elif tds[0].text.strip() == 'Abstract:':
                    rec['abs'] = tds[1].text.strip()
    #fulltext
    for form in artpage.find_all('form'):
        if form.has_attr('action') and re.search('pdf.*download', form['action']):
            rec['FFT'] = 'http://www.aspbooks.org' + form['action']
    ejlmod3.printrecsummary(rec)

                    
jnlfilename = 'aspcs%s.%s' % (vol, bookid)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
