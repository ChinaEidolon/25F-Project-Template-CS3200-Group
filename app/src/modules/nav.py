# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/40_About.py", label="About", icon="🧠")


#### ------------------------ Examples for Role of Gyme Member ------------------------
def MemberHomeNav():
    st.sidebar.page_link(
        "pages/00_Member_Home.py", label="Member Home", icon="👤"
    )

def WorkoutsNav():
    st.sidebar.page_link(
        "pages/01_Workouts.py", label="Log Your Workouts", icon="🏦"
    )

def ProgressNav():
    st.sidebar.page_link("pages/02_Progress.py", label="Progress Analytics Dashboard", icon="🗺️")

def MessageNav():
    st.sidebar.page_link(
        "pages/03_Messages.py", label="Message Your Trainer", icon="🏦"
    )


## ------------------------ Examples for Role of usaid_worker ------------------------

def usaidWorkerHomeNav():
    st.sidebar.page_link(
      "pages/10_Trainer_Home.py", label="Trainer Home", icon="🏠"
    )

def NgoDirectoryNav():
    st.sidebar.page_link("pages/14_NGO_Directory.py", label="NGO Directory", icon="📁")

def AddNgoNav():
    st.sidebar.page_link("pages/15_Add_NGO.py", label="Add New NGO", icon="➕")

def ApiTestNav():
    st.sidebar.page_link("pages/12_API_Test.py", label="Test the API", icon="🛜")

def PredictionNav():
    st.sidebar.page_link(
        "pages/11_Prediction.py", label="Regression Prediction", icon="📈"
    )

def ClassificationNav():
    st.sidebar.page_link(
        "pages/13_Classification.py", label="Classification Demo", icon="🌺"
    )





#### ------------------------ System Admin Role ------------------------
def AdminPageNav():
    st.sidebar.page_link("pages/20_Owner_Home.py", label="Owner Home", icon="🖥️")
    st.sidebar.page_link(
        "pages/21_ML_Model_Mgmt.py", label="ML Model Management", icon="🏢"
    )




## ------------------------ Examples for Role of Nutritionist ------------------------

def NutritionistHomeNav():
    st.sidebar.page_link(
      "pages/30_Nutritionist_Home.py", label="Nutritionist Home", icon="🏠"
    )

def MealPlansNav():
    st.sidebar.page_link(
        "pages/31_Meal_Plans.py", label="Manage Meal Plans", icon="🏦"
    )

def FoodLogsNav():
    st.sidebar.page_link(
        "pages/32_Food_Logs.py", label="View Food Logs & Nutrition", icon="🏦"
    )

def NutritionNav():
    st.sidebar.page_link(
        "pages/33_Nutrition_Analytics.py", label="Nutrition Dashboard", icon="🏦"
    )



# -------------------------------- Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/logo.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        # Show World Bank Link and Map Demo Link if the user is a political strategy advisor role.
        if st.session_state["role"] == "pol_strat_advisor":
            MemberHomeNav()
            WorkoutsNav()
            ProgressNav()
            MessageNav()

        # If the user role is usaid worker, show the Api Testing page
        if st.session_state["role"] == "usaid_worker":
            usaidWorkerHomeNav()
            NgoDirectoryNav()
            AddNgoNav()
            PredictionNav()
            ApiTestNav()
            ClassificationNav()

        # Show World Bank Link and Map Demo Link if the user is a political strategy advisor role.
        if st.session_state["role"] == "pol_strat_advisor":
            NutritionistHomeNav()
            MealPlansNav()
            FoodLogsNav()
            NutritionNav()
            

        # If the user is an administrator, give them access to the administrator pages
        if st.session_state["role"] == "administrator":
            AdminPageNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
