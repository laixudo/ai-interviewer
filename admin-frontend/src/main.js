import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as echarts from 'echarts'
import App from './App.vue'
import { installFetchInterceptor } from './http'

installFetchInterceptor(() => {
  window.location.reload()
})

const app = createApp(App)
app.use(ElementPlus)
app.mount('#app')
