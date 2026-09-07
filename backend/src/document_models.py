"""Pydantic Models for FILMFUND Document Processing

Following official pattern from:
https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/use-cases/document-processing/document_processing.ipynb

Models for extracting structured data from:
- Filmmaker scripts
- Budget documents
- Production schedules
- Filmmaker profiles
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


# ========== DOCUMENT METADATA (ALL DOCUMENTS) ==========

class DocumentMetadata(BaseModel):
    """Metadata about the document itself"""
    
    document_source_uri: Optional[str] = Field(
        None,
        description="URI or file path of original document"
    )
    document_filename: Optional[str] = Field(
        None,
        description="Original filename of the document"
    )
    extraction_date: Optional[date] = Field(
        None,
        description="Date when document was extracted"
    )
    extraction_confidence: Optional[float] = Field(
        None,
        description="Confidence level of extraction (0.0-1.0)"
    )
    total_pages: Optional[int] = Field(
        None,
        description="Total pages in original document"
    )
    relevant_pages: Optional[List[int]] = Field(
        None,
        description="Page numbers containing relevant data"
    )


# ========== FILMMAKER SCRIPT ==========

class FilmmakerScript(BaseModel):
    """Represents structured data extracted from a filmmaker's script document."""
    
    # Core project info
    project_title: str = Field(
        ..., 
        description="The title of the film project, e.g., 'The Last Dawn'"
    )
    logline: str = Field(
        ...,
        description="One-sentence summary of the film's plot"
    )
    genre: str = Field(
        ...,
        description="Film genre, e.g., sci-fi, horror, drama, comedy"
    )
    runtime_minutes: Optional[int] = Field(
        None,
        description="Expected runtime in minutes"
    )
    synopsis: Optional[str] = Field(
        None,
        description="Detailed plot summary (2-3 paragraphs)"
    )
    
    # Budget info
    estimated_budget: Optional[float] = Field(
        None,
        description="Estimated production budget in dollars"
    )
    budget_currency: Optional[str] = Field(
        None,
        description="Currency code, e.g., USD, EUR"
    )
    
    # Filmmaker info
    filmmaker_name: Optional[str] = Field(
        None,
        description="Name of the filmmaker/director"
    )
    
    # Production details
    production_stage: Optional[str] = Field(
        None,
        description="Current stage: concept, development, pre-production, in-production"
    )
    filming_locations: Optional[List[str]] = Field(
        None,
        description="List of planned filming locations"
    )
    key_cast: Optional[List[str]] = Field(
        None,
        description="List of main actors/cast members"
    )
    target_audience: Optional[str] = Field(
        None,
        description="Target audience demographic"
    )
    release_date: Optional[date] = Field(
        None,
        description="Planned release date"
    )
    
    # ===== FILMFUND-SPECIFIC FIELDS =====
    urgency_level: Optional[str] = Field(
        None,
        description="Funding urgency: urgent/soon/flexible"
    )
    target_funding_amount: Optional[float] = Field(
        None,
        description="Total funding amount needed for this project"
    )
    funding_type_seeking: Optional[List[str]] = Field(
        None,
        description="Types of funding sought: grants/investors/sponsors/crowdfunding"
    )
    tax_incentive_eligibility: Optional[List[str]] = Field(
        None,
        description="States/countries where eligible for tax incentives"
    )
    grant_eligibility_criteria: Optional[List[str]] = Field(
        None,
        description="Specific grant requirements this project meets"
    )
    
    # Metadata
    metadata: Optional[DocumentMetadata] = Field(
        None,
        description="Document metadata"
    )


# ========== BUDGET DOCUMENT ==========

class BudgetDocument(BaseModel):
    """Represents structured budget data extracted from filmmaker budget documents."""
    
    # Core budget info
    project_title: str = Field(
        ...,
        description="Film project title"
    )
    total_budget: float = Field(
        ...,
        description="Total project budget in dollars"
    )
    budget_currency: str = Field(
        ...,
        description="Currency code, e.g., USD"
    )
    
    # Budget categories
    development_budget: Optional[float] = Field(
        None,
        description="Development phase budget (writing, planning)"
    )
    pre_production_budget: Optional[float] = Field(
        None,
        description="Pre-production budget (location scouting, casting)"
    )
    production_budget: Optional[float] = Field(
        None,
        description="Principal photography/production budget"
    )
    post_production_budget: Optional[float] = Field(
        None,
        description="Post-production budget (editing, sound, color)"
    )
    marketing_budget: Optional[float] = Field(
        None,
        description="Marketing and distribution budget"
    )
    contingency_budget: Optional[float] = Field(
        None,
        description="Contingency/emergency fund (usually 10% of total)"
    )
    
    # Specific line items
    crew_budget: Optional[float] = Field(
        None,
        description="Total crew salaries/wages"
    )
    cast_budget: Optional[float] = Field(
        None,
        description="Actor/talent fees"
    )
    equipment_rental: Optional[float] = Field(
        None,
        description="Camera, lighting, sound equipment rental"
    )
    location_fees: Optional[float] = Field(
        None,
        description="Location rental and permits"
    )
    insurance_budget: Optional[float] = Field(
        None,
        description="Production insurance costs"
    )
    
    # Timeline
    budget_period_start: Optional[date] = Field(
        None,
        description="Start date of budget period"
    )
    budget_period_end: Optional[date] = Field(
        None,
        description="End date of budget period"
    )
    prepared_by: Optional[str] = Field(
        None,
        description="Name of person who prepared the budget"
    )
    last_updated: Optional[date] = Field(
        None,
        description="Date budget was last updated"
    )
    
    # ===== FILMFUND-SPECIFIC FIELDS =====
    funding_gap: Optional[float] = Field(
        None,
        description="Amount still needed (total_budget - secured_funding)"
    )
    funding_sources_secured: Optional[dict] = Field(
        None,
        description="Breakdown of already-secured funding by source"
    )
    total_funding_secured: Optional[float] = Field(
        None,
        description="Total funding already obtained"
    )
    co_production_partners: Optional[List[str]] = Field(
        None,
        description="Other entities providing co-production funding"
    )
    grant_funding_requested: Optional[float] = Field(
        None,
        description="Amount of grant funding being requested"
    )
    investor_funding_requested: Optional[float] = Field(
        None,
        description="Amount of investor/equity funding being requested"
    )
    budget_notes: Optional[str] = Field(
        None,
        description="Special notes about budget allocations or constraints"
    )
    
    # Metadata
    metadata: Optional[DocumentMetadata] = Field(
        None,
        description="Document metadata"
    )


# ========== PRODUCTION SCHEDULE ==========

class ProductionSchedule(BaseModel):
    """Represents structured schedule data extracted from filmmaker production schedules."""
    
    # Project identification
    project_title: str = Field(
        ...,
        description="Film project title"
    )
    
    # Overall timeline
    project_start_date: date = Field(
        ...,
        description="Project official start date"
    )
    estimated_completion_date: date = Field(
        ...,
        description="Estimated project completion date"
    )
    
    # Phase dates
    development_start: Optional[date] = Field(
        None,
        description="Development phase start date"
    )
    development_end: Optional[date] = Field(
        None,
        description="Development phase end date"
    )
    pre_production_start: Optional[date] = Field(
        None,
        description="Pre-production phase start date"
    )
    pre_production_end: Optional[date] = Field(
        None,
        description="Pre-production phase end date"
    )
    principal_photography_start: Optional[date] = Field(
        None,
        description="Principal photography start date"
    )
    principal_photography_end: Optional[date] = Field(
        None,
        description="Principal photography end date"
    )
    post_production_start: Optional[date] = Field(
        None,
        description="Post-production phase start date"
    )
    post_production_end: Optional[date] = Field(
        None,
        description="Post-production phase end date"
    )
    distribution_start: Optional[date] = Field(
        None,
        description="Distribution/release phase start date"
    )
    
    # Key milestones
    script_deadline: Optional[date] = Field(
        None,
        description="Final script deadline"
    )
    casting_deadline: Optional[date] = Field(
        None,
        description="Casting completion deadline"
    )
    first_day_of_shoot: Optional[date] = Field(
        None,
        description="First day of principal photography"
    )
    last_day_of_shoot: Optional[date] = Field(
        None,
        description="Last day of principal photography"
    )
    rough_cut_deadline: Optional[date] = Field(
        None,
        description="Rough cut completion deadline"
    )
    final_cut_deadline: Optional[date] = Field(
        None,
        description="Final cut completion deadline"
    )
    festival_submission_deadline: Optional[date] = Field(
        None,
        description="Film festival submission deadline"
    )
    
    # Production details
    total_shooting_days: Optional[int] = Field(
        None,
        description="Total number of shooting days planned"
    )
    prepared_by: Optional[str] = Field(
        None,
        description="Name of person who prepared the schedule"
    )
    
    # ===== FILMFUND-SPECIFIC FIELDS =====
    funding_deadline: Optional[date] = Field(
        None,
        description="Deadline by which funding must be secured"
    )
    milestone_funding_schedule: Optional[dict] = Field(
        None,
        description="Breakdown of when funding is needed for each phase"
    )
    phases_dependent_on_funding: Optional[List[str]] = Field(
        None,
        description="Which phases cannot start without funding (e.g., pre-production)"
    )
    critical_path_items: Optional[List[str]] = Field(
        None,
        description="Time-critical milestones that affect entire schedule"
    )
    schedule_buffer_days: Optional[int] = Field(
        None,
        description="Buffer/contingency days built into schedule"
    )
    
    # Metadata
    metadata: Optional[DocumentMetadata] = Field(
        None,
        description="Document metadata"
    )


# ========== FILMMAKER PROFILE ==========

class FilmmakerProfile(BaseModel):
    """Represents structured profile data extracted from filmmaker profile documents."""
    
    # Contact info
    filmmaker_name: str = Field(
        ...,
        description="Full name of the filmmaker"
    )
    title: Optional[str] = Field(
        None,
        description="Professional title, e.g., Director, Producer, Cinematographer"
    )
    email: Optional[str] = Field(
        None,
        description="Contact email address"
    )
    phone: Optional[str] = Field(
        None,
        description="Contact phone number"
    )
    website: Optional[str] = Field(
        None,
        description="Personal/portfolio website URL"
    )
    social_media: Optional[dict] = Field(
        None,
        description="Social media profiles (Instagram, LinkedIn, etc.)"
    )
    
    # Experience
    years_of_experience: Optional[int] = Field(
        None,
        description="Years working in film industry"
    )
    experience_level: Optional[str] = Field(
        None,
        description="Experience level: first-time, emerging, established, veteran"
    )
    
    # Specializations
    primary_role: Optional[str] = Field(
        None,
        description="Primary role: director, producer, writer, cinematographer, etc."
    )
    specializations: Optional[List[str]] = Field(
        None,
        description="Areas of specialization, e.g., documentary, animation, horror"
    )
    
    # Past work
    notable_films: Optional[List[str]] = Field(
        None,
        description="List of notable films/projects created"
    )
    festival_selections: Optional[List[str]] = Field(
        None,
        description="Film festival selections and awards"
    )
    awards_and_recognition: Optional[List[str]] = Field(
        None,
        description="Major awards and industry recognition"
    )
    
    # Education
    film_education: Optional[List[str]] = Field(
        None,
        description="Film school or formal training"
    )
    certifications: Optional[List[str]] = Field(
        None,
        description="Professional certifications"
    )
    
    # Current focus
    current_projects: Optional[List[str]] = Field(
        None,
        description="Current projects in development/production"
    )
    
    # Location
    location_city: Optional[str] = Field(
        None,
        description="City where filmmaker is based"
    )
    location_state: Optional[str] = Field(
        None,
        description="State/province where filmmaker is based"
    )
    location_country: Optional[str] = Field(
        None,
        description="Country where filmmaker is based"
    )
    
    bio: Optional[str] = Field(
        None,
        description="Brief biography or professional summary"
    )
    
    # ===== FILMFUND-SPECIFIC FIELDS =====
    seeking_funding: Optional[bool] = Field(
        None,
        description="Whether filmmaker is actively seeking funding"
    )
    funding_goals: Optional[str] = Field(
        None,
        description="Description of funding needs and goals"
    )
    grant_track_record: Optional[dict] = Field(
        None,
        description="History of grant funding received (amount, source, year)"
    )
    investor_track_record: Optional[dict] = Field(
        None,
        description="History of investor funding received"
    )
    previous_successful_projects: Optional[int] = Field(
        None,
        description="Number of successfully completed and funded projects"
    )
    grant_eligibility_met: Optional[List[str]] = Field(
        None,
        description="Specific grant programs filmmaker qualifies for"
    )
    
    # Metadata
    metadata: Optional[DocumentMetadata] = Field(
        None,
        description="Document metadata"
    )


# ========== FILMMAKER FUNDING PROFILE (NEW - COMBINES ALL) ==========

class FilmmakerFundingProfile(BaseModel):
    """
    COMPREHENSIVE filmmaker funding profile combining all document data.
    
    This is the COMPLETE picture needed for FILMFUND grant matching.
    """
    
    # Filmmaker info
    filmmaker_name: str = Field(
        ...,
        description="Filmmaker's full name"
    )
    filmmaker_profile: Optional[FilmmakerProfile] = Field(
        None,
        description="Complete filmmaker profile from profile document"
    )
    
    # Current project
    current_project_title: str = Field(
        ...,
        description="Title of project seeking funding"
    )
    script: Optional[FilmmakerScript] = Field(
        None,
        description="Film script/project details"
    )
    
    # Financial info
    budget: Optional[BudgetDocument] = Field(
        None,
        description="Complete budget breakdown"
    )
    schedule: Optional[ProductionSchedule] = Field(
        None,
        description="Production timeline and funding needs"
    )
    
    # ===== AGGREGATED FUNDING DATA =====
    
    # Calculate total funding need
    total_budget_needed: Optional[float] = Field(
        None,
        description="Total project budget"
    )
    total_funding_secured: Optional[float] = Field(
        None,
        description="Total funding already obtained"
    )
    total_funding_gap: Optional[float] = Field(
        None,
        description="Remaining funding needed"
    )
    
    # Timeline summary
    project_urgency: Optional[str] = Field(
        None,
        description="Urgency of funding need: urgent/soon/flexible"
    )
    funding_deadline: Optional[date] = Field(
        None,
        description="Critical deadline for funding"
    )
    time_to_production: Optional[int] = Field(
        None,
        description="Days until principal photography starts"
    )
    
    # Grant matching info
    target_grant_types: Optional[List[str]] = Field(
        None,
        description="Types of grants this filmmaker should target"
    )
    grant_eligibility_summary: Optional[List[str]] = Field(
        None,
        description="Summary of grant programs filmmaker qualifies for"
    )
    filmmaker_strengths_for_grants: Optional[List[str]] = Field(
        None,
        description="What makes this filmmaker strong grant candidate"
    )
    potential_concerns_for_grants: Optional[List[str]] = Field(
        None,
        description="Any concerns that might affect grant eligibility"
    )
    
    # Recommendations
    recommended_funding_strategy: Optional[str] = Field(
        None,
        description="Recommended approach for securing funding"
    )
    priority_grant_categories: Optional[List[str]] = Field(
        None,
        description="Priority order for which grants to pursue"
    )
    
    # Metadata
    profile_created_date: Optional[date] = Field(
        None,
        description="Date this comprehensive profile was created"
    )
    profile_last_updated: Optional[date] = Field(
        None,
        description="Date profile was last updated"
    )