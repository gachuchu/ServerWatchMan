# @charset "utf-8"
import os
import sys
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Meiryo'
from functools import reduce
from PIL import Image, ImageDraw, ImageFont
import datetime

# 引数を取得
args = sys.argv
output = args[1]
storage_info = args[2]
smart_folder = args[3]
diskinfo = args[4]
env = args[5]

# 現在日時
now = datetime.datetime.now()
datestr = now.strftime(f'%Y/%m/%d({["月","火","水","木","金","土","日"][now.weekday()]}) %H:%M:%S')

#--------------------------------------------------------------------
# ストレージの空き容量
si = pd.read_csv(storage_info)
si['SizeUsed'] = si['Size'] - si['SizeRemaining']
si['SizeRemainingPer'] = si['SizeRemaining'] / si['Size'] * 100
si['SizeUsedPer'] = si['SizeUsed'] / si['Size'] * 100

fig, ax = plt.subplots(figsize=(7, 2))
figv, axv = plt.subplots(figsize=(7, 2), tight_layout=True)

for idx, dat in si.iterrows():
    def plot(index, value, offset, color, label):
        bar = ax.barh(index, value, left=offset, color=color, edgecolor="#cccccc", linewidth=0.5)
        barv = axv.bar(index, value, bottom=offset, color=color, edgecolor="#cccccc", linewidth=0.5)
        for rect in bar:
            cx = rect.get_x() + rect.get_width() / 2
            cy = rect.get_y() + rect.get_height() / 2
            ax.text(cx, cy, label, color="k", ha="center", va="center", fontsize=8)
        for rect in barv:
            cx = rect.get_x() + rect.get_width() / 2
            cy = rect.get_y() + rect.get_height() / 2
            axv.text(cx, cy, label, color="k", ha="center", va="center", fontsize=8)
        return offset+value
    offset = 0
    offset = plot(dat['DriveLetter']+':'+str(round(dat['Size'] / (1024*1024*1024)))+'GB',
                  dat['SizeUsedPer'],
                  offset,
                  "#2299ee" if dat['SizeUsedPer'] < 70 else "#dda700" if dat['SizeUsedPer'] < 90 else "#ec345c",
                  str(round(dat['SizeUsed'] / (1024*1024*1024), 1))+'GB')
    offset = plot(dat['DriveLetter']+':'+str(round(dat['Size'] / (1024*1024*1024)))+'GB',
                  dat['SizeRemainingPer'],
                  offset,
                  "#eeeeee",
                  str(round(dat['SizeRemaining'] / (1024*1024*1024), 1))+'GB')
ax.minorticks_on()
ax.grid(linewidth=0.5, which='major', axis='x')
ax.grid(linestyle='dotted', linewidth=0.5, which='minor', axis='x')
#ax.set_title(datestr)
axv.minorticks_on()
axv.grid(linewidth=0.5, which='major', axis='y')
axv.grid(linestyle='dotted', linewidth=0.5, which='minor', axis='y')
#axv.set_title(datestr)
axv.yaxis.set_label_position('right')
axv.yaxis.tick_right()
fig.savefig(os.path.splitext(output + '/' + env + os.path.basename(storage_info))[0]+'.png')
figv.savefig(os.path.splitext(output + '/' + env + os.path.basename(storage_info))[0]+'_v.png')

#--------------------------------------------------------------------
# ストレージの健康状態
di = {}
health_img = Image.open('asset/health.png')
health_crop = {
    '正常':(0, 0,   234, 0+81),
    '注意':(0, 113, 234, 113+81),
    '危険':(0, 227, 234, 227+81),
    '不明':(0, 340, 234, 340+81),
    }
# DiskInfoから情報を読み出す
with open(smart_folder+'/'+diskinfo, 'r', encoding='utf-8') as f:
    dilines = f.readlines()
    # Disk List一覧を取得する
    lp = 0
    for lp, line in enumerate(dilines[lp:], lp):
        if line.strip() == '-- Disk List ---------------------------------------------------------------':
            break;
    for lp, line in enumerate(dilines[lp+1:], lp+1):
        disk = line.strip()
        if not disk:
            break;
        disk = disk.rsplit(':', 1)[0].strip()
        di[disk] = {}

    # 各Diskの現在情報を取得する
    for disk in di:
        # 各Disk情報の先頭を探す
        for lp, line in enumerate(dilines[lp+1:], lp+1):
            if disk == line.strip():
                break
        # 各Diskの基本情報を取得する
        info = {}
        for lp, line in enumerate(dilines[lp+2:], lp+2):
            line = line.strip()
            if not line:
                break
            line = line.split(':',1)
            info[line[0].strip()] = line[1].strip()
        di[disk]['info'] = info
        # HDDかSSDか適当に判定
        if 'Rotation Rate' not in info:
            if 'NVM' in info['Interface']:
                di[disk]['type'] = 'NVME'
            else:
                di[disk]['type'] = 'SSD'
        elif 'SSD' in info['Rotation Rate']:
            if 'NVM' in info['Interface']:
                di[disk]['type'] = 'NVME'
            else:
                di[disk]['type'] = 'SSD'
        else:
            di[disk]['type'] = 'HDD'
        # Health Statusを修正
        di[disk]['HealthStatus'] = di[disk]['info']['Health Status'].split('(')[0].strip()
        # DriveLetterを修正
        di[disk]['DriveLetter'] = di[disk]['info']['Drive Letter'].replace(':', '')
        img = Image.new('RGB', (640, 130), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', 30)
        draw.text((20, 2), di[disk]['info']['Drive Letter'] + di[disk]['type'], fill=(0, 0, 0), font=font)
        health = health_img.crop(health_crop[di[disk]['HealthStatus']])
        img.paste(health, (20, 40))
        font = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', 14)
        draw.multiline_text((270, 2),
                            "\n".join(['型番　　　　：'+di[disk]['info']['Model'],
                                       '接続　　　　：'+di[disk]['info']['Interface'],
                                       '電源投入回数：'+di[disk]['info']['Power On Count'],
                                       '使用時間　　：'+di[disk]['info']['Power On Hours'],
                                       '温度　　　　：'+di[disk]['info']['Temperature'],
                                       '健康状態　　：'+di[disk]['info']['Health Status'],
                                       ]),
                            fill=(0, 0, 0),
                            font=font)
        img.save(output + '/' + env + 'health_'+di[disk]['DriveLetter']+'.png')

# 各DiskのSmart情報を取得する
smart_lists = [
    {
    '代替処理済のセクタ数': 'ReallocatedSectorsCount.csv',
    'セクタ代替処理発生回数': 'ReallocationEventCount.csv',
    '代替処理保留中のセクタ数' : 'CurrentPendingSectorCount.csv',
    '回復不可能セクタ数': 'UncorrectableSectorCount.csv',
    },

    {
    '総読み込み量 (ホスト)' : 'HostReads.csv',
    '総書き込み量 (ホスト)' : 'HostWrites.csv',
    '総書き込み量 (NAND）' : 'NandWrites.csv',
    },

    {
    '残り寿命': 'Life.csv',
    },

    {
    '温度': 'Temperature.csv',
    },
    ]

marker_list = ['o','*','v','^','x','p',]
line_list = ['-','--','-.',':',]
last_date = '1900/01/01 00:00:00'

for disk in di:
    # まずはcsvを集計する
    path = smart_folder + '/' + di[disk]['info']['Model'] + di[disk]['info']['Serial Number']
    dfs = []
    count = [0]*len(smart_lists)
    for idx, smart in enumerate(smart_lists):
        for key, csv in smart.items():
            csvpath = path + '/' + csv
            if not os.path.isfile(csvpath):
                continue
            dfs.append(pd.read_csv(csvpath, header=None, names=['Date', key]))
            count[idx] += 1
    di[disk]['smart'] = reduce(lambda x, y: pd.merge(x, y, on='Date', how='outer'), dfs).sort_values(['Date']).fillna(method='ffill').tail(15).reset_index(drop=True)
    di_last_date = di[disk]['smart'].iloc[-1]['Date']
    if di_last_date > last_date:
        last_date = di_last_date

    # もう一度次はグラフ作成する
    fig, ax = plt.subplots(len(smart_lists), 1, tight_layout=True, sharex=True)
    marker = 0
    line = 0
    for idx, smart in enumerate(smart_lists):
        if count[idx] == 0:
            continue
        for key, csv in smart.items():
            if not key in di[disk]['smart']:
                continue
            ax[idx].plot(di[disk]['smart']['Date'], di[disk]['smart'][key], label=key, marker=marker_list[marker], linestyle=line_list[line], linewidth=0.8, markersize=4)
            marker = (marker+1) % len(marker_list)
            line = (line+1) % len(line_list)

        ax[idx].legend(fontsize=7, loc='upper left')
        plt.xticks(di[disk]['smart']['Date'], list(map(lambda x: x[:10], di[disk]['smart']['Date'].tolist())))
        xlabels = ax[idx].get_xticklabels()
        plt.setp(xlabels, rotation=45, fontsize=7)
        y_min, y_max = ax[idx].get_ylim()
        ax[idx].set_ylim(0, y_max*1.5)
        ax[idx].minorticks_on()
        ax[idx].grid(linewidth=0.5, which='major')
        ax[idx].grid(linestyle='dotted', linewidth=0.5, which='minor')
    # グラフを保存
    fig.suptitle(datestr)
    fig.savefig(output + f'/{env}smart_'+di[disk]['DriveLetter']+'.png')

#--------------------------------------------------------------------
# レポート用画像を作成する
for idx, dat in si.iterrows():
    drive_letter = dat['DriveLetter']
    ims = list(map(lambda x: Image.open(output + f'/{env}' + x + drive_letter + '.png'), ['health_', 'smart_']))
    w = max(list(map(lambda x: x.width, ims)))
    h = sum(list(map(lambda x: x.height, ims)))
    img = Image.new('RGB', (w, h), (255, 255, 255))
    ph = 0
    for i in ims:
        img.paste(i, (0, ph))
        ph += i.height
    img.save(output + f'/{env}report_' + drive_letter + '.png')


#--------------------------------------------------------------------
#--------------------------------------------------------------------
# サマリレポートを作成する
# 容量割合の履歴を作成
si['Date'] = last_date
si_csv_path = output + f'/{env}CustomStorageInfo.csv'
if not os.path.isfile(si_csv_path):
    si.to_csv(si_csv_path, index=False)
else:
    si.to_csv(si_csv_path, mode='a', index=False, header=False)

# 容量割合の履歴を取得しなおし
si = pd.read_csv(si_csv_path)
si.drop_duplicates(keep='last', subset=['Date', 'DriveLetter'], inplace=True)
si.reset_index(drop=True, inplace=True)

# 健康状態レポートの作成
hbtn_img = Image.open('asset/health_btn.png')
hbtn_crop = {
    '正常':(0, 46*0, 47, 46*1),
    '注意':(0, 46*1, 47, 46*2),
    '危険':(0, 46*2, 47, 46*3),
    '不明':(0, 46*3, 47, 46*4),
    }
drive_count = len(di)
img = Image.new('RGB', (drive_count * 110, 110+20), (255, 255, 255))
draw = ImageDraw.Draw(img)

font = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', 18)
draw.text((2, -4), datestr, fill=(0, 0, 0), font=font)

for idx, (key, dinfo) in enumerate(sorted(list(di.items()), key=lambda x:x[1]['DriveLetter'])):
    font = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', 38)
    draw.text((2+110*idx, 0+20-2), dinfo['DriveLetter'] + ':', fill=(0, 0, 0), font=font)
    hbtn = hbtn_img.crop(hbtn_crop[dinfo['HealthStatus']])
    img.paste(hbtn, (2+42+110*idx, 2+20))
    font = ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc', 14)
    draw.multiline_text((3+110*idx, 46+2+1+20),
                        "\n".join([dinfo['info']['Power On Count'],
                                   dinfo['info']['Power On Hours'],
                                   dinfo['info']['Temperature'],
                                   ]),
                        fill=(0, 0, 0),
                        font=font)
    draw.line((-2+110*idx, 2+20, -2+110*idx, 110-2+20), fill=(200,200,200),width=1)
img.save(output + f'/{env}health_summry.png')

# Smart情報＋容量情報のグラフ作成
smart_summry_lists = [
    '使用済み容量',
    '代替処理済のセクタ数',
    'セクタ代替処理発生回数',
    '代替処理保留中のセクタ数',
    '回復不可能セクタ数',
    '残り寿命',
    '温度',
    ]

fig, ax = plt.subplots(len(smart_summry_lists), 1, tight_layout=True, sharex=True, figsize=(6,9))
marker = 0
line = 0
dfs_list = {}
date_dfs = pd.DataFrame(columns=['Date'])

# 残容量の情報
dfs = pd.DataFrame(columns=['Date'])
for didx, (key, dinfo) in enumerate(sorted(list(di.items()), key=lambda x:x[1]['DriveLetter'])):
    tmp = si.query(f'DriveLetter == "{dinfo["DriveLetter"]}"').loc[:, ['Date', 'SizeUsedPer']].rename(columns={'SizeUsedPer':dinfo['DriveLetter']})
    dfs = pd.merge(dfs, tmp, on='Date', how='outer')
dfs = dfs.sort_values(['Date'])
dfs = dfs.fillna(method='ffill')
dfs = dfs.fillna(method='bfill')
dfs = dfs.reset_index(drop=True)
dfs_list['使用済み容量'] = dfs
date_dfs = pd.merge(date_dfs, dfs['Date'], on='Date', how='outer')

# Smart情報
for idx, smart in enumerate(smart_summry_lists):
    dfs = pd.DataFrame(columns=['Date'])
    for didx, (key, dinfo) in enumerate(sorted(list(di.items()), key=lambda x:x[1]['DriveLetter'])):
        if smart not in dinfo['smart']:
            continue
        tmp = dinfo['smart'].loc[:, ['Date', smart]].rename(columns={smart:dinfo['DriveLetter']})
        dfs = pd.merge(dfs, tmp, on='Date', how='outer')
    if len(dfs) > 0:
        dfs = dfs.sort_values(['Date'])
        dfs = dfs.fillna(method='ffill')
        dfs = dfs.fillna(method='bfill')
        dfs = dfs.reset_index(drop=True)
        dfs_list[smart] = dfs
        date_dfs = pd.merge(date_dfs, dfs['Date'], on='Date', how='outer')

for idx, key in enumerate(smart_summry_lists):
    dfs_list[key] = pd.merge(date_dfs, dfs_list[key], on='Date', how='outer').sort_values(['Date']).fillna(method='ffill').fillna(method='bfill').tail(15).reset_index(drop=True)
    for didx, (dkey, dinfo) in enumerate(sorted(list(di.items()), key=lambda x:x[1]['DriveLetter'])):
        if dinfo['DriveLetter'] not in dfs_list[key]:
            continue
        ax[idx].plot(dfs_list[key]['Date'],
                     dfs_list[key][dinfo['DriveLetter']],
                     label=dinfo['DriveLetter']+':',
                     marker=marker_list[marker], linestyle=line_list[line], linewidth=0.8, markersize=4)
        marker = (marker+1) % len(marker_list)
        line = (line+1) % len(line_list)
    ax[idx].set_title(key)
    ax[idx].legend(fontsize=7, loc='upper left', bbox_to_anchor=(1.1, 1))
    plt.xticks(dfs_list[key]['Date'], list(map(lambda x: x[:10], dfs_list[key]['Date'].tolist())))
    xlabels = ax[idx].get_xticklabels()
    plt.setp(xlabels, rotation=45, fontsize=7)
    y_min, y_max = ax[idx].get_ylim()
    ax[idx].set_ylim(0, y_max*1.5)
    ax[idx].minorticks_on()
    ax[idx].grid(linewidth=0.5, which='major')
    ax[idx].grid(linestyle='dotted', linewidth=0.5, which='minor')
    ax[idx].yaxis.set_label_position('right')
    ax[idx].yaxis.tick_right()

# グラフを保存
fig.savefig(output + f'/{env}smart_summry.png')

# 使用済み容量情報を再度保存しなおし
si.to_csv(si_csv_path, mode='a', index=False, header=False)

# 健康状態とsmartサマリを合体
ims = list(map(lambda x: Image.open(output + f'/{env}' + x + '.png'), ['health_summry', os.path.splitext(os.path.basename(storage_info))[0]+'_v', 'smart_summry']))
w = max(list(map(lambda x: x.width, ims)))
h = sum(list(map(lambda x: x.height, ims)))
img = Image.new('RGB', (w, h), (255, 255, 255))
ph = 0
for i in ims:
    img.paste(i, (0, ph))
    ph += i.height
img.save(output + f'/{env}report_summry.png')
