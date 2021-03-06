# -*- coding: utf-8 -*-
import xml.dom.minidom
import re
import os
import subprocess
import datetime
import platform
import unicodedata
import unidecode
import codecs
import time
from bs4 import BeautifulSoup
from iso639 import languages

from collclean_lib3 import coll_cleanforthe
from collclean_lib3 import coll_clean710
from collclean_lib3 import coll_split
try:
    from inspire_utils.date import normalize_date
except:
    def normalize_date(datum):
        return datum

try:
    # needed to remove the print-commands from /usr/lib/python2.6/site-packages/refextract/references/engine.py
    from refextract import  extract_references_from_string
except:
    #for running on PubDB
    print('could not import extract_references_from_string')

#QIS bibclassify
qisbibclassifycommand = "/usr/bin/python /afs/desy.de/user/l/library/proc/bibclassify/bibclassify_cli.py  -k /afs/desy.de/user/l/library/akw/QIS_TEST.rdf -n 10"
absdir = '/afs/desy.de/group/library/publisherdata/abs'
tmpdir = '/afs/desy.de/user/l/library/tmp'


#
journalskb = '/opt/invenio/etc/docextract/journal-titles-inspire.kb'
journalskb = '/afs/desy.de/user/l/library/lists/journal-titles-inspire.kb'

retfiles_path = '/afs/desy.de/user/l/library/proc/retinspire'
now = datetime.datetime.now()


#from collclean import clean710

#mappings for refferences in JSON to MARC
mappings = {'doi' : 'a',
            'hdl' : 'a',
            'collaborations' : 'c',
            'document_type' : 'd',
            'author' : 'h',
            'isbn' : 'i',
            'texkey' : 'k',
            'misc' : 'm',
            'journal_issue' : 'n',
            'label' : 'o',
            'linemarker' : 'o',
            'reportnumber' : 'r',
            'journal_reference' : 's',
            'title' : 't',
            'urls' : 'u',
            'raw_ref' : 'x',
            'year' : 'y'}

#find additional reportnumbers
repreprints = re.compile('.*Preprint:? ([A-Z0-9\-\/, ]+).*')
repreprint = re.compile('^[A-Z0-9\-\/ ]+$')
#split keywords
rekeywsplit1 =  re.compile(', .*, ')
rekeywsplit2 =  re.compile('; .*; ')
rekeywsplit1plus =  re.compile(', .*, .*, ')
rekeywsplit2plus =  re.compile('; .*; .*; ')

#valid arXiv numbers
rearxivold = re.compile('^[a-z\-]+\/\d{7}$')
rearxivnewshort = re.compile('^\d{4}\.\d{4,5}')
rearxivnew = re.compile('^ar[xX]iv:\d{4}\.\d{4,5}')
rearxivhttpold = re.compile('https?:.*arxiv.org.*?([a-z\-]+\/\d{7}).*')
rearxivhttpnew = re.compile('https?:.*arxiv.org.*(\d{4}\.\d{4,5}).*')
#valid ORCID
reorcid = re.compile('^ORCID:\d{4}\-\d{4}\-\d{4}\-\d{3}[0-9X]$')

#list of lists to automatically suggest fieldcodes based on journalname
#(can also handle mutiple FCs like 'ai' or so)
#from inspirelibrarylabs import fcjournalliste
fcjournalliste = [('b', ['IEEE Trans.Appl.Supercond.', 'Supercond.Sci.Technol.']),
                  ('m', ['Abstr.Appl.Anal.', 'Acta Appl.Math.', 'Adv.Appl.Clifford Algebras', 'Adv.Math.', 'Adv.Math.Phys.', 'Afr.Math.', 'Alg.Anal.', 'Algebr.Geom.Topol.', 'Alg.Groups Geom.', 'Alg.Logika', 'Anal.Math.Phys.', 'Anal.Part.Diff.Eq.', 'Annals Probab.', 'Ann.Inst.H.Poincare Probab.Statist.', 'Ann.Math.Sci.Appl.', 'Ann.PDE', 'Arab.J.Math.', 'Asian J.Math.', 'Axioms', 'Bayesian Anal.', 'Braz.J.Probab.Statist.', 'Bull.Am.Math.Soc.', 'Bull.Austral.Math.Soc.', 'Cahiers Topo.Geom.Diff.', 'Calc.Var.Part.Differ.Equ', 'Can.J.Math.', 'Commun.Anal.Geom.', 'Commun.Math.Phys.', 'Commun.Math.Sci.', 'Commun.Pure Appl.Math.', 'Compos.Math.', 'Compt.Rend.Math.', 'Conform.Geom.Dyn.', 'Contemp.Math.', 'Duke Math.J.', 'Eur.J.Combinatorics', 'Exper.Math.', 'Forum Math.Pi', 'Forum Math.Sigma', 'Fractals', 'Geom.Topol.', 'Geom.Topol.Monographs', 'Glasgow Math.J.', 'Hokkaido Math.J.', 'Int.Math.Res.Not.', 'Invent.Math.', 'Inverse Prob.', 'Izv.Vuz.Mat.', 'J.Alg.Geom.', 'J.Am.Math.Soc.', 'J.Appl.Math.', 'J.Appl.Math.Mech.', 'J.Austral.Math.Soc.', 'J.Diff.Geom.', 'J.Geom.Anal.', 'J.Geom.Symmetry Phys.', 'J.Inst.Math.Jussieu', 'J.Integrab.Syst.', 'J.Korean Math.Soc.', 'J.Math.Phys.', 'J.Math.Res.', 'J.Math.Sci.', 'J.Math.Soc.Jap.', 'J.Part.Diff.Eq.', 'Lect.Notes Math.', 'Lett.Math.Phys.', 'Manuscr.Math.', 'Math.Comput.', 'Mathematics', 'Math.Methods Appl.Sci.', 'Math.Nachr.', 'Math.Notes', 'Math.Phys.Anal.Geom.', 'Math.Phys.Stud.', 'Math.Proc.Cambridge Phil.Soc.', 'Math.Res.Lett.', 'Mat.Sbornik', 'Mat.Zametki', 'Moscow Math.J.', 'Pacific J.Math.', 'p Adic Ultra.Anal.Appl.', 'Proc.Am.Math.Soc.', 'Proc.Am.Math.Soc.Ser.B', 'Proc.Geom.Int.Quant.', 'Prog.Math.Phys.', 'Rept.Math.Phys.', 'Russ.J.Math.Phys.', 'Russ.Math.Surveys', 'Springer Proc.Math.Stat.', 'Tokyo J.Math.', 'Trans.Am.Math.Soc.', 'Trans.Am.Math.Soc.Ser.B', 'Trans.Moscow Math.Soc.', 'Turk.J.Math.', 'Ukr.Math.J.', 'J.Reine Angew.Math.', 'Arch.Ration.Mech.Anal.', 'Acta Math.Vietnamica', 'Quart.J.Math.Oxford Ser.', 'Int.J.Math.', 'Integral Transform.Spec.Funct.', 'Commun.Contemp.Math.', 'Selecta Math.', 'J.Sympl.Geom.', 'Q.Appl.Math.', 'J.Universal Math.']),
                  ('q', ['ACS Photonics', 'Atoms', 'J.Chem.Phys.', 'J.Chem.Theor.Comput.', 'J.Mod.Opt.', 'J.Molec.Struc.', 'J.Opt.', 'J.Opt.Soc.Am. A', 'J.Opt.Soc.Am. B', 'Mater.Chem.Phys.', 'Nano Lett.', 'Nanotechnol.', 'Nature Photon.']),
                  ('k', ['ACM Trans.Quant.Comput.', 'Quant.Inf.Proc.', 'Quantum Eng.', 'Quantum Rep.', 'Quantum Sci.Technol.', 'Quantum', 'AVS Quantum Sci.', 'Adv.Quantum Technol.']),
                  ('f', ['Adv.Cond.Mat.Phys.', 'Ann.Rev.Condensed Matter Phys.', 'Condens.Mat.', 'J.Noncryst.Solids', 'J.Phys.Chem.Solids', 'J.Phys.Condens.Matter', 'Solid State Commun.', 'Sov.Phys.Solid State', 'Condensed Matter Phys.', 'Phys.Status Solidi', 'Solid State Phenom.']),
                  ('a', ['Ann.Rev.Astron.Astrophys.', 'Acta Astron.', 'Acta Astron.Sin.', 'Adv.Astron.', 'Astron.Astrophys.', 'Astron.Astrophys.Lib.', 'Astron.Astrophys.Rev.', 'Astron.Geophys.', 'Astron.J.', 'Astron.Lett.', 'Astron.Nachr.', 'Astron.Rep.', 'Astrophys.Bull.', 'Astrophysics', 'Astrophys.J.', 'Astrophys.J.Lett.', 'Astrophys.J.Supp.', 'Astrophys.Space Sci.', 'Astrophys.Space Sci.Libr.', 'Astrophys.Space Sci.Proc.', 'Chin.Astron.Astrophys.', 'Exper.Astron.', 'Front.Astron.Space Sci.', 'Int.J.Astrobiol.', 'J.Astron.Space Sci.', 'J.Astrophys.Astron.', 'J.Atmos.Sol.Terr.Phys.', 'JCAP', 'J.Korean Astron.Soc.', 'Mon.Not.Roy.Astron.Soc.', 'Nat.Astron.', 'New Astron.', 'Open Astron.', 'Publ.Astron.Soc.Austral.', 'Publ.Astron.Soc.Jap.', 'Publ.Astron.Soc.Pac.', 'Res.Astron.Astrophys.', 'Res.Notes AAS', 'Rev.Mex.Astron.Astrofis.', 'Space Sci.Rev.', 'Nature Astron.', 'Galaxies']),
                  ('g', ['Class.Quant.Grav.', 'Gen.Rel.Grav.', 'Living Rev.Rel.']),
                  ('c', ['Comput.Softw.Big Sci.', 'J.Grid Comput.', 'J.Open Source Softw.', 'SoftwareX']),
                  ('i', ['IEEE Instrum.Measur.Mag.', 'IEEE Sensors J.', 'IEEE Trans.Circuits Theor.', 'IEEE Trans.Instrum.Measur.', 'Instruments', 'Instrum.Exp.Tech.', 'JAIS', 'JINST', 'Meas.Tech.', 'Measur.Sci.Tech.', 'Metrologia', 'Microscopy Microanal.', 'Rad.Det.Tech.Meth.', 'Rev.Sci.Instrum.', 'Sensors', 'J.Astron.Telesc.Instrum.Syst.', 'EPJ Tech.Instrum.'])]
#rearrange the lists into a dictionary
jnltofc = {}
for (fc, jnllist) in fcjournalliste:
    for jnl in jnllist:
        jnltofc[jnl] = fc

#auxiliary function to strip lines
def tgstrip(x): return x.strip()

def kapitalisiere(string):
    if re.search('[a-z]', string):
        return string
    elif re.search('[A-Z]', string):
        acronyms = ['LHC', 'CFT', 'QCD', 'QED', 'QFT', 'ABJM', 'NLO', 'LO', 'NNLO', 'IIB', 'IIA', 'MSSM', 'NMSSM', 'SYM', 'WIMP', 'ATLAS', 'CMS', 'ALICE', 'RHIC', 'DESY', 'HERA', 'CDF', 'D0', 'BELLE', 'BABAR', 'BFKL', 'DGLAP', 'SUSY', 'QM', 'UV', 'IR', 'BRST', 'PET', 'GPS', 'NMR', 'XXZ', 'CMB', 'LISA', 'CPT', 'KEK', 'TRIUMF', 'PHENIX', 'VLBI', 'NGC', 'SNR', 'HESS', 'AKARI', 'GALEX', 'ESO', 'J-PARC', 'CERN', 'XFEL', 'FAIUR', 'ILC', 'CLIC', 'SPS', 'BNL', 'CEBAF', 'SRF', 'LINAC', 'HERMES', 'ZEUS', 'H1', 'GRB', 'GSI']
        word_list = re.split(' +', string)
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            if word.upper() in acronyms:
                final.append(word.upper())
            elif len(word) > 3:
                final.append(word.capitalize())
            else:
                final.append(word.lower())
        return " ".join(final)
    else:
        return string

#FS: try to get arXiv-number from ADS for some journals
def arXivfromADS(rec):
    adslink = 'http://adsabs.harvard.edu/doi/' + rec['doi']
    print('try '+adslink+' to get arXiv-number')
    for adsline in os.popen("lynx -source \"%s\"|grep citation_arxiv_id" % (adslink)).readlines():
        if re.search('arxiv',adsline):
            rec['arxiv'] = re.sub('.*content="(.*)".*', r'\1', adsline).strip()
            print('---[ ADS: %s -> %s ]---' % (rec['doi'], rec['arxiv']))
            if 'note' in rec:
                if type(rec['note']) == type(['Liste']):
                    rec['note'].append('arXiv number from ADS (not from publisher!)')
                else:
                    rec['note'] = [rec['note'],'arXiv number from ADS (not from publisher!)']
            else:
                rec['note'] = ['arXiv number from ADS (not from publisher!)']
    return

#find collaborations in authorfield
refcauthor = re.compile(' *([A-Z].*? [A-Z][a-z]+ .*?) FFF ')
refcsplitter1 = re.compile('( |^)[fF]or [Tt]he ')
refcsplitter2 = re.compile('( |^)[oO]n [bB]ehalf [oO]f [Tt]he ')
refcsplitter3 = re.compile('( |^)[fF]or ')
refcsplitter4 = re.compile('( |^)[oO]n [bB]ehalf [oO]f ')
def findcollaborations(authorfield):
    if re.search('Collaboration', authorfield):
        aft = re.sub('^ *\( *(.*) *\) *$', r'\1', authorfield)
        aft = refcsplitter1.sub(' FFF ', aft)
        aft = refcsplitter2.sub(' FFF ', aft)
        aft = refcsplitter3.sub(' FFF ', aft)
        aft = refcsplitter4.sub(' FFF ', aft)
        author = False
        if refcauthor.search(aft):
            author = refcauthor.sub(r'\1', aft)
        collaborations = re.sub('.*FFF ', '', aft)
        collaborations = re.sub('^ *(.*) Collaborations.*', '', collaborations)
        colparts = re.split(' *, *', re.sub(' [aA]nd ', ', ', collaborations))
        return (author, colparts)
    else:
        return (authorfield, False)



#FS:
#add experiment line for existing collaboration
#and try to find experiment in title
colexpdictfilename = '/afs/desy.de/user/l/library/lists/expcolFS'
colexpdictfile = open(colexpdictfilename,'r')
colexpdict = {}
expexpdict = {}
for colexpline in colexpdictfile.readlines():
    parts = re.split(';',colexpline.strip())
    colexpdict[re.sub(' *Collabo.*','',parts[0]).upper()] = parts[1:]
    if not re.search(' and ',parts[0]):
        expexpdict[re.sub(' *Collabo.*','',parts[0])] = re.sub(' *experiment.*','',parts[1])
colexpdictfile.close()

def findexperiment(rec):
    if 'col' in rec:
        #print "COL=",rec['col']
        collaboration = re.sub(' *Collabo.*','',rec['col']).upper()
        if collaboration in colexpdict:
            rec['exp'] = colexpdict[collaboration]
            #print "EXP=",rec['exp']
    else:
        experiments = []
        for exp in expexpdict:
            if re.search('(\W|^)'+exp+'($|\W)',rec['tit']):
            #if (exp != 'DO') and re.search(exp,rec['tit']):
                experiments.append(expexpdict[exp] + '')
        if len(experiments) > 0:
            rec['exp'] = experiments
            print("EXP=",rec['exp'])
    return


#FS:
#get abstract from arXiv (e.g. Intl. Press;)
def getabsfromarxiv(rec):
    absdir = '/afs/desy.de/group/library/publisherdata/abs/'
    bull = re.sub('.*\: ','',rec['arxiv'])
    print(" get abstract for %s from arXiv" % (bull))
    arxivpage = os.popen("lynx -source \"http://export.arxiv.org/abs/%s\"" % (bull)).read().replace('\n',' ')
    abstract = re.sub('.*<span class=\"descriptor\">Abstract\:<\/span> *(.*) *<\/blockquote>.*',r'\1',arxivpage )
    abstract = re.sub('  +',' ',abstract)
    rec['abs'] = re.sub(';',',',abstract)
    return



#new stuff: writeXML
inspirefc = {'e':'Experiment-HEP', 'i':'Instrumentation',
             'b':'Accelerators', 'x':'Experiment-Nucl',
             'n':'Theory-Nucl', 'c':'Computing',
             'a':'Astrophysics', 'p':'Phenomenology-HEP',
             'o':'General Physics', 'g':'Gravitation and Cosmology',
             'l':'Lattice', 'm':'Math and Math Physics',
             'o':'Other', 'q':'General Physics',
             'f':'Condensed Matter', 'k':'Quantum Physics',
             's' : 'Data Analysis and Statistics', 't':'Theory-HEP'}
inspiretc = {'P':'Published', 'C':'ConferencePaper',
             'R':'Review', 'T':'Thesis',
             'B':'Book', 'S': 'BookChapter',
             'K': 'Proceedings', 'O': 'Note',
             'L' : 'Lectures', 'I':'Introductory'}


#translating HTML entities
htmlentity = re.compile(r'&#x.*?;')
def lam(x):
    x  = x.group()
    return chr(int(x[3:-1], 16))

#we can not install the latest refextractor :(
#here are some "manual" journal normalizations
renjwas = [(re.compile('Journal of Physics G.? Nuclear and Particle Physics, *'), 'J.Phys.,G'),
           (re.compile('Journal of Physics A.? General Physics, *'), 'J.Phys.,A'),
           (re.compile('Advances in High Energy Physics, *'), 'AHEP, '),
           (re.compile('Physical Review A.? Atomic, Molecular and Optical Physics, *'), 'Phys.Rev.,A'),
           (re.compile('Physical Review B.? Condensed Matter and Materials Physics, *'), 'Phys.Rev.,B'),
           (re.compile('Physical Review E.? Statistical, Nonlinear, and Soft Matter Physics, *'), 'Phys.Rev.,E'),
           (re.compile('Progress of Theoretical and Experimental Physics, *'), 'PTEP, '),
           (re.compile('Fortschritte der Physik.Progress of Physics, *'), 'Fortsch.Phys., '),
           (re.compile('Electronic Journal of Theoretical Physics, *'), 'Electron.J.Theor.Phys. , '),
           (re.compile('Journal of Modern Physics, *'), 'J.Mod.Phys., '),
           (re.compile('Physica Scripta. An International Journal for Experimental and Theoretical Physics, *'), 'Phys.Scripta, '),
           (re.compile('Results in Physics, *'), 'Results Phys., '),
           (re.compile('Computational Mathematics and Mathematical Physics, *'), 'Comput.Math.Math.Phys., '),
           (re.compile('Journal of Nonlinear Mathematical Physics, *'), 'J.Nonlin.Mathematical Phys., '),
           (re.compile('Journal of Geophysical Research.? .?Space Physics.?, *'), 'J.Geophys.Res.Space Phys., '),
           (re.compile('J. Geophys. Res. Space Physics, *'), 'J.Geophys.Res.Space Phys., '),
           (re.compile('Journal of Atmospheric and Solar..?.?Terrestrial Physics, *'), 'J.Atmos.Sol.Terr.Phys., '),
           (re.compile('International Journal Geometrical Methods in Modern Physics, *'), 'Int.J.Geom.Meth.Mod.Phys., '),
           (re.compile('Advances in Mathematical Physics, *'), 'Adv.Math.Phys., '),
           (re.compile('SciPost Physics, *'), 'SciPost Phys., '),
           (re.compile('Studies in History and Philosophy of Science. Part B. Studies in History and Philosophy of Modern Physics, *'), 'Stud.Hist.Phil.Sci.,B'),
           (re.compile('Indian Journal of Radio ..?.?.?.? Space Physics, *'), 'Indian J.Radio Space Phys, '),
           (re.compile('Atmospheric Chemistry And Physics, *'), 'Atmos.Chem.Phys., '),
           (re.compile('Opt. Exp., *'), 'Opt.Express, '),
           (re.compile('Low Temperature Physics, *'), 'Low Temp.Phys., ')]


def normalizejournalsworkaround(rawref):
    for (renjwa, normalized) in renjwas:
        rawref = renjwa.sub(normalized, rawref)
    return rawref



def validxml(string):
    if type(string) == type(()):
        return tuple([validxml(part) for part in string])
    elif type(string) == type([]):
        return [validxml(part) for part in string]
    else:
        #print '--->',string
        string = htmlentity.sub(lam, string)
        string = re.sub('&','&amp;',string)
        string = re.sub('>','&gt;',string)
        string = re.sub('<','&lt;',string)
        string = re.sub('"','&quot;',string)
        string = re.sub('\'','&apos;',string)
        return re.sub('  +', ' ', string)


def marcxml(marc,liste):
    if len(marc) < 5: marc += ' '
    if len(marc) < 5: marc += ' '
    #print marc,liste
    xmlstring = ' <datafield tag="%s" ind1="%s" ind2="%s">\n' % (marc[:3],marc[3],marc[4])
    for tupel in liste:
        if tupel[1] is not None:
            if type(tupel[1]) == type([]):
                for element in tupel[1]:
                    if element != '':
                        xmlstring += '  <subfield code="%s">%s</subfield>\n' % (tupel[0], validxml(element).strip())
            else:
                if tupel[1] != '':
                    try:
                        xmlstring += '  <subfield code="%s">%s</subfield>\n' % (tupel[0],validxml(tupel[1]).strip())
                    except:
                        print('ERROR in function "marcxml"')
                        print(marc, liste)
    xmlstring += ' </datafield>\n'
    #avoid empty xml entries
    if re.search('<subfield code="[a-z]">',xmlstring):
        return xmlstring
    else:
        return ''

reptep = re.compile('.*P.*?T.*?P.*?\D(\d\d\d?[A-J]\d\d\d?)\D.*')
def repairptep(erfs):
    newerfs = []
    for ref in erfs:
        if 'journal_title' in ref and 'PTEP' in ref['journal_title'] and reptep.search(ref['raw_ref'][0]):
            newref = {k : ref[k] for k in ref}
            artid = reptep.sub(r'\1', ref['raw_ref'][0])
            #if 'journal_page' in ref.keys():
            #    print '    [[PTEP]] replace p1=%s by p1=%s' % (ref['journal_page'][0], artid)
            #else:
            #    print '    [[PTEP]] added p1=%s' % (artid)
            newref['journal_page'] = [artid]
            newref['journal_reference'] = [ '%s,%s,%s' % (ref['journal_title'][0], ref['journal_volume'][0], artid) ]
            newerfs.append(newref)
        else:
            newerfs.append(ref)

    return newerfs


#regular expressions to add field code based on rec['note']
refcmp = re.compile('Mathematical Phys')
refcp = re.compile('Phys')
refcm = re.compile('Math')
refcc = re.compile('Comput')
refca = re.compile('Astro')
#refck = re.compile('[qQ]uantum.(Phys|phys|Infor|infor|Comp|comp|Tec|Com|Corr|Theor|Mech|Dynam|Opti|Elec)')
refck = re.compile('[qQ]uantum.(Infor|infor|Comp|comp)')
rerfc = re.compile('^([a-z][a-z])\W[A-Z].*')
def writeXML(recs,dokfile,publisher):
    dokfile.write('<collection>\n')
    i = 0
    for rec in recs:
        recdate = False
        if rec['jnl'] in ['Astron.Astrophys.', 'Mon.Not.Roy.Astron.Soc.',
                          'Astronom.J.', 'Adv.Astron.', 'Astron.Nachr.']:
            arXivfromADS(rec)
        liste = []
        i += 1
        if 'doi' in rec:
            print(rec['doi'], list(rec.keys()))
        elif 'hdl' in rec:
            print(rec['hdl'], list(rec.keys()))
        elif 'urn' in rec:
            print(rec['urn'], list(rec.keys()))
        else:
            print('no identifier?!       ', list(rec.keys()))
        if 'arxiv' in rec and re.search('v[0-9]+$', rec['arxiv']):
            rec['arxiv'] = re.sub('v[0-9]+$', '', rec['arxiv'])
        xmlstring = '<record>\n'
        #direct marc first (retinspire takes the first DOI?)
        if 'MARC' in rec:
            for marc in rec['MARC']:
                xmlstring += marcxml(marc[0], marc[1])
        #TITLE
        if 'tit' in rec:
            xmlstring += marcxml('245',[('a',kapitalisiere(rec['tit'])), ('9',publisher)])
        if 'otits' in rec:
            for otit in rec['otits']:
                xmlstring += marcxml('246', [('a',kapitalisiere(otit)), ('9',publisher)])
        if 'transtit' in rec:
            xmlstring += marcxml('242',[('a',kapitalisiere(rec['transtit'])), ('9',publisher)])
        #LANGUAGE
        if 'language' in rec:
            #combined language/country codes like RFC 1766
            if rerfc.search(rec['language']):
                rec['language'] = rerfc.sub(r'\1', rec['language'])
            #try ISO 639, then the other ISOs
            if len(rec['language']) == 2:
                try:
                    lang = languages.get(part1=rec['language']).name
                except:
                    lang = False                    
            elif len(rec['language']) == 3:              
                try:
                    lang = languages.get(part2t=rec['language']).name
                except:
                    try:
                        lang = languages.get(part2b=rec['language']).name
                    except:
                        try:
                            lang = languages.get(part3=rec['language']).name
                        except:
                            lang = False
            else:
                lang = rec['language']
            if lang:
                if lang != 'English':
                    xmlstring += marcxml('041', [('a', lang)])
                    xmlstring += marcxml('595', [('a', 'Text in %s' % (lang))])
            else:
                xmlstring += marcxml('595', [('a', 'unknown language "%s"' % (rec['language']))])  
        #ABSTRACT
        if 'abs' in rec:
            if len(rec['abs']) > 5:
                try:
                    xmlstring += marcxml('520',[('a',rec['abs']), ('9',publisher)])
                except:
                    #xmlstring += marcxml('595', [('a', 'could not write abstract!')])
                    xmlstring += marcxml('520', [('a', unidecode.unidecode(rec['abs'])), ('9', publisher)])
            else:
                print('abstract "%s" too short' % (rec['abs']))
        #DATE
        if 'date' in rec:
            try:
                #recdate = rec['date']
                recdate = normalize_date(rec['date'])
            except:
                try:
                    if re.search('[12]\d\d\d', rec['date']):
                        recdate = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
                except:
                        recdate = False
                        print(' !! invalid date "%s"' % (rec['date']))
                        del(rec['date'])
        if not 'date' in rec and 'year' in rec:
            rec['date'] = rec['year']
            recdate = rec['year']
        if 'date' in rec:
            try:
                if 'B' in rec['tc']:
                    xmlstring += marcxml('260', [('c', recdate), ('t', 'published'), ('b', publisher)])
                else:
                    xmlstring += marcxml('260', [('c', recdate), ('t', 'published')])
            except:
                try:
                    xmlstring += marcxml('260', [('c', rec['year']), ('t', 'published')])
                except:
                    print('{DATE}', recdate,  rec)
                    xmlstring += marcxml('599', [('a', 'date missing?!')])
        #KEYWORDS
        if 'keyw' in rec:
            if len(rec['keyw']) == 1:
                if rekeywsplit1.search(rec['keyw'][0]):
                    keywords = re.split(', ', rec['keyw'][0])
                    xmlstring += marcxml('595', [('a', 'Keywords split: "%s"' % (rec['keyw'][0]))])
                elif rekeywsplit2.search(rec['keyw'][0]):
                    keywords = re.split('; ', rec['keyw'][0])
                    xmlstring += marcxml('595', [('a', 'Keywords split: "%s"' % (rec['keyw'][0]))])
                else:
                    keywords = rec['keyw']
            else:
                keywords = rec['keyw']
            keywordsfinal = []
            for kw in keywords:
                if rekeywsplit1plus.search(kw):
                    for kwt in re.split(', ', kw):
                        if not kwt in rec['keyw']:
                            keywordsfinal.append(kwt)
                    xmlstring += marcxml('595', [('a', 'Keywords split: "%s"' % (kw))])
                elif rekeywsplit2plus.search(kw):
                    for kwt in re.split('; ', kw):
                        if not kwt in rec['keyw']:
                            keywordsfinal.append(kwt)
                    xmlstring += marcxml('595', [('a', 'Keywords split: "%s"' % (kw))])
                else:
                    keywordsfinal.append(kw)
            for kw in keywordsfinal:
                if kw.strip():                    
                    try:
                        xmlstring += marcxml('6531',[('a',kw), ('9','author')])
                    except:
                        if unidecode.unidecode(kw).strip():
                            xmlstring += marcxml('6531', [('a', unidecode.unidecode(kw)), ('9','author')])
        if 'authorkeyw' in rec:
            for kw in rec['authorkeyw']:
                if kw:
                    xmlstring += marcxml('6531',[('a',kw), ('9','author')])
        #PUBNOTE
        if 'jnl' in rec:
            liste = [('p',rec['jnl'])]
            if 'year' in rec:
                liste.append(('y',rec['year']))
            elif 'date' in rec:
                liste.append(('y',re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])))
            if 'p1' in rec:
                if 'p2' in rec:
                    if rec['p1'] != rec['p2']:
                        liste.append(('c',rec['p1']+'-'+rec['p2']))
                    else:
                        liste.append(('c',rec['p1']))
                    if 'pages' not in rec:
                        try:
                            if rec['p1'] != rec['p2']:
                                xmlstring += marcxml('300',[('a',str(int(rec['p2'])-int(rec['p1'])+1))])
                        except:
                            pass
                else:
                    liste.append(('c',rec['p1']))
            elif 'seq' in rec:
                liste.append(('c',rec['seq']))
            elif 'wsp_seq' in rec:
                liste.append(('c',rec['wsp_seq']))
            elif 'artnum' in rec:
                liste.append(('c',rec['artnum']))
            if 'vol' in rec: liste.append(('v',rec['vol']))
            if 'pbnrep' in rec: liste.append(('r',rec['pbnrep']))
            if 'issue' in rec: liste.append(('n',rec['issue']))
            if 'cnum' in rec: liste.append(('w',rec['cnum']))
            if 'motherisbn' in rec: liste.append(('z',rec['motherisbn']))
            xmlstring += marcxml('773',liste)
        if 'alternatejnl' in rec:
            alternateliste = [('p', rec['alternatejnl'])]
            for tup in liste:
                if tup[0] == 'v':
                    if 'alternatevol' in rec:
                        alternateliste.append(('v', rec['alternatevol']))
                    else:
                        alternateliste.append(tup)
                elif tup[0] == 'c':
                    if 'alternatep1' in rec:
                        if 'alternatep2' in rec:
                            if rec['alternatep1'] != rec['alternatep2']:
                                alternateliste.append(('c',rec['alternatep1']+'-'+rec['alternatep2']))
                            else:
                                alternateliste.append(('c',rec['alternatep1']))
                    else:
                        alternateliste.append(tup)
                elif tup[0] == 'n':
                    if 'alternateissue' in rec:
                        alternateliste.append(('n', rec['alternateissue']))
                    else:
                        alternateliste.append(tup)
                elif tup[0] != 'p':
                    alternateliste.append(tup)
            xmlstring += marcxml('7731', alternateliste)
        if 'jnl2' in rec and 'vol2' in rec:
            liste = [('p',rec['jnl2'])]
            if 'year2' in rec:
                liste.append(('y',rec['year2']))
            elif 'date' in rec:
                liste.append(('y',re.sub('.*([12]\d\d\d.*', r'\1', rec['date'])))
            if 'p1p22' in rec:
                rec['p1p22'] = re.sub('???', '-', rec['p1p22'])
                liste.append(('c',rec['p1p22']))
            if 'vol2' in rec: liste.append(('v',rec['vol2']))
            if 'issue2' in rec: liste.append(('n',rec['issue2']))
            if 'cnum' in rec: liste.append(('w',rec['cnum']))
            xmlstring += marcxml('773',liste)
        #BOOK SERIES
        if 'bookseries' in rec:
            xmlstring += marcxml('490', rec['bookseries'])
        #ISBN
        if 'isbns' in rec:
            for isbn in rec['isbns']:
                xmlstring += marcxml('020', isbn)
        elif 'isbn' in rec:
            xmlstring += marcxml('020',[('a', re.sub('\D', '', rec['isbn']))])
        #DOI
        if 'doi' in rec:
            xmlstring += marcxml('0247',[('a',rec['doi']), ('2','DOI'), ('9',publisher)])
            #special euclid:
            if re.search('^20.2000\/euclid\.', rec['doi']):
                xmlstring += marcxml('035', [('9', 'EUCLID'), ('a', rec['doi'][8:])])
        #HDL
        if 'hdl' in rec:
            xmlstring += marcxml('0247',[('a',rec['hdl']), ('2','HDL'), ('9',publisher)])
        #URN
        if 'urn' in rec:
            xmlstring += marcxml('0247',[('a',rec['urn']), ('2','URN'), ('9',publisher)])
#        elif not 'doi' in rec.keys() and not 'hdl' in rec.keys():
#            if len(liste) > 2 or rec.has_key('isbn') or rec.has_key('isbns'):
#                pseudodoi = '20.2000/'+re.sub(' ','_','-'.join([tup[1] for tup in liste]))
#                if rec.has_key('isbn'):
#                    pseudodoi += '_' + rec['isbn']
#                elif rec.has_key('isbns'):
#                    for tupel in rec['isbns'][0]:
#                        if tupel[0] == 'a':
#                            pseudodoi += '_' + tupel[1]
#                xmlstring += marcxml('0247',[('a',pseudodoi), ('2','NODOI'), ('9',publisher)])
#            elif 'tit' in rec.keys():
#                pseudodoi = '30.3000/' + re.sub('\W', '', rec['tit'])
#                if 'auts' in rec.keys() and rec['auts']:
#                    pseudodoi += '/' + re.sub('\W', '', rec['auts'][0])
#                elif 'autaff' in rec.keys() and rec['autaff'] and rec['autaff'][0]:
#                    pseudodoi += '/' + re.sub('\W', '', rec['autaff'][0][0])
#                xmlstring += marcxml('0247',[('a',pseudodoi), ('2','NODOI'), ('9',publisher)])
        #NUMBER OF PAGES
        if 'pages' in rec:
            if rec['pages']:
                if type(rec['pages']) == type('999'):
                    xmlstring += marcxml('300',[('a',rec['pages'])])
                elif type(rec['pages']) == type('999'):
                    xmlstring += marcxml('300',[('a',rec['pages'])])
                elif type(rec['pages']) == type(999):
                    xmlstring += marcxml('300',[('a',str(rec['pages']))])
        #TYPE CODE
        if 'tc' in rec:
            for tc in rec['tc']:
                if tc != '':
                    xmlstring += marcxml('980',[('a',inspiretc[tc])])
        #PACS
        if 'pacs' in rec:
            for pacs in rec['pacs']:
                xmlstring += marcxml('084',[('a',pacs), ('2','PACS')])
        #COLLABRATION
        if 'col' in rec:
            if type(rec['col']) != type([]):
                rec['col'] = [rec['col']]
            newcolls = []
            for col in rec['col']:
                for original in coll_split(col):
                    (coll, author) = coll_cleanforthe(original)
                    coll = coll_clean710(coll)
                    newcolls.append(coll)
                    if author:
                        try:
                            print('found author %s in collaboration string %s' % (author, original))
                        except:
                            print('found author in collaboration string')
            for col in newcolls:
                xmlstring += marcxml('710',[('g',col)])
                if 'exp' not in rec and col in colexpdict:
                    xmlstring += marcxml('693',[('e',colexpdict[col])])
        #arXiv NUMBER
        if 'arxiv' in rec:
            if re.search('^[0-9]',rec['arxiv']):
                rec['arxiv'] = 'arXiv:'+rec['arxiv']
            if rearxivnew.search(rec['arxiv']) or rearxivold.search(rec['arxiv']):
                xmlstring += marcxml('037',[('a',rec['arxiv']),('9','arXiv')])
            elif rearxivnewshort.search(rec['arxiv']):
                xmlstring += marcxml('037',[('a', 'arxiv:' + rec['arxiv']),('9','arXiv')])
            elif rearxivhttpnew.search(rec['arxiv']):
                bull = rearxivhttpnew.sub(r'\arxiv:\1', rec['arxiv'])
                xmlstring += marcxml('037',[('a',bull),('9','arXiv')])
            elif rearxivhttpold.search(rec['arxiv']):
                bull = rearxivhttpold.sub(r'\1', rec['arxiv'])
                xmlstring += marcxml('037',[('a',bull),('9','arXiv')])
            else:
                xmlstring += marcxml('037',[('a',rec['arxiv'])])
        #REPORT NUMBER
        if 'rn' in rec:
            for rn in rec['rn']:
                #check for OSTI
                if re.search('^OSTI\-', rn):
                    xmlstring += marcxml('035', [('9', 'OSTI'), ('a', rn[5:])])
                else:
                    xmlstring += marcxml('037', [('a', rn)])
        #EXPERIMENT
        if 'exp' in rec:
            xmlstring += marcxml('693',[('e',rec['exp'])])
        #PDF LINK
        if 'pdf' in rec:
            if re.search('^http', rec['pdf']):
                xmlstring += marcxml('8564',[('u',rec['pdf']), ('y','Fulltext')])
            else:
                xmlstring += marcxml('595', [('a', 'invalid link "%s"' % (rec['pdf']))])
        #FULLTEXT
        if 'FFT' in rec:
            if re.search('^http', rec['FFT']) or re.search('^\/afs\/cern', rec['FFT']):
                xmlstring += marcxml('FFT',[('a',rec['FFT']), ('d','Fulltext'), ('t','INSPIRE-PUBLIC')])
            else:
                xmlstring += marcxml('595', [('a', 'invalid link "%s"' % (rec['FFT']))])
        elif 'fft' in rec:
            if re.search('^http', rec['fft']) or re.search('^\/afs\/cern', rec['fft']):
                xmlstring += marcxml('FFT',[('a',rec['fft']), ('d','Fulltext'), ('t','INSPIRE-PUBLIC')])
            else:
                xmlstring += marcxml('595', [('a', 'invalid link "%s"' % (rec['fft']))])
        elif 'hidden' in rec:
            if re.search('^http', rec['hidden']) or re.search('^\/afs\/cern', rec['hidden']):
                xmlstring += marcxml('FFT',[('a',rec['hidden']), ('d','Fulltext'), ('o', 'HIDDEN')])
            else:
                xmlstring += marcxml('595', [('a', 'invalid link "%s"' % (rec['hidden']))])
        #LINK
        if 'link' in rec:
            if re.search('^http', rec['link']):
                xmlstring += marcxml('8564',[('u', rec['link'])])
            else:
                xmlstring += marcxml('595', [('a', 'invalid link "%s"' % (rec['link']))])
        #LICENSE
        if 'license' in rec and not 'licence' in rec:
            rec['licence'] = rec['license']
        if 'licence' in rec:
            entry = []
            if 'statement' in rec['licence']:
                entry.append(('a',rec['licence']['statement']))
            elif 'url' in rec['licence'] and re.search('creativecommons.org', rec['licence']['url']):
                if re.search('\/zero\/', rec['licence']['url'].lower()):
                    statement = 'CC-0'
                else:
                    statement = re.sub('.*licen[cs]es', 'CC', rec['licence']['url']).upper()
                    statement = re.sub('.LEGALCODE', '', statement)
                    statement = re.sub('.DEED...', '', statement)
                entry.append(('a', re.sub('\/', '-', re.sub('\/$', '', statement))))
            if 'url' in rec['licence']:
                entry.append(('u',rec['licence']['url']))
            if 'organization' in rec['licence']:
                entry.append(('b',rec['licence']['organization']))
            elif entry:
                entry.append(('b', publisher))
            if 'material' in rec['licence']:
                entry.append(('3',rec['licence']['material']))
            try:
                xmlstring += marcxml('540', entry)
            except:
                xmlstring += marcxml(marc, [(tup[0], unidecode.unidecode(tup[1])) for tup in entry])
        #SUPERVISOR
        if 'supervisor' in rec:
            marc = '701'
            for autaff in rec['supervisor']:
                autlist = [('a',shapeaut(autaff[0]))]
                for aff in autaff[1:]:
                    if re.search('ORCID', aff):
                        aff = re.sub('\s+', '', aff)
                        if reorcid.search(aff):
                            autlist.append(('j', aff))
                        else:
                            print(' "%s" is not a valid ORCID' % (aff))
                    elif re.search('EMAIL', aff):
                        if re.search('@', aff):
                            autlist.append(('m', re.sub('EMAIL:', '', aff)))
                    else:
                        autlist.append(('v', aff))
                try:
                    xmlstring += marcxml(marc, autlist)
                except:
                    autlist2 = [(tup[0], unidecode.unidecode(tup[1])) for tup in autlist]
                    xmlstring += marcxml(marc, autlist2)
        #AUTHORS
        if 'autaff' in rec:
            marc = '100'
            for autaff in rec['autaff']:
                grids = []
                #check for collaborations
                if re.search('Collaboration', autaff[0], re.IGNORECASE):
                    newcolls = []
                    (coll, author) = coll_cleanforthe(autaff[0])
                    for scoll in coll_split(coll):
                        newcolls.append(re.sub('^the ', '', coll_clean710(scoll), re.IGNORECASE))
                    for col in newcolls:
                        xmlstring += marcxml('710',[('g',col)])
                        if 'exp' not in rec and col in colexpdict:
                            xmlstring += marcxml('693',[('e',colexpdict[col])])
                    if author:
                        autaff[0] = author
                    else:
                        continue
                if re.search('\([eE]d\.\)', autaff[0]):
                    autlist = [('a', shapeaut(re.sub(' *\([eE]d\.\) *','',autaff[0]))), ('e','ed.')]
                else:
                    autlist = [('a',shapeaut(autaff[0]))]
                for aff in autaff[1:]:
                    if re.search('ORCID', aff):
                        aff = re.sub('\s+', '', aff)
                        if reorcid.search(aff):
                            autlist.append(('j', aff))
                        else:
                            print(' "%s" is not a valid ORCID' % (aff))
                    elif re.search('EMAIL', aff):
                        if re.search('@', aff):
                            autlist.append(('m', re.sub('EMAIL:', '', aff)))
                    else:
                        #GRID hier
                        if re.search(', GRID:', aff):
                            autlist.append(('v',  re.sub(', GRID:.*', '', aff)))
                            grid = re.sub('.*, GRID:', 'GRID:', aff)
                            if not grid in grids:
                                autlist.append(('t', grid))
                                grids.append(grid)
                        else:
                            autlist.append(('v', aff))
                try:
                    xmlstring += marcxml(marc, autlist)
                except:
                    print(rec['link'])
                    print(autlist)
                    autlist2 = [(tup[0], unidecode.unidecode(tup[1])) for tup in autlist]
                    xmlstring += marcxml(marc, autlist2)
                marc = '700'
        elif 'auts' in rec:
            affdict = {}
            tempaffs = []
            if 'aff' in rec:
                for aff in rec['aff']:
                    if re.search('=',aff):
                        parts = re.split('= *',aff)
                        affdict[parts[0]] = parts[1]
                    else:
                        tempaffs.append(('v',aff))
            #print affdict
            longauts = []
            rec['auts'].reverse()
            preventry = ' '
            for entry in rec['auts']:
                if entry == '':
                    continue
                #print '--', entry
                if entry[0] == '=':
                    if preventry[0] != '=':
                        tempaffs = []
                    affs = re.split('; ',entry)
                    affs.reverse()
                    for aff in affs:
                        if aff[1:] in affdict:
                            tempaffs.insert(0,('v',affdict[aff[1:]]))
                    #print tempaffs
                else:
                    #check for collaborations
                    if re.search('Collaboration', entry, re.IGNORECASE):
                        newcolls = []
                        (coll, author) = coll_cleanforthe(entry)
                        coll = re.sub(', ORCID.*', '', coll)
                        for scoll in coll_split(coll):
                            newcolls.append(re.sub('^the ', '', coll_clean710(scoll), re.IGNORECASE))
                        for col in newcolls:
                            if not re.search('(CHINESENAME|ORCID|EMAIL)', col):
                                xmlstring += marcxml('710',[('g',col)])
                                if 'exp' not in rec and col in colexpdict:
                                    xmlstring += marcxml('693',[('e',colexpdict[col])])
                        if author:
                            entry = author
                        else:
                            continue
                    if re.search('\([eE]d\.\)',entry):
                        aut = [('a', shapeaut(re.sub(' *\([eE]d\.\) *','',entry))), ('e','ed.')]
                    else:
                        author = entry
                        aut = []
                        if re.search('CHINESENAME', author):
                            aut.append(('q', re.sub('.*, CHINESENAME: ', '', author)))
                            author = re.sub(' *, CHINESENAME.*', '', author)
                        if re.search('ORCID', author):
                            orcid = re.sub('\s+', '', re.sub('\.$', '', re.sub('.*, ORCID',  'ORCID', author)))
                            if reorcid.search(orcid):
                                aut.append(('j', orcid))
                            else:
                                print(' "%s" is not a valid ORCID' % (orcid))
                            author = re.sub(' *, ORCID.*', '', author)
                        elif re.search('EMAIL', author):
                            if re.search('@', author):
                                aut.append(('m', re.sub('.*, EMAIL:',  '', author)))
                            author = re.sub(', EMAIL.*', '', author)
                        elif re.search('INSPIRE', author):
                            aut.append(('i', re.sub('.*, INSPIRE', 'INSPIRE', author)))
                            author = re.sub(', INSPIRE.*', '', author)
                        aut.append(('a', shapeaut(author)))
                    if (len(tempaffs) == 0) and (len(affdict) > 0):
                        tempaffs = [('v',affdict[list(affdict.keys())[0]])]
                    #GRID hier
                    ntempaffs = []
                    grids = []
                    for ta in tempaffs:
                        if re.search(', GRID:', ta[1]):
                            ntempaffs.append(('v', re.sub(', GRID:.*', '', ta[1])))
                            grid = re.sub('.*, GRID:', 'GRID:', ta[1])
                            if not grid in grids:
                                ntempaffs.append(('t', grid))
                                grids.append(grid)
                        else:
                            ntempaffs.append(ta)
                    longauts.insert(0,aut+ntempaffs)
                preventry = entry
            marc = '100'
            for aut in longauts:
                xmlstring += marcxml(marc,aut)
                marc = '700'
        #REFERENCES
        if 'refs' in rec:
            print(' extracting %i refs for record %i of %i' % (len(rec['refs']),i,len(recs)))
            for ref in rec['refs']:
                #print '  ->  ', ref
                if len(ref) == 1 and ref[0][0] == 'x':
                    rawref = re.sub('Google ?Scholar', '', ref[0][1])
                    rawref = re.sub('[cC]ross[rR]ef', '', rawref)
                    rawref = re.sub('[\n\t\r]', ' ', rawref)
                    rawref = re.sub('  +', ' ', rawref)
                    rawref = normalizejournalsworkaround(rawref)
                    rawref = re.sub('\xc2\xa0', ' ', rawref)
                    rawref = re.sub('\xa0', ' ', rawref)
                    try:
                        extractedrefs = repairptep(extract_references_from_string(rawref, override_kbs_files={'journals': journalskb}, reference_format="{title},{volume},{page}"))
                        for ref2 in extractedrefs:
                            #find additional reportnumbers
                            additionalreportnumbers = []
                            if 'misc' in ref2:
                                for misc in ref2['misc']:
                                    if repreprints.search(misc):
                                        for preprint in re.split(', ', repreprints.sub(r'\1', misc)):
                                            if repreprint.search(preprint):
                                                additionalreportnumbers.append(('r', re.sub('[\/ ]', '-', preprint)))
                            #translate refeextract output
                            entryaslist = [('9','refextract')]
                            for key in ref2:
                                if key in mappings:
                                    for entry in ref2[key]:
                                        entryaslist.append((mappings[key], entry))
                            if len(extractedrefs) == 1:
                                if re.search('inspirehep.net\/record\/\d+', rawref):
                                    entryaslist.append(('0', re.sub('.*inspirehep.net\/record\/(\d+).*', r'\1',  rawref)))
                            xmlstring += marcxml('999C5', entryaslist + additionalreportnumbers)
                    except:
                        #print 'UTF8 Problem in Referenzen'
                        try:
                            ref01 = str(unicodedata.normalize('NFKD', re.sub('??', 'ss', rawref)).encode('ascii', 'ignore'), 'utf-8')
                            extractedrefs = repairptep(extract_references_from_string(ref01, override_kbs_files={'journals': journalskb}, reference_format="{title},{volume},{page}"))
                            for ref2 in extractedrefs:
                                #find additional reportnumbers
                                additionalreportnumbers = []
                                if 'misc' in ref2:
                                    for misc in ref2['misc']:
                                        if repreprints.search(misc):
                                            for preprint in re.split(', ', repreprints.sub(r'\1', misc)):
                                                if repreprint.search(preprint):
                                                    additionalreportnumbers.append(('r', re.sub('[\/ ]', '-', preprint)))
                                #translate refeextract output
                                entryaslist = [('9','refextract')]
                                for key in ref2:
                                    if key in mappings:
                                        for entry in ref2[key]:
                                            entryaslist.append((mappings[key], entry))
                                if len(extractedrefs) == 1:
                                    if re.search('inspirehep.net\/record\/\d+', rawref):
                                        entryaslist.append(('0', re.sub('.*inspirehep.net\/record\/(\d+).*', r'\1',  rawref)))
                                xmlstring += marcxml('999C5', entryaslist + additionalreportnumbers)
                        except:
                            print('real UTF8 Problem in Referenzen')
                            xmlstring += marcxml('595', [('a', 'real UTF8 Problem in Referenzen')])
                else:
                    cleanref = []
                    for part in ref:
                        if part[0] == 'r':
                            if rearxivhttpold.search(part[1]):
                                cleanref.append(('r', rearxivhttpold.sub(r'\1', part[1])))
                            elif rearxivhttpnew.search(part[1]):
                                cleanref.append(('r', rearxivhttpnew.sub(r'arxiv:\1', part[1])))
                            elif rearxivnewshort.search(part[1]):
                                cleanref.append(('r', 'arxiv:' + part[1]))
                            else:
                                cleanref.append(part)
                        else:
                            cleanref.append(part)
                    xmlstring += marcxml('999C5',ref)
        xmlstring += marcxml('980',[('a','HEP')])
        #COMMENTS
        #temporary informations used for selection process
        if 'comments' in rec:
            for comment in rec['comments']:
                xmlstring += marcxml('595',[('a',comment)])
        if 'note' in rec:
            if not 'fc' in rec:
                for comment in rec['note']:
                    if refcmp.search(comment):
                        rec['fc'] = 'm'
                        rec['note'].append('added fieldcode by note')
                    elif refcp.search(comment):
                        pass # ignore things like 'School of Mathematics and Physics'
                    elif refcm.search(comment):
                        rec['fc'] = 'm'
                        rec['note'].append('added fieldcode by note')
                    elif refca.search(comment):
                        rec['fc'] = 'a'
                        rec['note'].append('added fieldcode by note')
                    elif refck.search(comment):
                        rec['fc'] = 'k'
                        rec['note'].append('added fieldcode by note')
#                    elif refcc.search(comment):
#                        rec['fc'] = 'c'
#                        rec['note'].append('added fieldcode by note')
            for comment in rec['note']:
                try:
                    xmlstring += marcxml('595', [('a', comment)])
                except:
                    xmlstring += marcxml('595', [('a', unidecode.unidecode(comment))])
        if 'typ' in rec:
            xmlstring += marcxml('595',[('a',rec['typ'])])
        #FIELD CODE
        if rec['jnl'] in jnltofc:
            if not 'fc' in rec:
                rec['fc'] = ''
            for fc in jnltofc[rec['jnl']]:
                print('  FC:', rec['jnl'], fc)
                if not fc in ['fc']:
                    rec['fc'] += fc
        if 'fc' in rec:
            for fc in rec['fc']:
                xmlstring += marcxml('65017',[('a',inspirefc[fc]),('2','INSPIRE')])
        #THESIS PUBNOTE
        if 'T' in rec['tc'] and not re.search('"502"', xmlstring):
            thesispbn = [('b', 'PhD')]
            if 'autaff' in rec and len(rec['autaff'][0]) > 1:
                for aff in rec['autaff'][0][1:]:
                    if not re.search('EMAIL', aff) and not re.search('ORCID', aff):
                        thesispbn.append(('c', aff))
            elif 'aff' in rec and rec['aff']:
                thesispbn.append(('c', rec['aff'][0]))
            if 'date' in rec:
                thesispbn.append(('d', re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])))
            xmlstring += marcxml('502', thesispbn)
        xmlstring += '</record>\n'
        try:
            dokfile.write(xmlstring)
        except:
            dokfile.write(xmlstring.encode("utf8", "ignore"))
    dokfile.write('</collection>\n')
    return


rebindestrich = re.compile('([A-Z] ?\.)[ \-]([A-Z] ?\.?)')
revan1a = re.compile('(.*) (van den|van der|van de|de la) (.*)')
revan2a = re.compile('(.*) (van|van|de|von|del|du) (.*)')
revan1b = re.compile('(.*) (van den|van der|van de|de la)$')
revan2b = re.compile('(.*) (van|van|de|von|del|du)$')
reswap = re.compile('(.*) (.*)')
def shapeaut(author):
    author = re.sub('\&nbps;', ' ', author)
    author = re.sub('\xa0', ' ', author)
    if re.search(' ',  author):
        if not re.search(',', author):
            if revan1a.search(author):
                author = revan1a.sub(r'\2 \3, \1',author).strip()
            elif revan2a.search(author):
                author = revan2a.sub(r'\2 \3, \1',author).strip()
            else:
                author = reswap.sub(r'\2, \1',author).strip()
        else:
            author = revan1b.sub(r'\2 \1', author)
            author = revan2b.sub(r'\2 \1', author)
    author = re.sub(' ([A-Z]) ',r' \1. ', author)
    author = rebindestrich.sub(r'\1\2', author)
    author = re.sub(', *', ', ', author.strip())
    if not re.search('[a-z]', author):
        author = author.title()
    author = re.sub('([A-Z])$',r'\1.', author)
    return author



reqis = re.compile('^\d+ *')
untitles = ['Calendar', 'Author Index', 'Editorial', 'News', 'Index', 'Spotlights on Recent JACS Publications',
            'Guest Editorial', 'Personalia, meetings, bibliography',
            'Changes to the Editorial Board', 'Preface', 'Obituary', 'Foreword', 'Replies']
potentialuntitles = [re.compile('[pP]reface'), re.compile('[iI]n [mM]emoriam'), re.compile('Congratulations'),
                     re.compile('[cC]ouncil [iI]nformation'), re.compile('[jJ]ournal [cC]over'),
                     re.compile('[Aa]uthor [iI]ndex'), re.compile('[bB]ack [mM]atter'), re.compile('Message'),
		     re.compile('[fF]ront [mM]atter'), re.compile('Welcome'), re.compile('Committee'),
                     re.compile('[iI]nformation for [aA]authors'), re.compile('[pP]ublication [iI]nofrmation'),
                     re.compile('Workshops'), re.compile('^In [mM]emory'), re.compile(' [bB]irthday'),
                     re.compile('[kK]eynote [sS]peaker'), re.compile('Schedule'), re.compile('[Pp]lenary [sS]peaker')]
def writenewXML(recs, publisher, jnlfilename, xmldir='/afs/desy.de/user/l/library/inspire/ejl', retfilename='retfiles'):
    global checkedmetatags    
    uniqrecs = []
    doi1s = []
    for rec in recs:
        #clean persistent identifiers
        if 'doi' in rec.keys() and rec['doi'] and not rec['doi'][:3] == '10.':
            rec['doi'] = re.sub('.*doi.org\/', '', rec['doi'])
            rec['doi'] = re.sub('doi:(10\.\d+\/)', r'\1', rec['doi'])
        if 'hdl' in rec.keys() and rec['hdl'] and not re.search('^\d+\/', rec['hdl']):
            rec['hdl'] = re.sub('.*handle.net\/', '', rec['hdl'])
        #remove link if DOI
        if 'doi' in rec and 'link' in rec:
            if re.search('^10\.\d+', rec['doi']):
                del(rec['link'])
        #open access fulltext
        if 'pdf_url' in rec.keys():
            if 'license' in rec.keys() or 'licence' in rec.keys():
                rec['FFT'] = rec['pdf_url']
            elif 'oa' in rec and rec['oa']:
                rec['FFT'] = rec['pdf_url']
            else:
                rec['hidden'] = rec['pdf_url']
        #add doki file name
        if 'note' in rec:
            rec['note'].append('DOKIFILE:'+jnlfilename)
        else:
            rec['note'] = ['DOKIFILE:'+jnlfilename]
        #QIS keywords
        doi1 = False
        if 'doi' in rec:
            doi1 = re.sub('[\(\)\/]', '_', rec['doi'])
        elif 'hdl' in rec:
            doi1 = re.sub('[\(\)\/]', '_', rec['hdl'])
        elif 'urn' in rec:
            doi1 = re.sub('[\(\)\/]', '_', rec['urn'])
        else:
            pseudodoi = False
            if 'isbn' in rec and rec['isbn']:
                pseudodoi = '20.2000/ISBN/' + rec['isbn']
            elif 'isbns' in rec and rec['isbns']:
                pseudodoi = '20.2000/ISBNS'
                for tupel in rec['isbns'][0]:
                    if tupel[0] == 'a':
                        pseudodoi += '/' + tupel[1]
            elif ('vol' in rec or 'cnum' in rec) and 'p1' in rec:
                pseudodoi = '20.2000/PBN'
                for pbnkey in ['jnl', 'vol', 'issue', 'year', 'p1', 'p2', 'cnum']:
                    if pbnkey in rec:
                        pseudodoi += '/' + re.sub('\W', '', rec[pbnkey])
            elif 'link' in rec:
                pseudodoi = '20.2000/LINK/' + re.sub('\W', '', rec['link'][4:])        
            elif 'tit' in rec:
                pseudodoi = '30.3000/AUT_TIT'
                if 'auts' in rec and rec['auts']:
                    pseudodoi += '/' + re.sub('\W', '', rec['auts'][0])
                elif 'autaff' in rec and rec['autaff'] and rec['autaff'][0]:
                    pseudodoi += '/' + re.sub('\W', '', rec['autaff'][0][0])
            if pseudodoi:
                rec['doi'] = pseudodoi
                doi1 = re.sub('[\(\)\/]', '_', rec['doi'])
                if 'artlink' in rec and not 'link' in rec:
                    rec['link'] = rec['artlink']
        if doi1:
            absfilename = os.path.join(absdir, doi1)
            bibfilename = os.path.join(tmpdir, doi1+'.qis.bib')
            if not os.path.isfile(absfilename):
                absfile = codecs.open(absfilename, mode='wb', encoding='utf8')
                try:
                    if 'tit' in rec:
                        try:
                            absfile.write(rec['tit'] + '\n\n')
                        except:
                            absfile.write(unidecode.unidecode(rec['tit']) + '\n\n')
                    if 'abs' in rec:
                        try:
                            absfile.write(rec['abs'] + '\n\n')
                        except:
                            absfile.write(unidecode.unidecode(rec['abs']) + '\n\n')
                    if 'keyw' in rec:
                        for kw in rec['keyw']:
                            try:
                                absfile.write(kw + '\n')
                            except:
                                absfile.write(unidecode.unidecode(kw) + '\n')
                except:
                    print('   could not write abstract to file')
                absfile.close()
            time.sleep(.3)
            if not os.path.isfile(bibfilename):
                print(' >bibclassify %s' % (doi1))
                try:
                    os.system('%s %s > %s' % (qisbibclassifycommand, absfilename, bibfilename))
                except:
                    print('FAILURE: %s %s > %s' % (qisbibclassifycommand, absfilename, bibfilename))
            qiskws = []
            if os.path.isfile(bibfilename):
                absbib = open(bibfilename, 'r')
                lines = absbib.readlines()
                for line in lines:
                    if reqis.search(line):
                        qiskws.append('[QIS] ' + line.strip())
                absbib.close()
            if qiskws:
                if not 'note' in rec:
                    rec['note'] = []
                rec['note'].append('%i QIS keywords found' % (len(qiskws)))
                print('   %i QIS keywords found' % (len(qiskws)))
                for qiskw in qiskws:
                    rec['note'].append(qiskw)
                if 'fc' in rec:
                    if not 'k' in rec['fc']:
                        rec['fc'] += 'k'
                else:
                    rec['fc'] = 'k'
            #check for "un"titles
            keepit = True
            if 'tit' in rec:
                if rec['tit'] in untitles:
                    keepit = False
                elif (not ('auts' in rec and rec['auts'])) and (not ('autaff' in rec and rec['autaff'])):
                    for pu in potentialuntitles:
                        if pu.search(rec['tit']):
                            keepit = False
                            break
            if doi1 in doi1s:
                print('--', doi1)
            elif keepit:
                print('>>', doi1)
                uniqrecs.append(rec)
                doi1s.append(doi1)
            else:
                print('--', doi1)
    if uniqrecs:
        xmlf = os.path.join(xmldir, jnlfilename+'.xml')
        xmlfile = codecs.open(xmlf, mode='wb', encoding='utf8')
        writeXML(uniqrecs, xmlfile, publisher)
        xmlfile.close()
        if checkedmetatags:
            print ('METATAGS: ' + ' | '.join(['%s %i/%i' % (k, checkedmetatags[k], len(recs)) for k in checkedmetatags]))
        #count datafields
        datafields = {}
        for rec in uniqrecs:
            for rk in rec:
                if rec[rk]:
                    if rk in datafields:
                        datafields[rk] += 1
                    else:
                        datafields[rk] = 1
        datafieldsoutBIG = []
        datafieldsout = []
        for rk in datafields:
            if datafields[rk] == len(uniqrecs):
                dfo = '%s(all)' % (rk)
            else:
                dfo = '%s(%i)' % (rk, datafields[rk])
            if rk in ['autaff', 'date', 'tit', 'auts']:
                datafieldsoutBIG.append(dfo.upper())
            else:
                datafieldsout.append(dfo)
        print('FINISHED writenewXML(%s;%i;%s || %s)' % (jnlfilename, len(uniqrecs), '|'.join(datafieldsoutBIG), '|'.join(datafieldsout)))
        #write retrival
        retfiles_text = open(os.path.join(retfiles_path, retfilename), "r").read()
        line = jnlfilename+'.xml'+ "\n"
        if not line in retfiles_text:
            retfiles = open(os.path.join(retfiles_path, retfilename), "a")
            retfiles.write(line)
            retfiles.close()
    return

#prints a progress line with some information
def printprogress(character, information):
    output = 3*character
    for subinfo in information:
        output += '{ %s }' % (' / '.join([str(fragment) for fragment in subinfo]))
        output += 3*character
    print(output)
    return output

#prints summary of record or full record
def printrecsummary(rec):
    output = []
    for k in rec.keys():
        try:
            output.append('%s[%i]' % (k, len(rec[k])))
        except:
            output.append('%s' % (k))
    print('  ', ', '.join(output))
    return
def printrec(rec):
    if rec:
        for k in rec:        
            print ('%-10s:: ' % (k), rec[k])
        printrecsummary(rec)
    else:
        print('-empty-record-')
    return

#gives the date
now = datetime.datetime.now()
def stampoftoday():
    return '%4d-%02d-%02d' % (now.year, now.month, now.day)
def year(backwards=0):
    return now.year-backwards

#gives the year, day, and time
def stampofnow():
    return time.strftime("%Y-%03j-%H%M", time.localtime())

#check whole page for CC license
def globallicensesearch(rec, artpage):
    #try check for simple a-tags
    if not 'license' in rec:
        for a in artpage.body.find_all('a'):
            if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                rec['license'] = {'url' : a['href']}
                if 'pdf_url' in rec:
                    rec['FFT'] = rec['pdf_url']
                elif 'hidden' in rec:
                    rec['FFT'] = rec['hidden']
                    del rec['hidden']
    #look for javascript hidden links
    if not 'license' in rec:
        for script in artpage.find_all('script', attrs = {'type' : 'text/javascript'}):
            sstring = re.sub('[\n\t\r]', '', script.text)
            if re.search('license.*http.*creativecommons.org\/licen', sstring):
                rec['license'] = {'url' : re.sub('.*license.*(http.*?creativecommons.org\/licen.*?)["\'].*', r'\1', sstring)}
                if 'pdf_url' in rec:
                    rec['FFT'] = rec['pdf_url']
                elif 'hidden' in rec:
                    rec['FFT'] = rec['hidden']
                    del rec['hidden']
    return

#gets informations from meta tags of webpage
#needs a list of tags to look for (as meta-tags are not as standardized as one would wish)
checkedmetatags = {}
def metatagcheck(rec, artpage, listoftags):
    global checkedmetatags
    for tag in listoftags:
        if not tag in checkedmetatags:
            checkedmetatags[tag] = 0
    done = []
    for meta in artpage.find_all('meta'):
        if meta.has_attr('content') and meta['content']:
            if meta.has_attr('name') and meta['name'] in listoftags:
                tag = meta['name']
            elif meta.has_attr('property') and meta['property'] in listoftags:
                tag = meta['property']
            else:
                tag = False
            if tag:
                #abstract
                if tag in ['abstract', 'citation_abstract', 'dc.description', 'dc.Description', 'DC.description', 'DC.Description',
                           'dcterms.abstract', 'DCTERMS.abstract','twitter:description', 'og:description', 'eprints.abstract',
                           'description', 'citation_abstract_content']:
                    rec['abs'] = meta['content']
                    done.append(tag)
                #persistant identifiers
                elif tag in ['bepress_citation_doi', 'citation_doi', 'Citation_DOI_Number', 'DC.Identifier.doi',  'DC.Identifier.DOI']:
                    rec['doi'] = meta['content']
                    done.append(tag)
                elif tag in ['citation_arxiv_id']:
                    rec['arxiv'] = meta['content']
                    done.append(tag)
                elif tag in ['citation_isbn']:
                    if 'isbns' in rec:
                        rec['isbns'].append([('a', re.sub('\D', '', meta['content']))])
                    else:
                        rec['isbns'] = [ [('a', re.sub('\D', '', meta['content']))] ]
                    done.append(tag)
                elif tag in ['dc.identifier', 'dc.Identifier', 'DC.identifier', 'DC.Identifier']:
                    if re.search('^(urn|URN):', meta['content']):
                        rec['urn'] = meta['content']
                        done.append(tag)
                    elif re.search('^(uri|URI):', meta['content']):
                        rec['uri'] = meta['content']
                        done.append(tag)
                    elif re.search('handle.net\/', meta['content']):
                        rec['hdl'] = re.sub('.*handle.net\/', '', meta['content'])
                        done.append(tag)
                    elif re.search('doi.org\/10', meta['content']):
                        rec['doi'] = re.sub('.*doi.org\/(10.*)', r'\1', meta['content'])
                        done.append(tag)
                    elif re.search('doi:10\.\d', meta['content']):
                        rec['doi'] = re.sub('.*doi:\/(10.*)', r'\1', meta['content'])
                        done.append(tag)
                    elif re.search('^10\.\d+\/', meta['content']):
                        rec['doi'] = meta['content']
                        done.append(tag)
                    elif re.search('^978', meta['content']):
                        if 'isbns' in rec:
                            rec['isbns'].append([('a', re.sub('\D', '', meta['content']))])
                        else:
                            rec['isbns'] = [ [('a', re.sub('\D', '', meta['content']))] ]
                        done.append(tag)
                #language
                elif tag in ['citation_language', 'dc.language', 'dc.Language', 'DC.language', 'DC.Language', 'language']:
                    rec['language'] = meta['content']
                    done.append(tag)
                #author
                elif tag in ['bepress_citation_author', 'citation_author', 'Citation_Author', 'eprints.creators_name',
                             'dc.Creator', 'DC.creator', 'DC.Creator', 'DC.Creator.PersonalName',
                             'DC.contributor.author']:
                    if 'autaff' in rec:
                        rec['autaff'].append([meta['content']])
                    else:
                        rec['autaff'] = [[meta['content']]]
                    done.append(tag)
                elif tag in ['DC.contributor.advisor', 'DC.contributor', 'eprints.supervisors_name']:
                    if 'supervisor' in rec:
                        rec['supervisor'].append([meta['content']])
                    else:
                        rec['supervisor'] = [[meta['content']]]
                    done.append(tag)
                elif tag in ['bepress_citation_author_institution', 'citation_author_institution', 'citation_editor_institution',
                             'citation_dissertation_institution']:
                    rec['autaff'][-1].append(meta['content'])
                    done.append(tag)
                elif tag in ['citation_author_email', 'citation_editor_email']:
                    rec['autaff'][-1].append('EMAIL:' + meta['content'])
                    done.append(tag)
                elif tag in ['citation_author_orcid', 'citation_editor_orcid']:
                    rec['autaff'][-1].append('ORCID:' + re.sub('.*\/', '', meta['content']))
                    done.append(tag)
                elif tag in ['citation_editor']:
                    if 'autaff' in rec:
                        rec['autaff'].append([meta['content'].title() + ' (Ed.)'])
                    else:
                        rec['autaff'] = [[meta['content'].title() + ' (Ed.)']]
                    done.append(tag)
                #title
                elif tag in ['bepress_citation_title', 'Citation_Article_Title', 'citation_title', 'eprints.title',
                             'twitter:title', 'dc.Title', 'DC.title', 'DC.Title', 'og:title']:
                    rec['tit'] = meta['content']
                    done.append(tag)
                #date
                elif tag in ['dc.date', 'dc.Date', 'DC.date', 'DC.Date.created', 'bepress_citation_date',
                             'bepress_citation_online_date', 'citation_cover_date', 'citation_date', 'eprints.date',
                             'citation_publication_date', 'DC.Date.issued', 'dc.onlineDate', 'dcterms.date',
                             'DCTERMS.issued']:
                    rec['date'] = meta['content']
                    done.append(tag)
                #pubnote
                elif tag in ['citation_lastpage', 'bepress_citation_lastpage']:
                    rec['p2'] = meta['content']
                    done.append(tag)
                elif tag in ['citation_firstpage', 'bepress_citation_firstpage']:
                    rec['p1'] = meta['content']
                    done.append(tag)
                elif tag in ['citation_issue']:
                    rec['issue'] = meta['content']
                    done.append(tag)
                elif tag in ['citation_num_pages', 'DCTERMS.extent']:
                    if re.search('^d+$', meta['content']):
                        rec['pages'] = meta['content']
                        done.append(tag)
                    elif re.search('\d\d', meta['content']):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', meta['content'])
                        done.append(tag)
                elif tag in ['citation_year', 'Citation_Year']:
                    rec['year'] = meta['content']
                    done.append(tag)
                elif tag in ['citation_volume']:
                    rec['vol'] = meta['content']
                    done.append(tag)
                #license
                elif tag in ['dc.rights', 'DC.rights', 'DC.Rights', 'DCTERMS.URI']:
                    if re.search('creativecommons.org', meta['content']):
                        rec['license'] = {'url' : meta['content']}
                        done.append(tag)
                    elif re.search('^cc_[a-z][a-z].*', meta['content']):
                        rec['license'] = {'statement' : re.sub('_', '-', meta['content'].upper())}
                        done.append(tag)
                #keywords
                elif tag in ['Citation_Keyword', 'citation_keywords', 'dc.keywords', 'dc.subject',
                             'dc.Subject', 'DC.subject', 'DC.Subject', 'keywords', 'eprints.keywords',
                             'keywords']:
                    if 'keyw' in rec:
                        if not meta['content'] in rec['keyw']:
                            rec['keyw'].append(meta['content'])
                    else:
                        rec['keyw'] = [meta['content']]
                    done.append(tag)
                #fulltext
                elif tag in ['bepress_citation_pdf_url', 'citation_pdf_url', 'eprints.document_url']:
                    rec['pdf_url'] = meta['content']
                    done.append(tag)
    #resume
    notdone = []
    for tag in listoftags:
        if tag in done:
            checkedmetatags[tag] += 1
        else:
            notdone.append(tag)
    if notdone:
        print("   %i of %i tags not found (%s)" % (len(notdone), len(listoftags), ', '.join(notdone)))
    return

#write entry in retfiles
def writeretrival(jnlfilename, retfilename='retfiles'):
    retfiles_text = open(os.path.join(retfiles_path, retfilename), "r").read()
    line = jnlfilename+'.xml'+ "\n"
    if not line in retfiles_text:
        retfiles = open(os.path.join(retfiles_path, retfilename), "a")
        retfiles.write(line)
        retfiles.close()

#uninteresting DOIs
inf = open('/afs/desy.de/user/l/library/dok/ejl/uninteresting.dois', 'r')
uninterestingDOIS = []
newuninterestingDOIS = []
for line in inf.readlines():
    uninterestingDOIS.append(line.strip())
inf.close()
def ckeckinterestingDOI(doi):
    if doi in uninterestingDOIS:
        return False
    else:
        return True
def adduninterestingDOI(doi):
    ouf = open('/afs/desy.de/user/l/library/dok/ejl/uninteresting.dois', 'a')
    ouf.write(doi + '\n')
    ouf.close()
    return


#standard DSPace
def getdspacerecs(tocpage, urltrunc, fakehdl=False):
    rehdl = re.compile('.*handle\/')
    reyear = re.compile('.*([12]\d\d\d).*')
    redegree = re.compile('rft.degree=')
    redate = re.compile('rft.date=')
    relicense = re.compile('rft.rights=(http.*creativecommons.org.*)')
    recs = []
    divs = tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'})
    links = []
    for div in divs:
        for a in div.find_all('a'):
            if a.has_attr('href') and rehdl.search(a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'keyw' : [], 'note' : [], 'autaff' : [], 'degree' : []}
                rec['soup'] = div
                rec['tit'] = a.text.strip()
                rec['link'] = urltrunc + a['href']
                #some have year in <span class="date">
                for span in div.find_all('span', attrs = {'class' : 'date'}):
                    if reyear.search(span.text):
                        rec['year'] = reyear.sub(r'\1', span.text.strip())
                #some have department in <div class="publisher">
                for div2 in div.find_all('div', attrs = {'class' : 'publisher'}):
                    rec['dep'] = div2.text.strip()
                #some have infos in <span class="Z3988">
                for span in div.find_all('span', attrs = {'class' : 'Z3988'}):
                    infos = re.split('&', span['title'])
                    for info in infos:
                        if redegree.search(info):
                            rec['degree'].append(redegree.sub('', info))
                        elif relicense.search(info):
                            rec['license'] = re.sub('%3A', ':', re.sub('%2F', '/', relicense.sub(r'\1', info)))
                        elif redate.search(info):
                            rec['date'].append(redate.sub('', info))
                #construct link and HDL (or fakeDOI)
                if not rec['link'] in links:
                    links.append(rec['link'])
                    if fakehdl:
                        rec['doi'] = '30.3000/' + re.sub('\W', '',  urltrunc) + rehdl.sub('/', a['href'])
                        if ckeckinterestingDOI(rec['link']):
                            recs.append(rec)
                    else:
                        rec['hdl'] = rehdl.sub('', a['href'])
                        if ckeckinterestingDOI(rec['hdl']):
                            recs.append(rec)
    print('  [getdspacerecs] %i/%i' % (len(recs), len(divs)))
    return recs


