import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface AssessmentReport {
    compliance_score: number;
    commitments: any[];
    source_document?: string;
    provider?: string;
    model?: string;
    mode?: string;
}

interface ProviderOption {
    id: string;
    name: string;
    models: string[];
}

interface LlmOptions {
    providers: ProviderOption[];
    current: { provider: string; model: string };
}

interface AssessmentContextType {
    step: 'upload' | 'assessing' | 'results';
    setStep: (step: 'upload' | 'assessing' | 'results') => void;
    report: AssessmentReport | null;
    setReport: (report: AssessmentReport | null) => void;
    llmOptions: LlmOptions | null;
    selectedProvider: string;
    setSelectedProvider: (provider: string) => void;
    selectedModel: string;
    setSelectedModel: (model: string) => void;
    selectedMode: 'single' | 'triple';
    setSelectedMode: (mode: 'single' | 'triple') => void;
    handleProviderChange: (providerId: string) => void;
    handleUploadComplete: () => Promise<void>;
}

const AssessmentContext = createContext<AssessmentContextType | undefined>(undefined);

export const AssessmentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [step, setStep] = useState<'upload' | 'assessing' | 'results'>('upload');
    const [report, setReport] = useState<AssessmentReport | null>(null);

    const [llmOptions, setLlmOptions] = useState<LlmOptions | null>(null);
    const [selectedProvider, setSelectedProvider] = useState('');
    const [selectedModel, setSelectedModel] = useState('');
    const [selectedMode, setSelectedMode] = useState<'single' | 'triple'>('single');

    useEffect(() => {
        axios.get('http://localhost:8000/llm-options')
            .then(res => {
                const opts: LlmOptions = res.data;
                setLlmOptions(opts);
                setSelectedProvider(opts.current.provider);
                setSelectedModel(opts.current.model);
            })
            .catch(err => console.error('Failed to fetch LLM options:', err));
    }, []);

    const handleProviderChange = (providerId: string) => {
        setSelectedProvider(providerId);
        const providerData = llmOptions?.providers.find(p => p.id === providerId);
        if (providerData && providerData.models.length > 0) {
            setSelectedModel(providerData.models[0]);
        }
    };

    const handleUploadComplete = async () => {
        setStep('assessing');
        try {
            const response = await axios.post(
                `http://localhost:8000/assess?provider=${selectedProvider}&model=${encodeURIComponent(selectedModel)}&mode=${selectedMode}`
            );
            setReport(response.data);
            setStep('results');
        } catch (error) {
            console.error('Assessment failed:', error);
            alert('Assessment failed. Please check the backend logs.');
            setStep('upload');
        }
    };

    return (
        <AssessmentContext.Provider value={{
            step, setStep, report, setReport, llmOptions,
            selectedProvider, setSelectedProvider,
            selectedModel, setSelectedModel,
            selectedMode, setSelectedMode,
            handleProviderChange, handleUploadComplete
        }}>
            {children}
        </AssessmentContext.Provider>
    );
};

export const useAssessment = () => {
    const context = useContext(AssessmentContext);
    if (context === undefined) {
        throw new Error('useAssessment must be used within an AssessmentProvider');
    }
    return context;
};
