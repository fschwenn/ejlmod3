# -*- coding: UTF-8 -*-
#program to harvest journals from the EDP journals
# FS 2016-10-05
# FS 2023-02-16

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

maxtries = 7
basewait = 60

#ejldir = '/afs/desy.de/user/l/library/dok/ejl'

publisher = 'EDP Sciences'
tc = 'P'
jnl = sys.argv[1]
year = sys.argv[2]
issue = sys.argv[3]
if len(sys.argv) > 4:
    cnum = sys.argv[4]
    tc = 'C'
if len(sys.argv) > 5:
    fc = sys.argv[5]

if   (jnl == 'epjconf'):
    jnlname = 'EPJ Web Conf.'
    urltrunk = 'https://www.epj-conferences.org/articles/epjconf/abs/'
    tc = 'C'
elif (jnl == 'ljpc'):
    jnlname = 'J.Phys.Colloq.'
    urltrunk = 'https://jphyscol.journaldephysique.org/articles/jphyscol/abs/'
    tc = 'C'
elif (jnl == 'easps'):
    jnlname = 'EAS Publ.Ser.'
    urltrunk = 'https://www.eas-journal.org/articles/eas/abs/'
    tc = 'C'
elif (jnl == 'aanda'):
    jnlname = 'Astron.Astrophys.'
    urltrunk = 'https://www.aanda.org/articles/aa/abs/'
    tc = 'P'
elif (jnl == 'aandas'):
    jnlname = 'Astron.Astrophys.Suppl.Ser.'
    urltrunk = 'https://aas.aanda.org/articles/aas/abs/'
    tc = 'P'
elif (jnl == '4open'):
    jnlname = '4open'
    urltrunk = 'https://www.4open-sciences.org/articles/fopen/abs/'
    tc = 'P'
elif (jnl == 'itmweb'):
    jnlname = 'ITM Web Conf.'
    urltrunk = 'https://www.itm-conferences.org/articles/itmconf/abs/'
    tc = 'C'
    

if (jnl == '4open'):
    jnlfilename = "%s%s.%s_%s" % (jnl, year, issue, ejlmod3.stampoftoday())
    toclink = "%s%s/%02i/contents/contents.html" % (urltrunk, year, int(issue))
else:
    jnlfilename = "%s%s.%s" % (jnl, year, issue)
    toclink = "%s%s/%02i/contents/contents.html" % (urltrunk, year, int(issue))

print("get table of content (%s) ..." % (toclink))

host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)


try:
    if host == 'l00schwenn':
        driver.get(toclink)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    else:
        tocpage = BeautifulSoup(urllib.request.urlopen(toclink), features="lxml")
except:
    print("wait 2 minutes, retry %s" % (toclink))
    time.sleep(120)
    if host == 'l00schwenn':
        driver.get(toclink)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    else:
        tocpage = BeautifulSoup(urllib.request.urlopen(toclink), features="lxml")


recs = []
i = 0
articleas = tocpage.find_all('a', attrs = {'class' : 'article_title'})
for a in articleas:
    i += 1
    rec = {'jnl' : jnlname, 'tc' : tc, 'year' : year, 'note' : [], 'autaff' : []}
    if len(sys.argv) > 4:
        rec['tc'] = 'C'
        rec['cnum'] = cnum
    if len(sys.argv) > 5:
        rec['fc'] = fc
    #title
    rec['tit'] = a.text.strip()
    artlink = re.sub('(.*\.org)\/.*', r'\1', toclink) + a['href']
    ejlmod3.printprogress('-', [[i, len(articleas)], [artlink]])
    #check article page
    time.sleep(10)
    tries = 0
    while tries < maxtries:
        try:
            if host == 'l00schwenn':
                driver.get(artlink)
                artpage = BeautifulSoup(driver.page_source, features="lxml")
            else:
                artpage = BeautifulSoup(urllib.request.urlopen(artlink), features="lxml")
            tries = 2*maxtries
        except:
            tries += 1
            print("    wait %3i seconds, retry %s (%i)" % (tries*basewait, artlink, tries))
            time.sleep(tries*basewait)
    if tries == maxtries:
        sys.exit(0)
    #check metatags
    ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_doi', 'citation_volume',
                                        'citation_issue', 'citation_publication_date', 'citation_language', 'citation_keywords',
                                        'citation_keyword', 'citation_collaboration', 'citation_author', 'citation_pdf_url',
                                        'citation_author_institution', 'citation_author_orcid', 'citation_author_email'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] == 'prism.issueName':
                rec['note'].append(meta['content'])

            elif meta['name'] == 'prism.section':
                rec['note'].append(meta['content'])
    if 'issue' in rec:
        print('   %s %s (%s), no. %s, %s' % (jnlname, rec['vol'], rec['year'], rec['issue'], rec['p1']))
    elif 'vol' in rec:
        print('   %s %s (%s), %s' % (jnlname, rec['vol'], rec['year'], rec['p1']))
    else:
        print('   %s (%s), %s' % (jnlname, rec['year'], rec['p1']))
    #abstract
    for div in artpage.body.find_all('div', attrs = {'id' : 'article'}):
        for p in div.find_all('p', attrs = {'align' : 'LEFT'}):
            rec['abs'] = p.text.strip()
            rec['abs'] = re.sub('^abstract *:? *', '', rec['abs'])
        if 'abs' not in rec:
            for div2 in div.find_all('div', attrs = {'id' : 'head'}):
                rec['abs'] = re.sub('.*Abstract', '', re.sub('\n', '', div2.text)).strip()
    #strip issue from page number ?
    if jnl in ['ljpc']:
        if 'p1' in rec:
            rec['p1'] = re.sub('.*\-', '', rec['p1'])
        if 'p2' in rec:
            rec['p2'] = re.sub('.*\-', '', rec['p2'])
    #number of pages
    if 'p2' not in rec:
        for tr in artpage.body.find_all('tr'):
            nop = False
            for th in tr.find_all('th'):
                if re.search('Number of page', th.text):
                    nop = True
            if nop:
                for td in tr.find_all('td'):
                    pages = td.text.strip()
                    if re.search('^\d+$', pages):
                        rec['pages'] = pages
    #PDF
    if 'pdf_url' not in rec:
        for a2 in artpage.body.find_all('a'):
            if 'title' in a2 and re.search('^PDF', a2['title']):
                if 'href' in a2 and re.search('pdf$', a2['href']):
                    rec['pdf_url'] = a2['href']
    #edpj gives incomplete links to PDF
    if 'pdf_url' in rec and not re.search('www', rec['pdf_url']):
            pdflink = re.sub('.*articles', '/articles', rec['pdf_url'])
            rec['pdf_url'] = re.sub('(.*?www.*?)\/.*', r'\1', urltrunk) + pdflink
    #licence
    ejlmod3.globallicensesearch(rec, artpage)
    #references
    for a in artpage.body.find_all('a', attrs = {'title' : 'References'}):
        reflink = re.sub('(.*\.org)\/.*', r'\1', toclink) + a['href']
        time.sleep(10)
        try:
            if host == 'l00schwenn':
                driver.get(reflink)
                refpage = BeautifulSoup(driver.page_source, features="lxml")
            else:
                refpage = BeautifulSoup(urllib.request.urlopen(reflink), features="lxml")
        except:
            print('    %s not found' % (reflink))
            break
        list = refpage.body.find_all('ol', attrs = {'class' : 'references'})
        if not list:
            list = refpage.body.find_all('ul', attrs = {'class' : 'references'})
        for ol in list:
            rec['refs'] = []
            for li in ol.find_all('li'):
                reference = re.sub('[\t\n]+', ' ', li.text).strip()
                reference = re.sub(' +', ' ', reference)
                reference = re.sub('\[NASA ADS\]', '', reference)
                reference = re.sub('\[CrossRef\]', '', reference)
                reference = re.sub('\[Google.Scholar\]', '', reference)
                reference = re.sub('\[PubMed\]', '', reference)
                reference = re.sub('\[EDP Sciences\]', '', reference)
                for a2 in li.find_all('a'):
                    if re.search('\[CrossRef\]', a2.text):
                        rdoi = a2['href']
                        rdoi = re.sub('http.*.doi.org.', ', DOI: ', rdoi)
                        reference += rdoi
                rec['refs'].append([('x', reference)])
    if rec['autaff']:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        print('no authors ?!')

ejlmod3.writenewXML(recs, publisher, jnlfilename)
