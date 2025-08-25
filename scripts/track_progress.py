#!/usr/bin/env python3
"""
Progress tracking system for job search automation.
Logs metrics, generates reports, and tracks performance over time.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class ProgressTracker:
    """Track and analyze job search progress."""
    
    def __init__(self, db_path: str = "data/progress.db"):
        """Initialize the progress tracker."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        cursor = self.conn.cursor()
        
        # Session tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                jobs_scraped INTEGER,
                jobs_filtered INTEGER,
                applications_generated INTEGER,
                applications_submitted INTEGER,
                time_spent_minutes REAL,
                api_cost REAL,
                notes TEXT
            )
        """)
        
        # Application tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                company TEXT,
                role TEXT,
                location TEXT,
                match_score REAL,
                status TEXT,
                applied_date TIMESTAMP,
                response_date TIMESTAMP,
                response_type TEXT,
                salary_range TEXT,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)
        
        # Metrics tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                metric_name TEXT,
                metric_value REAL,
                category TEXT
            )
        """)
        
        self.conn.commit()
    
    def log_session(self, session_data: Dict[str, Any]) -> int:
        """Log a job search session."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (
                start_time, end_time, jobs_scraped, jobs_filtered,
                applications_generated, applications_submitted,
                time_spent_minutes, api_cost, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_data.get('start_time'),
            session_data.get('end_time'),
            session_data.get('jobs_scraped', 0),
            session_data.get('jobs_filtered', 0),
            session_data.get('applications_generated', 0),
            session_data.get('applications_submitted', 0),
            session_data.get('time_spent_minutes', 0),
            session_data.get('api_cost', 0),
            session_data.get('notes', '')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def log_application(self, app_data: Dict[str, Any]):
        """Log an individual application."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO applications (
                session_id, company, role, location, match_score,
                status, applied_date, response_date, response_type,
                salary_range, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            app_data.get('session_id'),
            app_data.get('company'),
            app_data.get('role'),
            app_data.get('location'),
            app_data.get('match_score', 0),
            app_data.get('status', 'pending'),
            app_data.get('applied_date'),
            app_data.get('response_date'),
            app_data.get('response_type'),
            app_data.get('salary_range'),
            app_data.get('notes', '')
        ))
        self.conn.commit()
    
    def update_application_status(self, app_id: int, status: str, 
                                 response_type: Optional[str] = None):
        """Update application status and response."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE applications 
            SET status = ?, response_date = ?, response_type = ?
            WHERE id = ?
        """, (status, datetime.now(), response_type, app_id))
        self.conn.commit()
    
    def log_metric(self, metric_name: str, value: float, 
                   category: str = "general"):
        """Log a performance metric."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO metrics (date, metric_name, metric_value, category)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().date(), metric_name, value, category))
        self.conn.commit()
    
    def get_weekly_stats(self) -> Dict[str, Any]:
        """Get statistics for the past week."""
        week_ago = datetime.now() - timedelta(days=7)
        
        cursor = self.conn.cursor()
        
        # Session stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(jobs_scraped) as total_scraped,
                SUM(jobs_filtered) as total_filtered,
                SUM(applications_generated) as total_generated,
                SUM(applications_submitted) as total_submitted,
                SUM(time_spent_minutes) as total_time,
                SUM(api_cost) as total_cost
            FROM sessions
            WHERE start_time >= ?
        """, (week_ago,))
        
        session_stats = dict(zip(
            [col[0] for col in cursor.description],
            cursor.fetchone()
        ))
        
        # Application stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_applications,
                AVG(match_score) as avg_match_score,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses,
                COUNT(CASE WHEN response_type = 'interview' THEN 1 END) as interviews
            FROM applications
            WHERE applied_date >= ?
        """, (week_ago,))
        
        app_stats = dict(zip(
            [col[0] for col in cursor.description],
            cursor.fetchone()
        ))
        
        # Calculate rates
        response_rate = 0
        if app_stats['total_applications'] > 0:
            response_rate = (app_stats['responses'] / 
                           app_stats['total_applications']) * 100
        
        interview_rate = 0
        if app_stats['responses'] > 0:
            interview_rate = (app_stats['interviews'] / 
                            app_stats['responses']) * 100
        
        return {
            'sessions': session_stats,
            'applications': app_stats,
            'response_rate': response_rate,
            'interview_rate': interview_rate,
            'time_saved': (40 * 7) - (session_stats['total_time'] or 0) / 60
        }
    
    def generate_dashboard(self, output_path: str = "data/dashboard.html"):
        """Generate an HTML dashboard with metrics."""
        # Get data for last 30 days
        cursor = self.conn.cursor()
        
        # Daily application trend
        cursor.execute("""
            SELECT 
                DATE(applied_date) as date,
                COUNT(*) as applications,
                AVG(match_score) as avg_score
            FROM applications
            WHERE applied_date >= date('now', '-30 days')
            GROUP BY DATE(applied_date)
            ORDER BY date
        """)
        daily_data = cursor.fetchall()
        
        # Response rate by company type
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN company LIKE '%Tech%' THEN 'Tech'
                    WHEN company LIKE '%Finance%' THEN 'Finance'
                    ELSE 'Other'
                END as company_type,
                COUNT(*) as total,
                COUNT(CASE WHEN response_type IS NOT NULL THEN 1 END) as responses
            FROM applications
            GROUP BY company_type
        """)
        company_data = cursor.fetchall()
        
        # Create plotly figures
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Daily Applications', 'Match Score Trend',
                          'Response Rate by Type', 'Time Investment'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
                   [{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Daily applications
        if daily_data:
            dates = [row[0] for row in daily_data]
            apps = [row[1] for row in daily_data]
            scores = [row[2] for row in daily_data]
            
            fig.add_trace(
                go.Scatter(x=dates, y=apps, name='Applications',
                          line=dict(color='blue', width=2)),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=dates, y=scores, name='Avg Match Score',
                          line=dict(color='green', width=2)),
                row=1, col=2
            )
        
        # Response rates
        if company_data:
            types = [row[0] for row in company_data]
            response_rates = [(row[2]/row[1])*100 if row[1] > 0 else 0 
                            for row in company_data]
            
            fig.add_trace(
                go.Bar(x=types, y=response_rates, name='Response Rate %',
                      marker_color='coral'),
                row=2, col=1
            )
        
        # Time investment
        cursor.execute("""
            SELECT 
                DATE(start_time) as date,
                SUM(time_spent_minutes) as minutes
            FROM sessions
            WHERE start_time >= date('now', '-7 days')
            GROUP BY DATE(start_time)
        """)
        time_data = cursor.fetchall()
        
        if time_data:
            dates = [row[0] for row in time_data]
            minutes = [row[1] for row in time_data]
            
            fig.add_trace(
                go.Bar(x=dates, y=minutes, name='Minutes Spent',
                      marker_color='purple'),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title_text="Job Search Automation Dashboard",
            showlegend=False,
            height=800
        )
        
        # Generate HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Job Search Progress Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 20px;
                    background: #f5f5f5;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                .stat-card {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .stat-value {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #2563eb;
                }}
                .stat-label {{
                    color: #666;
                    margin-top: 5px;
                }}
            </style>
        </head>
        <body>
            <h1>📊 Job Search Automation Progress</h1>
            <div class="stats-grid">
                {self._generate_stat_cards()}
            </div>
            <div id="dashboard"></div>
            <script>
                var figure = {fig.to_json()};
                Plotly.newPlot('dashboard', figure.data, figure.layout);
            </script>
        </body>
        </html>
        """
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"Dashboard generated: {output_path}")
    
    def _generate_stat_cards(self) -> str:
        """Generate HTML for statistics cards."""
        stats = self.get_weekly_stats()
        
        cards = []
        cards.append(self._stat_card(
            stats['applications']['total_applications'] or 0,
            "Applications This Week"
        ))
        cards.append(self._stat_card(
            f"{stats['response_rate']:.1f}%",
            "Response Rate"
        ))
        cards.append(self._stat_card(
            f"{stats['time_saved']:.1f}h",
            "Time Saved"
        ))
        cards.append(self._stat_card(
            f"{stats['applications']['avg_match_score'] or 0:.1f}%",
            "Avg Match Score"
        ))
        
        return '\n'.join(cards)
    
    def _stat_card(self, value: Any, label: str) -> str:
        """Generate HTML for a single stat card."""
        return f"""
        <div class="stat-card">
            <div class="stat-value">{value}</div>
            <div class="stat-label">{label}</div>
        </div>
        """
    
    def export_metrics(self, output_path: str = "data/metrics.json"):
        """Export all metrics to JSON."""
        cursor = self.conn.cursor()
        
        # Get all data
        cursor.execute("SELECT * FROM sessions")
        sessions = [dict(zip([col[0] for col in cursor.description], row))
                   for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM applications")
        applications = [dict(zip([col[0] for col in cursor.description], row))
                       for row in cursor.fetchall()]
        
        cursor.execute("SELECT * FROM metrics")
        metrics = [dict(zip([col[0] for col in cursor.description], row))
                  for row in cursor.fetchall()]
        
        data = {
            'export_date': datetime.now().isoformat(),
            'sessions': sessions,
            'applications': applications,
            'metrics': metrics,
            'summary': self.get_weekly_stats()
        }
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Metrics exported to: {output_path}")


def main():
    """CLI interface for progress tracking."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track job search progress')
    parser.add_argument('action', choices=['log', 'stats', 'dashboard', 'export'],
                       help='Action to perform')
    parser.add_argument('--db', default='data/progress.db',
                       help='Database path')
    parser.add_argument('--output', help='Output path for dashboard/export')
    
    args = parser.parse_args()
    
    tracker = ProgressTracker(args.db)
    
    if args.action == 'stats':
        stats = tracker.get_weekly_stats()
        print("\n📊 Weekly Statistics:")
        print("-" * 40)
        print(f"Applications: {stats['applications']['total_applications']}")
        print(f"Response Rate: {stats['response_rate']:.1f}%")
        print(f"Interview Rate: {stats['interview_rate']:.1f}%")
        print(f"Time Saved: {stats['time_saved']:.1f} hours")
        print(f"Avg Match Score: {stats['applications']['avg_match_score']:.1f}%")
    
    elif args.action == 'dashboard':
        output = args.output or 'data/dashboard.html'
        tracker.generate_dashboard(output)
    
    elif args.action == 'export':
        output = args.output or 'data/metrics.json'
        tracker.export_metrics(output)
    
    elif args.action == 'log':
        # Interactive logging
        print("Log a new session:")
        session_data = {
            'start_time': datetime.now(),
            'jobs_scraped': int(input("Jobs scraped: ")),
            'jobs_filtered': int(input("Jobs filtered: ")),
            'applications_generated': int(input("Applications generated: ")),
            'applications_submitted': int(input("Applications submitted: ")),
            'time_spent_minutes': float(input("Time spent (minutes): ")),
            'api_cost': float(input("API cost ($): ")),
            'notes': input("Notes: "),
            'end_time': datetime.now()
        }
        session_id = tracker.log_session(session_data)
        print(f"✅ Session logged with ID: {session_id}")


if __name__ == "__main__":
    main()