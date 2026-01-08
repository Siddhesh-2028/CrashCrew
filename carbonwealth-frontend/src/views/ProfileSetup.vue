<template>
  <div class="page">
    <div class="card">
      <h2>Profile Setup</h2>

      <label>Living arrangement</label>
      <select v-model="living_arrangement">
        <option value="Apartment">Apartment</option>
        <option value="House">House</option>
        <option value="Hostel">Hostel</option>
        <option value="Shared">Shared</option>
      </select>

      <div style="margin-top:8px">
        <label>Pays electricity</label>
        <input type="checkbox" v-model="pays_electricity" />
      </div>

      <label>Household size</label>
      <select v-model="household_size">
        <option value="1">1</option>
        <option value="2-3">2-3</option>
        <option value="4-5">4-5</option>
        <option value="5+">5+</option>
      </select>

      <div style="margin-top:8px">
        <label>Appliances used</label>
        <div>
          <label><input type="checkbox" value="Refrigerator" v-model="appliances_arr" /> Refrigerator</label>
          <label><input type="checkbox" value="Washing Machine" v-model="appliances_arr" /> Washing Machine</label>
          <label><input type="checkbox" value="Water Heater" v-model="appliances_arr" /> Water Heater</label>
        </div>
      </div>

      <div style="margin-top:8px">
        <label>Primary Transport</label>
        <select v-model="primary_transport">
          <option value="walk">Walk</option>
          <option value="two-wheeler">Two-wheeler</option>
          <option value="car">Car</option>
          <option value="public">Public Transport</option>
        </select>
      </div>

      <div style="margin-top:8px">
        <label>Diet type</label>
        <select v-model="diet_type">
          <option value="veg">Vegetarian</option>
          <option value="non-veg">Non-Vegetarian</option>
          <option value="mixed">Mixed</option>
        </select>
      </div>

      <div style="margin-top:8px">
        <label>Eating out frequency</label>
        <select v-model="eating_out_frequency">
          <option value="rarely">Rarely</option>
          <option value="occasionally">Occasionally</option>
          <option value="frequently">Frequently</option>
        </select>
      </div>

      <button @click="submit">Save profile</button>
      <div v-if="error" class="error">{{ error }}</div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      user_id: null,
      living_arrangement: "",
      pays_electricity: false,
      household_size: "",
      appliances_arr: [],
      primary_transport: "",
      diet_type: "mixed",
      eating_out_frequency: "occasionally",
      error: null,
    };
  },
  mounted() {
    // Accept user_id via query param after registration
    this.user_id = this.$route.query.user_id || null;
  },
  methods: {
    async submit() {
      try {
        const payload = {
          user_id: this.user_id,
          living_arrangement: this.living_arrangement,
          pays_electricity: this.pays_electricity,
          household_size: this.household_size,
          appliances_used: this.appliances_arr,
          primary_transport: this.primary_transport,
          owns_vehicle: (this.primary_transport === 'car' || this.primary_transport === 'two-wheeler') ? this.primary_transport : 'none',
          diet_type: this.diet_type,
          eating_out_frequency: this.eating_out_frequency,
          life_stage: "working",
          sustainability_interest: "somewhat",
        };

        await api.post("/profile/create", payload);
        this.$router.push("/dashboard");
      } catch (err) {
        this.error = err.response?.data?.error || "Save failed";
      }
    },
  },
};
</script>

<style scoped>
.error { color: red; margin-top: 8px }
</style>