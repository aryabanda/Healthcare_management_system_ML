<template>
  <div class="appointments-page">
    <!-- Header -->
    <header class="page-header">
      <h1>My Appointments</h1>
      <p>Manage and view all your scheduled appointments</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Controls -->
    <div class="controls-section">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          class="search-input"
          placeholder="Search by patient, date, time, status, remarks..."
        />
      </div>
      <button class="refresh-btn" @click="fetchAppointments">
        🔄 Refresh
      </button>
    </div>

    <!-- Appointments Content -->
    <div class="appointments-section">
      <div v-if="filteredAppointments.length" class="appointments-container">
        <div class="appointment-card" v-for="appt in filteredAppointments" :key="appt.id">
          <div class="appointment-header">
            <div class="appointment-info">
              <h3 class="patient-name">{{ appt.patient_name }}</h3>
              <div class="appointment-meta">
                <span class="appointment-id">Appointment #{{ appt.id }}</span>
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
            <div class="detail-row">
              <div class="detail-item">
                <span class="detail-label">Time</span>
                <span class="detail-value">{{ appt.time }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Date</span>
                <span class="detail-value">{{ appt.date }}</span>
              </div>
            </div>
            
            <div class="detail-item full-width">
              <span class="detail-label">Remarks</span>
              <span class="detail-value remarks">{{ appt.remarks || "No remarks" }}</span>
            </div>
          </div>

          <div class="appointment-actions">
            <button class="btn btn-history" @click="viewHistory(appt.patient_id)">
              📋 View Patient History
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">📅</div>
        <h3>No Appointments Found</h3>
        <p v-if="searchQuery">No appointments match your search criteria.</p>
        <p v-else>You don't have any scheduled appointments at the moment.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DoctorAppointments",

  data() {
    return {
      appointments: [],
      message: null,
      category: null,
      searchQuery: ""
    };
  },

  computed: {
    filteredAppointments() {
      const q = this.searchQuery.toLowerCase().trim();

      if (!q) return this.appointments;

      return this.appointments.filter(a => {
        const searchableFields = [
          a.patient_name || '',
          a.date || '',
          a.time || '',
          a.status || '',
          a.remarks || ''
        ];

        return searchableFields.some(field => 
          field.toLowerCase().includes(q)
        );
      });
    }
  },

  methods: {
    viewHistory(patientId) {
      this.$router.push(`/doctor/patient/${patientId}/history`);
    },

    async fetchAppointments() {
      this.message = null;

      try {
        const res = await fetch(`http://127.0.0.1:5000/doctor/appointments`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        if (res.ok) {
          this.appointments = await res.json();

          if (!this.appointments.length) {
            this.message = "No appointments available.";
            this.category = "info";
          } else {
            this.message = `Loaded ${this.appointments.length} appointments successfully`;
            this.category = "success";
            
            // Auto-clear success message after 3 seconds
            setTimeout(() => {
              if (this.category === 'success') {
                this.message = null;
              }
            }, 3000);
          }
        } else {
          const errorData = await res.json().catch(() => ({ message: "Failed to fetch appointments" }));
          this.message = errorData.message || "Failed to fetch appointments.";
          this.category = "danger";
        }
      } catch (error) {
        console.error("Error fetching appointments:", error);
        this.message = "An unexpected error occurred.";
        this.category = "danger";
      }
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

    getStatusClass(status) {
      const statusMap = {
        'Booked': 'booked',
        'Completed': 'completed',
        'Cancelled': 'cancelled',
        'Confirmed': 'confirmed',
        'Pending': 'pending'
      };
      return statusMap[status] || 'default';
    }
  },

  mounted() {
    this.fetchAppointments();
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.appointments-page {
  max-width: 1000px;
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
  font-size: 2.2rem;
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

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Controls Section */
.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 15px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  background-color: white;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.refresh-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.refresh-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Appointments Section */
.appointments-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.appointments-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Appointment Card */
.appointment-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
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

/* Appointment Header */
.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.appointment-info {
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

.appointment-id {
  color: #7f8c8d;
  font-size: 0.9rem;
  background: #f8f9fa;
  padding: 4px 10px;
  border-radius: 15px;
}

.appointment-date {
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Status Badge */
.appointment-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.booked {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.confirmed {
  background-color: #cce7ff;
  color: #004085;
}

.status-badge.pending {
  background-color: #e2e3e5;
  color: #383d41;
}

.status-badge.default {
  background-color: #f8f9fa;
  color: #6c757d;
}

/* Appointment Details */
.appointment-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.detail-item {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 120px;
}

.detail-item.full-width {
  flex: 1 1 100%;
}

.detail-label {
  font-weight: 600;
  color: #5a6c7d;
  margin-bottom: 5px;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #2c3e50;
  font-size: 1rem;
}

.detail-value.remarks {
  font-style: italic;
  color: #7f8c8d;
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
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-history {
  background: #ffc107;
  color: #212529;
}

.btn-history:hover {
  background: #e0a800;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
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
  .appointments-page {
    padding: 15px;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .appointments-section {
    padding: 20px;
  }
  
  .appointment-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .appointment-status {
    align-self: flex-start;
  }
  
  .detail-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .appointment-actions {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
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
}
</style>