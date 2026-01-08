<template>
  <div class="page">
    <div class="card">
      <h2>Register</h2>
      <input v-model="username" placeholder="Username" />
      <input v-model="email" placeholder="Email" />
      <input v-model="password" type="password" placeholder="Password" />
      <button @click="register">Register</button>
      <div class="link" @click="$router.push('/login')">Already have an account? Login</div>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return { username: "", email: "", password: "", error: null };
  },
  methods: {
    async register() {
      try {
        const res = await api.post("/auth/register", {
          username: this.username,
          email: this.email,
          password: this.password,
        });
        // after register, navigate to profile setup
        this.$router.push({ path: "/profile", query: { user_id: res.data.user_id } });
      } catch (err) {
        this.error = err.response?.data?.error || "Registration failed";
      }
    },
  },
};
</script>

<style scoped>
.error { color: red; margin-top: 8px }
</style>