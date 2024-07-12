import PyPDF2
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

import os
import openai

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# Configuration for the language model
llm_config = {"model": "gpt-4o"}

# Define the agents
scope_agent = autogen.AssistantAgent(
    name="Scope and Change Management Risks Agent",
    llm_config=llm_config,
    system_message="""Scope and Change Management Risks Agent. Analyze the contract for risks related to scope clarity, change order procedures, and scope creep. Provide detailed findings based on your analysis.""",
)

manager_agent = autogen.AssistantAgent(
    name="Contract Analysis Manager",
    llm_config=llm_config,
    system_message="""Contract Analysis Manager. Coordinate the analysis of the contract by multiple agents, each focusing on a specific dimension of risk. Summarize the findings and provide a comprehensive risk analysis report.""",
)

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="What are the risks in the contract?",
    code_execution_config=False,
    human_input_mode= "NEVER"
)

groupchat = GroupChat(
    agents=[user_proxy, scope_agent, manager_agent],
    messages=[],
    max_round=5,
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

def extract_text_from_pdf(pdf_file):
    pdf_text = ""
    with open(pdf_file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            pdf_text += page.extract_text()
    return pdf_text

def analyze_contract_with_agents(pdf_text):
    context_message = {
        "role": "Admin",
        "content": f"Analyze the following contract for various risks:\n\n{pdf_text}"
    }
    print("Context message prepared for analysis.")
    manager.groupchat.messages.append(context_message)
    print("Context message added to group chat.")

# def analyze_contract_with_agents(pdf_text):
#    context_message = f"Analyze the following contract for various risks:\n\n{pdf_text}"
#    print("Context message prepared for analysis.")
#    manager.groupchat.messages.append({"role": "Admin", "content": context_message})
#    print("Context message added to group chat.")

    try:
        manager.initiate_chat(user_proxy, message=context_message)
        print("Chat initiated successfully.")
        #manager.run_chat()
    except Exception as e:
        print(f"An error occurred while initiating chat: {e}")

    conversation = manager.groupchat.messages
    print("Conversation collected after chat initiation.")
    return conversation

if __name__ == "__main__":
    pdf_file_path = '/Users/yoginishanth/Documents/Python/DatabaseAgent/data/sample.pdf'  # Update this to your actual PDF file path

    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_file_path)
    print("Extracted text from PDF:\n", text[:1000], "...")  # Print first 1000 characters for verification

    # Analyze the contract with agents
    analysis_result = analyze_contract_with_agents(text)
    print("Analysis result:")
    for message in analysis_result:
        print(f"{message['role']}: {message['content']}")
