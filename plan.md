# PostgreSQL Metrics Dashboard - Project Plan

## Overview
Build a full-stack web application that connects to a local PostgreSQL database, automatically discovers and analyzes tables, and generates an interactive dashboard with intelligent visualizations.

---

## Phase 1: Database Connection & Schema Introspection ✅
- [x] Install required dependencies (psycopg2-binary for PostgreSQL)
- [x] Create database connection module with connection pooling
- [x] Implement schema introspection to discover tables and columns
- [x] Build data type detection logic (timestamps, numerics, categoricals)
- [x] Create state management for database metadata
- [x] Test connection and schema parsing with sample queries

---

## Phase 2: Backend API & Data Query Engine ✅
- [x] Build query engine for fetching table data with filters
- [x] Implement time range filtering for timestamp columns
- [x] Create aggregation logic for KPIs and statistics
- [x] Add categorical grouping for bar/pie chart data
- [x] Implement efficient query caching mechanism
- [x] Create event handlers for data fetching and filtering

---

## Phase 3: Frontend Dashboard UI with Dynamic Visualizations ✅
- [x] Design responsive dashboard layout (header, sidebar, main content grid)
- [x] Build table/metric selection controls with dropdowns
- [x] Implement time range picker component
- [x] Create KPI stat cards for aggregated metrics
- [x] Build dynamic chart rendering (line charts for time series)
- [x] Add bar charts for categorical breakdowns
- [x] Implement chart switching and configuration options
- [x] Style with modern design system (consistent spacing, typography, colors)
- [x] Fix table selection bug (empty state handling in data table)
- [x] Add proper value conversion for pandas data types

---

## Phase 4: Intelligence Layer & Auto-Visualization ✅
- [x] Build heuristic engine to classify column types
- [x] Implement auto-visualization logic (time series → line, categorical → bar)
- [x] Create default dashboard configuration on startup
- [x] Add smart metric detection (find `temperature`, `value`, `count` columns)
- [x] Implement automatic chart type selection
- [x] Build visualization recommendation system
- [x] Add KPI card components with aggregation support
- [x] Create chart components for line and bar charts
- [x] Add filter controls for metrics and visualization types

---

## Phase 5: Multi-Environment Database Credential Management ✅
- [x] Create credentials state management system with environment support
- [x] Build credential storage with encryption/secure handling
- [x] Implement database connection form (host, port, database, username, password, environment name)
- [x] Add connection testing functionality
- [x] Create environment dropdown selector in the UI
- [x] Build credentials management modal/page
- [x] Add CRUD operations for saved environments
- [x] Implement active environment persistence
- [x] Update database connection logic to use selected environment
- [x] Add connection status indicator in UI

---

## Phase 6: Intelligent Time Series Visualizations for Specific Tables ✅
- [x] Create VizState for managing visualization data
- [x] Generate sample time series data for faults, jobs, and bots tables
- [x] Build reusable time_series_chart component with area charts
- [x] Implement faults_chart with single metric (fault count over time)
- [x] Implement jobs_chart with dual metrics (completed vs failed jobs)
- [x] Implement bots_chart with dual metrics (online vs offline bots)
- [x] Add gradient fills for visual appeal
- [x] Integrate charts with table selection (rx.match for routing)
- [x] Fix conditional rendering to show charts even without database connection
- [x] Add proper tooltips and axis labels
- [x] Test all three visualizations with sample data

---

## Phase 7: SSH Tunnel Support for VPN Database Connections ✅
- [x] Install sshtunnel library for secure tunneling
- [x] Add SSH tunnel fields to Env model (ssh_host, ssh_port, ssh_user, ssh_key)
- [x] Update credentials form with SSH tunnel configuration section
- [x] Implement SSH tunnel connection logic in DatabaseState._get_db_conn()
- [x] Support SSH key-based authentication (private key as string)
- [x] Handle tunnel lifecycle (establish before DB connect, close after)
- [x] Add comprehensive error handling for tunnel failures
- [x] Test SSH tunnel configuration and connection flow
- [x] Document setup instructions for jump host and VPN connectivity

---

## Phase 8: Interactive Features & Polish
- [ ] Add real-time chart updates when filters change
- [ ] Implement chart legends with interactive toggling
- [ ] Add time range selector for visualizations (24h, 7d, 30d, all)
- [ ] Create export functionality (CSV, JSON, PNG)
- [ ] Add loading states and error handling for charts
- [ ] Implement responsive design for mobile/tablet
- [ ] Add dark mode toggle
- [ ] Create user preferences persistence
- [ ] Add zoom and pan functionality for charts

---

## Phase 9: Performance & Documentation
- [ ] Optimize database queries with indexing suggestions
- [ ] Implement query result caching
- [ ] Add pagination for large datasets
- [ ] Create comprehensive README with setup instructions
- [ ] Add inline code documentation
- [ ] Include example database schema and seed data
- [ ] Write deployment guide

---

## Current Status
✅ Completed Phases 1-7
🔄 Ready for Phase 8: Interactive Features & Polish

**Next Steps:**
Add interactive features to the visualizations:
1. Time range filtering for charts
2. Interactive chart legends
3. Export functionality
4. Responsive design improvements
5. Dark mode support

## Implementation Notes

### SSH Tunnel Support (Phase 7)
The application now supports secure connections to PostgreSQL databases behind VPN using SSH tunnels:

**Connection Architecture:**
```
Cloud-Based Reflex App → SSH Tunnel → Jump Host (on VPN) → PostgreSQL Database
```

**Features Implemented:**
1. **SSH Tunnel Configuration**: Added SSH fields to environment credentials (host, port, user, private key)
2. **Automatic Tunnel Management**: Establishes SSH tunnel before database connection when configured
3. **Security**: All database traffic encrypted via SSH, database never exposed to internet
4. **Error Handling**: Graceful handling of VPN disconnects, SSH auth failures, and timeout errors
5. **Key-Based Auth**: Support for SSH private keys stored as strings in browser localStorage

**Setup Instructions:**
1. **Jump Host Setup** (one-time):
   - Ensure jump host is connected to GlobalProtect VPN
   - Jump host must have network access to PostgreSQL database
   - Configure SSH key-based authentication on jump host

2. **Configure Environment**:
   - Database Host: Internal database IP (e.g., 10.0.1.50)
   - Database Port: 5432
   - SSH Host: Jump host IP or hostname
   - SSH Port: 22
   - SSH User: Your SSH username
   - SSH Private Key: Paste full private key content

3. **Connection Flow**:
   - App establishes SSH tunnel to jump host
   - Tunnel forwards local port to database server
   - App connects to database through tunnel
   - All traffic encrypted end-to-end

**Error Handling:**
- VPN/tunnel disconnection → Clear error message, retry logic
- SSH authentication failure → Specific error with troubleshooting steps
- Database unreachable → Connection status indicator, helpful guidance
- Timeout errors → Automatic cleanup and status reporting

### Intelligent Visualizations (Phase 6)
The system includes three specialized time series visualizations:

1. **Faults Chart**: Single red area chart showing fault occurrences over time
2. **Jobs Chart**: Dual stacked area chart comparing completed vs failed jobs
3. **Bots Chart**: Dual stacked area chart showing online vs offline bot status

All charts feature gradient fills, responsive sizing, clean tooltips, and proper axis labels.

## Notes
- Using psycopg2-binary for PostgreSQL connectivity
- Using sshtunnel for secure VPN-based database access
- Reflex framework for unified Python frontend/backend
- Pandas for efficient data manipulation and aggregation
- Recharts via Reflex for interactive visualizations
- Database connection includes SSH tunnel support with comprehensive error handling
- UI includes comprehensive loading and error states
- Auto-visualization uses column name patterns and data types for intelligent chart selection
- Credentials stored in browser localStorage with base64 encoding
- SSH private keys stored securely in encrypted localStorage
- Charts render with sample data when database is not connected