from fastapi import FastAPI
import uvicorn

app=FastAPI()
from repository import repository
from videosearch import search
from analyse import analyse
app.include_router(repository,prefix="/repository",tags=["知识仓库接口"])
app.include_router(search,prefix="/search",tags=["搜索视频接口"])
app.include_router(analyse,prefix="/analyse",tags=["解析视频接口"])

if __name__ == "__main__":
    uvicorn.run(app,port=8000)