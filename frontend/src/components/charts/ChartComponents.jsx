import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  ZAxis,
  ScatterChart,
  Scatter,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';

const CHART_COLORS = [
  '#6366f1', // primary indigo
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#10b981', // emerald
  '#f59e0b', // amber
  '#3b82f6', // blue
  '#14b8a6', // teal
];

export function CustomTooltipWrapper({ active, payload, label, formatter, labelPrefix = '' }) {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: 'rgba(15, 23, 42, 0.95)',
        border: '1px solid rgba(255, 255, 255, 0.15)',
        backdropFilter: 'blur(10px)',
        padding: '0.65rem 0.9rem',
        borderRadius: '8px',
        boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
        fontSize: '0.78125rem',
      }}>
        <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '0.35rem', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '0.25rem' }}>
          {labelPrefix}{label}
        </div>
        {payload.map((entry, index) => (
          <div key={`item-${index}`} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', color: '#94a3b8', margin: '2px 0' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: entry.color || entry.fill }} />
              <span>{entry.name}:</span>
            </span>
            <span style={{ fontWeight: 600, color: '#f1f5f9' }}>
              {formatter ? formatter(entry.value, entry.name) : entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export function TrendAreaChart({
  data = [],
  xKey = 'period',
  yKey = 'gmv',
  yLabel = 'GMV (R$)',
  height = 300,
  isCurrency = true,
  color = '#6366f1',
  gradientId = 'trendGradient'
}) {
  const formatVal = (val) => {
    if (val === null || val === undefined) return '0';
    if (isCurrency) {
      return `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    }
    return Number(val).toLocaleString();
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.4} />
              <stop offset="95%" stopColor={color} stopOpacity={0.0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
          <XAxis
            dataKey={xKey}
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={{ stroke: 'rgba(255, 255, 255, 0.1)' }}
          />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => isCurrency ? `R$${(v / 1000).toFixed(0)}k` : v}
          />
          <Tooltip content={<CustomTooltipWrapper formatter={(v) => formatVal(v)} />} />
          <Area
            type="monotone"
            dataKey={yKey}
            name={yLabel}
            stroke={color}
            strokeWidth={2.5}
            fillOpacity={1}
            fill={`url(#${gradientId})`}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CategoryBarChart({
  data = [],
  xKey = 'category',
  yKey = 'gmv',
  height = 320,
  isCurrency = true,
  horizontal = false
}) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        No category data available
      </div>
    );
  }

  const normalizedData = (data || []).map(item => {
    const rawName = item[xKey] ?? item.category ?? item.category_name ?? item.category_name_en ?? item.customer_state ?? item.state ?? item.seller_id ?? 'Other';
    const displayCat = typeof rawName === 'string' 
      ? (rawName.includes('_') ? rawName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : rawName)
      : String(rawName);

    const gmvVal = Number(item.gmv ?? item.total_gmv ?? item.total_gmv_brl ?? 0);
    const orderVal = Number(item.orders ?? item.total_orders ?? 0);
    const lateVal = Number(item.late_rate ?? item.late_rate_pct ?? 0);
    const contribVal = Number(item.contribution_pct ?? 0);

    let activeVal = item[yKey] !== undefined && item[yKey] !== null ? Number(item[yKey]) : gmvVal;
    if (yKey === 'orders' || yKey === 'total_orders') activeVal = orderVal;
    else if (yKey === 'late_rate' || yKey === 'late_rate_pct') activeVal = lateVal;
    else if (yKey === 'contribution_pct') activeVal = contribVal;

    return {
      ...item,
      category: displayCat,
      category_name_en: item.category_name_en || displayCat,
      gmv: gmvVal,
      total_gmv: gmvVal,
      total_gmv_brl: gmvVal,
      orders: orderVal,
      total_orders: orderVal,
      late_rate: lateVal,
      late_rate_pct: lateVal,
      contribution_pct: contribVal,
      active_val: activeVal
    };
  });

  const formatCurrency = (val) =>
    `R$ ${Number(val || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  
  const formatShortCurrency = (val) => {
    const num = Number(val || 0);
    if (num >= 1000000) return `R$${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `R$${(num / 1000).toFixed(0)}k`;
    return `R$${num.toFixed(0)}`;
  };

  const formatTooltipValue = (val) => {
    if (isCurrency || yKey === 'gmv' || yKey === 'total_gmv' || yKey === 'total_gmv_brl') {
      return formatCurrency(val);
    }
    if (yKey === 'late_rate' || yKey === 'late_rate_pct' || yKey === 'contribution_pct') {
      return `${Number(val || 0).toFixed(1)}%`;
    }
    if (yKey.includes('days') || yKey.includes('duration')) {
      return `${Number(val || 0).toFixed(1)} days`;
    }
    return `${Number(val || 0).toLocaleString()}`;
  };

  const CategoryTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0]?.payload;
      if (!item) return null;

      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
          fontSize: '0.8rem',
          minWidth: '190px'
        }}>
          <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '0.35rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '0.25rem' }}>
            {item.category}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', color: '#94a3b8', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#818cf8', fontWeight: 600 }}>{isCurrency ? 'Revenue (GMV):' : (yKey.replace(/_/g, ' ').toUpperCase() + ':')}</span>
              <span style={{ color: '#f1f5f9', fontWeight: 700 }}>{formatTooltipValue(item.active_val != null ? item.active_val : item.gmv)}</span>
            </div>
            {item.contribution_pct > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Contribution Share:</span>
                <span style={{ color: '#10b981', fontWeight: 600 }}>{item.contribution_pct.toFixed(2)}%</span>
              </div>
            )}
            {item.orders > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Order Volume:</span>
                <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{item.orders.toLocaleString()} orders</span>
              </div>
            )}
            {item.late_rate > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Delay Rate:</span>
                <span style={{ color: item.late_rate > 10 ? '#ef4444' : '#f59e0b', fontWeight: 600 }}>{item.late_rate.toFixed(1)}%</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        {horizontal ? (
          <BarChart data={normalizedData} layout="vertical" margin={{ top: 10, right: 35, left: 10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" horizontal={false} />
            <XAxis 
              type="number" 
              stroke="#64748b" 
              fontSize={10} 
              tickFormatter={(v) => isCurrency ? formatShortCurrency(v) : Number(v).toLocaleString()} 
            />
            <YAxis 
              type="category" 
              dataKey="category" 
              stroke="#94a3b8" 
              fontSize={11} 
              width={115} 
              tickLine={false} 
            />
            <Tooltip content={<CategoryTooltip />} />
            <Bar dataKey="active_val" name={isCurrency ? 'Revenue (GMV)' : 'Metric Value'} fill="#6366f1" radius={[0, 6, 6, 0]}>
              {normalizedData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        ) : (
          <BarChart data={normalizedData} margin={{ top: 15, right: 15, left: 5, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
            <XAxis
              dataKey="category"
              stroke="#64748b"
              fontSize={10}
              angle={-35}
              textAnchor="end"
              tickLine={false}
              interval={0}
            />
            <YAxis 
              stroke="#64748b" 
              fontSize={11} 
              tickLine={false} 
              axisLine={false} 
              tickFormatter={(v) => isCurrency ? formatShortCurrency(v) : (yKey.includes('rate') ? `${v}%` : Number(v).toLocaleString())} 
            />
            <Tooltip content={<CategoryTooltip />} />
            <Bar dataKey="active_val" name={isCurrency ? 'Revenue (GMV)' : 'Metric Value'} fill="#6366f1" radius={[6, 6, 0, 0]}>
              {normalizedData.map((_, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export function TransitDurationBarChart({
  data = [],
  height = 300,
  nationalAvg = 12.6,
  showNationalBenchmark = true
}) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        No transit duration data available
      </div>
    );
  }

  const chartData = (data || []).map(item => {
    const code = (item.state_code || item.state || 'BR').trim().toUpperCase();
    const name = item.state_name || item.name || code;
    const days = item.avg_delivery_days != null 
      ? Number(item.avg_delivery_days) 
      : (item.average_transit_days != null ? Number(item.average_transit_days) : (item.avg_delivery_time_days != null ? Number(item.avg_delivery_time_days) : 0));
    const volume = Number(item.delivered_volume ?? item.total_orders ?? 0);
    const onTime = item.on_time_rate != null ? Number(item.on_time_rate) : null;
    const status = item.logistics_status || (days <= 13 ? 'Optimal' : days <= 18 ? 'Good' : days <= 24 ? 'Moderate' : 'High SLA Risk');
    const freight = item.avg_freight_cost != null ? Number(item.avg_freight_cost) : (item.avg_freight_brl != null ? Number(item.avg_freight_brl) : null);

    return {
      ...item,
      state_code: code,
      state_name: name,
      avg_transit_days: days,
      delivered_volume: volume,
      on_time_rate: onTime,
      logistics_status: status,
      avg_freight_cost: freight
    };
  });

  const getBarColor = (days) => {
    if (days <= 13.0) return '#10b981'; // Optimal (Emerald)
    if (days <= 18.0) return '#38bdf8'; // Good (Sky blue)
    if (days <= 24.0) return '#f59e0b'; // Moderate (Amber)
    return '#f43f5e'; // High SLA Risk (Rose)
  };

  const TransitTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0]?.payload;
      if (!item) return null;

      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
          fontSize: '0.8rem',
          minWidth: '200px'
        }}>
          <div style={{ 
            fontWeight: 700, 
            color: '#f8fafc', 
            marginBottom: '0.4rem', 
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)', 
            paddingBottom: '0.3rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span>{item.state_name} ({item.state_code})</span>
            <span style={{ 
              fontSize: '0.7rem', 
              padding: '2px 6px', 
              borderRadius: '4px',
              fontWeight: 600,
              background: `${getBarColor(item.avg_transit_days)}22`,
              color: getBarColor(item.avg_transit_days)
            }}>
              {item.logistics_status}
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem', color: '#94a3b8', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#818cf8', fontWeight: 600 }}>Avg Transit Duration:</span>
              <span style={{ color: '#f1f5f9', fontWeight: 700 }}>{item.avg_transit_days.toFixed(1)} days</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span>Delivered Volume:</span>
              <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{item.delivered_volume.toLocaleString()} orders</span>
            </div>
            {item.on_time_rate != null && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>On-Time SLA Rate:</span>
                <span style={{ color: item.on_time_rate >= 90 ? '#10b981' : '#f59e0b', fontWeight: 600 }}>
                  {item.on_time_rate.toFixed(1)}%
                </span>
              </div>
            )}
            {item.avg_freight_cost != null && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Avg Freight Cost:</span>
                <span style={{ color: '#cbd5e1', fontWeight: 600 }}>
                  R$ {item.avg_freight_cost.toFixed(2)}
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 15, right: 15, left: -10, bottom: 15 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
          <XAxis
            dataKey="state_code"
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            interval={0}
          />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${v}d`}
            domain={[0, 'dataMax + 4']}
          />
          <Tooltip content={<TransitTooltip />} />
          {showNationalBenchmark && (
            <ReferenceLine
              y={nationalAvg}
              stroke="#ec4899"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: `National Avg (${nationalAvg}d)`,
                position: 'top',
                fill: '#f472b6',
                fontSize: 10,
                fontWeight: 600
              }}
            />
          )}
          <Bar dataKey="avg_transit_days" name="Avg Transit (Days)" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getBarColor(entry.avg_transit_days)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PaymentDonutChart({ 
  data = [], 
  height = 300, 
  nameKey = 'payment_channel', 
  valueKey = 'total_payment_value' 
}) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        No payment channel data available
      </div>
    );
  }

  const normalizedData = (data || []).map(item => {
    const rawType = item[nameKey] || item.payment_type || item.order_status || item.channel || 'other';
    const channelName = item.payment_channel || (
      rawType === 'credit_card' ? 'Credit Card' :
      rawType === 'boleto' ? 'Boleto Bancário' :
      rawType === 'voucher' ? 'Voucher' :
      rawType === 'debit_card' ? 'Debit Card' : 
      (typeof rawType === 'string' ? rawType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : String(rawType))
    );

    const payVal = Number(item[valueKey] ?? item.total_payment_value_brl ?? item.total_payment_value ?? item.total_value ?? 0);
    const txCount = Number(item.total_transactions ?? item.transaction_count ?? item.order_count ?? 0);
    const shareVal = Number(item.share_pct ?? item.val_share_pct ?? item.value_share_pct ?? 0);
    const txShareVal = Number(item.tx_share_pct ?? 0);

    const isTxMetric = valueKey === 'total_transactions' || valueKey === 'transaction_count' || valueKey === 'order_count';
    const activeVal = Number(item[valueKey] ?? (isTxMetric ? txCount : payVal));

    return {
      ...item,
      payment_type: rawType,
      payment_channel: channelName,
      total_payment_value: payVal,
      total_payment_value_brl: payVal,
      total_value: payVal,
      total_transactions: txCount,
      transaction_count: txCount,
      share_pct: shareVal,
      val_share_pct: shareVal,
      tx_share_pct: txShareVal,
      active_val: activeVal
    };
  });

  const isTxMetric = valueKey === 'total_transactions' || valueKey === 'transaction_count' || valueKey === 'order_count';

  const formatCurrency = (val) =>
    `R$ ${Number(val || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

  const PaymentTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0]?.payload;
      if (!item) return null;

      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
          fontSize: '0.8rem',
          minWidth: '180px'
        }}>
          <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '0.35rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '0.25rem' }}>
            {item.payment_channel}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', color: '#94a3b8', fontSize: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#818cf8', fontWeight: 600 }}>{isTxMetric ? 'Count:' : 'Value:'}</span>
              <span style={{ color: '#f1f5f9', fontWeight: 700 }}>{isTxMetric ? item.active_val.toLocaleString() : formatCurrency(item.total_payment_value)}</span>
            </div>
            {item.val_share_pct > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Value Share:</span>
                <span style={{ color: '#10b981', fontWeight: 600 }}>{item.val_share_pct.toFixed(2)}%</span>
              </div>
            )}
            {item.share_pct > 0 && item.val_share_pct === 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Share:</span>
                <span style={{ color: '#10b981', fontWeight: 600 }}>{item.share_pct.toFixed(2)}%</span>
              </div>
            )}
            {item.total_transactions > 0 && !isTxMetric && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Transactions:</span>
                <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{item.total_transactions.toLocaleString()} txns</span>
              </div>
            )}
            {item.avg_installments > 1 && (
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Avg Installments:</span>
                <span style={{ color: '#cbd5e1', fontWeight: 600 }}>{item.avg_installments.toFixed(1)}x</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height, position: 'relative' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip content={<PaymentTooltip />} />
          <Legend
            verticalAlign="bottom"
            height={40}
            iconType="circle"
            formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: '0.75rem', fontWeight: 500 }}>{value}</span>}
          />
          <Pie
            data={normalizedData}
            dataKey="active_val"
            nameKey="payment_channel"
            cx="50%"
            cy="44%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={4}
          >
            {normalizedData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="rgba(0,0,0,0.3)" />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ForecastBandChart({
  data = [],
  height = 340,
  targetLabel = 'Daily GMV (R$)',
  isCurrency = true
}) {
  const isGmv = targetLabel.includes('GMV') || isCurrency;

  const formatCurrency = (val) => {
    if (val == null) return '—';
    return `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatOrders = (val) => {
    if (val == null) return '—';
    return `${Math.round(Number(val)).toLocaleString()} orders`;
  };

  const formatVal = isGmv ? formatCurrency : formatOrders;

  const chartData = (data || []).map(item => {
    const dateStr = item.date || item.forecast_date || '';
    const val = Number(item.forecast_value ?? item.predicted_value ?? 0);
    const low = Number(item.lower_bound ?? item.predicted_lower ?? 0);
    const up = Number(item.upper_bound ?? item.predicted_upper ?? val);
    const base = Math.max(0, low);
    const band = Math.max(0, up - base);

    return {
      ...item,
      display_date: dateStr ? dateStr.slice(5) : '',
      full_date: dateStr,
      day_name: item.day_name || '',
      forecast_value: val,
      lower_bound: low,
      upper_bound: up,
      ci_base: base,
      ci_band: band
    };
  });

  const ForecastTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const item = payload[0]?.payload;
      if (!item) return null;

      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          padding: '0.75rem 1rem',
          borderRadius: '8px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
          fontSize: '0.8rem',
          minWidth: '200px'
        }}>
          <div style={{ 
            fontWeight: 700, 
            color: '#f8fafc', 
            marginBottom: '0.45rem', 
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)', 
            paddingBottom: '0.35rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span>{item.full_date}</span>
            {item.day_name && (
              <span style={{ fontSize: '0.7rem', color: '#94a3b8', fontWeight: 500 }}>
                {item.day_name} {item.is_weekend ? '(Weekend)' : ''}
              </span>
            )}
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#818cf8', fontWeight: 600 }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#6366f1' }} />
                Predicted {targetLabel}:
              </span>
              <span style={{ fontWeight: 700, color: '#f1f5f9' }}>
                {formatVal(item.forecast_value)}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#94a3b8', fontSize: '0.75rem' }}>
              <span>95% CI Upper Bound:</span>
              <span style={{ fontWeight: 600, color: '#c7d2fe' }}>
                {formatVal(item.upper_bound)}
              </span>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#94a3b8', fontSize: '0.75rem' }}>
              <span>95% CI Lower Bound:</span>
              <span style={{ fontWeight: 600, color: '#c7d2fe' }}>
                {formatVal(item.lower_bound)}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData} margin={{ top: 15, right: 20, left: 10, bottom: 25 }}>
          <defs>
            <linearGradient id="forecastBandGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#818cf8" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#818cf8" stopOpacity={0.08} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
          <XAxis 
            dataKey="display_date" 
            stroke="#64748b" 
            fontSize={10} 
            tickLine={false}
            angle={-30}
            textAnchor="end"
            interval={2}
          />
          <YAxis 
            stroke="#64748b" 
            fontSize={11} 
            tickLine={false} 
            axisLine={false} 
            tickFormatter={(v) => isGmv ? (v >= 1000 ? `R$${(v / 1000).toFixed(0)}k` : `R$${v}`) : `${Math.round(v)}`}
          />
          <Tooltip content={<ForecastTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            wrapperStyle={{ paddingBottom: '0.75rem' }}
            formatter={(value) => <span style={{ color: '#94a3b8', fontSize: '0.75rem', fontWeight: 500 }}>{value}</span>}
          />
          
          {/* Base transparent stack for lower bound */}
          <Area
            type="monotone"
            dataKey="ci_base"
            stackId="ci"
            stroke="none"
            fill="none"
            legendType="none"
            isAnimationActive={false}
          />
          {/* Shaded 95% Confidence Band */}
          <Area
            type="monotone"
            dataKey="ci_band"
            name="95% Confidence / Prediction Band"
            stackId="ci"
            stroke="none"
            fill="url(#forecastBandGrad)"
            fillOpacity={1}
          />
          {/* Upper bound line (dashed) */}
          <Line
            type="monotone"
            dataKey="upper_bound"
            name="95% CI Upper"
            stroke="rgba(165, 180, 252, 0.5)"
            strokeDasharray="4 4"
            strokeWidth={1.5}
            dot={false}
          />
          {/* Lower bound line (dashed) */}
          <Line
            type="monotone"
            dataKey="lower_bound"
            name="95% CI Lower"
            stroke="rgba(165, 180, 252, 0.5)"
            strokeDasharray="4 4"
            strokeWidth={1.5}
            dot={false}
          />
          {/* Main Forecast Trajectory Line */}
          <Line
            type="monotone"
            dataKey="forecast_value"
            name={`Predicted ${targetLabel}`}
            stroke="#6366f1"
            strokeWidth={3}
            dot={{ r: 3, fill: '#6366f1', stroke: '#ffffff', strokeWidth: 1 }}
            activeDot={{ r: 6, fill: '#818cf8' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ScatterPlotChart({
  data = [],
  xKey = 'x',
  yKey = 'y',
  zKey = 'z',
  xLabel = 'X Axis',
  yLabel = 'Y Axis',
  height = 300,
  valueFormat = 'number'
}) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        No scatter correlation data available
      </div>
    );
  }

  const formatVal = (val, fmt) => {
    if (val == null) return '—';
    if (fmt === 'currency') return `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (fmt === 'duration') return `${Number(val).toFixed(1)} days`;
    if (fmt === 'percentage') return `${Number(val).toFixed(1)}%`;
    return Number(val).toLocaleString();
  };

  const ScatterTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const p = payload[0]?.payload;
      if (!p) return null;
      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          padding: '0.65rem 0.9rem',
          borderRadius: '8px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
          fontSize: '0.78125rem'
        }}>
          {p[zKey] && (
            <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '0.35rem', borderBottom: '1px solid rgba(255, 255, 255, 0.1)', paddingBottom: '0.2rem' }}>
              State / ID: {String(p[zKey])}
            </div>
          )}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', color: '#94a3b8' }}>
            <div>
              <span style={{ color: '#818cf8', fontWeight: 600 }}>{xLabel}: </span>
              <span style={{ color: '#f1f5f9', fontWeight: 600 }}>{formatVal(p[xKey], valueFormat === 'currency' ? 'currency' : 'number')}</span>
            </div>
            <div>
              <span style={{ color: '#10b981', fontWeight: 600 }}>{yLabel}: </span>
              <span style={{ color: '#f1f5f9', fontWeight: 600 }}>{formatVal(p[yKey], 'duration')}</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 15, right: 20, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" />
          <XAxis
            type="number"
            dataKey={xKey}
            name={xLabel}
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            tickFormatter={(v) => valueFormat === 'currency' ? `R$${v}` : v}
          />
          <YAxis
            type="number"
            dataKey={yKey}
            name={yLabel}
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => `${v}d`}
          />
          <ZAxis range={[30, 30]} />
          <Tooltip content={<ScatterTooltip />} />
          <Scatter name="Shipments" data={data} fill="#6366f1" fillOpacity={0.7} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export function HistogramBarChart({
  data = [],
  xKey = 'bin_range',
  yKey = 'order_count',
  height = 280,
  title = 'Distribution Frequency'
}) {
  if (!data || data.length === 0) {
    return (
      <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
        No distribution data available
      </div>
    );
  }

  const HistTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0]?.payload;
      if (!item) return null;
      return (
        <div style={{
          background: 'rgba(15, 23, 42, 0.95)',
          border: '1px solid rgba(255, 255, 255, 0.15)',
          backdropFilter: 'blur(10px)',
          padding: '0.65rem 0.9rem',
          borderRadius: '8px',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)',
          fontSize: '0.78125rem'
        }}>
          <div style={{ fontWeight: 700, color: '#f8fafc', marginBottom: '0.3rem' }}>
            Bucket: {item[xKey]}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', color: '#94a3b8' }}>
            <span>Orders / Count:</span>
            <span style={{ color: '#10b981', fontWeight: 700 }}>{Number(item[yKey] || 0).toLocaleString()}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 15, right: 15, left: -5, bottom: 15 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
          <XAxis
            dataKey={xKey}
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
          />
          <YAxis
            stroke="#64748b"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(v) => Number(v) >= 1000 ? `${(v/1000).toFixed(0)}k` : v}
          />
          <Tooltip content={<HistTooltip />} />
          <Bar dataKey={yKey} fill="#8b5cf6" radius={[4, 4, 0, 0]}>
            {data.map((_, idx) => (
              <Cell key={`cell-${idx}`} fill={CHART_COLORS[idx % CHART_COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function KpiMetricDisplay({
  title = 'Key Metric',
  value = 'R$ 0,00',
  unit = '',
  subtitle = ''
}) {
  return (
    <div style={{
      padding: '1.25rem 1.5rem',
      borderRadius: 'var(--radius-lg)',
      background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%)',
      border: '1px solid rgba(99, 102, 241, 0.3)',
      display: 'flex',
      flexDirection: 'column',
      gap: '0.4rem'
    }}>
      <span style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {title}
      </span>
      <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'baseline', gap: '0.5rem' }}>
        <span>{value}</span>
        {unit && unit !== 'BRL' && <span style={{ fontSize: '1rem', color: 'var(--text-accent)', fontWeight: 600 }}>{unit}</span>}
      </div>
      {subtitle && (
        <span style={{ fontSize: '0.78125rem', color: 'var(--text-secondary)' }}>
          {subtitle}
        </span>
      )}
    </div>
  );
}

export function DynamicChartRenderer({
  visualization = {},
  data = [],
  height = 280
}) {
  const chartType = (visualization.chart_type || visualization.recommended_chart || 'table').toLowerCase();
  const chartData = (visualization.data && visualization.data.length > 0) ? visualization.data : data;

  if (chartType === 'kpi') {
    return (
      <KpiMetricDisplay
        title={visualization.title || 'Summary KPI'}
        value={visualization.kpi_value || '—'}
        unit={visualization.kpi_unit || ''}
        subtitle={visualization.kpi_subtitle || ''}
      />
    );
  }

  if (chartType === 'scatter') {
    return (
      <ScatterPlotChart
        data={chartData}
        xKey={visualization.x_key || 'freight_cost_brl'}
        yKey={visualization.y_key || 'delivery_duration_days'}
        zKey={visualization.z_key || 'customer_state'}
        xLabel={visualization.x_axis_label || 'Freight Value (R$)'}
        yLabel={visualization.y_axis_label || 'Delivery Transit (Days)'}
        valueFormat={visualization.value_format || 'currency'}
        height={height}
      />
    );
  }

  if (chartType === 'histogram') {
    return (
      <HistogramBarChart
        data={chartData}
        xKey={visualization.x_key || 'bin_range'}
        yKey={visualization.y_key || 'order_count'}
        height={height}
        title={visualization.title}
      />
    );
  }

  if (chartType === 'donut' || chartType === 'pie') {
    return (
      <PaymentDonutChart
        data={chartData}
        height={height}
        nameKey={visualization.x_key || 'payment_type'}
        valueKey={visualization.y_key || 'total_payment_value_brl'}
      />
    );
  }

  if (chartType === 'line' || chartType === 'area') {
    return (
      <TrendAreaChart
        data={chartData}
        xKey={visualization.x_key || 'purchase_month_name'}
        yKey={visualization.y_key || 'total_gmv_brl'}
        yLabel={visualization.y_axis_label || 'GMV (R$)'}
        isCurrency={visualization.value_format === 'currency'}
        height={height}
      />
    );
  }

  if (chartType === 'bar' || chartType === 'horizontal_bar') {
    return (
      <CategoryBarChart
        data={chartData}
        xKey={visualization.x_key || 'category_name'}
        yKey={visualization.y_key || 'total_gmv_brl'}
        isCurrency={visualization.value_format === 'currency'}
        horizontal={chartType === 'horizontal_bar'}
        height={height}
      />
    );
  }

  // Fallback: Data Table
  if (!chartData || chartData.length === 0) {
    return (
      <div style={{ padding: '1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        No tabular records available.
      </div>
    );
  }

  return (
    <div style={{ overflowX: 'auto', maxHeight: '240px', overflowY: 'auto' }}>
      <table className="table" style={{ fontSize: '0.75rem' }}>
        <thead>
          <tr>
            {Object.keys(chartData[0] || {}).map((col) => (
              <th key={col}>{col.replace(/_/g, ' ').toUpperCase()}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {chartData.slice(0, 15).map((row, rIdx) => (
            <tr key={rIdx}>
              {Object.values(row).map((val, cIdx) => (
                <td key={cIdx}>
                  {typeof val === 'number'
                    ? (val % 1 !== 0 ? val.toFixed(2) : val.toLocaleString())
                    : String(val ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
