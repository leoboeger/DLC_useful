# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 15:07:01 2021

@author: LeoBoeger
"""

# this script is designed to calculate the 95 percentile confidence interval,
# ie.the likelihood interval of the95% most likeli frames.

# load csv prediction
# parse through the likelihhod columns
# 1. give back interval for each bp
# 2. how to find interval for complete video?

import os
scriptpath = os.path.realpath(__file__)
os.chdir(scriptpath)

import pandas as pd
import scipy.stats as st
import numpy as np
from pylibLeo import plot_functions
import matplotlib.pyplot as plt

dirIn = 'C:/Users/labgrprattenborg/DeepLabCut/DLCprojects/test_videos/fMRIsleepBudapestResNet101Contrast-Leo-2021-04-20/iteration 0_1'
#csvFile = 'Blue69_S2_Video_2021-01-12_09-30-00-000DLC_resnet_101_fMRIsleepBudapestResNet101Apr14shuffle1_400000.csv'

folderFound = []
for f in os.listdir(dirIn):
    if f.__contains__("csv"):
        folder = os.path.join(f)
        folderFound.append(folder)


def load_csv(dir_in, csv_file):
    csv_dir_in = os.path.join(dir_in, csv_file)
    csv_in = pd.read_csv(csv_dir_in, header=[1,2])

    bp_names = list(csv_in.columns)
    
    ### create csv_low as csv output, containing columns only with low likelihood frames
    ### create csv_nan, containing columns with nan values instead of high likelihood frames
    all_likeli = pd.DataFrame()
    for bp in bp_names:
        if "likelihood" in bp and not 'breast' in bp:
            bp_likeli= csv_in[bp]
            all_likeli = pd.concat([all_likeli,bp_likeli], axis=1, sort=True)
            
    return all_likeli


def ConfiInterval(all_likeli, ID):
    perc_dict = {"bp":[], "95percentile_"+str(ID): [], "5percentile_"+str(ID): []}
    all_appended = []
    for col in all_likeli:
        #confi_bp = st.norm.interval(alpha=0.95, loc=np.mean(all_likeli[col]), scale = st.sem(all_likeli[col]))
        # question: statistically correct? larger sample size n >= 30, sampling distribuition normally distributed?
        upper_perc = np.percentile(all_likeli[col],97.5)
        lower_perc = np.percentile(all_likeli[col],2.5)
        perc_dict["bp"].append(col[0])
        perc_dict["95percentile_"+str(ID)].append(upper_perc)
        perc_dict["5percentile_"+str(ID)].append(lower_perc)
        all_appended += list(all_likeli[col])
    
    upper_all = np.percentile(all_appended, 95)
    lower_all = np.percentile(all_appended, 5)
    
    return perc_dict, upper_all, lower_all

##############################################################################
### iterate through analysed folder

confiMerge = pd.DataFrame(columns=['bp'])
for csvFile in folderFound:
    name = "_".join(csvFile.split("_")[0:2]) # this is the position of the ID at the moment
    likelihoodDf = load_csv(dirIn, csvFile)
    confiBp, upperTotal, lowerTotal = ConfiInterval(likelihoodDf, name)
    
    
    confiDf = pd.DataFrame.from_dict(confiBp)
    confiDf = confiDf.append({"bp":'total', "95percentile_"+str(name): upperTotal,
                              "5percentile_"+str(name): lowerTotal}, ignore_index=True)
    confiMerge = confiMerge.merge(confiDf, how='outer', on='bp')

upper = confiMerge[['bp']+[x for x in confiMerge.columns if "95" in x]].set_index("bp")
lower = confiMerge[[x for x in confiMerge.columns if not "95" in x]].set_index("bp")
    
##############################################################################

upNP = upper.values
lowNP = lower.values
ylabels = upper.index.tolist()
xlabels = ['_'.join([y for y in x.split('_') if not y.__contains__("percentile")]) for x in upper.columns.tolist()]
#xlabels = [ for y in x if not y.__contains__("percentile")) for x in upper.index.tolist()]

fig, ax=plt.subplots(figsize=(15,8))
im1 = ax.imshow(upNP)
im2 = plot_functions.triamatrix(lowNP, ax, rot=180)

#fig.colorbar(im1, ax=ax, )
fig.colorbar(im2, ax=ax, )

ax.set_xticks(np.arange(len(xlabels)))
ax.set_yticks(np.arange(len(ylabels)))
ax.set_xticklabels(xlabels)
ax.set_yticklabels(ylabels)


ax.set_xticks(np.arange(upNP.shape[1]+1)-.5, minor=True)
ax.set_yticks(np.arange(upNP.shape[0]+1)-.5, minor=True)
ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
ax.tick_params(which="minor", bottom=False, left=False)

plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
         rotation_mode="anchor")
plt.title("95 Percentile and 5 Percentile")

plt.show()
