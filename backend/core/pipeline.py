import asyncio
import json
from typing import Dict, List, Optional
from api.models import (
    CriterionResult, Evidence, 
    AlignmentOutput, GapAnalysisOutput, SynthesisOutput
)
from core.retrieval import retrieve_evidence
from agents.reasoners import AlignmentAgent, GapAgent
from agents.judge import SynthesisAgent, SynthesisAllInOneAgent

# --- CONFIGURATION ---
# Set to True to run the "All-in-One" Synthesis Agent (Fast).
# Set to False to run the full 3-agent pipeline (Alignment -> Gap -> Synthesis).
SINGLE_AGENT_MODE = True
# ---------------------

async def run_compliance_check(criterion: Dict, provider: str = None, model: str = None, mode: str = "single") -> CriterionResult:
    """
    Runs the conceptual alignment pipeline.
    provider/model: Optional LLM overrides (falls back to env vars).
    mode: "single" or "triple" reasoning pipeline.
    """
    # 1. Retrieve Evidence
    keywords = criterion.get("extracted_keywords") or criterion.get("keywords", [])
    query = criterion['requirement']
    if keywords:
        query += " " + " ".join(keywords)
        
    evidence = await retrieve_evidence(query)
    
    # 2. Agent Execution (create agents with the selected LLM)
    alignment_result = None
    gap_result = None
    synthesis_result = None

    # Determine reasoning path
    if mode == "single":
        agent = SynthesisAllInOneAgent(provider=provider, model=model)
        results = await agent.run(criterion, evidence)
        
        alignment_result = results['alignment']
        gap_result = results['gap']
        synthesis_result = results['synthesis']
        
    else:
        a_agent = AlignmentAgent(provider=provider, model=model)
        g_agent = GapAgent(provider=provider, model=model)
        s_agent = SynthesisAgent(provider=provider, model=model)

        # Step A: Alignment
        alignment_result = await a_agent.run(criterion, evidence)
        
        # Step B: Gap Analysis
        gap_result = await g_agent.run(criterion, evidence, alignment_result)
        
        # Step C: Synthesis
        rubric_json = json.dumps(criterion.get("compliance_rubric", {}), indent=2)
        synthesis_result = await s_agent.synthesize(criterion, evidence, alignment_result, gap_result, rubric_json)

    # 3. Final Result Construction
    score_map = {
        "COMPLIANT": 100,
        "PARTIALLY_COMPLIANT": 50,
        "NOT_COMPLIANT": 0,
        "NOT_APPLICABLE": 0,
        "NOT_EVIDENCED": 0
    }
    
    final_status = synthesis_result.classification
    final_score = score_map.get(final_status, 0)

    return CriterionResult(
        criterion_id=criterion.get('id', 'unknown'),
        title=criterion.get('title', ''),
        requirement=criterion.get('requirement', ''),
        expected_evidence=criterion.get('expected_evidence', []),
        status=final_status,
        score=final_score,
        confidence=synthesis_result.confidence,
        reasoning=synthesis_result.justification,
        key_aligned_concepts=synthesis_result.key_aligned_concepts if hasattr(synthesis_result, 'key_aligned_concepts') else [],
        decisive_gaps_or_divergences=synthesis_result.decisive_gaps_or_divergences if hasattr(synthesis_result, 'decisive_gaps_or_divergences') else [],
        tensions_or_ambiguities=synthesis_result.tensions_or_ambiguities,
        
        alignment_findings=alignment_result,
        gap_analysis=gap_result,
        synthesis_result=synthesis_result,
        
        evidence=evidence
    )
