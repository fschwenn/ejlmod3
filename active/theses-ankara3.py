# -*- coding: utf-8 -*-
#harvest theses from Ankara U.
#FS: 2022-03-05
#FS: 2023-02-24

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc


rpp = 50
pages = 5
skipalreadyharvested = True

publisher = 'Ankara U.'
jnlfilename = 'THESES-ANKARA-%s' % (ejlmod3.stampoftoday())

options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

boringfacs = ['Sosyal Bilimleri Enstitüsü', 'Arkeoloji Ana Bilim Dalı', 'Bilgisayar ve Öğretim Teknolojileri Eğitimi Ana Bilim Dalı',
              'Bilgi ve Belge Yönetimi', 'Biyoloji Ana Bilim Dalı', 'Çalışma Ekonomisi ve Endüstri İlişkileri Ana Bilim Dalı',
              'Dil ve Tarih Coğrafya Fakültesi: Bilgi ve Belge Yönetimi Bölümü', 'Dil ve Tarih Coğrafya Fakültesi', 'Felsefe',
              'Hukuk', 'İslam Tarihi ve Sanatları Ana Bilim Dalı', 'Jeoloji Mühendisliği', 'Kimya Mühendisliği Ana Bilim Dalı',
              'Kimya', 'Özel Hukuk Ana Bilim Dalı', 'Siyaset Bilimi ve Kamu Yönetimi Ana Bilim Dalı',
              'Tarım Makineleri ve Teknolojileri Mühendisliği Ana Bilim Dalı', 'Felsefe ve Din Bilimleri Ana Bilim Dalı',
              'İletişim Fakültesi', 'Tarih', 'Türk İnkılap Tarihi Enstitüsü', 'Hukuk Fakültesi', 'Mühendislik Fakültesi',
              'Ziraat Fakültesi', 'Dil ve Tarih-Coğrafya Fakültesi', 'Eğitim Bilimleri Enstitüsü', 'Eğitim Bilimleri Fakültesi',
              'Siyasal Bilgiler Fakültesi', 'İlahiyat Fakültesi', 'Bilgisayar Mühendisliği Ana Bilim Dalı',
              'Doğu Dilleri ve Edebiyatları (Sinoloji) Ana Bilim Dalı', 'Felsefe Ana Bilim Dalı', 'Gazetecilik Ana Bilim Dalı',
              'Gazetecilik Bilim Dalı', 'İslam Mezhepleri Tarihi', 'Bilgisayar Mühendisliği Ana Bilim Dalı',
              'Doğu Dilleri ve Edebiyatları (Sinoloji) Ana Bilim Dalı', 'Felsefe Ana Bilim Dalı', 'Gazetecilik Ana Bilim Dalı',
              'Gazetecilik Bilim Dalı', 'İslam Mezhepleri Tarihi', 'Peyzaj Mimarlığı Ana Bilim Dalı', 'Tefsir Bilim Dalı',
              'Yer Bilgisi: Ankara Üniversitesi / Sosyal Bilimler Enstitüsü / İslam Tarihi ve Sanatları Ana Bilim Dalı / İslam Tarihi Bilim Dalı',
              'Fen Bilimler Enstitüsü', 'Kamu Hukuku Ana Bilim Dalı', 'Tasavvuf Bilim Dalı', 'Temel İslam Bilimleri Ana Bilim Dalı',
              'Sosyal Bilimler Enstitüsü', 'Biyoloji', 'Çalışma Ekonomisi ve Endüstri İlişkileri', 'Elektrik-Elektronik Mühendisliği',
              'Gayrimenkul Geliştirme ve Yönetimi', 'Hidrobiyoloji Anabilim Dalı', 'Kimya Mühendisliği', 'Peyzaj Mimarlığı',
              'Spor Bilimleri Fakültesi', 'Tarım Makineleri ve Teknolojileri Mühendisliği', 'Tarla Bitkileri', 'Bilgisayar Mühendisliği',
              'Gıda Mühendisliği', 'Tarımsal Yapılar ve Sulama', 'Toprak Bilimi ve Bitki Besleme', 'Bitki Koruma',
              'Ankara Üniversitesi Fen Bilimleri Enstitüsü Gıda Mühendisliği Anabilim Dalı',
              'Ankara Üniversitesi Sosyal Bilimler Enstitüsü Felsefe ve Din Bilimleri (İslam Felsefesi) Ana Bilim Dalı',
              'Ankara Üniversitesi Sosyal Bilimler Enstitüsü Özel Hukuk (Medenî Usul ve İcra-İflâs Hukuku) Anabilim Dalı',
              'Beslenme ve Diyetetik Anabilim Dalı', 'Biyokimya Bilim Dalı', 'Biyoteknoloji Anabilim Dalı', 'Biyoteknoloji Bilim Dalı',
              'Botanik Anabilim Dalı', 'Çocuk Gelişimi Anabilim Dalı', 'Çocuk Gelişimi Ana Bilim Dalı',
              'Elektrik-Elektronik Mühendisliği Ana Bilim Dalı', 'Fizikokimya Bilim Dalı', 'Fonksiyonel Analiz Anabilim Dalı',
              'Gayrimenkul Geliştirme ve Yönetimi Ana Bilim Dalı', 'Jeoloji Mühendisliği Anabilim Dalı', 'Tarım Ekonomisi Anabilim Dalı',
              'Tarım Ekonomisi', 'Tarım Makineleri ve Teknolojileri Mühendisliği Anabilim Dalı', 'Tarla Bitkileri Anabilim Dalı',
              'Zootekni Anabilim Dalı', 'Anorganik Kimya Bilim Dalı', 'Gıda Mühendisliği Anabilim Dalı', 'İstatistik Ana Bilim Dalı',
              'Kimya Ana Bilim Dalı', 'Kimya Anabilim Dalı', 'Sağlık Bilimleri Fakültesi', 'Biyoloji Anabilim Dalı',
              'Ankara Üniversitesi Eğitim Bilimleri Enstitüsü Eğitimde Psikolojik Hizmetler Anabilim Dalı Rehberlik ve Psikolojik Danışma Bilim Dalı',
              'Ankara Üniversitesi Fen Bilimleri Enstitüsü Bitki Koruma Anabilim Dalı',
              'Ankara Üniversitesi Fen Bilimleri Enstitüsü Jeofizik Mühendisliği Anabilim Dalı',
              'Ankara Üniversitesi Fen Bilimleri Enstitüsü Tarım Ekonomisi Anabilim Dalı',
              'Ankara Üniversitesi Fen Bilimleri Enstitüsü Zootekni Anabilim Dalı',
              'Ankara Üniversitesi Sağlık Bilimleri Enstitüsü Endodonti Ana Bilim Dalı',
              'Ankara Üniversitesi Sağlık Bilimleri Enstitüsü Mikrobiyoloji Anabilim Dalı',
              'Ankara Üniversitesi Sosyal Bilimler Enstitüsü İktisat Anabilim Dalı',
              'Ankara Üniversitesi Sosyal Bilimler Enstitüsü Tarih Anabilim Dalı', 'Diş Hekimliği Fakültesi', 'Diş Hekimliği',
              'Eğitim Bilimleri Enstitüs', 'Eğitim Bilimleri Enstitüsü Eğitim', 'Sağlık Bilimler Enstitüsü', 'Saglık Bilimleri Enstitüsü',
              'SOSYAL BİLİMLER ENSTİTÜSÜ', 'Türk İnkılâp Tarihi Enstitüsü', 'Economiques', 'Ziraat Mühendisliği',          
              'Sağlık Bilimleri Enstitüsü']

prerecs = []
for page in range(pages):
    tocurl = 'https://dspace.ankara.edu.tr/xmlui/handle/20.500.12575/27627/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print("retry in 300 seconds")
        time.sleep(300)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(3)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'ds-artifact-item'}):
        keepit = True
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor'  : []}
        for span in div.find_all('span', attrs = {'class' : 'publisher'}):
            for fac in re.split(' : ', span.text.strip()):
                if fac in boringfacs:
                    keepit = False
                elif not fac in ['Ankara', 'Ankara Üniversitesi']:
                    rec['note'].append(fac)
        for a in div.find_all('a'):
            rec['link'] = 'https://dspace.ankara.edu.tr' + a['href']
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        if keepit and ejlmod3.checkinterestingDOI(rec['hdl']):
            if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                print('   %s already in backup' % (rec['hdl']))
            else:
                prerecs.append(rec)
    print('  %4i prerecs so far' % (len(prerecs)))

recs = []
i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:        
        driver.get(rec['link'] + '?show=full')
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            driver.get(rec['link'] + '?show=full')
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'citation_pdf_url',
                                        'citation_language', 'DCTERMS.extent'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                if re.search('\(', meta['content']):
                    if re.search('\(Yazar', meta['content']):
                        rec['autaff'] = [[ re.sub(' *\(.*', '', meta['content']), publisher ]]
                else:
                    rec['autaff'] = [[ meta['content'], publisher ]]
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ', meta['content']):
                    rec['abs'] = meta['content']
    #date
    if not 'date' in list(rec.keys()):
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_date'}):
                rec['date'] = meta['content']            
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            if label == 'dc.contributor.department':
                fac = td.text.strip()
                if fac in boringfacs:
                    keepit = False
                else:
                    rec['note'].append(fac)
            #supervisor
            elif label == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
