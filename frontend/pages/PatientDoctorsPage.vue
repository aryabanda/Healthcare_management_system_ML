<template>
  <div class="customer-search-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Find Services</h1>
      <p>Search for professional services in your area</p>
    </header>

    <!-- Alert Messages -->
    <div v-if="messages.length" class="messages-container">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="'alert alert-' + msg.category"
      >
        {{ msg.text }}
      </div>
    </div>

    <!-- Search Section -->
    <section class="search-section">
      <div class="search-card">
        <h2>Search Services</h2>
        <p class="search-description">
          Find the perfect service professional for your needs
        </p>

        <!-- Search Form -->
        <form @submit.prevent="submitSearch" class="search-form">
          <div class="form-row">
            <div class="form-group">
              <label for="search_type" class="form-label">Search By</label>
              <select
                id="search_type"
                v-model="form.search_type"
                class="form-select"
                required
              >
                <option value="service">Service Name</option>
                <option value="location">Location</option>
                <option value="pin">PIN Code</option>
              </select>
            </div>

            <div class="form-group">
              <label for="search_text" class="form-label">Search Term</label>
              <input
                id="search_text"
                v-model="form.search_text"
                type="text"
                class="form-input"
                :placeholder="getPlaceholder()"
                required
              />
            </div>

            <div class="form-group">
              <button type="submit" class="search-btn">
                🔍 Search Services
              </button>
            </div>
          </div>
        </form>

        <div class="search-actions">
          <router-link to="/customer/dashboard" class="btn btn-secondary">
            ← Back to Dashboard
          </router-link>
        </div>
      </div>
    </section>

    <!-- Search Results -->
    <section v-if="service_professional.length" class="results-section">
      <div class="results-header">
        <h2>Search Results</h2>
        <p class="results-count">{{ service_professional.length }} services found</p>
      </div>

      <div class="services-grid">
        <div 
          v-for="(service, index) in service_professional" 
          :key="index" 
          class="service-card"
        >
          <div class="service-header">
            <div class="service-icon">
              <span>🔧</span>
            </div>
            <div class="service-info">
              <h3 class="service-name">{{ service.service_name }}</h3>
              <p class="service-price">₹{{ service.service_price }}</p>
            </div>
          </div>

          <div class="service-description">
            <p>{{ service.service_description || 'Professional service available' }}</p>
          </div>

          <div class="service-details">
            <div class="detail-item">
              <span class="detail-label">📍 Location</span>
              <span class="detail-value">{{ service.address || 'Not specified' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">📮 PIN Code</span>
              <span class="detail-value">{{ service.pin_code || 'Not specified' }}</span>
            </div>
          </div>

          <div class="service-actions">
            <button class="btn btn-primary">
              Book Service
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- No Results -->
    <div v-else-if="messages.some(m => m.category === 'success')" class="empty-state">
      <div class="empty-icon">🔍</div>
      <h3>No Services Found</h3>
      <p>Try adjusting your search criteria or browse different categories.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "CustomerSearch",

  data() {
    return {
      form: {
        search_type: "service",
        search_text: ""
      },
      service_professional: [],
      messages: []
    };
  },

  methods: {
    async submitSearch() {
      this.messages = [];

      if (!this.form.search_text.trim()) {
        this.messages.push({
          category: "warning",
          text: "Please enter a search term."
        });
        return;
      }

      try {
        const response = await fetch(`http://127.0.0.1:5000/customer/search`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify(this.form)
        });

        const data = await response.json();

        if (response.ok) {
          this.service_professional = data.data?.service_professional || [];
          this.messages.push({
            category: "success",
            text: data.message || "Search completed successfully."
          });
        } else {
          this.service_professional = [];
          this.messages.push({
            category: data.category || "danger",
            text: data.message || "No results found or an error occurred."
          });
        }
      } catch (err) {
        console.error("Search request failed:", err);

        this.service_professional = [];
        this.messages.push({
          category: "danger",
          text: "An unexpected error occurred. Please try again later."
        });
      }
    },

    getPlaceholder() {
      const placeholders = {
        'service': 'e.g., Plumbing, Electrical, Cleaning...',
        'location': 'e.g., Mumbai, Delhi, Bangalore...',
        'pin': 'e.g., 400001, 110001...'
      };
      return placeholders[this.form.search_type] || 'Enter your search...';
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

.customer-search-page {
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

/* Messages */
.messages-container {
  margin-bottom: 30px;
}

.alert {
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 10px;
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

/* Search Section */
.search-section {
  margin-bottom: 40px;
}

.search-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.search-card h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 8px;
  text-align: center;
}

.search-description {
  color: #7f8c8d;
  text-align: center;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

/* Search Form */
.search-form {
  margin-bottom: 30px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  gap: 20px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-select,
.form-input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.search-btn {
  background: linear-gradient(135deg, #3498db, #2c3e50);
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
  justify-content: center;
  gap: 8px;
  height: 46px;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(52, 152, 219, 0.3);
}

/* Search Actions */
.search-actions {
  text-align: center;
}

.btn {
  padding: 10px 20px;
  border: none;
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

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Results Section */
.results-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.results-header {
  text-align: center;
  margin-bottom: 30px;
}

.results-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.results-count {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Services Grid */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 25px;
}

.service-card {
  border: 1px solid #eaeaea;
  border-radius: 12px;
  padding: 25px;
  background: white;
  transition: all 0.3s ease;
  position: relative;
}

.service-card:hover {
  border-color: #3498db;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  transform: translateY(-3px);
}

.service-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #3498db, #2c3e50);
  border-radius: 4px 4px 0 0;
}

/* Service Header */
.service-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.service-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  font-size: 1.2rem;
}

.service-info {
  flex: 1;
}

.service-name {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.service-price {
  color: #27ae60;
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
}

/* Service Description */
.service-description {
  margin-bottom: 20px;
}

.service-description p {
  color: #5a6c7d;
  line-height: 1.5;
  margin: 0;
  font-size: 0.95rem;
}

/* Service Details */
.service-details {
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-weight: 600;
  color: #5a6c7d;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-value {
  color: #2c3e50;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Service Actions */
.service-actions {
  display: flex;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
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

/* Responsive Design */
@media (max-width: 768px) {
  .customer-search-page {
    padding: 15px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .search-card,
  .results-section {
    padding: 30px 25px;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .service-card {
    padding: 20px;
  }
  
  .service-header {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
  
  .service-icon {
    margin-right: 0;
  }
}

@media (max-width: 480px) {
  .search-card,
  .results-section {
    padding: 25px 20px;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .service-card {
    padding: 15px;
  }
  
  .service-name {
    font-size: 1.1rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>