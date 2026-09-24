import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, DollarSign, CreditCard, Sparkles, Filter, RefreshCw } from 'lucide-react';
import { analyticsApi } from '../api/coreApis';
import { MetricCard, LoadingSkeleton, ErrorState, Badge } from '../components/common/UIComponents';
import { TrendAreaChart, CategoryBarChart, PaymentDonutChart } from '../components/charts/ChartComponents';

export function AnalyticsPage() {
  const [interval, setInterval] = useState('month');
  const [categorySort, setCategorySort] = useState('gmv');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [trends, setTrends] = useState([]);
  const [categories, setCategories] = useState([]);
  const [payments, setPayments] = useState([]);
  const [insights, setInsights] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [trendRes, catRes, payRes, insRes] = await Promise.all([
        analyticsApi.getRevenueTrends({ interval }),
        analyticsApi.getCategoryAnalytics({ limit: 12, sort_by: categorySort }),
        analyticsApi.getPaymentAnalytics(),
        analyticsApi.getInsights()
      ]);

      setTrends(trendRes?.data || []);
      setCategories(catRes?.data || []);
      setPayments(payRes?.data || []);
      setInsights(insRes?.data || []);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError(err.message || 'Error fetching analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [interval, categorySort]);

  if (error) {
    return <ErrorState title="Analytics Error" message={error} onRetry={fetchData} />;
  }

  // Calculate totals
  const totalRevenue = categories.reduce((sum, c) => sum + (c.gmv || 0), 0);
  const totalItemsSold = categories.reduce((sum, c) => sum + (c.items_sold || 0), 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Controls Bar */}
      <div className="glass-card" style={{
        padding: '1rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <BarChart3 size={20} color="var(--text-accent)" />
          <span style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Analytics Aggregation Controls
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Interval Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'var(--bg-glass)', padding: '0.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <button
              className="btn"
              style={{
                padding: '0.35rem 0.75rem',
                fontSize: '0.75rem',
                background: interval === 'month' ? 'var(--primary)' : 'transparent',
                color: interval === 'month' ? '#fff' : 'var(--text-secondary)'
              }}
              onClick={() => setInterval('month')}
            >
              Monthly Trends
            </button>
            <button
              className="btn"
              style={{
                padding: '0.35rem 0.75rem',
                fontSize: '0.75rem',
                background: interval === 'day' ? 'var(--primary)' : 'transparent',
                color: interval === 'day' ? '#fff' : 'var(--text-secondary)'
              }}
              onClick={() => setInterval('day')}
            >
              Daily Trends
            </button>
          </div>

          {/* Category Sort Select */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sort Categories:</span>
            <select
              className="input"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', width: 'auto' }}
              value={categorySort}
              onChange={(e) => setCategorySort(e.target.value)}
            >
              <option value="gmv">Gross Merchandise Value (GMV)</option>
              <option value="orders">Total Order Volume</option>
              <option value="late_rate">Delivery Delay Rate</option>
            </select>
          </div>

          <button className="btn btn-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.75rem' }} onClick={fetchData}>
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Top Revenue & Trends Section */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Revenue Trajectory ({interval === 'month' ? 'Monthly' : 'Daily'})
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Historical gross revenue progression over the analyzed e-commerce operational timeline
            </p>
          </div>
          <Badge variant="primary">{trends.length} Data Points</Badge>
        </div>

        {loading ? (
          <LoadingSkeleton rows={5} height="3.5rem" />
        ) : (
          <TrendAreaChart
            data={trends}
            xKey="period"
            yKey="gmv"
            yLabel="GMV (R$)"
            height={320}
          />
        )}
      </div>

      {/* Category Breakdown & Payment Channels */}
      <div className="grid grid-cols-3" style={{ gridTemplateColumns: '2fr 1fr' }}>
        {/* Category Performance */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Category Contribution Ranking
              </h4>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Sorted by {categorySort === 'gmv' ? 'Total GMV (R$)' : (categorySort === 'orders' ? 'Order Volume' : 'Delay Rate (%)')}
              </p>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-accent)', fontWeight: 600 }}>
              Top 12 Categories
            </span>
          </div>

          {loading ? (
            <LoadingSkeleton rows={4} height="3.5rem" />
          ) : (
            <CategoryBarChart
              data={categories}
              xKey="category"
              yKey={categorySort}
              isCurrency={categorySort === 'gmv'}
              height={300}
            />
          )}
        </div>

        {/* Payment Methods */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Payment Channel Share
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Installment & channel volume distribution
            </p>
          </div>

          {loading ? (
            <LoadingSkeleton rows={4} height="3.5rem" />
          ) : (
            <PaymentDonutChart
              data={payments}
              height={300}
              nameKey="payment_type"
              valueKey="total_value"
            />
          )}
        </div>
      </div>

      {/* Automated Business Insights */}
      {insights && insights.length > 0 && (
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
            <Sparkles size={18} color="var(--text-accent)" />
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Automated Business Intelligence Insights
            </h4>
          </div>
          <div className="grid grid-cols-2" style={{ gap: '1rem' }}>
            {insights.map((item, idx) => (
              <div
                key={idx}
                style={{
                  padding: '1rem',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.35rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    {item.title || item.category || `Insight #${idx + 1}`}
                  </span>
                  <Badge variant={item.type === 'positive' ? 'success' : item.type === 'warning' ? 'warning' : 'info'}>
                    {item.type || 'Observation'}
                  </Badge>
                </div>
                <p style={{ fontSize: '0.78125rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {item.description || item.text || item.summary}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
