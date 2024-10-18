import streamlit as st
from methodology_page import main_methodology
from llm_explainer import main_explainer
from llm_topup_simulator import main_simulator
from utility import check_password  

# Check if the password is correct.  
if not check_password():  
    st.stop()


def about_us():

    st.title("About Us")
    st.write("Welcome to the CPF Policy Simplifier & Contribution Calculator — your go-to tool for understanding Central Provident Fund (CPF) policies and optimizing voluntary CPF contributions!")
    st.write("")

    # Project Scope Section
    st.subheader("Project Scope")
    st.write("""
    This project simplifies CPF policies and helps users understand how voluntary CPF top-ups can enhance their financial well-being. Through this tool, users can explore CPF regulations, calculate top-up benefits, and make more informed financial decisions.
    """)
    st.write("")

    # Objectives Section
    st.subheader("Objectives")
    st.write("""
    The objectives of this project are:
    1. Provide users with a clear understanding of CPF policies and how they apply to them.
    2. Help users gain insights on the benefits of voluntary CPF contributions, such as potential tax savings and interest earned, for improved financial planning.
    """)
    st.write("")

    # Data Sources Section
    st.subheader("Data Sources")
    st.write("""
    We rely on trusted sources to ensure the accuracy of our information:
    - [CPF Member Website](https://www.cpf.gov.sg/member)
    - [CPF Service Website](https://www.cpf.gov.sg/service)
    - [IRAS Website](https://www.iras.gov.sg/taxes)
    """)
    st.write("")

    # Features Section
    st.subheader("Features")
    st.write("""
    The project offers two primary use cases:
    
    1. **CPF Policy Simplifier**  
    This feature simplifies complex CPF policies and legal terms into easy-to-understand language. It also provides insights, allowing users to ask any questions about CPF policies and receive clear, concise responses.

    2. **CPF Contribution Calculator**  
    This calculator provides in-depth insights into voluntary CPF top-ups. Users can calculate their existing mandatory contributions, available top-up limits, and explore how top-ups to various CPF accounts can maximize their financial benefits. The tool also calculates tax savings and interest earned from top-ups, helping users make informed decisions.
    """)
    #st.write("")
    st.markdown("---")

    # Expander for the important notice
    with st.expander("IMPORTANT NOTICE"):
        st.write("""
        This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters.

        Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output.

        Always consult with qualified professionals for accurate and personalized advice.
        """)


def methodology():
    main_methodology()


def llm_simplifier():
    main_explainer()

def llm_topup_simulator():
    main_simulator()


# Sidebar for navigation
st.sidebar.title("Navigation Bar")
selection = st.sidebar.radio("Go to", ["About Us", "Methodology", "CPF Policy Simplifier", "CPF Contribution Calculator"])


# Pages mapping
pages = {
    "About Us": about_us,
    "Methodology": methodology,
    "CPF Policy Simplifier": llm_simplifier,
    "CPF Contribution Calculator": llm_topup_simulator,
}

# Run the selected page function
page = pages[selection]
page()
