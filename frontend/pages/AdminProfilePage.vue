<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <h3 class="text-center mb-4">Admin Profile</h3>

        <div v-if="message" :class="'alert alert-' + category" role="alert">
          {{ message }}
        </div>

        <div v-if="profile">
          <table class="table table-bordered">
            <tbody>
              <tr>
                <th>Username</th>
                <td>{{ profile.username }}</td>
              </tr>

              <tr>
                <th>Role</th>
                <td>{{ profile.role }}</td>
              </tr>

              <tr>
                <th>Status</th>
                <td class="text-success">Active</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminProfile",

  data() {
    return {
      message: "",
      category: "",
      profile: null
    };
  },

  mounted() {
    this.fetchProfileData();
  },

  methods: {
    async fetchProfileData() {
      try {
        const response = await fetch(`http://127.0.0.1:5000/admin/profile`, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + localStorage.getItem("token")
          }
        });

        if (response.ok) {
          const data = await response.json();

          this.message = data.message;
          this.category = data.category;

          this.profile = {
            username: data.username,
            role: data.role
          };
        } else {
          this.message = "Failed to load admin profile";
          this.category = "danger";
        }

      } catch (error) {
        console.error("Profile fetch error:", error);
        this.message = "An error occurred while fetching profile data.";
        this.category = "danger";
      }
    }
  }
};
</script>

<style scoped>
/* Add component-specific CSS if needed */
</style>
