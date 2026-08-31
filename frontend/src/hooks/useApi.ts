import { useState, useEffect } from 'react';
import type { BatchMetrics, BudgetState, Case, TimelineEvent } from '../types';

export function useMetrics(dataMode: string = 'all') {
  const [data, setData] = useState<BatchMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`/api/metrics?data_mode=${dataMode}`)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [dataMode]);

  return { data, loading, error };
}

export function useCases(filters: { data_mode?: string; outcome?: string; channel?: string; value_tier?: string; page?: number; per_page?: number } = {}) {
  const [data, setData] = useState<{ total: number; page: number; per_page: number; cases: Case[] } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filters.data_mode) params.append('data_mode', filters.data_mode);
    if (filters.outcome) params.append('outcome', filters.outcome);
    if (filters.channel) params.append('channel', filters.channel);
    if (filters.value_tier) params.append('value_tier', filters.value_tier);
    if (filters.page) params.append('page', filters.page.toString());
    if (filters.per_page) params.append('per_page', filters.per_page.toString());

    fetch(`/api/cases?${params.toString()}`)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [filters.data_mode, filters.outcome, filters.channel, filters.value_tier, filters.page, filters.per_page]);

  return { data, loading, error };
}

export function useCaseDetail(id: string | null) {
  const [data, setData] = useState<Case | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetch(`/api/cases/${id}`)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [id]);

  return { data, loading, error };
}

export function useTimeline(id: string | null) {
  const [data, setData] = useState<{ case_id: string; events: TimelineEvent[] } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetch(`/api/cases/${id}/timeline`)
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [id]);

  return { data, loading, error };
}

export function useBudget() {
  const [data, setData] = useState<BudgetState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch('/api/budget')
      .then(res => res.json())
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}
