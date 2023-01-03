
import scipy.io
import numpy as np
import matplotlib.pyplot as plt
import csv
from tqdm import tqdm 
import json
from scipy import stats
import pandas as pd
import seaborn as sns
import matplotlib as mpl

def test():
    print("Hello Module!!")

def td_array(dual_array):
    #2次元配列のままだと気持ち悪いので１次元に直す
    array = []
    for i in range(len(dual_array)):
        array.append(dual_array[i][0])
    np_array = np.array(array)
    return(np_array)

def sec_to_num(sec,Data):
    ts_step = Data['FP01_ts_step'][0][0]
    return int(sec/ts_step)

def num_to_sec(num,Data):
    ts_step = Data['FP01_ts_step'][0][0]
    return float(num*ts_step)

def str_fp(num):
    if(num < 10):
        str_s = 'FP0' + str(num)
    else:
        str_s = 'FP' + str(num)
    return str_s

######################################################################################################################    
#ここから純音
def csv_event_tone(csv_path,db,frequency):
    #csvを読み込んで音圧と周波数が何番目かを出力する
    csv_df = pd.read_csv(csv_path)
    db_df = csv_df[csv_df.db == db]
    specified_df =db_df[db_df.frequency == frequency]
    #print(specified_df)
    specified_num_list = specified_df.index.values + 1 #dfのindexは0スタート,stampは1スタートなので調整
    return specified_num_list

def one_wave_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path):
    #提示音の名前とchを入れると指定回分の波形を２次元配列で返す。
    #one_wave_list:2次元配列,10回分の波形,sec_axis:X軸-pre[ms]~post[ms]
    specified_num_list = csv_event_tone(csv_path,db,frequency)
    Event_stamp_sec = Event_stamp_raw - Data[str_fp(ch)+"_ts"][0][0]#本当か?
    #イベントの遅延時間補正
    one_wave_list = []
    wave_ch = Data[str_fp(ch)]
    pre_num = sec_to_num(pre,Data)
    post_num = sec_to_num(post,Data)
    sec_axis = [i for i in range(-pre_num,post_num)]
    for i,l in enumerate(specified_num_list):
        new_event_time = Event_stamp_sec[l]
        new_event_time_num = sec_to_num(new_event_time,Data)
        one_wave_data = td_array(wave_ch[new_event_time_num-pre_num:new_event_time_num+post_num])
        one_wave_list.append(one_wave_data)
        if(i == trial_num-1):break
    one_wave_np = np.array(one_wave_list)
    #returnにどこがトリガーか入れる?
    return one_wave_np,sec_axis

def one_wave_plot_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path):
    #提示音の名前とchを入れると指定回分の波形を２次元配列で返す。
    #one_wave_list:2次元配列,10回分の波形,sec_axis:X軸-pre[ms]~post[ms]
    specified_num_list = csv_event_tone(csv_path,db,frequency)
    Event_stamp_sec = Event_stamp_raw - Data[str_fp(ch)+"_ts"][0][0]#本当か?
    #イベントの遅延時間補正
    one_wave_list = []
    wave_ch = Data[str_fp(ch)]
    pre_num = sec_to_num(pre,Data)
    post_num = sec_to_num(post,Data)
    sec_axis = [i for i in range(-pre_num,post_num)]
    for i,l in enumerate(specified_num_list):
        new_event_time = Event_stamp_sec[l]
        new_event_time_num = sec_to_num(new_event_time,Data)
        one_wave_data = td_array(wave_ch[new_event_time_num-pre_num:new_event_time_num+post_num])
        one_wave_list.append(one_wave_data)
        plt.plot(sec_axis,one_wave_data)#デバッグ
        if(i == trial_num-1):break
    one_wave_np = np.array(one_wave_list)
    
def multi_wave_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path):
    #trial_num回(例えば10回)加算平均したものを返す
    one_wave_np,sec_axis = one_wave_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path)
    if(len(one_wave_np) < trial_num):
        print("試行回数が指定より不足しています")#エラー文
    else:
        weight_average = one_wave_np[0]
        for i in range(int(trial_num)):
            if(i == 0):pass#初期化対策
            else:weight_average = weight_average + one_wave_np[i]
            
        weight_average = weight_average /  int(trial_num)
        return weight_average,sec_axis
    
def multi_wave_plot_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path):
    #trial_num回(例えば10回)加算平均したものを返す
    one_wave_np,sec_axis = one_wave_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path)
    if(len(one_wave_np) < trial_num):
        print("試行回数が指定より不足しています")#エラー文
    else:
        weight_average = one_wave_np[0]
        for i in range(int(trial_num)):
            if(i == 0):pass#初期化対策
            else:weight_average = weight_average + one_wave_np[i]
            
        weight_average = weight_average /  int(trial_num)
        plt.axvline(x=0, color='r')
        plt.plot(sec_axis,weight_average)
        
def pre_weighted_average_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,pre_num,csv_path):
    #指定した数、その試行と試行前の波形を加重平均して返す。返しは二重配列になる。
    #pre_num:加重平均の数、全部の波形の数が10としてpre_numが3の時、返す配列は7個
    weighted_average_list = []
    one_wave_np,sec_axis = one_wave_tone(Data,Event_stamp_raw,pre,post,ch,db,frequency,trial_num,csv_path)
    for i in range(len(one_wave_np)):
        if(i < pre_num):pass#3試行平均するとき全体の1試行目だと前に3個無いのでpass
        else:
            for j in range(pre_num):
                if(j == 0):weight_average = one_wave_np[i]
                else:weight_average = weight_average + one_wave_np[i-j]
        
            weight_average_one = weight_average /  int(trial_num)
            weighted_average_list.append(weight_average_one)
    return weighted_average_list,sec_axis

######################################################################################################################    
#ここから求愛音
#求愛音の冠詞はcourtshipと置く
def csv_event_courtship(csv_path,sound_name):
    #csvを読み込んで音圧と周波数が何番目かを出力する
    csv_df = pd.read_csv(csv_path, names=('index', 'name', 'duration'))
    specified_num_list = []
    #specified_df_df = csv_df[csv_df.0 == sound_name]
    for i in range(len(csv_df)):
        if(csv_df["name"][i] == sound_name):
            specified_num_list.append(i)
    return specified_num_list

def one_wave_courtship(Data,Event_stamp_raw,pre,post,sound_name,ch,trial_num,csv_path):
    #提示音の名前とchを入れると指定回分の波形を２次元配列で返す。
    #one_wave_list:2次元配列,10回分の波形,sec_axis:X軸-pre[ms]~post[ms]
    specified_num_list = csv_event_courtship(csv_path,sound_name)
    Event_stamp_sec = Event_stamp_raw - Data[str_fp(ch)+"_ts"][0][0]#本当か?
    #イベントの遅延時間補正
    one_wave_list = []
    wave_ch = Data[str_fp(ch)]
    pre_num = sec_to_num(pre,Data)
    post_num = sec_to_num(post,Data)
    sec_axis = [i for i in range(-pre_num,post_num)]
    for i,l in enumerate(specified_num_list):
        new_event_time = Event_stamp_sec[l]
        new_event_time_num = sec_to_num(new_event_time,Data)
        one_wave_data = td_array(wave_ch[new_event_time_num-pre_num:new_event_time_num+post_num])
        one_wave_list.append(one_wave_data)
        if(i == trial_num-1):break
    one_wave_np = np.array(one_wave_list)
    #returnにどこがトリガーか入れる?
    return one_wave_np,sec_axis

def one_wave_plot_courtship(Data,Event_stamp_raw,pre,post,sound_name,ch,trial_num,csv_path):
    
    #提示音の名前とchを入れると指定回分の波形を２次元配列で返す。
    #one_wave_list:2次元配列,10回分の波形,sec_axis:X軸-pre[ms]~post[ms]
    specified_num_list = csv_event_courtship(csv_path,sound_name)
    Event_stamp_sec = Event_stamp_raw - Data[str_fp(ch)+"_ts"][0][0]#本当か?
    #イベントの遅延時間補正
    one_wave_list = []
    wave_ch = Data[str_fp(ch)]
    pre_num = sec_to_num(pre,Data)
    post_num = sec_to_num(post,Data)
    sec_axis = [i for i in range(-pre_num,post_num)]
    for i,l in enumerate(specified_num_list):
        new_event_time = Event_stamp_sec[l]
        new_event_time_num = sec_to_num(new_event_time,Data)
        one_wave_data = td_array(wave_ch[new_event_time_num-pre_num:new_event_time_num+post_num])
        one_wave_list.append(one_wave_data)
        plt.plot(sec_axis,one_wave_data)
        if(i == trial_num-1):break
    one_wave_np = np.array(one_wave_list)
    #returnにどこがトリガーか入れる?

def multi_wave_courtship(Data,Event_stamp_raw,pre,post,ch,sound_name,trial_num,csv_path):
    #trial_num回(例えば10回)加算平均したものを返す
    one_wave_np,sec_axis = one_wave_courtship(Data,Event_stamp_raw,pre,post,sound_name,ch,trial_num,csv_path)
    
    weight_average = one_wave_np[0]
    for i in range(int(trial_num)):
        if(i == 0):pass#初期化対策
        else:weight_average = weight_average + one_wave_np[i]

    weight_average = weight_average /  int(trial_num)
    return weight_average,sec_axis

def multi_wave_plot_courtship(Data,Event_stamp_raw,pre,post,ch,sound_name,trial_num,csv_path):
    #trial_num回(例えば10回)加算平均したものを返す
    one_wave_np,sec_axis = one_wave_courtship(Data,Event_stamp_raw,pre,post,sound_name,ch,trial_num,csv_path)
    #print("len(one_wave_np):{}".format(len(one_wave_np)))
    #print(trial_num)
    weight_average = one_wave_np[0]
    for i in range(int(trial_num)):
        if(i == 0):pass#初期化対策
        else:weight_average = weight_average + one_wave_np[i]

    weight_average = weight_average /  int(trial_num)
    plt.axvline(x=0, color='r')
    plt.plot(sec_axis,weight_average)
    
def pre_weighted_average_courtship(Data,Event_stamp_raw,pre,post,ch,sound_name,trial_num,pre_num,csv_path):
    #指定した数、その試行と試行前の波形を加重平均して返す。返しは二重配列になる。
    #pre_num:加重平均の数、全部の波形の数が10としてpre_numが3の時、返す配列は7個
    weighted_average_list = []
    one_wave_np,sec_axis = one_wave_courtship(Data,Event_stamp_raw,pre,post,sound_name,ch,trial_num,csv_path)
    for i in range(len(one_wave_np)):
        if(i < pre_num):pass#3試行平均するとき全体の1試行目だと前に3個無いのでpass
        else:
            for j in range(pre_num):
                if(j == 0):weight_average = one_wave_np[i]
                else:weight_average = weight_average + one_wave_np[i-j]
        
            weight_average_one = weight_average /  int(trial_num)
            weighted_average_list.append(weight_average_one)
    return weighted_average_list,sec_axis
