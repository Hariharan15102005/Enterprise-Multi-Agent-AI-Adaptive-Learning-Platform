import React, { useState, useEffect, useMemo } from 'react';
import { 
  Truck, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  DollarSign, 
  MapPin, 
  RefreshCw, 
  Search, 
  ArrowUpDown, 
  ArrowUp, 
  ArrowDown,
  Layers,
  Inbox
} from 'lucide-react';
import { logisticsApi } from '../api/domainApis';
import { MetricCard, LoadingSkeleton, ErrorState, Badge } from '../components/common/UIComponents';
import { CategoryBarChart, TransitDurationBarChart } from '../components/charts/ChartComponents';

const BRAZIL_STATE_NAMES = {
  AC: 'Acre',
  AL: 'Alagoas',
  AP: 'Amapá',
  AM: 'Amazonas',
  BA: 'Bahia',
  CE: 'Ceará',
  DF: 'Distrito Federal',
  ES: 'Espírito Santo',
  GO: 'Goiás',
  MA: 'Maranhão',
  MT: 'Mato Grosso',
  MS: 'Mato Grosso do Sul',
  MG: 'Minas Gerais',
  PA: 'Pará',
  PB: 'Paraíba',
  PR: 'Paraná',
  PE: 'Pernambuco',
  PI: 'Piauí',
  RJ: 'Rio de Janeiro',
  RN: 'Rio Grande do Norte',
  RS: 'Rio Grande do Sul',
  RO: 'Rondônia',
  RR: 'Roraima',
  SC: 'Santa Catarina',
  SP: 'São Paulo',
  SE: 'Sergipe',
  TO: 'Tocantins'
};

export function LogisticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [stateLogistics, setStateLogistics] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState('delivered_volume');
  const [sortDirection, setSortDirection] = useState('desc');
  const [chartSort, setChartSort] = useState('speed_asc');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overRes, stateRes] = await Promise.all([
        logisticsApi.getOverview(),
        logisticsApi.getByState()
      ]);

      setOverview(overRes?.data || null);
      setStateLogistics(Array.isArray(stateRes?.data) ? stateRes.data : []);
    } catch (err) {
      console.error('Failed to load logistics data:', err);
      setError(err.message || 'Error fetching logistics performance');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      // Default to desc for volume and rates, asc for speed and cost
      if (key === 'avg_delivery_days' || key === 'avg_freight_cost' || key === 'state_name') {
        setSortDirection('asc');
      } else {
        setSortDirection('desc');
      }
    }
  };

  const processedData = useMemo(() => {
    return stateLogistics.map(item => {
      const code = (item.state_code || '').trim().toUpperCase();
      const name = item.state_name || BRAZIL_STATE_NAMES[code] || code || 'Unknown';
      const volume = Number(item.delivered_volume ?? item.total_orders ?? 0);
      const deliveryDays = item.avg_delivery_days != null ? Number(item.avg_delivery_days) : (item.avg_delivery_time_days != null ? Number(item.avg_delivery_time_days) : null);
      const onTime = item.on_time_rate != null ? Number(item.on_time_rate) : null;
      const freightCost = item.avg_freight_cost != null ? Number(item.avg_freight_cost) : (item.avg_freight_brl != null ? Number(item.avg_freight_brl) : null);
      const status = item.logistics_status || 'Moderate';

      return {
        ...item,
        state_code: code,
        state_name: name,
        delivered_volume: volume,
        avg_delivery_days: deliveryDays,
        on_time_rate: onTime,
        avg_freight_cost: freightCost,
        logistics_status: status
      };
    });
  }, [stateLogistics]);

  const filteredAndSortedData = useMemo(() => {
    let result = [...processedData];

    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase().trim();
      result = result.filter(item => 
        item.state_code.toLowerCase().includes(q) ||
        item.state_name.toLowerCase().includes(q) ||
        item.logistics_status.toLowerCase().includes(q)
      );
    }

    result.sort((a, b) => {
      let valA = a[sortKey];
      let valB = b[sortKey];

      if (valA == null && valB == null) return 0;
      if (valA == null) return 1;
      if (valB == null) return -1;

      if (typeof valA === 'string') {
        return sortDirection === 'asc' 
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA);
      }

      return sortDirection === 'asc' ? valA - valB : valB - valA;
    });

    return result;
  }, [processedData, searchTerm, sortKey, sortDirection]);

  const transitChartData = useMemo(() => {
    let result = [...processedData];
    if (chartSort === 'speed_asc') {
      result.sort((a, b) => (a.avg_delivery_days ?? 999) - (b.avg_delivery_days ?? 999));
    } else if (chartSort === 'speed_desc') {
      result.sort((a, b) => (b.avg_delivery_days ?? 0) - (a.avg_delivery_days ?? 0));
    } else if (chartSort === 'volume') {
      result.sort((a, b) => (b.delivered_volume ?? 0) - (a.delivered_volume ?? 0));
    } else if (chartSort === 'alpha') {
      result.sort((a, b) => a.state_code.localeCompare(b.state_code));
    }
    return result;
  }, [processedData, chartSort]);

  if (error) {
    return <ErrorState title="Logistics Data Unavailable" message={error} onRetry={fetchData} />;
  }

  const onTimeRate = overview?.on_time_delivery_rate != null 
    ? `${Number(overview.on_time_delivery_rate).toFixed(1)}%` 
    : '—';
  const avgDays = overview?.avg_delivery_days != null 
    ? `${Number(overview.avg_delivery_days).toFixed(1)} Days` 
    : (overview?.avg_delivery_time_days != null ? `${Number(overview.avg_delivery_time_days).toFixed(1)} Days` : '—');
  const delayedCount = overview?.delayed_orders != null 
    ? Number(overview.delayed_orders).toLocaleString() 
    : '—';
  const avgFreight = overview?.avg_freight_value != null 
    ? `R$ ${Number(overview.avg_freight_value).toFixed(2)}` 
    : '—';

  const getStatusBadgeVariant = (status) => {
    switch (status) {
      case 'Optimal':
        return 'success';
      case 'Good':
        return 'info';
      case 'Moderate':
        return 'warning';
      case 'High SLA Risk':
        return 'danger';
      default:
        return 'neutral';
    }
  };

  const renderSortIndicator = (key) => {
    if (sortKey !== key) {
      return <ArrowUpDown size={12} style={{ opacity: 0.35, marginLeft: '0.35rem' }} />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp size={12} style={{ color: 'var(--primary)', marginLeft: '0.35rem' }} />
    ) : (
      <ArrowDown size={12} style={{ color: 'var(--primary)', marginLeft: '0.35rem' }} />
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Metrics Row */}
      {loading ? (
        <div className="grid grid-cols-4">
          <LoadingSkeleton height="7rem" rows={1} />
          <LoadingSkeleton height="7rem" rows={1} />
          <LoadingSkeleton height="7rem" rows={1} />
          <LoadingSkeleton height="7rem" rows={1} />
        </div>
      ) : (
        <div className="grid grid-cols-4">
          <MetricCard
            title="On-Time Delivery Rate"
            value={onTimeRate}
            subtitle="Delivered before estimated date"
            icon={CheckCircle2}
            variant="success"
          />
          <MetricCard
            title="Avg Doorstep Transit"
            value={avgDays}
            subtitle="Order placement to delivery"
            icon={Clock}
          />
          <MetricCard
            title="SLA Breach (Delayed)"
            value={delayedCount}
            subtitle="Orders exceeding promised SLA"
            icon={AlertTriangle}
            variant="danger"
          />
          <MetricCard
            title="Avg Freight Cost"
            value={avgFreight}
            subtitle="National carrier freight baseline"
            icon={DollarSign}
          />
        </div>
      )}

      {/* State Logistics Performance Chart */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
          <div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Truck size={18} color="var(--primary)" />
              <span>Transit Duration by Destination State (Days)</span>
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Average shipping turnaround from purchase to customer doorstep across all 27 Brazilian federative units
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sort:</span>
              <select
                className="input"
                style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', width: 'auto' }}
                value={chartSort}
                onChange={(e) => setChartSort(e.target.value)}
              >
                <option value="speed_asc">Fastest First (Speed)</option>
                <option value="speed_desc">Slowest First (Transit Time)</option>
                <option value="volume">Delivered Order Volume</option>
                <option value="alpha">State Code (A-Z)</option>
              </select>
            </div>

            <button 
              className="btn btn-secondary" 
              style={{ padding: '0.4rem 0.75rem', fontSize: '0.75rem' }} 
              onClick={fetchData}
              title="Refresh logistics benchmarks"
            >
              <RefreshCw size={13} style={{ marginRight: '0.35rem' }} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton rows={4} height="3.5rem" />
        ) : (
          <TransitDurationBarChart
            data={transitChartData}
            nationalAvg={overview?.avg_delivery_days != null ? Number(overview.avg_delivery_days) : 12.6}
            height={310}
          />
        )}
      </div>

      {/* State-by-State Logistics Benchmark Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          marginBottom: '1.25rem',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Federal State Logistics & Carrier Benchmark Table
              </h4>
              <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>
                {processedData.length} Federative Units
              </span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
              Regional logistics performance benchmarks calculated from delivered orders in the database
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', minWidth: '260px' }}>
            <div style={{ position: 'relative', width: '100%' }}>
              <Search 
                size={15} 
                style={{ 
                  position: 'absolute', 
                  left: '0.75rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  color: 'var(--text-muted)' 
                }} 
              />
              <input
                type="text"
                placeholder="Search state name or code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input"
                style={{ paddingLeft: '2.25rem', fontSize: '0.8rem' }}
                aria-label="Filter Federal States"
              />
            </div>
          </div>
        </div>

        {loading ? (
          <LoadingSkeleton rows={8} height="2.8rem" />
        ) : filteredAndSortedData.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
            <Inbox size={36} style={{ opacity: 0.4, margin: '0 auto 0.75rem' }} />
            <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
              No Brazilian states match "{searchTerm}"
            </div>
            <div style={{ fontSize: '0.8rem' }}>
              Clear search filter to view all 27 federative units.
            </div>
            <button 
              className="btn btn-secondary" 
              style={{ marginTop: '1rem', fontSize: '0.75rem' }}
              onClick={() => setSearchTerm('')}
            >
              Clear Filter
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto', borderRadius: 'var(--radius-md)' }}>
            <table className="table" style={{ width: '100%' }}>
              <thead>
                <tr>
                  <th 
                    style={{ cursor: 'pointer', userSelect: 'none' }} 
                    onClick={() => handleSort('state_name')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span>State</span>
                      {renderSortIndicator('state_name')}
                    </div>
                  </th>
                  <th 
                    style={{ cursor: 'pointer', userSelect: 'none' }} 
                    onClick={() => handleSort('delivered_volume')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span>Delivered Volume</span>
                      {renderSortIndicator('delivered_volume')}
                    </div>
                  </th>
                  <th 
                    style={{ cursor: 'pointer', userSelect: 'none' }} 
                    onClick={() => handleSort('avg_delivery_days')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span>Avg Delivery Days</span>
                      {renderSortIndicator('avg_delivery_days')}
                    </div>
                  </th>
                  <th 
                    style={{ cursor: 'pointer', userSelect: 'none' }} 
                    onClick={() => handleSort('on_time_rate')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span>On-Time Rate (%)</span>
                      {renderSortIndicator('on_time_rate')}
                    </div>
                  </th>
                  <th 
                    style={{ cursor: 'pointer', userSelect: 'none' }} 
                    onClick={() => handleSort('avg_freight_cost')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span>Avg Freight Cost (R$)</span>
                      {renderSortIndicator('avg_freight_cost')}
                    </div>
                  </th>
                  <th 
                    style={{ cursor: 'pointer', userSelect: 'none' }} 
                    onClick={() => handleSort('logistics_status')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <span>Logistics Status</span>
                      {renderSortIndicator('logistics_status')}
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredAndSortedData.map((row) => {
                  const rate = row.on_time_rate;
                  const isOptimal = rate != null && rate >= 92.0;
                  const isModerate = rate != null && rate >= 85.0 && rate < 92.0;

                  return (
                    <tr key={row.state_code}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                          <span 
                            className="badge badge-neutral" 
                            style={{ 
                              fontWeight: 700, 
                              minWidth: '2.2rem', 
                              justifyContent: 'center',
                              letterSpacing: '0.05em' 
                            }}
                          >
                            {row.state_code}
                          </span>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                            <MapPin size={13} color="var(--primary)" aria-hidden="true" style={{ flexShrink: 0 }} />
                            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                              {row.state_name}
                            </span>
                          </div>
                        </div>
                      </td>

                      <td>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                          {row.delivered_volume.toLocaleString()}
                        </span>
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: '0.3rem' }}>
                          orders
                        </span>
                      </td>

                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                        {row.avg_delivery_days != null ? `${row.avg_delivery_days.toFixed(1)} days` : '—'}
                      </td>

                      <td>
                        {rate != null ? (
                          <span style={{
                            fontWeight: 700,
                            color: isOptimal 
                              ? 'var(--success)' 
                              : (isModerate ? 'var(--warning)' : 'var(--danger)')
                          }}>
                            {rate.toFixed(1)}%
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>

                      <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                        {row.avg_freight_cost != null ? `R$ ${row.avg_freight_cost.toFixed(2)}` : '—'}
                      </td>

                      <td>
                        <Badge variant={getStatusBadgeVariant(row.logistics_status)}>
                          {row.logistics_status}
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
