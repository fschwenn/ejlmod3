# -*- coding: utf-8 -*-
#program to harvest individual DOIs from AIP-journals
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
import json
regexpref = re.compile('[\n\r\t]')

publisher = 'AIP'
typecode = 'P'
skipalreadyharvested = False
corethreshold = 15
bunchsize = 10

jnlfilename = 'AIP_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1063/1.5129672' : {'all' :  38, 'core' :      17},
          '10.1063/5.0020277' : {'all' :  38, 'core' :      14},
          '10.1063/1.5085002' : {'all' :  34, 'core' :      11},
          '10.1063/5.0023103' : {'all' :  30, 'core' :      16},
          '10.1063/5.0006002' : {'all' :  26, 'core' :      20},
          '10.1063/1.4992118' : {'all' :  26, 'core' :      11},
          '10.1063/5.0038838' : {'all' :  23, 'core' :      17},
          '10.1063/5.0047260' : {'all' :  22, 'core' :      13},
          '10.1063/1.5086493' : {'all' :  22, 'core' :      10},
          '10.1063/1.4982168' : {'all' :  20, 'core' :      12},
          '10.1063/1.5121444' : {'all' :  20, 'core' :      11},
          '10.1063/1.4994303' : {'all' :  20, 'core' :      10},
          '10.1063/5.0021755' : {'all' :  19, 'core' :      13},
          '10.1063/5.0004322' : {'all' :  19, 'core' :      11},
          '10.1063/1.4993937' : {'all' :  18, 'core' :      15},
          '10.1063/1.5110682' : {'all' :  18, 'core' :      14},
          '10.1063/1.5053461' : {'all' :  18, 'core' :      13},
          '10.1063/1.5002540' : {'all' :  18, 'core' :      11}}


    
host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
#    options.binary_location='/usr/bin/google-chrome'
    #options.add_argument('--headless')
#    options.add_argument('--no-sandbox')
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

def getarticle(artlink, secs):
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
    rec = {'tc' : typecode, 'keyw' : [],
           'note' : [artlink]}
    emails = {}
    for sec in secs:
        rec['note'].append(sec)
        secu = sec.upper()
        if secu in ['CONTRIBUTED REVIEW ARTICLES', 'REVIEW ARTICLES']:
            rec['tc'] = 'PR'
        if secu in ['CLASSICAL AND QUANTUM GRAVITY', 'GENERAL RELATIVITY AND GRAVITATION']:
            rec['fc'] = 'g'
        elif secu in ['ACCELERATOR', 'COMPACT PARTICLE ACCELERATORS TECHNOLOGY', 'LATEST TRENDS IN FREE ELECTRON LASERS', 'PLASMA-BASED ACCELERATORS, BEAMS, RADIATION GENERATION']:
            rec['fc'] = 'b'
        elif secu in ['CRYPTOGRAPHY AND ITS APPLICATIONS IN INFORMATION SECURITY']:
            rec['fc'] = 'c'
        elif secu in ['MACROSCOPIC AND HYBRID QUANTUM SYSTEMS', 'QUANTUM MEASUREMENT TECHNOLOGY', 'QUANTUM PHOTONICS', 'QUANTUM COMPUTERS AND SOFTWARE', 'QUANTUM SENSING AND METROLOGY', 'QUANTUM INFORMATION AND COMPUTATION', 'QUANTUM MECHANICS - GENERAL AND NONRELATIVISTIC', 'QUANTUM PHYSICS AND TECHNOLOGY', 'QUANTUM TECHNOLOGIES']:
            rec['fc'] = 'k'
        elif secu in ['IMPEDANCE SPECTROSCOPY AND ITS APPLICATION IN MEASUREMENT AND SENSOR TECHNOLOGY', 'SENSORS; ACTUATORS; POSITIONING DEVICES; MEMS/NEMS; ENERGY HARVESTING']:
            rec['fc'] = 'i'
        elif secu in ['REPRESENTATION THEORY AND ALGEBRAIC METHODS', 'METHODS OF MATHEMATICAL PHYSICS', 'PARTIAL DIFFERENTIAL EQUATIONS']:
            rec['fc'] = 'm'
        elif secu in ['HELIOSPHERIC AND ASTROPHYSICAL PLASMAS']:
            rec['fc'] = 'a'
        elif secu in ['MANY-BODY AND CONDENSED MATTER PHYSICS']:
            rec['fc'] = 'f'
        elif secu in ['STATISTICAL PHYSICS']:
            rec['fc'] = 's'            
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_institution',
                                        'citation_doi', 'citation_publication_date',
                                        'description', 'citation_title',
                                        'citation_reference', 'citation_volume',
                                        'citation_issue'])
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_journal_title'}):
        jnl = ''
        if meta['content'] in ["The Journal of Chemical Physics"]:
            rec['jnl'] = 'J.Chem.Phys.'
        elif meta['content'] in ['Applied Physics Letters']:
            rec['jnl'] = 'Appl.Phys.Lett.'
        elif meta['content'] in ['AIP Advances']:
            rec['jnl'] = 'AIP Adv.'
        elif meta['content'] in ['Journal of Mathematical Physics']:
            rec['jnl'] = 'J.Math.Phys.'
        elif meta['content'] in ['APL Photonics']:
            rec['jnl'] = 'APL Photon.'
        elif meta['content'] in ['Review of Scientific Instruments']:
            rec['jnl'] = 'Rev.Sci.Instrum.'
        elif meta['content'] in ['Physics of Plasmas']:
            rec['jnl'] = 'Phys.Plasmas'
        elif meta['content'] in ['Applied Physics Reviews']:
            rec['jnl'] = 'Appl.Phys.Rev.'
        elif meta['content'] in ['Physics Today']:
            rec['jnl'] = 'Phys.Today'
            jnl = 'pto'
        elif meta['content'] in ['Journal of Applied Physics']:
            rec['jnl'] = 'J.Appl.Phys.'
        elif meta['content'] in ['APL Materials']:
            rec['jnl'] = 'APL Mater.'
        elif meta['content'] in ['AIP Conference Proceedings']:
            rec['jnl'] = 'AIP Conf.Proc.'
        else:
            if not meta['content'] in missingjournals:
                missingjournals.append(meta['content'])
    if not 'jnl' in rec:
        return False
    #abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'abstract'}):
        rec['abs'] = section.text.strip()
    #license and fulltext
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    else:
        for h1 in artpage.find_all('h1'):
            for ii in h1.find_all('i', attrs = {'class' : ['icon-availability_free',
                                                           'icon-availability_open']}):
                ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    #article ID
    for script in artpage.find_all('script', attrs = {'type' : 'application/ld+json'}):
        scriptt = re.sub('[\n\t]', '', script.contents[0].strip())
        metadata = json.loads(scriptt)
        if 'pageStart' in metadata:
            rec['p1'] = metadata['pageStart']
        if jnl in ['pto']:
            if 'pageEnd' in metadata:
                rec['p2'] = metadata['pageEnd']
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
    if 'autaff' in rec:
        newautaff = []
        for aa in rec['autaff']:
            name = re.sub('(.*), (.*)', r'\2 \1', aa[0])
            if name in orcids and orcids[name]: 
                newautaff.append([aa[0], orcids[name]] + aa[1:])
                #print('   %s -> orcid.org/%s' % (name, orcids[name]))
            else:
                newautaff.append(aa)
        rec['autaff'] = newautaff
                        
    #field code for conferences
    if len(sys.argv) > 5:
        rec['fc'] = sys.argv[5]
    
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'ref-list'}):
        rec['refs'] = []
        for a in div.find_all('a'):
            if a.text in ['Google Scholar', 'Crossref', 'Search ADS', 'PubMed']:
                a.decompose()
        for div2 in div.find_all('div', attrs = {'class' : 'ref-content'}):
            rec['refs'].append([('x', re.sub('[\n\t\r]', ' ', div2.text.strip()))])
    
    ejlmod3.printrecsummary(rec)
    #print('AUTAFF', rec['autaff'])
    time.sleep(random.randint(30,90))    
    return rec
                
i = 0
recs = []
missingjournals = []
for doi in sample:
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    href = 'https://doi.org/' + doi
    rec = getarticle(href, [])
    if rec:
        #sample note
        rec['note'] = ['reharvest_based_on_refanalysis',
                       '%i citations from INSPIRE papers' % (sample[doi]['all']),
                       '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')









