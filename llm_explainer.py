import streamlit as st
import openai
import os
from dotenv import load_dotenv
from crewai_tools import WebsiteSearchTool
from crewai import Agent, Task, Crew
from langchain.tools import StructuredTool
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
import re


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

# Create a new instance of the WebsiteSearchTool
tool_websearch = WebsiteSearchTool("https://www.cpf.gov.sg/member")


# Creating Agents 
agent_planner = Agent(
    role="Content Planner",
    goal="Plan engaging and factually accurate content on {topic}",
    backstory="""You're working on planning a user-friendly explanation of CPF policies related to {topic}.
    Your goal is to break down complex information into concise and easily digestible points,
    helping users make informed decisions regarding their CPF-related inquiries.""",
    allow_delegation=True,
    verbose=True,
)

agent_researcher = Agent(
    role="Research Analyst",
    goal="Conduct in-depth research on CPF policies and their implications for {topic}",
    backstory="""You're responsible for gathering the latest trends and key details about CPF policies related to {topic}.
    You will extract relevant insights and provide the Content Planner with credible information
    from reliable sources, including the CPF website.""",
    allow_delegation=False,
    verbose=True,
)

agent_writer = Agent(
    role="Content Writer",
    goal="Write a concise and clear explanation about CPF policies related to {topic}",
    backstory="""You're tasked with writing user-friendly content that explains CPF policies in simple terms
    related to {topic}. Your writing should be structured, engaging, and include key points to facilitate understanding.
    Always ensure to incorporate user feedback for continuous improvement.""",
    allow_delegation=False, 
    verbose=True, 
)

# <---------------------------------- Creating Tasks ---------------------------------->
task_plan = Task(
    description="""\
    1. Identify the key aspects of CPF policies that users frequently inquire about regarding {topic}.
    2. Develop a clear outline that simplifies complex information into bullet points.
    3. Prioritize content based on user needs and common questions about CPF.""",
    expected_output="""\
    A structured content plan that includes key topics, concise bullet points, and a clear outline.""",
    agent=agent_planner,
)

task_research = Task(
    description="""\
    1. Research and gather detailed information on CPF policies from the official website related to {topic}.
    2. Extract relevant data, trends, and updates that can aid in simplifying CPF information.
    3. Provide insights to the Content Planner to enhance the content outline and plan.
    """,
    expected_output="""\
    A comprehensive research report summarizing the key aspects of CPF policies and their implications related to {topic}.""",
    agent=agent_researcher,
    tools=[tool_websearch],
)

task_write = Task(
    description="""\
    1. Use the content plan to craft concise explanations of CPF policies related to {topic}.
    2. Ensure information is broken down into easy-to-read bullet points for clarity.
    3. Include user-friendly summaries and actionable insights where relevant.
    4. Proofread for clarity and grammatical accuracy.""",
    expected_output="""\
    A well-structured document with clear and concise explanations of CPF policies, formatted for easy understanding related to {topic}.""",
    agent=agent_writer
)

# <---------------------------------- Creating the Crew ---------------------------------->
crew = Crew(
    agents=[agent_planner, agent_researcher, agent_writer],
    tasks=[task_plan, task_research, task_write],  # Include all tasks for a comprehensive process
    verbose=True
)

# <---------------------------------- Caching Function ---------------------------------->
@st.cache_data(show_spinner=False)  # Disable spinner for this cached function
def get_cached_crew_output(topic):
    result = crew.kickoff(inputs={"topic": topic})  # Call crew.kickoff()
    return result


# <---------------------------------- Streamlit UI ---------------------------------->

# Function to sanitize input
def sanitize_input(input_string):
    # Strip leading/trailing whitespace
    sanitized = input_string.strip()
    
    # Remove any special characters not allowed (allowing alphanumeric and spaces)
    sanitized = re.sub(r'[^\w\s]', '', sanitized)  
    print(sanitized)
    
    # Limit input length to prevent overly large prompts
    max_length = 200
    if len(sanitized) > max_length:
        st.warning(f"Input too long! Please limit to {max_length} characters.")
        return None
    
    # Validate if the input only contains letters, numbers, or spaces (no code or harmful characters)
    if not re.match("^[A-Za-z0-9\s]+$", sanitized):
        st.warning("Invalid input! Please only use letters, numbers, and spaces.")
        return None
    
    return sanitized


# Function to save feedback to a JSON file
def save_feedback(feedback, topic):
    print("Trying to save feedback")
    feedback_data = {"topic": topic, "feedback": feedback}
    try:
        with open("feedback.json", "a") as f:
            print("Trying to write into feedback file")
            json.dump(feedback_data, f)
            f.write("\n")
        return True  # Indicate success
    except Exception as e:
        st.error(f"Error saving feedback: {e}")  # Display error message in Streamlit
        return False  # Indicate failure
    

# Streamlit UI function
def main_explainer():
    st.title("CPF Policy Simplifier")

    # User input for the topic
    raw_topic = st.text_input("Ask about a CPF policy (e.g., 'What is the Ordinary Account?'): ")

    # Session state to handle results and flags
    if "generated_content" not in st.session_state:
        st.session_state.generated_content = ""

    # Button to generate content
    if st.button("Generate Content"):

        # Sanitize the input
        topic = sanitize_input(raw_topic)

        if topic.strip():  # Check if the user input is not empty
            with st.spinner("Generating content, please wait..."):
                result = get_cached_crew_output(topic)  # Run crew with caching
                st.session_state.generated_content = result  # Store result in session state

            # Display the final answer
            #st.markdown(result)
                
    # Display the final answer if it e'xists in session state
    if "generated_content" in st.session_state and st.session_state.generated_content:
        st.markdown(st.session_state.generated_content)

    # Feedback Section
    if st.session_state.generated_content:
        
        st.title("Feedback")
        
        # Feedback text area
        feedback = st.text_area("Please provide feedback on the Final Result and the Agent's actions:", 
                                key="feedback")  # Set the value from session state
        
        # Debugging: Show current feedback content
        #print("Current feedback content:", feedback)  # Print current feedback

        if st.button("Submit Feedback"):
            #st.write("Submit Feedback button clicked")  # Debugging line
            if feedback.strip():  # Check feedback directly from the local variable
                save_feedback(feedback, topic)  # Save feedback to a file
                st.success("Thank you for your feedback!")
            else:
                st.warning("Please provide feedback before submitting.")
    
    # Reset button
    if st.button("Reset"):
        st.session_state.generated_content = False
        st.experimental_rerun()