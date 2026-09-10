<template>
  <div class="community-hub">
    <div class="community-header">
      <h3>社区互动</h3>
      <el-button type="primary" size="small" @click="showPostDialog = true">
        <i class="el-icon-edit"></i> 发布帖子
      </el-button>
    </div>

    <div class="filter-tabs">
      <el-radio-group v-model="filterType" @change="handleFilter">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button value="experience">经验分享</el-radio-button>
        <el-radio-button value="question">问答</el-radio-button>
      </el-radio-group>
      <el-select v-model="filterCategory" placeholder="全部分类" clearable style="width: 150px" @change="handleFilter">
        <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
      </el-select>
    </div>

    <div v-loading="loading" class="posts-list">
      <div v-if="posts.length === 0 && !loading" class="empty-state">
        <i class="el-icon-chat-line-round"></i>
        <p>暂无帖子，成为第一个发帖的人吧</p>
      </div>

      <div v-else class="post-cards">
        <div v-for="post in posts" :key="post.id" class="post-card" @click="handleViewPost(post)">
          <div class="post-header">
            <div class="post-author">
              <el-avatar :size="36" icon="el-icon-user-solid"></el-avatar>
              <div class="author-info">
                <p class="author-name">{{ post.username }}</p>
                <p class="post-time">{{ formatDate(post.created_at) }}</p>
              </div>
            </div>
            <el-tag size="small" :type="post.type === 'experience' ? 'success' : 'warning'">
              {{ post.type === 'experience' ? '经验' : '问答' }}
            </el-tag>
          </div>

          <h4 class="post-title">{{ post.title }}</h4>
          <p class="post-content">{{ getPreviewContent(post.content) }}</p>

          <div v-if="post.tags?.length" class="post-tags">
            <el-tag v-for="tag in post.tags.slice(0, 3)" :key="tag" size="small" type="info">
              {{ tag }}
            </el-tag>
          </div>

          <div class="post-footer">
            <div class="post-stats">
              <span><i class="el-icon-view"></i> {{ post.view_count }}</span>
              <span><i class="el-icon-star-on"></i> {{ post.like_count }}</span>
              <span><i class="el-icon-chat-square"></i> {{ post.comment_count }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="total > pageSize" class="pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <el-dialog v-model="showPostDialog" :title="'发布帖子'" width="600px">
      <el-form :model="postForm" label-width="80px">
        <el-form-item label="类型" required>
          <el-radio-group v-model="postForm.type">
            <el-radio label="experience">经验分享</el-radio>
            <el-radio label="question">问答</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="标题" required>
          <el-input v-model="postForm.title" placeholder="请输入帖子标题" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="postForm.category" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="postForm.content" type="textarea" :rows="6" placeholder="请输入帖子内容" />
        </el-form-item>
        <el-form-item label="标签">
          <el-input v-model="postForm.tags" placeholder="多个标签用逗号分隔" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPostDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitPost">发布</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" :title="currentPost?.title" width="700px" class="post-detail-dialog">
      <div v-if="currentPost" class="post-detail">
        <div class="detail-header">
          <div class="detail-author">
            <el-avatar :size="48" icon="el-icon-user-solid"></el-avatar>
            <div class="author-info">
              <p class="author-name">{{ currentPost.username }}</p>
              <p class="post-time">{{ formatDate(currentPost.created_at) }}</p>
            </div>
          </div>
          <el-tag size="small" :type="currentPost.type === 'experience' ? 'success' : 'warning'">
            {{ currentPost.type === 'experience' ? '经验分享' : '问答' }}
          </el-tag>
        </div>

        <div class="detail-content">
          {{ currentPost.content }}
        </div>

        <div v-if="currentPost.tags?.length" class="detail-tags">
          <el-tag v-for="tag in currentPost.tags" :key="tag" size="small" type="info">
            {{ tag }}
          </el-tag>
        </div>

        <div class="detail-stats">
          <span><i class="el-icon-view"></i> {{ currentPost.view_count }} 阅读</span>
          <span><i class="el-icon-star-on"></i> {{ currentPost.like_count }} 点赞</span>
        </div>

        <el-divider></el-divider>

        <div class="comments-section">
          <h4>评论 ({{ currentPost.comments?.length || 0 }})</h4>

          <div class="comment-input">
            <el-input v-model="commentContent" placeholder="写下你的评论..." type="textarea" :rows="2" />
            <el-button type="primary" size="small" @click="handleSubmitComment" style="margin-top: 8px">
             发表评论
            </el-button>
          </div>

          <div class="comments-list">
            <div v-for="comment in currentPost.comments" :key="comment.id" class="comment-item">
              <el-avatar :size="32" icon="el-icon-user-solid"></el-avatar>
              <div class="comment-content">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.username }}</span>
                  <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <p class="comment-text">{{ comment.content }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'CommunityHub',
  data() {
    return {
      posts: [],
      categories: ['技术', '产品', '运营', '市场', '管培生', '公务员', '国企', '其他'],
      filterType: '',
      filterCategory: '',
      loading: false,
      currentPage: 1,
      pageSize: 10,
      total: 0,
      showPostDialog: false,
      showDetailDialog: false,
      currentPost: null,
      commentContent: '',
      postForm: {
        type: 'experience',
        title: '',
        category: '',
        content: '',
        tags: ''
      }
    }
  },
  mounted() {
    this.fetchPosts()
  },
  methods: {
    async fetchPosts() {
      this.loading = true
      try {
        const params = new URLSearchParams({
          page: this.currentPage,
          page_size: this.pageSize
        })
        if (this.filterType) params.append('type', this.filterType)
        if (this.filterCategory) params.append('category', this.filterCategory)

        const response = await fetch(`/api/posts?${params}`)
        const data = await response.json()
        if (data.success) {
          this.posts = data.data
          this.total = data.total
        }
      } catch (error) {
        console.error('获取帖子失败:', error)
      } finally {
        this.loading = false
      }
    },
    handleFilter() {
      this.currentPage = 1
      this.fetchPosts()
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchPosts()
    },
    async handleViewPost(post) {
      try {
        const response = await fetch(`/api/posts/${post.id}`)
        const data = await response.json()
        if (data.success) {
          this.currentPost = data.data
          this.showDetailDialog = true
        }
      } catch (error) {
        console.error('获取帖子详情失败:', error)
      }
    },
    async handleSubmitPost() {
      if (!this.postForm.title || !this.postForm.content) {
        this.$message.warning('请填写标题和内容')
        return
      }

      const userId = this.getCurrentUserId()
      const username = localStorage.getItem('username') || '匿名用户'
      if (!userId) {
        this.$message.warning('请先登录')
        return
      }

      try {
        const response = await fetch('/api/posts', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            username: username,
            title: this.postForm.title,
            content: this.postForm.content,
            type: this.postForm.type,
            category: this.postForm.category,
            tags: this.postForm.tags
          })
        })
        const data = await response.json()
        if (data.success) {
          this.$message.success('发布成功')
          this.showPostDialog = false
          this.resetPostForm()
          this.fetchPosts()
        }
      } catch (error) {
        console.error('发布失败:', error)
        this.$message.error('发布失败')
      }
    },
    async handleSubmitComment() {
      if (!this.commentContent) {
        this.$message.warning('请输入评论内容')
        return
      }

      const userId = this.getCurrentUserId()
      const username = localStorage.getItem('username') || '匿名用户'
      if (!userId) {
        this.$message.warning('请先登录')
        return
      }

      try {
        const response = await fetch(`/api/posts/${this.currentPost.id}/comments`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: userId,
            username: username,
            content: this.commentContent
          })
        })
        const data = await response.json()
        if (data.success) {
          this.$message.success('评论成功')
          this.commentContent = ''
          this.handleViewPost({ id: this.currentPost.id })
        }
      } catch (error) {
        console.error('评论失败:', error)
        this.$message.error('评论失败')
      }
    },
    resetPostForm() {
      this.postForm = {
        type: 'experience',
        title: '',
        category: '',
        content: '',
        tags: ''
      }
    },
    getCurrentUserId() {
      const userData = localStorage.getItem('userData')
      if (userData) {
        const user = JSON.parse(userData)
        return user.id || 0
      }
      return 0
    },
    getPreviewContent(content) {
      if (!content) return ''
      return content.length > 100 ? content.substring(0, 100) + '...' : content
    },
    formatDate(date) {
      if (!date) return ''
      const d = new Date(date)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.community-hub {
  padding: 0;
}

.community-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.community-header h3 {
  font-size: 18px;
  color: #ffffff;
  margin: 0;
}

.filter-tabs {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #909399;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
}

.post-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(102, 126, 234, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  cursor: pointer;
  transition: all 0.3s;
}

.post-card:hover {
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
  border-color: rgba(102, 126, 234, 0.6);
}

.post-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.post-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 600;
  color: #ffffff;
  margin: 0;
}

.post-time {
  font-size: 12px;
  color: #a0a0c0;
  margin: 0;
}

.post-title {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 8px;
}

.post-content {
  font-size: 14px;
  color: #a0a0c0;
  line-height: 1.6;
  margin-bottom: 12px;
}

.post-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.post-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.post-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.post-detail-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.detail-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-content {
  font-size: 14px;
  line-height: 1.8;
  color: #303133;
  margin-bottom: 16px;
  white-space: pre-wrap;
}

.detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.detail-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #909399;
}

.detail-stats span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.comments-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
}

.comment-input {
  margin-bottom: 24px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comment-item {
  display: flex;
  gap: 12px;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.comment-author {
  font-weight: 600;
  font-size: 14px;
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-text {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}
</style>
