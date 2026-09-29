# ExceptionIQ
AI-powered business exception management system with memory capabilities

## Overview
ExceptionIQ helps businesses solve unusual finance/business exceptions by remembering how similar problems were solved previously. The AI analyzes new exceptions against historical data to provide intelligent recommendations.

## Demo Features
1. **Dashboard** - View exception statistics and recent cases
2. **New Exception** - Create new exceptions with auto-calculated differences
3. **AI Investigation** - AI-powered analysis with suggestion of similar cases
4. **Memory Explorer** - Browse all historical memories and solutions
5. **Learning Timeline** - Visualize how the system improves over time

## Technology Stack
- **Frontend**: React + Inline JavaScript (Single HTML file)
- **Backend**: Python FastAPI
- **Database**: SQLite
- **AI**: Rule-based recommendations (demo mode)

## Quick Start

### 1. Install Python Dependencies

Navigate to backend directory:
```bash
cd ExceptionIQ/backend
pip install -r requirements.txt
```

### 2. Start the Backend Server

```bash
cd ExceptionIQ/backend
python main.py
```

The server will start at `http://127.0.0.1:8000`

### 3. Open the Frontend

Open this URL in your browser:
```
http://127.0.0.1:8000
```

## Demo Data

The system comes pre-loaded with 22 mock memories across 4 vendors:
- **NovaTech Solutions** - Freight charge mismatches
- **Bharat Logistics** - Missing GST/Unexpected charges
- **Vertex Systems** - Duplicate invoices/Incorrect PO
- **Deccan Supplies** - Partial invoices/Taxes mismatch

## Demo Flow

1. Navigate to **"New Exception"**
2. Fill in the exception details (try NovaTech Solutions)
3. Click **"Investigate with AI"**
4. See similar memories and AI recommendations
5. Approve or reject the solution
6. Save outcome to memory

## Project Structure

```
ExceptionIQ/
├── frontend/
│   ├── index.html          # Single-page frontend
│   ├── App.js              # React application
│   └── styles.css          # Styling
├── backend/
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   ├── api/
│   │   └── routes.py       # API endpoints
│   └── models/
│       └── database.py     # Database models & operations
├── data/
│   ├── exceptions.db       # Exception records
│   └── mock-hindsight.db   # Hindsight memories
└── README.md
```

## File Locations
- **Backend API**: `http://127.0.0.1:8000/api/`
  - `GET /api/exceptions` - List all exceptions
  - `POST /api/exceptions` - Create new exception
  - `POST /api/investigate` - AI investigation
  - `GET /api/memories` - List memories
  - `POST /api/memories` - Save memory

## Demo Case

Try this exact scenario to see Hindsight in action:

```
Vendor: NovaTech Solutions
Invoice: ₹1,08,000
PO: ₹1,00,000
Difference: ₹8,000
Exception Type: Invoice Amount Mismatch
```

The system will find 2 similar NovaTech memories related to freight charges and provide an AI recommendation based on the pattern.

## Future Enhancements (Not in Demo)
- Real LLM API integration (Anthropic, OpenAI)
- Hindsight API integration
- User authentication
- Advanced filtering & search
- Analytics & reporting
- Multi-tenant support

## License
For hackathon project demonstration only.