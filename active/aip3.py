# -*- coding: utf-8 -*-
#program to harvest AIP-journals
# FS 2015-02-11

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import random
import datetime
regexpref = re.compile('[\n\r\t]')

publisher = 'AIP'
typecode = 'P'
skipalreadyharvested = True
jnl = sys.argv[1]
vol = sys.argv[2]
jnlfilename = jnl+vol+'_'+ejlmod3.stampoftoday()
cnum = False
if len(sys.argv) > 3: 
    iss = sys.argv[3]
    jnlfilename = jnl + vol + '.' + iss + '_'+ejlmod3.stampoftoday()
if len(sys.argv) > 4:
    cnum = sys.argv[4]
    jnlfilename = jnl + vol + '.' + iss + '_' + cnum + '_'+ejlmod3.stampoftoday()
if   (jnl == 'rsi'): 
    jnlname = 'Rev.Sci.Instrum.'
elif (jnl == 'jmp'):
    jnlname = 'J.Math.Phys.'
elif (jnl == 'chaos'):
    jnlname = 'Chaos'
elif (jnl == 'ajp'):
    jnlname = 'Am.J.Phys.'
elif (jnl == 'ltp'):
    jnlname = 'Low Temp.Phys.'
    jnlname2 = 'Fiz.Nizk.Temp.'
elif (jnl == 'php'):
    jnlname = 'Phys.Plasmas'
elif (jnl == 'adva'):
    jnlname = 'AIP Adv.'
elif (jnl == 'aipconf') or (jnl == 'aipcp') or (jnl == 'apc'):
    jnlname = 'AIP Conf.Proc.'
    jnl = 'apc'
    typecode = 'C'
elif (jnl == 'apl'):
    jnlname = 'Appl.Phys.Lett.'
elif (jnl == 'jap'):
    jnlname = 'J.Appl.Phys.'
elif (jnl == 'jcp'):
    jnlname = 'J.Chem.Phys.'
elif (jnl == 'phf'):
    jnlname = 'Phys.Fluids'
elif (jnl == 'jva'):
    jnlname = 'J.Vac.Sci.Tech.A'
elif (jnl == 'jvb'):
    jnlname = 'J.Vac.Sci.Tech.B'
elif (jnl == 'aqs'):
    jnlname = 'AVS Quantum Sci.'
elif (jnl == 'app'):
    jnlname = 'APL Photonics?'
elif (jnl == 'sci'):
    jnlname = 'Scilight?'
elif (jnl == 'pto'): #authors messy
    jnlname = 'Phys.Today'
    typecode = ''


host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
#    options.binary_location='/usr/bin/google-chrome'
    #options.add_argument('--headless')
#    options.add_argument('--no-sandbox')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.headless=True
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
    
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
    now = datetime.datetime.now()
    filestosearch = '%s/*%s*doki ' % (dokidir, jnl)
    for i in range(3-1):
        filestosearch += '%s/%i/*%s*doki ' % (dokidir, now.year-i-1, jnl)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s | grep pubs.aip.org | sed 's/^I..//' | sed 's/..$//' " % (filestosearch))))
    print('%i records in backup (%s)' % (len(alreadyharvested), jnl))
    if len(alreadyharvested) > 2:
        print('[%s, ..., %s]' % (alreadyharvested[0], alreadyharvested[-1]))


boring = ['ADVANCED MATERIALS AND NANOTECHNOLOGY FOR SUSTAINABLE ENERGY AND ENVIRONMENTAL APPLICATIONS',
          'ADVANCED NUMERICAL SIMULATIONS IN GEOTECHNICAL ENGINEERING',
          'ADVANCED OPERATION AND MAINTENANCE IN SOLAR PLANTS, WIND FARMS AND MICROGRIDS',
          'ADVANCED TECHNOLOGIES IN DIGITIZING CULTURAL HERITAGE', 'ADVANCES IN APPLIED GEOPHYSICS',
          'ADVANCES IN ARTIFICIAL INTELLIGENCE METHODS FOR NATURAL LANGUAGE PROCESSING',
          'ADVANCES IN HIGH-PERFORMANCE FIBER-REINFORCED CONCRETE', 'ADVANCES IN HUMAN-CENTRIC LIGHTING',
          'ADVANCES IN MARINE BIOTECHNOLOGY: EXPLOITATION OF HALOPHYTE PLANTS',
          'ADVANCES IN MULTIMODALITY APPROACH TO ECHOCARDIOGRAPHIC IMAGING: DEFORMATION INDEXES, 3D-EVALUATIONS, AND FUTURE PERSPECTIVES',
          'ADVANCES IN WOOD ENGINEERING AND FORESTRY', 'ADVANCING COMPLEXITY RESEARCH IN EARTH SCIENCES AND GEOGRAPHY',
          'APPLICATIONS OF INSTRUMENTAL METHODS FOR FOOD AND FOOD BY-PRODUCTS ANALYSIS',
          'APPLICATIONS OF MACHINE LEARNING IN AUDIO CLASSIFICATION AND ACOUSTIC SCENE CHARACTERIZATION',
          'APPLICATIONS OF NUCLEIC ACIDS IN CHEMISTRY AND BIOLOGY', 'APPLICATIONS OF VIRTUAL, AUGMENTED, AND MIXED REALITY',
          'ARTICLES BIOLOGICAL MOLECULES AND NETWORKS', 'BIM IMPLEMENTATION TO MEET THE CHANGING DEMANDS OF THE CONSTRUCTION INDUSTRY',
          'BIOACTIVE COMPOUNDS FOR CARDIOVASCULAR AND METABOLIC DISEASES', 'BIOMECHANICS IN SPORT PERFORMANCE AND INJURY PREVENTING',
          'CONDITION MONITORING AND THEIR APPLICATIONS IN INDUSTRY',
          'CURRENT APPROACHES AND APPLICATIONS IN NATURAL LANGUAGE PROCESSING',
          'ETIOLOGY, CLASSIFICATION AND MANAGEMENT OF ENDODONTIC-PERIODONTAL LESIONS',
          'FOCUS ON TRAFFIC SAFETY: FROM ARTIFICIAL INTELLIGENCE APPROACHES TO OTHER ADVANCES',
          'FROM CHILDHOOD TO ADULTHOOD: NEW TRENDS IN MULTIDISCIPLINARY ORTHODONTICS',
          'FRONTIERS IN ATMOSPHERIC PRESSURE PLASMA TECHNOLOGY',
          'IMAGE PROCESSING AND ANALYSIS FOR PRECLINICAL AND CLINICAL APPLICATIONS',
          'IMPROVING DIAGNOSIS AND THERAPY OF LYMPHOPROLIFERATIVE DISEASES: LATEST ADVANCES AND PROSPECTS',
          'INDUSTRIAL MANAGEMENT AND ENGINEERING IN THE FOURTH INDUSTRIAL REVOLUTION',
          'MAGMA MIGRATION AND ERUPTIONS IN A VOLCANIC GROUP: CASE STUDIES FOR THE 2017-2018 ACTIVITY OF THE KIRISHIMA VOLCANO GROUP AND OTHER GLOBAL EXAMPLES',
          'MARITIME TRANSPORTATION SYSTEM AND TRAFFIC ENGINEERING', 'NATURAL LANGUAGE PROCESSING: APPROACHES AND APPLICATIONS',
          'NEW CHALLENGES IN CIVIL STRUCTURE FOR FIRE RESPONSE', 'NEW FRONTIERS IN BUILDINGS AND CONSTRUCTION',
          'NEW TRENDS OF SILVER NANOPARTICLES IN BIOMEDICINE', 'PSYCHOACOUSTICS FOR EXTENDED REALITY (XR)',
          'RECENT ADVANCES IN APPLICATION OF THIN FILMS AND COATINGS',
          'RENEWABLE AND SUSTAINABLE ENERGY SYSTEMS: RECENT DEVELOPMENTS, CHALLENGES, AND FUTURE PERSPECTIVES',
          'ROAD MATERIALS AND SUSTAINABLE PAVEMENT DESIGN', 'SEISMIC ASSESSMENT AND DESIGN OF STRUCTURES',
          'SEISMIC ASSESSMENT AND RETROFIT OF REINFORCED CONCRETE STRUCTURES', 'SMART ROBOTS FOR INDUSTRIAL APPLICATIONS',
          'SMART SERVICE TECHNOLOGY FOR INDUSTRIAL APPLICATIONS', 'SOFT COMPUTING APPLICATION TO ENGINEERING DESIGN',
          'STATE-OF-THE-ART IN HUMAN FACTORS AND INTERACTION DESIGN', 'STRUCTURAL AND THERMO-MECHANICAL ANALYSES IN NUCLEAR FUSION REACTORS',
          'TECHNOLOGY AND MANAGEMENT APPLIED IN CONSTRUCTION ENGINEERING PROJECTS', 'UNMANNED AERIAL VEHICLES',
          'URBAN SUSTAINABILITY AND RESILIENCE OF THE BUILT ENVIRONMENTS', 'URBAN TRANSPORT SYSTEMS EFFICIENCY, NETWORK PLANNING AND SAFETY',
          'ACOUSTICS AND VIBRATIONS ANALYSES OF MATERIALS AT DIFFERENT SCALES: EXPERIMENTAL AND NUMERICAL APPROACHES',
          'ADAPTIVE OPTICAL AND COMPUTATIONAL IMAGING TOWARDS BIOMEDICAL APPLICATION', 'ADVANCED MEASURES FOR EARTHQUAKE AND TSUNAMI DISASTER MITIGATION',
          'ADVANCED TECHNOLOGIES FOR ASSESSMENT AND THERAPY IN REHABILITATION MEDICINE', 'ADVANCES IN MICROALGAL BIOMASS PRODUCTIONS',
          'ADVANCES OF ENERGY EFFICIENCY IN ELECTRICAL ENGINEERING AND ELECTRONICS', 'ADVANCES ON APPLICATIONS OF BIOACTIVE NATURAL COMPOUNDS',
          'ASSESSMENT AND REHABILITATION OF EXISTING REINFORCED CONCRETE STRUCTURES AND INFRASTRUCTURES: METHODS, TECHNIQUES AND NEW FRONTIERS',
          'BIOMECHANICAL AND BIOMEDICAL FACTORS OF KNEE OSTEOARTHRITIS', 'CLINICAL APPLICATIONS FOR DENTISTRY AND ORAL HEALTH',
          'DEEP ROCK MASS ENGINEERING: EXCAVATION, MONITORING, AND CONTROL', 'DENTAL MATERIALS: LATEST ADVANCES AND PROSPECTS',
          'FRONTIER RESEARCH IN APICULTURE (DIAGNOSIS AND CONTROL OF BEE DISEASES, BEE PRODUCTS, ENVIRONMENTAL MONITORING)',
          'GEOHAZARDS: RISK ASSESSMENT, MITIGATION AND PREVENTION', 'GEOINFORMATICS AND DATA MINING IN EARTH SCIENCES',
          'IMAGING TECHNIQUES AND APPLICATIONS IN INTERNAL MEDICINE AND RHEUMATOLOGY', 'IMAGING TECHNIQUES FOR ORAL AND DENTAL APPLICATIONS',
          'INTEGRATED GEOPHYSICAL METHODS FOR SHALLOW AQUIFERS CHARACTERIZATION AND MODELLING', 'MATERIALS AND TECHNOLOGIES IN ORAL RESEARCH',
          'NATURAL-HAZARDS RISK ASSESSMENT FOR DISASTER MITIGATION', 'NEW VISTAS IN RADIOTHERAPY',
          'NONLINEAR ANALYSIS OF STATIC AND DYNAMIC PROBLEMS IN MECHANICAL ENGINEERING', 'PHOTOVOLTAICS AND ENERGY',
          'RECENT PROGRESS ON ADVANCED FOUNDATION ENGINEERING', 'REINFORCED CONCRETE: MATERIALS, PHYSICAL PROPERTIES AND APPLICATIONS',
          'SCIENTIFIC METHODS FOR CULTURAL HERITAGE', 'STENTS AND INTERVENTIONAL DEVICES: BIOENGINEERING AND BIOMEDICAL APPLICATIONS',
          'TECHNOLOGICAL ADVANCES IN SEISMIC DATA PROCESSING AND IMAGING', 'ULTRASONIC MODELLING FOR NON-DESTRUCTIVE TESTING',
          'APPLICATIONS OF ARTIFICIAL INTELLIGENCE IN MEDICINE PRACTICE',
          'CURRENTS CONCEPTS AND CHALLENGES IN ORAL HEALTH: IMPLICATIONS FOR THE GLOBAL POPULATION',
          'PAPER IN HISTORICAL AND SOCIAL STUDIES OF SCIENCE', 'PAPER IN THE PHILOSOPHY OF THE BIOMEDICAL SCIENCES',
          'TUNNELING AND UNDERGROUND ENGINEERING: FROM THEORIES TO PRACTICES', 'ADVANCED RAILWAY INFRASTRUCTURES ENGINEERING',
          'ADVANCING RELIABILITY & PROGNOSTICS AND HEALTH MANAGEMENT',
          'APPLICATIONS OF MACHINE LEARNING TO IMAGE, VIDEO, TEXT AND BIOINFORMATIC ANALYSIS',
          'ELECTRONIC AND OPTOELECTRONIC MATERIALS, DEVICES AND PROCESSING', 'FUTURE TRANSPORTATION OF PEOPLE AND GOODS',
          'PAPER IN THE PHILOSOPHY OF THE SCIENCES OF MIND AND BRAIN', 'HUMAN-COMPUTER INTERACTIONS',
          'MECHATRONICS AND ROBOTICS IN VEHICLE AND MEDICAL APPLICATIONS',
          'REMOTE SENSING APPLICATIONS AND AGRICULTURAL AUTOMATION', 'BIOPHYSICS, BIOMATERIALS, AND BIOELECTRONICS',
          'EFFECTS OF SURFACE GEOLOGY ON SEISMIC MOTION (ESG): GENERAL STATE-OF-RESEARCH',
          'REACTIVITY IN THE HUMAN SCIENCES', 'ORGANIC-INORGANIC SYSTEMS, INCLUDING ORGANIC ELECTRONICS',
          'PAPER IN THE PHILOSOPHY OF THE SOCIAL SCIENCES AND HUMANITIES', 'CHEMICAL PHYSICS SOFTWARE',
          'BIOFLUID MECHANICS', 'GEOPHYSICAL FLOWS', 'BIOPHYSICS, BIOMATERIALS, LIQUIDS, AND SOFT MATTER',
          'EQUIPMENT AND TECHNIQUES FOR CHEMISTRY; BIOLOGY; MEDICINE',
          'EQUIPMENT AND TECHNIQUES FOR MICROSCOPY; IMAGING METHODS; POSITIONING SYSTEMS, NANOPARTICLES',
          'PAPER IN THE PHILOSOPHY OF THE LIFE SCIENCES', 'TEACHING PHILOSOPHY OF SCIENCE TO STUDENTS FROM OTHER DISCIPLINES',
          'BOOK REVIEWS', 'PAPER IN HISTORY AND PHILOSOPHY OF SCIENCE', 'INSTRUCTIONAL LABORATORIES AND DEMONSTRATIONS', 'EDITORIAL',
          'PERSPECTIVE', 'PAPER IN PHILOSOPHY OF THE NATURAL SCIENCES', 'PAPER IN PHILOSOPHY OF SCIENCE IN PRACTICE', 'EDITORIAL',
          'COMMENTS', 'BIOLOGICAL MOLECULES AND NETWORKS', 'PHONONIC, ACOUSTIC, AND THERMAL PROPERTIES',
          'BIOPHYSICS, BIOIMAGING, AND BIOSENSORS', 'POLYMERS AND SOFT MATTER']
boring += ['FROM THE EDITOR', "READERS' FORUM", 'ISSUES AND EVENTS', 'BOOKS',
           'NEW PRODUCTS', 'OBITUARIES', 'QUICK STUDY', 'BACK MATTER',
           'BACK OF THE ENVELOPE', 'BOOK REVIEWS', 'READERS’ FORUM',
           'ANNOUNCEMENTS', 'EDITORIALS', 'EDITORIAL', 'TUTORIAL', 'PERSPECTIVES']

urltrunk = 'http://aip.scitation.org/toc/%s/%s/%s?size=all' % (jnl,vol,iss)
if jnl in ['aqs']:
    urltrunk = 'https://avs.scitation.org/toc/%s/%s/%s?size=all' % (jnl,vol,iss)
print(urltrunk)

driver.get(urltrunk)
tocpage = BeautifulSoup(driver.page_source, features="lxml")

def getarticle(artlink, secs, p1):
    try:
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        artpage.body.find_all('div')
    except:
        try:
            print(' --- SLEEP ---')
            time.sleep(300)
            driver.get(artlink)
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            artpage.body.find_all('div')
        except:
            print(' --- SLEEEEEP ---')
            time.sleep(600)
            driver.get(artlink)
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            artpage.body.find_all('div')            
    rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : iss, 'tc' : typecode, 'keyw' : [],
           'note' : [artlink], 'p1' : p1}
    emails = {}
    if cnum:
        rec['cnum'] = cnum
    for sec in secs:
        rec['note'].append(sec)
        secu = sec.upper()
        if secu in ['CONTRIBUTED REVIEW ARTICLES', 'REVIEW ARTICLES']:
            rec['tc'] = 'R'
        if secu in ['CLASSICAL AND QUANTUM GRAVITY', 'GENERAL RELATIVITY AND GRAVITATION']:
            rec['fc'] = 'g'
        elif secu in ['ACCELERATOR', 'COMPACT PARTICLE ACCELERATORS TECHNOLOGY', 'LATEST TRENDS IN FREE ELECTRON LASERS', 'PLASMA-BASED ACCELERATORS, BEAMS, RADIATION GENERATION']:
            rec['fc'] = 'b'
        elif secu in ['CRYPTOGRAPHY AND ITS APPLICATIONS IN INFORMATION SECURITY']:
            rec['fc'] = 'c'
        elif secu in ['MACROSCOPIC AND HYBRID QUANTUM SYSTEMS', 'QUANTUM MEASUREMENT TECHNOLOGY', 'QUANTUM PHOTONICS', 'QUANTUM COMPUTERS AND SOFTWARE', 'QUANTUM SENSING AND METROLOGY', 'QUANTUM INFORMATION AND COMPUTATION', 'QUANTUM MECHANICS - GENERAL AND NONRELATIVISTIC', 'QUANTUM PHYSICS AND TECHNOLOGY', 'QUANTUM TECHNOLOGIES']:
            rec['fc'] = 'k'
        elif secu in ['IMPEDANCE SPECTROSCOPY AND ITS APPLICATION IN MEASUREMENT AND SENSOR TECHNOLOGY', 'SENSORS; ACTUATORS; POSITIONING DEVICES; MEMS/NEMS; ENERGY HARVESTING']:
            rec['fc'] = 'i'
        elif secu in ['REPRESENTATION THEORY AND ALGEBRAIC METHODS', 'METHODS OF MATHEMATICAL PHYSICS', 'PARTIAL DIFFERENTIAL EQUATIONS']:
            rec['fc'] = 'm'
        elif secu in ['HELIOSPHERIC AND ASTROPHYSICAL PLASMAS']:
            rec['fc'] = 'a'
        elif secu in ['MANY-BODY AND CONDENSED MATTER PHYSICS']:
            rec['fc'] = 'f'
        elif secu in ['STATISTICAL PHYSICS']:
            rec['fc'] = 's'            
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_institution',
                                        'citation_doi', 'citation_publication_date',
                                        'description', 'citation_title'])
    #abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'abstract'}):
        rec['abs'] = section.text.strip()
    #ORCIDs
    orcids = {}
    for div in artpage.body.find_all('div', attrs = {'class' : 'al-author-name'}):
        for a in div.find_all('a', attrs = {'class' : 'linked-name'}):
            name = re.sub(' \(.*', '', a.text.strip())
            for span in div.find_all('span', attrs = {'class' : 'al-orcid-id'}):
                orcid = 'ORCID:' + span.text.strip()
                if name in orcids:
                    orcids[name] = False
                else:
                    orcids[name] = orcid
                    #print('         ', name, orcid)
    #combine ORCID with affiliations
    newautaff = []
    for aa in rec['autaff']:
        name = re.sub('(.*), (.*)', r'\2 \1', aa[0])
        if name in orcids:            
            newautaff.append([aa[0], orcids[name]] + aa[1:])
            #print('   %s -> orcid.org/%s' % (name, orcids[name]))
        else:
            newautaff.append(aa)
    rec['autaff'] = newautaff
                    
        
    
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'ref-list'}):
        rec['refs'] = []
        for a in div.find_all('a'):
            if a.text in ['Google Scholar', 'Crossref', 'Search ADS']:
                a.decompose()
        for div2 in div.find_all('div', attrs = {'class' : 'ref-content'}):
            rec['refs'].append([('x', div2.text.strip())])
    
    ejlmod3.printrecsummary(rec)
    time.sleep(random.randint(30,90))
    return rec
                
sections = {}
tocheck = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'section-container'}):
    for child in div.contents:
        if child.name in ['h4', 'h3', 'h5', 'h6', 'h2']: 
            sections[child.name] = child.text.strip()
            lev = int(child.name[1])-2
            print(lev*'#', sections[child.name])
        elif child.name in ['section', 'div']:
            for child2 in child.contents:
                if type(child2) == type(child):
                    #print('~', child2.name)
                    if child2.name in ['h3', 'h4', 'h5', 'h6']:
                        sections[child2.name] = child2.text.strip()
                        lev = int(child2.name[1])-2
                        print(lev*'*', sections[child2.name])
                    elif child2.name in ['section', 'div']:
                        for h in child2.find_all('h5'):
                            if h.has_attr('data-level'):
                                sections[h.name] = h.text.strip()
                                lev = int(h.name[1])-2
                                print(lev*'@', sections[h.name])
                        for a in child2.find_all('a', attrs = {'class' : 'viewArticleLink'}):
                            href = 'https://pubs.aip.org' + a['href']
                            #articleID is not on indiviual article page (sic!)
                            p1 = re.sub('.*\/(\d\d+)\/.*', r'\1', href)
                            if not skipalreadyharvested or not href in alreadyharvested:
                                secs = list(sections.values())                               
                                keepit = True
                                for sec in secs:
                                    if sec.upper() in boring:
                                        keepit = False
                                if keepit:
                                    tocheck.append((href, p1, secs))
                                    print(' + ', href)
                                else:
                                    print(' - ', href)
                            else:
                                print('   ', href)

time.sleep(10)                                
random.shuffle(tocheck)
recs = []
i = 0
for (href, p1, secs) in tocheck:
    i += 1
    if href in ['/doi/full/10.1063/1.5019809']:
        print('skip %s' % (href))
    else:
        ejlmod3.printprogress('-', [[i, len(tocheck)], secs, [href, p1]])
        rec = getarticle(href, secs, p1)
        if rec['autaff']:
            recs.append(rec)
            ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
print('%i records for %s' % (len(recs), jnlfilename))
#if not recs:
#    print(tocpage.text)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
driver.quit()












