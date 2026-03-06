import React, { useState } from 'react';
import { FileText, Database, Cpu, CheckCircle, X, ArrowRight, Zap } from 'lucide-react';

export const ProcessLifecycle: React.FC = () => {
    const [selectedStep, setSelectedStep] = useState<string | null>(null);

    const steps = [
        {
            id: 'intake',
            icon: <FileText className="w-6 h-6" />,
            title: 'Document Intake',
            shortDesc: 'Parsing & extraction',
            color: 'blue',
            angle: 0,
            details: {
                subtitle: 'Raw Data Processing',
                points: [
                    'PDF/Text parsing via specialized extractors',
                    'Metadata isolation (headers, footers, page IDs)',
                    'Text cleaning and normalization for LLM readiness',
                    'Automatic language detection and encoding check'
                ],
                tech: 'PyMuPDF | Tesseract | LangChain Parsers'
            }
        },
        {
            id: 'rag',
            icon: <Database className="w-6 h-6" />,
            title: 'RAG Indexing',
            shortDesc: 'Vector context retrieval',
            color: 'indigo',
            angle: 90,
            details: {
                subtitle: 'Vector Space Management',
                points: [
                    'Semantic chunking (800-1500 tokens with overlap)',
                    'Embedding generation using high-dim models',
                    'Vector database storage for sub-second lookup',
                    'Bi-encoder architecture for precise context matching'
                ],
                tech: 'FAISS | OpenAI Embeddings | ChromaDB'
            }
        },
        {
            id: 'reasoning',
            icon: <Cpu className="w-6 h-6" />,
            title: 'Agentic Reasoning',
            shortDesc: 'Multi-agent evaluation',
            color: 'purple',
            angle: 180,
            details: {
                subtitle: 'Multi-Agent Orchestration',
                points: [
                    'Alignment Agent: Searches for positive compliance evidence',
                    'Gap Agent: Strategically hunts for missing controls',
                    'Synthesis Agent: Weighs conflicting evidence and judges',
                    'JSON-structured reasoning feedback loops'
                ],
                tech: 'GPT-4o | Specialized Agentic Prompts'
            }
        },
        {
            id: 'validation',
            icon: <CheckCircle className="w-6 h-6" />,
            title: 'Validation & Scoring',
            shortDesc: 'Final report generation',
            color: 'teal',
            angle: 270,
            details: {
                subtitle: 'Traceability & Output',
                points: [
                    'Precise citation mapping to source document segments',
                    'Weighted scoring across 32 compliance criteria',
                    'Final report compilation with confidence metrics',
                    'Historical record versioning for audit trails'
                ],
                tech: 'jsPDF | Custom Scoring Algorithms'
            }
        }
    ];

    const currentStep = steps.find(s => s.id === selectedStep);

    // Tailwind Safelist/Lookup for dynamic colors
    const colorMap: Record<string, { bg: string, text: string, border: string, bgLight: string, shadow: string, button: string }> = {
        blue: { bg: 'bg-blue-600', text: 'text-blue-600', border: 'border-blue-500', bgLight: 'bg-blue-50', shadow: 'shadow-blue-200', button: 'bg-blue-600' },
        indigo: { bg: 'bg-indigo-600', text: 'text-indigo-600', border: 'border-indigo-500', bgLight: 'bg-indigo-50', shadow: 'shadow-indigo-200', button: 'bg-indigo-600' },
        purple: { bg: 'bg-purple-600', text: 'text-purple-600', border: 'border-purple-500', bgLight: 'bg-purple-50', shadow: 'shadow-purple-200', button: 'bg-purple-600' },
        teal: { bg: 'bg-teal-600', text: 'text-teal-600', border: 'border-teal-500', bgLight: 'bg-teal-50', shadow: 'shadow-teal-200', button: 'bg-teal-600' }
    };

    return (
        <div className="flex flex-col items-center gap-8 w-full max-w-5xl mx-auto py-8">
            {/* User Guidance Banner */}
            {!selectedStep && (
                <div className="flex items-center gap-3 px-6 py-3 bg-blue-50 border border-blue-100 rounded-2xl animate-bounce">
                    <Zap className="w-4 h-4 text-blue-600" />
                    <p className="text-sm font-bold text-blue-900">
                        Please click on the icons to see what actually is done in each stage
                    </p>
                </div>
            )}

            <div className="relative w-full flex flex-col md:flex-row items-center justify-center gap-12 p-8 transition-all duration-700 min-h-[500px]">
                {/* Diagram Side */}
                <div className={`relative aspect-square w-full max-w-[400px] flex items-center justify-center transition-all duration-500 ${selectedStep ? 'md:w-1/2 scale-90' : 'w-full'}`}>
                    {/* Background Rings */}
                    <div className="absolute inset-0 border-[1px] border-dashed border-gray-200 rounded-full animate-[spin_60s_linear_infinite]" />
                    <div className="absolute inset-16 border-[1px] border-gray-100 rounded-full shadow-inner" />

                    {/* Center Core */}
                    <div
                        className="relative z-10 w-24 h-24 bg-white rounded-full shadow-xl flex items-center justify-center border border-gray-100 cursor-pointer group"
                        onClick={() => setSelectedStep(null)}
                    >
                        <div className="absolute inset-0 bg-blue-500/5 rounded-full blur-xl group-hover:bg-blue-500/10 transition-colors" />
                        <div className="text-center">
                            <span className="text-[10px] font-black uppercase tracking-widest text-blue-600 block">Core</span>
                            <div className="flex items-center justify-center gap-1">
                                <span className="text-xs font-bold text-gray-900">Flow</span>
                                {selectedStep && <X size={10} className="text-gray-400" />}
                            </div>
                        </div>
                    </div>

                    {/* Connecting Paths (SVG) */}
                    <svg className="absolute inset-0 w-full h-full -rotate-45 pointer-events-none">
                        <circle
                            cx="50%"
                            cy="50%"
                            r="35%"
                            fill="none"
                            stroke="url(#gradient-path)"
                            strokeWidth="2"
                            strokeDasharray="8 12"
                            className="opacity-20 translate-x-0.5 translate-y-0.5"
                        />
                        <defs>
                            <linearGradient id="gradient-path" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stopColor="#3b82f6" />
                                <stop offset="50%" stopColor="#8b5cf6" />
                                <stop offset="100%" stopColor="#14b8a6" />
                            </linearGradient>
                        </defs>
                    </svg>

                    {/* Steps */}
                    {steps.map((step) => {
                        const radius = 35; // percentage
                        const x = 50 + radius * Math.cos((step.angle * Math.PI) / 180);
                        const y = 50 + radius * Math.sin((step.angle * Math.PI) / 180);
                        const isActive = selectedStep === step.id;

                        return (
                            <div
                                key={step.id}
                                className={`absolute transition-all duration-500 cursor-pointer ${isActive ? 'scale-125 z-30' : 'hover:scale-110'}`}
                                style={{
                                    left: `${x}%`,
                                    top: `${y}%`,
                                    transform: 'translate(-50%, -50%)'
                                }}
                                onClick={() => setSelectedStep(step.id)}
                            >
                                <div className={`relative w-14 h-14 bg-white rounded-2xl shadow-lg border-2 flex items-center justify-center transition-all ${isActive ? `${colorMap[step.color].border} ${colorMap[step.color].shadow}` : 'border-transparent hover:border-gray-200'}`}>
                                    <div className={`${isActive ? colorMap[step.color].text : 'text-gray-400'} transition-colors`}>
                                        {step.icon}
                                    </div>
                                    {isActive && (
                                        <div className={`absolute -top-1 -right-1 w-3 h-3 ${colorMap[step.color].bg} rounded-full animate-pulse border-2 border-white`} />
                                    )}
                                </div>

                                {/* Simple Label */}
                                <div className={`absolute top-full mt-2 left-1/2 -translate-x-1/2 whitespace-nowrap transition-opacity ${isActive ? 'opacity-0' : 'opacity-100'}`}>
                                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter">{step.title.split(' ')[0]}</span>
                                </div>
                            </div>
                        );
                    })}

                    {/* Data Flow Particles */}
                    {!selectedStep && (
                        <div className="absolute top-1/2 left-1/2 w-[70%] h-[70%] -translate-x-1/2 -translate-y-1/2 pointer-events-none">
                            <div className="absolute w-2 h-2 bg-blue-400 rounded-full blur-[2px] animate-[orbit_10s_linear_infinite]" />
                            <div className="absolute w-2 h-2 bg-purple-400 rounded-full blur-[2px] animate-[orbit_12s_linear_infinite_reverse] delay-2000" />
                        </div>
                    )}
                </div>

                {/* Detail Panel */}
                <div className={`flex-1 transition-all duration-500 overflow-hidden ${selectedStep ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-12 pointer-events-none absolute md:static'}`}>
                    {currentStep && (
                        <div className="bg-white p-8 rounded-[2.5rem] border border-gray-100 shadow-2xl shadow-gray-200/50 space-y-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className={`w-12 h-12 ${colorMap[currentStep.color].bgLight} rounded-2xl flex items-center justify-center ${colorMap[currentStep.color].text}`}>
                                        {currentStep.icon}
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-black text-gray-900 leading-none">{currentStep.title}</h3>
                                        <p className={`text-[11px] font-bold uppercase tracking-widest ${colorMap[currentStep.color].text} mt-1`}>{currentStep.details.subtitle}</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => setSelectedStep(null)}
                                    className="p-2 hover:bg-gray-50 rounded-xl transition-colors text-gray-400 hover:text-gray-900"
                                >
                                    <X size={20} />
                                </button>
                            </div>

                            <div className="space-y-4">
                                <ul className="space-y-3">
                                    {currentStep.details.points.map((point, i) => (
                                        <li key={i} className="flex gap-3 items-start animate-[fadeIn_0.5s_ease-out_forwards]" style={{ animationDelay: `${i * 100}ms` }}>
                                            <div className={`mt-1.5 w-1.5 h-1.5 rounded-full ${colorMap[currentStep.color].bg} opacity-60 shrink-0`} />
                                            <span className="text-sm text-gray-600 leading-snug">{point}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="pt-6 border-t border-gray-50 flex items-center justify-between">
                                <div>
                                    <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1">Tech Stack</span>
                                    <code className="text-[10px] font-bold text-gray-600 bg-gray-50 px-2 py-1 rounded-md">{currentStep.details.tech}</code>
                                </div>
                                <button
                                    onClick={() => {
                                        const nextIndex = (steps.findIndex(s => s.id === selectedStep) + 1) % steps.length;
                                        setSelectedStep(steps[nextIndex].id);
                                    }}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-xl ${colorMap[currentStep.color].button} text-white text-xs font-bold hover:shadow-lg transition-all active:scale-95`}
                                >
                                    Next Stage <ArrowRight size={14} />
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                <style>{`
                    @keyframes orbit {
                        from { transform: rotate(0deg) translateX(140px) rotate(0deg); }
                        to { transform: rotate(360deg) translateX(140px) rotate(-360deg); }
                    }
                    @keyframes fadeIn {
                        from { opacity: 0; transform: translateX(-10px); }
                        to { opacity: 1; transform: translateX(0); }
                    }
                `}</style>
            </div>
        </div>
    );
};
