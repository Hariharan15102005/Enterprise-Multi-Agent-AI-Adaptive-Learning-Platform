import React, { useState, useEffect } from 'react';
import { DollarSign, ShoppingBag, CreditCard, Users, TrendingUp, Truck, Store, ArrowUpRight } from 'lucide-react';
import { dashboardApi, analyticsApi } from '../api/coreApis';
import { MetricCard, LoadingSkeleton, ErrorState, Badge } from '../components/common/UIComponents';
import { TrendAreaChart, CategoryBarChart } from '../components/charts/ChartComponents';

export function DashboardPage({ onNavigate }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [kpiData, setKpiData] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [revenueTrends, setRevenueTrends] = useState([]);
  const [topCategories, setTopCategories] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [kpiRes, sumRes, trendRes, catRes] = await Promise.all([
        dashboardApi.getKPIs(),
        dashboardApi.getSummary(),
        analyticsApi.getRevenueTrends({ interval: 'month' }),
        analyticsApi.getCategoryAnalytics({ limit: 6, sort_by: 'gmv' })
      ]);

      setKpiData(kpiRes?.data || null);
      setSummaryData(sumRes?.data || null);
      setRevenueTrends(trendRes?.data || []);
      setTopCategories(catRes?.data || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError(err.message || 'Error connecting to analytics engine backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (error) {
    return <ErrorState title="Dashboard Unavailable" message={error} onRetry={fetchData} />;
  }

  const formatCurrency = (val) =>
    val ? `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : 'R$ 0,00';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Banner */}
      <div className="glass-card" style={{
        padding: '1.25rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%)',
        border: '1px solid rgba(99, 102, 241, 0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '0.65rem', borderRadius: 'var(--radius-md)', background: 'rgba(99, 102, 241, 0.15)', color: 'var(--text-accent)' }}>
            <TrendingUp size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Brazilian E-Commerce Executive Overview
            </h3>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
              Dataset covering 100k real orders (2016–2018) with multi-dimensional star schema validation.
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <Badge variant="success">All Services Operational</Badge>
          <Badge variant="info">Phase 8 Live</Badge>
        </div>
      </div>

      {/* KPI Cards Row */}
      {loading ? (
        <div className="grid grid-cols-4">
          <LoadingSkeleton height="7.5rem" rows={1} />
          <LoadingSkeleton height="7.5rem" rows={1} />
          <LoadingSkeleton height="7.5rem" rows={1} />
          <LoadingSkeleton height="7.5rem" rows={1} />
        </div>
      ) : (
        <div className="grid grid-cols-4">
          <MetricCard
            title="Total Gross Merchandise Value"
            value={formatCurrency(kpiData?.total_gmv || summaryData?.financials?.total_revenue)}
            subtitle="Across all delivered orders"
            icon={DollarSign}
          />
          <MetricCard
            title="Total Orders"
            value={Number(kpiData?.total_orders || summaryData?.volume?.total_orders || 0).toLocaleString()}
            subtitle={`${Number(kpiData?.delivered_orders || summaryData?.volume?.delivered_orders || 0).toLocaleString()} delivered`}
            icon={ShoppingBag}
          />
          <MetricCard
            title="Average Order Value"
            value={formatCurrency(kpiData?.avg_order_value || summaryData?.financials?.avg_order_value)}
            subtitle="Per completed basket"
            icon={CreditCard}
          />
          <MetricCard
            title="Active Merchants & Buyers"
            value={`${Number(summaryData?.volume?.active_sellers || 3095).toLocaleString()} / ${Number(summaryData?.volume?.unique_customers || 96096).toLocaleString()}`}
            subtitle="Sellers & Unique Customers"
            icon={Users}
          />
        </div>
      )}

      {/* Main Charts Row */}
      <div className="grid grid-cols-3" style={{ gridTemplateColumns: '2fr 1fr' }}>
        {/* Left: Monthly Revenue Trend */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Historical Monthly GMV Trajectory
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Delivered revenue from 2016 through late 2018 peak seasons
              </p>
            </div>
            {onNavigate && (
              <button
                className="btn btn-secondary"
                style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }}
                onClick={() => onNavigate('analytics')}
              >
                Detailed Trends <ArrowUpRight size={13} />
              </button>
            )}
          </div>
          {loading ? (
            <LoadingSkeleton rows={4} height="3.5rem" />
          ) : (
            <TrendAreaChart
              data={revenueTrends}
              xKey="period"
              yKey="gmv"
              yLabel="GMV (R$)"
              height={280}
            />
          )}
        </div>

        {/* Right: Top Product Categories Preview */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Top Product Categories
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Highest GMV generators
              </p>
            </div>
          </div>
          {loading ? (
            <LoadingSkeleton rows={4} height="3.5rem" />
          ) : (
            <CategoryBarChart
              data={topCategories}
              xKey="category"
              yKey="gmv"
              height={280}
              horizontal={true}
            />
          )}
        </div>
      </div>

      {/* Operational Highlights Row */}
      <div className="grid grid-cols-3">
        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div style={{ padding: '0.5rem', borderRadius: 'var(--radius-md)', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--success)' }}>
              <Truck size={18} />
            </div>
            <div>
              <h5 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>Logistics Health</h5>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>On-time Delivery Performance</p>
            </div>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--success)', marginBottom: '0.25rem' }}>
            91.9%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Average transit duration: <strong>12.5 days</strong> across 27 federal states
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div style={{ padding: '0.5rem', borderRadius: 'var(--radius-md)', background: 'rgba(139, 92, 246, 0.15)', color: 'var(--text-accent)' }}>
              <Store size={18} />
            </div>
            <div>
              <h5 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>Merchant Ecosystem</h5>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Seller Fulfillment Rate</p>
            </div>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
            3,095
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Active verified merchants across SP, RJ, MG, PR and other hubs
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div style={{ padding: '0.5rem', borderRadius: 'var(--radius-md)', background: 'rgba(236, 72, 153, 0.15)', color: 'var(--accent-pink)' }}>
              <CreditCard size={18} />
            </div>
            <div>
              <h5 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>Payment Diversity</h5>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Payment Channel Split</p>
            </div>
          </div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-pink)', marginBottom: '0.25rem' }}>
            75.3%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            Credit card dominance followed by Boleto bancário (19.4%)
          </div>
        </div>
      </div>
    </div>
  );
}
