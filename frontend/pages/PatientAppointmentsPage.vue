<template>
  <div class="patient-appointments-page">
    <!-- Header -->
    <header class="page-header">
      <h1>My Appointments</h1>
      <p>Manage and view all your scheduled appointments</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Main Content -->
    <div class="appointments-content">
      <!-- Appointments Section -->
      <section class="appointments-section">
        <div class="section-header">
          <h2>Scheduled Appointments</h2>
          <button class="refresh-btn" @click="fetchAppointments">
            🔄 Refresh
          </button>
        </div>

        <!-- No Appointments -->
        <div v-if="appointments.length === 0" class="empty-state">
          <div class="empty-icon">📅</div>
          <h3>No Appointments Found</h3>
          <p>You don't have any scheduled appointments at the moment.</p>
        </div>

        <!-- Appointments List -->
        <div v-else class="appointments-list">
          <div class="appointment-card" v-for="appt in appointments" :key="appt.id">
            <div class="appointment-header">
              <div class="appointment-info">
                <h3 class="doctor-name">Dr. {{ appt.doctor_username }}</h3>
                <div class="appointment-meta">
                  <span class="appointment-date">{{ formatDate(appt.date) }}</span>
                  <span class="appointment-time">{{ appt.time }}</span>
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
            </div>

            <div class="appointment-actions">
              <div class="action-buttons">
                <button
                  v-if="appt.status.toLowerCase() === 'booked'"
                  class="btn btn-cancel"
                  @click="cancelAppointment(appt.id)"
                >
                  ❌ Cancel
                </button>
                <button
                  v-if="appt.status.toLowerCase() === 'booked'"
                  class="btn btn-reschedule"
                  @click="openReschedule(appt)"
                >
                  📅 Reschedule
                </button>
                <span v-else class="no-actions">No actions available</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Summary Chart -->
      <section class="chart-section">
        <div class="chart-card">
          <h3>Appointments Overview</h3>
          <canvas id="appointmentsChart" height="200"></canvas>
        </div>
      </section>
    </div>

    <!-- Reschedule Modal -->
    <div class="modal" :class="{ 'active': modalActive }">
      <div class="modal-overlay" @click="closeModal"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Reschedule Appointment</h3>
          <button class="modal-close" @click="closeModal">×</button>
        </div>

        <div class="modal-body">
          <div v-if="msg" :class="'alert alert-' + msgType">{{ msg }}</div>

          <div class="form-group">
            <label class="form-label">Select Date</label>
            <input 
              type="date" 
              class="form-input" 
              v-model="form.date"
              :min="getTodayDate()"
            >
          </div>

          <div class="form-group">
            <label class="form-label">Select Time</label>
            <input 
              type="time" 
              class="form-input" 
              v-model="form.time24"
            >
            <small class="form-help">Use 24-hour format (e.g., 14:30 for 2:30 PM)</small>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">Cancel</button>
          <button 
            class="btn btn-primary" 
            @click="submitReschedule" 
            :disabled="processing"
          >
            <span v-if="processing" class="btn-loading">
              <span class="spinner"></span>
              Processing...
            </span>
            <span v-else>Reschedule Appointment</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";

export default {
  name: "PatientAppointmentsPage",

  data() {
    return {
      appointments: [],
      appointmentsChart: null,

      message: null,
      category: null,

      form: {
        appointmentId: null,
        date: "",
        time24: ""
      },

      msg: null,
      msgType: "info",
      processing: false,
      modalActive: false
    };
  },

  methods: {
    getStatusClass(status) {
      const statusMap = {
        'Booked': 'booked',
        'Pending': 'pending',
        'Completed': 'completed',
        'Cancelled': 'cancelled'
      };
      return statusMap[status] || 'default';
    },

    async fetchAppointments() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/patient/appointments`, {
          headers: { Authorization: "Bearer " + localStorage.getItem("token") }
        });

        if (!res.ok) throw new Error("Failed to fetch appointments");

        const data = await res.json();
        this.appointments = data;

        if (data.length === 0) {
          this.message = "No appointments found.";
          this.category = "info";
          this.updateAppointmentsChart([], []);
          return;
        }

        const grouped = {};
        data.forEach(a => {
          if (a && a.date) {
            grouped[a.date] = (grouped[a.date] || 0) + 1;
          }
        });

        this.updateAppointmentsChart(Object.keys(grouped), Object.values(grouped));

      } catch (e) {
        this.message = "Unable to load appointments.";
        this.category = "danger";
      }
    },

    async cancelAppointment(id) {
      if (!confirm("Are you sure you want to cancel this appointment?")) return;

      try {
        const res = await fetch(`http://127.0.0.1:5000/patient/appointments/${id}/cancel`, {
          method: "POST",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token"),
            "Content-Type": "application/json"
          }
        });

        const result = await res.json();
        if (!res.ok) throw new Error(result.message);

        this.message = "Appointment cancelled successfully.";
        this.category = "success";
        this.fetchAppointments();

      } catch (e) {
        this.message = e.message;
        this.category = "danger";
      }
    },

    openReschedule(appt) {
      this.form.appointmentId = appt.id;
      this.form.date = appt.date;
      this.form.time24 = appt.time ? appt.time.slice(0, 5) : "11:00";

      this.msg = null;
      this.modalActive = true;
    },

    closeModal() {
      this.modalActive = false;
      this.msg = null;
      this.processing = false;
    },

    async submitReschedule() {
      if (!this.form.date || !this.form.time24) {
        this.msg = "Please fill all fields.";
        this.msgType = "danger";
        return;
      }

      const toAmPm = (time) => {
        const [h, m] = time.split(":");
        const hour = parseInt(h);
        const ampm = hour >= 12 ? "PM" : "AM";
        const formatted = ((hour + 11) % 12) + 1;
        return `${String(formatted).padStart(2, "0")}:${m} ${ampm}`;
      };

      const time12 = toAmPm(this.form.time24);
      this.processing = true;

      try {
        const res = await fetch(`http://127.0.0.1:5000/appointments/${this.form.appointmentId}/reschedule`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({ date: this.form.date, time: time12 })
        });

        const data = await res.json();

        if (res.ok) {
          this.msg = "Appointment rescheduled successfully!";
          this.msgType = "success";
          setTimeout(() => {
            this.closeModal();
            this.fetchAppointments();
          }, 1500);
        } else {
          this.msg = data.message || "Unable to reschedule.";
          this.msgType = "danger";
        }

      } catch (err) {
        this.msg = "Server error. Please try again.";
        this.msgType = "danger";
      } finally {
        this.processing = false;
      }
    },

    updateAppointmentsChart(labels, values) {
      const ctx = document.getElementById("appointmentsChart");
      if (!ctx) return;

      const ctx2d = ctx.getContext("2d");

      if (this.appointmentsChart) this.appointmentsChart.destroy();

      this.appointmentsChart = new Chart(ctx2d, {
        type: "bar",
        data: {
          labels,
          datasets: [{
            label: "Appointments Per Day",
            data: values,
            backgroundColor: "rgba(54, 162, 235, 0.6)",
            borderColor: "rgba(54, 162, 235, 1)",
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: { 
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      });
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

    getTodayDate() {
      return new Date().toISOString().split('T')[0];
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

.patient-appointments-page {
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

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Appointments Content */
.appointments-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
  margin-bottom: 40px;
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

.doctor-name {
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

.appointment-date {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 500;
}

.appointment-time {
  color: #3498db;
  font-size: 1rem;
  font-weight: 500;
  background: #f1f8ff;
  padding: 6px 12px;
  border-radius: 20px;
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

.status-badge.booked {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.pending {
  background-color: #e2e3e5;
  color: #383d41;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.default {
  background-color: #f8f9fa;
  color: #6c757d;
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

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn-cancel {
  background: #dc3545;
  color: white;
}

.btn-reschedule {
  background: #ffc107;
  color: #212529;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.no-actions {
  color: #7f8c8d;
  font-style: italic;
}

/* Chart Section */
.chart-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  height: fit-content;
}

.chart-card h3 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 20px;
  text-align: center;
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

/* Modal */
.modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
}

.modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.4rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-close:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 30px;
}

.modal-footer {
  padding: 20px 30px;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Form Elements */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-help {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 5px;
  display: block;
}

/* Button Loading */
.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .appointments-content {
    grid-template-columns: 1fr;
  }
  
  .chart-section {
    order: -1;
  }
}

@media (max-width: 768px) {
  .patient-appointments-page {
    padding: 15px;
  }
  
  .appointments-section,
  .chart-section {
    padding: 20px;
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
  
  .action-buttons {
    justify-content: center;
    width: 100%;
  }
  
  .btn {
    flex: 1;
    justify-content: center;
    min-width: 120px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .appointment-card {
    padding: 20px;
  }
  
  .doctor-name {
    font-size: 1.2rem;
  }
  
  .appointment-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .modal-content {
    width: 95%;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }
}
</style>