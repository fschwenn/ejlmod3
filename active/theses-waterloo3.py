# -*- coding: utf-8 -*-
#harvest theses from Waterloo
#FS: 2019-09-24
#FS: 2022-09-27

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'U. Waterloo (main)'

jnlfilename = 'THESES-WATERLOO-%s' % (ejlmod3.stampoftoday())
rpp = 100
pages = 3
skipalreadyharvested = True

boring = ['School+of+Public+Health+and+Health+Systems', 'Kinesiology',
          'Health+Studies+and+Gerontology+%28Aging%2C+Health%2C+and+Well-Being%29',
          'Chemistry', 'English', 'Recreation+and+Leisure+Studies',
          'Chemical+Engineering+%28Nanotechnology%29', 'Chemical+Engineering',
          'Civil+and+Environmental+Engineering', 'Civil+Engineering',
          'Combinatorics+and+Optimization', 'Earth+and+Environmental+Sciences',
          'Earth+Sciences', 'Global+Governance', 'Planning', 'Political+Science',
          'Psychology', 'Public+Health+and+Health+Systems',
          'School+of+Environment%2C+Enterprise+and+Development', 'School+of+Planning',
          'School+of+Public+Health+Sciences', 'Sustainability+Management',
          'System+Design+Engineering', 'Systems+Design+Engineering', 'Actuarial+Science',
          'Biology+%28Water%29', 'Biology', 'Geography+%28Water%29',
          'Geography+and+Environmental+Management', 'Geography', 'Accounting',
          'Economics+%28Appplied+Economics%29', 'Economics', 'English+%28Literary+Studies%29',
          'English+%28Rhetoric+and+Communication+Design%29', 'English+Language+and+Literature',
          'Environment%2C+Resources+and+Sustainability+Studies+%28Social+and+Ecological%0D%0A++++++++++Sustainability%29',
          'Germanic+and+Slavic+Studies', 'German', 'History', 'Management+Sciences',
          'Pharmacy', 'Philosophy', 'Religious+Studies', 'School+of+Accounting+and+Finance',
          'School+of+Environment%2C+Resources+and+Sustainability',
          'School+of+Optometry+and+Vision+Science', 'School+of+Pharmacy',
          'Social+and+Ecological+Sustainability+%28Water%29',
          'Social+and+Ecological+Sustainability', 'Statistics+%28Biostatistics%29',
          'Vision+Science', 'French+Studies', 'Sociology+and+Legal+Studies', 'Sociology']
boring += ['Mechanical+Engineering', 'Mechanical+Engineering+%28Nanotechnology%29',
           'Mechanical+and+Mechatronics+Engineering']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
          

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for page in range(pages):
    tocurl = 'https://uwspace.uwaterloo.ca/handle/10012/6/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Doctoral+Thesis'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    prerecs = ejlmod3.getdspacerecs(tocpage, 'https://uwspace.uwaterloo.ca')
    for rec in prerecs:
        keepit = True
        if 'degrees' in rec:
            for degree in rec['degrees']:
                if degree in boring:
                    keepit = False
                elif degree in ['Computer+Science', 'David+R.+Cheriton+School+of+Computer+Science']:
                    rec['fc'] = 'c'
                elif degree in ['Applied+Mathematics', 'Pure+Mathematics', 'Applied+Mathematics+%28Water%29']:
                    rec['fc'] = 'm'
                elif degree in ['Statistics+and+Actuarial+Science', 'Statistics']:
                    rec['fc'] = 's'
                elif degree in ['Computer+Science+%28Quantum+Information%29']:
                    rec['fc'] = 'ck'
                elif degree in ['Physics+%28Quantum+Information%29']:
                    rec['fc'] = 'k'
                elif degree in ['Applied+Mathematics+%28Quantum+Information%29']:
                    rec['fc'] = 'km'
        if keepit and ejlmod3.checkinterestingDOI(rec['hdl']):
            if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    print('    %4i records so far' % (len(recs)))

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author ]]
        rec['autaff'][-1].append('U. Waterloo (main)')
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
