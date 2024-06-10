# -*- coding-8 -*-
#program to harvest individual DOIs IEEE-journals
# FS 2023-12-10

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

skipalreadyharvested = False
bunchsize = 10
publisher = 'IEEE'
corethreshold = 15

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
urltrunc = "https://ieeexplore.ieee.org"


jnlfilename = 'IEEE_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


sample = {'10.1109/SFCS.1994.365701' : {'all' : 23 , 'core' : 23},
          '10.1109/sfcs.1994.365700' : {'all' : 275 , 'core' : 275},
          '10.1109/SFCS.1994.365700' : {'all' : 275 , 'core' : 275},
          '10.1109/SFCS.1996.548464' : {'all' : 58 , 'core' : 58},
          '10.1109/SFCS.2000.892140' : {'all' : 16 , 'core' : 16},
          '10.1109/SFCS.1998.743501' : {'all' : 33 , 'core' : 33},
          '10.1109/FOCS.2018.00038' : {'all' : 13 , 'core' : 13},
          '10.1109/FOCS.2018.00039' : {'all' : 11 , 'core' : 11},
          '10.1109/LICS.2005.1' : {'all' : 12 , 'core' : 12},
          '10.1109/CCC.2009.42' : {'all' : 16 , 'core' : 16},
          '10.1109/CVPR.2015.7298594' : {'all' : 29 , 'core' : 29},
          '10.1109/ICCV.2015.123' : {'all' : 34 , 'core' : 34},
          '10.1109/LICS.2015.59' : {'all' : 24 , 'core' : 24},
          '10.1109/FOCS.2004.53' : {'all' : 34 , 'core' : 34},
          '10.1109/NSSMIC.2007.4437209' : {'all' : 38 , 'core' : 38},
          '10.1109/FOCS.2018.00033' : {'all' : 33 , 'core' : 33},
          '10.1109/ICNN.1995.488968' : {'all' : 57 , 'core' : 57},
          '10.1109/FOCS.2015.54' : {'all' : 46 , 'core' : 46},
          '10.1109/FOCS.2009.36' : {'all' : 45 , 'core' : 45},
          '10.1109/MICRO50266.2020.00029' : {'all' : 8 , 'core' : 8},
          '10.1109/FOCS.2019.00066' : {'all' : 10 , 'core' : 10},
          '10.1109/TIT.2012.2220519' : {'all' : 16 , 'core' : 16},
          '10.1109/5.726791' : {'all' : 187 , 'core' : 187},
          '10.1109/18.720553' : {'all' : 19 , 'core' : 19},
          '10.1109/TASC.2010.2097578' : {'all' : 20 , 'core' : 20},
          '10.1109/TCSI.2018.2853655' : {'all' : 18 , 'core' : 18},
          '10.1109/TIT.2002.806153' : {'all' : 19 , 'core' : 19},
          '10.1109/TIT.2003.822618' : {'all' : 11 , 'core' : 11},
          '10.1109/TIT.2010.2054174' : {'all' : 16 , 'core' : 16},
          '10.1109/TIT.2019.2929564' : {'all' : 21 , 'core' : 21},
          '10.1002/j.1538-7305.1948.tb01338.x' : {'all' : 259 , 'core' : 259},
          '10.1109/COMST.2018.2864557' : {'all' : 18 , 'core' : 18},
          '10.1109/TIT.2009.2039166' : {'all' : 21 , 'core' : 21},
          '10.1109/TIT.2013.2292052' : {'all' : 13 , 'core' : 13},
          '10.1002/j.1538-7305.1965.tb01684.x' : {'all' : 33 , 'core' : 33},
          '10.1109/18.256484' : {'all' : 15 , 'core' : 15},
          '10.1109/18.904522' : {'all' : 16 , 'core' : 16},
          '10.1109/JSAC.2020.2969035' : {'all' : 16 , 'core' : 16},
          '10.1109/TC.2018.2882774' : {'all' : 16 , 'core' : 16},
          '10.1109/TIT.2014.2308180' : {'all' : 16 , 'core' : 16},
          '10.1109/TKDE.2009.191' : {'all' : 27 , 'core' : 27},
          '10.1109/TPAMI.1984.4767596' : {'all' : 35 , 'core' : 35},
          '10.1109/4235.585893' : {'all' : 19 , 'core' : 19},
          '10.1109/JPROC.2019.2954005' : {'all' : 17 , 'core' : 17},
          '10.1109/TIT.2002.807289' : {'all' : 19 , 'core' : 19},
          '10.1109/TIT.2019.2907989' : {'all' : 31 , 'core' : 31},
          '10.1109/TMAG.2004.836740' : {'all' : 53 , 'core' : 53},
          '10.1109/TNNLS.2020.3009716' : {'all' : 17 , 'core' : 17},
          '10.1002/j.1538-7305.1948.tb00917.x' : {'all' : 43 , 'core' : 43},
          '10.1109/18.771249' : {'all' : 16 , 'core' : 16},
          '10.1109/TCOMM.2020.2978071' : {'all' : 30 , 'core' : 30},
          '10.1109/TIT.2009.2021379' : {'all' : 19 , 'core' : 19},
          '10.1109/TIT.2017.2711601' : {'all' : 15 , 'core' : 15},
          '10.1109/COMST.2022.3144219' : {'all' : 17 , 'core' : 17},
          '10.1109/JPROC.2015.2494218' : {'all' : 32 , 'core' : 32},
          '10.1109/TC.2015.2409842' : {'all' : 17 , 'core' : 17},
          '10.1109/TCAD.2007.911334' : {'all' : 18 , 'core' : 18},
          '10.1109/4235.996017' : {'all' : 77 , 'core' : 77},
          '10.1109/77.80745' : {'all' : 27 , 'core' : 27},
          '10.1109/JSTQE.2003.820918' : {'all' : 20 , 'core' : 20},
          '10.1109/MSP.2012.2211477' : {'all' : 19 , 'core' : 19},
          '10.1109/TPAMI.2013.50' : {'all' : 36 , 'core' : 36},
          '10.1109/LED.2020.2991351' : {'all' : 23 , 'core' : 23},
          '10.1109/TITS.2019.2891235' : {'all' : 18 , 'core' : 18},
          '10.1109/TNNLS.2020.2978386' : {'all' : 20 , 'core' : 20},
          '10.1109/18.476316' : {'all' : 31 , 'core' : 31},
          '10.1109/PROC.1978.10837' : {'all' : 56 , 'core' : 56},
          '10.1109/TASC.2016.2629670' : {'all' : 24 , 'core' : 24},
          '10.1109/TIT.1975.1055351' : {'all' : 39 , 'core' : 39},
          '10.1109/TSMCB.2008.925743' : {'all' : 24 , 'core' : 24},
          '10.1109/18.782103' : {'all' : 27 , 'core' : 27},
          '10.1109/7.705889' : {'all' : 26 , 'core' : 26},
          '10.1109/TIT.1962.1057683' : {'all' : 24 , 'core' : 24},
          '10.1109/TIT.1973.1055103' : {'all' : 35 , 'core' : 35},
          '10.1109/TIT.2006.890730' : {'all' : 26 , 'core' : 26},
          '10.1109/TNS.2015.2492778' : {'all' : 24 , 'core' : 24},
          '10.1109/TC.2020.3038063' : {'all' : 22 , 'core' : 22},
          '10.1109/TIT.2011.2158473' : {'all' : 38 , 'core' : 38},
          '10.1109/TAC.1974.1100705' : {'all' : 474 , 'core' : 474},
          '10.1109/99.660313' : {'all' : 35 , 'core' : 35},
          '10.1109/TIT.2021.3097347' : {'all' : 23 , 'core' : 23},
          '10.1109/MC.2016.291' : {'all' : 26 , 'core' : 26},
          '10.1109/MCSE.2010.118' : {'all' : 84 , 'core' : 84},
          '10.1109/TIT.2002.802612' : {'all' : 36 , 'core' : 36},
          '10.1109/COMST.2017.2786748' : {'all' : 35 , 'core' : 35},
          '10.1109/TIT.2009.2018325' : {'all' : 56 , 'core' : 56},
          '10.1109/JSTSP.2016.2574703' : {'all' : 31 , 'core' : 31},
          '10.1109/JLT.2018.2843136' : {'all' : 34 , 'core' : 34},
          '10.1109/JRPROC.1949.232969' : {'all' : 53 , 'core' : 53},
          '10.1109/TIT.1982.1056489' : {'all' : 56 , 'core' : 56},
          '10.1109/23.34577' : {'all' : 37 , 'core' : 37},
          '10.1109/TIT.2013.2292061' : {'all' : 33 , 'core' : 33},
          '10.1109/TNS.2004.839134' : {'all' : 48 , 'core' : 48},
          '10.1109/TASC.2014.2318294' : {'all' : 40 , 'core' : 40},
          '10.1109/TCAD.2018.2846658' : {'all' : 37 , 'core' : 37},
          '10.1109/JRPROC.1958.286741' : {'all' : 174 , 'core' : 174},
          '10.1109/TIT.2017.2719044' : {'all' : 51 , 'core' : 51},
          '10.1109/TIT.2018.2873764' : {'all' : 44 , 'core' : 44},
          '10.1002/j.1538-7305.1949.tb00928.x' : {'all' : 55 , 'core' : 55},
          '10.1109/18.959288' : {'all' : 46 , 'core' : 46},
          '10.1109/TIT.2004.839515' : {'all' : 48 , 'core' : 48},
          '10.1109/18.985948' : {'all' : 64 , 'core' : 64},
          '10.1109/TIT.1976.1055638' : {'all' : 47 , 'core' : 47},
          '10.1109/TIT.2009.2025545' : {'all' : 67 , 'core' : 67},
          '10.1109/JSTQE.2015.2392076' : {'all' : 47 , 'core' : 47},
          '10.1109/MNET.001.1900092' : {'all' : 59 , 'core' : 59},
          '10.1109/TIT.2006.883612' : {'all' : 52 , 'core' : 52},
          '10.1109/9.119632' : {'all' : 49 , 'core' : 49},
          '10.1109/TAU.1967.1161901' : {'all' : 75 , 'core' : 75},
          '10.1109/18.761271' : {'all' : 86 , 'core' : 86},
          '10.1109/TCAD.2014.2341953' : {'all' : 54 , 'core' : 54},
          '10.1109/tpami.2020.2992934' : {'all' : 63 , 'core' : 63},
          '10.1109/TPAMI.2020.2992934' : {'all' : 63 , 'core' : 63},
          '10.1109/JPROC.2009.2021005' : {'all' : 158 , 'core' : 158},
          '10.1109/TCAD.2013.2244643' : {'all' : 64 , 'core' : 64},
          '10.1109/18.681315' : {'all' : 98 , 'core' : 98},
          '10.1109/tcad.2005.855930' : {'all' : 98 , 'core' : 98},
          '10.1109/TCAD.2005.855930' : {'all' : 98 , 'core' : 98},
          '10.1109/18.748992' : {'all' : 9 , 'core' : 9},
          '10.1109/Access.6287639' : {'all' : 10 , 'core' : 10},
          '10.1109/LPT.2018.2810334' : {'all' : 10 , 'core' : 10}}
sample = {'10.1109/TIT.2009.2032797' : {'all' : 49, 'core' : 27},
          '10.1109/18.796385' : {'all' : 42, 'core' : 23},
          '10.1109/TIT.1968.1054108' : {'all' : 38, 'core' : 13},
          '10.1109/MMM.2020.2993476' : {'all' : 37, 'core' : 19},
          '10.1109/COMST.2022.3144219' : {'all' : 34, 'core' : 30},
          '10.1109/TIT.1979.1055985' : {'all' : 34, 'core' : 14},
          '10.1109/TIT.2002.807289' : {'all' : 33, 'core' : 27},
          '10.1109/JSTQE.2016.2573218' : {'all' : 33, 'core' : 21},
          '10.1109/TIT.2011.2161917' : {'all' : 31, 'core' : 26},
          '10.1109/18.959270' : {'all' : 30, 'core' : 15},
          '10.1109/MSP.2012.2211477' : {'all' : 29, 'core' : 26},
          '10.1109/TCAD.2007.911334' : {'all' : 29, 'core' : 25},
          '10.1109/TIT.2016.2555700' : {'all' : 29, 'core' : 19},
          '10.1109/18.256484' : {'all' : 28, 'core' : 26},
          '10.1109/TIT.1978.1055892' : {'all' : 28, 'core' : 23},
          '10.1109/4235.585893' : {'all' : 27, 'core' : 20},
          '10.1109/TIT.2008.917696' : {'all' : 27, 'core' : 16},
          '10.1109/TC.2020.3038063' : {'all' : 26, 'core' : 25},
          '10.1109/FOCS.2017.45' : {'all' : 26, 'core' : 20},
          '10.1109/TIT.2009.2021379' : {'all' : 26, 'core' : 19},
          '10.1109/TIT.2002.806153' : {'all' : 26, 'core' : 15},
          '10.1109/TC.2015.2409842' : {'all' : 25, 'core' : 23},
          '10.1109/TIT.2010.2048442' : {'all' : 25, 'core' : 19},
          '10.1109/TCSI.2018.2853655' : {'all' : 25, 'core' : 17},
          '10.1109/TIT.2014.2308180' : {'all' : 24, 'core' : 20},
          '10.1109/TIT.2003.822618' : {'all' : 23, 'core' : 23},
          '10.1109/18.771249' : {'all' : 23, 'core' : 21},
          '10.1109/LICS.2019.8785765' : {'all' : 23, 'core' : 20},
          '10.1109/TIT.2013.2238656' : {'all' : 23, 'core' : 18},
          '10.1109/TEVC.2002.804320' : {'all' : 23, 'core' : 17},
          '10.1109/COMST.2018.2864557' : {'all' : 23, 'core' : 17},
          '10.1109/18.904522' : {'all' : 22, 'core' : 16},
          '10.1109/TIT.2011.2177772' : {'all' : 22, 'core' : 14},
          '10.1109/TCOMM.2020.3006201' : {'all' : 22, 'core' : 14},
          '10.1109/TITS.2019.2891235' : {'all' : 21, 'core' : 20},
          '10.1109/SFCS.2000.892140' : {'all' : 21, 'core' : 20},
          '10.1109/MSP.2018.3761723' : {'all' : 21, 'core' : 18},
          '10.1109/JSAC.2020.2969035' : {'all' : 21, 'core' : 18},
          '10.1109/CCC.2007.26' : {'all' : 21, 'core' : 17},
          '10.1109/SFCS.1982.38' : {'all' : 21, 'core' : 15},
          '10.1109/TIT.2012.2220519' : {'all' : 21, 'core' : 14},
          '10.1109/TIT.2015.2388576' : {'all' : 20, 'core' : 16},
          '10.1109/TIT.2010.2054174' : {'all' : 20, 'core' : 13},
          '10.1109/TIT.2017.2711601' : {'all' : 19, 'core' : 19},
          '10.1109/TIT.2008.2009798' : {'all' : 19, 'core' : 18},
          '10.1109/CCC.2009.42' : {'all' : 19, 'core' : 18},
          '10.1109/FOCS.2018.00038' : {'all' : 19, 'core' : 16},
          '10.1109/TCAD.2003.811448' : {'all' : 18, 'core' : 16},
          '10.1109/TNNLS.2020.3009716' : {'all' : 18, 'core' : 15},
          '10.1109/TC.2018.2882774' : {'all' : 18, 'core' : 15},
          '10.1109/TIT.2013.2292052' : {'all' : 17, 'core' : 16},
          '10.1109/MCOM.2019.1800763' : {'all' : 17, 'core' : 16},
          '10.1109/TKDE.2019.2937491' : {'all' : 17, 'core' : 15},
          '10.1109/TIT.2015.2422294' : {'all' : 17, 'core' : 14},
          '10.1109/TIT.2018.2825602' : {'all' : 16, 'core' : 16},
          '10.1109/FOCS.2018.00039' : {'all' : 16, 'core' : 15},
          '10.1109/MC.2020.2984871' : {'all' : 16, 'core' : 14},
          '10.1109/TASC.2008.2012255' : {'all' : 16, 'core' : 13},
          '10.1109/LICS.2005.1' : {'all' : 15, 'core' : 15}}
         
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
    elif ieeename in ['The Bell System Technical Journal']:
        jnlname = 'Bell Syst.Tech.J.'
    elif ieeename in ['IEEE Transactions on Knowledge and Data Engineering']:
        jnlname = 'IEEE Trans.Knowledge Data Eng.'
    elif ieeename in ['IEEE Transactions on Pattern Analysis and Machine Intelligence']:
        jnlname = 'IEEE Trans.Pattern Anal.Machine Intell.'
    elif ieeename in ['IEEE Transactions on Communications']:
        jnlname = 'IEEE Trans.Commun.'
    elif ieeename in ['IEEE Transactions on Evolutionary Computation']:
        jnlname = 'IEEE Trans.Evol.Comput.'
    elif ieeename in ['IEEE Transactions on Neural Networks and Learning Systems']:
        jnlname = 'IEEE Trans.Neural Networks Learning Syst.'
    elif ieeename in ['IEEE Transactions on Systems, Man, and Cybernetics, Part B (Cybernetics)']:
        jnlname = 'IEEE Trans.Syst.Sci.Cybern.'
    elif ieeename in ['IEEE Transactions on Aerospace and Electronic Systems']:
        jnlname = 'IEEE Trans.Aerosp.Electron.Syst.'
    elif ieeename in ['IRE Transactions on Information Theory']:
        jnlname = 'IRE Trans.Inf.Theor.'
    elif ieeename in ['IEEE Computational Science and Engineering']:
        jnlname = 'IEEE Comput.Sci.Eng.'
    elif ieeename in ['Computer']:
        jnlname = 'Computer'
    elif ieeename in ['IEEE Communications Surveys & Tutorials']:
        jnlname = 'IEEE Commun.Surveys Tutorials'
    elif ieeename in ['IEEE Journal of Selected Topics in Signal Processing']:
        jnlname = 'IEEE J.Sel.Top.Sig.Proc.'
    elif ieeename in ['IEEE Network']:
        jnlname = 'IEEE Network'
    elif ieeename in ['IEEE Transactions on Audio and Electroacoustics']:
        jnlname = 'IEEE Trans.Audio Electroacoust.'
#    elif ieeename in ['']:
#        jnlname = ''
    elif ieeename in ["IEEE Symposium Conference Record Nuclear Science 2004.",
                      "IEEE Nuclear Science Symposium Conference Record, 2005",
                      'Proceedings 35th Annual Symposium on Foundations of Computer Science']:
        jnlname = 'BOOK'
        tc = 'C'
    elif re.search('(Proceeding|Conference|Symposium)', ieeename):
        jnlname = 'BOOK'
        tc = 'C'        
    else:
        print('unknown journal', ieeename)
        return False
    return jnlname

tc = 'P'
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

    
                
i = 0
recs = []
missingjournals = []
iref = 0
manager = Manager()
refsdict = manager.dict()
for doi in sample:
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    print(missingjournals)
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested:
        if doi in alreadyharvested or doi.lower() in alreadyharvested or doi.upper() in alreadyharvested:
            print('   already in backup')
            continue
    articlelink = 'https://doi.org/' + doi
    artfilename = '%s/ieee_%s.%s' % (tmpdir, 'QIS', re.sub('https', 'http', re.sub('\W', '', articlelink)))
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
    rec = {'keyw' : [], 'autaff' : [], 'note' : [articlelink], 'doi' : doi}
    #metadata now in javascript
    for script in articlepage.find_all('script', attrs = {'type' : 'text/javascript'}):
        #if re.search('global.document.metadata', script.text):
        if script.contents and len(script.contents):
            if re.search('[gG]lobal.document.metadata', script.contents[0]):
                gdm = re.sub('[\n\t]', '', script.contents[0]).strip()
                gdm = re.sub('.*[gG]lobal.document.metadata=(\{.*\}).*', r'\1', gdm)
                gdm = json.loads(gdm)
    hasreferencesection = False
    if 'sections' in gdm:
        if 'references' in gdm['sections']:
            if gdm['sections']['references'] in ['true', 'True']:
                hasreferencesection = True
    if 'publicationTitle' in gdm:
        jnlname = translatejnlname(gdm['publicationTitle'])
        if jnlname == 'IEEE Instrum.Measur.Mag.':
            tc = 'I'
        elif jnlname == 'BOOK':
            tc = 'C'
        elif not jnlname:
            missingjournals.append(gdm['publicationTitle'])
            continue
        rec['jnl'] = jnlname
    if 'authors' in gdm:
        for author in gdm['authors']:
            autaff = [author['name']]
            if 'affiliation' in author:
                autaff += author['affiliation']
            if 'orcid' in author:
                autaff.append('ORCID:'+author['orcid'])
            rec['autaff'].append(autaff)
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
            print('%3i/%3i %s (%s) %s, %s' % (i,len(sample),rec['conftitle'],rec['year'],rec['doi'],'')) #rec['tit'])
        except: 
            print('%3i/%3i %s' % (i,len(sample),rec['tit']))
    else:
        try:
            print('%3i/%3i %s %s (%s) %s, %s' % (i,len(sample),jnlname,rec['vol'],rec['year'],rec['p1'],'')) #rec['tit'])
        except:
            print(rec)
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
    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
