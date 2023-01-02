# -*- coding: utf-8 -*-
#harvest theses from ETH
#FS: 2019-09-13
#FS: 2022-10-04


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Zurich, ETH'
jnlfilename = 'THESES-ETH-%s' % (ejlmod3.stampoftoday())
rpp = 100
skipalreadyharvested = True
dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'


alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))        

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for (dep, fc) in [('02000', 'm'), ('02010', ''), ('02150', 'c')]:
    tocurl = 'https://www.research-collection.ethz.ch/handle/20.500.11850/16/discover?filtertype_1=datePublished&filter_relational_operator_1=equals&filter_1=[' + str(ejlmod3.year(backwards=1)) + '+TO+' + str(ejlmod3.year(backwards=-1)) + ']&filtertype_2=split_leitzahl&filter_relational_operator_2=contains&filter_2=' + dep + '&submit_apply_filter=&rpp=' + str(rpp)
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://www.research-collection.ethz.ch'):
        if fc:
            rec['fc'] = fc
        if not rec['hdl'] in alreadyharvested:
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))


recs = []
i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue      
    ejlmod3.metatagcheck(rec, artpage, ['DC.identifier', 'citation_title', 'DCTERMS.issued', 'DC.subject',
                                        'DC.language', 'citation_pdf_url', 'DCTERMS.abstract', 'DC.rights'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author ]]
        rec['autaff'][-1].append('Zurich, ETH')
    #fulltext
    if 'licence' in list(rec.keys()):
        for div in artpage.body.find_all('div', attrs = {'class' : 'file-link'}):
            for a in div.find_all('a'):
                if re.search('Fulltext', a.text):
                    #ETH is just too restrictive against robots (even 5 minutes delays do not work)
                    rec['FFT'] = 'https://www.research-collection.ethz.ch' + a['href']
                    #rec['link'] = 'https://www.research-collection.ethz.ch' + a['href']
    recs.append(rec)
    ejlmod3.printrecsummary(rec)
     
ejlmod3.writenewXML(recs, publisher, jnlfilename)
