from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query (e.g., restaurants)")
    city: str = Field(..., min_length=1, description="City name")
    state: str = Field(..., min_length=1, description="State abbreviation")
    zipCode: Optional[str] = Field(None, description="Zip code (optional)")
    maxResults: int = Field(20, ge=1, le=100, description="Maximum number of results")

class LeadResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    businessName: str
    businessType: str
    address: str
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None
    reviewCount: Optional[int] = None
    searchId: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SearchRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    city: str
    state: str
    zipCode: Optional[str] = None
    maxResults: int
    status: str = Field(default="completed")
    results_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmailEnrichmentRequest(BaseModel):
    leadId: str = Field(..., description="Lead ID to enrich")
    website: str = Field(..., description="Website URL for email discovery")

class DashboardStats(BaseModel):
    totalLeads: int
    totalSearches: int
    avgConversion: float
    emailsEnriched: int
    recentSearches: List[dict]