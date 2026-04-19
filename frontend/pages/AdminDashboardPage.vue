<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <h1>Admin Dashboard</h1>
      <p>Manage doctors, patients, and appointments</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- DOCTORS SECTION -->
    <section class="section">
      <h2>Manage Doctors</h2>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Approved</th>
              <th>Blocked</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in doctors" :key="doc.id">
              <td>{{ doc.id }}</td>
              <td>{{ doc.username }}</td>
              <td>
                <span :class="'status ' + (doc.approve ? 'approved' : 'pending')">
                  {{ doc.approve ? "Yes" : "No" }}
                </span>
              </td>
              <td>
                <span :class="'status ' + (doc.blocked ? 'blocked' : 'active')">
                  {{ doc.blocked ? "Yes" : "No" }}
                </span>
              </td>
              <td class="actions">
                <button
                  class="btn btn-success"
                  v-if="!doc.approve"
                  @click="updateDoctor(doc.id, 'approve')"
                >
                  Approve
                </button>

                <button
                  class="btn btn-secondary"
                  v-if="doc.approve"
                  @click="updateDoctor(doc.id, 'reject')"
                >
                  Reject
                </button>

                <button
                  class="btn btn-danger"
                  v-if="!doc.blocked"
                  @click="updateDoctor(doc.id, 'block')"
                >
                  Block
                </button>

                <button
                  class="btn btn-warning"
                  v-if="doc.blocked"
                  @click="updateDoctor(doc.id, 'unblock')"
                >
                  Unblock
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- PATIENTS SECTION -->
    <section class="section">
      <h2>Patients</h2>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>History</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id">
              <td>{{ p.id }}</td>
              <td>{{ p.username }}</td>
              <td>
                <button
                  class="btn btn-info"
                  @click="viewHistory(p.id)"
                >
                  View History
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- APPOINTMENTS SECTION -->
    <section class="section">
      <h2>Appointments</h2>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient ID</th>
              <th>Doctor ID</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
              <th>No-Show Risk</th>
              <th>Remarks</th>
              <th>Schedule</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id" :class="getNoShowRowClass(a)">
              <td>{{ a.id }}</td>
              <td>{{ a.patient_id }}</td>
              <td>{{ a.doctor_id }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td>
                <span :class="'status ' + a.status.toLowerCase()">
                  {{ a.status }}
                </span>
              </td>
              <td>
                <span v-if="a.no_show_risk" :class="'status ' + getNoShowRiskClass(a.no_show_risk)">
                  {{ a.no_show_risk.risk_label }}
                  ({{ (a.no_show_risk.risk_probability * 100).toFixed(1) }}%)
                </span>
                <span v-else>—</span>
              </td>
              <td>{{ a.remarks || "—" }}</td>
              <td>
                <button
                  class="btn btn-primary"
                  v-if="a.status === 'Booked'"
                  @click="openReschedule(a)"
                >
                  Reschedule
                </button>
                <span v-else>—</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- RESCHEDULE MODAL -->
    <div class="modal" :class="{ 'active': modalActive }">
      <div class="modal-overlay" @click="closeModal()"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Reschedule Appointment</h3>
          <button class="modal-close" @click="closeModal()">×</button>
        </div>

        <div class="modal-body">
          <div v-if="msg" :class="'alert alert-' + msgType">
            {{ msg }}
          </div>

          <!-- Select Date -->
          <div class="form-group">
            <label class="form-label">Select Date</label>
            <select
              class="form-select"
              v-model="form.date"
              @change="loadSlotsForDate"
            >
              <option disabled value="">Choose a date</option>
              <option
                v-for="d in availableDates"
                :key="d"
                :value="d"
              >
                {{ d }}
              </option>
            </select>
          </div>

          <!-- Select Slot -->
          <div class="form-group">
            <label class="form-label">Available Slots</label>
            <select
              class="form-select"
              v-model="form.time12"
            >
              <option disabled value="">Choose a time</option>
              <option
                v-for="slot in availableSlots"
                :key="slot"
                :value="slot"
              >
                {{ slot }}
              </option>
            </select>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal()">
            Cancel
          </button>
          <button
            class="btn btn-primary"
            @click="submitReschedule()"
            :disabled="processing"
          >
            {{ processing ? "Saving..." : "Reschedule" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminManagePage",

  data() {
    return {
      doctors: [],
      patients: [],
      appointments: [],
      message: null,
      category: null,

      // RESCHEDULE modal data
      availableDates: [],
      availableSlots: [],
      allAvailability: [],
      msg: null,
      msgType: "info",
      processing: false,
      modalActive: false,

      form: {
        appointmentId: null,
        date: "",
        time12: ""
      }
    };
  },

  mounted() {
    this.fetchDoctors();
    this.fetchPatients();
    this.fetchAppointments();
  },

  methods: {
    // ------------------ FETCH DATA ------------------
    async fetchDoctors() {
      const res = await fetch(`http://127.0.0.1:5000/admin/doctors`, {
        headers: {
          "Authorization": "Bearer " + localStorage.getItem("token")
        }
      });
      this.doctors = await res.json();
    },

    async fetchPatients() {
      const res = await fetch(`http://127.0.0.1:5000/admin/patients`, {
        headers: {
          "Authorization": "Bearer " + localStorage.getItem("token")
        }
      });
      this.patients = await res.json();
    },

    async fetchAppointments() {
      const res = await fetch(`http://127.0.0.1:5000/admin/appointments`, {
        headers: {
          "Authorization": "Bearer " + localStorage.getItem("token")
        }
      });
      this.appointments = await res.json();
    },
    getNoShowRiskClass(risk) {
      if (!risk || !risk.risk_label) return "pending";
      const label = risk.risk_label.toLowerCase();
      if (label === "high") return "noshow-high";
      if (label === "medium") return "noshow-medium";
      return "noshow-low";
    },
    getNoShowRowClass(appt) {
      if (!appt || !appt.no_show_risk) return "";
      const label = appt.no_show_risk.risk_label?.toLowerCase();
      if (label === "high") return "row-noshow-high";
      if (label === "medium") return "row-noshow-medium";
      return "row-noshow-low";
    },

    // ------------------ HISTORY ------------------
    viewHistory(patientId) {
      this.$router.push(`/admin/patient/${patientId}/history`);
    },

    // ------------------ UPDATE DOCTOR ------------------
    async updateDoctor(userId, action) {
      await fetch(`http://127.0.0.1:5000/admin/block_user/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify({ action })
      });

      this.fetchDoctors();
    },

    // ------------------ RESCHEDULE ------------------
    async openReschedule(appt) {
      this.form.appointmentId = appt.id;
      this.form.date = appt.date;
      this.form.time12 = "";

      const doctorId = appt.doctor_id;

      const res = await fetch(`http://127.0.0.1:5000/doctor/${doctorId}/availability`, {
        headers: {
          "Authorization": "Bearer " + localStorage.getItem("token")
        }
      });

      const data = await res.json();

      this.allAvailability = data.availability;
      this.availableDates = data.availability.map(d => d.date);

      const day = data.availability.find(d => d.date === appt.date);
      this.availableSlots = day ? day.slots : [];

      if (this.availableSlots.includes(appt.time)) {
        this.form.time12 = appt.time;
      }

      this.modalActive = true;
    },

    loadSlotsForDate() {
      const day = this.allAvailability.find(d => d.date === this.form.date);
      this.availableSlots = day ? day.slots : [];
      this.form.time12 = "";
    },

    closeModal() {
      this.modalActive = false;
      this.msg = null;
    },

    async submitReschedule() {
      if (!this.form.date || !this.form.time12) {
        this.msg = "Please select date and time slot!";
        this.msgType = "danger";
        return;
      }

      this.processing = true;

      try {
        const res = await fetch(`http://127.0.0.1:5000/appointments/${this.form.appointmentId}/reschedule`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({
            date: this.form.date,
            time: this.form.time12
          })
        });

        const data = await res.json();

        if (res.ok) {
          this.closeModal();
          this.fetchAppointments();
        } else {
          this.msg = data.message;
          this.msgType = "danger";
        }
      } finally {
        this.processing = false;
      }
    }
  }
};
</script>

<style scoped>
/* Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  background-color: #f8f9fa;
}

/* Header */
.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px 0;
  border-bottom: 1px solid #eaeaea;
}

.dashboard-header h1 {
  color: #2c3e50;
  font-size: 2.2rem;
  margin-bottom: 8px;
}

.dashboard-header p {
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

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.alert-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Section */
.section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background-color: #f1f8ff;
  color: #2c3e50;
  font-weight: 600;
  text-align: left;
  padding: 12px 15px;
  border-bottom: 2px solid #3498db;
}

.data-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #eaeaea;
}

.data-table tr:hover {
  background-color: #f8f9fa;
}

/* Status badges */
.status {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status.approved,
.status.active {
  background-color: #d4edda;
  color: #155724;
}

.status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status.blocked {
  background-color: #f8d7da;
  color: #721c24;
}

.status.booked {
  background-color: #cce7ff;
  color: #004085;
}

.status.noshow-low {
  background-color: #d4edda;
  color: #155724;
}

.status.noshow-medium {
  background-color: #fff3cd;
  color: #856404;
}

.status.noshow-high {
  background-color: #f8d7da;
  color: #721c24;
}

.data-table tr.row-noshow-low {
  background-color: #f4fff6;
}

.data-table tr.row-noshow-medium {
  background-color: #fffdf3;
}

.data-table tr.row-noshow-high {
  background-color: #fff5f5;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-right: 8px;
  margin-bottom: 5px;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Actions column */
.actions {
  white-space: nowrap;
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
  padding: 20px 25px;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  color: #2c3e50;
  margin: 0;
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
  padding: 25px;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Form elements */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.form-select {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  background-color: white;
}

.form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .admin-dashboard {
    padding: 15px;
  }
  
  .section {
    padding: 15px;
  }
  
  .data-table th,
  .data-table td {
    padding: 8px 10px;
    font-size: 0.9rem;
  }
  
  .btn {
    padding: 6px 12px;
    font-size: 0.85rem;
    margin-right: 5px;
    margin-bottom: 5px;
  }
  
  .modal-content {
    width: 95%;
  }
}
</style>