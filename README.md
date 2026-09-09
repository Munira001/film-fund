# FilmFund — Film Funding Discovery Agent

> An AI-powered film funding research workspace for independent filmmakers.

FilmFund helps filmmakers discover relevant film funding opportunities using
natural-language project requirements and live web research.

Instead of manually searching across fragmented grant databases and websites,
filmmakers can describe their project and funding needs, and FilmFund searches
for relevant opportunities using the Parallel Search API.

---

## The Problem

Finding film funding can be difficult and time-consuming.

Funding opportunities are distributed across organizations, countries,
eligibility requirements, deadlines, funding amounts, genres, production
stages, and application processes.

Independent filmmakers may spend hours searching multiple websites just to
determine which opportunities are relevant to their project.

FilmFund is designed to reduce that research burden.

---

## The Solution

FilmFund turns a filmmaker's funding requirements into a targeted research
workflow.

```text
Filmmaker Requirements
        ↓
Targeted Funding Search
        ↓
Parallel Search API
        ↓
Live Web Evidence
        ↓
Opportunity Results
        ↓
Filtering & Matching
        ↓
Funding Shortlist

The goal is to help filmmakers move from:

"Where can I find funding?"

to:

"Which funding opportunities are relevant to my project?"

What Makes FilmFund Agentic

FilmFund is designed around an AI-assisted research workflow rather than a
static database of grant links.

The project includes a Google ADK agent and a live Parallel Search integration.

The research workflow can use filmmaker requirements such as:

Genre
Location
Project budget
Production stage
Experience level
Funding requirements
Project timeline
Film format

The system uses these requirements to create targeted funding searches and
retrieve live web evidence.

Evidence-first research

FilmFund is designed to avoid inventing funding information.

When a funding opportunity does not provide enough evidence for a specific
field, the application can identify the information as unavailable rather than
fabricating a value.

Important information such as funding amounts, deadlines, eligibility, and
source URLs should be based on available source evidence.

Core Features
1. Live Film Funding Discovery

Filmmakers can search for opportunities using natural language.

Example:

Documentary film funding for an independent filmmaker in Africa in 2026.

FilmFund sends the research request through the Parallel Search API and
returns relevant web results.

2. Filmmaker Profile

FilmFund can use project information to improve funding discovery.

Relevant project information includes:

Location
Career level
Genre
Project budget
Production stage
Funding needs
Project timeline
3. Funding Filters

Funding opportunities can be filtered using available criteria such as:

Genre
Location
Budget
Eligibility
Deadline
Funding information
4. Opportunity Matching

FilmFund can organize discovered opportunities around the filmmaker's
requirements and available evidence.

Potential matching signals include:

Project relevance
Genre
Location
Eligibility
Funding information
Timeline
5. Save & Compare

Filmmakers can save promising opportunities and compare selected opportunities
within the application.

6. Application Tracking

Selected opportunities can be organized into an application workflow so
filmmakers can keep track of opportunities they intend to pursue.

7. Funding Research Resources

FilmFund also provides additional research resources to help filmmakers
navigate the funding process.

Agentic Architecture

The current architecture combines a Google ADK agent with a live Parallel
Search integration.

                    FILMFUND
                       │
                       ▼
              Filmmaker Requirements
                       │
                       ▼
                Funding Search
                       │
                       ▼
              Parallel Search API
                       │
                       ▼
                 Live Evidence
                       │
                       ▼
              Opportunity Results
                       │
                       ▼
              Filtering / Matching
                       │
                       ▼
               Funding Shortlist
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
            Save    Compare   Track
Google ADK Agent

FilmFund includes a Google ADK agent in:

backend/src/filmfund_adk_agent.py

The agent is defined using Google's ADK LlmAgent and is designed to support
film funding research.

The agent has access to the FilmFund funding search tool:

search_film_funding()

The search tool connects the agent's research workflow to the Parallel Search
API.

Parallel Search Integration

Parallel Search is the live web research and evidence layer of FilmFund.

The integration is implemented in:

backend/src/parallel_api.py

The FilmFund search workflow uses Parallel to discover real funding
opportunities from the web.

The application preserves source information so that discovered opportunities
can be connected back to their original web sources.

FilmFund does not intentionally create or mock funding opportunities.

Funding Search Workflow

The core funding search function is:

search_film_funding()
Input

The search can incorporate requirements such as:

Genre
Location
Budget
Experience
Production stage
Timeline
Funding requirements
Process
User Requirements
       ↓
Targeted Search Query
       ↓
Parallel Search API
       ↓
Live Web Results
       ↓
Evidence Processing
       ↓
Funding Opportunities
Output

The backend returns structured research results containing information such
as:

Opportunity title
Source
URL
Description / excerpt
Search result identifier
Available evidence

Information that is not supported by the retrieved evidence should not be
presented as verified fact.

Error Handling

FilmFund is designed to handle imperfect research results.

Search API failure

If the live search service fails, the application reports the failure rather
than pretending that live results were retrieved.

No relevant results

The user can broaden or change their search requirements.

Incomplete information

If a source does not provide a specific piece of information, FilmFund can
identify it as unavailable rather than inventing an answer.

Suspicious information

Funding information that cannot be adequately supported by available evidence
should be treated as requiring additional verification.

Technology Stack
Frontend
React
TypeScript
Vite
Tailwind CSS
TanStack Query
Lucide React
Backend
Python
FastAPI
REST API
AI / Agent Infrastructure
Google ADK
Gemini
Parallel Search API
Data & State
Browser localStorage for selected client-side state
Backend services for live funding discovery
Project Structure
film-fund/
│
├── backend/
│   └── src/
│       ├── api_server.py
│       ├── parallel_api.py
│       ├── filmfund_adk_agent.py
│       ├── gemini_client.py
│       └── ...
│
├── frontend/
│   └── src/
│       ├── App.tsx
│       ├── components/
│       ├── lib/
│       └── ...
│
├── docs/
│   └── ARCHITECTURE.md
│
├── main.py
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
Running Locally
Prerequisites

Install:

Node.js
npm
Python 3.x

API credentials should be configured through environment variables.

Do not commit API keys or other secrets to GitHub.

Start the Backend

From the project root:

cd backend
pip install -r ..\requirements.txt

Then start the backend using the project's configured FastAPI entry point.

Start the Frontend

Open another terminal:

cd frontend
npm install
npm run dev

The Vite development server runs locally on the configured development port.

Environment Variables

API credentials should be stored in environment variables or a local .env
file.

Example:

PARALLEL_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here

Never commit real API keys to the repository.

Live Application

FilmFund — Live Demo

The deployed application provides the FilmFund funding discovery experience.

Source Code

GitHub Repository

The complete source code contains the frontend, backend, Parallel Search
integration, and Google ADK agent implementation.

Hackathon Track

FilmFund is built for the Parallel Track of the Google Cloud Agentic
Cinema hackathon.

The project demonstrates:

A functional AI-agent architecture
Google ADK integration
Gemini-based agent infrastructure
Runtime use of the Parallel Search API
Live web research
Evidence-based funding discovery
A working filmmaker-facing application

The Parallel Search API is used as the live research layer for discovering
film funding opportunities.

Current Implementation

The current FilmFund implementation focuses on:

Live film funding discovery
Parallel Search API integration
Google ADK agent implementation
Evidence-based research
Natural-language funding searches
Filmmaker project requirements
Funding opportunity filtering
Opportunity matching
Saved opportunities
Grant comparison
Application tracking
Funding research resources
Error handling for unsuccessful searches

FilmFund is being developed as a functional funding research application
rather than a static directory of grant links.

Roadmap

Future improvements include:

Continuous funding opportunity monitoring
Deadline alerts
Deeper eligibility reasoning
Project-to-grant semantic matching
Automated application preparation
Grant requirement extraction
Personalized funding strategies
Multi-source opportunity verification
Funding pipeline analytics
Why FilmFund?

FilmFund is not intended to be another database of grant links.

Its purpose is to reduce the research burden surrounding film financing by
helping filmmakers discover funding opportunities that are relevant to their
specific projects.

The long-term vision is an intelligent funding research assistant that helps
filmmakers continuously identify realistic funding paths as their projects
evolve.

**Before you replace your README, I would also check the actual repository for those claimed f
