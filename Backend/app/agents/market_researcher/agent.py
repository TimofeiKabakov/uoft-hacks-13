"""
Market Researcher Agent

Analyzes market conditions and competition using Google Maps/Places data
"""
from typing import Dict, Any, List
from langchain_google_genai import ChatGoogleGenerativeAI

from app.services.google_service import GoogleService


class MarketResearcher:
    """
    Agent responsible for market analysis

    Analyzes location, competition, market density, and viability
    for loan assessment of business ventures.
    """

    def __init__(self, llm: ChatGoogleGenerativeAI):
        """
        Initialize Market Researcher agent

        Args:
            llm: Shared LLM instance
        """
        self.llm = llm
        self.google_service = GoogleService()

    async def analyze(
        self,
        user_job: str,
        location_lat: float,
        location_lng: float,
        loan_amount: float,
        loan_purpose: str
    ) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis

        Args:
            user_job: Applicant's job/business type
            location_lat: Latitude of business location
            location_lng: Longitude of business location
            loan_amount: Requested loan amount
            loan_purpose: Purpose of the loan

        Returns:
            Dictionary with market analysis results
        """
        try:
            # Extract business type from job description
            business_type = self._extract_business_type(user_job)

            # Search for nearby competing businesses
            nearby = self.google_service.get_nearby_businesses(
                lat=location_lat,
                lng=location_lng,
                business_type=business_type,
                radius=3200  # 2 miles in meters
            )

            # Analyze market density
            density = self.google_service.analyze_market_density(
                nearby_businesses=nearby,
                radius_miles=2.0
            )

            # Calculate viability score
            viability_score = self._calculate_viability_score(
                nearby_businesses=nearby,
                density=density,
                business_type=business_type
            )

            # Generate insights
            insights = self._generate_insights(
                nearby_businesses=nearby,
                density=density,
                business_type=business_type,
                user_job=user_job
            )

            return {
                'success': True,
                'competitor_count': len(nearby),
                'market_density': density,
                'viability_score': viability_score,
                'nearby_businesses': nearby[:10],  # Top 10 closest
                'market_insights': insights['summary'],
                'opportunities': insights['opportunities'],
                'risks': insights['risks'],
                'recommendations': insights['recommendations']
            }

        except Exception as e:
            # Return default analysis on error
            return {
                'success': False,
                'error': str(e),
                'competitor_count': 0,
                'market_density': 'unknown',
                'viability_score': 50.0,
                'nearby_businesses': [],
                'market_insights': f'Error analyzing market: {str(e)}',
                'opportunities': [],
                'risks': ['Unable to retrieve market data'],
                'recommendations': ['Manual market research recommended']
            }

    def _extract_business_type(self, user_job: str) -> str:
        """
        Extract business type from job description

        Args:
            user_job: Job/business description

        Returns:
            Business type for Google Places search
        """
        job_lower = user_job.lower()

        # Keyword matching for common business types
        if 'cafe' in job_lower or 'coffee' in job_lower:
            return 'cafe'
        elif 'restaurant' in job_lower or 'food' in job_lower or 'dining' in job_lower:
            return 'restaurant'
        elif 'retail' in job_lower or 'store' in job_lower or 'shop' in job_lower:
            return 'store'
        elif 'salon' in job_lower or 'barber' in job_lower or 'beauty' in job_lower:
            return 'beauty_salon'
        elif 'gym' in job_lower or 'fitness' in job_lower:
            return 'gym'
        elif 'bar' in job_lower or 'pub' in job_lower:
            return 'bar'
        elif 'bakery' in job_lower:
            return 'bakery'
        else:
            return 'establishment'

    def _calculate_viability_score(
        self,
        nearby_businesses: List[Dict[str, Any]],
        density: str,
        business_type: str
    ) -> float:
        """
        Calculate market viability score (0-100)

        Args:
            nearby_businesses: List of competing businesses
            density: Market density classification
            business_type: Type of business

        Returns:
            Viability score from 0-100
        """
        base_score = 50.0

        # Density impact
        if density == "low":
            density_score = 40.0
        elif density == "medium":
            density_score = 25.0
        else:  # high
            density_score = 5.0

        # Competition count impact
        competitor_count = len(nearby_businesses)
        if competitor_count == 0:
            competition_score = 30.0
        elif competitor_count <= 3:
            competition_score = 25.0
        elif competitor_count <= 7:
            competition_score = 15.0
        elif competitor_count <= 15:
            competition_score = 10.0
        else:
            competition_score = 0.0

        # Competitor quality impact (based on ratings)
        if nearby_businesses:
            avg_rating = sum(b.get('rating', 0) for b in nearby_businesses) / len(nearby_businesses)
            if avg_rating >= 4.5:
                quality_penalty = -10.0
            elif avg_rating >= 4.0:
                quality_penalty = -5.0
            else:
                quality_penalty = 0.0
        else:
            quality_penalty = 0.0

        total_score = base_score + density_score + competition_score + quality_penalty

        return min(100.0, max(0.0, total_score))

    def _generate_insights(
        self,
        nearby_businesses: List[Dict[str, Any]],
        density: str,
        business_type: str,
        user_job: str
    ) -> Dict[str, Any]:
        """
        Generate market insights, opportunities, and risks

        Args:
            nearby_businesses: List of competing businesses
            density: Market density classification
            business_type: Type of business
            user_job: Applicant's job description

        Returns:
            Dictionary with insights, opportunities, and risks
        """
        competitor_count = len(nearby_businesses)

        # Summary
        summary = (
            f"Found {competitor_count} competing {business_type}(s) within 2-mile radius. "
            f"Market density is {density}."
        )

        # Opportunities
        opportunities = []
        if density == "low":
            opportunities.append("Low competition presents opportunity for market entry")
            opportunities.append("Potential to establish strong market presence")
        elif density == "medium":
            opportunities.append("Balanced market with room for differentiation")

        if competitor_count == 0:
            opportunities.append("No direct competitors in immediate area")
        elif competitor_count <= 3:
            opportunities.append("Limited competition allows for market share capture")

        # Check for low-rated competitors
        if nearby_businesses:
            low_rated = [b for b in nearby_businesses if b.get('rating', 5.0) < 3.5]
            if low_rated:
                opportunities.append(f"{len(low_rated)} competitors have low ratings - quality differentiation opportunity")

        # Risks
        risks = []
        if density == "high":
            risks.append("High market saturation may limit growth potential")
            risks.append("Increased competition for customer acquisition")

        if competitor_count > 10:
            risks.append(f"{competitor_count} competitors in area indicates saturated market")

        # Check for highly-rated competitors
        if nearby_businesses:
            high_rated = [b for b in nearby_businesses if b.get('rating', 0) >= 4.5]
            if high_rated:
                risks.append(f"{len(high_rated)} competitors have high ratings (4.5+) - strong competition")

        if not opportunities:
            opportunities.append("Market conditions are competitive but manageable")

        if not risks:
            risks.append("Standard market entry risks apply")

        # Recommendations
        recommendations = []
        if density == "low":
            recommendations.append("Focus on building brand awareness in underserved market")
        elif density == "high":
            recommendations.append("Develop clear differentiation strategy to stand out")
            recommendations.append("Consider unique value proposition or niche targeting")

        if competitor_count > 5:
            recommendations.append("Conduct competitive analysis to identify gaps")

        recommendations.append("Monitor competitor performance and customer feedback")

        return {
            'summary': summary,
            'opportunities': opportunities,
            'risks': risks,
            'recommendations': recommendations
        }
