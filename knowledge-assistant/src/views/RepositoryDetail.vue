<template>
  <div class="repository-detail-page">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载知识详情中...</p>
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
    <div v-else-if="knowledgeData" class="knowledge-content">
      <!-- 头部信息 -->
      <div class="knowledge-header">
        <div class="breadcrumb">
          <router-link to="/repository" class="breadcrumb-link">
            知识仓库
          </router-link>
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-current">{{ knowledgeData.category }}</span>
        </div>

        <div class="header-main">
          <h1>{{ knowledgeData.title }}</h1>
          <p class="description">{{ knowledgeData.description }}</p>
          
          <div class="header-meta">
            <div class="meta-group">
              <span class="meta-item">
                <span class="meta-icon">👤</span>
                {{ knowledgeData.author }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">📅</span>
                {{ formatDate(knowledgeData.createdAt) }}
              </span>
              <span class="meta-item">
                <span class="meta-icon">👁️</span>
                {{ knowledgeData.views }} 次浏览
              </span>
            </div>

            <div class="tag-group">
              <span 
                v-for="tag in knowledgeData.tags" 
                :key="tag" 
                class="tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <div class="header-actions">
          <button 
            @click="toggleFavorite" 
            class="btn favorite-btn"
            :class="{ active: knowledgeData.isFavorite }"
          >
            ⭐ {{ knowledgeData.isFavorite ? '已收藏' : '收藏' }}
          </button>
          <button @click="exportMarkdown" class="btn btn-outline">
            📥 导出
          </button>
          <button @click="shareKnowledge" class="btn btn-outline">
            🔗 分享
          </button>
          <button @click="editKnowledge" class="btn btn-outline">
            ✏️ 编辑
          </button>
        </div>
      </div>

      <!-- 内容主体 -->
      <div class="knowledge-body">
        <!-- 侧边栏导航 -->
        <div class="sidebar">
          <div class="sidebar-sticky">
            <h3>内容导航</h3>
            <nav class="toc">
              <ul>
                <li 
                  v-for="(item, index) in tableOfContents" 
                  :key="index"
                  :class="['toc-item', `toc-level-${item.level}`]"
                >
                  <a 
                    :href="`#${item.id}`" 
                    @click.prevent="scrollToHeading(item.id)"
                    :class="{ active: activeHeading === item.id }"
                  >
                    {{ item.text }}
                  </a>
                </li>
              </ul>
            </nav>

            <div class="sidebar-stats">
              <h4>内容统计</h4>
              <div class="stat-item">
                <span>字数:</span>
                <span>{{ knowledgeData.wordCount }}</span>
              </div>
              <div class="stat-item">
                <span>阅读时间:</span>
                <span>{{ Math.ceil(knowledgeData.wordCount / 200) }} 分钟</span>
              </div>
              <div class="stat-item">
                <span>最后更新:</span>
                <span>{{ formatDateTime(knowledgeData.updatedAt) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 主要内容 -->
        <div class="main-content">
          <!-- Markdown内容 -->
          <div class="markdown-content" v-html="compiledMarkdown"></div>

          <!-- 相关资源 -->
          <div class="related-resources">
            <h3>📚 相关资源</h3>
            <div class="resources-grid">
              <a 
                v-for="resource in knowledgeData.relatedResources" 
                :key="resource.url"
                :href="resource.url" 
                target="_blank" 
                class="resource-card"
              >
                <span class="resource-icon">{{ resource.type === 'video' ? '🎬' : '📖' }}</span>
                <div class="resource-content">
                  <h4>{{ resource.title }}</h4>
                  <p>{{ resource.description }}</p>
                </div>
              </a>
            </div>
          </div>

          <!-- 评论区域 -->
          <div class="comments-section">
            <h3>💬 讨论区</h3>
            <div class="comment-form">
              <textarea 
                v-model="newComment" 
                placeholder="分享你的想法或提问..."
                rows="3"
                class="comment-input"
              ></textarea>
              <button 
                @click="addComment" 
                class="btn btn-primary"
                :disabled="!newComment.trim()"
              >
                发布评论
              </button>
            </div>

            <div class="comments-list">
              <div 
                v-for="comment in knowledgeData.comments" 
                :key="comment.id" 
                class="comment-card"
              >
                <div class="comment-header">
                  <span class="comment-author">{{ comment.author }}</span>
                  <span class="comment-date">{{ formatDateTime(comment.date) }}</span>
                </div>
                <p class="comment-content">{{ comment.content }}</p>
                <div class="comment-actions">
                  <button @click="likeComment(comment.id)" class="like-btn">
                    👍 {{ comment.likes }}
                  </button>
                  <button @click="replyToComment(comment.id)" class="reply-btn">
                    回复
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部推荐 -->
      <div class="recommendations">
        <h3>你可能也喜欢</h3>
        <div class="recommendations-grid">
          <div 
            v-for="item in recommendedKnowledge" 
            :key="item.id" 
            class="recommendation-card"
            @click="goToKnowledge(item.id)"
          >
            <div class="rec-thumbnail">
              <img :src="item.thumbnail" :alt="item.title" />
            </div>
            <div class="rec-content">
              <h4>{{ item.title }}</h4>
              <p class="rec-description">{{ truncateText(item.description, 80) }}</p>
              <div class="rec-meta">
                <span class="rec-author">by {{ item.author }}</span>
                <span class="rec-views">👁️ {{ item.views }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 浮动操作按钮 -->
    <div class="floating-actions">
      <button @click="scrollToTop" class="action-btn" title="返回顶部">
        ⬆️
      </button>
      <button @click="toggleFavorite" class="action-btn" :title="knowledgeData?.isFavorite ? '取消收藏' : '收藏'">
        ⭐
      </button>
      <button @click="exportMarkdown" class="action-btn" title="导出">
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
const knowledgeData = ref(null)
const newComment = ref('')
const activeHeading = ref('')

// 模拟数据
const mockKnowledgeData = {
  id: '1',
  title: 'Python数据分析完整指南：从入门到实战',
  description: '全面掌握Python数据分析的核心技术和最佳实践，包括Pandas、NumPy、Matplotlib等库的深入应用',
  author: '数据科学家',
  category: '数据分析',
  tags: ['Python', '数据分析', 'Pandas', 'NumPy', '可视化'],
  createdAt: '2024-01-15T10:30:00',
  updatedAt: '2024-01-16T14:20:00',
  views: 156,
  wordCount: 2850,
  isFavorite: true,
  markdownContent: `# Python数据分析完整指南

## 概述
本指南全面介绍Python在数据分析领域的应用，涵盖从基础到高级的各个方面。

## 核心概念

### 数据处理基础
- 数据清洗与预处理
- 数据转换与重塑
- 缺失值处理策略

### 数据分析技术
- 描述性统计分析
- 相关性分析
- 时间序列分析

## 实战案例

### 案例一：销售数据分析
通过真实销售数据演示完整分析流程...

### 案例二：用户行为分析
分析用户行为模式，提取有价值的信息...

## 最佳实践

### 性能优化
- 内存使用优化
- 计算效率提升
- 并行处理技巧

### 代码质量
- 可读性提升
- 模块化设计
- 测试策略

## 扩展学习

### 进阶主题
- 机器学习集成
- 大数据处理
- 实时数据分析

### 资源推荐
- 官方文档
- 在线课程
- 社区资源

---

*最后更新于 2024-01-16 14:20:00*`,
  relatedResources: [
    {
      type: 'video',
      title: 'Pandas高级技巧教程',
      description: '深入讲解Pandas的高级功能和使用技巧',
      url: 'https://www.bilibili.com/video/BV1xxx'
    },
    {
      type: 'article',
      title: 'NumPy性能优化指南',
      description: '提升NumPy计算效率的实用技巧',
      url: 'https://example.com/article'
    }
  ],
  comments: [
    {
      id: '1',
      author: '学习爱好者',
      date: '2024-01-15T14:30:00',
      content: '非常实用的教程，对我帮助很大！',
      likes: 12
    },
    {
      id: '2',
      author: 'Python开发者',
      date: '2024-01-15T16:45:00',
      content: '案例很丰富，希望能有更多实战内容',
      likes: 8
    }
  ]
}

const recommendedKnowledge = [
  {
    id: '2',
    title: '机器学习实战指南',
    description: '从零开始学习机器学习算法和实战应用',
    author: 'AI专家',
    views: 234,
    thumbnail: '/api/placeholder/120/80'
  },
  {
    id: '3',
    title: 'React高级开发',
    description: '深入理解React原理和高级开发技巧',
    author: '前端架构师',
    views: 189,
    thumbnail: '/api/placeholder/120/80'
  }
]

onMounted(() => {
  loadKnowledgeDetail()
  setupHeadingObserver()
})

const loadKnowledgeDetail = async () => {
  try {
    loading.value = true
    error.value = null
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    knowledgeData.value = mockKnowledgeData
    
    // 更新浏览量
    knowledgeData.value.views++
    
  } catch (err) {
    error.value = '加载知识详情失败，请稍后重试'
    console.error('Error loading knowledge detail:', err)
  } finally {
    loading.value = false
  }
}

const retryLoading = () => {
  loadKnowledgeDetail()
}

const compiledMarkdown = computed(() => {
  return marked(knowledgeData.value?.markdownContent || '')
})

const tableOfContents = computed(() => {
  const toc = []
  const headingRegex = /<h([2-3]) id="([^"]+)">([^<]+)<\/h\1>/gi
  let match
  
  while ((match = headingRegex.exec(compiledMarkdown.value)) !== null) {
    toc.push({
      level: parseInt(match[1]),
      id: match[2],
      text: match[3]
    })
  }
  
  return toc
})

const setupHeadingObserver = () => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          activeHeading.value = entry.target.id
        }
      })
    },
    { rootMargin: '-100px 0px -50% 0px' }
  )

  // 观察所有标题元素
  watch(compiledMarkdown, () => {
    setTimeout(() => {
      const headings = document.querySelectorAll('h2, h3')
      headings.forEach(heading => {
        observer.observe(heading)
      })
    }, 100)
  })
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const toggleFavorite = async () => {
  if (!knowledgeData.value) return
  
  try {
    knowledgeData.value.isFavorite = !knowledgeData.value.isFavorite
    // 模拟API调用更新收藏状态
    await new Promise(resolve => setTimeout(resolve, 300))
  } catch (err) {
    console.error('Error toggling favorite:', err)
  }
}

const exportMarkdown = () => {
  const content = knowledgeData.value.markdownContent
  const blob = new Blob([content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${knowledgeData.value.title}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const shareKnowledge = async () => {
  try {
    const shareData = {
      title: knowledgeData.value.title,
      text: knowledgeData.value.description,
      url: window.location.href
    }
    
    if (navigator.share) {
      await navigator.share(shareData)
    } else {
      await navigator.clipboard.writeText(window.location.href)
      alert('链接已复制到剪贴板！')
    }
  } catch (err) {
    console.error('Error sharing:', err)
  }
}

const editKnowledge = () => {
  router.push(`/repository/${knowledgeData.value.id}/edit`)
}

const addComment = async () => {
  if (!newComment.value.trim()) return
  
  try {
    const comment = {
      id: Date.now().toString(),
      author: '当前用户',
      date: new Date().toISOString(),
      content: newComment.value.trim(),
      likes: 0
    }
    
    knowledgeData.value.comments.unshift(comment)
    newComment.value = ''
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
  } catch (err) {
    console.error('Error adding comment:', err)
  }
}

const likeComment = async (commentId) => {
  try {
    const comment = knowledgeData.value.comments.find(c => c.id === commentId)
    if (comment) {
      comment.likes++
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 300))
    }
  } catch (err) {
    console.error('Error liking comment:', err)
  }
}

const replyToComment = (commentId) => {
  newComment.value = `@回复${commentId} `
  document.querySelector('.comment-input')?.focus()
}

const goToKnowledge = (id) => {
  router.push(`/repository/${id}`)
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN')
}

const truncateText = (text, length) => {
  if (!text) return ''
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    loadKnowledgeDetail()
  }
})
</script>

<style scoped>
.repository-detail-page {
  max-width: 1400px;
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

.knowledge-header {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  color: #718096;
}

.breadcrumb-link {
  color: #667eea;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #a0aec0;
}

.breadcrumb-current {
  color: #2d3748;
  font-weight: 600;
}

.header-main h1 {
  color: #2d3748;
  font-size: 2.5rem;
  margin-bottom: 1rem;
  line-height: 1.3;
}

.description {
  color: #718096;
  font-size: 1.2rem;
  line-height: 1.6;
  margin-bottom: 2rem;
}

.header-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1.5rem;
}

.meta-group {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4a5568;
  font-size: 0.9rem;
}

.meta-icon {
  font-size: 1.1rem;
}

.tag-group {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  background: #e2e8f0;
  color: #4a5568;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.favorite-btn.active {
  background: #f59e0b;
  color: white;
  border-color: #f59e0b;
}

.knowledge-body {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

.sidebar {
  position: relative;
}

.sidebar-sticky {
  position: sticky;
  top: 2rem;
}

.sidebar h3 {
  color: #2d3748;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.toc {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.toc ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin-bottom: 0.5rem;
}

.toc-item a {
  display: block;
  padding: 0.5rem 0.75rem;
  color: #4a5568;
  text-decoration: none;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.toc-item a:hover,
.toc-item a.active {
  background: #667eea;
  color: white;
}

.toc-level-3 {
  padding-left: 1.5rem;
  font-size: 0.85rem;
}

.sidebar-stats {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.sidebar-stats h4 {
  color: #2d3748;
  margin-bottom: 1rem;
  font-size: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid #e2e8f0;
  font-size: 0.9rem;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item span:first-child {
  color: #718096;
}

.stat-item span:last-child {
  color: #2d3748;
  font-weight: 600;
}

.main-content {
  min-width: 0;
}

.markdown-content {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  line-height: 1.8;
}

.markdown-content :deep(h1) {
  color: #2d3748;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.markdown-content :deep(h2) {
  color: #2d3748;
  margin: 2rem 0 1rem 0;
  padding-top: 1rem;
}

.markdown-content :deep(h3) {
  color: #4a5568;
  margin: 1.5rem 0 0.75rem 0;
}

.markdown-content :deep(p) {
  color: #4a5568;
  margin-bottom: 1rem;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  color: #4a5568;
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0.5rem;
}

.markdown-content :deep(a) {
  color: #667eea;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(code) {
  background: #f7fafc;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(pre) {
  background: #2d3748;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #718096;
  font-style: italic;
}

.related-resources {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.related-resources h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.resource-card {
  display: flex;
  align-items: start;
  gap: 1rem;
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.resource-card:hover {
  background: #edf2f7;
  transform: translateY(-2px);
}

.resource-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.resource-content h4 {
  color: #2d3748;
  margin-bottom: 0.5rem;
  line-height: 1.4;
}

.resource-content p {
  color: #718096;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.comments-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.comments-section h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.comment-form {
  margin-bottom: 2rem;
}

.comment-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  resize: vertical;
  margin-bottom: 1rem;
}

.comment-input:focus {
  outline: none;
  border-color: #667eea;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.comment-card {
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.comment-author {
  color: #2d3748;
  font-weight: 600;
}

.comment-date {
  color: #a0aec0;
  font-size: 0.8rem;
}

.comment-content {
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.comment-actions {
  display: flex;
  gap: 1rem;
}

.like-btn,
.reply-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #e2e8f0;
  background: white;
  color: #4a5568;
  border-radius: 4px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.like-btn:hover,
.reply-btn:hover {
  background: #f7fafc;
}

.recommendations {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.recommendations h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.recommendation-card {
  display: flex;
  gap: 1rem;
  padding: 1.5rem;
  background: #f7fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e2e8f0;
}

.recommendation-card:hover {
  background: #edf2f7;
  transform: translateY(-2px);
}

.rec-thumbnail {
  width: 80px;
  height: 60px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
}

.rec-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rec-content {
  flex: 1;
  min-width: 0;
}

.rec-content h4 {
  color: #2d3748;
  margin-bottom: 0.5rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rec-description {
  color: #718096;
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rec-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.rec-author {
  color: #667eea;
  font-weight: 500;
}

.rec-views {
  color: #a0aec0;
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

@media (max-width: 1024px) {
  .knowledge-body {
    grid-template-columns: 250px 1fr;
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .repository-detail-page {
    padding: 1rem;
  }

  .knowledge-body {
    grid-template-columns: 1fr;
  }

  .sidebar {
    order: 2;
  }

  .sidebar-sticky {
    position: static;
  }

  .header-meta {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .meta-group {
    justify-content: center;
  }

  .header-actions {
    justify-content: center;
  }

  .resources-grid {
    grid-template-columns: 1fr;
  }

  .recommendations-grid {
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
    font-size: 2rem;
  }

  .meta-group {
    flex-direction: column;
    gap: 0.75rem;
  }

  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .resource-card {
    flex-direction: column;
    text-align: center;
  }

  .recommendation-card {
    flex-direction: column;
    text-align: center;
  }

  .rec-thumbnail {
    width: 100%;
    height: 120px;
  }
}
</style>