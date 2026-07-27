import { useState } from 'react';
import { FileText, Copy, Download, RefreshCw, AlertCircle, Edit3, Check } from 'lucide-react';
import { chat } from '../services/api';

export const LeadershipReport = () => {
  const [report, setReport] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);

  const generateReport = async () => {
    setIsGenerating(true);
    try {
      const prompt = "Generate a comprehensive leadership update covering pipeline health, revenue performance, work order status, and key risks. Format it as an executive briefing.";
      const response = await chat(prompt, []);
      setReport(response.reply);
      setIsEditing(false);
    } catch (error) {
      console.error("Failed to generate report", error);
      setReport("Failed to generate report. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Leadership_Update_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
            <FileText className="w-6 h-6 text-brand-400" />
            Leadership Briefing
          </h1>
          <p className="text-sm text-slate-400">Generate AI-powered executive summaries</p>
        </div>
        <button
          onClick={generateReport}
          disabled={isGenerating}
          className="bg-gradient-to-r from-brand-600 to-cyan-500 hover:from-brand-500 hover:to-cyan-400 text-white px-5 py-2.5 rounded-xl font-medium transition-all transform hover:-translate-y-0.5 disabled:opacity-50 disabled:transform-none flex items-center gap-2 shadow-lg shadow-brand-500/20"
        >
          <RefreshCw className={`w-4 h-4 ${isGenerating ? 'animate-spin' : ''}`} />
          {isGenerating ? 'Generating...' : 'Generate Report'}
        </button>
      </div>

      <div className="glass-card rounded-2xl overflow-hidden flex flex-col min-h-[500px]">
        {/* Toolbar */}
        <div className="bg-surface-800/80 border-b border-white/5 p-3 flex justify-between items-center px-5">
          <div className="text-sm text-slate-400 font-medium">
            {new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
          <div className="flex items-center gap-2">
            {report && (
              <>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className={`p-2 rounded-lg transition-colors flex items-center gap-1.5 text-sm font-medium ${
                    isEditing ? 'bg-brand-500/20 text-brand-400' : 'text-slate-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <Edit3 className="w-4 h-4" />
                  {isEditing ? 'Save' : 'Edit'}
                </button>
                <div className="w-px h-4 bg-white/10 mx-1"></div>
                <button
                  onClick={handleCopy}
                  className="p-2 text-slate-400 hover:bg-white/5 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-sm"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                  Copy
                </button>
                <button
                  onClick={handleDownload}
                  className="p-2 text-slate-400 hover:bg-white/5 hover:text-white rounded-lg transition-colors flex items-center gap-1.5 text-sm"
                >
                  <Download className="w-4 h-4" />
                  Save .txt
                </button>
              </>
            )}
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-6 relative">
          {isGenerating ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-surface-900/50 backdrop-blur-sm z-10 animate-fade-in">
              <div className="w-64 h-2 bg-surface-800 rounded-full overflow-hidden mb-4 border border-white/5">
                <div className="h-full bg-gradient-to-r from-brand-500 to-cyan-400 w-1/2 animate-[gradient_2s_ease-in-out_infinite_alternate] rounded-full"></div>
              </div>
              <p className="text-brand-400 font-medium animate-pulse">Synthesizing live data...</p>
              <div className="mt-8 text-xs text-slate-500 space-y-2 text-center">
                <p>Analyzing pipeline health...</p>
                <p>Calculating revenue metrics...</p>
                <p>Evaluating work order delays...</p>
              </div>
            </div>
          ) : !report ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 text-center">
              <FileText className="w-12 h-12 mb-4 opacity-20" />
              <p>Click 'Generate Report' to create an AI-powered summary based on the latest data.</p>
              <div className="mt-6 text-left max-w-sm w-full bg-surface-800/50 p-4 rounded-xl border border-white/5 border-dashed">
                <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Template Sections Include:</p>
                <ul className="text-sm space-y-1.5 text-slate-500">
                  <li className="flex items-center gap-2"><div className="w-1 h-1 bg-brand-500 rounded-full"/>Executive Summary</li>
                  <li className="flex items-center gap-2"><div className="w-1 h-1 bg-brand-500 rounded-full"/>Pipeline Health</li>
                  <li className="flex items-center gap-2"><div className="w-1 h-1 bg-brand-500 rounded-full"/>Revenue & Collections</li>
                  <li className="flex items-center gap-2"><div className="w-1 h-1 bg-brand-500 rounded-full"/>Work Orders Status</li>
                </ul>
              </div>
            </div>
          ) : isEditing ? (
            <textarea
              value={report}
              onChange={(e) => setReport(e.target.value)}
              className="w-full h-full min-h-[400px] bg-surface-800/50 text-slate-200 p-4 rounded-xl border border-brand-500/30 focus:outline-none focus:ring-1 focus:ring-brand-500 resize-y font-mono text-sm leading-relaxed"
            />
          ) : (
            <div className="prose prose-invert max-w-none text-slate-300">
              {report.split('\n').map((paragraph, index) => {
                if (!paragraph.trim()) return <br key={index} />;
                if (paragraph.startsWith('## ')) return <h2 key={index} className="text-xl font-semibold text-white mt-6 mb-3">{paragraph.replace('## ', '')}</h2>;
                if (paragraph.startsWith('### ')) return <h3 key={index} className="text-lg font-medium text-brand-300 mt-4 mb-2">{paragraph.replace('### ', '')}</h3>;
                if (paragraph.startsWith('- ') || paragraph.startsWith('* ')) {
                  // Format bold text inside lists
                  const formattedText = paragraph.substring(2).replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
                  return <li key={index} className="ml-4 list-disc marker:text-brand-500 mb-1" dangerouslySetInnerHTML={{ __html: formattedText }} />;
                }
                const formattedParagraph = paragraph.replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>');
                return <p key={index} className="mb-3 leading-relaxed" dangerouslySetInnerHTML={{ __html: formattedParagraph }} />;
              })}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-start gap-3 p-4 bg-brand-900/20 border border-brand-500/20 rounded-xl text-brand-200/70 text-sm">
        <AlertCircle className="w-5 h-5 shrink-0 text-brand-400" />
        <p>Leadership updates are AI-generated summaries based on live data. Always verify key figures before sharing externally.</p>
      </div>
    </div>
  );
};
