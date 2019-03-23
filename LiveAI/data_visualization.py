import operate_sql

# グラフ化に必要なものの準備
import matplotlib
# matplotlib.rc({'backend': 'TkAgg'})
import matplotlib.pyplot as plt
import _
from _ import p, d, MyObject, MyException
# データの扱いに必要なライブラリ
import pandas as pd
import numpy as np
import datetime as dt
# import seaborn as sns
# sns.set_style("darkgrid")
# plt.style.use('ggplot') 
# font = {'family' : 'Times New Roman'}
# matplotlib.rc('font', **font)
if __name__ == '__main__':
	# operate_sql.save_stats(stats_dict = {'whose': 'sys', 'status': '', 'number': 114513})
	datas = operate_sql.get_stats(whose = 'LiveAI_Umi', status = 'time_line_cnt')
	df = pd.DataFrame({
		'value' : [data[0] for data in datas],
		'time' : [data[1] for data in datas]
		})
	print(df)