# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest De Gruyter journals
# FS 2016-01-04
# FS 2022-09-16

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup


urltrunc = 'https://www.degruyter.com'
publisher = 'De Gruyter'
skipalreadyharvested = True


journal = sys.argv[1]
year = sys.argv[2]
vol = sys.argv[3]
iss = sys.argv[4]



reemail = re.compile('(.*); ([^@]+@[^@]+\.[a-zA-Z]+) *$')
rebreaks = re.compile('[\n\t\r]')
jnlfilename = 'dg%s.%s.%s_%s' %  (journal, vol, iss, ejlmod3.stampoftoday())
if journal == 'phys':
    if int(vol) <= 12:
        jnl = 'Central Eur.J.Phys.'
    else:        
        jnl = 'Open Phys.'
elif journal == 'ract':
    jnl = 'Radiochim.Acta'
elif journal == 'astro':
    jnl = 'Open Astron.'
elif journal == 'ijnsns':
    jnl = 'Int.J.Nonlin.Sci.Numer.Simul.'
elif journal == 'kern':
    jnl = 'Kerntech.'
elif journal == 'crll':
    jnl = 'J.Reine Angew.Math.'
elif journal == 'agms':
    jnl = 'Anal.Geom.Metr.Spaces'
elif journal == 'cmam':
    jnl = 'Comp.Meth.Appl.Math.'
elif journal == 'zna':
    jnl = 'Z.Naturforsch.A'
elif journal == 'nanoph':
    jnl = 'Nanophoton.'
elif journal == 'bams':
    jnl = 'Bio-Alg.Med-Syst.'
elif journal == 'form':
    jnl = 'Forum Math.'
elif journal == 'jnet':
    jnl = 'J.Nonequil.Thermo.'
elif journal == 'coma':
    jnl = 'Compl.Manif.'
elif journal == 'qmetro':
    jnl = 'Quantum Meas.Quantum Metrol.'  
elif journal == 'ms':
    jnl = 'Math.Slovaca'
tc = 'P'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

    
#get list of volumes
if journal in ['kern', 'ract', 'phys', 'astro', 'crll', 'agms', 'cmam'] + ['zna', 'nanoph', 'bams', 'form', 'jnet', 'coma', 'qmetro', 'ms']:
    tocurl = 'https://www.degruyter.com/journal/key/%s/%s/%s/html' % (journal.upper(), vol, iss)
else:
    tocurl = "%s/view/j/%s.%s.%s.issue-%s/issue-files/%s.%s.%s.issue-%s.xml" % (urltrunc, journal, year, vol, iss, journal, year, vol, iss)        
print(tocurl)

tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

for h1 in tocpage.find_all('h1'):
    h1t = h1.text.strip()
    if re.search('(Proceedins|Conference|Workshop)', h1t):
        tc = 'C'

#get volumes
recs = []
i = 0
#for h4 in tocpage.find_all('h4'):
titledivs = tocpage.find_all('div', attrs = {'class' : 'resultTitle'})
for div in titledivs:
    for a in div.find_all('a'):        
        if a.has_attr('href'):
            i += 1
            vollink = 'https://www.degruyter.com' + a['href']
            ejlmod3.printprogress('-', [[i, len(titledivs)], [vollink]])
            if re.search('doi\/10', vollink):                
                doi = re.sub('.*doi\/(10.*)\/html', r'\1', vollink)
                if skipalreadyharvested and doi in alreadyharvested:
                    print('   already in backup')
                    continue
            rec = {'tc' : tc, 'jnl' : jnl, 'year' : year, 'vol' : vol, 'issue' : iss, 'autaff' : [],
                   'auts' : [], 'aff' : [], 'keyw' : [], 'pacs' : []}
            #conference
            if tc == 'C':
                rec['note'] = [h1t]
            #title
            rec['tit'] = a.text.strip()
            if rec['tit'] in ['Frontmatter', 'Backmatter', 'Contents', 'Editorial']:
                continue
            #get details
            if not os.path.isfile('/tmp/dg%s.%i' % (jnlfilename, i)):
                time.sleep(7)
                os.system('wget -T 300 -t 3 -q -U "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0"  -O /tmp/dg%s.%i %s' % (jnlfilename, i, vollink))
                time.sleep(0.1)
            if int(os.path.getsize('/tmp/dg%s.%i' % (jnlfilename, i))) == 0:
                print('  download again')
                time.sleep(15)
                os.system('rm /tmp/dg%s.%i' % (jnlfilename, i))
                time.sleep(.2)
                os.system('wget -T 300 -t 3 -q -U "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0"  -O /tmp/dg%s.%i %s' % (jnlfilename, i, vollink))                
                
                   
                       
            inf = open('/tmp/dg%s.%i' % (jnlfilename, i), 'r')
            artpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
            inf.close()
            ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_doi'])
            for meta in  artpage.find_all('meta'):
                if meta.has_attr('name'):
                    #keywords
                    if meta['name'] == 'citation_keywords':
                        if re.search('^\d\d\.\d\d...$', meta['content']):
                            rec['pacs'].append(meta['content'])
                        else:
                            rec['keyw'] += re.split('; ', meta['content'])
                elif meta.has_attr('property'):
                    #abstract
                    if meta['property'] == 'og:description':
                        rec['abs'] = meta['content']
            #abstract
            divs  = artpage.find_all('div', attrs = {'class' : 'articleBody_abstract'})
            if not divs:
                divs = artpage.find_all('section', attrs = {'class' : 'abstract'})
            for div in divs:
                for p in div.find_all('p'):
                    rec['abs'] = p.text.strip()
            #affiliations
            for div in artpage.find_all('div', attrs = {'class' : 'NLM_affiliations'}):                
                for p in div.find_all('p'):
                    for sup in p.find_all('sup'):
                        cont = sup.text
                        sup.replace_with('Aff%s= ' % (cont))
                    rec['aff'].append(p.text.strip())
            if not rec['aff']:
                for ul in artpage.find_all('ul', attrs = {'class' : 'affiliation-list'}):
                    for li in ul.find_all('li'):
                        for sup in li.find_all('sup'):
                            cont = sup.text
                            sup.replace_with('Aff%s= ' % (cont))
                        rec['aff'].append(li.text.strip())
                    ul.decompose()
            #authors
            divs = artpage.find_all('div', attrs = {'class' : 'contributors'})
            if not divs:
                divs = artpage.find_all('div', attrs = {'class' : 'component-content-contributors'})
            for div in divs:
                for span in div.find_all('span'):
                    if span.text.strip() in [',', ', and']:
                        span.replace_with(' / ')
                    elif re.search('^,.*and$', span.text.strip()):
                        span.replace_with(' / ')
                for sup in div.find_all('sup'):
                    for a in sup.find_all('a'):
                        cont = a.text.strip()
                        a.replace_with(' / =Aff%s ' % (cont))
                for aut in re.split(' +\/ +', rebreaks.sub(' ', div.text)):
                    if re.search('=Aff', aut):
                        rec['auts'].append(aut)
                    else:
                        rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', aut))
            if not divs:
                divs = artpage.find_all('div', attrs = {'class' : 'contributors-AUTHOR mb-2'})
                del rec['auts']
                del rec['aff']
                for div in divs:
                    for span in div.find_all('span'):
                        if span.has_attr('class'):
                            if 'contributor' in span['class']:
                                rec['autaff'].append([span.text])
                                if span.has_attr('title'):
                                    aff = span['title']
                                    if reemail.search(aff):
                                        email = reemail.sub(r'EMAIL:\2', aff)
                                        realaff = reemail.sub(r'\1', aff)
                                        rec['autaff'][-1].append(email)
                                        rec['autaff'][-1].append(realaff)
                                    else:
                                        rec['autaff'][-1].append(aff)
                            elif 'orcidLink' in span['class']:
                                for a in span.find_all('a'):
                                    rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            if not 'auts' in rec and not rec['autaff']:
                for ct in artpage.find_all('contributor-popdown'):
                    rec['autaff'].append([ct['name']])
                    if ct.has_attr('orcid') and ct['orcid']:
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', ct['orcid']))
                    elif ct.has_attr('email') and ct['email']:
                        rec['autaff'][-1].append('EMAIL:' + ct['email'])
                    if ct.has_attr('affiliations'):
                        rec['autaff'][-1].append(ct['affiliations'])
            #keywords / PACS
            for p in artpage.find_all('p', attrs = {'class' : 'articleBody_keywords'}):
                for span in p.find_all('span'):
                    if re.search('PACS', span.text):
                        key = 'pacs'                        
                    else:
                        key = 'keyw'
                    rec[key] = []
                for a in p.find_all('a'):
                    if a.text and not a.text in rec[key]:
                        rec[key].append(a.text)
            for div in artpage.find_all('div', attrs = {'class' : 'keywords'}):
                divt = div.text.strip()
                if divt[:5] == 'PACS:':
                    key = 'pacs'
                elif divt[:9] == 'Keywords:':
                    key = 'keyw'
                else:
                    key = 'note'
                if not key in rec:
                    rec[key] = []
                for a in div.find_all('a'):
                    rec[key].append(a.text.strip())
            #keywords
            for div in artpage.find_all('div', attrs = {'class' : 'column'}):
                for dl in div.find_all('dl'):
                    for dt in dl.find_all('dt'):
                        if re.search('Keywords', dt.text):
                            for dd in dl.find_all('dd'):
                                for a in dd.find_all('a'):
                                    rec['keyw'].append(a.text.strip())
            #references
            referencesection = artpage.find_all('div', attrs = {'class' : 'moduleDetail refList'})
            if not referencesection:
                referencesection = artpage.find_all('ul', attrs = {'class' : 'simple'})
            if not referencesection:
                referencesection = artpage.find_all('ul', attrs = {'class' : 'List'})
            for div in referencesection:
                rec['refs'] = []
                for li in div.find_all('li'):
                    for a in li.find_all('a'):
                        if a.has_attr('href'):
                            if re.search('doi.org', a['href']):
                                doi = re.sub('.*doi.org.', '', a['href'])
                                a.replace_with(', DOI: %s  ' % (doi))
                            elif re.search('google.com', a['href']):
                                a.replace_with('')
                    rec['refs'].append([('x', rebreaks.sub(' ', li.text.strip()))])
            if not 'refs' in list(rec.keys()):
                for span in artpage.find_all('span', attrs = {'class' : 'ref-list'}):
                    rec['refs'] = []
                    for p in span.find_all('p', attrs = {'class' : 'reference'}):
                        for a in p.find_all('a'):
                            if a.text.strip() == 'Search in Google Scholar':
                                a.decompose()
                            elif re.search('doi.org', a['href']):
                                doi = re.sub('.*doi.org.', '', a['href'])
                                a.replace_with(', DOI: %s  ' % (doi))
                        rec['refs'].append([('x', rebreaks.sub(' ', re.sub(';', ',', p.text)))])
            #date
            for div in artpage.find_all('div', attrs = {'class' : 'pubHistory'}):
                for dl in div.find_all('dl', attrs = {'id' : 'date-epub'}):
                    for dd in dl.find_all('dd', attrs = {'class' : 'fieldValue'}):
                        rec['date'] = dd.text
            for span in artpage.find_all('span', attrs = {'class' : 'publicationDate'}):
                rec['date'] = span.text
            #licence
            for div in artpage.find_all('div', attrs = {'class' : 'permissions'}):
                for a in div.find_all('a'):
                    rec['licence'] = {'url' : a['href']}
                    #fulltext pdf
                    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
                        rec['FFT'] = meta['content']
            if 'licence' not in rec:
                for a in  artpage.find_all('a', attrs = {'class' : ['ccLink', 'creative-commons-license']}):
                    rec['licence'] = {'url' : a['href']}
                    #fulltext pdf
                    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
                        rec['FFT'] = meta['content']
            if 'licence' not in rec:
                for span in artpage.find_all('span', attrs = {'class' : 'accessAccessible'}):
                    if re.search('Publicly Available', span.text):
                        for a in artpage.find_all('a', attrs = {'class' : 'downloadCompletePdfArticle'}):
                            rec['hidden'] = 'https://www.degruyter.com' + a['href']
            #pages 
            if 'p1' not in rec:
                for div in artpage.find_all('div', attrs = {'class' : 'citationInfo'}):
                    pages = re.sub('.*Volume \d*(.*)DOI:.*', r'\1', div.text.strip())
                    if re.search('[pP]ages \d+\D\d+', pages):
                        rec['p1'] = re.sub('.*[pP]ages (\d+).*', r'\1', pages)
                        rec['p2'] = re.sub('.*[pP]ages \d+\D(\d+).*', r'\1', pages)
            if 'p1' not in rec:
                for div in artpage.find_all('div', attrs = {'id' : 'citationContent'}):
                    for div2 in div.find_all('div', attrs = {'id' : 'MLA'}):
                        dt = div2.text.strip()
                        if re.search('pp\. \d+', dt):
                            rec['p1'] = re.sub('.*pp\. (\d+).*', r'\1', dt)
            #authors
            if not rec['autaff']:
                if not 'aff' in list(rec.keys()) or not arec['aff']:
                    if 'auts' in list(rec.keys()):
                        print('   DEL AUTS')
                        del rec['auts']
                    for span in artpage.find_all('span', attrs = {'class' : 'contrib'}):
                        (affs, email) = ([], '')
                        for a in span.find_all('a', attrs = {'class' : 'contrib-corresp'}):
                            email = re.sub('mailto.(.*?)\?.*', r'\1', a['href'])
                        for li in span.find_all('li'):
                            if not re.search('(De Gruyter Online|Other articles by this author|Email)', li.text):
                                aff = re.sub('Corresponding author', '', li.text.strip())
                                if aff:
                                    affs.append(aff)
                            li.replace_with('')
                        if email:
                            rec['autaff'].append([span.text.strip(), ' and '.join(affs), 'EMAIL:'+email])
                        else:
                            rec['autaff'].append([span.text.strip(), ' and '.join(affs)])
            if skipalreadyharvested and rec['doi'] in alreadyharvested:
                print('   already in backup')
            else:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
