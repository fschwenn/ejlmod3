# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest Cambridge-journals
# FS 2015-02-12
# FS 2023-02-03

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse,http.cookiejar
import time
from bs4 import BeautifulSoup

publisher = 'Cambridge University Press'

tc = 'P'
jid =  sys.argv[1]
vol = sys.argv[2]
skipalreadyharvested = True

jnlfilename = 'cambridge'+jid + vol
if len(sys.argv) > 3:
    iss = sys.argv[3]
    jnlfilename += '.' + iss +  '_' + ejlmod3.stampoftoday()
else:
    jnlfilename += '.' + ejlmod3.stampoftoday()

if len(sys.argv) > 4:
    jnlfilename += '.' + sys.argv[4]
    tc = 'C'
if len(sys.argv) > 5:
    explicittoclink = sys.argv[5]

if jid == 'IAU':
    jnlname = 'IAU Symp.'
elif jid == 'PSP':
    jnlname = 'Math.Proc.Cambridge Phil.Soc.'
elif jid == 'FMS':
    jnlname = 'Forum Math.Sigma'
elif jid == 'LPB':
    jnlname = 'Laser Part.Beams'
elif jid == 'JAZ':
    jnlname = 'J.Austral.Math.Soc.'
elif jid == 'PAS':
    jnlname = 'Publ.Astron.Soc.Austral.'
elif jid == 'PLA':
    jnlname = 'J.Plasma Phys.'
elif jid == 'IJA':
    jnlname = 'Int.J.Astrobiol.'
    camjnlname = 'international-journal-of-astrobiology'
elif jid == 'GMJ':
    jnlname = 'Glasgow Math.J.'    
elif jid == 'BAZ':
    jnlname = 'Bull.Austral.Math.Soc.'
elif jid == 'COM':
    jnlname = 'Compos.Math.'
elif jid == 'FMP':
    jnlname = 'Forum Math.Pi'
elif jid == 'MTK':
    jnlname = 'Mathematika'
elif jid == 'JOG':
    jnlname = 'J.Glaciol.'
elif jid == 'CJM':
    jnlname = 'Can.J.Math.'
elif jid == 'SIC':
    jnlname = 'Sci.Context'
elif jid == 'JMJ':
    jnlname = 'J.Inst.Math.Jussieu'
    camjnlname = 'journal-of-the-institute-of-mathematics-of-jussieu'
elif jid == 'MAM':
    jnlname = 'Microscopy Microanal.'
elif jid == 'PHS':
    jnlname = 'Phil.Sci.'
    camjnlname = 'philosophy-of-science'
elif jid == 'JFM':
    jnlname = 'J.Fluid Mech.'
    camjnlname = 'journal-of-fluid-mechanics'
#Now at Global Science Press
#elif jid == 'CPH':
#    jnlname = 'Commun.Comput.Phys.'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename, years=7)

if jid in ['PHS', 'JFM', 'IJA', 'JMJ']:
    supertocurl = 'https://www.cambridge.org/core/journals/%s/all-issues' % (camjnlname)
    ejlmod3.printprogress('==', [[supertocurl]])
    supertocfilename = '/tmp/%s.toc' % (camjnlname)
    if not os.path.isfile(supertocfilename):
        os.system('wget -q -O %s %s' % (supertocfilename, supertocurl))
    tocf = open(supertocfilename, 'r')
    toc = BeautifulSoup(''.join(tocf.readlines()), features="lxml")
    tocf.close()
    for li in toc.body.find_all('li', attrs = {'class' : 'accordion-navigation'}):
        if jid in ['PHS', 'JMJ']:
            for a in li.find_all('a', attrs = {'class' : 'row'}):
                if a.has_attr('aria-label') and re.search('Volume '+vol, a['aria-label']):
                    print(a['aria-label'])
                    for li2 in li.find_all('li'):
                        aa = li2.find_all('a', attrs = {'class' : 'row'})
                        if len(aa) == 1:
                            for span in li2.find_all('span', attrs = {'class' : 'issue'}):
                                print(' ', span, aa[0]['href'])
                                if re.search('Issue '+iss, span.text):
                                    toclink = 'https://www.cambridge.org' + aa[0]['href']
        else:
            for a in li.find_all('a', attrs = {'class' : 'row'}):
                for span in a.find_all('span', attrs = {'class' : 'issue'}):
                    if re.search('Volume '+vol, span.text):
                        toclink = 'https://www.cambridge.org' + a['href']
            
else:
    if len(sys.argv) > 5:
        toclink = explicittoclink
    else:
        toclink = 'http://journals.cambridge.org/action/displayIssue?jid=%s&volumeId=%s' % (jid, vol)
        if len(sys.argv) > 3:
            toclink += '&issueId=%s' % (iss)

if len(sys.argv) > 3:
    ejlmod3.printprogress('#', [[jid, vol, iss], [toclink]])
else:
    ejlmod3.printprogress('#', [[jid, vol], [toclink]])

#toclink = "https://www.cambridge.org/core/journals/glasgow-mathematical-journal/issue/FF36FC6AD93313180F0F572188FA2F70"
        
if not os.path.isfile('/tmp/%s.0.toc' % (jnlfilename)):
    os.system('wget -q -O /tmp/%s.0.toc "%s"' % (jnlfilename, toclink))
tocf = open('/tmp/%s.0.toc' % (jnlfilename), 'r')
toc = BeautifulSoup(''.join(tocf.readlines()), features="lxml")
tocf.close()

#check number of toc-pages
for meta in toc.head.find_all('meta', attrs = {'property' : 'og:url'}):
    baseurl = 'https://www.cambridge.org' + re.sub('http.*?www.cambridge.org', '', meta['content'])
    numpages = 1
    for div in toc.body.find_all('div', attrs = {'class' : 'results'}):
        for p in div.find_all('p', attrs = {'class' : 'paragraph_05'}):
            ptext = p.text.strip()
            if re.search('age \d+ of \d+', ptext):
                numpages = int(re.sub('.* of (\d+).*', r'\1', ptext))
                print('check %i pages' % (numpages))

note = ''
prerecs = []
#first run through TOC to get DOIs
for i in range(numpages):
    toclink = '%s?pageNum=%i' % (baseurl, i+1)
    ejlmod3.printprogress('=', [[i+1, numpages], [toclink]])
    if not os.path.isfile('/tmp/%s.%i.toc' % (jnlfilename, i)):
        os.system('wget -q -O /tmp/%s.%i.toc "%s"' % (jnlfilename, i, toclink))
        time.sleep(3)
    tocf = open('/tmp/%s.%i.toc' % (jnlfilename, i), 'r')
    toc = BeautifulSoup(''.join(tocf.readlines()), features="lxml")
    tocf.close()
    for div in toc.body.find_all('div'):
        if div.has_attr('class') and 'columns' in div['class']:
            if 'large-12' in div['class'] and 'margin-top' in div['class']:
                for child in div.children:
                    rec = {'refs' : [], 'tc' : tc,
                           'autaff' : [], 'keyw' : [], 'jnl' : jnlname}
                    if len(sys.argv) > 3:
                        rec['issue'] = iss
                    try:
                        child.name
                    except:
                        continue
                    if child.name == 'h4':
                        note = child.text.strip()
                    elif child.name == 'div':
                        for a in child.find_all('a', attrs = {'class' : 'url doi'}):
                            rec['artlink2'] = a['href']
                            rec['note'] = [ note ]
                            rec['doi'] = re.sub('.*doi.org.', '', a['href'])
                            if rec['doi'] in ['10.4208/cicp.060515.161115b', 
                                              '10.1017/S0022377818000430',
                                              '10.1112/S0025579318000232',
                                              '10.1112/S0025579318000244',
                                              '10.1017/S1431927620001191',
                                              '10.1112/S0025579318000256']:
                                continue
                            if skipalreadyharvested and rec['doi'] in alreadyharvested:
                                print('   %s already in backup' % (rec['hdl']))
                            elif not note in ['Front Cover (OFC, IFC) and matter', 
                                        'Back Cover (OBC, IBC) and matter']:
                                prerecs.append(rec)
                                print(rec['doi'], rec['note'])
                        #real article link
                        for a2 in child.find_all('a', attrs = {'class' : 'part-link'}):
                            rec['artlink'] = 'https://www.cambridge.org' + a2['href']
                            if not 'doi' in list(rec.keys()):
                                rec['note'] = [ note ]
                                if not note in ['Front Cover (OFC, IFC) and matter', 
                                                'Back Cover (OBC, IBC) and matter',
                                                'PhD Abstract']:
                                    if skipalreadyharvested and rec['artlink'] in alreadyharvested:
                                        print('   %s already in backup' % (rec['artlink']))
                                    else:
                                        prerecs.append(rec)
                                        print('?', rec['note'])


#2nd run to get details for individual articles
reref = re.compile('^reference\-\d')
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
i = 0
recs = []
for rec in prerecs:    
    i += 1 
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(8)
    except:
        if 'artlink2' in list(rec.keys()):
            print('wait 3 minutes befor trying %s instead of %s' % (rec['artlink2'], rec['artlink']))
            time.sleep(180)
            req = urllib.request.Request(rec['artlink2'], headers=hdr)
        else:
            print('wait 3 minutes befor trying  again')
            time.sleep(180)
            req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_firstpage', 'citation_lastpage',
                                        'citation_doi', 'citation_author', 'citation_author_institution',
                                        'citation_author_email', 'citation_author_orcid',
                                        'citation_online_date', 'citation_keywords',
                                        'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if 'name' in meta.attrs:
            #pubnote
            if meta['name'] == 'citation_volume':
                if jid == 'IAU':
                    rec['vol'] = vol
                else:
                    rec['vol'] = meta['content']
            elif meta['name'] == 'citation_issue':
                if not jid == 'IAU':
                    rec['issue'] = meta['content']
            elif meta['name'] == 'citation_publication_date':
                rec['year'] = meta['content'][:4]
    #CNUM
    if len(sys.argv) > 4:
        rec['cnum'] = sys.argv[4]
    #article-ID
    if not 'p1' in list(rec.keys()):
        for dl in artpage.body.find_all('dl', attrs = {'class' : 'article-details'}):
            for div in dl.find_all('div', attrs = {'class' : 'content__journal'}):
                for span in div.find_all('span'):
                    rec['p1'] = re.sub('^ *,? *', '', span.text.strip())
    #articleID
    if 'p1' not in rec:
        for ul in artpage.body.find_all('ul', attrs = {'class' : 'title-volume-issue'}):
            for li in ul.find_all('li', attrs = {'class' : 'published'}):
                rec['p1'] = re.sub('.*, ', '', re.sub('\n', ' ', li.text.strip()))
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'abstract'}):
        for tit in div.find_all('title'):
            tit.replace_with('')
        rec['abs'] = div.text.strip()
        rec['abs'] = re.sub('[\n\t\r]', ' ', rec['abs'])
        rec['abs'] = re.sub('  +', ' ', rec['abs'])
    #references (only with DOI)
    for div in artpage.body.find_all('div', attrs = {'id' : 'references'}):
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'div':
                reference = child.text.strip()
            elif child.name == 'ul':
                for a in child.find_all('a'):
                    if a.text == 'CrossRef':
                        refdoi = re.sub('.*doi.org.', '', a['href'])
                        reference += ', DOI: ' + refdoi
            elif child.name == 'hr':
                rec['refs'].append([('x', reference)])
        #(new/other) references
        if not rec['refs']:
            for div2 in div.find_all('div', attrs = {'class' : 'ref'}):
                rec['refs'].append([('x', div2.text.strip())])
    if not rec['refs']:
        refdivs = []
        for div in artpage.body.find_all('div'):
            if div.has_attr('id') and reref.search(div['id']):
                refdivs.append(div)
        for div in refdivs:
            reference = ''
            refnum = re.sub('\D', '', div['id'])
            for a in div.find_all('a'):
                if a.text == 'CrossRef':
                    refdoi = re.sub('.*doi.org.', '', a['href'])
                    reference += ', DOI: ' + refdoi
                    a.decompose()
                elif a.text in ['Google Scholar', 'Pubmed']:
                    a.decompose()
            rec['refs'].append([('x', '[%s] %s%s' % (refnum, re.sub('\. *$', '', div.text.strip()), reference))])
    #licence
    for div in artpage.body.find_all('div', attrs = {'class' : 'description'}):
        for div2 in div.find_all('div', attrs = {'class' : 'margin-top'}):
            div2text = div2.text.strip()
            if re.search('creativecommons.org', div2text):
                rec['licence'] = {'url' : re.sub('.*(http.*?creativecommons.*?0).*', r'\1', div2text)}                
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
