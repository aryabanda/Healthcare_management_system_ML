<template>
  <div class="department-page">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading department details...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="department-content">
      <!-- Header -->
      <header class="page-header">
        <h1>{{ department.name }}</h1>
        <p class="department-description">{{ department.description }}</p>
        <button class="back-btn" @click="$router.back()">
          ← Back to Departments
        </button>
      </header>

      <!-- Alert Message -->
      <div v-if="message" :class="'alert alert-' + category" role="alert">
        {{ message }}
      </div>

      <!-- Search -->
      <div class="search-section">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search doctors by name, specialization, experience..."
        />
      </div>

      <!-- Doctors Section -->
      <section class="doctors-section">
        <h2>Doctors in this Department</h2>
        
        <div v-if="filteredDoctors.length === 0" class="empty-state">
          <div class="empty-icon">👨‍⚕️</div>
          <h3>No Doctors Found</h3>
          <p v-if="searchQuery">No doctors match your search criteria.</p>
          <p v-else>No doctors are currently available in this department.</p>
        </div>

        <div v-else class="doctors-grid">
          <div class="doctor-card" v-for="doc in filteredDoctors" :key="doc.id">
            <div class="doctor-header">
              <div class="doctor-avatar">
                <span class="avatar-icon">👨‍⚕️</span>
              </div>
              <div class="doctor-info">
                <h3 class="doctor-name">{{ doc.name }}</h3>
                <p class="doctor-specialization">{{ doc.specialization_name }}</p>
              </div>
            </div>
            
            <div class="doctor-details">
              <div class="detail-item">
                <span class="detail-label">ID:</span>
                <span class="detail-value">{{ doc.id }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">Experience:</span>
                <span class="detail-value">{{ doc.experience || "Not specified" }}</span>
              </div>
            </div>

            <div class="doctor-actions">
              <button class="book-btn" @click="openBooking(doc)">
                Book Appointment
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- Booking Modal -->
      <div class="modal" :class="{ 'active': selectedDoctor }">
        <div class="modal-overlay" @click="closeBooking"></div>
        <div class="modal-content">
          <div class="modal-header">
            <h3>Book Appointment with Dr. {{ selectedDoctor?.name }}</h3>
            <button class="modal-close" @click="closeBooking">×</button>
          </div>

          <div class="modal-body">
            <div v-if="availableSlots.length === 0" class="empty-slots">
              <div class="empty-icon">📅</div>
              <h4>No Available Slots</h4>
              <p>This doctor doesn't have any available appointment slots at the moment.</p>
            </div>

            <div v-else class="slots-container">
              <div class="day-slots" v-for="(day, index) in availableSlots" :key="index">
                <h4 class="day-date">{{ formatDate(day.date) }}</h4>
                <div class="time-slots">
                  <button
                    v-for="slot in day.slots"
                    :key="slot"
                    class="time-slot"
                    :class="{ 'booked': isSlotBooked(day.date, slot) }"
                    :disabled="isSlotBooked(day.date, slot)"
                    @click="bookSlot(day.date, slot)"
                  >
                    {{ slot }}
                    <span v-if="isSlotBooked(day.date, slot)" class="booked-badge">Booked</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-secondary" @click="closeBooking">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DepartmentDetails",

  data() {
    return {
      loading: true,
      department: {},
      doctors: [],
      message: null,
      category: null,

      selectedDoctor: null,
      availableSlots: [],
      bookedAppointments: [],
      searchQuery: ""
    };
  },

  computed: {
    filteredDoctors() {
      const q = this.searchQuery.toLowerCase().trim();
      if (!q) return this.doctors;

      return this.doctors.filter(doc => {
        const searchableFields = [
          doc.name || '',
          doc.specialization_name || '',
          doc.experience || ''
        ];

        return searchableFields.some(field => 
          field.toLowerCase().includes(q)
        );
      });
    }
  },

  async mounted() {
    const deptId = this.$route.params.id;

    try {
      const res = await fetch(`http://127.0.0.1:5000/departments/${deptId}`, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      });

      const data = await res.json();

      if (res.ok) {
        this.department = data.department || {};
        this.doctors = data.doctors || [];
      } else {
        this.message = data.message || "Failed to load department details.";
        this.category = "danger";
      }
    } catch (err) {
      console.error(err);
      this.message = "Error fetching department details.";
      this.category = "danger";
    } finally {
      this.loading = false;
    }
  },

  methods: {
    /** Open the modal and load availability */
    async openBooking(doctor) {
      this.selectedDoctor = doctor;
      this.availableSlots = [];
      this.bookedAppointments = [];

      try {
        const res = await fetch(`http://127.0.0.1:5000/doctor/${doctor.id}/availability`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        const data = await res.json();

        if (res.ok) {
          this.availableSlots = data.availability || [];

          // Fetch booked appointments to disable them
          const bookedRes = await fetch(`http://127.0.0.1:5000/doctor/${doctor.id}/appointments`, {
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token")
            }
          });

          if (bookedRes.ok) {
            const bookedData = await bookedRes.json();
            this.bookedAppointments = bookedData.appointments || [];
          }

        } else {
          this.message = data.message || "Failed to load availability.";
          this.category = "danger";
        }

      } catch (err) {
        console.error(err);
        this.category = "danger";
      }
    },

    /** Check if a slot is already booked */
    isSlotBooked(date, time) {
      return this.bookedAppointments.some(
        appt => appt.date === date && appt.time === time
      );
    },

    /** Book an appointment */
    async bookSlot(date, time) {
      if (!confirm(`Confirm appointment with Dr. ${this.selectedDoctor.name} on ${this.formatDate(date)} at ${time}?`)) return;

      try {
        const res = await fetch(`http://127.0.0.1:5000/appointments/book`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({
            doctor_id: this.selectedDoctor.id,
            date,
            time
          })
        });

        const data = await res.json();
        this.message = data.message;
        this.category = res.ok ? "success" : "danger";

        if (res.ok) {
          this.closeBooking();
          // Refresh availability
          this.openBooking(this.selectedDoctor);
        }

      } catch (err) {
        console.error(err);
        this.message = "Error booking appointment.";
        this.category = "danger";
      }
    },

    /** Close booking modal */
    closeBooking() {
      this.selectedDoctor = null;
      this.availableSlots = [];
      this.bookedAppointments = [];
    },

    /** Format date for display */
    formatDate(dateString) {
      if (!dateString) return 'Unknown Date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
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

.department-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
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

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 15px;
}

.department-description {
  color: #7f8c8d;
  font-size: 1.2rem;
  margin-bottom: 20px;
  line-height: 1.6;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
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

/* Search Section */
.search-section {
  margin-bottom: 30px;
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

/* Doctors Section */
.doctors-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
}

.doctors-section h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 25px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* Doctors Grid */
.doctors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.doctor-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: all 0.3s ease;
}

.doctor-card:hover {
  border-color: #3498db;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

/* Doctor Header */
.doctor-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.doctor-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2c3e50);
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-icon {
  font-size: 1.5rem;
  color: white;
}

.doctor-info {
  flex: 1;
}

.doctor-name {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.doctor-specialization {
  color: #3498db;
  font-size: 0.95rem;
  font-weight: 500;
  margin: 0;
}

/* Doctor Details */
.doctor-details {
  margin-bottom: 20px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-label {
  font-weight: 600;
  color: #5a6c7d;
  font-size: 0.9rem;
}

.detail-value {
  color: #2c3e50;
  font-size: 0.9rem;
}

/* Doctor Actions */
.doctor-actions {
  text-align: center;
}

.book-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
}

.book-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(40, 167, 69, 0.3);
}

/* Empty States */
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
  max-width: 600px;
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
}

/* Empty Slots */
.empty-slots {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.empty-slots .empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.empty-slots h4 {
  color: #2c3e50;
  margin-bottom: 10px;
}

/* Slots Container */
.slots-container {
  max-height: 400px;
  overflow-y: auto;
}

.day-slots {
  margin-bottom: 25px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f1f8ff;
}

.day-slots:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.day-date {
  color: #2c3e50;
  font-size: 1.1rem;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid #f1f8ff;
}

.time-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.time-slot {
  background: #28a745;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.time-slot:hover:not(.booked) {
  background: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.time-slot.booked {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.6;
}

.booked-badge {
  display: block;
  font-size: 0.7rem;
  margin-top: 4px;
  opacity: 0.8;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .department-page {
    padding: 15px;
  }
  
  .doctors-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .doctors-section {
    padding: 20px;
  }
  
  .doctor-card {
    padding: 20px;
  }
  
  .modal-content {
    width: 95%;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 20px;
  }
  
  .time-slots {
    gap: 8px;
  }
  
  .time-slot {
    padding: 8px 12px;
    font-size: 0.85rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.6rem;
  }
  
  .doctor-header {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .time-slots {
    justify-content: center;
  }
}
</style>