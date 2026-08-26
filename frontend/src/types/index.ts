export interface Case {
  id: string;
  customer_name: string;
  customer_phone: string;
  payment_type: string;
  payment_amount: number;
  failure_reason: string;
  value_tier: string;
  risk_profile: string;
  difficulty_label: string;
  assigned_channel: string | null;
  contact_attempts: number;
  payment_retries: number;
  consecutive_refusals: number;
  do_not_contact: boolean;
  total_discount_given: number;
  extension_days_given: number;
  outcome: string | null;
  amount_recovered: number;
  created_at: string | null;
  detected_at?: string | null;
  resolved_at: string | null;
}

export interface BatchMetrics {
  total_cases: number;
  total_revenue_at_risk: number;
  gross_revenue_recovered: number;
  total_discounts_given: number;
  net_revenue_recovered: number;
  autonomous_recovery_rate: number;
  human_assisted_recovery_rate: number;
  blocked_action_count: number;
  modified_action_count: number;
  escalation_count: number;
  false_positive_block_cost: number;
  escalation_rate: number;
  average_recovery_time_seconds: number;
  budget_exhaustion_case_index: number | null;
  recovery_rate: number;
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  details: Record<string, unknown> | null;
  decision: string | null;
  reason: string | null;
}

export interface BudgetTransaction {
  case_id: string;
  amount: number;
  budget_before: number;
  budget_after: number;
  description: string | null;
  created_at: string | null;
}

export interface BudgetState {
  total_budget: number;
  spent: number;
  remaining: number;
  is_exhausted: boolean;
  exhausted_at_case: string | null;
  transactions: BudgetTransaction[];
}

export interface Decision {
  id: number;
  case_id: string;
  action_type: string;
  discount_pct: number | null;
  extension_days: number | null;
  reasoning: string;
  decision: string;
  decision_reason: string | null;
  rule_triggered: string | null;
  modified_discount_pct: number | null;
  modified_extension_days: number | null;
  budget_remaining: number | null;
  created_at: string | null;
}
