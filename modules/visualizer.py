import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import random

def display_thoughts(thoughts):
    """Display thoughts in a structured text format"""
    for i, thought in enumerate(thoughts):
        thought_type = thought.get('type', 'standard')
        
        # Different styling based on thought type
        if thought_type == 'analytical':
            
            color = "blue"
        elif thought_type == 'creative':
            
            color = "purple"
        elif thought_type == 'evaluative':
            
            color = "orange"
        elif thought_type == 'reflective':
            
            color = "green"
        else:
            
            color = "gray"
        
        # Display thought with styling
        st.markdown(
            f"""
            <div class="thought-bubble" style="border-left: 5px solid {color};">
                <div class="thought-header">
                    
                    <span class="thought-number">Thought {i+1}</span>
                </div>
                <div class="thought-content">
                    {thought['text']}
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )

def create_thought_graph(thoughts):
    """Create a graph representation of thoughts"""
    G = nx.DiGraph()
    
    # Add nodes for each thought
    for i, thought in enumerate(thoughts):
        # Truncate text for display
        display_text = thought['text']
        if len(display_text) > 100:
            display_text = display_text[:97] + "..."
        
        G.add_node(i, 
                  text=display_text,
                  full_text=thought['text'],
                  type=thought.get('type', 'standard'))
    
    # Add basic linear connections
    for i in range(len(thoughts) - 1):
        G.add_edge(i, i + 1, weight=1)
    
    # Add some non-linear connections based on keyword similarity
    # This is a simplified approach - in a real implementation, 
    # you would use semantic similarity or other NLP techniques
    keywords = ['decision', 'option', 'alternative', 'consequence', 
                'ethical', 'value', 'principle', 'creative', 'idea']
    
    for i in range(len(thoughts)):
        for j in range(len(thoughts)):
            if i != j and abs(i - j) > 1:  # Skip adjacent nodes
                # Check if they share keywords
                text_i = thoughts[i]['text'].lower()
                text_j = thoughts[j]['text'].lower()
                
                for keyword in keywords:
                    if keyword in text_i and keyword in text_j:
                        # Add a weaker connection
                        G.add_edge(i, j, weight=0.5)
                        break
    
    return G

def display_thought_graph(G):
    """Visualize thought graph using Plotly"""
    # Create a better layout than default
    pos = nx.spring_layout(G, seed=42)
    
    # Create edges
    edge_x = []
    edge_y = []
    edge_traces = []
    
    # Create separate traces for different weight edges
    for weight in [0.5, 1]:
        x, y = [], []
        for edge in G.edges(data=True):
            if edge[2]['weight'] == weight:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                x.extend([x0, x1, None])
                y.extend([y0, y1, None])
        
        width = 1 if weight == 0.5 else 2
        opacity = 0.5 if weight == 0.5 else 1
        
        edge_trace = go.Scatter(
            x=x, y=y,
            line=dict(width=width, color='#888'),
            opacity=opacity,
            hoverinfo='none',
            mode='lines')
        
        edge_traces.append(edge_trace)
    
    # Create nodes
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(G.nodes[node]['text'])
        
        # Color based on thought type
        node_type = G.nodes[node]['type']
        if node_type == 'analytical':
            node_color.append('#1f77b4')  # blue
        elif node_type == 'creative':
            node_color.append('#9467bd')  # purple
        elif node_type == 'evaluative':
            node_color.append('#ff7f0e')  # orange
        elif node_type == 'reflective':
            node_color.append('#2ca02c')  # green
        else:
            node_color.append('#7f7f7f')  # gray
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            color=node_color,
            size=15,
            line=dict(width=2, color='white')
        )
    )
    
    fig = go.Figure(
    data=edge_traces + [node_trace],
    layout=go.Layout(
        title=dict(
            text='Thought Process Visualization',
            font=dict(size=16)
        ),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600,
        clickmode='event+select'
    )
)

    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display legend
    st.markdown("""
    <div style="display: flex; justify-content: center; flex-wrap: wrap; margin-top: 10px;">
        <div style="margin: 5px 15px;"><span style="color: #1f77b4;">●</span> Analytical</div>
        <div style="margin: 5px 15px;"><span style="color: #9467bd;">●</span> Creative</div>
        <div style="margin: 5px 15px;"><span style="color: #ff7f0e;">●</span> Evaluative</div>
        <div style="margin: 5px 15px;"><span style="color: #2ca02c;">●</span> Reflective</div>
        <div style="margin: 5px 15px;"><span style="color: #7f7f7f;">●</span> Standard</div>
    </div>
    """, unsafe_allow_html=True)
