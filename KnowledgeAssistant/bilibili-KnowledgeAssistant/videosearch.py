from fastapi import APIRouter,HTTPException
import requests
import pandas as pd
import json
import re
import os
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from analyse import analyze_single_video_endpoint
from models import *
search= APIRouter()


def clean_html_tags(text):
    """清除HTML标签，只保留文本内容"""
    if not text:
        return "N/A"
    # 使用正则表达式移除<em>标签及其内容
    clean_text = re.sub(r'<em[^>]*>.*?</em>', '', text)
    clean_text = re.sub(r'<em[^>]* class>.*?</em>', '', text)
    # 移除其他可能的HTML标签
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    # 清理多余的空格
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text
    # """使用BeautifulSoup清理HTML标签"""
    # if not text:
    #     return "N/A"
    # soup = BeautifulSoup(text, 'html.parser')
    # return soup.get_text().strip()


def get_bilibili_videos_by_keyword(keyword, page=1, pagesize=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": "buvid3=7C5A5C0D-D9C5-F8D6-4C22-1339CF94A5DB98314infoc; b_nut=1730535199; buvid4=13ED6440-67F3-DA1A-A036-35F2309A1E2498314-024110208-iB7VVWR2nqEBzTQDRnwDJg%3D%3D; _uuid=8BACFED5-2F45-DCE1-610CF-9E76644F33B550450infoc; buvid_fp=a4124ef60191153b20d7d70fbbe3d91b; enable_web_push=DISABLE; DedeUserID=174437502; DedeUserID__ckMd5=94799109cbe66848; rpdid=|(u)ml)JlR~|0J'u~J|lRJu|R; hit-dyn-v2=1; CURRENT_BLACKGAP=0; PVID=1; LIVE_BUVID=AUTO9317337557704045; is-2022-channel=1; CURRENT_QUALITY=80; enable_feed_channel=ENABLE; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; theme-switch-show=SHOWED; SESSDATA=9f57847d%2C1764513375%2C4931d%2A61CjC6fsvAEWHCXQqXg4i6VaDV4nmzgE5rqs5wlMjXN8YYbGJ8dAW6BOIL4Cj6y-2aVRISVkNpLW8zTldLR09vbEFJY3g0Y2JiZTQ5cmFZZ3FZR00yU3FudC1VSmhzbmZDV1pWSFd3amlLWXNSSk0tMXVPa1VVb2tMQmdmZXFkMnFCODFxZC1ab3ZRIIEC; bili_jct=78d34fe822a8ca10fc500016f9933e38; sid=8v3xiseo; fingerprint=99dcdc0c21055fb5317ad2dabb60443a; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTcwMzg4NDIsImlhdCI6MTc1Njc3OTU4MiwicGx0IjotMX0.uFM-SrQhqH-MBBquGZEnqb7_iDlD11XqwqkwmP1UNcg; bili_ticket_expires=1757038782; browser_resolution=1528-738; bp_t_offset_174437502=1108718298196869120; b_lsid=F637F16B_199149061E5; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; CURRENT_FNVAL=4048",
    }
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "search_type": "video",
        "keyword": keyword,
        "page": page,
        "page_size": pagesize
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # 检查请求是否成功
    data = response.json()

    if data.get("code") != 0:
        print(f"API返回错误: {data.get('message')}")
        return None

    return data['data']['result']  # 返回视频列表


def getresponse(url):
    """通过url请求获得响应"""
    headers = {
            # Cookie 用户信息：
            "Cookie": "buvid3=7C5A5C0D-D9C5-F8D6-4C22-1339CF94A5DB98314infoc; b_nut=1730535199; buvid4=13ED6440-67F3-DA1A-A036-35F2309A1E2498314-024110208-iB7VVWR2nqEBzTQDRnwDJg%3D%3D; _uuid=8BACFED5-2F45-DCE1-610CF-9E76644F33B550450infoc; buvid_fp=a4124ef60191153b20d7d70fbbe3d91b; enable_web_push=DISABLE; DedeUserID=174437502; DedeUserID__ckMd5=94799109cbe66848; rpdid=|(u)ml)JlR~|0J'u~J|lRJu|R; hit-dyn-v2=1; CURRENT_BLACKGAP=0; PVID=1; LIVE_BUVID=AUTO9317337557704045; is-2022-channel=1; CURRENT_QUALITY=80; enable_feed_channel=ENABLE; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; theme-switch-show=SHOWED; SESSDATA=9f57847d%2C1764513375%2C4931d%2A61CjC6fsvAEWHCXQqXg4i6VaDV4nmzgE5rqs5wlMjXN8YYbGJ8dAW6BOIL4Cj6y-2aVRISVkNpLW8zTldLR09vbEFJY3g0Y2JiZTQ5cmFZZ3FZR00yU3FudC1VSmhzbmZDV1pWSFd3amlLWXNSSk0tMXVPa1VVb2tMQmdmZXFkMnFCODFxZC1ab3ZRIIEC; bili_jct=78d34fe822a8ca10fc500016f9933e38; sid=8v3xiseo; fingerprint=99dcdc0c21055fb5317ad2dabb60443a; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTcwMzg4NDIsImlhdCI6MTc1Njc3OTU4MiwicGx0IjotMX0.uFM-SrQhqH-MBBquGZEnqb7_iDlD11XqwqkwmP1UNcg; bili_ticket_expires=1757038782; browser_resolution=1528-738; bp_t_offset_174437502=1108718298196869120; b_lsid=F637F16B_199149061E5; bmg_af_switch=1; bmg_src_def_domain=i1.hdslb.com; CURRENT_FNVAL=4048",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "Referer": "https://space.bilibili.com/174437502/favlist?fid=1809407802&ftype=create"
    }
    response = requests.get(url=url, headers=headers)
    return response

def getvideoinfo(url_link):
        """请求视频信息"""
        link = url_link
        response = getresponse(url=link)
        html = response.text
        info = re.findall('<script>window.__playinfo__=(.*?)</script>', html)
        json_data = json.loads(info[0])
        audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
        video_url = json_data['data']['dash']['video'][0]['baseUrl']
        title = re.findall('<title>(.*?)</title>', html)[0]
        # title = re.sub(r'[\\/*?:"<>|]', '', title)
        # title = title.replace('?', '').replace(' ', '_').replace('！', '')   # 移除中文感叹号
        # print(title[0])
        # print(audio_url)
        # print(video_url)
        return title, audio_url, video_url

def save(title, audio_url, video_url):
        """保存数据"""
        audio_content = getresponse(url=audio_url).content
        video_content = getresponse(url=video_url).content
        with open('D:\\video\\' + title + '.mp3', mode='wb') as audio:
            audio.write(audio_content)
        with open('D:\\video\\' + title + '.mp4', mode='wb') as video:
            video.write(video_content)



# 使用函数获取数据
# 这里可以自行输入keyword和page然后调用函数即可。
#搜索视频
@search.get("/{searchname}",response_model=SearchResponse)
async def videosearch(searchname:str):
    videos = get_bilibili_videos_by_keyword(searchname, page=1)
    if not videos:
        raise HTTPException(status_code=404, detail="未获取到视频数据")
    if videos:
        # 提取我们需要的信息
        video_list = []
        for video in videos:
            clean_title = clean_html_tags(video.get('title', 'N/A'))
            video_info = {
                "标题": video.get('title', 'N/A'),
                "UP主": video.get('author', 'N/A'),
                "播放量": video.get('play', 'N/A'),
                "弹幕数": video.get('danmaku', 'N/A'),
                "发布时间": video.get('pubdate', 'N/A'),
                "视频时长": video.get('duration', 'N/A'),
                "视频链接": f"https://www.bilibili.com/video/{video.get('bvid', 'N/A')}",
                "aid": video.get('aid', 'N/A'),
                "bvid": video.get('bvid', 'N/A')
            }
            video_list.append(video_info)

    return {
        "keyword": searchname,
        "videos": video_list,
        "count": len(video_list)
    }
#导出excel
@search.post("/excel")
def vitoex(request: VideoExportRequest):
    try:
        # 转换为DataFrame
        df = pd.DataFrame(request.videos)
        # 确保文件路径存在
        if request.filepath and not os.path.exists(request.filepath):
            os.makedirs(request.filepath, exist_ok=True)
        # 生成文件名
        excel_filename = os.path.join(request.filepath, f"B站_{request.keyword}_搜索列表.xlsx")
        # 保存为Excel文件
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        # 检查文件是否成功创建
        if not os.path.exists(excel_filename):
            raise HTTPException(status_code=500, detail="Excel文件创建失败")

        return f"搜索到的视频列表已保存到 {excel_filename}",excel_filename
        # 返回文件下载响应
        # return FileResponse(
        #     path=excel_filename,
        #     filename=f"B站_{request.keyword}_搜索列表.xlsx",
        #     media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        # )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出Excel时发生错误: {str(e)}")

#下载视频
@search.post("/download")
def video_download(request:VideoExportRequest):
    for video in request.videos:
        url_link=video.get('url')
        title, audio_url, video_url = getvideoinfo(url_link)
        save(title, audio_url, video_url)
#将视频分析
@search.post("/")
def videotoanalyse(list:List[VideoItem]):
    analysis_results = analyze_single_video_endpoint(list)
    return {
        "search_results": list,
        "analysis_results": analysis_results,
    }



