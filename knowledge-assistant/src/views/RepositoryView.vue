<template>
  <div class="repository-page">
    <div class="page-header">
      <h2>知识仓库</h2>
      <p>管理您收藏的所有学习笔记和知识内容</p>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filters-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="搜索笔记内容..."
          class="search-input"
        />
        <button @click="performSearch" class="search-btn">
          🔍
        </button>
      </div>

      <div class="filter-group">
        <select v-model="sortBy" class="filter-select">
          <option value="newest">最新优先</option>
          <option value="oldest">最旧优先</option>
          <option value="title">按标题排序</option>
        </select>

        <select v-model="categoryFilter" class="filter-select">
          <option value="">所有分类</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>

        <select v-model="favoriteFilter" class="filter-select">
          <option value="">所有笔记</option>
          <option value="favorite">仅收藏</option>
        </select>
      </div>
    </div>

    <!-- 知识卡片网格 -->
    <div class="knowledge-grid">
      <div 
        v-for="item in filteredKnowledge" 
        :key="item.id" 
        class="knowledge-card"
        @click="viewKnowledgeDetail(item)"
      >
        <div class="card-header">
          <h3>{{ item.title }}</h3>
          <div class="card-actions">
            <button 
              @click.stop="toggleFavorite(item)" 
              class="favorite-btn"
              :class="{ active: item.isFavorite }"
            >
              ⭐
            </button>
            <button @click.stop="editKnowledge(item)" class="edit-btn">
              ✏️
            </button>
          </div>
        </div>

        <div class="card-content">
          <p class="description">{{ truncateText(item.description, 100) }}</p>
          
          <div class="meta-info">
            <span class="author">by {{ item.author }}</span>
            <span class="date">{{ formatDate(item.createdAt) }}</span>
          </div>

          <div class="tags">
            <span 
              v-for="tag in item.tags.slice(0, 3)" 
              :key="tag" 
              class="tag"
            >
              {{ tag }}
            </span>
            <span v-if="item.tags.length > 3" class="tag-more">
              +{{ item.tags.length - 3 }}
            </span>
          </div>
        </div>

        <div class="card-footer">
          <div class="stats">
            <span class="stat">📊 {{ item.tokenUsage }} tokens</span>
            <span class="stat">👁️ {{ item.views }} 浏览</span>
          </div>
          <span class="category">{{ item.category }}</span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredKnowledge.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>暂无知识内容</h3>
      <p>开始分析视频后，您的笔记将显示在这里</p>
      <router-link to="/analysis" class="btn btn-primary">
        去分析视频
      </router-link>
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const knowledgeItems = ref([])
const searchQuery = ref('')
const sortBy = ref('newest')
const categoryFilter = ref('')
const favoriteFilter = ref('')
const currentPage = ref(1)
const itemsPerPage = ref(12)

const categories = ref([
  '编程开发',
  '数据分析',
  '机器学习',
  '前端技术',
  '后端开发',
  '设计创意',
  '商业知识',
  '语言学习'
])

// 模拟知识数据
const mockKnowledge = [
  {
    id: '1',
    title: 'Python数据分析实战指南',
    description: '全面讲解Python在数据分析中的应用，包括Pandas、NumPy、Matplotlib等库的使用技巧和实战案例。',
    author: '数据科学家',
    category: '数据分析',
    tags: ['Python', '数据分析', 'Pandas', '可视化'],
    createdAt: '2024-01-15T10:30:00',
    tokenUsage: 2450,
    views: 156,
    isFavorite: true
  },
  {
    id: '2',
    title: 'React高级组件开发',
    description: '深入探讨React组件的高级用法，包括Hooks、Context、性能优化和自定义Hook开发。',
    author: '前端大神',
    category: '前端技术',
    tags: ['React', 'JavaScript', '前端', '组件'],
    createdAt: '2024-01-14T16:45:00',
    tokenUsage: 3120,
    views: 89,
    isFavorite: false
  },
  {
    id: '3',
    title: '机器学习基础概念',
    description: '机器学习的基本原理和算法介绍，适合初学者入门学习的基础知识整理。',
    author: 'AI教授',
    category: '机器学习',
    tags: ['机器学习', 'AI', '算法', '基础'],
    createdAt: '2024-01-13T09:15:00',
    tokenUsage: 1890,
    views: 234,
    isFavorite: true
  }
]

onMounted(() => {
  loadKnowledgeItems()
})

const loadKnowledgeItems = () => {
  knowledgeItems.value = mockKnowledge
}

const filteredKnowledge = computed(() => {
  let filtered = knowledgeItems.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query) ||
      item.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }

  // 分类过滤
  if (categoryFilter.value) {
    filtered = filtered.filter(item => item.category === categoryFilter.value)
  }

  // 收藏过滤
  if (favoriteFilter.value === 'favorite') {
    filtered = filtered.filter(item => item.isFavorite)
  }

  // 排序
  switch (sortBy.value) {
    case 'newest':
      filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      break
    case 'oldest':
      filtered.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
      break
    case 'title':
      filtered.sort((a, b) => a.title.localeCompare(b.title))
      break
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredKnowledge.value.length / itemsPerPage.value)
})

const performSearch = () => {
  currentPage.value = 1
}

const viewKnowledgeDetail = (item) => {
  router.push(`/repository/${item.id}`)
}

const toggleFavorite = (item) => {
  item.isFavorite = !item.isFavorite
}

const editKnowledge = (item) => {
  // 编辑知识项的逻辑
  console.log('Edit knowledge:', item)
}

const truncateText = (text, length) => {
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}
</script>

<style scoped>
.repository-page {
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

.filters-section {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  flex: 1;
  min-width: 300px;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px 0 0 8px;
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-btn {
  padding: 0.75rem 1rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
}

.filter-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  background: white;
  color: #4a5568;
  cursor: pointer;
  min-width: 120px;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.knowledge-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.knowledge-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.knowledge-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  padding: 1.5rem 1.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.card-header h3 {
  margin: 0;
  flex: 1;
  margin-right: 1rem;
  line-height: 1.4;
  font-size: 1.1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.favorite-btn,
.edit-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 6px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.favorite-btn:hover,
.edit-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.favorite-btn.active {
  background: #f59e0b;
  color: white;
}

.card-content {
  padding: 1.5rem;
}

.description {
  color: #4a5568;
  line-height: 1.6;
  margin-bottom: 1rem;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.author {
  color: #667eea;
  font-weight: 600;
}

.date {
  color: #a0aec0;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tag {
  background: #e2e8f0;
  color: #4a5568;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.tag-more {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: #f7fafc;
  border-top: 1px solid #e2e8f0;
}

.stats {
  display: flex;
  gap: 1rem;
}

.stat {
  color: #718096;
  font-size: 0.8rem;
}

.category {
  background: #667eea;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  border: 2px dashed #e2e8f0;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  color: #2d3748;
  margin-bottom: 1rem;
}

.empty-state p {
  color: #718096;
  margin-bottom: 2rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.pagination-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #e2e8f0;
  background: white;
  color: #4a5568;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f7fafc;
  border-color: #667eea;
  color: #667eea;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-info {
  color: #718096;
  font-weight: 500;
}

@media (max-width: 768px) {
  .repository-page {
    padding: 1rem;
  }
  
  .filters-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .filter-group {
    justify-content: center;
  }
  
  .knowledge-grid {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .card-actions {
    justify-content: flex-end;
  }
  
  .meta-info {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .card-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .stats {
    justify-content: center;
  }
}
</style>