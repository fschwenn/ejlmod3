# -*- coding: UTF-8 -*-
#program to harvest Project Euclid journals
# FS 2015-01-26
# FS 2023-02-25

import os
import ejlmod3
import re
import sys
import unicodedata
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup



lastyear = ejlmod3.year(backwards=1)
llastyear = ejlmod3.year(backwards=2)
skipalreadyharvested = True


ejldir = '/afs/desy.de/user/l/library/dok/ejl'

volumestodo = 5
journals = {#'aaa'   : ('Abstr.Appl.Anal. ', 'Hindawi'),
            'aihp'  : ('Ann.Inst.H.Poincare Probab.Statist.', 'Institut Henri Poincare',
                       'annales-de-linstitut-henri-poincare-probabilites-et-statistiques'),
            #'ajm'   : ('Asian J.Math.', 'International Press', 'asian-journal-of-mathematics'),
            'aop'   : ('Annals Probab.', 'The Institute of Mathematical Statistics', 'annals-of-probability'),          
            #'atmp'  : ('Adv.Theor.Math.Phys.', 'International Press'),
            'ba'    : ('Bayesian Anal.', 'International Society for Bayesian Analysis', 'bayesian-analysis'),
            'bjps'  : ('Braz.J.Probab.Statist.', 'Brazilian Statistical Association', 'brazilian-journal-of-probability-and-statistics'),
            #'cdm'   : ('Curr.Dev.Math.', 'International Press'),
            'dmj'   : ('Duke Math.J.', 'Duke University Press', 'duke-mathematical-journal'),
            'hokmj' : ('Hokkaido Math.J.', 'Hokkaido University, Department of Mathematics', 'hokkaido-mathematical-journal'),
            #'jam'   : ('J.Appl.Math.', 'Hindawi', 'journal-of-applied-mathematics'),
            'jdg'   : ('J.Diff.Geom.', 'Lehigh University', 'journal-of-differential-geometry'),
            'jgsp' : ('J.Geom.Symmetry Phys.', 'Bulgarian Academy of Sciences', 'journal-of-geometry-and-symmetry-in-physics'),
            'jmsj'  : ('J.Math.Soc.Jap.', 'Mathematical Society of Japan', 'journal-of-the-mathematical-society-of-japan'),
            #'jpm'   : ('J.Phys.Math.', 'OMICS International', 'journal-of-physical-mathematics'),
            #'maa'   : ('Methods Appl.Anal.', 'International Press'),
            'ps'    : ('Probab.Surv.', 'The Institute of Mathematical Statistics and the Bernoulli Society',
                       'probability-surveys'),
            'tjm'   : ('Tokyo J.Math.', 'Publication Committee for the Tokyo Journal of Mathematics',
                       'tokyo-journal-of-mathematics'),
            'facm'  : ('Funct.Approx.Comment.Math.', 'Adam Mickiewicz University, Faculty of Mathematics and Computer Science',
                       'functiones-et-approximatio-commentarii-mathematici'),
            'pgiq'  : ('Proc.Geom.Int.Quant.', 'Institute of Biophysics and Biomedical Engineering, Bulgarian Academy of Sciences',
                       'geometry-integrability-and-quantization')}

#journals = {'jgsp' : ('J.Geom.Symmetry Phys.', 'Bulgarian Academy of Sciences')}

jnl = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]

def tryeucllidnumber(rec):
    if 'doi' in list(rec.keys()):
        if re.search('^10.(4310|1214|14492|2969|3836|7169)\/[a-z]+\/\d+', rec['doi']):
            euclid = re.sub('^10.\d+\/([a-z]+)\/(\d+)', r'euclid.\1/\2', rec['doi'])
            try:
                euclidpage = BeautifulSoup(urllib.request.urlopen('http://projecteuclid.org/' + euclid), features="lxml")
            except:
                print('?', 'http://projecteuclid.org/' + euclid)
                return
            for meta in euclidpage.head.find_all('meta', attrs = {'name' : 'citation_doi'}):
                if meta['content'] == rec['doi']:
                    rec['MARC'] = [ ('035', [('9', 'EUCLID'), ('a', euclid)]) ]
                    print('   ->', euclid)          
    return 

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('projecteuclid')

prerecs = []
if jnl in list(journals.keys()):
    publisher = journals[jnl][1]
    jnlname = journals[jnl][0]
    jnlfilename = 'projecteuclid_%s%s.%s_%s' % (jnl, vol, iss, ejlmod3.stampoftoday())
    tocurl = 'https://projecteuclid.org/journals/%s/volume-%s/issue-%s' % (journals[jnl][2], vol, iss)
    #tocurl = 'https://projecteuclid.org/proceedings/geometry-integrability-and-quantization/Proceedings-of-the-Twenty-Second-International-Conference-on-Geometry-Integrability/toc/10.7546/giq-22-2021' #C20-06-08.6
    print('={ %s }={ %s }=' % (jnlname, tocurl))
    page = BeautifulSoup(urllib.request.urlopen(tocurl), features="lxml")
    for div in page.body.find_all('div', attrs = {'class' : 'TOCLineItemRow1'}):
        for div2 in div.find_all('div', attrs = {'class' : 'row'}):
            for a in div2.find_all('a'):
                for span in a.find_all('span', attrs = {'class' : 'TOCLineItemText1'}):
                    rec = {'jnl' : jnlname, 'auts' : [], 'tc' : 'P', 'vol' : vol, 'note' : []}
                    if (jnl == 'pgiq'):
                        rec['tc'] = 'C'
                        if len(sys.argv) > 4:
                            rec['cnum'] = sys.argv[4]
                    if iss != 'none':
                        rec['issue'] = iss
                    rec['artlink'] = 'https://projecteuclid.org' + a['href']
                    rec['tit'] = span.text.strip()
                    if not rec['tit'] in ['Editorial Board', 'Table of Contents',
                                          'Front Matter', 'Back Matter', 'Preface']:
                        prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']), features="lxml")
        time.sleep(2)
    except:
        print("retry '%s' in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['dc.Date', 'citation_year', 'citation_firstpage', 'citation_lastpage',
                                        'citation_author', 'citation_abstract' , 'citation_title',
                                        'citation_keywords', 'citation_pdf_url', 'dc.Language'])
    #DOI
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_doi'}):
        if re.search('^10\.\d+\/', meta['content']):
            rec['doi'] = meta['content']
        elif re.search('^[a-z]+\/\d+$', meta['content']):
            rec['MARC'] = [ ('035', [('9', 'EUCLID'), ('a', 'euclid.' + meta['content'])]) ]
            rec['doi'] = '20.2000/ProjectEuclid/' + meta['content']
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #references
    refurl = rec['artlink'] + '?tab=ArticleLinkReference'
    try:
        refpage = BeautifulSoup(urllib.request.urlopen(refurl), features="lxml")
    except:
        print("retry '%s' in 18 seconds" % (refurl))
        time.sleep(18)
        try:
            refpage = BeautifulSoup(urllib.request.urlopen(refurl), features="lxml")
        except:
            refpage = artpage
    for ul in refpage.body.find_all('ul', attrs = {'class' : 'ref-list'}):
        rec['refs'] = []
        for li in ul.find_all('li', attrs = {'class' : 'ref-label'}):
            for li2 in li.find_all('li', attrs = {'class' : 'googleScholar'}):
                li2.decompose()
            rec['refs'].append([('x', re.sub('[\n\t\r]', ' ', li.text.strip()))])
    if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        tryeucllidnumber(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
