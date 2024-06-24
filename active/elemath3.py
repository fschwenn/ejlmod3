# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest journals
# FS 2022-08-30

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
from sys import argv
import os
import ejlmod3
import re

publisher = 'Element d.o.o. publishing house'
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year()),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=2))]

years = 2+8
jnls = {'oam' : {'fullname' : 'Operators and Matrices',
                 'shortname' : 'Oper.Matr.',
                 'harvest' : False},
        'mia' : {'fullname' : 'Mathematical Inequalities & Applications',
                 'shortname' : 'Math.Ineq.Appl.',
                 'harvest' : True},
        'jca' : {'fullname' : 'Journal of Classical Analysis',
                 'shortname' : 'J.Class.Anal.',
                 'harvest' : True},
        'jmi' : {'fullname' : 'Journal of Mathematical Inequalities',
                 'shortname' : 'J.Math.Ineq.',
                 'harvest' : True},
        'dea' : {'fullname' : 'Differential Equations & Applications',
                 'shortname' : 'Diff.Eq.Appl.',
                 'harvest' : True},
        'fdc' : {'fullname' : 'Fractional Differential Calculus',
                 'shortname' : 'Fract.Diff.Calc.',
                 'harvest' : True}}

done = []
reelemath = re.compile('.*ele\-math_([a-z]{3})_(\d+)\.(\d+).doki')
for ejldir in ejldirs:
    for datei in os.listdir(ejldir):
        if reelemath.search(datei):
            tocurl = reelemath.sub(r'http://\1.ele-math.com/volume/\2/issue/\3', datei)
            done.append(tocurl)
print('%i ele-math dokis in backup' % (len(done)))

reabs = re.compile('^Abstract\. *')
remsc = re.compile('^Mathematics subject classification')
reref = re.compile('^REFERENCES')
renum = re.compile('^\[')
repap = re.compile('^Paper [A-Za-z0-9\-]+$')
redeliss = re.compile('(\d) (\(\d{1,2}\)) (\([12]\d\d\d)')
def getissue(jid, vol, year, tocurl, soup):
    iss = re.sub('.*\/', '', tocurl)
    jnlfilename = 'ele-math_%s_%s.%s' % (jid, vol, iss)
    recs = []
    for tbody in soup.find_all('tbody'):
        trs = tbody.find_all('tr')
        k = 0
        for tr in trs:
            k += 1
            rec = {'jnl' : jnls[jid]['shortname'], 'vol' : vol, 'issue' : iss, 'year' : year,
                   'tc' : 'P', 'keyw' : [], 'refs' : [], 'fc' : 'm'}
            ejlmod3.printprogress('-', [[jnlfilename], [k, len(trs)]])
            #title and DOI
            for span in tr.find_all('span', attrs = {'class' : 'title'}):
                for a in span.find_all('a'):
                    rec['tit'] = a.text.strip()
                    rec['artlink'] = a['href']
                    rec['doi'] = re.sub('.*?(10\..*)', r'\1', a['href'])
            #keywords
            try:
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
            except:
                print('   wait 30s...')
                time.sleep(30)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
            for div in artpage.find_all('div', attrs = {'id' : 'keywords'}):
                for li in div.find_all('li'):
                    rec['keyw'].append(li.text.strip())
            #PDF
            for ul in artpage.find_all('ul', attrs = {'class' : 'file-links'}):
                for a in ul.find_all('a'):
                    for img in a.find_all('img', attrs = {'title' : 'View full article in PDF'}):
                        rec['FFT'] = a['href']
            #authors
            for span in tr.find_all('span', attrs = {'class' : 'authors'}):
                rec['auts'] = []
                for a in span.find_all('a'):
                    rec['auts'].append(a.text)
            #pages
            for td in tr.find_all('td', attrs = {'class' : 'page'}):
                rec['p1'] = re.sub('\D.*', '', td.text.strip())
                rec['p2'] = re.sub('.*\D', '', td.text.strip())
            #abstract and references from short-PDF
            for td in tr.find_all('td', attrs = {'class' : 'abstract'}):
                for a in td.find_all('a'):
                    pdffilename = '/tmp/%s.abs.pdf' % (re.sub('\W', '', rec['doi']))
                    if pdffilename == '/tmp/httpelemathcomstaticimgmia194003png.abs.pdf':
                        continue
                    if not os.path.isfile(pdffilename):
                        print('      downloading %s...' % (pdffilename))
                        os.system('wget -T 300 -t 3 -q -O %s %s' % (pdffilename, a['href']))
                        time.sleep(5)
                    txtfilename = '/tmp/%s.abs.txt' % (re.sub('\W', '', rec['doi']))
                    if not os.path.isfile(txtfilename):
                        os.system('pdftotext %s %s' % (pdffilename, txtfilename))
                    print('      reading %s...' % (txtfilename))
                    inf = open(txtfilename, 'r')
                    abstract = 'notyet'
                    references = 'notyet'
                    refs = []
                    for line in inf.readlines():
                        if abstract == 'notyet':
                            if reabs.search(line):
                                rec['abs'] = reabs.sub('', line.strip())
                                abstract = 'active'
                        elif abstract == 'active':
                            if remsc.search(line):
                                abstract = 'done'
                            else:
                                rec['abs'] += ' ' + line.strip()
                        elif abstract == 'done' and references != 'done':
                            if references == 'notyet':
                                if reref.search(line):
                                    references = 'active'
                            elif references == 'active':
                                lt = line.strip()
                                #print(lt)
                                if lt in ['', 'c', ', Zagreb']:
                                    pass
                                elif lt == jnls[jid]['fullname']:
                                    references = done
                                elif repap.search(lt):
                                    pass
                                elif renum.search(lt):
                                    refs.append(lt)
                                elif refs:
                                    refs[-1] += ' '+lt
                    for r in refs:
                        rec['refs'].append([('x', redeliss.sub(r'\1 \2', r))])
                    inf.close()
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
            time.sleep(3)
    ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
    return

i = 0
for jid in jnls:
    i += 1
    jnlurl = 'http://%s.ele-math.com/' % (jid)
    ejlmod3.printprogress('===', [[i, len(jnls)], [jnls[jid]['fullname']], [jnlurl]])
    if jnls[jid]['harvest']:
        harvest = True
        try:
            jnlpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(jnlurl), features="lxml")
        except:
            print('   wait 30s...')
            time.sleep(30)
            jnlpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(jnlurl), features="lxml")
        time.sleep(20)
        vols = []
        for li in jnlpage.find_all('li', attrs = {'class' : 'volume'}):
            for a in li.find_all('a'):
                if a.has_attr('href') and re.search('volume', a['href']):
                    volurl = 'http://%s.ele-math.com/%s' % (jid, a['href'])
                    vol = re.sub('\D', '', a['href'])
                    vols.append((1/int(vol), vol, volurl))
        vols.sort()
        j = 0
        for (volsort, vol, volurl) in vols:
            j += 1
            if harvest:
                ejlmod3.printprogress('=', [[i, len(jnls)], [jnls[jid]['shortname']], [j, len(vols)], [volurl]])
                try:
                    volpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(volurl), features="lxml")
                    time.sleep(years*10)
                except:
                    print('   wait 30s...')
                    time.sleep(30)
                    volpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(volurl), features="lxml")
                for div in volpage('div', attrs = {'id' : 'content'}):
                    for child in div.children:
                        try:
                            cn = child.name
                        except:
                            continue
                        if cn == 'p':
                            if re.search('Year: [12]\d\d\d', child.text):
                                year = re.sub('.*Year: ([12]\d\d\d).*', r'\1', child.text)
                                if int(year) <= ejlmod3.year(backwards=years):
                                    harvest = False
                                    break
                        elif cn == 'div' and child.has_attr('class'):
                            if 'issue-header' in child['class']:
                                for a in child.find_all('a'):
                                    tocurl = 'http://%s.ele-math.com/%s' % (jid, a['href'])
                            elif 'volume-table' in child['class']:
                                if harvest and not tocurl in done:
                                    getissue(jid, vol, year, tocurl, child)

