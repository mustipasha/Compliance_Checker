import React from 'react';
import { Search, Compass, Target, Zap, ChevronRight, Activity } from 'lucide-react';

interface Evidence {
    text: string;
    source: string;
    page: number | string;
}

interface AlignmentOutput {
    alignment_summary: string;
    key_aligned_concepts: string[];
    evidence_citations?: any[];
    assumptions?: string[];
}

interface GapAnalysisOutput {
    gap_summary: string;
    missing_elements: string[];
}

interface SynthesisOutput {
    classification: string;
    justification: string;
    confidence: number;
}

interface CriterionResult {
    evidence: Evidence[];
    alignment_findings: AlignmentOutput;
    gap_analysis: GapAnalysisOutput;
    synthesis_result: SynthesisOutput;
}

interface WorkflowTraceProps {
    result: CriterionResult;
}

export const WorkflowTrace: React.FC<WorkflowTraceProps> = ({ result }) => {
    const steps = [
        {
            id: 'retrieval',
            title: 'Evidence Retrieval',
            icon: <Search className="w-4 h-4" />,
            description: `${result.evidence.length} context chunks retrieved from documents`,
            color: 'text-blue-500',
            bgColor: 'bg-blue-50'
        },
        {
            id: 'alignment',
            title: 'Conceptual Alignment',
            icon: <Compass className="w-4 h-4" />,
            description: `${result.alignment_findings.key_aligned_concepts.length} overlapping concepts identified`,
            color: 'text-indigo-500',
            bgColor: 'bg-indigo-50'
        },
        {
            id: 'gap',
            title: 'Gap Analysis',
            icon: <Target className="w-4 h-4" />,
            description: `${result.gap_analysis.missing_elements.length} divergence points found`,
            color: 'text-red-500',
            bgColor: 'bg-red-50'
        },
        {
            id: 'synthesis',
            title: 'Synthesis & Final Score',
            icon: <Zap className="w-4 h-4" />,
            description: `${result.synthesis_result.classification.replace(/_/g, ' ')} with ${(result.synthesis_result.confidence * 100).toFixed(0)}% confidence`,
            color: 'text-purple-500',
            bgColor: 'bg-purple-50'
        }
    ];

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-black text-gray-400 uppercase tracking-[0.2em] mb-4">
                <Activity size={14} className="text-blue-600" /> Backend Process Workflow
            </div>

            <div className="relative">
                {/* Vertical Line Connector */}
                <div className="absolute left-6 top-8 bottom-8 w-px bg-gradient-to-b from-blue-200 via-indigo-200 to-purple-200" />

                <div className="space-y-6 relative">
                    {steps.map((step, idx) => (
                        <div key={step.id} className="flex gap-4 group">
                            {/* Step Icon Container */}
                            <div className={`relative z-10 shrink-0 w-12 h-12 rounded-2xl ${step.bgColor} shadow-sm border border-white flex items-center justify-center transition-transform group-hover:scale-110 duration-300`}>
                                <div className={step.color}>
                                    {step.icon}
                                </div>
                                {idx < steps.length - 1 && (
                                    <div className="absolute top-12 left-1/2 -translate-x-1/2 flex items-center justify-center">
                                        <ChevronRight size={10} className="rotate-90 text-gray-300" />
                                    </div>
                                )}
                            </div>

                            {/* Step Content */}
                            <div className="flex-1 py-1">
                                <h4 className="text-xs font-black text-gray-800 uppercase tracking-widest mb-1 group-hover:text-blue-600 transition-colors">
                                    {step.title}
                                </h4>
                                <p className="text-xs text-gray-500 font-medium leading-relaxed">
                                    {step.description}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};
