import json
from typing import Dict, List, Optional, Any
from langchain_core.prompts import ChatPromptTemplate
from api.models import (
    AlignmentOutput, 
    GapAnalysisOutput, 
    SynthesisOutput, 
    Evidence, 
    EvidenceCitation
)
from agents.prompts import SYNTHESIS_PROMPT, SYNTHESIS_ALL_IN_ONE_PROMPT
from core.resilience import robust_invoke
from core.llm_config import get_llm
from core.json_utils import clean_and_parse_json


class SynthesisAgent:
    """
    Agent 3: Neutral Arbiter.
    Synthesizes Alignment and Gap findings into a final classification.
    """
    def __init__(self, provider: str = None, model: str = None):
        self.prompt = ChatPromptTemplate.from_template(SYNTHESIS_PROMPT)
        llm = get_llm(temperature=0, provider=provider, model=model)
        self.chain = self.prompt | llm

    def _parse_response(self, response: Any) -> Dict:
        return clean_and_parse_json(response.content)

    async def synthesize(self, 
                         criterion: Dict, 
                         evidence: List[Evidence], 
                         alignment_output: AlignmentOutput, 
                         gap_output: GapAnalysisOutput,
                         compliance_rubric_json: str) -> SynthesisOutput:
        
        try:
            # Format Expected Evidence
            expected_ev = criterion.get('expected_evidence', [])
            if isinstance(expected_ev, list):
                expected_ev_text = "\n".join([f"- {item}" for item in expected_ev])
            else:
                expected_ev_text = str(expected_ev)

            response = await robust_invoke(self.chain, {
                "criterion_requirement": criterion['requirement'],
                "assessment_question": criterion.get('assessment_question', ''),
                "expected_evidence_list": expected_ev_text,
                "alignment_json": alignment_output.model_dump_json(indent=2),
                "gap_json": gap_output.model_dump_json(indent=2),
                "criterion_id": criterion.get('id', 'unknown'),
                "compliance_rubric": compliance_rubric_json
            })
            
            data = self._parse_response(response)
            
            # Ensure confidence is a float
            if 'confidence' in data:
                data['confidence'] = float(data['confidence'])
                
            result = SynthesisOutput(**data)
            
            # Helper to attach evidence for easier UI rendering later
            result.selected_evidence = evidence[:5]
            
            return result
            
        except Exception as e:
            print(f"Synthesis Agent Error: {e}")
            return SynthesisOutput(
                criterion_id=criterion.get('id', 'unknown'),
                classification="NOT_APPLICABLE",
                justification=f"Synthesis Error: {str(e)}",
                key_aligned_concepts=[],
                decisive_gaps_or_divergences=[],
                tensions_or_ambiguities=[],
                confidence=0.0,
                selected_evidence=[]
            )


class SynthesisAllInOneAgent:
    """
    Single Agent Mode: 3-in-1.
    Performs Alignment, Gap, and Synthesis in one go.
    """
    def __init__(self, provider: str = None, model: str = None):
        self.prompt = ChatPromptTemplate.from_template(SYNTHESIS_ALL_IN_ONE_PROMPT)
        llm = get_llm(temperature=0, provider=provider, model=model)
        self.chain = self.prompt | llm

    def _parse_response(self, response: Any) -> Dict:
        return clean_and_parse_json(response.content)

    async def run(self, criterion: Dict, evidence: List[Evidence]) -> Dict[str, Any]:
        """
        Returns a dictionary containing all three output types to mimic the full pipeline.
        """
        evidence_text = "\n\n".join([f"[{e.chunk_id}] {e.text}" for i, e in enumerate(evidence)])
        
        # Format Expected Evidence
        expected_ev = criterion.get('expected_evidence', [])
        if isinstance(expected_ev, list):
            expected_ev_text = "\n".join([f"- {item}" for item in expected_ev])
        else:
            expected_ev_text = str(expected_ev)

        try:
            response = await robust_invoke(self.chain, {
                "criterion_id": criterion.get('id', 'unknown'),
                "criterion_requirement": criterion['requirement'],
                "expected_evidence_list": expected_ev_text,
                "evidence_text": evidence_text
            })
            
            data = self._parse_response(response)
            
            alignment = AlignmentOutput(
                criterion_id=data['criterion_id'],
                assessment_question_answer=data.get('assessment_question_answer', ''),
                alignment_summary=data.get('alignment_summary', ''),
                key_aligned_concepts=data.get('key_aligned_concepts', []),
                evidence_citations=data.get('evidence_citations', []),
                assumptions=[]
            )
            
            gap = GapAnalysisOutput(
                criterion_id=data['criterion_id'],
                gap_summary=data.get('gap_summary', ''),
                missing_elements=data.get('missing_elements', []),
                weaker_areas=data.get('weaker_areas', []),
                scope_divergences=data.get('scope_divergences', []),
                alignment_overreach=data.get('alignment_overreach', [])
            )
            
            synthesis = SynthesisOutput(
                criterion_id=data['criterion_id'],
                assessment_question_answered=data.get('assessment_question_answered', False),
                classification=data.get('classification', 'NOT_APPLICABLE'),
                justification=data.get('justification', ''),
                key_aligned_concepts=data.get('key_aligned_concepts', []),
                decisive_gaps_or_divergences=data.get('decisive_gaps_or_divergences', []),
                tensions_or_ambiguities=data.get('tensions_or_ambiguities', []),
                confidence=float(data.get('confidence', 0.0)),
                selected_evidence=evidence[:5]
            )
            
            return {
                "alignment": alignment,
                "gap": gap,
                "synthesis": synthesis
            }
            
        except Exception as e:
            print(f"All-In-One Agent Error: {e}")
            criterion_id = criterion.get('id', 'unknown')
            return {
                "alignment": AlignmentOutput(
                    criterion_id=criterion_id, 
                    alignment_summary=f"Analysis Failed: {str(e)}",
                    key_aligned_concepts=[],
                    evidence_citations=[],
                    assumptions=[]
                ),
                "gap": GapAnalysisOutput(
                    criterion_id=criterion_id, 
                    gap_summary="Error",
                    missing_elements=[],
                    weaker_areas=[],
                    scope_divergences=[]
                ),
                "synthesis": SynthesisOutput(
                    criterion_id=criterion_id, 
                    classification="NOT_APPLICABLE", 
                    justification=str(e), 
                    key_aligned_concepts=[],
                    decisive_gaps_or_divergences=[],
                    tensions_or_ambiguities=[],
                    confidence=0.0,
                    selected_evidence=[]
                )
            }
