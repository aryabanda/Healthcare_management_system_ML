<template>
  <div class="doctors-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Manage Doctors</h1>
      <p>Add, edit, and manage doctor accounts</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Add Doctor Card -->
    <div class="add-doctor-card">
      <h2>Add New Doctor</h2>
      <form @submit.prevent="addDoctor" class="doctor-form">
        <div class="form-row">
          <div class="form-group">
            <label>Doctor Email</label>
            <input
              v-model="newDoctor.username"
              type="email"
              class="form-input"
              placeholder="Enter doctor email"
              required
            />
          </div>

          <div class="form-group">
            <label>Password</label>
            <input
              v-model="newDoctor.password"
              type="password"
              class="form-input"
              placeholder="changeme123"
            />
          </div>

          <div class="form-group">
            <label>Department</label>
            <select
              v-model="newDoctor.specialization_id"
              class="form-select"
              required
            >
              <option disabled value="">Select Department</option>
              <option
                v-for="dept in departments"
                :key="dept.id"
                :value="dept.id"
              >
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Experience</label>
            <input
              v-model="newDoctor.experience"
              type="text"
              class="form-input"
              placeholder="e.g., 5 years"
            />
          </div>

          <div class="form-group">
            <button type="submit" class="submit-btn">Add Doctor</button>
          </div>
        </div>
      </form>
    </div>

    <!-- Search -->
    <div class="search-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search by name, email, department, experience..."
        />
      </div>
    </div>

    <!-- Doctor List -->
    <div class="doctors-list-section">
      <h2>All Doctors</h2>
      
      <div class="doctors-grid">
        <div class="doctor-card" v-for="doc in filteredDoctors" :key="doc.id">
          <div class="doctor-header">
            <div class="doctor-info">
              <h3 class="doctor-name">{{ doc.username }}</h3>
              <div class="doctor-meta">
                <span class="doctor-id">ID: {{ doc.id }}</span>
                <span class="doctor-dept">{{ doc.specialization_name || "—" }}</span>
              </div>
            </div>
            <div class="status-badges">
              <span class="status-badge" :class="doc.approve ? 'approved' : 'pending'">
                {{ doc.approve ? "Approved" : "Pending" }}
              </span>
              <span class="status-badge" :class="doc.blocked ? 'blocked' : 'active'">
                {{ doc.blocked ? "Blocked" : "Active" }}
              </span>
            </div>
          </div>

          <div class="doctor-details">
            <div class="detail-item">
              <span class="detail-label">Experience:</span>
              <span class="detail-value">{{ doc.experience || "—" }}</span>
            </div>
          </div>

          <div class="doctor-actions">
            <div class="action-group">
              <button
                class="btn btn-edit"
                @click="editProfile(doc.id)"
              >
                Edit Profile
              </button>
              <button
                class="btn btn-delete"
                @click="deleteDoctor(doc.id)"
              >
                Delete
              </button>
            </div>
            <div class="action-group">
              <button
                :class="doc.blocked ? 'btn btn-unblock' : 'btn btn-block'"
                @click="toggleBlock(doc)"
              >
                {{ doc.blocked ? "Unblock" : "Block" }}
              </button>
            </div>
          </div>
        </div>

        <div v-if="filteredDoctors.length === 0" class="empty-state">
          <p>No doctors found matching your search.</p>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div class="modal" :class="{ 'active': editingProfile }">
      <div class="modal-overlay" @click="editingProfile = false"></div>
      <div class="modal-content">
        <div class="modal-header">
          <h3>Edit Doctor Profile (ID: {{ selectedDoctorId }})</h3>
          <button class="modal-close" @click="editingProfile = false">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Specialization</label>
            <select v-model="profileForm.specialization_id" class="form-select">
              <option disabled value="">Select Department</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label">Experience</label>
            <input v-model="profileForm.experience" type="text" class="form-input" />
          </div>

          <div class="form-group">
            <label class="form-label">Availability (JSON)</label>
            <textarea v-model="profileForm.availability" class="form-textarea" rows="4"></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="editingProfile = false">
            Cancel
          </button>
          <button class="btn btn-primary" @click="saveProfile">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminManageDoctors",

  data() {
    return {
      message: null,
      category: null,

      doctors: [],
      departments: [],
      searchQuery: "",
      newDoctor: {
        username: "",
        password: "",
        specialization_id: "",
        experience: "",
        approve: true
      },

      editingProfile: false,
      selectedDoctorId: null,

      profileForm: {
        specialization_id: "",
        experience: "",
        availability: ""
      }
    };
  },

  computed: {
    filteredDoctors() {
      const q = this.searchQuery.toLowerCase().trim();
      if (!q) return this.doctors;

      return this.doctors.filter(d => {
        return (
          (d.username && d.username.toLowerCase().includes(q)) ||
          (d.specialization_name && d.specialization_name.toLowerCase().includes(q)) ||
          (d.experience && d.experience.toLowerCase().includes(q))
        );
      });
    }
  },

  mounted() {
    this.fetchDepartments();
    this.fetchDoctors();
  },

  methods: {
    // -------------------------------------------------------
    // LOAD DEPARTMENTS
    // -------------------------------------------------------
    async fetchDepartments() {
      const res = await fetch("http://127.0.0.1:5000/departments", {
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
      });
      if (res.ok) this.departments = await res.json();
    },

    // -------------------------------------------------------
    // LOAD DOCTORS
    // -------------------------------------------------------
    async fetchDoctors() {
      const res = await fetch("http://127.0.0.1:5000/admin/doctors", {
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
      });
      if (res.ok) this.doctors = await res.json();
    },

    // -------------------------------------------------------
    // ADD DOCTOR
    // -------------------------------------------------------
    async addDoctor() {
      const res = await fetch("http://127.0.0.1:5000/admin/doctors", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify(this.newDoctor)
      });

      const data = await res.json();
      this.message = data.message;
      this.category = res.ok ? "success" : "danger";

      if (res.ok) {
        this.fetchDoctors();
        this.newDoctor = {
          username: "",
          password: "",
          specialization_id: "",
          experience: "",
          approve: true
        };
      }
    },

    // -------------------------------------------------------
    // EDIT PROFILE
    // -------------------------------------------------------
    async editProfile(id) {
      this.selectedDoctorId = id;
      this.editingProfile = true;

      const res = await fetch(`http://127.0.0.1:5000/admin/doctors/${id}`, {
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
      });

      if (res.ok) {
        const data = await res.json();
        this.profileForm =
          data.profile || {
            specialization_id: "",
            experience: "",
            availability: ""
          };
      }
    },

    // -------------------------------------------------------
    // SAVE PROFILE
    // -------------------------------------------------------
    async saveProfile() {
      const res = await fetch(
        `http://127.0.0.1:5000/admin/doctors/${this.selectedDoctorId}/profile`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify(this.profileForm)
        }
      );

      const data = await res.json();
      this.message = data.message;
      this.category = res.ok ? "success" : "danger";

      this.editingProfile = false;
      this.fetchDoctors();
    },

    // -------------------------------------------------------
    // DELETE DOCTOR
    // -------------------------------------------------------
    async deleteDoctor(id) {
      if (!confirm("Are you sure you want to delete this doctor?")) return;

      const res = await fetch(`http://127.0.0.1:5000/admin/doctors/${id}`, {
        method: "DELETE",
        headers: { Authorization: "Bearer " + localStorage.getItem("token") }
      });

      const data = await res.json();
      this.message = data.message;
      this.category = res.ok ? "success" : "danger";

      this.fetchDoctors();
    },

    // -------------------------------------------------------
    // BLOCK / UNBLOCK DOCTOR
    // -------------------------------------------------------
    async toggleBlock(doc) {
      const action = doc.blocked ? "unblock" : "block";

      const res = await fetch(
        `http://127.0.0.1:5000/admin/block_user/${doc.id}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify({ action })
        }
      );

      const data = await res.json();

      if (res.ok) {
        doc.blocked = !doc.blocked;
        this.message = `Doctor ${action}ed successfully`;
        this.category = "success";
      } else {
        this.message = data.message || "Failed to update block status";
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

.doctors-page {
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
  margin-bottom: 30px;
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

/* Add Doctor Card */
.add-doctor-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.add-doctor-card h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* Form Styles */
.doctor-form {
  width: 100%;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.form-input,
.form-select,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.submit-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  height: 42px;
}

.submit-btn:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Search Section */
.search-section {
  margin-bottom: 25px;
}

.search-box {
  max-width: 600px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  background-color: white;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* Doctors List Section */
.doctors-list-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.doctors-list-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* Doctors Grid */
.doctors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.doctor-card {
  border: 1px solid #eaeaea;
  border-radius: 10px;
  padding: 20px;
  background: white;
  transition: all 0.3s ease;
}

.doctor-card:hover {
  border-color: #3498db;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.doctor-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.doctor-info {
  flex: 1;
}

.doctor-name {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 5px;
}

.doctor-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doctor-id {
  color: #7f8c8d;
  font-size: 0.85rem;
}

.doctor-dept {
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 500;
}

/* Status Badges */
.status-badges {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}

.status-badge.approved {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.active {
  background-color: #d1ecf1;
  color: #0c5460;
}

.status-badge.blocked {
  background-color: #f8d7da;
  color: #721c24;
}

/* Doctor Details */
.doctor-details {
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-label {
  font-weight: 600;
  color: #5a6c7d;
  font-size: 0.9rem;
}

.detail-value {
  color: #2c3e50;
  font-size: 0.9rem;
}

/* Doctor Actions */
.doctor-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.action-group {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn-edit {
  background-color: #007bff;
  color: white;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-block {
  background-color: #ffc107;
  color: #212529;
}

.btn-unblock {
  background-color: #28a745;
  color: white;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

/* Empty State */
.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

/* Modal */
.modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
}

.modal.active {
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: relative;
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h3 {
  color: #2c3e50;
  margin: 0;
  font-size: 1.3rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
}

.modal-close:hover {
  color: #2c3e50;
}

.modal-body {
  padding: 25px;
}

.modal-footer {
  padding: 20px 25px;
  border-top: 1px solid #eaeaea;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .doctors-page {
    padding: 15px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .doctors-grid {
    grid-template-columns: 1fr;
  }
  
  .doctor-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .status-badges {
    flex-direction: row;
    align-self: flex-start;
  }
  
  .doctor-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .action-group {
    justify-content: space-between;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .add-doctor-card,
  .doctors-list-section {
    padding: 20px;
  }
}
</style>