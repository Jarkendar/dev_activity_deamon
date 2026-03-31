"""Module for categorizing activities based on regex rules from YAML."""
import re
import yaml
from typing import Optional, Dict, List
from pathlib import Path


class Categorizer:
    """Activity categorizer based on regex rules."""
    
    def __init__(self, config_path: str = "config/categories.yaml"):
        """
        Initialize categorizer.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.rules: List[Dict] = []
        self._load_rules()
    
    def _load_rules(self):
        """Load categorization rules from YAML file."""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            print(f"Configuration file {self.config_path} does not exist. Using empty rules.")
            self.rules = []
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.rules = config.get('categories', [])
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.rules = []
    
    def categorize(self, window_title: str, process_name: str) -> Optional[str]:
        """
        Categorize activity based on window title and process name.
        
        Args:
            window_title: Window title
            process_name: Process name
        
        Returns:
            str: Category name or None if no match found
        """
        for rule in self.rules:
            category = rule.get('name')
            patterns = rule.get('patterns', [])
            
            for pattern_rule in patterns:
                field = pattern_rule.get('field')
                regex = pattern_rule.get('regex')
                
                if not field or not regex:
                    continue
                
                # Select field to check
                text_to_match = ""
                if field == 'window_title':
                    text_to_match = window_title
                elif field == 'process_name':
                    text_to_match = process_name
                elif field == 'both':
                    text_to_match = f"{window_title} {process_name}"
                
                # Check regex match
                try:
                    if re.search(regex, text_to_match, re.IGNORECASE):
                        return category
                except re.error:
                    print(f"Invalid regex: {regex}")
                    continue
        
        return None
    
    def reload(self):
        """Reload rules from configuration file."""
        self._load_rules()
