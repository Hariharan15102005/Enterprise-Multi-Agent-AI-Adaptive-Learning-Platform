import React, { useState, useEffect, useCallback } from 'react';
import { Users, MapPin, Award, Search, ChevronLeft, ChevronRight, RotateCcw, X, Filter } from 'lucide-react';
import { customersApi } from '../api/coreApis';
import { LoadingSkeleton, ErrorState, Badge, EmptyState } from '../components/common/UIComponents';
import { BrazilChoroplethMap } from '../components/charts/BrazilChoroplethMap';

export function CustomersPage() {
  const [loading, setLoading] = useState(true);
  const [tableLoading, setTableLoading] = useState(false);
  const [error, setError] = useState(null);
  const [segments, setSegments] = useState([]);
  const [geoDist, setGeoDist] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pageSize: 15, total: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStateCode, setSelectedStateCode] = useState(null);
  const [selectedStateObj, setSelectedStateObj] = useState(null);

  // Initial load of RFM segments and state Geo distribution
  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [segRes, geoRes] = await Promise.all([
        customersApi.getSegments(),
        customersApi.getGeoDistribution()
      ]);

      setSegments(segRes?.data || []);
      setGeoDist(geoRes?.data || []);
    } catch (err) {
      console.error('Failed to load customer segments/geo:', err);
      setError(err.message || 'Error fetching customer analytics');
    } finally {
      setLoading(false);
    }
  };

  // Fetch paginated customers with optional state & search filter
  const fetchCustomerList = useCallback(async (page = 1, stateCode = selectedStateCode, search = searchTerm) => {
    try {
      setTableLoading(true);
      const params = {
        page,
        page_size: pagination.pageSize,
        state: stateCode || undefined,
        search: search || undefined
      };

      const custRes = await customersApi.getCustomersList(params);
      setCustomers(custRes?.data || []);
      if (custRes?.metadata) {
        setPagination({
          page: custRes.metadata.page || page,
          pageSize: custRes.metadata.page_size || 15,
          total: custRes.metadata.total_records || 0
        });
      }
    } catch (err) {
      console.error('Failed to load customer list:', err);
    } finally {
      setTableLoading(false);
    }
  }, [pagination.pageSize, selectedStateCode, searchTerm]);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    fetchCustomerList(pagination.page, selectedStateCode, searchTerm);
  }, [pagination.page, selectedStateCode]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPagination((prev) => ({ ...prev, page: 1 }));
    fetchCustomerList(1, selectedStateCode, searchTerm);
  };

  const handleStateSelect = (stateItem) => {
    if (stateItem && stateItem.state_code) {
      setSelectedStateCode(stateItem.state_code);
      setSelectedStateObj(stateItem);
      setPagination((prev) => ({ ...prev, page: 1 }));
    } else {
      setSelectedStateCode(null);
      setSelectedStateObj(null);
      setPagination((prev) => ({ ...prev, page: 1 }));
    }
  };

  const handleClearStateFilter = () => {
    setSelectedStateCode(null);
    setSelectedStateObj(null);
    setPagination((prev) => ({ ...prev, page: 1 }));
  };

  if (error) {
    return <ErrorState title="Customer Intelligence Unavailable" message={error} onRetry={loadInitialData} />;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* RFM Segmentation Grid */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              RFM Customer Segment Distribution
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Recency, Frequency, Monetary (RFM) clustering on 96,096 verified buyers
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
                      {seg.share_pct ? `${seg.share_pct}%` : `${((seg.customer_count / 96096) * 100).toFixed(1)}%`}
                    </Badge>
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-accent)' }}>
                    {Number(seg.customer_count || seg.count || 0).toLocaleString()}
                  </div>
                  <p style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    Avg Spend: R$ {Number(seg.avg_monetary_spend || seg.avg_spend || 0).toFixed(2)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Upgraded Interactive Geographic Customer Concentration Map */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Geographic Customer Concentration (Interactive Brazil Map)
              </h4>
              <Badge variant="primary">27 Federative Units</Badge>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
              Explore buyer density, state-level GMV, AOV, ratings, and comparative metrics across all 26 states and the Federal District
            </p>
          </div>

          {selectedStateCode && (
            <button
              onClick={handleClearStateFilter}
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
            >
              <RotateCcw size={13} /> Reset Map & Filter
            </button>
          )}
        </div>

        {loading && geoDist.length === 0 ? (
          <LoadingSkeleton rows={8} height="3rem" />
        ) : (
          <BrazilChoroplethMap
            data={geoDist}
            loading={loading}
            onSelectState={handleStateSelect}
            selectedStateCode={selectedStateCode}
          />
        )}
      </div>

      {/* Customer Registry Table with Live State Filter Integration */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Customer Registry
              </h4>
              {selectedStateCode && (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem',
                    padding: '0.2rem 0.6rem',
                    background: 'rgba(56, 189, 248, 0.15)',
                    border: '1px solid #38bdf8',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.72rem',
                    color: '#38bdf8',
                    fontWeight: 600
                  }}
                >
                  <Filter size={11} /> Filtered by: {selectedStateObj?.state_name || selectedStateCode} ({selectedStateCode})
                  <button
                    onClick={handleClearStateFilter}
                    style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', display: 'flex', alignItems: 'center', padding: 0 }}
                    title="Clear filter"
                  >
                    <X size={12} />
                  </button>
                </div>
              )}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Browsing {pagination.total > 0 ? `${pagination.total.toLocaleString()} total verified buyer entities` : 'customer profiles'}
            </p>
          </div>

          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="input"
              placeholder="Search City or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: '220px', padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8125rem' }}>
              <Search size={14} /> Search
            </button>
          </form>
        </div>

        {tableLoading ? (
          <LoadingSkeleton rows={6} height="2.5rem" />
        ) : customers.length === 0 ? (
          <EmptyState 
            title="No customers found" 
            message={selectedStateCode ? `No customers matched the current filter in ${selectedStateCode}.` : "Try searching for a different state code or city name."} 
          />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>Customer Unique ID</th>
                  <th>City</th>
                  <th>State</th>
                  <th>Segment</th>
                  <th>Orders</th>
                  <th>Total Spend</th>
                  <th>Repeat Buyer</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c, idx) => (
                  <tr key={c.customer_unique_id || idx}>
                    <td style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'var(--text-accent)' }}>
                      {c.customer_unique_id ? `${c.customer_unique_id.substring(0, 16)}...` : 'N/A'}
                    </td>
                    <td>{c.current_city || 'N/A'}</td>
                    <td>
                      <Badge 
                        variant={selectedStateCode === c.current_state ? 'primary' : 'neutral'}
                        style={{ cursor: 'pointer' }}
                        onClick={() => handleStateSelect({ state_code: c.current_state, state_name: c.current_state })}
                        title={`Filter for ${c.current_state}`}
                      >
                        {c.current_state || 'N/A'}
                      </Badge>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        {c.rfm_segment || 'Standard'}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{c.lifetime_order_count || 1}</td>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      R$ {Number(c.lifetime_spend_brl || 0).toFixed(2)}
                    </td>
                    <td>
                      <Badge variant={c.is_repeat_customer ? 'success' : 'neutral'}>
                        {c.is_repeat_customer ? 'Repeat' : 'One-Time'}
                      </Badge>
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
            Page {pagination.page} of {Math.max(1, Math.ceil((pagination.total || 1) / pagination.pageSize))}
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
              disabled={pagination.page >= Math.ceil((pagination.total || 1) / pagination.pageSize)}
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
