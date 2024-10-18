import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from crewai_tools import WebsiteSearchTool
from crewai import Agent, Task, Crew
import asyncio


if load_dotenv('.env'):
   # for local development
   OPENAI_KEY = os.getenv('OPENAI_API_KEY')
else:
   OPENAI_KEY = st.secrets['OPENAI_API_KEY']


# Pass the API Key to the OpenAI Client
client = OpenAI(api_key=OPENAI_KEY)
# Some other code here are omitted for brevity
"""

# Load the OpenAI API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

"""

# Initialize the WebsiteSearchTool with relevant URLs
tool_websearch_cpf_service = WebsiteSearchTool("https://www.cpf.gov.sg/service")
tool_websearch_cpf_member = WebsiteSearchTool("https://www.cpf.gov.sg/member")
tool_websearch_iras = WebsiteSearchTool("https://www.iras.gov.sg/taxes")

# Agent to calculate mandatory contributions and available limits
agent_calculate_contribtions = Agent(
    role="Calculate Contributions Agent",
    goal="Calculate annual mandatory contributions based on the {user_inputs} for each accounts.",
    backstory="Based on the updated contribution rates and rules (e.g. CPF Ordinary Wage (OW) ceiling limits and CPF annual salary ceiling rules), use the {user_inputs} with user's age, ordinary/monthly and annual income to calculate the total mandatory contributions for each CPF accounts.",
    allow_delegation=False,
    verbose=True,
)

# Agent to calculate available limits
agent_calculate_limits = Agent(
    role="Calculate Limits Agent",
    goal="Calculate total available top-up limits for user based on the total annual contributions calculated.",
    backstory="Use the contribution calculated and take note of the CPF Annual Limit (voluntary top-up limit) amount stated in CPF website. The maximum amount you can voluntarily top up is the difference between the CPF Annual Limit and the mandatory CPF contributions made for the calendar year.",
    allow_delegation=False,
    verbose=True,
    max_iterations=20,  # Increase iteration limit
    max_time_limit=180,  # Increase time limit (in seconds)
    tools=[tool_websearch_cpf_service],
)

# Agent to retrieve tax relief and interest rates
agent_get_rates = Agent(
    role="Tax and Interest Rates Agent",
    goal="Retrieve the tax relief percentage and interest rates for each CPF account (OA, SA, MA). Then calculate the total tax relief and interest rate earned based on {topup_inputs}",
    backstory="Gather accurate tax relief percentage and interest rates from CPF and IRAS websites for each CPF account. Calculate how much tax is saved and how much interest is earned based on the user's top-up inputs.",
    allow_delegation=False,
    verbose=True,
    max_iterations=20,  # Increase iteration limit
    max_time_limit=120,  # Increase time limit (in seconds)
    tools=[tool_websearch_cpf_member, tool_websearch_iras],  # Add the tools for CPF and IRAS searches
)

# Agent to write output
agent_writer = Agent(
    role="Content Writer",
    goal="Reflect the output from task_calculate_limits.",
    backstory="""You're tasked with writing user-friendly content, reflecting the available top-up limits. 
                 Ensure the content is in bullet points and user-friendly format. No calculations required.""",
    allow_delegation=False, 
    verbose=True, 
)

# Task to calculate contributions 
task_calculate_contributions = Task(
    description="""\
    Based on the updated contribution rates and rules (e.g. CPF Ordinary Wage (OW) ceiling limits and CPF annual salary ceiling rules), use the {user_inputs} with user's age, ordinary/monthly and annual income to calculate the total mandatory contributions for each CPF accounts..
    Verify the ratio of contributions and the rules properly before calculation. Return total annual mandatory contributions for each OA, SA, and MA.
    """,
    expected_output="A structured output that includes only total annual mandatory contributions for each account in bullet points and a sum for all. No header required.",
    agent=agent_calculate_contribtions,
)

# Task to calculate limits
task_calculate_limits = Task(
    description="""\
    Calculate the total available top-up for user based on the mandatory contributions calculated.
    Return total available top-up amount.
    """,
    expected_output="A structured output that includes only total available top-up amount .",
    agent=agent_calculate_limits,
)

# Task to retrieve rates and calculate savings and interest
task_get_rates = Task(
    description="""\
    Retrieve the tax relief percentage and interest rates for CPF accounts (OA, SA, MA) from CPF and IRAS websites.
    Use the user-provided top-up amount and accounts in {topup_inputs} to calculate tax savings and interest earned.
    """,
    expected_output="""\
    A structured output that includes only, in currency format:
    - The calculted Total Annual Tax Savings amount
    - The calculated Annual Interest Earned amount for each account selected by user.
    - in bullet-points.
     """,
    agent=agent_get_rates,
)

# Task to write output
task_write = Task(
    description="""\
    1. Reflect the output from task_calculate_contributions and task_calculate_limits.
    2. Ensure the content is in bullet points and user-friendly format.
    3. Verify that the amounts are correctly reflected, and there are no placeholder values.
    """,
    expected_output="""\
    A structured output with:
    - A total available top-up amount.
    - Ensure the amount are correctly reflected without placeholder values.
    """,
    agent=agent_writer,
)

# Create the Crew
crew = Crew(
    agents=[agent_calculate_contribtions, agent_calculate_limits, agent_writer],  # Add both agents
    tasks=[task_calculate_contributions, task_calculate_limits, task_write],     # Add tasks for calculating limits and writing output
    verbose=True
)

# Create Contribution Crew
crew_contributions = Crew(
    agents=[agent_calculate_contribtions],  # Add both agents
    tasks=[task_calculate_contributions],     # Add tasks for calculating limits and writing output
    verbose=True
)

crew_topup = Crew(
    agents=[agent_get_rates],  # Add both agents
    tasks=[task_get_rates],     # Add tasks for calculating limits and writing output
    verbose=True
)


# <---------------------------------- Streamlit UI ---------------------------------->


# Streamlit UI
def introduction():
    st.title("CPF Contribution Calculator")
    
    st.subheader("What are CPF Top-Ups?")
    st.markdown("""
    - Voluntary contributions made to the Central Provident Fund (CPF).
    - Additional amounts beyond mandatory contributions.
    """)

    st.subheader("Eligible Accounts:")
    st.markdown("""
    - Ordinary Account (OA)
    - Special Account (SA)
    - Medisave Account (MA)
    """)

    st.subheader("Benefits:")
    st.markdown("""
    - **Higher Retirement Savings:** Increases overall CPF balance for retirement.
    - **Tax Relief:** Potential tax deductions on the amount contributed.
    - **Interest Earnings:** CPF savings earn interest (up to 5% for SA).
    - **Flexibility:** Use funds for various purposes, such as housing or healthcare.
    """)

    st.markdown("---")  # Horizontal line


# <---------------------------------- Main Function in UI ---------------------------------->

@st.cache_data
def calculate_contributions(user_inputs):
    return crew_contributions.kickoff(inputs={"user_inputs": user_inputs})

@st.cache_data
def calculate_limits(user_inputs):
    return crew.kickoff(inputs={"user_inputs": user_inputs})

async def async_calculate(user_inputs):
    # Perform both calculations
    contributions = await asyncio.to_thread(calculate_contributions, user_inputs)
    limits = await asyncio.to_thread(calculate_limits, user_inputs)
    return contributions, limits

def main_simulator():
    # Introduction
    introduction()  # Introductory information

    # User Input Section
    st.subheader("Maximize Your Financial Gains: Calculate Now!")
    st.write("Calculate your total mandatory CPF contributions and discover how much you can voluntarily top up to enhance your financial well-being!")

    # Age input first
    current_age = st.number_input("Current Age", min_value=18, step=1)

    # Income input
    ordinary_wage = st.number_input("Ordinary Wage (Monthly Income)", min_value=0.0, step=1000.0)
    annual_income = st.number_input("Annual Income", min_value=0.0, step=1000.0)

    # Collect user_inputs dictionary based on input fields
    user_inputs = {
        "current_age": current_age,
        "ordinary_wage": ordinary_wage,
        "annual_income": annual_income
    }

    # Session state to handle results and flags
    if "contribution_result" not in st.session_state:
        st.session_state.contribution_result = ""
        st.session_state.limits_result = ""
        st.session_state.calculated = False

    # Calculate mandatory contributions and available top-up limits
    if st.button("Calculate Contributions"):
        with st.spinner("Calculating your contributions & top-up limit..."):
            # Await the async calculations
            contribution_result, limits_result = asyncio.run(async_calculate(user_inputs))

        # Display results
        #st.markdown(contribution_result)
        #st.write("")
        #st.markdown(limits_result)
        
        # Store the results in session state
        st.session_state.contribution_result = contribution_result
        st.session_state.limits_result = limits_result

        # Mark that contributions are calculated
        st.session_state.calculated = True

        # Display results from the first calculation
    if st.session_state.calculated:
        st.markdown(st.session_state.contribution_result)
        st.markdown(st.session_state.limits_result)

    # Show second input section only if contributions are calculated
    if st.session_state.calculated:
        st.markdown("---")
        st.subheader("Tax Relief & Interest Calculator")

        # User selects multiple CPF accounts for top-up
        selected_accounts = st.multiselect(
            "Select CPF Accounts to Top Up:", 
            ["Ordinary Account", "Special Account", "Medisave Account"]
        )

        # Create input fields for each selected account
        topup_amounts = {}
        for account in selected_accounts:
            topup_amounts[account] = st.number_input(f"Enter Top-Up Amount for {account}", min_value=0.0, step=100.0)

        # Calculate tax savings and interest earned when user clicks 'Calculate'
        if st.button("Calculate Savings & Interest"):
            with st.spinner("Calculating your savings & interest earned..."):
                topup_inputs = [{"cpf_account": account, "topup_amount": amount} for account, amount in topup_amounts.items()]
                savings_interest_result = crew_topup.kickoff(inputs={"topup_inputs": topup_inputs})

            # Display results
            st.markdown(savings_interest_result)

    # Reset button
    if st.button("Reset"):
        st.session_state.calculated = False
        st.experimental_rerun()
