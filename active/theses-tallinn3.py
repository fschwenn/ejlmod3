# -*- coding: utf-8 -*-
#harvest theses from Tallinn U. Tech.
#FS: 2024-02-06

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Tallinn U. Tech.'
jnlfilename = 'THESES-TALLINN-%s' % (ejlmod3.stampoftoday())

pages = 5
skipalreadyharvested = True
boring = ['Ragnar Nurkse Department of Innovation and Governance', 'School of Business and Governance',
          'Department of Material and Environmental Technology',
          'Department of Chemistry and Biotechnology', 'Department of Marine Systems',
          'Department of Civil Engineering and Architecture', 'Department of Computer Systems',
          'Department of Electrical Power Engineering and Mechatronics',
          'Department of Energy Technology', 'Department of Geology',
          'Department of Health Technologies', 'Department of Materials and Environmental Technology',
          'School of Economics and Business Administration', 'Faculty of Social Sciences',
          'Faculty of Chemical and Materials Technology', 'Centre for Biorobotics',
          'Department of Business Administration', 'Department of Cardiovascular Medicine',
          'Department of Chemical Engineering', 'Department of Chemistry', 'Environmental Engineering',
          'Department of Gene Technology', 'Department of International Relations']
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://digikogu.taltech.ee/en/Search/Items?pageIndex=' + str(page) + '&ItemTypes=8&Query[4]=&Query[5]=&Query[8]=&Query[7]=&YearFrom=&YearTo=&SortType=-47'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for li in tocpage.body.find_all('li', attrs = {'class' : 'list-group-item'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
        for a in li.find_all('a', attrs = {'title' : 'dissertations'}):
            rec['artlink'] = 'https://digikogu.taltech.ee' + a['href']
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                if not skipalreadyharvested or not rec['artlink'] in alreadyharvested:
                    for span in li.find_all('span', attrs = {'class' : 'year'}):
                        rec['date'] = span.text.strip()
                    for span in li.find_all('span', attrs = {'class' : 'author'}):
                        rec['autaff'] = [[ span.text.strip(), publisher ]]
                    prerecs.append(rec)
                else:
                    print('   ', rec['artlink'], 'already in backup')
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(15)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    #
    for div in artpage.body.find_all('div', attrs = {'class' : 'col-lg-8'}):
        for child in div.children:
            try:
                cn = child.name
            except:
                continue
            if cn == 'div':
                for d2 in child.find_all('div', attrs = {'class' : 'db-item-key'}):
                    dbitemkey = d2.text.strip()
                for d2 in child.find_all('div', attrs = {'class' : 'db-item-value'}):
                    if dbitemkey == 'keywords':
                        rec['keyw'].append(d2.text.strip())
                    elif dbitemkey == 'supervisor':
                        rec['supervisor'].append([d2.text.strip()])
                    elif dbitemkey == 'identifier':
                        dbitemvalue = d2.text.strip()
                        if re.search('ISBN *978*', dbitemvalue):
                            rec['isbn'] = re.sub('.*ISBN (978[0-9X\-]+).*', r'\1', dbitemvalue)
                        elif re.search('doi.org\/10', dbitemvalue):
                            rec['doi'] = re.sub('.*doi.org\/', '', dbitemvalue)
                    elif dbitemkey == 'language':
                        rec['language'] = d2.text.strip()
                    elif dbitemkey == 'rights':
                        dbitemvalue = d2.text.strip()
                        if re.search('CC', dbitemvalue):
                            rec['license'] = {'statement' : dbitemvalue}
                        else:
                            rec['note'].append('RIGHTS:::' + dbitemvalue)
                    elif dbitemkey == 'department / college':
                        dbitemvalue = d2.text.strip()
                        if dbitemvalue in boring:
                            keepit = False
                            print('   skip "%s"' % (dbitemvalue))
                        else:
                            rec['note'].append('DEP:::' + d2.text.strip())
                    elif dbitemkey == 'faculty':
                        dbitemvalue = d2.text.strip()
                        if dbitemvalue in boring:
                            keepit = False
                            print('   skip "%s"' % (dbitemvalue))
                        else:
                            rec['note'].append('FAC:::' + d2.text.strip())
                    elif dbitemkey == 'title':
                        if 'tit' in rec:
                            rec['transtit'] = d2.text.strip()
                        else:
                            rec['tit'] = d2.text.strip()

    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
