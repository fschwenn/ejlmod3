# -*- coding: utf-8 -*-
#program to harvest individual DOIs from AIP-journals
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
import json
regexpref = re.compile('[\n\r\t]')

publisher = 'AIP'
typecode = 'P'
skipalreadyharvested = False
corethreshold = 15
bunchsize = 10

jnlfilename = 'AIP_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1063/1.461951' : {'all' : 27 , 'core' : 27},
          '10.1063/1.478295' : {'all' : 23 , 'core' : 23},
          '10.1063/1.4802893' : {'all' : 10 , 'core' : 10},
          '10.1063/1.4899186' : {'all' : 43 , 'core' : 43},
          '10.1063/1.4901039' : {'all' : 22 , 'core' : 22},
          '10.1063/1.4984299' : {'all' : 12 , 'core' : 12},
          '10.1063/1.5048097' : {'all' : 11 , 'core' : 11},
          '10.1063/5.0023103' : {'all' : 19 , 'core' : 19},
          '10.1063/5.0050173' : {'all' : 11 , 'core' : 11},
          '10.1063/1.3517252' : {'all' : 23 , 'core' : 23},
          '10.1063/1.446862' : {'all' : 36 , 'core' : 36},
          '10.1063/1.454125' : {'all' : 11 , 'core' : 11},
          '10.1063/1.4937922' : {'all' : 29 , 'core' : 29},
          '10.1063/1.5016931' : {'all' : 12 , 'core' : 12},
          '10.1063/1.5031034' : {'all' : 20 , 'core' : 20},
          '10.1063/1.525607' : {'all' : 22 , 'core' : 22},
          '10.1063/5.0026141' : {'all' : 11 , 'core' : 11},
          '10.1063/5.0036520' : {'all' : 15 , 'core' : 15},
          '10.1063/5.0039772' : {'all' : 25 , 'core' : 25},
          '10.1063/1.4768229' : {'all' : 139 , 'core' : 139},
          '10.1063/1.1498491' : {'all' : 19 , 'core' : 19},
          '10.1063/1.1703941' : {'all' : 22 , 'core' : 22},
          '10.1063/1.2953685' : {'all' : 18 , 'core' : 18},
          '10.1063/1.2992152' : {'all' : 29 , 'core' : 29},
          '10.1063/1.3224703' : {'all' : 23 , 'core' : 23},
          '10.1063/1.451548' : {'all' : 30 , 'core' : 30},
          '10.1063/1.478522' : {'all' : 31 , 'core' : 31},
          '10.1063/1.4901162' : {'all' : 14 , 'core' : 14},
          '10.1063/1.522875' : {'all' : 26 , 'core' : 26},
          '10.1063/1.98041' : {'all' : 20 , 'core' : 20},
          '10.1063/5.0003907' : {'all' : 16 , 'core' : 16},
          '10.1063/5.0016463' : {'all' : 17 , 'core' : 17},
          '10.1063/5.0023533' : {'all' : 14 , 'core' : 14},
          '10.1063/1.1889444' : {'all' : 22 , 'core' : 22},
          '10.1063/1.2943282' : {'all' : 34 , 'core' : 34},
          '10.1063/1.3273372' : {'all' : 18 , 'core' : 18},
          '10.1063/1.3598471' : {'all' : 16 , 'core' : 16},
          '10.1063/1.443164' : {'all' : 30 , 'core' : 30},
          '10.1063/1.464746' : {'all' : 29 , 'core' : 29},
          '10.1063/1.469508' : {'all' : 43 , 'core' : 43},
          '10.1063/1.4954700' : {'all' : 18 , 'core' : 18},
          '10.1063/1.5014033' : {'all' : 14 , 'core' : 14},
          '10.1063/1.5020038' : {'all' : 41 , 'core' : 41},
          '10.1063/1.5026238' : {'all' : 40 , 'core' : 40},
          '10.1063/1.5129672' : {'all' : 26 , 'core' : 26},
          '10.1063/5.0003320' : {'all' : 30 , 'core' : 30},
          '10.1063/5.0004844' : {'all' : 40 , 'core' : 40},
          '10.1063/5.0004873' : {'all' : 33 , 'core' : 33},
          '10.1063/5.0038838' : {'all' : 18 , 'core' : 18},
          '10.1063/5.0045990' : {'all' : 30 , 'core' : 30},
          '10.1063/1.1498000' : {'all' : 21 , 'core' : 21},
          '10.1063/1.2898887' : {'all' : 23 , 'core' : 23},
          '10.1063/1.4764940' : {'all' : 17 , 'core' : 17},
          '10.1063/1.4886408' : {'all' : 30 , 'core' : 30},
          '10.1063/5.0029536' : {'all' : 14 , 'core' : 14},
          '10.1063/1.1518555' : {'all' : 22 , 'core' : 22},
          '10.1063/1.2348775' : {'all' : 16 , 'core' : 16},
          '10.1063/1.3223548' : {'all' : 43 , 'core' : 43},
          '10.1063/1.3374022' : {'all' : 24 , 'core' : 24},
          '10.1063/1.469509' : {'all' : 36 , 'core' : 36},
          '10.1063/1.4959241' : {'all' : 17 , 'core' : 17},
          '10.1063/1.5142437' : {'all' : 24 , 'core' : 24},
          '10.1063/1.523789' : {'all' : 51 , 'core' : 51},
          '10.1063/5.0002013' : {'all' : 23 , 'core' : 23},
          '10.1063/5.0006002' : {'all' : 20 , 'core' : 20},
          '10.1063/5.0020014' : {'all' : 22 , 'core' : 22},
          '10.1063/5.0021468' : {'all' : 18 , 'core' : 18},
          '10.1063/5.0053378' : {'all' : 22 , 'core' : 22},
          '10.1063/1.1494474' : {'all' : 24 , 'core' : 24},
          '10.1063/1.1664623' : {'all' : 38 , 'core' : 38},
          '10.1063/1.2906373' : {'all' : 40 , 'core' : 40},
          '10.1063/1.3194778' : {'all' : 19 , 'core' : 19},
          '10.1063/1.3520564' : {'all' : 21 , 'core' : 21},
          '10.1063/1.4748280' : {'all' : 33 , 'core' : 33},
          '10.1063/1.4773316' : {'all' : 23 , 'core' : 23},
          '10.1063/1.4936880' : {'all' : 33 , 'core' : 33},
          '10.1063/1.4939148' : {'all' : 31 , 'core' : 31},
          '10.1063/1.4983266' : {'all' : 16 , 'core' : 16},
          '10.1063/1.531667' : {'all' : 29 , 'core' : 29},
          '10.1063/5.0006075' : {'all' : 31 , 'core' : 31},
          '10.1063/5.0011599' : {'all' : 61 , 'core' : 61},
          '10.1063/1.1664978' : {'all' : 79 , 'core' : 79},
          '10.1063/1.2929367' : {'all' : 29 , 'core' : 29},
          '10.1063/1.3086114' : {'all' : 22 , 'core' : 22},
          '10.1063/1.3193710' : {'all' : 35 , 'core' : 35},
          '10.1063/1.4891487' : {'all' : 18 , 'core' : 18},
          '10.1063/1.5015954' : {'all' : 18 , 'core' : 18},
          '10.1063/1.5063376' : {'all' : 20 , 'core' : 20},
          '10.1063/1.526000' : {'all' : 41 , 'core' : 41},
          '10.1063/1.1495899' : {'all' : 22 , 'core' : 22},
          '10.1063/1.3490188' : {'all' : 53 , 'core' : 53},
          '10.1063/1.3691827' : {'all' : 36 , 'core' : 36},
          '10.1063/1.5011033' : {'all' : 23 , 'core' : 23},
          '10.1063/1.5027030' : {'all' : 23 , 'core' : 23},
          '10.1063/1.5124967' : {'all' : 22 , 'core' : 22},
          '10.1063/1.5133894' : {'all' : 21 , 'core' : 21},
          '10.1063/5.0004454' : {'all' : 27 , 'core' : 27},
          '10.1063/1.1388868' : {'all' : 68 , 'core' : 68},
          '10.1063/1.1564060' : {'all' : 70 , 'core' : 70},
          '10.1063/1.1704171' : {'all' : 23 , 'core' : 23},
          '10.1063/1.3658630' : {'all' : 26 , 'core' : 26},
          '10.1063/1.3692073' : {'all' : 48 , 'core' : 48},
          '10.1063/1.4893297' : {'all' : 22 , 'core' : 22},
          '10.1063/1.4922348' : {'all' : 33 , 'core' : 33},
          '10.1063/1.5006525' : {'all' : 21 , 'core' : 21},
          '10.1063/1.5046663' : {'all' : 56 , 'core' : 56},
          '10.1063/1.113674' : {'all' : 49 , 'core' : 49},
          '10.1063/1.2794995' : {'all' : 34 , 'core' : 34},
          '10.1063/1.3002335' : {'all' : 55 , 'core' : 55},
          '10.1063/1.3638063' : {'all' : 43 , 'core' : 43},
          '10.1063/1.4922249' : {'all' : 34 , 'core' : 34},
          '10.1063/1.524742' : {'all' : 65 , 'core' : 65},
          '10.1063/5.0021950' : {'all' : 25 , 'core' : 25},
          '10.1063/5.0029735' : {'all' : 26 , 'core' : 26},
          '10.1063/1.1494475' : {'all' : 34 , 'core' : 34},
          '10.1063/1.3552890' : {'all' : 39 , 'core' : 39},
          '10.1063/1.3595693' : {'all' : 40 , 'core' : 40},
          '10.1063/1.367318' : {'all' : 58 , 'core' : 58},
          '10.1063/1.4868107' : {'all' : 31 , 'core' : 31},
          '10.1063/PT.3.4270' : {'all' : 33 , 'core' : 33},
          '10.1063/1.1459754' : {'all' : 38 , 'core' : 38},
          '10.1063/1.1738173' : {'all' : 29 , 'core' : 29},
          '10.1063/1.3236685' : {'all' : 29 , 'core' : 29},
          '10.1063/1.3637047' : {'all' : 27 , 'core' : 27},
          '10.1063/1.442271' : {'all' : 24 , 'core' : 24},
          '10.1063/1.4812323' : {'all' : 48 , 'core' : 48},
          '10.1063/1.881299' : {'all' : 40 , 'core' : 40},
          '10.1063/1.1666343' : {'all' : 33 , 'core' : 33},
          '10.1063/1.1703775' : {'all' : 58 , 'core' : 58},
          '10.1063/1.4863745' : {'all' : 29 , 'core' : 29},
          '10.1063/1.3010859' : {'all' : 52 , 'core' : 52},
          '10.1063/1.4919761' : {'all' : 42 , 'core' : 42},
          '10.1063/1.4993577' : {'all' : 31 , 'core' : 31},
          '10.1063/1.872134' : {'all' : 80 , 'core' : 80},
          '10.1063/1.2773988' : {'all' : 43 , 'core' : 43},
          '10.1063/1.5023340' : {'all' : 29 , 'core' : 29},
          '10.1063/1.89690' : {'all' : 35 , 'core' : 35},
          '10.1063/1.1703863' : {'all' : 81 , 'core' : 81},
          '10.1063/1.1740082' : {'all' : 38 , 'core' : 38},
          '10.1063/5.0056534' : {'all' : 43 , 'core' : 43},
          '10.1063/1.5006888' : {'all' : 35 , 'core' : 35},
          '10.1063/1.5019371' : {'all' : 31 , 'core' : 31},
          '10.1063/1.527734' : {'all' : 32 , 'core' : 32},
          '10.1063/1.1705005' : {'all' : 64 , 'core' : 64},
          '10.1063/1.4838855' : {'all' : 44 , 'core' : 44},
          '10.1063/1.527130' : {'all' : 44 , 'core' : 44},
          '10.1063/PT.3.4164' : {'all' : 41 , 'core' : 41},
          '10.1063/1.1703687' : {'all' : 137 , 'core' : 137},
          '10.1063/1.523763' : {'all' : 51 , 'core' : 51},
          '10.1063/1.526596' : {'all' : 45 , 'core' : 45},
          '10.1063/1.532206' : {'all' : 34 , 'core' : 34},
          '10.1063/1.1643788' : {'all' : 64 , 'core' : 64},
          '10.1063/1.1664470' : {'all' : 38 , 'core' : 38},
          '10.1063/1.2203364' : {'all' : 103 , 'core' : 103},
          '10.1063/1.4813269' : {'all' : 38 , 'core' : 38},
          '10.1063/1.5141835' : {'all' : 34 , 'core' : 34},
          '10.1063/1.1672392' : {'all' : 45 , 'core' : 45},
          '10.1063/1.431635' : {'all' : 35 , 'core' : 35},
          '10.1063/1.5133059' : {'all' : 37 , 'core' : 37},
          '10.1063/1.4807015' : {'all' : 52 , 'core' : 52},
          '10.1063/1.1497700' : {'all' : 60 , 'core' : 60},
          '10.1063/1.3693409' : {'all' : 55 , 'core' : 55},
          '10.1063/5.0017378' : {'all' : 52 , 'core' : 52},
          '10.1063/1.5089550' : {'all' : 469 , 'core' : 469},
          '10.1063/1.4950841' : {'all' : 91 , 'core' : 91},
          '10.1063/1.2126792' : {'all' : 45 , 'core' : 45},
          '10.1063/1.3435463' : {'all' : 45 , 'core' : 45},
          '10.1063/1.2916419' : {'all' : 41 , 'core' : 41},
          '10.1063/1.3610677' : {'all' : 116 , 'core' : 116},
          '10.1063/1.5027484' : {'all' : 46 , 'core' : 46},
          '10.1063/5.0006074' : {'all' : 57 , 'core' : 57},
          '10.1063/1.2155757' : {'all' : 57 , 'core' : 57},
          '10.1063/1.4962732' : {'all' : 56 , 'core' : 56},
          '10.1063/1.5100160' : {'all' : 53 , 'core' : 53},
          '10.1063/1.528839' : {'all' : 47 , 'core' : 47},
          '10.1063/1.4984142' : {'all' : 60 , 'core' : 60},
          '10.1063/1.1716296' : {'all' : 69 , 'core' : 69},
          '10.1063/1.4976737' : {'all' : 65 , 'core' : 65},
          '10.1063/1.1731409' : {'all' : 111 , 'core' : 111},
          '10.1063/1.2995837' : {'all' : 67 , 'core' : 67},
          '10.1063/1.5115323' : {'all' : 138 , 'core' : 138},
          '10.1063/1.2393152' : {'all' : 72 , 'core' : 72},
          '10.1063/1.2798382' : {'all' : 69 , 'core' : 69},
          '10.1063/1.2716992' : {'all' : 71 , 'core' : 71},
          '10.1063/1.2823979' : {'all' : 64 , 'core' : 64},
          '10.1063/1.4838856' : {'all' : 113 , 'core' : 113},
          '10.1063/1.4934486' : {'all' : 70 , 'core' : 70},
          '10.1063/1.1737053' : {'all' : 101 , 'core' : 101},
          '10.1063/1.1703787' : {'all' : 88 , 'core' : 88},
          '10.1063/1.341976' : {'all' : 79 , 'core' : 79},
          '10.1063/1.5115814' : {'all' : 125 , 'core' : 125},
          '10.1063/1.1498001' : {'all' : 84 , 'core' : 84},
          '10.1063/1.5141458' : {'all' : 80 , 'core' : 80},
          '10.1063/1.1665432' : {'all' : 143 , 'core' : 143},
          '10.1063/1.529425' : {'all' : 110 , 'core' : 110},
          '10.1063/1.431689' : {'all' : 114 , 'core' : 114},
          '10.1063/1.4879285' : {'all' : 19 , 'core' : 19},
          '10.1063/1.1674902' : {'all' : 12 , 'core' : 12},
          '10.1063/1.1785151' : {'all' : 12 , 'core' : 12},
          '10.1063/1.446313' : {'all' : 9 , 'core' : 9},
          '10.1063/1.4952418' : {'all' : 20 , 'core' : 20},
          '10.1063/1.5110682' : {'all' : 13 , 'core' : 13},
          '10.1063/1.5140884' : {'all' : 12 , 'core' : 12},
          '10.1063/5.0002595' : {'all' : 11 , 'core' : 11},
          '10.1063/5.0004322' : {'all' : 14 , 'core' : 14},
          '10.1063/5.0005082' : {'all' : 14 , 'core' : 14},
          '10.1063/5.0020277' : {'all' : 26 , 'core' : 26},
          '10.1063/5.0021088' : {'all' : 25 , 'core' : 25},
          '10.1063/5.0021755' : {'all' : 14 , 'core' : 14},
          '10.1063/5.0054822' : {'all' : 9 , 'core' : 9},
          '10.1063/1.3292407' : {'all' : 27 , 'core' : 27},
          '10.1063/1.3131295' : {'all' : 27 , 'core' : 27},
          '10.1063/1.1835238' : {'all' : 166 , 'core' : 166}}
sample = {'10.1063/1.5115814' : {'all' : 163, 'core' : 102},
          '10.1063/1.3610677' : {'all' : 151, 'core' : 59},
          '10.1063/1.4976737' : {'all' : 90, 'core' : 64},
          '10.1063/5.0011599' : {'all' : 84, 'core' : 27},
          '10.1063/5.0006074' : {'all' : 79, 'core' : 54},
          '10.1063/5.0056534' : {'all' : 70, 'core' : 45},
          '10.1063/5.0017378' : {'all' : 69, 'core' : 44},
          '10.1063/1.5046663' : {'all' : 61, 'core' : 21},
          '10.1063/1.5026238' : {'all' : 50, 'core' : 14},
          '10.1063/1.4838835' : {'all' : 49, 'core' : 19},
          '10.1063/5.0010193' : {'all' : 45, 'core' : 17},
          '10.1063/5.0045990' : {'all' : 43, 'core' : 17},
          '10.1063/PT.3.3626' : {'all' : 42, 'core' : 28},
          '10.1063/5.0006075' : {'all' : 41, 'core' : 20},
          '10.1063/1.3273372' : {'all' : 40, 'core' : 27},
          '10.1063/5.0003320' : {'all' : 40, 'core' : 20},
          '10.1063/5.0020277' : {'all' : 38, 'core' : 14},
          '10.1063/5.0029735' : {'all' : 37, 'core' : 28},
          '10.1063/1.5129672' : {'all' : 36, 'core' : 17},
          '10.1063/1.4955408' : {'all' : 34, 'core' : 15},
          '10.1063/1.1150518' : {'all' : 34, 'core' : 15},
          '10.1063/1.1896384' : {'all' : 32, 'core' : 18},
          '10.1063/1.5085002' : {'all' : 32, 'core' : 11},
          '10.1063/1.3194778' : {'all' : 30, 'core' : 23},
          '10.1063/1.1914731' : {'all' : 30, 'core' : 12},
          '10.1063/5.0023103' : {'all' : 29, 'core' : 15},
          '10.1063/1.3309703' : {'all' : 28, 'core' : 16},
          '10.1063/1.4804995' : {'all' : 28, 'core' : 12},
          '10.1063/1.5015954' : {'all' : 27, 'core' : 25},
          '10.1063/1.4959241' : {'all' : 27, 'core' : 23},
          '10.1063/1.4764940' : {'all' : 27, 'core' : 22},
          '10.1063/5.0029536' : {'all' : 26, 'core' : 26},
          '10.1063/1.3598471' : {'all' : 26, 'core' : 20},
          '10.1063/1.1498491' : {'all' : 26, 'core' : 15},
          '10.1063/1.4724105' : {'all' : 26, 'core' : 14},
          '10.1063/1.4974536' : {'all' : 26, 'core' : 13},
          '10.1063/1.2348775' : {'all' : 25, 'core' : 23},
          '10.1063/5.0021468' : {'all' : 25, 'core' : 21},
          '10.1063/1.4955109' : {'all' : 25, 'core' : 17},
          '10.1063/1.1449459' : {'all' : 25, 'core' : 13},
          '10.1063/1.4891487' : {'all' : 24, 'core' : 23},
          '10.1063/5.0016463' : {'all' : 24, 'core' : 18},
          '10.1063/1.4934867' : {'all' : 24, 'core' : 18},
          '10.1063/1.1785151' : {'all' : 24, 'core' : 18},
          '10.1063/1.2953685' : {'all' : 24, 'core' : 16},
          '10.1063/1.3005565' : {'all' : 23, 'core' : 19},
          '10.1063/5.0038838' : {'all' : 23, 'core' : 17},
          '10.1063/5.0006002' : {'all' : 23, 'core' : 17},
          '10.1063/1.454125' : {'all' : 22, 'core' : 21},
          '10.1063/1.4864398' : {'all' : 22, 'core' : 18},
          '10.1063/1.4954700' : {'all' : 22, 'core' : 16},
          '10.1063/1.449344' : {'all' : 21, 'core' : 18},
          '10.1063/1.4729623' : {'all' : 21, 'core' : 16},
          '10.1063/1.3511477' : {'all' : 21, 'core' : 14},
          '10.1063/1.4983266' : {'all' : 20, 'core' : 20},
          '10.1063/1.5094643' : {'all' : 20, 'core' : 16},
          '10.1063/1.4936216' : {'all' : 20, 'core' : 15},
          '10.1063/1.4935541' : {'all' : 20, 'core' : 13},
          '10.1063/1.4882646' : {'all' : 20, 'core' : 12},
          '10.1063/1.5121444' : {'all' : 20, 'core' : 11},
          '10.1063/1.5014033' : {'all' : 19, 'core' : 18},
          '10.1063/5.0021755' : {'all' : 19, 'core' : 13},
          '10.1063/5.0003907' : {'all' : 18, 'core' : 15},
          '10.1063/1.5001920' : {'all' : 18, 'core' : 15},
          '10.1063/1.4901162' : {'all' : 18, 'core' : 15},
          '10.1063/5.0002595' : {'all' : 17, 'core' : 14},
          '10.1063/1.4993937' : {'all' : 17, 'core' : 14},
          '10.1063/1.4966970' : {'all' : 17, 'core' : 12},
          '10.1063/1.5016931' : {'all' : 16, 'core' : 15},
          '10.1063/1.4984299' : {'all' : 16, 'core' : 13},
          '10.1063/1.1674902' : {'all' : 16, 'core' : 13},
          '10.1063/1.5110682' : {'all' : 16, 'core' : 12},
          '10.1063/5.0036520' : {'all' : 16, 'core' : 11},
          '10.1063/5.0026141' : {'all' : 15, 'core' : 15}}
    
    
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

def getarticle(artlink, secs):
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
    rec = {'tc' : typecode, 'keyw' : [],
           'note' : [artlink]}
    emails = {}
    for sec in secs:
        rec['note'].append(sec)
        secu = sec.upper()
        if secu in ['CONTRIBUTED REVIEW ARTICLES', 'REVIEW ARTICLES']:
            rec['tc'] = 'PR'
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
                                        'description', 'citation_title',
                                        'citation_reference', 'citation_volume',
                                        'citation_issue'])
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_journal_title'}):
        jnl = ''
        if meta['content'] in ["The Journal of Chemical Physics"]:
            rec['jnl'] = 'J.Chem.Phys.'
        elif meta['content'] in ['Applied Physics Letters']:
            rec['jnl'] = 'Appl.Phys.Lett.'
        elif meta['content'] in ['AIP Advances']:
            rec['jnl'] = 'AIP Adv.'
        elif meta['content'] in ['Journal of Mathematical Physics']:
            rec['jnl'] = 'J.Math.Phys.'
        elif meta['content'] in ['APL Photonics']:
            rec['jnl'] = 'APL Photon.'
        elif meta['content'] in ['Review of Scientific Instruments']:
            rec['jnl'] = 'Rev.Sci.Instrum.'
        elif meta['content'] in ['Physics of Plasmas']:
            rec['jnl'] = 'Phys.Plasmas'
        elif meta['content'] in ['Applied Physics Reviews']:
            rec['jnl'] = 'Appl.Phys.Rev.'
        elif meta['content'] in ['Physics Today']:
            rec['jnl'] = 'Phys.Today'
            jnl = 'pto'
        elif meta['content'] in ['Journal of Applied Physics']:
            rec['jnl'] = 'J.Appl.Phys.'
        elif meta['content'] in ['APL Materials']:
            rec['jnl'] = 'APL Mater.'
        elif meta['content'] in ['AIP Conference Proceedings']:
            rec['jnl'] = 'AIP Conf.Proc.'
        else:
            if not meta['content'] in missingjournals:
                missingjournals.append(meta['content'])
    if not 'jnl' in rec:
        return False
    #abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'abstract'}):
        rec['abs'] = section.text.strip()
    #license and fulltext
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    else:
        for h1 in artpage.find_all('h1'):
            for ii in h1.find_all('i', attrs = {'class' : ['icon-availability_free',
                                                           'icon-availability_open']}):
                ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    #article ID
    for script in artpage.find_all('script', attrs = {'type' : 'application/ld+json'}):
        scriptt = re.sub('[\n\t]', '', script.contents[0].strip())
        metadata = json.loads(scriptt)
        if 'pageStart' in metadata:
            rec['p1'] = metadata['pageStart']
        if jnl in ['pto']:
            if 'pageEnd' in metadata:
                rec['p2'] = metadata['pageEnd']
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
    if 'autaff' in rec:
        newautaff = []
        for aa in rec['autaff']:
            name = re.sub('(.*), (.*)', r'\2 \1', aa[0])
            if name in orcids and orcids[name]: 
                newautaff.append([aa[0], orcids[name]] + aa[1:])
                #print('   %s -> orcid.org/%s' % (name, orcids[name]))
            else:
                newautaff.append(aa)
        rec['autaff'] = newautaff
                        
    #field code for conferences
    if len(sys.argv) > 5:
        rec['fc'] = sys.argv[5]
    
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'ref-list'}):
        rec['refs'] = []
        for a in div.find_all('a'):
            if a.text in ['Google Scholar', 'Crossref', 'Search ADS', 'PubMed']:
                a.decompose()
        for div2 in div.find_all('div', attrs = {'class' : 'ref-content'}):
            rec['refs'].append([('x', re.sub('[\n\t\r]', ' ', div2.text.strip()))])
    
    ejlmod3.printrecsummary(rec)
    #print('AUTAFF', rec['autaff'])
    time.sleep(random.randint(30,90))    
    return rec
                
i = 0
recs = []
missingjournals = []
for doi in sample:
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    href = 'https://doi.org/' + doi
    rec = getarticle(href, [])
    if rec:
        #sample note
        rec['note'] = ['reharvest_based_on_refanalysis',
                       '%i citations from INSPIRE papers' % (sample[doi]['all']),
                       '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')









