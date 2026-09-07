"""
Phase 3 - Complete Integration
All features: Metrics, State, Reasoning, Error Recovery, MCP
REAL DATA ONLY - GLOBAL + USA searches with REAL data extraction
"""

import time
import os
import logging
from agent_metrics import AgentMetrics
from agent_state import AgentStateManager, AgentState
from agent_reasoning import AgentReasoning
from agent_error_handler import ErrorHandler
from agent_mcp import mcp_server
from parallel_api import ParallelAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase3CompleteAgent:
    
    def __init__(self, filmmaker: dict):
        self.filmmaker = filmmaker
        self.parallel_api = ParallelAPI()
        self.metrics = AgentMetrics()
        self.state = AgentStateManager("filmfund-agent-1")
        self.reasoning = AgentReasoning()
        self.error_handler = ErrorHandler(max_retries=3)
        
        logger.info("Phase 3 Complete Agent initialized")
    
    def run(self):
        """Execute complete agent workflow - GLOBAL + USA searches"""
        
        print("\n" + "="*60)
        print("PHASE 3 - COMPLETE INTEGRATION (USA + GLOBAL)")
        print("="*60 + "\n")
        
        try:
            self.state.transition(AgentState.SEARCHING, "Starting global searches")
            
            # Get search queries (returns LIST of 20+ queries)
            search_queries = self.reasoning.decide_search_strategy(self.filmmaker)
            self.state.record_decision("search_strategy", {"num_queries": len(search_queries)})
            
            print(f"Searching {len(search_queries)} categories (USA + GLOBAL)...\n")
            
            all_results = []
            
            # Search EACH query individually
            for i, query in enumerate(search_queries, 1):
                print(f"[{i}/{len(search_queries)}] Searching: {query}")
                
                start_time = time.time()
                
                # Pass single query string, 20 results per query
                results = self.error_handler.retry_with_backoff(
                    self.parallel_api.search,
                    query,
                    limit=20
                )
                
                duration = time.time() - start_time
                
                self.metrics.log_search(query, len(results), duration)
                all_results.extend(results)
                
                print(f"  Found {len(results)} opportunities\n")
            
            print(f"Total opportunities found: {len(all_results)}\n")
            
            if not all_results:
                print("No results found\n")
                self.state.transition(AgentState.ERROR, "No results from any search")
                return
            
            # Remove duplicates by URL
            unique_results = {opp.get('url', opp.get('name')): opp for opp in all_results}
            all_results = list(unique_results.values())
            
            print(f"Unique opportunities: {len(all_results)}\n")
            
            # Matching state
            self.state.transition(AgentState.MATCHING, "Matching opportunities")
            
            scored = []
            for opp in all_results:
                score = self._calculate_real_score(opp, self.filmmaker)
                priority = self.reasoning.decide_priority(opp, self.filmmaker)
                should_apply = self.reasoning.should_apply(score, priority)
                
                scored.append({
                    "opportunity": opp,
                    "score": score,
                    "should_apply": should_apply,
                    "priority": priority
                })
                
                if should_apply:
                    self.metrics.log_match(
                        self.filmmaker.get('filmmaker_name', 'Unknown'),
                        self._extract_opportunity_name(opp),
                        score
                    )
            
            # Ranking state
            self.state.transition(AgentState.RANKING, "Ranking results")
            
            ranked = sorted(
                scored,
                key=lambda x: x['score'],
                reverse=True
            )
            
            print("Top opportunities (USA + GLOBAL):\n")
            for i, item in enumerate(ranked[:20], 1):
                opp = item['opportunity']
                score = item['score']
                
                # REAL data extraction
                name = self._extract_opportunity_name(opp)
                deadline = self._extract_deadline(opp)
                budget = self._extract_budget(opp)
                organization = opp.get('organization', opp.get('provider', 'Organization'))
                
                print(f"{i}. {name}")
                print(f"   Organization: {organization}")
                print(f"   Score: {score:.0f}%")
                print(f"   Priority: {item['priority']['overall_priority']:.1%}")
                print(f"   Deadline: {deadline}")
                print(f"   Budget: {budget}")
                print(f"   URL: {opp.get('url', 'N/A')}")
                print()
            
            # Complete state
            self.state.transition(AgentState.COMPLETE, "Workflow complete")
            
            # Save reports
            os.makedirs("data", exist_ok=True)
            self.metrics.save_report("data/phase3_metrics.json")
            self.state.export_state("data/phase3_state.json")
            
            print("="*60)
            print("PHASE 3 COMPLETE - FULL INTEGRATION (USA + GLOBAL)")
            print("="*60)
            print(f"\nMetrics Summary:")
            summary = self.metrics.get_summary()
            for key, value in summary.items():
                print(f"  {key}: {value}")
            print()
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            self.state.transition(AgentState.ERROR, str(e))
            self.metrics.log_error("WorkflowError", str(e))
            raise
    
    def _calculate_real_score(self, opportunity: dict, filmmaker: dict) -> float:
        """REAL scoring based on ACTUAL opportunity data"""
        
        score = 0
        
        # Get actual budget data
        budget = filmmaker.get('total_budget_needed', 0)
        opp_budget = opportunity.get('budget', {})
        
        if isinstance(opp_budget, dict):
            opp_min = opp_budget.get('min', 0)
            opp_max = opp_budget.get('max', 999999)
        else:
            opp_min = 0
            opp_max = 999999
        
        # Budget fit (30 points) - REAL calculation
        if opp_min == 0 and opp_max == 999999:
            score += 15
        elif opp_min <= budget <= opp_max:
            score += 30
        elif budget * 0.8 <= opp_max and budget * 1.2 >= opp_min:
            score += 20
        else:
            score += 5
        
        # Genre match (25 points) - REAL calculation
        genres = opportunity.get('genres', ['all'])
        filmmaker_genre = filmmaker.get('film_genre', 'other')
        
        if 'all' in genres:
            score += 15
        elif filmmaker_genre in genres:
            score += 25
        else:
            score += 5
        
        # Deadline urgency (20 points)
        deadline = opportunity.get('deadline', '')
        if deadline and 'rolling' not in deadline.lower():
            score += 15
        elif deadline and 'rolling' in deadline.lower():
            score += 20
        
        # Application fee (15 points)
        has_fee = opportunity.get('application_fee', False)
        if not has_fee:
            score += 15
        else:
            score += 5
        
        # Experience level (10 points)
        experience = filmmaker.get('experience_level', 'some')
        eligibility = opportunity.get('eligibility', ['all'])
        
        if 'all' in eligibility or experience in eligibility:
            score += 10
        
        return min(100, max(0, score))
    
    def _extract_opportunity_name(self, opportunity: dict) -> str:
        """Extract opportunity name from various fields"""
        
        name = opportunity.get('name')
        if name and name != 'Unknown':
            return name
        
        name = opportunity.get('title')
        if name and name != 'Unknown':
            return name
        
        name = opportunity.get('opportunity_name')
        if name and name != 'Unknown':
            return name
        
        url = opportunity.get('url', '')
        if url:
            parts = url.split('/')
            if len(parts) > 2:
                return parts[2].replace('www.', '').replace('.com', '')
        
        return 'Grant Opportunity'
    
    def _extract_deadline(self, opportunity: dict) -> str:
        """Extract deadline from opportunity"""
        
        deadline = opportunity.get('deadline', 'Rolling')
        if deadline:
            return deadline
        
        deadline = opportunity.get('due_date', 'Rolling')
        if deadline:
            return deadline
        
        return 'Ongoing'
    
    def _extract_budget(self, opportunity: dict) -> str:
        """Extract budget range from opportunity"""
        
        budget = opportunity.get('budget', {})
        
        if isinstance(budget, dict):
            min_amt = budget.get('min', 0)
            max_amt = budget.get('max', 'Varies')
            
            if min_amt and max_amt:
                return f"${min_amt:,} - ${max_amt:,}"
            elif min_amt:
                return f"${min_amt:,}+"
        
        budget_str = opportunity.get('budget_range', '')
        if budget_str:
            return budget_str
        
        return 'Not specified'


def main():
    # REAL filmmaker data
    filmmaker = {
        "filmmaker_name": "Munira Mohammed",
        "filmmaker_email": "muniramohammed1256@gmail.com",
        "film_genre": "other",
        "total_budget_needed": 100000,
        "experience_level": "professional",
        "filmmaker_location": "Global",
        "project_title": "FILMFUND",
        "project_logline": "AI agent for filmmaker funding"
    }
    
    agent = Phase3CompleteAgent(filmmaker)
    agent.run()


if __name__ == "__main__":
    main()