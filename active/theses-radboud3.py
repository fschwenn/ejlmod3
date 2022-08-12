# -*- coding: utf-8 -*-
#harvest theses from Nijmegen U.
#FS: 2022-07-21

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Nijmegen U.'
jnlfilename = 'THESES-RADBOUD-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 2
years = 2
boring = ['Analytical Chemistry', 'Animal Ecology & Physiology', 'Applied Materials Science',
          'Biomolecular Chemistry', 'Bio-organic Chemistry', 'Biophysics', 'Digital Security',
          'Ecological Microbiology', 'Environmental Science', 'Molecular Biology',
          'Molecular Developmental Biology', 'Molecular Neurobiology', 'Neuroinformatics',
          'Neurophysiology', 'Onderzoekcentrum Onderneming & Recht (OO&R)',
          'Philosophy and Science Studies', 'Physical Organic Chemistry',
          'PI Group Memory & Space', 'Scanning Probe Microscopy', 'Science Education',
          'Solid State Chemistry', 'Solid State NMR', 'Spectroscopy and Catalysis',
          'Spectroscopy of Cold Molecules', 'Spectroscopy of Solids and Interfaces',
          'Synthetic Organic Chemistry', 'Systems Chemistry', 'Tumorimmunology',
          'Donders Centre for Neuroscience', 'Experimental Plant Ecology',
          'Institute for Science, Innovation and Society', 'Molecular Plant Physiology',
          'Proteomics and Chromatin Biology', 'Aquatic Ecology and Environmental Biology',
          'Department for Sustainable Management of Resources', 'Molecular and Biophysics',
          'Molecular Structure and Dynamics', 'Biophysical Chemistry',
          'Organismal Animal Physiology', 'Molecular Animal Physiology',
          'Theoretical Chemistry', 'Molecular Materials']
          
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://repository.ubn.ru.nl/handle/2066/119638/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Dissertation'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
    except:
        print("retry in 180 seconds")
        time.sleep(180)
        tocpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open('%s%i' % (tocurl, offset)), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://repository.ubn.ru.nl'):
        if 'year' in rec and int(rec['year']) < ejlmod3.year(backwards=years):
            pass
        else:
            prerecs.append(rec)

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'citation_pdf_url', "citation_author", "citation_isbn",
                                        "DC.language", "DCTERMS.abstract"])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #infos in DC.description
            if meta['name'] == 'DC.description':
                #supervisor
                if re.search('^Promotor', meta['content']):
                    promoter = re.sub('\.? *Co\-promotor.*', '', meta['content'])
                    promoter = re.sub('Promotore?s? *: *', '', promoter)
                    if not 'supervisor' in rec:
                        rec['supervisor'] = []
                    if re.search('Promotores *:', meta['content']):
                        rec['supervisor'] = [[sv] for sv in re.split(', ', promoter)]
                    else:
                        rec['supervisor'].append([promoter])
                #pages
                elif re.search('(\d\d+) p\.$', meta['content']):
                    rec['pages'] = re.sub('.*(\d\d+) p\.$', r'\1', meta['content'])
    #organization
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-organization'}):
        for div2 in div.find_all('div'):
            dt = div2.text.strip()
            if dt in ['Astrophysics']:
                rec['fc'] = 'a'
            elif dt in ['Experimental High Energy Physics']:
                rec['fc'] = 'e'
            elif dt in ['Correlated Electron Systems', 'FELIX Condensed Matter Physics',
                        'FELIX Condensed Matter Physic',
                        'Theory of Condensed Matter', 'Condensed Matter Science (HFML)',
                        'Soft Condensed Matter and Nanomaterials']:
                rec['fc'] = 'f'
            elif dt in ['Mathematics', 'Mathematical Physics', 'Algebra & Topologie']:
                rec['fc'] = 'm'
            elif dt in ['Software Science', 'ICIS - Institute for Computing and Information Sciences']:
                rec['fc'] = 'c'
            elif dt in boring:
                keepit = False
            else:
                rec['note'].append('organization:'+dt)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
