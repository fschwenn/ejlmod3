# -*- coding: utf-8 -*-
#harvest theses from Charles U. Prague
#FS: 2019-11-25
#FS: 2023-04-08

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True

publisher = 'Charles U., Prague (main)'
jnlfilename = 'THESES-CTU-%s' % (ejlmod3.stampoftoday())

years = [str(ejlmod3.year(backwards=1)), str(ejlmod3.year())]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for year in years:
    if year != years[0]:
        time.sleep(300)
    tocurl = 'https://dspace.cuni.cz/discover?filtertype_1=ds_uk_faculty&filter_relational_operator_1=equals&filter_1=Matematicko-fyzik%C3%A1ln%C3%AD+fakulta&filtertype_2=ds_thesesDefenceYear&filter_relational_operator_2=equals&filter_2=' + year + '&filtertype_3=ds_uk_language_iso&filter_relational_operator_3=equals&filter_3=en_US&submit_apply_filter=&rpp=500&locale-attribute=en'
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    recs += ejlmod3.getdspacerecs(tocpage, 'https://dspace.cuni.cz', alreadyharvested=alreadyharvested)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.issued', 'citation_pdf_url',
                                        'citation_language'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #title
            if meta['name'] == 'DC.title':
                if meta['xml:lang'] == "en_US":
                    rec['tit'] = meta['content']
            #keywords
            elif meta['name'] == 'DC.subject':
                if meta['xml:lang'] == "en_US":
                    for keyw in re.split(' *; *', meta['content']):
                        if re.search('\|.*\|', keyw):
                            rec['keyw'] += re.split('\|', keyw)
                        else:
                            rec['keyw'].append(keyw)
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if meta['xml:lang'] == "en_US":
                    rec['abs'] = meta['content']
    for span in artpage.body.find_all('span', attrs = {'class' : 'text-theses-failed'}):
        rec['tit'] += ' [FAILED]'
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
