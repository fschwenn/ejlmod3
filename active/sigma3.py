# -*- coding: utf-8 -*-
#program to harvest "Symmetry, Integrability and Geometry: Methods and Applications (SIGMA)"
# FS 2012-05-30
# FS 2023-02-06

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

publisher = 'SIGMA'
year = sys.argv[1]
firstarticle = int(sys.argv[2])
jnl = 'SIGMA'
jnlfilename = 'sigma'+year+'_'+str(firstarticle)

tocurl = 'https://www.emis.de/journals/SIGMA/%s/' % (year)
print(tocurl)

hdr = {'User-Agent' : 'MagicBrowser'}

#req = urllib.request.Request(tocurl, headers=hdr)
#tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
if not os.path.isfile('/tmp/s%s.html' % (jnlfilename)):
    os.system('wget -O /tmp/s%s.html %s' % (jnlfilename, tocurl))
inf = open('/tmp/s%s.html' % (jnlfilename), 'r')
lines = ''.join(inf.readlines())
lines = re.sub('> *<', '><', re.sub('[\n\r\t]', ' ', lines))
lines = re.sub('<\/DD><DL>', '</DD></DL><DL>', lines)
inf.close()
#print(lines)

tocpage = BeautifulSoup(lines)

prerecs = {}
for dl in tocpage.body.find_all('dl'):
    rec = {'jnl' : jnl, 'year' : year, 'tc' : 'P', 'auts' : [], 'aff' : [], 'note' : []}
    #title
    for dt in dl.find_all('dt'):
        for b in dt.find_all('b'):
            rec['tit'] = b.text.strip()
            #print('\n\n', rec['tit'])
    for dd in dl.find_all('dd'):
        ddt = re.sub('[\n\t\r]', ' ', dd.text.strip())
        #print('   ', ddt)
        parts = re.split('SIGMA', ddt)
        #p1
        p1 = int(re.sub('.*\), (\d+), .*', r'\1', parts[1]))
        #print(p1)
        rec['p1'] = '%03i' % (p1)
        #pages
        rec['pages'] = re.sub('.*?(\d+) page.*', r'\1', parts[1])
    if p1 >= firstarticle:
        time.sleep(1)
        artlink = 'https://www.emis.de/journals/SIGMA/%s/%03i/' % (year, p1)
        print(artlink)
        req = urllib.request.Request(artlink, headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_volume', 'citation_publication_date',
                                            'citation_doi', 'citation_pdf_url',
                                            'citation_keywords', 'citation_arxiv_id'])
        bqs = artpage.body.find_all('blockquote')
        #affiliations in superscripts
        for sup in bqs[0].find_all('sup'):    
            if re.search('\)', sup.text):
                aff = re.sub('(.*)\)', r' XXX Aff\1= ', sup.text)
                sup.replace_with(aff)
            else:
                aff = ', =Aff' + sup.text + ', '
                sup.replace_with(aff)
        #authors
        for b in bqs[0].find_all('b'):
            bt = re.sub('[\n\t\r]', ' ', b.text.strip())
            for aut in re.split(' *, *', re.sub(' and ', ', ', bt)):
                if len(aut) > 2:
                    rec['auts'].append(aut)
            b.decompose()
        #affiliations
        bqt = re.sub('[\n\t\r]', ' ', bqs[0].text.strip())
        for aff in re.split('XXX ', bqt):
            if len(aff) > 2:
                rec['aff'].append(aff)                        
        #abstract
        for p in artpage.body.find_all('p'):
            for b in p.find_all('b'):
                if b.text.strip() == 'Abstract':
                    b.decompose()
                    rec['abs'] = p.text.strip()
        #conference?
        for i in artpage.body.find_all('i'):
            if  re.search('Contribution to.*Proceedings', i.text):
                rec['note'].append(i.text.strip())
                rec['tc'] = 'C'
        #refernces
        for ol in artpage.body.find_all('ol'):
            rec['refs'] = []
            for li in ol.find_all('li'):
                rdoi = False
                for a in li.find_all('a'):
                    if a.has_attr('href'):
                        if re.search('doi.org\/10', a['href']):
                            rdoi = re.sub('.*org\/(10.*)', r', DOI: \1', a['href'])
                    else:
                        print('  non-linking anchor!?', a)    
                ref = li.text.strip()
                if rdoi:
                    ref = re.sub('\.$', '', ref)
                    ref += rdoi
                rec['refs'].append([('x', ref)])
        ejlmod3.printrecsummary(rec)
        prerecs[p1] = rec

keys = list(prerecs.keys())
keys.sort()
recs = [prerecs[key] for key in keys]

ejlmod3.writenewXML(recs, publisher, jnlfilename)
