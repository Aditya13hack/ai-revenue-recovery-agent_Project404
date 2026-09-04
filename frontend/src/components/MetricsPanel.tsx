import { useMetrics, useBudget } from '../hooks/useApi';
import BudgetGauge from './BudgetGauge';

interface MetricsPanelProps {
  dataMode: string;
}

export default function MetricsPanel({ dataMode }: MetricsPanelProps) {
  const { data: metrics, loading: metricsLoading } = useMetrics(dataMode);
  const { data: budget, loading: budgetLoading } = useBudget();

  if (metricsLoading || budgetLoading) {
    return (
      <div className="text-slate-400 p-8 text-center bg-white rounded-xl border border-slate-200 shadow-xs animate-pulse">
        Loading {dataMode === 'live' ? 'Live Razorpay' : dataMode === 'synthetic' ? 'Synthetic Benchmark' : 'All'} metrics...
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-rose-600 p-6 bg-rose-50 rounded-xl border border-rose-200">
        Error loading metrics from API
      </div>
    );
  }

  const atRisk = metrics.total_revenue_at_risk ?? 0;
  const recovered = metrics.net_revenue_recovered ?? 0;
  const discounts = metrics.total_discounts_given ?? 0;
  const recoveryPct = (metrics.recovery_rate ?? 0) * 100;
  const totalCases = metrics.total_cases ?? 0;
  const blockedCount = metrics.blocked_action_count ?? 0;
  const modifiedCount = metrics.modified_action_count ?? 0;
  const escalationCount = metrics.escalation_count ?? 0;
  const autoRate = (metrics.autonomous_recovery_rate ?? 0) * 100;

  return (
    <div className="space-y-5">

      <div className="bg-gradient-to-r from-slate-50 via-indigo-50/40 to-slate-50 p-6 rounded-xl border border-slate-200/80 shadow-xs text-center relative overflow-hidden">
        <div className="flex items-center justify-center gap-2 mb-2">
          {dataMode === 'live' ? (
            <span className="inline-flex items-center gap-1.5 text-xs uppercase tracking-wider text-emerald-700 font-semibold bg-emerald-50 px-3 py-0.5 rounded-full border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              Live Pipeline Active
            </span>
          ) : dataMode === 'synthetic' ? (
            <span className="inline-flex items-center gap-1.5 text-xs uppercase tracking-wider text-indigo-700 font-semibold bg-indigo-50 px-3 py-0.5 rounded-full border border-indigo-200">
              Benchmark Verification
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 text-xs uppercase tracking-wider text-slate-700 font-semibold bg-slate-100 px-3 py-0.5 rounded-full border border-slate-200">
              Combined Portfolio Overview
            </span>
          )}
        </div>

        <h2 className="text-2xl md:text-3xl font-extrabold mt-1 text-slate-900 tracking-tight">
          <span className="text-rose-600 font-black">₹{atRisk.toLocaleString()}</span>
          <span className="text-slate-400 mx-3 font-light">→</span>
          <span className="text-emerald-600 font-black">₹{recovered.toLocaleString()}</span>
          <span className="text-slate-600 font-medium text-base md:text-lg ml-2">net recovered</span>
          <span className="text-slate-300 mx-3 font-light">|</span>
          <span className="text-amber-600 font-bold">{blockedCount + modifiedCount}</span>
          <span className="text-slate-600 text-base md:text-lg ml-1.5 font-medium">unsafe AI actions prevented</span>
        </h2>
      </div>


      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

        <div className="bg-white rounded-xl p-5 shadow-xs border border-slate-200 hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-slate-500 text-xs font-bold uppercase tracking-wider">Revenue at Risk</h3>
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
          </div>
          <p className="text-2xl font-black text-rose-600 tracking-tight">
            ₹{atRisk.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </p>
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 text-xs">
            <span className="text-slate-500">Failed Volume</span>
            <span className="font-semibold text-slate-700">{totalCases} cases</span>
          </div>
        </div>


        <div className="bg-white rounded-xl p-5 shadow-xs border border-slate-200 hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-slate-500 text-xs font-bold uppercase tracking-wider">Net Recovered</h3>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
              Positive ROI
            </span>
          </div>
          <p className="text-2xl font-black text-emerald-600 tracking-tight">
            ₹{recovered.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </p>
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 text-xs">
            <span className="text-slate-500">Discounts Incurred</span>
            <span className="font-semibold text-slate-700">₹{discounts.toLocaleString()}</span>
          </div>
        </div>


        <div className="bg-white rounded-xl p-5 shadow-xs border border-slate-200 hover:border-slate-300 transition-all">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-slate-500 text-xs font-bold uppercase tracking-wider">Recovery Rate</h3>
            <span className="text-xs font-bold text-indigo-600">{recoveryPct.toFixed(1)}%</span>
          </div>
          <p className="text-2xl font-black text-indigo-600 tracking-tight">{recoveryPct.toFixed(1)}%</p>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2.5 overflow-hidden">
            <div 
              className="bg-indigo-600 h-1.5 rounded-full transition-all duration-500" 
              style={{ width: `${Math.min(recoveryPct, 100)}%` }}
            ></div>
          </div>
          <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 text-xs">
            <span className="text-slate-500">Autonomous</span>
            <span className="font-semibold text-slate-700">{autoRate.toFixed(0)}%</span>
          </div>
        </div>


        <div className="bg-white rounded-xl p-5 shadow-xs border border-slate-200 hover:border-slate-300 transition-all flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2.5">
              <h3 className="text-slate-500 text-xs font-bold uppercase tracking-wider">Control Plane</h3>
              <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
                8 Rules Active
              </span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-600">Blocked Actions</span>
                <span className="font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">{blockedCount}</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-600">Modified (Capped)</span>
                <span className="font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">{modifiedCount}</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-600">Escalated</span>
                <span className="font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded border border-orange-200">{escalationCount}</span>
              </div>
            </div>
          </div>
        </div>
      </div>


      {budget && <BudgetGauge budget={budget} />}
    </div>
  );
}
