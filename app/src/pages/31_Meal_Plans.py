import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://localhost:4000"   

st.title("Nutritionist Meal Plans")


# Get active members
@st.cache_data
def get_active_members():
    try:
        r = requests.get(f"{BASE_URL}/members", params={"status": "active"})
        if r.status_code == 200:
            return r.json()
        return []
    except Exception:
        return []

members = get_active_members()
if not members:
    st.warning("No active members found or failed to load members.")
    st.stop()

# Build  label for dropdown
def format_member(m):
    return f"{m.get('first_name', '')} {m.get('last_name', '')} (ID {m.get('member_id')})"

selected_member = st.selectbox(
    "Select a member to manage meal plans for:",
    members,
    format_func=format_member
)

member_id = selected_member.get("member_id")

st.markdown(f"### Meal Plans for {format_member(selected_member)}")

# Get meal plans for member 
def load_meal_plans(member_id: int):
    try:
        r = requests.get(f"{BASE_URL}/meal-plans", params={"member_id": member_id})
        if r.status_code == 200:
            return r.json()
        else:
            st.error("Failed to load meal plans.")
            return []
    except Exception as e:
        st.error(f"Error loading meal plans: {e}")
        return []

plans = load_meal_plans(member_id)

if plans:
    df = pd.DataFrame(plans)
    st.dataframe(df)
else:
    st.info("No meal plans found for this member yet.")

st.divider()

# Create new meal plan 
st.subheader("Create New Meal Plan")

with st.form("create_meal_plan_form"):
    plan_date = st.date_input("Plan Date")
    calorie_goals = st.number_input("Daily Calorie Goal", min_value=0, value=2000)
    macro_goals = st.text_area("Macro Goals (optional, e.g., 40% carbs / 30% protein / 30% fats)")

    submitted = st.form_submit_button("Create Meal Plan")
    if submitted:
        payload = {
            "member_id": member_id,
            "calorie_goals": calorie_goals,
            "macro_goals": macro_goals if macro_goals.strip() else None,
            "plan_date": str(plan_date),
        }
        try:
            r = requests.post(f"{BASE_URL}/meal-plans", json=payload)
            if r.status_code == 201:
                st.success("Meal plan created successfully!")
                st.cache_data.clear()  # clear cached data if using caching elsewhere
            else:
                st.error(f"Failed to create meal plan. Status: {r.status_code}")
        except Exception as e:
            st.error(f"Error creating meal plan: {e}")

st.divider()

# Update / Delete existing meal plan 
if plans:
    st.subheader("Update or Delete Existing Meal Plan")
    plan_options = {f"Plan {p['plan_id']} – {p.get('plan_date')}": p for p in plans}
    plan_label = st.selectbox("Select a plan:", list(plan_options.keys()))
    selected_plan = plan_options[plan_label]

    with st.form("edit_meal_plan_form"):
        edit_calories = st.number_input(
            "Calorie Goal",
            min_value=0,
            value=selected_plan.get("calorie_goals", 0),
            key="edit_calories",
        )
        edit_macro = st.text_area(
            "Macro Goals",
            value=selected_plan.get("macro_goals", "") or "",
            key="edit_macro",
        )
        edit_date = st.date_input(
            "Plan Date",
            value=pd.to_datetime(selected_plan.get("plan_date")).date()
            if selected_plan.get("plan_date")
            else pd.Timestamp.today().date(),
            key="edit_date",
        )

        col1, col2 = st.columns(2)
        with col1:
            save_btn = st.form_submit_button("Save Changes")
        with col2:
            delete_btn = st.form_submit_button("Delete Plan")

        if save_btn:
            payload = {
                "calorie_goals": edit_calories,
                "macro_goals": edit_macro,
                "plan_date": str(edit_date),
            }
            try:
                r = requests.put(
                    f"{BASE_URL}/meal-plans/{selected_plan['plan_id']}",
                    json=payload,
                )
                if r.status_code == 200:
                    st.success("Meal plan updated successfully!")
                else:
                    st.error(f"Failed to update meal plan. Status: {r.status_code}")
            except Exception as e:
                st.error(f"Error updating meal plan: {e}")

        if delete_btn:
            try:
                r = requests.delete(
                    f"{BASE_URL}/meal-plans/{selected_plan['plan_id']}"
                )
                if r.status_code == 200:
                    st.success("Meal plan deleted.")
                else:
                    st.error(f"Failed to delete meal plan. Status: {r.status_code}")
            except Exception as e:
                st.error(f"Error deleting meal plan: {e}")