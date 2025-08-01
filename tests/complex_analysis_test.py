
import re
import hashlib
from typing import List, Optional

class DataProcessor:
    """A sample class for demonstrating code analysis capabilities."""
    
    def __init__(self, data_source: str):
        self.data_source = data_source
        self.processed_items = []
        self.error_count = 0
    
    def process_data(self, data: List[str]) -> Optional[List[str]]:
        """Process a list of data items with validation."""
        if not data:
            return None
            
        results = []
        for item in data:
            try:
                if self._validate_item(item):
                    processed = self._transform_item(item)
                    results.append(processed)
                    self.processed_items.append(item)
                else:
                    self.error_count += 1
                    print(f"Invalid item: {item}")
            except Exception as e:
                self.error_count += 1
                print(f"Processing error: {e}")
        
        return results if results else None
    
    def _validate_item(self, item: str) -> bool:
        """Validate data item format."""
        # Simple validation - must be alphanumeric and at least 3 chars
        return bool(re.match(r'^[a-zA-Z0-9]{3,}$', item))
    
    def _transform_item(self, item: str) -> str:
        """Transform item by adding hash."""
        hash_obj = hashlib.md5(item.encode())
        return f"{item}_{hash_obj.hexdigest()[:8]}"
    
    def get_stats(self) -> dict:
        """Get processing statistics."""
        total_processed = len(self.processed_items)
        return {
            "total_processed": total_processed,
            "error_count": self.error_count,
            "success_rate": (total_processed / (total_processed + self.error_count)) * 100 
                           if (total_processed + self.error_count) > 0 else 0
        }

def main_function():
    """Main processing function."""
    processor = DataProcessor("test_source")
    sample_data = ["item1", "item2", "x", "valid_item_123", ""]
    
    results = processor.process_data(sample_data)
    stats = processor.get_stats()
    
    print(f"Processing complete. Results: {len(results or [])}")
    print(f"Stats: {stats}")

if __name__ == "__main__":
    main_function()
