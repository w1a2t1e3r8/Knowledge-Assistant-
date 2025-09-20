import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SearchView from '../views/SearchView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import RepositoryView from '../views/RepositoryView.vue'
import AnalysisDetail from '../views/AnalysisDetail.vue'
import RepositoryDetail from '../views/RepositoryDetail.vue'
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/',name: 'home',component: HomeView},
    {path: '/search',name: 'search',component: SearchView},
    {path: '/analysis',name: 'analysis',component: AnalysisView},
    {path: '/repository',name: 'repository',component: RepositoryView},
    {path: '/analysis/:id',name: 'analysisdetail',component: AnalysisDetail},
    {path: '/repository/:id',name: 'repositorydetail',component: RepositoryDetail}
  ]
})

export default router
