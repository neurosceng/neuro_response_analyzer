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

mpl.rcParams['axes.xmargin'] = 0#余白設定
mpl.rcParams['axes.ymargin'] = 0.05#デフォルト

"""
#サンプル
folder_path = r'D:\experiment_data\20220801電気生理'
data_file_path = 'file3npy_evt1930.mat'
csv_file_path = '220801_1959_npyorder_2回目削除済み.csv'
#savepath_fra = '1216_waves_a'
csv_save_path = "0801_npy_2回目.csv"
data_path = folder_path + str('/') + data_file_path
csv_path = folder_path + str('/') + csv_file_path
pre = 0.1 #刺激前の表示時間
post = 0.5 #刺激後の表示時間
ch = 12



Data = scipy.io.loadmat(data_path)
Event_stamp_raw = td_array(Data['EVT01'])
"""

def test():
    print("hello module!!")
    
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

def csv_array(csv_path):
    with open(csv_path, newline='') as f:
        #header = next(csv.reader(f)) 今回はヘッダーは無い
        csvreader = csv.reader(f)
        csv_data = [row for row in csvreader]
        csv_data = td_array(np.array(csv_data))
    return csv_data

def csv_event(csv_path):
    #csvを読み込んで提示音のリストと提示音に対応するイベントの何番目かを出力する
    sound_name = np.unique(csv_array(csv_path))
    stamp_list_all = []
    csv_arr = csv_array(csv_path)
    for i in sound_name:
        #94種
        stamp_list = []
        for j in range(len(csv_array(csv_path))):
            if(str(i) == str(csv_arr[j])):
                stamp_list.append(j)
        stamp_list_all.append(stamp_list)
    stamp_list_all = np.array(stamp_list_all).tolist()
    sound_name_array = np.array(sound_name).tolist()
    print("csv読み込み終了\n")
    return sound_name_array,stamp_list_all

def one_wave(wave_name,ch,csv_path,Data,Event_stamp_raw,pre,post):
    #提示音の名前とchを入れると10(提示)回分の波形を２次元配列で返す。
    #one_wave_list:2次元配列,10回分の波形,sec_axis:X軸-pre[ms]~post[ms]
    sound_name_array,stamp_list_all = csv_event(csv_path)
    wave_num = sound_name_array.index(wave_name)#csvの中の指定したwave_nameの名前のindexを返す
    #print(stamp_list_all[wave_num])
    #10回分のトリガーの回数
    Event_stamp_sec = Event_stamp_raw - Data[str_fp(ch)+"_ts"][0][0]#本当か?
    #イベントの遅延時間補正
    one_wave_list = []
    wave_ch = Data[str_fp(ch)]
    pre_num = sec_to_num(pre,Data)
    post_num = sec_to_num(post,Data)
    sec_axis = [i for i in range(-pre_num,post_num)]
    for i,l in enumerate(stamp_list_all[wave_num]):
        new_event_time = Event_stamp_sec[i]
        new_event_time_num = sec_to_num(new_event_time,Data)
        #print(new_event_time_num)
        one_wave_data = td_array(wave_ch[new_event_time_num-pre_num:new_event_time_num+post_num])
        one_wave_list.append(one_wave_data)
    one_wave_np = np.array(one_wave_list)
    #returnにどこがトリガーか入れる?
    return one_wave_np,sec_axis

def one_wave_plot(wave_name,ch,csv_path,Data,Event_stamp_raw,pre,post):
    #提示音の名前とchを入れると10(提示)回分の波形を２次元配列で返す。
    #one_wave_list:2次元配列,10回分の波形,sec_axis:X軸-pre[ms]~post[ms]
    sound_name_array,stamp_list_all = csv_event(csv_path)
    wave_num = sound_name_array.index(wave_name)#csvの中の指定したwave_nameの名前のindexを返す
    #print(stamp_list_all[wave_num])
    #10回分のトリガーの回数
    Event_stamp_sec = Event_stamp_raw - Data[str_fp(ch)+"_ts"][0][0]#本当か?
    #イベントの遅延時間補正
    one_wave_list = []
    wave_ch = Data[str_fp(ch)]
    pre_num = sec_to_num(pre,Data)
    post_num = sec_to_num(post,Data)
    sec_axis = [i for i in range(-pre_num,post_num)]
    
    for i,l in enumerate(stamp_list_all[wave_num]):
        new_event_time = Event_stamp_sec[i]
        new_event_time_num = sec_to_num(new_event_time,Data)
        #print(new_event_time_num)
        one_wave_data = td_array(wave_ch[new_event_time_num-pre_num:new_event_time_num+post_num])
        plt.plot(sec_axis,one_wave_data)#デバッグ
        one_wave_list.append(one_wave_data)
    one_wave_np = np.array(one_wave_list)
    #returnにどこがトリガーか入れる?
    return one_wave_np,sec_axis

def multi_wave(wave_name,ch,trial_num,csv_path,Data,Event_stamp_raw,pre,post):
    #trial_num回(例えば10回)加算平均したものを返す
    one_wave_np,sec_axis = one_wave(wave_name,ch,csv_path,Data,Event_stamp_raw,pre,post)
    if(len(one_wave_np) < trial_num):
        print("試行回数が指定より不足しています")#エラー文
    else:
        weight_average = one_wave_np[0]
        for i in range(int(trial_num)):
            if(i == 0):pass#初期化対策
            else:weight_average = weight_average + one_wave_np[i]
            
        weight_average = weight_average /  int(trial_num)
        return weight_average,sec_axis

def multi_wave_plot(wave_name,ch,trial_num,csv_path,Data,Event_stamp_raw,pre,post):
    #trial_num回(例えば10回)加算平均したものを返す
    one_wave_np,sec_axis = one_wave(wave_name,ch,csv_path,Data,Event_stamp_raw,pre,post)
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
        return weight_average,sec_axis
    

    
#ここまで波形のプロットと加算平均    
    
if __name__ == '__main__':
    print("これは自作モジュールです")