<template>
  <div class="container mt-5">
    <h2>Quiz ID: {{ quizId || 'Loading...' }}</h2>
    <p>Please complete and submit before time runs out.</p>
    <h5>Time Left: <span class="text-danger">{{ timeLeft }}</span></h5>

    <form @submit.prevent="submitQuiz">
      <div v-if="loadingQuestions">
        <p>Loading questions...</p>
      </div>
      <div v-else-if="questions.length === 0">
        <p>No questions found for this quiz.</p>
      </div>
      <div v-else v-for="(question, index) in questions" :key="question.id" class="mb-4">
        <h5>Q{{ index + 1 }}. {{ question.question_statement }} ({{ question.marks }} Mark{{ question.marks !== 1 ? 's' : '' }})</h5>
        <div v-for="(option, i) in question.options" :key="i" class="form-check">
          <input
            class="form-check-input"
            type="radio"
            :name="'question_' + question.id"
            :value="i + 1"
            v-model="answers[question.id]"
            required
          />
          <label class="form-check-label">
            {{ option }}
          </label>
        </div>
      </div>

      <button type="submit" class="btn btn-success">Submit Quiz</button>
      <router-link :to="`/user/${userId}/dashboard`" class="btn btn-secondary ml-2">Cancel</router-link>
    </form>
  </div>
</template>

<script>
const FLASK_BASE_URL = 'http://localhost:5000';

export default {
  name: 'QuizPage',
  data() {
    return {
      quizId: this.$route.params.quizId,
      userId: this.$route.params.id,
      questions: [],
      answers: {},
      durationSeconds: 0,
      timer: null,
      timeLeft: '',
      loadingQuestions: true,
    };
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler(newId) {
        this.userId = newId;
        if (this.quizId) this.fetchData();
      }
    },
    '$route.params.quizId': {
      immediate: true,
      handler(newQuizId) {
        this.quizId = newQuizId;
        if (this.userId) this.fetchData();
      }
    }
  },
  beforeUnmount() {
    clearInterval(this.timer);
  },
  methods: {
    async fetchData() {
      if (!this.userId || !this.quizId) {
        console.warn('User ID or Quiz ID is missing. Cannot fetch quiz data.');
        this.loadingQuestions = false;
        return;
      }
      this.loadingQuestions = true;
      try {
        await this.fetchQuizMetadata(); 
        await this.fetchQuestions();   
        this.startTimer();
      } catch (error) {
        console.error('Error fetching quiz data:', error);
        window.alert(error.message || 'Failed to load quiz. Please try again.');
        this.$router.push(`/user/${this.userId}/dashboard`);
      } finally {
        this.loadingQuestions = false;
      }
    },
    async fetchQuizMetadata() {
      console.log(`DEBUG: Fetching quiz metadata for quizId: ${this.quizId}`);
      const res = await fetch(`${FLASK_BASE_URL}/quizzes/${this.quizId}`, {
        credentials: 'include'
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to fetch quiz metadata.');
      }
      const quiz = await res.json();

      const [mins, secs] = quiz.time_duration.split(':').map(Number);
      this.durationSeconds = mins * 60 + secs;
      console.log(`DEBUG: Quiz metadata fetched. Duration: ${this.durationSeconds} seconds.`);
    },
    async fetchQuestions() {
      console.log(`DEBUG: Fetching questions for quizId: ${this.quizId}`);
      const res = await fetch(`${FLASK_BASE_URL}/user/${this.userId}/quiz/${this.quizId}`, {
        method: 'GET',
        credentials: 'include'
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to fetch questions.');
      }
      this.questions = await res.json();

      this.questions.forEach(q => {
        this.answers[q.id] = null;
      });
      console.log('DEBUG: Questions fetched:', this.questions);
    },
    startTimer() {
      clearInterval(this.timer);
      let secondsLeft = this.durationSeconds;
      this.updateTimeDisplay(secondsLeft);

      this.timer = setInterval(() => {
        secondsLeft--;
        this.updateTimeDisplay(secondsLeft);

        if (secondsLeft <= 0) {
          clearInterval(this.timer);
          window.alert("Submitting your quiz.");
          this.submitQuiz(true);
        }
      }, 1000);
    },
    updateTimeDisplay(seconds) {
      if (seconds < 0) seconds = 0;
      const min = String(Math.floor(seconds / 60)).padStart(2, '0');
      const sec = String(seconds % 60).padStart(2, '0');
      this.timeLeft = `${min}:${sec}`;
    },
    async submitQuiz(autoSubmit = false) {
      clearInterval(this.timer);

      const payload = {
        answers: this.answers
      };

      console.log(`DEBUG: Submitting quiz ${this.quizId} for user ${this.userId}. Payload:`, payload);
      const res = await fetch(`${FLASK_BASE_URL}/user/${this.userId}/quiz/${this.quizId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(payload)
      });

      const result = await res.json();

      if (res.ok) {
        window.alert(`${autoSubmit ? 'Auto-submitted! ' : ''}Score: ${result.score}/${result.total_marks}`);
      } else {
        console.error('Submission failed:', result.error || 'Unknown error');
        window.alert(result.error || 'Submission failed');
      }

      this.$router.push(`/user/${this.userId}/dashboard`);
    }
  }
};
</script>
