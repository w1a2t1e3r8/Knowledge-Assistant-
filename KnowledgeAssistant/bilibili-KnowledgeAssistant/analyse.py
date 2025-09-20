from fastapi import APIRouter, HTTPException,BackgroundTasks
from typing import List, Optional, Dict, Any
from models import VideoBase, VideoItem, AnalysisResponse,AnalysisRequest
import requests
import os
from pathlib import Path
from datetime import datetime
import aiofiles
import httpx
import asyncio
from openai import OpenAI

analyse= APIRouter()
# 配置
TONGYI_API_KEY = os.getenv("TONGYI_API_KEY", "your_tongyi_api_key_here")
TONGYI_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
OUTPUT_DIR = Path("./output/markdowns")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 存储分析任务的状态
analysis_tasks = {}



async def extract_bilibili_subtitle(bvid: str) -> Optional[str]:
    """
    尝试提取B站视频字幕
    """
    try:
        # 这里需要实现B站字幕提取逻辑
        # 实际实现可能需要使用B站API或web scraping
        async with httpx.AsyncClient() as client:
            # 示例：尝试获取字幕信息
            subtitle_url = f"https://api.bilibili.com/x/player/v2?bvid={bvid}"
            response = await client.get(subtitle_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # 这里需要根据实际API响应结构解析字幕
                # 如果没有字幕，返回None
                return None

    except Exception as e:
        print(f"提取字幕失败 {bvid}: {e}")
        return None

    return None


async def call_tongyi_qianwen(prompt: str, video_info: Dict) -> str:
    """
    调用通义千问API进行分析
    """

    # client = OpenAI(
    #     # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    #     api_key=os.getenv("TONGYI_API_KEY"),
    #     base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # )
    #
    # completion = client.chat.completions.create(
    #     # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    #     model="qwen-plus",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": "你是谁？"},
    #     ],
    #     # Qwen3模型通过enable_thinking参数控制思考过程（开源版默认True，商业版默认False）
    #     # 使用Qwen3开源版模型时，若未启用流式输出，请将下行取消注释，否则会报错
    #     # extra_body={"enable_thinking": False},
    # )
    # print(completion.model_dump_json())
    try:
        headers = {
            "Authorization": f"Bearer {TONGYI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "qwen-max",
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的知识整理助手，擅长从视频内容中提取关键信息并生成结构化的学习笔记。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "text"
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                TONGYI_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("output", {}).get("text", "分析失败")
            else:
                return f"API调用失败: {response.text}"

    except Exception as e:
        return f"调用通义千问失败: {str(e)}"


async def analyze_single_video(video: VideoItem, analysis_type: str) -> Dict[str, Any]:
    """
    分析单个视频
    """
    try:
        # 1. 尝试提取字幕
        subtitle = await extract_bilibili_subtitle(video.bvid)

        # 2. 构建提示词
        if subtitle:
            prompt = f"""
请分析以下B站视频内容并生成详细的学习笔记：

视频标题：{video.title}
UP主：{video.author}
视频时长：{video.duration}秒
更新时间：{video.update}

视频字幕内容：
{subtitle}

请生成结构化的Markdown文档，包括：
1. 视频概要
2. 核心知识点
3. 详细内容解析
4. 学习要点总结
5. 相关拓展思考
"""
        else:
            prompt = f"""
请基于以下B站视频信息生成学习笔记：

视频标题：{video.title}
UP主：{video.author}
视频时长：{video.duration}秒
更新时间：{video.update}
视频链接：{video.url}

由于无法获取字幕内容，请根据视频标题和基本信息进行分析，生成包含：
1. 基于标题的内容推测
2. 可能的知识点分析
3. 学习建议
4. 相关资源推荐

请用Markdown格式输出。
"""

        # 3. 调用通义千问
        analysis_result = await call_tongyi_qianwen(prompt, video.dict())

        # 4. 生成Markdown文档
        markdown_content = f"""# {video.title} - 学习笔记

**视频信息**
- UP主：{video.author}
- BV号：{video.bvid}
- 时长：{video.duration}秒
- 更新时间：{video.update}
- [观看视频]({video.url})

---

## 内容分析

{analysis_result}

---

## 知识点总结

*自动生成于 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

<!-- 收藏按钮数据 -->
<div class="knowledge-actions" data-bvid="{video.bvid}" data-title="{video.title}" data-author="{video.author}">
    <button onclick="collectKnowledge('{video.bvid}')">收藏知识点</button>
</div>
"""

        # 5. 保存Markdown文件
        filename = f"{video.bvid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = OUTPUT_DIR / filename

        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(markdown_content)

        return {
            "bvid": video.bvid,
            "title": video.title,
            "status": "success",
            "markdown_file": filename,
            "file_path": str(filepath),
            "analysis_type": analysis_type
        }

    except Exception as e:
        return {
            "bvid": video.bvid,
            "title": video.title,
            "status": "error",
            "error": str(e)
        }


async def analyze_videos_task(task_id: str, videos: List[VideoItem], analysis_type: str):
    """
    后台任务：批量分析视频
    """
    results = []

    for video in videos:
        result = await analyze_single_video(video, analysis_type)
        results.append(result)

        # 更新任务进度
        analysis_tasks[task_id] = {
            "status": "processing",
            "progress": f"{len(results)}/{len(videos)}",
            "completed": len(results),
            "total": len(videos),
            "results": results
        }

        # 稍微延迟，避免请求过于频繁
        await asyncio.sleep(1)

    # 标记任务完成
    analysis_tasks[task_id]["status"] = "completed"
#批量分析视频
@analyse.post("/",response_model=AnalysisResponse)
async def analyse_endpoint(videos: List[VideoItem]):
    async def analyze_videos(request: AnalysisRequest, background_tasks: BackgroundTasks):
        """
        分析视频集合并生成Markdown文档
        """
        if not request.videos:
            raise HTTPException(status_code=400, detail="视频列表不能为空")

        # 生成任务ID
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 启动后台任务
        background_tasks.add_task(
            analyze_videos_task,
            task_id,
            request.videos,
            request.analysis_type
        )

        # 初始化任务状态
        analysis_tasks[task_id] = {
            "status": "started",
            "progress": "0/0",
            "completed": 0,
            "total": len(request.videos),
            "results": []
        }

        return AnalysisResponse(
            status="started",
            task_id=task_id,
            message=f"开始分析 {len(request.videos)} 个视频",
            results=None
        )
#分析单个视频
@analyse.post("/single",response_model=AnalysisResponse)
async def analyze_single_video_endpoint(video: VideoItem, analysis_type: str = "summary"):
    """
    分析单个视频（同步返回）
    """
    result = await analyze_single_video(video, analysis_type)

    return AnalysisResponse(
        status="completed",
        message="单个视频分析完成",
        results=[result]
    )
#获取markdown文档
@analyse.post("/markdown/{bvid}")
async def analyse_markdown(bvid: str):
    """
       获取指定视频的Markdown文档
       """
    # 查找最新的Markdown文件
    markdown_files = list(OUTPUT_DIR.glob(f"{bvid}_*.md"))
    if not markdown_files:
        raise HTTPException(status_code=404, detail="未找到对应的Markdown文档")

    # 获取最新的文件
    latest_file = max(markdown_files, key=os.path.getctime)

    async with aiofiles.open(latest_file, 'r', encoding='utf-8') as f:
        content = await f.read()

    return {
        "bvid": bvid,
        "filename": latest_file.name,
        "content": content,
        "generated_at": datetime.fromtimestamp(os.path.getctime(latest_file)).isoformat()
    }
#获取整个markdown文档
@analyse.get("/documents")
async def list_all_documents():
    """
    列出所有已生成的Markdown文档
    """
    documents = []
    for file in OUTPUT_DIR.glob("*.md"):
        documents.append({
            "filename": file.name,
            "bvid": file.name.split('_')[0],
            "size": file.stat().st_size,
            "created_at": datetime.fromtimestamp(file.stat().st_ctime).isoformat()
        })

    return {"documents": documents}

# 工具函数
def generate_collect_button(bvid: str, title: str, author: str) -> str:
    """
    生成收藏按钮的HTML代码
    """
    return f'''
<div class="knowledge-item" data-bvid="{bvid}">
    <h3>{title}</h3>
    <p>UP主: {author}</p>
    <button class="collect-btn" onclick="collectKnowledge('{bvid}')">
        📌 收藏到知识库
    </button>
</div>
'''
