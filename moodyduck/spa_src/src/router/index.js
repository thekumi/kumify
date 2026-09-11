import { createRouter, createWebHistory } from 'vue-router'
import { isLoggedIn } from '@/api/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },

  { path: '/',           component: () => import('@/views/DashboardView.vue') },

  { path: '/mood',                              component: () => import('@/views/mood/StatusListView.vue') },
  { path: '/mood/new',                          component: () => import('@/views/mood/StatusFormView.vue') },
  { path: '/mood/:id',                          component: () => import('@/views/mood/StatusDetailView.vue') },
  { path: '/mood/:id/edit',                     component: () => import('@/views/mood/StatusFormView.vue') },
  { path: '/mood/settings',                      component: () => import('@/views/mood/MoodSettingsView.vue') },
  { path: '/mood/settings/moods',               component: () => import('@/views/mood/MoodsView.vue') },
  { path: '/mood/settings/moods/new',           component: () => import('@/views/mood/MoodFormView.vue') },
  { path: '/mood/settings/moods/:id/edit',      component: () => import('@/views/mood/MoodFormView.vue') },
  { path: '/mood/settings/activities',          component: () => import('@/views/mood/ActivitiesView.vue') },
  { path: '/mood/settings/activities/new',      component: () => import('@/views/mood/ActivityFormView.vue') },
  { path: '/mood/settings/activities/:id/edit', component: () => import('@/views/mood/ActivityFormView.vue') },

  { path: '/journal',           component: () => import('@/views/journal/JournalView.vue') },
  { path: '/journal/dreams',         component: () => import('@/views/journal/DreamListView.vue') },
  { path: '/journal/dreams/new',     component: () => import('@/views/journal/DreamFormView.vue') },
  { path: '/journal/dreams/themes',  component: () => import('@/views/journal/ThemesView.vue') },
  { path: '/journal/dreams/themes/new', component: () => import('@/views/journal/ThemeFormView.vue') },
  { path: '/journal/dreams/themes/:id/edit', component: () => import('@/views/journal/ThemeFormView.vue') },
  { path: '/journal/dreams/:id',     component: () => import('@/views/journal/DreamDetailView.vue') },
  { path: '/journal/dreams/:id/edit', component: () => import('@/views/journal/DreamFormView.vue') },
  { path: '/journal/cbt',       component: () => import('@/views/journal/CbtListView.vue') },
  { path: '/journal/cbt/new',   component: () => import('@/views/journal/CbtFormView.vue') },
  { path: '/journal/cbt/:id',   component: () => import('@/views/journal/CbtDetailView.vue') },
  { path: '/journal/cbt/:id/edit', component: () => import('@/views/journal/CbtFormView.vue') },

  { path: '/health',                     component: () => import('@/views/health/HealthView.vue') },
  { path: '/health/logs',                component: () => import('@/views/health/LogsView.vue') },
  { path: '/health/logs/new',            component: () => import('@/views/health/LogFormView.vue') },
  { path: '/health/logs/:id/edit',       component: () => import('@/views/health/LogFormView.vue') },
  { path: '/health/medications',         component: () => import('@/views/health/MedicationsView.vue') },
  { path: '/health/medications/new',     component: () => import('@/views/health/MedicationFormView.vue') },
  { path: '/health/medications/:id/edit',component: () => import('@/views/health/MedicationFormView.vue') },
  { path: '/health/vaccinations',        component: () => import('@/views/health/VaccinationsView.vue') },
  { path: '/health/vaccinations/new',    component: () => import('@/views/health/VaccinationFormView.vue') },
  { path: '/health/vaccinations/:id/edit',component: () => import('@/views/health/VaccinationFormView.vue') },
  { path: '/health/habits',                       component: () => import('@/views/health/HabitsView.vue') },
  { path: '/health/parameters',                   component: () => import('@/views/health/ParametersView.vue') },
  { path: '/health/parameters/new',               component: () => import('@/views/health/ParameterFormView.vue') },
  { path: '/health/parameters/:id/edit',          component: () => import('@/views/health/ParameterFormView.vue') },

  { path: '/people',          component: () => import('@/views/people/PeopleView.vue') },
  { path: '/people/new',      component: () => import('@/views/people/PersonFormView.vue') },
  { path: '/people/:id/edit', component: () => import('@/views/people/PersonFormView.vue') },

  { path: '/me',         component: () => import('@/views/me/MeView.vue') },
  { path: '/me/profile', component: () => import('@/views/me/ProfileView.vue') },
  { path: '/me/devices',    component: () => import('@/views/me/DevicesView.vue') },
  { path: '/me/key-backup', component: () => import('@/views/me/KeyBackupView.vue') },
  { path: '/me/security',   component: () => import('@/views/me/SecurityView.vue') },
  { path: '/me/emergency',  component: () => import('@/views/me/EmergencyView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  if (!to.meta.public && !isLoggedIn()) return '/login'
})

export default router
