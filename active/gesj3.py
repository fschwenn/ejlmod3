# -*- coding: utf-8 -*-
#program to harvest GESJ
# FS 2014-10-07
# FS 2022-12-02

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

#from removehtmlgesocks import removehtmlgesocks

def tfstrip(x): return x.strip()
tmpdir = '/tmp'
hdr = {'User-Agent' : 'Magic Browser'}

publisher = 'Internet Academy'
jnlid = sys.argv[1]
year = sys.argv[2]
issue = sys.argv[3]
month = sys.argv[4]
if jnlid == 'phys':
    jnl = 'GESJ Phys.'
elif jnlid == 'math':
    jnl = 'GESJ Math.Mech.'
elif jnlid == 'comp':
    jnl = 'GESJ Comp.Sci.Telecomm.'
jnlfilename = 'gesj%s%s.%s' % (jnlid, year, issue)

tocurl = 'https://www.gesj.internet-academy.org.ge/en/list_artic_en.php?b_sec=' + jnlid + '&issue=' + '%s-%02i' % (year, int(month))
tocfilename = '%s/%s.html' % (tmpdir, jnlfilename)

print(tocurl, '->', tocfilename)
if not os.path.isfile(tocfilename):
    os.system('wget -q -O %s "%s"' % (tocfilename, tocurl))
tocfil = open(tocfilename, 'r')

recs = []
toc = ''.join(map(tfstrip, tocfil.readlines()))
for record in  re.split('images.bul1.gif', toc)[1:]:
    record = re.sub('<hr.*', '', record)
    rec = {'jnl' : jnl, 'vol' : year, 'year' : year, 'issue' : issue, 'tc' : 'P'}
    #authors
    rec['autaff'] = []
    for author in re.split('<script>', re.sub('.*?<script>(.*)<table.*',r'\1',record)):
        authorname = re.sub('.*a title=.(.*?)".*', r'\1', author)
        rec['autaff'].append([re.sub('^(.*) (.*?)$', r'\2, \1', authorname)])
        #email-adress is not neccessarily that of the author :-(
        #authorlink = 'https://www.gesj.internet-academy.org.ge/en/' + re.sub('.*(v_au_info_en.*?)".*', r'\1', author)
        #print('        ', authorlink)
        #time.sleep(1)
        #req = urllib.request.Request(authorlink, headers=hdr)
        #autpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        #for a in autpage.find_all('a'):
        #    if a.has_attr('href') and re.search('mailto', a['href']):
        #        rec['autaff'][-1].append(re.sub('mailto:(.*)\?.*', 'EMAIL:', a['href']))
    #title
    title = re.sub('.*<strong>(.*?)</strong>.*spacer.gif.*',r'\1',record)
    if not re.search('[A-Z]', title):
        continue
    #rec['tit'] = title.encode('utf8')
    rec['tit'] = title
    #pages
    rest = re.sub('.*?spacer.gif', '', record)
    pages = re.sub('.*?<strong>(.*?)<\/strong>.*', r'\1', rest)
    [rec['p1'], rec['p2']] = re.split('\-', pages)
    #pdf
    rec['FFT'] = re.sub('.*<a href="(.*?)".*', r'\1', rest)
    rec['licence'] = {'url' : 'http://creativecommons.org/licenses/by/4.0/'}
    #abstract
    abstractlink = 'http://gesj.internet-academy.org.ge/en/'+re.sub('.*"(v_abstr.*issue.*?)".*', r'\1', rest)
    abstractfilename = '/tmp/%s%s.html' % (jnlfilename, rec['p1'])
    if not os.path.isfile(abstractfilename):
        os.system("wget -q -O %s '%s'" % (abstractfilename, abstractlink))
    absfil = open(abstractfilename, 'r')
    abstract = re.sub('<br *\/?>', '', ''.join(map(tfstrip, absfil.readlines())))
    rec['abs'] = re.sub('.*?<div class="indent">(.*?)<\/div>.*',  r'\1', abstract)
    ejlmod3.printrecsummary(rec)
    recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
