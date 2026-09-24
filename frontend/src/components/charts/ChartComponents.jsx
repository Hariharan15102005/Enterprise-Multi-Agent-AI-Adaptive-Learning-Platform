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
  CartesianGrid,
  Tooltip,
  Legend
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
  const formatVal = (val) => {
    if (isCurrency) {
      return `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
    }
    return Number(val).toLocaleString();
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        {horizontal ? (
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" horizontal={false} />
            <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={(v) => isCurrency ? `R$${(v / 1000).toFixed(0)}k` : v} />
            <YAxis type="category" dataKey={xKey} stroke="#94a3b8" fontSize={11} width={80} tickLine={false} />
            <Tooltip content={<CustomTooltipWrapper formatter={(v) => formatVal(v)} />} />
            <Bar dataKey={yKey} name={isCurrency ? 'Revenue (GMV)' : 'Count'} fill="#8b5cf6" radius={[0, 4, 4, 0]} />
          </BarChart>
        ) : (
          <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
            <XAxis
              dataKey={xKey}
              stroke="#64748b"
              fontSize={10}
              angle={-25}
              textAnchor="end"
              tickLine={false}
              interval={0}
            />
            <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => isCurrency ? `R$${(v / 1000).toFixed(0)}k` : v} />
            <Tooltip content={<CustomTooltipWrapper formatter={(v) => formatVal(v)} />} />
            <Bar dataKey={yKey} name={isCurrency ? 'Revenue (GMV)' : 'Volume'} fill="#6366f1" radius={[4, 4, 0, 0]}>
              {data.map((_, index) => (
                <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}

export function PaymentDonutChart({ data = [], height = 280, nameKey = 'payment_type', valueKey = 'total_value' }) {
  const formatVal = (val) => `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

  return (
    <div style={{ width: '100%', height, position: 'relative' }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip content={<CustomTooltipWrapper formatter={(v) => formatVal(v)} />} />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            formatter={(value) => <span style={{ color: '#cbd5e1', fontSize: '0.75rem', textTransform: 'capitalize' }}>{value.replace('_', ' ')}</span>}
          />
          <Pie
            data={data}
            dataKey={valueKey}
            nameKey={nameKey}
            cx="50%"
            cy="45%"
            innerRadius={60}
            outerRadius={85}
            paddingAngle={4}
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} stroke="rgba(0,0,0,0.2)" />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ForecastBandChart({ data = [], height = 320, targetLabel = 'Daily GMV (R$)' }) {
  const formatVal = (val) => `R$ ${Number(val).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 15, left: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="forecastBand" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.25} />
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.05)" vertical={false} />
          <XAxis dataKey="forecast_date" stroke="#64748b" fontSize={10} tickLine={false} />
          <YAxis stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(v) => `R$${(v / 1000).toFixed(0)}k`} />
          <Tooltip content={<CustomTooltipWrapper formatter={(v) => formatVal(v)} />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="line"
            formatter={(value) => <span style={{ color: '#94a3b8', fontSize: '0.75rem' }}>{value}</span>}
          />
          {/* Upper bound / interval area */}
          <Area
            type="monotone"
            dataKey="predicted_upper"
            name="95% CI Upper"
            stroke="none"
            fill="#8b5cf6"
            fillOpacity={0.15}
          />
          <Area
            type="monotone"
            dataKey="predicted_lower"
            name="95% CI Lower"
            stroke="none"
            fill="#0f172a"
            fillOpacity={1}
          />
          <Line
            type="monotone"
            dataKey="predicted_value"
            name={`Predicted ${targetLabel}`}
            stroke="#6366f1"
            strokeWidth={2.5}
            dot={{ r: 3, fill: '#6366f1' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
