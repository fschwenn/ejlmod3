# -*- coding: UTF-8 -*-
#program to harvest journals from Siberian Federal U.
# FS 2017-07-17
# FS 2023-02-27

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time


def tfstrip(x): return x.strip()

publisher = 'Siberian Federal U., Krasnoyarsk'
hdr = {'User-Agent' : 'Mozilla/5.0'}

jnl = sys.argv[1]
vol = sys.argv[2]
issues = sys.argv[3]
if jnl == 'mp':
    jnlname = 'J.Sib.Fed.U.'
    starturl = 'http://journal.sfu-kras.ru/en/series/mathematics_physics'
    
jnlfilename = 'sibfed_%s.%s.%s' % (jnl, vol, re.sub(',', '_', issues))
def tfstrip(x): return x.strip()


if len(sys.argv) > 4:
    year = str(2007+int(vol))
    tus = re.split(',', sys.argv[4])
    iss = re.split(',', sys.argv[3])
    tocurls = []
    for i in range(len(iss)):
        tocurls.append([iss[i], tus[i]])
else:
    print(starturl)
    req = urllib.request.Request(starturl, headers=hdr)
    startpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')

    #searchterms to find toclink on startpage
    searchterms = []
    for issue in re.split(',', issues):
        searchterms.append((issue, re.compile('Vol. %s, Issue %s' % (vol, issue))))

    tocurls = []
    for div in startpage.body.find_all('div', attrs = {'class' : 'collapsed-content'}):
        for li in div.find_all('li'):
            lit = li.text.strip()
            for searchterm in searchterms:
                if searchterm[1].search(lit):
                    for a in li.find_all('a'):
                        print(' -', lit)
                        year = re.sub('.*(20\d\d).*', r'\1', lit)
                        tocurls.append((searchterm[0], 'http://journal.sfu-kras.ru' + a['href']))

i = 0
prerecs = []
for (issue, tocurl) in tocurls:
    i += 1
    ejlmod3.printprogress("=", [[i, len(tocurls)], [tocurl]])
    time.sleep(2)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for ol in tocpage.body.find_all('ol', attrs = {'class' : 'articles'}):
        for li in ol.find_all('li'):
            rec = {'jnl' : jnlname, 'tc' : 'P', 'vol' : vol, 'issue' : issue, 'autaff' : [], 'year' : year}
            for strong in li.find_all('strong'):
                rec['tit'] = strong.text.strip()
            for a in li.find_all('a'):
                if a.text.strip() == 'abstract':
                     rec['artlink'] = 'http://journal.sfu-kras.ru' + a['href']
                     prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    
i=0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']]])
    artfilename = '/tmp/sibfed.%s' % (re.sub('\D', '', rec['artlink']))
    if not os.path.isfile(artfilename):
        time.sleep(2)
        os.system('wget  -T 300 -t 3 -q  -O %s %s' % (artfilename, rec['artlink']))
    artfil = open(artfilename, mode='r')
    artlines = ''.join(map(tfstrip, artfil.readlines()))
    artfil.close()
    artlines = re.sub('.*<html', '<html', artlines)
    artpage = BeautifulSoup(artlines, features='lxml')
    try:
        artpage.body.find_all('a')
    except:
        print('!!! %s !!!' % (rec['artlink']))
        del rec        
        continue
    #req = urllib2.Request(rec['artlink'], headers=hdr)
    #artpage = BeautifulSoup(urllib2.urlopen(req))
    #FFT
    for a in artpage.body.find_all('a', attrs = {'class' : 'xfulltext'}):
        rec['hidden'] = a['href']
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            try:
                child.name
            except:
                continue
            if child.name == 'dt':
                dtt = child.text.strip()
            elif child.name == 'dd':
                #authors
                if dtt == 'Contact information':
                    for script in child.find_all('script'):
                        script.replace_with('')
                    for autaff in re.split(' *; *', child.text.strip()):
                        if re.search('(ORCID|OCRID):', autaff):
                            author = rec['autaff'][-1]
                            rec['autaff'][-1] = [author[0], 'ORCID:'+re.sub('.*:\s', '', autaff)]
                            rec['autaff'][-1] += author[1:]                            
                        elif re.search(':', autaff):
                            parts = re.split(' *: *', autaff)
                            rec['autaff'].append([parts[0], parts[1]])
                        elif re.search('@', autaff):
                            author = rec['autaff'][-1]
                            rec['autaff'][-1] = [author[0], 'EMAIL:'+autaff]
                            rec['autaff'][-1] += author[1:]
                        else:
                            rec['autaff'].append([autaff])
                            
                #keywords
                elif dtt == 'Keywords':
                    rec['keyw'] = re.split('; ', child.text.strip())
                #abstract
                elif dtt == 'Abstract':
                    rec['abs'] = child.text.strip()
                #pages
                elif dtt == 'Pages':
                    rec['p1'] = re.sub('\D.*', '', child.text.strip())
                    rec['p2'] = re.sub('.*\D', '', child.text.strip())
                #DOI
                elif dtt == 'DOI':
                    rec['doi'] = child.text.strip()
                #link
                elif dtt == 'Paper at repository of SibFU' and not 'doi' in list(rec.keys()):
                    rec['link'] = child.text.strip()
                    rec['doi'] = '20.2000/SibFed' + re.sub('.*handle', '', rec['link'])
                
    ejlmod3.printrecsummary(rec)
    recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
