<script setup>
</script>
<template>
   <nav class="navbar">
      <div class="nav-container">
        <div class="nav-brand">
          <h1>📚 B站视频AI解析助手</h1>
        </div>
        <div class="nav-links">
          <router-link to="/" class="nav-link">首页</router-link>
          <router-link to="/search" class="nav-link">视频搜索</router-link>
          <router-link to="/analysis" class="nav-link">内容分析</router-link>
          <router-link to="/repository" class="nav-link">知识仓库</router-link>
        </div>
      </div>
    </nav>
  <router-view></router-view>
</template>

<style>
.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-link {
  color: #4a5568; /* 中灰色 */
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #667eea; /* 主题色 */
  background: rgba(102, 126, 234, 0.1);
}
</style>