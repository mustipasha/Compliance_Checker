import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ShieldCheck, HardDrive, LayoutDashboard, History, BookOpen, Activity } from 'lucide-react';
import { LandingPage } from './components/LandingPage';
import { AssessmentFlow } from './components/AssessmentFlow';
import { DocumentList } from './components/DocumentList';
import { AssessmentHistory } from './components/AssessmentHistory';
import { CommitmentExplorer } from './components/CommitmentExplorer';
import { Methodology } from './components/Methodology';
import { AssessmentProvider } from './context/AssessmentContext';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'text-blue-600 bg-blue-50' : 'text-gray-500 hover:text-gray-900 hover:bg-gray-50';
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-3 group">
          <ShieldCheck className="w-8 h-8 text-blue-600 transition-transform group-hover:scale-110" />
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">Compliance Checker</h1>
        </Link>
        <nav className="flex items-center space-x-2">
          <Link
            to="/methodology"
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${isActive('/methodology')}`}
          >
            <Activity size={18} /> How it Works
          </Link>
          <Link
            to="/explore"
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${isActive('/explore')}`}
          >
            <BookOpen size={18} /> Framework Guide
          </Link>
          <Link
            to="/assess"
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${isActive('/assess')}`}
          >
            <LayoutDashboard size={18} /> Assessment
          </Link>
          <Link
            to="/history"
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${isActive('/history')}`}
          >
            <History size={18} /> History
          </Link>
          <Link
            to="/documents"
            className={`px-4 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${isActive('/documents')}`}
          >
            <HardDrive size={18} /> Library
          </Link>
        </nav>
      </div>
    </header>
  );
};

function App() {
  return (
    <AssessmentProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 font-sans text-gray-900">
          <Navbar />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/explore" element={<CommitmentExplorer />} />
            <Route path="/assess" element={<AssessmentFlow />} />
            <Route path="/methodology" element={<Methodology />} />
            <Route path="/history" element={<AssessmentHistory />} />
            <Route path="/documents" element={<DocumentList />} />
          </Routes>
        </div>
      </Router>
    </AssessmentProvider>
  );
}

export default App;
