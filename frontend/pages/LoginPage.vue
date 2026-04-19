<template>
  <div class="login-container mt-5">
    <h2 class="text-center mb-3">Login</h2>

    <div v-if="message" :class="'alert alert-' + category">
      {{ message }}
    </div>

    <form @submit.prevent="loginUser">
      <div class="form-group mb-3">
        <label>Username (email)</label>
        <input v-model="form.username" class="form-control" required />
      </div>

      <div class="form-group mb-3">
        <label>Password</label>
        <input
          v-model="form.password"
          type="password"
          class="form-control"
          required
        />
      </div>

      <button class="btn btn-primary w-100" type="submit">Login</button>

      <div class="mt-3 text-center">
        <router-link to="/register">Register Patient</router-link>
      </div>
    </form>
  </div>
</template>

<script>
import { login } from "@/store/auth.js";

export default {
  name: "LoginPageView",

  data() {
    return {
      form: {
        username: "",
        password: ""
      },
      message: null,
      category: null
    };
  },

  methods: {
    async loginUser() {
      this.message = null;
      this.category = null;

      try {
        const res = await fetch(`http://127.0.0.1:5000/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.form)
        });

        const data = await res.json();

        if (!res.ok) {
          this.message = data.message || "Invalid credentials.";
          this.category = "danger";
          return;
        }

        // Save token (but ALSO update reactive store)
        const token = data.access_token;

        // Fetch claims
        const claimsRes = await fetch(`http://127.0.0.1:5000/get-claims`, {
          headers: { Authorization: "Bearer " + token }
        });

        if (!claimsRes.ok) {
          this.message = "Login successful, but unable to load profile.";
          this.category = "warning";
          return;
        }

        const claimData = await claimsRes.json();
        const redirect = claimData.claims.redirect;
        const role = claimData.claims.role;

        // Update global reactive state
        login(token, role);

        // Navigate based on backend redirect
        this.navigateUser(redirect);

      } catch (err) {
        console.error("Login error:", err);
        this.message = "An unexpected error occurred.";
        this.category = "danger";
      }
    },

    navigateUser(target) {
      const redirectMap = {
        doctor_dashboard: "/doctor/dashboard",
        doctor_profile: "/doctor/profile",
        patient_dashboard: "/patient/dashboard",
        patient_profile: "/patient/profile",
        admin_dashboard: "/admin/dashboard"
      };

      if (redirectMap[target]) {
        this.$router.push(redirectMap[target]);
      } else {
        this.message = "Unknown redirect from server.";
        this.category = "warning";
      }
    }
  }
};
</script>

<style scoped>
/* Optional styling */
</style>
