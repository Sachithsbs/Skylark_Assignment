import { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { 
  TrendingUp, Target, Briefcase, FileSpreadsheet, Activity, RefreshCw 
} from 'lucide-react';
import { getDashboard } from '../services/api';
import { AnalyticsDashboard } from '../types';

const COLORS = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#f43f5e', '#8b5cf6'];

const formatINR = (value: number) => {
  if (value >= 1e7) return `₹${(value / 1e7).toFixed(1)}Cr`;
  if (value >= 1e5) return `₹${(value / 1e5).toFixed(1)}L`;
  return `₹${value.toLocaleString('en-IN')}`;
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card p-3 border border-white/10 shadow-xl z-50">
        <p className="text-white font-medium mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 text-sm mb-1 last:mb-0">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-slate-300">{entry.name}:</span>
            <span className="text-white font-semibold stat-value">
              {entry.name.toLowerCase().includes('value') || entry.name.toLowerCase().includes('billed') || entry.name.toLowerCase().includes('collected')
                ? formatINR(entry.value) 
                : entry.value.toLocaleString()}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const DashboardCharts = () => {
  const [data, setData] = useState<AnalyticsDashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const result = await getDashboard();
      setData(result);
      setLastUpdated(new Date());
    } catch (error) {
      console.error("Failed to fetch dashboard data", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (isLoading && !data) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="animate-spin-slow w-10 h-10 border-4 border-brand-500 border-t-transparent rounded-full glow-blue" />
      </div>
    );
  }

  if (!data) return <div className="text-center text-rose-400 mt-10">Failed to load dashboard data.</div>;

  return (
    <div className="space-y-6 pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">Executive Dashboard</h1>
          <p className="text-sm text-slate-400">Live overview of business metrics</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-500">
            Updated: {lastUpdated.toLocaleTimeString()}
          </span>
          <button 
            onClick={fetchData}
            disabled={isLoading}
            className="p-2 glass-card hover:bg-white/10 text-slate-300 transition-colors rounded-lg disabled:opacity-50 flex items-center gap-2 text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-brand-500/10 rounded-full blur-xl group-hover:bg-brand-500/20 transition-colors" />
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-sm text-slate-400 font-medium mb-1">Open Pipeline</p>
              <h3 className="text-2xl font-bold text-white stat-value">{formatINR(data.deal_summary.total_pipeline_value)}</h3>
            </div>
            <div className="w-10 h-10 rounded-xl bg-brand-500/20 flex items-center justify-center text-brand-400">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-4"><span className="text-brand-400 font-medium">{data.deal_summary.open}</span> active deals</p>
        </div>

        <div className="glass-card p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl group-hover:bg-emerald-500/20 transition-colors" />
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-sm text-slate-400 font-medium mb-1">Win Rate</p>
              <h3 className="text-2xl font-bold text-white stat-value">{(data.deal_summary.win_rate * 100).toFixed(1)}%</h3>
            </div>
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Target className="w-5 h-5" />
            </div>
          </div>
          <div className="w-full bg-surface-900/50 rounded-full h-1.5 mt-5">
            <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${data.deal_summary.win_rate * 100}%` }} />
          </div>
        </div>

        <div className="glass-card p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-cyan-500/10 rounded-full blur-xl group-hover:bg-cyan-500/20 transition-colors" />
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-sm text-slate-400 font-medium mb-1">Active Work Orders</p>
              <h3 className="text-2xl font-bold text-white stat-value">{data.work_order_summary.ongoing}</h3>
            </div>
            <div className="w-10 h-10 rounded-xl bg-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Briefcase className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-4">Out of <span className="text-white font-medium">{data.work_order_summary.total_orders}</span> total orders</p>
        </div>

        <div className="glass-card p-5 relative overflow-hidden group">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-amber-500/10 rounded-full blur-xl group-hover:bg-amber-500/20 transition-colors" />
          <div className="flex items-start justify-between mb-2">
            <div>
              <p className="text-sm text-slate-400 font-medium mb-1">AR Outstanding</p>
              <h3 className="text-2xl font-bold text-white stat-value">{formatINR(data.work_order_summary.ar_outstanding)}</h3>
            </div>
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center text-amber-400">
              <FileSpreadsheet className="w-5 h-5" />
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-4">Total Contract Value: <span className="text-white font-medium">{formatINR(data.work_order_summary.total_contract_value)}</span></p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <div className="glass-card p-5 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
            <Activity className="w-5 h-5 text-brand-400" />
            Revenue Trend (Billed vs Collected)
          </h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.monthly_revenue} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="month" stroke="#94a3b8" tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} />
                <YAxis stroke="#94a3b8" tickFormatter={(value) => formatINR(value)} tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Line type="monotone" dataKey="billed" name="Billed Value" stroke="#3b82f6" strokeWidth={3} dot={{r: 4, fill: '#0d1729', strokeWidth: 2}} activeDot={{r: 6, strokeWidth: 0, fill: '#3b82f6'}} />
                <Line type="monotone" dataKey="collected" name="Collected Value" stroke="#10b981" strokeWidth={3} dot={{r: 4, fill: '#0d1729', strokeWidth: 2}} activeDot={{r: 6, strokeWidth: 0, fill: '#10b981'}} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Pipeline Funnel */}
        <div className="glass-card p-5">
          <h3 className="text-lg font-semibold text-white mb-6">Pipeline by Stage</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.pipeline_stages} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" hide />
                <YAxis dataKey="stage" type="category" stroke="#94a3b8" tick={{fill: '#94a3b8', fontSize: 12}} axisLine={false} tickLine={false} width={100} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Bar dataKey="value" name="Pipeline Value" radius={[0, 4, 4, 0]} barSize={24}>
                  {data.pipeline_stages.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Sector Breakdown Deals */}
        <div className="glass-card p-5">
          <h3 className="text-lg font-semibold text-white mb-6">Deal Value by Sector</h3>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.sector_breakdown_deals}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                  nameKey="sector"
                  stroke="rgba(255,255,255,0.05)"
                >
                  {data.sector_breakdown_deals.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip content={<CustomTooltip />} />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
