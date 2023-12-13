# -*- coding: UTF-8 -*-
#program to harvest OUP-journals
# FS 2023-12-10

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

skipalreadyharvested = True
bunchsize = 10

jnlfilename = 'OUP_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


tmpdir = '/tmp'
def tfstrip(x): return x.strip()
def fsunwrap(tag):
    try: 
        for em in tag.find_all('em'):
            cont = em.string
            em.replace_with(cont)
    except:
        print('fsunwrap-em-problem')
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
        print('fsunwrap-sup-problem')
    try: 
        for sub in tag.find_all('sub'):
            cont = sub.string
            sub.replace_with('_'+cont)
    except:
        print('fsunwrap-sub-problem')
    try: 
        for i in tag.find_all('i'):
            cont = i.string
            i.replace_with(cont)
    except:
        print('fsunwrap-i-problem')
    try: 
        for form in tag.find_all('formula',attrs={'formulatype': 'inline'}):
            form.replace_with(' [FORMULA] ')
    except:
        print('fsunwrap-form-problem')
    return tag

publisher = 'Oxford University Press'

sample = {'10.1093/pasj/psx061' : {'all' : 17 , 'core' : 17},
          '10.1093/mnras/218.4.629' : {'all' : 118 , 'core' : 118},
          '10.1143/PTPS.153.139' : {'all' : 121 , 'core' : 121},
          '10.1093/mnras/215.4.575' : {'all' : 147 , 'core' : 147},
          '10.1093/nsr/nwy088' : {'all' : 14 , 'core' : 14},
          '10.1093/mnras/182.2.147' : {'all' : 417 , 'core' : 417},
          '10.1093/mnras/191.3.483' : {'all' : 27 , 'core' : 27},
          '10.1093/mnras/150.1.1' : {'all' : 287 , 'core' : 287},
          '10.1093/mnras/224.1.131' : {'all' : 17 , 'core' : 17},
          '10.1093/mnras/227.2.403' : {'all' : 36 , 'core' : 36},
          '10.1093/mnras/273.3.583' : {'all' : 47 , 'core' : 47},
          '10.1093/mnras/216.2.403' : {'all' : 62 , 'core' : 62},
          '10.1143/ptp/3.4.440' : {'all' : 46 , 'core' : 46},
          '10.1093/mnras/128.4.307' : {'all' : 190 , 'core' : 190},
          '10.1093/mnras/stw1876' : {'all' : 52 , 'core' : 52},
          '10.1093/mnras/270.3.480' : {'all' : 117 , 'core' : 117},
          '10.1093/mnras/stv2162' : {'all' : 93 , 'core' : 93},
          '10.1093/mnras/sty618' : {'all' : 349 , 'core' : 349},
          '10.1093/mnras/stz1317' : {'all' : 65 , 'core' : 65},
          '10.1093/mnras/stz514' : {'all' : 82 , 'core' : 82},
          '10.1093/mnras/239.3.845' : {'all' : 37 , 'core' : 37},
          '10.1093/mnras/sty982' : {'all' : 93 , 'core' : 93},
          '10.1093/nsr/nwz227' : {'all' : 21 , 'core' : 21},
          '10.1143/PTP.33.423' : {'all' : 44 , 'core' : 44},
          '10.1093/mnras/116.6.662' : {'all' : 27 , 'core' : 27},
          '10.1093/mnras/260.3.675' : {'all' : 66 , 'core' : 66},
          '10.1093/mnras/237.2.355' : {'all' : 85 , 'core' : 85},
          '10.1093/nsr/nwy153' : {'all' : 37 , 'core' : 37},
          '10.1093/ptep/ptaa083' : {'all' : 34 , 'core' : 34},
          '10.1093/mnras/255.1.119' : {'all' : 43 , 'core' : 43},
          '10.1093/mnras/78.1.3' : {'all' : 44 , 'core' : 44},
          '10.1093/mnras/194.2.439' : {'all' : 57 , 'core' : 57},
          '10.1093/mnras/203.4.1049' : {'all' : 56 , 'core' : 56},
          '10.1093/mnras/91.5.483' : {'all' : 63 , 'core' : 63},
          '10.1093/mnras/258.1.41P' : {'all' : 121 , 'core' : 121},
          '10.1093/mnras/stz623' : {'all' : 39 , 'core' : 39},
          '10.1093/mnras/173.3.729' : {'all' : 170 , 'core' : 170},
          '10.1093/mnras/195.3.467' : {'all' : 344 , 'core' : 344},
          '10.1093/mnras/101.8.367' : {'all' : 63 , 'core' : 63},
          '10.1093/mnras/278.2.525' : {'all' : 62 , 'core' : 62},
          '10.1093/mnras/71.5.460' : {'all' : 165 , 'core' : 165},
          '10.1093/comjnl/7.2.155' : {'all' : 60 , 'core' : 60},
          '10.1093/mnras/264.1.201' : {'all' : 145 , 'core' : 145},
          '10.1093/mnras/265.3.533' : {'all' : 163 , 'core' : 163},
          '10.1111/j.1365-246X.2010.04804.x' : {'all' : 54 , 'core' : 54},
          '10.1143/PTP.20.948' : {'all' : 92 , 'core' : 92},
          '10.1143/PTPS.62.236' : {'all' : 43 , 'core' : 43},
          '10.1143/PTP.65.1772' : {'all' : 35 , 'core' : 35},
          '10.1093/mnras/167.1.31P' : {'all' : 292 , 'core' : 292},
          '10.1093/mnras/221.4.1023' : {'all' : 58 , 'core' : 58},
          '10.1093/mnras/262.3.627' : {'all' : 208 , 'core' : 208},
          '10.1093/biomet/26.4.404' : {'all' : 46 , 'core' : 46},
          '10.1143/ptp/5.4.570' : {'all' : 44 , 'core' : 44},
          '10.1143/PTP.56.1454' : {'all' : 78 , 'core' : 78},
          '10.1093/mnras/138.4.495' : {'all' : 95 , 'core' : 95},
          '10.1093/imamat/6.1.76' : {'all' : 57 , 'core' : 57},
          '10.1093/mnras/182.3.443' : {'all' : 107 , 'core' : 107},
          '10.1143/ptp.37.831' : {'all' : 53 , 'core' : 53},
          '10.1143/PTP.37.831' : {'all' : 53 , 'core' : 53},
          '10.1093/mnras/104.5.273' : {'all' : 218 , 'core' : 218},
          '10.1093/mnras/stv2422' : {'all' : 76 , 'core' : 76},
          '10.1111/j.1365-246X.1968.tb00216.x' : {'all' : 48 , 'core' : 48},
          '10.1155/S107379280320917X' : {'all' : 65 , 'core' : 65},
          '10.1093/mnras/199.4.883' : {'all' : 457 , 'core' : 457},
          '10.1093/comjnl/13.3.317' : {'all' : 71 , 'core' : 71},
          '10.1143/PTP.85.1' : {'all' : 52 , 'core' : 52},
          '10.1143/PTPS.88.1' : {'all' : 94 , 'core' : 94},
          '10.1143/PTPS.6.93' : {'all' : 88 , 'core' : 88},
          '10.1093/mnras/stw2759' : {'all' : 192 , 'core' : 192},
          '10.1111/j.1365-2966.2004.08097.x' : {'all' : 264 , 'core' : 264},
 #         '10.1093/oso/9780198739623.001.0001' : {'all' : 28 , 'core' : 28},
          '10.1093/acprof:oso/9780198507628.001.0001' : {'all' : 23 , 'core' : 23},
          '10.1093/acprof:oso/9780198758884.001.0001' : {'all' : 39 , 'core' : 39},
#          '10.1093/acprof:oso/9780198528906.001.0001' : {'all' : 121 , 'core' : 121},
          '10.1093/oso/9780198570899.001.0001' : {'all' : 49 , 'core' : 49},
          '10.1093/acprof:oso/9780198525004.001.0001' : {'all' : 65 , 'core' : 65},
          '10.1093/acprof:oso/9780199205677.001.0001' : {'all' : 60 , 'core' : 60},
          '10.1093/acprof:oso/9780199227259.001.0001' : {'all' : 43 , 'core' : 43},
          '10.1093/acprof:oso/9780198509141.001.0001' : {'all' : 53 , 'core' : 53},
          '10.1093/acprof:oso/9780198509233.001.0001' : {'all' : 75 , 'core' : 75}}
#          '10.1093/acprof:oso/9780198508717.001.0001' : {'all' : 88 , 'core' : 88}}


    
ptepcollcode = {'A0' : 'General physics', 'A00' : 'Classical mechanics', 'A01' : 'Electromagentism',
                'A02' : 'Other topics in general physics', 'A1' : 'Mathematical physics', 'A10' : 'Integrable systems and exact solutions',
                'A11' : 'Solitons', 'A12' : 'Rigorous results', 'A13' : 'Other topics in mathematical physics',
                'A2' : 'Computational physics', 'A20' : 'The algorithm of numerical calculations', 'A21' : 'Numerical diagonalization',
                'A22' : 'Monte-Carlo simulations', 'A23' : 'Molecular dynamics simulations', 'A24' : 'Other numerical methods',
                'A3' : 'Nonlinear dynamics', 'A30' : 'Dynamical systems', 'A31' : 'The other dynamical systems such as cellular-automata and coupled map lattices',
                'A32' : 'Quantum chaos', 'A33' : 'Classical chaos', 'A34' : 'Other topics in nonlinear dynamics',
                'A4' : 'Statistical mechanics - equilibrium systems', 'A40' : 'Critical phenomena, phase diagrams, phase transitions', 'A41' : 'Spin-glass, random spins',
                'A42' : 'Classical spins', 'A43' : 'Quantum spins', 'A44' : 'Neural networks',
                'A45' : 'Informational statistical physics', 'A46' : 'Quantum statistical mechanics', 'A47' : 'Other topics in equilibrium statistical mechanics',
                'A5' : 'Statistical mechanics - nonequilibrium systems', 'A50' : 'Stochastic processes, stochastic models and percolations', 'A51' : 'Relaxations, hysteresis, response, transport in classical systems',
                'A52' : 'Transport of quantum systems', 'A53' : 'Reaction-diffusion systems', 'A54' : 'Pattern formation, fracture, self-organizations',
                'A55' : 'Synchronization; coupled oscillators', 'A56' : 'Nonlinear and nonequilibrium phenomena', 'A57' : 'Nonequilibrium steady states',
                'A58' : 'Other topics in nonequilibrium statistical mechanics', 'A6' : 'Quantum physics', 'A60' : 'Foundation of quantum mechanics',
                'A61' : 'Quantum information', 'A62' : 'Quantum phase transition', 'A63' : 'Quantum many-body systems',
                'A64' : 'Other topics in quantum mechanics', 'A7' : 'Thermodynamics and thermodynamic processes', 'A70' : 'Mathematical theory of thermodynamics',
                'A71' : 'Molecular motors', 'A72' : 'Energy transfers in biological systems', 'A73' : 'Other thermal processes',
                'B0' : 'Gauge field theories', 'B00' : 'Lattice gauge field theories', 'B01' : 'Spontaneous symmetry breaking',
                'B02' : 'Confinement', 'B03' : 'Chern Simons theories', 'B04' : 'Quantization and formalism',
                'B05' : 'Other topics in gauge field theories', 'B1' : 'Supersymmetry', 'B10' : 'Extended supersymmetry',
                'B11' : 'Supergravity', 'B12' : 'Supersymmetry breaking', 'B13' : 'Supersymmetry phenomenology',
                'B14' : 'Dynamics of supersymmteric gauge theories', 'B15' : 'Supersymmetric quantum mechanics', 'B16' : 'Supersymmetric field theory',
                'B17' : 'Other topics in supersymmetry', 'B2' : 'String theory', 'B20' : 'String duality',
                'B21' : 'AdS/CFT correspondence', 'B22' : 'Black holes in string theory', 'B23' : 'Brane and its dynamics',
                'B24' : 'CFT approach in string theory', 'B25' : 'M theory, matrix theory', 'B26' : 'Tachyon condensation',
                'B27' : 'Topological field theory', 'B28' : 'String field theory', 'B29' : 'Other topics in string theory',
                'B3' : 'Quantum field theory', 'B30' : 'General', 'B31' : 'Symmetries and anomalies',
                'B32' : 'Renormalization and renormalization group equation', 'B33' : 'Field theories in higher dimensions', 'B34' : 'Field theories in lower dimensions',
                'B35' : 'Solitons, monopoles and instantons, 1/N expansion', 'B36' : 'Composite states and effective theories', 'B37' : 'Various models of field theory',
                'B38' : 'Lattice field theories', 'B39' : 'Quantization and formalism', 'B4' : 'Model building',
                'B40' : 'Beyond the Standard Model', 'B41' : 'Compactification and string', 'B42' : 'Grand unified theories',
                'B43' : 'Models with extra dimensions', 'B44' : 'Technicolor and composite models', 'B45' : 'Unified models with gravity',
                'B46' : 'Other topics in model building', 'B5' : 'Weak interactions and related phenomena', 'B50' : 'Electromagnetic processes and properties',
                'B51' : 'B, D, K physics', 'B52' : 'CP violation', 'B53' : 'Higgs physics',
                'B54' : 'Neutrino physics', 'B55' : 'Quark masses and Standard Model parameters', 'B56' : 'Rare decays',
                'B57' : 'Standard Model', 'B58' : 'Supersymmetric Standard Model', 'B59' : 'Other topics in weak interactions and related phenomena',
                'B6' : 'Strong interactions and related phenomena', 'B60' : 'Chiral lagrangians', 'B61' : 'Deep inelastic scattering',
                'B62' : 'Hadronic colliders', 'B63' : 'Jets', 'B64' : 'Lattice QCD',
                'B65' : 'Perturbative QCD', 'B66' : 'Spin and polarization effects', 'B67' : 'Sum rules',
                'B68' : 'Holographic approach to QCD', 'B69' : 'Other topics in strong interactions and related phenomena', 'B7' : 'Astroparticle physics',
                'B70' : 'Baryogenesis', 'B71' : 'Dark matter', 'B72' : 'Inflation',
                'B73' : 'Cosmology of theories beyond the Standard Model', 'B74' : 'High energy cosmic rays', 'B75' : 'Solar and atmospheric neutrinos',
                'B76' : 'Thermal field theory', 'B77' : 'Other topics in astroparticle physics', 'B8' : 'Mathematical methods',
                'B80' : 'Differential and algebraic geometry', 'B81' : 'Integrable systems', 'B82' : 'Noncommutative geometry',
                'B83' : 'Matrix models', 'B84' : 'Quantum groups', 'B85' : 'Bethe ansatz, exact S-matrix',
                'B86' : 'Statistical methods, random systems', 'B87' : 'Other topics in mathematical methods', 'C0' : 'Standard Model and related topics',
                'C00' : 'Quantum chromodynamics', 'C01' : 'Electroweak model, Higgs bosons, electroweak symmetry breaking', 'C02' : 'Cabibbo-Kobayashi-Maskawa quark-mixing matrix',
                'C03' : 'CP violation', 'C04' : 'Neutrino masses, mixing, and oscillations', 'C05' : 'Quark model',
                'C06' : 'Structure functions, fragmentation functions', 'C07' : 'Particle properties', 'C08' : 'Tests of conservation laws',
                'C09' : 'Other topics', 'C1' : 'Hypothetical particles and concepts', 'C10' : 'Supersymmmetry',
                'C11' : 'Dynamical electroweak symmetry breaking', 'C12' : 'Grand unified theories', 'C13' : 'Searches for quark and lepton compositeness',
                'C14' : 'Extra dimensions', 'C15' : 'Axions', 'C16' : 'Free quark searches',
                'C17' : 'Magnetic monopoles', 'C18' : 'Heavy vector bosons', 'C19' : 'Other topics',
                'C2' : 'Collider experiments', 'C20' : 'Hadron collider experiments', 'C21' : 'Lepton collider experiments',
                'C22' : 'Electron-proton collider experiments', 'C23' : 'Other topics', 'C3' : 'Experiments using particle beams',
                'C30' : 'Experiments using hadron beams', 'C31' : 'Experiments using charged lepton beams', 'C32' : 'Experiments using neutrino beams',
                'C33' : 'Experiments using photon beams', 'C34' : 'Other topics', 'C4' : 'Non-accelerator experiments',
                'C40' : 'Experiments using RI source', 'C41' : 'Laser experiments', 'C42' : 'Reactor experiments',
                'C43' : 'Underground experiments', 'C44' : 'Other topics', 'C5' : 'Other topics in experimental particle physics',
                'C50' : 'Other topics in experimental particle physics', 'D0' : 'Fundamental interactions and nuclear properties', 'D02' : 'Weak interactions in nuclear system',
                'D03' : 'Electromagnetic interactions in nuclear system', 'D04' : 'Nuclear matter and bulk properties of nuclei', 'D05' : 'Few-body problems in nuclear system',
                'D06' : 'Effective interactions in nuclear system', 'D1' : 'Nuclear structure', 'D10' : 'Nuclear many-body theories',
                'D11' : 'Models of nuclear structure', 'D12' : 'General properties of nuclei --- systematics and theoretical analysis', 'D13' : 'Stable and unstable nuclei',
                'D14' : 'Hypernuclei', 'D15' : 'Mesic nuclei and exotic atoms', 'D2' : 'Nuclear reactions and decays',
                'D20' : 'General reaction theories', 'D21' : 'Models of nuclear reactions', 'D22' : 'Light ion reactions',
                'D23' : 'Heavy-ion reactions', 'D24' : 'Photon and lepton reactions', 'D25' : 'Hadron reactions',
                'D26' : 'Fusion, fusion-fission reactions and superheavy nuclei', 'D27' : 'Reactions induced by unstable nuclei', 'D28' : 'Relativistic heavy-ion collisions',
                'D29' : 'Nuclear decays and radioactivities', 'D3' : 'Quarks, hadrons and QCD in nuclear physics', 'D30' : 'Quark matter',
                'D31' : 'Quark-gluon plasma', 'D32' : 'Hadron structure and interactions', 'D33' : 'Hadrons and quarks in nuclear matter',
                'D34' : 'Lattice QCD calculations in nuclear physics', 'D4' : 'Nuclear astrophysics', 'D40' : 'Nucleosynthesis',
                'D41' : 'Nuclear matter aspects in nuclear astrophysics', 'D42' : 'Nuclear physics aspects in explosive environments', 'D5' : 'Other topics in nuclear physics',
                'D50' : 'Other topics in nuclear physics', 'E0' : 'Gravity', 'E00' : 'Gravity in general',
                'E01' : 'Relativity', 'E02' : 'Gravitational waves', 'E03' : 'Alternative theory of gravity',
                'E04' : 'Higher-dimensional theories', 'E05' : 'Quantum gravity', 'E1' : 'Basic astrophysical processes',
                'E10' : 'Astrophysical processes in general', 'E11' : 'Radiative processes and thermodynamics', 'E12' : 'Chemical and nuclear reactions',
                'E13' : 'Kinetic theory and plasma', 'E14' : 'Hydrodynamics and magnetohydrodynamics', 'E15' : 'Relativistic dynamics',
                'E16' : 'Stellar dynamics', 'E2' : 'Stars and stellar systems', 'E20' : 'Stars and stellar systems in general',
                'E21' : 'The sun and solar system', 'E22' : 'Exoplanets', 'E23' : 'Interstellar matter and magnetic fields',
                'E24' : 'Star formation', 'E25' : 'Stellar structure and evolution', 'E26' : 'Supernovae',
                'E27' : 'Galaxies and clusters', 'E28' : 'Extragalactic medium and fields', 'E3' : 'Compact objects 　',
                'E30' : 'Compact objects in general', 'E31' : 'Black holes', 'E32' : 'Neutron stars',
                'E33' : 'Pulsars', 'E34' : 'Accretion, accretion disks', 'E35' : 'Relativistic jets',
                'E36' : 'Massive black holes', 'E37' : 'Gamma ray bursts', 'E38' : 'Physics of strong fields',
                'E4' : 'Cosmic rays and neutrinos', 'E40' : 'Cosmic rays and neutrino in general', 'E41' : 'Cosmic rays',
                'E42' : 'Acceleration of particles', 'E43' : 'Propagation of cosmic rays', 'E44' : 'Cosmic gamma rays',
                'E45' : 'Neutrinos', 'E5' : 'Large scale structure of the universe', 'E50' : 'Large scale structure in general',
                'E51' : 'Superclusters and voids', 'E52' : 'Statistical analysis of large scale structure', 'E53' : 'Large scale structure formation',
                'E54' : 'Semi-analytic modeling', 'E55' : 'Cosmological simulations', 'E56' : 'Cosmological perturbation theory',
                'E6' : 'Observational cosmology', 'E60' : 'Observational cosmology in general', 'E61' : 'Cosmometry',
                'E62' : 'Gravitational lensing', 'E63' : 'Cosmic background radiations', 'E64' : 'Dark energy and dark matter',
                'E65' : 'Probes of cosmology', 'E7' : 'Particle cosmology', 'E70' : 'Particle cosmology in general',
                'E71' : 'Big bang nucleosynthesis', 'E72' : 'Baryon asymmetry', 'E73' : 'Cosmological phase transitions and topological defects',
                'E74' : 'Cosmology of physics beyond the Standard Model', 'E75' : 'Physics of the early universe', 'E76' : 'Quantum field theory on curved space',
                'E8' : 'Inflation and cosmogenesis', 'E80' : 'Inflation and cosmology in general', 'E81' : 'Inflation',
                'E82' : 'Alternative to inflation', 'E83' : 'String theory and cosmology', 'E84' : 'Extra dimensions',
                'E85' : 'Transplanckian physics', 'E86' : 'Quantum cosmology', 'F0' : 'Cosmic ray particles',
                'F00' : 'Instrumentation and technique', 'F01' : 'Earth-Solar system and Heliosphere', 'F02' : 'Origin, composition, propagation and interactions of cosmic rays',
                'F03' : 'Ultra-high energy phenomena of cosmic rays', 'F04' : 'Other topics', 'F1' : 'Photons',
                'F10' : 'Instrumentation and technique', 'F11' : 'Radiation from galactic objects', 'F12' : 'Radiation from extragalactic objects',
                'F13' : 'High energy and non-thermal phenomena', 'F14' : 'Cosmic microwave background and extragalactic background lights', 'F15' : 'Other topics',
                'F2' : 'Neutrino', 'F20' : 'Instrumentation and technique', 'F21' : 'Solar, atmospheric and earth-originated neutrinos',
                'F22' : 'Neutrinos from supernova remnant and other astronomical objects', 'F23' : 'Neutrino mass, , mixing, oscillation and interaction', 'F24' : 'Other topics',
                'F3' : 'Gravitational wave', 'F30' : 'Instrumentation and technique', 'F31' : 'Expectation and estimation of gravitational radiation',
                'F32' : 'Calibration and operation of gravitational wave detector', 'F33' : 'Network system, coincident signal in other radiation bands', 'F34' : 'Other topics',
                'F4' : 'Dark matter, dark energy and particle physics', 'F40' : 'Instrumentation and technique', 'F41' : 'Laboratory experiments',
                'F42' : 'Observational result on astrophysical phenomena', 'F43' : 'Interpretation and explanation of observation and experiment', 'F44' : 'Cosmology, early universe and quantum gravity',
                'F45' : 'Other topics', 'G0' : 'Accelerators', 'G00' : 'Colliders',
                'G01' : 'Light sources', 'G02' : 'Ion accelerators', 'G03' : 'Electron accelerators',
                'G04' : 'Beam sources', 'G05' : 'Accelerator components', 'G06' : 'Accelerator design',
                'G07' : 'Others', 'G1' : 'Physics of beams', 'G10' : 'Beam dynamics',
                'G11' : 'Beam instabilities and cures', 'G12' : 'Beam measurement and manipulation', 'G13' : 'Interaction of beams',
                'G14' : 'Novel acceleration scheme', 'G15' : 'Accelerator theory', 'G16' : 'Others',
                'G2' : 'Application of beams', 'G20' : 'Scientific application', 'G21' : 'Medical application',
                'G22' : 'Industrial application', 'G23' : 'Others', 'H0' : 'General issue for instrumentation',
                'H00' : 'Interaction of radiation with matter', 'H01' : 'Concepts of the detector', 'H02' : 'Simulation and detector modeling',
                'H03' : 'Radiation damage/hardness', 'H04' : 'Dosimetry and apparatus', 'H1' : 'Detectors, apparatus and methods for the physics using accelerators',
                'H10' : 'Experimental detector systems', 'H11' : 'Gaseous detectors', 'H12' : 'Semiconductor detectors',
                'H13' : 'Calorimeters', 'H14' : 'Particle identification', 'H15' : 'Photon detectors',
                'H16' : 'Neutrino detectors', 'H17' : 'Instrumentation for medical, biological and materials research', 'H2' : 'Detectors, apparatus and methods for non-accelerator physics',
                'H20' : 'Instrumentation for underground experiments', 'H21' : 'Instrumentation for ground observatory', 'H22' : 'Instrumentation for space observatory',
                'H3' : 'Detector readout concepts, electronics, trigger and data acquisition methods', 'H30' : 'Electronic circuits', 'H31' : 'Front-end electronics',
                'H32' : 'Microelectronics', 'H33' : 'Digital Signal Processor', 'H34' : 'Data acquisition',
                'H35' : 'Trigger', 'H36' : 'Online farm and networking', 'H37' : 'Control and monitor systems',
                'H4' : 'Software and analysis related issue for instrumentation', 'H40' : 'Computing, data processing, data reduction methods', 'H41' : 'Image processing',
                'H42' : 'Pattern recognition, cluster finding, calibration and fitting methods', 'H43' : 'Software architectures', 'H5' : 'Engineering and technical issues',
                'H50' : 'Detector system design, construction technologies and materials', 'H51' : 'Manufacturing', 'H52' : 'Detector alignment and calibration methods',
                'H53' : 'Detector cooling and thermo-stabilization', 'H54' : 'Gas systems and purification', 'H55' : 'Machine detector interface',
                'I0' : 'Structure, mechanical and acoustical properties', 'I00' : 'Structure of liquids and solids', 'I01' : 'Equations of state',
                'I02' : 'Phase equilibria and phase transitions', 'I03' : 'Lattice dynamics and crystal statistics', 'I04' : 'Mechanical properties',
                'I05' : 'Defects', 'I06' : 'Liquid crystals', 'I07' : 'Acoustical properties',
                'I08' : 'Other topics', 'I1' : 'Thermal properties and nonelectronic transport properties', 'I10' : 'Thermal properties',
                'I11' : 'Thermal transport', 'I12' : 'Ionic transport', 'I13' : 'Liquid metal',
                'I14' : 'Other topics', 'I2' : 'Quantum fluids and solids', 'I20' : 'Liquid and solid helium',
                'I21' : 'Supersolid', 'I22' : 'Quantum states of cold gases', 'I23' : 'Other topics',
                'I3' : 'Low dimensional systems -nonelectronic properties', 'I30' : 'Surfaces, interfaces and thin films', 'I31' : 'Clusters',
                'I32' : 'Graphene, fullerene', 'I33' : 'Nanotube, nanowire', 'I34' : 'Quantum dot',
                'I35' : 'Other nanostructures', 'I36' : 'Other topics', 'I4' : 'Electron states in condensed matter',
                'I40' : 'Metal', 'I41' : 'Semiconductor', 'I42' : 'Organics',
                'I43' : 'd- and f- electron systems', 'I44' : 'First-principles calculations', 'I45' : 'Mott transitions',
                'I46' : 'Strong correlations', 'I47' : 'Other topics', 'I5' : 'Electronic transport properties',
                'I50' : 'Disordered systems, Anderson transitions', 'I51' : 'Hall effect', 'I52' : 'Magnetoresistance',
                'I53' : 'Thermal transport', 'I54' : 'Thermoelectric effect', 'I55' : 'Spin transport',
                'I56' : 'Other topics', 'I6' : 'Superconductivity', 'I60' : 'Mechanism and paring symmetry',
                'I61' : 'Phenomenology', 'I62' : 'Vortices', 'I63' : 'Tunnel junction and Josephson effect',
                'I64' : 'High-Tc superconductors and related materials', 'I65' : 'Heavy fermion superconductors', 'I66' : 'Organic superconductors',
                'I67' : 'Light-element superconductors', 'I68' : 'Other topics', 'I7' : 'Magnetic and dielectric properties',
                'I70' : 'Magnetic transitions', 'I71' : 'Frustration', 'I72' : 'Kondo effect, heavy fermions',
                'I73' : 'Magnetic resonance', 'I74' : 'Magnetism in nanosystems', 'I75' : 'Spintronics',
                'I76' : 'Dielectric properties', 'I77' : 'Orbital effects', 'I78' : 'Multiferroics',
                'I79' : 'Other topics', 'I8' : 'Optical properties', 'I80' : 'Spectroscopy',
                'I81' : 'Nonlinear optics', 'I82' : 'Exitons and polaritons', 'I83' : 'Photo-induced phase transitions',
                'I84' : 'Ultrafast phenomena', 'I85' : 'Other topics', 'I9' : 'Low dimensional systems -electronic properties',
                'I90' : 'Surfaces, interfaces and thin films', 'I91' : 'Clusters', 'I92' : 'Graphene, fullerene',
                'I93' : 'Nanotube, nanowire', 'I94' : 'Quantum dot', 'I95' : 'Other nanostructures',
                'I96' : 'Quantum Hall effect', 'I97' : 'Other topics', 'J0' : 'Mechanics, elasticity and rheology',
                'J00' : 'Frictions', 'J01' : 'Rheology', 'J02' : 'Linear and nonlinear elasticity',
                'J03' : 'Other mechanical problems', 'J1' : 'Fluid dynamics', 'J10' : 'Complex fluids',
                'J11' : 'Incompressible fluids', 'J12' : 'Compressible fluids and dilute gases', 'J13' : 'Electro-magnetic fluids',
                'J14' : 'Fluids in earth physics and astronomy', 'J15' : 'Convections and turbulences', 'J16' : 'Waves',
                'J17' : 'Creep flows', 'J18' : 'Vortices', 'J19' : 'Other topics in fluid dynamics',
                'J2' : 'Plasma physics', 'J20' : 'Nuclear fusions', 'J21' : 'Plasma astrophysics',
                'J22' : 'Waves, heating, instabilities', 'J23' : 'Transports, confinements', 'J24' : 'Nonlinear phenomena',
                'J25' : 'High energy, high density plasma, strongly coupled systems', 'J26' : 'Electrostatic discharges, ionization, emergence of plasma', 'J27' : 'Magnetic reconnections, particle accelerations, dynamo',
                'J28' : 'Non-neutral plasma, dust plasma', 'J29' : 'Other topics in plasma physics', 'J3' : 'Chemical physics',
                'J30' : 'Chemical reactions', 'J31' : 'Optical response, optical scatterings', 'J32' : 'Solutions and liquids',
                'J33' : 'Quantum chemistry, electronic states', 'J34' : 'Photosynthesis, optical response in biology', 'J35' : 'Supercooled liquids and glasses',
                'J36' : 'Other topics in chemical physics', 'J4' : 'Soft-matter physics', 'J40' : 'Liquid crystals',
                'J41' : 'Polymer physics', 'J42' : 'Gels', 'J43' : 'Glassy systems',
                'J44' : 'Granular physics', 'J45' : 'Other topics in soft-matter physics', 'J5' : 'Biophysics',
                'J50' : 'Proteins, nucleic acids, biomembranes, bio-supramolecules', 'J51' : 'Transmission of information and energy in living bodies', 'J52' : 'Neurons and brains',
                'J53' : 'Biomechanics, physics of biomolecules', 'J54' : 'Immunology', 'J55' : 'Embryology and bio-evolutions',
                'J56' : 'Other topics in biophysics', 'J6' : 'Geophysics', 'J60' : 'Earthquakes',
                'J61' : 'Geofluid mechanics, sand motion', 'J62' : 'Geophysical aspects of planet science', 'J63' : 'Other topics in geophysics',
                'J7' : 'Others', 'J70' : 'Traffic flows and pedestrian dynamics', 'J71' : 'Econophysics, social physics',
                'J72' : 'Physics of games and sports', 'J73' : 'Environmental physics', 'J74' : 'Other topics'}




hdr = {'User-Agent' : 'Magic Browser'}
req = urllib.request.Request('https://academic.oup.com/', headers=hdr)

typecode = 'P'

               
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
    artlink = 'https://doi.org/' + doi
    try:
        time.sleep(37)
        req = urllib.request.Request(artlink, headers=hdr)
        page = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        print("retry in 280 seconds")
        time.sleep(280)
        req = urllib.request.Request(artlink, headers=hdr)
        page = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    rec = {'note' : [], 'tc' : typecode,
           'refs' : [], 'autaff' : [], 'keyw' : []}
    if re.search('^10\.\d+\/[a-z][a-z][a-z]+', doi):
        jnl = re.sub('^10\.\d+\/([a-z]+).*', r'\1', doi)
        if   (jnl == 'rpd'): 
            rec['jnl'] = 'Radiat.Prot.Dosim.'
        elif (jnl == 'ptep'):
            rec['jnl'] = 'PTEP'
        elif (jnl == 'mnras'): 
            rec['jnl'] = 'Mon.Not.Roy.Astron.Soc.'
        elif (jnl == 'mnrasl'): 
            rec['jnl'] = 'Mon.Not.Roy.Astron.Soc.'
        elif (jnl == 'pasj'): 
            rec['jnl'] = "Publ.Astron.Soc.Jap."
        elif (jnl == 'qjmath'): 
            rec['jnl'] = "Quart.J.Math.Oxford Ser."
        elif (jnl == 'bjps'): 
            rec['jnl'] = "Brit.J.Phil.Sci."
        elif (jnl == 'imrn'): 
            rec['jnl'] = "Int.Math.Res.Not."
        elif (jnl == 'nsr'):
            rec['jnl'] = "Natl.Sci.Rev."
        elif (jnl == 'astrogeo'):
            rec['jnl'] = 'Astron.Geophys.'
        elif (jnl == 'integrablesystems'):
            rec['jnl'] = 'J.Integrab.Syst.'
        elif (jnl == 'mam'):
            rec['jnl'] = 'Microscopy Microanal.'
        elif (jnl == 'ptp'):
            rec['jnl'] = 'Prog.Theor.Phys.'
        elif jnl == 'comjnl':
            rec['jnl'] = 'Comput.J.'
        elif jnl == 'biomet':
            rec['jnl'] = 'Biometrika'
        elif jnl == 'imamat':
            rec['jnl'] = 'Ima J.Appl.Math.'
    if not 'jnl' in rec:
        for meta in page.find_all('meta', attrs = {'name' : 'citation_journal_title'}):
            if meta['content'] in ['Geophysical Journal International']:
                rec['jnl'] = 'Geophys.J.Int.'
                jnl = 'gji'
            elif meta['content'] in ['Progress of Theoretical Physics Supplement']:
                rec['jnl'] = 'Prog.Theor.Phys.Suppl.'
                rec['tc'] = 'C'
                jnl = 'ptps'
            elif meta['content'] in ['Progress of Theoretical Physics']:
                rec['jnl'] = 'Prog.Theor.Phys.'
                jnl = 'ptp'
#            elif meta['content'] in ['']:
#                rec['jnl'] = ''
#            elif meta['content'] in ['']:
#                rec['jnl'] = ''
            else:
                missingjournals.append(meta['content'])
    if not 'jnl' in rec:
        continue

        
    #not completely loaded?
    for meta in page.find_all('meta', attrs = {'name' : 'citation_doi'}):
        rec['doi'] = meta['content']
    if 'doi' in list(rec.keys()):
        print('   ', rec['doi'])
    else:
        print("retry in 180 seconds")
        time.sleep(180)
        pagreq = urllib.request.Request(artlink, headers={'User-Agent' : "Magic Browser"})
        page = BeautifulSoup(urllib.request.urlopen(pagreq), features="lxml")                               
    ejlmod3.metatagcheck(rec, page, ['citation_firstpage', 'citation_lastpage', 'citation_doi',
                                     'citation_title', 'citation_publication_date', 'citation_author',
                                     'citation_author_institution', 'citation_volume',
                                     'citation_issue'])
    for meta in page.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
        rec['pdf_url'] = meta['content']
        if jnl == 'ptep':
            rec['p1'] = re.sub('.*\/20\d\d\/\d+\/(.*?)\/.*', r'\1', rec['pdf_url'])
    for abstract in page.find_all('section', attrs = {'class' : 'abstract'}):
        try:
            fsunwrap(abstract)
            rec['abs'] = re.sub('\n *', ' ', abstract.p.text.strip())
        except:
            print(' -- no abstract --')
    for ref in page.find_all('div', attrs = {'class' : 'ref-content'}):
        refdois = []
        for a in ref.find_all('a'):
            atext = a.text                
            if re.search('Cross[rR]ef', atext) or re.search('https?...doi.org.', atext):
                refdoi = re.sub('http.*doi.org.', ', DOI: ', a['href']+' ')
                if not refdoi in refdois:
                    a.replace_with(refdoi)
                    refdois.append(refdoi)
                else:
                    a.replace_with('')
            elif re.search('Google Scholar', atext) or re.search('PubMed', atext) or re.search('Search ADS', atext):
                a.replace_with(' ')
        rec['refs'].append([('x', ref.text)])
    #PASJ p1
    if (jnl == 'pasj'): 
        for wwco in page.find_all('div', attrs = {'class' : 'ww-citation-primary'}):
            rec['p1'] = re.sub('.*: (.*?)\.?$', r'\1', wwco.text)
            if re.search('Publications of the Astronomi.*Page', rec['p1']):
                rec['p1'] = re.sub(',.*', '', re.sub('.*Pages? ', '', rec['p1']))
    elif (jnl == 'nsr'):
        rec['p1'] = re.sub('.*\/', '', rec['doi'])
    #licence
    ejlmod3.globallicensesearch(rec, page)
    #PASJ keywords
    for a in page.find_all('a', attrs = {'class' : 'kwd-part kwd-main'}):
        rec['keyw'].append(a.text)
    #PTEP keywords
    for am in page.find_all('div', attrs = {'class' : 'article-metadata'}):
        for a in am.find_all('a'):
            if a.has_attr('href') and re.search('PTEP', a['href']):
                rec['keyw'].append(a.text)
    #no hidden PDF!
    if not 'license' in rec and 'pdf_url' in rec:
        del rec['pdf_url']

    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')


