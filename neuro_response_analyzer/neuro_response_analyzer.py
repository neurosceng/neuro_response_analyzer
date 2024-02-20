
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
from scipy.ndimage.filters import gaussian_filter
from IPython.display import clear_output

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
        new_event_time = Event_stamp_sec[l-1]#csvは１から始まっているがEvent_stamp_secは0からなので調整
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
        new_event_time = Event_stamp_sec[l-1]
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


def multi_wave_ch_plot_tone(Data,Event_stamp_raw,pre,post,db,frequency,trial_num,csv_path):
    #32chをchごとに描画する
    electrode_ch = np.array([5,13,21,29,4,12,20,28,6,14,22,30,3,11,19,27,7,15,23,31,2,10,18,26,8,16,24,32,1,9,17,25])
    #np.reshape(electrode_ch, (8, 4))
    fig, ax = plt.subplots(8, 4, figsize=(24, 18))
    #ax3[0, 0].plot(np.sin(x))
    
    for i,l in enumerate(electrode_ch):
        x = i // 4
        y = i % 4 
        weight_average,sec_axis = multi_wave_tone(Data,Event_stamp_raw,pre,post,l,db,frequency,trial_num,csv_path)
        ax[x, y].axvline(x=0, color='r')
        ax[x, y].plot(sec_axis,weight_average)
    plt.show()

def multi_wave_ch_plot_tone_save(Data,Event_stamp_raw,pre,post,db,frequency,trial_num,csv_path):
    #32chをchごとに描画する
    electrode_ch = np.array([5,13,21,29,4,12,20,28,6,14,22,30,3,11,19,27,7,15,23,31,2,10,18,26,8,16,24,32,1,9,17,25])
    #np.reshape(electrode_ch, (8, 4))
    fig, ax = plt.subplots(8, 4, figsize=(24, 18))
    #ax3[0, 0].plot(np.sin(x))
    
    for i,l in enumerate(electrode_ch):
        x = i // 4
        y = i % 4 
        weight_average,sec_axis = multi_wave_tone(Data,Event_stamp_raw,pre,post,l,db,frequency,trial_num,csv_path)
        ax[x, y].axvline(x=0, color='r')
        ax[x, y].plot(sec_axis,weight_average)
    plt.savefig(str(frequency) + ".png")
    plt.clf()
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
        new_event_time = Event_stamp_sec[l-1]
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
        new_event_time = Event_stamp_sec[l-1]
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

#FRA
def csv_read_tone(csv_path):
    df = pd.read_csv(csv_path)
    
    df_list = sorted(df["frequency"].unique())
    return df_list


def FRA_save(mat_path,csv_path,save_path,freq_list):
    
    pre = 0.1 #刺激前の表示時間
    post = 0.2 #刺激後の表示時間
    Data = scipy.io.loadmat(mat_path)
    try:
        Event_stamp_raw = td_array(Data['EVT01'])
    except:
        #except:#EVTが01にも02にも無い
        Event_stamp_raw = td_array(Data['EVT02'])
        
    fra_list = np.zeros([32,6,41])
    ch_list = [i for i in range(1,33)]
    
    freq_list = csv_read_tone(csv_path)
    db_list = np.arange(30, 81, 10)
    fignum_list = [5,13,21,29,4,12,20,28,6,14,22,30,3,11,19,27,7,15,23,31,2,10,18,26,8,16,24,32,1,9,17,25]
    c = 0
    for ch_num,ch in enumerate(ch_list):
        for db_num in range(len(db_list)):
            for freq_num in range(len(freq_list)):
                db = db_list[db_num]
                freq = freq_list[freq_num]
                c+=1

                weight_average,sec_axis = multi_wave_tone(Data,Event_stamp_raw,pre,post,ch,db,freq,19,csv_path)
                #weight_average,sec_axis = multi_wave_tone(ch,db,freq,20,csv_path)
                amp = max(weight_average) - min(weight_average)
                print("{} / {} ".format(c,len(ch_list)*len(db_list)*len(freq_list)))
                print("{} {} {}".format(ch,db,freq))
                fra_list[ch_num, db_num, freq_num] = amp

                clear_output(True)
    sigma = 2.0
    fig = plt.figure(figsize=[12,18])
    for i,fignum in enumerate(fignum_list):
        ax = fig.add_subplot(8,4,i+1)
        fig.subplots_adjust(wspace=0.02,hspace=0.02)
        heatmap = ax.pcolor(gaussian_filter(fra_list[fignum-1],sigma=sigma),cmap='jet')
        ax.set_xticks([0.5,8.5,16.5,24.5,32.5,40.5])
        ax.set_xticklabels([1,2,4,8,16,32])
        ax.set_yticks([0.5,1.5,2.5,3.5,4.5,5.5],minor=False)
        ax.set_yticklabels([30,40,50,60,70,80])
        if i%4 != 0:
            ax.axes.yaxis.set_visible(False)
        if i<28:
            ax.axes.xaxis.set_visible(False)
        ax.set_xlabel('frequency (kHz)')
        ax.set_ylabel('sound pressure (dB SPL)')
    plt.savefig(save_path)
    plt.close()
    plt.clf()