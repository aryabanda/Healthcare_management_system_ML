<template>
  <div class="patient-dashboard">
    <!-- Header -->
    <header class="page-header">
      <h1>Welcome back, {{ patient || 'Patient' }}! 👋</h1>
      <p>Find and book appointments with our specialist doctors</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Dashboard Content -->
    <div class="dashboard-content">
      <!-- Quick Stats -->
      <div class="stats-section">
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon">
              <span>🏥</span>
            </div>
            <div class="stat-content">
              <h3>{{ departments.length }}</h3>
              <p>Available Departments</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <span>👨‍⚕️</span>
            </div>
            <div class="stat-content">
              <h3>{{ totalDoctors }}</h3>
              <p>Specialist Doctors</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <span>📅</span>
            </div>
            <div class="stat-content">
              <h3>24/7</h3>
              <p>Available Hours</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Departments Section -->
      <section class="departments-section">
        <div class="section-header">
          <h2>Medical Departments</h2>
          <p class="section-description">
            Choose a department to view available specialists and book appointments
          </p>
        </div>

        <!-- No Departments -->
        <div v-if="departments.length === 0" class="empty-state">
          <div class="empty-icon">🏥</div>
          <h3>No Departments Available</h3>
          <p>There are currently no medical departments available for booking.</p>
        </div>

        <!-- Departments Grid -->
        <div v-else class="departments-grid">
          <div 
            v-for="dept in departments" 
            :key="dept.id" 
            class="department-card"
            @click="deptDetails(dept.id)"
          >
            <div class="department-header">
              <div class="department-icon">
                <span>{{ getDepartmentIcon(dept.name) }}</span>
              </div>
              <div class="department-info">
                <h3 class="department-name">{{ dept.name }}</h3>
                <span class="department-id">ID: {{ dept.id }}</span>
              </div>
            </div>
            
            <div class="department-description">
              <p>{{ dept.description || "Comprehensive medical care and specialist consultations" }}</p>
            </div>

            <div class="department-actions">
              <button class="view-btn">
                View Specialists →
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  name: "PatientDashboard",

  data() {
    return {
      message: null,
      category: null,
      patient: "",
      departments: []
    };
  },

  computed: {
    totalDoctors() {
      // This would typically come from the backend
      // For now, we'll estimate based on departments
      return this.departments.length * 3;
    }
  },

  mounted() {
    this.fetchDashboard();
  },

  methods: {
    /** Load dashboard data from backend **/
    async fetchDashboard() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/patient/dashboard`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        const data = await res.json();

        if (res.ok) {
          this.patient = data.patient;
          this.message = data.message;
          this.category = data.category;
          this.departments = data.departments || [];
        } else {
          this.message = data.message || "Failed to load dashboard.";
          this.category = "danger";
        }

      } catch (err) {
        console.error(err);
        this.message = "An unexpected error occurred.";
        this.category = "danger";
      }
    },

    /** Navigate to department details **/
    deptDetails(id) {
      this.$router.push(`/department/${id}`);
    },

    /** Get appropriate icon for department **/
    getDepartmentIcon(deptName) {
      const iconMap = {
        'cardiology': '❤️',
        'neurology': '🧠',
        'orthopedics': '🦴',
        'pediatrics': '👶',
        'dermatology': '🔬',
        'surgery': '🩺',
        'psychiatry': '🧠',
        'radiology': '📷',
        'emergency': '🚑',
        'dentistry': '🦷'
      };

      const lowerName = deptName.toLowerCase();
      for (const [key, icon] of Object.entries(iconMap)) {
        if (lowerName.includes(key)) {
          return icon;
        }
      }
      
      return '🏥'; // Default icon
    }
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.patient-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 12px;
  font-weight: 700;
}

.page-header p {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

/* Alert */
.alert {
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-weight: 500;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Dashboard Content */
.dashboard-content {
  margin-bottom: 40px;
}

/* Stats Section */
.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  background: linear-gradient(135deg, #3498db, #2c3e50);
  color: white;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
}

.stat-content h3 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-content p {
  color: #7f8c8d;
  font-size: 1rem;
  margin: 0;
}

/* Departments Section */
.departments-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 12px;
}

.section-description {
  color: #7f8c8d;
  font-size: 1.1rem;
  line-height: 1.5;
  max-width: 600px;
  margin: 0 auto;
}

/* Departments Grid */
.departments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.department-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.department-card:hover {
  border-color: #3498db;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.department-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #3498db, #2c3e50);
}

/* Department Header */
.department-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.department-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 1.5rem;
}

.department-info {
  flex: 1;
}

.department-name {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.department-id {
  color: #7f8c8d;
  font-size: 0.85rem;
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 10px;
}

/* Department Description */
.department-description {
  margin-bottom: 20px;
}

.department-description p {
  color: #5a6c7d;
  line-height: 1.5;
  margin: 0;
  font-size: 0.95rem;
}

/* Department Actions */
.department-actions {
  display: flex;
  justify-content: flex-end;
}

.view-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.view-btn:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateX(5px);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
  line-height: 1.6;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .patient-dashboard {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .departments-grid {
    grid-template-columns: 1fr;
  }
  
  .departments-section {
    padding: 30px 25px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .section-header h2 {
    font-size: 1.7rem;
  }
  
  .department-card {
    padding: 20px;
  }
  
  .department-header {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .department-icon {
    margin-right: 0;
  }
}

@media (max-width: 480px) {
  .page-header {
    padding: 25px 15px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .departments-section {
    padding: 25px 20px;
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
    margin-right: 15px;
  }
  
  .stat-content h3 {
    font-size: 1.5rem;
  }
}
</style>