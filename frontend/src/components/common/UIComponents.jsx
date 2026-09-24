import React from 'react';
import { AlertTriangle, RefreshCw, Inbox } from 'lucide-react';

export function Badge({ variant = 'neutral', children, className = '' }) {
  return (
    <span className={`badge badge-${variant} ${className}`}>
      {children}
    </span>
  );
}

export function MetricCard({ title, value, subtitle, icon: Icon, trend, trendLabel, variant = 'primary', loading = false }) {
  if (loading) {
    return (
      <div className="glass-card" style={{ padding: '1.25rem' }}>
        <div className="skeleton" style={{ height: '1rem', width: '40%', marginBottom: '0.75rem' }} />
        <div className="skeleton" style={{ height: '2rem', width: '70%', marginBottom: '0.5rem' }} />
        <div className="skeleton" style={{ height: '0.85rem', width: '50%' }} />
      </div>
    );
  }

  return (
    <div className="glass-card glass-card-interactive" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{ padding: '0.45rem', borderRadius: 'var(--radius-md)', background: 'var(--bg-glass)', border: '1px solid var(--border-subtle)', color: 'var(--text-accent)' }}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <div>
        <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em', marginBottom: '0.25rem' }}>
          {value}
        </div>
        {(subtitle || trendLabel) && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
            {trend && (
              <span style={{ color: trend > 0 ? 'var(--success)' : (trend < 0 ? 'var(--danger)' : 'var(--text-muted)'), fontWeight: 600 }}>
                {trend > 0 ? `+${trend}%` : `${trend}%`}
              </span>
            )}
            <span>{subtitle || trendLabel}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export function LoadingSkeleton({ rows = 4, height = '2rem' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%' }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ height, width: '100%' }} />
      ))}
    </div>
  );
}

export function ErrorState({ title = 'Failed to load data', message, onRetry }) {
  return (
    <div className="glass-card" style={{ padding: '2.5rem 1.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
      <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-full)', background: 'var(--danger-bg)', color: 'var(--danger)' }}>
        <AlertTriangle size={28} />
      </div>
      <div>
        <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{title}</h4>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', maxWidth: '400px' }}>
          {message || 'An error occurred while fetching information from the analytical backend.'}
        </p>
      </div>
      {onRetry && (
        <button className="btn btn-secondary" onClick={onRetry}>
          <RefreshCw size={14} /> Retry Connection
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title = 'No data available', message }) {
  return (
    <div className="glass-card" style={{ padding: '2.5rem 1.5rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
      <div style={{ padding: '0.75rem', borderRadius: 'var(--radius-full)', background: 'var(--bg-glass)', color: 'var(--text-muted)' }}>
        <Inbox size={28} />
      </div>
      <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{title}</h4>
      <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', maxWidth: '350px' }}>
        {message || 'There are no records matching your current filter criteria.'}
      </p>
    </div>
  );
}
