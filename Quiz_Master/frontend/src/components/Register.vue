<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label>Full Name</label>
        <input v-model="full_name" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Username</label>
        <input v-model="username" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Qualification</label>
        <input v-model="qualification" type="text" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Date of Birth</label>
        <input v-model="dob" type="date" class="form-control" required />
      </div>
      <button type="submit" class="btn btn-primary">Register</button>
      <p class="mt-3"> have an account? <router-link to="/login">Login here</router-link></p>
      <p class="text-danger mt-2">{{ error }}</p>
    </form>
  </div>
</template>

<script>
export default {
  name: 'UserRegister',
  data() {
    return {
      full_name: '',
      username: '',
      password: '',
      qualification: '',
      dob: '',
      error: ''
    };
  },
  methods: {
    async handleRegister() {
      try {
        const response = await fetch('http://127.0.0.1:5000/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            full_name: this.full_name,
            username: this.username,
            password: this.password,
            qualification: this.qualification,
            dob: this.dob
          }),
          credentials: 'include'
        });

        const result = await response.json();

        if (!response.ok) {
          this.error = result.error || 'Registration failed';
        } else {
          alert("Registration successful! Please log in.");
          this.$router.push('/login');
        }
      } catch (err) {
        this.error = 'Server error or invalid data.';
      }
    }
  }
};
</script>