# -*- coding: UTF-8 -*-
#program to harvest journals of the Physical Society of Japan
# FS 2015-02-20
# FS 2023-02-02

import os
import ejlmod3
import re
import sys
import unicodedata
import string
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc


tmpdir = '/tmp'
def tfstrip(x): return x.strip()
jnl = sys.argv[1]
publisher = 'Physical Society of Japan'
urltrunc = 'https://journals.jps.jp'
if jnl == 'jpsj':
    jnlname = 'J.Phys.Soc.Jap.'
    vol = sys.argv[2]
    issue = sys.argv[3]
    year = sys.argv[4]
    jnlfilename = jnl+vol+'.'+issue
    toclink = '%s/toc/%s/%s/%s/%s' % (urltrunc, jnl, year, vol, issue)
    tc = 'P'
else:
    jnlname = 'JPS Conf.Proc.'
    volname = sys.argv[2]
    jnlfilename = 'jpsjcp.%s' % (volname)
    toclink = '%s/doi/book/10.7566/%s'  % (urltrunc, volname)
    tc = 'C'    

def fsunwrap(tag):
    try: 
        for b in tag.find_all('b'):
            cont = b.string
            b.replace_with(cont)
    except:
        print('fsunwrap-b-problem')
    try: 
        for sup in tag.find_all('sup'):
            cont = sup.string
            sup.replace_with('^'+cont)
    except:
        print('    fsunwrap-sup-problem')
    try: 
        for sub in tag.find_all('sub'):
            cont = sub.string
            sub.replace_with('_'+cont)
    except:
        print('    fsunwrap-sub-problem')
    try: 
        for i in tag.find_all('i'):
            cont = i.string
            i.replace_with('$' + cont + '$')
    except:
        print('    fsunwrap-i-problem')
    try: 
        for form in tag.find_all('formula',attrs={'formulatype': 'inline'}):
            form.replace_with(' [FORMULA] ')
    except:
        print('    fsunwrap-form-problem')
    return tag

#tocfile = '/tmp/%s.toc' % (jnlfilename)
#if not os.path.isfile(tocfile):
#    print(toclink)
#    os.system('wget -q -O %s "%s"' % (tocfile, toclink))
#inf = open(tocfile, 'r')
#toc = BeautifulSoup(''.join(inf.readlines()), features="lxml")
#inf.close()
options = uc.ChromeOptions()
options.add_argument('--headless')
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

print(toclink)
driver.get(toclink)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
time.sleep(3)

#check licence
licenseurl =False
for a in tocpage.body.find_all('a'):
    if a.has_attr('href') and re.search('creativecommons.org', a['href']):
        licenseurl = a['href']

recs = []
(noteA, noteB) = ('', '')
for tag in tocpage.body.find_all():
    if tag.name == 'h2' and tag.has_attr('class') and tag['class'] == ['header-bar', 'header-dark-gray', 'no-corner', 'clear', 'subject']:
        noteA = tag.text
        ejlmod3.printprogress('=', [[noteA]])
    if tag.name == 'h2' and tag.has_attr('class') and tag['class'] == ['title-group', 'level1']:
        noteB = tag.text
        ejlmod3.printprogress('+', [[noteB]])
    elif tag.name == 'div' and tag.has_attr('class') and tag['class'] == ['item', 'clearfix']:
        rec = {'jnl' : jnlname, 'tc' : tc, 'note' : [], 'auts' : [], 'aff' : [], 'refs' : []}
        if noteA != '':
            rec['note'].append(noteA)
            if re.search('^Condensed matter', noteA):
                rec['fc'] = 'f'
        if noteB != '': rec['note'].append(noteB)
        for span in tag.find_all('span', attrs = {'class' : 'hlFld-Title'}):
            rec['tit'] = span.text
        for inp in tag.find_all('input', attrs = {'name' : 'doi'}):
            rec['doi'] = inp['value']
            abslink = '%s/doi/abs/%s' % (urltrunc, rec['doi'])
            reflink = '%s/doi/ref/%s' % (urltrunc, rec['doi'])
            ejlmod3.printprogress('-', [[abslink], [len(recs)]])
            #pbn
            if jnl == 'jpsj':
                rec['vol'] = vol
                rec['issue'] = issue
                rec['year'] = year
            else:
                rec['vol'] = re.sub('.*\/.*?\.(\d+)\..*', r'\1', rec['doi'])
                if len(sys.argv) > 3:
                    rec['cnum'] = sys.argv[3]
                    if licenseurl:
                        rec['licence'] = {'url' : licenseurl}
                        rec['FFT'] = '%s/doi/pdf/%s' % (urltrunc, rec['doi'])
                    elif len(sys.argv) > 4:
                        rec['licence'] = {'statement' : sys.argv[4]}
                        rec['FFT'] = '%s/doi/pdf/%s' % (urltrunc, rec['doi'])
            rec['p1'] = re.sub('.*\.', '', rec['doi'])\
            #check abstract page
            #absfile = '/tmp/%s.abs' % (re.sub('\/', '_', rec['doi']))
            #if not os.path.isfile(absfile):
            #    time.sleep(23)
            #    os.system('wget -q -O %s "%s"' % (absfile, abslink))
            #    print('     wget', abslink)
            #inf = open(absfile, 'r')
            #abspage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
            #inf.close()
            driver.get(abslink)
            abspage = BeautifulSoup(driver.page_source, features='lxml')
            time.sleep(5)
            #abstract
            for div in abspage.body.find_all('div', attrs = {'class' : 'NLM_abstract'}):
                for p in div.find_all('p'):
                    rec['abs'] = fsunwrap(p).get_text()
            if 'abs' not in rec:
                for div in abspage.body.find_all('div', attrs = {'class' : 'abstractSection'}):
                    for p in div.find_all('p'):
                        rec['abs'] = fsunwrap(p).get_text()
            #pages
            for div in abspage.body.find_all('div', attrs = {'class' : 'chapterHeader'}):
                if re.search('\d page', div.text):
                    rec['pages'] = re.sub('.*\[(\d+) page.*',  r'\1', re.sub('[\r\n]', '', div.text))
                if jnlname == 'JPS Conf.Proc.':
                    rec['year'] = re.sub('.*\((\d\d\d\d)\).*',  r'\1', re.sub('[\r\n]', '', div.text))
            #authors
            for div in abspage.body.find_all('div', attrs = {'class' : 'authors'}):
                tempauts = []
                orciddict = {}
                i = 0 
                for tag in div.find_all():
                    if tag.name == 'a':
                        if tag.has_attr('class'):
                            if  tag['class'] == ['entryAuthor']:                                
                                i += 1
                                tempauts.append(re.sub('(.*) (.*)', r'\2, \1', tag.text.strip()))
                                author = tempauts[-1] + str(i)
                            elif tag['class'] == ['ref', 'aff']:
                                for sup in tag.find_all('sup'):
                                    tempauts.append('=Aff'+sup.text)
                        elif tag.has_attr('href'):
                            if re.search('orcid.org', tag['href']):
                                orcid = re.sub('.*orcid.org\/', ', ORCID:', tag['href'])                                
                                orciddict[author] = orcid
                i = 0
                for aut in tempauts:
                    if aut[:4] == '=Aff':
                        rec['auts'].append(aut)
                    else:
                        i += 1
                        author = aut + str(i)
                        if author in orciddict:
                            rec['auts'].append(aut + orciddict[author])
                        else:
                            rec['auts'].append(aut)
            #affiliations
            for span in abspage.body.find_all(attrs = {'class' : 'NLM_aff'}):
                for sup in span.find_all('sup'):
                    sup.replace_with('Aff'+sup.string+'= ')
                rec['aff'].append(span.text.strip())
            #licence
            for licence in abspage.body.find_all('license-p'):
                for a in licence.find_all('a'):
                    if re.search('Creative Commons', a.text):
                        rec['licence'] = {'url' : a['href']}
            if jnl == 'jpsjcp':
                rec['licence'] = {'url' : 'http://creativecommons.org/licenses/by/4.0/'}
                rec['FFT'] = '%s/doi/pdf/%s' % (urltrunc, rec['doi'])
            #references
            #if jnl == 'jpsj':
            if True:
                reffile = '/tmp/%s.ref' % (re.sub('\/', '_', rec['doi']))
                #if not os.path.isfile(reffile):
                #    time.sleep(23)
                #    os.system('wget -q -O %s "%s"' % (reffile, reflink))
                #    print('     wget', reflink)
                #inf = open(reffile, 'r')
                #ref = BeautifulSoup(''.join(inf.readlines()), features="lxml")
                #inf.close()
                ejlmod3.printprogress(' ', [[reflink]])
                driver.get(reflink)
                ref = BeautifulSoup(driver.page_source, features="lxml")
                time.sleep(5)
                for li in ref.find_all('li'):                
                    if li.has_attr('id'):
                        iref = [('o', li['id'])]
                        for script in li.find_all('script', attrs = {'type' : 'text/javascript'}):
                            #javascript = re.split(',', script.text.strip())
                            #if javascript[0] == 'genRefLink(16':
                            #    idoi = re.sub('.*?(10\..*?)\'.*', r'\1', javascript[2])
                            #    idoi = re.sub('%2F', '/', idoi)
                            #    iref.append(('a', idoi))
                            script.replace_with('')
                        if len(iref) == 1:
                            iref= [('x', li.text.strip())]
                        rec['refs'].append(iref)
            else:
                rec['FFT'] = '%s/doi/pdf/%s' % (urltrunc, rec['doi'])
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
