import React from 'react';
import { Upload } from './Upload';
import { Results } from './Results';
import { ShieldCheck, Loader2, Bot, ChevronDown, Zap, Users, Cpu } from 'lucide-react';
import { useAssessment } from '../context/AssessmentContext';

export const AssessmentFlow: React.FC = () => {
    const {
        step, setStep, report, llmOptions,
        selectedProvider, handleProviderChange,
        selectedModel, setSelectedModel,
        selectedMode, setSelectedMode,
        handleUploadComplete
    } = useAssessment();

    const currentProviderModels = llmOptions?.providers.find(p => p.id === selectedProvider)?.models || [];

    return (
        <div className="max-w-6xl mx-auto px-4 py-12 sm:px-6 lg:px-8">
            {/* Header Actions */}
            <div className="flex justify-end mb-8">
                {step === 'results' && (
                    <button
                        onClick={() => setStep('upload')}
                        className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    >
                        New Assessment
                    </button>
                )}
            </div>

            {step === 'upload' && (
                <div className="max-w-2xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    <div className="text-center space-y-4">
                        <h2 className="text-4xl font-black text-gray-900 tracking-tight">Evaluate AI Compliance</h2>
                        <p className="text-lg text-gray-500">
                            Upload your system documentation to check alignment with the EU AI Act Safety & Security Code of Practice.
                        </p>
                    </div>

                    {/* LLM Provider/Model Selector */}
                    {llmOptions && (
                        <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
                            <div className="flex items-center gap-2 mb-4">
                                <Bot className="w-5 h-5 text-blue-600" />
                                <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider">LLM Configuration</h3>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                {/* Provider Select */}
                                <div>
                                    <label className="block text-xs font-semibold text-gray-500 mb-1.5">Provider</label>
                                    <div className="relative">
                                        <select
                                            value={selectedProvider}
                                            onChange={(e) => handleProviderChange(e.target.value)}
                                            className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 pr-10 text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer hover:bg-gray-100"
                                        >
                                            {llmOptions.providers.map(p => (
                                                <option key={p.id} value={p.id}>{p.name}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                                    </div>
                                </div>
                                {/* Model Select */}
                                <div>
                                    <label className="block text-xs font-semibold text-gray-500 mb-1.5">Model</label>
                                    <div className="relative">
                                        <select
                                            value={selectedModel}
                                            onChange={(e) => setSelectedModel(e.target.value)}
                                            className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 pr-10 text-sm font-medium text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all cursor-pointer hover:bg-gray-100"
                                        >
                                            {currentProviderModels.map(m => (
                                                <option key={m} value={m}>{m}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Reasoning Mode Selector */}
                    <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
                        <div className="flex items-center gap-2 mb-4">
                            <Cpu className="w-5 h-5 text-purple-600" />
                            <h3 className="text-sm font-bold text-gray-700 uppercase tracking-wider">Reasoning Mode</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => setSelectedMode('single')}
                                className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMode === 'single' ? 'border-blue-500 bg-blue-50/50' : 'border-gray-100 hover:border-gray-200'}`}
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <Zap size={14} className={selectedMode === 'single' ? 'text-blue-600' : 'text-gray-400'} />
                                    <span className="text-xs font-bold uppercase tracking-wider">Single Agent</span>
                                </div>
                                <p className="text-[10px] text-gray-500 font-medium">Fast, direct synthesis for rapid screening.</p>
                            </button>
                            <button
                                onClick={() => setSelectedMode('triple')}
                                className={`p-4 rounded-xl border-2 text-left transition-all ${selectedMode === 'triple' ? 'border-purple-500 bg-purple-50/50' : 'border-gray-100 hover:border-gray-200'}`}
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <Users size={14} className={selectedMode === 'triple' ? 'text-purple-600' : 'text-gray-400'} />
                                    <span className="text-xs font-bold uppercase tracking-wider">Triple Agent</span>
                                </div>
                                <p className="text-[10px] text-gray-500 font-medium">High accuracy, multi-step adversarial pipeline.</p>
                            </button>
                        </div>
                    </div>

                    <div className="bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
                        <Upload onUploadComplete={handleUploadComplete} />
                    </div>
                </div>
            )}

            {step === 'assessing' && (
                <div className="flex flex-col items-center justify-center py-32 space-y-6 animate-in fade-in duration-500">
                    <div className="relative">
                        <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <ShieldCheck className="w-6 h-6 text-blue-400" />
                        </div>
                    </div>
                    <div className="text-center space-y-2">
                        <h2 className="text-2xl font-black text-gray-900">Analyzing Documentation</h2>
                        <p className="text-gray-500">
                            Running assessments using <span className="font-semibold text-blue-600">{selectedModel}</span> ({selectedProvider})...
                        </p>
                    </div>
                </div>
            )}

            {step === 'results' && report && (
                <Results report={report} />
            )}
        </div>
    );
};
