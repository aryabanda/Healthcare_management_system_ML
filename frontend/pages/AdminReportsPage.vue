<template>
  <div class="export-reports-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Export Doctor Reports</h1>
      <p>Generate and download professional service reports</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Export Section -->
    <div class="export-section">
      <div class="export-card">
        <h2>Generate New Report</h2>
        <p class="section-description">
          Enter a professional ID to generate a service request report for a doctor.
        </p>

        <div class="export-form">
          <div class="input-group">
            <label for="professionalId">Professional ID</label>
            <input
              id="professionalId"
              type="number"
              class="form-input"
              placeholder="Enter doctor's professional ID"
              v-model="professionalId"
              :disabled="isProcessing"
            />
          </div>

          <button
            class="export-btn"
            @click="triggerExport"
            :disabled="isProcessing || !professionalId"
          >
            <span v-if="isProcessing" class="btn-loading">
              <span class="spinner"></span>
              Processing...
            </span>
            <span v-else>
              📊 Export Service Requests
            </span>
          </button>
        </div>
      </div>
    </div>

    <!-- Available Downloads -->
    <div class="downloads-section">
      <div class="downloads-card">
        <div class="section-header">
          <h2>Available Reports</h2>
          <button class="refresh-btn" @click="fetchDownloads">
            🔄 Refresh
          </button>
        </div>

        <div v-if="downloads.length" class="downloads-list">
          <div class="download-item" v-for="(file, index) in downloads" :key="index">
            <div class="file-info">
              <div class="file-icon">📄</div>
              <div class="file-details">
                <span class="file-name">{{ file }}</span>
                <span class="file-type">CSV Report</span>
              </div>
            </div>
            <button
              class="download-btn"
              @click="downloadFile(file)"
            >
              ⬇️ Download
            </button>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-icon">📋</div>
          <h3>No Reports Available</h3>
          <p>Generated reports will appear here. Start by creating your first report above.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "ExportServiceRequests",

  data() {
    return {
      professionalId: "",
      downloads: [],
      isProcessing: false,
      message: null,
      category: null,
      timer: null
    };
  },

  methods: {
    async triggerExport() {
      if (!this.professionalId) {
        this.message = "Please enter a valid professional ID!";
        this.category = "danger";
        return;
      }

      this.isProcessing = true;
      this.message = null;

      try {
        const response = await fetch(
          `http://127.0.0.1:5000/admin/export/${this.professionalId}`,
          {
            method: "GET",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token")
            }
          }
        );

        if (response.ok) {
          const data = await response.json().catch(() => ({}));
          this.message = data.message || "Export triggered successfully!";
          this.category = "success";
          this.fetchDownloads();
        } else {
          const err = await response.json();
          this.message = err.message || "Failed to start export.";
          this.category = "danger";
        }
      } catch (error) {
        console.error("Error triggering export:", error);
        this.message = "Error triggering export.";
        this.category = "danger";
      } finally {
        this.isProcessing = false;
      }
    },

    async fetchDownloads() {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/admin/reports/list`,
          {
            method: "GET",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token")
            }
          }
        );

        if (response.ok) {
          const data = await response.json();
          this.downloads = data.downloads || [];
        }
      } catch (error) {
        console.error("Error fetching downloads:", error);
      }
    },

    async downloadFile(filename) {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/admin/reports/download/${filename}`,
          {
            method: "GET",
            headers: {
              Authorization: "Bearer " + localStorage.getItem("token")
            }
          }
        );

        if (!response.ok) {
          this.message = "Error downloading file.";
          this.category = "danger";
          return;
        }

        const blob = await response.blob();
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        URL.revokeObjectURL(link.href);
        
        this.message = "File downloaded successfully!";
        this.category = "success";
      } catch (error) {
        console.error("Error downloading file:", error);
        this.message = "An error occurred while downloading the file.";
        this.category = "danger";
      }
    }
  },

  mounted() {
    this.fetchDownloads();
    this.timer = setInterval(this.fetchDownloads, 10000);
  },

  beforeUnmount() {
    clearInterval(this.timer);
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.export-reports-page {
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

/* Export Section */
.export-section {
  margin-bottom: 40px;
}

.export-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.export-card h2 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 10px;
}

.section-description {
  color: #7f8c8d;
  margin-bottom: 25px;
  line-height: 1.5;
}

/* Export Form */
.export-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.form-input {
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

.form-input:disabled {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
}

.export-btn {
  background: linear-gradient(135deg, #3498db, #2c3e50);
  color: white;
  border: none;
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Downloads Section */
.downloads-section {
  margin-bottom: 40px;
}

.downloads-card {
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
  font-size: 1.5rem;
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

/* Downloads List */
.downloads-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.download-item:hover {
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-icon {
  font-size: 1.5rem;
}

.file-details {
  display: flex;
  flex-direction: column;
}

.file-name {
  color: #2c3e50;
  font-weight: 600;
  font-size: 1rem;
}

.file-type {
  color: #7f8c8d;
  font-size: 0.85rem;
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
  padding: 40px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 10px;
}

.empty-state p {
  font-size: 1rem;
  margin: 0;
  line-height: 1.5;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* Responsive Design */
@media (max-width: 768px) {
  .export-reports-page {
    padding: 15px;
  }
  
  .export-card,
  .downloads-card {
    padding: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .refresh-btn {
    align-self: flex-start;
  }
  
  .download-item {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
    text-align: center;
  }
  
  .file-info {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}

@media (max-width: 480px) {
  .export-form {
    gap: 15px;
  }
  
  .form-input,
  .export-btn {
    padding: 12px;
  }
  
  .download-item {
    padding: 15px;
  }
}
</style>