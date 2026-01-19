import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
// 在 Element Plus 样式之后导入，确保能够覆盖
import './styles/dialog.css'
import './styles/global.css'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  // 忽略常见的路由切换时的 DOM 访问错误
  if (err instanceof TypeError && err.message.includes('parentNode')) {
    // 这是已知的 Element Plus 在路由切换时的 DOM 访问问题，不影响功能
    console.debug('Ignoring parentNode error during route transition:', err)
    return
  }
  // 其他错误正常输出
  console.error('Global error:', err, info)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')

