<template>
  <div class="container mt-5">
    <h2>Welcome, Admin</h2>

    <div class="d-flex justify-content-between align-items-center mb-3">
      <input type="text" v-model="searchQuery" @input="search" placeholder="Search..." class="form-control w-50" />
      <div>
        <router-link to="/admin/manage-subject" class="btn btn-primary mr-2">Manage Subjects</router-link>
        <router-link to="/admin/attempts" class="btn btn-secondary mr-2">View Attempts</router-link>
        <button class="btn btn-success" @click="exportCSV">Export All CSV</button>
        <button @click="logout" class="btn btn-danger float-right">Logout</button>
      </div>
    </div>

    <h4>Subjects</h4>
    <table class="table table-bordered">
      <thead><tr><th>Name</th><th>Description</th></tr></thead>
      <tbody>
        <tr v-for="subject in filteredSubjects" :key="subject.id">
          <td>{{ subject.name }}</td>
          <td>{{ subject.description }}</td>
        </tr>
      </tbody>
    </table>

    <h4>Registered Users</h4>
    <table class="table table-striped">
      <thead><tr><th>Username</th><th>Full Name</th><th>Qualification</th></tr></thead>
      <tbody>
        <tr v-for="user in filteredUsers" :key="user.id">
          <td>{{ user.username }}</td>
          <td>{{ user.full_name }}</td>
          <td>{{ user.qualification }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  name: 'AdminDashboard',
  data() {
    return {
      subjects: [],
      users: [],
      searchQuery: '',
      filteredSubjects: [],
      filteredUsers: []
    };
  },
  async mounted() {
  try {
    const res = await fetch('/admin/dashboard', { credentials: 'include' });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || 'Failed to fetch admin dashboard');
    }

    const data = await res.json();

    this.subjects = data.subjects || [];
    this.users = data.users || [];
    this.filteredSubjects = this.subjects;
    this.filteredUsers = this.users;

  } catch (error) {
    console.error('Error fetching admin dashboard data:', error);
    alert(error.message || 'Error loading dashboard. Please log in as Admin.');
    this.$router.push('/login');
  }
},
  methods: {
    search() {
      const query = this.searchQuery.toLowerCase();
      this.filteredSubjects = this.subjects.filter(s =>
        s.name.toLowerCase().includes(query)
      );
      this.filteredUsers = this.users.filter(u =>
        u.username.toLowerCase().includes(query) || u.full_name.toLowerCase().includes(query)
      );
    },
    async exportCSV() {
      try {
        const response = await fetch('/admin/export/csv', {
          method: 'GET',
          credentials: 'include'
        });
        const result = await response.json();
        alert(result.message || 'Export process initiated.');
        if (!response.ok) {
          throw new Error(result.error || 'Failed to start export');
        }
      } catch (error) {
        console.error('Error exporting CSV:', error);
        alert(error.message || 'Error initiating CSV export. Please ensure you are logged in as Admin. Check if backend is running and proxy is configured.');
      }
    },
    async logout() {
      await fetch('/logout', {
        method: 'GET',
        credentials: 'include'
      });
      this.$router.push('/login');
    }
  }
};
</script>
