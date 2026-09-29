import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = '/api';

function App() {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [exceptions, setExceptions] = useState([]);
    const [investigatedException, setInvestigatedException] = useState(null);
    const [showMemorySaved, setShowMemorySaved] = useState(false);

    useEffect(() => { loadExceptions(); }, []);

    const loadExceptions = async () => {
        try {
            const response = await axios.get(`${API_BASE}/exceptions`);
            setExceptions(response.data.data || []);
        } catch (error) { console.error('Failed to load exceptions:', error); }
    };

    const handleSubmitNewException = async (exceptionData) => {
        try {
            const response = await axios.post(`${API_BASE}/exceptions`, exceptionData);
            setExceptions(prev => [response.data.data, ...prev]);
            setInvestigatedException(response.data.data);
            setCurrentPage('investigation');
        } catch (error) { alert(error.response?.data?.detail || 'Failed to create exception'); }
    };

    const handleResolved = async () => {
        await loadExceptions();
        setShowMemorySaved(true);
        setTimeout(() => setShowMemorySaved(false), 2500);
    };

    return <div className="app">
        <header className="header"><div className="header-content">
            <h1 className="logo"><span className="logo-icon">⚡</span>ExceptionIQ</h1>
            <div className="header-status"><div className="status-item"><span className="status-dot memory-dot"></span><span>Organizational Memory Active</span></div></div>
        </div></header>
        <div className="main-container">
            <nav className="sidebar">
                {[['dashboard','📊','Dashboard'],['new-exception','➕','New Exception'],['memory-explorer','📚','Memory Explorer'],['learning-timeline','📈','Learning Timeline']].map(([id,icon,label]) =>
                    <button key={id} className={`nav-btn ${currentPage===id?'active':''}`} onClick={()=>setCurrentPage(id)}><span className="nav-icon">{icon}</span>{label}</button>)}
            </nav>
            <main className="main-content">
                {currentPage==='dashboard' && <Dashboard exceptions={exceptions} onInvestigate={e=>{setInvestigatedException(e);setCurrentPage('investigation')}} />}
                {currentPage==='new-exception' && <NewExceptionForm onSubmit={handleSubmitNewException} onBack={()=>setCurrentPage('dashboard')} />}
                {currentPage==='investigation' && investigatedException && <AIInvestigation exception={investigatedException} onBack={()=>setCurrentPage('dashboard')} onResolved={handleResolved} />}
                {currentPage==='memory-explorer' && <MemoryExplorer />}
                {currentPage==='learning-timeline' && <LearningTimeline />}
                {showMemorySaved && <div className="memory-saved-notification"><div className="memory-saved-content"><span className="memory-saved-icon">✓</span><div><h3>Organizational memory updated</h3><p>The approved resolution can now help future investigations.</p></div></div></div>}
            </main>
        </div>
    </div>;
}

function Dashboard({exceptions,onInvestigate}) {
    const total=exceptions.length, open=exceptions.filter(e=>e.status==='open').length, resolved=exceptions.filter(e=>e.status==='resolved').length;
    return <div className="page"><h2 className="page-title">Exception Intelligence Dashboard</h2>
        <div className="stats-grid">{[['📋','Total Exceptions',total],['🔓','Open',open],['✅','Resolved',resolved]].map(([i,l,v])=><div className="stat-card" key={l}><div className="stat-icon">{i}</div><div className="stat-content"><div className="stat-label">{l}</div><div className="stat-value">{v}</div></div></div>)}</div>
        <div className="section"><h3>Recent Exceptions</h3><div className="table-container"><table className="exceptions-table"><thead><tr><th>Vendor</th><th>Invoice #</th><th>Type</th><th>Difference</th><th>Status</th><th>Action</th></tr></thead><tbody>
        {!exceptions.length?<tr><td colSpan="6" className="empty-state">No exceptions yet. Create the first case.</td></tr>:exceptions.slice(0,8).map(e=><tr key={e.id}><td>{e.vendor}</td><td>{e.invoice_number||'—'}</td><td>{e.exception_type}</td><td className={`diff-cell ${e.difference>=0?'positive':'negative'}`}>₹{Number(e.difference||0).toLocaleString()}</td><td><span className={`status-badge ${e.status}`}>{e.status}</span></td><td><button className="action-btn" onClick={()=>onInvestigate(e)}>Investigate</button></td></tr>)}</tbody></table></div></div>
    </div>;
}

function NewExceptionForm({onSubmit,onBack}) {
    const [form,setForm]=useState({vendor:'NovaTech Solutions',invoice_number:'',po_number:'',invoice_amount:'',po_amount:'',exception_type:'Invoice Amount Mismatch',description:''});
    const set=(k,v)=>setForm(p=>({...p,[k]:v}));
    const submit=e=>{e.preventDefault();onSubmit({...form,invoice_amount:Number(form.invoice_amount),po_amount:Number(form.po_amount)});};
    return <div className="page"><h2 className="page-title">Create Financial Exception</h2><form className="exception-form" onSubmit={submit}><div className="form-grid">
        <div className="form-group"><label>Vendor *</label><input value={form.vendor} onChange={e=>set('vendor',e.target.value)} required /></div>
        <div className="form-group"><label>Invoice Number *</label><input value={form.invoice_number} onChange={e=>set('invoice_number',e.target.value)} required /></div>
        <div className="form-group"><label>PO Number</label><input value={form.po_number} onChange={e=>set('po_number',e.target.value)} /></div>
        <div className="form-group"><label>Invoice Amount (₹) *</label><input type="number" min="0" step="0.01" value={form.invoice_amount} onChange={e=>set('invoice_amount',e.target.value)} required /></div>
        <div className="form-group"><label>PO Amount (₹) *</label><input type="number" min="0" step="0.01" value={form.po_amount} onChange={e=>set('po_amount',e.target.value)} required /></div>
        <div className="form-group"><label>Exception Type *</label><input value={form.exception_type} onChange={e=>set('exception_type',e.target.value)} required /></div>
        <div className="form-group form-group-full"><label>Description</label><textarea rows="4" value={form.description} onChange={e=>set('description',e.target.value)} /></div>
    </div><div className="form-result"><label>Calculated Difference</label><div className="calculation-result">{form.invoice_amount&&form.po_amount?`₹${(Number(form.invoice_amount)-Number(form.po_amount)).toLocaleString()}`:'Enter amounts to calculate'}</div></div><div className="form-actions"><button type="button" className="btn btn-secondary" onClick={onBack}>← Back</button><button className="btn btn-primary">🤖 Create & Investigate</button></div></form></div>;
}

function AIInvestigation({exception,onBack,onResolved}) {
    const [result,setResult]=useState(null), [error,setError]=useState(''), [saving,setSaving]=useState(false);
    useEffect(()=>{(async()=>{try{const r=await axios.post(`${API_BASE}/investigate`,{vendor:exception.vendor,invoice_number:exception.invoice_number||'',po_amount:exception.po_amount,invoice_amount:exception.invoice_amount,difference:exception.difference,exception_type:exception.exception_type,description:exception.description||''});setResult(r.data)}catch(e){setError('Investigation failed. Check that the API is running.')}})()},[exception]);
    const resolve=async()=>{if(!result)return;setSaving(true);try{await axios.post(`${API_BASE}/exceptions/${exception.id}/resolve`,{status:'resolved',root_cause:result.recommendation.root_cause||result.recommendation.pattern,solution:result.recommendation.recommendation,outcome:'successful'});await onResolved();onBack();}catch(e){setError(e.response?.data?.detail||'Could not save resolution')}finally{setSaving(false)}};
    if(error)return <div className="page"><button className="back-btn" onClick={onBack}>← Back</button><div className="section"><h3>Investigation unavailable</h3><p>{error}</p></div></div>;
    if(!result)return <div className="page"><h2 className="page-title">AI Investigation</h2><div className="section"><h3>Searching organizational memory…</h3><p>Comparing vendor, exception type, amount and prior outcomes.</p></div></div>;
    const r=result.recommendation;
    return <div className="page"><div className="investigation-header"><button className="back-btn" onClick={onBack}>← Back</button><h2 className="page-title">AI Investigation</h2></div><div className="investigation-container">
        <div className="exception-summary"><h3>{exception.vendor}</h3><p>{exception.exception_type} · Difference ₹{Number(exception.difference||0).toLocaleString()}</p></div>
        <div className="section"><h3>Evidence-grounded recommendation</h3><p><strong>Pattern:</strong> {r.pattern}</p><p><strong>Likely root cause:</strong> {r.root_cause}</p><p><strong>Recommended action:</strong> {r.recommendation}</p><p>{r.explanation}</p><div className="similarity-badge">Confidence {r.confidence}% · {r.evidence_count} evidence case(s)</div></div>
        <div className="section"><h3>Similar historical cases</h3>{result.similar_memories.length?result.similar_memories.map(m=><div className="memory-card" key={m.id}><strong>{m.vendor} · {m.problem_type}</strong><p>{m.root_cause} → {m.solution}</p><span className="similarity-badge">{m.similarity_score}% match</span></div>):<p>No stored precedent. Manual verification is required.</p>}</div>
        <div className="form-actions"><button className="btn btn-secondary" onClick={onBack}>Review later</button><button className="btn btn-primary" disabled={saving} onClick={resolve}>{saving?'Saving…':'✓ Approve Resolution & Learn'}</button></div>
    </div></div>;
}

function MemoryExplorer(){const [memories,setMemories]=useState([]);useEffect(()=>{axios.get(`${API_BASE}/memories`).then(r=>setMemories(r.data.data||[])).catch(()=>{})},[]);return <div className="page"><h2 className="page-title">Memory Explorer</h2><div className="section"><h3>{memories.length} reusable experiences</h3>{memories.map(m=><div className="memory-card" key={m.id}><strong>{m.vendor} · {m.problem_type}</strong><p><b>Root cause:</b> {m.root_cause}</p><p><b>Resolution:</b> {m.solution}</p><span className={`status-badge ${m.outcome==='successful'?'resolved':'open'}`}>{m.outcome}</span></div>)}</div></div>}

function LearningTimeline(){const [data,setData]=useState(null);useEffect(()=>{axios.get(`${API_BASE}/analytics`).then(r=>setData(r.data)).catch(()=>{})},[]);return <div className="page"><h2 className="page-title">Learning & Analytics</h2>{!data?<div className="section">Loading intelligence…</div>:<><div className="stats-grid"><div className="stat-card"><div className="stat-content"><div className="stat-label">Resolution Rate</div><div className="stat-value">{data.resolution_rate}%</div></div></div><div className="stat-card"><div className="stat-content"><div className="stat-label">Memories</div><div className="stat-value">{data.totals.memories}</div></div></div><div className="stat-card"><div className="stat-content"><div className="stat-label">Successful Memory</div><div className="stat-value">{data.memory_success_rate}%</div></div></div></div><div className="section"><h3>Top vendors</h3>{data.top_vendors.map(([name,count])=><p key={name}>{name}: <strong>{count}</strong> exception(s)</p>)}</div></>}</div>}

const root=ReactDOM.createRoot(document.getElementById('root'));
root.render(<App/>);
