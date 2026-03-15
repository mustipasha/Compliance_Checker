from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any

# --- Core Data Models ---
class Evidence(BaseModel):
    text: str
    source: str = "doc"
    page: int = 0
    chunk_id: Optional[str] = None  # Added for stable citation
    relevance_score: float = 0.0
    chapter: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class EvidenceCitation(BaseModel):
    chunk_id: str
    quote: str
    why_it_matters: Optional[str] = None
    indicator_addressed: Optional[str] = None

# 1. Alignment Agent (formerly Auditor) - Finds Overlap
class AlignmentOutput(BaseModel):
    criterion_id: str
    assessment_question_answer: str = "" # New grounding check
    alignment_summary: str  # Conceptual overlap description
    key_aligned_concepts: List[str] = []
    evidence_citations: List[EvidenceCitation] = []
    assumptions: List[str] = []

# 2. Gap Agent (formerly Challenger) - Finds Divergence
class GapAnalysisOutput(BaseModel):
    criterion_id: str
    gap_summary: str # Difference in scope/framing
    missing_elements: List[str] = [] # Concepts present in EU but missing in External Standard
    weaker_areas: List[str] = [] # Areas where standard is less specific than EU
    scope_divergences: List[str] = [] # Different risk framing etc.
    alignment_overreach: List[str] = [] # Indicators falsely claimed by Alignment agent

# 3. Synthesis Agent (formerly Judge) - Neutral Arbiter
class SynthesisOutput(BaseModel):
    criterion_id: str
    assessment_question_answered: bool = False # New grounding check
    classification: Literal["COMPLIANT", "PARTIALLY_COMPLIANT", "NOT_COMPLIANT", "NOT_APPLICABLE", "NOT_EVIDENCED"]
    justification: str # Explicitly referencing rubric conditions
    key_aligned_concepts: List[str] = []
    decisive_gaps_or_divergences: List[str] = []
    tensions_or_ambiguities: List[str] = []
    confidence: float
    
    # Internal helpers
    selected_evidence: List[Evidence] = [] 

# --- API Response Models ---

class CriterionResult(BaseModel):
    criterion_id: str
    title: str
    requirement: str 
    assessment_question: str = "" # New field
    expected_evidence: List[str] = []
    status: str  # e.g., "PARTIALLY_COMPLIANT" (Rubric-based)
    score: int   # Mapped from rubric (100, 50, 0)
    confidence: float
    reasoning: str # From Synthesis justification
    key_aligned_concepts: List[str] = []
    decisive_gaps_or_divergences: List[str] = []
    tensions_or_ambiguities: List[str] = []
    
    # Detailed Breakdown
    alignment_findings: AlignmentOutput
    gap_analysis: GapAnalysisOutput
    synthesis_result: SynthesisOutput
    
    evidence: List[Evidence]

class CommitmentResult(BaseModel):
    commitment_id: str
    title: str
    results: List[CriterionResult]


class AssessmentReport(BaseModel):
    compliance_score: float
    source_document: str = "Unknown Source"
    provider: Optional[str] = None
    model: Optional[str] = None
    mode: Optional[str] = None
    # Restored commitment hierarchy for frontend compatibility
    commitments: List[CommitmentResult]
    # Keep flat list for internal use if needed, but primary is commitments
    criteria: Optional[List[CriterionResult]] = None
