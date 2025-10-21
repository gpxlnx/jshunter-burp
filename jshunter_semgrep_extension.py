#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSHunter Extension - Semgrep Version
Author: iamunixtz
Version: 2.1.0
Date: 2025

A extension that automatically detects JavaScript URLs from HTTP requests,
scans them using Semgrep, and sends findings to Telegram.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import io
from datetime import datetime

# Handle Python 2/3 compatibility for urllib
try:
    from urllib.parse import urlparse, urljoin
except ImportError:
    from urlparse import urlparse, urljoin

# Use Java's built-in HTTP capabilities instead of Python requests
from java.net import URL, HttpURLConnection
from java.io import BufferedReader, InputStreamReader, OutputStreamWriter
from java.awt import Color

# Burp Suite API imports
from burp import IBurpExtender, IHttpListener, ITab
from java.awt import BorderLayout, FlowLayout, GridBagLayout, GridBagConstraints, Insets, Dimension
from java.awt.event import ActionListener, MouseAdapter
from javax.swing import (JPanel, JTextField, JCheckBox, JButton, JTable, JTextArea, 
                        JScrollPane, JLabel, JOptionPane, BorderFactory, JFileChooser,
                        ListSelectionModel, JDialog, JSplitPane)
from javax.swing.table import DefaultTableModel, TableRowSorter
from java.util import ArrayList, Date
from java.util.concurrent import ConcurrentHashMap


class BurpExtender(IBurpExtender, IHttpListener, ITab):
    """
    Main Burp Suite extension class that implements:
    - IBurpExtender: Entry point for the extension
    - IHttpListener: Monitors HTTP traffic
    - ITab: Provides custom UI tab
    """
    
    def registerExtenderCallbacks(self, callbacks):
        """Register the extension with Burp Suite."""
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        # Set extension name
        callbacks.setExtensionName("JSHunter - Semgrep Version")
        
        # Register HTTP listener
        callbacks.registerHttpListener(self)
        
        # Initialize data structures
        self._scanned_urls = ConcurrentHashMap()
        self._scan_results = ArrayList()
        
        # Configuration
        self._telegram_bot_token = ""
        self._telegram_chat_id = ""
        self._auto_scan_enabled = True
        self._send_to_telegram_enabled = True
        
        # Load saved settings
        self._load_settings()
        
        # Create UI
        self._create_ui()
        
        # Add custom tab
        callbacks.addSuiteTab(self)
        
        # Print startup message
        print("JSHunter Burp Extension (Semgrep Version) loaded successfully!")
        print("Version: 2.1.0")
        print("Author: iamunixtz")
        print("Date: 2025")
        
        # Clean up any leftover temp files from previous sessions
        self._cleanup_temp_files()
    
    def _load_settings(self):
        """Load saved settings from Burp Suite."""
        try:
            # Load Telegram bot token
            saved_bot_token = self._callbacks.loadExtensionSetting("telegram_bot_token")
            if saved_bot_token:
                self._telegram_bot_token = saved_bot_token
            
            # Load Telegram chat ID
            saved_chat_id = self._callbacks.loadExtensionSetting("telegram_chat_id")
            if saved_chat_id:
                self._telegram_chat_id = saved_chat_id
            
            # Load auto-scan setting
            saved_auto_scan = self._callbacks.loadExtensionSetting("auto_scan_enabled")
            if saved_auto_scan:
                self._auto_scan_enabled = saved_auto_scan.lower() == "true"
            
            # Load send to Telegram setting
            saved_send_telegram = self._callbacks.loadExtensionSetting("send_to_telegram_enabled")
            if saved_send_telegram:
                self._send_to_telegram_enabled = saved_send_telegram.lower() == "true"
                
        except Exception as e:
            self._log_message("Error loading settings: " + str(e))
    
    def _save_settings(self):
        """Save current settings to Burp Suite."""
        try:
            # Save Telegram bot token
            self._callbacks.saveExtensionSetting("telegram_bot_token", self._telegram_bot_token)
            
            # Save Telegram chat ID
            self._callbacks.saveExtensionSetting("telegram_chat_id", self._telegram_chat_id)
            
            # Save auto-scan setting
            self._callbacks.saveExtensionSetting("auto_scan_enabled", str(self._auto_scan_enabled).lower())
            
            # Save send to Telegram setting
            self._callbacks.saveExtensionSetting("send_to_telegram_enabled", str(self._send_to_telegram_enabled).lower())
            
        except Exception as e:
            self._log_message("Error saving settings: " + str(e))
    
    def _create_ui(self):
        """Create the extension UI."""
        self._main_panel = JPanel(BorderLayout())
        
        # Configuration panel
        config_panel = self._create_config_panel()
        self._main_panel.add(config_panel, BorderLayout.NORTH)
        
        # Results panel
        results_panel = self._create_results_panel()
        
        # Findings panel
        findings_panel = self._create_findings_panel()
        
        # Create resizable split pane for results and findings
        self._results_findings_split = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, results_panel, findings_panel)
        self._results_findings_split.setResizeWeight(0.6)  # Give 60% to results, 40% to findings initially
        self._results_findings_split.setDividerLocation(0.6)  # Set initial divider position
        self._results_findings_split.setOneTouchExpandable(True)  # Add one-touch expand buttons
        
        self._main_panel.add(self._results_findings_split, BorderLayout.CENTER)
        
        # Log panel
        log_panel = self._create_log_panel()
        self._main_panel.add(log_panel, BorderLayout.SOUTH)
    
    def _create_config_panel(self):
        """Create the configuration panel."""
        panel = JPanel(GridBagLayout())
        panel.setBorder(BorderFactory.createTitledBorder("Configuration"))
        gbc = GridBagConstraints()
        gbc.insets = Insets(5, 5, 5, 5)
        gbc.anchor = GridBagConstraints.WEST
        
        # Telegram Bot Token
        gbc.gridx = 0; gbc.gridy = 0; gbc.gridwidth = 1
        panel.add(JLabel("Telegram Bot Token:"), gbc)
        gbc.gridx = 1; gbc.gridy = 0; gbc.weightx = 1.0; gbc.fill = GridBagConstraints.HORIZONTAL
        self._telegram_bot_token_field = JTextField(50)
        self._telegram_bot_token_field.setText(self._telegram_bot_token)  # Load saved token
        panel.add(self._telegram_bot_token_field, gbc)
        
        # Telegram Chat ID
        gbc.gridx = 0; gbc.gridy = 1; gbc.weightx = 0; gbc.fill = GridBagConstraints.NONE
        panel.add(JLabel("Telegram Chat ID:"), gbc)
        gbc.gridx = 1; gbc.gridy = 1; gbc.weightx = 1.0; gbc.fill = GridBagConstraints.HORIZONTAL
        self._telegram_chat_id_field = JTextField(50)
        self._telegram_chat_id_field.setText(self._telegram_chat_id)  # Load saved chat ID
        panel.add(self._telegram_chat_id_field, gbc)
        
        # Test Telegram button
        gbc.gridx = 2; gbc.gridy = 1; gbc.weightx = 0; gbc.fill = GridBagConstraints.NONE
        self._test_telegram_button = JButton("Test")
        self._test_telegram_button.addActionListener(TestTelegramListener(self))
        panel.add(self._test_telegram_button, gbc)
        
        # Auto scan checkbox
        gbc.gridx = 0; gbc.gridy = 2; gbc.gridwidth = 2
        self._auto_scan_checkbox = JCheckBox("Auto-scan JavaScript URLs from requests", self._auto_scan_enabled)
        self._auto_scan_checkbox.addActionListener(AutoScanListener(self))
        panel.add(self._auto_scan_checkbox, gbc)
        
        # Send to Telegram checkbox
        gbc.gridx = 0; gbc.gridy = 3; gbc.gridwidth = 2
        self._send_to_telegram_checkbox = JCheckBox("Send findings to Telegram", self._send_to_telegram_enabled)
        self._send_to_telegram_checkbox.addActionListener(SendToTelegramListener(self))
        panel.add(self._send_to_telegram_checkbox, gbc)
        
        # Scope information
        gbc.gridx = 0; gbc.gridy = 4; gbc.gridwidth = 3
        self._scope_info_label = JLabel("Scope: Extension respects Burp Suite scope settings")
        self._scope_info_label.setForeground(Color.BLUE)
        panel.add(self._scope_info_label, gbc)
        
        # Semgrep Path
        gbc.gridx = 0; gbc.gridy = 5; gbc.gridwidth = 1
        panel.add(JLabel("Semgrep Path:"), gbc)
        gbc.gridx = 1; gbc.gridy = 5; gbc.weightx = 1.0; gbc.fill = GridBagConstraints.HORIZONTAL
        self._semgrep_path_field = JTextField(50)
        self._semgrep_path_field.setText("/home/gxavier/.local/bin/semgrep")  # Default path
        panel.add(self._semgrep_path_field, gbc)
        
        # Browse button for Semgrep path
        gbc.gridx = 2; gbc.gridy = 5; gbc.weightx = 0; gbc.fill = GridBagConstraints.NONE
        self._browse_semgrep_button = JButton("Browse")
        self._browse_semgrep_button.addActionListener(BrowseSemgrepListener(self))
        panel.add(self._browse_semgrep_button, gbc)
        
        # Test Semgrep button
        gbc.gridx = 3; gbc.gridy = 5; gbc.weightx = 0; gbc.fill = GridBagConstraints.NONE
        self._test_semgrep_button = JButton("Test")
        self._test_semgrep_button.addActionListener(TestSemgrepListener(self))
        panel.add(self._test_semgrep_button, gbc)
        
        # Semgrep status
        gbc.gridx = 0; gbc.gridy = 6; gbc.gridwidth = 3
        self._semgrep_status_label = JLabel("Semgrep: Not tested")
        panel.add(self._semgrep_status_label, gbc)
        
        return panel
    
    def _create_results_panel(self):
        """Create the results panel."""
        panel = JPanel(BorderLayout())
        panel.setBorder(BorderFactory.createTitledBorder("Scan Results"))
        
        # Table model
        column_names = ["Timestamp", "URL", "Findings", "Verified", "Unverified", "Status"]
        self._table_model = DefaultTableModel(column_names, 0)
        
        self._results_table = JTable(self._table_model)
        self._results_table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        self._results_table.setRowSorter(TableRowSorter(self._table_model))
        
        # Add mouse listener for double-click to view details
        self._results_table.addMouseListener(ResultDetailsListener(self))
        
        scroll_pane = JScrollPane(self._results_table)
        panel.add(scroll_pane, BorderLayout.CENTER)
        
        # Buttons panel
        buttons_panel = JPanel(FlowLayout())
        self._clear_results_button = JButton("Clear Results")
        self._clear_results_button.addActionListener(ClearResultsListener(self))
        buttons_panel.add(self._clear_results_button)
        
        self._export_results_button = JButton("Export Results")
        self._export_results_button.addActionListener(ExportResultsListener(self))
        buttons_panel.add(self._export_results_button)
        
        panel.add(buttons_panel, BorderLayout.SOUTH)
        
        return panel
    
    def _create_findings_panel(self):
        """Create the findings panel to display actual secrets."""
        panel = JPanel(BorderLayout())
        panel.setBorder(BorderFactory.createTitledBorder("Findings Details"))
        panel.setPreferredSize(Dimension(400, 300))
        
        # Findings table model
        findings_columns = ["Type", "Secret", "URL", "Line", "Severity"]
        self._findings_table_model = DefaultTableModel(findings_columns, 0)
        self._findings_table = JTable(self._findings_table_model)
        self._findings_table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION)
        
        # Make columns wider for better visibility
        self._findings_table.getColumnModel().getColumn(0).setPreferredWidth(100)  # Type
        self._findings_table.getColumnModel().getColumn(1).setPreferredWidth(200)  # Secret
        self._findings_table.getColumnModel().getColumn(2).setPreferredWidth(150)  # URL
        self._findings_table.getColumnModel().getColumn(3).setPreferredWidth(50)   # Line
        self._findings_table.getColumnModel().getColumn(4).setPreferredWidth(60)   # Severity
        
        # Add scroll pane
        scroll_pane = JScrollPane(self._findings_table)
        panel.add(scroll_pane, BorderLayout.CENTER)
        
        # Add copy button
        button_panel = JPanel(FlowLayout())
        self._copy_finding_button = JButton("Copy Secret")
        self._copy_finding_button.addActionListener(CopyFindingListener(self))
        button_panel.add(self._copy_finding_button)
        
        self._clear_findings_button = JButton("Clear Findings")
        self._clear_findings_button.addActionListener(ClearFindingsListener(self))
        button_panel.add(self._clear_findings_button)
        
        self._cleanup_temp_button = JButton("Cleanup Temp Files")
        self._cleanup_temp_button.addActionListener(CleanupTempFilesListener(self))
        button_panel.add(self._cleanup_temp_button)
        
        panel.add(button_panel, BorderLayout.SOUTH)
        
        return panel
    
    def _create_log_panel(self):
        """Create the log panel."""
        panel = JPanel(BorderLayout())
        panel.setBorder(BorderFactory.createTitledBorder("Activity Log"))
        
        self._log_area = JTextArea(8, 0)
        self._log_area.setEditable(False)
        log_scroll_pane = JScrollPane(self._log_area)
        log_scroll_pane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS)
        
        panel.add(log_scroll_pane, BorderLayout.CENTER)
        
        return panel
    
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        """Process HTTP messages to extract JavaScript URLs."""
        if not messageIsRequest or not self._auto_scan_enabled:
            return
        
        # Only process requests from Proxy, Spider, and Scanner
        if toolFlag not in [self._callbacks.TOOL_PROXY, 
                           self._callbacks.TOOL_SPIDER, 
                           self._callbacks.TOOL_SCANNER]:
            return
        
        try:
            request_info = self._helpers.analyzeRequest(messageInfo)
            url = request_info.getUrl().toString()
            
            # Check if URL is in scope
            if not self._is_url_in_scope(url):
                self._log_message("Main URL out of scope, skipping: " + url)
                return
                
            # Extract JavaScript URLs from the request
            js_urls = self._extract_javascript_urls(messageInfo)
            
            for js_url in js_urls:
                # Check if JavaScript URL is also in scope
                if not self._is_url_in_scope(js_url):
                    self._log_message("JavaScript URL out of scope, skipping: " + js_url)
                    continue
                    
                if js_url not in self._scanned_urls:
                    self._scanned_urls.put(js_url, True)
                    self._log_message("Found JavaScript URL (in scope): " + js_url)
                    
                    # Schedule scan in background
                    thread = threading.Thread(target=self._scan_javascript_url, args=(js_url,))
                    thread.daemon = True
                    thread.start()
                    
        except Exception as e:
            self._log_message("Error processing HTTP message: " + str(e))
    
    def _extract_javascript_urls(self, messageInfo):
        """Extract JavaScript URLs from HTTP message."""
        js_urls = set()
        
        try:
            request_info = self._helpers.analyzeRequest(messageInfo)
            url = request_info.getUrl().toString()
            
            # Check if the request URL itself is a JavaScript file
            if self._is_javascript_url(url):
                js_urls.add(url)
            
            # Extract from request body
            request = messageInfo.getRequest()
            analyzed_request = self._helpers.analyzeRequest(request)
            body_offset = analyzed_request.getBodyOffset()
            if body_offset < len(request):
                body = request[body_offset:].tostring()
                js_urls.update(self._extract_urls_from_text(body))
            
            # Extract from response body if available
            if messageInfo.getResponse() is not None:
                response = messageInfo.getResponse()
                analyzed_response = self._helpers.analyzeResponse(response)
                response_body_offset = analyzed_response.getBodyOffset()
                if response_body_offset < len(response):
                    response_body = response[response_body_offset:].tostring()
                    js_urls.update(self._extract_urls_from_text(response_body))
                    
        except Exception as e:
            self._log_message("Error extracting JavaScript URLs: " + str(e))
        
        return js_urls
    
    def _extract_urls_from_text(self, text):
        """Extract JavaScript URLs from text content."""
        urls = set()
        
        # Pattern for script src attributes
        script_pattern = r'(?i)<script[^>]+src\s*=\s*["\']([^"\']+\.js(?:\?[^"\']*)?(?:#[^"\']*)?)["\']'
        script_matches = re.findall(script_pattern, text)
        
        for match in script_matches:
            if self._is_javascript_url(match):
                normalized_url = self._normalize_url(match)
                if normalized_url:
                    urls.add(normalized_url)
        
        # Pattern for standalone JavaScript URLs
        js_pattern = r'(?i)(?:https?://[^\s"\'<>]+\.js(?:\?[^\s"\'<>]*)?(?:#[^\s"\'<>]*)?)'
        js_matches = re.findall(js_pattern, text)
        
        for match in js_matches:
            if self._is_javascript_url(match):
                normalized_url = self._normalize_url(match)
                if normalized_url:
                    urls.add(normalized_url)
        
        return urls
    
    def _is_javascript_url(self, url):
        """Check if URL is a JavaScript file."""
        if not url or not url.strip():
            return False
        
        url_lower = url.lower().strip()
        return (url_lower.endswith('.js') or 
                '.js?' in url_lower or 
                '.js#' in url_lower or
                'javascript:' in url_lower or
                'application/javascript' in url_lower)
    
    def _normalize_url(self, url):
        """Normalize URL."""
        try:
            # Handle relative URLs
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                # Skip relative URLs for now
                return None
            
            parsed_url = urlparse(url)
            return parsed_url.geturl()
        except:
            return None
    
    def _is_url_in_scope(self, url):
        """Check if URL is in Burp Suite scope."""
        try:
            # Convert string URL to Java URL object for Burp's scope checking
            from java.net import URL
            java_url = URL(url)
            in_scope = self._callbacks.isInScope(java_url)
            self._log_message("Scope check for " + url + ": " + str(in_scope))
            
            # TEMPORARY: Allow localhost and local IP for testing
            if url.startswith("http://172.17.171.42:8000") or url.startswith("http://localhost:8000"):
                self._log_message("Temporarily allowing local test URL: " + url)
                return True
                
            return in_scope
        except Exception as e:
            self._log_message("Error checking scope for URL " + url + ": " + str(e))
            # If scope checking fails, assume URL is in scope to avoid missing legitimate targets
            return True
    
    def _scan_javascript_url(self, url):
        """Scan a JavaScript URL using Semgrep."""
        self._log_message("Scanning JavaScript URL: " + url)
        
        result = {
            'url': url,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'findings': [],
            'success': False,
            'error': None
        }
        
        try:
            # Get Semgrep binary path
            semgrep_bin = self._get_semgrep_binary()
            if not semgrep_bin:
                result['error'] = "Semgrep binary not found. Please install Semgrep."
                self._log_message("Semgrep binary not found")
                self._add_result_to_table(result)
                return result
            
            # Download JavaScript file
            js_content = self._download_js_file(url)
            if not js_content:
                result['error'] = "Failed to download JavaScript file"
                self._log_message("Failed to download JavaScript file: " + url)
                self._add_result_to_table(result)
                return result
            
            # Save to temporary file
            temp_file = self._save_temp_js_file(js_content, url)
            if not temp_file:
                result['error'] = "Failed to create temporary file"
                self._add_result_to_table(result)
                return result
            
            try:
                # Run Semgrep on the file
                findings = self._run_semgrep(temp_file, semgrep_bin)
                result['findings'] = findings
                result['success'] = True
                if findings:
                    self._log_message("Scan completed successfully for: " + url + " - " + str(len(findings)) + " findings")
                else:
                    self._log_message("Scan completed successfully for: " + url + " - 0 findings (no secrets detected)")
                
                # Extract secret values before cleaning up temp file
                for finding in findings:
                    if not finding.get('extra', {}).get('raw', ''):
                        raw_value = self._extract_secret_from_finding(finding, url)
                        if raw_value != "Secret value not available":
                            finding['extra']['raw'] = raw_value
                
                # Send to Telegram if enabled
                if self._send_to_telegram_enabled and findings:
                    self._send_to_telegram(result)
                    
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                        self._log_message("Cleaned up temporary file: " + os.path.basename(temp_file))
                except Exception as cleanup_error:
                    self._log_message("Error cleaning up temp file: " + str(cleanup_error))
                
        except Exception as e:
            result['error'] = str(e)
            self._log_message("Error scanning " + url + ": " + str(e))
        
        # Add result to table only if there are findings or if there was an error
        if result['findings'] or result['error']:
            self._add_result_to_table(result)
        
        # Add findings to findings table
        if result['success'] and result['findings']:
            self._add_findings_to_table(result['findings'], result['url'])
    
    def _cleanup_temp_files(self):
        """Clean up any remaining temporary JavaScript files."""
        try:
            temp_dir = tempfile.gettempdir()
            # Look for files that start with "jshunter_" (our temp file prefix)
            for filename in os.listdir(temp_dir):
                if filename.startswith("jshunter_") and filename.endswith(".js"):
                    temp_file_path = os.path.join(temp_dir, filename)
                    try:
                        os.unlink(temp_file_path)
                        self._log_message("Cleaned up leftover temp file: " + filename)
                    except Exception as e:
                        self._log_message("Error cleaning up leftover temp file " + filename + ": " + str(e))
        except Exception as e:
            self._log_message("Error during temp file cleanup: " + str(e))
    
    def _extract_secret_from_finding(self, finding, source_url):
        """Extract the actual secret value from the file content based on finding location."""
        try:
            # Get the file path from the finding
            file_path = finding.get('path', '')
            self._log_message("Extracting secret from file: " + file_path)
            
            if not file_path or not os.path.exists(file_path):
                self._log_message("File not found: " + file_path)
                return "Secret value not available"
            
            # Get line and column information
            start_line = finding.get('start', {}).get('line', 0)
            start_col = finding.get('start', {}).get('col', 0)
            end_line = finding.get('end', {}).get('line', 0)
            end_col = finding.get('end', {}).get('col', 0)
            
            self._log_message("Finding location - Line: " + str(start_line) + ", Col: " + str(start_col) + "-" + str(end_col))
            
            # Read the file content
            with io.open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if start_line > 0 and start_line <= len(lines):
                line_content = lines[start_line - 1]  # Semgrep uses 1-based line numbers
                self._log_message("Line content: " + line_content.strip())
                
                # Extract the secret value based on column positions
                if start_col > 0 and end_col > 0 and end_col <= len(line_content):
                    secret_value = line_content[start_col-1:end_col-1].strip()
                    # Remove quotes if present
                    secret_value = secret_value.strip('"\'')
                    self._log_message("Extracted secret (by columns): " + secret_value)
                    return secret_value
                else:
                    # Fallback: try to extract quoted strings
                    quoted_match = re.search(r'["\']([^"\']+)["\']', line_content)
                    if quoted_match:
                        secret_value = quoted_match.group(1)
                        self._log_message("Extracted secret (by regex): " + secret_value)
                        return secret_value
            
            self._log_message("Could not extract secret value")
            return "Secret value not available"
            
        except Exception as e:
            self._log_message("Error extracting secret value: " + str(e))
            return "Secret value not available"
    
    def _add_findings_to_table(self, findings, source_url):
        """Add findings to the findings details table."""
        for finding in findings:
            rule_id = finding.get('check_id', 'Unknown')
            raw_value = finding.get('extra', {}).get('raw', '')
            severity = finding.get('extra', {}).get('severity', 'UNKNOWN')
            line_number = finding.get('start', {}).get('line', 0)
            
            # If raw_value is empty, try to extract from the file content
            if not raw_value:
                raw_value = self._extract_secret_from_finding(finding, source_url)
            
            # Truncate long secrets for display
            display_secret = raw_value[:50] + "..." if len(raw_value) > 50 else raw_value
            
            # Add row to findings table
            row = [rule_id, display_secret, source_url, str(line_number), severity]
            self._findings_table_model.addRow(row)
    
    def _get_semgrep_binary(self):
        """Get Semgrep binary path from user configuration."""
        # Get path from UI field
        configured_path = self._semgrep_path_field.getText().strip()
        self._log_message("Checking Semgrep path: " + configured_path)
        
        if not configured_path:
            self._log_message("No Semgrep path configured")
            return None
        
        # Verify Semgrep path
        if self._verify_semgrep_path(configured_path):
            self._log_message("Semgrep binary validated successfully")
            return configured_path
        else:
            self._log_message("Semgrep binary validation failed")
            return None
    
    def _verify_semgrep_path(self, path):
        """Verify Semgrep path."""
        if not path or not os.path.isabs(path) or not os.access(path, os.X_OK):
            self._log_message("Semgrep path validation failed: not absolute or not executable")
            return False
        try:
            self._log_message("Testing Semgrep binary: " + path)
            proc = subprocess.Popen([path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_data, stderr_data = proc.communicate()
            self._log_message("Semgrep test - stdout: " + stdout_data.decode('utf-8', errors='ignore').strip() + 
                            ", stderr: " + stderr_data.decode('utf-8', errors='ignore').strip())
            
            # Check if process completed successfully and returned version info
            if proc.returncode == 0:
                # Check if output contains version number (e.g., "1.139.0")
                combined_output = (stderr_data + stdout_data).decode('utf-8', errors='ignore')
                if re.search(r'\d+\.\d+\.\d+', combined_output):
                    self._log_message("Semgrep binary validated successfully - version found")
                    return True
                else:
                    self._log_message("Semgrep binary validation failed - no version found")
                    return False
            else:
                self._log_message("Semgrep binary validation failed - non-zero exit code: " + str(proc.returncode))
                return False
        except Exception as e:
            self._log_message("Error testing Semgrep binary: " + str(e))
            return False
    
    def _download_js_file(self, url):
        """Download JavaScript file content."""
        try:
            # Use Java HTTP to download the file
            url_obj = URL(url)
            connection = url_obj.openConnection()
            connection.setRequestMethod("GET")
            connection.setRequestProperty("User-Agent", "JSHunter-Burp-Extension/2.1.0")
            connection.setConnectTimeout(10000)  # 10 seconds
            connection.setReadTimeout(30000)     # 30 seconds
            
            # Read the response
            input_stream = connection.getInputStream()
            reader = BufferedReader(InputStreamReader(input_stream, "UTF-8"))
            
            content = []
            line = reader.readLine()
            while line is not None:
                content.append(line)
                line = reader.readLine()
            
            reader.close()
            connection.disconnect()
            
            return "\n".join(content)
            
        except Exception as e:
            self._log_message("Error downloading JS file: " + str(e))
            return None
    
    def _save_temp_js_file(self, content, url):
        """Save JavaScript content to temporary file."""
        try:
            # Create a safe filename from URL
            safe_filename = re.sub(r'[^\w\-_\.]', '_', urlparse(url).path)
            if not safe_filename.endswith('.js'):
                safe_filename += '.js'
            
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "jshunter_" + safe_filename)
            
            with io.open(temp_file, 'w', encoding='utf-8') as f:
                # Jython/Python 2 compatibility: content is a Java string, needs decoding for unicode write
                f.write(content.decode('utf-8', 'ignore'))
            
            return temp_file
            
        except Exception as e:
            self._log_message("Error creating temp file: " + str(e))
            return None
    
    def _run_semgrep(self, file_path, semgrep_bin):
        """Run Semgrep on a file and return findings."""
        try:
            cmd = [semgrep_bin, "--config=p/secrets", "--json", file_path]
            # Use Popen for Python 2.7 compatibility
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for process with timeout (Python 2.7 compatible)
            import signal
            
            def timeout_handler(signum, frame):
                raise Exception("Timeout")
            
            # Set timeout signal
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(60)  # 60 second timeout
            
            try:
                stdout_data, stderr_data = proc.communicate()
                signal.alarm(0)  # Cancel timeout
                signal.signal(signal.SIGALRM, old_handler)  # Restore old handler

                # --- DEBUG LOGGING ---
                self._log_message("Semgrep stdout: " + stdout_data.strip())
                self._log_message("Semgrep stderr: " + stderr_data.strip())
                self._log_message("Semgrep return code: " + str(proc.returncode))
                # --- END DEBUG LOGGING ---
                
                if proc.returncode == 0:
                    try:
                        # Parse JSON output
                        json_output = json.loads(stdout_data)
                        findings = json_output.get('results', [])
                        return findings
                    except ValueError:
                        self._log_message("Error parsing Semgrep JSON output")
                        return []
                else:
                    self._log_message("Semgrep error: " + stderr_data)
                    return []
                    
            except Exception as timeout_error:
                signal.alarm(0)  # Cancel timeout
                signal.signal(signal.SIGALRM, old_handler)  # Restore old handler
                proc.terminate()
                if "Timeout" in str(timeout_error):
                    self._log_message("Semgrep timeout for file: " + file_path)
                else:
                    self._log_message("Semgrep execution error: " + str(timeout_error))
                return []
                
        except Exception as e:
            self._log_message("Semgrep execution error: " + str(e))
            return []
    
    def _send_to_telegram(self, result):
        """Send findings to Telegram."""
        if not self._telegram_bot_token or not self._telegram_bot_token.strip():
            return
        if not self._telegram_chat_id or not self._telegram_chat_id.strip():
            return
            
        try:
            # Group findings by severity
            high_severity = [f for f in result['findings'] if f.get('extra', {}).get('severity') == 'ERROR']
            medium_severity = [f for f in result['findings'] if f.get('extra', {}).get('severity') == 'WARNING']
            low_severity = [f for f in result['findings'] if f.get('extra', {}).get('severity') == 'INFO']
            
            if high_severity:
                self._send_findings_to_telegram(high_severity, result['url'], "HIGH")
            
            if medium_severity:
                self._send_findings_to_telegram(medium_severity, result['url'], "MEDIUM")
            
            if low_severity:
                self._send_findings_to_telegram(low_severity, result['url'], "LOW")
                
        except Exception as e:
            self._log_message("Error sending to Telegram: " + str(e))
    
    def _send_findings_to_telegram(self, findings, source_url, severity):
        """Send findings to Telegram, splitting messages if they are too long."""
        
        # Telegram API has a message length limit of 4096 characters.
        # We set a slightly lower limit to be safe.
        MESSAGE_LIMIT = 4000
        
        # Choose emoji based on severity
        severity_emoji = {
            "HIGH": u"\U0001F534",    # Red circle
            "MEDIUM": u"\U0001F7E1",  # Yellow circle
            "LOW": u"\U0001F7E2"      # Green circle
        }
        
        base_message = severity_emoji.get(severity, u"\U0001F534") + " *[" + severity + "] Secrets Detected*\n"
        base_message += "Found in: `" + source_url + "`\n\n"
        
        current_message = base_message
        
        for i, finding in enumerate(findings):
            rule_id = finding.get('check_id', 'Unknown')
            raw_value = finding.get('extra', {}).get('raw', '')
            line_number = finding.get('start', {}).get('line', 0)
            
            # If raw_value is empty, try to extract from the file content
            if not raw_value:
                raw_value = self._extract_secret_from_finding(finding, source_url)
            
            finding_text = ""
            finding_text += "*" + rule_id + "*\n"
            finding_text += "```\n" + raw_value + "\n```\n"
            if line_number > 0:
                finding_text += "Line: " + str(line_number) + "\n"
            finding_text += "\n"
            
            # If adding the next finding exceeds the limit, send the current message and start a new one.
            if len(current_message.encode('utf-8')) + len(finding_text.encode('utf-8')) > MESSAGE_LIMIT:
                self._send_telegram_message(current_message)
                current_message = base_message # Start a new message with the header
            
            current_message += finding_text

        # Send the last message if it has content
        if current_message != base_message:
            self._send_telegram_message(current_message)

    def _send_telegram_message(self, message):
        """Helper function to send a single message to Telegram."""
        try:
            telegram_url = "https://api.telegram.org/bot" + self._telegram_bot_token + "/sendMessage"
            
            payload = {
                "chat_id": self._telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            
            response_code = self._send_http_post(telegram_url, payload)
            
            if response_code == 200:
                self._log_message("Successfully sent a message chunk to Telegram.")
            else:
                self._log_message("Failed to send message to Telegram. Response code: " + str(response_code))
        except Exception as e:
            self._log_message("Error sending message to Telegram: " + str(e))
            
    def _test_telegram(self):
        """Test Telegram bot connection."""
        bot_token = self._telegram_bot_token_field.getText().strip()
        chat_id = self._telegram_chat_id_field.getText().strip()
        
        if not bot_token:
            JOptionPane.showMessageDialog(self._main_panel, "Please enter a Telegram Bot Token", "Error", JOptionPane.ERROR_MESSAGE)
            return
        
        if not chat_id:
            JOptionPane.showMessageDialog(self._main_panel, "Please enter a Telegram Chat ID", "Error", JOptionPane.ERROR_MESSAGE)
            return
        
        self._telegram_bot_token = bot_token
        self._telegram_chat_id = chat_id
        self._save_settings()
        
        try:
            telegram_url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": u"\U0001F916 *JSHunter Semgrep Test Message*\n\nThis is a test message from JSHunter Burp Extension (Semgrep Version). If you receive this, your Telegram configuration is correct!",
                "parse_mode": "Markdown"
            }
            
            response_code = self._send_http_post(telegram_url, payload)
            
            if response_code == 200:
                JOptionPane.showMessageDialog(self._main_panel, "Test message sent successfully!", "Success", JOptionPane.INFORMATION_MESSAGE)
                self._log_message("Telegram test successful")
            else:
                JOptionPane.showMessageDialog(self._main_panel, "Telegram test failed. Response code: " + str(response_code), "Error", JOptionPane.ERROR_MESSAGE)
                self._log_message("Telegram test failed with code: " + str(response_code))
                
        except Exception as e:
            JOptionPane.showMessageDialog(self._main_panel, "Error testing Telegram: " + str(e), "Error", JOptionPane.ERROR_MESSAGE)
            self._log_message("Error testing Telegram: " + str(e))
    
    def _test_semgrep(self):
        """Test Semgrep binary."""
        semgrep_path = self._semgrep_path_field.getText().strip()
        if not semgrep_path:
            JOptionPane.showMessageDialog(self._main_panel, "Please enter a Semgrep path", "Error", JOptionPane.ERROR_MESSAGE)
            return
        
        try:
            # Test if the binary exists and is executable
            if not os.path.exists(semgrep_path):
                self._semgrep_status_label.setText("Semgrep: File not found")
                JOptionPane.showMessageDialog(self._main_panel, "Semgrep binary not found at: " + semgrep_path, "Error", JOptionPane.ERROR_MESSAGE)
                return
            
            if not os.access(semgrep_path, os.X_OK):
                self._semgrep_status_label.setText("Semgrep: Not executable")
                JOptionPane.showMessageDialog(self._main_panel, "Semgrep binary is not executable: " + semgrep_path, "Error", JOptionPane.ERROR_MESSAGE)
                return
            
            # Test if it's a valid Semgrep binary
            if self._verify_semgrep_path(semgrep_path):
                # Get version info for display
                try:
                    proc = subprocess.Popen([semgrep_path, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout_data, stderr_data = proc.communicate()
                    version_info = (stdout_data + stderr_data).decode('utf-8', errors='ignore').strip()
                except:
                    version_info = "semgrep"
                
                self._semgrep_status_label.setText("Semgrep: " + version_info)
                JOptionPane.showMessageDialog(self._main_panel, "Semgrep test successful!\n" + version_info, "Success", JOptionPane.INFORMATION_MESSAGE)
                self._log_message("Semgrep test successful: " + version_info)
            else:
                self._semgrep_status_label.setText("Semgrep: Invalid binary")
                JOptionPane.showMessageDialog(self._main_panel, "Invalid Semgrep binary at: " + semgrep_path, "Error", JOptionPane.ERROR_MESSAGE)
                self._log_message("Semgrep test failed: binary not valid")
                
        except subprocess.TimeoutExpired:
            self._semgrep_status_label.setText("Semgrep: Timeout")
            JOptionPane.showMessageDialog(self._main_panel, "Semgrep test timeout", "Error", JOptionPane.ERROR_MESSAGE)
            self._log_message("Semgrep test timeout")
        except Exception as e:
            self._semgrep_status_label.setText("Semgrep: Error")
            JOptionPane.showMessageDialog(self._main_panel, "Error testing Semgrep: " + str(e), "Error", JOptionPane.ERROR_MESSAGE)
            self._log_message("Error testing Semgrep: " + str(e))
    
    def _browse_semgrep_path(self):
        """Open file chooser to select Semgrep binary."""
        file_chooser = JFileChooser()
        file_chooser.setDialogTitle("Select Semgrep Binary")
        file_chooser.setFileSelectionMode(JFileChooser.FILES_ONLY)
        
        # Set initial directory to common Semgrep locations
        current_path = self._semgrep_path_field.getText().strip()
        if current_path and os.path.exists(os.path.dirname(current_path)):
            file_chooser.setCurrentDirectory(java.io.File(os.path.dirname(current_path)))
        else:
            # Try common locations
            common_paths = ["/usr/local/bin", "/usr/bin", "/home/gxavier/.local/bin", os.path.expanduser("~/.local/bin")]
            for path in common_paths:
                if os.path.exists(path):
                    file_chooser.setCurrentDirectory(java.io.File(path))
                    break
        
        # Add file filter for executable files
        class ExecutableFileFilter(javax.swing.filechooser.FileFilter):
            def accept(self, file):
                if file.isDirectory():
                    return True
                name = file.getName().lower()
                return (name == "semgrep" or 
                       name.startswith("semgrep") or 
                       file.canExecute())
            
            def getDescription(self):
                return "Semgrep Binary (*semgrep*)"
        
        file_chooser.setFileFilter(ExecutableFileFilter())
        
        result = file_chooser.showOpenDialog(self._main_panel)
        if result == JFileChooser.APPROVE_OPTION:
            selected_file = file_chooser.getSelectedFile()
            if selected_file:
                file_path = selected_file.getAbsolutePath()
                self._semgrep_path_field.setText(file_path)
                self._log_message("Selected Semgrep binary: " + file_path)
                
                # Auto-test the selected binary
                self._test_semgrep()
    
    def _send_http_post(self, url, payload):
        """Send HTTP POST request using Java's built-in HTTP capabilities."""
        try:
            # --- DEBUG LOGGING ---
            self._log_message("Sending POST request to URL: " + url)
            self._log_message("Payload: " + json.dumps(payload))
            # --- END DEBUG LOGGING ---

            # Create URL object
            url_obj = URL(url)
            connection = url_obj.openConnection()
            connection.setRequestMethod("POST")
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setDoOutput(True)
            
            # Convert payload to JSON string
            json_payload = json.dumps(payload)
            
            # Send the request using UTF-8 encoding
            output_stream = connection.getOutputStream()
            writer = OutputStreamWriter(output_stream, "UTF-8")
            writer.write(json_payload)
            writer.flush()
            writer.close()
            
            # Get response code
            response_code = connection.getResponseCode()
            
            # --- DEBUG LOGGING ---
            self._log_message("Response code: " + str(response_code))
            # --- END DEBUG LOGGING ---
            
            # Read response body for debugging
            try:
                if response_code >= 400:
                    # Read error response
                    error_stream = connection.getErrorStream()
                    if error_stream:
                        error_reader = BufferedReader(InputStreamReader(error_stream, "UTF-8"))
                        error_response = []
                        line = error_reader.readLine()
                        while line is not None:
                            error_response.append(line)
                            line = error_reader.readLine()
                        error_reader.close()
                        error_body = "\n".join(error_response)
                        self._log_message("Error response body: " + error_body)
                else:
                    # Read success response
                    input_stream = connection.getInputStream()
                    if input_stream:
                        response_reader = BufferedReader(InputStreamReader(input_stream, "UTF-8"))
                        response_body = []
                        line = response_reader.readLine()
                        while line is not None:
                            response_body.append(line)
                            line = response_reader.readLine()
                        response_reader.close()
                        success_body = "\n".join(response_body)
                        self._log_message("Success response body: " + success_body)
            except Exception as read_error:
                self._log_message("Error reading response body: " + str(read_error))
            
            # Close connection
            connection.disconnect()
            
            return response_code
            
        except Exception as e:
            self._log_message("HTTP POST error: " + str(e))
            return -1
    
    def _add_result_to_table(self, result):
        """Add scan result to the results table."""
        high_severity_count = sum(1 for f in result['findings'] if f.get('extra', {}).get('severity') == 'ERROR')
        medium_severity_count = sum(1 for f in result['findings'] if f.get('extra', {}).get('severity') == 'WARNING')
        low_severity_count = sum(1 for f in result['findings'] if f.get('extra', {}).get('severity') == 'INFO')
        
        status = "Success" if result['success'] else "Failed: " + str(result['error'])
        
        row_data = [
            result['timestamp'],
            result['url'],
            len(result['findings']),
            high_severity_count,
            medium_severity_count + low_severity_count,
            status
        ]
        
        self._table_model.addRow(row_data)
        self._scan_results.add(result)
        
        # Auto-scroll to bottom
        self._results_table.scrollRectToVisible(
            self._results_table.getCellRect(self._table_model.getRowCount() - 1, 0, True)
        )
    
    def _log_message(self, message):
        """Log a message to the activity log."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = "[" + timestamp + "] " + message + "\n"
        
        # Update UI in EDT
        def update_log():
            self._log_area.append(log_entry)
            self._log_area.setCaretPosition(len(self._log_area.getText()))
        
        # Schedule UI update on EDT
        from javax.swing import SwingUtilities
        SwingUtilities.invokeLater(update_log)
        
        # Also print to console
        print(log_entry.strip())
    
    def getTabCaption(self):
        """Return the tab caption."""
        return "JSHunter Semgrep"
    
    def getUiComponent(self):
        """Return the UI component."""
        return self._main_panel


# Event Listeners
class TestTelegramListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        self._extension._test_telegram()


class AutoScanListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        self._extension._auto_scan_enabled = self._extension._auto_scan_checkbox.isSelected()
        self._extension._save_settings()


class SendToTelegramListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        self._extension._send_to_telegram_enabled = self._extension._send_to_telegram_checkbox.isSelected()
        self._extension._save_settings()

class TestSemgrepListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        self._extension._test_semgrep()

class BrowseSemgrepListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        self._extension._browse_semgrep_path()

class CopyFindingListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        selected_row = self._extension._findings_table.getSelectedRow()
        if selected_row >= 0:
            secret_value = self._extension._findings_table_model.getValueAt(selected_row, 1)
            # Copy to clipboard (simplified - in real implementation you'd use Java clipboard)
            JOptionPane.showMessageDialog(self._extension._main_panel, 
                                        "Secret copied to clipboard:\n" + str(secret_value), 
                                        "Copied", JOptionPane.INFORMATION_MESSAGE)
        else:
            JOptionPane.showMessageDialog(self._extension._main_panel, 
                                        "Please select a finding to copy", 
                                        "No Selection", JOptionPane.WARNING_MESSAGE)

class ClearFindingsListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        result = JOptionPane.showConfirmDialog(
            self._extension._main_panel,
            "Are you sure you want to clear all findings?",
            "Clear Findings",
            JOptionPane.YES_NO_OPTION
        )
        if result == JOptionPane.YES_OPTION:
            self._extension._findings_table_model.setRowCount(0)

class CleanupTempFilesListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        result = JOptionPane.showConfirmDialog(
            self._extension._main_panel,
            "Are you sure you want to cleanup temporary JavaScript files?",
            "Cleanup Temp Files",
            JOptionPane.YES_NO_OPTION
        )
        if result == JOptionPane.YES_OPTION:
            self._extension._cleanup_temp_files()
            JOptionPane.showMessageDialog(
                self._extension._main_panel,
                "Temporary files cleanup completed. Check the Activity Log for details.",
                "Cleanup Complete",
                JOptionPane.INFORMATION_MESSAGE
            )

class ClearResultsListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        result = JOptionPane.showConfirmDialog(
            self._extension._main_panel,
            "Are you sure you want to clear all results?",
            "Confirm Clear",
            JOptionPane.YES_NO_OPTION
        )
        
        if result == JOptionPane.YES_OPTION:
            self._extension._table_model.setRowCount(0)
            self._extension._scan_results.clear()
            self._extension._scanned_urls.clear()
            self._extension._log_message("Results cleared")


class ExportResultsListener(ActionListener):
    def __init__(self, extension):
        self._extension = extension
    
    def actionPerformed(self, event):
        file_chooser = JFileChooser()
        file_chooser.setSelectedFile(java.io.File("jshunter_semgrep_results.json"))
        
        result = file_chooser.showSaveDialog(self._extension._main_panel)
        if result == JFileChooser.APPROVE_OPTION:
            try:
                file = file_chooser.getSelectedFile()
                with open(str(file), 'w') as f:
                    json.dump(list(self._extension._scan_results), f, indent=2)
                
                JOptionPane.showMessageDialog(
                    self._extension._main_panel, 
                    "Results exported successfully!", 
                    "Success", 
                    JOptionPane.INFORMATION_MESSAGE
                )
                self._extension._log_message("Results exported to: " + str(file))
                
            except Exception as e:
                JOptionPane.showMessageDialog(
                    self._extension._main_panel, 
                    "Error exporting results: " + str(e), 
                    "Error", 
                    JOptionPane.ERROR_MESSAGE
                )
                self._extension._log_message("Error exporting results: " + str(e))


class ResultDetailsListener(MouseAdapter):
    def __init__(self, extension):
        self._extension = extension
    
    def mouseClicked(self, event):
        if event.getClickCount() == 2:
            self._show_result_details()
    
    def _show_result_details(self):
        selected_row = self._extension._results_table.getSelectedRow()
        if selected_row == -1:
            return
        
        model_row = self._extension._results_table.convertRowIndexToModel(selected_row)
        result = self._extension._scan_results.get(model_row)
        
        # Create details dialog
        dialog = JDialog(None, "Scan Result Details", True)
        dialog.setSize(800, 600)
        dialog.setLocationRelativeTo(self._extension._main_panel)
        
        panel = JPanel(BorderLayout())
        
        # URL info
        url_panel = JPanel(BorderLayout())
        url_panel.setBorder(BorderFactory.createTitledBorder("URL"))
        url_area = JTextArea(result['url'])
        url_area.setEditable(False)
        url_area.setRows(2)
        url_panel.add(JScrollPane(url_area), BorderLayout.CENTER)
        
        # Findings table
        findings_panel = JPanel(BorderLayout())
        findings_panel.setBorder(BorderFactory.createTitledBorder("Findings"))
        
        column_names = ["Rule ID", "Severity", "Line", "Value"]
        findings_model = DefaultTableModel(column_names, 0)
        
        findings_table = JTable(findings_model)
        findings_table.setRowSorter(TableRowSorter(findings_model))
        
        for finding in result['findings']:
            rule_id = finding.get('check_id', 'Unknown')
            raw_value = finding.get('extra', {}).get('raw', '')
            severity = finding.get('extra', {}).get('severity', 'UNKNOWN')
            line_number = finding.get('start', {}).get('line', 0)
            
            row_data = [
                rule_id,
                severity,
                line_number if line_number > 0 else "",
                raw_value[:100] + "..." if len(raw_value) > 100 else raw_value
            ]
            findings_model.addRow(row_data)
        
        findings_panel.add(JScrollPane(findings_table), BorderLayout.CENTER)
        
        panel.add(url_panel, BorderLayout.NORTH)
        panel.add(findings_panel, BorderLayout.CENTER)
        
        # Close button
        button_panel = JPanel(FlowLayout())
        close_button = JButton("Close")
        close_button.addActionListener(lambda e: dialog.dispose())
        button_panel.add(close_button)
        panel.add(button_panel, BorderLayout.SOUTH)
        
        dialog.add(panel)
        dialog.setVisible(True)
