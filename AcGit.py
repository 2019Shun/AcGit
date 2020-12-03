## AtCoderでACしたコードを保存してGitHubにあげる
import urllib.request
import requests, bs4
import json
import os
import re
import time
import subprocess
import datetime

## User Setting

user_name = 'Shun2019'
target_dir = '/home/taka/ws/acgit/atcoder_submission'
wait_time = 0.2

## AtcoderProbremsのAPIを使用
# 提出コード一覧を取得 
url = 'https://kenkoooo.com/atcoder/atcoder-api/results?user=' + user_name
res = requests.get(url)
res.raise_for_status()
sub_list_json = bs4.BeautifulSoup(res.text, "html.parser")
sub_list = json.loads(sub_list_json.getText())

# ACコードのみ抽出
ac_sub_list = [sl for sl in sub_list if sl['result']=='AC']
# ac_sub_list.to_csv("test.csv", index=False)

## 提出コード取得
# 保存先ディレクトリの作成
os.makedirs(target_dir, exist_ok=True)
os.makedirs(os.path.join(target_dir, 'ABC'), exist_ok=True)
os.makedirs(os.path.join(target_dir, 'ARC'), exist_ok=True)
os.makedirs(os.path.join(target_dir, 'AGC'), exist_ok=True)
os.makedirs(os.path.join(target_dir, 'Other'), exist_ok=True)

# 保存済みかチェックして未保存だったらダウンロード
update_flag = False
for ac_sub in ac_sub_list:
    # 保存先サブディレクトリ文字列を作成
    if not re.match(r'abc\d+', ac_sub['contest_id']) is None:
        target_sub_dir = os.path.join('ABC', ac_sub['contest_id'])
    elif not re.match(r'arc\d+', ac_sub['contest_id']) is None:
        target_sub_dir = os.path.join('ARC', ac_sub['contest_id'])
    elif not re.match(r'agc\d+', ac_sub['contest_id']) is None:
        target_sub_dir = os.path.join('AGC', ac_sub['contest_id'])
    else:
        target_sub_dir = os.path.join('Other', ac_sub['contest_id'])

    # 保存先サブディレクトリの作成
    os.makedirs(os.path.join(target_dir, target_sub_dir), exist_ok=True)

    # 保存ファイル名の作成
    if not re.match(r'C\+\+*', ac_sub['language']) is None:
        target_file_name = ac_sub["problem_id"] + ('_%d.cpp' % ac_sub['id'])
    elif not re.match(r'C#*', ac_sub['language']) is None:
        target_file_name = ac_sub["problem_id"] + ('_%d.cs' % ac_sub['id'])
    elif not re.match(r'Py*', ac_sub['language']) is None:
        target_file_name = ac_sub["problem_id"] + ('_%d.py' % ac_sub['id'])
    else:
        target_file_name = ac_sub['problem_id'] + ('_%d.tmp' % ac_sub['id'])

    # ファイルが未保存の場合ダウンロード
    target_file_path = os.path.join(os.path.join(target_dir, target_sub_dir, target_file_name))
    if not os.path.exists(target_file_path):
        # スクレイピングして取り出す
        print('Save as => ' + target_file_path)
        res = requests.get('https://atcoder.jp/contests/%s/submissions/%d' % (ac_sub['contest_id'], ac_sub['id']))
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        elems = soup.select('#submission-code')[0]

        # ファイルに書き込む
        with open(target_file_path, mode='w') as f:
            f.write(elems.getText())

        # 指定時間待つ
        time.sleep(wait_time)
        update_flag = True

# update_flagが立っていた場合，GitHubへpush
# ユーザ名・パスワードの設定は事前にしておく(https://qiita.com/azusanakano/items/8dc1d7e384b00239d4d9)
if update_flag:
    commit_msg = datetime.datetime.now().strftime('%Y%m%d%H%M')
    subprocess.run(['git', '-C', target_dir, 'add', '.'])
    subprocess.run(['git', '-C', target_dir, 'commit', '-am', commit_msg])
    subprocess.run(['git', '-C', target_dir, 'push', 'origin', 'master'])
    print('Finished.')