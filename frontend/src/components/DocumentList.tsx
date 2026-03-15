import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { FileText, Trash2, Calendar, HardDrive, AlertCircle } from 'lucide-react';

interface Document {
    filename: string;
    size_bytes: number;
    modified: number;
}

export const DocumentList: React.FC = () => {
    const [documents, setDocuments] = useState<Document[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchDocuments = async () => {
        try {
            setLoading(true);
            const response = await api.get('/documents');
            setDocuments(response.data);
            setError('');
        } catch (err) {
            console.error(err);
            setError('Failed to load documents.');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (filename: string) => {
        if (!confirm(`Are you sure you want to delete "${filename}"? This will confirm remove it from the database.`)) return;

        try {
            await api.delete(`/documents/${filename}`);
            setDocuments(docs => docs.filter(d => d.filename !== filename));
        } catch (err) {
            console.error(err);
            alert('Failed to delete document.');
        }
    };

    useEffect(() => {
        fetchDocuments();
    }, []);

    const formatSize = (bytes: number) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const result = bytes / k;
        return result < 1024 ? `${result.toFixed(1)} KB` : `${(result / 1024).toFixed(1)} MB`;
    };

    const formatDate = (timestamp: number) => {
        return new Date(timestamp * 1000).toLocaleDateString() + ' ' + new Date(timestamp * 1000).toLocaleTimeString();
    };

    return (
        <div className="max-w-5xl mx-auto px-4 py-12">
            <div className="mb-8 flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-black text-gray-900 tracking-tight">Indexed Documents</h2>
                    <p className="text-gray-500 mt-2">Manage files currently stored in the vector database.</p>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={async () => {
                            if (!confirm('Are you sure you want to clear all indexed documents? This cannot be undone.')) return;
                            try {
                                await api.post('/reset-db');
                                fetchDocuments();
                                alert('Database cleared successfully!');
                            } catch (error) {
                                console.error('Reset failed:', error);
                                alert('Failed to clear database.');
                            }
                        }}
                        className="px-4 py-2 text-xs font-bold uppercase tracking-widest text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-red-100"
                    >
                        Clear All Records
                    </button>
                    <div className="bg-blue-50 text-blue-700 px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2">
                        <HardDrive size={16} />
                        {documents.length} Files
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-20 text-gray-400 animate-pulse">Loading library...</div>
            ) : error ? (
                <div className="bg-red-50 text-red-600 p-4 rounded-xl flex items-center gap-3">
                    <AlertCircle /> {error}
                </div>
            ) : documents.length === 0 ? (
                <div className="text-center py-20 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200">
                    <div className="inline-flex bg-white p-4 rounded-full shadow-sm mb-4">
                        <FileText className="w-8 h-8 text-gray-300" />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900">No documents found</h3>
                    <p className="text-gray-400">Upload documents in the assessment tab to see them here.</p>
                </div>
            ) : (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 border-b border-gray-100 text-xs font-bold text-gray-400 uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-4">Document Name</th>
                                <th className="px-6 py-4">Size</th>
                                <th className="px-6 py-4">Uploaded</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {documents.map((doc) => (
                                <tr key={doc.filename} className="hover:bg-blue-50/30 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                                                <FileText size={18} />
                                            </div>
                                            <span className="font-medium text-gray-900">{doc.filename}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        {formatSize(doc.size_bytes)}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        <div className="flex items-center gap-2">
                                            <Calendar size={14} className="text-gray-300" />
                                            {formatDate(doc.modified)}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => handleDelete(doc.filename)}
                                            className="p-2 hover:bg-red-50 text-gray-300 hover:text-red-500 rounded-lg transition-colors"
                                            title="Delete document"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
