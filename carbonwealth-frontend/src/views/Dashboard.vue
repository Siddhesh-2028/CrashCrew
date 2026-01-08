<template>
  <div class="page">
    <div class="card">
      <h2>Dashboard</h2>

      <div v-if="loading">Loading...</div>

      <div v-else>
        <div v-if="redirect">
          <p>{{ message }}</p>
          <button @click="$router.push('/profile')">Go to Profile Setup</button>
        </div>

        <div v-else>
          <h3>Current Goal</h3>
          <div v-if="current_goal">
            <p>Plan: {{ current_goal.plan_type }}</p>
            <p>Target: {{ current_goal.target_amount }}</p>
            <p>Monthly: {{ current_goal.monthly_target }}</p>
          </div>

          <div style="margin-top:12px">
            <label>Set a monthly goal (₹)</label>
            <input v-model.number="goalAmount" type="number" />
            <button @click="saveGoal">Save Goal</button>
          </div>
      
          <div v-if="messageText" style="margin-top:12px;color:green">{{ messageText }}</div>
          <div v-if="errorText" style="margin-top:12px;color:red">{{ errorText }}</div>

          <div v-if="recommendations.length" style="margin-top:16px">
            <h4>Recommended actions to reach your goal</h4>
            <div v-for="r in recommendations" :key="r.id" style="margin-bottom:8px">
              <div>
                <strong>{{ r.action_name }}</strong>
                <div>Category: {{ r.category }} | ₹{{ r.monthly_savings }} / month | CO₂ {{ r.co2_saved_per_month }} kg</div>
              </div>
            </div>

            <div style="margin-top:12px">
              <strong>Total estimated monthly savings:</strong> ₹{{ totalEstimatedSavings }}
            </div>
            <div>
              <strong>Remaining gap to target:</strong> ₹{{ remainingGap > 0 ? remainingGap : 0 }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../services/api";

export default {
  data() {
    return {
      loading: true,
      redirect: false,
      message: null,
      current_goal: null,
      goalAmount: 500,
      recommendations: [],
      messageText: '',
      errorText: '',
    };
  },
  computed: {
    // total estimated monthly savings from selected recommended actions
    totalEstimatedSavings() {
      if (!this.recommendations || !this.recommendations.length) return 0;
      return this.recommendations.reduce((sum, r) => {
        const ms = r && r.monthly_savings ? Number(r.monthly_savings) : 0;
        return sum + (isNaN(ms) ? 0 : ms);
      }, 0);
    },

    // determine which monthly target to compare against
    effectiveTarget() {
      if (this.current_goal && this.current_goal.monthly_target) return Number(this.current_goal.monthly_target);
      return Number(this.goalAmount || 0);
    },

    remainingGap() {
      return this.effectiveTarget - this.totalEstimatedSavings;
    },

    isGoalValid() {
      return Number.isInteger(Number(this.goalAmount)) && Number(this.goalAmount) > 0;
    }
  },
  async mounted() {
    try {
      const res = await api.get('/dashboard/overview');
      const data = res.data;
      if (data.redirect === 'profile_setup') {
        this.redirect = true;
        this.message = data.message;
      } else if (data.current_goal) {
        this.current_goal = data.current_goal;
      }
    } catch (err) {
      console.error(err);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    async saveGoal() {
      try {
        // client-side validation
        if (!this.isGoalValid) {
          this.errorText = 'Enter a valid positive integer goal amount';
          this.messageText = '';
          return;
        }

        const payload = { plan_type: 'monthly', target_amount: Number(this.goalAmount) };
        const res = await api.post('/dashboard/goal', payload);
        // load recommendations returned from backend
        this.recommendations = res.data.recommendations || [];
        this.messageText = res.data.message || 'Goal saved';
        this.errorText = '';
        // refresh current goal
        const ov = await api.get('/dashboard/overview');
        if (ov.data.current_goal) this.current_goal = ov.data.current_goal;
      } catch (err) {
        console.error(err);
        this.errorText = err.response?.data?.error || 'Failed to save goal';
        this.messageText = '';
      }
    },

    // no-op: recommendations are read-only now
    toggleAction() {},
  },
};
</script>

<style scoped>
.card { padding: 16px }
</style>