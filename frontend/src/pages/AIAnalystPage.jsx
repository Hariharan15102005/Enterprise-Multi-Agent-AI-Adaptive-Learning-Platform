import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, Sparkles, Code2, Table as TableIcon, BarChart2, CheckCircle2, AlertCircle, RefreshCw, HelpCircle, MessageSquare, ArrowRight, ShieldCheck } from 'lucide-react';
import { aiApi } from '../api/domainApis';
import { Badge, LoadingSkeleton, ErrorState } from '../components/common/UIComponents';
import { DynamicChartRenderer } from '../components/charts/ChartComponents';

const SAMPLE_PROMPTS = [
  "What is our total revenue?",
  "Which product categories generate the most revenue?",
  "Show monthly sales trends.",
  "Which states have the longest delivery times?",
  "What percentage of payments are made by credit card?",
  "Is freight cost related to delivery duration?",
  "Which customer segments have the highest spending?",
  "Show the distribution of order values.",
  "Which states have high sales but poor review scores?"
];

export function AIAnalystPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your OlistIQ Conversational AI Decision Analyst. You can ask any natural language business, operational, or financial question about the 100k Brazilian e-commerce dataset. I will generate verified analytical SQL queries, derive executive insights, and automatically select the most suitable visualization for your data.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggested_followups: [
        "What is our total revenue?",
        "Top 10 product categories by revenue",
        "Show monthly sales trends."
      ]
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTabMap, setActiveTabMap] = useState({});
  const chatBottomRef = useRef(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (questionText) => {
    const query = (questionText || inputQuestion).trim();
    if (!query || loading) return;

    setInputQuestion('');
    const userMsg = {
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      // Build conversation context from previous messages
      const conversationContext = messages
        .filter(m => m.content)
        .slice(-6)
        .map(m => ({ role: m.role, content: m.content }));

      const res = await aiApi.query(query, conversationContext);
      // Safely unwrap response payload without mistaking data rows array for the wrapper
      const aiResponse = (res && typeof res === 'object' && res.answer !== undefined)
        ? res
        : (res?.data && typeof res.data === 'object' && !Array.isArray(res.data) ? res.data : res);

      const botMsg = {
        role: 'assistant',
        content: aiResponse?.answer || (aiResponse?.error ? `Query Error: ${aiResponse.error}` : 'Analysis completed successfully with verified SQL metrics.'),
        sql: aiResponse?.sql,
        data: aiResponse?.data,
        columns: aiResponse?.columns,
        visualization: aiResponse?.visualization,
        insights: aiResponse?.insights || [],
        suggested_followups: aiResponse?.suggested_followups || [],
        caveats: aiResponse?.caveats,
        intent: aiResponse?.intent,
        execution_time_ms: aiResponse?.execution_time_ms,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('AI Query failed:', err);
      const errorMsg = {
        role: 'assistant',
        isError: true,
        content: `Query Execution Error: ${err.message || 'Unable to execute natural language SQL query.'}`,
        suggested_followups: [
          "What is our total revenue?",
          "What are the top 5 product categories by GMV?",
          "Show monthly sales trends."
        ],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const renderFormattedText = (text) => {
    if (!text) return null;
    // Basic bold **text** parsing
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: '#f8fafc', fontWeight: 700 }}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)', gap: '1rem' }}>
      {/* Top Suggestions Strip */}
      <div className="glass-card" style={{ padding: '0.85rem 1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem', overflowX: 'auto' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Sparkles size={14} color="var(--text-accent)" /> Suggested Queries:
        </span>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'nowrap' }}>
          {SAMPLE_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              className="btn btn-secondary"
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.75rem', whiteSpace: 'nowrap', borderRadius: 'var(--radius-full)' }}
              onClick={() => handleSend(prompt)}
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Main Chat Stream Container */}
      <div className="glass-card" style={{ flex: 1, padding: '1.25rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          const activeSubTab = activeTabMap[idx] || 'chart';
          const hasViz = msg.visualization && msg.visualization.chart_type;
          const hasData = msg.data && msg.data.length > 0;
          const hasInsights = msg.insights && msg.insights.length > 0;

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: isUser ? 'flex-end' : 'flex-start',
                width: '100%'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: isUser ? 'var(--text-accent)' : 'var(--accent-pink)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  {isUser ? 'You' : <><Bot size={14} /> OlistIQ Decision Analyst</>}
                </span>
                {msg.intent && !isUser && (
                  <Badge variant="primary">{msg.intent.replace(/_/g, ' ')}</Badge>
                )}
                {msg.execution_time_ms && !isUser && (
                  <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{msg.execution_time_ms} ms</span>
                )}
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{msg.timestamp}</span>
              </div>

              <div
                style={{
                  maxWidth: isUser ? '75%' : '92%',
                  padding: '1.25rem 1.5rem',
                  borderRadius: 'var(--radius-lg)',
                  background: isUser
                    ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%)'
                    : 'rgba(30, 41, 59, 0.75)',
                  border: isUser ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem',
                  lineHeight: 1.6,
                  boxShadow: '0 4px 20px rgba(0,0,0,0.25)'
                }}
              >
                {/* Text answer */}
                <p style={{ whiteSpace: 'pre-wrap', marginBottom: (!isUser && (hasViz || hasData || msg.sql)) ? '1.25rem' : 0 }}>
                  {renderFormattedText(msg.content)}
                </p>

                {/* Sub-tabs for Analysis & Chart, Table, SQL */}
                {!isUser && (hasViz || hasData || msg.sql) && (
                  <div style={{ marginTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.85rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                      {hasViz && (
                        <button
                          className="btn"
                          style={{
                            padding: '0.3rem 0.75rem',
                            fontSize: '0.75rem',
                            background: activeSubTab === 'chart' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                            color: '#fff',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}
                          onClick={() => setActiveTabMap({ ...activeTabMap, [idx]: 'chart' })}
                        >
                          <BarChart2 size={13} /> Chart & Insights
                        </button>
                      )}

                      {hasData && (
                        <button
                          className="btn"
                          style={{
                            padding: '0.3rem 0.75rem',
                            fontSize: '0.75rem',
                            background: activeSubTab === 'table' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                            color: '#fff',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}
                          onClick={() => setActiveTabMap({ ...activeTabMap, [idx]: 'table' })}
                        >
                          <TableIcon size={13} /> Data Table ({msg.data.length})
                        </button>
                      )}

                      {msg.sql && (
                        <button
                          className="btn"
                          style={{
                            padding: '0.3rem 0.75rem',
                            fontSize: '0.75rem',
                            background: activeSubTab === 'sql' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                            color: '#fff',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}
                          onClick={() => setActiveTabMap({ ...activeTabMap, [idx]: 'sql' })}
                        >
                          <Code2 size={13} /> Verified SQL Query
                        </button>
                      )}
                    </div>

                    {/* Chart & Insights Tab View */}
                    {activeSubTab === 'chart' && (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {/* Adaptive Chart Rendering */}
                        {hasViz && (
                          <div style={{
                            background: 'rgba(15, 23, 42, 0.6)',
                            padding: '1rem',
                            borderRadius: 'var(--radius-md)',
                            border: '1px solid rgba(255,255,255,0.05)'
                          }}>
                            {msg.visualization.title && (
                              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                                {msg.visualization.title}
                              </div>
                            )}
                            <DynamicChartRenderer
                              visualization={msg.visualization}
                              data={msg.data}
                              height={280}
                            />
                          </div>
                        )}

                        {/* Structured Analytical Insights */}
                        {hasInsights && (
                          <div style={{
                            padding: '0.85rem 1rem',
                            background: 'rgba(99, 102, 241, 0.08)',
                            border: '1px solid rgba(99, 102, 241, 0.2)',
                            borderRadius: 'var(--radius-md)'
                          }}>
                            <div style={{ fontSize: '0.78125rem', fontWeight: 700, color: 'var(--text-accent)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                              <Sparkles size={13} /> Key Analytical Insights:
                            </div>
                            <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.78125rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
                              {msg.insights.map((ins, iIdx) => (
                                <li key={iIdx}>{ins}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Caveats / Methodology note */}
                        {msg.caveats && (
                          <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                            Note: {msg.caveats}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Data Table View */}
                    {activeSubTab === 'table' && hasData && (
                      <div style={{ overflowX: 'auto', maxHeight: '260px', overflowY: 'auto', background: 'rgba(15, 23, 42, 0.6)', borderRadius: 'var(--radius-md)', padding: '0.5rem' }}>
                        <table className="table" style={{ fontSize: '0.75rem' }}>
                          <thead>
                            <tr>
                              {Object.keys(msg.data[0] || {}).map((col) => (
                                <th key={col}>{col.replace(/_/g, ' ').toUpperCase()}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.data.slice(0, 20).map((row, rIdx) => (
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
                    )}

                    {/* SQL View */}
                    {activeSubTab === 'sql' && msg.sql && (
                      <div style={{ position: 'relative' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.7rem', color: '#10b981', marginBottom: '0.35rem' }}>
                          <ShieldCheck size={13} /> Safe Read-Only SQL Grounded against Analytical Warehouse
                        </div>
                        <pre style={{
                          background: 'rgba(15, 23, 42, 0.95)',
                          padding: '0.9rem',
                          borderRadius: 'var(--radius-md)',
                          fontSize: '0.75rem',
                          color: '#38bdf8',
                          overflowX: 'auto',
                          border: '1px solid rgba(255,255,255,0.1)',
                          lineHeight: 1.4
                        }}>
                          <code>{msg.sql}</code>
                        </pre>
                      </div>
                    )}
                  </div>
                )}

                {/* Suggested Follow-up Question Chips */}
                {!isUser && msg.suggested_followups && msg.suggested_followups.length > 0 && (
                  <div style={{ marginTop: '0.85rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <div style={{ fontSize: '0.725rem', color: 'var(--text-muted)', marginBottom: '0.45rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <MessageSquare size={12} /> Suggested Follow-ups:
                    </div>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                      {msg.suggested_followups.map((followup, fIdx) => (
                        <button
                          key={fIdx}
                          className="btn btn-secondary"
                          style={{
                            padding: '0.25rem 0.6rem',
                            fontSize: '0.725rem',
                            borderRadius: 'var(--radius-full)',
                            background: 'rgba(255,255,255,0.04)',
                            borderColor: 'rgba(99, 102, 241, 0.3)'
                          }}
                          onClick={() => handleSend(followup)}
                        >
                          <span>{followup}</span>
                          <ArrowRight size={11} style={{ marginLeft: '0.25rem', opacity: 0.7 }} />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', color: 'var(--text-accent)' }}>
            <Sparkles size={18} className="animate-spin" />
            <span style={{ fontSize: '0.85rem' }}>Executing LangGraph agent reasoning and querying analytical warehouse...</span>
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Box Bar */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          className="input"
          placeholder="Ask any analytical question (e.g., 'What is our total revenue?', 'Top 5 categories by GMV', 'Is freight related to delivery duration?')..."
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          disabled={loading}
          style={{ flex: 1, padding: '0.65rem 1rem', fontSize: '0.875rem' }}
        />
        <button type="submit" className="btn btn-primary" disabled={loading || !inputQuestion.trim()} style={{ padding: '0.65rem 1.25rem' }}>
          <Send size={16} /> Send Query
        </button>
      </form>
    </div>
  );
}
