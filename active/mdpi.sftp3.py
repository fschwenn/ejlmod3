# -*- coding: UTF-8 -*-
#program to harvest MDPI journals (Universe, Symmetry, Sensors, Instruments, Galaxies, Entropy, Atoms) via sftp
# FS 2022-02-03
# FS 2023-02-28 

import os
import ejlmod3
import re
import sys
import unicodedata
import string
 
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import datetime
import time
import pysftp
import tarfile
from refextract import  extract_references_from_string
from extract_jats_references3 import jatsreferences

publisherpath = '/afs/desy.de/group/library/publisherdata/mdpi'
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf/10.3390'
tmppath = publisherpath + '/tmp'

def tfstrip(x): return x.strip()

chunksize = 100
numberofissues = 4

publisher = 'MDPI'
jnl = sys.argv[1]
if jnl in ['proceedings', 'psf']:
    volume = sys.argv[2]
    issue = sys.argv[3]
    cnum = sys.argv[4]


now = datetime.datetime.now()
startdate = now + datetime.timedelta(days=-90)
stampofstartdate = '%4d-%02d-%02d' % (startdate.year, startdate.month, startdate.day)

conferences = {'Selected Papers from the 1st International Electronic Conference on Universe (ECU 2021)' : 'C21-02-22',
               'Selected Papers from the 17th Russian Gravitational Conference —International Conference on Gravitation, Cosmology and Astrophysics (RUSGRAV-17)' : 'C20-06-28'}



missingpubnotes = ["10.3390/universe8020085","10.3390/sym14010130","10.3390/photonics9020061","10.3390/sym14020265","10.3390/metrology1020008","10.3390/app112411669","10.3390/e24010104","10.3390/molecules27030597","10.3390/e24010043","10.3390/sym14010180","10.3390/nano12020243","10.3390/nano11112972","10.3390/foundations1020017","10.3390/galaxies9040078","10.3390/math9182178","10.3390/e23111371","10.3390/universe6050068","10.3390/e23101353","10.3390/e23111377","10.3390/psf2021003008","10.3390/universe7010015","10.3390/galaxies9020023","10.3390/ECU2021-09310","10.3390/e24010012","10.3390/atmos12091230","10.3390/e24010101","10.3390/universe705013","10.3390/universe7050139","10.3390/e23101333","10.3390/e23101350","10.3390/photonics8120552","10.3390/sym13060978","10.3390/app11104357","10.3390/rs12203440","10.3390/sym1010000","10.3390/w12113263","10.3390/math8091469","10.3390/data5030085","10.3390/e22010111","10.3390/s20071930","10.3390/books978-3-03921-765-6","10.3390/e22010101","10.3390/quantum1020025","10.3390/universe5050099","10.3390/sym11070880","10.3390/data3040056","10.3390/universe5030080","10.3390/sym10090396","10.3390/sym10090415","10.3390/jimaging4060077","10.3390/mi8090277","10.3390/polym12051066","10.3390/s150100515","10.3390/fractalfract2040026","10.3390/geosciences11060239","10.3390/s151127905","10.3390/cli3030474"]
calor22 = ["10.3390/instruments6030036", "10.3390/instruments6040075", "10.3390/instruments6040071", "10.3390/instruments6040070", "10.3390/instruments6040068", "10.3390/instruments6040067", "10.3390/instruments6040065", "10.3390/instruments6040064", "10.3390/instruments6040063", "10.3390/instruments6040062", "10.3390/instruments6040060", "10.3390/instruments6040059", "10.3390/instruments6040058", "10.3390/instruments6040057", "10.3390/instruments6040055", "10.3390/instruments6040054", "10.3390/instruments6040053", "10.3390/instruments6040052", "10.3390/instruments6040051", "10.3390/instruments6040049", "10.3390/instruments6040048", "10.3390/instruments6040046", "10.3390/instruments6040045", "10.3390/instruments6040044", "10.3390/instruments6040043", "10.3390/instruments6030041", "10.3390/instruments6030040", "10.3390/instruments6030039", "10.3390/instruments6030037", "10.3390/instruments6030035", "10.3390/instruments6030034", "10.3390/instruments6030033", "10.3390/instruments6030032", "10.3390/instruments6030031", "10.3390/instruments6030030", "10.3390/instruments6030029", "10.3390/instruments6030028", "10.3390/instruments6030027", "10.3390/instruments6030025", "10.3390/instruments6040050", "10.3390/instruments6040047", "10.3390/instruments6030026"]


done = []
if jnl == 'proceedings':
    jnlfilename = 'mdpi_proc%s.%s_%s' % (volume, issue, cnum)
elif jnl == 'psf':
    jnlfilename = 'mdpi_psf%s.%s_%s' % (volume, issue, cnum)
else:
    reoldsyntax = re.compile('^([a-z]*\-\d+\-)(\d+).xml$')
    jnlfilename = '%s.%s' % (jnl, ejlmod3.stampoftoday())
    donepath = os.path.join(publisherpath, 'done', jnl)
    for voldir in os.listdir(donepath):
        for issuedir in os.listdir(os.path.join(donepath, voldir)):
            for articledir in os.listdir(os.path.join(donepath, voldir, issuedir)):
                for articlefile in os.listdir(os.path.join(donepath, voldir, issuedir, articledir)):
                    done.append(os.path.join(tmppath, voldir, issuedir, articledir, articlefile))
                    if reoldsyntax.search(articlefile):
                        iss = '%02i' % (int(re.sub('\D', '', issuedir)))
                        afn = reoldsyntax.sub(r'\1', articlefile) + iss + reoldsyntax.sub(r'-\2.xml', articlefile)
                        adn = afn[:-4]
                        done.append(os.path.join(tmppath, voldir, issuedir, adn, afn))
    print('already done:', len(done))


    
###clean formulas in tag
def cleanformulas(tag):
    #change html-tags into LaTeX
    for italic in tag.find_all('italic'):
        it = italic.text.strip()
        #appears within sub/sup :(
        #  italic.replace_with('$%s$' % (it))
        italic.replace_with(it)
    for sub in tag.find_all('sub'):
        st = sub.text.strip()
        sub.replace_with('$_{%s}$' % (st))
    for sup in tag.find_all('sup'):
        st = sup.text.strip()
        sup.replace_with('$^{%s}$' % (st))
    #handle MathML/LaTeX formulas
    for inlineformula in tag.find_all(['inline-formula', 'disp-formula']):
        mmls = inlineformula.find_all('mml:math')
        tms = inlineformula.find_all('tex-math')
        #if len(mmls) == 1:
        #    inlineformula.replace_with(mmls[0])
        if len(tms) == 1:
            for tm in tms:
                tmt = re.sub('  +', ' ', re.sub('[\n\t\r]', '', tm.text.strip()))
                tmt = re.sub('.*begin.document..(.*)..end.document.*', r'\1', tmt)
                inlineformula.replace_with(tmt)
        else:
            #print 'DECOMPOSE', inlineformula
            inlineformula.decompose()            
    output = tag.text.strip()
    #MML output = ''
    #MML for tt in tag.contents:
    #MML     output += unicode(tt)
    #unite subsequent LaTeX formulas
    output = re.sub('\$\$', '', output)
    return output

#quick check whether volume is to old
def quickcheck(jnl, vol):
    if jnl == 'particles' and vol < 4: #normal run
        return False
    elif jnl == 'sensors' and vol < 21: #normal run
        return False
    elif jnl == 'axioms' and vol < 10: #normal run ARTID
        return False
    elif jnl == 'mathematics' and vol < 9: #normal run
        return False
    elif jnl == 'symmetry' and vol < 13: #normal run ARTID
        return False
    elif jnl == 'galaxies' and vol < 9: #normal run
        return False
    elif jnl == 'condensedmatter' and vol < 6: #normal run
        return False
    elif jnl == 'applsci' and vol < 11: #k5crontab
        return False
    elif jnl == 'physics' and vol < 3: #normal run
        return False
    elif jnl == 'quantumrep' and vol < 3: #normal run ARTID?
        return False
    elif jnl == 'universe' and vol < 7: #normal run
        return False
    elif jnl == 'instruments' and vol < 5: #normal run ARTID
        return False
    elif jnl == 'entropy' and vol < 23: #normal run
        return False
    elif jnl == 'atoms' and vol < 9: #normal run
        return False
    elif jnl == 'information' and vol < 12: #normal run ARTID
        return False
    elif jnl == 'photonics' and vol < 8-2:#normal run
        return False
    
    elif jnl == 'foundations' and vol < 0: #normal run
        return False

    elif jnl == 'fractalfract' and vol < 5-2:#normal run
        return False
    elif jnl == 'nanomaterials' and vol < 11-2: #k5crontab
        return False

    else:
        return True


    
if not os.path.isdir(tmppath):
    os.system('mkdir %s' % (tmppath))
print('connect to ftp://download.mdpi.com') 
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None
srv = pysftp.Connection(host="download.mdpi.com", username="mdpi_public_ftp", password="j7kzfbf9RDiJnEuX", port=9922, cnopts=cnopts)
srv.cwd('MDPI_corpus')
srv.cwd(jnl)
if jnl in ['proceedings', 'psf']:
    iss = 'volume-%02i/%s-%02i-%02i.tar' % (int(volume), jnl, int(volume), int(issue))
    print('get %s from ftp://download.mdpi.com' % (iss))
    localfilename = '%s/%s' % (tmppath, re.sub('.*\/', '', iss))
    srv.get(iss, localfilename)
    issueslocal.append(localfilename)
else:
    issuesonserver = []
    for vol in srv.listdir():
        for iss in srv.listdir(vol):
            issuesonserver.append('%s/%s' % (vol, iss))
    issueslocal = []
    for iss in issuesonserver[-numberofissues:]:
        print('get %s from ftp://download.mdpi.com' % (iss))
        localfilename = '%s/%s' % (tmppath, re.sub('.*\/', '', iss))
        srv.get(iss, localfilename)
        issueslocal.append(localfilename)

for localfilename in issueslocal:
    print('read %s' % (localfilename))
    journalfeed = tarfile.open(localfilename, 'r')
    journalfeed.extractall(path=tmppath)#, numeric_owner=3770)
    journalfeed.close()


prerecs = []
for voldir in os.listdir(tmppath):
    if re.search('volume', voldir):
        for issdir in os.listdir(os.path.join(tmppath, voldir)):            
            for artdir in os.listdir(os.path.join(tmppath, voldir, issdir)):
                for artfile in os.listdir(os.path.join(tmppath, voldir, issdir, artdir)):
                    if not re.search('xml$', artfile):
                        continue
                    rec = {'jnl' : jnl.title(), 'tc' : 'P', 'keyw' : [], 'aff' : [], 'auts' : [],
                           'note' : [], 'refs' : [], 'col' : []}
                    rec['artfilename'] = os.path.join(tmppath, voldir, issdir, artdir, artfile)
                    if rec['artfilename'] in done:
                        print('   %s in done' % (artfile))
                        continue
                    rec['vol'] = re.sub('\D', '', voldir)
                    rec['iss'] = re.sub('\D', '', issdir)
                    if jnl == 'proceedings':
                        rec['jnl'] = 'MDPI Proc.'
                        rec['tc'] = 'C'
                        rec['cnum'] = cnum
                    elif jnl == 'psf':
                        rec['jnl'] = 'Phys.Sci.Forum'
                        rec['tc'] = 'C'
                        rec['cnum'] = cnum
                    elif jnl == 'condensedmatter':
                        rec['jnl'] = 'Condens.Mat.'
                    elif jnl == 'physics':
                        rec['jnl'] = 'MDPI Physics'
                    elif jnl == 'quantumrep':
                        rec['jnl'] = 'Quantum Rep.'
                    elif jnl == 'fractalfract':
                        rec['jnl'] = 'Fractal Fract.'
                    elif jnl == 'applsci':
                        rec['jnl'] = 'Appl.Sciences'
                    prerecs.append(rec)
    
recs = []
i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artfilename']], [len(recs)]])
    keepit = True
    inf = codecs.EncodedFile(codecs.open(rec['artfilename'], mode='rb'), 'utf8')
    article = BeautifulSoup(''.join(inf.readlines()), features="lxml")
    inf.close()
    for meta in article.find_all('article-meta'):
        #DOI
        for aid in meta.find_all('article-id', attrs = {'pub-id-type' : 'doi'}):
            rec['doi'] = aid.text.strip()
            #checkdone    
            if rec['doi'] in done and not rec['doi'] in missingpubnotes:
                print('  %s already in done'  % (rec['doi']))
                keepit = False
            #check conference
            if rec['doi'] in calor22:
                rec['tc'] = 'C'
                rec['cnum'] = 'C22-05-15.4'
        #date
        for pd in  meta.find_all('pub-date', attrs = {'pub-type' : 'epub'}):
            for year in pd.find_all('year'):
                rec['date'] = year.text.strip()
            for month in pd.find_all('month'):
                rec['date'] += '-' + month.text.strip()
            for day in pd.find_all('day'):
                rec['date'] += '-' + day.text.strip()
            #checkdate
            if rec['date'] < stampofstartdate and not rec['doi'] in missingpubnotes:
                print('  %s is older than %s' % (rec['date'], stampofstartdate))
                keepit = False
        #article type
        for ac in meta.find_all('article-categories'):
            for subj in ac.find_all('subject'):
                subjt = subj.text.strip()
                if re.search('[a-zA-Z]', subjt):
                    rec['note'].append(subjt)
                if subjt in ['Review']:
                    if not 'R' in rec['tc']:
                        rec['tc'] += 'R'
                elif subjt in ['Conference Report']:
                    rec['tc'] = 'C'
                elif subjt in ['Editorial']:
                    keepit = False
        if keepit:
            #title # xml:lang="en" ?
            for tg in meta.find_all('title-group'):
                for at in tg.find_all(['article-title', 'title']):
                    rec['tit'] = cleanformulas(at)
                for st in tg.find_all('subtitle'):
                    rec['tit'] += ': %s' % (cleanformulas(st))
            #year
            for pd in  meta.find_all('pub-date', attrs = {'pub-type' : 'collection'}):
                for year in pd.find_all('year'):
                    rec['year'] = year.text.strip()
            #volume
            for vol in meta.find_all('volume'):
                rec['vol'] = vol.text.strip()        
            #issue
            for iss in meta.find_all('issue'):
                rec['issue'] = iss.text.strip()
            #pages
            for p1 in meta.find_all('fpage'):
                rec['p1'] = p1.text.strip()
            for p2 in meta.find_all('lpage'):
                rec['p2'] = p2.text.strip()
            if not 'p1' in list(rec.keys()):
                for p1 in meta.find_all('elocation-id'):
                    rec['p1'] = p1.text.strip()
            #license
            for permissions in meta.find_all('permissions'):
                for licence in permissions.find_all('license', attrs = {'license-type' : 'open-access'}):
                    for el in licence.find_all('ext-link', attrs = {'ext-link-type' : 'uri'}):
                        if el.has_attr('xlink:href'):
                            rec['license'] = {'url' : el['xlink:href']}
            #keywords
            for kwg in meta.find_all('kwd-group'):
                for kw in kwg.find_all('kwd'):
                    rec['keyw'].append(kw.text.strip())         
            #abstract
            for abstract in meta.find_all('abstract'):
                rec['abs'] = ''
                for p in abstract.find_all('p'):
                    rec['abs'] += cleanformulas(p)
            #emails
            emails = {}
            for an in meta.find_all('author-notes'):
                for cor in an.find_all('corresp'):
                    for email in cor.find_all('email'):
                        emails[cor['id']] = email.text.strip()
            #affiliations
            for aff in meta.find_all('aff'):
                for label in aff.find_all(['label', 'email']):
                    label.decompose()
                afftext = aff.text.strip()
                if aff.has_attr('id'):
                    rec['aff'].append('%s= %s' % (aff['id'], re.sub('[\n\t\r]', ' ', afftext)))
                else:
                    rec['aff'].append('%s' % (re.sub('[\n\t\r]', ' ', afftext)))
            #authors and collaboration
            for contrib in meta.find_all('contrib', attrs = {'contrib-type' : 'author'}):
                #authors
                for name in contrib.find_all('name'):
                    for sn in name.find_all('surname'):
                        authorname = sn.text.strip()
                    for gn in name.find_all('given-names'):
                        authorname += ', %s' % (gn.text.strip())
                    #ORCID
                    for cid in contrib.find_all('contrib-id', attrs = {'contrib-id-type' : 'orcid'}):
                        authorname += re.sub('.*\/', ', ORCID:', cid.text.strip())
                    #Email
                    if not re.search('ORCID:', authorname):
                        for xref in contrib.find_all('xref', attrs = {'ref-type' : 'corresp'}):
                            if xref['rid'] in list(emails.keys()):
                                authorname += ', EMAIL:' + emails[xref['rid']]
                        if not re.search('EMAIL:', authorname):
                            for adr in contrib.find_all('address'):
                                for email in adr.find_all('email'):
                                    authorname += ', EMAIL:' + email.text.strip()
                    rec['auts'].append(authorname)
                    #Affiliation
                    for xref in contrib.find_all('xref', attrs = {'ref-type' : 'aff'}):
                        rec['auts'].append('=%s' % (xref['rid']))
                #collaboration
                for coll in contrib.find_all('collab'):
                    #safety check if authors are under collaboration
                    authorsundercoll = False
                    for bla in coll.find_all('contrib', attrs = {'contrib-type' : 'author'}):
                        authorsundercoll = True
                    if authorsundercoll:
                        for inst in coll.find_all('institution'):
                            rec['col'].append(inst.text.strip())
                    else:
                        for email in coll.find_all('email'):
                            email.decompose()
                        rec['col'].append(coll.text.strip())
            #references
            for rl in article.find_all('ref-list'):
                rec['refs'] = jatsreferences(rl)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
            #copy pdf
            pdffilename = re.sub('xml$', 'pdf', rec['artfilename'])
            if os.path.isfile(pdffilename):
                doi1 = re.sub('[\(\)\/]', '_', rec['doi'])                
                os.system('mv %s %s/%s.pdf' % (pdffilename, pdfpath, doi1))
            print('    copied pdf file')                          

#write to disc
numofchunks = (len(recs)-1) // chunksize + 1
for chunk in range(numofchunks):
    xmlfilename = '%s-%02i_of_%i.xml' % (jnlfilename, chunk + 1, numofchunks)
    ejlmod3.writenewXML(recs[chunk*chunksize:(chunk+1)*chunksize], publisher, xmlfilename)

#cleanup
for rec in prerecs:
    donefilename = re.sub('\/tmp', '\/done\/'+jnl, rec['artfilename'])
    targetdir = re.sub('(.*)\/.*', r'\1', donefilename)
    if not os.path.isdir(targetdir):
        os.system('mkdir -p '+targetdir)
    if not os.path.isdir(donefilename):
        os.system('mv %s %s' % (rec['artfilename'], donefilename))
print('moved %i xml-files to done' % (len(prerecs)))
os.system('rm -rf %s' % (tmppath))
            
