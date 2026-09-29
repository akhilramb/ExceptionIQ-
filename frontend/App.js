import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8001/api';

// Main Application Component
function App() {
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [exceptions, setExceptions] = useState([]);
    const [showInvestigation, setShowInvestigation] = useState(false);
    const [investigatedException, setInvestigatedException] = useState(null);
    const [solutionSuccess, setSolutionSuccess] = useState(null);
    const [showMemorySaved, setShowMemorySaved] = useState(false);

    // Load exceptions on mount
    useEffect(() => {
        loadExceptions();
    }, []);

    const loadExceptions = async () => {
        try {
            const response = await axios.get(`${API_BASE}/exceptions`);
            setExceptions(response.data.data);
        } catch (error) {
            console.error('Failed to load exceptions:', error);
        }
    };

    const handleSubmitNewException = async (exceptionData) => {
        try {
            const response = await axios.post(`${API_BASE}/exceptions`, exceptionData);
            setExceptions([response.data.data, ...exceptions]);
            setShowInvestigation(true);
            setInvestigatedException(response.data.data);
            setCurrentPage('investigation');
        } catch (error) {
            alert('Failed to create exception');
        }
    };

    const handleSaveMemory = async (data) => {
        try {
            await axios.post(`${API_BASE}/memories`, data);
            setShowMemorySaved(true);
            setTimeout(() => {
                setShowMemorySaved(false);
                setCurrentPage('dashboard');
            }, 3000);
        } catch (error) {
            alert('Failed to save memory');
        }
    };

    const calculateDifference = (invAmount, poAmount) => {
        return invAmount - poAmount;
    };

    return (
        <div className="app">
            {/* Header */}
            <header className="header">
                <div className="header-content">
                    <h1 className="logo">
                        <span className="logo-icon">⚡</span>
                        ExceptionIQ
                    </h1>
                    <div className="header-status">
                        <div className="status-item">
                            <span className="status-dot memory-dot"></span>
                            <span>Hindsight: Active</span>
                        </div>
                    </div>
                </div>
            </header>

            <div className="main-container">
                {/* Sidebar Navigation */}
                <nav className="sidebar">
                    <button
                        className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('dashboard')}
                    >
                        <span className="nav-icon">📊</span>
                        Dashboard
                    </button>
                    <button
                        className={`nav-btn ${currentPage === 'new-exception' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('new-exception')}
                    >
                        <span className="nav-icon">➕</span>
                        New Exception
                    </button>
                    <button
                        className={`nav-btn ${currentPage === 'investigation' && showInvestigation ? 'active' : ''} ${currentPage === 'investigation' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('investigation')}
                    >
                        <span className="nav-icon">🤖</span>
                        AI Investigation
                    </button>
                    <button
                        className={`nav-btn ${currentPage === 'memory-explorer' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('memory-explorer')}
                    >
                        <span className="nav-icon">📚</span>
                        Memory Explorer
                    </button>
                    <button
                        className={`nav-btn ${currentPage === 'learning-timeline' ? 'active' : ''}`}
                        onClick={() => setCurrentPage('learning-timeline')}
                    >
                        <span className="nav-icon">📈</span>
                        Learning Timeline
                    </button>
                </nav>

                {/* Main Content */}
                <main className="main-content">
                    {currentPage === 'dashboard' && (
                        <Dashboard
                            exceptions={exceptions}
                            onInvestigate={(exception) => {
                                setInvestigatedException(exception);
                                setShowInvestigation(true);
                                setCurrentPage('investigation');
                            }}
                        />
                    )}

                    {currentPage === 'new-exception' && (
                        <NewExceptionForm
                            onSubmit={handleSubmitNewException}
                            onBack={() => setCurrentPage('dashboard')}
                        />
                    )}

                    {currentPage === 'investigation' && investigatedException && (
                        <AIInvestigation
                            exception={investigatedException}
                            onBack={() => {
                                setShowInvestigation(false);
                                setCurrentPage('dashboard');
                            }}
                            onSaveMemory={handleSaveMemory}
                            onNewException={() => setCurrentPage('new-exception')}
                        />
                    )}

                    {currentPage === 'memory-explorer' && (
                        <MemoryExplorer />
                    )}

                    {currentPage === 'learning-timeline' && (
                        <LearningTimeline />
                    )}

                    {/* Memory Saved Notification */}
                    {showMemorySaved && (
                        <div className="memory-saved-notification">
                            <div className="memory-saved-content">
                                <span className="memory-saved-icon">✓</span>
                                <div>
                                    <h3>New Organizational Memory</h3>
                                    <p>This experience can now help solve future cases</p>
                                </div>
                            </div>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
}

// Child Components (separated for clarity)
function Dashboard({ exceptions, onInvestigate }) {
    const total = exceptions.length;
    const open = exceptions.filter(e => e.status === 'open').length;
    const resolved = exceptions.filter(e => e.status === 'resolved').length;

    return (
        <div className="page">
            <h2 className="page-title">Dashboard</h2>

            {/* Stats Cards */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon">📋</div>
                    <div className="stat-content">
                        <div className="stat-label">Total Exceptions</div>
                        <div className="stat-value">{total}</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">🔓</div>
                    <div className="stat-content">
                        <div className="stat-label">Open</div>
                        <div className="stat-value">{open}</div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="stat-icon">✅</div>
                    <div className="stat-content">
                        <div className="stat-label">Resolved</div>
                        <div className="stat-value">{resolved}</div>
                    </div>
                </div>
            </div>

            {/* Recent Exceptions Table */}
            <div className="section">
                <h3>Recent Exceptions</h3>
                <div className="table-container">
                    <table className="exceptions-table">
                        <thead>
                            <tr>
                                <th>Vendor</th>
                                <th>Invoice #</th>
                                <th>Type</th>
                                <th>Difference</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {exceptions.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="empty-state">No exceptions yet. Create one in the form!</td>
                                </tr>
                            ) : (
                                exceptions.slice(0, 5).map((exception) => (
                                    <tr key={exception.id}>
                                        <td>{exception.vendor}</td>
                                        <td>{exception.invoice_number}</td>
                                        <td>{exception.exception_type}</td>
                                        <td className={`diff-cell ${exception.difference >= 0 ? 'positive' : 'negative'}`}>
                                            {exception.difference >= 0 ? '+' : ''}{exception.difference.toFixed(2)}
                                        </td>
                                        <td>
                                            <span className={`status-badge ${exception.status}`}>
                                                {exception.status}
                                            </span>
                                        </td>
                                        <td>
                                            <button
                                                className="action-btn"
                                                onClick={() => onInvestigate(exception)}
                                            >
                                                Investigate
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function NewExceptionForm({ onSubmit, onBack }) {
    const [formData, setFormData] = useState({
        vendor: 'NovaTech Solutions',
        invoice_number: '',
        po_number: '',
        invoice_amount: '',
        po_amount: '',
        exception_type: 'Invoice Amount Mismatch',
        description: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            vendor: formData.vendor,
            invoice_number: formData.invoice_number,
            po_number: formData.po_number,
            invoice_amount: parseFloat(formData.invoice_amount),
            po_amount: parseFloat(formData.po_amount),
            exception_type: formData.exception_type,
            description: formData.description
        });
    };

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleVendorChange = (e) => {
        handleInputChange('vendor', e.target.value);
    };

    const vendorOptions = [
        'NovaTech Solutions',
        'Bharat Logistics',
        'Vertex Systems',
        'Deccan Supplies'
    ];

    return (
        <div className="page">
            <h2 className="page-title">New Exception</h2>
            <form onSubmit={handleSubmit} className="exception-form">
                <div className="form-grid">
                    {/* Vendor */}
                    <div className="form-group">
                        <label>Vendor *</label>
                        <select
                            value={formData.vendor}
                            onChange={handleVendorChange}
                            required
                        >
                            {vendorOptions.map(v => (
                                <option key={v} value={v}>{v}</option>
                            ))}
                        </select>
                    </div>

                    {/* Invoice Number */}
                    <div className="form-group">
                        <label>Invoice Number *</label>
                        <input
                            type="text"
                            value={formData.invoice_number}
                            onChange={(e) => handleInputChange('invoice_number', e.target.value)}
                            placeholder="INV-001"
                            required
                        />
                    </div>

                    {/* PO Number */}
                    <div className="form-group">
                        <label>PO Number</label>
                        <input
                            type="text"
                            value={formData.po_number}
                            onChange={(e) => handleInputChange('po_number', e.target.value)}
                            placeholder="PO-001"
                        />
                    </div>

                    {/* Invoice Amount */}
                    <div className="form-group">
                        <label>Invoice Amount (₹) *</label>
                        <input
                            type="number"
                            value={formData.invoice_amount}
                            onChange={(e) => handleInputChange('invoice_amount', e.target.value)}
                            placeholder="100000"
                            required
                            step="0.01"
                        />
                    </div>

                    {/* PO Amount */}
                    <div className="form-group">
                        <label>PO Amount (₹) *</label>
                        <input
                            type="number"
                            value={formData.po_amount}
                            onChange={(e) => handleInputChange('po_amount', e.target.value)}
                            placeholder="90000"
                            required
                            step="0.01"
                        />
                    </div>

                    {/* Exception Type */}
                    <div className="form-group">
                        <label>Exception Type *</label>
                        <input
                            type="text"
                            value={formData.exception_type}
                            onChange={(e) => handleInputChange('exception_type', e.target.value)}
                            placeholder="Invoice Amount Mismatch"
                            required
                        />
                    </div>

                    {/* Description */}
                    <div className="form-group form-group-full">
                        <label>Description</label>
                        <textarea
                            value={formData.description}
                            onChange={(e) => handleInputChange('description', e.target.value)}
                            placeholder="Describe the exception..."
                            rows={4}
                        />
                    </div>
                </div>

                {/* Auto-calculated Difference */}
                <div className="form-result">
                    <label>Auto-calculated Difference</label>
                    <div className="calculation-result">
                        {formData.invoice_amount && formData.po_amount ? (
                            <>
                                {(parseFloat(formData.invoice_amount) - parseFloat(formData.po_amount)).toFixed(2)}
                                <span className="currency">₹</span>
                            </>
                        ) : (
                            <span className="placeholder">Enter amounts to calculate</span>
                        )}
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="form-actions">
                    <button
                        type="button"
                        className="btn btn-secondary"
                        onClick={onBack}
                    >
                        ← Back
                    </button>
                    <button
                        type="submit"
                        className="btn btn-primary"
                    >
                        <span className="btn-icon">🤖</span>
                        Investigate with AI
                    </button>
                </div>
            </form>
        </div>
    );
}

function AIInvestigation({ exception, onBack, onSaveMemory, onNewException }) {
    const [currentStep, setCurrentStep] = useState('searching');
    const [investigationResult, setInvestigationResult] = useState(null);
    const [showApproval, setShowApproval] = useState(false);
    const [approvalStatus, setApprovalStatus] = useState('');
    const [solutionSaved, setSolutionSaved] = useState(false);

    useEffect(() => {
        performInvestigation(exception);
    }, [exception]);

    const performInvestigation = async () => {
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/investigate', {
                vendor: exception.vendor,
                invoice_number: exception.invoice_number || '',
                po_amount: exception.po_amount,
                exception_type: exception.exception_type
            });
            setInvestigationResult(response.data);
            setCurrentStep('result');
        } catch (error) {
            console.error('Investigation failed:', error);
            setCurrentStep('error');
        }
    };

    const handleApprove = (status) => {
        setApprovalStatus(status);
        setShowApproval(true);
    };

    const handleSaveOutcome = () => {
        if (investigationResult) {
            const memoryData = {
                vendor: exception.vendor,
                problem_type: exception.exception_type,
                amount_difference: exception.difference,
                root_cause: investigationResult.recommendation.pattern.substring(0, 100),
                solution: investigationResult.recommendation.recommendation.substring(0, 150),
                outcome: approvalStatus === 'success' ? 'successful' : 'failed'
            };
            onSaveMemory(memoryData);
            setSolutionSaved(true);
        }
    };

    return (
        <div className="page">
            <div className="investigation-header">
                <button className="back-btn" onClick={onBack}>← Back</button>
                <h2 className="page-title">AI Investigation</h2>
            </div>

            {investigationResult && investigationResult.recommendation ? (
                <div className="investigation-container">
                    {/* Current Exception */}
                    <div className="exception-summary">
                        <h3>Current Exception</h3>
                        <div className="exception-details">
                            <div className="detail-row">
                                <span className="detail-label">Vendor:</span>
                                <span className="detail-value">{investigationResult.current_exception.vendor}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Invoice Number:</span>
                                <span className="detail-value">{investigationResult.current_exception.invoice_number || 'N/A'}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">PO Amount:</span>
                                <span className="detail-value">{investigationResult.current_exception.po_amount} ₹</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Exception Type:</span>
                                <span className="detail-value">{investigationResult.current_exception.exception_type}</span>
                            </div>
                            {investigationResult.similarity_score !== undefined && (
                                <div className="detail-row">
                                    <span className="detail-label">Similarity Score:</span>
                                    <span className="detail-value similarity">{investigationResult.similarity_score}%</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Similar Cases */}
                    {investigationResult.similar_memories && investigationResult.similar_memories.length > 0 && (
                        <div className="similar-cases">
                            <h3>📚 Similar Cases Found</h3>
                            <div className="memories-grid">
                                {investigationResult.similar_memories.map((memory, idx) => (
                                    <div key={idx} className="memory-card compact">
                                        <div className="memory-header">
                                            <span className="memory-vendor">{memory.vendor}</span>
                                            <span className="memory-diff">
                                                {memory.amount_difference >= 0 ? '+' : ''}
                                                {memory.amount_difference} ₹
                                            </span>
                                        </div>
                                        <div className="memory-body">
                                            <div className="memory-item">
                                                <span className="item-label">Problem:</span>
                                                <span>{memory.problem_type}</span>
                                            </div>
                                            <div className="memory-item">
                                                <span className="item-label">Cause:</span>
                                                <span>{memory.root_cause}</span>
                                            </div>
                                            <div className="memory-item">
                                                <span className="item-label">Solution:</span>
                                                <span>{memory.solution}</span>
                                            </div>
                                            <div className="memory-item">
                                                <span className="item-label">Outcome:</span>
                                                <span className={`outcome ${memory.outcome}`}>{memory.outcome}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Pattern Detected */}
                    {investigationResult.pattern_detected ? (
                        <div className="pattern-section">
                            <h3>🔍 Pattern Detected</h3>
                            <p className="pattern-paragraph">
                                {investigationResult.recommendation.pattern}
                            </p>
                        </div>
                    ) : null}

                    {/* AI Recommendation */}
                    <div className="ai-recommendation">
                        <h3>🤖 AI Recommendation</h3>
                        <div className="recommendation-content">
                            <p className="recommendation-text">
                                {investigationResult.recommendation.recommendation}
                            </p>
                            {investigationResult.recommendation.explanation && (
                                <p className="recommendation-explanation">
                                    {investigationResult.recommendation.explanation}
                                </p>
                            )}
                        </div>
                    </div>

                    {/* Approval */}
                    {!solutionSaved ? (
                        <div className="approval-section">
                            <h3>Was the solution successful?</h3>
                            <div className="approval-buttons">
                                <button
                                    className="btn approval-btn"
                                    onClick={() => handleApprove('success')}
                                >
                                    ✅ Yes
                                </button>
                                <button
                                    className="btn approval-btn"
                                    onClick={() => handleApprove('failed')}
                                >
                                    ❌ No
                                </button>
                            </div>

                            {showApproval && (
                                <div className="approval-actions">
                                    <button
                                        className="btn btn-primary"
                                        onClick={handleSaveOutcome}
                                    >
                                        Save Outcome to Memory
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="memory-saved-result">
                            <h3>✓ Memory Updated</h3>
                            <p>
                                "New organizational memory created. Thanks for documenting this solution!
                                This experience can now help solve future cases."
                            </p>
                            <div className="solution-actions">
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setSolutionSaved(false)}
                                >
                                    Investigate Another Exception
                                </button>
                                <button
                                    className="btn btn-primary"
                                    onClick={onNewException}
                                >
                                    Create New Exception
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            ) : investigationResult && investigationResult.recommendation ? (
                // Another view for empty results
                <div className="investigation-container">
                    <h3>Searching organizational memory...</h3>
                    <p>No similar memories found for this vendor.</p>
                </div>
            ) : (
                <div className="investigation-container">
                    <div className="investigation-status">
                        <div className={`status-dot ${currentStep === 'searching' ? 'searching' : 'error'}`}></div>
                        <p>Investigating...</p>
                    </div>
                </div>
            )}
        </div>
    );
}

function MemoryExplorer() {
    return (
        <div className="page">
            <h2 className="page-title">Memory Explorer</h2>
            <div className="memory-grid">
                {[
                    {
                        vendor: 'NovaTech Solutions',
                        problem: 'Invoice Amount Mismatch',
                        diff: '+8,000',
                        cause: 'Freight charge',
                        solution: 'Verify freight agreement',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'Bharat Logistics',
                        problem: 'Missing GST',
                        diff: '+18,000',
                        cause: 'GST not included in invoice',
                        solution: 'Request GST invoice document',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'Vertex Systems',
                        problem: 'Duplicate Invoice',
                        diff: '+75,000',
                        cause: 'Duplicate invoice number',
                        solution: 'Contact vendor to correct',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'Deccan Supplies',
                        problem: 'Unexpected Charges',
                        diff: '+5,500',
                        cause: 'Miscellaneous charges',
                        solution: 'Ask vendor for breakdown',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'NovaTech Solutions',
                        problem: 'Taxes Mismatch',
                        diff: '+4,800',
                        cause: 'Service tax not included',
                        solution: 'Request tax details',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'Bharat Logistics',
                        problem: 'Delivery Charges',
                        diff: '+3,200',
                        cause: 'Extra delivery charges',
                        solution: 'Check delivery terms',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'Vertex Systems',
                        problem: 'Discount Issue',
                        diff: '+7,800',
                        cause: 'Discount not applied',
                        solution: 'Verify discount policy',
                        outcome: '✅ Successful'
                    },
                    {
                        vendor: 'Deccan Supplies',
                        problem: 'Partial Invoice',
                        diff: '+42,000',
                        cause: 'Partial payment made',
                        solution: 'Check partial invoice status',
                        outcome: '✅ Successful'
                    },
                ].map((memory, idx) => (
                    <div key={idx} className="memory-card">
                        <div className="memory-card-header">
                            <h4>{memory.vendor}</h4>
                            <span className="memory-card-diff">{memory.diff}</span>
                        </div>
                        <div className="memory-card-body">
                            <div className="memory-item">
                                <span className="item-label">Problem:</span>
                                <span>{memory.problem}</span>
                            </div>
                            <div className="memory-item">
                                <span className="item-label">Cause:</span>
                                <span>{memory.cause}</span>
                            </div>
                            <div className="memory-item">
                                <span className="item-label">Solution:</span>
                                <span>{memory.solution}</span>
                            </div>
                            <div className="memory-item outcome">
                                <span>Outcome:</span>
                                <span>{memory.outcome}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function LearningTimeline() {
    return (
        <div className="page">
            <h2 className="page-title">Learning Timeline</h2>
            <div className="timeline">
                {/* Case 1 */}
                <div className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h4>Case 1: NovaTech Freight</h4>
                        <p className="timeline-desc">No memory available</p>
                        <div className="timeline-action without-memory">
                            🔍 Check invoice and contact vendor
                        </div>
                    </div>
                </div>

                {/* Case 2 */}
                <div className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h4>Case 2: Bharat GST</h4>
                        <p className="timeline-desc">No memory available</p>
                        <div className="timeline-action without-memory">
                            🔍 Request GST invoice document
                        </div>
                    </div>
                </div>

                {/* Case 3 */}
                <div className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h4>Case 3: Vertex Systems</h4>
                        <p className="timeline-desc">No memory available</p>
                        <div className="timeline-action without-memory">
                            🔍 Contact vendor to correct duplicate
                        </div>
                    </div>
                </div>

                {/* Case 4 */}
                <div className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h4>Case 4: NovaTech Freight Match</h4>
                        <p className="timeline-desc">Memory created after resolution</p>
                        <div className="timeline-action with-memory">
                            ✨ Memory saved: "Verify freight agreement"
                        </div>
                    </div>
                </div>

                {/* Case 5 */}
                <div className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h4>Case 5: More NovaTech Mismatches</h4>
                        <p className="timeline-desc">1 similar memory found</p>
                        <div className="timeline-action with-memory">
                            🧠 AI Recommendation: "Verify freight agreement"
                        </div>
                    </div>
                </div>

                {/* Case 20 */}
                <div className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-content">
                        <h4>Case 20: Complex NovaTech Pattern</h4>
                        <p className="timeline-desc">Multiple memories found - Pattern detected</p>
                        <div className="timeline-action with-memory">
                            🔍 Previous NovaTech invoice mismatches were often caused by freight charges.
                            Verify the freight agreement before rejecting the invoice.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);