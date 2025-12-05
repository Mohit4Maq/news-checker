"""
Streamlit UI for News Analyzer
Simple web interface for fact-checking and propaganda detection
"""

import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from news_analyzer import NewsAnalyzer

# App Version
APP_VERSION = "1.2.0"
VERSION_DATE = "2025-12-05"

# Page configuration
st.set_page_config(
    page_title="News Checker - Fact-Checking & Propaganda Detection",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .score-box {
        background-color: #f0f2f6;
        padding: 1.2rem;
        border-radius: 0.5rem;
        margin: 0.8rem 0;
        border: 1px solid #e0e0e0;
    }
    .section-header {
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1f77b4;
    }
    .verdict-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .factual {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .propaganda {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    .misinformation {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .opinion {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
    }
    .stProgress > div > div > div {
        background-color: #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

@st.cache_resource
def get_analyzer():
    """Get or create analyzer instance"""
    try:
        return NewsAnalyzer()
    except Exception as e:
        st.error(f"Error initializing analyzer: {str(e)}")
        return None

def format_score_color(score, max_score):
    """Get color based on score percentage"""
    percentage = (score / max_score) * 100
    if percentage >= 70:
        return "🟢"
    elif percentage >= 50:
        return "🟡"
    else:
        return "🔴"

def get_category_style(category):
    """Get CSS class for category"""
    category_lower = category.lower()
    if "factual" in category_lower:
        return "factual"
    elif "propaganda" in category_lower:
        return "propaganda"
    elif "misinformation" in category_lower:
        return "misinformation"
    elif "opinion" in category_lower or "analysis" in category_lower:
        return "opinion"
    return ""

def display_analysis_result(result):
    """Display the analysis result in a formatted way"""
    if not result or not result.get("success"):
        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        return
    
    analysis = result.get("analysis", {})
    article = result.get("article", {})
    
    # Header
    st.markdown("---")
    st.markdown(f"### 📰 {article.get('title', 'No Title')}")
    st.markdown(f"**🔗 URL:** {result.get('url', 'N/A')}")
    
    # Overall Verdict
    category = analysis.get("category", "UNKNOWN")
    overall_score = analysis.get("overall_score", 0)
    
    category_style = get_category_style(category)
    
    st.markdown(f"""
    <div class="verdict-box {category_style}">
        <h2>🎯 Overall Verdict: {category}</h2>
        <h3>📊 Overall Score: {overall_score}/100</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Category reasoning and keywords
    if "category_reasoning" in analysis and analysis.get("category_reasoning"):
        st.caption(f"📝 **Category Reasoning:** {analysis.get('category_reasoning')}")
    if "category_keywords" in analysis and analysis.get("category_keywords"):
        keywords = analysis.get("category_keywords", [])
        if keywords:
            st.caption(f"🔑 **Key Terms:** {', '.join(keywords[:5])}")
    
    # Score breakdown
    st.markdown("---")
    st.markdown("### 📈 Detailed Scoring")
    st.markdown("")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Factual Accuracy
        if "factual_accuracy" in analysis:
            fa = analysis["factual_accuracy"]
            score = fa.get("score", 0)
            st.markdown(f"""
            <div class="score-box">
                <h4>{format_score_color(score, 30)} Factual Accuracy: {score}/30</h4>
                <p>{fa.get('reasoning', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Source Credibility
        if "source_credibility" in analysis:
            sc = analysis["source_credibility"]
            score = sc.get("score", 0)
            st.markdown(f"""
            <div class="score-box">
                <h4>{format_score_color(score, 20)} Source Credibility: {score}/20</h4>
                <p>{sc.get('reasoning', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Bias Level
        if "bias_level" in analysis:
            bl = analysis["bias_level"]
            score = bl.get("score", 0)
            st.markdown(f"""
            <div class="score-box">
                <h4>{format_score_color(score, 15)} Bias Level: {score}/15</h4>
                <p>{bl.get('reasoning', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        # Propaganda Indicators
        if "propaganda_indicators" in analysis:
            pi = analysis["propaganda_indicators"]
            score = pi.get("score", 0)
            st.markdown(f"""
            <div class="score-box">
                <h4>{format_score_color(score, 15)} Propaganda Indicators: {score}/15</h4>
                <p>{pi.get('reasoning', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # India Relevance
        if "india_relevance" in analysis:
            ir = analysis["india_relevance"]
            score = ir.get("score", 0)
            st.markdown(f"""
            <div class="score-box">
                <h4>{format_score_color(score, 20)} 🇮🇳 India Relevance: {score}/20</h4>
                <p>{ir.get('reasoning', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # India-Specific Analysis
    if "india_specific_analysis" in analysis:
        st.markdown("---")
        st.markdown("### 🇮🇳 India-Specific Analysis")
        isa = analysis["india_specific_analysis"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**📌 Relevance to India:**")
            st.info(isa.get('relevance_to_india', 'N/A'))
            st.markdown(f"**💡 Potential Impact:**")
            st.info(isa.get('potential_impact', 'N/A'))
        with col2:
            st.markdown(f"**⚠️ Harm Assessment:**")
            st.warning(isa.get('harm_assessment', 'N/A'))
            st.markdown(f"**💬 Recommendation:**")
            st.success(isa.get('recommendation', 'N/A'))
    
    # Comprehensive Verdict
    if "verdict" in analysis:
        st.markdown("---")
        st.markdown("### 📋 Comprehensive Verdict")
        st.info(analysis.get("verdict", "N/A"))
    
    # Key Findings
    if "key_findings" in analysis:
        st.markdown("---")
        st.markdown("### 🔍 Key Findings")
        findings = analysis["key_findings"]
        if isinstance(findings, list):
            for i, finding in enumerate(findings, 1):
                st.markdown(f"**{i}.** {finding}")
        else:
            st.info(str(findings))
    
    # Critical Questions & Opposition Viewpoint
    if "critical_questions" in analysis:
        st.markdown("---")
        st.markdown("### ❓ Critical Questions & Opposition Viewpoint")
        cq = analysis["critical_questions"]
        
        if "questions_raised" in cq and cq.get("questions_raised"):
            st.markdown("#### Questions That Should Be Asked:")
            for i, q in enumerate(cq["questions_raised"][:5], 1):
                st.markdown(f"**{i}.** {q}")
    
    # Opposition Viewpoint
    if "opposition_viewpoint" in analysis and analysis.get("opposition_viewpoint"):
        st.markdown("---")
        st.markdown("### 🗣️ Opposition Viewpoint")
        with st.expander("📖 View Opposition Analysis", expanded=False):
            st.markdown(analysis.get("opposition_viewpoint"))
    
    # Citizen Accountability Section
    if "citizen_accountability" in analysis:
        st.markdown("---")
        st.markdown("## 👥 CITIZEN ACCOUNTABILITY")
        st.markdown("### What Should Have Been Reported for Indian Citizens")
        
        ca = analysis["citizen_accountability"]
        
        # Important highlights first
        if "real_citizen_impact" in ca and ca.get("real_citizen_impact"):
            st.error(f"**💡 Real Impact on Citizens (Not Covered):** {ca.get('real_citizen_impact')}")
        
        if "citizen_right_to_know" in ca and ca.get("citizen_right_to_know"):
            st.warning(f"**📜 Citizen's Right to Know:** {ca.get('citizen_right_to_know')}")
        
        if "democratic_accountability" in ca and ca.get("democratic_accountability"):
            st.info(f"**🗳️ Democratic Accountability:** {ca.get('democratic_accountability')}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "questions_citizens_should_ask" in ca and ca["questions_citizens_should_ask"]:
                st.markdown("#### ❓ Questions Citizens Should Ask")
                for i, q in enumerate(ca["questions_citizens_should_ask"][:5], 1):
                    st.markdown(f"**{i}.** {q}")
            
            if "topics_should_have_covered" in ca and ca["topics_should_have_covered"]:
                st.markdown("#### 📋 Topics Article Should Have Covered")
                for i, topic in enumerate(ca["topics_should_have_covered"][:5], 1):
                    st.markdown(f"**{i}.** {topic}")
        
        with col2:
            if "information_citizens_need" in ca and ca["information_citizens_need"]:
                st.markdown("#### 📰 Information Citizens Need (Missing)")
                for i, info in enumerate(ca["information_citizens_need"][:5], 1):
                    st.markdown(f"**{i}.** {info}")
            
            if "accountability_gaps" in ca and ca["accountability_gaps"]:
                st.markdown("#### ⚖️ Accountability Gaps")
                for i, gap in enumerate(ca["accountability_gaps"][:5], 1):
                    st.markdown(f"**{i}.** {gap}")
        
        if "transparency_issues" in ca and ca["transparency_issues"]:
            st.markdown("---")
            st.markdown("#### 🔍 Transparency Issues")
            for i, issue in enumerate(ca["transparency_issues"][:5], 1):
                st.markdown(f"**{i}.** {issue}")
        
        if "what_should_have_been_investigated" in ca and ca["what_should_have_been_investigated"]:
            st.markdown("---")
            st.markdown("#### 🔎 What Should Have Been Investigated")
            for i, inv in enumerate(ca["what_should_have_been_investigated"][:5], 1):
                st.markdown(f"**{i}.** {inv}")
    
    # World-Class Comparison Section with Visualizations
    if "world_class_comparison" in analysis:
        st.markdown("---")
        st.markdown("## 🌍 WORLD-CLASS REPORTING COMPARISON")
        st.markdown("### How This Article Compares to World's Best News Organizations")
        
        wcc = analysis["world_class_comparison"]
        
        # Overall Rating
        overall_rating = wcc.get("overall_rating_vs_world_class", 0)
        st.metric("📊 Overall Rating vs World-Class Standards", f"{overall_rating}/100")
        
        # Create comparison chart
        if "comparison_categories" in wcc:
            categories = wcc["comparison_categories"]
            
            # Prepare data for visualization
            category_names = []
            article_scores = []
            world_standards = []
            gaps = []
            
            for cat_name, cat_data in categories.items():
                if isinstance(cat_data, dict):
                    cat_display = cat_name.replace("_", " ").title()
                    category_names.append(cat_display)
                    article_scores.append(cat_data.get("this_article_score", 0))
                    world_standards.append(cat_data.get("world_class_standard", 85))
                    gaps.append(cat_data.get("gap", 0))
            
            # Create comparison bar chart
            if category_names:
                df = pd.DataFrame({
                    'Category': category_names,
                    'This Article': article_scores,
                    'World-Class Standard': world_standards
                })
                
                # Bar chart comparing scores
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='This Article',
                    x=category_names,
                    y=article_scores,
                    marker_color='#ff6b6b',
                    text=[f'{score}' for score in article_scores],
                    textposition='auto',
                ))
                fig.add_trace(go.Bar(
                    name='World-Class Standard',
                    x=category_names,
                    y=world_standards,
                    marker_color='#4ecdc4',
                    text=[f'{std}' for std in world_standards],
                    textposition='auto',
                ))
                
                fig.update_layout(
                    title='📊 Reporting Quality: This Article vs World-Class Standards',
                    xaxis_title='Categories',
                    yaxis_title='Score (0-100)',
                    barmode='group',
                    height=500,
                    xaxis={'tickangle': -45},
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Gap analysis chart
                gap_df = pd.DataFrame({
                    'Category': category_names,
                    'Gap': gaps
                })
                
                fig2 = go.Figure()
                colors = ['#ff6b6b' if gap < 0 else '#4ecdc4' for gap in gaps]
                fig2.add_trace(go.Bar(
                    x=category_names,
                    y=gaps,
                    marker_color=colors,
                    text=[f'{gap:+.0f}' for gap in gaps],
                    textposition='auto',
                ))
                fig2.update_layout(
                    title='📉 Gap Analysis: How Far Behind/Ahead of World-Class Standards',
                    xaxis_title='Categories',
                    yaxis_title='Gap (This Article - World Standard)',
                    height=400,
                    xaxis={'tickangle': -45},
                    shapes=[dict(type='line', yref='y', y0=0, y1=0, xref='paper', x0=0, x1=1, 
                                line=dict(color='gray', width=2, dash='dash'))]
                )
                st.plotly_chart(fig2, use_container_width=True)
                
                # Radar chart for overall comparison
                fig3 = go.Figure()
                fig3.add_trace(go.Scatterpolar(
                    r=article_scores + [article_scores[0]],  # Close the loop
                    theta=category_names + [category_names[0]],
                    fill='toself',
                    name='This Article',
                    line_color='#ff6b6b'
                ))
                fig3.add_trace(go.Scatterpolar(
                    r=world_standards + [world_standards[0]],
                    theta=category_names + [category_names[0]],
                    fill='toself',
                    name='World-Class Standard',
                    line_color='#4ecdc4'
                ))
                fig3.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    title='🎯 Radar Chart: Comprehensive Quality Comparison',
                    height=500
                )
                st.plotly_chart(fig3, use_container_width=True)
                
                # Impact Summary Chart
                impact_data = {
                    'High Impact': sum(1 for score in article_scores if score >= 70),
                    'Medium Impact': sum(1 for score in article_scores if 50 <= score < 70),
                    'Low Impact': sum(1 for score in article_scores if score < 50)
                }
                
                fig4 = px.pie(
                    values=list(impact_data.values()),
                    names=list(impact_data.keys()),
                    title='📊 Quality Distribution: How Many Categories Meet Standards',
                    color_discrete_map={'High Impact': '#4ecdc4', 'Medium Impact': '#ffe66d', 'Low Impact': '#ff6b6b'}
                )
                st.plotly_chart(fig4, use_container_width=True)
            
            # Detailed category assessments
            st.markdown("#### 📋 Detailed Category Assessments")
            for cat_name, cat_data in categories.items():
                if isinstance(cat_data, dict):
                    cat_display = cat_name.replace("_", " ").title()
                    with st.expander(f"🔍 {cat_display}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("This Article", f"{cat_data.get('this_article_score', 0)}/100")
                        with col2:
                            st.metric("World Standard", f"{cat_data.get('world_class_standard', 85)}/100")
                        with col3:
                            gap = cat_data.get('gap', 0)
                            st.metric("Gap", f"{gap:+.0f}", delta=f"{abs(gap)} points")
                        st.markdown(f"**Assessment:** {cat_data.get('assessment', 'N/A')}")
        
        # World-class benchmarks comparison
        if "world_class_benchmarks" in wcc:
            st.markdown("#### 🏆 Comparison with Specific News Organizations")
            benchmarks = wcc["world_class_benchmarks"]
            
            orgs = ["BBC", "Reuters", "The Guardian", "New York Times"]
            org_data = {}
            for org in orgs:
                key = f"{org.lower().replace(' ', '_').replace('the_', '')}_standard"
                if key in benchmarks:
                    org_data[org] = benchmarks[key]
            
            if org_data:
                for org, assessment in org_data.items():
                    st.markdown(f"**{org}:** {assessment}")
        
        # Strengths and improvements
        col1, col2 = st.columns(2)
        with col1:
            if "strengths" in wcc and wcc.get("strengths"):
                st.markdown("#### ✅ Strengths (Matches World-Class)")
                for strength in wcc["strengths"]:
                    st.success(f"• {strength}")
        
        with col2:
            if "improvement_needed" in wcc and wcc.get("improvement_needed"):
                st.markdown("#### ⚠️ Areas Needing Improvement")
                for improvement in wcc["improvement_needed"]:
                    st.error(f"• {improvement}")
        
        if "overall_assessment" in wcc.get("world_class_benchmarks", {}):
            st.markdown("#### 🌐 Overall World-Class Assessment")
            st.info(wcc["world_class_benchmarks"]["overall_assessment"])
    
    # True Report Section - Most Important
    if "true_report" in analysis:
        st.markdown("---")
        st.markdown("## 📰 TRUE REPORT - How This Should Have Been Reported")
        st.markdown("### Complete, Unbiased Report for Indian Citizens")
        
        tr = analysis["true_report"]
        
        if "title" in tr and tr.get("title"):
            st.markdown(f"#### 📌 Proper Title")
            st.success(tr.get("title"))
        
        if "lead_paragraph" in tr and tr.get("lead_paragraph"):
            st.markdown(f"#### 📝 Lead Paragraph")
            st.info(tr.get("lead_paragraph"))
        
        if "full_report" in tr and tr.get("full_report"):
            st.markdown("#### 📄 Complete Report")
            with st.expander("📖 Read Full Report", expanded=True):
                st.markdown(tr.get("full_report"))
        
        if "sections" in tr:
            st.markdown("#### 📋 Report Sections")
            sections = tr["sections"]
            
            section_tabs = st.tabs([
                "Background", "Perspectives", "Citizen Impact", 
                "Accountability", "Data & Evidence", "Expert Views"
            ])
            
            with section_tabs[0]:
                if "background_context" in sections and sections.get("background_context"):
                    st.markdown(sections["background_context"])
                if "historical_context" in sections and sections.get("historical_context"):
                    st.markdown("**Historical Context:**")
                    st.markdown(sections["historical_context"])
            
            with section_tabs[1]:
                if "multiple_perspectives" in sections and sections.get("multiple_perspectives"):
                    st.markdown(sections["multiple_perspectives"])
            
            with section_tabs[2]:
                if "citizen_impact_analysis" in sections and sections.get("citizen_impact_analysis"):
                    st.markdown(sections["citizen_impact_analysis"])
                if "citizen_rights_impact" in sections and sections.get("citizen_rights_impact"):
                    st.markdown("**Citizen Rights Impact:**")
                    st.markdown(sections["citizen_rights_impact"])
            
            with section_tabs[3]:
                if "accountability_questions" in sections and sections.get("accountability_questions"):
                    st.markdown(sections["accountability_questions"])
                if "transparency_issues" in sections and sections.get("transparency_issues"):
                    st.markdown("**Transparency Issues:**")
                    st.markdown(sections["transparency_issues"])
                if "policy_implications" in sections and sections.get("policy_implications"):
                    st.markdown("**Policy Implications:**")
                    st.markdown(sections["policy_implications"])
            
            with section_tabs[4]:
                if "data_and_evidence" in sections and sections.get("data_and_evidence"):
                    st.markdown(sections["data_and_evidence"])
            
            with section_tabs[5]:
                if "expert_opinions" in sections and sections.get("expert_opinions"):
                    st.markdown(sections["expert_opinions"])
        
        if "sources_and_references" in tr:
            st.markdown("#### 📚 Sources & References (What Should Have Been Used)")
            sources = tr["sources_and_references"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if "primary_sources" in sources and sources.get("primary_sources"):
                    st.markdown("**📄 Primary Sources:**")
                    for src in sources["primary_sources"][:5]:
                        st.markdown(f"• {src}")
                
                if "official_sources" in sources and sources.get("official_sources"):
                    st.markdown("**🏛️ Official Sources:**")
                    for src in sources["official_sources"][:5]:
                        st.markdown(f"• {src}")
                
                if "data_sources" in sources and sources.get("data_sources"):
                    st.markdown("**📊 Data Sources:**")
                    for src in sources["data_sources"][:5]:
                        st.markdown(f"• {src}")
            
            with col2:
                if "expert_sources" in sources and sources.get("expert_sources"):
                    st.markdown("**👨‍🔬 Expert Sources:**")
                    for src in sources["expert_sources"][:5]:
                        st.markdown(f"• {src}")
                
                if "independent_sources" in sources and sources.get("independent_sources"):
                    st.markdown("**🔍 Independent Sources:**")
                    for src in sources["independent_sources"][:5]:
                        st.markdown(f"• {src}")
                
                if "opposition_perspectives" in sources and sources.get("opposition_perspectives"):
                    st.markdown("**⚖️ Opposition Perspectives:**")
                    for src in sources["opposition_perspectives"][:5]:
                        st.markdown(f"• {src}")
        
        if "reporting_standards" in tr:
            st.markdown("#### 📋 Reporting Standards")
            standards = tr["reporting_standards"]
            
            if "what_was_missing" in standards and standards.get("what_was_missing"):
                st.error(f"**❌ What Was Missing:** {standards.get('what_was_missing')}")
            
            if "how_to_improve" in standards and standards.get("how_to_improve"):
                st.info(f"**✅ How to Improve:** {standards.get('how_to_improve')}")
            
            if "journalistic_standards" in standards and standards.get("journalistic_standards"):
                st.warning(f"**📰 Journalistic Standards:** {standards.get('journalistic_standards')}")
            
            if "citizen_focus" in standards and standards.get("citizen_focus"):
                st.success(f"**👥 Citizen Focus:** {standards.get('citizen_focus')}")
    
    # Related Articles Section
    if "related_articles" in result:
        st.markdown("---")
        st.markdown("## 🔗 RELATED ARTICLES & THEIR RELEVANCE")
        st.markdown("### Comparison with Other Articles on Same Website")
        
        ra = result["related_articles"]
        if ra.get("related_articles_found"):
            st.success(f"📰 Found {ra.get('total_found', 0)} related articles on the same website")
            
            for i, article in enumerate(ra.get("articles", []), 1):
                with st.expander(f"📄 {i}. {article.get('title', 'No title')[:80]}..."):
                    st.markdown(f"**🔗 URL:** [{article.get('url', 'N/A')}]({article.get('url', '#')})")
                    st.markdown(f"**📊 Relevance Score:** {article.get('relevance_score', 0)}")
                    
                    if article.get('summary'):
                        st.markdown(f"**📝 Summary:** {article.get('summary', '')}")
                    
                    comparison = article.get("comparison", {})
                    if comparison:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if comparison.get("common_topics"):
                                st.markdown("**🔄 Common Topics:**")
                                st.write(", ".join(comparison['common_topics'][:5]))
                            
                            if comparison.get("topics_in_related_not_in_current"):
                                st.markdown("**➕ Topics in Related (Missing in Current):**")
                                st.write(", ".join(comparison['topics_in_related_not_in_current'][:5]))
                        
                        with col2:
                            if comparison.get("topics_in_current_not_in_related"):
                                st.markdown("**➖ Topics in Current (Not in Related):**")
                                st.write(", ".join(comparison['topics_in_current_not_in_related'][:5]))
                        
                        if comparison.get("information_in_related_not_in_current"):
                            st.markdown("**⚠️ Information in Related Article (NOT in Current Article):**")
                            for info in comparison["information_in_related_not_in_current"]:
                                st.warning(f"• {info[:200]}...")
        else:
            st.info(f"ℹ️ {ra.get('message', 'No related articles found on the same website')}")
    
    # Fact Check Notes
    if "fact_check_notes" in analysis and analysis["fact_check_notes"]:
        st.markdown("---")
        st.markdown("### ⚠️ Fact-Check Notes")
        st.warning(analysis["fact_check_notes"])
    
    # Beneficiary Analysis Section - MOVED TO LAST
    if "beneficiary_analysis" in analysis:
        st.markdown("---")
        st.markdown("## 💰 BENEFICIARY & HIDDEN AGENDA ANALYSIS")
        st.markdown("### Who Benefits? What's Being Hidden?")
        
        ba = analysis["beneficiary_analysis"]
        
        # Critical findings first (most important)
        if "real_news_hidden" in ba and ba.get("real_news_hidden"):
            st.error(f"**🔍 Real News Being Hidden:** {ba.get('real_news_hidden')}")
        
        if "agenda_masking" in ba and ba.get("agenda_masking"):
            st.warning(f"**🎭 Agenda Masking:** {ba.get('agenda_masking')}")
        
        if "distraction_purpose" in ba and ba.get("distraction_purpose"):
            st.warning(f"**🎪 Distraction Purpose:** {ba.get('distraction_purpose')}")
        
        if "timing_analysis" in ba and ba.get("timing_analysis"):
            st.info(f"**⏰ Timing Analysis:** {ba.get('timing_analysis')}")
        
        st.markdown("---")
        
        # People and Beneficiaries in organized columns
        col1, col2 = st.columns(2)
        
        with col1:
            if "people_involved" in ba and ba.get("people_involved"):
                with st.container():
                    st.markdown("#### 👥 People/Entities Involved")
                    for person in ba["people_involved"]:
                        st.markdown(f"• {person}")
                    st.markdown("")
            
            if "direct_beneficiaries" in ba and ba.get("direct_beneficiaries"):
                with st.container():
                    st.markdown("#### ✅ Direct Beneficiaries")
                    for beneficiary in ba["direct_beneficiaries"]:
                        st.success(f"• {beneficiary}")
                    st.markdown("")
            
            if "indirect_beneficiaries" in ba and ba.get("indirect_beneficiaries"):
                with st.container():
                    st.markdown("#### 🔗 Indirect Beneficiaries")
                    for beneficiary in ba["indirect_beneficiaries"]:
                        st.warning(f"• {beneficiary}")
        
        with col2:
            if "political_beneficiaries" in ba and ba.get("political_beneficiaries"):
                with st.container():
                    st.markdown("#### 🏛️ Political Beneficiaries")
                    for beneficiary in ba["political_beneficiaries"]:
                        st.markdown(f"• {beneficiary}")
                    st.markdown("")
            
            if "economic_beneficiaries" in ba and ba.get("economic_beneficiaries"):
                with st.container():
                    st.markdown("#### 💵 Economic Beneficiaries")
                    for beneficiary in ba["economic_beneficiaries"]:
                        st.markdown(f"• {beneficiary}")
                    st.markdown("")
            
            if "who_loses" in ba and ba.get("who_loses"):
                with st.container():
                    st.markdown("#### ❌ Who Stands to Lose")
                    for entity in ba["who_loses"]:
                        st.error(f"• {entity}")
        
        # Connections section
        if "connections_and_relationships" in ba:
            st.markdown("---")
            st.markdown("#### 🔗 Connections & Relationships")
            connections = ba["connections_and_relationships"]
            
            conn_cols = st.columns(3)
            with conn_cols[0]:
                if "media_connections" in connections and connections.get("media_connections"):
                    st.markdown("**📺 Media Connections:**")
                    for conn in connections["media_connections"][:5]:
                        st.caption(f"• {conn}")
            
            with conn_cols[1]:
                if "business_relationships" in connections and connections.get("business_relationships"):
                    st.markdown("**💼 Business Relationships:**")
                    for conn in connections["business_relationships"][:5]:
                        st.caption(f"• {conn}")
            
            with conn_cols[2]:
                if "political_affiliations" in connections and connections.get("political_affiliations"):
                    st.markdown("**🏛️ Political Affiliations:**")
                    for conn in connections["political_affiliations"][:5]:
                        st.caption(f"• {conn}")
            
            if "undisclosed_relationships" in connections and connections.get("undisclosed_relationships"):
                st.markdown("---")
                st.markdown("**⚠️ Undisclosed Relationships:**")
                for conn in connections["undisclosed_relationships"]:
                    st.error(f"• {conn}")
        
        # Conflicts of Interest
        if "conflict_of_interest" in ba and ba.get("conflict_of_interest"):
            st.markdown("---")
            st.markdown("#### ⚠️ Conflicts of Interest")
            for conflict in ba["conflict_of_interest"]:
                st.error(f"• {conflict}")

# Main UI
st.markdown('<div class="main-header">📰 News Checker</div>', unsafe_allow_html=True)
st.markdown("### Fact-Checking & Propaganda Detection for Indian News")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Initialize analyzer
    if st.session_state.analyzer is None:
        with st.spinner("Initializing analyzer..."):
            st.session_state.analyzer = get_analyzer()
    
    if st.session_state.analyzer:
        st.success("✅ Analyzer Ready")
        
        # Test API key
        if st.button("🔑 Test API Key"):
            with st.spinner("Testing..."):
                if st.session_state.analyzer.test_api_key():
                    st.success("✅ API key is working!")
                else:
                    st.error("❌ API key test failed!")
    else:
        st.error("❌ Analyzer not initialized")
        st.stop()
    
    st.markdown("---")
    st.markdown("### 📖 About")
    st.markdown("""
    This tool analyzes news articles to:
    - ✅ Verify factual accuracy
    - 🚨 Detect propaganda
    - 🇮🇳 Assess India relevance
    - ⚖️ Identify bias
    - 📊 Provide comprehensive scoring
    """)
    
    st.markdown("---")
    st.markdown("### 💡 How to Use")
    st.markdown("""
    1. Enter a news article URL
    2. Click "Analyze News"
    3. Review the detailed analysis
    4. Check scores and verdict
    """)
    
    st.markdown("---")
    st.markdown("### 📌 Version")
    st.caption(f"**v{APP_VERSION}**")
    st.caption(f"Updated: {VERSION_DATE}")

# Main content area
st.markdown("---")

# Check for content parameter (from Chrome extension - NEW METHOD)
content_param = st.query_params.get("content", None)
if content_param:
    try:
        import base64
        import json
        
        # Decode base64 content from extension (Unicode-safe)
        try:
            # Decode URL encoding first
            decoded_param = content_param
            # Decode base64
            decoded_bytes = base64.b64decode(decoded_param)
            # Decode UTF-8
            decoded = decoded_bytes.decode('utf-8')
            article_data = json.loads(decoded)
        except Exception as e:
            st.error(f"❌ Error decoding content: {str(e)}")
            raise
        
        st.info(f"📰 Article content received from extension: {article_data.get('title', 'Untitled')[:60]}...")
        
        # Auto-analyze if content parameter is present
        if 'auto_analyzed' not in st.session_state:
            st.session_state.auto_analyzed = True
            with st.spinner("🧠 Analyzing article content... This may take 30-60 seconds."):
                try:
                    # Use the content directly - no fetching needed!
                    article_data_structured = {
                        "success": True,
                        "title": article_data.get('title', 'No title found'),
                        "content": article_data.get('content', ''),
                        "url": article_data.get('url', 'extension-input')
                    }
                    
                    # Load rules and create prompt
                    rules = st.session_state.analyzer.load_rules()
                    prompt = st.session_state.analyzer.create_analysis_prompt(article_data_structured, rules)
                    
                    # Call OpenAI API
                    response = st.session_state.analyzer.client.chat.completions.create(
                        model=st.session_state.analyzer.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a CRITICAL OPPOSITION REPORTER and investigative journalist analyzing Indian news. Your job is to QUESTION EVERYTHING, identify what's MISSING, challenge claims, and demand answers that Indian citizens deserve. Don't accept reports at face value - be skeptical, ask hard questions, and judge based on what answers the report provides."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.4,
                        max_tokens=4000
                    )
                    
                    analysis_text = response.choices[0].message.content
                    
                    # Parse JSON
                    try:
                        if "```json" in analysis_text:
                            json_start = analysis_text.find("```json") + 7
                            json_end = analysis_text.find("```", json_start)
                            analysis_text = analysis_text[json_start:json_end].strip()
                        elif "```" in analysis_text:
                            json_start = analysis_text.find("```") + 3
                            json_end = analysis_text.find("```", json_start)
                            analysis_text = analysis_text[json_start:json_end].strip()
                        
                        analysis_json = json.loads(analysis_text)
                        analysis_json = st.session_state.analyzer.refine_category_based_on_scores(analysis_json, article_data_structured)
                    except json.JSONDecodeError:
                        analysis_json = {"raw_response": analysis_text}
                    
                    result = {
                        "success": True,
                        "url": article_data.get('url', 'extension-input'),
                        "article": article_data_structured,
                        "analysis": analysis_json
                    }
                    
                    st.session_state.last_result = result
                    st.success("✅ Analysis complete! (Content extracted directly from page - no fetching needed)")
                    display_analysis_result(result)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())
    except Exception as e:
        st.warning(f"⚠️ Could not decode content parameter: {e}. Falling back to URL method...")
        content_param = None

# Check for URL parameter (from Chrome extension or direct link - FALLBACK METHOD)
url_param = st.query_params.get("url", None)
if url_param and not content_param:
    st.info(f"📰 Article URL received: {url_param[:80]}...")
    # Auto-analyze if URL parameter is present
    if 'auto_analyzed' not in st.session_state:
        st.session_state.auto_analyzed = True
        with st.spinner("🔍 Fetching and analyzing article... This may take 30-60 seconds."):
            try:
                result = st.session_state.analyzer.analyze_news(url_param)
                st.session_state.last_result = result
                
                if result.get("success"):
                    st.success("✅ Analysis complete!")
                    if result.get("article", {}).get("method"):
                        st.info(f"📡 Fetched using: {result['article']['method']}")
                    display_analysis_result(result)
                else:
                    error_msg = result.get('error', 'Unknown error')
                    st.error(f"❌ Analysis failed: {error_msg}")
                    if result.get('suggestion'):
                        st.info(f"💡 {result.get('suggestion')}")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                import traceback
                with st.expander("🔍 Error Details"):
                    st.code(traceback.format_exc())

# Input method selection
input_method = st.radio(
    "Choose input method:",
    ["🔗 Enter URL", "📝 Paste Article Content"],
    horizontal=True
)

if input_method == "🔗 Enter URL":
    # URL input - pre-fill if URL parameter exists
    default_url = url_param if url_param else ""
    url_input = st.text_input(
        "🔗 Enter News Article URL",
        value=default_url,
        placeholder="https://example.com/news-article",
        help="Paste the full URL of the news article you want to analyze"
    )
    manual_content = None
    manual_title = None
else:
    # Manual content input
    manual_title = st.text_input(
        "📰 Article Title (Optional)",
        placeholder="Enter the article title",
        help="Title of the news article"
    )
    manual_content = st.text_area(
        "📝 Paste Article Content",
        placeholder="Paste the full text of the news article here...",
        height=200,
        help="Copy and paste the article content if URL fetching fails"
    )
    url_input = None

col1, col2 = st.columns([1, 4])

with col1:
    analyze_button = st.button("🔍 Analyze News", type="primary", use_container_width=True)

with col2:
    if st.session_state.last_result:
        if st.button("📄 Show Last Result", use_container_width=True):
            st.session_state.show_last = True

# Analyze button clicked
if analyze_button:
    if input_method == "🔗 Enter URL":
        if not url_input:
            st.warning("⚠️ Please enter a URL")
        elif not url_input.startswith(('http://', 'https://')):
            st.warning("⚠️ Please enter a valid URL starting with http:// or https://")
        else:
            with st.spinner("🔍 Fetching and analyzing article... This may take 30-60 seconds."):
                try:
                    result = st.session_state.analyzer.analyze_news(url_input)
                    st.session_state.last_result = result
                    
                    if result.get("success"):
                        st.success("✅ Analysis complete!")
                        if result.get("article", {}).get("method"):
                            st.info(f"📡 Fetched using: {result['article']['method']}")
                        display_analysis_result(result)
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        
                        # Check if it's a content extraction error
                        if "Could not extract sufficient content" in error_msg or "extract" in error_msg.lower():
                            st.error(f"❌ Could not fetch article content automatically")
                            
                            # Show prominent manual paste option
                            st.warning("""
                            **⚠️ Website blocking detected or unsupported page structure**
                            
                            This is common on Streamlit Cloud. The website may be blocking automated access.
                            """)
                            
                            st.info("""
                            **✅ SOLUTION: Use Manual Paste**
                            
                            1. **Switch to "📝 Paste Article Content"** (radio button above)
                            2. Copy the article text from the website
                            3. Paste it into the text area
                            4. Click "Analyze News"
                            
                            This method works 100% of the time and is often faster!
                            """)
                            
                            # Show the manual paste section prominently
                            st.markdown("---")
                            st.markdown("### 📝 Quick Fix: Paste Article Content Below")
                            
                            manual_title_fallback = st.text_input(
                                "📰 Article Title (Optional)",
                                key="fallback_title",
                                placeholder="Enter the article title",
                                help="Title of the news article"
                            )
                            manual_content_fallback = st.text_area(
                                "📝 Paste Article Content Here",
                                key="fallback_content",
                                placeholder="Copy and paste the full article text here...",
                                height=300,
                                help="This works when URL fetching fails"
                            )
                            
                            if st.button("🔍 Analyze Pasted Content", type="primary", key="fallback_analyze"):
                                if manual_content_fallback and len(manual_content_fallback.strip()) >= 50:
                                    with st.spinner("🧠 Analyzing pasted content... This may take 30-60 seconds."):
                                        try:
                                            article_data = {
                                                "success": True,
                                                "title": manual_title_fallback or "Manually Entered Article",
                                                "content": manual_content_fallback,
                                                "url": url_input or "manual-input"
                                            }
                                            
                                            rules = st.session_state.analyzer.load_rules()
                                            prompt = st.session_state.analyzer.create_analysis_prompt(article_data, rules)
                                            
                                            response = st.session_state.analyzer.client.chat.completions.create(
                                                model=st.session_state.analyzer.model,
                                                messages=[
                                                    {
                                                        "role": "system",
                                                        "content": "You are a CRITICAL OPPOSITION REPORTER and investigative journalist analyzing Indian news. Your job is to QUESTION EVERYTHING, identify what's MISSING, challenge claims, and demand answers that Indian citizens deserve. Don't accept reports at face value - be skeptical, ask hard questions, and judge based on what answers the report provides."
                                                    },
                                                    {
                                                        "role": "user",
                                                        "content": prompt
                                                    }
                                                ],
                                                temperature=0.4,
                                                max_tokens=4000
                                            )
                                            
                                            analysis_text = response.choices[0].message.content
                                            
                                            try:
                                                if "```json" in analysis_text:
                                                    json_start = analysis_text.find("```json") + 7
                                                    json_end = analysis_text.find("```", json_start)
                                                    analysis_text = analysis_text[json_start:json_end].strip()
                                                elif "```" in analysis_text:
                                                    json_start = analysis_text.find("```") + 3
                                                    json_end = analysis_text.find("```", json_start)
                                                    analysis_text = analysis_text[json_start:json_end].strip()
                                                
                                                analysis_json = json.loads(analysis_text)
                                                analysis_json = st.session_state.analyzer.refine_category_based_on_scores(analysis_json, article_data)
                                            except json.JSONDecodeError:
                                                analysis_json = {"raw_response": analysis_text}
                                            
                                            result = {
                                                "success": True,
                                                "url": url_input or "manual-input",
                                                "article": article_data,
                                                "analysis": analysis_json
                                            }
                                            
                                            st.session_state.last_result = result
                                            st.success("✅ Analysis complete!")
                                            display_analysis_result(result)
                                            
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                                            import traceback
                                            with st.expander("🔍 Error Details"):
                                                st.code(traceback.format_exc())
                                else:
                                    st.warning("⚠️ Please paste article content (at least 50 characters)")
                        else:
                            # Check if it's a 403/401 error - show prominent manual paste
                            if "403" in error_msg or "401" in error_msg or "Forbidden" in error_msg or "block" in error_msg.lower():
                                st.error(f"❌ {error_msg}")
                                
                                # Show prominent manual paste option for 403 errors
                                st.warning("""
                                **🚫 Website Blocking Detected**
                                
                                This website is blocking automated requests from Streamlit Cloud. This is very common and expected.
                                """)
                                
                                st.success("""
                                **✅ EASY SOLUTION: Use Manual Paste**
                                
                                This method works 100% of the time and is often faster than automated fetching!
                                """)
                                
                                st.markdown("---")
                                st.markdown("### 📝 Quick Fix: Paste Article Content Below")
                                
                                manual_title_fallback = st.text_input(
                                    "📰 Article Title (Optional)",
                                    key="fallback_title_403",
                                    placeholder="Enter the article title",
                                    help="Title of the news article"
                                )
                                manual_content_fallback = st.text_area(
                                    "📝 Paste Article Content Here",
                                    key="fallback_content_403",
                                    placeholder="Copy and paste the full article text here...",
                                    height=300,
                                    help="This works when websites block automated access"
                                )
                                
                                if st.button("🔍 Analyze Pasted Content", type="primary", key="fallback_analyze_403"):
                                    if manual_content_fallback and len(manual_content_fallback.strip()) >= 50:
                                        with st.spinner("🧠 Analyzing pasted content... This may take 30-60 seconds."):
                                            try:
                                                article_data = {
                                                    "success": True,
                                                    "title": manual_title_fallback or "Manually Entered Article",
                                                    "content": manual_content_fallback,
                                                    "url": url_input or "manual-input"
                                                }
                                                
                                                rules = st.session_state.analyzer.load_rules()
                                                prompt = st.session_state.analyzer.create_analysis_prompt(article_data, rules)
                                                
                                                response = st.session_state.analyzer.client.chat.completions.create(
                                                    model=st.session_state.analyzer.model,
                                                    messages=[
                                                        {
                                                            "role": "system",
                                                            "content": "You are a CRITICAL OPPOSITION REPORTER and investigative journalist analyzing Indian news. Your job is to QUESTION EVERYTHING, identify what's MISSING, challenge claims, and demand answers that Indian citizens deserve. Don't accept reports at face value - be skeptical, ask hard questions, and judge based on what answers the report provides."
                                                        },
                                                        {
                                                            "role": "user",
                                                            "content": prompt
                                                        }
                                                    ],
                                                    temperature=0.4,
                                                    max_tokens=4000
                                                )
                                                
                                                analysis_text = response.choices[0].message.content
                                                
                                                try:
                                                    if "```json" in analysis_text:
                                                        json_start = analysis_text.find("```json") + 7
                                                        json_end = analysis_text.find("```", json_start)
                                                        analysis_text = analysis_text[json_start:json_end].strip()
                                                    elif "```" in analysis_text:
                                                        json_start = analysis_text.find("```") + 3
                                                        json_end = analysis_text.find("```", json_start)
                                                        analysis_text = analysis_text[json_start:json_end].strip()
                                                    
                                                    analysis_json = json.loads(analysis_text)
                                                    analysis_json = st.session_state.analyzer.refine_category_based_on_scores(analysis_json, article_data)
                                                except json.JSONDecodeError:
                                                    analysis_json = {"raw_response": analysis_text}
                                                
                                                result = {
                                                    "success": True,
                                                    "url": url_input or "manual-input",
                                                    "article": article_data,
                                                    "analysis": analysis_json
                                                }
                                                
                                                st.session_state.last_result = result
                                                st.success("✅ Analysis complete!")
                                                display_analysis_result(result)
                                                
                                            except Exception as e:
                                                st.error(f"❌ Error: {str(e)}")
                                                import traceback
                                                with st.expander("🔍 Error Details"):
                                                    st.code(traceback.format_exc())
                                    else:
                                        st.warning("⚠️ Please paste article content (at least 50 characters)")
                            else:
                                # Other types of errors
                                st.error(f"❌ Analysis failed: {error_msg}")
                                
                                # Show suggestion if available
                                if result.get('suggestion'):
                                    st.info(f"💡 {result.get('suggestion')}")
                                
                                # Show fallback options
                                with st.expander("🔧 Alternative Methods Available"):
                                    st.markdown("""
                                    **When a site blocks automated access, you can try:**
                                    
                                    1. **📝 Manual Paste** (Recommended - Fastest)
                                       - Switch to "Paste Article Content" above
                                       - Copy article from website
                                       - Paste and analyze
                                    
                                    2. **📰 Newspaper3k Library**
                                       - Already installed and auto-tries
                                       - Works for many news sites
                                    
                                    3. **📡 RSS Feed**
                                       - Auto-checks for RSS feeds
                                       - Good for news sites
                                    
                                    4. **🌐 Browser Automation** (Advanced)
                                       - Install Selenium: `pip install selenium`
                                       - Install Playwright: `pip install playwright && playwright install chromium`
                                       - Handles JavaScript-heavy sites
                                    
                                    5. **📋 Read Documentation**
                                       - See `ADVANCED_FETCHING.md` for details
                                    """)
                                
                                st.info("💡 Tip: Use the 'Paste Article Content' option above for the most reliable method.")
            
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())
    
    else:  # Manual content input
        if not manual_content or len(manual_content.strip()) < 50:
            st.warning("⚠️ Please paste article content (at least 50 characters)")
        else:
            with st.spinner("🧠 Analyzing article content... This may take 30-60 seconds."):
                try:
                    # Create article data structure
                    article_data = {
                        "success": True,
                        "title": manual_title or "Manually Entered Article",
                        "content": manual_content,
                        "url": "manual-input"
                    }
                    
                    # Load rules and create prompt
                    rules = st.session_state.analyzer.load_rules()
                    prompt = st.session_state.analyzer.create_analysis_prompt(article_data, rules)
                    
                    # Call OpenAI API
                    response = st.session_state.analyzer.client.chat.completions.create(
                        model=st.session_state.analyzer.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a CRITICAL OPPOSITION REPORTER and investigative journalist analyzing Indian news. Your job is to QUESTION EVERYTHING, identify what's MISSING, challenge claims, and demand answers that Indian citizens deserve. Don't accept reports at face value - be skeptical, ask hard questions, and judge based on what answers the report provides."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.4,
                        max_tokens=4000
                    )
                    
                    analysis_text = response.choices[0].message.content
                    
                    # Parse JSON
                    try:
                        if "```json" in analysis_text:
                            json_start = analysis_text.find("```json") + 7
                            json_end = analysis_text.find("```", json_start)
                            analysis_text = analysis_text[json_start:json_end].strip()
                        elif "```" in analysis_text:
                            json_start = analysis_text.find("```") + 3
                            json_end = analysis_text.find("```", json_start)
                            analysis_text = analysis_text[json_start:json_end].strip()
                        
                        analysis_json = json.loads(analysis_text)
                    except json.JSONDecodeError:
                        analysis_json = {"raw_response": analysis_text}
                    
                    result = {
                        "success": True,
                        "url": "manual-input",
                        "article": article_data,
                        "analysis": analysis_json
                    }
                    
                    st.session_state.last_result = result
                    st.success("✅ Analysis complete!")
                    display_analysis_result(result)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    with st.expander("🔍 Error Details"):
                        st.code(traceback.format_exc())

# Show last result if requested
if st.session_state.get('show_last', False) and st.session_state.last_result:
    st.session_state.show_last = False
    display_analysis_result(st.session_state.last_result)

# Footer
st.markdown("---")
st.markdown(
    f"<div style='text-align: center; color: #666; padding: 1rem;'>"
    f"Powered by OpenAI GPT-4 | Built for Indian News Analysis<br>"
    f"<small>Version {APP_VERSION} | Updated {VERSION_DATE}</small>"
    f"</div>",
    unsafe_allow_html=True
)

