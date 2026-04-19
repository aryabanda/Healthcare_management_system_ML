<template>
  <div class="patient-history-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1>Patient Medical History</h1>
        <button class="back-btn" @click="$router.back()">
          ← Back
        </button>
      </div>
      <p class="page-subtitle">Complete medical record and consultation history</p>
    </header>

    <!-- History Content -->
    <div class="history-content">
      <div v-if="history.length" class="history-list">
        <div class="history-card" v-for="(h, i) in history" :key="i">
          <div class="history-header">
            <div class="consultation-info">
              <h3 class="consultation-title">Consultation #{{ i + 1 }}</h3>
              <div class="consultation-meta">
                <span class="consultation-date">{{ formatDate(h.date) }}</span>
                <span class="consultation-time">{{ h.time }}</span>
              </div>
            </div>
            <div class="doctor-info">
              <span class="doctor-name">Dr. {{ h.doctor }}</span>
            </div>
          </div>

          <div class="history-details">
            <div class="detail-section">
              <h4>Diagnosis</h4>
              <div class="detail-content">
                <p>{{ h.diagnosis || "No diagnosis recorded" }}</p>
              </div>
            </div>

            <div class="detail-section">
              <h4>Prescription</h4>
              <div class="detail-content">
                <p>{{ h.prescription || "No prescription given" }}</p>
              </div>
            </div>

            <div class="detail-section">
              <h4>Medical Notes</h4>
              <div class="detail-content">
                <p>{{ h.notes || "No additional notes" }}</p>
              </div>
            </div>
            <div class="detail-section" v-if="h.readmission_risk">
              <h4>Readmission Risk</h4>
              <div class="detail-content">
                <p>
                  {{ h.readmission_risk.risk_label }}
                  ({{ (h.readmission_risk.risk_probability * 100).toFixed(2) }}%)
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No Medical History Available</h3>
        <p>This patient doesn't have any recorded medical history yet.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PatientHistory",

  data() {
    return {
      history: []
    };
  },

  async mounted() {
    const id = this.$route.params.id;

    try {
      const res = await fetch(`http://127.0.0.1:5000/patient/${id}/history`, {
        headers: {
          Authorization: "Bearer " + localStorage.getItem("token")
        }
      });

      if (res.ok) {
        const data = await res.json();
        this.history = data.history || [];
      } else {
        console.error("Failed to fetch patient history");
      }
    } catch (error) {
      console.error("Error fetching patient history:", error);
    }
  },

  methods: {
    formatDate(dateString) {
      if (!dateString) return 'Unknown Date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
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

.patient-history-page {
  max-width: 1000px;
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
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 15px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2.2rem;
  margin: 0;
}

.page-subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* Back Button */
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

/* History Content */
.history-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* History List */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

/* History Card */
.history-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
}

.history-card:hover {
  border-color: #3498db;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.history-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(to bottom, #3498db, #2c3e50);
  border-radius: 4px 0 0 4px;
}

/* History Header */
.history-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f1f8ff;
  flex-wrap: wrap;
  gap: 15px;
}

.consultation-info {
  flex: 1;
}

.consultation-title {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 8px;
}

.consultation-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.consultation-date {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 500;
}

.consultation-time {
  color: #7f8c8d;
  font-size: 0.95rem;
  background: #f8f9fa;
  padding: 4px 10px;
  border-radius: 15px;
}

/* Doctor Info */
.doctor-info {
  text-align: right;
}

.doctor-name {
  color: #3498db;
  font-size: 1.1rem;
  font-weight: 600;
  background: #f1f8ff;
  padding: 8px 16px;
  border-radius: 20px;
  display: inline-block;
}

/* History Details */
.history-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.detail-section {
  display: flex;
  flex-direction: column;
}

.detail-section h4 {
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 2px solid #f1f8ff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.detail-content {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 3px solid #3498db;
  min-height: 100px;
  display: flex;
  align-items: flex-start;
}

.detail-content p {
  color: #5a6c7d;
  line-height: 1.6;
  margin: 0;
  font-size: 0.95rem;
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
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .patient-history-page {
    padding: 15px;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .history-content {
    padding: 20px;
  }
  
  .history-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .doctor-info {
    text-align: left;
    align-self: flex-start;
  }
  
  .history-details {
    grid-template-columns: 1fr;
  }
  
  .history-card {
    padding: 20px;
  }
  
  .consultation-meta {
    flex-direction: column;
    gap: 5px;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .history-card {
    padding: 15px;
  }
  
  .consultation-title {
    font-size: 1.1rem;
  }
  
  .doctor-name {
    font-size: 1rem;
    padding: 6px 12px;
  }
  
  .detail-content {
    padding: 12px;
    min-height: 80px;
  }
  
  .detail-content p {
    font-size: 0.9rem;
  }
}
</style>