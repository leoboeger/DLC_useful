# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 14:46:56 2021

@author: LeoBoeger
"""

# skeleton builder myself

bp_file =  'C:/Users/labgrprattenborg/DeepLabCut/DLCprojects/bp_names_file.txt'

  
with open(bp_file) as txt:
    bp_initial_txt = txt.readlines()
    
bp_names = [x.strip() for x in bp_initial_txt]

skel_all = ''
for bp in bp_names:
    skel_bp = ''
    for bp_else in bp_names:
        if not bp_else == bp:
            skel_tmp = '- - '+bp+'\n  - '+bp_else
            skel_bp = skel_bp+'\n'+skel_tmp
    skel_all = skel_all+'\n\n'+skel_bp
    
