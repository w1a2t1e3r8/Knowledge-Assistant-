<template>
  <div class="search-page">
    <div class="search-header">
      <h2>搜索B站视频</h2>
      <p>输入关键词，发现优质学习内容</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
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
      
      <!-- 高级搜索选项 -->
      <div class="advanced-options">
        <div class="filter-group">
          <label>排序方式：</label>
          <select v-model="sortBy" class="filter-select">
            <option value="pubdate">发布时间</option>
            <option value="click">播放量</option>
            <option value="dm">弹幕数</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>时长：</label>
          <select v-model="durationFilter" class="filter-select">
            <option value="">全部</option>
            <option value="1">短于10分钟</option>
            <option value="2">10-30分钟</option>
            <option value="3">长于30分钟</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div class="results-header">
        <h3>搜索结果 ({{ searchResults.length }})</h3>
        <button @click="analyzeSelected" class="btn btn-primary" :disabled="selectedVideos.length === 0">
          🤖 分析选中视频
        </button>
      </div>

      <div class="results-grid">
        <div
          v-for="video in searchResults"
          :key="video.bvid"
          :class="['video-card', { selected: isSelected(video.bvid) }]"
          @click="toggleSelect(video)"
        >
          <div class="video-thumbnail">
            <img :src="video.pic" :alt="video.title" />
            <div class="video-duration">{{ formatDuration(video.duration) }}</div>
            <div class="select-overlay">
              <div class="select-checkbox">
                {{ isSelected(video.bvid) ? '✓' : '+' }}
              </div>
            </div>
          </div>
          
          <div class="video-info">
            <h4 class="video-title">{{ video.title }}</h4>
            <p class="video-author">UP主: {{ video.author }}</p>
            
            <div class="video-stats">
              <span>👁️ {{ formatNumber(video.play) }}</span>
              <span>💬 {{ formatNumber(video.danmaku) }}</span>
              <span>📅 {{ formatDate(video.pubdate) }}</span>
            </div>
            
            <p class="video-desc">{{ video.description }}</p>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="pagination">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="pagination-btn"
        >
          上一页
        </button>
        
        <span class="pagination-info">
          第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
        </span>
        
        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="pagination-btn"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="hasSearched" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>暂无搜索结果</h3>
      <p>尝试使用不同的关键词或调整筛选条件</p>
    </div>

    <!-- 热门推荐 -->
    <div v-else class="popular-suggestions">
      <h3>热门搜索推荐</h3>
      <div class="suggestions-grid">
        <button
          v-for="suggestion in popularSuggestions"
          :key="suggestion"
          @click="setSearchKeyword(suggestion)"
          class="suggestion-tag"
        >
          {{ suggestion }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const searchKeyword = ref('')
const searchResults = ref([])
const selectedVideos = ref([])
const currentPage = ref(1)
const totalPages = ref(1)
const hasSearched = ref(false)
const sortBy = ref('pubdate')
const durationFilter = ref('')

const popularSuggestions = [
  'Python教程',
  '机器学习',
  '前端开发',
  '数据分析',
  '人工智能',
  'React教程',
  '深度学习',
  '算法入门'
]

const performSearch = async () => {
  if (!searchKeyword.value.trim()) return
  
  hasSearched.value = true
  selectedVideos.value = []
  
  try {
    // 这里调用后端的搜索API
    const response = await fetch(`/api/search?keyword=${encodeURIComponent(searchKeyword.value)}&page=${currentPage.value}&sort=${sortBy.value}&duration=${durationFilter.value}`)
    const data = await response.json()
    
    searchResults.value = data.results || []
    totalPages.value = data.totalPages || 1
    
  } catch (error) {
    console.error('搜索失败:', error)
    searchResults.value = []
  }
}

const toggleSelect = (video) => {
  const index = selectedVideos.value.findIndex(v => v.bvid === video.bvid)
  if (index > -1) {
    selectedVideos.value.splice(index, 1)
  } else {
    selectedVideos.value.push(video)
  }
}

const isSelected = (bvid) => {
  return selectedVideos.value.some(v => v.bvid === bvid)
}

const analyzeSelected = () => {
  if (selectedVideos.value.length === 0) return
  
  // 跳转到分析页面，传递选中的视频数据
  router.push({
    path: '/analysis',
    query: {
      videos: JSON.stringify(selectedVideos.value)
    }
  })
}

const setSearchKeyword = (keyword) => {
  searchKeyword.value = keyword
  performSearch()
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  performSearch()
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const formatDate = (timestamp) => {
  return new Date(timestamp * 1000).toLocaleDateString()
}
</script>

<style scoped>
.search-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-header {
  text-align: center;
  margin-bottom: 3rem;
}

.search-header h2 {
  color: white;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.search-header p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.1rem;
}

.search-box {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 2rem;
  margin-bottom: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.search-input-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  color: #333;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

.search-btn {
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.advanced-options {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
}

.filter-select option {
  background: #2d3748;
  color: white;
}

.search-results {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.results-header h3 {
  color: white;
  font-size: 1.5rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.video-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.video-card:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.15);
}

.video-card.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.video-thumbnail {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.video-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-duration {
  position: absolute;
  bottom: 0.5rem;
  right: 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.select-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(102, 126, 234, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.video-card:hover .select-overlay,
.video-card.selected .select-overlay {
  opacity: 1;
}

.select-checkbox {
  width: 32px;
  height: 32px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.video-info {
  padding: 1rem;
}

.video-title {
  color: white;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.video-author {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.video-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.video-stats span {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.8rem;
}

.video-desc {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.pagination-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: rgba(255, 255, 255, 0.7);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: white;
  margin-bottom: 1rem;
}

.popular-suggestions {
  text-align: center;
  padding: 3rem 2rem;
}

.popular-suggestions h3 {
  color: white;
  margin-bottom: 2rem;
  font-size: 1.5rem;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.suggestion-tag {
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.suggestion-tag:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .search-input-group {
    flex-direction: column;
  }
  
  .advanced-options {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filter-group {
    justify-content: space-between;
  }
  
  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .results-grid {
    grid-template-columns: 1fr;
  }
  
  .suggestions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>