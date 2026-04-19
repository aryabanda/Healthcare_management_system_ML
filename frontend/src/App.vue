<template>
  <div id="app">
    <!-- Navbar for logged-in users -->
    <Navbar 
      v-if="isLoggedIn"
      :userRole="userRole"
      @logout="logout"
    />

    <!-- Main content -->
    <router-view />

    <!-- Floating Chatbot Button -->
    <div 
      v-if="isLoggedIn" 
      class="chatbot-fab"
      @click="toggleChat"
    >
      🤖
    </div>

    <!-- Chatbot Popup -->
    <div v-if="isLoggedIn && isChatOpen" class="chatbot-popup">
      <div class="chatbot-header">
        <span>🤖 HealthCare ChatBot</span>
        <button class="close-btn" @click="toggleChat">✖</button>
      </div>

      <div class="form">
  <input 
    v-model="symptomsInput" 
    placeholder="Type yes or no..." 
    @keyup.enter="handleSubmit"
  />
  <button @click="handleSubmit">Send</button>
</div>

      <div class="chatbox">
        <p v-for="(msg, index) in chatLog" :key="index">{{ msg }}</p>
      </div>
    </div>
  </div>
</template>


<script>
import Navbar from "./components/Navbar.vue";
import router from "./utils/router.js";
import { isLoggedIn, userRole, logout } from "@/store/auth.js";
import axios from "axios";

export default {
  name: "App",
  components: { Navbar },
  router,
  setup() {
    return {
      isLoggedIn,
      userRole,
      logout,
    };
  },
  data() {
    return {
      name: "",
      age: "",
      gender: "",
      symptomsInput: "",
      severity: 5,
      duration: 1,
      bp: "",
      cholesterol: "",
      chatLog: [],
      isChatOpen: false,
      awaitingAnswer: false
    };
  },
  methods: {

    // ---------------- Start Q&A Chat ----------------
    async startChat() {
      try {
        const res = await axios.get("http://localhost:5000/chat/start");

        if (res.data.type === "question") {
          this.chatLog.push("🤖 " + res.data.question);
          this.awaitingAnswer = true;
        }

      } catch (err) {
        console.error(err);
        this.chatLog.push("❌ Could not start chatbot.");
      }
    },

    // ---------------- Send YES / NO ----------------
    async handleSubmit() {
      if (!this.symptomsInput) {
        this.chatLog.push("❌ Please type yes or no.");
        return;
      }

      const userText = this.symptomsInput.toLowerCase();
      this.chatLog.push("You: " + userText);

      try {
        const res = await axios.post("http://localhost:5000/chat/answer", {
          answer: userText
        });

        if (res.data.type === "question") {
          this.chatLog.push("🤖 " + res.data.question);
        }

        else if (res.data.type === "result") {
          this.chatLog.push(`🤖 You may have: ${res.data.disease}`);
          this.chatLog.push(`🤖 Symptoms you confirmed: ${res.data.symptoms_present.join(", ")}`);
          this.chatLog.push(`⚠ ${res.data.advice}`);
          this.awaitingAnswer = false;
        }

      } catch (err) {
        console.error(err);
        this.chatLog.push("❌ Error communicating with chatbot.");
      }

      this.symptomsInput = "";
    },

    // ---------------- Auth ----------------
    async checkAuthentication() {
      const token = localStorage.getItem("token");
      if (!token) {
        isLoggedIn.value = false;
        userRole.value = null;
        return;
      }

      try {
        const res = await fetch(`http://127.0.0.1:5000/get-claims`, {
          headers: { Authorization: "Bearer " + token },
        });

        if (res.ok) {
          const data = await res.json();
          isLoggedIn.value = true;
          userRole.value = data.claims.role;
          localStorage.setItem("userRole", data.claims.role);
        } else {
          logout();
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        logout();
      }
    },

    // ---------------- Toggle Chat ----------------
    toggleChat() {
      this.isChatOpen = !this.isChatOpen;

      // Start chatbot when opened
      if (this.isChatOpen && this.chatLog.length === 0) {
        this.startChat();
      }
    },

  },
  watch: {
    $route: {
      immediate: true,
      handler() {
        this.checkAuthentication();
      },
    },
  },
  async mounted() {
    await this.checkAuthentication();
    const openRoutes = ["/", "/login", "/register", "/admin/login"];
    if (!this.isLoggedIn && !openRoutes.includes(this.$route.path)) {
      this.$router.replace("/login");
    }
  },
};
</script>



<style>

/* Floating Chat Button */
.chatbot-fab {
  position: fixed;
  bottom: 25px;
  right: 25px;
  width: 60px;
  height: 60px;
  background-color: #007bff;
  color: white;
  border-radius: 50%;
  font-size: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 99999;   /* 🔥 ensures it's clickable */
}


.chatbot-fab:hover {
  background-color: #0056b3;
  transform: scale(1.1);
}

/* Chatbot Popup Window */
.chatbot-popup {
  position: fixed;
  bottom: 100px;
  right: 25px;
  width: 350px;
  max-height: 550px;
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

/* Header */
.chatbot-header {
  background-color: #007bff;
  color: white;
  padding: 12px;
  font-weight: bold;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 16px;
  cursor: pointer;
}

/* Form Area */
.form {
  padding: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.form input,
.form select {
  padding: 5px;
  font-size: 13px;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.form button {
  grid-column: span 2;
  padding: 7px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.form button:hover {
  background-color: #0056b3;
}

/* Chat Box */
.chatbox {
  flex: 1;
  margin: 8px;
  border: 1px solid #ddd;
  padding: 8px;
  overflow-y: auto;
  background-color: #f9f9f9;
  border-radius: 5px;
}

.chatbox p {
  margin: 5px 0;
  padding: 5px;
  background-color: #e6e6e6;
  border-radius: 5px;
  font-size: 13px;
  white-space: pre-line;
}

/* Animation */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}


#app {
  font-family: Arial, sans-serif;
  text-align: center;
  padding: 20px;
}

.form input,
.form select {
  margin: 5px;
  padding: 5px;
  width: 200px;
}

.form button {
  padding: 5px 15px;
  margin-top: 10px;
}

.chatbox {
  margin-top: 30px;
  text-align: left;
  border: 1px solid #ccc;
  padding: 10px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  height: 400px;
  overflow-y: auto;
  background-color: #f9f9f9;
}

.chatbox p {
  margin: 5px 0;
  padding: 5px;
  background-color: #e0e0e0;
  border-radius: 5px;
  white-space: pre-line;
}

.chatbot-container h1 {
  margin-bottom: 15px;
}
</style>
