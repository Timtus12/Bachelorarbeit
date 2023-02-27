from os import stat
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mpcol
import matplotlib.lines as mlines
from matplotlib.ticker import (MultipleLocator,AutoMinorLocator)
from scipy import stats
import numpy as np
from collections import defaultdict


def niceboxplot(data,ax,**kwargs):

    # Kwargs:
    # groups: [[g1],[g2]] -> groups boxes together
    # color: list -> colors for boxes
    # groupcolor: list -> color of groups
    # groupcolors: list -> color of boxes in group. repeats each group
    # sig_fontsize: str -> fontsize of significance indicators
    # sig_distance: int -> distnace of significance connectors (lines). larger numbers equate to smaller distance. default: 10
    # sig_labeloffset: int -> distance of indicator from line. default: 0.3
    # sig_lw: int -> lineweight of significance indicator
    # BHcorrection: bool -> enabels Bonferroni holm correction. default: True

    kwargs.setdefault("change_color",False)
    kwargs.setdefault("legend_fontsize",10)
    kwargs.setdefault("legend_markersize",5)
    kwargs.setdefault("paired",False)
    kwargs.setdefault("return_box_pos",False)
    kwargs.setdefault("grid_minor",3)
    kwargs.setdefault("sig_fontsize", 7)
    kwargs.setdefault("sig_distance",10)
    kwargs.setdefault("sig_labeloffset",0.3)
    kwargs.setdefault("BHcorrection",False)
    kwargs.setdefault("sig_lw",0.7)

    colors = [(i/360,0.8,0.9) for i in range(20,361,62)]
    statistics = {}
    if "columns" in kwargs:
        data = data[kwargs["columns"]]
    for column in data.columns:
        mean = np.nanmean(data[column])
        median = np.nanmedian(data[column])
        upperquant = np.nanquantile(data[column],0.75)
        lowerquant = np.nanquantile(data[column],0.25)
        statistics[f"{column}"] = {"mean":mean,"median":median,"75":upperquant,"25":lowerquant}
    
    ###############
    # Box Styling #
    ###############

    if "groups" not in kwargs:
        plot = ax.boxplot([vals.dropna() for col, vals in data.iteritems()],patch_artist=True,widths=[0.2 for i in data.columns])
        label_dic = {}
        dic_label = {}
        pos_list = []
        for i in range(len(data.columns)):
            label_dic[data.columns[i]] = i+1
            dic_label[i+1] = data.columns[i]
            pos_list.append(i)
        label_dic_prev = label_dic
    else:
        col_order = []
        if type(kwargs["groups"][0]) == list:
            for group in kwargs["groups"]:
                for el in group:
                    col_order.append(el)
        else:
            for el in kwargs["groups"]:
                col_order.append(el)
        data = data[col_order]
        n = 0
        index = 1
        pos_dic = {}
        label_dic = {}
        label_dic_prev = {}
        dic_label = {}
        if type(kwargs["groups"][0]) == list:
            for group in kwargs["groups"]:
                pos_dic[f"group{n}"] = []
                for el in group:
                    pos_dic[f"group{n}"].append(index)
                    index += 1
                n += 1
        else:
            pos_dic[f"group{n}"] = []
            for el in kwargs["groups"]:
                pos_dic[f"group{n}"].append(index)
                index += 1
        label_index = 0
        means = []
        for group in pos_dic:
            mean = np.array(pos_dic[group]).mean()
            means.append(mean)
            i = 0
            for el in pos_dic[group]:
                distance = mean-el
                pos_dic[group][i] = el + distance/3
                label_dic[data.columns[label_index]] = el + distance/3
                label_dic_prev[data.columns[label_index]] = el
                dic_label[el] = data.columns[label_index]
                i+=1
                label_index += 1
        pos_list = []
        for group in pos_dic:
            pos_list = pos_list+pos_dic[group]
        plot = ax.boxplot([vals.dropna() for col, vals in data.iteritems()],patch_artist=True,positions=pos_list,widths=[0.2 for i in data.columns])
    
    for median in plot["medians"]:
        median.set_color("black")
    for flier in plot["fliers"]:
        flier.set_markersize(2)
        flier.set_markerfacecolor("black")
        #flier.set_markeredgecolor(color)
    for whisker in plot["whiskers"]:
        whisker.set_linewidth(0.7)
    
    if "groups" not in kwargs:
        if "color" not in kwargs:
            for box,color in zip(plot["boxes"],colors):
                box.set_alpha(0.6)
                box.set_facecolor(mpcol.hsv_to_rgb(color))
                box.set_edgecolor("black")
                box.set_linewidth(0.7)
        else:
            for box,color in zip(plot["boxes"],kwargs["color"]):
                box.set_alpha(0.6)
                box.set_facecolor(mpcol.hsv_to_rgb(color))
                box.set_edgecolor("black")
                box.set_linewidth(0.7)
    else:
        if "color" not in kwargs and "groupcolors" not in kwargs and "groupcolor" not in kwargs: 
            box_index = 0
            group_index = 0
            for group in kwargs["groups"]:
                el_index = 0
                for i in group:
                    if el_index == 0 or kwargs["change_color"] == False:
                        color = mpcol.hsv_to_rgb(colors[group_index]).tolist()
                        color.append(0.7)
                        plot["boxes"][box_index].set_facecolor(color)
                        plot["boxes"][box_index].set_linewidth(0.7)
                    else:
                        color = (colors[group_index][0]+(el_index*8/360),colors[group_index][1]-(el_index/4),colors[group_index][2]-(el_index/4))
                        color = mpcol.hsv_to_rgb(color).tolist()
                        color.append(0.7)
                        plot["boxes"][box_index].set_facecolor(color)
                        plot["boxes"][box_index].set_linewidth(0.7)
                    el_index += 1
                    box_index += 1
                group_index += 1
        elif "color" in kwargs:
            for box,color in zip(plot["boxes"],kwargs["color"]):
                box.set_alpha(0.6)
                box.set_facecolor(mpcol.hsv_to_rgb(color))
                box.set_edgecolor("black")
                box.set_linewidth(0.7)
        elif "groupcolor" in kwargs:
            box_index = 0
            for group,groupcolor in zip(kwargs["groups"],kwargs["groupcolor"]):
                el_index = 0
                for i in group:
                    if el_index == 0 or kwargs["change_color"] == False:
                        color = mpcol.hsv_to_rgb(groupcolor).tolist()
                        color.append(0.7)
                        plot["boxes"][box_index].set_facecolor(color)
                        plot["boxes"][box_index].set_linewidth(0.7)
                    else:
                        color = (groupcolor[0]+(el_index*8/360),groupcolor[1]-(el_index/5),groupcolor[2]-(el_index/5))
                        color = mpcol.hsv_to_rgb(color).tolist()
                        color.append(0.7)
                        plot["boxes"][box_index].set_facecolor(color)
                        plot["boxes"][box_index].set_linewidth(0.7)
                    el_index += 1
                    box_index += 1
        else:
            group_index = 0
            box_index = 0
            for group in zip(kwargs["groups"]):
               # print(group)
                for i,col in zip(group[0],kwargs["groupcolors"]):
                    #print(i,col)
                    el_index = 0
                    if group_index == 0 or kwargs["change_color"] == False:
                        plot["boxes"][box_index].set_facecolor(mpcol.hsv_to_rgb(col))
                        plot["boxes"][box_index].set_linewidth(0.7)
                    else:
                        color = (col[0]+(group_index*8/360),col[1]-(group_index/5),col[2]-(group_index/5))
                        #print(color)
                        color = mpcol.hsv_to_rgb(color).tolist()
                        color.append(0.7)
                        plot["boxes"][box_index].set_facecolor(color)
                        plot["boxes"][box_index].set_linewidth(0.7)
                    el_index += 1
                    box_index += 1
                group_index += 1

    data_min = np.nanmin(data.to_numpy()); data_max = np.nanmax(data.to_numpy())
    
    
    ##############
    # Statistics #
    ##############
   
    if "compare" in kwargs:
        onesample = False
        onesample_means = []
        if type(kwargs["compare"][0]) == list:
            results = {}
            for comparison in kwargs["compare"]:
                results["-".join(comparison)] = {"shapiro":{}}
                shapiro_p = []
                for column in comparison:
                    try:
                        onesample_expectedmean = float(column)
                        onesample_means.append(onesample_expectedmean)
                        onesample = True
                        columnIsInt = True
                    except:
                        columnIsInt = False
                    if not columnIsInt:
                        shapiro = stats.shapiro(data[column].dropna())
                        results["-".join(comparison)]["shapiro"][f"{column}"] = shapiro
                        shapiro_p.append(shapiro[1])

                if all(p > 0.05 for p in shapiro_p) and not onesample:
                    levene = stats.levene(data[comparison[0]].dropna(),data[comparison[1]].dropna())
                    results["-".join(comparison)]["levene"] = levene
                    if levene[1] < 0.05:
                        if kwargs["paired"]:
                            t = stats.ttest_rel(data[comparison[0]],data[comparison[1]],nan_policy="omit")
                        else:
                            t = stats.ttest_ind(data[comparison[0]],data[comparison[1]],nan_policy="omit")
                        results["-".join(comparison)]["t"] = t
                    else:
                        if kwargs["paired"]:
                            wilcoxon = stats.wilcoxon(data[comparison[0]].dropna(),data[comparison[1]].dropna())
                            results["-".join(comparison)]["wilcoxon"] = wilcoxon
                        else:
                            mwu = stats.mannwhitneyu(data[comparison[0]].dropna(),data[comparison[1]].dropna())
                            results["-".join(comparison)]["mwu"] = mwu
                
                elif all(p > 0.05 for p in shapiro_p) and onesample:
                    if comparison.index(str(onesample_expectedmean)) == 0:
                        t = stats.ttest_1samp(data[comparison[1]].dropna(),popmean=onesample_expectedmean)
                        results["-".join(comparison)]["t"] = t
                    else:
                        t = stats.ttest_1samp(data[comparison[0]].dropna(),popmean=onesample_expectedmean)
                        results["-".join(comparison)]["t"] = t
                
                elif all(p < 0.05 for p in shapiro_p) and onesample:
                    if comparison.index(str(onesample_expectedmean)) == 0:
                        wilcoxon = stats.wilcoxon(data[comparison[1]].dropna(),[onesample_expectedmean for i in range(data[comparison[1]].dropna().shape[0])])
                        results["-".join(comparison)]["wilcoxon"] = wilcoxon
                    else:
                        wilcoxon = stats.wilcoxon(data[comparison[0]].dropna(),[onesample_expectedmean for i in range(data[comparison[0]].dropna().shape[0])])
                        results["-".join(comparison)]["wilcoxon"] = wilcoxon

                else:
                    if kwargs["paired"]:
                        wilcoxon = stats.wilcoxon(data[comparison[0]].dropna(),data[comparison[1]].dropna())
                        results["-".join(comparison)]["wilcoxon"] = wilcoxon
                    else:
                        mwu = stats.mannwhitneyu(data[comparison[0]].dropna(),data[comparison[1]].dropna())
                        results["-".join(comparison)]["mwu"] = mwu
            # Bonferoni-Holm korrektur
            if kwargs["BHcorrection"]:
                n_comparisons = {}
                needs_correction = []
                for comp in kwargs["compare"]:
                    for compared in comp:
                        if compared in n_comparisons.keys():
                            n_comparisons[compared] += 1
                        else:
                            n_comparisons[compared] = 1
                for compared in n_comparisons:
                    if n_comparisons[compared] > 1:
                        for comp in results:
                            if compared in comp.split("-"):
                                if "mwu" in results[comp]:
                                    p = results[comp]["mwu"][1]
                                elif "wilcoxon" in results[comp]:
                                    p = results[comp]["wilcoxon"][1]
                                elif "t" in results[comp]:
                                    p = results[comp]["t"][1]
                                if len(needs_correction) > 0:
                                    for i,el in enumerate(needs_correction):
                                        if any(compared in e.split("-") for e in el):
                                            append_new = False
                                            break
                                        else:
                                            append_new = True
                                    if append_new:
                                        needs_correction.append({comp:p})
                                    else:
                                        needs_correction[i][comp] = p
                                else:
                                    needs_correction.append({comp:p})
                corrected_p = {}
                for group in needs_correction:
                    n_comparisons = len(list(group.keys()))
                    sorted_p = np.sort([p for p in group.values()])
                    sorted_p_dic = {}
                    for p in sorted_p:
                        for comp in group:
                            if p == group[comp]:
                                sorted_p_dic[p] = comp
                    for p in sorted_p_dic:
                        corrected_p[sorted_p_dic[p]] = p*n_comparisons
                        n_comparisons -= 1
                for comp in corrected_p:
                    results[comp]["Adjusted P"] = corrected_p[comp]

            
        else:
            results = {"shapiro":{},"shapiro_p":[]}
            for column in kwargs["compare"]:
                shapiro = stats.shapiro(data[column].dropna())
                results["shapiro"][f"{column}"] = shapiro
                results["shapiro_p"].append(shapiro[1])
            if results["shapiro_p"][0] > 0.05 and results["shapiro_p"][1] > 0.05:
                levene = stats.levene(data[kwargs["compare"][0]].dropna(),data[kwargs["compare"][1]].dropna())
                results["levene"] = levene
                if levene[1] < 0.05:
                    if kwargs["paired"]:
                        t = stats.ttest_rel(data[kwargs["compare"][0]],data[kwargs["compare"][1]],nan_policy="omit")
                    else:
                        t = stats.ttest_ind(data[kwargs["compare"][0]],data[kwargs["compare"][1]],nan_policy="omit")
                    results["t"] = t
                else:
                    if kwargs["paired"]:
                        wilcoxon = stats.wilcoxon(data[kwargs["compare"][0]].dropna(),data[kwargs["compare"][1]].dropna())
                        results["wilcoxon"] = wilcoxon
                    else:
                        mwu = stats.mannwhitneyu(data[kwargs["compare"][0]].dropna(),data[kwargs["compare"][1]].dropna())
                        results["mwu"] = mwu
                        
            else:
                if kwargs["paired"]:
                    wilcoxon = stats.wilcoxon(data[kwargs["compare"][0]].dropna(),data[kwargs["compare"][1]].dropna())
                    results["wilcoxon"] = wilcoxon
                else:
                    mwu = stats.wilcoxon(data[kwargs["compare"][0]].dropna(),data[kwargs["compare"][1]].dropna())
                    results["mwu"] = mwu
                    
        #########################
        # Plotting of Statistic #
        #########################
        higher = 1
        if type(kwargs["compare"][0]) == list:
            comp_boxes = []
            compared_groups = []
            for comparison in kwargs["compare"]:
                oneInCompGroup = False
                if not onesample:   # Plot for 2 Sample tests
                    if "groups" in kwargs:
                        for group in kwargs["groups"]:
                            if comparison[0] in group or comparison[1] in group:
                                if group in compared_groups:
                                    oneInCompGroup = True
                                if group not in compared_groups and higher != 2:
                                    if not oneInCompGroup:
                                        higher = 1
                                    compared_groups.append(group)
                                elif group not in compared_groups:
                                    compared_groups.append(group)
                    points_x = (label_dic[comparison[0]],label_dic[comparison[0]],label_dic[comparison[1]],label_dic[comparison[1]])
                    points_y = (
                        data_max+ (((data_max-data_min)/kwargs["sig_distance"])*higher) - (data_max-data_min)/50,
                        data_max+ (((data_max-data_min)/kwargs["sig_distance"])*higher),
                        data_max+ (((data_max-data_min)/kwargs["sig_distance"])*higher),
                        data_max+ (((data_max-data_min)/kwargs["sig_distance"])*higher) - (data_max-data_min)/50
                    )
                    text_x = (label_dic[comparison[0]],label_dic[comparison[1]]) 
                    text_y1 = data_max+(((data_max-data_min)/kwargs["sig_distance"])*(higher+kwargs["sig_labeloffset"]))
                    text_y2 = data_max+(((data_max-data_min)/kwargs["sig_distance"])*(higher+kwargs["sig_labeloffset"]-kwargs["sig_labeloffset"]/2.5))
                    for i in range(label_dic_prev[comparison[0]],label_dic_prev[comparison[1]]+1):
                        comp_boxes.append(dic_label[i])
                    if (comparison[0] in comp_boxes) or (comparison[1] in comp_boxes):
                        higher += 1
                    ax.plot(points_x,points_y, c="black",lw=kwargs["sig_lw"])
                    """if "t" in list(results["-".join(comparison)].keys()):
                        if results["-".join(comparison)]["t"][1] < 0.001:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"***",horizontalalignment="center")
                        elif results["-".join(comparison)]["t"][1] < 0.01:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"**",horizontalalignment="center")
                        elif results["-".join(comparison)]["t"][1] < 0.05:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y1,"*",rotation=90,horizontalalignment="center")
                        else:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"n.s.",fontsize=7,horizontalalignment="center") """
                    #if "t" in list(results["-".join(comparison)].keys()) or "mwu" in list(results["-".join(comparison)].keys()) or "wilcoxon" in list(results["-".join(comparison)].keys()):
                    if "Adjusted P" in list(results["-".join(comparison)].keys()):
                        teststring = "Adjusted P"
                        if results["-".join(comparison)][teststring] < 0.001:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"***",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                        elif results["-".join(comparison)][teststring] < 0.01:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"**",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                        elif results["-".join(comparison)][teststring] < 0.05:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y1,"*",rotation=90,horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                        else:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"n.s.",horizontalalignment="center",fontsize=kwargs["sig_fontsize"]) 
                    else:
                        if "t" in list(results["-".join(comparison)].keys()):
                            teststring = "t"
                        elif "mwu" in list(results["-".join(comparison)].keys()):
                            teststring = "mwu"
                        else:
                            teststring = "wilcoxon"
                        if results["-".join(comparison)][teststring][1] < 0.001:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"***",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                        elif results["-".join(comparison)][teststring][1] < 0.01:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"**",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                        elif results["-".join(comparison)][teststring][1] < 0.05:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y1,"*",rotation=90,horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                        else:
                            ax.text(text_x[0]+(text_x[1]-text_x[0])/2,text_y2,"n.s.",horizontalalignment="center",fontsize=kwargs["sig_fontsize"]) 
                
                else: # Plot for onesample test
                    if all(mean == onesample_means[0] for mean in onesample_means):
                        # onesample_means is list of expected means 
                        ax.plot([ax.get_xlim()[0],ax.get_xlim()[1]],[onesample_means[0],onesample_means[0]],c="black",lw=0.5,ls="--")
                        for col in comparison:
                            if col != str(onesample_means[0]):
                                comparison_string = f"{col}-{onesample_means[0]}"
                                if data[col].median() < onesample_means[0]:
                                    y_val_littlemore = data[col].min() - abs(ax.get_ylim()[1]/20)
                                    y_val_more = data[col].min() - abs(ax.get_ylim()[1]/15)
                                    y_text = data[col].min() - abs(ax.get_ylim()[1]/10) - kwargs["sig_labeloffset"]
                                    y_text2 = y_text
                                else:
                                    y_val_littlemore = data[col].max() + abs(ax.get_ylim()[1]/20)
                                    y_val_more = data[col].max() + abs(ax.get_ylim()[1]/15)
                                    y_text = y_val_more + kwargs["sig_labeloffset"]
                                    y_text2 = data[col].max() + abs(ax.get_ylim()[1]/12) + kwargs["sig_labeloffset"]
                                ax.plot(
                                    [label_dic[col],label_dic[col],label_dic[col]+0.2,label_dic[col]+0.2],
                                    [y_val_littlemore,y_val_more,y_val_more,onesample_means[0]],
                                    c="black",lw=kwargs["sig_lw"]
                                )
                                if "t" in list(results[comparison_string].keys()) or "mwu" in list(results[comparison_string].keys()) or "wilcoxon" in list(results[comparison_string].keys()):
                                    if "t" in list(results[comparison_string].keys()):
                                        teststring = "t"
                                    elif "mwu" in list(results[comparison_string].keys()):
                                        teststring = "mwu"
                                    else:
                                        teststring = "wilcoxon"
                                    if results[comparison_string][teststring][1] < 0.001:
                                        ax.text(label_dic[col]+0.1,y_text,"***",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                                    elif results[comparison_string][teststring][1] < 0.051:
                                        ax.text(label_dic[col]+0.1,y_text,"**",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                                    elif results[comparison_string][teststring][1] < 0.05:
                                        ax.text(label_dic[col]+0.1,y_text,"*",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                                    else:
                                        ax.text(label_dic[col]+0.1,y_text2,"n.s.",horizontalalignment="center",verticalalignment="center",fontsize=kwargs["sig_fontsize"])
                                    
        
        else:
            points_x = (label_dic[kwargs["compare"][0]],label_dic[kwargs["compare"][1]])
            points_y = (data_max+(((data_max-data_min)/10)*1) ,data_max+(((data_max-data_min)/10)*1))  
            text_y = data_max+(((data_max-data_min)/10)*(higher+0.3)) 
            ax.plot(points_x,points_y, c="black",lw="0.7")
            if "t" in list(results.keys()):
                if results["t"][1] < 0.05:
                    ax.text(points_x[0]+(points_x[1]-points_x[0])/2.1,text_y,"*",rotation=90)
                else:
                    ax.text(points_x[0]+(points_x[1]-points_x[0])/2.4,text_y,"n.s.",fontsize=7) 
            if "mwu" in list(results.keys()) or "wilcoxon" in list(results.keys()):
                if "mwu" in list(results.keys()):
                    teststring = "mwu"
                else:
                    teststring = "wilcoxon"
                if results[teststring][1] < 0.05:
                    ax.text(points_x[0]+(points_x[1]-points_x[0])/2.1,text_y,"*",rotation=90)
                else:
                    ax.text(points_x[0]+(points_x[1]-points_x[0])/2.4,text_y,"n.s.",fontsize=7)

    ################
    # Plot Styling #
    ################
    
    ax.spines["right"].set_color("none"); ax.spines["top"].set_color("none")
    ax.spines["left"].set_position(("outward",15))
    ax.spines["bottom"].set_position(("outward",15))
    if "ylim" in kwargs:
        ax.set_ylim(*kwargs["ylim"])
    else:
        if "higher" in locals():
            ax.set_ylim(data_min-(((data_max-data_min)/10)*2),data_max+(((data_max-data_min)/10)*higher))
        else:
            ax.set_ylim(data_min-(((data_max-data_min)/10)*2),data_max+(((data_max-data_min)/10)*2))
    ax.spines["left"].set_bounds(ax.get_yticks()[0],ax.get_yticks()[-1])
    ax.set_yticks(ax.get_yticks())
    if "xticklabels" in kwargs and not "groupticklabels" in kwargs:
        ax.set_xticklabels(kwargs["xticklabels"])
    elif "xticklabels" in kwargs and not "groupticklabels" in kwargs:
        raise Exception("set either group labels or individual labels!")
    elif "groupticklabels" in kwargs:
        ax.set_xticks([np.array(pos_dic[group]).mean() for group in pos_dic])
        ax.set_xticklabels(kwargs["groupticklabels"])
    else:
        ax.set_xticklabels(list(data.columns))
    if "yticklabels" in kwargs:
        ax.set_yticklabels(kwargs["yticklabels"])
    if "xtickfontsize" in kwargs or "xtickrotation" in kwargs:
        for tick in ax.xaxis.get_major_ticks():
            if "xtickfontsize" in kwargs:
                tick.label.set_fontsize(kwargs["xtickfontsize"])
            if "xtickrotation" in kwargs:
                tick.label.set_rotation(kwargs["xtickrotation"])
    if "ytickfontsize" in kwargs or "ytickrotation" in kwargs:
        for tick in ax.yaxis.get_major_ticks():
            if "ytickfontsize" in kwargs:
                tick.label.set_fontsize(kwargs["ytickfontsize"])
            if "ytickrotation" in kwargs:
                tick.label.set_rotation(kwargs["ytickrotation"])
    ax.spines["bottom"].set_bounds(ax.get_xticks()[0],ax.get_xticks()[-1])
    if "title" in kwargs:
        if "title_y" in kwargs and "titlefontsize" in kwargs:
            ax.set_title(kwargs["title"],y=kwargs["title_y"],fontsize=kwargs["titlefontsize"])
        elif "title_y" in kwargs:
            ax.set_title(kwargs["title"],y=kwargs["title_y"])
        elif "titlefontsize" in kwargs:
            ax.set_title(kwargs["title"],y=1.1,fontsize=kwargs["titlefontsize"])
        else:
            ax.set_title(kwargs["title"],y=1.1)
    if "ylabel" in kwargs:
        if "ylabelfontsize" in kwargs:
            ax.set_ylabel(kwargs["ylabel"], fontsize=kwargs["ylabelfontsize"])
        else:
            ax.set_ylabel(kwargs["ylabel"])
    if "xlabel" in kwargs:
        if "xlabelfontsize" in kwargs:
            ax.set_xlabel(kwargs["xlabel"], fontsize=kwargs["xlabelfontsize"])
        else:
            ax.set_xlabel(kwargs["xlabel"])
    if "legend" in kwargs:
        handles = []
        for label in kwargs["legend"]:
            handler = mlines.Line2D([],[],color=mpcol.hsv_to_rgb(kwargs["legend"][label]),label=label,marker="o",lw=0,markersize=kwargs["legend_markersize"])
            handles.append(handler)
        ax.legend(handles=handles,loc="lower right",frameon=False, fontsize=kwargs["legend_fontsize"])
    if "grid" in kwargs:
        if "grid_minor" in kwargs:
            ax.yaxis.set_minor_locator(MultipleLocator(abs(ax.get_yticks()[1]-ax.get_yticks()[0])/kwargs["grid_minor"]))
        ax.grid(b=True,axis=kwargs["grid"],alpha=0.5,which="both" if "grid_minor" in kwargs else "major")
    
    
    if "compare" in kwargs:
        results_df = pd.DataFrame([])
        results_df_dic = {}
        if type(results[list(results.keys())[0]]) == dict:
            for key in results:
                key_dfs = []
                shapiro_keys = list(results[key]["shapiro"].keys())
                if len(shapiro_keys) == 2:
                    key_dfs.append(pd.DataFrame({"Shapiro Statistic":f'{results[key]["shapiro"][shapiro_keys[0]][0]} | {results[key]["shapiro"][shapiro_keys[1]][0]}',
                                                "Shapiro P":f'{results[key]["shapiro"][shapiro_keys[0]][1]} | {results[key]["shapiro"][shapiro_keys[1]][1]}'},index=[key]).T)
                else:
                    key_dfs.append(pd.DataFrame({"Shapiro Statistic":f'{results[key]["shapiro"][shapiro_keys[0]][0]}',
                                                "Shapiro P":f'{results[key]["shapiro"][shapiro_keys[0]][1]}'},index=[key]).T)
                if "levene" in results[key]:
                    key_dfs.append(pd.DataFrame({"Levene Statistic":results[key]["levene"][0],"Levene P":results[key]["levene"][1]},index=[key]).T)
                if "t" in results[key]:
                    key_dfs.append(pd.DataFrame({"T Statistic":results[key]["t"][0],"T P":results[key]["t"][1]},index=[key]).T)
                if "mwu" in results[key]:
                    key_dfs.append(pd.DataFrame({"MWU Statistic":results[key]["mwu"][0],"MWU P":results[key]["mwu"][1]},index=[key]).T)
                if "wilcoxon" in results[key]:
                    key_dfs.append(pd.DataFrame({"Wilcoxon Statistic":results[key]["wilcoxon"][0],"Wilcoxon P":results[key]["wilcoxon"][1]},index=[key]).T)
                if "Adjusted P" in results[key]:
                    key_dfs.append(pd.DataFrame({"Adjusted P":results[key]["Adjusted P"]},index=[key]).T)
                results_df_dic[key] = pd.DataFrame([])
                for df in key_dfs:
                    results_df_dic[key] = pd.concat([results_df_dic[key],df])
            for key in results_df_dic:
                results_df = pd.concat([results_df,results_df_dic[key]],axis=1)
            if not kwargs["return_box_pos"]:
                return pd.DataFrame(statistics), results_df.T
            else:
                return pd.DataFrame(statistics), results_df.T,pos_list
        else:
            if not kwargs["return_box_pos"]:
                return pd.DataFrame(statistics), results
            else:
                return pd.DataFrame(statistics), results,pos_list
    else:
        if not kwargs["return_box_pos"]:
            return pd.DataFrame(statistics)
        else:
            return pd.DataFrame(statistics),pos_list
    

if __name__ == "__main__":
    test = pd.DataFrame({"x":[np.random.randint(-2,20) for i in range(20)],
                       "y":[np.random.randint(10,60) for i in range(20)],
                       "z":[np.random.randint(-20,10) for i in range(20)],
                       "a":[np.random.randint(20,50) for i in range(20)],
                       "b":[np.random.randint(-10,10) for i in range(20)],
                       "c":[np.random.randint(-10,32) for i in range(20)]})
    test2 = pd.DataFrame({"x":np.random.normal(loc=0,size=1000),"y":np.random.normal(loc=10,size=1000)})
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #df = pd.DataFrame({"x":[3,4,6,7,8,4,3,5,8,3]})
    #stats, results = niceboxplot(test,ax,groups=(["x","a","z"],["y","b","c"]),compare=(["x","a"],["y","a"],["c","x"]),groupcolor=([0,0.8,0.8],[260/360,0.8,0.8]),change_color=True,legend={"green label":[0,0.8,0.8],"blue label":[260/360,0.8,0.8]})
    #stats,results = niceboxplot(test,ax,columns=["x","y"],compare=("x","y"),groups=("y","x"))
    #print(stats)
    stats, results = niceboxplot(test,ax,groups=(["x","y"],["z","a"],["b","c"]),compare=(["x","z"],["y","a"],["x","b"],["y","c"]),groupcolors=[(0,0.5,0.5),(0.7,0.5,0.5)],sig_distance=20)
    print(results)
    #stats, results = niceboxplot(test2,ax,groups=["x","y"],compare=[["x","0"],["y","0"]],grid="y",grid_minor=5,)
    #ax.boxplot(df)
    #print(results)
    plt.show()



    #
    # Example plot for BA
    #

    
    """
    BAplot = pd.DataFrame({
        "x":[np.random.randint(-2,20) for _ in range(20)],
        "y":[np.random.randint(0,40) for _ in range(20)],
        "z":[np.random.randint(-10,25) for _ in range(19)] + [-50]
    })
    fig = plt.figure(figsize=(8,5),dpi=100)
    ax1 = fig.add_axes([0.1,0.12,0.3,0.8])
    ax2 = fig.add_axes([0.65,0.12,0.3,0.8])
    niceboxplot(
        BAplot,ax1,groups=[["x","y"]],compare=[["x","y"]],grid="y",grid_minor=2,xticklabels=["group 1","group 2"],
        color=[(65/360,0.20,0.91),(174/360,0.20,0.93)],ytickfontsize="8",xtickfontsize="8",
        title="Two-sample test",titlefontsize=10,title_y=1
    )
    niceboxplot(
        BAplot,ax2,groups=[["z"]],compare=[["z","0"]],grid="y",grid_minor=2,xticklabels=["group 3"],
        color=[(284/360,0.20,0.93)],ytickfontsize="8",xtickfontsize="8",
        title="One-sample test",titlefontsize=10,title_y=1
    )
    #print(BAplot["x"].quantile(0.25))
    
    x25quant = BAplot["x"].quantile(0.25); x75quant = BAplot["x"].quantile(0.75); xmedian = BAplot["x"].median(); xIQR = x75quant - x25quant
    xlastpoint = BAplot["x"].min(); xfirstpoint = BAplot["x"].max()
    ax1.plot(
        [0.98,0.95,0.95,0.98],
        [x25quant,x25quant,x75quant,x75quant],
        lw=0.7,c="black"
    )
    ax1.text(0.93,(BAplot["x"].quantile(0.25)+BAplot["x"].quantile(0.75))/2,"IQR",horizontalalignment="right",verticalalignment="center",fontsize="9")
    ax1.plot(
        [1.35,1.38,1.38,1.35],
        [x25quant,x25quant,xmedian,xmedian],
        lw=0.7,c="black"
    )
    ax1.plot(
        [1.35,1.38,1.38,1.35],
        [xmedian,xmedian,x75quant,x75quant],
        lw=0.7,c="black"
    )
    ax1.text(1.4,(x25quant+xmedian)/2,"Q1",horizontalalignment="left",verticalalignment="center",fontsize="9")
    ax1.text(1.4,(xmedian+x75quant)/2,"Q3",horizontalalignment="left",verticalalignment="center",fontsize="9")

    
    y25quant = BAplot["y"].quantile(0.25); y75quant = BAplot["y"].quantile(0.75); ymedian = BAplot["y"].median(); yIQR = y75quant - y25quant
    ylastpoint = BAplot["y"].min(); yfirstpoint = BAplot["y"].max()
    ax1.plot(
        [1.98,2.01,2.01,1.98],
        [y25quant,y25quant,ylastpoint,ylastpoint],
        lw=0.7,c="black"
    )
    ax1.plot(
        [1.98,2.01,2.01,1.98],
        [y75quant,y75quant,yfirstpoint,yfirstpoint],
        lw=0.7,c="black"
    )
    ax1.text(2.03,(ylastpoint+y25quant)/2,"max Q1 - 1.5*IQR\nwhisker",horizontalalignment="left",verticalalignment="center",fontsize="9")
    ax1.text(2.03,(y75quant+yfirstpoint)/2,"max Q3 + 1.5*IQR\nwhisker",horizontalalignment="left",verticalalignment="center",fontsize="9")
    ax1.text(2.03,ymedian,"median",horizontalalignment="left",verticalalignment="center",fontsize="9")

    ax2.text(1.1,-50,"datapoint outside \nof Q1 - 1.5*IQR\nflier",horizontalalignment="left",verticalalignment="center",fontsize="9")
    ax2.text(1.25,10,"comparison \nagainst 0",horizontalalignment="left",verticalalignment="center",fontsize="9")
    plt.savefig("exampleBoxplot.svg",format="svg")
    plt.show()
    """