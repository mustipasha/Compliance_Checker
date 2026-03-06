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


class SynthesisAgent:
    """
    Agent 3: Neutral Arbiter.
    Synthesizes Alignment and Gap findings into a final classification.
    """
    def __init__(self, provider: str = None, model: str = None):
        self.prompt = ChatPromptTemplate.from_template(SYNTHESIS_PROMPT)
        llm = get_llm(temperature=0, provider=provider, model=model)
        self.chain = self.prompt | llm

    def _clean_json(self, response) -> str:
        content = response.content
        if isinstance(content, list):
            content = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
            
        import re
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        return content.strip()

    async def synthesize(self, 
                         criterion: Dict, 
                         evidence: List[Evidence], 
                         alignment_output: AlignmentOutput, 
                         gap_output: GapAnalysisOutput,
                         compliance_rubric_json: str) -> SynthesisOutput:
        
        try:
            response = await robust_invoke(self.chain, {
                "criterion_requirement": criterion['requirement'],
                "alignment_json": alignment_output.model_dump_json(indent=2),
                "gap_json": gap_output.model_dump_json(indent=2),
                "criterion_id": criterion.get('id', 'unknown'),
                "compliance_rubric_json": compliance_rubric_json
            })
            
            from langchain_core.utils.json import parse_json_markdown
            
            try:
                content = self._clean_json(response)
                data = json.loads(content)
            except json.JSONDecodeError:
                raw_content = response.content
                if isinstance(raw_content, list):
                    raw_content = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in raw_content])
                data = parse_json_markdown(raw_content)
            
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

    def _clean_json(self, response) -> str:
        content = response.content
        if isinstance(content, list):
            content = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
            
        import re
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        return content.strip()

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
            
            from langchain_core.utils.json import parse_json_markdown
            
            try:
                # Try standard parsing first after cleaning
                content = self._clean_json(response)
                data = json.loads(content)
            except json.JSONDecodeError:
                # Fallback to robust langchain parser
                # Need the raw content for parse_json_markdown to work best
                raw_content = response.content
                if isinstance(raw_content, list):
                    raw_content = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in raw_content])
                data = parse_json_markdown(raw_content)
            
            alignment = AlignmentOutput(
                criterion_id=data['criterion_id'],
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
                scope_divergences=data.get('scope_divergences', [])
            )
            
            synthesis = SynthesisOutput(
                criterion_id=data['criterion_id'],
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
            return {
                "alignment": AlignmentOutput(criterion_id=criterion.get('id'), alignment_summary="Error", evidence_citations=[]),
                "gap": GapAnalysisOutput(criterion_id=criterion.get('id'), gap_summary="Error"),
                "synthesis": SynthesisOutput(criterion_id=criterion.get('id'), classification="NOT_APPLICABLE", justification=str(e), confidence=0.0)
            }
