import React, { useState, useMemo, useRef } from 'react';
import { geoMercator, geoPath } from 'd3-geo';
import { 
  MapPin, Users, DollarSign, Star, TrendingUp, Award, 
  RotateCcw, Layers, ArrowRight, CheckCircle2, SlidersHorizontal, BarChart3
} from 'lucide-react';
import brazilGeoJson from '../../assets/brazil_states.json';
import { Badge } from '../common/UIComponents';

const METRIC_CONFIG = {
  customer_count: {
    label: 'Customer Count',
    shortLabel: 'Customers',
    format: (v) => Number(v || 0).toLocaleString(),
    unit: 'buyers',
    colors: ['#0f172a', '#0369a1', '#0284c7', '#06b6d4', '#6366f1', '#a855f7'],
    icon: Users
  },
  total_spend_brl: {
    label: 'Total Spend (GMV)',
    shortLabel: 'GMV',
    format: (v) => `R$ ${Number(v || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    unit: 'BRL',
    colors: ['#0f172a', '#047857', '#059669', '#10b981', '#34d399', '#6ee7b7'],
    icon: DollarSign
  },
  avg_spend_per_customer: {
    label: 'Avg Spend / Buyer (AOV)',
    shortLabel: 'AOV',
    format: (v) => `R$ ${Number(v || 0).toFixed(2)}`,
    unit: 'BRL',
    colors: ['#0f172a', '#c2410c', '#ea580c', '#f97316', '#fb923c', '#fdba74'],
    icon: TrendingUp
  },
  avg_review_score: {
    label: 'Avg Review Score',
    shortLabel: 'Review Score',
    format: (v) => `${Number(v || 0).toFixed(2)} ★`,
    unit: 'Stars',
    colors: ['#0f172a', '#854d0e', '#ca8a04', '#eab308', '#facc15', '#fef08a'],
    icon: Star
  },
  repeat_customer_rate: {
    label: 'Repeat Buyer Rate',
    shortLabel: 'Repeat %',
    format: (v) => `${Number(v || 0).toFixed(2)}%`,
    unit: '%',
    colors: ['#0f172a', '#4338ca', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe'],
    icon: Award
  }
};

export function BrazilChoroplethMap({ 
  data = [], 
  loading = false, 
  onSelectState, 
  selectedStateCode = null 
}) {
  const [activeMetric, setActiveMetric] = useState('customer_count');
  const [hoveredState, setHoveredState] = useState(null);
  const [selectedState, setSelectedState] = useState(null);
  const [compareList, setCompareList] = useState([]);
  const [compareMode, setCompareMode] = useState(false);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const containerRef = useRef(null);

  // Sync external selectedStateCode if provided
  React.useEffect(() => {
    if (selectedStateCode) {
      const match = data.find((d) => d.state_code === selectedStateCode);
      if (match) setSelectedState(match);
    } else if (selectedStateCode === null && selectedState) {
      setSelectedState(null);
    }
  }, [selectedStateCode, data]);

  // Index backend data by 2-letter state UF code
  const stateDataMap = useMemo(() => {
    const map = new Map();
    data.forEach((item) => {
      map.set(item.state_code, item);
    });
    return map;
  }, [data]);

  // Compute National Aggregations
  const nationalSummary = useMemo(() => {
    const totalCustomers = data.reduce((sum, d) => sum + (d.customer_count || 0), 0);
    const totalSpend = data.reduce((sum, d) => sum + (d.total_spend_brl || 0), 0);
    const topState = [...data].sort((a, b) => b.customer_count - a.customer_count)[0];
    const lowestState = [...data].sort((a, b) => a.customer_count - b.customer_count)[0];
    const top3Share = data
      .slice(0, 3)
      .reduce((sum, d) => sum + (d.customer_count || 0), 0) / (totalCustomers || 1) * 100;

    return {
      totalCustomers,
      totalSpend,
      coveredStates: data.length,
      topState,
      lowestState,
      top3Share: top3Share.toFixed(1)
    };
  }, [data]);

  // Calculate min, max, and percentiles for choropleth color scale
  const { minVal, maxVal, values } = useMemo(() => {
    const vals = data.map((d) => Number(d[activeMetric] || 0)).filter((v) => !isNaN(v));
    const min = vals.length ? Math.min(...vals) : 0;
    const max = vals.length ? Math.max(...vals) : 1;
    return { minVal: min, maxVal: max, values: vals.sort((a, b) => a - b) };
  }, [data, activeMetric]);

  // Color interpolator
  const getColor = (val) => {
    if (val === undefined || val === null || isNaN(val) || val <= 0) {
      return '#1e293b'; // subtle dark background for no data
    }
    const colors = METRIC_CONFIG[activeMetric].colors;
    if (maxVal === minVal) return colors[colors.length - 1];

    // Logarithmic scale for customer count and GMV to handle São Paulo dominance
    let norm;
    if (activeMetric === 'customer_count' || activeMetric === 'total_spend_brl') {
      const logMin = Math.log(Math.max(minVal, 1));
      const logMax = Math.log(Math.max(maxVal, 1));
      norm = (Math.log(Math.max(val, 1)) - logMin) / (logMax - logMin || 1);
    } else {
      norm = (val - minVal) / (maxVal - minVal || 1);
    }
    norm = Math.max(0, Math.min(1, norm));
    const idx = Math.min(Math.floor(norm * (colors.length - 1)), colors.length - 2);
    return colors[idx + 1];
  };

  // D3 Projection for Brazil
  const { paths, centroids } = useMemo(() => {
    const width = 640;
    const height = 620;
    const projection = geoMercator().fitSize([width, height], brazilGeoJson);
    const pathGenerator = geoPath().projection(projection);

    const pathList = [];
    const centroidList = [];

    brazilGeoJson.features.forEach((feature) => {
      const uf = feature.properties.sigla || feature.properties.UF || feature.properties.id;
      const d = pathGenerator(feature);
      const centroid = pathGenerator.centroid(feature);
      pathList.push({ uf, d, feature });
      if (centroid && !isNaN(centroid[0]) && !isNaN(centroid[1])) {
        centroidList.push({ uf, x: centroid[0], y: centroid[1] });
      }
    });

    return { paths: pathList, centroids: centroidList };
  }, []);

  const handleStateClick = (stateItem, uf) => {
    const item = stateItem || { state_code: uf, customer_count: 0, state_name: uf };
    if (compareMode) {
      setCompareList((prev) => {
        const exists = prev.some((s) => s.state_code === uf);
        if (exists) {
          return prev.filter((s) => s.state_code !== uf);
        }
        if (prev.length >= 4) return prev; // max 4 states
        return [...prev, item];
      });
    } else {
      if (selectedState?.state_code === uf) {
        setSelectedState(null);
        if (onSelectState) onSelectState(null);
      } else {
        setSelectedState(item);
        if (onSelectState) onSelectState(item);
      }
    }
  };

  const handleMouseMove = (e, item, uf) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setTooltipPos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      });
    }
    setHoveredState(item || { state_code: uf, customer_count: 0, state_name: uf });
  };

  const handleReset = () => {
    setSelectedState(null);
    setCompareList([]);
    setCompareMode(false);
    if (onSelectState) onSelectState(null);
  };

  const activeConfig = METRIC_CONFIG[activeMetric];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Top Analytics Summary Strip */}
      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '0.75rem',
          padding: '1rem',
          background: 'rgba(255, 255, 255, 0.02)',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '8px', background: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#818cf8' }}>
            <Users size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Total Customers</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {nationalSummary.totalCustomers.toLocaleString()}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '8px', background: 'rgba(6, 182, 212, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#06b6d4' }}>
            <MapPin size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>States Covered</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#06b6d4' }}>
              {nationalSummary.coveredStates} / 27 (100%)
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '8px', background: 'rgba(16, 185, 129, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#10b981' }}>
            <Award size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Leading State</div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              {nationalSummary.topState ? `${nationalSummary.topState.state_name} (${nationalSummary.topState.percentage_of_total}%)` : 'N/A'}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '8px', background: 'rgba(236, 72, 153, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ec4899' }}>
            <TrendingUp size={18} />
          </div>
          <div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Top 3 Concentration</div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ec4899' }}>
              {nationalSummary.top3Share}% <span style={{ fontSize: '0.7rem', fontWeight: 400, color: 'var(--text-muted)' }}>(SP, RJ, MG)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Map Header & Controls Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <SlidersHorizontal size={14} /> Metric:
          </span>
          {Object.entries(METRIC_CONFIG).map(([key, cfg]) => {
            const Icon = cfg.icon;
            const isActive = activeMetric === key;
            return (
              <button
                key={key}
                onClick={() => setActiveMetric(key)}
                className="btn"
                style={{
                  padding: '0.35rem 0.75rem',
                  fontSize: '0.75rem',
                  fontWeight: isActive ? 700 : 500,
                  borderRadius: 'var(--radius-full)',
                  background: isActive ? 'var(--primary-gradient)' : 'rgba(255, 255, 255, 0.04)',
                  color: isActive ? '#fff' : 'var(--text-secondary)',
                  border: `1px solid ${isActive ? 'transparent' : 'var(--border-subtle)'}`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
              >
                <Icon size={12} /> {cfg.shortLabel}
              </button>
            );
          })}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            onClick={() => {
              setCompareMode(!compareMode);
              if (!compareMode) setCompareList(selectedState ? [selectedState] : []);
            }}
            className="btn"
            style={{
              padding: '0.35rem 0.75rem',
              fontSize: '0.75rem',
              borderRadius: 'var(--radius-md)',
              background: compareMode ? 'rgba(6, 182, 212, 0.2)' : 'rgba(255, 255, 255, 0.04)',
              color: compareMode ? '#06b6d4' : 'var(--text-secondary)',
              border: `1px solid ${compareMode ? '#06b6d4' : 'var(--border-subtle)'}`,
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            <Layers size={13} /> {compareMode ? `Comparing (${compareList.length}/4)` : 'Compare States'}
          </button>

          {(selectedState || compareList.length > 0) && (
            <button
              onClick={handleReset}
              className="btn btn-secondary"
              style={{
                padding: '0.35rem 0.75rem',
                fontSize: '0.75rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
              title="Reset state selection"
            >
              <RotateCcw size={13} /> Reset View
            </button>
          )}
        </div>
      </div>

      {/* Main Map + Intelligence Sidebar Grid */}
      <div 
        ref={containerRef}
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(420px, 1.4fr) minmax(320px, 1fr)',
          gap: '1.5rem',
          position: 'relative',
          minHeight: '560px'
        }}
      >
        {/* Map Canvas Card */}
        <div
          style={{
            position: 'relative',
            background: 'radial-gradient(circle at 50% 50%, rgba(15, 23, 42, 0.8) 0%, rgba(11, 15, 25, 0.95) 100%)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            padding: '1rem',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden'
          }}
        >
          {loading ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading Brazilian Geographic Intelligence...
            </div>
          ) : (
            <>
              <svg
                viewBox="0 0 640 620"
                style={{ width: '100%', height: 'auto', maxHeight: '520px', filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.5))' }}
              >
                <defs>
                  <filter id="glow-filter" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feComposite in="SourceGraphic" in2="blur" operator="over" />
                  </filter>
                </defs>

                {/* State Polygons */}
                <g>
                  {paths.map(({ uf, d }) => {
                    const stateItem = stateDataMap.get(uf);
                    const metricVal = stateItem ? stateItem[activeMetric] : 0;
                    const isSelected = selectedState?.state_code === uf;
                    const isHovered = hoveredState?.state_code === uf;
                    const isCompared = compareList.some((s) => s.state_code === uf);
                    const fillColor = getColor(metricVal);

                    let strokeColor = 'rgba(255, 255, 255, 0.15)';
                    let strokeWidth = 1;

                    if (isSelected) {
                      strokeColor = '#38bdf8';
                      strokeWidth = 3;
                    } else if (isCompared) {
                      strokeColor = '#06b6d4';
                      strokeWidth = 2.5;
                    } else if (isHovered) {
                      strokeColor = '#818cf8';
                      strokeWidth = 2;
                    }

                    return (
                      <path
                        key={uf}
                        d={d}
                        fill={fillColor}
                        stroke={strokeColor}
                        strokeWidth={strokeWidth}
                        strokeLinejoin="round"
                        style={{
                          cursor: 'pointer',
                          transition: 'all 0.18s ease-in-out',
                          opacity: (selectedState && !isSelected && !compareMode) ? 0.45 : 1,
                          filter: (isSelected || isHovered) ? 'url(#glow-filter)' : 'none'
                        }}
                        onClick={() => handleStateClick(stateItem, uf)}
                        onMouseMove={(e) => handleMouseMove(e, stateItem, uf)}
                        onMouseLeave={() => setHoveredState(null)}
                      />
                    );
                  })}
                </g>

                {/* State Centroid UF Badges for Large States */}
                <g pointerEvents="none">
                  {centroids.map(({ uf, x, y }) => {
                    // Show text labels on prominent states
                    const isProminent = ['SP', 'RJ', 'MG', 'RS', 'PR', 'BA', 'SC', 'GO', 'PE', 'CE', 'PA', 'MT', 'AM'].includes(uf);
                    if (!isProminent) return null;

                    return (
                      <text
                        key={uf}
                        x={x}
                        y={y}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fontSize="9px"
                        fontWeight="700"
                        fill="#ffffff"
                        style={{
                          textShadow: '0 1px 3px rgba(0,0,0,0.9), 0 0 2px #000',
                          opacity: 0.85
                        }}
                      >
                        {uf}
                      </text>
                    );
                  })}
                </g>
              </svg>

              {/* Color Gradient Legend Bar */}
              <div
                style={{
                  width: '90%',
                  marginTop: '0.75rem',
                  padding: '0.5rem 1rem',
                  background: 'rgba(0, 0, 0, 0.4)',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.3rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                  <span>Low ({activeConfig.format(minVal)})</span>
                  <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Choropleth Scale: {activeConfig.label}
                  </span>
                  <span>High ({activeConfig.format(maxVal)})</span>
                </div>
                <div
                  style={{
                    height: '8px',
                    borderRadius: '4px',
                    background: `linear-gradient(to right, ${activeConfig.colors.join(', ')})`
                  }}
                />
              </div>
            </>
          )}

          {/* Interactive Floating Tooltip */}
          {hoveredState && (
            <div
              style={{
                position: 'absolute',
                left: `${Math.min(Math.max(tooltipPos.x + 15, 10), 380)}px`,
                top: `${Math.min(Math.max(tooltipPos.y - 40, 10), 450)}px`,
                pointerEvents: 'none',
                background: 'rgba(15, 23, 42, 0.95)',
                backdropFilter: 'blur(8px)',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid #38bdf8',
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.8)',
                zIndex: 50,
                minWidth: '210px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                  {hoveredState.state_name || hoveredState.state_code}
                </span>
                <Badge variant="primary">{hoveredState.state_code}</Badge>
              </div>
              <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 600, marginBottom: '0.5rem' }}>
                {activeConfig.label}: {activeConfig.format(hoveredState[activeMetric])}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.35rem', fontSize: '0.7rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.4rem' }}>
                <div>Customers: <strong style={{ color: '#fff' }}>{hoveredState.customer_count?.toLocaleString() || 0}</strong></div>
                <div>Share: <strong style={{ color: '#fff' }}>{hoveredState.percentage_of_total || 0}%</strong></div>
                <div>Rank: <strong style={{ color: '#fff' }}>#{hoveredState.rank || '-'}</strong></div>
                <div>Rating: <strong style={{ color: '#facc15' }}>{hoveredState.avg_review_score ? `${hoveredState.avg_review_score}★` : '-'}</strong></div>
              </div>
            </div>
          )}
        </div>

        {/* State Analytics Details Card / Comparison Matrix */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {compareMode ? (
            /* Multi-State Comparison Mode Panel */
            <div
              className="glass-card"
              style={{
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                height: '100%',
                overflowY: 'auto'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <h5 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    State Comparison Matrix
                  </h5>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Click up to 4 states on the map to compare metrics
                  </p>
                </div>
                <Badge variant="info">{compareList.length} Selected</Badge>
              </div>

              {compareList.length === 0 ? (
                <div style={{ padding: '2.5rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                  <MapPin size={28} style={{ margin: '0 auto 0.5rem', opacity: 0.4 }} />
                  <p style={{ fontSize: '0.8rem' }}>No states selected for comparison.</p>
                  <p style={{ fontSize: '0.72rem', marginTop: '0.25rem' }}>Click any state on the map or choose a preset below.</p>
                  
                  <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center', marginTop: '1rem', flexWrap: 'wrap' }}>
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.7rem', padding: '0.3rem 0.6rem' }}
                      onClick={() => {
                        const top3 = data.slice(0, 3);
                        setCompareList(top3);
                      }}
                    >
                      Top 3 (SP, RJ, MG)
                    </button>
                    <button
                      className="btn btn-secondary"
                      style={{ fontSize: '0.7rem', padding: '0.3rem 0.6rem' }}
                      onClick={() => {
                        const south = data.filter((d) => ['RS', 'PR', 'SC'].includes(d.state_code));
                        setCompareList(south);
                      }}
                    >
                      South Region (RS, PR, SC)
                    </button>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {compareList.map((st) => (
                    <div
                      key={st.state_code}
                      style={{
                        padding: '0.75rem 1rem',
                        borderRadius: 'var(--radius-md)',
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid var(--border-subtle)',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '0.5rem'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                          {st.state_name} ({st.state_code})
                        </span>
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-accent)' }}>
                          Rank #{st.rank}
                        </span>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.4rem', fontSize: '0.72rem' }}>
                        <div>
                          <div style={{ color: 'var(--text-muted)' }}>Buyers</div>
                          <div style={{ fontWeight: 700, color: '#fff' }}>{st.customer_count?.toLocaleString()}</div>
                        </div>
                        <div>
                          <div style={{ color: 'var(--text-muted)' }}>Share</div>
                          <div style={{ fontWeight: 700, color: '#06b6d4' }}>{st.percentage_of_total}%</div>
                        </div>
                        <div>
                          <div style={{ color: 'var(--text-muted)' }}>GMV</div>
                          <div style={{ fontWeight: 700, color: '#10b981' }}>R$ {(st.total_spend_brl / 1000).toFixed(0)}k</div>
                        </div>
                        <div>
                          <div style={{ color: 'var(--text-muted)' }}>Rating</div>
                          <div style={{ fontWeight: 700, color: '#facc15' }}>{st.avg_review_score}★</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : selectedState ? (
            /* Single Selected State Detailed Intelligence Card */
            <div
              className="glass-card"
              style={{
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
                height: '100%',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                boxShadow: 'var(--shadow-glow)'
              }}
            >
              {/* Card Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <h5 style={{ fontSize: '1.1rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                      {selectedState.state_name}
                    </h5>
                    <Badge variant="primary">{selectedState.state_code}</Badge>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    Region: {selectedState.region} • National Rank #{selectedState.rank} of 27
                  </p>
                </div>
                <button
                  onClick={handleReset}
                  className="btn btn-secondary"
                  style={{ padding: '0.3rem 0.6rem', fontSize: '0.7rem' }}
                >
                  Clear
                </button>
              </div>

              {/* 4 Core State Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Customer Volume</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.2rem' }}>
                    {selectedState.customer_count?.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: '#06b6d4', marginTop: '0.15rem' }}>
                    {selectedState.percentage_of_total}% of Brazil total
                  </div>
                </div>

                <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>State GMV (Spend)</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#10b981', marginTop: '0.2rem' }}>
                    R$ {Number(selectedState.total_spend_brl || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    {selectedState.total_orders?.toLocaleString()} total orders
                  </div>
                </div>

                <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Avg Spend / Customer</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f97316', marginTop: '0.2rem' }}>
                    R$ {Number(selectedState.avg_spend_per_customer || 0).toFixed(2)}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    Repeat rate: {selectedState.repeat_customer_rate}%
                  </div>
                </div>

                <div style={{ padding: '0.75rem', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Customer Satisfaction</div>
                  <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#facc15', marginTop: '0.2rem' }}>
                    {selectedState.avg_review_score ? `${selectedState.avg_review_score} / 5.0` : 'N/A'}
                  </div>
                  <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                    Average Review Rating
                  </div>
                </div>
              </div>

              {/* Progress Contribution Bar */}
              <div style={{ marginTop: '0.25rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
                  <span>National Market Share</span>
                  <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{selectedState.percentage_of_total}%</span>
                </div>
                <div style={{ height: '6px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
                  <div 
                    style={{ 
                      width: `${Math.min(selectedState.percentage_of_total * 2, 100)}%`, 
                      height: '100%', 
                      background: 'var(--primary-gradient)',
                      borderRadius: '3px',
                      transition: 'width 0.4s ease'
                    }} 
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ marginTop: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <button
                  className="btn btn-primary"
                  style={{ width: '100%', fontSize: '0.75rem', padding: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}
                  onClick={() => {
                    if (onSelectState) onSelectState(selectedState);
                  }}
                >
                  <CheckCircle2 size={14} /> Filter Customer Registry for {selectedState.state_code}
                </button>
              </div>
            </div>
          ) : (
            /* National Leaderboard & Guide when no state is selected */
            <div
              className="glass-card"
              style={{
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
                height: '100%',
                overflowY: 'auto'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <h5 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    Top Brazilian Markets
                  </h5>
                  <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Ranked by verified buyer density
                  </p>
                </div>
                <Badge variant="neutral">27 States</Badge>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {data.slice(0, 7).map((st, idx) => (
                  <div
                    key={st.state_code}
                    onClick={() => handleStateClick(st, st.state_code)}
                    style={{
                      padding: '0.5rem 0.75rem',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid var(--border-subtle)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      cursor: 'pointer',
                      transition: 'background var(--transition-fast)'
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.06)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)')}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: idx === 0 ? '#fbbf24' : 'var(--text-muted)', width: '16px' }}>
                        #{idx + 1}
                      </span>
                      <div>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                          {st.state_name}
                        </div>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                          {st.region}
                        </div>
                      </div>
                    </div>

                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-accent)' }}>
                        {st.customer_count?.toLocaleString()}
                      </div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                        {st.percentage_of_total}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: 'auto' }}>
                💡 Click any state on the map to view in-depth revenue, AOV, and rating intelligence.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
