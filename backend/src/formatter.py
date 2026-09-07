"""Response formatting - Phase 5"""

from logs import logger

class ResponseFormatter:
    """Formats opportunities for filmmaker"""
    
    @staticmethod
    def build_response(grants: list, filmmaker_budget: int) -> str:
        """Build human-readable response - Phase 5"""
        try:
            response = []
            response.append("=" * 60)
            response.append("FILMFUND OPPORTUNITIES")
            response.append("=" * 60)
            response.append("")
            
            response.append(f"SUMMARY")
            response.append(f"Found {len(grants)} verified opportunities")
            response.append(f"Estimated total available: ${sum(g.amount for g in grants):,.0f}")
            response.append("")
            
            response.append("TOP OPPORTUNITIES (Ranked by fit)")
            response.append("-" * 60)
            
            for i, grant in enumerate(grants, 1):
                response.append(f"\n{i}. {grant.name}")
                response.append(f"   Amount: ${grant.amount:,.0f}")
                response.append(f"   Deadline: {grant.deadline}")
                response.append(f"   Fit Score: {grant.fit_score:.0f}%")
                response.append(f"   Link: {grant.link}")
            
            response.append("")
            response.append("=" * 60)
            response.append("NEXT STEPS:")
            response.append("1. Review top 3 opportunities")
            response.append("2. Gather required documents")
            response.append("3. Apply this week")
            response.append("4. Follow up in 2 weeks")
            response.append("=" * 60)
            
            output = "\n".join(response)
            logger.info("Response formatted successfully")
            return output
            
        except Exception as e:
            logger.error(f"Formatting error: {str(e)}")
            return "Error formatting response"