import React from 'react';
import {
  LayoutDashboard,
  BarChart3,
  Users,
  Truck,
  Store,
  Brain,
  Bot,
  ShieldCheck,
  Activity,
  Sparkles,
  ChevronRight
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Executive Dashboard', icon: LayoutDashboard, category: 'Overview' },
  { id: 'analytics', label: 'Deep Analytics', icon: BarChart3, category: 'Core Business' },
  { id: 'customers', label: 'Customer Intelligence', icon: Users, category: 'Core Business' },
  { id: 'logistics', label: 'Logistics & SLA', icon: Truck, category: 'Core Business' },
  { id: 'sellers', label: 'Seller Leaderboard', icon: Store, category: 'Core Business' },
  { id: 'ml', label: 'Predictive ML Engine', icon: Brain, category: 'Intelligence' },
  { id: 'ai', label: 'AI Analyst (NL2SQL)', icon: Bot, category: 'Intelligence' },
  { id: 'quality', label: 'Data Quality & Governance', icon: ShieldCheck, category: 'Platform' },
  { id: 'health', label: 'System Health & APIs', icon: Activity, category: 'Platform' },
];

export function Sidebar({ currentTab, onSelectTab }) {
  // Group nav items by category
  const categories = ['Overview', 'Core Business', 'Intelligence', 'Platform'];

  return (
    <aside style={{
      width: '260px',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border-subtle)',
      display: 'flex',
      flexDirection: 'column',
      flexShrink: 0,
      minHeight: '100vh',
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        <div style={{
          width: '38px',
          height: '38px',
          borderRadius: 'var(--radius-md)',
          background: 'var(--primary-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)'
        }}>
          <Sparkles size={20} />
        </div>
        <div>
          <h1 style={{ fontSize: '1.125rem', fontWeight: 800, letterSpacing: '-0.03em', color: '#fff' }}>
            Olist<span style={{ color: 'var(--text-accent)' }}>IQ</span>
          </h1>
          <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            Enterprise Decision AI
          </p>
        </div>
      </div>

      {/* Navigation List */}
      <div style={{ padding: '1rem 0.75rem', flex: 1, display: 'flex', flexDirection: 'column', gap: '1.25rem', overflowY: 'auto' }}>
        {categories.map((category) => {
          const items = NAV_ITEMS.filter((item) => item.category === category);
          return (
            <div key={category}>
              <div style={{
                padding: '0 0.75rem 0.4rem',
                fontSize: '0.6875rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em'
              }}>
                {category}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                {items.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => onSelectTab(item.id)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        borderRadius: 'var(--radius-md)',
                        background: isActive ? 'rgba(99, 102, 241, 0.14)' : 'transparent',
                        border: isActive ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
                        color: isActive ? '#fff' : 'var(--text-secondary)',
                        fontSize: '0.85rem',
                        fontWeight: isActive ? 600 : 500,
                        cursor: 'pointer',
                        transition: 'all var(--transition-fast)',
                        textAlign: 'left',
                        outline: 'none',
                      }}
                      onMouseEnter={(e) => {
                        if (!isActive) e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                      }}
                      onMouseLeave={(e) => {
                        if (!isActive) e.currentTarget.style.background = 'transparent';
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <Icon size={17} color={isActive ? 'var(--text-accent)' : 'var(--text-muted)'} />
                        <span>{item.label}</span>
                      </div>
                      {isActive && <ChevronRight size={14} color="var(--text-accent)" />}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Info */}
      <div style={{
        padding: '1rem 1.25rem',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '0.75rem',
        color: 'var(--text-muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <span>API v1.0.0</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--success)' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }} />
          Online
        </span>
      </div>
    </aside>
  );
}
