/**
 * 全局 fetch 拦截器：给同源 /api/ 请求自动附上登录令牌。
 *
 * 项目里 76 处调用全部直接用原生 fetch()，没有统一的请求层。
 * 与其改 76 个调用点（回归面大），不如在入口处包一层 —— 调用点零改动。
 *
 * 修复前：登录结果只存在 localStorage 里，请求靠 URL 参数 user_id 表明身份，
 * 服务端不做任何校验。
 */

const TOKEN_KEY = 'authToken'

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch (e) {
    return ''
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token)
    else localStorage.removeItem(TOKEN_KEY)
  } catch (e) {
    /* 隐私模式下 localStorage 可能不可用，忽略 */
  }
}

export function clearAuth() {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem('userData')
    localStorage.removeItem('username')
  } catch (e) {
    /* 同上 */
  }
}

function isApiRequest(url) {
  try {
    const resolved = new URL(url, window.location.origin)
    return resolved.origin === window.location.origin && resolved.pathname.startsWith('/api/')
  } catch (e) {
    return typeof url === 'string' && url.startsWith('/api/')
  }
}

export function installFetchInterceptor(onUnauthorized) {
  const nativeFetch = window.fetch.bind(window)

  window.fetch = async (input, init = {}) => {
    const url = typeof input === 'string' ? input : (input && input.url) || ''
    const token = getToken()

    if (token && isApiRequest(url)) {
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined))
      if (!headers.has('Authorization')) headers.set('Authorization', `Bearer ${token}`)
      init = { ...init, headers }
    }

    const response = await nativeFetch(input, init)

    if (response.status === 401 && isApiRequest(url)) {
      clearAuth()
      if (typeof onUnauthorized === 'function') onUnauthorized()
    }
    return response
  }
}
