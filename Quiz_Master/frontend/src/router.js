import { createRouter, createWebHistory } from 'vue-router'

import Index from './components/Index.vue';
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import UserDashboard from './components/UserDashboard.vue'
import AdminDashboard from './components/AdminDashboard.vue'
import ManageSubject from './components/ManageSubject.vue'
import ManageChapter from './components/ManageChapter.vue'
import ManageQuiz from './components/ManageQuiz.vue'
import ManageQuestion from './components/ManageQuestion.vue'
import QuizList from './components/QuizList.vue'
import QuizPage from './components/QuizPage.vue'
import ViewAttempts from './components/ViewAttempts.vue'

const routes = [
  { path: '/', component: Index },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/user/:id/dashboard', component: UserDashboard },
  { path: '/user/:id/quizzes/:subjectId', component: QuizList },
  { path: '/user/:id/quiz/:quizId', component: QuizPage },
  { path: '/admin/dashboard', component: AdminDashboard },
  { path: '/admin/manage-subject', component: ManageSubject },
  {
    path: '/admin/subject/:subjectId/chapters',
    name: 'ManageChaptersForSubject',
    component: ManageChapter,
    props: true
  },
  {
    path: '/admin/chapter/:chapterId/quizzes',
    component: ManageQuiz,
    props: true
  },
  {
    path: '/admin/quiz/:quizId/questions',
    component: ManageQuestion,
    props: true
  },
  { path: '/admin/attempts', component: ViewAttempts }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router