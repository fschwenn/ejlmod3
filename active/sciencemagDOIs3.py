 # -*- coding: UTF-8 -*-
#program to harvest DOIs from Science
# FS 2023-12-08

import sys
import os
import ejlmod3
import re
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import random
import cloudscraper

publisher = 'American Association for the Advancement of Science'
skipalreadyharvested = True
bunchsize = 10

jnlfilename = 'AAAS_QIS_retro.' + ejlmod3.stampoftoday() + '_2'
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium-browser'
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
    
#scraper = cloudscraper.create_scraper()


sample = {'10.1126/science.273.5278.1073' : {'all' : 486, 'core' : 397},
          '10.1126/science.aam9288' : {'all' : 423, 'core' : 296},
          '10.1126/science.1113479' : {'all' : 230, 'core' : 208},
          '10.1126/science.1231930' : {'all' : 290, 'core' : 200},
          '10.1126/science.1104149' : {'all' : 369, 'core' : 190},
          '10.1126/science.aaf6725' : {'all' : 396, 'core' : 176},
          '10.1126/science.1057726' : {'all' : 223, 'core' : 175},
          '10.1126/science.aag2302' : {'all' : 398, 'core' : 168},
          '10.1126/science.aau4963' : {'all' : 262, 'core' : 158},
          '10.1126/science.1121541' : {'all' : 164, 'core' : 153},
          '10.1126/science.aan3211' : {'all' : 207, 'core' : 144},
          '10.1126/science.aal3837' : {'all' : 360, 'core' : 135},
          '10.1126/science.1116955' : {'all' : 207, 'core' : 118},
          '10.1126/science.abg1919' : {'all' : 154, 'core' : 104},
          '10.1126/science.aah3752' : {'all' : 211, 'core' : 104},
          '10.1126/science.aax9743' : {'all' : 179, 'core' : 103},
          '10.1126/science.1175552' : {'all' : 144, 'core' : 102},
          '10.1126/science.aau0818' : {'all' : 195, 'core' : 96},
          '10.1126/science.aah3778' : {'all' : 203, 'core' : 96},
          '10.1126/science.abg7812' : {'all' : 120, 'core' : 93},
          '10.1126/science.aaa8525' : {'all' : 156, 'core' : 89},
          '10.1126/science.aaa7432' : {'all' : 374, 'core' : 86},
          '10.1126/science.1231298' : {'all' : 114, 'core' : 84},
          '10.1126/science.aao5965' : {'all' : 110, 'core' : 83},
          '10.1126/sciadv.aay5901' : {'all' : 87, 'core' : 79},
          '10.1126/science.1102896' : {'all' : 234, 'core' : 78},
          '10.1126/science.aaa2085' : {'all' : 128, 'core' : 77},
          '10.1126/science.1224953' : {'all' : 254, 'core' : 77},
          '10.1126/science.1236408' : {'all' : 134, 'core' : 75},
          '10.1126/science.aao4309' : {'all' : 97, 'core' : 72},
          '10.1126/science.1253742' : {'all' : 87, 'core' : 72},
          '10.1126/science.aay4354' : {'all' : 113, 'core' : 71},
          '10.1126/science.aar3106' : {'all' : 90, 'core' : 71},
          '10.1126/science.aao1401' : {'all' : 135, 'core' : 70},
          '10.1126/science.aay2645' : {'all' : 116, 'core' : 69},
          '10.1126/science.1243289' : {'all' : 116, 'core' : 69},
          '10.1126/science.aaf8834' : {'all' : 244, 'core' : 68},
          '10.1126/science.aab3642' : {'all' : 119, 'core' : 68},
          '10.1126/science.282.5389.706' : {'all' : 135, 'core' : 68},
          '10.1126/science.1252319' : {'all' : 81, 'core' : 68},
          '10.1126/science.aar7053' : {'all' : 111, 'core' : 65},
          '10.1126/science.aan0070' : {'all' : 82, 'core' : 64},
          '10.1126/sciadv.aao3603' : {'all' : 75, 'core' : 64},
          '10.1126/science.aay0600' : {'all' : 95, 'core' : 63},
          '10.1126/science.1208001' : {'all' : 107, 'core' : 62},
          '10.1126/science.1068774' : {'all' : 79, 'core' : 62},
          '10.1126/science.aad0343' : {'all' : 144, 'core' : 61},
          '10.1126/science.1177838' : {'all' : 114, 'core' : 60},
          '10.1126/science.1133734' : {'all' : 530, 'core' : 58},
          '10.1126/science.aav9105' : {'all' : 168, 'core' : 57},
          '10.1126/science.aad9480' : {'all' : 69, 'core' : 57},
          '10.1126/science.1131563' : {'all' : 64, 'core' : 57},
          '10.1126/science.1203329' : {'all' : 64, 'core' : 56},
          '10.1126/science.1131871' : {'all' : 110, 'core' : 56},
          '10.1126/science.284.5415.779' : {'all' : 67, 'core' : 55},
          '10.1126/science.279.5349.342' : {'all' : 63, 'core' : 55},
          '10.1126/sciadv.aaw9918' : {'all' : 60, 'core' : 55},
          '10.1126/science.1220513' : {'all' : 96, 'core' : 54},
          '10.1126/science.1257026' : {'all' : 172, 'core' : 53},
          '10.1126/sciadv.1701491' : {'all' : 71, 'core' : 52},
          '10.1126/sciadv.1602589' : {'all' : 81, 'core' : 52},
          '10.1126/science.aar7709' : {'all' : 260, 'core' : 51},
          '10.1126/science.aad9958' : {'all' : 131, 'core' : 51},
          '10.1126/science.1142892' : {'all' : 100, 'core' : 50},
          '10.1126/science.abb2823' : {'all' : 72, 'core' : 49},
          '10.1126/science.285.5430.1036' : {'all' : 66, 'core' : 49},
          '10.1126/science.1253512' : {'all' : 71, 'core' : 49},
          '10.1126/science.aat2025' : {'all' : 68, 'core' : 48},
          '10.1126/science.aah6875' : {'all' : 120, 'core' : 48},
          '10.1126/science.1167343' : {'all' : 94, 'core' : 48},
          '10.1126/science.1160627' : {'all' : 112, 'core' : 48},
          '10.1126/science.1139831' : {'all' : 89, 'core' : 48},
          '10.1126/sciadv.1601540' : {'all' : 57, 'core' : 48},
          '10.1126/science.aat3996' : {'all' : 52, 'core' : 47},
          '10.1126/science.1154622' : {'all' : 114, 'core' : 46},
          '10.1126/science.1058835' : {'all' : 71, 'core' : 45},
          '10.1126/sciadv.1500838' : {'all' : 62, 'core' : 45},
          '10.1126/science.aaf2941' : {'all' : 76, 'core' : 44},
          '10.1126/science.aar4054' : {'all' : 78, 'core' : 43},
          '10.1126/science.1217692' : {'all' : 54, 'core' : 43},
          '10.1126/sciadv.aar3960' : {'all' : 67, 'core' : 43},
          '10.1126/science.aad6320' : {'all' : 124, 'core' : 42},
          '10.1126/science.270.5234.255' : {'all' : 66, 'core' : 42},
          '10.1126/science.1192739' : {'all' : 84, 'core' : 42},
          '10.1126/science.1145699' : {'all' : 46, 'core' : 42},
          '10.1126/science.aah4758' : {'all' : 73, 'core' : 41},
          '10.1126/science.aad5007' : {'all' : 112, 'core' : 41},
          '10.1126/science.1122858' : {'all' : 89, 'core' : 41},
          '10.1126/sciadv.aav2761' : {'all' : 47, 'core' : 41},
          '10.1126/science.aaa3693' : {'all' : 99, 'core' : 40},
          '10.1126/science.1227612' : {'all' : 80, 'core' : 40},
          '10.1126/science.1189075' : {'all' : 71, 'core' : 40},
          '10.1126/science.1181918' : {'all' : 77, 'core' : 40},
          '10.1126/science.1138007' : {'all' : 77, 'core' : 40},
          '10.1126/sciadv.aap9646' : {'all' : 46, 'core' : 39},
          '10.1126/science.aaz9236' : {'all' : 80, 'core' : 38},
          '10.1126/science.aaa8415' : {'all' : 56, 'core' : 38},
          '10.1126/science.1127647' : {'all' : 69, 'core' : 38},
          '10.1126/science.1069372' : {'all' : 62, 'core' : 38},
          '10.1126/science.1250147' : {'all' : 86, 'core' : 37},
          '10.1126/science.1232296' : {'all' : 89, 'core' : 37},
          '10.1126/science.1166767' : {'all' : 187, 'core' : 37},
          '10.1126/sciadv.1701074' : {'all' : 41, 'core' : 37},
          '10.1126/science.1244324' : {'all' : 82, 'core' : 36},
          '10.1126/science.1148047' : {'all' : 377, 'core' : 36},
          '10.1126/sciadv.1600694' : {'all' : 48, 'core' : 36},
          '10.1126/science.1231692' : {'all' : 86, 'core' : 35},
          '10.1126/sciadv.aau8342' : {'all' : 51, 'core' : 35},
          '10.1126/science.1229957' : {'all' : 62, 'core' : 34},
          '10.1126/science.1173440' : {'all' : 48, 'core' : 33},
          '10.1126/science.1148092' : {'all' : 67, 'core' : 33},
          '10.1126/science.1078955' : {'all' : 99, 'core' : 33},
          '10.1126/sciadv.aat0346' : {'all' : 299, 'core' : 33},
          '10.1126/science.1141324' : {'all' : 43, 'core' : 32},
          '10.1126/science.1081045' : {'all' : 43, 'core' : 32},
          '10.1126/sciadv.1500707' : {'all' : 43, 'core' : 32},
          '10.1126/sciadv.1500214' : {'all' : 41, 'core' : 32},
          '10.1126/science.aao1511' : {'all' : 70, 'core' : 31},
          '10.1126/science.aaf2581' : {'all' : 46, 'core' : 31},
          '10.1126/science.1188172' : {'all' : 58, 'core' : 31},
          '10.1126/science.1139892' : {'all' : 51, 'core' : 31},
          '10.1126/sciadv.aat9304' : {'all' : 47, 'core' : 31},
          '10.1126/science.aag1635' : {'all' : 96, 'core' : 30},
          '10.1126/science.1114375' : {'all' : 81, 'core' : 30},
          '10.1126/science.aaw8415' : {'all' : 57, 'core' : 29},
          '10.1126/science.aah4243' : {'all' : 58, 'core' : 29},
          '10.1126/science.1257219' : {'all' : 65, 'core' : 29},
          '10.1126/science.1167209' : {'all' : 40, 'core' : 29},
          '10.1126/science.aaz8727' : {'all' : 165, 'core' : 28},
          '10.1126/science.aah6442' : {'all' : 326, 'core' : 28},
          '10.1126/science.aaa8515' : {'all' : 166, 'core' : 28},
          '10.1126/science.1231440' : {'all' : 66, 'core' : 28},
          '10.1126/science.1198804' : {'all' : 84, 'core' : 28},
          '10.1126/science.1193515' : {'all' : 65, 'core' : 28},
          '10.1126/science.1155441' : {'all' : 51, 'core' : 28},
          '10.1126/science.1130886' : {'all' : 33, 'core' : 28},
          '10.1126/sciadv.abc8268' : {'all' : 64, 'core' : 28},
          '10.1126/science.1261033' : {'all' : 53, 'core' : 27},
          '10.1126/science.1157233' : {'all' : 50, 'core' : 27},
          '10.1126/sciadv.aba4935' : {'all' : 51, 'core' : 27},
          '10.1126/sciadv.1603150' : {'all' : 63, 'core' : 27},
          '10.1126/science.abc7776' : {'all' : 53, 'core' : 26},
          '10.1126/science.aah5844' : {'all' : 28, 'core' : 26},
          '10.1126/science.aaa4170' : {'all' : 33, 'core' : 26},
          '10.1126/science.276.5321.2012' : {'all' : 84, 'core' : 26},
          '10.1126/science.1152697' : {'all' : 96, 'core' : 26},
          '10.1126/science.1090790' : {'all' : 36, 'core' : 26},
          '10.1126/science.aax1265' : {'all' : 63, 'core' : 25},
          '10.1126/science.aam5532' : {'all' : 61, 'core' : 25},
          '10.1126/science.aal2469' : {'all' : 60, 'core' : 25},
          '10.1126/science.1149858' : {'all' : 48, 'core' : 25},
          '10.1126/science.1148259' : {'all' : 56, 'core' : 25},
          '10.1126/science.1119678' : {'all' : 44, 'core' : 25},
          '10.1126/sciadv.aat9004' : {'all' : 28, 'core' : 25},
          '10.1126/sciadv.1700672' : {'all' : 59, 'core' : 25},
          '10.1126/sciadv.1501286' : {'all' : 91, 'core' : 25},
          '10.1126/science.aah5178' : {'all' : 50, 'core' : 24},
          '10.1126/science.aag1430' : {'all' : 79, 'core' : 24},
          '10.1126/science.1231675' : {'all' : 60, 'core' : 24},
          '10.1126/science.1226897' : {'all' : 42, 'core' : 24},
          '10.1126/science.1162242' : {'all' : 35, 'core' : 24},
          '10.1126/science.1103190' : {'all' : 65, 'core' : 24},
          '10.1126/science.1100700' : {'all' : 112, 'core' : 24},
          '10.1126/sciadv.aaz3666' : {'all' : 42, 'core' : 24},
          '10.1126/sciadv.aay4929' : {'all' : 28, 'core' : 24},
          '10.1126/sciadv.aat9459' : {'all' : 24, 'core' : 24},
          '10.1126/science.aag3349' : {'all' : 78, 'core' : 23},
          '10.1126/science.290.5491.498' : {'all' : 37, 'core' : 23},
          '10.1126/science.272.5265.1131' : {'all' : 41, 'core' : 23},
          '10.1126/science.1260364' : {'all' : 69, 'core' : 23},
          '10.1126/science.aay0644' : {'all' : 51, 'core' : 22},
          '10.1126/science.aan5959' : {'all' : 36, 'core' : 22},
          '10.1126/science.aam7009' : {'all' : 48, 'core' : 22},
          '10.1126/science.aaf5134' : {'all' : 68, 'core' : 22},
          '10.1126/science.aad8022' : {'all' : 64, 'core' : 22},
          '10.1126/science.1258480' : {'all' : 155, 'core' : 22},
          '10.1126/science.1258479' : {'all' : 171, 'core' : 22},
          '10.1126/science.1214987' : {'all' : 113, 'core' : 22},
          '10.1126/science.1070958' : {'all' : 31, 'core' : 22},
          '10.1126/science.aar6404' : {'all' : 30, 'core' : 21},
          '10.1126/science.aad8665' : {'all' : 46, 'core' : 21},
          '10.1126/science.1244563' : {'all' : 96, 'core' : 21},
          '10.1126/science.1195596' : {'all' : 104, 'core' : 21},
          '10.1126/science.1176496' : {'all' : 38, 'core' : 21},
          '10.1126/science.1174436' : {'all' : 65, 'core' : 21},
          '10.1126/sciadv.abb0451' : {'all' : 56, 'core' : 21},
          '10.1126/science.aaz6801' : {'all' : 36, 'core' : 20},
          '10.1126/science.aad8532' : {'all' : 43, 'core' : 20},
          '10.1126/science.aaa2253' : {'all' : 39, 'core' : 20},
          '10.1126/science.1231540' : {'all' : 57, 'core' : 20},
          '10.1126/science.1231473' : {'all' : 60, 'core' : 20},
          '10.1126/science.1208798' : {'all' : 64, 'core' : 20},
          '10.1126/science.1192368' : {'all' : 83, 'core' : 20},
          '10.1126/science.1173731' : {'all' : 27, 'core' : 20},
          '10.1126/science.1091277' : {'all' : 35, 'core' : 20},
          '10.1126/sciadv.abe0395' : {'all' : 29, 'core' : 20},
          '10.1126/science.abf2998' : {'all' : 69, 'core' : 19},
          '10.1126/science.aaw2884' : {'all' : 45, 'core' : 19},
          '10.1126/science.aam7127' : {'all' : 72, 'core' : 19},
          '10.1126/science.1237125' : {'all' : 57, 'core' : 19},
          '10.1126/science.1226487' : {'all' : 24, 'core' : 19},
          '10.1126/sciadv.abc5055' : {'all' : 27, 'core' : 19},
          '10.1126/science.abc7312' : {'all' : 52, 'core' : 18},
          '10.1126/science.aac9812' : {'all' : 81, 'core' : 18},
          '10.1126/science.1259052' : {'all' : 68, 'core' : 18},
          '10.1126/science.1258676' : {'all' : 101, 'core' : 18},
          '10.1126/science.1208517' : {'all' : 23, 'core' : 18},
          '10.1126/science.1181193' : {'all' : 33, 'core' : 18},
          '10.1126/science.1177077' : {'all' : 27, 'core' : 18},
          '10.1126/sciadv.aay3050' : {'all' : 20, 'core' : 18},
          '10.1126/sciadv.aaw0297' : {'all' : 60, 'core' : 18},
          '10.1126/sciadv.aas9401' : {'all' : 28, 'core' : 18},
          '10.1126/sciadv.1501531' : {'all' : 22, 'core' : 18},
          '10.1126/science.aaw4352' : {'all' : 38, 'core' : 17},
          '10.1126/science.aav6926' : {'all' : 43, 'core' : 17},
          '10.1126/science.aao2254' : {'all' : 56, 'core' : 17},
          '10.1126/science.aao1850' : {'all' : 59, 'core' : 17},
          '10.1126/science.aaj2118' : {'all' : 48, 'core' : 17},
          '10.1126/science.290.5492.773' : {'all' : 32, 'core' : 17},
          '10.1126/science.280.5367.1238' : {'all' : 35, 'core' : 17},
          '10.1126/science.275.5298.350' : {'all' : 32, 'core' : 17},
          '10.1126/science.1258004' : {'all' : 108, 'core' : 17},
          '10.1126/science.1236362' : {'all' : 50, 'core' : 17},
          '10.1126/science.1225258' : {'all' : 35, 'core' : 17},
          '10.1126/science.1209524' : {'all' : 24, 'core' : 17},
          '10.1126/sciadv.aax1950' : {'all' : 31, 'core' : 17},
          '10.1126/sciadv.aaw8586' : {'all' : 34, 'core' : 17},
          '10.1126/sciadv.1602811' : {'all' : 21, 'core' : 17},
          '10.1126/science.abe2824' : {'all' : 23, 'core' : 16},
          '10.1126/science.abc7821' : {'all' : 31, 'core' : 16},
          '10.1126/science.aay5820' : {'all' : 20, 'core' : 16},
          '10.1126/science.aat4134' : {'all' : 66, 'core' : 16},
          '10.1126/science.aar4005' : {'all' : 120, 'core' : 16},
          '10.1126/science.aaq0327' : {'all' : 53, 'core' : 16},
          '10.1126/science.aam8697' : {'all' : 38, 'core' : 16},
          '10.1126/science.aaa3786' : {'all' : 32, 'core' : 16},
          '10.1126/science.aaa0754' : {'all' : 32, 'core' : 16},
          '10.1126/science.1258351' : {'all' : 49, 'core' : 16},
          '10.1126/science.1247715' : {'all' : 35, 'core' : 16},
          '10.1126/science.1242072' : {'all' : 20, 'core' : 16},
          '10.1126/science.1189164' : {'all' : 52, 'core' : 16},
          '10.1126/science.1146204' : {'all' : 40, 'core' : 16},
          '10.1126/science.aay0668' : {'all' : 135, 'core' : 15},
          '10.1126/science.aaw2906' : {'all' : 33, 'core' : 15},
          '10.1126/science.aao0290' : {'all' : 32, 'core' : 15},
          '10.1126/science.aag1106' : {'all' : 50, 'core' : 15},
          '10.1126/science.1257671' : {'all' : 50, 'core' : 15},
          '10.1126/science.1163861' : {'all' : 82, 'core' : 15},
          '10.1126/science.1155400' : {'all' : 32, 'core' : 15},
          '10.1126/science.1155309' : {'all' : 61, 'core' : 15},
          '10.1126/science.1150841' : {'all' : 60, 'core' : 15},
          '10.1126/science.1140300' : {'all' : 26, 'core' : 15},
          '10.1126/sciadv.aaw6664' : {'all' : 28, 'core' : 15},
          '10.1126/sciadv.aaw4530' : {'all' : 21, 'core' : 15},
          '10.1126/sciadv.aau5999' : {'all' : 31, 'core' : 15},
          '10.1126/sciadv.aau0823' : {'all' : 29, 'core' : 15},
          '10.1126/science.aau4691' : {'all' : 44, 'core' : 14},
          '10.1126/science.aat4625' : {'all' : 23, 'core' : 14},
          '10.1126/science.aap9859' : {'all' : 128, 'core' : 14},
          '10.1126/science.aaa4298' : {'all' : 30, 'core' : 14},
          '10.1126/science.1249802' : {'all' : 17, 'core' : 14},
          '10.1126/science.1207239' : {'all' : 83, 'core' : 14},
          '10.1126/science.1190545' : {'all' : 33, 'core' : 14},
          '10.1126/science.1183628' : {'all' : 26, 'core' : 14},
          '10.1126/science.1143835' : {'all' : 27, 'core' : 14},
          '10.1126/sciadv.aaz4888' : {'all' : 35, 'core' : 14},
          '10.1126/sciadv.aav2372' : {'all' : 30, 'core' : 14},
          '10.1126/sciadv.aat3174' : {'all' : 35, 'core' : 14},
          '10.1126/sciadv.aar4994' : {'all' : 35, 'core' : 14},
          '10.1126/sciadv.1500022' : {'all' : 19, 'core' : 14},
          '10.1126/science.aax9406' : {'all' : 35, 'core' : 13},
          '10.1126/science.aan7939' : {'all' : 48, 'core' : 13},
          '10.1126/science.aam8990' : {'all' : 50, 'core' : 13},
          '10.1126/science.aak9611' : {'all' : 37, 'core' : 13},
          '10.1126/science.1242308' : {'all' : 55, 'core' : 13},
          '10.1126/science.1240516' : {'all' : 44, 'core' : 13},
          '10.1126/science.1211914' : {'all' : 38, 'core' : 13},
          '10.1126/science.1201351' : {'all' : 54, 'core' : 13},
          '10.1126/science.1134008' : {'all' : 19, 'core' : 13},
          '10.1126/sciadv.abf2447' : {'all' : 17, 'core' : 13},
          '10.1126/sciadv.abc3847' : {'all' : 32, 'core' : 13},
          '10.1126/sciadv.aba4508' : {'all' : 18, 'core' : 13},
          '10.1126/sciadv.1701513' : {'all' : 60, 'core' : 13},
          '10.1126/sciadv.1602273' : {'all' : 19, 'core' : 13},
          '10.1126/sciadv.1601915' : {'all' : 18, 'core' : 13},
          '10.1126/sciadv.1501165' : {'all' : 24, 'core' : 13},
          '10.1126/science.abf5389' : {'all' : 46, 'core' : 12},
          '10.1126/science.abf0147' : {'all' : 56, 'core' : 12},
          '10.1126/science.aau7742' : {'all' : 51, 'core' : 12},
          '10.1126/science.aau7230' : {'all' : 45, 'core' : 12},
          '10.1126/science.aat3581' : {'all' : 23, 'core' : 12},
          '10.1126/science.aao2035' : {'all' : 45, 'core' : 12},
          '10.1126/science.290.5500.2282' : {'all' : 44, 'core' : 12},
          '10.1126/science.1202218' : {'all' : 60, 'core' : 12},
          '10.1126/science.1095232' : {'all' : 30, 'core' : 12},
          '10.1126/sciadv.abh0952' : {'all' : 24, 'core' : 12},
          '10.1126/sciadv.abg9158' : {'all' : 13, 'core' : 12},
          '10.1126/sciadv.aau1946' : {'all' : 19, 'core' : 12},
          '10.1126/sciadv.aap9416' : {'all' : 36, 'core' : 12},
          '10.1126/sciadv.aao4748' : {'all' : 39, 'core' : 12},
          '10.1126/sciadv.1400255' : {'all' : 30, 'core' : 12},
          '10.1126/science.aat4387' : {'all' : 46, 'core' : 11},
          '10.1126/science.aao5686' : {'all' : 62, 'core' : 11},
          '10.1126/science.1248905' : {'all' : 23, 'core' : 11},
          '10.1126/science.1154643' : {'all' : 17, 'core' : 11},
          '10.1126/science.1093649' : {'all' : 21, 'core' : 11},
          '10.1126/science.1078446' : {'all' : 26, 'core' : 11},
          '10.1126/sciadv.abm5912' : {'all' : 18, 'core' : 11},
          '10.1126/sciadv.abb8780' : {'all' : 17, 'core' : 11},
          '10.1126/sciadv.aba9186' : {'all' : 33, 'core' : 11},
          '10.1126/sciadv.aat9331' : {'all' : 19, 'core' : 11},
          '10.1126/sciadv.1600036' : {'all' : 24, 'core' : 11},
          '10.1126/science.abf0345' : {'all' : 35, 'core' : 10},
          '10.1126/science.abd0336' : {'all' : 66, 'core' : 10},
          '10.1126/science.aay2354' : {'all' : 42, 'core' : 10},
          '10.1126/science.aaw6259' : {'all' : 26, 'core' : 10},
          '10.1126/science.aaw4329' : {'all' : 26, 'core' : 10},
          '10.1126/science.1254699' : {'all' : 48, 'core' : 10},
          '10.1126/sciadv.1700930' : {'all' : 18, 'core' : 10}}





def harvestarticle(jnl, rec, i, l, r):
    sleepingtime = random.randint(30, 150)
    ejlmod3.printprogress('-', [[i, l], [rec['artlink']], ['%isec' % (sleepingtime)], [r]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    except:
        print("retry in 900 seconds")
        time.sleep(900)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    #meta-tags 
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Date'])
    if 'tit' in rec:
        if rec['tit'] in ['In Science Journals']:
            return False
    else:
        print(artpage.text)
    #volume, issue
    for span in artpage.find_all('span', attrs = {'property' : 'volumeNumber'}):
        rec['vol'] = span.text.strip()
    for span in artpage.find_all('span', attrs = {'property' : 'issueNumber'}):
        rec['issue'] = span.text.strip()
    #pages
    for meta in artpage.find_all('meta', attrs = {'name' : 'dc.Identifier'}):
        if meta.has_attr('scheme'):
            if meta['scheme'] == 'publisher-id':
                rec['p1'] = meta['content']
            elif meta['scheme'] == 'doi':
                rec['doi'] = meta['content']
    #authors and affiliations
    for div in artpage.find_all('div', attrs = {'property' : 'author'}):
        name = False
        for span in div.find_all('span', attrs = {'property' : 'familyName'}):
            name = span.text.strip()
        for span in div.find_all('span', attrs = {'property' : 'givenName'}):
            name += ', ' + span.text.strip()
        if name:
            rec['autaff'].append([name])
            for a in div.find_all('a', attrs = {'class' : 'orcid-id'}):
                rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            for div2 in div.find_all('div', attrs = {'property' : ['affiliation', 'organization']}):
                rec['autaff'][-1].append(div2.text.strip())
        else:
            rec['autaff'].append([re.sub('View all articles by this author', '', div.text.strip())])
            print('\n  added "%s" as author - is it ok or a collaboration or ...?\n' % (rec['autaff'][-1][0]))
    #abstract
    for section in artpage.find_all('section', attrs = {'id' : 'abstract'}):
        for h2 in section.find_all('h2'):
            h2.decompose()
        rec['abs'] = section.text.strip()
    #strange page
    if not 'p1' in list(rec.keys()):
        rec['p1'] = re.sub('.*\.', '', rec['doi'])
    #references
    divs = artpage.find_all('div', attrs = {'class' : 'labeled'})
    if not len(divs):
         divs = artpage.find_all('div', attrs = {'role' : 'doc-biblioentry'})
    if not len(divs):
        for section in artpage.find_all('section', attrs = {'id'  : 'bibliography'}):
            divs = section.find_all('div', attrs = {'role' : 'listitem'})
    for div in divs:
        for d2 in div.find_all('div', attrs = {'class' : 'label'}):
            d2t = d2.text
            d2.replace_with('[%s] ' % d2t)
        for a in div.find_all('a'):
            if a.has_attr('href'):
                at = a.text.strip()
                ah = a['href']
                if at == 'Crossref':
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', ah))
                else:
                    a.decompose()
        rec['refs'].append([('x', div.text.strip())])
    #PDF    
    for a in artpage.find_all('a', attrs = {'data-toggle' : 'tooltip'}):
        if a.has_attr('href') and re.search('doi\/pdf', a['href']):
            if jnl == 'research':
                rec['pdf_url'] = 'https://spj.science.org' + a['href']
            else:
                rec['pdf_url'] = 'https://science.org' + a['href']
    ejlmod3.globallicensesearch(rec, artpage)
    time.sleep(sleepingtime)
    return True


i = 0
recs = []
missingjournals = []
for doi in sample:
    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < 20:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    if re.search('10.1126\/science\.', doi):
        jnlname = 'Science'
        jnl = 'science'
    elif re.search('10.1126\/sciadv', doi):
        jnlname = 'Sci.Adv.'
        jnl = 'sciadv'
    else:
        missingjournals.append(meta['content'])
        continue

    rec = {'tc' : 'P', 'jnl' : jnlname, 'autaff' : [], 'note' : [],
           'refs' : [], 'doi' : doi}
    rec['artlink'] = 'https://doi.org/' + doi
    rec['artlink'] = 'https://www.science.org/doi/' + doi
    #check article pages
    if harvestarticle(jnl, rec, i, len(sample), len(recs)):
        #sample note
        rec['note'] = ['reharvest_based_on_refanalysis',
                       '%i citations from INSPIRE papers' % (sample[doi]['all']),
                       '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
        if missingjournals:
            print('\nmissing journals:', missingjournals, '\n')

