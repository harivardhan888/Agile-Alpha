import { useState } from 'react';
import { Upload, CheckCircle2, TrendingUp, Activity, Newspaper, BarChart2, LineChart, Lightbulb, Check } from 'lucide-react';
import './index.css';

function App() {
  const [view, setView] = useState('home'); // 'home' or 'manual'
  const [company, setCompany] = useState('');
  const [symbol, setSymbol] = useState('');
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, completed, error
  const [report, setReport] = useState('');
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('Initializing Agents...');

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedFile(file);
      setStatus('uploading');
      const formData = new FormData();
      formData.append('file', file);
      try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.status === 'success') setStatus('idle');
        else throw new Error('Upload failed');
      } catch (err) {
        setError("Failed to upload document");
        setStatus('error');
      }
    }
  };

  const startResearch = async () => {
    if (!company || !symbol) return;
    setStatus('processing');
    setReport('');
    setError('');
    setProgress(0);
    setProgressMsg('Initializing Agents...');

    try {
      const res = await fetch('/api/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company, symbol })
      });
      const data = await res.json();
      pollStatus(data.task_id);
    } catch (err) {
      setError("Failed to start research");
      setStatus('error');
    }
  };

  const pollStatus = (taskId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/status/${taskId}`);
        const data = await res.json();
        
        if (data.status === 'processing') {
          if (data.progress !== undefined) setProgress(data.progress);
          if (data.message !== undefined) setProgressMsg(data.message);
        } else if (data.status === 'completed') {
          clearInterval(interval);
          setProgress(100);
          setProgressMsg('Finalizing Report...');
          setReport(data.result);
          setStatus('completed');
        } else if (data.status === 'failed') {
          clearInterval(interval);
          setError(data.error);
          setStatus('error');
        }
      } catch (err) {
        console.error(err);
      }
    }, 5000);
  };

  const colorRecommendation = (contentArray) => {
    return contentArray.map((part, idx) => {
      if (typeof part === 'string') {
        const parts = part.split(/\b(BUY|SELL|HOLD)\b/i);
        return parts.map((word, i) => {
          const upperWord = word.toUpperCase();
          if (upperWord === 'BUY') return <span key={i} style={{ color: '#10b981', fontWeight: 'bold' }}>{word}</span>;
          if (upperWord === 'SELL') return <span key={i} style={{ color: '#ef4444', fontWeight: 'bold' }}>{word}</span>;
          if (upperWord === 'HOLD') return <span key={i} style={{ color: '#f59e0b', fontWeight: 'bold' }}>{word}</span>;
          return word;
        });
      }
      return part;
    });
  };

  const renderMarkdown = (text) => {
    const lines = text.split('\n');
    let inList = false;
    let listItems = [];
    const elements = [];

    const flushList = () => {
      if (inList && listItems.length > 0) {
        elements.push(<ul key={`ul-${elements.length}`}>{...listItems}</ul>);
        listItems = [];
        inList = false;
      }
    };

    lines.forEach((line, i) => {
      let formattedLine = line.split(/\*\*(.*?)\*\*/g).map((part, index) => 
        index % 2 === 1 ? <strong key={index}>{part}</strong> : part
      );
      
      formattedLine = formattedLine.reduce((acc, curr) => {
        if (typeof curr === 'string') {
          const parts = curr.split(/(https?:\/\/[^\s]+)/g);
          parts.forEach(p => {
            if (p.startsWith('http')) acc.push(<a href={p} target="_blank" rel="noreferrer" key={p}>{p}</a>);
            else acc.push(p);
          });
        } else acc.push(curr);
        return acc;
      }, []);

      if (line.startsWith('# ')) {
        flushList();
        elements.push(<h1 key={i}>{formattedLine.slice(1)}</h1>);
      } else if (line.startsWith('## ')) {
        flushList();
        elements.push(<h2 key={i}>{formattedLine.slice(1)}</h2>);
      } else if (line.startsWith('### ')) {
        flushList();
        elements.push(<h3 key={i}>{formattedLine.slice(1)}</h3>);
      } else if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        inList = true;
        let listItemContent = formattedLine.slice(1);
        elements.push(<li key={i}>{colorRecommendation(listItemContent)}</li>);
      } else if (line.trim() === '') {
        flushList();
      } else {
        flushList();
        elements.push(<p key={i}>{colorRecommendation(formattedLine)}</p>);
      }
    });
    flushList();
    return elements;
  };

  return (
    <>
      <nav className="navbar">
        <div className="brand" onClick={() => setView('home')}>
          <Activity size={24} /> Agile Alpha
        </div>
        <div className="nav-links">
          <div className={`nav-item ${view === 'home' ? 'active' : ''}`} onClick={() => setView('home')}>Terminal</div>
          <div className={`nav-item ${view === 'manual' ? 'active' : ''}`} onClick={() => setView('manual')}>User Manual</div>
        </div>
      </nav>
      
      <div className="app-container">
        {view === 'home' ? (
          <>
            <div>
              <h1 className="page-title">Investment Intelligence</h1>
              <p className="page-subtitle">Autonomous agentic workflow for equity research and institutional-grade analysis.</p>
            </div>

            <div className="input-grid">
              <input 
                type="text" 
                className="input-field" 
                placeholder="Target Company (e.g., Nvidia)"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                disabled={status === 'processing'}
              />
              <input 
                type="text" 
                className="input-field" 
                placeholder="Ticker Symbol (e.g., NVDA)"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                disabled={status === 'processing'}
              />
            </div>

            <div className="file-upload-wrapper">
              <input 
                type="file" 
                className="file-upload-input" 
                accept=".txt,.pdf"
                onChange={handleFileChange}
                disabled={status === 'processing' || status === 'uploading'}
              />
              {selectedFile ? <CheckCircle2 color="#10b981" /> : <Upload color="#a1a1aa" />}
              <div>
                <p style={{fontWeight: 500, color: selectedFile ? 'white' : '#f4f4f5', fontSize: '0.95rem'}}>
                  {selectedFile ? selectedFile.name : "Upload Custom Context (Optional)"}
                </p>
                <p style={{fontSize: '0.85rem', color: '#a1a1aa', marginTop: '0.2rem'}}>
                  {selectedFile ? "Document loaded into AI Memory" : "PDF or TXT for specific analysis."}
                </p>
              </div>
              {!selectedFile && (
                <a 
                  href="/example_document.txt" 
                  download
                  style={{ marginLeft: 'auto', fontSize: '0.85rem', color: '#a1a1aa', textDecoration: 'underline', position: 'relative', zIndex: 10 }}
                  onClick={(e) => e.stopPropagation()}
                >
                  Download Sample
                </a>
              )}
            </div>

            <button 
              className="btn-primary"
              onClick={startResearch}
              disabled={!company || !symbol || status === 'processing' || status === 'uploading'}
            >
              {status === 'processing' ? 'Analyzing Market Data...' : 'Generate Investment Strategy'}
            </button>

            {status === 'processing' && (
              <div className="modern-timeline">
                {[
                  {
                    title: 'News Analyst',
                    description: 'Collecting and analyzing recent news, market sentiment, and key developments.',
                    icon: <Newspaper size={20} className="step-icon" />,
                    status: progress >= 25 ? 'completed' : (progress >= 0 ? 'active' : 'pending')
                  },
                  {
                    title: 'Fundamental Researcher',
                    description: 'Fetching and analyzing financial data, company fundamentals, and key metrics.',
                    icon: <BarChart2 size={20} className="step-icon" />,
                    status: progress >= 50 ? 'completed' : (progress >= 25 ? 'active' : 'pending')
                  },
                  {
                    title: 'Quant Strategist',
                    description: 'Analyzing historical market data, quantitative indicators, and market trends.',
                    icon: <LineChart size={20} className="step-icon" />,
                    status: progress >= 75 ? 'completed' : (progress >= 50 ? 'active' : 'pending')
                  },
                  {
                    title: 'Investment Advisor',
                    description: 'Synthesizing insights from all analysis to generate the final investment thesis.',
                    icon: <Lightbulb size={20} className="step-icon" />,
                    status: progress >= 100 ? 'completed' : (progress >= 75 ? 'active' : 'pending')
                  }
                ].map((step, index, array) => (
                  <div key={index} className={`modern-timeline-item ${step.status}`}>
                    {index < array.length - 1 && <div className={`modern-timeline-connector ${step.status === 'completed' ? 'completed' : ''}`}></div>}
                    
                    <div className="modern-timeline-marker">
                      {step.status === 'completed' && <Check size={16} color="white" />}
                    </div>

                    <div className="modern-timeline-icon-box">
                      {step.icon}
                    </div>

                    <div className="modern-timeline-content">
                      <div className="modern-timeline-header-row">
                        <span className="modern-timeline-title">{step.title}</span>
                        {step.status === 'completed' && <span className="modern-badge completed">Completed</span>}
                        {step.status === 'active' && <span className="modern-badge active">In Progress</span>}
                        {step.status === 'pending' && <span className="modern-badge pending">Pending</span>}
                      </div>
                      <div className="modern-timeline-desc">
                        {step.description}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {status === 'error' && (
              <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ef4444', borderRadius: '8px', color: '#ef4444', fontSize: '0.9rem' }}>
                Error: {error}
              </div>
            )}

            {status === 'completed' && (
              <div className="report-container">
                <div className="report-content">
                  {renderMarkdown(report)}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="prose">
            <h1 className="page-title">Agile Alpha — User Guide</h1>
            
            <h2>What is Agile Alpha?</h2>
            <p><strong>Agile Alpha</strong> is an AI-powered research tool that helps you understand a publicly traded company before making an investment decision.</p>
            <p>Instead of manually searching through news, financial information, market data, and documents, Agile Alpha brings this information together and generates a structured research report.</p>
            <p>It looks at a company from multiple perspectives, including:</p>
            <ul>
              <li>📰 <strong>Recent News</strong> — What is happening around the company?</li>
              <li>💰 <strong>Financial Performance</strong> — How is the company performing financially?</li>
              <li>📊 <strong>Market Data</strong> — What do the historical numbers and market trends show?</li>
              <li>📄 <strong>Your Documents</strong> — What information is available in documents you provide?</li>
              <li>💡 <strong>Overall Analysis</strong> — What do all these findings indicate?</li>
            </ul>

            <hr style={{ borderColor: 'var(--border-color)', margin: '2rem 0' }} />

            <h2>How to Use Agile Alpha</h2>
            <p>Using Agile Alpha is simple.</p>

            <h3>Step 1 — Enter a Company</h3>
            <p>Enter the <strong>name or ticker symbol</strong> of the company you want to research.</p>
            <p>For example:</p>
            <pre style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1rem' }}>
              <code>Apple<br/>AAPL</code>
            </pre>
            <p>For Indian companies, you can use the Yahoo Finance ticker format:</p>
            <pre style={{ background: 'var(--bg-card)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', marginBottom: '1rem' }}>
              <code>RELIANCE.NS<br/>TCS.NS<br/>INFY.NS</code>
            </pre>

            <h3>Step 2 — Upload Documents (Optional)</h3>
            <p>If you have documents related to the company, you can upload them for additional analysis. For example: Annual reports, Investor presentations, Earnings reports, Company filings, or Research documents.</p>
            <p>Uploading documents is <strong>optional</strong>. You can still perform a company analysis without them.</p>

            <h3>Step 3 — Start the Analysis</h3>
            <p>Click the <strong>Analyze</strong> button. Agile Alpha will automatically collect and analyze relevant information from multiple sources. This process may take some time because the system performs several research tasks before generating the final report.</p>

            <h3>Step 4 — Read the Report</h3>
            <p>Once the analysis is complete, you will receive a structured report covering areas such as:</p>
            <ul>
              <li><strong>Company Overview:</strong> A brief introduction to the company and its business.</li>
              <li><strong>Recent News & Sentiment:</strong> Important recent developments and how the news may affect the company.</li>
              <li><strong>Financial Analysis:</strong> Key financial information and company performance.</li>
              <li><strong>Market & Quantitative Analysis:</strong> Historical market information and quantitative observations.</li>
              <li><strong>Document Insights:</strong> Important information extracted from the documents you uploaded.</li>
              <li><strong>Investment Thesis:</strong> A summary bringing the different findings together.</li>
              <li><strong>Sources:</strong> References to the information used during the analysis.</li>
            </ul>

            <hr style={{ borderColor: 'var(--border-color)', margin: '2rem 0' }} />

            <h2>Where Does the Information Come From?</h2>
            <h3>News & Web Information</h3>
            <p>The system searches the web for relevant and recent information about the company.</p>
            <h3>Financial & Market Data</h3>
            <p>Market and financial information is obtained through <strong>Yahoo Finance</strong>.</p>
            <h3>Your Documents</h3>
            <p>If you upload documents, Agile Alpha can analyze the information contained within them and use relevant sections in the report.</p>
            <h3>Source References</h3>
            <p>Where possible, the generated report provides sources so you can <strong>verify the information yourself</strong>.</p>

            <hr style={{ borderColor: 'var(--border-color)', margin: '2rem 0' }} />

            <h2>Supported Companies & Markets</h2>
            <p>Agile Alpha can be used to research publicly traded companies from many markets around the world. Examples:</p>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '2rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '0.5rem 0' }}>Company</th>
                  <th style={{ padding: '0.5rem 0' }}>Ticker</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem 0' }}>Apple</td><td style={{ padding: '0.5rem 0' }}><code>AAPL</code></td></tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem 0' }}>Microsoft</td><td style={{ padding: '0.5rem 0' }}><code>MSFT</code></td></tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem 0' }}>Reliance Industries</td><td style={{ padding: '0.5rem 0' }}><code>RELIANCE.NS</code></td></tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem 0' }}>Tata Consultancy Services</td><td style={{ padding: '0.5rem 0' }}><code>TCS.NS</code></td></tr>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}><td style={{ padding: '0.5rem 0' }}>Infosys</td><td style={{ padding: '0.5rem 0' }}><code>INFY.NS</code></td></tr>
                <tr><td style={{ padding: '0.5rem 0' }}>Tencent</td><td style={{ padding: '0.5rem 0' }}><code>TCEHY</code></td></tr>
              </tbody>
            </table>
            <p>Ticker availability depends on the underlying market-data provider.</p>

            <hr style={{ borderColor: 'var(--border-color)', margin: '2rem 0' }} />

            <h2>Important Things to Keep in Mind</h2>
            <p>Agile Alpha uses AI to analyze information from multiple sources. <strong>AI-generated analysis can contain mistakes, incomplete information, outdated information, or incorrect interpretations.</strong></p>
            <p>Always verify important information using reliable primary sources such as Company filings, Official company announcements, Stock exchange filings, Annual reports, Investor presentations, and Regulatory disclosures.</p>
            <p>Do not rely on the AI-generated report as your only source of information.</p>

            <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', padding: '1.5rem', borderRadius: '8px', marginTop: '2rem' }}>
              <h2 style={{ color: '#ef4444', marginTop: 0 }}>⚠️ Disclaimer</h2>
              <p><strong>Agile Alpha is an AI-powered research and educational tool. It is not a financial advisor, broker, or investment service.</strong></p>
              <p>The information and analysis generated by Agile Alpha are provided <strong>for informational and educational purposes only</strong> and should not be considered financial, investment, legal, tax, or professional advice.</p>
              <p>The platform may produce inaccurate, incomplete, outdated, or misleading information. Past performance and historical market data do not guarantee future results.</p>
              <p><strong>Agile Alpha does not guarantee the accuracy of its analysis or the performance of any investment.</strong></p>
              <p>You should conduct your own research and, where appropriate, consult a <strong>qualified financial advisor</strong> before making any investment decision.</p>
              <p style={{ marginBottom: 0 }}><strong>Never make an investment decision solely based on the output generated by Agile Alpha.</strong></p>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default App;
