import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Calendar, ChevronRight, BarChart3, AlertCircle, Trash2, Filter, XCircle } from 'lucide-react';
import { Results } from './Results';
import { API_BASE_URL } from '../config';

interface AssessmentSummary {
    filename: string;
    timestamp: number;
    score: number;
    commitments_count: number;
    source_document: string;
    provider?: string;
    model?: string;
    mode?: string;
}

export const AssessmentHistory: React.FC = () => {
    const [history, setHistory] = useState<AssessmentSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedReport, setSelectedReport] = useState<any | null>(null);
    const [error, setError] = useState('');

    // Filters State
    const [selectedProvider, setSelectedProvider] = useState<string>('');
    const [selectedModel, setSelectedModel] = useState<string>('');
    const [selectedMode, setSelectedMode] = useState<string>('');

    const fetchHistory = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_BASE_URL}/assessments`);
            setHistory(response.data);
            setError('');
        } catch (err) {
            console.error(err);
            setError('Failed to load assessment history.');
        } finally {
            setLoading(false);
        }
    };

    const loadReport = async (filename: string) => {
        try {
            const response = await axios.get(`${API_BASE_URL}/assessments/${filename}`);
            setSelectedReport(response.data);
        } catch (err) {
            console.error(err);
            alert('Failed to load report details.');
        }
    };

    const deleteReport = async (filename: string, e: React.MouseEvent) => {
        e.stopPropagation(); // Prevent opening the report
        if (!confirm('Are you sure you want to delete this assessment?')) return;

        try {
            await axios.delete(`${API_BASE_URL}/assessments/${filename}`);
            setHistory(history.filter(h => h.filename !== filename));
        } catch (err) {
            console.error(err);
            alert('Failed to delete assessment.');
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const formatDate = (timestamp: number) => {
        return new Date(timestamp * 1000).toLocaleDateString() + ' ' + new Date(timestamp * 1000).toLocaleTimeString();
    };

    // Derived Data for Filters
    const availableProviders = Array.from(new Set(history.map(h => h.provider).filter(Boolean))).sort() as string[];
    const availableModels = Array.from(new Set(
        history
            .filter(h => !selectedProvider || h.provider === selectedProvider)
            .map(h => h.model)
            .filter(Boolean)
    )).sort() as string[];

    const filteredHistory = history.filter(item => {
        const matchesProvider = !selectedProvider || item.provider === selectedProvider;
        const matchesModel = !selectedModel || item.model === selectedModel;
        const matchesMode = !selectedMode || item.mode === selectedMode;
        return matchesProvider && matchesModel && matchesMode;
    });

    const resetFilters = () => {
        setSelectedProvider('');
        setSelectedModel('');
        setSelectedMode('');
    };

    if (selectedReport) {
        return (
            <div className="animate-in fade-in slide-in-from-right duration-300">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <button
                        onClick={() => setSelectedReport(null)}
                        className="mb-4 flex items-center text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors"
                    >
                        <ChevronRight className="rotate-180 mr-1" size={16} /> Back to History
                    </button>
                    <Results report={selectedReport} />
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-5xl mx-auto px-4 py-12">
            <div className="mb-8">
                <h2 className="text-3xl font-black text-gray-900 tracking-tight">Assessment History</h2>
                <p className="text-gray-500 mt-2">View past compliance reports and track progress over time.</p>
            </div>

            {loading ? (
                <div className="text-center py-20 text-gray-400 animate-pulse">Loading history...</div>
            ) : error ? (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center gap-3">
                    <AlertCircle /> {error}
                </div>
            ) : history.length === 0 ? (
                <div className="text-center py-20 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200">
                    <div className="inline-flex bg-white p-4 rounded-full shadow-sm mb-4">
                        <BarChart3 className="w-8 h-8 text-gray-300" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">No assessments found</h3>
                    <p className="text-gray-400">Run a new assessment to see it listed here.</p>
                </div>
            ) : (
                <div className="space-y-6">
                    {/* Filter Bar */}
                    <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-wrap items-center gap-4">
                        <div className="flex items-center gap-2 text-gray-400 mr-2">
                            <Filter size={18} />
                            <span className="text-xs font-bold uppercase tracking-widest">Filters</span>
                        </div>

                        <div className="flex flex-wrap items-center gap-3 flex-1">
                            {/* Provider Filter */}
                            <select
                                value={selectedProvider}
                                onChange={(e) => {
                                    setSelectedProvider(e.target.value);
                                    setSelectedModel(''); // Reset model when provider changes
                                }}
                                className="bg-gray-50 border-none text-gray-700 text-xs font-bold py-2 px-3 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all outline-none min-w-[120px]"
                            >
                                <option value="">Suppliers (All)</option>
                                {availableProviders.map(p => (
                                    <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                                ))}
                            </select>

                            {/* Model Filter */}
                            <select
                                value={selectedModel}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                className="bg-gray-50 border-none text-gray-700 text-xs font-bold py-2 px-3 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all outline-none min-w-[120px]"
                            >
                                <option value="">Models (All)</option>
                                {availableModels.map(m => (
                                    <option key={m} value={m}>{m}</option>
                                ))}
                            </select>

                            {/* Mode Filter */}
                            <select
                                value={selectedMode}
                                onChange={(e) => setSelectedMode(e.target.value)}
                                className="bg-gray-50 border-none text-gray-700 text-xs font-bold py-2 px-3 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all outline-none min-w-[120px]"
                            >
                                <option value="">Mode (All)</option>
                                <option value="single">Single Agent</option>
                                <option value="triple">Triple Agent</option>
                            </select>

                            {(selectedProvider || selectedModel || selectedMode) && (
                                <button
                                    onClick={resetFilters}
                                    className="flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-700 bg-blue-50 px-3 py-2 rounded-lg transition-colors"
                                >
                                    <XCircle size={14} /> Clear
                                </button>
                            )}
                        </div>

                        <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                            {filteredHistory.length} Results
                        </div>
                    </div>

                    {filteredHistory.length === 0 ? (
                        <div className="text-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-100">
                            <h3 className="text-lg font-bold text-gray-900">No matches found</h3>
                            <p className="text-gray-400">Try adjusting your filters.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {filteredHistory.map((item) => (
                                <div
                                    key={item.filename}
                                    onClick={() => loadReport(item.filename)}
                                    className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group"
                                >
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-4">
                                            <div className={`p-3 rounded-xl ${item.score >= 80 ? 'bg-green-100 text-green-600' : item.score >= 50 ? 'bg-yellow-100 text-yellow-600' : 'bg-red-100 text-red-600'}`}>
                                                <BarChart3 size={24} />
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                                    {item.source_document || "Assessment Report"}
                                                </h3>
                                                <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
                                                    <Calendar size={14} />
                                                    {formatDate(item.timestamp)}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex items-center gap-8">
                                            <div className="hidden lg:flex flex-col items-end gap-1 text-right">
                                                <div className="flex items-center gap-2 justify-end">
                                                    {item.provider && (
                                                        <span className="text-[10px] font-bold px-1.5 py-0.5 bg-gray-100 rounded text-gray-600 uppercase tracking-wider">
                                                            {item.provider}
                                                        </span>
                                                    )}
                                                    {item.model && (
                                                        <span className="text-[10px] font-bold px-1.5 py-0.5 bg-blue-50 text-blue-600 rounded uppercase tracking-wider">
                                                            {item.model}
                                                        </span>
                                                    )}
                                                </div>
                                                <span className="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none">
                                                    {item.mode === 'triple' ? 'Triple Agent Pipeline' : 'Single Agent Speed'}
                                                </span>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-2xl font-black text-gray-900">{item.score.toFixed(1)}%</div>
                                                <div className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Score</div>
                                            </div>
                                            <div className="hidden sm:block text-right">
                                                <div className="text-2xl font-black text-gray-900">{item.commitments_count}</div>
                                                <div className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Commitments</div>
                                            </div>
                                            <button
                                                onClick={(e) => deleteReport(item.filename, e)}
                                                className="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-full transition-colors"
                                                title="Delete Assessment"
                                            >
                                                <Trash2 size={20} />
                                            </button>
                                            <ChevronRight className="text-gray-300 group-hover:text-blue-500 transition-colors" />
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
