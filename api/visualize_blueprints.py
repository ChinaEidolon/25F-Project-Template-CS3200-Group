"""
Flask Blueprint Visualizer (Static Analysis)
Parses your Python files to extract blueprint structure without running the app.

Usage: python visualize_blueprints.py
"""

import re
import os
from pathlib import Path

# Configuration - paths relative to this script
ROUTE_FILES = [
    ("members", "backend/members/member_routes.py", "/members"),
    ("managers", "backend/manager/manager_routes.py", "/managers"),
    ("nutritionists", "backend/nutritionists/nutritionist_routes.py", "/nutritionists"),
    ("trainers", "backend/trainer/trainer_routes.py", "/trainers"),
]


def extract_routes_from_file(filepath):
    """Extract route definitions from a Python file"""
    routes = []
    
    if not os.path.exists(filepath):
        return routes
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find all @blueprint.route decorators
    # Pattern matches: @name.route('/path', methods=['GET', 'POST'])
    pattern = r"@\w+\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)"
    
    # Also find the function name that follows
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        match = re.search(pattern, line)
        if match:
            route_path = match.group(1)
            methods_str = match.group(2)
            
            # Parse methods
            if methods_str:
                methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
            else:
                methods = ['GET']
            
            # Find the function name (next line starting with 'def')
            func_name = "unknown"
            for j in range(i + 1, min(i + 5, len(lines))):
                func_match = re.match(r'\s*def\s+(\w+)\s*\(', lines[j])
                if func_match:
                    func_name = func_match.group(1)
                    break
            
            routes.append({
                'path': route_path,
                'methods': methods,
                'function': func_name
            })
    
    return routes


def print_header():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    🏗️  FLASK BLUEPRINT STRUCTURE                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)


def visualize_blueprints():
    print_header()
    
    all_routes = {}
    total_routes = 0
    method_counts = {'GET': 0, 'POST': 0, 'PUT': 0, 'DELETE': 0}
    
    for bp_name, filepath, prefix in ROUTE_FILES:
        routes = extract_routes_from_file(filepath)
        all_routes[bp_name] = {'prefix': prefix, 'routes': routes}
        total_routes += len(routes)
        
        print(f"╭{'─' * 68}╮")
        print(f"│ 📦 Blueprint: {bp_name.upper():<52} │")
        print(f"│    URL Prefix: {prefix:<51} │")
        print(f"│    File: {filepath:<57} │")
        print(f"╰{'─' * 68}╯")
        
        if not routes:
            print("   (No routes found)\n")
            continue
        
        # Sort routes by path
        routes = sorted(routes, key=lambda x: x['path'])
        
        for route in routes:
            full_path = prefix + route['path']
            methods_str = ', '.join(sorted(route['methods']))
            
            # Method icons
            icons = []
            for m in sorted(route['methods']):
                if m == 'GET':
                    icons.append('🟢')
                    method_counts['GET'] += 1
                elif m == 'POST':
                    icons.append('🟡')
                    method_counts['POST'] += 1
                elif m == 'PUT':
                    icons.append('🔵')
                    method_counts['PUT'] += 1
                elif m == 'DELETE':
                    icons.append('🔴')
                    method_counts['DELETE'] += 1
            
            icon_str = ' '.join(icons)
            
            print(f"   {icon_str} [{methods_str:^15}] {full_path}")
            print(f"      └── {route['function']}()")
        
        print()
    
    # Summary
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                           📊 SUMMARY                                 ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print(f"   Total Blueprints: {len(ROUTE_FILES)}")
    print(f"   Total Routes: {total_routes}")
    
    print("\n   Routes per Blueprint:")
    for bp_name, data in all_routes.items():
        count = len(data['routes'])
        bar = '█' * count
        print(f"      • {bp_name:<15}: {bar} ({count})")
    
    print("\n   HTTP Methods Distribution:")
    print(f"      🟢 GET    : {'█' * method_counts['GET']} ({method_counts['GET']})")
    print(f"      🟡 POST   : {'█' * method_counts['POST']} ({method_counts['POST']})")
    print(f"      🔵 PUT    : {'█' * method_counts['PUT']} ({method_counts['PUT']})")
    print(f"      🔴 DELETE : {'█' * method_counts['DELETE']} ({method_counts['DELETE']})")
    print()


def generate_ascii_tree():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                        🌳 ASCII TREE VIEW                            ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print("Flask App (api/)")
    print("│")
    
    for i, (bp_name, filepath, prefix) in enumerate(ROUTE_FILES):
        is_last_bp = (i == len(ROUTE_FILES) - 1)
        bp_prefix = "└── " if is_last_bp else "├── "
        connector = "    " if is_last_bp else "│   "
        
        print(f"{bp_prefix}📦 {bp_name}/ (prefix: {prefix})")
        
        routes = extract_routes_from_file(filepath)
        routes = sorted(routes, key=lambda x: x['path'])
        
        for j, route in enumerate(routes):
            is_last_route = (j == len(routes) - 1)
            route_prefix = "└── " if is_last_route else "├── "
            methods_str = ','.join(sorted(route['methods']))
            full_path = prefix + route['path']
            
            print(f"{connector}{route_prefix}[{methods_str}] {full_path}")
    
    print()


def generate_mermaid_diagram():
    """Generate a Mermaid.js diagram that can be rendered on GitHub or mermaid.live"""
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                    📈 MERMAID DIAGRAM CODE                           ║
║  (paste this into https://mermaid.live or a GitHub markdown file)    ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    print("```mermaid")
    print("flowchart TB")
    print("    subgraph Flask[\"🏠 Flask Application\"]")
    print("        APP[\"backend_app.py\"]")
    print("    end")
    print()
    
    for bp_name, filepath, prefix in ROUTE_FILES:
        safe_name = bp_name.replace("-", "_")
        print(f"    subgraph {safe_name}[\"{bp_name.upper()} Blueprint\"]")
        print(f"        {safe_name}_prefix[\"{prefix}/*\"]")
        
        routes = extract_routes_from_file(filepath)
        for i, route in enumerate(routes[:5]):  # Limit to 5 routes per blueprint for readability
            full_path = prefix + route['path']
            methods = '/'.join(route['methods'])
            print(f"        {safe_name}_{i}[\"{methods}: {full_path}\"]")
        
        if len(routes) > 5:
            print(f"        {safe_name}_more[\"... +{len(routes) - 5} more routes\"]")
        
        print("    end")
        print(f"    APP --> {safe_name}_prefix")
        print()
    
    print("```")
    print()


if __name__ == "__main__":
    visualize_blueprints()
    generate_ascii_tree()
    generate_mermaid_diagram()
