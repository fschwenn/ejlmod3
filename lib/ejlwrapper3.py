# this program (called regularly each month) calls dedicated
# programs to harvest journals by scaning homepages
#
# FS: 2022-06-13
#

import datetime
import os
import re
import sys
import subprocess
import time

protocol = "/afs/desy.de/group/library/publisherdata/log/protocol"
#get previous month
if len(sys.argv) == 4:
    today = datetime.date(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
else:
    today = datetime.datetime.now()
if today.month == 1:
    prmonth = 12
    pryear = today.year - 1
else:
    prmonth = today.month - 1
    pryear = today.year
prquarter = prmonth // 3
prsixth = prmonth // 2
prthird = prmonth // 4
mnrasbignumber = 36*pryear + 3*prmonth - 70759
#get next to previous
if prmonth == 1:
    prprmonth = 12
    prpryear = pryear - 1
else:
    prprmonth = prmonth - 1
    prpryear = pryear
if prquarter == 1:
    prprquarter = 4
    prpryear = pryear - 1
else:
    prprquarter = prquarter - 1
    prpryear = pryear

now = datetime.datetime.now()
stampoftoday = '%4d-%02d-%02d' % (now.year, now.month, now.day)

#put all output of harvesters into:
logfile = '/afs/desy.de/group/library/publisherdata/log/ejlwrapper3.log.%i.%02d.%02d' % (pryear, prmonth, today.day)
#path of harvesters
lproc = {'python2' : '/afs/desy.de/user/l/library/proc',
         'python3' : '/afs/desy.de/user/l/library/proc/python3'}
#pyhton version from virt env
python = {'python3' : '/home/library/.virtualenvs/inspire3-python3.8/bin/python',
          'python2' : '/home/library/.virtualenvs/inspire/bin/python'}

#list of harvesters
#entries: (after how many months it should run next time, [program, argument1, argument2])
jnls = [(1, ['aip3.py', 'rsi', pryear-1929, prmonth]),
        (6, ['theses-bogota3.py']),
        (1, ['aip3.py', 'jmp', pryear-1959, prmonth]),
        (3, ['theses-bristol3.py']),
        (3, ['aip3.py', 'chaos', pryear-1990, prquarter]),
        (2, ['theses-goettingen3.py']),
        (1, ['aip3.py', 'ltp', pryear-1974, prmonth]),
        (2, ['theses-helda3.py']),
        (1, ['aip3.py', 'php', pryear-1993, prmonth]),
        (2, ['theses-leedssheffieldyork3.py']),
        (1, ['aip3.py', 'adva', pryear-2010, prmonth]),
        (3, ['theses-oslo3.py']),
        (1, ['aip3.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + (4*prmonth - 3) % 24]),
        (1, ['osa3.py', 'ol', pryear-1975, prmonth * 2 - 1]),
        (1, ['aip3.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + (4*prmonth - 2) % 24]),
        (1, ['osa3.py', 'ol', pryear-1975, prmonth * 2]),
        (1, ['aip3.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + (4*prmonth - 1) % 24]),
        (1, ['osa3.py', 'oe', pryear-1992, prmonth * 2 - 1]),
        (1, ['aip3.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + 4*prmonth % 24]),
        (1, ['osa3.py', 'oe', pryear-1992, prmonth * 2]),
        (1, ['aip3.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + (4*prmonth - 3) % 24]),
        (1, ['osa3.py', 'ao', pryear-1961, prmonth * 3 - 2]),
        (1, ['aip3.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + (4*prmonth - 2) % 24]),
        (1, ['osa3.py', 'ao', pryear-1961, prmonth * 3 - 1]),
        (1, ['aip3.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + (4*prmonth - 1) % 24]),
        (1, ['osa3.py', 'ao', pryear-1961, prmonth * 3]),
        (1, ['aip3.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + 4*prmonth % 24]),
        (1, ['osa3.py', 'josaa', pryear-1983, prmonth]),
        (1, ['aip3.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + (4*prmonth - 3) % 24]),
        (1, ['osa3.py', 'josab', pryear-1983, prmonth]),
        (1, ['aip3.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + (4*prmonth - 2) % 24]),
        (1, ['osa3.py', 'optica', pryear-2013, prmonth]),
        (1, ['aip3.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + (4*prmonth - 1) % 24]),
        (2, ['theses-oregon3.py']),
        (1, ['aip3.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + 4*prmonth % 24]),
        (2, ['theses-aachen3.py']),
        (1, ['aip3.py', 'ajp', pryear-1932, prmonth]),
        (2, ['theses-oatd.py', '0', '3']),
        (1, ['aip3.py', 'phf', pryear-1988, prmonth]),
        (3, ['theses-oatd.py', '3', '5']),
        (2, ['aip3.py', 'jva', pryear-1982, prsixth]),
        (2, ['theses-oatd.py', '5', '7']),
        (2, ['aip3.py', 'jvb', pryear-1982, prsixth]),
        (3, ['theses-oatd.py', '7', '9']),
        (3, ['aip3.py', 'aqs', pryear-2018, prquarter]),
        (1, ['mdpi.sftp.py', 'symmetry']),
        (1, ['aip3.py', 'pto', pryear-1947, prmonth]),
        (1, ['mdpi.sftp.py', 'sensors']),
        (1, ['cjp.py', 'cjp', pryear-1922, prmonth]),
        (1, ['mdpi.sftp.py', 'nanomaterials']),
        (2, ['theses-oatd.py', '9', '11']),
        (12, ['annualreview.py', 'arnps', pryear-1950]),
        (3, ['theses-oatd.py', '11', '13']),
        (12, ['annualreview.py', 'araa', pryear-1962]),
        (2, ['theses-oatd.py', '13', '15']),
        (1, ['royalsociety.xml2.py', 'prs', pryear-1544, (pryear-1834)*12+prmonth]),
        (3, ['theses-oatd.py', '15', '17']),
        (1, ['actapolytechnica.py']),
        (2, ['theses-oatd.py', '17', '19 ']),
        (2, ['oxfordjournals.xml.py', 'pasj', pryear-1948, prsixth]),
        (3, ['theses-oatd.py', '19', '21']),
        (1, ['oxfordjournals.xml.py', 'ptep', pryear, prmonth]),
        (2, ['theses-oatd.py', '21', '23']),
        (1, ['figshare.py', 'kilthub']),
        (3, ['theses-oatd.py', '23', '25']),
        (1, ['mdpi.sftp.py', 'universe']),
        (2, ['theses-oatd.py', '25', '27']),
        (1, ['oxfordjournals.xml.py', 'imrn', pryear, 2*prmonth]),
        (3, ['theses-oatd.py', '27', '29']),
        (3, ['ccsenet.py', 'apr', pryear-2008, prquarter]),
        (2, ['theses-oatd.py', '29', '31']),
        (1, ['oxfordjournals.xml.py', 'mnras', mnrasbignumber//4, mnrasbignumber % 4 + 1]),
        (2, ['ccsenet.py', 'jmr', pryear-2008, prsixth]),
        (3, ['intlpress.py', 'cms', pryear-2002, prquarter]),
        (1, ['oxfordjournals.xml.py', 'mnras', (mnrasbignumber+1)//4, (mnrasbignumber+1)%4 + 1]),
        (1, ['edpjournals.py', 'aanda', pryear, prmonth]),
        (1, ['oxfordjournals.xml.py', 'mnras', (mnrasbignumber+2)//4, (mnrasbignumber+2)%4 + 1]),
        (3, ['intlpress.py', 'jsg', pryear-2002, prquarter]),
        (1, ['oxfordjournals.xml.py', 'mnrasl', mnrasbignumber//4, '1']),
        (2, ['scipost.py', 'sps', 2*(pryear-2016) + (prmonth-1)//6, (prmonth -1) % 6 +1]),
        (3, ['chicago.py', 'bjps', prpryear, prpryear-1949, prprquarter]),
        (1, ['figshare.py', 'monash']),
        (1, ['oxfordjournals.xml.py', 'imrn', pryear, 2*prmonth-1]),
        (1, ['mdpi.sftp.py', 'galaxies']),
        (1, ['cambridgebooks.xml.py']),
        (1, ['mdpi.sftp.py', 'entropy']),
        (1, ['oxfordbooks3.py']),
        (1, ['wspbooks3.py']),
        (2, ['theses-kit3.py']),
        (3, ['theses-ora.py']),
        (2, ['theses-nikhef.py']),
        (2, ['theses-clas.py']),
        (2, ['theses-kentucky.py']),
        (2, ['theses-sissa.py']),
        (2, ['theses-maryland.py']),
        (1, ['figshare.py', 'ryerson']),
        (2, ['theses-belle.py']),
        (2, ['theses-CSUC.py']),
        (2, ['theses-cambridge.py']),
        (2, ['theses-pennstate.py']),
        (2, ['theses-DCN.py']),
        (2, ['theses-PANDA.py']),
        (1, ['mdpi.sftp.py', 'particles']),
        (1, ['oxfordjournals.xml.py', 'mnras', 1 + mnrasbignumber//4, mnrasbignumber % 4 + 1, 'in_progress']),
        (1, ['mdpi.sftp.py', 'physics']),
        (1, ['oxfordjournals.xml.py', 'mnras', 1 + (mnrasbignumber+1)//4, (mnrasbignumber+1)%4 + 1, 'in_progress']),
        (1, ['procnas3.py', pryear-1903, '%i,%i' % (4*(prmonth-1)+1, 4*(prmonth-1)+2)]),
        (1, ['oxfordjournals.xml.py', 'mnras', 1 + (mnrasbignumber+2)//4, (mnrasbignumber+2)%4 + 1, 'in_progress']),
        (1, ['mdpi.sftp.py', 'condensedmatter']),
        (1, ['oxfordjournals.xml.py', 'mnrasl', 1 + mnrasbignumber//4, 'in_progress']),
        (1, ['procnas3.py', pryear-1903, '%i,%i' % (4*(prmonth-1)+3, 4*(prmonth-1)+4)]),
        (2, ['annualreview.py', 'arcmp', pryear-2009]),
        (2, ['theses-kit_etp.py']),
        (1, ['mdpi.sftp.py', 'atoms']),
        (3, ['spie_journal.py', 'jatis', pryear-2014, prquarter]),
        (3, ['messenger.py', 4*pryear + prquarter - 7902]),
        (1, ['sciencemag3.py', 'science', pryear]),
        (2, ['theses-unesp3.py']),
        (1, ['sciencemag3.py', 'sciadv', pryear]),
        (2, ['theses-eth.py']),
        (2, ['theses-hub.py']),
        (2, ['theses-mit.py']),
        (1, ['theses-unibo.py']),
        (1, ['theses-heidelberg.py']),
        (1, ['theses-rutgers.py']),
        (2, ['theses-frankfurt.py']),
        (1, ['theses-diva.py']),
        (1, ['theses-tum.py']),
        (2, ['theses-waterloo.py']),
        (2, ['theses-princeton.py']),
        (2, ['theses-capetown.py']),
        (1, ['sciencemag3.py', 'science', pryear]),
        (1, ['theses-uam.py']),
        (2, ['theses-durham.py']),
        (1, ['sciencemag3.py', 'sciadv', pryear]),
        (2, ['theses-southampton.py']),
        (2, ['theses-imperial.py']),
        (2, ['theses-bern.py']),
        (2, ['theses-edinburgh.py']),
        (2, ['theses-kyoto.py']),
        (1, ['theses-narcis.py']),
        (2, ['theses-tud.py']),
        (1, ['theses-surrey.py']),
        (2, ['theses-lmu.py']),
        (1, ['theses-regensburg.py']),
        (2, ['theses-saopaulo.py']),
        (2, ['theses-wm.py']),
        (2, ['theses-michigan.py']),
        (2, ['theses-epfl.py']),
        (2, ['theses-erlangen.py']),
        (1, ['theses-ucla.py', 'ucla']),
        (1, ['theses-wuerzburg.py']),
        (1, ['theses-oklahoma.py']),
        (1, ['theses-infn.py']),
        (2, ['theses-ino.py']),
        (2, ['theses-cologne.py']),
        (2, ['theses-charles.py']),
        (2, ['theses-victoria.py']),
        (2, ['theses-valencia.py']),
        (2, ['theses-bielefeld.py']),
        (2, ['theses-cracow.py']),
        (2, ['theses-cornell.py']),
        (2, ['theses-texasam.py']),
        (2, ['theses-gent.py']),
        (2, ['theses-mainz.py']),
        (2, ['theses-texas.py']),
        (2, ['theses-johnhopkins.py']),
        (2, ['theses-sidney.py']),
        (2, ['theses-toronto.py']),
        (2, ['theses-arizona.py']),
        (2, ['theses-carleton.py']),
        (2, ['theses-duke.py']),
        (1, ['theses-ucla.py', 'ucd']),
        (3, ['theses-shodganga.py', 'Astro', '1', '500']),
        (1, ['theses-ucla.py', 'uci']),
        (2, ['theses-shodganga.py', 'Physics', '1', '50']),
        (1, ['theses-ucla.py', 'ucb']),
        (2, ['theses-shodganga.py', 'Physics', '51', '100']),
        (1, ['theses-ucla.py', 'ucr']),
        (2, ['theses-shodganga.py', 'Physics', '101', '150']),
        (1, ['theses-ucla.py', 'ucsd']),
        (2, ['theses-shodganga.py', 'Physics', '151', '200']),
        (1, ['theses-ucla.py', 'ucsf']),
        (2, ['theses-shodganga.py', 'Physics', '201', '500']),
        (2, ['theses-aachen.py']),
        (3, ['theses-shodganga.py', 'Math', '1', '50']),
        (2, ['theses-harvard.py']),
        (3, ['theses-shodganga.py', 'Math', '51', '100']),
        (1, ['theses-ucla.py', 'ucsb']),
        (3, ['theses-shodganga.py', 'Math', '101', '150']),
        (1, ['theses-ucla.py', 'ucsc']),
        (3, ['theses-shodganga.py', 'Math', '151', '200']),
        (2, ['theses-ibict.py', 'physics']),
        (3, ['theses-shodganga.py', 'Math', '201', '500']),
        (2, ['theses-ibict.py', 'math']),
        (1, ['theoj.py', 'joss']),
        (2, ['theses-ibict.py', 'nucl']),
        (2, ['theses-prr.py']),
        (2, ['theses-ibict.py', 'physpost']),
        (2, ['theses-freiburg.py']),
        (2, ['theses-montreal.py']),
        (2, ['theses-hamburg.py']),
        (3, ['theses-nielsbohr.py']),
        (2, ['theses-pittsburgh.py']),
        (3, ['theses-unlp.py']),
        (3, ['theses-simonfraser.py']),
        (2, ['theses-liverpool.py']),
        (2, ['theses-baylor.py']),
        (2, ['theses-mcgill.py']),
        (2, ['theses-uclondon.py']),
        (2, ['theses-italy3.py', 'milanbicocca']),
        (3, ['theses-adelaide.py']),
        (2, ['theses-glasgow.py']),
        (2, ['theses-siegen.py']),
        (2, ['theses-basel.py']),
        (2, ['theses-britishcolumbia.py']),
        (2, ['theses-bonn2.py', pryear]),
        (2, ['theses-granada.py']),
        (2, ['theses-stanford.py']),
        (3, ['theses-chilecatolica.py']),
        (3, ['theses-wuppertal.py']),
        (3, ['theses-kansas.py']),
        (2, ['theses-chicago.py']),
        (2, ['theses-padua.py']),
        (2, ['theses-purdue.py']),
        (1, ['theses-columbia3.py']),
        (1, ['theses-tel.py']),
        (2, ['theses-sussex.py']),
        (2, ['theses-federicosantamaria.py']),
        (2, ['theses-hannover.py']),
        (2, ['theses-stonybrook.py']),
        (2, ['theses-nust.py']),
        (2, ['theses-cbpf.py']),
        (2, ['theses-chennai.py']),
        (2, ['theses-caltech.py']),
        (2, ['theses-iowa.py']),
        (1, ['mdpi.sftp.py', 'mathematics']),
        (2, ['theses-floridastate.py']),
        (3, ['theses-southermethodist.py']),
        (2, ['theses-tubingen.py']),
        (2, ['theses-waynestate.py']),
        (2, ['theses-thueringen.py']),
        (1, ['theses-minnesota.py']),
        (2, ['oxfordjournals.xml.py', 'astrogeo', pryear-1959, prsixth]),
        (2, ['theses-indiana.py']),
        (1, ['theses-alberta.py']),
        (2, ['theses-mississippi.py']),
        (3, ['theses-vtech.py']),
        (3, ['theses-vcommonwealth.py']),
        (3, ['comaphy.py', pryear-1998, prquarter]),
        (2, ['theses-tokyo.py']),
        (2, ['theses-unlp.py']),
        (2, ['theses-dresden.py']),
        (2, ['theses-northcarolina.py']),
        (2, ['theses-gsi.py']),
        (2, ['theses-osti.py']),
        (3, ['theses-brown.py']),
        (3, ['theses-lancaster.py']),
        (3, ['theses-warwick.py']),
        (2, ['theses-rome.py']),
        (2, ['theses-lund.py']),
        (2, ['theses-italy3.py', 'trento']),
        (2, ['theses-italy3.py', 'pavia']),
        (2, ['theses-italy3.py', 'turinpoly']),
        (2, ['theses-italy3.py', 'milan']),
        (2, ['theses-italy3.py', 'udine']),
        (2, ['theses-italy3.py', 'genoa']),
        (3, ['theses-italy3.py', 'ferrara']),
        (3, ['theses-italy3.py', 'siena']),
        (3, ['theses-italy3.py', 'verona']),
        (2, ['theses-italy3.py', 'cagliari']),
        (2, ['theses-italy3.py', 'sns']),
        (2, ['theses-italy3.py', 'cagliarieprints']),
        (3, ['theses-oslo.py']),
        (3, ['theses-naples.py']),
        (3, ['theses-cantabria.py']),
        (3, ['theses-coimbra.py']),
        (3, ['theses-salerno.py']),
        (3, ['theses-kamiokande.py']),
        (3, ['theses-louvain.py']),
        (2, ['theses-graz.py']),
        (2, ['theses-osaka.py']),
        (3, ['theses-kingscollege.py']),
        (3, ['theses-okayama.py']),
        (2, ['theses-italy3.py', 'parma']),
        (2, ['theses-washington.py']),
        (2, ['theses-queenmary.py']),
        (3, ['theses-trinity.py']),
        (3, ['theses-jyvaskyla.py']),
        (2, ['theses-ohio.py']),
        (1, ['theses-manitoba.py']),
        (2, ['theses-canterbury.py']),
        (2, ['theses-saskatchewan.py']),
        (1, ['theses-manchester.py']),
        (2, ['theses-compostella.py']),
        (2, ['theses-riogrande.py']),
        (6, ['cahiers.py']),
        (2, ['theses-tuwien.py']),
        (2, ['theses-amsterdam.py']),
        (3, ['theses-colombiaunatl.py']),
        (1, ['theses-northeastern.py']),
        (1, ['theses-forskningsdatabasen.py']), #stopped January 2021
        (2, ['theses-arizona_u.py']),
        (2, ['theses-geneve.py']),
        (3, ['theses-hawc.py']),
        (3, ['theses-concepcion.py']),
        (2, ['theses-illinois.py']),
        (2, ['theses-melbourne.py']),
        (2, ['theses-barcelona.py']),
        (2, ['theses-seoulnatlu.py']),
        (1, ['quantum.py', pryear-2016]),
        (1, ['mdpi.sftp.py', 'quantumrep']),
        (3, ['theses-witwatersrand.py']),
        (2, ['theses-birmingham.py']),
        (2, ['theses-montana.py']),
        (2, ['theses-zurich.py']),
        (2, ['theses-warsaw.py']),
        (2, ['theses-zagreb.py']),
        (3, ['scipost.py', 'spsc', pryear-2017, prquarter]),
        (1, ['figshare.py', 'lboro']),
        (3, ['ljp.py']),
        (1, ['acs3.py', 'nalefd', pryear-2000, prmonth]),
        (2, ['scipost.py', 'spsln']),
        (1, ['acs3.py', 'jctcce', pryear-2004, prmonth]),
        (2, ['theses-italy3.py', 'trieste']),
        (1, ['acs3.py', 'apchd5', pryear-2013, prmonth]),
        (3, ['theses-northernillinois.py']),
        (1, ['theses-leuven.py']),
        (2, ['msp.py']),
        (3, ['theses-izmir.py']),
        (2, ['theses-kansasu.py']),
        (2, ['theses-barcelonaautonoma.py']),
        (2, ['theses-mcmaster.py']),
        (2, ['theses-oregon.py']),
        (2, ['theses-brunel.py']),
        (3, ['theses-paraiba.py']),
        (2, ['theses-dart.py']),
        (1, ['theses-didaktorika.py']),
        (2, ['theses-giessen.py']),
        (2, ['theses-bochum.py']),
        (2, ['theses-lisbon.py']),
        (2, ['theses-munster.py']),
        (3, ['theses-houston.py']),
        (3, ['theses-iisc.py']),
        (1, ['mdpi.sftp.py', 'applsci']),
        (2, ['theses-hawaii.py']),
        (3, ['theses-porto.py']),
        (4, ['theses-dart.py']),
        (3, ['edpjournals.py', '4open', pryear, '1']),
        (2, ['theses-wien.py']),
        (3, ['theses-rostock.py']),
        (3, ['theses-texastech.py']),
        (2, ['theses-rochester.py']),
        (2, ['theses-colorado.py']),
        (1, ['mdpi.sftp.py', 'information']),
        (2, ['theses-buenosaires.py']),
        (2, ['theses-florida3.py']),
        (3, ['theses-syracuse.py']),
        (2, ['theses-ncsu.py']),
        (3, ['theses-oviedo.py']),
        (3, ['theses-yorkcanada.py']),
        (3, ['theses-alabama.py']),
        (3, ['theses-louisianastate.py']),
        (1, ['oapen.py']),
        (3, ['theses-tsukuba.py']),
        (3, ['theses-rice.py']),
        (3, ['npreview.py', pryear, prquarter]),
        (12, ['oxfordjournals.xml.py', 'integrablesystems', pryear-2015, '1']),
        (2, ['theses-taiwannatlu.py']),
        (2, ['theses-virginia.py']),
        (3, ['theses-washingtonustlouis.py']),
        (3, ['theses-swansea.py']),
        (3, ['theses-vanderbilt.py']),
        (3, ['theses-wisconsinmadison.py']),
        (3, ['theses-royalholloway.py']),
        (2, ['theses-ucm.py']),
        (3, ['theses-coloradostate.py']),
        (3, ['theses-nottingham.py']),
        (3, ['theses-cardiff.py']),
        (3, ['theses-floridaintlu.py']),
        (3, ['theses-olddominion.py']),
        (2, ['theses-connecticut.py']),
        (3, ['theses-hokkaido.py']),
        (3, ['theses-wisconsinmilwaukee.py']),
        (3, ['theses-hkust.py']),
        (2, ['theses-vrijeuamsterdam.py']),
        (3, ['theses-regina.py']),
        (2, ['theses-brussels.py']),
        (2, ['theses-ljubljana.py']),
        (1, ['theses-antwerp.py']),
        (3, ['theses-conicet.py']),
        (3, ['theses-groningen.py']),
        (2, ['theses-kyushu.py']),
        (3, ['theses-ankara.py']),
        (2, ['theses-new-mexico.py']),
        (2, ['theses-fub.py']),
        (3, ['theses-auckland3.py']),
        (5, ['theses-temple.py']),
        (3, ['theses-tennessee.py']),
        (2, ['theses-queensukingston.py']),
        (2, ['theses-estadoriodejaneiro.py']),
        (3, ['theses-georgiatech.py']),
        (3, ['theses-marburg.py']),
        (2, ['theses-salamanca.py']),
        (2, ['theses-kwazulu.py']),
        (3, ['theses-guelph.py']),
        (1, ['theses-potsdam.py']),
        (1, ['figshare.py', 'techrxiv']),
        (1, ['theses-middleeasttech.py']),
        (3, ['theses-wigner.py']),
        (3, ['theses-zaragoza.py']),
        (3, ['theses-melbourne.py']),
        (1, ['theses-queensland.py']),
        (3, ['theses-laval.py']),
        (3, ['theses-cyprus.py']),
        (2, ['theses-barcelonapolytech.py']),
        (1, ['mitbooks.py']),
        (2, ['theses-puebla.py']),
        (2, ['theses-westernaustralia3.py']),
        (2, ['theses-bergen3.py']),
        (3, ['theses-warwick3.py']),
        (1, ['sppu3.py', 'jpm'])]

if prmonth == 12:
    jnls.append((1, ['aip3.py', 'apl', 2*pryear - 3924 + 1, 25]))
    jnls.append((1, ['aip3.py', 'apl', 2*pryear - 3924 + 1, 26]))
    jnls.append((1, ['osa3.py', 'oe', pryear-1992, prmonth * 2 + 1]))
    jnls.append((1, ['osa3.py', 'oe', pryear-1992, prmonth * 2 + 2]))
    jnls.append((1, ['procnas3.py', pryear-1903, '49, 50']))
    jnls.append((1, ['procnas3.py', pryear-1903, '51, 52']))
    jnls.append((1, ['intlpress.py', pryear-1992, '7']))
    jnls.append((1, ['intlpress.py', pryear-1992, '8']))
if prmonth == 6:
    jnls.append((1, ['aip3.py', 'apl', 2*pryear - 3924, 25]))
    jnls.append((1, ['aip3.py', 'apl', 2*pryear - 3924, 26]))


#work from 3th to 28th day of a month
def checkday(entrynumber):
    return (3 + (entrynumber % 26) == today.day)

#writing to do list and protocol
prfil = open(protocol, "a")
print("previous month = %i/%i [today = %s]\n" % (prmonth, pryear, today.day))
prfil.write("\n---------{ %s }---{ running ejlwrapper3.py for previous month %i/%i }---------\n will start the following commands:\n" % (stampoftoday, prmonth, pryear))
listofcommands = []
for entrynumber in range(len(jnls)):
    if (prmonth % jnls[entrynumber][0] == 0) and checkday(entrynumber):
        listofcommands.append(jnls[entrynumber][1])
        prfil.write(' - ' + ' '.join([str(ee) for ee in jnls[entrynumber][1]]) + '\n')

#do always WSP or IOP or IEEE
if (today.day % 3 == 0):
    listofcommands.append(['wsp.xml2.py'])
    prfil.write(' - wsp.xml2.py\n')
elif (today.day % 3 == 1):
    listofcommands.append(['ieee_wrapper.py'])
    prfil.write(' - ieee_wrapper.py\n')
if (today.weekday() == 0):
    listofcommands.append(['pubdbweb.py'])
    prfil.write(' - pubdbweb.py\n')
#IOP books still old workflow
if (today.day % 7 == 0):
    listofcommands.append(['iop.stack.py'])
    prfil.write(' - iop.stacks.py\n')
else:
    listofcommands.append(['iop.sftp.py'])
    prfil.write(' - iop.sftp.py\n')

prfil.close()

#send to do list to FS
commandoliste = ''
for lc in listofcommands:
    commandoliste += '\n' + ' '.join([str(ee) for ee in lc])
os.system('echo "%s" | mail -s "ejlwrapper3 commands"  florian.schwennsen@desy.de ' % (commandoliste))


prfil = open(protocol, "a")
prfil.write('\n\n detailed protocols will be written to %s\n' % (logfile))
prfil.write(' has executed the following commands:\n')
prfil.close()


#do the jobs
refin = re.compile('FINISHED writenewXML\((.*);(.*)\)')
shortreport = ''
for com in listofcommands:
    writtenfiles = []
    print(com)
    time.sleep(10)
    if re.search('3\.py', com[0]):
        commando = [python['python3'], os.path.join(lproc['python3'], com[0])] + [str(c) for c in com[1:]]
    else:
        commando = [python['python2'], os.path.join(lproc['python2'], com[0])] + [str(c) for c in com[1:]]
    harvest = subprocess.Popen(commando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    result, errors = harvest.communicate()
    errors = re.sub('No handlers could be found for logger .?rdflib.term.?\n', '', errors)
    errors = re.sub('\/afs.*?\d+: UserWarning: No parser was explicitly specified.*?\n\n.*to the BeautifulSoup constructor.\n\n.*?\n', '    [kein expliziter Parser fuer BeautifulSoup angegeben]\n', errors)
    errors = re.sub('\/home\/library\/.virtualenvs\/inspire\/lib\/python2.7\/site-packages\/selenium\/webdriver\/phantomjs\/webdriver.py:49: UserWarning: Selenium support for PhantomJS has been deprecated, please use headless versions of Chrome or Firefox instead\n *warnings.warn..Selenium support for PhantomJS has been deprecated, please use headless *.', '    [PhantomJS ist veraltet]', errors)
    errors = re.sub('\/home\/library\/.virtualenvs\/inspire\/lib\/python2.7\/site-packages\/paramiko\/transport.py.*elease. *\n *from cryptography.hazmat.backends import default_backend', '    [Cryptography ist veraltet]', errors)
    #detailed log
    logfil = open(logfile, "a")
    logfil.write('========={ %s }=========\n' % (' '.join([str(c) for c in com])))
    logfil.write(result)
    for line in re.split('\n', result):
        if refin.search(line):
            writtenfiles.append(refin.sub(r'   \1.xml (\2 records)', line))
    logfil.write(errors)
    logfil.close()
    #summary to bes
    shortreport += '\n- ' + ' '.join(commando)
    shortreport += '\n  ' + '\n  '.join(writtenfiles) + '\n'
    if len(errors) > 0:
        shortreport += '\n' + errors + '\n'

    prfil = open(protocol, "a")
    prfil.write('  {did} ' + ' '.join([str(c) for c in com]) + '\n')
    prfil.close()


shortreport += '\n\ndetailed protocols has been written to '+logfile

prfil = open(protocol, "a")
prfil.write('\n' + 50*'-' +  shortreport + '\n\n')
prfil.close()

os.system('echo "%s" | mail -s "ejlwrapper3 finished"  florian.schwennsen@desy.de ' % (shortreport))

os.system('echo "ejlwrapper3 finished" >> '+logfile)
prfil = open(protocol, "a")
prfil.write(' ejlwrapper3.py has executed ALL commands.\n')
prfil.write("---------------------------------------------------------------------\n")
prfil.close()
