# -*- coding: UTF-8 -*-
#program to harvest Bulgarian Journal of Physics
# FS 2012-06-01
# FS 2023-03-22

import os
import ejlmod3
import re
import sys
from removehtmlgesocks3 import removehtmlgesocks

tmpdir = '/tmp'
def tfstrip(x): return x.strip()

publisher = 'Bulgarian Academy of Sciences'
vol = sys.argv[1]
issue = sys.argv[2]
year = str(int(vol)+1973)
jnl = 'buljp'
jnlfilename = jnl+vol+'.'+issue
jnlname = 'Bulg.J.Phys.'

urltrunk = 'http://www.bjp-bg.com'


recnr = 1
print("get table of content ...")
print("lynx -source \"%s/papers.php?year=%s&vol=%s&issue=%s\"  > %s/%s.toc" % (urltrunk,year,vol,issue,tmpdir,jnlfilename))
os.system("lynx -source \"%s/papers.php?year=%s&vol=%s&issue=%s\"  > %s/%s.toc" % (urltrunk,year,vol,issue,tmpdir,jnlfilename))
    
tocfil = open("%s/%s.toc" % (tmpdir,jnlfilename),'r')
#for tline in  map(tfstrip,tocfil.readlines()):
tocline = re.sub('\s\s+',' ',' '.join(map(tfstrip,tocfil.readlines())))
subject = ''
recs = []
for tline in re.split(' *<DT> *',tocline):    
    tline = removehtmlgesocks(tline)
    if re.search('href.*pdf',tline):
        rec = {'auts': [], 'aff': [], 'typ': '', 'year': year,
               'vol': vol, 'issue': issue, 'jnl': jnlname, 
               'tc': 'P', 'note': []}
        if len(sys.argv) > 3:
            rec['cnum'] = sys.argv[3]
            rec['tc'] = 'C'
        rec['tit'] = re.sub('.*?<strong><a.*?> *(.*?) *<\/a>.*',r'\1',tline)
        rec['tit'] = re.sub('<sub>(.*?)<\/sub>',r'_\1',rec['tit'])
        rec['tit'] = re.sub('<sup>(.*?)<\/sup>',r'^\1',rec['tit'])
        rec['hidden'] = urltrunk+re.sub('.*?<a href=\"(papers\/.*?)\.pdf\".*',r'/\1',tline)+str(recnr)+'.pdf'
        doi1 = re.sub('.*\/(.*)\.pdf',r'\1',rec['hidden'])
        pbn = re.sub('.*> *pp\. (\d.*?),.*',r'\1',tline)
        rec['p1'] = re.sub('(\d+) *\- *(\d+)',r'\1',pbn)
        rec['p2'] = re.sub('(\d+) *\- *(\d+)',r'\2',pbn)
        print("%s%s (%s) %s-%s" %(jnlname,rec['vol'],rec['year'],rec['p1'],rec['p2']))
        rec['link'] = urltrunk+re.sub('.*\[<a href=\"(.*?)\".*',r'/\1',tline)
        artfilname = "%s/%s.%s" %(tmpdir,jnlfilename,doi1)
        #get more infos from article-page
        if not os.path.isfile(artfilname):
            print("lynx -source \"%s\" > %s" %(rec['link'],artfilname))
            os.system("lynx -source \"%s\" > %s" %(rec['link'],artfilname))
        artfil = open(artfilname,'r')
        artline = re.sub('\s\s+',' ',' '.join(map(tfstrip,artfil.readlines())))
        artline =removehtmlgesocks(artline)
        artline = re.sub('^.*?<\/h4> *','',artline)
        artline = re.sub(' *<\/BLOCKQUOTE>.*','',artline)
        if re.search('doi.org\/10.55318', artline):
            rec['doi'] = re.sub('.*doi.org\/(10.55318.*?)".*', r'\1', artline)
        rec['abs'] = re.sub('.*<BLOCKQUOTE>.*?Abstract\.?<\/strong> *','',artline)
        rec['abs'] = re.sub('.*<a href *="https\/\/doi.org.*','', rec['abs'])
        rec['abs'] = re.sub('<sub>(.*?)<\/sub>',r'_\1',rec['abs'])
        rec['abs'] = re.sub('<sup>(.*?)<\/sup>',r'^\1',rec['abs'])
        rec['abs'] = re.sub('<\/?i>','',rec['abs'])
        autaffs = re.split(' *<BR.*?> *',re.sub('<BLOCKQUOTE>.*','',artline))
        authors = autaffs[0]
        authors = re.sub('.*<div class="style12">', '', authors)
        authors = re.sub('<sup>([0-9;])+ *, *',r'<sup>\1;',authors)
        authors = re.sub('<sup>([0-9;])+ *, *',r'<sup>\1;',authors)
        authors = re.sub('<sup>([0-9;])+ *, *',r'<sup>\1;',authors)
        for aut in re.split(' *, *',authors):
            if re.search('<sup>',aut):
                marker = re.sub('.*<sup>(.*?)<\/sup>.*',r'\1',aut)
                aut = re.sub('<sup>.*','',aut)
            else:
                marker = ''
            aut = re.sub('\. ([A-Z])\.', r'.\1.',aut)
            aut = re.sub('\.\-([A-Z])\.', r'.\1.',aut)
            if re.search('[a-z]',aut):
                #print "  aut:"+aut
                rec['auts'].append(re.sub('^(.*) (.*?)$', r'\2, \1',aut))
                if not (marker == ''):
                    for mark in re.split(';',marker):
                        rec['auts'].append("=Aff"+mark)                    
        for aff in autaffs[1:]:
            if (len(aff) > 5):
                aff = re.sub(' *<sup>(.*)<\/sup> *',r'Aff\1=',aff)
                rec['aff'].append(re.sub(' *<\/?em> *','',aff))
        #write record
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
        recnr += 1

ejlmod3.writenewXML(recs, publisher, jnlfilename)
