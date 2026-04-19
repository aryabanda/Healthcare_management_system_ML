<template>
  <div class="register-page">
    <div class="register-container">
      <!-- Header Section -->
      <header class="register-header">
        <div class="header-icon">🏥</div>
        <h1>Create Your Account</h1>
        <p>Join our healthcare platform and start your wellness journey</p>
      </header>

      <!-- Alert Message -->
      <div v-if="message" :class="'alert alert-' + category" role="alert">
        {{ message }}
      </div>

      <!-- Registration Form -->
      <div class="register-card">
        <form @submit.prevent="submitRegister" class="register-form">
          <!-- Personal Information Section -->
          <div class="form-section">
            <h3 class="section-title">
              <span class="section-icon">👤</span>
              Personal Information
            </h3>
            
            <div class="form-grid">
              <!-- Full Name -->
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">📝</span>
                  Full Name
                </label>
                <input
                  type="text"
                  v-model="form.full_name"
                  class="form-input"
                  placeholder="Enter your full name"
                  required
                />
              </div>

              <!-- Age -->
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🎂</span>
                  Age
                </label>
                <input
                  type="number"
                  v-model="form.age"
                  class="form-input"
                  placeholder="Enter your age"
                  min="1"
                  max="120"
                  required
                />
              </div>

              <!-- Contact -->
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">📱</span>
                  Contact Number
                </label>
                <input
                  type="tel"
                  v-model="form.contact"
                  class="form-input"
                  placeholder="Enter your mobile number"
                  required
                />
              </div>
            </div>

            <!-- Address -->
            <div class="form-group">
              <label class="form-label">
                <span class="label-icon">🏠</span>
                Address
              </label>
              <textarea
                v-model="form.address"
                rows="3"
                class="form-textarea"
                placeholder="Enter your complete address"
              ></textarea>
            </div>
          </div>

          <!-- Account Information Section -->
          <div class="form-section">
            <h3 class="section-title">
              <span class="section-icon">🔐</span>
              Account Information
            </h3>

            <div class="form-grid">
              <!-- Email -->
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">📧</span>
                  Email Address
                </label>
                <input
                  type="email"
                  v-model="form.username"
                  class="form-input"
                  placeholder="example@gmail.com"
                  required
                />
              </div>

              <!-- Password -->
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🔒</span>
                  Password
                </label>
                <input
                  type="password"
                  v-model="form.password"
                  class="form-input"
                  placeholder="Create a strong password"
                  required
                />
                <small class="form-help">Use at least 8 characters with letters and numbers</small>
              </div>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="submit" class="register-btn">
              <span class="btn-icon">✅</span>
              Create Account
            </button>
            <router-link to="/login" class="login-link">
              <span class="link-icon">←</span>
              Already have an account? Sign In
            </router-link>
          </div>
        </form>
      </div>

      <!-- Security Notice -->
      <div class="security-notice">
        <div class="notice-icon">🔒</div>
        <p>Your personal information is protected and secure. We never share your data with third parties.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RegisterPage",

  data() {
    return {
      message: null,
      category: null,

      form: {
        username: "",
        password: "",
        full_name: "",
        age: "",
        contact: "",
        address: "",
      }
    };
  },

  methods: {
    async submitRegister() {
      // Basic validation
      if (!this.form.full_name.trim() || !this.form.age || !this.form.contact || !this.form.username || !this.form.password) {
        this.message = "Please fill in all required fields.";
        this.category = "warning";
        return;
      }

      if (this.form.password.length < 6) {
        this.message = "Password should be at least 6 characters long.";
        this.category = "warning";
        return;
      }

      try {
        const res = await fetch("http://127.0.0.1:5000/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ...this.form,
            role: "patient"
          })
        });

        const data = await res.json();

        if (res.ok) {
          this.message = "Account created successfully! Redirecting to login...";
          this.category = "success";
          setTimeout(() => {
            this.$router.push("/login");
          }, 1500);
        } else {
          this.message = data.message || "Registration failed. Please try again.";
          this.category = "danger";
        }
      } catch (err) {
        console.error("Registration error:", err);
        this.message = "Network error. Please check your connection and try again.";
        this.category = "danger";
      }
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

.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-container {
  width: 100%;
  max-width: 600px;
}

/* Header */
.register-header {
  text-align: center;
  margin-bottom: 30px;
  color: white;
}

.header-icon {
  font-size: 4rem;
  margin-bottom: 15px;
}

.register-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  font-weight: 700;
}

.register-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* Alert */
.alert {
  padding: 12px 20px;
  border-radius: 8px;
  margin-bottom: 25px;
  font-weight: 500;
  text-align: center;
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

/* Register Card */
.register-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  margin-bottom: 25px;
}

/* Form Sections */
.form-section {
  margin-bottom: 35px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 25px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f1f8ff;
}

.section-icon {
  font-size: 1.2rem;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

/* Form Groups */
.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.label-icon {
  font-size: 1rem;
}

.form-input,
.form-textarea {
  padding: 14px 16px;
  border: 2px solid #eaeaea;
  border-radius: 10px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  background: white;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-help {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 6px;
}

/* Form Actions */
.form-actions {
  text-align: center;
  margin-top: 30px;
}

.register-btn {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  width: 100%;
  justify-content: center;
}

.register-btn:hover {
  background: linear-gradient(135deg, #218838, #1e9e8a);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(40, 167, 69, 0.3);
}

.login-link {
  color: #6c757d;
  text-decoration: none;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  transition: color 0.3s ease;
}

.login-link:hover {
  color: #3498db;
}

.link-icon {
  font-size: 1rem;
}

/* Security Notice */
.security-notice {
  display: flex;
  align-items: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 20px;
  border-radius: 12px;
  color: white;
  text-align: left;
}

.notice-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.security-notice p {
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.4;
}

/* Responsive Design */
@media (max-width: 768px) {
  .register-page {
    padding: 15px;
  }
  
  .register-card {
    padding: 30px 25px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .register-header h1 {
    font-size: 2rem;
  }
  
  .header-icon {
    font-size: 3rem;
  }
  
  .security-notice {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .register-card {
    padding: 25px 20px;
  }
  
  .register-header h1 {
    font-size: 1.8rem;
  }
  
  .section-title {
    font-size: 1.1rem;
  }
  
  .form-input,
  .form-textarea {
    padding: 12px 14px;
  }
  
  .register-btn {
    padding: 14px 24px;
    font-size: 1rem;
  }
}
</style>