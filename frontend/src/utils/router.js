import { createRouter, createWebHistory } from "vue-router";

// Public
import HomePage from "../../pages/HomePage.vue";
import RegisterPage from "../../pages/RegisterPage.vue";

// Admin
import AdminLoginPage from "../../pages/AdminLoginPage.vue";
import AdminDashboardPage from "../../pages/AdminDashboardPage.vue";
import AdminDoctorsPage from "../../pages/AdminDoctorsPage.vue";
import AdminPatientsPage from "../../pages/AdminPatientsPage.vue";
import AdminAppointmentsPage from "../../pages/AdminAppointmentsPage.vue";
import AdminReportsPage from "../../pages/AdminReportsPage.vue";
import AdminPatientHistoryPage from "../../pages/AdminPatientHistoryPage.vue";
import AdminPatientDetailsPage from "../../pages/AdminPatientDetailsPage.vue";
import AdminDepartmentsPage from "../../pages/AdminDepartments.vue";


// Doctor
import DoctorDashboardPage from "../../pages/DoctorDashboardPage.vue";
import DoctorProfilePage from "../../pages/DoctorProfilePage.vue";
import DoctorAppointmentsPage from "../../pages/DoctorAppointmentsPage.vue";
import DoctorAvailabilityPage from "../../pages/DoctorAvailabilityPage.vue";
import DoctorPatientHistoryPage from "../../pages/DoctorPatientHistoryPage.vue";

// Patient
import PatientDashboardPage from "../../pages/PatientDashboardPage.vue";
import PatientProfilePage from "../../pages/PatientProfilePage.vue";
import PatientDoctorsPage from "../../pages/PatientDoctorsPage.vue";
import PatientAppointmentsPage from "../../pages/PatientAppointmentsPage.vue";
import PatientTreatmentsPage from "../../pages/PatientTreatmentsPage.vue";
import DepartmentDetailsPage from "../../pages/DepartmentDetailsPage.vue";
import PatientBookAppointmentPage from "../../pages/PatientBookAppointmentPage.vue";
import PatientExportPage from "../../pages/PatientExportPage.vue";
import PatientHistoryPage from "../../pages/PatientHistoryPage.vue";

const routes = [
  // -- Public --
  { path: "/", component: HomePage },
  { path: "/register", component: RegisterPage },

  // -- Admin --
  { path: "/admin/login", component: AdminLoginPage },
  { path: "/admin/dashboard", component: AdminDashboardPage },
  { path: "/admin/doctors", component: AdminDoctorsPage },
  { path: "/admin/patients", component: AdminPatientsPage },
  { path: "/admin/appointments", component: AdminAppointmentsPage },
  { path: "/admin/reports", component: AdminReportsPage },
  { path: "/admin/departments", component: AdminDepartmentsPage },
  { path: "/admin/patient/:id/history", component: AdminPatientHistoryPage },
  { path: "/admin/patient/:id", component: AdminPatientDetailsPage },

  // -- Doctor --
  { path: "/doctor/dashboard", component: DoctorDashboardPage },
  { path: "/doctor/profile", component: DoctorProfilePage },
  { path: "/doctor/appointments", component: DoctorAppointmentsPage },
  { path: "/doctor/availability", component: DoctorAvailabilityPage },
  { path: "/doctor/patient/:id/history", component: DoctorPatientHistoryPage },

  // -- Patient --
  { path: "/patient/dashboard", component: PatientDashboardPage },
  { path: "/patient/profile", component: PatientProfilePage },
  { path: "/patient/doctors", component: PatientDoctorsPage },
  { path: "/patient/appointments", component: PatientAppointmentsPage },
  { path: "/patient/treatments", component: PatientTreatmentsPage },
  { path: "/department/:id", component: DepartmentDetailsPage },
  { path: "/book/:id", component: PatientBookAppointmentPage },
  { path: "/patient/reports", component: PatientExportPage },
  { path: "/patient/history", component: PatientHistoryPage },

  // -- Logout --
  {
    path: "/logout",
    component: {
      template: `
        <div class="text-center mt-5">
          <h3>Logging out...</h3>
        </div>
      `,
      mounted() {
        this.$root.logout();
      },
    },
  },

  // -- Fallback (Vue 3 syntax)
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
