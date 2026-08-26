import { useMetrics, useBudget } from '../hooks/useApi';
import BudgetGauge from './BudgetGauge';

export default function MetricsPanel() {
  const { data: metrics, loading: metricsLoading } = useMetrics();
  const { data: budget, loading: budgetLoading } = useBudget();

  if (metricsLoading || budgetLoading) return <div className="text-gray-400 p-8 text-center bg-gray-900 rounded-xl border border-gray-800 animate-pulse">Loading recovery metrics...</div>;
  if (!metrics) return <div className="text-red-400 p-6 bg-gray-900 rounded-xl border border-red-900/50">Error loading metrics from API</div>;

  const recoveryPct = (metrics.recovery_rate * 100);

  return (
    <div className="space-y-6">
      {/* Headline Banner */}
      <div className="bg-gradient-to-r from-gray-900 via-gray-850 to-gray-900 p-6 rounded-xl border border-gray-800 shadow-lg text-center">
        <span className="text-xs uppercase tracking-widest text-blue-400 font-bold">Buildathon Track 03 Proof of Value</span>
        <h2 className="text-2xl md:text-3xl font-extrabold mt-1 text-gray-100">
          <span className="text-red-400">₹{metrics.total_revenue_at_risk.toLocaleString()}</span>
          <span className="text-gray-500 mx-3">→</span>
          <span className="text-green-400 font-black">₹{metrics.net_revenue_recovered.toLocaleString()}</span>
          <span className="text-gray-400 font-medium text-lg ml-2">recovered</span>
          <span className="text-gray-600 mx-3 font-light">|</span>
          <span className="text-yellow-400 font-bold">{metrics.blocked_action_count + metrics.modified_action_count}</span>
          <span className="text-gray-400 text-lg ml-1.5 font-medium">unsafe AI actions prevented</span>
        </h2>
      </div>

      {/* Hero Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Revenue at Risk */}
        <div className="bg-gray-900 rounded-xl p-5 shadow-lg border border-red-900/30 hover:border-red-800/60 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Revenue at Risk</h3>
            <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
          </div>
          <p className="text-3xl font-bold text-red-400 tracking-tight">
            ₹{metrics.total_revenue_at_risk.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </p>
          <p className="text-gray-400 text-xs mt-2 font-medium">{metrics.total_cases} total failed cases</p>
        </div>

        {/* Net Revenue Recovered */}
        <div className="bg-gray-900 rounded-xl p-5 shadow-lg border border-green-900/30 hover:border-green-800/60 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Net Recovered</h3>
            <span className="text-xs font-bold text-green-400 bg-green-950 px-2 py-0.5 rounded border border-green-800/40">ROI +</span>
          </div>
          <p className="text-3xl font-bold text-green-400 tracking-tight">
            ₹{metrics.net_revenue_recovered.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
          </p>
          <p className="text-gray-400 text-xs mt-2 font-medium">Discounts given: ₹{metrics.total_discounts_given.toLocaleString()}</p>
        </div>

        {/* Recovery Rate */}
        <div className="bg-gray-900 rounded-xl p-5 shadow-lg border border-gray-800 hover:border-blue-900/50 transition-colors">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-gray-400 text-xs font-semibold uppercase tracking-wider">Recovery Rate</h3>
            <span className="text-xs font-bold text-blue-400">{recoveryPct.toFixed(1)}%</span>
          </div>
          <p className="text-3xl font-bold text-blue-400 tracking-tight">{recoveryPct.toFixed(1)}%</p>
          <div className="w-full bg-gray-800 rounded-full h-2 mt-3 overflow-hidden">
            <div className="bg-blue-500 h-2 rounded-full transition-all duration-500" style={{ width: `${Math.min(recoveryPct, 100)}%` }}></div>
          </div>
          <p className="text-gray-400 text-xs mt-2 font-medium">
            Autonomous: {(metrics.autonomous_recovery_rate * 100).toFixed(0)}% • Escalated: {(metrics.escalation_rate * 100).toFixed(0)}%
          </p>
        </div>

        {/* Control Plane Guardrails */}
        <div className="bg-gray-900 rounded-xl p-5 shadow-lg border border-gray-800 flex flex-col justify-between">
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-gray-400 text-xs font-medium">Blocked Bad Actions</span>
            <span className="text-lg font-bold text-red-400">{metrics.blocked_action_count}</span>
          </div>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-gray-400 text-xs font-medium">Modified (Capped)</span>
            <span className="text-lg font-bold text-yellow-400">{metrics.modified_action_count}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-400 text-xs font-medium">Human Escalations</span>
            <span className="text-lg font-bold text-orange-400">{metrics.escalation_count}</span>
          </div>
        </div>
      </div>

      {/* Budget Gauge */}
      {budget && <BudgetGauge budget={budget} />}
    </div>
  );
}
