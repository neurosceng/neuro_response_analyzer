# neuro_response_analyzer

西川班の解析が手軽に出来るように自分の作成したライブラリを公表する。
参考なり改良してもらえると嬉しい

2024/02/20追記
pip install git+https://github.com/neurosceng/neuro_response_analyzer.git

でinstall出来るようにした。

import neuro_response_analyzer as NRA

として使うようにする。

~~実験データは共用データベース(Bmistation2)に順次追記していく予定~~    
→Bmistation2 share/ozeki/experiment_data  -->純音関係のデータ   
→Bmistation2 share/ozeki/R5実験データ      -->求愛音関係のデータ   


~~最終的にはpipでやりたいが、最初は更新多めのため、同ディレクトリ下での使用をすることを想定。~~  

ライブラリ材料.ipynbはライブラリの作成時に使用した確認用ファイル   
動作確認.ipynbはライブラリが正常に動作したかの確認。動作の参考に。まんまコピペしたら使えるはず      

##  計測環境
32ch多点電極

##  動作確認環境
windows11


##  各関数解説   

純音は末尾に_tone   
求愛音は末尾に_courtship   
純音と求愛音でcsvの書式が違うため、少し違う   

plot_は描画をするだけで変数は返ってこない。主に確認用   
one_waveは１試行の波形関連   
multi_waveはすべての波形を加重平均したもの   
pre_weighted_averageは指定した数、前の波を遡って加重平均する   

#### 読み込み確認:   
test:Hello Module!と返る   

#### 共通の数値処理:   
td_array:2次配列の変換   
sec_to_num:秒から要素   
num_to_sec:要素から秒   
str_fp:FP1ではなくFP01にする

#### 純音用:   
csv_event_tone   
one_wave_tone   
one_wave_plot_tone   
multi_wave_tone   
multi_wave_plot_tone   
pre_weighted_average_tone

#### 求愛音用:   
csv_event_courtship   
one_wave_courtship   
one_wave_plot_courtship   
multi_wave_courtship   
multi_wave_plot_courtship   
pre_weighted_average_courtship


##  更新情報   
2022/12/29   
version2　アップロード   
純音と求愛音に対応   
v1の波形指定が出来ないことのバグの修正   

2022/1/03   
version3 アップロード 　  
加重平均の関数を追加   

2023/8/31
version7 アプロード
FRAに対応

2024/02/20
git経由でpipを使えるようにした。
