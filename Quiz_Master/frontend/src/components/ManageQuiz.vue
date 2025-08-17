<template>
  <div class="container mt-5">
    <h2>Manage Quizzes for Chapter ID: {{ chapterId || 'Loading...' }}</h2>
    <router-link :to="`/admin/dashboard`" class="btn btn-secondary mb-3">Back to Dashboard</router-link>

    <form @submit.prevent="createQuiz" class="mb-4">
      <h3>Create New Quiz</h3>
      <div class="form-group">
        <label>Date of Quiz</label>
        <input v-model="form.date_of_quiz" type="date" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Time Duration (MM:SS)</label>
        <input v-model="form.time_duration" type="text" class="form-control" placeholder="e.g., 01:30" required />
      </div>
      <div class="form-group">
        <label>Remarks</label>
        <textarea v-model="form.remarks" class="form-control"></textarea>
      </div>
      <button class="btn btn-primary">Create Quiz</button>
    </form>

    <h4>All Quizzes</h4>
    <table class="table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Duration</th>
          <th>Remarks</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="quiz in quizzes" :key="quiz.id">
          <td>{{ quiz.date_of_quiz }}</td>
          <td>{{ quiz.time_duration }}</td>
          <td>{{ quiz.remarks }}</td>
          <td>
            <router-link :to="`/admin/quiz/${quiz.id}/questions`" class="btn btn-sm btn-info">Manage Questions</router-link>
            <button @click="startEditQuiz(quiz)" class="btn btn-sm btn-warning ml-2">Edit</button>
            <button @click="deleteQuiz(quiz.id)" class="btn btn-sm btn-danger ml-2">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editingQuiz" class="modal-overlay">
      <div class="modal-content">
        <h3>Edit Quiz</h3>
        <form @submit.prevent="saveEditQuiz">
          <div class="form-group">
            <label>Date of Quiz</label>
            <input v-model="editingQuiz.date_of_quiz" type="date" class="form-control" required />
          </div>
          <div class="form-group">
            <label>Time Duration(MM:SS)</label>
            <input v-model="editingQuiz.time_duration" type="text" class="form-control" placeholder="e.g., 01:30" required />
          </div>
          <div class="form-group">
            <label>Remarks</label>
            <textarea v-model="editingQuiz.remarks" class="form-control"></textarea>
          </div>
          <button type="submit" class="btn btn-success">Save Changes</button>
          <button type="button" @click="cancelEditQuiz" class="btn btn-secondary ml-2">Cancel</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
const FLASK_BASE_URL = 'http://localhost:5000';

export default {
  name: 'ManageQuiz',
  props: ['chapterId'],
  data() {
    return {
      quizzes: [],
      form: {
        date_of_quiz: '',
        time_duration: '',
        remarks: ''
      },
      editingQuiz: null
    };
  },
  watch: {
    chapterId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.fetchQuizzes();
        }
      }
    }
  },
  methods: {
    async fetchQuizzes() {
      if (!this.chapterId) {
        console.warn('chapterId is not available for fetching quizzes. Skipping fetch.');
        return;
      }
      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/chapter/${this.chapterId}/quizzes`, {
          method: 'GET',
          credentials: 'include'
        });

        const data = await res.json();
        if (!res.ok) {
          console.error('Failed to load quizzes:', data.error || 'Unknown error');
          window.alert(data.error || 'Error fetching quizzes. Please ensure you are logged in as Admin.');
          this.$router.push('/login');
          return;
        }
        this.quizzes = data.quizzes || [];
      } catch (error) {
        console.error('Network error during fetchQuizzes:', error);
        window.alert('Network error or server unreachable while fetching quizzes. Check Flask server and endpoint.');
      }
    },
    async createQuiz() {
      if (!this.chapterId) {
        console.warn('chapterId is not available for creating quiz.');
        window.alert('Cannot create quiz: Chapter ID is missing.');
        return;
      }
      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/quiz/new/${this.chapterId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(this.form)
        });

        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to create quiz:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to create quiz.');
          return;
        }
        window.alert(result.message || 'Quiz created');
        this.form = { date_of_quiz: '', time_duration: '', remarks: '' }; // Reset form
        await this.fetchQuizzes();
      } catch (error) {
        console.error('Error creating quiz:', error);
        window.alert('Network error while creating quiz. Server might be down.');
      }
    },
    startEditQuiz(quiz) {
      console.log("DEBUG: startEditQuiz called with quiz:", quiz);

      this.editingQuiz = { ...quiz, date_of_quiz: quiz.date_of_quiz.split('T')[0] };
      console.log("DEBUG: editingQuiz set to:", this.editingQuiz);
    },
    async saveEditQuiz() {
      if (!this.editingQuiz) return;

      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/quiz/edit/${this.editingQuiz.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            date_of_quiz: this.editingQuiz.date_of_quiz,
            time_duration: this.editingQuiz.time_duration,
            remarks: this.editingQuiz.remarks
          })
        });

        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to update quiz:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to update quiz.');
          return;
        }
        window.alert(result.message || 'Quiz updated');
        this.editingQuiz = null;
        await this.fetchQuizzes();
      } catch (error) {
        console.error('Error updating quiz:', error);
        window.alert('Network error while updating quiz. Server might be down.');
      }
    },
    cancelEditQuiz() {
      this.editingQuiz = null; 
    },
    async deleteQuiz(id) {
      if (!window.confirm("Are you sure you want to delete this quiz?")) return;

      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/quiz/delete/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to delete quiz:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to delete quiz.');
          return;
        }
        window.alert(result.message || 'Quiz deleted');
        await this.fetchQuizzes();
      } catch (error) {
        console.error('Error deleting quiz:', error);
        window.alert('Network error while deleting quiz. Server might be down.');
      }
    }
  },
};
</script>
