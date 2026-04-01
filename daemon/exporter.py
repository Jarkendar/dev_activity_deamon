"""Module for exporting session data to external services."""
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    import yaml
except ImportError:
    # Fallback if PyYAML is not installed
    yaml = None

from daemon.db import Database


def _load_config() -> dict:
    """
    Load configuration from config/config.yaml.
    
    Returns:
        dict: Configuration dictionary
    """
    config_path = Path("config/config.yaml")
    
    if not config_path.exists():
        return {}
    
    if yaml is None:
        # Simple fallback parser for single key-value
        with open(config_path, 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('n8n_webhook_url:'):
                    url = line.split(':', 1)[1].strip().strip('"\'')
                    return {'n8n_webhook_url': url}
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


def run():
    """
    Export unsynced sessions to configured webhook.
    
    Loads webhook URL from config, fetches unsynced sessions,
    builds JSON payload with sessions and summary, sends HTTP POST,
    and marks sessions as synced on success.
    """
    # Load configuration
    config = _load_config()
    webhook_url = config.get('n8n_webhook_url', '').strip()
    
    # Skip silently if no webhook URL configured
    if not webhook_url:
        return
    
    # Get unsynced sessions
    with Database() as db:
        sessions = db.get_unsynced_sessions()
        
        if not sessions:
            return
        
        # Build payload
        session_list = []
        category_totals = {}
        total_active_seconds = 0
        
        for session in sessions:
            session_dict = dict(session)
            session_list.append(session_dict)
            
            # Calculate summary
            duration = session_dict.get('duration_seconds', 0) or 0
            is_idle = session_dict.get('is_idle', 0)
            
            if not is_idle:
                total_active_seconds += duration
                category = session_dict.get('category') or 'uncategorized'
                category_totals[category] = category_totals.get(category, 0) + duration
        
        payload = {
            'sessions': session_list,
            'summary': {
                'total_active_seconds': total_active_seconds,
                'category_breakdown': category_totals,
                'export_timestamp': datetime.now().isoformat()
            }
        }
        
        # Send HTTP POST using urllib
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status == 200:
                    # Mark sessions as synced
                    session_ids = [s['id'] for s in session_list]
                    db.mark_synced(session_ids)
                    db.delete_old_synced()
                    print(f"Successfully exported {len(session_ids)} sessions")
                else:
                    print(f"Export failed with status {response.status}")
        
        except urllib.error.HTTPError as e:
            print(f"Export failed: HTTP {e.code} - {e.reason}")
        except urllib.error.URLError as e:
            print(f"Export failed: {e.reason}")
        except Exception as e:
            print(f"Export failed: {e}")
