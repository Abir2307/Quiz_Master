<template>
  <div class="container mt-5">
    <h2>All Quiz Attempts</h2>
    <router-link to="/admin/dashboard" class="btn btn-info mb-3">Back to Admin Dashboard</router-link>
    <div v-if="loading" class="alert alert-info" role="alert">
      <p>Loading quiz attempts...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <p>Error: {{ error }}</p>
      <p>Please ensure you are logged in as Admin and the backend server is running.</p>
    </div>
    <div v-else-if="attempts.length === 0" class="alert alert-warning" role="alert">
      <p>No quiz attempts found yet. Users need to take quizzes for data to appear here.</p>
    </div>
    
    <table v-else class="table table-bordered mt-3">
      <thead class="thead-dark">
        <tr>
          <th>User ID</th>
          <th>User Name</th>
          <th>Full Name</th>
          <th>Quiz ID</th>
          <th>Subject Name</th>
          <th>Score</th>
          <th>Total Marks</th>
          <th>Attempted On</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="attempt in attempts" :key="attempt.user_id + '-' + attempt.quiz_id + '-' + attempt.timestamp">
          <td>{{ attempt.user_id }}</td>
          <td>{{ attempt.username }}</td>
          <td>{{ attempt.full_name }}</td>
          <td>{{ attempt.quiz_id }}</td>
          <td>{{ attempt.subject_name }}</td>
          <td>{{ attempt.score }}</td>
          <td>{{ attempt.total_marks }}</td>
          <td>{{ formatTimestamp(attempt.timestamp) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { apiFetch } from "@/services/api";
export default {
  name: 'ViewAttempts',
  data() {
    return {
      attempts: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    this.loading = true;
    this.error = null;
    try {
      console.log('DEBUG: ViewAttempts - Attempting to fetch attempts from:', `${FLASK_BASE_URL}/admin/attempts`);
      const res = await apiFetch(`/admin/attempts`, {
        method: 'GET'
      });

      const data = await res.json();
      if (res.ok) {
        this.attempts = data;
        console.log('DEBUG: ViewAttempts - Attempts fetched successfully. Count:', this.attempts.length);
      } else {
        console.error('DEBUG: ViewAttempts - Failed to load attempts. Status:', res.status, 'Error:', data.error || 'Unknown error');
        this.error = data.error || `Failed to load attempts (Status: ${res.status}).`;
        if (res.status === 401 || res.status === 403) {
          window.alert(this.error + " Redirecting to login.");
          this.$router.push('/login');
        } else {
          window.alert(this.error);
        }
      }
    } catch (error) {
      console.error('DEBUG: ViewAttempts - Network error during fetch attempts:', error);
      this.error = 'Network error or server unreachable while fetching attempts. Please check Flask server.';
      window.alert(this.error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    formatTimestamp(ts) {
      if (!ts) return '';
      try {
        return new Date(ts).toLocaleString();
      } catch (e) {
        console.error("Error formatting timestamp:", ts, e);
        return 'Invalid Date';
      }
    }
  }
};
</script>
