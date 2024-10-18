import streamlit as st

def main_methodology():
    st.title("Methodology")
    
    # Introduction Section
    st.write("""
    Our methodology utilizes a multi-agent system combined with advanced caching and asynchronous processing to optimize responses to user queries regarding CPF policies and financial calculations. Each component of the system plays a vital role in simplifying complex information and delivering clear, accurate insights.
    """)
    
    # Process Flow Section
    st.subheader("Process Flow")
    st.write("""
    - **User Inputs**: The user provides a query or request for financial calculations.
    - **CrewAI Agents**: Agents collaborate to research, collate data, compute results, and generate responses.
    - **Caching & Async**: Information is stored for future requests, and queries are processed in parallel to improve performance.
    - **Output**: The system delivers simplified CPF policy information or detailed financial calculations tailored to the user's needs.
    """)
    st.write("")

    # Input Sanitization and Handling Section
    st.subheader("User Input Sanitization and Handling")
    st.write("""
    - Input sanitization is implemented to validate and clean user inputs, allowing only numbers in relevant fields to prevent invalid data submissions.
    - This approach enhances the reliability of calculations performed in both use cases by minimizing potential user mistakes.
    - It also safeguard the application from prompt injection attacks and manimise the chances of exploitaton.
    - In use case 2 (calculating tax savings and interest), only numerical inputs are allowed, ensuring valid financial figures and minimizing error risks.
    """)
    st.write("") 
    
    # Caching Section
    st.subheader("Data Caching")
    st.write("""
    The system uses caching to store frequently requested CPF information, improving response times for repeat queries by retrieving data from memory instead of making new requests.
    """)
    st.write("")
    
    # Asynchronous Processing Section
    st.subheader("Asynchronous Processing")
    st.write("""
    - Asynchronous processing allows the system to handle multiple user queries simultaneously without slowing down, ensuring seamless interaction even when multiple requests are made concurrently.
    - When a task involves waiting on I/O, such as searching the CPF website or waiting for responses from APIs (e.g., OpenAI), the asynchronous structure enhances the app's responsiveness to user input during those waiting periods.
    - In scenarios where operations like `crew.kickoff()` involve long-running tasks—such as fetching data from the CPF website or querying OpenAI—async processing allows other parts of the app to continue functioning while waiting for these I/O tasks to complete.
    """)
    st.write("")

    # Multi-Agent System Section
    st.subheader("Multi-Agent System")
    st.write("""
    The system is powered by CrewAI agents that collaborate to handle user queries and perform specific tasks. Based on user inputs, the agents execute the following steps:
    """)
    
    st.write("1. **Planner Agent**: Defines the structure of the response based on the type of user query (policy explanation or CPF financial calculation).")
    st.write("2. **Researcher Agent**: Gathers relevant and updated information from trusted online sources such as the CPF and IRAS websites.")
    st.write("3. **Computation Agent**: Performs any required calculations, such as CPF top-up amounts, tax savings, and interest earned based on user financial data.")
    st.write("4. **Writer Agent**: Simplifies and organizes the data or computation results into concise and easy-to-understand outputs for the user.")
    
    st.write("""
    These agents work in harmony to provide comprehensive answers, ensuring that the user receives accurate, timely, and clear information.
    """)
    st.write("")


    #------------------------- Flow Chart -----------------------#

    st.markdown("---")

    st.subheader("Flow Chart")

    st.image("explainer_chart.png", caption="Flow Chart for Use Case 1: CPF Policy Explainer", use_column_width=True)
    st.write("")
    st.write("")
    st.image("calculator_chart.png", caption="Flow Chart for Use Case 2: CPF Contribution Calculator", use_column_width=True)


