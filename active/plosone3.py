# -*- coding: utf-8 -*-
#program to harvest PLoS One
# FS 2022-11-17

import os
import ejlmod3
import re
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
import random
import datetime

publisher = 'PLOS'
chunksize = 30
#threshold for html harvest
years = 2
#API harvest
rpp = 200
daystocheck = 150
wheretosearch = 'abstract' # everywhere? title?

skipalreadyharvested = True

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

#avoid douple harvesting
dois = ["10.1371/journal.pone.0271462", "10.1371/journal.pone.0222371", "10.1371/journal.pone.0223636", "10.1371/journal.pone.0220237", "10.1371/journal.pone.0207827", "10.1371/journal.pone.0210817", "10.1371/journal.pone.0229382", "10.1371/journal.pone.0193785", "10.1371/journal.pone.0215287", "10.1371/journal.pone.0200910", "10.1371/journal.pone.0186624", "10.1371/journal.pone.0195494", "10.1371/journal.pone.0188398", "10.1371/journal.pone.0166011", "10.1371/journal.pone.0175876", "10.1371/journal.pone.0170920", "10.1371/journal.pone.0159898", "10.1371/journal.pone.0197735", "10.1371/journal.pone.0169832", "10.1371/journal.pone.0182779", "10.1371/journal.pone.0163241", "10.1371/journal.pone.0182130", "10.1371/journal.pone.0131184", "10.1371/journal.pone.0133679", "10.1371/journal.pone.0115993", "10.1371/journal.pone.0109507", "10.1371/journal.pone.0108482", "10.1371/journal.pone.0106368", "10.1371/journal.pone.0078114", "10.1371/journal.pone.0085777", "10.1371/journal.pone.0054165", "10.1371/journal.pone.0056086", "10.1371/journal.pone.0064694", "10.1371/journal.pone.0046428", "10.1371/journal.pone.0069469", "10.1371/journal.pone.0040689", "10.1371/journal.pone.0047523", "10.1371/journal.pone.0031929", "10.1371/journal.pone.0097107", "10.1371/journal.pone.0020721", "10.1371/journal.pone.0030136", "10.1371/journal.pone.0024330", "10.1371/journal.pone.0013061", "10.1371/journal.pone.0002052"]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('plosone')

boring = ['Behavioral and social aspects of health', 'Biomarkers', 'Educational attainment', 'Health care facilities', 'Hospitals', 'Lymphocytes', 'Marine fish', 'Myocardial infarction', 'Neurons', 'Obesity', 'Prostate cancer', 'Psychological stress', 'Social communication', 'Social media', 'Teeth', 'Trees', 'Urine', 'Cancers and neoplasms', 'Cancer treatment', 'Cardiovascular disease risk', 'Diagnostic medicine', 'DNA extraction', 'Drug therapy', 'Genomics', 'Musculoskeletal mechanics', 'Pregnancy', 'Prosocial behavior', 'Psychometrics', 'Respiratory infections', 'Blood', 'Diet', 'Infants', 'Inflammation', 'Intensive care units', 'Medical devices and equipment', 'SARS CoV 2', 'Economic development', 'Mental health and psychiatry', 'Psychological attitudes', 'Diabetes mellitus', 'Food', 'Polymerase chain reaction', 'Surgical and invasive medical procedures', 'Sports', 'Pandemics', 'Virus testing', 'Body weight', 'Finance', 'Emotions', 'COVID 19', 'Medical risk factors', 'Antibiotic resistance', 'Antibiotics', 'Bioinformatics', 'Biological locomotion', 'Biomaterial implants', 'Biomechanics', 'Bionanotechnology', 'Biophysical simulations', 'Biophysics', 'Biosphere', 'Biostatistics', 'Evolutionary biology', 'Evolutionary developmental biology', 'Biochemical simulations', 'Biodiversity', 'Biopsy', 'Biosynthesis', 'Chronobiology', 'Bioacoustics', 'Bioluminescence', 'Clinical medicine', 'Dehydration (medicine)', 'Lysis (medicine)', 'Medical personnel', 'Oral medicine', 'Medical dialysis', 'Medical implants', 'Medical journals', 'Sports and exercise medicine', 'Traditional medicine', 'Electronic medical records', 'Medicine and health sciences', 'Traditional Chinese medicine', 'Critical care and emergency medicine', 'Chemical dissociation', 'Chemistry', 'Chemokines', 'Chemoradiotherapy', 'Organic chemistry', 'Soil chemistry', 'Biochemical simulations', 'Chemical elements', 'Chemical synthesis', 'Electrochemistry', 'Environmental health', 'Health care sector', 'Health education and awareness', 'Health systems strengthening', 'Mental health therapies', 'Oral health', 'Child health', 'Health care providers', 'Health economics', 'Health informatics', 'Health insurance', 'Health care policy', 'Medicine and health sciences', 'Allied health care professionals', 'Public and occupational health', 'Socioeconomic aspects of health', 'Colorimetric protein concentration assays', 'G protein coupled receptors', 'Lipoproteins', 'Metalloproteases', 'Serine proteases', 'Serum proteins', 'Yellow fluorescent protein', 'C-reactive proteins', 'Environmental protection', 'Antisocial behavior', 'Psychological and psychosocial issues', 'Social discrimination', 'Social epidemiology', 'Social geography', 'Social mobility', 'Social play', 'Social psychology', 'Social stratification', 'Social distancing', 'Social networks', 'Animal sociality', 'Social influence', 'Social systems', 'Social theory', 'Neuropsychological testing', 'Clinical psychology', 'Enzymes', 'Escherichia coli', 'Cancer epidemiology', 'Head and neck cancers', 'Rectal cancer', 'Bladder cancer', 'Colorectal cancer', 'Renal cancer', 'Cancer risk factors', 'Breast cancer', 'Cancer detection and diagnosis', 'Type 2 diabetes', 'Urban environments', 'Variant genotypes', 'Video games', 'Ocean temperature', 'HIV diagnosis and management', 'Economic impact analysis', 'Environmental economics', 'Urban economics', 'Economic growth', 'Economic models', 'Experimental economics', 'Econometrics', 'Economics', 'Vitamin D', 'Cytoskeleton', 'Gene regulation', 'Genetically modified animals', 'MicroRNAs', 'T cells', 'Heart rate', 'Hippocampus', 'Human learning', 'Human mobility', 'Agricultural soil science', 'Algae', 'Archaeology', 'Fish physiology', 'Flowering plants', 'DNA-binding proteins', 'DNA damage', 'DNA repair', 'Drosophila melanogaster', 'Brain mapping', 'Breathing', 'Cell cultures', 'Cell differentiation', 'Cell migration', 'Cerebellum', 'Cerebral arteries', 'Chondrocytes']
boring += ['Air pollution', 'Allergies', 'Alzheimer&apos;s disease', 'B cells', 'Blood pressure', 'Bone deformation', 'Bone fracture', 'Cell disruption', 'Cell membranes', 'Cell polarity', 'Cell staining', 'Cell swimming', 'Cellulose', 'Diarrhea', 'DNA cloning', 'DNA methylation', 'DNA-RNA hybridization', 'Drag', 'Drug delivery', 'Drug dependence', 'Drug discovery', 'Drug interactions', 'Eye diseases', 'Grasslands', 'Mining engineering', 'Proteases', 'Protein domains', 'Protein folding', 'Protein sequencing', 'Protein structure comparison', 'Protein structure databases', 'Protein structure determination', 'Protein structure networks', 'Protein structure prediction', 'Protein structure', 'Prussian blue staining', 'Pseudomonas aeruginosa', 'Pseudomonas syringae', 'Rivers', 'RNA alignment', 'RNA structure', 'Water columns', 'Water pollution', 'Water quality', 'Water resources', 'Adenosine', 'Adenosine triphosphatase', 'Adenylyl cyclase', 'ADP-ribosylation', 'Agricultural irrigation', 'Agricultural workers', 'Amyloid proteins', 'Amyotrophic lateral sclerosis', 'Animal antennae', 'Animal behavior', 'Animal flight', 'Animal migration', 'Animal navigation', 'Animal wings', 'Antibacterials', 'Antibody isotype determination', 'Antibody isotypes', 'Antibody therapy', 'Antifreeze proteins', 'Antifungals', 'Antigen-presenting cells', 'Antigens', 'Antioxidants', 'Antioxidant therapy', 'Antipsychotics', 'Antitoxins', 'Aorta', 'Bacillus', 'Bacillus subtilis', 'Bacterial biofilms', 'Bacterial pathogens', 'Bacteria', 'Bamboo', 'Biocatalysis', 'Bioceramics', 'Biochemical cofactors', 'Bioengineering', 'Biofilms', 'Biomaterials', 'Biosensors', 'Biotin', 'Bird eggs', 'Bird flight', 'Blood donors', 'Blood flow', 'Blood transfusion', 'Blood volume', 'Body limbs', 'Bone and joint mechanics', 'Bone and mineral metabolism', 'Bone density', 'Bone imaging', 'Botulinum toxin', 'Botulism', 'Cardiac atria', 'Cardiac electrophysiology', 'Cardiac muscles', 'Cardiac surgery', 'Cardiac transplantation', 'Cardiac ventricles', 'Cardiology', 'Cardiomyopathies', 'Cardiovascular anatomy', 'Cardiovascular diseases', 'Cardiovascular imaging', 'Cell binding assay', 'Cell binding', 'Cell cycle and cell division', 'Cell enumeration techniques', 'Cell growth', 'Cell metabolism', 'Cell phones', 'Cellular structures and organelles', 'Central nervous system', 'Cerebrospinal fluid', 'Chickens', 'Chikungunya virus', 'Coronary heart disease', 'Corpus callosum', 'Cytoplasm', 'DNA structure', 'DNA', 'Endoscopy', 'Enzyme assays', 'Enzyme-linked immunoassays', 'Enzyme structure', 'Epidemiology', 'Health care', 'Hemoglobin', 'Histology', 'Multiple sclerosis', 'Muscle analysis', 'Muscle contraction', 'Muscular dystrophies', 'Parkinson disease', 'Pediatrics', 'Protein complexes', 'Protein denaturation', 'Protein expression', 'Protein extraction', 'Protein interaction networks', 'Protein interactions', 'Protein kinases', 'Protein-protein interactions', 'Protein secretion', 'Protein synthesis', 'Respiratory physiology', 'Schistosoma mansoni', 'Schizophrenia', 'Single nucleotide polymorphisms', 'Single strand conformational polymorphism analysis', 'Sjogren syndrome', 'Skeletal joints', 'Skin anatomy', 'Skin physiology', 'Skin tissue', 'Species diversity', 'Species interactions', 'Toxicity', 'Transfer RNA', 'Trehalose', 'Urban infrastructure', 'Uric acid', 'Vaccines', 'Vegetable oils', 'Vegetables', 'Veins', 'Viral persistence and latency', 'Viral replication', 'Vitamin E', 'Volcanic ashes', 'Volcanic eruptions', 'Volcanic rocks', 'Volcanoes', 'Weather stations', 'Weather', 'Wetlands', 'Wheat', 'White blood cells', 'Wildfires', 'Xylose', 'Zebrafish', 'Zika virus', 'Lung and intrathoracic tumors']
boring += ['Abdomen', 'Academic skills', 'Acetic acid', 'Acidic amino acids', 'Adenine', 'Adenosine', 'ADHD', 'ADP-ribosylation', 'Aggression', 'Agricultural economics', 'Agricultural workers', 'Agroforests', 'Alcoholics', 'Alcoholism', 'Allergic rhinitis', 'Aminotransferases', 'Amyotrophic lateral sclerosis', 'Animal sexual behavior', 'Antibacterials', 'Antibody isotype determination', 'Antibody isotypes', 'Antifungals', 'Antigen-presenting cells', 'Antigens', 'Antioxidant therapy', 'Antiport proteins', 'Antipsychotics', 'Antitoxins', 'Anxiety', 'Aorta', 'Aquatic respiration', 'Arabinose', 'Armed forces', 'Arteries', 'Arthritis', 'Arthropoda', 'Atrophy', 'Auditory nerves', 'Autism', 'Bacillus', 'Bacillus subtilis', 'Bacterial disk diffusion', 'Bacterial pathogens', 'Basal cell carcinomas', 'Basal ganglia', 'Behavioral economics', 'Behavioral geography', 'Biocatalysis', 'Bioceramics', 'Bioeconomics', 'Bioengineering', 'Biofilms', 'Biogeography', 'Biological transport', 'Biomass', 'Biosensors', 'Bird eggs', 'Bird flight', 'Birth weight', 'Bisexuals', 'Blood cells', 'Blood donors', 'Blood transfusion', 'Blood vessels', 'Blood volume', 'Bone and joint mechanics', 'Bone density', 'Bone marrow cells', 'Bone marrow transplantation', 'Botulinum toxin', 'Botulism', 'Bovine mastitis', 'Brain damage', 'Breast milk', 'Bronchodilators', 'Cancer screening', 'Cannabis sativa', 'Cardiac electrophysiology', 'Cardiac muscles', 'Cardiac rehabilitation', 'Cardiac surgery', 'Cardiac transplantation', 'Cardiac ventricles', 'Cardiology', 'Cardiomyocytes', 'Cardiovascular anatomy', 'Cell biology', 'Cell cycle and cell division', 'Cell enumeration techniques', 'Cell growth', 'Cell metabolism', 'Cell motility', 'Cell phones', 'Cellular structures and organelles', 'Central limit theorem', 'Centrosomes', 'Ceramography', 'Cerebrum', 'Chemical precipitation', 'Chemical radicals', 'Chemists', 'Chemotaxis', 'Chickens', 'Child development', 'Childhood obesity', 'Chitin', 'Chloroplast genome', 'Chloroplasts', 'CHO cells', 'Cholera', 'Cholines', 'Chorionic gonadotropin', 'Chromatids', 'Chromophores', 'Chromosome pairs', 'Chromosomes', 'Chromosome staining', 'Chronic kidney disease', 'Citric acid', 'Clinical trials (cancer treatment)', 'Clostridium perfringens', 'Cognitive linguistics', 'Cognitive psychology', 'Co-immunoprecipitation', 'Community structure', 'Congenital heart defects', 'Consciousness', 'Conservation biology', 'Coronary heart disease', 'Coronary stenting', 'Corticosteroid therapy', 'Cortisol', 'Coughing', 'Cyanobacteria', 'Cystic fibrosis', 'Cytolysis', 'Cytosine', 'Cytoskeletal proteins', 'Cytosol', 'Dactyloscopy', 'Deafness', 'Diastole', 'DNA annealing', 'DNA barcoding', 'DNA binding assay', 'DNA helicases', 'DNA polymerase', 'DNA recombination', 'DNA replication', 'Drug absorption', 'Drug screening', 'Duchenne muscular dystrophy', 'Dystrophin', 'Earthquake engineering', 'Economics of migration', 'Embryos', 'Endoplasmic reticulum', 'Endoscopy', 'Endothelium', 'Enzyme metabolism', 'Eosinophils', 'Epidemiology', 'Erythrocyte membrane', 'Exoskeleton', 'Exosomes', 'Experimental psychology', 'Eye muscles', 'Facial expressions', 'Fatty alcohols', 'Fertility rates', 'Fertilizers', 'Financial markets', 'Firearms', 'Fish biology', 'Fisheries science', 'Fluorescence competition', 'Fluorescence recovery after photobleaching', 'Fluorescence spectroscopy', 'Fluorides', 'Fluorine', 'Food poisoning', 'Forest ecology', 'Fossil fuels', 'Fovea centralis', 'Gamma Knife radiosurgery', 'Gastrocnemius muscles', 'Gastroenteritis', 'Gastroesophageal reflux disease', 'Gastrointestinal cancers', 'Gastrointestinal infections', 'Gene mapping', 'Gene regulatory networks', 'Genetic interactions', 'Genetic screens', 'Genetics of disease', 'Genetic testing', 'Genital anatomy', 'Genitourinary infections', 'Genome analysis', 'Genome annotation', 'Genome-wide association studies', 'Genotyping', 'Geochemistry', 'Geotechnical engineering', 'Geriatric care', 'Giant pandas', 'Giemsa staining', 'Glaucoma', 'Global health', 'Globus pallidus', 'Glucose metabolism', 'Glucose signaling', 'Glutamine', 'Glutathione chromatography', 'Glycerolization', 'Glycogen storage diseases', 'Glycolipids', 'Glycols', 'Glycoproteins', 'Gorillas', 'Gram positive bacteria', 'Guanosine triphosphatase', 'Guide RNA', 'Guillain-Barre syndrome', 'Guinea', 'Gut bacteria', 'Haemophilus influenzae', 'Headaches', 'Health services administration and management', 'Health surveys', 'Heat shock response', 'Helicobacter pylori infection', 'Helicobacter pylori', 'Helminth infections', 'Hematopoietic stem cells', 'Hemorrhagic stroke', 'Hepatitis B', 'Hepatitis C', 'Heterosexuality', 'Heterosexuals', 'Hinduism', 'Histamine', 'Histones', 'Histopathology', 'Homeostasis', 'Homosexuals', 'Homozygosity', 'Honey bees', 'Honey', 'Hong Kong', 'Host-pathogen interactions', 'HPV-16', 'Human genetics', 'Human intelligence', 'Human papillomavirus infection', 'Human rights', 'Human trafficking', 'Hydrocephalus', 'Hydrolases', 'Hydroxyl radicals', 'Hypocotyl', 'Imaging equipment', 'Imitation', 'Immunoassays', 'Immunohistochemistry techniques', 'Immunoprecipitation', 'Incisors', 'Incontinence', 'Indigenous Australian people', 'Induced pluripotent stem cells', 'Industrial chemicals', 'Industrial ecology', 'Infectious disease epidemiology', 'Influenza viruses', 'Inhalation', 'Inpatients', 'Insecticides', 'Insect pests', 'Insemination', 'Insulin', 'Integral membrane proteins', 'Intellectual property', 'Interstitial lung diseases', 'Intrinsically disordered proteins', 'Iron deficiency anemia', 'Italian people', 'Ketones', 'Kinase inhibitors', 'Labor economics', 'Laccases', 'Lactation', 'Lanthanum', 'Laparoscopic cholecystectomy', 'Laparoscopy', 'Larynx', 'Lecithin', 'Limb regeneration', 'Linguistic geography', 'Linguistics', 'Liver diseases', 'Liver fibrosis', 'Liver', 'Liver transplantation', 'Luciferase assay', 'Luciferase', 'Lung volume reduction surgery', 'Lysozyme', 'Malnutrition', 'Mammary glands', 'Mammography', 'Manganese', 'Marine ecology', 'Marine monitoring', 'Measles virus', 'Medicinal plants', 'Melanoma cells', 'Melanoma', 'Membrane protein crystallization', 'Mexican people', 'Microbial evolution', 'Microbial mutation', 'Microbial taxonomy', 'Midwives', 'Migraine without aura', 'Military personnel', 'Mineral metabolism and the kidney', 'Miocene epoch', 'Money supply and banking', 'Monosaccharides', 'Morbid obesity', 'Muscle differentiation']
boring += ['Mutagenesis', 'Mutation detection', 'Myelin sheath', 'Myofilaments', 'Myopia', 'Naphthalenes', 'National security', 'Natural disasters', 'Natural history of disease', 'Necrotic cell death', 'Neurorehabilitation', 'Neuroscience', 'Neutron scattering', 'Nicotine replacement therapy', 'Norovirus', 'Nurses', 'Nursing science', 'Nutrient and storage proteins', 'Oceanography', 'Odorants', 'Oligopolies', 'Oncogenes', 'Oncology', 'Optic neuropathy', 'Organic solvents', 'Osteoblast differentiation', 'Osteoblasts', 'Osteology', 'Osteoporosis', 'Otolaryngological procedures', 'Otorhinolaryngology', 'Outer membrane proteins', 'Outpatients', 'Pain sensation', 'Paints', 'Pakistan', 'Paleooceanography', 'Parasite evolution', 'Parasitism', 'Pathogen motility', 'Pathogens', 'Pediatrics', 'Pest control', 'Pets and companion animals', 'Phase II clinical investigation', 'Phase III clinical investigation', 'Phase IV clinical investigation', 'Phenylalanine', 'Phospholipids', 'Physical fitness', 'Pigeons', 'Pilot whales', 'Plankton', 'Plant cell walls', 'Planting', 'Plant tissues', 'Plasmodium falciparum', 'Pneumococcus', 'Pneumoconioses', 'Pneumonitis', 'Political geography', 'Pollen', 'Pollution', 'Precambrian supereon', 'Precision agriculture', 'Primates', 'Probiotics', 'Protein denaturation', 'Protein expression', 'Protein extraction', 'Protein interaction networks', 'Protein kinases', 'Protein metabolism', 'Protein-protein interactions', 'Protein secretion', 'Protein synthesis', 'Proteus vulgaris', 'Psychological rehabilitation', 'Psychoses', 'Puberty', 'Pyrococcus', 'Pyruvate', 'Regional geography', 'Riboflavin', 'Ribosomal RNA', 'Ribosomes', 'Salmon', 'Schizophrenia', 'Sciatic nerves', 'Sex determination', 'Sexual reproduction', 'Sharks', 'Skeletal muscles', 'Skin physiology', 'Skin tumors', 'Slavic people', 'Slovakian people', 'Smoking legislation', 'Smooth muscle cells', 'Social security system', 'Sociology', 'Soil ecology', 'Soil salinity', 'Soil-transmitted helminthiases', 'Soleus muscles', 'Spermatogonia', 'Sperm head', 'Stem cells', 'Stem cell therapy', 'Systole', 'Systolic pressure', 'Tanzania', 'Taxes', 'Tissue engineering', 'Tobacco', 'Toddlers', 'Transfer RNA', 'Triceps', 'Trichomes', 'Tyrosine kinases', 'Tyrosine', 'Ubiquitin ligases', 'Uric acid', 'Veterinary diseases', 'Viable cell counting', 'Vitamin A', 'Vitamins', 'War and civil unrest', 'White blood cells', 'Wildfires', 'Xylose', 'Zebrafish', 'Zebras', 'Zika virus', 'Adenosine triphosphatase', 'African American people', 'Agricultural irrigation', 'Airports', 'Altruistic behavior', 'Amhara people', 'Anesthesia', 'Aneurysms', 'Animal antennae', 'Animal behavior', 'Animal migration', 'Animal models', 'Animal wings', 'Aquaculture', 'Asthma', 'Atherosclerosis', 'Bacterial biofilms', 'Bacteria', 'Bioenergetics', 'Biological data management', 'Blood counts', 'Bone and mineral metabolism', 'Breast tissue', 'Cannabinoids', 'Cannabis', 'Cardiac atria', 'Cardiomyopathies', 'Cardiovascular imaging', 'Cognitive impairment', 'Cognitive science']
boring += ['Dengue virus', 'Depolarization', 'DNA', 'DNA transcription', 'Drug-drug interactions', 'Drug research and development', 'Dutch people', 'Ebola virus', 'Echocardiography', 'Economic agents', 'Economic analysis', 'El Niño-Southern Oscillation', 'Enzyme assays', 'Enzyme-linked immunoassays', 'Epithelium', 'Ethnicities', 'Fisheries', 'Genetic networks', 'Health statistics', 'Hemodynamics', 'Hemoglobin', 'Heparin', 'Hepatocellular carcinoma', 'Histidine', 'HIV epidemiology', 'Inflammatory diseases', 'Kidney stones', 'Leaf veins', 'Malarial parasites', 'Malaria', 'Maternal mortality', 'Mitochondrial DNA', 'Mosquitoes', 'Moths and butterflies', 'Muscle analysis', 'Muscle cells', 'Muscle contraction', 'Muscular dystrophies', 'Musculoskeletal system', 'Non-small cell lung cancer', 'Parasitic diseases', 'Pediatric infections', 'Plant breeding', 'Plant pathogens', 'Plant pathology', 'Plants', 'Prefrontal cortex', 'Protein complexes', 'Protein translation', 'Psychology', 'Radiology and imaging', 'Respiratory analysis', 'Respiratory physiology', 'Retail', 'Retinal detachment', 'Sexual and gender issues', 'Smoking habits', 'Social welfare', 'Viral disease diagnosis', 'Vitamin E', 'Wildlife', 'Agriculture', 'Agronomy', 'Alcohol consumption', 'Alcohols', 'Antibody therapy', 'Antiretroviral therapy', 'Body mass index', 'Metabolomics', 'Psycholinguistics', 'Social sciences', 'Biometrics', 'Blood flow', 'Caenorhabditis elegans', 'Clinical trials', 'Crime', 'Health care', 'Traumatic brain injury', 'DNA structure', 'Mycobacterium tuberculosis', 'Osteoarthritis', 'Physiotherapy', 'Psychophysics', 'Cerebrospinal fluid', 'Wound healing', 'Protective clothing', 'Prosthetics', 'Electroencephalography', 'Traffic safety', 'Liver and spleen scan', 'Intracellular receptors', 'Amoebas', 'Beluga whales', 'Intracellular receptors', 'Linguistic morphology', 'Monsoons', 'Muscle fibers', 'Staphylococcus aureus', 'Surgeons', 'Microsurgery']
boring += ['5-bisphosphate carboxylase oxygenase', 'Bladder', 'Blood plasma', 'Cataract surgery', 'Catheters', 'Ecological niches', 'Ecosystems', 'Herbivory', 'Horses', 'Larvae', 'Music perception', 'Oysters', 'Retina', 'Young adults']
boring += ['Abdominal muscles', 'Adolescents', 'Agarose gel electrophoresis', 'Aquatic insects', 'Biocompatibility', 'Blood-brain barrier', 'Cell physiology', 'Epidermis', 'Fatty liver', 'Goldfish', 'Middle ear', 'Plant fossils', 'Plant-herbivore interactions', 'Plant hormones', 'Plant physiology', 'Trachea', 'Ophthalmology', 'Urology', 'Theoretical biology', 'Evolutionary genetics', 'Evolutionary immunology', 'Birds', 'Caribbean', 'Coral reefs', 'Employment', 'Eye movements', 'Hearing', 'Marketing', 'Phylogenetic analysis', 'Phylogeography', 'Rabbits', 'Surface water', 'Swine', 'T cell receptors', 'Team behavior', 'Tuberculosis', 'Wolves']


prerecs = []
now = datetime.datetime.now()
startdate = now + datetime.timedelta(days=-daystocheck)
startstamp = '%4d-%02d-%02d' % (startdate.year, startdate.month, startdate.day)
i = 0
qiskeywords = ["quantum computing", "quantum computer", "qubit", "quantum information", "quantum algorithm", "qudit",
               "variational quantum", "quantum circuit", "quantum device", "quantum sensing", "quantum sensor",
               "quantum communication", "quantum error correction", "quantum key distribution",
               "quantum photonic integrated circuits", 'IBMQ', 'Qiskit', 'noisy intermediate-scale quantum', 'transmon']
for qiskeyword in qiskeywords:
    i += 1
#    tocurl = 'https://journals.plos.org/plosone/search?unformattedQuery=abstract%3A%22%22' + qiskeyword + '%22%22&q=abstract%3A%22%22' + qiskeyword + '%22%22&sortOrder=DATE_NEWEST_FIRST&utm_content=b&utm_campaign=ENG-467'
    apiurl = 'https://api.plos.org/search?q=' + wheretosearch + ':%22' + qiskeyword + '%22%20and%20journal:%22PLoS%20ONE%22%20and%20publication_date:[' + startstamp + 'T00:00:00Z%20TO%20' + ejlmod3.stampoftoday() + 'T23:59:59Z]&fl=id,publication_date&rows=' + str(rpp) + '&wt=xml'
    ejlmod3.printprogress('=', [[i, len(qiskeywords), qiskeyword], [apiurl]])
    try:
        driver.get(apiurl)
        apipages = [BeautifulSoup(driver.page_source, features="lxml")]
    except:
        time.sleep(random.randint(100,115))
        driver.get(apiurl)
        apipages = [BeautifulSoup(driver.page_source, features="lxml")]        
    time.sleep(random.randint(10,15))
    for result in apipages[0].find_all('result'):
        numfound = int(result['numfound'])
        pages = (numfound-1)//rpp + 1 
        print('   numfound = ', numfound)
        for page in range(pages-1):
            nexturl = apiurl + '&start=' + str(1+rpp*(page+1))
            ejlmod3.printprogress('=', [[i, len(qiskeywords), qiskeyword], [page+1, pages], [nexturl]])
            try:
                driver.get(nexturl)
                apipages.append(BeautifulSoup(driver.page_source, features="lxml"))
            except:
                time.sleep(random.randint(100,115))
                driver.get(nexturl)
                apipages.append(BeautifulSoup(driver.page_source, features="lxml"))
            time.sleep(random.randint(10,15))
    for apipage in apipages:
        for doc in apipage.find_all('doc'):
            rec = {'jnl' : 'PLoS One', 'tc' : 'P', 'fc' : 'kc'}
            for s in doc.find_all('str', attrs = {'name' : 'id'}):
                rec['doi'] = s.text
            for date in doc.find_all('date', attrs = {'name' : 'publication_date'}):
                rec['date'] = date.text
            if not rec['doi'] in dois and ejlmod3.checkinterestingDOI(rec['doi']):
                dois.append(rec['doi'])
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    prerecs.append(rec)
        print('   %4i records so far' % (len(prerecs)))

baseurls = []
for (sec, fc, pages) in [('quantum_computing', 'kc', 1), #64
                         #('computer_and_information_sciences', 'c', 1), #32033 too much noise
                         ('astronomical_sciences', 'a', 2), #269
                         ('mathematics', 'm', 110),#34929
                         ('astrophysics', 'a', 1),#36
                         ('condensed_matter_physics', 'f', 6),#4651
                         ('gravitation', 'g', 2),#111
                         ('mathematical_physics', 'm', 1),#46
                         ('quantum_mechanics', 'k', 2),#156
                         ('physics', '', 50), #26665
                         ('relativity', 'g', 1)]:#10
    tocurl = 'https://journals.plos.org/plosone/browse/' + sec + '?resultView=list&sortOrder=DATE_NEWEST_FIRST'
    baseurls.append((sec, tocurl, pages, fc))


i = 0
for (sec, baseurl, pages, fc) in baseurls:
    i += 1
    seccount = 0
    for page in range(pages):
        newdois = []
        tocurl = baseurl + '&page=' + str(page+1)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.printprogress('=', [[i, len(baseurls), sec], [page+1, pages], [tocurl]])
        for ul in tocpage.body.find_all('ul', attrs = {'id' : 'search-results'}):
            for li in ul.find_all('li'):
                rec = {'jnl' : 'PloS One', 'tc' : 'P', 'note' : []}
                rec['doi'] = li['data-doi']
                rec['date'] = li['data-pdate'][:10]
                rec['year'] = li['data-pdate'][:4]
                if fc: rec['fc'] = fc
                if int(rec['year']) > ejlmod3.year(backwards=years):
                    seccount += 1
                    #rec['note'] = [ 'SECCOUNT(%s) = %5i' % (sec, seccount) ]
                    newdois.append(rec['doi'])
                    if not rec['doi'] in dois and ejlmod3.checkinterestingDOI(rec['doi']):
                        dois.append(rec['doi'])
                        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                            prerecs.append(rec)
        print('   %4i records so far' % (len(prerecs)))
        if not newdois:
            break
        time.sleep(random.randint(3,7))

recs = []
actualchunk = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    arturl = 'https://journals.plos.org/plosone/article?id=' + rec['doi']
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [arturl], [len(recs)]])
    driver.get(arturl)
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_abstract', 'keywords', 'citation_title',
                                        'citation_firstpage', 'citation_issue', 'citation_volume',
                                        'citation_pdf_url'])#, 'citation_author', 'citation_author_institution'])
    if 'keyw' in rec and len(rec['keyw']) == 1:
        rec['keyw'] = re.split(',', rec['keyw'][0])
        for kw in rec['keyw']:
            if kw in boring: keepit = False
    ejlmod3.globallicensesearch(rec, artpage)
    #ORCIDs only in body
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'author-list'}):
        rec['autaff'] = []
        for li in ul.find_all('li'):
            #name
            for a in li.find_all('a', attrs = {'class' : 'author-name'}):
                rec['autaff'].append([re.sub(',', '', a.text.strip())])
            if rec['autaff']:
                #ORCID
                for p in li.find_all('p', attrs = {'class' : 'orcid'}):
                    for a in p.find_all('a'):
                        rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
                #email
                if len(rec['autaff'][-1]) == 1:
                    for a in li.find_all('a'):
                        if a.has_attr('href') and a['href'][:6] == 'mailto':
                            rec['autaff'][-1].append(re.sub('.*:', 'EMAIL:', a['href']))
                #affiliation
                for p in li.find_all('p'):
                    if p.has_attr('id') and p['id'][:7] == 'authAff':
                        for span in p.find_all('span'):
                            span.decompose()
                        rec['autaff'][-1].append(p.text.strip())
    time.sleep(random.randint(4,8))
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        actualchunk.append(rec)
        if len(actualchunk) == chunksize:
            jnlfilename = 'plosone_%s_%03i' % (ejlmod3.stampoftoday(), len(recs)//chunksize)
            ejlmod3.writenewXML(actualchunk, publisher, jnlfilename)
            actualchunk = []
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

if actualchunk:
    jnlfilename = 'plosone_%s_%03i' % (ejlmod3.stampoftoday(), len(recs)//chunksize+1)
    ejlmod3.writenewXML(actualchunk, publisher, jnlfilename)

driver.quit()
