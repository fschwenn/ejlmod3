# this program (called regularly each month) calls dedicated
# programs to harvest journals by scaning homepages
#
# FS: 2022-06-13
#
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
python = {'python3' : '/home/library/.virtualenvs/inspire/bin/python',
          'python2' : 'python'}

#list of harvesters
#entries: (after how many months it should run next time, [program, argument1, argument2])
jnls = [(1, ['aip3YYY.py', 'rsi', pryear-1929, prmonth]),
        (1, ['aip3YYY.py', 'pto', pryear-1947, prmonth]),
        (1, ['aip3YYY.py', 'jmp', pryear-1959, prmonth]),
        (3, ['aip3YYY.py', 'aqs', pryear-2018, prquarter]),
        (1, ['aip3YYY.py', 'cha', pryear-1990, prmonth]),
        (2, ['aip3XXX.py', 'jvb', pryear-1982, prsixth]),
        (1, ['aip3YYY.py', 'ltp', pryear-1974, prmonth]),
        (1, ['aip3YYY.py', 'php', pryear-1993, prmonth]),
        (1, ['aip3YYY.py', 'adv', pryear-2010, prmonth]),
        (1, ['aip3YYY.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + (4*prmonth - 3) % 24]),
        (1, ['aip3YYY.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + (4*prmonth - 2) % 24]),
        (1, ['aip3YYY.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + (4*prmonth - 1) % 24]),
        (1, ['aip3YYY.py', 'apl', 2*pryear - 3924 + ((prmonth-1) // 6), 1 + 4*prmonth % 24]),
        (1, ['aip3YYY.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + (4*prmonth - 3) % 24]),
        (1, ['aip3YYY.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + (4*prmonth - 2) % 24]),
        (1, ['aip3YYY.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + (4*prmonth - 1) % 24]),
        (1, ['aip3YYY.py', 'jcp', 2*pryear - 3888 + ((prmonth-1) // 6), 1 + 4*prmonth % 24]),
        (1, ['aip3YYY.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + (4*prmonth - 3) % 24]),
        (1, ['aip3YYY.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + (4*prmonth - 2) % 24]),
        (1, ['aip3YYY.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + (4*prmonth - 1) % 24]),
        (1, ['aip3YYY.py', 'jap', 2*pryear - 3913 + ((prmonth-1) // 6), 1 + 4*prmonth % 24]),
        (1, ['aip3YYY.py', 'ajp', pryear-1932, prmonth]),
        (1, ['aip3YYY.py', 'phf', pryear-1988, prmonth]),
        (2, ['aip3YYY.py', 'jva', pryear-1982, prsixth]),
        (6, ['theses-bogota3.py']),
        (3, ['theses-bristol3.py']),
        (2, ['theses-helda3.py']),
        (1, ['osa3XXX.py', 'ol', pryear-1975, prmonth * 2 - 1]),
        (1, ['osa3XXX.py', 'ol', pryear-1975, prmonth * 2]),
        (1, ['osa3XXX.py', 'oe', pryear-1992, prmonth * 2 - 1]),
        (1, ['osa3XXX.py', 'oe', pryear-1992, prmonth * 2]),
        (1, ['osa3XXX.py', 'ao', pryear-1961, prmonth * 3 - 2]),
        (1, ['osa3XXX.py', 'ao', pryear-1961, prmonth * 3 - 1]),
        (1, ['osa3XXX.py', 'ao', pryear-1961, prmonth * 3]),
        (1, ['osa3XXX.py', 'josaa', pryear-1983, prmonth]),
        (1, ['osa3XXX.py', 'josab', pryear-1983, prmonth]),
        (1, ['osa3XXX.py', 'optica', pryear-2013, prmonth]),
        (3, ['theses-oregon3.py']),
        (2, ['theses-aachen3.py']),
        (2, ['theses-oatdXXX.py', '0', '5']), #proteced by Claudflare
        (2, ['theses-oatdXXX.py', '5', '10']), #proteced by Claudflare
        (2, ['theses-oatdXXX.py', '10', '15']), #proteced by Claudflare
        (2, ['theses-oatdXXX.py', '15', '20']), #proteced by Claudflare
        (2, ['theses-oatdXXX.py', '20', '25']), #proteced by Claudflare
        (2, ['theses-oatdXXX.py', '25', '30']), #proteced by Claudflare
        (2, ['theses-oatdXXX.py', '30', '35']), #proteced by Claudflare
        (1, ['mdpi.sftp3.py', 'symmetry']),
        (1, ['mdpi.sftp3.py', 'sensors']),
        (1, ['cjp3XXX.py', 'cjp', pryear-1922, prmonth]),
        (1, ['mdpi.sftp3.py', 'nanomaterials']),
        (12, ['annualreview3.py', 'arnps', pryear-1950]),
        (12, ['annualreview3.py', 'araa', pryear-1962]),
        (1, ['royalsociety3XXX.py', 'prs', pryear-1544, (pryear-1834)*12+prmonth]),
        (1, ['actapolytechnica3.py']),
        (2, ['oxfordjournals3.py', 'pasj', pryear-1948, prsixth]),
        (1, ['oxfordjournals3.py', 'ptep', pryear, prmonth]),
        (1, ['figshare3.py', 'kilthub']),
        (1, ['mdpi.sftp3.py', 'universe']),
        (2, ['ccsenet3.py', 'jmr', pryear-2008, prsixth]),
        (2, ['intlpress3.py', 'cms', pryear-2002, prsixth]),
        (1, ['oxfordjournals3.py', 'imrn', pryear, 2*prmonth]),
        (1, ['oxfordjournals3.py', 'mnras', mnrasbignumber//4, mnrasbignumber % 4 + 1]),
        (1, ['oxfordjournals3.py', 'mnras', (mnrasbignumber+1)//4, (mnrasbignumber+1)%4 + 1]),
        (1, ['edpjournals3XXX.py', 'aanda', pryear, prmonth]),
        (1, ['oxfordjournals3.py', 'mnras', (mnrasbignumber+2)//4, (mnrasbignumber+2)%4 + 1]),
        (1, ['oxfordjournals3.py', 'mnrasl', mnrasbignumber//4, '1']),
        (2, ['scipost3.py', 'sps', 2*(pryear-2016) + (prmonth-1)//6, (prmonth -1) % 6 +1]),
        (1, ['oxfordjournals3.py', 'mnras', 1 + mnrasbignumber//4, mnrasbignumber % 4 + 1, 'in_progress']),
        (1, ['oxfordjournals3.py', 'mnras', 1 + (mnrasbignumber+1)//4, (mnrasbignumber+1)%4 + 1, 'in_progress']),
        (1, ['oxfordjournals3.py', 'mnras', 1 + (mnrasbignumber+2)//4, (mnrasbignumber+2)%4 + 1, 'in_progress']),
        (1, ['oxfordjournals3.py', 'mnrasl', 1 + mnrasbignumber//4, '1', 'in_progress']),
        (3, ['chicago3XXX.py', 'bjps', prpryear, prpryear-1949, prprquarter]),
        (1, ['oxfordjournals3.py', 'mnras', 2 + mnrasbignumber//4, mnrasbignumber % 4 + 1, 'early']),
        (1, ['oxfordjournals3.py', 'mnras', 2 + (mnrasbignumber+1)//4, (mnrasbignumber+1)%4 + 1, 'early']),
        (1, ['oxfordjournals3.py', 'mnras', 2 + (mnrasbignumber+2)//4, (mnrasbignumber+2)%4 + 1, 'early']),
        (1, ['oxfordjournals3.py', 'mnrasl', 2 + mnrasbignumber//4, '1', 'early']),
        (1, ['figshare3.py', 'monash']),
        (1, ['oxfordjournals3.py', 'imrn', pryear, 2*prmonth-1]),
        (1, ['mdpi.sftp3.py', 'galaxies']),
        (1, ['cambridgebooks3.py']),
        (1, ['mdpi.sftp3.py', 'entropy']),
        (1, ['oxfordbooks3XXX.py']),
        (1, ['wspbooks3XXX.py']),
        (2, ['theses-kit3XXX.py']),
        (3, ['theses-ora3.py']),
        (2, ['theses-nikhef3.py']),
        (2, ['theses-clas3.py']),
        (2, ['theses-kentucky3.py']),
        (2, ['theses-italy3XXX.py', 'sissa']),
        (1, ['theses-maryland3XXX.py']),
        (1, ['figshare3.py', 'ryerson']),
        (2, ['theses-belle3.py']),
        (2, ['theses-CSUC3.py']),
        (2, ['theses-cambridge3.py']),
        (2, ['theses-pennstate3.py']),
        (2, ['theses-DCN3.py']),
        (2, ['theses-PANDA3.py']),
        (1, ['mdpi.sftp3.py', 'particles']),
        (1, ['mdpi.sftp3.py', 'physics']),
        (1, ['procnas3XXX.py', pryear-1903, '%i,%i' % (4*(prmonth-1)+1, 4*(prmonth-1)+2)]),
        (1, ['mdpi.sftp3.py', 'condensedmatter']),
        (1, ['procnas3XXX.py', pryear-1903, '%i,%i' % (4*(prmonth-1)+3, 4*(prmonth-1)+4)]),
        (12, ['annualreview3.py', 'arcmp', pryear-2009]),
        (2, ['theses-kit_etp3.py']),
        (1, ['mdpi.sftp3.py', 'atoms']),
        (3, ['spie_journal3.py', 'jatis', pryear-2014, prquarter]),
        (3, ['messenger3.py', 4*pryear + prquarter - 7902 - 2]),
        (2, ['theses-unesp3.py']),
        (2, ['theses-eth3.py']),
        (2, ['theses-hub3XXX.py']),
        (2, ['theses-mit3.py']),
        (1, ['theses-unibo3.py']),
        (1, ['theses-heidelberg3.py']),
        (1, ['theses-rutgers3.py']),
        (2, ['theses-frankfurt3.py']),
        (1, ['theses-diva3.py']),
        (1, ['theses-tum3.py']),
        (1, ['theses-goettingen3.py']),
        (2, ['theses-waterloo3.py']),
        (2, ['theses-princeton3.py']),
        (2, ['theses-capetown3XXX.py']),
        (1, ['sciencemag3XXX.py', 'science', pryear]),
        (1, ['theses-uam3.py']),
        (2, ['theses-durham3.py']),
        (1, ['sciencemag3XXX.py', 'sciadv', pryear]),
        (2, ['theses-southampton3.py']),
        (1, ['theses-imperial3.py']),
        (2, ['theses-bern3.py']),
        (2, ['theses-edinburgh3.py']),
        (2, ['theses-kyoto3.py']),
        (1111, ['theses-narcis3.py']), #dead
        (2, ['theses-tud3.py']),
        (1, ['theses-surrey3.py']),
        (1, ['theses-lmu3.py']),
        (1, ['theses-regensburg3.py']),
        (2, ['theses-saopaulo3.py']),
        (2, ['theses-wm3.py']),
        (2, ['theses-michigan3.py']),
        (2, ['theses-epfl3.py']),
        (2, ['theses-erlangen3.py']),
        (1, ['theses-ucla3.py', 'ucla']),
        (1, ['theses-wuerzburg3.py']),
        (1, ['theses-oklahoma3.py']),
        (1, ['theses-infn.py']),
        (2, ['theses-ino3.py']),
        (2, ['theses-cologne3.py']),
        (2, ['theses-charles3.py']),
        (2, ['theses-victoria3.py']),
        (1, ['theses-valencia3.py']),
        (2, ['theses-bielefeld3.py']),
        (2, ['theses-cracow3.py']),
        (1, ['theses-cornell3XXX.py']),
        (1, ['theses-texasam3.py']),
        (2, ['theses-gent3.py']),
        (2, ['theses-mainz3.py']),
        (1, ['theses-texas3XXX.py']),
        (2, ['theses-johnhopkins3XXX.py']),
        (2, ['theses-sidney3XXX.py']),
        (1, ['theses-toronto3.py']),
        (2, ['theses-arizona3.py']),
        (2, ['theses-carleton3.py']),
        (2, ['theses-duke3.py']),
        (1, ['theses-ucla3.py', 'ucd']),
        (3, ['theses-shodganga3.py', 'Astro', '1', '500']),
        (1, ['theses-ucla3.py', 'uci']),
        (2, ['theses-shodganga3.py', 'Physics', '1', '50']),
        (1, ['theses-ucla3.py', 'ucb']),
        (2, ['theses-shodganga3.py', 'Physics', '51', '100']),
        (1, ['theses-ucla3.py', 'ucr']),
        (2, ['theses-shodganga3.py', 'Physics', '101', '150']),
        (1, ['theses-ucla3.py', 'ucsd']),
        (2, ['theses-shodganga3.py', 'Physics', '151', '200']),
        (1, ['theses-ucla3.py', 'ucsf']),
        (2, ['theses-shodganga3.py', 'Physics', '201', '500']),
        (1, ['theses-mpg3.py']),
        (3, ['theses-shodganga3.py', 'Math', '1', '50']),
        (1, ['theses-harvard3XXX.py']),
        (3, ['theses-shodganga3.py', 'Math', '51', '100']),
        (1, ['theses-ucla3.py', 'ucsb']),
        (3, ['theses-shodganga3.py', 'Math', '101', '150']),
        (1, ['theses-ucla3.py', 'ucsc']),
        (3, ['theses-shodganga3.py', 'Math', '151', '200']),
        (2, ['theses-ibict3.py', 'physics']),
        (3, ['theses-shodganga3.py', 'Math', '201', '500']),
        (2, ['theses-ibict3.py', 'math']),
        (1, ['theoj3XXX.py', 'joss']),
        (2, ['theses-ibict3.py', 'cnpq']),
        (2, ['theses-prr3.py']),
        (2, ['theses-ibict3.py', 'physpost']),
        (2, ['theses-freiburg3.py']),
        (2, ['theses-montreal3.py']),
        (2, ['theses-hamburg3.py']),
        (3, ['theses-nielsbohr3.py']),
        (2, ['theses-pittsburgh3.py']),
        (3, ['theses-unlp3.py']),
        (3, ['theses-simonfraser3.py']),
        (2, ['theses-liverpool3.py']),
        (3, ['theses-baylor3XXX.py']),
        (1, ['theses-mcgill3.py']),
        (2, ['theses-uclondon3.py']),
        (2, ['theses-italy3XXX.py', 'milanbicocca']),
        (3, ['theses-adelaide3.py']),
        (1, ['theses-glasgow3.py']),
        (1, ['theses-siegen3.py']),
        (1, ['theses-basel3.py']),
        (1, ['theses-britishcolumbia3XXX.py']),
        (1, ['theses-bonn23.py', pryear]),
        (1, ['theses-granada3.py']),
        (2, ['theses-stanford3.py']),
        (3, ['theses-wuppertal3.py']),
        (1, ['theses-kansas3.py']),
        (2, ['theses-chicago3.py']),
#        (666, ['theses-padua.py']), # hat nur Bachlor (Laurea triennale) und Master (Laurea magistrale/Laurea Specialistica)
        (4, ['theses-purdue3.py']),
        (1, ['theses-columbia3.py']),
        (1, ['theses-tel3.py']),
        (2, ['theses-sussex3.py']),
        (2, ['theses-federicosantamaria3.py']),
        (2, ['theses-hannover3.py']),
#        (666, ['theses-stonybrook.py']), #2017 eingeschlafen, https://commons.library.stonybrook.edu/ not yet ready?
        (2, ['theses-nust3.py']),
        (2, ['theses-cbpf3.py']),
        (2, ['theses-chennai3.py']),
        (2, ['theses-caltech3.py']),
        (2, ['theses-iowa3.py']),
        (1, ['mdpi.sftp3.py', 'mathematics']),
        (2, ['theses-floridastate3XXX.py']),
        (3, ['theses-southermethodist3.py']),
        (2, ['theses-tubingen3.py']),
        (2, ['theses-waynestate3.py']),
        (2, ['theses-thueringen3XXX.py']),
        (1, ['theses-minnesota3.py']),
        (2, ['oxfordjournals3.py', 'astrogeo', pryear-1959, prsixth]),
        (1, ['theses-indiana3.py']),
        (1, ['theses-alberta3.py']),
        (2, ['theses-mississippi3.py']),
        (3, ['theses-vtech3.py']),
        (3, ['theses-vcommonwealth3.py']),
        (3, ['comaphy3.py', pryear-1998, prquarter]),
        (2, ['theses-qucosa3XXX.py', 'dresden']),
        (2, ['theses-northcarolina3.py']),
        (2, ['theses-gsi3.py']),
        (2, ['theses-osti3XXX.py']),
        (3, ['theses-brown3.py']),
        (3, ['theses-lancaster3.py']),
        (3, ['theses-warwick3.py']),
        (2, ['theses-rome3.py']),
        (2, ['theses-lund3.py']),
        (2, ['theses-italy3XXX.py', 'trento']),
        (2, ['theses-italy3XXX.py', 'pavia']),
        (2, ['theses-italy3XXX.py', 'turinpoly']),
        (2, ['theses-italy3XXX.py', 'milan']),
        (2, ['theses-italy3XXX.py', 'udine']),
        (2, ['theses-italy3XXX.py', 'genoa']),
        (3, ['theses-italy3XXX.py', 'ferrara']),
        (3, ['theses-italy3XXX.py', 'siena']),
        (3, ['theses-italy3XXX.py', 'verona']),
        (2, ['theses-italy3XXX.py', 'cagliari']),
        (2, ['theses-italy3XXX.py', 'sns']),
        (3, ['theses-naples3.py']),
        (3, ['theses-cantabria3.py']),
        (3, ['theses-coimbra3.py']),
        (3, ['theses-salerno3.py']),
        (3, ['theses-kamiokande3.py']),
        (3, ['theses-louvain3.py']),
        (2, ['theses-graz3.py']),
        (2, ['theses-osaka3.py']),
        (3, ['theses-kingscollege3.py']),
        (3, ['theses-okayama3.py']),
        (2, ['theses-italy3XXX.py', 'parma']),
        (2, ['theses-washington3.py']),
        (2, ['theses-queenmary3.py']),
        (1, ['theses-trinity3.py']),
        (3, ['theses-jyvaskyla3.py']),
        (1, ['theses-manitoba3.py']),
        (2, ['theses-canterbury3XXX.py']),
        (2, ['theses-saskatchewan3.py']),
        (1, ['theses-manchester3.py']),
        (2, ['theses-compostella3.py']),
        (2, ['theses-riogrande3.py']),
        (6, ['cahiers3.py']),
        (1, ['theses-wien3.py']),
        (2, ['theses-amsterdam3XXX.py']),
        (3, ['theses-colombiaunatl3.py']),
        (1, ['theses-northeastern3XXX.py']),
        (1, ['theses-forskningsportal3.py']),
        (3, ['theses-oslo3.py']),
        (2, ['theses-arizona_u3.py']),
        (2, ['theses-geneve3XXX.py']),
        (3, ['theses-hawc3.py']),
        (3, ['theses-concepcion3.py']),
        (2, ['theses-illinois3.py']),
        (2, ['theses-leedssheffieldyork3.py']),
        (2, ['theses-melbourne3.py']),
        (2, ['theses-barcelona3.py']),
        (2, ['theses-seoulnatlu3.py']),
        (1, ['quantum3.py', pryear-2016]),
        (1, ['mdpi.sftp3.py', 'quantumrep']),
        (3, ['theses-witwatersrand3.py']),
        (2, ['theses-birmingham3.py']),
        (2, ['theses-montana3.py']),
        (2, ['theses-zurich3.py']),
        (2, ['theses-warsaw3.py']),
        (2, ['theses-zagreb3.py']),
        (3, ['scipost3.py', 'spsc', pryear-2017, prquarter]),
        (1, ['figshare3.py', 'lboro']),
        (3, ['ljp3.py']),
        (1, ['acs3XXX.py', 'nalefd', pryear-2000, prmonth]),
        (2, ['scipost3.py', 'spsln']),
        (1, ['acs3XXX.py', 'jctcce', pryear-2004, prmonth]),
        (2, ['theses-italy3XXX.py', 'trieste']),
        (1, ['acs3XXX.py', 'apchd5', pryear-2013, prmonth]),
        (3, ['theses-northernillinois3.py']),
        (1, ['theses-leuven3XXX.py']),
        (2, ['msp3.py']),
        (3, ['theses-izmir3.py']),
        (2, ['theses-kansasu3.py']),
        (2, ['theses-barcelonaautonoma3XXX.py']),
        (2, ['theses-mcmaster3.py']),
        (2, ['theses-brunel3.py']),
        (3, ['theses-paraiba3.py']),
        (2, ['theses-dart3.py']),
        (1, ['theses-didaktorika3.py']),
        (1, ['theses-giessen3XXX.py']),
        (2, ['theses-bochum3.py']),
        (2, ['theses-lisbon3.py']),
        (2, ['theses-munster3.py']),
        (3, ['theses-houston3XXX.py']),
        (3, ['theses-iisc3XXX.py']),
        (1, ['mdpi.sftp3.py', 'applsci']),
        (2, ['theses-hawaii3.py']),
        (3, ['theses-porto3.py']),
        (3, ['edpjournals3.py', '4open', pryear, '1']),
        (1, ['theses-tuwien3.py']),
        (3, ['theses-rostock3.py']),
        (3, ['theses-texastech3.py']),
        (2, ['theses-rochester3.py']),
        (2, ['theses-colorado3.py']),
        (1, ['mdpi.sftp3.py', 'information']),
        (2, ['theses-buenosaires3.py']),
        (2, ['theses-florida3XXX.py']),
        (3, ['theses-syracuse3.py']),
        (2, ['theses-ncsu3.py']),
        (3, ['theses-oviedo3.py']),
        (3, ['theses-yorkcanada3XXX.py']),
        (3, ['theses-alabama3.py']),
        (3, ['theses-louisianastate3.py']),
        (1, ['oapen3.py']),
        (3, ['theses-tsukuba3XXX.py']),
        (3, ['theses-rice3XXX.py']),
#        (3333, ['npreview.py', pryear, prquarter]), #zu unregulaer
        (2, ['theses-taiwannatlu3.py']),
        (2, ['theses-virginia3XXX.py']),
        (3, ['theses-washingtonustlouis3.py']),
        (3, ['theses-swansea3.py']),
        (3, ['theses-vanderbilt3.py']),
        (3, ['theses-wisconsinmadison3XXX.py']),
        (3, ['theses-royalholloway3.py']),
        (2, ['theses-ucm3.py']),
        (3, ['theses-coloradostate3XXX.py']),
        (3, ['theses-nottingham3.py']),
        (3, ['theses-cardiff3.py']),
        (3, ['theses-floridaintlu3.py']),
        (3, ['theses-olddominion3.py']),
        (2, ['theses-connecticut3.py']),
        (3, ['theses-hokkaido3.py']),
        (3, ['theses-wisconsinmilwaukee3.py']),
        (3, ['theses-hkust3XXX.py']),
        (2, ['theses-vrijeuamsterdam3.py']),
        (3, ['theses-regina3.py']),
        (2, ['theses-brussels3XXX.py']),
        (2, ['theses-ljubljana3.py']),
        (1, ['theses-antwerp3.py']),
        (3, ['theses-conicet3.py']),
        (3, ['theses-groningen3.py']),
        (2, ['theses-kyushu3.py']),
        (3, ['theses-ankara3XXX.py']),
        (2, ['theses-new-mexico3.py']),
        (2, ['theses-fub3XXX.py']),
        (3, ['theses-auckland3.py']),
        (5, ['theses-temple3.py']),
        (3, ['theses-tennessee3.py']),
        (2, ['theses-queensukingston3XXX.py']),
        (2, ['theses-estadoriodejaneiro3.py']),
        (3, ['theses-georgiatech3XXX.py']),
        (2, ['theses-marburg3.py']),
        (2, ['theses-salamanca3.py']),
        (2, ['theses-kwazulu3.py']),
        (3, ['theses-guelph3XXX.py']),
        (1, ['theses-potsdam3.py']),
        (1, ['figshare3.py', 'techrxiv']),
        (1, ['theses-middleeasttech3XXX.py']),
        (3, ['theses-wigner3.py']),
        (3, ['theses-zaragoza3XXX.py']),
        (1, ['theses-queensland3XXX.py']),
        (3, ['theses-laval3XXX.py']),
        (3, ['theses-cyprus3XXX.py']),
        (2, ['theses-barcelonapolytech3XXX.py']),
        (1, ['mitbooks3.py']),
        (2, ['theses-puebla3XXX.py']),
        (2, ['theses-westernaustralia3XXX.py']),
        (2, ['theses-bergen3.py']),
        (3, ['theses-warwick3.py']),
        (1, ['sppu3.py', 'jpm']),
        (1, ['dergipark3.py', 'jum']),
        (1, ['theses-radboud3.py']),
        (4, ['theses-antioquia3.py']),
        (2, ['theses-rit3.py']),
        (2, ['theses-brasilia3.py']),
        (1, ['ems3.py']),
        (3, ['theses-italy3XXX.py', 'ferraraeprints']),
        (2, ['theses-cuny3.py']),
        (3, ['theses-maynooth3.py']),
        (2, ['theses-delaware3.py']),
        (2, ['theses-ifj3.py']),
        (1, ['scientific3.py']),
        (2, ['theses-ibict3.py', 'physics2']),
        (1, ['figshare3.py', 'leicester']),
        (2, ['scipost3.py', 'sps', 2*(prpryear-2016) + (prprmonth-1)//6, (prprmonth -1) % 6 +1]),
        (2, ['theses-unsw3.py']),
        (2, ['theses-italy3XXX.py', 'modena']),
        (3, ['theses-liege3XXX.py']),
        (3, ['theses-georgiastate3.py']),
        (3, ['theses-standrews3.py']),
        (3, ['theses-patras3XXX.py']),
        (2, ['theses-chilecatolica3.py']),
        (1, ['theses-upenn3.py']),
        (1, ['theses-umassamherst3XXX.py']),
        (1, ['theses-westvirginia3.py']),
        (1, ['theses-louisville3.py']),
        (1, ['theses-southcarolina3.py']),
        (3, ['theses-stellenbosch3XXX.py']),
        (1, ['theses-bepress3.py']),
        (1, ['theses-michigantech3.py']),
        (1, ['mdpi.sftp3.py', 'axioms']),
        (1, ['mdpi.sftp3.py', 'foundations']),
        (1, ['mdpi.sftp3.py', 'instruments']),
        (1, ['mdpi.sftp3.py', 'photonics']),
        (1, ['theses-louisianatech3.py']),
        (3, ['theses-minho3.py']),
        (3, ['theses-island3.py']),
        (2, ['theses-calgary3XXX.py']),
        (2, ['theses-aveiro3.py']),
        (2, ['theses-santacatarina3.py']),
        (2, ['theses-ohio3XXX.py']),
        (2, ['theses-coloradomines3.py']),
        (2, ['theses-debrecen3.py']),
        (2, ['theses-carlos3.py']),
        (3, ['theses-southdakota3.py']),
        (2, ['theses-valenciapolytechnic3.py']),
        (2, ['theses-sancarlosfederal3.py']),
        (1, ['theses-openuengland3.py']),
        (3, ['theses-utahstate3XXX.py']),
        (3, ['theses-dekalb3XXX.py']),
        (1, ['theses-limapont3.py']),
        (1, ['theses-clemson3.py']),
        (1, ['theses-cityulondon3.py']),
        (1, ['theses-bayreuth3.py']),
        (3, ['indianjst3XXX.py', pryear-2007]),
        (2, ['theses-waseda3.py']),
        (1, ['sciencemag3XXX.py', 'research', pryear]),
        (1, ['plosone3XXX.py']),
        (3, ['episciences3.py', pryear-2007]),
        (1, ['theses-boston3.py']),
        (1, ['theses-westernontario3.py']),
        (1, ['mdpi.sftp3.py', 'astronomy']),
        (1, ['figshare3.py', 'mq']),
        (1, ['figshare3.py', 'hammer']),
        (1, ['figshare3.py', 'wellington']),
        (2, ['theses-michoacan3.py']),
        (1, ['aip3YYY.py', 'app', pryear-2015, prmonth]),
        (1, ['theses-bilbao3XXX.py']),
        (1, ['theses-minasgerais3.py']),
        (1, ['theses-cordoba3.py']),
        (1, ['iranjpr3XXX.py']),
        (1, ['theses-openaire3.py']),
        (1, ['theses-delft3.py']),
        (1, ['theses-saarland3.py']),
        (2, ['theses-italy3XXX.py', 'padua']),
        (2, ['theses-italy3XXX.py', 'messina']),
        (2, ['theses-stavanger3.py']),
        (2, ['theses-riograndedonorte3.py']),
        (1, ['theses-ulm3.py']),
        (2, ['theses-italy3XXX.py', 'aquila']),
        (1, ['theses-italy3XXX.py', 'florence']),
        (2, ['theses-juizdefora3.py']),
        (1, ['theses-msu3.py']),
        (2, ['theses-qucosa3XXX.py', 'chemnitz']),
        (2, ['theses-qucosa3XXX.py', 'leipzig']),
        (2, ['theses-elpaso3.py']),
        (1, ['theses-msu3.py']),
        (2, ['siam3XXX.py', 'sjmaah', pryear-1968, prsixth]),
        (2, ['siam3XXX.py', 'sjoce3', pryear-1978, prsixth]),
        (2, ['degruyterjournals3.py', 'form', pryear, pryear-1988, prsixth]),
        (3, ['degruyterjournals3.py', 'jnet', pryear, pryear-1975, prquarter]),
        (3, ['siam3XXX.py', 'siread', pryear-1958, prquarter]),
        (2, ['siam3XXX.py', 'smjcat', pryear-1971, prsixth]),
        (1, ['rinton3.py', 'qic']),
        (2, ['siam3XXX.py', 'smjmap', pryear-1940, prsixth]),
        (3, ['aip3YYY.py', 'apr', pryear-2013, prquarter]),
        (3, ['siam3XXX.py', 'sjmael', pryear-1979, prquarter]),
        (2, ['siam3XXX.py', 'sjnaam', pryear-1962, prsixth]),
        (2, ['degruyterjournals3.py', 'ms', pryear, pryear-1950, prsixth]),
        (3, ['sciendo3.py', 'nuka', pryear-1955, prquarter]),
        (3, ['siam3XXX.py', 'sjdmec', pryear-1986, prquarter]),
        (2, ['princetonbooks3XXX.py']),
        (3, ['siam3XXX.py', 'sjaabq', pryear-2016, prquarter]),
        (2, ['muse3.py', '5']),
        (3, ['osa3XXX.py', 'aop', pryear-2008, prquarter]),
        (1, ['rsc3XXX.py', 'cp', pryear-1998, prmonth*4]),
        (1, ['rsc3XXX.py', 'cp', pryear-1998, prmonth*4-1]),
        (1, ['rsc3XXX.py', 'cp', pryear-1998, prmonth*4-2]),
        (1, ['rsc3XXX.py', 'cp', pryear-1998, prmonth*4-3]),
        (3, ['aip3YYY.py', 'aml', pryear-2022, prquarter]),
        (3, ['theses-embryriddle3.py']),
        (1, ['theses-bremen3.py']),
        (2, ['aip3YYY.py', 'mre', pryear-2015, prsixth]),
        #
        (1, ['theses-tokyo3.py']),
        (1, ['theses-cds3.py'])]


if prmonth == 12:
    jnls.append((1, ['aip3YYY.py', 'apl', 2*pryear - 3924 + 1, 25]))
    jnls.append((1, ['aip3YYY.py', 'apl', 2*pryear - 3924 + 1, 26]))
    jnls.append((1, ['osa3XXX.py', 'oe', pryear-1992, prmonth * 2 + 1]))
    jnls.append((1, ['osa3XXX.py', 'oe', pryear-1992, prmonth * 2 + 2]))
    jnls.append((111, ['procnas3.py', pryear-1903, '49,50']))
    jnls.append((111, ['procnas3.py', pryear-1903, '51,52']))
    jnls.append((1, ['intlpress3.py', 'cms', pryear-2002, '7']))
    jnls.append((1, ['intlpress3.py', 'cms', pryear-2002, '8']))
if prmonth == 6:
    jnls.append((1, ['aip3XXX.py', 'apl', 2*pryear - 3924, 25]))
    jnls.append((1, ['aip3XXX.py', 'apl', 2*pryear - 3924, 26]))


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

#do Springer each day
listofcommands.append(['springer3.py', '-sftp'])
prfil.write(' - springer3.py\n')

#do always WSP or IOP or HINDWAI
if (today.day % 3 == 0):
    listofcommands.append(['wsp3XXX.py'])
    prfil.write(' - wsp3.py\n')
elif (today.day % 3 == 1):
    listofcommands.append(['ieee_wrapper3XXX.py'])
    prfil.write(' - ieee_wrapper3XXX.py\n')
elif (today.day % 3 == 2):
    listofcommands.append(['hindawi3.py', '-ftp'])
    prfil.write(' - hindawi3.py\n')
#harvest PubDB each week
if (today.weekday() == 0):
    listofcommands.append(['pubdbweb3.py'])
    prfil.write(' - pubdbweb3.py\n')
#IOP books still old workflow, do IOP journals 6 times per week
if (today.day % 7 == 0):
    listofcommands.append(['iopbooks3XXX.py'])
    prfil.write(' - iopbooks3.py\n')
else:
    listofcommands.append(['iop3.py'])
    prfil.write(' - iop3.py\n')

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
refin = re.compile('FINISHED writenewXML\((.*);(.*);(.*)\)')
shortreport = ''
for com in listofcommands:
    writtenfiles = []
    print(com)
    time.sleep(10)

    if re.search('(XXX|YYY)\.py', com[0]):
        #code that has to run on laptop
        kommando = re.sub('(XXX|YYY)', '', com[0]) + ' ' + ' '.join([str(c) for c in com[1:]])        
        #detailed log
        logfil = open(logfile, "a")
        logfil.write('========={ %s }=========\n  has to run on laptop\n\n' % (' '.join([str(c) for c in com])))
        logfil.close()
        #summary to bes        
        shortreport += '\n-@l00schwenn: nice -10 ~/Envs/inspire3-python3.8/bin/python %s/%s\n\n' % (lproc['python3'], kommando)
        prfil = open(protocol, "a")
        prfil.write('  {could not do} ' + kommando + '\n')
        prfil.close()
    else:
        #code that can run at DESY
        if re.search('3\.py', com[0]):
            commando = [python['python3'], os.path.join(lproc['python3'], com[0])] + [str(c) for c in com[1:]]
        else:
            commando = [python['python2'], os.path.join(lproc['python2'], com[0])] + [str(c) for c in com[1:]]
        harvest = subprocess.Popen(commando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        result, errors = harvest.communicate()
        errors = re.sub('No handlers could be found for logger .?rdflib.term.?\n', '', errors)
        errors = re.sub('cat: ..afs.*?: No such file or directory\n', '', errors)
        errors = re.sub('\/afs.*?\d+: UserWarning: No parser was explicitly specified.*?\n\n.*to the BeautifulSoup constructor.\n\n.*?\n', '    [kein expliziter Parser fuer BeautifulSoup angegeben]\n', errors)
        errors = re.sub('\/home\/library\/.virtualenvs\/inspire\/lib\/python2.7\/site-packages\/selenium\/webdriver\/phantomjs\/webdriver.py:49: UserWarning: Selenium support for PhantomJS has been deprecated, please use headless versions of Chrome or Firefox instead\n *warnings.warn..Selenium support for PhantomJS has been deprecated, please use headless *.', '    [PhantomJS ist veraltet]', errors)
        errors = re.sub('\/home\/library\/.virtualenvs\/inspire\/lib\/python2.7\/site-packages\/paramiko\/transport.py.*elease. *\n *from cryptography.hazmat.backends import default_backend', '    [Cryptography ist veraltet]', errors)
        errors = re.sub('It looks like you.re parsing an XML document using an HTML parser. If this really is an HTML document', '', errors)
        errors = re.sub('.*GuessedAtParserWarning: No parser was explicitly specified.*', '    [kein expliziter Parser fuer BeautifulSoup angegeben]\n', errors)
        errors = re.sub('.*To get rid of this warning, pass the additional argument .features=lxml. to the BeautifulSoup constructor.*', '    [kein expliziter Parser fuer BeautifulSoup angegeben]\n', errors)
        errors = re.sub('.*you can ignore or filter this warning. If it.s XML, you should know that using an XML parser.*', '', errors)
        errors = re.sub('^warnings.warn\($', '', errors.strip())
        #detailed log
        logfil = open(logfile, "a")
        logfil.write('========={ %s }=========\n' % (' '.join([str(c) for c in com])))
        logfil.write(result)
        for line in re.split('\n', result):
            if refin.search(line):
                writtenfiles.append(refin.sub(r'   \1.xml (\2 records)\n   [records with datafields: \3]\n\n', line))
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

print('====================')
print(shortreport)
print('====================')

os.system('echo "%s" | mail -s "ejlwrapper3 finished"  florian.schwennsen@desy.de ' % (re.sub('"', "'", shortreport)))

os.system('echo "ejlwrapper3 finished" >> '+logfile)
prfil = open(protocol, "a")
prfil.write(' ejlwrapper3.py has executed ALL commands.\n')
prfil.write("---------------------------------------------------------------------\n")
prfil.close()
