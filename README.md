# FilmFund — Film Funding Discovery Agent

> An agentic funding research workspace for independent filmmakers.

FilmFund helps independent filmmakers discover, analyze, rank, and manage film funding opportunities from a single workspace.

Instead of manually searching across fragmented grant databases and websites, a filmmaker can describe their project and funding needs in natural language. FilmFund uses an agentic research workflow to find relevant opportunities, analyze them, and surface the strongest matches.

## The Problem

Independent filmmakers often face a funding discovery problem, not simply a lack of funding.

Film grants and financing opportunities are distributed across organizations, countries, eligibility requirements, deadlines, funding amounts, and application processes.

Finding the right opportunity can require hours of manual research.

FilmFund is designed to reduce that research burden.

## The Solution

FilmFund turns a filmmaker's project requirements into a targeted funding research workflow:

```text
Filmmaker Profile
       ↓
Project Requirements
       ↓
Agentic Grant Discovery
       ↓
Opportunity Analysis
       ↓
Relevance & Match Scoring
       ↓
Ranked Opportunities
       ↓
Save / Compare / Track

The goal is to move filmmakers from:

"Where can I find funding?"

to:

"Which opportunities should I pursue next?"

What Makes FilmFund Agentic

FilmFund is designed as an agentic research workflow rather than a static grant directory.

The system can:

interpret a filmmaker's natural-language funding request
generate targeted search queries
search external funding sources
collect and normalize opportunity data
remove duplicate opportunities
analyze grant information
identify incomplete or suspicious information
evaluate opportunities against filmmaker requirements
rank relevant opportunities
apply project-specific filters
help filmmakers shortlist opportunities
organize selected opportunities into an application workflow

The agentic workflow reduces the amount of manual research required between having a film project and identifying realistic funding opportunities.

Core Features
Intelligent Grant Discovery

Filmmakers can describe what they are looking for using natural language.

Example:

Find film funding opportunities for an independent drama filmmaker
with a $50,000 project budget.

FilmFund transforms the request into a targeted research workflow and retrieves relevant opportunities.

Filmmaker Profile

FilmFund uses project information such as:

location
career level
genre
project budget
production stage
funding needs
project timeline

These signals can be used to improve opportunity matching.

Match Scoring

Funding opportunities are evaluated using available signals such as:

relevance
funding amount
eligibility
project fit
timeline

The strongest opportunities can then be surfaced first.

Grant Filtering

Opportunities can be filtered by criteria such as:

genre
location
budget
eligibility
deadline
funding amount
Save and Compare

Filmmakers can save promising opportunities and compare selected grants within the workspace.

Application Tracker

Selected opportunities can be moved into an application workflow so filmmakers can keep track of funding opportunities they intend to pursue.

Budget Calculator

The workspace includes budgeting functionality to help filmmakers understand their funding requirements and how opportunities relate to their project budget.

Research Resources

FilmFund also provides additional filmmaking and funding resources alongside discovered opportunities.

Agentic Architecture

FilmFund uses a multi-step research pipeline to transform filmmaker requirements into actionable funding opportunities.

                         FILMFUND
                            |
                            v
                  Filmmaker Requirements
                            |
                            v
                    Search Planning
                            |
                            v
                 Parallel Search API
                            |
                            v
                  Opportunity Results
                            |
                            v
                 Analyze & Normalize
                            |
                            v
                 Relevance / Matching
                            |
                            v
                   Rank Opportunities
                            |
                            v
                 Actionable Results
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
            Save         Compare       Track
1. Grant Discovery

search_grants()

Input

Filmmaker information such as:

budget
genre
experience
location
timeline
funding requirements

Action

Generates a targeted research query and uses the Parallel Search API to discover relevant opportunities.

Output

Raw funding opportunities.

2. Grant Analysis

analyze_grants()

Input

Raw opportunity results.

Action

Processes discovered opportunities, extracts important information, checks available details, identifies suspicious or incomplete information, and normalizes the results.

Output

Structured funding opportunities ready for matching.

3. Opportunity Ranking

rank_opportunities()

Input

Analyzed opportunities and filmmaker requirements.

Action

Evaluates opportunities using available relevance, funding, eligibility, and timeline signals.

Output

Ranked opportunities.

4. Producer Discovery

search_producers()

Input

Project information such as budget and genre.

Action

Searches for potentially relevant production companies and producer opportunities.

Output

Potential production matches.

5. Response Generation

build_response()

Input

Funding opportunities, producer opportunities, and other research results.

Action

Organizes the research into a clear response with actionable next steps.

Output

Prioritized opportunities for the filmmaker.

Error Handling

FilmFund is designed to handle imperfect research results.

Search API failure

The system can fall back to available fallback or cached information where supported.

No relevant results

The system can suggest broader search criteria or alternative funding paths.

Suspicious opportunity

Potentially suspicious opportunities can be flagged for additional review rather than being presented as automatically trustworthy.

Incomplete information

Missing information is identified rather than being presented as verified.

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
Flask
REST API
Grant discovery and analysis services
AI / Agent Infrastructure
Google Gemini
Google Cloud Agent Builder / ADK components
Parallel Search API
Data & State
Browser localStorage for selected client-side state
Backend services for live opportunity discovery
Project Structure
film-fund/
├── backend/
│   └── src/
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
├── test_adk.py
├── README.md
├── LICENSE
└── .gitignore
Running Locally
Prerequisites
Node.js
npm
Python 3.x
Required API credentials configured through environment variables
Frontend
cd frontend
npm install
npm run dev
Backend

Install the Python dependencies:

pip install -r requirements.txt

Then start the backend using the project's configured entry point.

Environment variables should be provided through a local .env file or your deployment environment.

Do not commit API keys or other secrets to the repository.

Example Workflow
Create or update a filmmaker profile.
Describe the project's funding requirements.
Search for funding opportunities.
Review discovered opportunities.
Analyze relevance and eligibility.
Filter opportunities.
Compare promising opportunities.
Save the strongest matches.
Move selected opportunities into the application tracker.
Continue managing the funding pipeline from the workspace.
Hackathon Submission
Live Application

FilmFund — Live Demo

Source Code

GitHub Repository

Current Implementation

The current FilmFund implementation focuses on:

agentic funding discovery
live grant search
opportunity analysis
relevance and match scoring
filmmaker profile information
filtering
saved opportunities
grant comparison
application tracking
funding research resources
fallback handling for unsuccessful searches

The project is being developed as a functional agentic funding research platform rather than a static directory.

Roadmap

Future improvements include:

continuous funding opportunity monitoring
deadline alerts
deeper eligibility reasoning
project-to-grant semantic matching
automated application preparation
grant requirement extraction
personalized funding strategies
multi-source opportunity verification
funding pipeline analytics
Why FilmFund

FilmFund is not intended to be another database of grant links.

Its purpose is to reduce the research burden surrounding film financing by helping filmmakers discover opportunities that are relevant to their specific project.

The long-term vision is an intelligent funding assistant that continuously helps filmmakers identify realistic funding paths as their projects evolve.









