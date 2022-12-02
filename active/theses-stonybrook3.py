# -*- coding: utf-8 -*-
#harvest theses Stony Brook U.
#FS: 2020-03-26
#FS: 2022-11-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
import ssl

rpp = 100-90
pages = 5-3
jnlfilename = 'THESES-STONYBROOK-%s' % (ejlmod3.stampoftoday())
publisher = 'Stony Brook U.'

boringdepartments = ['Department of Molecular and Cellular Biology',
                     'Department of Biomedical Engineering',
                     'Department of Biopsychology',
                     'Department of Chemistry', 'Department of Geosciences',
                     'Department of Marine and Atmospheric Science',
                     'Department of Neuroscience', 'Department of Anthropology',
                     'Department of Art History and Criticism',
                     'Department of Materials Science and Engineering',
                     'Department of Biochemistry and Cell Biology',
                     'Department of Biomedical Engineering.',
                     'Department of Comparative Literary and Cultural Studies',
                     'Department of Ecology and Evolution',
                     'Department of Economics', 'Department of English',
                     'Department of Electrical Engineering',
                     'Department of Experimental Psychology',
                     'Department of Genetics', 'Department of Linguistics',
                     'Department of Music', 'Department of Philosophy',
                     'Department of Physiology and Biophysics',
                     'Department of Social/Health Psychology',
                     'Department of Science Education', 'Department of Studio Art',
                     'Department of Biochemistry and Structural Biology',
                     'Department of Clinical Psychology',
                     'Department of Comparative Literature',
                     #'Department of Computer Engineering',
                     #'Department of Computer Engineering.',
                     'Department of Electrical Engineering.',
                     'Department of English.', 'Department of Chemistry.',
                     'Department of Experimental Psychology.',
                     'Department of Hispanic Languages and Literature',
                     'Department of History', 'Department of Sociology',
                     'Department of Materials Science and Engineering.',
                     'Department of Mechanical Engineering',
                     'Department of Molecular Genetics and Microbiology',
                     'Department of Molecular Genetics and Microbiology.',
                     'Department of Oral Biology and Pathology',
                     'Department of Political Science',
                     'Department of Romance Languages and Literature (Italian)',
                     'Department of Technology, Policy, and Innovation',
                     'Department of Theatre Arts',
                     'Department of Anatomical Sciences.',
                     'Department of Anthropology.',
                     'Department of Art History and Criticism.',
                     'Department of Biochemistry and Cell Biology.',
                     'Department of Biochemistry and Structural Biology.',
                     'Department of Biological Sciences.',
                     'Department of Biopsychology.',
                     'Department of Clinical Psychology.',
                     'Department of Comparative Literary and Cultural Studies.',
                     'Department of Comparative Literature.',
                     'Department of Dramaturgy.',
                     'Department of Ecology and Evolution.',
                     'Department of Economics.', 'Department of Genetics.',
                     'Department of Geosciences.',
                     'Department of Hispanic Languages and Literature.',
                     'Department of History.', 'Department of Linguistics.',
                     'Department of Marine and Atmospheric Science.',
                     'Department of Mechanical Engineering.',
                     'Department of Molecular and Cellular Biology.',
                     'Department of Molecular and Cellular Pharmacology',
                     'Department of Molecular and Cellular Pharmacology.',
                     'Department of Music.', 'Department of Neuroscience.',
                     'Department of Oral Biology and Pathology.',
                     'Department of Philosophy.', 'Department of Political Science.',
                     'Department of Physiology and Biophysics.',
                     'Department of Social/Health Psychology.',
                     'Department of Social Welfare.',
                     'Department of Creative Writing and Literature.',
                     'Department of Sociology.', 'Department of Studio Art.',
                     'Department of Technology, Policy, and Innovation.',
                     'Department of Theatre Arts.',
                     'Department of English (Comparative Literature)',
                     'Department of Creative Writing and Literature',
                     'Department of Dramaturgy', 'Department of Art History',
                     'Department of Marine and Atmospheric Scienc',
                     'Department of Population Health and Clinical Outcomes Research',
                     'Department of Romance Languages and Literature (French)',
                     'Department of Social Welfare']

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://ir.stonybrook.edu/xmlui/handle/11401/73112/browse?order=DESC&rpp=' + str(rpp) + '&sort_by=2&etal=-1&offset=' + str(page*rpp) + '&type=dateissued'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://ir.stonybrook.edu')
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['link']))
            time.sleep(15)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued', 'DC.subject',
                                         'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #pages
            if meta['name'] == 'DC.description':
                if re.search('\d\d pg\.', meta['content']):
                    rec['pages'] = re.sub('.*?(\d\d+) pg.*', r'\1', meta['content'])
            #department
            elif meta['name'] == 'DC.contributor':
                if re.search('Department', meta['content']):
                    rec['department'] = meta['content']
                    rec['note'].append(meta['content'])
            #thesis type
            elif meta['name'] == 'DC.type':
                rec['note'].append(meta['content'])
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if 'department' in rec and rec['department'] in boringdepartments:
        print('  skip "%s"' % (rec['department']))
        ejlmod3.adduninterestingDOI(rec['hdl'])
    else:
        print('  ', list(rec.keys()))
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
