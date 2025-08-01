#!/usr/bin/env python3
"""
Memory Interconnection Layer - Creates intelligent links between memory systems

This enhancement layer provides:
- Semantic similarity matching between memories
- Automatic cross-referencing of related content
- Context-aware memory retrieval
- Intelligence amplification through memory synthesis
"""

import json
import re
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Callable
from collections import defaultdict, Counter
import hashlib
import difflib

class MemoryInterconnectionEngine:
    """Creates intelligent connections between different memory systems"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.logger = logging.getLogger(__name__)
        
        # Memory relationship graph
        self.relationships_file = self.data_dir / "memory_relationships.json"
        self.concept_index_file = self.data_dir / "concept_index.json"
        self.importance_scores_file = self.data_dir / "importance_scores.json"
        
        # Initialize indices
        self._load_indices()
        
    def _load_indices(self):
        """Load memory relationship indices"""
        try:
            if self.relationships_file.exists():
                with open(self.relationships_file, 'r') as f:
                    self.relationships = json.load(f)
            else:
                self.relationships = {"memory_links": {}, "concept_map": {}, "session_connections": {}}
                
            if self.concept_index_file.exists():
                with open(self.concept_index_file, 'r') as f:
                    self.concept_index = json.load(f)
            else:
                self.concept_index = {"concepts": {}, "term_frequency": {}, "inverse_document_frequency": {}}
                
            if self.importance_scores_file.exists():
                with open(self.importance_scores_file, 'r') as f:
                    self.importance_scores = json.load(f)
            else:
                self.importance_scores = {}
                
        except Exception as e:
            self.logger.error(f"Error loading memory indices: {e}")
            self._initialize_empty_indices()
    
    def _initialize_empty_indices(self):
        """Initialize empty indices if loading fails"""
        self.relationships = {"memory_links": {}, "concept_map": {}, "session_connections": {}}
        self.concept_index = {"concepts": {}, "term_frequency": {}, "inverse_document_frequency": {}}
        self.importance_scores = {}
    
    def _save_indices(self):
        """Save all memory indices"""
        try:
            with open(self.relationships_file, 'w') as f:
                json.dump(self.relationships, f, indent=2)
            with open(self.concept_index_file, 'w') as f:
                json.dump(self.concept_index, f, indent=2)
            with open(self.importance_scores_file, 'w') as f:
                json.dump(self.importance_scores, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving memory indices: {e}")
    
    def extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from text using multiple heuristics"""
        if not text:
            return []
        
        concepts = set()
        text = str(text).lower()
        
        # Extract technical terms (camelCase, snake_case, UPPER_CASE)
        tech_terms = re.findall(r'\b[a-zA-Z]+[A-Z][a-zA-Z]*\b|\b[a-z]+_[a-z_]+\b|\b[A-Z_]{2,}\b', text)
        concepts.update(tech_terms)
        
        # Extract quoted strings (likely important terms)
        quoted = re.findall(r'["\']([^"\']{3,20})["\']', text)
        concepts.update(quoted)
        
        # Extract file/path references
        paths = re.findall(r'\b[\w/\\.-]+\.(?:py|js|json|md|txt|yml|yaml|toml|cfg)\b', text)
        concepts.update(paths)
        
        # Extract function/method names
        functions = re.findall(r'\b[a-z_][a-z0-9_]*(?=\s*\()', text)
        concepts.update(functions)
        
        # Extract important multi-word phrases (2-4 words)
        phrases = re.findall(r'\b(?:[a-z]+\s+){1,3}[a-z]+\b', text)
        important_phrases = [p for p in phrases if len(p) > 8 and len(p.split()) <= 4]
        concepts.update(important_phrases)
        
        # Filter out common words and very short terms
        common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'this', 'that', 'these', 'those', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must'}
        
        filtered_concepts = []
        for concept in concepts:
            if (len(concept) >= 3 and 
                concept.lower() not in common_words and 
                not concept.isdigit() and
                len(set(concept)) > 1):  # Not all same character
                filtered_concepts.append(concept.strip())
        
        return list(set(filtered_concepts))[:20]  # Limit to top 20 concepts
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        if not text1 or not text2:
            return 0.0
        
        # Extract concepts from both texts
        concepts1 = set(self.extract_concepts(text1))
        concepts2 = set(self.extract_concepts(text2))
        
        if not concepts1 or not concepts2:
            # Fallback to simple text similarity
            return difflib.SequenceMatcher(None, str(text1).lower(), str(text2).lower()).ratio()
        
        # Calculate concept overlap
        intersection = concepts1 & concepts2
        union = concepts1 | concepts2
        
        if not union:
            return 0.0
        
        concept_similarity = len(intersection) / len(union)
        
        # Boost similarity if key concepts match
        important_matches = 0
        for concept in intersection:
            if (len(concept) > 5 or 
                '_' in concept or 
                any(c.isupper() for c in concept[1:])):  # Technical terms
                important_matches += 1
        
        importance_boost = min(important_matches * 0.2, 0.5)
        
        return min(concept_similarity + importance_boost, 1.0)
    
    def analyze_memory_entry(self, key: str, value: str, source: str = "memory") -> Dict[str, Any]:
        """Analyze a memory entry and create connections"""
        concepts = self.extract_concepts(value)
        
        # Calculate importance score
        importance = self._calculate_importance(value, concepts)
        self.importance_scores[f"{source}:{key}"] = {
            "score": importance,
            "timestamp": time.time(),
            "concepts": concepts
        }
        
        # Update concept index
        for concept in concepts:
            if concept not in self.concept_index["concepts"]:
                self.concept_index["concepts"][concept] = []
            
            entry_ref = f"{source}:{key}"
            if entry_ref not in self.concept_index["concepts"][concept]:
                self.concept_index["concepts"][concept].append(entry_ref)
        
        # Find related memories
        related_memories = self._find_related_memories(key, value, source)
        
        # Store relationships
        memory_id = f"{source}:{key}"
        self.relationships["memory_links"][memory_id] = {
            "concepts": concepts,
            "related": related_memories,
            "importance": importance,
            "last_updated": time.time()
        }
        
        self._save_indices()
        
        return {
            "concepts": concepts,
            "importance": importance,
            "related_memories": related_memories
        }
    
    def _calculate_importance(self, content: str, concepts: List[str]) -> float:
        """Calculate importance score for content"""
        importance = 0.0
        
        # Length factor (longer content often more important)
        length_score = min(len(content) / 1000, 0.3)
        importance += length_score
        
        # Concept richness
        concept_score = min(len(concepts) * 0.05, 0.4)
        importance += concept_score
        
        # Technical content indicators
        tech_indicators = ['error', 'debug', 'fix', 'solution', 'bug', 'issue', 'problem', 'resolve']
        tech_score = sum(0.1 for indicator in tech_indicators if indicator in content.lower())
        importance += min(tech_score, 0.3)
        
        # Decision/insight indicators
        insight_indicators = ['decided', 'learned', 'discovered', 'realized', 'important', 'key', 'critical']
        insight_score = sum(0.1 for indicator in insight_indicators if indicator in content.lower())
        importance += min(insight_score, 0.3)
        
        return min(importance, 1.0)
    
    def _find_related_memories(self, key: str, value: str, source: str) -> List[Dict[str, Any]]:
        """Find memories related to the current entry"""
        related = []
        
        # Search across all memory sources
        current_concepts = set(self.extract_concepts(value))
        
        for memory_id, memory_data in self.relationships["memory_links"].items():
            if memory_id == f"{source}:{key}":
                continue  # Skip self
            
            memory_concepts = set(memory_data.get("concepts", []))
            
            # Calculate concept overlap
            if current_concepts and memory_concepts:
                overlap = current_concepts & memory_concepts
                if overlap:
                    similarity = len(overlap) / len(current_concepts | memory_concepts)
                    if similarity > 0.2:  # Threshold for relatedness
                        related.append({
                            "memory_id": memory_id,
                            "similarity": similarity,
                            "shared_concepts": list(overlap),
                            "importance": memory_data.get("importance", 0.0)
                        })
        
        # Sort by similarity and importance
        related.sort(key=lambda x: (x["similarity"] * 0.7 + x["importance"] * 0.3), reverse=True)
        
        return related[:10]  # Return top 10 related memories
    
    def intelligent_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Intelligent search across all memory systems"""
        query_concepts = set(self.extract_concepts(query))
        results = []
        
        for memory_id, memory_data in self.relationships["memory_links"].items():
            memory_concepts = set(memory_data.get("concepts", []))
            
            if query_concepts and memory_concepts:
                # Concept-based similarity
                concept_similarity = len(query_concepts & memory_concepts) / len(query_concepts | memory_concepts)
                
                # Boost for exact matches
                exact_matches = sum(1 for concept in query_concepts if concept in memory_concepts)
                exact_boost = exact_matches * 0.2
                
                total_score = concept_similarity + exact_boost + (memory_data.get("importance", 0.0) * 0.1)
                
                if total_score > 0.1:  # Minimum relevance threshold
                    results.append({
                        "memory_id": memory_id,
                        "relevance_score": total_score,
                        "matched_concepts": list(query_concepts & memory_concepts),
                        "importance": memory_data.get("importance", 0.0)
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:max_results]
    
    def get_concept_network(self, concept: str) -> Dict[str, Any]:
        """Get the network of memories connected to a concept"""
        if concept not in self.concept_index["concepts"]:
            return {"concept": concept, "memories": [], "related_concepts": []}
        
        # Get all memories containing this concept
        memory_refs = self.concept_index["concepts"][concept]
        
        # Find related concepts (concepts that co-occur)
        related_concepts = Counter()
        for memory_ref in memory_refs:
            if memory_ref in self.relationships["memory_links"]:
                memory_concepts = self.relationships["memory_links"][memory_ref].get("concepts", [])
                for other_concept in memory_concepts:
                    if other_concept != concept:
                        related_concepts[other_concept] += 1
        
        return {
            "concept": concept,
            "memories": memory_refs,
            "related_concepts": dict(related_concepts.most_common(10)),
            "total_references": len(memory_refs)
        }
    
    def get_memory_insights(self) -> Dict[str, Any]:
        """Generate insights about the memory system"""
        total_memories = len(self.relationships["memory_links"])
        total_concepts = len(self.concept_index["concepts"])
        
        # Find most important memories
        top_memories = sorted(
            [(mid, data.get("importance", 0.0)) for mid, data in self.relationships["memory_links"].items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Find most connected concepts
        concept_connections = {
            concept: len(refs) 
            for concept, refs in self.concept_index["concepts"].items()
        }
        top_concepts = sorted(concept_connections.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Memory network statistics
        total_connections = sum(len(data.get("related", [])) for data in self.relationships["memory_links"].values())
        avg_connections = total_connections / total_memories if total_memories > 0 else 0
        
        return {
            "total_memories": total_memories,
            "total_concepts": total_concepts,
            "average_connections_per_memory": avg_connections,
            "top_memories": top_memories,
            "top_concepts": top_concepts,
            "memory_network_density": total_connections / (total_memories * (total_memories - 1)) if total_memories > 1 else 0
        }
    
    def consolidate_memories(self, age_threshold_days: int = 30) -> Dict[str, Any]:
        """Consolidate old memories and remove low-importance entries"""
        current_time = time.time()
        threshold_time = current_time - (age_threshold_days * 24 * 60 * 60)
        
        consolidated = 0
        archived = 0
        
        memories_to_archive = []
        
        for memory_id, memory_data in self.relationships["memory_links"].items():
            last_updated = memory_data.get("last_updated", current_time)
            importance = memory_data.get("importance", 0.0)
            
            # Archive low-importance, old memories
            if last_updated < threshold_time and importance < 0.3:
                memories_to_archive.append(memory_id)
        
        # Create archive
        archive_file = None
        if memories_to_archive:
            archive_file = self.data_dir / f"memory_archive_{int(current_time)}.json"
            archive_data = {
                "archived_at": current_time,
                "memories": {mid: self.relationships["memory_links"][mid] for mid in memories_to_archive}
            }
            
            with open(archive_file, 'w') as f:
                json.dump(archive_data, f, indent=2)
            
            # Remove from active memory
            for memory_id in memories_to_archive:
                del self.relationships["memory_links"][memory_id]
                archived += 1
        
        self._save_indices()
        
        return {
            "consolidated": consolidated,
            "archived": archived,
            "archive_file": str(archive_file) if archive_file else None
        }
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all memory interconnection tools with their metadata."""
        return {
            'bb7_memory_analyze_entry': {
                "callable": lambda key, value, source="memory": self.analyze_memory_entry(key, value, source),
                "metadata": {
                    "name": "bb7_memory_analyze_entry",
                    "description": "Analyze a memory entry for key concepts, importance, and semantic connections. Use to extract insights and relationships from stored knowledge.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["knowledge_extraction", "semantic_analysis", "insight_generation"],
                    "input_schema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "source": {"type": "string", "default": "memory"}}, "required": ["key", "value"]}
                }
            },
            'bb7_memory_intelligent_search': {
                "callable": lambda query, max_results=10: self.intelligent_search(query, max_results),
                "metadata": {
                    "name": "bb7_memory_intelligent_search",
                    "description": "Search memories using semantic similarity and concept matching. Use for advanced context recall and finding related information.",
                    "category": "memory",
                    "priority": "high",
                    "when_to_use": ["semantic_search", "context_recall", "information_retrieval"],
                    "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}
                }
            },
            'bb7_memory_get_insights': {
                "callable": self.get_memory_insights,
                "metadata": {
                    "name": "bb7_memory_get_insights",
                    "description": "Generate high-level insights and statistics about the memory system, including categories, importance, and usage patterns.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["memory_analysis", "system_overview", "performance_metrics"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            },
            'bb7_memory_consolidate': {
                "callable": lambda age_threshold_days=30: self.consolidate_memories(age_threshold_days),
                "metadata": {
                    "name": "bb7_memory_consolidate",
                    "description": "🗃️ Consolidate and archive old or low-importance memories. Use for memory optimization and long-term storage.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["archive", "optimize", "cleanup"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "days_old": {"type": "integer", "default": 30, "description": "Archive memories older than this (optional)"} },
                        "required": []
                    }
                }
            },
            'bb7_memory_concept_network': {
                "callable": self.get_concept_network,
                "metadata": {
                    "name": "bb7_memory_concept_network",
                    "description": "Build and visualize the network of concepts and relationships across all memories. Use for knowledge graph analysis and discovery.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["knowledge_graph", "concept_mapping", "relationship_discovery"],
                    "input_schema": {"type": "object", "properties": {"concept": {"type": "string"}}, "required": ["concept"]}
                }
            },
            'bb7_memory_extract_concepts': {
                "callable": self.extract_concepts,
                "metadata": {
                    "name": "bb7_memory_extract_concepts",
                    "description": "Extract key concepts, technical terms, and important phrases from memory entries or text. Use for tagging, indexing, and semantic enrichment.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["tagging", "indexing", "semantic_enrichment"],
                    "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
                }
            }
        }
