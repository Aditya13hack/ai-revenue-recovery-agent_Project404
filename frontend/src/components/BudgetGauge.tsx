import type { BudgetState } from '../types';

interface BudgetGaugeProps {
  budget?: BudgetState | null;
}

export default function BudgetGauge({ budget }: BudgetGaugeProps) {
  if (!budget || typeof budget.total_budget !== 'number' || typeof budget.remaining !== 'number') {
    return null;
  }

  const totalBudget = budget.total_budget || 50000;
  const remaining = budget.remaining ?? totalBudget;
  const spent = budget.spent ?? 0;
  const percentLeft = Math.max(0, Math.min(100, (remaining / totalBudget) * 100));
  
  let color = 'bg-gradient-to-r from-emerald-500 to-teal-500';
  let badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (percentLeft < 20) {
    color = 'bg-gradient-to-r from-rose-500 to-red-500';
    badgeColor = 'bg-rose-50 text-rose-700 border-rose-200';
  } else if (percentLeft < 50) {
    color = 'bg-gradient-to-r from-amber-500 to-yellow-500';
    badgeColor = 'bg-amber-50 text-amber-700 border-amber-200';
  }

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs">
      <div className="flex justify-between items-end mb-3">
        <div>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Merchant Campaign Incentive Budget</span>
          <h3 className="text-sm font-bold text-slate-800 mt-0.5">Budget Capacity & Live Expenditure</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
            {percentLeft.toFixed(0)}% Remaining
          </span>
          <span className="text-lg font-black text-slate-900">₹{remaining.toLocaleString()}</span>
        </div>
      </div>
      
      <div className="w-full bg-slate-100 rounded-full h-3 mb-2.5 overflow-hidden p-0.5 border border-slate-200/60">
        <div 
          className={`h-2 rounded-full transition-all duration-500 shadow-xs ${color}`} 
          style={{ width: `${percentLeft}%` }}
        ></div>
      </div>
      
      <div className="flex justify-between text-xs text-slate-500 font-medium mb-3">
        <span>Spent: <strong className="text-slate-700">₹{spent.toLocaleString()}</strong></span>
        <span>Total Cap: <strong className="text-slate-700">₹{totalBudget.toLocaleString()}</strong></span>
      </div>

      {budget.is_exhausted && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 p-2.5 rounded-xl text-xs mb-3 font-semibold text-center flex items-center justify-center gap-2">
          <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
          <span>CAMPAIGN BUDGET EXHAUSTED {budget.exhausted_at_case ? `at ${budget.exhausted_at_case}` : ''} — Zero-discount policy enforced.</span>
        </div>
      )}

      {budget.transactions && budget.transactions.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100">
          <h4 className="text-xs text-slate-500 mb-2 font-bold uppercase tracking-wider">Live Budget Ledger (Recent Deductions)</h4>
          <div className="space-y-1.5 max-h-32 overflow-y-auto pr-1">
            {budget.transactions.slice(-5).reverse().map((tx, i) => (
              <div key={i} className="flex justify-between items-center text-xs py-1.5 px-2.5 bg-slate-50 hover:bg-slate-100/80 rounded-lg border border-slate-100 transition-colors">
                <span className="font-mono font-bold text-indigo-600 truncate w-24">{tx.case_id}</span>
                <span className="text-slate-600 truncate flex-1 mx-2 text-[11px]">{tx.description}</span>
                <span className="font-bold text-rose-600">-₹{(tx.amount ?? 0).toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
