# neuro_response_analyzer

西川班の解析が手軽に出来るように自分の作成したライブラリを公表する。
参考なり改良してもらえると嬉しい

import neuro_response_analyzer as NRA

とする。

実験データは共用データベースに

順次追記していく予定

##  計測環境


##  動作確認環境
windows11


##  各関数解説   

純音は末尾に_tone   
求愛音は末尾に_courtship   
純音と求愛音でcsvの書式が違うため、少し違う   

_plot_は描画をするだけで変数は返ってこない。主に確認用   
one_waveは１試行の波形関連   
multi_waveは加重平均したもの   
#### 読み込み確認   
test   

#### 純音用   
csv_event_tone   
one_wave_tone   
one_wave_plot_tone   
multi_wave_tone   
multi_wave_plot_tone   

#### 求愛音用   
csv_event_courtship   
one_wave_courtship   
one_wave_plot_courtship   
multi_wave_courtship   
multi_wave_plot_courtship   



##  更新情報   
2022/12/29
version2　アップロード
純音と求愛音に対応
v1の波形指定が出来ないことのバグの修正
