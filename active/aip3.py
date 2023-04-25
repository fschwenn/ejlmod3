# -*- coding: utf-8 -*-
#program to harvest AIP-journals
# FS 2015-02-11

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import random
import datetime
regexpref = re.compile('[\n\r\t]')

publisher = 'AIP'
typecode = 'P'
skipalreadyharvested = True
jnl = sys.argv[1]
vol = sys.argv[2]
jnlfilename = jnl+vol+'_'+ejlmod3.stampoftoday()
cnum = False
if len(sys.argv) > 3: 
    iss = sys.argv[3]
    jnlfilename = jnl + vol + '.' + iss + '_'+ejlmod3.stampoftoday()
if len(sys.argv) > 4:
    cnum = sys.argv[4]
    jnlfilename = jnl + vol + '.' + iss + '_' + cnum + '_'+ejlmod3.stampoftoday()
if   (jnl == 'rsi'): 
    jnlname = 'Rev.Sci.Instrum.'
elif (jnl == 'jmp'):
    jnlname = 'J.Math.Phys.'
elif (jnl == 'chaos'):
    jnlname = 'Chaos'
elif (jnl == 'ajp'):
    jnlname = 'Am.J.Phys.'
elif (jnl == 'ltp'):
    jnlname = 'Low Temp.Phys.'
    jnlname2 = 'Fiz.Nizk.Temp.'
elif (jnl == 'php'):
    jnlname = 'Phys.Plasmas'
elif (jnl == 'adva'):
    jnlname = 'AIP Adv.'
elif (jnl == 'aipconf') or (jnl == 'aipcp') or (jnl == 'apc'):
    jnlname = 'AIP Conf.Proc.'
    jnl = 'apc'
    typecode = 'C'
elif (jnl == 'apl'):
    jnlname = 'Appl.Phys.Lett.'
elif (jnl == 'jap'):
    jnlname = 'J.Appl.Phys.'
elif (jnl == 'jcp'):
    jnlname = 'J.Chem.Phys.'
elif (jnl == 'phf'):
    jnlname = 'Phys.Fluids'
elif (jnl == 'jva'):
    jnlname = 'J.Vac.Sci.Tech.A'
elif (jnl == 'jvb'):
    jnlname = 'J.Vac.Sci.Tech.B'
elif (jnl == 'aqs'):
    jnlname = 'AVS Quantum Sci.'
elif (jnl == 'app'):
    jnlname = 'APL Photonics?'
elif (jnl == 'sci'):
    jnlname = 'Scilight?'
elif (jnl == 'pto'): #authors messy
    jnlname = 'Phys.Today'
    typecode = ''


host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
#    options.binary_location='/usr/bin/google-chrome'
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.headless=True
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
    now = datetime.datetime.now()
    filestosearch = '%s/*%s*doki ' % (dokidir, jnl)
    for i in range(3-1):
        filestosearch += '%s/%i/*%s*doki ' % (dokidir, now.year-i-1, jnl)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s | grep pubs.aip.org | sed 's/^_..//' | sed 's/..$//' " % (filestosearch))))
    print('%i records in backup (%s)' % (len(alreadyharvested), jnl))
    if len(alreadyharvested) > 2:
        print('[%s, ..., %s]' % (alreadyharvested[0], alreadyharvested[-1]))

urltrunk = 'http://aip.scitation.org/toc/%s/%s/%s?size=all' % (jnl,vol,iss)
if jnl in ['aqs']:
    urltrunk = 'https://avs.scitation.org/toc/%s/%s/%s?size=all' % (jnl,vol,iss)
print(urltrunk)

driver.get(urltrunk)
tocpage = BeautifulSoup(driver.page_source, features="lxml")

def getarticle(artlink, secs, p1):
    try:
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        artpage.body.find_all('div')
    except:
        try:
            print(' --- SLEEP ---')
            time.sleep(300)
            driver.get(artlink)
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            artpage.body.find_all('div')
        except:
            print(' --- SLEEEEEP ---')
            time.sleep(600)
            driver.get(artlink)
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            artpage.body.find_all('div')            
    rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : iss, 'tc' : typecode, 'keyw' : [],
           'note' : [artlink], 'p1' : p1}
    emails = {}
    if cnum:
        rec['cnum'] = cnum
    for sec in secs:
        rec['note'].append(sec)
        if sec == 'CONTRIBUTED REVIEW ARTICLES':
            rec['tc'] = 'R'    
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_institution',
                                        'citation_doi', 'citation_publication_date',
                                        'description', 'citation_title'])
    #abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'abstract'}):
        rec['abs'] = section.text.strip()
    #ORCIDs
    orcids = {}
    for div in artpage.body.find_all('div', attrs = {'class' : 'al-author-name'}):
        for a in div.find_all('a', attrs = {'class' : 'linked-name'}):
            name = re.sub(' \(.*', '', a.text.strip())
            for span in div.find_all('span', attrs = {'class' : 'al-orcid-id'}):
                orcid = 'ORCID:' + span.text.strip()
                if name in orcids:
                    orcids[name] = False
                else:
                    orcids[name] = orcid
                    #print('         ', name, orcid)
    #combine ORCID with affiliations
    newautaff = []
    for aa in rec['autaff']:
        name = re.sub('(.*), (.*)', r'\2 \1', aa[0])
        if name in orcids:            
            newautaff.append([aa[0], orcids[name]] + aa[1:])
            #print('   %s -> orcid.org/%s' % (name, orcids[name]))
        else:
            newautaff.append(aa)
    rec['autaff'] = newautaff
                    
        
    
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'ref-list'}):
        rec['refs'] = []
        for a in div.find_all('a'):
            if a.text in ['Google Scholar', 'Crossref', 'Search ADS']:
                a.decompose()
        for div2 in div.find_all('div', attrs = {'class' : 'ref-content'}):
            rec['refs'].append([('x', div2.text.strip())])
    
    ejlmod3.printrecsummary(rec)
    time.sleep(random.randint(30,90))
    return rec
                
sections = {}
tocheck = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'section-container'}):
    for child in div.contents:
        if child.name in ['h4', 'h3', 'h5', 'h6', 'h2']: 
            sections[child.name] = child.text.strip()
            lev = int(child.name[1])-2
            print(lev*'#', child.text.strip())
        elif child.name == 'section':
            print('section')
            for child2 in child.contents:
                if type(child2) == type(child):
                    if child2.name in ['h3', 'h4', 'h5', 'h6']:
                        sections[child2.name] = child.text.strip()
                        lev = int(child2.name[1])-2
                        print(lev*'*', child2.text.strip())
                    elif child2.name in ['section', 'div']:
                        for h in child2.find_all('h5'):
                            if h.has_attr('data-level'):
                                sections[h.name] = h.text.strip()
                                lev = int(h.name[1])-2
                                print(lev*'*', h.text.strip())
                        for a in child2.find_all('a', attrs = {'class' : 'viewArticleLink'}):
                            href = 'https://pubs.aip.org' + a['href']
                            print(' - ', href)
                            #articleID is not on indiviual article page (sic!)
                            p1 = re.sub('.*\/(\d\d+)\/.*', r'\1', href)
                            tocheck.append((href, p1, sections.values()))

random.shuffle(tocheck)
recs = []
i = 0
for (href, p1, secs) in tocheck:
    i += 1
    if href in ['/doi/full/10.1063/1.5019809']:
        print('skip %s' % (href))
    else:
        ejlmod3.printprogress('-', [[i, len(tocheck)], [href, p1]])
        keepit = True
        for sec in secs:
            if sec in ['From the Editor', "Readers' Forum", 'Issues and Events', 'Books',
                       'New Products', 'Obituaries', 'Quick Study', 'Back Scatter']:
                print('     skip "%s"' % (sec))
                keepit = False
        if keepit:
            rec = getarticle(href, secs, p1)
            if rec['autaff']:
                recs.append(rec)
                ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
print('%i records for %s' % (len(recs), jnlfilename))
#if not recs:
#    print(tocpage.text)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
driver.quit()
