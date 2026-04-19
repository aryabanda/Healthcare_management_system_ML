<template>
  <div class="doctor-dashboard">
    <!-- Header -->
    <header class="page-header">
      <h1>Doctor Dashboard</h1>
      <p>Manage your appointments and patient care</p>
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
              <span>📅</span>
            </div>
            <div class="stat-content">
              <h3>{{ totalAppointments }}</h3>
              <p>Total Appointments</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <span>⏳</span>
            </div>
            <div class="stat-content">
              <h3>{{ pendingAppointments }}</h3>
              <p>Pending</p>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">
              <span>✅</span>
            </div>
            <div class="stat-content">
              <h3>{{ completedAppointments }}</h3>
              <p>Completed</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Appointments Section -->
      <section class="appointments-section">
        <div class="section-header">
          <h2>Today's Appointments</h2>
          <button class="refresh-btn" @click="fetchAppointments">
            🔄 Refresh
          </button>
        </div>

        <!-- No Appointments -->
        <div v-if="appointments.length === 0" class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>No Appointments Scheduled</h3>
          <p>You don't have any appointments scheduled for today.</p>
        </div>

        <!-- Appointments List -->
        <div v-else class="appointments-list">
          <div
            class="appointment-card"
            :class="getRiskCardClass(appt)"
            v-for="appt in appointments"
            :key="appt.id"
          >
            <div class="appointment-header">
              <div class="patient-info">
                <h3 class="patient-name">{{ getPatientName(appt.patient_id) }}</h3>
                <div class="appointment-meta">
                  <span class="appointment-time">{{ appt.time }}</span>
                  <span class="appointment-date">{{ formatDate(appt.date) }}</span>
                </div>
              </div>
              <div class="appointment-status">
                <span :class="'status-badge ' + getStatusClass(appt.status)">
                  {{ appt.status }}
                </span>
              </div>
            </div>

            <div class="appointment-details">
              <div class="detail-item">
                <span class="detail-label">Remarks</span>
                <span class="detail-value">{{ appt.remarks || "No remarks" }}</span>
              </div>
              <div class="detail-item" v-if="appt.readmission_risk">
                <span class="detail-label">Readmission Risk</span>
                <span class="detail-value">
                  {{ appt.readmission_risk.risk_label }}
                  ({{ (appt.readmission_risk.risk_probability * 100).toFixed(2) }}%)
                </span>
              </div>
            </div>

            <div class="appointment-actions">
              <button
                v-if="appt.status === 'Booked'"
                @click="markCompleted(appt.id)"
                class="btn btn-complete"
              >
                ✅ Mark Completed
              </button>
              <span v-else class="completed-text">Appointment Completed</span>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- Completion Modal -->
    <CompletionModal @submit="handleCompletionSubmit" />
  </div>
</template>

<script>
import CompletionModal from "@/components/CompletionModal.vue";
import { Modal } from "bootstrap";

export default {
  name: "DoctorDashboard",
  components: { CompletionModal },
  data() {
    return {
      message: null,
      category: null,
      appointments: [],
      patients: {},
      selectedAppointmentId: null,
      completionModalInstance: null
    };
  },

  computed: {
    totalAppointments() {
      return this.appointments.length;
    },
    pendingAppointments() {
      return this.appointments.filter(appt => appt.status === 'Booked').length;
    },
    completedAppointments() {
      return this.appointments.filter(appt => appt.status === 'Completed').length;
    }
  },

  mounted() {
    this.fetchAppointments();
    this.completionModalInstance = new Modal(document.getElementById('completionModal'));
  },

  methods: {
    async fetchAppointments() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          this.message = "You are not logged in.";
          this.category = "danger";
          return;
        }

        const res = await fetch(`http://127.0.0.1:5000/doctor/appointments`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) throw new Error("Failed to fetch appointments");

        const data = await res.json();
        this.appointments = data;

        // Fetch patient info
        await this.fetchPatients();

      } catch (err) {
        console.error(err);
        this.message = "Error loading appointments.";
        this.category = "danger";
      }
    },

    async fetchPatients() {
      try {
        const token = localStorage.getItem("token");

        const res = await fetch(`http://127.0.0.1:5000/doctor/patients`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.ok) {
          const data = await res.json();
          // Map: patient_id → username
          this.patients = Object.fromEntries(
            data.map((p) => [p.id, p.username])
          );
        }
      } catch (err) {
        console.log("Error fetching patient list:", err);
      }
    },

    getPatientName(id) {
      return this.patients[id] || "Unknown Patient";
    },

    getStatusClass(status) {
      const statusMap = {
        'Completed': 'completed',
        'Booked': 'booked',
        'Cancelled': 'cancelled'
      };
      return statusMap[status] || 'default';
    },
    getRiskCardClass(appt) {
      if (!appt.readmission_risk) return '';
      const score = Number(appt.readmission_risk.risk_probability || 0);
      if (score >= 0.7) return 'risk-high';
      if (score >= 0.4) return 'risk-medium';
      return 'risk-low';
    },

    formatDate(dateString) {
      if (!dateString) return 'Unknown Date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },

    markCompleted(appointmentId) {
      this.selectedAppointmentId = appointmentId;
      this.completionModalInstance.show();
    },

    async handleCompletionSubmit(formData) {

      try {
        const token = localStorage.getItem("token");
        const res = await fetch(
          `http://127.0.0.1:5000/doctor/appointments/${this.selectedAppointmentId}/complete`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(formData)
          }
        );

        const data = await res.json();

        if (res.ok) {
          if (data.readmission && data.readmission.risk_label) {
            this.message = `${data.message || "Appointment completed."} Readmission risk: ${data.readmission.risk_label} (${(data.readmission.risk_probability * 100).toFixed(2)}%).`;
          } else {
            this.message = data.message || "Appointment completed successfully.";
          }
          this.category = "success";
          this.fetchAppointments(); // Refresh the list
        } else {
          this.message = data.message || "Failed to complete appointment.";
          this.category = "danger";
        }
      } catch (err) {
        console.error(err);
        this.message = "A network error occurred.";
        this.category = "danger";
      } finally {
        this.completionModalInstance.hide();
        this.selectedAppointmentId = null;
      }
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

.doctor-dashboard {
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
  padding: 20px 0;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 8px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
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
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
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

/* Appointments Section */
.appointments-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin: 0;
}

.refresh-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Appointments List */
.appointments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.appointment-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
}

.appointment-card.risk-high {
  border-color: #f5c6cb;
  background: #fff5f5;
}

.appointment-card.risk-medium {
  border-color: #ffeeba;
  background: #fffcf0;
}

.appointment-card.risk-low {
  border-color: #c3e6cb;
  background: #f4fff6;
}

.appointment-card:hover {
  border-color: #3498db;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.appointment-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(to bottom, #3498db, #2c3e50);
  border-radius: 4px 0 0 4px;
}

.appointment-card.risk-high::before {
  background: linear-gradient(to bottom, #dc3545, #c82333);
}

.appointment-card.risk-medium::before {
  background: linear-gradient(to bottom, #ffc107, #e0a800);
}

.appointment-card.risk-low::before {
  background: linear-gradient(to bottom, #28a745, #1e7e34);
}

/* Appointment Header */
.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.patient-info {
  flex: 1;
}

.patient-name {
  color: #2c3e50;
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.appointment-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.appointment-time {
  color: #3498db;
  font-size: 1rem;
  font-weight: 500;
  background: #f1f8ff;
  padding: 6px 12px;
  border-radius: 20px;
}

.appointment-date {
  color: #7f8c8d;
  font-size: 0.95rem;
}

/* Status Badge */
.appointment-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.booked {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.default {
  background-color: #e2e3e5;
  color: #383d41;
}

/* Appointment Details */
.appointment-details {
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-weight: 600;
  color: #5a6c7d;
  margin-bottom: 5px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #2c3e50;
  font-size: 1rem;
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
  border-left: 3px solid #3498db;
}

/* Appointment Actions */
.appointment-actions {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-complete {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.btn-complete:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.completed-text {
  color: #28a745;
  font-weight: 600;
  font-style: italic;
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
}

/* Responsive Design */
@media (max-width: 768px) {
  .doctor-dashboard {
    padding: 15px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .refresh-btn {
    align-self: flex-start;
  }
  
  .appointment-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .appointment-status {
    align-self: flex-start;
  }
  
  .appointment-actions {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .appointments-section {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .appointment-card {
    padding: 20px;
  }
  
  .patient-name {
    font-size: 1.2rem;
  }
  
  .appointment-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .btn {
    padding: 8px 16px;
    font-size: 0.9rem;
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