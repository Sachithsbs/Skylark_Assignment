import { useState, useEffect } from 'react';
import { Shield, CheckCircle, Clock, Database, Check } from 'lucide-react';
import { getDashboard } from '../services/api';
import { AnalyticsDashboard } from '../types';

export const DataQualityDashboard = () => {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await getDashboard();
        setData(result);
      } catch (error) {
        console.error("Failed to fetch dashboard data", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading && !data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin-slow w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full glow-blue" />
      </div>
    );
  }

  if (!data) return <div className="text-center text-rose-400 mt-10">Failed to load data quality report.</div>;

  const dq = data.data_quality;

  // Calculate completeness score (rough estimate)
  const totalIssues = dq.deals_missing_sector + dq.deals_missing_close_date + dq.wo_missing_amounts + dq.wo_missing_dates;
  const totalRecords = dq.deals_total + dq.wo_total;
  const completenessScore = Math.max(0, 100 - (totalIssues / (totalRecords * 2)) * 100);

  const getHealthColor = (percent: number) => {
    if (percent < 5) return 'bg-emerald-500 text-emerald-400 border-emerald-500/20';
    if (percent < 20) return 'bg-amber-500 text-amber-400 border-amber-500/20';
    return 'bg-rose-500 text-rose-400 border-rose-500/20';
  };

  const getBarColor = (percent: number) => {
    if (percent < 5) return 'bg-emerald-500';
    if (percent < 20) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const renderIssueRow = (label: string, count: number, total: number) => {
    const percent = total > 0 ? (count / total) * 100 : 0;
    const colorClasses = getHealthColor(percent);
    const barClass = getBarColor(percent);
    
    return (
      <div className="mb-4 last:mb-0">
        <div className="flex justify-between items-end mb-1.5">
          <span className="text-sm text-slate-300">{label}</span>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-white">{count} rows</span>
            <span className={`text-xs px-1.5 py-0.5 rounded border ${colorClasses.split(' ')[1]} ${colorClasses.split(' ')[2]} bg-opacity-10`}>
              {percent.toFixed(1)}% missing
            </span>
          </div>
        </div>
        <div className="w-full bg-surface-900/50 rounded-full h-2">
          <div className={`h-2 rounded-full ${barClass}`} style={{ width: `${Math.min(100, percent)}%` }} />
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4 mb-2">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1 flex items-center gap-2">
            <Shield className="w-6 h-6 text-emerald-400" />
            Data Quality Audit
          </h1>
          <p className="text-sm text-slate-400">Automated cleaning and integrity checks</p>
        </div>
        
        <div className="glass-card px-4 py-2 flex items-center gap-4">
          <div className="flex flex-col items-end">
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Completeness</span>
            <span className="text-lg font-bold text-white">{completenessScore.toFixed(1)}%</span>
          </div>
          <div className="w-12 h-12 relative rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 transform -rotate-90">
              <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent" className="text-surface-800" />
              <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="4" fill="transparent" strokeDasharray={125.6} strokeDashoffset={125.6 - (125.6 * completenessScore) / 100} className="text-emerald-500 transition-all duration-1000 ease-out" />
            </svg>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* CRM Deals Card */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">CRM Deals Dataset</h2>
              <p className="text-xs text-slate-400">{dq.deals_total} total records scanned</p>
            </div>
          </div>
          
          <div className="space-y-2">
            {renderIssueRow("Missing Sector Information", dq.deals_missing_sector, dq.deals_total)}
            {renderIssueRow("Missing Close Date", dq.deals_missing_close_date, dq.deals_total)}
          </div>
          
          <div className="mt-6 pt-5 border-t border-white/5 flex justify-between items-center text-sm">
            <span className="text-slate-400 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" /> Auto-fixed issues
            </span>
            <span className="text-white font-medium">{dq.deals_duplicate_headers_removed} duplicates removed</span>
          </div>
        </div>

        {/* Work Orders Card */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Work Orders Dataset</h2>
              <p className="text-xs text-slate-400">{dq.wo_total} total records scanned</p>
            </div>
          </div>
          
          <div className="space-y-2">
            {renderIssueRow("Missing Financial Amounts", dq.wo_missing_amounts, dq.wo_total)}
            {renderIssueRow("Missing Schedule Dates", dq.wo_missing_dates, dq.wo_total)}
          </div>
          
          <div className="mt-6 pt-5 border-t border-white/5 flex justify-between items-center text-sm">
            <span className="text-slate-400 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-emerald-400" /> Auto-fixed issues
            </span>
            <span className="text-white font-medium">{dq.wo_excel_errors_fixed} #VALUE! errors resolved</span>
          </div>
        </div>
      </div>

      {/* Cleaning Steps Log */}
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
          <Clock className="w-5 h-5 text-brand-400" />
          Automated Cleaning Log
        </h3>
        
        <div className="space-y-3">
          {dq.cleaning_steps.length > 0 ? (
            dq.cleaning_steps.map((step, index) => (
              <div key={index} className="flex items-start gap-3 p-3 rounded-xl bg-surface-800/50 border border-white/5 hover:border-brand-500/20 transition-colors">
                <div className="mt-0.5 rounded-full bg-emerald-500/20 p-1">
                  <Check className="w-3 h-3 text-emerald-400" />
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{step}</p>
              </div>
            ))
          ) : (
            <div className="text-center p-6 text-slate-500 flex flex-col items-center">
              <CheckCircle className="w-8 h-8 mb-2 opacity-50" />
              <p>No automated cleaning steps recorded in this session.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
