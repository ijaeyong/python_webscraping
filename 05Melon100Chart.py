# melon100 chart
# 100곡 노래의 제목과 SongID 추출해서 .list에 저장하기
# 100곡 노래의 상세정보를 추출해서 list와 dict에 저장해서 json 파일로 저장
# json 파일을 load하여 Pandas의 DataFrame에 저장하기
# DataFrame 객체를 DB에 Table로 저장하기

import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.melon.com/chart/index.htm'

req_header_dict = {
    # 요청헤더 : 브라우저정보
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}

res = requests.get(url, headers=req_header_dict)
print(res.status_code)

if res.ok:
    html = res.text
    # print(html)  # 해당페이지의 소스보기 할 때, 나오는 코드
    soup = BeautifulSoup(html, 'html.parser')
    print(len(soup.select("div#tb_list tr a[href*='playSong']")))
    a_tags = soup.select("div#tb_list tr a[href*='playSong']")
    song_list = []
    for idx, a_tag in enumerate(a_tags, 1):
        song_dict = {}
        song_title = a_tag.text
        song_dict['song_title'] = song_title

        href_value = a_tag['href']
        # print(href_value)
        # print(idx, song_title)
        matched = re.search(r'(\d+)\);', href_value)
        if matched:
            # print(matched.group(0), matched.group(1)) 뭐가 필요한지 보기
            song_id = matched.group(1)
            song_dict['song_id'] = song_id
            song_detail_url = f'https://www.melon.com/song/detail.htm?songId={song_id}'
            song_dict['song_detail_url'] = song_detail_url
            # print(song_id, song_detail_url)
            # print(song_dict) <-- 이거 다 나옴
            song_list.append(song_dict)

print(len(song_list))

print('---------------------')

song_detail_list = []
for idx, song in enumerate(song_list[:3], 1):
    # 노래1곡의 상세정보를 저장할 딕셔너리dict
    song_detail_dict = {}
    song_detail_url = song['song_detail_url']

    res = requests.get(song_detail_url, headers=req_header_dict)

    print(res.status_code)
    if res.ok:
        soup = BeautifulSoup(res.text, 'html.parser')
        print(idx, song['song_title'])
        song_detail_dict['곡명'] = song['song_title']
        singer_span = soup.select("a[href*='goArtistDetail'] span")
        if singer_span:
            song_detail_dict['가수'] = singer_span[0].text
        # print(song_detail_dict)

        # print(soup.select("div.meta dd"))
        song_dd = soup.select("div.meta dd")
        if song_dd:
            # print(song_dd[0].text)
            song_detail_dict['앨범'] = song_dd[0].text
            song_detail_dict['발매일'] = song_dd[1].text
            song_detail_dict['장르'] = song_dd[2].text

        # print(song_detail_dict)
        # song_detail_list.append(song_detail_dict)

        song_id = song['song_id']
        like_url = f'https://www.melon.com/commonlike/getSongLike.json?contsIds={song_id}]'
        print(like_url)
        like_res = requests.get(like_url, headers=req_header_dict)
        if like_res.ok:
            print(like_res.status_code)
            print(like_res.json())
            print(like_res.json()['contsLike'][0]['SUMMCNT'])
            song_detail_dict['좋아요'] = like_res.json()['contsLike'][0]['SUMMCNT']
        # print(soup.select("div#d_video_summary"))
        lyric_div = soup.select("div#d_video_summary")
        if lyric_div:
            lyric_temp = lyric_div[0].text
            # print(lyric_temp)
            pattern = re.compile(r'[\r\n\t]')
            # /r/n/t 특수문자를 ''(empty string)으로 대체(substitute) 해라
            lyric = pattern.sub('', lyric_temp.strip())
        else:
            lyric = ''
        song_detail_dict['가사'] = lyric

        # print(song_detail_dict)
        song_detail_list.append(song_detail_dict)

print(len(song_detail_list))
song_detail_list[:5]

print('--------------------')
# json 파일로 옮기기
import json

with open('data/songs.json', 'w', encoding='utf-8') as file:
    json.dump(song_detail_list, file)

with open('data/songs.json', encoding='utf-8') as file:
    # contents = file.read()
    song_json = json.loads(file.read())

# print(song_json)   <--표 확인할라고 jsonviewer로 봄

print('---------------------')
# pandas의 dataframe 객체 사용하기
# song_detail_list를 읽어서 DataFrame객체를 생성하는 방법
# DataFrame객체를 생성
import pandas as pd
song_df2 = pd

song_df2 = pd.DataFrame(columns=['곡명', '가수', '앨범', '발매일 ', '장르', '좋아요', '가사'])
# song_df2
# 1개의 row = Series 객체, 1개의 column = Series 객체
for song_detail in song_detail_list:
    print(type(song_detail), song_detail)
    series_obj = pd.Series(song_detail)
    song_df2 = song_df2.append(series_obj, ignore_index=True)

song_df2



# ------다른방법
import pandas as pd

# json file을 읽어서 DataFrame 객체를 생성하는 방법
song_df = pd.read_json('data/songs.json')
print(type(song_df))
song_df.head()

song_df.tail()

print('shape', song_df.shape)
print('columns', song_df.columns)
print('index', song_df.index)
print('values', song_df.values[0:1])