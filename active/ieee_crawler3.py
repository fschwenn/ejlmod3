# -*- coding: utf-8 -*-
#program to harvest IEEE-journals
# FS 2022-08-20

import getopt
import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from multiprocessing import Process
from multiprocessing import Manager
import codecs

articlesperpage = 100
skipalreadyharvested = True

host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    tmpdir = '/home/schwenn/tmp'
else:
    options = uc.ChromeOptions()
    options.headless=True
#    options.binary_location='/usr/bin/chromium-browser'
    options.add_argument('--headless')
    #chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    chromeversion = 108
    driver = uc.Chrome(version_main=chromeversion, options=options)
    tmpdir = '/tmp'
#useragent for wget
useragent = ' --user-agent "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0" '

ppdfpath = '/afs/desy.de/group/library/publisherdata/pdf'
dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = 'ieee*doki'
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s %s/%i/*%s| grep '^I.*http' | sed 's/.*https\?/http/' | sed 's/\-\-$//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc, dokidir, ejlmod3.year(), filenametrunc))))
    filenametrunc = 'IEEE*doki'
    print('%i records in backup' % (len(alreadyharvested)))
    alreadyharvested += list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s %s/%i/*%s| grep '^I.*http' | sed 's/.*https\?/http/' | sed 's/\-\-$//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc, dokidir, ejlmod3.year(), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))
alreadyharvested.append('http://ieeexplore.ieee.org/document/10189126/')
alreadyharvested.append('http://ieeexplore.ieee.org/document/10188200/')

def meta_with_name(tag):
    return tag.name == 'meta' and tag.has_attr('name')
    
def fsunwrap(tag):
    try: 
        for i in tag.find_all('i'):
            cont = i.string
            i.replace_with(cont)
    except:
        print('fsunwrap-i-problem')
    try: 
        for b in tag.find_all('b'):
            cont = b.string
            b.replace_with(cont)
    except:
        print('fsunwrap-b-problem')
    try: 
        for sup in tag.find_all('sup'):
            cont = sup.string
            sup.replace_with('^'+cont)
    except:
         'fsunwrap-sup-problem'
    try: 
        for sub in tag.find_all('sub'):
            cont = sub.string
            sub.replace_with('_'+cont)
    except:
        print('fsunwrap-sub-problem')
    try: 
        for form in tag.find_all('formula',attrs={'formulatype': 'inline'}):
            form.replace_with(' [FORMULA] ')
    except:
        print('fsunwrap-form-problem')
    return tag

def referencetostring(reference):
    refstring = re.sub('\s+',' ',fsunwrap(reference).prettify())
    refstring = re.sub('<li> *(.*) *<br.*',r'\1',refstring)
    for a in reference.find_all('a'):
        if a.has_attr('href') and re.search('dx.doi.org\/',a['href']):
            refstring += ', doi: %s' % (re.sub('.*dx.doi.org\/','',a['href']))
    return refstring

def translatejnlname(ieeename):
    if ieeename in ["Applied Superconductivity, IEEE Transactions on", "IEEE Transactions on Applied Superconductivity"]:
        jnlname = 'IEEE Trans.Appl.Supercond.'
    elif ieeename in ["Nuclear Science, IEEE Transactions on",  "IEEE Transactions on Nuclear Science"]:
        jnlname = 'IEEE Trans.Nucl.Sci.'
    elif ieeename in ["IEEE Xplore: Magnetics, IEEE Transactions on", "Magnetics, IEEE Transactions on", 'IEEE Transactions on Magnetics']:
        jnlname = 'IEEE Trans.Magnetics'

    elif ieeename in ["IEEE Xplore: Microwave Theory and Techniques, IEEE Transactions on", "IEEE Xplore: IEEE Transactions on Microwave Theory and Techniques"]:
        jnlname = 'IEEE Trans.Microwave Theor.Tech.'
    elif ieeename in ["IEEE Xplore: Plasma Science, IEEE Transactions on", "IEEE Transactions on Plasma Science"]:
        jnlname = 'IEEE Trans.Plasma Sci.'
    elif ieeename in ["IEEE Xplore: Quantum Electronics, IEEE Journal of", "IEEE Xplore: IEEE Journal of Quantum Electronics"]:
        jnlname = 'IEEE J.Quant.Electron.'
    elif ieeename in ["Instrumentation and Measurement, IEEE Transactions on", "IEEE Xplore: IEEE Transactions on Instrumentation and Measurement", "IEEE Transactions on Instrumentation and Measurement"]:
        jnlname = 'IEEE Trans.Instrum.Measur.'
    elif re.search('^IEEE Xplore . Nuclear Science Symposium Conference Record', ieeename):
        jnlname = 'IEEE Nucl.Sci.Symp.Conf.Rec.'
    elif ieeename in ["Journal of Lightwave Technology"]:
        jnlname = 'J.Lightwave Tech.'
    elif ieeename in ["IEEE Transactions on Microwave Theory and Techniques"]:
        jnlname = 'IEEE Trans.Microwave Theor.Tech.'
    elif ieeename in ["Instrumentation & Measurement Magazine, IEEE", "IEEE Instrumentation & Measurement Magazine"]:
        jnlname = 'IEEE Instrum.Measur.Mag.'
        tc = 'I'
    elif ieeename in ['IEEE Sensors Journal']:
        jnlname = 'IEEE Sensors J.'
    elif ieeename in ['IEEE Transactions on Image Processing']:
        jnlname = 'IEEE Trans.Image Process.'
    elif ieeename in ['Computing in Science & Engineering']:
        jnlname = 'Comput.Sci.Eng.'
    elif ieeename in ['IEEE Transactions on Circuits and Systems I: Regular Papers']:
        jnlname = 'IEEE Trans.Circuits Theor.'
    elif ieeename in ['IEEE Transactions on Information Theory']:
        jnlname = 'IEEE Trans.Info.Theor.'
    elif ieeename in ['IEEE Transactions on Computers']:
        jnlname = 'IEEE Trans.Comput.'
    elif ieeename in ['Journal on Selected Areas in Information Theory (JSAIT)', 'IEEE Journal on Selected Areas in Information Theory']:
        jnlname = 'IEEE J.Sel.Areas Inf.Theory'
    elif ieeename in ['IEEE Journal of Selected Topics in Quantum Electronics']:
        jnlname = 'IEEE J.Sel.Top.Quant.Electron.'
    elif ieeename in ['IEEE Communications Letters']:
        jnlname = 'IEEE Commun.Lett.'
    elif ieeename in ['IEEE Electron Device Letters']:
        jnlname = 'IEEE Electron.Dev.Lett.'
    elif ieeename in ['IEEE Transactions on Electron Devices']:
        jnlname = 'IEEE Trans.Electron.Dev.'
    elif ieeename in ['IEEE Transactions on Automatic Control']:
        jnlname = 'IEEE Trans.Automatic Control'
    elif ieeename in ['IEEE Journal on Selected Areas in Communications']:
        jnlname = 'IEEE J.Sel.Areas Commun.'
    elif ieeename in ['IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems']:
        jnlname = 'IEEE Trans.Comput.Aided Design Integr.Circuits Syst.'
    elif ieeename in ['IEEE Transactions on Quantum Engineering']:
        jnlname = 'IEEE Trans.Quantum Eng.'
    elif ieeename in ['IEEE Transactions on Nanotechnology']:
        jnlname = 'IEEE Trans.Nanotechnol.'
    elif ieeename in ['IEEE Journal of Quantum Electronics']:
        jnlname = 'IEEE J.Quant.Electron.'
    elif ieeename in ['IEEE Access']:
        jnlname = 'IEEE Access'
    elif ieeename in ['IEEE Journal of Solid-State Circuits']:
        jnlname = 'IEEE J.Solid State Circuits'
    elif ieeename in ["IEEE Symposium Conference Record Nuclear Science 2004.",
                      "IEEE Nuclear Science Symposium Conference Record, 2005"]:
        jnlname = 'BOOK'
        tc = 'C'
    else:
        print('unknown journal', ieeename)
        sys.exit(0)
    return jnlname

#get references
refwait = 300
def addreferences(refsdict, articlelink):
    global refwait
    refsdict[articlelink] = []
    arefs = []
    reffilename = '%s/ieee.%s.refs' % (tmpdir, re.sub('\W', '', re.sub('https', 'http', articlelink)))
    print('    ... from %s%s' % (articlelink, 'references'))
    needtowait = True
    try:
        driver.get(articlelink + 'references')
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'stats-reference-link-googleScholar')))
        refpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(40)
        needtowait = False
    except:
        print(' wait %i seconds' % (refwait))
        time.sleep(refwait)
        driver.get(articlelink + 'references')
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'stats-reference-link-googleScholar')))
        refpage = BeautifulSoup(driver.page_source, features="lxml")
    if needtowait:
        refwait *= 2
    else:
        refwait = 300            
    reffile = codecs.open(reffilename, mode='wb', encoding='utf8')
    for div in refpage.find_all('div', attrs = {'class' : 'reference-container'}):
        for span in div.find_all('span', attrs = {'class' : 'number'}):
            for b in span.find_all('b'):
                refnumber = re.sub('\.', '', span.text.strip())
                span.replace_with('[%s] ' % (refnumber))
        for a in div.find_all('a', attrs = {'class' : 'stats-reference-link-crossRef'}):
            rdoi = re.sub('.*doi.org\/(10.*)', r'\1', a['href'])
            a.replace_with(', DOI: %s' % (rdoi))
        for a in div.find_all('a', attrs = {'class' : 'stats-reference-link-googleScholar'}):
            a.replace_with('')
        ref = re.sub('[\n\t]', ' ', div.text.strip())
        ref = re.sub('  +', ' ', ref)
        if not ref in arefs:
            refsdict[articlelink].append([('x', ref)])
            arefs.append(ref)
            reffile.write(ref)
            reffile.write('\n')
    reffile.close()
    print('  found %i references' % (len(arefs)))
    time.sleep(5)

    


def ieee(number):
    manager = Manager()
    refsdict = manager.dict()
    urltrunc = "https://ieeexplore.ieee.org"
    #get name of journal
    if number[0] in ['C', 'N']: 
        #toclink = "/xpl/mostRecentIssue.jsp?punumber=%s&rowsPerPage=2000" % (number[1:])        
        toclink = "/xpl/conhome/%s/proceeding?rowsPerPage=%i" % (number[1:], articlesperpage)
        tc = 'C'
        jnlname = 'IEEE Nucl.Sci.Symp.Conf.Rec.'
        jnlname = 'BOOK'
    else:
        if number[0] == 'Q':
            toclink = "/xpl/tocresult.jsp?isnumber=%s&rowsPerPage=%i&searchWithin=quantum" % (number[1:], articlesperpage)
        else:
            toclink = "/xpl/tocresult.jsp?isnumber=%s&rowsPerPage=%i" % (number, articlesperpage)
        tc = 'P'
        
    articlelinks = []
    gotallarticles = False
    allarticlelinks = []
    notproperarticles = 0
    numberofarticles = 1000000
    i = 0 #XYZ
    while not gotallarticles:
        i += 1
        pagecommand = '&pageNumber=%i' % (i)
        print('getting TOC from %s%s%s' % (urltrunc, toclink, pagecommand))        
        try:
            driver.get(urltrunc + toclink + pagecommand)
            #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'icon-pdf')))
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'result-item-title')))
        except:
            print(' wait a minute')
            time.sleep(60)
            driver.get(urltrunc + toclink + pagecommand)
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'global-content-wrapper')))
        #click to accept cookies
        if i == 1:
            try:
                time.sleep(1)
                #driver.find_element_by_css_selector('.cc-btn.cc-dismiss').click()

                driver.find_element(by=By.CSS_SELECTOR, value='.cc-btn.cc-dismiss').click()
                
            except:
                print("\033[0;91mCould not click .cc-btn.cc-dismiss\033[0m")
        time.sleep(3)
        page = BeautifulSoup(driver.page_source, features="lxml")
        if i == 1:
            for div in page.body.find_all('div', attrs = {'class' : 'Dashboard-header'}):
                divt = re.sub('[\n\t\r]', ' ', div.text.strip())
                divt = re.sub(',', '', divt)
                numberofarticles = int(re.sub('.* of +(\d+).*', r'\1', divt))
        #get links to individual articles
        articlelinks = []
        resultitems = page.body.find_all('h2', attrs = {'class' : 'result-item-title'})
        print('   %i potential items' % (len(resultitems)))
        for headline in resultitems:
            links = headline.find_all('a')
            if links:
                for a in links:
                    if a.text.strip() in ['Title Page I', 'Title Page II',
                                          'Title Page III', 'Title Page IV',
                                          'Copyright', 'Table of Contents',
                                          'Message from the AI4I 2022 General Co-Chairs',
                                          'Message from the AI4I 2022 Program Co-Chairs',
                                          'Program', 'Welcome Message', 'Advance Program']:
                        notproperarticles += 1
                    else:
                        #print a
                        #if a.text == 'View more':
                        link = a['href']
                        if not link in ['/document/8733895/']:
                            articlelinks.append(urltrunc+link)
            else:
                #print ' not an article: %s' % (headline.text.strip())
                notproperarticles += 1
        if articlelinks:
            allarticlelinks += articlelinks
            print('   %i article links of %i so far (+ %i not proper articles)' % (len(allarticlelinks), numberofarticles, notproperarticles))
            if len(allarticlelinks) + notproperarticles >= numberofarticles:
                gotallarticles = True
            elif len(resultitems) < articlesperpage:
                gotallarticles = True                
        else:
            break
        time.sleep(10)
    
    print('found %i article links' % (len(allarticlelinks)))
#    if not allarticlelinks:
#        print page
    recs = []
    i = 0
    iref = 1
    jnlname = False
    for articlelink in allarticlelinks:
        i += 1
        if (iref % 45) == 0:
            print('\n   [[[ special pause for not to be blocked ]]]\n')
            time.sleep(180)
            iref += 1
        hasreferencesection = False
        ejlmod3.printprogress('-', [[i, len(allarticlelinks)], [articlelink], [len(recs)]])
        if articlelink in alreadyharvested or re.sub('https', 'http', articlelink) in alreadyharvested:
            print('   already in backup')
            continue
        #rec['note'] = ['Konferenz ?']
        artfilename = '%s/ieee_%s.%s' % (tmpdir, number, re.sub('https', 'http', re.sub('\W', '', articlelink)))
        if not os.path.isfile(artfilename):
            time.sleep(20)
            try:
                os.system("wget -T 300 -t 3 -q -O %s %s" % (artfilename, articlelink))
            except:
                print("retry in 300 seconds")
                time.sleep(300)
                os.system("wget -T 300 -t 3 -q -O %s %s" % (artfilename, articlelink))
        inf = open(artfilename, 'r')
        articlepage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
        inf.close()
        rec = {'keyw' : [], 'autaff' : [], 'note' : [articlelink]}
        #rec['fc'] = 'kc'
        #metadata now in javascript
        for script in articlepage.find_all('script', attrs = {'type' : 'text/javascript'}):
            #if re.search('global.document.metadata', script.text):
            if script.contents and len(script.contents):
                if re.search('[gG]lobal.document.metadata', script.contents[0]):
                    gdm = re.sub('[\n\t]', '', script.contents[0]).strip()
                    gdm = re.sub('.*[gG]lobal.document.metadata=(\{.*\}).*', r'\1', gdm)
                    gdm = json.loads(gdm)
        if 'sections' in gdm:
            if 'references' in gdm['sections']:
                if gdm['sections']['references'] in ['true', 'True']:
                    hasreferencesection = True
        if 'publicationTitle' in gdm:
            if number[0] in ['C', 'N']:
                jnlname = 'BOOK'
                tc = 'C'
            else:
                jnlname = translatejnlname(gdm['publicationTitle'])
                if jnlname == 'IEEE Instrum.Measur.Mag.':
                    tc = 'I'
                elif jnlname == 'BOOK':
                    tc = 'C'
            rec['jnl'] = jnlname
        if 'authors' in gdm:
            for author in gdm['authors']:
                autaff = [author['name']]
                if 'affiliation' in author:
                    autaff += author['affiliation']
                if 'orcid' in author:
                    autaff.append('ORCID:'+author['orcid'])
                rec['autaff'].append(autaff)
        if number[0] != 'N':
            if jnlname in ['IEEE Trans.Magnetics', 'IEEE Trans.Appl.Supercond.', 'IEEE J.Sel.Top.Quant.Electron.',
                           'IEEE Trans.Instrum.Measur.', 'IEEE J.Quant.Electron.']:
                if 'externalId' in gdm:
                    rec['p1'] = gdm['externalId']
                elif 'articleNumber' in gdm:
                    rec['p1'] = gdm['articleNumber']
                else:
                    rec['p1'] = gdm['startPage']
                    rec['p2'] = gdm['endPage']
            else:
                if 'endPage' in gdm:
                    rec['p1'] = gdm['startPage']
                    rec['p2'] = gdm['endPage']
                elif 'externalId' in gdm:
                    rec['p1'] = gdm['externalId']
                else:
                    rec['p1'] = gdm['articleNumber']
        rec['tit'] = gdm['formulaStrippedArticleTitle']
        if 'abstract' in gdm:
            rec['abs'] = gdm['abstract']
        ## mistake in metadata
        if re.search('\d+ pp', gdm['startPage']):
            rec['pages'] = re.sub(' .*', '', gdm['startPage'])
            if number[0] != 'N':
                rec['p1'] = str(int(gdm['endPage']) - int(rec['pages']) + 1)            
        else:
            try:
                rec['pages'] = int(re.sub(' .*', '', gdm['endPage'])) - int(gdm['startPage']) + 1
            except:
                pass
        if 'doi' in gdm:
            rec['doi'] = gdm['doi']
        else:
            rec['doi'] = '30.3000/ieee_%s_%06i' % (number, i)
            rec['link'] = articlelink
        if 'isFreeDocument' in gdm and gdm['isFreeDocument']:
            rec['pdf_url'] = urltrunc + gdm['pdfPath']
            rec['pdf_url'] = urltrunc + re.sub('iel7', 'ielx7', gdm['pdfPath'])
        if 'keywords' in gdm:
            for kws in gdm['keywords']:
                for kw in kws['kwd']:
                    if not kw in rec['keyw']:
                        rec['keyw'].append(kw)
        try:
            rec['date'] = gdm['journalDisplayDateOfPublication']
        except:
            rec['date'] = gdm['publicationDate']
        rec['year'] = rec['date'][-4:]
        if 'issue' in gdm:
            rec['issue'] = gdm['issue']
            rec['issue'] = re.sub('(\d+): .*', r'\1', rec['issue'])
        if 'volume' in gdm:
            rec['vol'] = gdm['volume']
        rec['tc'] = tc
        if gdm['isConference']:
            rec['tc'] = 'C'
            rec['note'].append(gdm['publicationTitle'])
        if len(args) > 1:
            rec['tc'] = 'C'
            if re.search('^C\d\d\-\d\d\-\d\d', args[1]):
                rec['cnum'] = args[1]
                if len(args) > 2:
                    rec['fc'] = args[2]
            elif not args[1] in rec['note']:
                rec['note'].append(args[1])
        #references
        if hasreferencesection:
                refilename = '%s/ieee.%s.refs' % (tmpdir, re.sub('https?', 'http', re.sub('\W', '', articlelink)))
                if not os.path.isfile(refilename) and host == 'l00schwenn':                    
                    iref += 1
                    print('  try to get references since %s not found' % (refilename))
                    action_process = Process(target=addreferences, args=(refsdict, articlelink))
                    action_process.start()
                    #action_process.join(timeout=5)
                    action_process.join(100)
                    if action_process.is_alive():
                        action_process.terminate()
                        action_process.join()
                        print('  killed reference extraction')
                    else:
                        print('  finished reference extraction')
                        #print refsdict[articlelink]
                if os.path.isfile(refilename):
                    reffile = codecs.EncodedFile(codecs.open(refilename, mode='rb'), 'utf8')
                    rec['refs'] = []
                    for line in reffile.readlines():
                        rec['refs'].append([('x', line.decode('utf-8'))])
                    reffile.close()
        #print '    ' + ', '.join( ['%s (%i)' % (k, len(rec[k])) for k in rec.keys()] ) + '\n'
                    
        if jnlname in ['BOOK', 'IEEE Nucl.Sci.Symp.Conf.Rec.']:
            try:
                print('%3i/%3i %s (%s) %s, %s' % (i,len(allarticlelinks),rec['conftitle'],rec['year'],rec['doi'],'')) #rec['tit'])
            except: 
                print('%3i/%3i %s' % (i,len(allarticlelinks),rec['tit']))
        else:
            try:
                print('%3i/%3i %s %s (%s) %s, %s' % (i,len(allarticlelinks),jnlname,rec['vol'],rec['year'],rec['p1'],'')) #rec['tit'])
            except:
                print(rec)
        if not rec['tit'] in ['IEEE Communications Society', 'IEEE Transactions on Electron Devices information for authors',
                              'IEEE Communications Society Information', 'IEEE Sensors Council', 'General Information',
                              'IEEE Circuits and Systems Society Information', '[Masthead]', '[PDF Not Yet Available In IEEE Xplore]',
                              'IEEE Transactions on Information Theory information for authors', 'Corporate Sponsors',
                              'IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems society information',
                              'IEEE Computer Society Has You Covered!', 'Sponsor', 'Copyright', 'Organizers and Sponsor',
                              'IEEE Computer Society Information',  'Workshop Organization', 'Organizing Committee',
                              'IEEE Transactions on Magnetics Institutional Listings', 'Acknowledgement', 'Organization',
                              'IEEE Computer Society', 'Masthead', 'ComputingEdge', 'Cover', 'Tutorials', 'Conference Chairs',
                              'IEEE Transactions on Magnetics publication information', 'Keynotes', 'Sponsors and Supporters',
                              'IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems publication information',
                              'IEEE Open Access Publishing', 'Introducing IEEE Collabratec', 'IEEE Control Systems Society',
                              'Table of Contents', 'Sponsors', 'Conference Organization', '[Sponsors]', 'Contents',
                              'IEEE Information Theory Society information', 'Board of Governors', 'Commitees',
                              'IEEE Journal on Special Areas in Information Theory information for authors', 'Copyright Page',
                              'IEEE Journal on Special Areas in Information Theoryinformation for authors', 'Title Page',
                              'Back Cover', 'Conference Programme', 'Panel', 'Message from the Chairs',
                              'Message from the Chair', 'IEEE Computer Society Jobs Board', 'Full Program',
                              'Get Published in the New IEEE Open Journal of the Computer Scoiety',
                              'IEEE Computer Society Jobs Board', 'Ieee Computer Society Jobs Board',
                              'Message from the General Chair', 'Speakers', 'Sponsors and Organizers',
                              'Copyright and Reprint Permission']:
            if 'pdf_url'  in rec:
                #download it NOW as availability may change quckly
                doi1trunk = re.sub('\/.*', '', rec['doi'])
                doi1 = re.sub('[\/\(\)]', '_', rec['doi'])
                poufname = '%s/%s/%s.pdf' % (ppdfpath, doi1trunk, doi1)
                if not os.path.isfile(poufname):
                    print('          -> download %s NOW as availability may change quckly' % (rec['pdf_url']))
                    time.sleep(10)
                    os.system('wget -T 300 -t 3 %s -O %s "%s"' % (useragent, poufname, rec['pdf_url']))
                    time.sleep(10)                                                          
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    if recs:
        if jnlname == 'BOOK':
            oufname = 'IEEENuclSciSympConfRec'
        else:
            oufname = re.sub('[ \.]','',jnlname).lower()
        if 'vol' in rec: oufname += '.'+rec['vol']
        if 'issue' in rec:
            oufname += '.'+rec['issue'] + '_'+ejlmod3.stampoftoday()
        else:
            oufname += '_'+ejlmod3.stampoftoday()
        if 'cnum' in rec: oufname += '.'+rec['cnum']
        #driver.quit()
        return (recs, oufname+'_'+number) #XYZ
    else:
        return (recs, 'none')


#journals: isnumber
#journals (IEEE Access) but only QIS stuff: Qisnumber
#proceedings with pagination: punumber
#proceedings without pagination: Npunumber
if __name__ == '__main__':
    usage = """
        python ieee_crawler.py Cpunumber|isnumber|Npunumber|Qisnumber [cnum] 
        use Npunumber if no pagination
    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], "")
        if len(args) > 3:
            raise getopt.GetoptError("Too many arguments given!!!")
        elif not args:
            raise getopt.GetoptError("Missing mandatory argument number")
    except getopt.GetoptError as err:
        print((str(err)))  # will print something like "option -a not recognized"
        print(usage)
        sys.exit(2)
    number = args[0]
    publisher = 'IEEE'

    numbers = re.split(',', number)
    for (i, singlenumber) in enumerate(numbers):
        ejlmod3.printprogress('###', [[i+1, len(numbers)], [singlenumber]])
        (recs, jnlfilename) = ieee(singlenumber)
#        if host != 'l00schwenn':
        ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
        if i+1 < len(numbers):
            time.sleep(120)

driver.quit()
