#digest feeds from World Scientific Publishig
import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import zipfile
from ftplib import FTP
import undetected_chromedriver as uc



tmpdir = '/tmp'
wspdir = '/afs/desy.de/group/library/publisherdata/wsp'
feeddir = '/afs/desy.de/group/library/preprints/incoming/WSP'
publisher = 'WSP'


#regular expressions for reference extraction
regexparx = re.compile('.*org\/abs\/')
regexpdoi = re.compile('.*genRefLink.*\'(10\.\d\d.*)\'.*')
regexpdoihtml = re.compile('%2(52)?F')
regexpdoihtml2 = re.compile('%2(53)?A') #:
regexpdoihtml3 = re.compile('%2(52)?8') #(
regexpdoihtml4 = re.compile('%2(52)?9') #)
regexpdoihtml5 = re.compile('%2(53)?C') #<
regexpdoihtml6 = re.compile('%2(53)?E') #>
regexpabs = re.compile('.*worldscientific.com\/doi\/(10.*?)\'.*')
regexpcr = re.compile('[\n\t\r]')
regexpdoi2 = re.compile('.*servlet.*key=(10\.\d\d.*).*')


options = uc.ChromeOptions()
#options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

def getreferencesfromweb(doi):
    link = 'http://www.worldscientific.com/doi/ref/%s' % (doi)
    link = 'http://www.worldscientific.com/doi/%s' % (doi)
    print('   ', link)
    driver.get(link)
    refpage = BeautifulSoup(driver.page_source, features="lxml")
    uls = refpage.body.find_all('ul', attrs = {'class' : 'rlist separator'})
    refs = []
    for ul in uls:
        print('      %i references' % (len(ul)))
        for li in ul.find_all('li'):
            for a in li.find_all('a'):
                if a.has_attr('href'):
                    #arXiv-links
                    if a.text in ['arXiv', 'arxiv', 'ARXIV']:
                        rn = regexparx.sub(',  arXiv: ', a['href']) + ', '
                        a.replace_with(rn)
                    #WSP-DOI
                    elif regexpabs.search(a['href']):
                        rdoi = regexpabs.sub(r', DOI: \1 , ', a['href'])
                        a.replace_with(rdoi)
                    #Crossref
                    elif regexpdoi2.search(a['href']):
                        rdoi = regexpdoi2.sub(r', DOI: \1 , ', a['href'])
                        a.replace_with(rdoi)
            #Crossref-DOI
            for script in li.find_all('script'):
                if script.contents:
                    scriptt = script.contents[0].strip()
                    if regexpdoi.search(scriptt):
                        rdoi = regexpdoi.sub(r', DOI: \1 , ', scriptt)
                        rdoi = regexpdoihtml.sub('/', rdoi)
                        rdoi = regexpdoihtml2.sub(':', rdoi)
                        rdoi = regexpdoihtml3.sub(')', rdoi)
                        rdoi = regexpdoihtml4.sub('(', rdoi)
                        rdoi = regexpdoihtml5.sub('<', rdoi)
                        rdoi = regexpdoihtml6.sub('>', rdoi)
                        script.replace_with(rdoi)
                    else:
                        script.replace_with(' ')
            #refextract
            reftext = regexpcr.sub(' ', li.text.strip())
            #print '     ', reftext
            refs.append([('x', reftext)])
    time.sleep(50)
    return refs





#mapping from WSP-xml to ejlmod2-format
def concert(rawrecs):
    recs = []
    print('found %i xml files' % (len(rawrecs)))
    for (k, rawrec) in enumerate(rawrecs):
        xmlrec = open(rawrec, mode='r')
        wsprecord = BeautifulSoup(''.join(xmlrec.readlines()), features="lxml")
        xmlrec.close()
        rec = {'tc' : 'P', 'note' : [], 'autaff' : [], 'keyw' : []}
        #ignore references in metadata delivery
        for reflist in wsprecord.find_all('ref-list'):
            for ref in reflist.find_all('ref'):
                x = re.sub('[\n\t]', ' ', ref.text.strip())
                #print '\n\n--->', x
            reflist.replace_with('')
        #Journal
        for jt in wsprecord.find_all('journal-title'):
            rec['jnl'] = jt.text
            if jt.text == 'International Journal of Modern Physics: Conference Series':
                rec['tc'] = 'C'
        if 'jnl' not in rec:
            rec['jnl'] = 'BOOK'
            rec['tc'] = 'S'
            if re.search('fmatter', rawrec):
                rec['tc'] = 'B'
                rec['note'].append('Hauptaufnahme')
        for series in wsprecord.find_all('series'):
            if re.search('^Advanced series on directions in high energy physics', series.text):
                rec['jnl'] = 'Adv.Ser.Direct.High Energy Phys.'
                if re.search('\d', series.text):
                    rec['vol'] = re.sub('.*?(\d+).*', r'\1', series.text.strip())
        else:
            for volume in wsprecord.find_all('volume'):
                rec['vol'] = volume.text
            for issue in wsprecord.find_all('issue'):
                rec['issue'] = issue.text
        #book without individual records
        rawrecparts = re.split('\/', rawrec)
        if len(rawrecparts) > 3 and (rawrecparts[-2] == rawrecparts[-3]):
            rec['note'].append('no metatdata for individual chapters!') 
            rec['tc'] = 'B'
        for p1 in wsprecord.find_all('fpage'):
            rec['p1'] = p1.text
        for p2 in wsprecord.find_all('lpage'):
            rec['p2'] = p2.text
        for eid in wsprecord.find_all('elocation-id'):
            rec['p1'] = eid.text
        for pc in wsprecord.find_all('page-count'):
            rec['pages'] = pc['count']
        #title
        for title in wsprecord.find_all('article-title'):
            rec['tit'] = title.text
        if 'tit' not in rec:
            for title in wsprecord.find_all('title'):
                rec['tit'] = title.text
        if rec['tc'] == 'B':
            for title in wsprecord.find_all('book-title'):
                rec['tit'] = title.text
        #DOI
        if rec['tc'] == 'B':
            for bid in wsprecord.find_all('book-id', attrs = {'pub-id-type' : 'doi'}):
                rec['doi'] = bid.text
                ejlmod3.printprogress('-', [[k+1, len(rawrecs)], [rec['doi']]])
        else:
            for aid in wsprecord.find_all(['article-id', 'book-part-id'], attrs = {'pub-id-type' : 'doi'}):
                rec['doi'] = aid.text
                ejlmod3.printprogress('-', [[k+1, len(rawrecs)], [rec['doi']]])
        #Note
        for sg in wsprecord.find_all('subj-group', attrs = {'subj-group-type' : 'heading'}):
            for s in sg.find_all('subject'):
                rec['note'].append(s.text)      
        #PACS
        for sg in wsprecord.find_all('subj-group', attrs = {'subj-group-type' : 'PACS'}):
            rec['pacs'] = []
            for s in sg.find_all('subject'):
                rec['pacs'].append(s.text)      
        #PACS
        #affiliations
        affdict = {}
        for aff in wsprecord.find_all('aff'):
            for sup in aff.find_all('sup'):
                sup.replace_with('')
            if aff.has_attr('id'):
                affdict[aff['id']] = re.sub('[\n\t\r]', ' ', aff.text.strip())
        #authors
        for c in wsprecord.find_all('contrib', attrs = {'contrib-type' : 'author'}):
            author = ''
            for sn in c.find_all('string-name'):
                author = ''
                for surn in sn.find_all('surname'):
                    author += surn.text
                author += ', '
                for givenn in sn.find_all('given-names'):
                    author += givenn.text
            #no emails
            autaff = [author]
            for aff in c.find_all('aff'):
                autaff.append(aff.text)
            for xref in c.find_all('xref', attrs = {'ref-type' : 'aff'}):
                if xref['rid'] in affdict:
                    autaff.append(affdict[xref['rid']])
            rec['autaff'].append(autaff)
        if not rec['autaff']:
            for c in wsprecord.find_all('contrib', attrs = {'contrib-type' : 'editor'}):                
                author = ''
                for sn in c.find_all('string-name'):
                    author = ''
                    for surn in sn.find_all('surname'):
                        author += surn.text
                    author += ', '
                    for givenn in sn.find_all('given-names'):
                        author += givenn.text + ' (ed.)'
                #no emails
                autaff = [author]
                for aff in c.find_all('aff'):
                    autaff.append(aff.text)
                for xref in c.find_all('xref', attrs = {'ref-type' : 'aff'}):
                    if xref['rid'] in affdict:
                        autaff.append(affdict[xref['rid']])
                rec['autaff'].append(autaff)
        if not rec['autaff']:
            for c in wsprecord.find_all('contrib'):
                author = ''
                for sn in c.find_all('string-name'):
                    author = ''
                    for surn in sn.find_all('surname'):
                        author += surn.text
                    author += ', '
                    for givenn in sn.find_all('given-names'):
                        author += givenn.text 
                #no emails
                autaff = [author]
                for aff in c.find_all('aff'):
                    autaff.append(aff.text)
                for xref in c.find_all('xref', attrs = {'ref-type' : 'aff'}):
                    if xref['rid'] in affdict:
                        autaff.append(affdict[xref['rid']])
                rec['autaff'].append(autaff)
        #year
        for date in wsprecord.find_all('pub-date', attrs = {'pub-type' : 'ppub'}):
            for year in date.find_all('year'):
                rec['year'] = year.text.strip()
        if not 'year' in list(rec.keys()):
            for cry in wsprecord.find_all('copyright-year'):
                if cry.text.strip():
                    rec['year'] = cry.text.strip()
        #date
        for date in wsprecord.find_all('date', attrs = {'date-type' : 'published'}):
            try:
                rec['date'] = '%s-%s-%s' % (date.year.text, date.month.text, date.day.text)
            except:
                print(' (date.year.text, date.month.text, date.day.text) failed')
            if not 'date' in list(rec.keys()):
                try:
                    rec['date'] = '%s-%s' % (date.year.text, date.month.text)
                except:
                    print(' (date.year.text, date.month.text) failed')
            if not 'date' in list(rec.keys()):
                try:
                    rec['date'] = date.year.text
                except:
                    print(' (date.year.text) failed')
            if not 'date' in list(rec.keys()):
                for sd in date.find_all('string-date'):
                    if re.search(' [12]\d\d\d', sd.text):
                        rec['date'] = re.sub('.* ([12]\d\d\d).*', r'\1', sd.text)
        if 'date' not in rec:
            for date in wsprecord.find_all('pub-date', attrs = {'pub-type' : 'ppub'}):
                try:
                    rec['date'] = '%s-%s-%s' % (date.year.text, date.month.text, date.day.text)
                except:
                    try:
                        rec['date'] = '%s-%s' % (date.year.text, date.month.text)
                    except:
                        rec['date'] = date.year.text
        if 'date' not in rec:
            for cry in wsprecord.find_all('copyright-year'):
                if cry.text.strip():
                    rec['date'] = cry.text.strip()
        if 'date' not in rec:
            for date in wsprecord.find_all('pub-date'):
                try:
                    rec['date'] = '%s-%s-%s' % (date.year.text, date.month.text, date.day.text)
                except:
                    try:
                        rec['date'] = '%s-%s' % (date.year.text, date.month.text)
                    except:
                        rec['date'] = date.year.text
        #license
        for lic in wsprecord.find_all('license'):
            lict = lic.text.strip()
            if re.search('CC\-BY', lict):
                stat = re.sub('.*(CC.*\d).*', r'\1', lict)
                stat = re.sub('\)', '', stat)
                stat = re.sub(' ', '-', stat)
                rec['licence'] = {'statement' : stat}
                rec['FFT'] = 'http://www.worldscientific.com/doi/pdf/' + rec['doi']
        #abstract
        for abstract in wsprecord.find_all('abstract'):
            rec['abs'] = ''
            for p in abstract.find_all('p'):
                rec['abs'] += p.text + ' '              
        #keywords
        for keywgrp in wsprecord.find_all('kwd-group'):
            for keyw in keywgrp.find_all('kwd'):
                rec['keyw'].append(keyw.text)
        #num of pages
        for pagecount in wsprecord.find_all('page-count'):
            rec['pages'] = pagecount['count']
        #references
        if 'refs' not in rec:
#            try:
                if not rec['tc'] in ['B', 'S']:
                    rec['refs'] = getreferencesfromweb(rec['doi'])
                #print 'referenzen ausgeschaltet'
#            except:
#                print('could not get references from the web')
        #OF?
        if 'no metatdata for individual chapters!' in rec['note']:
            rec['note'].append(rec['date'])
        else:
            recs.append(rec)                                   
    return recs


#download metadata feeds
os.chdir(feeddir)
done = os.listdir(os.path.join(wspdir, 'done'))
print('%i files in done' % (len(done)))
filestodo = []

ftp = FTP("ftp.wspc.com.sg")
ftp.login("XXX", "XXX")
ftp.cwd('journals')
files = ftp.nlst()  #list of the zip.files
numofskipped = 0
for filename in files:
    if filename in done:
        #print 'skip "%s"' % (filename)
        numofskipped += 1
    else:
        if os.path.isfile(os.path.join(feeddir, filename)):
            print('found "%s"' % (filename))
        else:
            print('download "%s"' % (filename))
            f2 = open(filename,"wb")
            ftp.retrbinary("RETR " + filename,f2.write)
            f2.close()
        if re.search('.zip$', filename):
            filestodo.append(filename)

print('skipped %i zip-files, found %i new WSP zip-files to digest' % (numofskipped, len(filestodo)))

#unzip new files
for zipdatei in filestodo:
    try:
        zfile = zipfile.ZipFile(os.path.join(feeddir, zipdatei))
        zfile.extractall(wspdir)
    except:
        print("%s is not a zip file" % (zipdatei))
        sys.exit(0)

#checking extracted zip-files
folders = os.listdir(wspdir)
for (k, datei) in enumerate(folders):
    ordner = os.path.join(wspdir, datei)
    if not os.path.isdir(ordner): 
        continue
    elif datei in ['done']:
        continue
    jnlfilename = 'WSP__'+datei
    #jnlfilename = datei
    ejlmod3.printprogress('=', [[k+1, len(folders)], [jnlfilename]])
    rawrecs = []
    for datei2 in os.listdir(ordner):
        if not datei == datei2:
            ordner2 = os.path.join(ordner, datei2)
            if not re.search('bmatter', datei2):
                for datei3 in os.listdir(ordner2):
                    rawrecs.append(os.path.join(ordner2, datei3))
    print(rawrecs)
    if not rawrecs:
        for datei2 in os.listdir(ordner):
            ordner2 = os.path.join(ordner, datei2)
            if not re.search('bmatter', datei2):
                for datei3 in os.listdir(ordner2):
                    rawrecs.append(os.path.join(ordner2, datei3))    
    if rawrecs:
        recs = concert(rawrecs)
        if len(recs) > 0:
            ejlmod3.writenewXML(recs, publisher, jnlfilename)
        else:
            print("no records for %s" % (jnlfilename))

#move to 'done'
for zipdatei in filestodo:
    os.system('cp %s/%s %s/done/' % (feeddir, zipdatei, wspdir))

#clean WSP directory
for datei in os.listdir(wspdir):
    ordner = os.path.join(wspdir, datei)
    if not datei in ['done']:
        os.system('rm -rf %s' % (ordner))
    
