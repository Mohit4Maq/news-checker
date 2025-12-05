#!/usr/bin/env python3
"""
Test script to verify visualizations work
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

print("🧪 Testing Visualization Components\n")
print("=" * 80)

# Sample data
categories = ['Factual Accuracy', 'Source Diversity', 'Investigative Depth', 
              'Balance', 'Transparency', 'Citizen Focus']
article_scores = [20, 15, 18, 12, 25, 22]
world_standards = [90, 85, 88, 87, 90, 85]

# Test bar chart
print("1️⃣  Testing Bar Chart...")
fig = go.Figure()
fig.add_trace(go.Bar(name='This Article', x=categories, y=article_scores, marker_color='#ff6b6b'))
fig.add_trace(go.Bar(name='World Standard', x=categories, y=world_standards, marker_color='#4ecdc4'))
fig.update_layout(title='Test Chart', barmode='group')
print("   ✅ Bar chart created successfully")

# Test radar chart
print("2️⃣  Testing Radar Chart...")
fig2 = go.Figure()
fig2.add_trace(go.Scatterpolar(r=article_scores + [article_scores[0]], 
                                theta=categories + [categories[0]], 
                                fill='toself', name='This Article'))
print("   ✅ Radar chart created successfully")

# Test pie chart
print("3️⃣  Testing Pie Chart...")
fig3 = px.pie(values=[5, 2, 3], names=['High', 'Medium', 'Low'])
print("   ✅ Pie chart created successfully")

print("\n✅ All visualization components working!")
print("   Charts can be displayed in Streamlit UI")

