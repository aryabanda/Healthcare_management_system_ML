<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-4">
      <h3 class="text-center mb-4">Admin Login</h3>

      <div v-if="message" :class="'alert alert-' + category" role="alert">
        {{ message }}
      </div>

      <form @submit.prevent="submitLogin">
        <div class="form-group mb-3">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            class="form-control"
            placeholder="Enter admin username"
            required
          />
        </div>

        <div class="form-group mb-3">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            class="form-control"
            placeholder="Enter password"
            required
          />
        </div>

        <div class="text-center">
          <button type="submit" class="btn btn-primary w-100">Login</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: "AdminLogin",

  data() {
    return {
      username: "",
      password: "",
      message: null,
      category: null,
    };
  },

  methods: {
    async submitLogin() {
      this.message = null;
      this.category = null;

      try {
        const res = await fetch(`http://127.0.0.1:5000/admin/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: this.username,
            password: this.password,
          }),
        });

        if (res.ok) {
          const data = await res.json();
          this.$root.login("admin", data.access_token);
          this.$router.push("/admin/dashboard");
        } else {
          const err = await res.json();
          this.message = err.message || "Invalid credentials";
          this.category = err.category || "danger";
        }
      } catch (error) {
        console.error("Login error:", error);
        this.message = "An unexpected error occurred.";
        this.category = "danger";
      }
    },
  },
};
</script>

<style scoped>
/* Add any login-specific styles if needed */
</style>
