<template>
  <div class="export-history-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Export Treatment History</h1>
      <p>Download your complete medical records and treatment history</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Export Section -->
    <section class="export-section">
      <div class="export-card">
        <div class="export-header">
          <h2>Generate New Report</h2>
          <p class="export-description">
            Create a comprehensive CSV file containing your complete treatment history, 
            including all appointments, diagnoses, prescriptions, and medical notes.
          </p>
        </div>

        <div class="export-actions">
          <button 
            class="export-btn" 
            @click="triggerExport" 
            :disabled="isProcessing"
          >
            <span v-if="isProcessing" class="btn-loading">
              <span class="spinner"></span>
              Generating Report...
            </span>
            <span v-else>
              📊 Export Treatment History
            </span>
          </button>
          
          <div class="export-info">
            <p>⏱️ Report generation usually takes 10-30 seconds</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Available Reports -->
    <section class="reports-section">
      <div class="reports-card">
        <div class="reports-header">
          <h2>Available Reports</h2>
          <button class="refresh-btn" @click="fetchDownloads">
            🔄 Refresh List
          </button>
        </div>

        <!-- Reports List -->
        <div v-if="downloads.length" class="reports-list">
          <div class="report-item" v-for="file in downloads" :key="file">
            <div class="report-info">
              <div class="report-icon">📄</div>
              <div class="report-details">
                <h4 class="report-name">{{ file }}</h4>
                <p class="report-type">CSV Treatment History</p>
              </div>
            </div>
            <button class="download-btn" @click="downloadFile(file)">
              ⬇️ Download
            </button>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>No Reports Available</h3>
          <p>Generated reports will appear here. Start by creating your first report above.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "PatientExportHistory",

  data() {
    return {
      message: null,
      category: null,
      downloads: [],
      isProcessing: false,
      timer: null,
    };
  },

  methods: {
    // 🔵 Trigger CSV Export
    async triggerExport() {
      this.isProcessing = true;
      this.message = null;

      try {
        const res = await fetch(`http://127.0.0.1:5000/patient/export_treatments`, {
          method: "GET",
          headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
        });

        if (res.ok) {
          this.message = "Export started! Your report will be ready shortly...";
          this.category = "success";
          this.fetchDownloads();
        } else {
          const data = await res.json();
          this.message = data.message || "Failed to start export.";
          this.category = "danger";
        }
      } catch (err) {
        console.error(err);
        this.message = "Server error. Please try again later.";
        this.category = "danger";
      } finally {
        this.isProcessing = false;
      }
    },

    // 🔵 Fetch downloadable reports
    async fetchDownloads() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/patient/reports/list`, {
          method: "GET",
          headers: { Authorization: "Bearer " + localStorage.getItem("token") },
        });

        // If unauthorized, avoid clearing list
        if (response.status === 401) {
          console.warn("Token expired or unauthorized");
          return;
        }

        if (response.ok) {
          const data = await response.json();

          // Decode JWT to extract patient ID
          const token = localStorage.getItem("token");
          const payload = JSON.parse(atob(token.split(".")[1]));
          const userId = payload.user_id;

          this.downloads = (data.downloads || [])
            .map((p) => p.split(/[/\\]/).pop()) // Extract filename
            .filter((name) => name.includes(`patient_${userId}`));
        }
      } catch (error) {
        console.error("Error fetching downloads:", error);
      }
    },

    // 🔵 Download File
    async downloadFile(filename) {
      try {
        const res = await fetch(`http://127.0.0.1:5000/patient/reports/download/${filename}`, {
          headers: { Authorization: "Bearer " + localStorage.getItem("token") },
        });

        if (!res.ok) {
          throw new Error('Download failed');
        }

        const blob = await res.blob();
        const link = document.createElement("a");

        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();

        URL.revokeObjectURL(link.href);
        
        this.message = "File downloaded successfully!";
        this.category = "success";
      } catch (error) {
        console.error("Download error:", error);
        this.message = "Failed to download file. Please try again.";
        this.category = "danger";
      }
    },
  },

  mounted() {
    this.fetchDownloads();
    this.timer = setInterval(this.fetchDownloads, 10000); // Refresh every 10 sec
  },

  beforeUnmount() {
    clearInterval(this.timer);
  },
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.export-history-page {
  max-width: 800px;
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

/* Export Section */
.export-section {
  margin-bottom: 40px;
}

.export-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.export-header {
  text-align: center;
  margin-bottom: 30px;
}

.export-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 12px;
}

.export-description {
  color: #7f8c8d;
  font-size: 1rem;
  line-height: 1.6;
  max-width: 600px;
  margin: 0 auto;
}

/* Export Actions */
.export-actions {
  text-align: center;
}

.export-btn {
  background: linear-gradient(135deg, #3498db, #2c3e50);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3);
}

.export-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 10px;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.export-info {
  text-align: center;
}

.export-info p {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin: 0;
}

/* Reports Section */
.reports-section {
  margin-bottom: 40px;
}

.reports-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.reports-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.reports-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin: 0;
}

.refresh-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* Reports List */
.reports-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #eaeaea;
  border-radius: 10px;
  background: white;
  transition: all 0.3s ease;
}

.report-item:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.report-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.report-icon {
  font-size: 1.8rem;
}

.report-details {
  display: flex;
  flex-direction: column;
}

.report-name {
  color: #2c3e50;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.report-type {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin: 0;
}

.download-btn {
  background: #28a745;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.download-btn:hover {
  background: #218838;
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .export-history-page {
    padding: 15px;
  }
  
  .export-card,
  .reports-card {
    padding: 30px 25px;
  }
  
  .reports-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .refresh-btn {
    align-self: flex-start;
  }
  
  .report-item {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
    text-align: center;
  }
  
  .report-info {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .export-card,
  .reports-card {
    padding: 25px 20px;
  }
  
  .export-btn {
    padding: 14px 24px;
    font-size: 1rem;
  }
  
  .report-item {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .export-header h2,
  .reports-header h2 {
    font-size: 1.5rem;
  }
}
</style>