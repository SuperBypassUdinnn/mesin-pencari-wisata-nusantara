"""Pydantic request and response schemas for the wisata search engine API.

Defines the data contracts for search queries and results, Rocchio relevance
feedback, preprocessing inspection, posting list inspection, and evaluation
benchmarks returned by the REST endpoints.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    """A single ranked search result returned to the client."""

    rank: int = Field(description="1-based position in the result list")
    score: Optional[float] = Field(default=None, description="Retrieval score from the engine")
    title: str = Field(default="", description="Document title")
    snippet: str = Field(default="", description="Highlighted or fallback snippet")
    url: str = Field(default="", description="Document URL")
    badges: Dict[str, str] = Field(default_factory=dict, description="Source, location, and category badges")


class SearchResponse(BaseModel):
    """Response envelope for a single-model search query."""

    query: str
    model: str
    index: Optional[str] = None
    top_k: int = 10
    latency_ms: Optional[float] = None
    total: int = 0
    total_hits: int = 0
    results: List[SearchResultItem] = Field(default_factory=list)


class RocchioFeedbackRequest(BaseModel):
    """Request body for the Rocchio relevance feedback endpoint."""

    query: str = Field(description="Original user query")
    relevant_doc_ids: List[str] = Field(default_factory=list, description="Relevant document IDs")
    non_relevant_doc_ids: List[str] = Field(default_factory=list, description="Non-relevant document IDs")
    alpha: float = Field(default=1.0, description="Original query weight")
    beta: float = Field(default=0.75, description="Relevant feedback weight")
    gamma: float = Field(default=0.15, description="Non-relevant feedback weight")


class RocchioFeedbackResponse(BaseModel):
    """Response envelope for Rocchio relevance feedback."""

    original_query: str
    weights: Dict[str, float] = Field(default_factory=dict)
    results: List[SearchResultItem] = Field(default_factory=list)


class InspectPreprocessingResponse(BaseModel):
    """Step-by-step preprocessing inspection report for a single text."""

    raw: str
    case_folded: str
    cleaned: str
    tokens: List[str]
    filtered: List[str]
    stemmed: List[str]


class PostingListResponse(BaseModel):
    """Posting list statistics for a term in an index."""

    index: str
    field: str
    term: str
    df: int = Field(description="Document frequency")
    tf: int = Field(description="Total term frequency")
    postings: List[Dict[str, Any]] = Field(default_factory=list)


class EvaluationResponse(BaseModel):
    """Structured evaluation benchmark response."""

    available: bool = False
    source: str = ""
    benchmarks: List[Dict[str, Any]] = Field(default_factory=list)
    note: str = ""
