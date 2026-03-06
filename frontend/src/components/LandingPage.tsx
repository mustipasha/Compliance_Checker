import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, UploadCloud, FileText, Search } from 'lucide-react';

export const LandingPage: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white flex flex-col justify-center items-center p-6">
            <div className="max-w-4xl w-full text-center space-y-12 animate-in fade-in zoom-in-95 duration-500">

                {/* Hero Section */}
                <div className="space-y-6">
                    <div className="inline-flex items-center justify-center p-4 bg-blue-50 rounded-3xl mb-4 shadow-sm">
                        <ShieldCheck className="w-16 h-16 text-blue-600" />
                    </div>
                    <h1 className="text-5xl md:text-6xl font-black text-gray-900 tracking-tight leading-tight">
                        AI Compliance <span className="text-blue-600">Checker</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-gray-500 max-w-2xl mx-auto leading-relaxed">
                        Verify your AI system's alignment with the <strong className="text-gray-700">EU AI Act Safety & Security Code of Practice</strong>.
                    </p>
                </div>

                {/* Steps Grid */}
                <div className="grid md:grid-cols-3 gap-8 text-left">
                    {[
                        {
                            icon: <UploadCloud className="w-6 h-6 text-white" />,
                            title: "1. Upload Evidence",
                            desc: "Submit your system documentation, technical reports, or policy PDFs.",
                            color: "bg-indigo-500"
                        },
                        {
                            icon: <Search className="w-6 h-6 text-white" />,
                            title: "2. AI Analysis",
                            desc: (
                                <span>
                                    Our agents analyze your documents against 32 specific safety measures.
                                    <button
                                        onClick={() => navigate('/methodology')}
                                        className="block mt-2 text-blue-600 font-bold hover:underline"
                                    >
                                        See how it works →
                                    </button>
                                </span>
                            ),
                            color: "bg-blue-500"
                        },
                        {
                            icon: <FileText className="w-6 h-6 text-white" />,
                            title: "3. Get Report",
                            desc: "Receive a detailed compliance verification with traceable evidence.",
                            color: "bg-teal-500"
                        }
                    ].map((step, idx) => (
                        <div key={idx} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                            <div className={`w-12 h-12 ${step.color} rounded-xl flex items-center justify-center shadow-lg shadow-blue-900/5 mb-4`}>
                                {step.icon}
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-2">{step.title}</h3>
                            <p className="text-sm text-gray-500 leading-relaxed">{step.desc}</p>
                        </div>
                    ))}
                </div>

                {/* CTA */}
                <div className="pt-8">
                    <button
                        onClick={() => navigate('/assess')}
                        className="px-10 py-4 bg-blue-600 text-white text-lg font-bold rounded-2xl hover:bg-blue-700 transition-all shadow-xl shadow-blue-200 hover:scale-105 active:scale-95"
                    >
                        Start Evaluation
                    </button>
                    <button
                        onClick={() => navigate('/explore')}
                        className="px-10 py-4 bg-white text-blue-600 text-lg font-bold rounded-2xl border-2 border-blue-100 hover:border-blue-200 hover:bg-blue-50 transition-all shadow-lg shadow-blue-900/5 hover:scale-105 active:scale-95 ml-4"
                    >
                        Explore Framework
                    </button>
                    <p className="mt-4 text-xs text-center text-gray-400 font-medium uppercase tracking-widest">
                        Secure & Private • Local Processing
                    </p>
                </div>

            </div>
        </div>
    );
};
