<template>
  <div class="doctor-profile-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Doctor Profile</h1>
      <p>Your professional information and details</p>
    </header>

    <!-- Alert Messages -->
    <div v-if="messages.length" class="messages-container">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="'alert alert-' + message.category"
      >
        {{ message.text }}
      </div>
    </div>

    <!-- Profile Card -->
    <div class="profile-card">
      <div class="profile-header">
        <div class="profile-avatar">
          <span class="avatar-icon">👨‍⚕️</span>
        </div>
        <div class="profile-title">
          <h2>{{ form.username || 'Doctor' }}</h2>
          <p class="profile-subtitle">Medical Professional</p>
        </div>
      </div>

      <div class="profile-content">
        <!-- Username -->
        <div class="profile-field">
          <div class="field-label">
            <span class="field-icon">👤</span>
            Username
          </div>
          <div class="field-value">
            {{ form.username || 'Not available' }}
          </div>
        </div>

        <!-- Specialization -->
        <div class="profile-field">
          <div class="field-label">
            <span class="field-icon">🏥</span>
            Specialization
          </div>
          <div class="field-value">
            {{ specializationName(form.specialization_id) || 'Not specified' }}
          </div>
        </div>

        <!-- Experience -->
        <div class="profile-field">
          <div class="field-label">
            <span class="field-icon">📅</span>
            Experience
          </div>
          <div class="field-value">
            {{ form.experience ? form.experience + ' years' : 'Not specified' }}
          </div>
        </div>
      </div>

      <!-- Contact Admin Notice -->
      <div v-if="!form.specialization_id" class="admin-notice">
        <div class="notice-icon">ℹ️</div>
        <div class="notice-content">
          <h4>Profile Incomplete</h4>
          <p>Please contact the administrator to update your professional details and specialization.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "DoctorProfile",

  data() {
    return {
      form: {
        username: "",
        specialization_id: "",
        experience: ""
      },
      specializationOptions: [],
      messages: []
    };
  },

  mounted() {
    this.fetchProfileData();
    this.fetchSpecializations();
  },

  methods: {
    /** Fetch doctor profile **/
    async fetchProfileData() {
      this.messages = [];

      try {
        const res = await fetch(`http://127.0.0.1:5000/doctor/profile`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        const data = await res.json();

        if (res.ok) {
          if (data.message === "no profile") {
            this.messages.push({
              category: "info",
              text: "No profile found. Please contact admin to update your details."
            });
            return;
          }

          this.form.username =
            data.username || localStorage.getItem("username") || "";
          this.form.specialization_id = data.specialization_id || "";
          this.form.experience = data.experience || "";
        } else {
          this.messages.push({
            category: "danger",
            text: data.message || "Failed to load profile data."
          });
        }
      } catch (error) {
        console.error(error);
        this.messages.push({
          category: "danger",
          text: "Error loading profile information."
        });
      }
    },

    /** Fetch list of departments (specializations) **/
    async fetchSpecializations() {
      try {
        const res = await fetch(`http://127.0.0.1:5000/departments`);
        if (res.ok) {
          this.specializationOptions = await res.json();
        }
      } catch (error) {
        console.error("Error loading specializations:", error);
      }
    },

    /** Look up specialization name **/
    specializationName(id) {
      if (!id) return '';
      const spec = this.specializationOptions.find((s) => s.id === id);
      return spec ? spec.name : "Unknown";
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

.doctor-profile-page {
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

/* Messages Container */
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

.alert-info {
  background-color: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

/* Profile Card */
.profile-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
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
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2c3e50);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 25px;
}

.avatar-icon {
  font-size: 3rem;
  color: white;
}

.profile-title h2 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 5px;
}

.profile-subtitle {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin: 0;
}

/* Profile Content */
.profile-content {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.profile-field {
  display: flex;
  flex-direction: column;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #3498db;
  transition: all 0.3s ease;
}

.profile-field:hover {
  background: #f1f8ff;
  transform: translateX(5px);
}

.field-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.field-icon {
  font-size: 1.1rem;
}

.field-value {
  color: #5a6c7d;
  font-size: 1.2rem;
  font-weight: 500;
  padding: 8px 0;
}

/* Admin Notice */
.admin-notice {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 25px;
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border-radius: 12px;
  border-left: 4px solid #ffc107;
  margin-top: 30px;
}

.notice-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.notice-content h4 {
  color: #856404;
  font-size: 1.2rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.notice-content p {
  color: #856404;
  margin: 0;
  line-height: 1.5;
  font-size: 0.95rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .doctor-profile-page {
    padding: 15px;
  }
  
  .profile-card {
    padding: 30px 25px;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
  
  .profile-avatar {
    margin-right: 0;
  }
  
  .profile-title h2 {
    font-size: 1.7rem;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
  
  .admin-notice {
    flex-direction: column;
    text-align: center;
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .profile-card {
    padding: 25px 20px;
  }
  
  .profile-avatar {
    width: 80px;
    height: 80px;
  }
  
  .avatar-icon {
    font-size: 2.5rem;
  }
  
  .profile-title h2 {
    font-size: 1.5rem;
  }
  
  .field-value {
    font-size: 1.1rem;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .profile-field {
    padding: 15px;
  }
}
</style>