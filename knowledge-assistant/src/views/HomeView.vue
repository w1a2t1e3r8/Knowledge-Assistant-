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
<template>
  <div id="app">
    <!-- 导航栏 -->
   

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="home">
        <!-- 英雄区域 -->
        <section class="hero">
          <div class="hero-content">
            <h2>智能B站知识管理平台</h2>
            <p>一键分析B站视频内容，生成结构化学习笔记，构建个人知识体系</p>
            <div class="hero-actions">
              <router-link to="/search" class="btn btn-primary">
                🎬 开始搜索视频
              </router-link>
              <router-link to="/repository" class="btn btn-secondary">
                📚 查看知识仓库
              </router-link>
            </div>
          </div>
        </section>

        <!-- 核心功能 -->
        <section class="features">
          <h3>核心功能</h3>
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">🔍</div>
              <h4>智能搜索</h4>
              <p>快速搜索B站视频，支持关键词和高级筛选</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">🤖</div>
              <h4>AI分析</h4>
              <p>通义千问深度分析视频内容，提取核心知识点</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📝</div>
              <h4>笔记生成</h4>
              <p>自动生成结构化Markdown学习笔记</p>
            </div>
            <div class="feature-card">
              <div class="feature-icon">📚</div>
              <h4>知识管理</h4>
              <p>构建个人知识体系，支持分类和标签管理</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #2d3748; /* 默认文字颜色 */
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 导航栏样式 */
.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e2e8f0;
  padding: 1rem 0;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.nav-brand h1 {
  color: #2d3748; /* 深灰色 */
  font-size: 1.8rem;
  font-weight: 700;
}



/* 主内容区 */
.main-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* 首页样式 */
.home {
  color: #2d3748; /* 确保文字颜色 */
}

.hero {
  text-align: center;
  padding: 4rem 0;
  margin-bottom: 4rem;
}

.hero-content h2 {
  font-size: 3rem;
  font-weight: 700;
  color: #2d3748; /* 深灰色 */
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.hero-content p {
  font-size: 1.3rem;
  color: #4a5568; /* 中灰色 */
  margin-bottom: 2.5rem;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white !important; /* 确保按钮文字是白色 */
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea !important; /* 按钮文字颜色 */
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white !important;
}

/* 核心功能区域 */
.features {
  margin-bottom: 4rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  padding: 3rem 2rem;
}

.features h3 {
  text-align: center;
  color: #2d3748;
  font-size: 2.2rem;
  margin-bottom: 3rem;
  font-weight: 700;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1000px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  padding: 2.5rem 2rem;
  border-radius: 16px;
  text-align: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 3.5rem;
  margin-bottom: 1.5rem;
  display: block;
}

.feature-card h4 {
  color: #2d3748;
  font-size: 1.4rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.feature-card p {
  color: #718096;
  line-height: 1.6;
  font-size: 1rem;
}

/* 确保所有文字元素都有明确的颜色 */
h1, h2, h3, h4, h5, h6 {
  color: #2d3748; /* 深灰色 */
}

p, span, div {
  color: #4a5568; /* 中灰色 */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-content h2 {
    font-size: 2.2rem;
  }
  
  .hero-content p {
    font-size: 1.1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .hero-content h2 {
    font-size: 1.8rem;
  }
  
  .feature-card {
    padding: 2rem 1.5rem;
  }
  
  .feature-icon {
    font-size: 2.5rem;
  }
}
</style>