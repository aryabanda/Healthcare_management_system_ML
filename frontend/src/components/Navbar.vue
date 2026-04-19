<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- Brand Logo -->
      <router-link to="/" class="nav-brand">
        🏥 HMS Portal
      </router-link>

      <!-- Navigation Links -->
      <div class="nav-links">
        <!-- Admin Links -->
        <template v-if="isAdmin">
          <router-link to="/admin/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/admin/departments" class="nav-link">Departments</router-link>
          <router-link to="/admin/doctors" class="nav-link">Doctors</router-link>
          <router-link to="/admin/patients" class="nav-link">Patients</router-link>
          <router-link to="/admin/reports" class="nav-link">Reports</router-link>
        </template>

        <!-- Doctor Links -->
        <template v-if="isDoctor">
          <router-link to="/doctor/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/doctor/appointments" class="nav-link">Appointments</router-link>
          <router-link to="/doctor/profile" class="nav-link">Profile</router-link>
          <router-link to="/doctor/availability" class="nav-link">Availability</router-link>
        </template>

        <!-- Patient Links -->
        <template v-if="isPatient">
          <router-link to="/patient/dashboard" class="nav-link">Dashboard</router-link>
          <router-link to="/patient/appointments" class="nav-link">My Appointments</router-link>
          <router-link to="/patient/profile" class="nav-link">Profile</router-link>
          <router-link to="/patient/history" class="nav-link">My History</router-link>
          <router-link to="/patient/reports" class="nav-link">My Reports</router-link>
        </template>

        <!-- Logout Button -->
        <button @click="handleLogout" class="logout-btn">
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
import { logout } from "@/store/auth.js";

export default {
  name: "NavBar",
  props: {
    userRole: {
      type: String,
      required: true
    },
    userName: {
      type: String,
      default: "User"
    }
  },
  computed: {
    isAdmin() {
      return this.userRole === "admin";
    },
    isDoctor() {
      return this.userRole === "doctor";
    },
    isPatient() {
      return this.userRole === "patient";
    }
  },
  methods: {
    handleLogout() {
      logout();
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
.navbar {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  border-bottom: 1px solid #eaeaea;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.nav-brand {
  margin-right: 200px;
  font-size: 1.5rem;
  font-weight: bold;
  color: #3498db;
  text-decoration: none;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-link {
  color: #555;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background: #f8f9fa;
  color: #3498db;
}

.nav-link.router-link-active {
  background: #3498db;
  color: white;
}

.logout-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s ease;
}

.logout-btn:hover {
  background: #c0392b;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .navbar {
    padding: 1rem;
  }
  
  .nav-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
    gap: 1rem;
  }
  
  .nav-link {
    padding: 0.5rem;
    font-size: 0.9rem;
  }
}
</style>