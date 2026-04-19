<template>
  <div class="departments-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Manage Departments</h1>
      <p>Add and manage hospital departments</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category">
      {{ message }}
    </div>

    <!-- Add Department Card -->
    <div class="add-dept-card">
      <h2>Add New Department</h2>
      
      <form @submit.prevent="addDepartment" class="dept-form">
        <div class="form-group">
          <label for="deptName">Department Name</label>
          <input
            id="deptName"
            v-model="newDept.name"
            class="form-input"
            placeholder="Enter department name"
            required
          />
        </div>

        <div class="form-group">
          <label for="deptDesc">Description</label>
          <textarea
            id="deptDesc"
            v-model="newDept.description"
            class="form-textarea"
            placeholder="Enter department description (optional)"
            rows="3"
          ></textarea>
        </div>

        <button type="submit" class="submit-btn">
          Add Department
        </button>
      </form>
    </div>

    <!-- Department List -->
    <div class="dept-list-section">
      <h2>Department List</h2>
      
      <div class="dept-list">
        <div class="dept-item" v-for="dept in departments" :key="dept.id">
          <div class="dept-info">
            <div class="dept-header">
              <h3 class="dept-name">{{ dept.name }}</h3>
              <span class="dept-id">ID: {{ dept.id }}</span>
            </div>
            <p class="dept-description">{{ dept.description || "No description provided" }}</p>
          </div>
          <div class="dept-actions">
            <button
              class="delete-btn"
              @click="deleteDepartment(dept.id)"
            >
              Delete
            </button>
          </div>
        </div>
        
        <div v-if="departments.length === 0" class="empty-state">
          <p>No departments found. Add your first department above.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminDepartments",

  data() {
    return {
      departments: [],
      newDept: {
        name: "",
        description: ""
      },
      message: null,
      category: null
    };
  },

  mounted() {
    this.fetchDepartments();
  },

  methods: {
    async fetchDepartments() {
      try {
        const res = await fetch("http://127.0.0.1:5000/admin/departments", {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        if (res.ok) {
          this.departments = await res.json();
        }
      } catch (err) {
        console.error(err);
      }
    },

    async addDepartment() {
      try {
        const res = await fetch("http://127.0.0.1:5000/admin/departments", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + localStorage.getItem("token")
          },
          body: JSON.stringify(this.newDept)
        });

        const data = await res.json();
        this.message = data.message;
        this.category = res.ok ? "success" : "danger";

        if (res.ok) {
          this.newDept = { name: "", description: "" };
          this.fetchDepartments();
        }
      } catch (err) {
        console.error(err);
      }
    },

    async deleteDepartment(id) {
      if (!confirm("Are you sure you want to delete this department?")) return;

      try {
        const res = await fetch(`http://127.0.0.1:5000/admin/departments/${id}`, {
          method: "DELETE",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        const data = await res.json();
        this.message = data.message;
        this.category = res.ok ? "success" : "danger";

        if (res.ok) {
          this.fetchDepartments();
        }

      } catch (err) {
        console.error(err);
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

.departments-page {
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

/* Add Department Card */
.add-dept-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.add-dept-card h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* Form Styles */
.dept-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.form-input,
.form-textarea {
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.submit-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Department List Section */
.dept-list-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.dept-list-section h2 {
  color: #2c3e50;
  margin-bottom: 20px;
  font-size: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 10px;
}

/* Department List */
.dept-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.dept-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 20px;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.dept-item:hover {
  border-color: #3498db;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.dept-info {
  flex: 1;
}

.dept-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 8px;
}

.dept-name {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.dept-id {
  color: #7f8c8d;
  font-size: 0.9rem;
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.dept-description {
  color: #5a6c7d;
  line-height: 1.5;
  margin: 0;
}

/* Actions */
.dept-actions {
  display: flex;
  gap: 10px;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn:hover {
  background-color: #c82333;
  transform: translateY(-2px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #7f8c8d;
}

.empty-state p {
  font-size: 1.1rem;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .departments-page {
    padding: 15px;
  }
  
  .add-dept-card,
  .dept-list-section {
    padding: 20px;
  }
  
  .dept-item {
    flex-direction: column;
    gap: 15px;
  }
  
  .dept-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .dept-actions {
    align-self: flex-end;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}
</style>