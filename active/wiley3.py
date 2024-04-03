# -*- coding: UTF-8 -*-
#program to harvest Wiley-journals
# FS 2016-12-13
# FS 2022-12-12

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

skipalreadyharvested = True
bunchsize = 10
jnl = sys.argv[1]
vol = sys.argv[2]
issues = sys.argv[3]
year = sys.argv[4]
jnlfilename = re.sub('\/','-',jnl+vol+'.'+re.sub(',', '-', issues)+'_'+ejlmod3.stampoftoday())
donepath = '/afs/desy.de/group/library/publisherdata/wiley/done'
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
    issn = '1749-6632'
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
elif (jnl == 'ntls'):
    issn = '2698-6248'
    doitrunk = '10.1002/ntls'
    jnlname = 'Natural Sci.'
elif (jnl == 'apxr'):
    issn = '2751-1200'
    doitrunk = '10.1002/apxr'
    jnlname = 'Adv.Phys.Res.'
elif (jnl == 'cjoc'):
    issn = '1614-7065'
    doitrunk = '10.1002/cjoc'
    jnlname = 'Chin.J.Chem.'
elif (jnl == 'adfm'):
    issn = '1616-3028'
    doitrunk = '10.1002/adfm'
    jnlname = 'Adv.Funct.Mater.'
elif (jnl == 'lpor'):
    issn = '1863-8899'
    doitrunk = '10.1002/lpor'
    jnlname = 'Laser Photonics Rev.'
elif (jnl == 'adma'):
    issn = '1521-4095'
    doitrunk = '10.1002/adma'
    jnlname = 'Adv.Mater.'
elif (jnl == 'anie'):
    issn = '1521-3773'
    doitrunk = '10.1002/anie'
    jnlname = 'Angew.Chem.Int.Ed.'
elif (jnl == 'jcc'):
    issn = '1096-987x'
    doitrunk = '10.1002/jcc'
    jnlname = 'J.Comput.Chem.'
elif (jnl == 'ietqc'):
    issn = '2632-8925'
    doitrunk = '10.1049/qtc2'
    jnlname = 'IET Quant.Commun.'
    

    
if skipalreadyharvested:
    alldois = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alldois = []


#scraper = cloudscraper.create_scraper()
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
driver.get('http://onlinelibrary.wiley.com')
time.sleep(15)
prerecs = []
for issue in re.split(',', issues):
    print("%s %s, Issue %s" %(jnlname,vol,issue))
    if re.search('1111',doitrunk):
        toclink = '%s/%s.%s.%s.issue-%s/issuetoc' % (urltrunk,doitrunk,year,vol,issue)
        toclink = 'https://nyaspubs.onlinelibrary.wiley.com/toc/%s/%s/%s/%s'  % (issn[:4]+issn[5:], year, vol, issue)
    else:
        toclink = '%s/%s.v%s.%s/issuetoc' % (urltrunk,doitrunk,vol,issue)
        toclink = 'https://onlinelibrary.wiley.com/toc/%s/%s/%s/%s'  % (issn[:4]+issn[5:], year, vol, issue)
    ejlmod3.printprogress('##', [[issue, issues], [toclink]])

    #tocpage = BeautifulSoup(scraper.get(toclink).text, features="lxml")
    driver.get(toclink)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")

    for divc in tocpage.find_all('div', attrs = {'class' : 'issue-items-container'}):
        headline = divc.find_all('h3')
        keepit = True
        if len(headline) > 1 and headline[1].text.strip() == 'This article corrects the following:':
            headtit = 'Corrigenda'
            ejlmod3.printprogress('~', [[headtit], [len(prerecs)]])
        elif len(headline) > 1 and headline[1].text.strip() in ['Correction(s) for this article', 'This article relates to:', 'This article retracts the following:', 'Retraction(s) for this article']:
            headtit = headline[0].text.strip()
            ejlmod3.printprogress('~', [[headtit], [len(prerecs)]])
        elif len(headline) == 1:
            headtit = headline[0].text.strip()
            ejlmod3.printprogress('~', [[headtit], [len(prerecs)]])
        else:
            print(headline)
            sys.exit(0)
        if headtit == 'Contents' or re.search('^Issue Information', headtit) or re.search('^Cover Picture', headtit) or re.search('^Cover Image', headtit) or re.search('^Masthead', headtit):
            keepit = False
        elif re.search('^Introducing .$', headtit) or headtit in ['Frontispiece', 'Announcement', 'Graphical Abstract',
                                                                  'Team profile', 'Team Profile', 'Obituary', 'Editorials',
                                                                  'Classifieds: Jobs and Awards, Products and Services',
                                                                  'ISSUE INFORMATION', 'BOOKS IN BRIEF', 'COMMENTARY', 'News',
                                                                  'PERSPECTIVE', 'CONCISE REPORT', 'ISSUE INFORMATION - TOC',
                                                                  'Front Cover', 'Inside Front Cover', 'Inside Back Cover',
                                                                  'Back Cover', 'Covers', 'Cover Image', 'Guest Editorial',
                                                                  'PREFACE', 'COVER PICTURE', 'CONTENTS', 'Author Profile',
                                                                  'GUEST EDITORIAL', 'Editorial']:
            keepit = False
        if keepit:
            for div in divc.find_all('div', attrs = {'class' : 'issue-item'}):
                for h2 in div.find_all('h2'):
                    tit = h2.text.strip()
                rec = {'tit' : tit, 'year' : year, 'jnl' : jnlname, 'autaff' : [],
                       'note' : [headtit], 'vol' : vol, 'issue' : issue, 'keyw' : []}
                if jnl == 'pssa':
                    rec['vol'] = 'A'+vol
                for a in div.find_all('a', attrs = {'class' : 'issue-item__title'}):
                    rec['doi'] = re.sub('.*\/(10\..*)', r'\1', a['href'])
                    rec['artlink'] = 'https://onlinelibrary.wiley.com' + a['href']
                if not rec['doi'] in alldois:
                    prerecs.append(rec)
                    alldois.append(rec['doi'])
                    print('      ', rec['doi'])
        divc.decompose()

    print('>>>')
    for div in tocpage.find_all('div', attrs = {'class' : 'issue-item'}):
        keepit = True
        for h3 in div.find_all('h3'):
            headtit = h3.text.strip()
            if headtit == 'Contents' or re.search('^Issue Information', headtit) or re.search('^Cover Picture', headtit) or re.search('^Cover Image', headtit) or re.search('^Masthead', headtit):
                keepit = False
            if re.search('^Introducing .$', headtit) or headtit in ['Frontispiece', 'Announcement', 'Graphical Abstract',
                                                                    'Team profile', 'Team Profile', 'Obituary', 'Editorials',
                                                                    'Classifieds: Jobs and Awards, Products and Services',
                                                                    'ISSUE INFORMATION', 'BOOKS IN BRIEF', 'COMMENTARY', 'News',
                                                                    'PERSPECTIVE', 'CONCISE REPORT', 'ISSUE INFORMATION - TOC',
                                                                    'Front Cover', 'Inside Front Cover', 'Inside Back Cover',
                                                                    'Back Cover', 'Covers', 'Cover Image', 'Guest Editorial',
                                                                    'PREFACE', 'COVER PICTURE', 'CONTENTS', 'Editorial',
                                                                    'FRONT COVER']:
                keepit = False
        for h2 in div.find_all('h2'):
            tit = h2.text.strip()
        if tit == 'Contents' or re.search('^Issue Information', tit) or re.search('^Cover Picture', tit) or re.search('^Cover Image', tit) or re.search('^Masthead', tit):
            keepit = False
        if re.search('^Introducing .$', tit) or tit in ['Frontispiece', 'Announcement', 'Graphical Abstract', 'Team profile', 'Classifieds: Jobs and Awards, Products and Services']:
            keepit = False
        rec = {'tit' : tit, 'year' : year, 'jnl' : jnlname, 'autaff' : [],
               'note' : [], 'vol' : vol, 'issue' : issue, 'keyw' : []}    
        if jnl == 'pssa':
            rec['vol'] = 'A'+vol
        for a in div.find_all('a', attrs = {'class' : 'issue-item__title'}):
            rec['doi'] = re.sub('.*\/(10\..*)', r'\1', a['href'])
            rec['artlink'] = 'https://onlinelibrary.wiley.com' + a['href']
        if keepit and not rec['doi'] in alldois:
            prerecs.append(rec)
            alldois.append(rec['doi'])
            print('      ', rec['doi'])
    time.sleep(random.randint(70, 130))

#if not alldois:
#    print(tocpage)
    
i = 0
recs = []
for rec in prerecs:
    i += 1
    typecode = 'P'
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['doi']], [rec['artlink']]])
    try:
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
        driver.get(rec['artlink'])
        artpage  = BeautifulSoup(driver.page_source, features="lxml")
        for span in artpage.body.find_all('span', attrs = {'class' : 'primary-heading'}):
            if span.text.strip() == 'Cover Picture':
                keepit = False
        if keepit:
            ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                                'citation_lastpage', 'citation_publication_date', 'citation_author',
                                                'citation_author_institution', 'citation_author_orcid', 
                                                'citation_author_email'])#'citation_pdf_url' does not resolve
            rec['autaff'][0]
    except:
        print('  ... try again in 90-190 s')
        rec['artlink'] = re.sub('doi\/', 'doi/ftr/', rec['artlink'])
        time.sleep(random.randint(90,190))
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
        driver.get(rec['artlink'])
        artpage  = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                            'citation_lastpage', 'citation_publication_date', 'citation_author',
                                            'citation_author_institution', 'citation_author_orcid',
                                            'citation_author_email'])#'citation_pdf_url' does not resolve
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
    if not jnl in ['puz']:
        rec['tc'] = typecode
    else:
        rec['tc'] = ''
    if keepit:
        if len(sys.argv) > 5:
            rec['tc'] = 'C'
            rec['cnum'] = sys.argv[5]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))#, retfilename='retfiles_special')
    time.sleep(random.randint(70, 130))

os.system('touch %s/%s' % (donepath, jnlfilename[:-11]))
