<template>
  <div class="treatment-history-page">
    <!-- Header -->
    <header class="page-header">
      <h1>My Treatment History</h1>
      <p>Complete record of your medical consultations and treatments</p>
    </header>

    <!-- Main Content -->
    <div class="history-content">
      <!-- No History -->
      <div v-if="history.length === 0" class="empty-state">
        <div class="empty-icon">📋</div>
        <h3>No Treatment History Found</h3>
        <p>You don't have any recorded medical consultations yet.</p>
      </div>

      <!-- History Timeline -->
      <div v-else class="history-timeline">
        <div class="timeline-header">
          <h2>Medical Consultations</h2>
          <p class="consultation-count">{{ history.length }} consultation{{ history.length !== 1 ? 's' : '' }} recorded</p>
        </div>

        <div class="consultation-list">
          <div 
            v-for="(h, index) in history" 
            :key="index" 
            class="consultation-card"
          >
            <div class="consultation-header">
              <div class="consultation-date">
                <span class="date">{{ formatDate(h.date) }}</span>
                <span class="time">{{ h.time }}</span>
              </div>
              <div class="doctor-info">
                <span class="doctor-name">Dr. {{ h.doctor }}</span>
              </div>
            </div>

            <div class="consultation-details">
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

            <div class="consultation-number">
              Consultation #{{ history.length - index }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "PatientTreatmentHistory",

  data() {
    return {
      history: [],
    };
  },

  async mounted() {
    try {
      const token = localStorage.getItem("token");
      const payload = JSON.parse(atob(token.split(".")[1]));
      const userId = payload.user_id;

      const res = await fetch(`http://127.0.0.1:5000/patient/${userId}/history`, {
        headers: { Authorization: "Bearer " + token },
      });

      if (res.ok) {
        const data = await res.json();
        this.history = data.history || [];
      }
    } catch (error) {
      console.error("Error loading treatment history:", error);
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

.treatment-history-page {
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
  padding: 30px 20px;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.page-header p {
  color: #7f8c8d;
  font-size: 1.2rem;
}

/* History Content */
.history-content {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-bottom: 40px;
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

/* Timeline Header */
.timeline-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f1f8ff;
}

.timeline-header h2 {
  color: #2c3e50;
  font-size: 2rem;
  margin-bottom: 8px;
}

.consultation-count {
  color: #7f8c8d;
  font-size: 1.1rem;
  font-weight: 500;
}

/* Consultation List */
.consultation-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* Consultation Card */
.consultation-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 30px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.consultation-card:hover {
  border-color: #3498db;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.consultation-card::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(to bottom, #3498db, #2c3e50);
  border-radius: 4px 0 0 4px;
}

/* Consultation Header */
.consultation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 15px;
}

.consultation-date {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.date {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
}

.time {
  color: #3498db;
  font-size: 1rem;
  font-weight: 500;
  background: #f1f8ff;
  padding: 6px 12px;
  border-radius: 20px;
  display: inline-block;
  width: fit-content;
}

.doctor-info {
  text-align: right;
}

.doctor-name {
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  display: inline-block;
}

/* Consultation Details */
.consultation-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
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

/* Consultation Number */
.consultation-number {
  text-align: right;
  color: #7f8c8d;
  font-size: 0.85rem;
  font-weight: 500;
  font-style: italic;
  padding-top: 10px;
  border-top: 1px solid #f1f8ff;
}

/* Responsive Design */
@media (max-width: 768px) {
  .treatment-history-page {
    padding: 15px;
  }
  
  .history-content {
    padding: 30px 25px;
  }
  
  .consultation-header {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .doctor-info {
    text-align: left;
  }
  
  .consultation-details {
    grid-template-columns: 1fr;
  }
  
  .consultation-card {
    padding: 25px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .timeline-header h2 {
    font-size: 1.7rem;
  }
}

@media (max-width: 480px) {
  .history-content {
    padding: 25px 20px;
  }
  
  .consultation-card {
    padding: 20px;
  }
  
  .date {
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
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .timeline-header h2 {
    font-size: 1.5rem;
  }
}
</style>