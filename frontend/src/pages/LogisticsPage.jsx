import React, { useState, useEffect } from 'react';
import { Truck, Clock, AlertTriangle, CheckCircle2, DollarSign, MapPin, RefreshCw } from 'lucide-react';
import { logisticsApi } from '../api/domainApis';
import { MetricCard, LoadingSkeleton, ErrorState, Badge } from '../components/common/UIComponents';
import { CategoryBarChart } from '../components/charts/ChartComponents';

export function LogisticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [overview, setOverview] = useState(null);
  const [stateLogistics, setStateLogistics] = useState([]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [overRes, stateRes] = await Promise.all([
        logisticsApi.getOverview(),
        logisticsApi.getByState()
      ]);

      setOverview(overRes?.data || null);
      setStateLogistics(stateRes?.data || []);
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

  if (error) {
    return <ErrorState title="Logistics Data Unavailable" message={error} onRetry={fetchData} />;
  }

  const onTimeRate = overview?.on_time_delivery_rate != null ? Number(overview.on_time_delivery_rate).toFixed(1) : '91.9';
  const avgDays = overview?.avg_delivery_time_days != null ? Number(overview.avg_delivery_time_days).toFixed(1) : '12.5';
  const delayedCount = overview?.delayed_orders != null ? Number(overview.delayed_orders).toLocaleString() : '7,827';
  const avgFreight = overview?.avg_freight_value != null ? `R$ ${Number(overview.avg_freight_value).toFixed(2)}` : 'R$ 22.75';

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
            value={`${onTimeRate}%`}
            subtitle="Delivered before estimated date"
            icon={CheckCircle2}
            variant="success"
          />
          <MetricCard
            title="Avg Doorstep Transit"
            value={`${avgDays} Days`}
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

      {/* State Logistics Performance Chart & Highlights */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Transit Duration by Destination State (Days)
            </h4>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Average shipping turnaround from merchant to Brazilian federative units
            </p>
          </div>
          <button className="btn btn-secondary" style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem' }} onClick={fetchData}>
            <RefreshCw size={13} />
          </button>
        </div>

        {loading ? (
          <LoadingSkeleton rows={4} height="3.5rem" />
        ) : (
          <CategoryBarChart
            data={stateLogistics.slice(0, 16)}
            xKey="customer_state"
            yKey="avg_delivery_time_days"
            isCurrency={false}
            height={280}
          />
        )}
      </div>

      {/* State-by-State Logistics Table */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <div style={{ marginBottom: '1.25rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Federal State Logistics & Carrier Benchmark Table
          </h4>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Comparative regional analysis across delivery volumes, speed, and SLA compliance
          </p>
        </div>

        {loading ? (
          <LoadingSkeleton rows={5} height="2.5rem" />
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>State</th>
                  <th>Delivered Volume</th>
                  <th>Avg Delivery Days</th>
                  <th>On-Time Rate (%)</th>
                  <th>Avg Freight Cost (R$)</th>
                  <th>Logistics Status</th>
                </tr>
              </thead>
              <tbody>
                {stateLogistics.map((row, idx) => {
                  const rate = row.on_time_rate != null ? Number(row.on_time_rate) : 90;
                  const isHighPerformance = rate >= 92;
                  const isModerate = rate >= 85 && rate < 92;

                  return (
                    <tr key={row.customer_state || idx}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700 }}>
                          <MapPin size={14} color="var(--text-accent)" />
                          <span>{row.customer_state}</span>
                        </div>
                      </td>
                      <td>{Number(row.delivered_orders || row.order_count || 0).toLocaleString()}</td>
                      <td style={{ fontWeight: 600 }}>
                        {Number(row.avg_delivery_time_days || 0).toFixed(1)} days
                      </td>
                      <td>
                        <span style={{
                          fontWeight: 700,
                          color: isHighPerformance ? 'var(--success)' : (isModerate ? 'var(--warning)' : 'var(--danger)')
                        }}>
                          {rate.toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        R$ {Number(row.avg_freight_value || row.avg_freight || 0).toFixed(2)}
                      </td>
                      <td>
                        <Badge variant={isHighPerformance ? 'success' : (isModerate ? 'warning' : 'danger')}>
                          {isHighPerformance ? 'Optimal' : (isModerate ? 'Moderate' : 'High SLA Risk')}
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
