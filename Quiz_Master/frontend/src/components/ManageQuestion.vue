<template>
  <div class="container mt-5">
    <h2>Manage Questions for Quiz {{ quizId }}</h2>
    <router-link :to="`/admin/dashboard`" class="btn btn-secondary mb-3">Back to Dashboard</router-link>
    <form @submit.prevent="createQuestion" class="mb-4">
      <div class="form-group">
        <label>Question Statement</label>
        <textarea v-model="form.question_statement" class="form-control" required></textarea>
      </div>
      <div class="form-group">
        <label>Option 1</label>
        <input v-model="form.option1" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Option 2</label>
        <input v-model="form.option2" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Option 3</label>
        <input v-model="form.option3" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Option 4</label>
        <input v-model="form.option4" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Correct Option (1-4)</label>
        <input type="number" v-model="form.correct_option" class="form-control" min="1" max="4" required />
      </div>
      <div class="form-group">
        <label>Marks for this Question</label>
        <input type="number" v-model="form.marks" class="form-control" min="1" required />
      </div>
      <button type="submit" class="btn btn-primary">Add Question</button>
    </form>

    <h4>All Questions</h4>
    <div v-if="loadingQuestions">
      <p>Loading questions...</p>
    </div>
    <div v-else-if="questions.length === 0">
      <p>No questions added to this quiz yet.</p>
    </div>
    <table v-else class="table table-bordered">
      <thead>
        <tr>
          <th>Statement</th>
          <th>Options</th>
          <th>Correct</th>
          <th>Marks</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="question in questions" :key="question.id">
          <td>{{ question.question_statement }}</td>
          <td>
            <ol>
              <li v-for="(option, i) in question.options" :key="i">
                {{ option }}
              </li>
            </ol>
          </td>
          <td>{{ question.correct_option }}</td>
          <td>{{ question.marks }}</td>
          <td>
            <button @click="editQuestionPrompt(question)" class="btn btn-sm btn-warning mr-2">Edit</button>
            <button @click="deleteQuestion(question.id)" class="btn btn-sm btn-danger">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { apiFetch } from "@/services/api";
export default {
  name: 'ManageQuestion',
  props: ['quizId'],
  data() {
    return {
      chapterId: this.$route.params.chapterId,
      questions: [],
      form: {
        question_statement: '',
        option1: '',
        option2: '',
        option3: '',
        option4: '',
        correct_option: 1,
        marks: 1 
      },
      loadingQuestions: true,
    };
  },
  async mounted() {
    await this.fetchQuestions();
  },
  methods: {
    async fetchQuestions() {
      this.loadingQuestions = true;
      try {
        const res = await apiFetch(`/admin/quiz/${this.quizId}/questions`, {
          method:"GET"
        });
        const data = await res.json();
        if (res.ok) {
          this.questions = data;
        } else {
          window.alert(data.error || 'Unable to fetch questions. Please ensure you are logged in as Admin.');
          this.$router.push('/login');
        }
      } catch (error) {
        console.error('Error fetching questions:', error);
        window.alert('Network error or server unreachable while fetching questions.');
      } finally {
        this.loadingQuestions = false;
      }
    },
    async createQuestion() {
      try {
        const res = await apiFetch(`/admin/question/new/${this.quizId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          ,
          body: JSON.stringify(this.form)
        });

        const result = await res.json();
        if (res.ok) {
          window.alert(result.message || 'Question added');
          this.form = {
            question_statement: '',
            option1: '',
            option2: '',
            option3: '',
            option4: '',
            correct_option: 1,
            marks: 1
          };
          await this.fetchQuestions();
        } else {
          window.alert(result.error || 'Failed to add question');
        }
      } catch (error) {
        console.error('Error creating question:', error);
        window.alert('Network error or server unreachable while adding question.');
      }
    },
    async editQuestionPrompt(question) {
      const newStatement = window.prompt("Edit question statement:", question.question_statement);
      if (newStatement === null) return;

      const newOption1 = window.prompt("Edit Option 1:", question.options[0]);
      if (newOption1 === null) return;
      const newOption2 = window.prompt("Edit Option 2:", question.options[1]);
      if (newOption2 === null) return;
      const newOption3 = window.prompt("Edit Option 3:", question.options[2]);
      if (newOption3 === null) return;
      const newOption4 = window.prompt("Edit Option 4:", question.options[3]);
      if (newOption4 === null) return;

      let newCorrectOption = window.prompt("Edit correct option (1-4):", question.correct_option);
      if (newCorrectOption === null) return;
      newCorrectOption = parseInt(newCorrectOption);
      if (isNaN(newCorrectOption) || newCorrectOption < 1 || newCorrectOption > 4) {
        window.alert("Invalid correct option. Must be a number between 1 and 4.");
        return;
      }

      let newMarks = window.prompt("Edit marks for this question:", question.marks);
      if (newMarks === null) return;
      newMarks = parseInt(newMarks);
      if (isNaN(newMarks) || newMarks < 1) {
        window.alert("Invalid marks. Must be a positive number.");
        return;
      }

      try {
        const res = await apiFetch(`/admin/question/edit/${question.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          ,
          body: JSON.stringify({
            question_statement: newStatement,
            option1: newOption1,
            option2: newOption2,
            option3: newOption3,
            option4: newOption4,
            correct_option: newCorrectOption,
            marks: newMarks
          })
        });

        const result = await res.json();
        if (res.ok) {
          window.alert(result.message || 'Question updated');
          await this.fetchQuestions();
        } else {
          window.alert(result.error || 'Failed to update question');
        }
      } catch (error) {
        console.error('Error editing question:', error);
        window.alert('Network error or server unreachable while editing question.');
      }
    },
    async deleteQuestion(id) {
      if (!window.confirm("Delete this question?")) return;
      try {
        const res = await apiFetch(`/admin/question/delete/${id}`, {
          method: 'DELETE',
          
        });
        const result = await res.json();
        if (res.ok) {
          window.alert(result.message || 'Question deleted');
          await this.fetchQuestions();
        } else {
          window.alert(result.error || 'Failed to delete question');
        }
      } catch (error) {
        console.error('Error deleting question:', error);
        window.alert('Network error or server unreachable while deleting question.');
      }
    }
  }
};
</script>
