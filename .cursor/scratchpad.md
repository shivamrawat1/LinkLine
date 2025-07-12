# LinkLine: AI Agents for Participant Recruitment

---

## Hackathon Eligibility Requirements (WeaveHacks)
- [ ] Code is in a public GitHub repo
- [ ] Entire project built at the hackathon (no prior work)
- [ ] Work is primarily our own
- [ ] Project uses W&B Weave (at least 2 lines of code)
- [ ] Team present in-person for creation and demo
- [ ] No team members work for sponsor orgs

---

## Judging Criteria Checklist
- [ ] **Creativity:** Innovative use of agents/protocols; "wow" factor
- [ ] **Technical Implementation:** Multiple agents, high technical ability, difficulty
- [ ] **Utility/Usefulness:** Real-world impact, production potential
- [ ] **Presentation:** Clear, concise demo; open GitHub; Weave dashboards/traces included
- [ ] **Sponsor Usage:** Effective use of W&B Weave and featured agent protocols

---

## Background and Motivation

LinkLine is an AI-powered tool designed to automate participant recruitment for scientific studies. This project is being built for **WeaveHacks hackathon** with a **2-day timeline** for completion and demo.

**Key Problem**: Small teams and solo researchers struggle to find study participants without hiring dedicated recruitment staff.

**Solution**: An autonomous AI agent system that handles the entire recruitment pipeline using CrewAI, Exa search, and browser automation.

**Hackathon Constraints**: 
- 2 days to complete and demo
- Focus on core MVP functionality
- Prioritize working demo over comprehensive features

## Key Challenges and Analysis

### Technical Challenges
1. **Integration Complexity**: Coordinating multiple AI agents (SearchAgent, OutreachAgent, SchedulerAgent) using CrewAI
2. **Web Automation**: Using BrowserBase to send messages and fill forms across different platforms
3. **Search Quality**: Leveraging Exa to find relevant participants based on research criteria
4. **Data Management**: Storing and tracking research studies, participants, and outreach history in SQLite

### Business Challenges
1. **Message Personalization**: Creating compelling outreach messages that convert to appointments
2. **Platform Diversity**: Handling different contact methods (DMs, contact forms, emails)
3. **Scheduling Coordination**: Integrating with Calendly for appointment booking
4. **Success Tracking**: Measuring recruitment effectiveness and participant quality

## High-level Task Breakdown

### Phase 1: Core MVP Setup (Day 1 - Morning)
- [ ] **Task 1.1**: Initialize project structure and dependencies
  - Success Criteria: All folders created, requirements.txt with necessary packages
- [ ] **Task 1.2**: Set up SQLite database with basic schema
  - Success Criteria: Database with research_studies and participants tables
- [ ] **Task 1.3**: Create basic HTML form for research input
  - Success Criteria: Form with title, description, inclusion/exclusion criteria fields
- [ ] **Task 1.4**: Implement basic backend endpoint
  - Success Criteria: FastAPI endpoint that saves research data to database

### Phase 2: Participant Discovery (Day 1 - Afternoon)
- [ ] **Task 2.1**: Implement basic Exa integration
  - Success Criteria: Can search for participants based on research criteria
- [ ] **Task 2.2**: Create simple SearchAgent
  - Success Criteria: Agent can parse criteria and execute targeted searches
- [ ] **Task 2.3**: Display found participants in frontend
  - Success Criteria: Show list of potential participants with basic info

### Phase 3: Demo Preparation (Day 2)
- [ ] **Task 3.1**: Polish frontend UI/UX
  - Success Criteria: Clean, professional-looking interface
- [ ] **Task 3.2**: Add basic error handling
  - Success Criteria: Graceful error handling and user feedback
- [ ] **Task 3.3**: Create demo script and test flow
  - Success Criteria: Working end-to-end demo from form to participant list

### Stretch Goals (If Time Permits)
- [ ] **Stretch 1**: Basic outreach message generation
- [ ] **Stretch 2**: Simple scheduling link integration
- [ ] **Stretch 3**: Basic participant filtering/ranking

## Project Status Board

### Current Sprint: Phase 1 - Core MVP Setup (Day 1 - Morning)
- [ ] Project structure initialization
- [ ] Database setup with basic schema
- [ ] Basic frontend form (title, description, inclusion/exclusion criteria)
- [ ] Backend API endpoint

### Completed Tasks
*None yet*

### In Progress
*None yet*

### Blocked
*None yet*

### Timeline
- **Day 1 Morning**: Core setup and basic form
- **Day 1 Afternoon**: Participant discovery with Exa
- **Day 2**: Polish and demo preparation

## Executor's Feedback or Assistance Requests

*This section will be updated by the Executor during implementation*

## Lessons

### Technical Lessons
- Include info useful for debugging in the program output
- Read the file before you try to edit it
- If there are vulnerabilities that appear in the terminal, run npm audit before proceeding
- Always ask before using the -force git command

### Project-Specific Lessons
*To be populated during development*

## Next Steps

1. **Immediate (Day 1 Morning)**: Set up project structure and basic form
2. **Short-term (Day 1 Afternoon)**: Implement Exa search and participant discovery
3. **Medium-term (Day 2)**: Polish UI and prepare demo
4. **Stretch Goals**: Basic outreach and scheduling if time permits

## MVP Scope (Hackathon Focus)

**Core Features for Demo:**
- Research input form (title, description, inclusion/exclusion criteria)
- Participant discovery using Exa search
- Display of found participants
- Clean, professional UI

**Out of Scope for MVP:**
- Automated outreach/messaging
- Scheduling integration
- Payment processing
- Advanced filtering/ranking

## Success Metrics

- **Functional**: Complete workflow from research input to participant discovery
- **Demo Ready**: Working end-to-end demo that shows participant search results
- **Usability**: Simple interface that non-technical researchers can use
- **Hackathon Success**: Impressive demo that showcases AI-powered recruitment potential 