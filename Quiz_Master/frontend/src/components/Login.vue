<template>
  <div class="container mt-5">
    <h2>Login</h2>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label>Username</label>
        <input v-model="username" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-primary">Login</button>
      <p class="mt-3">Don't have an account? <router-link to="/register">Register here</router-link></p>
      <p v-if="error" class="text-danger mt-2">{{ error }}</p>
      <p v-if="successMessage" class="text-success mt-2">{{ successMessage }}</p>
    </form>
  </div>
</template>

<script>
export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      successMessage: ''
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      this.successMessage = '';
      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          }),
          credentials: 'include'
        });

        const result = await response.json();

        if (!response.ok) {
          this.error = result.error || 'Login failed';
        } else {
          this.successMessage = result.message || 'Login successful!';
          if (result.is_admin) {
            this.$router.push('/admin/dashboard');
          } else {
            this.$router.push(`/user/${result.user_id}/dashboard`);
          }
        }
      } catch (error) {
        console.error('Error during login:', error);
        this.error = 'Network error or server unreachable. Check if backend is running and proxy is configured.';
      }
    }
  }
};
</script>