from fastapi import APIRouter, HTTPException
from typing import List,Dict
from models import KnowledgeItem
import uuid

repository = APIRouter()

# 内存中存储知识库项（生产环境应该用数据库）
knowledge_base: Dict[str, KnowledgeItem] = {}


@repository.get("/knowledge", response_model=List[KnowledgeItem])
async def get_knowledge_items():
    """获取所有知识库项"""
    return list(knowledge_base.values())


@repository.post("/knowledge/save")
async def save_to_knowledge(bvid: str, markdown_content: str, title: str, author: str, analysis_type: str):
    """保存分析结果到知识库"""
    knowledge_id = str(uuid.uuid4())

    knowledge_item = KnowledgeItem(
        id=knowledge_id,
        bvid=bvid,
        title=title,
        author=author,
        markdown_content=markdown_content,
        analysis_type=analysis_type
    )

    knowledge_base[knowledge_id] = knowledge_item

    return {
        "message": "保存成功",
        "knowledge_id": knowledge_id,
        "item": knowledge_item
    }


@repository.post("/knowledge/{knowledge_id}/favorite")
async def toggle_favorite(knowledge_id: str):
    """切换收藏状态"""
    if knowledge_id not in knowledge_base:
        raise HTTPException(status_code=404, detail="知识库项不存在")

    knowledge_base[knowledge_id].is_favorite = not knowledge_base[knowledge_id].is_favorite

    return {
        "message": "收藏状态已更新",
        "is_favorite": knowledge_base[knowledge_id].is_favorite
    }


@repository.delete("/knowledge/{knowledge_id}")
async def delete_knowledge_item(knowledge_id: str):
    """删除知识库项"""
    if knowledge_id not in knowledge_base:
        raise HTTPException(status_code=404, detail="知识库项不存在")

    deleted_item = knowledge_base.pop(knowledge_id)

    return {
        "message": "删除成功",
        "deleted_item": deleted_item
    }