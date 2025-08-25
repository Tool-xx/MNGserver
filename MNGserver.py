import sys
import os
import subprocess
import time
import requests
import psutil
import webbrowser
import json
from datetime import datetime, timedelta
from threading import Thread, Event
from collections import deque
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QFileDialog, 
                             QListWidget, QLabel, QMessageBox, QSplitter, 
                             QStatusBar, QAction, QToolBar, QMenu, QTabWidget,
                             QLineEdit, QGroupBox, QFormLayout, QCheckBox,
                             QSpinBox, QComboBox, QScrollArea, QFrame, QGridLayout,
                             QTimeEdit, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QTime
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QPainter
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis

# English translations only
translations = {
    'title': 'MNGserver 🤖',
    'github': 'GitHub Repository',
    'add_script': '📁 Add Script',
    'scripts_list': '📋 Monitored Scripts:',
    'start_monitoring': '▶️ Start Monitoring',
    'stop_monitoring': '⏹️ Stop Monitoring',
    'remove_script': '🗑️ Remove Script',
    'logs': '📝 Logs',
    'stats': '📊 Statistics',
    'settings': '⚙️ Settings',
    'save_logs': '💾 Save Logs',
    'clear_logs': '🧹 Clear Logs',
    'real_time_stats': '📊 Real-time Statistics',
    'status': 'Status:',
    'cpu_usage': 'CPU Usage:',
    'memory_usage': 'Memory Usage:',
    'restarts': 'Restarts:',
    'running': '✅ Running',
    'stopped': '⏹️ Stopped',
    'basic_settings': 'Basic Settings',
    'script_path': 'Script Path:',
    'max_restarts': 'Max Restarts:',
    'check_interval': 'Check Interval:',
    'telegram_settings': 'Telegram Notifications',
    'enable_telegram': 'Enable Telegram Notifications',
    'bot_token': 'Bot Token:',
    'chat_id': 'Chat ID:',
    'test_telegram': 'Test Telegram',
    'save_settings': '💾 Save Settings',
    'language': 'Language:',
    'theme': 'Theme:',
    'light_theme': 'Light',
    'dark_theme': 'Dark',
    'cpu_chart': 'CPU Usage (%)',
    'memory_chart': 'Memory Usage (MB)',
    'system_stats': 'System Statistics',
    'total_cpu': 'Total CPU:',
    'total_memory': 'Total Memory:',
    'script': 'Script:',
    'telegram_test_success': 'Test message sent successfully!',
    'telegram_test_error': 'Failed to send test message',
    'settings_saved': 'Settings saved successfully!',
    'script_added': 'Script added:',
    'script_removed': 'Script removed:',
    'monitoring_started': 'Monitoring started:',
    'monitoring_stopped': 'Monitoring stopped:',
    'confirm_remove': 'Are you sure you want to remove this script?',
    'no_script_selected': 'No script selected',
    'script_already_exists': 'Script already exists',
    'script_not_found': 'Script not found',
    'scheduled_actions': 'Scheduled Actions',
    'enable_scheduled_restart': 'Enable Scheduled Restart',
    'restart_every': 'Restart every:',
    'seconds': 'seconds',
    'minutes': 'minutes',
    'hours': 'hours',
    'export_stats': '📊 Export Statistics',
    'stats_exported': 'Statistics exported successfully!'
}

class MonitorSignals(QObject):
    log_signal = pyqtSignal(str, str)
    status_signal = pyqtSignal(str, str)
    stats_signal = pyqtSignal(str, dict)
    restart_signal = pyqtSignal(str)

class ResourceChart(QChartView):
    def __init__(self, title, max_points=60, y_range=(0, 100)):
        super().__init__()
        self.chart = QChart()
        self.chart.setTitle(title)
        self.chart.legend().hide()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        
        self.series = QLineSeries()
        self.series.setPen(QColor(42, 130, 218))
        self.chart.addSeries(self.series)
        
        self.axis_x = QValueAxis()
        self.axis_x.setRange(0, max_points)
        self.axis_x.setLabelsVisible(False)
        self.axis_x.setGridLineVisible(True)
        
        self.axis_y = QValueAxis()
        self.axis_y.setRange(*y_range)
        self.axis_y.setGridLineVisible(True)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        self.setChart(self.chart)
        self.setRenderHint(QPainter.Antialiasing)
        
        self.data = deque(maxlen=max_points)
        self.max_points = max_points

    def add_data_point(self, value):
        self.data.append(value)
        self.series.clear()
        
        for i, val in enumerate(self.data):
            self.series.append(i, val)

class ScriptLogTab(QWidget):
    def __init__(self, script_name, parent=None):
        super().__init__(parent)
        self.script_name = script_name
        self.parent = parent
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        log_label = QLabel(f"{translations['logs']} - {self.script_name}")
        log_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New';
                font-size: 11px;
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
            }
        """)
        
        # Log buttons
        log_buttons = QHBoxLayout()
        
        self.save_log_btn = QPushButton(translations['save_logs'])
        self.save_log_btn.clicked.connect(self.save_logs)
        self.save_log_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        self.clear_log_btn = QPushButton(translations['clear_logs'])
        self.clear_log_btn.clicked.connect(self.clear_logs)
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #8e44ad;
            }
        """)
        
        log_buttons.addWidget(self.save_log_btn)
        log_buttons.addWidget(self.clear_log_btn)
        log_buttons.addStretch()
        
        layout.addWidget(log_label)
        layout.addWidget(self.log_text)
        layout.addLayout(log_buttons)
    
    def add_log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        self.log_text.clear()
        if self.parent:
            self.parent.log("SYSTEM", f"Logs cleared for {self.script_name}")
    
    def save_logs(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Save Logs - {self.script_name}", "", "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                if self.parent:
                    self.parent.log("SYSTEM", f"Logs for {self.script_name} saved to: {file_path}")
            except Exception as e:
                if self.parent:
                    self.parent.log("SYSTEM", f"Error saving logs for {self.script_name}: {e}")

class ScriptStatsTab(QWidget):
    def __init__(self, script_name, parent=None):
        super().__init__(parent)
        self.script_name = script_name
        self.parent = parent
        self.stats_history = []
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        stats_label = QLabel(f"{translations['stats']} - {self.script_name}")
        stats_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        
        # Create charts
        charts_layout = QHBoxLayout()
        
        self.cpu_chart = ResourceChart(translations['cpu_chart'], 60, (0, 100))
        self.memory_chart = ResourceChart(translations['memory_chart'], 60, (0, 500))
        
        charts_layout.addWidget(self.cpu_chart)
        charts_layout.addWidget(self.memory_chart)
        
        # Current stats
        stats_group = QGroupBox("Current Statistics")
        stats_group.setStyleSheet("color: white;")
        stats_form = QFormLayout()
        
        self.status_label = QLabel("Stopped")
        self.status_label.setStyleSheet("color: #e74c3c;")
        
        self.cpu_label = QLabel("0.0%")
        self.cpu_label.setStyleSheet("color: white;")
        
        self.memory_label = QLabel("0.0 MB")
        self.memory_label.setStyleSheet("color: white;")
        
        self.restarts_label = QLabel("0")
        self.restarts_label.setStyleSheet("color: white;")
        
        self.uptime_label = QLabel("00:00:00")
        self.uptime_label.setStyleSheet("color: white;")
        
        stats_form.addRow(QLabel("Status:"), self.status_label)
        stats_form.addRow(QLabel("CPU Usage:"), self.cpu_label)
        stats_form.addRow(QLabel("Memory Usage:"), self.memory_label)
        stats_form.addRow(QLabel("Restarts:"), self.restarts_label)
        stats_form.addRow(QLabel("Uptime:"), self.uptime_label)
        stats_group.setLayout(stats_form)
        
        # Export button
        self.export_btn = QPushButton(translations['export_stats'])
        self.export_btn.clicked.connect(self.export_stats)
        self.export_btn.setStyleSheet("""
            QPushButton {
                padding: 8px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        
        layout.addWidget(stats_label)
        layout.addLayout(charts_layout)
        layout.addWidget(stats_group)
        layout.addWidget(self.export_btn)
    
    def update_stats(self, stats):
        self.cpu_label.setText(f"{stats['cpu']}%")
        self.memory_label.setText(f"{stats['memory']} MB")
        self.restarts_label.setText(f"{stats['restarts']}")
        self.uptime_label.setText(stats.get('uptime', '00:00:00'))
        
        # Save to history
        stats_with_time = stats.copy()
        stats_with_time['timestamp'] = datetime.now().isoformat()
        self.stats_history.append(stats_with_time)
        
        # Keep only last 1000 records
        if len(self.stats_history) > 1000:
            self.stats_history = self.stats_history[-1000:]
        
        # Update charts
        self.cpu_chart.add_data_point(stats['cpu'])
        self.memory_chart.add_data_point(stats['memory'])
    
    def update_status(self, status, start_time=None):
        if status == 'running':
            self.status_label.setText("Running")
            self.status_label.setStyleSheet("color: #27ae60;")
            if start_time:
                self.start_time = start_time
        elif status == 'stopped':
            self.status_label.setText("Stopped")
            self.status_label.setStyleSheet("color: #e74c3c;")
            self.start_time = None
        else:
            self.status_label.setText(status.capitalize())
            self.status_label.setStyleSheet("color: #f39c12;")
    
    def export_stats(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export Statistics - {self.script_name}", "", "HTML Files (*.html)"
        )
        
        if file_path:
            try:
                self.generate_html_report(file_path)
                if self.parent:
                    self.parent.log("SYSTEM", f"Statistics for {self.script_name} exported to: {file_path}")
                    QMessageBox.information(self, "Success", translations['stats_exported'])
            except Exception as e:
                if self.parent:
                    self.parent.log("SYSTEM", f"Error exporting stats for {self.script_name}: {e}")
    
    def generate_html_report(self, file_path):
        # Generate a beautiful HTML report with charts and statistics
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Statistics Report - {self.script_name}</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #eee;
                }}
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    border-left: 4px solid #3498db;
                }}
                .stat-card h3 {{
                    margin: 0 0 10px 0;
                    font-size: 16px;
                }}
                .stat-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .chart-container {{
                    margin: 30px 0;
                    height: 400px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 MNGserver Statistics Report</h1>
                    <h2>Script: {self.script_name}</h2>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Current Status</h3>
                        <div class="stat-value">{self.status_label.text()}</div>
                    </div>
                    <div class="stat-card">
                        <h3>CPU Usage</h3>
                        <div class="stat-value">{self.cpu_label.text()}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Memory Usage</h3>
                        <div class="stat-value">{self.memory_label.text()}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Restarts</h3>
                        <div class="stat-value">{self.restarts_label.text()}</div>
                    </div>
                    <div class="stat-card">
                        <h3>Uptime</h3>
                        <div class="stat-value">{self.uptime_label.text()}</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <canvas id="cpuChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
                
                <h2>Detailed Statistics History</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>CPU (%)</th>
                            <th>Memory (MB)</th>
                            <th>Uptime</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Add table rows
        for stat in self.stats_history[-100:]:  # Show last 100 records
            timestamp = datetime.fromisoformat(stat['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            html_content += f"""
                        <tr>
                            <td>{timestamp}</td>
                            <td>{stat['cpu']}</td>
                            <td>{stat['memory']}</td>
                            <td>{stat.get('uptime', '00:00:00')}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
            </div>
            
            <script>
                // CPU Chart
                const cpuCtx = document.getElementById('cpuChart').getContext('2d');
                const cpuChart = new Chart(cpuCtx, {
                    type: 'line',
                    data: {
                        labels: [
        """
        
        # Add labels for CPU chart
        labels = [datetime.fromisoformat(stat['timestamp']).strftime('%H:%M:%S') for stat in self.stats_history[-60:]]
        html_content += ', '.join([f'"{label}"' for label in labels])
        
        html_content += """
                        ],
                        datasets: [{
                            label: 'CPU Usage (%)',
                            data: [
        """
        
        # Add data for CPU chart
        cpu_data = [stat['cpu'] for stat in self.stats_history[-60:]]
        html_content += ', '.join([str(cpu) for cpu in cpu_data])
        
        html_content += """
                            ],
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'CPU Usage Over Time'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                });
                
                // Memory Chart
                const memoryCtx = document.getElementById('memoryChart').getContext('2d');
                const memoryChart = new Chart(memoryCtx, {
                    type: 'line',
                    data: {
                        labels: [
        """
        
        # Add labels for Memory chart
        html_content += ', '.join([f'"{label}"' for label in labels])
        
        html_content += """
                        ],
                        datasets: [{
                            label: 'Memory Usage (MB)',
                            data: [
        """
        
        # Add data for Memory chart
        memory_data = [stat['memory'] for stat in self.stats_history[-60:]]
        html_content += ', '.join([str(memory) for memory in memory_data])
        
        html_content += """
                            ],
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Memory Usage Over Time'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

class ScriptMonitor(Thread):
    def __init__(self, script_info):
        super().__init__()
        self.script_info = script_info
        self.script_path = script_info['path']
        self.script_name = script_info['name']
        self.max_restarts = script_info.get('max_restarts', 5)
        self.check_interval = script_info.get('check_interval', 10)
        
        self.telegram_enabled = script_info.get('telegram_enabled', False)
        self.telegram_token = script_info.get('telegram_token', '')
        self.telegram_chat_id = script_info.get('telegram_chat_id', '')
        
        # Scheduled restart settings - УПРОЩЕННАЯ ВЕРСИЯ
        self.scheduled_restart_enabled = script_info.get('scheduled_restart_enabled', False)
        self.restart_interval_value = script_info.get('restart_interval_value', 1)
        self.restart_interval_unit = script_info.get('restart_interval_unit', 'hours')
        
        self.restart_count = script_info.get('restarts', 0)
        self.process = None
        self.stop_event = Event()
        self.signals = MonitorSignals()
        self.daemon = True
        self.last_stats = {'cpu': 0.0, 'memory': 0.0, 'restarts': 0, 'uptime': '00:00:00'}
        self.start_time = None
        self.next_restart_time = self.calculate_next_restart_time()

    def calculate_next_restart_time(self):
        if not self.scheduled_restart_enabled or not self.start_time:
            return None
            
        # Конвертируем в секунды в зависимости от единицы измерения
        unit_multipliers = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600
        }
        
        interval_seconds = self.restart_interval_value * unit_multipliers.get(self.restart_interval_unit, 3600)
        return self.start_time + timedelta(seconds=interval_seconds)

    def run(self):
        self.start_time = datetime.now()
        self.signals.log_signal.emit(self.script_name, f"🚀 Starting monitoring: {self.script_name}")
        self.signals.status_signal.emit(self.script_name, "running")
        
        if not self.start_script():
            self.signals.status_signal.emit(self.script_name, "error")
            return
        
        try:
            while not self.stop_event.is_set():
                time.sleep(self.check_interval)
                
                # Check if it's time for scheduled restart
                if (self.scheduled_restart_enabled and self.next_restart_time and 
                    datetime.now() >= self.next_restart_time and self.is_running()):
                    message = f"⏰ Scheduled restart for {self.script_name}"
                    self.signals.log_signal.emit(self.script_name, message)
                    self.send_telegram_message(message)
                    
                    # Stop the current process
                    if self.process:
                        try:
                            self.process.terminate()
                            self.process.wait(timeout=5)
                        except:
                            try:
                                self.process.kill()
                            except:
                                pass
                    
                    # Restart the script
                    if not self.start_script():
                        self.signals.status_signal.emit(self.script_name, "error")
                        break
                    
                    # Calculate next restart time
                    self.next_restart_time = self.calculate_next_restart_time()
                    continue
                
                self.send_stats()
                
                if not self.is_running() and not self.stop_event.is_set():
                    message = f"⚠️ Script {self.script_name} crashed, restarting..."
                    self.signals.log_signal.emit(self.script_name, message)
                    self.send_telegram_message(message)
                    
                    if not self.restart_script():
                        self.signals.status_signal.emit(self.script_name, "error")
                        break
                
                if self.is_running():
                    self.signals.status_signal.emit(self.script_name, "running")
                    
        except Exception as e:
            error_msg = f"❌ Monitoring error: {e}"
            self.signals.log_signal.emit(self.script_name, error_msg)
            self.send_telegram_message(error_msg)
        finally:
            self.stop()

    def start_script(self):
        try:
            self.process = subprocess.Popen(
                [sys.executable, self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.start_time = datetime.now()
            message = f"✅ Started: {self.script_name}"
            self.signals.log_signal.emit(self.script_name, message)
            self.send_telegram_message(message)
            return True
        except Exception as e:
            error_msg = f"❌ Start error: {e}"
            self.signals.log_signal.emit(self.script_name, error_msg)
            self.send_telegram_message(error_msg)
            return False

    def is_running(self):
        return self.process and self.process.poll() is None

    def restart_script(self):
        if self.restart_count >= self.max_restarts:
            message = f"⛔ Restart limit reached for {self.script_name}"
            self.signals.log_signal.emit(self.script_name, message)
            self.send_telegram_message(message)
            return False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        
        self.restart_count += 1
        self.script_info['restarts'] = self.restart_count
        return self.start_script()

    def send_stats(self):
        stats = {
            'cpu': 0.0,
            'memory': 0.0,
            'restarts': self.restart_count,
            'uptime': '00:00:00'
        }
        
        if self.process and self.is_running() and self.start_time:
            try:
                process = psutil.Process(self.process.pid)
                stats['cpu'] = round(process.cpu_percent(), 1)
                stats['memory'] = round(process.memory_info().rss / 1024 / 1024, 1)
                
                # Calculate uptime
                uptime = datetime.now() - self.start_time
                hours, remainder = divmod(uptime.total_seconds(), 3600)
                minutes, seconds = divmod(remainder, 60)
                stats['uptime'] = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Send only if data changed
        if stats != self.last_stats:
            self.last_stats = stats
            self.signals.stats_signal.emit(self.script_name, stats)

    def send_telegram_message(self, message):
        if not self.telegram_enabled or not self.telegram_token or not self.telegram_chat_id:
            return
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': f"🤖 MNGserver:\n{message}",
                'parse_mode': 'HTML'
            }
            requests.post(url, data=payload, timeout=5)
        except Exception:
            pass

    def stop(self):
        self.stop_event.set()
        if self.process and self.is_running():
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except:
                try:
                    self.process.kill()
                except:
                    pass
        message = f"🛑 Stopped monitoring: {self.script_name}"
        self.signals.log_signal.emit(self.script_name, message)
        self.send_telegram_message(message)
        self.signals.status_signal.emit(self.script_name, "stopped")

class SettingsTab(QWidget):
    def __init__(self, script_info, parent=None):
        super().__init__(parent)
        self.script_info = script_info
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # Basic settings
        basic_group = QGroupBox(translations['basic_settings'])
        basic_layout = QFormLayout()
        
        self.script_path_edit = QLineEdit(self.script_info['path'])
        self.script_path_edit.setReadOnly(True)
        self.browse_btn = QPushButton("...")
        self.browse_btn.clicked.connect(self.browse_script)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.script_path_edit)
        path_layout.addWidget(self.browse_btn)
        
        self.max_restarts_spin = QSpinBox()
        self.max_restarts_spin.setRange(1, 100)
        self.max_restarts_spin.setValue(self.script_info.get('max_restarts', 5))
        
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(1, 300)
        self.check_interval_spin.setValue(self.script_info.get('check_interval', 10))
        self.check_interval_spin.setSuffix("s")
        
        basic_layout.addRow(translations['script_path'], path_layout)
        basic_layout.addRow(translations['max_restarts'], self.max_restarts_spin)
        basic_layout.addRow(translations['check_interval'], self.check_interval_spin)
        basic_group.setLayout(basic_layout)
        
        # Scheduled actions - УПРОЩЕННАЯ ВЕРСИЯ
        scheduled_group = QGroupBox(translations['scheduled_actions'])
        scheduled_layout = QFormLayout()
        
        self.scheduled_restart_enable = QCheckBox(translations['enable_scheduled_restart'])
        self.scheduled_restart_enable.setChecked(self.script_info.get('scheduled_restart_enabled', False))
        self.scheduled_restart_enable.stateChanged.connect(self.toggle_scheduled_fields)
        
        # Поле для числа
        self.restart_interval_value_spin = QSpinBox()
        self.restart_interval_value_spin.setRange(1, 1000)
        self.restart_interval_value_spin.setValue(self.script_info.get('restart_interval_value', 1))
        
        # Выпадающий список для единиц измерения
        self.restart_interval_unit_combo = QComboBox()
        self.restart_interval_unit_combo.addItems(['seconds', 'minutes', 'hours'])
        self.restart_interval_unit_combo.setCurrentText(self.script_info.get('restart_interval_unit', 'hours'))
        
        # Группируем число и единицы измерения в одну строку
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.restart_interval_value_spin)
        interval_layout.addWidget(self.restart_interval_unit_combo)
        interval_layout.addStretch()
        
        scheduled_layout.addRow(self.scheduled_restart_enable)
        scheduled_layout.addRow(QLabel(translations['restart_every']), interval_layout)
        scheduled_group.setLayout(scheduled_layout)
        
        # Telegram settings
        telegram_group = QGroupBox(translations['telegram_settings'])
        telegram_layout = QFormLayout()
        
        self.telegram_enable = QCheckBox(translations['enable_telegram'])
        self.telegram_enable.setChecked(self.script_info.get('telegram_enabled', False))
        self.telegram_enable.stateChanged.connect(self.toggle_telegram_fields)
        
        self.telegram_token_edit = QLineEdit(self.script_info.get('telegram_token', ''))
        self.telegram_token_edit.setPlaceholderText("bot token")
        
        self.telegram_chat_id_edit = QLineEdit(self.script_info.get('telegram_chat_id', ''))
        self.telegram_chat_id_edit.setPlaceholderText("chat id")
        
        self.test_telegram_btn = QPushButton(translations['test_telegram'])
        self.test_telegram_btn.clicked.connect(self.test_telegram)
        
        telegram_layout.addRow(self.telegram_enable)
        telegram_layout.addRow(translations['bot_token'], self.telegram_token_edit)
        telegram_layout.addRow(translations['chat_id'], self.telegram_chat_id_edit)
        telegram_layout.addRow(self.test_telegram_btn)
        telegram_group.setLayout(telegram_layout)
        
        # Save button
        self.save_btn = QPushButton(translations['save_settings'])
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        layout.addWidget(basic_group)
        layout.addWidget(scheduled_group)
        layout.addWidget(telegram_group)
        layout.addStretch()
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
        self.toggle_scheduled_fields()
        self.toggle_telegram_fields()
        
    def toggle_scheduled_fields(self):
        enabled = self.scheduled_restart_enable.isChecked()
        self.restart_interval_value_spin.setEnabled(enabled)
        self.restart_interval_unit_combo.setEnabled(enabled)
        
    def toggle_telegram_fields(self):
        enabled = self.telegram_enable.isChecked()
        self.telegram_token_edit.setEnabled(enabled)
        self.telegram_chat_id_edit.setEnabled(enabled)
        self.test_telegram_btn.setEnabled(enabled)
        
    def browse_script(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Python script", "", "Python Files (*.py)")
        if file_path:
            self.script_path_edit.setText(file_path)
            
    def test_telegram(self):
        if self.telegram_enable.isChecked():
            token = self.telegram_token_edit.text().strip()
            chat_id = self.telegram_chat_id_edit.text().strip()
            
            if not token or not chat_id:
                QMessageBox.warning(self, "Error", "Please fill all Telegram fields")
                return
                
            try:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': '✅ Test message from MNGserver',
                    'parse_mode': 'HTML'
                }
                response = requests.post(url, data=payload, timeout=10)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", translations['telegram_test_success'])
                else:
                    QMessageBox.warning(self, "Error", translations['telegram_test_error'])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"{translations['telegram_test_error']}: {e}")
                
    def save_settings(self):
        self.script_info['path'] = self.script_path_edit.text()
        self.script_info['max_restarts'] = self.max_restarts_spin.value()
        self.script_info['check_interval'] = self.check_interval_spin.value()
        
        # Scheduled actions - УПРОЩЕННАЯ ВЕРСИЯ
        self.script_info['scheduled_restart_enabled'] = self.scheduled_restart_enable.isChecked()
        self.script_info['restart_interval_value'] = self.restart_interval_value_spin.value()
        self.script_info['restart_interval_unit'] = self.restart_interval_unit_combo.currentText()
        
        # Telegram settings
        self.script_info['telegram_enabled'] = self.telegram_enable.isChecked()
        self.script_info['telegram_token'] = self.telegram_token_edit.text().strip()
        self.script_info['telegram_chat_id'] = self.telegram_chat_id_edit.text().strip()
        
        if self.parent and self.script_info['name'] in self.parent.monitors:
            script_info = self.parent.monitors[self.script_info['name']]
            if script_info['monitor'] and script_info['monitor'].is_alive():
                script_info['monitor'].stop()
                self.parent.start_monitoring_for_script(self.script_info['name'])
        
        QMessageBox.information(self, "Success", translations['settings_saved'])

class ServerMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.monitors = {}
        self.current_script = None
        self.script_tabs = {}  # Хранит вкладки для каждого скрипта
        self.initUI()
        
    def tr(self, key):
        return translations.get(key, key)

    def initUI(self):
        self.setWindowTitle(self.tr('title'))
        self.setGeometry(100, 100, 1600, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Title with GitHub link
        title_label = QLabel("MNGserver")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("padding: 10px; color: white;")
        
        github_label = QLabel(f'<a href="https://github.com/Tool-xx/MNGserver" style="color: #3498db;">{self.tr("github")}</a>')
        github_label.setAlignment(Qt.AlignCenter)
        github_label.setOpenExternalLinks(True)
        github_label.linkActivated.connect(webbrowser.open)
        
        # Add script button
        self.add_btn = QPushButton(self.tr('add_script'))
        self.add_btn.clicked.connect(self.add_script)
        self.add_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                margin: 5px;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        
        # Scripts list
        scripts_label = QLabel(self.tr('scripts_list'))
        scripts_label.setStyleSheet("font-weight: bold; margin-top: 10px; color: white;")
        
        self.script_list = QListWidget()
        self.script_list.currentItemChanged.connect(self.on_script_selected)
        self.script_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #555;
                border-radius: 5px;
                background: #353535;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444;
            }
            QListWidget::item:selected {
                background: #2a82da;
                color: white;
            }
        """)
        
        left_layout.addWidget(title_label)
        left_layout.addWidget(github_label)
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(scripts_label)
        left_layout.addWidget(self.script_list)
        left_layout.addStretch()
        
        # Right panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Control buttons
        self.control_buttons_widget = QWidget()
        self.control_buttons_layout = QHBoxLayout(self.control_buttons_widget)
        
        self.start_btn = QPushButton(self.tr('start_monitoring'))
        self.start_btn.clicked.connect(self.start_monitoring)
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        self.stop_btn = QPushButton(self.tr('stop_monitoring'))
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        
        self.remove_btn = QPushButton(self.tr('remove_script'))
        self.remove_btn.clicked.connect(self.remove_script)
        self.remove_btn.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 2px;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        self.control_buttons_layout.addWidget(self.start_btn)
        self.control_buttons_layout.addWidget(self.stop_btn)
        self.control_buttons_layout.addWidget(self.remove_btn)
        
        # Main tabs for scripts
        self.tab_widget = QTabWidget()
        
        right_layout.addWidget(self.control_buttons_widget)
        right_layout.addWidget(self.tab_widget)
        
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)
        
        # Timers
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats_display)
        self.stats_timer.start(1000)
        
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(1000)
        
        self.update_control_buttons()
        self.apply_dark_theme()

    def apply_dark_theme(self):
        # Dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #353535;
                color: white;
            }
            QGroupBox {
                color: white;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                background: #454545;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background: #353535;
            }
            QTabBar::tab {
                background: #454545;
                color: white;
                padding: 8px 16px;
                border: 1px solid #555;
                border-radius: 4px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: #2a82da;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QSpinBox {
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QDoubleSpinBox {
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QTimeEdit {
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QComboBox {
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
            QCheckBox {
                color: white;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                background: #454545;
                border: 1px solid #555;
            }
            QCheckBox::indicator:checked {
                background: #2a82da;
                border: 1px solid #2a82da;
            }
        """)
        
        QApplication.setPalette(palette)

    def update_ui(self):
        self.update_script_list_status()
        self.update_control_buttons()

    def update_script_list_status(self):
        for i in range(self.script_list.count()):
            item = self.script_list.item(i)
            script_name = item.text().replace("🟢 ", "").replace("🔴 ", "")
            
            if script_name in self.monitors:
                status = self.monitors[script_name]['status']
                
                if status == 'running':
                    if not item.text().startswith("🟢 "):
                        item.setText(f"🟢 {script_name}")
                else:
                    if not item.text().startswith("🔴 "):
                        item.setText(f"🔴 {script_name}")
        
    def update_control_buttons(self):
        has_selection = self.current_script is not None
        
        self.start_btn.setVisible(has_selection)
        self.stop_btn.setVisible(has_selection)
        self.remove_btn.setVisible(has_selection)
        
        if has_selection and self.current_script in self.monitors:
            script_info = self.monitors[self.current_script]
            is_running = script_info['status'] == 'running'
            
            self.start_btn.setVisible(not is_running)
            self.stop_btn.setVisible(is_running)
        
    def on_script_selected(self, current, previous):
        if current:
            clean_name = current.text().replace("🟢 ", "").replace("🔴 ", "")
            self.current_script = clean_name
            
            # Показываем вкладки для выбранного скрипта
            self.show_script_tabs(clean_name)
            self.update_control_buttons()
            
    def show_script_tabs(self, script_name):
        """Показывает вкладки для выбранного скрипта"""
        # Удаляем все текущие вкладки
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        
        # Добавляем вкладки выбранного скрипта
        if script_name in self.script_tabs:
            script_tabs = self.script_tabs[script_name]
            self.tab_widget.addTab(script_tabs['widget'], f"{script_name}")
            
    def add_script(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Python script", "", "Python Files (*.py)"
        )
        
        if file_path:
            script_name = os.path.basename(file_path)
            if script_name not in self.monitors:
                self.script_list.addItem(f"🔴 {script_name}")
                
                script_config = {
                    'name': script_name,
                    'path': file_path,
                    'monitor': None,
                    'status': 'stopped',
                    'restarts': 0,
                    'max_restarts': 5,
                    'check_interval': 10,
                    'telegram_enabled': False,
                    'telegram_token': '',
                    'telegram_chat_id': '',
                    # УБРАНЫ НАСТРОЙКИ ПРОКСИ
                    'scheduled_restart_enabled': False,
                    'restart_interval_value': 1,  # Новая упрощенная настройка
                    'restart_interval_unit': 'hours',  # Новая упрощенная настройка
                    'stats': {'cpu': 0.0, 'memory': 0.0, 'restarts': 0, 'uptime': '00:00:00'}
                }
                
                self.monitors[script_name] = script_config
                
                # Создаем вкладки для нового скрипта
                self.create_tabs_for_script(script_name)
                
                self.log(script_name, f"{self.tr('script_added')} {script_name}")
            else:
                QMessageBox.warning(self, "Warning", self.tr('script_already_exists'))
    
    def create_tabs_for_script(self, script_name):
        """Создает вкладки для конкретного скрипта"""
        if script_name not in self.script_tabs:
            # Создаем виджет с вкладками для этого скрипта
            script_tab_widget = QTabWidget()
            
            # Вкладка логов
            log_tab = ScriptLogTab(script_name, self)
            
            # Вкладка статистики
            stats_tab = ScriptStatsTab(script_name, self)
            
            # Вкладка настроек
            settings_tab = SettingsTab(self.monitors[script_name], self)
            
            script_tab_widget.addTab(log_tab, translations['logs'])
            script_tab_widget.addTab(stats_tab, translations['stats'])
            script_tab_widget.addTab(settings_tab, translations['settings'])
            
            self.script_tabs[script_name] = {
                'widget': script_tab_widget,
                'log_tab': log_tab,
                'stats_tab': stats_tab,
                'settings_tab': settings_tab
            }
    
    def remove_script(self):
        if not self.current_script:
            QMessageBox.warning(self, "Warning", self.tr('no_script_selected'))
            return
            
        reply = QMessageBox.question(
            self, "Confirmation", 
            self.tr('confirm_remove'),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.current_script in self.monitors:
                monitor = self.monitors[self.current_script]['monitor']
                if monitor and monitor.is_alive():
                    monitor.stop()
                
                # Удаляем вкладки скрипта
                if self.current_script in self.script_tabs:
                    self.script_tabs[self.current_script]['widget'].setParent(None)
                    del self.script_tabs[self.current_script]
                
                del self.monitors[self.current_script]
            
            # Find and remove item considering status emoji
            items = []
            for i in range(self.script_list.count()):
                item_text = self.script_list.item(i).text()
                clean_name = item_text.replace("🟢 ", "").replace("🔴 ", "")
                if clean_name == self.current_script:
                    items.append(self.script_list.item(i))
            
            for item in items:
                self.script_list.takeItem(self.script_list.row(item))
            
            self.log(self.current_script, f"{self.tr('script_removed')} {self.current_script}")
            self.current_script = None
            
            # Очищаем вкладки
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
            
            self.update_control_buttons()
    
    def start_monitoring(self):
        if not self.current_script:
            QMessageBox.warning(self, "Warning", self.tr('no_script_selected'))
            return
            
        self.start_monitoring_for_script(self.current_script)
    
    def start_monitoring_for_script(self, script_name):
        if script_name in self.monitors:
            script_info = self.monitors[script_name]
            
            if script_info['monitor'] is None or not script_info['monitor'].is_alive():
                monitor = ScriptMonitor(script_info)
                monitor.signals.log_signal.connect(self.log)
                monitor.signals.status_signal.connect(self.update_status)
                monitor.signals.stats_signal.connect(self.update_stats)
                
                script_info['monitor'] = monitor
                script_info['status'] = 'starting'
                monitor.start()
                self.log(script_name, f"{self.tr('monitoring_started')} {script_name}")
    
    def stop_monitoring(self):
        if not self.current_script:
            QMessageBox.warning(self, "Warning", self.tr('no_script_selected'))
            return
            
        script_info = self.monitors[self.current_script]
        
        if script_info['monitor'] and script_info['monitor'].is_alive():
            script_info['monitor'].stop()
            script_info['status'] = 'stopped'
            self.log(self.current_script, f"{self.tr('monitoring_stopped')} {self.current_script}")
    
    def update_status(self, script_name, status):
        if script_name in self.monitors:
            self.monitors[script_name]['status'] = status
            
            # Обновляем статус во вкладке статистики
            if script_name in self.script_tabs:
                start_time = None
                if status == 'running' and self.monitors[script_name]['monitor']:
                    start_time = self.monitors[script_name]['monitor'].start_time
                self.script_tabs[script_name]['stats_tab'].update_status(status, start_time)
    
    def update_stats(self, script_name, stats):
        if script_name in self.monitors:
            self.monitors[script_name]['stats'] = stats
            self.monitors[script_name]['restarts'] = stats['restarts']
            
            # Обновляем статистику во вкладке
            if script_name in self.script_tabs:
                self.script_tabs[script_name]['stats_tab'].update_stats(stats)
    
    def update_stats_display(self):
        # Можно добавить обновление системной статистики если нужно
        pass
    
    def log(self, script_name, message):
        # Добавляем лог в соответствующую вкладку скрипта
        if script_name in self.script_tabs:
            self.script_tabs[script_name]['log_tab'].add_log(message)
    
    def closeEvent(self, event):
        # Stop all monitors
        for script_name, script_info in self.monitors.items():
            if script_info['monitor'] and script_info['monitor'].is_alive():
                script_info['monitor'].stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ServerMonitorGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
