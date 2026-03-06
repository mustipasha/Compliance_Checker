import React from 'react';
import { Shield, Zap, Users, Search, Compass, Target, MessageSquare, ArrowRight, Activity, Cpu } from 'lucide-react';
import { ProcessLifecycle } from './ProcessLifecycle';

export const Methodology: React.FC = () => {
    return (
        <div className="max-w-5xl mx-auto px-4 py-16 sm:px-6 lg:px-8 space-y-24">
            {/* Header */}
            <div className="text-center space-y-4">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-[10px] font-bold text-blue-600 uppercase tracking-widest mb-4">
                    <Activity className="w-3 h-3" /> Methodology & Architecture
                </div>
                <h1 className="text-4xl md:text-5xl font-black text-gray-900 tracking-tight">
                    How the AI Compliance <span className="text-blue-600">Checker Works</span>
                </h1>
                <p className="text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed">
                    A transparent look into the agentic reasoning and retrieval-augmented generation (RAG)
                    pipeline that powers your compliance assessments.
                </p>
            </div>

            {/* Process Diagram */}
            <section className="bg-white/50 rounded-3xl p-12 border border-gray-100 shadow-xl shadow-blue-500/5 backdrop-blur-sm overflow-hidden">
                <div className="text-center mb-8">
                    <h3 className="text-xl font-bold text-gray-900">The Compliance Pipeline</h3>
                    <p className="text-sm text-gray-500">Interactive overview of our end-to-end assessment lifecycle</p>
                </div>
                <ProcessLifecycle />
            </section>

            {/* Core Engine: RAG */}
            <section className="space-y-12">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-200">
                        <Search className="text-white w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">1. Evidence Retrieval (RAG)</h2>
                        <p className="text-gray-500 font-medium">Turning raw documentation into actionable knowledge.</p>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm grid md:grid-cols-2 gap-12 items-center">
                    <div className="space-y-6">
                        <p className="text-gray-600 leading-relaxed">
                            Our system uses <strong>Retrieval-Augmented Generation</strong> to ensure every assessment is grounded in your specific documentation.
                            Instead of relying on general knowledge, the AI first "searches" your uploaded files.
                        </p>
                        <ul className="space-y-4">
                            <li className="flex gap-3">
                                <div className="mt-1 w-5 h-5 rounded-full bg-green-50 flex items-center justify-center shrink-0">
                                    <Shield className="w-3 h-3 text-green-600" />
                                </div>
                                <span className="text-sm text-gray-700 font-medium">Semantic search identifies relevant technical snippets across hundreds of pages.</span>
                            </li>
                            <li className="flex gap-3">
                                <div className="mt-1 w-5 h-5 rounded-full bg-green-50 flex items-center justify-center shrink-0">
                                    <Shield className="w-3 h-3 text-green-600" />
                                </div>
                                <span className="text-sm text-gray-700 font-medium">Contextual windowing ensures LLMs receive pinpointed evidence from the right chapters.</span>
                            </li>
                        </ul>
                    </div>
                    <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                        <div className="flex flex-col gap-3">
                            <div className="bg-white p-3 rounded-xl border border-dashed border-gray-300 text-[10px] font-mono text-gray-400">PDF Document / Reports</div>
                            <div className="flex justify-center"><ArrowRight className="rotate-90 text-gray-300" /></div>
                            <div className="bg-blue-600 p-3 rounded-xl text-white text-center text-xs font-bold">Vector Database / Indexing</div>
                            <div className="flex justify-center"><ArrowRight className="rotate-90 text-gray-300" /></div>
                            <div className="bg-white p-3 rounded-xl border border-blue-200 text-blue-600 text-center text-xs font-bold">Ranked Evidence Chunks</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Assessment Modes */}
            <section className="space-y-12">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-200">
                        <Cpu className="text-white w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">2. Agentic Reasoning Modes</h2>
                        <p className="text-gray-500 font-medium">Choose between speed and deep adversarial verification.</p>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    {/* Single Agent Mode */}
                    <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm space-y-6 hover:border-blue-200 transition-colors">
                        <div className="flex items-center gap-3">
                            <Zap className="w-5 h-5 text-yellow-500" />
                            <h3 className="text-lg font-bold text-gray-900">Single Agent Mode</h3>
                        </div>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            A streamlined process where a single LLM acts as the "Synthesis Agent."
                            It retrieves evidence and directly maps it to the compliance rubric in one pass.
                        </p>
                        <div className="pt-4 border-t border-gray-50">
                            <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest">
                                <span className="text-gray-400">Step 1</span>
                                <span className="text-blue-500">Retrieval & Synthesis</span>
                            </div>
                            <div className="mt-2 h-1.5 w-full bg-gray-100 rounded-full overflow-hidden">
                                <div className="h-full bg-blue-600 w-full" />
                            </div>
                            <p className="mt-3 text-[10px] text-gray-400 font-bold italic">Best for rapid prototyping and initial document screening.</p>
                        </div>
                    </div>

                    {/* Triple Agent Mode */}
                    <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm space-y-6 border-l-4 border-l-purple-500 hover:border-purple-200 transition-colors">
                        <div className="flex items-center gap-3">
                            <Users className="w-5 h-5 text-purple-600" />
                            <h3 className="text-lg font-bold text-gray-900">Triple Agent Pipeline</h3>
                        </div>
                        <p className="text-sm text-gray-600 leading-relaxed">
                            Our most robust mode. It utilizes three specialized agents in a multi-step
                            adversarial and collaborative pipeline to minimize "AI Hallucinations."
                        </p>

                        <div className="space-y-4 pt-4 border-t border-gray-50">
                            <div className="flex items-start gap-3">
                                <div className="p-1.5 bg-indigo-50 rounded-lg text-indigo-600 shrink-0"><Compass size={14} /></div>
                                <div>
                                    <h4 className="text-[11px] font-black text-gray-800 uppercase tracking-tighter">1. Alignment Agent</h4>
                                    <p className="text-[10px] text-gray-500 leading-tight">Focuses solely on finding where documentation matches the EU UI Act.</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <div className="p-1.5 bg-red-50 rounded-lg text-red-600 shrink-0"><Target size={14} /></div>
                                <div>
                                    <h4 className="text-[11px] font-black text-gray-800 uppercase tracking-tighter">2. Gap Agent</h4>
                                    <p className="text-[10px] text-gray-500 leading-tight">Specifically hunts for missing evidence or scope divergences.</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <div className="p-1.5 bg-purple-50 rounded-lg text-purple-600 shrink-0"><MessageSquare size={14} /></div>
                                <div>
                                    <h4 className="text-[11px] font-black text-gray-800 uppercase tracking-tighter">3. Synthesis Agent</h4>
                                    <p className="text-[10px] text-gray-500 leading-tight">Acts as a neutral judge, weighing the findings of both agents to score.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* The Processing Lifecycle */}
            <section className="space-y-12">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-teal-600 rounded-2xl flex items-center justify-center shadow-lg shadow-teal-200">
                        <Activity className="text-white w-6 h-6" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-gray-900">3. The Processing Lifecycle</h2>
                        <p className="text-gray-500 font-medium">From global document knowledge to per-criterion validation.</p>
                    </div>
                </div>

                <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm space-y-8">
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="space-y-3">
                            <div className="text-xs font-black text-teal-600 uppercase tracking-widest">Phase A</div>
                            <h4 className="font-bold text-gray-900">Document Ingestion</h4>
                            <p className="text-xs text-gray-500 leading-relaxed">The entire document is parsed, chunked, and stored in a vector database to provide a "global brain" for the agents.</p>
                        </div>
                        <div className="space-y-3">
                            <div className="text-xs font-black text-teal-600 uppercase tracking-widest">Phase B</div>
                            <h4 className="font-bold text-gray-900">Criterion Isolation</h4>
                            <p className="text-xs text-gray-500 leading-relaxed">Each of the 32 criteria is processed as an individual task. The backend triggers parallel reasoning pipelines for every measure.</p>
                        </div>
                        <div className="space-y-3">
                            <div className="text-xs font-black text-teal-600 uppercase tracking-widest">Phase C</div>
                            <h4 className="font-bold text-gray-900">Final Aggregation</h4>
                            <p className="text-xs text-gray-500 leading-relaxed">Individual scores and evidence citations are aggregated into the final compliance report and historical record.</p>
                        </div>
                    </div>

                    <div className="p-6 bg-teal-50/50 rounded-2xl border border-teal-100 text-sm text-gray-700 italic">
                        "This granular approach ensures that a single large document is evaluated 32 times with 32 different lenses, uncovering gaps that global summaries might miss."
                    </div>
                </div>
            </section>

            {/* Why This Matters */}
            <section className="bg-gray-900 rounded-[3rem] p-12 text-white overflow-hidden relative">
                <div className="relative z-10 space-y-6">
                    <h2 className="text-3xl font-black tracking-tight">Traceability & Trust</h2>
                    <p className="text-gray-400 max-w-2xl leading-relaxed">
                        By abstracting the backend process into these discrete steps, we provide
                        mathematical and semantic traceability. You don't just get a score; you
                        see the "receipt" of how the AI navigated your documents.
                    </p>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-8 pt-8 border-t border-white/10">
                        <div>
                            <div className="text-2xl font-black text-blue-400">Zero</div>
                            <div className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Hallucination Target</div>
                        </div>
                        <div>
                            <div className="text-2xl font-black text-purple-400">100%</div>
                            <div className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Data Privacy</div>
                        </div>
                        <div>
                            <div className="text-2xl font-black text-teal-400">RAG</div>
                            <div className="text-[10px] font-bold uppercase tracking-widest text-gray-500">Driven Accuracy</div>
                        </div>
                    </div>
                </div>
                {/* Decorative gradients */}
                <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/20 rounded-full blur-[100px] -mr-48 -mt-48" />
                <div className="absolute bottom-0 left-0 w-80 h-80 bg-purple-600/10 rounded-full blur-[80px] -ml-40 -mb-40" />
            </section>
        </div>
    );
};
