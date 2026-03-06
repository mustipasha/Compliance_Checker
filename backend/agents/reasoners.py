from typing import List, Dict, Any
import json
from langchain_core.prompts import ChatPromptTemplate
from api.models import Evidence, AlignmentOutput, GapAnalysisOutput
from agents.prompts import ALIGNMENT_PROMPT, GAP_PROMPT

from core.resilience import robust_invoke
from core.llm_config import get_llm


class BaseAgent:
    def __init__(self, prompt_template: str, provider: str = None, model: str = None):
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        llm = get_llm(temperature=0, provider=provider, model=model)
        self.chain = self.prompt | llm

    def _clean_json(self, response) -> str:
        content = response.content
        if isinstance(content, list):
            content = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in content])
        
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Simple heuristic to fix common JSON errors (like missing commas between fields)
        # This is very basic: if we see "key": preceded by ", or ] or } without a comma, we might be able to help.
        # However, it's safer to just return as is if it fails.
        return content

class AlignmentAgent(BaseAgent):
    """
    Agent 1: Alignment Analyzer.
    Identifies conceptual overlap between external standard and EU requirement.
    """
    def __init__(self, provider: str = None, model: str = None):
        super().__init__(ALIGNMENT_PROMPT, provider=provider, model=model)

    async def run(self, criterion: Dict, evidence: List[Evidence]) -> AlignmentOutput:
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
            
            content = self._clean_json(response)
            data = json.loads(content)
            return AlignmentOutput(**data)
            
        except Exception as e:
            print(f"Alignment Agent Error: {e}")
            return AlignmentOutput(
                criterion_id=criterion.get('id', 'unknown'),
                alignment_summary=f"Analysis Failed: {str(e)}",
                key_aligned_concepts=[],
                evidence_citations=[],
                assumptions=[]
            )


class GapAgent(BaseAgent):
    """
    Agent 2: Gap Analyzer.
    Identifies missing elements or divergences.
    """
    def __init__(self, provider: str = None, model: str = None):
        super().__init__(GAP_PROMPT, provider=provider, model=model)

    async def run(self, criterion: Dict, evidence: List[Evidence], alignment_output: AlignmentOutput) -> GapAnalysisOutput:
        evidence_text = "\n\n".join([f"[{e.chunk_id}] {e.text}" for i, e in enumerate(evidence)])
        
        try:
            response = await robust_invoke(self.chain, {
                "criterion_requirement": criterion['requirement'],
                "alignment_json": alignment_output.model_dump_json(indent=2),
                "evidence_text": evidence_text,
                "criterion_id": criterion.get('id', 'unknown')
            })
            
            content = self._clean_json(response)
            data = json.loads(content)
            return GapAnalysisOutput(**data)
            
        except Exception as e:
            print(f"Gap Agent Error: {e}")
            return GapAnalysisOutput(
                criterion_id=criterion.get('id', 'unknown'),
                gap_summary=f"Analysis Failed: {str(e)}",
                missing_elements=[],
                weaker_areas=[],
                scope_divergences=[]
            )
