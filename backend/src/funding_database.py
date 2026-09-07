"""
FILMFUND Database Schema & Management
Stores opportunities, search history, analytics

Official References:
https://docs.python.org/3/library/sqlite3.html
https://www.sqlite.org/lang.html
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class FilmfundDatabase:
    """SQLite database for FILMFUND"""
    
    DB_PATH = "data/filmfund.db"
    
    def __init__(self):
        """Initialize database"""
        os.makedirs(os.path.dirname(self.DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cursor = self.conn.cursor()
        self._create_tables()
        logger.info(f"Database initialized: {self.DB_PATH}")
    
    def _create_tables(self):
        """Create database tables"""
        
        # Table 1: Filmmaker Profiles
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS filmmaker_profiles (
                id TEXT PRIMARY KEY,
                filmmaker_name TEXT NOT NULL,
                email TEXT NOT NULL,
                project_title TEXT NOT NULL,
                film_genre TEXT,
                total_budget REAL,
                experience_level TEXT,
                created_at TEXT,
                updated_at TEXT,
                profile_data TEXT
            )
        """)
        
        # Table 2: Funding Opportunities
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS funding_opportunities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                amount REAL,
                deadline TEXT,
                organization TEXT,
                eligibility TEXT,
                source TEXT,
                confidence_score REAL,
                match_score REAL,
                application_link TEXT,
                discovered_at TEXT,
                opportunity_data TEXT
            )
        """)
        
        # Table 3: Search History
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id TEXT PRIMARY KEY,
                filmmaker_profile_id TEXT NOT NULL,
                search_query TEXT,
                total_results INTEGER,
                sources_used TEXT,
                execution_time REAL,
                timestamp TEXT,
                FOREIGN KEY (filmmaker_profile_id) REFERENCES filmmaker_profiles(id)
            )
        """)
        
        # Table 4: Opportunity Matches
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS opportunity_matches (
                id TEXT PRIMARY KEY,
                filmmaker_profile_id TEXT NOT NULL,
                opportunity_id TEXT NOT NULL,
                search_id TEXT NOT NULL,
                match_score REAL,
                rank_position INTEGER,
                viewed BOOLEAN DEFAULT 0,
                applied BOOLEAN DEFAULT 0,
                application_date TEXT,
                outcome TEXT,
                timestamp TEXT,
                FOREIGN KEY (filmmaker_profile_id) REFERENCES filmmaker_profiles(id),
                FOREIGN KEY (opportunity_id) REFERENCES funding_opportunities(id),
                FOREIGN KEY (search_id) REFERENCES search_history(id)
            )
        """)
        
        # Table 5: Analytics Events
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                filmmaker_id TEXT,
                opportunity_id TEXT,
                metadata TEXT,
                timestamp TEXT
            )
        """)
        
        # Table 6: Rate Limit Tracking
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_tracking (
                id TEXT PRIMARY KEY,
                api_name TEXT,
                request_count INTEGER,
                daily_quota INTEGER,
                usage_date TEXT,
                timestamp TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("Database tables created")
    
    def save_filmmaker_profile(self, profile_id: str, profile_data: Dict) -> bool:
        """Save filmmaker profile"""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO filmmaker_profiles
                (id, filmmaker_name, email, project_title, film_genre, 
                 total_budget, experience_level, created_at, updated_at, profile_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                profile_data.get("filmmaker_name", ""),
                profile_data.get("filmmaker_email", ""),
                profile_data.get("project_title", ""),
                profile_data.get("film_genre", ""),
                profile_data.get("total_budget_needed", 0),
                profile_data.get("experience_level", ""),
                profile_data.get("created_at", datetime.now().isoformat()),
                datetime.now().isoformat(),
                json.dumps(profile_data)
            ))
            self.conn.commit()
            logger.info(f"Saved profile: {profile_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")
            return False
    
    def save_funding_opportunity(self, opportunity_data: Dict) -> bool:
        """Save funding opportunity"""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO funding_opportunities
                (id, name, type, amount, deadline, organization, eligibility, 
                 source, confidence_score, match_score, application_link, 
                 discovered_at, opportunity_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                opportunity_data.get("id", ""),
                opportunity_data.get("name", ""),
                opportunity_data.get("type", ""),
                opportunity_data.get("amount", 0),
                opportunity_data.get("deadline"),
                opportunity_data.get("organization", ""),
                opportunity_data.get("eligibility_requirements", ""),
                opportunity_data.get("source", ""),
                opportunity_data.get("confidence_score", 0),
                opportunity_data.get("match_score", 0),
                opportunity_data.get("application_link", ""),
                datetime.now().isoformat(),
                json.dumps(opportunity_data)
            ))
            self.conn.commit()
            logger.info(f"Saved opportunity: {opportunity_data.get('name')}")
            return True
        except Exception as e:
            logger.error(f"Error saving opportunity: {str(e)}")
            return False
    
    def save_search_history(self, search_id: str, filmmaker_id: str, 
                          search_query: str, total_results: int, 
                          sources: List[str], exec_time: float) -> bool:
        """Save search history"""
        try:
            self.cursor.execute("""
                INSERT INTO search_history
                (id, filmmaker_profile_id, search_query, total_results, 
                 sources_used, execution_time, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                search_id,
                filmmaker_id,
                search_query,
                total_results,
                json.dumps(sources),
                exec_time,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            logger.info(f"Saved search history: {search_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving search history: {str(e)}")
            return False
    
    def save_opportunity_match(self, filmmaker_id: str, opportunity_id: str,
                              search_id: str, match_score: float, 
                              rank: int) -> bool:
        """Save opportunity match result"""
        try:
            match_id = f"match_{filmmaker_id}_{opportunity_id}_{datetime.now().timestamp()}"
            self.cursor.execute("""
                INSERT INTO opportunity_matches
                (id, filmmaker_profile_id, opportunity_id, search_id, 
                 match_score, rank_position, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                match_id,
                filmmaker_id,
                opportunity_id,
                search_id,
                match_score,
                rank,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            logger.info(f"Saved opportunity match: {match_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving match: {str(e)}")
            return False
    
    def log_analytics_event(self, event_type: str, filmmaker_id: Optional[str] = None,
                           opportunity_id: Optional[str] = None, 
                           metadata: Optional[Dict] = None) -> bool:
        """Log analytics event"""
        try:
            event_id = f"event_{event_type}_{datetime.now().timestamp()}"
            self.cursor.execute("""
                INSERT INTO analytics_events
                (id, event_type, filmmaker_id, opportunity_id, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                event_type,
                filmmaker_id,
                opportunity_id,
                json.dumps(metadata) if metadata else None,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error logging event: {str(e)}")
            return False
    
    def get_filmmaker_profile(self, profile_id: str) -> Optional[Dict]:
        """Retrieve filmmaker profile"""
        try:
            self.cursor.execute(
                "SELECT profile_data FROM filmmaker_profiles WHERE id = ?",
                (profile_id,)
            )
            result = self.cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving profile: {str(e)}")
            return None
    
    def get_search_history(self, filmmaker_id: str, limit: int = 10) -> List[Dict]:
        """Get filmmaker's search history"""
        try:
            self.cursor.execute("""
                SELECT * FROM search_history 
                WHERE filmmaker_profile_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (filmmaker_id, limit))
            
            results = self.cursor.fetchall()
            return [dict(zip([desc[0] for desc in self.cursor.description], row)) 
                   for row in results]
        except Exception as e:
            logger.error(f"Error retrieving search history: {str(e)}")
            return []
    
    def get_opportunity_applications(self, filmmaker_id: str) -> List[Dict]:
        """Get opportunities filmmaker applied to"""
        try:
            self.cursor.execute("""
                SELECT om.*, fo.name, fo.amount, fo.deadline
                FROM opportunity_matches om
                JOIN funding_opportunities fo ON om.opportunity_id = fo.id
                WHERE om.filmmaker_profile_id = ? AND om.applied = 1
                ORDER BY om.application_date DESC
            """, (filmmaker_id,))
            
            results = self.cursor.fetchall()
            return [dict(zip([desc[0] for desc in self.cursor.description], row)) 
                   for row in results]
        except Exception as e:
            logger.error(f"Error retrieving applications: {str(e)}")
            return []
    
    def track_api_usage(self, api_name: str, daily_quota: int) -> bool:
        """Track API rate limit usage"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            self.cursor.execute("""
                SELECT request_count FROM rate_limit_tracking 
                WHERE api_name = ? AND usage_date = ?
            """, (api_name, today))
            
            result = self.cursor.fetchone()
            
            if result:
                count = result[0] + 1
                self.cursor.execute("""
                    UPDATE rate_limit_tracking 
                    SET request_count = ? 
                    WHERE api_name = ? AND usage_date = ?
                """, (count, api_name, today))
            else:
                tracking_id = f"ratelimit_{api_name}_{today}"
                self.cursor.execute("""
                    INSERT INTO rate_limit_tracking
                    (id, api_name, request_count, daily_quota, usage_date, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (tracking_id, api_name, 1, daily_quota, today, datetime.now().isoformat()))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error tracking API usage: {str(e)}")
            return False
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        logger.info("Database closed")