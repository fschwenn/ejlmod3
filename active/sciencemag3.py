# -*- coding: UTF-8 -*-
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
import cloudscraper

publisher = 'American Association for the Advancement of Science'
jnl = sys.argv[1]
year = sys.argv[2]
skipalreadyharvested = True
rpp = 100
pages = 3
bunchsize = 10

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium-browser'
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
    
#scraper = cloudscraper.create_scraper()



if jnl == 'science':
    jnlname = 'Science'
elif jnl == 'sciadv':
    jnlname = 'Sci.Adv.'
elif jnl == 'research':
    jnlname = 'Research'

def getissuenumbers(jnl, year):
    issues = []
    tocurl = 'https://%s.sciencemag.org/content/by/year/%s' % (jnl, year)
    tocurl = 'https://www.science.org/loi/%s/group/y%s' % (jnl, year)
    print(tocurl)
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    #tocpage = BeautifulSoup(scraper.get(tocurl).text, features="lxml")
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
    for directory in [ejldir+'/backup', ejldir+'/backup/' + str(ejlmod3.year(backwards=1))]:
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

def harvestarticle(jnl, rec, i, l, r):
    sleepingtime = random.randint(30, 150)
    ejlmod3.printprogress('-', [[i, l], [rec['artlink']], ['%isec' % (sleepingtime)], [r]])
    try:
        time.sleep(sleepingtime)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    except:
        print("retry in 900 seconds")
        time.sleep(900)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    #DOI
    rec['doi'] = re.sub('.*?(10\.\d+\/)', r'\1', rec['artlink'])
    #meta-tags
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Date'])
    if 'tit' in rec:
        if rec['tit'] in ['In Science Journals']:
            return False
    else:
        print(artpage.text)
    #volume
    if jnl in ['research']:
        for span in artpage.find_all('span', attrs = {'property' : 'volumeNumber'}):
            rec['vol'] = span.text.strip()
    #pages
    for meta in artpage.find_all('meta', attrs = {'name' : 'dc.Identifier'}):
        if meta.has_attr('scheme'):
            if meta['scheme'] == 'publisher-id':
                rec['p1'] = meta['content']
            elif meta['scheme'] == 'doi':
                rec['doi'] = meta['content']
    #authors and affiliations
    for div in artpage.find_all('div', attrs = {'property' : 'author'}):
        name = False
        for span in div.find_all('span', attrs = {'property' : 'familyName'}):
            name = span.text.strip()
        for span in div.find_all('span', attrs = {'property' : 'givenName'}):
            name += ', ' + span.text.strip()
        if name:
            rec['autaff'].append([name])
            for a in div.find_all('a', attrs = {'class' : 'orcid-id'}):
                rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            for div2 in div.find_all('div', attrs = {'property' : ['affiliation', 'organization']}):
                rec['autaff'][-1].append(div2.text.strip())
        else:
            rec['autaff'].append([re.sub('View all articles by this author', '', div.text.strip())])
            print('\n  added "%s" as author - is it ok or a collaboration or ...?\n' % (rec['autaff'][-1][0]))
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
    if not len(divs):
        for section in artpage.find_all('section', attrs = {'id'  : 'bibliography'}):
            divs = section.find_all('div', attrs = {'role' : 'listitem'})
    for div in divs:
        for d2 in div.find_all('div', attrs = {'class' : 'label'}):
            d2t = d2.text
            d2.replace_with('[%s] ' % d2t)
        for a in div.find_all('a'):
            if a.has_attr('href'):
                at = a.text.strip()
                ah = a['href']
                if at == 'Crossref':
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', ah))
                else:
                    a.decompose()
        rec['refs'].append([('x', div.text.strip())])
    #PDF    
    for a in artpage.find_all('a', attrs = {'data-toggle' : 'tooltip'}):
        if a.has_attr('href') and re.search('doi\/pdf', a['href']):
            if jnl == 'research':
                rec['pdf_url'] = 'https://spj.science.org' + a['href']
            else:
                rec['pdf_url'] = 'https://science.org' + a['href']
    ejlmod3.globallicensesearch(rec, artpage)
    return True

def harvestissue(jnl, vol, issue):
    tocurl = 'https://www.science.org/toc/%s/%s/%s' % (jnl, vol, issue)
    print("   get table of content of %s %s.%s via %s ..." % (jnlname, vol, issue, tocurl))
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    #tocpage = BeautifulSoup(scraper.get(tocurl).text, features="lxml")
    prerecs = []
    for sct in tocpage.find_all('section', attrs = {'class' : 'toc__section'}):
        for h4 in sct.find_all('h4'):
            scttit = h4.text.strip()
        if scttit in ['Editorial', 'In Brief', 'In Depth', 'Feature', 'Working Life',
                      'Books et al.', 'Policy Forum', 'Perspectives', 'Association Affairs',
                      'Products & Materials', 'Careers', 'Insights',
                      'In Other Journals', 'In Science Journals', 'Neuroscience', 'News', 
                      'Social and Interdisciplinary Sciences', 'Biomedicine and Life Sciences']:
            print('      skip', scttit)
        else:
            print('          ', scttit)
            for h3 in sct.find_all('h3'):
                for a in h3.find_all('a'):
                    rec = {'tc' : 'P', 'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                           'year' : year, 'autaff' : [], 'note' : [scttit], 'refs' : []}
                    rec['artlink'] = 'https://www.science.org%s' % (a['href'])
                    prerecs.append(rec)
        sct.decompose()
    #articles no in regular sections
    for h3 in tocpage.find_all('h3', attrs = {'class' : 'article-title'}):
        for a in h3.find_all('a'):
            rec = {'tc' : 'P', 'jnl' : jnlname, 'vol' : vol, 'issue' : issue,
                   'year' : year, 'autaff' : [], 'note' : [scttit], 'refs' : []}
            rec['artlink'] = 'https://www.science.org%s' % (a['href'])
            prerecs.append(rec)
    #check article pages
    i = 0
    recs = []
    for rec in prerecs:
        i += 1
        if harvestarticle(jnl, rec, i, len(prerecs), len(recs)):
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    return recs


if jnl in ['science', 'sciadv']:
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
else:
    jnlfilename = jnl + ejlmod3.stampoftoday()
    if skipalreadyharvested:
        alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    prerecs = []
    for page in range(pages):
        tocurl = 'https://spj.science.org/index/' + jnl + '?pageSize=' + str(rpp) + '&startPage=' + str(page)
        #tocpage = BeautifulSoup(scraper.get(tocurl).text, features="lxml")
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
        for div in tocpage.find_all('div', attrs = {'class' : 'card-content'}):
            for h3 in div.find_all('h3', attrs = {'class' : 'article-title'}):
                for a in h3.find_all('a'):
                    rec = {'tc' : 'P', 'jnl' : jnlname, 'autaff' : [], 'refs' : []}
                    rec['artlink'] = 'https://spj.science.org%s' % (a['href'])
                    rec['doi'] = a['href'][5:]
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(random.randint(20, 50))
    i = 0
    recs = []
    for rec in prerecs:
        i += 1
        if harvestarticle(jnl, rec, i, len(prerecs), len(recs)):
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
            ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))

