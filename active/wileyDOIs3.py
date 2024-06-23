# -*- coding: UTF-8 -*-
#program to harvest individua DOIs from Wiley-journals
# FS 2023-12-11

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
#import cloudscraper
import undetected_chromedriver as uc
import random

publisher = 'WILEY'

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'WILEY_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)



sample = {'10.1002/spe.3039' : {'all' :  52, 'core' :      45},
          '10.1002/qute.201900141' : {'all' :  28, 'core' :      18},
          '10.1002/qute.202000005' : {'all' :  18, 'core' :      15}}
    
host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
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

urltrunk = 'http://onlinelibrary.wiley.com/doi'

driver.get('https://www.desy.de')
time.sleep(60)
               
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
    rec = {'tc' : 'P', 'artlink' : urltrunk + '/' +  doi, 'doi' : doi}
    jnl = re.sub('^10.\d+\/([a-z]+).*', r'\1', doi)
    if   (jnl == 'annphys'):
        issn = '1521-3889'
        doitrunk = '10.1002/andp'
        rec['jnl'] = 'Annalen Phys.'
    elif jnl in ['prop', 'fortp']:
        issn = '1521-3978'
        doitrunk = '10.1002/prop'
        rec['jnl'] = 'Fortsch.Phys.'
    elif jnl in ['cpama', 'cpa']:
        issn = '1097-0312'
        doitrunk = '10.1002/cpa'
        rec['jnl'] = 'Commun.Pure Appl.Math.'  
    elif (jnl == 'mdpc'):
        issn = '2577-6576'
        doitrunk = '10.1002/mdp2'
        rec['jnl'] = 'Mater.Des.Proc.Comm.'
    elif jnl in ['anyaa']:
        issn = '1749-6643'
        issn = '1749-6632'
        doitrunk = '10.1111/nyas'
        rec['jnl'] = 'Annals N.Y.Acad.Sci.'
    elif (jnl == 'ctpp'):
        issn = '1521-3986'
        doitrunk = '10.1002/ctpp'
        rec['jnl'] = 'Contrib.Plasma Phys.'
    elif (jnl == 'mma'):
        issn = '1099-1476'
        doitrunk = '10.1002/mma'
        rec['jnl'] = 'Math.Methods Appl.Sci.'
    #not harvested
    elif (jnl == 'jamma'):
        issn = '1521-4001'
        doitrunk = '10.1002/zamm'
        rec['jnl'] = 'J.Appl.Math.Mech.'
    elif (jnl == 'puz'):
        issn = '1521-3943'
        doitrunk = '10.1002/piuz'
        rec['jnl'] = 'Phys.Unserer Zeit'
    #now at other publishers    
    elif (jnl == 'mnraa'): 
        issn = '1356-2966'
        doitrunk = '10.1111/mnr'
        rec['jnl'] = 'Mon.Not Roy.Astron.Soc.'
    elif (jnl == 'mnraal'):
        issn = '1745-3933'
        doitrunk = '10.1002/mnl'
        rec['jnl'] = 'Mon.Not.Roy.Astron.Soc.'
    elif (jnl == 'asnaa'):
        issn = '1521-3994'
        doitrunk = '10.1002/asna'
        rec['jnl'] = 'Astron.Nachr.'
    elif (jnl == 'mtk'):
        issn = '2041-7942'
        doitrunk = '10.1112/mtk.'
        rec['jnl'] = 'Mathematika'
    elif jnl in ['aqt', 'qute']:
        issn = '2511-9044'
        doitrunk = '10.1002/qute.'
        rec['jnl'] = 'Adv.Quantum Technol.'
    elif jnl in ['quanteng', 'que']:
        issn = '2577-0470'
        doitrunk = '10.1002/que'
        rec['jnl'] = 'Quantum Eng.'
    #
    elif (jnl == 'mana'):
        issn = '1522-2616'
        doitrunk = '10.1002/mana'
        rec['jnl'] = 'Math.Nachr.'
    elif (jnl == 'pssa'):
        issn = '1862-6319'
        doitrunk = '10.1002/pssa'
        rec['jnl'] = 'Phys.Status Solidi'
    elif (jnl == 'pssr'):
        issn = '1862-6270'
        doitrunk = '10.1002/pssr'
        rec['jnl'] = 'Phys.Status Solidi RRL'
    elif (jnl == 'qua'):
        issn = '1097-461x'
        doitrunk = '10.1002/qua'
        rec['jnl'] = 'Int.J.Quant.Chem.'
    
    elif (jnl == 'pssb'):
        issn = '1521-3951'
        doitrunk = '10.1002/pssb'
        rec['jnl'] = 'Phys.Status Solidi B'
    elif (jnl == 'adma'):
        issn = '1521-4095'
        doitrunk = '10.1002/adma'
        rec['jnl'] = 'Adv.Mater.'
    elif (jnl == 'xrs'):
        issn = '1097-4539'
        doitrunk = '10.1002/'
        rec['jnl'] = 'X Ray Spectrom.'
    elif (jnl == 'qj'):
        issn = '1477-870X'
        doitrunk = '10.1002/qj'
        rec['jnl'] = 'Quarterly Journal of the Royal Meteorological Society'
    elif (jnl == 'mop'):
        issn = '1098-2760'
        doitrunk = '10.1002/mop'
        rec['jnl'] = 'Microw.Opt.Technol.Lett.'
    elif (jnl == 'ntls'):
        issn = '2698-6248'
        doitrunk = '10.1002/ntls'
        rec['jnl'] = 'Natural Sci.'
    elif (jnl == 'apxr'):
        issn = '2751-1200'
        doitrunk = '10.1002/apxr'
        rec['jnl'] = 'Adv.Phys.Res.'
    elif (jnl == 'cjoc'):
        issn = '1614-7065'
        doitrunk = '10.1002/cjoc'
        rec['jnl'] = 'Chin.J.Chem.'
    elif (jnl == 'adfm'):
        issn = '1616-3028'
        doitrunk = '10.1002/adfm'
        rec['jnl'] = 'Adv.Funct.Mater.'
    elif (jnl == 'lpor'):
        issn = '1863-8899'
        doitrunk = '10.1002/lpor'
        rec['jnl'] = 'Laser Photonics Rev.'
    elif (jnl == 'adma'):
        issn = '1521-4095'
        doitrunk = '10.1002/adma'
        rec['jnl'] = 'Adv.Mater.'
    elif (jnl == 'anie'):
        issn = '1521-3773'
        doitrunk = '10.1002/anie'
        rec['jnl'] = 'Angew.Chem.Int.Ed.'
    elif (jnl == 'jcc'):
        issn = '1096-987x'
        doitrunk = '10.1002/jcc'
        rec['jnl'] = 'J.Comput.Chem.'
    elif (jnl == 'net'):
        doitrunk = '10.1002/net'
        rec['jnl'] = 'Networks'
    elif (jnl == 'andp'):
        doitrunk = '10.1002/anp'
        rec['jnl'] = 'Annalen Phys.'
    elif (jnl == 'plms'):
        doitrunk = '10.1002/plms'
        rec['jnl'] = 'Proc.Lond.Math.Soc.'
    elif (jnl == 'nme'):
        doitrunk = '10.1002/nme'
        rec['jnl'] = 'Int.J.Numer.Meth.Eng.'
    elif (jnl == 'wics'):
        doitrunk = '10.1002/wics'
        rec['jnl'] = 'WIREs Comput.Stat.'
    elif (jnl == 'wcms'):
        doitrunk = '10.1002/wcms'
        rec['jnl'] = 'WIREs Comput.Mol.Sci.'
    elif (jnl == 'cta'):
        doitrunk = '10.1002/cta'
        rec['jnl'] = 'Int.J.Circuit Theor.Appl.'
    elif (jnl == 'cpe'):
        doitrunk = '10.1002/cpe'
        rec['jnl'] = 'Concurrency Comput.Pract.Exp.'
    elif (jnl == 'aic'):
        doitrunk = '10.1002/aic'
        rec['jnl'] = 'Aiche J.'
    elif (jnl == 'adts'):
        doitrunk = '10.1002/adts'
        rec['jnl'] = 'Adv.Theor.Simul.'
    elif (jnl == 'spe'):
        doitrunk = '10.1002/spe'
        rec['jnl'] = 'Software Pract.Exper.'
    elif re.search('10.1111\/j.1749\-6632', doi):
        rec['jnl'] = 'Annals N.Y.Acad.Sci.'
    elif re.search('10.1111\/j.1469\-1809', doi):
        rec['jnl'] = 'Annals Eugen.'
    elif re.search('10.1111\/j.2517\-6161', doi):
        rec['jnl'] = 'J.Roy.Statist.Soc.B'
    elif doi in ['10.1002\/047174882X', '10.1002/j.1538-7305.1950.tb00463.x']:
        rec['jcl'] = 'Bell Syst.Tech.J.'
    if not 'jnl' in rec:
        missingjournals.append(doi)
        continue

    try:
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
        driver.get(rec['artlink'])
        artpage  = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                            'citation_lastpage', 'citation_publication_date', 'citation_author',
                                            'citation_author_institution', 'citation_author_orcid', 
                                            'citation_author_email', 'citation_volume',
                                            'citation_issue'])#'citation_pdf_url' does not resolve
        rec['autaff'][0]
    except:
        rec['artlink'] = re.sub('doi\/', 'doi/ftr/', rec['artlink'])
        print('  ... try again in 90-190 s')
        time.sleep(random.randint(90,190))
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
        driver.get(rec['artlink'])
        artpage  = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                            'citation_lastpage', 'citation_publication_date', 'citation_author',
                                            'citation_author_institution', 'citation_author_orcid',
                                            'citation_author_email', 'citation_volume',
                                            'citation_issue'])#'citation_pdf_url' does not resolve
    for span in artpage.find_all('span', attrs = {'class' : 'primary-heading'}):
        if span.text.strip() in ['Frontispiece', 'Announcement']:
            print('    skip ', span.text)
            continue
    if not 'p1' in rec:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'article_references'}):
            rec['p1'] = re.sub('.*, (.+?)\..*', r'\1', meta['content'].strip())
            rec['p1'] = re.sub('.*: (\d+)', r'\1', rec['p1'])
    ejlmod3.globallicensesearch(rec, artpage)
    #cover picture
    for span in artpage.body.find_all('span', attrs = {'class' : 'primary-heading'}):
        if span.text.strip() == 'Cover Picture':
            print('   skip Cover Picture')
            keepit = False
    #ORCIDS etc.
    divs = artpage.body.find_all('div', attrs = {'class' : 'comma__list'})
    if len(divs) > 1:
        rec['autaff'] = []
        for div in divs[0].find_all('div', attrs = {'class' : 'author-info'}):
            emailfound = False
            for p in div.find_all('p', attrs = {'class' : 'author-name'}):
                rec['autaff'].append([p.text])
                p.decompose()
            for p in div.find_all('p', attrs = {'class' : 'author-type'}):
                p.decompose()
            for ul in div.find_all('ul', attrs = {'class' : 'rlist'}):
                for a in ul.find_all('a', attrs = {'class' : 'sm-account__link'}):
                    if re.search('mailto', a['href']):
                        rec['autaff'][-1].append(re.sub('mailto:', 'EMAIL:', a['href']))
                        emailfound = True
                    elif re.search('orcid.org', a['href']):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
            for p in div.find_all('p'):
                pt = p.text.strip()
                if re.search('^[eE].?mail:.*@', pt):
                    if not emailfound:
                        rec['autaff'][-1].append(re.sub('.*: *', 'EMAIL:', pt))
                        emailfound = True
                elif re.search('^Contribution:', pt) or pt in ['Deceased author', 'Correspondence']:
                    pass
                else:
                    rec['autaff'][-1].append(pt)
    #abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'article-section__abstract'}):
        rec['abs'] = section.text.strip()
        rec['abs'] = re.sub('^Abstract', '', rec['abs'])
    #special issue
    for p in artpage.body.find_all('p', attrs = {'class' : 'specialIssue'}):
        note = p.text.strip()
        rec['note'].append(note)
        if re.search('(Proceedings|Conference|Workshop)',note):
            typecode = 'C'
    #references ?
    uls = artpage.body.find_all('ul', attrs = {'class' : 'article-section__references-list'})
    if not uls:
        for section in artpage.body.find_all('section', attrs = {'id' : 'references-section'}):
            uls = section.find_all('ul', attrs = {'class' : 'rlist'})
            len(uls)
    for ul in uls:
        rec['refs'] = []
        for li in ul.find_all('li'):
            refno = False
            if not li.has_attr('data-bib-id'):
                continue
            for span in li.find_all('span', attrs = {'class' : 'bullet'}):
                refno = span.text
                span.decompose()
            for a in li.find_all('a'):
                if a.text in ['CrossRef', 'Crossref']:
                    rdoi = re.sub('.*=', '', a['href'])
                    rdoi = re.sub('%28', '(', rdoi)
                    rdoi = re.sub('%29', ')', rdoi)
                    rdoi = re.sub('%2F', '/', rdoi)
                    rdoi = re.sub('%3A', ':', rdoi)
                    a.replace_with(', DOI: %s' % (rdoi))
                else:
                    a.replace_with('')
            for div in li.find_all('div', attrs = {'class' : 'extra-links'}):
                divt = div.text.strip()
                div.replace_with(divt + ' XXXTRENNER ')
            lit = re.sub('[\n\t\r]', ' ', li.text.strip())
            lit = re.sub(' *XXXTRENNER$', '', lit)
            refs = re.split(' XXXTRENNER ', lit)
            for ref in refs:
                ref = re.sub('; *, DOI', ', DOI', ref)
                if len(refs) > 1 and re.search('^[a-z]\)', ref):
                    if refno:
                        #rec['refs'].append([('x', '[%s%s] %s' % (refno, ref[0], ref[2:]))])
                        rec['refs'].append([('x', '[%s] %s' % (refno, ref[2:]))])
                    else:
                        rec['refs'].append([('x', ref)])
                else:
                    if refno:
                        rec['refs'].append([('x', '[%s] %s' % (refno, ref[2:]))])
                    else:
                        rec['refs'].append([('x', ref)])
                        
    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')

    time.sleep(random.randint(30,90))
