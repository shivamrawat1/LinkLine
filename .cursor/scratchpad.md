# LinkLine: AI Agents for Participant Recruitment

---

## Hackathon Eligibility Requirements (WeaveHacks)
- [x] Code is in a public GitHub repo
- [x] Entire project built at the hackathon (no prior work)
- [x] Work is primarily our own
- [ ] Project uses W&B Weave (at least 2 lines of code)
- [x] Team present in-person for creation and demo
- [x] No team members work for sponsor orgs

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

---

## High-level Task Breakdown

### Phase 1: Core MVP Setup (Day 1 - Morning)
- [x] **Task 1.1**: Initialize project structure and dependencies
  - Success Criteria: All folders created, requirements.txt with necessary packages
- [x] **Task 1.2**: Set up SQLite database with basic schema
  - Success Criteria: Database with research_studies and participants tables
- [x] **Task 1.3**: Create basic HTML form for research input
  - Success Criteria: Form with title, description, inclusion/exclusion criteria fields
- [x] **Task 1.4**: Implement basic backend endpoint
  - Success Criteria: Flask endpoint that saves research data to database

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

---

## Project Status Board

### Current Sprint: Phase 1 - Core MVP Setup (Day 1 - Morning)
- [x] Project structure initialization
- [x] Database setup with basic schema
- [x] Basic frontend form (title, description, inclusion/exclusion criteria)
- [x] Backend API endpoint (Flask)

### Completed Tasks
- Project skeleton and initial commit complete
- Switched backend framework from FastAPI to Flask

### In Progress
*None yet*

### Blocked
*None yet*

### Timeline
- **Day 1 Morning**: Core setup and basic form (done)
- **Day 1 Afternoon**: Participant discovery with Exa
- **Day 2**: Polish and demo preparation

---

## Executor's Feedback or Assistance Requests

- Project skeleton and initial commit are complete. Ready for parallel development.
- Backend will use Flask instead of FastAPI (update requirements and boilerplate as needed).

---

## Lessons

### Technical Lessons
- Include info useful for debugging in the program output
- Read the file before you try to edit it
- If there are vulnerabilities that appear in the terminal, run npm audit before proceeding
- Always ask before using the -force git command

### Project-Specific Lessons
*To be populated during development*

---

## Next Steps

1. Update backend boilerplate and requirements for Flask
2. Push repo to GitHub if not already done
3. Assign tasks for parallel development
4. Begin implementing MVP features

---

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

---

## Success Metrics

- **Functional**: Complete workflow from research input to participant discovery
- **Demo Ready**: Working end-to-end demo that shows participant search results
- **Usability**: Simple interface that non-technical researchers can use
- **Hackathon Success**: Impressive demo that showcases AI-powered recruitment potential 