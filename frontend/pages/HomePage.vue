<template>
  <div class="container-fluid homepage-container">
    <div class="row min-vh-100 align-items-center">

      <!-- LEFT IMAGE -->
      <div class="col-md-6 d-none d-md-flex justify-content-center">
        <img
          src="https://img.freepik.com/free-vector/hospital-building-concept-illustration_114360-7503.jpg"
          alt="HMS Illustration"
          class="img-fluid home-image"
        />
      </div>

      <!-- RIGHT LOGIN FORM -->
      <div class="col-md-4 offset-md-1">
        <div class="card shadow-lg p-4 login-card">

          <h2 class="fw-bold text-center mb-2">Welcome to HMS</h2>
          <p class="text-center text-muted mb-3">
            Admin • Doctor • Patient Login
          </p>

          <!-- ALERT -->
          <div v-if="message" :class="'alert alert-' + category">
            {{ message }}
          </div>

          <!-- LOGIN FORM -->
          <form @submit.prevent="submitLogin">

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input
                v-model="username"
                type="email"
                class="form-control"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label">Password</label>
              <input
                v-model="password"
                type="password"
                class="form-control"
                required
              />
            </div>

            <button class="btn btn-primary w-100 btn-lg mt-2">
              Login
            </button>
          </form>

          <div class="text-center mt-3">
            <router-link to="/register">New Patient? Register Here</router-link>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script>
export default {
  name: "HomePage",

  data() {
    return {
      username: "",
      password: "",
      message: null,
      category: null
    };
  },

  methods: {
    async submitLogin() {
      this.message = null;
      this.category = null;

      try {
        const res = await fetch("http://127.0.0.1:5000/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password
          })
        });

        const data = await res.json();

        if (!res.ok) {
          this.message = data.message || "Login failed.";
          this.category = "danger";
          return;
        }

        // Save token
        localStorage.setItem("token", data.access_token);

        // Decode JWT claims
        const claims = JSON.parse(atob(data.access_token.split(".")[1]));
        const redirect = claims.redirect;

        // Redirect to correct page
        const redirectMap = {
          doctor_dashboard: "/doctor/dashboard",
          doctor_profile: "/doctor/profile",
          patient_dashboard: "/patient/dashboard",
          patient_profile: "/patient/profile",
          admin_dashboard: "/admin/dashboard"
        };

        if (redirectMap[redirect]) {
          this.$router.push(redirectMap[redirect]);
        } else {
          this.message = "Unknown redirect from server.";
          this.category = "warning";
        }

      } catch (err) {
        console.error(err);
        this.message = "Something went wrong.";
        this.category = "danger";
      }
    }
  }
};
</script>

<style scoped>
.homepage-container {
  background: #f2f7ff;
}

.home-image {
  max-width: 80%;
  border-radius: 12px;
}

.login-card {
  border-radius: 12px;
  background: white;
}
</style>
