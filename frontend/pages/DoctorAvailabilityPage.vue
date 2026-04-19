<template>
  <div class="availability-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Manage Availability</h1>
      <p>Set your availability for the next 7 days</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading your availability...</p>
    </div>

    <!-- Main Content -->
    <div v-else class="availability-content">
      <div class="availability-card">
        <div class="card-header">
          <h2>Next 7 Days Schedule</h2>
          <p class="card-description">
            Toggle your availability for each day. Patients can only book appointments on available days.
          </p>
        </div>

        <div class="days-grid">
          <div 
            v-for="day in days" 
            :key="day.date" 
            class="day-card"
            :class="{ 'unavailable': !day.available }"
          >
            <div class="day-header">
              <h3 class="day-name">{{ day.dayName }}</h3>
              <span class="day-date">{{ formatDate(day.date) }}</span>
            </div>
            
            <div class="day-status">
              <span class="status-text" :class="{ 'available': day.available, 'unavailable': !day.available }">
                {{ day.available ? 'Available' : 'Unavailable' }}
              </span>
            </div>

            <div class="day-toggle">
              <label class="toggle-switch">
                <input 
                  type="checkbox" 
                  v-model="day.available" 
                  class="toggle-input"
                />
                <span class="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>

        <div class="actions-section">
          <button class="save-btn" @click="saveAvailability">
            💾 Save Availability
          </button>
          <button class="reset-btn" @click="resetToDefault">
            🔄 Reset to Default
          </button>
        </div>

        <div class="availability-summary">
          <div class="summary-item available">
            <span class="summary-count">{{ availableDaysCount }}</span>
            <span class="summary-label">Available Days</span>
          </div>
          <div class="summary-item unavailable">
            <span class="summary-count">{{ unavailableDaysCount }}</span>
            <span class="summary-label">Unavailable Days</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DoctorAvailability",

  data() {
    return {
      days: [],
      loading: true,
      message: null,
      category: null
    };
  },

  computed: {
    availableDaysCount() {
      return this.days.filter(day => day.available).length;
    },
    unavailableDaysCount() {
      return this.days.filter(day => !day.available).length;
    }
  },

  async mounted() {
    this.generateNext7Days();
    await this.fetchAvailability();
  },

  methods: {
    /** Generate next 7 days **/
    generateNext7Days() {
      const today = new Date();

      this.days = Array.from({ length: 7 }, (_, i) => {
        const date = new Date(today);
        date.setDate(today.getDate() + i);

        return {
          date: date.toLocaleDateString("en-CA"), // YYYY-MM-DD
          dayName: date.toLocaleDateString("en-US", { weekday: "long" }),
          available: true // default true
        };
      });
    },

    /** Fetch saved availability **/
    async fetchAvailability() {
      this.loading = true;

      try {
        const res = await fetch(`http://127.0.0.1:5000/doctor/availability`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        const data = await res.json();

        if (res.ok && data.availability) {
          let saved = data.availability;

          // If backend returns JSON string, parse it
          if (typeof saved === "string") {
            try {
              saved = JSON.parse(saved);
            } catch (e) {
              console.error("Invalid availability JSON:", saved);
              saved = {};
            }
          }

          // Merge saved availability with generated days
          this.days.forEach((d) => {
            if (Object.prototype.hasOwnProperty.call(saved, d.date)) {
              d.available = Boolean(saved[d.date]);
            }
          });
        }
      } catch (err) {
        console.error("Error fetching availability:", err);
        this.message = "Error loading availability.";
        this.category = "danger";
      } finally {
        this.loading = false;
      }
    },

    /** Save doctor availability **/
    async saveAvailability() {
      const availability = {};
      this.days.forEach((d) => {
        availability[d.date] = d.available;
      });

      try {
        const res = await fetch(`http://127.0.0.1:5000/doctor/availability`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({ availability })
        });

        const data = await res.json();

        if (res.ok) {
          this.message = "Availability saved successfully!";
          this.category = "success";
          
          // Auto-clear success message after 3 seconds
          setTimeout(() => {
            if (this.category === 'success') {
              this.message = null;
            }
          }, 3000);
        } else {
          this.message = data.message || "Failed to save availability.";
          this.category = "danger";
        }
      } catch (err) {
        console.error(err);
        this.message = "Network error saving availability.";
        this.category = "danger";
      }
    },

    /** Reset all days to available **/
    resetToDefault() {
      if (confirm("Reset all days to available? This will clear your current settings.")) {
        this.days.forEach(day => {
          day.available = true;
        });
        this.message = "All days reset to available.";
        this.category = "info";
      }
    },

    /** Format date for display **/
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
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

.availability-page {
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

/* Availability Card */
.availability-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.card-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 10px;
}

.card-description {
  color: #7f8c8d;
  font-size: 1rem;
  line-height: 1.5;
  max-width: 600px;
  margin: 0 auto;
}

/* Days Grid */
.days-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.day-card {
  border: 2px solid #eaeaea;
  border-radius: 12px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
  text-align: center;
}

.day-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.day-card.unavailable {
  border-color: #f8d7da;
  background-color: #fefefe;
}

.day-card:not(.unavailable) {
  border-color: #d4edda;
}

.day-header {
  margin-bottom: 15px;
}

.day-name {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.day-date {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.day-status {
  margin-bottom: 15px;
}

.status-text {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-text.available {
  background-color: #d4edda;
  color: #155724;
}

.status-text.unavailable {
  background-color: #f8d7da;
  color: #721c24;
}

/* Toggle Switch */
.day-toggle {
  display: flex;
  justify-content: center;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

.toggle-input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #dc3545;
  transition: .4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.toggle-input:checked + .toggle-slider {
  background-color: #28a745;
}

.toggle-input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

/* Actions Section */
.actions-section {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.save-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.save-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(40, 167, 69, 0.3);
}

.reset-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.reset-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Availability Summary */
.availability-summary {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding-top: 20px;
  border-top: 1px solid #eaeaea;
}

.summary-item {
  text-align: center;
  padding: 15px 25px;
  border-radius: 8px;
  min-width: 120px;
}

.summary-item.available {
  background-color: #d4edda;
  border: 1px solid #c3e6cb;
}

.summary-item.unavailable {
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.summary-count {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.summary-item.available .summary-count {
  color: #155724;
}

.summary-item.unavailable .summary-count {
  color: #721c24;
}

.summary-label {
  font-size: 0.9rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-item.available .summary-label {
  color: #155724;
}

.summary-item.unavailable .summary-label {
  color: #721c24;
}

/* Responsive Design */
@media (max-width: 768px) {
  .availability-page {
    padding: 15px;
  }
  
  .days-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
    align-items: center;
  }
  
  .save-btn,
  .reset-btn {
    width: 100%;
    max-width: 250px;
    justify-content: center;
  }
  
  .availability-summary {
    flex-direction: column;
    gap: 15px;
    align-items: center;
  }
  
  .summary-item {
    width: 100%;
    max-width: 200px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .availability-card {
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .day-card {
    padding: 15px;
  }
  
  .card-header h2 {
    font-size: 1.5rem;
  }
  
  .summary-count {
    font-size: 1.5rem;
  }
}
</style>