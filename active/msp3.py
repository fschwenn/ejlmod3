# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest MS journals
# FS 2020-12-05
# FS 2022-11-17

import os
import ejlmod3
import re
import unicodedata
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

lastyear = ejlmod3.year(backwards=1)
llastyear = ejlmod3.year(backwards=2)


publisher = 'MSP'
volumestodo = 3
journals = {'gt' : ('Geom.Topol.', 'https://msp.org/gt/2020/24-4/'),
            'pjm' : ('Pacific J.Math.', 'https://msp.org/pjm/2020/308-1/index.xhtml'),
            'agt' : ('Algebr.Geom.Topol.', 'https://msp.org/agt/2020/20-5/'),
            'gtm' : ('Geom.Topol.Monographs', 'https://msp.org/gtm/1998/01/'),
            'apde' : ('Anal.Part.Diff.Eq.', 'https://msp.org/apde/2020/13-7/'),
            'paa' : ('Pure Appl.Anal.', 'https://msp.org/paa/2020/2-3/')}

ejldir = '/afs/desy.de/user/l/library/dok/ejl'
j = 0
for jnl in list(journals.keys()):
    j += 1
    (jnlname, url) = journals[jnl]
    #all issues page
    print('===[ %s | %s | %s ]===' % (jnl, jnlname, url))
    todo = []
    page = BeautifulSoup(urllib.request.urlopen(url))
    issuelinks = []
    for a in page.find_all('a', attrs = {'class' : 'about'}):
        if a.has_attr('href') and re.search('\d.*index\.xhtml', a['href']):
            link = 'https://msp.org' + a['href']
            issuelinks.append(link)
    #print ' issues:', issuelinks
    if jnl == 'gtm':
        tc = 'S'
        todo = issuelinks[-volumestodo:]
    else:
        tc = 'P'
        todo = issuelinks[:volumestodo]
    i = 0 
    for link in todo:
        recs = []
        i += 1
        print('==={ %s (%i/%i) }==={ %i/%i }==={ %s }==' % (jnl, j, len(list(journals.keys())), i, len(todo), link))
        if jnl == 'gtm':
            structure = re.search('.*\/([12]\d\d\d)\/(\d+).*', link)
            year = structure.group(1)
            vol = structure.group(2)
            iss = False
            jnlfilename = 'msp_%s%s' % (jnl, vol)
        else:
            structure = re.search('.*\/([12]\d\d\d)\/(\d+)\-(\d+).*', link)
            year = structure.group(1)
            vol = structure.group(2)
            iss = structure.group(3)
            jnlfilename = 'msp_%s%s.%s' % (jnl, vol, iss)
        #check whether file already exists
        goahead = True
        for ordner in ['/backup/', '/backup/%i/' % (lastyear), '/backup/%i/' % (llastyear)]:
            if os.path.isfile(ejldir + ordner + jnlfilename + '.doki') or os.path.isfile(ejldir + ordner + 'LABS_'+jnlfilename + '.doki') or os.path.isfile(ejldir + ordner + 'JSONL_'+jnlfilename + '.doki'):
                print('    Datei %s exisitiert bereit in %s' % (jnlfilename, ordner))
                goahead = False
        if not goahead:
            continue
        print(' file: ', jnlfilename)
        time.sleep(2)
        tocpage = BeautifulSoup(urllib.request.urlopen(link))
        for table in tocpage.body.find_all('table', attrs = {'id' : 'toc-area'}):
            for a in table.find_all('a', attrs = {'class' : 'title'}):
                rec = {'jnl' : jnlname, 'tc' : tc, 'vol' : vol, 'year' : year, 'autaff' : []}
                rec['artlink'] = re.sub('index.xhtml', a['href'], link)
                if iss:
                    rec['issue'] = iss
                recs.append(rec)
        k = 0
        for rec in recs:
            k += 1
            print('---{ %s (%i/%i) }---{ %i/%i }---{ %i/%i }---{ %s }---' % (jnl, j, len(list(journals.keys())), i, len(todo), k, len(recs), rec['artlink']))
            time.sleep(3)
            artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']))
            ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_author_institution',
                                                'citation_firstpage', 'citation_lastpage', 'citation_pdf_url',
                                                'citation_publication_date', 'citation_doi'])
            for table in artpage.find_all('table', attrs = {'class' : 'article'}):
                for h5 in table.find_all('h5'):
                    h5t = h5.text.strip() 
                    #abstract
                    if h5t == 'Abstract':
                        for p in table.find_all('p'):
                            rec['abs'] = p.text.strip()
                    #keywords
                    elif h5t == 'Keywords':
                        for div in table.find_all('div', attrs = {'class' : 'keywords'}):
                            rec['keyw'] = re.split(', ', div.text.strip())
                    #references
                    elif h5t == 'References':
                        for a in table.find_all('a'):
                            refurl = re.sub('index.xhtml', a['href'], link)
                            print('  references:', refurl)
                            time.sleep(1)
                            refpage = BeautifulSoup(urllib.request.urlopen(refurl))
                            for table2 in refpage.find_all('table', attrs = {'class' : 'article'}):
                                rec['refs'] = []
                                for tr in table2.find_all('tr'):
                                    rdoi = ''
                                    for a in tr.find_all('a'):
                                        if re.search('doi.org\/', a['href']):
                                            rdoi = re.sub('.*doi.org\/', ', DOI: ', a['href'])
                                    ref = tr.text.strip() + rdoi
                                    rec['refs'].append([('x', ref)])
                #arXiv
                for a in table.find_all('a'):
                    if a.has_attr('href') and re.search('arxiv.org', a['href']):
                        rec['arxiv'] = a.text.strip()
            print('  ', list(rec.keys()))
        #Hauptaufnahme
        if jnl == 'gtm':
            rec = {'jnl' : jnlname, 'tc' : 'B', 'vol' : vol, 'year' : year, 'autaff' : []}
            #DOI
            for td in tocpage.find_all('td', attrs = {'class' : 'article-area'}):
                for a in td.find_all('a'):
                    if re.search('doi.org\/', a['href']):
                        rec['doi'] = re.sub('.*doi.org\/', ', DOI: ', a['href'])
            #Editors
            for h3 in tocpage.find_all('h3'):
                h3t = h3.text.strip()
                if re.search('^Editor', h3t):
                    h3t = re.sub('^.*?: *', '', h3t)
                    h3t = re.sub(' and ', ', ', h3t)
                    for editor in re.split(' *, *', h3t):
                        rec['autaff'].append([editor+ ' (Ed.)'])
            #Title
            for div in tocpage.find_all('div', attrs = {'class' : 'title'}):
                rec['tit'] = div.text.strip()
            recs.append(rec)

        #write xml
        if recs:
            ejlmod3.writenewXML(recs, publisher, jnlfilename)

