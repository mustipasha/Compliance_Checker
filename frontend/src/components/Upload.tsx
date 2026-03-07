import React, { useState } from 'react';
import axios from 'axios';
import { Upload as UploadIcon, FileText, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';

interface UploadProps {
    onUploadComplete: () => void;
}

export const Upload: React.FC<UploadProps> = ({ onUploadComplete }) => {
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            await axios.post(`${API_BASE_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            onUploadComplete();
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || 'Failed to upload file. Please try again.';
            setError(errorMessage);
            console.error(err);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="p-6 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 text-center">
            <div className="flex flex-col items-center justify-center space-y-4">
                <div className="p-4 bg-blue-100 rounded-full">
                    <UploadIcon className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-medium text-gray-900">Upload System Documentation</h3>
                <p className="text-sm text-gray-500">PDF files only</p>

                <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                />
                <label
                    htmlFor="file-upload"
                    className="px-4 py-2 text-sm font-medium text-blue-700 bg-blue-100 rounded-md cursor-pointer hover:bg-blue-200"
                >
                    Select File
                </label>

                {file && (
                    <div className="flex items-center space-x-2 text-sm text-gray-700">
                        <FileText className="w-4 h-4" />
                        <span>{file.name}</span>
                    </div>
                )}

                {error && (
                    <div className="flex items-center space-x-2 text-sm text-red-600">
                        <AlertCircle className="w-4 h-4" />
                        <span>{error}</span>
                    </div>
                )}

                <button
                    onClick={handleUpload}
                    disabled={!file || uploading}
                    className={`px-6 py-2 text-white rounded-md ${!file || uploading
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 hover:bg-blue-700'
                        }`}
                >
                    {uploading ? 'Uploading...' : 'Upload & Process'}
                </button>
            </div>
        </div>
    );
};
