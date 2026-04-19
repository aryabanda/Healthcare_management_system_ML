<template>
  <div class="customer-profile-page">
    <!-- Header -->
    <header class="page-header">
      <h1>My Profile</h1>
      <p>Manage your personal information and contact details</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Profile Section -->
    <section class="profile-section">
      <div class="profile-card">
        <div class="profile-header">
          <div class="profile-avatar">
            <span class="avatar-icon">👤</span>
          </div>
          <div class="profile-title">
            <h2>Personal Information</h2>
            <p>Update your profile details below</p>
          </div>
        </div>

        <!-- Profile Form -->
        <form @submit.prevent="handleSubmit" class="profile-form">
          <div class="form-grid">           

            <!-- Full Name -->
            <div class="form-group">
              <label for="full_name" class="form-label">
                <span class="label-icon">👤</span>
                Full Name
              </label>
              <input
                type="text"
                id="full_name"
                v-model="form.full_name"
                class="form-input"
                placeholder="Enter your full name"
                required
              />
              <small class="form-help">Your complete legal name</small>
            </div>

            <!-- Age -->
            <div class="form-group">
              <label for="age" class="form-label">
                <span class="label-icon">🎂</span>
                Age
              </label>
              <input
                type="number"
                id="age"
                v-model.number="form.age"
                class="form-input"
                min="0"
                max="120"
                placeholder="Enter your age"
                required
              />
              <small class="form-help">Age in years</small>
            </div>

            <!-- Gender -->
            <div class="form-group">
              <label for="gender" class="form-label">
                <span class="label-icon">⚧</span>
                Gender
              </label>
              <select
                id="gender"
                v-model="form.gender"
                class="form-input"
                required
              >
                <option value="Unknown">Prefer not to say</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
              <small class="form-help">Used for health risk prediction</small>
            </div>

            <!-- Address -->
            <div class="form-group full-width">
              <label for="address" class="form-label">
                <span class="label-icon">🏠</span>
                Address
              </label>
              <input
                type="text"
                id="address"
                v-model="form.address"
                class="form-input"
                placeholder="Enter your complete address"
                required
              />
              <small class="form-help">Street address, city, and state</small>
            </div>

            <!-- PIN Code -->
            <div class="form-group">
              <label for="pin_code" class="form-label">
                <span class="label-icon">📮</span>
                PIN Code
              </label>
              <input
                type="text"
                id="pin_code"
                v-model="form.pin_code"
                class="form-input"
                placeholder="Enter your PIN code"
                required
                maxlength="6"
                pattern="[0-9]{6}"
              />
              <small class="form-help">6-digit postal code</small>
            </div>
          </div>

          <!-- Form Actions -->
          <div class="form-actions">
            <button type="submit" class="save-btn">
              💾 Save Changes
            </button>
            <button type="button" class="cancel-btn" @click="fetchCustomerProfile">
              🔄 Reset
            </button>
          </div>
        </form>

        <!-- Profile Summary -->
        <div class="profile-summary">
          <h3>Profile Summary</h3>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">Account Status</span>
              <span class="summary-value active">Active</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Member Since</span>
              <span class="summary-value">{{ currentYear }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: "CustomerProfile",

  data() {
    return {
      form: {
        user_name: "",
        full_name: "",
        age: "",
        gender: "Unknown",
        address: "",
        pin_code: "",
      },
      user_id: "",
      message: "",
      category: "",
    };
  },

  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  },

  mounted() {
    this.fetchCustomerProfile();
  },

  methods: {
    /** Fetch profile from backend */
    async fetchCustomerProfile() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/patient/profile`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
        });

        if (response.ok) {
          const data = await response.json();
          this.user_id = data.user_id;
          this.form.user_name = data.username;
          this.form.full_name = data.full_name || "";
          this.form.age = data.age ?? "";
          this.form.gender = data.gender || "Unknown";
          this.form.address = data.address || "";
          this.form.pin_code = data.pin_code || "";
          
          // Clear any existing messages when data loads successfully
          this.message = "";
        } else {
          const err = await response.json();
          this.message = err.message || "Failed to load profile data.";
          this.category = err.category || "danger";
        }
      } catch (error) {
        console.error("Profile fetch error:", error);
        this.message = "An error occurred while fetching the profile data.";
        this.category = "danger";
      }
    },

    /** Submit profile update */
    async handleSubmit() {
      if (
        !this.form.full_name.trim() ||
        this.form.age === "" ||
        !this.form.gender ||
        !this.form.address.trim() ||
        !this.form.pin_code.trim()
      ) {
        this.message = "Please fill out all required fields.";
        this.category = "warning";
        return;
      }

      // Validate PIN code format (6 digits)
      const pinRegex = /^[0-9]{6}$/;
      if (!pinRegex.test(this.form.pin_code)) {
        this.message = "Please enter a valid 6-digit PIN code.";
        this.category = "warning";
        return;
      }
      if (this.form.age < 0 || this.form.age > 120) {
        this.message = "Please enter a valid age between 0 and 120.";
        this.category = "warning";
        return;
      }

      try {
        const response = await fetch(`http://127.0.0.1:5000/patient/profile`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token"),
          },
          body: JSON.stringify({
            full_name: this.form.full_name,
            age: Number(this.form.age),
            gender: this.form.gender,
            address: this.form.address,
            pin_code: this.form.pin_code,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          this.message = data.message || "Profile updated successfully!";
          this.category = data.category || "success";
          
          // Auto-clear success message after 3 seconds
          setTimeout(() => {
            if (this.category === 'success') {
              this.message = "";
            }
          }, 3000);
        } else {
          this.message = data.message || "Failed to update profile.";
          this.category = data.category || "danger";
        }
      } catch (error) {
        console.error("Profile update error:", error);
        this.message = "An unexpected error occurred while updating your profile.";
        this.category = "danger";
      }
    },
  },
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.customer-profile-page {
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

/* Profile Section */
.profile-section {
  margin-bottom: 40px;
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

/* Profile Header */
.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f1f8ff;
}

.profile-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 25px;
}

.avatar-icon {
  font-size: 2.5rem;
  color: white;
}

.profile-title h2 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin-bottom: 8px;
}

.profile-title p {
  color: #7f8c8d;
  margin: 0;
  font-size: 1rem;
}

/* Profile Form */
.profile-form {
  margin-bottom: 40px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-bottom: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
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

.form-input {
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-input.readonly {
  background-color: #f8f9fa;
  color: #6c757d;
  cursor: not-allowed;
  border-color: #e9ecef;
}

.form-help {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-top: 5px;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.save-btn {
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

.save-btn:hover {
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

/* Profile Summary */
.profile-summary {
  padding-top: 30px;
  border-top: 2px solid #f1f8ff;
}

.profile-summary h3 {
  color: #2c3e50;
  font-size: 1.3rem;
  margin-bottom: 20px;
  text-align: center;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #3498db;
}

.summary-label {
  font-weight: 600;
  color: #5a6c7d;
  font-size: 0.9rem;
}

.summary-value {
  font-weight: 600;
  color: #2c3e50;
}

.summary-value.active {
  color: #28a745;
}

/* Responsive Design */
@media (max-width: 768px) {
  .customer-profile-page {
    padding: 15px;
  }
  
  .profile-card {
    padding: 30px 25px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .profile-avatar {
    margin-right: 0;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .save-btn,
  .cancel-btn {
    justify-content: center;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .profile-card {
    padding: 25px 20px;
  }
  
  .profile-avatar {
    width: 70px;
    height: 70px;
  }
  
  .avatar-icon {
    font-size: 2rem;
  }
  
  .profile-title h2 {
    font-size: 1.5rem;
  }
  
  .summary-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}
</style>