(function(){
  const {useState}=React;

  function DemoLogin(){
    const [username,setUsername]=useState('');
    const [password,setPassword]=useState('');
    const [customerId,setCustomerId]=useState('');
    const [showPassword,setShowPassword]=useState(false);
    const [opening,setOpening]=useState(false);
    const [error,setError]=useState('');

    const fillDemo=()=>{
      setUsername('demo@exceptioniq.ai');
      setPassword('demo123');
      setCustomerId('EXIQ-DEMO-001');
      setError('');
    };

    const reset=()=>{
      setUsername('');
      setPassword('');
      setCustomerId('');
      setError('');
      setOpening(false);
    };

    const submit=e=>{
      e.preventDefault();
      if(!username.trim()||!password.trim()||!customerId.trim()){
        setError('Enter the three demo fields to continue. No real credentials are required.');
        return;
      }
      setError('');
      setOpening(true);
      setTimeout(()=>{
        const host=document.getElementById('demo-login-root');
        if(host){host.classList.add('demo-login-exit');setTimeout(()=>host.remove(),260)}
      },700);
    };

    return <div className="demo-login-shell" role="dialog" aria-label="ExceptionIQ demo login">
      <section className="demo-showcase" aria-label="ExceptionIQ overview">
        <div className="demo-brand"><span className="demo-brand-mark">IQ</span><span>ExceptionIQ</span></div>
        <div className="demo-hero">
          <span className="demo-kicker"><span className="demo-kicker-dot"/>AI-assisted finance operations</span>
          <h1>From exceptions to answers, <span>faster.</span></h1>
          <p>ExceptionIQ uses AI and organizational memory to investigate financial exceptions, connect relevant evidence, surface patterns, and help teams resolve issues with human oversight.</p>
        </div>
        <div className="demo-features">
          <article className="demo-feature"><span className="demo-feature-icon">⌕</span><strong>Investigate</strong><p>Analyze invoice, payment, vendor and purchase-order exceptions.</p></article>
          <article className="demo-feature"><span className="demo-feature-icon">◎</span><strong>Understand</strong><p>Surface historical patterns, supporting evidence and likely root causes.</p></article>
          <article className="demo-feature"><span className="demo-feature-icon">✓</span><strong>Resolve</strong><p>Recommend next actions and learn from human-approved outcomes.</p></article>
        </div>
        <aside className="demo-sample-card" aria-label="Sample AI investigation">
          <div className="demo-sample-top"><span className="demo-sample-label">Sample AI investigation</span><span className="demo-sample-badge">87% match</span></div>
          <div className="demo-sample-title">Invoice amount mismatch</div>
          <div className="demo-sample-row"><span>Vendor</span><strong>Electronics Pvt Ltd</strong></div>
          <div className="demo-sample-row"><span>Evidence</span><strong>Historical memory found</strong></div>
          <div className="demo-sample-row"><span>Decision</span><strong>Human approval required</strong></div>
        </aside>
      </section>

      <section className="demo-auth-panel">
        <div className="demo-auth-inner">
          <span className="demo-security-pill">🔒 Protected Demo Workspace</span>
          <h2 className="demo-auth-title">Welcome back</h2>
          <p className="demo-auth-subtitle">Sign in to continue to your ExceptionIQ demo workspace.</p>

          <form onSubmit={submit}>
            {error&&<div className="demo-error" role="alert">{error}</div>}
            <div className="demo-field"><label htmlFor="demo-user">Username / Work Email</label><div className="demo-input-wrap"><span className="demo-input-icon">✉</span><input id="demo-user" value={username} onChange={e=>setUsername(e.target.value)} placeholder="demo@exceptioniq.ai" autoComplete="off"/></div></div>
            <div className="demo-field"><label htmlFor="demo-password">Password</label><div className="demo-input-wrap"><span className="demo-input-icon">⌑</span><input id="demo-password" type={showPassword?'text':'password'} value={password} onChange={e=>setPassword(e.target.value)} placeholder="Enter demo password" autoComplete="off"/><button type="button" className="demo-password-toggle" aria-label={showPassword?'Hide password':'Show password'} onClick={()=>setShowPassword(v=>!v)}>{showPassword?'◉':'◌'}</button></div></div>
            <div className="demo-field"><label htmlFor="demo-customer">Customer ID / Organization ID</label><div className="demo-input-wrap"><span className="demo-input-icon">▦</span><input id="demo-customer" value={customerId} onChange={e=>setCustomerId(e.target.value)} placeholder="EXIQ-DEMO-001" autoComplete="off"/></div></div>

            <div className="demo-form-meta"><label className="demo-check"><input type="checkbox" defaultChecked/>Remember me</label><button className="demo-link" type="button" onClick={()=>setError('This is a demo portal, so password recovery is not required.')}>Forgot password?</button></div>

            <div className="demo-login-actions"><button className="demo-signin" disabled={opening}>{opening?<span className="demo-opening">Opening workspace…</span>:'Sign In →'}</button><button className="demo-reset" type="button" onClick={reset}>Reset</button></div>
          </form>

          <div className="demo-credentials">
            <div className="demo-credentials-head"><strong>Demo credentials</strong><button type="button" className="demo-fill" onClick={fillDemo}>Fill demo details</button></div>
            <div className="demo-cred-grid"><div className="demo-cred-row"><span>Username</span><code>demo@exceptioniq.ai</code></div><div className="demo-cred-row"><span>Password</span><code>demo123</code></div><div className="demo-cred-row"><span>Customer ID</span><code>EXIQ-DEMO-001</code></div></div>
          </div>

          <p className="demo-disclaimer"><span>ⓘ</span><span>This is a dummy login page for demonstration only. No real credentials are required or stored, and signing in does not change the existing ExceptionIQ backend or workflows.</span></p>
        </div>
      </section>
    </div>;
  }

  const host=document.createElement('div');
  host.id='demo-login-root';
  document.body.appendChild(host);
  ReactDOM.createRoot(host).render(<DemoLogin/>);
})();