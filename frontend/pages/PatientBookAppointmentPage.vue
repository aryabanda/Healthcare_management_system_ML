<template>
  <div class="book-appointment-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Book Appointment</h1>
      <p>Schedule your appointment with Dr. {{ doctorName || "..." }}</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading available time slots...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="appointment-content">
      <!-- No Availability -->
      <div v-if="availability.length === 0" class="empty-state">
        <div class="empty-icon">📅</div>
        <h3>No Available Slots</h3>
        <p>This doctor doesn't have any available appointment slots at the moment.</p>
        <button class="btn btn-secondary" @click="$router.back()">
          ← Back to Doctors
        </button>
      </div>

      <!-- Availability Calendar -->
      <div v-else class="availability-calendar">
        <div class="calendar-header">
          <h2>Available Time Slots</h2>
          <p class="calendar-description">
            Select your preferred date and time for the appointment
          </p>
        </div>

        <div class="days-container">
          <div
            v-for="day in availability"
            :key="day.date"
            class="day-card"
          >
            <div class="day-header">
              <h3 class="day-date">{{ formatDate(day.date) }}</h3>
              <span class="day-weekday">{{ getWeekday(day.date) }}</span>
            </div>

            <div class="time-slots">
              <button
                v-for="slot in day.slots"
                :key="slot"
                class="time-slot"
                @click="bookSlot(day.date, slot)"
              >
                <span class="slot-time">{{ slot }}</span>
                <span class="slot-book">Book Now</span>
              </button>
            </div>

            <div v-if="day.slots.length === 0" class="no-slots">
              No available slots
            </div>
          </div>
        </div>

        <div class="actions-section">
          <button class="btn btn-secondary" @click="$router.back()">
            ← Back to Doctors
          </button>
          <button class="btn btn-refresh" @click="fetchAvailability">
            🔄 Refresh Availability
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "BookAppointment",

  data() {
    return {
      doctorId: null,
      doctorName: "",
      availability: [],
      loading: true,
      message: null,
      category: null
    };
  },

  async mounted() {
    this.doctorId = this.$route.params.id;

    // If the router also passed doctor name (optional improvement)
    if (this.$route.query.name) {
      this.doctorName = this.$route.query.name;
    }

    await this.fetchAvailability();
  },

  methods: {
    /** Fetch available slots from backend **/
    async fetchAvailability() {
      this.loading = true;
      this.message = null;

      try {
        const res = await fetch(`http://127.0.0.1:5000/doctor/${this.doctorId}/availability`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        const data = await res.json();

        if (res.ok) {
          this.availability = data.availability || [];
          
          // If doctor name wasn't passed via router, try to get it from availability data
          if (!this.doctorName && data.doctor_name) {
            this.doctorName = data.doctor_name;
          }
        } else {
          this.message = data.message || "Failed to load availability.";
          this.category = "danger";
        }
      } catch (err) {
        console.error(err);
        this.message = "Error fetching availability.";
        this.category = "danger";
      } finally {
        this.loading = false;
      }
    },

    /** Book selected time slot **/
    async bookSlot(date, time) {
      if (!confirm(`Confirm appointment with Dr. ${this.doctorName} on ${this.formatDate(date)} at ${time}?`)) return;

      try {
        const res = await fetch(`http://127.0.0.1:5000/appointments/book`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({
            doctor_id: this.doctorId,
            date,
            time
          })
        });

        const data = await res.json();

        if (res.ok) {
          this.message = "Appointment booked successfully!";
          this.category = "success";

          // Refresh availability after booking
          await this.fetchAvailability();
          
          // Auto-clear success message after 3 seconds
          setTimeout(() => {
            if (this.category === 'success') {
              this.message = null;
            }
          }, 3000);
        } else {
          this.message = data.message || "Failed to book appointment.";
          this.category = "danger";
        }
      } catch (err) {
        console.error(err);
        this.message = "Error booking appointment. Please try again.";
        this.category = "danger";
      }
    },

    /** Format date for display **/
    formatDate(dateString) {
      if (!dateString) return 'Unknown Date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric'
      });
    },

    /** Get weekday from date **/
    getWeekday(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { weekday: 'long' });
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

.book-appointment-page {
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

.alert-warning {
  background-color: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
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

/* Appointment Content */
.appointment-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
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
  margin-bottom: 25px;
  line-height: 1.6;
}

/* Availability Calendar */
.calendar-header {
  text-align: center;
  margin-bottom: 30px;
}

.calendar-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.calendar-description {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Days Container */
.days-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

/* Day Card */
.day-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
}

.day-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.day-header {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f1f8ff;
}

.day-date {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.day-weekday {
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Time Slots */
.time-slots {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.time-slot {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 12px 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.time-slot:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.slot-time {
  font-size: 0.9rem;
  font-weight: 600;
}

.slot-book {
  font-size: 0.7rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* No Slots */
.no-slots {
  text-align: center;
  color: #7f8c8d;
  font-style: italic;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 6px;
}

/* Actions Section */
.actions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #eaeaea;
  flex-wrap: wrap;
  gap: 15px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.btn-refresh {
  background: #17a2b8;
  color: white;
}

.btn-refresh:hover {
  background: #138496;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .book-appointment-page {
    padding: 15px;
  }
  
  .days-container {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn {
    justify-content: center;
    width: 100%;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .appointment-content {
    padding: 20px;
  }
  
  .time-slots {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
}

@media (max-width: 480px) {
  .day-card {
    padding: 15px;
  }
  
  .time-slot {
    padding: 10px 6px;
  }
  
  .slot-time {
    font-size: 0.85rem;
  }
  
  .slot-book {
    font-size: 0.65rem;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .calendar-header h2 {
    font-size: 1.5rem;
  }
}
</style>