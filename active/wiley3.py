# -*- coding: UTF-8 -*-
#program to harvest Wiley-journals
# FS 2016-12-13

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
import undetected_chromedriver as uc

publisher = 'WILEY'
jnl = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]
year = sys.argv[4]
jnlfilename = re.sub('\/','-',jnl+vol+'.'+issue)
#harvested vi desydoc
if   (jnl == 'annphys'):
    issn = '1521-3889'
    doitrunk = '10.1002/andp'
    jnlname = 'Annalen Phys.'
elif (jnl == 'fortp'):
    issn = '1521-3978'
    doitrunk = '10.1002/prop'
    jnlname = 'Fortsch.Phys.'
elif (jnl == 'cpama'):
    issn = '1097-0312'
    doitrunk = '10.1002/cpa'
    jnlname = 'Commun.Pure Appl.Math.'  
#harevsted by hand
elif (jnl == 'mdpc'):
    issn = '2577-6576'
    doitrunk = '10.1002/mdp2'
    jnlname = 'Mater.Des.Proc.Comm.'
elif (jnl == 'anyaa'):
    issn = '1749-6643'
    doitrunk = '10.1111/nyas'
    jnlname = 'Annals N.Y.Acad.Sci.'
elif (jnl == 'ctpp'):
    issn = '1521-3986'
    doitrunk = '10.1002/ctpp'
    jnlname = 'Contrib.Plasma Phys.'
elif (jnl == 'mma'):
    issn = '1099-1476'
    doitrunk = '10.1002/mma'
    jnlname = 'Math.Methods Appl.Sci.'
#not harvested
elif (jnl == 'jamma'):
    issn = '1521-4001'
    doitrunk = '10.1002/zamm'
    jnlname = 'J.Appl.Math.Mech.'
elif (jnl == 'puz'):
    issn = '1521-3943'
    doitrunk = '10.1002/piuz'
    jnlname = 'Phys.Unserer Zeit'
#now at other publishers    
elif (jnl == 'mnraa'): 
    issn = '1356-2966'
    doitrunk = '10.1111/mnr'
    jnlname = 'Mon.Not Roy.Astron.Soc.'
elif (jnl == 'mnraal'):
    issn = '1745-3933'
    doitrunk = '10.1002/mnl'
    jnlname = 'Mon.Not.Roy.Astron.Soc.'
elif (jnl == 'asnaa'):
    issn = '1521-3994'
    doitrunk = '10.1002/asna'
    jnlname = 'Astron.Nachr.'
elif (jnl == 'mtk'):
    issn = '2041-7942'
    doitrunk = '10.1112/mtk.'
    jnlname = 'Mathematika'
elif (jnl == 'aqt'):
    issn = '2511-9044'
    doitrunk = '10.1002/qute.'
    jnlname = 'Adv.Quantum Technol.'
elif (jnl == 'quanteng'):
    issn = '2577-0470'
    doitrunk = '10.1002/que'
    jnlname = 'Quantum Eng.'
#
elif (jnl == 'mana'):
    issn = '1522-2616'
    doitrunk = '10.1002/mana'
    jnlname = 'Math.Nachr.'
elif (jnl == 'pssa'):
    issn = '1862-6319'
    doitrunk = '10.1002/pssa'
    jnlname = 'Phys.Status Solidi'
elif (jnl == 'pssr'):
    issn = '1862-6270'
    doitrunk = '10.1002/pssr'
    jnlname = 'Phys.Status Solidi RRL'
elif (jnl == 'qua'):
    issn = '1097-461x'
    doitrunk = '10.1002/qua'
    jnlname = 'Int.J.Quant.Chem.'

elif (jnl == 'pssb'):
    issn = '1521-3951'
    doitrunk = '10.1002/pssb'
    jnlname = 'Phys.Status Solidi B'
elif (jnl == 'adma'):
    issn = '1521-4095'
    doitrunk = '10.1002/adma'
    jnlname = 'Adv.Mater.'
elif (jnl == 'xrs'):
    issn = '1097-4539'
    doitrunk = '10.1002/'
    jnlname = 'X Ray Spectrom.'
elif (jnl == 'qj'):
    issn = '1477-870X'
    doitrunk = '10.1002/qj'
    jnlname = 'Quarterly Journal of the Royal Meteorological Society'
elif (jnl == 'mop'):
    issn = '1098-2760'
    doitrunk = '10.1002/mop'
    jnlname = 'Microw.Opt.Technol.Lett.'


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

urltrunk = 'http://onlinelibrary.wiley.com/doi'
print("%s %s, Issue %s" %(jnlname,vol,issue))
if re.search('1111',doitrunk):
    toclink = '%s/%s.%s.%s.issue-%s/issuetoc' % (urltrunk,doitrunk,year,vol,issue)
else:
    toclink = '%s/%s.v%s.%s/issuetoc' % (urltrunk,doitrunk,vol,issue)
    toclink = 'https://onlinelibrary.wiley.com/toc/%s/%s/%s/%s'  % (issn[:4]+issn[5:], year, vol, issue)
print(toclink)

driver.get(toclink)
tocpage = BeautifulSoup(driver.page_source, features="lxml")


recs = []
alldois = []
for div in tocpage.find_all('div', attrs = {'class' : 'issue-item'}):
    for h3 in div.find_all('h3'):
        tit = h2.text.strip()
        if tit == 'Contents' or re.search('^Issue Information', tit) or re.search('^Cover Picture', tit) or re.search('^Masthead', tit):
            continue
    for h2 in div.find_all('h2'):
        tit = h2.text.strip()
    if tit == 'Contents' or re.search('^Issue Information', tit) or re.search('^Cover Picture', tit) or re.search('^Masthead', tit):
        continue
    rec = {'tit' : tit, 'year' : year, 'jnl' : jnlname, 'autaff' : [],
           'note' : [], 'vol' : vol, 'issue' : issue, 'keyw' : []}
    if jnl == 'pssa':
        rec['vol'] = 'A'+vol
    for a in div.find_all('a', attrs = {'class' : 'issue-item__title'}):
        rec['doi'] = re.sub('.*\/(10\..*)', r'\1', a['href'])
        rec['artlink'] = 'https://onlinelibrary.wiley.com' + a['href']
    if not rec['doi'] in alldois:
        recs.append(rec)
        alldois.append(rec['doi'])
    
i = 0
for rec in recs:
    i += 1
    typecode = 'P'
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['doi']], [rec['artlink']]])
    time.sleep(5)
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                        'citation_lastpage', 'citation_publication_date', 'citation_author',
                                        'citation_author_institution', 'citation_author_orcid',
                                        'citation_author_email'])#'citation_pdf_url' does not resolve
    if not 'p1' in rec:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'article_references'}):
            rec['p1'] = re.sub('.*, (.+?)\..*', r'\1', meta['content'].strip())
            rec['p1'] = re.sub('.*: (\d+)', r'\1', rec['p1'])
    ejlmod3.globallicensesearch(rec, artpage)
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
    if not jnl in ['puz']:
        rec['tc'] = typecode
    else:
        rec['tc'] = ''
    ejlmod3.printrecsummary(rec)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
ejlmod3.writeretrival(jnlfilename)
