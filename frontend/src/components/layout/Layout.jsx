import React from 'react';
import { Activity, ShieldCheck, Database, Calendar } from 'lucide-react';
import { Sidebar } from './Sidebar';

const TAB_TITLES = {
  dashboard: { title: 'Executive Overview', desc: 'Real-time financial, order, and operational KPIs across Brazilian e-commerce' },
  analytics: { title: 'Deep Analytics & Insights', desc: 'Category GMV breakdown, revenue trends, and payment distributions' },
  customers: { title: 'Customer Intelligence', desc: 'RFM cluster segmentation, geographic state shares, and customer lifetime value' },
  logistics: { title: 'Logistics & Delivery SLA', desc: 'Doorstep transit performance, carrier durations, and delay breach analytics' },
  sellers: { title: 'Seller Performance', desc: 'Merchant revenue rankings, SLA compliance ratings, and merchant tiers' },
  ml: { title: 'Predictive ML Intelligence', desc: 'Supervised delay classifiers, satisfaction models, 30-day forecasts, and anomalies' },
  ai: { title: 'AI Analyst (LangGraph NL2SQL)', desc: 'Grounded natural language business query planner with safety guardrails' },
  quality: { title: 'Data Quality & Warehouse Health', desc: 'Warehouse profiling, table row counts, and referential integrity scores' },
  health: { title: 'System Health & REST Endpoints', desc: 'Service health check, latency monitoring, and OpenAPI endpoint catalog' },
};

export function Header({ currentTab, onSelectTab }) {
  const current = TAB_TITLES[currentTab] || { title: 'Analytics', desc: 'Platform Decision Intelligence' };

  return (
    <header style={{
      height: '70px',
      background: 'rgba(17, 24, 39, 0.75)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border-subtle)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 2rem',
      position: 'sticky',
      top: 0,
      zIndex: 20
    }}>
      <div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          {current.title}
        </h2>
        <p style={{ fontSize: '0.78125rem', color: 'var(--text-muted)' }}>
          {current.desc}
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 0.85rem',
          background: 'var(--bg-glass)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-full)',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)'
        }}>
          <Database size={14} color="var(--text-accent)" />
          <span>Warehouse: <strong style={{ color: 'var(--text-primary)' }}>100k Orders</strong></span>
        </div>

        <button
          className="btn btn-secondary"
          onClick={() => onSelectTab('ai')}
          style={{ padding: '0.45rem 0.9rem', fontSize: '0.8125rem' }}
        >
          <span>Ask AI Analyst</span>
        </button>
      </div>
    </header>
  );
}

export function Layout({ currentTab, onSelectTab, children }) {
  return (
    <div className="app-container">
      <Sidebar currentTab={currentTab} onSelectTab={onSelectTab} />
      <div className="main-content">
        <Header currentTab={currentTab} onSelectTab={onSelectTab} />
        <main className="page-container">
          {children}
        </main>
      </div>
    </div>
  );
}
