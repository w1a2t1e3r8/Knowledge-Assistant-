<template>
  <div class="analysis-page">
    <div class="page-header">
      <h2>视频内容分析</h2>
      <p>选择视频进行AI智能分析，生成结构化学习笔记</p>
    </div>

    <!-- 分析方式选择 -->
    <div class="analysis-modes">
      <div class="mode-card" :class="{ active: activeMode === 'search' }" @click="activeMode = 'search'">
        <div class="mode-icon">🔍</div>
        <h4>搜索分析</h4>
        <p>先搜索B站视频再进行分析</p>
      </div>
      <div class="mode-card" :class="{ active: activeMode === 'direct' }" @click="activeMode = 'direct'">
        <div class="mode-icon">📺</div>
        <h4>直接分析</h4>
        <p>输入BV号或链接直接分析</p>
      </div>
      <div class="mode-card" :class="{ active: activeMode === 'batch' }" @click="activeMode = 'batch'">
        <div class="mode-icon">📦</div>
        <h4>批量分析</h4>
        <p>一次分析多个视频内容</p>
      </div>
    </div>

    <!-- 搜索分析模式 -->
    <div v-if="activeMode === 'search'" class="mode-content">
      <div class="search-section">
        <div class="search-input-group">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="输入视频关键词..."
            @keyup.enter="performSearch"
            class="search-input"
          />
          <button @click="performSearch" class="search-btn">
            🔍 搜索
          </button>
        </div>
      </div>

      <div v-if="searchResults.length > 0" class="search-results">
        <h3>搜索结果</h3>
        <div class="video-selection">
          <div
            v-for="video in searchResults"
            :key="video.bvid"
            :class="['video-item', { selected: selectedVideos.includes(video.bvid) }]"
            @click="toggleVideoSelection(video)"
          >
            <div class="video-thumb">
              <img :src="video.pic" :alt="video.title" />
              <div class="video-duration">{{ formatDuration(video.duration) }}</div>
            </div>
            <div class="video-info">
              <h4>{{ video.title }}</h4>
              <p class="author">by {{ video.author }}</p>
              <div class="video-stats">
                <span>👁️ {{ formatNumber(video.play) }}</span>
                <span>💬 {{ formatNumber(video.danmaku) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="analysis-actions">
          <button
            @click="startAnalysis"
            :disabled="selectedVideos.length === 0"
            class="btn btn-primary analyze-btn"
          >
            🤖 开始分析 ({{ selectedVideos.length }})
          </button>
        </div>
      </div>
    </div>

    <!-- 直接分析模式 -->
    <div v-if="activeMode === 'direct'" class="mode-content">
      <div class="direct-input-section">
        <div class="input-group">
          <label for="bvid-input">BV号或视频链接：</label>
          <input
            id="bvid-input"
            v-model="directBvid"
            type="text"
            placeholder="例如：BV1xxx 或 https://www.bilibili.com/video/BV1xxx"
            class="bvid-input"
          />
        </div>
        <button @click="analyzeDirect" :disabled="!directBvid" class="btn btn-primary">
          🔍 分析视频
        </button>
      </div>
    </div>

    <!-- 批量分析模式 -->
    <div v-if="activeMode === 'batch'" class="mode-content">
      <div class="batch-section">
        <div class="upload-area">
          <div class="upload-content">
            <div class="upload-icon">📁</div>
            <h4>上传视频列表</h4>
            <p>支持JSON或CSV格式文件</p>
            <input
              type="file"
              @change="handleFileUpload"
              accept=".json,.csv,.txt"
              class="file-input"
            />
          </div>
        </div>

        <div class="batch-list">
          <h4>待分析视频列表 ({{ batchVideos.length }})</h4>
          <div v-if="batchVideos.length > 0" class="video-list">
            <div v-for="(video, index) in batchVideos" :key="index" class="batch-video-item">
              <span class="video-title">{{ video.title || video.bvid }}</span>
              <button @click="removeBatchVideo(index)" class="remove-btn">×</button>
            </div>
          </div>
          <div v-else class="empty-list">
            <p>暂无视频，请上传文件或手动添加</p>
          </div>

          <div class="batch-actions">
            <button @click="analyzeBatch" :disabled="batchVideos.length === 0" class="btn btn-primary">
              📦 批量分析
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析进度 -->
    <div v-if="analysisProgress" class="analysis-progress">
      <h3>分析进度</h3>
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: analysisProgress.percentage + '%' }"></div>
      </div>
      <div class="progress-info">
        <span>{{ analysisProgress.current }}/{{ analysisProgress.total }} 完成</span>
        <span>{{ analysisProgress.percentage }}%</span>
      </div>
    </div>

    <!-- 分析历史 -->
    <div class="analysis-history">
      <h3>最近分析记录</h3>
      <div v-if="recentAnalyses.length > 0" class="history-list">
        <div v-for="analysis in recentAnalyses" :key="analysis.id" class="history-item">
          <div class="history-info">
            <h4>{{ analysis.title }}</h4>
            <p class="analysis-time">{{ formatTime(analysis.timestamp) }}</p>
            <span :class="['status-badge', analysis.status]">{{ analysis.status }}</span>
          </div>
          <div class="history-actions">
            <button @click="viewAnalysisResult(analysis)" class="btn btn-sm">
              查看结果
            </button>
          </div>
        </div>
      </div>
      <div v-else class="empty-history">
        <p>暂无分析记录</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeMode = ref('search')
const searchKeyword = ref('')
const searchResults = ref([])
const selectedVideos = ref([])
const directBvid = ref('')
const batchVideos = ref([])
const analysisProgress = ref(null)

const recentAnalyses = ref([
  {
    id: 1,
    title: 'Python数据分析教程',
    timestamp: Date.now() - 3600000,
    status: 'completed'
  },
  {
    id: 2,
    title: '机器学习入门',
    timestamp: Date.now() - 86400000,
    status: 'completed'
  }
])

const performSearch = async () => {
  if (!searchKeyword.value.trim()) return
  
  try {
    const response = await fetch(`/api/search?keyword=${encodeURIComponent(searchKeyword.value)}`)
    const data = await response.json()
    searchResults.value = data.results || []
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  }
}

const toggleVideoSelection = (video) => {
  const index = selectedVideos.value.indexOf(video.bvid)
  if (index > -1) {
    selectedVideos.value.splice(index, 1)
  } else {
    selectedVideos.value.push(video.bvid)
  }
}

const startAnalysis = async () => {
  const selectedVideosData = searchResults.value.filter(v => selectedVideos.value.includes(v.bvid))
  
  try {
    analysisProgress.value = {
      current: 0,
      total: selectedVideosData.length,
      percentage: 0
    }

    const response = await fetch('/api/analyze/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ videos: selectedVideosData })
    })

    const result = await response.json()
    
    if (result.task_id) {
      router.push(`/analysis/result/${result.task_id}`)
    }
  } catch (error) {
    console.error('分析失败:', error)
  }
}

const analyzeDirect = async () => {
  // 提取BV号
  let bvid = directBvid.value
  if (bvid.includes('bilibili.com')) {
    const match = bvid.match(/video\/(BV\w+)/)
    if (match) bvid = match[1]
  }

  try {
    const response = await fetch('/api/analyze/direct', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ bvid })
    })

    const result = await response.json()
    if (result.success) {
      router.push(`/analysis/${result.analysis_id}`)
    }
  } catch (error) {
    console.error('直接分析失败:', error)
  }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target.result
      // 解析文件内容
      if (file.name.endsWith('.json')) {
        const data = JSON.parse(content)
        batchVideos.value = Array.isArray(data) ? data : []
      } else if (file.name.endsWith('.csv')) {
        // 简单CSV解析
        const lines = content.split('\n')
        const videos = lines.slice(1).map(line => {
          const [bvid, title] = line.split(',')
          return { bvid, title }
        }).filter(v => v.bvid)
        batchVideos.value = videos
      }
    } catch (error) {
      console.error('文件解析失败:', error)
    }
  }
  reader.readAsText(file)
}

const removeBatchVideo = (index) => {
  batchVideos.value.splice(index, 1)
}

const analyzeBatch = async () => {
  try {
    const response = await fetch('/api/analyze/batch', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ videos: batchVideos.value })
    })

    const result = await response.json()
    if (result.task_id) {
      router.push(`/analysis/result/${result.task_id}`)
    }
  } catch (error) {
    console.error('批量分析失败:', error)
  }
}

const viewAnalysisResult = (analysis) => {
  router.push(`/analysis/${analysis.id}`)
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatNumber = (num) => {
  if (num >= 10000) return (num / 10000).toFixed(1) + '万'
  return num.toString()
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}
</script>

<style scoped>
.analysis-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.page-header h2 {
  color: #2d3748;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.page-header p {
  color: #718096;
  font-size: 1.2rem;
}

.analysis-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.mode-card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid #e2e8f0;
}

.mode-card:hover,
.mode-card.active {
  border-color: #667eea;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
}

.mode-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.mode-card h4 {
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.mode-card p {
  color: #718096;
}

.mode-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 3rem;
  border: 1px solid #e2e8f0;
}

.search-input-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input {
  flex: 1;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-btn {
  padding: 1rem 2rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.video-selection {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.video-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.video-item:hover,
.video-item.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
}

.video-thumb {
  position: relative;
  width: 120px;
  height: 80px;
  flex-shrink: 0;
}

.video-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.video-duration {
  position: absolute;
  bottom: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.video-info h4 {
  color: #2d3748;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.video-info .author {
  color: #718096;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.video-stats {
  display: flex;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #a0aec0;
}

.analysis-actions {
  text-align: center;
}

.analyze-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.direct-input-section {
  max-width: 600px;
  margin: 0 auto;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2d3748;
  font-weight: 500;
}

.bvid-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
}

.bvid-input:focus {
  outline: none;
  border-color: #667eea;
}

.upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  margin-bottom: 2rem;
  cursor: pointer;
  position: relative;
}

.upload-area:hover {
  border-color: #667eea;
}

.upload-content {
  color: #718096;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.batch-list h4 {
  color: #2d3748;
  margin-bottom: 1rem;
}

.video-list {
  margin-bottom: 1.5rem;
}

.batch-video-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.video-title {
  color: #2d3748;
  font-size: 0.9rem;
}

.remove-btn {
  background: #e53e3e;
  color: white;
  border: none;
  border-radius: 4px;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
}

.empty-list,
.empty-history {
  text-align: center;
  padding: 2rem;
  color: #a0aec0;
}

.analysis-progress {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  margin-bottom: 2rem;
  border: 1px solid #e2e8f0;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  transition: width 0.3s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  color: #718096;
  font-size: 0.9rem;
}

.analysis-history {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.history-list {
  margin-top: 1rem;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  margin-bottom: 0.75rem;
}

.history-info h4 {
  color: #2d3748;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.analysis-time {
  color: #718096;
  font-size: 0.8rem;
  margin-bottom: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.completed {
  background: #c6f6d5;
  color: #2d7d32;
}

.status-badge.processing {
  background: #bee3f8;
  color: #2b6cb0;
}

.status-badge.error {
  background: #fed7d7;
  color: #c53030;
}

.history-actions .btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .analysis-modes {
    grid-template-columns: 1fr;
  }
  
  .search-input-group {
    flex-direction: column;
  }
  
  .video-selection {
    grid-template-columns: 1fr;
  }
  
  .video-item {
    flex-direction: column;
    text-align: center;
  }
  
  .video-thumb {
    width: 100%;
    height: 120px;
  }
  
  .history-item {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
}
</style>