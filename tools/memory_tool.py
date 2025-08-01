#!/usr/bin/env python3
"""
Enhanced Memory Tool - Intelligent persistent memory with semantic connections
Integrates with the Memory Interconnection Engine for advanced capabilities
"""

import json
import logging
from pathlib import Path
from typing import Callable, Dict, Any, List, Optional
import threading
import time
from datetime import datetime, timedelta

# Import the interconnection engine
try:
    from tools.memory_interconnect import MemoryInterconnectionEngine as RealMemoryInterconnectionEngine
    INTERCONNECT_AVAILABLE = True
except ImportError:
    INTERCONNECT_AVAILABLE = False
    class RealMemoryInterconnectionEngine:
        def __init__(self, *args, **kwargs):
            pass

        def analyze_memory_entry(self, key, value, source):
            raise NotImplementedError

        def intelligent_search(self, query: str, max_results: int = 5):
            raise NotImplementedError

        def get_memory_insights(self):
            raise NotImplementedError

class EnhancedMemoryTool:
    """Enhanced memory with semantic intelligence and cross-system connections"""
    
    def __init__(self, storage_file: str = "data/memory_store.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(exist_ok=True)
        self._lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Initialize interconnection engine
        if INTERCONNECT_AVAILABLE:
            self.intelligence = RealMemoryInterconnectionEngine(str(self.storage_file.parent))
        else:
            self.intelligence = None
            self.logger.warning("Memory interconnection engine not available")
        
        # Initialize storage
        if not self.storage_file.exists():
            self._save_data({})
            
        # Memory categories for better organization
        self.categories = {
            "insights": "Important discoveries and learnings",
            "decisions": "Key decisions and their rationale", 
            "patterns": "Recurring patterns and observations",
            "context": "Project and session context",
            "solutions": "Problem solutions and fixes",
            "references": "Important references and links",
            "goals": "Objectives and progress tracking",
            "technical": "Technical details and configurations"
        }
        
        self.logger.info(f"Enhanced memory tool initialized with storage: {self.storage_file}")
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from storage file with enhanced error handling"""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Ensure all entries have proper structure
            for key, entry in data.items():
                if not isinstance(entry, dict):
                    # Convert old format to new format
                    data[key] = {
                        'value': str(entry),
                        'timestamp': time.time(),
                        'created': time.time(),
                        'category': 'uncategorized',
                        'importance': 0.5,
                        'tags': [],
                        'access_count': 0,
                        'last_accessed': time.time()
                    }
                else:
                    # Ensure all required fields exist
                    entry.setdefault('category', 'uncategorized')
                    entry.setdefault('importance', 0.5)
                    entry.setdefault('tags', [])
                    entry.setdefault('access_count', 0)
                    entry.setdefault('last_accessed', entry.get('timestamp', time.time()))
            
            return data
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"Could not load memory data: {e}. Starting with empty storage.")
            return {}
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Save data to storage file with atomic write"""
        temp_file = self.storage_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            temp_file.replace(self.storage_file)
            
        except Exception as e:
            self.logger.error(f"Failed to save memory data: {e}")
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def store(self, key: str, value: str, category: str = "uncategorized",
              importance: float = 0.5, tags: Optional[List[str]] = None) -> str:
        """Store a key-value pair with enhanced metadata and intelligence"""
        with self._lock:
            data = self._load_data()
            current_time = time.time()
            
            # Validate inputs
            if not key or not value:
                return "Error: Both key and value are required"
            
            if category not in self.categories and category != "uncategorized":
                available_cats = ", ".join(self.categories.keys())
                return f"Warning: Unknown category '{category}'. Available: {available_cats}"
            
            importance = max(0.0, min(1.0, importance))  # Clamp to 0-1
            tags = tags or []
            
            # Create enhanced entry
            entry = {
                'value': value,
                'timestamp': current_time,
                'created': data.get(key, {}).get('created', current_time),
                'category': category,
                'importance': importance,
                'tags': tags,
                'access_count': data.get(key, {}).get('access_count', 0),
                'last_accessed': current_time,
                'version': data.get(key, {}).get('version', 0) + 1
            }
            
            # Add intelligence analysis if available
            if self.intelligence:
                try:
                    analysis = self.intelligence.analyze_memory_entry(key, value, "memory")
                    entry['concepts'] = analysis.get('concepts', [])
                    entry['ai_importance'] = analysis.get('importance', importance)
                    entry['related_memories'] = analysis.get('related_memories', [])
                except Exception as e:
                    self.logger.warning(f"Intelligence analysis failed for {key}: {e}")
            
            data[key] = entry
            self._save_data(data)
            
            self.logger.info(f"Enhanced store: '{key}' (category: {category}, importance: {importance})")
            
            # Format response with intelligence insights
            response = f"✅ Stored '{key}' in persistent memory"
            if entry.get('concepts'):
                response += f"\n🧠 Detected concepts: {', '.join(entry['concepts'][:5])}"
            if entry.get('related_memories'):
                related_count = len(entry['related_memories'])
                response += f"\n🔗 Found {related_count} related memories"
            
            return response
    
    def retrieve(self, key: str, include_related: bool = False) -> str:
        """Retrieve a value with optional related memories"""
        with self._lock:
            data = self._load_data()
            
            if key not in data:
                # Try intelligent search as fallback
                if self.intelligence:
                    search_results = self.intelligence.intelligent_search(key, max_results=3)
                    if search_results:
                        suggestions = [result['memory_id'].split(':', 1)[1] for result in search_results]
                        return f"Key '{key}' not found. Did you mean: {', '.join(suggestions)}?"
                
                return f"Key '{key}' not found in memory"
            
            entry = data[key]
            
            # Update access tracking
            entry['access_count'] = entry.get('access_count', 0) + 1
            entry['last_accessed'] = time.time()
            self._save_data(data)
            
            # Build response
            value = entry.get('value', entry) if isinstance(entry, dict) else str(entry)
            response = str(value)
            
            # Add metadata if entry is enhanced
            if isinstance(entry, dict) and include_related:
                metadata = []
                
                if entry.get('category') != 'uncategorized':
                    metadata.append(f"Category: {entry['category']}")
                
                if entry.get('importance', 0) > 0.7:
                    metadata.append(f"High importance ({entry['importance']:.1f})")
                
                if entry.get('tags'):
                    metadata.append(f"Tags: {', '.join(entry['tags'])}")
                
                if entry.get('concepts'):
                    metadata.append(f"Concepts: {', '.join(entry['concepts'][:3])}")
                
                if entry.get('related_memories'):
                    related_keys = [rel['memory_id'].split(':', 1)[1] for rel in entry['related_memories'][:3]]
                    metadata.append(f"Related: {', '.join(related_keys)}")
                
                if metadata:
                    response += f"\n\n📊 " + " | ".join(metadata)
            
            self.logger.info(f"Retrieved key '{key}' from memory")
            return response
    
    def intelligent_search(self, query: str, max_results: int = 5) -> str:
        """Search memories using intelligent semantic matching"""
        if not self.intelligence:
            # Fallback to simple text search
            return self._simple_search(query, max_results)
        
        try:
            results = self.intelligence.intelligent_search(query, max_results)
            
            if not results:
                return f"No memories found matching '{query}'"
            
            response = [f"🔍 Intelligent search results for '{query}':\n"]
            
            for i, result in enumerate(results, 1):
                memory_id = result['memory_id']
                key = memory_id.split(':', 1)[1] if ':' in memory_id else memory_id
                relevance = result['relevance_score']
                matched_concepts = result.get('matched_concepts', [])
                
                response.append(f"{i}. {key} (relevance: {relevance:.2f})")
                if matched_concepts:
                    response.append(f"   Matched concepts: {', '.join(matched_concepts[:3])}")
            
            return "\n".join(response)
            
        except Exception as e:
            self.logger.error(f"Intelligent search failed: {e}")
            return self._simple_search(query, max_results)
    
    def _simple_search(self, query: str, max_results: int = 5) -> str:
        """Fallback simple text search"""
        with self._lock:
            data = self._load_data()
            matches = []
            
            query_lower = query.lower()
            for key, entry in data.items():
                value = entry.get('value', str(entry)) if isinstance(entry, dict) else str(entry)
                
                if query_lower in key.lower() or query_lower in value.lower():
                    matches.append((key, value))
            
            if not matches:
                return f"No memories found matching '{query}'"
            
            response = [f"🔍 Search results for '{query}':\n"]
            for i, (key, value) in enumerate(matches[:max_results], 1):
                preview = value[:100] + "..." if len(value) > 100 else value
                response.append(f"{i}. {key}: {preview}")
            
            return "\n".join(response)
    
    def list_keys(self, prefix: Optional[str] = None, category: Optional[str] = None,
                  min_importance: float = 0.0, sort_by: str = "timestamp") -> str:
        """Enhanced key listing with filtering and sorting options"""
        with self._lock:
            data = self._load_data()
            
            # Filter keys
            filtered_keys = []
            for key, entry in data.items():
                # Apply prefix filter
                if prefix and not key.startswith(prefix):
                    continue
                
                # Apply category filter
                if category:
                    entry_category = entry.get('category', 'uncategorized') if isinstance(entry, dict) else 'uncategorized'
                    if entry_category != category:
                        continue
                
                # Apply importance filter
                if isinstance(entry, dict):
                    entry_importance = entry.get('importance', 0.5)
                    if entry_importance < min_importance:
                        continue
                
                filtered_keys.append((key, entry))
            
            if not filtered_keys:
                filter_desc = []
                if prefix:
                    filter_desc.append(f"prefix '{prefix}'")
                if category:
                    filter_desc.append(f"category '{category}'")
                if min_importance > 0:
                    filter_desc.append(f"importance >= {min_importance}")
                
                return f"No keys found" + (f" with {' and '.join(filter_desc)}" if filter_desc else "")
            
            # Sort keys
            if sort_by == "timestamp":
                filtered_keys.sort(key=lambda x: x[1].get('timestamp', 0) if isinstance(x[1], dict) else 0, reverse=True)
            elif sort_by == "importance":
                filtered_keys.sort(key=lambda x: x[1].get('importance', 0.5) if isinstance(x[1], dict) else 0.5, reverse=True)
            elif sort_by == "access":
                filtered_keys.sort(key=lambda x: x[1].get('access_count', 0) if isinstance(x[1], dict) else 0, reverse=True)
            elif sort_by == "alphabetical":
                filtered_keys.sort(key=lambda x: x[0])
            
            # Build response
            response = [f"📋 Memory keys ({len(filtered_keys)} total):"]
            
            for key, entry in filtered_keys:
                if isinstance(entry, dict):
                    category = entry.get('category', 'uncategorized')
                    importance = entry.get('importance', 0.5)
                    access_count = entry.get('access_count', 0)
                    
                    # Format key with metadata
                    key_line = f"  • {key}"
                    metadata = []
                    
                    if category != 'uncategorized':
                        metadata.append(f"[{category}]")
                    
                    if importance > 0.7:
                        metadata.append(f"⭐{importance:.1f}")
                    elif importance < 0.3:
                        metadata.append(f"📎{importance:.1f}")
                    
                    if access_count > 5:
                        metadata.append(f"👁️{access_count}")
                    
                    if metadata:
                        key_line += f" {' '.join(metadata)}"
                    
                    response.append(key_line)
                else:
                    response.append(f"  • {key}")
            
            return "\n".join(response)
    
    def get_memory_insights(self) -> str:
        """Get comprehensive insights about the memory system"""
        with self._lock:
            data = self._load_data()
            
            if not data:
                return "Memory is empty - no insights available"
            
            insights = []
            insights.append("🧠 Memory System Insights\n" + "=" * 40)
            
            # Basic statistics
            total_memories = len(data)
            insights.append(f"📊 Total memories: {total_memories}")
            
            # Category breakdown
            categories = {}
            importance_scores = []
            access_counts = []
            recent_activity = 0
            week_ago = time.time() - (7 * 24 * 60 * 60)
            
            for entry in data.values():
                if isinstance(entry, dict):
                    cat = entry.get('category', 'uncategorized')
                    categories[cat] = categories.get(cat, 0) + 1
                    importance_scores.append(entry.get('importance', 0.5))
                    access_counts.append(entry.get('access_count', 0))
                    
                    if entry.get('last_accessed', 0) > week_ago:
                        recent_activity += 1
            
            if categories:
                insights.append(f"\n📁 Categories:")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_memories) * 100
                    insights.append(f"  • {cat}: {count} ({percentage:.1f}%)")
            
            # Importance analysis
            if importance_scores:
                avg_importance = sum(importance_scores) / len(importance_scores)
                high_importance = sum(1 for score in importance_scores if score > 0.7)
                insights.append(f"\n⭐ Importance Analysis:")
                insights.append(f"  • Average importance: {avg_importance:.2f}")
                insights.append(f"  • High importance memories: {high_importance}")
            
            # Usage patterns
            if access_counts:
                total_accesses = sum(access_counts)
                frequently_accessed = sum(1 for count in access_counts if count > 5)
                insights.append(f"\n👁️ Usage Patterns:")
                insights.append(f"  • Total accesses: {total_accesses}")
                insights.append(f"  • Frequently accessed: {frequently_accessed}")
                insights.append(f"  • Recent activity (7 days): {recent_activity}")
            
            # Intelligence insights
            if self.intelligence:
                try:
                    intel_insights = self.intelligence.get_memory_insights()
                    insights.append(f"\n🔗 Network Analysis:")
                    insights.append(f"  • Total concepts: {intel_insights.get('total_concepts', 0)}")
                    insights.append(f"  • Avg connections per memory: {intel_insights.get('average_connections_per_memory', 0):.1f}")
                    insights.append(f"  • Network density: {intel_insights.get('memory_network_density', 0):.3f}")
                    
                    if intel_insights.get('top_concepts'):
                        insights.append(f"\n🏷️ Top Concepts:")
                        for concept, count in intel_insights['top_concepts'][:5]:
                            insights.append(f"  • {concept} ({count} memories)")
                            
                except Exception as e:
                    insights.append(f"\n⚠️ Intelligence analysis error: {e}")
            
            return "\n".join(insights)
    
    def consolidate_memories(self, days_old: int = 30) -> str:
        """Consolidate and optimize memory storage"""
        try:
            with self._lock:
                data = self._load_data()
                
                if not data:
                    return "No memories to consolidate"
                
                cutoff_time = time.time() - (days_old * 24 * 60 * 60)
                old_memories = {}
                active_memories = {}
                
                # Separate old and active memories
                for key, entry in data.items():
                    if isinstance(entry, dict):
                        last_accessed = entry.get('last_accessed', entry.get('timestamp', time.time()))
                        importance = entry.get('importance', 0.5)
                        access_count = entry.get('access_count', 0)
                        
                        # Keep memories that are:
                        # - Recently accessed OR high importance OR frequently accessed
                        if (last_accessed > cutoff_time or 
                            importance > 0.7 or 
                            access_count > 5):
                            active_memories[key] = entry
                        else:
                            old_memories[key] = entry
                    else:
                        # Old format entries - keep them for now
                        active_memories[key] = entry
                
                if not old_memories:
                    return f"No memories older than {days_old} days found for consolidation"
                
                # Create archive file
                archive_dir = self.storage_file.parent / "archives"
                archive_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_file = archive_dir / f"memory_archive_{timestamp}.json"
                
                # Save archived memories
                archive_data = {
                    "archived_date": datetime.now().isoformat(),
                    "days_old_threshold": days_old,
                    "archived_count": len(old_memories),
                    "memories": old_memories
                }
                
                with open(archive_file, 'w', encoding='utf-8') as f:
                    json.dump(archive_data, f, indent=2, ensure_ascii=False)
                
                # Update active storage
                self._save_data(active_memories)
                
                response = "🧹 Memory Consolidation Complete"
                response += f"\n  • Archived: {len(old_memories)} old memories"
                response += f"\n  • Retained: {len(active_memories)} active memories"
                response += f"\n  • Archive saved to: {archive_file.name}"
                
                self.logger.info(f"Consolidated {len(old_memories)} memories to archive")
                return response
                
        except Exception as e:
            self.logger.error(f"Memory consolidation failed: {e}")
            return f"Memory consolidation failed: {str(e)}"
    
    def delete(self, key: str) -> str:
        """Delete a key from persistent memory"""
        with self._lock:
            data = self._load_data()
            
            if key not in data:
                return f"Key '{key}' not found in memory"
            
            del data[key]
            self._save_data(data)
            
            self.logger.info(f"Deleted key '{key}' from memory")
            return f"Successfully deleted '{key}' from persistent memory"
    
    def get_stats(self) -> str:
        """Get comprehensive statistics about memory usage"""
        with self._lock:
            data = self._load_data()
            
            if not data:
                return "Memory is empty (0 keys stored)"
            
            # Calculate comprehensive statistics
            stats = []
            stats.append("📊 Enhanced Memory Statistics")
            stats.append("=" * 40)
            
            total_keys = len(data)
            storage_size = self.storage_file.stat().st_size if self.storage_file.exists() else 0
            
            stats.append(f"🔢 Total keys: {total_keys}")
            stats.append(f"💾 Storage file size: {storage_size:,} bytes")
            
            # Content analysis
            total_content_size = 0
            timestamps = []
            categories = {}
            importance_levels = {'low': 0, 'medium': 0, 'high': 0}
            
            for key, entry in data.items():
                if isinstance(entry, dict):
                    value = entry.get('value', '')
                    total_content_size += len(str(value))
                    
                    if 'timestamp' in entry:
                        timestamps.append(entry['timestamp'])
                    
                    cat = entry.get('category', 'uncategorized')
                    categories[cat] = categories.get(cat, 0) + 1
                    
                    importance = entry.get('importance', 0.5)
                    if importance >= 0.7:
                        importance_levels['high'] += 1
                    elif importance >= 0.4:
                        importance_levels['medium'] += 1
                    else:
                        importance_levels['low'] += 1
                else:
                    total_content_size += len(str(entry))
            
            avg_size = total_content_size / total_keys if total_keys > 0 else 0
            stats.append(f"📝 Total content: {total_content_size:,} characters")
            stats.append(f"📏 Average entry size: {avg_size:.1f} characters")
            
            # Temporal analysis
            if timestamps:
                oldest = min(timestamps)
                newest = max(timestamps)
                oldest_str = datetime.fromtimestamp(oldest).strftime('%Y-%m-%d %H:%M')
                newest_str = datetime.fromtimestamp(newest).strftime('%Y-%m-%d %H:%M')
                stats.append(f"⏰ Oldest entry: {oldest_str}")
                stats.append(f"🕐 Newest entry: {newest_str}")
            
            # Category breakdown
            if categories:
                stats.append(f"\n📁 Categories:")
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_keys) * 100
                    stats.append(f"  • {cat}: {count} entries ({percentage:.1f}%)")
            
            # Importance distribution
            if any(importance_levels.values()):
                stats.append(f"\n⭐ Importance Distribution:")
                for level, count in importance_levels.items():
                    if count > 0:
                        percentage = (count / total_keys) * 100
                        stats.append(f"  • {level.capitalize()}: {count} ({percentage:.1f}%)")
            
            return "\n".join(stats)
    
    def get_tools(self) -> Dict[str, Callable]:
        """Return all available tool functions with enhanced capabilities"""
        return {
            # Core memory operations
            'bb7_memory_store': lambda k, v, category="uncategorized", importance=0.5, tags=None: 
                self.store(k, v, category, importance, tags or []),
            'bb7_memory_retrieve': lambda k, include_related=False: 
                self.retrieve(k, include_related),
            'bb7_memory_delete': self.delete,
            
            # Enhanced listing and search
            'bb7_memory_list': lambda prefix=None, category=None, min_importance=0.0, sort_by="timestamp": 
                self.list_keys(prefix, category, min_importance, sort_by),
            'bb7_memory_search': lambda query, max_results=5: 
                self.intelligent_search(query, max_results),
            
            # Analytics and insights
            'bb7_memory_stats': self.get_stats,
            'bb7_memory_insights': self.get_memory_insights,
            'bb7_memory_consolidate': lambda days_old=30: 
                self.consolidate_memories(days_old),
                
            # Category management
            'bb7_memory_categories': lambda: 
                f"Available categories:\n" + "\n".join(f"• {cat}: {desc}" for cat, desc in self.categories.items())
        }


# For standalone testing
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    memory = EnhancedMemoryTool()
    
    # Test enhanced operations
    print("=== Enhanced Memory Tool Test ===")
    print(memory.store("test_insight", "Discovered that caching improves performance by 40%", 
                      category="insights", importance=0.8, tags=["performance", "caching"]))
    print(memory.retrieve("test_insight", include_related=True))
    print(memory.get_memory_insights())
