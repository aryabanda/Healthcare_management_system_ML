<template>
  <div class="feedback-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Service Request Feedback</h1>
      <p>Share your experience and help us improve our services</p>
    </header>

    <!-- Alert Messages -->
    <div v-if="flashMessages.length" class="messages-container">
      <div
        v-for="(message, index) in flashMessages"
        :key="index"
        class="alert"
        :class="'alert-' + message.category"
      >
        {{ message.text }}
      </div>
    </div>

    <!-- Feedback Form -->
    <section class="feedback-section">
      <div class="feedback-card">
        <div class="card-header">
          <h2>Service Details</h2>
          <p class="card-description">
            Please provide your feedback for the completed service
          </p>
        </div>

        <form @submit.prevent="submitForm" class="feedback-form">
          <!-- Service Information -->
          <div class="service-info">
            <div class="info-grid">
              <div class="info-item">
                <label class="info-label">
                  <span class="label-icon">📋</span>
                  Request ID
                </label>
                <div class="info-value">{{ formData.request_id }}</div>
              </div>

              <div class="info-item">
                <label class="info-label">
                  <span class="label-icon">🔧</span>
                  Service Name
                </label>
                <div class="info-value">{{ formData.service_name }}</div>
              </div>

              <div class="info-item">
                <label class="info-label">
                  <span class="label-icon">👤</span>
                  Customer Name
                </label>
                <div class="info-value">{{ formData.full_name }}</div>
              </div>

              <div class="info-item full-width">
                <label class="info-label">
                  <span class="label-icon">📝</span>
                  Service Description
                </label>
                <div class="info-value">{{ formData.service_description }}</div>
              </div>
            </div>
          </div>

          <!-- Feedback Section -->
          <div class="feedback-inputs">
            <h3>Your Feedback</h3>

            <!-- Rating -->
            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">⭐</span>
                Service Rating
              </label>
              <div class="rating-container">
                <div class="rating-stars">
                  <button
                    v-for="star in 5"
                    :key="star"
                    type="button"
                    class="star-btn"
                    :class="{ 'active': star <= formData.rating }"
                    @click="formData.rating = star"
                  >
                    ★
                  </button>
                </div>
                <div class="rating-text">
                  {{ getRatingText(formData.rating) }}
                </div>
              </div>
              <small class="form-help">Click on stars to rate the service (1-5)</small>
            </div>

            <!-- Remarks -->
            <div class="form-group">
              <label for="remarks" class="form-label">
                <span class="label-icon">💬</span>
                Your Remarks
              </label>
              <textarea
                id="remarks"
                v-model="formData.remarks"
                class="form-textarea"
                placeholder="Tell us about your experience with the service. What did you like? How can we improve?"
                rows="5"
              ></textarea>
              <small class="form-help">Share your detailed feedback about the service quality</small>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="submit" class="submit-btn">
              📤 Submit Feedback
            </button>
            <button type="button" @click="cancel" class="cancel-btn">
              ← Back to Dashboard
            </button>
          </div>
        </form>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "ServiceRequestFeedback",

  props: {
    id: {
      type: [String, Number],
      required: true,
    },
  },

  data() {
    return {
      flashMessages: [],
      formData: {
        request_id: "",
        service_name: "",
        full_name: "",
        service_description: "",
        remarks: "",
        rating: null,
      },
    };
  },

  created() {
    if (this.id) {
      this.fetchServiceRequest();
    } else {
      alert("No service request ID provided.");
      this.$router.push("/customer/dashboard");
    }
  },

  methods: {
    async fetchServiceRequest() {
      try {
        const response = await fetch(
          `http://127.0.0.1:5000/customer/close_service_request/${this.id}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          this.formData = {
            request_id: data.id,
            service_name: data.service_name,
            full_name: data.full_name,
            service_description: data.service_description,
            remarks: data.remarks || "",
            rating: data.rating || null,
          };
        } else {
          const err = await response.json();
          this.flashMessages = [
            {
              text: err.message || "Failed to load service request.",
              category: err.category || "danger",
            },
          ];
        }
      } catch (error) {
        console.error("Error fetching service request:", error);
        this.flashMessages = [
          { text: "Error loading data.", category: "danger" },
        ];
      }
    },

    async submitForm() {
      if (!this.formData.remarks.trim() || !this.formData.rating) {
        this.flashMessages = [
          {
            text: "Please provide both a rating and remarks.",
            category: "warning",
          },
        ];
        return;
      }

      try {
        const response = await fetch(
          `http://127.0.0.1:5000/customer/close_service_request/${this.formData.request_id}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            body: JSON.stringify(this.formData),
          }
        );

        const data = await response.json();

        if (response.ok) {
          this.flashMessages = [
            {
              text: data.message || "Thank you! Your feedback has been submitted successfully.",
              category: "success",
            },
          ];
          setTimeout(() => this.$router.push("/customer/dashboard"), 2000);
        } else {
          this.flashMessages = [
            {
              text: data.message || "Failed to submit feedback. Please try again.",
              category: "danger",
            },
          ];
        }
      } catch (error) {
        console.error("Submit error:", error);
        this.flashMessages = [
          {
            text: "Network error. Please try again later.",
            category: "danger",
          },
        ];
      }
    },

    cancel() {
      this.$router.push("/customer/dashboard");
    },

    getRatingText(rating) {
      const ratings = {
        1: "Poor - Very dissatisfied",
        2: "Fair - Needs improvement",
        3: "Good - Met expectations",
        4: "Very Good - Exceeded expectations",
        5: "Excellent - Outstanding service"
      };
      return ratings[rating] || "Select a rating";
    }
  },
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.feedback-page {
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

/* Feedback Section */
.feedback-section {
  margin-bottom: 40px;
}

.feedback-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f1f8ff;
}

.card-header h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.card-description {
  color: #7f8c8d;
  font-size: 1rem;
}

/* Service Information */
.service-info {
  margin-bottom: 40px;
  padding: 25px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #3498db;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.label-icon {
  font-size: 1rem;
}

.info-value {
  color: #5a6c7d;
  font-size: 1rem;
  font-weight: 500;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #eaeaea;
}

/* Feedback Inputs */
.feedback-inputs {
  margin-bottom: 40px;
}

.feedback-inputs h3 {
  color: #2c3e50;
  font-size: 1.5rem;
  margin-bottom: 25px;
  text-align: center;
}

.form-group {
  margin-bottom: 30px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 1rem;
}

/* Rating System */
.rating-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rating-stars {
  display: flex;
  gap: 8px;
}

.star-btn {
  background: none;
  border: none;
  font-size: 2.5rem;
  color: #ddd;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 5px;
}

.star-btn:hover {
  transform: scale(1.2);
  color: #ffc107;
}

.star-btn.active {
  color: #ffc107;
  text-shadow: 0 2px 8px rgba(255, 193, 7, 0.4);
}

.rating-text {
  color: #7f8c8d;
  font-size: 0.95rem;
  font-weight: 500;
  text-align: center;
}

/* Textarea */
.form-textarea {
  width: 100%;
  padding: 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  resize: vertical;
  min-height: 120px;
}

.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-help {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 6px;
  display: block;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
  padding-top: 20px;
  border-top: 2px solid #f1f8ff;
}

.submit-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(40, 167, 69, 0.3);
}

.cancel-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.cancel-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Responsive Design */
@media (max-width: 768px) {
  .feedback-page {
    padding: 15px;
  }
  
  .feedback-card {
    padding: 30px 25px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .submit-btn,
  .cancel-btn {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .star-btn {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .feedback-card {
    padding: 25px 20px;
  }
  
  .service-info {
    padding: 20px;
  }
  
  .rating-stars {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .card-header h2 {
    font-size: 1.5rem;
  }
}
</style>