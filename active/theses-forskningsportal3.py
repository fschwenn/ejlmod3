# -*- coding: UTF-8 -*-
#program to harvest theses from national repository forskningsportal.dk
# FS 2022.07.16
# FS 2023-03-17

import sys
import os
from bs4 import BeautifulSoup
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#import undetected_chromedriver as uc
import re
import ejlmod3
import time
import json

publisher = 'Danish National Research Database'
jnlfilename = 'THESES-FORSKNINGSPORTAL-%s' % (ejlmod3.stampoftoday())
pages = 20
skipalreadyharvested = True
boring = ['Aalborg University, The Faculty of Engineering and Science, Department of Chemistry and Bioscience, Environmental Biology Monitoring',
          'Aalborg University, The Faculty of Engineering and Science, Department of the Built Environment',
          'Aalborg University, The Faculty of Engineering and Science, Department of the Built Environment, Sustainable Cities and Everyday Practice Research Group',
          'Aalborg University, The Faculty of Engineering and Science, Department of the Built Environment, Technology Organisation and Circular Construction Research Group',
          'Aalborg University, The Faculty of Engineering and Science, Department of the Built Environment, Transformation of Housing and Places Research Group',
          'Aalborg University, The Faculty of Engineering and Science, Department of the Built Environment, Universal Design Research Group',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Architecture, Design and Media Technology',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Architecture, Design and Media Technology, Urban Design – transformation &amp; mobilities',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Sustainability and Planning, Center for Design, Innovation and Sustainable Transitions',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Sustainability and Planning, Centre for Blue Governance',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Sustainability and Planning, Design for Sustainability',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Sustainability and Planning',
          'Aalborg University, The Technical Faculty of IT and Design, Department of Sustainability and Planning, Sustainable Energy Planning Research Group',
          'Aarhus University, Health, Department of Clinical Medicine, Department of Clinical Medicine - Department of Obstetrics and Gynaecology',
          'Aarhus University, Interfaculty Centre, Centre for Educational Development - CED, Centre for Educational Development - CED - Programme Development',
          'Aarhus University, Interfaculty Centre, Centre for Educational Development - CED',
          'Aarhus University, Natural Sciences, Arctic Research Centre, Arctic Research Centre - Arctic Research Centre, Silkeborg',
          'Aarhus University, Natural Sciences, Arctic Research Centre',
          'Aarhus University, Natural Sciences, Department of Biology, Department of Biology - Aquatic Biology',
          'Aarhus University, Natural Sciences, Department of Biology, Department of Biology - Center for Electromicrobiology',
          'Aarhus University, Natural Sciences, Department of Biology, Department of Biology - Ecoinformatics and Biodiversity',
          'Aarhus University, Natural Sciences, Department of Biology, Department of Biology - Genetics, Ecology and Evolution',
          'Aarhus University, Natural Sciences, Department of Biology, Department of Biology - Microbiology',
          'Aarhus University, Natural Sciences, Department of Biology, Department of Biology - Zoophysiology',
          'Aarhus University, Natural Sciences, Department of Chemistry, Department of Chemistry',
          'Aarhus University, Natural Sciences, Department of Chemistry',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics, Department of Molecular Biology and Genetics - Bioinformatics Research Centre (BiRC)',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics, Department of Molecular Biology and Genetics - Cellular Health, Intervention, and Nutrition',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics, Department of Molecular Biology and Genetics - Neurobiology',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics, Department of Molecular Biology and Genetics - Plant Molecular Biology',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics, Department of Molecular Biology and Genetics - Protein Science',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics, Department of Molecular Biology and Genetics - RNA Biology and Innovation',
          'Aarhus University, Natural Sciences, Department of Molecular Biology and Genetics',
          'Aarhus University, Technical Sciences, Center for Quantitative Genetics and Genomics',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Agricultural Systems and Sustainability',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Climate and Water',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Crop Health',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Entomology and Plant Pathology',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Research facilities Flakkebjerg',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Soil Fertility',
          'Aarhus University, Technical Sciences, Department of Agroecology, Department of Agroecology - Soil Physics and Hydropedology',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - ANIS Nutrition',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - ANIVET Behaviour, stress and welfare (BSW)',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - ANIVET Gut and host health (GHH)',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - ANIVET Management and Modelling (MAMO)',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - ANIVET Monogastric Nutrition (MONU)',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - ANIVET Ruminant Nutrition (RUN)',
          'Aarhus University, Technical Sciences, Department of Animal and Veterinary Sciences, Department of Animal and Veterinary Sciences - Behaviour and stressbiology',
          'Aarhus University, Technical Sciences, Department of Biological and Chemical Engineering, Department of Biological and Chemical Engineering - Environmental Engineering',
          'Aarhus University, Technical Sciences, Department of Biological and Chemical Engineering, Department of Biological and Chemical Engineering - Industrial Biotechnology - Gustav Wieds Vej 10D',
          'Aarhus University, Technical Sciences, Department of Biological and Chemical Engineering, Department of Biological and Chemical Engineering - Industrial Biotechnology',
          'Aarhus University, Technical Sciences, Department of Biological and Chemical Engineering, Department of Biological and Chemical Engineering - Medical Biotechnology',
          'Aarhus University, Technical Sciences, Department of Biological and Chemical Engineering, Department of Biological and Chemical Engineering - Process and Materials Engineering',
          'Aarhus University, Technical Sciences, Department of Civil and Architectural Engineering, Department of Civil and Architectural Engineering - Building Science',
          'Aarhus University, Technical Sciences, Department of Civil and Architectural Engineering, Department of Civil and Architectural Engineering - Design and Construction',
          'Aarhus University, Technical Sciences, Department of Civil and Architectural Engineering, Department of Civil and Architectural Engineering - Structural Dynamics and Geotechnical Engineering',
          'Aarhus University, Technical Sciences, Department of Civil and Architectural Engineering, Department of Civil and Architectural Engineering - Structural Engineering',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Applied Marine Ecology and Modelling',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Arctic Ecosystem Ecology',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Arctic Environment',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Biodiversity and Conservation',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Catchment Science and Environmental Management',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Lake Ecology',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Marine Ecology',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Marine Mammal Research',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Terrestrial Ecology',
          'Aarhus University, Technical Sciences, Department of Ecoscience, Department of Ecoscience - Wildlife Ecology',
          'Aarhus University, Technical Sciences, Department of Engineering, Department of Engineering - Biomechanics and Mechanobiology',
          'Aarhus University, Technical Sciences, Department of Engineering, Department of Engineering - Machine Learning and Computational Intelligence',
          'Aarhus University, Technical Sciences, Department of Environmental Science, Department of Environmental Science - Atmospheric Measurements',
          'Aarhus University, Technical Sciences, Department of Environmental Science, Department of Environmental Science - Atmospheric modeling',
          'Aarhus University, Technical Sciences, Department of Environmental Science, Department of Environmental Science - Department of Environmental Science, Environmental social science and geography, Aarhus',
          'Aarhus University, Technical Sciences, Department of Environmental Science, Department of Environmental Science - Environmental chemistry &amp; toxicology',
          'Aarhus University, Technical Sciences, Department of Environmental Science, Department of Environmental Science - Environmental Microbiology',
          'Aarhus University, Technical Sciences, Department of Environmental Science, Department of Environmental Science - Environmental social science and geography',
          'Aarhus University, Technical Sciences, Department of Environmental Science',
          'Aarhus University, Technical Sciences, Department of Food Science, Department of Food Science - Differentiated &amp; Biofunctional Foods',
          'Aarhus University, Technical Sciences, Department of Food Science, Department of Food Science - Food Chemistry',
          'Aarhus University, Technical Sciences, Department of Food Science, Department of Food Science - Food Quality Perception &amp; Society',
          'Aarhus University, Technical Sciences, Department of Food Science, Department of Food Science - Food Technology',
          'Aarhus University, Technical Sciences, Department of Food Science, Department of Food Science - Plant, Food &amp; Climate',
          'Aarhus University, Technical Sciences, Department of Food Science, Department of Food Science - Plant, Food &amp; Sustainability',
          'Aarhus University, Technical Sciences, Department of Mechanical and Production Engineering, Department of Mechanical and Production Engineering - Design and Manufacturing',
          'Aarhus University, Technical Sciences, Department of Mechanical and Production Engineering, Department of Mechanical and Production Engineering - Fluids and Energy',
          'Aarhus University, Technical Sciences, Department of Mechanical and Production Engineering',
          'Aarhus University, Technical Sciences, International Centre for Research in Organic Food Systems',
          'Aberystwyth Business School',
          'Copenhagen Business School',
          'Copenhagen University Hospital - Bispebjerg and Frederiksberg',
          'Danish Meteorological Institute',
          'Institut for Folkesundhed, Aarhus Universitet',
          'Institut for Kultur og Samfund - Forhistorisk Arkæologi, fag',
          'International Institute of Tropical Agriculture',
          'IT University of Copenhagen, Business IT',
          'IT University of Copenhagen, Digital Design',
          'Københavns Universitet, Faculty of Health and Medical Sciences, Department of Clinical Medicine, Department of Clinical Medicine',
          'Københavns Universitet, Faculty of Health and Medical Sciences, Department of Veterinary and Animal Sciences, Animal Welfare and Disease Control',
          'Københavns Universitet, Faculty of Health and Medical Sciences, Globe Institute, Section for Geobiology',
          'Københavns Universitet, Faculty of Science, Department of Biology, Biomolecular Sciences',
          'Københavns Universitet, Faculty of Science, Department of Biology, Cell and Neurobiology',
          'Københavns Universitet, Faculty of Science, Department of Biology, Cell Biology and Physiology',
          'Københavns Universitet, Faculty of Science, Department of Biology, Computational and RNA Biology',
          'Københavns Universitet, Faculty of Science, Department of Biology, Ecology and Evolution',
          'Københavns Universitet, Faculty of Science, Department of Biology, Freshwater Biology',
          'Københavns Universitet, Faculty of Science, Department of Biology, Functional Genomics',
          'Københavns Universitet, Faculty of Science, Department of Biology, Genome Research and Molecular Bio Medicine',
          'Københavns Universitet, Faculty of Science, Department of Biology, Microbiology',
          'Københavns Universitet, Faculty of Science, Department of Biology',
          'Københavns Universitet, Faculty of Science, Department of Biology, Terrestrial Ecology',
          'Københavns Universitet, Faculty of Science, Department of Chemistry, Department of Chemistry',
          'Københavns Universitet, Faculty of Science, Department of Food and Resource Economics, Section for Consumption, Bioethics and Governance',
          'Københavns Universitet, Faculty of Science, Department of Food and Resource Economics, Section for Environment and Natural Resources',
          'Københavns Universitet, Faculty of Science, Department of Food and Resource Economics, Section for Global Development',
          'Københavns Universitet, Faculty of Science, Department of Food and Resource Economics, Section for Production, Markets and Policy',
          'Københavns Universitet, Faculty of Science, Department of Food Science, Design and Consumer Behavior',
          'Københavns Universitet, Faculty of Science, Department of Food Science, Food Analytics and Biotechnology',
          'Københavns Universitet, Faculty of Science, Department of Food Science, Ingredient and Dairy Technology',
          'Københavns Universitet, Faculty of Science, Department of Food Science, Microbiology and Fermentation',
          'Københavns Universitet, Faculty of Science, Department of Geosciences and Natural Resource Management, Forest, Nature and Biomass',
          'Københavns Universitet, Faculty of Science, Department of Geosciences and Natural Resource Management, Geography',
          'Københavns Universitet, Faculty of Science, Department of Geosciences and Natural Resource Management, Geology',
          'Københavns Universitet, Faculty of Science, Department of Geosciences and Natural Resource Management, Landscape Architecture and Planning',
          'Københavns Universitet, Faculty of Science, Department of Geosciences and Natural Resource Management, Landscape Architecture and Urbanism',
          'Københavns Universitet, Faculty of Science, Department of Nutrition, Exercise and Sports, Lifecourse Nutrition &amp; Health',
          'Københavns Universitet, Faculty of Science, Department of Nutrition, Exercise and Sports, Movement and Neuroscience',
          'Københavns Universitet, Faculty of Science, Department of Nutrition, Exercise and Sports, Nutrition and Health',
          'Københavns Universitet, Faculty of Science, Department of Nutrition, Exercise and Sports, Sport, Individual &amp; Society',
          'Københavns Universitet, Faculty of Science, Department of Nutrition, Exercise and Sports, The August Krogh Section for Human Physiology',
          'Københavns Universitet, Faculty of Science, Department of Nutrition, Exercise and Sports, The August Krogh Section for Molecular Physiology',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Microbial Ecology and Biotechnology',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Crop Sciences',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Environmental Chemistry and Physics',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Molecular Plant Biology',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Organismal Biology',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Plant and Soil Sciences',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Plant Biochemistry',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Plant Glycobiology',
          'Københavns Universitet, Faculty of Science, Department of Plant and Environmental Sciences, Section for Transport Biology',
          'Københavns Universitet, Faculty of Science, Department of Science Education, Science Communication',
          'Københavns Universitet, Faculty of Science, Department of Science Education',
          'Københavns Universitet, Faculty of Science, Niels Bohr Institute, Biocomplexity',
          'Københavns Universitet, Faculty of Science, Niels Bohr Institute, Climate and Geophysics',
          'Københavns Universitet, Faculty of Science, Niels Bohr Institute, Physics of Ice, Climate and Earth',
          'Københavns Universitet, Faculty of Science, The Natural History Museum, Administration and operations',
          'Københavns Universitet, Faculty of Science, The Natural History Museum, Exhibitions and Visitors Experience',
          'Københavns Universitet, Faculty of Science, The Natural History Museum, Research',
          'Københavns Universitet, Faculty of Science, The Natural History Museum',
          'Københavns Universitet, Faculty of Social Sciences, Department of Economics, Department of Economics',
          'Københavns Universitet, Faculty of Social Sciences, Department of Sociology, Department of Sociology',
          'Roskilde University, Department of People and Technology, Mobility, Space, Place and Urban Studies (MOSPUS)',
          'Roskilde University, Department of People and Technology',
          'Roskilde University, Department of Science and Environment, Environmental Dynamics',
          'Roskilde University, Department of Science and Environment, Glass and Time',
          'Roskilde University, Department of Science and Environment, Molecular and Medical Biology',
          'Roskilde University, Department of Science and Environment, PandemiX Center',
          'SDU, Faculty of Science, Department of Biochemistry and Molecular Biology, Biomedical Mass Spectrometry and Systems Biology',
          'SDU, Faculty of Science, Department of Biology, Ecology',
          'Technical University of Denmark, Centers, Center for Electric Power and Energy',
          'Technical University of Denmark, Centers, Center for Energy Resources Engineering',
          'Technical University of Denmark, Centers, Center for Microbial Secondary Metabolites',
          'Technical University of Denmark, Centers, DTU Microbes Initiative',
          'Technical University of Denmark, Centers, VISION – Center for Visualizing Catalytic Processes',
          'Technical University of Denmark, Centre for Technology Entrepreneurship',
          'Technical University of Denmark, Danish Offshore Technology Centre',
          'Technical University of Denmark, Department of Biotechnology and Biomedicine, Center for Antibody Technologies',
          'Technical University of Denmark, Department of Biotechnology and Biomedicine, Section for Microbial and Chemical Ecology, Bacterial Interactions and Evolution',
          'Technical University of Denmark, Department of Biotechnology and Biomedicine, Section for Protein Chemistry and Enzyme Technology, Lignin Biotechnology',
          'Technical University of Denmark, Department of Biotechnology and Biomedicine, Section for Protein Science and Biotherapeutics, Mammalian Cell Line Engineering',
          'Technical University of Denmark, Department of Biotechnology and Biomedicine, Section for Protein Science and Biotherapeutics, Protease Systems Biology',
          'Technical University of Denmark, Department of Biotechnology and Biomedicine',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, Bio Conversions',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, CERE – Center for Energy Ressources Engineering',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, CHEC Research Centre',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, KT Consortium',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, PROSYS - Process and Systems Engineering Centre',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, The Danish Polymer Centre',
          'Technical University of Denmark, Department of Chemical and Biochemical Engineering, The Hempel Foundation Coatings Science and Technology Centre (CoaST)',
          'Technical University of Denmark, Department of Chemistry, Organic and Inorganic Chemistry',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Energy and Services',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Fluid Mechanics, Coastal and Maritime Engineering',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Manufacturing Engineering',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Materials and Surface Engineering',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Solid Mechanics',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Structures and Safety',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering',
          'Technical University of Denmark, Department of Civil and Mechanical Engineering, Thermal Energy',
          'Technical University of Denmark, Department of Energy Conversion and Storage, Atomic Scale Materials Modelling',
          'Technical University of Denmark, Department of Energy Conversion and Storage, Continuum Modelling and Testing',
          'Technical University of Denmark, Department of Energy Conversion and Storage, Functional Oxides',
          'Technical University of Denmark, Department of Energy Conversion and Storage, Imaging and Structural Analysis',
          'Technical University of Denmark, Department of Energy Conversion and Storage, Solid State Chemistry',
          'Technical University of Denmark, Department of Energy Conversion and Storage',
          'Technical University of Denmark, Department of Engineering Technology and Didactics, Strategy and Leadership Development',
          'Technical University of Denmark, Department of Environmental and Resource Engineering, Circularity &amp; Environmental Impact',
          'Technical University of Denmark, Department of Environmental and Resource Engineering, Climate &amp; Monitoring',
          'Technical University of Denmark, Department of Environmental and Resource Engineering, Geotechnics &amp; Geology',
          'Technical University of Denmark, Department of Environmental and Resource Engineering, Materials &amp; Durability',
          'Technical University of Denmark, Department of Environmental and Resource Engineering, Quantitative Sustainability Assessment',
          'Technical University of Denmark, Department of Environmental and Resource Engineering',
          'Technical University of Denmark, Department of Environmental and Resource Engineering, Water Technology &amp; Processes',
          'Technical University of Denmark, Department of Environmental Engineering, Climate &amp; Monitoring',
          'Technical University of Denmark, Department of Health Technology, Bioinformatics, Cancer Systems Biology',
          'Technical University of Denmark, Department of Health Technology, Bioinformatics, Immunoinformatics and Machine Learning',
          'Technical University of Denmark, Department of Health Technology, Bioinformatics',
          'Technical University of Denmark, Department of Health Technology, Biomimetics, Engineered Fluidics and Tissues',
          'Technical University of Denmark, Department of Health Technology, Biotherapeutic Engineering and Drug Targeting, Biomimetics, Biocarriers and Bioimplants',
          'Technical University of Denmark, Department of Health Technology, Biotherapeutic Engineering and Drug Targeting, Ocular Drug Delivery',
          'Technical University of Denmark, Department of Health Technology, Biotherapeutic Engineering and Drug Targeting',
          'Technical University of Denmark, Department of Health Technology, Biotherapeutic Engineering and Drug Targeting, Tailored Materials and Tissues',
          'Technical University of Denmark, Department of Health Technology, Digital Health, Biomedical Signal Processing &amp; AI',
          'Technical University of Denmark, Department of Health Technology, Digital Health, Brain Computer Interface',
          'Technical University of Denmark, Department of Health Technology, Digital Health, Personalized Health Technology',
          'Technical University of Denmark, Department of Health Technology, Drug Delivery and Sensing',
          'Technical University of Denmark, Department of Health Technology, Experimental &amp; Translational Immunology',
          'Technical University of Denmark, Department of Health Technology, Experimental &amp; Translational Immunology, T-cell antigens and Immunogenicity',
          'Technical University of Denmark, Department of Health Technology, Experimental &amp; Translational Immunology, T-Cells and Cancer',
          'Technical University of Denmark, Department of Health Technology, Hearing Systems Section, Computational auditory modeling',
          'Technical University of Denmark, Department of Health Technology, Hearing Systems Section',
          'Technical University of Denmark, Department of Health Technology, Hevesy and Dosimetry, Dosimetry',
          'Technical University of Denmark, Department of Health Technology, Magnetic Resonance, Medical Image Computing',
          'Technical University of Denmark, Department of Health Technology, Magnetic Resonance, MRI Acquisition',
          'Technical University of Denmark, Department of Health Technology, Medical Isotopes and Dosimetry, Dosimetry',
          'Technical University of Denmark, Department of Health Technology, Optical Sensing and Imaging Systems, Fluidic Array Systems and Technology',
          'Technical University of Denmark, Department of Health Technology, Optical Sensing and Imaging Systems, Nanofluidics and Bioimaging',
          'Technical University of Denmark, Department of Health Technology, Optical Sensing and Imaging Systems',
          'Technical University of Denmark, Department of Health Technology, Section for Cell and Drug Technologies, Colloids &amp; Biological Interfaces',
          'Technical University of Denmark, Department of Health Technology',
          'Technical University of Denmark, Department of Health Technology, UltraSound and Biomechanics, Cardiovascular Biomechanics',
          'Technical University of Denmark, Department of Health Technology, UltraSound and Biomechanics, Center for Fast Ultrasound Imaging',
          'Technical University of Denmark, Department of Photonics Engineering, Structured Electromagnetic Materials',
          'Technical University of Denmark, Department of Photonics Engineering, Ultra-fast Optical Communication',
          'Technical University of Denmark, Department of Physics',
          'Technical University of Denmark, Department of Physics, Surface Physics and Catalysis',
          'Technical University of Denmark, Department of Technology, Management and Economics, Management Science, Operations and Supply Chain Management',
          'Technical University of Denmark, Department of Technology, Management and Economics, Management Science, Operations Management',
          'Technical University of Denmark, Department of Technology, Management and Economics, Management Science, Operations Research',
          'Technical University of Denmark, Department of Technology, Management and Economics',
          'Technical University of Denmark, Department of Technology, Management and Economics, Sustainability, Society and Economics, Climate Economics and Risk Management',
          'Technical University of Denmark, Department of Technology, Management and Economics, Technology and Business Studies, Human-Centered Innovation',
          'Technical University of Denmark, Department of Technology, Management and Economics, Transport',
          'Technical University of Denmark, Department of Wind and Energy Systems, Power and Energy Systems',
          'Technical University of Denmark, Department of Wind and Energy Systems',
          'Technical University of Denmark, Department of Wind and Energy Systems, Wind Energy Materials and Components Division',
          'Technical University of Denmark, Department of Wind and Energy Systems, Wind Energy Systems Division',
          'Technical University of Denmark, Department of Wind and Energy Systems, Wind Turbine Design Division',
          'Technical University of Denmark, Department of Wind Energy, Wind Energy Materials and Components Division',
          'Technical University of Denmark, Department of Wind Energy, Wind Energy Systems Division, GRID Integration and Energy Systems',
          'Technical University of Denmark, National Centre for Nano Fabrication and Characterization, Nanocharacterization, Molecular Windows',
          'Technical University of Denmark, National Centre for Nano Fabrication and Characterization, Nanofabrication, Biomaterial Microsystems',
          'Technical University of Denmark, National Centre for Nano Fabrication and Characterization, Nanofabrication',
          'Technical University of Denmark, National Centre for Nano Fabrication and Characterization',
          'Technical University of Denmark, National Food Institute, Research Group for Analytical Food Chemistry',
          'Technical University of Denmark, National Food Institute, Research Group for Food Allergy',
          'Technical University of Denmark, National Food Institute, Research Group for Foodborne Pathogens and Epidemiology',
          'Technical University of Denmark, National Food Institute, Research Group for Food Microbiology and Hygiene',
          'Technical University of Denmark, National Food Institute, Research Group for Global Capacity Building',
          'Technical University of Denmark, National Food Institute, Research Group for Gut, Microbes and Health',
          'Technical University of Denmark, National Food Institute, Research Group for Microbial Biotechnology and Biorefining',
          'Technical University of Denmark, National Food Institute, Research Group for Molecular and Reproductive Toxicology',
          'Technical University of Denmark, National Food Institute, Research Group for Nutrition, Sustainability and Health Promotion',
          'Technical University of Denmark, National Food Institute, Research Group for Risk Benefit',
          'Technical University of Denmark, National Food Institute',
          'Technical University of Denmark, National Institute of Aquatic Resources, Centre for Ocean Life',
          'Technical University of Denmark, National Institute of Aquatic Resources, Section for Aquaculture',
          'Technical University of Denmark, National Institute of Aquatic Resources, Section for Oceans and Arctic',
          'Technical University of Denmark, National Institute of Aquatic Resources',
          'Technical University of Denmark, Novo Nordisk Foundation Center for Biosustainability, Bacterial Cell Factories',
          'Technical University of Denmark, Novo Nordisk Foundation Center for Biosustainability, Flux Optimisation and Bioanalytics',
          'Technical University of Denmark, Novo Nordisk Foundation Center for Biosustainability, Genome Engineering',
          'Technical University of Denmark, Novo Nordisk Foundation Center for Biosustainability']
factofc = {'Københavns Universitet, Faculty of Science, Niels Bohr Institute, Experimental Particle Physics' : 'e',
           'Københavns Universitet, Faculty of Science, Niels Bohr Institute, Condensed Matter Physics' : 'f',
           'Københavns Universitet, Faculty of Science, Niels Bohr Institute, Theoretical high energy, astroparticle and gravitational physics' : 't',
           'Technical University of Denmark, Department of Physics, Quantum Physics and Information Techology' : 'k',
           'Aarhus University, Natural Sciences, Department of Mathematics, Department of Mathematics - Science Studies' : 'm',
           'Aarhus University, Natural Sciences, Department of Mathematics' : 'm',
           'Københavns Universitet, Faculty of Science, Department of Mathematical Sciences' : 'm',
           'Aarhus University, Natural Sciences, Department of Computer Science' : 'c',
           'IT University of Copenhagen, Computer Science, Robotics, Evolution, and Art Lab (REAL)' : 'c',
           'IT University of Copenhagen, Computer Science' : 'c',
           'Københavns Universitet, Faculty of Science, Department of Computer Science, Algorithms and Complexity' : 'c',
           'Københavns Universitet, Faculty of Science, Department of Computer Science, Image Analysis, Computational Modelling and Geometry' : 'c',
           'Københavns Universitet, Faculty of Science, Department of Computer Science, Machine Learning' : 'c',
           'Københavns Universitet, Faculty of Science, Department of Computer Science, Natural Language Processing' : 'c',
           'Københavns Universitet, Faculty of Science, Department of Computer Science, Programming Languages and Theory of Computing' : 'c',
           'Københavns Universitet, Faculty of Science, Department of Computer Science, Software, Data, People &amp; Society' : 'c'}

publisherdata = '/afs/desy.de/group/library/publisherdata/nora'

#options = uc.ChromeOptions()
#options.add_argument('--headless')
#options.binary_location='/opt/google/chrome/google-chrome'
#options.binary_location='/usr/bin/chromium'
#chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
#driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for year in [ejlmod3.year(backwards=1), ejlmod3.year()]:
    recs = []
    jnlfilename = 'THESES-FORSKNINGSPORTAL-%s_%i' % (ejlmod3.stampoftoday(), year)
    os.system('wget -q -O %s/nora-data-all-%i.json.gz https://local.forskningsportal.dk/local-data/extract/%s/json/nora-data-all-%i.json.gz' % (publisherdata, year, ejlmod3.stampoftoday()[:7], year))
    time.sleep(25)
    os.system('cd %s && gunzip nora-data-all-%i.json.gz' % (publisherdata, year))

    inf = open('%s/nora-data-all-%i.json' % (publisherdata, year), 'r')
    data = json.load(inf)
    inf.close()
    for record in data:
        keepit = True
        #print(record)
        #print('------\n')
        rec = {'year' : str(year), 'isbns' : [], 'note' : [], 'rn' : [], 'jnl' : 'BOOK',
               'auts' : [], 'aff' : [], 'tc' : 'T'}


        #type
        if 'type' in record:
            if record['type'] in ['Book Chapter', 'Book Preface, Encycl. Entry',
                                  'Book', 'Conference Paper', 'Journal Article',
                                  'Journal Review', 'Patent', 'Working Paper, (pr)eprint',
                                  'Conference Abstract', 'Conference Poster', 'Journal Comment',
                                  'Lecture Notes', 'Other-Internet Publication', 'Other',
                                  'Other-Unknown', 'Report', 'Data Set', 'Journal Book Review',
                                  'Newspaper Article', 'Report Chapter', 'Software']:
                keepit = False
            elif not record['type'] in ['Thesis Doctoral', 'Thesis PhD']:
                rec['note'].append('TYPE:::' + record['type'])
        #title
        if 'title' in record:
            rec['tit'] = record['title']
        #abstract
        if 'abstract' in record:
            rec['abs'] = record['abstract']
        #pubnote
        if 'pub' in record:
            #DOI
            if 'doi' in record['pub']:
                rec['doi'] = record['pub']['doi']
            #ISBN
            if 'eisbn' in record['pub']:
                for isbn in record['pub']['eisbn']:
                    rec['isbns'].append([('a', isbn), ('b', 'ebook')])
            if 'isbn' in record['pub']:
                for isbn in record['pub']['isbn']:
                    rec['isbns'].append([('a', isbn), ('b', 'print')])
            #report number
            if 'repno' in record['pub']:
                rec['rn'] = record['pub']['repno']
            #journal stuff
            if 'title' in record['pub']:
                rec['jnl'] = record['pub']['title']
            if 'issue' in record['pub']:
                rec['issue'] = record['pub']['issue']
            if 'volume' in record['pub']:
                rec['vol'] = record['pub']['volume']
            if 'pages' in record['pub']:
                rec['p1'] = re.sub('\-.*', '', record['pub']['pages'])
                rec['p2'] = re.sub('.*\-', '', record['pub']['pages'])
        #year
        if 'year' in record:
            rec['year'] = str(record['year'])
        #author/affiliation
        if 'person' in record:
            for person in record['person']:
                if 'name' in person:
                    author = person['name']
                elif 'last' in person and 'first' in person:
                    author = person['last'] + ', ' + person['first']
                else:
                    print('author????')
                    author = 'Doe, John'
                if 'orcid' in person:
                    author += ', ORCID:' + person['orcid']
                rec['auts'].append(author)
                if 'affno' in person:
                    rec['auts'].append('=Aff' + person['affno'])
        if 'org' in record:
            for org in record['org']:
                if org['name'] in boring:
                    keepit = False
                    #print('  skip "%s"' % (org['name']))
                elif org['name'] in factofc:
                    rec['fc'] = factofc[org['name']]                          
                if 'affno' in org:
                    rec['aff'].append('Aff%s= %s' % (org['affno'], org['name']))
                else:
                    rec['aff'].append(org['name'])
        #FFT
        if 'oa_link' in record:
            for oal in  record['oa_link']:
                if 'url' in oal:
                    rec['pdf_url'] = oal['url']
                if 'license' in oal:
                    if re.search('creativecommons.org', oal['license']):
                        rec['license'] = {'url' : oal['license']}
                    elif re.search('^CC[ \-]BY', oal['license']):
                        rec['license'] = {'statement' : oal['license']}
                    else:
                        rec['note'].append('LICENSE:::' + oal['license'])            
        #language
        if 'lang' in record:
            rec['language'] = record['lang']
        #keywords
        if 'keyword' in record:
            rec['keyw'] = record['keyword']
        #filtes
        if 'filters' in record:
            if 'oa' in record['filters']:
                rec['note'].append('OA:::' + record['filters']['oa'])
            #if 'org' in record['filters']:
            #    for level in ['level1', 'level2', 'level3']:
            #        if level in record['filters']['org']:
            #            for lvt in record['filters']['org'][level]:
            #                rec['note'].append(level.upper() + ':::' + lvt)
            #if 'type' in record['filters']:
            #    rec['note'].append('FILTERSTYPE:::' + record['filters']['type'])
            if 'mra' in record['filters']:
                if record['filters']['mra'] in ['hum', 'soc', 'med']:
                    keepit = False
                else:
                    rec['note'].append('MRA:::' + record['filters']['mra'])
                                

        #link
        if 'id' in record:
            rec['artlink'] = 'https://local.forskningsportal.dk/search/1/%s' % (record['id'])
            if not 'doi' in rec:
                rec['doi'] = '30.3000/NORA/' + re.sub('\W', '', record['id'])

        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            keepit = False

        if keepit:
            recs.append(rec)

#        if len(recs) > 100:
#            break

    ejlmod3.writenewXML(recs, publisher, jnlfilename)
    os.system('mv %s/nora-data-all-%i.json %s/done' % (publisherdata, year, publisherdata))


