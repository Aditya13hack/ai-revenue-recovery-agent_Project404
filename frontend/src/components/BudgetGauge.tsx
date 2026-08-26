import type { BudgetState } from '../types';

interface BudgetGaugeProps {
  budget?: BudgetState | null;
}

export default function BudgetGauge({ budget }: BudgetGaugeProps) {
  if (!budget) return null;

  const percentLeft = Math.max(0, (budget.remaining / budget.total_budget) * 100);
  
  let color = 'bg-green-500';
  if (percentLeft < 20) color = 'bg-red-500';
  else if (percentLeft < 50) color = 'bg-yellow-500';

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex justify-between items-end mb-2">
        <h3 className="text-gray-400 text-sm font-medium uppercase">Recovery Budget</h3>
        <span className="text-xl font-bold text-gray-200">Rs.{budget.remaining.toLocaleString()}</span>
      </div>
      
      <div className="w-full bg-gray-900 rounded-full h-3 mb-2 border border-gray-700">
        <div 
          className={`h-3 rounded-full transition-all duration-500 ${color}`} 
          style={{ width: `${percentLeft}%` }}
        ></div>
      </div>
      
      <div className="flex justify-between text-xs text-gray-500 mb-2">
        <span>Spent: Rs.{budget.spent.toLocaleString()}</span>
        <span>Total: Rs.{budget.total_budget.toLocaleString()}</span>
      </div>

      {budget.is_exhausted && (
        <div className="bg-red-900/50 border border-red-800 text-red-300 p-2 rounded text-xs mb-3 font-medium text-center">
          BUDGET EXHAUSTED {budget.exhausted_at_case ? `at ${budget.exhausted_at_case}` : ''}
        </div>
      )}

      {budget.transactions && budget.transactions.length > 0 && (
        <div className="mt-2">
          <h4 className="text-xs text-gray-400 mb-2 font-medium">Recent Transactions</h4>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {budget.transactions.slice(-5).reverse().map((tx, i) => (
              <div key={i} className="flex justify-between text-xs py-1 border-b border-gray-700/50">
                <span className="text-gray-400 truncate w-24">{tx.case_id}</span>
                <span className="text-gray-500 truncate flex-1 mx-2">{tx.description}</span>
                <span className="text-red-400">-Rs.{tx.amount.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
