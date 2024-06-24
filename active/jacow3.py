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
import ssl
from urllib3 import poolmanager
from json import loads
import time

publisher = 'JACOW'
tmppath = '/afs/desy.de/group/library/publisherdata/tmp/'
publisherdatapath = '/afs/desy.de/group/library/publisherdata/jacow/'
badpdf = []
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf/10.18429/'

acronym = sys.argv[1]
cnum = sys.argv[2]

jnlfilename = 'jacow.%s_B' % (acronym)

sourceurl = 'http://jacow.org/%s/json/inspire-%s.jsonl' % (acronym, acronym)
sourceurl = 'https://www.desy.de/~schwenn/inspire-IPAC2023.jsonl'
print(sourceurl)
re_thisConf = re.compile(r'(?i)%s[^a-zA-Z]*%s' % (re.sub('\d.*','',acronym), acronym[-2:]))

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

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
                time.sleep(1)
            os.system('/usr/bin/pdftotext %s%s.pdf %s%s.txt' % (pdfpath, doi1, tmppath, filename[:-4]))
        if not os.path.isfile('%s%s.txt' % (tmppath, filename[:-4])):
            return []
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
    
    refs = extract_references_from_string(fulltext, is_only_references=False, override_kbs_files={'journals': '/afs/desy.de/user/l/library/lists/journal-titles-inspire.py3.kb'}, reference_format="{title},{volume},{page}")
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
if not os.path.isfile('/tmp/inspire-%s.jsonl' % (acronym)):
    os.system("wget -q -O /tmp/inspire-%s.jsonl %s" % (acronym, sourceurl))
inf = open('/tmp/inspire-%s.jsonl' % (acronym))
lines = inf.readlines()
inf.close()

nrec = 0
info = {}
licence = False
for line in lines:    
    nrec += 1
    jsonrecord = loads(line)
    rec = {'tc' : 'C', 'jnl' : 'JACoW', 'cnum' : cnum, 'acronym' : acronym, 'autaff' : [],
           'refs' : [], 'keyw' : []}
    #DOI
    if 'dois' in jsonrecord:
        rec['doi'] = jsonrecord['dois'][0]['value']
        jacow_doi = rec['doi'][9:].split('-')
        base_doi = '10.18429/%s-%s' % (jacow_doi[0], jacow_doi[1])
    elif 'urls' in jsonrecord:
        rec['link'] = jsonrecord['urls'][0]['value']
    #find PDF
    if 'documents' in jsonrecord:
        rec['FFT'] = jsonrecord['documents'][0]['url']
        #add references
        references = get_references(rec['FFT'], rec['doi'])
        for ref in references:
            ref = addDOI_thisConference(ref, base_doi, re_thisConf)
            rec['refs'].append(ref)
        else:
            rec['artlink'] = rec['FFT'] 
    #ISBN
    if 'isbns' in jsonrecord:
        rec['isbn'] = re.sub('-', '', jsonrecord['isbns'][0]['value'])
        rec['tc'] = 'K'
    #license
    if 'license' in jsonrecord:
        rec['license'] = {'url' : jsonrecord['license'][0]['url']}
    #date
    if 'imprints' in jsonrecord:
        rec['date'] = jsonrecord['imprints'][0]['date']
    #pubnote
    if 'publication_info' in jsonrecord:
        if 'artid' in jsonrecord['publication_info'][0]:
            rec['p1'] = jsonrecord['publication_info'][0]['artid']
        rec['year'] = str(jsonrecord['publication_info'][0]['year'])
        if 'journal_volume' in jsonrecord['publication_info'][0]:
            rec['vol'] = jsonrecord['publication_info'][0]['journal_volume']
            rec['acronym'] = jsonrecord['publication_info'][0]['conf_acronym']
        if 'acronym' in jsonrecord['publication_info'][0]:
            rec['vol'] = jsonrecord['publication_info'][0]['journal_volume']
            rec['acronym'] = jsonrecord['publication_info'][0]['conf_acronym']
    #authors
    if 'authors' in jsonrecord:
        for author in jsonrecord['authors']:
            if rec['tc'] == 'C':
                rec['autaff'].append([author['full_name']])
            else:
                rec['autaff'].append([author['full_name'] + ' (Ed.)'])
            if 'raw_affiliations' in author:
                for aff in author['raw_affiliations']:
                    rec['autaff'][-1].append(aff['value'])                                 
    #title
    rec['tit'] = jsonrecord['titles'][0]['title']
    #pages
    #abstract
    if 'abstracts' in jsonrecord:
        rec['abs'] = jsonrecord['abstracts'][0]['value']
    #keywords
    if 'keywords' in jsonrecord:
        for keyw in jsonrecord['keywords']:
            rec['keyw'].append(keyw['value'])
    recs.append(rec)
    ejlmod3.printprogress('==', [[nrec, len(lines)]])
    ejlmod3.printrecsummary(rec)
    #ejlmod3.printrec(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

