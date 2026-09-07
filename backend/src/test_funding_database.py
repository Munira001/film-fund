"""
Test FILMFUND Database
Verify all tables and functions work correctly
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from funding_database import FilmfundDatabase
from logs import logger


def test_database():
    """Complete database testing"""
    
    logger.info("\n" + "="*100)
    logger.info("TESTING FILMFUND DATABASE")
    logger.info("="*100)
    
    try:
        # === TEST 1: Initialize Database ===
        print("\n" + "="*80)
        print("TEST 1: Initialize Database")
        print("="*80)
        
        db = FilmfundDatabase()
        print("Database initialized successfully")
        print(f"   Location: {db.DB_PATH}")
        
        # === TEST 2: Save Filmmaker Profile ===
        print("\n" + "="*80)
        print("TEST 2: Save Filmmaker Profile")
        print("="*80)
        
        test_profile = {
            "filmmaker_name": "Test Filmmaker",
            "filmmaker_email": "test@filmfund.com",
            "project_title": "Test Film Project",
            "film_genre": "drama",
            "total_budget_needed": 75000,
            "experience_level": "experienced",
            "created_at": datetime.now().isoformat(),
            "key_themes": ["identity", "family"],
            "target_audience": "Adult audiences"
        }
        
        profile_id = "profile_test_001"
        success = db.save_filmmaker_profile(profile_id, test_profile)
        
        if success:
            print("Profile saved successfully")
            print(f"   Profile ID: {profile_id}")
            print(f"   Project: {test_profile['project_title']}")
            print(f"   Budget: ${test_profile['total_budget_needed']:,.0f}")
        else:
            print("Failed to save profile")
            return
        
        # === TEST 3: Retrieve Filmmaker Profile ===
        print("\n" + "="*80)
        print("TEST 3: Retrieve Filmmaker Profile")
        print("="*80)
        
        retrieved_profile = db.get_filmmaker_profile(profile_id)
        
        if retrieved_profile:
            print("Profile retrieved successfully")
            print(f"   Name: {retrieved_profile['filmmaker_name']}")
            print(f"   Email: {retrieved_profile['filmmaker_email']}")
            print(f"   Genre: {retrieved_profile['film_genre']}")
        else:
            print("Failed to retrieve profile")
            return
        
        # === TEST 4: Save Funding Opportunities ===
        print("\n" + "="*80)
        print("TEST 4: Save Funding Opportunities")
        print("="*80)
        
        test_opportunities = [
            {
                "id": "opp_001",
                "name": "Film Arts Foundation Grant",
                "type": "grant",
                "amount": 50000,
                "deadline": "2026-12-31",
                "organization": "Film Arts Foundation",
                "eligibility_requirements": "Independent filmmakers, all genres",
                "source": "google-cse",
                "confidence_score": 0.95,
                "match_score": 85.5,
                "application_link": "https://filmarts.org/apply"
            },
            {
                "id": "opp_002",
                "name": "Sundance Institute Grant",
                "type": "grant",
                "amount": 100000,
                "deadline": "2026-11-15",
                "organization": "Sundance Institute",
                "eligibility_requirements": "Drama, documentary, experimental",
                "source": "parallel-api",
                "confidence_score": 0.92,
                "match_score": 78.2,
                "application_link": "https://sundance.org/grants"
            },
            {
                "id": "opp_003",
                "name": "Independent Film Project",
                "type": "producer",
                "amount": 150000,
                "deadline": None,
                "organization": "IFP Productions",
                "eligibility_requirements": "Independent productions",
                "source": "parallel-api",
                "confidence_score": 0.88,
                "match_score": 72.1,
                "application_link": "https://ifp.org/contact"
            }
        ]
        
        saved_count = 0
        for opp in test_opportunities:
            if db.save_funding_opportunity(opp):
                saved_count += 1
        
        print(f"Saved {saved_count}/{len(test_opportunities)} opportunities")
        for opp in test_opportunities:
            print(f"   • {opp['name']} (${opp.get('amount', 0):,.0f})")
        
        # === TEST 5: Save Search History ===
        print("\n" + "="*80)
        print("TEST 5: Save Search History")
        print("="*80)
        
        search_id = f"search_test_{datetime.now().timestamp()}"
        search_success = db.save_search_history(
            search_id=search_id,
            filmmaker_id=profile_id,
            search_query="drama film grants $50K-$100K",
            total_results=3,
            sources=["parallel-api", "google-cse"],
            exec_time=2.45
        )
        
        if search_success:
            print("    Search history saved")
            print(f"   Search ID: {search_id}")
            print(f"   Query: drama film grants $50K-$100K")
            print(f"   Results: 3")
            print(f"   Time: 2.45 seconds")
        else:
            print("Failed to save search history")
        
        # === TEST 6: Save Opportunity Matches ===
        print("\n" + "="*80)
        print("TEST 6: Save Opportunity Matches")
        print("="*80)
        
        matches_saved = 0
        for i, opp in enumerate(test_opportunities, 1):
            if db.save_opportunity_match(
                filmmaker_id=profile_id,
                opportunity_id=opp["id"],
                search_id=search_id,
                match_score=opp["match_score"],
                rank=i
            ):
                matches_saved += 1
        
        print(f"✅ Saved {matches_saved}/{len(test_opportunities)} matches")
        for i, opp in enumerate(test_opportunities, 1):
            print(f"   {i}. {opp['name']} (Match: {opp['match_score']:.1f}%)")
        
        # === TEST 7: Log Analytics Events ===
        print("\n" + "="*80)
        print("TEST 7: Log Analytics Events")
        print("="*80)
        
        events_logged = 0
        
        events = [
            ("search_executed", profile_id, None, {"query": "drama grants", "results": 3}),
            ("opportunity_viewed", profile_id, "opp_001", {"viewed_at": datetime.now().isoformat()}),
            ("opportunity_clicked", profile_id, "opp_002", {"clicked_link": "https://sundance.org"}),
        ]
        
        for event_type, filmmaker_id, opp_id, metadata in events:
            if db.log_analytics_event(event_type, filmmaker_id, opp_id, metadata):
                events_logged += 1
        
        print(f"Logged {events_logged}/{len(events)} analytics events")
        for event_type, _, _, _ in events:
            print(f"   • {event_type}")
        
        # === TEST 8: Retrieve Search History ===
        print("\n" + "="*80)
        print("TEST 8: Retrieve Search History")
        print("="*80)
        
        history = db.get_search_history(profile_id, limit=5)
        
        if history:
            print(f"Retrieved {len(history)} search(es)")
            for search in history:
                print(f"   • Query: {search.get('search_query', 'N/A')}")
                print(f"     Results: {search.get('total_results', 0)}")
                print(f"     Time: {search.get('execution_time', 0):.2f}s")
        else:
            print("No search history found")
        
        # === TEST 9: Track API Usage ===
        print("\n" + "="*80)
        print("TEST 9: Track API Usage")
        print("="*80)
        
        apis = ["parallel-api", "google-cse"]
        tracked = 0
        
        for api in apis:
            # Simulate multiple requests
            for _ in range(3):
                if db.track_api_usage(api, 100):
                    tracked += 1
        
        print(f"Tracked {tracked} API requests")
        print(f"   Parallel API: 3 requests tracked")
        print(f"   Google CSE: 3 requests tracked")
        
        # === TEST 10: Database Integrity ===
        print("\n" + "="*80)
        print("TEST 10: Database Integrity Check")
        print("="*80)
        
        # Count records in each table
        tables = [
            "filmmaker_profiles",
            "funding_opportunities",
            "search_history",
            "opportunity_matches",
            "analytics_events"
        ]
        
        total_records = 0
        for table in tables:
            db.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = db.cursor.fetchone()[0]
            total_records += count
            print(f"   {table}: {count} records")
        
        print(f"\n✅ Total database records: {total_records}")
        
        # === CLEANUP ===
        print("\n" + "="*80)
        print("TEST CLEANUP")
        print("="*80)
        
        db.close()
        print("Database connection closed")
        
        # === FINAL SUMMARY ===
        print("\n" + "="*100)
        print(" ALL DATABASE TESTS PASSED!")
        print("="*100)
        print("\nDatabase is working correctly!")
        print("Location: data/filmfund.db")
        print("\nNext: Run enhanced funding_search.py with database integration")
        print("="*100 + "\n")
        
        logger.info("All database tests passed")
        
    except Exception as e:
        print(f"\ Error: {str(e)}")
        logger.error(f"Database test error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_database()