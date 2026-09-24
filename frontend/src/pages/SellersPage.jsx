import React, { useState, useEffect } from 'react';
import { Store, Award, Star, TrendingUp, Search, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { sellersApi } from '../api/domainApis';
import { MetricCard, LoadingSkeleton, ErrorState, Badge, EmptyState } from '../components/common/UIComponents';

export function SellersPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sellers, setSellers] = useState([]);
  const [sortBy, setSortBy] = useState('sales');
  const [limit, setLimit] = useState(25);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await sellersApi.getLeaderboard({ limit, sort_by: sortBy });
      setSellers(res?.data || []);
    } catch (err) {
      console.error('Failed to load sellers leaderboard:', err);
      setError(err.message || 'Error fetching merchant data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [sortBy, limit]);

  if (error) {
    return <ErrorState title="Seller Leaderboard Unavailable" message={error} onRetry={fetchData} />;
  }

  const formatCurrency = (val) =>
    `R$ ${Number(val || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Controls Header */}
      <div className="glass-card" style={{
        padding: '1rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Store size={20} color="var(--text-accent)" />
          <span style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Merchant Performance & Leaderboard
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sort Leaderboard By:</span>
            <select
              className="input"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', width: 'auto' }}
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="sales">Gross Sales Volume (R$)</option>
              <option value="items_sold">Total Items Sold</option>
              <option value="avg_review_score">Average Review Score</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Limit:</span>
            <select
              className="input"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', width: 'auto' }}
              value={limit}
              onChange={(e) => setLimit(Number(e.target.value))}
            >
              <option value={15}>Top 15</option>
              <option value={25}>Top 25</option>
              <option value={50}>Top 50</option>
            </select>
          </div>

          <button className="btn btn-secondary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.75rem' }} onClick={fetchData}>
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Top Merchant Rankings
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Evaluated across 3,095 sellers on revenue generation and customer satisfaction
            </p>
          </div>
          <Badge variant="primary">{sellers.length} Top Sellers Displayed</Badge>
        </div>

        {loading ? (
          <LoadingSkeleton rows={6} height="2.8rem" />
        ) : sellers.length === 0 ? (
          <EmptyState title="No sellers found" message="No merchant records returned from backend." />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: '60px' }}>Rank</th>
                  <th>Seller ID</th>
                  <th>Location</th>
                  <th>Total Sales (GMV)</th>
                  <th>Items Sold</th>
                  <th>Orders Fulfilled</th>
                  <th>Avg Review Score</th>
                  <th>Merchant Tier</th>
                </tr>
              </thead>
              <tbody>
                {sellers.map((s, idx) => {
                  const rating = Number(s.avg_review_score || 4.0);
                  const isTopTier = idx < 3;

                  return (
                    <tr key={s.seller_id || idx}>
                      <td>
                        <div style={{
                          width: '26px',
                          height: '26px',
                          borderRadius: '50%',
                          background: isTopTier ? 'var(--primary-gradient)' : 'rgba(255, 255, 255, 0.05)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          color: '#fff'
                        }}>
                          {idx + 1}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontFamily: 'monospace', fontSize: '0.8125rem', color: 'var(--text-accent)' }}>
                          {s.seller_id ? `${s.seller_id.substring(0, 16)}...` : 'Unknown'}
                        </div>
                      </td>
                      <td>
                        <div style={{ fontSize: '0.8125rem' }}>
                          <span>{s.seller_city || 'N/A'}, </span>
                          <strong style={{ color: 'var(--text-primary)' }}>{s.seller_state || 'N/A'}</strong>
                        </div>
                      </td>
                      <td style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                        {formatCurrency(s.total_sales || s.total_gmv)}
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        {Number(s.items_sold || 0).toLocaleString()}
                      </td>
                      <td>
                        {Number(s.order_count || s.total_orders || 0).toLocaleString()}
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <Star size={14} color="#f59e0b" fill="#f59e0b" />
                          <span style={{ fontWeight: 700, color: rating >= 4.0 ? 'var(--success)' : (rating >= 3.0 ? 'var(--warning)' : 'var(--danger)') }}>
                            {rating.toFixed(2)}
                          </span>
                        </div>
                      </td>
                      <td>
                        <Badge variant={isTopTier ? 'success' : (idx < 10 ? 'primary' : 'neutral')}>
                          {isTopTier ? 'Platinum Merchant' : (idx < 10 ? 'Gold Merchant' : 'Verified')}
                        </Badge>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
