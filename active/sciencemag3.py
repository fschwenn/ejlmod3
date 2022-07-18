# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest Science
# FS 2020-11-24

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random


publisher = 'American Association for the Advancement of Science'
jnl = sys.argv[1]
year = sys.argv[2]

try:
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(version_main=102, options=options)
except:
    print('try Chrome=99 instead')
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(version_main=99, options=options)
    #driver = uc.Chrome(options=options)


if jnl == 'science':
    jnlname = 'Science'
elif jnl == 'sciadv':
    jnlname = 'Sci.Adv.'

def getissuenumbers(jnl, year):
    issues = []
    tocurl = 'https://%s.sciencemag.org/content/by/year/%s' % (jnl, year)
    tocurl = 'https://www.science.org/loi/%s/group/y%s' % (jnl, year)
    print(tocurl)
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for a in tocpage.find_all('a', attrs = {'class' : 'd-flex'}):
            vol = re.sub('.*[a-z]\/(\d+).*', r'\1', a['href'])
            issue = re.sub('.*\/(\d+).*', r'\1', a['href'])
            if re.search('^\d+$', vol) and  re.search('^\d+$', issue):
                issues.append((vol, issue))
    issues.sort()
    print('available', issues)
    return issues

def getdone():
    if jnl == 'science':
        reg = re.compile('science(\d+)\.(\d+)')
    elif jnl == 'sciadv':
        reg = re.compile('sciadv(\d+)\.(\d+)')
    ejldir = '/afs/desy.de/user/l/library/dok/ejl'
    issues = []
    for directory in [ejldir+'/onhold', ejldir+'/zu_punkten/enriched', ejldir+'/backup', ejldir+'/backup/' + str(ejlmod3.year(backwards=1))]:
        for datei in os.listdir(directory):
            if reg.search(datei):
                regs = reg.search(datei)
                vol = regs.group(1)
                issue = regs.group(2)
                if not (vol, issue) in issues:
                    issues.append((vol, issue))
    issues.sort()
    print('done', issues)
    return issues

def harvestissue(jnl, vol, issue):
    tocurl = 'https://www.science.org/toc/%s/%s/%s' % (jnl, vol, issue)
    print("   get table of content of %s %s.%s via %s ..." % (jnlname, vol, issue, tocurl))
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    recs = []
    for sct in tocpage.find_all('section', attrs = {'class' : 'toc__section'}):
        for h4 in sct.find_all('h4'):
            scttit = h4.text.strip()
        if scttit in ['Editorial', 'In Brief', 'In Depth', 'Feature', 'Working Life',
                      'Books et al.', 'Policy Forum', 'Perspectives', 'Association Affairs',
                      'Products & Materials', 'Careers',
                      'In Other Journals', 'In Science Journals', 'Neuroscience', 'News', 
                      'Social and Interdisciplinary Sciences', 'Biomedicine and Life Sciences']:
            print('      skip', scttit)
        else:
            for h3 in sct.find_all('h3'):
                for a in h3.find_all('a'):
                    rec = {'tc' : 'P', 'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                           'year' : year, 'autaff' : [], 'note' : [scttit], 'refs' : []}
                    rec['artlink'] = 'https://www.science.org%s' % (a['href'])
                    recs.append(rec)
    #check article pages
    i = 0
    for rec in recs:
        i += 1
        sleepingtime = random.randint(100, 300)
        ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']], [sleepingtime]])
        try:
            time.sleep(sleepingtime)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print("retry in 900 seconds")
            time.sleep(900)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        #DOI
        rec['doi'] = re.sub('.*?(10\.\d+\/)', r'\1', rec['artlink'])
        #meta-tags
        ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Date'])
        #pages
        for meta in artpage.find_all('meta', attrs = {'name' : 'dc.Identifier'}):
            if meta.has_attr('scheme'):
                if meta['scheme'] == 'publisher-id':
                    rec['p1'] = meta['content']
                elif meta['scheme'] == 'doi':
                    rec['doi'] = meta['content']
        #authors and affiliations
        for div in artpage.find_all('div', attrs = {'property' : 'author'}):
            for span in div.find_all('span', attrs = {'property' : 'familyName'}):
                name = span.text.strip()
            for span in div.find_all('span', attrs = {'property' : 'givenName'}):
                name += ', ' + span.text.strip()
            rec['autaff'].append([name])
            for a in div.find_all('a', attrs = {'class' : 'orcid-id'}):
                rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            for div2 in div.find_all('div', attrs = {'property' : 'organization'}):
                rec['autaff'][-1].append(div2.text.strip())
        #abstract
        for section in artpage.find_all('section', attrs = {'id' : 'abstract'}):
            for h2 in section.find_all('h2'):
                h2.decompose()
            rec['abs'] = section.text.strip()
        #strange page
        if not 'p1' in list(rec.keys()):
            rec['p1'] = re.sub('.*\.', '', rec['doi'])
        #references
        divs = artpage.find_all('div', attrs = {'class' : 'labeled'})
        if not len(divs):
             divs = artpage.find_all('div', attrs = {'role' : 'doc-biblioentry'})
        for div in divs:
            for d2 in div.find_all('div', attrs = {'class' : 'label'}):
                d2t = d2.text
                d2.replace_with('[%s] ' % d2t)
            for a in div.find_all('a'):
                at = a.text.strip()
                ah = a['href']
                if at == 'Crossref':
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', ah))
                else:
                    a.decompose()
            rec['refs'].append([('x', div.text.strip())])
        ejlmod3.printrecsummary(rec)
    return recs


done = getdone()
available = getissuenumbers(jnl, year)
todo = []
for tupel in available:
    if not tupel in done:
        todo.append(tupel)
i = 0
for (vol, issue) in todo:
    i += 1
    ejlmod3.printprogress('=', [[i, len(todo)], [jnlname, vol, issue]])
    recs = harvestissue(jnl, vol, issue)
    jnlfilename = '%s%s.%s' % (re.sub('\.', '', jnlname.lower()), vol, issue)
    ejlmod3.writenewXML(recs, publisher, jnlfilename)
