# -*- coding: UTF-8 -*-
#program to harvest journals from SciPost
# FS 2016-09-27
# FS 2022-09-27

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

regexpsubm1 = re.compile('[sS]ubmissions')
regexpsubm2 = re.compile('.*\/(\d\d\d\d\.\d\d\d\d\d).*')

publisher = 'SciPost Fundation'
jnl = sys.argv[1]
if jnl in ['spsln']:
    jnlfilename = "%s.%s" % (jnl, ejlmod3.stampoftoday())
else:
    vol = sys.argv[2]
    issue = sys.argv[3]
    jnlfilename = "%s%s.%s" % (jnl, vol, issue)
tc = 'P'
if   (jnl == 'sps'): 
    jnlname = 'SciPost Phys.'
    urltrunk = 'https://scipost.org/SciPostPhys'    
    toclink = "%s.%s.%s" % (urltrunk, vol, issue)
elif (jnl == 'spsp'): 
    jnlname = 'SciPost Phys.Proc.'
    urltrunk = 'https://scipost.org/SciPostPhysProc'
    toclink = "%s.%s" % (urltrunk, vol)
    tc = 'C'
elif (jnl == 'spsc'):
    jnlname = 'SciPost Phys.Core'
    urltrunk = 'https://scipost.org/SciPostPhysCore' 
    toclink = "%s.%s.%s" % (urltrunk, vol, issue)
elif (jnl == 'spsln'):
    jnlname = 'SciPost Phys.Lect.Notes'
    urltrunk = 'https://scipost.org/SciPostPhysLectNotes'
    toclink = urltrunk
    tc = 'LP'
    if len(sys.argv) > 2:
        toclink = sys.argv[2]
        jnlfilename = "%s.%s" % (jnl, re.sub('\W', '', re.sub('.*collection\/', '', toclink)))
        if len(sys.argv) > 3:
            cnum = sys.argv[3]
        
#elif (jnl == 'spscb'):
#    jnlname = 'SciPost ???'
#    urltrunk = 'https://scipost.org/SciPostPhysCodeb' 
#    toclink = "%s.%s.%s" % (urltrunk, vol, issue)
#elif (jnl == 'spa'):
#    jnlname = 'SciPost Astro.'
#    urltrunk = 'https://scipost.org/SciPostAstro' 
#    toclink = "%s.%s.%s" % (urltrunk, vol, issue)
#elif (jnl == ''):
#    jnlname = 'SciPost ???'
#    urltrunk = 'https://scipost.org/SciPostAstroCore' 
#    toclink = "%s.%s.%s" % (urltrunk, vol, issue)
#elif (jnl == ''):
#    jnlname = 'SciPost ???'
#    urltrunk = 'https://scipost.org/SciPostMathCore' 
#    toclink = "%s.%s.%s" % (urltrunk, vol, issue)
#elif (jnl == ''):
#    jnlname = 'SciPost ???'
#    urltrunk = 'https://scipost.org/SciPostMath' 
#    toclink = "%s.%s.%s" % (urltrunk, vol, issue)

    


print("get table of content... from %s" % (toclink))
tocpage = BeautifulSoup(urllib.request.urlopen(toclink), features="lxml")
recs = []

if (jnl == 'spsln') and (len(sys.argv) > 2):
    for a in tocpage.body.find_all('a'):
        if a.has_attr('href') and re.search('SciPostPhysLectNotes.\d', a['href']):
            rec = {'tc' : 'CL', 'jnl' : jnlname, 'auts' : []}
            rec['artlink'] = 'https://scipost.org' + a['href']
            if len(sys.argv) > 3:
                rec['cnum'] = cnum
            recs.append(rec)
else:    
    #divs = tocpage.body.find_all('div', attrs = {'class' : 'card card-grey card-publication'})
    divs = tocpage.body.find_all('div', attrs = {'class' : ['card', 'card-gray', 'card-publication']})
    divs = tocpage.body.find_all('div', attrs = {'class' : 'card-publication'})


    #for div  in tocpage.body.find_all('div', attrs = {'class' : 'publicationHeader'}):
    for div  in divs:
        rec = {'jnl' : jnlname, 'tc' : tc, 'vol' : vol, 'auts' : []}
        if (jnl == 'sps'):
            rec['issue'] = issue
        elif (jnl == 'spsp'):
            rec['cnum'] = issue
        for h3 in div.find_all('h3'):
            for a in h3.find_all('a'):
                rec['artlink'] = 'https://scipost.org' + a['href']
                #title
                rec['tit'] = h3.text.strip()
        #abstract
        #for p in div.find_all('p', attrs = {'class' : 'publicationAbstract'}):
        #for p in div.find_all('p', attrs = {'class' : 'abstract mb-0 py-2'}):
        for p in div.find_all('p', attrs = {'class' : 'abstract'}):
            rec['abs'] = re.sub('  +', ' ', re.sub('[\n\t\r]', ' ', p.text.strip()))
        #year
        #for p in div.find_all('p', attrs = {'class' : 'publicationReference'}):
        for p in div.find_all('p', attrs = {'class' : 'card-text text-muted'}):
            rec['year'] = re.sub('.*\((20\d\d)\).*', r'\1', re.sub('[\n\t]', '', p.text.strip()))
        #article page
        recs.append(rec)
    
for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    time.sleep(3)
    artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']), features="lxml")
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_pdf_url', 'citation_publication_date', 'citation_title'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #article ID
            if meta['name'] == 'citation_firstpage':
                if jnl in ['spsln']:
                    rec['vol'] = re.sub('^0*', '', meta['content'])
                    rec['p1'] = '1'
                else:
                    rec['p1'] = meta['content']
    #abstract
    if not 'abs' in rec:
        for div in artpage.body.find_all('div', attrs = {'class' : 'col-12'}):
            for h3 in div.find_all('h3'):
                if h3.text.strip() == 'Abstract':
                    h3.decompose()
                    rec['abs'] = div.text.strip()
    #arXiv-number
    for a in artpage.body.find_all('a'):
        if a.has_attr('href'):
            if regexpsubm1.search(a.text) and regexpsubm2.search(a['href']):
                rec['arxiv'] = regexpsubm2.sub(r'\1', a['href'])
    #author
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'list-inline'}):
        if ul['class'] != ['list-inline', 'my-2']:
            continue
        rec['auts'] = []
        for li in ul.find_all('li', attrs = {'class' : ['list-inline-item', 'mr-1']}):            
            sups = []
            for sup in li.find_all('sup'):
                sups.append('=Aff' + sup.text.strip())                
                sup.replace_with('')
            lit = li.text.strip()
            lit = re.sub(', *$', '', lit)
            rec['auts'].append(lit)
            rec['auts'] += sups
    #affiliation
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'list'}):
        if ul['class'] != ['list', 'list-unstyled', 'my-2', 'mx-3']:
            continue
        rec['aff'] = []
        for li in ul.find_all('li'):
            for sup in li.find_all('sup'):
                supnr = sup.text.strip()
                sup.replace_with('')
            rec['aff'].append('Aff%s= %s' % (supnr, li.text.strip()))
    #collaboration
    for p in artpage.body.find_all('p', attrs = {'class' : 'mb-1'}):
        pt = p.text.strip()
        if re.search('[Cc]ollaboration', pt):
            rec['col'] = pt
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
  
