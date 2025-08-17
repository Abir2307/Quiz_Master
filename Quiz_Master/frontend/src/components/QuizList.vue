<template>
  <div class="container mt-5">
    <h2>Quizzes for {{ subject.name || 'Loading Subject...' }}</h2>
    <router-link :to="`/user/${userId}/dashboard`" class="btn btn-secondary mb-3">Back to Dashboard</router-link>

    <div v-if="quizzes.length === 0 && !loading">
      <p>No quizzes available for this subject yet.</p>
    </div>
    <div v-else-if="loading">
      <p>Loading quizzes...</p>
    </div>

    <table v-else class="table table-hover">
      <thead>
        <tr>
          <th>Quiz ID</th>
          <th>Chapter</th>
          <th>Date</th>
          <th>Time Duration</th>
          <th>Remarks</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="quiz in quizzes" :key="quiz.id">
          <td>{{ quiz.id }}</td>
          <td>{{ quiz.chapter_id }}</td>
          <td>{{ formatDate(quiz.date_of_quiz) }}</td>
          <td>{{ quiz.time_duration }}</td>
          <td>{{ quiz.remarks }}</td>
          <td>
            <router-link v-if="isQuizAvailable(quiz.date_of_quiz)" :to="`/user/${userId}/quiz/${quiz.id}`" class="btn btn-primary btn-sm">Take Quiz</router-link>
            <span v-else class="text-muted">Quiz Unavailable</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
const FLASK_BASE_URL = 'http://localhost:5000'; // Consistent base URL

export default {
  name: 'QuizList',
  data() {
    return {
      quizzes: [],
      subject: {},
      userId: this.$route.params.id,
      subjectId: this.$route.params.subjectId,
      loading: true,
      error: null
    };
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler(newId) {
        this.userId = newId;
        this.fetchData();
      }
    },
    '$route.params.subjectId': {
      immediate: true,
      handler(newSubjectId) {
        this.subjectId = newSubjectId;
        this.fetchData();
      }
    }
  },
  methods: {
    async fetchData() {
      if (!this.userId || !this.subjectId) {
        console.warn('User ID or Subject ID is missing. Cannot fetch quizzes.');
        this.loading = false;
        return;
      }

      this.loading = true;
      this.error = null;
      try {
        const subjectRes = await fetch(`${FLASK_BASE_URL}/subjects/${this.subjectId}`, 
        {
          credentials: 'include'
        });
        if (!subjectRes.ok) {
          throw new Error('Failed to fetch subject details.');
        }
        const subjectData = await subjectRes.json();
        this.subject = subjectData.subject || { name: 'Unknown Subject' };

        const quizRes = await fetch(`${FLASK_BASE_URL}/user/${this.userId}/quizzes/${this.subjectId}`, {
          credentials: 'include'
        });
        if (!quizRes.ok) {
          throw new Error('Failed to fetch quizzes.');
        }
        this.quizzes = await quizRes.json();
        console.log('Fetched quizzes:', this.quizzes);

      } catch (err) {
        console.error('Error fetching quiz list:', err);
        this.error = err.message || 'Network error or server unreachable while fetching quizzes.';
        window.alert(this.error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(date) {
      if (!date) return '';
      return new Date(date).toLocaleDateString();
    },
    isQuizAvailable(date) {
      if (!date) return false;
      const quizDate = new Date(date);
      const today = new Date();
      return quizDate <= today;
    }
  }
};
</script>
