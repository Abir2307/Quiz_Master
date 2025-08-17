<template>
  <div class="container mt-5">
    <h2 v-if="user.full_name">Welcome, {{ user.full_name }}</h2>

    <div class="mb-3">
      <button @click="exportCSV" class="btn btn-success">Export My Quizzes as CSV</button>
      <button @click="logout" class="btn btn-danger float-right">Logout</button>
    </div>

    <h3>Subjects</h3>
    <table class="table table-bordered" v-if="subjects.length">
      <thead>
        <tr><th>Name</th><th>Description</th><th>Action</th></tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>{{ subject.name }}</td>
          <td>{{ subject.description }}</td>
          <td>
            <router-link :to="`/user/${user.id}/quizzes/${subject.id}`" class="btn btn-info btn-sm">
              View Quizzes
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <h3 v-if="scores.length">Your Scores</h3>
    <table class="table table-striped" v-if="scores.length">
      <thead>
        <tr>
          <th>Quiz ID</th>
          <th>Subject</th>
          <th>Score</th>
          <th>Max Score</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="score in scores" :key="score.quiz_id">
          <td>{{ score.quiz_id }}</td>
          <td>{{ score.subject_name }}</td>
          <td>{{ score.total_scored }}</td>
          <td>{{ score.total_marks_possible }}</td>
          <td>{{ formatDate(score.time_stamp_of_attempt) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  name: 'UserDashboardView',
  data() {
    return {
      user: {
        id: null,
        full_name: '',
        qualification: '',
        username: ''
      },
      subjects: [],
      scores: []
    };
  },
  methods: {
    async fetchData() {
      const id = this.$route.params.id;

      const response = await fetch(`/user/${id}/dashboard`, {
        method: 'GET',
        credentials: 'include'
      });

      const result = await response.json();

      if (response.ok) {
        this.user = result.user;
        this.subjects = result.subjects;
        this.scores = result.scores;
      } else {
        console.error("Failed to fetch user dashboard data:", result.error || 'Unknown error');
        window.alert(result.error || 'Error fetching dashboard data. Please log in.');
        this.$router.push('/login');
      }
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString();
    },
    async exportCSV() {
      const id = this.$route.params.id;
      const res = await fetch(`/user/${id}/export/my_csv`, {
        method: 'GET',
        credentials: 'include'
      });
      const result = await res.json();
      window.alert(result.message || "Export started! You'll receive the email shortly.");
    },
    async logout() {
      await fetch('/logout', {
        method: 'GET',
        credentials: 'include'
      });
      this.$router.push('/login');
    }
  },
  mounted() {
    this.fetchData();
  }
};
</script>