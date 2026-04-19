<template>
  <div class="patients-page">
    <!-- Header -->
    <header class="page-header">
      <h1>Patient Management</h1>
      <p>Manage and view all patient accounts</p>
    </header>

    <!-- Alert Message -->
    <div v-if="message" :class="'alert alert-' + category" role="alert">
      {{ message }}
    </div>

    <!-- Controls -->
    <div class="controls-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="Search by name, email, contact, age, address..."
        />
      </div>
      <button @click="fetchPatients" class="refresh-btn">
        🔄 Refresh
      </button>
    </div>

    <!-- Patients Table -->
    <div class="patients-table-container">
      <div class="table-responsive">
        <table class="patients-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Email</th>
              <th>Full Name</th>
              <th>Age</th>
              <th>Contact</th>
              <th>Address</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="patient in filteredPatients" :key="patient.id">
              <td class="patient-id">{{ patient.id }}</td>
              <td class="patient-email">{{ patient.username || 'N/A' }}</td>
              <td class="patient-name">{{ patient.profile?.full_name || "N/A" }}</td>
              <td class="patient-age">{{ patient.profile?.age || "-" }}</td>
              <td class="patient-contact">{{ patient.profile?.contact || "-" }}</td>
              <td class="patient-address">{{ patient.profile?.address || "-" }}</td>
              
              <td class="patient-status">
                <span :class="'status-badge ' + (patient.blocked ? 'blocked' : 'active')">
                  {{ patient.blocked ? "Blocked" : "Active" }}
                </span>
              </td>

              <td class="patient-actions">
                <div class="action-buttons">
                  <button
                    class="btn btn-view"
                    @click="$router.push('/admin/patient/' + patient.id)"
                  >
                    View Details
                  </button>
                  <button
                    @click="toggleBlock(patient)"
                    :class="patient.blocked ? 'btn btn-unblock' : 'btn btn-block'"
                  >
                    {{ patient.blocked ? "Unblock" : "Block" }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- Empty State -->
        <div v-if="filteredPatients.length === 0" class="empty-state">
          <div class="empty-icon">👥</div>
          <h3>No Patients Found</h3>
          <p v-if="searchQuery">No patients match your search criteria.</p>
          <p v-else>No patients are currently registered in the system.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminPatients",

  data() {
    return {
      patients: [],
      message: null,
      category: null,
      searchQuery: "",
      loading: false
    };
  },

  computed: {
    filteredPatients() {
      const q = this.searchQuery.toLowerCase().trim();
      if (!q) return this.patients;

      return this.patients.filter(p => {
        const searchableFields = [
          p.username || '',
          p.profile?.full_name || '',
          p.profile?.contact || '',
          p.profile?.address || '',
          p.profile?.age ? String(p.profile.age) : ''
        ];

        return searchableFields.some(field => 
          field.toLowerCase().includes(q)
        );
      });
    }
  },

  mounted() {
    this.fetchPatients();
  },

  methods: {
    async fetchPatients() {
      if (this.loading) return;
      
      this.loading = true;
      this.message = null;

      try {
        const res = await fetch(`http://127.0.0.1:5000/admin/patients`, {
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        if (res.ok) {
          const data = await res.json();

          // Load profiles for each patient with error handling
          const patientsWithProfiles = await Promise.all(
            data.map(async (u) => {
              try {
                const profileRes = await fetch(
                  `http://127.0.0.1:5000/admin/patient/${u.id}`,
                  {
                    headers: {
                      Authorization: "Bearer " + localStorage.getItem("token")
                    }
                  }
                );

                let profile = null;
                let blocked = u.blocked || false;

                if (profileRes.ok) {
                  const details = await profileRes.json();
                  profile = details.profile || null;
                  blocked = details.blocked || blocked;
                }

                return { 
                  ...u, 
                  profile, 
                  blocked 
                };
              } catch (error) {
                console.error(`Error loading profile for patient ${u.id}:`, error);
                return { 
                  ...u, 
                  profile: null, 
                  blocked: u.blocked || false 
                };
              }
            })
          );

          this.patients = patientsWithProfiles;
          this.message = `Loaded ${patientsWithProfiles.length} patients successfully`;
          this.category = "success";

        } else {
          const err = await res.json().catch(() => ({ message: "Failed to fetch patients" }));
          this.message = err.message || "Failed to fetch patients";
          this.category = "danger";
        }

      } catch (error) {
        console.error("Fetch patients error:", error);
        this.message = "An unexpected error occurred while loading patients.";
        this.category = "danger";
      } finally {
        this.loading = false;
      }
    },

    async toggleBlock(patient) {
      const action = patient.blocked ? "unblock" : "block";

      try {
        const res = await fetch(
          `http://127.0.0.1:5000/admin/block_user/${patient.id}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + localStorage.getItem("token")
            },
            body: JSON.stringify({ action })
          }
        );

        if (res.ok) {
          patient.blocked = !patient.blocked;
          this.message = `Patient ${action}ed successfully`;
          this.category = "success";
          
          // Auto-clear success message after 3 seconds
          setTimeout(() => {
            if (this.message === `Patient ${action}ed successfully`) {
              this.message = null;
            }
          }, 3000);
        } else {
          const err = await res.json().catch(() => ({ message: "Failed to update block status" }));
          this.message = err.message || "Failed to update block status.";
          this.category = "danger";
        }

      } catch (error) {
        console.error("Toggle block error:", error);
        this.message = "Error updating block status.";
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

.patients-page {
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

/* Controls Section */
.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  gap: 15px;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 300px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  background-color: white;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.refresh-btn {
  background: #6c757d;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.refresh-btn:hover {
  background: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Patients Table */
.patients-table-container {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.table-responsive {
  overflow-x: auto;
}

.patients-table {
  width: 100%;
  border-collapse: collapse;
}

.patients-table th {
  background-color: #f1f8ff;
  color: #2c3e50;
  font-weight: 600;
  text-align: left;
  padding: 15px 12px;
  border-bottom: 2px solid #3498db;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.patients-table td {
  padding: 15px 12px;
  border-bottom: 1px solid #eaeaea;
  font-size: 0.95rem;
}

.patients-table tr:hover {
  background-color: #f8f9fa;
}

/* Table Cell Styles */
.patient-id {
  color: #7f8c8d;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.patient-email {
  color: #3498db;
  font-weight: 500;
}

.patient-name {
  color: #2c3e50;
  font-weight: 600;
}

.patient-age,
.patient-contact {
  color: #5a6c7d;
  text-align: center;
}

.patient-address {
  color: #5a6c7d;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Status Badge */
.status-badge {
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.blocked {
  background-color: #f8d7da;
  color: #721c24;
}

/* Action Buttons */
.patient-actions {
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

.btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.btn-view {
  background-color: #17a2b8;
  color: white;
}

.btn-block {
  background-color: #dc3545;
  color: white;
}

.btn-unblock {
  background-color: #28a745;
  color: white;
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

/* Responsive Design */
@media (max-width: 768px) {
  .patients-page {
    padding: 15px;
  }
  
  .controls-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .patients-table-container {
    padding: 15px;
  }
  
  .patients-table th,
  .patients-table td {
    padding: 10px 8px;
    font-size: 0.85rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 5px;
  }
  
  .btn {
    padding: 6px 12px;
    font-size: 0.8rem;
  }
  
  .page-header h1 {
    font-size: 1.8rem;
  }
}

@media (max-width: 480px) {
  .patients-table {
    font-size: 0.8rem;
  }
  
  .patients-table th,
  .patients-table td {
    padding: 8px 6px;
  }
  
  .status-badge {
    font-size: 0.7rem;
    padding: 4px 8px;
  }
}
</style>