<template>
  <div class="container mt-5">
    <h2>Manage Chapters for Subject ID: {{ subjectId || 'Loading...' }}</h2>
    <router-link :to="`/admin/manage-subject`" class="btn btn-secondary mb-3">Back to Subject Management</router-link>

    <form @submit.prevent="createChapter" class="mb-4">
      <h3>Create New Chapter</h3>
      <div class="form-group">
        <label>Name</label>
        <input v-model="form.name" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Description</label>
        <textarea v-model="form.description" class="form-control" required></textarea>
      </div>
      <button class="btn btn-primary">Create Chapter</button>
    </form>

    <h4>Chapters</h4>
    <table class="table">
      <thead><tr><th>Name</th><th>Description</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-for="chapter in chapters" :key="chapter.id">
          <td>{{ chapter.name }}</td>
          <td>{{ chapter.description }}</td>
          <td>
            <router-link :to="`/admin/chapter/${chapter.id}/quizzes`" class="btn btn-sm btn-info">Manage Quizzes</router-link>
            <button @click="startEditChapter(chapter)" class="btn btn-sm btn-warning ml-2">Edit</button>
            <button @click="deleteChapter(chapter.id)" class="btn btn-sm btn-danger ml-2">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editingChapter" class="modal-overlay">
      <div class="modal-content">
        <h3>Edit Chapter</h3>
        <form @submit.prevent="saveEditChapter">
          <div class="form-group">
            <label>Name</label>
            <input v-model="editingChapter.name" class="form-control" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editingChapter.description" class="form-control" required></textarea>
          </div>
          <button type="submit" class="btn btn-success">Save Changes</button>
          <button type="button" @click="cancelEditChapter" class="btn btn-secondary ml-2">Cancel</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
const FLASK_BASE_URL = 'http://localhost:5000';

export default {
  name: 'ManageChapter',
  props: ['subjectId'],
  data() {
    return {
      chapters: [],
      form: { name: '', description: '' },
      editingChapter: null // Holds the chapter object being edited
    };
  },
  watch: {
    subjectId: {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.fetchChapters();
        }
      }
    }
  },
  methods: {
    async fetchChapters() {
      if (!this.subjectId) {
        console.warn('subjectId is not available for fetching chapters.');
        return;
      }
      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/subject/${this.subjectId}/chapters`, {
          method: 'GET',
          credentials: 'include'
        });

        const data = await res.json();
        if (!res.ok) {
          console.error('Failed to load chapters:', data.error || 'Unknown error');
          window.alert(data.error || 'Error fetching chapters. Please ensure you are logged in as Admin.');
          this.$router.push('/login');
          return;
        }

        this.chapters = data.chapters || [];
      } catch (err) {
        console.error('Network error during fetchChapters:', err);
        window.alert('Network error or server unreachable while fetching chapters.');
      }
    },
    async createChapter() {
      if (!this.subjectId) {
        console.warn('subjectId is not available for creating chapter.');
        window.alert('Cannot create chapter: Subject ID is missing.');
        return;
      }
      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/chapter/new/${this.subjectId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(this.form)
        });

        const result = await res.json();
        if (!res.ok) {
          console.error('Failed to create chapter:', result.error || 'Unknown error');
          window.alert(result.error || 'Error creating chapter. Please check your input and admin status.');
          return;
        }

        window.alert(result.message || 'Chapter created successfully!');
        this.form.name = '';
        this.form.description = '';
        await this.fetchChapters();
      } catch (err) {
        console.error('Network error during createChapter:', err);
        window.alert('Network error or server unreachable while creating chapter.');
      }
    },
    startEditChapter(chapter) {
      this.editingChapter = { ...chapter };
    },
    async saveEditChapter() {
      if (!this.editingChapter) return;

      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/chapter/edit/${this.editingChapter.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            name: this.editingChapter.name,
            description: this.editingChapter.description
          })
        });

        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to update chapter:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to update chapter.');
          return;
        }
        window.alert(result.message || 'Chapter updated');
        this.editingChapter = null;
        await this.fetchChapters();
      } catch (error) {
        console.error('Error updating chapter:', error);
        window.alert('Network error while updating chapter. Server might be down.');
      }
    },
    cancelEditChapter() {
      this.editingChapter = null;
    },
    async deleteChapter(id) {
      if (!window.confirm("Are you sure you want to delete this chapter? This action cannot be undone.")) {
        console.log("Chapter deletion cancelled by user.");
        return;
      }

      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/chapter/delete/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        });

        const result = await res.json();
        if (!res.ok) {
          console.error('Failed to delete chapter:', result.error || 'Unknown error');
          window.alert(result.error || 'Error deleting chapter. Please ensure you are authorized.');
          return;
        }

        window.alert(result.message || 'Chapter deleted successfully!');
        await this.fetchChapters();
      } catch (err) {
        console.error('Network error during deleteChapter:', err);
        window.alert('Network error or server unreachable while deleting chapter.');
      }
    }
  },
};
</script>
