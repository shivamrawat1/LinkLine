from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

def setup_crewai_agents():
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.7
    )

    research_analyst = Agent(
        role='Research Study Analyst',
        goal='Analyze research study descriptions to understand participant requirements, study purpose, and methodology',
        backstory=(
            "You are an expert research analyst with years of experience in "
            "understanding research methodologies and participant recruitment strategies. "
            "You excel at breaking down complex research studies into clear, actionable "
            "components for participant recruitment."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    email_copywriter = Agent(
        role='Professional Email Copywriter',
        goal='Create compelling, professional recruitment emails that effectively communicate study details and encourage participation',
        backstory=(
            "You are a senior email copywriter specializing in research "
            "recruitment communications. You have a proven track record of creating "
            "emails that achieve high response rates from potential research participants. "
            "You understand how to balance professionalism with approachability and "
            "always include clear calls-to-action."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    email_editor = Agent(
        role='Email Content Editor',
        goal='Review and polish email content to ensure it meets professional standards and is ready for sending',
        backstory=(
            "You are a meticulous email editor with expertise in research "
            "communications. You ensure all emails are grammatically correct, "
            "professionally formatted, and follow best practices for participant "
            "recruitment. You have a keen eye for tone, clarity, and effectiveness."
        ),
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    return research_analyst, email_copywriter, email_editor

def compose_recruitment_email(study_description):
    if not study_description:
        raise ValueError("Study description cannot be None or empty")

    try:
        research_analyst, email_copywriter, email_editor = setup_crewai_agents()

        analyze_study_task = Task(
            description=f"""
            Analyze the following research study description and extract key information:

            Study Description: {study_description}

            Provide a detailed analysis including:
            1. Study purpose and objectives
            2. Target participant characteristics
            3. Participation requirements and time commitment
            4. Potential benefits or compensation
            5. Key selling points for recruitment
            6. Any special considerations or requirements

            Format your analysis in a clear, structured manner that can be used 
            by an email copywriter to create compelling recruitment content.
            """,
            agent=research_analyst,
            expected_output="A comprehensive analysis of the research study with all key recruitment factors identified"
        )

        create_email_task = Task(
            description="""
            Using the research study analysis provided, create a compelling and 
            professional recruitment email that:

            1. Has a clear, attention-grabbing subject line
            2. Opens with a professional greeting
            3. Clearly explains the research study and its importance
            4. Outlines what participation involves (time, activities, etc.)
            5. Mentions any compensation, benefits, or incentives
            6. Provides clear next steps for interested participants
            7. Maintains a professional yet friendly tone
            8. Includes a strong call-to-action
            9. Has a professional closing

            The email should be well-structured with proper paragraphs and formatting.
            Focus on making it compelling while maintaining ethical recruitment practices.
            """,
            agent=email_copywriter,
            context=[analyze_study_task],
            expected_output="A complete, professional recruitment email ready for review"
        )

        review_email_task = Task(
            description="""
            Review the generated recruitment email and ensure it meets the highest 
            professional standards:

            1. Check for grammatical correctness and clarity
            2. Verify the tone is appropriate for research recruitment
            3. Ensure all key study information is included
            4. Confirm the call-to-action is clear and actionable
            5. Make any necessary improvements to structure or content
            6. Ensure the email follows best practices for participant recruitment

            Provide the final, polished email that is ready to send to potential participants.
            """,
            agent=email_editor,
            context=[create_email_task],
            expected_output="A final, polished recruitment email ready for sending"
        )

        crew = Crew(
            agents=[research_analyst, email_copywriter, email_editor],
            tasks=[analyze_study_task, create_email_task, review_email_task],
            verbose=True,
            process=Process.sequential
        )

        result = crew.kickoff()
        print(f"Generated email content: {result[:100]}...")
        return result

    except Exception as e:
        print(f"Error generating email content with CrewAI: {e}")
        return f"""Subject: Invitation to Participate in Research Study

Dear Potential Participant,

We are conducting a research study and would like to invite you to participate. Your insights and experience would be valuable to our research.

Study Details:
{study_description}

What participation involves:
- Brief survey or interview (approximately 30-60 minutes)
- Your responses will be kept confidential
- You may receive compensation for your time

If you are interested in participating, please reply to this email or contact us at [researcher-email@university.edu].

Thank you for considering this opportunity.

Best regards,
Research Team"""
