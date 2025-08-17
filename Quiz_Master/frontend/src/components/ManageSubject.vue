<template>
  <div class="container mt-5">
    <h2>Manage Subjects</h2>
    <router-link :to="`/admin/dashboard`" class="btn btn-secondary mb-3">Back to Dashboard</router-link>
    <form @submit.prevent="createSubject" class="mb-4">
      <h3>Create New Subject</h3>
      <div class="form-group">
        <label>Name</label>
        <input v-model="form.name" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Description</label>
        <textarea v-model="form.description" class="form-control" required></textarea>
      </div>
      <button class="btn btn-primary">Create Subject</button>
    </form>

    <h4>All Subjects</h4>
    <table class="table">
      <thead>
        <tr><th>Name</th><th>Description</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>{{ subject.name }}</td>
          <td>{{ subject.description }}</td>
          <td>
            <router-link :to="`/admin/subject/${subject.id}/chapters`" class="btn btn-sm btn-info">Manage Chapters</router-link>
            <button @click="startEditSubject(subject)" class="btn btn-sm btn-warning ml-2">Edit</button>
            <button @click="deleteSubject(subject.id)" class="btn btn-sm btn-danger ml-2">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="editingSubject" class="modal-overlay">
      <div class="modal-content">
        <h3>Edit Subject</h3>
        <form @submit.prevent="saveEditSubject">
          <div class="form-group">
            <label>Name</label>
            <input v-model="editingSubject.name" class="form-control" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editingSubject.description" class="form-control" required></textarea>
          </div>
          <button type="submit" class="btn btn-success">Save Changes</button>
          <button type="button" @click="cancelEditSubject" class="btn btn-secondary ml-2">Cancel</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
const FLASK_BASE_URL = 'http://localhost:5000';

export default {
  name: 'ManageSubject',
  data() {
    return {
      subjects: [],
      form: { name: '', description: '' },
      editingSubject: null
    };
  },
  methods: {
    async fetchSubjects() {
      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/dashboard`, {
          method: 'GET',
          credentials: 'include'
        });

        const data = await res.json();
        if (!res.ok) {
          console.error("Failed to fetch subjects:", data.error || 'Unknown error');
          window.alert("Unable to fetch subjects. Please ensure you are logged in as Admin.");
          this.$router.push('/login');
          return;
        }
        this.subjects = data.subjects || [];
      } catch (error) {
        console.error('Error fetching subjects:', error);
        window.alert('Network error while fetching subjects. Server might be down.');
      }
    },
    async createSubject() {
      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/subject/new`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(this.form)
        });

        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to create subject:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to create subject.');
          return;
        }
        window.alert(result.message || 'Subject created');
        this.form.name = '';
        this.form.description = '';
        await this.fetchSubjects();
      } catch (error) {
        console.error('Error creating subject:', error);
        window.alert('Network error while creating subject. Server might be down.');
      }
    },
    startEditSubject(subject) {
      this.editingSubject = { ...subject };
    },
    async saveEditSubject() {
      if (!this.editingSubject) return;

      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/subject/edit/${this.editingSubject.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            name: this.editingSubject.name,
            description: this.editingSubject.description
          })
        });

        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to update subject:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to update subject.');
          return;
        }
        window.alert(result.message || 'Subject updated');
        this.editingSubject = null; 
        await this.fetchSubjects(); 
      } catch (error) {
        console.error('Error updating subject:', error);
        window.alert('Network error while updating subject. Server might be down.');
      }
    },
    cancelEditSubject() {
      this.editingSubject = null;
    },
    async deleteSubject(id) {
      if (!window.confirm("Are you sure you want to delete this subject? This action cannot be undone.")) {
        console.log("Subject deletion cancelled by user.");
        return;
      }

      try {
        const res = await fetch(`${FLASK_BASE_URL}/admin/subject/delete/${id}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        const result = await res.json();
        if (!res.ok) {
          console.error("Failed to delete subject:", result.error || 'Unknown error');
          window.alert(result.error || 'Failed to delete subject.');
          return;
        }
        window.alert(result.message || 'Subject deleted');
        await this.fetchSubjects();
      } catch (error) {
        console.error('Error deleting subject:', error);
        window.alert('Network error while deleting subject. Server might be down.');
      }
    }
  },
  mounted() {
    this.fetchSubjects();
  }
};
</script>
