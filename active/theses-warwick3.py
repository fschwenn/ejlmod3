# -*- coding: utf-8 -*-
# harvest theses from Warwick
# JH: 2020-28-06

from bs4 import BeautifulSoup
import re
import ejlmod3
import time
from urllib.request import Request, urlopen

startyear = ejlmod3.year(backwards=1)

publisher = 'Warwick U.'

jnlfilename = "THESES-WARWICK-%s" % (ejlmod3.stampoftoday())

hdr = {'User-Agent': 'Magic Browser'}
recs = []
for (dep, fc) in [('Department_of_Physics', ''), ('Department_of_Computer_Science', 'c'),
                  ('Mathematics_Institute', 'm'), ('Mathematics_Institute_', 'm'),
                  ('Mathematics_Institute_=3B_Centre_for_Scientific_Computing', 'mc'),
                  ('Mathematics_for_Real-World_Systems_Centre_for_Doctoral_Training', 'm'),
                  ('Department_of_Physics_=3B_Centre_for_Complexity_Science', ''),
                  ('Department_of_Mathematics', 'm')]:
    tocurl = 'http://wrap.warwick.ac.uk/view/theses/%s.html' % (dep)
    print(tocurl)
    req = Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urlopen(req), 'lxml')
    ps = tocpage.body.find_all('p')
    i = 0
    for p in ps:
        i += 1
        for span in p.find_all('span', attrs={'class': 'person_name'}):
            rec = {'tc': 'T', 'keyw': [], 'jnl': 'BOOK'}
            for a in p.find_all('a'):
                rec['link'] = a['href']
                rec['doi'] = '20.2000/WARWICK/' + re.sub('\W', '', re.sub('.*=', '', a['href']))
                rec['tit'] = a.text.strip()
                a.replace_with('')
                if fc: rec['fc'] = fc
                pt = re.sub('[\n\t\r]', ' ', p.text.strip())
                if re.search('\(\d\d\d\d\)', pt):
                    rec['date'] = re.sub('.*\((\d\d\d\d)\).*', r'\1', pt)
                    if rec['date'] >= str(startyear):
                        recs.append(rec)
    time.sleep(5)
    #ejlmod3.printprogress('=', [[i, len(ps)], [rec['date']], [len(recs)]])

i = 0
for rec in recs:
    i += 1
    time.sleep(3)
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    req = Request(rec['link'], headers=hdr)
    artpage = BeautifulSoup(urlopen(req), 'lxml')
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.keywords', 'eprints.document_url', 'DC.description', 'DC.rights'])
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        for th in tr.find_all('th'):
            tht = th.text.strip()
            for td in tr.find_all('td'):
                # keywords
                if tht == 'Library of Congress Subject Headings (LCSH):':
                    rec['keyw'] = re.split(', ', re.sub(' \-\-', ', ', td.text.strip()))
                # pages
                elif tht == 'Extent:':
                    if re.search('\d\d', td.text):
                        rec['pages'] = re.sub('.*(\d\d+).*', r'\1', td.text.strip())
                # supervisor
                elif tht == 'Supervisor(s)/Advisor:':
                    rec['supervisor'] = []
                    for sv in re.split('; ', td.text.strip()):
                        rec['supervisor'].append([re.sub(' \(.*', '', sv)])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename)
