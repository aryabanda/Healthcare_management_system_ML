<template>
  <div class="patient-details-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>Patient Details</h1>
        <button class="back-btn" @click="$router.push('/admin/patients')">
          ← Back to Patients
        </button>
      </div>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category">
      {{ message }}
    </div>

    <!-- Patient Details Card -->
    <div v-if="patient" class="patient-card">
      <div class="patient-header">
        <div class="patient-avatar">
          <span class="avatar-icon">👤</span>
        </div>
        <div class="patient-title">
          <h2>{{ patient.profile?.full_name || "Unnamed Patient" }}</h2>
          <p class="patient-email">{{ patient.username }}</p>
        </div>
        <div class="patient-status">
          <span :class="'status-badge ' + (patient.blocked ? 'blocked' : 'active')">
            {{ patient.blocked ? "Blocked" : "Active" }}
          </span>
        </div>
      </div>

      <div class="patient-content">
        <div class="info-section">
          <h3>Basic Information</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>Patient ID</label>
              <p class="info-value">{{ patient.id }}</p>
            </div>
            <div class="info-item">
              <label>Email Address</label>
              <p class="info-value">{{ patient.username }}</p>
            </div>
            <div class="info-item">
              <label>Account Status</label>
              <p :class="'info-value status ' + (patient.blocked ? 'blocked' : 'active')">
                {{ patient.blocked ? "Blocked" : "Active" }}
              </p>
            </div>
          </div>
        </div>

        <div class="info-section">
          <h3>Profile Details</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>Full Name</label>
              <p class="info-value">{{ patient.profile?.full_name || "Not provided" }}</p>
            </div>
            <div class="info-item">
              <label>Age</label>
              <p class="info-value">{{ patient.profile?.age || "Not provided" }}</p>
            </div>
            <div class="info-item">
              <label>Contact Number</label>
              <p class="info-value">{{ patient.profile?.contact || "Not provided" }}</p>
            </div>
            <div class="info-item full-width">
              <label>Address</label>
              <p class="info-value">{{ patient.profile?.address || "Not provided" }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="patient-actions">
        <button class="btn btn-secondary" @click="$router.push('/admin/patients')">
          Back to Patient List
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading patient details...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminPatientDetailsPage",

  data() {
    return {
      patient: null,
      message: null,
      category: null,
    };
  },

  async mounted() {
    const id = this.$route.params.id;

    try {
      const res = await fetch(`http://127.0.0.1:5000/admin/patient/${id}`, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token"),
        },
      });

      if (res.ok) {
        this.patient = await res.json();
      } else {
        const err = await res.json();
        this.message = err.message;
        this.category = "danger";
      }
    } catch (error) {
      this.message = "Failed to load patient details.";
      this.category = "danger";
    }
  },
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.patient-details-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* Header */
.page-header {
  margin-bottom: 30px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  margin: 0;
}

.back-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.back-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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

/* Patient Card */
.patient-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

/* Patient Header */
.patient-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f8ff;
}

.patient-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2c3e50);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 2rem;
  color: white;
}

.patient-title {
  flex: 1;
}

.patient-title h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 5px;
}

.patient-email {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* Status Badge */
.patient-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.blocked {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* Patient Content */
.patient-content {
  margin-bottom: 30px;
}

.info-section {
  margin-bottom: 30px;
}

.info-section h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eaeaea;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-item label {
  font-weight: 600;
  color: #5a6c7d;
  margin-bottom: 8px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  color: #2c3e50;
  font-size: 1.1rem;
  margin: 0;
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fa;
}

.info-value.status {
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 6px;
  display: inline-block;
  width: fit-content;
}

.info-value.status.active {
  background-color: #d4edda;
  color: #155724;
}

.info-value.status.blocked {
  background-color: #f8d7da;
  color: #721c24;
}

/* Patient Actions */
.patient-actions {
  display: flex;
  justify-content: center;
  padding-top: 20px;
  border-top: 2px solid #f1f8ff;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

.loading-state p {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
  .patient-details-page {
    padding: 15px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .page-header h1 {
    font-size: 1.6rem;
    text-align: center;
  }
  
  .back-btn {
    align-self: center;
  }
  
  .patient-card {
    padding: 20px;
  }
  
  .patient-header {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .patient-title h2 {
    font-size: 1.5rem;
  }
}
</style>