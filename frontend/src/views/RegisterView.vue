<template>
  <div class="register">
    <div class="register-container">
      <div class="register-bg"></div>
      <div class="register-card">
        <div class="register-header">
          <h2>智能问卷系统</h2>
          <p>用户注册</p>
        </div>
        <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="80px">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="registerForm.email" type="email" placeholder="请输入邮箱" :prefix-icon="Message"></el-input>
          </el-form-item>
          <el-form-item label="用户名" prop="username">
            <el-input v-model="registerForm.username" placeholder="请输入用户名" :prefix-icon="User"></el-input>
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="registerForm.password" type="password" placeholder="请输入密码" show-password :prefix-icon="Lock"></el-input>
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="registerForm.confirmPassword" type="password" placeholder="请确认密码" show-password :prefix-icon="Lock"></el-input>
          </el-form-item>
          <el-form-item>
            <div class="button-group">
              <el-button type="primary" @click="handleRegister" :loading="loading" class="register-btn">注册</el-button>
              <el-button @click="goToLogin" class="login-btn">登录</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { Message, User, Lock } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能少于3个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    loading.value = true
    await registerFormRef.value.validate()
    
    await userStore.register({
      email: registerForm.email,
      username: registerForm.username,
      password: registerForm.password
    })
    
    // 注册成功后直接跳转到登录页面
    router.push('/login')
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.register-container {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 1200px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.register-card {
  width: 400px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  padding: 40px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.register-card:hover {
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
  transform: translateY(-5px);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.register-header p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.register-btn {
  flex: 1;
  height: 48px;
  font-size: 16px;
  border-radius: 8px;
  margin-right: 10px;
  background: linear-gradient(135deg, #67C23A 0%, #85ce61 100%);
  border: none;
  transition: all 0.3s ease;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.login-btn {
  flex: 1;
  height: 48px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #409EFF;
  color: #409EFF;
  transition: all 0.3s ease;
}

.login-btn:hover {
  background-color: #409EFF;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.el-input {
  border-radius: 8px;
  height: 48px;
  font-size: 16px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.el-input:focus-within {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.el-form-item {
  margin-bottom: 20px;
}

.button-group {
  display: flex;
  width: 100%;
  gap: 10px;
}

.el-form-item__label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .register-card {
    width: 100%;
    max-width: 350px;
    padding: 30px 20px;
  }
  
  .register-header h2 {
    font-size: 20px;
  }
  
  .register-btn, .login-btn {
    height: 44px;
    font-size: 14px;
  }
  
  .el-input {
    height: 44px;
    font-size: 14px;
  }
}
</style>
