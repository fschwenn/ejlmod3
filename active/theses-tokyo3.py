# -*- coding: utf-8 -*-
#harvest theses (with english titles) from Tokyo U.
#FS: 2020-06-22

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import datetime

startdate = datetime.datetime.now() + datetime.timedelta(days=-90-30)
stampofstartdate = '%4d-%02d-%02d' % (startdate.year, startdate.month, startdate.day)

publisher = 'Tokyo U.'
verbose = True
years = 2+3

hdr = {'User-Agent' : 'Magic Browser'}
boring = ['journal article', 'conference paper', 'departmental bulletin paper', 'article',
          'other', 'book', 'conference object', 'dataset', 'master thesis', 'conference poster',
          'periodical', 'still image', 'technical report']
boringfacs = ['110', '111', '112', '113', '114',
              '116', '117', '118', '119', '120',
              '122', '123', '124', '131', '132', '133', '134', '135', '136',
              '138', '139', '140', '156', '166', '181', '182', '190', '191', '192', '200', '300']
boringfacs += ['1150910', '1150920', '1150620', '1150625', '1150920', '1151120', '1151420']
interesting = ['doctoral thesis', 'thesis']

#tocurl = 'https://repository.dl.itc.u-tokyo.ac.jp/oai?verb=ListIdentifiers&metadataPrefix=oai_dc&from=' + stampofstartdate
tocurl = 'https://repository.dl.itc.u-tokyo.ac.jp/oai?verb=ListRecords&from=' + stampofstartdate + '&until=' + ejlmod3.stampoftoday() + '&metadataPrefix=jpcoar_1.0'
prerecs = {}
notcomplete = True
cls = 0
i = 0
rec= {'identifier' : ''}
while notcomplete:
    i += 1
    ejlmod3.printprogress('=', [[i, (cls-1)//100 + 1], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    j = 0
    for record in tocpage.find_all('record'):
        j += 1
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'autaff' : []}
        category = 'none'
        keepit = True
        #deleted?
        for header in record.find_all('header', attrs = {'status' : 'deleted'}):
            keepit = False
            if verbose: print('   deleted')            
        #identifier
        for identifier in record.find_all('identifier'):
            rec['identifier'] = identifier.text
        if ejlmod3.ckeckinterestingDOI(rec['identifier']):
            keepit = False
            if verbose: print('   uninterestingDOI')
        ejlmod3.printprogress('-', [[100*(i-1)+j, cls], [rec['identifier']]])
        #type
        for dt in record.find_all('dc:type'):
            category = dt.text
            if category in boring:
                if verbose: print('   skip "%s"' % (category))
                keepit = False
            elif category == 'thesis':
                for dn in record.find_all('dcndl:degreename'):
                    dnt = dn.text
                    if verbose: print('   '+dnt)
                    if dnt in ['理学博士', '博士(理学)']:
                        category = 'doctoral thesis'
                    elif dnt in ['修士(工学)', '修士(理学)']:
                        if verbose: print('   skip "%s"' % (dnt))
                        keepit = False
                    else:                        
                        category = 'thesis_' + dn.text
        if verbose: print('   category: '+category)
        #title
        for dt in record.find_all('dc:title'):
            rec['tit'] = dt.text
        for dt in record.find_all('dcterms:alternative'):
            rec['transtit'] = dt.text
        #language
        for dl in record.find_all('dc:language'):
            rec['language'] = dl.text
        #date
        for dd in record.find_all('datacite:date', attrs = {'datetype' : 'Issued'}):
            rec['date'] = dd.text
            if re.search('[12]\d\d\d', rec['date']):
                rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
                if int(rec['year']) < ejlmod3.year(backwards=years):
                    keepit = False
                    if verbose: print('   skip '+ rec['date'])                    
        #PIDs
        for pid in record.find_all('jpcoar:identifier', attrs = {'identifiertype' : 'HDL'}):
            rec['hdl'] = pid.text
        for pid in record.find_all('jpcoar:identifier', attrs = {'identifiertype' : 'DOI'}):
            rec['doi'] = pid.text
        for pid in record.find_all('jpcoar:identifier', attrs = {'identifiertype' : 'URI'}):
            rec['link'] = pid.text
        #Nippon Decimal Classification
        for ndc in record.find_all('jpcoar:subject', attrs = {'subjectscheme' : 'NDC'}):
            ndt = ndc.text[:2]
            if ndt == '41':
                rec['fc'] = 'm'
            elif ndt == '44':
                rec['fc'] = 'a'
            elif not ndt == '42':
                if verbose: print('   skip NDC='+ndc.text)
                keepit = False
        #pdf
        for jf in record.find_all('jpcoar:file'):
            for jm in jf.find_all('jpcoar:mimetype'):
                if jm.text == 'application/pdf':
                    for ju in jf.find_all('jpcoar:uri'):
                        rec['pdf_url'] = ju.text
        #author
        for jcn in record.find_all('jpcoar:creatorname'):
            rec['autaff'].append([ jcn.text, publisher ])
        #article page
        if keepit and 'link' in rec:
            if verbose: print(rec['link'])
            time.sleep(2)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            for pre in artpage.body.find_all('pre', attrs = {'class' : 'hide'}):
                metadata = json.loads(pre.text)
                #abstract
                if 'item_4_description_5' in metadata.keys():
                    abstract = metadata['item_4_description_5']['attribute_value_mlt'][0]['subitem_description']
                    if re.search('the', abstract):
                        rec['abs'] = abstract
                #degree
                if 'item_7_select_21' in metadata.keys():
                    degree = metadata['item_7_select_21']['attribute_value_mlt'][0]['subitem_select_item']
                    if degree in 'master':
                        if verbose: print('   skip degree "%s"' % (degree))
                        ejlmod3.adduninterestingDOI(rec['identifier'])
                        keepit = False
                    else:
                        rec['note'].append('DEGREE:'+degree)
            #faculty
            for ols in artpage.body.find_all('ol', attrs = {'class' : 'breadcrumb'}):
                for a in ols.find_all('a'):
                    fac = re.sub('\D', '', a.text.strip())
                    if fac in boringfacs:
                        if verbose: print( '  skip fac=%s' % (a.text.strip()))
                        ejlmod3.adduninterestingDOI(rec['identifier'])
                        keepit = False
        if keepit:        
            rec['artlink'] = 'https://repository.dl.itc.u-tokyo.ac.jp/records/' + re.sub('.*:0*', '', rec['identifier'])            
            if category in prerecs:
                prerecs[category].append(rec)
            else:
                prerecs[category] = [rec]
            ejlmod3.printrecsummary(rec)
    notcomplete = False
    for rt in tocpage.find_all('resumptiontoken'):
        tocurl = 'https://repository.dl.itc.u-tokyo.ac.jp/oai?verb=ListRecords&metadataPrefix=jpcoar_1.0&resumptionToken=' + rt.text.strip()
        cls = int(rt['completelistsize'])
        notcomplete = True
    lp = [len(prerecs[category]) for category in prerecs]
    ejlmod3.printprogress('+', [[sum(lp), 100*i, cls], list(prerecs.keys()), lp])
    if 100*i >= cls:
        notcomplete = False
    time.sleep(2)

if 'doctoral thesis' in prerecs:
    jnlfilename = 'THESES-TOKYO_U-%s' % (ejlmod3.stampoftoday())
    ejlmod3.writenewXML(prerecs['doctoral thesis'], publisher, jnlfilename, retfilename='retfiles_special')
    
for category in prerecs:
    if category != 'doctoral thesis':
        jnlfilename = '%s-TOKYO_U-%s' % (re.sub('\W', '', category.upper()), ejlmod3.stampoftoday())
        try:
            ejlmod3.writenewXML(prerecs[category], publisher, jnlfilename, retfilename='retfiles_special')
        except:
            ejlmod3.writenewXML([], publisher, jnlfilename, retfilename='retfiles_special')
