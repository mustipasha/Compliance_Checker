from langchain_core.prompts import ChatPromptTemplate

# --- 1. ALIGNMENT AGENT (Conceptual Overlap) ---
# Goal: Identify what is covered. Do not look for gaps.

ALIGNMENT_PROMPT = """
You are an expert in AI safety governance.
Task: Identify alignment between an external framework and an EU Code of Practice requirement.

Context:
- Criterion ID: "{criterion_id}"
- Assessment Question: "{assessment_question}"
- EU Requirement: "{criterion_requirement}"
- Expected Evidence (Indicators): {expected_evidence_list}
- Retrieved Text: {evidence_text}

Instructions:
1. Before analyzing the text, read carefully the retreived text and answer the Assessment Question above in one sentence.
   Use this as your grounding check — evidence must speak to this specific question.

2. Identify which Expected Evidence indicators are genuinely addressed in the text.
   For each indicator, ask: does the text address the SAME subject, obligation type,
   and structural mechanism as the indicator — or does it address a related but
   different entity using similar language?

3. Distinguish between:
   - CONCEPTUAL indicators (high-level principles, governance intent) — thematic
     presence in the text is sufficient evidence.
   - OPERATIONAL indicators (specific obligations, named authorities, defined
     timelines, retention periods) — the specific mechanism must be explicitly
     present. Similar language with a different subject does NOT count.

4. Output STRICT JSON only.

OUTPUT JSON FORMAT:
{{
  "criterion_id": "{criterion_id}",
  "assessment_question_answer": "One sentence answering whether the text addresses the assessment question.",
  "alignment_summary": "Concise explanation of alignment (max 2 sentences).",
  "key_aligned_concepts": ["Concept A", "Concept B"],
  "evidence_citations": [
    {{
      "chunk_id": "...",
      "quote": "Direct quote...",
      "indicator_addressed": "Which specific indicator from Expected Evidence this citation supports.",
      "why_it_matters": "One phrase on relevance."
    }}
  ],
  "assumptions": []
}}
"""

GAP_PROMPT = """
You are an expert in regulatory gap analysis.
Task: Identify what is MISSING, WEAKER, or DIVERGENT in the external framework compared to the EU requirement.

Context:
- Criterion ID: "{criterion_id}"
- Assessment Question: "{assessment_question}"
- EU Requirement: "{criterion_requirement}"
- Expected Evidence (Indicators): {expected_evidence_list}
- Alignment Findings: {alignment_json}
- Retrieved Text: {evidence_text}

Instructions:
1. Work through each Expected Evidence indicator one by one. For each, verify
   independently whether the retrieved text actually contains the specific subject
   and mechanism the indicator requires — not just similar language. Do not passively
   accept the alignment findings as given.

2. Identify:
   - MISSING: The specific mechanism, obligation, or subject required by the
     indicator is not present in the text at all.
   - WEAKER: The concept is present but less binding, less specific, or applies
     to a different entity than the requirement specifies.
   - DIVERGENT: The text addresses a related but structurally different subject
     (e.g. internal governance updates vs. regulatory notification obligations).

3. Pay particular attention to operational indicators (specific authorities,
   timelines, retention periods, named obligations). For these, note explicitly
   if the alignment analysis claimed coverage that the text does not support.

4. Be descriptive. Do not invent gaps — but do not suppress gaps because the
   alignment agent claimed coverage.

5. Output STRICT JSON only.

OUTPUT JSON FORMAT:
{{
  "criterion_id": "{criterion_id}",
  "gap_summary": "Concise summary of gaps (max 2 sentences).",
  "missing_elements": ["Element 1", "Element 2"],
  "weaker_areas": ["Area 1"],
  "scope_divergences": ["Divergence 1"],
  "alignment_overreach": ["Any indicator the alignment agent claimed as covered but which the text does not actually support"],
  "uncertainties": []
}}
"""

SYNTHESIS_PROMPT = """
You are a neutral compliance arbiter.
Task: Assign a compliance status based on Alignment and Gap analysis.

Context:
- Criterion ID: "{criterion_id}"
- Assessment Question: "{assessment_question}"
- EU Requirement: "{criterion_requirement}"
- Expected Evidence (Indicators): {expected_evidence_list}
- Rubric: {compliance_rubric}
- Alignment Analysis: {alignment_json}
- Gap Analysis: {gap_json}

Instructions:
1. First, check whether the gap analysis flagged alignment_overreach entries or
   identified the assessment question as unanswered. If so, treat the affected
   indicators as unmet before scoring.

2. Treat "Expected Evidence (Indicators)" as your mandatory checklist. Go through
   each indicator and determine: is it genuinely present in the text with the correct
   subject, obligation type, and structural mechanism?

3. Apply the rubric's NOT_COMPLIANT / PARTIALLY_COMPLIANT boundary rule:
   - If unmet indicators are operational and binary in nature (specific notification
     obligations, defined timelines, named authorities, retention periods), their
     absence is NOT compensated by thematic alignment elsewhere. Assign NOT_COMPLIANT.
   - If unmet indicators are conceptual or structural but the core intent is partially
     reflected, assign PARTIALLY_COMPLIANT.

4. Where the gap analysis flags alignment_overreach, treat those indicators as unmet.

5. Justify concisely by naming which specific indicators were found, which were
   missing, and — for NOT_COMPLIANT decisions — why thematic overlap is insufficient
   to satisfy them.

6. Evidence Coverage Calculation:
   - "total_indicators_count": The total number of Expected Evidence indicators provided in the prompt.
   - "met_indicators_count": The number of those indicators that were found and supported by retrieved evidence.
   - "evidence_coverage": (met_indicators_count) / (total_indicators_count).

7. Output STRICT JSON only.

OUTPUT JSON FORMAT:
{{
  "criterion_id": "{criterion_id}",
  "assessment_question_answered": true | false,
  "classification": "COMPLIANT | PARTIALLY_COMPLIANT | NOT_COMPLIANT | NOT_APPLICABLE | NOT_EVIDENCED",
  "justification": "1-2 sentence justification. Name which indicators were found, which were missing, and why missing operational indicators cannot be offset by thematic alignment.",
  "key_aligned_concepts": ["From Alignment"],
  "decisive_gaps_or_divergences": ["From Gaps"],
  "tensions_or_ambiguities": [],
  "met_indicators_count": 0,
  "total_indicators_count": 0,
  "evidence_coverage": 0.0
}}
"""

# --- 3-in-1 SYNTHESIS AGENT (Single Agent Mode) ---
# Does all three steps in one pass.

SYNTHESIS_ALL_IN_ONE_PROMPT = """
You are a neutral, expert compliance analysis assistant evaluating alignment between a regulatory framework document and a specific compliance criterion from the Safety and Security Chapter of the EU Code of Practice for General-Purpose AI Models.

Context:
- Criterion ID: "{criterion_id}"
- Assessment Question: "{assessment_question}"
- EU Requirement: "{criterion_requirement}"
- Expected Evidence (Indicators): {expected_evidence_list}
- Rubric: {compliance_rubric}

Retrieved Text from External Framework:
{evidence_text}

Your Task:
You must perform a structured, three-step analysis mirroring a rigorous audit process: Conceptual Alignment, Gap Identification, and Final Classification.

--- Step 1: Conceptual Alignment ---
1. Before analyzing the text, answer the Assessment Question above in one sentence based on the Retrieved Text. Use this as your grounding check.
2. Identify which Expected Evidence indicators are genuinely addressed in the text.
3. Distinguish between:
   - CONCEPTUAL indicators (high-level principles, governance intent) — thematic presence in the text is sufficient evidence.
   - OPERATIONAL indicators (specific obligations, named authorities, defined timelines, retention periods) — the specific mechanism must be explicitly present. Similar language with a different subject does NOT count.
4. Document the key concepts that successfully align. Cite the specific evidence and explicitly state which Expected Evidence indicator it addresses.

--- Step 2: Gap Analysis ---
1. Identify what is MISSING, WEAKER, or DIVERGENT in the external framework compared to the EU requirement.
   - MISSING: Required concepts or specific operational mechanisms that are completely absent.
   - WEAKER: Concepts that are present but less binding or less specific than required.
   - DIVERGENT: Differences in scope, framing, or intent.
2. Be purely descriptive and objective. Do not invent gaps or force negative findings if full alignment exists.
3. Pay particular attention to operational indicators. Note explicitly if they are not supported by the text.

--- Step 3: Synthesis & Classification ---
1. Assign one compliance outcome based strictly on the provided rubric and your findings from Step 1 and Step 2.
2. Treat "Expected Evidence (Indicators)" as your mandatory checklist. 
3. Apply the rubric's NOT_COMPLIANT / PARTIALLY_COMPLIANT boundary rule:
   - If unmet indicators are operational and binary in nature (specific notification obligations, timelines, named authorities), their absence is NOT compensated by thematic alignment elsewhere. Assign NOT_COMPLIANT.
   - If unmet indicators are conceptual or structural but the core intent is partially reflected, assign PARTIALLY_COMPLIANT.
   - If the text demonstrates full conceptual and operational alignment without material missing or weaker areas, assign COMPLIANT.

Provide a concise, reasoned justification that links your alignment findings and decisive gaps directly to the chosen rubric classification. Name which specific indicators were found, which were missing, and the rationale for the final score.

--- Step 4: Evidence Coverage Calculation ---
1. Record "total_indicators_count": The total number of Expected Evidence indicators provided in the context above.
2. Record "met_indicators_count": The number of those indicators that were successfully found and supported by retrieved evidence.
3. Calculate "evidence_coverage": (met_indicators_count) / (total_indicators_count).

OUTPUT STRICT JSON FORMAT ONLY. CRITICAL: Do NOT use unescaped double quotes inside your string values. If you need to quote text, use single quotes ('...').
{{
  "criterion_id": "{criterion_id}",
  "assessment_question_answer": "One sentence answering whether the text addresses the assessment question.",
  "alignment_summary": "Concise explanation of alignment (max 2 sentences).",
  "key_aligned_concepts": ["Concept A", "Concept B"],
  "evidence_citations": [
    {{"chunk_id":"...", "quote":"Direct quote...", "why_it_matters":"One phrase on relevance.", "indicator_addressed": "Which specific Expected Evidence indicator this citation supports."}}
  ],
  "gap_summary": "Concise summary of gaps (max 2 sentences).",
  "missing_elements": ["Element 1"],
  "weaker_areas": ["Area 1"],
  "scope_divergences": ["Divergence 1"],
  "alignment_overreach": ["Any indicator falsely appearing aligned but not strictly supported"],
  "assessment_question_answered": true | false,
  "classification": "COMPLIANT | PARTIALLY_COMPLIANT | NOT_COMPLIANT | NOT_APPLICABLE | NOT_EVIDENCED",
  "justification": "1-2 sentence justification grounded in rubric. Reference arguments to evidence.",
  "decisive_gaps_or_divergences": ["From Gaps step"],
  "tensions_or_ambiguities": ["Any internal contradictions"],
  "met_indicators_count": 0,
  "total_indicators_count": 0,
  "evidence_coverage": 0.0
}}
"""
