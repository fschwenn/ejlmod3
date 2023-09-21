# -*- coding: UTF-8 -*-
# crawls iop web page to get metadata of journal issue
#
# FS 2017-05-15
# FS 2022-11-27

import os
import sys
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc

publisher = 'IOP'
regexpiopurl = re.compile('http...iopscience.iop.org.')
regexpdxdoi = re.compile('http...dx.doi.org.')

#driver
host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium-browser'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    driver.implicitly_wait(30)

book = False
starturls = re.split(',', sys.argv[1])
issns = [re.sub('.*\/(\d\d\d\d\-\d\d\d.)\/.*', r'\1', starturl) for starturl in starturls]
if len(set(issns)) > 1:
    print('several issues only works (at the moment) not for different journals')
    print(set(issns))
    sys.exit(0)
else:
    issn = issns[0]

jnls = {'1538-3881': 'Astron.J.',
        '0004-637X': 'Astrophys.J.',
        '1538-4357': 'Astrophys.J.',
        '2041-8205': 'Astrophys.J.Lett.',
        '0067-0049': 'Astrophys.J.Supp.',
        '0264-9381': 'Class.Quant.Grav.',
        '1009-9271': 'Chin.J.Astron.Astrophys.',
        '1009-1963': 'Chin.Phys.',
        '1674-1056': 'Chin.Phys.',
        '1674-1137': 'Chin.Phys.',
        '0256-307X': 'Chin.Phys.Lett.',
        '0253-6102': 'Commun.Theor.Phys.',
        '0143-0807': 'Eur.J.Phys.',
        '0295-5075': 'EPL',
        '0266-5611': 'Inv.Problems',
        '1757-899X': 'IOP Conf.Ser.Mater.Sci.Eng.',
        '1751-8121': 'J.Phys.',
        '1742-6596': 'J.Phys.Conf.Ser.',
        '0954-3899': 'J.Phys.',
        '1361-6463': 'J.Phys.',
        '1475-7516': 'JCAP ',
        '1126-6708': 'JHEP ',
        '1748-0221': 'JINST ',
        '1742-5468': 'JSTAT ',
        '0957-0233': 'Measur.Sci.Tech.',
        '1367-2630': 'New J.Phys.',
        '0031-9120': 'Phys.Educ.',
        '1063-7869': 'Phys.Usp.',
        '0034-4885': 'Rep.Prog.Phys.',
        '1674-4527': 'Res.Astron.Astrophys.',
        '1402-4896': 'Phys.Scripta',        
        '0953-2048': 'Supercond.Sci.Technol.',
        '2399-6528': 'J.Phys.Comm.',
        '1757-899X': 'IOP Conf.Ser.Mater.Sci.Eng.',
        '0036-0279': 'Russ.Math.Surveys',
        '0951-7715': 'Nonlinearity',
        '0953-4075': 'J.Phys.',
        '0953-8984': 'J.Phys.Condens.Matter',
        '0031-9155': 'Phys.Med.Biol.',
        '1538-3873': 'Publ.Astron.Soc.Pac.',
        '2399-6528': 'J.Phys.Comm.',
        '0741-3335': 'Plasma Phys.Control.Fusion',
        '2515-5172': 'Res.Notes AAS',
        '0026-1394': 'Metrologia'}
jnls['2516-1067'] = 'Plasma Res.Express'
jnls['2633-4356'] = 'Mat.Quant.Tech.'
if issn in jnls:
    jnl = jnls[issn]
elif re.search('\/book\/', issn):
    book = True
else:
    print('journal not known:', issn)
    sys.exit(0)




    
tocpages = []
j = 0
for starturl in starturls:
    j += 1
    #tocfile = '/tmp/iop_' + re.sub('\/', '_', re.sub('.*issue\/', '', starturl)) + '.toc'
    #if not os.path.isfile(tocfile):
    #    os.system('wget -q -T 300 -O %s "%s"' % (tocfile, starturl))
    #inf = open(tocfile, 'r')
    #tocpages.append(BeautifulSoup(''.join(inf.readlines())))
    driver.get(starturl)
    tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
    time.sleep(30)
    
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

recs = []
voliss = []
vols = []
j = 0
motherisbn = False
for tocpage in tocpages:
    j += 1
    print('---------{_} %i/%i {_}---------' % (j, len(tocpages)))
    issnote = False
    h3note = False
    h4note = False
    for div in tocpage.find_all('div', attrs = {'id' : 'wd-jnl-issue-title'}):
        for h4 in div.find_all('h4'):
            issnote = h4.text
    divs = tocpage.find_all('div', attrs = {'id' : 'wd-jnl-issue-art-list'})
    if not divs:
        divs = tocpage.find_all('div', attrs = {'class' : 'art-list'})
    if book:
        for meta in tocpage.find_all('meta', attrs = {'name' : 'citation_isbn'}):
            motherisbn = re.sub('\-', '', meta['content'])
    print(len(divs))
    if len(divs) == 0:
        print(tocpage.text)
    for div in divs:
        children = div.children
        (k, kmax) = (0, 0)
        for child in children:
            kmax += 1
        children = div.children
        for child in children:
            k += 1
            try:
                child.name
            except:
                continue
            print('      -{ %i/%i }-{ %s }-' % (k, kmax, child.name))
            if child.name == 'h3':
                h4note = False
                h3note = child.text
                print('===%s===' % (h3note))
            elif child.name == 'h4':
                h4note = child.text
                print('---%s---' % (h4note))
            elif child.name == 'div':
                if book:
                    for div2 in child.find_all('h2', attrs = {'class' : 'art-list-item-title'}):
                        linksoup = div2.find_all('a')
                else:
                    linksoup = child.find_all('a', attrs = {'class' : 'art-list-item-title'})
                for a in linksoup:
                    preface = False
                    time.sleep(20)
                    if book:
                        rec = {'jnl' : 'BOOK', 'note' : [], 'tc' : 'S', 'autaff' : [], 'refs' : []}
                        if motherisbn:
                            rec['motherisbn'] = motherisbn
                        if a['href'][-4:] == '.pdf':
                            print('  skip', a.text.strip())
                            continue
                    else:
                        rec = {'jnl' : jnl, 'note' : [], 'tc' : 'P', 'autaff' : [], 'refs' : []}
                    orcidsfound = False
                    if len(sys.argv) > 2:
                        rec['cnum'] = sys.argv[2]
                        rec['tc'] = 'C'
                    elif issn in ['1742-6596', '1757-899X']:
                        rec['tc'] = 'C'
                    elif issn in ['2515-5172']:
                        rec['tc'] = ''
                    if issnote: rec['note'].append(issnote)
                    if h3note: rec['note'].append(h3note)
                    if h4note: rec['note'].append(h4note)
                    artlink = 'http://iopscience.iop.org' + a['href']
                    print('     (%i) %s ' % (len(recs), artlink))
                    try:
                        driver.get(artlink)
                        artpage = BeautifulSoup(driver.page_source, features="lxml")
                    except:
                        print('try "%s" again after 1 minutes' % (artlink))
                        time.sleep(60)
                        driver.get(artlink)
                        artpage = BeautifulSoup(driver.page_source, features="lxml")
                    #roboter check
                    doimeta = artpage.find_all('meta', attrs = {'name' : 'citation_doi'})
                    if not doimeta:
                        print('\n !!! ROBO CHECK !!!\n')
                        print('try "%s" again after 5 minutes' % (artlink))
                        time.sleep(300)
                        driver.get(artlink)
                        artpage = BeautifulSoup(driver.page_source, features="lxml")
                    autaff = False
                    #licence
                    for divl in artpage.body.find_all('div', attrs = {'class' : 'col-no-break wd-jnl-art-license media'}):
                        for a in divl.find_all('a'):
                            if a.has_attr('href'):
                                if re.search('creativecommons.org', a['href']):
                                    rec['licence'] = {'url' : a['href']}       
                    #metadata
                    ejlmod3.metatagcheck(rec, artpage, ['citation_online_date', 'citation_issue', 'citation_doi',
                                                        'citation_author', 'citation_author_institution', 'citation_author_orcid',
                                                        'citation_author_email', 'citation_abstract'])
                    if not 'date' in rec:
                        ejlmod3.metatagcheck(rec, artpage, ['citation_publication_date'])
                    for meta in artpage.find_all('meta'):
                        if meta.has_attr('name'):
                            if meta['name'] == 'citation_title':
                                rec['tit'] = meta['content']
                                if re.search('^Preface ', meta['content']):
                                    preface = True
                            elif meta['name'] == 'citation_volume':
                                if issn in ['1674-1056', '0953-4075']:
                                    rec['vol'] = 'B' + meta['content']
                                elif issn == '1674-1137':
                                    rec['vol'] = 'C' + meta['content']
                                elif issn == '1751-8121':
                                    rec['vol'] = 'A' + meta['content']
                                elif issn == '0954-3899':
                                    rec['vol'] = 'G' + meta['content']
                                elif issn == '1361-6463':
                                    rec['vol'] = 'D' + meta['content']
                                else:
                                    rec['vol'] = meta['content']
                            elif meta['name'] == 'citation_firstpage':
                                rec['p1'] = meta['content']
                                if issn == '1748-0221' and rec['p1'][0] == 'C':
                                    rec['tc'] = 'C'
                    if preface:
                        continue
                    #JCAP
                    if issn == '1475-7516':
                        rec['vol'] = '%s%02i' % (rec['date'][2:4], int(rec['issue']))
                        del rec['issue']
                    if autaff:
                        rec['autaff'].append(autaff)
                    #authors if no ORCIDs in meta-section
                    if not orcidsfound or not rec['autaff']:
                        (auts, aff) = ([], [])
                        for authorsection in artpage.body.find_all('span'):
                            if authorsection.has_attr('data-authors'):
                                break
                        for span in authorsection.find_all('span', attrs = {'itemprop' : 'author'}):
                            orcid = False
                            affis = []
                            for sup in span.find_all('sup'):
                                affis = re.split(' *, *', sup.text)
                                sup.replace_with('')
                            author = re.sub('(.*) (.*)', r'\2, \1', span.text.strip())
                            for a in span.find_all('a'):
                                if a.has_attr('href') and re.search('orcid.org', a['href']):
                                    orcid = re.sub('.*orcid.org\/(\d.*[\dX])', r'\1', a['href'])
                            if orcid:
                                auts.append('%s, ORCID:%s' % (author, orcid))
                                orcidsfound = True
                            else:
                                auts.append(author)
                            for affi in affis:
                                auts.append('=Aff%s' % (affi))
                        for diva in artpage.body.find_all('div', attrs = {'class' : 'wd-jnl-art-author-affiliations'}):
                            for p in diva.find_all('p'):
                                for sup in p.find_all('sup'):
                                    affi = sup.text
                                    sup.replace_with('Aff%s= ' % (affi))
                                aff.append(p.text)
                        if len(auts) >= len(rec['autaff']):
                            del rec['autaff']
                            rec['auts'] = auts
                            rec['aff'] = aff
                    #abstract
                    for abstr in artpage.body.find_all('div', attrs = {'class' : 'article-text wd-jnl-art-abstract cf'}):
                        rec['abs'] = abstr.text.strip()
                    #keywords:
                    for divk in artpage.body.find_all('div', attrs = {'class' : 'wd-jnl-aas-keywords'}):
                        rec['keyw'] = []
                        for a in divk.find_all('a'):
                            rec['keyw'].append(a.text)
                    #get rid of footnotes
                    for ul in artpage.body.find_all('ul', attrs = {'class' : 'clear-list wd-content-footnotes'}):
                        ul.replace_with('')      
                    #references
                    for li in artpage.body.find_all('li', attrs = {'class' : 'indices-list'}):
                        for a in li.find_all('a',  attrs = {'class' : 'indices-id'}):
                            nummer = a.text
                            a.replace_with(nummer + ' ')
                        for a in li.find_all('a',  attrs = {'title' : 'CrossRef'}):
                            if a.has_attr('href'):
                                doi = regexpdxdoi.sub(', DOI: ', a['href'])
                                a.replace_with(doi)
                        for a in li.find_all('a',  attrs = {'title' : 'IOPScience'}):
                            if a.has_attr('href'):
                                doi = regexpiopurl.sub(', DOI: 10.1088/', a['href'])
                                a.replace_with(doi)
                        for a in li.find_all('a',  attrs = {'title' : 'IOPscience'}):
                            if a.has_attr('href'):
                                doi = regexpiopurl.sub(', DOI: 10.1088/', a['href'])
                                a.replace_with(doi)
                        for a in li.find_all('a'):
                            if re.search('Google.?Scholar', a.text) or re.search('ADS', a.text):
                                a.replace_with('')
                            elif a.has_attr('href'):
                                link = ', %s: %s' % (a.text, a['href'])
                                a.replace_with(link)
                        ref = li.text
                        if regexpdxdoi.search(ref):
                            ref = regexpdxdoi.sub('DOI: ', ref)
                        if regexpiopurl.search(ref):
                            ref = regexpiopurl.sub('DOI: 10.1088/', ref)
                        rec['refs'].append([('x', ref)])
                    print('  - ', rec['doi'], ' orcidfound:', orcidsfound)
                    print('    ', list(rec.keys()))
                    #print rec
                    if 'autaff' in rec:
                        if rec['autaff']:
                            recs.append(rec)
                    else:
                        if rec['auts']:
                            recs.append(rec)
    if not book:
        if 'issue' in list(rec.keys()):
            voliss.append('%s.%s' % (rec['vol'], rec['issue']))
        elif not rec['vol'] in voliss:
            voliss.append(rec['vol'])
        if not rec['vol'] in vols:
            vols.append(rec['vol'])

if book:
    iopf = 'iopcrawl.book.' + re.sub('\D', '', starturls[0])
else:
    if len(vols) == 1:
        iopf = 'iopcrawl.' + re.sub(' ', '', jnl) + re.sub('_\d+', '', '.' + '_'.join(voliss))
    else:
        iopf = 'iopcrawl.' + re.sub(' ', '', jnl) + '.' + '_'.join(voliss)
        

ejlmod3.writenewXML(recs, publisher, iopf, retfilename='retfiles_special')
