"""Load MULTIPLE REAL FILMFUND Projects - 2026-2029 Timelines

Creates realistic multi-project dataset with CURRENT and FUTURE timelines
(August 2026 - 2029), not past dates.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from google.cloud import bigquery
from src.config import Config
from src.logs import logger
from src.bigquery_rag import bq_rag_manager
from langchain_core.documents import Document

PROJECT_ID = Config.GOOGLE_PROJECT_ID
DATASET = "filmfund_rag"
TABLE = "scripts_embeddings"

client = bigquery.Client(project=PROJECT_ID)
table_id = f"{PROJECT_ID}.{DATASET}.{TABLE}"

def create_realistic_2026_2029_projects():
    """Create REAL projects with 2026-2029 timelines (CURRENT & FUTURE)"""
    
    projects = {
        "the_last_dawn": {
            "filmmaker": "Sarah Chen",
            "budget": 1200000,
            "gap": 850000,
            "funding_deadline": "2026-10-15",  # 2 months away (CURRENT)
            "production_start": "2026-11-01",
            "production_end": "2027-06-30",
            "release_target": "2027-12-01",
            "documents": [
                Document(
                    page_content="""THE LAST DAWN - OFFICIAL SCRIPT 2026
Genre: Science Fiction / Drama
Director: Sarah Chen
Logline: When Earth's last satellite fails, a disillusioned engineer must lead humanity's final mission.
Runtime: 112 minutes
Budget: $1,200,000 USD
Current Status: Post-funding (ACTIVE)
Funding Deadline: October 15, 2026 (URGENT - 2 MONTHS)
Production Start: November 1, 2026
Production End: June 30, 2027
Target Release: December 2027

PROJECT TIMELINE 2026-2027:
Aug-Oct 2026: Finalize funding (CURRENT PHASE)
Nov 2026-Jan 2027: Pre-production & crew hiring
Feb-Apr 2027: Principal photography (8 weeks)
May-Oct 2027: Post-production (editing, VFX, sound)
Nov-Dec 2027: Festival circuit launch

FILMING LOCATIONS:
- Los Angeles, California
- Mojave Desert, California  
- San Francisco Bay Area
- Studio sequences (space scenes)

CAST & CREW:
- Lead: (Casting in progress)
- Cinematographer: James Wilson (Echoes)
- Production Designer: Maria Garcia (Neon Dreams)

DISTRIBUTION PLAN:
- Sundance 2028 premiere target
- International festival circuit
- Theatrical + streaming hybrid release""",
                    metadata={
                        "source": "gs://filmfund-staging/the_last_dawn_2026/script.pdf",
                        "document_name": "the_last_dawn_script_2026.pdf",
                        "project": "The Last Dawn",
                        "filmmaker": "Sarah Chen",
                        "type": "filmmaker_script",
                        "timeline": "2026-2027",
                        "page": 1
                    }
                ),
                Document(
                    page_content="""THE LAST DAWN - PRODUCTION BUDGET 2026
Total Project Budget: $1,200,000 USD
Current Date: August 19, 2026
Funding Deadline: October 15, 2026

BUDGET BREAKDOWN:
Development (Completed): $45,000
Pre-Production: $185,000 (Nov 2026 - Jan 2027)
Principal Photography: $650,000 (Feb-Apr 2027)
Post-Production: $200,000 (May-Oct 2027)
Marketing & Distribution: $100,000 (Oct 2027 onwards)
Contingency (10%): $20,000

FUNDING STATUS (As of Aug 2026):
Secured: $350,000
- Producer Capital: $100,000
- ABC Films Investment: $200,000
- Arts Council Grant: $50,000

Remaining Gap: $850,000
Grant Funding Requested: $600,000
- California Arts Council (apply Sept 2026)
- NEA Production Grants
- International co-production funds

Investor Funding Needed: $250,000
- Looking for strategic investors
- Revenue share model available

FUNDING TIMELINE:
- Aug 2026: Final grant applications (THIS MONTH)
- Sept 2026: Investor meetings
- Oct 15, 2026: Funding deadline (CRITICAL)
- Nov 1, 2026: Production begins (if funded)""",
                    metadata={
                        "source": "gs://filmfund-staging/the_last_dawn_2026/budget.pdf",
                        "document_name": "the_last_dawn_budget_2026.pdf",
                        "project": "The Last Dawn",
                        "filmmaker": "Sarah Chen",
                        "type": "production_budget",
                        "timeline": "2026-2027",
                        "page": 1
                    }
                ),
            ]
        },
        
        "neon_dreams": {
            "filmmaker": "Marcus Johnson",
            "budget": 450000,
            "gap": 200000,
            "funding_deadline": "2026-11-30",  # 3 months away
            "production_start": "2027-01-15",
            "production_end": "2027-08-31",
            "release_target": "2028-03-01",
            "documents": [
                Document(
                    page_content="""NEON DREAMS - FEATURE FILM 2026-2027
Genre: Cyberpunk Thriller
Director: Marcus Johnson
Status: In pre-production (Funding in progress)
Logline: In a neon-soaked future city, a rogue hacker discovers a conspiracy that threatens humanity.
Runtime: 95 minutes
Total Budget: $450,000 USD
Funding Deadline: November 30, 2026

PRODUCTION TIMELINE 2026-2028:
Sep-Nov 2026: Complete funding (CURRENT)
Dec 2026: Finalize cast & crew
Jan-Aug 2027: Principal photography (32 days)
Sep 2027-Feb 2028: Post-production
Mar 2028: Festival premiere (SXSW target)

PRODUCTION APPROACH:
- Cyberpunk aesthetic with practical stunts
- Minimal VFX (cost effective)
- International co-production (Japan/Korea)
- Guerrilla filming in urban locations

FUNDING STATUS (Aug 2026):
Secured: $250,000
Gap: $200,000
Grant Requested: $150,000 (Foundation grants)
Investor Needed: $50,000 (Completion guarantor)

KEY TALENT:
- Lead Actor: (Negotiations in progress)
- Visual Effects: Studio Ghibli partners
- International Sales: CAA Media Finance""",
                    metadata={
                        "source": "gs://filmfund-staging/neon_dreams_2026/script.pdf",
                        "document_name": "neon_dreams_script_2026.pdf",
                        "project": "Neon Dreams",
                        "filmmaker": "Marcus Johnson",
                        "type": "filmmaker_script",
                        "timeline": "2026-2028",
                        "page": 1
                    }
                ),
            ]
        },
        
        "voices_of_change": {
            "filmmaker": "Aisha Patel",
            "budget": 300000,
            "gap": 100000,
            "funding_deadline": "2026-12-15",
            "production_start": "2027-02-01",
            "production_end": "2027-12-31",
            "release_target": "2028-06-01",
            "documents": [
                Document(
                    page_content="""VOICES OF CHANGE - DOCUMENTARY 2026-2028
Genre: Documentary / Social Justice
Director: Aisha Patel
Status: Production ready (Awaiting final funding)
Focus: Climate activism movement across developing nations
Runtime: 88 minutes
Budget: $300,000 USD
Funding Deadline: December 15, 2026

PRODUCTION TIMELINE 2026-2028:
Sep-Dec 2026: Secure remaining funding (CURRENT)
Jan 2027: Crew assembly & pre-production
Feb-Oct 2027: Production (5 countries)
Nov 2027-Feb 2028: Post-production
Jun 2028: Sundance 2029 submission (premiere target)

IMPACT STRATEGY:
- Follow 5 climate activists in real-time
- 5 countries: India, Brazil, Kenya, Indonesia, Philippines
- Educational toolkit for schools/universities
- International broadcast agreements (BBC, PBS, Al Jazeera)

FUNDING STATUS (Aug 2026):
Secured: $200,000
- Climate foundation grants: $100,000
- Documentary funds: $100,000

Remaining Gap: $100,000
Grant Sources Pending:
- Environmental Justice Fund (decision Sept 2026)
- International Documentary Association
- UNESCO Cultural Heritage Fund

FESTIVAL TARGETS:
- Sundance 2029 (premiere)
- SXSW 2029 (North America)
- Hot Docs 2029 (Canada)
- International Documentary Film Festival Amsterdam

CURRENT PRODUCTION STATUS:
- Crew: Partially assembled
- Pre-production: 80% complete
- Scheduling: Locked (subject to funding)
- Budget: Realistic & achievable""",
                    metadata={
                        "source": "gs://filmfund-staging/voices_of_change_2026/script.pdf",
                        "document_name": "voices_of_change_treatment_2026.pdf",
                        "project": "Voices of Change",
                        "filmmaker": "Aisha Patel",
                        "type": "filmmaker_script",
                        "timeline": "2026-2028",
                        "page": 1
                    }
                ),
            ]
        },
        
        "love_in_the_city": {
            "filmmaker": "Jessica Torres",
            "budget": 150000,
            "gap": 50000,
            "funding_deadline": "2026-09-30",  # 1.5 months away (URGENT)
            "production_start": "2026-10-15",
            "production_end": "2026-12-31",
            "release_target": "2027-06-01",
            "documents": [
                Document(
                    page_content="""LOVE IN THE CITY - INDIE ROMANCE 2026
Genre: Independent Romance Drama
Director: Jessica Torres
Status: URGENT - Last call for funding
Logline: Two strangers meet on the last weekend of summer in Los Angeles and must decide what's real.
Runtime: 78 minutes
Budget: $150,000 USD
Funding Deadline: September 30, 2026 (URGENT - 6 WEEKS)

PRODUCTION TIMELINE 2026-2027 (FAST-TRACK):
Sep 2026: Final funding push (CRITICAL)
Oct 15-Nov 10, 2026: Production (4 weeks principal photography)
Nov-Dec 2026: Post-production (color, sound, music)
Jan 2027: Film festivals submissions (Sundance, SXSW)
Jun 2027: Target release (festivals + streaming)

FAST-TRACK PRODUCTION:
- Guerrilla-style filming (no permits needed where possible)
- Real Los Angeles locations (parks, streets, apartments)
- Unknown actors (authentic casting, reduced costs)
- Minimal crew (20 people max)
- Digital intermediate (fast turnaround)

PRODUCTION STRATEGY 2026:
- Casting: Complete by Sept 15
- Location scouts: Already done
- Equipment rental: Pre-negotiated (30% discount)
- Post-production: Pre-booked facility (Sept available)

FUNDING STATUS (Aug 19, 2026):
Secured: $100,000
- Director's savings: $40,000
- Producer's investment: $60,000

Remaining Gap: $50,000
URGENT - Ways to close gap:
- Streaming pre-sales (Netflix, A24)
- Completion bond companies
- Last-minute angel investors
- Co-production with international partner

MARKET OPPORTUNITY:
- Strong millennial/Gen-Z appeal
- Perfect for streaming platforms
- No-budget indie success stories
- Low-budget, high-ROI potential
- Sundance 2027 premiere target""",
                    metadata={
                        "source": "gs://filmfund-staging/love_in_the_city_2026/script.pdf",
                        "document_name": "love_in_the_city_script_2026.pdf",
                        "project": "Love in the City",
                        "filmmaker": "Jessica Torres",
                        "type": "filmmaker_script",
                        "timeline": "2026-2027",
                        "page": 1
                    }
                ),
            ]
        },
        
        "the_future_calls": {
            "filmmaker": "David Kim",
            "budget": 800000,
            "gap": 400000,
            "funding_deadline": "2027-03-15",  # Future deadline
            "production_start": "2027-06-01",
            "production_end": "2028-03-31",
            "release_target": "2029-01-01",
            "documents": [
                Document(
                    page_content="""THE FUTURE CALLS - SCI-FI ACTION 2027-2029
Genre: Science Fiction / Action Adventure
Director: David Kim
Status: In development (Long-term project)
Logline: Earth receives its first message from an advanced civilization, and humanity must choose its future.
Runtime: 126 minutes
Budget: $800,000 USD
Timeline: 2027-2029 production
Funding Deadline: March 15, 2027 (8 months away)

LONG-TERM PRODUCTION PLAN 2027-2029:
2027 Q1: Final funding (Mar deadline)
2027 Q2: Pre-production begins (April-May)
2027 Q2-2028 Q1: Principal photography (36 days)
2028 Q1-Q3: Post-production
2028 Q4: Festival circuit (Sundance 2029, Berlin 2029)
2029: Theatrical release

AMBITIOUS VISION:
- $800K budget for major sci-fi action
- International co-production with China/Korea
- Visual effects: World-class standards
- Lead talent: A-list negotiations ongoing
- Theatrical distribution target

CURRENT STATUS (Aug 2026):
- Story development: 90% complete
- Budget refinement: In progress
- International partnerships: Being negotiated
- Pre-production: Scheduled to begin April 2027

This is a long-term strategic investment in 
the FILMFUND portfolio, targeting 2029 market.""",
                    metadata={
                        "source": "gs://filmfund-staging/the_future_calls_2026/script.pdf",
                        "document_name": "the_future_calls_script_2026.pdf",
                        "project": "The Future Calls",
                        "filmmaker": "David Kim",
                        "type": "filmmaker_script",
                        "timeline": "2027-2029",
                        "page": 1
                    }
                ),
            ]
        },
    }
    
    return projects

def insert_all_projects():
    """Insert all 2026-2029 projects to BigQuery"""
    
    logger.info("\n" + "="*80)
    logger.info("LOADING REAL FILMFUND PROJECTS - 2026-2029 TIMELINES")
    logger.info("Current Date: August 19, 2026")
    logger.info("="*80)
    
    projects = create_realistic_2026_2029_projects()
    total_rows = 0
    
    for project_name, project_data in projects.items():
        logger.info(f"\n{'='*80}")
        logger.info(f"Project: {project_data.get('filmmaker', 'Unknown')}")
        logger.info(f"Budget: ${project_data['budget']:,}")
        logger.info(f"Funding Gap: ${project_data['gap']:,}")
        logger.info(f"Funding Deadline: {project_data['funding_deadline']}")
        logger.info(f"Production: {project_data['production_start']} to {project_data['production_end']}")
        logger.info(f"Release Target: {project_data['release_target']}")
        logger.info(f"{'='*80}")
        
        rows_to_insert = []
        
        for doc_idx, doc in enumerate(project_data['documents']):
            logger.info(f"\nProcessing: {doc.metadata['document_name']}")
            
            content = doc.page_content
            embedding = bq_rag_manager.get_embedding(content)
            
            if not embedding:
                logger.error(f"Failed to generate embedding")
                continue
            
            logger.info(f"Embedding generated (dimension: {len(embedding)})")
            
            row = {
                "doc_id": f"{project_name}_{doc_idx}_{int(datetime.now().timestamp())}",
                "document_name": doc.metadata.get("document_name"),
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page", 1),
                "chunk": doc.metadata.get("chunk", 0),
                "content": content,
                "embedding": embedding,
                "type": doc.metadata.get("type"),
            }
            
            rows_to_insert.append(row)
        
        logger.info(f"\nInserting {len(rows_to_insert)} documents for {project_data.get('filmmaker')}...")
        
        try:
            errors = client.insert_rows_json(table_id, rows_to_insert)
            
            if errors:
                logger.error("Insertion errors:")
                for error in errors:
                    logger.error(f"  {error}")
            else:
                logger.info(f"Successfully inserted {len(rows_to_insert)} documents")
                total_rows += len(rows_to_insert)
        
        except Exception as e:
            logger.error(f"Error inserting project: {str(e)}")
    
    logger.info("\n" + "="*80)
    logger.info(f"TOTAL DOCUMENTS LOADED: {total_rows}")
    logger.info("REAL FILMFUND PROJECTS 2026-2029 LOADED TO BIGQUERY!")
    logger.info("August 2026 - Ready for REAL production workflows")
    logger.info("="*80)

def main():
    try:
        insert_all_projects()
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())