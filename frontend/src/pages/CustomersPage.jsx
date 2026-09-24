import React, { useState, useEffect } from 'react';
import { Users, MapPin, Award, Search, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { customersApi } from '../api/coreApis';
import { MetricCard, LoadingSkeleton, ErrorState, Badge, EmptyState } from '../components/common/UIComponents';
import { CategoryBarChart } from '../components/charts/ChartComponents';

export function CustomersPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [segments, setSegments] = useState([]);
  const [geoDist, setGeoDist] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 15, total: 0 });
  const [searchTerm, setSearchTerm] = useState('');

  const fetchData = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);

      const [segRes, geoRes, custRes] = await Promise.all([
        customersApi.getSegments(),
        customersApi.getGeoDistribution(),
        customersApi.getCustomersList({ page, page_size: pagination.pageSize, search: searchTerm || undefined })
      ]);

      setSegments(segRes?.data || []);
      setGeoDist(geoRes?.data || []);
      setCustomers(custRes?.data || []);
      if (custRes?.metadata) {
        setPagination({
          page: custRes.metadata.page || page,
          pageSize: custRes.metadata.page_size || 15,
          total: custRes.metadata.total_records || 0
        });
      }
    } catch (err) {
      console.error('Failed to load customer intelligence:', err);
      setError(err.message || 'Error fetching customer data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(pagination.page);
  }, [pagination.page]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchData(1);
  };

  if (error) {
    return <ErrorState title="Customer Intelligence Unavailable" message={error} onRetry={() => fetchData(1)} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* RFM Segmentation Grid */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              RFM Customer Segment Distribution
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Recency, Frequency, Monetary (RFM) clustering on 96,096 unique buyers
            </p>
          </div>
          <Badge variant="info">{segments.length} Behavioral Clusters</Badge>
        </div>

        {loading && segments.length === 0 ? (
          <LoadingSkeleton rows={3} height="4rem" />
        ) : (
          <div className="grid grid-cols-4">
            {segments.map((seg, idx) => (
              <div
                key={idx}
                style={{
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.8125rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {seg.segment_name || seg.segment || `Cluster ${idx}`}
                    </span>
                    <Badge variant={idx === 0 ? 'success' : (idx === 1 ? 'primary' : 'neutral')}>
                      {seg.percentage ? `${seg.percentage}%` : `${((seg.customer_count / 96096) * 100).toFixed(1)}%`}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-accent)' }}>
                    {Number(seg.customer_count || seg.count || 0).toLocaleString()}
                  </div>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    Avg GMV: R$ {Number(seg.avg_monetary || seg.avg_spend || 0).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* State Geographic Distribution */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Geographic Customer Concentration (Federative Units)
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Distribution of consumer base across Brazilian states (SP, RJ, MG leading)
            </p>
          </div>
        </div>

        {loading && geoDist.length === 0 ? (
          <LoadingSkeleton rows={4} height="3rem" />
        ) : (
          <CategoryBarChart
            data={geoDist.slice(0, 15)}
            xKey="customer_state"
            yKey="customer_count"
            isCurrency={false}
            height={280}
          />
        )}
      </div>

      {/* Customer Registry Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Customer Registry
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Browsing {pagination.total > 0 ? `${pagination.total.toLocaleString()} total verified customer entities` : 'customer profiles'}
            </p>
          </div>

          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="input"
              placeholder="Filter by State or City..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: '220px', padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}>
              <Search size={14} /> Search
            </button>
          </form>
        </div>

        {loading ? (
          <LoadingSkeleton rows={6} height="2.5rem" />
        ) : customers.length === 0 ? (
          <EmptyState title="No customers found" message="Try searching for a different state code or city name." />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Customer ID</th>
                  <th>Unique Buyer ID</th>
                  <th>City</th>
                  <th>State</th>
                  <th>Total Orders</th>
                  <th>Total Spend</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c, idx) => (
                  <tr key={c.customer_id || idx}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-accent)' }}>
                      {c.customer_id ? `${c.customer_id.substring(0, 12)}...` : 'N/A'}
                    </td>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                      {c.customer_unique_id ? `${c.customer_unique_id.substring(0, 12)}...` : 'N/A'}
                    </td>
                    <td>{c.customer_city || 'N/A'}</td>
                    <td>
                      <Badge variant="neutral">{c.customer_state || 'N/A'}</Badge>
                    </td>
                    <td style={{ fontWeight: 600 }}>{c.order_count || 1}</td>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      R$ {Number(c.total_spend || c.total_value || 0).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Controls */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Page {pagination.page} of {Math.ceil((pagination.total || 1) / pagination.pageSize)}
          </span>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              disabled={pagination.page <= 1}
              onClick={() => setPagination((prev) => ({ ...prev, page: prev.page - 1 }))}
            >
              <ChevronLeft size={14} /> Previous
            </button>
            <button
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem' }}
              disabled={customers.length < pagination.pageSize}
              onClick={() => setPagination((prev) => ({ ...prev, page: prev.page + 1 }))}
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
