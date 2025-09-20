<template>
  <div class="analysis-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载分析详情中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">❌</div>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="retryLoading" class="btn btn-primary">
        重试
      </button>
    </div>

    <!-- 内容区域 -->
    <div v-else-if="analysisData" class="analysis-content">
      <!-- 头部信息 -->
      <div class="analysis-header">
        <div class="header-main">
          <h1>{{ analysisData.videoTitle }}</h1>
          <p class="author">UP主: {{ analysisData.author }}</p>
          <div class="header-meta">
            <span class="meta-item">
              <span class="meta-label">分析时间:</span>
              {{ formatDateTime(analysisData.analyzedAt) }}
            </span>
            <span class="meta-item">
              <span class="meta-label">Token用量:</span>
              {{ analysisData.tokenUsage }} tokens
            </span>
            <span class="meta-item">
              <span class="meta-label">分析状态:</span>
              <span :class="['status-badge', analysisData.status]">
                {{ getStatusText(analysisData.status) }}
              </span>
            </span>
          </div>
        </div>

        <div class="header-actions">
          <button 
            @click="toggleFavorite" 
            class="btn favorite-btn"
            :class="{ active: analysisData.isFavorite }"
          >
            ⭐ {{ analysisData.isFavorite ? '已收藏' : '收藏' }}
          </button>
          <button @click="exportMarkdown" class="btn btn-outline">
            📥 导出Markdown
          </button>
          <button @click="copyToClipboard" class="btn btn-outline">
            📋 复制内容
          </button>
        </div>
      </div>

      <!-- 视频信息卡片 -->
      <div class="video-info-card">
        <div class="video-thumbnail">
          <img :src="analysisData.videoThumbnail" :alt="analysisData.videoTitle" />
          <div class="video-duration">{{ formatDuration(analysisData.duration) }}</div>
        </div>
        
        <div class="video-details">
          <h3>视频信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">BV号:</span>
              <span class="value">{{ analysisData.bvid }}</span>
            </div>
            <div class="detail-item">
              <span class="label">发布时间:</span>
              <span class="value">{{ formatDate(analysisData.publishDate) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">播放量:</span>
              <span class="value">{{ formatNumber(analysisData.playCount) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">弹幕数:</span>
              <span class="value">{{ formatNumber(analysisData.danmakuCount) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">视频链接:</span>
              <a :href="analysisData.videoUrl" target="_blank" class="value link">
                前往B站观看
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Markdown内容区域 -->
      <div class="markdown-section">
        <div class="section-header">
          <h2>AI生成的学习笔记</h2>
          <div class="section-actions">
            <button 
              @click="toggleEditMode" 
              class="btn btn-sm"
              :class="{ active: isEditing }"
            >
              {{ isEditing ? '预览模式' : '编辑模式' }}
            </button>
          </div>
        </div>

        <!-- 编辑模式 -->
        <div v-if="isEditing" class="edit-mode">
          <textarea
            v-model="editedContent"
            class="markdown-editor"
            placeholder="在此编辑Markdown内容..."
            rows="20"
          ></textarea>
          <div class="editor-actions">
            <button @click="saveChanges" class="btn btn-primary">
              保存更改
            </button>
            <button @click="cancelEdit" class="btn btn-outline">
              取消
            </button>
          </div>
        </div>

        <!-- 预览模式 -->
        <div v-else class="preview-mode">
          <div class="markdown-preview" v-html="compiledMarkdown"></div>
        </div>
      </div>

      <!-- 分析统计 -->
      <div class="analysis-stats">
        <h3>分析统计</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisData.tokenUsage }}</div>
              <div class="stat-label">Token用量</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">⏱️</div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisData.analysisTime }}s</div>
              <div class="stat-label">分析耗时</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisData.contentLength }}</div>
              <div class="stat-label">内容长度</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🔗</div>
            <div class="stat-content">
              <div class="stat-number">{{ analysisData.linkCount }}</div>
              <div class="stat-label">参考链接</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 相关推荐 -->
      <div class="related-analysis">
        <h3>相关分析</h3>
        <div class="related-grid">
          <div 
            v-for="item in relatedAnalyses" 
            :key="item.id" 
            class="related-card"
            @click="goToAnalysis(item.id)"
          >
            <h4>{{ item.title }}</h4>
            <p class="author">by {{ item.author }}</p>
            <span class="date">{{ formatDate(item.date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div v-if="analysisData" class="floating-actions">
      <button @click="scrollToTop" class="action-btn" title="返回顶部">
        ⬆️
      </button>
      <button @click="toggleFavorite" class="action-btn" :title="analysisData.isFavorite ? '取消收藏' : '收藏'">
        ⭐
      </button>
      <button @click="exportMarkdown" class="action-btn" title="导出Markdown">
        📥
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const error = ref(null)
const analysisData = ref(null)
const isEditing = ref(false)
const editedContent = ref('')
const originalContent = ref('')

// 模拟数据
const mockAnalysisData = {
  id: '1',
  videoTitle: 'Python数据分析实战教程：从入门到精通',
  author: '数据科学家',
  bvid: 'BV1xxx123456',
  videoUrl: 'https://www.bilibili.com/video/BV1xxx123456',
  videoThumbnail: '/api/placeholder/400/225',
  duration: 1860,
  publishDate: '2024-01-10',
  playCount: 125000,
  danmakuCount: 2345,
  analyzedAt: '2024-01-15T10:30:00',
  tokenUsage: 2450,
  status: 'completed',
  analysisTime: 45,
  contentLength: 2850,
  linkCount: 8,
  isFavorite: true,
  markdownContent: `# Python数据分析实战教程

## 视频概要
本视频全面讲解Python在数据分析中的应用，涵盖数据处理、可视化、统计分析等核心内容。

## 核心知识点

### 1. Pandas数据处理
- DataFrame的基本操作
- 数据清洗与预处理
- 数据聚合与分组

### 2. NumPy数值计算
- 数组操作与广播机制
- 数学函数与统计方法
- 性能优化技巧

### 3. Matplotlib可视化
- 基本图表绘制
- 子图与布局管理
- 样式与主题设置

## 详细内容解析

### 数据处理最佳实践
视频中演示了如何高效处理大型数据集，包括内存优化和并行处理技巧。

### 实战案例
通过真实数据集展示完整的数据分析流程，从数据获取到最终可视化。

## 学习要点总结

1. **基础扎实**: 掌握Pandas和NumPy的核心API
2. **实践导向**: 多动手练习真实案例
3. **性能意识**: 关注代码效率和内存使用
4. **可视化能力**: 学会用图表讲述数据故事

## 相关资源推荐

- [Pandas官方文档](https://pandas.pydata.org/)
- [NumPy用户指南](https://numpy.org/doc/)
- [Matplotlib示例库](https://matplotlib.org/stable/gallery/index.html)

---

*分析生成于 2024-01-15 10:30:00*`
}

const relatedAnalyses = [
  {
    id: '2',
    title: '机器学习基础入门',
    author: 'AI教授',
    date: '2024-01-14'
  },
  {
    id: '3',
    title: 'React高级组件开发',
    author: '前端大神',
    date: '2024-01-13'
  },
  {
    id: '4',
    title: '深度学习实战',
    author: '神经网络专家',
    date: '2024-01-12'
  }
]

onMounted(() => {
  loadAnalysisDetail()
})

const loadAnalysisDetail = async () => {
  try {
    loading.value = true
    error.value = null
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    analysisData.value = mockAnalysisData
    originalContent.value = mockAnalysisData.markdownContent
    editedContent.value = mockAnalysisData.markdownContent
    
  } catch (err) {
    error.value = '加载分析详情失败，请稍后重试'
    console.error('Error loading analysis detail:', err)
  } finally {
    loading.value = false
  }
}

const retryLoading = () => {
  loadAnalysisDetail()
}

const compiledMarkdown = computed(() => {
  return marked(editedContent.value || '')
})

const toggleEditMode = () => {
  isEditing.value = !isEditing.value
  if (isEditing.value) {
    editedContent.value = originalContent.value
  }
}

const saveChanges = async () => {
  try {
    // 模拟保存操作
    await new Promise(resolve => setTimeout(resolve, 500))
    originalContent.value = editedContent.value
    isEditing.value = false
    
    // 显示成功消息
    alert('内容保存成功！')
  } catch (err) {
    alert('保存失败，请重试')
  }
}

const cancelEdit = () => {
  editedContent.value = originalContent.value
  isEditing.value = false
}

const toggleFavorite = async () => {
  if (!analysisData.value) return
  
  try {
    analysisData.value.isFavorite = !analysisData.value.isFavorite
    // 模拟API调用更新收藏状态
    await new Promise(resolve => setTimeout(resolve, 300))
  } catch (err) {
    console.error('Error toggling favorite:', err)
  }
}

const exportMarkdown = () => {
  const content = editedContent.value
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${analysisData.value.videoTitle}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(editedContent.value)
    alert('内容已复制到剪贴板！')
  } catch (err) {
    console.error('Failed to copy:', err)
    alert('复制失败，请手动复制内容')
  }
}

const goToAnalysis = (id) => {
  router.push(`/analysis/${id}`)
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const getStatusText = (status) => {
  const statusMap = {
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return statusMap[status] || status
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
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
  return num.toLocaleString()
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadAnalysisDetail()
  }
})
</script>

<style scoped>
.analysis-detail-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  min-height: 100vh;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 4rem 2rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  color: #2d3748;
  margin-bottom: 1rem;
}

.error-state p {
  color: #718096;
  margin-bottom: 2rem;
}

.analysis-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2rem;
  align-items: start;
  margin-bottom: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-main h1 {
  color: #2d3748;
  font-size: 2.2rem;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.author {
  color: #718096;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.header-meta {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
}

.meta-label {
  font-weight: 600;
  color: #2d3748;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.status-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.processing {
  background: #ffeaa7;
  color: #d63031;
}

.status-badge.failed {
  background: #fee2e2;
  color: #b91c1c;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-width: 200px;
}

.favorite-btn.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.video-info-card {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 2rem;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.video-thumbnail {
  position: relative;
  width: 300px;
  height: 180px;
  border-radius: 8px;
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

.video-details h3 {
  color: #2d3748;
  margin-bottom: 1rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f7fafc;
  border-radius: 6px;
}

.label {
  font-weight: 600;
  color: #2d3748;
}

.value {
  color: #4a5568;
}

.link {
  color: #667eea;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.markdown-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: #f7fafc;
  border-bottom: 1px solid #e2e8f0;
}

.section-header h2 {
  color: #2d3748;
  margin: 0;
}

.markdown-editor {
  width: 100%;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9rem;
  line-height: 1.6;
  resize: vertical;
  min-height: 400px;
}

.markdown-editor:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.editor-actions {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: #f7fafc;
  border-top: 1px solid #e2e8f0;
}

.markdown-preview {
  padding: 2rem;
  line-height: 1.8;
}

.markdown-preview :deep(h1) {
  color: #2d3748;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.markdown-preview :deep(h2) {
  color: #2d3748;
  margin: 2rem 0 1rem 0;
}

.markdown-preview :deep(h3) {
  color: #4a5568;
  margin: 1.5rem 0 0.75rem 0;
}

.markdown-preview :deep(p) {
  color: #4a5568;
  margin-bottom: 1rem;
}

.markdown-preview :deep(ul), 
.markdown-preview :deep(ol) {
  color: #4a5568;
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.markdown-preview :deep(li) {
  margin-bottom: 0.5rem;
}

.markdown-preview :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.markdown-preview :deep(a:hover) {
  text-decoration: underline;
}

.markdown-preview :deep(code) {
  background: #f7fafc;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.markdown-preview :deep(pre) {
  background: #2d3748;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-preview :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #718096;
  font-style: italic;
}

.analysis-stats {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.analysis-stats h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-icon {
  font-size: 2rem;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: #718096;
  font-size: 0.9rem;
  font-weight: 500;
}

.related-analysis {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.related-analysis h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.related-card {
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.related-card:hover {
  background: #edf2f7;
  transform: translateY(-2px);
}

.related-card h4 {
  color: #2d3748;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.related-card .author {
  color: #718096;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.related-card .date {
  color: #a0aec0;
  font-size: 0.8rem;
}

.floating-actions {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 1000;
}

.action-btn {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-outline {
  background: white;
  color: #667eea;
  border-color: #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .analysis-detail-page {
    padding: 1rem;
  }

  .analysis-header {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .header-actions {
    flex-direction: row;
    flex-wrap: wrap;
    min-width: auto;
  }

  .video-info-card {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .video-thumbnail {
    width: 100%;
    height: 200px;
  }

  .header-meta {
    flex-direction: column;
    gap: 1rem;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .related-grid {
    grid-template-columns: 1fr;
  }

  .floating-actions {
    bottom: 1rem;
    right: 1rem;
  }

  .action-btn {
    width: 45px;
    height: 45px;
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .header-main h1 {
    font-size: 1.8rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .editor-actions {
    flex-direction: column;
  }
}
</style>