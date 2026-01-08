from datetime import datetime
from extensions import db

# =========================================================
# 1️⃣ USER (AUTH ONLY)
# =========================================================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("UserProfile", backref="user", uselist=False)
    goals = db.relationship("Goal", backref="user", lazy=True)


# =========================================================
# 2️⃣ USER PROFILE (Q1–Q11 STORED HERE)
# Asked ONCE during profile creation, editable later
# =========================================================
class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # ---------- Housing & Living ----------
    living_arrangement = db.Column(db.String(50))   # Apartment / House / Hostel / Shared
    pays_electricity = db.Column(db.Boolean)
    household_size = db.Column(db.String(20))        # 1, 2-3, 4-5, 5+

    # ---------- Energy Usage ----------
    uses_ac = db.Column(db.Boolean)
    appliances_used = db.Column(db.String(200))
    # stored as CSV: Refrigerator,Washing Machine,Water Heater

    # ---------- Transportation ----------
    primary_transport = db.Column(db.String(50))     # car / two-wheeler / public / walk
    owns_vehicle = db.Column(db.String(30))          # car / two-wheeler / none

    # ---------- Food ----------
    diet_type = db.Column(db.String(30))              # veg / non-veg / mixed
    eating_out_frequency = db.Column(db.String(30))   # rarely / occasionally / frequently

    # ---------- Life Stage (Optional) ----------
    life_stage = db.Column(db.String(30))             # student / working / etc

    # ---------- Sustainability Orientation ----------
    sustainability_interest = db.Column(db.String(30))  # very / somewhat / neutral / no

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# =========================================================
# 3️⃣ ACTION MASTER (STATIC FINTECH CORE)
# Maps actions → carbon → money
# =========================================================
class ActionMaster(db.Model):
    __tablename__ = "action_master"

    id = db.Column(db.Integer, primary_key=True)

    action_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    # energy, transport, housing, food, lifestyle

    co2_saved_per_month = db.Column(db.Float)         # kg CO2e
    monthly_savings = db.Column(db.Integer)           # ₹ estimated savings
    credit_value = db.Column(db.Integer)              # virtual carbon credits

    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# 4️⃣ USER ACTION PREFERENCES / SELECTIONS
# Stores what user accepts or rejects
# =========================================================
class UserActionPreference(db.Model):
    __tablename__ = "user_action_preferences"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_id = db.Column(db.Integer, db.ForeignKey("action_master.id"), nullable=False)

    selected = db.Column(db.Boolean, default=False)
    reason_skipped = db.Column(db.String(200))  # optional UX insight

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================================================
# 5️⃣ GOALS (MONTHLY / YEARLY NORMALIZED)
# =========================================================
class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    plan_type = db.Column(db.String(20))           # monthly / yearly
    target_amount = db.Column(db.Integer)          # ₹ user entered
    normalized_monthly_amount = db.Column(db.Integer)

    achieved_amount = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
