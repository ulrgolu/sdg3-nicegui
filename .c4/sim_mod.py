import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import json
import pickle
from files import luf

#  not_allowed = ["NSU","KKK","AFD","CDU","CSU","BSW","FDP","NPD","FDJ","XXX","FCK","FCU","FKU","FKK"]

def read_mdf_play_320_endyr(datei, runde):
  f = data_files[datei]
#  print('----- read_mdf_play_320_endyr loading: ' + datei + ' for runde '+str(runde))
  mdf_play = np.load(f)
  if runde == 1:
    mdf_play = mdf_play[320:1440, :]
  elif runde == 2:
    mdf_play = mdf_play[320:1920, :]
  elif runde == 3:
    mdf_play = mdf_play[320:2560, :]
  elif runde == 4:
    mdf_play = mdf_play[320:3840, :]
  return mdf_play

def read_mdfplay_full(datei, runde):
  f = data_files[datei]
  mdf_play_full = np.load(f)
  return mdf_play_full

def pick(ys, x, y):
  o = []
  ys_len = len(ys)
  ys_cnt = 0
  ys_check = ys[ys_cnt]
  for i in range(0, len(x)):
    if ys_check == x[i]:
      o.append(y[i])
      ys_cnt += 1
      if ys_cnt == ys_len:
        ys_check = 1952
      else:
        ys_check = ys[ys_cnt]
    else:
      o.append(np.nan)
  return o

def make_png(df, row, pyidx, end_yr, my_title):
  fig, ax = plt.subplots()
  pct = row["pct"]
  x = df[:, 0]
  y = df[:, 1] * pct
  data_max = y.max() * 1.1
  data_min = y.min()
  plot_max = row["ymax"]
  plot_min = row["ymin"]
  ymin = min(data_min, plot_min)
  ymax = max(data_max, plot_max)
  if ymin > 0:
    ymin = 0
  if ymax < 0:
    ymax = 0
  if int(row["id"]) in [27, 5]:  # Labour share of GDP | life expectancy
    ymin = plot_min  # red min
  if int(row["id"]) in [26]:  # population |
    ymax = data_max
  if int(row["id"]) in [32]:  # Nitrogen use
    ymax = max(25, data_max)
  if int(row["id"]) in [21]:  # pH  |
    ymin = plot_min
    ymax = plot_max
  abc_name = app_tables.regions.get(pyidx=pyidx)
  my_lab = abc_name["name"]
  # hex values for regional lines
  abc = ["#435df4","#b95c39","#ff0000","#ff37f6","#ff9300","#ad00ff","#00ff0c","#008a0f","#00ffbf","#00b2ff"]
  my_colhex = abc[pyidx]
  plt.plot(x, y, color=my_colhex, linewidth=2.5, label=my_lab)
  if end_yr == 2025:
    yr_picks = mg.yr_picks_start
  elif end_yr == 2040:
    yr_picks = mg.yr_picks_r1
  elif end_yr == 2060:
    yr_picks = mg.yr_picks_r2
  elif end_yr == 2100:
    yr_picks = mg.yr_picks_r3
  else:
    print("problem with yr_picks")
  ys = pick(yr_picks, x, y)
  plt.scatter(x, ys, color=my_colhex, s=200, alpha=0.65)
  if int(row["lowerbetter"]) == 1:
    grn_min = row["ymin"]  # 8
    grn_max = row["green"]  # vars_df.iloc[varx, 4]
    red_min = row["red"]  # vars_df.iloc[varx, 5]
    if int(row["id"]) == 16:  # Emissions per person
      red_max = max(data_max, 8)
      ymax = red_max
    else:
      red_max = row["ymax"]  # vars_df.iloc[varx, 9]
    if red_max < ymax:
      red_max = ymax
    yel_min = grn_max
    yel_max = red_min
  else:
    red_min = row["ymin"]  # vars_df.iloc[varx, 8]
    if int(row["id"]) == 10:  # Access to electricity
      if red_min > ymin:
        ymin = red_min
    red_max = row["red"]  # vars_df.iloc[varx, 5]
    grn_min = row["green"]  # vars_df.iloc[varx, 4]
    grn_max = row["ymax"]  # vars_df.iloc[varx, 9]
    yel_min = red_max
    yel_max = grn_min
  plt.ylim(ymin, ymax)
  xmin = 1990
  xmax = end_yr
  if not int(row["id"]) == 26:  # population
    opa = 0.075
    poly_coords = [(xmin, grn_max), (xmax, grn_max), (xmax, grn_min), (xmin, grn_min)]
    ax.add_patch(plt.Polygon(poly_coords, color="green", alpha=opa))
    poly_coords = [(xmin, red_max), (xmax, red_max), (xmax, red_min), (xmin, red_min)]
    ax.add_patch(plt.Polygon(poly_coords, color="red", alpha=opa))
    poly_coords = [(xmin, yel_max), (xmax, yel_max), (xmax, yel_min), (xmin, yel_min)]
    ax.add_patch(plt.Polygon(poly_coords, color="yellow", alpha=opa))
  plt.grid(color="gainsboro", linestyle="-", linewidth=0.5)
  plt.box(False)
  return anvil.mpl_util.plot_image()

def get_longrole_from_lu(x, lang):
  if x == "pov":
    return luf.ta_to_longmini_pov_str[lang]
  if x == "ineq":
    return luf.ta_to_longmini_ineq_str[lang]
  if x == "emp":
    return luf.ta_to_longmini_emp_str[lang]
  if x == "food":
    return luf.ta_to_longmini_food_str[lang]
  if x == "ener":
    return luf.ta_to_longmini_ener_str[lang]
  if x == "fut":
    return luf.ta_to_longmini_fut_str[lang]

def get_longreg_from_lu(x, lang):
  if x == "us":
    return luf.reg_to_longreg_us_str[lang]
  if x == "af":
    return luf.reg_to_longreg_af_str[lang]
  if x == "cn":
    return luf.reg_to_longreg_cn_str[lang]
  if x == "me":
    return luf.reg_to_longreg_me_str[lang]
  if x == "sa":
    return luf.reg_to_longreg_sa_str[lang]
  if x == "la":
    return luf.reg_to_longreg_la_str[lang]
  if x == "pa":
    return luf.reg_to_longreg_pa_str[lang]
  if x == "ec":
    return luf.reg_to_longreg_ec_str[lang]
  if x == "eu":
    return luf.reg_to_longreg_eu_str[lang]
  if x == "se":
    return luf.reg_to_longreg_se_str[lang]
  pass

def get_title_from_lu(x, lang):
  if x == 0:
#    return luf.sdgvarID_to_sdg_0_str[lang]
    return luf.nat_graph_9_title[lang]
  if x == 1:
    return luf.sdgvarID_to_sdg_1_str[lang]
  if x == 2:
    return luf.sdgvarID_to_sdg_2_str[lang]
  if x == 3:
    return luf.sdgvarID_to_sdg_3_str[lang]
  if x == 4:
    return luf.sdgvarID_to_sdg_4_str[lang]
  if x == 5:
    return luf.sdgvarID_to_sdg_5_str[lang]
  if x == 6:
    return luf.sdgvarID_to_sdg_6_str[lang]
  if x == 7:
    return luf.sdgvarID_to_sdg_7_str[lang]
  if x == 8:
    return luf.sdgvarID_to_sdg_8_str[lang]
  if x == 9:
    return luf.sdgvarID_to_sdg_9_str[lang]
  if x == 10:
    return luf.sdgvarID_to_sdg_10_str[lang]
  if x == 11:
    return luf.sdgvarID_to_sdg_11_str[lang]
  if x == 12:
    return luf.sdgvarID_to_sdg_12_str[lang]
  if x == 13:
    return luf.sdgvarID_to_sdg_13_str[lang]
  if x == 14:
    return luf.sdgvarID_to_sdg_14_str[lang]
  if x == 15:
    return luf.sdgvarID_to_sdg_15_str[lang]
  if x == 16:
#    return luf.sdgvarID_to_sdg_16_str[lang]
    return luf.sdgvarID_to_subtitle_16_str[lang]
  if x == 17:
    return luf.sdgvarID_to_sdg_17_str[lang]
  if x == 18:
    return luf.sdgvarID_to_sdg_18_str[lang]
  if x == 19:
    return luf.sdgvarID_to_sdg_19_str[lang]
  if x == 20:
    return luf.sdgvarID_to_sdg_20_str[lang]
  if x == 21:
    return luf.sdgvarID_to_sdg_21_str[lang]
  if x == 22:
    return luf.sdgvarID_to_sdg_22_str[lang]
  if x == 23:
    return luf.sdgvarID_to_sdg_23_str[lang]
  if x == 24:
    return luf.sdgvarID_to_sdg_24_str[lang]
  if x == 25:
    return luf.sdgvarID_to_sdg_25_str[lang]
  if x == 26:
    return luf.sdgvarID_to_sdg_26_str[lang]
  if x == 27:
    return luf.sdgvarID_to_sdg_27_str[lang]
  if x == 28:
    return luf.sdgvarID_to_sdg_28_str[lang]
  if x == 29:
    return luf.sdgvarID_to_sdg_29_str[lang]
  if x == 30:
    return luf.sdgvarID_to_sdg_30_str[lang]
  if x == 31:
    return luf.sdgvarID_to_sdg_31_str[lang]
  if x == 32:
    return luf.sdgvarID_to_sdg_32_str[lang]
  if x == 33:
    return luf.sdgvarID_to_sdg_33_str[lang]
  if x == 34:
    return luf.sdgvarID_to_sdg_34_str[lang]
  if x == 35:
    return luf.sdgvarID_to_sdg_35_str[lang]
  if x == 36:
    return luf.sdgvarID_to_sdg_36_str[lang]
  if x == 37:
    return luf.sdgvarID_to_sdg_37_str[lang]
  if x == 38:
    return luf.sdgvarID_to_sdg_38_str[lang]
  if x == 39:
#    return luf.sdgvarID_to_sdg_39_str[lang]
    return luf.nat_graph_7_title[lang]
  if x == 40:
    return luf.sdgvarID_to_sdg_40_str[lang]

def get_indicator_from_lu(x, lang):
  if x == 0:
#    return luf.sdgvarID_to_indicator_0_str[lang]
    return luf.sdgvarID_to_indicator_0_str[lang]
  if x == 1:
#    return luf.sdgvarID_to_indicator_1_str[lang]
    return luf.sdgvarID_to_subtitle_1_str[lang]
  if x == 2:
#    return luf.sdgvarID_to_indicator_2_str[lang]
    return luf.sdgvarID_to_subtitle_2_str[lang]
  if x == 3:
#    return luf.sdgvarID_to_indicator_3_str[lang]
    return luf.sdgvarID_to_subtitle_3_str[lang]
  if x == 4:
#    return luf.sdgvarID_to_indicator_4_str[lang]
    return luf.sdgvarID_to_subtitle_4_str[lang]
  if x == 5:
#    return luf.sdgvarID_to_indicator_5_str[lang]
    return luf.sdgvarID_to_subtitle_5_str[lang]
  if x == 6:
#    return luf.sdgvarID_to_indicator_6_str[lang]
    return luf.sdgvarID_to_subtitle_6_str[lang]
  if x == 7:
#    return luf.sdgvarID_to_indicator_7_str[lang]
    return luf.sdgvarID_to_subtitle_7_str[lang]
  if x == 8:
#    return luf.sdgvarID_to_indicator_8_str[lang]
    return luf.sdgvarID_to_subtitle_8_str[lang]
  if x == 9:
#    return luf.sdgvarID_to_indicator_9_str[lang]
    return luf.sdgvarID_to_subtitle_9_str[lang]
  if x == 10:
#    return luf.sdgvarID_to_indicator_10_str[lang]
    return luf.sdgvarID_to_subtitle_10_str[lang]
  if x == 11:
#    return luf.sdgvarID_to_indicator_11_str[lang]
    return luf.sdgvarID_to_subtitle_11_str[lang]
  if x == 12:
#    return luf.sdgvarID_to_indicator_12_str[lang]
    return luf.sdgvarID_to_subtitle_12_str[lang]
  if x == 13:
#    return luf.sdgvarID_to_indicator_13_str[lang]
    return luf.sdgvarID_to_subtitle_13_str[lang]
  if x == 14:
#    return luf.sdgvarID_to_indicator_14_str[lang]
    return luf.sdgvarID_to_subtitle_14_str[lang]
  if x == 15:
#    return luf.sdgvarID_to_indicator_15_str[lang]
    return luf.sdgvarID_to_subtitle_15_str[lang]
  if x == 16:
#    return luf.sdgvarID_to_indicator_16_str[lang]
    return luf.sdgvarID_to_subtitle_16_str[lang]
  if x == 17:
#    return luf.sdgvarID_to_indicator_17_str[lang]
    return luf.sdgvarID_to_subtitle_17_str[lang]
  if x == 18:
#    return luf.sdgvarID_to_indicator_18_str[lang]
    return luf.sdgvarID_to_subtitle_18_str[lang]
  if x == 19:
#    return luf.sdgvarID_to_indicator_19_str[lang]
    return luf.sdgvarID_to_subtitle_19_str[lang]
  if x == 20:
#    return luf.sdgvarID_to_indicator_20_str[lang]
    return luf.sdgvarID_to_subtitle_20_str[lang]
  if x == 21:
#    return luf.sdgvarID_to_indicator_21_str[lang]
    return luf.sdgvarID_to_subtitle_21_str[lang]
  if x == 22:
#    return luf.sdgvarID_to_indicator_22_str[lang]
    return luf.sdgvarID_to_subtitle_22_str[lang]
  if x == 23:
#    return luf.sdgvarID_to_indicator_23_str[lang]
    return luf.sdgvarID_to_subtitle_23_str[lang]
  if x == 24:
#    return luf.sdgvarID_to_indicator_24_str[lang]
    return luf.sdgvarID_to_subtitle_24_str[lang]
  if x == 25:
#    return luf.sdgvarID_to_indicator_25_str[lang]
    return luf.sdgvarID_to_subtitle_25_str[lang]
  if x == 26:
#    return luf.sdgvarID_to_indicator_26_str[lang]
    return luf.sdgvarID_to_subtitle_26_str[lang]
  if x == 27:
#    return luf.sdgvarID_to_indicator_27_str[lang]
    return luf.sdgvarID_to_subtitle_27_str[lang]
  if x == 28:
#    return luf.sdgvarID_to_indicator_28_str[lang]
    return luf.sdgvarID_to_subtitle_28_str[lang]
  if x == 29:
#    return luf.sdgvarID_to_indicator_29_str[lang]
    return luf.sdgvarID_to_subtitle_29_str[lang]
  if x == 30:
#    return luf.sdgvarID_to_indicator_30_str[lang]
    return luf.sdgvarID_to_subtitle_30_str[lang]
  if x == 31:
#    return luf.sdgvarID_to_indicator_31_str[lang]
    return luf.sdgvarID_to_subtitle_31_str[lang]
  if x == 32:
#    return luf.sdgvarID_to_indicator_32_str[lang]
    return luf.sdgvarID_to_subtitle_32_str[lang]
  if x == 33:
#    return luf.sdgvarID_to_indicator_33_str[lang]
    return luf.sdgvarID_to_subtitle_33_str[lang]
  if x == 34:
#    return luf.sdgvarID_to_indicator_34_str[lang]
    return luf.sdgvarID_to_subtitle_34_str[lang]
  if x == 35:
#    return luf.sdgvarID_to_indicator_35_str[lang]
    return luf.sdgvarID_to_subtitle_35_str[lang]
  if x == 36:
#    return luf.sdgvarID_to_indicator_36_str[lang]
    return luf.sdgvarID_to_subtitle_36_str[lang]
  if x == 37:
#    return luf.sdgvarID_to_indicator_37_str[lang]
    return luf.sdgvarID_to_subtitle_37_str[lang]
  if x == 38:
#    return luf.sdgvarID_to_indicator_38_str[lang]
    return luf.sdgvarID_to_subtitle_38_str[lang]
  if x == 39:
#    return luf.sdgvarID_to_indicator_39_str[lang]
    return luf.sdgvarID_to_subtitle_39_str[lang]
  if x == 40:
#    return luf.sdgvarID_to_indicator_40_str[lang]
    return luf.sdgvarID_to_indicator_40_str[lang]

def make_png_nat(df):
  fig, ax = plt.subplots()
  x = df[:, 0]
  y = df[:, 1]
  data_max = y.max() * 1.1
  data_min = y.min()
  plot_max = data_max
  plot_min = data_min
  ymin = min(data_min, plot_min)
  ymax = max(data_max, plot_max)
  if ymin > 0:
    ymin = 0
  if ymax < 0:
    ymax = 0
  plt.plot(x, y, color='darkred', linewidth=2.5)
  plt.ylim(ymin, ymax)
  plt.grid(color="gainsboro", linestyle="-", linewidth=0.5)
  plt.box(False)
  return anvil.mpl_util.plot_image()

def make_png_nat_over(runde, lang):
  mdf_play_nat = read_mdf_play_320_endyr("mdf_play_nat.npy", runde)
  print('make_png_nat_over shape on next lne ' + str(runde))
  print(mdf_play_nat.shape)
  df = mdf_play_nat[:, [0, 413, 411, 410, 409, 414, 415]] # this is global pop, soc, ineq, well, gdppp, temp
  x = df[:, 0]
  y1 = df[:, 1]
  y2 = df[:, 2]
  y3 = df[:, 3]
  y4 = df[:, 4]
  y5 = df[:, 5]
  y6 = df[:, 6]
  fig, ax1 = plt.subplots(figsize=(12, 8))
  fig.subplots_adjust(right=.7)
  fig.subplots_adjust(left=.07)
  ax1.plot(x, y1, 'red', label=luf.nat_graph_9_title[lang], linewidth=4.0) # 'Population'
  plt.box(False)
  #ax1.set_xlabel('Years')
  ax1.set_ylabel(luf.nat_graph_9_title[lang], color='red')
  ax1.tick_params('y', colors='red')
  ax2 = ax1.twinx()
  ax2.plot(x, y2, 'brown', label=luf.nat_graph_7_title[lang], linewidth=3.0) # 'Social tension'
  ax2.set_ylabel(luf.nat_graph_7_title[lang], color='brown')
  ax2.tick_params('y', colors='brown')
  ax3 = ax1.twinx()
  ax3.plot(x, y3, 'grey', label=luf.nat_graph_6_title[lang], linestyle='--', linewidth=5.0) #'Inequality'
  ax3.spines['right'].set_position(('outward', 50))
  ax3.set_ylabel(luf.nat_graph_6_title[lang], color='grey')
  ax3.tick_params('y', colors='grey')
  ax4 = ax1.twinx()
  ax4.plot(x, y4, 'green', label=luf.nat_graph_5_title[lang], linewidth=3.0) #'Wellbeing'
  ax4.spines['right'].set_position(('outward', 100))
  ax4.set_ylabel(luf.nat_graph_5_title[lang], color='green')
  ax4.tick_params('y', colors='green')
  ax5 = ax1.twinx()
  ax5.plot(x, y5, 'blue', label=luf.nat_graph_11_title[lang], linewidth=3.0) # 'GDPpp'
  ax5.spines['right'].set_position(('outward', 150))
  ax5.set_ylabel(luf.nat_graph_11_title[lang], color='blue')
  ax5.tick_params('y', colors='blue')
  ax6 = ax1.twinx()
  ax6.plot(x, y6, 'black', label=luf.nat_graph_4_title[lang], linewidth=3.0) # 'Warming'
  ax6.spines['right'].set_position(('outward', 200))
  ax6.set_ylabel(luf.nat_graph_4_title[lang], color='black')
  ax6.tick_params('y', colors='black')
  lines1, labels1 = ax1.get_legend_handles_labels()
  lines2, labels2 = ax2.get_legend_handles_labels()
  lines3, labels3 = ax3.get_legend_handles_labels()
  lines4, labels4 = ax4.get_legend_handles_labels()
  lines5, labels5 = ax5.get_legend_handles_labels()
  lines6, labels6 = ax6.get_legend_handles_labels()
  lines = lines1 + lines2 + lines3 + lines4 + lines5 + lines6
  labels = labels1 + labels2 + labels3 + labels4 + labels5 + labels6
  plt.legend(lines, labels, loc='lower right')
  plt.title(luf.nat_graph_10_title[lang]) # 'Global Overview'
#  plt.savefig('foo.pdf', bbox_inches='tight')
#  plt.show()
  return anvil.mpl_util.plot_image()  
  
# cap, runde, lang, 'gm', idx
def build_plot_nat(cap, runde, lang, reg, nat_idx):
  if nat_idx == 415:
    # do the global 
    my_title = luf.nat_graph_10_title[lang]
    cur_sub = luf.nat_graph_10_subtitle[lang]
    longreg = 'Global'
    cur_title = ("DRG: "+ my_title+ ", "+ longreg)
    cur_fig = make_png_nat_over(runde, lang)
    fdz = {"title": cur_title, "subtitle": cur_sub, "fig": cur_fig, "cap": cap}
    return fdz
  mdf_play = read_mdf_play_320_endyr("mdf_play_nat.npy", runde)
  print('build_plot_nat shape on next lne ' + str(runde))
  print(mdf_play.shape)
  dfv = mdf_play[:, [0, nat_idx]]
  if nat_idx == 405:
    my_title = luf.nat_graph_1_title[lang]
    cur_sub = luf.nat_graph_1_subtitle[lang]
  elif nat_idx == 406:
    my_title = luf.nat_graph_2_title[lang]
    cur_sub = luf.nat_graph_2_subtitle[lang]
  elif nat_idx == 407:
    my_title = luf.nat_graph_3_title[lang]
    cur_sub = luf.nat_graph_3_subtitle[lang]
  elif nat_idx == 408:
    my_title = luf.nat_graph_4_title[lang]
    cur_sub = luf.nat_graph_4_subtitle[lang]
  elif nat_idx == 409:
    my_title = luf.nat_graph_5_title[lang]
    cur_sub = luf.nat_graph_5_subtitle[lang]
  elif nat_idx == 410:
    my_title = luf.nat_graph_6_title[lang]
    cur_sub = luf.nat_graph_6_subtitle[lang]
  elif nat_idx == 411:
    my_title = luf.nat_graph_7_title[lang]
    cur_sub = luf.nat_graph_7_subtitle[lang]
  elif nat_idx == 412:
    my_title = luf.nat_graph_8_title[lang]
    cur_sub = luf.nat_graph_8_subtitle[lang]
  elif nat_idx == 413:
    my_title = luf.nat_graph_9_title[lang]
    cur_sub = luf.nat_graph_9_subtitle[lang]
  elif nat_idx == 414:
    my_title = luf.nat_graph_11_title[lang]
    cur_sub = luf.nat_graph_11_subtitle[lang]
  longreg = 'Global'
  cur_title = ("DRG: "+ my_title+ ", "+ longreg)
  cur_fig = make_png_nat(dfv)
  fdz = {"title": cur_title, "subtitle": cur_sub, "fig": cur_fig, "cap": cap}
  return fdz
  
def build_plot(var_row, regidx, cap, cid, runde, lang, reg, role):
  # find out for which round
  if runde == 1:
    yr = 2025
    ## load mdf play with Nathalie's globals
#    mdf_play = read_mdf_play_320_endyr("mdf_play.npy", runde)
    mdf_play = read_mdf_play_320_endyr("mdf_play_nat.npy", runde)
    print('build_plot cid='+cid+' runde='+str(runde)+' reg='+reg+' role='+role)
  elif runde == 2:
    yr = 2040
    s_row = app_tables.game_files.get(game_id=cid, yr=2040)
    s_row_elem = s_row["mdf_play"]
    mdf_bud = pickle.loads(s_row_elem.get_bytes())
    mdf_play = mdf_bud[320:1920, :]
    print(mdf_play.shape)
    print('build_plot cid='+cid+' runde='+str(runde)+' reg='+reg+' role='+role)
  elif runde == 3:
    yr = 2060
    s_row = app_tables.game_files.get(game_id=cid, yr=2060)
    s_row_elem = s_row["mdf_play"]
    mdf_bud = pickle.loads(s_row_elem.get_bytes())
    mdf_play = mdf_bud[320:2560, :]
    print(mdf_play.shape)
    print('build_plot cid='+cid+' runde='+str(runde)+' reg='+reg+' role='+role)
  elif runde == 4:
    yr = 2100
    s_row = app_tables.game_files.get(game_id=cid, yr=2100)
    s_row_elem = s_row["mdf_play"]
    mdf_bud = pickle.loads(s_row_elem.get_bytes())
    mdf_play = mdf_bud[320:3840, :]
    print(mdf_play.shape)
    print('build_plot cid='+cid+' runde='+str(runde)+' reg='+reg+' role='+role)
  var_l = var_row["vensim_name"]
  print('build plot var_l is: '+var_l+' shape is next')
  print(mdf_play.shape)
  var_l = var_l.replace(" ", "_")  # vensim uses underscores not whitespace in variable name
  varx = var_row["id"]
  #  print('starting new plot ...')
#  print('  --varx: '+str(varx))
  rowx = app_tables.mdf_play_vars.get(var_name=var_l)
  idx = rowx["col_idx"]
#  print('    --idx: '+str(idx))
  if varx in [19, 21, 22, 35]:  # global variable
    lx = idx  # find location of variable in mdf
  else:
    lx = idx + regidx  # find location of variable in mdf with reg offset
  dfv = mdf_play[:, [0, lx]]
  which_sdg = int(var_row["id"])
  longreg = get_longreg_from_lu(reg, lang)
  longrole = get_longrole_from_lu(role, lang)
  my_title = get_title_from_lu(which_sdg, lang)
  cur_title = ("DRG-"+ str(int(var_row["sdg_nbr"]))+ ": "+ my_title+ ", "+ longreg+ ", "+ longrole)
  cur_sub = get_indicator_from_lu(which_sdg, lang)
  cur_fig = make_png(dfv, var_row, regidx, yr, cur_sub)
  fdz = {"title": cur_title, "subtitle": cur_sub, "fig": cur_fig, "cap": cap}
  return fdz

def launch_create_plots_for_slots(game_id, reg, ta, runde, lang):
  task = anvil.server.launch_background_task("create_plots_for_slots", game_id, reg, ta, runde, lang)
  return task

def launch_create_plots_for_nat_slots(game_id, runde, lang):
  task = anvil.server.launch_background_task("create_plots_for_nat_slots", game_id, 'gm', runde, lang)
  return task

def get_all_vars_for_ta(ta):
  ta1 = mg.pov_to_Poverty[ta]
#  print('get_all_vars_for_ta +++++ '+ta1)
  v_row = app_tables.sdg_vars.search(ta=ta1)
  vars = [r["vensim_name"] for r in app_tables.sdg_vars.search(ta=ta1)]
  return vars, v_row

def create_plots_for_slots(game_id, region, single_ta, runde, lang):
  cid = game_id
  if runde == 1:
    yr = 2025
  elif runde == 2:
    yr = 2040
  elif runde == 3:
    yr = 2060
  elif runde == 4:
    yr = 2100
  else:
    print("In put_plots_for_slots: We dont know which runde")
  # generate a dictionary of
  regrow = app_tables.regions.get(abbr=region)
  regidx = int(regrow["pyidx"])
  my_time = datetime.datetime.now().strftime("%a %d %b %G")
#  print("off to build plot: regidx?"+ str(regidx)+ " cid:"+ cid+ " runde:"+ str(runde)+ " lang:"+ str(lang))
  foot1 = "mov250403 e4a 10reg.mdl"
  cap = foot1 + " - " + my_time
  vars_info_l, vars_info_rows = get_all_vars_for_ta(single_ta)
#  print(vars_info_rows)
  for var_row in vars_info_rows:
#    print(var_row['vensim_name'])
    fdz = build_plot(var_row, regidx, cap, cid, runde, lang, region, single_ta)
#    print(fdz)
    app_tables.plots.add_row(game_id=game_id,title=fdz["title"],subtitle=fdz["subtitle"],fig=fdz["fig"],cap=cap,runde=runde,ta=single_ta,reg=region)

def launch_do_gm_graphs(game_id, reg, runde, lang):
  task = anvil.server.launch_background_task("do_gm_graphs", game_id, reg, runde, lang)
  return task

def create_plots_for_nat_slots(game_id, region, runde, lang):
  cid = game_id
  if runde == 1:
    yr = 2025
  elif runde == 2:
    yr = 2040
  elif runde == 3:
    yr = 2060
  elif runde == 4:
    yr = 2100
  else:
    print("In put_plots_for_slots: We dont know which runde")
  # generate a dictionary of
  my_time = datetime.datetime.now().strftime("%a %d %b %G")
  #  print("off to do_gm_graphs: regidx?"+ str(regidx)+ " cid:"+ cid+ " runde:"+ str(runde)+ " lang:"+ str(lang))
  foot1 = "mov250403 e4a 10reg.mdl"
  cap = foot1 + " - " + my_time
  for idx in range(405,416):
    fdz = build_plot_nat(cap, runde, lang, 'gm', idx)
#    print(fdz)
    app_tables.plots.add_row(game_id=game_id,title=fdz["title"],subtitle=fdz["subtitle"],fig=fdz["fig"],cap=cap, runde=runde, ta='', reg=region)

def budget_to_db(yr, cid):
  regs = mg.regs
  if yr == 2025:
    app_tables.budget.delete_all_rows()
    ## load mdf play with Nathalie's globals
#    f = data_files["mdf_play.npy"]
    f = data_files["mdf_play_nat.npy"]
    mdf_bud = np.load(f)
    mdf_bud = mdf_bud[320:1440, :]
    rx = 1440 - 321
    runde = 1
    print("IN budget_to_db ... " + cid + " " + str(yr) + " " + str(runde) + " rx=" + str(rx))
  elif yr == 2040:
    runde = 2
    s_row = app_tables.game_files.get(game_id=cid, yr=2040)
    s_row_elem = s_row["mdf_play"]
    mdf_bud = pickle.loads(s_row_elem.get_bytes())
    mdf_bud = mdf_bud[320:1920, :]
    rx = 1920 - 321
    print("IN budget_to_db ... " + cid + " " + str(yr) + " " + str(runde) + " rx=" + str(rx))
  elif yr == 2060:
    runde = 3
    s_row = app_tables.game_files.get(game_id=cid, yr=2060)
    s_row_elem = s_row["mdf_play"]
    mdf_bud = pickle.loads(s_row_elem.get_bytes())
    mdf_bud = mdf_bud[320:2560, :]
    rx = 2560 - 321
    print("IN budget_to_db ... " + cid + " " + str(yr) + " " + str(runde) + " rx=" + str(rx))
  elif yr == 2100:
    runde = 4
    rx = 3840 - 321
    print(
      "IN budget_to_db ... " + cid + " " + str(yr) + " " + str(runde) + " rx=" + str(rx)
    )
  else:
    print("Forgot to add reading later mdfs")
  ba = []
  rowx = app_tables.mdf_play_vars.get(var_name="Budget_for_all_TA_per_region")
  idx = rowx["col_idx"]
  for i in range(0, 10):
    ba.append(mdf_bud[rx, idx + i])
  #  print('IN put_budget ... Budget_for_all_TA_per_region')
  #  print(ba)
  cpov = []
  rowx = app_tables.mdf_play_vars.get(var_name="Cost_per_regional_poverty_policy")
  idx = rowx["col_idx"]
  for i in range(10):
    cpov.append(mdf_bud[rx, idx + i])  # poverty
  #  print('IN put_budget ... cpov ')
  #  print(cpov)

  cineq = []
  rowx = app_tables.mdf_play_vars.get(var_name="Cost_per_regional_inequality_policy")
  idx = rowx["col_idx"]
  for i in range(10):
    cineq.append(mdf_bud[rx, idx + i])  # inequality
  #  print('IN put_budget ... cineq ')
  #  print(cineq)

  cemp = []
  rowx = app_tables.mdf_play_vars.get(var_name="Cost_per_regional_empowerment_policy")
  idx = rowx["col_idx"]
  for i in range(10):
    cemp.append(mdf_bud[rx, idx + i])  # empowerment
  #  print('IN put_budget ... cemp ')
  #  print(cemp)

  cfood = []
  rowx = app_tables.mdf_play_vars.get(var_name="Cost_per_regional_food_policy")
  idx = rowx["col_idx"]
  for i in range(10):
    cfood.append(mdf_bud[rx, idx + i])  # food
  #  print('IN put_budget ... cfood ')
  #  print(cfood)

  cener = []
  rowx = app_tables.mdf_play_vars.get(var_name="Cost_per_regional_energy_policy")
  idx = rowx["col_idx"]
  for i in range(10):
    cener.append(mdf_bud[rx, idx + i])  # energy
  #  print('IN put_budget ... cener ')
  #  print(cener)
  for i in range(0, 10):
    #    print("add row " + str(i) + ' ' + str(yr) + ' ' + str(runde) + ' ' + cid + ' ' + regs[i] + ' ' + str(ba[i]) + ' ' + str(cpov[i]) + ' ' + str(cineq[i]) + ' ' + str(cemp[i]) + ' ' + str(cener[i]))
    app_tables.budget.add_row(yr=yr,game_id=cid,reg=regs[i],runde=runde,bud_all_tas=ba[i],c_pov=cpov[i],c_ineq=cineq[i],c_emp=cemp[i],c_food=cfood[i],c_ener=cener[i])

def get_pol_expl_lang(pol, lang):
  if pol == "ExPS":
    return luf.pol_to_expl_ExPS_str[lang]
  if pol == "CCS":
    return luf.pol_to_expl_CCS_str[lang]
  if pol == "TOW":
    return luf.pol_to_expl_TOW_str[lang]
  if pol == "FPGDC":
    return luf.pol_to_expl_FPGDC_str[lang]
  if pol == "RMDR":
    return luf.pol_to_expl_RMDR_str[lang]
  if pol == "REFOREST":
    return luf.pol_to_expl_REFOREST_str[lang]
  if pol == "FTPEE":
    return luf.pol_to_expl_FTPEE_str[lang]
  if pol == "LPBsplit":
    return luf.pol_to_expl_LPBsplit_str[lang]
  if pol == "FMPLDD":
    return luf.pol_to_expl_FMPLDD_str[lang]
  if pol == "StrUP":
    return luf.pol_to_expl_StrUP_str[lang]
  if pol == "Wreaction":
    return luf.pol_to_expl_Wreaction_str[lang]
  if pol == "SGMP":
    return luf.pol_to_expl_SGMP_str[lang]
  if pol == "FWRP":
    return luf.pol_to_expl_FWRP_str[lang]
  if pol == "ICTR":
    return luf.pol_to_expl_ICTR_str[lang]
  if pol == "XtaxCom":
    return luf.pol_to_expl_XtaxCom_str[lang]
  if pol == "Lfrac":
    return luf.pol_to_expl_Lfrac_str[lang]
  if pol == "IOITR":
    return luf.pol_to_expl_IOITR_str[lang]
  if pol == "IWITR":
    return luf.pol_to_expl_IWITR_str[lang]
  if pol == "SGRPI":
    return luf.pol_to_expl_SGRPI_str[lang]
  if pol == "FEHC":
    return luf.pol_to_expl_FEHC_str[lang]
  if pol == "XtaxRateEmp":
    return luf.pol_to_expl_XtaxRateEmp_str[lang]
  if pol == "FLWR":
    return luf.pol_to_expl_FLWR_str[lang]
  if pol == "RIPLGF":
    return luf.pol_to_expl_RIPLGF_str[lang]
  if pol == "FC":
    return luf.pol_to_expl_FC_str[lang]
  if pol == "NEP":
    return luf.pol_to_expl_NEP_str[lang]
  if pol == "Ctax":
    return luf.pol_to_expl_Ctax_str[lang]
  if pol == "DAC":
    return luf.pol_to_expl_DAC_str[lang]
  if pol == "XtaxFrac":
    return luf.pol_to_expl_XtaxFrac_str[lang]
  if pol == "LPBgrant":
    return luf.pol_to_expl_LPBgrant_str[lang]
  if pol == "LPB":
    return luf.pol_to_expl_LPB_str[lang]
  if pol == "SSGDR":
    return luf.pol_to_expl_SSGDR_str[lang]
  if pol == "ISPV":
    return luf.pol_to_expl_ISPV_str[lang]

def get_pol_name_lang(pol, lang):
  if pol == "ExPS":
    return luf.pol_to_name_ExPS_str[lang]
  if pol == "CCS":
    return luf.pol_to_name_CCS_str[lang]
  if pol == "TOW":
    return luf.pol_to_name_TOW_str[lang]
  if pol == "FPGDC":
    return luf.pol_to_name_FPGDC_str[lang]
  if pol == "RMDR":
    return luf.pol_to_name_RMDR_str[lang]
  if pol == "REFOREST":
    return luf.pol_to_name_REFOREST_str[lang]
  if pol == "FTPEE":
    return luf.pol_to_name_FTPEE_str[lang]
  if pol == "LPBsplit":
    return luf.pol_to_name_LPBsplit_str[lang]
  if pol == "FMPLDD":
    return luf.pol_to_name_FMPLDD_str[lang]
  if pol == "StrUP":
    return luf.pol_to_name_StrUP_str[lang]
  if pol == "Wreaction":
    return luf.pol_to_name_Wreaction_str[lang]
  if pol == "SGMP":
    return luf.pol_to_name_SGMP_str[lang]
  if pol == "FWRP":
    return luf.pol_to_name_FWRP_str[lang]
  if pol == "ICTR":
    return luf.pol_to_name_ICTR_str[lang]
  if pol == "XtaxCom":
    return luf.pol_to_name_XtaxCom_str[lang]
  if pol == "Lfrac":
    return luf.pol_to_name_Lfrac_str[lang]
  if pol == "IOITR":
    return luf.pol_to_name_IOITR_str[lang]
  if pol == "IWITR":
    return luf.pol_to_name_IWITR_str[lang]
  if pol == "SGRPI":
    return luf.pol_to_name_SGRPI_str[lang]
  if pol == "FEHC":
    return luf.pol_to_name_FEHC_str[lang]
  if pol == "XtaxRateEmp":
    return luf.pol_to_name_XtaxRateEmp_str[lang]
  if pol == "FLWR":
    return luf.pol_to_name_FLWR_str[lang]
  if pol == "RIPLGF":
    return luf.pol_to_name_RIPLGF_str[lang]
  if pol == "FC":
    return luf.pol_to_name_FC_str[lang]
  if pol == "NEP":
    return luf.pol_to_name_NEP_str[lang]
  if pol == "Ctax":
    return luf.pol_to_name_Ctax_str[lang]
  if pol == "DAC":
    return luf.pol_to_name_DAC_str[lang]
  if pol == "XtaxFrac":
    return luf.pol_to_name_XtaxFrac_str[lang]
  if pol == "LPBgrant":
    return luf.pol_to_name_LPBgrant_str[lang]
  if pol == "LPB":
    return luf.pol_to_name_LPB_str[lang]
  if pol == "SSGDR":
    return luf.pol_to_name_SSGDR_str[lang]
  if pol == "ISPV":
    return luf.pol_to_name_ISPV_str[lang]

def get_policy_budgets(reg, ta, yr, cid, lang):
  TA = mg.pov_to_Poverty[ta]
  pol_list = []
  pols = app_tables.policies.search(ta=TA)
  if yr == 2025:
    runde = 1
  elif yr == 2040:
    runde = 2
  elif yr == 2060:
    runde = 3
  else:
    pass
  for pol in pols:
    #    print(pol)
    pol_abbr = pol["abbr"]
    slide_val_row = app_tables.roles_assign.get(
      game_id=cid, reg=reg, role=ta, round=runde, pol=pol_abbr
    )
    slide_val = float(slide_val_row["wert"])
    pol_name = get_pol_name_lang(pol_abbr, lang)
    #    pol_name = pol['name']
    pol_expl = get_pol_expl_lang(pol_abbr, lang)
    #    pol_expl = pol['expl']
    pol_tltl = pol["tltl"]
    pol_gl = pol["gl"]

    fdz = {
      "pol_name": pol_name,   "pol_expl": pol_expl,   "pol_tltl": pol_tltl,   "pol_gl": pol_gl,   "pol_abbr": pol_abbr,   "slide_val": slide_val, }
    pol_list.append(fdz)
  return pol_list

##############################
##############################
##############################
# -*- coding: utf-8 -*-
# Created on Thu 05 Dec 2024 18:12:02
# changed to running rounds from April 04, 2025
# @author: U Goluke
def STEP(zeit, amt, start):
  #    print(zeit,' ',amt,' ',start)
  if zeit < start:
    back = 0
  if zeit >= start:
    back = amt
  #    st.write('zeit=',zeit,' amt=',amt,' start=',start, 'back=',back)
  return back

def SAMPLE_IF_TRUE(zeit, a, t, f, i):
  var_sampeld = np.float64([1.11495,1.04327,1.2296,1.07187,1.07767,1.08293,1.14946,1.07685,1.08014,1.09736,])
  if zeit < a:
    return f
  elif zeit == a:
    var_sampeld[i] = t
    return var_sampeld[i]
  else:
    return var_sampeld[i]

def ZIDZ(a, b):
  if b < 1e-06 and b > -1e-06:
    return 0.0
  else:
    return a / b

def PULSE_TRAIN(zeit, first, duration, every, height):
  s = list(range(first, 2100, every))
  e = list(range(first + duration, 2100, every))
  if len(e) != 3:
    raise ValueError(
      "in PULSE_TRAIN as coded there must be exactly 3 repetitions before 2100"
    )
  if zeit < first:
    return 0
  if ((zeit >= s[0] and zeit < e[0]) or (zeit >= s[1] and zeit < e[1]) or (zeit >= s[2] and zeit < e[2])):
    return height
  else:
    return 0

def SQRT(a):
  return np.sqrt(a)

def GRAPH(x, xarr, yarr):
  last = len(xarr) - 1
  if x < xarr[0]:
    return yarr[0]
  if x > xarr[last]:
    return yarr[last]
  if np.all(np.diff(xarr) == 0):
    print("x not monotonically increasing ==0")
  if np.all(np.diff(xarr) < 0):
    print("x not monotonically increasing <0")
  return np.interp(x, xarr, yarr)

def IF_THEN_ELSE(c, t, f):
  if c:
    return t
  else:
    return f

def get_sorted_pol_list(cid, runde, pol):
  r_to_x = {"us": 0,"af": 1,"cn": 2,"me": 3,"sa": 4,"la": 5,"pa": 6,"ec": 7,"eu": 8,"se": 9}
  rows = app_tables.roles_assign.search(game_id=cid, round=runde, pol=pol)  # in production also use game_id
  dic = {}
  for row in rows:
    rreg2 = r_to_x[row["reg"]]
    dic[rreg2] = row["wert"]
  myKeys = list(dic.keys())
  myKeys.sort()
  sd = {i: dic[i] for i in myKeys}
  pol_list = list(sd.values())
#  print(cid + " " + str(runde) + " " + pol)
#  print(pol_list)
  return pol_list

def ugregmod(game_id, von, bis):
  plot_glob = ["Temp surface anomaly compared to 1850 degC","pH in surface","TROP with normal cover","Planetary risk"]
  plot_reg = ["Energy footprint pp","Fraction of population undernourished","Cost_per_regional_poverty_policy","RoC in Forest land","Total energy use per GDP", "Years of schooling","All SDG Scores","RoC Populated land","Public services pp","Safe sanitation","Smoothed RoC in GDPpp", "Fraction of population below existential minimum","Regenerative cropland fraction","Total government revenue as a proportion of GDP", "El from wind and PV","Labour share of GDP","Cropland","Smoothed Social tension index with trust effect", "LPB investment share","Food footprint kgN ppy","Life expectancy at birth","GenderEquality","Social trust","Total CO2 emissions", "Social trust","Safe water","Access to electricity","Carbon intensity","Disposable income pp post tax pre loan impact","Population", "Average wellbeing index","Local private and govt investment share","Unemployment rate smoothed","Renewable energy share in the total final energy consumption", "GDP USED","Nitrogen use per ha","Budget_for_all_TA_per_region","Cost_per_regional_inequality_policy","Cost_per_regional_empowerment_policy", "Cost_per_regional_food_policy","Cost_per_regional_energy_policy"]

  pg = []
  pr = []
  for i in range(0, len(plot_glob)):
    v = plot_glob[i]
    v = v.replace(" ", "_")
    v = v.replace("_alt", "")
    pg.append(v)
  plot_glob = list(dict.fromkeys(pg))

  for i in range(0, len(plot_reg)):
    v = plot_reg[i]
    v = v.replace(" ", "_")
    v = v.replace("_alt", "")
    pr.append(v)
  plot_reg = list(dict.fromkeys(pr))

  ## policies for each round. ______R[1|2|3]_via_Excel to be read in
  ## from anvil DB
  StrUP_policy_Max = 3
  StrUP_policy_Min = 0.0
  StrUP_R3_via_Excel = get_sorted_pol_list(game_id, 3, "StrUP")
  StrUP_R2_via_Excel = get_sorted_pol_list(game_id, 2, "StrUP")
  StrUP_R1_via_Excel = get_sorted_pol_list(game_id, 1, "StrUP")
  #    StrUP_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    StrUP_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    StrUP_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  SGMP_policy_Max = 10
  SGMP_policy_Min = 0.0
  SGMP_R3_via_Excel = get_sorted_pol_list(game_id, 3, "SGMP")
  SGMP_R2_via_Excel = get_sorted_pol_list(game_id, 2, "SGMP")
  SGMP_R1_via_Excel = get_sorted_pol_list(game_id, 1, "SGMP")
  #    SGMP_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    SGMP_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    SGMP_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  IWITR_policy_Max = 10
  IWITR_policy_Min = 0.0
  IWITR_R3_via_Excel = get_sorted_pol_list(game_id, 3, "IWITR")
  IWITR_R2_via_Excel = get_sorted_pol_list(game_id, 2, "IWITR")
  IWITR_R1_via_Excel = get_sorted_pol_list(game_id, 1, "IWITR")
  #    IWITR_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    IWITR_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    IWITR_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  FWRP_policy_Max = 90
  FWRP_policy_Min = 0.0
  FWRP_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FWRP")
  FWRP_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FWRP")
  FWRP_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FWRP")
  #    FWRP_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FWRP_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FWRP_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  IOITR_policy_Max = 10
  IOITR_policy_Min = 0.0
  IOITR_R3_via_Excel = get_sorted_pol_list(game_id, 3, "IOITR")
  IOITR_R2_via_Excel = get_sorted_pol_list(game_id, 2, "IOITR")
  IOITR_R1_via_Excel = get_sorted_pol_list(game_id, 1, "IOITR")
  #    IOITR_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    IOITR_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    IOITR_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  XtaxRateEmp_policy_Max = 5
  XtaxRateEmp_policy_Min = 0.0
  XtaxEmp_R3_via_Excel = get_sorted_pol_list(game_id, 3, "XtaxRateEmp")
  XtaxEmp_R2_via_Excel = get_sorted_pol_list(game_id, 2, "XtaxRateEmp")
  XtaxEmp_R1_via_Excel = get_sorted_pol_list(game_id, 1, "XtaxRateEmp")
  #    XtaxEmp_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    XtaxEmp_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    XtaxEmp_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  Xtaxfrac_policy_Max = 90
  Xtaxfrac_policy_Min = 50.0
  XtaxFrac_R3_via_Excel = get_sorted_pol_list(game_id, 3, "XtaxFrac")
  XtaxFrac_R2_via_Excel = get_sorted_pol_list(game_id, 2, "XtaxFrac")
  XtaxFrac_R1_via_Excel = get_sorted_pol_list(game_id, 1, "XtaxFrac")
  #    XtaxFrac_R3_via_Excel = [50, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
  #    XtaxFrac_R2_via_Excel = [50, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
  #    XtaxFrac_R1_via_Excel = [50, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
  XtaxCom_policy_Max = 5
  XtaxCom_policy_Min = 0.0
  XtaxCom_R3_via_Excel = get_sorted_pol_list(game_id, 3, "XtaxCom")
  XtaxCom_R2_via_Excel = get_sorted_pol_list(game_id, 2, "XtaxCom")
  XtaxCom_R1_via_Excel = get_sorted_pol_list(game_id, 1, "XtaxCom")
  #    XtaxCom_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    XtaxCom_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    XtaxCom_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  TOW_policy_Max = 80
  TOW_policy_Min = 0.0
  TOW_R3_via_Excel = get_sorted_pol_list(game_id, 3, "TOW")
  TOW_R2_via_Excel = get_sorted_pol_list(game_id, 2, "TOW")
  TOW_R1_via_Excel = get_sorted_pol_list(game_id, 1, "TOW")
  #    TOW_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    TOW_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    TOW_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  NEP_policy_Max = 95
  NEP_policy_Min = 0.0
  NEP_R3_via_Excel = get_sorted_pol_list(game_id, 3, "NEP")
  NEP_R2_via_Excel = get_sorted_pol_list(game_id, 2, "NEP")
  NEP_R1_via_Excel = get_sorted_pol_list(game_id, 1, "NEP")
  #    NEP_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    NEP_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    NEP_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  CCS_policy_Max = 80
  CCS_policy_Min = 0.0
  CCS_R3_via_Excel = get_sorted_pol_list(game_id, 3, "CCS")
  CCS_R2_via_Excel = get_sorted_pol_list(game_id, 2, "CCS")
  CCS_R1_via_Excel = get_sorted_pol_list(game_id, 1, "CCS")
  #    CCS_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    CCS_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    CCS_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  Ctax_policy_Max = 100
  Ctax_policy_Min = 0.0
  Ctax_R3_via_Excel = get_sorted_pol_list(game_id, 3, "Ctax")
  Ctax_R2_via_Excel = get_sorted_pol_list(game_id, 2, "Ctax")
  Ctax_R1_via_Excel = get_sorted_pol_list(game_id, 1, "Ctax")
  #    Ctax_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    Ctax_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    Ctax_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  Lfrac_policy_Max = 100
  Lfrac_policy_Min = 0.0
  Lfrac_R3_via_Excel = get_sorted_pol_list(game_id, 3, "Lfrac")
  Lfrac_R2_via_Excel = get_sorted_pol_list(game_id, 2, "Lfrac")
  Lfrac_R1_via_Excel = get_sorted_pol_list(game_id, 1, "Lfrac")
  #    Lfrac_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    Lfrac_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    Lfrac_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  SSGDR_policy_Max = 5
  SSGDR_policy_Min = 1.0
  SSGDR_R3_via_Excel = get_sorted_pol_list(game_id, 3, "SSGDR")
  SSGDR_R2_via_Excel = get_sorted_pol_list(game_id, 2, "SSGDR")
  SSGDR_R1_via_Excel = get_sorted_pol_list(game_id, 1, "SSGDR")
  #    SSGDR_R3_via_Excel = [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  #    SSGDR_R2_via_Excel = [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  #    SSGDR_R1_via_Excel = [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  FMPLDD_policy_Max = 90
  FMPLDD_policy_Min = 0.0
  FMPLDD_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FMPLDD")
  FMPLDD_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FMPLDD")
  FMPLDD_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FMPLDD")
  #    FMPLDD_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FMPLDD_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FMPLDD_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  SGRPI_policy_Max = 50
  SGRPI_policy_Min = 0.0
  SGRPI_R3_via_Excel = get_sorted_pol_list(game_id, 3, "SGRPI")
  SGRPI_R2_via_Excel = get_sorted_pol_list(game_id, 2, "SGRPI")
  SGRPI_R1_via_Excel = get_sorted_pol_list(game_id, 1, "SGRPI")
  #    SGRPI_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    SGRPI_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    SGRPI_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  LPB_policy_Max = 30
  LPB_policy_Min = 0.0
  LPB_R3_via_Excel = get_sorted_pol_list(game_id, 3, "LPB")
  LPB_R2_via_Excel = get_sorted_pol_list(game_id, 2, "LPB")
  LPB_R1_via_Excel = get_sorted_pol_list(game_id, 1, "LPB")
  #    LPB_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    LPB_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    LPB_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  LPBsplit_policy_Max = 100
  LPBsplit_policy_Min = 0.0
  LPBsplit_R3_via_Excel = get_sorted_pol_list(game_id, 3, "LPBsplit")
  LPBsplit_R2_via_Excel = get_sorted_pol_list(game_id, 2, "LPBsplit")
  LPBsplit_R1_via_Excel = get_sorted_pol_list(game_id, 1, "LPBsplit")
  #    LPBsplit_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    LPBsplit_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    LPBsplit_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  FEHC_policy_Max = 10
  FEHC_policy_Min = 0.0
  FEHC_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FEHC")
  FEHC_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FEHC")
  FEHC_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FEHC")
  #    FEHC_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FEHC_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FEHC_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  RMDR_policy_Max = 95
  RMDR_policy_Min = 0.0
  RMDR_R3_via_Excel = get_sorted_pol_list(game_id, 3, "RMDR")
  RMDR_R2_via_Excel = get_sorted_pol_list(game_id, 2, "RMDR")
  RMDR_R1_via_Excel = get_sorted_pol_list(game_id, 1, "RMDR")
  #    RMDR_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    RMDR_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    RMDR_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  RIPLGF_policy_Max = 50
  RIPLGF_policy_Min = 0.0
  RIPLGF_R3_via_Excel = get_sorted_pol_list(game_id, 3, "RIPLGF")
  RIPLGF_R2_via_Excel = get_sorted_pol_list(game_id, 2, "RIPLGF")
  RIPLGF_R1_via_Excel = get_sorted_pol_list(game_id, 1, "RIPLGF")
  #    RIPLGF_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    RIPLGF_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    RIPLGF_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  DAC_policy_Max = 1.5
  DAC_policy_Min = 0.0
  DAC_R3_via_Excel = get_sorted_pol_list(game_id, 3, "DAC")
  DAC_R2_via_Excel = get_sorted_pol_list(game_id, 2, "DAC")
  DAC_R1_via_Excel = get_sorted_pol_list(game_id, 1, "DAC")
  #    DAC_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    DAC_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    DAC_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ISPV_policy_Max = 95
  ISPV_policy_Min = 50.0
  ISPV_R3_via_Excel = get_sorted_pol_list(game_id, 3, "ISPV")
  ISPV_R2_via_Excel = get_sorted_pol_list(game_id, 2, "ISPV")
  ISPV_R1_via_Excel = get_sorted_pol_list(game_id, 1, "ISPV")
  #    ISPV_R3_via_Excel = [50, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
  #    ISPV_R2_via_Excel = [50, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
  #    ISPV_R1_via_Excel = [50, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]
  FLWR_policy_Max = 95
  FLWR_policy_Min = 0.0
  FLWR_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FLWR")
  FLWR_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FLWR")
  FLWR_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FLWR")
  #    FLWR_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FLWR_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FLWR_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  FTPEE_policy_Max = 2.5
  FTPEE_policy_Min = 1.0
  FTPEE_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FTPEE")
  FTPEE_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FTPEE")
  FTPEE_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FTPEE")
  #    FTPEE_R3_via_Excel = [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  #    FTPEE_R2_via_Excel = [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  #    FTPEE_R1_via_Excel = [1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
  FPGDC_policy_Max = 100
  FPGDC_policy_Min = 0.0
  FPGDC_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FPGDC")
  FPGDC_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FPGDC")
  FPGDC_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FPGDC")
  #    FPGDC_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FPGDC_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FPGDC_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ICTR_policy_Max = 10
  ICTR_policy_Min = 0.0
  ICTR_R3_via_Excel = get_sorted_pol_list(game_id, 3, "ICTR")
  ICTR_R2_via_Excel = get_sorted_pol_list(game_id, 2, "ICTR")
  ICTR_R1_via_Excel = get_sorted_pol_list(game_id, 1, "ICTR")
  #    ICTR_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    ICTR_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    ICTR_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  LPBgrant_policy_Max = 100
  LPBgrant_policy_Min = 0.0
  LPBgrant_R3_via_Excel = get_sorted_pol_list(game_id, 3, "LPBgrant")
  LPBgrant_R2_via_Excel = get_sorted_pol_list(game_id, 2, "LPBgrant")
  LPBgrant_R1_via_Excel = get_sorted_pol_list(game_id, 1, "LPBgrant")
  #    LPBgrant_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    LPBgrant_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    LPBgrant_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  WReaction_policy_Max = 3
  WReaction_policy_Min = 0.0
  Wreaction_R3_via_Excel = get_sorted_pol_list(game_id, 3, "Wreaction")
  Wreaction_R2_via_Excel = get_sorted_pol_list(game_id, 2, "Wreaction")
  Wreaction_R1_via_Excel = get_sorted_pol_list(game_id, 1, "Wreaction")
  #    Wreaction_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    Wreaction_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    Wreaction_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  Forest_cutting_policy_Max = 90
  Forest_cutting_policy_Min = 0.0
  FC_R3_via_Excel = get_sorted_pol_list(game_id, 3, "FC")
  FC_R2_via_Excel = get_sorted_pol_list(game_id, 2, "FC")
  FC_R1_via_Excel = get_sorted_pol_list(game_id, 1, "FC")
  #    FC_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FC_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    FC_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  REFOREST_policy_Max = 3
  REFOREST_policy_Min = 0.0
  REFOREST_R3_via_Excel = get_sorted_pol_list(game_id, 3, "REFOREST")
  REFOREST_R2_via_Excel = get_sorted_pol_list(game_id, 2, "REFOREST")
  REFOREST_R1_via_Excel = get_sorted_pol_list(game_id, 1, "REFOREST")
  #    REFOREST_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    REFOREST_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    REFOREST_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  ExPS_policy_Max = 100
  ExPS_policy_Min = 0.0
  ExPS_R3_via_Excel = get_sorted_pol_list(game_id, 3, "ExPS")
  ExPS_R2_via_Excel = get_sorted_pol_list(game_id, 2, "ExPS")
  ExPS_R1_via_Excel = get_sorted_pol_list(game_id, 1, "ExPS")
  #    ExPS_R3_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    ExPS_R2_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
  #    ExPS_R1_via_Excel = [0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

  #    ExPS_R1_via_Excel = [77.64, 0, 0, 0, 0, 0, 0, 0, 0, 73.36]
  #    ExPS_R2_via_Excel = [84.71, 0, 0, 0, 0, 0, 0, 0, 0, 62.96]
  #    ExPS_R3_via_Excel = [58.33, 0, 0, 0, 0, 0, 0, 0, 0, 88.49]
  #    LPB_R1_via_Excel = [25.64, 0, 0, 0, 0, 0, 0, 0, 0, 24.59]
  #    LPB_R2_via_Excel = [25.25, 0, 0, 0, 0, 0, 0, 0, 0, 15.54]
  #    LPB_R3_via_Excel = [16.32, 0, 0, 0, 0, 0, 0, 0, 0, 27.71]
  #    LPBsplit_R1_via_Excel = [76.95, 0, 0, 0, 0, 0, 0, 0, 0, 69.09]
  #    LPBsplit_R2_via_Excel = [78.66, 0, 0, 0, 0, 0, 0, 0, 0, 75.29]
  #    LPBsplit_R3_via_Excel = [78.03, 0, 0, 0, 0, 0, 0, 0, 0, 86.93]
  #    LPBgrant_R1_via_Excel = [60.23, 0, 0, 0, 0, 0, 0, 0, 0, 53.01]
  #    LPBgrant_R2_via_Excel = [76.34, 0, 0, 0, 0, 0, 0, 0, 0, 69.73]
  #    LPBgrant_R3_via_Excel = [75.77, 0, 0, 0, 0, 0, 0, 0, 0, 99.15]
  #    FMPLDD_R1_via_Excel = [73.27, 0, 0, 0, 0, 0, 0, 0, 0, 77.3]
  #    FMPLDD_R2_via_Excel = [73.73, 0, 0, 0, 0, 0, 0, 0, 0, 49.96]
  #    FMPLDD_R3_via_Excel = [50.59, 0, 0, 0, 0, 0, 0, 0, 0, 51.2]
  #    TOW_R1_via_Excel = [77.03, 0, 0, 0, 0, 0, 0, 0, 0, 79.3]
  #    TOW_R2_via_Excel = [41.59, 0, 0, 0, 0, 0, 0, 0, 0, 69.54]
  #    TOW_R3_via_Excel = [48.77, 0, 0, 0, 0, 0, 0, 0, 0, 43.53]
  #    FPGDC_R1_via_Excel = [84.4, 0, 0, 0, 0, 0, 0, 0, 0, 58.04]
  #    FPGDC_R2_via_Excel = [78.24, 0, 0, 0, 0, 0, 0, 0, 0, 68.25]
  #    FPGDC_R3_via_Excel = [58.15, 0, 0, 0, 0, 0, 0, 0, 0, 55.88]
  #    Lfrac_R1_via_Excel = [90.49, 0, 0, 0, 0, 0, 0, 0, 0, 98.64]
  #    Lfrac_R2_via_Excel = [73.83, 0, 0, 0, 0, 0, 0, 0, 0, 61.94]
  #    Lfrac_R3_via_Excel = [56.77, 0, 0, 0, 0, 0, 0, 0, 0, 79.22]
  #    SSGDR_R1_via_Excel = [3.66, 1, 1, 1, 1, 1, 1, 1, 1, 3.06]
  #    SSGDR_R2_via_Excel = [3.31, 1, 1, 1, 1, 1, 1, 1, 1, 3.84]
  #    SSGDR_R3_via_Excel = [4.51, 1, 1, 1, 1, 1, 1, 1, 1, 3.47]
  #    XtaxFrac_R1_via_Excel = [70.21, 50, 50, 50, 50, 50, 50, 50, 50, 75.86]
  #    XtaxFrac_R2_via_Excel = [84.62, 50, 50, 50, 50, 50, 50, 50, 50, 83.68]
  #    XtaxFrac_R3_via_Excel = [71.19, 50, 50, 50, 50, 50, 50, 50, 50, 70.6]
  #    StrUP_R1_via_Excel = [1.51, 0, 0, 0, 0, 0, 0, 0, 0, 2.74]
  #    StrUP_R2_via_Excel = [2.51, 0, 0, 0, 0, 0, 0, 0, 0, 1.92]
  #    StrUP_R3_via_Excel = [2.91, 0, 0, 0, 0, 0, 0, 0, 0, 2.74]
  #    Wreaction_R1_via_Excel = [2.5, 0, 0, 0, 0, 0, 0, 0, 0, 2.23]
  #    Wreaction_R2_via_Excel = [2.54, 0, 0, 0, 0, 0, 0, 0, 0, 1.95]
  #    Wreaction_R3_via_Excel = [2.62, 0, 0, 0, 0, 0, 0, 0, 0, 1.93]
  #    XtaxCom_R1_via_Excel = [2.58, 0, 0, 0, 0, 0, 0, 0, 0, 4.97]
  #    XtaxCom_R2_via_Excel = [4.61, 0, 0, 0, 0, 0, 0, 0, 0, 3.38]
  #    XtaxCom_R3_via_Excel = [2.51, 0, 0, 0, 0, 0, 0, 0, 0, 4.69]
  #    ICTR_R1_via_Excel = [6.73, 0, 0, 0, 0, 0, 0, 0, 0, 5.92]
  #    ICTR_R2_via_Excel = [6.71, 0, 0, 0, 0, 0, 0, 0, 0, 6.03]
  #    ICTR_R3_via_Excel = [5.78, 0, 0, 0, 0, 0, 0, 0, 0, 5.17]
  #    IOITR_R1_via_Excel = [8.71, 0, 0, 0, 0, 0, 0, 0, 0, 6.5]
  #    IOITR_R2_via_Excel = [9.74, 0, 0, 0, 0, 0, 0, 0, 0, 8.92]
  #    IOITR_R3_via_Excel = [6.72, 0, 0, 0, 0, 0, 0, 0, 0, 9.87]
  #    IWITR_R1_via_Excel = [8.87, 0, 0, 0, 0, 0, 0, 0, 0, 6.24]
  #    IWITR_R2_via_Excel = [6.34, 0, 0, 0, 0, 0, 0, 0, 0, 6.47]
  #    IWITR_R3_via_Excel = [6.1, 0, 0, 0, 0, 0, 0, 0, 0, 8.56]
  #    Ctax_R1_via_Excel = [64.87, 0, 0, 0, 0, 0, 0, 0, 0, 61.81]
  #    Ctax_R2_via_Excel = [72.62, 0, 0, 0, 0, 0, 0, 0, 0, 79.01]
  #    Ctax_R3_via_Excel = [74.57, 0, 0, 0, 0, 0, 0, 0, 0, 87.66]
  #    SGRPI_R1_via_Excel = [25.72, 0, 0, 0, 0, 0, 0, 0, 0, 45.73]
  #    SGRPI_R2_via_Excel = [46.18, 0, 0, 0, 0, 0, 0, 0, 0, 46.05]
  #    SGRPI_R3_via_Excel = [37.37, 0, 0, 0, 0, 0, 0, 0, 0, 33.38]
  #    FEHC_R1_via_Excel = [9.81, 0, 0, 0, 0, 0, 0, 0, 0, 5.3]
  #    FEHC_R2_via_Excel = [5.09, 0, 0, 0, 0, 0, 0, 0, 0, 6.03]
  #    FEHC_R3_via_Excel = [7.6, 0, 0, 0, 0, 0, 0, 0, 0, 8.44]
  #    XtaxRateEmp_R1_via_Excel = [3.43, 0, 0, 0, 0, 0, 0, 0, 0, 2.77]
  #    XtaxRateEmp_R2_via_Excel = [3.07, 0, 0, 0, 0, 0, 0, 0, 0, 3.44]
  #    XtaxRateEmp_R3_via_Excel = [3.41, 0, 0, 0, 0, 0, 0, 0, 0, 3.94]
  #    SGMP_R1_via_Excel = [7.32, 0, 0, 0, 0, 0, 0, 0, 0, 9.32]
  #    SGMP_R2_via_Excel = [9.56, 0, 0, 0, 0, 0, 0, 0, 0, 6.61]
  #    SGMP_R3_via_Excel = [5.19, 0, 0, 0, 0, 0, 0, 0, 0, 5.58]
  #    FWRP_R1_via_Excel = [46.72, 0, 0, 0, 0, 0, 0, 0, 0, 72.64]
  #    FWRP_R2_via_Excel = [65.29, 0, 0, 0, 0, 0, 0, 0, 0, 49.5]
  #    FWRP_R3_via_Excel = [67.57, 0, 0, 0, 0, 0, 0, 0, 0, 59.73]
  #    FLWR_R1_via_Excel = [50.19, 0, 0, 0, 0, 0, 0, 0, 0, 56.95]
  #    FLWR_R2_via_Excel = [61.09, 0, 0, 0, 0, 0, 0, 0, 0, 79.95]
  #    FLWR_R3_via_Excel = [51.01, 0, 0, 0, 0, 0, 0, 0, 0, 74.72]
  #    RMDR_R1_via_Excel = [74.23, 0, 0, 0, 0, 0, 0, 0, 0, 89.52]
  #    RMDR_R2_via_Excel = [70.68, 0, 0, 0, 0, 0, 0, 0, 0, 56.49]
  #    RMDR_R3_via_Excel = [86.22, 0, 0, 0, 0, 0, 0, 0, 0, 65.78]
  #    RIPLGF_R1_via_Excel = [39.33, 0, 0, 0, 0, 0, 0, 0, 0, 38.61]
  #    RIPLGF_R2_via_Excel = [44.24, 0, 0, 0, 0, 0, 0, 0, 0, 49.99]
  #    RIPLGF_R3_via_Excel = [44.41, 0, 0, 0, 0, 0, 0, 0, 0, 28.45]
  #    FC_R1_via_Excel = [87.22, 0, 0, 0, 0, 0, 0, 0, 0, 63.56]
  #    FC_R2_via_Excel = [87.07, 0, 0, 0, 0, 0, 0, 0, 0, 77.93]
  #    FC_R3_via_Excel = [61.98, 0, 0, 0, 0, 0, 0, 0, 0, 46.46]
  #    REFOREST_R1_via_Excel = [1.52, 0, 0, 0, 0, 0, 0, 0, 0, 1.61]
  #    REFOREST_R2_via_Excel = [2.73, 0, 0, 0, 0, 0, 0, 0, 0, 2.96]
  #    REFOREST_R3_via_Excel = [2.14, 0, 0, 0, 0, 0, 0, 0, 0, 2.68]
  #    FTPEE_R1_via_Excel = [2.41, 1, 1, 1, 1, 1, 1, 1, 1, 2.45]
  #    FTPEE_R2_via_Excel = [1.77, 1, 1, 1, 1, 1, 1, 1, 1, 2.48]
  #    FTPEE_R3_via_Excel = [1.99, 1, 1, 1, 1, 1, 1, 1, 1, 1.87]
  #    NEP_R1_via_Excel = [54.79, 0, 0, 0, 0, 0, 0, 0, 0, 59.37]
  #    NEP_R2_via_Excel = [92.06, 0, 0, 0, 0, 0, 0, 0, 0, 90.93]
  #    NEP_R3_via_Excel = [59, 0, 0, 0, 0, 0, 0, 0, 0, 72.16]
  #    ISPV_R1_via_Excel = [90.4, 50, 50, 50, 50, 50, 50, 50, 50, 89.78]
  #    ISPV_R2_via_Excel = [88.95, 50, 50, 50, 50, 50, 50, 50, 50, 85.69]
  #    ISPV_R3_via_Excel = [85.8, 50, 50, 50, 50, 50, 50, 50, 50, 80.13]
  #    CCS_R1_via_Excel = [45.18, 0, 0, 0, 0, 0, 0, 0, 0, 42.64]
  #    CCS_R2_via_Excel = [61.47, 0, 0, 0, 0, 0, 0, 0, 0, 76.64]
  #    CCS_R3_via_Excel = [56.82, 0, 0, 0, 0, 0, 0, 0, 0, 55.78]
  #    DAC_R1_via_Excel = [1.26, 0, 0, 0, 0, 0, 0, 0, 0, 1.07]
  #    DAC_R2_via_Excel = [1.41, 0, 0, 0, 0, 0, 0, 0, 0, 0.98]
  #    DAC_R3_via_Excel = [0.81, 0, 0, 0, 0, 0, 0, 0, 0, 1.03]
  #
  #    Capital_output_ratio_in_1980 = ([3, 8, 1.6, 8, 8, 6, 4, 5, 3, 8])
  Employed_in_1980 = [103, 139, 494, 41, 322, 114, 92, 163, 194, 128]
  SoE_of_inventory_on_indicated_hours_worked_index = [-1, -1, -0.6, -1, -1, -1, -1, -1, -1, -1]
  #    Perceived_relative_inventory_in_1980 = ([1, 1, 1, 1, 0.89, 0.8, 0.89, 1, 0.8, 1])
  #    Cohort_0_to_4_in_1980 = (
  #        [16.907701, 66.801562, 103.943347, 31.569206, 135.398637, 51.48271, 17.468252, 30.095115, 36.461211,
  #        52.640757])
#  Cohort_10_to_14_in_1980 = [18.937472, 43.940929, 133.948072, 22.767273, 103.455397, 43.046737, 19.352604, 26.373505, 40.038377, 44.788868]
#  Cohort_15_to_19_in_1980 = [21.517461, 37.081781, 110.482973, 19.527712, 92.45383, 38.903513, 18.357064, 28.52345, 40.461573, 39.511144]
#  Cohort_5_to_9_in_1980 = [17.16009, 53.164399, 128.476879, 26.126713, 116.397822, 46.652054, 20.355446, 28.12971, 37.948148, 48.979344]
#  Cohort_20_to_24_in_1980 = [21.8119, 30.9356, 90.8949, 16.2883, 80.2574, 33.0054, 17.9121, 29.3363, 38.3132, 33.8076]
#  Cohort_25_to_29_in_1980 = [20.1388, 25.7601, 93.9462, 13.5363, 68.8477, 27.871, 16.9721, 27.0832, 35.9392, 27.1812]
#  Cohort_30_to_34_in_1980 = [17.9741, 21.4953, 66.5902, 10.1467, 54.7314, 22.3587, 18.112, 21.9265, 34.3898, 20.3428]
#  Cohort_35_to_39_in_1980 = [14.1212, 18.1089, 51.7003, 8.11063, 47.8514, 18.4678, 15.4939, 15.9304, 29.6731, 17.5491]
#  Cohort_40to_44_in_1980 = [12.0704, 15.1989, 49.1493, 7.57296, 43.0932, 16.0675, 13.9846, 23.9835, 29.6751, 16.2267]
#  Cohort_45_to_49_in_1980 = [11.2448, 12.9651, 45.6996, 6.93185, 37.0717, 13.7945, 12.771, 18.9808, 28.5509, 14.2525]
#  Cohort_50_to_54_in_1980 = [11.8282, 10.7494, 38.8158, 5.90496, 31.0911, 12.1465, 11.2918, 21.2099, 27.634, 11.6688]
#  Cohort_55_to_59_in_1980 = [11.7494, 8.77535, 32.7015, 4.77509, 25.2041, 9.80378, 9.31261, 14.8069, 26.0149, 9.27789]
#  Cohort_60to_64_in_1980 = [10.3383, 6.85514, 28.8279, 3.5816, 19.5622, 7.63257, 7.39933, 9.67908, 17.9898, 7.30147]
#  Cohort_65_to_69_in_1980 = [9.05561, 4.99637, 21.6784, 2.67587, 14.1206, 6.14692, 6.37421, 11.5565, 20.9206, 5.76418]
#  Cohort_70_to_74_in_1980 = [7.12572, 3.26783, 13.93, 1.9277, 9.35538, 4.35627, 4.72676, 8.85296, 17.7072, 3.98601]
#  Cohort_75_to_79_in_1980 = [5.33309, 1.78414, 7.96522, 1.14022, 5.04137, 2.7543, 3.06813, 5.64866, 12.3354, 2.32888]
#  Cohort_80_to_84_in_1980 = [2.9033, 0.730893, 3.1889, 0.527981, 2.38067, 1.44232, 1.65191, 2.70643, 6.80679, 1.07722]
#  Cohort_85_to_89_in_1980 = [1.65033, 0.193374, 0.968024, 0.168828, 0.729614, 0.527403, 0.665821, 1.10846, 2.78283, 0.360152]
#  Cohort_90_to_94_in_1980 = [0.564662, 0.02922, 0.173605, 0.0348, 0.187232, 0.145646, 0.185384, 0.364529, 0.791019, 0.085622]
#  Cohort_95p_in_1980 = [0.134325, 0.002834, 0.020406, 0.004407, 0.033359, 0.029358, 0.031645, 0.075015, 0.13436, 0.015641]
  cereal_dmd_func_pp_L = [220, 250, 199, 230, 290, 200, 250, 250, 250, 275]
  cereal_dmd_func_pp_k = [0.06, 0.3, 0.1, 0.081, 0.19, 0.078, 0.01, 0.01, 0.0189, 0.3]
  cereal_dmd_func_pp_x0 = [10, 3, 1, -6.46, 1, 1.1368, 1, -50, -2.2, 2]
  Food_wasted_in_1980 = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
#  Unemployment_in_1980 = [8, 10, 35, 5, 10, 5, 5, 5, 15, 10]
  Life_expec_a = [47, 36, 64, 40, 57, 40, 53, 47, 35, 58]
  Life_expec_b = [10, 15, 7, 10, 8, 10, 8, 10, 13, 8]
  Life_expectancy_at_birth_in_1980 = [73.8, 48.5, 66.8, 58.2, 54, 64.5, 73.3, 66.8, 72, 60.4]
  Pension_age_in_1980 = [65, 65, 65, 65, 65, 65, 65, 65, 65, 65]
  SoE_of_LE_on_Pension_age = [0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
  Indicated_WACC_fraction = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
  OSF_in_1980 = [0.8, 0.2, 0.45, 0.4, 0.3, 0.4, 0.85, 0.4, 0.8, 0.3]
#  Fraction_multiple_of_regional_GDP_as_owners_wealth_in_1980 = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
  toe_to_CO2_a = [2.7, 2.8, 2.6, 2.16, 2.4, 2.37, 2, 3, 2.1, 2.1]
  Fossil_use_pp_NOT_for_El_gen_WO_CN_L = [5.7, 4, 4, 3.5, 4, 3.5, 3.5, 4, 9.7, 4]
  Fossil_use_pp_NOT_for_El_gen_WO_CN_k = [-0.06, 0.25, 0.01, 0.055, 0.197, 0.027, 0.0395, 0.05, -0.0205, 0.1]
  Fossil_use_pp_NOT_for_El_gen_WO_CN_x0 = [80, 15, 1, 22.03, 16.81, 60, 6.134, 20, -25, 26.5]
  Hydro_gen_cap_L = [85, 100, 500, 13, 80, 200, 150, 84, 200, 65]
  Hydro_gen_cap_k = [0.045, 0.4, 0.3, 0.15, 0.25, 0.3, 0.04, 0.08, 0.045, 0.3]
  Hydro_gen_cap_x0 = [12, 7.2, 11, 8, 4, 6, -2, 6, 12, 7.5]
  Hydrocapacity_factor = [0.45, 0.45, 0.41, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45]
#  Fossil_el_gen_cap_in_1980 = [200, 30, 50, 30, 10, 25, 70, 160, 160, 20]
  Fossil_actual_uptime_factor = [0.82, 1, 1, 1, 1, 1, 1, 1, 0.81, 1]
  Conversion_Mtoe_to_TWh = [4, 4, 4, 4, 4, 4.5, 5, 4.5, 4, 4]
  toe_to_CO2_b = [1, 0, -0.0036, 0.1599, 0.1, 0.15, 0.8, 0.0347, 1, 0.1]
  CO2_emi_from_IPC2_use_a = [-0.132, 0.0494, 0.7005, 0.2, 0.0882, 0.1347, 0.0352, -0.056, -0.038, 0.1055]
  CO2_emi_from_IPC2_use_b = [0.7855, -0.0029, -0.5722, -0.35, 0.0396, -0.1619, 0.0264, 0.4819, 0.4481, -0.0839]
#  Govt_debt_initially_as_frac_of_NI = [0.5, 1, 0.2, 1, 1, 1, 1, 1, 1, 1]
#  Central_bank_signal_rate_in_1980 = [0.13, 0.1, 0.1, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13, 0.13]
  Reference_max_govt_debt_burden = [2, 2, 1.25, 2, 2, 2, 2, 2, 2, 2]
#  GE_in_1980 = [0.3, 0.2, 0.4, 0.1, 0.17, 0.3, 0.28, 0.38, 0.28, 0.25]
  oth_crop_dmd_pp_a = [61.5666, 155.265, 218.985, 103.477, 89.3181, 713.147, 44.8079, -63.6056, -118.483, 113.732]
  oth_crop_dmd_pp_b = [351.895, 288.935, 157.457, 149.41, 322.62, -129.904, 285.873, 820.263, 1183.46, 280.016]
#  Barren_land_in_1980 = [59.725, 598.224, 302.224, 532.885, 61.2205, 231.005, 562.628, 75.1457, 225.261, 15.9273]
  Normal_signal_rate = [0.02, 0.04, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02, 0.02]
#  Cropland_in_1980 = [190.624, 131.158, 100.219, 51.67, 214.32, 138.743, 68.646, 248.075, 145.678, 77.2311]
#  Forest_land_in_1980 = [257.393, 297.096, 213.879, 50, 35.6341, 769.077, 620.972, 1066.66, 118.106, 234.835]
  Frac_outside_of_labour_pool_in_1980 = [0.52, 0.77, 0.47, 0.69, 0.61, 0.62, 0.55, 0.58, 0.58, 0.53]
#  Grazing_land_in_1980 = [237.539, 609.232, 328.3, 227.076, 20.209, 512.548, 513.767, 452.092, 81.1108, 15.133]
#  Populated_land_in_1980 = [43.4524, 3.612, 48.6394, 3.82125, 6.94276, 9.03042, 13.6515, 2.953, 14.5271, 6.66976]
#  Rate_of_tech_advance_RoTA_in_TFP_in_1980 = [0.019, 0.0225, 0.05, 0.0375, 0.06, 0.035, 0.0275, 0.03, 0.0225, 0.06]
#  Worker_debt_ratio_in_1980 = [1, 0.2, 0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
  Feed_dmd_a = [79.37, 266.31, 465.61, 91.78, 619.57, 105.51, 23.507, 113.92, 115.57, 169.85]
  red_meat_dmd_func_pp_L = [33.6, 20, 20, 15, 20, 35, 20, 20, 21, 20]
  red_meat_dmd_func_pp_k = [-0.053, 0.13, 0.13, 0.0469, 0.01, 0.065, 0.01, 0.03, -0.044, 0.05]
  red_meat_dmd_func_pp_x0 = [63.233, 7.5, 16, -2.97, 1, -3.03, 1, -35, 49, 37]
  red_meat_dmd_func_pp_min = [20, 0, 0, 0, 0, 0, 0, 0, 5, 0]
  Desired_net_export_of_red_meat = [0.1, -0.06, -0.06, -0.35, -0.06, 0.1, 0.1, 0.1, 0.1, -0.06]
  white_meat_dmd_func_pp_L = [120, 50, 50, 50, 20, 65, 70, 65, 58, 50]
  white_meat_dmd_func_pp_k = [0.0313, 0.3, 0.1, 0.122, 0.2, 0.2, 0.04, 0.075, 0.18, 0.1]
  white_meat_dmd_func_pp_x0 = [31.39, 11, 1, 21.97, 14, 10, 31, 17, 11.7, 11]
  Feed_dmd_b = [-151.9, -267.87, -1104.3, -1.2125, -702.71, -165.85, 31.095, -168.57, -180.11, -208.09]
  Desired_net_export_of_crops = [0.23, 0, 0, -0.2, 0, 0.3, 0, 0.3, 0.05, 0.4]
#  crop_yield_in_1980 = [2.5, 1.5, 4.8, 1.6, 2, 1.6, 2.33, 1.6, 4.5, 3.2]
  Fraction_of_supply_imbalance_to_be_closed_by_land = [0.1, 1, 1, 1, 1, 0.1, 0, 0.1, 0.1, 1]
  Fraction_of_cropland_gap_closed_from_acgl = [1, 1, 1, 1, 1, 1, 0, 1, 1, 1]
  Grazing_land_Rest_L = [300, 720, 393, 300, 300, 300, 300, 300, 100, 300]
  Grazing_land_Rest_k = [0.00344, 0.1, 0.107, 0, 0, 0, 0, 0, 0.0131, 0]
  Grazing_land_Rest_x = [-418, -14, -0.127, 1, 1, 1, 1, 1, -96, 1]
  Urban_land_per_population = [0.25, 0.049, 0.036, 0.06, 0.03, 0.06, 0.07, 0.019, 0.06, 0.034]
  Nuclear_gen_cap_WO_EU_L = [117.5, 2.1, 75, 2, 10, 5, 100, 43, 99, 0]
  Nuclear_gen_cap_WO_EU_k = [0.1, 0.5, 0.3, 0.5, 0.5, 0.3, 0.06, 0.2, 0.1, 0.2]
  Nuclear_gen_cap_WO_EU_x0 = [32.5, 2, 14, 20, 5, 10, 30, 12, 1, 3.5]
  El_use_pp_WO_US_L = [8, 10, 10, 8, 8, 8, 12, 12, 8, 10]
  El_use_pp_WO_US_k = [0.055, 0.3, 0.3, 0.0939, 0.2541, 0.0939, 0.069, 0.075, 0.055, 0.1]
  El_use_pp_WO_US_x0 = [6.2, 13, 13, 22.6, 13.49, 22.6, 20.34, 26, 6.2, 28]
  Fossil_capacity_factor = [0.45, 0.4, 0.4, 0.4, 0.4, 0.3, 0.4, 0.5, 0.45, 0.4]
  Time_to_close_gap_in_fossil_el_cap = [15, 5, 6, 10, 5, 5, 5, 5, 10, 6]
  wind_and_PV_el_share_k = [0.128133, 0.5, 0.4, 0.135, 0.66707, 0.2, 0.15, 0.367, 0.158, 0.1]
  wind_and_PV_el_share_x0 = [76, 10, 17.5, 45, 7.48978, 24, 60, 32, 46, 35]
  Fraction_of_supply_imbalance_to_be_closed_by_yield_adjustment = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
  Nitrogen_use_rest_L = [108, 22.5, 50, 75, 50, 85, 100, 50, 130, 65]
  Nitrogen_use_rest_k = [0.04, 0.6, 0.1, 0.134, 0.1, 0.12, 0.066148, 0.09, 0.016, 0.9]
  Nitrogen_use_rest_x0 = [36.64, 4.4, 1, 10.46, 1, 12.3717, 30.348, 21, -34, 2.5]
  Capital_labour_ratio_in_1980 = [20000, 11000, 5000, 25000, 5000, 15000, 25000, 25000, 25000, 5000]
  RoC_Capital_labour_ratio_in_1980 = [0.025, 0.025, 0.05, 0.025, 0.02, 0.02, 0.02, 0.01, 0.025, 0.02]
  SoE_of_GDPpp_on_RoC_of_CLR = [0.05, 0.3, 0.3, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
  CH4_emi_from_agriculture_a = [3, 10.342, 3.12151, 0.8249, 10, 9.1509, -1.7, 8.6162, 5.3, 4.08118]
  CH4_emi_from_agriculture_b = [1.672, 0.605134, 14.4031, 1.75, 5, -1.6894, 9.06, -8.3246, -1.75, 8.71646]
  CH4_emi_from_energy_a = [1, 25, 9.7, 22.561, 3.2, 6.9187, 3.7161, 16, 1, 6]
  CH4_emi_from_energy_b = [1, 0.6, 0.756, 0.5886, -0.2, 0.7615, 0.0535, -0.7615, 1, 0.4]
  CH4_emi_from_waste_a = [-4.858, 1, 1, 3.672, 3, 7.082, -0.235, 1.53, -3.947, 7]
  CH4_emi_from_waste_b = [25.387, 1, 1, -4.58, 1, -11.039, 3.4589, 0.5983, 22.115, -6]
  N_excreted_a = [7.687, 2.3781, 0.6, 2.308, 5.3304, 6.2719, 9.943, 3.439, 124.64, 1.5105]
  N_excreted_b = [-1.031, -0.018, -0.016, -0.651, -0.506, -0.658, -1.146, -0.742, -1.624, -0.599]
  N2O_emi_from_agri_a = [0.0265, 0.036, 0.029, 0.037, 0.0159, 0.037, 0.0159, 0.0263, 0.03, 0.0228]
  N2O_emi_from_agri_b = [0.6528, 0.38, -0.09, -0.024, -0.0934, -0.024, 0.042, 0.2452, -0.024, 0.083]
  N2O_emi_X_agri_a = [0, 0.0252, 0.0671, 0.007, 0.05, 0.0048, -0.0009, 0.0012, 0, 0.009]
  N2O_emi_X_agri_b = [0.1, 0.0484, 0.0035, 0.043, 0, 0.0858, 0.2027, 0.1361, 0.1, 0.0309]
  Annual_pct_deforested = [0.1, 1, 0.3, 1, 0.5, 1, 0.1, 0.3, 0, 1]
  Slope_of_Corporate_borrowing_cost_eff_on_available_capital = [-0.1, 0, 0, 0, 0, -0.4, 0, -0.3, -0.1, 0]
  SWITCH_CBC_effect_on_available_capital = [1, 2, 2, 2, 2, 1, 2, 1, 1, 2]
  birth_rate_a = [0.0982, 0.205, 0.09, 0.232, 0.086, 1.87, 0.1317, 0.0418, 0.1214, 0.1174]
  birth_rate_b = [-0.472, -0.83, -0.01, -0.5599, -1.025, -1.92394, -0.459, -0.042, -0.414, -0.515]
  birth_rate_c = [0.015, 0.0025, 0.01, 0, 0.025, 0.025, 0, 0, 0, 0]
  Births_effect_from_cohorts_outside_15_to_45 = [1, 1.06, 0.97, 1.03, 0.83, 0.775, 0.93, 0.95, 1, 0.84]
  So_Eff_of_labour_imbalance_on_FOLP = [0.0002, 0.012, 0.005, 0.0003, 0.0005, 0.0018, 0.001, 0, 0.0003, 0.0005]
  Scaling_strength_of_RoC_from_unemployed_to_pool = [1, 0.95, 1, 1, 1, 1, 1, 1, 1, 1]
  SoE_of_PC_on_RoC_in_change_in_rate_of_tech_advance = [1, 6, 1, 1, 1, 1, 1, 1, 1, 1]
  SoE_of_tertiary_sector_on_RoC_in_TFP = [-0.06, -0.05, -0.05, -0.05, -0.05, -0.05, -0.06, -0.05, -0.05, -0.06]
#  Perceived_inflation_in_1980 = [0.15, 0.08, 0.08, 0.1, 0.18, 0.15, 0.1, 0.15, 0.15, 0.08]
  Inflation_target = [0.02, 0.05, 0.035, 0.035, 0.05, 0.05, 0.02, 0.03, 0.02, 0.025]
  SWITCH_unemp_target_or_long_term = [1, 1, 1, 2, 1, 2, 1, 1, 1, 2]
  Unemployment_target_for_interest = [0.05, 0.07, 0.07, 0.03, 0.07, 0.03, 0.03, 0.03, 0.05, 0.04]
  Indicated_crop_yield_rest_L = [6.24, 4.6, 15, 4.5, 10, 12, 5, 6, 12, 11]
  Indicated_crop_yield_rest_k = [0.0508, 0.3, 0.012, 0.15, 0.0198, 0.1, 0.027, 0.06, 0.085, 0.03171]
  Indicated_crop_yield_rest_x0 = [59.34, 6.2, 150, 32, 88, 30, 30, 30, 97, 1]
  dr0_a = [0.2044, 0.0968, 0.0239721, 0.0970563, 0.0463457, 0.760547, 0.172593, 0.0548485, 0.342607, 0.0581034]
  dr0_b = [-1.221, -1.119, -0.759395, -0.924117, -0.986135, -1.98658, -1.26419, -0.715971, -1.33556, -1.04907]
  dr35_a = [0.0053, 0.016668, 0.00267271, 0.0137294, 0.00510275, 0.0141353, 0.0164776, 0.00768488, 0.00967385, 0.00712475]
  dr35_b = [-0.292, -0.621721, -0.332791, -0.749027, -0.41194, -0.692944, -0.759418, -0.265449, -0.588911, -0.480438]
  dr40_a = [0.0128, 0.0180344, 0.00371472, 0.0156144, 0.00678361, 0.0202697, 0.0163656, 0.0131108, 0.0111224, 0.00827057]
  dr40_b = [-0.437, -0.559318, -0.319419, -0.688518, -0.407372, -0.735979, -0.640284, -0.351418, -0.504529, -0.400984]
  dr50_a = [0.0442, 0.022758, 0.00955783, 0.0277957, 0.0139832, 0.0330396, 0.0295831, 0.0403044, 0.0235237, 0.0138102]
  dr50_b = [-0.54, -0.413595, -0.360736, -0.547992, -0.343307, -0.650265, -0.570757, -0.515076, -0.46261, -0.283289]
  dr55_a = [0.0873, 0.0282151, 0.0148174, 0.034803, 0.0208927, 0.0467877, 0.0442172, 0.0414436, 0.0383174, 0.0195808]
  dr55_b = [-0.611, -0.363389, -0.331583, -0.487561, -0.330148, -0.636649, -0.556872, -0.382674, -0.481035, -0.257094]
  dr60_a = [0.2076, 0.0394868, 0.0247627, 0.0448349, 0.0345093, 0.0729714, 0.074377, 0.0499546, 0.0654207, 0.0325169]
  dr60_b = [-0.73, -0.320545, -0.280082, -0.393731, -0.37166, -0.651625, -0.575179, -0.322127, -0.512493, -0.301312]
  dr65_a = [0.3796, 0.0569518, 0.0376463, 0.0679361, 0.0504093, 0.106026, 0.12198, 0.0611206, 0.111736, 0.0550353]
  dr65_b = [-0.787, -0.277367, -0.218713, -0.374043, -0.332814, -0.638809, -0.591236, -0.269116, -0.542689, -0.340119]
  dr70_a = [0.572, 0.087954, 0.0667662, 0.103967, 0.0739432, 0.158873, 0.192363, 0.0884276, 0.191794, 0.0888564]
  dr70_b = [-0.785, -0.254721, -0.205684, -0.33058, -0.283363, -0.635569, -0.588862, -0.248511, -0.563631, -0.351908]
  dr75_a = [0.5533, 0.13508, 0.107517, 0.149683, 0.108474, 0.227804, 0.272054, 0.135544, 0.30471, 0.132639]
  dr75_b = [-0.664, -0.230475, -0.188994, -0.270794, -0.272187, -0.603628, -0.537849, -0.240646, -0.550445, -0.325219]
  dr80_a = [0.7722, 0.21254, 0.182508, 0.212282, 0.160006, 0.423807, 0.37234, 0.245588, 0.432721, 0.20363]
  dr80_b = [-0.621, -0.223126, -0.237083, -0.214784, -0.234113, -0.670318, -0.478028, -0.299529, -0.497531, -0.325019]
  mort_80_to_84_adjust_factor = [0.8, 1.3, 1, 1.2, 1.8, 1.4, 0.6, 0.7, 0.8, 1.8]
  dr85_a = [0.5184, 0.324963, 0.270235, 0.305642, 0.233244, 0.581153, 0.491005, 0.281373, 0.602357, 0.271059]
  dr85_b = [-0.389, -0.221219, -0.218259, -0.184128, -0.208412, -0.620289, -0.410508, -0.178954, -0.443274, -0.284262]
  mort_85_to_89_adjust_factor = [1.1, 1.7, 1.8, 1.5, 1.3, 1.4, 1, 1.4, 1.1, 1.3]
  dr90_a = [0.524, 0.456045, 0.383196, 0.42516, 0.324786, 0.687932, 0.593281, 0.380448, 0.678884, 0.346641]
  dr90_b = [-0.267, -0.200075, -0.220698, -0.166495, -0.173688, -0.535241, -0.325032, -0.144953, -0.334793, -0.261247]
  mort_90_to_94_adjust_factor = [1.2, 2.2, 1.6, 2.1, 1.7, 1.4, 1.2, 1.4, 1.2, 1.7]
  dr95p_a = [0.5031, 0.579391, 0.492643, 0.595128, 0.347011, 0.656443, 0.707515, 0.563918, 0.735896, 0.444143]
  dr95p_b = [-0.132, -0.194424, -0.179435, -0.167295, -0.186558, -0.3355, -0.234102, -0.157949, -0.220606, -0.236568]
  mort_95plus_adjust_factor = [2.2, 3.6, 2, 3.1, 2.6, 2.3, 1.9, 3.3, 2.2, 2.6]
  dr45_a = [0.0264, 0.0196008, 0.00538171, 0.0205822, 0.00936926, 0.0266287, 0.0207681, 0.0214813, 0.0152363, 0.0102799]
  dr45_b = [-0.518, -0.498066, -0.326391, -0.626545, -0.372203, -0.713779, -0.58857, -0.400453, -0.463706, -0.330488]
  Reference_fraction_of_supply_imbalance_to_be_closed_by_imports = [0, 0.3, 0.3, 0.75, 0.3, 0.75, 0.3, 0.75, 0, 0.3]
  Factor_to_account_for_net_migration_not_officially_recorded = [0.1, 14, -9, 0, -0.1, -0.1, 0.7, 0, 0, -2]
  LULUC_emissions_a = [0.1, 2, -0.3, 0, -4, -0.8, 0.5, 0.15, 0.3, -0.7]
  LULUC_emissions_b = [-0.65, 1.5, -0.75, 0, -0.4, 1.2, -1.8, -1.5, -0.4, -0.5]
  Slope_of_OSF_from_GDPpp_alone = [-0.06, -0.06, -0.06, -0.02, -0.02, -0.06, -0.06, -0.06, -0.02, -0.06]
  Strength_of_effect_of_industrial_sector_size_on_OSF = [1, 1.85, 1.5, 1, 1, 1, 1, 1, 1, 1]
  Inflation_perception_time = [1, 2, 2, 1, 1, 1, 1, 1, 1, 1]
  SoE_of_inventory_on_inflation_rate = [0.5, 3, 3, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 2]
  Minimum_relative_inventory_without_inflation = [0.94, 0.97, 0.99, 0.88, 0.9, 0.75, 0.95, 0.85, 0.92, 0.981]
  Migration_fraction_10_to_14_cohort = [0.4, 0.2, 0, 0.2, 0, 0, 0.2, 0, 0, 0.2]
  Migration_fraction_20_to_24_cohort = [0, 0.2, 0, 0.2, 0, 0, 0, 0, 0, 0.2]
  Migration_fraction_25_to_29_cohort = [0.3, 0.2, 0, 0.2, 0, 0, 0, 0, 0, 0.2]
  Migration_fraction_30_to_34_cohort = [0, 0.2, 0, 0.2, 0, 0, 0, 0, 0, 0.2]
  nmf_a = [0.4133, -0.3, -0.16, 0.0889, 2.78, 0.4073, 0.4322, 0.4812, 1.7649, -0.3]
  nmf_b = [-0.6174, 0.1, 0.0969, -0.1085, -1.716, -1.6676, -1.1157, -1.3905, -4.8616, 0.1]
  nmf_c = [0, 0, 0, 0, -1.58, 0, 0, 0, 0, 0]
#  Population_in_1979 = [230, 356, 1017, 179, 861, 355, 215, 326, 484, 356]
  Time_to_adjust_cultural_birth_rate_norm = [1, 10, 1, 5, 5, 3, 1, 2, 1, 2]
  Time_to_adjust_work_hours = [0.5, 0.25, 0.25, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.25]

  cereal_dmd_CN_a = 30.3753
  Switch_GDP_hist_1_mod_2 = 2
  UNIT_conv_Tera_to_Giga = 1000
  Kappa = 0.3
  Lambdav = 1 - Kappa
  Goal_for_relative_inventory = 1
  Hours_worked_index_in_1980 = 1
  UNIT_conv_to_k2017pppUSD_pr_py = 1
  UNIT_conv_to_make_exp_dmnl = 1
  cereal_dmd_CN_b = 121.165
  UNIT_conv_to_kg_crop_ppy = 1
  Round3_start = 2060
  Round2_start = 2040
  Policy_start_year = 2025
  SoE_of_social_trust_on_reform = 0.1
  Social_trust_in_1980 = 0.6
  Scaling_factor_for_amplitude_in_RoC_in_living_conditions_index = 20
  Strength_of_the_impact_of_social_tension_on_reform_willingness = 0.3
  Strength_of_inequality_effect_on_energy_TA = 2
  SDG4_a = 1.3463
  Delivery_delay_index_in_1980 = 1
# Owner_power_in_1980 = 0.5
  Worker_power_scaling_factor = 60
  Worker_power_scaling_factor_reference = 0.53
  SoE_of_unemployment_ratio_on_WSO = 0.01
  Societal_unemployment_rate_norm = 0.06
  Income_tax_rate_ie_fraction_owners_before_policies = 0.22
  Max_age = 100
  Years_between_60_and_max_age = 40
  UNIT_conv_to_kUSDpp = 1
  Income_tax_rate_ie_fraction_for_workers_before_policies = 0.3
  Worker_consumption_fraction = 0.85
  Consumption_tax_rate_ie_fraction = 0.03
  TOW_UNIT_conv_to_pa = 1
  Fossil_use_pp_NOT_for_El_gen_CN_a = 0
  Fossil_use_pp_NOT_for_El_gen_CN_b = 0.7
  UNIT_conv_to_toe_py = 1
  UNIT_conv_toe_to_Mtoe = 1
#  wind_and_PV_el_cap_in_1980 = 0.1
  wind_and_PV_capacity_factor = 0.1
  Hours_per_year = 8760
  UNIT_conv_GWh_and_TWh = 1 / 1000
  Actual_GH_share = 0
  kWh_per_kgH = 55
  UNIT_conv_to_TWh_per_Mth = 1
  TWh_per_MtH = kWh_per_kgH * UNIT_conv_to_TWh_per_Mth
  toe_per_tH = 0.338524
  Fraction_of_Fossil_fuel_for_NON_El_use_that_cannot_be_electrified = 0.05
  UNIT_conv_to_Gtoe = 1 / 1000
  CO2_emi_from_IPC_2_CN_L = 2
  CO2_emi_from_IPC_2_CN_k = 0.25
  CO2_emi_from_IPC_2_CN_x0 = 10
  Ctax_UNIT_conv_to_GtCO2_pr_yr = 1
  UNIT_conv_to_G2017pppUSD = 1
  Ref_Future_TLTL_leakage = 0.2
  Fraction_of_govt_income_transferred_to_workers_a = 0.45
  Fraction_of_govt_income_transferred_to_workers_b = -0.0424405
  Fraction_of_govt_income_transferred_to_workers_c = 1.62454
  One_year = 1
  Normal_Govt_payback_period_to_PL = 20
  Normal_basic_bank_margin = 0.02
  Long_term_risk_margin = 0.015
  Fraction_set_aside_to_service_loans = 0.9
  Fraction_of_avail_cash_used_to_meet_private_lender_obligations = 0.9
  UNIT_conv_to_pa = 1
  Normal_time_to_payback_public_debt = 30
  Govt_consumption_fraction = 0.3
  UNIT_conv_to_make_base_and_ln_dmnl = 1
  SDG4_b = 9.734
  Strength_of_FEHC_mult_on_years_of_schooling = 0.1
  SDG4_threshold_red = 13
  SDG4_threshold_green = 15
  SDG5_threshold_red = 0.4
  SDG5_threshold_green = 0.48
  Strength_of_Effect_of_empowerment_on_speed_of_food_TA = 0.1
  UNIT_conv_from_kg_to_Mt = 1e09
  UNIT_conv_btw_p_and_Mp = 1e06
#  Antarctic_ice_volume_in_1980 = 3e07
#  Arctic_ice_area_in_1980_km2 = 1.18874e07
#  C_in_atmosphere_in_1980 = 752.397
#  C_in_the_form_of_CH4_in_atm_1980 = 2.79426
  CC_in_cold_ocean_0_to_100m_in_1980 = 2325.64
  UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre = 1e06 / 12.01 * 1000
  Area_of_ocean_at_surface_361900_Gm2 = 361900
  Thickness_of_surface_water_box_100m = 100
  Fraction_of_ocean_classified_warm_surface = 0.8
  Fraction_of_ocean_classified_as_cold_surface = (
    1 - Fraction_of_ocean_classified_warm_surface
  )
  UNIT_conversion_to_Gm3 = 1
  Volume_cold_ocean_0_to_100m = (
    Area_of_ocean_at_surface_361900_Gm2
    * Thickness_of_surface_water_box_100m
    * Fraction_of_ocean_classified_as_cold_surface
    * UNIT_conversion_to_Gm3
  )
  Carbon_in_cold_ocean_0_to_100m_1850 = (
    CC_in_cold_ocean_0_to_100m_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
  ) * Volume_cold_ocean_0_to_100m
  CC_in_cold_ocean_downwelling_100m_bottom_in_1980 = 2253.86
  Thickness_of_intermediate_water_box_800m = 800
  Thickness_of_deep_water_box_1km_to_bottom = 2800
  Volume_cold_ocean_downwelling_100m_to_bottom = (
    Area_of_ocean_at_surface_361900_Gm2
    * (
      Thickness_of_intermediate_water_box_800m
      + Thickness_of_deep_water_box_1km_to_bottom
    )
    * Fraction_of_ocean_classified_as_cold_surface
    * UNIT_conversion_to_Gm3
  )
#  Carbon_in_cold_ocean_trunk_100m_to_bottom_1850 = (
#    CC_in_cold_ocean_downwelling_100m_bottom_in_1980
#    / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
#  ) * Volume_cold_ocean_downwelling_100m_to_bottom
  CC_ocean_deep_1km_to_bottom_in_1980 = 2232.12
  Volume_ocean_deep_1km_to_bottom = (
    Area_of_ocean_at_surface_361900_Gm2
    * Thickness_of_deep_water_box_1km_to_bottom
    * Fraction_of_ocean_classified_warm_surface
    * UNIT_conversion_to_Gm3
  )
#  Carbon_in_ocean_deep_1k_to_bottom_ocean_1850 = (
#    CC_ocean_deep_1km_to_bottom_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
#  ) * Volume_ocean_deep_1km_to_bottom
#  CC_in_ocean_upwelling_100m_to_1km_in_1980 = 2237.8
  Volume_ocean_upwelling_100m_to_1km = (
    Area_of_ocean_at_surface_361900_Gm2
    * Thickness_of_intermediate_water_box_800m
    * Fraction_of_ocean_classified_warm_surface
    * UNIT_conversion_to_Gm3
  )
#  Carbon_in_ocean_upwelling_100m_to_1km_1850 = (
#    CC_in_ocean_upwelling_100m_to_1km_in_1980
#    / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
#  ) * Volume_ocean_upwelling_100m_to_1km
#  C_in_sediment_initially = 3e09
  CC_in_warm_ocean_0_to_100m_in_1980 = 2242.96
  Volume_warm_ocean_0_to_100m = (
    Area_of_ocean_at_surface_361900_Gm2
    * Thickness_of_surface_water_box_100m
    * Fraction_of_ocean_classified_warm_surface
    * UNIT_conversion_to_Gm3
  )
  Carbon_in_warm_ocean_0_to_100m_1850 = (
    CC_in_warm_ocean_0_to_100m_in_1980 / UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
  ) * Volume_warm_ocean_0_to_100m
  Lifetime_of_capacity_in_1980 = 15
  Capacity_construction_time = 1.5
  Normal_bank_operating_margin = 0.015
  Normal_corporate_credit_risk_margin = 0.02
#  Cumulative_N_use_since_2020_in_1980 = 0
  Normal_k = 0.3
  JR_sINEeolLOK_lt_0 = -0.45
  Strength_of_inequality_proxy = 6
  UNIT_conv_to_dmnl = 1
  Fossil_fuel_reserves_in_ground_at_initial_time_GtC = 5827.98
#  Glacial_ice_volume_in_1980 = 165694
#  GRASS_area_burned_in_1980 = 1.741
#  GRASS_area_harvested_in_1980 = 2.15683
#  GRASS_Biomass_locked_in_construction_material_in_1980 = 1.99186
#  GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 1086.88
#  GRASS_area_deforested_in_1980 = 1.22174
#  GRASS_Living_biomass_in_1980 = 381.43
  Greenland_ice_volume_in_1980 = 2.85e06
#  Heat_in_atmosphere_in_1980 = 1030.43
#  Heat_in_ocean_deep_in_1980 = 1.95347e06
#  Heat_in_surface_in_1980 = 25034.6
  Incoming_solar_in_1850_ZJ_py = 5470.69
  Evaporation_as_fraction_of_incoming_solar_in_1850 = 0.289
  Sensitivity_of_evaporation_to_temp = 0.36
  Temp_surface_1850 = 286.815
  Heat_in_surface_in_1850_ZJ = 25000
  Conversion_heat_surface_to_temp = Temp_surface_1850 / Heat_in_surface_in_1850_ZJ
  Reference_temp_C = 10
  Water_content_of_evaporation_g_p_kg_per_ZJ_py = 0.001253
  Goal_for_inventory_coverage = 0.4
  Emissivity_atm = 1
  Stephan_Boltzmann_constant = 5.67037e-08
  Temp_atm_1850 = 274.31
  Heat_in_atmosphere_in_1850_ZJ = 1025.67
  Conversion_heat_atm_to_temp = Temp_atm_1850 / Heat_in_atmosphere_in_1850_ZJ
  Seconds_per_yr = 60 * 60 * 24 * 365
  Area_of_earth_m2 = 5.1e14
  UNIT_conversion_W_to_ZJ_p_sec = 1
  Zetta = 1e21
  UNIT_conversion_W_p_m2_earth_to_ZJ_py = (
    (Seconds_per_yr * Area_of_earth_m2) * UNIT_conversion_W_to_ZJ_p_sec / Zetta
  )
  Emissivity_surface = 1
  Frac_of_surface_emission_through_atm_window = 0.051
  C_in_atmosphere_in_1850_GtC = 600
  CO2_concentration_ppm_in_1850 = 284.725
  Conversion_constant_GtC_to_ppm = (
    C_in_atmosphere_in_1850_GtC / CO2_concentration_ppm_in_1850
  )
  conversion_factor_CH4_Gt_to_ppb = 468
  LW_radiation_fraction_blocked_by_other_GHG_in_1850 = 0.0398
  Slope_btw_Kyoto_Fluor_ppt_and_blocking_multiplier = 0.3
  Conversion_from_Kyoto_Fluor_amount_to_concentration_ppt_p_kt = 0.04
  Kyoto_Fluor_concentration_in_1970_ppt = 9.32074
  Slope_btw_Montreal_gases_ppt_and_blocking_multiplier = 0.3
  Conversion_from_Montreal_gases_amount_to_concentration_ppt_p_kt = 0.04
  Montreal_gases_concentration_in_1970_ppt = 262.353
  Slope_btw_N2O_ppb_and_blocking_multiplier = 0.1
#  N2O_in_atmosphere_MtN2O_in_1980 = 1082.4
  UNIT_Conversion_from_N2O_amount_to_concentration_ppb_p_MtN2O = 0.305
  Model_N2O_concentration_in_1850_ppb = 274.5
  LW_LO_cloud_radiation_reference_in_1980 = 20
  Area_covered_by_low_clouds_in_1980 = 0.431994
  Sensitivity_of_low_cloud_coverage_to_temp = 58
  LW_HI_cloud_radiation_reference_in_1980 = 7.9
  Area_covered_by_high_clouds_in_1980 = 0.214448
  Sensitivity_of_high_cloud_coverage_to_temp_normal = 50
  Logistics_curve_param_c = 20
  Logistics_curve_param_k = 0.1
  Logistics_curve_param_shift = 2000
#  NF_area_burned_in_1980 = 2.09605
#  NF_area_clear_cut_in_1980 = 3.99473
#  NF_area_deforested_in_1980 = 0.129448
#  NF_area_harvested_in_1980 = 0.897719
#  NF_Biomass_locked_in_construction_material_in_1980 = 16.8741
#  NF_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 304.415
#  NF_Living_biomass_in_1980 = 150.39
#  People_considering_entering_the_pool_in_1980 = 2
#  People_considering_leaving_the_pool_in_1980 = 2
#  Size_of_public_capacity_in_1980 = 0.2
  Size_of_agri_sector_a = 1
  Size_of_agri_sector_b = 37
  Size_of_agri_sector_c = 5
  Size_of_tertiary_sector_lim = 80
  Size_of_tertiary_sector_a = 40
  Size_of_tertiary_sector_c = 20
#  TFP_in_1980 = 1
#  TROP_area_burned_in_1980 = 1.64305
#  TROP_area_clear_cut_in_1980 = 0.467813
#  TROP_area_deforested_in_1980 = 5.97649
#  TROP_area_harvested_in_1980 = 0.24296
#  TROP_Biomass_locked_in_construction_material_in_1980 = 44.963
#  TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 158.789
#  TROP_Living_biomass_in_1980 = 379.797
#  TUNDRA_area_burned_in_1980 = 1.8566
#  TUNDRA_area_harvested_in_1980 = 2.5
#  TUNDRA_Biomass_locked_in_construction_material_in_1980 = 1.92761
#  TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 = 1207.56
#  TUNDRA_area_deforested_in_1980 = 0
#  TUNDRA_Living_biomass_in_1980 = 391.84
#  Wetlands_area_in_1980 = 1e07
#  Worker_resistance_initially = 1 - Owner_power_in_1980
  Access_to_electricity_L = 0.999
  Access_to_electricity_k = 0.5
  UNIT_conv_to_make_base_dmnless = 1
  Access_to_electricity_x0 = 3
  Access_to_electricity_min = -0.01
  red_meat_dmd_PA_a = 11.878
  red_meat_dmd_PA_b = 0.0945
  red_meat_dmd_SA_a = 1.49475
  red_meat_dmd_SA_b = -0.6628
  red_meat_dmd_SA_c = 2.5
  UNIT_conv_to_kg_red_meat_ppy = 1
  UNIT_conv_kgrmeat_and_Mtrmea = 1e09
  UNIT_conv_red_meat = 1
  white_meat_dmd_CN_a = 19.1013
  white_meat_dmd_CN_b = 2.61946
  UNIT_conv_to_kg_white_meat_ppy = 1
  UNIT_conv_kgwmeat_and_Mtwmeat = 1e09
  UNIT_conv_white_meat = 1
  UNIT_conv_meat_to_feed = 1
#  Reference_crop_import_in_1980 = 0
  Soil_quality_in_1980 = 1
  Soil_quality_of_regenerative_cropland = 1.2
  SoE_of_CO2_on_yield = 0.2
  CO2_concentration_2020 = 426
  Temp_surface_1850_less_zero_k = Temp_surface_1850 - 273.15
  Pressure_adjustment_surface_pct = 0.2
  UNIT_conversion_Gm3_to_km3 = 1
  Ocean_surface_area_km2 = 0.3619 * 1e09
  UNIT_Conversion_from_km3_to_km2 = 1
  Temp_ocean_deep_in_1850_C = 4
  Temp_ocean_deep_in_1850_in_K = Temp_ocean_deep_in_1850_C + 273.15
  Heat_in_ocean_deep_in_1850_ZJ = 1.9532e06
  Conversion_constant_heat_ocean_deep_to_temp = (
    Temp_ocean_deep_in_1850_in_K / Heat_in_ocean_deep_in_1850_ZJ
  )
  Pressure_adjustment_deep_pct = 1
  UNIT_conversion_from_km_to_m = 1000
  Avg_flatness_of_worlds_coastline = 0.65
  sea_level_rise_2020 = 0.269
  temp_in_2020 = 1.07
  expSoE_of_ed_on_agri_yield = 0.1
  SoE_of_relative_wealth_on_env_damage = 0.01
  Time_for_abandoned_agri_land_to_become_forest = 300
  Grazing_land_EC_a = 529.5
  UNIT_conv_meat_to_dmnl = 1
  Grazing_land_EC_b = -0.031
  Grazing_land_LA_L = 418.8
  Grazing_land_LA_k = 0.17169
  Grazing_land_LA_x = 0.3264
  Grazing_land_LA_L2 = -170
  Grazing_land_LA_k2 = -0.0313754
  Grazing_land_LA_x2 = 49.3867
  Grazing_land_ME_L = 320
  Grazing_land_ME_k = 0.309
  Grazing_land_ME_x = -1.27
  Grazing_land_ME_min = 0
  Grazing_land_PA_L = 271
  Grazing_land_PA_k = -0.42
  Grazing_land_PA_x = 16.11
  Grazing_land_PA_min = 250
  Grazing_land_SA_a = 23.72
  Grazing_land_SA_b = -0.109
  Grazing_land_SE_a = 0.48
  Grazing_land_SE_b = 14.721
  UNIT_conv_to_Mha = 1
  Fraction_of_grazing_land_gap_closed_from_acgl = 1
  Fraction_of_abandoned_agri_land_developed_for_urban_land = 0.03
  pb_Ocean_acidification_green_threshold = 8.15
  UNIT_conversion_C_to_pH = 1
  UNIT_conversion_km3_to_Gm3 = 1
  Volume_of_total_ocean_Gm3 = (
    Volume_cold_ocean_0_to_100m
    + Volume_cold_ocean_downwelling_100m_to_bottom
    + Volume_ocean_deep_1km_to_bottom
    + Volume_ocean_upwelling_100m_to_1km
    + Volume_warm_ocean_0_to_100m
  )
  Frac_vol_warm_ocean_0_to_100m_of_total = (
    Volume_warm_ocean_0_to_100m / Volume_of_total_ocean_Gm3
  )
  UNIT_conversion_ymoles_p_litre_to_dless = 1
  Frac_vol_cold_ocean_0_to_100m_of_total = (
    Volume_cold_ocean_0_to_100m / Volume_of_total_ocean_Gm3
  )
  UNIT_conv_to_GtCO2_pr_yr = 1
  Nuclear_gen_cap_EU_s = 25
  Nuclear_gen_cap_EU_g = 100
  Nuclear_gen_cap_EU_h = 31
  Nuclear_gen_cap_EU_k = 16
  UNIT_conv_to_GW = 1
  Nuclear_capacity_factor = 0.91
  UNIT_conv_to_kWh_ppp = 1
  Inequality_considered_normal_in_1980 = 1.1
  GRASS_Ref_historical_deforestation_pct_py = 0.1
  GRASS_historical_deforestation_pct_py = (
    GRASS_Ref_historical_deforestation_pct_py / 100
  )
  Fraction_GRASS_being_deforested_1_py = GRASS_historical_deforestation_pct_py
  GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
  GRASS_Living_biomass_in_1850 = 310
  Use_of_GRASS_biomass_for_energy_in_1850_pct = 1
  Use_of_GRASS_for_energy_in_2000_GtBiomass = (
    GRASS_Living_biomass_in_1850 * Use_of_GRASS_biomass_for_energy_in_1850_pct / 100
  )
  UNIT_conv_to_Bp = 1000
  Population_2000_bn = 6.187
  UNIT_conversion_1_py = 1
  GRASS_living_biomass_densitiy_in_1850_tBiomass_pr_km2 = 14500
  Sensitivity_of_biomass_new_growth_to_CO2_concentration = 1.5
  Slope_of_temp_eff_on_potential_biomass_per_km2 = -0.5
  UNIT_conversion_GtBiomass_py_to_Mkm2_py = 1000
  GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
  GRASS_runoff_time = 2000
  Slope_temp_eff_on_fire_incidence = 0.1
  GRASS_Normal_fire_incidence_fraction_py = 1
  GRASS_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
  GRASS_Time_to_decompose_undisturbed_dead_biomass_yr = 1000
  NF_Ref_historical_deforestation_pct_py = 0.02
  NF_historical_deforestation_pct_py = NF_Ref_historical_deforestation_pct_py / 100
  NF_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
  NF_DeadB_and_SOM_densitiy_in_1850 = 27500
  NF_Living_biomass_in_1850 = 115
  Use_of_NF_biomass_for_energy_in_1850_pct = 1.09
  Use_of_NF_for_energy_in_2000_GtBiomass = (
    NF_Living_biomass_in_1850 * Use_of_NF_biomass_for_energy_in_1850_pct / 100
  )
  NF_living_biomass_densitiy_in_1850_tBiomass_pr_km2 = 7500
  Switch_to_run_POLICY_4_Stopping_logging_in_Northern_forests_0_off_1_on = 0
  NF_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
  NF_runoff_time = 2000
  NF_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting = 0.5
  NF_Normal_fire_incidence_fraction_py = 0.7
  NF_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
  NF_Time_to_decompose_undisturbed_dead_biomass_yr = 250
  TROP_Ref_historical_deforestation = 1
  Time_at_which_human_deforestation_is_stopped = 3000
  TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
  TROP_DeadB_and_SOM_densitiy_in_1850_tBiomass_pr_km2 = 8500
  TROP_Living_biomass_in_1850 = 370
  Use_of_TROP_biomass_for_energy_in_1850_pct = 0.07
  Use_of_TROP_for_energy_in_2000_GtBiomass = (
    TROP_Living_biomass_in_1850 * Use_of_TROP_biomass_for_energy_in_1850_pct / 100
  )
  UNIT_conversion_to_yr = 1
  TROP_living_biomass_densitiy_in_1850_tBiomass_pr_km2 = 16500
  TROP_clear_cut_fraction = 0.5
  TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
  TROP_runoff_time = 2000
  TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting = 0.5
  TROP_Normal_fire_incidence = 0.3
  TROP_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
  TROP_Time_to_decompose_undisturbed_dead_biomass_yr = 24
  SoE_of_env_damage_indicator = -0.4
  El_use_pp_US_s = 9.3
  El_use_pp_US_g = 5
  El_use_pp_US_h = 55
  El_use_pp_US_k = 18
  UNIT_conv_to_MWh_ppy = 1
  UNIT_conv_to_TWh = 1
  Life_of_fossil_el_gen_cap = 40
  wind_and_PV_construction_time = 1.5
  Lifetime_of_wind_and_PV_el_cap = 40
  Nitrogen_use_AF_L = 22.5
  Nitrogen_use_AF_k = 0.62
  UNIT_conv_to_make_N_use_dmnl = 1
  Nitrogen_use_AF_x0 = 4.4
  Nitrogen_use_CN_b = 164
  Nitrogen_use_CN_a = 200
  Nitrogen_use_SA_a = 65.3
  Nitrogen_use_SA_b = 25
  Fraction_of_N_use_saved_through_regenerative_practice = 0.9
  UNIT_conv_kgN_to_Nt = 1 / 1000
  Slope_of_Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio = 2
  UNIT_conv_to_Mp = 1000
  Addl_time_to_shift_govt_expenditure = 3
  Value_of_anthropogenic_aerosol_emissions_during_2015 = 0.225
  Cohort_duration_is_5_yrs = 5
#  Urban_aerosol_concentration_in_2020 = 43.5
  pb_Urban_aerosol_concentration_green_threshold = 20
  Albedo_Antarctic_hist = 0.7
  Albedo_Antarctic_sens = 0.7
  Albedo_BARREN_normal = 0.17
  Albedo_DESERT_normal = 0.24
  Albedo_glacier_sens = 0.4
  Albedo_glacier_hist = 0.4
  Albedo_GRASS_burnt = 0.08
  Albedo_GRASS_deforested = 0.3
  Albedo_GRASS_normal_cover = 0.16
  Albedo_Greenland = 0.7
  UNIT_conversion_m2_to_Mkm2 = 1e12
  Area_of_earth_Mkm2 = Area_of_earth_m2 / UNIT_conversion_m2_to_Mkm2
  Fraction_of_earth_surface_as_ocean = 0.7
  Urban_area_fraction_2000 = 0.004
  Avg_thickness_Antarctic_sens_km = 2.14
  Avg_thickness_Antarctic_hist_km = 2.14
  Avg_thickness_glacier_km = 0.23
  UNIT_conversion_km3_div_km_to_km2 = 1
  Avg_thickness_Greenland_km = 1.35
  UNIT_conversion_km2_to_Mkm2 = 1 / 1e06
  Area_of_land_Mkm2 = Area_of_earth_Mkm2 * (1 - Fraction_of_earth_surface_as_ocean)
  Conversion_Million_km2_to_km2 = 1e-06
  Albedo_NF_normal_cover = 0.08
  Albedo_NF_burnt = 0.13
  Albedo_NF_deforested = 0.18
  Albedo_TROP_normal_cover = 0.14
  Albedo_TROP_burnt = 0.1
  Albedo_TROP_deforested = 0.168
  Albedo_TUNDRA_normal_cover = 0.23
  Albedo_TUNDRA_burnt = 0.23
  Albedo_TUNDRA_deforested = 0.23
  Albedo_URBAN_normal = 0.15
  Albedo_URBAN = Albedo_URBAN_normal
  Arctic_ice_albedo_1850 = 0.7
  Ocean_area_km2 = 5.1e08 * 0.7
  Open_ocean_albedo = 0.065
  Solar_sine_forcing_offset_yr = -7
  Solar_sine_forcing_period_yr = 11
  Solar_sine_forcing_amplitude = 0.085
  Solar_sine_forcing_lift = 0.06
  Frac_SW_HI_cloud_efffect_aka_cloud_albedo = 0.006
  Frac_SW_LO_cloud_efffect_aka_cloud_albedo = 0.158
  UNIT_conv_kgac_to_kg = 1
  SWITCH_choose_4_for_e4a_or_2_for_ssp245 = 4
  UNIT_conv_CO2_to_C = 3.667
  UNIT_conversion_for_CO2_from_CO2e_to_C = 12 / 44
  UNIT_conversion_from_MtCH4_to_GtC = 1 / (1000 / 12 * 16)
  UNIT_conv_Mtrmeat = 1
  CH4_emi_from_energy_EU_a = 14
  CH4_emi_from_energy_EU_b = -0.036
  CH4_emi_from_energy_US_a = 18
  CH4_emi_from_energy_US_b = -0.008
  CH4_emi_from_energy_EC_a = 11.39
  UNIT_conv_to_make_fossil_fuels_dmnl = 1000
  CH4_emi_from_energy_EC_b = 18.271
  CH4_emi_from_waste_AF_a = 1.2596
  CH4_emi_from_waste_AF_b = 0.9904
  CH4_emi_from_waste_CN_a = 7.09
  CH4_emi_from_waste_CN_b = -0.071
  Global_Warming_Potential_CH4 = 25
  UNIT_conversion_for_CH4_from_CO2e_to_C = 1 / (16 / 12 * Global_Warming_Potential_CH4)
  N2O_emi_from_agri_AF_a = 0.5301
  UNIT_conv_to_MtN = 1 / 1000
  UNIT_conv_to_dmnl_for_MtNmeat = 1
  UNIT_conv_to_MtN_from_meat = 1
  UNIT_conv_to_make_LN_dmnl = 1
  N2O_emi_from_agri_AF_b = -0.579
  N2O_emi_X_agri_US_a = 0.9042
  N2O_emi_X_agri_US_b = -0.012
  N2O_emi_X_agri_EU_a = 1.8178
  N2O_emi_X_agri_EU_b = -0.047
  N2O_emi_X_agri_CN_a = 0.4272
  N2O_emi_X_agri_CN_b = -0.2683
  N2O_emi_X_agri_SA_a = 0.1257
  N2O_emi_X_agri_SA_b = 0.0234
  Global_Warming_Potential_N20 = 298
  UNIT_conversion_Gt_to_Mt = 1000
  Kyoto_Fluor_Global_Warming_Potential = 7000
  UNIT_conversion_Gt_to_kt = 1e06
  Montreal_Global_Warming_Potential = 10000
  N2O_natural_emissions = 9
  All_region_max_cost_estimate_empowerment_PES = 1000
  All_region_max_cost_estimate_energy_PES = 1000
  All_region_max_cost_estimate_food_PES = 1000
  All_region_max_cost_estimate_inequality_PES = 4000
  All_region_max_cost_estimate_poverty_PES = 1000
  SDG1_threshold_red = 0.13
  SDG1_threshold_green = 0.05
  SDG2_a = 0.42
  SDG2_b = -0.747
  SDG2_threshold_red = 0.07
  SDG2_threshold_green = 0.03
  Weight_disposable_income = 1
  Disposable_income_threshold_for_wellbeing = 8
  Weight_el_use = 1
  El_use_wellbeing_a = 4
  El_use_wellbeing_b = 1
  Basic_el_use = 2
  Weight_food = 1
  stdev = 0.4
  UNIT_conv_kgwmeat_to_kg = 1
  Healthy_white_meat_consumption = 30
  mean_value = 1
  Weight_on_white_meat = 0.5
  UNIT_conv_kgrmeat_to_kg = 1
  Healthy_red_meat_consumption = 30
  Weight_on_red_meat = 0.25
  Healthy_all_crop_consumption = 800
  Weight_on_crops = 1
  Sum_of_food_weights = Weight_on_crops + Weight_on_red_meat + Weight_on_white_meat
  Weight_inequality = 0.1
  Weight_population_in_job_market = 1
  Slope_of_wellbeing_from_fraction_of_people_outside_of_labor_pool = 3
  Weight_public_spending = 1
  UNIT_conv_to_k217pppUSD_ppy = 1
  Satisfactory_public_spending = 0.22
  Sum_weights_living_conditions = (Weight_disposable_income + Weight_el_use    + Weight_food    + Weight_inequality    + Weight_population_in_job_market    + Weight_public_spending)
  Weight_on_living_conditions = 0.65
  Weight_on_env_conditions = 1 - Weight_on_living_conditions
  Weight_on_physical_conditions = 0.75
  SoE_of_Wellbeing_from_social_tension = -2
  Social_tension_index_in_1980 = 1
  SDG3_threshold_red = 1.2
  SDG3_threshold_green = 1.4
  Safe_water_cn_L = 0.999
  Safe_water_cn_k = 1
  Safe_water_cn_x0 = 0
  Safe_water_cn_min = -0.02
  Safe_water_rest_L = 0.999
  Safe_water_rest_k = 0.2
  Safe_water_rest_x0 = 10
  Safe_water_rest_min = -0.02
  SDG6a_threshold_red = 0.8
  SDG6a_threshold_green = 0.95
  Safe_sanitation_L = 0.999
  Safe_sanitation_k = 0.15
  Safe_sanitation_x0 = 12
  Safe_sanitation_min = -0.02
  SDG6b_threshold_red = 0.65
  SDG6b_threshold_green = 0.9
  SDG_7_threshold_red = 0.9
  SDG_7_threshold_green = 0.98
  Normal_consumer_credit_risk_margin = 0
  Worker_drawdown_period = 5
  Fraction_by_law_or_custom_left_for_surviving = 0.5
  Workers_payback_period = 3
  SDG_8_threshold_red = 15
  SDG_8_threshold_green = 25
  UNIT_conv_to_tCO2_pr_USD = 1000
  SDG_9_threshold_green = 0
  SDG_9_threshold_red = 0.1
  SDG_10_threshold_green = 0.6
  SDG_10_threshold_red = 0.4
  UNIT_conv_to_t_ppy = 1000
  SDG_11_threshold_green = 0
  SDG_11_threshold_red = 2
  UNIT_conv_to_kgN = 1000
  SDG12_global_green_threshold = 62
  SDG12_global_red_threshold = 82
  SDG_13_threshold_green = 1
  SDG_13_threshold_red = 1.5
  SDG_14_threshold_green = 8.15
  SDG_14_threshold_red = 8.1
  SDG_15_threshold_green = 25
  SDG_15_threshold_red = 15
  SDG_16_threshold_green = 15
  SDG_16_threshold_red = 5
  SDG_17_threshold_green = 1
  SDG_17_threshold_red = 0.75
  GRASS_Speed_of_regrowth_yr = 2
  Carbon_per_biomass = 0.5
  NF_Speed_of_regrowth_yr = 3
  TROP_Speed_of_regrowth_yr = 3
  TUNDRA_living_biomass_densitiy_at_initial_time_tBiomass_pr_km2 = 14500
  TUNDRA_Speed_of_regrowth_yr = 3
  GRASS_Avg_life_of_building_yr = 10
  GRASS_Fraction_of_construction_waste_burned_0_to_1 = 0.5
  NF_Avg_life_of_building_yr = 20
  NF_Fraction_of_construction_waste_burned_0_to_1 = 0.5
  TROP_Avg_life_of_building_yr = 20
  TROP_Fraction_of_construction_waste_burned_0_to_1 = 0.5
  TUNDRA_Avg_life_of_building_yr = 10
  TUNDRA_Fraction_of_construction_waste_burned_0_to_1 = 0.5
  TUNDRA_Time_to_decompose_undisturbed_dead_biomass_yr = 1000
  TUNDRA_Ref_historical_deforestation_pct_py = 0
  TUNDRA_historical_deforestation_pct_py = (
    TUNDRA_Ref_historical_deforestation_pct_py / 100
  )
  Fraction_TUNDRA_being_deforested_1_py = TUNDRA_historical_deforestation_pct_py
  TUNDRA_Normal_fire_incidence_fraction_py = 1
  TUNDRA_Living_biomass_in_1850 = 300
  Use_of_TUNDRA_biomass_for_energy_in_1850_pct = 1
  Use_of_TUNDRA_for_energy_in_2000_GtBiomass = (
    TUNDRA_Living_biomass_in_1850 * Use_of_TUNDRA_biomass_for_energy_in_1850_pct / 100
  )
  TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting = 1
  TUNDRA_DeadB_and_SOM_densitiy_at_initial_time_tBiomass_pr_km2 = 65000
  TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting = 0.1
  TUNDRA_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires = 0
  TUNDRA_runoff_time = 2000
  Time_to_melt_or_freeze_glacial_ice_at_the_reference_delta_temp = 500
  Effective_time_to_melt_glacial_ice_at_the_reference_delta_temp = (
    Time_to_melt_or_freeze_glacial_ice_at_the_reference_delta_temp
  )
  Slope_temp_vs_glacial_ice_melting = 1
  SCALE_converter_zero_C_to_K = 273.15
  UNIT_conversion_Celsius_to_Kelvin_C_p_K = 1
  Ref_temp_difference_for_glacial_ice_melting_1_degC = 3
  GtIce_vs_km3 = 0.9167
  Annual_reduction_in_UAC_TLTL = 0.2
  UNIT_conv_to_1_per_yr = 1
  Time_at_which_govt_public_debt_is_cancelled = 2025
  Public_Govt_debt_cancelling_spread = 2
  Nbr_of_policies = 30
  Annual_reduction_in_UAC_GL = 2
  Switch_btw_historical_CO2_CH4_emissions_or_constant_1_history_0_constant = 1
  Melting_of_permafrost_at_all_depths_at_4_deg_C_temp_diff_km_py = 0.71
  Area_equivalent_of_1km_linear_retreat_km2 = 17500
  UNIT_conversion_to_km2_py = 1
  Area_equivalent_of_linear_retreat_km2_py = (
    Melting_of_permafrost_at_all_depths_at_4_deg_C_temp_diff_km_py
    * Area_equivalent_of_1km_linear_retreat_km2
    * UNIT_conversion_to_km2_py
  )
  Avg_amount_of_C_in_the_form_of_CH4_per_km2 = 4.8e-05
  Slope_btw_temp_and_permafrost_melting_or_freezing_base = 1
  Slope_btw_temp_and_permafrost_melting_or_freezing_sensitivity = 1
  Ref_temp_difference_4_degC = 4
  Avg_depth_of_permafrost_km = 0.1
  Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3 = 0.0001717
  Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl = 0.125
  Slope_of_Worker_share_of_output_with_unemployment_effect_on_available_capital = -2.9
  Slope_of_Eff_of_dmd_imbalance_on_flow_of_available_capital = 1
  Dmd_imbalance_in_1980 = 1
  Foreign_capital_inflow = 0
  Time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp = 18000
  Effective_time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp = (
    Time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp
  )
  Slope_temp_vs_antarctic_ice_melting = 1.2
  Ref_temp_difference_for_antarctic_ice_melting_3_degC = 3
  Land_area_km2 = 5.1e08 * 0.3
#  Atmos_heat_used_for_melting_Initially_1_py = 0
#  Ocean_heat_used_for_melting_Initially_1_py = 0
  UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py = 1e-06
  Densitiy_of_water_relative_to_ice = 0.916
  Human_aerosol_forcing_1_is_ON_0_is_OFF = 1
  Conversion_of_anthro_aerosol_emissions_to_forcing = -1.325
  Time_for_abandoned_urban_land_to_become_fallow = 100
  Time_to_develop_urban_land_from_abandoned_land = 2
  UNIT_conversion_m2_to_km2 = 1e06
  Arctic_ice_area_max_km2 = Area_of_earth_m2 / UNIT_conversion_m2_to_km2 - Land_area_km2
  Time_to_melt_Arctic_ice_at_the_reference_delta_temp = 500
  Effective_time_to_melt_Arctic_ice_at_the_reference_delta_temp = (
    Time_to_melt_Arctic_ice_at_the_reference_delta_temp
  )
  Slope_temp_vs_Arctic_ice_melting = 0.65
  Ref_temp_difference_for_Arctic_ice_melting = 0.4
  Arctic_surface_temp_delay_yr = 15
  Heat_needed_to_melt_1_km3_of_ice_ZJ = 0.0003327
  UNIT_conversion_1_p_km3 = 1
  UNIT_conversion_GtIce_to_ZJ_melting = 1
  Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air = 0.6
  Time_to_melt_greenland_ice_at_the_reference_delta_temp = 4000
  Effective_time_to_melt_greenland_ice_at_the_reference_delta_temp = (
    Time_to_melt_greenland_ice_at_the_reference_delta_temp
  )
  Slope_temp_vs_greenland_ice_melting = 0.1
  Ref_temp_difference_for_greenland_ice_melting_C = 1
  Time_to_melt_greenland_ice_that_slid_into_the_ocean_at_the_reference_delta_temp = 20
  Slope_temp_vs_greenland_ice_that_slid_into_the_ocean_melting = 0.71
  Ref_temp_difference_for_greenland_ice_that_slid_into_the_ocean_melting_degC = 1
  Fraction_of_heat_needed_to_melt_Greenland_ice_that_slid_into_the_ocean_coming_from_air = 0.1
  Average_thickness_arctic_ice_km = 0.0025
  UNIT_conversion_km2_times_km_to_km3 = 1
  Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air = 0.5
  UNIT_conv_to_y = 1
  Conversion_ymoles_per_kg_to_pCO2_yatm = 0.127044
  Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions = -1
  Future_volcanic_eruptions_1_is_ON_0_is_OFF = 0
  NEvt_2a_Volcanic_eruptions_in_the_future_VAEs_first_future_pulse = 2025
  VAES_pulse_duration = 4
  VAES_puls_repetition = 30
  VAES_pulse_height = 1
  Conversion_of_volcanic_aerosol_emissions_to_CO2_emissions_GtC_pr_VAE = 2.8
  Biocapacity_reference = 1.2e07
  UNIT_conv_to_Mha_footprint = 1000
  pb_Biodiversity_loss_green_threshold = 0.4
  Net_marine_primary_production_in_1850 = 0.4
  Carbon_in_top_ocean_layer_1850 = (
    Carbon_in_cold_ocean_0_to_100m_1850 + Carbon_in_warm_ocean_0_to_100m_1850
  )
  Concentration_of_C_in_ocean_top_layer_in_1850 = Carbon_in_top_ocean_layer_1850 / (
    Volume_cold_ocean_0_to_100m + Volume_warm_ocean_0_to_100m
  )
  Slope_of_efffect_of_acidification_on_NMPP = 5
  Frac_vol_cold_ocean_downwelling_of_total = (
    Volume_cold_ocean_downwelling_100m_to_bottom / Volume_of_total_ocean_Gm3
  )
  ph_in_cold_water_in_1980 = 8.30948
  Slope_Effect_Temp_on_NMPP = 2
  birth_rate_a_CN = 0.0262464
  birth_rate_b_CN = 0.00216569
  birth_rate_c_CN = -0.190456
  birth_rate_d_CN = -0.95
  UNIT_conv_to_make_the_bell_shaped_birth_rate_formula_have_units_of_1_pr_y = 1
  expSoE_of_ed_on_cost_of_TAs = 0.075
  Fraction_of_budget_available_for_policies = 0.5
  Time_to_reach_C_equilibrium_between_atmosphere_and_ocean = 90
  Ocean_slowdown_experimental_factor = 1
  Greenland_ice_slide_circulation_slowdown_effect = 0.33
  NEvt_13d_Greenland_slide_experiment_start_yr = 3e06
  Greenland_slide_experiment_over_how_many_years_yr = 70
#  UNIT_conversion_GtC_to_MtC = 1000
  Time_for_agri_land_to_become_abandoned = 2
  Fraction_of_cropland_developed_for_urban_land = 0.01
  expSoE_of_ed_on_cost_of_new_capacity = 0.075
  Frac_vol_deep_ocean_of_total = (
    Volume_ocean_deep_1km_to_bottom / Volume_of_total_ocean_Gm3
  )
  Frac_vol_ocean_upwelling_of_total = (Volume_ocean_upwelling_100m_to_1km / Volume_of_total_ocean_Gm3)
  Time_in_cold = 6.51772
  Time_in_trunk = 234.638
  Time_in_deep = 739.89
  Time_in_intermediate_yr = 211.397
  Time_in_warm = 26.227
  Rate_of_wetland_destruction_pct_of_existing_wetlands_py = 0
  When_first_destroyed_yr = 2020
  Duration_of_destruction_yr = 5
  Ratio_of_methane_in_tundra_to_wetland = 4
  CH4_per_sqkm_of_wetlands = (
    Avg_amount_of_C_in_the_form_of_CH4_per_km2 / Ratio_of_methane_in_tundra_to_wetland
  )
  Emissions_of_natural_CH4_GtC_py = 0.19
  CH4_halflife_in_atmosphere = 7.3
  SoE_of_Inventory_on_RoC_of_ddx = -0.2
  Sufficient_relative_inventory = 1
  Max_FOPOLM = 0.2
  Half_life_of_tech_progress_in_non_energy_footprint = 120
  GenEq_cn_a = 0.4314
  GenEq_cn_b = -0.095
  GenEq_ec_a = 0.0152
  GenEq_ec_b = 0.3476
  GenEq_me_a = 0.0003
  GenEq_me_b = 0.1032
  GenEq_sa_la_af_a = 0.06
  GenEq_sa_la_af_b = 0.15
  GenEq_se_eu_pa_us_a = 0.0021
  GenEq_se_eu_pa_us_b = 0.241
  Time_to_change_GE = 10
  Strength_of_owner_reaction_to_worker_resistance = 0.03
  Slope_of_RoC_of_people_considering_entering_the_labor_pool = -1
  Slope_of_RoC_of_people_considering_leaving_the_labor_pool = 1
  SoE_of_industrialization_on_RoC_in_TFP = 0
  SoE_of_inflation_rate_on_indicated_signal_rate = 1.4
  SoE_of_unemployment_rate_on_indicated_signal_rate = -1.3
  Signal_rate_adjustment_time = 0.1
  Reference_public_spending_fraction = 0.3
  Strength_of_Effect_of_gender_inequality_on_social_trust = 0.1
  Strength_of_Effect_of_schooling_on_social_trust = 0.1
  Time_to_change_social_trust = 10
  Strength_of_worker_reaction_to_owner_power_normal = 0.075
  Strength_of_inequality_effect_on_food_TA = 2
  Strength_of_Effect_of_TAs_on_inequality = 0.1
  Cold_dense_water_sinking_in_Sverdrup_in_1850 = 35
  Strength_of_Effect_of_SDG_scores_on_wellbeing = 0.3
  Convection_as_f_of_incoming_solar_in_1850 = 0.071
  Sensitivity_of_convection_to_temp = 2.5
  Nbr_of_relevant_energy_policies = 5
  Nbr_of_relevant_inequality_policies = 9
  Nbr_of_relevant_poverty_policies = 9
  Nbr_of_relevant_food_policies = 6
  Nbr_of_relevant_empowerment_policies = 3
  Indicated_crop_yield_SE_L = 11
  Indicated_crop_yield_SE_k = 0.03171
  UNIT_conv_N_to_yield = 1
  Indicated_crop_yield_SE_x = -14.5
  Indicated_crop_yield_SE_L2 = 5
  Indicated_crop_yield_SE_k2 = -0.232
  Indicated_crop_yield_SE_x2 = 62.13
  Indicated_crop_yield_SE_min = 2.1
#  UNIT_conv_to_per_thousand = 1000
  expSoE_of_ed_on_dying = 0.15
  Strength_of_malnutrition_effect = 6
  Strength_of_poverty_effect = 2
  Strength_of_inequality_effect_on_mortality = 0.5
  Ctax_Time_to_implement_goal = 5
  DAC_Time_to_implement_goal = 15
  Debt_cancelling_stepheight = 1
  Govt_debt_cancelling_spread = 2
  Lifetime_of_public_capacity = 25
  Time_to_write_of_public_loan_defaults = 30
  Time_to_implement_conventional_practices = 1
  Demand_adjustment_time = 1
  Time_to_deposit_C_in_sediment = 20000
  Slope_of_Eff_of_dmd_imbalnce_on_life_of_capacity = 0
  expSoE_of_ed_on_TFP = 0.1
  Sensitivity_of_trop_to_humidity = 5
  Humidity_of_atmosphere_in_1850_g_p_kg = 1.98018
  Strength_of_effect_of_income_ratio_after_tax = 0.1
  Reference_Time_to_regrow_TROP_after_deforesting = 1000
  Time_to_implement_actually_entering_the_pool = 1
  Greenland_slide_experiment_how_much_sildes_in_the_ocean_fraction = 0.25
  Reference_max_fraction_of_forest_possible_to_cut = 0.8
  FEHC_Time_to_implement_policy = 3
  Finance_sector_response_time_to_central_bank = 1
  UNIT_conversion_Sv_to_Gm3_py = 31536
  FLWR_Time_to_implement_ISPV_goal = 5
  Forest_cutting_policy_Time_to_implement_goal = 5
  pb_Forest_degradation_green_threshold = 25
  UNIT_conv_to_Mkm2 = 1000
  Frac_atm_absorption = 75 / 340
  Frac_SW_clear_sky_reflection_aka_scattering = 0.0837
#  Fraction_blocked_by_ALL_GHG_in_1980 = 0.213577
#  Fraction_blocked_CH4_in_1980 = 0.00445458
#  Fraction_blocked_CO2_in_1980 = 0.0911213
#  Fraction_blocked_othGHG_in_1980 = 0.0393
  UNIT_conv_pct_to_fraction = 100
  Freshwater_withdrawal_per_person_TLTL = 415
  UNIT_conv_to_cubic_km_pr_yr = 1 / 1000
  pb_Freshwater_withdrawal_green_threshold = 3000
  FTPEE_Time_to_implement_goal = 3
  FVE_shape_time = 3
  FWRP_Time_to_implement_goal = 15
  Time_required_to_fill_jobs = 7
  Global_warming_potential_CO2 = 1
  UNIT_conversion_to_tCO2e_pr_USD = 1000
  UNIT_conv_to_TUSD = 1 / 1000
  pb_Global_Warming_green_threshold = 1
  Time_to_write_off_govt_defaults_to_private_lenders = 30
  GRASS_Avg_life_biomass_yr = 100
  Use_of_GRASS_biomass_for_construction_in_1850_pct = 0.05
  Use_of_GRASS_for_construction_in_2000_GtBiomass = (
    GRASS_Living_biomass_in_1850
    * Use_of_GRASS_biomass_for_construction_in_1850_pct
    / 100
  )
  Time_to_regrow_GRASS_yr = 10
  Time_to_regrow_GRASS_after_deforesting_yr = 80
  Heat_flow_from_the_earths_core = 0.1 * 16.09
  Hydro_future_net_dep_rate = 0.01
  Time_to_implement_regen_practices = 5
  Max_OSF = 0.95
  Min_OSF = 0.1
  pb_Air_Pollution_a = 0.0425
  pb_Air_Pollution_Unit_conv_to_make_LN_dmnl_from_terra_USD = 1
  pb_Air_Pollution_b = 37.7
  UNIT_conv_to_UAC = 1
#  INITIAL_TIME = 1980
  Inventory_coverage_perception_time = 0.3
  K_to_C_conversion = 273.15
  Time_to_degrade_Kyoto_Fluor_yr = 50
  Land_surface_temp_adjustment_time_yr = 25
  Time_to_implement_lay_off = 3
  Lead_PB_green_threshold = 5
  Lead_release_a = 3.2
  Lead_release_b = 4.0412
  Unit_conv_to_make_LN_dmnl_from_terra_USD = 1000
  Start_year_P_Pb_phaseout = 2020
  P_Pb_Phaseout_time_TLTL = 150
  Lead_UNIT_conv_to_Mt_pr_yr = 1
  Time_to_implement_actually_leaving_the_pool = 1.5
  Long_term_interest_rate_expectation_formation_time = 4
  LPB_Time_to_implement_policy = 3
  LPBgrant_Time_to_implement_policy = 3
  LPBsplit_Time_to_implement_policy = 3
#  UNIT_conversion_to_pct = 100
  Time_for_volcanic_aerosols_to_remain_in_the_stratosphere = 1
  Time_to_degrade_Montreal_gases_yr = 30
  N_number_of_years_ago = 5
  Nitrogen_PB_green_threshold = 100
  Time_to_degrade_N2O_in_atmopshere_yr = 95
  NEP_Time_to_implement_goal = 3
  Time_to_adjust_owner_investment_behaviour_in_productive_assets = 10
  Net_heat_flow_ocean_between_surface_and_deep_per_K_of_difference_ZJ_py_K = 10
  Temp_gradient_in_surface_degK = 9.7
  NF_Avg_life_biomass_yr = 60
  Use_of_NF_biomass_for_construction_in_1850_pct = 0.58
  Use_of_NF_for_construction_in_2000_GtBiomass = (
    NF_Living_biomass_in_1850 * Use_of_NF_biomass_for_construction_in_1850_pct / 100
  )
  Time_to_regrow_NF_yr = 30
  Time_to_regrow_NF_after_deforesting_yr = 80
  Normal_Time_to_implement_UN_policies = 5
  Nuclear_future_net_dep_rate = 0.02
  P_release_a = 5.3439
  P_release_b = 7.6136
  UNIT_conv_to_Mt_pr_yr = 1
  Phosphorous_PB_green_threshold = 10
#  Temp_ocean_surface_in_1850_C = Temp_surface_1850 - Temp_gradient_in_surface_degK
#  Output_growth_in_1980 = 0.035
  UNIT_conversion_to_M = 1000
  pb_Ozone_depletion_green_threshold = 0.25
  per_annum_yr = 1
  Time_for_urban_land_to_become_abandoned = 20
  Ref_shifting_biome_yr = 50
  REFOREST_policy_Time_to_implement_goal = 15
  Retooling_time = 3
  RIPLGF_Addl_time_to_shift_govt_expenditure = 3
  RMDR_Time_to_implement_policy = 10
  Social_tension_perception_delay = 5
  Sales_averaging_time = 1
#  TIME_STEP = 0.03125
  Scaling_factor_of_eff_of_poverty_on_social_tension = 0.08
#  UNIT_conversion_mm_to_m = 1 / 1000
#  UNIT_conv_to_m = 1 / 100
  SGMP_Time_to_implement_policy = 3
  Zero_C_on_K_scale_K = 273.15
  Slope_of_effect_of_temp_shifting_DESERT_to_GRASS = 0.4
  Slope_of_effect_of_temp_shifting_GRASS_to_DESERT = 5
  Slope_of_effect_of_temp_shifting_GRASS_to_NF = 0.1
  Slope_of_effect_of_temp_shifting_GRASS_to_TROP = 0.2
  Slope_of_effect_of_temp_shifting_NF_to_GRASS = 0.01
  Slope_of_effect_of_temp_shifting_NF_to_TROP = 0.2
  Slope_of_effect_of_temp_on_shifting_NF_to_Tundra = 0.1
  Slope_of_effect_of_temp_shifting_TROP_to_GRASS = 0.05
  Slope_of_effect_of_temp_on_shifting_TROP_to_NF = 1
  Slope_of_effect_of_temp_shifting_tundra_to_NF = 0.2
  StrUP_Time_to_implement_policy = 3
  the_N_for_PC_N_yrs_ago = 5
  Time_for_defaulting_to_impact_cost_of_capital = 3
  Time_for_env_damage_to_affect_wellbeing = 3
  Time_for_GDPpp_to_affect_death_rates = 1
  Time_for_GDPpp_to_affect_owner_saving_fraction = 10
  Time_for_inequality_to_impact_wellbeing = 5
  Time_for_max_debt_debt_burden_to_affect_max_debt = 5
  Time_for_N_use_to_affect_regeneative_choice = 5
  Time_for_N_use_to_affect_soil_quality = 10
  Time_for_poverty_to_affect_social_tension_and_trust = 5
  Time_for_public_spending_to_affect_wellbeing = 5
  Time_for_shifts_in_relative_wealth_to_affect_env_damage_response = 10
  Time_lag_for_env_damage_to_affect_mortality = 5
  Time_required_for_inventory_fluctuations_to_impact_inflation_rate = 2
  Time_to_adjust_budget = 1
  Time_to_adjust_Existential_minimum_income = 5
  Time_to_adjust_forest_area_to_CO2_emissions = 2
  Time_to_adjust_owners_budget = 1
  Time_to_adjust_reform_willingness = 5
  Time_to_adjust_worker_consumption_pattern = 1
  Time_to_affect_life_expectancy = 10
  Time_to_ease_in_wealth_accumulation = 10
  Time_to_establish_Long_term_unemployment_rate = 5
  Time_to_form_an_opinion_about_demand_imbalance = 1
  Time_to_implement_CCS_goal = 10
  Time_to_implement_deforestation = 5
  Time_to_implement_ISPV_goal = 3
  Time_to_let_shells_form_and_sink_to_sediment_yr = 25
  Time_to_propagate_temperature_change_through_the_volume_of_permafrost_yr = 5
  Time_to_ramp_in_future_TLTL_leakage = 5
  Time_to_regrow_TROP_yr = 30
  Time_to_regrow_TUNDRA_after_deforesting_yr = 80
  Time_to_regrow_TUNDRA_yr = 10
  Time_to_smooth_cost_of_capital_for_workers = 10
  Time_to_smooth_forest_land_comparison = 15
  Time_to_smooth_malnutrition_effect = 3
  Time_to_smooth_max_govt_debt = 2
  Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust = 5
  Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA = 5
  Time_to_smooth_non_energy_footprint_changes = 5
  Time_to_smooth_out_temperature_diff_relevant_for_melting_or_freezing_from_1850_yr = 3
  Time_to_smooth_poverty_effect = 3
  Time_to_smooth_regional_food_balance = 3
  Time_to_smooth_RoC_in_GDPpp = 4
  Time_to_smooth_SDG_scores_for_wellbeing = 5
  Time_to_smooth_social_tension_index = 3
  Time_to_smooth_the_anchor_SDG_scores_for_wellbeing = 5
  Time_to_smooth_UAC = 10
  Time_to_smooth_unemp_rate = 5
  Time_to_verify_emi = 2
  Time_to_write_off_worker_defaults = 5
  TROP_Avg_life_biomass_yr = 60
  Use_of_TROP_biomass_for_construction_in_1850_pct = 0.48
  Use_of_TROP_for_construction_in_2000_GtBiomass = (
    TROP_Living_biomass_in_1850 * Use_of_TROP_biomass_for_construction_in_1850_pct / 100
  )
  TUNDRA_Avg_life_biomass_yr = 100
  Use_of_TUNDRA_biomass_for_construction_in_1850_pct = 0.05
  Use_of_TUNDRA_for_construction_in_2000_GtBiomass = (
    TUNDRA_Living_biomass_in_1850
    * Use_of_TUNDRA_biomass_for_construction_in_1850_pct
    / 100
  )
  Unemployment_perception_time = 1
  WReaction_Time_to_implement_policy = 3
  XtaxCom_Time_to_implement_policy = 3
  Xtaxfrac_Time_to_implement_policy = 3
  XtaxRateEmp_Time_to_implement_policy = 3
  Years_for_CBC_comparison = 5

#  GDP_in_1980 = [7070.0, 1160.0, 1970.0, 1510.0, 1210.0, 2650.0, 3750.0, 4290.0, 8780.0, 940.0]
  Capacity_in_1980 = [21210.0, 9280.0, 3152.0, 12080.0, 9680.0, 15900.0, 15000.0, 21450.0, 26340.0, 7520.0]
  Optimal_output_in_1980 = [7070.0, 1160.0, 1970.0, 1510.0, 1210.0, 2650.0, 3750.0, 4290.0, 8780.0, 940.0]
#  Demand_in_1980 = [7070.0, 1160.0, 1970.0, 1510.0, 1210.0, 2650.0, 3750.0, 4290.0, 8780.0, 940.0]
#  Owner_income_in_1980 = [2444.98357368932, 401.6364889208633, 682.2448010526314, 517.3716314634146, 422.51786329192544, 922.9009947368421, 1303.1542663043476, 1498.1358241104292, 3036.5664395876292, 325.04474437500005]
#  Worker_income_after_tax_in_1980 = [2754.783972330097, 451.5569971223021, 766.7290246963564, 592.6921256097561, 467.817302173913, 1026.7555175438597, 1455.502581521739, 1658.519132208589, 3420.876272164948, 366.29317812499994]
#  Consumption_taxes_in_1980 = [84.9168927365534, 21.153979160719423, 30.808629347125507, 24.42633856939024, 20.802216334565216, 42.79448360263157, 42.9795100271739, 69.25868270530675, 105.45174357773196, 16.1664156740625]
#  Govt_debt_in_1980 = [3535.0, 1160.0, 394.0, 1510.0, 1210.0, 2650.0, 3750.0, 4290.0, 8780.0, 940.0]
#  All_crop_dmd_food_in_1980 = [170.26654560129538, 217.0057926743663, 452.21248710575935, 99.72094126054908, 454.0325733386143, 556.2973268965412, 119.58734313350372, 267.49973275275136, 470.721254279469, 193.06382452194592]
#  Capacity_under_construction_in_1980 = [2121.0, 928.0, 315.2, 1208.0, 968.0, 1590.0, 1500.0, 2145.0, 2634.0, 752.0]
  Corporate_borrowing_cost_in_1980 = [0.07500000000000001, 0.095, 0.07500000000000001, 0.07500000000000001, 0.07500000000000001, 0.07500000000000001, 0.07500000000000001, 0.07500000000000001, 0.07500000000000001, 0.07500000000000001]
  Worker_share_of_output_with_unemployment_effect_in_1980 = [0.5566344660194176, 0.5561046762589928, 0.5560036437246965, 0.5607304878048781, 0.5523226708074535, 0.5535070175438597, 0.5544771739130435, 0.5522874233128835, 0.5566020618556701, 0.5566765625]
  Effect_of_poverty_on_social_tension_in_1980 = [0.8959910106335136, 0.21240214937921398, 0.19288246412336335, 0.3619369660522107, 0.18958434769674412, 0.3791125730168431, 0.7532928033231301, 0.5628666035524531, 0.8076690781037237, 0.19856155397797282]
  GDPpp_in_1980 = [30.78847069, 3.118545931, 1.923464459, 8.873859532, 1.362280228, 7.634754409, 18.93943182, 6.719867521, 19.03997639, 2.628879465]
#  Inventory_in_1980 = [2828.0, 464.0, 788.0, 604.0, 484.0, 1060.0, 1500.0, 1716.0, 3512.0, 376.0]
#  LW_TOA_radiation_from_atm_to_space_in_1850 = 3826.196024026106
#  Public_Capacity_in_1980 = [4242.0, 1856.0, 630.4000000000001, 2416.0, 1936.0, 3180.0, 3000.0, 4290.0, 5268.0, 1504.0]
  Size_of_industrial_sector_in_1980 = [0.27663871838081144, 0.3356939464577147, 0.30154469574192583, 0.3837259973983511, 0.28749251905661244, 0.38392771269234593, 0.3344966720230427, 0.37061638260621077, 0.32008763862611544, 0.322106784272718]
  Worker_to_owner_income_after_tax_ratio_in_1980 = [1.2768295877969231, 1.1919382944356827, 1.187939509109339, 1.2261985626729526, 1.170164109044806, 1.1934698036363887, 1.227277700326229, 1.1995428747041386, 1.2458121573553074, 1.1930852649531762]
#  Workers_debt_in_1980 = [7070.0, 232.0, 394.0, 604.0, 484.0, 1060.0, 1500.0, 1716.0, 3512.0, 376.0]
  WSO_in_1980 = [0.5566344660194176, 0.5561046762589928, 0.5560036437246965, 0.5607304878048781, 0.5523226708074535, 0.5535070175438597, 0.5544771739130435, 0.5522874233128835, 0.5566020618556701, 0.5566765625]
  Global_forest_land_in_1980 = 3663.6520999999993
#  Output_last_year_in_1980 = [6830.917874396136, 1120.7729468599034, 1903.3816425120774, 1458.937198067633, 1169.0821256038648, 2560.386473429952, 3623.188405797102, 4144.927536231884, 8483.091787439615, 908.2125603864735]
#  Output_last_year_in_1980 = [6830.917874396136, 1120.7729468599034, 1903.3816425120774, 1458.937198067633, 1169.0821256038648, 2560.386473429952, 3623.188405797102, 4144.927536231884, 8483.091787439615, 908.2125603864735]

  if von == 2025:
    runde = 1
  elif von == 2040:
    runde = 2
  elif von == 2060:
    runde = 3
  else:
    print("von not 2025 | 2040 | 2060")
## load mdf play with Nathalie's globals
#  mdf_play_3841_405 = read_mdfplay_full("mdf_play.npy", runde)
  mdf_play_3841_415 = read_mdfplay_full("mdf_play_nat.npy", runde)

# from PyCharm
#  mdf_play_nat = np.load('mdf_play_nat.npy')
#  ch = np.load('ch.npy')
#  ch_nat = np.load('ch_nat.npy')
#  chtab = np.load('chtab.npy')
#  with open('fcol_in_mdf_nat.json') as ff:
#    with open('fcol_in_mdf.json') as ff:
#    fcol_in_mdf = json.load(ff)
#  with open('ftab_in_d_table.json') as ff:
#    ftab_in_d_table = json.load(ff)
#  with open('d_table.pkl', 'rb') as fp:
#    d_table = pickle.load(fp)
#  dt = 1 / 32
#  start_tick = 1
#  if von == 2025 and bis == 2040:
#    howlong = 40
#    row_start = np.load('row2025_nat.npy')

#  ff = data_files["ch.npy"]
  ff = data_files["ch_nat.npy"]
  ch = np.load(ff)
#    ch = np.load('ch.npy')
  ff = data_files["chtab.npy"]
#  chtab = np.load(ff)
  #    chtab = np.load('chtab.npy')
  with open(data_files["fcol_in_mdf_nat.json"]) as fj:
    fcol_in_mdf = json.load(fj)
  with open(data_files["ftab_in_d_table.json"]) as fj:
    ftab_in_d_table = json.load(fj)
  #    with open('ftab_in_d_table.json') as ff:
  #        ftab_in_d_table = json.load(ff)
  with open(data_files["d_table.pkl"], "rb") as fp:
    d_table = pickle.load(fp)
  #    with open('d_table.pkl', 'rb') as fp:
  #        d_table = pickle.load(fp)
  dt = 1 / 32
  start_tick = 1
  if von == 2025 and bis == 2040:
    howlong = 40
    ff = data_files["row2025_nat.npy"]
    row_start = np.load(ff)
    #        row_start = np.load('row2025.npy')
    start_mod = von
    zeit = start_mod
    end_mod = bis
    time_slots = int((end_mod - start_mod) * 1 / dt + 1)
    cols = len(ch)
    # set up the data matrix with ALL columns and rows according to current timeslots
    mdf = np.full((time_slots, cols), np.nan)
    tid = np.linspace(start_mod, end_mod, time_slots)
    mdf[:, 0] = tid
    mdf[0, :] = row_start
    start_tick_in_mdf_play = int((von - 1980) / dt + 1)
    end_tick = int((bis - von) / dt + 1)
    print("ugregmod r1 start_tick_in_mdf_play "+ str(start_tick_in_mdf_play)+ " bis "+ str(end_tick))
  elif von == 2040 and bis == 2060:
    howlong = 60
    s_row = app_tables.game_files.get(game_id=game_id, yr=2040)
    s_row_elem = s_row["start_row_data"]
    row_start = pickle.loads(s_row_elem.get_bytes())
    #        row_start = np.load('row2040.npy')
    s_row = app_tables.game_files.get(game_id=game_id, yr=2040)
    s_row_elem = s_row["mdf_play"]
    mdf_play_3841_415 = pickle.loads(s_row_elem.get_bytes())
    start_mod = von
    zeit = start_mod
    end_mod = bis
    time_slots = int((end_mod - start_mod) * 1 / dt + 1)
    cols = len(ch)
    # set up the data matrix with ALL columns and rows according to current timeslots
    mdf = np.full((time_slots, cols), np.nan)
    tid = np.linspace(start_mod, end_mod, time_slots)
    mdf[:, 0] = tid
    mdf[0, :] = row_start
    start_tick_in_mdf_play = int((von - 1980) / dt + 1)
    end_tick = int((bis - von) / dt + 1)
    print("ugregmod r2 start_tick_in_mdf_play "+ str(start_tick_in_mdf_play)+ " bis "+ str(end_tick))
  elif von == 2060 and bis == 2100:
    howlong = 21
    s_row = app_tables.game_files.get(game_id=game_id, yr=2060)
    s_row_elem = s_row["start_row_data"]
    row_start = pickle.loads(s_row_elem.get_bytes())
    s_row = app_tables.game_files.get(game_id=game_id, yr=2060)
    s_row_elem = s_row["mdf_play"]
    mdf_play_3841_415 = pickle.loads(s_row_elem.get_bytes())
    print("in ugregmod von=2060")
    start_mod = von
    zeit = start_mod
    end_mod = bis
    time_slots = int((end_mod - start_mod) * 1 / dt + 1)
    cols = len(ch)
    # set up the data matrix with ALL columns and rows according to current timeslots
    mdf = np.full((time_slots, cols), np.nan)
    tid = np.linspace(start_mod, end_mod, time_slots)
    mdf[:, 0] = tid
    mdf[0, :] = row_start
    start_tick_in_mdf_play = int((von - 1980) / dt + 1)
    end_tick = int((bis - von) / dt + 1)
    print("ugregmod r3 start_tick_in_mdf_play "+ str(start_tick_in_mdf_play)+ " bis "+ str(end_tick))
  else:
    print("We have a problem in def run_game with von and bis")

  ###################
  #
  # loop to run the model
  #
  yr = int(zeit)
  for rowi in range(start_tick, end_tick):
    zeit = zeit + dt
    jjyr = rowi - 1
    if jjyr % 32 == 0:
      print(yr)
      anvil.server.task_state["Year"] = yr
      yr += 1

    # GDP_in_TeraUSD_hist_exo[region] =  GET_XLS_DATA ( 'e4a-exo.xlsx' , 'ts' , '1' , 'D612' )
    tabidx = ftab_in_d_table["GDP_in_TeraUSD_hist_exo"]  # fetch the correct table
    idxlhs = fcol_in_mdf["GDP_in_TeraUSD_hist_exo"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for i in range(0, 10):
      mdf[rowi, idxlhs + i] = GRAPH(zeit, look[:, 0], look[:, i + 1])

    # GDPpp_H_exo[region] =  GET_XLS_DATA ( 'e4a-exo.xlsx' , 'ts' , '1' , 'D2' )
    tabidx = ftab_in_d_table["GDPpp_H_exo"]  # fetch the correct table
    idxlhs = fcol_in_mdf["GDPpp_H_exo"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for i in range(0, 10):
      mdf[rowi, idxlhs + i] = GRAPH(zeit, look[:, 0], look[:, i + 1])

    # Sea_level_rise_H_cm =  GET_XLS_DATA ( 'e4a-exo.xlsx' , 'ts' , '1196' , 'D1197' )
    tabidx = ftab_in_d_table["Sea_level_rise_H_cm"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Sea_level_rise_H_cm"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    mdf[rowi, idxlhs] = GRAPH(zeit, look[:, 0], look[:, 1])

    # Abandoned_crop_and_grazing_land[region] = INTEG ( c_to_acgl[region] + gl_to_acgl[region] + apl_to_acgl[region] - acgl_to_c[region] - acgl_to_fa[region] - acgl_to_gl[region] - acgl_to_pl[region] , 0 )
    idx1 = fcol_in_mdf["Abandoned_crop_and_grazing_land"]
    idx2 = fcol_in_mdf["c_to_acgl"]
    idx3 = fcol_in_mdf["gl_to_acgl"]
    idx4 = fcol_in_mdf["apl_to_acgl"]
    idx5 = fcol_in_mdf["acgl_to_c"]
    idx6 = fcol_in_mdf["acgl_to_fa"]
    idx7 = fcol_in_mdf["acgl_to_gl"]
    idx8 = fcol_in_mdf["acgl_to_pl"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (
          mdf[rowi - 1, idx2 + j]
          + mdf[rowi - 1, idx3 + j]
          + mdf[rowi - 1, idx4 + j]
          - mdf[rowi - 1, idx5 + j]
          - mdf[rowi - 1, idx6 + j]
          - mdf[rowi - 1, idx7 + j]
          - mdf[rowi - 1, idx8 + j]
        )
        * dt
      )

    # Abandoned_populated_land[region] = INTEG ( pl_to_apl[region] - apl_to_pl[region] - apl_to_acgl[region] , 0 )
    idx1 = fcol_in_mdf["Abandoned_populated_land"]
    idx2 = fcol_in_mdf["pl_to_apl"]
    idx3 = fcol_in_mdf["apl_to_pl"]
    idx4 = fcol_in_mdf["apl_to_acgl"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # GDP_H[region] = GDP_in_TeraUSD_hist_exo[region] * UNIT_conv_Tera_to_Giga
    idxlhs = fcol_in_mdf["GDP_H"]
    idx1 = fcol_in_mdf["GDP_in_TeraUSD_hist_exo"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_Tera_to_Giga

    # Capacity[region] = INTEG ( Adding_capacity[region] - Discarding_capacity[region] , Capacity_in_1980[region] )
    idx1 = fcol_in_mdf["Capacity"]
    idx2 = fcol_in_mdf["Adding_capacity"]
    idx3 = fcol_in_mdf["Discarding_capacity"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Employed[region] = INTEG ( Getting_a_job[region] - Loosing_a_job[region] , Employed_in_1980[region] )
    idx1 = fcol_in_mdf["Employed"]
    idx2 = fcol_in_mdf["Getting_a_job"]
    idx3 = fcol_in_mdf["Loosing_a_job"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Embedded_TFP[region] = INTEG ( Effect_of_capacity_renewal[region] , 1 )
    idx1 = fcol_in_mdf["Embedded_TFP"]
    idx2 = fcol_in_mdf["Effect_of_capacity_renewal"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Optimal_real_output[region] = Optimal_output_in_1980[region] * ( Capacity[region] / Capacity_in_1980[region] ) ^ Kappa * ( Employed[region] / Employed_in_1980[region] ) ^ Lambdav * ( Embedded_TFP[region] )
    idxlhs = fcol_in_mdf["Optimal_real_output"]
    idx1 = fcol_in_mdf["Capacity"]
    idx2 = fcol_in_mdf["Employed"]
    idx3 = fcol_in_mdf["Embedded_TFP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Optimal_output_in_1980[j]
        * (mdf[rowi, idx1 + j] / Capacity_in_1980[j]) ** Kappa
        * (mdf[rowi, idx2 + j] / Employed_in_1980[j]) ** Lambdav
        * (mdf[rowi, idx3 + j])
      )

    # Perceived_relative_inventory[region] = SMOOTHI ( Inventory_coverage_to_goal_ratio[region] , Inventory_coverage_perception_time , Perceived_relative_inventory_in_1980[region] )
    idx1 = fcol_in_mdf["Perceived_relative_inventory"]
    idx2 = fcol_in_mdf["Inventory_coverage_to_goal_ratio"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Inventory_coverage_perception_time
        * dt
      )

    # Indicated_hours_worked_index[region] = 1 + SoE_of_inventory_on_indicated_hours_worked_index[region] * ( Perceived_relative_inventory[region] / Goal_for_relative_inventory - 1 )
    idxlhs = fcol_in_mdf["Indicated_hours_worked_index"]
    idx1 = fcol_in_mdf["Perceived_relative_inventory"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + SoE_of_inventory_on_indicated_hours_worked_index[    j
      ] * (mdf[rowi, idx1 + j] / Goal_for_relative_inventory - 1)

    # Hours_worked_index[region] = SMOOTH ( Indicated_hours_worked_index[region] , Time_to_adjust_work_hours[region] )
    idx1 = fcol_in_mdf["Hours_worked_index"]
    idx2 = fcol_in_mdf["Indicated_hours_worked_index"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_adjust_work_hours[j]
        * dt
      )

    # Output[region] = Optimal_real_output[region] * Hours_worked_index[region] / Hours_worked_index_in_1980[region]
    idxlhs = fcol_in_mdf["Output"]
    idx1 = fcol_in_mdf["Optimal_real_output"]
    idx2 = fcol_in_mdf["Hours_worked_index"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / Hours_worked_index_in_1980
      )

    # GDP_model[region] = Output[region]
    idxlhs = fcol_in_mdf["GDP_model"]
    idx1 = fcol_in_mdf["Output"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Cohort_0_to_4[region] = INTEG ( Births[region] - Aging_4_to_5[region] - dying_0_to_4[region] , Cohort_0_to_4_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_0_to_4"]
    idx2 = fcol_in_mdf["Births"]
    idx3 = fcol_in_mdf["Aging_4_to_5"]
    idx4 = fcol_in_mdf["dying_0_to_4"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_10_to_14[region] = INTEG ( Aging_9_to_10[region] - Aging_14_to_15[region] + net_migration_10_to_14[region] , Cohort_10_to_14_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_10_to_14"]
    idx2 = fcol_in_mdf["Aging_9_to_10"]
    idx3 = fcol_in_mdf["Aging_14_to_15"]
    idx4 = fcol_in_mdf["net_migration_10_to_14"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] + mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_15_to_19[region] = INTEG ( Aging_14_to_15[region] - Aging_19_to_20[region] , Cohort_15_to_19_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_15_to_19"]
    idx2 = fcol_in_mdf["Aging_14_to_15"]
    idx3 = fcol_in_mdf["Aging_19_to_20"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Cohort_5_to_9[region] = INTEG ( Aging_4_to_5[region] - Aging_9_to_10[region] , Cohort_5_to_9_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_5_to_9"]
    idx2 = fcol_in_mdf["Aging_4_to_5"]
    idx3 = fcol_in_mdf["Aging_9_to_10"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Cohort_0_to_20[region] = Cohort_0_to_4[region] + Cohort_10_to_14[region] + Cohort_15_to_19[region] + Cohort_5_to_9[region]
    idxlhs = fcol_in_mdf["Cohort_0_to_20"]
    idx1 = fcol_in_mdf["Cohort_0_to_4"]
    idx2 = fcol_in_mdf["Cohort_10_to_14"]
    idx3 = fcol_in_mdf["Cohort_15_to_19"]
    idx4 = fcol_in_mdf["Cohort_5_to_9"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
      )

    # Cohort_20_to_24[region] = INTEG ( Aging_19_to_20[region] - Aging_24_to_25[region] + net_migration_20_to_24[region] , Cohort_20_to_24_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_20_to_24"]
    idx2 = fcol_in_mdf["Aging_19_to_20"]
    idx3 = fcol_in_mdf["Aging_24_to_25"]
    idx4 = fcol_in_mdf["net_migration_20_to_24"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] + mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_25_to_29[region] = INTEG ( Aging_24_to_25[region] - Aging_29_to_30[region] + net_migration_25_to_29[region] , Cohort_25_to_29_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_25_to_29"]
    idx2 = fcol_in_mdf["Aging_24_to_25"]
    idx3 = fcol_in_mdf["Aging_29_to_30"]
    idx4 = fcol_in_mdf["net_migration_25_to_29"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] + mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_30_to_34[region] = INTEG ( Aging_29_to_30[region] - Aging_34_to_35[region] + net_migration_30_to_34[region] , Cohort_30_to_34_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_30_to_34"]
    idx2 = fcol_in_mdf["Aging_29_to_30"]
    idx3 = fcol_in_mdf["Aging_34_to_35"]
    idx4 = fcol_in_mdf["net_migration_30_to_34"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] + mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_35_to_39[region] = INTEG ( Aging_34_to_35[region] - Aging_39_to_40[region] - dying_35_to_39[region] , Cohort_35_to_39_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_35_to_39"]
    idx2 = fcol_in_mdf["Aging_34_to_35"]
    idx3 = fcol_in_mdf["Aging_39_to_40"]
    idx4 = fcol_in_mdf["dying_35_to_39"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_20_to_40[region] = Cohort_20_to_24[region] + Cohort_25_to_29[region] + Cohort_30_to_34[region] + Cohort_35_to_39[region]
    idxlhs = fcol_in_mdf["Cohort_20_to_40"]
    idx1 = fcol_in_mdf["Cohort_20_to_24"]
    idx2 = fcol_in_mdf["Cohort_25_to_29"]
    idx3 = fcol_in_mdf["Cohort_30_to_34"]
    idx4 = fcol_in_mdf["Cohort_35_to_39"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
      )

    # Cohort_40_to_44[region] = INTEG ( Aging_39_to_40[region] - Aging_44_to_45[region] - dying_40_to_45[region] , Cohort_40to_44_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_40_to_44"]
    idx2 = fcol_in_mdf["Aging_39_to_40"]
    idx3 = fcol_in_mdf["Aging_44_to_45"]
    idx4 = fcol_in_mdf["dying_40_to_45"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_45_to_49[region] = INTEG ( Aging_44_to_45[region] - Aging_49_to_50[region] - dying_45_to_49[region] , Cohort_45_to_49_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_45_to_49"]
    idx2 = fcol_in_mdf["Aging_44_to_45"]
    idx3 = fcol_in_mdf["Aging_49_to_50"]
    idx4 = fcol_in_mdf["dying_45_to_49"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_50_to_54[region] = INTEG ( Aging_49_to_50[region] - Aging_54_to_55[region] - dying_50_to_54[region] , Cohort_50_to_54_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_50_to_54"]
    idx2 = fcol_in_mdf["Aging_49_to_50"]
    idx3 = fcol_in_mdf["Aging_54_to_55"]
    idx4 = fcol_in_mdf["dying_50_to_54"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_55_to_59[region] = INTEG ( Aging_54_to_55[region] - Aging_59_to_60[region] - dying_55_to_59[region] , Cohort_55_to_59_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_55_to_59"]
    idx2 = fcol_in_mdf["Aging_54_to_55"]
    idx3 = fcol_in_mdf["Aging_59_to_60"]
    idx4 = fcol_in_mdf["dying_55_to_59"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_40_to_60[region] = Cohort_40_to_44[region] + Cohort_45_to_49[region] + Cohort_50_to_54[region] + Cohort_55_to_59[region]
    idxlhs = fcol_in_mdf["Cohort_40_to_60"]
    idx1 = fcol_in_mdf["Cohort_40_to_44"]
    idx2 = fcol_in_mdf["Cohort_45_to_49"]
    idx3 = fcol_in_mdf["Cohort_50_to_54"]
    idx4 = fcol_in_mdf["Cohort_55_to_59"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
      )

    # Cohort_60_to_64[region] = INTEG ( Aging_59_to_60[region] - Aging_64_to_65[region] - dying_60_to_64[region] , Cohort_60to_64_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_60_to_64"]
    idx2 = fcol_in_mdf["Aging_59_to_60"]
    idx3 = fcol_in_mdf["Aging_64_to_65"]
    idx4 = fcol_in_mdf["dying_60_to_64"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_65_to_69[region] = INTEG ( Aging_64_to_65[region] - Aging_69_to_70[region] - dying_65_to_69[region] , Cohort_65_to_69_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_65_to_69"]
    idx2 = fcol_in_mdf["Aging_64_to_65"]
    idx3 = fcol_in_mdf["Aging_69_to_70"]
    idx4 = fcol_in_mdf["dying_65_to_69"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_70_to_74[region] = INTEG ( Aging_69_to_70[region] - Aging_74_to_75[region] - dying_70_to_74[region] , Cohort_70_to_74_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_70_to_74"]
    idx2 = fcol_in_mdf["Aging_69_to_70"]
    idx3 = fcol_in_mdf["Aging_74_to_75"]
    idx4 = fcol_in_mdf["dying_70_to_74"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_75_to_79[region] = INTEG ( Aging_74_to_75[region] - Aging_79_to_80[region] - dying_75_to_79[region] , Cohort_75_to_79_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_75_to_79"]
    idx2 = fcol_in_mdf["Aging_74_to_75"]
    idx3 = fcol_in_mdf["Aging_79_to_80"]
    idx4 = fcol_in_mdf["dying_75_to_79"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_80_to_84[region] = INTEG ( Aging_79_to_80[region] - Aging_84_to_85[region] - dying_80_to_84[region] , Cohort_80_to_84_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_80_to_84"]
    idx2 = fcol_in_mdf["Aging_79_to_80"]
    idx3 = fcol_in_mdf["Aging_84_to_85"]
    idx4 = fcol_in_mdf["dying_80_to_84"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_85_to_89[region] = INTEG ( Aging_84_to_85[region] - Aging_89_to_90[region] - dying_85_to_89[region] , Cohort_85_to_89_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_85_to_89"]
    idx2 = fcol_in_mdf["Aging_84_to_85"]
    idx3 = fcol_in_mdf["Aging_89_to_90"]
    idx4 = fcol_in_mdf["dying_85_to_89"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_90_to_94[region] = INTEG ( Aging_89_to_90[region] - Aging_95_to_95plus[region] - dying_90_to_94[region] , Cohort_90_to_94_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_90_to_94"]
    idx2 = fcol_in_mdf["Aging_89_to_90"]
    idx3 = fcol_in_mdf["Aging_95_to_95plus"]
    idx4 = fcol_in_mdf["dying_90_to_94"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Cohort_95p[region] = INTEG ( Aging_95_to_95plus[region] - dying_95p[region] , Cohort_95p_in_1980[region] )
    idx1 = fcol_in_mdf["Cohort_95p"]
    idx2 = fcol_in_mdf["Aging_95_to_95plus"]
    idx3 = fcol_in_mdf["dying_95p"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Cohort_60plus[region] = Cohort_60_to_64[region] + Cohort_65_to_69[region] + Cohort_70_to_74[region] + Cohort_75_to_79[region] + Cohort_80_to_84[region] + Cohort_85_to_89[region] + Cohort_90_to_94[region] + Cohort_95p[region]
    idxlhs = fcol_in_mdf["Cohort_60plus"]
    idx1 = fcol_in_mdf["Cohort_60_to_64"]
    idx2 = fcol_in_mdf["Cohort_65_to_69"]
    idx3 = fcol_in_mdf["Cohort_70_to_74"]
    idx4 = fcol_in_mdf["Cohort_75_to_79"]
    idx5 = fcol_in_mdf["Cohort_80_to_84"]
    idx6 = fcol_in_mdf["Cohort_85_to_89"]
    idx7 = fcol_in_mdf["Cohort_90_to_94"]
    idx8 = fcol_in_mdf["Cohort_95p"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
        + mdf[rowi, idx7 + j]
        + mdf[rowi, idx8 + j]
      )

    # Population[region] = Cohort_0_to_20[region] + Cohort_20_to_40[region] + Cohort_40_to_60[region] + Cohort_60plus[region]
    idxlhs = fcol_in_mdf["Population"]
    idx1 = fcol_in_mdf["Cohort_0_to_20"]
    idx2 = fcol_in_mdf["Cohort_20_to_40"]
    idx3 = fcol_in_mdf["Cohort_40_to_60"]
    idx4 = fcol_in_mdf["Cohort_60plus"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
      )

    # GDPpp_model[region] = GDP_model[region] / Population[region] * UNIT_conv_to_k2017pppUSD_pr_py[region]
    idxlhs = fcol_in_mdf["GDPpp_model"]
    idx1 = fcol_in_mdf["GDP_model"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] * UNIT_conv_to_k2017pppUSD_pr_py
      )

    # GDPpp_USED[region] = IF_THEN_ELSE ( Switch_GDP_hist_1_mod_2 == 1 , GDPpp_H_exo , GDPpp_model )
    idxlhs = fcol_in_mdf["GDPpp_USED"]
    idx1 = fcol_in_mdf["GDPpp_H_exo"]
    idx2 = fcol_in_mdf["GDPpp_model"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        Switch_GDP_hist_1_mod_2 == 1, mdf[rowi, idx1 + j], mdf[rowi, idx2 + j]
      )

    # cereal_dmd_CN = cereal_dmd_CN_a * LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) + cereal_dmd_CN_b
    idxlhs = fcol_in_mdf["cereal_dmd_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      cereal_dmd_CN_a * math.log(mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl)
      + cereal_dmd_CN_b
    )

    # cereal_dmd_func_pp[region] = cereal_dmd_func_pp_L[region] / ( 1 + math.exp ( - cereal_dmd_func_pp_k[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl - cereal_dmd_func_pp_x0[region] ) ) )
    idxlhs = fcol_in_mdf["cereal_dmd_func_pp"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = cereal_dmd_func_pp_L[j] / (
        1
        + math.exp(
          -cereal_dmd_func_pp_k[j]
          * (
            mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl - cereal_dmd_func_pp_x0[j]
          )
        )
      )

    # cereal_dmd_pp[region] = IF_THEN_ELSE ( j==2 , cereal_dmd_CN , cereal_dmd_func_pp )
    idxlhs = fcol_in_mdf["cereal_dmd_pp"]
    idx1 = fcol_in_mdf["cereal_dmd_CN"]
    idx2 = fcol_in_mdf["cereal_dmd_func_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 2, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # cereal_dmd_food_pp[region] = cereal_dmd_pp[region] * UNIT_conv_to_kg_crop_ppy
    idxlhs = fcol_in_mdf["cereal_dmd_food_pp"]
    idx1 = fcol_in_mdf["cereal_dmd_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_kg_crop_ppy

    # cereal_dmd_food_pp_consumed[region] = cereal_dmd_food_pp[region] * ( 1 - Food_wasted_in_1980[region] )
    idxlhs = fcol_in_mdf["cereal_dmd_food_pp_consumed"]
    idx1 = fcol_in_mdf["cereal_dmd_food_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - Food_wasted_in_1980[j])

    # FWRP_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , FWRP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FWRP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FWRP_R1_via_Excel , FWRP_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FWRP_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FWRP_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FWRP_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FWRP_R1_via_Excel[j], FWRP_policy_Min
          ),     ),   )

    # Social_trust[region] = INTEG ( Change_in_social_trust[region] , Social_trust_in_1980 )
    idx1 = fcol_in_mdf["Social_trust"]
    idx2 = fcol_in_mdf["Change_in_social_trust"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Eff_of_social_trust_on_reform_willingness_and_social_tension[region] = 1 + SoE_of_social_trust_on_reform * ( Social_trust[region] / Social_trust_in_1980 - 1 )
    idxlhs = fcol_in_mdf["Eff_of_social_trust_on_reform_willingness_and_social_tension"]
    idx1 = fcol_in_mdf["Social_trust"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + SoE_of_social_trust_on_reform * (
        mdf[rowi, idx1 + j] / Social_trust_in_1980 - 1
      )

    # Perceived_RoC_in_Living_conditions_index_with_env_damage[region] = SMOOTHI ( RoC_in_Living_conditions_index_with_env_damage[region] , Social_tension_perception_delay , 0 )
    idx1 = fcol_in_mdf["Perceived_RoC_in_Living_conditions_index_with_env_damage"]
    idx2 = fcol_in_mdf["RoC_in_Living_conditions_index_with_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Social_tension_perception_delay
        * dt
      )

    # Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust[region] = SMOOTHI ( Scaled_Effect_of_poverty_on_social_tension_and_trust[region] , Time_for_poverty_to_affect_social_tension_and_trust , 1 )
    idx1 = fcol_in_mdf["Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust"
    ]
    idx2 = fcol_in_mdf["Scaled_Effect_of_poverty_on_social_tension_and_trust"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_poverty_to_affect_social_tension_and_trust
        * dt
      )

    # Indicated_Social_tension_index[region] = 1 + ( 1 / ( 1 + Perceived_RoC_in_Living_conditions_index_with_env_damage[region] ) - 1 ) * Scaling_factor_for_amplitude_in_RoC_in_living_conditions_index * Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust[region]
    idxlhs = fcol_in_mdf["Indicated_Social_tension_index"]
    idx1 = fcol_in_mdf["Perceived_RoC_in_Living_conditions_index_with_env_damage"]
    idx2 = fcol_in_mdf["Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + (1 / (1 + mdf[rowi, idx1 + j]) - 1)
        * Scaling_factor_for_amplitude_in_RoC_in_living_conditions_index
        * mdf[rowi, idx2 + j]
      )

    # Actual_Social_tension_index[region] = WITH LOOKUP ( Indicated_Social_tension_index[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0.1 ) , ( 0.25 , 0.13 ) , ( 0.5 , 0.23 ) , ( 0.75 , 0.5 ) , ( 1 , 1 ) , ( 1.25 , 1.5 ) , ( 1.5 , 1.85 ) , ( 1.75 , 1.95 ) , ( 2 , 2 ) ) )
    tabidx = ftab_in_d_table["Actual_Social_tension_index"]  # fetch the correct table
    idx2 = fcol_in_mdf["Actual_Social_tension_index"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Indicated_Social_tension_index"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Smoothed_Social_tension_index_ie_rate_of_progress[region] = SMOOTH ( Actual_Social_tension_index[region] , Time_to_smooth_social_tension_index )
    idx1 = fcol_in_mdf["Smoothed_Social_tension_index_ie_rate_of_progress"]
    idx2 = fcol_in_mdf["Actual_Social_tension_index"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_social_tension_index
        * dt
      )

    # Smoothed_Social_tension_index_with_trust_effect[region] = Smoothed_Social_tension_index_ie_rate_of_progress[region] / Eff_of_social_trust_on_reform_willingness_and_social_tension[region]
    idxlhs = fcol_in_mdf["Smoothed_Social_tension_index_with_trust_effect"]
    idx1 = fcol_in_mdf["Smoothed_Social_tension_index_ie_rate_of_progress"]
    idx2 = fcol_in_mdf["Eff_of_social_trust_on_reform_willingness_and_social_tension"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Indicated_effect_of_social_tension_on_reform_willingness[region] = ( Smoothed_Social_tension_index_with_trust_effect[region] - 1 ) * Strength_of_the_impact_of_social_tension_on_reform_willingness
    idxlhs = fcol_in_mdf["Indicated_effect_of_social_tension_on_reform_willingness"]
    idx1 = fcol_in_mdf["Smoothed_Social_tension_index_with_trust_effect"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - 1) * Strength_of_the_impact_of_social_tension_on_reform_willingness

    # Effect_of_social_tension_on_reform_willingness[region] = Indicated_effect_of_social_tension_on_reform_willingness[region] + 1
    idxlhs = fcol_in_mdf["Effect_of_social_tension_on_reform_willingness"]
    idx1 = fcol_in_mdf["Indicated_effect_of_social_tension_on_reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + 1

    # Indicated_reform_willingness[region] = Eff_of_social_trust_on_reform_willingness_and_social_tension[region] / Effect_of_social_tension_on_reform_willingness[region]
    idxlhs = fcol_in_mdf["Indicated_reform_willingness"]
    idx1 = fcol_in_mdf["Eff_of_social_trust_on_reform_willingness_and_social_tension"]
    idx2 = fcol_in_mdf["Effect_of_social_tension_on_reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Indicated_reform_willingness_at_policy_start_year[region] = SAMPLE IF TRUE ( zeit = Policy_start_year , Indicated_reform_willingness[region] , 1 )
    idxlhs = fcol_in_mdf["Indicated_reform_willingness_at_policy_start_year"]
    idx1 = fcol_in_mdf["Indicated_reform_willingness"]
    for i in range(0, 10):
      mdf[rowi, idxlhs + i] = SAMPLE_IF_TRUE(zeit, Policy_start_year, mdf[rowi, idx1 + i], 1, i)

    # Reform_willingness_scaled_to_today[region] = IF_THEN_ELSE ( zeit < Policy_start_year , 1 , Indicated_reform_willingness / Indicated_reform_willingness_at_policy_start_year )
    idxlhs = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    idx1 = fcol_in_mdf["Indicated_reform_willingness"]
    idx2 = fcol_in_mdf["Indicated_reform_willingness_at_policy_start_year"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(zeit < Policy_start_year, 1, mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j])

    # Smoothed_Reform_willingness[region] = SMOOTH3 ( Reform_willingness_scaled_to_today[region] , Time_to_adjust_reform_willingness )
    idxin = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness_2"]
    idx1 = fcol_in_mdf["Smoothed_Reform_willingness_1"]
    idxout = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_adjust_reform_willingness / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_adjust_reform_willingness / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_adjust_reform_willingness / 3)
        * dt
      )

    # Actual_inequality_index_higher_is_more_unequal[region] = SMOOTH3I ( Indicated_inequality_index_with_tax[region] , Time_for_inequality_to_impact_wellbeing , 1 )
    idxin = fcol_in_mdf["Indicated_inequality_index_with_tax"]
    idx2 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_2"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_1"]
    idxout = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_for_inequality_to_impact_wellbeing / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_for_inequality_to_impact_wellbeing / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_for_inequality_to_impact_wellbeing / 3)
        * dt
      )

    # Inequality_effect_on_energy_TA[region] = 1 + ( Actual_inequality_index_higher_is_more_unequal[region] - 1 ) * Strength_of_inequality_effect_on_energy_TA
    idxlhs = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 + (mdf[rowi, idx1 + j] - 1) * Strength_of_inequality_effect_on_energy_TA
      )

    # Effective_purchasing_power[region] = SMOOTHI ( Consumption_and_investment[region] , Demand_adjustment_time , Demand_in_1980[region] )
    idx1 = fcol_in_mdf["Effective_purchasing_power"]
    idx2 = fcol_in_mdf["Consumption_and_investment"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Demand_adjustment_time
        * dt
      )

    # Delivery_delay_index[region] = INTEG ( Change_in_delivery_delay_index[region] , 1 )
    idx1 = fcol_in_mdf["Delivery_delay_index"]
    idx2 = fcol_in_mdf["Change_in_delivery_delay_index"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Sales[region] = ( Effective_purchasing_power[region] / ( Delivery_delay_index[region] / Delivery_delay_index_in_1980[region] ) )
    idxlhs = fcol_in_mdf["Sales"]
    idx1 = fcol_in_mdf["Effective_purchasing_power"]
    idx2 = fcol_in_mdf["Delivery_delay_index"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        mdf[rowi, idx2 + j] / Delivery_delay_index_in_1980
      )

    # National_income[region] = Sales[region]
    idxlhs = fcol_in_mdf["National_income"]
    idx1 = fcol_in_mdf["Sales"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Owner_power_or_weakness[region] = INTEG ( - Change_in_Owner_power[region] , Owner_power_in_1980 )
    idx1 = fcol_in_mdf["Owner_power_or_weakness"]
    idx2 = fcol_in_mdf["Change_in_Owner_power"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (-mdf[rowi - 1, idx2 + j]) * dt

    # Worker_share_of_output[region] = ( ( Owner_power_or_weakness[region] + 1 ) / Worker_power_scaling_factor ) + Worker_power_scaling_factor_reference
    idxlhs = fcol_in_mdf["Worker_share_of_output"]
    idx1 = fcol_in_mdf["Owner_power_or_weakness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] + 1) / Worker_power_scaling_factor
      ) + Worker_power_scaling_factor_reference

    # StrUP_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , StrUP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , StrUP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , StrUP_R1_via_Excel , StrUP_policy_Min ) ) )
    idxlhs = fcol_in_mdf["StrUP_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     StrUP_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       StrUP_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, StrUP_R1_via_Excel[j], StrUP_policy_Min
          ),     ),   )

    # StrUP_policy_with_RW[region] = StrUP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["StrUP_policy_with_RW"]
    idx1 = fcol_in_mdf["StrUP_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # StrUP_pol_div_100[region] = MIN ( StrUP_policy_Max , MAX ( StrUP_policy_Min , StrUP_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["StrUP_pol_div_100"]
    idx1 = fcol_in_mdf["StrUP_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(StrUP_policy_Max, max(StrUP_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # StrUP_policy[region] = SMOOTH3 ( StrUP_pol_div_100[region] , StrUP_Time_to_implement_policy )
    idxin = fcol_in_mdf["StrUP_pol_div_100"]
    idx2 = fcol_in_mdf["StrUP_policy_2"]
    idx1 = fcol_in_mdf["StrUP_policy_1"]
    idxout = fcol_in_mdf["StrUP_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (StrUP_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (StrUP_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (StrUP_Time_to_implement_policy / 3)
        * dt
      )

    # StrU_mult_used[region] = 1 + StrUP_policy[region]
    idxlhs = fcol_in_mdf["StrU_mult_used"]
    idx1 = fcol_in_mdf["StrUP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + mdf[rowi, idx1 + j]

    # Worker_share_of_output_with_policy[region] = Worker_share_of_output[region] * StrU_mult_used[region]
    idxlhs = fcol_in_mdf["Worker_share_of_output_with_policy"]
    idx1 = fcol_in_mdf["Worker_share_of_output"]
    idx2 = fcol_in_mdf["StrU_mult_used"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Unemployed[region] = INTEG ( Entering_the_labor_pool[region] + Loosing_a_job[region] - Getting_a_job[region] - Leaving_the_labor_pool[region] , Unemployment_in_1980[region] )
    idx1 = fcol_in_mdf["Unemployed"]
    idx2 = fcol_in_mdf["Entering_the_labor_pool"]
    idx3 = fcol_in_mdf["Loosing_a_job"]
    idx4 = fcol_in_mdf["Getting_a_job"]
    idx5 = fcol_in_mdf["Leaving_the_labor_pool"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (
          mdf[rowi - 1, idx2 + j]
          + mdf[rowi - 1, idx3 + j]
          - mdf[rowi - 1, idx4 + j]
          - mdf[rowi - 1, idx5 + j]
        )
        * dt
      )

    # Unemployment_rate[region] = Unemployed[region] / Employed[region]
    idxlhs = fcol_in_mdf["Unemployment_rate"]
    idx1 = fcol_in_mdf["Unemployed"]
    idx2 = fcol_in_mdf["Employed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Unemployment_ratio[region] = Unemployment_rate[region] / Societal_unemployment_rate_norm
    idxlhs = fcol_in_mdf["Unemployment_ratio"]
    idx1 = fcol_in_mdf["Unemployment_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Societal_unemployment_rate_norm

    # Effect_of_unemployment_ratio_on_Worker_share_of_output[region] = 1 + SoE_of_unemployment_ratio_on_WSO * ( Unemployment_ratio[region] - 1 )
    idxlhs = fcol_in_mdf["Effect_of_unemployment_ratio_on_Worker_share_of_output"]
    idx1 = fcol_in_mdf["Unemployment_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + SoE_of_unemployment_ratio_on_WSO * (
        mdf[rowi, idx1 + j] - 1
      )

    # Worker_share_of_output_with_unemployment_effect[region] = Worker_share_of_output_with_policy[region] * Effect_of_unemployment_ratio_on_Worker_share_of_output[region]
    idxlhs = fcol_in_mdf["Worker_share_of_output_with_unemployment_effect"]
    idx1 = fcol_in_mdf["Worker_share_of_output_with_policy"]
    idx2 = fcol_in_mdf["Effect_of_unemployment_ratio_on_Worker_share_of_output"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Owner_income[region] = National_income[region] * ( 1 - Worker_share_of_output_with_unemployment_effect[region] )
    idxlhs = fcol_in_mdf["Owner_income"]
    idx1 = fcol_in_mdf["National_income"]
    idx2 = fcol_in_mdf["Worker_share_of_output_with_unemployment_effect"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # IOITR_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , IOITR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , IOITR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , IOITR_R1_via_Excel , IOITR_policy_Min ) ) )
    idxlhs = fcol_in_mdf["IOITR_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     IOITR_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       IOITR_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, IOITR_R1_via_Excel[j], IOITR_policy_Min
          ),     ),   )

    # IOITR_policy_with_RW[region] = IOITR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["IOITR_policy_with_RW"]
    idx1 = fcol_in_mdf["IOITR_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # IOITR_pol_div_100[region] = MIN ( IOITR_policy_Max , MAX ( IOITR_policy_Min , IOITR_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["IOITR_pol_div_100"]
    idx1 = fcol_in_mdf["IOITR_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(IOITR_policy_Max, max(IOITR_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # IOITR_policy[region] = SMOOTH3 ( IOITR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["IOITR_pol_div_100"]
    idx2 = fcol_in_mdf["IOITR_policy_2"]
    idx1 = fcol_in_mdf["IOITR_policy_1"]
    idxout = fcol_in_mdf["IOITR_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Life_expectancy_at_birth_as_f_of_GDPpp[region] = Life_expec_a[region] + Life_expec_b[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl )
    idxlhs = fcol_in_mdf["Life_expectancy_at_birth_as_f_of_GDPpp"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Life_expec_a[j] + Life_expec_b[j] * math.log(
        mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl
      )

    # Life_expectancy_at_birth[region] = SMOOTH ( Life_expectancy_at_birth_as_f_of_GDPpp[region] , Time_to_affect_life_expectancy )
    idx1 = fcol_in_mdf["Life_expectancy_at_birth"]
    idx2 = fcol_in_mdf["Life_expectancy_at_birth_as_f_of_GDPpp"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_affect_life_expectancy
        * dt
      )

    # Pension_age[region] = IF_THEN_ELSE ( Life_expectancy_at_birth < Life_expectancy_at_birth_in_1980 , Pension_age_in_1980 , Pension_age_in_1980 + SoE_of_LE_on_Pension_age * ( Life_expectancy_at_birth - Life_expectancy_at_birth_in_1980 ) )
    idxlhs = fcol_in_mdf["Pension_age"]
    idx1 = fcol_in_mdf["Life_expectancy_at_birth"]
    idx2 = fcol_in_mdf["Life_expectancy_at_birth"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < Life_expectancy_at_birth_in_1980[j],     Pension_age_in_1980[j],     Pension_age_in_1980[j]
        + SoE_of_LE_on_Pension_age[j]
        * (mdf[rowi, idx2 + j] - Life_expectancy_at_birth_in_1980[j]),   )

    # Theoretical_fraction_of_people_60plus_drawing_a_pension[region] = MAX ( 0 , ( Max_age - Pension_age[region] ) / Years_between_60_and_max_age )
    idxlhs = fcol_in_mdf["Theoretical_fraction_of_people_60plus_drawing_a_pension"]
    idx1 = fcol_in_mdf["Pension_age"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0, (Max_age - mdf[rowi, idx1 + j]) / Years_between_60_and_max_age
      )

    # People_drawing_a_pension[region] =  Cohort_60plus * IF_THEN_ELSE ( Pension_age < 60 , 1 , Theoretical_fraction_of_people_60plus_drawing_a_pension )
    idxlhs = fcol_in_mdf["People_drawing_a_pension"]
    idx1 = fcol_in_mdf["Cohort_60plus"]
    idx2 = fcol_in_mdf["Pension_age"]
    idx3 = fcol_in_mdf["Theoretical_fraction_of_people_60plus_drawing_a_pension"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * IF_THEN_ELSE(
        mdf[rowi, idx2 + j] < 60, 1, mdf[rowi, idx3 + j]
      )

    # SGMP_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , SGMP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , SGMP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , SGMP_R1_via_Excel , SGMP_policy_Min ) ) )
    idxlhs = fcol_in_mdf["SGMP_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     SGMP_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       SGMP_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, SGMP_R1_via_Excel[j], SGMP_policy_Min
          ),     ),   )

    # SGMP_policy_with_RW[region] = SGMP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["SGMP_policy_with_RW"]
    idx1 = fcol_in_mdf["SGMP_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # SGMP_pol_div_100[region] = MIN ( SGMP_policy_Max , MAX ( SGMP_policy_Min , SGMP_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["SGMP_pol_div_100"]
    idx1 = fcol_in_mdf["SGMP_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(SGMP_policy_Max, max(SGMP_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # SGMP_policy[region] = SMOOTH3 ( SGMP_pol_div_100[region] , SGMP_Time_to_implement_policy )
    idxin = fcol_in_mdf["SGMP_pol_div_100"]
    idx2 = fcol_in_mdf["SGMP_policy_2"]
    idx1 = fcol_in_mdf["SGMP_policy_1"]
    idxout = fcol_in_mdf["SGMP_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (SGMP_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (SGMP_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (SGMP_Time_to_implement_policy / 3)
        * dt
      )

    # State_guaranteed_minimum_pension[region] = People_drawing_a_pension[region] * GDPpp_USED[region] * UNIT_conv_to_kUSDpp * SGMP_policy[region]
    idxlhs = fcol_in_mdf["State_guaranteed_minimum_pension"]
    idx1 = fcol_in_mdf["People_drawing_a_pension"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    idx3 = fcol_in_mdf["SGMP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * UNIT_conv_to_kUSDpp
        * mdf[rowi, idx3 + j]
      )

    # Additional_tax_rate_needed_to_pay_for_SGMP[region] = State_guaranteed_minimum_pension[region] / Owner_income[region]
    idxlhs = fcol_in_mdf["Additional_tax_rate_needed_to_pay_for_SGMP"]
    idx1 = fcol_in_mdf["State_guaranteed_minimum_pension"]
    idx2 = fcol_in_mdf["Owner_income"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Income_tax_rate_owners_after_GITx[region] =  Income_tax_rate_ie_fraction_owners_before_policies + IOITR_policy + IF_THEN_ELSE ( zeit > Policy_start_year , Additional_tax_rate_needed_to_pay_for_SGMP , 0 )
    idxlhs = fcol_in_mdf["Income_tax_rate_owners_after_GITx"]
    idx1 = fcol_in_mdf["IOITR_policy"]
    idx2 = fcol_in_mdf["Additional_tax_rate_needed_to_pay_for_SGMP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Income_tax_rate_ie_fraction_owners_before_policies
        + mdf[rowi, idx1 + j]
        + IF_THEN_ELSE(zeit > Policy_start_year, mdf[rowi, idx2 + j], 0)
      )

    # Income_tax_rate[region] = Income_tax_rate_owners_after_GITx[region]
    idxlhs = fcol_in_mdf["Income_tax_rate"]
    idx1 = fcol_in_mdf["Income_tax_rate_owners_after_GITx"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # XtaxEmp_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , XtaxEmp_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , XtaxEmp_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , XtaxEmp_R1_via_Excel , XtaxRateEmp_policy_Min ) ) )
    idxlhs = fcol_in_mdf["XtaxEmp_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     XtaxEmp_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       XtaxEmp_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, XtaxEmp_R1_via_Excel[j], XtaxRateEmp_policy_Min
          ),     ),   )

    # XtaxEmp_policy_with_RW[region] = XtaxEmp_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["XtaxEmp_policy_with_RW"]
    idx1 = fcol_in_mdf["XtaxEmp_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # XtaxEmp_pol_div_100[region] = MIN ( XtaxRateEmp_policy_Max , MAX ( XtaxRateEmp_policy_Min , XtaxEmp_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["XtaxEmp_pol_div_100"]
    idx1 = fcol_in_mdf["XtaxEmp_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(XtaxRateEmp_policy_Max, max(XtaxRateEmp_policy_Min, mdf[rowi, idx1 + j]))
        / 100
      )

    # XtaxRateEmp_policy[region] = SMOOTH3 ( XtaxEmp_pol_div_100[region] , XtaxRateEmp_Time_to_implement_policy )
    idxin = fcol_in_mdf["XtaxEmp_pol_div_100"]
    idx2 = fcol_in_mdf["XtaxRateEmp_policy_2"]
    idx1 = fcol_in_mdf["XtaxRateEmp_policy_1"]
    idxout = fcol_in_mdf["XtaxRateEmp_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (XtaxRateEmp_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (XtaxRateEmp_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (XtaxRateEmp_Time_to_implement_policy / 3)
        * dt
      )

    # Female_leadership_spending[region] = National_income[region] * XtaxRateEmp_policy[region]
    idxlhs = fcol_in_mdf["Female_leadership_spending"]
    idx1 = fcol_in_mdf["National_income"]
    idx2 = fcol_in_mdf["XtaxRateEmp_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Extra_policy_taxes[region] = Female_leadership_spending[region]
    idxlhs = fcol_in_mdf["Extra_policy_taxes"]
    idx1 = fcol_in_mdf["Female_leadership_spending"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # XtaxFrac_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , XtaxFrac_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , XtaxFrac_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , XtaxFrac_R1_via_Excel , Xtaxfrac_policy_Min ) ) )
    idxlhs = fcol_in_mdf["XtaxFrac_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     XtaxFrac_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       XtaxFrac_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, XtaxFrac_R1_via_Excel[j], Xtaxfrac_policy_Min
          ),     ),   )

    # XtaxFrac_policy_with_RW[region] = Xtaxfrac_policy_Min + ( XtaxFrac_rounds_via_Excel[region] - Xtaxfrac_policy_Min ) * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["XtaxFrac_policy_with_RW"]
    idx1 = fcol_in_mdf["XtaxFrac_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Xtaxfrac_policy_Min
        + (mdf[rowi, idx1 + j] - Xtaxfrac_policy_Min) * mdf[rowi, idx2 + j]
      )

    # XtaxFrac_pol_div_100[region] = MIN ( Xtaxfrac_policy_Max , MAX ( Xtaxfrac_policy_Min , XtaxFrac_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["XtaxFrac_pol_div_100"]
    idx1 = fcol_in_mdf["XtaxFrac_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(Xtaxfrac_policy_Max, max(Xtaxfrac_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # Xtaxfrac_policy[region] = SMOOTH3 ( XtaxFrac_pol_div_100[region] , Xtaxfrac_Time_to_implement_policy )
    idxin = fcol_in_mdf["XtaxFrac_pol_div_100"]
    idx2 = fcol_in_mdf["Xtaxfrac_policy_2"]
    idx1 = fcol_in_mdf["Xtaxfrac_policy_1"]
    idxout = fcol_in_mdf["Xtaxfrac_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Xtaxfrac_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Xtaxfrac_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Xtaxfrac_Time_to_implement_policy / 3)
        * dt
      )

    # Fraction_of_extra_taxes_paid_by_owners[region] = Xtaxfrac_policy[region]
    idxlhs = fcol_in_mdf["Fraction_of_extra_taxes_paid_by_owners"]
    idx1 = fcol_in_mdf["Xtaxfrac_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Extra_policy_taxes_paid_by_owners[region] = Extra_policy_taxes[region] * Fraction_of_extra_taxes_paid_by_owners[region]
    idxlhs = fcol_in_mdf["Extra_policy_taxes_paid_by_owners"]
    idx1 = fcol_in_mdf["Extra_policy_taxes"]
    idx2 = fcol_in_mdf["Fraction_of_extra_taxes_paid_by_owners"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Income_and_policy_taxes_paid_by_owners[region] = Owner_income[region] * Income_tax_rate[region] + Extra_policy_taxes_paid_by_owners[region]
    idxlhs = fcol_in_mdf["Income_and_policy_taxes_paid_by_owners"]
    idx1 = fcol_in_mdf["Owner_income"]
    idx2 = fcol_in_mdf["Income_tax_rate"]
    idx3 = fcol_in_mdf["Extra_policy_taxes_paid_by_owners"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # Worker_income[region] = National_income[region] * Worker_share_of_output_with_unemployment_effect[region] + State_guaranteed_minimum_pension[region]
    idxlhs = fcol_in_mdf["Worker_income"]
    idx1 = fcol_in_mdf["National_income"]
    idx2 = fcol_in_mdf["Worker_share_of_output_with_unemployment_effect"]
    idx3 = fcol_in_mdf["State_guaranteed_minimum_pension"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # IWITR_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , IWITR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , IWITR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , IWITR_R1_via_Excel , IWITR_policy_Min ) ) )
    idxlhs = fcol_in_mdf["IWITR_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     IWITR_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       IWITR_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, IWITR_R1_via_Excel[j], IWITR_policy_Min
          ),     ),   )

    # IWITR_policy_with_RW[region] = IWITR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["IWITR_policy_with_RW"]
    idx1 = fcol_in_mdf["IWITR_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # IWITR_pol_div_100[region] = MIN ( IWITR_policy_Max , MAX ( IWITR_policy_Min , IWITR_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["IWITR_pol_div_100"]
    idx1 = fcol_in_mdf["IWITR_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(IWITR_policy_Max, max(IWITR_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # IWITR_policy[region] = SMOOTH3 ( IWITR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["IWITR_pol_div_100"]
    idx2 = fcol_in_mdf["IWITR_policy_2"]
    idx1 = fcol_in_mdf["IWITR_policy_1"]
    idxout = fcol_in_mdf["IWITR_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Income_tax_rate_workers_after_GITx[region] = Income_tax_rate_ie_fraction_for_workers_before_policies + IWITR_policy[region]
    idxlhs = fcol_in_mdf["Income_tax_rate_workers_after_GITx"]
    idx1 = fcol_in_mdf["IWITR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Income_tax_rate_ie_fraction_for_workers_before_policies + mdf[rowi, idx1 + j]
      )

    # Income_tax_rate_workers[region] = Income_tax_rate_workers_after_GITx[region]
    idxlhs = fcol_in_mdf["Income_tax_rate_workers"]
    idx1 = fcol_in_mdf["Income_tax_rate_workers_after_GITx"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Extra_policy_taxes_paid_by_workers[region] = Extra_policy_taxes[region] * ( 1 - Fraction_of_extra_taxes_paid_by_owners[region] )
    idxlhs = fcol_in_mdf["Extra_policy_taxes_paid_by_workers"]
    idx1 = fcol_in_mdf["Extra_policy_taxes"]
    idx2 = fcol_in_mdf["Fraction_of_extra_taxes_paid_by_owners"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # Worker_income_and_policy_taxes[region] = Worker_income[region] * Income_tax_rate_workers[region] + Extra_policy_taxes_paid_by_workers[region]
    idxlhs = fcol_in_mdf["Worker_income_and_policy_taxes"]
    idx1 = fcol_in_mdf["Worker_income"]
    idx2 = fcol_in_mdf["Income_tax_rate_workers"]
    idx3 = fcol_in_mdf["Extra_policy_taxes_paid_by_workers"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # Owner_income_after_tax_but_before_lending_transactions[region] = Owner_income[region] - Income_and_policy_taxes_paid_by_owners[region]
    idxlhs = fcol_in_mdf["Owner_income_after_tax_but_before_lending_transactions"]
    idx1 = fcol_in_mdf["Owner_income"]
    idx2 = fcol_in_mdf["Income_and_policy_taxes_paid_by_owners"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Owner_cash_inflow_seasonally_adjusted[region] = SMOOTHI ( Owner_cash_inflow_with_lending_transactions[region] , Time_to_adjust_owners_budget , Owner_income_in_1980[region] )
    idx1 = fcol_in_mdf["Owner_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Owner_cash_inflow_with_lending_transactions"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_adjust_owners_budget
        * dt
      )

    # Future_WACC_fraction[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Indicated_WACC_fraction , 0 )
    idxlhs = fcol_in_mdf["Future_WACC_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit > Policy_start_year, Indicated_WACC_fraction[j], 0
      )

    # WACC_fraction[region] = SMOOTH3 ( Future_WACC_fraction[region] , Time_to_ease_in_wealth_accumulation )
    idxin = fcol_in_mdf["Future_WACC_fraction"]
    idx2 = fcol_in_mdf["WACC_fraction_2"]
    idx1 = fcol_in_mdf["WACC_fraction_1"]
    idxout = fcol_in_mdf["WACC_fraction"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_ease_in_wealth_accumulation / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_ease_in_wealth_accumulation / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_ease_in_wealth_accumulation / 3)
        * dt
      )

    # Owner_saving_fraction[region] = INTEG ( Net_change_in_OSF[region] , OSF_in_1980[region] )
    idx1 = fcol_in_mdf["Owner_saving_fraction"]
    idx2 = fcol_in_mdf["Net_change_in_OSF"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation[region] = 1 - Owner_saving_fraction[region]
    idxlhs = fcol_in_mdf["Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation"
    ]
    idx1 = fcol_in_mdf["Owner_saving_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - mdf[rowi, idx1 + j]

    # Owner_consumption_fraction[region] = ( 1 - WACC_fraction[region] ) * Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation[region]
    idxlhs = fcol_in_mdf["Owner_consumption_fraction"]
    idx1 = fcol_in_mdf["WACC_fraction"]
    idx2 = fcol_in_mdf["Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 - mdf[rowi, idx1 + j]) * mdf[rowi, idx2 + j]

    # Owner_consumption[region] = Owner_cash_inflow_seasonally_adjusted[region] * Owner_consumption_fraction[region]
    idxlhs = fcol_in_mdf["Owner_consumption"]
    idx1 = fcol_in_mdf["Owner_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Owner_consumption_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Worker_cash_inflow_seasonally_adjusted[region] = SMOOTHI ( Worker_cash_inflow[region] , Time_to_adjust_worker_consumption_pattern , Worker_income_after_tax_in_1980[region] )
    idx1 = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Worker_cash_inflow"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_adjust_worker_consumption_pattern
        * dt
      )

    # Worker_consumption_demand[region] = Worker_cash_inflow_seasonally_adjusted[region] * Worker_consumption_fraction
    idxlhs = fcol_in_mdf["Worker_consumption_demand"]
    idx1 = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Worker_consumption_fraction

    # End_user_consumption_to_be_taxed[region] = Owner_consumption[region] + Worker_consumption_demand[region]
    idxlhs = fcol_in_mdf["End_user_consumption_to_be_taxed"]
    idx1 = fcol_in_mdf["Owner_consumption"]
    idx2 = fcol_in_mdf["Worker_consumption_demand"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # ICTR_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , ICTR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , ICTR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , ICTR_R1_via_Excel , ICTR_policy_Min ) ) )
    idxlhs = fcol_in_mdf["ICTR_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     ICTR_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       ICTR_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, ICTR_R1_via_Excel[j], ICTR_policy_Min
          ),     ),   )

    # ICTR_policy_with_RW[region] = ICTR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["ICTR_policy_with_RW"]
    idx1 = fcol_in_mdf["ICTR_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # ICTR_pol_div_100[region] = MIN ( ICTR_policy_Max , MAX ( ICTR_policy_Min , ICTR_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["ICTR_pol_div_100"]
    idx1 = fcol_in_mdf["ICTR_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(ICTR_policy_Max, max(ICTR_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # ICTR_policy[region] = SMOOTH3 ( ICTR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["ICTR_pol_div_100"]
    idx2 = fcol_in_mdf["ICTR_policy_2"]
    idx1 = fcol_in_mdf["ICTR_policy_1"]
    idxout = fcol_in_mdf["ICTR_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Consumption_taxes[region] = End_user_consumption_to_be_taxed[region] * ( Consumption_tax_rate_ie_fraction + ICTR_policy[region] )
    idxlhs = fcol_in_mdf["Consumption_taxes"]
    idx1 = fcol_in_mdf["End_user_consumption_to_be_taxed"]
    idx2 = fcol_in_mdf["ICTR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (
        Consumption_tax_rate_ie_fraction + mdf[rowi, idx2 + j]
      )

    # Consumption_taxes_last_year[region] = SMOOTHI ( Consumption_taxes[region] , One_year , Consumption_taxes_in_1980[region] )
    idx1 = fcol_in_mdf["Consumption_taxes_last_year"]
    idx2 = fcol_in_mdf["Consumption_taxes"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / One_year * dt
      )

    # XtaxCom_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , XtaxCom_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , XtaxCom_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , XtaxCom_R1_via_Excel , XtaxCom_policy_Min ) ) )
    idxlhs = fcol_in_mdf["XtaxCom_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     XtaxCom_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       XtaxCom_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, XtaxCom_R1_via_Excel[j], XtaxCom_policy_Min
          ),     ),   )

    # XtaxCom_policy_with_RW[region] = XtaxCom_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["XtaxCom_policy_with_RW"]
    idx1 = fcol_in_mdf["XtaxCom_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # XtaxCom_pol_div_100[region] = MIN ( XtaxCom_policy_Max , MAX ( XtaxCom_policy_Min , XtaxCom_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["XtaxCom_pol_div_100"]
    idx1 = fcol_in_mdf["XtaxCom_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(XtaxCom_policy_Max, max(XtaxCom_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # XtaxCom_policy[region] = SMOOTH3 ( XtaxCom_pol_div_100[region] , XtaxCom_Time_to_implement_policy )
    idxin = fcol_in_mdf["XtaxCom_pol_div_100"]
    idx2 = fcol_in_mdf["XtaxCom_policy_2"]
    idx1 = fcol_in_mdf["XtaxCom_policy_1"]
    idxout = fcol_in_mdf["XtaxCom_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (XtaxCom_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (XtaxCom_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (XtaxCom_Time_to_implement_policy / 3)
        * dt
      )

    # Universal_basic_dividend[region] = National_income[region] * XtaxCom_policy[region]
    idxlhs = fcol_in_mdf["Universal_basic_dividend"]
    idx1 = fcol_in_mdf["National_income"]
    idx2 = fcol_in_mdf["XtaxCom_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Owner_wealth_accumulated[region] = INTEG ( Owner_wealth_accumulating[region] - Wealth_taxing[region] , GDP_in_1980[region] * Fraction_multiple_of_regional_GDP_as_owners_wealth_in_1980[region] )
    idx1 = fcol_in_mdf["Owner_wealth_accumulated"]
    idx2 = fcol_in_mdf["Owner_wealth_accumulating"]
    idx3 = fcol_in_mdf["Wealth_taxing"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # TOW_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , TOW_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , TOW_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , TOW_R1_via_Excel , TOW_policy_Min ) ) )
    idxlhs = fcol_in_mdf["TOW_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     TOW_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       TOW_R2_via_Excel[j],       IF_THEN_ELSE(zeit >= Policy_start_year, TOW_R1_via_Excel[j], TOW_policy_Min),     ),   )

    # TOW_policy_with_RW[region] = TOW_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["TOW_policy_with_RW"]
    idx1 = fcol_in_mdf["TOW_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # TOW_pol_div_100[region] = MIN ( TOW_policy_Max , MAX ( TOW_policy_Min , TOW_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["TOW_pol_div_100"]
    idx1 = fcol_in_mdf["TOW_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(TOW_policy_Max, max(TOW_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # TOW_policy_converted_to_pa[region] = TOW_pol_div_100[region] * TOW_UNIT_conv_to_pa
    idxlhs = fcol_in_mdf["TOW_policy_converted_to_pa"]
    idx1 = fcol_in_mdf["TOW_pol_div_100"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * TOW_UNIT_conv_to_pa

    # TOW_policy[region] = SMOOTH3 ( TOW_policy_converted_to_pa[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["TOW_policy_converted_to_pa"]
    idx2 = fcol_in_mdf["TOW_policy_2"]
    idx1 = fcol_in_mdf["TOW_policy_1"]
    idxout = fcol_in_mdf["TOW_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Wealth_taxing[region] = Owner_wealth_accumulated[region] * TOW_policy[region]
    idxlhs = fcol_in_mdf["Wealth_taxing"]
    idx1 = fcol_in_mdf["Owner_wealth_accumulated"]
    idx2 = fcol_in_mdf["TOW_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Fossil_use_pp_NOT_for_El_gen_CN = Fossil_use_pp_NOT_for_El_gen_CN_a + Fossil_use_pp_NOT_for_El_gen_CN_b * ( LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) )
    idxlhs = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      Fossil_use_pp_NOT_for_El_gen_CN_a
      + Fossil_use_pp_NOT_for_El_gen_CN_b
      * (math.log(mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl))
    )

    # Fossil_use_pp_NOT_for_El_gen_WO_CN[region] = Fossil_use_pp_NOT_for_El_gen_WO_CN_L[region] / ( 1 + math.exp ( - Fossil_use_pp_NOT_for_El_gen_WO_CN_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - Fossil_use_pp_NOT_for_El_gen_WO_CN_x0[region] ) ) )
    idxlhs = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen_WO_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Fossil_use_pp_NOT_for_El_gen_WO_CN_L[j] / (
        1
        + math.exp(
          -Fossil_use_pp_NOT_for_El_gen_WO_CN_k[j]
          * (
            (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl)
            - Fossil_use_pp_NOT_for_El_gen_WO_CN_x0[j]
          )
        )
      )

    # Fossil_use_pp_NOT_for_El_gen[region] = IF_THEN_ELSE ( j==2 , Fossil_use_pp_NOT_for_El_gen_CN , Fossil_use_pp_NOT_for_El_gen_WO_CN )
    idxlhs = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen"]
    idx1 = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen_CN"]
    idx2 = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen_WO_CN"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 2, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # Fossil_use_pp_NOT_for_El_gen_toe_py[region] = Fossil_use_pp_NOT_for_El_gen[region] * UNIT_conv_to_toe_py
    idxlhs = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen_toe_py"]
    idx1 = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_toe_py

    # Extra_energy_productivity_index_2024_is_1[region] = INTEG ( Increase_in_exepi[region] , 1 )
    idx1 = fcol_in_mdf["Extra_energy_productivity_index_2024_is_1"]
    idx2 = fcol_in_mdf["Increase_in_exepi"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # wind_and_PV_el_capacity[region] = INTEG ( Addition_of_wind_and_PV_el_capacity[region] - Discarding_wind_and_PV_el_capacity[region] , wind_and_PV_el_cap_in_1980 )
    idx1 = fcol_in_mdf["wind_and_PV_el_capacity"]
    idx2 = fcol_in_mdf["Addition_of_wind_and_PV_el_capacity"]
    idx3 = fcol_in_mdf["Discarding_wind_and_PV_el_capacity"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # El_from_wind_and_PV[region] = wind_and_PV_el_capacity[region] * wind_and_PV_capacity_factor[region] * Hours_per_year * UNIT_conv_GWh_and_TWh
    idxlhs = fcol_in_mdf["El_from_wind_and_PV"]
    idx1 = fcol_in_mdf["wind_and_PV_el_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * wind_and_PV_capacity_factor
        * Hours_per_year
        * UNIT_conv_GWh_and_TWh
      )

    # Hydro_net_depreciation_multiplier_on_gen_cap = INTEG ( - Hydro_net_depreciation , 1 )
    idx1 = fcol_in_mdf["Hydro_net_depreciation_multiplier_on_gen_cap"]
    idx2 = fcol_in_mdf["Hydro_net_depreciation"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Hydro_gen_cap[region] = ( Hydro_gen_cap_L[region] / ( 1 + math.exp ( - Hydro_gen_cap_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - Hydro_gen_cap_x0[region] ) ) ) ) * Hydro_net_depreciation_multiplier_on_gen_cap
    idxlhs = fcol_in_mdf["Hydro_gen_cap"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    idx2 = fcol_in_mdf["Hydro_net_depreciation_multiplier_on_gen_cap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Hydro_gen_cap_L[j]
        / (
          1
          + math.exp(
            -Hydro_gen_cap_k[j]
            * ((mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) - Hydro_gen_cap_x0[j])
          )
        )
      ) * mdf[rowi, idx2]

    # El_from_Hydro[region] = Hydro_gen_cap[region] * Hydrocapacity_factor[region] * Hours_per_year * UNIT_conv_GWh_and_TWh
    idxlhs = fcol_in_mdf["El_from_Hydro"]
    idx1 = fcol_in_mdf["Hydro_gen_cap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Hydrocapacity_factor[j]
        * Hours_per_year
        * UNIT_conv_GWh_and_TWh
      )

    # wind_PV_and_hydro_el_generation[region] = El_from_wind_and_PV[region] + El_from_Hydro[region]
    idxlhs = fcol_in_mdf["wind_PV_and_hydro_el_generation"]
    idx1 = fcol_in_mdf["El_from_wind_and_PV"]
    idx2 = fcol_in_mdf["El_from_Hydro"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Green_hydrogen[region] = wind_PV_and_hydro_el_generation[region] * Actual_GH_share / TWh_per_MtH
    idxlhs = fcol_in_mdf["Green_hydrogen"]
    idx1 = fcol_in_mdf["wind_PV_and_hydro_el_generation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Actual_GH_share / TWh_per_MtH

    # Green_hydrogen_in_Mtoe_py[region] = Green_hydrogen[region] * toe_per_tH
    idxlhs = fcol_in_mdf["Green_hydrogen_in_Mtoe_py"]
    idx1 = fcol_in_mdf["Green_hydrogen"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * toe_per_tH

    # Low_carbon_heat_production[region] = Green_hydrogen_in_Mtoe_py[region]
    idxlhs = fcol_in_mdf["Low_carbon_heat_production"]
    idx1 = fcol_in_mdf["Green_hydrogen_in_Mtoe_py"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Fossil_fuel_NOT_for_El_gen[region] = ( ( Fossil_use_pp_NOT_for_El_gen_toe_py[region] * Population[region] ) / Extra_energy_productivity_index_2024_is_1[region] ) * UNIT_conv_toe_to_Mtoe - Low_carbon_heat_production[region]
    idxlhs = fcol_in_mdf["Fossil_fuel_NOT_for_El_gen"]
    idx1 = fcol_in_mdf["Fossil_use_pp_NOT_for_El_gen_toe_py"]
    idx2 = fcol_in_mdf["Population"]
    idx3 = fcol_in_mdf["Extra_energy_productivity_index_2024_is_1"]
    idx4 = fcol_in_mdf["Low_carbon_heat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j]
      ) * UNIT_conv_toe_to_Mtoe - mdf[rowi, idx4 + j]

    # Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region] = Fossil_fuel_NOT_for_El_gen[region] * Fraction_of_Fossil_fuel_for_NON_El_use_that_cannot_be_electrified
    idxlhs = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified"]
    idx1 = fcol_in_mdf["Fossil_fuel_NOT_for_El_gen"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Fraction_of_Fossil_fuel_for_NON_El_use_that_cannot_be_electrified
      )

    # Fossil_fuel_for_NON_El_use_that_COULD_be_electrified[region] = Fossil_fuel_NOT_for_El_gen[region] - Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region]
    idxlhs = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_COULD_be_electrified"]
    idx1 = fcol_in_mdf["Fossil_fuel_NOT_for_El_gen"]
    idx2 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # NEP_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , NEP_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , NEP_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , NEP_R1_via_Excel , NEP_policy_Min ) ) )
    idxlhs = fcol_in_mdf["NEP_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     NEP_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       NEP_R2_via_Excel[j],       IF_THEN_ELSE(zeit >= Policy_start_year, NEP_R1_via_Excel[j], NEP_policy_Min),     ),   )

    # NEP_policy_with_RW[region] = NEP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
    idxlhs = fcol_in_mdf["NEP_policy_with_RW"]
    idx1 = fcol_in_mdf["NEP_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # NEP_pol_div_100[region] = MIN ( NEP_policy_Max , MAX ( NEP_policy_Min , NEP_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["NEP_pol_div_100"]
    idx1 = fcol_in_mdf["NEP_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(NEP_policy_Max, max(NEP_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # NEP_policy[region] = SMOOTH3 ( NEP_pol_div_100[region] , NEP_Time_to_implement_goal )
    idxin = fcol_in_mdf["NEP_pol_div_100"]
    idx2 = fcol_in_mdf["NEP_policy_2"]
    idx1 = fcol_in_mdf["NEP_policy_1"]
    idxout = fcol_in_mdf["NEP_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (NEP_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (NEP_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (NEP_Time_to_implement_goal / 3)
        * dt
      )

    # Fossil_fuel_for_NON_El_use_that_IS_being_electrified[region] = Fossil_fuel_for_NON_El_use_that_COULD_be_electrified[region] * NEP_policy[region]
    idxlhs = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_being_electrified"]
    idx1 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_COULD_be_electrified"]
    idx2 = fcol_in_mdf["NEP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] = Fossil_fuel_for_NON_El_use_that_COULD_be_electrified[region] - Fossil_fuel_for_NON_El_use_that_IS_being_electrified[region]
    idxlhs = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified"]
    idx1 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_COULD_be_electrified"]
    idx2 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_being_electrified"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Fossil_el_gen_cap[region] = INTEG ( Addition_of_FEGC[region] - Discarding_of_FEGC[region] , Fossil_el_gen_cap_in_1980[region] )
    idx1 = fcol_in_mdf["Fossil_el_gen_cap"]
    idx2 = fcol_in_mdf["Addition_of_FEGC"]
    idx3 = fcol_in_mdf["Discarding_of_FEGC"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # El_gen_from_fossil_fuels[region] = Fossil_el_gen_cap[region] * Hours_per_year * Fossil_actual_uptime_factor[region] * UNIT_conv_GWh_and_TWh
    idxlhs = fcol_in_mdf["El_gen_from_fossil_fuels"]
    idx1 = fcol_in_mdf["Fossil_el_gen_cap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Hours_per_year
        * Fossil_actual_uptime_factor[j]
        * UNIT_conv_GWh_and_TWh
      )

    # Fossil_fuels_for_el_gen[region] = El_gen_from_fossil_fuels[region] / Conversion_Mtoe_to_TWh[region]
    idxlhs = fcol_in_mdf["Fossil_fuels_for_el_gen"]
    idx1 = fcol_in_mdf["El_gen_from_fossil_fuels"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Conversion_Mtoe_to_TWh[j]

    # Total_use_of_fossil_fuels[region] = Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified[region] + Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] + Fossil_fuels_for_el_gen[region]
    idxlhs = fcol_in_mdf["Total_use_of_fossil_fuels"]
    idx1 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_CANNOT_be_electrified"]
    idx2 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified"]
    idx3 = fcol_in_mdf["Fossil_fuels_for_el_gen"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # CCS_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , CCS_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , CCS_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , CCS_R1_via_Excel , CCS_policy_Min ) ) )
    idxlhs = fcol_in_mdf["CCS_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     CCS_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       CCS_R2_via_Excel[j],       IF_THEN_ELSE(zeit >= Policy_start_year, CCS_R1_via_Excel[j], CCS_policy_Min),     ),   )

    # CCS_policy_with_RW[region] = CCS_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
    idxlhs = fcol_in_mdf["CCS_policy_with_RW"]
    idx1 = fcol_in_mdf["CCS_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # CCS_pol_div_100[region] = MIN ( CCS_policy_Max , MAX ( CCS_policy_Min , CCS_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["CCS_pol_div_100"]
    idx1 = fcol_in_mdf["CCS_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(CCS_policy_Max, max(CCS_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # CCS_policy[region] = SMOOTH3 ( CCS_pol_div_100[region] , Time_to_implement_CCS_goal )
    idxin = fcol_in_mdf["CCS_pol_div_100"]
    idx2 = fcol_in_mdf["CCS_policy_2"]
    idx1 = fcol_in_mdf["CCS_policy_1"]
    idxout = fcol_in_mdf["CCS_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_implement_CCS_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_implement_CCS_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_implement_CCS_goal / 3)
        * dt
      )

    # Fraction_of_fossil_fuels_compensated_by_CCS[region] = CCS_policy[region]
    idxlhs = fcol_in_mdf["Fraction_of_fossil_fuels_compensated_by_CCS"]
    idx1 = fcol_in_mdf["CCS_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Total_use_of_fossil_fuels_NOT_compensated[region] = Total_use_of_fossil_fuels[region] * ( 1 - Fraction_of_fossil_fuels_compensated_by_CCS[region] )
    idxlhs = fcol_in_mdf["Total_use_of_fossil_fuels_NOT_compensated"]
    idx1 = fcol_in_mdf["Total_use_of_fossil_fuels"]
    idx2 = fcol_in_mdf["Fraction_of_fossil_fuels_compensated_by_CCS"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # CO2_from_fossil_fuels_to_atm[region] = MAX ( 0 , toe_to_CO2_a[region] * ( Total_use_of_fossil_fuels_NOT_compensated[region] * UNIT_conv_to_Gtoe ) + toe_to_CO2_b[region] )
    idxlhs = fcol_in_mdf["CO2_from_fossil_fuels_to_atm"]
    idx1 = fcol_in_mdf["Total_use_of_fossil_fuels_NOT_compensated"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0, toe_to_CO2_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_Gtoe) + toe_to_CO2_b[j]
      )

    # CO2_emi_from_IPC_2_CN = CO2_emi_from_IPC_2_CN_L / ( 1 + math.exp ( - CO2_emi_from_IPC_2_CN_k * ( ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) - CO2_emi_from_IPC_2_CN_x0 ) ) )
    idxlhs = fcol_in_mdf["CO2_emi_from_IPC_2_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = CO2_emi_from_IPC_2_CN_L / (
      1
      + math.exp(
        -CO2_emi_from_IPC_2_CN_k
        * (
          (mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl) - CO2_emi_from_IPC_2_CN_x0
        )
      )
    )

    # CO2_emi_from_IPC2_use_wo_CN[region] = CO2_emi_from_IPC2_use_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + CO2_emi_from_IPC2_use_b[region]
    idxlhs = fcol_in_mdf["CO2_emi_from_IPC2_use_wo_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (CO2_emi_from_IPC2_use_a[j]
        * math.log(mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl)
        + CO2_emi_from_IPC2_use_b[j]
      )

    # CO2_emi_from_IPC2_use[region] = IF_THEN_ELSE ( j==2 , CO2_emi_from_IPC_2_CN , CO2_emi_from_IPC2_use_wo_CN )
    idxlhs = fcol_in_mdf["CO2_emi_from_IPC2_use"]
    idx1 = fcol_in_mdf["CO2_emi_from_IPC_2_CN"]
    idx2 = fcol_in_mdf["CO2_emi_from_IPC2_use_wo_CN"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 2, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # Total_CO2_emissions[region] = CO2_from_fossil_fuels_to_atm[region] + CO2_emi_from_IPC2_use[region]
    idxlhs = fcol_in_mdf["Total_CO2_emissions"]
    idx1 = fcol_in_mdf["CO2_from_fossil_fuels_to_atm"]
    idx2 = fcol_in_mdf["CO2_emi_from_IPC2_use"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Ctax_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , Ctax_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , Ctax_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , Ctax_R1_via_Excel , Ctax_policy_Min ) ) )
    idxlhs = fcol_in_mdf["Ctax_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     Ctax_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       Ctax_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, Ctax_R1_via_Excel[j], Ctax_policy_Min
          ),     ),   )

    # Ctax_policy_with_RW[region] = Ctax_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["Ctax_policy_with_RW"]
    idx1 = fcol_in_mdf["Ctax_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Ctax_pol_div_100[region] = MIN ( Ctax_policy_Max , MAX ( Ctax_policy_Min , Ctax_policy_with_RW[region] ) ) / 1
    idxlhs = fcol_in_mdf["Ctax_pol_div_100"]
    idx1 = fcol_in_mdf["Ctax_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(Ctax_policy_Max, max(Ctax_policy_Min, mdf[rowi, idx1 + j])) / 1
      )

    # Ctax_policy_with_inequality_effect[region] = MIN ( Ctax_policy_Max , Ctax_pol_div_100[region] / Inequality_effect_on_energy_TA[region] )
    idxlhs = fcol_in_mdf["Ctax_policy_with_inequality_effect"]
    idx1 = fcol_in_mdf["Ctax_pol_div_100"]
    idx2 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(
        Ctax_policy_Max, mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]
      )

    # Ctax_policy[region] = SMOOTH3 ( Ctax_policy_with_inequality_effect[region] , Ctax_Time_to_implement_goal )
    idxin = fcol_in_mdf["Ctax_policy_with_inequality_effect"]
    idx2 = fcol_in_mdf["Ctax_policy_2"]
    idx1 = fcol_in_mdf["Ctax_policy_1"]
    idxout = fcol_in_mdf["Ctax_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Ctax_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Ctax_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Ctax_Time_to_implement_goal / 3)
        * dt
      )

    # Ctax_carbon_tax_policy[region] = Ctax_policy[region] * Ctax_UNIT_conv_to_GtCO2_pr_yr
    idxlhs = fcol_in_mdf["Ctax_carbon_tax_policy"]
    idx1 = fcol_in_mdf["Ctax_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Ctax_UNIT_conv_to_GtCO2_pr_yr

    # Carbon_taxes[region] = Total_CO2_emissions[region] * Ctax_carbon_tax_policy[region] * UNIT_conv_to_G2017pppUSD
    idxlhs = fcol_in_mdf["Carbon_taxes"]
    idx1 = fcol_in_mdf["Total_CO2_emissions"]
    idx2 = fcol_in_mdf["Ctax_carbon_tax_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * UNIT_conv_to_G2017pppUSD
      )

    # Gross_Govt_income[region] = Income_and_policy_taxes_paid_by_owners[region] + Worker_income_and_policy_taxes[region] + Consumption_taxes_last_year[region] + Universal_basic_dividend[region] + Wealth_taxing[region] + Carbon_taxes[region]
    idxlhs = fcol_in_mdf["Gross_Govt_income"]
    idx1 = fcol_in_mdf["Income_and_policy_taxes_paid_by_owners"]
    idx2 = fcol_in_mdf["Worker_income_and_policy_taxes"]
    idx3 = fcol_in_mdf["Consumption_taxes_last_year"]
    idx4 = fcol_in_mdf["Universal_basic_dividend"]
    idx5 = fcol_in_mdf["Wealth_taxing"]
    idx6 = fcol_in_mdf["Carbon_taxes"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
      )

    # Indicated_Future_TLTL_leakage[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Ref_Future_TLTL_leakage , 0 )
    idxlhs = fcol_in_mdf["Indicated_Future_TLTL_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit > Policy_start_year, Ref_Future_TLTL_leakage, 0
      )

    # Future_TLTL_leakage[region] = SMOOTH3 ( Indicated_Future_TLTL_leakage[region] , Time_to_ramp_in_future_TLTL_leakage )
    idxin = fcol_in_mdf["Indicated_Future_TLTL_leakage"]
    idx2 = fcol_in_mdf["Future_TLTL_leakage_2"]
    idx1 = fcol_in_mdf["Future_TLTL_leakage_1"]
    idxout = fcol_in_mdf["Future_TLTL_leakage"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_ramp_in_future_TLTL_leakage / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_ramp_in_future_TLTL_leakage / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_ramp_in_future_TLTL_leakage / 3)
        * dt
      )

    # Lfrac_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , Lfrac_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , Lfrac_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , Lfrac_R1_via_Excel , Lfrac_policy_Min ) ) )
    idxlhs = fcol_in_mdf["Lfrac_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     Lfrac_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       Lfrac_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, Lfrac_R1_via_Excel[j], Lfrac_policy_Min
          ),     ),   )

    # Lfrac_policy_with_RW[region] = Lfrac_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["Lfrac_policy_with_RW"]
    idx1 = fcol_in_mdf["Lfrac_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Lfrac_pol_div_100[region] = MIN ( Lfrac_policy_Max , MAX ( Lfrac_policy_Min , Lfrac_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["Lfrac_pol_div_100"]
    idx1 = fcol_in_mdf["Lfrac_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(Lfrac_policy_Max, max(Lfrac_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # Lfrac_policy[region] = SMOOTH3 ( Lfrac_pol_div_100[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["Lfrac_pol_div_100"]
    idx2 = fcol_in_mdf["Lfrac_policy_2"]
    idx1 = fcol_in_mdf["Lfrac_policy_1"]
    idxout = fcol_in_mdf["Lfrac_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Future_leakage_indicated[region] = Future_TLTL_leakage[region] * ( 1 - Lfrac_policy[region] )
    idxlhs = fcol_in_mdf["Future_leakage_indicated"]
    idx1 = fcol_in_mdf["Future_TLTL_leakage"]
    idx2 = fcol_in_mdf["Lfrac_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # Future_leakage[region] = SMOOTH3 ( Future_leakage_indicated[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["Future_leakage_indicated"]
    idx2 = fcol_in_mdf["Future_leakage_2"]
    idx1 = fcol_in_mdf["Future_leakage_1"]
    idxout = fcol_in_mdf["Future_leakage"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Max_transfer_share[region] = MIN ( 1 , Fraction_of_govt_income_transferred_to_workers_a )
    idxlhs = fcol_in_mdf["Max_transfer_share"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(1, Fraction_of_govt_income_transferred_to_workers_a)

    # Fraction_of_govt_income_transferred_to_workers[region] = Max_transfer_share[region] / ( 1 + math.exp ( Fraction_of_govt_income_transferred_to_workers_b * GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl + Fraction_of_govt_income_transferred_to_workers_c ) )
    idxlhs = fcol_in_mdf["Fraction_of_govt_income_transferred_to_workers"]
    idx1 = fcol_in_mdf["Max_transfer_share"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        1
        + math.exp(
          Fraction_of_govt_income_transferred_to_workers_b
          * mdf[rowi, idx2 + j]
          * UNIT_conv_to_make_exp_dmnl
          + Fraction_of_govt_income_transferred_to_workers_c
        )
      )

    # Transfer_from_govt_to_workers[region] = Gross_Govt_income[region] * ( 1 - Future_leakage[region] ) * Fraction_of_govt_income_transferred_to_workers[region]
    idxlhs = fcol_in_mdf["Transfer_from_govt_to_workers"]
    idx1 = fcol_in_mdf["Gross_Govt_income"]
    idx2 = fcol_in_mdf["Future_leakage"]
    idx3 = fcol_in_mdf["Fraction_of_govt_income_transferred_to_workers"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j]) * mdf[rowi, idx3 + j]
      )

    # Govt_income_after_transfers[region] = Gross_Govt_income[region] - Transfer_from_govt_to_workers[region]
    idxlhs = fcol_in_mdf["Govt_income_after_transfers"]
    idx1 = fcol_in_mdf["Gross_Govt_income"]
    idx2 = fcol_in_mdf["Transfer_from_govt_to_workers"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Govt_debt_owed_to_private_lenders[region] = INTEG ( Govt_new_debt_from_private_lenders[region] - Govt_debt_paid_back_to_private_lenders[region] - Govt_debt_cancelling[region] , Govt_debt_in_1980[region] )
    idx1 = fcol_in_mdf["Govt_debt_owed_to_private_lenders"]
    idx2 = fcol_in_mdf["Govt_new_debt_from_private_lenders"]
    idx3 = fcol_in_mdf["Govt_debt_paid_back_to_private_lenders"]
    idx4 = fcol_in_mdf["Govt_debt_cancelling"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # SSGDR_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , SSGDR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , SSGDR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , SSGDR_R1_via_Excel , SSGDR_policy_Min ) ) )
    idxlhs = fcol_in_mdf["SSGDR_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     SSGDR_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       SSGDR_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, SSGDR_R1_via_Excel[j], SSGDR_policy_Min
          ),     ),   )

    # SSGDR_policy_with_RW[region] = SSGDR_policy_Min + ( SSGDR_rounds_via_Excel[region] - SSGDR_policy_Min ) * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["SSGDR_policy_with_RW"]
    idx1 = fcol_in_mdf["SSGDR_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (SSGDR_policy_Min
        + (mdf[rowi, idx1 + j] - SSGDR_policy_Min) * mdf[rowi, idx2 + j]
      )

    # SSGDR_pol_div_100[region] = MIN ( SSGDR_policy_Max , MAX ( SSGDR_policy_Min , SSGDR_policy_with_RW[region] ) ) / 1
    idxlhs = fcol_in_mdf["SSGDR_pol_div_100"]
    idx1 = fcol_in_mdf["SSGDR_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(SSGDR_policy_Max, max(SSGDR_policy_Min, mdf[rowi, idx1 + j])) / 1
      )

    # SSGDR_policy[region] = SMOOTH3 ( SSGDR_pol_div_100[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["SSGDR_pol_div_100"]
    idx2 = fcol_in_mdf["SSGDR_policy_2"]
    idx1 = fcol_in_mdf["SSGDR_policy_1"]
    idxout = fcol_in_mdf["SSGDR_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Govt_payback_period_to_PL[region] = Normal_Govt_payback_period_to_PL * SSGDR_policy[region]
    idxlhs = fcol_in_mdf["Govt_payback_period_to_PL"]
    idx1 = fcol_in_mdf["SSGDR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Normal_Govt_payback_period_to_PL * mdf[rowi, idx1 + j]

    # Govt_debt_repayment_obligation[region] = Govt_debt_owed_to_private_lenders[region] / Govt_payback_period_to_PL[region]
    idxlhs = fcol_in_mdf["Govt_debt_repayment_obligation"]
    idx1 = fcol_in_mdf["Govt_debt_owed_to_private_lenders"]
    idx2 = fcol_in_mdf["Govt_payback_period_to_PL"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Central_bank_signal_rate[region] = INTEG ( Change_in_signal_rate[region] , Central_bank_signal_rate_in_1980[region] )
    idx1 = fcol_in_mdf["Central_bank_signal_rate"]
    idx2 = fcol_in_mdf["Change_in_signal_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Short_term_interest_rate[region] = Central_bank_signal_rate[region] + Normal_basic_bank_margin
    idxlhs = fcol_in_mdf["Short_term_interest_rate"]
    idx1 = fcol_in_mdf["Central_bank_signal_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Normal_basic_bank_margin

    # Indicated_long_term_interest_rate[region] = Short_term_interest_rate[region] + Long_term_risk_margin
    idxlhs = fcol_in_mdf["Indicated_long_term_interest_rate"]
    idx1 = fcol_in_mdf["Short_term_interest_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Long_term_risk_margin

    # Long_term_interest_rate_used_by_private_lenders[region] = SMOOTH ( Indicated_long_term_interest_rate[region] , Long_term_interest_rate_expectation_formation_time )
    idx1 = fcol_in_mdf["Long_term_interest_rate_used_by_private_lenders"]
    idx2 = fcol_in_mdf["Indicated_long_term_interest_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Long_term_interest_rate_expectation_formation_time
        * dt
      )

    # Govt_defaulting_N_yrs_ago[region] = SMOOTHI ( Govt_defaulting[region] , Time_for_defaulting_to_impact_cost_of_capital , 0 )
    idx1 = fcol_in_mdf["Govt_defaulting_N_yrs_ago"]
    idx2 = fcol_in_mdf["Govt_defaulting"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_defaulting_to_impact_cost_of_capital
        * dt
      )

    # Govt_default_ratio[region] = Govt_defaulting_N_yrs_ago[region] / Govt_income_after_transfers[region]
    idxlhs = fcol_in_mdf["Govt_default_ratio"]
    idx1 = fcol_in_mdf["Govt_defaulting_N_yrs_ago"]
    idx2 = fcol_in_mdf["Govt_income_after_transfers"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing[region] = WITH LOOKUP ( Govt_default_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 1.04 ) , ( 0.5 , 1.1 ) , ( 0.75 , 1.3 ) , ( 1 , 1.6 ) , ( 1.5 , 2.5 ) , ( 2 , 4 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Govt_default_ratio"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Govt_interest_payment_obligation_to_PL[region] = Govt_debt_owed_to_private_lenders[region] * Long_term_interest_rate_used_by_private_lenders[region] * Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing[region]
    idxlhs = fcol_in_mdf["Govt_interest_payment_obligation_to_PL"]
    idx1 = fcol_in_mdf["Govt_debt_owed_to_private_lenders"]
    idx2 = fcol_in_mdf["Long_term_interest_rate_used_by_private_lenders"]
    idx3 = fcol_in_mdf["Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_govt_borrowing"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * mdf[rowi, idx3 + j]
      )

    # Govt_loan_obligations_to_PL[region] = Govt_debt_repayment_obligation[region] + Govt_interest_payment_obligation_to_PL[region]
    idxlhs = fcol_in_mdf["Govt_loan_obligations_to_PL"]
    idx1 = fcol_in_mdf["Govt_debt_repayment_obligation"]
    idx2 = fcol_in_mdf["Govt_interest_payment_obligation_to_PL"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Govt_cash_available_to_meet_all_loan_obligations[region] = Govt_income_after_transfers[region] * Fraction_set_aside_to_service_loans[region]
    idxlhs = fcol_in_mdf["Govt_cash_available_to_meet_all_loan_obligations"]
    idx1 = fcol_in_mdf["Govt_income_after_transfers"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Fraction_set_aside_to_service_loans

    # Govt_cash_to_meet_private_loan_obligations[region] = Govt_cash_available_to_meet_all_loan_obligations[region] * Fraction_of_avail_cash_used_to_meet_private_lender_obligations[region]
    idxlhs = fcol_in_mdf["Govt_cash_to_meet_private_loan_obligations"]
    idx1 = fcol_in_mdf["Govt_cash_available_to_meet_all_loan_obligations"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Fraction_of_avail_cash_used_to_meet_private_lender_obligations
      )

    # Govt_loan_obligations_to_PL_MET[region] = MIN ( Govt_loan_obligations_to_PL[region] , Govt_cash_to_meet_private_loan_obligations[region] )
    idxlhs = fcol_in_mdf["Govt_loan_obligations_to_PL_MET"]
    idx1 = fcol_in_mdf["Govt_loan_obligations_to_PL"]
    idx2 = fcol_in_mdf["Govt_cash_to_meet_private_loan_obligations"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(mdf[rowi, idx1 + j], mdf[rowi, idx2 + j])

    # GDP_USED[region] = IF_THEN_ELSE ( Switch_GDP_hist_1_mod_2 == 1 , GDP_H , GDP_model )
    idxlhs = fcol_in_mdf["GDP_USED"]
    idx1 = fcol_in_mdf["GDP_H"]
    idx2 = fcol_in_mdf["GDP_model"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        Switch_GDP_hist_1_mod_2 == 1, mdf[rowi, idx1 + j], mdf[rowi, idx2 + j]
      )

    # Max_govt_debt_burden_multiplier_historical_and_future[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 2050 , 2 ) ] , ( 1980 , 0 ) , ( 1990 , 1 ) , ( 2000 , 0 ) , ( 2018 , 1.2 ) , ( 2020 , 1 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 0.75 ) , ( 2000 , 0.5 ) , ( 2018 , 0.35 ) , ( 2020 , 0.3 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.9 ) , ( 2020 , 0.9 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.6 ) , ( 2020 , 0.75 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.5 ) , ( 2000 , 1 ) , ( 2018 , 0.5 ) , ( 2020 , 0.5 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.6 ) , ( 2020 , 0.75 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.5 ) , ( 2000 , 1 ) , ( 2018 , 1.5 ) , ( 2020 , 1 ) , ( 2050 , 0.5 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.05 ) , ( 2000 , 0.1 ) , ( 2018 , 0.2 ) , ( 2020 , 0.5 ) , ( 2050 , 0.4 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.25 ) , ( 2000 , 0.5 ) , ( 2018 , 0.6 ) , ( 2020 , 0.75 ) , ( 2050 , 0.6 ) ) ) Max_govt_debt_burden_multiplier_historical_and_future[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 0.75 ) , ( 2000 , 0.5 ) , ( 2018 , 0.35 ) , ( 2020 , 0.3 ) , ( 2050 , 0.5 ) ) )
    tabidx = ftab_in_d_table[  "Max_govt_debt_burden_multiplier_historical_and_future"]  # fetch the correct table
    idx2 = fcol_in_mdf["Max_govt_debt_burden_multiplier_historical_and_future"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # Max_govt_debt[region] = GDP_USED[region] * Max_govt_debt_burden_multiplier_historical_and_future[region] * Reference_max_govt_debt_burden[region]
    idxlhs = fcol_in_mdf["Max_govt_debt"]
    idx1 = fcol_in_mdf["GDP_USED"]
    idx2 = fcol_in_mdf["Max_govt_debt_burden_multiplier_historical_and_future"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * Reference_max_govt_debt_burden[j]
      )

    # Max_govt_debt_smoothed[region] = SMOOTH ( Max_govt_debt[region] , Time_to_smooth_max_govt_debt )
    idx1 = fcol_in_mdf["Max_govt_debt_smoothed"]
    idx2 = fcol_in_mdf["Max_govt_debt"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_max_govt_debt
        * dt
      )

    # Smoothed_Govt_debt_owed_to_private_lenders[region] = SMOOTH ( Govt_debt_owed_to_private_lenders[region] , Time_to_smooth_max_govt_debt )
    idx1 = fcol_in_mdf["Smoothed_Govt_debt_owed_to_private_lenders"]
    idx2 = fcol_in_mdf["Govt_debt_owed_to_private_lenders"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_max_govt_debt
        * dt
      )

    # FMPLDD_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , FMPLDD_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FMPLDD_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FMPLDD_R1_via_Excel , FMPLDD_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FMPLDD_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FMPLDD_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FMPLDD_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FMPLDD_R1_via_Excel[j], FMPLDD_policy_Min
          ),     ),   )

    # FMPLDD_policy_with_RW[region] = FMPLDD_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["FMPLDD_policy_with_RW"]
    idx1 = fcol_in_mdf["FMPLDD_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # FMPLDD_pol_div_100[region] = MIN ( FMPLDD_policy_Max , MAX ( FMPLDD_policy_Min , FMPLDD_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["FMPLDD_pol_div_100"]
    idx1 = fcol_in_mdf["FMPLDD_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FMPLDD_policy_Max, max(FMPLDD_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # FMPLDD_policy_converted_to_pa[region] = FMPLDD_pol_div_100[region] * UNIT_conv_to_pa
    idxlhs = fcol_in_mdf["FMPLDD_policy_converted_to_pa"]
    idx1 = fcol_in_mdf["FMPLDD_pol_div_100"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_pa

    # FMPLDD_policy[region] = SMOOTH3 ( FMPLDD_policy_converted_to_pa[region] , Time_to_implement_UN_policies[region] )
    idxin = fcol_in_mdf["FMPLDD_policy_converted_to_pa"]
    idx2 = fcol_in_mdf["FMPLDD_policy_2"]
    idx1 = fcol_in_mdf["FMPLDD_policy_1"]
    idxout = fcol_in_mdf["FMPLDD_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Govt_new_debt_from_private_lenders[region] = MAX ( 0 , ( Max_govt_debt_smoothed[region] - Smoothed_Govt_debt_owed_to_private_lenders[region] ) ) * ( 1 - FMPLDD_policy[region] )
    idxlhs = fcol_in_mdf["Govt_new_debt_from_private_lenders"]
    idx1 = fcol_in_mdf["Max_govt_debt_smoothed"]
    idx2 = fcol_in_mdf["Smoothed_Govt_debt_owed_to_private_lenders"]
    idx3 = fcol_in_mdf["FMPLDD_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])) * (
        1 - mdf[rowi, idx3 + j]
      )

    # Govt_cashflow_to_owners[region] = Govt_loan_obligations_to_PL_MET[region] - Govt_new_debt_from_private_lenders[region]
    idxlhs = fcol_in_mdf["Govt_cashflow_to_owners"]
    idx1 = fcol_in_mdf["Govt_loan_obligations_to_PL_MET"]
    idx2 = fcol_in_mdf["Govt_new_debt_from_private_lenders"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Govt_debt_from_public_lenders[region] = INTEG ( Increase_in_GDPL[region] - Decrease_in_GDPL[region] - Govt_debt_from_public_lenders_cancelled[region] , 0 )
    idx1 = fcol_in_mdf["Govt_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Increase_in_GDPL"]
    idx3 = fcol_in_mdf["Decrease_in_GDPL"]
    idx4 = fcol_in_mdf["Govt_debt_from_public_lenders_cancelled"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Global_GDP_H = SUM ( GDP_H[region!] )
    idxlhs = fcol_in_mdf["Global_GDP_H"]
    idx1 = fcol_in_mdf["GDP_H"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # GLobal_GDP = SUM ( GDP_model[region!] )
    idxlhs = fcol_in_mdf["GLobal_GDP"]
    idx1 = fcol_in_mdf["GDP_model"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_GDP_USED = IF_THEN_ELSE ( Switch_GDP_hist_1_mod_2 == 1 , Global_GDP_H , GLobal_GDP )
    idxlhs = fcol_in_mdf["Global_GDP_USED"]
    idx1 = fcol_in_mdf["Global_GDP_H"]
    idx2 = fcol_in_mdf["GLobal_GDP"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      Switch_GDP_hist_1_mod_2 == 1, mdf[rowi, idx1], mdf[rowi, idx2]
    )

    # Avg_global_long_term_interest_rate = Long_term_interest_rate_used_by_private_lenders[us] * GDP_USED[us] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[cn] * GDP_USED[cn] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[af] * GDP_USED[af] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[me] * GDP_USED[me] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[pa] * GDP_USED[pa] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[ec] * GDP_USED[ec] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[eu] * GDP_USED[eu] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[la] * GDP_USED[la] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[sa] * GDP_USED[sa] / Global_GDP_USED + Long_term_interest_rate_used_by_private_lenders[se] * GDP_USED[se] / Global_GDP_USED
    idxlhs = fcol_in_mdf["Avg_global_long_term_interest_rate"]
    idx1 = fcol_in_mdf["Long_term_interest_rate_used_by_private_lenders"]
    idx2 = fcol_in_mdf["GDP_USED"]
    idx3 = fcol_in_mdf["Global_GDP_USED"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1 + 0] * mdf[rowi, idx2 + 0] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 1] * mdf[rowi, idx2 + 1] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 2] * mdf[rowi, idx2 + 2] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 3] * mdf[rowi, idx2 + 3] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 4] * mdf[rowi, idx2 + 4] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 5] * mdf[rowi, idx2 + 5] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 6] * mdf[rowi, idx2 + 6] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 7] * mdf[rowi, idx2 + 7] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 8] * mdf[rowi, idx2 + 8] / mdf[rowi, idx3]
      + mdf[rowi, idx1 + 9] * mdf[rowi, idx2 + 9] / mdf[rowi, idx3]
    )

    # Indicated_long_term_interest_rate_after_global_considerations[region] = MIN ( Long_term_interest_rate_used_by_private_lenders[region] , Avg_global_long_term_interest_rate )
    idxlhs = fcol_in_mdf["Indicated_long_term_interest_rate_after_global_considerations"
    ]
    idx1 = fcol_in_mdf["Long_term_interest_rate_used_by_private_lenders"]
    idx2 = fcol_in_mdf["Avg_global_long_term_interest_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(mdf[rowi, idx1 + j], mdf[rowi, idx2])

    # Long_term_interest_rate_used_by_public_lenders[region] = SMOOTH ( Indicated_long_term_interest_rate_after_global_considerations[region] , Long_term_interest_rate_expectation_formation_time )
    idx1 = fcol_in_mdf["Long_term_interest_rate_used_by_public_lenders"]
    idx2 = fcol_in_mdf["Indicated_long_term_interest_rate_after_global_considerations"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Long_term_interest_rate_expectation_formation_time
        * dt
      )

    # Public_loan_defaults[region] = INTEG ( Increase_in_public_loan_defaults[region] - Decrease_in_public_loan_defaults[region] , 0 )
    idx1 = fcol_in_mdf["Public_loan_defaults"]
    idx2 = fcol_in_mdf["Increase_in_public_loan_defaults"]
    idx3 = fcol_in_mdf["Decrease_in_public_loan_defaults"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Public_loan_defaults_as_fraction_of_GDP[region] = Public_loan_defaults[region] / GDP_USED[region]
    idxlhs = fcol_in_mdf["Public_loan_defaults_as_fraction_of_GDP"]
    idx1 = fcol_in_mdf["Public_loan_defaults"]
    idx2 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Effect_of_public_loan_defaults_on_interest_rate[region] = WITH LOOKUP ( Public_loan_defaults_as_fraction_of_GDP[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 0.25 , 0 ) , ( 0.5 , 0.005 ) , ( 0.75 , 0.01 ) , ( 1 , 0.02 ) , ( 1.5 , 0.05 ) , ( 2 , 0.1 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_public_loan_defaults_on_interest_rate"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_public_loan_defaults_on_interest_rate"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Public_loan_defaults_as_fraction_of_GDP"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Long_term_interest_rate_applied[region] = Long_term_interest_rate_used_by_public_lenders[region] + Effect_of_public_loan_defaults_on_interest_rate[region]
    idxlhs = fcol_in_mdf["Long_term_interest_rate_applied"]
    idx1 = fcol_in_mdf["Long_term_interest_rate_used_by_public_lenders"]
    idx2 = fcol_in_mdf["Effect_of_public_loan_defaults_on_interest_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Obligation_for_interest_payments_on_debt_from_public_lenders[region] = Govt_debt_from_public_lenders[region] * Long_term_interest_rate_applied[region]
    idxlhs = fcol_in_mdf["Obligation_for_interest_payments_on_debt_from_public_lenders"]
    idx1 = fcol_in_mdf["Govt_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Long_term_interest_rate_applied"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Time_to_payback_public_debt[region] = Normal_time_to_payback_public_debt * SSGDR_policy[region]
    idxlhs = fcol_in_mdf["Time_to_payback_public_debt"]
    idx1 = fcol_in_mdf["SSGDR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Normal_time_to_payback_public_debt * mdf[rowi, idx1 + j]

    # Obligation_for_payback_of_debt_from_public_lenders[region] = Govt_debt_from_public_lenders[region] / Time_to_payback_public_debt[region]
    idxlhs = fcol_in_mdf["Obligation_for_payback_of_debt_from_public_lenders"]
    idx1 = fcol_in_mdf["Govt_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Time_to_payback_public_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # All_loan_service_obligations_to_public_lenders[region] = Obligation_for_interest_payments_on_debt_from_public_lenders[region] + Obligation_for_payback_of_debt_from_public_lenders[region]
    idxlhs = fcol_in_mdf["All_loan_service_obligations_to_public_lenders"]
    idx1 = fcol_in_mdf["Obligation_for_interest_payments_on_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Obligation_for_payback_of_debt_from_public_lenders"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Govt_cash_to_meet_public_loan_obligations[region] = Govt_cash_available_to_meet_all_loan_obligations[region] * ( 1 - Fraction_of_avail_cash_used_to_meet_private_lender_obligations[region] )
    idxlhs = fcol_in_mdf["Govt_cash_to_meet_public_loan_obligations"]
    idx1 = fcol_in_mdf["Govt_cash_available_to_meet_all_loan_obligations"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (
        1 - Fraction_of_avail_cash_used_to_meet_private_lender_obligations
      )

    # All_loan_service_obligations_to_public_lenders_met[region] = MIN ( All_loan_service_obligations_to_public_lenders[region] , Govt_cash_to_meet_public_loan_obligations[region] )
    idxlhs = fcol_in_mdf["All_loan_service_obligations_to_public_lenders_met"]
    idx1 = fcol_in_mdf["All_loan_service_obligations_to_public_lenders"]
    idx2 = fcol_in_mdf["Govt_cash_to_meet_public_loan_obligations"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(mdf[rowi, idx1 + j], mdf[rowi, idx2 + j])

    # All_loan_service_obligations_to_public_lenders_not_met[region] = MAX ( 0 , All_loan_service_obligations_to_public_lenders[region] - All_loan_service_obligations_to_public_lenders_met[region] )
    idxlhs = fcol_in_mdf["All_loan_service_obligations_to_public_lenders_not_met"]
    idx1 = fcol_in_mdf["All_loan_service_obligations_to_public_lenders"]
    idx2 = fcol_in_mdf["All_loan_service_obligations_to_public_lenders_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])

    # Fraction_of_public_loans_not_serviced[region] = ZIDZ ( All_loan_service_obligations_to_public_lenders_not_met[region] , All_loan_service_obligations_to_public_lenders[region] )
    idxlhs = fcol_in_mdf["Fraction_of_public_loans_not_serviced"]
    idx1 = fcol_in_mdf["All_loan_service_obligations_to_public_lenders_not_met"]
    idx2 = fcol_in_mdf["All_loan_service_obligations_to_public_lenders"]
    for i in range(0, 10):
      mdf[rowi, idxlhs + i] = ZIDZ(mdf[rowi, idx1 + i], mdf[rowi, idx2 + i])

    # Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met[region] = Obligation_for_interest_payments_on_debt_from_public_lenders[region] * ( 1 - Fraction_of_public_loans_not_serviced[region] )
    idxlhs = fcol_in_mdf["Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met"
    ]
    idx1 = fcol_in_mdf["Obligation_for_interest_payments_on_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Fraction_of_public_loans_not_serviced"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # Actual_govt_cash_inflow[region] = Govt_income_after_transfers[region] - Govt_cashflow_to_owners[region] - Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met[region]
    idxlhs = fcol_in_mdf["Actual_govt_cash_inflow"]
    idx1 = fcol_in_mdf["Govt_income_after_transfers"]
    idx2 = fcol_in_mdf["Govt_cashflow_to_owners"]
    idx3 = fcol_in_mdf["Obligation_for_interest_payments_on_debt_from_public_lenders_actually_met"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j] - mdf[rowi, idx3 + j]
      )

    # Actual_govt_cash_inflow_seasonally_adjusted[region] = SMOOTH ( Actual_govt_cash_inflow[region] , Time_to_adjust_budget )
    idx1 = fcol_in_mdf["Actual_govt_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Actual_govt_cash_inflow"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_adjust_budget
        * dt
      )

    # SGRPI_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , SGRPI_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , SGRPI_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , SGRPI_R1_via_Excel , SGRPI_policy_Min ) ) )
    idxlhs = fcol_in_mdf["SGRPI_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     SGRPI_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       SGRPI_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, SGRPI_R1_via_Excel[j], SGRPI_policy_Min
          ),     ),   )

    # SGRPI_policy_with_RW[region] = SGRPI_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["SGRPI_policy_with_RW"]
    idx1 = fcol_in_mdf["SGRPI_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # SGRPI_pol_div_100[region] = MIN ( SGRPI_policy_Max , MAX ( SGRPI_policy_Min , SGRPI_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["SGRPI_pol_div_100"]
    idx1 = fcol_in_mdf["SGRPI_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(SGRPI_policy_Max, max(SGRPI_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # SGRPI_policy[region] = SMOOTH3 ( SGRPI_pol_div_100[region] , Time_to_implement_SGRPI_policy[region] )
    idxin = fcol_in_mdf["SGRPI_pol_div_100"]
    idx2 = fcol_in_mdf["SGRPI_policy_2"]
    idx1 = fcol_in_mdf["SGRPI_policy_1"]
    idxout = fcol_in_mdf["SGRPI_policy"]
    idx5 = fcol_in_mdf["Time_to_implement_SGRPI_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Govt_consumption_fraction_after_SGRPI[region] = MAX ( 0.05 , Govt_consumption_fraction * ( 1 - SGRPI_policy[region] ) )
    idxlhs = fcol_in_mdf["Govt_consumption_fraction_after_SGRPI"]
    idx1 = fcol_in_mdf["SGRPI_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0.05, Govt_consumption_fraction * (1 - mdf[rowi, idx1 + j])
      )

    # Govt_consumption_ie_purchases[region] = Actual_govt_cash_inflow_seasonally_adjusted[region] * Govt_consumption_fraction_after_SGRPI[region]
    idxlhs = fcol_in_mdf["Govt_consumption_ie_purchases"]
    idx1 = fcol_in_mdf["Actual_govt_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Govt_consumption_fraction_after_SGRPI"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # LPB_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , LPB_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , LPB_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , LPB_R1_via_Excel , LPB_policy_Min ) ) )
    idxlhs = fcol_in_mdf["LPB_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     LPB_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       LPB_R2_via_Excel[j],       IF_THEN_ELSE(zeit >= Policy_start_year, LPB_R1_via_Excel[j], LPB_policy_Min),     ),   )

    # LPB_policy_with_RW[region] = LPB_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["LPB_policy_with_RW"]
    idx1 = fcol_in_mdf["LPB_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # LPB_pol_div_100[region] = MIN ( LPB_policy_Max , MAX ( LPB_policy_Min , LPB_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["LPB_pol_div_100"]
    idx1 = fcol_in_mdf["LPB_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(LPB_policy_Max, max(LPB_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # LPB_policy[region] = SMOOTH3 ( LPB_pol_div_100[region] , LPB_Time_to_implement_policy )
    idxin = fcol_in_mdf["LPB_pol_div_100"]
    idx2 = fcol_in_mdf["LPB_policy_2"]
    idx1 = fcol_in_mdf["LPB_policy_1"]
    idxout = fcol_in_mdf["LPB_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (LPB_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (LPB_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (LPB_Time_to_implement_policy / 3)
        * dt
      )

    # Public_money_from_LPB_policy[region] = GDP_USED[region] * LPB_policy[region]
    idxlhs = fcol_in_mdf["Public_money_from_LPB_policy"]
    idx1 = fcol_in_mdf["GDP_USED"]
    idx2 = fcol_in_mdf["LPB_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # LPBsplit_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , LPBsplit_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , LPBsplit_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , LPBsplit_R1_via_Excel , LPBsplit_policy_Min ) ) )
    idxlhs = fcol_in_mdf["LPBsplit_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     LPBsplit_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       LPBsplit_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, LPBsplit_R1_via_Excel[j], LPBsplit_policy_Min
          ),     ),   )

    # LPBsplit_policy_with_RW[region] = LPBsplit_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["LPBsplit_policy_with_RW"]
    idx1 = fcol_in_mdf["LPBsplit_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # LPBsplit_pol_div_100[region] = MIN ( LPBsplit_policy_Max , MAX ( LPBsplit_policy_Min , LPBsplit_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["LPBsplit_pol_div_100"]
    idx1 = fcol_in_mdf["LPBsplit_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(LPBsplit_policy_Max, max(LPBsplit_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # LPBsplit_policy[region] = SMOOTH3 ( LPBsplit_pol_div_100[region] , LPBsplit_Time_to_implement_policy )
    idxin = fcol_in_mdf["LPBsplit_pol_div_100"]
    idx2 = fcol_in_mdf["LPBsplit_policy_2"]
    idx1 = fcol_in_mdf["LPBsplit_policy_1"]
    idxout = fcol_in_mdf["LPBsplit_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (LPBsplit_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (LPBsplit_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (LPBsplit_Time_to_implement_policy / 3)
        * dt
      )

    # Effect_of_public_loan_defaults_on_availability_of_new_loans[region] = WITH LOOKUP ( Public_loan_defaults_as_fraction_of_GDP[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 1 ) , ( 0.5 , 1 ) , ( 0.75 , 0.98 ) , ( 1 , 0.95 ) , ( 1.5 , 0.7 ) , ( 2 , 0.3 ) , ( 3 , 0 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_public_loan_defaults_on_availability_of_new_loans"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_public_loan_defaults_on_availability_of_new_loans"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Public_loan_defaults_as_fraction_of_GDP"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Public_money_from_LPB_policy_to_investment[region] = Public_money_from_LPB_policy[region] * LPBsplit_policy[region] * Effect_of_public_loan_defaults_on_availability_of_new_loans[region]
    idxlhs = fcol_in_mdf["Public_money_from_LPB_policy_to_investment"]
    idx1 = fcol_in_mdf["Public_money_from_LPB_policy"]
    idx2 = fcol_in_mdf["LPBsplit_policy"]
    idx3 = fcol_in_mdf["Effect_of_public_loan_defaults_on_availability_of_new_loans"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * mdf[rowi, idx3 + j]
      )

    # Public_money_from_LPB_policy_to_public_spending[region] = Public_money_from_LPB_policy[region] - Public_money_from_LPB_policy_to_investment[region]
    idxlhs = fcol_in_mdf["Public_money_from_LPB_policy_to_public_spending"]
    idx1 = fcol_in_mdf["Public_money_from_LPB_policy"]
    idx2 = fcol_in_mdf["Public_money_from_LPB_policy_to_investment"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Public_services[region] = Transfer_from_govt_to_workers[region] + Govt_consumption_ie_purchases[region] * ( 1 - Future_leakage[region] ) + Public_money_from_LPB_policy_to_public_spending[region] * ( 1 - Future_leakage[region] )
    idxlhs = fcol_in_mdf["Public_services"]
    idx1 = fcol_in_mdf["Transfer_from_govt_to_workers"]
    idx2 = fcol_in_mdf["Govt_consumption_ie_purchases"]
    idx3 = fcol_in_mdf["Future_leakage"]
    idx4 = fcol_in_mdf["Public_money_from_LPB_policy_to_public_spending"]
    idx5 = fcol_in_mdf["Future_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j] * (1 - mdf[rowi, idx3 + j])
        + mdf[rowi, idx4 + j] * (1 - mdf[rowi, idx5 + j])
      )

    # Public_services_pp[region] = Public_services[region] / Population[region]
    idxlhs = fcol_in_mdf["Public_services_pp"]
    idx1 = fcol_in_mdf["Public_services"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # FEHC_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , FEHC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FEHC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FEHC_R1_via_Excel , FEHC_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FEHC_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FEHC_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FEHC_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FEHC_R1_via_Excel[j], FEHC_policy_Min
          ),     ),   )

    # FEHC_policy_with_RW[region] = FEHC_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["FEHC_policy_with_RW"]
    idx1 = fcol_in_mdf["FEHC_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # FEHC_pol_div_100[region] = MIN ( FEHC_policy_Max , MAX ( FEHC_policy_Min , FEHC_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["FEHC_pol_div_100"]
    idx1 = fcol_in_mdf["FEHC_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FEHC_policy_Max, max(FEHC_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # FEHC_policy[region] = SMOOTH3 ( FEHC_pol_div_100[region] , FEHC_Time_to_implement_policy )
    idxin = fcol_in_mdf["FEHC_pol_div_100"]
    idx2 = fcol_in_mdf["FEHC_policy_2"]
    idx1 = fcol_in_mdf["FEHC_policy_1"]
    idxout = fcol_in_mdf["FEHC_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (FEHC_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (FEHC_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (FEHC_Time_to_implement_policy / 3)
        * dt
      )

    # FEHC_mult_used[region] = 1 - FEHC_policy[region]
    idxlhs = fcol_in_mdf["FEHC_mult_used"]
    idx1 = fcol_in_mdf["FEHC_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - mdf[rowi, idx1 + j]

    # Effect_of_FEHC_mult_on_years_of_schooling[region] = 1 + ( FEHC_mult_used[region] - 1 ) * Strength_of_FEHC_mult_on_years_of_schooling
    idxlhs = fcol_in_mdf["Effect_of_FEHC_mult_on_years_of_schooling"]
    idx1 = fcol_in_mdf["FEHC_mult_used"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 + (mdf[rowi, idx1 + j] - 1) * Strength_of_FEHC_mult_on_years_of_schooling
      )

    # Years_of_schooling[region] = ( SDG4_a * LN ( Public_services_pp[region] / UNIT_conv_to_make_base_and_ln_dmnl ) + SDG4_b ) / Effect_of_FEHC_mult_on_years_of_schooling[region]
    idxlhs = fcol_in_mdf["Years_of_schooling"]
    idx1 = fcol_in_mdf["Public_services_pp"]
    idx2 = fcol_in_mdf["Effect_of_FEHC_mult_on_years_of_schooling"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (SDG4_a * math.log(mdf[rowi, idx1 + j] / UNIT_conv_to_make_base_and_ln_dmnl)
        + SDG4_b
      ) / mdf[rowi, idx2 + j]

    # SDG4_Score[region] = IF_THEN_ELSE ( Years_of_schooling < SDG4_threshold_red , 0 , IF_THEN_ELSE ( Years_of_schooling < SDG4_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG4_Score"]
    idx1 = fcol_in_mdf["Years_of_schooling"]
    idx2 = fcol_in_mdf["Years_of_schooling"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG4_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG4_threshold_green, 0.5, 1),   )

    # GenderEquality[region] = INTEG ( Change_in_GE[region] , GE_in_1980[region] )
    idx1 = fcol_in_mdf["GenderEquality"]
    idx2 = fcol_in_mdf["Change_in_GE"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # SDG_5_Score[region] = IF_THEN_ELSE ( GenderEquality < SDG5_threshold_red , 0 , IF_THEN_ELSE ( GenderEquality < SDG5_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG_5_Score"]
    idx1 = fcol_in_mdf["GenderEquality"]
    idx2 = fcol_in_mdf["GenderEquality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG5_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG5_threshold_green, 0.5, 1),   )

    # Empowerment_score[region] = ( SDG4_Score[region] + SDG_5_Score[region] ) / 2
    idxlhs = fcol_in_mdf["Empowerment_score"]
    idx1 = fcol_in_mdf["SDG4_Score"]
    idx2 = fcol_in_mdf["SDG_5_Score"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]) / 2

    # Multplier_from_empowerment_on_speed_of_food_TA[region] = 1 + ( Empowerment_score[region] - 0.5 ) * Strength_of_Effect_of_empowerment_on_speed_of_food_TA
    idxlhs = fcol_in_mdf["Multplier_from_empowerment_on_speed_of_food_TA"]
    idx1 = fcol_in_mdf["Empowerment_score"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + (mdf[rowi, idx1 + j] - 0.5)
        * Strength_of_Effect_of_empowerment_on_speed_of_food_TA
      )

    # Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region] = SMOOTH3 ( Multplier_from_empowerment_on_speed_of_food_TA[region] , Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA )
    idxin = fcol_in_mdf["Multplier_from_empowerment_on_speed_of_food_TA"]
    idx2 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA_2"]
    idx1 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA_1"]
    idxout = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_speed_of_food_TA / 3)
        * dt
      )

    # FWRP_policy_with_RW[region] = FWRP_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
    idxlhs = fcol_in_mdf["FWRP_policy_with_RW"]
    idx1 = fcol_in_mdf["FWRP_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
      )

    # FWRP_pol_div_100[region] = MIN ( FWRP_policy_Max , MAX ( FWRP_policy_Min , FWRP_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["FWRP_pol_div_100"]
    idx1 = fcol_in_mdf["FWRP_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FWRP_policy_Max, max(FWRP_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # FWRP_policy[region] = SMOOTH3 ( FWRP_pol_div_100[region] , FWRP_Time_to_implement_goal )
    idxin = fcol_in_mdf["FWRP_pol_div_100"]
    idx2 = fcol_in_mdf["FWRP_policy_2"]
    idx1 = fcol_in_mdf["FWRP_policy_1"]
    idxout = fcol_in_mdf["FWRP_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (FWRP_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (FWRP_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (FWRP_Time_to_implement_goal / 3)
        * dt
      )

    # Fraction_of_food_wasted[region] = Food_wasted_in_1980[region] * ( 1 - FWRP_policy[region] )
    idxlhs = fcol_in_mdf["Fraction_of_food_wasted"]
    idx1 = fcol_in_mdf["FWRP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Food_wasted_in_1980[j] * (1 - mdf[rowi, idx1 + j])

    # cereal_dmd_food_pp_wasted[region] = cereal_dmd_food_pp[region] * Fraction_of_food_wasted[region]
    idxlhs = fcol_in_mdf["cereal_dmd_food_pp_wasted"]
    idx1 = fcol_in_mdf["cereal_dmd_food_pp"]
    idx2 = fcol_in_mdf["Fraction_of_food_wasted"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # oth_crop_dmd_pp[region] = oth_crop_dmd_pp_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + oth_crop_dmd_pp_b[region]
    idxlhs = fcol_in_mdf["oth_crop_dmd_pp"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (oth_crop_dmd_pp_a[j]
        * math.log(mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl)
        + oth_crop_dmd_pp_b[j]
      )

    # oth_crop_dmd_food_pp[region] = oth_crop_dmd_pp[region] * UNIT_conv_to_kg_crop_ppy
    idxlhs = fcol_in_mdf["oth_crop_dmd_food_pp"]
    idx1 = fcol_in_mdf["oth_crop_dmd_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_kg_crop_ppy

    # oth_crop_dmd_food_pp_consumed[region] = oth_crop_dmd_food_pp[region] * ( 1 - Food_wasted_in_1980[region] )
    idxlhs = fcol_in_mdf["oth_crop_dmd_food_pp_consumed"]
    idx1 = fcol_in_mdf["oth_crop_dmd_food_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - Food_wasted_in_1980[j])

    # oth_crop_dmd_food_pp_wasted[region] = oth_crop_dmd_food_pp[region] * Fraction_of_food_wasted[region]
    idxlhs = fcol_in_mdf["oth_crop_dmd_food_pp_wasted"]
    idx1 = fcol_in_mdf["oth_crop_dmd_food_pp"]
    idx2 = fcol_in_mdf["Fraction_of_food_wasted"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # All_crop_dmd_food[region] = ( cereal_dmd_food_pp_consumed[region] + cereal_dmd_food_pp_wasted[region] + oth_crop_dmd_food_pp_consumed[region] + oth_crop_dmd_food_pp_wasted[region] ) * Population[region] / UNIT_conv_from_kg_to_Mt * UNIT_conv_btw_p_and_Mp
    idxlhs = fcol_in_mdf["All_crop_dmd_food"]
    idx1 = fcol_in_mdf["cereal_dmd_food_pp_consumed"]
    idx2 = fcol_in_mdf["cereal_dmd_food_pp_wasted"]
    idx3 = fcol_in_mdf["oth_crop_dmd_food_pp_consumed"]
    idx4 = fcol_in_mdf["oth_crop_dmd_food_pp_wasted"]
    idx5 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((
          mdf[rowi, idx1 + j]
          + mdf[rowi, idx2 + j]
          + mdf[rowi, idx3 + j]
          + mdf[rowi, idx4 + j]
        )
        * mdf[rowi, idx5 + j]
        / UNIT_conv_from_kg_to_Mt
        * UNIT_conv_btw_p_and_Mp
      )

    # Antarctic_ice_volume_km3 = INTEG ( - Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py , Antarctic_ice_volume_in_1980 )
    idx1 = fcol_in_mdf["Antarctic_ice_volume_km3"]
    idx2 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Arctic_ice_on_sea_area_km2 = INTEG ( - Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py , Arctic_ice_area_in_1980_km2 )
    idx1 = fcol_in_mdf["Arctic_ice_on_sea_area_km2"]
    idx2 = fcol_in_mdf["Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Barren_land_which_is_ice_and_snow[region] = INTEG ( future_deforestation[region] - historical_deforestation[region] - Reforestation_policy[region] , Barren_land_in_1980[region] )
    idx1 = fcol_in_mdf["Barren_land_which_is_ice_and_snow"]
    idx2 = fcol_in_mdf["future_deforestation"]
    idx3 = fcol_in_mdf["historical_deforestation"]
    idx4 = fcol_in_mdf["Reforestation_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # C_in_atmosphere_GtC = INTEG ( Avg_volcanic_activity_GtC_py + C_release_from_permafrost_melting_as_CO2_GtC_py + CH4_in_the_atmosphere_converted_to_CO2 + CO2_flux_GRASS_to_atm_GtC_py + CO2_flux_NF_to_atm_GtC_py + CO2_flux_TROP_to_atm_GtC_py + CO2_flux_TUNDRA_to_atm + Man_made_fossil_C_emissions_GtC_py - C_diffusion_into_ocean_from_atm_net - Carbon_captured_and_stored_GtC_py - CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py - CO2_flux_from_atm_to_NF_for_new_growth_GtC_py - CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py - CO2_flux_from_atm_to_TUNDRA_for_new_growth , C_in_atmosphere_in_1980 )
    idx1 = fcol_in_mdf["C_in_atmosphere_GtC"]
    idx2 = fcol_in_mdf["Avg_volcanic_activity_GtC_py"]
    idx3 = fcol_in_mdf["C_release_from_permafrost_melting_as_CO2_GtC_py"]
    idx4 = fcol_in_mdf["CH4_in_the_atmosphere_converted_to_CO2"]
    idx5 = fcol_in_mdf["CO2_flux_GRASS_to_atm_GtC_py"]
    idx6 = fcol_in_mdf["CO2_flux_NF_to_atm_GtC_py"]
    idx7 = fcol_in_mdf["CO2_flux_TROP_to_atm_GtC_py"]
    idx8 = fcol_in_mdf["CO2_flux_TUNDRA_to_atm"]
    idx9 = fcol_in_mdf["Man_made_fossil_C_emissions_GtC_py"]
    idx10 = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    idx11 = fcol_in_mdf["Carbon_captured_and_stored_GtC_py"]
    idx12 = fcol_in_mdf["CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py"]
    idx13 = fcol_in_mdf["CO2_flux_from_atm_to_NF_for_new_growth_GtC_py"]
    idx14 = fcol_in_mdf["CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py"]
    idx15 = fcol_in_mdf["CO2_flux_from_atm_to_TUNDRA_for_new_growth"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        + mdf[rowi - 1, idx5]
        + mdf[rowi - 1, idx6]
        + mdf[rowi - 1, idx7]
        + mdf[rowi - 1, idx8]
        + mdf[rowi - 1, idx9]
        - mdf[rowi - 1, idx10]
        - mdf[rowi - 1, idx11]
        - mdf[rowi - 1, idx12]
        - mdf[rowi - 1, idx13]
        - mdf[rowi - 1, idx14]
        - mdf[rowi - 1, idx15]
      )
      * dt
    )

    # C_in_atmosphere_in_form_of_CH4 = INTEG ( CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py + Human_activity_CH4_emissions + Natural_CH4_emissions - CH4_conversion_to_CO2_and_H2O , C_in_the_form_of_CH4_in_atm_1980 )
    idx1 = fcol_in_mdf["C_in_atmosphere_in_form_of_CH4"]
    idx2 = fcol_in_mdf["CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py"
    ]
    idx3 = fcol_in_mdf["Human_activity_CH4_emissions"]
    idx4 = fcol_in_mdf["Natural_CH4_emissions"]
    idx5 = fcol_in_mdf["CH4_conversion_to_CO2_and_H2O"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # C_in_cold_surface_water_GtC = INTEG ( C_diffusion_into_ocean_from_atm_net + Carbon_flow_from_warm_to_cold_surface_GtC_per_yr - Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr , Carbon_in_cold_ocean_0_to_100m_1850 )
    idx1 = fcol_in_mdf["C_in_cold_surface_water_GtC"]
    idx2 = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    idx3 = fcol_in_mdf["Carbon_flow_from_warm_to_cold_surface_GtC_per_yr"]
    idx4 = fcol_in_mdf["Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] + mdf[rowi - 1, idx3] - mdf[rowi - 1, idx4]) * dt
    )

    # C_in_cold_water_trunk_downwelling_GtC = INTEG ( Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr - Carbon_flow_from_cold_to_deep_GtC_per_yr , Carbon_in_cold_ocean_trunk_100m_to_bottom_1850 )
    idx1 = fcol_in_mdf["C_in_cold_water_trunk_downwelling_GtC"]
    idx2 = fcol_in_mdf["Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr"]
    idx3 = fcol_in_mdf["Carbon_flow_from_cold_to_deep_GtC_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # C_in_deep_water_volume_1km_to_bottom_GtC = INTEG ( Carbon_flow_from_cold_to_deep_GtC_per_yr - Depositing_of_C_to_sediment - Carbon_flow_from_deep , Carbon_in_ocean_deep_1k_to_bottom_ocean_1850 )
    idx1 = fcol_in_mdf["C_in_deep_water_volume_1km_to_bottom_GtC"]
    idx2 = fcol_in_mdf["Carbon_flow_from_cold_to_deep_GtC_per_yr"]
    idx3 = fcol_in_mdf["Depositing_of_C_to_sediment"]
    idx4 = fcol_in_mdf["Carbon_flow_from_deep"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3] - mdf[rowi - 1, idx4]) * dt
    )

    # C_in_intermediate_upwelling_water_100m_to_1km_GtC = INTEG ( Carbon_flow_from_deep - Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr , Carbon_in_ocean_upwelling_100m_to_1km_1850 )
    idx1 = fcol_in_mdf["C_in_intermediate_upwelling_water_100m_to_1km_GtC"]
    idx2 = fcol_in_mdf["Carbon_flow_from_deep"]
    idx3 = fcol_in_mdf["Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # C_in_permafrost_in_form_of_CH4 = INTEG ( - CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py , 1199.78 )
    idx1 = fcol_in_mdf["C_in_permafrost_in_form_of_CH4"]
    idx2 = fcol_in_mdf["CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py"
    ]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # C_in_warm_surface_water_GtC = INTEG ( Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr + C_runoff_from_biomass_soil - Biological_removal_of_C_from_WSW_GtC_per_yr - Carbon_flow_from_warm_to_cold_surface_GtC_per_yr , Carbon_in_warm_ocean_0_to_100m_1850 )
    idx1 = fcol_in_mdf["C_in_warm_surface_water_GtC"]
    idx2 = fcol_in_mdf["Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr"]
    idx3 = fcol_in_mdf["C_runoff_from_biomass_soil"]
    idx4 = fcol_in_mdf["Biological_removal_of_C_from_WSW_GtC_per_yr"]
    idx5 = fcol_in_mdf["Carbon_flow_from_warm_to_cold_surface_GtC_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # Capacity_under_construction[region] = INTEG ( Initiating_capacity_construction[region] - Adding_capacity[region] , Capacity_under_construction_in_1980[region] )
    idx1 = fcol_in_mdf["Capacity_under_construction"]
    idx2 = fcol_in_mdf["Initiating_capacity_construction"]
    idx3 = fcol_in_mdf["Adding_capacity"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Cold_surface_water_volume_Gm3 = INTEG ( Flow_of_water_from_warm_to_cold_surface_Gcubicm_per_yr - Flow_of_cold_surface_water_welling_down_GcubicM_per_yr , Volume_cold_ocean_0_to_100m )
    idx1 = fcol_in_mdf["Cold_surface_water_volume_Gm3"]
    idx2 = fcol_in_mdf["Flow_of_water_from_warm_to_cold_surface_Gcubicm_per_yr"]
    idx3 = fcol_in_mdf["Flow_of_cold_surface_water_welling_down_GcubicM_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Cold_water_volume_downwelling_Gm3 = INTEG ( Flow_of_cold_surface_water_welling_down_GcubicM_per_yr - Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr , Volume_cold_ocean_downwelling_100m_to_bottom )
    idx1 = fcol_in_mdf["Cold_water_volume_downwelling_Gm3"]
    idx2 = fcol_in_mdf["Flow_of_cold_surface_water_welling_down_GcubicM_per_yr"]
    idx3 = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Cropland[region] = INTEG ( acgl_to_c[region] + fa_to_c[region] - c_to_acgl[region] - c_to_pl[region] , Cropland_in_1980[region] )
    idx1 = fcol_in_mdf["Cropland"]
    idx2 = fcol_in_mdf["acgl_to_c"]
    idx3 = fcol_in_mdf["fa_to_c"]
    idx4 = fcol_in_mdf["c_to_acgl"]
    idx5 = fcol_in_mdf["c_to_pl"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (
          mdf[rowi - 1, idx2 + j]
          + mdf[rowi - 1, idx3 + j]
          - mdf[rowi - 1, idx4 + j]
          - mdf[rowi - 1, idx5 + j]
        )
        * dt
      )

    # Cumulative_N_use_since_2020[region] = INTEG ( Addition_to_N_use_over_the_years[region] , Cumulative_N_use_since_2020_in_1980[region] )
    idx1 = fcol_in_mdf["Cumulative_N_use_since_2020"]
    idx2 = fcol_in_mdf["Addition_to_N_use_over_the_years"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Cumulative_ocean_volume_increase_due_to_ice_melting_km3 = INTEG ( Antarctic_ice_melting_as_water_km3_py + Glacial_ice_melting_as_water_km3_py + Greenland_ice_melting_as_water_km3_py + Greenland_ice_melting_that_slid_into_the_ocean_km3_py , 46498.3 )
    idx1 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    idx2 = fcol_in_mdf["Antarctic_ice_melting_as_water_km3_py"]
    idx3 = fcol_in_mdf["Glacial_ice_melting_as_water_km3_py"]
    idx4 = fcol_in_mdf["Greenland_ice_melting_as_water_km3_py"]
    idx5 = fcol_in_mdf["Greenland_ice_melting_that_slid_into_the_ocean_km3_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        + mdf[rowi - 1, idx5]
      )
      * dt
    )

    # Deep_water_volume_1km_to_4km_Gm3 = INTEG ( Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr - Upwelling_from_deep , Volume_ocean_deep_1km_to_bottom )
    idx1 = fcol_in_mdf["Deep_water_volume_1km_to_4km_Gm3"]
    idx2 = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    idx3 = fcol_in_mdf["Upwelling_from_deep"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # DESERT_Mkm2 = INTEG ( Shifting_GRASS_to_DESERT_Mkm2_py - Shifting_DESERT_to_GRASS_Mkm2_py , 25.4039 )
    idx1 = fcol_in_mdf["DESERT_Mkm2"]
    idx2 = fcol_in_mdf["Shifting_GRASS_to_DESERT_Mkm2_py"]
    idx3 = fcol_in_mdf["Shifting_DESERT_to_GRASS_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Indicated_inequality_index_higher_is_more_unequal[region] = 1 + Strength_of_inequality_proxy * ( Worker_share_of_output_with_unemployment_effect_in_1980[region] / Worker_share_of_output_with_unemployment_effect[region] - 1 )
    idxlhs = fcol_in_mdf["Indicated_inequality_index_higher_is_more_unequal"]
    idx1 = fcol_in_mdf["Worker_share_of_output_with_unemployment_effect"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + Strength_of_inequality_proxy * (
        Worker_share_of_output_with_unemployment_effect_in_1980[j] / mdf[rowi, idx1 + j]
        - 1
      )

    # JR_inequality_effect_on_logistic_k[region] = 1 + JR_sINEeolLOK_lt_0 * ( Indicated_inequality_index_higher_is_more_unequal[region] / 0.5 - 1 )
    idxlhs = fcol_in_mdf["JR_inequality_effect_on_logistic_k"]
    idx1 = fcol_in_mdf["Indicated_inequality_index_higher_is_more_unequal"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + JR_sINEeolLOK_lt_0 * (mdf[rowi, idx1 + j] / 0.5 - 1)

    # Logistic_k[region] = Normal_k * JR_inequality_effect_on_logistic_k[region]
    idxlhs = fcol_in_mdf["Logistic_k"]
    idx1 = fcol_in_mdf["JR_inequality_effect_on_logistic_k"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Normal_k * mdf[rowi, idx1 + j]

    # Indicated_Existential_minimum_income = INTEG ( Increase_in_existential_minimum_income , 2.5 )
    idx1 = fcol_in_mdf["Indicated_Existential_minimum_income"]
    idx2 = fcol_in_mdf["Increase_in_existential_minimum_income"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2]) * dt

    # Existential_minimum_income = SMOOTH ( Indicated_Existential_minimum_income , Time_to_adjust_Existential_minimum_income )
    idx1 = fcol_in_mdf["Existential_minimum_income"]
    idx2 = fcol_in_mdf["Indicated_Existential_minimum_income"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Time_to_adjust_Existential_minimum_income
      * dt
    )

    # Fraction_of_population_below_existential_minimum[region] = 1 - ( 0.975 / ( 1 + math.exp ( - Logistic_k[region] * ( ( GDPpp_USED[region] - Existential_minimum_income ) / UNIT_conv_to_dmnl ) ) ) )
    idxlhs = fcol_in_mdf["Fraction_of_population_below_existential_minimum"]
    idx1 = fcol_in_mdf["Logistic_k"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    idx3 = fcol_in_mdf["Existential_minimum_income"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        0.975
        / (
          1
          + math.exp(
            -mdf[rowi, idx1 + j]
            * ((mdf[rowi, idx2 + j] - mdf[rowi, idx3]) / UNIT_conv_to_dmnl)
          )
        )
      )

    # Effect_of_poverty_on_social_tension[region] = WITH LOOKUP ( Fraction_of_population_below_existential_minimum[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.1 , 0.7 ) , ( 0.25 , 0.4 ) , ( 0.5 , 0.2 ) , ( 0.75 , 0.15 ) , ( 1 , 0.1 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_poverty_on_social_tension"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_poverty_on_social_tension"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Fraction_of_population_below_existential_minimum"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Forest_land[region] = INTEG ( acgl_to_fa[region] + historical_deforestation[region] + Reforestation_policy[region] - fa_to_c[region] - fa_to_gl[region] - future_deforestation[region] , Forest_land_in_1980[region] )
    idx1 = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["acgl_to_fa"]
    idx3 = fcol_in_mdf["historical_deforestation"]
    idx4 = fcol_in_mdf["Reforestation_policy"]
    idx5 = fcol_in_mdf["fa_to_c"]
    idx6 = fcol_in_mdf["fa_to_gl"]
    idx7 = fcol_in_mdf["future_deforestation"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (
          mdf[rowi - 1, idx2 + j]
          + mdf[rowi - 1, idx3 + j]
          + mdf[rowi - 1, idx4 + j]
          - mdf[rowi - 1, idx5 + j]
          - mdf[rowi - 1, idx6 + j]
          - mdf[rowi - 1, idx7 + j]
        )
        * dt
      )

    # Fossil_fuel_reserves_in_ground_GtC = INTEG ( - Man_made_fossil_C_emissions_GtC_py , Fossil_fuel_reserves_in_ground_at_initial_time_GtC )
    idx1 = fcol_in_mdf["Fossil_fuel_reserves_in_ground_GtC"]
    idx2 = fcol_in_mdf["Man_made_fossil_C_emissions_GtC_py"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Fraction_of_people_outside_of_labour_market_FOPOLM[region] = INTEG ( Change_in_Fraction_of_people_outside_of_labour_market[region] , Frac_outside_of_labour_pool_in_1980[region] )
    idx1 = fcol_in_mdf["Fraction_of_people_outside_of_labour_market_FOPOLM"]
    idx2 = fcol_in_mdf["Change_in_Fraction_of_people_outside_of_labour_market"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Glacial_ice_volume_km3 = INTEG ( - Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py , Glacial_ice_volume_in_1980 )
    idx1 = fcol_in_mdf["Glacial_ice_volume_km3"]
    idx2 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Global_speculative_asset_pool_relative_to_init = INTEG ( increase_in_global_speculative_asset_pool - decrease_in_global_speculative_asset_pool , 0 )
    idx1 = fcol_in_mdf["Global_speculative_asset_pool_relative_to_init"]
    idx2 = fcol_in_mdf["increase_in_global_speculative_asset_pool"]
    idx3 = fcol_in_mdf["decrease_in_global_speculative_asset_pool"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Govt_in_default_to_private_lenders[region] = INTEG ( Govt_defaulting[region] - Govt_defaults_written_off[region] , 0 )
    idx1 = fcol_in_mdf["Govt_in_default_to_private_lenders"]
    idx2 = fcol_in_mdf["Govt_defaulting"]
    idx3 = fcol_in_mdf["Govt_defaults_written_off"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # GRASS_area_burnt_Mkm2 = INTEG ( GRASS_burning_Mkm2_py - GRASS_regrowing_after_being_burnt_Mkm2_py , GRASS_area_burned_in_1980 )
    idx1 = fcol_in_mdf["GRASS_area_burnt_Mkm2"]
    idx2 = fcol_in_mdf["GRASS_burning_Mkm2_py"]
    idx3 = fcol_in_mdf["GRASS_regrowing_after_being_burnt_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # GRASS_area_harvested_Mkm2 = INTEG ( GRASS_being_harvested_Mkm2_py - GRASS_regrowing_after_harvesting_Mkm2_py , GRASS_area_harvested_in_1980 )
    idx1 = fcol_in_mdf["GRASS_area_harvested_Mkm2"]
    idx2 = fcol_in_mdf["GRASS_being_harvested_Mkm2_py"]
    idx3 = fcol_in_mdf["GRASS_regrowing_after_harvesting_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # GRASS_Biomass_locked_in_construction_material_GtBiomass = INTEG ( GRASS_for_construction_use - GRASS_Biomass_in_construction_material_being_burnt - GRASS_Biomass_in_construction_material_left_to_rot , GRASS_Biomass_locked_in_construction_material_in_1980 )
    idx1 = fcol_in_mdf["GRASS_Biomass_locked_in_construction_material_GtBiomass"]
    idx2 = fcol_in_mdf["GRASS_for_construction_use"]
    idx3 = fcol_in_mdf["GRASS_Biomass_in_construction_material_being_burnt"]
    idx4 = fcol_in_mdf["GRASS_Biomass_in_construction_material_left_to_rot"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3] - mdf[rowi - 1, idx4]) * dt
    )

    # GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( GRASS_Biomass_in_construction_material_left_to_rot + GRASS_Living_biomass_rotting - GRASS_Dead_biomass_decomposing - GRASS_DeadB_SOM_being_lost_due_to_deforestation - GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting - GRASS_runoff - GRASS_soil_degradation_from_forest_fires , GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
    idx1 = fcol_in_mdf["GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    idx2 = fcol_in_mdf["GRASS_Biomass_in_construction_material_left_to_rot"]
    idx3 = fcol_in_mdf["GRASS_Living_biomass_rotting"]
    idx4 = fcol_in_mdf["GRASS_Dead_biomass_decomposing"]
    idx5 = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_deforestation"]
    idx6 = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx7 = fcol_in_mdf["GRASS_runoff"]
    idx8 = fcol_in_mdf["GRASS_soil_degradation_from_forest_fires"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
        - mdf[rowi - 1, idx8]
      )
      * dt
    )

    # GRASS_deforested_Mkm2 = INTEG ( GRASS_being_deforested_Mkm2_py - GRASS_regrowing_after_being_deforested_Mkm2_py , GRASS_area_deforested_in_1980 )
    idx1 = fcol_in_mdf["GRASS_deforested_Mkm2"]
    idx2 = fcol_in_mdf["GRASS_being_deforested_Mkm2_py"]
    idx3 = fcol_in_mdf["GRASS_regrowing_after_being_deforested_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # GRASS_Living_biomass_GtBiomass = INTEG ( GRASS_biomass_new_growing - GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting - GRASS_for_construction_use - GRASS_Living_biomass_rotting , GRASS_Living_biomass_in_1980 )
    idx1 = fcol_in_mdf["GRASS_Living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["GRASS_biomass_new_growing"]
    idx3 = fcol_in_mdf["GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["GRASS_for_construction_use"]
    idx5 = fcol_in_mdf["GRASS_Living_biomass_rotting"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        - mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # GRASS_potential_area_Mkm2 = INTEG ( Shifting_NF_to_GRASS_Mkm2_py + Shifting_TROP_to_GRASS_Mkm2_py + Shifting_DESERT_to_GRASS_Mkm2_py - Shifting_GRASS_to_DESERT_Mkm2_py - Shifting_GRASS_to_NF_Mkm2_py - Shifting_GRASS_to_TROP_Mkm2_py , 22.5095 )
    idx1 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["Shifting_NF_to_GRASS_Mkm2_py"]
    idx3 = fcol_in_mdf["Shifting_TROP_to_GRASS_Mkm2_py"]
    idx4 = fcol_in_mdf["Shifting_DESERT_to_GRASS_Mkm2_py"]
    idx5 = fcol_in_mdf["Shifting_GRASS_to_DESERT_Mkm2_py"]
    idx6 = fcol_in_mdf["Shifting_GRASS_to_NF_Mkm2_py"]
    idx7 = fcol_in_mdf["Shifting_GRASS_to_TROP_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
      )
      * dt
    )

    # Grazing_land[region] = INTEG ( fa_to_gl[region] + acgl_to_gl[region] - gl_to_acgl[region] , Grazing_land_in_1980[region] )
    idx1 = fcol_in_mdf["Grazing_land"]
    idx2 = fcol_in_mdf["fa_to_gl"]
    idx3 = fcol_in_mdf["acgl_to_gl"]
    idx4 = fcol_in_mdf["gl_to_acgl"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] + mdf[rowi - 1, idx3 + j] - mdf[rowi - 1, idx4 + j])
        * dt
      )

    # Greenland_ice_volume_on_Greenland_km3 = INTEG ( - Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py - Greenland_ice_sliding_into_the_ocean_km3_py , Greenland_ice_volume_in_1980 )
    idx1 = fcol_in_mdf["Greenland_ice_volume_on_Greenland_km3"]
    idx2 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx3 = fcol_in_mdf["Greenland_ice_sliding_into_the_ocean_km3_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Greenland_ice_volume_that_slid_into_the_ocean_km3 = INTEG ( Greenland_ice_sliding_into_the_ocean_km3_py - Greenland_ice_that_slid_into_the_ocean_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
    idx1 = fcol_in_mdf["Greenland_ice_volume_that_slid_into_the_ocean_km3"]
    idx2 = fcol_in_mdf["Greenland_ice_sliding_into_the_ocean_km3_py"]
    idx3 = fcol_in_mdf["Greenland_ice_that_slid_into_the_ocean_melting_is_pos_or_freezing_is_neg_km3_py"
    ]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Heat_in_atmosphere_ZJ = INTEG ( Convection_aka_sensible_heat_flow + Evaporation_aka_latent_heat_flow + LW_surface_emissions_NOT_escaping_through_atm_window + SW_Atmospheric_absorption - Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py - LW_clear_sky_emissions_to_surface - LW_TOA_radiation_from_atm_to_space , Heat_in_atmosphere_in_1980 )
    idx1 = fcol_in_mdf["Heat_in_atmosphere_ZJ"]
    idx2 = fcol_in_mdf["Convection_aka_sensible_heat_flow"]
    idx3 = fcol_in_mdf["Evaporation_aka_latent_heat_flow"]
    idx4 = fcol_in_mdf["LW_surface_emissions_NOT_escaping_through_atm_window"]
    idx5 = fcol_in_mdf["SW_Atmospheric_absorption"]
    idx6 = fcol_in_mdf["Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py"
    ]
    idx7 = fcol_in_mdf["LW_clear_sky_emissions_to_surface"]
    idx8 = fcol_in_mdf["LW_TOA_radiation_from_atm_to_space"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        + mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
        - mdf[rowi - 1, idx8]
      )
      * dt
    )

    # Heat_in_deep_ZJ = INTEG ( Heat_flow_from_the_earths_core + Net_heat_flow_ocean_from_surface_to_deep_ZJ_py , Heat_in_ocean_deep_in_1980 )
    idx1 = fcol_in_mdf["Heat_in_deep_ZJ"]
    idx2 = fcol_in_mdf["Net_heat_flow_ocean_from_surface_to_deep_ZJ_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (Heat_flow_from_the_earths_core + mdf[rowi - 1, idx2]) * dt
    )

    # Heat_in_surface = INTEG ( LW_clear_sky_emissions_to_surface + LW_re_radiated_by_clouds + SW_surface_absorption - Convection_aka_sensible_heat_flow - Evaporation_aka_latent_heat_flow - Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py - Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py - Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_Greenland_ice_that_slid_into_the_ocean_ZJ_py - LW_surface_emission - Net_heat_flow_ocean_from_surface_to_deep_ZJ_py , Heat_in_surface_in_1980 )
    idx1 = fcol_in_mdf["Heat_in_surface"]
    idx2 = fcol_in_mdf["LW_clear_sky_emissions_to_surface"]
    idx3 = fcol_in_mdf["LW_re_radiated_by_clouds"]
    idx4 = fcol_in_mdf["SW_surface_absorption"]
    idx5 = fcol_in_mdf["Convection_aka_sensible_heat_flow"]
    idx6 = fcol_in_mdf["Evaporation_aka_latent_heat_flow"]
    idx7 = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py"
    ]
    idx8 = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py"
    ]
    idx9 = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_Greenland_ice_that_slid_into_the_ocean_ZJ_py"
    ]
    idx10 = fcol_in_mdf["LW_surface_emission"]
    idx11 = fcol_in_mdf["Net_heat_flow_ocean_from_surface_to_deep_ZJ_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
        - mdf[rowi - 1, idx8]
        - mdf[rowi - 1, idx9]
        - mdf[rowi - 1, idx10]
        - mdf[rowi - 1, idx11]
      )
      * dt
    )

    # Temp_surface_average_K = Heat_in_surface * Conversion_heat_surface_to_temp
    idxlhs = fcol_in_mdf["Temp_surface_average_K"]
    idx1 = fcol_in_mdf["Heat_in_surface"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Conversion_heat_surface_to_temp

    # Temp_surface = Temp_surface_average_K - 273.15
    idxlhs = fcol_in_mdf["Temp_surface"]
    idx1 = fcol_in_mdf["Temp_surface_average_K"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - 273.15

    # Temp_surface_anomaly_compared_to_1850_degC = Temp_surface - ( Temp_surface_1850 - 273.15 )
    idxlhs = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - (Temp_surface_1850 - 273.15)

    # Evaporation_as_f_of_temp = ( Incoming_solar_in_1850_ZJ_py * Evaporation_as_fraction_of_incoming_solar_in_1850 ) * ( 1 + Sensitivity_of_evaporation_to_temp * ( Temp_surface_anomaly_compared_to_1850_degC / Reference_temp_C ) )
    idxlhs = fcol_in_mdf["Evaporation_as_f_of_temp"]
    idx1 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    mdf[rowi, idxlhs] = (
      Incoming_solar_in_1850_ZJ_py * Evaporation_as_fraction_of_incoming_solar_in_1850
    ) * (1 + Sensitivity_of_evaporation_to_temp * (mdf[rowi, idx1] / Reference_temp_C))

    # Humidity_of_atmosphere = Evaporation_as_f_of_temp * Water_content_of_evaporation_g_p_kg_per_ZJ_py
    idxlhs = fcol_in_mdf["Humidity_of_atmosphere"]
    idx1 = fcol_in_mdf["Evaporation_as_f_of_temp"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Water_content_of_evaporation_g_p_kg_per_ZJ_py

    # Intermediate_upwelling_water_volume_100m_to_1km_Gm3 = INTEG ( Upwelling_from_deep - Upwelling_to_surface , Volume_ocean_upwelling_100m_to_1km )
    idx1 = fcol_in_mdf["Intermediate_upwelling_water_volume_100m_to_1km_Gm3"]
    idx2 = fcol_in_mdf["Upwelling_from_deep"]
    idx3 = fcol_in_mdf["Upwelling_to_surface"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Inventory[region] = INTEG ( Output[region] - Sales[region] , Inventory_in_1980[region] )
    idx1 = fcol_in_mdf["Inventory"]
    idx2 = fcol_in_mdf["Output"]
    idx3 = fcol_in_mdf["Sales"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Kyoto_Fluor_gases_in_atm = INTEG ( Kyoto_Fluor_emissions - Kyoto_Fluor_degradation , 361.575 )
    idx1 = fcol_in_mdf["Kyoto_Fluor_gases_in_atm"]
    idx2 = fcol_in_mdf["Kyoto_Fluor_emissions"]
    idx3 = fcol_in_mdf["Kyoto_Fluor_degradation"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Temp_atm_average_K = Heat_in_atmosphere_ZJ * Conversion_heat_atm_to_temp
    idxlhs = fcol_in_mdf["Temp_atm_average_K"]
    idx1 = fcol_in_mdf["Heat_in_atmosphere_ZJ"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Conversion_heat_atm_to_temp

    # BB_radiation_at_Temp_in_atm_ZJ_py = Emissivity_atm * Stephan_Boltzmann_constant * Temp_atm_average_K ^ 4 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["BB_radiation_at_Temp_in_atm_ZJ_py"]
    idx1 = fcol_in_mdf["Temp_atm_average_K"]
    mdf[rowi, idxlhs] = (
      Emissivity_atm
      * Stephan_Boltzmann_constant
      * mdf[rowi, idx1] ** 4
      * UNIT_conversion_W_p_m2_earth_to_ZJ_py
    )

    # BB_radiation_at_surface_temp_ZJ_py = Emissivity_surface * Stephan_Boltzmann_constant * Temp_surface_average_K ^ 4 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["BB_radiation_at_surface_temp_ZJ_py"]
    idx1 = fcol_in_mdf["Temp_surface_average_K"]
    mdf[rowi, idxlhs] = (
      Emissivity_surface
      * Stephan_Boltzmann_constant
      * mdf[rowi, idx1] ** 4
      * UNIT_conversion_W_p_m2_earth_to_ZJ_py
    )

    # LW_surface_emission = BB_radiation_at_surface_temp_ZJ_py
    idxlhs = fcol_in_mdf["LW_surface_emission"]
    idx1 = fcol_in_mdf["BB_radiation_at_surface_temp_ZJ_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # LW_surface_emissions_escaping_through_atm_window = LW_surface_emission * Frac_of_surface_emission_through_atm_window
    idxlhs = fcol_in_mdf["LW_surface_emissions_escaping_through_atm_window"]
    idx1 = fcol_in_mdf["LW_surface_emission"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Frac_of_surface_emission_through_atm_window

    # MODEL_CO2_concentration_in_atmosphere2_ppm = C_in_atmosphere_GtC / Conversion_constant_GtC_to_ppm
    idxlhs = fcol_in_mdf["MODEL_CO2_concentration_in_atmosphere2_ppm"]
    idx1 = fcol_in_mdf["C_in_atmosphere_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Conversion_constant_GtC_to_ppm

    # CO2_concentration_used_after_any_experiments_ppm = MODEL_CO2_concentration_in_atmosphere2_ppm
    idxlhs = fcol_in_mdf["CO2_concentration_used_after_any_experiments_ppm"]
    idx1 = fcol_in_mdf["MODEL_CO2_concentration_in_atmosphere2_ppm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # CO2_concentration_ppm = CO2_concentration_used_after_any_experiments_ppm
    idxlhs = fcol_in_mdf["CO2_concentration_ppm"]
    idx1 = fcol_in_mdf["CO2_concentration_used_after_any_experiments_ppm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Fraction_blocked_by_CO2_spectrum = WITH LOOKUP ( CO2_concentration_ppm , ( [ ( 0 , 0 ) - ( 1000 , 0.2 ) ] , ( 0 , 0 ) , ( 40 , 0.0508772 ) , ( 100 , 0.0756579 ) , ( 200 , 0.085978 ) , ( 285 , 0.091138 ) , ( 300 , 0.0919195 ) , ( 400 , 0.0960065 ) , ( 500 , 0.0993184 ) , ( 570 , 0.10117 ) , ( 600 , 0.1019 ) , ( 800 , 0.106134 ) , ( 1000 , 0.109347 ) , ( 10000 , 0.146835 ) ) )
    tabidx = ftab_in_d_table[  "Fraction_blocked_by_CO2_spectrum"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Fraction_blocked_by_CO2_spectrum"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["CO2_concentration_ppm"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Blocked_by_CO2 = Fraction_blocked_by_CO2_spectrum
    idxlhs = fcol_in_mdf["Blocked_by_CO2"]
    idx1 = fcol_in_mdf["Fraction_blocked_by_CO2_spectrum"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # MODEL_CH4_in_atm_in_ppb = C_in_atmosphere_in_form_of_CH4 * conversion_factor_CH4_Gt_to_ppb
    idxlhs = fcol_in_mdf["MODEL_CH4_in_atm_in_ppb"]
    idx1 = fcol_in_mdf["C_in_atmosphere_in_form_of_CH4"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * conversion_factor_CH4_Gt_to_ppb

    # CH4_concentration_ppb = MODEL_CH4_in_atm_in_ppb
    idxlhs = fcol_in_mdf["CH4_concentration_ppb"]
    idx1 = fcol_in_mdf["MODEL_CH4_in_atm_in_ppb"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Fraction_blocked_by_CH4_spectrum = WITH LOOKUP ( CH4_concentration_ppb , ( [ ( 0 , 0 ) - ( 1e+06 , 0.2 ) ] , ( 0 , 0 ) , ( 350 , 0.0028 ) , ( 700 , 0.0042 ) , ( 1200 , 0.0056 ) , ( 1700 , 0.007 ) , ( 3000 , 0.0106 ) , ( 5000 , 0.0125 ) , ( 7000 , 0.013477 ) , ( 10000 , 0.0153945 ) , ( 20000 , 0.0201881 ) , ( 40000 , 0.0259404 ) , ( 70000 , 0.0316927 ) , ( 100000 , 0.0355276 ) , ( 150000 , 0.0403212 ) , ( 250000 , 0.0456888 ) , ( 500000 , 0.0539356 ) , ( 1e+06 , 0.0625641 ) , ( 1e+07 , 0.0954476 ) , ( 1e+08 , 0.130154 ) , ( 5e+08 , 0.152204 ) , ( 9e+08 , 0.159776 ) , ( 1e+09 , 0.16112 ) ) )
    tabidx = ftab_in_d_table[  "Fraction_blocked_by_CH4_spectrum"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Fraction_blocked_by_CH4_spectrum"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["CH4_concentration_ppb"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Blocked_by_CH4 = Fraction_blocked_by_CH4_spectrum
    idxlhs = fcol_in_mdf["Blocked_by_CH4"]
    idx1 = fcol_in_mdf["Fraction_blocked_by_CH4_spectrum"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Humidity_of_atmosphere_current_g_p_kg = Humidity_of_atmosphere
    idxlhs = fcol_in_mdf["Humidity_of_atmosphere_current_g_p_kg"]
    idx1 = fcol_in_mdf["Humidity_of_atmosphere"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Blocked_by_H20_Table_lookup = WITH LOOKUP ( Humidity_of_atmosphere_current_g_p_kg , ( [ ( 1.7 , 0 ) - ( 2.5 , 0.2 ) ] , ( 1.76 , 0.06 ) , ( 1.85 , 0.0638 ) , ( 1.9 , 0.0649123 ) , ( 1.95 , 0.071 ) , ( 1.97 , 0.0753 ) , ( 1.99 , 0.081 ) , ( 2.00026 , 0.0846 ) , ( 2.02999 , 0.092 ) , ( 2.05039 , 0.0976 ) , ( 2.07286 , 0.1025 ) , ( 2.10017 , 0.109 ) , ( 2.11642 , 0.113 ) , ( 2.14996 , 0.1205 ) , ( 2.16275 , 0.1235 ) , ( 2.18522 , 0.129 ) , ( 2.20009 , 0.132 ) , ( 2.21288 , 0.135 ) , ( 2.235 , 0.14 ) , ( 2.25022 , 0.144 ) , ( 2.26992 , 0.148 ) , ( 2.3 , 0.155 ) , ( 2.4 , 0.174 ) , ( 2.5 , 0.19 ) ) )
    tabidx = ftab_in_d_table["Blocked_by_H20_Table_lookup"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Blocked_by_H20_Table_lookup"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Humidity_of_atmosphere_current_g_p_kg"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Blocked_by_H20 = Blocked_by_H20_Table_lookup
    idxlhs = fcol_in_mdf["Blocked_by_H20"]
    idx1 = fcol_in_mdf["Blocked_by_H20_Table_lookup"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Kyoto_Fluor_concentration_ppt = Kyoto_Fluor_gases_in_atm * Conversion_from_Kyoto_Fluor_amount_to_concentration_ppt_p_kt
    idxlhs = fcol_in_mdf["Kyoto_Fluor_concentration_ppt"]
    idx1 = fcol_in_mdf["Kyoto_Fluor_gases_in_atm"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Conversion_from_Kyoto_Fluor_amount_to_concentration_ppt_p_kt
    )

    # Blocking_multiplier_from_Kyoto_Fluor = IF_THEN_ELSE ( zeit > 1970 , 1 + Slope_btw_Kyoto_Fluor_ppt_and_blocking_multiplier / 1000 * ( Kyoto_Fluor_concentration_ppt / Kyoto_Fluor_concentration_in_1970_ppt - 1 ) , 1 )
    idxlhs = fcol_in_mdf["Blocking_multiplier_from_Kyoto_Fluor"]
    idx1 = fcol_in_mdf["Kyoto_Fluor_concentration_ppt"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 1970,   1
      + Slope_btw_Kyoto_Fluor_ppt_and_blocking_multiplier
      / 1000
      * (mdf[rowi, idx1] / Kyoto_Fluor_concentration_in_1970_ppt - 1),   1, )

    # Montreal_gases_in_atm = INTEG ( Montreal_gases_emissions - Montreal_gases_degradation , 16239.5 )
    idx1 = fcol_in_mdf["Montreal_gases_in_atm"]
    idx2 = fcol_in_mdf["Montreal_gases_emissions"]
    idx3 = fcol_in_mdf["Montreal_gases_degradation"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Montreal_gases_concentration_ppt = Montreal_gases_in_atm * Conversion_from_Montreal_gases_amount_to_concentration_ppt_p_kt
    idxlhs = fcol_in_mdf["Montreal_gases_concentration_ppt"]
    idx1 = fcol_in_mdf["Montreal_gases_in_atm"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Conversion_from_Montreal_gases_amount_to_concentration_ppt_p_kt
    )

    # Blocking_multiplier_from_Montreal_gases = IF_THEN_ELSE ( zeit > 1970 , 1 + Slope_btw_Montreal_gases_ppt_and_blocking_multiplier / 100 * ( Montreal_gases_concentration_ppt / Montreal_gases_concentration_in_1970_ppt - 1 ) , 1 )
    idxlhs = fcol_in_mdf["Blocking_multiplier_from_Montreal_gases"]
    idx1 = fcol_in_mdf["Montreal_gases_concentration_ppt"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 1970,   1
      + Slope_btw_Montreal_gases_ppt_and_blocking_multiplier
      / 100
      * (mdf[rowi, idx1] / Montreal_gases_concentration_in_1970_ppt - 1),   1, )

    # N2O_in_atmosphere_MtN2O = INTEG ( All_N2O_emissions - N2O_degradation_MtN2O_py , N2O_in_atmosphere_MtN2O_in_1980 )
    idx1 = fcol_in_mdf["N2O_in_atmosphere_MtN2O"]
    idx2 = fcol_in_mdf["All_N2O_emissions"]
    idx3 = fcol_in_mdf["N2O_degradation_MtN2O_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # N2O_concentration_ppb = N2O_in_atmosphere_MtN2O * UNIT_Conversion_from_N2O_amount_to_concentration_ppb_p_MtN2O
    idxlhs = fcol_in_mdf["N2O_concentration_ppb"]
    idx1 = fcol_in_mdf["N2O_in_atmosphere_MtN2O"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * UNIT_Conversion_from_N2O_amount_to_concentration_ppb_p_MtN2O
    )

    # Blocking_multiplier_from_N2O = 1 + Slope_btw_N2O_ppb_and_blocking_multiplier * ( N2O_concentration_ppb / Model_N2O_concentration_in_1850_ppb - 1 )
    idxlhs = fcol_in_mdf["Blocking_multiplier_from_N2O"]
    idx1 = fcol_in_mdf["N2O_concentration_ppb"]
    mdf[rowi, idxlhs] = 1 + Slope_btw_N2O_ppb_and_blocking_multiplier * (
      mdf[rowi, idx1] / Model_N2O_concentration_in_1850_ppb - 1
    )

    # LW_Blocking_multiplier_from_other_GHG = ( Blocking_multiplier_from_Kyoto_Fluor + Blocking_multiplier_from_Montreal_gases + Blocking_multiplier_from_N2O ) / 3
    idxlhs = fcol_in_mdf["LW_Blocking_multiplier_from_other_GHG"]
    idx1 = fcol_in_mdf["Blocking_multiplier_from_Kyoto_Fluor"]
    idx2 = fcol_in_mdf["Blocking_multiplier_from_Montreal_gases"]
    idx3 = fcol_in_mdf["Blocking_multiplier_from_N2O"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]) / 3

    # Fraction_blocked_by_other_GHG = LW_radiation_fraction_blocked_by_other_GHG_in_1850 * LW_Blocking_multiplier_from_other_GHG
    idxlhs = fcol_in_mdf["Fraction_blocked_by_other_GHG"]
    idx1 = fcol_in_mdf["LW_Blocking_multiplier_from_other_GHG"]
    mdf[rowi, idxlhs] = (
      LW_radiation_fraction_blocked_by_other_GHG_in_1850 * mdf[rowi, idx1]
    )

    # Blocked_by_otherGHG = Fraction_blocked_by_other_GHG
    idxlhs = fcol_in_mdf["Blocked_by_otherGHG"]
    idx1 = fcol_in_mdf["Fraction_blocked_by_other_GHG"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Frac_blocked_by_ALL_GHG = Blocked_by_CO2 + Blocked_by_CH4 + Blocked_by_H20 + Blocked_by_otherGHG
    idxlhs = fcol_in_mdf["Frac_blocked_by_ALL_GHG"]
    idx1 = fcol_in_mdf["Blocked_by_CO2"]
    idx2 = fcol_in_mdf["Blocked_by_CH4"]
    idx3 = fcol_in_mdf["Blocked_by_H20"]
    idx4 = fcol_in_mdf["Blocked_by_otherGHG"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    )

    # LW_Clear_sky_emissions_from_atm = ( BB_radiation_at_Temp_in_atm_ZJ_py + LW_surface_emissions_escaping_through_atm_window ) * ( 1 - Frac_blocked_by_ALL_GHG )
    idxlhs = fcol_in_mdf["LW_Clear_sky_emissions_from_atm"]
    idx1 = fcol_in_mdf["BB_radiation_at_Temp_in_atm_ZJ_py"]
    idx2 = fcol_in_mdf["LW_surface_emissions_escaping_through_atm_window"]
    idx3 = fcol_in_mdf["Frac_blocked_by_ALL_GHG"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2]) * (1 - mdf[rowi, idx3])

    # Temp_surface_current_divided_by_value_in_1850_K_p_K = Temp_surface_average_K / Temp_surface_1850
    idxlhs = fcol_in_mdf["Temp_surface_current_divided_by_value_in_1850_K_p_K"]
    idx1 = fcol_in_mdf["Temp_surface_average_K"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Temp_surface_1850

    # Area_covered_by_low_clouds = Area_covered_by_low_clouds_in_1980 * ( 1 + Sensitivity_of_low_cloud_coverage_to_temp * ( Temp_surface_current_divided_by_value_in_1850_K_p_K - 1 ) )
    idxlhs = fcol_in_mdf["Area_covered_by_low_clouds"]
    idx1 = fcol_in_mdf["Temp_surface_current_divided_by_value_in_1850_K_p_K"]
    mdf[rowi, idxlhs] = Area_covered_by_low_clouds_in_1980 * (
      1 + Sensitivity_of_low_cloud_coverage_to_temp * (mdf[rowi, idx1] - 1)
    )

    # Ratio_of_area_covered_by_low_clouds_current_to_init = Area_covered_by_low_clouds / Area_covered_by_low_clouds_in_1980
    idxlhs = fcol_in_mdf["Ratio_of_area_covered_by_low_clouds_current_to_init"]
    idx1 = fcol_in_mdf["Area_covered_by_low_clouds"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Area_covered_by_low_clouds_in_1980

    # LW_LO_cloud_radiation = LW_LO_cloud_radiation_reference_in_1980 * UNIT_conversion_W_p_m2_earth_to_ZJ_py * Ratio_of_area_covered_by_low_clouds_current_to_init
    idxlhs = fcol_in_mdf["LW_LO_cloud_radiation"]
    idx1 = fcol_in_mdf["Ratio_of_area_covered_by_low_clouds_current_to_init"]
    mdf[rowi, idxlhs] = (
      LW_LO_cloud_radiation_reference_in_1980
      * UNIT_conversion_W_p_m2_earth_to_ZJ_py
      * mdf[rowi, idx1]
    )

    # Sensitivity_of_high_cloud_coverage_to_temp_logistics = Sensitivity_of_high_cloud_coverage_to_temp_normal + ( Logistics_curve_param_c / ( 1 + math.exp ( - Logistics_curve_param_k * ( zeit - Logistics_curve_param_shift ) ) ) )
    idxlhs = fcol_in_mdf["Sensitivity_of_high_cloud_coverage_to_temp_logistics"]
    mdf[rowi, idxlhs] = Sensitivity_of_high_cloud_coverage_to_temp_normal + (
      Logistics_curve_param_c
      / (1 + math.exp(-Logistics_curve_param_k * (zeit - Logistics_curve_param_shift)))
    )

    # Area_covered_by_high_clouds = Area_covered_by_high_clouds_in_1980 * ( 1 + Sensitivity_of_high_cloud_coverage_to_temp_logistics * ( Temp_surface_current_divided_by_value_in_1850_K_p_K - 1 ) )
    idxlhs = fcol_in_mdf["Area_covered_by_high_clouds"]
    idx1 = fcol_in_mdf["Sensitivity_of_high_cloud_coverage_to_temp_logistics"]
    idx2 = fcol_in_mdf["Temp_surface_current_divided_by_value_in_1850_K_p_K"]
    mdf[rowi, idxlhs] = Area_covered_by_high_clouds_in_1980 * (
      1 + mdf[rowi, idx1] * (mdf[rowi, idx2] - 1)
    )

    # Ratio_of_area_covered_by_high_clouds_current_to_init = Area_covered_by_high_clouds / Area_covered_by_high_clouds_in_1980
    idxlhs = fcol_in_mdf["Ratio_of_area_covered_by_high_clouds_current_to_init"]
    idx1 = fcol_in_mdf["Area_covered_by_high_clouds"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Area_covered_by_high_clouds_in_1980

    # LW_HI_cloud_radiation = LW_HI_cloud_radiation_reference_in_1980 * UNIT_conversion_W_p_m2_earth_to_ZJ_py * Ratio_of_area_covered_by_high_clouds_current_to_init
    idxlhs = fcol_in_mdf["LW_HI_cloud_radiation"]
    idx1 = fcol_in_mdf["Ratio_of_area_covered_by_high_clouds_current_to_init"]
    mdf[rowi, idxlhs] = (
      LW_HI_cloud_radiation_reference_in_1980
      * UNIT_conversion_W_p_m2_earth_to_ZJ_py
      * mdf[rowi, idx1]
    )

    # Blocking_of_LW_rad_by_clouds = LW_LO_cloud_radiation + LW_HI_cloud_radiation
    idxlhs = fcol_in_mdf["Blocking_of_LW_rad_by_clouds"]
    idx1 = fcol_in_mdf["LW_LO_cloud_radiation"]
    idx2 = fcol_in_mdf["LW_HI_cloud_radiation"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # LW_Cloudy_sky_emissions_from_atm = LW_Clear_sky_emissions_from_atm - Blocking_of_LW_rad_by_clouds
    idxlhs = fcol_in_mdf["LW_Cloudy_sky_emissions_from_atm"]
    idx1 = fcol_in_mdf["LW_Clear_sky_emissions_from_atm"]
    idx2 = fcol_in_mdf["Blocking_of_LW_rad_by_clouds"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # LW_TOA_radiation_from_atm_to_space = LW_Cloudy_sky_emissions_from_atm
    idxlhs = fcol_in_mdf["LW_TOA_radiation_from_atm_to_space"]
    idx1 = fcol_in_mdf["LW_Cloudy_sky_emissions_from_atm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # NF_area_burnt_Mkm2 = INTEG ( NF_burning_Mkm2_py - NF_regrowing_after_being_burnt_Mkm2_py , NF_area_burned_in_1980 )
    idx1 = fcol_in_mdf["NF_area_burnt_Mkm2"]
    idx2 = fcol_in_mdf["NF_burning_Mkm2_py"]
    idx3 = fcol_in_mdf["NF_regrowing_after_being_burnt_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # NF_area_clear_cut_Mkm2 = INTEG ( NF_being_harvested_by_clear_cutting_Mkm2_py - NF_regrowing_after_being_clear_cut_Mkm2_py , NF_area_clear_cut_in_1980 )
    idx1 = fcol_in_mdf["NF_area_clear_cut_Mkm2"]
    idx2 = fcol_in_mdf["NF_being_harvested_by_clear_cutting_Mkm2_py"]
    idx3 = fcol_in_mdf["NF_regrowing_after_being_clear_cut_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # NF_area_deforested_Mkm2 = INTEG ( NF_being_deforested_Mkm2_py - NF_regrowing_after_being_deforested_Mkm2_py , NF_area_deforested_in_1980 )
    idx1 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    idx2 = fcol_in_mdf["NF_being_deforested_Mkm2_py"]
    idx3 = fcol_in_mdf["NF_regrowing_after_being_deforested_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # NF_area_harvested_Mkm2 = INTEG ( NF_being_harvested_normally_Mkm2_py - NF_regrowing_after_harvesting_Mkm2_py , NF_area_harvested_in_1980 )
    idx1 = fcol_in_mdf["NF_area_harvested_Mkm2"]
    idx2 = fcol_in_mdf["NF_being_harvested_normally_Mkm2_py"]
    idx3 = fcol_in_mdf["NF_regrowing_after_harvesting_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # NF_Biomass_locked_in_construction_material_GtBiomass = INTEG ( NF_for_construction_use - NF_Biomass_in_construction_material_being_burnt - NF_TUNDRA_Biomass_in_construction_material_left_to_rot , NF_Biomass_locked_in_construction_material_in_1980 )
    idx1 = fcol_in_mdf["NF_Biomass_locked_in_construction_material_GtBiomass"]
    idx2 = fcol_in_mdf["NF_for_construction_use"]
    idx3 = fcol_in_mdf["NF_Biomass_in_construction_material_being_burnt"]
    idx4 = fcol_in_mdf["NF_TUNDRA_Biomass_in_construction_material_left_to_rot"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3] - mdf[rowi - 1, idx4]) * dt
    )

    # NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( NF_TUNDRA_Biomass_in_construction_material_left_to_rot + NF_Living_biomass_rotting - NF_Dead_biomass_decomposing - NF_DeadB_SOM_being_lost_due_to_deforestation - NF_DeadB_SOM_being_lost_due_to_energy_harvesting - NF_runoff - NF_soil_degradation_from_clear_cutting - NF_soil_degradation_from_forest_fires , NF_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
    idx1 = fcol_in_mdf["NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    idx2 = fcol_in_mdf["NF_TUNDRA_Biomass_in_construction_material_left_to_rot"]
    idx3 = fcol_in_mdf["NF_Living_biomass_rotting"]
    idx4 = fcol_in_mdf["NF_Dead_biomass_decomposing"]
    idx5 = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_deforestation"]
    idx6 = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx7 = fcol_in_mdf["NF_runoff"]
    idx8 = fcol_in_mdf["NF_soil_degradation_from_clear_cutting"]
    idx9 = fcol_in_mdf["NF_soil_degradation_from_forest_fires"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
        - mdf[rowi - 1, idx8]
        - mdf[rowi - 1, idx9]
      )
      * dt
    )

    # NF_Living_biomass_GtBiomass = INTEG ( NF_biomass_new_growing - NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting - NF_for_construction_use - NF_Living_biomass_rotting , NF_Living_biomass_in_1980 )
    idx1 = fcol_in_mdf["NF_Living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["NF_biomass_new_growing"]
    idx3 = fcol_in_mdf["NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["NF_for_construction_use"]
    idx5 = fcol_in_mdf["NF_Living_biomass_rotting"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        - mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # NF_potential_area_Mkm2 = INTEG ( Shifting_GRASS_to_NF_Mkm2_py + Shifting_TROP_to_NF_Mkm2_py + Shifting_Tundra_to_NF_Mkm2_py - Shifting_NF_to_GRASS_Mkm2_py - Shifting_NF_to_TROP_Mkm2_py - Shifting_NF_to_Tundra_Mkm2_py , 17.0089 )
    idx1 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["Shifting_GRASS_to_NF_Mkm2_py"]
    idx3 = fcol_in_mdf["Shifting_TROP_to_NF_Mkm2_py"]
    idx4 = fcol_in_mdf["Shifting_Tundra_to_NF_Mkm2_py"]
    idx5 = fcol_in_mdf["Shifting_NF_to_GRASS_Mkm2_py"]
    idx6 = fcol_in_mdf["Shifting_NF_to_TROP_Mkm2_py"]
    idx7 = fcol_in_mdf["Shifting_NF_to_Tundra_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        + mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
      )
      * dt
    )

    # Non_energy_footprint_pp_future = INTEG ( - Change_in_future_footprint_pp , 0.99 )
    idx1 = fcol_in_mdf["Non_energy_footprint_pp_future"]
    idx2 = fcol_in_mdf["Change_in_future_footprint_pp"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Nuclear_net_depreciation_multiplier_on_gen_cap = INTEG ( - Nuclear_net_depreciation , 1 )
    idx1 = fcol_in_mdf["Nuclear_net_depreciation_multiplier_on_gen_cap"]
    idx2 = fcol_in_mdf["Nuclear_net_depreciation"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # People_considering_entering_the_pool[region] = INTEG ( Change_in_people_considering_entering_the_pool[region] , People_considering_entering_the_pool_in_1980 )
    idx1 = fcol_in_mdf["People_considering_entering_the_pool"]
    idx2 = fcol_in_mdf["Change_in_people_considering_entering_the_pool"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # People_considering_leaving_the_pool[region] = INTEG ( Change_in_people_considering_leaving_the_pool[region] , People_considering_leaving_the_pool_in_1980 )
    idx1 = fcol_in_mdf["People_considering_leaving_the_pool"]
    idx2 = fcol_in_mdf["Change_in_people_considering_leaving_the_pool"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Populated_land[region] = INTEG ( acgl_to_pl[region] + apl_to_pl[region] + c_to_pl[region] - pl_to_apl[region] , Populated_land_in_1980[region] )
    idx1 = fcol_in_mdf["Populated_land"]
    idx2 = fcol_in_mdf["acgl_to_pl"]
    idx3 = fcol_in_mdf["apl_to_pl"]
    idx4 = fcol_in_mdf["c_to_pl"]
    idx5 = fcol_in_mdf["pl_to_apl"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (
          mdf[rowi - 1, idx2 + j]
          + mdf[rowi - 1, idx3 + j]
          + mdf[rowi - 1, idx4 + j]
          - mdf[rowi - 1, idx5 + j]
        )
        * dt
      )

    # Public_capacity[region] = INTEG ( Increase_in_public_capacity[region] - Decrease_in_public_capacity[region] , Public_Capacity_in_1980[region] )
    idx1 = fcol_in_mdf["Public_capacity"]
    idx2 = fcol_in_mdf["Increase_in_public_capacity"]
    idx3 = fcol_in_mdf["Decrease_in_public_capacity"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Rate_of_tech_advance_RoTA_in_TFP[region] = INTEG ( Change_in_RoTA[region] , Rate_of_tech_advance_RoTA_in_TFP_in_1980[region] )
    idx1 = fcol_in_mdf["Rate_of_tech_advance_RoTA_in_TFP"]
    idx2 = fcol_in_mdf["Change_in_RoTA"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Regenerative_cropland_fraction[region] = INTEG ( Increase_in_regen_cropland[region] - Decrease_in_regen_cropland[region] , 0 )
    idx1 = fcol_in_mdf["Regenerative_cropland_fraction"]
    idx2 = fcol_in_mdf["Increase_in_regen_cropland"]
    idx3 = fcol_in_mdf["Decrease_in_regen_cropland"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )
      if j == 1:
        a1 = str(mdf[rowi, idx1 + j])
#        print('Regenerative_cropland_fraction zeit='+str(zeit)+' value af='+a1+' idx1='+str(idx1))

    # Size_of_agri_sector[region] = ( Size_of_agri_sector_a + Size_of_agri_sector_b * math.exp ( - 1 * ( GDPpp_USED[region] / Size_of_agri_sector_c ) ) ) / 100
    idxlhs = fcol_in_mdf["Size_of_agri_sector"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Size_of_agri_sector_a
        + Size_of_agri_sector_b
        * math.exp(-1 * (mdf[rowi, idx1 + j] / Size_of_agri_sector_c))
      ) / 100

    # Size_of_tertiary_sector[region] = ( Size_of_tertiary_sector_lim - Size_of_tertiary_sector_a * math.exp ( - 1 * ( ( GDPpp_USED[region] ) / Size_of_tertiary_sector_c ) ) ) / 100
    idxlhs = fcol_in_mdf["Size_of_tertiary_sector"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Size_of_tertiary_sector_lim
        - Size_of_tertiary_sector_a
        * math.exp(-1 * ((mdf[rowi, idx1 + j]) / Size_of_tertiary_sector_c))
      ) / 100

    # Size_of_industrial_sector[region] = 1 - Size_of_agri_sector[region] - Size_of_tertiary_sector[region]
    idxlhs = fcol_in_mdf["Size_of_industrial_sector"]
    idx1 = fcol_in_mdf["Size_of_agri_sector"]
    idx2 = fcol_in_mdf["Size_of_tertiary_sector"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Total_factor_productivity_TFP_before_env_damage[region] = INTEG ( Change_in_TFP[region] , TFP_in_1980 )
    idx1 = fcol_in_mdf["Total_factor_productivity_TFP_before_env_damage"]
    idx2 = fcol_in_mdf["Change_in_TFP"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # TROP_area_burnt = INTEG ( TROP_burning - TROP_regrowing_after_being_burnt_Mkm2_py , TROP_area_burned_in_1980 )
    idx1 = fcol_in_mdf["TROP_area_burnt"]
    idx2 = fcol_in_mdf["TROP_burning"]
    idx3 = fcol_in_mdf["TROP_regrowing_after_being_burnt_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TROP_area_clear_cut = INTEG ( TROP_being_harvested_by_clear_cutting - TROP_regrowing_after_being_clear_cut , TROP_area_clear_cut_in_1980 )
    idx1 = fcol_in_mdf["TROP_area_clear_cut"]
    idx2 = fcol_in_mdf["TROP_being_harvested_by_clear_cutting"]
    idx3 = fcol_in_mdf["TROP_regrowing_after_being_clear_cut"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TROP_area_deforested = INTEG ( TROP_being_deforested_Mkm2_py - TROP_regrowing_after_being_deforested , TROP_area_deforested_in_1980 )
    idx1 = fcol_in_mdf["TROP_area_deforested"]
    idx2 = fcol_in_mdf["TROP_being_deforested_Mkm2_py"]
    idx3 = fcol_in_mdf["TROP_regrowing_after_being_deforested"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TROP_area_harvested_Mkm2 = INTEG ( TROP_being_harvested_normally - TROP_NF_regrowing_after_harvesting_Mkm2_py , TROP_area_harvested_in_1980 )
    idx1 = fcol_in_mdf["TROP_area_harvested_Mkm2"]
    idx2 = fcol_in_mdf["TROP_being_harvested_normally"]
    idx3 = fcol_in_mdf["TROP_NF_regrowing_after_harvesting_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TROP_Biomass_locked_in_construction_material_GtBiomass = INTEG ( TROP_for_construction_use - TROP_Biomass_in_construction_material_being_burnt - TROP_Biomass_in_construction_material_left_to_rot , TROP_Biomass_locked_in_construction_material_in_1980 )
    idx1 = fcol_in_mdf["TROP_Biomass_locked_in_construction_material_GtBiomass"]
    idx2 = fcol_in_mdf["TROP_for_construction_use"]
    idx3 = fcol_in_mdf["TROP_Biomass_in_construction_material_being_burnt"]
    idx4 = fcol_in_mdf["TROP_Biomass_in_construction_material_left_to_rot"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3] - mdf[rowi - 1, idx4]) * dt
    )

    # TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( TROP_Biomass_in_construction_material_left_to_rot + TROP_Living_biomass_rotting - TROP_Dead_biomass_decomposing - TROP_DeadB_SOM_being_lost_due_to_deforestation - TROP_DeadB_SOM_being_lost_due_to_energy_harvesting - TROP_runoff - TROP_soil_degradation_from_clear_cutting - TROP_soil_degradation_from_forest_fires , TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
    idx1 = fcol_in_mdf["TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    idx2 = fcol_in_mdf["TROP_Biomass_in_construction_material_left_to_rot"]
    idx3 = fcol_in_mdf["TROP_Living_biomass_rotting"]
    idx4 = fcol_in_mdf["TROP_Dead_biomass_decomposing"]
    idx5 = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_deforestation"]
    idx6 = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx7 = fcol_in_mdf["TROP_runoff"]
    idx8 = fcol_in_mdf["TROP_soil_degradation_from_clear_cutting"]
    idx9 = fcol_in_mdf["TROP_soil_degradation_from_forest_fires"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
        - mdf[rowi - 1, idx8]
        - mdf[rowi - 1, idx9]
      )
      * dt
    )

    # TROP_Living_biomass_GtBiomass = INTEG ( TROP_biomass_new_growing - TROP_for_construction_use - TROP_Living_biomass_rotting - TROP_NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting , TROP_Living_biomass_in_1980 )
    idx1 = fcol_in_mdf["TROP_Living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["TROP_biomass_new_growing"]
    idx3 = fcol_in_mdf["TROP_for_construction_use"]
    idx4 = fcol_in_mdf["TROP_Living_biomass_rotting"]
    idx5 = fcol_in_mdf["TROP_NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        - mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # TROP_potential_area_Mkm2 = INTEG ( Shifting_GRASS_to_TROP_Mkm2_py + Shifting_NF_to_TROP_Mkm2_py - Shifting_TROP_to_GRASS_Mkm2_py - Shifting_TROP_to_NF_Mkm2_py , 25.0208 )
    idx1 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["Shifting_GRASS_to_TROP_Mkm2_py"]
    idx3 = fcol_in_mdf["Shifting_NF_to_TROP_Mkm2_py"]
    idx4 = fcol_in_mdf["Shifting_TROP_to_GRASS_Mkm2_py"]
    idx5 = fcol_in_mdf["Shifting_TROP_to_NF_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # TUNDRA_area_burnt_Mkm2 = INTEG ( TUNDRA_burning_Mkm2_py - TUNDRA_regrowing_after_being_burnt_Mkm2_py , TUNDRA_area_burned_in_1980 )
    idx1 = fcol_in_mdf["TUNDRA_area_burnt_Mkm2"]
    idx2 = fcol_in_mdf["TUNDRA_burning_Mkm2_py"]
    idx3 = fcol_in_mdf["TUNDRA_regrowing_after_being_burnt_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TUNDRA_area_harvested_Mkm2 = INTEG ( TUNDRA_being_harvested_Mkm2_py - TUNDRA_regrowing_after_harvesting_Mkm2_py , TUNDRA_area_harvested_in_1980 )
    idx1 = fcol_in_mdf["TUNDRA_area_harvested_Mkm2"]
    idx2 = fcol_in_mdf["TUNDRA_being_harvested_Mkm2_py"]
    idx3 = fcol_in_mdf["TUNDRA_regrowing_after_harvesting_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TUNDRA_Biomass_locked_in_construction_material_GtBiomass = INTEG ( TUNDRA_for_construction_use - TUNDRA_Biomass_in_construction_material_being_burnt - TUNDRA_Biomass_in_construction_material_left_to_rot , TUNDRA_Biomass_locked_in_construction_material_in_1980 )
    idx1 = fcol_in_mdf["TUNDRA_Biomass_locked_in_construction_material_GtBiomass"]
    idx2 = fcol_in_mdf["TUNDRA_for_construction_use"]
    idx3 = fcol_in_mdf["TUNDRA_Biomass_in_construction_material_being_burnt"]
    idx4 = fcol_in_mdf["TUNDRA_Biomass_in_construction_material_left_to_rot"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3] - mdf[rowi - 1, idx4]) * dt
    )

    # TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass = INTEG ( TUNDRA_Biomass_in_construction_material_left_to_rot + TUNDRA_Living_biomass_rotting - TUNDRA_Dead_biomass_decomposing - TUNDRA_DeadB_SOM_being_lost_due_to_deforestation - TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting - TUNDRA_runoff - TUNDRA_soil_degradation_from_forest_fires , TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_in_1980 )
    idx1 = fcol_in_mdf["TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    idx2 = fcol_in_mdf["TUNDRA_Biomass_in_construction_material_left_to_rot"]
    idx3 = fcol_in_mdf["TUNDRA_Living_biomass_rotting"]
    idx4 = fcol_in_mdf["TUNDRA_Dead_biomass_decomposing"]
    idx5 = fcol_in_mdf["TUNDRA_DeadB_SOM_being_lost_due_to_deforestation"]
    idx6 = fcol_in_mdf["TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx7 = fcol_in_mdf["TUNDRA_runoff"]
    idx8 = fcol_in_mdf["TUNDRA_soil_degradation_from_forest_fires"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
        - mdf[rowi - 1, idx6]
        - mdf[rowi - 1, idx7]
        - mdf[rowi - 1, idx8]
      )
      * dt
    )

    # TUNDRA_deforested_Mkm2 = INTEG ( TUNDRA_being_deforested_Mkm2_py - TUNDRA_regrowing_after_being_deforested_Mkm2_py , TUNDRA_area_deforested_in_1980 )
    idx1 = fcol_in_mdf["TUNDRA_deforested_Mkm2"]
    idx2 = fcol_in_mdf["TUNDRA_being_deforested_Mkm2_py"]
    idx3 = fcol_in_mdf["TUNDRA_regrowing_after_being_deforested_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # TUNDRA_Living_biomass = INTEG ( TUNDRA_biomass_new_growing - TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting - TUNDRA_for_construction_use - TUNDRA_Living_biomass_rotting , TUNDRA_Living_biomass_in_1980 )
    idx1 = fcol_in_mdf["TUNDRA_Living_biomass"]
    idx2 = fcol_in_mdf["TUNDRA_biomass_new_growing"]
    idx3 = fcol_in_mdf["TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["TUNDRA_for_construction_use"]
    idx5 = fcol_in_mdf["TUNDRA_Living_biomass_rotting"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        - mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # Tundra_potential_area_Mkm2 = INTEG ( Shifting_ice_on_land_to_tundra_Mkm2_py + Shifting_NF_to_Tundra_Mkm2_py - Shifting_tundra_to_ice_on_land_Mkm2_py - Shifting_Tundra_to_NF_Mkm2_py , 22.5089 )
    idx1 = fcol_in_mdf["Tundra_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["Shifting_ice_on_land_to_tundra_Mkm2_py"]
    idx3 = fcol_in_mdf["Shifting_NF_to_Tundra_Mkm2_py"]
    idx4 = fcol_in_mdf["Shifting_tundra_to_ice_on_land_Mkm2_py"]
    idx5 = fcol_in_mdf["Shifting_Tundra_to_NF_Mkm2_py"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (
        mdf[rowi - 1, idx2]
        + mdf[rowi - 1, idx3]
        - mdf[rowi - 1, idx4]
        - mdf[rowi - 1, idx5]
      )
      * dt
    )

    # UAC_reduction_effort = INTEG ( - Change_in_UACre , 1 )
    idx1 = fcol_in_mdf["UAC_reduction_effort"]
    idx2 = fcol_in_mdf["Change_in_UACre"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Volcanic_aerosols_in_stratosphere = INTEG ( Volcanic_aerosols_emissions - Volcanic_aerosols_removed_from_stratosphere , 0.118607 )
    idx1 = fcol_in_mdf["Volcanic_aerosols_in_stratosphere"]
    idx2 = fcol_in_mdf["Volcanic_aerosols_emissions"]
    idx3 = fcol_in_mdf["Volcanic_aerosols_removed_from_stratosphere"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Warm_surface_water_volume_Gm3 = INTEG ( Upwelling_to_surface - Flow_of_water_from_warm_to_cold_surface_Gcubicm_per_yr , Volume_warm_ocean_0_to_100m )
    idx1 = fcol_in_mdf["Warm_surface_water_volume_Gm3"]
    idx2 = fcol_in_mdf["Upwelling_to_surface"]
    idx3 = fcol_in_mdf["Flow_of_water_from_warm_to_cold_surface_Gcubicm_per_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1] + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx3]) * dt
    )

    # Wetlands_area = INTEG ( - Rate_of_destruction_of_wetlands , Wetlands_area_in_1980 )
    idx1 = fcol_in_mdf["Wetlands_area"]
    idx2 = fcol_in_mdf["Rate_of_destruction_of_wetlands"]
    mdf[rowi, idx1] = mdf[rowi - 1, idx1] + (-mdf[rowi - 1, idx2]) * dt

    # Worker_debt_defaults_outstanding[region] = INTEG ( Worker_debt_defaulting[region] - Worker_defaults_written_off[region] , 0 )
    idx1 = fcol_in_mdf["Worker_debt_defaults_outstanding"]
    idx2 = fcol_in_mdf["Worker_debt_defaulting"]
    idx3 = fcol_in_mdf["Worker_defaults_written_off"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Worker_resistance_or_resignation[region] = INTEG ( Change_in_worker_resistance[region] , Worker_resistance_initially )
    idx1 = fcol_in_mdf["Worker_resistance_or_resignation"]
    idx2 = fcol_in_mdf["Change_in_worker_resistance"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = mdf[rowi - 1, idx1 + j] + (mdf[rowi - 1, idx2 + j]) * dt

    # Worker_income_after_tax[region] = Worker_income[region] - Worker_income_and_policy_taxes[region] + Transfer_from_govt_to_workers[region]
    idxlhs = fcol_in_mdf["Worker_income_after_tax"]
    idx1 = fcol_in_mdf["Worker_income"]
    idx2 = fcol_in_mdf["Worker_income_and_policy_taxes"]
    idx3 = fcol_in_mdf["Transfer_from_govt_to_workers"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # Workers_debt[region] = INTEG ( Workers_taking_on_new_debt[region] - Workers_debt_payback[region] , Workers_debt_in_1980[region] )
    idx1 = fcol_in_mdf["Workers_debt"]
    idx2 = fcol_in_mdf["Workers_taking_on_new_debt"]
    idx3 = fcol_in_mdf["Workers_debt_payback"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx3 + j]) * dt
      )

    # Access_to_electricity[region] = Access_to_electricity_L / ( 1 + math.exp ( - Access_to_electricity_k * ( ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) - Access_to_electricity_x0 ) ) ) + Access_to_electricity_min
    idxlhs = fcol_in_mdf["Access_to_electricity"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Access_to_electricity_L
        / (
          1
          + math.exp(
            -Access_to_electricity_k
            * (
              (mdf[rowi, idx1 + j] / UNIT_conv_to_make_base_dmnless)
              - Access_to_electricity_x0
            )
          )
        )
        + Access_to_electricity_min
      )

    # red_meat_dmd_PA = red_meat_dmd_PA_a * ( GDPpp_USED[pa] * UNIT_conv_to_make_exp_dmnl ) ^ red_meat_dmd_PA_b
    idxlhs = fcol_in_mdf["red_meat_dmd_PA"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      red_meat_dmd_PA_a
      * (mdf[rowi, idx1 + 6] * UNIT_conv_to_make_exp_dmnl) ** red_meat_dmd_PA_b
    )

    # red_meat_dmd_SA = red_meat_dmd_SA_a * ( GDPpp_USED[sa] * UNIT_conv_to_make_exp_dmnl ) ^ red_meat_dmd_SA_b + red_meat_dmd_SA_c
    idxlhs = fcol_in_mdf["red_meat_dmd_SA"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      red_meat_dmd_SA_a
      * (mdf[rowi, idx1 + 4] * UNIT_conv_to_make_exp_dmnl) ** red_meat_dmd_SA_b
      + red_meat_dmd_SA_c
    )

    # red_meat_dmd_func_pp[region] = red_meat_dmd_func_pp_L[region] / ( 1 + math.exp ( - red_meat_dmd_func_pp_k[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl - red_meat_dmd_func_pp_x0[region] ) ) ) + red_meat_dmd_func_pp_min[region]
    idxlhs = fcol_in_mdf["red_meat_dmd_func_pp"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (red_meat_dmd_func_pp_L[j]
        / (
          1
          + math.exp(
            -red_meat_dmd_func_pp_k[j]
            * (
              mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl
              - red_meat_dmd_func_pp_x0[j]
            )
          )
        )
        + red_meat_dmd_func_pp_min[j]
      )

    # red_meat_dmd_pp[region] = IF_THEN_ELSE ( j==6 , red_meat_dmd_PA , IF_THEN_ELSE ( j==4 , red_meat_dmd_SA , red_meat_dmd_func_pp ) )
    idxlhs = fcol_in_mdf["red_meat_dmd_pp"]
    idx1 = fcol_in_mdf["red_meat_dmd_PA"]
    idx2 = fcol_in_mdf["red_meat_dmd_SA"]
    idx3 = fcol_in_mdf["red_meat_dmd_func_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 6,     mdf[rowi, idx1],     IF_THEN_ELSE(j == 4, mdf[rowi, idx2], mdf[rowi, idx3 + j]),   )

    # RMDR_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , RMDR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , RMDR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , RMDR_R1_via_Excel , RMDR_policy_Min ) ) )
    idxlhs = fcol_in_mdf["RMDR_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     RMDR_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       RMDR_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, RMDR_R1_via_Excel[j], RMDR_policy_Min
          ),     ),   )

    # RMDR_policy_with_RW[region] = RMDR_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
    idxlhs = fcol_in_mdf["RMDR_policy_with_RW"]
    idx1 = fcol_in_mdf["RMDR_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
      )

    # RMDR_pol_div_100[region] = MIN ( RMDR_policy_Max , MAX ( RMDR_policy_Min , RMDR_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["RMDR_pol_div_100"]
    idx1 = fcol_in_mdf["RMDR_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(RMDR_policy_Max, max(RMDR_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # RMDR_policy[region] = SMOOTH3 ( RMDR_pol_div_100[region] , RMDR_Time_to_implement_policy )
    idxin = fcol_in_mdf["RMDR_pol_div_100"]
    idx2 = fcol_in_mdf["RMDR_policy_2"]
    idx1 = fcol_in_mdf["RMDR_policy_1"]
    idxout = fcol_in_mdf["RMDR_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (RMDR_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (RMDR_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (RMDR_Time_to_implement_policy / 3)
        * dt
      )

    # RMDR_multiplier_used[region] = 1 - RMDR_policy[region]
    idxlhs = fcol_in_mdf["RMDR_multiplier_used"]
    idx1 = fcol_in_mdf["RMDR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - mdf[rowi, idx1 + j]

    # red_meat_demand_pp[region] = red_meat_dmd_pp[region] * UNIT_conv_to_kg_red_meat_ppy * RMDR_multiplier_used[region]
    idxlhs = fcol_in_mdf["red_meat_demand_pp"]
    idx1 = fcol_in_mdf["red_meat_dmd_pp"]
    idx2 = fcol_in_mdf["RMDR_multiplier_used"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * UNIT_conv_to_kg_red_meat_ppy * mdf[rowi, idx2 + j]
      )

    # red_meat_demand_pp_consumed[region] = red_meat_demand_pp[region] * ( 1 - Food_wasted_in_1980[region] )
    idxlhs = fcol_in_mdf["red_meat_demand_pp_consumed"]
    idx1 = fcol_in_mdf["red_meat_demand_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - Food_wasted_in_1980[j])

    # red_meat_demand_pp_wasted[region] = red_meat_demand_pp[region] * Fraction_of_food_wasted[region]
    idxlhs = fcol_in_mdf["red_meat_demand_pp_wasted"]
    idx1 = fcol_in_mdf["red_meat_demand_pp"]
    idx2 = fcol_in_mdf["Fraction_of_food_wasted"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # red_meat_demand[region] = ( red_meat_demand_pp_consumed[region] + red_meat_demand_pp_wasted[region] ) * Population[region] / UNIT_conv_kgrmeat_and_Mtrmea * UNIT_conv_btw_p_and_Mp
    idxlhs = fcol_in_mdf["red_meat_demand"]
    idx1 = fcol_in_mdf["red_meat_demand_pp_consumed"]
    idx2 = fcol_in_mdf["red_meat_demand_pp_wasted"]
    idx3 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j])
        * mdf[rowi, idx3 + j]
        / UNIT_conv_kgrmeat_and_Mtrmea
        * UNIT_conv_btw_p_and_Mp
      )

    # RIPLGF_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , RIPLGF_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , RIPLGF_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , RIPLGF_R1_via_Excel , RIPLGF_policy_Min ) ) )
    idxlhs = fcol_in_mdf["RIPLGF_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     RIPLGF_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       RIPLGF_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, RIPLGF_R1_via_Excel[j], RIPLGF_policy_Min
          ),     ),   )

    # RIPLGF_policy_with_RW[region] = RIPLGF_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
    idxlhs = fcol_in_mdf["RIPLGF_policy_with_RW"]
    idx1 = fcol_in_mdf["RIPLGF_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
      )

    # RIPLGF_pol_div_100[region] = MIN ( RIPLGF_policy_Max , MAX ( RIPLGF_policy_Min , RIPLGF_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["RIPLGF_pol_div_100"]
    idx1 = fcol_in_mdf["RIPLGF_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(RIPLGF_policy_Max, max(RIPLGF_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # RIPLGF_policy[region] = SMOOTH3 ( RIPLGF_pol_div_100[region] , RIPLGF_smoothing_time[region] )
    idxin = fcol_in_mdf["RIPLGF_pol_div_100"]
    idx2 = fcol_in_mdf["RIPLGF_policy_2"]
    idx1 = fcol_in_mdf["RIPLGF_policy_1"]
    idxout = fcol_in_mdf["RIPLGF_policy"]
    idx5 = fcol_in_mdf["RIPLGF_smoothing_time"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (mdf[rowi - 1, idx5 + j] / 3)
        * dt
      )

    # Desired_net_export_of_red_meat_after_import_restriction_policy[region] = Desired_net_export_of_red_meat[region] * ( 1 - RIPLGF_policy[region] )
    idxlhs = fcol_in_mdf["Desired_net_export_of_red_meat_after_import_restriction_policy"
    ]
    idx1 = fcol_in_mdf["RIPLGF_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Desired_net_export_of_red_meat[j] * (
        1 - mdf[rowi, idx1 + j]
      )

    # Red_meat_production[region] = ( red_meat_demand[region] / ( 1 - Desired_net_export_of_red_meat_after_import_restriction_policy[region] ) )
    idxlhs = fcol_in_mdf["Red_meat_production"]
    idx1 = fcol_in_mdf["red_meat_demand"]
    idx2 = fcol_in_mdf["Desired_net_export_of_red_meat_after_import_restriction_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (1 - mdf[rowi, idx2 + j])

    # white_meat_dmd_CN = white_meat_dmd_CN_a * LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) + white_meat_dmd_CN_b
    idxlhs = fcol_in_mdf["white_meat_dmd_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      white_meat_dmd_CN_a * math.log(mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl)
      + white_meat_dmd_CN_b
    )

    # white_meat_dmd_func_pp[region] = white_meat_dmd_func_pp_L[region] / ( 1 + math.exp ( - white_meat_dmd_func_pp_k[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl - white_meat_dmd_func_pp_x0[region] ) ) )
    idxlhs = fcol_in_mdf["white_meat_dmd_func_pp"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = white_meat_dmd_func_pp_L[j] / (
        1
        + math.exp(
          -white_meat_dmd_func_pp_k[j]
          * (
            mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl
            - white_meat_dmd_func_pp_x0[j]
          )
        )
      )

    # white_meat_dmd_pp[region] = IF_THEN_ELSE ( j==2 , white_meat_dmd_CN , white_meat_dmd_func_pp )
    idxlhs = fcol_in_mdf["white_meat_dmd_pp"]
    idx1 = fcol_in_mdf["white_meat_dmd_CN"]
    idx2 = fcol_in_mdf["white_meat_dmd_func_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 2, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # white_meat_demand_pp[region] = white_meat_dmd_pp[region] * UNIT_conv_to_kg_white_meat_ppy
    idxlhs = fcol_in_mdf["white_meat_demand_pp"]
    idx1 = fcol_in_mdf["white_meat_dmd_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_kg_white_meat_ppy

    # white_meat_demand_pp_consumed[region] = white_meat_demand_pp[region] * ( 1 - Food_wasted_in_1980[region] )
    idxlhs = fcol_in_mdf["white_meat_demand_pp_consumed"]
    idx1 = fcol_in_mdf["white_meat_demand_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - Food_wasted_in_1980[j])

    # white_meat_demand_pp_wasted[region] = white_meat_demand_pp[region] * Fraction_of_food_wasted[region]
    idxlhs = fcol_in_mdf["white_meat_demand_pp_wasted"]
    idx1 = fcol_in_mdf["white_meat_demand_pp"]
    idx2 = fcol_in_mdf["Fraction_of_food_wasted"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # white_meat_demand[region] = ( white_meat_demand_pp_consumed[region] + white_meat_demand_pp_wasted[region] ) * Population[region] / UNIT_conv_kgwmeat_and_Mtwmeat * UNIT_conv_btw_p_and_Mp
    idxlhs = fcol_in_mdf["white_meat_demand"]
    idx1 = fcol_in_mdf["white_meat_demand_pp_consumed"]
    idx2 = fcol_in_mdf["white_meat_demand_pp_wasted"]
    idx3 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j])
        * mdf[rowi, idx3 + j]
        / UNIT_conv_kgwmeat_and_Mtwmeat
        * UNIT_conv_btw_p_and_Mp
      )

    # Desired_net_export_of_white_meat[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0.1 ) , ( 2020 , 0.2 ) , ( 2050 , 0.2 ) , ( 2100 , 0.1 ) ) ) Desired_net_export_of_white_meat[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) ) Desired_net_export_of_white_meat[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) ) Desired_net_export_of_white_meat[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.2 ) , ( 1990 , - 0.2 ) , ( 2000 , - 0.2 ) , ( 2010 , - 0.2 ) , ( 2020 , - 0.2 ) , ( 2050 , - 0.2 ) , ( 2100 , - 0.2 ) ) ) Desired_net_export_of_white_meat[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) ) Desired_net_export_of_white_meat[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Desired_net_export_of_white_meat[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Desired_net_export_of_white_meat[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Desired_net_export_of_white_meat[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0.1 ) , ( 2020 , 0.2 ) , ( 2050 , 0.2 ) , ( 2100 , 0.1 ) ) ) Desired_net_export_of_white_meat[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.04 ) , ( 1990 , - 0.04 ) , ( 2000 , - 0.04 ) , ( 2010 , - 0.04 ) , ( 2020 , - 0.04 ) , ( 2050 , - 0.04 ) , ( 2100 , - 0.04 ) ) )
    tabidx = ftab_in_d_table[  "Desired_net_export_of_white_meat"]  # fetch the correct table
    idx2 = fcol_in_mdf["Desired_net_export_of_white_meat"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # Desired_net_export_of_white_meat_after_import_restriction_policy[region] = Desired_net_export_of_white_meat[region] * ( 1 - RIPLGF_policy[region] )
    idxlhs = fcol_in_mdf["Desired_net_export_of_white_meat_after_import_restriction_policy"
    ]
    idx1 = fcol_in_mdf["Desired_net_export_of_white_meat"]
    idx2 = fcol_in_mdf["RIPLGF_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # White_meat_production[region] = white_meat_demand[region] / ( 1 - Desired_net_export_of_white_meat_after_import_restriction_policy[region] )
    idxlhs = fcol_in_mdf["White_meat_production"]
    idx1 = fcol_in_mdf["white_meat_demand"]
    idx2 = fcol_in_mdf["Desired_net_export_of_white_meat_after_import_restriction_policy"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (1 - mdf[rowi, idx2 + j])

    # Meat_production[region] = Red_meat_production[region] * UNIT_conv_red_meat + White_meat_production[region] * UNIT_conv_white_meat
    idxlhs = fcol_in_mdf["Meat_production"]
    idx1 = fcol_in_mdf["Red_meat_production"]
    idx2 = fcol_in_mdf["White_meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * UNIT_conv_red_meat
        + mdf[rowi, idx2 + j] * UNIT_conv_white_meat
      )

    # Feed_dmd[region] = Feed_dmd_a[region] * LN ( Meat_production[region] * UNIT_conv_meat_to_feed ) + Feed_dmd_b[region]
    idxlhs = fcol_in_mdf["Feed_dmd"]
    idx1 = fcol_in_mdf["Meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Feed_dmd_a[j] * math.log(mdf[rowi, idx1 + j] * UNIT_conv_meat_to_feed)
        + Feed_dmd_b[j]
      )

    # All_crop_regional_dmd_last_year[region] = SMOOTHI ( All_crop_regional_dmd[region] , One_year , All_crop_dmd_food_in_1980[region] )
    idx1 = fcol_in_mdf["All_crop_regional_dmd_last_year"]
    idx2 = fcol_in_mdf["All_crop_regional_dmd"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / One_year * dt
      )

    # Desired_crop_import[region] = SMOOTHI ( Desired_crop_import_indicated[region] , One_year , Reference_crop_import_in_1980[region] )
    idx1 = fcol_in_mdf["Desired_crop_import"]
    idx2 = fcol_in_mdf["Desired_crop_import_indicated"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / One_year * dt
      )

    # Eff_of_wealth_on_crop_import[region] = WITH LOOKUP ( GDPpp_USED[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 10 , 0.2 ) , ( 20 , 0.3 ) , ( 30 , 0.4 ) , ( 50 , 0.6 ) , ( 60 , 0.7 ) , ( 100 , 1 ) ) )
    tabidx = ftab_in_d_table["Eff_of_wealth_on_crop_import"]  # fetch the correct table
    idx2 = fcol_in_mdf["Eff_of_wealth_on_crop_import"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["GDPpp_USED"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Actual_crop_import[region] = Desired_crop_import[region] * Eff_of_wealth_on_crop_import[region]
    idxlhs = fcol_in_mdf["Actual_crop_import"]
    idx1 = fcol_in_mdf["Desired_crop_import"]
    idx2 = fcol_in_mdf["Eff_of_wealth_on_crop_import"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Net_export_of_crops[region] = All_crop_regional_dmd_last_year[region] * Desired_net_export_of_crops[region] - Actual_crop_import[region]
    idxlhs = fcol_in_mdf["Net_export_of_crops"]
    idx1 = fcol_in_mdf["All_crop_regional_dmd_last_year"]
    idx2 = fcol_in_mdf["Actual_crop_import"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * Desired_net_export_of_crops[j] - mdf[rowi, idx2 + j]
      )

    # All_crop_regional_dmd[region] = All_crop_dmd_food[region] + Feed_dmd[region] + Net_export_of_crops[region]
    idxlhs = fcol_in_mdf["All_crop_regional_dmd"]
    idx1 = fcol_in_mdf["All_crop_dmd_food"]
    idx2 = fcol_in_mdf["Feed_dmd"]
    idx3 = fcol_in_mdf["Net_export_of_crops"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # Smoothed_Crop_yield_from_N_use[region] = SMOOTHI ( Crop_yield_from_N_use[region] , One_year , crop_yield_in_1980[region] )
    idx1 = fcol_in_mdf["Smoothed_Crop_yield_from_N_use"]
    idx2 = fcol_in_mdf["Crop_yield_from_N_use"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / One_year * dt
      )

    # Smoothed_Cumulative_N_use_for_soil_quality[region] = SMOOTH ( Cumulative_N_use_since_2020[region] , Time_for_N_use_to_affect_soil_quality )
    idx1 = fcol_in_mdf["Smoothed_Cumulative_N_use_for_soil_quality"]
    idx2 = fcol_in_mdf["Cumulative_N_use_since_2020"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_N_use_to_affect_soil_quality
        * dt
      )

    # Eff_of_cumulative_N_use_on_soil_quality[region] = WITH LOOKUP ( Smoothed_Cumulative_N_use_for_soil_quality[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 10 , 1.05 ) , ( 20 , 1.5 ) ) )
    tabidx = ftab_in_d_table[  "Eff_of_cumulative_N_use_on_soil_quality"]  # fetch the correct table
    idx2 = fcol_in_mdf["Eff_of_cumulative_N_use_on_soil_quality"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Smoothed_Cumulative_N_use_for_soil_quality"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Soil_quality[region] = ( Soil_quality_in_1980[region] / Eff_of_cumulative_N_use_on_soil_quality[region] ) * ( ( 1 - Regenerative_cropland_fraction[region] ) + Soil_quality_of_regenerative_cropland[region] * Regenerative_cropland_fraction[region] )
    idxlhs = fcol_in_mdf["Soil_quality"]
    idx1 = fcol_in_mdf["Eff_of_cumulative_N_use_on_soil_quality"]
    idx2 = fcol_in_mdf["Regenerative_cropland_fraction"]
    idx3 = fcol_in_mdf["Regenerative_cropland_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Soil_quality_in_1980 / mdf[rowi, idx1 + j]) * (
        (1 - mdf[rowi, idx2 + j])
        + Soil_quality_of_regenerative_cropland * mdf[rowi, idx3 + j]
      )

    # CO2_concentration_ratio_wrt_2020 = IF_THEN_ELSE ( zeit < 2020 , 1 , CO2_concentration_used_after_any_experiments_ppm / CO2_concentration_2020 )
    idxlhs = fcol_in_mdf["CO2_concentration_ratio_wrt_2020"]
    idx1 = fcol_in_mdf["CO2_concentration_used_after_any_experiments_ppm"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit < 2020, 1, mdf[rowi, idx1] / CO2_concentration_2020
    )

    # Eff_of_CO2_on_yield = 1 + SoE_of_CO2_on_yield * ( CO2_concentration_ratio_wrt_2020 - 1 )
    idxlhs = fcol_in_mdf["Eff_of_CO2_on_yield"]
    idx1 = fcol_in_mdf["CO2_concentration_ratio_wrt_2020"]
    mdf[rowi, idxlhs] = 1 + SoE_of_CO2_on_yield * (mdf[rowi, idx1] - 1)

    # Surface_ocean_warm_volume = Warm_surface_water_volume_Gm3 + Intermediate_upwelling_water_volume_100m_to_1km_Gm3
    idxlhs = fcol_in_mdf["Surface_ocean_warm_volume"]
    idx1 = fcol_in_mdf["Warm_surface_water_volume_Gm3"]
    idx2 = fcol_in_mdf["Intermediate_upwelling_water_volume_100m_to_1km_Gm3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # Thermal_expansion_surface_pct = WITH LOOKUP ( Temp_surface , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
    tabidx = ftab_in_d_table["Thermal_expansion_surface_pct"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Thermal_expansion_surface_pct"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Temp_surface"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Thermal_expansion_surface_in_1850_pct = WITH LOOKUP ( Temp_surface_1850_less_zero_k , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
    tabidx = ftab_in_d_table[  "Thermal_expansion_surface_in_1850_pct"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Thermal_expansion_surface_in_1850_pct"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(Temp_surface_1850_less_zero_k, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3 = Surface_ocean_warm_volume * ( Thermal_expansion_surface_pct - Thermal_expansion_surface_in_1850_pct ) / 100 * ( 1 - Pressure_adjustment_surface_pct / 100 ) * UNIT_conversion_Gm3_to_km3
    idxlhs = fcol_in_mdf["Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3"]
    idx1 = fcol_in_mdf["Surface_ocean_warm_volume"]
    idx2 = fcol_in_mdf["Thermal_expansion_surface_pct"]
    idx3 = fcol_in_mdf["Thermal_expansion_surface_in_1850_pct"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * (mdf[rowi, idx2] - mdf[rowi, idx3])
      / 100
      * (1 - Pressure_adjustment_surface_pct / 100)
      * UNIT_conversion_Gm3_to_km3
    )

    # Sea_level_change_from_thermal_expansion_surface_m = Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3 / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2
    idxlhs = fcol_in_mdf["Sea_level_change_from_thermal_expansion_surface_m"]
    idx1 = fcol_in_mdf["Volume_expansion_from_thermal_expansion_surface_Gm3_is_km3"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2
    )

    # Deep_ocean_cold_volume = Cold_surface_water_volume_Gm3 + Cold_water_volume_downwelling_Gm3 + Deep_water_volume_1km_to_4km_Gm3
    idxlhs = fcol_in_mdf["Deep_ocean_cold_volume"]
    idx1 = fcol_in_mdf["Cold_surface_water_volume_Gm3"]
    idx2 = fcol_in_mdf["Cold_water_volume_downwelling_Gm3"]
    idx3 = fcol_in_mdf["Deep_water_volume_1km_to_4km_Gm3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Temp_ocean_deep_in_K = Heat_in_deep_ZJ * Conversion_constant_heat_ocean_deep_to_temp
    idxlhs = fcol_in_mdf["Temp_ocean_deep_in_K"]
    idx1 = fcol_in_mdf["Heat_in_deep_ZJ"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Conversion_constant_heat_ocean_deep_to_temp

    # Temp_ocean_deep_in_C = Temp_ocean_deep_in_K - 273.15
    idxlhs = fcol_in_mdf["Temp_ocean_deep_in_C"]
    idx1 = fcol_in_mdf["Temp_ocean_deep_in_K"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - 273.15

    # Thermal_expansion_deep_pct = WITH LOOKUP ( Temp_ocean_deep_in_C , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
    tabidx = ftab_in_d_table["Thermal_expansion_deep_pct"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Thermal_expansion_deep_pct"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Temp_ocean_deep_in_C"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Thermal_expansion_deep_in_1850_pct = WITH LOOKUP ( Temp_ocean_deep_in_1850_C , ( [ ( 0 , 0 ) - ( 20 , 0.2 ) ] , ( 0 , 0.015 ) , ( 1 , 0.008 ) , ( 2 , 0.0033 ) , ( 3 , 0.001 ) , ( 4 , 0 ) , ( 5 , 0.0012 ) , ( 6 , 0.0033 ) , ( 7 , 0.008 ) , ( 8 , 0.013 ) , ( 9 , 0.021 ) , ( 10 , 0.0287 ) , ( 20 , 0.1963 ) ) )
    tabidx = ftab_in_d_table[  "Thermal_expansion_deep_in_1850_pct"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Thermal_expansion_deep_in_1850_pct"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(Temp_ocean_deep_in_1850_C, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3 = Deep_ocean_cold_volume * ( Thermal_expansion_deep_pct - Thermal_expansion_deep_in_1850_pct ) / 100 * ( 1 - Pressure_adjustment_deep_pct / 100 ) * UNIT_conversion_Gm3_to_km3
    idxlhs = fcol_in_mdf["Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3"]
    idx1 = fcol_in_mdf["Deep_ocean_cold_volume"]
    idx2 = fcol_in_mdf["Thermal_expansion_deep_pct"]
    idx3 = fcol_in_mdf["Thermal_expansion_deep_in_1850_pct"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * (mdf[rowi, idx2] - mdf[rowi, idx3])
      / 100
      * (1 - Pressure_adjustment_deep_pct / 100)
      * UNIT_conversion_Gm3_to_km3
    )

    # Sea_level_change_from_thermal_expansion_deep_m = Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3 / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2
    idxlhs = fcol_in_mdf["Sea_level_change_from_thermal_expansion_deep_m"]
    idx1 = fcol_in_mdf["Volume_expansion_from_thermal_expansion_deep_Gm3_is_km3"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2
    )

    # Total_sea_level_change_from_thermal_expansion_m = ( Sea_level_change_from_thermal_expansion_surface_m + Sea_level_change_from_thermal_expansion_deep_m ) * UNIT_conversion_from_km_to_m
    idxlhs = fcol_in_mdf["Total_sea_level_change_from_thermal_expansion_m"]
    idx1 = fcol_in_mdf["Sea_level_change_from_thermal_expansion_surface_m"]
    idx2 = fcol_in_mdf["Sea_level_change_from_thermal_expansion_deep_m"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2]
    ) * UNIT_conversion_from_km_to_m

    # Sea_level_rise_from_melting_ice_m = Cumulative_ocean_volume_increase_due_to_ice_melting_km3 / Ocean_surface_area_km2 * UNIT_Conversion_from_km3_to_km2 * UNIT_conversion_from_km_to_m * Avg_flatness_of_worlds_coastline
    idxlhs = fcol_in_mdf["Sea_level_rise_from_melting_ice_m"]
    idx1 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / Ocean_surface_area_km2
      * UNIT_Conversion_from_km3_to_km2
      * UNIT_conversion_from_km_to_m
      * Avg_flatness_of_worlds_coastline
    )

    # Sea_level_change_from_melting_ice_and_thermal_expansion_m = Total_sea_level_change_from_thermal_expansion_m + Sea_level_rise_from_melting_ice_m
    idxlhs = fcol_in_mdf["Sea_level_change_from_melting_ice_and_thermal_expansion_m"]
    idx1 = fcol_in_mdf["Total_sea_level_change_from_thermal_expansion_m"]
    idx2 = fcol_in_mdf["Sea_level_rise_from_melting_ice_m"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # sea_level_rise_ratio_wrt_2020 = IF_THEN_ELSE ( zeit < 2020 , 1 , Sea_level_change_from_melting_ice_and_thermal_expansion_m / sea_level_rise_2020 )
    idxlhs = fcol_in_mdf["sea_level_rise_ratio_wrt_2020"]
    idx1 = fcol_in_mdf["Sea_level_change_from_melting_ice_and_thermal_expansion_m"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit < 2020, 1, mdf[rowi, idx1] / sea_level_rise_2020
    )

    # temp_ratio_wrt_2020 = IF_THEN_ELSE ( zeit < 2020 , 1 , Temp_surface_anomaly_compared_to_1850_degC / temp_in_2020 )
    idxlhs = fcol_in_mdf["temp_ratio_wrt_2020"]
    idx1 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit < 2020, 1, mdf[rowi, idx1] / temp_in_2020)

    # Combined_env_damage_indicator = ( sea_level_rise_ratio_wrt_2020 + temp_ratio_wrt_2020 ) / 2 - 1
    idxlhs = fcol_in_mdf["Combined_env_damage_indicator"]
    idx1 = fcol_in_mdf["sea_level_rise_ratio_wrt_2020"]
    idx2 = fcol_in_mdf["temp_ratio_wrt_2020"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2]) / 2 - 1

    # GDPpp_of_the_richest_region = VMAX ( GDPpp_USED[region!] )
    idxlhs = fcol_in_mdf["GDPpp_of_the_richest_region"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    vmax = mdf[rowi, idx1 + 0]
    for j in range(1, 10):
      if mdf[rowi, idx1 + j] > vmax:
        vmax = mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = vmax

    # Ratio_of_regional_GDPpp_to_richest_region_GDPpp[region] = GDPpp_USED[region] / GDPpp_of_the_richest_region
    idxlhs = fcol_in_mdf["Ratio_of_regional_GDPpp_to_richest_region_GDPpp"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    idx2 = fcol_in_mdf["GDPpp_of_the_richest_region"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2]

    # Indicated_eff_of_relative_wealth_on_env_damage[region] = IF_THEN_ELSE ( zeit > 2020 , 1 + SoE_of_relative_wealth_on_env_damage * ( Ratio_of_regional_GDPpp_to_richest_region_GDPpp - 1 ) , 1 )
    idxlhs = fcol_in_mdf["Indicated_eff_of_relative_wealth_on_env_damage"]
    idx1 = fcol_in_mdf["Ratio_of_regional_GDPpp_to_richest_region_GDPpp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit > 2020,     1 + SoE_of_relative_wealth_on_env_damage * (mdf[rowi, idx1 + j] - 1),     1,   )

    # Actual_eff_of_relative_wealth_on_env_damage[region] = SMOOTH3 ( Indicated_eff_of_relative_wealth_on_env_damage[region] , Time_for_shifts_in_relative_wealth_to_affect_env_damage_response )
    idxin = fcol_in_mdf["Indicated_eff_of_relative_wealth_on_env_damage"]
    idx2 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage_2"]
    idx1 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage_1"]
    idxout = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_for_shifts_in_relative_wealth_to_affect_env_damage_response / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_for_shifts_in_relative_wealth_to_affect_env_damage_response / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_for_shifts_in_relative_wealth_to_affect_env_damage_response / 3)
        * dt
      )

    # Eff_of_env_damage_on_agri_yield[region] = math.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_agri_yield ) / Actual_eff_of_relative_wealth_on_env_damage[region]
    idxlhs = fcol_in_mdf["Eff_of_env_damage_on_agri_yield"]
    idx1 = fcol_in_mdf["Combined_env_damage_indicator"]
    idx2 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (math.exp(mdf[rowi, idx1] * expSoE_of_ed_on_agri_yield) / mdf[rowi, idx2 + j]
      )

    # Crop_yield_with_soil_quality_CO2_and_env_dam_effects[region] = Smoothed_Crop_yield_from_N_use[region] * Soil_quality[region] * Eff_of_CO2_on_yield / Eff_of_env_damage_on_agri_yield[region]
    idxlhs = fcol_in_mdf["Crop_yield_with_soil_quality_CO2_and_env_dam_effects"]
    idx1 = fcol_in_mdf["Smoothed_Crop_yield_from_N_use"]
    idx2 = fcol_in_mdf["Soil_quality"]
    idx3 = fcol_in_mdf["Eff_of_CO2_on_yield"]
    idx4 = fcol_in_mdf["Eff_of_env_damage_on_agri_yield"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3]
        / mdf[rowi, idx4 + j]
      )

    # Crop_grown_regionally[region] = Cropland[region] * Crop_yield_with_soil_quality_CO2_and_env_dam_effects[region]
    idxlhs = fcol_in_mdf["Crop_grown_regionally"]
    idx1 = fcol_in_mdf["Cropland"]
    idx2 = fcol_in_mdf["Crop_yield_with_soil_quality_CO2_and_env_dam_effects"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Ratio_of_demand_to_regional_supply_of_crops[region] = All_crop_regional_dmd[region] / Crop_grown_regionally[region]
    idxlhs = fcol_in_mdf["Ratio_of_demand_to_regional_supply_of_crops"]
    idx1 = fcol_in_mdf["All_crop_regional_dmd"]
    idx2 = fcol_in_mdf["Crop_grown_regionally"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Desired_cropland[region] = Cropland[region] * ( 1 + Ratio_of_demand_to_regional_supply_of_crops[region] * Fraction_of_supply_imbalance_to_be_closed_by_land[region] )
    idxlhs = fcol_in_mdf["Desired_cropland"]
    idx1 = fcol_in_mdf["Cropland"]
    idx2 = fcol_in_mdf["Ratio_of_demand_to_regional_supply_of_crops"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (
        1 + mdf[rowi, idx2 + j] * Fraction_of_supply_imbalance_to_be_closed_by_land[j]
      )

    # Cropland_gap[region] = Desired_cropland[region] - Cropland[region]
    idxlhs = fcol_in_mdf["Cropland_gap"]
    idx1 = fcol_in_mdf["Desired_cropland"]
    idx2 = fcol_in_mdf["Cropland"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # acgl_to_c[region] = MIN ( Abandoned_crop_and_grazing_land[region] , MAX ( 0 , Cropland_gap[region] ) ) * Fraction_of_cropland_gap_closed_from_acgl[region]
    idxlhs = fcol_in_mdf["acgl_to_c"]
    idx1 = fcol_in_mdf["Abandoned_crop_and_grazing_land"]
    idx2 = fcol_in_mdf["Cropland_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(mdf[rowi, idx1 + j], max(0, mdf[rowi, idx2 + j]))
        * Fraction_of_cropland_gap_closed_from_acgl[j]
      )

    # acgl_to_fa[region] = Abandoned_crop_and_grazing_land[region] / Time_for_abandoned_agri_land_to_become_forest
    idxlhs = fcol_in_mdf["acgl_to_fa"]
    idx1 = fcol_in_mdf["Abandoned_crop_and_grazing_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_for_abandoned_agri_land_to_become_forest
      )

    # Grazing_land_EC = Grazing_land_EC_a * ( Meat_production[ec] * UNIT_conv_meat_to_dmnl ) ^ Grazing_land_EC_b
    idxlhs = fcol_in_mdf["Grazing_land_EC"]
    idx1 = fcol_in_mdf["Meat_production"]
    mdf[rowi, idxlhs] = (
      Grazing_land_EC_a
      * (mdf[rowi, idx1 + 7] * UNIT_conv_meat_to_dmnl) ** Grazing_land_EC_b
    )

    # Grazing_land_LA = ( Grazing_land_LA_L / ( 1 + math.exp ( - Grazing_land_LA_k * ( Meat_production[la] * UNIT_conv_meat_to_dmnl - Grazing_land_LA_x ) ) ) ) - ( Grazing_land_LA_L2 / ( 1 + math.exp ( - Grazing_land_LA_k2 * ( Meat_production[la] * UNIT_conv_meat_to_dmnl - Grazing_land_LA_x2 ) ) ) )
    idxlhs = fcol_in_mdf["Grazing_land_LA"]
    idx1 = fcol_in_mdf["Meat_production"]
    idx2 = fcol_in_mdf["Meat_production"]
    mdf[rowi, idxlhs] = (
      Grazing_land_LA_L
      / (
        1
        + math.exp(
          -Grazing_land_LA_k
          * (mdf[rowi, idx1 + 5] * UNIT_conv_meat_to_dmnl - Grazing_land_LA_x)
        )
      )
    ) - (
      Grazing_land_LA_L2
      / (
        1
        + math.exp(
          -Grazing_land_LA_k2
          * (mdf[rowi, idx2 + 5] * UNIT_conv_meat_to_dmnl - Grazing_land_LA_x2)
        )
      )
    )

    # Grazing_land_ME = Grazing_land_ME_L / ( 1 + math.exp ( - Grazing_land_ME_k * ( Meat_production[me] * UNIT_conv_meat_to_dmnl - Grazing_land_ME_x ) ) ) + Grazing_land_ME_min
    idxlhs = fcol_in_mdf["Grazing_land_ME"]
    idx1 = fcol_in_mdf["Meat_production"]
    mdf[rowi, idxlhs] = (
      Grazing_land_ME_L
      / (
        1
        + math.exp(
          -Grazing_land_ME_k
          * (mdf[rowi, idx1 + 3] * UNIT_conv_meat_to_dmnl - Grazing_land_ME_x)
        )
      )
      + Grazing_land_ME_min
    )

    # Grazing_land_PA = Grazing_land_PA_L / ( 1 + math.exp ( - Grazing_land_PA_k * ( Meat_production[pa] * UNIT_conv_meat_to_dmnl - Grazing_land_PA_x ) ) ) + Grazing_land_PA_min
    idxlhs = fcol_in_mdf["Grazing_land_PA"]
    idx1 = fcol_in_mdf["Meat_production"]
    mdf[rowi, idxlhs] = (
      Grazing_land_PA_L
      / (
        1
        + math.exp(
          -Grazing_land_PA_k
          * (mdf[rowi, idx1 + 6] * UNIT_conv_meat_to_dmnl - Grazing_land_PA_x)
        )
      )
      + Grazing_land_PA_min
    )

    # Grazing_land_SA = Grazing_land_SA_a * ( Meat_production[sa] * UNIT_conv_meat_to_dmnl ) ^ Grazing_land_SA_b
    idxlhs = fcol_in_mdf["Grazing_land_SA"]
    idx1 = fcol_in_mdf["Meat_production"]
    mdf[rowi, idxlhs] = (
      Grazing_land_SA_a
      * (mdf[rowi, idx1 + 4] * UNIT_conv_meat_to_dmnl) ** Grazing_land_SA_b
    )

    # Grazing_land_SE = Grazing_land_SE_a * LN ( Meat_production[se] * UNIT_conv_meat_to_dmnl ) + Grazing_land_SE_b
    idxlhs = fcol_in_mdf["Grazing_land_SE"]
    idx1 = fcol_in_mdf["Meat_production"]
    mdf[rowi, idxlhs] = (
      Grazing_land_SE_a * math.log(mdf[rowi, idx1 + 9] * UNIT_conv_meat_to_dmnl)
      + Grazing_land_SE_b
    )

    # Grazing_land_Rest[region] = Grazing_land_Rest_L[region] / ( 1 + math.exp ( - Grazing_land_Rest_k[region] * ( Meat_production[region] * UNIT_conv_meat_to_dmnl - Grazing_land_Rest_x[region] ) ) )
    idxlhs = fcol_in_mdf["Grazing_land_Rest"]
    idx1 = fcol_in_mdf["Meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Grazing_land_Rest_L[j] / (
        1
        + math.exp(
          -Grazing_land_Rest_k[j]
          * (mdf[rowi, idx1 + j] * UNIT_conv_meat_to_dmnl - Grazing_land_Rest_x[j])
        )
      )

    # Desired_grazing_land[region] = IF_THEN_ELSE ( j==7 , Grazing_land_EC , IF_THEN_ELSE ( j==5 , Grazing_land_LA , IF_THEN_ELSE ( j==3 , Grazing_land_ME , IF_THEN_ELSE ( j==6 , Grazing_land_PA , IF_THEN_ELSE ( j==4 , Grazing_land_SA , IF_THEN_ELSE ( j==9 , Grazing_land_SE , Grazing_land_Rest ) ) ) ) ) )
    idxlhs = fcol_in_mdf["Desired_grazing_land"]
    idx1 = fcol_in_mdf["Grazing_land_EC"]
    idx2 = fcol_in_mdf["Grazing_land_LA"]
    idx3 = fcol_in_mdf["Grazing_land_ME"]
    idx4 = fcol_in_mdf["Grazing_land_PA"]
    idx5 = fcol_in_mdf["Grazing_land_SA"]
    idx6 = fcol_in_mdf["Grazing_land_SE"]
    idx7 = fcol_in_mdf["Grazing_land_Rest"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 7,     mdf[rowi, idx1],     IF_THEN_ELSE(
          j == 5,       mdf[rowi, idx2],       IF_THEN_ELSE(
            j == 3,         mdf[rowi, idx3],         IF_THEN_ELSE(
              j == 6,           mdf[rowi, idx4],           IF_THEN_ELSE(
                j == 4,             mdf[rowi, idx5],             IF_THEN_ELSE(j == 9, mdf[rowi, idx6], mdf[rowi, idx7 + j]),           ),         ),       ),     ),   )

    # Graing_land_desired_for_all_meat[region] = Desired_grazing_land[region] * UNIT_conv_to_Mha
    idxlhs = fcol_in_mdf["Graing_land_desired_for_all_meat"]
    idx1 = fcol_in_mdf["Desired_grazing_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_Mha

    # Grazing_land_need[region] = Graing_land_desired_for_all_meat[region]
    idxlhs = fcol_in_mdf["Grazing_land_need"]
    idx1 = fcol_in_mdf["Graing_land_desired_for_all_meat"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Grazing_land_gap[region] = Grazing_land_need[region] - Grazing_land[region]
    idxlhs = fcol_in_mdf["Grazing_land_gap"]
    idx1 = fcol_in_mdf["Grazing_land_need"]
    idx2 = fcol_in_mdf["Grazing_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # acgl_to_gl[region] = MIN ( Abandoned_crop_and_grazing_land[region] , MAX ( 0 , Grazing_land_gap[region] ) ) * Fraction_of_grazing_land_gap_closed_from_acgl
    idxlhs = fcol_in_mdf["acgl_to_gl"]
    idx1 = fcol_in_mdf["Abandoned_crop_and_grazing_land"]
    idx2 = fcol_in_mdf["Grazing_land_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(mdf[rowi, idx1 + j], max(0, mdf[rowi, idx2 + j]))
        * Fraction_of_grazing_land_gap_closed_from_acgl
      )

    # Populated_land_need[region] = Population[region] * Urban_land_per_population[region]
    idxlhs = fcol_in_mdf["Populated_land_need"]
    idx1 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Urban_land_per_population[j]

    # Populated_land_gap[region] = Populated_land_need[region] - Populated_land[region]
    idxlhs = fcol_in_mdf["Populated_land_gap"]
    idx1 = fcol_in_mdf["Populated_land_need"]
    idx2 = fcol_in_mdf["Populated_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # acgl_to_pl[region] = MIN ( Abandoned_crop_and_grazing_land[region] , MAX ( 0 , Populated_land_gap[region] ) ) * Fraction_of_abandoned_agri_land_developed_for_urban_land
    idxlhs = fcol_in_mdf["acgl_to_pl"]
    idx1 = fcol_in_mdf["Abandoned_crop_and_grazing_land"]
    idx2 = fcol_in_mdf["Populated_land_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(mdf[rowi, idx1 + j], max(0, mdf[rowi, idx2 + j]))
        * Fraction_of_abandoned_agri_land_developed_for_urban_land
      )

    # Carbon_concentration_in_warm_surface = C_in_warm_surface_water_GtC / ( Warm_surface_water_volume_Gm3 + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_warm_ocean_0_to_100m_of_total )
    idxlhs = fcol_in_mdf["Carbon_concentration_in_warm_surface"]
    idx1 = fcol_in_mdf["C_in_warm_surface_water_GtC"]
    idx2 = fcol_in_mdf["Warm_surface_water_volume_Gm3"]
    idx3 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (
      mdf[rowi, idx2]
      + mdf[rowi, idx3]
      * UNIT_conversion_km3_to_Gm3
      * Frac_vol_warm_ocean_0_to_100m_of_total
    )

    # CC_in_warm_surface_ymoles_per_litre = Carbon_concentration_in_warm_surface * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
    idxlhs = fcol_in_mdf["CC_in_warm_surface_ymoles_per_litre"]
    idx1 = fcol_in_mdf["Carbon_concentration_in_warm_surface"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre

    # CC_in_warm_surface_ymoles_per_litre_dmnl = CC_in_warm_surface_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
    idxlhs = fcol_in_mdf["CC_in_warm_surface_ymoles_per_litre_dmnl"]
    idx1 = fcol_in_mdf["CC_in_warm_surface_ymoles_per_litre"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_ymoles_p_litre_to_dless

    # pH_in_warm_surface_water = UNIT_conversion_C_to_pH * ( 1 - 0.0017 * Temp_surface - 0.0003 ) * ( 163.2 * CC_in_warm_surface_ymoles_per_litre_dmnl ** ( - 0.385 ) )
    idxlhs = fcol_in_mdf["pH_in_warm_surface_water"]
    idx1 = fcol_in_mdf["Temp_surface"]
    idx2 = fcol_in_mdf["CC_in_warm_surface_ymoles_per_litre_dmnl"]
    mdf[rowi, idxlhs] = (
      UNIT_conversion_C_to_pH
      * (1 - 0.0017 * mdf[rowi, idx1] - 0.0003)
      * (163.2 * mdf[rowi, idx2] ** (-0.385))
    )

    # Temp_of_cold_surface_water = Temp_surface / 3
    idxlhs = fcol_in_mdf["Temp_of_cold_surface_water"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / 3

    # Carbon_concentration_in_cold_surface_ocean = C_in_cold_surface_water_GtC / ( Cold_surface_water_volume_Gm3 + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_cold_ocean_0_to_100m_of_total )
    idxlhs = fcol_in_mdf["Carbon_concentration_in_cold_surface_ocean"]
    idx1 = fcol_in_mdf["C_in_cold_surface_water_GtC"]
    idx2 = fcol_in_mdf["Cold_surface_water_volume_Gm3"]
    idx3 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (
      mdf[rowi, idx2]
      + mdf[rowi, idx3]
      * UNIT_conversion_km3_to_Gm3
      * Frac_vol_cold_ocean_0_to_100m_of_total
    )

    # CC_in_cold_surface_ymoles_per_litre = Carbon_concentration_in_cold_surface_ocean * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
    idxlhs = fcol_in_mdf["CC_in_cold_surface_ymoles_per_litre"]
    idx1 = fcol_in_mdf["Carbon_concentration_in_cold_surface_ocean"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre

    # CC_in_cold_surface_ymoles_per_litre_dmnl = CC_in_cold_surface_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
    idxlhs = fcol_in_mdf["CC_in_cold_surface_ymoles_per_litre_dmnl"]
    idx1 = fcol_in_mdf["CC_in_cold_surface_ymoles_per_litre"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_ymoles_p_litre_to_dless

    # pH_in_cold_suface_water = UNIT_conversion_C_to_pH * ( 1 - 0.0017 * Temp_of_cold_surface_water - 0.0003 ) * ( 163.2 * CC_in_cold_surface_ymoles_per_litre_dmnl ^ ( - 0.385 ) )
    idxlhs = fcol_in_mdf["pH_in_cold_suface_water"]
    idx1 = fcol_in_mdf["Temp_of_cold_surface_water"]
    idx2 = fcol_in_mdf["CC_in_cold_surface_ymoles_per_litre_dmnl"]
    mdf[rowi, idxlhs] = (
      UNIT_conversion_C_to_pH
      * (1 - 0.0017 * mdf[rowi, idx1] - 0.0003)
      * (163.2 * mdf[rowi, idx2] ** (-0.385))
    )

    # pH_in_surface = pH_in_warm_surface_water * Volume_warm_ocean_0_to_100m / ( Volume_warm_ocean_0_to_100m + Volume_cold_ocean_0_to_100m ) + pH_in_cold_suface_water * Volume_cold_ocean_0_to_100m / ( Volume_warm_ocean_0_to_100m + Volume_cold_ocean_0_to_100m )
    idxlhs = fcol_in_mdf["pH_in_surface"]
    idx1 = fcol_in_mdf["pH_in_warm_surface_water"]
    idx2 = fcol_in_mdf["pH_in_cold_suface_water"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Volume_warm_ocean_0_to_100m / (
      Volume_warm_ocean_0_to_100m + Volume_cold_ocean_0_to_100m
    ) + mdf[rowi, idx2] * Volume_cold_ocean_0_to_100m / (
      Volume_warm_ocean_0_to_100m + Volume_cold_ocean_0_to_100m
    )

    # pb_Ocean_acidification = pH_in_surface
    idxlhs = fcol_in_mdf["pb_Ocean_acidification"]
    idx1 = fcol_in_mdf["pH_in_surface"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Acidification_risk_score = IF_THEN_ELSE ( pb_Ocean_acidification_green_threshold > pb_Ocean_acidification , 1 , 0 )
    idxlhs = fcol_in_mdf["Acidification_risk_score"]
    idx1 = fcol_in_mdf["pb_Ocean_acidification"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      pb_Ocean_acidification_green_threshold > mdf[rowi, idx1], 1, 0
    )

    # DAC_CCS_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , DAC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , DAC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , DAC_R1_via_Excel , DAC_policy_Min ) ) )
    idxlhs = fcol_in_mdf["DAC_CCS_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     DAC_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       DAC_R2_via_Excel[j],       IF_THEN_ELSE(zeit >= Policy_start_year, DAC_R1_via_Excel[j], DAC_policy_Min),     ),   )

    # DAC_policy_with_RW[region] = DAC_CCS_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
    idxlhs = fcol_in_mdf["DAC_policy_with_RW"]
    idx1 = fcol_in_mdf["DAC_CCS_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # DAC_pol_div_100[region] = MIN ( DAC_policy_Max , MAX ( DAC_policy_Min , DAC_policy_with_RW[region] ) ) / 1
    idxlhs = fcol_in_mdf["DAC_pol_div_100"]
    idx1 = fcol_in_mdf["DAC_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(DAC_policy_Max, max(DAC_policy_Min, mdf[rowi, idx1 + j])) / 1
      )

    # DAC_policy[region] = SMOOTH3 ( DAC_pol_div_100[region] , DAC_Time_to_implement_goal )
    idxin = fcol_in_mdf["DAC_pol_div_100"]
    idx2 = fcol_in_mdf["DAC_policy_2"]
    idx1 = fcol_in_mdf["DAC_policy_1"]
    idxout = fcol_in_mdf["DAC_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (DAC_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (DAC_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (DAC_Time_to_implement_goal / 3)
        * dt
      )

    # Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture[region] = DAC_policy[region] * UNIT_conv_to_GtCO2_pr_yr
    idxlhs = fcol_in_mdf["Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture"
    ]
    idx1 = fcol_in_mdf["DAC_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_GtCO2_pr_yr

    # Nuclear_gen_cap_EU = ( Nuclear_gen_cap_EU_s + Nuclear_gen_cap_EU_g * math.exp ( - ( ( ( ( GDPpp_USED[eu] * UNIT_conv_to_make_exp_dmnl ) - Nuclear_gen_cap_EU_h ) ^ 2 ) / ( 2 * Nuclear_gen_cap_EU_k ^ 2 ) ) ) ) * UNIT_conv_to_GW
    idxlhs = fcol_in_mdf["Nuclear_gen_cap_EU"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      Nuclear_gen_cap_EU_s
      + Nuclear_gen_cap_EU_g
      * math.exp(
        -(
          (
            ((mdf[rowi, idx1 + 8] * UNIT_conv_to_make_exp_dmnl) - Nuclear_gen_cap_EU_h)
            ** 2
          )
          / (2 * Nuclear_gen_cap_EU_k**2)
        )
      )
    ) * UNIT_conv_to_GW

    # Nuclear_gen_cap_WO_EU[region] = Nuclear_gen_cap_WO_EU_L[region] / ( 1 + math.exp ( - Nuclear_gen_cap_WO_EU_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - Nuclear_gen_cap_WO_EU_x0[region] ) ) )
    idxlhs = fcol_in_mdf["Nuclear_gen_cap_WO_EU"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Nuclear_gen_cap_WO_EU_L[j] / (
        1
        + math.exp(
          -Nuclear_gen_cap_WO_EU_k[j]
          * (
            (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl)
            - Nuclear_gen_cap_WO_EU_x0[j]
          )
        )
      )

    # Nuclear_gen_cap[region] = IF_THEN_ELSE ( j==8 , Nuclear_gen_cap_EU , Nuclear_gen_cap_WO_EU )
    idxlhs = fcol_in_mdf["Nuclear_gen_cap"]
    idx1 = fcol_in_mdf["Nuclear_gen_cap_EU"]
    idx2 = fcol_in_mdf["Nuclear_gen_cap_WO_EU"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 8, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # Nuclear_gen_cap_after_depreciation[region] = Nuclear_gen_cap[region] * Nuclear_net_depreciation_multiplier_on_gen_cap
    idxlhs = fcol_in_mdf["Nuclear_gen_cap_after_depreciation"]
    idx1 = fcol_in_mdf["Nuclear_gen_cap"]
    idx2 = fcol_in_mdf["Nuclear_net_depreciation_multiplier_on_gen_cap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2]

    # El_from_nuclear[region] = Nuclear_gen_cap_after_depreciation[region] * Nuclear_capacity_factor * Hours_per_year * UNIT_conv_GWh_and_TWh
    idxlhs = fcol_in_mdf["El_from_nuclear"]
    idx1 = fcol_in_mdf["Nuclear_gen_cap_after_depreciation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Nuclear_capacity_factor
        * Hours_per_year
        * UNIT_conv_GWh_and_TWh
      )

    # wind_PV_nuclear_hydro_el_generation[region] = El_from_wind_and_PV[region] + El_from_nuclear[region] + El_from_Hydro[region]
    idxlhs = fcol_in_mdf["wind_PV_nuclear_hydro_el_generation"]
    idx1 = fcol_in_mdf["El_from_wind_and_PV"]
    idx2 = fcol_in_mdf["El_from_nuclear"]
    idx3 = fcol_in_mdf["El_from_Hydro"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # El_from_all_sources[region] = El_gen_from_fossil_fuels[region] + wind_PV_nuclear_hydro_el_generation[region]
    idxlhs = fcol_in_mdf["El_from_all_sources"]
    idx1 = fcol_in_mdf["El_gen_from_fossil_fuels"]
    idx2 = fcol_in_mdf["wind_PV_nuclear_hydro_el_generation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Actual_el_use_pp[region] = El_from_all_sources[region] / Population[region] * UNIT_conv_to_kWh_ppp
    idxlhs = fcol_in_mdf["Actual_el_use_pp"]
    idx1 = fcol_in_mdf["El_from_all_sources"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] * UNIT_conv_to_kWh_ppp
      )

    # Actual_inequality_index_higher_is_more_unequal_N_years_ago[region] = SMOOTH3I ( Actual_inequality_index_higher_is_more_unequal[region] , N_number_of_years_ago , Inequality_considered_normal_in_1980[region] )
    idxlhs = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_N_years_ago"]
    idxin = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal"]
    idx2 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_N_years_ago_2"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_N_years_ago_1"]
    idxout = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_N_years_ago"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (N_number_of_years_ago / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (N_number_of_years_ago / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (N_number_of_years_ago / 3)
        * dt
      )

    # GRASS_with_normal_cover_Mkm2 = GRASS_potential_area_Mkm2 - GRASS_area_burnt_Mkm2 - GRASS_deforested_Mkm2 - GRASS_area_harvested_Mkm2
    idxlhs = fcol_in_mdf["GRASS_with_normal_cover_Mkm2"]
    idx1 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["GRASS_area_burnt_Mkm2"]
    idx3 = fcol_in_mdf["GRASS_deforested_Mkm2"]
    idx4 = fcol_in_mdf["GRASS_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4]
    )

    # GRASS_being_deforested_Mkm2_py = GRASS_with_normal_cover_Mkm2 * Fraction_GRASS_being_deforested_1_py
    idxlhs = fcol_in_mdf["GRASS_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["GRASS_with_normal_cover_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Fraction_GRASS_being_deforested_1_py

    # GRASS_DeadB_and_SOM_tB_per_km2 = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / GRASS_with_normal_cover_Mkm2 * 1000
    idxlhs = fcol_in_mdf["GRASS_DeadB_and_SOM_tB_per_km2"]
    idx1 = fcol_in_mdf["GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    idx2 = fcol_in_mdf["GRASS_with_normal_cover_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] * 1000

    # GRASS_DeadB_SOM_being_lost_due_to_deforestation = GRASS_being_deforested_Mkm2_py * GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * GRASS_DeadB_and_SOM_tB_per_km2 / 1000
    idxlhs = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_deforestation"]
    idx1 = fcol_in_mdf["GRASS_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["GRASS_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting
      * mdf[rowi, idx2]
      / 1000
    )

    # Global_population = SUM ( Population[region!] )
    idxlhs = fcol_in_mdf["Global_population"]
    idx1 = fcol_in_mdf["Population"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_population_in_Bp = Global_population / UNIT_conv_to_Bp
    idxlhs = fcol_in_mdf["Global_population_in_Bp"]
    idx1 = fcol_in_mdf["Global_population"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conv_to_Bp

    # Urbanzation_Effect_on_biomass_use = WITH LOOKUP ( zeit , ( [ ( 1850 , 0 ) - ( 2300 , 5 ) ] , ( 1850 , 5 ) , ( 1880 , 4.71 ) , ( 1900 , 4.4 ) , ( 1925 , 3.73 ) , ( 1945 , 3.11 ) , ( 1965 , 2.37 ) , ( 1975 , 1.93 ) , ( 1988 , 1.4 ) , ( 2000 , 1 ) , ( 2012 , 0.79 ) , ( 2028 , 0.59 ) , ( 2060 , 0.37 ) , ( 2100 , 0.25 ) , ( 2300 , 0 ) ) )
    tabidx = ftab_in_d_table[  "Urbanzation_Effect_on_biomass_use"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Urbanzation_Effect_on_biomass_use"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Effect_of_population_and_urbanization_on_biomass_use = Global_population_in_Bp / Population_2000_bn * Urbanzation_Effect_on_biomass_use
    idxlhs = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    idx1 = fcol_in_mdf["Global_population_in_Bp"]
    idx2 = fcol_in_mdf["Urbanzation_Effect_on_biomass_use"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Population_2000_bn * mdf[rowi, idx2]

    # Use_of_GRASS_biomass_for_energy = Use_of_GRASS_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_GRASS_biomass_for_energy"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_GRASS_for_energy_in_2000_GtBiomass * mdf[rowi, idx1] * UNIT_conversion_1_py
    )

    # Effect_of_CO2_on_new_biomass_growth = 1 + Sensitivity_of_biomass_new_growth_to_CO2_concentration * LN ( CO2_concentration_used_after_any_experiments_ppm / CO2_concentration_ppm_in_1850 )
    idxlhs = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx1 = fcol_in_mdf["CO2_concentration_used_after_any_experiments_ppm"]
    mdf[rowi, idxlhs] = (
      1
      + Sensitivity_of_biomass_new_growth_to_CO2_concentration
      * math.log(mdf[rowi, idx1] / CO2_concentration_ppm_in_1850)
    )

    # Effect_of_temperature_on_new_biomass_growth_dmnl = ( 1 + Slope_of_temp_eff_on_potential_biomass_per_km2 * ( Temp_surface / ( Temp_surface_1850 - 273.15 ) - 1 ) )
    idxlhs = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = 1 + Slope_of_temp_eff_on_potential_biomass_per_km2 * (
      mdf[rowi, idx1] / (Temp_surface_1850 - 273.15) - 1
    )

    # GRASS_living_biomass_densitiy_tBiomass_pr_km2 = GRASS_living_biomass_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
    idxlhs = fcol_in_mdf["GRASS_living_biomass_densitiy_tBiomass_pr_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    mdf[rowi, idxlhs] = (
      GRASS_living_biomass_densitiy_in_1850_tBiomass_pr_km2
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
    )

    # GRASS_being_harvested_Mkm2_py = Use_of_GRASS_biomass_for_energy / GRASS_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["GRASS_being_harvested_Mkm2_py"]
    idx1 = fcol_in_mdf["Use_of_GRASS_biomass_for_energy"]
    idx2 = fcol_in_mdf["GRASS_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / mdf[rowi, idx2] * UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting = GRASS_being_harvested_Mkm2_py * GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * GRASS_DeadB_and_SOM_tB_per_km2 / 1000
    idxlhs = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx1 = fcol_in_mdf["GRASS_being_harvested_Mkm2_py"]
    idx2 = fcol_in_mdf["GRASS_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * GRASS_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting
      * mdf[rowi, idx2]
      / 1000
    )

    # GRASS_runoff = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / GRASS_runoff_time
    idxlhs = fcol_in_mdf["GRASS_runoff"]
    idx1 = fcol_in_mdf["GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / GRASS_runoff_time

    # Effect_of_temperature_on_fire_incidence = 1 + Slope_temp_eff_on_fire_incidence * ( Temp_surface / ( Temp_surface_1850 - 273.15 ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temperature_on_fire_incidence"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = 1 + Slope_temp_eff_on_fire_incidence * (
      mdf[rowi, idx1] / (Temp_surface_1850 - 273.15) - 1
    )

    # GRASS_burning_Mkm2_py = GRASS_with_normal_cover_Mkm2 * Effect_of_temperature_on_fire_incidence * GRASS_Normal_fire_incidence_fraction_py / 100
    idxlhs = fcol_in_mdf["GRASS_burning_Mkm2_py"]
    idx1 = fcol_in_mdf["GRASS_with_normal_cover_Mkm2"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_fire_incidence"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * mdf[rowi, idx2] * GRASS_Normal_fire_incidence_fraction_py / 100
    )

    # GRASS_soil_degradation_from_forest_fires = GRASS_burning_Mkm2_py * GRASS_DeadB_and_SOM_tB_per_km2 / 1000 * GRASS_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    idxlhs = fcol_in_mdf["GRASS_soil_degradation_from_forest_fires"]
    idx1 = fcol_in_mdf["GRASS_burning_Mkm2_py"]
    idx2 = fcol_in_mdf["GRASS_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * mdf[rowi, idx2]
      / 1000
      * GRASS_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    )

    # GRASS_Dead_biomass_decomposing = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / GRASS_Time_to_decompose_undisturbed_dead_biomass_yr
    idxlhs = fcol_in_mdf["GRASS_Dead_biomass_decomposing"]
    idx1 = fcol_in_mdf["GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / GRASS_Time_to_decompose_undisturbed_dead_biomass_yr
    )

    # Sum_outflows_GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM = GRASS_DeadB_SOM_being_lost_due_to_deforestation + GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting + GRASS_runoff + GRASS_soil_degradation_from_forest_fires + GRASS_Dead_biomass_decomposing
    idxlhs = fcol_in_mdf["Sum_outflows_GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM"
    ]
    idx1 = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_deforestation"]
    idx2 = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx3 = fcol_in_mdf["GRASS_runoff"]
    idx4 = fcol_in_mdf["GRASS_soil_degradation_from_forest_fires"]
    idx5 = fcol_in_mdf["GRASS_Dead_biomass_decomposing"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
    )

    # NF_with_normal_cover_Mkm2 = NF_potential_area_Mkm2 - NF_area_burnt_Mkm2 - NF_area_deforested_Mkm2 - NF_area_clear_cut_Mkm2 - NF_area_harvested_Mkm2
    idxlhs = fcol_in_mdf["NF_with_normal_cover_Mkm2"]
    idx1 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["NF_area_burnt_Mkm2"]
    idx3 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    idx4 = fcol_in_mdf["NF_area_clear_cut_Mkm2"]
    idx5 = fcol_in_mdf["NF_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      - mdf[rowi, idx2]
      - mdf[rowi, idx3]
      - mdf[rowi, idx4]
      - mdf[rowi, idx5]
    )

    # NF_being_deforested_Mkm2_py = NF_with_normal_cover_Mkm2 * NF_historical_deforestation_pct_py
    idxlhs = fcol_in_mdf["NF_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_with_normal_cover_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * NF_historical_deforestation_pct_py

    # NF_DeadB_and_SOM_tB_per_km2 = NF_DeadB_and_SOM_densitiy_in_1850 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
    idxlhs = fcol_in_mdf["NF_DeadB_and_SOM_tB_per_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    mdf[rowi, idxlhs] = (
      NF_DeadB_and_SOM_densitiy_in_1850 * mdf[rowi, idx1] * mdf[rowi, idx2]
    )

    # NF_DeadB_SOM_being_lost_due_to_deforestation = NF_being_deforested_Mkm2_py * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_deforestation"]
    idx1 = fcol_in_mdf["NF_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # Use_of_NF_biomass_for_energy = Use_of_NF_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_NF_biomass_for_energy"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_NF_for_energy_in_2000_GtBiomass * mdf[rowi, idx1] * UNIT_conversion_1_py
    )

    # Global_forest_land = SUM ( Forest_land[region!] )
    idxlhs = fcol_in_mdf["Global_forest_land"]
    idx1 = fcol_in_mdf["Forest_land"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Forest_land_rel_to_init = Global_forest_land / Global_forest_land_in_1980
    idxlhs = fcol_in_mdf["Forest_land_rel_to_init"]
    idx1 = fcol_in_mdf["Global_forest_land"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Global_forest_land_in_1980

    # Smoothed_Forest_land_rel_to_init = SMOOTH3 ( Forest_land_rel_to_init , Time_to_smooth_forest_land_comparison )
    idx1 = fcol_in_mdf["Forest_land_rel_to_init"]
    idxin = fcol_in_mdf["Forest_land_rel_to_init"]
    idx2 = fcol_in_mdf["Smoothed_Forest_land_rel_to_init_2"]
    idx1 = fcol_in_mdf["Smoothed_Forest_land_rel_to_init_1"]
    idxout = fcol_in_mdf["Smoothed_Forest_land_rel_to_init"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idxin] - mdf[rowi - 1, idx1])
      / (Time_to_smooth_forest_land_comparison / 3)
      * dt
    )
    mdf[rowi, idx2] = (
      mdf[rowi - 1, idx2]
      + (mdf[rowi - 1, idx1] - mdf[rowi - 1, idx2])
      / (Time_to_smooth_forest_land_comparison / 3)
      * dt
    )
    mdf[rowi, idxout] = (
      mdf[rowi - 1, idxout]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idxout])
      / (Time_to_smooth_forest_land_comparison / 3)
      * dt
    )

    # NF_living_biomass_densitiy_tBiomass_pr_km2 = NF_living_biomass_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl * Smoothed_Forest_land_rel_to_init
    idxlhs = fcol_in_mdf["NF_living_biomass_densitiy_tBiomass_pr_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    idx3 = fcol_in_mdf["Smoothed_Forest_land_rel_to_init"]
    mdf[rowi, idxlhs] = (
      NF_living_biomass_densitiy_in_1850_tBiomass_pr_km2
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
    )

    # NF_usage_as_pct_of_potential_area = ( NF_area_burnt_Mkm2 + NF_area_clear_cut_Mkm2 + NF_area_deforested_Mkm2 + NF_area_harvested_Mkm2 ) / NF_with_normal_cover_Mkm2
    idxlhs = fcol_in_mdf["NF_usage_as_pct_of_potential_area"]
    idx1 = fcol_in_mdf["NF_area_burnt_Mkm2"]
    idx2 = fcol_in_mdf["NF_area_clear_cut_Mkm2"]
    idx3 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    idx4 = fcol_in_mdf["NF_area_harvested_Mkm2"]
    idx5 = fcol_in_mdf["NF_with_normal_cover_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    ) / mdf[rowi, idx5]

    # NF_usage_cutoff = WITH LOOKUP ( NF_usage_as_pct_of_potential_area , ( [ ( 0.5 , 0 ) - ( 0.8 , 1 ) ] , ( 0.5 , 1 ) , ( 0.621101 , 0.921053 ) , ( 0.700917 , 0.732456 ) , ( 0.738532 , 0.442982 ) , ( 0.761468 , 0.223684 ) , ( 0.777064 , 0.0789474 ) , ( 0.8 , 0 ) ) )
    tabidx = ftab_in_d_table["NF_usage_cutoff"]  # fetch the correct table
    idxlhs = fcol_in_mdf["NF_usage_cutoff"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["NF_usage_as_pct_of_potential_area"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # POLICY_4_Stopping_logging_in_Northern_forests = IF_THEN_ELSE ( zeit > 2015 , 0 , 1 )
    idxlhs = fcol_in_mdf["POLICY_4_Stopping_logging_in_Northern_forests"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit > 2015, 0, 1)

    # NF_being_harvested_Mkm2_py =  Use_of_NF_biomass_for_energy / NF_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py * NF_usage_cutoff * IF_THEN_ELSE ( Switch_to_run_POLICY_4_Stopping_logging_in_Northern_forests_0_off_1_on == 1 , POLICY_4_Stopping_logging_in_Northern_forests , 1 )
    idxlhs = fcol_in_mdf["NF_being_harvested_Mkm2_py"]
    idx1 = fcol_in_mdf["Use_of_NF_biomass_for_energy"]
    idx2 = fcol_in_mdf["NF_living_biomass_densitiy_tBiomass_pr_km2"]
    idx3 = fcol_in_mdf["NF_usage_cutoff"]
    idx4 = fcol_in_mdf["POLICY_4_Stopping_logging_in_Northern_forests"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / mdf[rowi, idx2]
      * UNIT_conversion_GtBiomass_py_to_Mkm2_py
      * mdf[rowi, idx3]
      * IF_THEN_ELSE(
        Switch_to_run_POLICY_4_Stopping_logging_in_Northern_forests_0_off_1_on == 1,     mdf[rowi, idx4],     1,   )
    )

    # NF_clear_cut_fraction = WITH LOOKUP ( zeit , ( [ ( 1850 , - 0.0005 ) - ( 2100 , 0.9 ) ] , ( 1850 , 0 ) , ( 1900 , 0.5 ) , ( 1950 , 0.8 ) , ( 2000 , 0.8 ) , ( 2050 , 0.6 ) , ( 2100 , 0.8 ) ) )
    tabidx = ftab_in_d_table["NF_clear_cut_fraction"]  # fetch the correct table
    idxlhs = fcol_in_mdf["NF_clear_cut_fraction"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # NF_being_harvested_normally_Mkm2_py = NF_being_harvested_Mkm2_py * ( 1 - NF_clear_cut_fraction )
    idxlhs = fcol_in_mdf["NF_being_harvested_normally_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_being_harvested_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_clear_cut_fraction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * (1 - mdf[rowi, idx2])

    # NF_DeadB_SOM_being_lost_due_to_energy_harvesting = NF_being_harvested_normally_Mkm2_py * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx1 = fcol_in_mdf["NF_being_harvested_normally_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # NF_runoff = NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / NF_runoff_time
    idxlhs = fcol_in_mdf["NF_runoff"]
    idx1 = fcol_in_mdf["NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / NF_runoff_time

    # NF_being_harvested_by_clear_cutting_Mkm2_py = NF_being_harvested_Mkm2_py * NF_clear_cut_fraction
    idxlhs = fcol_in_mdf["NF_being_harvested_by_clear_cutting_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_being_harvested_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_clear_cut_fraction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # NF_soil_degradation_from_clear_cutting = NF_being_harvested_by_clear_cutting_Mkm2_py * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["NF_soil_degradation_from_clear_cutting"]
    idx1 = fcol_in_mdf["NF_being_harvested_by_clear_cutting_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * NF_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # NF_burning_Mkm2_py = NF_with_normal_cover_Mkm2 * Effect_of_temperature_on_fire_incidence * NF_Normal_fire_incidence_fraction_py / 100
    idxlhs = fcol_in_mdf["NF_burning_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_with_normal_cover_Mkm2"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_fire_incidence"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * mdf[rowi, idx2] * NF_Normal_fire_incidence_fraction_py / 100
    )

    # NF_soil_degradation_from_forest_fires = NF_burning_Mkm2_py * NF_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py * NF_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    idxlhs = fcol_in_mdf["NF_soil_degradation_from_forest_fires"]
    idx1 = fcol_in_mdf["NF_burning_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
      * NF_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    )

    # NF_Dead_biomass_decomposing = NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / NF_Time_to_decompose_undisturbed_dead_biomass_yr
    idxlhs = fcol_in_mdf["NF_Dead_biomass_decomposing"]
    idx1 = fcol_in_mdf["NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / NF_Time_to_decompose_undisturbed_dead_biomass_yr
    )

    # NF_Sum_outflows_NF_Dead_biomass_litter_and_soil_organic_matter_SOM = NF_DeadB_SOM_being_lost_due_to_deforestation + NF_DeadB_SOM_being_lost_due_to_energy_harvesting + NF_runoff + NF_soil_degradation_from_clear_cutting + NF_soil_degradation_from_forest_fires + NF_Dead_biomass_decomposing
    idxlhs = fcol_in_mdf["NF_Sum_outflows_NF_Dead_biomass_litter_and_soil_organic_matter_SOM"
    ]
    idx1 = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_deforestation"]
    idx2 = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx3 = fcol_in_mdf["NF_runoff"]
    idx4 = fcol_in_mdf["NF_soil_degradation_from_clear_cutting"]
    idx5 = fcol_in_mdf["NF_soil_degradation_from_forest_fires"]
    idx6 = fcol_in_mdf["NF_Dead_biomass_decomposing"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
    )

    # TROP_with_normal_cover = TROP_potential_area_Mkm2 - TROP_area_burnt - TROP_area_deforested - TROP_area_clear_cut - TROP_area_harvested_Mkm2
    idxlhs = fcol_in_mdf["TROP_with_normal_cover"]
    idx1 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["TROP_area_burnt"]
    idx3 = fcol_in_mdf["TROP_area_deforested"]
    idx4 = fcol_in_mdf["TROP_area_clear_cut"]
    idx5 = fcol_in_mdf["TROP_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      - mdf[rowi, idx2]
      - mdf[rowi, idx3]
      - mdf[rowi, idx4]
      - mdf[rowi, idx5]
    )

    # TROP_deforestion_multiplier = WITH LOOKUP ( zeit , ( [ ( 1850 , 0 ) - ( 2100 , 2 ) ] , ( 1850 , 0 ) , ( 1970 , 0.4 ) , ( 2000 , 0.5 ) , ( 2020 , 0.5 ) , ( 2100 , 0 ) ) )
    tabidx = ftab_in_d_table["TROP_deforestion_multiplier"]  # fetch the correct table
    idxlhs = fcol_in_mdf["TROP_deforestion_multiplier"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # TROP_historical_deforestation = ( TROP_Ref_historical_deforestation / 100 ) * TROP_deforestion_multiplier
    idxlhs = fcol_in_mdf["TROP_historical_deforestation"]
    idx1 = fcol_in_mdf["TROP_deforestion_multiplier"]
    mdf[rowi, idxlhs] = (TROP_Ref_historical_deforestation / 100) * mdf[rowi, idx1]

    # TROP_deforested_as_pct_of_potential_area = TROP_area_deforested / TROP_potential_area_Mkm2
    idxlhs = fcol_in_mdf["TROP_deforested_as_pct_of_potential_area"]
    idx1 = fcol_in_mdf["TROP_area_deforested"]
    idx2 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]

    # TROP_deforestation_cutoff = WITH LOOKUP ( TROP_deforested_as_pct_of_potential_area , ( [ ( 0.5 , 0 ) - ( 0.8 , 1 ) ] , ( 0.5 , 1 ) , ( 0.621101 , 0.921053 ) , ( 0.700917 , 0.732456 ) , ( 0.738532 , 0.442982 ) , ( 0.761468 , 0.223684 ) , ( 0.777064 , 0.0789474 ) , ( 0.8 , 0 ) ) )
    tabidx = ftab_in_d_table["TROP_deforestation_cutoff"]  # fetch the correct table
    idxlhs = fcol_in_mdf["TROP_deforestation_cutoff"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["TROP_deforested_as_pct_of_potential_area"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Stop_of_human_deforestation = IF_THEN_ELSE ( zeit > Time_at_which_human_deforestation_is_stopped , 0 , 1 )
    idxlhs = fcol_in_mdf["Stop_of_human_deforestation"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > Time_at_which_human_deforestation_is_stopped, 0, 1
    )

    # TROP_being_deforested_Mkm2_py = TROP_with_normal_cover * TROP_historical_deforestation * TROP_deforestation_cutoff * Stop_of_human_deforestation
    idxlhs = fcol_in_mdf["TROP_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["TROP_with_normal_cover"]
    idx2 = fcol_in_mdf["TROP_historical_deforestation"]
    idx3 = fcol_in_mdf["TROP_deforestation_cutoff"]
    idx4 = fcol_in_mdf["Stop_of_human_deforestation"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3] * mdf[rowi, idx4]
    )

    # TROP_DeadB_and_SOM_tB_per_km2 = TROP_DeadB_and_SOM_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
    idxlhs = fcol_in_mdf["TROP_DeadB_and_SOM_tB_per_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    mdf[rowi, idxlhs] = (
      TROP_DeadB_and_SOM_densitiy_in_1850_tBiomass_pr_km2
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
    )

    # TROP_DeadB_SOM_being_lost_due_to_deforestation = TROP_being_deforested_Mkm2_py * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_deforestation"]
    idx1 = fcol_in_mdf["TROP_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["TROP_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TROP_Use_of_NF_biomass_for_energy = Use_of_TROP_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_to_yr
    idxlhs = fcol_in_mdf["TROP_Use_of_NF_biomass_for_energy"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_TROP_for_energy_in_2000_GtBiomass * mdf[rowi, idx1] * UNIT_conversion_to_yr
    )

    # TROP_living_biomass_densitiy_tBiomass_pr_km2 = TROP_living_biomass_densitiy_in_1850_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl * Smoothed_Forest_land_rel_to_init
    idxlhs = fcol_in_mdf["TROP_living_biomass_densitiy_tBiomass_pr_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    idx3 = fcol_in_mdf["Smoothed_Forest_land_rel_to_init"]
    mdf[rowi, idxlhs] = (
      TROP_living_biomass_densitiy_in_1850_tBiomass_pr_km2
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
    )

    # TROP_being_harvested = TROP_Use_of_NF_biomass_for_energy / TROP_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TROP_being_harvested"]
    idx1 = fcol_in_mdf["TROP_Use_of_NF_biomass_for_energy"]
    idx2 = fcol_in_mdf["TROP_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / mdf[rowi, idx2] * UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TROP_being_harvested_normally = TROP_being_harvested * ( 1 - TROP_clear_cut_fraction )
    idxlhs = fcol_in_mdf["TROP_being_harvested_normally"]
    idx1 = fcol_in_mdf["TROP_being_harvested"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * (1 - TROP_clear_cut_fraction)

    # TROP_DeadB_SOM_being_lost_due_to_energy_harvesting = TROP_being_harvested_normally * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx1 = fcol_in_mdf["TROP_being_harvested_normally"]
    idx2 = fcol_in_mdf["TROP_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TROP_runoff = TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TROP_runoff_time
    idxlhs = fcol_in_mdf["TROP_runoff"]
    idx1 = fcol_in_mdf["TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / TROP_runoff_time

    # TROP_being_harvested_by_clear_cutting = TROP_being_harvested * TROP_clear_cut_fraction
    idxlhs = fcol_in_mdf["TROP_being_harvested_by_clear_cutting"]
    idx1 = fcol_in_mdf["TROP_being_harvested"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * TROP_clear_cut_fraction

    # TROP_soil_degradation_from_clear_cutting = TROP_being_harvested_by_clear_cutting * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TROP_soil_degradation_from_clear_cutting"]
    idx1 = fcol_in_mdf["TROP_being_harvested_by_clear_cutting"]
    idx2 = fcol_in_mdf["TROP_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * TROP_fraction_of_DeadB_and_SOM_being_destroyed_by_clear_cutting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TROP_burning = TROP_with_normal_cover * Effect_of_temperature_on_fire_incidence * TROP_Normal_fire_incidence / 100
    idxlhs = fcol_in_mdf["TROP_burning"]
    idx1 = fcol_in_mdf["TROP_with_normal_cover"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_fire_incidence"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * mdf[rowi, idx2] * TROP_Normal_fire_incidence / 100
    )

    # TROP_soil_degradation_from_forest_fires = TROP_burning * TROP_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py * TROP_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    idxlhs = fcol_in_mdf["TROP_soil_degradation_from_forest_fires"]
    idx1 = fcol_in_mdf["TROP_burning"]
    idx2 = fcol_in_mdf["TROP_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
      * TROP_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    )

    # TROP_Dead_biomass_decomposing = TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TROP_Time_to_decompose_undisturbed_dead_biomass_yr
    idxlhs = fcol_in_mdf["TROP_Dead_biomass_decomposing"]
    idx1 = fcol_in_mdf["TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / TROP_Time_to_decompose_undisturbed_dead_biomass_yr
    )

    # TROP_Sum_outflows_TROP_Dead_biomass_litter_and_soil_organic_matter_SOM = TROP_DeadB_SOM_being_lost_due_to_deforestation + TROP_DeadB_SOM_being_lost_due_to_energy_harvesting + TROP_runoff + TROP_soil_degradation_from_clear_cutting + TROP_soil_degradation_from_forest_fires + TROP_Dead_biomass_decomposing
    idxlhs = fcol_in_mdf["TROP_Sum_outflows_TROP_Dead_biomass_litter_and_soil_organic_matter_SOM"
    ]
    idx1 = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_deforestation"]
    idx2 = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx3 = fcol_in_mdf["TROP_runoff"]
    idx4 = fcol_in_mdf["TROP_soil_degradation_from_clear_cutting"]
    idx5 = fcol_in_mdf["TROP_soil_degradation_from_forest_fires"]
    idx6 = fcol_in_mdf["TROP_Dead_biomass_decomposing"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
    )

    # Indicated_wellbeing_from_env_damage[region] = MAX ( 0 , 1 + SoE_of_env_damage_indicator * Combined_env_damage_indicator )
    idxlhs = fcol_in_mdf["Indicated_wellbeing_from_env_damage"]
    idx1 = fcol_in_mdf["Combined_env_damage_indicator"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, 1 + SoE_of_env_damage_indicator * mdf[rowi, idx1])

    # Actual_wellbeing_from_env_damage[region] = SMOOTH3 ( Indicated_wellbeing_from_env_damage[region] , Time_for_env_damage_to_affect_wellbeing )
    idxin = fcol_in_mdf["Indicated_wellbeing_from_env_damage"]
    idx2 = fcol_in_mdf["Actual_wellbeing_from_env_damage_2"]
    idx1 = fcol_in_mdf["Actual_wellbeing_from_env_damage_1"]
    idxout = fcol_in_mdf["Actual_wellbeing_from_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_for_env_damage_to_affect_wellbeing / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_for_env_damage_to_affect_wellbeing / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_for_env_damage_to_affect_wellbeing / 3)
        * dt
      )

    # Adding_capacity[region] = Capacity_under_construction[region] / Capacity_construction_time
    idxlhs = fcol_in_mdf["Adding_capacity"]
    idx1 = fcol_in_mdf["Capacity_under_construction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Capacity_construction_time

    # El_use_pp_US = El_use_pp_US_s + El_use_pp_US_g * math.exp ( - ( ( ( GDPpp_USED[us] * UNIT_conv_to_make_exp_dmnl ) - El_use_pp_US_h ) ^ 2 ) / ( 1.8 * El_use_pp_US_k ^ 2 ) )
    idxlhs = fcol_in_mdf["El_use_pp_US"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = El_use_pp_US_s + El_use_pp_US_g * math.exp(
      -(((mdf[rowi, idx1 + 0] * UNIT_conv_to_make_exp_dmnl) - El_use_pp_US_h) ** 2)
      / (1.8 * El_use_pp_US_k**2)
    )

    # El_use_pp_WO_US[region] = El_use_pp_WO_US_L[region] / ( 1 + math.exp ( - El_use_pp_WO_US_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - El_use_pp_WO_US_x0[region] ) ) )
    idxlhs = fcol_in_mdf["El_use_pp_WO_US"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = El_use_pp_WO_US_L[j] / (
        1
        + math.exp(
          -El_use_pp_WO_US_k[j]
          * ((mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) - El_use_pp_WO_US_x0[j])
        )
      )

    # El_use_pp[region] = IF_THEN_ELSE ( j==0 , El_use_pp_US , El_use_pp_WO_US )
    idxlhs = fcol_in_mdf["El_use_pp"]
    idx1 = fcol_in_mdf["El_use_pp_US"]
    idx2 = fcol_in_mdf["El_use_pp_WO_US"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 0, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # El_use_pp_in_MWh_ppy[region] = El_use_pp[region] * UNIT_conv_to_MWh_ppy
    idxlhs = fcol_in_mdf["El_use_pp_in_MWh_ppy"]
    idx1 = fcol_in_mdf["El_use_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_MWh_ppy

    # Demand_for_El_before_NEP[region] = ( ( ( Population[region] * El_use_pp_in_MWh_ppy[region] ) / Extra_energy_productivity_index_2024_is_1[region] ) ) * UNIT_conv_to_TWh
    idxlhs = fcol_in_mdf["Demand_for_El_before_NEP"]
    idx1 = fcol_in_mdf["Population"]
    idx2 = fcol_in_mdf["El_use_pp_in_MWh_ppy"]
    idx3 = fcol_in_mdf["Extra_energy_productivity_index_2024_is_1"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j]
      ) * UNIT_conv_to_TWh

    # Increase_in_el_dmd_from_NEP[region] = Fossil_fuel_for_NON_El_use_that_IS_being_electrified[region] * Conversion_Mtoe_to_TWh[region]
    idxlhs = fcol_in_mdf["Increase_in_el_dmd_from_NEP"]
    idx1 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_being_electrified"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Conversion_Mtoe_to_TWh[j]

    # Demand_for_El_afer_NEP[region] = Demand_for_El_before_NEP[region] + Increase_in_el_dmd_from_NEP[region]
    idxlhs = fcol_in_mdf["Demand_for_El_afer_NEP"]
    idx1 = fcol_in_mdf["Demand_for_El_before_NEP"]
    idx2 = fcol_in_mdf["Increase_in_el_dmd_from_NEP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Demand_for_el_from_fossil_fuel[region] = MAX ( 0 , Demand_for_El_afer_NEP[region] - wind_PV_nuclear_hydro_el_generation[region] )
    idxlhs = fcol_in_mdf["Demand_for_el_from_fossil_fuel"]
    idx1 = fcol_in_mdf["Demand_for_El_afer_NEP"]
    idx2 = fcol_in_mdf["wind_PV_nuclear_hydro_el_generation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])

    # Desired_fossil_gen_capacity[region] = Demand_for_el_from_fossil_fuel[region] / Fossil_capacity_factor[region] / Hours_per_year / UNIT_conv_GWh_and_TWh
    idxlhs = fcol_in_mdf["Desired_fossil_gen_capacity"]
    idx1 = fcol_in_mdf["Demand_for_el_from_fossil_fuel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        / Fossil_capacity_factor[j]
        / Hours_per_year
        / UNIT_conv_GWh_and_TWh
      )

    # Discarding_of_FEGC[region] = Fossil_el_gen_cap[region] / Life_of_fossil_el_gen_cap
    idxlhs = fcol_in_mdf["Discarding_of_FEGC"]
    idx1 = fcol_in_mdf["Fossil_el_gen_cap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Life_of_fossil_el_gen_cap

    # Desired_fossil_el_capacity_change[region] = ( Desired_fossil_gen_capacity[region] - Fossil_el_gen_cap[region] ) / Time_to_close_gap_in_fossil_el_cap[region] + Discarding_of_FEGC[region]
    idxlhs = fcol_in_mdf["Desired_fossil_el_capacity_change"]
    idx1 = fcol_in_mdf["Desired_fossil_gen_capacity"]
    idx2 = fcol_in_mdf["Fossil_el_gen_cap"]
    idx3 = fcol_in_mdf["Discarding_of_FEGC"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]
      ) / Time_to_close_gap_in_fossil_el_cap[j] + mdf[rowi, idx3 + j]

    # Addition_of_FEGC[region] = Desired_fossil_el_capacity_change[region]
    idxlhs = fcol_in_mdf["Addition_of_FEGC"]
    idx1 = fcol_in_mdf["Desired_fossil_el_capacity_change"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # ISPV_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , ISPV_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , ISPV_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , ISPV_R1_via_Excel , ISPV_policy_Min ) ) )
    idxlhs = fcol_in_mdf["ISPV_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     ISPV_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       ISPV_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, ISPV_R1_via_Excel[j], ISPV_policy_Min
          ),     ),   )

    # ISPV_policy_with_RW[region] = ISPV_policy_Min + ( ISPV_rounds_via_Excel[region] - ISPV_policy_Min ) * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
    idxlhs = fcol_in_mdf["ISPV_policy_with_RW"]
    idx1 = fcol_in_mdf["ISPV_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (ISPV_policy_Min
        + (mdf[rowi, idx1 + j] - ISPV_policy_Min)
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
      )

    # ISPV_pol_div_100[region] = MIN ( ISPV_policy_Max , MAX ( ISPV_policy_Min , ISPV_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["ISPV_pol_div_100"]
    idx1 = fcol_in_mdf["ISPV_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(ISPV_policy_Max, max(ISPV_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # wind_and_PV_el_share_max[region] = SMOOTH3 ( ISPV_pol_div_100[region] , Time_to_implement_ISPV_goal )
    idxin = fcol_in_mdf["ISPV_pol_div_100"]
    idx2 = fcol_in_mdf["wind_and_PV_el_share_max_2"]
    idx1 = fcol_in_mdf["wind_and_PV_el_share_max_1"]
    idxout = fcol_in_mdf["wind_and_PV_el_share_max"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_implement_ISPV_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_implement_ISPV_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_implement_ISPV_goal / 3)
        * dt
      )

    # wind_and_PV_el_share[region] = wind_and_PV_el_share_max[region] / ( 1 + math.exp ( - wind_and_PV_el_share_k[region] * ( ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) - wind_and_PV_el_share_x0[region] ) ) )
    idxlhs = fcol_in_mdf["wind_and_PV_el_share"]
    idx1 = fcol_in_mdf["wind_and_PV_el_share_max"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        1
        + math.exp(
          -wind_and_PV_el_share_k[j]
          * (
            (mdf[rowi, idx2 + j] * UNIT_conv_to_make_exp_dmnl)
            - wind_and_PV_el_share_x0[j]
          )
        )
      )

    # Goal_for_suppy_of_wind_and_PV_el[region] = Demand_for_El_afer_NEP[region] * wind_and_PV_el_share[region]
    idxlhs = fcol_in_mdf["Goal_for_suppy_of_wind_and_PV_el"]
    idx1 = fcol_in_mdf["Demand_for_El_afer_NEP"]
    idx2 = fcol_in_mdf["wind_and_PV_el_share"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Desired_wind_and_PV_el_cap[region] = Goal_for_suppy_of_wind_and_PV_el[region] / Hours_per_year / wind_and_PV_capacity_factor[region] / UNIT_conv_GWh_and_TWh
    idxlhs = fcol_in_mdf["Desired_wind_and_PV_el_cap"]
    idx1 = fcol_in_mdf["Goal_for_suppy_of_wind_and_PV_el"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        / Hours_per_year
        / wind_and_PV_capacity_factor
        / UNIT_conv_GWh_and_TWh
      )

    # Goal_for_wind_and_PV_el_capacity_change[region] = Desired_wind_and_PV_el_cap[region] - wind_and_PV_el_capacity[region]
    idxlhs = fcol_in_mdf["Goal_for_wind_and_PV_el_capacity_change"]
    idx1 = fcol_in_mdf["Desired_wind_and_PV_el_cap"]
    idx2 = fcol_in_mdf["wind_and_PV_el_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Discarding_wind_and_PV_el_capacity[region] = wind_and_PV_el_capacity[region] / Lifetime_of_wind_and_PV_el_cap
    idxlhs = fcol_in_mdf["Discarding_wind_and_PV_el_capacity"]
    idx1 = fcol_in_mdf["wind_and_PV_el_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Lifetime_of_wind_and_PV_el_cap

    # Addition_of_wind_and_PV_el_capacity[region] = MAX ( 0 , ( Goal_for_wind_and_PV_el_capacity_change[region] / wind_and_PV_construction_time ) + Discarding_wind_and_PV_el_capacity[region] )
    idxlhs = fcol_in_mdf["Addition_of_wind_and_PV_el_capacity"]
    idx1 = fcol_in_mdf["Goal_for_wind_and_PV_el_capacity_change"]
    idx2 = fcol_in_mdf["Discarding_wind_and_PV_el_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0, (mdf[rowi, idx1 + j] / wind_and_PV_construction_time) + mdf[rowi, idx2 + j]
      )

    # Crop_yield_last_year[region] = SMOOTHI ( Crop_yield_with_soil_quality_CO2_and_env_dam_effects[region] , One_year , crop_yield_in_1980[region] )
    idx1 = fcol_in_mdf["Crop_yield_last_year"]
    idx2 = fcol_in_mdf["Crop_yield_with_soil_quality_CO2_and_env_dam_effects"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / One_year * dt
      )

    # Desired_crop_yield[region] = Crop_yield_last_year[region] * ( 1 + Ratio_of_demand_to_regional_supply_of_crops[region] * Fraction_of_supply_imbalance_to_be_closed_by_yield_adjustment[region] )
    idxlhs = fcol_in_mdf["Desired_crop_yield"]
    idx1 = fcol_in_mdf["Crop_yield_last_year"]
    idx2 = fcol_in_mdf["Ratio_of_demand_to_regional_supply_of_crops"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (
        1
        + mdf[rowi, idx2 + j]
        * Fraction_of_supply_imbalance_to_be_closed_by_yield_adjustment[j]
      )

    # Nitrogen_use_AF = Nitrogen_use_AF_L / ( 1 + math.exp ( - Nitrogen_use_AF_k * ( Desired_crop_yield[af] / UNIT_conv_to_make_N_use_dmnl - Nitrogen_use_AF_x0 ) ) )
    idxlhs = fcol_in_mdf["Nitrogen_use_AF"]
    idx1 = fcol_in_mdf["Desired_crop_yield"]
    mdf[rowi, idxlhs] = Nitrogen_use_AF_L / (
      1
      + math.exp(
        -Nitrogen_use_AF_k
        * (mdf[rowi, idx1 + 1] / UNIT_conv_to_make_N_use_dmnl - Nitrogen_use_AF_x0)
      )
    )

    # Nitrogen_use_CN = Nitrogen_use_CN_b * LN ( Desired_crop_yield[cn] / UNIT_conv_to_make_N_use_dmnl ) - Nitrogen_use_CN_a
    idxlhs = fcol_in_mdf["Nitrogen_use_CN"]
    idx1 = fcol_in_mdf["Desired_crop_yield"]
    mdf[rowi, idxlhs] = (
      Nitrogen_use_CN_b * math.log(mdf[rowi, idx1 + 2] / UNIT_conv_to_make_N_use_dmnl)
      - Nitrogen_use_CN_a
    )

    # Nitrogen_use_SA = ( Nitrogen_use_SA_a * LN ( GDPpp_USED[sa] * UNIT_conv_to_make_exp_dmnl ) + Nitrogen_use_SA_b )
    idxlhs = fcol_in_mdf["Nitrogen_use_SA"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      Nitrogen_use_SA_a * math.log(mdf[rowi, idx1 + 4] * UNIT_conv_to_make_exp_dmnl)
      + Nitrogen_use_SA_b
    )

    # Nitrogen_use_rest[region] = Nitrogen_use_rest_L[region] / ( 1 + math.exp ( - Nitrogen_use_rest_k[region] * ( GDPpp_USED[region] - Nitrogen_use_rest_x0[region] ) ) )
    idxlhs = fcol_in_mdf["Nitrogen_use_rest"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Nitrogen_use_rest_L[j] / (
        1
        + math.exp(
          -Nitrogen_use_rest_k[j] * (mdf[rowi, idx1 + j] - Nitrogen_use_rest_x0[j])
        )
      )

    # Nitrogen_use[region] = IF_THEN_ELSE ( j==1 , Nitrogen_use_AF , IF_THEN_ELSE ( j==2 , Nitrogen_use_CN , IF_THEN_ELSE ( j==4 , Nitrogen_use_SA , Nitrogen_use_rest ) ) )
    idxlhs = fcol_in_mdf["Nitrogen_use"]
    idx1 = fcol_in_mdf["Nitrogen_use_AF"]
    idx2 = fcol_in_mdf["Nitrogen_use_CN"]
    idx3 = fcol_in_mdf["Nitrogen_use_SA"]
    idx4 = fcol_in_mdf["Nitrogen_use_rest"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 1,     mdf[rowi, idx1],     IF_THEN_ELSE(
          j == 2,       mdf[rowi, idx2],       IF_THEN_ELSE(j == 4, mdf[rowi, idx3], mdf[rowi, idx4 + j]),     ),   )

    # Nitrogen_use_after_soil_regeneration[region] = Nitrogen_use[region] * ( 1 - Regenerative_cropland_fraction[region] * Fraction_of_N_use_saved_through_regenerative_practice[region] )
    idxlhs = fcol_in_mdf["Nitrogen_use_after_soil_regeneration"]
    idx1 = fcol_in_mdf["Nitrogen_use"]
    idx2 = fcol_in_mdf["Regenerative_cropland_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (
        1 - mdf[rowi, idx2 + j] * Fraction_of_N_use_saved_through_regenerative_practice
      )

    # Addition_to_N_use_over_the_years[region] = IF_THEN_ELSE ( zeit > 2022 , Nitrogen_use_after_soil_regeneration * UNIT_conv_kgN_to_Nt , 0 )
    idxlhs = fcol_in_mdf["Addition_to_N_use_over_the_years"]
    idx1 = fcol_in_mdf["Nitrogen_use_after_soil_regeneration"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit > 2022, mdf[rowi, idx1 + j] * UNIT_conv_kgN_to_Nt, 0
      )

    # Effect_of_GDPpp_on_RoC_of_CLR[region] = 1 + SoE_of_GDPpp_on_RoC_of_CLR[region] * ( GDPpp_USED[region] / GDPpp_in_1980[region] - 1 )
    idxlhs = fcol_in_mdf["Effect_of_GDPpp_on_RoC_of_CLR"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + SoE_of_GDPpp_on_RoC_of_CLR[j] * (
        mdf[rowi, idx1 + j] / GDPpp_in_1980[j] - 1
      )

    # RoC_in_Capital_labour_ratio[region] = RoC_Capital_labour_ratio_in_1980[region] / Effect_of_GDPpp_on_RoC_of_CLR[region]
    idxlhs = fcol_in_mdf["RoC_in_Capital_labour_ratio"]
    idx1 = fcol_in_mdf["Effect_of_GDPpp_on_RoC_of_CLR"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = RoC_Capital_labour_ratio_in_1980[j] / mdf[rowi, idx1 + j]

    # Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio[region] = 1 + Slope_of_Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio * ( Worker_share_of_output_with_unemployment_effect[region] / WSO_in_1980[region] - 1 )
    idxlhs = fcol_in_mdf["Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio"
    ]
    idx1 = fcol_in_mdf["Worker_share_of_output_with_unemployment_effect"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + Slope_of_Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio
        * (mdf[rowi, idx1 + j] / WSO_in_1980[j] - 1)
      )

    # effect_of_worker_share_of_output_on_capital_labour_ratio[region] = SMOOTH ( Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio[region] , Retooling_time )
    idx1 = fcol_in_mdf["effect_of_worker_share_of_output_on_capital_labour_ratio"]
    idx2 = fcol_in_mdf["Indicated_effect_of_worker_share_of_output_on_capital_labour_ratio"
    ]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / Retooling_time * dt
      )

    # Capital_labour_ratio[region] = Capital_labour_ratio_in_1980[region] * math.exp ( RoC_in_Capital_labour_ratio[region] * ( zeit - 1980 ) ) * effect_of_worker_share_of_output_on_capital_labour_ratio[region]
    idxlhs = fcol_in_mdf["Capital_labour_ratio"]
    idx1 = fcol_in_mdf["RoC_in_Capital_labour_ratio"]
    idx2 = fcol_in_mdf["effect_of_worker_share_of_output_on_capital_labour_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Capital_labour_ratio_in_1980[j]
        * math.exp(mdf[rowi, idx1 + j] * (zeit - 1980))
        * mdf[rowi, idx2 + j]
      )

    # Theoretical_full_time_jobs_at_current_CLR[region] = ( Capacity[region] / Capital_labour_ratio[region] ) * UNIT_conv_to_Mp
    idxlhs = fcol_in_mdf["Theoretical_full_time_jobs_at_current_CLR"]
    idx1 = fcol_in_mdf["Capacity"]
    idx2 = fcol_in_mdf["Capital_labour_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]
      ) * UNIT_conv_to_Mp

    # Max_people_in_labour_pool[region] = Population[region] * ( 1 - Fraction_of_people_outside_of_labour_market_FOPOLM[region] )
    idxlhs = fcol_in_mdf["Max_people_in_labour_pool"]
    idx1 = fcol_in_mdf["Population"]
    idx2 = fcol_in_mdf["Fraction_of_people_outside_of_labour_market_FOPOLM"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # Full_time_jobs_with_participation_constraint[region] = MIN ( Theoretical_full_time_jobs_at_current_CLR[region] , Max_people_in_labour_pool[region] )
    idxlhs = fcol_in_mdf["Full_time_jobs_with_participation_constraint"]
    idx1 = fcol_in_mdf["Theoretical_full_time_jobs_at_current_CLR"]
    idx2 = fcol_in_mdf["Max_people_in_labour_pool"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(mdf[rowi, idx1 + j], mdf[rowi, idx2 + j])

    # Additional_people_required[region] = MAX ( 0 , Full_time_jobs_with_participation_constraint[region] - Employed[region] )
    idxlhs = fcol_in_mdf["Additional_people_required"]
    idx1 = fcol_in_mdf["Full_time_jobs_with_participation_constraint"]
    idx2 = fcol_in_mdf["Employed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])

    # Future_shape_of_anthropogenic_aerosol_emissions = WITH LOOKUP ( zeit , ( [ ( 2015 , 0 ) - ( 2100 , 1 ) ] , ( 2015 , 1 ) , ( 2030 , 0.7 ) , ( 2050 , 0.5 ) , ( 2075 , 0.3 ) , ( 2100 , 0.1 ) ) )
    tabidx = ftab_in_d_table[  "Future_shape_of_anthropogenic_aerosol_emissions"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Future_shape_of_anthropogenic_aerosol_emissions"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Historical_aerosol_emissions_anthro = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.24244 ) , ( 1981 , 0.252631 ) , ( 1982 , 0.255142 ) , ( 1983 , 0.258769 ) , ( 1984 , 0.262684 ) , ( 1985 , 0.264687 ) , ( 1986 , 0.267037 ) , ( 1987 , 0.270969 ) , ( 1988 , 0.274536 ) , ( 1989 , 0.276449 ) , ( 1990 , 0.277538 ) , ( 1991 , 0.276088 ) , ( 1992 , 0.275472 ) , ( 1993 , 0.274971 ) , ( 1994 , 0.272579 ) , ( 1995 , 0.267623 ) , ( 1996 , 0.261881 ) , ( 1997 , 0.264898 ) , ( 1998 , 0.274336 ) , ( 1999 , 0.281674 ) , ( 2000 , 0.2881 ) , ( 2001 , 0.291714 ) , ( 2002 , 0.291645 ) , ( 2003 , 0.292187 ) , ( 2004 , 0.293088 ) , ( 2005 , 0.292335 ) , ( 2006 , 0.288602 ) , ( 2007 , 0.283524 ) , ( 2008 , 0.278418 ) , ( 2009 , 0.273299 ) , ( 2010 , 0.267428 ) , ( 2011 , 0.260052 ) , ( 2012 , 0.251923 ) , ( 2013 , 0.243794 ) , ( 2014 , 0.235665 ) , ( 2015 , 0.227536 ) ) )
    tabidx = ftab_in_d_table[  "Historical_aerosol_emissions_anthro"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Historical_aerosol_emissions_anthro"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Aerosol_anthropogenic_emissions = IF_THEN_ELSE ( zeit >= 2015 , Future_shape_of_anthropogenic_aerosol_emissions * Value_of_anthropogenic_aerosol_emissions_during_2015 , Historical_aerosol_emissions_anthro )
    idxlhs = fcol_in_mdf["Aerosol_anthropogenic_emissions"]
    idx1 = fcol_in_mdf["Future_shape_of_anthropogenic_aerosol_emissions"]
    idx2 = fcol_in_mdf["Historical_aerosol_emissions_anthro"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit >= 2015,   mdf[rowi, idx1] * Value_of_anthropogenic_aerosol_emissions_during_2015,   mdf[rowi, idx2], )

    # Aging_14_to_15[region] = Cohort_10_to_14[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_14_to_15"]
    idx1 = fcol_in_mdf["Cohort_10_to_14"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_19_to_20[region] = Cohort_15_to_19[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_19_to_20"]
    idx1 = fcol_in_mdf["Cohort_15_to_19"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_24_to_25[region] = Cohort_20_to_24[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_24_to_25"]
    idx1 = fcol_in_mdf["Cohort_20_to_24"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_29_to_30[region] = Cohort_25_to_29[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_29_to_30"]
    idx1 = fcol_in_mdf["Cohort_25_to_29"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_34_to_35[region] = Cohort_30_to_34[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_34_to_35"]
    idx1 = fcol_in_mdf["Cohort_30_to_34"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_39_to_40[region] = Cohort_35_to_39[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_39_to_40"]
    idx1 = fcol_in_mdf["Cohort_35_to_39"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_4_to_5[region] = Cohort_0_to_4[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_4_to_5"]
    idx1 = fcol_in_mdf["Cohort_0_to_4"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_44_to_45[region] = Cohort_40_to_44[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_44_to_45"]
    idx1 = fcol_in_mdf["Cohort_40_to_44"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_49_to_50[region] = Cohort_45_to_49[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_49_to_50"]
    idx1 = fcol_in_mdf["Cohort_45_to_49"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_54_to_55[region] = Cohort_50_to_54[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_54_to_55"]
    idx1 = fcol_in_mdf["Cohort_50_to_54"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_59_to_60[region] = Cohort_55_to_59[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_59_to_60"]
    idx1 = fcol_in_mdf["Cohort_55_to_59"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_64_to_65[region] = Cohort_60_to_64[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_64_to_65"]
    idx1 = fcol_in_mdf["Cohort_60_to_64"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_69_to_70[region] = Cohort_65_to_69[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_69_to_70"]
    idx1 = fcol_in_mdf["Cohort_65_to_69"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_74_to_75[region] = Cohort_70_to_74[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_74_to_75"]
    idx1 = fcol_in_mdf["Cohort_70_to_74"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_79_to_80[region] = Cohort_75_to_79[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_79_to_80"]
    idx1 = fcol_in_mdf["Cohort_75_to_79"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_84_to_85[region] = Cohort_80_to_84[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_84_to_85"]
    idx1 = fcol_in_mdf["Cohort_80_to_84"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_89_to_90[region] = Cohort_85_to_89[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_89_to_90"]
    idx1 = fcol_in_mdf["Cohort_85_to_89"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_9_to_10[region] = Cohort_5_to_9[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_9_to_10"]
    idx1 = fcol_in_mdf["Cohort_5_to_9"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Aging_95_to_95plus[region] = Cohort_90_to_94[region] / Cohort_duration_is_5_yrs
    idxlhs = fcol_in_mdf["Aging_95_to_95plus"]
    idx1 = fcol_in_mdf["Cohort_90_to_94"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Cohort_duration_is_5_yrs

    # Smoothed_Urban_aerosol_concentration_future = SMOOTH3I ( Urban_aerosol_concentration_future , Time_to_smooth_UAC , Urban_aerosol_concentration_in_2020 )
    idxlhs = fcol_in_mdf["Smoothed_Urban_aerosol_concentration_future"]
    idxin = fcol_in_mdf["Urban_aerosol_concentration_future"]
    idx2 = fcol_in_mdf["Smoothed_Urban_aerosol_concentration_future_2"]
    idx1 = fcol_in_mdf["Smoothed_Urban_aerosol_concentration_future_1"]
    idxout = fcol_in_mdf["Smoothed_Urban_aerosol_concentration_future"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idxin] - mdf[rowi - 1, idx1]) / (Time_to_smooth_UAC / 3) * dt
    )
    mdf[rowi, idx2] = (
      mdf[rowi - 1, idx2]
      + (mdf[rowi - 1, idx1] - mdf[rowi - 1, idx2]) / (Time_to_smooth_UAC / 3) * dt
    )
    mdf[rowi, idxout] = (
      mdf[rowi - 1, idxout]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idxout]) / (Time_to_smooth_UAC / 3) * dt
    )

    # Air_Pollution_risk_score = IF_THEN_ELSE ( Smoothed_Urban_aerosol_concentration_future > pb_Urban_aerosol_concentration_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Air_Pollution_risk_score"]
    idx1 = fcol_in_mdf["Smoothed_Urban_aerosol_concentration_future"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > pb_Urban_aerosol_concentration_green_threshold, 1, 0
    )

    # Albedo_Antartic = IF_THEN_ELSE ( zeit > 2020 , Albedo_Antarctic_sens , Albedo_Antarctic_hist )
    idxlhs = fcol_in_mdf["Albedo_Antartic"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 2020, Albedo_Antarctic_sens, Albedo_Antarctic_hist
    )

    # Albedo_glacier = IF_THEN_ELSE ( zeit > 2020 , Albedo_glacier_sens , Albedo_glacier_hist )
    idxlhs = fcol_in_mdf["Albedo_glacier"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 2020, Albedo_glacier_sens, Albedo_glacier_hist
    )

    # Urban_area_fraction = MAX ( 0 , MIN ( 1 , Global_population_in_Bp / Population_2000_bn * Urban_area_fraction_2000 ) )
    idxlhs = fcol_in_mdf["Urban_area_fraction"]
    idx1 = fcol_in_mdf["Global_population_in_Bp"]
    mdf[rowi, idxlhs] = max(
      0, min(1, mdf[rowi, idx1] / Population_2000_bn * Urban_area_fraction_2000)
    )

    # Urban_Mkm2 = Area_of_earth_Mkm2 * ( 1 - Fraction_of_earth_surface_as_ocean ) * Urban_area_fraction
    idxlhs = fcol_in_mdf["Urban_Mkm2"]
    idx1 = fcol_in_mdf["Urban_area_fraction"]
    mdf[rowi, idxlhs] = (
      Area_of_earth_Mkm2 * (1 - Fraction_of_earth_surface_as_ocean) * mdf[rowi, idx1]
    )

    # Avg_thickness_Antarctic_km = IF_THEN_ELSE ( zeit > 2020 , Avg_thickness_Antarctic_sens_km , Avg_thickness_Antarctic_hist_km )
    idxlhs = fcol_in_mdf["Avg_thickness_Antarctic_km"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 2020, Avg_thickness_Antarctic_sens_km, Avg_thickness_Antarctic_hist_km
    )

    # Antarctic_ice_area_km2 = Antarctic_ice_volume_km3 / Avg_thickness_Antarctic_km * UNIT_Conversion_from_km3_to_km2
    idxlhs = fcol_in_mdf["Antarctic_ice_area_km2"]
    idx1 = fcol_in_mdf["Antarctic_ice_volume_km3"]
    idx2 = fcol_in_mdf["Avg_thickness_Antarctic_km"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / mdf[rowi, idx2] * UNIT_Conversion_from_km3_to_km2
    )

    # Glacial_ice_area_km2 = Glacial_ice_volume_km3 / Avg_thickness_glacier_km * UNIT_conversion_km3_div_km_to_km2
    idxlhs = fcol_in_mdf["Glacial_ice_area_km2"]
    idx1 = fcol_in_mdf["Glacial_ice_volume_km3"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Avg_thickness_glacier_km * UNIT_conversion_km3_div_km_to_km2
    )

    # Greenland_ice_area_km2 = ( Greenland_ice_volume_on_Greenland_km3 / Avg_thickness_Greenland_km ) * UNIT_Conversion_from_km3_to_km2
    idxlhs = fcol_in_mdf["Greenland_ice_area_km2"]
    idx1 = fcol_in_mdf["Greenland_ice_volume_on_Greenland_km3"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Avg_thickness_Greenland_km
    ) * UNIT_Conversion_from_km3_to_km2

    # Land_covered_with_ice_km2 = Antarctic_ice_area_km2 + Glacial_ice_area_km2 + Greenland_ice_area_km2
    idxlhs = fcol_in_mdf["Land_covered_with_ice_km2"]
    idx1 = fcol_in_mdf["Antarctic_ice_area_km2"]
    idx2 = fcol_in_mdf["Glacial_ice_area_km2"]
    idx3 = fcol_in_mdf["Greenland_ice_area_km2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Sum_biomes_Mkm2 = Land_covered_with_ice_km2 * UNIT_conversion_km2_to_Mkm2 + Tundra_potential_area_Mkm2 + NF_potential_area_Mkm2 + DESERT_Mkm2 + GRASS_potential_area_Mkm2 + TROP_potential_area_Mkm2
    idxlhs = fcol_in_mdf["Sum_biomes_Mkm2"]
    idx1 = fcol_in_mdf["Land_covered_with_ice_km2"]
    idx2 = fcol_in_mdf["Tundra_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx4 = fcol_in_mdf["DESERT_Mkm2"]
    idx5 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx6 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * UNIT_conversion_km2_to_Mkm2
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
    )

    # Barren_land_Mkm2 = Area_of_earth_Mkm2 * ( 1 - Fraction_of_earth_surface_as_ocean ) - Urban_Mkm2 - Sum_biomes_Mkm2
    idxlhs = fcol_in_mdf["Barren_land_Mkm2"]
    idx1 = fcol_in_mdf["Urban_Mkm2"]
    idx2 = fcol_in_mdf["Sum_biomes_Mkm2"]
    mdf[rowi, idxlhs] = (
      Area_of_earth_Mkm2 * (1 - Fraction_of_earth_surface_as_ocean)
      - mdf[rowi, idx1]
      - mdf[rowi, idx2]
    )

    # BARREN_land_normal_albedo_Mkm2 = Barren_land_Mkm2
    idxlhs = fcol_in_mdf["BARREN_land_normal_albedo_Mkm2"]
    idx1 = fcol_in_mdf["Barren_land_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Contrib_of_BARREN_land_to_albedo_land = BARREN_land_normal_albedo_Mkm2 / Area_of_land_Mkm2 * Albedo_BARREN_normal
    idxlhs = fcol_in_mdf["Contrib_of_BARREN_land_to_albedo_land"]
    idx1 = fcol_in_mdf["BARREN_land_normal_albedo_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Area_of_land_Mkm2 * Albedo_BARREN_normal

    # Contrib_of_GRASS_to_albedo_land = ( GRASS_potential_area_Mkm2 - GRASS_area_burnt_Mkm2 - GRASS_deforested_Mkm2 ) / Area_of_land_Mkm2 * Albedo_GRASS_normal_cover + GRASS_area_burnt_Mkm2 / Area_of_land_Mkm2 * Albedo_GRASS_burnt + GRASS_deforested_Mkm2 / Area_of_land_Mkm2 * Albedo_GRASS_deforested
    idxlhs = fcol_in_mdf["Contrib_of_GRASS_to_albedo_land"]
    idx1 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["GRASS_area_burnt_Mkm2"]
    idx3 = fcol_in_mdf["GRASS_deforested_Mkm2"]
    idx4 = fcol_in_mdf["GRASS_area_burnt_Mkm2"]
    idx5 = fcol_in_mdf["GRASS_deforested_Mkm2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3])
      / Area_of_land_Mkm2
      * Albedo_GRASS_normal_cover
      + mdf[rowi, idx4] / Area_of_land_Mkm2 * Albedo_GRASS_burnt
      + mdf[rowi, idx5] / Area_of_land_Mkm2 * Albedo_GRASS_deforested
    )

    # Contrib_of_ICE_ON_LAND_to_albedo_land = Antarctic_ice_area_km2 * Conversion_Million_km2_to_km2 / Area_of_land_Mkm2 * Albedo_Antartic + Glacial_ice_area_km2 * Conversion_Million_km2_to_km2 / Area_of_land_Mkm2 * Albedo_glacier + Greenland_ice_area_km2 * Conversion_Million_km2_to_km2 / Area_of_land_Mkm2 * Albedo_Greenland
    idxlhs = fcol_in_mdf["Contrib_of_ICE_ON_LAND_to_albedo_land"]
    idx1 = fcol_in_mdf["Antarctic_ice_area_km2"]
    idx2 = fcol_in_mdf["Albedo_Antartic"]
    idx3 = fcol_in_mdf["Glacial_ice_area_km2"]
    idx4 = fcol_in_mdf["Albedo_glacier"]
    idx5 = fcol_in_mdf["Greenland_ice_area_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * Conversion_Million_km2_to_km2
      / Area_of_land_Mkm2
      * mdf[rowi, idx2]
      + mdf[rowi, idx3]
      * Conversion_Million_km2_to_km2
      / Area_of_land_Mkm2
      * mdf[rowi, idx4]
      + mdf[rowi, idx5]
      * Conversion_Million_km2_to_km2
      / Area_of_land_Mkm2
      * Albedo_Greenland
    )

    # Contrib_of_NF_to_albedo_land = ( NF_potential_area_Mkm2 - NF_area_burnt_Mkm2 - NF_area_deforested_Mkm2 - NF_area_clear_cut_Mkm2 ) / Area_of_land_Mkm2 * Albedo_NF_normal_cover + NF_area_burnt_Mkm2 / Area_of_land_Mkm2 * Albedo_NF_burnt + NF_area_deforested_Mkm2 / Area_of_land_Mkm2 * Albedo_NF_deforested + NF_area_clear_cut_Mkm2 / Area_of_land_Mkm2 * Albedo_NF_deforested
    idxlhs = fcol_in_mdf["Contrib_of_NF_to_albedo_land"]
    idx1 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["NF_area_burnt_Mkm2"]
    idx3 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    idx4 = fcol_in_mdf["NF_area_clear_cut_Mkm2"]
    idx5 = fcol_in_mdf["NF_area_burnt_Mkm2"]
    idx6 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    idx7 = fcol_in_mdf["NF_area_clear_cut_Mkm2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4])
      / Area_of_land_Mkm2
      * Albedo_NF_normal_cover
      + mdf[rowi, idx5] / Area_of_land_Mkm2 * Albedo_NF_burnt
      + mdf[rowi, idx6] / Area_of_land_Mkm2 * Albedo_NF_deforested
      + mdf[rowi, idx7] / Area_of_land_Mkm2 * Albedo_NF_deforested
    )

    # Contrib_of_TROP_to_albedo_land = ( TROP_potential_area_Mkm2 - TROP_area_burnt - TROP_area_deforested ) / Area_of_land_Mkm2 * Albedo_TROP_normal_cover + TROP_area_burnt / Area_of_land_Mkm2 * Albedo_TROP_burnt + TROP_area_deforested / Area_of_land_Mkm2 * Albedo_TROP_deforested + TROP_area_clear_cut / Area_of_land_Mkm2 * Albedo_TROP_deforested
    idxlhs = fcol_in_mdf["Contrib_of_TROP_to_albedo_land"]
    idx1 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["TROP_area_burnt"]
    idx3 = fcol_in_mdf["TROP_area_deforested"]
    idx4 = fcol_in_mdf["TROP_area_burnt"]
    idx5 = fcol_in_mdf["TROP_area_deforested"]
    idx6 = fcol_in_mdf["TROP_area_clear_cut"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3])
      / Area_of_land_Mkm2
      * Albedo_TROP_normal_cover
      + mdf[rowi, idx4] / Area_of_land_Mkm2 * Albedo_TROP_burnt
      + mdf[rowi, idx5] / Area_of_land_Mkm2 * Albedo_TROP_deforested
      + mdf[rowi, idx6] / Area_of_land_Mkm2 * Albedo_TROP_deforested
    )

    # Contrib_of_TUNDRA_to_albedo_land = ( Tundra_potential_area_Mkm2 - TUNDRA_area_burnt_Mkm2 - TUNDRA_deforested_Mkm2 ) / Area_of_land_Mkm2 * Albedo_TUNDRA_normal_cover + TUNDRA_area_burnt_Mkm2 / Area_of_land_Mkm2 * Albedo_TUNDRA_burnt + TUNDRA_deforested_Mkm2 / Area_of_land_Mkm2 * Albedo_TUNDRA_deforested
    idxlhs = fcol_in_mdf["Contrib_of_TUNDRA_to_albedo_land"]
    idx1 = fcol_in_mdf["Tundra_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["TUNDRA_area_burnt_Mkm2"]
    idx3 = fcol_in_mdf["TUNDRA_deforested_Mkm2"]
    idx4 = fcol_in_mdf["TUNDRA_area_burnt_Mkm2"]
    idx5 = fcol_in_mdf["TUNDRA_deforested_Mkm2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3])
      / Area_of_land_Mkm2
      * Albedo_TUNDRA_normal_cover
      + mdf[rowi, idx4] / Area_of_land_Mkm2 * Albedo_TUNDRA_burnt
      + mdf[rowi, idx5] / Area_of_land_Mkm2 * Albedo_TUNDRA_deforested
    )

    # Albedo_land_biomes = Contrib_of_BARREN_land_to_albedo_land + Albedo_DESERT_normal * DESERT_Mkm2 / Area_of_land_Mkm2 + Contrib_of_GRASS_to_albedo_land + Contrib_of_ICE_ON_LAND_to_albedo_land + Contrib_of_NF_to_albedo_land + Contrib_of_TROP_to_albedo_land + Contrib_of_TUNDRA_to_albedo_land + Albedo_URBAN * Urban_Mkm2 / Area_of_land_Mkm2
    idxlhs = fcol_in_mdf["Albedo_land_biomes"]
    idx1 = fcol_in_mdf["Contrib_of_BARREN_land_to_albedo_land"]
    idx2 = fcol_in_mdf["DESERT_Mkm2"]
    idx3 = fcol_in_mdf["Contrib_of_GRASS_to_albedo_land"]
    idx4 = fcol_in_mdf["Contrib_of_ICE_ON_LAND_to_albedo_land"]
    idx5 = fcol_in_mdf["Contrib_of_NF_to_albedo_land"]
    idx6 = fcol_in_mdf["Contrib_of_TROP_to_albedo_land"]
    idx7 = fcol_in_mdf["Contrib_of_TUNDRA_to_albedo_land"]
    idx8 = fcol_in_mdf["Urban_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + Albedo_DESERT_normal * mdf[rowi, idx2] / Area_of_land_Mkm2
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
      + mdf[rowi, idx7]
      + Albedo_URBAN * mdf[rowi, idx8] / Area_of_land_Mkm2
    )

    # Arctic_as_fraction_of_ocean = Arctic_ice_on_sea_area_km2 / Ocean_area_km2
    idxlhs = fcol_in_mdf["Arctic_as_fraction_of_ocean"]
    idx1 = fcol_in_mdf["Arctic_ice_on_sea_area_km2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Ocean_area_km2

    # Open_water_as_frac_of_ocean_area = 1 - ( Arctic_ice_on_sea_area_km2 / Ocean_area_km2 )
    idxlhs = fcol_in_mdf["Open_water_as_frac_of_ocean_area"]
    idx1 = fcol_in_mdf["Arctic_ice_on_sea_area_km2"]
    mdf[rowi, idxlhs] = 1 - (mdf[rowi, idx1] / Ocean_area_km2)

    # Albedo_ocean_with_arctic_ice_changes = Arctic_ice_albedo_1850 * Arctic_as_fraction_of_ocean + Open_ocean_albedo * Open_water_as_frac_of_ocean_area
    idxlhs = fcol_in_mdf["Albedo_ocean_with_arctic_ice_changes"]
    idx1 = fcol_in_mdf["Arctic_as_fraction_of_ocean"]
    idx2 = fcol_in_mdf["Open_water_as_frac_of_ocean_area"]
    mdf[rowi, idxlhs] = (
      Arctic_ice_albedo_1850 * mdf[rowi, idx1] + Open_ocean_albedo * mdf[rowi, idx2]
    )

    # LW_HI_cloud_radiation_W_p_m2 = LW_HI_cloud_radiation / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["LW_HI_cloud_radiation_W_p_m2"]
    idx1 = fcol_in_mdf["LW_HI_cloud_radiation"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # Solar_sine_forcing_W_p_m2 = math.sin ( 2 * 3.14 * ( zeit - Solar_sine_forcing_offset_yr ) / Solar_sine_forcing_period_yr ) * ( Solar_sine_forcing_amplitude ) + Solar_sine_forcing_lift
    idxlhs = fcol_in_mdf["Solar_sine_forcing_W_p_m2"]
    mdf[rowi, idxlhs] = (
      math.sin(
        2 * 3.14 * (zeit - Solar_sine_forcing_offset_yr) / Solar_sine_forcing_period_yr
      )
      * (Solar_sine_forcing_amplitude)
      + Solar_sine_forcing_lift
    )

    # Historical_forcing_from_solar_insolation_W_p_m2 = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.146265 ) , ( 1981 , 0.133052 ) , ( 1982 , 0.0955062 ) , ( 1983 , 0.0530031 ) , ( 1984 , 0.00780063 ) , ( 1985 , - 0.0241369 ) , ( 1986 , - 0.0251912 ) , ( 1987 , 0.0007525 ) , ( 1988 , 0.0577456 ) , ( 1989 , 0.115876 ) , ( 1990 , 0.127623 ) , ( 1991 , 0.107787 ) , ( 1992 , 0.0785487 ) , ( 1993 , 0.0382069 ) , ( 1994 , 0.00171938 ) , ( 1995 , - 0.0207681 ) , ( 1996 , - 0.0270988 ) , ( 1997 , - 0.00389812 ) , ( 1998 , 0.0457669 ) , ( 1999 , 0.099435 ) , ( 2000 , 0.134374 ) , ( 2001 , 0.143745 ) , ( 2002 , 0.127334 ) , ( 2003 , 0.08337 ) , ( 2004 , 0.0392613 ) , ( 2005 , 0.0124513 ) , ( 2006 , - 0.00364 ) , ( 2007 , - 0.0145513 ) , ( 2008 , - 0.0211619 ) , ( 2009 , 0.0257119 ) , ( 2010 , 0.099435 ) , ( 2011 , 0.134374 ) , ( 2012 , 0.15 ) , ( 2013 , 0.12 ) , ( 2014 , 0 ) , ( 2015 , - 0.02 ) , ( 2016 , - 0.03 ) , ( 2017 , - 0.02 ) , ( 2018 , 0 ) , ( 2019 , 0.1 ) , ( 2020 , 0.15 ) ) )
    tabidx = ftab_in_d_table[  "Historical_forcing_from_solar_insolation_W_p_m2"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Historical_forcing_from_solar_insolation_W_p_m2"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Solar_cycle_W_p_m2 = IF_THEN_ELSE ( zeit > 2019 , Solar_sine_forcing_W_p_m2 , Historical_forcing_from_solar_insolation_W_p_m2 )
    idxlhs = fcol_in_mdf["Solar_cycle_W_p_m2"]
    idx1 = fcol_in_mdf["Solar_sine_forcing_W_p_m2"]
    idx2 = fcol_in_mdf["Historical_forcing_from_solar_insolation_W_p_m2"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit > 2019, mdf[rowi, idx1], mdf[rowi, idx2])

    # Incoming_solar_W_p_m2 = 340 + Solar_cycle_W_p_m2
    idxlhs = fcol_in_mdf["Incoming_solar_W_p_m2"]
    idx1 = fcol_in_mdf["Solar_cycle_W_p_m2"]
    mdf[rowi, idxlhs] = 340 + mdf[rowi, idx1]

    # Incoming_solar_ZJ_py = Incoming_solar_W_p_m2 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["Incoming_solar_ZJ_py"]
    idx1 = fcol_in_mdf["Incoming_solar_W_p_m2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # SW_HI_cloud_efffect_aka_cloud_albedo = Incoming_solar_ZJ_py * Frac_SW_HI_cloud_efffect_aka_cloud_albedo * Ratio_of_area_covered_by_high_clouds_current_to_init
    idxlhs = fcol_in_mdf["SW_HI_cloud_efffect_aka_cloud_albedo"]
    idx1 = fcol_in_mdf["Incoming_solar_ZJ_py"]
    idx2 = fcol_in_mdf["Ratio_of_area_covered_by_high_clouds_current_to_init"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Frac_SW_HI_cloud_efffect_aka_cloud_albedo * mdf[rowi, idx2]
    )

    # SW_HI_cloud_efffect_aka_TOA_albedo_W_p_m2 = SW_HI_cloud_efffect_aka_cloud_albedo / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["SW_HI_cloud_efffect_aka_TOA_albedo_W_p_m2"]
    idx1 = fcol_in_mdf["SW_HI_cloud_efffect_aka_cloud_albedo"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # HI_clouds_net_effect_pos_is_warming_neg_is_cooling_W_p_m2 = LW_HI_cloud_radiation_W_p_m2 - SW_HI_cloud_efffect_aka_TOA_albedo_W_p_m2
    idxlhs = fcol_in_mdf["HI_clouds_net_effect_pos_is_warming_neg_is_cooling_W_p_m2"]
    idx1 = fcol_in_mdf["LW_HI_cloud_radiation_W_p_m2"]
    idx2 = fcol_in_mdf["SW_HI_cloud_efffect_aka_TOA_albedo_W_p_m2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # LW_LO_cloud_radiation_W_p_m2 = LW_LO_cloud_radiation / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["LW_LO_cloud_radiation_W_p_m2"]
    idx1 = fcol_in_mdf["LW_LO_cloud_radiation"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # SW_LO_cloud_efffect_aka_cloud_albedo = Incoming_solar_ZJ_py * Frac_SW_LO_cloud_efffect_aka_cloud_albedo * Ratio_of_area_covered_by_low_clouds_current_to_init
    idxlhs = fcol_in_mdf["SW_LO_cloud_efffect_aka_cloud_albedo"]
    idx1 = fcol_in_mdf["Incoming_solar_ZJ_py"]
    idx2 = fcol_in_mdf["Ratio_of_area_covered_by_low_clouds_current_to_init"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Frac_SW_LO_cloud_efffect_aka_cloud_albedo * mdf[rowi, idx2]
    )

    # SW_LO_cloud_efffect_aka_cloud_albedo_W_p_m2 = SW_LO_cloud_efffect_aka_cloud_albedo / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["SW_LO_cloud_efffect_aka_cloud_albedo_W_p_m2"]
    idx1 = fcol_in_mdf["SW_LO_cloud_efffect_aka_cloud_albedo"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # LO_clouds_net_effect_pos_is_warming_neg_is_cooling_W_p_m2 = LW_LO_cloud_radiation_W_p_m2 - SW_LO_cloud_efffect_aka_cloud_albedo_W_p_m2
    idxlhs = fcol_in_mdf["LO_clouds_net_effect_pos_is_warming_neg_is_cooling_W_p_m2"]
    idx1 = fcol_in_mdf["LW_LO_cloud_radiation_W_p_m2"]
    idx2 = fcol_in_mdf["SW_LO_cloud_efffect_aka_cloud_albedo_W_p_m2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # all_crop_not_wasted_pp[region] = ( cereal_dmd_food_pp_consumed[region] + oth_crop_dmd_food_pp_consumed[region] ) * UNIT_conv_kgac_to_kg
    idxlhs = fcol_in_mdf["all_crop_not_wasted_pp"]
    idx1 = fcol_in_mdf["cereal_dmd_food_pp_consumed"]
    idx2 = fcol_in_mdf["oth_crop_dmd_food_pp_consumed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]
      ) * UNIT_conv_kgac_to_kg

    # Emissions_of_anthro_CO2_from_Excel_SSP245spliced_to_PRIMAP_history_GtC_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 5.60338 ) , ( 1981 , 5.43663 ) , ( 1982 , 5.3609 ) , ( 1983 , 5.41261 ) , ( 1984 , 5.58317 ) , ( 1985 , 5.77454 ) , ( 1986 , 5.82824 ) , ( 1987 , 5.976 ) , ( 1988 , 6.21619 ) , ( 1989 , 6.30073 ) , ( 1990 , 6.16508 ) , ( 1991 , 6.29272 ) , ( 1992 , 6.10415 ) , ( 1993 , 6.15783 ) , ( 1994 , 6.20212 ) , ( 1995 , 6.35632 ) , ( 1996 , 6.54807 ) , ( 1997 , 6.55936 ) , ( 1998 , 6.55426 ) , ( 1999 , 6.61756 ) , ( 2000 , 6.80252 ) , ( 2001 , 6.86167 ) , ( 2002 , 7.01497 ) , ( 2003 , 7.37669 ) , ( 2004 , 7.68727 ) , ( 2005 , 7.95053 ) , ( 2006 , 8.18815 ) , ( 2007 , 8.44511 ) , ( 2008 , 8.5821 ) , ( 2009 , 8.4779 ) , ( 2010 , 8.92064 ) , ( 2011 , 9.21049 ) , ( 2012 , 9.38678 ) , ( 2013 , 9.46723 ) , ( 2014 , 9.60763 ) , ( 2015 , 9.58832 ) , ( 2016 , 9.54482 ) , ( 2017 , 9.66788 ) , ( 2018 , 9.83454 ) , ( 2019 , 9.86017 ) , ( 2020 , 10.1967 ) , ( 2021 , 10.2841 ) , ( 2022 , 10.3716 ) , ( 2023 , 10.459 ) , ( 2024 , 10.5465 ) , ( 2025 , 10.6339 ) , ( 2026 , 10.7214 ) , ( 2027 , 10.8088 ) , ( 2028 , 10.8963 ) , ( 2029 , 10.9837 ) , ( 2030 , 11.0712 ) , ( 2031 , 11.1119 ) , ( 2032 , 11.1527 ) , ( 2033 , 11.1934 ) , ( 2034 , 11.2341 ) , ( 2035 , 11.2749 ) , ( 2036 , 11.3156 ) , ( 2037 , 11.3564 ) , ( 2038 , 11.3971 ) , ( 2039 , 11.4379 ) , ( 2040 , 11.4786 ) , ( 2041 , 11.5024 ) , ( 2042 , 11.5262 ) , ( 2043 , 11.55 ) , ( 2044 , 11.5738 ) , ( 2045 , 11.5976 ) , ( 2046 , 11.6214 ) , ( 2047 , 11.6452 ) , ( 2048 , 11.669 ) , ( 2049 , 11.6928 ) , ( 2050 , 11.7166 ) , ( 2051 , 11.6832 ) , ( 2052 , 11.6498 ) , ( 2053 , 11.6164 ) , ( 2054 , 11.583 ) , ( 2055 , 11.5496 ) , ( 2056 , 11.5162 ) , ( 2057 , 11.4828 ) , ( 2058 , 11.4494 ) , ( 2059 , 11.416 ) , ( 2060 , 11.3826 ) , ( 2061 , 11.2656 ) , ( 2062 , 11.1486 ) , ( 2063 , 11.0316 ) , ( 2064 , 10.9146 ) , ( 2065 , 10.7976 ) , ( 2066 , 10.6806 ) , ( 2067 , 10.5636 ) , ( 2068 , 10.4466 ) , ( 2069 , 10.3296 ) , ( 2070 , 10.2126 ) , ( 2071 , 10.016 ) , ( 2072 , 9.8193 ) , ( 2073 , 9.62264 ) , ( 2074 , 9.42599 ) , ( 2075 , 9.22933 ) , ( 2076 , 9.03267 ) , ( 2077 , 8.83601 ) , ( 2078 , 8.63935 ) , ( 2079 , 8.44269 ) , ( 2080 , 8.24603 ) , ( 2081 , 7.98437 ) , ( 2082 , 7.72271 ) , ( 2083 , 7.46106 ) , ( 2084 , 7.1994 ) , ( 2085 , 6.93774 ) , ( 2086 , 6.67608 ) , ( 2087 , 6.41443 ) , ( 2088 , 6.15277 ) , ( 2089 , 5.89111 ) , ( 2090 , 5.62945 ) , ( 2091 , 5.46149 ) , ( 2092 , 5.29353 ) , ( 2093 , 5.12557 ) , ( 2094 , 4.95761 ) , ( 2095 , 4.78965 ) , ( 2096 , 4.62169 ) , ( 2097 , 4.45373 ) , ( 2098 , 4.28578 ) , ( 2099 , 4.11782 ) , ( 2100 , 3.94986 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_anthro_CO2_from_Excel_SSP245spliced_to_PRIMAP_history_GtC_py"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_anthro_CO2_from_Excel_SSP245spliced_to_PRIMAP_history_GtC_py"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Global_Total_CO2_emissions = SUM ( Total_CO2_emissions[region!] )
    idxlhs = fcol_in_mdf["Global_Total_CO2_emissions"]
    idx1 = fcol_in_mdf["Total_CO2_emissions"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_Total_CO2_emissions_GtC_py = Global_Total_CO2_emissions / UNIT_conv_CO2_to_C
    idxlhs = fcol_in_mdf["Global_Total_CO2_emissions_GtC_py"]
    idx1 = fcol_in_mdf["Global_Total_CO2_emissions"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conv_CO2_to_C

    # Emissions_of_CO2_1850_to_2100_GtC_py = IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2 , Emissions_of_anthro_CO2_from_Excel_SSP245spliced_to_PRIMAP_history_GtC_py , IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4 , Global_Total_CO2_emissions_GtC_py , 0 ) )
    idxlhs = fcol_in_mdf["Emissions_of_CO2_1850_to_2100_GtC_py"]
    idx1 = fcol_in_mdf["Emissions_of_anthro_CO2_from_Excel_SSP245spliced_to_PRIMAP_history_GtC_py"
    ]
    idx2 = fcol_in_mdf["Global_Total_CO2_emissions_GtC_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2,   mdf[rowi, idx1],   IF_THEN_ELSE(SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4, mdf[rowi, idx2], 0), )

    # Fossil_fuel_reserves_in_ground_current_to_inital_ratio = Fossil_fuel_reserves_in_ground_GtC / Fossil_fuel_reserves_in_ground_at_initial_time_GtC
    idxlhs = fcol_in_mdf["Fossil_fuel_reserves_in_ground_current_to_inital_ratio"]
    idx1 = fcol_in_mdf["Fossil_fuel_reserves_in_ground_GtC"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Fossil_fuel_reserves_in_ground_at_initial_time_GtC
    )

    # RCPFossil_fuel_usage_cutoff = WITH LOOKUP ( Fossil_fuel_reserves_in_ground_current_to_inital_ratio , ( [ ( 0 , 0 ) - ( 1 , 1 ) ] , ( 0 , 0 ) , ( 0.25 , 0.657895 ) , ( 0.5 , 0.881579 ) , ( 0.75 , 0.960526 ) , ( 1 , 1 ) ) )
    tabidx = ftab_in_d_table["RCPFossil_fuel_usage_cutoff"]  # fetch the correct table
    idxlhs = fcol_in_mdf["RCPFossil_fuel_usage_cutoff"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Fossil_fuel_reserves_in_ground_current_to_inital_ratio"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # CO2_emissions_before_co2e_exp = Emissions_of_CO2_1850_to_2100_GtC_py * RCPFossil_fuel_usage_cutoff
    idxlhs = fcol_in_mdf["CO2_emissions_before_co2e_exp"]
    idx1 = fcol_in_mdf["Emissions_of_CO2_1850_to_2100_GtC_py"]
    idx2 = fcol_in_mdf["RCPFossil_fuel_usage_cutoff"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Man_made_fossil_C_emissions_GtC_py = CO2_emissions_before_co2e_exp
    idxlhs = fcol_in_mdf["Man_made_fossil_C_emissions_GtC_py"]
    idx1 = fcol_in_mdf["CO2_emissions_before_co2e_exp"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Man_made_fossil_C_emissions_GtCO2e_py = Man_made_fossil_C_emissions_GtC_py / UNIT_conversion_for_CO2_from_CO2e_to_C
    idxlhs = fcol_in_mdf["Man_made_fossil_C_emissions_GtCO2e_py"]
    idx1 = fcol_in_mdf["Man_made_fossil_C_emissions_GtC_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_for_CO2_from_CO2e_to_C

    # Emissions_of_anthro_CH4_SSP245_spliced_to_history = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 233.235 ) , ( 1981 , 228.928 ) , ( 1982 , 230.782 ) , ( 1983 , 231.971 ) , ( 1984 , 233.703 ) , ( 1985 , 236.305 ) , ( 1986 , 240.002 ) , ( 1987 , 243.31 ) , ( 1988 , 247.82 ) , ( 1989 , 254.123 ) , ( 1990 , 256.328 ) , ( 1991 , 254.611 ) , ( 1992 , 255.501 ) , ( 1993 , 257.105 ) , ( 1994 , 257.418 ) , ( 1995 , 262.517 ) , ( 1996 , 267.218 ) , ( 1997 , 266.434 ) , ( 1998 , 266.436 ) , ( 1999 , 268.047 ) , ( 2000 , 273.769 ) , ( 2001 , 273.707 ) , ( 2002 , 271.651 ) , ( 2003 , 279.901 ) , ( 2004 , 285.262 ) , ( 2005 , 290.557 ) , ( 2006 , 292.285 ) , ( 2007 , 293.906 ) , ( 2008 , 297.35 ) , ( 2009 , 294.897 ) , ( 2010 , 300.664 ) , ( 2011 , 304.952 ) , ( 2012 , 308.152 ) , ( 2013 , 306.117 ) , ( 2014 , 305.444 ) , ( 2015 , 307.249 ) , ( 2016 , 309.868 ) , ( 2017 , 311.126 ) , ( 2018 , 313.209 ) , ( 2019 , 317.65 ) , ( 2020 , 311.82 ) , ( 2021 , 312.733 ) , ( 2022 , 313.645 ) , ( 2023 , 314.558 ) , ( 2024 , 315.47 ) , ( 2025 , 316.382 ) , ( 2026 , 317.295 ) , ( 2027 , 318.207 ) , ( 2028 , 319.12 ) , ( 2029 , 320.032 ) , ( 2030 , 320.944 ) , ( 2031 , 319.607 ) , ( 2032 , 318.269 ) , ( 2033 , 316.931 ) , ( 2034 , 315.593 ) , ( 2035 , 314.256 ) , ( 2036 , 312.918 ) , ( 2037 , 311.58 ) , ( 2038 , 310.242 ) , ( 2039 , 308.905 ) , ( 2040 , 307.567 ) , ( 2041 , 305.508 ) , ( 2042 , 303.448 ) , ( 2043 , 301.389 ) , ( 2044 , 299.33 ) , ( 2045 , 297.271 ) , ( 2046 , 295.211 ) , ( 2047 , 293.152 ) , ( 2048 , 291.093 ) , ( 2049 , 289.033 ) , ( 2050 , 286.974 ) , ( 2051 , 284.737 ) , ( 2052 , 282.499 ) , ( 2053 , 280.262 ) , ( 2054 , 278.025 ) , ( 2055 , 275.788 ) , ( 2056 , 273.55 ) , ( 2057 , 271.313 ) , ( 2058 , 269.076 ) , ( 2059 , 266.838 ) , ( 2060 , 264.601 ) , ( 2061 , 263.582 ) , ( 2062 , 262.563 ) , ( 2063 , 261.544 ) , ( 2064 , 260.525 ) , ( 2065 , 259.506 ) , ( 2066 , 258.487 ) , ( 2067 , 257.468 ) , ( 2068 , 256.449 ) , ( 2069 , 255.43 ) , ( 2070 , 254.411 ) , ( 2071 , 253.308 ) , ( 2072 , 252.204 ) , ( 2073 , 251.101 ) , ( 2074 , 249.998 ) , ( 2075 , 248.894 ) , ( 2076 , 247.791 ) , ( 2077 , 246.688 ) , ( 2078 , 245.585 ) , ( 2079 , 244.481 ) , ( 2080 , 243.378 ) , ( 2081 , 243.049 ) , ( 2082 , 242.721 ) , ( 2083 , 242.392 ) , ( 2084 , 242.063 ) , ( 2085 , 241.734 ) , ( 2086 , 241.406 ) , ( 2087 , 241.077 ) , ( 2088 , 240.748 ) , ( 2089 , 240.42 ) , ( 2090 , 240.091 ) , ( 2091 , 239.797 ) , ( 2092 , 239.502 ) , ( 2093 , 239.208 ) , ( 2094 , 238.914 ) , ( 2095 , 238.619 ) , ( 2096 , 238.325 ) , ( 2097 , 238.031 ) , ( 2098 , 237.736 ) , ( 2099 , 237.442 ) , ( 2100 , 237.147 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_anthro_CH4_SSP245_spliced_to_history"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_anthro_CH4_SSP245_spliced_to_history"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Emissions_of_anthro_CH4_from_Excel_SSP245_spliced_to_history_GtC_py = Emissions_of_anthro_CH4_SSP245_spliced_to_history * UNIT_conversion_from_MtCH4_to_GtC
    idxlhs = fcol_in_mdf["Emissions_of_anthro_CH4_from_Excel_SSP245_spliced_to_history_GtC_py"
    ]
    idx1 = fcol_in_mdf["Emissions_of_anthro_CH4_SSP245_spliced_to_history"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_from_MtCH4_to_GtC

    # CH4_emi_from_agriculture[region] = MAX ( 0 , CH4_emi_from_agriculture_a[region] * LN ( Red_meat_production[region] / UNIT_conv_Mtrmeat ) + CH4_emi_from_agriculture_b[region] )
    idxlhs = fcol_in_mdf["CH4_emi_from_agriculture"]
    idx1 = fcol_in_mdf["Red_meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0,     CH4_emi_from_agriculture_a[j]
        * math.log(mdf[rowi, idx1 + j] / UNIT_conv_Mtrmeat)
        + CH4_emi_from_agriculture_b[j],   )

    # Global_CH4_emi_from_agriculture = SUM ( CH4_emi_from_agriculture[region!] )
    idxlhs = fcol_in_mdf["Global_CH4_emi_from_agriculture"]
    idx1 = fcol_in_mdf["CH4_emi_from_agriculture"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # CH4_emi_from_energy_EU = CH4_emi_from_energy_EU_a * math.exp ( GDPpp_USED[eu] * UNIT_conv_to_make_exp_dmnl * CH4_emi_from_energy_EU_b )
    idxlhs = fcol_in_mdf["CH4_emi_from_energy_EU"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = CH4_emi_from_energy_EU_a * math.exp(
      mdf[rowi, idx1 + 8] * UNIT_conv_to_make_exp_dmnl * CH4_emi_from_energy_EU_b
    )

    # CH4_emi_from_energy_US = CH4_emi_from_energy_US_a * math.exp ( GDPpp_USED[us] * UNIT_conv_to_make_exp_dmnl * CH4_emi_from_energy_US_b )
    idxlhs = fcol_in_mdf["CH4_emi_from_energy_US"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = CH4_emi_from_energy_US_a * math.exp(
      mdf[rowi, idx1 + 0] * UNIT_conv_to_make_exp_dmnl * CH4_emi_from_energy_US_b
    )

    # CH4_emi_from_energy_EC = MAX ( 0 , CH4_emi_from_energy_EC_a * LN ( Total_use_of_fossil_fuels[ec] / UNIT_conv_to_make_fossil_fuels_dmnl ) + CH4_emi_from_energy_EC_b )
    idxlhs = fcol_in_mdf["CH4_emi_from_energy_EC"]
    idx1 = fcol_in_mdf["Total_use_of_fossil_fuels"]
    mdf[rowi, idxlhs] = max(
      0,   CH4_emi_from_energy_EC_a
      * math.log(mdf[rowi, idx1 + 7] / UNIT_conv_to_make_fossil_fuels_dmnl)
      + CH4_emi_from_energy_EC_b, )

    # CH4_emi_from_energy_WO_US_EC_EU[region] = CH4_emi_from_energy_a[region] * ( Total_use_of_fossil_fuels[region] / UNIT_conv_to_make_fossil_fuels_dmnl ) ^ CH4_emi_from_energy_b[region]
    idxlhs = fcol_in_mdf["CH4_emi_from_energy_WO_US_EC_EU"]
    idx1 = fcol_in_mdf["Total_use_of_fossil_fuels"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (CH4_emi_from_energy_a[j]
        * (mdf[rowi, idx1 + j] / UNIT_conv_to_make_fossil_fuels_dmnl)
        ** CH4_emi_from_energy_b[j]
      )

    # CH4_emi_from_energy[region] = IF_THEN_ELSE ( j==8 , CH4_emi_from_energy_EU , IF_THEN_ELSE ( j==0 , CH4_emi_from_energy_US , IF_THEN_ELSE ( j==7 , CH4_emi_from_energy_EC , CH4_emi_from_energy_WO_US_EC_EU ) ) )
    idxlhs = fcol_in_mdf["CH4_emi_from_energy"]
    idx1 = fcol_in_mdf["CH4_emi_from_energy_EU"]
    idx2 = fcol_in_mdf["CH4_emi_from_energy_US"]
    idx3 = fcol_in_mdf["CH4_emi_from_energy_EC"]
    idx4 = fcol_in_mdf["CH4_emi_from_energy_WO_US_EC_EU"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 8,     mdf[rowi, idx1],     IF_THEN_ELSE(
          j == 0,       mdf[rowi, idx2],       IF_THEN_ELSE(j == 7, mdf[rowi, idx3], mdf[rowi, idx4 + j]),     ),   )

    # Global_CH4_emi_from_energy = SUM ( CH4_emi_from_energy[region!] )
    idxlhs = fcol_in_mdf["Global_CH4_emi_from_energy"]
    idx1 = fcol_in_mdf["CH4_emi_from_energy"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # CH4_emi_from_waste_AF = CH4_emi_from_waste_AF_a * ( GDPpp_USED[af] * UNIT_conv_to_make_exp_dmnl ) ^ CH4_emi_from_waste_AF_b
    idxlhs = fcol_in_mdf["CH4_emi_from_waste_AF"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      CH4_emi_from_waste_AF_a
      * (mdf[rowi, idx1 + 1] * UNIT_conv_to_make_exp_dmnl) ** CH4_emi_from_waste_AF_b
    )

    # CH4_emi_from_waste_CN = CH4_emi_from_waste_CN_a * ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) ^ CH4_emi_from_waste_CN_b
    idxlhs = fcol_in_mdf["CH4_emi_from_waste_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      CH4_emi_from_waste_CN_a
      * (mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl) ** CH4_emi_from_waste_CN_b
    )

    # CH4_emi_from_waste_WO_CN_AF[region] = CH4_emi_from_waste_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + CH4_emi_from_waste_b[region]
    idxlhs = fcol_in_mdf["CH4_emi_from_waste_WO_CN_AF"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (CH4_emi_from_waste_a[j]
        * math.log(mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl)
        + CH4_emi_from_waste_b[j]
      )

    # CH4_emi_from_waste[region] = IF_THEN_ELSE ( j==1 , CH4_emi_from_waste_AF , IF_THEN_ELSE ( j==2 , CH4_emi_from_waste_CN , CH4_emi_from_waste_WO_CN_AF ) )
    idxlhs = fcol_in_mdf["CH4_emi_from_waste"]
    idx1 = fcol_in_mdf["CH4_emi_from_waste_AF"]
    idx2 = fcol_in_mdf["CH4_emi_from_waste_CN"]
    idx3 = fcol_in_mdf["CH4_emi_from_waste_WO_CN_AF"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 1,     mdf[rowi, idx1],     IF_THEN_ELSE(j == 2, mdf[rowi, idx2], mdf[rowi, idx3 + j]),   )

    # Global_CH4_emi_from_waste = SUM ( CH4_emi_from_waste[region!] )
    idxlhs = fcol_in_mdf["Global_CH4_emi_from_waste"]
    idx1 = fcol_in_mdf["CH4_emi_from_waste"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_CH4_emissions = Global_CH4_emi_from_agriculture + Global_CH4_emi_from_energy + Global_CH4_emi_from_waste
    idxlhs = fcol_in_mdf["Global_CH4_emissions"]
    idx1 = fcol_in_mdf["Global_CH4_emi_from_agriculture"]
    idx2 = fcol_in_mdf["Global_CH4_emi_from_energy"]
    idx3 = fcol_in_mdf["Global_CH4_emi_from_waste"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Global_CH4_emissions_GtC_py = Global_CH4_emissions * UNIT_conversion_from_MtCH4_to_GtC
    idxlhs = fcol_in_mdf["Global_CH4_emissions_GtC_py"]
    idx1 = fcol_in_mdf["Global_CH4_emissions"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_from_MtCH4_to_GtC

    # Emissions_of_anthro_CH4_1850_to_2100_GtC_py = IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2 , Emissions_of_anthro_CH4_from_Excel_SSP245_spliced_to_history_GtC_py , IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4 , Global_CH4_emissions_GtC_py , 0 ) )
    idxlhs = fcol_in_mdf["Emissions_of_anthro_CH4_1850_to_2100_GtC_py"]
    idx1 = fcol_in_mdf["Emissions_of_anthro_CH4_from_Excel_SSP245_spliced_to_history_GtC_py"
    ]
    idx2 = fcol_in_mdf["Global_CH4_emissions_GtC_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2,   mdf[rowi, idx1],   IF_THEN_ELSE(SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4, mdf[rowi, idx2], 0), )

    # CH4_emissions_before_co2e_exp = Emissions_of_anthro_CH4_1850_to_2100_GtC_py
    idxlhs = fcol_in_mdf["CH4_emissions_before_co2e_exp"]
    idx1 = fcol_in_mdf["Emissions_of_anthro_CH4_1850_to_2100_GtC_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Human_activity_CH4_emissions = CH4_emissions_before_co2e_exp
    idxlhs = fcol_in_mdf["Human_activity_CH4_emissions"]
    idx1 = fcol_in_mdf["CH4_emissions_before_co2e_exp"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Human_activity_CH4_emissions_GtCO2e_py = Human_activity_CH4_emissions / UNIT_conversion_for_CH4_from_CO2e_to_C
    idxlhs = fcol_in_mdf["Human_activity_CH4_emissions_GtCO2e_py"]
    idx1 = fcol_in_mdf["Human_activity_CH4_emissions"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_for_CH4_from_CO2e_to_C

    # Emissions_of_anthro_N2O_SSP245_MtN2O_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7.24546 ) , ( 1981 , 7.48314 ) , ( 1982 , 7.72083 ) , ( 1983 , 7.95852 ) , ( 1984 , 8.1962 ) , ( 1985 , 8.43389 ) , ( 1986 , 8.67157 ) , ( 1987 , 8.90926 ) , ( 1988 , 9.14694 ) , ( 1989 , 9.38463 ) , ( 1990 , 9.86 ) , ( 1991 , 9.928 ) , ( 1992 , 9.996 ) , ( 1993 , 10.064 ) , ( 1994 , 10.132 ) , ( 1995 , 10.2 ) , ( 1996 , 10.082 ) , ( 1997 , 9.964 ) , ( 1998 , 9.846 ) , ( 1999 , 9.728 ) , ( 2000 , 9.61 ) , ( 2001 , 9.788 ) , ( 2002 , 9.966 ) , ( 2003 , 10.144 ) , ( 2004 , 10.322 ) , ( 2005 , 10.5 ) , ( 2006 , 10.5 ) , ( 2007 , 10.5 ) , ( 2008 , 10.5 ) , ( 2009 , 10.5 ) , ( 2010 , 10.5 ) , ( 2011 , 10.55 ) , ( 2012 , 10.6 ) , ( 2013 , 10.75 ) , ( 2014 , 10.9 ) , ( 2015 , 10.9 ) , ( 2016 , 10.9846 ) , ( 2017 , 11.0691 ) , ( 2018 , 11.1537 ) , ( 2019 , 11.2383 ) , ( 2020 , 11.3229 ) , ( 2021 , 11.4114 ) , ( 2022 , 11.5 ) , ( 2023 , 11.5886 ) , ( 2024 , 11.6772 ) , ( 2025 , 11.7658 ) , ( 2026 , 11.8544 ) , ( 2027 , 11.943 ) , ( 2028 , 12.0316 ) , ( 2029 , 12.1202 ) , ( 2030 , 12.2088 ) , ( 2031 , 12.2503 ) , ( 2032 , 12.2918 ) , ( 2033 , 12.3333 ) , ( 2034 , 12.3748 ) , ( 2035 , 12.4163 ) , ( 2036 , 12.4578 ) , ( 2037 , 12.4993 ) , ( 2038 , 12.5408 ) , ( 2039 , 12.5823 ) , ( 2040 , 12.6238 ) , ( 2041 , 12.6201 ) , ( 2042 , 12.6164 ) , ( 2043 , 12.6127 ) , ( 2044 , 12.609 ) , ( 2045 , 12.6054 ) , ( 2046 , 12.6017 ) , ( 2047 , 12.598 ) , ( 2048 , 12.5943 ) , ( 2049 , 12.5906 ) , ( 2050 , 12.5869 ) , ( 2051 , 12.5501 ) , ( 2052 , 12.5133 ) , ( 2053 , 12.4764 ) , ( 2054 , 12.4396 ) , ( 2055 , 12.4028 ) , ( 2056 , 12.3659 ) , ( 2057 , 12.3291 ) , ( 2058 , 12.2922 ) , ( 2059 , 12.2554 ) , ( 2060 , 12.2186 ) , ( 2061 , 12.1513 ) , ( 2062 , 12.084 ) , ( 2063 , 12.0167 ) , ( 2064 , 11.9494 ) , ( 2065 , 11.8821 ) , ( 2066 , 11.8149 ) , ( 2067 , 11.7476 ) , ( 2068 , 11.6803 ) , ( 2069 , 11.613 ) , ( 2070 , 11.5457 ) , ( 2071 , 11.4274 ) , ( 2072 , 11.3091 ) , ( 2073 , 11.1908 ) , ( 2074 , 11.0725 ) , ( 2075 , 10.9542 ) , ( 2076 , 10.8359 ) , ( 2077 , 10.7176 ) , ( 2078 , 10.5993 ) , ( 2079 , 10.4809 ) , ( 2080 , 10.3626 ) , ( 2081 , 10.2788 ) , ( 2082 , 10.1951 ) , ( 2083 , 10.1113 ) , ( 2084 , 10.0275 ) , ( 2085 , 9.9437 ) , ( 2086 , 9.85991 ) , ( 2087 , 9.77612 ) , ( 2088 , 9.69234 ) , ( 2089 , 9.60855 ) , ( 2090 , 9.52476 ) , ( 2091 , 9.44552 ) , ( 2092 , 9.36627 ) , ( 2093 , 9.28703 ) , ( 2094 , 9.20779 ) , ( 2095 , 9.12855 ) , ( 2096 , 9.0493 ) , ( 2097 , 8.97006 ) , ( 2098 , 8.89082 ) , ( 2099 , 8.81158 ) , ( 2100 , 8.73233 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_anthro_N2O_SSP245_MtN2O_py"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_anthro_N2O_SSP245_MtN2O_py"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Nitrogen_syn_use[region] = Cropland[region] * Nitrogen_use_after_soil_regeneration[region] * UNIT_conv_to_MtN
    idxlhs = fcol_in_mdf["Nitrogen_syn_use"]
    idx1 = fcol_in_mdf["Cropland"]
    idx2 = fcol_in_mdf["Nitrogen_use_after_soil_regeneration"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * UNIT_conv_to_MtN
      )

    # Red_and_White_meat_production[region] = Meat_production[region]
    idxlhs = fcol_in_mdf["Red_and_White_meat_production"]
    idx1 = fcol_in_mdf["Meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # N_excreted_AF = N_excreted_a[af] * math.exp ( Red_and_White_meat_production[af] / UNIT_conv_to_dmnl_for_MtNmeat * N_excreted_b[af] )
    idxlhs = fcol_in_mdf["N_excreted_AF"]
    idx1 = fcol_in_mdf["Red_and_White_meat_production"]
    mdf[rowi, idxlhs] = N_excreted_a[1] * math.exp(
      mdf[rowi, idx1 + 1] / UNIT_conv_to_dmnl_for_MtNmeat * N_excreted_b[1]
    )

    # N_excreted_CN = N_excreted_a[cn] * math.exp ( Red_and_White_meat_production[cn] / UNIT_conv_to_dmnl_for_MtNmeat * N_excreted_b[cn] )
    idxlhs = fcol_in_mdf["N_excreted_CN"]
    idx1 = fcol_in_mdf["Red_and_White_meat_production"]
    mdf[rowi, idxlhs] = N_excreted_a[2] * math.exp(
      mdf[rowi, idx1 + 2] / UNIT_conv_to_dmnl_for_MtNmeat * N_excreted_b[2]
    )

    # N_excreted_without_AF_CN[region] = N_excreted_a[region] * ( Red_and_White_meat_production[region] / UNIT_conv_to_dmnl_for_MtNmeat ) ^ N_excreted_b[region]
    idxlhs = fcol_in_mdf["N_excreted_without_AF_CN"]
    idx1 = fcol_in_mdf["Red_and_White_meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (N_excreted_a[j]
        * (mdf[rowi, idx1 + j] / UNIT_conv_to_dmnl_for_MtNmeat) ** N_excreted_b[j]
      )

    # N_excreted_per_unit_of_meat_production_func[region] = IF_THEN_ELSE ( j==1 , N_excreted_AF , IF_THEN_ELSE ( j==2 , N_excreted_CN , N_excreted_without_AF_CN ) )
    idxlhs = fcol_in_mdf["N_excreted_per_unit_of_meat_production_func"]
    idx1 = fcol_in_mdf["N_excreted_AF"]
    idx2 = fcol_in_mdf["N_excreted_CN"]
    idx3 = fcol_in_mdf["N_excreted_without_AF_CN"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 1,     mdf[rowi, idx1],     IF_THEN_ELSE(j == 2, mdf[rowi, idx2], mdf[rowi, idx3 + j]),   )

    # N_excreted_per_unit_of_meat_production[region] = N_excreted_per_unit_of_meat_production_func[region] * UNIT_conv_to_MtN_from_meat
    idxlhs = fcol_in_mdf["N_excreted_per_unit_of_meat_production"]
    idx1 = fcol_in_mdf["N_excreted_per_unit_of_meat_production_func"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_MtN_from_meat

    # N_excreted_on_pasture[region] = Red_and_White_meat_production[region] * N_excreted_per_unit_of_meat_production[region]
    idxlhs = fcol_in_mdf["N_excreted_on_pasture"]
    idx1 = fcol_in_mdf["Red_and_White_meat_production"]
    idx2 = fcol_in_mdf["N_excreted_per_unit_of_meat_production"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # All_N_use_syn_and_excreted[region] = Nitrogen_syn_use[region] + N_excreted_on_pasture[region]
    idxlhs = fcol_in_mdf["All_N_use_syn_and_excreted"]
    idx1 = fcol_in_mdf["Nitrogen_syn_use"]
    idx2 = fcol_in_mdf["N_excreted_on_pasture"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # N2O_emi_from_agri_AF = N2O_emi_from_agri_AF_a * LN ( All_N_use_syn_and_excreted[af] / UNIT_conv_to_make_LN_dmnl ) + N2O_emi_from_agri_AF_b
    idxlhs = fcol_in_mdf["N2O_emi_from_agri_AF"]
    idx1 = fcol_in_mdf["All_N_use_syn_and_excreted"]
    mdf[rowi, idxlhs] = (
      N2O_emi_from_agri_AF_a * math.log(mdf[rowi, idx1 + 1] / UNIT_conv_to_make_LN_dmnl)
      + N2O_emi_from_agri_AF_b
    )

    # N2O_emi_from_agri_X_AF[region] = N2O_emi_from_agri_a[region] * All_N_use_syn_and_excreted[region] + N2O_emi_from_agri_b[region]
    idxlhs = fcol_in_mdf["N2O_emi_from_agri_X_AF"]
    idx1 = fcol_in_mdf["All_N_use_syn_and_excreted"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (N2O_emi_from_agri_a[j] * mdf[rowi, idx1 + j] + N2O_emi_from_agri_b[j]
      )

    # N2O_emi_from_agri[region] = IF_THEN_ELSE ( j==1 , N2O_emi_from_agri_AF , N2O_emi_from_agri_X_AF )
    idxlhs = fcol_in_mdf["N2O_emi_from_agri"]
    idx1 = fcol_in_mdf["N2O_emi_from_agri_AF"]
    idx2 = fcol_in_mdf["N2O_emi_from_agri_X_AF"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 1, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # Global_N2O_emi_from_agri = SUM ( N2O_emi_from_agri[region!] )
    idxlhs = fcol_in_mdf["Global_N2O_emi_from_agri"]
    idx1 = fcol_in_mdf["N2O_emi_from_agri"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # N2O_emi_X_agri_US = N2O_emi_X_agri_US_a * math.exp ( GDPpp_USED[us] * UNIT_conv_to_make_exp_dmnl * N2O_emi_X_agri_US_b )
    idxlhs = fcol_in_mdf["N2O_emi_X_agri_US"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = N2O_emi_X_agri_US_a * math.exp(
      mdf[rowi, idx1 + 0] * UNIT_conv_to_make_exp_dmnl * N2O_emi_X_agri_US_b
    )

    # N2O_emi_X_agri_EU = N2O_emi_X_agri_EU_a * math.exp ( GDPpp_USED[eu] * UNIT_conv_to_make_exp_dmnl * N2O_emi_X_agri_EU_b )
    idxlhs = fcol_in_mdf["N2O_emi_X_agri_EU"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = N2O_emi_X_agri_EU_a * math.exp(
      mdf[rowi, idx1 + 8] * UNIT_conv_to_make_exp_dmnl * N2O_emi_X_agri_EU_b
    )

    # N2O_emi_X_agri_CN = N2O_emi_X_agri_CN_a * LN ( GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) + N2O_emi_X_agri_CN_b
    idxlhs = fcol_in_mdf["N2O_emi_X_agri_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      N2O_emi_X_agri_CN_a * math.log(mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl)
      + N2O_emi_X_agri_CN_b
    )

    # N2O_emi_X_agri_SA = N2O_emi_X_agri_SA_a * LN ( GDPpp_USED[sa] * UNIT_conv_to_make_exp_dmnl ) + N2O_emi_X_agri_SA_b
    idxlhs = fcol_in_mdf["N2O_emi_X_agri_SA"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      N2O_emi_X_agri_SA_a * math.log(mdf[rowi, idx1 + 4] * UNIT_conv_to_make_exp_dmnl)
      + N2O_emi_X_agri_SA_b
    )

    # N2O_emi_X_agri_WO_US_EU_CN_SA[region] = N2O_emi_X_agri_a[region] * GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl + N2O_emi_X_agri_b[region]
    idxlhs = fcol_in_mdf["N2O_emi_X_agri_WO_US_EU_CN_SA"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (N2O_emi_X_agri_a[j] * mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl
        + N2O_emi_X_agri_b[j]
      )

    # N2O_emi_X_agri[region] = IF_THEN_ELSE ( j==0 , N2O_emi_X_agri_US , IF_THEN_ELSE ( j==8 , N2O_emi_X_agri_EU , IF_THEN_ELSE ( j==2 , N2O_emi_X_agri_CN , IF_THEN_ELSE ( j==4 , N2O_emi_X_agri_SA , N2O_emi_X_agri_WO_US_EU_CN_SA ) ) ) )
    idxlhs = fcol_in_mdf["N2O_emi_X_agri"]
    idx1 = fcol_in_mdf["N2O_emi_X_agri_US"]
    idx2 = fcol_in_mdf["N2O_emi_X_agri_EU"]
    idx3 = fcol_in_mdf["N2O_emi_X_agri_CN"]
    idx4 = fcol_in_mdf["N2O_emi_X_agri_SA"]
    idx5 = fcol_in_mdf["N2O_emi_X_agri_WO_US_EU_CN_SA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 0,     mdf[rowi, idx1],     IF_THEN_ELSE(
          j == 8,       mdf[rowi, idx2],       IF_THEN_ELSE(
            j == 2,         mdf[rowi, idx3],         IF_THEN_ELSE(j == 4, mdf[rowi, idx4], mdf[rowi, idx5 + j]),       ),     ),   )

    # Global_N2O_emi_X_agri = SUM ( N2O_emi_X_agri[region!] )
    idxlhs = fcol_in_mdf["Global_N2O_emi_X_agri"]
    idx1 = fcol_in_mdf["N2O_emi_X_agri"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_N2O_emissions = Global_N2O_emi_from_agri + Global_N2O_emi_X_agri
    idxlhs = fcol_in_mdf["Global_N2O_emissions"]
    idx1 = fcol_in_mdf["Global_N2O_emi_from_agri"]
    idx2 = fcol_in_mdf["Global_N2O_emi_X_agri"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # N2O_emissions_JR_RCP3_or_SSP245 = IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2 , Emissions_of_anthro_N2O_SSP245_MtN2O_py , IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4 , Global_N2O_emissions , 0 ) )
    idxlhs = fcol_in_mdf["N2O_emissions_JR_RCP3_or_SSP245"]
    idx1 = fcol_in_mdf["Emissions_of_anthro_N2O_SSP245_MtN2O_py"]
    idx2 = fcol_in_mdf["Global_N2O_emissions"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2,   mdf[rowi, idx1],   IF_THEN_ELSE(SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4, mdf[rowi, idx2], 0), )

    # N2O_man_made_emissions_exp_12a = N2O_emissions_JR_RCP3_or_SSP245
    idxlhs = fcol_in_mdf["N2O_man_made_emissions_exp_12a"]
    idx1 = fcol_in_mdf["N2O_emissions_JR_RCP3_or_SSP245"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # N2O_man_made_emissions_GtCO2e_py = N2O_man_made_emissions_exp_12a * Global_Warming_Potential_N20 / UNIT_conversion_Gt_to_Mt
    idxlhs = fcol_in_mdf["N2O_man_made_emissions_GtCO2e_py"]
    idx1 = fcol_in_mdf["N2O_man_made_emissions_exp_12a"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Global_Warming_Potential_N20 / UNIT_conversion_Gt_to_Mt
    )

    # Emissions_of_Kyoto_Fluor_F_gases_SSP245_kt_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 22.9501 ) , ( 1981 , 22.074 ) , ( 1982 , 23.4422 ) , ( 1983 , 23.2237 ) , ( 1984 , 23.4892 ) , ( 1985 , 23.7867 ) , ( 1986 , 26.7277 ) , ( 1987 , 26.1138 ) , ( 1988 , 26.0124 ) , ( 1989 , 27.824 ) , ( 1990 , 28.2991 ) , ( 1991 , 30.2933 ) , ( 1992 , 33.3907 ) , ( 1993 , 39.3754 ) , ( 1994 , 54.2056 ) , ( 1995 , 67.9878 ) , ( 1996 , 81.2674 ) , ( 1997 , 91.8081 ) , ( 1998 , 103.682 ) , ( 1999 , 113.371 ) , ( 2000 , 144.458 ) , ( 2001 , 158.931 ) , ( 2002 , 176.526 ) , ( 2003 , 191.492 ) , ( 2004 , 210.618 ) , ( 2005 , 224.991 ) , ( 2006 , 238.121 ) , ( 2007 , 259.671 ) , ( 2008 , 281.72 ) , ( 2009 , 303.77 ) , ( 2010 , 325.819 ) , ( 2011 , 338.297 ) , ( 2012 , 350.774 ) , ( 2013 , 363.252 ) , ( 2014 , 375.729 ) , ( 2015 , 388.207 ) , ( 2016 , 400.685 ) , ( 2017 , 413.162 ) , ( 2018 , 425.64 ) , ( 2019 , 438.117 ) , ( 2020 , 450.595 ) , ( 2021 , 452.946 ) , ( 2022 , 455.297 ) , ( 2023 , 457.648 ) , ( 2024 , 460 ) , ( 2025 , 462.351 ) , ( 2026 , 464.702 ) , ( 2027 , 467.053 ) , ( 2028 , 469.404 ) , ( 2029 , 471.755 ) , ( 2030 , 474.107 ) , ( 2031 , 478.767 ) , ( 2032 , 483.428 ) , ( 2033 , 488.088 ) , ( 2034 , 492.749 ) , ( 2035 , 497.409 ) , ( 2036 , 502.069 ) , ( 2037 , 506.73 ) , ( 2038 , 511.39 ) , ( 2039 , 516.051 ) , ( 2040 , 520.711 ) , ( 2041 , 517.107 ) , ( 2042 , 513.504 ) , ( 2043 , 509.9 ) , ( 2044 , 506.296 ) , ( 2045 , 502.692 ) , ( 2046 , 499.088 ) , ( 2047 , 495.484 ) , ( 2048 , 491.88 ) , ( 2049 , 488.276 ) , ( 2050 , 484.672 ) , ( 2051 , 491.238 ) , ( 2052 , 497.804 ) , ( 2053 , 504.369 ) , ( 2054 , 510.935 ) , ( 2055 , 517.501 ) , ( 2056 , 524.067 ) , ( 2057 , 530.633 ) , ( 2058 , 537.198 ) , ( 2059 , 543.764 ) , ( 2060 , 550.33 ) , ( 2061 , 557.156 ) , ( 2062 , 563.982 ) , ( 2063 , 570.808 ) , ( 2064 , 577.634 ) , ( 2065 , 584.46 ) , ( 2066 , 591.286 ) , ( 2067 , 598.112 ) , ( 2068 , 604.939 ) , ( 2069 , 611.765 ) , ( 2070 , 618.591 ) , ( 2071 , 620.479 ) , ( 2072 , 622.368 ) , ( 2073 , 624.257 ) , ( 2074 , 626.146 ) , ( 2075 , 628.035 ) , ( 2076 , 629.923 ) , ( 2077 , 631.812 ) , ( 2078 , 633.701 ) , ( 2079 , 635.59 ) , ( 2080 , 637.478 ) , ( 2081 , 634.811 ) , ( 2082 , 632.143 ) , ( 2083 , 629.475 ) , ( 2084 , 626.807 ) , ( 2085 , 624.139 ) , ( 2086 , 621.472 ) , ( 2087 , 618.804 ) , ( 2088 , 616.136 ) , ( 2089 , 613.468 ) , ( 2090 , 610.8 ) , ( 2091 , 605.13 ) , ( 2092 , 599.46 ) , ( 2093 , 593.79 ) , ( 2094 , 588.119 ) , ( 2095 , 582.449 ) , ( 2096 , 576.779 ) , ( 2097 , 571.109 ) , ( 2098 , 565.438 ) , ( 2099 , 559.768 ) , ( 2100 , 554.098 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_Kyoto_Fluor_F_gases_SSP245_kt_py"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_Kyoto_Fluor_F_gases_SSP245_kt_py"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Emissions_of_Kyoto_Fluor_with_JR_2052_shape_kt_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 102.464 ) , ( 1981 , 102.866 ) , ( 1982 , 97.6419 ) , ( 1983 , 104.071 ) , ( 1984 , 114.518 ) , ( 1985 , 113.715 ) , ( 1986 , 115.724 ) , ( 1987 , 121.349 ) , ( 1988 , 133.404 ) , ( 1989 , 140.637 ) , ( 1990 , 137.824 ) , ( 1991 , 135.413 ) , ( 1992 , 132.198 ) , ( 1993 , 129.787 ) , ( 1994 , 135.413 ) , ( 1995 , 147.467 ) , ( 1996 , 159.12 ) , ( 1997 , 173.586 ) , ( 1998 , 178.006 ) , ( 1999 , 187.649 ) , ( 2000 , 184.033 ) , ( 2001 , 177.604 ) , ( 2002 , 188.855 ) , ( 2003 , 193.275 ) , ( 2004 , 217.786 ) , ( 2005 , 236.671 ) , ( 2006 , 254.753 ) , ( 2007 , 262.789 ) , ( 2008 , 274.844 ) , ( 2009 , 272.031 ) , ( 2010 , 289.309 ) , ( 2011 , 302.569 ) , ( 2012 , 319.044 ) , ( 2013 , 349.984 ) , ( 2014 , 381.728 ) , ( 2015 , 371.682 ) , ( 2016 , 384.139 ) , ( 2017 , 399.809 ) , ( 2018 , 413.873 ) , ( 2019 , 421.91 ) , ( 2020 , 425.573 ) , ( 2021 , 430.467 ) , ( 2022 , 435.361 ) , ( 2023 , 440.255 ) , ( 2024 , 445.149 ) , ( 2025 , 450.043 ) , ( 2026 , 452.659 ) , ( 2027 , 455.275 ) , ( 2028 , 457.891 ) , ( 2029 , 460.507 ) , ( 2030 , 463.123 ) , ( 2031 , 461.834 ) , ( 2032 , 460.546 ) , ( 2033 , 459.257 ) , ( 2034 , 457.968 ) , ( 2035 , 456.68 ) , ( 2036 , 453.04 ) , ( 2037 , 449.401 ) , ( 2038 , 445.761 ) , ( 2039 , 442.122 ) , ( 2040 , 438.482 ) , ( 2041 , 431.628 ) , ( 2042 , 424.774 ) , ( 2043 , 417.92 ) , ( 2044 , 411.065 ) , ( 2045 , 404.211 ) , ( 2046 , 394.801 ) , ( 2047 , 385.39 ) , ( 2048 , 375.979 ) , ( 2049 , 366.568 ) , ( 2050 , 357.158 ) , ( 2051 , 350.015 ) , ( 2052 , 342.871 ) , ( 2053 , 335.728 ) , ( 2054 , 328.585 ) , ( 2055 , 321.442 ) , ( 2056 , 314.299 ) , ( 2057 , 307.156 ) , ( 2058 , 300.012 ) , ( 2059 , 292.869 ) , ( 2060 , 285.726 ) , ( 2061 , 278.583 ) , ( 2062 , 271.44 ) , ( 2063 , 264.297 ) , ( 2064 , 257.154 ) , ( 2065 , 250.01 ) , ( 2066 , 242.867 ) , ( 2067 , 235.724 ) , ( 2068 , 228.581 ) , ( 2069 , 221.438 ) , ( 2070 , 214.295 ) , ( 2071 , 207.151 ) , ( 2072 , 200.008 ) , ( 2073 , 192.865 ) , ( 2074 , 185.722 ) , ( 2075 , 178.579 ) , ( 2076 , 171.436 ) , ( 2077 , 164.293 ) , ( 2078 , 157.149 ) , ( 2079 , 150.006 ) , ( 2080 , 142.863 ) , ( 2081 , 135.72 ) , ( 2082 , 128.577 ) , ( 2083 , 121.434 ) , ( 2084 , 114.29 ) , ( 2085 , 107.147 ) , ( 2086 , 100.004 ) , ( 2087 , 92.861 ) , ( 2088 , 85.7178 ) , ( 2089 , 78.5747 ) , ( 2090 , 71.4315 ) , ( 2091 , 64.2884 ) , ( 2092 , 57.1452 ) , ( 2093 , 50.0021 ) , ( 2094 , 42.8589 ) , ( 2095 , 35.7158 ) , ( 2096 , 28.5726 ) , ( 2097 , 21.4295 ) , ( 2098 , 14.2863 ) , ( 2099 , 7.14315 ) , ( 2100 , 0 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_Kyoto_Fluor_with_JR_2052_shape_kt_py"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_Kyoto_Fluor_with_JR_2052_shape_kt_py"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Kyoto_Fluor_emissions_JR_RCP3_or_SSP245 = IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2 , Emissions_of_Kyoto_Fluor_F_gases_SSP245_kt_py , IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4 , Emissions_of_Kyoto_Fluor_with_JR_2052_shape_kt_py , 0 ) )
    idxlhs = fcol_in_mdf["Kyoto_Fluor_emissions_JR_RCP3_or_SSP245"]
    idx1 = fcol_in_mdf["Emissions_of_Kyoto_Fluor_F_gases_SSP245_kt_py"]
    idx2 = fcol_in_mdf["Emissions_of_Kyoto_Fluor_with_JR_2052_shape_kt_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2,   mdf[rowi, idx1],   IF_THEN_ELSE(SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4, mdf[rowi, idx2], 0), )

    # Kyoto_Fluor_emissions = Kyoto_Fluor_emissions_JR_RCP3_or_SSP245
    idxlhs = fcol_in_mdf["Kyoto_Fluor_emissions"]
    idx1 = fcol_in_mdf["Kyoto_Fluor_emissions_JR_RCP3_or_SSP245"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Kyoto_Fluor_emissions_GtCO2e_py = Kyoto_Fluor_emissions * Kyoto_Fluor_Global_Warming_Potential / UNIT_conversion_Gt_to_kt
    idxlhs = fcol_in_mdf["Kyoto_Fluor_emissions_GtCO2e_py"]
    idx1 = fcol_in_mdf["Kyoto_Fluor_emissions"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Kyoto_Fluor_Global_Warming_Potential / UNIT_conversion_Gt_to_kt
    )

    # Emissions_of_Montreal_gases_SSP245_kt_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1638.4 ) , ( 1981 , 1532.3 ) , ( 1982 , 1539.42 ) , ( 1983 , 1677.43 ) , ( 1984 , 1792.07 ) , ( 1985 , 1685.65 ) , ( 1986 , 1939.86 ) , ( 1987 , 2064.68 ) , ( 1988 , 2060.15 ) , ( 1989 , 1813.51 ) , ( 1990 , 1989.86 ) , ( 1991 , 1607.8 ) , ( 1992 , 1517.42 ) , ( 1993 , 1168.94 ) , ( 1994 , 1014.23 ) , ( 1995 , 962.917 ) , ( 1996 , 795.891 ) , ( 1997 , 711.038 ) , ( 1998 , 728.513 ) , ( 1999 , 680.544 ) , ( 2000 , 677.163 ) , ( 2001 , 625.922 ) , ( 2002 , 609.698 ) , ( 2003 , 626.466 ) , ( 2004 , 605.364 ) , ( 2005 , 545.23 ) , ( 2006 , 557.65 ) , ( 2007 , 564.595 ) , ( 2008 , 566.209 ) , ( 2009 , 568.007 ) , ( 2010 , 564.927 ) , ( 2011 , 550.292 ) , ( 2012 , 535.908 ) , ( 2013 , 521.714 ) , ( 2014 , 507.677 ) , ( 2015 , 486.503 ) , ( 2016 , 479.534 ) , ( 2017 , 472.965 ) , ( 2018 , 466.766 ) , ( 2019 , 460.903 ) , ( 2020 , 455.355 ) , ( 2021 , 435.413 ) , ( 2022 , 415.665 ) , ( 2023 , 396.093 ) , ( 2024 , 376.678 ) , ( 2025 , 357.406 ) , ( 2026 , 338.26 ) , ( 2027 , 319.227 ) , ( 2028 , 300.295 ) , ( 2029 , 281.454 ) , ( 2030 , 262.688 ) , ( 2031 , 244.298 ) , ( 2032 , 226.279 ) , ( 2033 , 208.622 ) , ( 2034 , 191.318 ) , ( 2035 , 174.355 ) , ( 2036 , 157.728 ) , ( 2037 , 141.428 ) , ( 2038 , 125.449 ) , ( 2039 , 109.785 ) , ( 2040 , 94.4303 ) , ( 2041 , 87.7823 ) , ( 2042 , 81.3364 ) , ( 2043 , 75.082 ) , ( 2044 , 69.0179 ) , ( 2045 , 63.1357 ) , ( 2046 , 57.4293 ) , ( 2047 , 51.8959 ) , ( 2048 , 46.5323 ) , ( 2049 , 41.3309 ) , ( 2050 , 36.2895 ) , ( 2051 , 34.5942 ) , ( 2052 , 32.9107 ) , ( 2053 , 31.2384 ) , ( 2054 , 29.5769 ) , ( 2055 , 27.924 ) , ( 2056 , 26.2799 ) , ( 2057 , 24.64 ) , ( 2058 , 23.0086 ) , ( 2059 , 21.3792 ) , ( 2060 , 19.7546 ) , ( 2061 , 18.9096 ) , ( 2062 , 18.0799 ) , ( 2063 , 17.2587 ) , ( 2064 , 16.4495 ) , ( 2065 , 15.6506 ) , ( 2066 , 14.8597 ) , ( 2067 , 14.0776 ) , ( 2068 , 13.3052 ) , ( 2069 , 12.5383 ) , ( 2070 , 11.7786 ) , ( 2071 , 11.2949 ) , ( 2072 , 10.8192 ) , ( 2073 , 10.3525 ) , ( 2074 , 9.89385 ) , ( 2075 , 9.44502 ) , ( 2076 , 9.00251 ) , ( 2077 , 8.56719 ) , ( 2078 , 8.13906 ) , ( 2079 , 7.7181 ) , ( 2080 , 7.30258 ) , ( 2081 , 7.03404 ) , ( 2082 , 6.77378 ) , ( 2083 , 6.51485 ) , ( 2084 , 6.25904 ) , ( 2085 , 6.009 ) , ( 2086 , 5.76214 ) , ( 2087 , 5.51762 ) , ( 2088 , 5.27545 ) , ( 2089 , 5.03744 ) , ( 2090 , 4.80273 ) , ( 2091 , 4.60003 ) , ( 2092 , 4.40176 ) , ( 2093 , 4.20965 ) , ( 2094 , 4.021 ) , ( 2095 , 3.8384 ) , ( 2096 , 3.66004 ) , ( 2097 , 3.48504 ) , ( 2098 , 3.31763 ) , ( 2099 , 3.15178 ) , ( 2100 , 2.99003 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_Montreal_gases_SSP245_kt_py"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_Montreal_gases_SSP245_kt_py"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Emissions_of_Montreal_gases_with_JR_2052_shape_kt_py = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1638.4 ) , ( 1981 , 1532.3 ) , ( 1982 , 1539.42 ) , ( 1983 , 1677.43 ) , ( 1984 , 1792.07 ) , ( 1985 , 1685.65 ) , ( 1986 , 1939.86 ) , ( 1987 , 2064.68 ) , ( 1988 , 2060.15 ) , ( 1989 , 1813.51 ) , ( 1990 , 1989.86 ) , ( 1991 , 1607.8 ) , ( 1992 , 1517.42 ) , ( 1993 , 1168.94 ) , ( 1994 , 1014.23 ) , ( 1995 , 962.917 ) , ( 1996 , 795.891 ) , ( 1997 , 711.038 ) , ( 1998 , 728.513 ) , ( 1999 , 680.544 ) , ( 2000 , 677.163 ) , ( 2001 , 625.922 ) , ( 2002 , 609.698 ) , ( 2003 , 626.466 ) , ( 2004 , 605.364 ) , ( 2005 , 545.23 ) , ( 2006 , 557.65 ) , ( 2007 , 564.595 ) , ( 2008 , 566.209 ) , ( 2009 , 568.007 ) , ( 2010 , 564.927 ) , ( 2011 , 550.292 ) , ( 2012 , 535.908 ) , ( 2013 , 521.714 ) , ( 2014 , 507.677 ) , ( 2015 , 486.503 ) , ( 2016 , 479.534 ) , ( 2017 , 472.965 ) , ( 2018 , 466.766 ) , ( 2019 , 460.903 ) , ( 2020 , 455.355 ) , ( 2021 , 434.648 ) , ( 2022 , 414.207 ) , ( 2023 , 394.013 ) , ( 2024 , 374.045 ) , ( 2025 , 354.289 ) , ( 2026 , 334.726 ) , ( 2027 , 315.343 ) , ( 2028 , 296.127 ) , ( 2029 , 277.066 ) , ( 2030 , 258.146 ) , ( 2031 , 242.019 ) , ( 2032 , 226 ) , ( 2033 , 210.081 ) , ( 2034 , 194.256 ) , ( 2035 , 178.515 ) , ( 2036 , 162.855 ) , ( 2037 , 147.269 ) , ( 2038 , 131.752 ) , ( 2039 , 116.301 ) , ( 2040 , 100.909 ) , ( 2041 , 94.99 ) , ( 2042 , 89.141 ) , ( 2043 , 83.353 ) , ( 2044 , 77.627 ) , ( 2045 , 71.956 ) , ( 2046 , 66.335 ) , ( 2047 , 60.763 ) , ( 2048 , 55.238 ) , ( 2049 , 49.753 ) , ( 2050 , 44.307 ) , ( 2051 , 42.06 ) , ( 2052 , 39.846 ) , ( 2053 , 37.664 ) , ( 2054 , 35.513 ) , ( 2055 , 33.39 ) , ( 2056 , 31.295 ) , ( 2057 , 29.222 ) , ( 2058 , 27.176 ) , ( 2059 , 25.149 ) , ( 2060 , 23.144 ) , ( 2061 , 22.109 ) , ( 2062 , 21.096 ) , ( 2063 , 20.097 ) , ( 2064 , 19.116 ) , ( 2065 , 18.151 ) , ( 2066 , 17.199 ) , ( 2067 , 16.261 ) , ( 2068 , 15.338 ) , ( 2069 , 14.425 ) , ( 2070 , 13.524 ) , ( 2071 , 12.972 ) , ( 2072 , 12.429 ) , ( 2073 , 11.896 ) , ( 2074 , 11.372 ) , ( 2075 , 10.859 ) , ( 2076 , 10.353 ) , ( 2077 , 9.855 ) , ( 2078 , 9.365 ) , ( 2079 , 8.883 ) , ( 2080 , 8.407 ) , ( 2081 , 8.079 ) , ( 2082 , 7.762 ) , ( 2083 , 7.448 ) , ( 2084 , 7.139 ) , ( 2085 , 6.838 ) , ( 2086 , 6.542 ) , ( 2087 , 6.25 ) , ( 2088 , 5.962 ) , ( 2089 , 5.68 ) , ( 2090 , 5.403 ) , ( 2091 , 5.201 ) , ( 2092 , 5.002 ) , ( 2093 , 4.808 ) , ( 2094 , 4.616 ) , ( 2095 , 4.429 ) , ( 2096 , 4.245 ) , ( 2097 , 4.063 ) , ( 2098 , 3.888 ) , ( 2099 , 3.713 ) , ( 2100 , 3.541 ) ) )
    tabidx = ftab_in_d_table[  "Emissions_of_Montreal_gases_with_JR_2052_shape_kt_py"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Emissions_of_Montreal_gases_with_JR_2052_shape_kt_py"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Montreal_gases_emissions_JR_RCP3_or_SSP245 = IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2 , Emissions_of_Montreal_gases_SSP245_kt_py , IF_THEN_ELSE ( SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4 , Emissions_of_Montreal_gases_with_JR_2052_shape_kt_py , 0 ) )
    idxlhs = fcol_in_mdf["Montreal_gases_emissions_JR_RCP3_or_SSP245"]
    idx1 = fcol_in_mdf["Emissions_of_Montreal_gases_SSP245_kt_py"]
    idx2 = fcol_in_mdf["Emissions_of_Montreal_gases_with_JR_2052_shape_kt_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 2,   mdf[rowi, idx1],   IF_THEN_ELSE(SWITCH_choose_4_for_e4a_or_2_for_ssp245 == 4, mdf[rowi, idx2], 0), )

    # Montreal_gases_emissions = Montreal_gases_emissions_JR_RCP3_or_SSP245
    idxlhs = fcol_in_mdf["Montreal_gases_emissions"]
    idx1 = fcol_in_mdf["Montreal_gases_emissions_JR_RCP3_or_SSP245"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Montreal_emissions_GtCO2e_py = Montreal_gases_emissions * Montreal_Global_Warming_Potential / UNIT_conversion_Gt_to_kt
    idxlhs = fcol_in_mdf["Montreal_emissions_GtCO2e_py"]
    idx1 = fcol_in_mdf["Montreal_gases_emissions"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Montreal_Global_Warming_Potential / UNIT_conversion_Gt_to_kt
    )

    # N_excreted_on_pasture_H[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7.06 ) , ( 1981 , 7.21 ) , ( 1982 , 7.2 ) , ( 1983 , 7.15 ) , ( 1984 , 7.09 ) , ( 1985 , 6.94 ) , ( 1986 , 6.78 ) , ( 1987 , 6.69 ) , ( 1988 , 6.62 ) , ( 1989 , 6.54 ) , ( 1990 , 6.54 ) , ( 1991 , 6.62 ) , ( 1992 , 6.69 ) , ( 1993 , 6.77 ) , ( 1994 , 6.88 ) , ( 1995 , 6.97 ) , ( 1996 , 7.01 ) , ( 1997 , 6.98 ) , ( 1998 , 6.87 ) , ( 1999 , 6.82 ) , ( 2000 , 6.81 ) , ( 2001 , 6.8 ) , ( 2002 , 6.81 ) , ( 2003 , 6.81 ) , ( 2004 , 6.78 ) , ( 2005 , 6.84 ) , ( 2006 , 6.96 ) , ( 2007 , 6.98 ) , ( 2008 , 7.03 ) , ( 2009 , 6.87 ) , ( 2010 , 6.85 ) , ( 2011 , 6.81 ) , ( 2012 , 6.75 ) , ( 2013 , 6.67 ) , ( 2014 , 6.64 ) , ( 2015 , 6.68 ) , ( 2016 , 6.84 ) , ( 2017 , 6.94 ) , ( 2018 , 6.98 ) , ( 2019 , 7.01 ) ) ) N_excreted_on_pasture_H[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7.86 ) , ( 1981 , 7.95 ) , ( 1982 , 8.17 ) , ( 1983 , 8.24 ) , ( 1984 , 7.97 ) , ( 1985 , 8.03 ) , ( 1986 , 8.22 ) , ( 1987 , 8.32 ) , ( 1988 , 8.61 ) , ( 1989 , 8.88 ) , ( 1990 , 9.2 ) , ( 1991 , 9.47 ) , ( 1992 , 9.57 ) , ( 1993 , 11.23 ) , ( 1994 , 11.38 ) , ( 1995 , 11.66 ) , ( 1996 , 11.86 ) , ( 1997 , 12.23 ) , ( 1998 , 12.68 ) , ( 1999 , 13.18 ) , ( 2000 , 13.27 ) , ( 2001 , 13.62 ) , ( 2002 , 14.07 ) , ( 2003 , 14.44 ) , ( 2004 , 14.84 ) , ( 2005 , 15.35 ) , ( 2006 , 15.75 ) , ( 2007 , 17.07 ) , ( 2008 , 17.75 ) , ( 2009 , 18.24 ) , ( 2010 , 18.78 ) , ( 2011 , 19.47 ) , ( 2012 , 22.71 ) , ( 2013 , 23.3 ) , ( 2014 , 23.82 ) , ( 2015 , 24.4 ) , ( 2016 , 25.18 ) , ( 2017 , 25.62 ) , ( 2018 , 26.25 ) , ( 2019 , 27.09 ) ) ) N_excreted_on_pasture_H[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7.99 ) , ( 1981 , 8.02 ) , ( 1982 , 8.07 ) , ( 1983 , 8.22 ) , ( 1984 , 8.14 ) , ( 1985 , 8.3 ) , ( 1986 , 8.66 ) , ( 1987 , 9.14 ) , ( 1988 , 9.44 ) , ( 1989 , 9.98 ) , ( 1990 , 10.27 ) , ( 1991 , 10.62 ) , ( 1992 , 10.79 ) , ( 1993 , 11.13 ) , ( 1994 , 11.71 ) , ( 1995 , 12.65 ) , ( 1996 , 13.82 ) , ( 1997 , 12.24 ) , ( 1998 , 12.72 ) , ( 1999 , 13.26 ) , ( 2000 , 13.67 ) , ( 2001 , 13.54 ) , ( 2002 , 13.44 ) , ( 2003 , 13.36 ) , ( 2004 , 13.59 ) , ( 2005 , 13.82 ) , ( 2006 , 13.72 ) , ( 2007 , 13.3 ) , ( 2008 , 13.63 ) , ( 2009 , 13.62 ) , ( 2010 , 13.5 ) , ( 2011 , 13 ) , ( 2012 , 13 ) , ( 2013 , 12.91 ) , ( 2014 , 12.83 ) , ( 2015 , 13.06 ) , ( 2016 , 13.32 ) , ( 2017 , 12.94 ) , ( 2018 , 12.8 ) , ( 2019 , 12.44 ) ) ) N_excreted_on_pasture_H[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 3.01 ) , ( 1981 , 3.04 ) , ( 1982 , 3 ) , ( 1983 , 3.14 ) , ( 1984 , 3.17 ) , ( 1985 , 3.24 ) , ( 1986 , 3.38 ) , ( 1987 , 3.46 ) , ( 1988 , 3.44 ) , ( 1989 , 3.62 ) , ( 1990 , 3.73 ) , ( 1991 , 3.63 ) , ( 1992 , 3.79 ) , ( 1993 , 3.78 ) , ( 1994 , 3.81 ) , ( 1995 , 3.84 ) , ( 1996 , 3.91 ) , ( 1997 , 4.03 ) , ( 1998 , 4.11 ) , ( 1999 , 4.16 ) , ( 2000 , 4.22 ) , ( 2001 , 4.23 ) , ( 2002 , 4.27 ) , ( 2003 , 4.37 ) , ( 2004 , 4.52 ) , ( 2005 , 4.63 ) , ( 2006 , 4.7 ) , ( 2007 , 4.82 ) , ( 2008 , 4.71 ) , ( 2009 , 4.78 ) , ( 2010 , 4.83 ) , ( 2011 , 4.96 ) , ( 2012 , 5.01 ) , ( 2013 , 5.05 ) , ( 2014 , 4.86 ) , ( 2015 , 4.89 ) , ( 2016 , 4.92 ) , ( 2017 , 4.82 ) , ( 2018 , 4.82 ) , ( 2019 , 4.91 ) ) ) N_excreted_on_pasture_H[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 10.17 ) , ( 1981 , 10.4 ) , ( 1982 , 10.67 ) , ( 1983 , 10.91 ) , ( 1984 , 11.12 ) , ( 1985 , 11.27 ) , ( 1986 , 11.59 ) , ( 1987 , 11.8 ) , ( 1988 , 11.99 ) , ( 1989 , 12.17 ) , ( 1990 , 12.36 ) , ( 1991 , 12.53 ) , ( 1992 , 12.78 ) , ( 1993 , 12.95 ) , ( 1994 , 13.16 ) , ( 1995 , 13.36 ) , ( 1996 , 13.47 ) , ( 1997 , 13.61 ) , ( 1998 , 13.65 ) , ( 1999 , 13.76 ) , ( 2000 , 13.85 ) , ( 2001 , 14 ) , ( 2002 , 14.18 ) , ( 2003 , 14.38 ) , ( 2004 , 14.7 ) , ( 2005 , 15.04 ) , ( 2006 , 15.45 ) , ( 2007 , 15.92 ) , ( 2008 , 16.06 ) , ( 2009 , 16.22 ) , ( 2010 , 16.35 ) , ( 2011 , 16.57 ) , ( 2012 , 16.72 ) , ( 2013 , 16.82 ) , ( 2014 , 16.96 ) , ( 2015 , 17.29 ) , ( 2016 , 17.67 ) , ( 2017 , 18.1 ) , ( 2018 , 18.43 ) , ( 2019 , 18.71 ) ) ) N_excreted_on_pasture_H[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 16.84 ) , ( 1981 , 17.04 ) , ( 1982 , 17.13 ) , ( 1983 , 17.17 ) , ( 1984 , 17.36 ) , ( 1985 , 17.49 ) , ( 1986 , 17.74 ) , ( 1987 , 17.93 ) , ( 1988 , 18.22 ) , ( 1989 , 18.61 ) , ( 1990 , 18.68 ) , ( 1991 , 18.95 ) , ( 1992 , 19.16 ) , ( 1993 , 19.21 ) , ( 1994 , 19.51 ) , ( 1995 , 19.64 ) , ( 1996 , 19.07 ) , ( 1997 , 19.26 ) , ( 1998 , 19.29 ) , ( 1999 , 19.38 ) , ( 2000 , 19.68 ) , ( 2001 , 20.12 ) , ( 2002 , 20.72 ) , ( 2003 , 21.42 ) , ( 2004 , 21.96 ) , ( 2005 , 22.29 ) , ( 2006 , 22.43 ) , ( 2007 , 22.32 ) , ( 2008 , 22.56 ) , ( 2009 , 22.73 ) , ( 2010 , 22.73 ) , ( 2011 , 22.84 ) , ( 2012 , 22.84 ) , ( 2013 , 22.87 ) , ( 2014 , 23.02 ) , ( 2015 , 23.15 ) , ( 2016 , 23.25 ) , ( 2017 , 23.17 ) , ( 2018 , 23.25 ) , ( 2019 , 23.43 ) ) ) N_excreted_on_pasture_H[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7.57 ) , ( 1981 , 7.49 ) , ( 1982 , 7.55 ) , ( 1983 , 7.34 ) , ( 1984 , 7.45 ) , ( 1985 , 7.68 ) , ( 1986 , 7.68 ) , ( 1987 , 7.54 ) , ( 1988 , 7.63 ) , ( 1989 , 7.75 ) , ( 1990 , 7.95 ) , ( 1991 , 7.79 ) , ( 1992 , 7.51 ) , ( 1993 , 7.29 ) , ( 1994 , 7.32 ) , ( 1995 , 7.14 ) , ( 1996 , 7.18 ) , ( 1997 , 7.17 ) , ( 1998 , 7.06 ) , ( 1999 , 7.01 ) , ( 2000 , 7.06 ) , ( 2001 , 6.92 ) , ( 2002 , 6.87 ) , ( 2003 , 6.65 ) , ( 2004 , 6.78 ) , ( 2005 , 6.83 ) , ( 2006 , 6.69 ) , ( 2007 , 6.49 ) , ( 2008 , 6.17 ) , ( 2009 , 6.1 ) , ( 2010 , 5.93 ) , ( 2011 , 6.05 ) , ( 2012 , 6.11 ) , ( 2013 , 6.21 ) , ( 2014 , 6.12 ) , ( 2015 , 5.93 ) , ( 2016 , 5.7 ) , ( 2017 , 5.87 ) , ( 2018 , 5.85 ) , ( 2019 , 5.66 ) ) ) N_excreted_on_pasture_H[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 12.4 ) , ( 1981 , 12.4 ) , ( 1982 , 12.5 ) , ( 1983 , 12.63 ) , ( 1984 , 12.9 ) , ( 1985 , 12.93 ) , ( 1986 , 12.82 ) , ( 1987 , 12.93 ) , ( 1988 , 12.67 ) , ( 1989 , 12.74 ) , ( 1990 , 12.59 ) , ( 1991 , 12.27 ) , ( 1992 , 11.12 ) , ( 1993 , 10.55 ) , ( 1994 , 10.03 ) , ( 1995 , 9.06 ) , ( 1996 , 8.36 ) , ( 1997 , 7.54 ) , ( 1998 , 6.97 ) , ( 1999 , 6.72 ) , ( 2000 , 6.61 ) , ( 2001 , 6.35 ) , ( 2002 , 6.29 ) , ( 2003 , 6.39 ) , ( 2004 , 6.27 ) , ( 2005 , 6.26 ) , ( 2006 , 6.52 ) , ( 2007 , 6.69 ) , ( 2008 , 6.79 ) , ( 2009 , 6.79 ) , ( 2010 , 6.67 ) , ( 2011 , 6.7 ) , ( 2012 , 6.84 ) , ( 2013 , 7.02 ) , ( 2014 , 7.17 ) , ( 2015 , 7.28 ) , ( 2016 , 7.45 ) , ( 2017 , 7.56 ) , ( 2018 , 7.57 ) , ( 2019 , 7.64 ) ) ) N_excreted_on_pasture_H[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 13.75 ) , ( 1981 , 13.72 ) , ( 1982 , 13.85 ) , ( 1983 , 13.66 ) , ( 1984 , 13.71 ) , ( 1985 , 13.42 ) , ( 1986 , 13.61 ) , ( 1987 , 13.4 ) , ( 1988 , 13.41 ) , ( 1989 , 13.4 ) , ( 1990 , 13.32 ) , ( 1991 , 12.93 ) , ( 1992 , 13.01 ) , ( 1993 , 12.67 ) , ( 1994 , 12.46 ) , ( 1995 , 12.28 ) , ( 1996 , 12.17 ) , ( 1997 , 12.17 ) , ( 1998 , 12.05 ) , ( 1999 , 11.95 ) , ( 2000 , 12.19 ) , ( 2001 , 11.83 ) , ( 2002 , 11.77 ) , ( 2003 , 11.55 ) , ( 2004 , 11.41 ) , ( 2005 , 11.35 ) , ( 2006 , 11.31 ) , ( 2007 , 11.3 ) , ( 2008 , 11.19 ) , ( 2009 , 11.02 ) , ( 2010 , 10.96 ) , ( 2011 , 10.88 ) , ( 2012 , 10.93 ) , ( 2013 , 11.08 ) , ( 2014 , 11.21 ) , ( 2015 , 11.34 ) , ( 2016 , 11.36 ) , ( 2017 , 11.37 ) , ( 2018 , 11.15 ) , ( 2019 , 11.16 ) ) ) N_excreted_on_pasture_H[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2.29 ) , ( 1981 , 2.41 ) , ( 1982 , 2.5 ) , ( 1983 , 2.71 ) , ( 1984 , 2.78 ) , ( 1985 , 2.86 ) , ( 1986 , 2.96 ) , ( 1987 , 2.99 ) , ( 1988 , 3.04 ) , ( 1989 , 3.06 ) , ( 1990 , 3.12 ) , ( 1991 , 3.2 ) , ( 1992 , 3.34 ) , ( 1993 , 3.4 ) , ( 1994 , 3.54 ) , ( 1995 , 3.58 ) , ( 1996 , 3.65 ) , ( 1997 , 3.64 ) , ( 1998 , 3.44 ) , ( 1999 , 3.38 ) , ( 2000 , 3.5 ) , ( 2001 , 3.57 ) , ( 2002 , 3.77 ) , ( 2003 , 3.81 ) , ( 2004 , 3.85 ) , ( 2005 , 3.93 ) , ( 2006 , 4.03 ) , ( 2007 , 4.21 ) , ( 2008 , 4.27 ) , ( 2009 , 4.41 ) , ( 2010 , 4.46 ) , ( 2011 , 4.57 ) , ( 2012 , 4.7 ) , ( 2013 , 4.66 ) , ( 2014 , 4.84 ) , ( 2015 , 5.01 ) , ( 2016 , 5.12 ) , ( 2017 , 5.76 ) , ( 2018 , 5.91 ) , ( 2019 , 6.06 ) ) )
    tabidx = ftab_in_d_table["N_excreted_on_pasture_H"]  # fetch the correct table
    idx2 = fcol_in_mdf["N_excreted_on_pasture_H"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # syn_N_use_hist_table[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 10.66 ) , ( 1981 , 10.25 ) , ( 1982 , 8.84 ) , ( 1983 , 9.47 ) , ( 1984 , 10.31 ) , ( 1985 , 9.78 ) , ( 1986 , 9.33 ) , ( 1987 , 9.45 ) , ( 1988 , 9.59 ) , ( 1989 , 9.9 ) , ( 1990 , 10.18 ) , ( 1991 , 10.34 ) , ( 1992 , 10.35 ) , ( 1993 , 11.1 ) , ( 1994 , 10.91 ) , ( 1995 , 10.99 ) , ( 1996 , 11.19 ) , ( 1997 , 11.18 ) , ( 1998 , 11.25 ) , ( 1999 , 11.22 ) , ( 2000 , 10.7 ) , ( 2001 , 10.75 ) , ( 2002 , 10.97 ) , ( 2003 , 11.82 ) , ( 2004 , 11.19 ) , ( 2005 , 10.93 ) , ( 2006 , 11.97 ) , ( 2007 , 11.4 ) , ( 2008 , 10.4 ) , ( 2009 , 11.1 ) , ( 2010 , 11.62 ) , ( 2011 , 12.23 ) , ( 2012 , 12.25 ) , ( 2013 , 12.06 ) , ( 2014 , 11.8 ) , ( 2015 , 11.83 ) , ( 2016 , 11.64 ) , ( 2017 , 11.58 ) , ( 2018 , 11.63 ) , ( 2019 , 11.67 ) ) ) syn_N_use_hist_table[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.88 ) , ( 1981 , 0.96 ) , ( 1982 , 0.9 ) , ( 1983 , 0.79 ) , ( 1984 , 0.83 ) , ( 1985 , 0.84 ) , ( 1986 , 0.82 ) , ( 1987 , 0.78 ) , ( 1988 , 0.89 ) , ( 1989 , 0.9 ) , ( 1990 , 0.93 ) , ( 1991 , 0.93 ) , ( 1992 , 0.93 ) , ( 1993 , 1.04 ) , ( 1994 , 0.96 ) , ( 1995 , 0.86 ) , ( 1996 , 1 ) , ( 1997 , 0.98 ) , ( 1998 , 0.97 ) , ( 1999 , 1.02 ) , ( 2000 , 0.99 ) , ( 2001 , 0.97 ) , ( 2002 , 1.17 ) , ( 2003 , 1.07 ) , ( 2004 , 1.13 ) , ( 2005 , 1.1 ) , ( 2006 , 1.26 ) , ( 2007 , 1.12 ) , ( 2008 , 1.22 ) , ( 2009 , 1.24 ) , ( 2010 , 1.55 ) , ( 2011 , 1.44 ) , ( 2012 , 1.65 ) , ( 2013 , 1.81 ) , ( 2014 , 1.88 ) , ( 2015 , 1.81 ) , ( 2016 , 2.2 ) , ( 2017 , 2.65 ) , ( 2018 , 2.54 ) , ( 2019 , 2.54 ) ) ) syn_N_use_hist_table[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 12.11 ) , ( 1981 , 11.53 ) , ( 1982 , 12.27 ) , ( 1983 , 13.72 ) , ( 1984 , 15.18 ) , ( 1985 , 13.84 ) , ( 1986 , 13.58 ) , ( 1987 , 16.8 ) , ( 1988 , 18.51 ) , ( 1989 , 18.86 ) , ( 1990 , 19.56 ) , ( 1991 , 19.97 ) , ( 1992 , 20.33 ) , ( 1993 , 18 ) , ( 1994 , 19.16 ) , ( 1995 , 23.78 ) , ( 1996 , 25.28 ) , ( 1997 , 22.95 ) , ( 1998 , 22.89 ) , ( 1999 , 24.14 ) , ( 2000 , 22.14 ) , ( 2001 , 22.42 ) , ( 2002 , 25.26 ) , ( 2003 , 25.38 ) , ( 2004 , 26.43 ) , ( 2005 , 26.82 ) , ( 2006 , 27.43 ) , ( 2007 , 28.17 ) , ( 2008 , 28.56 ) , ( 2009 , 29.13 ) , ( 2010 , 29.7 ) , ( 2011 , 30.3 ) , ( 2012 , 30.8 ) , ( 2013 , 30.96 ) , ( 2014 , 31.14 ) , ( 2015 , 30.95 ) , ( 2016 , 30.54 ) , ( 2017 , 29.69 ) , ( 2018 , 28.29 ) , ( 2019 , 26.87 ) ) ) syn_N_use_hist_table[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.25 ) , ( 1981 , 1.4 ) , ( 1982 , 1.57 ) , ( 1983 , 1.74 ) , ( 1984 , 1.73 ) , ( 1985 , 1.85 ) , ( 1986 , 2.12 ) , ( 1987 , 2.15 ) , ( 1988 , 2.19 ) , ( 1989 , 2.33 ) , ( 1990 , 2.21 ) , ( 1991 , 2.27 ) , ( 1992 , 2.46 ) , ( 1993 , 2.43 ) , ( 1994 , 2.28 ) , ( 1995 , 2.5 ) , ( 1996 , 2.59 ) , ( 1997 , 2.75 ) , ( 1998 , 2.93 ) , ( 1999 , 2.94 ) , ( 2000 , 3.04 ) , ( 2001 , 3.27 ) , ( 2002 , 3.47 ) , ( 2003 , 3.07 ) , ( 2004 , 3.48 ) , ( 2005 , 3.5 ) , ( 2006 , 3.75 ) , ( 2007 , 3.36 ) , ( 2008 , 3.39 ) , ( 2009 , 3.14 ) , ( 2010 , 2.93 ) , ( 2011 , 2.66 ) , ( 2012 , 2.65 ) , ( 2013 , 2.55 ) , ( 2014 , 2.56 ) , ( 2015 , 2.52 ) , ( 2016 , 2.54 ) , ( 2017 , 2.73 ) , ( 2018 , 2.61 ) , ( 2019 , 2.63 ) ) ) syn_N_use_hist_table[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 4.9 ) , ( 1981 , 5.25 ) , ( 1982 , 5.4 ) , ( 1983 , 6.01 ) , ( 1984 , 6.78 ) , ( 1985 , 7.38 ) , ( 1986 , 8.42 ) , ( 1987 , 7.6 ) , ( 1988 , 9.16 ) , ( 1989 , 9.41 ) , ( 1990 , 9.79 ) , ( 1991 , 10.37 ) , ( 1992 , 10.94 ) , ( 1993 , 11.34 ) , ( 1994 , 12.24 ) , ( 1995 , 12.94 ) , ( 1996 , 13.49 ) , ( 1997 , 14.07 ) , ( 1998 , 14.56 ) , ( 1999 , 15.04 ) , ( 2000 , 14.39 ) , ( 2001 , 14.86 ) , ( 2002 , 14.14 ) , ( 2003 , 14.64 ) , ( 2004 , 15.41 ) , ( 2005 , 16.72 ) , ( 2006 , 17.91 ) , ( 2007 , 18.34 ) , ( 2008 , 19.29 ) , ( 2009 , 20.38 ) , ( 2010 , 21.1 ) , ( 2011 , 22.09 ) , ( 2012 , 21.01 ) , ( 2013 , 21.31 ) , ( 2014 , 21.64 ) , ( 2015 , 22.19 ) , ( 2016 , 21.37 ) , ( 2017 , 21.85 ) , ( 2018 , 22.6 ) , ( 2019 , 23.96 ) ) ) syn_N_use_hist_table[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2.58 ) , ( 1981 , 2.54 ) , ( 1982 , 2.54 ) , ( 1983 , 2.43 ) , ( 1984 , 2.91 ) , ( 1985 , 3.09 ) , ( 1986 , 3.5 ) , ( 1987 , 3.65 ) , ( 1988 , 3.47 ) , ( 1989 , 3.39 ) , ( 1990 , 3.41 ) , ( 1991 , 3.24 ) , ( 1992 , 3.33 ) , ( 1993 , 3.6 ) , ( 1994 , 3.81 ) , ( 1995 , 3.77 ) , ( 1996 , 4.31 ) , ( 1997 , 4.58 ) , ( 1998 , 4.77 ) , ( 1999 , 4.86 ) , ( 2000 , 5.06 ) , ( 2001 , 5.17 ) , ( 2002 , 4.95 ) , ( 2003 , 5.58 ) , ( 2004 , 6.12 ) , ( 2005 , 5.72 ) , ( 2006 , 5.95 ) , ( 2007 , 7.13 ) , ( 2008 , 6.53 ) , ( 2009 , 5.96 ) , ( 2010 , 7.11 ) , ( 2011 , 8.06 ) , ( 2012 , 7.93 ) , ( 2013 , 8.83 ) , ( 2014 , 8.54 ) , ( 2015 , 7.32 ) , ( 2016 , 8.35 ) , ( 2017 , 9.41 ) , ( 2018 , 9.36 ) , ( 2019 , 9.8 ) ) ) syn_N_use_hist_table[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2.27 ) , ( 1981 , 2.31 ) , ( 1982 , 2.35 ) , ( 1983 , 2.66 ) , ( 1984 , 2.82 ) , ( 1985 , 2.7 ) , ( 1986 , 2.63 ) , ( 1987 , 2.7 ) , ( 1988 , 2.67 ) , ( 1989 , 2.81 ) , ( 1990 , 2.76 ) , ( 1991 , 2.83 ) , ( 1992 , 2.95 ) , ( 1993 , 3.15 ) , ( 1994 , 3.22 ) , ( 1995 , 3.41 ) , ( 1996 , 3.6 ) , ( 1997 , 3.63 ) , ( 1998 , 3.69 ) , ( 1999 , 3.85 ) , ( 2000 , 3.65 ) , ( 2001 , 3.7 ) , ( 2002 , 3.78 ) , ( 2003 , 3.81 ) , ( 2004 , 3.89 ) , ( 2005 , 4.05 ) , ( 2006 , 3.38 ) , ( 2007 , 4.09 ) , ( 2008 , 3.83 ) , ( 2009 , 3.72 ) , ( 2010 , 4.04 ) , ( 2011 , 4.62 ) , ( 2012 , 4.88 ) , ( 2013 , 4.64 ) , ( 2014 , 4.97 ) , ( 2015 , 4.88 ) , ( 2016 , 4.96 ) , ( 2017 , 5 ) , ( 2018 , 5.22 ) , ( 2019 , 4.94 ) ) ) syn_N_use_hist_table[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 9.43 ) , ( 1981 , 9.87 ) , ( 1982 , 10.54 ) , ( 1983 , 11.82 ) , ( 1984 , 11.7 ) , ( 1985 , 12.42 ) , ( 1986 , 12.76 ) , ( 1987 , 13.06 ) , ( 1988 , 12.94 ) , ( 1989 , 11.28 ) , ( 1990 , 10.04 ) , ( 1991 , 8.46 ) , ( 1992 , 5.76 ) , ( 1993 , 4.43 ) , ( 1994 , 3.01 ) , ( 1995 , 2.89 ) , ( 1996 , 2.63 ) , ( 1997 , 3.04 ) , ( 1998 , 2.86 ) , ( 1999 , 2.78 ) , ( 2000 , 2.88 ) , ( 2001 , 3.06 ) , ( 2002 , 2.98 ) , ( 2003 , 2.93 ) , ( 2004 , 2.87 ) , ( 2005 , 3 ) , ( 2006 , 3.5 ) , ( 2007 , 3.84 ) , ( 2008 , 4.26 ) , ( 2009 , 4.32 ) , ( 2010 , 4.31 ) , ( 2011 , 4.81 ) , ( 2012 , 4.74 ) , ( 2013 , 4.87 ) , ( 2014 , 4.7 ) , ( 2015 , 4.88 ) , ( 2016 , 5.31 ) , ( 2017 , 5.58 ) , ( 2018 , 5.65 ) , ( 2019 , 6 ) ) ) syn_N_use_hist_table[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 13.39 ) , ( 1981 , 13.11 ) , ( 1982 , 13.59 ) , ( 1983 , 14.05 ) , ( 1984 , 14.16 ) , ( 1985 , 14.42 ) , ( 1986 , 14.83 ) , ( 1987 , 14.87 ) , ( 1988 , 15.07 ) , ( 1989 , 14.85 ) , ( 1990 , 13.08 ) , ( 1991 , 12.15 ) , ( 1992 , 11.66 ) , ( 1993 , 11.96 ) , ( 1994 , 12.22 ) , ( 1995 , 12.12 ) , ( 1996 , 12.91 ) , ( 1997 , 12.72 ) , ( 1998 , 12.95 ) , ( 1999 , 13.17 ) , ( 2000 , 12.34 ) , ( 2001 , 12.11 ) , ( 2002 , 12.05 ) , ( 2003 , 12.48 ) , ( 2004 , 12.19 ) , ( 2005 , 11.83 ) , ( 2006 , 11.71 ) , ( 2007 , 12.23 ) , ( 2008 , 11.09 ) , ( 2009 , 10.84 ) , ( 2010 , 11.48 ) , ( 2011 , 11.1 ) , ( 2012 , 11.57 ) , ( 2013 , 11.97 ) , ( 2014 , 12.17 ) , ( 2015 , 12.29 ) , ( 2016 , 12.64 ) , ( 2017 , 12.56 ) , ( 2018 , 11.92 ) , ( 2019 , 11.91 ) ) ) syn_N_use_hist_table[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.51 ) , ( 1981 , 1.76 ) , ( 1982 , 1.97 ) , ( 1983 , 2.14 ) , ( 1984 , 2.36 ) , ( 1985 , 2.46 ) , ( 1986 , 2.71 ) , ( 1987 , 2.83 ) , ( 1988 , 3.13 ) , ( 1989 , 3.1 ) , ( 1990 , 3.33 ) , ( 1991 , 3.32 ) , ( 1992 , 3.56 ) , ( 1993 , 3.66 ) , ( 1994 , 4.07 ) , ( 1995 , 4.19 ) , ( 1996 , 4.76 ) , ( 1997 , 4.46 ) , ( 1998 , 5.18 ) , ( 1999 , 5.19 ) , ( 2000 , 5.22 ) , ( 2001 , 4.91 ) , ( 2002 , 5.1 ) , ( 2003 , 5.79 ) , ( 2004 , 6.12 ) , ( 2005 , 5.84 ) , ( 2006 , 5.7 ) , ( 2007 , 6.18 ) , ( 2008 , 5.83 ) , ( 2009 , 6.98 ) , ( 2010 , 6.94 ) , ( 2011 , 6.89 ) , ( 2012 , 7.13 ) , ( 2013 , 7.38 ) , ( 2014 , 7.31 ) , ( 2015 , 7.15 ) , ( 2016 , 7.36 ) , ( 2017 , 7.85 ) , ( 2018 , 7.76 ) , ( 2019 , 7.25 ) ) )
    tabidx = ftab_in_d_table["syn_N_use_hist_table"]  # fetch the correct table
    idx2 = fcol_in_mdf["syn_N_use_hist_table"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # All_N2O_emissions = N2O_man_made_emissions_exp_12a + N2O_natural_emissions
    idxlhs = fcol_in_mdf["All_N2O_emissions"]
    idx1 = fcol_in_mdf["N2O_man_made_emissions_exp_12a"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + N2O_natural_emissions

    # Regional_GDP_weight[region] = GDP_USED[region] / Global_GDP_USED
    idxlhs = fcol_in_mdf["Regional_GDP_weight"]
    idx1 = fcol_in_mdf["GDP_USED"]
    idx2 = fcol_in_mdf["Global_GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2]

    # Each_region_max_cost_estimate_empowerment_PES[region] = All_region_max_cost_estimate_empowerment_PES * Regional_GDP_weight[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_empowerment_PES"]
    idx1 = fcol_in_mdf["Regional_GDP_weight"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (All_region_max_cost_estimate_empowerment_PES * mdf[rowi, idx1 + j]
      )

    # Each_region_max_cost_estimate_energy_PES[region] = All_region_max_cost_estimate_energy_PES * Regional_GDP_weight[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_energy_PES"]
    idx1 = fcol_in_mdf["Regional_GDP_weight"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (All_region_max_cost_estimate_energy_PES * mdf[rowi, idx1 + j]
      )

    # Each_region_max_cost_estimate_food_PES[region] = All_region_max_cost_estimate_food_PES * Regional_GDP_weight[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_food_PES"]
    idx1 = fcol_in_mdf["Regional_GDP_weight"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (All_region_max_cost_estimate_food_PES * mdf[rowi, idx1 + j]
      )

    # Each_region_max_cost_estimate_inequality_PES[region] = All_region_max_cost_estimate_inequality_PES * Regional_GDP_weight[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_inequality_PES"]
    idx1 = fcol_in_mdf["Regional_GDP_weight"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (All_region_max_cost_estimate_inequality_PES * mdf[rowi, idx1 + j]
      )

    # Each_region_max_cost_estimate_poverty_PES[region] = All_region_max_cost_estimate_poverty_PES * Regional_GDP_weight[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_poverty_PES"]
    idx1 = fcol_in_mdf["Regional_GDP_weight"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (All_region_max_cost_estimate_poverty_PES * mdf[rowi, idx1 + j]
      )

    # Each_region_max_cost_estimate_all_TAs_PES[region] = Each_region_max_cost_estimate_empowerment_PES[region] + Each_region_max_cost_estimate_energy_PES[region] + Each_region_max_cost_estimate_food_PES[region] + Each_region_max_cost_estimate_inequality_PES[region] + Each_region_max_cost_estimate_poverty_PES[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_all_TAs_PES"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_empowerment_PES"]
    idx2 = fcol_in_mdf["Each_region_max_cost_estimate_energy_PES"]
    idx3 = fcol_in_mdf["Each_region_max_cost_estimate_food_PES"]
    idx4 = fcol_in_mdf["Each_region_max_cost_estimate_inequality_PES"]
    idx5 = fcol_in_mdf["Each_region_max_cost_estimate_poverty_PES"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
      )

    # SDG1_Score[region] = IF_THEN_ELSE ( Fraction_of_population_below_existential_minimum > SDG1_threshold_red , 0 , IF_THEN_ELSE ( Fraction_of_population_below_existential_minimum > SDG1_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG1_Score"]
    idx1 = fcol_in_mdf["Fraction_of_population_below_existential_minimum"]
    idx2 = fcol_in_mdf["Fraction_of_population_below_existential_minimum"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] > SDG1_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] > SDG1_threshold_green, 0.5, 1),   )

    # Fraction_of_population_undernourished[region] = MIN ( 1 , SDG2_a * ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) ^ ( SDG2_b ) )
    idxlhs = fcol_in_mdf["Fraction_of_population_undernourished"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(
        1, SDG2_a * (mdf[rowi, idx1 + j] / UNIT_conv_to_make_base_dmnless) ** (SDG2_b)
      )

    # SDG_2_Score[region] = IF_THEN_ELSE ( Fraction_of_population_undernourished > SDG2_threshold_red , 0 , IF_THEN_ELSE ( Fraction_of_population_undernourished > SDG2_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG_2_Score"]
    idx1 = fcol_in_mdf["Fraction_of_population_undernourished"]
    idx2 = fcol_in_mdf["Fraction_of_population_undernourished"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] > SDG2_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] > SDG2_threshold_green, 0.5, 1),   )

    # Worker_cash_inflow_seasonally_adjusted_pp[region] = Worker_cash_inflow_seasonally_adjusted[region] / Population[region]
    idxlhs = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted_pp"]
    idx1 = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Wellbeing_from_disposable_income[region] = Worker_cash_inflow_seasonally_adjusted_pp[region] / Disposable_income_threshold_for_wellbeing
    idxlhs = fcol_in_mdf["Wellbeing_from_disposable_income"]
    idx1 = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Disposable_income_threshold_for_wellbeing
      )

    # Ratio_actual_to_basic_el_use[region] = Actual_el_use_pp[region] / Basic_el_use
    idxlhs = fcol_in_mdf["Ratio_actual_to_basic_el_use"]
    idx1 = fcol_in_mdf["Actual_el_use_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Basic_el_use

    # Wellbeing_from_el_use_raw[region] = El_use_wellbeing_a + El_use_wellbeing_b * LN ( Ratio_actual_to_basic_el_use[region] )
    idxlhs = fcol_in_mdf["Wellbeing_from_el_use_raw"]
    idx1 = fcol_in_mdf["Ratio_actual_to_basic_el_use"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = El_use_wellbeing_a + El_use_wellbeing_b * math.log(
        mdf[rowi, idx1 + j]
      )

    # Wellbeing_from_el_use_scaled[region] = Wellbeing_from_el_use_raw[region] / ( El_use_wellbeing_a + El_use_wellbeing_b * LN ( 1 ) )
    idxlhs = fcol_in_mdf["Wellbeing_from_el_use_scaled"]
    idx1 = fcol_in_mdf["Wellbeing_from_el_use_raw"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        El_use_wellbeing_a + El_use_wellbeing_b * math.log(1)
      )

    # white_meat_not_wasted_pp[region] = white_meat_demand_pp_consumed[region] * UNIT_conv_kgwmeat_to_kg
    idxlhs = fcol_in_mdf["white_meat_not_wasted_pp"]
    idx1 = fcol_in_mdf["white_meat_demand_pp_consumed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_kgwmeat_to_kg

    # Ratio_of_actual_to_healthy_white_meat[region] = white_meat_not_wasted_pp[region] / Healthy_white_meat_consumption
    idxlhs = fcol_in_mdf["Ratio_of_actual_to_healthy_white_meat"]
    idx1 = fcol_in_mdf["white_meat_not_wasted_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Healthy_white_meat_consumption

    # Wellbeing_from_white_meat[region] = ( 1 / ( stdev * SQRT ( 2 * 3.14142 ) ) ) * math.exp ( - ( ( Ratio_of_actual_to_healthy_white_meat[region] - mean_value ) ^ 2 ) / ( 2 * stdev ^ 2 ) )
    idxlhs = fcol_in_mdf["Wellbeing_from_white_meat"]
    idx1 = fcol_in_mdf["Ratio_of_actual_to_healthy_white_meat"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 / (stdev * SQRT(2 * 3.14142))) * math.exp(
        -((mdf[rowi, idx1 + j] - mean_value) ** 2) / (2 * stdev**2)
      )

    # red_meat_not_wasted_pp[region] = red_meat_demand_pp_consumed[region] * UNIT_conv_kgrmeat_to_kg
    idxlhs = fcol_in_mdf["red_meat_not_wasted_pp"]
    idx1 = fcol_in_mdf["red_meat_demand_pp_consumed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_kgrmeat_to_kg

    # Ratio_of_actual_to_healthy_red_meat[region] = red_meat_not_wasted_pp[region] / Healthy_red_meat_consumption
    idxlhs = fcol_in_mdf["Ratio_of_actual_to_healthy_red_meat"]
    idx1 = fcol_in_mdf["red_meat_not_wasted_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Healthy_red_meat_consumption

    # Wellbeing_from_red_meat[region] = ( 1 / ( stdev * SQRT ( 2 * 3.14142 ) ) ) * math.exp ( - ( ( Ratio_of_actual_to_healthy_red_meat[region] - mean_value ) ^ 2 ) / ( 2 * stdev ^ 2 ) )
    idxlhs = fcol_in_mdf["Wellbeing_from_red_meat"]
    idx1 = fcol_in_mdf["Ratio_of_actual_to_healthy_red_meat"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 / (stdev * SQRT(2 * 3.14142))) * math.exp(
        -((mdf[rowi, idx1 + j] - mean_value) ** 2) / (2 * stdev**2)
      )

    # Ratio_of_actual_to_healthy_all_crop[region] = all_crop_not_wasted_pp[region] / Healthy_all_crop_consumption
    idxlhs = fcol_in_mdf["Ratio_of_actual_to_healthy_all_crop"]
    idx1 = fcol_in_mdf["all_crop_not_wasted_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Healthy_all_crop_consumption

    # Wellbeing_from_crops[region] = ( 1 / ( stdev * SQRT ( 2 * 3.14142 ) ) ) * math.exp ( - ( ( Ratio_of_actual_to_healthy_all_crop[region] - mean_value ) ^ 2 ) / ( 2 * stdev ^ 2 ) )
    idxlhs = fcol_in_mdf["Wellbeing_from_crops"]
    idx1 = fcol_in_mdf["Ratio_of_actual_to_healthy_all_crop"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 / (stdev * SQRT(2 * 3.14142))) * math.exp(
        -((mdf[rowi, idx1 + j] - mean_value) ** 2) / (2 * stdev**2)
      )

    # Wellbeing_from_food[region] = ( Wellbeing_from_white_meat[region] * Weight_on_white_meat + Wellbeing_from_red_meat[region] * Weight_on_red_meat + Wellbeing_from_crops[region] * Weight_on_crops ) / Sum_of_food_weights
    idxlhs = fcol_in_mdf["Wellbeing_from_food"]
    idx1 = fcol_in_mdf["Wellbeing_from_white_meat"]
    idx2 = fcol_in_mdf["Wellbeing_from_red_meat"]
    idx3 = fcol_in_mdf["Wellbeing_from_crops"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * Weight_on_white_meat
        + mdf[rowi, idx2 + j] * Weight_on_red_meat
        + mdf[rowi, idx3 + j] * Weight_on_crops
      ) / Sum_of_food_weights

    # Wellbeing_from_inequality[region] = 1 / Actual_inequality_index_higher_is_more_unequal[region]
    idxlhs = fcol_in_mdf["Wellbeing_from_inequality"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 / mdf[rowi, idx1 + j]

    # Wellbeing_from_population_with_regular_job[region] = 1 + Slope_of_wellbeing_from_fraction_of_people_outside_of_labor_pool * ( Frac_outside_of_labour_pool_in_1980[region] / Fraction_of_people_outside_of_labour_market_FOPOLM[region] - 1 )
    idxlhs = fcol_in_mdf["Wellbeing_from_population_with_regular_job"]
    idx1 = fcol_in_mdf["Fraction_of_people_outside_of_labour_market_FOPOLM"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + Slope_of_wellbeing_from_fraction_of_people_outside_of_labor_pool
        * (Frac_outside_of_labour_pool_in_1980[j] / mdf[rowi, idx1 + j] - 1)
      )

    # Public_spending_as_share_of_GDP[region] = Public_services_pp[region] / GDPpp_USED[region] / UNIT_conv_to_k217pppUSD_ppy
    idxlhs = fcol_in_mdf["Public_spending_as_share_of_GDP"]
    idx1 = fcol_in_mdf["Public_services_pp"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] / UNIT_conv_to_k217pppUSD_ppy
      )

    # Smoothed_Public_spending_as_share_of_GDP[region] = SMOOTH ( Public_spending_as_share_of_GDP[region] , Time_for_public_spending_to_affect_wellbeing )
    idx1 = fcol_in_mdf["Smoothed_Public_spending_as_share_of_GDP"]
    idx2 = fcol_in_mdf["Public_spending_as_share_of_GDP"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_public_spending_to_affect_wellbeing
        * dt
      )

    # Public_spending_ratio[region] = Smoothed_Public_spending_as_share_of_GDP[region] / Satisfactory_public_spending
    idxlhs = fcol_in_mdf["Public_spending_ratio"]
    idx1 = fcol_in_mdf["Smoothed_Public_spending_as_share_of_GDP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Satisfactory_public_spending

    # Wellbeing_from_public_spending[region] = WITH LOOKUP ( Public_spending_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 0.25 , 0.02907 ) , ( 0.5 , 0.08995 ) , ( 0.75 , 0.2175 ) , ( 1 , 0.4699 ) , ( 1.25 , 0.9055 ) , ( 1.5 , 1.5 ) , ( 1.75 , 2.095 ) , ( 2 , 2.53 ) , ( 2.25 , 2.782 ) , ( 2.5 , 2.91 ) , ( 2.75 , 2.971 ) , ( 3 , 3 ) ) )
    tabidx = ftab_in_d_table[  "Wellbeing_from_public_spending"]  # fetch the correct table
    idx2 = fcol_in_mdf["Wellbeing_from_public_spending"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Public_spending_ratio"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Living_conditions_index[region] = ( Weight_disposable_income * Wellbeing_from_disposable_income[region] + Weight_el_use * Wellbeing_from_el_use_scaled[region] + Weight_food * Wellbeing_from_food[region] + Weight_inequality * Wellbeing_from_inequality[region] + Weight_population_in_job_market * Wellbeing_from_population_with_regular_job[region] + Weight_public_spending * Wellbeing_from_public_spending[region] ) / Sum_weights_living_conditions
    idxlhs = fcol_in_mdf["Living_conditions_index"]
    idx1 = fcol_in_mdf["Wellbeing_from_disposable_income"]
    idx2 = fcol_in_mdf["Wellbeing_from_el_use_scaled"]
    idx3 = fcol_in_mdf["Wellbeing_from_food"]
    idx4 = fcol_in_mdf["Wellbeing_from_inequality"]
    idx5 = fcol_in_mdf["Wellbeing_from_population_with_regular_job"]
    idx6 = fcol_in_mdf["Wellbeing_from_public_spending"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Weight_disposable_income * mdf[rowi, idx1 + j]
        + Weight_el_use * mdf[rowi, idx2 + j]
        + Weight_food * mdf[rowi, idx3 + j]
        + Weight_inequality * mdf[rowi, idx4 + j]
        + Weight_population_in_job_market * mdf[rowi, idx5 + j]
        + Weight_public_spending * mdf[rowi, idx6 + j]
      ) / Sum_weights_living_conditions

    # Living_conditions_index_with_env_damage[region] = Living_conditions_index[region] * Weight_on_living_conditions + Actual_wellbeing_from_env_damage[region] * Weight_on_env_conditions
    idxlhs = fcol_in_mdf["Living_conditions_index_with_env_damage"]
    idx1 = fcol_in_mdf["Living_conditions_index"]
    idx2 = fcol_in_mdf["Actual_wellbeing_from_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * Weight_on_living_conditions
        + mdf[rowi, idx2 + j] * Weight_on_env_conditions
      )

    # Wellbeing_from_social_tension[region] = 1 + SoE_of_Wellbeing_from_social_tension * ( Smoothed_Social_tension_index_with_trust_effect[region] / Social_tension_index_in_1980 - 1 )
    idxlhs = fcol_in_mdf["Wellbeing_from_social_tension"]
    idx1 = fcol_in_mdf["Smoothed_Social_tension_index_with_trust_effect"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + SoE_of_Wellbeing_from_social_tension * (
        mdf[rowi, idx1 + j] / Social_tension_index_in_1980 - 1
      )

    # Smoothed_comparison_Effect_of_SDG_score_on_wellbeing[region] = SMOOTH3I ( Comparison_Effect_of_SDG_score_on_wellbeing[region] , Time_to_smooth_SDG_scores_for_wellbeing , 1 )
    idxin = fcol_in_mdf["Comparison_Effect_of_SDG_score_on_wellbeing"]
    idx2 = fcol_in_mdf["Smoothed_comparison_Effect_of_SDG_score_on_wellbeing_2"]
    idx1 = fcol_in_mdf["Smoothed_comparison_Effect_of_SDG_score_on_wellbeing_1"]
    idxout = fcol_in_mdf["Smoothed_comparison_Effect_of_SDG_score_on_wellbeing"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_smooth_SDG_scores_for_wellbeing / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_smooth_SDG_scores_for_wellbeing / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_smooth_SDG_scores_for_wellbeing / 3)
        * dt
      )

    # Average_wellbeing_index[region] = ( Living_conditions_index_with_env_damage[region] * Weight_on_physical_conditions + Wellbeing_from_social_tension[region] * ( 1 - Weight_on_physical_conditions ) ) * Smoothed_comparison_Effect_of_SDG_score_on_wellbeing[region]
    idxlhs = fcol_in_mdf["Average_wellbeing_index"]
    idx1 = fcol_in_mdf["Living_conditions_index_with_env_damage"]
    idx2 = fcol_in_mdf["Wellbeing_from_social_tension"]
    idx3 = fcol_in_mdf["Smoothed_comparison_Effect_of_SDG_score_on_wellbeing"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * Weight_on_physical_conditions
        + mdf[rowi, idx2 + j] * (1 - Weight_on_physical_conditions)
      ) * mdf[rowi, idx3 + j]

    # SDG_3_Score[region] = IF_THEN_ELSE ( Average_wellbeing_index < SDG3_threshold_red , 0 , IF_THEN_ELSE ( Average_wellbeing_index < SDG3_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG_3_Score"]
    idx1 = fcol_in_mdf["Average_wellbeing_index"]
    idx2 = fcol_in_mdf["Average_wellbeing_index"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG3_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG3_threshold_green, 0.5, 1),   )

    # Safe_water_cn = Safe_water_cn_L / ( 1 + math.exp ( - Safe_water_cn_k * ( ( GDPpp_USED[cn] / UNIT_conv_to_make_base_dmnless ) - Safe_water_cn_x0 ) ) ) + Safe_water_cn_min
    idxlhs = fcol_in_mdf["Safe_water_cn"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      Safe_water_cn_L
      / (
        1
        + math.exp(
          -Safe_water_cn_k
          * ((mdf[rowi, idx1 + 2] / UNIT_conv_to_make_base_dmnless) - Safe_water_cn_x0)
        )
      )
      + Safe_water_cn_min
    )

    # Safe_water_rest[region] = Safe_water_rest_L / ( 1 + math.exp ( - Safe_water_rest_k * ( ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) - Safe_water_rest_x0 ) ) ) + Safe_water_rest_min
    idxlhs = fcol_in_mdf["Safe_water_rest"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Safe_water_rest_L
        / (
          1
          + math.exp(
            -Safe_water_rest_k
            * (
              (mdf[rowi, idx1 + j] / UNIT_conv_to_make_base_dmnless)
              - Safe_water_rest_x0
            )
          )
        )
        + Safe_water_rest_min
      )

    # Safe_water[region] = IF_THEN_ELSE ( j==2 , Safe_water_cn , Safe_water_rest )
    idxlhs = fcol_in_mdf["Safe_water"]
    idx1 = fcol_in_mdf["Safe_water_cn"]
    idx2 = fcol_in_mdf["Safe_water_rest"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 2, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # SDG6a_Score[region] = IF_THEN_ELSE ( Safe_water < SDG6a_threshold_red , 0 , IF_THEN_ELSE ( Safe_water < SDG6a_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG6a_Score"]
    idx1 = fcol_in_mdf["Safe_water"]
    idx2 = fcol_in_mdf["Safe_water"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG6a_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG6a_threshold_green, 0.5, 1),   )

    # Safe_sanitation[region] = Safe_sanitation_L / ( 1 + math.exp ( - Safe_sanitation_k * ( ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) - Safe_sanitation_x0 ) ) ) + Safe_sanitation_min
    idxlhs = fcol_in_mdf["Safe_sanitation"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Safe_sanitation_L
        / (
          1
          + math.exp(
            -Safe_sanitation_k
            * (
              (mdf[rowi, idx1 + j] / UNIT_conv_to_make_base_dmnless)
              - Safe_sanitation_x0
            )
          )
        )
        + Safe_sanitation_min
      )

    # SDG6b_Score[region] = IF_THEN_ELSE ( Safe_sanitation < SDG6b_threshold_red , 0 , IF_THEN_ELSE ( Safe_sanitation < SDG6b_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG6b_Score"]
    idx1 = fcol_in_mdf["Safe_sanitation"]
    idx2 = fcol_in_mdf["Safe_sanitation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG6b_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG6b_threshold_green, 0.5, 1),   )

    # SDG_6_score[region] = ( SDG6a_Score[region] + SDG6b_Score[region] ) / 2
    idxlhs = fcol_in_mdf["SDG_6_score"]
    idx1 = fcol_in_mdf["SDG6a_Score"]
    idx2 = fcol_in_mdf["SDG6b_Score"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]) / 2

    # SDG_7_Score[region] = IF_THEN_ELSE ( Access_to_electricity < SDG_7_threshold_red , 0 , IF_THEN_ELSE ( Access_to_electricity < SDG_7_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG_7_Score"]
    idx1 = fcol_in_mdf["Access_to_electricity"]
    idx2 = fcol_in_mdf["Access_to_electricity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG_7_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG_7_threshold_green, 0.5, 1),   )

    # Indicated_cost_of_capital_for_secured_debt[region] = Short_term_interest_rate[region] + Normal_bank_operating_margin
    idxlhs = fcol_in_mdf["Indicated_cost_of_capital_for_secured_debt"]
    idx1 = fcol_in_mdf["Short_term_interest_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Normal_bank_operating_margin

    # Cost_of_capital_for_secured_debt[region] = SMOOTHI ( Indicated_cost_of_capital_for_secured_debt[region] , Finance_sector_response_time_to_central_bank , Indicated_cost_of_capital_for_secured_debt[region] )
    idx1 = fcol_in_mdf["Cost_of_capital_for_secured_debt"]
    idx2 = fcol_in_mdf["Indicated_cost_of_capital_for_secured_debt"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Finance_sector_response_time_to_central_bank
        * dt
      )

    # Cost_of_capital_for_worker_borrowing[region] = Cost_of_capital_for_secured_debt[region] + Normal_consumer_credit_risk_margin
    idxlhs = fcol_in_mdf["Cost_of_capital_for_worker_borrowing"]
    idx1 = fcol_in_mdf["Cost_of_capital_for_secured_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Normal_consumer_credit_risk_margin

    # Cost_of_capital_for_worker_borrowing_smoothed[region] = SMOOTH ( Cost_of_capital_for_worker_borrowing[region] , Time_to_smooth_cost_of_capital_for_workers )
    idx1 = fcol_in_mdf["Cost_of_capital_for_worker_borrowing_smoothed"]
    idx2 = fcol_in_mdf["Cost_of_capital_for_worker_borrowing"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_cost_of_capital_for_workers
        * dt
      )

    # Worker_debt_defaulting_N_yrs_ago[region] = SMOOTHI ( Worker_debt_defaulting[region] , Time_for_defaulting_to_impact_cost_of_capital , 0 )
    idx1 = fcol_in_mdf["Worker_debt_defaulting_N_yrs_ago"]
    idx2 = fcol_in_mdf["Worker_debt_defaulting"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_defaulting_to_impact_cost_of_capital
        * dt
      )

    # Worker_default_ratio[region] = Worker_debt_defaulting_N_yrs_ago[region] / Worker_income_after_tax[region]
    idxlhs = fcol_in_mdf["Worker_default_ratio"]
    idx1 = fcol_in_mdf["Worker_debt_defaulting_N_yrs_ago"]
    idx2 = fcol_in_mdf["Worker_income_after_tax"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing[region] = WITH LOOKUP ( Worker_default_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 1.04 ) , ( 0.5 , 1.1 ) , ( 0.75 , 1.3 ) , ( 1 , 1.6 ) , ( 1.5 , 2.5 ) , ( 2 , 4 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Worker_default_ratio"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Worker_interest_payment_obligation[region] = Workers_debt[region] * Cost_of_capital_for_worker_borrowing_smoothed[region] * Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing[region]
    idxlhs = fcol_in_mdf["Worker_interest_payment_obligation"]
    idx1 = fcol_in_mdf["Workers_debt"]
    idx2 = fcol_in_mdf["Cost_of_capital_for_worker_borrowing_smoothed"]
    idx3 = fcol_in_mdf["Effect_of_defaulting_on_debt_obligations_on_cost_of_capital_for_worker_borrowing"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * mdf[rowi, idx3 + j]
      )

    # Max_workers_debt_burden[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2 ) , ( 1990 , 3 ) , ( 2000 , 1 ) , ( 2010 , 3 ) , ( 2020 , 2.4 ) , ( 2050 , 2 ) ) ) Max_workers_debt_burden[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 0.5 ) , ( 2000 , 0.65 ) , ( 2010 , 0.7 ) , ( 2020 , 0.7 ) , ( 2050 , 0.7 ) ) ) Max_workers_debt_burden[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 2.5 ) , ( 2000 , 3 ) , ( 2010 , 4 ) , ( 2020 , 5 ) , ( 2050 , 3 ) ) ) Max_workers_debt_burden[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 0.5 ) , ( 2000 , 1 ) , ( 2010 , 1.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 1 ) , ( 2000 , 2 ) , ( 2010 , 2.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.1 ) , ( 1990 , 2 ) , ( 2000 , 1 ) , ( 2010 , 1.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 3 ) , ( 1990 , 5 ) , ( 2000 , 4 ) , ( 2010 , 4.5 ) , ( 2020 , 5 ) , ( 2050 , 4 ) ) ) Max_workers_debt_burden[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.1 ) , ( 1990 , 1.5 ) , ( 2000 , 0.1 ) , ( 2010 , 1.5 ) , ( 2020 , 2 ) , ( 2050 , 1.5 ) ) ) Max_workers_debt_burden[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2 ) , ( 1990 , 3 ) , ( 2000 , 3 ) , ( 2010 , 4.5 ) , ( 2020 , 3 ) , ( 2050 , 2 ) ) ) Max_workers_debt_burden[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.5 ) , ( 1990 , 2.5 ) , ( 2000 , 2 ) , ( 2010 , 1.5 ) , ( 2020 , 2.5 ) , ( 2050 , 1.5 ) ) )
    tabidx = ftab_in_d_table["Max_workers_debt_burden"]  # fetch the correct table
    idx2 = fcol_in_mdf["Max_workers_debt_burden"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # Indicated_max_workers_debt[region] = Worker_income[region] * Max_workers_debt_burden[region]
    idxlhs = fcol_in_mdf["Indicated_max_workers_debt"]
    idx1 = fcol_in_mdf["Worker_income"]
    idx2 = fcol_in_mdf["Max_workers_debt_burden"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Smoothed_max_workers_debt[region] = SMOOTH ( Indicated_max_workers_debt[region] , Time_for_max_debt_debt_burden_to_affect_max_debt )
    idx1 = fcol_in_mdf["Smoothed_max_workers_debt"]
    idx2 = fcol_in_mdf["Indicated_max_workers_debt"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_max_debt_debt_burden_to_affect_max_debt
        * dt
      )

    # Workers_taking_on_new_debt[region] = MAX ( 0 , ( Smoothed_max_workers_debt[region] - Workers_debt[region] ) / Worker_drawdown_period )
    idxlhs = fcol_in_mdf["Workers_taking_on_new_debt"]
    idx1 = fcol_in_mdf["Smoothed_max_workers_debt"]
    idx2 = fcol_in_mdf["Workers_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0, (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / Worker_drawdown_period
      )

    # Worker_cash_available_to_meet_loan_obligations[region] = ( Worker_income_after_tax[region] + Workers_taking_on_new_debt[region] ) * Fraction_by_law_or_custom_left_for_surviving
    idxlhs = fcol_in_mdf["Worker_cash_available_to_meet_loan_obligations"]
    idx1 = fcol_in_mdf["Worker_income_after_tax"]
    idx2 = fcol_in_mdf["Workers_taking_on_new_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]
      ) * Fraction_by_law_or_custom_left_for_surviving

    # Worker_debt_repayment_obligation[region] = Workers_debt[region] / Workers_payback_period
    idxlhs = fcol_in_mdf["Worker_debt_repayment_obligation"]
    idx1 = fcol_in_mdf["Workers_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Workers_payback_period

    # Worker_loan_repayment_obligations[region] = Worker_interest_payment_obligation[region] + Worker_debt_repayment_obligation[region]
    idxlhs = fcol_in_mdf["Worker_loan_repayment_obligations"]
    idx1 = fcol_in_mdf["Worker_interest_payment_obligation"]
    idx2 = fcol_in_mdf["Worker_debt_repayment_obligation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Fraction_of_worker_loan_obligations_met[region] = MIN ( 1 , Worker_cash_available_to_meet_loan_obligations[region] / Worker_loan_repayment_obligations[region] )
    idxlhs = fcol_in_mdf["Fraction_of_worker_loan_obligations_met"]
    idx1 = fcol_in_mdf["Worker_cash_available_to_meet_loan_obligations"]
    idx2 = fcol_in_mdf["Worker_loan_repayment_obligations"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(1, mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j])

    # Worker_interest_payment_obligation_met[region] = Worker_interest_payment_obligation[region] * Fraction_of_worker_loan_obligations_met[region]
    idxlhs = fcol_in_mdf["Worker_interest_payment_obligation_met"]
    idx1 = fcol_in_mdf["Worker_interest_payment_obligation"]
    idx2 = fcol_in_mdf["Fraction_of_worker_loan_obligations_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Workers_debt_payback[region] = Worker_debt_repayment_obligation[region] * Fraction_of_worker_loan_obligations_met[region]
    idxlhs = fcol_in_mdf["Workers_debt_payback"]
    idx1 = fcol_in_mdf["Worker_debt_repayment_obligation"]
    idx2 = fcol_in_mdf["Fraction_of_worker_loan_obligations_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Worker_cashflow_to_owners[region] = Worker_interest_payment_obligation_met[region] + Workers_debt_payback[region] - Workers_taking_on_new_debt[region]
    idxlhs = fcol_in_mdf["Worker_cashflow_to_owners"]
    idx1 = fcol_in_mdf["Worker_interest_payment_obligation_met"]
    idx2 = fcol_in_mdf["Workers_debt_payback"]
    idx3 = fcol_in_mdf["Workers_taking_on_new_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] - mdf[rowi, idx3 + j]
      )

    # Disposable_income_pp_post_tax_pre_loan_impact[region] = ( Worker_cash_inflow_seasonally_adjusted[region] - Worker_cashflow_to_owners[region] ) / Population[region]
    idxlhs = fcol_in_mdf["Disposable_income_pp_post_tax_pre_loan_impact"]
    idx1 = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Worker_cashflow_to_owners"]
    idx3 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / mdf[ rowi, idx3 + j
      ]

    # SDG_8_Score[region] = IF_THEN_ELSE ( Disposable_income_pp_post_tax_pre_loan_impact < SDG_8_threshold_red , 0 , IF_THEN_ELSE ( Disposable_income_pp_post_tax_pre_loan_impact < SDG_8_threshold_green , 0.5 , 1 ) )
    idxlhs = fcol_in_mdf["SDG_8_Score"]
    idx1 = fcol_in_mdf["Disposable_income_pp_post_tax_pre_loan_impact"]
    idx2 = fcol_in_mdf["Disposable_income_pp_post_tax_pre_loan_impact"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG_8_threshold_red,     0,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG_8_threshold_green, 0.5, 1),   )

    # Carbon_intensity[region] = ( Total_CO2_emissions[region] - Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture[region] ) / GDP_USED[region] * UNIT_conv_to_tCO2_pr_USD
    idxlhs = fcol_in_mdf["Carbon_intensity"]
    idx1 = fcol_in_mdf["Total_CO2_emissions"]
    idx2 = fcol_in_mdf["Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture"
    ]
    idx3 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])
        / mdf[rowi, idx3 + j]
        * UNIT_conv_to_tCO2_pr_USD
      )

    # SDG_9_Score[region] = IF_THEN_ELSE ( Carbon_intensity < SDG_9_threshold_green , 1 , IF_THEN_ELSE ( Carbon_intensity < SDG_9_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_9_Score"]
    idx1 = fcol_in_mdf["Carbon_intensity"]
    idx2 = fcol_in_mdf["Carbon_intensity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG_9_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG_9_threshold_red, 0.5, 0),   )

    # Labour_share_of_GDP[region] = Worker_income_after_tax[region] / ( Worker_income_after_tax[region] + Owner_income_after_tax_but_before_lending_transactions[region] )
    idxlhs = fcol_in_mdf["Labour_share_of_GDP"]
    idx1 = fcol_in_mdf["Worker_income_after_tax"]
    idx2 = fcol_in_mdf["Worker_income_after_tax"]
    idx3 = fcol_in_mdf["Owner_income_after_tax_but_before_lending_transactions"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # SDG_10_Score[region] = IF_THEN_ELSE ( Labour_share_of_GDP > SDG_10_threshold_green , 1 , IF_THEN_ELSE ( Labour_share_of_GDP > SDG_10_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_10_Score"]
    idx1 = fcol_in_mdf["Labour_share_of_GDP"]
    idx2 = fcol_in_mdf["Labour_share_of_GDP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] > SDG_10_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2 + j] > SDG_10_threshold_red, 0.5, 0),   )

    # Energy_footprint_pp[region] = ( Total_CO2_emissions[region] ) / Population[region] * UNIT_conv_to_t_ppy
    idxlhs = fcol_in_mdf["Energy_footprint_pp"]
    idx1 = fcol_in_mdf["Total_CO2_emissions"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j]) / mdf[rowi, idx2 + j] * UNIT_conv_to_t_ppy
      )

    # SDG_11_Score[region] = IF_THEN_ELSE ( Energy_footprint_pp < SDG_11_threshold_green , 1 , IF_THEN_ELSE ( Energy_footprint_pp < SDG_11_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_11_Score"]
    idx1 = fcol_in_mdf["Energy_footprint_pp"]
    idx2 = fcol_in_mdf["Energy_footprint_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < SDG_11_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2 + j] < SDG_11_threshold_red, 0.5, 0),   )

    # Food_footprint[region] = Nitrogen_syn_use[region] / Population[region]
    idxlhs = fcol_in_mdf["Food_footprint"]
    idx1 = fcol_in_mdf["Nitrogen_syn_use"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Food_footprint_kgN_ppy[region] = Food_footprint[region] * UNIT_conv_to_kgN
    idxlhs = fcol_in_mdf["Food_footprint_kgN_ppy"]
    idx1 = fcol_in_mdf["Food_footprint"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * UNIT_conv_to_kgN

    # SDG_12_threshold_green_PES = SDG12_global_green_threshold / Global_population * UNIT_conv_to_kgN
    idxlhs = fcol_in_mdf["SDG_12_threshold_green_PES"]
    idx1 = fcol_in_mdf["Global_population"]
    mdf[rowi, idxlhs] = (
      SDG12_global_green_threshold / mdf[rowi, idx1] * UNIT_conv_to_kgN
    )

    # SDG_12_threshold_red_PES = SDG12_global_red_threshold / Global_population * UNIT_conv_to_kgN
    idxlhs = fcol_in_mdf["SDG_12_threshold_red_PES"]
    idx1 = fcol_in_mdf["Global_population"]
    mdf[rowi, idxlhs] = SDG12_global_red_threshold / mdf[rowi, idx1] * UNIT_conv_to_kgN

    # SDG_12_Score[region] = IF_THEN_ELSE ( Food_footprint_kgN_ppy < SDG_12_threshold_green_PES , 1 , IF_THEN_ELSE ( Food_footprint_kgN_ppy < SDG_12_threshold_red_PES , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_12_Score"]
    idx1 = fcol_in_mdf["Food_footprint_kgN_ppy"]
    idx2 = fcol_in_mdf["SDG_12_threshold_green_PES"]
    idx3 = fcol_in_mdf["Food_footprint_kgN_ppy"]
    idx4 = fcol_in_mdf["SDG_12_threshold_red_PES"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < mdf[rowi, idx2],     1,     IF_THEN_ELSE(mdf[rowi, idx3 + j] < mdf[rowi, idx4], 0.5, 0),   )

    # SDG_13_Score[region] = IF_THEN_ELSE ( Temp_surface_anomaly_compared_to_1850_degC < SDG_13_threshold_green , 1 , IF_THEN_ELSE ( Temp_surface_anomaly_compared_to_1850_degC < SDG_13_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_13_Score"]
    idx1 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    idx2 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1] < SDG_13_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2] < SDG_13_threshold_red, 0.5, 0),   )

    # SDG_14_Score[region] = IF_THEN_ELSE ( pH_in_surface > SDG_14_threshold_green , 1 , IF_THEN_ELSE ( pH_in_surface > SDG_14_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_14_Score"]
    idx1 = fcol_in_mdf["pH_in_surface"]
    idx2 = fcol_in_mdf["pH_in_surface"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1] > SDG_14_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2] > SDG_14_threshold_red, 0.5, 0),   )

    # SDG_15_Score[region] = IF_THEN_ELSE ( TROP_with_normal_cover > SDG_15_threshold_green , 1 , IF_THEN_ELSE ( TROP_with_normal_cover > SDG_15_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_15_Score"]
    idx1 = fcol_in_mdf["TROP_with_normal_cover"]
    idx2 = fcol_in_mdf["TROP_with_normal_cover"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1] > SDG_15_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2] > SDG_15_threshold_red, 0.5, 0),   )

    # SDG_16_Score[region] = IF_THEN_ELSE ( Public_services_pp > SDG_16_threshold_green , 1 , IF_THEN_ELSE ( Public_services_pp > SDG_16_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_16_Score"]
    idx1 = fcol_in_mdf["Public_services_pp"]
    idx2 = fcol_in_mdf["Public_services_pp"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] > SDG_16_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2 + j] > SDG_16_threshold_red, 0.5, 0),   )

    # Social_trust_init_is_1[region] = Social_trust[region] / Social_trust_in_1980
    idxlhs = fcol_in_mdf["Social_trust_init_is_1"]
    idx1 = fcol_in_mdf["Social_trust"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Social_trust_in_1980

    # SDG_17_Score[region] = IF_THEN_ELSE ( Social_trust_init_is_1 > SDG_17_threshold_green , 1 , IF_THEN_ELSE ( Social_trust_init_is_1 > SDG_17_threshold_red , 0.5 , 0 ) )
    idxlhs = fcol_in_mdf["SDG_17_Score"]
    idx1 = fcol_in_mdf["Social_trust_init_is_1"]
    idx2 = fcol_in_mdf["Social_trust_init_is_1"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] > SDG_17_threshold_green,     1,     IF_THEN_ELSE(mdf[rowi, idx2 + j] > SDG_17_threshold_red, 0.5, 0),   )

    # All_SDG_Scores[region] = SDG1_Score[region] + SDG_2_Score[region] + SDG_3_Score[region] + SDG4_Score[region] + SDG_5_Score[region] + SDG_6_score[region] + SDG_7_Score[region] + SDG_8_Score[region] + SDG_9_Score[region] + SDG_10_Score[region] + SDG_11_Score[region] + SDG_12_Score[region] + SDG_13_Score[region] + SDG_14_Score[region] + SDG_15_Score[region] + SDG_16_Score[region] + SDG_17_Score[region]
    idxlhs = fcol_in_mdf["All_SDG_Scores"]
    idx1 = fcol_in_mdf["SDG1_Score"]
    idx2 = fcol_in_mdf["SDG_2_Score"]
    idx3 = fcol_in_mdf["SDG_3_Score"]
    idx4 = fcol_in_mdf["SDG4_Score"]
    idx5 = fcol_in_mdf["SDG_5_Score"]
    idx6 = fcol_in_mdf["SDG_6_score"]
    idx7 = fcol_in_mdf["SDG_7_Score"]
    idx8 = fcol_in_mdf["SDG_8_Score"]
    idx9 = fcol_in_mdf["SDG_9_Score"]
    idx10 = fcol_in_mdf["SDG_10_Score"]
    idx11 = fcol_in_mdf["SDG_11_Score"]
    idx12 = fcol_in_mdf["SDG_12_Score"]
    idx13 = fcol_in_mdf["SDG_13_Score"]
    idx14 = fcol_in_mdf["SDG_14_Score"]
    idx15 = fcol_in_mdf["SDG_15_Score"]
    idx16 = fcol_in_mdf["SDG_16_Score"]
    idx17 = fcol_in_mdf["SDG_17_Score"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
        + mdf[rowi, idx7 + j]
        + mdf[rowi, idx8 + j]
        + mdf[rowi, idx9 + j]
        + mdf[rowi, idx10 + j]
        + mdf[rowi, idx11 + j]
        + mdf[rowi, idx12 + j]
        + mdf[rowi, idx13 + j]
        + mdf[rowi, idx14 + j]
        + mdf[rowi, idx15 + j]
        + mdf[rowi, idx16 + j]
        + mdf[rowi, idx17 + j]
      )

    # GRASS_potential_living_biomass_GtBiomass = ( GRASS_potential_area_Mkm2 - GRASS_deforested_Mkm2 ) * GRASS_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["GRASS_potential_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["GRASS_deforested_Mkm2"]
    idx3 = fcol_in_mdf["GRASS_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2])
      * mdf[rowi, idx3]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # GRASS_potential_less_actual_living_biomass_GtBiomass = GRASS_potential_living_biomass_GtBiomass - GRASS_Living_biomass_GtBiomass
    idxlhs = fcol_in_mdf["GRASS_potential_less_actual_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["GRASS_potential_living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["GRASS_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # GRASS_biomass_new_growing = GRASS_potential_less_actual_living_biomass_GtBiomass / GRASS_Speed_of_regrowth_yr
    idxlhs = fcol_in_mdf["GRASS_biomass_new_growing"]
    idx1 = fcol_in_mdf["GRASS_potential_less_actual_living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / GRASS_Speed_of_regrowth_yr

    # CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py = GRASS_biomass_new_growing * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py"]
    idx1 = fcol_in_mdf["GRASS_biomass_new_growing"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # NF_potential_living_biomass_GtBiomass = ( NF_potential_area_Mkm2 - NF_area_deforested_Mkm2 ) * NF_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["NF_potential_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    idx3 = fcol_in_mdf["NF_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2])
      * mdf[rowi, idx3]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # NF_potential_less_actual_living_biomass_GtBiomass = NF_potential_living_biomass_GtBiomass - NF_Living_biomass_GtBiomass
    idxlhs = fcol_in_mdf["NF_potential_less_actual_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["NF_potential_living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["NF_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # NF_biomass_new_growing = NF_potential_less_actual_living_biomass_GtBiomass / NF_Speed_of_regrowth_yr
    idxlhs = fcol_in_mdf["NF_biomass_new_growing"]
    idx1 = fcol_in_mdf["NF_potential_less_actual_living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / NF_Speed_of_regrowth_yr

    # CO2_flux_from_atm_to_NF_for_new_growth_GtC_py = NF_biomass_new_growing * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flux_from_atm_to_NF_for_new_growth_GtC_py"]
    idx1 = fcol_in_mdf["NF_biomass_new_growing"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # TROP_potential_living_biomass_GtBiomass = ( TROP_potential_area_Mkm2 - TROP_area_deforested ) * TROP_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TROP_potential_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["TROP_area_deforested"]
    idx3 = fcol_in_mdf["TROP_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2])
      * mdf[rowi, idx3]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TROP_potential_less_actual_living_biomass_GtBiomass = TROP_potential_living_biomass_GtBiomass - TROP_Living_biomass_GtBiomass
    idxlhs = fcol_in_mdf["TROP_potential_less_actual_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["TROP_potential_living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["TROP_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # TROP_biomass_new_growing = TROP_potential_less_actual_living_biomass_GtBiomass / TROP_Speed_of_regrowth_yr
    idxlhs = fcol_in_mdf["TROP_biomass_new_growing"]
    idx1 = fcol_in_mdf["TROP_potential_less_actual_living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / TROP_Speed_of_regrowth_yr

    # CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py = TROP_biomass_new_growing * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py"]
    idx1 = fcol_in_mdf["TROP_biomass_new_growing"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 = TUNDRA_living_biomass_densitiy_at_initial_time_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
    idxlhs = fcol_in_mdf["TUNDRA_living_biomass_densitiy_tBiomass_pr_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    mdf[rowi, idxlhs] = (
      TUNDRA_living_biomass_densitiy_at_initial_time_tBiomass_pr_km2
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
    )

    # TUNDRA_potential_living_biomass_GtBiomass = ( Tundra_potential_area_Mkm2 - TUNDRA_deforested_Mkm2 ) * TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TUNDRA_potential_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["Tundra_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["TUNDRA_deforested_Mkm2"]
    idx3 = fcol_in_mdf["TUNDRA_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] - mdf[rowi, idx2])
      * mdf[rowi, idx3]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TUNDRA_potential_less_actual_living_biomass_GtBiomass = TUNDRA_potential_living_biomass_GtBiomass - TUNDRA_Living_biomass
    idxlhs = fcol_in_mdf["TUNDRA_potential_less_actual_living_biomass_GtBiomass"]
    idx1 = fcol_in_mdf["TUNDRA_potential_living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["TUNDRA_Living_biomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # TUNDRA_biomass_new_growing = TUNDRA_potential_less_actual_living_biomass_GtBiomass / TUNDRA_Speed_of_regrowth_yr
    idxlhs = fcol_in_mdf["TUNDRA_biomass_new_growing"]
    idx1 = fcol_in_mdf["TUNDRA_potential_less_actual_living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / TUNDRA_Speed_of_regrowth_yr

    # CO2_flux_from_atm_to_TUNDRA_for_new_growth = TUNDRA_biomass_new_growing * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flux_from_atm_to_TUNDRA_for_new_growth"]
    idx1 = fcol_in_mdf["TUNDRA_biomass_new_growing"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # Flow_from_atm_to_biomass = CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py + CO2_flux_from_atm_to_NF_for_new_growth_GtC_py + CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py + CO2_flux_from_atm_to_TUNDRA_for_new_growth
    idxlhs = fcol_in_mdf["Flow_from_atm_to_biomass"]
    idx1 = fcol_in_mdf["CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py"]
    idx2 = fcol_in_mdf["CO2_flux_from_atm_to_NF_for_new_growth_GtC_py"]
    idx3 = fcol_in_mdf["CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py"]
    idx4 = fcol_in_mdf["CO2_flux_from_atm_to_TUNDRA_for_new_growth"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    )

    # GRASS_Biomass_in_construction_material_being_burnt = GRASS_Biomass_locked_in_construction_material_GtBiomass / GRASS_Avg_life_of_building_yr * GRASS_Fraction_of_construction_waste_burned_0_to_1
    idxlhs = fcol_in_mdf["GRASS_Biomass_in_construction_material_being_burnt"]
    idx1 = fcol_in_mdf["GRASS_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / GRASS_Avg_life_of_building_yr
      * GRASS_Fraction_of_construction_waste_burned_0_to_1
    )

    # GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( GRASS_being_deforested_Mkm2_py + GRASS_burning_Mkm2_py + GRASS_being_harvested_Mkm2_py ) * GRASS_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx1 = fcol_in_mdf["GRASS_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["GRASS_burning_Mkm2_py"]
    idx3 = fcol_in_mdf["GRASS_being_harvested_Mkm2_py"]
    idx4 = fcol_in_mdf["GRASS_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3])
      * mdf[rowi, idx4]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # CO2_flow_from_GRASS_to_atmosphere_GtC_py = ( GRASS_Biomass_in_construction_material_being_burnt + GRASS_Dead_biomass_decomposing + GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + GRASS_DeadB_SOM_being_lost_due_to_deforestation + GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting + GRASS_soil_degradation_from_forest_fires + GRASS_runoff ) * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flow_from_GRASS_to_atmosphere_GtC_py"]
    idx1 = fcol_in_mdf["GRASS_Biomass_in_construction_material_being_burnt"]
    idx2 = fcol_in_mdf["GRASS_Dead_biomass_decomposing"]
    idx3 = fcol_in_mdf["GRASS_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_deforestation"]
    idx5 = fcol_in_mdf["GRASS_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx6 = fcol_in_mdf["GRASS_soil_degradation_from_forest_fires"]
    idx7 = fcol_in_mdf["GRASS_runoff"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
      + mdf[rowi, idx7]
    ) * Carbon_per_biomass

    # CO2_flux_GRASS_to_atm_GtC_py = CO2_flow_from_GRASS_to_atmosphere_GtC_py
    idxlhs = fcol_in_mdf["CO2_flux_GRASS_to_atm_GtC_py"]
    idx1 = fcol_in_mdf["CO2_flow_from_GRASS_to_atmosphere_GtC_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # NF_Biomass_in_construction_material_being_burnt = NF_Biomass_locked_in_construction_material_GtBiomass / NF_Avg_life_of_building_yr * NF_Fraction_of_construction_waste_burned_0_to_1
    idxlhs = fcol_in_mdf["NF_Biomass_in_construction_material_being_burnt"]
    idx1 = fcol_in_mdf["NF_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / NF_Avg_life_of_building_yr
      * NF_Fraction_of_construction_waste_burned_0_to_1
    )

    # NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( NF_being_deforested_Mkm2_py + NF_burning_Mkm2_py + NF_being_harvested_by_clear_cutting_Mkm2_py + NF_being_harvested_normally_Mkm2_py ) * NF_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx1 = fcol_in_mdf["NF_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["NF_burning_Mkm2_py"]
    idx3 = fcol_in_mdf["NF_being_harvested_by_clear_cutting_Mkm2_py"]
    idx4 = fcol_in_mdf["NF_being_harvested_normally_Mkm2_py"]
    idx5 = fcol_in_mdf["NF_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4])
      * mdf[rowi, idx5]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # CO2_flow_from_NF_to_atmosphere_GtC_py = ( NF_Biomass_in_construction_material_being_burnt + NF_Dead_biomass_decomposing + NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + NF_DeadB_SOM_being_lost_due_to_deforestation + NF_DeadB_SOM_being_lost_due_to_energy_harvesting + NF_soil_degradation_from_clear_cutting + NF_soil_degradation_from_forest_fires + NF_runoff ) * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flow_from_NF_to_atmosphere_GtC_py"]
    idx1 = fcol_in_mdf["NF_Biomass_in_construction_material_being_burnt"]
    idx2 = fcol_in_mdf["NF_Dead_biomass_decomposing"]
    idx3 = fcol_in_mdf["NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_deforestation"]
    idx5 = fcol_in_mdf["NF_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx6 = fcol_in_mdf["NF_soil_degradation_from_clear_cutting"]
    idx7 = fcol_in_mdf["NF_soil_degradation_from_forest_fires"]
    idx8 = fcol_in_mdf["NF_runoff"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
      + mdf[rowi, idx7]
      + mdf[rowi, idx8]
    ) * Carbon_per_biomass

    # CO2_flux_NF_to_atm_GtC_py = CO2_flow_from_NF_to_atmosphere_GtC_py
    idxlhs = fcol_in_mdf["CO2_flux_NF_to_atm_GtC_py"]
    idx1 = fcol_in_mdf["CO2_flow_from_NF_to_atmosphere_GtC_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # TROP_Biomass_in_construction_material_being_burnt = TROP_Biomass_locked_in_construction_material_GtBiomass / TROP_Avg_life_of_building_yr * TROP_Fraction_of_construction_waste_burned_0_to_1
    idxlhs = fcol_in_mdf["TROP_Biomass_in_construction_material_being_burnt"]
    idx1 = fcol_in_mdf["TROP_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / TROP_Avg_life_of_building_yr
      * TROP_Fraction_of_construction_waste_burned_0_to_1
    )

    # TROP_NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( TROP_being_deforested_Mkm2_py + TROP_burning + TROP_being_harvested_by_clear_cutting + TROP_being_harvested_normally ) * TROP_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TROP_NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx1 = fcol_in_mdf["TROP_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["TROP_burning"]
    idx3 = fcol_in_mdf["TROP_being_harvested_by_clear_cutting"]
    idx4 = fcol_in_mdf["TROP_being_harvested_normally"]
    idx5 = fcol_in_mdf["TROP_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4])
      * mdf[rowi, idx5]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # CO2_flow_from_TROP_to_atmosphere_GtC_py = ( TROP_Biomass_in_construction_material_being_burnt + TROP_Dead_biomass_decomposing + TROP_NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + TROP_DeadB_SOM_being_lost_due_to_deforestation + TROP_DeadB_SOM_being_lost_due_to_energy_harvesting + TROP_soil_degradation_from_clear_cutting + TROP_soil_degradation_from_forest_fires + TROP_runoff ) * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flow_from_TROP_to_atmosphere_GtC_py"]
    idx1 = fcol_in_mdf["TROP_Biomass_in_construction_material_being_burnt"]
    idx2 = fcol_in_mdf["TROP_Dead_biomass_decomposing"]
    idx3 = fcol_in_mdf["TROP_NF_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_deforestation"]
    idx5 = fcol_in_mdf["TROP_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx6 = fcol_in_mdf["TROP_soil_degradation_from_clear_cutting"]
    idx7 = fcol_in_mdf["TROP_soil_degradation_from_forest_fires"]
    idx8 = fcol_in_mdf["TROP_runoff"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
      + mdf[rowi, idx7]
      + mdf[rowi, idx8]
    ) * Carbon_per_biomass

    # CO2_flux_TROP_to_atm_GtC_py = CO2_flow_from_TROP_to_atmosphere_GtC_py
    idxlhs = fcol_in_mdf["CO2_flux_TROP_to_atm_GtC_py"]
    idx1 = fcol_in_mdf["CO2_flow_from_TROP_to_atmosphere_GtC_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # TUNDRA_Biomass_in_construction_material_being_burnt = TUNDRA_Biomass_locked_in_construction_material_GtBiomass / TUNDRA_Avg_life_of_building_yr * TUNDRA_Fraction_of_construction_waste_burned_0_to_1
    idxlhs = fcol_in_mdf["TUNDRA_Biomass_in_construction_material_being_burnt"]
    idx1 = fcol_in_mdf["TUNDRA_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / TUNDRA_Avg_life_of_building_yr
      * TUNDRA_Fraction_of_construction_waste_burned_0_to_1
    )

    # TUNDRA_Dead_biomass_decomposing = TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TUNDRA_Time_to_decompose_undisturbed_dead_biomass_yr
    idxlhs = fcol_in_mdf["TUNDRA_Dead_biomass_decomposing"]
    idx1 = fcol_in_mdf["TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / TUNDRA_Time_to_decompose_undisturbed_dead_biomass_yr
    )

    # TUNDRA_with_normal_cover_Mkm2 = Tundra_potential_area_Mkm2 - TUNDRA_area_burnt_Mkm2 - TUNDRA_deforested_Mkm2 - TUNDRA_area_harvested_Mkm2
    idxlhs = fcol_in_mdf["TUNDRA_with_normal_cover_Mkm2"]
    idx1 = fcol_in_mdf["Tundra_potential_area_Mkm2"]
    idx2 = fcol_in_mdf["TUNDRA_area_burnt_Mkm2"]
    idx3 = fcol_in_mdf["TUNDRA_deforested_Mkm2"]
    idx4 = fcol_in_mdf["TUNDRA_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] - mdf[rowi, idx2] - mdf[rowi, idx3] - mdf[rowi, idx4]
    )

    # TUNDRA_being_deforested_Mkm2_py = TUNDRA_with_normal_cover_Mkm2 * Fraction_TUNDRA_being_deforested_1_py
    idxlhs = fcol_in_mdf["TUNDRA_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["TUNDRA_with_normal_cover_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Fraction_TUNDRA_being_deforested_1_py

    # TUNDRA_burning_Mkm2_py = TUNDRA_with_normal_cover_Mkm2 * Effect_of_temperature_on_fire_incidence * TUNDRA_Normal_fire_incidence_fraction_py / 100
    idxlhs = fcol_in_mdf["TUNDRA_burning_Mkm2_py"]
    idx1 = fcol_in_mdf["TUNDRA_with_normal_cover_Mkm2"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_fire_incidence"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * mdf[rowi, idx2] * TUNDRA_Normal_fire_incidence_fraction_py / 100
    )

    # Use_of_TUNDRA_biomass_for_energy = Use_of_TUNDRA_for_energy_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_TUNDRA_biomass_for_energy"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_TUNDRA_for_energy_in_2000_GtBiomass
      * mdf[rowi, idx1]
      * UNIT_conversion_1_py
    )

    # TUNDRA_being_harvested_Mkm2_py = Use_of_TUNDRA_biomass_for_energy / TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TUNDRA_being_harvested_Mkm2_py"]
    idx1 = fcol_in_mdf["Use_of_TUNDRA_biomass_for_energy"]
    idx2 = fcol_in_mdf["TUNDRA_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / mdf[rowi, idx2] * UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting = ( TUNDRA_being_deforested_Mkm2_py + TUNDRA_burning_Mkm2_py + TUNDRA_being_harvested_Mkm2_py ) * TUNDRA_living_biomass_densitiy_tBiomass_pr_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx1 = fcol_in_mdf["TUNDRA_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["TUNDRA_burning_Mkm2_py"]
    idx3 = fcol_in_mdf["TUNDRA_being_harvested_Mkm2_py"]
    idx4 = fcol_in_mdf["TUNDRA_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3])
      * mdf[rowi, idx4]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TUNDRA_DeadB_and_SOM_tB_per_km2 = TUNDRA_DeadB_and_SOM_densitiy_at_initial_time_tBiomass_pr_km2 * Effect_of_CO2_on_new_biomass_growth * Effect_of_temperature_on_new_biomass_growth_dmnl
    idxlhs = fcol_in_mdf["TUNDRA_DeadB_and_SOM_tB_per_km2"]
    idx1 = fcol_in_mdf["Effect_of_CO2_on_new_biomass_growth"]
    idx2 = fcol_in_mdf["Effect_of_temperature_on_new_biomass_growth_dmnl"]
    mdf[rowi, idxlhs] = (
      TUNDRA_DeadB_and_SOM_densitiy_at_initial_time_tBiomass_pr_km2
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
    )

    # TUNDRA_DeadB_SOM_being_lost_due_to_deforestation = TUNDRA_being_deforested_Mkm2_py * TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting * TUNDRA_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TUNDRA_DeadB_SOM_being_lost_due_to_deforestation"]
    idx1 = fcol_in_mdf["TUNDRA_being_deforested_Mkm2_py"]
    idx2 = fcol_in_mdf["TUNDRA_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_deforesting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting = TUNDRA_being_harvested_Mkm2_py * TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting * TUNDRA_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    idxlhs = fcol_in_mdf["TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx1 = fcol_in_mdf["TUNDRA_being_harvested_Mkm2_py"]
    idx2 = fcol_in_mdf["TUNDRA_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * TUNDRA_fraction_of_DeadB_and_SOM_being_destroyed_by_energy_harvesting
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
    )

    # TUNDRA_soil_degradation_from_forest_fires = TUNDRA_burning_Mkm2_py * TUNDRA_DeadB_and_SOM_tB_per_km2 / UNIT_conversion_GtBiomass_py_to_Mkm2_py * TUNDRA_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    idxlhs = fcol_in_mdf["TUNDRA_soil_degradation_from_forest_fires"]
    idx1 = fcol_in_mdf["TUNDRA_burning_Mkm2_py"]
    idx2 = fcol_in_mdf["TUNDRA_DeadB_and_SOM_tB_per_km2"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * mdf[rowi, idx2]
      / UNIT_conversion_GtBiomass_py_to_Mkm2_py
      * TUNDRA_fraction_of_DeadB_and_SOM_destroyed_by_natural_fires
    )

    # TUNDRA_runoff = TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass / TUNDRA_runoff_time
    idxlhs = fcol_in_mdf["TUNDRA_runoff"]
    idx1 = fcol_in_mdf["TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / TUNDRA_runoff_time

    # CO2_flow_from_TUNDRA_to_atmosphere = ( TUNDRA_Biomass_in_construction_material_being_burnt + TUNDRA_Dead_biomass_decomposing + TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting + TUNDRA_DeadB_SOM_being_lost_due_to_deforestation + TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting + TUNDRA_soil_degradation_from_forest_fires + TUNDRA_runoff ) * Carbon_per_biomass
    idxlhs = fcol_in_mdf["CO2_flow_from_TUNDRA_to_atmosphere"]
    idx1 = fcol_in_mdf["TUNDRA_Biomass_in_construction_material_being_burnt"]
    idx2 = fcol_in_mdf["TUNDRA_Dead_biomass_decomposing"]
    idx3 = fcol_in_mdf["TUNDRA_biomass_being_lost_from_deforestation_fires_energy_harvesting_and_clear_cutting"
    ]
    idx4 = fcol_in_mdf["TUNDRA_DeadB_SOM_being_lost_due_to_deforestation"]
    idx5 = fcol_in_mdf["TUNDRA_DeadB_SOM_being_lost_due_to_energy_harvesting"]
    idx6 = fcol_in_mdf["TUNDRA_soil_degradation_from_forest_fires"]
    idx7 = fcol_in_mdf["TUNDRA_runoff"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
      + mdf[rowi, idx7]
    ) * Carbon_per_biomass

    # CO2_flux_TUNDRA_to_atm = CO2_flow_from_TUNDRA_to_atmosphere
    idxlhs = fcol_in_mdf["CO2_flux_TUNDRA_to_atm"]
    idx1 = fcol_in_mdf["CO2_flow_from_TUNDRA_to_atmosphere"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Flow_from_biomass_to_atm_Gtc_pr_yr = CO2_flux_GRASS_to_atm_GtC_py + CO2_flux_NF_to_atm_GtC_py + CO2_flux_TROP_to_atm_GtC_py + CO2_flux_TUNDRA_to_atm
    idxlhs = fcol_in_mdf["Flow_from_biomass_to_atm_Gtc_pr_yr"]
    idx1 = fcol_in_mdf["CO2_flux_GRASS_to_atm_GtC_py"]
    idx2 = fcol_in_mdf["CO2_flux_NF_to_atm_GtC_py"]
    idx3 = fcol_in_mdf["CO2_flux_TROP_to_atm_GtC_py"]
    idx4 = fcol_in_mdf["CO2_flux_TUNDRA_to_atm"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    )

    # Land_sink_Net_C_flow_from_atm_to_biomass = Flow_from_atm_to_biomass - Flow_from_biomass_to_atm_Gtc_pr_yr
    idxlhs = fcol_in_mdf["Land_sink_Net_C_flow_from_atm_to_biomass"]
    idx1 = fcol_in_mdf["Flow_from_atm_to_biomass"]
    idx2 = fcol_in_mdf["Flow_from_biomass_to_atm_Gtc_pr_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # Annual_flux_of_C_to_biomass = Land_sink_Net_C_flow_from_atm_to_biomass
    idxlhs = fcol_in_mdf["Annual_flux_of_C_to_biomass"]
    idx1 = fcol_in_mdf["Land_sink_Net_C_flow_from_atm_to_biomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Temp_diff_relevant_for_melting_or_freezing_from_1850 = Temp_surface - ( Temp_surface_1850 - SCALE_converter_zero_C_to_K ) * UNIT_conversion_Celsius_to_Kelvin_C_p_K
    idxlhs = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_from_1850"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      - (Temp_surface_1850 - SCALE_converter_zero_C_to_K)
      * UNIT_conversion_Celsius_to_Kelvin_C_p_K
    )

    # Effect_of_temp_on_melting_or_freezing_glacial_ice = 1 + Slope_temp_vs_glacial_ice_melting * ( ( Temp_diff_relevant_for_melting_or_freezing_from_1850 / Ref_temp_difference_for_glacial_ice_melting_1_degC ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temp_on_melting_or_freezing_glacial_ice"]
    idx1 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_from_1850"]
    mdf[rowi, idxlhs] = 1 + Slope_temp_vs_glacial_ice_melting * (
      (mdf[rowi, idx1] / Ref_temp_difference_for_glacial_ice_melting_1_degC) - 1
    )

    # Heat_in_atmosphere_current_to_initial_ratio = Heat_in_atmosphere_ZJ / Heat_in_atmosphere_in_1850_ZJ
    idxlhs = fcol_in_mdf["Heat_in_atmosphere_current_to_initial_ratio"]
    idx1 = fcol_in_mdf["Heat_in_atmosphere_ZJ"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Heat_in_atmosphere_in_1850_ZJ

    # Effect_of_heat_in_atm_on_melting_ice_cut_off = WITH LOOKUP ( Heat_in_atmosphere_current_to_initial_ratio , ( [ ( 0 , 0 ) - ( 1 , 1 ) ] , ( 0 , 0 ) , ( 0.16 , 0.85 ) , ( 0.5 , 1 ) , ( 1 , 1 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_heat_in_atm_on_melting_ice_cut_off"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Effect_of_heat_in_atm_on_melting_ice_cut_off"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Heat_in_atmosphere_current_to_initial_ratio"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py = Glacial_ice_volume_km3 / Effective_time_to_melt_glacial_ice_at_the_reference_delta_temp * Effect_of_temp_on_melting_or_freezing_glacial_ice * Effect_of_heat_in_atm_on_melting_ice_cut_off
    idxlhs = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx1 = fcol_in_mdf["Glacial_ice_volume_km3"]
    idx2 = fcol_in_mdf["Effect_of_temp_on_melting_or_freezing_glacial_ice"]
    idx3 = fcol_in_mdf["Effect_of_heat_in_atm_on_melting_ice_cut_off"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / Effective_time_to_melt_glacial_ice_at_the_reference_delta_temp
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
    )

    # Annual_glacial_ice_losing_pos_or_gaining_neg = Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * GtIce_vs_km3
    idxlhs = fcol_in_mdf["Annual_glacial_ice_losing_pos_or_gaining_neg"]
    idx1 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * GtIce_vs_km3

    # CCS_contribution_to_GL[region] = ( CCS_policy[region] * 100 - CCS_policy_Min ) / ( CCS_policy_Max - CCS_policy_Min )
    idxlhs = fcol_in_mdf["CCS_contribution_to_GL"]
    idx1 = fcol_in_mdf["CCS_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - CCS_policy_Min) / (
        CCS_policy_Max - CCS_policy_Min
      )

    # Ctax_contribution_to_GL[region] = ( Ctax_policy[region] * 1 - Ctax_policy_Min ) / ( Ctax_policy_Max - Ctax_policy_Min )
    idxlhs = fcol_in_mdf["Ctax_contribution_to_GL"]
    idx1 = fcol_in_mdf["Ctax_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 1 - Ctax_policy_Min) / (
        Ctax_policy_Max - Ctax_policy_Min
      )

    # DAC_contribution_to_GL[region] = ( DAC_policy[region] * 1 - DAC_policy_Min ) / ( DAC_policy_Max - DAC_policy_Min )
    idxlhs = fcol_in_mdf["DAC_contribution_to_GL"]
    idx1 = fcol_in_mdf["DAC_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 1 - DAC_policy_Min) / (
        DAC_policy_Max - DAC_policy_Min
      )

    # FEHC_contribution_to_GL[region] = ( FEHC_policy[region] * 100 - FEHC_policy_Min ) / ( FEHC_policy_Max - FEHC_policy_Min )
    idxlhs = fcol_in_mdf["FEHC_contribution_to_GL"]
    idx1 = fcol_in_mdf["FEHC_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - FEHC_policy_Min) / (
        FEHC_policy_Max - FEHC_policy_Min
      )

    # FLWR_rounds_via_Excel_future[region] = IF_THEN_ELSE ( zeit >= Round3_start , FLWR_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FLWR_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FLWR_R1_via_Excel , FLWR_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FLWR_rounds_via_Excel_future"]
#    print('FLWR_rounds_via_Excel_future - idxlhs '+str(idxlhs))
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FLWR_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FLWR_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FLWR_R1_via_Excel[j], FLWR_policy_Min
          ),     ),   )
#      if j == 1:
#        print(mdf[rowi, idxlhs + j])

    # FLWR_policy_with_RW[region] = FLWR_rounds_via_Excel_future[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
    idxlhs = fcol_in_mdf["FLWR_policy_with_RW"]
    idx1 = fcol_in_mdf["FLWR_rounds_via_Excel_future"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
      )

    # FLWR_pol_div_100[region] = MIN ( FLWR_policy_Max , MAX ( FLWR_policy_Min , FLWR_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["FLWR_pol_div_100"]
    idx1 = fcol_in_mdf["FLWR_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FLWR_policy_Max, max(FLWR_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # FLWR_policy[region] = SMOOTH3 ( FLWR_pol_div_100[region] , FLWR_Time_to_implement_ISPV_goal )
    idxin = fcol_in_mdf["FLWR_pol_div_100"]
    idx2 = fcol_in_mdf["FLWR_policy_2"]
    idx1 = fcol_in_mdf["FLWR_policy_1"]
    idxout = fcol_in_mdf["FLWR_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (FLWR_Time_to_implement_ISPV_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (FLWR_Time_to_implement_ISPV_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (FLWR_Time_to_implement_ISPV_goal / 3)
        * dt
      )
      if j == 1:
        a1 = str(mdf[rowi, idxout + j])
#        print('FLWR_policy zeit='+str(zeit)+' value af='+a1+' idxout='+str(idxout))
        
    # FLWR_contribution_to_GL[region] = ( FLWR_policy[region] * 100 - FLWR_policy_Min ) / ( FLWR_policy_Max - FLWR_policy_Min )
    idxlhs = fcol_in_mdf["FLWR_contribution_to_GL"]
    idx1 = fcol_in_mdf["FLWR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - FLWR_policy_Min) / (
        FLWR_policy_Max - FLWR_policy_Min
      )

    # FTPEE_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , FTPEE_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FTPEE_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FTPEE_R1_via_Excel , FTPEE_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FTPEE_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FTPEE_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FTPEE_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FTPEE_R1_via_Excel[j], FTPEE_policy_Min
          ),     ),   )

    # FTPEE_policy_with_RW[region] = FTPEE_policy_Min + ( FTPEE_rounds_via_Excel[region] - FTPEE_policy_Min ) * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region]
    idxlhs = fcol_in_mdf["FTPEE_policy_with_RW"]
    idx1 = fcol_in_mdf["FTPEE_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (FTPEE_policy_Min
        + (mdf[rowi, idx1 + j] - FTPEE_policy_Min)
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
      )

    # FTPEE_pol_div_100[region] = MIN ( FTPEE_policy_Max , MAX ( FTPEE_policy_Min , FTPEE_policy_with_RW[region] ) ) / 1
    idxlhs = fcol_in_mdf["FTPEE_pol_div_100"]
    idx1 = fcol_in_mdf["FTPEE_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FTPEE_policy_Max, max(FTPEE_policy_Min, mdf[rowi, idx1 + j])) / 1
      )

    # FTPEE_rate_of_change_policy[region] = SMOOTH3 ( FTPEE_pol_div_100[region] , FTPEE_Time_to_implement_goal )
    idxin = fcol_in_mdf["FTPEE_pol_div_100"]
    idx2 = fcol_in_mdf["FTPEE_rate_of_change_policy_2"]
    idx1 = fcol_in_mdf["FTPEE_rate_of_change_policy_1"]
    idxout = fcol_in_mdf["FTPEE_rate_of_change_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (FTPEE_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (FTPEE_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (FTPEE_Time_to_implement_goal / 3)
        * dt
      )

    # FTPEE_contribution_to_GL[region] = ( FTPEE_rate_of_change_policy[region] * 1 - FTPEE_policy_Min ) / ( FTPEE_policy_Max - FTPEE_policy_Min )
    idxlhs = fcol_in_mdf["FTPEE_contribution_to_GL"]
    idx1 = fcol_in_mdf["FTPEE_rate_of_change_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 1 - FTPEE_policy_Min) / (
        FTPEE_policy_Max - FTPEE_policy_Min
      )

    # FWRP_contribution_to_GL[region] = ( FWRP_policy[region] * 100 - FWRP_policy_Min ) / ( FWRP_policy_Max - FWRP_policy_Min )
    idxlhs = fcol_in_mdf["FWRP_contribution_to_GL"]
    idx1 = fcol_in_mdf["FWRP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - FWRP_policy_Min) / (
        FWRP_policy_Max - FWRP_policy_Min
      )

    # FPGDC_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , FPGDC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FPGDC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FPGDC_R1_via_Excel , FPGDC_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FPGDC_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FPGDC_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FPGDC_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FPGDC_R1_via_Excel[j], FPGDC_policy_Min
          ),     ),   )

    # FPGDC_policy_with_RW[region] = FPGDC_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["FPGDC_policy_with_RW"]
    idx1 = fcol_in_mdf["FPGDC_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # FPGDC_pol_div_100[region] = MIN ( FPGDC_policy_Max , MAX ( FPGDC_policy_Min , FPGDC_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["FPGDC_pol_div_100"]
    idx1 = fcol_in_mdf["FPGDC_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FPGDC_policy_Max, max(FPGDC_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # FPGDC_logically_constrained[region] = MIN ( FPGDC_policy_Max , MAX ( FPGDC_policy_Min , FPGDC_pol_div_100[region] ) ) * UNIT_conv_to_1_per_yr
    idxlhs = fcol_in_mdf["FPGDC_logically_constrained"]
    idx1 = fcol_in_mdf["FPGDC_pol_div_100"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(FPGDC_policy_Max, max(FPGDC_policy_Min, mdf[rowi, idx1 + j]))
        * UNIT_conv_to_1_per_yr
      )

    # Public_Debt_cancelling_pulse[region] = ( STEP ( 1 , Time_at_which_govt_public_debt_is_cancelled[region] ) - STEP ( 1 , Time_at_which_govt_public_debt_is_cancelled[region] + Public_Govt_debt_cancelling_spread[region] ) ) * FPGDC_logically_constrained[region]
    idxlhs = fcol_in_mdf["Public_Debt_cancelling_pulse"]
    idx1 = fcol_in_mdf["FPGDC_logically_constrained"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (STEP(zeit, 1, Time_at_which_govt_public_debt_is_cancelled)
        - STEP(
          zeit,       1,       Time_at_which_govt_public_debt_is_cancelled
          + Public_Govt_debt_cancelling_spread,     )
      ) * mdf[rowi, idx1 + j]

    # FPGDC_contribution_to_GL[region] = FPGDC_logically_constrained[region] * Public_Debt_cancelling_pulse[region] / UNIT_conv_to_1_per_yr / UNIT_conv_to_1_per_yr
    idxlhs = fcol_in_mdf["FPGDC_contribution_to_GL"]
    idx1 = fcol_in_mdf["FPGDC_logically_constrained"]
    idx2 = fcol_in_mdf["Public_Debt_cancelling_pulse"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / UNIT_conv_to_1_per_yr
        / UNIT_conv_to_1_per_yr
      )

    # ICTR_contribution_to_GL[region] = 1 - ( ( ICTR_policy[region] * 100 - ICTR_policy_Max ) / ( ICTR_policy_Min - ICTR_policy_Max ) )
    idxlhs = fcol_in_mdf["ICTR_contribution_to_GL"]
    idx1 = fcol_in_mdf["ICTR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 100 - ICTR_policy_Max)
        / (ICTR_policy_Min - ICTR_policy_Max)
      )

    # IOITR_contribution_to_GL[region] = 1 - ( ( IOITR_policy[region] * 100 - IOITR_policy_Max ) / ( IOITR_policy_Min - IOITR_policy_Max ) )
    idxlhs = fcol_in_mdf["IOITR_contribution_to_GL"]
    idx1 = fcol_in_mdf["IOITR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 100 - IOITR_policy_Max)
        / (IOITR_policy_Min - IOITR_policy_Max)
      )

    # ISPV_contribution_to_GL[region] = ( wind_and_PV_el_share_max[region] * 100 - ISPV_policy_Min ) / ( ISPV_policy_Max - ISPV_policy_Min )
    idxlhs = fcol_in_mdf["ISPV_contribution_to_GL"]
    idx1 = fcol_in_mdf["wind_and_PV_el_share_max"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - ISPV_policy_Min) / (
        ISPV_policy_Max - ISPV_policy_Min
      )

    # IWITR_contribution_to_GL[region] = 1 - ( ( IWITR_policy[region] * 100 - IWITR_policy_Max ) / ( IWITR_policy_Min - IWITR_policy_Max ) )
    idxlhs = fcol_in_mdf["IWITR_contribution_to_GL"]
    idx1 = fcol_in_mdf["IWITR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 100 - IWITR_policy_Max)
        / (IWITR_policy_Min - IWITR_policy_Max)
      )

    # Lfrac_contribution_to_GL[region] = Lfrac_policy[region]
    idxlhs = fcol_in_mdf["Lfrac_contribution_to_GL"]
    idx1 = fcol_in_mdf["Lfrac_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # LPB_contribution_to_GL[region] = ( LPB_policy[region] * 100 - LPB_policy_Min ) / ( LPB_policy_Max - LPB_policy_Min )
    idxlhs = fcol_in_mdf["LPB_contribution_to_GL"]
    idx1 = fcol_in_mdf["LPB_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - LPB_policy_Min) / (
        LPB_policy_Max - LPB_policy_Min
      )

    # LPBgrant_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , LPBgrant_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , LPBgrant_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , LPBgrant_R1_via_Excel , LPBgrant_policy_Min ) ) )
    idxlhs = fcol_in_mdf["LPBgrant_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     LPBgrant_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       LPBgrant_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, LPBgrant_R1_via_Excel[j], LPBgrant_policy_Min
          ),     ),   )

    # LPBgrant_policy_with_RW[region] = LPBgrant_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["LPBgrant_policy_with_RW"]
    idx1 = fcol_in_mdf["LPBgrant_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # LPBgrant_pol_div_100[region] = MIN ( LPBgrant_policy_Max , MAX ( LPBgrant_policy_Min , LPBgrant_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["LPBgrant_pol_div_100"]
    idx1 = fcol_in_mdf["LPBgrant_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(LPBgrant_policy_Max, max(LPBgrant_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # LPBgrant_policy[region] = SMOOTH3 ( LPBgrant_pol_div_100[region] , LPBgrant_Time_to_implement_policy )
    idxin = fcol_in_mdf["LPBgrant_pol_div_100"]
    idx2 = fcol_in_mdf["LPBgrant_policy_2"]
    idx1 = fcol_in_mdf["LPBgrant_policy_1"]
    idxout = fcol_in_mdf["LPBgrant_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (LPBgrant_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (LPBgrant_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (LPBgrant_Time_to_implement_policy / 3)
        * dt
      )

    # LPBgrant_contribution_to_GL[region] = ( LPBgrant_policy[region] * 100 - LPBgrant_policy_Min ) / ( LPBgrant_policy_Max - LPBgrant_policy_Min )
    idxlhs = fcol_in_mdf["LPBgrant_contribution_to_GL"]
    idx1 = fcol_in_mdf["LPBgrant_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - LPBgrant_policy_Min) / (
        LPBgrant_policy_Max - LPBgrant_policy_Min
      )

    # LPBsplit_contribution_to_GL[region] = ( LPBsplit_policy[region] * 100 - LPBsplit_policy_Min ) / ( LPBsplit_policy_Max - LPBsplit_policy_Min )
    idxlhs = fcol_in_mdf["LPBsplit_contribution_to_GL"]
    idx1 = fcol_in_mdf["LPBsplit_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - LPBsplit_policy_Min) / (
        LPBsplit_policy_Max - LPBsplit_policy_Min
      )

    # NEP_contribution_to_GL[region] = ( NEP_policy[region] * 100 - NEP_policy_Min ) / ( NEP_policy_Max - NEP_policy_Min )
    idxlhs = fcol_in_mdf["NEP_contribution_to_GL"]
    idx1 = fcol_in_mdf["NEP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - NEP_policy_Min) / (
        NEP_policy_Max - NEP_policy_Min
      )

    # RMDR_contribution_to_GL[region] = ( RMDR_policy[region] * 100 - RMDR_policy_Min ) / ( RMDR_policy_Max - RMDR_policy_Min )
    idxlhs = fcol_in_mdf["RMDR_contribution_to_GL"]
    idx1 = fcol_in_mdf["RMDR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - RMDR_policy_Min) / (
        RMDR_policy_Max - RMDR_policy_Min
      )

    # SGMP_contribution_to_GL[region] = ( SGMP_policy[region] * 100 - SGMP_policy_Min ) / ( SGMP_policy_Max - SGMP_policy_Min )
    idxlhs = fcol_in_mdf["SGMP_contribution_to_GL"]
    idx1 = fcol_in_mdf["SGMP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - SGMP_policy_Min) / (
        SGMP_policy_Max - SGMP_policy_Min
      )

    # SGRPI_contribution_to_GL[region] = 1 - ( ( SGRPI_policy[region] * 100 - SGRPI_policy_Max ) / ( SGRPI_policy_Min - SGRPI_policy_Max ) )
    idxlhs = fcol_in_mdf["SGRPI_contribution_to_GL"]
    idx1 = fcol_in_mdf["SGRPI_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 100 - SGRPI_policy_Max)
        / (SGRPI_policy_Min - SGRPI_policy_Max)
      )

    # SSDGR_contribution_to_GL[region] = 1 - ( ( SSGDR_policy[region] * 1 - SSGDR_policy_Max ) / ( SSGDR_policy_Min - SSGDR_policy_Max ) )
    idxlhs = fcol_in_mdf["SSDGR_contribution_to_GL"]
    idx1 = fcol_in_mdf["SSGDR_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 1 - SSGDR_policy_Max)
        / (SSGDR_policy_Min - SSGDR_policy_Max)
      )

    # StrUP_contribution_to_GL[region] = ( StrUP_policy[region] * 100 - StrUP_policy_Min ) / ( StrUP_policy_Max - StrUP_policy_Min )
    idxlhs = fcol_in_mdf["StrUP_contribution_to_GL"]
    idx1 = fcol_in_mdf["StrUP_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - StrUP_policy_Min) / (
        StrUP_policy_Max - StrUP_policy_Min
      )

    # Wreaction_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , Wreaction_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , Wreaction_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , Wreaction_R1_via_Excel , WReaction_policy_Min ) ) )
    idxlhs = fcol_in_mdf["Wreaction_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     Wreaction_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       Wreaction_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, Wreaction_R1_via_Excel[j], WReaction_policy_Min
          ),     ),   )

    # Wreaction_policy_with_RW[region] = Wreaction_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["Wreaction_policy_with_RW"]
    idx1 = fcol_in_mdf["Wreaction_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Wreaction_pol_div_100[region] = MIN ( WReaction_policy_Max , MAX ( WReaction_policy_Min , Wreaction_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["Wreaction_pol_div_100"]
    idx1 = fcol_in_mdf["Wreaction_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(WReaction_policy_Max, max(WReaction_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # WReaction_policy[region] = SMOOTH3 ( Wreaction_pol_div_100[region] , WReaction_Time_to_implement_policy )
    idxin = fcol_in_mdf["Wreaction_pol_div_100"]
    idx2 = fcol_in_mdf["WReaction_policy_2"]
    idx1 = fcol_in_mdf["WReaction_policy_1"]
    idxout = fcol_in_mdf["WReaction_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (WReaction_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (WReaction_Time_to_implement_policy / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (WReaction_Time_to_implement_policy / 3)
        * dt
      )

    # WReaction_contribution_to_GL[region] = ( WReaction_policy[region] * 100 - WReaction_policy_Min ) / ( WReaction_policy_Max - WReaction_policy_Min )
    idxlhs = fcol_in_mdf["WReaction_contribution_to_GL"]
    idx1 = fcol_in_mdf["WReaction_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - WReaction_policy_Min) / (
        WReaction_policy_Max - WReaction_policy_Min
      )

    # XtaxCom_contribution_to_GL[region] = ( XtaxCom_policy[region] * 100 - XtaxCom_policy_Min ) / ( XtaxCom_policy_Max - XtaxCom_policy_Min )
    idxlhs = fcol_in_mdf["XtaxCom_contribution_to_GL"]
    idx1 = fcol_in_mdf["XtaxCom_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - XtaxCom_policy_Min) / (
        XtaxCom_policy_Max - XtaxCom_policy_Min
      )

    # Xtaxfrac_contribution_to_GL[region] = ( Xtaxfrac_policy[region] * 100 - Xtaxfrac_policy_Min ) / ( Xtaxfrac_policy_Max - Xtaxfrac_policy_Min )
    idxlhs = fcol_in_mdf["Xtaxfrac_contribution_to_GL"]
    idx1 = fcol_in_mdf["Xtaxfrac_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - Xtaxfrac_policy_Min) / (
        Xtaxfrac_policy_Max - Xtaxfrac_policy_Min
      )

    # XtaxRateEmp_contribution_to_GL[region] = ( XtaxRateEmp_policy[region] * 100 - XtaxRateEmp_policy_Min ) / ( XtaxRateEmp_policy_Max - XtaxRateEmp_policy_Min )
    idxlhs = fcol_in_mdf["XtaxRateEmp_contribution_to_GL"]
    idx1 = fcol_in_mdf["XtaxRateEmp_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - XtaxRateEmp_policy_Min) / (
        XtaxRateEmp_policy_Max - XtaxRateEmp_policy_Min
      )

    # TOW_contribution_to_GL[region] = 1 - ( ( TOW_policy[region] * 100 / TOW_UNIT_conv_to_pa - TOW_policy_Max ) / ( TOW_policy_Min - TOW_policy_Max ) )
    idxlhs = fcol_in_mdf["TOW_contribution_to_GL"]
    idx1 = fcol_in_mdf["TOW_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 100 / TOW_UNIT_conv_to_pa - TOW_policy_Max)
        / (TOW_policy_Min - TOW_policy_Max)
      )

    # RIPLGF_contribution_to_GL[region] = 1 - ( ( RIPLGF_policy[region] * 100 - RIPLGF_policy_Max ) / ( RIPLGF_policy_Min - RIPLGF_policy_Max ) )
    idxlhs = fcol_in_mdf["RIPLGF_contribution_to_GL"]
    idx1 = fcol_in_mdf["RIPLGF_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - (
        (mdf[rowi, idx1 + j] * 100 - RIPLGF_policy_Max)
        / (RIPLGF_policy_Min - RIPLGF_policy_Max)
      )

    # FC_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , FC_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , FC_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , FC_R1_via_Excel , Forest_cutting_policy_Min ) ) )
    idxlhs = fcol_in_mdf["FC_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     FC_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       FC_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, FC_R1_via_Excel[j], Forest_cutting_policy_Min
          ),     ),   )

    # FC_policy_with_RW[region] = FC_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
    idxlhs = fcol_in_mdf["FC_policy_with_RW"]
    idx1 = fcol_in_mdf["FC_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
      )

    # FC_pol_div_100[region] = MIN ( Forest_cutting_policy_Max , MAX ( Forest_cutting_policy_Min , FC_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["FC_pol_div_100"]
    idx1 = fcol_in_mdf["FC_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(
          Forest_cutting_policy_Max, max(Forest_cutting_policy_Min, mdf[rowi, idx1 + j])
        )
        / 100
      )

    # Forest_cutting_policy[region] = SMOOTH3 ( FC_pol_div_100[region] , Forest_cutting_policy_Time_to_implement_goal )
    idxin = fcol_in_mdf["FC_pol_div_100"]
    idx2 = fcol_in_mdf["Forest_cutting_policy_2"]
    idx1 = fcol_in_mdf["Forest_cutting_policy_1"]
    idxout = fcol_in_mdf["Forest_cutting_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Forest_cutting_policy_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Forest_cutting_policy_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Forest_cutting_policy_Time_to_implement_goal / 3)
        * dt
      )

    # Forest_cutting_policy_contribution_to_GL[region] = ( Forest_cutting_policy[region] * 100 - Forest_cutting_policy_Min ) / ( Forest_cutting_policy_Max - Forest_cutting_policy_Min )
    idxlhs = fcol_in_mdf["Forest_cutting_policy_contribution_to_GL"]
    idx1 = fcol_in_mdf["Forest_cutting_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - Forest_cutting_policy_Min
      ) / (Forest_cutting_policy_Max - Forest_cutting_policy_Min)

    # REFOREST_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , REFOREST_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , REFOREST_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , REFOREST_R1_via_Excel , REFOREST_policy_Min ) ) )
    idxlhs = fcol_in_mdf["REFOREST_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     REFOREST_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       REFOREST_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, REFOREST_R1_via_Excel[j], REFOREST_policy_Min
          ),     ),   )

    # REFOREST_policy_with_RW[region] = REFOREST_rounds_via_Excel[region] * Smoothed_Reform_willingness[region] / Inequality_effect_on_energy_TA[region] * Smoothed_Multplier_from_empowerment_on_speed_of_food_TA[region]
    idxlhs = fcol_in_mdf["REFOREST_policy_with_RW"]
    idx1 = fcol_in_mdf["REFOREST_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx3 = fcol_in_mdf["Inequality_effect_on_energy_TA"]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_empowerment_on_speed_of_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
      )

    # REFOREST_pol_div_100[region] = MIN ( REFOREST_policy_Max , MAX ( REFOREST_policy_Min , REFOREST_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["REFOREST_pol_div_100"]
    idx1 = fcol_in_mdf["REFOREST_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(REFOREST_policy_Max, max(REFOREST_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # REFOREST_policy[region] = SMOOTH3 ( REFOREST_pol_div_100[region] , REFOREST_policy_Time_to_implement_goal )
    idxin = fcol_in_mdf["REFOREST_pol_div_100"]
    idx2 = fcol_in_mdf["REFOREST_policy_2"]
    idx1 = fcol_in_mdf["REFOREST_policy_1"]
    idxout = fcol_in_mdf["REFOREST_policy"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (REFOREST_policy_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (REFOREST_policy_Time_to_implement_goal / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (REFOREST_policy_Time_to_implement_goal / 3)
        * dt
      )

    # REFOREST_policy_contribution_to_GL[region] = ( REFOREST_policy[region] * 100 - REFOREST_policy_Min ) / ( REFOREST_policy_Max - REFOREST_policy_Min )
    idxlhs = fcol_in_mdf["REFOREST_policy_contribution_to_GL"]
    idx1 = fcol_in_mdf["REFOREST_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * 100 - REFOREST_policy_Min) / (
        REFOREST_policy_Max - REFOREST_policy_Min
      )

    # Which_Scenario_is_run[region] = ( CCS_contribution_to_GL[region] + Ctax_contribution_to_GL[region] + DAC_contribution_to_GL[region] + FEHC_contribution_to_GL[region] + FLWR_contribution_to_GL[region] + FTPEE_contribution_to_GL[region] + FWRP_contribution_to_GL[region] + FPGDC_contribution_to_GL[region] + ICTR_contribution_to_GL[region] + IOITR_contribution_to_GL[region] + ISPV_contribution_to_GL[region] + IWITR_contribution_to_GL[region] + Lfrac_contribution_to_GL[region] + LPB_contribution_to_GL[region] + LPBgrant_contribution_to_GL[region] + LPBsplit_contribution_to_GL[region] + NEP_contribution_to_GL[region] + RMDR_contribution_to_GL[region] + SGMP_contribution_to_GL[region] + SGRPI_contribution_to_GL[region] + SSDGR_contribution_to_GL[region] + StrUP_contribution_to_GL[region] + WReaction_contribution_to_GL[region] + XtaxCom_contribution_to_GL[region] + Xtaxfrac_contribution_to_GL[region] + XtaxRateEmp_contribution_to_GL[region] + TOW_contribution_to_GL[region] + RIPLGF_contribution_to_GL[region] + Forest_cutting_policy_contribution_to_GL[region] + REFOREST_policy_contribution_to_GL[region] ) / Nbr_of_policies
    idxlhs = fcol_in_mdf["Which_Scenario_is_run"]
    idx1 = fcol_in_mdf["CCS_contribution_to_GL"]
    idx2 = fcol_in_mdf["Ctax_contribution_to_GL"]
    idx3 = fcol_in_mdf["DAC_contribution_to_GL"]
    idx4 = fcol_in_mdf["FEHC_contribution_to_GL"]
    idx5 = fcol_in_mdf["FLWR_contribution_to_GL"]
    idx6 = fcol_in_mdf["FTPEE_contribution_to_GL"]
    idx7 = fcol_in_mdf["FWRP_contribution_to_GL"]
    idx8 = fcol_in_mdf["FPGDC_contribution_to_GL"]
    idx9 = fcol_in_mdf["ICTR_contribution_to_GL"]
    idx10 = fcol_in_mdf["IOITR_contribution_to_GL"]
    idx11 = fcol_in_mdf["ISPV_contribution_to_GL"]
    idx12 = fcol_in_mdf["IWITR_contribution_to_GL"]
    idx13 = fcol_in_mdf["Lfrac_contribution_to_GL"]
    idx14 = fcol_in_mdf["LPB_contribution_to_GL"]
    idx15 = fcol_in_mdf["LPBgrant_contribution_to_GL"]
    idx16 = fcol_in_mdf["LPBsplit_contribution_to_GL"]
    idx17 = fcol_in_mdf["NEP_contribution_to_GL"]
    idx18 = fcol_in_mdf["RMDR_contribution_to_GL"]
    idx19 = fcol_in_mdf["SGMP_contribution_to_GL"]
    idx20 = fcol_in_mdf["SGRPI_contribution_to_GL"]
    idx21 = fcol_in_mdf["SSDGR_contribution_to_GL"]
    idx22 = fcol_in_mdf["StrUP_contribution_to_GL"]
    idx23 = fcol_in_mdf["WReaction_contribution_to_GL"]
    idx24 = fcol_in_mdf["XtaxCom_contribution_to_GL"]
    idx25 = fcol_in_mdf["Xtaxfrac_contribution_to_GL"]
    idx26 = fcol_in_mdf["XtaxRateEmp_contribution_to_GL"]
    idx27 = fcol_in_mdf["TOW_contribution_to_GL"]
    idx28 = fcol_in_mdf["RIPLGF_contribution_to_GL"]
    idx29 = fcol_in_mdf["Forest_cutting_policy_contribution_to_GL"]
    idx30 = fcol_in_mdf["REFOREST_policy_contribution_to_GL"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
        + mdf[rowi, idx7 + j]
        + mdf[rowi, idx8 + j]
        + mdf[rowi, idx9 + j]
        + mdf[rowi, idx10 + j]
        + mdf[rowi, idx11 + j]
        + mdf[rowi, idx12 + j]
        + mdf[rowi, idx13 + j]
        + mdf[rowi, idx14 + j]
        + mdf[rowi, idx15 + j]
        + mdf[rowi, idx16 + j]
        + mdf[rowi, idx17 + j]
        + mdf[rowi, idx18 + j]
        + mdf[rowi, idx19 + j]
        + mdf[rowi, idx20 + j]
        + mdf[rowi, idx21 + j]
        + mdf[rowi, idx22 + j]
        + mdf[rowi, idx23 + j]
        + mdf[rowi, idx24 + j]
        + mdf[rowi, idx25 + j]
        + mdf[rowi, idx26 + j]
        + mdf[rowi, idx27 + j]
        + mdf[rowi, idx28 + j]
        + mdf[rowi, idx29 + j]
        + mdf[rowi, idx30 + j]
      ) / Nbr_of_policies

    # Regional_population_as_fraction_of_total[region] = Population[region] / Global_population
    idxlhs = fcol_in_mdf["Regional_population_as_fraction_of_total"]
    idx1 = fcol_in_mdf["Population"]
    idx2 = fcol_in_mdf["Global_population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2]

    # Which_Scenario_is_run_globally = Which_Scenario_is_run[us] * Regional_population_as_fraction_of_total[us] + Which_Scenario_is_run[af] * Regional_population_as_fraction_of_total[af] + Which_Scenario_is_run[cn] * Regional_population_as_fraction_of_total[cn] + Which_Scenario_is_run[me] * Regional_population_as_fraction_of_total[me] + Which_Scenario_is_run[sa] * Regional_population_as_fraction_of_total[sa] + Which_Scenario_is_run[la] * Regional_population_as_fraction_of_total[la] + Which_Scenario_is_run[pa] * Regional_population_as_fraction_of_total[pa] + Which_Scenario_is_run[ec] * Regional_population_as_fraction_of_total[ec] + Which_Scenario_is_run[eu] * Regional_population_as_fraction_of_total[eu] + Which_Scenario_is_run[se] * Regional_population_as_fraction_of_total[se]
    idxlhs = fcol_in_mdf["Which_Scenario_is_run_globally"]
    idx1 = fcol_in_mdf["Which_Scenario_is_run"]
    idx2 = fcol_in_mdf["Regional_population_as_fraction_of_total"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1 + 0] * mdf[rowi, idx2 + 0]
      + mdf[rowi, idx1 + 1] * mdf[rowi, idx2 + 1]
      + mdf[rowi, idx1 + 2] * mdf[rowi, idx2 + 2]
      + mdf[rowi, idx1 + 3] * mdf[rowi, idx2 + 3]
      + mdf[rowi, idx1 + 4] * mdf[rowi, idx2 + 4]
      + mdf[rowi, idx1 + 5] * mdf[rowi, idx2 + 5]
      + mdf[rowi, idx1 + 6] * mdf[rowi, idx2 + 6]
      + mdf[rowi, idx1 + 7] * mdf[rowi, idx2 + 7]
      + mdf[rowi, idx1 + 8] * mdf[rowi, idx2 + 8]
      + mdf[rowi, idx1 + 9] * mdf[rowi, idx2 + 9]
    )

    # Annual_reduction_in_UAC = Annual_reduction_in_UAC_TLTL * ( 1 - Which_Scenario_is_run_globally ) + Annual_reduction_in_UAC_GL * Which_Scenario_is_run_globally
    idxlhs = fcol_in_mdf["Annual_reduction_in_UAC"]
    idx1 = fcol_in_mdf["Which_Scenario_is_run_globally"]
    idx2 = fcol_in_mdf["Which_Scenario_is_run_globally"]
    mdf[rowi, idxlhs] = (
      Annual_reduction_in_UAC_TLTL * (1 - mdf[rowi, idx1])
      + Annual_reduction_in_UAC_GL * mdf[rowi, idx2]
    )

    # Slope_btw_temp_and_permafrost_melting_or_freezing = IF_THEN_ELSE ( zeit < 2020 , Slope_btw_temp_and_permafrost_melting_or_freezing_base , Slope_btw_temp_and_permafrost_melting_or_freezing_sensitivity )
    idxlhs = fcol_in_mdf["Slope_btw_temp_and_permafrost_melting_or_freezing"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit < 2020,   Slope_btw_temp_and_permafrost_melting_or_freezing_base,   Slope_btw_temp_and_permafrost_melting_or_freezing_sensitivity, )

    # Temp_diff_relevant_for_melting_or_freezing_from_1850_smoothed = SMOOTH ( Temp_diff_relevant_for_melting_or_freezing_from_1850 , Time_to_smooth_out_temperature_diff_relevant_for_melting_or_freezing_from_1850_yr )
    idx1 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_from_1850_smoothed"]
    idx2 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_from_1850"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Time_to_smooth_out_temperature_diff_relevant_for_melting_or_freezing_from_1850_yr
      * dt
    )

    # Effect_of_temp_on_permafrost_melting_dmnl = 1 + Slope_btw_temp_and_permafrost_melting_or_freezing * ( ( Temp_diff_relevant_for_melting_or_freezing_from_1850_smoothed / Ref_temp_difference_4_degC ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temp_on_permafrost_melting_dmnl"]
    idx1 = fcol_in_mdf["Slope_btw_temp_and_permafrost_melting_or_freezing"]
    idx2 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_from_1850_smoothed"]
    mdf[rowi, idxlhs] = 1 + mdf[rowi, idx1] * (
      (mdf[rowi, idx2] / Ref_temp_difference_4_degC) - 1
    )

    # Effect_of_temp_on_permafrost_melting_dmnl_smoothed = SMOOTH ( Effect_of_temp_on_permafrost_melting_dmnl , Time_to_propagate_temperature_change_through_the_volume_of_permafrost_yr )
    idx1 = fcol_in_mdf["Effect_of_temp_on_permafrost_melting_dmnl_smoothed"]
    idx2 = fcol_in_mdf["Effect_of_temp_on_permafrost_melting_dmnl"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Time_to_propagate_temperature_change_through_the_volume_of_permafrost_yr
      * dt
    )

    # Slowing_of_recapture_of_CH4_dmnl = IF_THEN_ELSE ( Effect_of_temp_on_permafrost_melting_dmnl_smoothed < 0 , 0.01 , 1 )
    idxlhs = fcol_in_mdf["Slowing_of_recapture_of_CH4_dmnl"]
    idx1 = fcol_in_mdf["Effect_of_temp_on_permafrost_melting_dmnl_smoothed"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] < 0, 0.01, 1)

    # Permafrost_melting_cutoff = WITH LOOKUP ( C_in_permafrost_in_form_of_CH4 , ( [ ( 0 , 0 ) - ( 200 , 1 ) ] , ( 0 , 0 ) , ( 50 , 0.6 ) , ( 100 , 0.9 ) , ( 150 , 0.965 ) , ( 200 , 1 ) ) )
    tabidx = ftab_in_d_table["Permafrost_melting_cutoff"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Permafrost_melting_cutoff"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["C_in_permafrost_in_form_of_CH4"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint = Switch_btw_historical_CO2_CH4_emissions_or_constant_1_history_0_constant * ( Area_equivalent_of_linear_retreat_km2_py * Avg_amount_of_C_in_the_form_of_CH4_per_km2 * Effect_of_temp_on_permafrost_melting_dmnl_smoothed * Slowing_of_recapture_of_CH4_dmnl * Permafrost_melting_cutoff )
    idxlhs = fcol_in_mdf["CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint"
    ]
    idx1 = fcol_in_mdf["Effect_of_temp_on_permafrost_melting_dmnl_smoothed"]
    idx2 = fcol_in_mdf["Slowing_of_recapture_of_CH4_dmnl"]
    idx3 = fcol_in_mdf["Permafrost_melting_cutoff"]
    mdf[rowi, idxlhs] = (
      Switch_btw_historical_CO2_CH4_emissions_or_constant_1_history_0_constant
      * (
        Area_equivalent_of_linear_retreat_km2_py
        * Avg_amount_of_C_in_the_form_of_CH4_per_km2
        * mdf[rowi, idx1]
        * mdf[rowi, idx2]
        * mdf[rowi, idx3]
      )
    )

    # Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py = ( CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint / Avg_amount_of_C_in_the_form_of_CH4_per_km2 ) * Avg_depth_of_permafrost_km * Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3 / UNIT_conversion_km3_div_km_to_km2
    idxlhs = fcol_in_mdf["Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py"
    ]
    idx1 = fcol_in_mdf["CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] / Avg_amount_of_C_in_the_form_of_CH4_per_km2)
      * Avg_depth_of_permafrost_km
      * Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3
      / UNIT_conversion_km3_div_km_to_km2
    )

    # Heat_in_atmosphere_needed_to_available_ratio = Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py / Heat_in_atmosphere_ZJ
    idxlhs = fcol_in_mdf["Heat_in_atmosphere_needed_to_available_ratio"]
    idx1 = fcol_in_mdf["Heat_gained_or_needed_for_the_desired_freezing_or_unfreezing_of_permafrost_ZJ_py"
    ]
    idx2 = fcol_in_mdf["Heat_in_atmosphere_ZJ"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]

    # Melting_restraint_for_permafrost_from_heat_in_atmophere = WITH LOOKUP ( Heat_in_atmosphere_needed_to_available_ratio , ( [ ( 0 , 0 ) - ( 0.5 , 1 ) ] , ( 0 , 1 ) , ( 0.4 , 0.95 ) , ( 0.45 , 0.75 ) , ( 0.5 , 0.01 ) ) )
    tabidx = ftab_in_d_table[  "Melting_restraint_for_permafrost_from_heat_in_atmophere"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Melting_restraint_for_permafrost_from_heat_in_atmophere"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Heat_in_atmosphere_needed_to_available_ratio"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py = CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint * Melting_restraint_for_permafrost_from_heat_in_atmophere * Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl
    idxlhs = fcol_in_mdf["CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py"
    ]
    idx1 = fcol_in_mdf["CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint"]
    idx2 = fcol_in_mdf["Melting_restraint_for_permafrost_from_heat_in_atmophere"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * mdf[rowi, idx2]
      * Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl
    )

    # Annual_release_of_C_from_permafrost_GtC_py = CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py
    idxlhs = fcol_in_mdf["Annual_release_of_C_from_permafrost_GtC_py"]
    idx1 = fcol_in_mdf["CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # WSO_effect_on_available_capital[region] = 1 + Slope_of_Worker_share_of_output_with_unemployment_effect_on_available_capital * ( Worker_share_of_output_with_unemployment_effect[region] / WSO_in_1980[region] - 1 )
    idxlhs = fcol_in_mdf["WSO_effect_on_available_capital"]
    idx1 = fcol_in_mdf["Worker_share_of_output_with_unemployment_effect"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + Slope_of_Worker_share_of_output_with_unemployment_effect_on_available_capital
        * (mdf[rowi, idx1 + j] / WSO_in_1980[j] - 1)
      )

    # Corporate_borrowing_cost[region] = Cost_of_capital_for_secured_debt[region] + Normal_corporate_credit_risk_margin
    idxlhs = fcol_in_mdf["Corporate_borrowing_cost"]
    idx1 = fcol_in_mdf["Cost_of_capital_for_secured_debt"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Normal_corporate_credit_risk_margin

    # Corporate_borrowing_cost_N_years_ago[region] = SMOOTHI ( Corporate_borrowing_cost[region] , Years_for_CBC_comparison , Corporate_borrowing_cost_in_1980[region] )
    idx1 = fcol_in_mdf["Corporate_borrowing_cost_N_years_ago"]
    idx2 = fcol_in_mdf["Corporate_borrowing_cost"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Years_for_CBC_comparison
        * dt
      )

    # CBC_rate_denominator[region] = IF_THEN_ELSE ( SWITCH_CBC_effect_on_available_capital == 1 , Corporate_borrowing_cost_in_1980 , Corporate_borrowing_cost_N_years_ago )
    idxlhs = fcol_in_mdf["CBC_rate_denominator"]
    idx1 = fcol_in_mdf["Corporate_borrowing_cost_N_years_ago"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        SWITCH_CBC_effect_on_available_capital[j] == 1,     Corporate_borrowing_cost_in_1980[j],     mdf[rowi, idx1 + j],   )

    # Corporate_borrowing_cost_eff_on_available_capital[region] = 1 + Slope_of_Corporate_borrowing_cost_eff_on_available_capital[region] * ( Corporate_borrowing_cost[region] / CBC_rate_denominator[region] - 1 )
    idxlhs = fcol_in_mdf["Corporate_borrowing_cost_eff_on_available_capital"]
    idx1 = fcol_in_mdf["Corporate_borrowing_cost"]
    idx2 = fcol_in_mdf["CBC_rate_denominator"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + Slope_of_Corporate_borrowing_cost_eff_on_available_capital[j]
        * (mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] - 1)
      )

    # Perceived_demand_imblance[region] = SMOOTH3I ( Demand_imbalance[region] , Time_to_form_an_opinion_about_demand_imbalance , Dmd_imbalance_in_1980[region] )
    idxlhs = fcol_in_mdf["Perceived_demand_imblance"]
    idxin = fcol_in_mdf["Demand_imbalance"]
    idx2 = fcol_in_mdf["Perceived_demand_imblance_2"]
    idx1 = fcol_in_mdf["Perceived_demand_imblance_1"]
    idxout = fcol_in_mdf["Perceived_demand_imblance"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_form_an_opinion_about_demand_imbalance / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_form_an_opinion_about_demand_imbalance / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_form_an_opinion_about_demand_imbalance / 3)
        * dt
      )

    # Eff_of_dmd_imbalance_on_flow_of_available_capital[region] = 1 + Slope_of_Eff_of_dmd_imbalance_on_flow_of_available_capital * ( Perceived_demand_imblance[region] / Dmd_imbalance_in_1980[region] - 1 )
    idxlhs = fcol_in_mdf["Eff_of_dmd_imbalance_on_flow_of_available_capital"]
    idx1 = fcol_in_mdf["Perceived_demand_imblance"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + Slope_of_Eff_of_dmd_imbalance_on_flow_of_available_capital
        * (mdf[rowi, idx1 + j] / Dmd_imbalance_in_1980 - 1)
      )

    # Fraction_of_available_capital_to_new_capacity[region] = ( WSO_effect_on_available_capital[region] + Corporate_borrowing_cost_eff_on_available_capital[region] + Eff_of_dmd_imbalance_on_flow_of_available_capital[region] ) / 3
    idxlhs = fcol_in_mdf["Fraction_of_available_capital_to_new_capacity"]
    idx1 = fcol_in_mdf["WSO_effect_on_available_capital"]
    idx2 = fcol_in_mdf["Corporate_borrowing_cost_eff_on_available_capital"]
    idx3 = fcol_in_mdf["Eff_of_dmd_imbalance_on_flow_of_available_capital"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      ) / 3

    # Annual_shortfall_fraction_of_available_private_capital[region] = IF_THEN_ELSE ( Fraction_of_available_capital_to_new_capacity > 1 , Fraction_of_available_capital_to_new_capacity - 1 , 0 )
    idxlhs = fcol_in_mdf["Annual_shortfall_fraction_of_available_private_capital"]
    idx1 = fcol_in_mdf["Fraction_of_available_capital_to_new_capacity"]
    idx2 = fcol_in_mdf["Fraction_of_available_capital_to_new_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] > 1, mdf[rowi, idx2 + j] - 1, 0
      )

    # Workers_savings[region] = Worker_cash_inflow_seasonally_adjusted[region] - Worker_consumption_demand[region]
    idxlhs = fcol_in_mdf["Workers_savings"]
    idx1 = fcol_in_mdf["Worker_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Worker_consumption_demand"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Owners_savings[region] = Owner_cash_inflow_seasonally_adjusted[region] * Owner_saving_fraction[region]
    idxlhs = fcol_in_mdf["Owners_savings"]
    idx1 = fcol_in_mdf["Owner_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Owner_saving_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Total_savings[region] = Workers_savings[region] + Owners_savings[region]
    idxlhs = fcol_in_mdf["Total_savings"]
    idx1 = fcol_in_mdf["Workers_savings"]
    idx2 = fcol_in_mdf["Owners_savings"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Available_private_capital_for_investment[region] = Total_savings[region] + Foreign_capital_inflow[region]
    idxlhs = fcol_in_mdf["Available_private_capital_for_investment"]
    idx1 = fcol_in_mdf["Total_savings"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Foreign_capital_inflow

    # Annual_shortfall_of_available_private_capital[region] = Available_private_capital_for_investment[region] * Annual_shortfall_fraction_of_available_private_capital[region]
    idxlhs = fcol_in_mdf["Annual_shortfall_of_available_private_capital"]
    idx1 = fcol_in_mdf["Available_private_capital_for_investment"]
    idx2 = fcol_in_mdf["Annual_shortfall_fraction_of_available_private_capital"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Annual_surplus_fraction_of_available_private_capital[region] = IF_THEN_ELSE ( Fraction_of_available_capital_to_new_capacity < 1 , 1 - Fraction_of_available_capital_to_new_capacity , 0 )
    idxlhs = fcol_in_mdf["Annual_surplus_fraction_of_available_private_capital"]
    idx1 = fcol_in_mdf["Fraction_of_available_capital_to_new_capacity"]
    idx2 = fcol_in_mdf["Fraction_of_available_capital_to_new_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] < 1, 1 - mdf[rowi, idx2 + j], 0
      )

    # Annual_surplus_of_available_private_capital[region] = Available_private_capital_for_investment[region] * Annual_surplus_fraction_of_available_private_capital[region]
    idxlhs = fcol_in_mdf["Annual_surplus_of_available_private_capital"]
    idx1 = fcol_in_mdf["Available_private_capital_for_investment"]
    idx2 = fcol_in_mdf["Annual_surplus_fraction_of_available_private_capital"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Effect_of_temp_on_melting_antarctic_ice = 1 + Slope_temp_vs_antarctic_ice_melting * ( ( Temp_diff_relevant_for_melting_or_freezing_from_1850 / Ref_temp_difference_for_antarctic_ice_melting_3_degC ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temp_on_melting_antarctic_ice"]
    idx1 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_from_1850"]
    mdf[rowi, idxlhs] = 1 + Slope_temp_vs_antarctic_ice_melting * (
      (mdf[rowi, idx1] / Ref_temp_difference_for_antarctic_ice_melting_3_degC) - 1
    )

    # Land_covered_with_ice_to_land_area_ratio = Land_covered_with_ice_km2 / Land_area_km2
    idxlhs = fcol_in_mdf["Land_covered_with_ice_to_land_area_ratio"]
    idx1 = fcol_in_mdf["Land_covered_with_ice_km2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Land_area_km2

    # Snowball_earth_cutoff = WITH LOOKUP ( Land_covered_with_ice_to_land_area_ratio , ( [ ( 0.8 , 0 ) - ( 1 , 1 ) ] , ( 0.8 , 1 ) , ( 0.9 , 0.97 ) , ( 0.97 , 0.75 ) , ( 1 , 0 ) ) )
    tabidx = ftab_in_d_table["Snowball_earth_cutoff"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Snowball_earth_cutoff"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Land_covered_with_ice_to_land_area_ratio"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Atmos_heat_used_for_melting_last_year_1_py = SMOOTHI ( Atmos_heat_used_for_melting_1_py , per_annum_yr , Atmos_heat_used_for_melting_Initially_1_py )
    idxout = fcol_in_mdf["Atmos_heat_used_for_melting_last_year_1_py"]
    idx1 = fcol_in_mdf["Atmos_heat_used_for_melting_1_py"]
    mdf[rowi, idxout] = (
      mdf[rowi - 1, idxout]
      + (mdf[rowi - 1, idx1] - mdf[rowi - 1, idxout]) / per_annum_yr * dt
    )

    # Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction = WITH LOOKUP ( Atmos_heat_used_for_melting_last_year_1_py , ( [ ( 0 , 0 ) - ( 0.5 , 1 ) ] , ( 0 , 1 ) , ( 0.4 , 0.95 ) , ( 0.45 , 0.75 ) , ( 0.5 , 0.01 ) ) )
    tabidx = ftab_in_d_table[  "Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Atmos_heat_used_for_melting_last_year_1_py"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Ocean_heat_used_for_melting_last_year_ZJ_py = SMOOTHI ( Ocean_heat_used_for_melting_ZJ_py , per_annum_yr , Ocean_heat_used_for_melting_Initially_1_py )
    idxout = fcol_in_mdf["Ocean_heat_used_for_melting_last_year_ZJ_py"]
    idx1 = fcol_in_mdf["Ocean_heat_used_for_melting_ZJ_py"]
    mdf[rowi, idxout] = (
      mdf[rowi - 1, idxout]
      + (mdf[rowi - 1, idx1] - mdf[rowi - 1, idxout]) / per_annum_yr * dt
    )

    # Melting_constraint_from_the_heat_in_ocean_surface_reservoir = WITH LOOKUP ( Ocean_heat_used_for_melting_last_year_ZJ_py , ( [ ( 0 , 0 ) - ( 0.5 , 1 ) ] , ( 0 , 1 ) , ( 0.4 , 0.95 ) , ( 0.45 , 0.75 ) , ( 0.5 , 0.01 ) ) )
    tabidx = ftab_in_d_table[  "Melting_constraint_from_the_heat_in_ocean_surface_reservoir"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Melting_constraint_from_the_heat_in_ocean_surface_reservoir"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Ocean_heat_used_for_melting_last_year_ZJ_py"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py = ( Antarctic_ice_volume_km3 / Effective_time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp ) * Effect_of_temp_on_melting_antarctic_ice * Effect_of_heat_in_atm_on_melting_ice_cut_off * Snowball_earth_cutoff * Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction * Melting_constraint_from_the_heat_in_ocean_surface_reservoir
    idxlhs = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx1 = fcol_in_mdf["Antarctic_ice_volume_km3"]
    idx2 = fcol_in_mdf["Effect_of_temp_on_melting_antarctic_ice"]
    idx3 = fcol_in_mdf["Effect_of_heat_in_atm_on_melting_ice_cut_off"]
    idx4 = fcol_in_mdf["Snowball_earth_cutoff"]
    idx5 = fcol_in_mdf["Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction"
    ]
    idx6 = fcol_in_mdf["Melting_constraint_from_the_heat_in_ocean_surface_reservoir"]
    mdf[rowi, idxlhs] = (
      (
        mdf[rowi, idx1]
        / Effective_time_to_melt_or_freeze_antarctic_ice_at_the_reference_delta_temp
      )
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
      * mdf[rowi, idx4]
      * mdf[rowi, idx5]
      * mdf[rowi, idx6]
    )

    # Antarctic_ice_melting_km3_py = IF_THEN_ELSE ( Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py > 0 , Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
    idxlhs = fcol_in_mdf["Antarctic_ice_melting_km3_py"]
    idx1 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx2 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] > 0, mdf[rowi, idx2], 0)

    # Antarctic_ice_area_decrease_Mkm2_pr_yr = ( Antarctic_ice_melting_km3_py / Avg_thickness_Antarctic_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
    idxlhs = fcol_in_mdf["Antarctic_ice_area_decrease_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Antarctic_ice_melting_km3_py"]
    idx2 = fcol_in_mdf["Avg_thickness_Antarctic_km"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / mdf[rowi, idx2]
    ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py

    # Antarctic_ice_freezing_km3_py = IF_THEN_ELSE ( Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py < 0 , Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py * ( - 1 ) , 0 )
    idxlhs = fcol_in_mdf["Antarctic_ice_freezing_km3_py"]
    idx1 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx2 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] < 0, mdf[rowi, idx2] * (-1), 0)

    # Antarctic_ice_area_increase_Mkm2_pr_yr = ( Antarctic_ice_freezing_km3_py / Avg_thickness_Antarctic_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
    idxlhs = fcol_in_mdf["Antarctic_ice_area_increase_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Antarctic_ice_freezing_km3_py"]
    idx2 = fcol_in_mdf["Avg_thickness_Antarctic_km"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / mdf[rowi, idx2]
    ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py

    # Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py = Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py * GtIce_vs_km3
    idxlhs = fcol_in_mdf["Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py"]
    idx1 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * GtIce_vs_km3

    # Antarctic_ice_melting_as_water_km3_py = Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py * Densitiy_of_water_relative_to_ice
    idxlhs = fcol_in_mdf["Antarctic_ice_melting_as_water_km3_py"]
    idx1 = fcol_in_mdf["Antarctic_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Densitiy_of_water_relative_to_ice

    # Anthropogenic_aerosol_forcing = IF_THEN_ELSE ( Human_aerosol_forcing_1_is_ON_0_is_OFF == 0 , 0 , Aerosol_anthropogenic_emissions * Conversion_of_anthro_aerosol_emissions_to_forcing )
    idxlhs = fcol_in_mdf["Anthropogenic_aerosol_forcing"]
    idx1 = fcol_in_mdf["Aerosol_anthropogenic_emissions"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      Human_aerosol_forcing_1_is_ON_0_is_OFF == 0,   0,   mdf[rowi, idx1] * Conversion_of_anthro_aerosol_emissions_to_forcing, )

    # apl_to_acgl[region] = Abandoned_populated_land[region] / Time_for_abandoned_urban_land_to_become_fallow
    idxlhs = fcol_in_mdf["apl_to_acgl"]
    idx1 = fcol_in_mdf["Abandoned_populated_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_for_abandoned_urban_land_to_become_fallow
      )

    # apl_to_pl[region] = MIN ( Abandoned_populated_land[region] , MAX ( 0 , Populated_land_gap[region] ) ) / Time_to_develop_urban_land_from_abandoned_land
    idxlhs = fcol_in_mdf["apl_to_pl"]
    idx1 = fcol_in_mdf["Abandoned_populated_land"]
    idx2 = fcol_in_mdf["Populated_land_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(mdf[rowi, idx1 + j], max(0, mdf[rowi, idx2 + j]))
        / Time_to_develop_urban_land_from_abandoned_land
      )

    # Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio = Arctic_ice_on_sea_area_km2 / Arctic_ice_area_max_km2
    idxlhs = fcol_in_mdf["Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio"]
    idx1 = fcol_in_mdf["Arctic_ice_on_sea_area_km2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Arctic_ice_area_max_km2

    # Arctic_freezing_cutoff = WITH LOOKUP ( Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio , ( [ ( 0.8 , 0 ) - ( 1 , 1 ) ] , ( 0.8 , 1 ) , ( 0.899694 , 0.934211 ) , ( 0.949847 , 0.710526 ) , ( 1 , 0 ) ) )
    tabidx = ftab_in_d_table["Arctic_freezing_cutoff"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Arctic_freezing_cutoff"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Arctic_ice_on_sea_area_to_arctic_ice_area_max_ratio"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_1850 = SMOOTH ( Temp_surface_anomaly_compared_to_1850_degC , Arctic_surface_temp_delay_yr )
    idx1 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_1850"
    ]
    idx2 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1]) / Arctic_surface_temp_delay_yr * dt
    )

    # Effect_of_temp_on_melting_or_freezing_of_Arctic_ice = 1 + Slope_temp_vs_Arctic_ice_melting * ( ( Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_1850 / Ref_temp_difference_for_Arctic_ice_melting ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temp_on_melting_or_freezing_of_Arctic_ice"]
    idx1 = fcol_in_mdf["Temp_diff_relevant_for_melting_or_freezing_arctic_ice_from_1850"
    ]
    mdf[rowi, idxlhs] = 1 + Slope_temp_vs_Arctic_ice_melting * (
      (mdf[rowi, idx1] / Ref_temp_difference_for_Arctic_ice_melting) - 1
    )

    # Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py = ( Arctic_ice_on_sea_area_km2 / Effective_time_to_melt_Arctic_ice_at_the_reference_delta_temp ) * Effect_of_temp_on_melting_or_freezing_of_Arctic_ice * Arctic_freezing_cutoff * Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction * Melting_constraint_from_the_heat_in_ocean_surface_reservoir
    idxlhs = fcol_in_mdf["Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py"]
    idx1 = fcol_in_mdf["Arctic_ice_on_sea_area_km2"]
    idx2 = fcol_in_mdf["Effect_of_temp_on_melting_or_freezing_of_Arctic_ice"]
    idx3 = fcol_in_mdf["Arctic_freezing_cutoff"]
    idx4 = fcol_in_mdf["Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction"
    ]
    idx5 = fcol_in_mdf["Melting_constraint_from_the_heat_in_ocean_surface_reservoir"]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] / Effective_time_to_melt_Arctic_ice_at_the_reference_delta_temp)
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
      * mdf[rowi, idx4]
      * mdf[rowi, idx5]
    )

    # Arctic_land_surface_temp_anomaly_compared_to_1850 = SMOOTH ( Temp_surface_anomaly_compared_to_1850_degC , Land_surface_temp_adjustment_time_yr )
    idx1 = fcol_in_mdf["Arctic_land_surface_temp_anomaly_compared_to_1850"]
    idx2 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Land_surface_temp_adjustment_time_yr
      * dt
    )

    # Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py = Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
    idxlhs = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
    )

    # Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py = Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_GtIce_to_ZJ_melting
    idxlhs = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Antarctic_ice_losing_is_pos_or_gaining_is_neg_GtIce_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * Heat_needed_to_melt_1_km3_of_ice_ZJ
      * UNIT_conversion_GtIce_to_ZJ_melting
    )

    # Effect_of_temp_on_melting_greenland_ice = 1 + Slope_temp_vs_greenland_ice_melting * ( ( Arctic_land_surface_temp_anomaly_compared_to_1850 / Ref_temp_difference_for_greenland_ice_melting_C ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temp_on_melting_greenland_ice"]
    idx1 = fcol_in_mdf["Arctic_land_surface_temp_anomaly_compared_to_1850"]
    mdf[rowi, idxlhs] = 1 + Slope_temp_vs_greenland_ice_melting * (
      (mdf[rowi, idx1] / Ref_temp_difference_for_greenland_ice_melting_C) - 1
    )

    # Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py = ( Greenland_ice_volume_on_Greenland_km3 / Effective_time_to_melt_greenland_ice_at_the_reference_delta_temp ) * Effect_of_temp_on_melting_greenland_ice * Effect_of_heat_in_atm_on_melting_ice_cut_off * Snowball_earth_cutoff * Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction
    idxlhs = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx1 = fcol_in_mdf["Greenland_ice_volume_on_Greenland_km3"]
    idx2 = fcol_in_mdf["Effect_of_temp_on_melting_greenland_ice"]
    idx3 = fcol_in_mdf["Effect_of_heat_in_atm_on_melting_ice_cut_off"]
    idx4 = fcol_in_mdf["Snowball_earth_cutoff"]
    idx5 = fcol_in_mdf["Melting_constraint_from_the_heat_in_atmosphere_reservoir_fraction"
    ]
    mdf[rowi, idxlhs] = (
      (
        mdf[rowi, idx1]
        / Effective_time_to_melt_greenland_ice_at_the_reference_delta_temp
      )
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
      * mdf[rowi, idx4]
      * mdf[rowi, idx5]
    )

    # Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py = Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
    idxlhs = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
    )

    # Effect_of_temp_on_melting_greenland_ice_that_slid_into_the_ocean = 1 + Slope_temp_vs_greenland_ice_that_slid_into_the_ocean_melting * ( ( ( Temp_surface - ( Temp_surface_1850 - 273.15 ) ) / Ref_temp_difference_for_greenland_ice_that_slid_into_the_ocean_melting_degC ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temp_on_melting_greenland_ice_that_slid_into_the_ocean"
    ]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = (
      1
      + Slope_temp_vs_greenland_ice_that_slid_into_the_ocean_melting
      * (
        (
          (mdf[rowi, idx1] - (Temp_surface_1850 - 273.15))
          / Ref_temp_difference_for_greenland_ice_that_slid_into_the_ocean_melting_degC
        )
        - 1
      )
    )

    # Greenland_ice_that_slid_into_the_ocean_melting_is_pos_or_freezing_is_neg_km3_py = Greenland_ice_volume_that_slid_into_the_ocean_km3 / Time_to_melt_greenland_ice_that_slid_into_the_ocean_at_the_reference_delta_temp * Effect_of_temp_on_melting_greenland_ice_that_slid_into_the_ocean * Melting_constraint_from_the_heat_in_ocean_surface_reservoir
    idxlhs = fcol_in_mdf["Greenland_ice_that_slid_into_the_ocean_melting_is_pos_or_freezing_is_neg_km3_py"
    ]
    idx1 = fcol_in_mdf["Greenland_ice_volume_that_slid_into_the_ocean_km3"]
    idx2 = fcol_in_mdf["Effect_of_temp_on_melting_greenland_ice_that_slid_into_the_ocean"
    ]
    idx3 = fcol_in_mdf["Melting_constraint_from_the_heat_in_ocean_surface_reservoir"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / Time_to_melt_greenland_ice_that_slid_into_the_ocean_at_the_reference_delta_temp
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
    )

    # Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_that_slid_into_the_water_ZJ_py = Greenland_ice_that_slid_into_the_ocean_melting_is_pos_or_freezing_is_neg_km3_py * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
    idxlhs = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_that_slid_into_the_water_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Greenland_ice_that_slid_into_the_ocean_melting_is_pos_or_freezing_is_neg_km3_py"
    ]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Heat_needed_to_melt_1_km3_of_ice_ZJ * UNIT_conversion_1_p_km3
    )

    # Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py = Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py * Average_thickness_arctic_ice_km * Heat_needed_to_melt_1_km3_of_ice_ZJ / UNIT_conversion_km2_times_km_to_km3
    idxlhs = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Arctic_ice_melting_is_pos_or_freezing_is_neg_km2_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * Average_thickness_arctic_ice_km
      * Heat_needed_to_melt_1_km3_of_ice_ZJ
      / UNIT_conversion_km2_times_km_to_km3
    )

    # Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py = ( CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py / Avg_amount_of_C_in_the_form_of_CH4_per_km2 ) * Avg_depth_of_permafrost_km * Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3 / UNIT_conversion_km3_div_km_to_km2
    idxlhs = fcol_in_mdf["Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py"
    ]
    idx1 = fcol_in_mdf["CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py"
    ]
    mdf[rowi, idxlhs] = (
      (mdf[rowi, idx1] / Avg_amount_of_C_in_the_form_of_CH4_per_km2)
      * Avg_depth_of_permafrost_km
      * Heat_gained_or_needed_to_freeze_or_unfreeze_1_km3_permafrost_ZJ_p_km3
      / UNIT_conversion_km3_div_km_to_km2
    )

    # Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py + Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py * Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air + Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py + Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_that_slid_into_the_water_ZJ_py * Fraction_of_heat_needed_to_melt_Greenland_ice_that_slid_into_the_ocean_coming_from_air + Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py * Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air + Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py
    idxlhs = fcol_in_mdf["Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_glacial_ice_ZJ_py"
    ]
    idx2 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py"
    ]
    idx3 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_ZJ_py"
    ]
    idx4 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_that_slid_into_the_water_ZJ_py"
    ]
    idx5 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py"
    ]
    idx6 = fcol_in_mdf["Heat_actually_gained_or_needed_for_freezing_or_unfreezing_of_permafrost_ZJ_py"
    ]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2] * Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      * Fraction_of_heat_needed_to_melt_Greenland_ice_that_slid_into_the_ocean_coming_from_air
      + mdf[rowi, idx5] * Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air
      + mdf[rowi, idx6]
    )

    # Atmos_heat_used_for_melting_1_py = Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py / Heat_in_atmosphere_ZJ
    idxlhs = fcol_in_mdf["Atmos_heat_used_for_melting_1_py"]
    idx1 = fcol_in_mdf["Heat_withdrawn_from_atm_by_melting_pos_or_added_neg_by_freezing_ice_ZJ_py"
    ]
    idx2 = fcol_in_mdf["Heat_in_atmosphere_ZJ"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]

    # Carbon_in_top_ocean_layer_GtC = C_in_cold_surface_water_GtC + C_in_warm_surface_water_GtC
    idxlhs = fcol_in_mdf["Carbon_in_top_ocean_layer_GtC"]
    idx1 = fcol_in_mdf["C_in_cold_surface_water_GtC"]
    idx2 = fcol_in_mdf["C_in_warm_surface_water_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # Avg_C_concentration_in_top_layer = Carbon_in_top_ocean_layer_GtC / ( Cold_surface_water_volume_Gm3 + Warm_surface_water_volume_Gm3 )
    idxlhs = fcol_in_mdf["Avg_C_concentration_in_top_layer"]
    idx1 = fcol_in_mdf["Carbon_in_top_ocean_layer_GtC"]
    idx2 = fcol_in_mdf["Cold_surface_water_volume_Gm3"]
    idx3 = fcol_in_mdf["Warm_surface_water_volume_Gm3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (mdf[rowi, idx2] + mdf[rowi, idx3])

    # Avg_CC_in_ocean_top_layer_ymoles_per_litre = Avg_C_concentration_in_top_layer * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
    idxlhs = fcol_in_mdf["Avg_CC_in_ocean_top_layer_ymoles_per_litre"]
    idx1 = fcol_in_mdf["Avg_C_concentration_in_top_layer"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre

    # Avg_earths_surface_albedo = Albedo_ocean_with_arctic_ice_changes * Fraction_of_earth_surface_as_ocean + Albedo_land_biomes * ( 1 - Fraction_of_earth_surface_as_ocean )
    idxlhs = fcol_in_mdf["Avg_earths_surface_albedo"]
    idx1 = fcol_in_mdf["Albedo_ocean_with_arctic_ice_changes"]
    idx2 = fcol_in_mdf["Albedo_land_biomes"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Fraction_of_earth_surface_as_ocean + mdf[rowi, idx2
    ] * (1 - Fraction_of_earth_surface_as_ocean)

    # Historical_aerosol_forcing_volcanic = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , - 0.0843062 ) , ( 1981 , - 0.152848 ) , ( 1982 , - 0.823871 ) , ( 1983 , - 1.10866 ) , ( 1984 , - 0.552446 ) , ( 1985 , - 0.25566 ) , ( 1986 , - 0.1974 ) , ( 1987 , - 0.166556 ) , ( 1988 , - 0.126459 ) , ( 1989 , - 0.103155 ) , ( 1990 , - 0.105897 ) , ( 1991 , - 1.04732 ) , ( 1992 , - 1.6522 ) , ( 1993 , - 0.914346 ) , ( 1994 , - 0.363956 ) , ( 1995 , - 0.173753 ) , ( 1996 , - 0.108639 ) , ( 1997 , - 0.0791656 ) , ( 1998 , - 0.0448948 ) , ( 1999 , - 0.0161073 ) , ( 2000 , - 0.00376979 ) , ( 2001 , 0 ) , ( 2002 , 0 ) , ( 2003 , 0 ) , ( 2004 , 0 ) , ( 2005 , - 0.0484259 ) , ( 2006 , - 0.164648 ) , ( 2007 , - 0.232444 ) , ( 2008 , 0 ) , ( 2009 , 0 ) , ( 2010 , 0 ) , ( 2011 , 0 ) , ( 2012 , 0 ) , ( 2013 , 0 ) , ( 2014 , 0 ) , ( 2015 , 0 ) ) )
    tabidx = ftab_in_d_table[  "Historical_aerosol_forcing_volcanic"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Historical_aerosol_forcing_volcanic"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Future_volcanic_emissions_shape_pulse_train = PULSE_TRAIN ( NEvt_2a_Volcanic_eruptions_in_the_future_VAEs_first_future_pulse , VAES_pulse_duration , VAES_puls_repetition , 9999 ) * VAES_pulse_height
    idxlhs = fcol_in_mdf["Future_volcanic_emissions_shape_pulse_train"]
    mdf[rowi, idxlhs] = PULSE_TRAIN(
      zeit,   NEvt_2a_Volcanic_eruptions_in_the_future_VAEs_first_future_pulse,   VAES_pulse_duration,   VAES_puls_repetition,   VAES_pulse_height, )

    # Future_volcanic_emissions_shape = IF_THEN_ELSE ( Future_volcanic_eruptions_1_is_ON_0_is_OFF == 0 , 0 , Future_volcanic_emissions_shape_pulse_train )
    idxlhs = fcol_in_mdf["Future_volcanic_emissions_shape"]
    idx1 = fcol_in_mdf["Future_volcanic_emissions_shape_pulse_train"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      Future_volcanic_eruptions_1_is_ON_0_is_OFF == 0, 0, mdf[rowi, idx1]
    )

    # Future_volcanic_emissions = SMOOTH3 ( Future_volcanic_emissions_shape , FVE_shape_time )
    idx1 = fcol_in_mdf["Future_volcanic_emissions_shape"]
    idxin = fcol_in_mdf["Future_volcanic_emissions_shape"]
    idx2 = fcol_in_mdf["Future_volcanic_emissions_2"]
    idx1 = fcol_in_mdf["Future_volcanic_emissions_1"]
    idxout = fcol_in_mdf["Future_volcanic_emissions"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idxin] - mdf[rowi - 1, idx1]) / (FVE_shape_time / 3) * dt
    )
    mdf[rowi, idx2] = (
      mdf[rowi - 1, idx2]
      + (mdf[rowi - 1, idx1] - mdf[rowi - 1, idx2]) / (FVE_shape_time / 3) * dt
    )
    mdf[rowi, idxout] = (
      mdf[rowi - 1, idxout]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idxout]) / (FVE_shape_time / 3) * dt
    )

    # Volcanic_aerosols_emissions = IF_THEN_ELSE ( zeit < 2008 , Historical_aerosol_forcing_volcanic / Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions , Future_volcanic_emissions )
    idxlhs = fcol_in_mdf["Volcanic_aerosols_emissions"]
    idx1 = fcol_in_mdf["Historical_aerosol_forcing_volcanic"]
    idx2 = fcol_in_mdf["Future_volcanic_emissions"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit < 2008,   mdf[rowi, idx1]
      / Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions,   mdf[rowi, idx2], )

    # Avg_volcanic_activity_GtC_py = Volcanic_aerosols_emissions * Conversion_of_volcanic_aerosol_emissions_to_CO2_emissions_GtC_pr_VAE
    idxlhs = fcol_in_mdf["Avg_volcanic_activity_GtC_py"]
    idx1 = fcol_in_mdf["Volcanic_aerosols_emissions"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * Conversion_of_volcanic_aerosol_emissions_to_CO2_emissions_GtC_pr_VAE
    )

    # BB_radiation_at_atm_temp_in_atm_W_p_m2 = BB_radiation_at_Temp_in_atm_ZJ_py / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["BB_radiation_at_atm_temp_in_atm_W_p_m2"]
    idx1 = fcol_in_mdf["BB_radiation_at_Temp_in_atm_ZJ_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # Global_population_TLTL = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 4429.29 ) , ( 1981 , 4496.99 ) , ( 1982 , 4565.8 ) , ( 1983 , 4637.14 ) , ( 1984 , 4714.02 ) , ( 1985 , 4794.22 ) , ( 1986 , 4875.37 ) , ( 1987 , 4958.62 ) , ( 1988 , 5043.24 ) , ( 1989 , 5127.61 ) , ( 1990 , 5212.36 ) , ( 1991 , 5297.99 ) , ( 1992 , 5383.77 ) , ( 1993 , 5469.92 ) , ( 1994 , 5557.22 ) , ( 1995 , 5645.17 ) , ( 1996 , 5733.67 ) , ( 1997 , 5823.18 ) , ( 1998 , 5913.28 ) , ( 1999 , 6003.57 ) , ( 2000 , 6094.22 ) , ( 2001 , 6184.81 ) , ( 2002 , 6274.89 ) , ( 2003 , 6364.45 ) , ( 2004 , 6453.16 ) , ( 2005 , 6540.68 ) , ( 2006 , 6626.99 ) , ( 2007 , 6711.97 ) , ( 2008 , 6795.42 ) , ( 2009 , 6877.37 ) , ( 2010 , 6957.8 ) , ( 2011 , 7036.66 ) , ( 2012 , 7114 ) , ( 2013 , 7189.88 ) , ( 2014 , 7264.28 ) , ( 2015 , 7337.26 ) , ( 2016 , 7408.86 ) , ( 2017 , 7479.08 ) , ( 2018 , 7547.94 ) , ( 2019 , 7615.46 ) , ( 2020 , 7681.64 ) , ( 2021 , 7746.45 ) , ( 2022 , 7809.85 ) , ( 2023 , 7871.81 ) , ( 2024 , 7932.28 ) , ( 2025 , 7991.25 ) , ( 2026 , 8047.86 ) , ( 2027 , 8101.52 ) , ( 2028 , 8152.71 ) , ( 2029 , 8201.73 ) , ( 2030 , 8248.72 ) , ( 2031 , 8293.72 ) , ( 2032 , 8336.72 ) , ( 2033 , 8377.71 ) , ( 2034 , 8416.69 ) , ( 2035 , 8453.68 ) , ( 2036 , 8488.76 ) , ( 2037 , 8522.04 ) , ( 2038 , 8553.65 ) , ( 2039 , 8583.67 ) , ( 2040 , 8612.19 ) , ( 2041 , 8639.29 ) , ( 2042 , 8665.03 ) , ( 2043 , 8689.41 ) , ( 2044 , 8712.45 ) , ( 2045 , 8734.12 ) , ( 2046 , 8754.36 ) , ( 2047 , 8773.13 ) , ( 2048 , 8790.31 ) , ( 2049 , 8805.78 ) , ( 2050 , 8819.42 ) , ( 2051 , 8831.18 ) , ( 2052 , 8840.97 ) , ( 2053 , 8848.77 ) , ( 2054 , 8854.55 ) , ( 2055 , 8858.34 ) , ( 2056 , 8860.17 ) , ( 2057 , 8860.14 ) , ( 2058 , 8858.33 ) , ( 2059 , 8854.75 ) , ( 2060 , 8849.43 ) , ( 2061 , 8842.46 ) , ( 2062 , 8833.91 ) , ( 2063 , 8823.88 ) , ( 2064 , 8812.43 ) , ( 2065 , 8799.62 ) , ( 2066 , 8785.51 ) , ( 2067 , 8770.14 ) , ( 2068 , 8753.54 ) , ( 2069 , 8735.72 ) , ( 2070 , 8716.76 ) , ( 2071 , 8696.74 ) , ( 2072 , 8675.78 ) , ( 2073 , 8653.93 ) , ( 2074 , 8631.19 ) , ( 2075 , 8607.58 ) , ( 2076 , 8583.07 ) , ( 2077 , 8557.64 ) , ( 2078 , 8531.2 ) , ( 2079 , 8503.61 ) , ( 2080 , 8474.78 ) , ( 2081 , 8444.72 ) , ( 2082 , 8413.47 ) , ( 2083 , 8381.08 ) , ( 2084 , 8347.63 ) , ( 2085 , 8313.15 ) , ( 2086 , 8277.66 ) , ( 2087 , 8241.18 ) , ( 2088 , 8203.7 ) , ( 2089 , 8165.26 ) , ( 2090 , 8125.93 ) , ( 2091 , 8085.86 ) , ( 2092 , 8045.2 ) , ( 2093 , 8004.14 ) , ( 2094 , 7962.83 ) , ( 2095 , 7921.42 ) , ( 2096 , 7880.01 ) , ( 2097 , 7838.69 ) , ( 2098 , 7797.53 ) , ( 2099 , 7756.59 ) , ( 2100 , 7715.93 ) ) )
    tabidx = ftab_in_d_table["Global_population_TLTL"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_population_TLTL"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Effect_of_population_on_forest_degradation_and_biocapacity = Global_population / Global_population_TLTL
    idxlhs = fcol_in_mdf["Effect_of_population_on_forest_degradation_and_biocapacity"]
    idx1 = fcol_in_mdf["Global_population"]
    idx2 = fcol_in_mdf["Global_population_TLTL"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]

    # Biocapacity_with_population_effect = Biocapacity_reference / Effect_of_population_on_forest_degradation_and_biocapacity
    idxlhs = fcol_in_mdf["Biocapacity_with_population_effect"]
    idx1 = fcol_in_mdf["Effect_of_population_on_forest_degradation_and_biocapacity"]
    mdf[rowi, idxlhs] = Biocapacity_reference / mdf[rowi, idx1]

    # Biocapacity = IF_THEN_ELSE ( zeit >= 2020 , Biocapacity_with_population_effect , Biocapacity_reference )
    idxlhs = fcol_in_mdf["Biocapacity"]
    idx1 = fcol_in_mdf["Biocapacity_with_population_effect"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit >= 2020, mdf[rowi, idx1], Biocapacity_reference
    )

    # Global_GDPpp_USED = GDPpp_USED[us] * Regional_population_as_fraction_of_total[us] + GDPpp_USED[af] * Regional_population_as_fraction_of_total[af] + GDPpp_USED[cn] * Regional_population_as_fraction_of_total[cn] + GDPpp_USED[me] * Regional_population_as_fraction_of_total[me] + GDPpp_USED[sa] * Regional_population_as_fraction_of_total[sa] + GDPpp_USED[la] * Regional_population_as_fraction_of_total[la] + GDPpp_USED[pa] * Regional_population_as_fraction_of_total[pa] + GDPpp_USED[ec] * Regional_population_as_fraction_of_total[ec] + GDPpp_USED[eu] * Regional_population_as_fraction_of_total[eu] + GDPpp_USED[se] * Regional_population_as_fraction_of_total[se]
    idxlhs = fcol_in_mdf["Global_GDPpp_USED"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    idx2 = fcol_in_mdf["Regional_population_as_fraction_of_total"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1 + 0] * mdf[rowi, idx2 + 0]
      + mdf[rowi, idx1 + 1] * mdf[rowi, idx2 + 1]
      + mdf[rowi, idx1 + 2] * mdf[rowi, idx2 + 2]
      + mdf[rowi, idx1 + 3] * mdf[rowi, idx2 + 3]
      + mdf[rowi, idx1 + 4] * mdf[rowi, idx2 + 4]
      + mdf[rowi, idx1 + 5] * mdf[rowi, idx2 + 5]
      + mdf[rowi, idx1 + 6] * mdf[rowi, idx2 + 6]
      + mdf[rowi, idx1 + 7] * mdf[rowi, idx2 + 7]
      + mdf[rowi, idx1 + 8] * mdf[rowi, idx2 + 8]
      + mdf[rowi, idx1 + 9] * mdf[rowi, idx2 + 9]
    )

    # Effect_of_Wealth_on_non_energy_footprint = WITH LOOKUP ( Global_GDPpp_USED , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1.5 ) , ( 10 , 1.2 ) , ( 20 , 1 ) , ( 30 , 1.1 ) , ( 40 , 1.2 ) , ( 50 , 1.4 ) , ( 75 , 1.8 ) , ( 100 , 1.9 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_Wealth_on_non_energy_footprint"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Effect_of_Wealth_on_non_energy_footprint"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Global_GDPpp_USED"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Smoothed_Effect_of_Wealth_on_non_energy_footprint = SMOOTH ( Effect_of_Wealth_on_non_energy_footprint , Time_to_smooth_non_energy_footprint_changes )
    idx1 = fcol_in_mdf["Smoothed_Effect_of_Wealth_on_non_energy_footprint"]
    idx2 = fcol_in_mdf["Effect_of_Wealth_on_non_energy_footprint"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Time_to_smooth_non_energy_footprint_changes
      * dt
    )

    # Non_energy_footprint_future = Non_energy_footprint_pp_future * Global_population * UNIT_conv_to_Mha_footprint * Smoothed_Effect_of_Wealth_on_non_energy_footprint
    idxlhs = fcol_in_mdf["Non_energy_footprint_future"]
    idx1 = fcol_in_mdf["Non_energy_footprint_pp_future"]
    idx2 = fcol_in_mdf["Global_population"]
    idx3 = fcol_in_mdf["Smoothed_Effect_of_Wealth_on_non_energy_footprint"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * mdf[rowi, idx2] * UNIT_conv_to_Mha_footprint * mdf[rowi, idx3]
    )

    # Non_energy_footprint_pp = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.6 ) , ( 1985 , 1.5 ) , ( 1990 , 1.44 ) , ( 1995 , 1.35 ) , ( 2000 , 1.28 ) , ( 2005 , 1.24 ) , ( 2010 , 1.13 ) , ( 2015 , 1.04 ) , ( 2020 , 0.99 ) ) )
    tabidx = ftab_in_d_table["Non_energy_footprint_pp"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Non_energy_footprint_pp"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Non_energy_footprint_hist = Non_energy_footprint_pp * Global_population * UNIT_conv_to_Mha_footprint
    idxlhs = fcol_in_mdf["Non_energy_footprint_hist"]
    idx1 = fcol_in_mdf["Non_energy_footprint_pp"]
    idx2 = fcol_in_mdf["Global_population"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] * UNIT_conv_to_Mha_footprint

    # Non_energy_footprint = IF_THEN_ELSE ( zeit >= 2020 , Non_energy_footprint_future , Non_energy_footprint_hist )
    idxlhs = fcol_in_mdf["Non_energy_footprint"]
    idx1 = fcol_in_mdf["Non_energy_footprint_future"]
    idx2 = fcol_in_mdf["Non_energy_footprint_hist"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit >= 2020, mdf[rowi, idx1], mdf[rowi, idx2])

    # Smoothed_Non_energy_footprint = SMOOTH ( Non_energy_footprint , Time_to_smooth_non_energy_footprint_changes )
    idx1 = fcol_in_mdf["Smoothed_Non_energy_footprint"]
    idx2 = fcol_in_mdf["Non_energy_footprint"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Time_to_smooth_non_energy_footprint_changes
      * dt
    )

    # Biocapacity_fraction_unused = ( Biocapacity - Smoothed_Non_energy_footprint ) / Biocapacity
    idxlhs = fcol_in_mdf["Biocapacity_fraction_unused"]
    idx1 = fcol_in_mdf["Biocapacity"]
    idx2 = fcol_in_mdf["Smoothed_Non_energy_footprint"]
    idx3 = fcol_in_mdf["Biocapacity"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] - mdf[rowi, idx2]) / mdf[rowi, idx3]

    # Biocapacity_risk_score = IF_THEN_ELSE ( Biocapacity_fraction_unused < pb_Biodiversity_loss_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Biocapacity_risk_score"]
    idx1 = fcol_in_mdf["Biocapacity_fraction_unused"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] < pb_Biodiversity_loss_green_threshold, 1, 0
    )

    # Effect_of_C_concentration_on_NMPP = 1 + LN ( Avg_C_concentration_in_top_layer / Concentration_of_C_in_ocean_top_layer_in_1850 ) / LN ( 2 )
    idxlhs = fcol_in_mdf["Effect_of_C_concentration_on_NMPP"]
    idx1 = fcol_in_mdf["Avg_C_concentration_in_top_layer"]
    mdf[rowi, idxlhs] = 1 + math.log(
      mdf[rowi, idx1] / Concentration_of_C_in_ocean_top_layer_in_1850
    ) / math.log(2)

    # Temp_of_cold_downwelling_water = ( Temp_of_cold_surface_water + Temp_ocean_deep_in_C ) / 2
    idxlhs = fcol_in_mdf["Temp_of_cold_downwelling_water"]
    idx1 = fcol_in_mdf["Temp_of_cold_surface_water"]
    idx2 = fcol_in_mdf["Temp_ocean_deep_in_C"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2]) / 2

    # Carbon_concentration_in_CWTtB = C_in_cold_water_trunk_downwelling_GtC / ( Cold_water_volume_downwelling_Gm3 + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_cold_ocean_downwelling_of_total )
    idxlhs = fcol_in_mdf["Carbon_concentration_in_CWTtB"]
    idx1 = fcol_in_mdf["C_in_cold_water_trunk_downwelling_GtC"]
    idx2 = fcol_in_mdf["Cold_water_volume_downwelling_Gm3"]
    idx3 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (
      mdf[rowi, idx2]
      + mdf[rowi, idx3]
      * UNIT_conversion_km3_to_Gm3
      * Frac_vol_cold_ocean_downwelling_of_total
    )

    # CC_in_cold_downwelling_ymoles_per_litre = Carbon_concentration_in_CWTtB * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
    idxlhs = fcol_in_mdf["CC_in_cold_downwelling_ymoles_per_litre"]
    idx1 = fcol_in_mdf["Carbon_concentration_in_CWTtB"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre

    # CC_in_cold_downwelling_ymoles_per_litre_dmnl = CC_in_cold_downwelling_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
    idxlhs = fcol_in_mdf["CC_in_cold_downwelling_ymoles_per_litre_dmnl"]
    idx1 = fcol_in_mdf["CC_in_cold_downwelling_ymoles_per_litre"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_ymoles_p_litre_to_dless

    # ph_in_cold_downwelling_water = UNIT_conversion_C_to_pH * ( 1 - 0.0017 * Temp_of_cold_downwelling_water - 0.0003 ) * ( 163.2 * CC_in_cold_downwelling_ymoles_per_litre_dmnl ^ ( - 0.385 ) )
    idxlhs = fcol_in_mdf["ph_in_cold_downwelling_water"]
    idx1 = fcol_in_mdf["Temp_of_cold_downwelling_water"]
    idx2 = fcol_in_mdf["CC_in_cold_downwelling_ymoles_per_litre_dmnl"]
    mdf[rowi, idxlhs] = (
      UNIT_conversion_C_to_pH
      * (1 - 0.0017 * mdf[rowi, idx1] - 0.0003)
      * (163.2 * mdf[rowi, idx2] ** (-0.385))
    )

    # Effect_of_acidification_on_NMPP = 1 + Slope_of_efffect_of_acidification_on_NMPP * ( ph_in_cold_downwelling_water / ph_in_cold_water_in_1980 - 1 )
    idxlhs = fcol_in_mdf["Effect_of_acidification_on_NMPP"]
    idx1 = fcol_in_mdf["ph_in_cold_downwelling_water"]
    mdf[rowi, idxlhs] = 1 + Slope_of_efffect_of_acidification_on_NMPP * (
      mdf[rowi, idx1] / ph_in_cold_water_in_1980 - 1
    )

    # Effect_of_temperature_on_NMPP = 1 + Slope_Effect_Temp_on_NMPP * ( Temp_surface / ( Temp_surface_1850 - 273.15 ) - 1 )
    idxlhs = fcol_in_mdf["Effect_of_temperature_on_NMPP"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = 1 + Slope_Effect_Temp_on_NMPP * (
      mdf[rowi, idx1] / (Temp_surface_1850 - 273.15) - 1
    )

    # Net_marine_primary_production_NMPP_GtC_pr_yr = Net_marine_primary_production_in_1850 * Effect_of_C_concentration_on_NMPP * Effect_of_acidification_on_NMPP * Effect_of_temperature_on_NMPP
    idxlhs = fcol_in_mdf["Net_marine_primary_production_NMPP_GtC_pr_yr"]
    idx1 = fcol_in_mdf["Effect_of_C_concentration_on_NMPP"]
    idx2 = fcol_in_mdf["Effect_of_acidification_on_NMPP"]
    idx3 = fcol_in_mdf["Effect_of_temperature_on_NMPP"]
    mdf[rowi, idxlhs] = (
      Net_marine_primary_production_in_1850
      * mdf[rowi, idx1]
      * mdf[rowi, idx2]
      * mdf[rowi, idx3]
    )

    # Biological_removal_of_C_from_WSW_GtC_per_yr = SMOOTH ( Net_marine_primary_production_NMPP_GtC_pr_yr , Time_to_let_shells_form_and_sink_to_sediment_yr )
    idx1 = fcol_in_mdf["Biological_removal_of_C_from_WSW_GtC_per_yr"]
    idx2 = fcol_in_mdf["Net_marine_primary_production_NMPP_GtC_pr_yr"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idx1])
      / Time_to_let_shells_form_and_sink_to_sediment_yr
      * dt
    )

    # birth_rate_CN = ( birth_rate_a_CN * math.exp ( birth_rate_b_CN * GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) - birth_rate_c_CN * math.exp ( birth_rate_d_CN * GDPpp_USED[cn] * UNIT_conv_to_make_exp_dmnl ) ) * UNIT_conv_to_make_the_bell_shaped_birth_rate_formula_have_units_of_1_pr_y
    idxlhs = fcol_in_mdf["birth_rate_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      birth_rate_a_CN
      * math.exp(birth_rate_b_CN * mdf[rowi, idx1 + 2] * UNIT_conv_to_make_exp_dmnl)
      - birth_rate_c_CN
      * math.exp(birth_rate_d_CN * mdf[rowi, idx2 + 2] * UNIT_conv_to_make_exp_dmnl)
    ) * UNIT_conv_to_make_the_bell_shaped_birth_rate_formula_have_units_of_1_pr_y

    # birth_rate_WO_CN[region] = birth_rate_a[region] * ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) ^ birth_rate_b[region] + birth_rate_c[region]
    idxlhs = fcol_in_mdf["birth_rate_WO_CN"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (birth_rate_a[j]
        * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** birth_rate_b[j]
        + birth_rate_c[j]
      )

    # birth_rate_as_f_GDPpp_alone[region] = IF_THEN_ELSE ( j==2 , birth_rate_CN , birth_rate_WO_CN )
    idxlhs = fcol_in_mdf["birth_rate_as_f_GDPpp_alone"]
    idx1 = fcol_in_mdf["birth_rate_CN"]
    idx2 = fcol_in_mdf["birth_rate_WO_CN"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 2, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # birth_rate[region] = SMOOTH3 ( birth_rate_as_f_GDPpp_alone[region] , Time_to_adjust_cultural_birth_rate_norm[region] )
    idxin = fcol_in_mdf["birth_rate_as_f_GDPpp_alone"]
    idx2 = fcol_in_mdf["birth_rate_2"]
    idx1 = fcol_in_mdf["birth_rate_1"]
    idxout = fcol_in_mdf["birth_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_adjust_cultural_birth_rate_norm[j] / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_adjust_cultural_birth_rate_norm[j] / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_adjust_cultural_birth_rate_norm[j] / 3)
        * dt
      )

    # Cohort_15_to_45[region] = Cohort_15_to_19[region] + Cohort_20_to_24[region] + Cohort_25_to_29[region] + Cohort_30_to_34[region] + Cohort_35_to_39[region] + Cohort_40_to_44[region]
    idxlhs = fcol_in_mdf["Cohort_15_to_45"]
    idx1 = fcol_in_mdf["Cohort_15_to_19"]
    idx2 = fcol_in_mdf["Cohort_20_to_24"]
    idx3 = fcol_in_mdf["Cohort_25_to_29"]
    idx4 = fcol_in_mdf["Cohort_30_to_34"]
    idx5 = fcol_in_mdf["Cohort_35_to_39"]
    idx6 = fcol_in_mdf["Cohort_40_to_44"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
      )

    # Births[region] = Cohort_15_to_45[region] * Births_effect_from_cohorts_outside_15_to_45[region] * birth_rate[region] * FEHC_mult_used[region]
    idxlhs = fcol_in_mdf["Births"]
    idx1 = fcol_in_mdf["Cohort_15_to_45"]
    idx2 = fcol_in_mdf["birth_rate"]
    idx3 = fcol_in_mdf["FEHC_mult_used"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Births_effect_from_cohorts_outside_15_to_45[j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
      )

    # Eff_of_env_damage_on_costs_of_TAs[region] = math.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_cost_of_TAs ) / Actual_eff_of_relative_wealth_on_env_damage[region]
    idxlhs = fcol_in_mdf["Eff_of_env_damage_on_costs_of_TAs"]
    idx1 = fcol_in_mdf["Combined_env_damage_indicator"]
    idx2 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (math.exp(mdf[rowi, idx1] * expSoE_of_ed_on_cost_of_TAs) / mdf[rowi, idx2 + j]
      )

    # Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_empowerment_PES[region] * Eff_of_env_damage_on_costs_of_TAs[region] / Reform_willingness_scaled_to_today[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform"
    ]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_empowerment_PES"]
    idx2 = fcol_in_mdf["Eff_of_env_damage_on_costs_of_TAs"]
    idx3 = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_energy_PES[region] * Eff_of_env_damage_on_costs_of_TAs[region] / Reform_willingness_scaled_to_today[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform"
    ]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_energy_PES"]
    idx2 = fcol_in_mdf["Eff_of_env_damage_on_costs_of_TAs"]
    idx3 = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_inequality_PES[region] * Eff_of_env_damage_on_costs_of_TAs[region] / Reform_willingness_scaled_to_today[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform"
    ]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_inequality_PES"]
    idx2 = fcol_in_mdf["Eff_of_env_damage_on_costs_of_TAs"]
    idx3 = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_food_PES[region] * Eff_of_env_damage_on_costs_of_TAs[region] / Reform_willingness_scaled_to_today[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform"
    ]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_food_PES"]
    idx2 = fcol_in_mdf["Eff_of_env_damage_on_costs_of_TAs"]
    idx3 = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform[region] = Each_region_max_cost_estimate_poverty_PES[region] * Eff_of_env_damage_on_costs_of_TAs[region] / Reform_willingness_scaled_to_today[region]
    idxlhs = fcol_in_mdf["Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform"
    ]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_poverty_PES"]
    idx2 = fcol_in_mdf["Eff_of_env_damage_on_costs_of_TAs"]
    idx3 = fcol_in_mdf["Reform_willingness_scaled_to_today"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / mdf[rowi, idx3 + j]
      )

    # Budget_for_all_TA_per_region[region] = ( Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform[region] + Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform[region] ) * Fraction_of_budget_available_for_policies
    idxlhs = fcol_in_mdf["Budget_for_all_TA_per_region"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform"
    ]
    idx2 = fcol_in_mdf["Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform"
    ]
    idx3 = fcol_in_mdf["Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform"
    ]
    idx4 = fcol_in_mdf["Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform"]
    idx5 = fcol_in_mdf["Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
      ) * Fraction_of_budget_available_for_policies

    # CO2_conc_in_cold_surface_water_in_ppm = CC_in_cold_surface_ymoles_per_litre * Conversion_ymoles_per_kg_to_pCO2_yatm
    idxlhs = fcol_in_mdf["CO2_conc_in_cold_surface_water_in_ppm"]
    idx1 = fcol_in_mdf["CC_in_cold_surface_ymoles_per_litre"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Conversion_ymoles_per_kg_to_pCO2_yatm

    # CO2_conc_atm_less_CO2_conc_sea = CO2_concentration_used_after_any_experiments_ppm - CO2_conc_in_cold_surface_water_in_ppm
    idxlhs = fcol_in_mdf["CO2_conc_atm_less_CO2_conc_sea"]
    idx1 = fcol_in_mdf["CO2_concentration_used_after_any_experiments_ppm"]
    idx2 = fcol_in_mdf["CO2_conc_in_cold_surface_water_in_ppm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # Guldberg_Waage_air_sea_formulation = ( CO2_conc_atm_less_CO2_conc_sea * Conversion_constant_GtC_to_ppm ) / Time_to_reach_C_equilibrium_between_atmosphere_and_ocean
    idxlhs = fcol_in_mdf["Guldberg_Waage_air_sea_formulation"]
    idx1 = fcol_in_mdf["CO2_conc_atm_less_CO2_conc_sea"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Conversion_constant_GtC_to_ppm
    ) / Time_to_reach_C_equilibrium_between_atmosphere_and_ocean

    # NatEvent_d_slowing_down_ocean_circulation_from_2015 = IF_THEN_ELSE ( zeit > 2015 , Ocean_slowdown_experimental_factor , 1 )
    idxlhs = fcol_in_mdf["NatEvent_d_slowing_down_ocean_circulation_from_2015"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit > 2015, Ocean_slowdown_experimental_factor, 1)

    # Time_less_Greenland_slide_experiment_start_yr = zeit - NEvt_13d_Greenland_slide_experiment_start_yr
    idxlhs = fcol_in_mdf["Time_less_Greenland_slide_experiment_start_yr"]
    mdf[rowi, idxlhs] = zeit - NEvt_13d_Greenland_slide_experiment_start_yr

    # Ocean_circulation_slowdown_from_Greenland_ice_sliding_into_the_Atlantic = MAX ( 1 - Greenland_ice_slide_circulation_slowdown_effect , MIN ( 1 , 1 - Time_less_Greenland_slide_experiment_start_yr / ( Greenland_slide_experiment_over_how_many_years_yr + Time_to_melt_greenland_ice_that_slid_into_the_ocean_at_the_reference_delta_temp ) * ( 1 - Greenland_ice_slide_circulation_slowdown_effect ) ) )
    idxlhs = fcol_in_mdf["Ocean_circulation_slowdown_from_Greenland_ice_sliding_into_the_Atlantic"
    ]
    idx1 = fcol_in_mdf["Time_less_Greenland_slide_experiment_start_yr"]
    mdf[rowi, idxlhs] = max(
      1 - Greenland_ice_slide_circulation_slowdown_effect,   min(
        1,     1
        - mdf[rowi, idx1]
        / (
          Greenland_slide_experiment_over_how_many_years_yr
          + Time_to_melt_greenland_ice_that_slid_into_the_ocean_at_the_reference_delta_temp
        )
        * (1 - Greenland_ice_slide_circulation_slowdown_effect),   ), )

    # C_diffusion_into_ocean_from_atm_net = Guldberg_Waage_air_sea_formulation * NatEvent_d_slowing_down_ocean_circulation_from_2015 * Ocean_circulation_slowdown_from_Greenland_ice_sliding_into_the_Atlantic
    idxlhs = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    idx1 = fcol_in_mdf["Guldberg_Waage_air_sea_formulation"]
    idx2 = fcol_in_mdf["NatEvent_d_slowing_down_ocean_circulation_from_2015"]
    idx3 = fcol_in_mdf["Ocean_circulation_slowdown_from_Greenland_ice_sliding_into_the_Atlantic"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2] * mdf[rowi, idx3]

    # C_absorption_by_ocean_from_atm_for_accumulation = C_diffusion_into_ocean_from_atm_net
    idxlhs = fcol_in_mdf["C_absorption_by_ocean_from_atm_for_accumulation"]
    idx1 = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Ocean_sink_C_diffusion_into_ocean_from_atm = IF_THEN_ELSE ( C_diffusion_into_ocean_from_atm_net >= 0 , C_diffusion_into_ocean_from_atm_net , 0 )
    idxlhs = fcol_in_mdf["Ocean_sink_C_diffusion_into_ocean_from_atm"]
    idx1 = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    idx2 = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] >= 0, mdf[rowi, idx2], 0)

    # Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture = SUM ( Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture[region!] ) / UNIT_conv_CO2_to_C
    idxlhs = fcol_in_mdf["Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture"
    ]
    idx1 = fcol_in_mdf["Actual_CO2_taken_directly_out_of_the_atmosphere_ie_direct_air_capture"
    ]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j] / UNIT_conv_CO2_to_C
    mdf[rowi, idxlhs] = globsum

    # Total_use_of_fossil_fuels_BEING_compensated[region] = Total_use_of_fossil_fuels[region] * Fraction_of_fossil_fuels_compensated_by_CCS[region]
    idxlhs = fcol_in_mdf["Total_use_of_fossil_fuels_BEING_compensated"]
    idx1 = fcol_in_mdf["Total_use_of_fossil_fuels"]
    idx2 = fcol_in_mdf["Fraction_of_fossil_fuels_compensated_by_CCS"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Total_CCS_from_fossil_fuels_BEING_compensated[region] = IF_THEN_ELSE ( Total_use_of_fossil_fuels_BEING_compensated == 0 , 0 , toe_to_CO2_a * ( Total_use_of_fossil_fuels_BEING_compensated * UNIT_conv_to_Gtoe ) + toe_to_CO2_b )
    idxlhs = fcol_in_mdf["Total_CCS_from_fossil_fuels_BEING_compensated"]
    idx1 = fcol_in_mdf["Total_use_of_fossil_fuels_BEING_compensated"]
    idx2 = fcol_in_mdf["Total_use_of_fossil_fuels_BEING_compensated"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] == 0,     0,     toe_to_CO2_a[j] * (mdf[rowi, idx2 + j] * UNIT_conv_to_Gtoe) + toe_to_CO2_b[j],   )

    # Global_Total_CCS_from_fossil_fuels_BEING_compensated = SUM ( Total_CCS_from_fossil_fuels_BEING_compensated[region!] )
    idxlhs = fcol_in_mdf["Global_Total_CCS_from_fossil_fuels_BEING_compensated"]
    idx1 = fcol_in_mdf["Total_CCS_from_fossil_fuels_BEING_compensated"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Carbon_captured_and_stored_GtC_py = Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture + Global_Total_CCS_from_fossil_fuels_BEING_compensated / UNIT_conv_CO2_to_C
    idxlhs = fcol_in_mdf["Carbon_captured_and_stored_GtC_py"]
    idx1 = fcol_in_mdf["Global_C_taken_directly_out_of_the_atmosphere_ie_direct_air_capture"
    ]
    idx2 = fcol_in_mdf["Global_Total_CCS_from_fossil_fuels_BEING_compensated"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] / UNIT_conv_CO2_to_C

    # Flow_of_C_from_atm_GtC_py = Ocean_sink_C_diffusion_into_ocean_from_atm + Carbon_captured_and_stored_GtC_py + CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py + CO2_flux_from_atm_to_NF_for_new_growth_GtC_py + CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py + CO2_flux_from_atm_to_TUNDRA_for_new_growth
    idxlhs = fcol_in_mdf["Flow_of_C_from_atm_GtC_py"]
    idx1 = fcol_in_mdf["Ocean_sink_C_diffusion_into_ocean_from_atm"]
    idx2 = fcol_in_mdf["Carbon_captured_and_stored_GtC_py"]
    idx3 = fcol_in_mdf["CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py"]
    idx4 = fcol_in_mdf["CO2_flux_from_atm_to_NF_for_new_growth_GtC_py"]
    idx5 = fcol_in_mdf["CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py"]
    idx6 = fcol_in_mdf["CO2_flux_from_atm_to_TUNDRA_for_new_growth"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
    )

    # C_in_NF_LB_GtC = NF_Living_biomass_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_NF_LB_GtC"]
    idx1 = fcol_in_mdf["NF_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_NF_DeadB_and_soil_GtC = NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_NF_DeadB_and_soil_GtC"]
    idx1 = fcol_in_mdf["NF_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_NF_GtC = C_in_NF_LB_GtC + C_in_NF_DeadB_and_soil_GtC + NF_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_NF_GtC"]
    idx1 = fcol_in_mdf["C_in_NF_LB_GtC"]
    idx2 = fcol_in_mdf["C_in_NF_DeadB_and_soil_GtC"]
    idx3 = fcol_in_mdf["NF_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] * Carbon_per_biomass
    )

    # C_in_TROP_LB_GtC = TROP_Living_biomass_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_TROP_LB_GtC"]
    idx1 = fcol_in_mdf["TROP_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_TROP_DeadB_and_soil_GtC = TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_TROP_DeadB_and_soil_GtC"]
    idx1 = fcol_in_mdf["TROP_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_TROP_GtC = C_in_TROP_LB_GtC + C_in_TROP_DeadB_and_soil_GtC + TROP_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_TROP_GtC"]
    idx1 = fcol_in_mdf["C_in_TROP_LB_GtC"]
    idx2 = fcol_in_mdf["C_in_TROP_DeadB_and_soil_GtC"]
    idx3 = fcol_in_mdf["TROP_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] * Carbon_per_biomass
    )

    # C_in_GRASS_LB_GtC = GRASS_Living_biomass_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_GRASS_LB_GtC"]
    idx1 = fcol_in_mdf["GRASS_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_GRASS_DeadB_and_soil_GtC = GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_GRASS_DeadB_and_soil_GtC"]
    idx1 = fcol_in_mdf["GRASS_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_GRASS_GtC = C_in_GRASS_LB_GtC + C_in_GRASS_DeadB_and_soil_GtC + GRASS_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_GRASS_GtC"]
    idx1 = fcol_in_mdf["C_in_GRASS_LB_GtC"]
    idx2 = fcol_in_mdf["C_in_GRASS_DeadB_and_soil_GtC"]
    idx3 = fcol_in_mdf["GRASS_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] * Carbon_per_biomass
    )

    # C_in_TUNDRA_LB_GtC = TUNDRA_Living_biomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_TUNDRA_LB_GtC"]
    idx1 = fcol_in_mdf["TUNDRA_Living_biomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_TUNDRA_DeadB_and_soil_GtC = TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_TUNDRA_DeadB_and_soil_GtC"]
    idx1 = fcol_in_mdf["TUNDRA_Dead_biomass_litter_and_soil_organic_matter_SOM_GtBiomass"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Carbon_per_biomass

    # C_in_TUNDRA_GtC = C_in_TUNDRA_LB_GtC + C_in_TUNDRA_DeadB_and_soil_GtC + TUNDRA_Biomass_locked_in_construction_material_GtBiomass * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_in_TUNDRA_GtC"]
    idx1 = fcol_in_mdf["C_in_TUNDRA_LB_GtC"]
    idx2 = fcol_in_mdf["C_in_TUNDRA_DeadB_and_soil_GtC"]
    idx3 = fcol_in_mdf["TUNDRA_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] * Carbon_per_biomass
    )

    # C_release_from_permafrost_melting_as_CO2_GtC_py = CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint * Melting_restraint_for_permafrost_from_heat_in_atmophere * ( 1 - Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl )
    idxlhs = fcol_in_mdf["C_release_from_permafrost_melting_as_CO2_GtC_py"]
    idx1 = fcol_in_mdf["CH4_in_permafrost_area_melted_or_frozen_before_heat_constraint"]
    idx2 = fcol_in_mdf["Melting_restraint_for_permafrost_from_heat_in_atmophere"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * mdf[rowi, idx2]
      * (1 - Fraction_of_C_released_from_permafrost_released_as_CH4_dmnl)
    )

    # C_released_from_permafrost_as_either_CH4_or_CO2_in_GtC_py = C_release_from_permafrost_melting_as_CO2_GtC_py + CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py
    idxlhs = fcol_in_mdf["C_released_from_permafrost_as_either_CH4_or_CO2_in_GtC_py"]
    idx1 = fcol_in_mdf["C_release_from_permafrost_melting_as_CO2_GtC_py"]
    idx2 = fcol_in_mdf["CH4_release_or_capture_from_permafrost_area_loss_or_gain_GtC_py"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # C_runoff_from_biomass_soil = ( TROP_runoff + NF_runoff + GRASS_runoff + TUNDRA_runoff ) * Carbon_per_biomass
    idxlhs = fcol_in_mdf["C_runoff_from_biomass_soil"]
    idx1 = fcol_in_mdf["TROP_runoff"]
    idx2 = fcol_in_mdf["NF_runoff"]
    idx3 = fcol_in_mdf["GRASS_runoff"]
    idx4 = fcol_in_mdf["TUNDRA_runoff"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    ) * Carbon_per_biomass

    # c_to_acgl[region] = abs ( MIN ( 0 , Cropland_gap[region] ) ) / Time_for_agri_land_to_become_abandoned
    idxlhs = fcol_in_mdf["c_to_acgl"]
    idx1 = fcol_in_mdf["Cropland_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (abs(min(0, mdf[rowi, idx1 + j])) / Time_for_agri_land_to_become_abandoned
      )

    # c_to_pl[region] = MAX ( 0 , Populated_land_gap[region] ) * Fraction_of_cropland_developed_for_urban_land
    idxlhs = fcol_in_mdf["c_to_pl"]
    idx1 = fcol_in_mdf["Populated_land_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (max(0, mdf[rowi, idx1 + j]) * Fraction_of_cropland_developed_for_urban_land
      )

    # Private_Investment_in_new_capacity[region] = Available_private_capital_for_investment[region] * Fraction_of_available_capital_to_new_capacity[region]
    idxlhs = fcol_in_mdf["Private_Investment_in_new_capacity"]
    idx1 = fcol_in_mdf["Available_private_capital_for_investment"]
    idx2 = fcol_in_mdf["Fraction_of_available_capital_to_new_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Govt_investment_in_public_capacity[region] = Actual_govt_cash_inflow_seasonally_adjusted[region] - Govt_consumption_ie_purchases[region]
    idxlhs = fcol_in_mdf["Govt_investment_in_public_capacity"]
    idx1 = fcol_in_mdf["Actual_govt_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Govt_consumption_ie_purchases"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Increase_in_public_capacity[region] = ( Govt_investment_in_public_capacity[region] + Public_money_from_LPB_policy_to_investment[region] ) * ( 1 - Future_leakage[region] )
    idxlhs = fcol_in_mdf["Increase_in_public_capacity"]
    idx1 = fcol_in_mdf["Govt_investment_in_public_capacity"]
    idx2 = fcol_in_mdf["Public_money_from_LPB_policy_to_investment"]
    idx3 = fcol_in_mdf["Future_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]) * (
        1 - mdf[rowi, idx3 + j]
      )

    # Eff_of_env_damage_on_cost_of_new_capacity[region] = math.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_cost_of_new_capacity ) / Actual_eff_of_relative_wealth_on_env_damage[region]
    idxlhs = fcol_in_mdf["Eff_of_env_damage_on_cost_of_new_capacity"]
    idx1 = fcol_in_mdf["Combined_env_damage_indicator"]
    idx2 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (math.exp(mdf[rowi, idx1] * expSoE_of_ed_on_cost_of_new_capacity)
        / mdf[rowi, idx2 + j]
      )

    # Initiating_capacity_construction[region] = MAX ( ( Private_Investment_in_new_capacity[region] * ( 1 - Future_leakage[region] ) + Increase_in_public_capacity[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] , 0 )
    idxlhs = fcol_in_mdf["Initiating_capacity_construction"]
    idx1 = fcol_in_mdf["Private_Investment_in_new_capacity"]
    idx2 = fcol_in_mdf["Future_leakage"]
    idx3 = fcol_in_mdf["Increase_in_public_capacity"]
    idx4 = fcol_in_mdf["Eff_of_env_damage_on_cost_of_new_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        (mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j]) + mdf[rowi, idx3 + j])
        / mdf[rowi, idx4 + j],     0,   )

    # Capacity_renewal_rate[region] = Initiating_capacity_construction[region] / Capacity[region]
    idxlhs = fcol_in_mdf["Capacity_renewal_rate"]
    idx1 = fcol_in_mdf["Initiating_capacity_construction"]
    idx2 = fcol_in_mdf["Capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Carbon_concentration_in_deep_box_GtC_per_G_cubicM = C_in_deep_water_volume_1km_to_bottom_GtC / ( Deep_water_volume_1km_to_4km_Gm3 + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_deep_ocean_of_total )
    idxlhs = fcol_in_mdf["Carbon_concentration_in_deep_box_GtC_per_G_cubicM"]
    idx1 = fcol_in_mdf["C_in_deep_water_volume_1km_to_bottom_GtC"]
    idx2 = fcol_in_mdf["Deep_water_volume_1km_to_4km_Gm3"]
    idx3 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (
      mdf[rowi, idx2]
      + mdf[rowi, idx3] * UNIT_conversion_km3_to_Gm3 * Frac_vol_deep_ocean_of_total
    )

    # Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM = C_in_intermediate_upwelling_water_100m_to_1km_GtC / ( Intermediate_upwelling_water_volume_100m_to_1km_Gm3 + Cumulative_ocean_volume_increase_due_to_ice_melting_km3 * UNIT_conversion_km3_to_Gm3 * Frac_vol_ocean_upwelling_of_total )
    idxlhs = fcol_in_mdf["Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM"]
    idx1 = fcol_in_mdf["C_in_intermediate_upwelling_water_100m_to_1km_GtC"]
    idx2 = fcol_in_mdf["Intermediate_upwelling_water_volume_100m_to_1km_Gm3"]
    idx3 = fcol_in_mdf["Cumulative_ocean_volume_increase_due_to_ice_melting_km3"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (
      mdf[rowi, idx2]
      + mdf[rowi, idx3] * UNIT_conversion_km3_to_Gm3 * Frac_vol_ocean_upwelling_of_total
    )

    # Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr = C_in_cold_surface_water_GtC / Time_in_cold
    idxlhs = fcol_in_mdf["Carbon_flow_from_cold_surface_downwelling_Gtc_per_yr"]
    idx1 = fcol_in_mdf["C_in_cold_surface_water_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_in_cold

    # Carbon_flow_from_cold_to_deep_GtC_per_yr = C_in_cold_water_trunk_downwelling_GtC / Time_in_trunk
    idxlhs = fcol_in_mdf["Carbon_flow_from_cold_to_deep_GtC_per_yr"]
    idx1 = fcol_in_mdf["C_in_cold_water_trunk_downwelling_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_in_trunk

    # Carbon_flow_from_deep = C_in_deep_water_volume_1km_to_bottom_GtC / Time_in_deep
    idxlhs = fcol_in_mdf["Carbon_flow_from_deep"]
    idx1 = fcol_in_mdf["C_in_deep_water_volume_1km_to_bottom_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_in_deep

    # Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr = C_in_intermediate_upwelling_water_100m_to_1km_GtC / Time_in_intermediate_yr
    idxlhs = fcol_in_mdf["Carbon_flow_from_intermediate_to_surface_box_GtC_per_yr"]
    idx1 = fcol_in_mdf["C_in_intermediate_upwelling_water_100m_to_1km_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_in_intermediate_yr

    # Carbon_flow_from_warm_to_cold_surface_GtC_per_yr = C_in_warm_surface_water_GtC / Time_in_warm
    idxlhs = fcol_in_mdf["Carbon_flow_from_warm_to_cold_surface_GtC_per_yr"]
    idx1 = fcol_in_mdf["C_in_warm_surface_water_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_in_warm

    # Carbon_intensity_last_year[region] = SMOOTH3 ( Carbon_intensity[region] , One_year )
    idxin = fcol_in_mdf["Carbon_intensity"]
    idx2 = fcol_in_mdf["Carbon_intensity_last_year_2"]
    idx1 = fcol_in_mdf["Carbon_intensity_last_year_1"]
    idxout = fcol_in_mdf["Carbon_intensity_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # CC_in_deep_box_ymoles_per_litre = Carbon_concentration_in_deep_box_GtC_per_G_cubicM * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
    idxlhs = fcol_in_mdf["CC_in_deep_box_ymoles_per_litre"]
    idx1 = fcol_in_mdf["Carbon_concentration_in_deep_box_GtC_per_G_cubicM"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre

    # CC_in_deep_box_ymoles_per_litre_dmnl = CC_in_deep_box_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
    idxlhs = fcol_in_mdf["CC_in_deep_box_ymoles_per_litre_dmnl"]
    idx1 = fcol_in_mdf["CC_in_deep_box_ymoles_per_litre"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_ymoles_p_litre_to_dless

    # CC_in_intermediate_box_ymoles_per_litre = Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre
    idxlhs = fcol_in_mdf["CC_in_intermediate_box_ymoles_per_litre"]
    idx1 = fcol_in_mdf["Carbon_concentration_in_intermdiate_box_GtC_per_G_cubicM"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_converter_GtC_p_Gm3_to_ymoles_p_litre

    # CC_in_intermediate_box_ymoles_per_litre_dmnl = CC_in_intermediate_box_ymoles_per_litre * UNIT_conversion_ymoles_p_litre_to_dless
    idxlhs = fcol_in_mdf["CC_in_intermediate_box_ymoles_per_litre_dmnl"]
    idx1 = fcol_in_mdf["CC_in_intermediate_box_ymoles_per_litre"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_ymoles_p_litre_to_dless

    # Rate_of_destruction_of_wetlands = STEP ( Wetlands_area * Rate_of_wetland_destruction_pct_of_existing_wetlands_py / 100 , When_first_destroyed_yr ) - STEP ( Wetlands_area * Rate_of_wetland_destruction_pct_of_existing_wetlands_py / 100 , When_first_destroyed_yr + Duration_of_destruction_yr )
    idxlhs = fcol_in_mdf["Rate_of_destruction_of_wetlands"]
    idx1 = fcol_in_mdf["Wetlands_area"]
    idx2 = fcol_in_mdf["Wetlands_area"]
    mdf[rowi, idxlhs] = STEP(
      zeit,   mdf[rowi, idx1] * Rate_of_wetland_destruction_pct_of_existing_wetlands_py / 100,   When_first_destroyed_yr, ) - STEP(
      zeit,   mdf[rowi, idx2] * Rate_of_wetland_destruction_pct_of_existing_wetlands_py / 100,   When_first_destroyed_yr + Duration_of_destruction_yr, )

    # CH4_emissions_from_wetlands_destruction = Rate_of_destruction_of_wetlands * CH4_per_sqkm_of_wetlands
    idxlhs = fcol_in_mdf["CH4_emissions_from_wetlands_destruction"]
    idx1 = fcol_in_mdf["Rate_of_destruction_of_wetlands"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * CH4_per_sqkm_of_wetlands

    # Natural_CH4_emissions = ( CH4_emissions_from_wetlands_destruction + Emissions_of_natural_CH4_GtC_py )
    idxlhs = fcol_in_mdf["Natural_CH4_emissions"]
    idx1 = fcol_in_mdf["CH4_emissions_from_wetlands_destruction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + Emissions_of_natural_CH4_GtC_py

    # CH4_conversion_to_CO2_and_H2O = C_in_atmosphere_in_form_of_CH4 / CH4_halflife_in_atmosphere
    idxlhs = fcol_in_mdf["CH4_conversion_to_CO2_and_H2O"]
    idx1 = fcol_in_mdf["C_in_atmosphere_in_form_of_CH4"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / CH4_halflife_in_atmosphere

    # CH4_emissions[region] = ( CH4_emi_from_agriculture[region] + CH4_emi_from_energy[region] + CH4_emi_from_waste[region] ) * UNIT_conversion_from_MtCH4_to_GtC
    idxlhs = fcol_in_mdf["CH4_emissions"]
    idx1 = fcol_in_mdf["CH4_emi_from_agriculture"]
    idx2 = fcol_in_mdf["CH4_emi_from_energy"]
    idx3 = fcol_in_mdf["CH4_emi_from_waste"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      ) * UNIT_conversion_from_MtCH4_to_GtC

    # CH4_Emissions_CO2e[region] = CH4_emissions[region] * Global_Warming_Potential_CH4
    idxlhs = fcol_in_mdf["CH4_Emissions_CO2e"]
    idx1 = fcol_in_mdf["CH4_emissions"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Global_Warming_Potential_CH4

    # CH4_in_the_atmosphere_converted_to_CO2 = CH4_conversion_to_CO2_and_H2O
    idxlhs = fcol_in_mdf["CH4_in_the_atmosphere_converted_to_CO2"]
    idx1 = fcol_in_mdf["CH4_conversion_to_CO2_and_H2O"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # RoC_in_delivery_delay_index[region] = SoE_of_Inventory_on_RoC_of_ddx * ( Perceived_relative_inventory[region] / Sufficient_relative_inventory - 1 )
    idxlhs = fcol_in_mdf["RoC_in_delivery_delay_index"]
    idx1 = fcol_in_mdf["Perceived_relative_inventory"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = SoE_of_Inventory_on_RoC_of_ddx * (
        mdf[rowi, idx1 + j] / Sufficient_relative_inventory - 1
      )

    # Change_in_delivery_delay_index[region] = Delivery_delay_index[region] * RoC_in_delivery_delay_index[region]
    idxlhs = fcol_in_mdf["Change_in_delivery_delay_index"]
    idx1 = fcol_in_mdf["Delivery_delay_index"]
    idx2 = fcol_in_mdf["RoC_in_delivery_delay_index"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Eff_of_labour_imbalance_on_FOLP[region] = So_Eff_of_labour_imbalance_on_FOLP[region] * ( Theoretical_full_time_jobs_at_current_CLR[region] / Employed[region] - 1 )
    idxlhs = fcol_in_mdf["Eff_of_labour_imbalance_on_FOLP"]
    idx1 = fcol_in_mdf["Theoretical_full_time_jobs_at_current_CLR"]
    idx2 = fcol_in_mdf["Employed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = So_Eff_of_labour_imbalance_on_FOLP[j] * (
        mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] - 1
      )

    # RoC_in_FOPOLM[region] = Eff_of_labour_imbalance_on_FOLP[region]
    idxlhs = fcol_in_mdf["RoC_in_FOPOLM"]
    idx1 = fcol_in_mdf["Eff_of_labour_imbalance_on_FOLP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Change_in_Fraction_of_people_outside_of_labour_market[region] = ( Max_FOPOLM - Fraction_of_people_outside_of_labour_market_FOPOLM[region] ) * RoC_in_FOPOLM[region]
    idxlhs = fcol_in_mdf["Change_in_Fraction_of_people_outside_of_labour_market"]
    idx1 = fcol_in_mdf["Fraction_of_people_outside_of_labour_market_FOPOLM"]
    idx2 = fcol_in_mdf["RoC_in_FOPOLM"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Max_FOPOLM - mdf[rowi, idx1 + j]) * mdf[rowi, idx2 + j]

    # Change_in_future_footprint_pp = IF_THEN_ELSE ( zeit >= 2020 , Non_energy_footprint_pp_future / Half_life_of_tech_progress_in_non_energy_footprint , 0 )
    idxlhs = fcol_in_mdf["Change_in_future_footprint_pp"]
    idx1 = fcol_in_mdf["Non_energy_footprint_pp_future"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit >= 2020,   mdf[rowi, idx1] / Half_life_of_tech_progress_in_non_energy_footprint,   0, )

    # GenEq_cn = GenEq_cn_a * ( GDPpp_USED[cn] / UNIT_conv_to_make_base_dmnless ) ^ GenEq_cn_b
    idxlhs = fcol_in_mdf["GenEq_cn"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      GenEq_cn_a * (mdf[rowi, idx1 + 2] / UNIT_conv_to_make_base_dmnless) ** GenEq_cn_b
    )

    # GenEq_ec = GenEq_ec_a * LN ( GDPpp_USED[ec] / UNIT_conv_to_make_base_dmnless ) + GenEq_ec_b
    idxlhs = fcol_in_mdf["GenEq_ec"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      GenEq_ec_a * math.log(mdf[rowi, idx1 + 7] / UNIT_conv_to_make_base_dmnless)
      + GenEq_ec_b
    )

    # GenEq_me = GenEq_me_a * ( GDPpp_USED[me] / UNIT_conv_to_make_base_dmnless ) + GenEq_me_b
    idxlhs = fcol_in_mdf["GenEq_me"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      GenEq_me_a * (mdf[rowi, idx1 + 3] / UNIT_conv_to_make_base_dmnless) + GenEq_me_b
    )

    # GenEq_sa = GenEq_sa_la_af_a * LN ( GDPpp_USED[sa] / UNIT_conv_to_make_base_dmnless ) + GenEq_sa_la_af_b
    idxlhs = fcol_in_mdf["GenEq_sa"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      GenEq_sa_la_af_a * math.log(mdf[rowi, idx1 + 4] / UNIT_conv_to_make_base_dmnless)
      + GenEq_sa_la_af_b
    )

    # GenEq_la = GenEq_sa_la_af_a * LN ( GDPpp_USED[la] / UNIT_conv_to_make_base_dmnless ) + GenEq_sa_la_af_b
    idxlhs = fcol_in_mdf["GenEq_la"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      GenEq_sa_la_af_a * math.log(mdf[rowi, idx1 + 5] / UNIT_conv_to_make_base_dmnless)
      + GenEq_sa_la_af_b
    )

    # GenEq_af = GenEq_sa_la_af_a * LN ( GDPpp_USED[af] / UNIT_conv_to_make_base_dmnless ) + GenEq_sa_la_af_b
    idxlhs = fcol_in_mdf["GenEq_af"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    mdf[rowi, idxlhs] = (
      GenEq_sa_la_af_a * math.log(mdf[rowi, idx1 + 1] / UNIT_conv_to_make_base_dmnless)
      + GenEq_sa_la_af_b
    )

    # GenEq_se_eu_pa_us[region] = GenEq_se_eu_pa_us_a * ( GDPpp_USED[region] / UNIT_conv_to_make_base_dmnless ) + GenEq_se_eu_pa_us_b
    idxlhs = fcol_in_mdf["GenEq_se_eu_pa_us"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (GenEq_se_eu_pa_us_a * (mdf[rowi, idx1 + j] / UNIT_conv_to_make_base_dmnless)
        + GenEq_se_eu_pa_us_b
      )

    # GenEq_before_female_leadership_spending[region] = IF_THEN_ELSE ( j==2 , GenEq_cn , IF_THEN_ELSE ( j==7 , GenEq_ec , IF_THEN_ELSE ( j==3 , GenEq_me , IF_THEN_ELSE ( j==4 , GenEq_sa , IF_THEN_ELSE ( j==5 , GenEq_la , IF_THEN_ELSE ( j==1 , GenEq_af , GenEq_se_eu_pa_us ) ) ) ) ) )
    idxlhs = fcol_in_mdf["GenEq_before_female_leadership_spending"]
    idx1 = fcol_in_mdf["GenEq_cn"]
    idx2 = fcol_in_mdf["GenEq_ec"]
    idx3 = fcol_in_mdf["GenEq_me"]
    idx4 = fcol_in_mdf["GenEq_sa"]
    idx5 = fcol_in_mdf["GenEq_la"]
    idx6 = fcol_in_mdf["GenEq_af"]
    idx7 = fcol_in_mdf["GenEq_se_eu_pa_us"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        j == 2,     mdf[rowi, idx1],     IF_THEN_ELSE(
          j == 7,       mdf[rowi, idx2],       IF_THEN_ELSE(
            j == 3,         mdf[rowi, idx3],         IF_THEN_ELSE(
              j == 4,           mdf[rowi, idx4],           IF_THEN_ELSE(
                j == 5,             mdf[rowi, idx5],             IF_THEN_ELSE(j == 1, mdf[rowi, idx6], mdf[rowi, idx7 + j]),           ),         ),       ),     ),   )

    # Effect_of_Female_Leadership_on_gender_equality[region] = 1 + Female_leadership_spending[region] / GDP_USED[region]
    idxlhs = fcol_in_mdf["Effect_of_Female_Leadership_on_gender_equality"]
    idx1 = fcol_in_mdf["Female_leadership_spending"]
    idx2 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # GenEq[region] = GenEq_before_female_leadership_spending[region] * Effect_of_Female_Leadership_on_gender_equality[region]
    idxlhs = fcol_in_mdf["GenEq"]
    idx1 = fcol_in_mdf["GenEq_before_female_leadership_spending"]
    idx2 = fcol_in_mdf["Effect_of_Female_Leadership_on_gender_equality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Cutoff_GE_change[region] = WITH LOOKUP ( GenderEquality[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.1 , 0.98 ) , ( 0.2 , 0.9 ) , ( 0.3 , 0.72 ) , ( 0.4 , 0.43 ) , ( 0.55 , 0.0001 ) ) )
    tabidx = ftab_in_d_table["Cutoff_GE_change"]  # fetch the correct table
    idx2 = fcol_in_mdf["Cutoff_GE_change"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["GenderEquality"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Change_in_GE[region] = ( GenEq[region] - GenderEquality[region] ) / Time_to_change_GE[region] * Cutoff_GE_change[region]
    idxlhs = fcol_in_mdf["Change_in_GE"]
    idx1 = fcol_in_mdf["GenEq"]
    idx2 = fcol_in_mdf["GenderEquality"]
    idx3 = fcol_in_mdf["Cutoff_GE_change"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])
        / Time_to_change_GE
        * mdf[rowi, idx3 + j]
      )

    # Change_in_Owner_power[region] = Strength_of_owner_reaction_to_worker_resistance * Worker_resistance_or_resignation[region]
    idxlhs = fcol_in_mdf["Change_in_Owner_power"]
    idx1 = fcol_in_mdf["Worker_resistance_or_resignation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Strength_of_owner_reaction_to_worker_resistance * mdf[rowi, idx1 + j]
      )

    # RoC_of_people_considering_entering_the_labor_pool[region] = Slope_of_RoC_of_people_considering_entering_the_labor_pool * ( Unemployment_ratio[region] - 1 )
    idxlhs = fcol_in_mdf["RoC_of_people_considering_entering_the_labor_pool"]
    idx1 = fcol_in_mdf["Unemployment_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Slope_of_RoC_of_people_considering_entering_the_labor_pool
        * (mdf[rowi, idx1 + j] - 1)
      )

    # Change_in_people_considering_entering_the_pool[region] = People_considering_entering_the_pool[region] * RoC_of_people_considering_entering_the_labor_pool[region]
    idxlhs = fcol_in_mdf["Change_in_people_considering_entering_the_pool"]
    idx1 = fcol_in_mdf["People_considering_entering_the_pool"]
    idx2 = fcol_in_mdf["RoC_of_people_considering_entering_the_labor_pool"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # RoC_of_people_considering_leaving_the_labor_pool[region] = Slope_of_RoC_of_people_considering_leaving_the_labor_pool * ( Unemployment_ratio[region] - Scaling_strength_of_RoC_from_unemployed_to_pool[region] )
    idxlhs = fcol_in_mdf["RoC_of_people_considering_leaving_the_labor_pool"]
    idx1 = fcol_in_mdf["Unemployment_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Slope_of_RoC_of_people_considering_leaving_the_labor_pool
        * (mdf[rowi, idx1 + j] - Scaling_strength_of_RoC_from_unemployed_to_pool[j])
      )

    # Change_in_people_considering_leaving_the_pool[region] = People_considering_leaving_the_pool[region] * RoC_of_people_considering_leaving_the_labor_pool[region]
    idxlhs = fcol_in_mdf["Change_in_people_considering_leaving_the_pool"]
    idx1 = fcol_in_mdf["People_considering_leaving_the_pool"]
    idx2 = fcol_in_mdf["RoC_of_people_considering_leaving_the_labor_pool"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Public_capacity_N_yrs_ago[region] = SMOOTH3 ( Public_capacity[region] , the_N_for_PC_N_yrs_ago )
    idxin = fcol_in_mdf["Public_capacity"]
    idx2 = fcol_in_mdf["Public_capacity_N_yrs_ago_2"]
    idx1 = fcol_in_mdf["Public_capacity_N_yrs_ago_1"]
    idxout = fcol_in_mdf["Public_capacity_N_yrs_ago"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (the_N_for_PC_N_yrs_ago / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (the_N_for_PC_N_yrs_ago / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (the_N_for_PC_N_yrs_ago / 3)
        * dt
      )

    # RoC_in_in_RoTA_from_public_capacity[region] = ( SoE_of_PC_on_RoC_in_change_in_rate_of_tech_advance[region] / 1000 ) * ( 1 + Public_capacity[region] / Public_capacity_N_yrs_ago[region] - 1 )
    idxlhs = fcol_in_mdf["RoC_in_in_RoTA_from_public_capacity"]
    idx1 = fcol_in_mdf["Public_capacity"]
    idx2 = fcol_in_mdf["Public_capacity_N_yrs_ago"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (SoE_of_PC_on_RoC_in_change_in_rate_of_tech_advance[j] / 1000
      ) * (1 + mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] - 1)

    # RoC_in_RoTA_in_TFP_from_industrialization[region] = SoE_of_industrialization_on_RoC_in_TFP * ( 1 + Size_of_industrial_sector[region] - 1 )
    idxlhs = fcol_in_mdf["RoC_in_RoTA_in_TFP_from_industrialization"]
    idx1 = fcol_in_mdf["Size_of_industrial_sector"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = SoE_of_industrialization_on_RoC_in_TFP * (
        1 + mdf[rowi, idx1 + j] - 1
      )

    # RoC_in_RoTA_in_TFP_from_tertiary_sector[region] = SoE_of_tertiary_sector_on_RoC_in_TFP[region] * ( 1 + Size_of_tertiary_sector[region] - 1 )
    idxlhs = fcol_in_mdf["RoC_in_RoTA_in_TFP_from_tertiary_sector"]
    idx1 = fcol_in_mdf["Size_of_tertiary_sector"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = SoE_of_tertiary_sector_on_RoC_in_TFP[j] * (
        1 + mdf[rowi, idx1 + j] - 1
      )

    # Change_in_RoTA[region] = Rate_of_tech_advance_RoTA_in_TFP[region] * ( RoC_in_in_RoTA_from_public_capacity[region] + RoC_in_RoTA_in_TFP_from_industrialization[region] + RoC_in_RoTA_in_TFP_from_tertiary_sector[region] )
    idxlhs = fcol_in_mdf["Change_in_RoTA"]
    idx1 = fcol_in_mdf["Rate_of_tech_advance_RoTA_in_TFP"]
    idx2 = fcol_in_mdf["RoC_in_in_RoTA_from_public_capacity"]
    idx3 = fcol_in_mdf["RoC_in_RoTA_in_TFP_from_industrialization"]
    idx4 = fcol_in_mdf["RoC_in_RoTA_in_TFP_from_tertiary_sector"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (
        mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j] + mdf[rowi, idx4 + j]
      )

    # Perceived_inflation[region] = SMOOTHI ( Inflation_rate_used_only_for_interest_rate[region] , Inflation_perception_time[region] , Perceived_inflation_in_1980[region] )
    idx1 = fcol_in_mdf["Perceived_inflation"]
    idx2 = fcol_in_mdf["Inflation_rate_used_only_for_interest_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Inflation_perception_time[j]
        * dt
      )

    # Eff_of_inflation_on_Indicated_signal_rate[region] = 1 + SoE_of_inflation_rate_on_indicated_signal_rate * ( Perceived_inflation[region] / Inflation_target[region] - 1 )
    idxlhs = fcol_in_mdf["Eff_of_inflation_on_Indicated_signal_rate"]
    idx1 = fcol_in_mdf["Perceived_inflation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + SoE_of_inflation_rate_on_indicated_signal_rate * (
        mdf[rowi, idx1 + j] / Inflation_target[j] - 1
      )

    # Perceived_unemployment_rate[region] = SMOOTH ( Unemployment_rate[region] , Unemployment_perception_time )
    idx1 = fcol_in_mdf["Perceived_unemployment_rate"]
    idx2 = fcol_in_mdf["Unemployment_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Unemployment_perception_time
        * dt
      )

    # Long_term_unemployment_rate[region] = SMOOTH ( Unemployment_rate[region] , Time_to_establish_Long_term_unemployment_rate )
    idx1 = fcol_in_mdf["Long_term_unemployment_rate"]
    idx2 = fcol_in_mdf["Unemployment_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_establish_Long_term_unemployment_rate
        * dt
      )

    # Unemployment_rate_used[region] = IF_THEN_ELSE ( SWITCH_unemp_target_or_long_term == 1 , Unemployment_target_for_interest , Long_term_unemployment_rate )
    idxlhs = fcol_in_mdf["Unemployment_rate_used"]
    idx1 = fcol_in_mdf["Long_term_unemployment_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        SWITCH_unemp_target_or_long_term[j] == 1,     Unemployment_target_for_interest[j],     mdf[rowi, idx1 + j],   )

    # Eff_of_unemployment_on_Indicated_signal_rate[region] = SoE_of_unemployment_rate_on_indicated_signal_rate * ( Perceived_unemployment_rate[region] / Unemployment_rate_used[region] - 1 )
    idxlhs = fcol_in_mdf["Eff_of_unemployment_on_Indicated_signal_rate"]
    idx1 = fcol_in_mdf["Perceived_unemployment_rate"]
    idx2 = fcol_in_mdf["Unemployment_rate_used"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = SoE_of_unemployment_rate_on_indicated_signal_rate * (
        mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] - 1
      )

    # Indicated_signal_rate[region] = Normal_signal_rate[region] * ( Eff_of_inflation_on_Indicated_signal_rate[region] + Eff_of_unemployment_on_Indicated_signal_rate[region] )
    idxlhs = fcol_in_mdf["Indicated_signal_rate"]
    idx1 = fcol_in_mdf["Eff_of_inflation_on_Indicated_signal_rate"]
    idx2 = fcol_in_mdf["Eff_of_unemployment_on_Indicated_signal_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Normal_signal_rate[j] * (
        mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]
      )

    # Change_in_signal_rate[region] = ( Indicated_signal_rate[region] - Central_bank_signal_rate[region] ) / Signal_rate_adjustment_time
    idxlhs = fcol_in_mdf["Change_in_signal_rate"]
    idx1 = fcol_in_mdf["Indicated_signal_rate"]
    idx2 = fcol_in_mdf["Central_bank_signal_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]
      ) / Signal_rate_adjustment_time

    # Ratio_of_actual_public_spending_vs_reference[region] = Public_spending_as_share_of_GDP[region] / Reference_public_spending_fraction
    idxlhs = fcol_in_mdf["Ratio_of_actual_public_spending_vs_reference"]
    idx1 = fcol_in_mdf["Public_spending_as_share_of_GDP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Reference_public_spending_fraction

    # Public_spending_effect_on_social_trust[region] = WITH LOOKUP ( Ratio_of_actual_public_spending_vs_reference[region] , ( [ ( 0 , 0 ) - ( 0.601626 , 0.822581 ) ] , ( 0 , 0.8 ) , ( 0.25 , 0.82 ) , ( 0.5 , 0.87 ) , ( 0.75 , 0.93 ) , ( 1 , 1 ) , ( 1.25 , 1.07 ) , ( 1.5 , 1.13 ) , ( 1.75 , 1.18 ) , ( 2 , 1.2 ) ) )
    tabidx = ftab_in_d_table[  "Public_spending_effect_on_social_trust"]  # fetch the correct table
    idx2 = fcol_in_mdf["Public_spending_effect_on_social_trust"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Ratio_of_actual_public_spending_vs_reference"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Ratio_of_actual_inequality_to_norm[region] = Actual_inequality_index_higher_is_more_unequal_N_years_ago[region] / Inequality_considered_normal_in_1980[region]
    idxlhs = fcol_in_mdf["Ratio_of_actual_inequality_to_norm"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal_N_years_ago"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Inequality_considered_normal_in_1980

    # Inequality_effect_on_social_trust[region] = WITH LOOKUP ( Ratio_of_actual_inequality_to_norm[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 2 ) , ( 0.2 , 1.975 ) , ( 0.4 , 1.913 ) , ( 0.6 , 1.767 ) , ( 0.8 , 1.465 ) , ( 1 , 1 ) , ( 1.2 , 0.5352 ) , ( 1.4 , 0.2331 ) , ( 1.6 , 0.08682 ) , ( 1.8 , 0.02526 ) , ( 2 , 0 ) ) )
    tabidx = ftab_in_d_table[  "Inequality_effect_on_social_trust"]  # fetch the correct table
    idx2 = fcol_in_mdf["Inequality_effect_on_social_trust"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Ratio_of_actual_inequality_to_norm"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Multplier_from_gender_inequality_on_indicated_social_trust[region] = 1 + ( SDG_5_Score[region] - 0.5 ) * Strength_of_Effect_of_gender_inequality_on_social_trust
    idxlhs = fcol_in_mdf["Multplier_from_gender_inequality_on_indicated_social_trust"]
    idx1 = fcol_in_mdf["SDG_5_Score"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + (mdf[rowi, idx1 + j] - 0.5)
        * Strength_of_Effect_of_gender_inequality_on_social_trust
      )

    # Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust[region] = SMOOTH3 ( Multplier_from_gender_inequality_on_indicated_social_trust[region] , Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust )
    idxin = fcol_in_mdf["Multplier_from_gender_inequality_on_indicated_social_trust"]
    idx2 = fcol_in_mdf["Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust_2"
    ]
    idx1 = fcol_in_mdf["Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust_1"
    ]
    idxout = fcol_in_mdf["Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust"
    ]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3)
        * dt
      )

    # Multplier_from_schooling_on_indicated_social_trust[region] = 1 + ( SDG4_Score[region] - 0.5 ) * Strength_of_Effect_of_schooling_on_social_trust
    idxlhs = fcol_in_mdf["Multplier_from_schooling_on_indicated_social_trust"]
    idx1 = fcol_in_mdf["SDG4_Score"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1
        + (mdf[rowi, idx1 + j] - 0.5) * Strength_of_Effect_of_schooling_on_social_trust
      )

    # Smoothed_Multplier_from_schooling_on_indicated_social_trust[region] = SMOOTH3 ( Multplier_from_schooling_on_indicated_social_trust[region] , Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust )
    idxin = fcol_in_mdf["Multplier_from_schooling_on_indicated_social_trust"]
    idx2 = fcol_in_mdf["Smoothed_Multplier_from_schooling_on_indicated_social_trust_2"]
    idx1 = fcol_in_mdf["Smoothed_Multplier_from_schooling_on_indicated_social_trust_1"]
    idxout = fcol_in_mdf["Smoothed_Multplier_from_schooling_on_indicated_social_trust"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_smooth_Multplier_from_empowerment_on_indicated_social_trust / 3)
        * dt
      )

    # Indicated_social_trust[region] = Public_spending_effect_on_social_trust[region] * Inequality_effect_on_social_trust[region] / Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust[region] * Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust[region] * Smoothed_Multplier_from_schooling_on_indicated_social_trust[region]
    idxlhs = fcol_in_mdf["Indicated_social_trust"]
    idx1 = fcol_in_mdf["Public_spending_effect_on_social_trust"]
    idx2 = fcol_in_mdf["Inequality_effect_on_social_trust"]
    idx3 = fcol_in_mdf["Scaled_and_smoothed_Effect_of_poverty_on_social_tension_and_trust"
    ]
    idx4 = fcol_in_mdf["Smoothed_Multplier_from_gender_inequality_on_indicated_social_trust"
    ]
    idx5 = fcol_in_mdf["Smoothed_Multplier_from_schooling_on_indicated_social_trust"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        / mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # Change_in_social_trust[region] = ( Indicated_social_trust[region] - Social_trust[region] ) / Time_to_change_social_trust
    idxlhs = fcol_in_mdf["Change_in_social_trust"]
    idx1 = fcol_in_mdf["Indicated_social_trust"]
    idx2 = fcol_in_mdf["Social_trust"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]
      ) / Time_to_change_social_trust

    # Change_in_TFP[region] = Total_factor_productivity_TFP_before_env_damage[region] * Rate_of_tech_advance_RoTA_in_TFP[region]
    idxlhs = fcol_in_mdf["Change_in_TFP"]
    idx1 = fcol_in_mdf["Total_factor_productivity_TFP_before_env_damage"]
    idx2 = fcol_in_mdf["Rate_of_tech_advance_RoTA_in_TFP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Future_Annual_reduction_in_UAC = IF_THEN_ELSE ( zeit >= 2020 , Annual_reduction_in_UAC / 100 , 0 )
    idxlhs = fcol_in_mdf["Future_Annual_reduction_in_UAC"]
    idx1 = fcol_in_mdf["Annual_reduction_in_UAC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit >= 2020, mdf[rowi, idx1] / 100, 0)

    # Change_in_UACre = Future_Annual_reduction_in_UAC * UAC_reduction_effort
    idxlhs = fcol_in_mdf["Change_in_UACre"]
    idx1 = fcol_in_mdf["Future_Annual_reduction_in_UAC"]
    idx2 = fcol_in_mdf["UAC_reduction_effort"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power[region] = 1 + WReaction_policy[region]
    idxlhs = fcol_in_mdf["Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power"
    ]
    idx1 = fcol_in_mdf["WReaction_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + mdf[rowi, idx1 + j]

    # Inequality_effect_on_food_TA[region] = 1 + ( Actual_inequality_index_higher_is_more_unequal[region] - 1 ) * Strength_of_inequality_effect_on_food_TA
    idxlhs = fcol_in_mdf["Inequality_effect_on_food_TA"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 + (mdf[rowi, idx1 + j] - 1) * Strength_of_inequality_effect_on_food_TA
      )

    # Reform_willingness_with_inequality[region] = ( Smoothed_Reform_willingness[region] / Inequality_effect_on_food_TA[region] )
    idxlhs = fcol_in_mdf["Reform_willingness_with_inequality"]
    idx1 = fcol_in_mdf["Smoothed_Reform_willingness"]
    idx2 = fcol_in_mdf["Inequality_effect_on_food_TA"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Effect_of_TAs_on_inequality[region] = Reform_willingness_with_inequality[region] / Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["Effect_of_TAs_on_inequality"]
    idx1 = fcol_in_mdf["Reform_willingness_with_inequality"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Scaled_Effect_of_TAs_on_inequality[region] = ( Effect_of_TAs_on_inequality[region] - 1 ) * Strength_of_Effect_of_TAs_on_inequality
    idxlhs = fcol_in_mdf["Scaled_Effect_of_TAs_on_inequality"]
    idx1 = fcol_in_mdf["Effect_of_TAs_on_inequality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - 1
      ) * Strength_of_Effect_of_TAs_on_inequality

    # Strength_of_worker_reaction_to_owner_power[region] = Strength_of_worker_reaction_to_owner_power_normal * Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power[region] + Scaled_Effect_of_TAs_on_inequality[region]
    idxlhs = fcol_in_mdf["Strength_of_worker_reaction_to_owner_power"]
    idx1 = fcol_in_mdf["Eff_of_scenario_on_strength_of_worker_reaction_to_owner_power"]
    idx2 = fcol_in_mdf["Scaled_Effect_of_TAs_on_inequality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Strength_of_worker_reaction_to_owner_power_normal * mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
      )

    # Change_in_worker_resistance[region] = Owner_power_or_weakness[region] * Strength_of_worker_reaction_to_owner_power[region]
    idxlhs = fcol_in_mdf["Change_in_worker_resistance"]
    idx1 = fcol_in_mdf["Owner_power_or_weakness"]
    idx2 = fcol_in_mdf["Strength_of_worker_reaction_to_owner_power"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Global_CO2_from_fossil_fuels_to_atm = SUM ( CO2_from_fossil_fuels_to_atm[region!] )
    idxlhs = fcol_in_mdf["Global_CO2_from_fossil_fuels_to_atm"]
    idx1 = fcol_in_mdf["CO2_from_fossil_fuels_to_atm"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Fraction_of_CO2_emi_from_fossils_attributable_to_a_region[region] = CO2_from_fossil_fuels_to_atm[region] / Global_CO2_from_fossil_fuels_to_atm
    idxlhs = fcol_in_mdf["Fraction_of_CO2_emi_from_fossils_attributable_to_a_region"]
    idx1 = fcol_in_mdf["CO2_from_fossil_fuels_to_atm"]
    idx2 = fcol_in_mdf["Global_CO2_from_fossil_fuels_to_atm"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2]

    # Fraction_of_CO2_emi_from_fossils_attributable_to_a_region_smoothed[region] = SMOOTH ( Fraction_of_CO2_emi_from_fossils_attributable_to_a_region[region] , Time_to_verify_emi )
    idx1 = fcol_in_mdf["Fraction_of_CO2_emi_from_fossils_attributable_to_a_region_smoothed"
    ]
    idx2 = fcol_in_mdf["Fraction_of_CO2_emi_from_fossils_attributable_to_a_region"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / Time_to_verify_emi * dt
      )

    # Cohort_50plus[region] = Cohort_50_to_54[region] + Cohort_55_to_59[region] + Cohort_60plus[region]
    idxlhs = fcol_in_mdf["Cohort_50plus"]
    idx1 = fcol_in_mdf["Cohort_50_to_54"]
    idx2 = fcol_in_mdf["Cohort_55_to_59"]
    idx3 = fcol_in_mdf["Cohort_60plus"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # Cold_dense_water_sinking_in_Sverdrup = Cold_dense_water_sinking_in_Sverdrup_in_1850 * NatEvent_d_slowing_down_ocean_circulation_from_2015 * Ocean_circulation_slowdown_from_Greenland_ice_sliding_into_the_Atlantic
    idxlhs = fcol_in_mdf["Cold_dense_water_sinking_in_Sverdrup"]
    idx1 = fcol_in_mdf["NatEvent_d_slowing_down_ocean_circulation_from_2015"]
    idx2 = fcol_in_mdf["Ocean_circulation_slowdown_from_Greenland_ice_sliding_into_the_Atlantic"
    ]
    mdf[rowi, idxlhs] = (
      Cold_dense_water_sinking_in_Sverdrup_in_1850 * mdf[rowi, idx1] * mdf[rowi, idx2]
    )

    # Global_All_SDG_Scores = All_SDG_Scores[us] * Regional_population_as_fraction_of_total[us] + All_SDG_Scores[af] * Regional_population_as_fraction_of_total[af] + All_SDG_Scores[cn] * Regional_population_as_fraction_of_total[cn] + All_SDG_Scores[me] * Regional_population_as_fraction_of_total[me] + All_SDG_Scores[sa] * Regional_population_as_fraction_of_total[sa] + All_SDG_Scores[la] * Regional_population_as_fraction_of_total[la] + All_SDG_Scores[pa] * Regional_population_as_fraction_of_total[pa] + All_SDG_Scores[ec] * Regional_population_as_fraction_of_total[ec] + All_SDG_Scores[eu] * Regional_population_as_fraction_of_total[eu] + All_SDG_Scores[se] * Regional_population_as_fraction_of_total[se]
    idxlhs = fcol_in_mdf["Global_All_SDG_Scores"]
    idx1 = fcol_in_mdf["All_SDG_Scores"]
    idx2 = fcol_in_mdf["Regional_population_as_fraction_of_total"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1 + 0] * mdf[rowi, idx2 + 0]
      + mdf[rowi, idx1 + 1] * mdf[rowi, idx2 + 1]
      + mdf[rowi, idx1 + 2] * mdf[rowi, idx2 + 2]
      + mdf[rowi, idx1 + 3] * mdf[rowi, idx2 + 3]
      + mdf[rowi, idx1 + 4] * mdf[rowi, idx2 + 4]
      + mdf[rowi, idx1 + 5] * mdf[rowi, idx2 + 5]
      + mdf[rowi, idx1 + 6] * mdf[rowi, idx2 + 6]
      + mdf[rowi, idx1 + 7] * mdf[rowi, idx2 + 7]
      + mdf[rowi, idx1 + 8] * mdf[rowi, idx2 + 8]
      + mdf[rowi, idx1 + 9] * mdf[rowi, idx2 + 9]
    )

    # Smoothed_SDG_score_for_effect_of_wellbeing = SMOOTH3 ( Global_All_SDG_Scores , Time_to_smooth_the_anchor_SDG_scores_for_wellbeing )
    idx1 = fcol_in_mdf["Global_All_SDG_Scores"]
    idxin = fcol_in_mdf["Global_All_SDG_Scores"]
    idx2 = fcol_in_mdf["Smoothed_SDG_score_for_effect_of_wellbeing_2"]
    idx1 = fcol_in_mdf["Smoothed_SDG_score_for_effect_of_wellbeing_1"]
    idxout = fcol_in_mdf["Smoothed_SDG_score_for_effect_of_wellbeing"]
    mdf[rowi, idx1] = (
      mdf[rowi - 1, idx1]
      + (mdf[rowi - 1, idxin] - mdf[rowi - 1, idx1])
      / (Time_to_smooth_the_anchor_SDG_scores_for_wellbeing / 3)
      * dt
    )
    mdf[rowi, idx2] = (
      mdf[rowi - 1, idx2]
      + (mdf[rowi - 1, idx1] - mdf[rowi - 1, idx2])
      / (Time_to_smooth_the_anchor_SDG_scores_for_wellbeing / 3)
      * dt
    )
    mdf[rowi, idxout] = (
      mdf[rowi - 1, idxout]
      + (mdf[rowi - 1, idx2] - mdf[rowi - 1, idxout])
      / (Time_to_smooth_the_anchor_SDG_scores_for_wellbeing / 3)
      * dt
    )

    # Comparison_Effect_of_SDG_score_on_wellbeing[region] = IF_THEN_ELSE ( zeit < 2023 , 1 , 1 + ( All_SDG_Scores / Smoothed_SDG_score_for_effect_of_wellbeing - 1 ) * Strength_of_Effect_of_SDG_scores_on_wellbeing )
    idxlhs = fcol_in_mdf["Comparison_Effect_of_SDG_score_on_wellbeing"]
    idx1 = fcol_in_mdf["All_SDG_Scores"]
    idx2 = fcol_in_mdf["Smoothed_SDG_score_for_effect_of_wellbeing"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit < 2023,     1,     1
        + (mdf[rowi, idx1 + j] / mdf[rowi, idx2] - 1)
        * Strength_of_Effect_of_SDG_scores_on_wellbeing,   )

    # Investment_demand[region] = Initiating_capacity_construction[region]
    idxlhs = fcol_in_mdf["Investment_demand"]
    idx1 = fcol_in_mdf["Initiating_capacity_construction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Total_consumption[region] = Worker_consumption_demand[region] + Govt_consumption_ie_purchases[region] + Owner_consumption[region] - Consumption_taxes[region]
    idxlhs = fcol_in_mdf["Total_consumption"]
    idx1 = fcol_in_mdf["Worker_consumption_demand"]
    idx2 = fcol_in_mdf["Govt_consumption_ie_purchases"]
    idx3 = fcol_in_mdf["Owner_consumption"]
    idx4 = fcol_in_mdf["Consumption_taxes"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        - mdf[rowi, idx4 + j]
      )

    # Consumption_and_investment[region] = Investment_demand[region] + Total_consumption[region]
    idxlhs = fcol_in_mdf["Consumption_and_investment"]
    idx1 = fcol_in_mdf["Investment_demand"]
    idx2 = fcol_in_mdf["Total_consumption"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Convection_as_f_of_temp_ZJ_py = ( Incoming_solar_in_1850_ZJ_py * Convection_as_f_of_incoming_solar_in_1850 ) * ( 1 + Sensitivity_of_convection_to_temp * ( Temp_surface_current_divided_by_value_in_1850_K_p_K - 1 ) )
    idxlhs = fcol_in_mdf["Convection_as_f_of_temp_ZJ_py"]
    idx1 = fcol_in_mdf["Temp_surface_current_divided_by_value_in_1850_K_p_K"]
    mdf[rowi, idxlhs] = (
      Incoming_solar_in_1850_ZJ_py * Convection_as_f_of_incoming_solar_in_1850
    ) * (1 + Sensitivity_of_convection_to_temp * (mdf[rowi, idx1] - 1))

    # Convection_aka_sensible_heat_flow = Convection_as_f_of_temp_ZJ_py
    idxlhs = fcol_in_mdf["Convection_aka_sensible_heat_flow"]
    idx1 = fcol_in_mdf["Convection_as_f_of_temp_ZJ_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Cost_per_regional_energy_policy[region] = Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_energy_policies
    idxlhs = fcol_in_mdf["Cost_per_regional_energy_policy"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_energy_PES_with_env_dam_and_reform"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Nbr_of_relevant_energy_policies

    # Cost_per_regional_inequality_policy[region] = Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_inequality_policies
    idxlhs = fcol_in_mdf["Cost_per_regional_inequality_policy"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_inequality_PES_with_env_dam_and_reform"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Nbr_of_relevant_inequality_policies

    # Cost_per_regional_poverty_policy[region] = Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_poverty_policies
    idxlhs = fcol_in_mdf["Cost_per_regional_poverty_policy"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_poverty_PES_with_env_dam_and_reform"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Nbr_of_relevant_poverty_policies

    # Cost_per_regional_food_policy[region] = Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_food_policies
    idxlhs = fcol_in_mdf["Cost_per_regional_food_policy"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_food_PES_with_env_dam_and_reform"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Nbr_of_relevant_food_policies

    # Cost_per_regional_empowerment_policy[region] = Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform[region] / Nbr_of_relevant_empowerment_policies
    idxlhs = fcol_in_mdf["Cost_per_regional_empowerment_policy"]
    idx1 = fcol_in_mdf["Each_region_max_cost_estimate_empowerment_PES_with_env_dam_and_reform"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Nbr_of_relevant_empowerment_policies

    # Indicated_crop_yield_SE = IF_THEN_ELSE ( Nitrogen_use[9] >= 5 , ( Indicated_crop_yield_SE_L / ( 1 + math.exp ( - Indicated_crop_yield_SE_k * ( Nitrogen_use[9] * UNIT_conv_N_to_yield - Indicated_crop_yield_SE_x ) ) ) ) - ( Indicated_crop_yield_SE_L2 / ( 1 + math.exp ( - Indicated_crop_yield_SE_k2 * ( Nitrogen_use[9] * UNIT_conv_N_to_yield - Indicated_crop_yield_SE_x2 ) ) ) ) , Indicated_crop_yield_SE_min )
    idxlhs = fcol_in_mdf["Indicated_crop_yield_SE"]
    idx1 = fcol_in_mdf["Nitrogen_use"]
    idx2 = fcol_in_mdf["Nitrogen_use"]
    idx3 = fcol_in_mdf["Nitrogen_use"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1 + 9] >= 5,   (
        Indicated_crop_yield_SE_L
        / (
          1
          + math.exp(
            -Indicated_crop_yield_SE_k
            * (mdf[rowi, idx2 + 9] * UNIT_conv_N_to_yield - Indicated_crop_yield_SE_x)
          )
        )
      )
      - (
        Indicated_crop_yield_SE_L2
        / (
          1
          + math.exp(
            -Indicated_crop_yield_SE_k2
            * (mdf[rowi, idx3 + 9] * UNIT_conv_N_to_yield - Indicated_crop_yield_SE_x2)
          )
        )
      ),   Indicated_crop_yield_SE_min, )

    # Indicated_crop_yield_rest[region] = Indicated_crop_yield_rest_L[region] / ( 1 + math.exp ( - Indicated_crop_yield_rest_k[region] * ( Nitrogen_use[region] * UNIT_conv_N_to_yield - Indicated_crop_yield_rest_x0[region] ) ) )
    idxlhs = fcol_in_mdf["Indicated_crop_yield_rest"]
    idx1 = fcol_in_mdf["Nitrogen_use"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Indicated_crop_yield_rest_L[j] / (
        1
        + math.exp(
          -Indicated_crop_yield_rest_k[j]
          * (
            mdf[rowi, idx1 + j] * UNIT_conv_N_to_yield - Indicated_crop_yield_rest_x0[j]
          )
        )
      )

    # Crop_yield_from_N_use[region] = IF_THEN_ELSE ( j==9 , Indicated_crop_yield_SE , Indicated_crop_yield_rest )
    idxlhs = fcol_in_mdf["Crop_yield_from_N_use"]
    idx1 = fcol_in_mdf["Indicated_crop_yield_SE"]
    idx2 = fcol_in_mdf["Indicated_crop_yield_rest"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(j == 9, mdf[rowi, idx1], mdf[rowi, idx2 + j])

    # GDPpp_USED_for_influencing_death_rates[region] = SMOOTH3 ( GDPpp_USED[region] , Time_for_GDPpp_to_affect_death_rates )
    idxin = fcol_in_mdf["GDPpp_USED"]
    idx2 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates_2"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates_1"]
    idxout = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_for_GDPpp_to_affect_death_rates / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_for_GDPpp_to_affect_death_rates / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_for_GDPpp_to_affect_death_rates / 3)
        * dt
      )

    # death_rate_dr0[region] = dr0_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ^ dr0_b[region] )
    idxlhs = fcol_in_mdf["death_rate_dr0"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = dr0_a[j] * (
        (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr0_b[j]
      )

    # Indicated_Eff_of_env_damage_on_dying[region] = math.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_dying ) / Actual_eff_of_relative_wealth_on_env_damage[region]
    idxlhs = fcol_in_mdf["Indicated_Eff_of_env_damage_on_dying"]
    idx1 = fcol_in_mdf["Combined_env_damage_indicator"]
    idx2 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (math.exp(mdf[rowi, idx1] * expSoE_of_ed_on_dying) / mdf[rowi, idx2 + j]
      )

    # Eff_of_env_damage_on_dying[region] = SMOOTH ( Indicated_Eff_of_env_damage_on_dying[region] , Time_lag_for_env_damage_to_affect_mortality )
    idx1 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx2 = fcol_in_mdf["Indicated_Eff_of_env_damage_on_dying"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_lag_for_env_damage_to_affect_mortality
        * dt
      )

    # Ratio_of_regionally_available_crop_including_imports_to_regional_demand[region] = All_crop_regional_dmd[region] / ( Crop_grown_regionally[region] + Actual_crop_import[region] )
    idxlhs = fcol_in_mdf["Ratio_of_regionally_available_crop_including_imports_to_regional_demand"
    ]
    idx1 = fcol_in_mdf["All_crop_regional_dmd"]
    idx2 = fcol_in_mdf["Crop_grown_regionally"]
    idx3 = fcol_in_mdf["Actual_crop_import"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j]
      )

    # Ratio_of_demand_and_supply_of_crops_smoothed[region] = SMOOTH3 ( Ratio_of_regionally_available_crop_including_imports_to_regional_demand[region] , Time_to_smooth_regional_food_balance )
    idxin = fcol_in_mdf["Ratio_of_regionally_available_crop_including_imports_to_regional_demand"
    ]
    idx2 = fcol_in_mdf["Ratio_of_demand_and_supply_of_crops_smoothed_2"]
    idx1 = fcol_in_mdf["Ratio_of_demand_and_supply_of_crops_smoothed_1"]
    idxout = fcol_in_mdf["Ratio_of_demand_and_supply_of_crops_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_smooth_regional_food_balance / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_smooth_regional_food_balance / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_smooth_regional_food_balance / 3)
        * dt
      )

    # Malnutrition[region] =  1 + IF_THEN_ELSE ( zeit > Policy_start_year , ( Ratio_of_demand_and_supply_of_crops_smoothed - 1 ) * Strength_of_malnutrition_effect , 0 )
    idxlhs = fcol_in_mdf["Malnutrition"]
    idx1 = fcol_in_mdf["Ratio_of_demand_and_supply_of_crops_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + IF_THEN_ELSE(
        zeit > Policy_start_year,     (mdf[rowi, idx1 + j] - 1) * Strength_of_malnutrition_effect,     0,   )

    # Effect_of_malnutrition_on_dying[region] = WITH LOOKUP ( Malnutrition[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1 , 1 ) , ( 2 , 1.15 ) , ( 3 , 1.5 ) , ( 4 , 2 ) , ( 5 , 3 ) , ( 10 , 15 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_malnutrition_on_dying"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_malnutrition_on_dying"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Malnutrition"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Effect_of_malnutrition_on_dying_smoothed[region] = SMOOTH ( Effect_of_malnutrition_on_dying[region] , Time_to_smooth_malnutrition_effect )
    idx1 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx2 = fcol_in_mdf["Effect_of_malnutrition_on_dying"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_malnutrition_effect
        * dt
      )

    # Effect_of_poverty_on_dying[region] = WITH LOOKUP ( Fraction_of_population_below_existential_minimum[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.5 , 1.025 ) , ( 1 , 1.1 ) ) )
    tabidx = ftab_in_d_table["Effect_of_poverty_on_dying"]  # fetch the correct table
    idx2 = fcol_in_mdf["Effect_of_poverty_on_dying"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Fraction_of_population_below_existential_minimum"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Effect_of_poverty_on_dying_from_policy_start[region] =  1 + IF_THEN_ELSE ( zeit > Policy_start_year , ( Effect_of_poverty_on_dying - 1 ) * Strength_of_poverty_effect , 0 )
    idxlhs = fcol_in_mdf["Effect_of_poverty_on_dying_from_policy_start"]
    idx1 = fcol_in_mdf["Effect_of_poverty_on_dying"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + IF_THEN_ELSE(
        zeit > Policy_start_year,     (mdf[rowi, idx1 + j] - 1) * Strength_of_poverty_effect,     0,   )

    # Effect_of_poverty_on_dying_smoothed[region] = SMOOTH ( Effect_of_poverty_on_dying_from_policy_start[region] , Time_to_smooth_poverty_effect )
    idx1 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx2 = fcol_in_mdf["Effect_of_poverty_on_dying_from_policy_start"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_poverty_effect
        * dt
      )

    # Inequality_effect_on_mortality[region] = 1 + ( Actual_inequality_index_higher_is_more_unequal[region] - 1 ) * Strength_of_inequality_effect_on_mortality
    idxlhs = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx1 = fcol_in_mdf["Actual_inequality_index_higher_is_more_unequal"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (1 + (mdf[rowi, idx1 + j] - 1) * Strength_of_inequality_effect_on_mortality
      )

    # dying_0_to_4[region] = Cohort_0_to_4[region] * death_rate_dr0[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
    idxlhs = fcol_in_mdf["dying_0_to_4"]
    idx1 = fcol_in_mdf["Cohort_0_to_4"]
    idx2 = fcol_in_mdf["death_rate_dr0"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx5 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx6 = fcol_in_mdf["Inequality_effect_on_mortality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
        * mdf[rowi, idx6 + j]
      )

    # death_rate_dr35[region] = dr35_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr35_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr35"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr35_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr35_b[j]
      )

    # dying_35_to_39[region] = Cohort_35_to_39[region] * death_rate_dr35[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_35_to_39"]
    idx1 = fcol_in_mdf["Cohort_35_to_39"]
    idx2 = fcol_in_mdf["death_rate_dr35"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr40[region] = dr40_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr40_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr40"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr40_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr40_b[j]
      )

    # dying_40_to_45[region] = Cohort_40_to_44[region] * death_rate_dr40[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_40_to_45"]
    idx1 = fcol_in_mdf["Cohort_40_to_44"]
    idx2 = fcol_in_mdf["death_rate_dr40"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr50[region] = dr50_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr50_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr50"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr50_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr50_b[j]
      )

    # dying_50_to_54[region] = Cohort_50_to_54[region] * death_rate_dr50[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_50_to_54"]
    idx1 = fcol_in_mdf["Cohort_50_to_54"]
    idx2 = fcol_in_mdf["death_rate_dr50"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr55[region] = dr55_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr55_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr55"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr55_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr55_b[j]
      )

    # dying_55_to_59[region] = Cohort_55_to_59[region] * death_rate_dr55[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_55_to_59"]
    idx1 = fcol_in_mdf["Cohort_55_to_59"]
    idx2 = fcol_in_mdf["death_rate_dr55"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr60[region] = dr60_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr60_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr60"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr60_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr60_b[j]
      )

    # dying_60_to_64[region] = Cohort_60_to_64[region] * death_rate_dr60[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_60_to_64"]
    idx1 = fcol_in_mdf["Cohort_60_to_64"]
    idx2 = fcol_in_mdf["death_rate_dr60"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr65[region] = dr65_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr65_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr65"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr65_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr65_b[j]
      )

    # dying_65_to_69[region] = Cohort_65_to_69[region] * death_rate_dr65[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_65_to_69"]
    idx1 = fcol_in_mdf["Cohort_65_to_69"]
    idx2 = fcol_in_mdf["death_rate_dr65"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr70[region] = dr70_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr70_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr70"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr70_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr70_b[j]
      )

    # dying_70_to_74[region] = Cohort_70_to_74[region] * death_rate_dr70[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_70_to_74"]
    idx1 = fcol_in_mdf["Cohort_70_to_74"]
    idx2 = fcol_in_mdf["death_rate_dr70"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # death_rate_dr75[region] = dr75_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr75_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr75"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr75_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr75_b[j]
      )

    # dying_75_to_79[region] = Cohort_75_to_79[region] * death_rate_dr75[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
    idxlhs = fcol_in_mdf["dying_75_to_79"]
    idx1 = fcol_in_mdf["Cohort_75_to_79"]
    idx2 = fcol_in_mdf["death_rate_dr75"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx5 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx6 = fcol_in_mdf["Inequality_effect_on_mortality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
        * mdf[rowi, idx6 + j]
      )

    # death_rate_dr80[region] = dr80_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr80_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr80"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr80_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr80_b[j]
      )

    # dying_80_to_84[region] = Cohort_80_to_84[region] * death_rate_dr80[region] * mort_80_to_84_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
    idxlhs = fcol_in_mdf["dying_80_to_84"]
    idx1 = fcol_in_mdf["Cohort_80_to_84"]
    idx2 = fcol_in_mdf["death_rate_dr80"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx5 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx6 = fcol_in_mdf["Inequality_effect_on_mortality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mort_80_to_84_adjust_factor[j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
        * mdf[rowi, idx6 + j]
      )

    # death_rate_dr85[region] = dr85_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr85_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr85"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr85_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr85_b[j]
      )

    # dying_85_to_89[region] = Cohort_85_to_89[region] * death_rate_dr85[region] * mort_85_to_89_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
    idxlhs = fcol_in_mdf["dying_85_to_89"]
    idx1 = fcol_in_mdf["Cohort_85_to_89"]
    idx2 = fcol_in_mdf["death_rate_dr85"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx5 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx6 = fcol_in_mdf["Inequality_effect_on_mortality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mort_85_to_89_adjust_factor[j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
        * mdf[rowi, idx6 + j]
      )

    # death_rate_dr90[region] = dr90_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr90_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr90"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr90_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr90_b[j]
      )

    # dying_90_to_94[region] = Cohort_90_to_94[region] * death_rate_dr90[region] * mort_90_to_94_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
    idxlhs = fcol_in_mdf["dying_90_to_94"]
    idx1 = fcol_in_mdf["Cohort_90_to_94"]
    idx2 = fcol_in_mdf["death_rate_dr90"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx5 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx6 = fcol_in_mdf["Inequality_effect_on_mortality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mort_90_to_94_adjust_factor[j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
        * mdf[rowi, idx6 + j]
      )

    # death_rate_dr95_plus[region] = dr95p_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr95p_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr95_plus"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr95p_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr95p_b[j]
      )

    # dying_95p[region] = Cohort_95p[region] * death_rate_dr95_plus[region] * mort_95plus_adjust_factor[region] * Eff_of_env_damage_on_dying[region] * Effect_of_malnutrition_on_dying_smoothed[region] * Effect_of_poverty_on_dying_smoothed[region] * Inequality_effect_on_mortality[region]
    idxlhs = fcol_in_mdf["dying_95p"]
    idx1 = fcol_in_mdf["Cohort_95p"]
    idx2 = fcol_in_mdf["death_rate_dr95_plus"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    idx5 = fcol_in_mdf["Effect_of_poverty_on_dying_smoothed"]
    idx6 = fcol_in_mdf["Inequality_effect_on_mortality"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mort_95plus_adjust_factor[j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
        * mdf[rowi, idx6 + j]
      )

    # dying[region] = dying_0_to_4[region] + dying_35_to_39[region] + dying_40_to_45[region] + dying_50_to_54[region] + dying_55_to_59[region] + dying_60_to_64[region] + dying_65_to_69[region] + dying_70_to_74[region] + dying_75_to_79[region] + dying_80_to_84[region] + dying_85_to_89[region] + dying_90_to_94[region] + dying_95p[region]
    idxlhs = fcol_in_mdf["dying"]
    idx1 = fcol_in_mdf["dying_0_to_4"]
    idx2 = fcol_in_mdf["dying_35_to_39"]
    idx3 = fcol_in_mdf["dying_40_to_45"]
    idx4 = fcol_in_mdf["dying_50_to_54"]
    idx5 = fcol_in_mdf["dying_55_to_59"]
    idx6 = fcol_in_mdf["dying_60_to_64"]
    idx7 = fcol_in_mdf["dying_65_to_69"]
    idx8 = fcol_in_mdf["dying_70_to_74"]
    idx9 = fcol_in_mdf["dying_75_to_79"]
    idx10 = fcol_in_mdf["dying_80_to_84"]
    idx11 = fcol_in_mdf["dying_85_to_89"]
    idx12 = fcol_in_mdf["dying_90_to_94"]
    idx13 = fcol_in_mdf["dying_95p"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
        + mdf[rowi, idx7 + j]
        + mdf[rowi, idx8 + j]
        + mdf[rowi, idx9 + j]
        + mdf[rowi, idx10 + j]
        + mdf[rowi, idx11 + j]
        + mdf[rowi, idx12 + j]
        + mdf[rowi, idx13 + j]
      )

    # death_rate_dr45[region] = dr45_a[region] * ( ( GDPpp_USED_for_influencing_death_rates[region] * UNIT_conv_to_make_exp_dmnl ) ) ^ dr45_b[region]
    idxlhs = fcol_in_mdf["death_rate_dr45"]
    idx1 = fcol_in_mdf["GDPpp_USED_for_influencing_death_rates"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (dr45_a[j] * (mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl) ** dr45_b[j]
      )

    # Time_at_which_govt_debt_is_cancelled[region] = Policy_start_year
    idxlhs = fcol_in_mdf["Time_at_which_govt_debt_is_cancelled"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Policy_start_year

    # ExPS_rounds_via_Excel[region] = IF_THEN_ELSE ( zeit >= Round3_start , ExPS_R3_via_Excel , IF_THEN_ELSE ( zeit >= Round2_start , ExPS_R2_via_Excel , IF_THEN_ELSE ( zeit >= Policy_start_year , ExPS_R1_via_Excel , ExPS_policy_Min ) ) )
    idxlhs = fcol_in_mdf["ExPS_rounds_via_Excel"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit >= Round3_start,     ExPS_R3_via_Excel[j],     IF_THEN_ELSE(
          zeit >= Round2_start,       ExPS_R2_via_Excel[j],       IF_THEN_ELSE(
            zeit >= Policy_start_year, ExPS_R1_via_Excel[j], ExPS_policy_Min
          ),     ),   )

    # ExPS_policy_with_RW[region] = ExPS_rounds_via_Excel[region] * Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["ExPS_policy_with_RW"]
    idx1 = fcol_in_mdf["ExPS_rounds_via_Excel"]
    idx2 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # ExPS_pol_div_100[region] = MIN ( ExPS_policy_Max , MAX ( ExPS_policy_Min , ExPS_policy_with_RW[region] ) ) / 100
    idxlhs = fcol_in_mdf["ExPS_pol_div_100"]
    idx1 = fcol_in_mdf["ExPS_policy_with_RW"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(ExPS_policy_Max, max(ExPS_policy_Min, mdf[rowi, idx1 + j])) / 100
      )

    # Debt_cancelling_pulse[region] = ( STEP ( Debt_cancelling_stepheight , Time_at_which_govt_debt_is_cancelled[region] ) - STEP ( Debt_cancelling_stepheight , Time_at_which_govt_debt_is_cancelled[region] + Govt_debt_cancelling_spread[region] ) ) * ExPS_pol_div_100[region]
    idxlhs = fcol_in_mdf["Debt_cancelling_pulse"]
    idx1 = fcol_in_mdf["Time_at_which_govt_debt_is_cancelled"]
    idx2 = fcol_in_mdf["Time_at_which_govt_debt_is_cancelled"]
    idx3 = fcol_in_mdf["ExPS_pol_div_100"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (STEP(zeit, Debt_cancelling_stepheight, mdf[rowi, idx1 + j])
        - STEP(
          zeit,       Debt_cancelling_stepheight,       mdf[rowi, idx2 + j] + Govt_debt_cancelling_spread,     )
      ) * mdf[rowi, idx3 + j]

    # Decrease_in_GDPL[region] = Obligation_for_payback_of_debt_from_public_lenders[region] * ( 1 - Fraction_of_public_loans_not_serviced[region] )
    idxlhs = fcol_in_mdf["Decrease_in_GDPL"]
    idx1 = fcol_in_mdf["Obligation_for_payback_of_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Fraction_of_public_loans_not_serviced"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # Global_annual_shortfall_of_available_private_capital = SUM ( Annual_shortfall_of_available_private_capital[region!] )
    idxlhs = fcol_in_mdf["Global_annual_shortfall_of_available_private_capital"]
    idx1 = fcol_in_mdf["Annual_shortfall_of_available_private_capital"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # decrease_in_global_speculative_asset_pool = Global_annual_shortfall_of_available_private_capital
    idxlhs = fcol_in_mdf["decrease_in_global_speculative_asset_pool"]
    idx1 = fcol_in_mdf["Global_annual_shortfall_of_available_private_capital"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Decrease_in_public_capacity[region] = Public_capacity[region] / Lifetime_of_public_capacity
    idxlhs = fcol_in_mdf["Decrease_in_public_capacity"]
    idx1 = fcol_in_mdf["Public_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Lifetime_of_public_capacity

    # Decrease_in_public_loan_defaults[region] = Public_loan_defaults[region] / Time_to_write_of_public_loan_defaults
    idxlhs = fcol_in_mdf["Decrease_in_public_loan_defaults"]
    idx1 = fcol_in_mdf["Public_loan_defaults"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_to_write_of_public_loan_defaults
      )

    # Smoothed_cumulative_N_use_for_regenerative_choice[region] = SMOOTHI ( Cumulative_N_use_since_2020[region] , Time_for_N_use_to_affect_regeneative_choice , Cumulative_N_use_since_2020_in_1980[region] )
    idx1 = fcol_in_mdf["Smoothed_cumulative_N_use_for_regenerative_choice"]
    idx2 = fcol_in_mdf["Cumulative_N_use_since_2020"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_N_use_to_affect_regeneative_choice
        * dt
      )

    # Desired_regenerative_cropland_fraction[region] = WITH LOOKUP ( Smoothed_cumulative_N_use_for_regenerative_choice[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 10 , 0.02 ) , ( 20 , 0.1 ) , ( 30 , 0.5 ) ) )
    tabidx = ftab_in_d_table[  "Desired_regenerative_cropland_fraction"]  # fetch the correct table
    idx2 = fcol_in_mdf["Desired_regenerative_cropland_fraction"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Smoothed_cumulative_N_use_for_regenerative_choice"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Too_much_regen_cropland[region] = IF_THEN_ELSE ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction < 0 , ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction ) * - 1 , 0 )
    idxlhs = fcol_in_mdf["Too_much_regen_cropland"]
    idx1 = fcol_in_mdf["Desired_regenerative_cropland_fraction"]
    idx2 = fcol_in_mdf["FLWR_policy"]
    idx3 = fcol_in_mdf["Regenerative_cropland_fraction"]
    idx4 = fcol_in_mdf["Desired_regenerative_cropland_fraction"]
    idx5 = fcol_in_mdf["FLWR_policy"]
    idx6 = fcol_in_mdf["Regenerative_cropland_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] - mdf[rowi, idx3 + j] < 0,     (mdf[rowi, idx4 + j] + mdf[rowi, idx5 + j] - mdf[rowi, idx6 + j]) * -1,     0,   )

    # Decrease_in_regen_cropland[region] = Too_much_regen_cropland[region] / Time_to_implement_conventional_practices
    idxlhs = fcol_in_mdf["Decrease_in_regen_cropland"]
    idx1 = fcol_in_mdf["Too_much_regen_cropland"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_to_implement_conventional_practices
      )

    # Demand_imbalance[region] = ( Investment_demand[region] + Total_consumption[region] ) / Optimal_real_output[region]
    idxlhs = fcol_in_mdf["Demand_imbalance"]
    idx1 = fcol_in_mdf["Investment_demand"]
    idx2 = fcol_in_mdf["Total_consumption"]
    idx3 = fcol_in_mdf["Optimal_real_output"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]) / mdf[ rowi, idx3 + j
      ]

    # Depositing_of_C_to_sediment = C_in_deep_water_volume_1km_to_bottom_GtC / Time_to_deposit_C_in_sediment
    idxlhs = fcol_in_mdf["Depositing_of_C_to_sediment"]
    idx1 = fcol_in_mdf["C_in_deep_water_volume_1km_to_bottom_GtC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_deposit_C_in_sediment

    # Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy[region] = Reference_fraction_of_supply_imbalance_to_be_closed_by_imports[region] * ( 1 - RIPLGF_policy[region] )
    idxlhs = fcol_in_mdf["Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy"
    ]
    idx1 = fcol_in_mdf["RIPLGF_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Reference_fraction_of_supply_imbalance_to_be_closed_by_imports[j]
        * (1 - mdf[rowi, idx1 + j])
      )

    # Desired_crop_import_indicated[region] = All_crop_regional_dmd_last_year[region] * Ratio_of_demand_to_regional_supply_of_crops[region] * Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy[region]
    idxlhs = fcol_in_mdf["Desired_crop_import_indicated"]
    idx1 = fcol_in_mdf["All_crop_regional_dmd_last_year"]
    idx2 = fcol_in_mdf["Ratio_of_demand_to_regional_supply_of_crops"]
    idx3 = fcol_in_mdf["Fraction_of_supply_imbalance_to_be_closed_by_imports_after_policy"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * mdf[rowi, idx3 + j]
      )

    # Eff_of_dmd_imbalance_on_life_of_capacity[region] = 1 + Slope_of_Eff_of_dmd_imbalnce_on_life_of_capacity * ( Perceived_demand_imblance[region] / Dmd_imbalance_in_1980[region] - 1 )
    idxlhs = fcol_in_mdf["Eff_of_dmd_imbalance_on_life_of_capacity"]
    idx1 = fcol_in_mdf["Perceived_demand_imblance"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + Slope_of_Eff_of_dmd_imbalnce_on_life_of_capacity * (
        mdf[rowi, idx1 + j] / Dmd_imbalance_in_1980 - 1
      )

    # Lifetime_of_capacity[region] = Lifetime_of_capacity_in_1980 / Eff_of_dmd_imbalance_on_life_of_capacity[region]
    idxlhs = fcol_in_mdf["Lifetime_of_capacity"]
    idx1 = fcol_in_mdf["Eff_of_dmd_imbalance_on_life_of_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Lifetime_of_capacity_in_1980 / mdf[rowi, idx1 + j]

    # Discarding_capacity[region] = Capacity[region] / Lifetime_of_capacity[region]
    idxlhs = fcol_in_mdf["Discarding_capacity"]
    idx1 = fcol_in_mdf["Capacity"]
    idx2 = fcol_in_mdf["Lifetime_of_capacity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # dying_45_to_49[region] = Cohort_45_to_49[region] * death_rate_dr45[region] * Eff_of_env_damage_on_dying[region] * Inequality_effect_on_mortality[region] * Effect_of_malnutrition_on_dying_smoothed[region]
    idxlhs = fcol_in_mdf["dying_45_to_49"]
    idx1 = fcol_in_mdf["Cohort_45_to_49"]
    idx2 = fcol_in_mdf["death_rate_dr45"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_dying"]
    idx4 = fcol_in_mdf["Inequality_effect_on_mortality"]
    idx5 = fcol_in_mdf["Effect_of_malnutrition_on_dying_smoothed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * mdf[rowi, idx2 + j]
        * mdf[rowi, idx3 + j]
        * mdf[rowi, idx4 + j]
        * mdf[rowi, idx5 + j]
      )

    # Eff_of_env_damage_on_TFP[region] = math.exp ( Combined_env_damage_indicator * expSoE_of_ed_on_TFP ) / Actual_eff_of_relative_wealth_on_env_damage[region]
    idxlhs = fcol_in_mdf["Eff_of_env_damage_on_TFP"]
    idx1 = fcol_in_mdf["Combined_env_damage_indicator"]
    idx2 = fcol_in_mdf["Actual_eff_of_relative_wealth_on_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (math.exp(mdf[rowi, idx1] * expSoE_of_ed_on_TFP) / mdf[rowi, idx2 + j]
      )

    # Eff_of_wealth_on_regnerative_practices[region] = WITH LOOKUP ( GDPpp_USED[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 60 , 0.9 ) ) )
    tabidx = ftab_in_d_table[  "Eff_of_wealth_on_regnerative_practices"]  # fetch the correct table
    idx2 = fcol_in_mdf["Eff_of_wealth_on_regnerative_practices"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["GDPpp_USED"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # TFP_including_effect_of_env_damage[region] = Total_factor_productivity_TFP_before_env_damage[region] / Eff_of_env_damage_on_TFP[region]
    idxlhs = fcol_in_mdf["TFP_including_effect_of_env_damage"]
    idx1 = fcol_in_mdf["Total_factor_productivity_TFP_before_env_damage"]
    idx2 = fcol_in_mdf["Eff_of_env_damage_on_TFP"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Indicated_TFP[region] = TFP_including_effect_of_env_damage[region]
    idxlhs = fcol_in_mdf["Indicated_TFP"]
    idx1 = fcol_in_mdf["TFP_including_effect_of_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Effect_of_capacity_renewal[region] = ( Indicated_TFP[region] - Embedded_TFP[region] ) * Capacity_renewal_rate[region]
    idxlhs = fcol_in_mdf["Effect_of_capacity_renewal"]
    idx1 = fcol_in_mdf["Indicated_TFP"]
    idx2 = fcol_in_mdf["Embedded_TFP"]
    idx3 = fcol_in_mdf["Capacity_renewal_rate"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) * mdf[ rowi, idx3 + j
      ]

    # Effect_of_GL_on_freshwater_use = WITH LOOKUP ( Which_Scenario_is_run_globally , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 0.97 ) , ( 0.5 , 0.9 ) , ( 0.75 , 0.8 ) , ( 1 , 0.66 ) ) )
    tabidx = ftab_in_d_table[  "Effect_of_GL_on_freshwater_use"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Effect_of_GL_on_freshwater_use"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Which_Scenario_is_run_globally"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Effect_of_GL_on_phaseout_time = WITH LOOKUP ( Which_Scenario_is_run_globally , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 1 ) , ( 0.25 , 0.97 ) , ( 0.5 , 0.9 ) , ( 0.75 , 0.5 ) , ( 1 , 0.33 ) ) )
    tabidx = ftab_in_d_table["Effect_of_GL_on_phaseout_time"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Effect_of_GL_on_phaseout_time"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Which_Scenario_is_run_globally"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Effect_of_humidity_on_shifting_biomes = 1 + Sensitivity_of_trop_to_humidity * ( Humidity_of_atmosphere / Humidity_of_atmosphere_in_1850_g_p_kg - 1 )
    idxlhs = fcol_in_mdf["Effect_of_humidity_on_shifting_biomes"]
    idx1 = fcol_in_mdf["Humidity_of_atmosphere"]
    mdf[rowi, idxlhs] = 1 + Sensitivity_of_trop_to_humidity * (
      mdf[rowi, idx1] / Humidity_of_atmosphere_in_1850_g_p_kg - 1
    )

    # Worker_to_owner_income_after_tax_ratio[region] = Worker_income_after_tax[region] / Owner_income_after_tax_but_before_lending_transactions[region]
    idxlhs = fcol_in_mdf["Worker_to_owner_income_after_tax_ratio"]
    idx1 = fcol_in_mdf["Worker_income_after_tax"]
    idx2 = fcol_in_mdf["Owner_income_after_tax_but_before_lending_transactions"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Worker_to_owner_income_after_tax_ratio_scaled_to_init[region] = Worker_to_owner_income_after_tax_ratio[region] / Worker_to_owner_income_after_tax_ratio_in_1980[region]
    idxlhs = fcol_in_mdf["Worker_to_owner_income_after_tax_ratio_scaled_to_init"]
    idx1 = fcol_in_mdf["Worker_to_owner_income_after_tax_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Worker_to_owner_income_after_tax_ratio_in_1980[j]
      )

    # Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init[region] = 1 + Strength_of_effect_of_income_ratio_after_tax * ( Worker_to_owner_income_after_tax_ratio_scaled_to_init[region] - 1 )
    idxlhs = fcol_in_mdf["Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init"
    ]
    idx1 = fcol_in_mdf["Worker_to_owner_income_after_tax_ratio_scaled_to_init"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 + Strength_of_effect_of_income_ratio_after_tax * (
        mdf[rowi, idx1 + j] - 1
      )

    # Effective_GDPpp_for_OSF[region] = SMOOTH ( GDPpp_USED[region] , Time_for_GDPpp_to_affect_owner_saving_fraction )
    idx1 = fcol_in_mdf["Effective_GDPpp_for_OSF"]
    idx2 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_for_GDPpp_to_affect_owner_saving_fraction
        * dt
      )

    # TROP_deforestation_cutoff_effect = WITH LOOKUP ( TROP_deforested_as_pct_of_potential_area , ( [ ( 0.5 , 0 ) - ( 0.8 , 10 ) ] , ( 0.5 , 1 ) , ( 0.619266 , 1.92982 ) , ( 0.683486 , 2.7193 ) , ( 0.733028 , 4.03509 ) , ( 0.76055 , 5.26316 ) , ( 0.783486 , 6.84211 ) , ( 0.8 , 10 ) ) )
    tabidx = ftab_in_d_table[  "TROP_deforestation_cutoff_effect"]  # fetch the correct table
    idxlhs = fcol_in_mdf["TROP_deforestation_cutoff_effect"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["TROP_deforested_as_pct_of_potential_area"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Effective_Time_to_regrow_TROP_after_deforesting = Reference_Time_to_regrow_TROP_after_deforesting / TROP_deforestation_cutoff_effect
    idxlhs = fcol_in_mdf["Effective_Time_to_regrow_TROP_after_deforesting"]
    idx1 = fcol_in_mdf["TROP_deforestation_cutoff_effect"]
    mdf[rowi, idxlhs] = (
      Reference_Time_to_regrow_TROP_after_deforesting / mdf[rowi, idx1]
    )

    # Labor_pool[region] = Employed[region] + Unemployed[region]
    idxlhs = fcol_in_mdf["Labor_pool"]
    idx1 = fcol_in_mdf["Employed"]
    idx2 = fcol_in_mdf["Unemployed"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Employed_to_labor_pool_ratio[region] = Employed[region] / Labor_pool[region]
    idxlhs = fcol_in_mdf["Employed_to_labor_pool_ratio"]
    idx1 = fcol_in_mdf["Employed"]
    idx2 = fcol_in_mdf["Labor_pool"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Labor_market_imbalance[region] = Labor_pool[region] / Max_people_in_labour_pool[region]
    idxlhs = fcol_in_mdf["Labor_market_imbalance"]
    idx1 = fcol_in_mdf["Labor_pool"]
    idx2 = fcol_in_mdf["Max_people_in_labour_pool"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Limitation_on_entering_the_pool_from_market_imbalance[region] = WITH LOOKUP ( Labor_market_imbalance[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0.7 , 1 ) , ( 0.75 , 0.97 ) , ( 0.8 , 0.9 ) , ( 0.85 , 0.8 ) , ( 0.9 , 0.65 ) , ( 0.95 , 0.4 ) , ( 1 , 0.02 ) ) )
    tabidx = ftab_in_d_table[  "Limitation_on_entering_the_pool_from_market_imbalance"]  # fetch the correct table
    idx2 = fcol_in_mdf["Limitation_on_entering_the_pool_from_market_imbalance"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Labor_market_imbalance"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Entering_the_labor_pool[region] = ( People_considering_entering_the_pool[region] / Time_to_implement_actually_entering_the_pool ) * Limitation_on_entering_the_pool_from_market_imbalance[region]
    idxlhs = fcol_in_mdf["Entering_the_labor_pool"]
    idx1 = fcol_in_mdf["People_considering_entering_the_pool"]
    idx2 = fcol_in_mdf["Limitation_on_entering_the_pool_from_market_imbalance"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_to_implement_actually_entering_the_pool
      ) * mdf[rowi, idx2 + j]

    # Evaporation_aka_latent_heat_flow = Evaporation_as_f_of_temp
    idxlhs = fcol_in_mdf["Evaporation_aka_latent_heat_flow"]
    idx1 = fcol_in_mdf["Evaporation_as_f_of_temp"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Greenland_ice_volume_as_fraction_of_1850_volume = Greenland_ice_volume_in_1980 / Greenland_ice_volume_on_Greenland_km3
    idxlhs = fcol_in_mdf["Greenland_ice_volume_as_fraction_of_1850_volume"]
    idx1 = fcol_in_mdf["Greenland_ice_volume_on_Greenland_km3"]
    mdf[rowi, idxlhs] = Greenland_ice_volume_in_1980 / mdf[rowi, idx1]

    # Greenland_slide_experiment_end_condition = WITH LOOKUP ( Greenland_ice_volume_as_fraction_of_1850_volume , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 0.1 , 0.05 ) , ( 0.2 , 0.2 ) , ( 0.3 , 0.5 ) , ( 0.4 , 0.75 ) , ( 0.5 , 0.93 ) , ( 0.6 , 1 ) ) )
    tabidx = ftab_in_d_table[  "Greenland_slide_experiment_end_condition"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Greenland_slide_experiment_end_condition"]  # get the location of the lhs in mdf
    idx1 = fcol_in_mdf["Greenland_ice_volume_as_fraction_of_1850_volume"]
    look = d_table[tabidx]
    valgt = GRAPH(mdf[rowi, idx1], look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Exogenous_sliding_of_Greenland_ice_into_the_ocean = IF_THEN_ELSE ( zeit > NEvt_13d_Greenland_slide_experiment_start_yr , Greenland_slide_experiment_how_much_sildes_in_the_ocean_fraction / ( Greenland_slide_experiment_over_how_many_years_yr * 0.7 ) , 0 )
    idxlhs = fcol_in_mdf["Exogenous_sliding_of_Greenland_ice_into_the_ocean"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > NEvt_13d_Greenland_slide_experiment_start_yr,   Greenland_slide_experiment_how_much_sildes_in_the_ocean_fraction
      / (Greenland_slide_experiment_over_how_many_years_yr * 0.7),   0, )

    # Max_forest_cut_after_policy[region] = Forest_land[region] * Reference_max_fraction_of_forest_possible_to_cut
    idxlhs = fcol_in_mdf["Max_forest_cut_after_policy"]
    idx1 = fcol_in_mdf["Forest_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * Reference_max_fraction_of_forest_possible_to_cut
      )

    # Fraction_of_cropland_gap_closed_by_cutting_forests[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.1 ) , ( 2010 , - 0.1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.05 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0.03 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0.001 ) , ( 2100 , 0.01 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.03 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0.0003 ) , ( 2050 , 0.001 ) , ( 2100 , 0.002 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.03 ) , ( 2000 , 0.01 ) , ( 2010 , 0.01 ) , ( 2020 , 0.01 ) , ( 2030 , 0.01 ) , ( 2050 , 0.01 ) , ( 2100 , 0.01 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0.03 ) , ( 2020 , 0 ) , ( 2030 , 0.0003 ) , ( 2050 , 0.001 ) , ( 2100 , 0.001 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.03 ) , ( 2000 , 0.01 ) , ( 2010 , 0.01 ) , ( 2020 , 0.01 ) , ( 2030 , 0.0107 ) , ( 2050 , 0.012 ) , ( 2100 , 0.015 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0.000161 ) , ( 2050 , 0.001 ) , ( 2100 , 0.002 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.1 ) , ( 2010 , - 0.1 ) , ( 2020 , 0 ) , ( 2031 , 0 ) , ( 2050 , - 0.001 ) , ( 2100 , - 0.002 ) ) ) Fraction_of_cropland_gap_closed_by_cutting_forests[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.02 ) , ( 2000 , 0 ) , ( 2010 , 0.03 ) , ( 2020 , 0 ) , ( 2030 , 0.00036 ) , ( 2050 , 0.001 ) , ( 2100 , 0.002 ) ) )
    tabidx = ftab_in_d_table[  "Fraction_of_cropland_gap_closed_by_cutting_forests"]  # fetch the correct table
    idx2 = fcol_in_mdf["Fraction_of_cropland_gap_closed_by_cutting_forests"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # fa_to_c[region] = MIN ( Max_forest_cut_after_policy[region] , MIN ( Forest_land[region] , MAX ( 0 , Cropland_gap[region] ) ) * Fraction_of_cropland_gap_closed_by_cutting_forests[region] )
    idxlhs = fcol_in_mdf["fa_to_c"]
    idx1 = fcol_in_mdf["Max_forest_cut_after_policy"]
    idx2 = fcol_in_mdf["Forest_land"]
    idx3 = fcol_in_mdf["Cropland_gap"]
    idx4 = fcol_in_mdf["Fraction_of_cropland_gap_closed_by_cutting_forests"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(
        mdf[rowi, idx1 + j],     min(mdf[rowi, idx2 + j], max(0, mdf[rowi, idx3 + j])) * mdf[rowi, idx4 + j],   )

    # Fraction_of_grazing_land_gap_closed_by_cutting_forests[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 1 ) , ( 2020 , 1 ) , ( 2030 , 1 ) , ( 2050 , 1 ) , ( 2075 , 1 ) , ( 2100 , 1 ) ) ) Fraction_of_grazing_land_gap_closed_by_cutting_forests[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1 ) , ( 2000 , 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) )
    tabidx = ftab_in_d_table[  "Fraction_of_grazing_land_gap_closed_by_cutting_forests"]  # fetch the correct table
    idx2 = fcol_in_mdf["Fraction_of_grazing_land_gap_closed_by_cutting_forests"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # fa_to_gl[region] = MIN ( Max_forest_cut_after_policy[region] , MIN ( Forest_land[region] , MAX ( 0 , Grazing_land_gap[region] ) ) * Fraction_of_grazing_land_gap_closed_by_cutting_forests[region] )
    idxlhs = fcol_in_mdf["fa_to_gl"]
    idx1 = fcol_in_mdf["Max_forest_cut_after_policy"]
    idx2 = fcol_in_mdf["Forest_land"]
    idx3 = fcol_in_mdf["Grazing_land_gap"]
    idx4 = fcol_in_mdf["Fraction_of_grazing_land_gap_closed_by_cutting_forests"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = min(
        mdf[rowi, idx1 + j],     min(mdf[rowi, idx2 + j], max(0, mdf[rowi, idx3 + j])) * mdf[rowi, idx4 + j],   )

    # Flow_of_C_from_atm_to_biomass_GtC_py = CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py + CO2_flux_from_atm_to_NF_for_new_growth_GtC_py + CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py + CO2_flux_from_atm_to_TUNDRA_for_new_growth
    idxlhs = fcol_in_mdf["Flow_of_C_from_atm_to_biomass_GtC_py"]
    idx1 = fcol_in_mdf["CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py"]
    idx2 = fcol_in_mdf["CO2_flux_from_atm_to_NF_for_new_growth_GtC_py"]
    idx3 = fcol_in_mdf["CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py"]
    idx4 = fcol_in_mdf["CO2_flux_from_atm_to_TUNDRA_for_new_growth"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    )

    # Flow_of_C_from_biomass_to_atm = CO2_flux_GRASS_to_atm_GtC_py + CO2_flux_NF_to_atm_GtC_py + CO2_flux_TROP_to_atm_GtC_py + CO2_flux_TUNDRA_to_atm
    idxlhs = fcol_in_mdf["Flow_of_C_from_biomass_to_atm"]
    idx1 = fcol_in_mdf["CO2_flux_GRASS_to_atm_GtC_py"]
    idx2 = fcol_in_mdf["CO2_flux_NF_to_atm_GtC_py"]
    idx3 = fcol_in_mdf["CO2_flux_TROP_to_atm_GtC_py"]
    idx4 = fcol_in_mdf["CO2_flux_TUNDRA_to_atm"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    )

    # Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr = Cold_dense_water_sinking_in_Sverdrup * UNIT_conversion_Sv_to_Gm3_py
    idxlhs = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    idx1 = fcol_in_mdf["Cold_dense_water_sinking_in_Sverdrup"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_Sv_to_Gm3_py

    # Flow_of_cold_surface_water_welling_down_GcubicM_per_yr = Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr
    idxlhs = fcol_in_mdf["Flow_of_cold_surface_water_welling_down_GcubicM_per_yr"]
    idx1 = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Flow_of_water_from_warm_to_cold_surface_Gcubicm_per_yr = Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr
    idxlhs = fcol_in_mdf["Flow_of_water_from_warm_to_cold_surface_Gcubicm_per_yr"]
    idx1 = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Total_land_area[region] = Abandoned_crop_and_grazing_land[region] + Abandoned_populated_land[region] + Barren_land_which_is_ice_and_snow[region] + Cropland[region] + Grazing_land[region] + Populated_land[region] + Forest_land[region]
    idxlhs = fcol_in_mdf["Total_land_area"]
    idx1 = fcol_in_mdf["Abandoned_crop_and_grazing_land"]
    idx2 = fcol_in_mdf["Abandoned_populated_land"]
    idx3 = fcol_in_mdf["Barren_land_which_is_ice_and_snow"]
    idx4 = fcol_in_mdf["Cropland"]
    idx5 = fcol_in_mdf["Grazing_land"]
    idx6 = fcol_in_mdf["Populated_land"]
    idx7 = fcol_in_mdf["Forest_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
        + mdf[rowi, idx6 + j]
        + mdf[rowi, idx7 + j]
      )

    # Forest_area_as_pct_of_total_land[region] = Forest_land[region] / Total_land_area[region]
    idxlhs = fcol_in_mdf["Forest_area_as_pct_of_total_land"]
    idx1 = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["Total_land_area"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Forest_area_as_pct_of_total_land_last_year[region] = SMOOTH3 ( Forest_area_as_pct_of_total_land[region] , One_year )
    idxin = fcol_in_mdf["Forest_area_as_pct_of_total_land"]
    idx2 = fcol_in_mdf["Forest_area_as_pct_of_total_land_last_year_2"]
    idx1 = fcol_in_mdf["Forest_area_as_pct_of_total_land_last_year_1"]
    idxout = fcol_in_mdf["Forest_area_as_pct_of_total_land_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Forest_area_last_year[region] = SMOOTH3I ( Forest_land[region] , One_year , Forest_land_in_1980[region] )
    idxlhs = fcol_in_mdf["Forest_area_last_year"]
    idxin = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["Forest_area_last_year_2"]
    idx1 = fcol_in_mdf["Forest_area_last_year_1"]
    idxout = fcol_in_mdf["Forest_area_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Forest_cutting_policy_used[region] = 1 - Forest_cutting_policy[region]
    idxlhs = fcol_in_mdf["Forest_cutting_policy_used"]
    idx1 = fcol_in_mdf["Forest_cutting_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = 1 - mdf[rowi, idx1 + j]

    # NF_area = NF_Living_biomass_GtBiomass / NF_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conv_to_Mkm2
    idxlhs = fcol_in_mdf["NF_area"]
    idx1 = fcol_in_mdf["NF_Living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["NF_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] * UNIT_conv_to_Mkm2

    # TROP_area = TROP_Living_biomass_GtBiomass / TROP_living_biomass_densitiy_tBiomass_pr_km2 * UNIT_conv_to_Mkm2
    idxlhs = fcol_in_mdf["TROP_area"]
    idx1 = fcol_in_mdf["TROP_Living_biomass_GtBiomass"]
    idx2 = fcol_in_mdf["TROP_living_biomass_densitiy_tBiomass_pr_km2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2] * UNIT_conv_to_Mkm2

    # pb_Forest_degradation = ( NF_area + TROP_area ) * Effect_of_population_on_forest_degradation_and_biocapacity
    idxlhs = fcol_in_mdf["pb_Forest_degradation"]
    idx1 = fcol_in_mdf["NF_area"]
    idx2 = fcol_in_mdf["TROP_area"]
    idx3 = fcol_in_mdf["Effect_of_population_on_forest_degradation_and_biocapacity"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2]) * mdf[rowi, idx3]

    # Forest_degradation_risk_score = IF_THEN_ELSE ( pb_Forest_degradation_green_threshold > pb_Forest_degradation , 0 , 1 )
    idxlhs = fcol_in_mdf["Forest_degradation_risk_score"]
    idx1 = fcol_in_mdf["pb_Forest_degradation"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      pb_Forest_degradation_green_threshold > mdf[rowi, idx1], 0, 1
    )

    # Forest_land_last_year[region] = SMOOTH3I ( Forest_land[region] , One_year , Forest_land_in_1980[region] )
    idxlhs = fcol_in_mdf["Forest_land_last_year"]
    idxin = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["Forest_land_last_year_2"]
    idx1 = fcol_in_mdf["Forest_land_last_year_1"]
    idxout = fcol_in_mdf["Forest_land_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Indicted_Fraction_deforested[region] = Annual_pct_deforested[region] * Forest_cutting_policy_used[region] / UNIT_conv_pct_to_fraction
    idxlhs = fcol_in_mdf["Indicted_Fraction_deforested"]
    idx1 = fcol_in_mdf["Forest_cutting_policy_used"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Annual_pct_deforested[j] * mdf[rowi, idx1 + j] / UNIT_conv_pct_to_fraction
      )

    # Fraction_deforested[region] = SMOOTH ( Indicted_Fraction_deforested[region] , Time_to_implement_deforestation )
    idx1 = fcol_in_mdf["Fraction_deforested"]
    idx2 = fcol_in_mdf["Indicted_Fraction_deforested"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_implement_deforestation
        * dt
      )

    # Fraction_of_govt_loan_obligations_to_PL_met[region] = ZIDZ ( Govt_loan_obligations_to_PL_MET[region] , Govt_loan_obligations_to_PL[region] )
    idxlhs = fcol_in_mdf["Fraction_of_govt_loan_obligations_to_PL_met"]
    idx1 = fcol_in_mdf["Govt_loan_obligations_to_PL_MET"]
    idx2 = fcol_in_mdf["Govt_loan_obligations_to_PL"]
    for i in range(0, 10):
      mdf[rowi, idxlhs + i] = ZIDZ(mdf[rowi, idx1 + i], mdf[rowi, idx2 + i])

    # Fraction_of_population_over_50_still_working[region] = WITH LOOKUP ( GDPpp_USED[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0.95 ) , ( 50 , 0.8 ) , ( 100 , 0.5 ) ) )
    tabidx = ftab_in_d_table[  "Fraction_of_population_over_50_still_working"]  # fetch the correct table
    idx2 = fcol_in_mdf["Fraction_of_population_over_50_still_working"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["GDPpp_USED"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Freshwater_withdrawal_per_person = Freshwater_withdrawal_per_person_TLTL * Effect_of_GL_on_freshwater_use
    idxlhs = fcol_in_mdf["Freshwater_withdrawal_per_person"]
    idx1 = fcol_in_mdf["Effect_of_GL_on_freshwater_use"]
    mdf[rowi, idxlhs] = Freshwater_withdrawal_per_person_TLTL * mdf[rowi, idx1]

    # pb_Freshwater_withdrawal[region] = Freshwater_withdrawal_per_person * Population[region] * UNIT_conv_to_cubic_km_pr_yr
    idxlhs = fcol_in_mdf["pb_Freshwater_withdrawal"]
    idx1 = fcol_in_mdf["Freshwater_withdrawal_per_person"]
    idx2 = fcol_in_mdf["Population"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1] * mdf[rowi, idx2 + j] * UNIT_conv_to_cubic_km_pr_yr
      )

    # pb_Freshwater_withdrawal_global = SUM ( pb_Freshwater_withdrawal[region!] )
    idxlhs = fcol_in_mdf["pb_Freshwater_withdrawal_global"]
    idx1 = fcol_in_mdf["pb_Freshwater_withdrawal"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Freshwater_withdrawal_risk_score = IF_THEN_ELSE ( pb_Freshwater_withdrawal_global > pb_Freshwater_withdrawal_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Freshwater_withdrawal_risk_score"]
    idx1 = fcol_in_mdf["pb_Freshwater_withdrawal_global"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > pb_Freshwater_withdrawal_green_threshold, 1, 0
    )

    # Funds_from_private_investment_leaked[region] = ( Private_Investment_in_new_capacity[region] ) * Future_leakage[region]
    idxlhs = fcol_in_mdf["Funds_from_private_investment_leaked"]
    idx1 = fcol_in_mdf["Private_Investment_in_new_capacity"]
    idx2 = fcol_in_mdf["Future_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]) * mdf[rowi, idx2 + j]

    # Funds_leaked_during_transfer_to_workers[region] = Gross_Govt_income[region] * Fraction_of_govt_income_transferred_to_workers[region] * Future_leakage[region]
    idxlhs = fcol_in_mdf["Funds_leaked_during_transfer_to_workers"]
    idx1 = fcol_in_mdf["Gross_Govt_income"]
    idx2 = fcol_in_mdf["Fraction_of_govt_income_transferred_to_workers"]
    idx3 = fcol_in_mdf["Future_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] * mdf[rowi, idx3 + j]
      )

    # Funds_leaks_on_the_way_to_investment_in_public_capacity[region] = ( Govt_investment_in_public_capacity[region] + Public_money_from_LPB_policy_to_investment[region] ) * Future_leakage[region]
    idxlhs = fcol_in_mdf["Funds_leaks_on_the_way_to_investment_in_public_capacity"]
    idx1 = fcol_in_mdf["Govt_investment_in_public_capacity"]
    idx2 = fcol_in_mdf["Public_money_from_LPB_policy_to_investment"]
    idx3 = fcol_in_mdf["Future_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]) * mdf[ rowi, idx3 + j
      ]

    # Funds_leaks_on_the_way_to_public_services[region] = ( Govt_consumption_ie_purchases[region] + Public_money_from_LPB_policy_to_public_spending[region] ) * Future_leakage[region]
    idxlhs = fcol_in_mdf["Funds_leaks_on_the_way_to_public_services"]
    idx1 = fcol_in_mdf["Govt_consumption_ie_purchases"]
    idx2 = fcol_in_mdf["Public_money_from_LPB_policy_to_public_spending"]
    idx3 = fcol_in_mdf["Future_leakage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]) * mdf[ rowi, idx3 + j
      ]

    # Increase_in_funds_leaked[region] = Funds_from_private_investment_leaked[region] + Funds_leaked_during_transfer_to_workers[region] + Funds_leaks_on_the_way_to_investment_in_public_capacity[region] + Funds_leaks_on_the_way_to_public_services[region]
    idxlhs = fcol_in_mdf["Increase_in_funds_leaked"]
    idx1 = fcol_in_mdf["Funds_from_private_investment_leaked"]
    idx2 = fcol_in_mdf["Funds_leaked_during_transfer_to_workers"]
    idx3 = fcol_in_mdf["Funds_leaks_on_the_way_to_investment_in_public_capacity"]
    idx4 = fcol_in_mdf["Funds_leaks_on_the_way_to_public_services"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
      )

    # future_deforestation[region] = IF_THEN_ELSE ( zeit > Policy_start_year , Forest_land * Fraction_deforested , 0 )
    idxlhs = fcol_in_mdf["future_deforestation"]
    idx1 = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["Fraction_deforested"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit > Policy_start_year, mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j], 0
      )

    # LW_TOA_radiation_from_atm_to_space_W_p_m2 = LW_TOA_radiation_from_atm_to_space / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["LW_TOA_radiation_from_atm_to_space_W_p_m2"]
    idx1 = fcol_in_mdf["LW_TOA_radiation_from_atm_to_space"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # GDP_model_one_year_ago[region] = SMOOTH3 ( GDP_model[region] , One_year )
    idxin = fcol_in_mdf["GDP_model"]
    idx2 = fcol_in_mdf["GDP_model_one_year_ago_2"]
    idx1 = fcol_in_mdf["GDP_model_one_year_ago_1"]
    idxout = fcol_in_mdf["GDP_model_one_year_ago"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # GDPpp_model_One_yr_ago[region] = SMOOTH3 ( GDPpp_model[region] , One_year )
    idxin = fcol_in_mdf["GDPpp_model"]
    idx2 = fcol_in_mdf["GDPpp_model_One_yr_ago_2"]
    idx1 = fcol_in_mdf["GDPpp_model_One_yr_ago_1"]
    idxout = fcol_in_mdf["GDPpp_model_One_yr_ago"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Hiring_rate[region] = Additional_people_required[region] / Time_required_to_fill_jobs
    idxlhs = fcol_in_mdf["Hiring_rate"]
    idx1 = fcol_in_mdf["Additional_people_required"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Time_required_to_fill_jobs

    # Unemployed_to_labor_pool_ratio[region] = Unemployed[region] / Labor_pool[region]
    idxlhs = fcol_in_mdf["Unemployed_to_labor_pool_ratio"]
    idx1 = fcol_in_mdf["Unemployed"]
    idx2 = fcol_in_mdf["Labor_pool"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Getting_a_job_cut_off[region] = WITH LOOKUP ( Unemployed_to_labor_pool_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0.01 , 0 ) , ( 0.02 , 0.02 ) , ( 0.04 , 0.25 ) , ( 0.06 , 0.7 ) , ( 0.08 , 0.95 ) , ( 0.1 , 1 ) ) )
    tabidx = ftab_in_d_table["Getting_a_job_cut_off"]  # fetch the correct table
    idx2 = fcol_in_mdf["Getting_a_job_cut_off"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Unemployed_to_labor_pool_ratio"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Getting_a_job[region] = Hiring_rate[region] * Getting_a_job_cut_off[region]
    idxlhs = fcol_in_mdf["Getting_a_job"]
    idx1 = fcol_in_mdf["Hiring_rate"]
    idx2 = fcol_in_mdf["Getting_a_job_cut_off"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # N2O_emissions_in_CO2e[region] = ( N2O_emi_from_agri[region] + N2O_emi_X_agri[region] ) * Global_Warming_Potential_N20 / UNIT_conversion_Gt_to_Mt
    idxlhs = fcol_in_mdf["N2O_emissions_in_CO2e"]
    idx1 = fcol_in_mdf["N2O_emi_from_agri"]
    idx2 = fcol_in_mdf["N2O_emi_X_agri"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j])
        * Global_Warming_Potential_N20
        / UNIT_conversion_Gt_to_Mt
      )

    # Total_CO2_emissions_in_CO2e[region] = Total_CO2_emissions[region] * Global_warming_potential_CO2
    idxlhs = fcol_in_mdf["Total_CO2_emissions_in_CO2e"]
    idx1 = fcol_in_mdf["Total_CO2_emissions"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * Global_warming_potential_CO2

    # Kyoto_Fluor_emissions_allocated_to_region[region] = Kyoto_Fluor_emissions_GtCO2e_py * Regional_population_as_fraction_of_total[region]
    idxlhs = fcol_in_mdf["Kyoto_Fluor_emissions_allocated_to_region"]
    idx1 = fcol_in_mdf["Kyoto_Fluor_emissions_GtCO2e_py"]
    idx2 = fcol_in_mdf["Regional_population_as_fraction_of_total"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1] * mdf[rowi, idx2 + j]

    # Montreal_emissions_allocated_to_region[region] = Montreal_emissions_GtCO2e_py * Regional_population_as_fraction_of_total[region]
    idxlhs = fcol_in_mdf["Montreal_emissions_allocated_to_region"]
    idx1 = fcol_in_mdf["Montreal_emissions_GtCO2e_py"]
    idx2 = fcol_in_mdf["Regional_population_as_fraction_of_total"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1] * mdf[rowi, idx2 + j]

    # Total_GHG_emissions[region] = CH4_Emissions_CO2e[region] + N2O_emissions_in_CO2e[region] + Total_CO2_emissions_in_CO2e[region] + Kyoto_Fluor_emissions_allocated_to_region[region] + Montreal_emissions_allocated_to_region[region]
    idxlhs = fcol_in_mdf["Total_GHG_emissions"]
    idx1 = fcol_in_mdf["CH4_Emissions_CO2e"]
    idx2 = fcol_in_mdf["N2O_emissions_in_CO2e"]
    idx3 = fcol_in_mdf["Total_CO2_emissions_in_CO2e"]
    idx4 = fcol_in_mdf["Kyoto_Fluor_emissions_allocated_to_region"]
    idx5 = fcol_in_mdf["Montreal_emissions_allocated_to_region"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        + mdf[rowi, idx2 + j]
        + mdf[rowi, idx3 + j]
        + mdf[rowi, idx4 + j]
        + mdf[rowi, idx5 + j]
      )

    # GHG_intensity[region] = Total_GHG_emissions[region] / GDP_USED[region] * UNIT_conversion_to_tCO2e_pr_USD
    idxlhs = fcol_in_mdf["GHG_intensity"]
    idx1 = fcol_in_mdf["Total_GHG_emissions"]
    idx2 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j] * UNIT_conversion_to_tCO2e_pr_USD
      )

    # GHG_intensity_last_year[region] = SMOOTH3 ( GHG_intensity[region] , One_year )
    idxin = fcol_in_mdf["GHG_intensity"]
    idx2 = fcol_in_mdf["GHG_intensity_last_year_2"]
    idx1 = fcol_in_mdf["GHG_intensity_last_year_1"]
    idxout = fcol_in_mdf["GHG_intensity_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # gl_to_acgl[region] = abs ( MIN ( 0 , Grazing_land_gap[region] ) ) / Time_for_agri_land_to_become_abandoned
    idxlhs = fcol_in_mdf["gl_to_acgl"]
    idx1 = fcol_in_mdf["Grazing_land_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (abs(min(0, mdf[rowi, idx1 + j])) / Time_for_agri_land_to_become_abandoned
      )

    # Glacial_ice_melting_km3_py = IF_THEN_ELSE ( Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py > 0 , Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
    idxlhs = fcol_in_mdf["Glacial_ice_melting_km3_py"]
    idx1 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx2 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] > 0, mdf[rowi, idx2], 0)

    # Glacial_ice_area_decrease_Mkm2_pr_yr = ( Glacial_ice_melting_km3_py / Avg_thickness_glacier_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
    idxlhs = fcol_in_mdf["Glacial_ice_area_decrease_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Glacial_ice_melting_km3_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Avg_thickness_glacier_km
    ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py

    # Glacial_ice_freezing_km3_py = IF_THEN_ELSE ( Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py < 0 , Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * ( - 1 ) , 0 )
    idxlhs = fcol_in_mdf["Glacial_ice_freezing_km3_py"]
    idx1 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx2 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] < 0, mdf[rowi, idx2] * (-1), 0)

    # Glacial_ice_area_increase_Mkm2_pr_yr = ( Glacial_ice_freezing_km3_py / Avg_thickness_glacier_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
    idxlhs = fcol_in_mdf["Glacial_ice_area_increase_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Glacial_ice_freezing_km3_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Avg_thickness_glacier_km
    ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py

    # Glacial_ice_melting_as_water_km3_py = Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py * Densitiy_of_water_relative_to_ice
    idxlhs = fcol_in_mdf["Glacial_ice_melting_as_water_km3_py"]
    idx1 = fcol_in_mdf["Glacial_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Densitiy_of_water_relative_to_ice

    # Global_annual_surplus_of_available_private_capital = SUM ( Annual_surplus_of_available_private_capital[region!] )
    idxlhs = fcol_in_mdf["Global_annual_surplus_of_available_private_capital"]
    idx1 = fcol_in_mdf["Annual_surplus_of_available_private_capital"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_CH4_emi_from_agriculture_H_PRIMAP = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 111.22 ) , ( 1981 , 111 ) , ( 1982 , 112.06 ) , ( 1983 , 112.42 ) , ( 1984 , 112.16 ) , ( 1985 , 112.37 ) , ( 1986 , 113.22 ) , ( 1987 , 114.27 ) , ( 1988 , 113.96 ) , ( 1989 , 116.19 ) , ( 1990 , 118.01 ) , ( 1991 , 118.28 ) , ( 1992 , 118.7 ) , ( 1993 , 118.47 ) , ( 1994 , 119.13 ) , ( 1995 , 120.77 ) , ( 1996 , 121.39 ) , ( 1997 , 119.55 ) , ( 1998 , 121.15 ) , ( 1999 , 122.39 ) , ( 2000 , 123.24 ) , ( 2001 , 123.26 ) , ( 2002 , 123.81 ) , ( 2003 , 125.68 ) , ( 2004 , 127.45 ) , ( 2005 , 129.96 ) , ( 2006 , 129.68 ) , ( 2007 , 130.8 ) , ( 2008 , 131.85 ) , ( 2009 , 131.79 ) , ( 2010 , 132.8 ) , ( 2011 , 133.76 ) , ( 2012 , 134.76 ) , ( 2013 , 134.71 ) , ( 2014 , 134.67 ) , ( 2015 , 136.1 ) , ( 2016 , 137.82 ) , ( 2017 , 138.66 ) , ( 2018 , 138.61 ) , ( 2019 , 138.92 ) ) )
    tabidx = ftab_in_d_table[  "Global_CH4_emi_from_agriculture_H_PRIMAP"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_CH4_emi_from_agriculture_H_PRIMAP"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Global_CH4_emi_from_energy_H = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 79.25 ) , ( 1981 , 75.14 ) , ( 1982 , 75.3 ) , ( 1983 , 75.03 ) , ( 1984 , 76.88 ) , ( 1985 , 78.89 ) , ( 1986 , 81.08 ) , ( 1987 , 82.63 ) , ( 1988 , 86.32 ) , ( 1989 , 89.9 ) , ( 1990 , 89.34 ) , ( 1991 , 86.86 ) , ( 1992 , 86.44 ) , ( 1993 , 87.45 ) , ( 1994 , 86.78 ) , ( 1995 , 88.98 ) , ( 1996 , 92 ) , ( 1997 , 93.01 ) , ( 1998 , 90.97 ) , ( 1999 , 91.15 ) , ( 2000 , 94.95 ) , ( 2001 , 94.68 ) , ( 2002 , 92.3 ) , ( 2003 , 98.36 ) , ( 2004 , 100.52 ) , ( 2005 , 102.45 ) , ( 2006 , 104.85 ) , ( 2007 , 104.78 ) , ( 2008 , 106.24 ) , ( 2009 , 104 ) , ( 2010 , 107.63 ) , ( 2011 , 110.94 ) , ( 2012 , 109.89 ) , ( 2013 , 107.78 ) , ( 2014 , 106.32 ) , ( 2015 , 105.98 ) , ( 2016 , 105.45 ) , ( 2017 , 105.79 ) , ( 2018 , 106.45 ) , ( 2019 , 109.3 ) ) )
    tabidx = ftab_in_d_table["Global_CH4_emi_from_energy_H"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_CH4_emi_from_energy_H"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Global_CH4_emi_from_waste_H = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 37.07 ) , ( 1981 , 37.56 ) , ( 1982 , 38.1 ) , ( 1983 , 38.68 ) , ( 1984 , 39.36 ) , ( 1985 , 40.01 ) , ( 1986 , 40.64 ) , ( 1987 , 41.36 ) , ( 1988 , 42.05 ) , ( 1989 , 42.71 ) , ( 1990 , 43.31 ) , ( 1991 , 44.28 ) , ( 1992 , 44.95 ) , ( 1993 , 45.65 ) , ( 1994 , 46.34 ) , ( 1995 , 47.15 ) , ( 1996 , 47.81 ) , ( 1997 , 48.28 ) , ( 1998 , 48.61 ) , ( 1999 , 49.14 ) , ( 2000 , 49.93 ) , ( 2001 , 50.19 ) , ( 2002 , 50.41 ) , ( 2003 , 50.78 ) , ( 2004 , 50.99 ) , ( 2005 , 51.25 ) , ( 2006 , 52 ) , ( 2007 , 52.55 ) , ( 2008 , 53.07 ) , ( 2009 , 53.63 ) , ( 2010 , 54.35 ) , ( 2011 , 55.53 ) , ( 2012 , 56.71 ) , ( 2013 , 57.73 ) , ( 2014 , 58.93 ) , ( 2015 , 59.82 ) , ( 2016 , 60.41 ) , ( 2017 , 61.54 ) , ( 2018 , 62.56 ) , ( 2019 , 63.93 ) ) )
    tabidx = ftab_in_d_table["Global_CH4_emi_from_waste_H"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_CH4_emi_from_waste_H"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Global_CH4_emissions_H = Global_CH4_emi_from_agriculture_H_PRIMAP + Global_CH4_emi_from_energy_H + Global_CH4_emi_from_waste_H
    idxlhs = fcol_in_mdf["Global_CH4_emissions_H"]
    idx1 = fcol_in_mdf["Global_CH4_emi_from_agriculture_H_PRIMAP"]
    idx2 = fcol_in_mdf["Global_CH4_emi_from_energy_H"]
    idx3 = fcol_in_mdf["Global_CH4_emi_from_waste_H"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Global_CO2_emi_from_IPC1_use_H_PRIMAP = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 18.41 ) , ( 1981 , 17.89 ) , ( 1982 , 17.8 ) , ( 1983 , 17.93 ) , ( 1984 , 18.47 ) , ( 1985 , 19.08 ) , ( 1986 , 19.33 ) , ( 1987 , 19.78 ) , ( 1988 , 20.54 ) , ( 1989 , 20.85 ) , ( 1990 , 20.5 ) , ( 1991 , 20.99 ) , ( 1992 , 20.3 ) , ( 1993 , 20.46 ) , ( 1994 , 20.63 ) , ( 1995 , 21.08 ) , ( 1996 , 21.77 ) , ( 1997 , 21.87 ) , ( 1998 , 21.81 ) , ( 1999 , 22.03 ) , ( 2000 , 22.64 ) , ( 2001 , 22.82 ) , ( 2002 , 23.32 ) , ( 2003 , 24.51 ) , ( 2004 , 25.48 ) , ( 2005 , 26.37 ) , ( 2006 , 27.14 ) , ( 2007 , 27.92 ) , ( 2008 , 28.47 ) , ( 2009 , 28.1 ) , ( 2010 , 29.49 ) , ( 2011 , 30.47 ) , ( 2012 , 31.02 ) , ( 2013 , 31.25 ) , ( 2014 , 31.62 ) , ( 2015 , 31.63 ) , ( 2016 , 31.47 ) , ( 2017 , 31.86 ) , ( 2018 , 32.4 ) , ( 2019 , 32.4 ) ) )
    tabidx = ftab_in_d_table[  "Global_CO2_emi_from_IPC1_use_H_PRIMAP"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_CO2_emi_from_IPC1_use_H_PRIMAP"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Global_CO2_emi_from_IPC2_use = SUM ( CO2_emi_from_IPC2_use[region!] )
    idxlhs = fcol_in_mdf["Global_CO2_emi_from_IPC2_use"]
    idx1 = fcol_in_mdf["CO2_emi_from_IPC2_use"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_CO2_emi_from_IPC2_use_H_PRIMAP = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.68 ) , ( 1981 , 1.66 ) , ( 1982 , 1.47 ) , ( 1983 , 1.48 ) , ( 1984 , 1.6 ) , ( 1985 , 1.59 ) , ( 1986 , 1.6 ) , ( 1987 , 1.64 ) , ( 1988 , 1.73 ) , ( 1989 , 1.73 ) , ( 1990 , 1.7 ) , ( 1991 , 1.7 ) , ( 1992 , 1.7 ) , ( 1993 , 1.71 ) , ( 1994 , 1.76 ) , ( 1995 , 1.83 ) , ( 1996 , 1.82 ) , ( 1997 , 1.87 ) , ( 1998 , 1.87 ) , ( 1999 , 1.89 ) , ( 2000 , 1.96 ) , ( 2001 , 1.98 ) , ( 2002 , 2.04 ) , ( 2003 , 2.16 ) , ( 2004 , 2.3 ) , ( 2005 , 2.37 ) , ( 2006 , 2.54 ) , ( 2007 , 2.67 ) , ( 2008 , 2.67 ) , ( 2009 , 2.6 ) , ( 2010 , 2.82 ) , ( 2011 , 2.96 ) , ( 2012 , 3 ) , ( 2013 , 3.11 ) , ( 2014 , 3.23 ) , ( 2015 , 3.15 ) , ( 2016 , 3.18 ) , ( 2017 , 3.23 ) , ( 2018 , 3.36 ) , ( 2019 , 3.46 ) ) )
    tabidx = ftab_in_d_table[  "Global_CO2_emi_from_IPC2_use_H_PRIMAP"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_CO2_emi_from_IPC2_use_H_PRIMAP"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Net_growth_in_forest_area[region] = ( Forest_land[region] - Forest_area_last_year[region] ) / One_year
    idxlhs = fcol_in_mdf["Net_growth_in_forest_area"]
    idx1 = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["Forest_area_last_year"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / One_year

    # Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption[region] = SMOOTH3 ( Net_growth_in_forest_area[region] , Time_to_adjust_forest_area_to_CO2_emissions )
    idxin = fcol_in_mdf["Net_growth_in_forest_area"]
    idx2 = fcol_in_mdf["Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption_2"
    ]
    idx1 = fcol_in_mdf["Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption_1"
    ]
    idxout = fcol_in_mdf["Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption"
    ]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_to_adjust_forest_area_to_CO2_emissions / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_to_adjust_forest_area_to_CO2_emissions / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_to_adjust_forest_area_to_CO2_emissions / 3)
        * dt
      )

    # LULUC_emissions[region] = LULUC_emissions_a[region] * Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption[region] + LULUC_emissions_b[region]
    idxlhs = fcol_in_mdf["LULUC_emissions"]
    idx1 = fcol_in_mdf["Net_growth_in_forest_area_causing_CO2_emissions_resp_absorption"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (LULUC_emissions_a[j] * mdf[rowi, idx1 + j] + LULUC_emissions_b[j]
      )

    # Global_LULUC_emissions = SUM ( LULUC_emissions[region!] )
    idxlhs = fcol_in_mdf["Global_LULUC_emissions"]
    idx1 = fcol_in_mdf["LULUC_emissions"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_CO2_emissions = Global_CO2_from_fossil_fuels_to_atm + Global_CO2_emi_from_IPC2_use + Global_LULUC_emissions
    idxlhs = fcol_in_mdf["Global_CO2_emissions"]
    idx1 = fcol_in_mdf["Global_CO2_from_fossil_fuels_to_atm"]
    idx2 = fcol_in_mdf["Global_CO2_emi_from_IPC2_use"]
    idx3 = fcol_in_mdf["Global_LULUC_emissions"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Global_LULUC_emissions_H = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.71 ) , ( 1981 , - 4.67 ) , ( 1982 , - 0.72 ) , ( 1983 , 1.42 ) , ( 1984 , - 5.17 ) , ( 1985 , - 1.94 ) , ( 1986 , - 0.75 ) , ( 1987 , 4.39 ) , ( 1988 , - 4.78 ) , ( 1989 , - 6.21 ) , ( 1990 , - 0.26 ) , ( 1991 , - 1.48 ) , ( 1992 , - 1.24 ) , ( 1993 , - 2.73 ) , ( 1994 , - 1.25 ) , ( 1995 , - 4.16 ) , ( 1996 , - 7.21 ) , ( 1997 , - 5.45 ) , ( 1998 , - 4.12 ) , ( 1999 , - 10.02 ) , ( 2000 , - 11.55 ) , ( 2001 , - 3.5 ) , ( 2002 , - 0.81 ) , ( 2003 , - 2.63 ) , ( 2004 , - 4.69 ) , ( 2005 , - 1.16 ) , ( 2006 , - 7.54 ) , ( 2007 , - 7.62 ) , ( 2008 , - 10.51 ) , ( 2009 , - 4.37 ) , ( 2010 , - 10.68 ) , ( 2011 , - 11.28 ) , ( 2012 , - 5.02 ) , ( 2013 , - 6.22 ) , ( 2014 , - 4.11 ) , ( 2015 , - 0.33 ) , ( 2016 , - 4.43 ) , ( 2017 , - 5.77 ) , ( 2018 , - 6.67 ) ) )
    tabidx = ftab_in_d_table["Global_LULUC_emissions_H"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_LULUC_emissions_H"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Global_CO2_emissions_H = Global_CO2_emi_from_IPC1_use_H_PRIMAP + Global_CO2_emi_from_IPC2_use_H_PRIMAP + Global_LULUC_emissions_H
    idxlhs = fcol_in_mdf["Global_CO2_emissions_H"]
    idx1 = fcol_in_mdf["Global_CO2_emi_from_IPC1_use_H_PRIMAP"]
    idx2 = fcol_in_mdf["Global_CO2_emi_from_IPC2_use_H_PRIMAP"]
    idx3 = fcol_in_mdf["Global_LULUC_emissions_H"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # GLobal_GDP_in_terraUSD = GLobal_GDP * UNIT_conv_to_TUSD
    idxlhs = fcol_in_mdf["GLobal_GDP_in_terraUSD"]
    idx1 = fcol_in_mdf["GLobal_GDP"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conv_to_TUSD

    # Regional_population_as_fraction_of_total_hist[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0525066 ) , ( 1981 , 0.0520854 ) , ( 1982 , 0.0516664 ) , ( 1983 , 0.0512454 ) , ( 1984 , 0.0508179 ) , ( 1985 , 0.0503829 ) , ( 1986 , 0.0499397 ) , ( 1987 , 0.0494946 ) , ( 1988 , 0.049062 ) , ( 1989 , 0.0486594 ) , ( 1990 , 0.0482986 ) , ( 1991 , 0.0479783 ) , ( 1992 , 0.0476952 ) , ( 1993 , 0.0474536 ) , ( 1994 , 0.0472591 ) , ( 1995 , 0.0471124 ) , ( 1996 , 0.0470165 ) , ( 1997 , 0.0469638 ) , ( 1998 , 0.0469296 ) , ( 1999 , 0.0468833 ) , ( 2000 , 0.0468038 ) , ( 2001 , 0.0466826 ) , ( 2002 , 0.046527 ) , ( 2003 , 0.0463513 ) , ( 2004 , 0.0461761 ) , ( 2005 , 0.0460159 ) , ( 2006 , 0.0458736 ) , ( 2007 , 0.045742 ) , ( 2008 , 0.0456134 ) , ( 2009 , 0.0454756 ) , ( 2010 , 0.0453203 ) , ( 2011 , 0.0451475 ) , ( 2012 , 0.0449605 ) , ( 2013 , 0.0447612 ) , ( 2014 , 0.0445527 ) , ( 2015 , 0.044338 ) , ( 2016 , 0.0441171 ) , ( 2017 , 0.0438914 ) , ( 2018 , 0.0436659 ) , ( 2019 , 0.0434473 ) , ( 2020 , 0.0432399 ) ) ) Regional_population_as_fraction_of_total_hist[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0819172 ) , ( 1981 , 0.0827883 ) , ( 1982 , 0.0836937 ) , ( 1983 , 0.0846219 ) , ( 1984 , 0.0855565 ) , ( 1985 , 0.0864879 ) , ( 1986 , 0.0874107 ) , ( 1987 , 0.0883292 ) , ( 1988 , 0.0892647 ) , ( 1989 , 0.0902449 ) , ( 1990 , 0.0912861 ) , ( 1991 , 0.0923989 ) , ( 1992 , 0.0935728 ) , ( 1993 , 0.0947917 ) , ( 1994 , 0.0960295 ) , ( 1995 , 0.0972692 ) , ( 1996 , 0.0985085 ) , ( 1997 , 0.0997543 ) , ( 1998 , 0.101019 ) , ( 1999 , 0.102315 ) , ( 2000 , 0.103652 ) , ( 2001 , 0.105032 ) , ( 2002 , 0.106453 ) , ( 2003 , 0.10792 ) , ( 2004 , 0.109433 ) , ( 2005 , 0.110993 ) , ( 2006 , 0.112599 ) , ( 2007 , 0.114255 ) , ( 2008 , 0.115959 ) , ( 2009 , 0.117712 ) , ( 2010 , 0.119515 ) , ( 2011 , 0.121367 ) , ( 2012 , 0.123265 ) , ( 2013 , 0.125208 ) , ( 2014 , 0.127192 ) , ( 2015 , 0.129214 ) , ( 2016 , 0.131275 ) , ( 2017 , 0.133373 ) , ( 2018 , 0.135502 ) , ( 2019 , 0.137659 ) , ( 2020 , 0.139838 ) ) ) Regional_population_as_fraction_of_total_hist[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.230985 ) , ( 1981 , 0.230163 ) , ( 1982 , 0.22929 ) , ( 1983 , 0.228471 ) , ( 1984 , 0.227835 ) , ( 1985 , 0.227453 ) , ( 1986 , 0.227366 ) , ( 1987 , 0.227509 ) , ( 1988 , 0.227709 ) , ( 1989 , 0.227745 ) , ( 1990 , 0.227472 ) , ( 1991 , 0.226847 ) , ( 1992 , 0.225934 ) , ( 1993 , 0.224817 ) , ( 1994 , 0.22362 ) , ( 1995 , 0.222429 ) , ( 1996 , 0.221259 ) , ( 1997 , 0.220086 ) , ( 1998 , 0.2189 ) , ( 1999 , 0.217679 ) , ( 2000 , 0.216414 ) , ( 2001 , 0.215106 ) , ( 2002 , 0.213772 ) , ( 2003 , 0.212418 ) , ( 2004 , 0.211051 ) , ( 2005 , 0.209679 ) , ( 2006 , 0.208304 ) , ( 2007 , 0.206931 ) , ( 2008 , 0.205566 ) , ( 2009 , 0.204222 ) , ( 2010 , 0.202904 ) , ( 2011 , 0.201613 ) , ( 2012 , 0.200347 ) , ( 2013 , 0.199103 ) , ( 2014 , 0.197873 ) , ( 2015 , 0.196653 ) , ( 2016 , 0.195441 ) , ( 2017 , 0.194236 ) , ( 2018 , 0.193027 ) , ( 2019 , 0.191802 ) , ( 2020 , 0.190552 ) ) ) Regional_population_as_fraction_of_total_hist[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0413879 ) , ( 1981 , 0.0420248 ) , ( 1982 , 0.0426981 ) , ( 1983 , 0.0433867 ) , ( 1984 , 0.0440657 ) , ( 1985 , 0.0447153 ) , ( 1986 , 0.0453284 ) , ( 1987 , 0.0459083 ) , ( 1988 , 0.0464516 ) , ( 1989 , 0.0469621 ) , ( 1990 , 0.047442 ) , ( 1991 , 0.0478925 ) , ( 1992 , 0.0483151 ) , ( 1993 , 0.0487096 ) , ( 1994 , 0.0490767 ) , ( 1995 , 0.0494193 ) , ( 1996 , 0.0497389 ) , ( 1997 , 0.0500402 ) , ( 1998 , 0.0503324 ) , ( 1999 , 0.0506257 ) , ( 2000 , 0.0509276 ) , ( 2001 , 0.0512398 ) , ( 2002 , 0.0515632 ) , ( 2003 , 0.0519077 ) , ( 2004 , 0.0522839 ) , ( 2005 , 0.052699 ) , ( 2006 , 0.0531555 ) , ( 2007 , 0.0536464 ) , ( 2008 , 0.0541575 ) , ( 2009 , 0.0546675 ) , ( 2010 , 0.0551629 ) , ( 2011 , 0.0556404 ) , ( 2012 , 0.0561025 ) , ( 2013 , 0.0565471 ) , ( 2014 , 0.0569748 ) , ( 2015 , 0.0573861 ) , ( 2016 , 0.0577769 ) , ( 2017 , 0.0581493 ) , ( 2018 , 0.0585139 ) , ( 2019 , 0.0588861 ) , ( 2020 , 0.0592743 ) ) ) Regional_population_as_fraction_of_total_hist[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.200317 ) , ( 1981 , 0.201682 ) , ( 1982 , 0.203062 ) , ( 1983 , 0.204418 ) , ( 1984 , 0.205705 ) , ( 1985 , 0.206896 ) , ( 1986 , 0.207975 ) , ( 1987 , 0.208962 ) , ( 1988 , 0.209905 ) , ( 1989 , 0.210871 ) , ( 1990 , 0.211905 ) , ( 1991 , 0.213015 ) , ( 1992 , 0.214185 ) , ( 1993 , 0.215413 ) , ( 1994 , 0.216688 ) , ( 1995 , 0.217999 ) , ( 1996 , 0.219343 ) , ( 1997 , 0.220715 ) , ( 1998 , 0.222087 ) , ( 1999 , 0.223428 ) , ( 2000 , 0.224715 ) , ( 2001 , 0.225936 ) , ( 2002 , 0.22709 ) , ( 2003 , 0.22817 ) , ( 2004 , 0.229172 ) , ( 2005 , 0.230092 ) , ( 2006 , 0.23093 ) , ( 2007 , 0.231685 ) , ( 2008 , 0.232347 ) , ( 2009 , 0.232909 ) , ( 2010 , 0.233365 ) , ( 2011 , 0.233716 ) , ( 2012 , 0.233974 ) , ( 2013 , 0.234166 ) , ( 2014 , 0.234331 ) , ( 2015 , 0.234494 ) , ( 2016 , 0.234664 ) , ( 2017 , 0.234837 ) , ( 2018 , 0.235017 ) , ( 2019 , 0.2352 ) , ( 2020 , 0.235384 ) ) ) Regional_population_as_fraction_of_total_hist[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0805174 ) , ( 1981 , 0.0808909 ) , ( 1982 , 0.0812472 ) , ( 1983 , 0.0815746 ) , ( 1984 , 0.0818569 ) , ( 1985 , 0.0820873 ) , ( 1986 , 0.0822603 ) , ( 1987 , 0.0823858 ) , ( 1988 , 0.0824875 ) , ( 1989 , 0.0825949 ) , ( 1990 , 0.0827308 ) , ( 1991 , 0.0828983 ) , ( 1992 , 0.0830915 ) , ( 1993 , 0.0833012 ) , ( 1994 , 0.0835174 ) , ( 1995 , 0.08373 ) , ( 1996 , 0.083939 ) , ( 1997 , 0.084144 ) , ( 1998 , 0.0843381 ) , ( 1999 , 0.0845128 ) , ( 2000 , 0.0846633 ) , ( 2001 , 0.084787 ) , ( 2002 , 0.0848845 ) , ( 2003 , 0.0849569 ) , ( 2004 , 0.0850064 ) , ( 2005 , 0.085035 ) , ( 2006 , 0.0850422 ) , ( 2007 , 0.0850297 ) , ( 2008 , 0.0850001 ) , ( 2009 , 0.0849597 ) , ( 2010 , 0.0849092 ) , ( 2011 , 0.0848529 ) , ( 2012 , 0.0847901 ) , ( 2013 , 0.0847197 ) , ( 2014 , 0.0846417 ) , ( 2015 , 0.0845547 ) , ( 2016 , 0.0844588 ) , ( 2017 , 0.0843559 ) , ( 2018 , 0.0842489 ) , ( 2019 , 0.0841415 ) , ( 2020 , 0.0840364 ) ) ) Regional_population_as_fraction_of_total_hist[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0486504 ) , ( 1981 , 0.0482934 ) , ( 1982 , 0.0479349 ) , ( 1983 , 0.0475661 ) , ( 1984 , 0.0471766 ) , ( 1985 , 0.0467614 ) , ( 1986 , 0.0463189 ) , ( 1987 , 0.0458572 ) , ( 1988 , 0.0453935 ) , ( 1989 , 0.0449487 ) , ( 1990 , 0.0445358 ) , ( 1991 , 0.0441586 ) , ( 1992 , 0.0438104 ) , ( 1993 , 0.0434824 ) , ( 1994 , 0.0431616 ) , ( 1995 , 0.0428382 ) , ( 1996 , 0.0425109 ) , ( 1997 , 0.0421826 ) , ( 1998 , 0.0418547 ) , ( 1999 , 0.0415297 ) , ( 2000 , 0.0412096 ) , ( 2001 , 0.0408947 ) , ( 2002 , 0.040583 ) , ( 2003 , 0.0402744 ) , ( 2004 , 0.0399685 ) , ( 2005 , 0.0396647 ) , ( 2006 , 0.0393627 ) , ( 2007 , 0.0390622 ) , ( 2008 , 0.0387638 ) , ( 2009 , 0.038468 ) , ( 2010 , 0.0381754 ) , ( 2011 , 0.0378856 ) , ( 2012 , 0.0375986 ) , ( 2013 , 0.0373113 ) , ( 2014 , 0.0370199 ) , ( 2015 , 0.0367226 ) , ( 2016 , 0.0364185 ) , ( 2017 , 0.0361091 ) , ( 2018 , 0.0357966 ) , ( 2019 , 0.0354841 ) , ( 2020 , 0.0351743 ) ) ) Regional_population_as_fraction_of_total_hist[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0736851 ) , ( 1981 , 0.0729648 ) , ( 1982 , 0.0722219 ) , ( 1983 , 0.071467 ) , ( 1984 , 0.0707135 ) , ( 1985 , 0.0699724 ) , ( 1986 , 0.069245 ) , ( 1987 , 0.0685265 ) , ( 1988 , 0.0678181 ) , ( 1989 , 0.0671179 ) , ( 1990 , 0.0664223 ) , ( 1991 , 0.0657367 ) , ( 1992 , 0.0650568 ) , ( 1993 , 0.064363 ) , ( 1994 , 0.0636314 ) , ( 1995 , 0.0628475 ) , ( 1996 , 0.0620063 ) , ( 1997 , 0.0611217 ) , ( 1998 , 0.0602247 ) , ( 1999 , 0.0593565 ) , ( 2000 , 0.058546 ) , ( 2001 , 0.0578029 ) , ( 2002 , 0.0571189 ) , ( 2003 , 0.0564842 ) , ( 2004 , 0.0558807 ) , ( 2005 , 0.0552956 ) , ( 2006 , 0.0547266 ) , ( 2007 , 0.0541798 ) , ( 2008 , 0.0536651 ) , ( 2009 , 0.0531966 ) , ( 2010 , 0.0527824 ) , ( 2011 , 0.0524254 ) , ( 2012 , 0.0521157 ) , ( 2013 , 0.0518375 ) , ( 2014 , 0.0515692 ) , ( 2015 , 0.0512955 ) , ( 2016 , 0.0510114 ) , ( 2017 , 0.0507203 ) , ( 2018 , 0.0504225 ) , ( 2019 , 0.0501221 ) , ( 2020 , 0.0498219 ) ) ) Regional_population_as_fraction_of_total_hist[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.1094 ) , ( 1981 , 0.108038 ) , ( 1982 , 0.106667 ) , ( 1983 , 0.10529 ) , ( 1984 , 0.103908 ) , ( 1985 , 0.102526 ) , ( 1986 , 0.101142 ) , ( 1987 , 0.099766 ) , ( 1988 , 0.0984307 ) , ( 1989 , 0.0971721 ) , ( 1990 , 0.0960105 ) , ( 1991 , 0.0949569 ) , ( 1992 , 0.0939958 ) , ( 1993 , 0.0930973 ) , ( 1994 , 0.0922191 ) , ( 1995 , 0.0913368 ) , ( 1996 , 0.0904396 ) , ( 1997 , 0.0895391 ) , ( 1998 , 0.0886591 ) , ( 1999 , 0.0878342 ) , ( 2000 , 0.0870852 ) , ( 2001 , 0.0864168 ) , ( 2002 , 0.0858157 ) , ( 2003 , 0.0852604 ) , ( 2004 , 0.0847241 ) , ( 2005 , 0.0841861 ) , ( 2006 , 0.083642 ) , ( 2007 , 0.0830959 ) , ( 2008 , 0.0825474 ) , ( 2009 , 0.0819995 ) , ( 2010 , 0.0814537 ) , ( 2011 , 0.080906 ) , ( 2012 , 0.0803554 ) , ( 2013 , 0.0798082 ) , ( 2014 , 0.0792715 ) , ( 2015 , 0.0787511 ) , ( 2016 , 0.0782506 ) , ( 2017 , 0.0777639 ) , ( 2018 , 0.077278 ) , ( 2019 , 0.0767714 ) , ( 2020 , 0.076233 ) ) ) Regional_population_as_fraction_of_total_hist[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.0806328 ) , ( 1981 , 0.0810695 ) , ( 1982 , 0.0815188 ) , ( 1983 , 0.0819591 ) , ( 1984 , 0.0823646 ) , ( 1985 , 0.0827183 ) , ( 1986 , 0.0830137 ) , ( 1987 , 0.083262 ) , ( 1988 , 0.0834777 ) , ( 1989 , 0.0836841 ) , ( 1990 , 0.083897 ) , ( 1991 , 0.0841183 ) , ( 1992 , 0.0843436 ) , ( 1993 , 0.0845711 ) , ( 1994 , 0.0847973 ) , ( 1995 , 0.0850194 ) , ( 1996 , 0.0852385 ) , ( 1997 , 0.0854534 ) , ( 1998 , 0.0856562 ) , ( 1999 , 0.0858352 ) , ( 2000 , 0.0859846 ) , ( 2001 , 0.086102 ) , ( 2002 , 0.0861917 ) , ( 2003 , 0.0862575 ) , ( 2004 , 0.0863053 ) , ( 2005 , 0.0863407 ) , ( 2006 , 0.0863636 ) , ( 2007 , 0.0863738 ) , ( 2008 , 0.08638 ) , ( 2009 , 0.0863907 ) , ( 2010 , 0.0864116 ) , ( 2011 , 0.0864464 ) , ( 2012 , 0.0864915 ) , ( 2013 , 0.0865381 ) , ( 2014 , 0.0865743 ) , ( 2015 , 0.0865909 ) , ( 2016 , 0.0865863 ) , ( 2017 , 0.0865637 ) , ( 2018 , 0.0865282 ) , ( 2019 , 0.0864875 ) , ( 2020 , 0.0864466 ) ) )
    tabidx = ftab_in_d_table[  "Regional_population_as_fraction_of_total_hist"]  # fetch the correct table
    idx2 = fcol_in_mdf["Regional_population_as_fraction_of_total_hist"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # Govt_debt_paid_back_to_private_lenders[region] = Govt_debt_repayment_obligation[region] * Fraction_of_govt_loan_obligations_to_PL_met[region]
    idxlhs = fcol_in_mdf["Govt_debt_paid_back_to_private_lenders"]
    idx1 = fcol_in_mdf["Govt_debt_repayment_obligation"]
    idx2 = fcol_in_mdf["Fraction_of_govt_loan_obligations_to_PL_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # N2O_emi_from_agri_hist_table[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1.15 ) , ( 1981 , 1.17 ) , ( 1982 , 1.11 ) , ( 1983 , 1.09 ) , ( 1984 , 1.16 ) , ( 1985 , 1.13 ) , ( 1986 , 1.09 ) , ( 1987 , 1.07 ) , ( 1988 , 1.04 ) , ( 1989 , 1.08 ) , ( 1990 , 1.11 ) , ( 1991 , 1.07 ) , ( 1992 , 1.06 ) , ( 1993 , 1.14 ) , ( 1994 , 1.08 ) , ( 1995 , 1.1 ) , ( 1996 , 1.13 ) , ( 1997 , 1.1 ) , ( 1998 , 1.12 ) , ( 1999 , 1.09 ) , ( 2000 , 1.04 ) , ( 2001 , 1.12 ) , ( 2002 , 1.11 ) , ( 2003 , 1.12 ) , ( 2004 , 1.16 ) , ( 2005 , 1.11 ) , ( 2006 , 1.09 ) , ( 2007 , 1.13 ) , ( 2008 , 1.12 ) , ( 2009 , 1.13 ) , ( 2010 , 1.15 ) , ( 2011 , 1.11 ) , ( 2012 , 1.04 ) , ( 2013 , 1.2 ) , ( 2014 , 1.23 ) , ( 2015 , 1.23 ) , ( 2016 , 1.17 ) , ( 2017 , 1.16 ) , ( 2018 , 1.2 ) , ( 2019 , 1.22 ) ) ) N2O_emi_from_agri_hist_table[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.59 ) , ( 1981 , 0.55 ) , ( 1982 , 0.59 ) , ( 1983 , 0.58 ) , ( 1984 , 0.53 ) , ( 1985 , 0.53 ) , ( 1986 , 0.53 ) , ( 1987 , 0.59 ) , ( 1988 , 0.53 ) , ( 1989 , 0.57 ) , ( 1990 , 0.68 ) , ( 1991 , 0.69 ) , ( 1992 , 0.7 ) , ( 1993 , 0.7 ) , ( 1994 , 0.72 ) , ( 1995 , 0.74 ) , ( 1996 , 0.78 ) , ( 1997 , 0.82 ) , ( 1998 , 0.88 ) , ( 1999 , 0.91 ) , ( 2000 , 0.91 ) , ( 2001 , 0.9 ) , ( 2002 , 0.91 ) , ( 2003 , 0.91 ) , ( 2004 , 0.92 ) , ( 2005 , 0.94 ) , ( 2006 , 0.92 ) , ( 2007 , 0.97 ) , ( 2008 , 1.02 ) , ( 2009 , 0.99 ) , ( 2010 , 1.06 ) , ( 2011 , 1.06 ) , ( 2012 , 1.08 ) , ( 2013 , 1.09 ) , ( 2014 , 1.1 ) , ( 2015 , 1.11 ) , ( 2016 , 1.16 ) , ( 2017 , 1.17 ) , ( 2018 , 1.17 ) , ( 2019 , 1.18 ) ) ) N2O_emi_from_agri_hist_table[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.53 ) , ( 1981 , 0.52 ) , ( 1982 , 0.54 ) , ( 1983 , 0.58 ) , ( 1984 , 0.61 ) , ( 1985 , 0.58 ) , ( 1986 , 0.59 ) , ( 1987 , 0.67 ) , ( 1988 , 0.71 ) , ( 1989 , 0.73 ) , ( 1990 , 0.76 ) , ( 1991 , 0.78 ) , ( 1992 , 0.79 ) , ( 1993 , 0.76 ) , ( 1994 , 0.79 ) , ( 1995 , 0.92 ) , ( 1996 , 0.99 ) , ( 1997 , 0.91 ) , ( 1998 , 0.93 ) , ( 1999 , 0.98 ) , ( 2000 , 0.95 ) , ( 2001 , 0.96 ) , ( 2002 , 1.01 ) , ( 2003 , 1.02 ) , ( 2004 , 1.05 ) , ( 2005 , 1.07 ) , ( 2006 , 1.09 ) , ( 2007 , 1.1 ) , ( 2008 , 1.12 ) , ( 2009 , 1.15 ) , ( 2010 , 1.16 ) , ( 2011 , 1.31 ) , ( 2012 , 1.48 ) , ( 2013 , 1.32 ) , ( 2014 , 1.17 ) , ( 2015 , 1.18 ) , ( 2016 , 1.18 ) , ( 2017 , 1.15 ) , ( 2018 , 1.13 ) , ( 2019 , 1.12 ) ) ) N2O_emi_from_agri_hist_table[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.13 ) , ( 1981 , 0.14 ) , ( 1982 , 0.14 ) , ( 1983 , 0.15 ) , ( 1984 , 0.16 ) , ( 1985 , 0.17 ) , ( 1986 , 0.18 ) , ( 1987 , 0.18 ) , ( 1988 , 0.18 ) , ( 1989 , 0.19 ) , ( 1990 , 0.2 ) , ( 1991 , 0.2 ) , ( 1992 , 0.21 ) , ( 1993 , 0.21 ) , ( 1994 , 0.21 ) , ( 1995 , 0.21 ) , ( 1996 , 0.22 ) , ( 1997 , 0.22 ) , ( 1998 , 0.23 ) , ( 1999 , 0.23 ) , ( 2000 , 0.23 ) , ( 2001 , 0.24 ) , ( 2002 , 0.25 ) , ( 2003 , 0.25 ) , ( 2004 , 0.27 ) , ( 2005 , 0.28 ) , ( 2006 , 0.28 ) , ( 2007 , 0.28 ) , ( 2008 , 0.27 ) , ( 2009 , 0.26 ) , ( 2010 , 0.26 ) , ( 2011 , 0.26 ) , ( 2012 , 0.27 ) , ( 2013 , 0.27 ) , ( 2014 , 0.26 ) , ( 2015 , 0.26 ) , ( 2016 , 0.27 ) , ( 2017 , 0.27 ) , ( 2018 , 0.27 ) , ( 2019 , 0.28 ) ) ) N2O_emi_from_agri_hist_table[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.18 ) , ( 1981 , 0.19 ) , ( 1982 , 0.19 ) , ( 1983 , 0.2 ) , ( 1984 , 0.21 ) , ( 1985 , 0.22 ) , ( 1986 , 0.23 ) , ( 1987 , 0.23 ) , ( 1988 , 0.24 ) , ( 1989 , 0.25 ) , ( 1990 , 0.25 ) , ( 1991 , 0.26 ) , ( 1992 , 0.27 ) , ( 1993 , 0.27 ) , ( 1994 , 0.28 ) , ( 1995 , 0.3 ) , ( 1996 , 0.31 ) , ( 1997 , 0.32 ) , ( 1998 , 0.33 ) , ( 1999 , 0.35 ) , ( 2000 , 0.35 ) , ( 2001 , 0.36 ) , ( 2002 , 0.36 ) , ( 2003 , 0.37 ) , ( 2004 , 0.38 ) , ( 2005 , 0.4 ) , ( 2006 , 0.42 ) , ( 2007 , 0.43 ) , ( 2008 , 0.45 ) , ( 2009 , 0.47 ) , ( 2010 , 0.48 ) , ( 2011 , 0.5 ) , ( 2012 , 0.5 ) , ( 2013 , 0.52 ) , ( 2014 , 0.54 ) , ( 2015 , 0.56 ) , ( 2016 , 0.57 ) , ( 2017 , 0.59 ) , ( 2018 , 0.6 ) , ( 2019 , 0.6 ) ) ) N2O_emi_from_agri_hist_table[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.74 ) , ( 1981 , 0.74 ) , ( 1982 , 0.74 ) , ( 1983 , 0.74 ) , ( 1984 , 0.75 ) , ( 1985 , 0.76 ) , ( 1986 , 0.78 ) , ( 1987 , 0.81 ) , ( 1988 , 0.8 ) , ( 1989 , 0.81 ) , ( 1990 , 0.82 ) , ( 1991 , 0.82 ) , ( 1992 , 0.83 ) , ( 1993 , 0.84 ) , ( 1994 , 0.85 ) , ( 1995 , 0.86 ) , ( 1996 , 0.84 ) , ( 1997 , 0.85 ) , ( 1998 , 0.87 ) , ( 1999 , 0.87 ) , ( 2000 , 0.89 ) , ( 2001 , 0.93 ) , ( 2002 , 0.94 ) , ( 2003 , 0.99 ) , ( 2004 , 0.99 ) , ( 2005 , 1.02 ) , ( 2006 , 1.03 ) , ( 2007 , 1.06 ) , ( 2008 , 1.05 ) , ( 2009 , 1.05 ) , ( 2010 , 1.07 ) , ( 2011 , 1.1 ) , ( 2012 , 1.11 ) , ( 2013 , 1.11 ) , ( 2014 , 1.12 ) , ( 2015 , 1.09 ) , ( 2016 , 1.14 ) , ( 2017 , 1.18 ) , ( 2018 , 1.16 ) , ( 2019 , 1.18 ) ) ) N2O_emi_from_agri_hist_table[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.19 ) , ( 1981 , 0.18 ) , ( 1982 , 0.19 ) , ( 1983 , 0.19 ) , ( 1984 , 0.19 ) , ( 1985 , 0.21 ) , ( 1986 , 0.2 ) , ( 1987 , 0.19 ) , ( 1988 , 0.18 ) , ( 1989 , 0.19 ) , ( 1990 , 0.19 ) , ( 1991 , 0.19 ) , ( 1992 , 0.19 ) , ( 1993 , 0.19 ) , ( 1994 , 0.2 ) , ( 1995 , 0.2 ) , ( 1996 , 0.2 ) , ( 1997 , 0.21 ) , ( 1998 , 0.21 ) , ( 1999 , 0.21 ) , ( 2000 , 0.21 ) , ( 2001 , 0.2 ) , ( 2002 , 0.2 ) , ( 2003 , 0.2 ) , ( 2004 , 0.21 ) , ( 2005 , 0.21 ) , ( 2006 , 0.21 ) , ( 2007 , 0.2 ) , ( 2008 , 0.21 ) , ( 2009 , 0.21 ) , ( 2010 , 0.21 ) , ( 2011 , 0.21 ) , ( 2012 , 0.22 ) , ( 2013 , 0.23 ) , ( 2014 , 0.22 ) , ( 2015 , 0.22 ) , ( 2016 , 0.23 ) , ( 2017 , 0.23 ) , ( 2018 , 0.23 ) , ( 2019 , 0.23 ) ) ) N2O_emi_from_agri_hist_table[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.82 ) , ( 1981 , 0.82 ) , ( 1982 , 0.85 ) , ( 1983 , 0.89 ) , ( 1984 , 0.89 ) , ( 1985 , 0.91 ) , ( 1986 , 0.92 ) , ( 1987 , 0.93 ) , ( 1988 , 0.92 ) , ( 1989 , 0.88 ) , ( 1990 , 0.84 ) , ( 1991 , 0.78 ) , ( 1992 , 0.73 ) , ( 1993 , 0.68 ) , ( 1994 , 0.6 ) , ( 1995 , 0.56 ) , ( 1996 , 0.53 ) , ( 1997 , 0.53 ) , ( 1998 , 0.51 ) , ( 1999 , 0.49 ) , ( 2000 , 0.49 ) , ( 2001 , 0.49 ) , ( 2002 , 0.5 ) , ( 2003 , 0.48 ) , ( 2004 , 0.51 ) , ( 2005 , 0.5 ) , ( 2006 , 0.5 ) , ( 2007 , 0.5 ) , ( 2008 , 0.53 ) , ( 2009 , 0.53 ) , ( 2010 , 0.51 ) , ( 2011 , 0.54 ) , ( 2012 , 0.52 ) , ( 2013 , 0.55 ) , ( 2014 , 0.55 ) , ( 2015 , 0.56 ) , ( 2016 , 0.59 ) , ( 2017 , 0.59 ) , ( 2018 , 0.61 ) , ( 2019 , 0.61 ) ) ) N2O_emi_from_agri_hist_table[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.78 ) , ( 1981 , 0.77 ) , ( 1982 , 0.79 ) , ( 1983 , 0.79 ) , ( 1984 , 0.8 ) , ( 1985 , 0.8 ) , ( 1986 , 0.81 ) , ( 1987 , 0.8 ) , ( 1988 , 0.79 ) , ( 1989 , 0.79 ) , ( 1990 , 0.78 ) , ( 1991 , 0.75 ) , ( 1992 , 0.72 ) , ( 1993 , 0.7 ) , ( 1994 , 0.69 ) , ( 1995 , 0.7 ) , ( 1996 , 0.71 ) , ( 1997 , 0.71 ) , ( 1998 , 0.71 ) , ( 1999 , 0.71 ) , ( 2000 , 0.7 ) , ( 2001 , 0.69 ) , ( 2002 , 0.68 ) , ( 2003 , 0.67 ) , ( 2004 , 0.68 ) , ( 2005 , 0.67 ) , ( 2006 , 0.66 ) , ( 2007 , 0.67 ) , ( 2008 , 0.66 ) , ( 2009 , 0.65 ) , ( 2010 , 0.65 ) , ( 2011 , 0.65 ) , ( 2012 , 0.66 ) , ( 2013 , 0.67 ) , ( 2014 , 0.69 ) , ( 2015 , 0.68 ) , ( 2016 , 0.69 ) , ( 2017 , 0.7 ) , ( 2018 , 0.69 ) , ( 2019 , 0.69 ) ) ) N2O_emi_from_agri_hist_table[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0.18 ) , ( 1981 , 0.18 ) , ( 1982 , 0.19 ) , ( 1983 , 0.2 ) , ( 1984 , 0.2 ) , ( 1985 , 0.2 ) , ( 1986 , 0.21 ) , ( 1987 , 0.22 ) , ( 1988 , 0.22 ) , ( 1989 , 0.22 ) , ( 1990 , 0.23 ) , ( 1991 , 0.23 ) , ( 1992 , 0.24 ) , ( 1993 , 0.25 ) , ( 1994 , 0.25 ) , ( 1995 , 0.26 ) , ( 1996 , 0.27 ) , ( 1997 , 0.27 ) , ( 1998 , 0.27 ) , ( 1999 , 0.27 ) , ( 2000 , 0.27 ) , ( 2001 , 0.27 ) , ( 2002 , 0.28 ) , ( 2003 , 0.29 ) , ( 2004 , 0.3 ) , ( 2005 , 0.31 ) , ( 2006 , 0.31 ) , ( 2007 , 0.32 ) , ( 2008 , 0.33 ) , ( 2009 , 0.34 ) , ( 2010 , 0.35 ) , ( 2011 , 0.35 ) , ( 2012 , 0.36 ) , ( 2013 , 0.36 ) , ( 2014 , 0.36 ) , ( 2015 , 0.35 ) , ( 2016 , 0.37 ) , ( 2017 , 0.39 ) , ( 2018 , 0.39 ) , ( 2019 , 0.39 ) ) )
    tabidx = ftab_in_d_table["N2O_emi_from_agri_hist_table"]  # fetch the correct table
    idx2 = fcol_in_mdf["N2O_emi_from_agri_hist_table"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # Global_N2O_emi_from_agri_H = SUM ( N2O_emi_from_agri_hist_table[region!] )
    idxlhs = fcol_in_mdf["Global_N2O_emi_from_agri_H"]
    idx1 = fcol_in_mdf["N2O_emi_from_agri_hist_table"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # Global_N2O_emi_X_agri_H = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2.42 ) , ( 1981 , 2.37 ) , ( 1982 , 2.28 ) , ( 1983 , 2.3 ) , ( 1984 , 2.32 ) , ( 1985 , 2.29 ) , ( 1986 , 2.26 ) , ( 1987 , 2.27 ) , ( 1988 , 2.25 ) , ( 1989 , 2.24 ) , ( 1990 , 2.12 ) , ( 1991 , 2.11 ) , ( 1992 , 2.14 ) , ( 1993 , 2.13 ) , ( 1994 , 2.17 ) , ( 1995 , 2.25 ) , ( 1996 , 2.33 ) , ( 1997 , 2.36 ) , ( 1998 , 2.3 ) , ( 1999 , 2.22 ) , ( 2000 , 2.29 ) , ( 2001 , 2.27 ) , ( 2002 , 2.3 ) , ( 2003 , 2.37 ) , ( 2004 , 2.5 ) , ( 2005 , 2.54 ) , ( 2006 , 2.56 ) , ( 2007 , 2.59 ) , ( 2008 , 2.52 ) , ( 2009 , 2.49 ) , ( 2010 , 2.52 ) , ( 2011 , 2.52 ) , ( 2012 , 2.47 ) , ( 2013 , 2.59 ) , ( 2014 , 2.7 ) , ( 2015 , 2.67 ) , ( 2016 , 2.7 ) , ( 2017 , 2.73 ) , ( 2018 , 2.77 ) , ( 2019 , 2.81 ) ) )
    tabidx = ftab_in_d_table["Global_N2O_emi_X_agri_H"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Global_N2O_emi_X_agri_H"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Owner_income_from_lending_activity[region] = Worker_cashflow_to_owners[region] + Govt_cashflow_to_owners[region]
    idxlhs = fcol_in_mdf["Owner_income_from_lending_activity"]
    idx1 = fcol_in_mdf["Worker_cashflow_to_owners"]
    idx2 = fcol_in_mdf["Govt_cashflow_to_owners"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Population_below_2p5_kusd_ppy[region] = Population[region] * Fraction_of_population_below_existential_minimum[region]
    idxlhs = fcol_in_mdf["Population_below_2p5_kusd_ppy"]
    idx1 = fcol_in_mdf["Population"]
    idx2 = fcol_in_mdf["Fraction_of_population_below_existential_minimum"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Population_H[region] = Cohort_0_to_20_H[region] + Cohort_20_to_40_H[region] + Cohort_40_to_60_H[region] + Cohort_60plus_H[region]
    #        idxlhs = fcol_in_mdf['Population_H']
    #        idx1 = fcol_in_mdf['Cohort_0_to_20_H']
    #        idx2 = fcol_in_mdf['Cohort_20_to_40_H']
    #        idx3 = fcol_in_mdf['Cohort_40_to_60_H']
    #        idx4 = fcol_in_mdf['Cohort_60plus_H']
    #        for j in range(0, 10):
    #            mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j] + mdf[rowi, idx4 + j]

    # RoC_GHG_intensity[region] = ( GHG_intensity[region] - GHG_intensity_last_year[region] ) / GHG_intensity_last_year[region] / One_year
    idxlhs = fcol_in_mdf["RoC_GHG_intensity"]
    idx1 = fcol_in_mdf["GHG_intensity"]
    idx2 = fcol_in_mdf["GHG_intensity_last_year"]
    idx3 = fcol_in_mdf["GHG_intensity_last_year"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j] / One_year
      )

    # RoC_in_Carbon_intensity[region] = ( Carbon_intensity[region] - Carbon_intensity_last_year[region] ) / Carbon_intensity_last_year[region] / One_year
    idxlhs = fcol_in_mdf["RoC_in_Carbon_intensity"]
    idx1 = fcol_in_mdf["Carbon_intensity"]
    idx2 = fcol_in_mdf["Carbon_intensity_last_year"]
    idx3 = fcol_in_mdf["Carbon_intensity_last_year"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j] / One_year
      )

    # pb_Global_Warming = Temp_surface_anomaly_compared_to_1850_degC
    idxlhs = fcol_in_mdf["pb_Global_Warming"]
    idx1 = fcol_in_mdf["Temp_surface_anomaly_compared_to_1850_degC"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Global_warming_risk_score = IF_THEN_ELSE ( pb_Global_Warming > pb_Global_Warming_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Global_warming_risk_score"]
    idx1 = fcol_in_mdf["pb_Global_Warming"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > pb_Global_Warming_green_threshold, 1, 0
    )

    # Govt_debt_to_PL_to_be_cancelled[region] = Govt_debt_owed_to_private_lenders[region] * Debt_cancelling_pulse[region] / One_year
    idxlhs = fcol_in_mdf["Govt_debt_to_PL_to_be_cancelled"]
    idx1 = fcol_in_mdf["Govt_debt_owed_to_private_lenders"]
    idx2 = fcol_in_mdf["Debt_cancelling_pulse"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j] / One_year

    # Govt_debt_cancelling[region] = Govt_debt_to_PL_to_be_cancelled[region]
    idxlhs = fcol_in_mdf["Govt_debt_cancelling"]
    idx1 = fcol_in_mdf["Govt_debt_to_PL_to_be_cancelled"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Govt_debt_from_public_lenders_cancelled[region] = Govt_debt_from_public_lenders[region] * Public_Debt_cancelling_pulse[region]
    idxlhs = fcol_in_mdf["Govt_debt_from_public_lenders_cancelled"]
    idx1 = fcol_in_mdf["Govt_debt_from_public_lenders"]
    idx2 = fcol_in_mdf["Public_Debt_cancelling_pulse"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Govt_loan_obligation_to_PL_not_met[region] = MAX ( 0 , Govt_loan_obligations_to_PL[region] - Govt_loan_obligations_to_PL_MET[region] )
    idxlhs = fcol_in_mdf["Govt_loan_obligation_to_PL_not_met"]
    idx1 = fcol_in_mdf["Govt_loan_obligations_to_PL"]
    idx2 = fcol_in_mdf["Govt_loan_obligations_to_PL_MET"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])

    # Govt_defaulting[region] = Govt_loan_obligation_to_PL_not_met[region]
    idxlhs = fcol_in_mdf["Govt_defaulting"]
    idx1 = fcol_in_mdf["Govt_loan_obligation_to_PL_not_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Govt_defaults_written_off[region] = Govt_in_default_to_private_lenders[region] / Time_to_write_off_govt_defaults_to_private_lenders
    idxlhs = fcol_in_mdf["Govt_defaults_written_off"]
    idx1 = fcol_in_mdf["Govt_in_default_to_private_lenders"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_to_write_off_govt_defaults_to_private_lenders
      )

    # Govt_investment_share[region] = ( ( ( 1 - Future_leakage[region] ) * Govt_investment_in_public_capacity[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] ) / GDP_USED[region]
    idxlhs = fcol_in_mdf["Govt_investment_share"]
    idx1 = fcol_in_mdf["Future_leakage"]
    idx2 = fcol_in_mdf["Govt_investment_in_public_capacity"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_cost_of_new_capacity"]
    idx4 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (((1 - mdf[rowi, idx1 + j]) * mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j]
      ) / mdf[rowi, idx4 + j]

    # GRASS_Biomass_in_construction_material_left_to_rot = GRASS_Biomass_locked_in_construction_material_GtBiomass / GRASS_Avg_life_of_building_yr * ( 1 - GRASS_Fraction_of_construction_waste_burned_0_to_1 )
    idxlhs = fcol_in_mdf["GRASS_Biomass_in_construction_material_left_to_rot"]
    idx1 = fcol_in_mdf["GRASS_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / GRASS_Avg_life_of_building_yr
      * (1 - GRASS_Fraction_of_construction_waste_burned_0_to_1)
    )

    # Use_of_GRASS_biomass_for_construction = Use_of_GRASS_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_GRASS_biomass_for_construction"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_GRASS_for_construction_in_2000_GtBiomass
      * mdf[rowi, idx1]
      * UNIT_conversion_1_py
    )

    # GRASS_for_construction_use = Use_of_GRASS_biomass_for_construction
    idxlhs = fcol_in_mdf["GRASS_for_construction_use"]
    idx1 = fcol_in_mdf["Use_of_GRASS_biomass_for_construction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # GRASS_Living_biomass_rotting = GRASS_Living_biomass_GtBiomass / GRASS_Avg_life_biomass_yr
    idxlhs = fcol_in_mdf["GRASS_Living_biomass_rotting"]
    idx1 = fcol_in_mdf["GRASS_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / GRASS_Avg_life_biomass_yr

    # GRASS_regrowing_after_being_burnt_Mkm2_py = GRASS_area_burnt_Mkm2 / Time_to_regrow_GRASS_yr
    idxlhs = fcol_in_mdf["GRASS_regrowing_after_being_burnt_Mkm2_py"]
    idx1 = fcol_in_mdf["GRASS_area_burnt_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_GRASS_yr

    # GRASS_regrowing_after_being_deforested_Mkm2_py = GRASS_deforested_Mkm2 / Time_to_regrow_GRASS_after_deforesting_yr
    idxlhs = fcol_in_mdf["GRASS_regrowing_after_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["GRASS_deforested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_GRASS_after_deforesting_yr

    # GRASS_regrowing_after_harvesting_Mkm2_py = GRASS_area_harvested_Mkm2 / Time_to_regrow_GRASS_yr
    idxlhs = fcol_in_mdf["GRASS_regrowing_after_harvesting_Mkm2_py"]
    idx1 = fcol_in_mdf["GRASS_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_GRASS_yr

    # Greenland_ice_melting_km3_py = IF_THEN_ELSE ( Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py > 0 , Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py , 0 )
    idxlhs = fcol_in_mdf["Greenland_ice_melting_km3_py"]
    idx1 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx2 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] > 0, mdf[rowi, idx2], 0)

    # Greenland_ice_area_decrease_Mkm2_pr_yr = ( Greenland_ice_melting_km3_py / Avg_thickness_Greenland_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
    idxlhs = fcol_in_mdf["Greenland_ice_area_decrease_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Greenland_ice_melting_km3_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Avg_thickness_Greenland_km
    ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py

    # Greenland_ice_freezing_km3_py = IF_THEN_ELSE ( Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py < 0 , Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * ( - 1 ) , 0 )
    idxlhs = fcol_in_mdf["Greenland_ice_freezing_km3_py"]
    idx1 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    idx2 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] < 0, mdf[rowi, idx2] * (-1), 0)

    # Greenland_ice_area_increase_Mkm2_pr_yr = ( Greenland_ice_freezing_km3_py / Avg_thickness_Greenland_km ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py
    idxlhs = fcol_in_mdf["Greenland_ice_area_increase_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Greenland_ice_freezing_km3_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Avg_thickness_Greenland_km
    ) * UNIT_Conversion_from_km3_p_kmy_to_Mkm2_py

    # Greenland_ice_losing_is_pos_or_gaining_is_neg_GtIce_py = Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * GtIce_vs_km3
    idxlhs = fcol_in_mdf["Greenland_ice_losing_is_pos_or_gaining_is_neg_GtIce_py"]
    idx1 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * GtIce_vs_km3

    # Greenland_ice_melting_as_water_km3_py = Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py * Densitiy_of_water_relative_to_ice
    idxlhs = fcol_in_mdf["Greenland_ice_melting_as_water_km3_py"]
    idx1 = fcol_in_mdf["Greenland_ice_melting_is_pos_or_freezing_is_neg_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Densitiy_of_water_relative_to_ice

    # Greenland_ice_sliding_into_the_ocean_km3_py = Greenland_ice_volume_on_Greenland_km3 * Exogenous_sliding_of_Greenland_ice_into_the_ocean
    idxlhs = fcol_in_mdf["Greenland_ice_sliding_into_the_ocean_km3_py"]
    idx1 = fcol_in_mdf["Greenland_ice_volume_on_Greenland_km3"]
    idx2 = fcol_in_mdf["Exogenous_sliding_of_Greenland_ice_into_the_ocean"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Greenland_ice_melting_that_slid_into_the_ocean_km3_py = Greenland_ice_sliding_into_the_ocean_km3_py
    idxlhs = fcol_in_mdf["Greenland_ice_melting_that_slid_into_the_ocean_km3_py"]
    idx1 = fcol_in_mdf["Greenland_ice_sliding_into_the_ocean_km3_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py * ( 1 - Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air )
    idxlhs = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_antarctic_ice_ZJ_py"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * (
      1 - Fraction_of_heat_needed_to_melt_antarctic_ice_coming_from_air
    )

    # Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py * ( 1 - Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air )
    idxlhs = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_arctic_sea_ice_ZJ_py"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * (
      1 - Fraction_of_heat_needed_to_melt_arctic_ice_coming_from_air
    )

    # Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_Greenland_ice_that_slid_into_the_ocean_ZJ_py = Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_that_slid_into_the_water_ZJ_py * ( 1 - Fraction_of_heat_needed_to_melt_Greenland_ice_that_slid_into_the_ocean_coming_from_air )
    idxlhs = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_Greenland_ice_that_slid_into_the_ocean_ZJ_py"
    ]
    idx1 = fcol_in_mdf["Heat_used_in_melting_is_pos_or_freezing_is_neg_Greenland_ice_that_slid_into_the_water_ZJ_py"
    ]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * (
      1
      - Fraction_of_heat_needed_to_melt_Greenland_ice_that_slid_into_the_ocean_coming_from_air
    )

    # historical_deforestation_table[us] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 1 ) , ( 1990 , 1.1 ) , ( 2000 , - 2 ) , ( 2010 , - 1.1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[af] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 7 ) , ( 1990 , 4 ) , ( 2000 , 0 ) , ( 2010 , 6 ) , ( 2020 , - 1 ) , ( 2030 , - 1 ) , ( 2050 , - 1 ) , ( 2075 , - 1 ) , ( 2100 , - 1 ) ) ) historical_deforestation_table[cn] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 3 ) , ( 1990 , 7 ) , ( 2000 , - 1 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[me] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 2 ) , ( 1990 , 2 ) , ( 2000 , 2 ) , ( 2010 , 2 ) , ( 2020 , 1 ) , ( 2030 , 0.5 ) , ( 2050 , 0.5 ) , ( 2075 , 0.5 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[sa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0.5 ) , ( 2000 , 0 ) , ( 2010 , 0.6 ) , ( 2020 , - 0.1 ) , ( 2030 , - 0.1 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[la] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.5 ) , ( 2010 , - 1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[pa] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 0 ) , ( 2020 , - 1 ) , ( 2030 , - 0.5 ) , ( 2050 , - 0.5 ) , ( 2075 , - 0.5 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[ec] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 10 ) , ( 1990 , - 5 ) , ( 2000 , 2 ) , ( 2010 , 0 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[eu] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , - 0.5 ) , ( 2010 , 1 ) , ( 2020 , 0 ) , ( 2030 , 0 ) , ( 2050 , 0 ) , ( 2075 , 0 ) , ( 2100 , 0 ) ) ) historical_deforestation_table[se] = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1980 , 0 ) , ( 1990 , 0 ) , ( 2000 , 0 ) , ( 2010 , 1 ) , ( 2020 , 0 ) , ( 2030 , - 1 ) , ( 2050 , - 1 ) , ( 2075 , - 1 ) , ( 2100 , - 1 ) ) )
    tabidx = ftab_in_d_table[  "historical_deforestation_table"]  # fetch the correct table
    idx2 = fcol_in_mdf["historical_deforestation_table"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(zeit, look[:, 0], look[:, j + 1])

    # historical_deforestation[region] = IF_THEN_ELSE ( zeit < Policy_start_year , historical_deforestation_table , 0 )
    idxlhs = fcol_in_mdf["historical_deforestation"]
    idx1 = fcol_in_mdf["historical_deforestation_table"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        zeit < Policy_start_year, mdf[rowi, idx1 + j], 0
      )

    # Hydro_net_depreciation = IF_THEN_ELSE ( zeit > 2025 , Hydro_net_depreciation_multiplier_on_gen_cap * Hydro_future_net_dep_rate , 0 )
    idxlhs = fcol_in_mdf["Hydro_net_depreciation"]
    idx1 = fcol_in_mdf["Hydro_net_depreciation_multiplier_on_gen_cap"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 2025, mdf[rowi, idx1] * Hydro_future_net_dep_rate, 0
    )

    # Increase_in_exepi[region] = Extra_energy_productivity_index_2024_is_1[region] * ( FTPEE_rate_of_change_policy[region] / 100 ) * UNIT_conv_to_1_per_yr
    idxlhs = fcol_in_mdf["Increase_in_exepi"]
    idx1 = fcol_in_mdf["Extra_energy_productivity_index_2024_is_1"]
    idx2 = fcol_in_mdf["FTPEE_rate_of_change_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * (mdf[rowi, idx2 + j] / 100) * UNIT_conv_to_1_per_yr
      )

    # Increase_in_existential_minimum = IF_THEN_ELSE ( zeit > 2023 , 0 , 0 )
    idxlhs = fcol_in_mdf["Increase_in_existential_minimum"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit > 2023, 0, 0)

    # Increase_in_existential_minimum_income = Indicated_Existential_minimum_income * Increase_in_existential_minimum
    idxlhs = fcol_in_mdf["Increase_in_existential_minimum_income"]
    idx1 = fcol_in_mdf["Indicated_Existential_minimum_income"]
    idx2 = fcol_in_mdf["Increase_in_existential_minimum"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Increase_in_GDPL[region] = Public_money_from_LPB_policy[region] * ( 1 - LPBgrant_policy[region] )
    idxlhs = fcol_in_mdf["Increase_in_GDPL"]
    idx1 = fcol_in_mdf["Public_money_from_LPB_policy"]
    idx2 = fcol_in_mdf["LPBgrant_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # increase_in_global_speculative_asset_pool = Global_annual_surplus_of_available_private_capital
    idxlhs = fcol_in_mdf["increase_in_global_speculative_asset_pool"]
    idx1 = fcol_in_mdf["Global_annual_surplus_of_available_private_capital"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Increase_in_public_loan_defaults[region] = All_loan_service_obligations_to_public_lenders_not_met[region]
    idxlhs = fcol_in_mdf["Increase_in_public_loan_defaults"]
    idx1 = fcol_in_mdf["All_loan_service_obligations_to_public_lenders_not_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j]

    # Not_enough_regen_cropland[region] = IF_THEN_ELSE ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction >= 0.03 , ( Desired_regenerative_cropland_fraction + FLWR_policy - Regenerative_cropland_fraction ) , 0 )
    idxlhs = fcol_in_mdf["Not_enough_regen_cropland"]
    idx1 = fcol_in_mdf["Desired_regenerative_cropland_fraction"]
    idx2 = fcol_in_mdf["FLWR_policy"]
    idx3 = fcol_in_mdf["Regenerative_cropland_fraction"]
    idx4 = fcol_in_mdf["Desired_regenerative_cropland_fraction"]
    idx5 = fcol_in_mdf["FLWR_policy"]
    idx6 = fcol_in_mdf["Regenerative_cropland_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = IF_THEN_ELSE(
        mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] - mdf[rowi, idx3 + j] >= 0.03,     (mdf[rowi, idx4 + j] + mdf[rowi, idx5 + j] - mdf[rowi, idx6 + j]),     0,   )

    # Increase_in_regen_cropland[region] = Not_enough_regen_cropland[region] / Time_to_implement_regen_practices * Eff_of_wealth_on_regnerative_practices[region]
    idxlhs = fcol_in_mdf["Increase_in_regen_cropland"]
    idx1 = fcol_in_mdf["Not_enough_regen_cropland"]
    idx2 = fcol_in_mdf["Eff_of_wealth_on_regnerative_practices"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_to_implement_regen_practices * mdf[rowi, idx2 + j]
      )

    # Indicated_inequality_index_with_tax[region] = Indicated_inequality_index_higher_is_more_unequal[region] / Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init[region]
    idxlhs = fcol_in_mdf["Indicated_inequality_index_with_tax"]
    idx1 = fcol_in_mdf["Indicated_inequality_index_higher_is_more_unequal"]
    idx2 = fcol_in_mdf["Effect_of_Worker_to_owner_income_after_tax_ratio_scaled_to_init"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # OSF_from_GDPpp_alone[region] = OSF_in_1980[region] * ( 1 + Slope_of_OSF_from_GDPpp_alone[region] * ( Effective_GDPpp_for_OSF[region] / GDPpp_in_1980[region] - 1 ) )
    idxlhs = fcol_in_mdf["OSF_from_GDPpp_alone"]
    idx1 = fcol_in_mdf["Effective_GDPpp_for_OSF"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = OSF_in_1980[j] * (
        1
        + Slope_of_OSF_from_GDPpp_alone[j]
        * (mdf[rowi, idx1 + j] / GDPpp_in_1980[j] - 1)
      )

    # Scaled_Size_of_industrial_sector[region] = Size_of_industrial_sector[region] / Size_of_industrial_sector_in_1980[region]
    idxlhs = fcol_in_mdf["Scaled_Size_of_industrial_sector"]
    idx1 = fcol_in_mdf["Size_of_industrial_sector"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Size_of_industrial_sector_in_1980[j]

    # Indicated_OSF_with_ind_sector_effect[region] = MIN ( Max_OSF , MAX ( Min_OSF , OSF_from_GDPpp_alone[region] ) ) * Scaled_Size_of_industrial_sector[region] * Strength_of_effect_of_industrial_sector_size_on_OSF[region]
    idxlhs = fcol_in_mdf["Indicated_OSF_with_ind_sector_effect"]
    idx1 = fcol_in_mdf["OSF_from_GDPpp_alone"]
    idx2 = fcol_in_mdf["Scaled_Size_of_industrial_sector"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (min(Max_OSF, max(Min_OSF, mdf[rowi, idx1 + j]))
        * mdf[rowi, idx2 + j]
        * Strength_of_effect_of_industrial_sector_size_on_OSF[j]
      )

    # pb_Air_Pollution_global = pb_Air_Pollution_a * ( GLobal_GDP_in_terraUSD / pb_Air_Pollution_Unit_conv_to_make_LN_dmnl_from_terra_USD ) + pb_Air_Pollution_b
    idxlhs = fcol_in_mdf["pb_Air_Pollution_global"]
    idx1 = fcol_in_mdf["GLobal_GDP_in_terraUSD"]
    mdf[rowi, idxlhs] = (
      pb_Air_Pollution_a
      * (mdf[rowi, idx1] / pb_Air_Pollution_Unit_conv_to_make_LN_dmnl_from_terra_USD)
      + pb_Air_Pollution_b
    )

    # Urban_aerosol_concentration_hist = WITH LOOKUP ( zeit , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 1990 , 39.7 ) , ( 1995 , 39.6 ) , ( 2000 , 40.1 ) , ( 2005 , 41 ) , ( 2010 , 41.9 ) , ( 2015 , 41.9 ) , ( 2020 , 43.5 ) ) )
    tabidx = ftab_in_d_table[  "Urban_aerosol_concentration_hist"]  # fetch the correct table
    idxlhs = fcol_in_mdf["Urban_aerosol_concentration_hist"]  # get the location of the lhs in mdf
    look = d_table[tabidx]
    valgt = GRAPH(zeit, look[:, 0], look[:, 1])
    mdf[rowi, idxlhs] = valgt

    # Indicated_Urban_aerosol_concentration_future = IF_THEN_ELSE ( zeit >= 2020 , pb_Air_Pollution_global * UNIT_conv_to_UAC , Urban_aerosol_concentration_hist )
    idxlhs = fcol_in_mdf["Indicated_Urban_aerosol_concentration_future"]
    idx1 = fcol_in_mdf["pb_Air_Pollution_global"]
    idx2 = fcol_in_mdf["Urban_aerosol_concentration_hist"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit >= 2020, mdf[rowi, idx1] * UNIT_conv_to_UAC, mdf[rowi, idx2]
    )

    # Recent_sales[region] = SMOOTHI ( Sales[region] , Sales_averaging_time , Demand_in_1980[region] )
    idx1 = fcol_in_mdf["Recent_sales"]
    idx2 = fcol_in_mdf["Sales"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Sales_averaging_time
        * dt
      )

    # Inventory_coverage[region] = Inventory[region] / Recent_sales[region]
    idxlhs = fcol_in_mdf["Inventory_coverage"]
    idx1 = fcol_in_mdf["Inventory"]
    idx2 = fcol_in_mdf["Recent_sales"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Inventory_coverage_to_goal_ratio[region] = Inventory_coverage[region] / Goal_for_inventory_coverage
    idxlhs = fcol_in_mdf["Inventory_coverage_to_goal_ratio"]
    idx1 = fcol_in_mdf["Inventory_coverage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Goal_for_inventory_coverage

    # Perceived_inventory_ratio[region] = SMOOTH3 ( Inventory_coverage_to_goal_ratio[region] , Time_required_for_inventory_fluctuations_to_impact_inflation_rate )
    idxin = fcol_in_mdf["Inventory_coverage_to_goal_ratio"]
    idx2 = fcol_in_mdf["Perceived_inventory_ratio_2"]
    idx1 = fcol_in_mdf["Perceived_inventory_ratio_1"]
    idxout = fcol_in_mdf["Perceived_inventory_ratio"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j])
        / (Time_required_for_inventory_fluctuations_to_impact_inflation_rate / 3)
        * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j])
        / (Time_required_for_inventory_fluctuations_to_impact_inflation_rate / 3)
        * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j])
        / (Time_required_for_inventory_fluctuations_to_impact_inflation_rate / 3)
        * dt
      )

    # Inflation_rate_used_only_for_interest_rate[region] = MAX ( 0 , SoE_of_inventory_on_inflation_rate[region] * ( Perceived_inventory_ratio[region] / Minimum_relative_inventory_without_inflation[region] - 1 ) )
    idxlhs = fcol_in_mdf["Inflation_rate_used_only_for_interest_rate"]
    idx1 = fcol_in_mdf["Perceived_inventory_ratio"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(
        0,     SoE_of_inventory_on_inflation_rate[j]
        * (mdf[rowi, idx1 + j] / Minimum_relative_inventory_without_inflation[j] - 1),   )

    # Kyoto_Fluor_degradation = Kyoto_Fluor_gases_in_atm / Time_to_degrade_Kyoto_Fluor_yr
    idxlhs = fcol_in_mdf["Kyoto_Fluor_degradation"]
    idx1 = fcol_in_mdf["Kyoto_Fluor_gases_in_atm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_degrade_Kyoto_Fluor_yr

    # Laying_off_cut_off[region] = WITH LOOKUP ( Employed_to_labor_pool_ratio[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0.01 , 0 ) , ( 0.02 , 0.02 ) , ( 0.04 , 0.25 ) , ( 0.06 , 0.7 ) , ( 0.08 , 0.95 ) , ( 0.1 , 1 ) ) )
    tabidx = ftab_in_d_table["Laying_off_cut_off"]  # fetch the correct table
    idx2 = fcol_in_mdf["Laying_off_cut_off"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Employed_to_labor_pool_ratio"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Number_of_people_to_be_let_go[region] = MAX ( 0 , Employed[region] - Full_time_jobs_with_participation_constraint[region] )
    idxlhs = fcol_in_mdf["Number_of_people_to_be_let_go"]
    idx1 = fcol_in_mdf["Employed"]
    idx2 = fcol_in_mdf["Full_time_jobs_with_participation_constraint"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])

    # Laying_off_rate[region] = Number_of_people_to_be_let_go[region] / Time_to_implement_lay_off
    idxlhs = fcol_in_mdf["Laying_off_rate"]
    idx1 = fcol_in_mdf["Number_of_people_to_be_let_go"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Time_to_implement_lay_off

    # P_Pb_Phaseout_time = P_Pb_Phaseout_time_TLTL * Effect_of_GL_on_phaseout_time
    idxlhs = fcol_in_mdf["P_Pb_Phaseout_time"]
    idx1 = fcol_in_mdf["Effect_of_GL_on_phaseout_time"]
    mdf[rowi, idxlhs] = P_Pb_Phaseout_time_TLTL * mdf[rowi, idx1]

    # P_Pb_Phaseout_multiplier = math.exp ( - ( ( zeit - Start_year_P_Pb_phaseout ) / P_Pb_Phaseout_time ) )
    idxlhs = fcol_in_mdf["P_Pb_Phaseout_multiplier"]
    idx1 = fcol_in_mdf["P_Pb_Phaseout_time"]
    mdf[rowi, idxlhs] = math.exp(-((zeit - Start_year_P_Pb_phaseout) / mdf[rowi, idx1]))

    # Lead_release_global = ( ( Lead_release_a * LN ( GLobal_GDP / Unit_conv_to_make_LN_dmnl_from_terra_USD ) - Lead_release_b ) * P_Pb_Phaseout_multiplier ) * Lead_UNIT_conv_to_Mt_pr_yr
    idxlhs = fcol_in_mdf["Lead_release_global"]
    idx1 = fcol_in_mdf["GLobal_GDP"]
    idx2 = fcol_in_mdf["P_Pb_Phaseout_multiplier"]
    mdf[rowi, idxlhs] = (
      (
        Lead_release_a
        * math.log(mdf[rowi, idx1] / Unit_conv_to_make_LN_dmnl_from_terra_USD)
        - Lead_release_b
      )
      * mdf[rowi, idx2]
    ) * Lead_UNIT_conv_to_Mt_pr_yr

    # Leaving_the_labor_pool_limitation[region] = WITH LOOKUP ( Unemployed_to_labor_pool_ratio[region] , ( [ ( 0 , 0 ) - ( 0.55382 , 39.1651 ) ] , ( 0.01 , 0 ) , ( 0.02 , 0.02 ) , ( 0.04 , 0.25 ) , ( 0.06 , 0.7 ) , ( 0.08 , 0.95 ) , ( 0.1 , 1 ) ) )
    tabidx = ftab_in_d_table[  "Leaving_the_labor_pool_limitation"]  # fetch the correct table
    idx2 = fcol_in_mdf["Leaving_the_labor_pool_limitation"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Unemployed_to_labor_pool_ratio"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Leaving_the_labor_pool[region] = ( People_considering_leaving_the_pool[region] / Time_to_implement_actually_leaving_the_pool ) * Leaving_the_labor_pool_limitation[region]
    idxlhs = fcol_in_mdf["Leaving_the_labor_pool"]
    idx1 = fcol_in_mdf["People_considering_leaving_the_pool"]
    idx2 = fcol_in_mdf["Leaving_the_labor_pool_limitation"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Time_to_implement_actually_leaving_the_pool
      ) * mdf[rowi, idx2 + j]

    # Private_investment_share[region] = ( Private_Investment_in_new_capacity[region] - Funds_from_private_investment_leaked[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] / GDP_USED[region]
    idxlhs = fcol_in_mdf["Private_investment_share"]
    idx1 = fcol_in_mdf["Private_Investment_in_new_capacity"]
    idx2 = fcol_in_mdf["Funds_from_private_investment_leaked"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_cost_of_new_capacity"]
    idx4 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j])
        / mdf[rowi, idx3 + j]
        / mdf[rowi, idx4 + j]
      )

    # Local_private_and_govt_investment_share[region] = Govt_investment_share[region] + Private_investment_share[region]
    idxlhs = fcol_in_mdf["Local_private_and_govt_investment_share"]
    idx1 = fcol_in_mdf["Govt_investment_share"]
    idx2 = fcol_in_mdf["Private_investment_share"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Loosing_a_job[region] = Laying_off_rate[region] * Laying_off_cut_off[region]
    idxlhs = fcol_in_mdf["Loosing_a_job"]
    idx1 = fcol_in_mdf["Laying_off_rate"]
    idx2 = fcol_in_mdf["Laying_off_cut_off"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # LPB_investment_share[region] = ( ( ( 1 - Future_leakage[region] ) * Public_money_from_LPB_policy_to_investment[region] ) / Eff_of_env_damage_on_cost_of_new_capacity[region] ) / GDP_USED[region]
    idxlhs = fcol_in_mdf["LPB_investment_share"]
    idx1 = fcol_in_mdf["Future_leakage"]
    idx2 = fcol_in_mdf["Public_money_from_LPB_policy_to_investment"]
    idx3 = fcol_in_mdf["Eff_of_env_damage_on_cost_of_new_capacity"]
    idx4 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (((1 - mdf[rowi, idx1 + j]) * mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j]
      ) / mdf[rowi, idx4 + j]

    # LW_clear_sky_emissions_to_surface = BB_radiation_at_Temp_in_atm_ZJ_py
    idxlhs = fcol_in_mdf["LW_clear_sky_emissions_to_surface"]
    idx1 = fcol_in_mdf["BB_radiation_at_Temp_in_atm_ZJ_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # LW_re_radiated_by_clouds = LW_LO_cloud_radiation + LW_HI_cloud_radiation
    idxlhs = fcol_in_mdf["LW_re_radiated_by_clouds"]
    idx1 = fcol_in_mdf["LW_LO_cloud_radiation"]
    idx2 = fcol_in_mdf["LW_HI_cloud_radiation"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # LW_surface_emissions_NOT_escaping_through_atm_window = LW_surface_emission * ( 1 - Frac_of_surface_emission_through_atm_window )
    idxlhs = fcol_in_mdf["LW_surface_emissions_NOT_escaping_through_atm_window"]
    idx1 = fcol_in_mdf["LW_surface_emission"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * (
      1 - Frac_of_surface_emission_through_atm_window
    )

    # Model_Volcanic_aerosol_forcing_W_p_m2 = Volcanic_aerosols_in_stratosphere / Time_for_volcanic_aerosols_to_remain_in_the_stratosphere * Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions
    idxlhs = fcol_in_mdf["Model_Volcanic_aerosol_forcing_W_p_m2"]
    idx1 = fcol_in_mdf["Volcanic_aerosols_in_stratosphere"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / Time_for_volcanic_aerosols_to_remain_in_the_stratosphere
      * Conversion_of_volcanic_aerosol_forcing_to_volcanic_aerosol_emissions
    )

    # Montreal_gases_degradation = Montreal_gases_in_atm / Time_to_degrade_Montreal_gases_yr
    idxlhs = fcol_in_mdf["Montreal_gases_degradation"]
    idx1 = fcol_in_mdf["Montreal_gases_in_atm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_degrade_Montreal_gases_yr

    # Nitrogen_syn_use_global = SUM ( Nitrogen_syn_use[region!] )
    idxlhs = fcol_in_mdf["Nitrogen_syn_use_global"]
    idx1 = fcol_in_mdf["Nitrogen_syn_use"]
    globsum = 0
    for j in range(0, 10):
      globsum = globsum + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = globsum

    # N_pb_overloading = Nitrogen_syn_use_global / Nitrogen_PB_green_threshold
    idxlhs = fcol_in_mdf["N_pb_overloading"]
    idx1 = fcol_in_mdf["Nitrogen_syn_use_global"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Nitrogen_PB_green_threshold

    # N2O_degradation_MtN2O_py = N2O_in_atmosphere_MtN2O / Time_to_degrade_N2O_in_atmopshere_yr
    idxlhs = fcol_in_mdf["N2O_degradation_MtN2O_py"]
    idx1 = fcol_in_mdf["N2O_in_atmosphere_MtN2O"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_degrade_N2O_in_atmopshere_yr

    # Net_C_to_atm = Avg_volcanic_activity_GtC_py - C_diffusion_into_ocean_from_atm_net - Carbon_captured_and_stored_GtC_py + CH4_in_the_atmosphere_converted_to_CO2 - CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py - CO2_flux_from_atm_to_NF_for_new_growth_GtC_py - CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py - CO2_flux_from_atm_to_TUNDRA_for_new_growth + CO2_flux_GRASS_to_atm_GtC_py + CO2_flux_NF_to_atm_GtC_py + CO2_flux_TROP_to_atm_GtC_py + CO2_flux_TUNDRA_to_atm + Man_made_fossil_C_emissions_GtC_py
    idxlhs = fcol_in_mdf["Net_C_to_atm"]
    idx1 = fcol_in_mdf["Avg_volcanic_activity_GtC_py"]
    idx2 = fcol_in_mdf["C_diffusion_into_ocean_from_atm_net"]
    idx3 = fcol_in_mdf["Carbon_captured_and_stored_GtC_py"]
    idx4 = fcol_in_mdf["CH4_in_the_atmosphere_converted_to_CO2"]
    idx5 = fcol_in_mdf["CO2_flux_from_atm_to_GRASS_for_new_growth_GtC_py"]
    idx6 = fcol_in_mdf["CO2_flux_from_atm_to_NF_for_new_growth_GtC_py"]
    idx7 = fcol_in_mdf["CO2_flux_from_atm_to_TROP_for_new_growth_GtC_py"]
    idx8 = fcol_in_mdf["CO2_flux_from_atm_to_TUNDRA_for_new_growth"]
    idx9 = fcol_in_mdf["CO2_flux_GRASS_to_atm_GtC_py"]
    idx10 = fcol_in_mdf["CO2_flux_NF_to_atm_GtC_py"]
    idx11 = fcol_in_mdf["CO2_flux_TROP_to_atm_GtC_py"]
    idx12 = fcol_in_mdf["CO2_flux_TUNDRA_to_atm"]
    idx13 = fcol_in_mdf["Man_made_fossil_C_emissions_GtC_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      - mdf[rowi, idx2]
      - mdf[rowi, idx3]
      + mdf[rowi, idx4]
      - mdf[rowi, idx5]
      - mdf[rowi, idx6]
      - mdf[rowi, idx7]
      - mdf[rowi, idx8]
      + mdf[rowi, idx9]
      + mdf[rowi, idx10]
      + mdf[rowi, idx11]
      + mdf[rowi, idx12]
      + mdf[rowi, idx13]
    )

    # Net_C_to_atm_rate = Net_C_to_atm
    idxlhs = fcol_in_mdf["Net_C_to_atm_rate"]
    idx1 = fcol_in_mdf["Net_C_to_atm"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Net_change_in_OSF[region] = ( Indicated_OSF_with_ind_sector_effect[region] - Owner_saving_fraction[region] ) / Time_to_adjust_owner_investment_behaviour_in_productive_assets
    idxlhs = fcol_in_mdf["Net_change_in_OSF"]
    idx1 = fcol_in_mdf["Indicated_OSF_with_ind_sector_effect"]
    idx2 = fcol_in_mdf["Owner_saving_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]
      ) / Time_to_adjust_owner_investment_behaviour_in_productive_assets

    # Temp_ocean_surface_in_K = Temp_surface_average_K - Temp_gradient_in_surface_degK
    idxlhs = fcol_in_mdf["Temp_ocean_surface_in_K"]
    idx1 = fcol_in_mdf["Temp_surface_average_K"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - Temp_gradient_in_surface_degK

    # Surface_deep_ocean_temp_diff_degC = Temp_ocean_surface_in_K - Temp_ocean_deep_in_K
    idxlhs = fcol_in_mdf["Surface_deep_ocean_temp_diff_degC"]
    idx1 = fcol_in_mdf["Temp_ocean_surface_in_K"]
    idx2 = fcol_in_mdf["Temp_ocean_deep_in_K"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # Net_heat_flow_ocean_from_surface_to_deep_ZJ_py = Surface_deep_ocean_temp_diff_degC * Net_heat_flow_ocean_between_surface_and_deep_per_K_of_difference_ZJ_py_K
    idxlhs = fcol_in_mdf["Net_heat_flow_ocean_from_surface_to_deep_ZJ_py"]
    idx1 = fcol_in_mdf["Surface_deep_ocean_temp_diff_degC"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      * Net_heat_flow_ocean_between_surface_and_deep_per_K_of_difference_ZJ_py_K
    )

    # net_migration_function[region] = nmf_a[region] * LN ( GDPpp_USED[region] * UNIT_conv_to_make_exp_dmnl ) + nmf_b[region] + nmf_c[region]
    idxlhs = fcol_in_mdf["net_migration_function"]
    idx1 = fcol_in_mdf["GDPpp_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (nmf_a[j] * math.log(mdf[rowi, idx1 + j] * UNIT_conv_to_make_exp_dmnl)
        + nmf_b[j]
        + nmf_c[j]
      )

    # net_migration_10_to_14[region] = Migration_fraction_10_to_14_cohort[region] * net_migration_function[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
    idxlhs = fcol_in_mdf["net_migration_10_to_14"]
    idx1 = fcol_in_mdf["net_migration_function"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Migration_fraction_10_to_14_cohort[j]
        * mdf[rowi, idx1 + j]
        * Factor_to_account_for_net_migration_not_officially_recorded[j]
      )

    # net_migration_20_to_24[region] = net_migration_function[region] * Migration_fraction_20_to_24_cohort[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
    idxlhs = fcol_in_mdf["net_migration_20_to_24"]
    idx1 = fcol_in_mdf["net_migration_function"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Migration_fraction_20_to_24_cohort[j]
        * Factor_to_account_for_net_migration_not_officially_recorded[j]
      )

    # net_migration_25_to_29[region] = Migration_fraction_25_to_29_cohort[region] * net_migration_function[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
    idxlhs = fcol_in_mdf["net_migration_25_to_29"]
    idx1 = fcol_in_mdf["net_migration_function"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (Migration_fraction_25_to_29_cohort[j]
        * mdf[rowi, idx1 + j]
        * Factor_to_account_for_net_migration_not_officially_recorded[j]
      )

    # net_migration_30_to_34[region] = net_migration_function[region] * Migration_fraction_30_to_34_cohort[region] * Factor_to_account_for_net_migration_not_officially_recorded[region]
    idxlhs = fcol_in_mdf["net_migration_30_to_34"]
    idx1 = fcol_in_mdf["net_migration_function"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j]
        * Migration_fraction_30_to_34_cohort[j]
        * Factor_to_account_for_net_migration_not_officially_recorded[j]
      )

    # Use_of_NF_biomass_for_construction = Use_of_NF_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_NF_biomass_for_construction"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_NF_for_construction_in_2000_GtBiomass
      * mdf[rowi, idx1]
      * UNIT_conversion_1_py
    )

    # NF_for_construction_use = Use_of_NF_biomass_for_construction
    idxlhs = fcol_in_mdf["NF_for_construction_use"]
    idx1 = fcol_in_mdf["Use_of_NF_biomass_for_construction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # NF_Living_biomass_rotting = NF_Living_biomass_GtBiomass / NF_Avg_life_biomass_yr
    idxlhs = fcol_in_mdf["NF_Living_biomass_rotting"]
    idx1 = fcol_in_mdf["NF_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / NF_Avg_life_biomass_yr

    # NF_regrowing_after_being_burnt_Mkm2_py = NF_area_burnt_Mkm2 / Time_to_regrow_NF_yr
    idxlhs = fcol_in_mdf["NF_regrowing_after_being_burnt_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_area_burnt_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_NF_yr

    # NF_regrowing_after_being_clear_cut_Mkm2_py = NF_area_clear_cut_Mkm2 / ( Time_to_regrow_NF_yr * 2 )
    idxlhs = fcol_in_mdf["NF_regrowing_after_being_clear_cut_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_area_clear_cut_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (Time_to_regrow_NF_yr * 2)

    # NF_regrowing_after_being_deforested_Mkm2_py = NF_area_deforested_Mkm2 / Time_to_regrow_NF_after_deforesting_yr
    idxlhs = fcol_in_mdf["NF_regrowing_after_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_area_deforested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_NF_after_deforesting_yr

    # NF_regrowing_after_harvesting_Mkm2_py = NF_area_harvested_Mkm2 / Time_to_regrow_NF_yr
    idxlhs = fcol_in_mdf["NF_regrowing_after_harvesting_Mkm2_py"]
    idx1 = fcol_in_mdf["NF_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_NF_yr

    # NF_TUNDRA_Biomass_in_construction_material_left_to_rot = NF_Biomass_locked_in_construction_material_GtBiomass / NF_Avg_life_of_building_yr * ( 1 - NF_Fraction_of_construction_waste_burned_0_to_1 )
    idxlhs = fcol_in_mdf["NF_TUNDRA_Biomass_in_construction_material_left_to_rot"]
    idx1 = fcol_in_mdf["NF_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / NF_Avg_life_of_building_yr
      * (1 - NF_Fraction_of_construction_waste_burned_0_to_1)
    )

    # Nitrogen_risk_score = IF_THEN_ELSE ( Nitrogen_syn_use_global > Nitrogen_PB_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Nitrogen_risk_score"]
    idx1 = fcol_in_mdf["Nitrogen_syn_use_global"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > Nitrogen_PB_green_threshold, 1, 0
    )

    # Nitrogen_use_per_ha[region] = Nitrogen_syn_use[region] / Cropland[region]
    idxlhs = fcol_in_mdf["Nitrogen_use_per_ha"]
    idx1 = fcol_in_mdf["Nitrogen_syn_use"]
    idx2 = fcol_in_mdf["Cropland"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # Nuclear_net_depreciation = IF_THEN_ELSE ( zeit > 2025 , Nuclear_net_depreciation_multiplier_on_gen_cap * Nuclear_future_net_dep_rate , 0 )
    idxlhs = fcol_in_mdf["Nuclear_net_depreciation"]
    idx1 = fcol_in_mdf["Nuclear_net_depreciation_multiplier_on_gen_cap"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      zeit > 2025, mdf[rowi, idx1] * Nuclear_future_net_dep_rate, 0
    )

    # Phosphorous_release_global = ( ( P_release_a * LN ( GLobal_GDP / Unit_conv_to_make_LN_dmnl_from_terra_USD ) - P_release_b ) * P_Pb_Phaseout_multiplier ) * UNIT_conv_to_Mt_pr_yr
    idxlhs = fcol_in_mdf["Phosphorous_release_global"]
    idx1 = fcol_in_mdf["GLobal_GDP"]
    idx2 = fcol_in_mdf["P_Pb_Phaseout_multiplier"]
    mdf[rowi, idxlhs] = (
      (
        P_release_a
        * math.log(mdf[rowi, idx1] / Unit_conv_to_make_LN_dmnl_from_terra_USD)
        - P_release_b
      )
      * mdf[rowi, idx2]
    ) * UNIT_conv_to_Mt_pr_yr

    # Phosphorous_risk_score = IF_THEN_ELSE ( Phosphorous_release_global > Phosphorous_PB_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Phosphorous_risk_score"]
    idx1 = fcol_in_mdf["Phosphorous_release_global"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > Phosphorous_PB_green_threshold, 1, 0
    )

    # Nutrient_risk_score = ( Nitrogen_risk_score + Phosphorous_risk_score ) / 2
    idxlhs = fcol_in_mdf["Nutrient_risk_score"]
    idx1 = fcol_in_mdf["Nitrogen_risk_score"]
    idx2 = fcol_in_mdf["Phosphorous_risk_score"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2]) / 2

    # Ocean_heat_used_for_melting_ZJ_py = ( Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py + Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py + Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_Greenland_ice_that_slid_into_the_ocean_ZJ_py ) / Heat_in_surface
    idxlhs = fcol_in_mdf["Ocean_heat_used_for_melting_ZJ_py"]
    idx1 = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_antarctic_ice_ZJ_py"
    ]
    idx2 = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_arctic_ice_ZJ_py"
    ]
    idx3 = fcol_in_mdf["Heat_withdrawn_from_ocean_surface_by_melting_pos_or_added_neg_by_freezing_Greenland_ice_that_slid_into_the_ocean_ZJ_py"
    ]
    idx4 = fcol_in_mdf["Heat_in_surface"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]) / mdf[rowi, idx4
    ]

    # Total_net_aerosol_forcings_W_p_m2 = Anthropogenic_aerosol_forcing + Model_Volcanic_aerosol_forcing_W_p_m2
    idxlhs = fcol_in_mdf["Total_net_aerosol_forcings_W_p_m2"]
    idx1 = fcol_in_mdf["Anthropogenic_aerosol_forcing"]
    idx2 = fcol_in_mdf["Model_Volcanic_aerosol_forcing_W_p_m2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2]

    # Total_net_aerosol_forcing_ZJ_py = Total_net_aerosol_forcings_W_p_m2 * UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["Total_net_aerosol_forcing_ZJ_py"]
    idx1 = fcol_in_mdf["Total_net_aerosol_forcings_W_p_m2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # SW_clear_sky_reflection_aka_scattering = Incoming_solar_ZJ_py * Frac_SW_clear_sky_reflection_aka_scattering - Total_net_aerosol_forcing_ZJ_py
    idxlhs = fcol_in_mdf["SW_clear_sky_reflection_aka_scattering"]
    idx1 = fcol_in_mdf["Incoming_solar_ZJ_py"]
    idx2 = fcol_in_mdf["Total_net_aerosol_forcing_ZJ_py"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] * Frac_SW_clear_sky_reflection_aka_scattering - mdf[rowi, idx2]
    )

    # SW_Atmospheric_absorption = Incoming_solar_ZJ_py * Frac_atm_absorption
    idxlhs = fcol_in_mdf["SW_Atmospheric_absorption"]
    idx1 = fcol_in_mdf["Incoming_solar_ZJ_py"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * Frac_atm_absorption

    # SW_to_surface = Incoming_solar_ZJ_py - SW_Atmospheric_absorption - SW_HI_cloud_efffect_aka_cloud_albedo - SW_LO_cloud_efffect_aka_cloud_albedo - SW_clear_sky_reflection_aka_scattering
    idxlhs = fcol_in_mdf["SW_to_surface"]
    idx1 = fcol_in_mdf["Incoming_solar_ZJ_py"]
    idx2 = fcol_in_mdf["SW_Atmospheric_absorption"]
    idx3 = fcol_in_mdf["SW_HI_cloud_efffect_aka_cloud_albedo"]
    idx4 = fcol_in_mdf["SW_LO_cloud_efffect_aka_cloud_albedo"]
    idx5 = fcol_in_mdf["SW_clear_sky_reflection_aka_scattering"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      - mdf[rowi, idx2]
      - mdf[rowi, idx3]
      - mdf[rowi, idx4]
      - mdf[rowi, idx5]
    )

    # SW_surface_reflection = Avg_earths_surface_albedo * SW_to_surface
    idxlhs = fcol_in_mdf["SW_surface_reflection"]
    idx1 = fcol_in_mdf["Avg_earths_surface_albedo"]
    idx2 = fcol_in_mdf["SW_to_surface"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Reflected_Solar_SW = SW_clear_sky_reflection_aka_scattering + SW_HI_cloud_efffect_aka_cloud_albedo + SW_LO_cloud_efffect_aka_cloud_albedo + SW_surface_reflection
    idxlhs = fcol_in_mdf["Reflected_Solar_SW"]
    idx1 = fcol_in_mdf["SW_clear_sky_reflection_aka_scattering"]
    idx2 = fcol_in_mdf["SW_HI_cloud_efffect_aka_cloud_albedo"]
    idx3 = fcol_in_mdf["SW_LO_cloud_efffect_aka_cloud_albedo"]
    idx4 = fcol_in_mdf["SW_surface_reflection"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3] + mdf[rowi, idx4]
    )

    # Reflected_Solar_SW_W_p_m2 = Reflected_Solar_SW / UNIT_conversion_W_p_m2_earth_to_ZJ_py
    idxlhs = fcol_in_mdf["Reflected_Solar_SW_W_p_m2"]
    idx1 = fcol_in_mdf["Reflected_Solar_SW"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_W_p_m2_earth_to_ZJ_py

    # Outgoing_radiation_at_TOA = LW_TOA_radiation_from_atm_to_space_W_p_m2 + Reflected_Solar_SW_W_p_m2 - LW_HI_cloud_radiation_W_p_m2
    idxlhs = fcol_in_mdf["Outgoing_radiation_at_TOA"]
    idx1 = fcol_in_mdf["LW_TOA_radiation_from_atm_to_space_W_p_m2"]
    idx2 = fcol_in_mdf["Reflected_Solar_SW_W_p_m2"]
    idx3 = fcol_in_mdf["LW_HI_cloud_radiation_W_p_m2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] - mdf[rowi, idx3]

    # Output_last_year[region] = SMOOTHI ( Optimal_real_output[region] , One_year , Output_last_year_in_1980[region] )
    idx1 = fcol_in_mdf["Output_last_year"]
    idx2 = fcol_in_mdf["Optimal_real_output"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j]) / One_year * dt
      )

    # Owner_cash_inflow_with_lending_transactions[region] = Owner_income_after_tax_but_before_lending_transactions[region] + Owner_income_from_lending_activity[region]
    idxlhs = fcol_in_mdf["Owner_cash_inflow_with_lending_transactions"]
    idx1 = fcol_in_mdf["Owner_income_after_tax_but_before_lending_transactions"]
    idx2 = fcol_in_mdf["Owner_income_from_lending_activity"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j]

    # Owner_wealth_accumulation_fraction[region] = WACC_fraction[region] * Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation[region]
    idxlhs = fcol_in_mdf["Owner_wealth_accumulation_fraction"]
    idx1 = fcol_in_mdf["WACC_fraction"]
    idx2 = fcol_in_mdf["Fraction_of_owner_income_left_for_consumption_or_wealth_accumulation"
    ]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Owner_wealth_accumulating[region] = Owner_cash_inflow_seasonally_adjusted[region] * Owner_wealth_accumulation_fraction[region]
    idxlhs = fcol_in_mdf["Owner_wealth_accumulating"]
    idx1 = fcol_in_mdf["Owner_cash_inflow_seasonally_adjusted"]
    idx2 = fcol_in_mdf["Owner_wealth_accumulation_fraction"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Release_of_Montreal_gases = Montreal_gases_emissions / UNIT_conversion_to_M
    idxlhs = fcol_in_mdf["Release_of_Montreal_gases"]
    idx1 = fcol_in_mdf["Montreal_gases_emissions"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / UNIT_conversion_to_M

    # pb_Ozone_depletion = Release_of_Montreal_gases * Effect_of_population_on_forest_degradation_and_biocapacity
    idxlhs = fcol_in_mdf["pb_Ozone_depletion"]
    idx1 = fcol_in_mdf["Release_of_Montreal_gases"]
    idx2 = fcol_in_mdf["Effect_of_population_on_forest_degradation_and_biocapacity"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Ozone_depletion_risk_score = IF_THEN_ELSE ( pb_Ozone_depletion > pb_Ozone_depletion_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["Ozone_depletion_risk_score"]
    idx1 = fcol_in_mdf["pb_Ozone_depletion"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > pb_Ozone_depletion_green_threshold, 1, 0
    )

    # Past_Living_conditions_index_with_env_damage[region] = SMOOTH ( Living_conditions_index_with_env_damage[region] , Social_tension_perception_delay )
    idx1 = fcol_in_mdf["Past_Living_conditions_index_with_env_damage"]
    idx2 = fcol_in_mdf["Living_conditions_index_with_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Social_tension_perception_delay
        * dt
      )

    # pb_Air_Pollution_overloading = Smoothed_Urban_aerosol_concentration_future / pb_Urban_aerosol_concentration_green_threshold
    idxlhs = fcol_in_mdf["pb_Air_Pollution_overloading"]
    idx1 = fcol_in_mdf["Smoothed_Urban_aerosol_concentration_future"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / pb_Urban_aerosol_concentration_green_threshold

    # pb_Biodiversity_loss_overloading = Biocapacity_fraction_unused / pb_Biodiversity_loss_green_threshold
    idxlhs = fcol_in_mdf["pb_Biodiversity_loss_overloading"]
    idx1 = fcol_in_mdf["Biocapacity_fraction_unused"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / pb_Biodiversity_loss_green_threshold

    # pb_Forest_degradation_overloading = pb_Forest_degradation / pb_Forest_degradation_green_threshold
    idxlhs = fcol_in_mdf["pb_Forest_degradation_overloading"]
    idx1 = fcol_in_mdf["pb_Forest_degradation"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / pb_Forest_degradation_green_threshold

    # pb_Freshwater_withdrawal_overloading = pb_Freshwater_withdrawal_global / pb_Freshwater_withdrawal_green_threshold
    idxlhs = fcol_in_mdf["pb_Freshwater_withdrawal_overloading"]
    idx1 = fcol_in_mdf["pb_Freshwater_withdrawal_global"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / pb_Freshwater_withdrawal_green_threshold

    # pb_Global_warming_overloading = pb_Global_Warming / pb_Global_Warming_green_threshold
    idxlhs = fcol_in_mdf["pb_Global_warming_overloading"]
    idx1 = fcol_in_mdf["pb_Global_Warming"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / pb_Global_Warming_green_threshold

    # Phosphorous_overloading = Phosphorous_release_global / Phosphorous_PB_green_threshold
    idxlhs = fcol_in_mdf["Phosphorous_overloading"]
    idx1 = fcol_in_mdf["Phosphorous_release_global"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Phosphorous_PB_green_threshold

    # pb_Nutrient_overloading = ( N_pb_overloading + Phosphorous_overloading ) / 2
    idxlhs = fcol_in_mdf["pb_Nutrient_overloading"]
    idx1 = fcol_in_mdf["N_pb_overloading"]
    idx2 = fcol_in_mdf["Phosphorous_overloading"]
    mdf[rowi, idxlhs] = (mdf[rowi, idx1] + mdf[rowi, idx2]) / 2

    # pb_Ocean_acidification_overloading = pb_Ocean_acidification_green_threshold / pb_Ocean_acidification
    idxlhs = fcol_in_mdf["pb_Ocean_acidification_overloading"]
    idx1 = fcol_in_mdf["pb_Ocean_acidification"]
    mdf[rowi, idxlhs] = pb_Ocean_acidification_green_threshold / mdf[rowi, idx1]

    # pb_Ozone_depletion_overloading = pb_Ozone_depletion / pb_Ozone_depletion_green_threshold
    idxlhs = fcol_in_mdf["pb_Ozone_depletion_overloading"]
    idx1 = fcol_in_mdf["pb_Ozone_depletion"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / pb_Ozone_depletion_green_threshold

    # PB_Toxic_entities = Lead_release_global / Lead_PB_green_threshold
    idxlhs = fcol_in_mdf["PB_Toxic_entities"]
    idx1 = fcol_in_mdf["Lead_release_global"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Lead_PB_green_threshold

    # PB_Toxic_risk_score = IF_THEN_ELSE ( Lead_release_global > Lead_PB_green_threshold , 1 , 0 )
    idxlhs = fcol_in_mdf["PB_Toxic_risk_score"]
    idx1 = fcol_in_mdf["Lead_release_global"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(mdf[rowi, idx1] > Lead_PB_green_threshold, 1, 0)

    # pl_to_apl[region] = abs ( MIN ( 0 , Populated_land_gap[region] ) ) / Time_for_urban_land_to_become_abandoned
    idxlhs = fcol_in_mdf["pl_to_apl"]
    idx1 = fcol_in_mdf["Populated_land_gap"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (abs(min(0, mdf[rowi, idx1 + j])) / Time_for_urban_land_to_become_abandoned
      )

    # Planetary_risk = Acidification_risk_score + Air_Pollution_risk_score + Biocapacity_risk_score + Forest_degradation_risk_score + Freshwater_withdrawal_risk_score + Global_warming_risk_score + Nutrient_risk_score + Ozone_depletion_risk_score + PB_Toxic_risk_score
    idxlhs = fcol_in_mdf["Planetary_risk"]
    idx1 = fcol_in_mdf["Acidification_risk_score"]
    idx2 = fcol_in_mdf["Air_Pollution_risk_score"]
    idx3 = fcol_in_mdf["Biocapacity_risk_score"]
    idx4 = fcol_in_mdf["Forest_degradation_risk_score"]
    idx5 = fcol_in_mdf["Freshwater_withdrawal_risk_score"]
    idx6 = fcol_in_mdf["Global_warming_risk_score"]
    idx7 = fcol_in_mdf["Nutrient_risk_score"]
    idx8 = fcol_in_mdf["Ozone_depletion_risk_score"]
    idx9 = fcol_in_mdf["PB_Toxic_risk_score"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      + mdf[rowi, idx2]
      + mdf[rowi, idx3]
      + mdf[rowi, idx4]
      + mdf[rowi, idx5]
      + mdf[rowi, idx6]
      + mdf[rowi, idx7]
      + mdf[rowi, idx8]
      + mdf[rowi, idx9]
    )

    # Populated_land_last_year[region] = SMOOTH3 ( Populated_land[region] , One_year )
    idxin = fcol_in_mdf["Populated_land"]
    idx2 = fcol_in_mdf["Populated_land_last_year_2"]
    idx1 = fcol_in_mdf["Populated_land_last_year_1"]
    idxout = fcol_in_mdf["Populated_land_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Population_last_year[region] = SMOOTH3I ( Population[region] , One_year , Population_in_1979[region] )
    idxlhs = fcol_in_mdf["Population_last_year"]
    idxin = fcol_in_mdf["Population"]
    idx2 = fcol_in_mdf["Population_last_year_2"]
    idx1 = fcol_in_mdf["Population_last_year_1"]
    idxout = fcol_in_mdf["Population_last_year"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Population_over_50_still_working[region] = Cohort_50plus[region] * Fraction_of_population_over_50_still_working[region]
    idxlhs = fcol_in_mdf["Population_over_50_still_working"]
    idx1 = fcol_in_mdf["Cohort_50plus"]
    idx2 = fcol_in_mdf["Fraction_of_population_over_50_still_working"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]

    # Rate_of_hist_volcanic_aerosol_emissions_2000_to_2150_GtVae_py = IF_THEN_ELSE ( zeit > 2008 :AND: zeit < 2150 , Volcanic_aerosols_emissions , 0 )
    idxlhs = fcol_in_mdf["Rate_of_hist_volcanic_aerosol_emissions_2000_to_2150_GtVae_py"
    ]
    idx1 = fcol_in_mdf["Volcanic_aerosols_emissions"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE((zeit > 2008) & (zeit < 2150), mdf[rowi, idx1], 0)

    # Rate_of_hist_volcanic_aerosol_emissions_GtVae_py = IF_THEN_ELSE ( zeit < 2008 , Volcanic_aerosols_emissions , 0 )
    idxlhs = fcol_in_mdf["Rate_of_hist_volcanic_aerosol_emissions_GtVae_py"]
    idx1 = fcol_in_mdf["Volcanic_aerosols_emissions"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(zeit < 2008, mdf[rowi, idx1], 0)

    # Raw_Effect_of_poverty_on_social_tension[region] = Effect_of_poverty_on_social_tension[region] / Effect_of_poverty_on_social_tension_in_1980[region]
    idxlhs = fcol_in_mdf["Raw_Effect_of_poverty_on_social_tension"]
    idx1 = fcol_in_mdf["Effect_of_poverty_on_social_tension"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] / Effect_of_poverty_on_social_tension_in_1980[j]
      )

    # REFOREST_policy_used[region] = REFOREST_policy[region] / 10 * UNIT_conv_to_1_per_yr
    idxlhs = fcol_in_mdf["REFOREST_policy_used"]
    idx1 = fcol_in_mdf["REFOREST_policy"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / 10 * UNIT_conv_to_1_per_yr

    # Reforestation_cutoff_from_lack_of_barren_land[region] = WITH LOOKUP ( Barren_land_which_is_ice_and_snow[region] , ( [ ( 0 , 0 ) - ( 10 , 10 ) ] , ( 0 , 0 ) , ( 10 , 0 ) , ( 20 , 0.06 ) , ( 30 , 0.2 ) , ( 40 , 0.5 ) , ( 50 , 0.8 ) , ( 60 , 0.95 ) , ( 70 , 1 ) ) )
    tabidx = ftab_in_d_table[  "Reforestation_cutoff_from_lack_of_barren_land"]  # fetch the correct table
    idx2 = fcol_in_mdf["Reforestation_cutoff_from_lack_of_barren_land"]  # get the location of the lhs in mdf
    idx3 = fcol_in_mdf["Barren_land_which_is_ice_and_snow"]
    look = d_table[tabidx]
    for j in range(0, 10):
      mdf[rowi, idx2 + j] = GRAPH(mdf[rowi, idx3 + j], look[:, 0], look[:, 1])

    # Reforestation_policy[region] = Forest_land[region] * ( REFOREST_policy_used[region] ) * Reforestation_cutoff_from_lack_of_barren_land[region]
    idxlhs = fcol_in_mdf["Reforestation_policy"]
    idx1 = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["REFOREST_policy_used"]
    idx3 = fcol_in_mdf["Reforestation_cutoff_from_lack_of_barren_land"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] * (mdf[rowi, idx2 + j]) * mdf[rowi, idx3 + j]
      )

    # Renewable_energy_share_in_the_total_final_energy_consumption[region] = El_from_wind_and_PV[region] / ( El_from_all_sources[region] + Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] * Conversion_Mtoe_to_TWh[region] )
    idxlhs = fcol_in_mdf["Renewable_energy_share_in_the_total_final_energy_consumption"]
    idx1 = fcol_in_mdf["El_from_wind_and_PV"]
    idx2 = fcol_in_mdf["El_from_all_sources"]
    idx3 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / (
        mdf[rowi, idx2 + j] + mdf[rowi, idx3 + j] * Conversion_Mtoe_to_TWh[j]
      )

    # Time_to_implement_UN_policies[region] = Normal_Time_to_implement_UN_policies / Smoothed_Reform_willingness[region]
    idxlhs = fcol_in_mdf["Time_to_implement_UN_policies"]
    idx1 = fcol_in_mdf["Smoothed_Reform_willingness"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = Normal_Time_to_implement_UN_policies / mdf[rowi, idx1 + j]

    # RIPLGF_smoothing_time[region] = Time_to_implement_UN_policies[region] + RIPLGF_Addl_time_to_shift_govt_expenditure
    idxlhs = fcol_in_mdf["RIPLGF_smoothing_time"]
    idx1 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + RIPLGF_Addl_time_to_shift_govt_expenditure
      )

    # RoC_in_Forest_land[region] = ( Forest_land[region] - Forest_land_last_year[region] ) / Forest_land_last_year[region] / One_year
    idxlhs = fcol_in_mdf["RoC_in_Forest_land"]
    idx1 = fcol_in_mdf["Forest_land"]
    idx2 = fcol_in_mdf["Forest_land_last_year"]
    idx3 = fcol_in_mdf["Forest_land_last_year"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j] / One_year
      )

    # RoC_in_GDPpp[region] = ( GDPpp_model[region] - GDPpp_model_One_yr_ago[region] ) / GDPpp_model_One_yr_ago[region] / One_year
    idxlhs = fcol_in_mdf["RoC_in_GDPpp"]
    idx1 = fcol_in_mdf["GDPpp_model"]
    idx2 = fcol_in_mdf["GDPpp_model_One_yr_ago"]
    idx3 = fcol_in_mdf["GDPpp_model_One_yr_ago"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j] / One_year
      )

    # RoC_in_Living_conditions_index_with_env_damage[region] = ( Living_conditions_index_with_env_damage[region] - Past_Living_conditions_index_with_env_damage[region] ) / Social_tension_perception_delay
    idxlhs = fcol_in_mdf["RoC_in_Living_conditions_index_with_env_damage"]
    idx1 = fcol_in_mdf["Living_conditions_index_with_env_damage"]
    idx2 = fcol_in_mdf["Past_Living_conditions_index_with_env_damage"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]
      ) / Social_tension_perception_delay

    # RoC_Populated_land[region] = ( Populated_land[region] - Populated_land_last_year[region] ) / Populated_land_last_year[region] / One_year
    idxlhs = fcol_in_mdf["RoC_Populated_land"]
    idx1 = fcol_in_mdf["Populated_land"]
    idx2 = fcol_in_mdf["Populated_land_last_year"]
    idx3 = fcol_in_mdf["Populated_land_last_year"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]) / mdf[rowi, idx3 + j] / One_year
      )

    # Total_CO2_emissionslast_yr[region] = SMOOTH3 ( Total_CO2_emissions[region] , One_year )
    idxin = fcol_in_mdf["Total_CO2_emissions"]
    idx2 = fcol_in_mdf["Total_CO2_emissionslast_yr_2"]
    idx1 = fcol_in_mdf["Total_CO2_emissionslast_yr_1"]
    idxout = fcol_in_mdf["Total_CO2_emissionslast_yr"]
    for j in range(0, 10):
      tigg = rowi
      tce_alt = mdf[rowi - 1, idxin + j]
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idxin + j] - mdf[rowi - 1, idx1 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idx2 + j] = (
        mdf[rowi - 1, idx2 + j]
        + (mdf[rowi - 1, idx1 + j] - mdf[rowi - 1, idx2 + j]) / (One_year / 3) * dt
      )
      mdf[rowi, idxout + j] = (
        mdf[rowi - 1, idxout + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idxout + j]) / (One_year / 3) * dt
      )

    # Scaled_Effect_of_poverty_on_social_tension_and_trust[region] = ( ( Raw_Effect_of_poverty_on_social_tension[region] - 1 ) * Scaling_factor_of_eff_of_poverty_on_social_tension ) + 1
    idxlhs = fcol_in_mdf["Scaled_Effect_of_poverty_on_social_tension_and_trust"]
    idx1 = fcol_in_mdf["Raw_Effect_of_poverty_on_social_tension"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = ((mdf[rowi, idx1 + j] - 1) * Scaling_factor_of_eff_of_poverty_on_social_tension
      ) + 1

    # Temp_driver_to_shift_biomes_degC = Temp_surface / ( ( Temp_surface_1850 - Zero_C_on_K_scale_K ) * K_to_C_conversion ) - 0
    idxlhs = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx1 = fcol_in_mdf["Temp_surface"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / ((Temp_surface_1850 - Zero_C_on_K_scale_K) * K_to_C_conversion)
      - 0
    )

    # Shifting_DESERT_to_GRASS_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , DESERT_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_DESERT_to_GRASS * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_DESERT_to_GRASS_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["DESERT_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] < 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_DESERT_to_GRASS
      * mdf[rowi, idx3],   0, )

    # Shifting_GRASS_to_DESERT_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , GRASS_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_GRASS_to_DESERT * Temp_driver_to_shift_biomes_degC * Temp_driver_to_shift_biomes_degC * ( 1 / Effect_of_humidity_on_shifting_biomes ) , 0 )
    idxlhs = fcol_in_mdf["Shifting_GRASS_to_DESERT_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx4 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx5 = fcol_in_mdf["Effect_of_humidity_on_shifting_biomes"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_GRASS_to_DESERT
      * mdf[rowi, idx3]
      * mdf[rowi, idx4]
      * (1 / mdf[rowi, idx5]),   0, )

    # Shifting_GRASS_to_NF_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , GRASS_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_GRASS_to_NF * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_GRASS_to_NF_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] < 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_GRASS_to_NF
      * mdf[rowi, idx3],   0, )

    # Shifting_GRASS_to_TROP_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , GRASS_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_GRASS_to_TROP * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_GRASS_to_TROP_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["GRASS_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] < 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_GRASS_to_TROP
      * mdf[rowi, idx3],   0, )

    # Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr = Antarctic_ice_area_decrease_Mkm2_pr_yr + Glacial_ice_area_decrease_Mkm2_pr_yr + Greenland_ice_area_decrease_Mkm2_pr_yr
    idxlhs = fcol_in_mdf["Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Antarctic_ice_area_decrease_Mkm2_pr_yr"]
    idx2 = fcol_in_mdf["Glacial_ice_area_decrease_Mkm2_pr_yr"]
    idx3 = fcol_in_mdf["Greenland_ice_area_decrease_Mkm2_pr_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Shifting_ice_on_land_to_tundra_Mkm2_py = Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr
    idxlhs = fcol_in_mdf["Shifting_ice_on_land_to_tundra_Mkm2_py"]
    idx1 = fcol_in_mdf["Shifting_ice_to_tundra_from_detail_ice_on_land_Mkm2_pr_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Shifting_NF_to_GRASS_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , NF_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_NF_to_GRASS * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_NF_to_GRASS_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_NF_to_GRASS
      * mdf[rowi, idx3],   0, )

    # Shifting_NF_to_TROP_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , NF_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_NF_to_TROP * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_NF_to_TROP_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_NF_to_TROP
      * mdf[rowi, idx3],   0, )

    # Shifting_NF_to_Tundra_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , NF_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_on_shifting_NF_to_Tundra * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_NF_to_Tundra_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["NF_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] < 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_on_shifting_NF_to_Tundra
      * mdf[rowi, idx3],   0, )

    # Shifting_TROP_to_GRASS_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , TROP_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_TROP_to_GRASS * Temp_driver_to_shift_biomes_degC * ( 1 / Effect_of_humidity_on_shifting_biomes ) , 0 )
    idxlhs = fcol_in_mdf["Shifting_TROP_to_GRASS_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx4 = fcol_in_mdf["Effect_of_humidity_on_shifting_biomes"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_TROP_to_GRASS
      * mdf[rowi, idx3]
      * (1 / mdf[rowi, idx4]),   0, )

    # Shifting_TROP_to_NF_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC < 0 , TROP_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_on_shifting_TROP_to_NF * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_TROP_to_NF_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["TROP_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] < 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_on_shifting_TROP_to_NF
      * mdf[rowi, idx3],   0, )

    # Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr = Antarctic_ice_area_increase_Mkm2_pr_yr + Glacial_ice_area_increase_Mkm2_pr_yr + Greenland_ice_area_increase_Mkm2_pr_yr
    idxlhs = fcol_in_mdf["Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr"]
    idx1 = fcol_in_mdf["Antarctic_ice_area_increase_Mkm2_pr_yr"]
    idx2 = fcol_in_mdf["Glacial_ice_area_increase_Mkm2_pr_yr"]
    idx3 = fcol_in_mdf["Greenland_ice_area_increase_Mkm2_pr_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] + mdf[rowi, idx2] + mdf[rowi, idx3]

    # Shifting_tundra_to_ice_on_land_Mkm2_py = Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr
    idxlhs = fcol_in_mdf["Shifting_tundra_to_ice_on_land_Mkm2_py"]
    idx1 = fcol_in_mdf["Shifting_tundra_to_ice_from_detail_ice_on_land_Mkm2_pr_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Shifting_Tundra_to_NF_Mkm2_py = IF_THEN_ELSE ( Temp_driver_to_shift_biomes_degC > 0 , Tundra_potential_area_Mkm2 / Ref_shifting_biome_yr * Slope_of_effect_of_temp_shifting_tundra_to_NF * Temp_driver_to_shift_biomes_degC , 0 )
    idxlhs = fcol_in_mdf["Shifting_Tundra_to_NF_Mkm2_py"]
    idx1 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    idx2 = fcol_in_mdf["Tundra_potential_area_Mkm2"]
    idx3 = fcol_in_mdf["Temp_driver_to_shift_biomes_degC"]
    mdf[rowi, idxlhs] = IF_THEN_ELSE(
      mdf[rowi, idx1] > 0,   mdf[rowi, idx2]
      / Ref_shifting_biome_yr
      * Slope_of_effect_of_temp_shifting_tundra_to_NF
      * mdf[rowi, idx3],   0, )

    # Smoothed_RoC_in_GDPpp[region] = SMOOTH ( RoC_in_GDPpp[region] , Time_to_smooth_RoC_in_GDPpp )
    idx1 = fcol_in_mdf["Smoothed_RoC_in_GDPpp"]
    idx2 = fcol_in_mdf["RoC_in_GDPpp"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_RoC_in_GDPpp
        * dt
      )

    # SW_surface_absorption = SW_to_surface - SW_surface_reflection
    idxlhs = fcol_in_mdf["SW_surface_absorption"]
    idx1 = fcol_in_mdf["SW_to_surface"]
    idx2 = fcol_in_mdf["SW_surface_reflection"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] - mdf[rowi, idx2]

    # Time_to_implement_SGRPI_policy[region] = Time_to_implement_UN_policies[region] + Addl_time_to_shift_govt_expenditure
    idxlhs = fcol_in_mdf["Time_to_implement_SGRPI_policy"]
    idx1 = fcol_in_mdf["Time_to_implement_UN_policies"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] + Addl_time_to_shift_govt_expenditure

    # Total_energy_use_per_GDP[region] = ( El_from_all_sources[region] + Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified[region] * Conversion_Mtoe_to_TWh[region] ) / GDP_USED[region]
    idxlhs = fcol_in_mdf["Total_energy_use_per_GDP"]
    idx1 = fcol_in_mdf["El_from_all_sources"]
    idx2 = fcol_in_mdf["Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified"]
    idx3 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = (mdf[rowi, idx1 + j] + mdf[rowi, idx2 + j] * Conversion_Mtoe_to_TWh[j]
      ) / mdf[rowi, idx3 + j]

    # Total_government_revenue_as_a_proportion_of_GDP[region] = Govt_income_after_transfers[region] / GDP_USED[region]
    idxlhs = fcol_in_mdf["Total_government_revenue_as_a_proportion_of_GDP"]
    idx1 = fcol_in_mdf["Govt_income_after_transfers"]
    idx2 = fcol_in_mdf["GDP_USED"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / mdf[rowi, idx2 + j]

    # TROP_Biomass_in_construction_material_left_to_rot = TROP_Biomass_locked_in_construction_material_GtBiomass / TROP_Avg_life_of_building_yr * ( 1 - TROP_Fraction_of_construction_waste_burned_0_to_1 )
    idxlhs = fcol_in_mdf["TROP_Biomass_in_construction_material_left_to_rot"]
    idx1 = fcol_in_mdf["TROP_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / TROP_Avg_life_of_building_yr
      * (1 - TROP_Fraction_of_construction_waste_burned_0_to_1)
    )

    # Use_of_TROP_biomass_for_construction = Use_of_TROP_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_TROP_biomass_for_construction"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_TROP_for_construction_in_2000_GtBiomass
      * mdf[rowi, idx1]
      * UNIT_conversion_1_py
    )

    # TROP_for_construction_use = Use_of_TROP_biomass_for_construction
    idxlhs = fcol_in_mdf["TROP_for_construction_use"]
    idx1 = fcol_in_mdf["Use_of_TROP_biomass_for_construction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # TROP_Living_biomass_rotting = TROP_Living_biomass_GtBiomass / TROP_Avg_life_biomass_yr
    idxlhs = fcol_in_mdf["TROP_Living_biomass_rotting"]
    idx1 = fcol_in_mdf["TROP_Living_biomass_GtBiomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / TROP_Avg_life_biomass_yr

    # TROP_NF_regrowing_after_harvesting_Mkm2_py = TROP_area_harvested_Mkm2 / Time_to_regrow_TROP_yr
    idxlhs = fcol_in_mdf["TROP_NF_regrowing_after_harvesting_Mkm2_py"]
    idx1 = fcol_in_mdf["TROP_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_TROP_yr

    # TROP_regrowing_after_being_burnt_Mkm2_py = TROP_area_burnt / Time_to_regrow_TROP_yr
    idxlhs = fcol_in_mdf["TROP_regrowing_after_being_burnt_Mkm2_py"]
    idx1 = fcol_in_mdf["TROP_area_burnt"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_TROP_yr

    # TROP_regrowing_after_being_clear_cut = TROP_area_clear_cut / ( Time_to_regrow_TROP_yr * 2 )
    idxlhs = fcol_in_mdf["TROP_regrowing_after_being_clear_cut"]
    idx1 = fcol_in_mdf["TROP_area_clear_cut"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / (Time_to_regrow_TROP_yr * 2)

    # TROP_regrowing_after_being_deforested = TROP_area_deforested / Effective_Time_to_regrow_TROP_after_deforesting
    idxlhs = fcol_in_mdf["TROP_regrowing_after_being_deforested"]
    idx1 = fcol_in_mdf["TROP_area_deforested"]
    idx2 = fcol_in_mdf["Effective_Time_to_regrow_TROP_after_deforesting"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / mdf[rowi, idx2]

    # TUNDRA_Biomass_in_construction_material_left_to_rot = TUNDRA_Biomass_locked_in_construction_material_GtBiomass / TUNDRA_Avg_life_of_building_yr * ( 1 - TUNDRA_Fraction_of_construction_waste_burned_0_to_1 )
    idxlhs = fcol_in_mdf["TUNDRA_Biomass_in_construction_material_left_to_rot"]
    idx1 = fcol_in_mdf["TUNDRA_Biomass_locked_in_construction_material_GtBiomass"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1]
      / TUNDRA_Avg_life_of_building_yr
      * (1 - TUNDRA_Fraction_of_construction_waste_burned_0_to_1)
    )

    # Use_of_TUNDRA_biomass_for_construction = Use_of_TUNDRA_for_construction_in_2000_GtBiomass * Effect_of_population_and_urbanization_on_biomass_use * UNIT_conversion_1_py
    idxlhs = fcol_in_mdf["Use_of_TUNDRA_biomass_for_construction"]
    idx1 = fcol_in_mdf["Effect_of_population_and_urbanization_on_biomass_use"]
    mdf[rowi, idxlhs] = (
      Use_of_TUNDRA_for_construction_in_2000_GtBiomass
      * mdf[rowi, idx1]
      * UNIT_conversion_1_py
    )

    # TUNDRA_for_construction_use = Use_of_TUNDRA_biomass_for_construction
    idxlhs = fcol_in_mdf["TUNDRA_for_construction_use"]
    idx1 = fcol_in_mdf["Use_of_TUNDRA_biomass_for_construction"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # TUNDRA_Living_biomass_rotting = TUNDRA_Living_biomass / TUNDRA_Avg_life_biomass_yr
    idxlhs = fcol_in_mdf["TUNDRA_Living_biomass_rotting"]
    idx1 = fcol_in_mdf["TUNDRA_Living_biomass"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / TUNDRA_Avg_life_biomass_yr

    # TUNDRA_regrowing_after_being_burnt_Mkm2_py = TUNDRA_area_burnt_Mkm2 / Time_to_regrow_TUNDRA_yr
    idxlhs = fcol_in_mdf["TUNDRA_regrowing_after_being_burnt_Mkm2_py"]
    idx1 = fcol_in_mdf["TUNDRA_area_burnt_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_TUNDRA_yr

    # TUNDRA_regrowing_after_being_deforested_Mkm2_py = TUNDRA_deforested_Mkm2 / Time_to_regrow_TUNDRA_after_deforesting_yr
    idxlhs = fcol_in_mdf["TUNDRA_regrowing_after_being_deforested_Mkm2_py"]
    idx1 = fcol_in_mdf["TUNDRA_deforested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_TUNDRA_after_deforesting_yr

    # TUNDRA_regrowing_after_harvesting_Mkm2_py = TUNDRA_area_harvested_Mkm2 / Time_to_regrow_TUNDRA_yr
    idxlhs = fcol_in_mdf["TUNDRA_regrowing_after_harvesting_Mkm2_py"]
    idx1 = fcol_in_mdf["TUNDRA_area_harvested_Mkm2"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] / Time_to_regrow_TUNDRA_yr

    # Unemployment_rate_smoothed[region] = SMOOTH ( Unemployment_rate[region] , Time_to_smooth_unemp_rate )
    idx1 = fcol_in_mdf["Unemployment_rate_smoothed"]
    idx2 = fcol_in_mdf["Unemployment_rate"]
    for j in range(0, 10):
      mdf[rowi, idx1 + j] = (
        mdf[rowi - 1, idx1 + j]
        + (mdf[rowi - 1, idx2 + j] - mdf[rowi - 1, idx1 + j])
        / Time_to_smooth_unemp_rate
        * dt
      )

    # Upwelling_from_deep = Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr
    idxlhs = fcol_in_mdf["Upwelling_from_deep"]
    idx1 = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Upwelling_to_surface = Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr
    idxlhs = fcol_in_mdf["Upwelling_to_surface"]
    idx1 = fcol_in_mdf["Flow_of_cold_water_sinking_to_very_bottom_GcubicM_per_yr"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1]

    # Urban_aerosol_concentration_future = Indicated_Urban_aerosol_concentration_future * UAC_reduction_effort
    idxlhs = fcol_in_mdf["Urban_aerosol_concentration_future"]
    idx1 = fcol_in_mdf["Indicated_Urban_aerosol_concentration_future"]
    idx2 = fcol_in_mdf["UAC_reduction_effort"]
    mdf[rowi, idxlhs] = mdf[rowi, idx1] * mdf[rowi, idx2]

    # Volcanic_aerosols_removed_from_stratosphere = Volcanic_aerosols_in_stratosphere / Time_for_volcanic_aerosols_to_remain_in_the_stratosphere
    idxlhs = fcol_in_mdf["Volcanic_aerosols_removed_from_stratosphere"]
    idx1 = fcol_in_mdf["Volcanic_aerosols_in_stratosphere"]
    mdf[rowi, idxlhs] = (
      mdf[rowi, idx1] / Time_for_volcanic_aerosols_to_remain_in_the_stratosphere
    )

    # W_loan_obligations_not_met[region] = Worker_loan_repayment_obligations[region] * ( 1 - Fraction_of_worker_loan_obligations_met[region] )
    idxlhs = fcol_in_mdf["W_loan_obligations_not_met"]
    idx1 = fcol_in_mdf["Worker_loan_repayment_obligations"]
    idx2 = fcol_in_mdf["Fraction_of_worker_loan_obligations_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] * (1 - mdf[rowi, idx2 + j])

    # Worker_cash_inflow[region] = Worker_income_after_tax[region] - Worker_cashflow_to_owners[region]
    idxlhs = fcol_in_mdf["Worker_cash_inflow"]
    idx1 = fcol_in_mdf["Worker_income_after_tax"]
    idx2 = fcol_in_mdf["Worker_cashflow_to_owners"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] - mdf[rowi, idx2 + j]

    # Worker_debt_defaulting[region] = MAX ( 0 , W_loan_obligations_not_met[region] )
    idxlhs = fcol_in_mdf["Worker_debt_defaulting"]
    idx1 = fcol_in_mdf["W_loan_obligations_not_met"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = max(0, mdf[rowi, idx1 + j])

    # Worker_defaults_written_off[region] = Worker_debt_defaults_outstanding[region] / Time_to_write_off_worker_defaults
    idxlhs = fcol_in_mdf["Worker_defaults_written_off"]
    idx1 = fcol_in_mdf["Worker_debt_defaults_outstanding"]
    for j in range(0, 10):
      mdf[rowi, idxlhs + j] = mdf[rowi, idx1 + j] / Time_to_write_off_worker_defaults

    #####
    ##### create the vars Nathalie wants
    ###   Trust in instituations = Global social trust
    print('create Nats vars - shape of mdf_play')
    print(mdf_play_3841_415.shape)
    idx1 = fcol_in_mdf['Social_trust']
    idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
    idxlhs = fcol_in_mdf['Global_social_trust']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 405] = a4
    ### Energy intensity in terms of ...
    idx1 = fcol_in_mdf['Fossil_fuel_for_NON_El_use_that_IS_NOT_being_electrified']
    idx2 = fcol_in_mdf['El_from_all_sources']
    idx3 = fcol_in_mdf['GDP_USED']
    idxlhs = fcol_in_mdf['Energy_intensity_in_terms_of']
    summe1 = 0
    summe2 = 0
    summe3 = 0
    for i in range(0, 10): # get all regions
      summe1 += mdf[rowi, idx1 + i] * Conversion_Mtoe_to_TWh[i]
      summe2 += mdf[rowi, idx2 + i]
      summe3 += mdf[rowi, idx3 + i]
    mdf[rowi, idxlhs] = ((summe1 + summe2) / summe3)
    mdf_play_3841_415[start_tick_in_mdf_play, 406] = mdf[rowi, idxlhs]
    ### Emissions per person = Global average Energy footprint pp
    idx1 = fcol_in_mdf['Energy_footprint_pp']
    idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
    idxlhs = fcol_in_mdf['Global_average_Energy_footprint_pp']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 407] = mdf[rowi, idxlhs]
    ### Perceived global warming = Temp surface anomaly compared to 1850 degC
    idx1 = fcol_in_mdf['Temp_surface_anomaly_compared_to_1850_degC']
#    Perceived_global_warming = mdf[rowi, idx1]
    mdf_play_3841_415[start_tick_in_mdf_play, 408] = mdf[rowi, idx1]
    ### Average well being
    idx1 = fcol_in_mdf['Average_wellbeing_index']
    idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
    idxlhs = fcol_in_mdf['Global_average_Energy_footprint_pp']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 409] = mdf[rowi, idxlhs]
    ### Inequality
    idx1 = fcol_in_mdf['Actual_inequality_index_higher_is_more_unequal']
    idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
    idxlhs = fcol_in_mdf['Global_inequality']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 410] = mdf[rowi, idxlhs]
    ### Social tension
    idx1 = fcol_in_mdf['Smoothed_Social_tension_index_with_trust_effect']
    idx2 = fcol_in_mdf['Regional_population_as_fraction_of_total']
    idxlhs = fcol_in_mdf['Global_social_tension']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 411] = mdf[rowi, idxlhs]
    ### Pop below 15 kpy = Global Population below 2p5 kusd p py
    idx1 = fcol_in_mdf['Fraction_of_population_below_existential_minimum']
    idx2 = fcol_in_mdf['Population']
    idxlhs = fcol_in_mdf['Pop_below_15_kpy']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j] * mdf[rowi, idx2 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 412] = mdf[rowi, idxlhs]
    ### Pop = Global population
    idx1 = fcol_in_mdf['Population']
    idxlhs = fcol_in_mdf['Global_Population']
    a4 = 0
    for j in range(0, 10):
      a4 = a4 + mdf[rowi, idx1 + j]
    mdf[rowi, idxlhs] = a4
    mdf_play_3841_415[start_tick_in_mdf_play, 413] = mdf[rowi, idxlhs]
    idx2 = fcol_in_mdf['Temp_surface_anomaly_compared_to_1850_degC']
    idx1 = fcol_in_mdf['Global_GDPpp_USED']
    mdf_play_3841_415[start_tick_in_mdf_play, 414] = mdf[rowi, idx1]
    mdf_play_3841_415[start_tick_in_mdf_play, 415] = mdf[rowi, idx2]
    
    ##########
    ###        save output variables from normal model (ie wo Nat's variables)
    ##########
    colmdf = 1
    for prr in plot_reg:
      if prr == 'Regenerative_cropland_fraction':
#        print('saving reg-crop_frac')
        pass
      idx = fcol_in_mdf[prr]
      if prr == 'Regenerative_cropland_fraction':
#        print('stimp='+str(start_tick_in_mdf_play)+ ' colmdf='+str(colmdf)+' idx='+str(idx)+ ' zeit='+str(zeit)+' value af')
        pass
      for jk in range(0, 10):
        a2 = mdf[rowi, idx + jk]
        if prr == 'Regenerative_cropland_fraction' and jk == 1:
#          print(a2)
          pass
        mdf_play_3841_415[start_tick_in_mdf_play, colmdf] = a2
        colmdf += 1
    for pgg in plot_glob:
      idx = fcol_in_mdf[pgg]
      a2 = mdf[rowi, idx]
      mdf_play_3841_415[start_tick_in_mdf_play, colmdf] = a2
      colmdf += 1

    start_tick_in_mdf_play += 1

  ##### END loop
  # make sure I save the entire ndarray
  #mdf_new_full = mdf_play_3841_415
  #print(mdf_play_3841_415.shape)
  if howlong == 40:
#    mdf_play = mdf_play_3841_415[0:1920, :]
    row2040 = mdf[480, :]
    amo = anvil.BlobMedia("text/plain",   pickle.dumps(row2040), name='row2040.pkl')
    amo2 = anvil.BlobMedia("text/plain",   pickle.dumps(mdf_play_3841_415), name='full2040.pkl')
    app_tables.game_files.add_row(game_id=game_id,   start_row_data=amo,   mdf_play=amo2,   version=datetime.datetime.now(),   yr=2040, )
  elif howlong == 60:
#   mdf_play = mdf_play_3841_415[0:2560, :]
    row2060 = mdf[640, :]
    amo = anvil.BlobMedia("text/plain",   pickle.dumps(row2060), name='row2060.pkl')
    amo2 = anvil.BlobMedia("text/plain",   pickle.dumps(mdf_play_3841_415), name='full2060.pkl')
    app_tables.game_files.add_row(game_id=game_id,   start_row_data=amo,   mdf_play=amo2,   version=datetime.datetime.now(),   yr=2060, )
  elif howlong == 21:
    row2100 = mdf[1280, :]
    amo = anvil.BlobMedia("text/plain",   pickle.dumps(row2100), name='row2100.pkl')
    amo2 = anvil.BlobMedia("text/plain",   pickle.dumps(mdf_play_3841_415), name='full2100.pkl' )
    app_tables.game_files.add_row(game_id=game_id,   start_row_data=amo,   mdf_play=amo2,   version=datetime.datetime.now(),   yr=2100, )


    return mdf_play, plot_reg, plot_glob


###### run simulation model

###### make mdf_plot_1990_2025_pddf
data = np.load('files/mdf_play_nat.npy')
plt.plot(data[0])
plt.show()