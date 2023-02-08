# -*- coding: UTF-8 -*-
#program to harvest International Press Boston
# FS 2012-06-01
# FS 2023-02-07

import os
import ejlmod3
import re
import sys
import unicodedata
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup

publisher = 'International Press'
jnl = sys.argv[1]
vol = sys.argv[2]
isu = sys.argv[3]

jnlfilename = jnl+vol+'.'+isu

if   (jnl == 'atmp'): 
    jnlname = 'Adv.Theor.Math.Phys.'
    issn = '1095-0761'
    url = "http://www.intlpress.com/%s/%s-issue_%s_%s.php" % (jnl.upper(),jnl.upper(),vol,isu)
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
elif (jnl == 'amsa'):
    jnlname = 'Ann.Math.Sci.Appl.'
    issn = '2380-288X'
    url = "http://www.intlpress.com/%s/%s-vol-%s.php" % (jnl.upper(),jnl.upper(),vol)
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
elif (jnl == 'cntp'):
    jnlname = 'Commun.Num.Theor.Phys.'
    issn = '1931-4523'
    url = "http://www.intlpress.com/%s/%s-vol-%s.php" % (jnl.upper(),jnl.upper(),vol)
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
elif (jnl == 'ajm'):
    jnlname = 'Asian J.Math.'
    issn = '1093-6106'
    url = "http://www.intlpress.com/%s/%s-v%s.php" % (jnl.upper(),jnl.upper(),vol)
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
elif (jnl == 'jdg'):
    jnlname = 'J.Diff.Geom.'
    issn = '0022-040X'
    year = str(int(vol) / 3 + 1982)
    url = "http://www.intlpress.com/%s/%s/%s-v%s.php" % (jnl.upper(),year,jnl.upper(),vol)
elif (jnl == 'cag'):
    jnlname = 'Commun.Anal.Geom.'
    issn = '1019-8385'
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
elif (jnl == 'cjm'): #fall 2012
    jnlname = 'Cambridge J.Math.'
    issn = '2168-0930'
    url = "http://www.intlpress.com/%s/%s-v%s.php" % (jnl.upper(),jnl.upper(),vol)
elif (jnl == 'cms'):
    jnlname = 'Commun.Math.Sci.'
    issn = '1539-6746'
    year = str(int(vol)+2002)
    url = "http://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/00%s/000%s/index.php" % (jnl,vol,isu)
elif (jnl == 'jsg'):
    jnlname = 'J.Sympl.Geom.'
    issn = '1527-5256'
    url = "http://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/00%s/000%s/index.php" % (jnl,vol,isu)
elif (jnl == 'mrl'): # fulltext via http://www.intlpress.com/_newsite/site/pub/files/_fulltext/journals/mrl/
    jnlname = 'Math.Res.Lett.'
    issn = '1073-2780'
    url = "http://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/00%s/000%s/index.php" % (jnl,vol,isu)
elif (jnl == 'pamq'):
    jnlname = 'Pure Appl.Math.Quart.'
    issn = '1558-8599'
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
elif (jnl == 'iccm'):
    jnlname = 'ICCM Not.'
    issn = '2326-4810'
    url = 'https://www.intlpress.com/site/pub/pages/journals/items/%s/content/vols/%04i/%04i/index.php' % (jnl,int(vol),int(re.sub('\D.*', '', isu)))
if len(vol) == 1: vol = '0'+vol
#url = "http://intlpress.com/site/pub/pages/journals/items/%s/content/vols/00%s/000%s/body.html" % (jnl,vol,isu)


print("get table of content of %s%s.%s ..." %(jnlname,vol,isu))
print("lynx -source \"%s\"" % (url))
tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url), features="lxml")


recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'list_item'}):
    rec = {'vol' : vol, 'jnl' : jnlname, 'tc' : 'P', 'issue' : isu,
           'autaff' : [], 'note' : [], 'abs' : ''}
    for a in div.find_all('a'):
        rec['artlink'] = 'http://www.intlpress.com/' + a['href']
        print('.', rec['artlink'])
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_year',
                                            'citation_doi', 'citation_title', 'citation_author',
                                            'citation_author_institution', 'citation_author_email',
                                            'citation_pdf_url'])
        for p in artpage.body.find_all('p', attrs = {'class' : 'contentitem_abstract'}):
            rec['abs'] += p.text
        for p in artpage.body.find_all('p', attrs = {'class' : 'contentitem_keywords'}):
            rec['keyw'] = re.split(', ', p.text)
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
