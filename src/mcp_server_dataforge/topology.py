"""
Topology Module - Automatic table dependency resolution
"""
from typing import Dict, List, Set, Tuple
from sqlalchemy import inspect


class TopologySorter:
    """Handles topological sorting of database tables based on foreign key dependencies"""
    
    def __init__(self, inspector):
        """
        Initialize with SQLAlchemy inspector
        
        Args:
            inspector: SQLAlchemy inspector instance
        """
        self.inspector = inspector
        self.dependency_graph = self._build_dependency_graph()
    
    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Build dependency graph from foreign key relationships
        
        Returns:
            Dictionary mapping table names to sets of tables they depend on
        """
        graph = {}
        tables = self.inspector.get_table_names()
        
        # Initialize all tables with empty dependencies
        for table in tables:
            graph[table] = set()
        
        # Add dependencies based on foreign keys
        for table in tables:
            foreign_keys = self.inspector.get_foreign_keys(table)
            for fk in foreign_keys:
                # Each foreign key creates a dependency on the referenced table
                referred_table = fk['referred_table']
                if referred_table in graph:
                    graph[table].add(referred_table)
        
        return graph
    
    def get_dependencies(self, table_name: str) -> Set[str]:
        """
        Get direct dependencies for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Set of table names that this table depends on
        """
        return self.dependency_graph.get(table_name, set())
    
    def get_all_dependencies(self, table_name: str) -> Set[str]:
        """
        Get all dependencies (direct and indirect) for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Set of all table names that this table depends on
        """
        all_deps = set()
        visited = set()
        
        def _collect_deps(table: str):
            if table in visited:
                return
            visited.add(table)
            for dep in self.get_dependencies(table):
                all_deps.add(dep)
                _collect_deps(dep)
        
        _collect_deps(table_name)
        return all_deps
    
    def get_dependents(self, table_name: str) -> Set[str]:
        """
        Get all tables that depend on this table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Set of table names that depend on this table
        """
        dependents = set()
        for table, deps in self.dependency_graph.items():
            if table_name in deps:
                dependents.add(table)
        return dependents
    
    def topological_sort(self) -> List[str]:
        """
        Perform topological sort on the dependency graph
        
        Returns:
            List of table names in dependency order (parents before children)
            
        Raises:
            ValueError: If the graph contains cycles
        """
        # Kahn's algorithm for topological sorting
        in_degree = {table: len(deps) for table, deps in self.dependency_graph.items()}
        queue = [table for table, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Sort queue for deterministic output
            queue.sort()
            node = queue.pop(0)
            result.append(node)
            
            # Find all tables that depend on this node
            for table in self.get_dependents(node):
                in_degree[table] -= 1
                if in_degree[table] == 0:
                    queue.append(table)
        
        # Check for cycles
        if len(result) != len(self.dependency_graph):
            # Find the cycle
            cycle = self._find_cycle()
            raise ValueError(
                f"Circular dependency detected in database schema. "
                f"Cycle: {' -> '.join(cycle)}"
            )
        
        return result
    
    def _find_cycle(self) -> List[str]:
        """
        Find a cycle in the dependency graph using DFS
        
        Returns:
            List of table names forming a cycle
        """
        visited = set()
        rec_stack = set()
        path = []
        
        def _dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.get_dependencies(node):
                if neighbor not in visited:
                    if _dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
            
            rec_stack.remove(node)
            path.pop()
            return False
        
        for table in self.dependency_graph:
            if table not in visited:
                if _dfs(table):
                    return path
        
        return []
    
    def get_dependency_levels(self) -> Dict[int, List[str]]:
        """
        Group tables by their dependency level
        
        Returns:
            Dictionary mapping levels to lists of tables at that level
            Level 0: tables with no dependencies
            Level 1: tables that depend only on level 0 tables
            etc.
        """
        sorted_tables = self.topological_sort()
        levels = {}
        table_levels = {}
        
        # Calculate level for each table
        for table in sorted_tables:
            deps = self.get_dependencies(table)
            if not deps:
                table_levels[table] = 0
            else:
                max_dep_level = max(table_levels.get(dep, 0) for dep in deps)
                table_levels[table] = max_dep_level + 1
        
        # Group tables by level
        for table, level in table_levels.items():
            if level not in levels:
                levels[level] = []
            levels[level].append(table)
        
        return levels
    
    def visualize_dependencies(self) -> str:
        """
        Create a text-based visualization of the dependency graph
        
        Returns:
            String representation of the dependency graph
        """
        lines = ["Database Dependency Graph:", "=" * 60]
        
        sorted_tables = self.topological_sort()
        
        for table in sorted_tables:
            deps = self.get_dependencies(table)
            if deps:
                lines.append(f"{table} <- {', '.join(sorted(deps))}")
            else:
                lines.append(f"{table} (no dependencies)")
        
        return "\n".join(lines)
    
    def validate_no_self_references(self) -> Tuple[bool, List[str]]:
        """
        Check for tables that reference themselves
        
        Returns:
            Tuple of (is_valid, list_of_tables_with_self_references)
        """
        self_refs = []
        
        for table, deps in self.dependency_graph.items():
            if table in deps:
                self_refs.append(table)
        
        return (len(self_refs) == 0, self_refs)


def get_table_order(inspector) -> List[str]:
    """
    Convenience function to get tables in dependency order
    
    Args:
        inspector: SQLAlchemy inspector instance
        
    Returns:
        List of table names in dependency order
    """
    sorter = TopologySorter(inspector)
    return sorter.topological_sort()


def print_dependency_tree(inspector) -> str:
    """
    Convenience function to print dependency tree
    
    Args:
        inspector: SQLAlchemy inspector instance
        
    Returns:
        String representation of dependency tree
    """
    sorter = TopologySorter(inspector)
    return sorter.visualize_dependencies()
