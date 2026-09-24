import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, Sparkles, Code2, Table as TableIcon, BarChart2, CheckCircle2, AlertCircle, RefreshCw, HelpCircle } from 'lucide-react';
import { aiApi } from '../api/domainApis';
import { Badge, LoadingSkeleton, ErrorState } from '../components/common/UIComponents';
import { CategoryBarChart, TrendAreaChart } from '../components/charts/ChartComponents';

const SAMPLE_PROMPTS = [
  "What is the total revenue and order volume by month?",
  "What are the top 5 product categories by GMV?",
  "Which state has the longest delivery transit times?",
  "What is the average review score for top sellers?",
  "Show payment method distribution by total value"
];

export function AIAnalystPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I am your OlistIQ AI Decision Analyst. You can ask any natural language business or financial question about the Brazilian e-commerce dataset, and I will generate grounded SQL queries and analytical answers directly from the warehouse.',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
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
      const res = await aiApi.query(query);
      const aiResponse = res?.data || res;

      const botMsg = {
        role: 'assistant',
        content: aiResponse.answer || 'Query completed successfully.',
        sql: aiResponse.sql,
        data: aiResponse.data,
        columns: aiResponse.columns,
        visualization: aiResponse.visualization,
        insights: aiResponse.insights,
        intent: aiResponse.intent,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error('AI Query failed:', err);
      const errorMsg = {
        role: 'assistant',
        isError: true,
        content: `Query Execution Error: ${err.message || 'Unable to execute natural language SQL query.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
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
          const activeSubTab = activeTabMap[idx] || 'answer';

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
                <span style={{ fontSize: '0.75rem', fontWeight: 600, color: isUser ? 'var(--text-accent)' : 'var(--accent-pink)' }}>
                  {isUser ? 'You' : 'OlistIQ Decision Agent'}
                </span>
                <span style={{ fontSize: '0.6875rem', color: 'var(--text-muted)' }}>{msg.timestamp}</span>
              </div>

              <div
                style={{
                  maxWidth: isUser ? '75%' : '90%',
                  padding: '1.15rem 1.35rem',
                  borderRadius: 'var(--radius-lg)',
                  background: isUser
                    ? 'linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.25) 100%)'
                    : 'rgba(30, 41, 59, 0.7)',
                  border: isUser ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.875rem',
                  lineHeight: 1.5,
                  boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
                }}
              >
                {/* Text answer */}
                <p style={{ whiteSpace: 'pre-wrap', marginBottom: (msg.sql || msg.data) ? '1rem' : 0 }}>
                  {msg.content}
                </p>

                {/* Sub-tabs for SQL, Data, Visualization if available */}
                {!isUser && (msg.sql || (msg.data && msg.data.length > 0)) && (
                  <div style={{ marginTop: '0.75rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                      <button
                        className="btn"
                        style={{
                          padding: '0.25rem 0.6rem',
                          fontSize: '0.75rem',
                          background: activeSubTab === 'answer' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                          color: '#fff'
                        }}
                        onClick={() => setActiveTabMap({ ...activeTabMap, [idx]: 'answer' })}
                      >
                        Summary
                      </button>

                      {msg.sql && (
                        <button
                          className="btn"
                          style={{
                            padding: '0.25rem 0.6rem',
                            fontSize: '0.75rem',
                            background: activeSubTab === 'sql' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                            color: '#fff'
                          }}
                          onClick={() => setActiveTabMap({ ...activeTabMap, [idx]: 'sql' })}
                        >
                          <Code2 size={13} /> Generated SQL
                        </button>
                      )}

                      {msg.data && msg.data.length > 0 && (
                        <button
                          className="btn"
                          style={{
                            padding: '0.25rem 0.6rem',
                            fontSize: '0.75rem',
                            background: activeSubTab === 'table' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                            color: '#fff'
                          }}
                          onClick={() => setActiveTabMap({ ...activeTabMap, [idx]: 'table' })}
                        >
                          <TableIcon size={13} /> Data Table ({msg.data.length})
                        </button>
                      )}
                    </div>

                    {/* SQL View */}
                    {activeSubTab === 'sql' && msg.sql && (
                      <pre style={{
                        background: 'rgba(15, 23, 42, 0.9)',
                        padding: '0.85rem',
                        borderRadius: 'var(--radius-md)',
                        fontSize: '0.75rem',
                        color: '#38bdf8',
                        overflowX: 'auto',
                        border: '1px solid rgba(255,255,255,0.1)'
                      }}>
                        <code>{msg.sql}</code>
                      </pre>
                    )}

                    {/* Data Table View */}
                    {activeSubTab === 'table' && msg.data && (
                      <div style={{ overflowX: 'auto', maxHeight: '240px', overflowY: 'auto' }}>
                        <table className="table" style={{ fontSize: '0.75rem' }}>
                          <thead>
                            <tr>
                              {Object.keys(msg.data[0] || {}).map((col) => (
                                <th key={col}>{col}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {msg.data.slice(0, 10).map((row, rIdx) => (
                              <tr key={rIdx}>
                                {Object.values(row).map((val, cIdx) => (
                                  <td key={cIdx}>{String(val)}</td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', padding: '1rem', color: 'var(--text-accent)' }}>
            <Sparkles size={18} className="animate-spin" />
            <span style={{ fontSize: '0.85rem' }}>Synthesizing SQL query and analyzing analytical warehouse...</span>
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Box Bar */}
      <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="glass-card" style={{ padding: '0.75rem 1.25rem', display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          className="input"
          placeholder="Ask a decision intelligence question (e.g., 'What are the top categories by GMV in RJ?')..."
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
