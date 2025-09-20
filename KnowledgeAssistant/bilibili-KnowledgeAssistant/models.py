from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoBase(BaseModel):
    bvid: str = Field(..., description="B站视频BV号")
    title: str = Field(..., description="视频标题")
    author: str = Field(..., description="UP主名称")


class VideoItem(VideoBase):
    description: Optional[str] = None
    duration: str = Field(..., description="视频时长")
    play: int = 0
    danmaku: int = 0
    pubdate: Optional[datetime] = None
    url: str = Field(..., description="视频链接")
    avid:str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    keyword: str
    max_results: int = 20
    order: str = "totalrank"


class SearchResponse(BaseModel):
    keyword: str
    count: int
    videos: List[VideoItem]


class AnalysisRequest(BaseModel):
    videos: List[VideoItem]
    analysis_type: str = "summary"  # summary, detailed, educational, etc.

class AnalysisResponse(BaseModel):
    status: str
    task_id: Optional[str] = None
    message: str
    results: Optional[List[Dict]] = None

class MarkdownDocument(BaseModel):
    title: str
    content: str
    video_bvid: str
    video_title: str
    author: str
    generated_at: str
    tags: List[str] = []

class AnalysisTask(BaseModel):
    task_id: str
    bvids: List[str]
    status: AnalysisStatus = AnalysisStatus.PENDING
    progress: Dict[str, int] = {}  # bvid -> progress percentage
    results: Dict[str, Optional[str]] = {}  # bvid -> markdown content
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class KnowledgeItem(BaseModel):
    id: str
    bvid: str
    title: str
    author: str
    markdown_content: str
    analysis_type: str
    tags: List[str] = []
    is_favorite: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class VideoExportRequest(BaseModel):
    videos: List[VideoItem]
    keyword: str
    filepath: str = ""
