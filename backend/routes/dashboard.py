from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Goal, UserProfile, ActionMaster, UserActionPreference

DEFAULT_PER_ACTION_MAX = 500  # assumption: user won't take actions with monthly_savings > 500 by default

dashboard_bp = Blueprint("dashboard", __name__)

# ==================================================
# 1️⃣ CREATE / UPDATE SAVED GOAL (REAL GOAL)
# ==================================================
@dashboard_bp.route("/goal", methods=["POST"])
@jwt_required()
def create_or_update_goal():
    data = request.json
    user_id = get_jwt_identity()

    plan_type = data.get("plan_type")   # monthly / yearly
    target_amount = data.get("target_amount")

    if plan_type not in ["monthly", "yearly"]:
        return {"error": "Invalid plan type"}, 400

    if not isinstance(target_amount, int) or target_amount <= 0:
        return {"error": "Invalid target amount"}, 400

    # Normalize to monthly
    normalized_monthly = (
        target_amount if plan_type == "monthly" else target_amount // 12
    )

    goal = Goal.query.filter_by(user_id=user_id).first()

    if goal:
        goal.plan_type = plan_type
        goal.target_amount = target_amount
        goal.normalized_monthly_amount = normalized_monthly
    else:
        goal = Goal(
            user_id=user_id,
            plan_type=plan_type,
            target_amount=target_amount,
            normalized_monthly_amount=normalized_monthly
        )
        db.session.add(goal)

    db.session.commit()

    # Build recommendations based on user's profile
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    recs = []

    # derive relevant categories from profile if present, otherwise use broad defaults
    categories = set()
    if profile:
        if getattr(profile, 'owns_vehicle', None) and str(profile.owns_vehicle).lower() != "none":
            categories.add("transport")
        if getattr(profile, 'primary_transport', None) and str(profile.primary_transport).lower() in ["car", "two-wheeler"]:
            categories.add("transport")
        if getattr(profile, 'uses_ac', None) or getattr(profile, 'pays_electricity', None):
            categories.add("energy")
        if getattr(profile, 'diet_type', None):
            categories.add("food")
    else:
        # no profile: use general categories to recommend a useful mix
        categories.update(["transport", "energy", "food", "lifestyle", "water", "waste"])

    # always include lifestyle and water/waste as low-effort options
    categories.update(["lifestyle", "water", "waste"])

    per_action_max = min(DEFAULT_PER_ACTION_MAX, normalized_monthly)

    # allow zero-cost actions and actions under per_action_max
    query = ActionMaster.query.filter(ActionMaster.category.in_(list(categories))).filter(
        (ActionMaster.monthly_savings <= per_action_max) | (ActionMaster.monthly_savings == 0)
    )

    actions = query.order_by(ActionMaster.co2_saved_per_month.desc()).all()

    # pick top actions until we reach ~80% of monthly target or exhaust list
    target_threshold = normalized_monthly * 0.8
    cum = 0
    for a in actions:
        recs.append({
            "id": a.id,
            "action_name": a.action_name,
            "category": a.category,
            "co2_saved_per_month": a.co2_saved_per_month,
            "monthly_savings": a.monthly_savings,
        })
        # treat None or negative monthly_savings as 0 for accumulation
        try:
            ms = a.monthly_savings or 0
        except Exception:
            ms = 0
        cum += ms
        if cum >= target_threshold:
            break

    return {
        "message": "Goal saved successfully",
        "plan_type": plan_type,
        "target_amount": target_amount,
        "monthly_target": normalized_monthly,
        "recommendations": recs
    }, 200


# ==================================================
# 2️⃣ DASHBOARD OVERVIEW (ENTRY POINT)
# ==================================================
@dashboard_bp.route("/overview", methods=["GET"])
@jwt_required()
def dashboard_overview():
    user_id = get_jwt_identity()

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    goal = Goal.query.filter_by(user_id=user_id).first()

    # Profile mandatory
    if not profile:
        return {
            "redirect": "profile_setup",
            "message": "Complete profile setup to continue"
        }, 200

    # Profile done, goal not set
    if not goal:
        return {
            "redirect": "set_goal",
            "profile_ready": True,
            "goal_set": False
        }, 200

    # Profile + goal done
    return {
        "redirect": "dashboard",
        "profile_ready": True,
        "goal_set": True,
        "current_goal": {
            "plan_type": goal.plan_type,
            "target_amount": goal.target_amount,
            "monthly_target": goal.normalized_monthly_amount
        }
    }, 200



@dashboard_bp.route("/actions", methods=["POST"]) 
@jwt_required()
def save_selected_actions():
    """Save the user's selected action IDs as preferences."""
    user_id = get_jwt_identity()
    data = request.json or {}
    action_ids = data.get("action_ids", [])

    if not isinstance(action_ids, list):
        return {"error": "action_ids must be a list"}, 400

    # Remove previous preferences for user and add new ones (simple approach)
    UserActionPreference.query.filter_by(user_id=user_id).delete()

    for aid in action_ids:
        pref = UserActionPreference(user_id=user_id, action_id=aid, selected=True)
        db.session.add(pref)

    db.session.commit()

    return {"message": "Selected actions saved"}, 200


# ==================================================
# 3️⃣ ESTIMATION MODE (WHAT-IF / EXCLAMATION MODE)
# DOES NOT SAVE TO DB
# ==================================================
@dashboard_bp.route("/estimate", methods=["POST"])
@jwt_required()
def estimate_goal():
    data = request.json
    user_id = get_jwt_identity()

    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        return {"error": "Profile not completed"}, 400

    plan_type = data.get("plan_type")     # monthly / yearly
    amount = data.get("amount")

    if plan_type not in ["monthly", "yearly"]:
        return {"error": "Invalid plan type"}, 400

    if not isinstance(amount, int) or amount <= 0:
        return {"error": "Invalid amount"}, 400

    normalized_monthly = amount if plan_type == "monthly" else amount // 12

    return {
        "mode": "estimation",
        "message": "This is an estimated plan. It does not change your saved goal.",
        "plan_type": plan_type,
        "entered_amount": amount,
        "monthly_target": normalized_monthly,
        "next_step": "action_selection"
    }, 200
