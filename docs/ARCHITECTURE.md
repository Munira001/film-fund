# FILMFUND Architecture

### Main Components

#### 1. search_grants()
- Input: filmmaker details (budget, genre, experience, timeline)
- Action: Call Parallel API with search query
- Output: List of grants with details
- Uses: Phase 2 from 12-phase instructions

#### 2. analyze_grants()
- Input: Raw grants data
- Action: Filter scams, verify details, extract key info
- Output: Cleaned, analyzed grants
- Uses: Phase 3 from 12-phase instructions

#### 3. rank_opportunities()
- Input: Analyzed grants + filmmaker profile
- Action: Score by relevance, amount, ease, timeline
- Output: Top 5 ranked opportunities
- Uses: Phase 4 from 12-phase instructions

#### 4. search_producers()
- Input: Budget, genre
- Action: Search for matching production companies
- Output: List of producers
- Uses: Phase 2 research

#### 5. build_response()
- Input: All opportunities (grants, producers, crowdfunding)
- Action: Format for filmmaker
- Output: Actionable next steps
- Uses: Phase 5 from 12-phase instructions

### Data Flow

Filmmaker Query
    ↓
Extract Details (Phase 1)
    ↓
Search Parallel API (Phase 2)
    ↓
Analyze Results (Phase 3)
    ↓
Rank Opportunities (Phase 4)
    ↓
Format Response (Phase 5)
    ↓
Return to Filmmaker

### Error Handling
- Parallel API failures → fallback to cached data
- No results → suggest alternatives
- Scam detection → flag suspicious grants