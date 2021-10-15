# -*- coding: utf-8 -*-
"""
Created on Wed Mar 10 09:44:03 2021

@author: LeoBoeger
"""
import os
import pandas as pd
import math

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as colors
import matplotlib.cm as cm

from helper_plots import break_finder_OnDurList

### settings
dir_in = 'C:/Users/labgrprattenborg/DeepLabCut/DLCprojects/test_videos/fMRIsleepBudapest-Leo-2021-02-23/iteration 1'
csv_file = 'fMRIcam_2020-12-11_10-19-00-418_red38DLC_resnet_50_fMRIsleepBudapestFeb23shuffle1_350000.csv'
csv_dir_in = os.path.join(dir_in, csv_file)
csv_path = os.path.dirname(csv_dir_in)
csv_name = os.path.basename(csv_dir_in).split('.')[0]
csv_in = pd.read_csv(csv_dir_in, header=[1,2])
below = 0.97

bp_names = list(csv_in.columns)

### create csv_low as csv output, containing columns only with low likelihood frames
### create csv_nan, containing columns with nan values instead of high likelihood frames
csv_low = pd.DataFrame()
csv_nan = pd.DataFrame()
for bp in bp_names:
    if "likelihood" in bp:
        index = csv_in[csv_in[bp]<below].index.tolist()
        df_idx = pd.DataFrame(index, columns=[bp])
        #df_nan = csv_in.loc[csv_in[bp] < below, bp] = 1
        csv_nan[bp] = csv_in[bp].apply(lambda x: bp[0] if x < below else np.nan)
        #df_nan = csv_in.loc[csv_in[bp] > below, bp] = 0
        csv_low = pd.concat([csv_low,df_idx], axis=1, sort=True)
        
### writing
csv_low.to_csv(os.path.join(csv_path,csv_name+'_low'+str(below).replace('.', '')+'.csv'))

# creating on-off low likelihood pairs for broken barh plotin matplotlib
csv_pairs = []
for bp in bp_names:
    if "likelihood" in bp:
        on = []
        off = []
        for i in range(len(csv_low[bp])):
            if csv_low[bp][i] != np.nan:
                if i == 0:
                    on.append(csv_low[bp][i])
                # at the end
                if i == len(csv_low[bp])-1:
                    off.append(csv_low[bp][i]-on[-1]+1)
                    break
                # premature ending
                if math.isnan(csv_low[bp][i+1]):
                    off.append(csv_low[bp][i]-on[-1]+1)
                    break
                if csv_low[bp][i]+1 < csv_low[bp][i+1]:
                    off.append(csv_low[bp][i]-on[-1]+1)
                    on.append(csv_low[bp][i+1])
        pairs = [(on[i],off[i]) for i in range(len(off))]
        csv_pairs.append(pairs)
        
### get rid of beginning and end part with high likelihood
first_idx = csv_nan.first_valid_index()
last_idx = csv_nan.last_valid_index()
print(first_idx, last_idx)
csv_nan = csv_nan.loc[first_idx:last_idx]



### defines frame range of interest, in which low likelihood frames are present
frame_rng = np.array(range(first_idx,last_idx+1))


### optimisation of csv_nan for plotting             
csv_nan = csv_nan.fillna('')
csv_nan_np =csv_nan.values.transpose()
    
"""
fig, ax = plt.subplots()
for col in csv_nan_np:
    ax.scatter(frame_rng,col)
plt.show()

"""

breaksat, RngOI = break_finder_OnDurList(csv_pairs,1000)
asmuch=len(RngOI)

pairs_w = []
for pair in RngOI:
    pair_w = pair[1]-pair[0]+4
    pairs_w.append(pair_w)
total_w = sum(pairs_w)



fig =  plt.figure(constrained_layout=True, figsize=(24,4))
spec5 = fig.add_gridspec(ncols = asmuch, width_ratios=pairs_w)
jet = cm.get_cmap('jet') 
cmap = []
for i in np.arange(0, 1, 1/16).tolist():
    cmap.append(jet(i))
labels = [x[0] for x in bp_names if 'likelihood'in x]


for region in range(len(RngOI)):
    count=1
    for on2offs in csv_pairs:
        ax = fig.add_subplot(spec5[region])
        ax.broken_barh(on2offs,(10*count,9),facecolors=cmap[count-1])
        count += 1

        ax.set_xlim(RngOI[region][0]-2, RngOI[region][1]+2)
        ax.ticklabel_format(useOffset=False)
        plt.xticks(rotation=270)
        
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.tick_params(labelleft=False)  # don't put tick labels at the top
        ax.grid(True)
plt.legend(labels, bbox_to_anchor=(1.0, 1.0), loc='upper left')
plt.save(os.path.join(csv_path,csv_name+'_low'+str(below).replace('.', '')+'.png'))
        

