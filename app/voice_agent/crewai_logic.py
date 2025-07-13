# app/voice_agent/crewai_logic.py

from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os


def run_crewai_response(user_input: str) -> str:
    
    load_dotenv()  # This loads variables from .env

    api_key = os.getenv('GEMINI_API_KEY')
    print(f"DEBUG: API key found: {'Yes' if api_key else 'No'}")
    print(f"DEBUG: API key length: {len(api_key) if api_key else 0}")
    print(f"DEBUG: API key starts with: {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite-preview-06-17",  # Using the specific model you requested
        google_api_key=api_key,
        temperature=0.7,
        max_tokens=1000
    )

    # Test the LLM with a simple prompt first
    print("DEBUG: Testing LLM with simple prompt...")
    try:
        simple_test = llm.invoke("Say hello in a friendly way.")
        print(f"DEBUG: Simple test successful: {simple_test}")
    except Exception as simple_error:
        print(f"DEBUG: Simple test failed: {str(simple_error)}")

    voice_agent = Agent(
        role="Research Participant Assistant",
        goal="Speak with potential participants and guide them through the study process",
        backstory=(
            "You're calling people who may be interested in joining a research study. "
            "Your job is to answer questions, sound friendly, and collect basic info if needed."
        ),
        verbose=True,
        llm=llm,
        allow_delegation=False,
        max_iter=1
    )

    task = Task(
        description=f"User said: '{user_input}'. Respond conversationally as if on a phone call.",
        expected_output="A friendly, conversational response",
        agent=voice_agent
    )

    crew = Crew(
        agents=[voice_agent],
        tasks=[task],
        verbose=True
    )

    try:
        result = crew.kickoff()
        print(f"DEBUG: Crew execution successful: {result}")
        return result
    except Exception as e:
        print(f"DEBUG: Crew execution failed with error: {str(e)}")
        print(f"DEBUG: Error type: {type(e).__name__}")
        print(f"DEBUG: Full error details: {repr(e)}")
        
        # Fallback: Use LLM directly instead of CrewAI
        print("DEBUG: Falling back to direct LLM call...")
        try:
            fallback_prompt = f"You are a friendly research assistant on a phone call. The person just said: '{user_input}'. Respond naturally and conversationally."
            fallback_response = llm.invoke(fallback_prompt)
            print(f"DEBUG: Fallback successful: {fallback_response}")
            return str(fallback_response.content)
        except Exception as fallback_error:
            print(f"DEBUG: Fallback also failed: {str(fallback_error)}")
            raise e
