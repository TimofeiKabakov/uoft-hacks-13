"""
Render LangGraph Structure Visualization

This script generates a visual diagram of the Community Spark agent workflow,
showing the nodes (auditor, impact analyst, compliance sentry) and the
conditional routing logic between them.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.graph import build_graph


def render_graph():
    """
    Render the LangGraph workflow as an image.
    
    Uses LangGraph's built-in visualization capabilities to generate
    a diagram showing:
    - Agent nodes (auditor, impact, compliance)
    - Conditional edges (based on auditor_score)
    - Start and end points
    """
    # Build the graph
    print("Building LangGraph workflow...")
    graph = build_graph()
    
    # Create artifacts directory if it doesn't exist
    artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    
    output_path = artifacts_dir / "graph.png"
    
    try:
        # Try using LangGraph's built-in visualization
        print("Attempting to render graph using LangGraph's draw_mermaid_png...")
        
        # Get the graph structure
        graph_data = graph.get_graph()
        
        # Try to draw using mermaid (LangGraph's preferred method)
        try:
            from langchain_core.runnables.graph import MermaidDrawMethod
            png_bytes = graph_data.draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )
            
            with open(output_path, "wb") as f:
                f.write(png_bytes)
            
            print(f"✅ Graph rendered successfully using Mermaid!")
            print(f"📁 Output: {output_path}")
            return True
            
        except ImportError:
            print("⚠️ Mermaid method not available, trying alternative...")
    
    except Exception as e:
        print(f"⚠️ LangGraph native visualization failed: {e}")
    
    # Fallback: Generate simple graphviz diagram
    print("Using Graphviz fallback...")
    try:
        import graphviz
        
        dot = graphviz.Digraph(comment='Community Spark Agent Flow')
        dot.attr(rankdir='TB')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        
        # Add nodes
        dot.node('START', 'START', shape='circle', fillcolor='lightgreen')
        dot.node('auditor', 'Auditor Agent\n(Financial Analysis)', fillcolor='#87CEEB')
        dot.node('impact', 'Impact Analyst\n(Community Multiplier)', fillcolor='#90EE90')
        dot.node('compliance', 'Compliance Sentry\n(Final Decision)', fillcolor='#FFB6C1')
        dot.node('END', 'END', shape='doublecircle', fillcolor='#FFD700')
        
        # Add edges
        dot.edge('START', 'auditor', label='Initialize')
        
        # Conditional edge from auditor
        dot.edge('auditor', 'impact', label='if score < 60\n(needs community boost)', color='blue')
        dot.edge('auditor', 'compliance', label='if score >= 60\n(sufficient baseline)', color='green')
        
        # Impact always goes to compliance
        dot.edge('impact', 'compliance', label='Apply multiplier')
        
        # Compliance to end
        dot.edge('compliance', 'END', label='APPROVE/DENY/REFER')
        
        # Render to PNG
        dot.render(output_path.with_suffix(''), format='png', cleanup=True)
        
        print(f"✅ Graph rendered successfully using Graphviz!")
        print(f"📁 Output: {output_path}")
        
        # Print graph info
        print("\n📊 Graph Structure:")
        print("  Nodes: START → auditor → [impact] → compliance → END")
        print("  Conditional Logic: auditor_score < 60 routes through impact_analyst")
        print("  Decision Flow: compliance_sentry makes final APPROVE/DENY/REFER decision")
        
        return True
        
    except ImportError:
        print("❌ Error: graphviz package not installed")
        print("Install with: pip install graphviz")
        print("Note: You may also need to install Graphviz system package:")
        print("  - macOS: brew install graphviz")
        print("  - Ubuntu: sudo apt-get install graphviz")
        print("  - Windows: download from https://graphviz.org/download/")
        return False
    
    except Exception as e:
        print(f"❌ Error rendering graph: {e}")
        return False


def print_graph_text():
    """Print a text representation of the graph structure"""
    print("\n" + "="*60)
    print("COMMUNITY SPARK AGENT WORKFLOW")
    print("="*60)
    print("""
    START
      ↓
    [Auditor Agent]
    - Analyzes bank_data (revenue, volatility, NSF, debt)
    - Outputs: auditor_score (1-100), flags, summary
      ↓
      ├─→ (if score < 60) → [Impact Analyst]
      │                      - Evaluates community metrics
      │                      - Outputs: community_multiplier (1.0-1.6)
      │                      ↓
      └─→ (if score >= 60) ─┘
      ↓
    [Compliance Sentry]
    - Combines auditor_score × community_multiplier
    - Applies policy guardrails
    - Outputs: APPROVE / DENY / REFER
      ↓
    END
    """)
    print("="*60 + "\n")


if __name__ == "__main__":
    print("="*60)
    print("Community Spark - Graph Visualization Tool")
    print("="*60 + "\n")
    
    # Print text representation
    print_graph_text()
    
    # Render visual diagram
    success = render_graph()
    
    if success:
        print("\n✨ Done! View the graph diagram at artifacts/graph.png")
    else:
        print("\n⚠️ Could not generate image, but text representation shown above")
    
    sys.exit(0 if success else 1)

