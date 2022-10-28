# -*- coding: utf-8 -*-
#harvest Proceedings from JACoW
#FS: 2022-10-27

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
from inspirelabslib3 import *
from clean_fulltext3 import clean_fulltext_jacow, clean_fulltext_moriond, clean_linebreaks, get_reference_section
import sys

publisher = 'JACOW'
tmppath = '/afs/desy.de/group/library/publisherdata/tmp/'
publisherdatapath = '/afs/desy.de/group/library/publisherdata/jacow/'
badpdf = []
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf/10.18429/'

acronym = sys.argv[1]
cnum = sys.argv[2]

jnlfilename = 'jacow.%s' % (acronym)

sourceurl = 'http://jacow.org/%s/html/inspire-%s.xml' % (acronym, acronym)
re_thisConf = re.compile(r'(?i)%s[^a-zA-Z]*%s' % (re.sub('\d.*','',acronym), acronym[-2:]))


re_number = re.compile(r'^\[(\d+)\]')
def by_number(a):
    '''
    sort references by number
    works only if one reference per line
    '''
    number_a = re_number.search(a)
    if number_a:
        return int(number_a.group(1))
    else:
        return 0
    
#get references from fulltext
def get_references(url, doi, clean='jacow'):
    from refextract import extract_references_from_string
    doi1 = re.sub('[\(\)\/]', '_', doi)
    filename = url.split('/')[-1]
    if os.path.isfile('%s/%s_clean.txt' % (tmppath, filename[:-4])):
        #controlfile = codecs.EncodedFile(codecs.open('%s/%s_clean.txt' % (tmppath, filename[:-4])),'utf8')
        controlfile = open('%s%s_clean.txt' % (tmppath, filename[:-4]), 'r')
        fulltext = controlfile.read()
        #fulltext = fulltext.decode("utf-8")
        controlfile.close()      
    else:
        if not os.path.isfile('%s%s.txt' % (tmppath, filename[:-4])):
#           if not os.path.isfile('%s/%s' % (tmppath, filename)):
#               os.system('wget -q -O %s%s %s' % (tmppath, filename, url))
            if not os.path.isfile('%s%s.pdf' % (pdfpath, doi1)):
                os.system('wget -q -O %s%s.pdf %s' % (pdfpath, doi1, url))
            os.system('/usr/bin/pdftotext %s%s.pdf %s%s.txt' % (pdfpath, doi1, tmppath, filename[:-4]))
        #infile = codecs.EncodedFile(codecs.open('%s/%s.txt' % (tmppath, filename[:-4])),'utf8')
        #fulltext = infile.readlines()
        #fulltext = [line.decode("utf-8") for line in fulltext]
        infile = open('%s%s.txt' % (tmppath, filename[:-4]), 'r')
        fulltext = infile.readlines()
        if clean == 'jacow':
            fulltext = clean_fulltext_jacow(fulltext, verbose=1)
        elif clean == 'moriond':
            fulltext = clean_fulltext_moriond(fulltext)
        elif clean == 'linebreaks':
            fulltext = '\n'.join(fulltext)+'\n'
            fulltext = clean_linebreaks(fulltext)
        else:
            fulltext = '\n'.join(fulltext)+'\n'
        fulltext = get_reference_section(fulltext, item_tag='[')
        infile.close()

        if '[2]' in fulltext:
            lines = fulltext.split('\n')
            lines.sort(key=by_number)
            fulltext = '\n'.join(lines)
            last_number = 0
            errors = ''
            for line in lines:
                number = re_number.search(line)
                if number:
                    this_number = int(number.group(1))
                    if not this_number - last_number == 1:
                        errors += '%s: [%s] followed by [%s]\n' % (filename[:-4], last_number, this_number)
                    last_number = this_number
                elif last_number:
                    errors += '%s: No number for %s\n' % (filename[:-4], line[:30])
            if errors:
                reflog_file = open('%s/%s.log' % (publisherdatapath, filename[:-4]), mode='w')
                reflog_file.write(errors)
                reflog_file.close()

        controlfile = codecs.EncodedFile(codecs.open('%s/%s_clean.txt' % (tmppath, filename[:-4]), mode='wb'),'utf8')
        controlfile.write(fulltext.encode("utf-8"))
        controlfile.close()        
    
    refs = extract_references_from_string(fulltext, is_only_references=False, override_kbs_files={'journals': '/opt/invenio/etc/docextract/journal-titles-inspire.kb'}, reference_format="{title},{volume},{page}")
    references = []
    
    #mappings for references in JSON to MARC
    mappings = {'doi': 'a',
                'collaborations': 'c',
                'document_type': 'd',
                'author': 'h',
                'isbn': 'i',
                'texkey': 'k',
                'misc': 'm',
                'journal_issue': 'n',
                'label': 'o',
                'linemarker': 'o',
                'reportnumber': 'r',
                'journal_reference': 's',
                'title': 't',
                'urls': 'u',
                'url': 'u',
                'raw_ref': 'x',
#                'journal_title': None,
#                'journal_volume': None,
#                'journal_page': None,
#                'journal_year': None,
#                'publisher': None,
                'year': 'y'}
    
    for ref in refs:
        entryaslist = [('9','refextract')]
        for key in ref.keys():
            if key in mappings:
                for entry in ref[key]:
                     entryaslist.append((mappings[key], entry))
#            else:
#                print 'no mapping for', key
        references.append(entryaslist)
    return references   
    


#create DOI for references to other contributions of these proceedings
def addDOI_thisConference(ref, base_doi, re_thisConf):
    re_artid = re.compile(r'paper ([A-Z][A-Z0-9]{5,8})')
    no_doi = True
    rawref = ''
    for code, value in ref:
        if code == 'a':
            no_doi = False
        if code == 'x':
            rawref = value
    if no_doi and rawref:
        found_artid = re_artid.search(rawref)
        in_thisConf = "this conference" in rawref.lower() or re_thisConf.search(rawref)
        if found_artid and in_thisConf:
            ref.append(('a', 'doi:%s-%s' % (base_doi, found_artid.group(1))))
    return ref    

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
req = urllib.request.Request(sourceurl, headers=hdr)
sourcesoup = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

nrec = 0
info = {}
licence = False
records = sourcesoup.find_all('record')
for record in records:
    nrec += 1
    rec = {'tc' : 'C', 'jnl' : 'JACoW', 'cnum' : cnum, 'acronym' : acronym, 'autaff' : [],
           'refs' : [], 'keyw' : []}
    (p1, url) = ('-', False)
    #URL
    for df in record.find_all('datafield', attrs = {'tag' : '856'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
            url = sf.text.strip()
    #DOI 
    for df in record.find_all('datafield', attrs = {'tag' : '024', 'ind1' : '7'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['doi'] = sf.text.strip()
            jacow_doi = rec['doi'][9:].split('-')
            base_doi = '10.18429/%s-%s' % (jacow_doi[0], jacow_doi[1])
            if not re.search('10.18429\/jacow\-', rec['doi'], flags=re.IGNORECASE):
                print('  invalid DOI?: %s' % (rec['doi']))
    #find PDF
    if not url and 'doi' in rec:
        url = "http://jacow.org/%s/papers/%s.pdf" % (jacow_doi[1].lower(), jacow_doi[2].lower())         
    if url:
        if url[-4:].lower() == '.pdf':
            if nrec < 10:
                url_type = urllib.request.urlopen(url).info().get('Content-Type')
                if not url_type == 'application/pdf':
                    if first:
                        print('  switch to accelconf')
                        first = False
                    url = url.replace("http://jacow.org/", "http://accelconf.web.cern.ch/AccelConf/") 
                    url_type = urllib.urlopen(url).info().get('Content-Type')
                    if not url_type == 'application/pdf':
                        print('  still doesnt work:', url)
                        url = None
            if url:
                rec['artlink'] = url
                artid = url.split('/')[-1].split('.')[0]
                if artid.upper() in badpdf:
                    print('  No FFT for',url)
                else:
                    rec['FFT'] = url
                    #add references
                    references = get_references(url, rec['doi'])
                    for ref in references:
                        ref = addDOI_thisConference(ref, base_doi, re_thisConf)
                        rec['refs'].append(ref)
            else:
                rec['artlink'] = url                           
        else:
            rec['artlink'] = url
    else:
        print('  No URL found!')
        print(record)
    #ISBN
    for df in record.find_all('datafield', attrs = {'tag' : '020'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['isbn'] = sf.text.strip()
            rec['tc'] = 'K'
    #license
    for df in record.find_all('datafield', attrs = {'tag' : '540'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            licence = sf.text.strip() 
            if not licence in ['CC-BY-4.0', 'Open Access']:
                print('  Licence different:', licence)
    if licence:
        rec['license'] = {'statement' : licence}
    #date
    for df in record.find_all('datafield', attrs = {'tag' : '260'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'c'}):
            rec['date'] = sf.text.strip()
    #pubnote
    for df in record.find_all('datafield', attrs = {'tag' : '773'}):
        #article ID
        for sf in df.find_all('subfield', attrs = {'code' : 'c'}):
            p1 = sf.text.strip()
            rec['p1'] = p1
        #volume
        for sf in df.find_all('subfield', attrs = {'code' : 'q'}):
            rec['vol'] = sf.text.strip()
            rec['acronym'] = sf.text.strip()
    #authors
    for df in record.find_all('datafield', attrs = {'tag' : ['100', '700']}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            name = sf.text.strip()
            if name in ['Schaa, Volker RW', 'Schaa, Volker R. W.']:
                name = 'Schaa, Volker R.W.'
            rec['autaff'].append([name])
        for sf in df.find_all('subfield', attrs = {'code' : 'e'}):
            rec['autaff'][-1][0] += ' (Ed.)'
        for sf in df.find_all('subfield', attrs = {'code' : 'j'}):
            rec['autaff'][-1].append(sf.text.strip())
        for sf in df.find_all('subfield', attrs = {'code' : 'm'}):
            rec['autaff'][-1].append('EMAIL:'+sf.text.strip())
        for sf in df.find_all('subfield', attrs = {'code' : 'v'}):
            rec['autaff'][-1].append(sf.text.strip())
    #title
    for df in record.find_all('datafield', attrs = {'tag' : '245'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            title = sf.text.strip()
            rec['tit'] = title
            if title in info:
                print('  same title in %s and' % (p1))
                print('                %s \n ' % (info[title]))
                info[title] += p1
            else:
                info[title] = p1                
    #pages
    for df in record.find_all('datafield', attrs = {'tag' : '300'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', sf.text.strip())
    #abstract
    for df in record.find_all('datafield', attrs = {'tag' : '520'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['abs'] = sf.text.strip()
    #keywords
    for df in record.find_all('datafield', attrs = {'tag' : '653', 'ind1' : '1'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['keyw'].append(sf.text.strip())
    recs.append(rec)
    ejlmod3.printprogress('==', [[nrec, len(records)], [p1]])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

