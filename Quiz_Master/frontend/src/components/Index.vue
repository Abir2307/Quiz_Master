<template>
  <div class="d-flex justify-content-center align-items-center vh-100 text-primary text-center">
    <div>
      <h1>Welcome to QUIZ MASTER</h1>
      <p>Find the best Quizzes for prep with ease.</p>
      <router-link to="/register" class="btn btn-primary m-2">Register</router-link>
      <router-link to="/login" class="btn btn-primary m-2">Login</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: "IndexPage"
};
</script>

<style scoped>
h1, p {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}
</style>