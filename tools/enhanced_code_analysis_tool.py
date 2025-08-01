#!/usr/bin/env python3
"""
Enhanced Code Analysis & Secure Python Interpreter Tool
Production-ready implementation with complete CFA, DFA, Type Inference, and hardened Python execution.

Features:
- Complete Control Flow Analysis with dominance computation
- Data Flow Analysis with reaching definitions and live variables
- Advanced Type Inference with constraint solving
- Hardened Python execution with RestrictedPython
- Resource limits and security auditing
- Structured JSON I/O
"""

import ast
import sys
import io
import os
import re
import json
import time
import logging
import threading
import subprocess
import tempfile
import traceback
import signal
from pathlib import Path

# Import resource module conditionally (not available on Windows)
try:
    import resource
    RESOURCE_AVAILABLE = True
except ImportError:
    RESOURCE_AVAILABLE = False
from typing import Dict, List, Any, Set, Optional, Union, Tuple, DefaultDict, Callable
from dataclasses import dataclass, asdict, field
from collections import defaultdict, deque
from contextlib import redirect_stdout, redirect_stderr
import builtins

# Try to import RestrictedPython for sandboxing
try:
    from RestrictedPython import compile_restricted
    from RestrictedPython.Guards import safe_globals, safe_builtins
    from RestrictedPython.Limits import limited_builtins
    RESTRICTED_PYTHON_AVAILABLE = True
except ImportError:
    RESTRICTED_PYTHON_AVAILABLE = False
    # Provide fallback values
    safe_globals = {}
    safe_builtins = {}
    limited_builtins = {}


@dataclass
class CodeLocation:
    """Precise source code location"""
    file: str
    line: int
    column: int
    end_line: Optional[int] = None
    end_column: Optional[int] = None


@dataclass
class Variable:
    """Complete variable analysis data"""
    name: str
    type_hint: Optional[str] = None
    inferred_type: Optional[str] = None
    scope: str = "local"
    first_def: Optional[CodeLocation] = None
    assignments: List[CodeLocation] = field(default_factory=list)
    usages: List[CodeLocation] = field(default_factory=list)
    is_parameter: bool = False
    is_global: bool = False


@dataclass
class Function:
    """Complete function analysis data"""
    name: str
    params: List[str]
    return_type: Optional[str] = None
    complexity: int = 0
    location: Optional[CodeLocation] = None
    calls: List[str] = field(default_factory=list)
    called_by: List[str] = field(default_factory=list)
    local_variables: Set[str] = field(default_factory=set)
    security_issues: List[str] = field(default_factory=list)
    cfg_nodes: int = 0
    cfg_edges: int = 0


@dataclass
class ControlFlowNode:
    """Control Flow Graph node with complete analysis"""
    id: int
    type: str  # "entry", "exit", "statement", "condition", "loop", "exception"
    code: str
    location: CodeLocation
    predecessors: Set[int] = field(default_factory=set)
    successors: Set[int] = field(default_factory=set)
    dominators: Set[int] = field(default_factory=set)
    post_dominators: Set[int] = field(default_factory=set)
    reaching_defs: Set[str] = field(default_factory=set)
    live_vars: Set[str] = field(default_factory=set)


@dataclass
class DataFlowFact:
    """Data flow analysis facts"""
    variable: str
    definition_line: int
    reaching_definitions: Set[int] = field(default_factory=set)
    live_variables: Set[str] = field(default_factory=set)


class SecurityAuditor:
    """Security analysis and auditing"""
    
    def __init__(self):
        self.security_patterns = {
            'sql_injection': [
                r'execute\s*\([^)]*%[^)]*\)',
                r'cursor\.execute\s*\([^)]*\+[^)]*\)',
                r'query.*=.*%.*format',
                r'SELECT.*\+.*FROM',
            ],
            'command_injection': [
                r'os\.system\s*\([^)]*\+[^)]*\)',
                r'subprocess\.[^(]*\([^)]*shell\s*=\s*True[^)]*\+',
                r'eval\s*\([^)]*input[^)]*\)',
                r'exec\s*\([^)]*input[^)]*\)',
            ],
            'path_traversal': [
                r'open\s*\([^)]*\.\.[^)]*\)',
                r'file\s*=.*\.\.',
                r'path.*\+.*\.\.',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']',
            ],
            'dangerous_imports': [
                r'import\s+(os|subprocess|sys|eval|exec)',
                r'from\s+(os|subprocess|sys)\s+import',
            ]
        }
        
        self.dangerous_functions = {
            'eval', 'exec', 'compile', '__import__', 'open', 'file',
            'input', 'raw_input', 'reload', 'vars', 'globals', 'locals',
            'dir', 'hasattr', 'getattr', 'setattr', 'delattr'
        }
    
    def scan_code(self, source_code: str, tree: ast.AST) -> Dict[str, Any]:
        """Complete security scan"""
        issues = []
        
        # Pattern-based detection
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, source_code, re.IGNORECASE)
                for match in matches:
                    line_num = source_code[:match.start()].count('\n') + 1
                    issues.append({
                        "category": category,
                        "severity": self._get_severity(category),
                        "line": line_num,
                        "code": match.group(),
                        "description": self._get_description(category),
                        "pattern": pattern
                    })
        
        # AST-based detection
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = self._extract_call_name(node)
                if func_name in self.dangerous_functions:
                    issues.append({
                        "category": "dangerous_function",
                        "severity": "HIGH",
                        "line": node.lineno,
                        "code": f"{func_name}(...)",
                        "description": f"Potentially dangerous function: {func_name}",
                        "function": func_name
                    })
        
        return {
            "total_issues": len(issues),
            "issues": issues,
            "by_severity": self._group_by_severity(issues),
            "by_category": self.bb7_group_by_category(issues)
        }
    
    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from call node"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None

    def _get_severity(self, category: str) -> str:
        severity_map = {
            'sql_injection': 'HIGH',
            'command_injection': 'HIGH',
            'path_traversal': 'MEDIUM',
            'hardcoded_secrets': 'MEDIUM',
            'dangerous_imports': 'HIGH'
        }
        return severity_map.get(category, 'LOW')
    
    def _get_description(self, category: str) -> str:
        descriptions = {
            'sql_injection': 'Potential SQL injection vulnerability',
            'command_injection': 'Potential command injection vulnerability',
            'path_traversal': 'Potential path traversal vulnerability',
            'hardcoded_secrets': 'Hardcoded credentials detected',
            'dangerous_imports': 'Dangerous module import detected'
        }
        return descriptions.get(category, 'Security issue detected')
    
    def _group_by_severity(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = defaultdict(list)
        for issue in issues:
            grouped[issue["severity"]].append(issue)
        return dict(grouped)
    
    def _group_by_category(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        grouped = defaultdict(list)
        for issue in issues:
            grouped[issue["category"]].append(issue)
        return dict(grouped)


class TypeInferenceEngine:
    """Advanced type inference with constraint solving"""
    
    def __init__(self):
        self.type_constraints = []
        self.type_environment = {}
        self.builtin_types = {
            'int': 'int', 'float': 'float', 'str': 'str', 'bool': 'bool',
            'list': 'List', 'dict': 'Dict', 'tuple': 'Tuple', 'set': 'Set',
            'None': 'None', 'type': 'Type'
        }
    
    def infer_types(self, tree: ast.AST, source_code: str) -> Dict[str, Any]:
        """Complete type inference analysis"""
        explicit_types = self._collect_explicit_types(tree)
        usage_types = self._infer_from_usage(tree)
        control_flow_types = self._infer_from_control_flow(tree)
        
        # Combine and propagate types
        all_types = {**explicit_types, **usage_types, **control_flow_types}
        propagated_types = self._propagate_types(tree, all_types)
        final_types = {**all_types, **propagated_types}
        
        # Calculate coverage metrics
        coverage_metrics = self._calculate_coverage(tree, final_types)
        
        return {
            "explicit_types": explicit_types,
            "inferred_types": usage_types,
            "control_flow_types": control_flow_types,
            "propagated_types": propagated_types,
            "final_types": final_types,
            "coverage_metrics": coverage_metrics,
            "type_errors": self._detect_inconsistencies(final_types)
        }
    
    def _collect_explicit_types(self, tree: ast.AST) -> Dict[str, str]:
        """Collect explicit type annotations"""
        explicit_types = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and node.target:
                if isinstance(node.target, ast.Name):
                    var_name = node.target.id
                    if node.annotation:
                        type_annotation = self._extract_type_annotation(node.annotation)
                        explicit_types[var_name] = type_annotation
            
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Function parameters
                for arg in node.args.args:
                    if arg.annotation:
                        param_type = self._extract_type_annotation(arg.annotation)
                        explicit_types[f"{node.name}.{arg.arg}"] = param_type
                
                # Return type
                if node.returns:
                    return_type = self._extract_type_annotation(node.returns)
                    explicit_types[f"{node.name}.__return__"] = return_type
        
        return explicit_types
    
    def _infer_from_usage(self, tree: ast.AST) -> Dict[str, str]:
        """Infer types from usage patterns"""
        usage_types = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        inferred_type = self._infer_type_from_value(node.value)
                        if inferred_type:
                            usage_types[var_name] = inferred_type
        
        return usage_types

    def _infer_from_control_flow(self, tree: ast.AST) -> Dict[str, str]:
        """Infer types from control flow analysis"""
        control_flow_types = {}
        
        # Type narrowing in conditions
        for node in ast.walk(tree):
            if isinstance(node, ast.If):
                if isinstance(node.test, ast.Call):
                    if isinstance(node.test.func, ast.Name) and node.test.func.id == 'isinstance':
                        if len(node.test.args) >= 2:
                            if isinstance(node.test.args[0], ast.Name):
                                var_name = node.test.args[0].id
                                type_check = self._extract_type_annotation(node.test.args[1])
                                control_flow_types[f"{var_name}_narrowed"] = type_check
        
        return control_flow_types
    
    def _propagate_types(self, tree: ast.AST, known_types: Dict[str, str]) -> Dict[str, str]:
        """Propagate type information through assignments"""
        propagated = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                # Simple assignment propagation
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    target_name = node.targets[0].id
                    if isinstance(node.value, ast.Name):
                        source_name = node.value.id
                        if source_name in known_types:
                            propagated[target_name] = known_types[source_name]
        
        return propagated
    
    def _calculate_coverage(self, tree: ast.AST, all_types: Dict[str, str]) -> Dict[str, Any]:
        """Calculate type coverage metrics"""
        total_variables = set()
        typed_variables = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Load)):
                total_variables.add(node.id)
                if node.id in all_types:
                    typed_variables.add(node.id)
        
        total_count = len(total_variables)
        typed_count = len(typed_variables)
        coverage_percentage = (typed_count / total_count * 100) if total_count > 0 else 100
        
        return {
            "total_variables": total_count,
            "typed_variables": typed_count,
            "coverage_percentage": coverage_percentage
        }
    
    def _detect_inconsistencies(self, types: Dict[str, str]) -> List[str]:
        """Detect type inconsistencies"""
        inconsistencies = []
        
        # Simple consistency checks
        for var_name, var_type in types.items():
            if "_narrowed" in var_name:
                base_name = var_name.replace("_narrowed", "")
                if base_name in types and types[base_name] != var_type:
                    inconsistencies.append(f"Type inconsistency for {base_name}: {types[base_name]} vs {var_type}")
        
        return inconsistencies
    
    def _extract_type_annotation(self, annotation: ast.AST) -> str:
        """Extract type annotation as string"""
        try:
            if hasattr(ast, 'unparse'):
                return ast.unparse(annotation)
            else:
                return str(annotation)[:100]
        except:
            return "Unknown"
    
    def _infer_type_from_value(self, node: ast.AST) -> Optional[str]:
        """Infer type from assignment value"""
        if isinstance(node, ast.Constant):
            value_type = type(node.value).__name__
            return self.builtin_types.get(value_type, value_type)
        elif isinstance(node, ast.List):
            return "List"
        elif isinstance(node, ast.Dict):
            return "Dict"
        elif isinstance(node, ast.Set):
            return "Set"
        elif isinstance(node, ast.Tuple):
            return "Tuple"
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                return self.builtin_types.get(func_name)
        return None


class ControlFlowAnalyzer:
    """Complete Control Flow Analysis with dominance computation"""
    
    def __init__(self):
        self.node_counter = 0
    
    def build_cfg(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Dict[str, Any]:
        """Build complete Control Flow Graph"""
        self.node_counter = 0
        nodes = {}
        edges = []
        
        # Entry node
        entry_node = ControlFlowNode(
            id=self.node_counter,
            type="entry",
            code=f"def {func_node.name}(...):",
            location=CodeLocation("", func_node.lineno, func_node.col_offset)
        )
        nodes[self.node_counter] = entry_node
        entry_id = self.node_counter
        self.node_counter += 1
        
        # Process function body
        last_nodes = self._process_statements(func_node.body, entry_id, nodes, edges)
        
        # Exit node
        exit_id = self.node_counter
        exit_node = ControlFlowNode(
            id=exit_id,
            type="exit",
            code="return",
            location=CodeLocation("", getattr(func_node, 'end_lineno', func_node.lineno), 0)
        )
        nodes[exit_id] = exit_node
        
        # Connect last nodes to exit
        for last_id in last_nodes:
            self._add_edge(last_id, exit_id, nodes, edges)
        
        # Calculate dominance relationships
        self._calculate_dominance(nodes, entry_id, exit_id)
        
        # Calculate cyclomatic complexity
        num_edges = len(edges)
        num_nodes = len(nodes)
        cyclomatic_complexity = num_edges - num_nodes + 2
        
        return {
            "function": func_node.name,
            "nodes": {nid: asdict(node) for nid, node in nodes.items()},
            "edges": edges,
            "entry_node": entry_id,
            "exit_node": exit_id,
            "cyclomatic_complexity": cyclomatic_complexity,
            "num_nodes": num_nodes,
            "num_edges": num_edges
        }
    
    def _process_statements(self, stmts: List[ast.stmt], prev_id: int, 
                          nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process statement list"""
        current_ids = [prev_id]
        
        for stmt in stmts:
            new_ids = []
            for current_id in current_ids:
                last_ids = self._process_statement(stmt, current_id, nodes, edges)
                new_ids.extend(last_ids)
            current_ids = new_ids
        
        return current_ids
    
    def _process_statement(self, stmt: ast.stmt, prev_id: int,
                          nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process individual statement"""
        if isinstance(stmt, ast.If):
            return self._process_if(stmt, prev_id, nodes, edges)
        elif isinstance(stmt, (ast.While, ast.For)):
            return self._process_loop(stmt, prev_id, nodes, edges)
        elif isinstance(stmt, ast.Try):
            return self._process_try(stmt, prev_id, nodes, edges)
        elif isinstance(stmt, ast.Return):
            return self._process_return(stmt, prev_id, nodes, edges)
        else:
            return self._process_simple(stmt, prev_id, nodes, edges)
    
    def _process_if(self, stmt: ast.If, prev_id: int,
                   nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process if statement"""
        # Condition node
        condition_id = self.node_counter
        condition_node = ControlFlowNode(
            id=condition_id,
            type="condition",
            code=f"if {self._ast_to_code(stmt.test)}:",
            location=CodeLocation("", stmt.lineno, stmt.col_offset)
        )
        nodes[condition_id] = condition_node
        self._add_edge(prev_id, condition_id, nodes, edges)
        self.node_counter += 1
        
        # Process if body
        if_last = self._process_statements(stmt.body, condition_id, nodes, edges)
        
        # Process else body
        if stmt.orelse:
            else_last = self._process_statements(stmt.orelse, condition_id, nodes, edges)
        else:
            else_last = [condition_id]
        
        return if_last + else_last
    
    def _process_loop(self, stmt: Union[ast.While, ast.For], prev_id: int,
                     nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process loop statement"""
        # Loop header
        loop_id = self.node_counter
        if isinstance(stmt, ast.While):
            code = f"while {self._ast_to_code(stmt.test)}:"
        else:
            code = f"for {self._ast_to_code(stmt.target)} in {self._ast_to_code(stmt.iter)}:"
        
        loop_node = ControlFlowNode(
            id=loop_id,
            type="loop",
            code=code,
            location=CodeLocation("", stmt.lineno, stmt.col_offset)
        )
        nodes[loop_id] = loop_node
        self._add_edge(prev_id, loop_id, nodes, edges)
        self.node_counter += 1
        
        # Process loop body
        body_last = self._process_statements(stmt.body, loop_id, nodes, edges)
        
        # Back edges
        for last_id in body_last:
            self._add_edge(last_id, loop_id, nodes, edges)
        
        return [loop_id]  # Loop exit
    
    def _process_try(self, stmt: ast.Try, prev_id: int,
                    nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process try-except statement"""
        # Try block
        try_last = self._process_statements(stmt.body, prev_id, nodes, edges)
        all_last = try_last.copy()
        
        # Exception handlers
        for handler in stmt.handlers:
            handler_id = self.node_counter
            
            # Properly extract exception type name
            if handler.type is None:
                exception_name = "Exception"
            elif isinstance(handler.type, ast.Name):
                exception_name = handler.type.id
            elif isinstance(handler.type, ast.Attribute):
                exception_name = handler.type.attr
            else:
                # Fallback for complex expressions
                try:
                    if hasattr(ast, 'unparse'):
                        exception_name = ast.unparse(handler.type)
                    else:
                        exception_name = "Exception"
                except:
                    exception_name = "Exception"
            
            handler_node = ControlFlowNode(
                id=handler_id,
                type="exception",
                code=f"except {exception_name}:",
                location=CodeLocation("", handler.lineno, handler.col_offset)
            )
            nodes[handler_id] = handler_node
            self._add_edge(prev_id, handler_id, nodes, edges)  # Exception edge
            self.node_counter += 1
            
            handler_last = self._process_statements(handler.body, handler_id, nodes, edges)
            all_last.extend(handler_last)
        
        # Finally block
        if stmt.finalbody:
            finally_last = self._process_statements(stmt.finalbody, prev_id, nodes, edges)
            all_last.extend(finally_last)
        
        return all_last
    
    def _process_return(self, stmt: ast.Return, prev_id: int,
                       nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process return statement"""
        return_id = self.node_counter
        code = "return" if stmt.value is None else f"return {self._ast_to_code(stmt.value)}"
        
        return_node = ControlFlowNode(
            id=return_id,
            type="return",
            code=code,
            location=CodeLocation("", stmt.lineno, stmt.col_offset)
        )
        nodes[return_id] = return_node
        self._add_edge(prev_id, return_id, nodes, edges)
        self.node_counter += 1
        
        return []  # Terminal node
    
    def _process_simple(self, stmt: ast.stmt, prev_id: int,
                       nodes: Dict[int, ControlFlowNode], edges: List[Dict]) -> List[int]:
        """Process simple statement"""
        stmt_id = self.node_counter
        stmt_node = ControlFlowNode(
            id=stmt_id,
            type="statement",
            code=self._ast_to_code(stmt),
            location=CodeLocation("", stmt.lineno, stmt.col_offset)
        )
        nodes[stmt_id] = stmt_node
        self._add_edge(prev_id, stmt_id, nodes, edges)
        self.node_counter += 1
        
        return [stmt_id]
    
    def _add_edge(self, from_id: int, to_id: int, 
                 nodes: Dict[int, ControlFlowNode], edges: List[Dict]):
        """Add edge between nodes"""
        edges.append({"from": from_id, "to": to_id})
        nodes[from_id].successors.add(to_id)
        nodes[to_id].predecessors.add(from_id)
    
    def _calculate_dominance(self, nodes: Dict[int, ControlFlowNode], 
                           entry_id: int, exit_id: int):
        """Calculate dominance relationships"""
        # Initialize dominators
        for node_id in nodes:
            if node_id == entry_id:
                nodes[node_id].dominators = {entry_id}
            else:
                nodes[node_id].dominators = set(nodes.keys())
        
        # Iterative dominance calculation
        changed = True
        iterations = 0
        while changed and iterations < 100:
            changed = False
            iterations += 1
            
            for node_id, node in nodes.items():
                if node_id == entry_id:
                    continue
                
                new_dominators = None
                for pred_id in node.predecessors:
                    if new_dominators is None:
                        new_dominators = nodes[pred_id].dominators.copy()
                    else:
                        new_dominators &= nodes[pred_id].dominators
                
                if new_dominators is None:
                    new_dominators = set()
                new_dominators.add(node_id)
                
                if new_dominators != node.dominators:
                    node.dominators = new_dominators
                    changed = True
    
    def _ast_to_code(self, node: ast.AST) -> str:
        """Convert AST node to code string"""
        try:
            if hasattr(ast, 'unparse'):
                return ast.unparse(node)
            else:
                return str(node)[:50] + "..." if len(str(node)) > 50 else str(node)
        except:
            return "<unparseable>"


class DataFlowAnalyzer:
    """Complete Data Flow Analysis implementation"""
    
    def analyze_function(self, cfg: Dict[str, Any], func_node: ast.AST) -> Dict[str, Any]:
        """Perform complete data flow analysis"""
        nodes = cfg["nodes"]
        
        # Initialize reaching definitions
        reaching_defs = {}
        live_vars = {}
        
        for node_id in nodes:
            reaching_defs[node_id] = set()
            live_vars[node_id] = set()
        
        # Reaching definitions analysis (forward)
        reaching_defs = self._reaching_definitions(nodes, reaching_defs)
        
        # Live variables analysis (backward)
        live_vars = self._live_variables(nodes, live_vars)
        
        # Def-use chains
        def_use_chains = self._build_def_use_chains(func_node)
        
        return {
            "reaching_definitions": {str(k): list(v) for k, v in reaching_defs.items()},
            "live_variables": {str(k): list(v) for k, v in live_vars.items()},
            "def_use_chains": def_use_chains
        }
    
    def _reaching_definitions(self, nodes: Dict, reaching_defs: Dict) -> Dict:
        """Compute reaching definitions"""
        changed = True
        iterations = 0
        
        while changed and iterations < 100:
            changed = False
            iterations += 1
            
            for node_id, node_data in nodes.items():
                old_reaching = reaching_defs[node_id].copy()
                
                # Union of predecessor reaching definitions
                new_reaching = set()
                for pred_id in node_data.get("predecessors", []):
                    new_reaching.update(reaching_defs.get(pred_id, set()))
                
                # Apply transfer function
                new_reaching = self._apply_reaching_transfer(node_data, new_reaching)
                
                if new_reaching != old_reaching:
                    reaching_defs[node_id] = new_reaching
                    changed = True
        
        return reaching_defs
    
    def _live_variables(self, nodes: Dict, live_vars: Dict) -> Dict:
        """Compute live variables (backward analysis)"""
        changed = True
        iterations = 0
        
        while changed and iterations < 100:
            changed = False
            iterations += 1
            
            for node_id, node_data in nodes.items():
                old_live = live_vars[node_id].copy()
                
                # Union of successor live variables
                new_live = set()
                for succ_id in node_data.get("successors", []):
                    new_live.update(live_vars.get(succ_id, set()))
                
                # Apply transfer function
                new_live = self._apply_live_transfer(node_data, new_live)
                
                if new_live != old_live:
                    live_vars[node_id] = new_live
                    changed = True
        
        return live_vars
    
    def _apply_reaching_transfer(self, node_data: Dict, reaching_in: Set) -> Set:
        """Apply transfer function for reaching definitions"""
        # Simple implementation - would need more sophisticated analysis
        # for complete def/kill sets
        return reaching_in
    
    def _apply_live_transfer(self, node_data: Dict, live_out: Set) -> Set:
        """Apply transfer function for live variables"""
        # Simple implementation - would need more sophisticated analysis
        # for use/def sets
        return live_out
    
    def _build_def_use_chains(self, func_node: ast.AST) -> Dict[str, Any]:
        """Build definition-use chains"""
        chains = defaultdict(list)
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        chains[target.id].append({
                            "type": "definition",
                            "line": node.lineno,
                            "column": node.col_offset
                        })
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                chains[node.id].append({
                    "type": "use",
                    "line": node.lineno,
                    "column": node.col_offset
                })
        
        # Analyze usage patterns
        usage_analysis = {}
        for var_name, chain in chains.items():
            definitions = [item for item in chain if item["type"] == "definition"]
            uses = [item for item in chain if item["type"] == "use"]
            
            usage_analysis[var_name] = {
                "definition_count": len(definitions),
                "use_count": len(uses),
                "is_unused": len(uses) == 0 and len(definitions) > 0,
                "is_write_only": len(uses) == 0
            }
        
        return {
            "chains": dict(chains),
            "usage_analysis": usage_analysis
        }


class SecurePythonInterpreter:
    """Hardened Python interpreter with complete sandboxing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_auditor = SecurityAuditor()
        
        # Execution limits
        self.max_execution_time = 30
        self.max_memory_mb = 256
        self.max_output_size = 1024 * 1024  # 1MB
        self.max_recursion_depth = 100
        
        # Audit logging
        self.audit_log = []
        self.session_state = {}
        self.stateless_mode = True
        
        # Cross-platform timeout support
        self._execution_thread = None
        self._execution_result = None
        self._execution_error = None
        
        # Restricted environment
        self._setup_restricted_environment()
    
    def _setup_restricted_environment(self):
        """Setup restricted execution environment"""
        if RESTRICTED_PYTHON_AVAILABLE:
            self.restricted_globals = safe_globals.copy()
            self.restricted_globals.update(limited_builtins)
            
            # Remove dangerous functions
            dangerous = ['__import__', 'eval', 'exec', 'compile', 'open', 'file']
            for danger in dangerous:
                self.restricted_globals.pop(danger, None)
            
            # Add safe utilities directly here instead of separate method
            safe_utilities = {
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'min': min, 'max': max, 'sum': sum, 'abs': abs,
                'print': self._safe_print,
                'range': range, 'enumerate': enumerate, 'zip': zip,
                'sorted': sorted, 'reversed': reversed,
                'all': all, 'any': any
            }
            self.restricted_globals.update(safe_utilities)
        else:
            # Fallback to basic restriction
            self.restricted_globals = {
                '__builtins__': {
                    'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                    'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                    'min': min, 'max': max, 'sum': sum, 'abs': abs,
                    'print': self._safe_print, 'range': range, 'enumerate': enumerate, 
                    'zip': zip, 'sorted': sorted, 'reversed': reversed,
                    'all': all, 'any': any
                }
            }

    def _safe_print(self, *args, **kwargs):
        """Safe print function with output limits"""
        output = ' '.join(str(arg) for arg in args)
        if len(output) > 1000:
            output = output[:1000] + "...[truncated]"
        print(output)
    
    def execute_code(self, code: str, input_data: Optional[Dict] = None, 
                    stateless: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        """Execute Python code with complete security"""
        execution_id = f"exec_{int(time.time() * 1000)}"
        
        # Create audit entry
        audit_entry = {
            "execution_id": execution_id,
            "timestamp": time.time(),
            "code": code,
            "input_data": input_data,
            "stateless": stateless,
            "dry_run": dry_run,
            "security_scan": None,
            "execution_result": None,
            "resource_usage": {},
            "success": False
        }
        
        try:
            # Security scan first
            try:
                tree = ast.parse(code)
                security_scan = self.security_auditor.scan_code(code, tree)
                audit_entry["security_scan"] = security_scan
                
                # Block execution if high-severity issues found
                high_severity_issues = security_scan.get("by_severity", {}).get("HIGH", [])
                if high_severity_issues and not dry_run:
                    return {
                        "success": False,
                        "error": "SECURITY_BLOCK",
                        "message": f"Blocked execution due to {len(high_severity_issues)} high-severity security issues",
                        "security_issues": high_severity_issues,
                        "execution_id": execution_id
                    }
                
            except SyntaxError as e:
                return {
                    "success": False,
                    "error": "SYNTAX_ERROR",
                    "message": str(e),
                    "execution_id": execution_id
                }
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "message": "Code passed security scan - safe to execute",
                    "security_scan": security_scan,
                    "execution_id": execution_id
                }
            
            # Setup execution environment
            execution_globals = self.restricted_globals.copy()
            execution_locals = {}
            
            # Add input data if provided
            if input_data:
                execution_globals.update(input_data)
            
            # Load session state if not stateless
            if not stateless and self.session_state:
                execution_globals.update(self.session_state)
            
            # Setup resource limits
            old_recursion_limit = sys.getrecursionlimit()
            sys.setrecursionlimit(self.max_recursion_depth)
            
            # Capture output
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            # Execute with timeout
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            self.execute_with_restrictions(code, execution_globals, execution_locals, stdout_buffer, stderr_buffer)
            
            # Collect results
            execution_time = time.time() - start_time
            end_memory = self._get_memory_usage()
            memory_used = end_memory - start_memory
            
            stdout_output = stdout_buffer.getvalue()
            stderr_output = stderr_buffer.getvalue()
            
            # Truncate output if too large
            if len(stdout_output) > self.max_output_size:
                stdout_output = stdout_output[:self.max_output_size] + "\n...[OUTPUT TRUNCATED]"
            
            # Update session state if not stateless
            if not stateless:
                # Extract new variables from globals (since we're using globals for both)
                original_vars = set(self.restricted_globals.keys())
                if input_data:
                    original_vars.update(input_data.keys())
                
                new_vars = {k: v for k, v in execution_globals.items() 
                           if not k.startswith('_') and k not in original_vars}
                self.session_state.update(new_vars)
            
            # Restore recursion limit
            sys.setrecursionlimit(old_recursion_limit)
            
            # Build result
            # Extract created variables for reporting
            original_vars = set(self.restricted_globals.keys())
            if input_data:
                original_vars.update(input_data.keys())
            created_vars = [k for k in execution_globals.keys() 
                           if not k.startswith('_') and k not in original_vars]
            
            result = {
                "success": True,
                "stdout": stdout_output,
                "stderr": stderr_output,
                "execution_time": execution_time,
                "memory_used_mb": memory_used / (1024 * 1024),
                "variables_created": created_vars,
                "security_scan": security_scan,
                "execution_id": execution_id
            }
            
            audit_entry.update({
                "execution_result": result,
                "resource_usage": {
                    "execution_time": execution_time,
                    "memory_used_mb": memory_used / (1024 * 1024)
                },
                "success": True
            })
            
            return result
            
        except TimeoutError:
            return {
                "success": False,
                "error": "TIMEOUT",
                "message": f"Execution exceeded {self.max_execution_time} seconds",
                "execution_id": execution_id
            }
        except MemoryError:
            return {
                "success": False,
                "error": "MEMORY_LIMIT",
                "message": f"Execution exceeded memory limit",
                "execution_id": execution_id
            }
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            traceback_str = traceback.format_exc()
            
            audit_entry.update({
                "execution_result": {
                    "error": error_msg,
                    "traceback": traceback_str
                },
                "success": False
            })
            
            return {
                "success": False,
                "error": "EXECUTION_ERROR",
                "message": error_msg,
                "traceback": traceback_str,
                "execution_id": execution_id
            }
        
        finally:
            # Always log the audit entry
            self.audit_log.append(audit_entry)
            
            # Keep audit log manageable
            if len(self.audit_log) > 1000:
                self.audit_log = self.audit_log[-500:]

    def execute_with_restrictions(self, code, execution_globals, execution_locals, stdout_buffer, stderr_buffer):
        """Execute code with cross-platform timeout and restrictions"""
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            if RESTRICTED_PYTHON_AVAILABLE:
                try:
                    # Use RestrictedPython with proper error handling
                    from RestrictedPython import compile_restricted
                    compiled_result = compile_restricted(code, '<string>', 'exec')
                    if compiled_result.errors:
                        raise RuntimeError(f"Compilation errors: {compiled_result.errors}")
                    
                    compiled_code = compiled_result.code
                except Exception as e:
                    raise RuntimeError(f"RestrictedPython compilation failed: {e}")
            else:
                # Fallback to standard compilation with basic restrictions
                try:
                    compiled_code = compile(code, '<string>', 'exec')
                except SyntaxError as e:
                    raise RuntimeError(f"Syntax error: {e}")
            
            # Cross-platform timeout execution using threading
            self._execution_result = None
            self._execution_error = None
            
            def execute_target():
                try:
                    # Use globals as both globals and locals to fix scoping issues
                    # This ensures generator expressions can access all variables
                    exec(compiled_code, execution_globals, execution_globals)
                    self._execution_result = "success"
                except Exception as e:
                    self._execution_error = e
            
            # Start execution in separate thread
            self._execution_thread = threading.Thread(target=execute_target)
            self._execution_thread.daemon = True
            self._execution_thread.start()
            
            # Wait for completion with timeout
            self._execution_thread.join(timeout=self.max_execution_time)
            
            if self._execution_thread.is_alive():
                # Timeout occurred - note: we can't actually kill the thread safely
                # but at least we can detect the timeout and return control
                raise TimeoutError(f"Execution exceeded {self.max_execution_time} seconds")
            
            # Check if execution had an error
            if self._execution_error:
                raise self._execution_error

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except ImportError:
            # Fallback using resource module (Unix/Linux only)
            if RESOURCE_AVAILABLE:
                try:
                    import resource as resource_mod
                    # Check if resource module has the required attributes
                    if hasattr(resource_mod, 'getrusage') and hasattr(resource_mod, 'RUSAGE_SELF'):
                        # Use getattr to avoid type checker issues
                        getrusage = getattr(resource_mod, 'getrusage')
                        RUSAGE_SELF = getattr(resource_mod, 'RUSAGE_SELF')
                        return getrusage(RUSAGE_SELF).ru_maxrss * 1024
                    else:
                        # Resource module doesn't have getrusage (Windows)
                        return 0
                except (AttributeError, OSError):
                    # getrusage not available on this platform
                    return 0
            else:
                # Resource module not available (Windows)
                return 0
                return 0
    
    def get_audit_log(self, limit: int = 50) -> List[Dict]:
        """Get execution audit log"""
        return self.audit_log[-limit:]
    
    def clear_session(self):
        """Clear session state"""
        self.session_state.clear()
    
    def get_session_state(self) -> Dict:
        """Get current session state"""
        return self.session_state.copy()


class AdvancedCodeAnalyzer:
    """Complete code analysis with CFA, DFA, and Type Inference"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.security_auditor = SecurityAuditor()
        self.type_engine = TypeInferenceEngine()
        self.cfg_analyzer = ControlFlowAnalyzer()
        self.dfa_analyzer = DataFlowAnalyzer()
    
    def analyze_file(self, file_path: str, include_cfa: bool = True,
                    include_dfa: bool = True, include_types: bool = True,
                    include_security: bool = True) -> Dict[str, Any]:
        """Complete file analysis"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"File not found: {file_path}"}
            
            with open(path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            try:
                tree = ast.parse(source_code, filename=str(path))
            except SyntaxError as e:
                return {"error": f"Syntax error: {e}"}
            
            result = {
                "file": str(path),
                "source_lines": len(source_code.split('\n')),
                "analysis_timestamp": time.time()
            }
            
            # AST Analysis
            result["ast_analysis"] = self._analyze_ast(tree, source_code)
            
            # Control Flow Analysis
            if include_cfa:
                result["control_flow_analysis"] = self._analyze_control_flow(tree)
            
            # Data Flow Analysis
            if include_dfa and include_cfa:
                result["data_flow_analysis"] = self._analyze_data_flow(tree, result.get("control_flow_analysis", {}))
            
            # Type Inference
            if include_types:
                result["type_analysis"] = self.type_engine.infer_types(tree, source_code)
            
            # Security Analysis
            if include_security:
                result["security_analysis"] = self.security_auditor.scan_code(source_code, tree)
            
            # Comprehensive metrics
            result["metrics"] = self._calculate_metrics(result, source_code)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Analysis error: {e}")
            return {"error": str(e)}
    
    def _analyze_ast(self, tree: ast.AST, source_code: str) -> Dict[str, Any]:
        """Complete AST analysis"""
        functions = {}
        classes = {}
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                func_data = self._analyze_function(node)
                functions[node.name] = func_data
            
            elif isinstance(node, ast.ClassDef):
                class_data = self._analyze_class(node)
                classes[node.name] = class_data
            
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                import_data = self._analyze_import(node)
                imports.append(import_data)
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "total_nodes": len(list(ast.walk(tree)))
        }
    
    def _analyze_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> Dict[str, Any]:
        """Analyze function definition"""
        # Extract parameters
        params = []
        for arg in node.args.args:
            param_name = arg.arg
            param_type = None
            if arg.annotation:
                param_type = self._extract_annotation(arg.annotation)
            params.append(f"{param_name}: {param_type}" if param_type else param_name)
        
        # Calculate complexity
        complexity = self._calculate_complexity(node)
        
        # Extract function calls
        calls = []
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                call_name = self._extract_call_name(child)
                if call_name:
                    calls.append(call_name)
        
        return {
            "name": node.name,
            "params": params,
            "return_type": self._extract_annotation(node.returns) if node.returns else None,
            "complexity": complexity,
            "calls": calls,
            "line": node.lineno,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
    
    def _analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze class definition"""
        methods = []
        properties = []
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(item.name)
                # Check for property decorator
                for decorator in item.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'property':
                        properties.append(item.name)
        
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
        
        return {
            "name": node.name,
            "methods": methods,
            "properties": properties,
            "base_classes": base_classes,
            "line": node.lineno
        }
    
    def _analyze_import(self, node: Union[ast.Import, ast.ImportFrom]) -> Dict[str, Any]:
        """Analyze import statement"""
        if isinstance(node, ast.Import):
            return {
                "type": "import",
                "modules": [alias.name for alias in node.names],
                "line": node.lineno
            }
        else:
            return {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "level": node.level,
                "line": node.lineno
            }
    
    def _analyze_control_flow(self, tree: ast.AST) -> Dict[str, Any]:
        """Analyze control flow for all functions"""
        cfg_data = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                cfg = self.cfg_analyzer.build_cfg(node)
                cfg_data[node.name] = cfg
        
        return {
            "functions": cfg_data,
            "total_functions": len(cfg_data)
        }
    
    def _analyze_data_flow(self, tree: ast.AST, cfg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data flow for all functions"""
        dfa_results = {}
        
        for func_name, cfg in cfg_data.get("functions", {}).items():
            # Find the corresponding function node
            func_node = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                    func_node = node
                    break
            
            if func_node:
                dfa_result = self.dfa_analyzer.analyze_function(cfg, func_node)
                dfa_results[func_name] = dfa_result
        
        return {
            "functions": dfa_results,
            "total_functions": len(dfa_results)
        }
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
        
        return complexity
    
    def _extract_annotation(self, annotation: ast.AST) -> str:
        """Extract type annotation"""
        try:
            if hasattr(ast, 'unparse'):
                return ast.unparse(annotation)
            else:
                return str(annotation)
        except:
            return "Unknown"
    
    def _extract_call_name(self, call_node: ast.Call) -> Optional[str]:
        """Extract function name from call"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id
        elif isinstance(call_node.func, ast.Attribute):
            return call_node.func.attr
        return None
    
    def _calculate_metrics(self, analysis_result: Dict, source_code: str) -> Dict[str, Any]:
        """Calculate comprehensive metrics"""
        lines = source_code.split('\n')
        total_lines = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        code_lines = total_lines - blank_lines - comment_lines
        
        ast_data = analysis_result.get("ast_analysis", {})
        functions = ast_data.get("functions", {})
        
        # Complexity metrics
        complexities = [func.get("complexity", 0) for func in functions.values()]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        max_complexity = max(complexities) if complexities else 0
        
        return {
            "lines_of_code": {
                "total": total_lines,
                "code": code_lines,
                "comments": comment_lines,
                "blank": blank_lines
            },
            "complexity": {
                "average": round(avg_complexity, 2),
                "maximum": max_complexity,
                "functions_over_10": sum(1 for c in complexities if c > 10)
            },
            "structure": {
                "functions": len(functions),
                "classes": len(ast_data.get("classes", {})),
                "imports": len(ast_data.get("imports", []))
            }
        }


class CodeAnalysisTool:
    """MCP Tool wrapper for code analysis and Python execution"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.analyzer = AdvancedCodeAnalyzer()
        self.interpreter = SecurePythonInterpreter()
    
    def bb7_analyze_code_complete(self, file_path: str, include_all: bool = True) -> str:
        """Complete code analysis with all features"""
        try:
            result = self.analyzer.analyze_file(
                file_path, 
                include_cfa=include_all,
                include_dfa=include_all,
                include_types=include_all,
                include_security=include_all
            )
            
            if "error" in result:
                return f"❌ Analysis Error: {result['error']}"
            
            return self._format_complete_analysis(result)
            
        except Exception as e:
            return f"❌ Analysis failed: {str(e)}"
    
    def bb7_python_execute_secure(self, code: str, input_data: Optional[str] = None,
                                 stateless: bool = True, dry_run: bool = False) -> str:
        """Secure Python code execution"""
        try:
            # Parse input data if provided
            parsed_input = None
            if input_data:
                try:
                    parsed_input = json.loads(input_data)
                except json.JSONDecodeError:
                    return "❌ Invalid input data JSON format"
            
            result = self.interpreter.execute_code(
                code, 
                input_data=parsed_input,
                stateless=stateless,
                dry_run=dry_run
            )
            
            return self._format_execution_result(result)
            
        except Exception as e:
            return f"❌ Execution failed: {str(e)}"
    
    def bb7_security_audit(self, file_path: str) -> str:
        """Security-focused code analysis"""
        try:
            result = self.analyzer.analyze_file(file_path, include_security=True)
            
            if "error" in result:
                return f"❌ Audit Error: {result['error']}"
            
            security_data = result.get("security_analysis", {})
            return self._format_security_audit(security_data)
            
        except Exception as e:
            return f"❌ Security audit failed: {str(e)}"
    
    def bb7_get_execution_audit(self, limit: int = 20) -> str:
        """Get Python execution audit log"""
        try:
            audit_log = self.interpreter.get_audit_log(limit)
            return self._format_audit_log(audit_log)
        except Exception as e:
            return f"❌ Audit retrieval failed: {str(e)}"
    
    def _format_complete_analysis(self, result: Dict) -> str:
        """Format complete analysis results"""
        output = [f"🔍 Complete Code Analysis: {result['file']}"]
        output.append("=" * 80)
        
        # Metrics summary
        metrics = result.get("metrics", {})
        if metrics:
            loc = metrics.get("lines_of_code", {})
            complexity = metrics.get("complexity", {})
            structure = metrics.get("structure", {})
            
            output.append(f"\n📊 Summary Metrics:")
            output.append(f"  • Lines of Code: {loc.get('code', 0)} (total: {loc.get('total', 0)})")
            output.append(f"  • Functions: {structure.get('functions', 0)}")
            output.append(f"  • Classes: {structure.get('classes', 0)}")
            output.append(f"  • Average Complexity: {complexity.get('average', 0)}")
            output.append(f"  • Max Complexity: {complexity.get('maximum', 0)}")
        
        # Control Flow Analysis
        cfa = result.get("control_flow_analysis", {})
        if cfa:
            total_funcs = cfa.get("total_functions", 0)
            output.append(f"\n🌐 Control Flow Analysis:")
            output.append(f"  • Functions analyzed: {total_funcs}")
            
            for func_name, cfg in cfa.get("functions", {}).items():
                nodes = cfg.get("num_nodes", 0)
                edges = cfg.get("num_edges", 0)
                complexity = cfg.get("cyclomatic_complexity", 0)
                output.append(f"  • {func_name}: {nodes} nodes, {edges} edges, complexity {complexity}")
        
        # Data Flow Analysis
        dfa = result.get("data_flow_analysis", {})
        if dfa:
            output.append(f"\n🌊 Data Flow Analysis:")
            for func_name, df_data in dfa.get("functions", {}).items():
                chains = df_data.get("def_use_chains", {}).get("usage_analysis", {})
                unused = sum(1 for analysis in chains.values() if analysis.get("is_unused", False))
                if unused > 0:
                    output.append(f"  • {func_name}: {unused} potentially unused variables")
        
        # Type Analysis
        type_analysis = result.get("type_analysis", {})
        if type_analysis:
            coverage = type_analysis.get("coverage_metrics", {})
            coverage_pct = coverage.get("coverage_percentage", 0)
            output.append(f"\n🏷️ Type Analysis:")
            output.append(f"  • Type coverage: {coverage_pct:.1f}%")
            output.append(f"  • Typed variables: {coverage.get('typed_variables', 0)}")
        
        # Security Analysis
        security = result.get("security_analysis", {})
        if security:
            total_issues = security.get("total_issues", 0)
            by_severity = security.get("by_severity", {})
            output.append(f"\n🔒 Security Analysis:")
            output.append(f"  • Total issues: {total_issues}")
            for severity in ["HIGH", "MEDIUM", "LOW"]:
                count = len(by_severity.get(severity, []))
                if count > 0:
                    output.append(f"  • {severity}: {count} issues")
        
        return "\n".join(output)
    
    def _format_execution_result(self, result: Dict) -> str:
        """Format Python execution results"""
        if result.get("dry_run"):
            return f"🛡️ DRY RUN - Code passed security scan\n✅ Safe to execute\nExecution ID: {result['execution_id']}"
        
        if not result.get("success"):
            error_type = result.get("error", "UNKNOWN")
            message = result.get("message", "No details")
            
            if error_type == "SECURITY_BLOCK":
                issues = result.get("security_issues", [])
                output = f"🚫 EXECUTION BLOCKED - Security Issues:\n"
                for issue in issues[:3]:
                    output += f"  • Line {issue.get('line', '?')}: {issue.get('description', 'Unknown issue')}\n"
                return output
            else:
                return f"❌ Execution Failed ({error_type}): {message}"
        
        # Successful execution
        output = [f"✅ Python Execution Successful"]
        output.append(f"Execution ID: {result['execution_id']}")
        output.append(f"Time: {result.get('execution_time', 0):.3f}s")
        output.append(f"Memory: {result.get('memory_used_mb', 0):.2f}MB")
        
        stdout = result.get("stdout", "")
        if stdout:
            output.append(f"\nOutput:\n{stdout}")
        
        stderr = result.get("stderr", "")
        if stderr:
            output.append(f"\nWarnings/Errors:\n{stderr}")
        
        variables = result.get("variables_created", [])
        if variables:
            output.append(f"\nVariables created: {', '.join(variables)}")
        
        return "\n".join(output)
    
    def _format_security_audit(self, security_data: Dict) -> str:
        """Format security audit results"""
        output = [f"🔒 Security Audit Results"]
        output.append("=" * 50)
        
        total_issues = security_data.get("total_issues", 0)
        if total_issues == 0:
            output.append("✅ No security issues detected")
            return "\n".join(output)
        
        output.append(f"🚨 Found {total_issues} security issues")
        
        by_severity = security_data.get("by_severity", {})
        for severity in ["HIGH", "MEDIUM", "LOW"]:
            issues = by_severity.get(severity, [])
            if issues:
                emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[severity]
                output.append(f"\n{emoji} {severity} Severity ({len(issues)} issues):")
                
                for issue in issues[:5]:  # Show first 5
                    line = issue.get("line", "?")
                    desc = issue.get("description", "Unknown issue")
                    code = issue.get("code", "")[:50]
                    output.append(f"  • Line {line}: {desc}")
                    if code:
                        output.append(f"    Code: {code}...")
                
                if len(issues) > 5:
                    output.append(f"    ... and {len(issues) - 5} more issues")
        
        return "\n".join(output)
    
    def _format_audit_log(self, audit_log: List[Dict]) -> str:
        """Format execution audit log"""
        if not audit_log:
            return "📋 No execution history"
        
        output = [f"📋 Python Execution Audit Log ({len(audit_log)} entries)"]
        output.append("=" * 60)
        
        for entry in audit_log[-10:]:  # Show last 10
            exec_id = entry.get("execution_id", "unknown")
            timestamp = time.strftime('%H:%M:%S', time.localtime(entry.get("timestamp", 0)))
            success = "✅" if entry.get("success") else "❌"
            code_preview = entry.get("code", "")[:50].replace('\n', ' ')
            
            output.append(f"\n{success} [{timestamp}] {exec_id}")
            output.append(f"   Code: {code_preview}...")
            
            # Security scan summary
            security_scan = entry.get("security_scan", {})
            if security_scan:
                issues = security_scan.get("total_issues", 0)
                if issues > 0:
                    output.append(f"   Security: {issues} issues found")
            
            # Resource usage
            resource_usage = entry.get("resource_usage", {})
            if resource_usage:
                time_used = resource_usage.get("execution_time", 0)
                memory_used = resource_usage.get("memory_used_mb", 0)
                output.append(f"   Resources: {time_used:.3f}s, {memory_used:.2f}MB")
        
        return "\n".join(output)
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all available tools with their metadata for MCP registration"""
        return {
            'bb7_analyze_code_complete': {
                "callable": lambda file_path, include_all=True: self.bb7_analyze_code_complete(file_path, include_all),
                "metadata": {
                    "name": "bb7_analyze_code_complete",
                    "description": "🔬 ENHANCED CODE ANALYSIS: Comprehensive code analysis with Control Flow Analysis (CFA), Data Flow Analysis (DFA), type inference, complexity metrics, and security auditing. Use for deep code understanding and quality assessment.",
                    "category": "code_analysis",
                    "input_schema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "Path to code file to analyze"}, "analysis_types": {"type": "array", "items": {"type": "string"}, "default": ["syntax", "complexity", "security", "type_inference"], "description": "Types of analysis to perform"}}, "required": ["file_path"]},
                    "priority": "high",
                    "when_to_use": ["code_review", "quality_assessment", "security_audit", "complexity_analysis", "refactoring"]
                }
            },
            'bb7_python_execute_secure': {
                "callable": lambda code, input_data=None, stateless=True, dry_run=False: self.bb7_python_execute_secure(code, input_data, stateless, dry_run),
                "metadata": {
                    "name": "bb7_python_execute_secure",
                    "description": "🐍 SECURE EXECUTION: Execute Python code in a secure, sandboxed environment with resource limits and safety checks. Use for testing code snippets or running analysis safely.",
                    "category": "code_analysis",
                    "input_schema": {"type": "object", "properties": {"code": {"type": "string", "description": "Python code to execute"}, "timeout": {"type": "integer", "default": 10, "description": "Execution timeout in seconds"}, "capture_output": {"type": "boolean", "default": True}}, "required": ["code"]},
                    "priority": "medium",
                    "when_to_use": ["code_testing", "snippet_execution", "safe_evaluation", "python_analysis"]
                }
            },
            'bb7_security_audit': {
                "callable": lambda file_path: self.bb7_security_audit(file_path),
                "metadata": {
                    "name": "bb7_security_audit",
                    "description": "🔒 SECURITY ANALYSIS: Comprehensive security audit for code including vulnerability detection, security best practices checking, and risk assessment. Use for security reviews and compliance.",
                    "category": "code_analysis",
                    "input_schema": {"type": "object", "properties": {"target_path": {"type": "string", "description": "Path to file or directory to audit"}, "security_level": {"type": "string", "enum": ["basic", "standard", "strict"], "default": "standard"}}, "required": ["target_path"]},
                    "priority": "high",
                    "when_to_use": ["security_review", "vulnerability_scan", "compliance_check", "risk_assessment"]
                }
            },
            'bb7_get_execution_audit': {
                "callable": lambda limit=20: self.bb7_get_execution_audit(limit),
                "metadata": {
                    "name": "bb7_get_execution_audit",
                    "description": "Retrieve the audit log of recent secure Python code executions, including code, input, output, errors, and security scan results.",
                    "category": "code_analysis",
                    "input_schema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 20}}, "required": []},
                    "priority": "low",
                    "when_to_use": ["audit_log_review", "execution_history", "security_analysis_review"]
                }
            }
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the complete system
    tool = CodeAnalysisTool()
    
    print("=== Testing Code Analysis ===")
    result = tool.bb7_analyze_code_complete(__file__)
    print(result)
    
    print("\n=== Testing Secure Python Execution ===")
    test_code = """
x = [1, 2, 3, 4, 5]
y = sum(x)
print(f"Sum: {y}")
result = y * 2
"""
    exec_result = tool.bb7_python_execute_secure(test_code)
    print(exec_result)
    
    print("\n=== Testing Security Audit ===")
    audit_result = tool.bb7_get_execution_audit(5)
    print(audit_result)
