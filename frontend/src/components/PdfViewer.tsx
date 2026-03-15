import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, X, Search, AlertCircle } from 'lucide-react';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// Set up the worker for PDF.js
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

interface PdfViewerProps {
    url: string;
    initialPage?: number;
    highlightText?: string;
    onClose: () => void;
}

export const PdfViewer: React.FC<PdfViewerProps> = ({ url, initialPage = 1, highlightText, onClose }) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const [pageNumber, setPageNumber] = useState<number>(isNaN(initialPage) ? 1 : Math.max(1, Math.floor(initialPage)));
    const [scale, setScale] = useState<number>(1.0);

    // Sync initial page when it changes
    useEffect(() => {
        setPageNumber(isNaN(initialPage) ? 1 : Math.max(1, Math.floor(initialPage)));
    }, [initialPage]);

    function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
        setNumPages(numPages);
    }

    return (
        <div className="fixed inset-0 z-[100] bg-gray-900/90 backdrop-blur-sm flex flex-col animate-in fade-in duration-200">
            {/* Toolbar */}
            <div className="bg-white px-4 py-3 flex items-center justify-between shadow-lg z-10">
                <div className="flex items-center gap-4">
                    <h3 className="text-sm font-bold text-gray-700 max-w-xs truncate">
                        Document Viewer
                    </h3>
                    {highlightText && (
                        <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-yellow-50 text-yellow-700 text-xs rounded-full border border-yellow-100">
                            <Search size={12} />
                            <span className="truncate max-w-[200px]">Highlighting: "{highlightText}"</span>
                        </div>
                    )}
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setPageNumber(prev => Math.max(prev - 1, 1))}
                        disabled={pageNumber <= 1}
                        className="p-2 hover:bg-gray-100 rounded-lg disabled:opacity-30 transition-colors"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <span className="text-sm font-medium text-gray-600 min-w-[3rem] text-center">
                        {pageNumber} / {numPages || '--'}
                    </span>
                    <button
                        onClick={() => setPageNumber(prev => Math.min(prev + 1, numPages || 1))}
                        disabled={pageNumber >= (numPages || 1)}
                        className="p-2 hover:bg-gray-100 rounded-lg disabled:opacity-30 transition-colors"
                    >
                        <ChevronRight size={20} />
                    </button>

                    <div className="w-px h-6 bg-gray-200 mx-2" />

                    <button onClick={() => setScale(s => Math.max(s - 0.1, 0.5))} className="p-2 hover:bg-gray-100 rounded-lg">
                        <ZoomOut size={20} />
                    </button>
                    <span className="text-xs font-medium text-gray-500 w-12 text-center">{Math.round(scale * 100)}%</span>
                    <button onClick={() => setScale(s => Math.min(s + 0.1, 2.0))} className="p-2 hover:bg-gray-100 rounded-lg">
                        <ZoomIn size={20} />
                    </button>

                    <div className="w-px h-6 bg-gray-200 mx-2" />

                    <button
                        onClick={onClose}
                        className="p-2 bg-gray-900 text-white hover:bg-gray-700 rounded-lg transition-colors shadow-md"
                    >
                        <X size={20} />
                    </button>
                </div>
            </div>

            {/* Viewer Area */}
            <div className="flex-1 overflow-auto bg-gray-100 flex justify-center p-8">
                <Document
                    file={url}
                    onLoadSuccess={onDocumentLoadSuccess}
                    className="shadow-2xl"
                    loading={
                        <div className="flex items-center justify-center p-20">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                        </div>
                    }
                    error={
                        <div className="flex flex-col items-center justify-center p-12 text-center bg-gray-50 rounded-3xl border-2 border-dashed border-gray-200 m-8">
                            <div className="w-16 h-16 bg-red-50 text-red-500 rounded-full flex items-center justify-center mb-6">
                                <AlertCircle size={32} />
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">Document Unavailable</h3>
                            <p className="text-gray-500 text-sm leading-relaxed max-w-xs mb-8">
                                Failed to load the PDF. This usually happens if the source file was removed from the <strong>Library</strong> after the assessment was completed.
                            </p>
                            <button
                                onClick={onClose}
                                className="px-8 py-3 bg-gray-900 text-white rounded-xl font-bold uppercase tracking-widest text-xs hover:bg-gray-800 transition-all shadow-lg shadow-gray-200"
                            >
                                Close Viewer
                            </button>
                        </div>
                    }
                >
                    <Page
                        pageNumber={pageNumber}
                        scale={scale}
                        renderTextLayer={true}
                        renderAnnotationLayer={true}
                    />
                </Document>
            </div>
        </div>
    );
};
