import { createRouter, createWebHashHistory } from 'vue-router'
import { tokenManager } from '../utils/token'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      redirect: '/projects/list'
    },
    {
      path: '/bugs',
      name: 'Bugs',
      component: () => import('../views/BugsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/apitest',
      redirect: '/apitest/api'
    },
    {
      path: '/apitest/api',
      name: 'ApiTest',
      component: () => import('../views/ApiTestPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/apitest/flow',
      name: 'ApiFlow',
      component: () => import('../views/ApiFlowPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/apitest/task',
      name: 'TestTask',
      component: () => import('../views/TestTaskPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/apitest/codescan',
      name: 'CodeScan',
      component: () => import('../views/CodeScanPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/apitest/codescan/:id',
      name: 'CodeScanResult',
      component: () => import('../views/CodeScanResultPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/api-environments',
      name: 'ApiEnvironments',
      component: () => import('../views/ApiEnvironmentPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/testcases',
      redirect: '/testcases/detail'
    },
    {
      path: '/testcases/detail',
      name: 'TestCases',
      component: () => import('../views/TestCasesPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/testcases/review',
      name: 'TestCaseReview',
      component: () => import('../views/TestCaseReviewPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/statistics',
      name: 'Statistics',
      component: () => import('../views/StatisticsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/models',
      name: 'Models',
      component: () => import('../views/ModelsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects',
      redirect: '/projects/list'
    },
    {
      path: '/projects/list',
      name: 'Projects',
      component: () => import('../views/ProjectsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/projects/sprints',
      name: 'Sprints',
      component: () => import('../views/SprintsPage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/users',
      name: 'Users',
      component: () => import('../views/UsersPage.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫：检查登录状态
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.meta.requiresAuth) {
    // 检查是否有 token
    if (!tokenManager.hasToken()) {
      // 未登录，触发登录对话框事件
      window.dispatchEvent(new CustomEvent('auth:required', { detail: { route: to.path } }))
      // 阻止路由跳转
      next(false)
      return
    }
  }
  
  // 允许访问
  next()
})

// 路由错误处理
router.onError((error) => {
  // 忽略导航重复的错误
  if (error.name === 'NavigationDuplicated') {
    return
  }
  // 忽略路由切换时的 DOM 访问错误
  if (error instanceof TypeError && error.message.includes('parentNode')) {
    console.debug('Ignoring parentNode error during route navigation:', error)
    return
  }
  console.error('Router error:', error)
})

export default router

