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
    print(f"DEBUG: [{criterion.get('id')}] Starting retrieval...")
    keywords = criterion.get("extracted_keywords") or criterion.get("keywords", [])
    query = criterion['assessment_question']
    if keywords:
        query += " " + " ".join(keywords)
    
    evidence = await retrieve_evidence(query)
    print(f"DEBUG: [{criterion.get('id')}] Retrieval complete: {len(evidence)} chunks.")
    
    # 2. Agent Execution (create agents with the selected LLM)
    alignment_result = None
    gap_result = None
    synthesis_result = None

    # Determine reasoning path
    if mode == "single":
        print(f"DEBUG: [{criterion.get('id')}] Running Single Agent mode...")
        agent = SynthesisAllInOneAgent(provider=provider, model=model)
        results = await agent.run(criterion, evidence)
        
        alignment_result = results['alignment']
        gap_result = results['gap']
        synthesis_result = results['synthesis']
        print(f"DEBUG: [{criterion.get('id')}] Single Agent complete.")
        
    else:
        print(f"DEBUG: [{criterion.get('id')}] Running Triple Agent mode...")
        a_agent = AlignmentAgent(provider=provider, model=model)
        g_agent = GapAgent(provider=provider, model=model)
        s_agent = SynthesisAgent(provider=provider, model=model)

        # Step A: Alignment
        print(f"DEBUG: [{criterion.get('id')}] Running Alignment...")
        alignment_result = await a_agent.run(criterion, evidence)
        
        # Step B: Gap Analysis
        print(f"DEBUG: [{criterion.get('id')}] Running Gap Analysis...")
        gap_result = await g_agent.run(criterion, evidence, alignment_result)
        
        # Step C: Synthesis
        print(f"DEBUG: [{criterion.get('id')}] Running Synthesis...")
        rubric_json = json.dumps(criterion.get("compliance_rubric", {}), indent=2)
        synthesis_result = await s_agent.synthesize(criterion, evidence, alignment_result, gap_result, rubric_json)
        print(f"DEBUG: [{criterion.get('id')}] Triple Agent complete.")

    # 3. Final Result Construction
    print(f"DEBUG: [{criterion.get('id')}] Constructing CriterionResult...")
    score_map = {
        "COMPLIANT": 100,
        "PARTIALLY_COMPLIANT": 50,
        "NOT_COMPLIANT": 0,
        "NOT_APPLICABLE": 0,
        "NOT_EVIDENCED": 0
    }
    
    final_status = synthesis_result.classification
    final_score = score_map.get(final_status, 0)

    res = CriterionResult(
        criterion_id=criterion.get('id', 'unknown'),
        title=criterion.get('title', ''),
        requirement=criterion.get('requirement', ''),
        assessment_question=criterion.get('assessment_question', ''),
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
    print(f"DEBUG: [{criterion.get('id')}] CriterionResult constructed.")
    return res
