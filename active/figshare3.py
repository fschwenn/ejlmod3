# -*- coding: utf-8 -*-
#harvest theses from Figshare
#FS: 2022-02-15
#FS: 2022-09-01

import sys
import datetime
import requests
import time
import urllib3
import json
import re
import ejlmod3
import codecs
import os

urllib3.disable_warnings()

now = datetime.datetime.now()
startdate = '%4d-%02d-%02d' % (now.year-1, now.month, now.day)

srv = sys.argv[1]

rpp = 200
pages = 2+2 
bunchsize = 100-90
sleepingtime = 3
years = 3
skipalreadyharvested = True
skipnonlistedcategories = False
apiurl = "https://api.figshare.com/v2/articles/search"
my_secret_token = "df88e4ebd43b823b945a7e6cd4809a579ba7dee9e60ac2e5a1c18874b36d67a128d8b8b447d01fcd521d44e2a8d7128a3bf3b1fb860fb6c1f4aaf77c43dfd0d7"
auth = "Bearer %s" % (my_secret_token)

#categories with fieldcodes
cattofc = {'Uncategorized' : '',
           'Computing and Processing' : 'c',
           'Components, Circuits, Devices and Systems' : 'i',
           'Components Circuits Devices and Systems' : 'i',
           'Electronic and Magnetic Properties of Condensed Matter; Superconductivity' : 'f',
           'Software Engineering' : 'c',
           'Stellar Astronomy' : 'a',
           'Galactic Astronomy' : 'a',
           'Cosmology' : 'a',
           'Astrophysics' : 'a',
           'Crystallography' : 'f',
           'Molecular Physics' : 'q',
           'Theoretical Computer Science' : 'c',
           'Applied Computer Science' : 'c',
           'Geophysics' : 'q',
           'Nuclear Engineering' : 'i',
           'Algebra' : 'm',
           'Geometry' : 'm',
           'Probability' : 'm',
           'Statistics' : 'm',
           'Applied Physics' : 'q',
           'Atomic Physics' : 'q',
           'Computational Physics' : 'c',
           'Condensed Matter Physics' : 'f',
           'Mechanics' : 'q',
           'Particle Physics' : '',
           'Plasma Physics' : 'q',
           'Quantum Mechanics' : 'k',
           'Solid Mechanics' : 'q',
           'Thermodynamics' : 'q',
           'Entropy' : 'q',
           'General Relativity' : 'g',
           'M-Theory' : 't',
           'Special Relativity' : 'g',
           'Solar System, Solar Physics, Planets and Exoplanets' : 'a',
           'Space Science' : 'a',
           'Stars, Variable Stars' : 'a',
           'Instrumentation, Techniques, and Astronomical Observations' : 'ai',
           'Interstellar and Intergalactic Matter' : 'a',
           'Extragalactic Astronomy' : 'a',
           'Artificial Intelligence and Image Processing' : 'c',
           'Computation Theory and Mathematics' : 'cm',
           'Computer Software' : 'c',
           'Distributed Computing' : 'c',
           'Classical and Physical Optics' : 'q',
           'Nonlinear Optics and Spectroscopy' : 'q',
           'Photonics, Optoelectronics and Optical Communications' : 'q',
           'Optical Physics not elsewhere classified' : 'q',
           'Degenerate Quantum Gases and Atom Optics' : 'q',
           'Quantum Optics' : 'k',
           'Gravimetrics' : 'g',
           'Astronomical and Space Instrumentation' : 'ai',
           'Cosmology and Extragalactic Astronomy' : 'a',
           'General Relativity and Gravitational Waves' : 'g',
           'High Energy Astrophysics; Cosmic Rays' : 'a',
           'Space and Solar Physics' : 'a',
           'Stellar Astronomy and Planetary Systems' : 'a',
           'Astronomical and Space Sciences not elsewhere classified' : 'a',
           'Photodetectors, Optical Sensors and Solar Cells' : 'i',
           'Signal Processing' : 'i',
           'Signal Processing and Analysis' : 'i',
           'Algebra and Number Theory' : 'm',
           'Algebraic and Differential Geometry' : 'm',
           'Category Theory, K Theory, Homological Algebra' : 'm',
           'Combinatorics and Discrete Mathematics (excl. Physical Combinatorics)' : 'm',
           'Group Theory and Generalisations' : 'm',
           'Lie Groups, Harmonic and Fourier Analysis' : 'm',
           'Mathematical Logic, Set Theory, Lattices and Universal Algebra' : 'm',
           'Operator Algebras and Functional Analysis' : 'm',
           'Ordinary Differential Equations, Difference Equations and Dynamical Systems' : 'm',
           'Partial Differential Equations' : 'm',
           'Real and Complex Functions (incl. Several Variables)' : 'm',
           'Topology' : 'm',
           'Pure Mathematics not elsewhere classified' : 'm',
           'Approximation Theory and Asymptotic Methods' : 'm',
           'Calculus of Variations, Systems Theory and Control Theory' : 'm',
           'Dynamical Systems in Applications' : 'm',
           'Theoretical and Applied Mechanics' : 'q',
           'Applied Mathematics not elsewhere classified' : 'm',
           'Numerical Solution of Differential and Integral Equations' : 'm',
           'Optimisation' : 'm',
           'Numerical and Computational Mathematics not elsewhere classified' : 'm',
           'Applied Statistics' : 'm',
           'Probability Theory' : 'm',
           'Statistical Theory' : 'm',
           'Stochastic Analysis and Modelling' : 'm',
           'Statistics not elsewhere classified' : 'm',
           'Algebraic Structures in Mathematical Physics' : 'm',
           'Integrable Systems (Classical and Quantum)' : 'm',
           'Mathematical Aspects of Classical Mechanics, Quantum Mechanics and Quantum Information Theory' : 'm',
           'Mathematical Aspects of General Relativity' : 'gm',
           'Mathematical Aspects of Quantum and Conformal Field Theory, Quantum Gravity and String Theory' : 'mt',
           'Statistical Mechanics, Physical Combinatorics and Mathematical Aspects of Condensed Matter' : 'mf',
           'Mathematical Physics not elsewhere classified' : 'm',
           'Mathematical Sciences not elsewhere classified' : 'm',
           'Atomic and Molecular Physics' : 'q',
           'Nuclear Physics' : '',
           'Plasma Physics; Fusion Plasmas; Electrical Discharges' : 'q',
           'Atomic, Molecular, Nuclear, Particle and Plasma Physics not elsewhere classified' : 'q',
           'Electrostatics and Electrodynamics' : 'q',
           'Fluid Physics' : 'q',
           'Thermodynamics and Statistical Physics' : 's',
           'Classical Physics not elsewhere classified' : 'q',
           'Condensed Matter Characterisation Technique Development' : 'f',
           'Condensed Matter Imaging' : 'f',
           'Condensed Matter Modelling and Density Functional Theory' : 'f',
           'Electronic and Magnetic Properties of Condensed Matter; Superconductivity' : 'f',
           'Soft Condensed Matter' : 'f',
           'Surfaces and Structural Properties of Condensed Matter' : 'f',
           'Condensed Matter Physics not elsewhere classified' : 'f',
           'Lasers and Quantum Electronics' : 'k',
           'Field Theory and String Theory' : 't',
           'Quantum Information, Computation and Communication' : 'kc',
           'Quantum Physics not elsewhere classified' : 'k',
           'Complex Physical Systems' : 'q',
           'Synchrotrons; Accelerators; Instruments and Techniques' : 'bi',
           'Physical Sciences not elsewhere classified' : 'q',
           'Mathematical Software' : 'mc',
           'Numerical Computation' : 'mc',
           'Computation Theory and Mathematics not elsewhere classified' : 'mc',
           'Distributed and Grid Systems' : 'c',
           'Quantum Chemistry' : 'o'}
cattofc['Fields, Waves and Electromagnetics'] = 'q'
cattofc['Other education not elsewhere classified'] = ''
cattofc['Mathematical aspects of quantum and conformal field theory, quantum gravity and string theory'] = 't'
cattofc['Cosmology and extragalactic astronomy'] = 'a'
cattofc['Particle and high energy physics not elsewhere classified'] = ''
cattofc['Field theory and string theory'] = 't'
cattofc['Condensed matter physics not elsewhere classified'] = 'f'
cattofc['Quantum information, computation and communication'] = 'k'
cattofc['Quantum physics not elsewhere classified'] = 'k'
cattofc['Stellar astronomy and planetary systems'] = 'a'
cattofc['General relativity and gravitational waves'] = 'g'
cattofc['Foundations of quantum mechanics'] = 'k'
cattofc['Other physical sciences not elsewhere classified'] = 'q'
cattofc['Photonics, optoelectronics and optical communications'] = 'q'
cattofc['Analysis of Algorithms and Complexity'] = 'm'
cattofc['Information and Computing Sciences not elsewhere classified'] = 'c'
cattofc['Numerical Analysis'] = 'm'
cattofc['Sensory Systems'] = 'i'
cattofc['Simulation and Modelling'] = ''
cattofc['Astroparticle physics and particle cosmology'] = 'a'
cattofc['High energy astrophysics and galactic cosmic rays'] = 'a'
cattofc['Nuclear physics'] = ''
cattofc['Quantum computation'] = 'kc'


uncategories = ['Aboriginal and Torres Strait Islander Information and Knowledge Systems', 'Acoustics and acoustical devices; waves',
                'Additive manufacturing', 'Adversarial machine learning', 'Adverse weather events', 
                'Aerodynamics (excl. hypersonic aerodynamics)', 'Aerospace engineering not elsewhere classified',
                'Aerospace materials', 'Aerospace structures', 'Affective computing', 'Aged Care Nursing', 'Aged health care',
                'Agricultural biotechnology not elsewhere classified', 'Agricultural Biotechnology not elsewhere classified',
                'Agricultural engineering', 'Agricultural hydrology', 'Agricultural Land Management',
                'Agricultural management of nutrients', 'Agricultural production systems simulation',
                'Agricultural spatial analysis and modelling', 'Agricultural systems analysis and modelling',
                'Agriculture, land and farm management not elsewhere classified', 'Agrochemicals and biocides (incl. application)',
                'Agro-ecosystem function and prediction', 'Agronomy', 'Aircraft performance and flight control systems',
                'Aircraft Performance and Flight Control Systems', 'Air pollution modelling and control', 'Allergy',
                'Analog electronics and interfaces', 'Analytical Biochemistry', 'Analytical chemistry not elsewhere classified',
                'Analytical Chemistry not elsewhere classified', 'Analytical spectrometry', 'Analytical Spectrometry',
                'Animal behaviour', 'Animal cell and molecular biology', 'Animal Cell and Molecular Biology',
                'Animal developmental and reproductive biology', 'Animal growth and development', 'Animal immunology',
                'Animal management', 'Animal neurobiology', 'Animal nutrition', 'Animal physiology - biophysics',
                'Animal physiology - cell', 'Animal Physiology - Cell', 'Animal physiology - systems', 
                'Animal protection (incl. pests and pathogens)', 'Animal Reproduction', 'Animal reproduction and breeding',
                'Animal systematics and taxonomy', 'Animal welfare', 'Antennas and propagation', 'Anthropology not elsewhere classified',
                'Applications in health', 'Applications in life sciences', 'Applications in physical sciences',
                'Applied computing not elsewhere classified', 'Applied economics not elsewhere classified',
                'Applied Economics not elsewhere classified', 'Applied Ethics not elsewhere classified', 'Applied geophysics',
                'Applied linguistics and educational linguistics', 'Applied Linguistics and Educational Linguistics', 'Aquaculture',
                'Architectural Design', 'Architectural engineering', 'Architectural Heritage and Conservation',                
                'Architectural Science and Technology (incl. Acoustics, Lighting, Structure and Ecologically Sustainable Design)',
                'Architectural History and Theory', 'Architecture Management', 'Architecture not elsewhere classified',
                'Artificial Intelligence and Image Processing not elsewhere classified',
                'Artificial intelligence not elsewhere classified', 'Asian Cultural Studies', 'Asian History', 'Atmospheric Aerosols',
                'Atmospheric radiation', 'Atmospheric Sciences not elsewhere classified', 'Audio processing', 'Autoimmunity',
                'Automated software engineering', 'Automation and Control Engineering',
                'Automation and technology in building and construction', 'Automation engineering',
                'Automotive combustion and fuel engineering', 'Autonomic nervous system', 'Autonomous Vehicles',
                'Autonomous vehicle systems', 'Bacteriology', 'Basic pharmacology', 'Behavioural economics', 'Behavioural genetics',
                'Behavioural neuroscience', 'Bioassays', 'Biochemistry and cell biology not elsewhere classified',
                'Biochemistry and Cell Biology not elsewhere classified', 'Biofabrication', 'Bio-fluids',
                'Bioinformatic methods development', 'Bioinformatics', 'Bioinformatics and computational biology not elsewhere classified',
                'Biological control', 'Biologically active molecules', 'Biologically Active Molecules', 'Biological mathematics',
                'Biological (physical) anthropology', 'Biological physics',
                'Biological Psychology (Neuropsychology, Psychopharmacology, Physiological Psychology)',
                'Biological psychology not elsewhere classified', 'Biomaterials', 'Biomechanical engineering', 'Biomechanics',
                'Biomedical engineering not elsewhere classified', 'Biomedical fluid mechanics', 'Biomedical imaging',
                'Biomedical instrumentation', 'Biomolecular modelling and design', 'Biostatistics', 'British and Irish literature',
                'British history', 'Building construction management and project planning', 'Building science, technologies and systems',
                'Built Environment and Design not elsewhere classified', 'Business and Management not elsewhere classified',
                'Business information systems', 'Business systems in context', 'CAD/CAM systems', 'Cancer cell biology',
                'Cancer Cell Biology', 'Carbon sequestration science', 'Carbon Sequestration Science',
                'Cardiology (incl. cardiovascular diseases)', 'Cardiology (incl. Cardiovascular Diseases)',
                'Catalysis and mechanisms of reactions', 'Causes and Prevention of Crime', 'Cell development, proliferation and death',
                'Cell metabolism', 'Cell Metabolism', 'Cell neurochemistry', 'Cell Neurochemistry', 'Cell physiology',
                'Cellular immunology', 'Cellular interactions (incl. adhesion, matrix, cell wall)', 'Central nervous system',
                'Central Nervous System', 'Ceramics', 'Characterisation of biological macromolecules',
                'Characterisation of Biological Macromolecules', 'Chemical and thermal processes in energy and combustion',
                'Chemical engineering design', 'Chemical engineering not elsewhere classified',
                'Chemical Sciences not elsewhere classified', 'Chemical thermodynamics and energetics',
                'Cheminformatics and quantitative structure-activity relationships', 'Chemotherapy', 'Child and adolescent development',
                'Child language acquisition', 'Chinese Languages', 'Cinema Studies', 'Citizenship',
                'Civil engineering not elsewhere classified', 'Civil geotechnical engineering', 'Classical Greek and Roman History',
                'Climate Change Processes', 'Climate change science not elsewhere classified', 'Climatology (excl. Climate Change Processes)',
                'Clinical microbiology', 'Clinical Nursing: Primary (Preventative)', 'Clinical nutrition',
                'Clinical pharmacology and therapeutics', 'Clinical pharmacy and pharmacy practice',
                'Coding, information theory and compression', 'Cognition', 'Cognitive and computational psychology not elsewhere classified',
                'Cognitive neuroscience', 'Colloid and surface chemistry', 'Colloid and Surface Chemistry',
                'Combinatorics and discrete mathematics (excl. physical combinatorics)',
                'Communication and Media Studies not elsewhere classified', 'Communications and media policy', 'Communication studies',
                'Communication technology and digital media studies', 'Communication Technology and Digital Media Studies',
                'Community Child Health', 'Community Ecology (excl. Invasive Species Ecology)', 'Community Planning',
                'Comparative and transnational literature', 'Comparative Government and Politics', 'Comparative Literature Studies',
                'Complex systems', 'Composite and hybrid materials', 'Compound semiconductors', 'Computational chemistry',
                'Computational imaging', 'Computational linguistics', 'Digital and Interaction Design',
                'Computational methods in fluid flow, heat and mass transfer (incl. computational fluid dynamics)',
                'Computational neuroscience (incl. mathematical neuroscience and theoretical neuroscience)', 'Computational physiology',
                'Computer aided design', 'Computer gaming and animation', 'Computer Gaming and Animation', 'Computer graphics',
                'Computer Graphics', 'Computer Perception, Memory and Attention', 'Computer vision', 'Computer Vision',
                'Computer vision and multimedia computation not elsewhere classified', 'Concurrent/parallel systems and technologies',
                'Conservation and Biodiversity', 'Construction engineering', 'Consumer behaviour',
                'Consumer-Oriented Product or Service Development', 'Context learning', 'Control engineering',
                'Control engineering, mechatronics and robotics not elsewhere classified',
                'Correctional Theory, Offender Treatment and Rehabilitation', 'Counselling, Welfare and Community Services',
                'Creative arts, media and communication curriculum and pedagogy', 'Criminological Theories',
                'Criminology not elsewhere classified', 'Critical theory', 'Crop and pasture nutrition',
                'Crop and pasture protection (incl. pests, diseases and weeds)', 'Cross-sectional analysis', 'Cross-Sectional Analysis',
                'Cultural studies not elsewhere classified', 'Cultural Studies not elsewhere classified', 'Cultural theory',
                'Cultural Theory', 'Culture, Gender, Sexuality', 'Culture, representation and identity',
                'Curriculum and pedagogy not elsewhere classified', 'Curriculum and Pedagogy not elsewhere classified',
                'Curriculum and pedagogy theory and development', 'Curriculum and Pedagogy Theory and Development', 'Database systems',
                'Decision making', 'Decision Making', 'Deep learning', 'Defence Studies', 'Dental therapeutics, pharmacology and toxicology',
                'Design History and Theory', 'Design Management and Studio and Professional Practice',
                'Design Practice and Management not elsewhere classified', 'Developmental Psychology and Ageing',                
                'Digital electronic devices', 'Digital forensics', 'Digital processor architectures', 'Discourse and pragmatics',
                'Discourse and Pragmatics', 'Drama, Theatre and Performance Studies', 'Dynamics, vibration and vibration control',
                'Early childhood education', 'Early Childhood Education (excl. Maori)', 'Earthquake engineering',
                'Earth Sciences not elsewhere classified', 'Ecological applications not elsewhere classified',
                'Ecological Applications not elsewhere classified', 'Ecological Impacts of Climate Change',
                'Ecology not elsewhere classified', 'Econometric and statistical methods', 'Econometric and Statistical Methods',
                'Economic Models and Forecasting', 'Ecosystem Function', 'Educational psychology', 'Educational Psychology',
                'Educational technology and computing', 'Education not elsewhere classified', 'Education policy', 'Education Policy',
                'Education systems not elsewhere classified', 'Electrical and Electronic Engineering not elsewhere classified',
                'Electrical circuits and systems', 'Electrical energy generation (incl. renewables, excl. photovoltaics)',
                'Electrical energy storage', 'Electrical energy transmission, networks and systems',
                'Electrical engineering not elsewhere classified', 'Electrical machines and drives', 'Electroanalytical chemistry',
                'Electrochemical energy storage and conversion', 'Electrochemistry', 'Empirical software engineering', 'Endocrinology',
                'Energy-efficient computing', 'Energy generation, conversion and storage (excl. chemical and electrical)',
                'English as a Second Language', 'Environmental assessment and monitoring',
                'Environmental Chemistry (incl. Atmospheric Chemistry)', 'Environmental communication',
                'Environmental Education and Extension', 'Environmental engineering not elsewhere classified', 'Environmental history',
                'Environmental Impact Assessment', 'Environmentally sustainable engineering', 'Environmental management',
                'Environmental Politics', 'Environmental Rehabilitation (excl. Bioremediation)',
                'Environmental Science and Management not elsewhere classified', 'Environmental Sciences not elsewhere classified',
                'Environment policy', 'Enzymes', 'Epidemiology not elsewhere classified',
                'Epigenetics (incl. genome methylation and epigenomics)',
                'Ethical Use of New Technology (e.g. Nanotechnology, Biotechnology)',
                'European history (excl. British, classical Greek and Roman)', 'Evolutionary computation', 'Evolutionary ecology',
                'Experimental economics', 'Experimental methods in fluid flow, heat and mass transfer', 'Family care', 'Family Law',
                'Farming Systems Research', 'Farm management, rural management and agribusiness',
                'Farm Management, Rural Management and Agribusiness', 'F-block chemistry', 'Feminist and queer theory', 'Feminist Theory',
                'Field organic and low chemical input horticulture', 'Field robotics', 'Film and Television', 'Finance',
                'Financial Economics', 'Fire safety engineering', 'Flexible manufacturing systems', 'Flight dynamics',
                'Food and Hospitality Services', 'Food chemistry and food sensory science', 'Food engineering', 'Food nutritional balance',
                'Food packaging, preservation and processing', 'Food properties (incl. characteristics and health benefits)',
                'Food safety, traceability, certification and authenticity', 'Food sciences not elsewhere classified', 'Food sustainability',
                'Food technology', 'Forensic chemistry', 'Forensic psychology', 'Forensic Psychology', 'Forest biodiversity',
                'Forest ecosystems', 'Forestry biomass and bioproducts', 'Forestry management and environment',
                'Forestry sciences not elsewhere classified', 'Freshwater ecology', 'Functional materials',
                'Fundamental and theoretical fluid dynamics', 'Gastroenterology and hepatology', 'Gender history', 'Gender relations',
                'Gender, sexuality and education', 'Gender, Sexuality and Education', 'Gender Specific Studies',
                'Gender studies not elsewhere classified', 'Gene and Molecular Therapy',
                'Gene expression (incl. microarray and other genome-wide approaches)'
                , 'Gene Expression (incl. Microarray and other genome-wide approaches)', 'Genetic immunology',
                'Genetics not elsewhere classified', 'Genomics', 'Genomics and transcriptomics', 'Geochronology',
                'Geophysics not elsewhere classified', 'Geospatial information systems and geospatial data modelling',
                'Geriatrics and gerontology', 'Glaciology', 'Globalisation and culture', 'Granular mechanics',
                'Graphics, augmented reality and games not elsewhere classified', 'Graph, social and multimedia data',
                'Groundwater hydrology', 'Health and community services', 'Health and Community Services',
                'Health and ecological risk assessment', 'Health Care Administration', 'Health, Clinical and Counselling Psychology',
                'Health equity', 'Health informatics and information systems', 'Health promotion', 'Health psychology',
                'Health services and systems not elsewhere classified', 'Health systems',
                'Heritage, archive and museum studies not elsewhere classified', 'Higher education', 'Higher Education',
                'Historical studies not elsewhere classified', 'Historical Studies not elsewhere classified', 'Histories of race',
                'History and Archaeology not elsewhere classified', 'History and philosophy of medicine', 'History and philosophy of science',
                'History and philosophy of specific fields not elsewhere classified',
                'History and Theory of the Built Environment (excl. Architecture)', 'History of Ideas', 'History of religion',
                'Horticultural crop growth and development', 'Horticultural crop protection (incl. pests, diseases and weeds)',
                'Host-parasite interactions', 'Human-computer interaction', 'Human Geography not elsewhere classified',
                'Humanitarian disasters, conflict and peacebuilding', 'Human Rights and Justice Issues',
                'Humoural Immunology and Immunochemistry', 'Hybrid and electric vehicles and powertrains',
                'Hydrodynamics and hydraulic engineering', 'Hypersonic propulsion and hypersonic aerothermodynamics', 'Image processing',
                'Immunological and Bioassay Methods', 'Immunology not elsewhere classified', 'Implementation science and evaluation',
                'Inclusive education', 'Industrial and Organisational Psychology',
                'Industrial and organisational psychology (incl. human factors)', 'Industrial and product design',
                'Industrial biotechnology diagnostics (incl. biosensors)', 'Industrial Design', 'Industrial electronics',
                'Industrial engineering', 'Industrial Molecular Engineering of Nucleic Acids and Proteins', 'Infant and child health',
                'Infectious agents', 'Infectious diseases', 'Information extraction and fusion', 'Information governance, policy and ethics',
                'Information modelling, management and ontologies', 'Information retrieval and web search',
                'Information security management', 'Information systems for sustainable development and the public good',
                'Infrastructure engineering and asset management', 'Inorganic chemistry not elsewhere classified',
                'Inorganic Chemistry not elsewhere classified', 'Inorganic geochemistry', 'Inorganic materials (incl. nanomaterials)',
                'Instrumental methods (excl. immunological and bioassay methods)', 'Intellectual Property Law', 'Intelligent robotics',
                'Interactive media', 'Interactive narrative', 'International and development communication', 'International economics',
                'International history', 'International Relations',
                'Inter-organisational, extra-organisational and global information systems',
                'Interorganisational Information Systems and Web Services', 'Intersectional studies', 'Invertebrate biology',
                'Isotope Geochemistry', 'Knowledge and information management', 'Knowledge Representation and Machine Learning',
                'Knowledge representation and reasoning', 'Korean Language', 'Korean Literature', 'Labour economics', 'Labour Economics',
                'Land Capability and Soil Degradation', 'Landscape Architecture', 'Landscape ecology', 'Land use and environmental planning',
                'Land Use and Environmental Planning', 'Language, Communication and Culture not elsewhere classified',
                'Latin and Classical Greek Languages', 'Latin and classical Greek literature', 'Latin and Classical Greek Literature',
                'Law and Legal Studies not elsewhere classified', 'Law not elsewhere classified', 'Learning, motivation and emotion',
                'Learning sciences', 'Legal Institutions (incl. Courts and Justice Systems)', 'Library and Information Studies',
                'Linguistic anthropology', 'Linguistics not elsewhere classified',
                'Linguistic structures (incl. phonology, morphology and syntax)', 'Literary theory', 'Literature in Chinese',
                'Literature in French', 'Literature in Spanish and Portuguese', 'Logistics and Supply Chain Management', 'Machining',
                'Macroeconomics (incl. monetary and fiscal theory)', 'Macroeconomics (incl. Monetary and Fiscal Theory)',
                'Macromolecular and materials chemistry not elsewhere classified',
                'Macromolecular and Materials Chemistry not elsewhere classified', 'Macromolecular materials', 'Main Group Metal Chemistry',
                'Manufacturing engineering not elsewhere classified', 'Manufacturing Engineering not elsewhere classified',
                'Manufacturing processes and technologies (excl. textiles)', 'Manufacturing safety and quality',
                'Maori Education (excl. Early Childhood and Primary Education)', 'Maori Information and Knowledge Systems',
                'Marine and Estuarine Ecology (incl. Marine Ichthyology)', 'Marine engineering', 'Marketing communications',
                'Marketing Communications', 'Marketing not elsewhere classified', 'Marketing research methodology', 'Marketing technology',
                'Marketing Theory', 'Materials engineering not elsewhere classified', 'Mechanobiology',
                'Mechatronics hardware design and architecture', 'Media studies', 'Media Studies',
                'Medical and Health Sciences not elsewhere classified', 'Medical biochemistry - lipids',
                'Medical biochemistry - proteins and peptides (incl. medical proteomics)', 'Medical biotechnology not elsewhere classified',
                'Medical devices', 'Medical Molecular Engineering of Nucleic Acids and Proteins', 'Medical physics',
                'Medical physiology not elsewhere classified', 'Medical robotics',
                'Medicinal and biomolecular chemistry not elsewhere classified',
                'Medicinal and Biomolecular Chemistry not elsewhere classified', 'Metabolomic chemistry', 'Metal cluster chemistry',
                'Metals and alloy materials', 'Meteorology', 'Micro- and nanosystems', 'Microbial ecology', 'Microbial Ecology',
                'Microbiology not elsewhere classified', 'Microeconomic theory', 'Microelectromechanical systems (MEMS)', 'Microelectronics',
                'Microfluidics and nanofluidics', 'Microtechnology', 'Mineralogy and Crystallography',
                'Mixed initiative and human-in-the-loop', 'Mobile computing', 'Models and simulations of design',
                'Molecular and organic electronics', 'Molecular imaging (incl. electron microscopy and neutron diffraction)',
                'Molecular medicine', 'Molecular Medicine', 'Motor control', 'Multicultural, intercultural and cross-cultural studies',
                'Multicultural, Intercultural and Cross-cultural Studies', 'Multimodal analysis and synthesis',
                'Multiphysics flows (incl. multiphase and reacting flows)', 'Museum Studies', 'Music not elsewhere classified',
                'Musicology and ethnomusicology', 'Musicology and Ethnomusicology', 'Music performance', 'Nanobiotechnology',
                'Nanochemistry', 'Nanofabrication, growth and self assembly', 'Nanomanufacturing', 'Nanomaterials', 'Nanomedicine',
                'Natural hazards', 'Natural Hazards', 'Natural language processing', 'Natural products and bioactive compounds',
                'Natural Products Chemistry', 'Natural resource management', 'Natural Resource Management', 'Nephrology and urology',
                'Networking and communications', 'Neural engineering', 'Neural, Evolutionary and Fuzzy Computation', 'Neural networks',
                'Neurocognitive Patterns and Neural Networks', 'Neurogenetics', 'Neurology and neuromuscular diseases',
                'Neurosciences not elsewhere classified', 'New Zealand Government and Politics', 'New Zealand History',
                'Nonlinear optics and spectroscopy', 'Non-Newtonian fluid flows (incl. rheology)', 'North American history',
                'Nursing not elsewhere classified', 'Nutritional science', 'Nutrition and dietetics not elsewhere classified',
                'Obstetrics and gynaecology', 'Operating systems', 'Operations research', 'Optical properties of materials',
                'Organic chemical synthesis', 'Organic Chemical Synthesis', 'Organic Chemistry', 'Organic chemistry not elsewhere classified',
                'Organic semiconductors', 'Organisational Behaviour', 'Organisational, interpersonal and intercultural communication',
                'Organisational Planning and Management', 'Organisation and Management Theory', 'Organometallic chemistry',
                'Organometallic Chemistry', 'Orthopaedics', 'Other agricultural, veterinary and food sciences not elsewhere classified',
                'Other Asian Literature (excl. South-East Asian)', 'Other biological sciences not elsewhere classified',
                'Other biomedical and clinical sciences not elsewhere classified', 'Other chemical sciences not elsewhere classified',
                'Other earth sciences not elsewhere classified', 'Other engineering not elsewhere classified',
                'Other environmental sciences not elsewhere classified', 'Other health sciences not elsewhere classified',
                'Other human society not elsewhere classified', 'Other language, communication and culture not elsewhere classified',
                'Other Literatures in English', 'Other philosophy and religious studies not elsewhere classified',
                'Other psychology not elsewhere classified', 'Pacific Languages', 'Pacific Literature', 'Pacific Peoples Health',
                'Packaging, storage and transportation (excl. food and agricultural products)', 'Palaeoclimatology', 'Panel data analysis',
                'Panel Data Analysis', 'Particle physics', 'Pathology (excl. oral pathology)', 'Pattern recognition',
                'Pattern Recognition and Data Mining', 'People with disability', 'Performance evaluation', 'Peripheral nervous system',
                'Personality, Abilities and Assessment', 'Personality and individual differences', 'Pervasive computing',
                'Pharmaceutical delivery technologies', 'Pharmaceutical sciences',
                'Pharmacology and pharmaceutical sciences not elsewhere classified', 'Phonetics and speech science', 'Photochemistry',
                'Photogrammetry and remote sensing', 'Photovoltaic devices (solar cells)', 'Photovoltaic power systems',
                'Phylogeny and comparative analysis', 'Planetary geology', 'Planetary science (excl. solar system and planetary geology)',
                'Planning and decision making', 'Plant biochemistry', 'Plant biology not elsewhere classified',
                'Plant Biology not elsewhere classified', 'Plant cell and molecular biology', 'Plant pathology', 'Plant physiology',
                'Political science not elsewhere classified', 'Political Science not elsewhere classified',
                'Political Theory and Political Philosophy', 'Pollution and contamination not elsewhere classified', 'Polymers and plastics',
                'Poststructuralism', 'Poverty, inclusivity and wellbeing', 'Powder and particle technology',
                'Power and Energy Systems Engineering (excl. Renewable Power)', 'Precision engineering', 'Preventative health care',
                'Primary Education (excl. Maori)', 'Primary health care', 'Private policing and security services', 'Probability theory',
                'Procedural content generation', 'Process control and simulation', 'Production and operations management',
                'Professional education and training', 'Proteins and peptides', 'Protein trafficking',
                'Proteomics and intermolecular interactions (excl. medical proteomics)',
                'Proteomics and Intermolecular Interactions (excl. Medical Proteomics)', 'Proteomics and metabolomics',
                'Psychiatry (incl. psychotherapy)', 'Psychological Methodology, Design and Analysis',
                'Psychology and Cognitive Sciences not elsewhere classified', 'Psychology not elsewhere classified', 'Psychology of ageing',
                'Psychophysiology', 'Public economics - taxation and revenue', 'Public Economics- Taxation and Revenue',
                'Public Health and Health Services not elsewhere classified', 'Public health not elsewhere classified', 'Public policy',
                'Pure mathematics not elsewhere classified', 'Quality Management', 'Quaternary Environments',
                'Query processing and optimisation', 'Race and Ethnic Relations', 'Radiation Therapy', 'Radio frequency engineering',
                'Radiology and organ imaging', 'Reaction engineering (excl. nuclear reactions)', 'Reaction kinetics and dynamics',
                'Real and complex functions (incl. several variables)', 'Receptors and membrane biology', 'Recommender systems',
                'Regenerative medicine (incl. stem cells)', 'Rehabilitation', 'Reinforcement learning',
                'Religion and Religious Studies not elsewhere classified', 'Reproduction', 'Research, science and technology policy',
                'Risk engineering', 'Satellite, space vehicle and missile design and testing',
                'Science, technology and engineering curriculum and pedagogy', 'Screen and Media Culture', 'Sedimentology',
                'Semi- and unsupervised learning', 'Separation science', 'Separation Science', 'Separation technologies', 'Sequence analysis',
                'Sexualities', 'Signal processing', 'Signal transduction', 'Simulation, modelling, and programming of mechatronics systems',
                'Social and affective neuroscience', 'Social and Community Psychology', 'Social and Cultural Anthropology',
                'Social and Cultural Geography', 'Social change', 'Social Change', 'Social psychology', 'Social theory', 'Social Theory',
                'Sociology', 'Sociology and Social Studies of Science and Technology', 'Sociology not elsewhere classified',
                'Sociology of education', 'Sociology of Education', 'Software and application security',
                'Soil chemistry and soil carbon sequestration (excl. carbon sequestration science)', 'Soil physics',
                'Soil sciences not elsewhere classified', 'Solar system planetary science (excl. planetary geology)',
                'Solid state chemistry', 'Solution chemistry', 'Spatial data and applications', 'Special education and disability',
                'Special Education and Disability', 'Specialist Studies in Education not elsewhere classified', 'Special vehicles',
                'Speech recognition', 'Sport and exercise psychology',
                'Stratigraphy (incl. biostratigraphy, sequence stratigraphy and basin analysis)', 'Stream and sensor data',
                'Structural biology (incl. macromolecular modelling)', 'Structural Chemistry and Spectroscopy', 'Structural dynamics',
                'Structural engineering', 'Structural geology and tectonics', 'Structural properties of condensed matter',
                'Structure and dynamics of materials', 'Studies of Asian Society', 'Stylistics and Textual Analysis', 'Supply chains',
                'Supramolecular chemistry', 'Surface Processes', 'Surface water hydrology',
                'Surface water quality processes and contaminated sediment assessment', 'Sustainability accounting and reporting',
                'Sustainability Accounting and Reporting', 'Sustainable agricultural development', 'Synthesis of Materials',
                'Systems biology', 'Systems engineering', 'Systems physiology', 'Teacher education and professional development of educators',
                'Terrestrial ecology', 'Terrestrial Ecology', 'Textile and Fashion Design', 'Theology',
                'Theoretical and computational chemistry not elsewhere classified', 'Theoretical quantum chemistry',
                'Theory and design of materials', 'Thermodynamics and statistical physics', 'Time-series analysis', 'Time-Series Analysis',
                'Tissue engineering', 'Toxicology (incl. clinical toxicology)',
                'Traditional, complementary and integrative medicine not elsewhere classified', 'Transition metal chemistry',
                'Translational and applied bioinformatics', 'Transportation, logistics and supply chains not elsewhere classified',
                'Transport engineering', 'Transport properties and non-equilibrium processes', 'Tribology', 'Tumour immunology',
                'Turbulent flows', 'Urban Analysis and Development', 'Urban and Regional Economics', 'Urban Design', 'Veterinary immunology',
                'Veterinary sciences not elsewhere classified', 'Video processing', 'Virtual and mixed reality',
                'Virtual Reality and Related Simulation', 'Vision science', 'Visual Arts and Crafts not elsewhere classified',
                'Visual Communication Design (incl. Graphic Design)', 'Vocational education and training curriculum and pedagogy',
                'Volcanology', 'Water treatment processes', 'Wearable materials', 'Welfare Economics', 'Wildlife and Habitat Management',
                'Wireless communication systems and technologies (incl. microwave and millimetrewave)', 'Wood processing']
uncategories += ['Early English languages', 'Educational administration, management and leadership', 'Education assessment and evaluation',
                 'Biosecurity science and invasive species ecology', 'Other literatures in English', 'Zoology not elsewhere classified',
                 'Biosecurity science and invasive species ecology']
boring = ['Economics Theses', 'Institute of Development Studies Theses', 'Law Theses', 'Biology Theses',
          'International Relations Theses', 'Accounting and Finance Theses', 'Anthropology Theses', 'Art History Theses',
          'Biochemistry Theses', 'Biology and Environmental Science Theses', 'Business and Management Theses', 'Chemistry Theses',
          'Education Theses', 'Engineering and Design Theses', 'English Theses', 'Geography Theses', 'History Theses',
          'International Development Theses', 'Management Theses', 'Media and Film Theses', 'Neuroscience Theses',
          'Philosophy Theses', 'Politics Theses', 'Psychology Theses', 'Social Work and Social Care Theses',
          'Sociology and Criminology Theses', 'SPRU - Science Policy Research Unit Theses', 'American Studies Theses',
          'Sussex Centre for Genome Damage Stability Theses', 'Faculty of Medicine, Nursing and Health Sciences',
          'BSMS Neuroscience Theses', 'Music Theses', 'Faculty of Art, Design and Architecture', 'Faculty of Law', 'Fine Art', 'Law',
          'Monash Sustainability Institute', 'Monash Sustainable Development Institute', 'Creative Arts', 'Design', 'English',
          'Sport, Exercise and Health Sciences', 'Architecture, Building and Civil Engineering', 'Accounting', 'Biological Sciences',
          'Business and Economics (Monash University Malaysia)', 'Chemical & Biological Engineering', 'Civil Engineering',
          'Econometrics and Business Statistics', 'Economics', 'Education', 'Faculty of Arts', 'Faculty of Business and Economics',
          'Faculty of Education', 'Faculty of Engineering', 'Faculty of Pharmacy and Pharmaceutical Sciences',
          'Human Centred Computing', 'Management', 'Mechanical and Aerospace Engineering', 'Tepper School of Business',
          'School of Curriculum, Teaching and Inclusive Education', 'School of Education, Culture and Society',
          'School of Language, Literatures, Cultures and Linguistics', 'School of Media, Film and Journalism',
          'School of Pharmacy (Malaysia)', 'School of Philosophical, Historical & International Studies',
          'School of Sciences (Monash University Malaysia)', 'School of Social Sciences (Monash Australia)',
          'Monash University Accident Research Centre (MUARC)', 'Monash University Accident Research Centre',
          'Architecture', 'Chemical Engineering', 'Civil and Environmental Engineering',  'Human-Computer Interaction Institute',
          'Language Technologies Institute', 'Philosophy', 'School of History, Politics and International Relations',
          'School of Geography, Geology and the Environmen', 'Department of Chemistry',
          'Department of Molecular & Cell Biology', 'Bishop Grosseteste University',
          'College of Life Sciences', 'College of Social Sciences, Arts, and Humanities',
          'Department of Allied Health professions', 'Department of Archaeology and Ancient History',
          'Department of Cardiovascular Sciences', 'Department of Cardiovascular Science,',
          'Department of Clinical Psychology', 'Department of Economics, Finance and Accounting',
          'Department of English', 'Department of Genetics and Genome Biology',
          'Department of Geography', 'Department of Health Sciences', 'Department of Health Science',
          'Department of Molecular & Cell Biology', 'Department of Molecular and Cell Biology',
          'Department of Neuroscience, Psychology and Behaviour', 'Social Work',
          'Department of Neuroscience, Psychology, and Behaviour',
          'Department of Politics and International Relations', 'Department of Population Health Sciences',
          'Department of Respiratory Sciences', 'Leicester Business School',
          'Leicester Cancer Research Centre', 'Leicester Law School', 'Communication and Culture',
          'Mahmoud Ehnesh School of Engineering', 'Newman College/Bishops Grosseteste',
          'Politics and International Relations', 'School of Archaeology and Ancient History',
          'School of Arts', 'School of Business', 'School of Chemistry', 'School of Criminology',
          'School of Education', 'School of Engineering', 'Architecture',
          'School of Geography, Geology and the Environment', 'Biomedical Engineering',
          'School of History, Politics & International Relations',
          'School of Media, Communication and Sociology', 'School of Media, Communication, and Sociology',
          'School of Museum Studies', 'School of Neuroscience, Psychology and Behaviour',
          'School of Psychology & Vision Sciences', 'School of Psychology and Vision Sciences',
          'Aerospace Engineering', 'Biomedical Physics', 'Digital Media', 'Documentary Media',
          'Environmental Applied Science and Management', 'Fashion', 'Department of Management',
          'Film and Photography Preservation and Collection Management',
          'Immigration and Settlement Studies', 'Management (TRSM)', 'Master of Science in Management',
          'Mechanical and Industrial Engineering', 'Nursing', 'Public Policy and Administration',
          'Urban Development', 'Agricultural Economics', 'Botany and Plant Pathology',
          'Educational Studies', 'Hospitality and Tourism Management', 'Nutrition Science',
          'Political Science', 'Psychological Sciences', 'Speech, Language, and Hearing Sciences',
          'Technology Leadership and Innovation', 'Cardiovascular Sciences',
          'Department of Genetics & Genome Biology', 'Department of Respiratory Science',
          'Department of Sociology', 'History', 'School of Engineering, University of Leicester',
          'School of History, Politics, and International Relations', 'School of Management',
          'Australian Institute of Health Innovation', 'Department of Applied Finance',
          'Department of Media, Communications, Creative Arts, Languages & Literature',
          'Department of Philosophy', 'Dept of Applied Finance', 'Macquarie Law School',
          'Macquarie School of Education', 'Macquarie School of Social Sciences',
          'School of Psychological Sciences', 'Comparative Pathobiology', 'Building Science',
          'Chemistry', 'College of Social Sciences, Arts and Humanities', 'Consumer Science',
          'Curriculum and Instruction', 'Department of Accounting and Corporate Governance',
          'Department of Cardiovascular Science', 'Department of Economics',
          'Department of Engineering', 'Department of Marketing',
          'Department of Media, Communication and Sociology',
          'Department of Media, Communication, and Sociology', 'Design and Creative Arts',
          'Division of Medical Education Theses', 'Engineering Education',
          'Evolution, Behaviour and Environment Theses', 'Loughborough Business School',
          'Materials Science and Engineering', 'Policy Studies', 'Psychology',
          'Respiratory Sciences', 'Robotics Institute',
          'School of Geography, Geology, and the Environment', 'School of Social Sciences',
          'Sociology']
boring += ['Anatomy and Cell Biology', 'Anthropology', 'ANTHROPOLOGY', 'Art and Art History', 'Art History', 'Biobehavioral Nursing Science', 'Biochemistry and Molecular Genetics', 'Bioengineering', 'Biomedical engineering', 'Business Administration', 'Cellular and Molecular Pharmacology', 'Civil, Material and Environmental Engineering', 'Civil, Material, and Environmental Engineering', 'Civil , Materials and Environmental Engineering', 'Civil Materials and Environmental Engineering', 'Civil, Materials and Environmental Engineering', 'Civil, Materials, and Environmental Engineering', 'Civil, Materials and Environment', 'College of Dentistry', 'Communication', 'Criminology, Law, and Justice', 'Curriculum & Instruction', 'Dentistry', 'Department of Biobehavioral Nursing Science', 'Department of Public Policy, Management and Analytics', 'Disability and Human Development', 'Disability Studies', 'Earth and Environmental Sciences', 'Educational Policy Studies', 'Educational Psychology', 'Endodontics', 'Epidemiology & Biostatistics', 'Epidemiology and Biostatistics', 'Epidemiology', 'Germanic Studies', 'Graduate Program in Neuroscience', 'Hematology and Oncology', 'Hispanic and Italian Studies', 'Human Development Nursing Science', 'Industrial Engineering', 'Jane Addams College of Social Work', 'Kinesiology & Nutrition', 'Kinesiology and Nutrition', 'Learning Sciences', 'Mechanical Engineering', 'Medical Education', 'Microbiology and Immunology', 'Museum and Exhibition Studies', 'Neurology & Rehabilitation', 'Neuroscience', 'Oral Biology', 'Oral Sciences', 'Oral Science', 'Orthodontics', 'Pathology', 'Pediatric Dentistry', 'Periodontics', 'Pharmaceutical sciences', 'Pharmaceutical Sciences', 'Pharmaceutical Science', 'Pharmacology', 'Pharmacy Systems, Outcomes & Policy', 'Pharmacy Systems, Outcomes and Policy', 'Pharmacy, Systems, Outcomes and Policy', 'Physical Therapy', 'Physiology and Biophysics', 'Prosthodontics', 'PSCI', 'Public Administration', 'Public Health Sciences-Clinical and Transitional Science', 'Public Health Sciences - Community Health Sciences', 'Public Health Sciences-Community Health Sciences', 'Public Health Sciences-Environmental and Occupational Health Sciences', 'Public Health Sciences-Epidemiology', 'Public Health Sciences-Health Policy Administration', 'Public Health Sciences-Health Policy & Administration', 'Public Health Sciences-Health Policy and Administration', 'Restorative Dentistry', 'Restorative', 'Special Education', 'Urban Planning and Policy']
#try and error to find server-name: it's "lboro" because  https://lboro.figshare.com/ exists
thesesstandardservers = {'kilthub' : 'Carnegie Mellon U. (main)',
                         'melbourne' : 'U. Melbourne (main)', #2
                         'brunel' : 'Brunel U.', #no theses 
                         'auckland' : 'Auckland U.', #6
                         'leicester' : 'Leicester U.',
                         'sussex' : 'Sussex U.',
                         'monash' : 'Monash U.',
                         'ryerson' : 'Ryerson U.', 
                         'wellington' : 'Victoria U., Wellington',#no theses ???
                         'lboro' : 'Loughborough U.',
                         'mq' : 'Macquarie U.',
                         'uic' : 'U. Illinois, Chicago',
                         'hammer' : 'Purdue U.'} 

nonlistedcategories = {}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('figshare')

###formulate the search statements
payloads = []
#Preprint server TechRxiv
if srv == 'techrxiv':
    publisher = 'IEEE'
    jnl = 'BOOK'
    for cat in ['Computing and Processing', 'Nuclear Engineering',
                'Signal Processing and Analysis', 'Components, Circuits, Devices and Systems']:
        payloads.append(('', {"search": ":institution: %s AND :category: %s" % (srv, cat)}))     
    alloweditems = ['preprint']   
#Stockholm #0
elif srv == 'su':
    publisher = 'Stockholm U. (main)'
    jnl = 'BOOK'
    for cat in list(cattofc.keys()):
        if cattofc[cat] == 'm':
            payloads.append(('Stockholm U., Math. Dept.', {"search": ":institution: %s AND :category: %s AND :item_type: thesis" % (srv, cat)}))
        if cattofc[cat] in ['q', 't', 'k']:
            payloads.append(('Stockholm U.', {"search": ":institution: %s AND :category: %s AND :item_type: thesis" % (srv, cat)}))
        else:
            payloads.append(('Stockholm U. (main)', {"search": ":institution: %s AND :category: %s AND :item_type: thesis" % (srv, cat)}))
    alloweditems = ['thesis']
#standard server for theses
elif srv in list(thesesstandardservers.keys()):
    publisher = thesesstandardservers[srv]
    jnl = 'BOOK'
#    for cat in list(cattofc.keys()):
#        payloads.append((thesesstandardservers[srv], {"search": ":institution: %s AND :category: %s AND :item_type: thesis" % (srv, cat)}))
    for y in range(years-1):
        payloads.append((thesesstandardservers[srv], {"search": ":institution: %s AND :posted_date: %i AND :item_type: thesis" % (srv, ejlmod3.year(backwards=y))}))
        payloads.append((thesesstandardservers[srv], {"search": ":institution: %s AND :publication_date: %i AND :item_type: thesis" % (srv, ejlmod3.year(backwards=y))}))
    alloweditems = ['thesis']
#search at figshare directly
elif srv == 'figshare':
    publisher = 'Figshare'
    jnl = 'BOOK'
    rpp = 20
    pages = 1
    for cat in list(cattofc.keys()):
        payloads.append(('', {"search": ":category: %s AND :item_type: thesis" % (cat)}))
    alloweditems = ['thesis']
    skipnonlistedcategories = False
    alreadyharvested += ejlmod3.getalreadyharvested('THESES')


    
###search and get indiviual article links
prerecs = []
articleurls = []
i = 0
for (aff, payload) in payloads:
    i += 1
    payload['page_size'] = rpp
    for page in range(pages):
        payload['page'] = page+1
        ejlmod3.printprogress('=', [[i, len(payloads)], [payload]])
        try:
            response = requests.post(apiurl, json=payload, headers={"authorization": auth}, timeout=120, verify=False)
            response.raise_for_status()  # will raise an exception if there's an error
            r = response.json()
        except:
            time.sleep(300)
            response = requests.post(apiurl, json=payload, headers={"authorization": auth}, timeout=120, verify=False)
            response.raise_for_status()  # will raise an exception if there's an error
            r = response.json()            
        for article in r:
            rec = {'url_public_api' : article['url_public_api'], 'autaff' : [], 'note' : [payload['search']], 'jnl' : jnl}
            if aff:
                rec['affiliation'] = aff
            if article['timeline']['firstOnline'][:10] > startdate:
                if not article['url_public_api'] in articleurls:
                    if ejlmod3.checkinterestingDOI(article['url_public_api']):
                        if skipalreadyharvested and article['url_public_api'] in alreadyharvested:
                            print('   %s already in backup' % (article['url_public_api']))
                        else:
                            prerecs.append(rec)
                            articleurls.append(article['url_public_api'])
        print('  %4i records so far (checked %i)' % (len(prerecs), len(r)))
        time.sleep(sleepingtime)
        if len(r) < rpp:
            break

###harvest individual articles
i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['url_public_api']], [len(recs)]])
    artjson = requests.get(rec['url_public_api']).json()
    #submitter, degree, supervisor, department/
    submitter = ''
    for cf in artjson['custom_fields']:
        if cf['name'] == 'Email Address of Submitting Author':
            submitter = 'submitter: ' + cf['value']
        elif cf['name'] == 'ORCID of Submitting Author':
            submitter += ', ORCID: ' + cf['value']
        elif cf['name'] == 'Language':
            for lg in cf['value']:
                rec['language'] = lg
        elif cf['name'] in ['Qualification level', 'Qualification name',
                            'Degree Type', 'Degree Name']:
            if type(cf['value']) == type(''):
                degs = [cf['value']]
            else:
                degs = cf['value']
            for deg in degs:
                if deg in ['master', 'bachelor', 'masters', 'mphil', 'MASTERS', 'Doctor of Juridical Science',
                           'Masters', 'MPHIL', 'Master of Science (MS)', "Master's Thesis", 'DClinPsy', 'MD',
                           'DPsych', 'DSocSci', 'EdD', 'Master of Arts', 'Bachelor of Arts',
                           'Bachelor of Science', 'Master of Science', 'Master of Architecture',
                           'Master of Applied Science', 'Master of Social Work', 'Thesis MRes',
                           'Master of Architecture (Professional)', 'Doctor of Education', 'edd',
                           'Master of Commerce and Administration', 'Master of Interior Architecture',
                           'Master of Landscape Architecture', 'Master of Music Therapy',
                           'Master of Science in Mechanical Engineering', 'Thesis masters research']:
                    keepit = False
                    print('    skip "%s"' % (deg))
                    ejlmod3.adduninterestingDOI(rec['url_public_api'])
                elif not deg in ['phd', 'doctoral', 'PhD', 'Ph.D.', 'dissertation', 'DOCTORATE',
                                 'Doctoral', 'Dissertation', 'Doctor of Philosophy (PhD)',
                                 'Thesis PhD']:
                    rec['note'].append('DEGREE:::' + deg)                    
        elif cf['name'] in ['Advisor(s)', 'Supervisor(s)', 'Thesis Advisor', 'Principal Supervisor', 'Advisor/Supervisor/Committee Chair']:
            for sv in re.split(' *[;\n] *', cf['name']):
                if 'supervisor' in list(rec.keys()):
                    rec['supervisor'].append([sv])
                else:
                    rec['supervisor'] = [[sv]]
        elif cf['name'] in ['Department', 'Department affiliated with', 'Department, School or Centre', 'Faculty',
                            'School', 'Author affiliation', 'Program', 'Department, Centre or School'] and keepit:
            if type(cf['value']) == type(''):
                deps = [cf['value']]
            else:
                deps = cf['value']
            for dep in deps:
                if dep in boring:
                    keepit = False
                    print('    skip "%s"' % (dep))
                    ejlmod3.adduninterestingDOI(rec['url_public_api'])
                elif dep in ['Informatics Theses', 'Computer Science']:
                    rec['fc'] = 'c'
                elif dep in ['Mathematics Theses', 'Mathematics', 'Applied Mathematics']:
                    rec['fc'] = 'm'
                elif not dep in ['Physics and Astronomy Theses', 'Physics and Astronomy',
                                 'Department of Physics and Astronomy',
                                 'School of Computing and Mathematical Sciences.',
                                 'School of Computing and Mathematical Sciences',
                                 'School of Physics and Astronomy',
                                 'School of Physics & Astronomy']:
                    rec['note'].append('DEPARTMENT:::'+dep)
        elif cf['name'] == 'Pages':
            rec['pages'] = re.sub('\.0$', '', cf['value'])
        elif cf['name'] == 'ISBN':
            rec['isbn'] = cf['value']
    if submitter:
        rec['note'].append(submitter)
    #doctype
    if 'defined_type_name' in artjson and keepit:
        if artjson['defined_type_name'] == 'preprint':
            rec['tc'] = ''
        elif artjson['defined_type_name'] == 'thesis':
            rec['tc'] = 'T'
        elif artjson['defined_type_name'] == 'monograph':
            rec['tc'] = 'B'
        elif artjson['defined_type_name'] == 'journal contribution':
            rec['tc'] = 'P'
        elif artjson['defined_type_name'] == 'conference contribution':
            rec['tc'] = 'C'
        elif artjson['defined_type_name'] == 'chapter':
            rec['tc'] = 'S'
        else:
            rec['tc'] = ''
        if not artjson['defined_type_name'] in alloweditems:
            keepit = False
            print('    skip "%s"' % (artjson['defined_type_name']))
            ejlmod3.adduninterestingDOI(rec['url_public_api'])            
    #categories
    if 'categories' in artjson and keepit:
        for cat in artjson['categories']:
            if cat['title'] in cattofc:
                rec['note'].append('category: ' + cat['title'])
                if cattofc[cat['title']]:
                    if 'fc' in list(rec.keys()):
                        if not cattofc[cat['title']] in rec['fc']:
                            rec['fc'] += cattofc[cat['title']]
                    else:
                        rec['fc'] = cattofc[cat['title']]
            else:
                rec['note'].append('category: ' + cat['title'] + '???')
                if skipnonlistedcategories or cat['title'] in uncategories:
                    keepit = False
                    print('    skip "%s"' % (cat['title']))
                    ejlmod3.adduninterestingDOI(rec['url_public_api'])
                    if cat['title'] in nonlistedcategories:
                        nonlistedcategories[cat['title']] += 1
                    else:
                        nonlistedcategories[cat['title']] = 1
    #authos
    if 'authors' in artjson:
        for author in artjson['authors']:
            rec['autaff'].append([author['full_name']])
            if 'orcid_id' in list(author.keys()) and author['orcid_id'] :
                rec['autaff'][-1].append('ORCID:'+author['orcid_id'])
            if 'affiliation' in list(rec.keys()):
                rec['autaff'][-1].append(rec['affiliation'])
    #title
    if 'title' in artjson:
        rec['tit'] = artjson['title']
    #abstract
    if 'description' in artjson:
        rec['abs'] = artjson['description']
    #license
    if 'license' in artjson:
        if re.search('creativecommons', artjson['license']['url']):
            rec['license'] = {'url' : artjson['license']['url']}
    #keywords
    if 'tags' in artjson:
        rec['keyw'] = artjson['tags']
    #PID
    if 'doi' in artjson and artjson['doi']:
        rec['doi'] = artjson['doi']
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            keepit = False
            print('  %s already in backup' % (rec['doi']))
    if 'handle' in artjson and artjson['handle']:
        rec['hdl'] = artjson['handle']
        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
            keepit = False
            print('  %s already in backup' % (rec['hdl']))
    #date
    if 'published_date' in artjson:
        rec['date'] = artjson['published_date']
    #FFT
    if 'files' in artjson:
        if len(artjson['files']) > 1:
            rec['note'].append('%i files attached' % (len(artjson['files'])))
        for file in artjson['files']:
            if 'license' in list(rec.keys()):
                rec['FFT'] = file['download_url']
            else:
                rec['hidden'] = file['download_url']
    #link
    if not 'doi' in list(rec.keys()) and not 'hdl' in list(rec.keys()):
        rec['link'] = artjson['url_public_html']
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    time.sleep(sleepingtime)

numofbunches = (len(recs)-1) // bunchsize + 1
for i in range(numofbunches):
    jnlfilename = 'figshare.%s.%s.%04i_of_%04i' % (srv, ejlmod3.stampoftoday(), i+1, numofbunches)
    bunchrecs = recs[bunchsize*i:bunchsize*(i+1)]
    ejlmod3.writenewXML(bunchrecs, publisher, jnlfilename)#, retfilename='retfiles_special')

if skipnonlistedcategories:
    print('\n\nnon listed categories:')
    for cat in nonlistedcategories:
        print('%4i %s' % (nonlistedcategories[cat], cat))
