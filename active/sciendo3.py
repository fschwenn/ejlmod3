# -*- coding: UTF-8 -*-
#program to harvest Sciendo journals
# FS 2023-09-20

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import json

urltrunc = 'https://www.degruyter.com'
publisher = 'Sciendo'
skipalreadyharvested = True

journal = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]

jnlfilename = 'sciendo%s%s.%s_%s' %  (journal, vol, iss, ejlmod3.stampoftoday())

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


tc = 'P'
if journal == 'nuka':
    jnl = 'Nukleonika'
elif journal == 'ausm':
    jnl = 'Acta Univ.Sap.Math.'


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

tocurl = 'https://sciendo.com/issue/%s/%s/%s' % (journal.upper(), vol, iss)
print(tocurl)

#tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
#print(tocpage.text)
recs = []
for h4 in tocpage.find_all('h5'):
    print(h4)
    for a in h4.find_all('a'):
        if a.has_attr('href') and re.search('\/article\/', a['href']):
            rec = {'tc' : tc, 'jnl' : jnl, 'vol' : vol, 'issue' : iss, 'autaff' : [], 'keyw' : []}
            rec['artlink'] = 'https://sciendo.com' + a['href']
            rec['doi'] = re.sub('.*article\/', '', a['href'])
            if not rec['doi'] in alreadyharvested:
                recs.append(rec)
                alreadyharvested.append(rec['doi'])

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['dc.identifier', 'citation_title', 'citation_publication_date',
                                        'citation_firstpage', 'citation_lastpage', 'citation_pdf_url'])
    #JSON
    for script in artpage.body.find_all('script'):
        articledata = False
        if script.contents:
            #scriptt = re.sub('[\n\t]', '', script.text.strip())
            scriptt = re.sub('[\n\t]', '', script.contents[0].strip())
            scriptt = re.sub('.*window.jscholApp_initialPageData *= *(\{.*\}).*', r'\1', scriptt)
            if not re.search('abstract.*authors', scriptt):
                scriptt = False
        else:
            scriptt = False
        if scriptt:
            scripttjson = json.loads(scriptt)
            if 'props' in scripttjson and 'pageProps' in scripttjson['props']:
                if 'product' in scripttjson['props']['pageProps']:
                    if 'articleData' in scripttjson['props']['pageProps']['product']:
                        articledata = scripttjson['props']['pageProps']['product']['articleData']
        if articledata:
            affs = {}
            if 'contribGroup' in articledata:
                #print(articledata['contribGroup'])
                    #affiliation
                    if 'aff' in articledata['contribGroup'] and articledata['contribGroup']['aff']:
                        if type(articledata['contribGroup']['aff']) == type({'a' : 1}):
                            afflist = [articledata['contribGroup']['aff']]
                        else:
                            afflist = articledata['contribGroup']['aff']
                        for aff in afflist:
                            #print(aff)
                            rawaff = ''
                            if 'institution' in aff:
                                if type(aff['institution']) == type('STRING'):
                                    rawaff += aff['institution'] + ', '
                                else:
                                    if type(aff['institution']) == type({'a' : 1}):
                                        instlist = [aff['institution']]
                                    else:
                                        instlist = aff['institution']
                                    for inst in instlist:
                                        if 'content' in inst:
                                            rawaff += str(inst['content']) + ', '
                            elif 'content' in aff and aff['content']:
                                rawaff += str(aff['content']) + ', '
                            if 'addr-line' in aff:
                                rawaff += str(aff['addr-line'])
                            if 'postal-code' in aff:
                                rawaff += str(aff['postal-code'])
                            if 'city' in aff:
                                rawaff += ' ' + str(aff['city']) +', '
                            if 'country' in aff:
                                if 'content' in aff['country']:
                                    rawaff += ' ' + aff['country']['content']
                                else:
                                    for c in aff['country']:
                                        if 'content' in c:
                                            rawaff += ' ' + c['content'] + ', '
                                        else:
                                            rawaff += ' ' + str(c) + ', '
                            affs[aff['id']] = rawaff
                    #authors
                    if 'contrib' in articledata['contribGroup'] and articledata['contribGroup']['contrib']:
                        for contrib in articledata['contribGroup']['contrib']:
                            if 'name' in contrib and contrib['name']:
                                author = contrib['name']['surname']
                                if 'prefix' in contrib['name'] and contrib['name']['prefix']:
                                    if 'given-names' in contrib['name'] and contrib['name']['given-names']:
                                        author += ', %s %s' % (contrib['name']['prefix'], contrib['name']['given-names'])
                                elif 'given-names' in contrib['name'] and contrib['name']['given-names']:
                                    author += ', %s' % ( contrib['name']['given-names'])
                                if 'suffix' in contrib['name'] and contrib['name']['suffix']:
                                    author += ' %s' % (contrib['name']['suffix'])
                                rec['autaff'].append([author])
                                if 'contrib-id' in contrib and contrib['contrib-id']:
                                    if contrib['contrib-id']['contrib-id-type'] == 'orcid':
                                        rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', contrib['contrib-id']['content']))
                                    elif 'email' in contrib:
                                        rec['autaff'][-1].append('EMAIL:' + contrib['email']['content'])
                                if 'xref' in contrib and contrib['xref'] and 'rid' in contrib['xref']:
                                    xrefid = contrib['xref']['rid']
                                    if xrefid in affs:
                                        rec['autaff'][-1].append(affs[xrefid])
                                    else:
                                        print(xrefid, '???')
                            else:
                                print(contrib, '???')
            #license
            if 'permissions' in articledata and 'license' in articledata['permissions']:
                if 'xlink:href' in articledata['permissions']['license']:
                    href = articledata['permissions']['license']['xlink:href']
                    if re.search('creativecommons.org', href):
                        rec['license'] = {'url' : href}
            #abstract
            if 'abstractContent' in articledata and articledata['abstractContent']:
                if type(articledata['abstractContent']) == type('hallo'):
                    rec['abs'] = articledata['abstractContent']
                else:
                    for abstract in articledata['abstractContent']:
                        print(abstract)
                        if not 'language' in abstract or abstract['language'] == 'English':
                            rec['abs'] =  BeautifulSoup(abstract['content'], features='lxml').text.strip()
            #year
            if 'publishYear' in articledata:
                rec['year'] = str(articledata['publishYear'])
            #keywords
            if 'keywords' in articledata and articledata['keywords']:
                print(articledata['keywords'])
                if type(articledata['keywords']) == type('hallo'):
                    rec['keyw'] = [articledata['keywords']]
                elif type(articledata['keywords']) == type([]):
                    rec['keyw'] = articledata['keywords']
                else:
                    for kw in articledata['keywords']:
                        rec['keyw'] += kw['keywords']
            #references
            if 'referenceList' in articledata and articledata['referenceList']:
                rec['refs'] = []
                for ref in articledata['referenceList']:
                    if 'doi' in ref and ref['doi']:
                        rec['refs'].append([('x', ref['citeString']), ('a', 'doi:' + ref['doi'])])
                    else:
                        rec['refs'].append([('x', ref['citeString'])])

    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
