# -*- coding: UTF-8 -*-
#program to crawl Springer
# FS 2017-02-22
# FS 2022-09-26

import os
import ejlmod3
import re
import sys
import unicodedata
import string
import codecs
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

skipalreadyharvested = False
bunchsize = 10
corethreshold = 15
publisher = 'Springer'
jnlfilename = 'SPRINGER_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

sample = {'10.1038/s42254-018-0006-2' : {'all' : 305, 'core' : 108},
          '10.1038/nnano.2013.243' : {'all' : 203, 'core' : 40},
          '10.1038/nmat4811' : {'all' : 179, 'core' : 25},
          '10.1038/s41534-016-0004-0' : {'all' : 163, 'core' : 132},
          '10.1038/s41586-021-03928-y' : {'all' : 149, 'core' : 135},
          '10.1038/s42254-020-0195-3' : {'all' : 144, 'core' : 50},
          '10.1038/s42254-020-0193-5' : {'all' : 140, 'core' : 89},
          '10.1038/s42254-020-0228-y' : {'all' : 134, 'core' : 16},
          '10.1038/s41567-019-0698-y' : {'all' : 119, 'core' : 16},
          '10.1038/s41586-021-03617-w' : {'all' : 117, 'core' : 36},
          '10.1038/s41567-021-01357-2' : {'all' : 114, 'core' : 44},
          '10.1038/s41586-019-1287-z' : {'all' : 106, 'core' : 56},
          '10.1038/s41467-016-0009-6' : {'all' : 101, 'core' : 41},
          '10.1038/lsa.2017.146' : {'all' : 100, 'core' : 52},
          '10.1038/nnano.2013.267' : {'all' : 100, 'core' : 10},
          '10.1038/s41467-020-20314-w' : {'all' : 96, 'core' : 49},
          '10.1038/s41578-021-00306-y' : {'all' : 96, 'core' : 43},
          '10.1038/s41586-020-2463-x' : {'all' : 96, 'core' : 13},
          '10.1038/s41566-021-00828-5' : {'all' : 95, 'core' : 83},
          '10.1038/s42254-021-00283-9' : {'all' : 94, 'core' : 57},
          '10.1038/nature25011' : {'all' : 94, 'core' : 15},
          '10.1038/nature22811' : {'all' : 93, 'core' : 14},
          '10.1038/s41566-019-0453-z' : {'all' : 93, 'core' : 11},
          '10.1038/s41467-017-02088-w' : {'all' : 89, 'core' : 34},
          '10.1038/nnano.2017.101' : {'all' : 89, 'core' : 23},
          '10.1038/nmat4176' : {'all' : 86, 'core' : 18},
          '10.1038/s41467-021-21425-8' : {'all' : 84, 'core' : 34},
          '10.1038/natrevmats.2017.31' : {'all' : 84, 'core' : 13},
          '10.1038/s41467-018-05739-8' : {'all' : 83, 'core' : 30},
          '10.1038/s41467-019-12599-3' : {'all' : 82, 'core' : 12},
          '10.1038/s41467-022-28767-x' : {'all' : 79, 'core' : 70},
          '10.1038/nnano.2015.242' : {'all' : 77, 'core' : 20},
          '10.1038/s41578-020-00262-z' : {'all' : 74, 'core' : 35},
          '10.1038/s41586-018-0674-1' : {'all' : 74, 'core' : 15},
          '10.1038/s41377-021-00634-2' : {'all' : 73, 'core' : 53},
          '10.1038/s41467-020-16863-9' : {'all' : 71, 'core' : 13},
          '10.1038/s41467-018-03434-2' : {'all' : 70, 'core' : 11},
          '10.1038/nmat4144' : {'all' : 69, 'core' : 30},
          '10.1038/nmat5017' : {'all' : 69, 'core' : 10},
          '10.1038/s41598-016-0001-8' : {'all' : 67, 'core' : 24},
          '10.1038/s41586-021-03819-2' : {'all' : 65, 'core' : 45},
          '10.1038/s41598-016-0028-x' : {'all' : 64, 'core' : 29},
          '10.1038/s41567-021-01316-x' : {'all' : 63, 'core' : 20},
          '10.1038/s41377-019-0194-2' : {'all' : 63, 'core' : 20},
          '10.1038/s41567-019-0702-6' : {'all' : 63, 'core' : 18},
          '10.1038/s41567-021-01296-y' : {'all' : 60, 'core' : 47},
          '10.1038/nphys4241' : {'all' : 59, 'core' : 14},
          '10.1038/s41563-020-0619-6' : {'all' : 57, 'core' : 19},
          '10.1038/s41563-020-00840-0' : {'all' : 57, 'core' : 10},
          '10.1038/s41565-018-0200-5' : {'all' : 56, 'core' : 20},
          '10.1038/s41586-021-03528-w' : {'all' : 54, 'core' : 20},
          '10.1038/s41567-021-01232-0' : {'all' : 52, 'core' : 34},
          '10.1038/s41567-017-0020-9' : {'all' : 52, 'core' : 12},
          '10.1038/s41598-019-56847-4' : {'all' : 50, 'core' : 27},
          '10.1038/s41563-020-00802-6' : {'all' : 49, 'core' : 35},
          '10.1038/ncomms15506' : {'all' : 49, 'core' : 15},
          '10.1038/s42254-021-00313-6' : {'all' : 47, 'core' : 39},
          '10.1038/s41377-022-00769-w' : {'all' : 47, 'core' : 35},
          '10.1038/s41566-019-0517-0' : {'all' : 47, 'core' : 12},
          '10.1038/s41566-020-0692-z' : {'all' : 47, 'core' : 11},
          '10.1038/s41586-019-1061-2' : {'all' : 45, 'core' : 14},
          '10.1038/s41567-019-0565-x' : {'all' : 45, 'core' : 14},
          '10.1038/s42005-020-0364-9' : {'all' : 45, 'core' : 11},
          '10.1038/ncomms9655' : {'all' : 44, 'core' : 13},
          '10.1038/s41586-021-03576-2' : {'all' : 43, 'core' : 39},
          '10.1038/s41566-021-00873-0' : {'all' : 43, 'core' : 37},
          '10.1038/s41565-018-0188-x' : {'all' : 43, 'core' : 15},
          '10.1038/s41467-020-15402-w' : {'all' : 42, 'core' : 15},
          '10.1038/s41566-018-0246-9' : {'all' : 42, 'core' : 10},
          '10.1038/s41467-021-24371-7' : {'all' : 41, 'core' : 31},
          '10.1038/nnano.2014.82' : {'all' : 41, 'core' : 10},
          '10.1038/nnano.2015.291' : {'all' : 40, 'core' : 29},
          '10.1038/s41567-018-0191-z' : {'all' : 40, 'core' : 15},
          '10.1038/s41467-017-00810-2' : {'all' : 40, 'core' : 12},
          '10.1038/s41567-019-0782-3' : {'all' : 40, 'core' : 11},
          '10.1038/nnano.2013.169' : {'all' : 40, 'core' : 11},
          '10.1038/s41586-020-2133-z' : {'all' : 40, 'core' : 10},
          '10.1038/s41586-019-1319-8' : {'all' : 38, 'core' : 13},
          '10.1038/nnano.2014.30' : {'all' : 38, 'core' : 13},
          '10.1038/s41567-021-01317-w' : {'all' : 37, 'core' : 12},
          '10.1038/srep33381' : {'all' : 37, 'core' : 10},
          '10.1038/s41567-021-01184-5' : {'all' : 37, 'core' : 10},
          '10.1038/s41567-021-01237-9' : {'all' : 36, 'core' : 24},
          '10.1038/s42005-020-0306-6' : {'all' : 36, 'core' : 14},
          '10.1038/s41598-019-39595-3' : {'all' : 36, 'core' : 11},
          '10.1038/nnano.2012.21' : {'all' : 35, 'core' : 19},
          '10.1038/nnano.2015.282' : {'all' : 35, 'core' : 16},
          '10.1038/s41567-019-0508-6' : {'all' : 35, 'core' : 14},
          '10.1038/s41467-018-06142-z' : {'all' : 34, 'core' : 12},
          '10.1038/s42005-018-0105-5' : {'all' : 33, 'core' : 28},
          '10.1038/s41467-018-06601-7' : {'all' : 33, 'core' : 14},
          '10.1038/nnano.2014.313' : {'all' : 33, 'core' : 12},
          '10.1038/s41534-021-00454-7' : {'all' : 32, 'core' : 23},
          '10.1038/s41563-019-0418-0' : {'all' : 32, 'core' : 13},
          '10.1038/ncomms14538' : {'all' : 32, 'core' : 10},
          '10.1038/s41467-019-13822-x' : {'all' : 31, 'core' : 13},
          '10.1038/s41467-018-06598-z' : {'all' : 30, 'core' : 20},
          '10.1038/s41467-021-25196-0' : {'all' : 29, 'core' : 27},
          '10.1038/s41467-018-03577-2' : {'all' : 29, 'core' : 22},
          '10.1038/s41467-020-17519-4' : {'all' : 29, 'core' : 18},
          '10.1038/s41586-019-1566-8' : {'all' : 29, 'core' : 17},
          '10.1038/s41534-021-00440-z' : {'all' : 29, 'core' : 17},
          '10.1038/nphys3484' : {'all' : 29, 'core' : 14},
          '10.1038/s41598-017-06059-5' : {'all' : 29, 'core' : 13},
          '10.1038/s41563-020-00850-y' : {'all' : 29, 'core' : 12},
          '10.1038/s41467-020-18269-z' : {'all' : 29, 'core' : 12},
          '10.1038/s41566-018-0324-z' : {'all' : 29, 'core' : 10},
          '10.1038/s41467-019-14053-w' : {'all' : 28, 'core' : 22},
          '10.1038/s42005-021-00556-w' : {'all' : 28, 'core' : 19},
          '10.1038/s41467-020-17835-9' : {'all' : 28, 'core' : 17},
          '10.1038/ncomms8706' : {'all' : 28, 'core' : 17},
          '10.1038/s41467-021-24699-0' : {'all' : 28, 'core' : 16},
          '10.1038/s41467-019-09327-2' : {'all' : 28, 'core' : 14},
          '10.1038/s41566-018-0282-5' : {'all' : 28, 'core' : 12},
          '10.1038/s41467-018-08101-0' : {'all' : 28, 'core' : 10},
          '10.1038/s41534-021-00493-0' : {'all' : 27, 'core' : 24},
          '10.1038/s42254-020-0230-4' : {'all' : 27, 'core' : 20},
          '10.1038/s41566-018-0342-x' : {'all' : 27, 'core' : 20},
          '10.1038/s41566-018-0097-4' : {'all' : 27, 'core' : 16},
          '10.1038/s41467-020-17053-3' : {'all' : 27, 'core' : 13},
          '10.1038/s41467-018-07433-1' : {'all' : 27, 'core' : 13},
          '10.1038/s41534-021-00436-9' : {'all' : 27, 'core' : 12},
          '10.1038/s41586-020-2051-0' : {'all' : 27, 'core' : 11},
          '10.1038/s41586-019-1201-8' : {'all' : 27, 'core' : 10},
          '10.1038/s41467-021-25054-z' : {'all' : 27, 'core' : 10},
          '10.1038/s41467-020-18055-x' : {'all' : 27, 'core' : 10},
          '10.1038/s41598-019-46722-7' : {'all' : 26, 'core' : 25},
          '10.1038/s41467-018-04200-0' : {'all' : 26, 'core' : 21},
          '10.1038/s41467-017-01245-5' : {'all' : 26, 'core' : 21},
          '10.1038/s41567-019-0747-6' : {'all' : 26, 'core' : 20},
          '10.1038/s41467-017-02298-2' : {'all' : 26, 'core' : 20},
          '10.1038/s41467-021-22416-5' : {'all' : 26, 'core' : 12},
          '10.1038/s41467-020-18625-z' : {'all' : 26, 'core' : 12},
          '10.1038/s41467-019-08544-z' : {'all' : 26, 'core' : 12},
          '10.1038/s41467-017-00987-6' : {'all' : 26, 'core' : 11},
          '10.1038/ncomms12999' : {'all' : 26, 'core' : 10},
          '10.1038/s41534-021-00474-3' : {'all' : 25, 'core' : 22},
          '10.1038/s42005-019-0238-1' : {'all' : 25, 'core' : 21},
          '10.1038/s41567-020-01109-8' : {'all' : 25, 'core' : 20},
          '10.1038/s41567-019-0550-4' : {'all' : 25, 'core' : 19},
          '10.1038/s41467-020-17865-3' : {'all' : 25, 'core' : 19},
          '10.1038/s41467-018-04372-9' : {'all' : 25, 'core' : 16},
          '10.1038/s41586-020-2752-4' : {'all' : 25, 'core' : 15},
          '10.1038/s41566-021-00903-x' : {'all' : 25, 'core' : 14},
          '10.1038/s41566-019-0502-7' : {'all' : 25, 'core' : 12},
          '10.1038/s41467-019-13199-x' : {'all' : 25, 'core' : 12},
          '10.1038/s41567-020-01139-2' : {'all' : 25, 'core' : 11},
          '10.1038/s41467-017-00706-1' : {'all' : 25, 'core' : 11},
          '10.1038/nphoton.2016.228' : {'all' : 25, 'core' : 10},
          '10.1038/s41467-020-14818-8' : {'all' : 24, 'core' : 21},
          '10.1038/s41467-019-13416-7' : {'all' : 24, 'core' : 21},
          '10.1038/s41467-020-19916-1' : {'all' : 24, 'core' : 20},
          '10.1038/s42254-020-0182-8' : {'all' : 24, 'core' : 19},
          '10.1038/s41586-021-03290-z' : {'all' : 24, 'core' : 17},
          '10.1038/s41467-020-20280-3' : {'all' : 24, 'core' : 15},
          '10.1038/s41567-018-0394-3' : {'all' : 24, 'core' : 12},
          '10.1038/s41467-018-04536-7' : {'all' : 24, 'core' : 10},
          '10.1038/s41567-019-0478-8' : {'all' : 23, 'core' : 18},
          '10.1038/s41467-021-24033-8' : {'all' : 23, 'core' : 18},
          '10.1038/s41534-022-00539-x' : {'all' : 23, 'core' : 16},
          '10.1038/s41567-021-01201-7' : {'all' : 23, 'core' : 13},
          '10.1038/s41467-020-17471-3' : {'all' : 23, 'core' : 12},
          '10.1038/nnano.2015.171' : {'all' : 23, 'core' : 12},
          '10.1038/s41586-021-03721-x' : {'all' : 22, 'core' : 20},
          '10.1038/s41598-019-41324-9' : {'all' : 22, 'core' : 19},
          '10.1038/s41534-021-00438-7' : {'all' : 22, 'core' : 18},
          '10.1038/s41467-017-00534-3' : {'all' : 22, 'core' : 12},
          '10.1038/s41598-017-04225-3' : {'all' : 22, 'core' : 11},
          '10.1038/s41467-019-13545-z' : {'all' : 22, 'core' : 11},
          '10.1038/s41467-018-03623-z' : {'all' : 22, 'core' : 11},
          '10.1038/s41592-020-01004-3' : {'all' : 21, 'core' : 19},
          '10.1038/s41598-019-49657-1' : {'all' : 21, 'core' : 18},
          '10.1038/s41467-018-06055-x' : {'all' : 21, 'core' : 18},
          '10.1038/s41598-017-10051-4' : {'all' : 21, 'core' : 16},
          '10.1038/s41467-018-05879-x' : {'all' : 21, 'core' : 16},
          '10.1038/s41566-017-0050-y' : {'all' : 21, 'core' : 15},
          '10.1038/s41598-019-38495-w' : {'all' : 21, 'core' : 14},
          '10.1038/s41467-019-13735-9' : {'all' : 21, 'core' : 13},
          '10.1038/s41598-018-35264-z' : {'all' : 21, 'core' : 12},
          '10.1038/s41467-018-07124-x' : {'all' : 21, 'core' : 12},
          '10.1038/s41467-020-15240-w' : {'all' : 21, 'core' : 10},
          '10.1038/s41535-021-00310-z' : {'all' : 20, 'core' : 14},
          '10.1038/s41467-021-21256-7' : {'all' : 20, 'core' : 13},
          '10.1038/s41467-018-06848-0' : {'all' : 20, 'core' : 13},
          '10.1038/s41566-019-0506-3' : {'all' : 20, 'core' : 12},
          '10.1038/s41467-019-09501-6' : {'all' : 20, 'core' : 12},
          '10.1038/s41467-018-03849-x' : {'all' : 20, 'core' : 12},
          '10.1038/s41567-020-01161-4' : {'all' : 20, 'core' : 11},
          '10.1038/s41598-019-53435-4' : {'all' : 19, 'core' : 18},
          '10.1038/s41467-020-20729-5' : {'all' : 19, 'core' : 16},
          '10.1038/s41467-018-05700-9' : {'all' : 19, 'core' : 14},
          '10.1038/s41467-018-03254-4' : {'all' : 19, 'core' : 13},
          '10.1038/s41467-021-22709-9' : {'all' : 19, 'core' : 12},
          '10.1038/s41586-021-03999-x' : {'all' : 19, 'core' : 11},
          '10.1038/s41467-021-23454-9' : {'all' : 19, 'core' : 11},
          '10.1038/s41467-017-02366-7' : {'all' : 19, 'core' : 11},
          '10.1038/s41467-021-24809-y' : {'all' : 19, 'core' : 10},
          '10.1038/s41467-017-01589-y' : {'all' : 19, 'core' : 10},
          '10.1038/s41598-018-28703-4' : {'all' : 18, 'core' : 18},
          '10.1038/s41598-020-71107-6' : {'all' : 18, 'core' : 17},
          '10.1038/s41534-022-00525-3' : {'all' : 18, 'core' : 17},
          '10.1038/s41598-021-82740-0' : {'all' : 18, 'core' : 16},
          '10.1038/s42005-020-00415-0' : {'all' : 18, 'core' : 15},
          '10.1038/s41598-021-01445-6' : {'all' : 18, 'core' : 15},
          '10.1038/s41567-021-01355-4' : {'all' : 18, 'core' : 12},
          '10.1038/s41467-020-20799-5' : {'all' : 18, 'core' : 12},
          '10.1038/s41598-018-25492-8' : {'all' : 18, 'core' : 11},
          '10.1038/s41567-020-01102-1' : {'all' : 18, 'core' : 11},
          '10.1038/s41467-019-09429-x' : {'all' : 18, 'core' : 11},
          '10.1038/s41598-020-77315-4' : {'all' : 17, 'core' : 15},
          '10.1038/s41598-018-38388-4' : {'all' : 17, 'core' : 15},
          '10.1038/s41598-019-50429-0' : {'all' : 17, 'core' : 14},
          '10.1038/s41467-020-14873-1' : {'all' : 17, 'core' : 14},
          '10.1038/s41598-017-13378-0' : {'all' : 17, 'core' : 13},
          '10.1038/s42005-021-00524-4' : {'all' : 17, 'core' : 12},
          '10.1038/s41566-021-00802-1' : {'all' : 17, 'core' : 12},
          '10.1038/s41467-021-24679-4' : {'all' : 17, 'core' : 12},
          '10.1038/nnano.2017.85' : {'all' : 17, 'core' : 12},
          '10.1038/s41534-021-00450-x' : {'all' : 17, 'core' : 11},
          '10.1038/s41534-021-00414-1' : {'all' : 17, 'core' : 11},
          '10.1038/s41467-019-13000-z' : {'all' : 17, 'core' : 11},
          '10.1038/s42005-019-0209-6' : {'all' : 16, 'core' : 16},
          '10.1038/s42005-020-00502-2' : {'all' : 16, 'core' : 15},
          '10.1038/s41534-021-00444-9' : {'all' : 16, 'core' : 13},
          '10.1038/s41467-018-05239-9' : {'all' : 16, 'core' : 12},
          '10.1038/srep26284' : {'all' : 16, 'core' : 10},
          '10.1038/s41467-021-23437-w' : {'all' : 15, 'core' : 10},
          '10.1007/s43673-021-00017-0' : {'all' : 75, 'core' : 60},
          '10.1007/978-3-662-02520-8' : {'all' : 56, 'core' : 23},
          '10.1007/s11433-021-1734-3' : {'all' : 53, 'core' : 49},
          '10.1007/s43673-021-00030-3' : {'all' : 44, 'core' : 42},
          '10.1007/s00220-021-04118-7' : {'all' : 35, 'core' : 25},
          '10.1007/s11433-017-9113-4' : {'all' : 32, 'core' : 13},
          '10.1007/s00023-018-0736-9' : {'all' : 31, 'core' : 15},
          '10.1007/978-3-030-34489-4' : {'all' : 27, 'core' : 17},
          '10.1007/s11128-017-1809-2' : {'all' : 25, 'core' : 22},
          '10.1007/s11433-021-1775-4' : {'all' : 25, 'core' : 21},
          '10.1007/s11128-021-02992-7' : {'all' : 24, 'core' : 14},
          '10.1007/s11128-021-03140-x' : {'all' : 23, 'core' : 23},
          '10.1007/s11128-018-2082-8' : {'all' : 23, 'core' : 14},
          '10.1007/s11128-018-2107-3' : {'all' : 22, 'core' : 21},
          '10.1007/s11128-020-02938-5' : {'all' : 22, 'core' : 15},
          '10.1007/s40509-019-00217-2' : {'all' : 22, 'core' : 10},
          '10.1007/s11128-019-2364-9' : {'all' : 21, 'core' : 17},
          '10.1007/s11128-018-2002-y' : {'all' : 21, 'core' : 17},
          '10.1007/s00220-020-03884-0' : {'all' : 21, 'core' : 16},
          '10.1007/978-3-030-20726-7_17' : {'all' : 21, 'core' : 16},
          '10.1007/s11128-018-2161-x' : {'all' : 21, 'core' : 15},
          '10.1007/s00220-017-2928-4' : {'all' : 21, 'core' : 10},
          '10.1007/s11128-021-03079-z' : {'all' : 20, 'core' : 19},
          '10.1007/s10208-018-9385-0' : {'all' : 19, 'core' : 10},
          '10.1007/s11128-021-03165-2' : {'all' : 18, 'core' : 18},
          '10.1007/s11128-021-03157-2' : {'all' : 18, 'core' : 12},
          '10.1007/s11128-018-2155-8' : {'all' : 17, 'core' : 16},
          '10.1007/s11128-018-2055-y' : {'all' : 17, 'core' : 11},
          '10.1007/s10676-017-9438-0' : {'all' : 16, 'core' : 14},
          '10.1140/epjd/e2015-60464-1' : {'all' : 184, 'core' : 109},
          '10.1140/epjst/e2018-800091-5' : {'all' : 81, 'core' : 12},
          '10.1140/epjqt/s40507-017-0059-7' : {'all' : 18, 'core' : 12},
          '10.1140/epjqt/s40507-021-00114-x' : {'all' : 17, 'core' : 17},
          '10.1140/epjqt/s40507-021-00108-9' : {'all' : 17, 'core' : 14},
          '10.1140/epjqt/s40507-021-00100-3' : {'all' : 17, 'core' : 14}}

jc = {'00006': ['aaca', 'Adv.Appl.Clifford Algebras', '', '', 'P'],
      '00016': ['pip', 'Phys.Perspect.', '', '', 'P'],
      '00023': ['ahp', 'Annales Henri Poincare', '', '', 'P'],
      '00029': ['selmat', 'Selecta Math.', '', '', 'P'],
      '00031': ['trgr', 'Transform.Groups', '', '', 'P'],
      '00159': ['aar', 'Astron.Astrophys.Rev.', '', '', 'P'],
      '00205': ['arma', 'Arch.Ration.Mech.Anal.', '', '', 'P'],
      '00220': ['cmp', 'Commun.Math.Phys.', '', '', 'P'],
      '00222': ['invmat', 'Invent.Math.', '', '', 'P'],
      '00229': ['manusmat', 'Manuscr.Math.', '', '', 'P'],
      '00332': ['jnonlinsci', 'J.Nonlin.Sci.', '', '', 'P'],
      '00339': ['apa', 'Appl.Phys.', 'A', '', 'P'], #HAL
      '00340': ['apb', 'Appl.Phys.', 'B', '', 'P'], #HAL
      '00526': ['cvpde', 'Calc.Var.Part.Differ.Equ', '', '', 'P'],
      '00601': ['fbs', 'Few Body Syst.', '', '', 'P'],
      '10050': ['epja', 'Eur.Phys.J.', 'A', '', 'P'],
      '10051': ['epjb', 'Eur.Phys.J.', 'B', '', 'P'],
      '10052': ['epjc', 'Eur.Phys.J.', 'C', '', 'P'],
      '10053': ['epjd', 'Eur.Phys.J.', 'D', '', 'P'],
      '10440': ['acapma', 'Acta Appl.Math.', '', '', 'P'],
      '10509': ['ass', 'Astrophys.Space Sci.', '', '', 'P'],
      '10511': ['ast', 'Astrophysics', '', '', 'P'],
      '10512': ['atenerg', 'At.Energ.', '', '', 'P'],
      '10582': ['czjp', 'Czech.J.Phys.', '', '', 'P'], # stopped 2006
      '10686': ['ea', 'Exper.Astron.', '', '', 'P'],
      '10699': ['fosi', 'Found.Sci.', '', '', 'P'],
      '10701': ['fp', 'Found.Phys.', '', '', 'P'],
      '10702': ['fpl', 'Found.Phys.Lett.', '', '', 'P'], # stopped 2006
      '10714': ['grg', 'Gen.Rel.Grav.', '', '', 'P'],
      '10723': ['jgc', 'J.Grid Comput.', '', '', 'P'],
      '10740': ['hite', 'High Temperature', '', 'Teplofizika Vysokikh Temperatur', 'P'], #last issue 2021-03 ? Russian War?
      '10751': ['hypfin', 'Hyperfine Interact.', '', '', 'P'],
      '10773': ['ijtp', 'Int.J.Theor.Phys.', '', '', 'P'],
      '10781': ['fias', 'FIAS Interdisc.Sci.Ser.', '', '', 'P'], #book series
      '10786': ['iet', 'Instrum.Exp.Tech.', '', '', 'P'],
      '10853': ['jmsme', 'J.Materials Sci.', '', '', 'P'],
      '10909': ['jltp', 'J.Low Temp.Phys.', '', '', 'P'],
      '10946': ['jrlr', 'J.Russ.Laser Res.', '', '', 'P'],
      '10955': ['jstatphys', 'J.Statist.Phys.', '', '', 'P'],
      '10958': ['jms', 'J.Math.Sci.', '', 'Zap.Nauchn.Semin.', 'P'],
      '10967': ['jrnc', 'J.Radioanal.Nucl.Chem.', '', '', 'P'],
      '11005': ['lmp', 'Lett.Math.Phys.', '', '', 'P'],
      '11006': ['matnot', 'Math.Notes', '', '', 'P'], #also harvested via mathnet.ru
      '11018': ['mt', 'Meas.Tech.', '', '', 'P'],
      '11040': ['mpag', 'Math.Phys.Anal.Geom.', '', '', 'P'],
      '11128': ['qif', 'Quant.Inf.Proc.', '', '', 'P'],
      '11139': ['ramanujan', 'Ramanujan J.', '', '', 'P'],
      '11182': ['rpj', 'Russ.Phys.J.', '', 'Izv.Vuz.Fiz.', 'P'],
      '11207': ['soph', 'Solar Phys.', '', '', 'P'],#HAL
      '11214': ['ssr', 'Space Sci.Rev.', '', '', 'P'],
      '11229': ['synthese', 'Synthese', '', '', 'P'],
      '11232': ['tmp', 'Theor.Math.Phys.', '', 'Teor.Mat.Fiz.', 'P'],
      '11253': ['umj', 'Ukr.Math.J.', '', '', 'P'],
      '11425': ['sica', 'Sci.China Math.', '', '', 'P'],
      '11433': ['sicg', 'Sci.China Phys.Mech.Astron.', '', '', 'P'],
      '11434': ['csb', 'Chin.Sci.Bull.', '', '', 'P'], #stopped 2016
      '11443': ['al', 'Astron.Lett.', '', '', 'P'],
      '11444': ['ar', 'Astron.Rep.', '', '', 'P'],
      '11446': ['dok', 'Dokl.Phys.', '', '', 'P'], #last issue 2021-03 ? Russian War?
      '11447': ['jetp', 'J.Exp.Theor.Phys.', '', 'Zh.Eksp.Teor.Fiz.', 'P'],
      '11448': ['jtpl', 'JETP Lett.', '', 'Pisma Zh.Eksp.Teor.Fiz.', 'P'],
      '11449': ['opsp', 'Opt.Spectrosc.', '', '', 'P'],
      '11450': ['pan', 'Phys.At.Nucl.', '', 'Yad.Fiz.', 'P'],
      '11451': ['ptss', 'Sov.Phys.Solid State', '', 'Fiz.Tverd.Tela', 'P'],
      '11452': ['plpr', 'Plasma Phys.Rep.', '', 'Fiz.Plasmy', 'P'],
      '11454': ['tp', 'Tech.Phys.', '', '', 'P'],
      '11455': ['tpl', 'Tech.Phys.Lett.', '', '', 'P'],
      '11467': ['fpc', 'Front.Phys.(Beijing)', '', '', 'P'],
      '11470': ['cmmp', 'Comput.Math.Math.Phys.', '', '', 'P'],
      '11490': ['lasp', 'Laser Phys.', '', '', 'P'], # stopped 2012
      '11496': ['ppn', 'Phys.Part.Nucl.', '', 'Fiz.Elem.Chast.Atom.Yadra', 'P'],
      '11497': ['ppnl', 'Phys.Part.Nucl.Lett.', '', 'Pisma Fiz.Elem.Chast.Atom.Yadra', 'P'],
      '11503': ['rjmp', 'Russ.J.Math.Phys.', '', '', 'P'],
      '11534': ['cejp', 'Central Eur.J.Phys.', '', '', 'P'], # stopped 2014
      '11734': ['epjst', 'Eur.Phys.J.ST', '', '', 'P'],
      '11755': ['ab', 'Astrophys.Bull.', '', '', 'P'],
      '11953': ['blpi', 'Bull.Lebedev Phys.Inst.', '', '', 'P'],
      '11954': ['brasp', 'Bull.Russ.Acad.Sci.Phys.', '', 'Izv.Ross.Akad.Nauk Ser.Fiz.', 'P'],
      '11958': ['jocoph', 'J.Contemp.Phys.', '', 'Izv.Akad.Nauk Arm.SSR Fiz.', 'P'],
      '11972': ['mupb', 'Moscow Univ.Phys.Bull.', '', '', 'P'],
      '12036': ['jasas', 'J.Astrophys.Astron.', '', '', 'P'],
      '12043': ['pramana', 'Pramana', '', '', 'P'],
      '12045': ['resonance', 'Reson.', '', '', 'P'],
      '12220': ['jganal', 'J.Geom.Anal.', '', '', 'P'],
      '12267': ['gc', 'Grav.Cosmol.', '', '', 'P'],
      '12607': ['pauaa', 'p Adic Ultra.Anal.Appl.', '', '', 'P'],
      '12648': ['ijp', 'Indian J.Phys.', '', '', 'P'],
      '13129': ['epjh', 'Eur.Phys.J.', 'H', '', 'P'],
      '13130': ['jhep', 'JHEP', '', '', 'P'],
      '13194': ['ejphilsci', 'Eur.J.Phil.Sci.', '', '', 'P'],
      '13324': ['anmp', 'Anal.Math.Phys.', '', '', 'P'],
      '13360': ['epjp', 'Eur.Phys.J.Plus', '', '', 'P'],
      '13538': ['bjp', 'Braz.J.Phys.', '', '', 'P'],
      '13370': ['afrmat', 'Afr.Math.', '', '', 'P'],
      '40009': ['nasl', 'Natl.Acad.Sci.Lett.', '', '', 'P'],
      '40010': ['pnisia', 'Proc.Nat.Inst.Sci.India (Pt.A Phys.Sci.)', '', '', 'P'],
      '40042': ['jkps', 'J.Korean Phys.Soc.', '', '', 'P'],
      '40065': ['arjoma', 'Arab.J.Math.', '', '', 'P'],
      '40306': ['avietnamm', 'Acta Math.Vietnamica', '', '', 'P'],
      '40485': ['epjti', 'EPJ Tech.Instrum.', '', '', 'P'],
      '40507': ['epjqt', 'EPJ Quant.Technol.', '', '', 'P'],
      '40509': ['qsmf', 'Quant.Stud.Math.Found.', '', '', 'P'],
      '40623': ['eaplsc', 'Earth Planets Space', '', '', 'P'],
      '40766': ['rnc', 'Riv.Nuovo Cim.', '', '', 'PR'],
      '40818': ['apde', 'Ann.PDE', '', '', 'P'],
      '40995': ['ijsta', 'Iran.J.Sci.Technol.A', '', '', 'P'],
      '41114': ['lrr', 'Living Rev.Rel.', '', '', 'R'],
      '41365': ['nst', 'Nucl.Sci.Tech.', '', '', 'P'],
      '41467': ['natcomm', 'Nature Commun.', '', '', 'P'],
      '41534': ['natquantinf', 'npj Quantum Inf.', '', '', 'P'],
      '41550': ['natastr', 'Nature Astron.', '', '', 'P'],
      '41566': ['natphoton', 'Nature Photon.', '', '', 'P'],
      '41567': ['natphys', 'Nature Phys.', '', '', 'P'],
      '41586': ['nature', 'Nature', '', '', 'P'],
      '41598': ['scirep', 'Sci.Rep.', '', '', 'P'],
      '41605': ['rdtm', 'Radiat.Detect.Technol.Methods', '', '', 'P'],
      '41614': ['rmplasmap', 'Rev.Mod.Plasma Phys.', '', '', 'P'],
      '41781': ['csbg', 'Comput.Softw.Big Sci.', '', '', 'P'],
      '42005': ['communphys', 'Commun.Phys.', '', '', 'P'],
      '42254': ['natrp', 'Nature Rev.Phys.', '', '', 'P'],
      '43538': ['pinsa', 'Proc.Indian Natl.Sci.Acad.', '', '', 'RP'],
      '43673': ['aappsb', 'AAPPS Bull.', '', '', ''],
      '44198': ['jnlmp', 'J.Nonlin.Math.Phys.', '', '', 'P'],
      '44214': ['qufr', 'Quant.Front', '', '', 'P'],
#Books
       '0304': ['lnm', 'Lect.Notes Math.', '', '', 'PS', ''],
       '0361': ['spprph', 'Springer Proc.Phys.', '', '', 'C', ''],
       '0426': ['stmp', 'Springer Tracts Mod.Phys.', '', '', 'S', ''],
       '0720': ['thmaph', 'Theor.Math.Phys.', '', '', 'S', ''], #???
       '0840': ['grtecoph', 'BOOK', '', '', 'S', ''], # stopped 2005
       '0848': ['asasli', 'BOOK', '', '', 'S', ''],
       '3052': ['acph', 'Accel.Phys.', '', '', 'S', ''], # stopped 1998
       '4308': ['adteph', 'Adv.Texts Phys.', '', '', 'S', ''], # stopped 2007
       '4813': ['prmaph', 'Prog.Math.Phys.', '', '', 'S', ''],
       '4890': ['eist', 'Einstein Studies', '', '', 'S', ''], #stopped 2012
       '5267': ['paacde', 'BOOK', '', '', 'S', ''],
       '5304': ['lnp', 'Lect.Notes Phys.', '', '', 'PS', ''],
       '5664': ['assl', 'Astrophys.Space Sci.Libr.', '', '', 'S', ''],
       '6001': ['futhph', 'Fundam.Theor.Phys.', '', '', 'S', ''],
       '6316': ['mpstud', 'Math.Phys.Stud.', '', '', 'S', ''],
       '7395': ['assp', 'Astrophys.Space Sci.Proc.', '', '', 'C', ''],

       '5584': ['aemb', 'BOOK', '', '', 'S', 'Advances in Experimental Medicine and Biology'], #whole book
       '4848': ['pim', 'BOOK' , '', '', 'S', ''], #whole book (327)
      '15602': ['sscml', 'BOOK', '', '', 'S', 'The Springer Series on Challenges in Machine Learning'], #Einzelaufnah
      '15585': ['icme', 'BOOK', '', '', 'C', ''], #einzelaufnahmen

       '8389': ['nophsc', 'Nonlin.Phys.Sci.', '', '', 'S', ''], # stopped 2013?
       '8431': ['gtip', 'BOOK', '', '', 'S', 'Grad.Texts Math.'],
       '8790': ['sprthe', 'BOOK', '', '', 'T', 'Springer Theses'], #Springer Theses
       '8806': ['spprma', 'Springer Proc.Math.', '', '', 'C', ''], #discontinued
       '8902': ['sprbip', 'BOOK', '', '', 'S', 'SpringerBriefs in Physics'],
      '10502': ['fimono', 'Fields Inst.Monogr.', '', '', 'S', ''], #Fields Institute Monographs
      '10503': ['ficomm', 'Fields Inst.Commun.', '', '', 'S']} #Fields Institute Communications
#42005 Commun.Phys.

jc['10948'] = ['jsnovm', 'J.Supercond.Nov.Mag.', '', '', 'P'] #! (requested 2022-09-15, added 2023-01-18)
jc['00209'] = ['matz', 'Math.Z.', '', '', 'P'] #(requested 2022-09-15, added 2023-01-18)
jc['11082'] = ['oqe', 'Opt.Quant.Electron.', '', '', 'P'] #(requested 2022-09-15, added 2023-01-18)
jc['40094'] = ['jtap', 'J.Theor.Appl.Phys.', '', '', 'P'] #now at New publisher: Please contact Islamic Azad University
#asked for
jc['00031'] = ['transfgr', 'Transform.Groups', '', '', 'P'] # requested on 2023-11-14
jc['00037'] = ['compcompl', 'Comp.Complexity', '', '', 'P'] # requested on 2023-11-14
jc['00205'] = ['armanal', 'Arch.Ration.Mech.Anal.', '', '', 'P'] # requested on 2023-11-14
jc['00208'] = ['mathann', 'Math.Ann.', '', '', 'P'] # requested on 2023-11-14
jc['00440'] = ['ptrfield', 'Probab.Theor.Related Fields', '', '', 'P'] # requested on 2023-11-14
jc['00453'] = ['algorithmica', 'Algorithmica', '', '', 'P'] # requested on 2023-11-14
jc['10455'] = ['annalsgag', 'Annals Global Anal.Geom.', '', '', 'P'] # requested on 2023-11-14
jc['10623'] = ['dccryptogr', 'Des.Codes Cryptogr.', '', '', 'P'] # requested on 2023-11-14
jc['10910'] = ['jmathchem', 'J.Math.Chem.', '', '', 'P'] # requested on 2023-11-14
jc['10915'] = ['jscicomput', 'J.Sci.Comput.', '', '', 'P'] # requested on 2023-11-14
jc['11038'] = ['earthmoonp', 'Earth Moon Planets', '', '', 'P'] # requested on 2023-11-14
jc['11227'] = ['jsupercomput', 'J.Supercomput.', '', '', 'P'] # requested on 2023-11-14
jc['40009'] = ['natlasl', 'Natl.Acad.Sci.Lett.', '', '', 'P'] # requested on 2023-11-14
jc['40306'] = ['amvietnam', 'Acta Math.Vietnamica', '', '', 'P'] # requested on 2023-11-14
jc['41115'] = ['livrevcompastr', 'Liv.Rev.Comput.Astrophys.', '', '', 'P'] # requested on 2023-11-14
jc['41524'] = ['mpjcm', 'npj Computat.Mater.', '', '', 'P'] # requested on 2023-11-14
jc['41563'] = ['natmaterials', 'Nature Materials', '', '', 'P'] # requested on 2023-11-14
jc['41565'] = ['natnanotech', 'Nature Nanotech.', '', '', 'P'] # requested on 2023-11-14
jc['41928'] = ['natelectron', 'Nature Electron.', '', '', 'P'] # requested on 2023-11-14
jc['42484'] = ['quantmachint', 'Quantum Machine Intelligence ', '', '', 'P'] # requested on 2023-11-14
jc['42979'] = ['sncomputsci', 'SN Comput.Sci.', '', '', 'P'] # requested on 2023-11-14
jc['43246'] = ['communmater', 'Commun.Mater.', '', '', 'P'] # requested on 2023-11-14
jc['43538'] = ['pindiannsa', 'Proc.Indian Natl.Sci.Acad.', '', '', 'P'] # requested on 2023-11-14
jc['43588'] = ['natcomputatsci', 'Nature Computat.Sci.', '', '', 'P'] # requested on 2023-11-14


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
    keepit = True
    jnlnr = False
    rec = {'doi' : doi, 'note' : []}
    rec['artlink'] = 'https://doi.org/' + rec['doi']
    #"known" journal?
    if re.search('10.\d+\/s\d\d\d\d\d', rec['doi']):
        jnlnr = re.sub('10.\d+\/s(\d\d\d\d\d).*', r'\1', rec['doi'])
        if jnlnr in jc:
            rec['jnl'] = jc[jnlnr][1]
            rec['tc'] = jc[jnlnr][4]
        else:
            jnlnr = False

    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(10)
    except:
        print('  wait 120s to try again')
        time.sleep(120)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(20)
    ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_author_email', 'citation_author_orcid',
                                        'description', 'dc.description', 'citation_cover_date', 'citation_article_type',
                                        'prism.publicationDate', 'prism.volume', 'citation_title',
                                        'prism.number',  'prism.keyword'])
    if not jnlnr:
        rec['tc'] = 'P'
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'prism.publicationName'}):
            jnlname = meta['content']
            if jnlname in ['Nature Communications']:
                rec['jnl'] = 'Nature Commun.'
                jnlnr = True
            elif jnlname in ['Nature']:
                rec['jnl'] = 'Nature'
                jnlnr = True
            elif jnlname in ['Nature Physics']:
                rec['jnl'] = 'Nature Phys.'
                jnlnr = True
            elif jnlname in ['Nature Photonics']:
                rec['jnl'] = 'Nature Photon.'
                jnlnr = True
            elif jnlname in ['Journal of Soviet Laser Research']:
                rec['jnl'] = 'J.Russ.Laser Res.'
                jnlnr = True
            elif jnlname in ['Journal of Statistical Physics']:
                rec['jnl'] = 'J.Statist.Phys.'
                jnlnr = True
            elif jnlname in ['Journal of Global Optimization']:
                rec['jnl'] = 'J.Global Optim.'
                jnlnr = True
            elif jnlname in ['npj Quantum Information']:
                rec['jnl'] = 'npj Quantum Inf.'
                jnlnr = True
            elif jnlname in ['Living Reviews in Relativity']:
                rec['jnl'] = 'Living Rev.Rel.'
                jnlnr = True
            elif jnlname in ['Mathematics of Control, Signals and Systems']:
                rec['jnl'] = 'Math.Control Signals Syst.'
                jnlnr = True
            elif jnlname in ['The European Physical Journal D']:
                rec['jnl'] = 'Eur.Phys.J.D'
                jnlnr = True
            elif jnlname in ['Zeitschrift für Physik']:
                rec['jnl'] = 'Z.Phys.'
                jnlnr = True
            elif jnlname in ['Theoretical and Mathematical Physics']:
                rec['jnl'] = 'Theor.Math.Phys.'
                jnlnr = True
            elif jnlname in ['Journal of Cryptology']:
                rec['jnl'] = 'J.Cryptolog.'
                jnlnr = True
            elif jnlname in ['Scientific Reports']:
                rec['jnl'] = 'Sci.Rep.'
                jnlnr = True
            elif jnlname in ['Rendiconti del Circolo Matematico di Palermo (1884-1940)']:
                rec['jnl'] = 'Rend.Circ.Mat.Palermo'
                jnlnr = True
            elif jnlname in ['General Relativity and Gravitation']:
                rec['jnl'] = 'Gen.Rel.Grav.'
                jnlnr = True
            elif jnlname in ['Nature Materials']:
                rec['jnl'] = 'Nature Materials'
                jnlnr = True
            elif jnlname in ['Foundations of Physics']:
                rec['jnl'] = 'Found.Phys.'
                jnlnr = True
            elif jnlname in ['EPJ Quantum Technology']:
                rec['jnl'] = 'EPJ Quant.Technol.'
                jnlnr = True
            elif jnlname in ['The European Physical Journal A - Hadrons and Nuclei']:
                rec['jnl'] = 'Eur.Phys.J.A'
                jnlnr = True
            elif jnlname in ['Communications in Mathematical Physics']:
                rec['jnl'] = 'Commun.Math.Phys.'
                jnlnr = True
            elif jnlname in ['Nature Nanotechnology']:
                rec['jnl'] = 'Nature Nanotech.'
                jnlnr = True
            elif jnlname in ['Nature Machine Intelligence']:
                rec['jnl'] = 'Nature Mach.Intell.'
                jnlnr = True
            elif jnlname in ['The bulletin of mathematical biophysics']:
                rec['jnl'] = 'Bull.Math.Biol.'
                jnlnr = True
            elif jnlname in ['Il Nuovo Cimento (1955-1965)']:
                rec['jnl'] = 'Nuovo Cim.'
                jnlnr = True
            elif jnlname in ['MRS Bulletin']:
                rec['jnl'] = 'MRS Bull.'
                jnlnr = True
            elif jnlname in ['Il Nuovo Cimento A (1965-1970)']:
                rec['jnl'] = 'Nuovo Cim.A'
                jnlnr = True
            elif jnlname in ['Machine Learning']:
                rec['jnl'] = 'Machine Learning'
                jnlnr = True
            elif jnlname in ['Mathematical Programming Computation']:
                rec['jnl'] = 'Math.Prog.Comput.'
                jnlnr = True
            elif jnlname in ['Light: Science & Applications']:
                rec['jnl'] = 'Light Sci. Appl.'
                jnlnr = True
            elif jnlname in ['International Journal of Theoretical Physics']:
                rec['jnl'] = 'Int.J.Theor.Phys.'
                jnlnr = True
            elif jnlname in ['Theory of Computing Systems']:
                rec['jnl'] = 'Theor.Comp.Syst.'
                jnlnr = True
            elif jnlname in ['Astrophysics and Space Science']:
                rec['jnl'] = 'Astrophys.Space Sci.'
                jnlnr = True
            elif jnlname in ['Mathematical Programming']:
                rec['jnl'] = 'Math.Programming'
                jnlnr = True
            elif jnlname in ['aequationes mathematicae']:
                rec['jnl'] = 'Aequat.Math.'
                jnlnr = True
            elif jnlname in ['Inventiones mathematicae']:
                rec['jnl'] = 'Invent.Math.'
                jnlnr = True
            elif jnlname in ['Journal of Combinatorial Optimization']:
                rec['jnl'] = 'J.Combin.Optim.'
                jnlnr = True
            elif jnlname in ['Materials Theory']:
                rec['jnl'] = 'Mater.Theor.'
                jnlnr = True
            elif jnlname in ['Nature Reviews Materials']:
                rec['jnl'] = 'Nature Rev.Mater.'
                jnlnr = True
            elif jnlname in ['Journal of Low Temperature Physics']:
                rec['jnl'] = 'J.Low Temp.Phys.'
                jnlnr = True
            elif jnlname in ['Proceedings of the Indian Academy of Sciences - Section A']:
                rec['jnl'] = 'Proc.Indian Acad.Sci.A'
                jnlnr = True
            elif jnlname in ['Mathematische Zeitschrift']:
                rec['jnl'] = 'Math.Z.'
                jnlnr = True
            elif jnlname in ['Mathematische Annalen']:
                rec['jnl'] = 'Math.Ann.'
                jnlnr = True
            elif jnlname in ['Foundations of Computational Mathematics']:
                rec['jnl'] = 'Found.Comput.Math.'
                jnlnr = True
            elif jnlname in ['Il Nuovo Cimento B (1971-1996)']:
                rec['jnl'] = 'Nuovo Cim.B'
                jnlnr = True
            elif jnlname in ['Space Science Reviews']:
                rec['jnl'] = 'Space Sci.Rev.'
                jnlnr = True
            elif jnlname in ['4OR']:
                rec['jnl'] = '4OR'
                jnlnr = True
            elif jnlname in ['Il Nuovo Cimento B (1965-1970)']:
                rec['jnl'] = 'Nuovo Cim.B'
                jnlnr = True
            elif jnlname in ['Lettere al Nuovo Cimento (1971-1985)']:
                rec['jnl'] = 'Lett.Nuovo Cim.'
                jnlnr = True
            elif jnlname in ['International Journal of Computer Vision']:
                rec['jnl'] = 'Int.J.Comput.Vision'
                jnlnr = True
            elif jnlname in ['Radiophysics and Quantum Electronics']:
                rec['jnl'] = 'Radiophys.Quant.Electron.'
                jnlnr = True
            elif jnlname in ['Computational Optimization and Applications']:
                rec['jnl'] = 'Comput.Optim.Appl.'
                jnlnr = True
            elif jnlname in ['Quantum Information Processing']:
                rec['jnl'] = 'Quant.Inf.Proc.'
                jnlnr = True
            elif jnlname in ['Networking Science']:
                rec['jnl'] = 'Netw.Sci.'
                jnlnr = True
            elif jnlname in ['Scientific Data']:
                rec['jnl'] = 'Sci.Data'
                jnlnr = True
            elif jnlname in ['Naturwissenschaften']:
                rec['jnl'] = 'Naturwiss.'
                jnlnr = True
            elif jnlname in ['Natural Computing']:
                rec['jnl'] = 'Natural Comput.'
                jnlnr = True
            elif jnlname in ['Applied Physics B']:
                rec['jnl'] = 'Appl.Phys.B'
                jnlnr = True
            elif jnlname in ['The European Physical Journal Special Topics']:
                rec['jnl'] = 'Eur.Phys.J.ST'
                jnlnr = True
            elif jnlname in ['Biological Cybernetics']:
                rec['jnl'] = 'Biol.Cyber.'
                jnlnr = True
            elif jnlname in ['Czechoslovak Journal of Physics']:
                rec['jnl'] = 'Czech.J.Phys.'
                jnlnr = True
            elif jnlname in ['Nature Chemistry']:
                rec['jnl'] = 'Nature Chem.'
                jnlnr = True
            elif jnlname in ['Zeitschrift für Physik B Condensed Matter']:
                rec['jnl'] = 'Z.Phys.B'
                jnlnr = True
            elif jnlname in ['Journal of Soviet Mathematics']:
                rec['jnl'] = 'J.Sov.Math.'
                jnlnr = True
            elif jnlname in ['Il Nuovo Cimento (1924-1942)']:
                rec['jnl'] = 'Nuovo Cim.'
                jnlnr = True
            elif jnlname in ['Topoi']:
                rec['jnl'] = 'Topoi'
                jnlnr = True
            elif jnlname in ['Numerische Mathematik']:
                rec['jnl'] = 'Numer.Math.'
                jnlnr = True
            elif jnlname in ['The European Physical Journal D - Atomic, Molecular, Optical and Plasma Physics']:
                rec['jnl'] = 'Eur.Phys.J.D'
                jnlnr = True
            elif jnlname in ['Zeitschrift für Physik A Hadrons and nuclei']:
                rec['jnl'] = 'Z.Phys.A'
                jnlnr = True
                jnlnr = True
            elif jnlname in ['Nature Methods']:
                rec['jnl'] = 'Nature Meth.'
                jnlnr = True
#            elif jnlname in ['']:
#                rec['jnl'] = ''
#                jnlnr = True
            else:
                print('  prism.publicationName=',  meta['content'])
                if not meta['content'] in missingjournals:
                    missingjournals.append(meta['content'])


    if not jnlnr:
        continue

    #von Hand
    if doi == '10.1038/s41586-018-0085-3':
        rec['autaff'] = []
        rec['col'] = 'BIG Bell Test'
    elif doi == '10.1038/s41586-021-03253-4':
        rec['autaff'] = []
        rec['col'] = 'BACON'

    #article number
    ps = artpage.find_all('p', attrs = {'class' : 'c-article-info-details'})
    if not ps:
        ps = artpage.find_all('li', attrs = {'class' : 'c-article-identifiers__item'})
    for p in ps:
        for span in p.find_all('span', attrs = {'data-test' : 'article-number'}):
#            if jnl in ['npj Quantum Inf.', 'J.Cryptolog.', 'Quantum Machine Intelligence', 'SN Comput.Sci.',
#                       'Complexity', 'Stat.Comput.']:
            if 'p2' in rec:
                spant = span.text.strip()
                print('     change pagination (%s-%s) to article-id (%s)' % (rec['p1'], rec['p2'], spant))
                rec['pages'] = int(rec['p2']) - int(rec['p1']) + 1
                rec['p1'] = spant
                del rec['p2']
            else:
                print("     no rec['p2'] -> keep rec['p1']=%s, neglect article-id=%s" % (rec['p1'], spant))

#            else:
#                print('  > may be article numer %s' % (span.text.strip()))
    #article type
    if 'citation_article_type' in rec:
        for at in rec['citation_article_type']:
            rec['note'].append(at)
    #license
    for a in artpage.body.find_all('a', attrs = {'rel' : 'license'}):
        if a.has_attr('href') and re.search('creativecomm', a['href']):
            rec['license'] = {'url' : a['href']}
            ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    #date
    if not 'date' in list(rec.keys()):
        for  meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_publication_date'}):
            rec['date'] = meta['content']
    if not 'date' in list(rec.keys()):
        for span in artpage.body.find_all('span', attrs = {'class' : 'bibliographic-information__value', 'id' : 'copyright-info'}):
            if re.search('[12]\d\d\d', span.text):
                rec['date'] = re.sub('.*?([12]\d\d\d).*', r'\1', span.text.strip())
    if not 'date' in rec:
        for a in artpage.body.find_all('a', attrs = {'data-track-action' : 'publication date'}):
            for dt in a.find_all('time'):
                rec['date'] = dt['datetime']
    #Keywords
    for div in artpage.body.find_all('div', attrs = {'class' : 'KeywordGroup'}):
        rec['keyw'] = []
        for span in div.find_all('span', attrs = {'class' : 'Keyword'}):
            rec['keyw'].append(span.text.strip())
    if not 'keyw' in rec:
        rec['keyw'] = []
        for li in artpage.body.find_all('li', attrs = {'class' : 'c-article-subject-list__subject'}):
            rec['keyw'].append(li.text.strip())

    #Abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'Abstract'}):
        abstract = ''
        for p in section.find_all('p'):
            abstract += p.text.strip() + ' '
        if not 'abs' in rec or len(abstract) > len(rec['abs']):
            rec['abs'] = abstract
    for div in artpage.body.find_all('div', attrs = {'id' : 'Abs1-content'}):
        for h3 in div.find_all('h3', attrs = {'class' : 'c-article__sub-heading'}):
            h3.decompose()
        for ul in div.find_all('ul', attrs = {'class' : 'c-article-subject-list'}):
            ul.decompose()
        abstract = div.text.strip()
        if not 'abs' in rec or len(abstract) > len(rec['abs']):
            rec['abs'] = abstract    #References
    references = artpage.body.find_all('ol', attrs = {'class' : ['BibliographyWrapper', 'c-article-references']})
    if not references:
        references = artpage.body.find_all('ul', attrs = {'class' : ['BibliographyWrapper', 'c-article-references']})
    for ol in references:
        rec['refs'] = []
        for li in ol.find_all('li'):
            for a in li.find_all('a'):
                if a.text.strip() in ['Google Scholar', 'MathSciNet', 'ADS']:
                    a.replace_with(' ')
                elif a.text.strip() in ['CrossRef' ,'Article']:
                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                    rdoi = re.sub('%2F', '/', rdoi)
                    a.replace_with(', DOI: %s' % (rdoi))
            rec['refs'].append([('x', li.text.strip())])

    #SPECIAL CASE LANDOLT-BOERNSTEIN
    if not rec['autaff']:
        del rec['autaff']
        #date
        #rec['tc'] = 'S'
        if not 'date' in list(rec.keys()):
            rec['date'] = re.sub('.* (\d\d\d\d) *$', r'\1', rec['abs'])
        for dl in artpage.body.find_all('dl', attrs = {'class' : 'definition-list__content'}):
            chapterDOI = False
            #ChapterDOI
            for child in dl.children:
                try:
                    child.name
                except:
                    continue
                if re.search('Chapter DOI', child.text):
                    chapterDOI = True
                elif chapterDOI:
                    rec['doi'] = child.text.strip()
                    chapterDOI = False
            #Authors and Email
            for dd in dl.find_all('dd', attrs = {'id' : 'authors'}):
                rec['auts'] = []
                for li in dd.find_all('li'):
                    email = False
                    for sup in li.find_all('sup'):
                        aff = re.sub('.*\((.*)\).*', r'\1', sup.text.strip())
                        sup.replace_with(',,=Aff%s' % (aff))
                    for a in li.find_all('a'):
                        for img in a.find_all('img'):
                            if re.search('@', img['title']):
                                email = img['title']
                                a.replace_with('')
                    autaff = re.split(' *,, *', re.sub('[\n\t]', '', li.text.strip()))
                    author = autaff[0]
                    if email:
                         rec['auts'].append(re.sub(' *(.*) (.*)', r'\2, \1', author) + ', EMAIL:%s' % (email))
                    else:
                         rec['auts'].append(re.sub(' *(.*) (.*)', r'\2, \1', author))
                    if len(autaff) > 1:
                        rec['auts'] += autaff[1:]
            #Affiliations
            for dd in dl.find_all('dd', attrs = {'class' : 'definition-description author-affiliation'}):
                rec['aff'] = []
                for li in dd.find_all('li'):
                    aff = re.sub('[\n\t]', ' ', li.text.strip())
                    aff = re.sub('  +', ' ', aff).strip()
                    rec['aff'].append(re.sub('^(\d.*?) (.*)', r'Aff\1= \2', aff))
        #Abstract
        if not 'abs' in list(rec.keys()):
            for div in artpage.body.find_all('div', attrs = {'class' : 'section__content'}):
                for p in div.find_all('p'):
                    rec['abs'] = p.text.strip()


    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')

