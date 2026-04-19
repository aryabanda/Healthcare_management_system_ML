<template>
  <div class="dashboard">
    <!-- Header Section -->
    <header class="dashboard-header">
      <h1>Hospital Dashboard</h1>
      <p>Overview of hospital appointments and statistics</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Statistics Cards -->
    <div class="stats-container">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-md"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_doctors }}</h3>
          <p>Total Doctors</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-user-injured"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_patients }}</h3>
          <p>Total Patients</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-calendar-check"></i>
        </div>
        <div class="stat-content">
          <h3>{{ stats.total_appointments }}</h3>
          <p>Total Appointments</p>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-container">
      <div class="chart-card">
        <h3>Upcoming Appointments</h3>
        <canvas id="appointmentsChart" width="400" height="250"></canvas>
      </div>

      <div class="chart-card">
        <h3>Appointments by Status</h3>
        <canvas id="statusChart" width="400" height="250"></canvas>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from "chart.js/auto";

export default {
  name: "AdminDashboard",

  data() {
    return {
      message: null,
      category: null,

      stats: {
        total_doctors: 0,
        total_patients: 0,
        total_appointments: 0,
        upcoming_appointments: 0
      },

      appointments: [],
      appointmentsChart: null,
      statusChart: null
    };
  },

  mounted() {
    this.fetchDashboardStats();
    this.fetchAppointments();
  },

  methods: {
    async fetchDashboardStats() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/admin/dashboard`, {
          headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
          }
        });

        if (!res.ok) throw new Error("Failed to fetch dashboard");

        const data = await res.json();
        this.stats = data;

      } catch (err) {
        this.message = err.message;
        this.category = "danger";
      }
    },

    async fetchAppointments() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/admin/appointments`, {
          headers: {
            "Authorization": "Bearer " + localStorage.getItem("token")
          }
        });

        if (!res.ok) throw new Error("Failed to fetch appointments");

        const data = await res.json();
        this.appointments = data;

        this.renderCharts();

      } catch (err) {
        console.error(err);
        this.message = err.message;
        this.category = "danger";
      }
    },

    renderCharts() {
      const ctx1 = document.getElementById("appointmentsChart").getContext("2d");
      const ctx2 = document.getElementById("statusChart").getContext("2d");

      // Group by date
      const grouped = {};
      this.appointments.forEach(a => {
        grouped[a.date] = (grouped[a.date] || 0) + 1;
      });

      const labels = Object.keys(grouped);
      const counts = Object.values(grouped);

      if (this.appointmentsChart) this.appointmentsChart.destroy();

      this.appointmentsChart = new Chart(ctx1, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Appointments per Day",
              data: counts,
              backgroundColor: "rgba(54, 162, 235, 0.4)",
              borderColor: "rgba(54, 162, 235, 1)",
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          scales: {
            y: { beginAtZero: true }
          }
        }
      });

      // Group by status
      const statusGrouped = {};
      this.appointments.forEach(a => {
        statusGrouped[a.status] = (statusGrouped[a.status] || 0) + 1;
      });

      const sLabels = Object.keys(statusGrouped);
      const sCounts = Object.values(statusGrouped);

      if (this.statusChart) this.statusChart.destroy();

      this.statusChart = new Chart(ctx2, {
        type: "doughnut",
        data: {
          labels: sLabels,
          datasets: [
            {
              label: "Appointment Status",
              data: sCounts,
              backgroundColor: [
                "rgba(75,192,192,0.5)",
                "rgba(255,159,64,0.5)",
                "rgba(255,99,132,0.5)",
                "rgba(153,102,255,0.5)"
              ],
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "bottom" }
          }
        }
      });
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

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f7fa;
  color: #333;
}

.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* Header */
.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px 0;
}

.dashboard-header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 10px;
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

/* Statistics Cards */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  background: #3498db;
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
}

/* Charts */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 25px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.chart-card h3 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard {
    padding: 15px;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
  }
}
</style>