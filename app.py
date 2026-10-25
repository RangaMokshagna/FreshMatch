from pathlib import Path
import json, html, time, textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title='FreshMatch · Better alternatives',page_icon='🌿',layout='wide',initial_sidebar_state='auto')
BASE=Path(__file__).resolve().parent
ART=BASE/'artifacts'
ACCENT='#0F7B5F'
px.defaults.template='plotly_white'
px.defaults.color_discrete_sequence=[ACCENT,'#99620B','#3E65A0','#AF4035']
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
/* FreshMatch design tokens: an 8 px spacing scale, AA text colours, one brand green. */
:root{--primary:#0F7B5F;--primary-hover:#084D39;--ink:#193D2D;--muted:#4B5A52;--background:#F6FAF7;--card:#FFFFFF;--border:#CFE3D8;--soft:#EAF4EE;--amber:#875608;--amber-bg:#FFF3D9;--danger:#A33226;--danger-bg:#FFF0EC;--space-1:8px;--space-2:16px;--space-3:24px;--space-4:32px;--radius:16px;--shadow:0 4px 20px rgba(25,61,45,.045)}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--background);color:var(--ink);font-family:'Inter',sans-serif;font-weight:400}
/* Remove Streamlit chrome, retaining only the essential mobile sidebar opener. */
[data-testid="stHeader"]{height:0!important;background:transparent!important;visibility:hidden;pointer-events:none}
#MainMenu,footer,[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stToolbar"]{visibility:hidden;pointer-events:none}
[data-testid="stSidebarCollapsedControl"]{visibility:visible!important;pointer-events:auto;position:fixed!important;left:8px!important;top:8px!important;z-index:1000}
[data-testid="stExpandSidebarButton"]{visibility:visible!important;pointer-events:auto!important;position:fixed!important;top:8px!important;left:8px!important;z-index:1000;background:var(--card)!important;color:var(--primary)!important;border:1px solid var(--border)!important;border-radius:10px!important;min-width:32px;min-height:32px}
[data-testid="stSidebarCollapsedControl"] button{background:var(--card)!important;color:var(--primary)!important;border:1px solid var(--border)!important;border-radius:10px}
.block-container{padding:2.5rem 2.5rem 2rem;max-width:1344px;min-width:0}
[data-testid="stMain"] [data-testid="stVerticalBlock"]{gap:12px}
h1,h2,h3{font-family:'Inter',sans-serif!important;letter-spacing:-.035em!important;color:var(--ink)!important;overflow-wrap:anywhere}
h1{font-size:2rem!important;font-weight:700!important;line-height:1.2!important;margin:0!important;padding:0!important}
h2{font-size:1.45rem!important;font-weight:700!important}h3{font-size:1.05rem!important;font-weight:600!important}
.stApp p,.stApp li{font-weight:400;line-height:1.6}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p{color:var(--muted)!important;font-weight:400!important;opacity:1!important;font-size:.78rem}
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, label, [data-testid="stSlider"] [data-testid="stMarkdownContainer"]{color:var(--ink)!important;font-weight:600!important;opacity:1!important}
[data-testid="stSlider"] [role="slider"], [data-testid="stSliderTickBar"]{color:var(--muted)!important;font-weight:600!important}
.eyebrow{color:var(--primary);font-size:.66rem;font-weight:700;line-height:1.6;letter-spacing:.15em;text-transform:uppercase;margin:0 0 8px;overflow:visible}
.hero{background:linear-gradient(115deg,#E8F3EB,#F0F6E8);border:1px solid var(--border);border-radius:var(--radius);padding:20px 24px;margin:0;min-height:100px}
.hero h1{font-size:2rem!important;line-height:1.2!important;max-width:100%}
.hero p{font-size:.875rem;color:var(--muted);font-weight:400;line-height:1.45;margin:8px 0 0}
[data-testid="stSidebar"]{background:#EDF5EF!important;border-right:1px solid var(--border);min-width:0}
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding:24px 16px!important}
[data-testid="stSidebar"] .block-container{padding:16px!important}
.brand{display:flex;align-items:center;gap:10px;font-size:1.5rem;font-weight:800;letter-spacing:-.055em;color:var(--ink);line-height:1.2}
.brand-icon{font-size:32px;line-height:1}.brand-name span{color:var(--primary)}
.subbrand{font-size:.65rem;letter-spacing:.1em;color:var(--muted);font-weight:600;margin:8px 0 24px 42px}
.nav-label{font-size:.65rem;font-weight:700;color:var(--muted);letter-spacing:.12em;margin:0 0 8px;text-transform:uppercase}
[data-testid="stSidebar"] .stButton>button{min-height:44px;width:100%;justify-content:flex-start;text-align:left;padding:10px 16px;border:1px solid transparent!important;border-radius:24px!important;background:transparent;color:var(--ink);font-weight:600;box-shadow:none;transition:background .18s}
[data-testid="stSidebar"] .stButton>button>div,[data-testid="stSidebar"] .stButton>button [data-has-shortcut]{width:100%;justify-content:flex-start!important}
[data-testid="stSidebar"] .stButton>button p{font-size:.83rem;font-weight:600;white-space:normal;text-align:left}
[data-testid="stSidebar"] .stButton>button:hover{background:#DCECDF;border-color:transparent;color:var(--ink)}
[data-testid="stSidebar"] .stButton>button[kind="primary"], [data-testid="stSidebar"] [data-testid="stBaseButton-primary"]{background:var(--primary)!important;color:white!important;border-color:var(--primary)!important}
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p{color:#fff!important}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:8px}
.catalogue-card{padding:16px;background:var(--card);border:1px solid var(--border);border-radius:16px;margin:24px 0 8px}
.catalogue-head{display:flex;align-items:center;justify-content:space-between;gap:8px;color:var(--muted);font-size:.68rem;font-weight:700}
.data-badge{font-size:.6rem;line-height:1.5;font-weight:600;padding:3px 7px;border-radius:20px;color:var(--primary);background:var(--soft);white-space:nowrap}
.catalogue-stats{display:grid;grid-template-columns:1fr 1fr;margin-top:16px;gap:16px}
.catalogue-stats strong{font-size:1.5rem;line-height:1.2;display:block;letter-spacing:-.04em}
.catalogue-stats span{display:block;font-size:.7rem;color:var(--muted);margin-top:4px}
.sidebar-note{font-size:.69rem;line-height:1.65;color:var(--muted);margin:0 4px}
/* Inputs use one explicit surface and an accessible, visible keyboard focus ring. */
[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stMultiSelect"] [data-baseweb="select"]>div,[data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stNumberInput"] [data-baseweb="input"], [data-testid="stSelectbox"] [data-testid="stSelectboxRoot"], [data-testid="stMultiSelect"] [data-testid="stMultiSelectRoot"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;min-height:44px;color:var(--ink)!important;box-shadow:0 2px 6px #193d2d03}
[data-testid="stSelectbox"] [role="combobox"], [data-testid="stMultiSelect"] [role="combobox"]{color:var(--ink)!important;font-weight:500;min-width:0}
[data-testid="stSelectbox"]:focus-within [data-baseweb="select"]>div,[data-testid="stMultiSelect"]:focus-within [data-baseweb="select"]>div,[data-testid="stTextInput"]:focus-within [data-baseweb="input"],[data-testid="stNumberInput"]:focus-within [data-baseweb="input"]{border-color:var(--primary)!important;outline:3px solid #0F7B5F33;outline-offset:2px}
button:focus-visible,input:focus-visible,[role="combobox"]:focus-visible,summary:focus-visible{outline:3px solid var(--primary)!important;outline-offset:3px!important}
input::placeholder{color:var(--muted)!important;opacity:1}
[data-testid="stTextInput"] input{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;min-height:44px;color:var(--ink)!important;padding:10px 12px!important}
[data-testid="stTextInput"] input:focus{border-color:var(--primary)!important;outline:3px solid #0F7B5F33!important;outline-offset:2px!important}
[data-testid="stNumberInput"] input{background:var(--card)!important;color:var(--ink)!important}
[data-testid="stMetricLabel"] p{font-weight:600!important;color:var(--muted)!important}
[data-testid="stSelectbox"] .react-aria-ComboBox>[role="group"],[data-testid="stMultiSelect"] [role="group"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;min-height:44px}
[data-testid="stSelectbox"] .react-aria-ComboBox>[role="group"]:focus-within,[data-testid="stMultiSelect"] [role="group"]:focus-within{border-color:var(--primary)!important;box-shadow:0 0 0 3px #0F7B5F33!important}
[data-testid="stTooltipIcon"] button{color:var(--muted)!important;opacity:1!important}
.stButton>button,.stDownloadButton>button{min-height:44px;border:1px solid var(--border);border-radius:12px;font-weight:600;color:var(--primary);background:white;transition:background .18s,transform .18s}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--primary);background:var(--soft);color:var(--primary)}
.selection{display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--card);border:1px solid var(--border);border-radius:16px;min-width:0}
.selection{margin-bottom:8px}.selection-body{flex:1;min-width:0}.selection-label{font-size:.62rem;text-transform:uppercase;letter-spacing:.1em;font-weight:700;color:var(--muted)}
.selection-name{font-size:.875rem;font-weight:600;line-height:1.45;overflow-wrap:anywhere}.selection-price{font-size:.9rem;font-weight:700;white-space:nowrap}
.stock-pill{color:var(--danger);background:var(--danger-bg);border:1px solid #EAC6BE;border-radius:24px;padding:5px 10px;font-size:.66rem;font-weight:700;white-space:nowrap}
.stock-pill.available{color:var(--amber);background:var(--amber-bg);border-color:#E6D5AC}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:14px!important;box-shadow:0 2px 8px #193d2d02;min-width:0}
[data-testid="stExpander"] summary{font-size:.83rem;color:var(--ink);font-weight:600;padding:10px 16px!important;min-height:44px}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{padding:8px 16px 16px}
.product-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;animation:fade-in .3s ease-out}
.product-card{min-width:0;background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;box-shadow:var(--shadow);transition:transform .18s ease,box-shadow .18s ease;position:relative}
.product-card:hover{transform:translateY(-4px);box-shadow:0 10px 24px #193D2D12}
.card-top{display:flex;align-items:center;gap:8px;min-width:0}.rank{font-size:.68rem;color:var(--muted);font-weight:700;font-variant-numeric:tabular-nums}
.tile-icon{width:36px;height:36px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0;background:var(--soft);border-radius:10px;font-size:1.4rem}
.badge{margin-left:auto;font-size:.6rem;font-weight:700;line-height:1.4;white-space:nowrap;padding:4px 8px;border-radius:24px;background:var(--soft);color:var(--primary)}
.badge.cheaper{background:var(--amber-bg);color:var(--amber)}
.product-card h3{font-size:.91rem!important;font-weight:600!important;line-height:1.45!important;letter-spacing:-.02em!important;margin:12px 0 4px!important;padding:0!important;min-height:42px;overflow-wrap:anywhere}
.category{font-size:.7rem;color:var(--muted);line-height:1.45;overflow-wrap:anywhere}
.price-row{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin-top:12px}.price{font-size:1.3rem;font-weight:700;letter-spacing:-.04em;color:var(--ink)}
.price-difference{color:var(--primary);font-size:.65rem;font-weight:600}.price-difference.higher{color:var(--amber)}
.score-label{display:flex;align-items:center;justify-content:space-between;gap:8px;font-size:.68rem;color:var(--muted);margin-top:12px;font-weight:500}.score-label b{color:var(--primary);font-weight:700}
.track{height:6px;background:#DCEBE2;border-radius:8px;margin:8px 0 0}.fill{background:var(--primary);height:6px;border-radius:8px}
.reason{color:var(--muted)!important;font-size:.7rem!important;font-weight:400!important;line-height:1.6!important;margin:10px 0 0!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty-state{text-align:center;background:white;border:1px dashed #AFCBB9;border-radius:16px;padding:24px 16px 16px;margin-top:4px}
.empty-illustration{font-size:2.3rem;display:inline-flex;align-items:center;justify-content:center;width:72px;height:72px;background:var(--soft);border-radius:50%;margin-bottom:12px}
.empty-state h2{font-size:1.15rem!important;margin:0!important;padding:0!important}.empty-state p{color:var(--muted);font-size:.83rem;margin:8px 0 0}
.metric-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;box-shadow:var(--shadow);height:100%;min-width:0}
.metric-heading{font-size:.72rem;color:var(--muted);font-weight:600;line-height:1.5;display:flex;gap:8px;align-items:center}.metric-icon{font-size:1rem}.metric-value{font-size:1.8rem;line-height:1.2;font-weight:700;letter-spacing:-.05em;margin:12px 0 6px;color:var(--ink);overflow-wrap:anywhere}.metric-caption{font-size:.67rem;line-height:1.5;color:var(--muted)}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;box-shadow:var(--shadow)}
[data-testid="stMetricLabel"]{color:var(--muted)!important;font-weight:600}[data-testid="stMetricValue"]{color:var(--ink);font-size:1.8rem!important;font-weight:700}
.stAlert{border-radius:12px;color:var(--ink)}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"],[data-testid="stGraphVizChart"]{max-width:100%;min-width:0;overflow:hidden}
.footnote{border-top:1px solid var(--border);padding:16px 0 0;margin-top:24px;font-size:.66rem;line-height:1.6;color:var(--muted);text-align:center;overflow-wrap:anywhere}
.mobile-method{display:none}.method-step{padding:12px 16px;background:var(--card);border:1px solid var(--border);border-radius:12px;display:flex;align-items:center;gap:12px;font-size:.8rem;font-weight:600;color:var(--ink)}.method-step span{color:var(--primary);font-size:.65rem;font-weight:700}.method-arrow{color:var(--primary);text-align:center;line-height:1}
@keyframes fade-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}

@media(max-width:900px) and (min-width:641px){.product-card{padding:12px}.card-top{flex-wrap:wrap}.badge{font-size:.56rem;padding:4px 6px}}
@media(max-width:750px){[data-testid="stElementContainer"]:has([data-testid="stGraphVizChart"]),[data-testid="stGraphVizChart"]{display:none}.mobile-method{display:grid;gap:8px}.block-container{padding:3.5rem 1rem 1.5rem}.hero{padding:14px 16px}.hero h1{font-size:1.5rem!important;line-height:1.15!important}.hero p{font-size:.79rem}.eyebrow{font-size:.61rem}.selection{flex-wrap:wrap}.selection-body{flex-basis:calc(100% - 52px)}.selection-price{margin-left:48px}.stock-pill{margin-left:auto}.footnote{font-size:.6rem}.metric-value{font-size:1.65rem}.stApp{overflow-x:clip}[data-testid="stMain"]{min-width:0}h1{font-size:1.65rem!important}[data-testid="stHorizontalBlock"]{flex-wrap:wrap;gap:12px}[data-testid="stHorizontalBlock"]>[data-testid="stColumn"]{width:100%;flex:1 1 100%;min-width:0}.product-grid{grid-template-columns:1fr}.product-card h3{min-height:0!important}.metric-card{min-height:120px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}.product-card:hover{transform:none}}

/* Section rhythm: prevent adjacent cards, controls and captions touching. */
[data-testid="stMain"] [data-testid="stVerticalBlock"]{gap:16px!important}
.hero{margin-bottom:12px}
.empty-state{margin-top:16px;margin-bottom:16px;padding:28px 20px 24px}
.empty-state p{margin-top:10px}
.metric-card{padding:20px;min-height:148px}
.metric-caption{margin-top:8px;line-height:1.65}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has(.metric-card){margin-bottom:12px}
[data-testid="stMain"] [data-testid="stCaptionContainer"]{line-height:1.7;padding-top:4px;padding-bottom:4px}
[data-testid="stMain"] [data-testid="stHorizontalBlock"]:has([data-testid="stSelectbox"]){align-items:flex-end}
[data-testid="stToggle"]{padding:8px 0;min-height:44px;display:flex;align-items:center}
@media(max-width:750px){.empty-state{padding:24px 16px;margin-top:12px;margin-bottom:12px}.metric-card{min-height:132px}.hero{margin-bottom:8px}}
.score-ring{width:60px;height:60px;position:relative;margin:8px 0}.score-ring svg{width:60px;height:60px;transform:rotate(-90deg)}.score-ring circle{fill:none;stroke-width:4}.ring-track{stroke:#DCEBE2}.ring-value{stroke:var(--primary);stroke-dasharray:100;stroke-dashoffset:calc(100 - var(--score));stroke-linecap:round;animation:ring-reveal .8s ease-out}.score-ring b{position:absolute;inset:0;display:grid;place-items:center;font-size:.8rem;color:var(--ink)}@keyframes ring-reveal{from{stroke-dashoffset:100}}.local-explanation{font-size:.7rem;color:var(--muted);margin-top:8px}.local-explanation summary{cursor:pointer;font-weight:600;color:var(--primary)}.local-explanation p{white-space:normal;line-height:1.6}.local-explanation small{font-size:.65rem}.skeletons{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.skeleton{height:160px;border-radius:16px;background:linear-gradient(90deg,#EAF4EE,#fff,#EAF4EE);background-size:200% 100%;animation:shimmer 1s infinite}@keyframes shimmer{to{background-position:-200% 0}}@media(max-width:750px){.skeletons{grid-template-columns:1fr}.skeleton{height:80px}}
</style>""",unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data(artifact_version):
    manifest=json.loads((ART/'manifest.json').read_text(encoding='utf-8'))
    tables={name:pd.read_csv(ART/f'{name}.csv') for name in ['products','rules','importance','model_metrics','ranking_metrics','mining_compare','switch_events','comparison']}
    curves=json.loads((ART/'curves.json').read_text(encoding='utf-8'))
    return manifest,tables,curves

@st.cache_resource(show_spinner=False)
def load_matrices(artifact_version):
    with np.load(ART/'matrices.npz',allow_pickle=False) as z:
        return {k:z[k] for k in z.files}

try:
    with st.spinner('Getting the shelves ready…'):
        ARTIFACT_VERSION=tuple((ART/name).stat().st_mtime_ns for name in ['manifest.json','matrices.npz','comparison.csv'])
        meta,tables,curves=load_data(ARTIFACT_VERSION); matrices=load_matrices(ARTIFACT_VERSION)
    products=tables['products']; names=products.name.to_dict()
except (OSError,ValueError,KeyError,json.JSONDecodeError) as exc:
    st.error('The catalogue is not ready. Run notebook sections 1–8 to create the artifacts, then refresh.')
    st.caption(f'Details: {type(exc).__name__}: {exc}')
    st.stop()

def esc(s): return html.escape(str(s))
def money(x): return f'${float(x):,.2f}'
def make_comparison_figure(frame,selected):
    # One interactive bar chart: the dropdown keeps unlike units off the same axis.
    metrics=['PR-AUC','ROC-AUC','F1','Precision@5','Recall@5','NDCG@5','MAP@5','Training time (s)','CV PR-AUC']
    labels=[('★ ' if name==selected else '')+('Soft Voting' if name=='Soft Voting (RF + GB + XGB)' else name) for name in frame['Model']]
    colors=['#0F7B5F' if name==selected else ('#4B7C69' if role=='Proposed' else '#5C7293')
            for name,role in zip(frame['Model'],frame['Role'])]
    fig=go.Figure()
    for i,metric in enumerate(metrics):
        values=frame[metric].astype(float).to_numpy()
        text=[f'{v:.2f}s' if metric=='Training time (s)' else f'{v:.4f}' for v in values]
        fig.add_trace(go.Bar(x=values,y=labels,orientation='h',name=metric,visible=i==0,
            marker_color=colors,text=text,textposition='outside',cliponaxis=False,customdata=frame['Model'].tolist(),
            hovertemplate='%{customdata}<br>'+metric+': %{x:.6f}<extra></extra>'))
    buttons=[]
    for i,metric in enumerate(metrics):
        maximum=float(frame[metric].max())
        buttons.append(dict(label=metric,method='update',args=[{'visible':[j==i for j in range(len(metrics))]},
            {'xaxis.title.text':metric,'xaxis.range':[0,max(1.15,maximum*1.22)],'title.text':'Model comparison · '+metric}]))
    fig.update_layout(title=dict(text='Model comparison · PR-AUC',x=0,y=.98,yanchor='top'),height=460,showlegend=False,meta={'comparison':True},
        font=dict(family='Inter',color='#4B5A52'),barcornerradius=5,
        xaxis=dict(title='PR-AUC',range=[0,1.15],showgrid=False,zeroline=False),
        yaxis=dict(autorange='reversed',automargin=True,showgrid=False),margin=dict(l=12,r=84,t=140,b=48),
        updatemenus=[dict(buttons=buttons,direction='down',x=1,y=1.15,xanchor='right',yanchor='top',
            bgcolor='white',bordercolor='#CFE3D8',font=dict(color='#193D2D'))],
        paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
    return fig

def chart(fig,key=None):
    # Presentation only: data, traces and evaluated values remain unchanged.
    heading=fig.layout.title.text or ''
    heading='<br>'.join(textwrap.wrap(heading,46))
    fig.update_layout(font=dict(family='Inter',size=12,color='#4B5A52'),
        title=dict(text=heading,font=dict(size=15,color='#193D2D'),x=0,xanchor='left'),
        margin=dict(l=12,r=84 if (fig.layout.meta or {}).get('comparison') else 12,t=140 if (fig.layout.meta or {}).get('comparison') else 68,b=48),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
        legend_title_text='',legend=dict(orientation='h',yanchor='top',y=-.22,x=0,font=dict(size=11,color='#4B5A52')),
        barcornerradius=5,colorway=[ACCENT,'#99620B','#3E65A0','#AF4035'],
        coloraxis_colorscale=[[0,'#EAF4EE'],[1,ACCENT]],coloraxis_colorbar=dict(tickfont=dict(color='#4B5A52')))
    fig.update_xaxes(showgrid=False,zeroline=False,showline=False,automargin=True,tickfont=dict(color='#4B5A52'))
    fig.update_yaxes(showgrid=False,zeroline=False,showline=False,automargin=True,tickfont=dict(color='#4B5A52'))
    st.plotly_chart(fig,width='stretch',key=key,config={'displayModeBar':False,'responsive':True})

def metric_card(container,icon,label,value,caption,help_text=''):
    with container:
        st.markdown(f'<div class="metric-card" title="{esc(help_text)}"><div class="metric-heading"><span class="metric-icon" aria-hidden="true">{icon}</span>{esc(label)}</div><div class="metric-value">{esc(value)}</div><div class="metric-caption">{esc(caption)}</div></div>',unsafe_allow_html=True)

def set_page(name):
    st.session_state['freshmatch_page']=name

def choose_example(idx):
    st.session_state['chosen_product']=int(idx)

PRODUCT_ICONS={'Milk':'🥛','Cereal':'🥣','Bread':'🍞','Coffee':'☕','Pasta':'🍝','Sauce':'🥫','Protein':'🥡','Vegetables':'🥬','Snacks':'🥨','Dips':'🫙','Fruit':'🍎','Yogurt':'🥣'}

def title(kicker,heading,description):
    st.markdown(f'<div class="eyebrow">{esc(kicker)}</div><h1>{esc(heading)}</h1>',unsafe_allow_html=True)
    st.caption(description)

@st.cache_data(show_spinner=False,max_entries=512)
def recommend(query,max_price,same_brand,same_category,k,unavailable,artifact_version=ARTIFACT_VERSION):
    if query<0 or query>=len(products):
        return pd.DataFrame()
    q=products.iloc[query]
    mask=matrices['eligible'][query].copy()
    mask &= products.price.to_numpy()<=max_price+1e-8
    if same_brand: mask &= products.brand.to_numpy()==q.brand
    if same_category: mask &= products.category.to_numpy()==q.category
    for idx in unavailable:
        if 0<=idx<len(mask): mask[idx]=False
    ids=np.flatnonzero(mask)
    ids=ids[np.argsort(-matrices['scores'][query,ids],kind='stable')][:k]
    if not len(ids): return pd.DataFrame()
    out=products.iloc[ids].copy()
    out['score']=matrices['scores'][query,ids]*100
    out['buyer_context']=matrices['context'][query,ids]*100
    out['price_saving_pct']=(1-out.price/q.price)*100
    reasons=[]
    for idx,row in out.iterrows():
        similarity=float(matrices['context'][query,idx])*100
        location='Same aisle' if row.aisle==q.aisle else 'Same department'
        change=(1-row.price/q.price)*100
        price_words=f'{change:.0f}% cheaper' if change>=1 else ('similar price' if abs(change)<1 else f'{abs(change):.0f}% higher price')
        reasons.append(f'{location}, {similarity:.0f}% similar shopping patterns, {price_words}.')
    out['reason']=reasons
    friendly={'same_category':'same category','same_aisle':'same aisle','same_department':'same department','same_brand':'same brand','text_similarity':'name similarity','context_similarity':'shopping-context similarity','log_lift':'low co-purchase lift','price_ratio':'price similarity','popularity_ratio':'popularity balance','reorder_similarity':'reorder similarity'}
    explanations=[]
    for idx in out.index:
        effects=matrices['local_effects'][query,idx]
        top=np.argsort(-np.abs(effects))[:2]
        explanations.append('; '.join(f"{friendly[str(matrices['feature_names'][j])]} {effects[j]*100:+.1f} score points" for j in top))
    out['model_explanation']=explanations
    return out

def cards(result,original_price):
    if result.empty:
        st.info('No alternatives fit these filters. Raise the price limit or switch off a brand/category filter.')
        return
    rendered=[]
    for rank,(_,row) in enumerate(result.iterrows()):
        badge='Best match' if rank==0 else ('Cheaper' if row.price_saving_pct>1 else ('Popular' if row.popularity>=products.popularity.quantile(.7) else 'Alternative'))
        difference=float(original_price)-float(row.price)
        delta=f'↓ {money(difference)} cheaper' if difference>.005 else (f'↑ {money(-difference)} more' if difference<-.005 else 'Same price')
        direction='higher' if difference<-.005 else ''
        badge_style='cheaper' if badge=='Cheaper' else ''
        rendered.append(f"""<article class="product-card"><div class="card-top"><span class="rank">{rank+1:02d}</span><span class="tile-icon" aria-hidden="true">{PRODUCT_ICONS.get(row.category,'🛒')}</span><span class="badge {badge_style}">{badge}</span></div><h3>{esc(row['name'])}</h3><div class="category">{esc(row.brand)} · {esc(row.category)}</div><div class="price-row"><span class="price">{money(row.price)}</span><span class="price-difference {direction}">{delta}</span></div><div class="score-label"><span>Match score</span><b>{row.score:.0f} / 100</b></div><div class="score-ring" role="meter" aria-label="Match score" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{row.score:.0f}"><svg viewBox="0 0 44 44" aria-hidden="true"><circle class="ring-track" cx="22" cy="22" r="18"/><circle class="ring-value" cx="22" cy="22" r="18" pathLength="100" style="--score:{row.score:.1f}"/></svg><b>{row.score:.0f}</b></div><p class="reason" title="{esc(row.reason)}">{esc(row.reason)}</p><details class="local-explanation"><summary>Why this score?</summary><p>{esc(row.model_explanation)}</p><small>Change vs training-median feature values; sensitivity, not causal or additive.</small></details></article>""")
    st.markdown('<div class="product-grid">'+''.join(rendered)+'</div>',unsafe_allow_html=True)
    st.download_button('↓ Download alternatives',result[['name','category','brand','price','score','reason','model_explanation']].to_csv(index=False).encode(),file_name='freshmatch_alternatives.csv',mime='text/csv')

PAGES=['Find Substitutes','Out-of-Stock Simulator','Product Explorer','Relationship Explorer','Model Performance','About']
NAV_ICONS=['🔎','🛒','🧺','🔗','📊','🌱']
if st.session_state.get('freshmatch_page') not in PAGES:
    st.session_state['freshmatch_page']=PAGES[0]
with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-icon" aria-hidden="true">🌿</span><span class="brand-name">Fresh<span>Match</span></span></div><div class="subbrand">GOOD ALTERNATIVES. FULLER BASKETS.</div><div class="nav-label">Your workspace</div>',unsafe_allow_html=True)
    for i,(name,icon) in enumerate(zip(PAGES,NAV_ICONS)):
        st.button(name,icon=icon,key=f'nav_{i}',type='primary' if name==st.session_state['freshmatch_page'] else 'secondary',width='stretch',on_click=set_page,args=(name,))
    data_label='Synthetic data' if meta['source']!='Instacart' else 'Instacart'
    st.markdown(f'<section class="catalogue-card"><div class="catalogue-head">YOUR CATALOGUE <span class="data-badge">{data_label}</span></div><div class="catalogue-stats"><div><strong>{len(products):,}</strong><span>products</span></div><div><strong>{products.category.nunique()}</strong><span>categories</span></div></div></section><p class="sidebar-note">{esc(meta["price_note"])}.<br>{esc(meta["brand_note"])}.</p>',unsafe_allow_html=True)
page=st.session_state['freshmatch_page']

if page=='Find Substitutes':
    st.markdown('<div class="eyebrow">YOUR NEXT BEST CHOICE</div><section class="hero"><h1>Out of stock? Still in good company.</h1><p>Thoughtful alternatives to your everyday essentials, in one quick search.</p></section>',unsafe_allow_html=True)
    left,right=st.columns([3,1.25],vertical_alignment='bottom')
    with left:
        q=st.selectbox('Find your product',options=list(names),format_func=lambda i:names[i],index=None,placeholder='Search by product or brand…',key='chosen_product',help='Start typing a product or brand to search the catalogue.')
    with right:
        oos=st.toggle('Out of stock',value=True,help='Exclude the selected item and show available alternatives immediately.')
    if q is None:
        st.markdown('<section class="empty-state"><div class="empty-illustration" aria-hidden="true">🛒</div><h2>A good swap is one search away.</h2><p>Choose an essential above, or try one of these favourites.</p></section>',unsafe_allow_html=True)
        examples=products.drop_duplicates('category').head(3)
        columns=st.columns(3)
        for col,(idx,row) in zip(columns,examples.iterrows()):
            col.button(row['name'],icon=PRODUCT_ICONS.get(row.category,'🛒'),key=f'example_{idx}',width='stretch',on_click=choose_example,args=(idx,))
    else:
        selected=products.iloc[q]
        status='Out of stock' if oos else 'Exploring alternatives'
        status_class='' if oos else 'available'
        st.markdown(f'<div class="selection"><span class="tile-icon" aria-hidden="true">{PRODUCT_ICONS.get(selected.category,"🛒")}</span><div class="selection-body"><div class="selection-label">Your selection</div><div class="selection-name">{esc(selected["name"])}</div></div><span class="selection-price">{money(selected.price)}</span><span class="stock-pill {status_class}">{status}</span></div>',unsafe_allow_html=True)
        with st.expander('Refine your alternatives',expanded=False):
            c1,c2,c3,c4=st.columns([2,1,1.2,.9],vertical_alignment='center')
            max_catalogue=round(float(products.price.max()),2)
            limit=c1.slider('Maximum price ($)',min_value=.1,max_value=max(1.,max_catalogue),value=max(1.,max_catalogue),step=.1)
            same_brand=c2.checkbox('Same brand',value=False,help=meta['brand_note'])
            same_category=c3.checkbox('Same category',value=True,help='Keep alternatives within the selected product category.')
            k=c4.selectbox('Results',[3,5,8,10],index=1)
        heading,info=st.columns([3,1],vertical_alignment='center')
        heading.subheader('A good swap starts here')
        info.caption('Match score ⓘ',help='Calibrated suitability from heuristic pair labels. This is not a purchase probability or a guarantee of dietary equivalence.')
        loading=st.empty()
        loading.markdown('<div class="skeletons"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div>',unsafe_allow_html=True)
        with st.spinner('Finding your best alternatives…'):
            result=recommend(int(q),float(limit),same_brand,same_category,k,(int(q),))
        loading.empty()
        cards(result,float(selected.price))
        with st.expander('How it works'):
            st.write('We look for products that serve a similar shopping purpose. We compare names, shared purchase patterns and prices, then avoid products people usually buy together. A higher match score means stronger evidence of suitability in our training labels.')
            st.caption('Similar shopping patterns compare co-purchase contexts; they do not mean that a stated percentage of buyers are identical. Check ingredients, allergies, pack size and dietary needs before swapping.')
            st.caption('An unavailable item is excluded. Turning the stock toggle off lets you browse the same alternatives for price or preference reasons.')

elif page=='Out-of-Stock Simulator':
    title('PLAN FOR THE UNEXPECTED','Keep the basket moving.','Test several unavailable products together and explore a clearly labelled recovery scenario.')
    unavailable=st.multiselect('Unavailable products',list(names),default=[0,24],format_func=lambda i:names[i],help='All selected products are removed from every recommendation pool.')
    c1,c2,c3=st.columns(3)
    demand=c1.number_input('Units of demand per unavailable item',min_value=1,max_value=10000,value=10,step=1)
    budget=c2.number_input('Maximum alternative price ($)',min_value=.1,max_value=1000.,value=float(np.ceil(products.price.max())),step=.5)
    only_cat=c3.checkbox('Keep the same category',value=True)
    st.caption('Scenario estimate ⓘ',help='Recovered units = units of demand × measured conditional top-5 future-switch hit rate, for covered products. It assumes that rate applies to this scenario; it is not a causal forecast.')
    if not unavailable:
        st.info('Choose one or more unavailable products to see how the basket could recover.')
    else:
        results={q:recommend(q,float(budget),False,only_cat,5,tuple(sorted(unavailable))) for q in unavailable}
        coverage=sum(not r.empty for r in results.values())/len(unavailable)
        observed=tables['ranking_metrics'].query("model == 'FreshMatch'").iloc[0]
        assumption=st.slider('Assumed customer acceptance (%)',0,100,int(round(observed.hit_rate*100)),help='Default: conditional offline hit rate. Adjust this scenario assumption; it is not a calibrated acceptance estimate.')/100
        units=demand*sum(not r.empty for r in results.values())*assumption
        revenue=demand*assumption*sum(float(r.iloc[0].price) for r in results.values() if not r.empty)
        cols=st.columns(3)
        metric_card(cols[0],'🛒','Estimated units recovered',f'{units:,.1f}','From your acceptance assumption',help_text='Scenario only: covered demand multiplied by the chosen acceptance assumption.')
        metric_card(cols[1],'💰','Estimated revenue saved',money(revenue),'Scenario estimate · not actual sales',help_text='Scenario units multiplied by each first-ranked alternative price. Prices are synthetic or estimated; no inventory capacity model is used.')
        metric_card(cols[2],'✓','Alternative coverage',f'{coverage:.0%}','Unavailable items with a suitable swap',help_text='Share of unavailable products with at least one eligible, available alternative.')
        st.caption(f'Default offline hit rate: {observed.hit_rate:.1%} (95% household-bootstrap interval {observed.hit_ci_low:.1%}–{observed.hit_ci_high:.1%}). Inventory quantities and shopper acceptance are scenario assumptions.')
        exports=[]
        for q,r in results.items():
            with st.expander(names[q],expanded=len(unavailable)<=2):
                if r.empty: st.info('No available alternatives under this price cap. Increase the cap or broaden the category filter.')
                else:
                    st.dataframe(r[['name','price','score','reason']].rename(columns={'name':'Alternative','price':'Price ($)','score':'Match / 100','reason':'Why it fits'}),hide_index=True,width='stretch')
                    exports.append(r.assign(unavailable_product=names[q]))
        if exports:
            st.download_button('↓ Download scenario',pd.concat(exports).to_csv(index=False).encode(),file_name='stockout_scenario.csv',mime='text/csv')

elif page=='Product Explorer':
    title('GET TO KNOW YOUR SHELVES','Everyday essentials, explored.','Browse the catalogue and discover what shoppers return to.')
    categories=['All categories']+sorted(products.category.unique())
    c1,c2=st.columns([1,2])
    category=c1.selectbox('Category',categories)
    search=c2.text_input('Search products',placeholder='Try coffee, milk, or a brand…',max_chars=120)
    subset=products if category=='All categories' else products[products.category==category]
    if search: subset=subset[subset.name.str.contains(search,case=False,regex=False)]
    if subset.empty: st.info('No products match that search. Try a shorter name or a different category.')
    else:
        cols=st.columns(3)
        cols[0].metric('Products',len(subset))
        cols[1].metric('Typical price',money(subset.price.median()),help=meta['price_note'])
        cols[2].metric('Repeat purchase rate',f'{subset.reorder_rate.mean():.0%}',help='Mean product reorder rate in historical purchases, not a forecast.')
        a,b=st.columns(2)
        with a:
            top=subset.nlargest(10,'popularity').sort_values('popularity')
            chart(px.bar(top,x='popularity',y='name',orientation='h',title='Most purchased essentials',labels={'popularity':'Historical item purchases','name':'Product'}))
        with b:
            chart(px.scatter(subset,x='price',y='popularity',color='category',size='reorder_rate',hover_name='name',title='Price and purchase frequency',labels={'price':'Price ($)','popularity':'Historical purchases','reorder_rate':'Repeat rate'}))
        st.dataframe(subset[['name','category','brand','price','popularity','reorder_rate']].rename(columns={'name':'Product','category':'Category','brand':'Brand','price':'Price ($)','popularity':'Purchases','reorder_rate':'Repeat rate'}),hide_index=True,width='stretch')

elif page=='Relationship Explorer':
    title('THE BIGGER PICTURE','Better together. Or instead.','See which products share a purpose and which belong in the same basket.')
    q=st.selectbox('Explore a product',list(names),format_func=lambda i:names[i])
    c1,c2=st.columns(2)
    c1.caption('Complement ⓘ',help='Products purchased together more often than expected; direct lift above 1.5.')
    c2.caption('Substitute ⓘ',help='An eligible alternative ranked by the calibrated model; this is a predicted relationship.')
    subs=recommend(int(q),float(products.price.max())+.1,False,False,5,(int(q),))
    comp_idx=np.flatnonzero((matrices['lift'][q]>1.5)&(np.arange(len(products))!=q))
    comp_idx=comp_idx[np.argsort(-matrices['lift'][q,comp_idx])][:5]
    nodes=list(dict.fromkeys([q]+subs.index.tolist()+comp_idx.tolist()))
    positions={q:(0.,0.)}
    for i,node in enumerate(nodes[1:]):
        angle=2*np.pi*i/max(1,len(nodes)-1)
        positions[node]=(np.cos(angle),np.sin(angle))
    fig=go.Figure()
    for label,ids,color in [('Substitute',subs.index.tolist(),ACCENT),('Complement',comp_idx.tolist(),'#99620B')]:
        xs=[];ys=[]
        for node in ids: xs.extend([0,positions[node][0],None]);ys.extend([0,positions[node][1],None])
        fig.add_trace(go.Scatter(x=xs,y=ys,mode='lines',line=dict(color=color,width=3),name=label,hoverinfo='skip'))
    fig.add_trace(go.Scatter(x=[positions[i][0] for i in nodes],y=[positions[i][1] for i in nodes],mode='markers+text',text=[names[i][:15]+'…' if len(names[i])>15 else names[i] for i in nodes],textfont=dict(size=10,color='#193D2D'),textposition='top center',hovertext=[names[i] for i in nodes],hoverinfo='text',marker=dict(size=[25 if i==q else 16 for i in nodes],color=['#203D31' if i==q else '#b9d9c9' for i in nodes],line=dict(color='#0F7B5F',width=2)),showlegend=False))
    fig.update_layout(title='Product relationship network · hover, pan and zoom',height=430,xaxis=dict(visible=False,range=[-1.5,1.5]),yaxis=dict(visible=False,range=[-1.4,1.4]),legend=dict(orientation='h'))
    chart(fig)
    st.subheader('Patterns in the basket')
    c1,c2,c3=st.columns([1,2,1])
    algo=c1.selectbox('Mining algorithm',['Apriori','FP-Growth'],help='Two exact frequent-itemset mining methods, run at the same support threshold.')
    term=c2.text_input('Search rules',placeholder='Filter either product name…',max_chars=120)
    min_lift=c3.number_input('Minimum lift',min_value=0.,max_value=100.,value=1.,step=.1,help='Observed co-purchase divided by expected co-purchase. Above one suggests complements.')
    rr=tables['rules']; rr=rr[(rr.algorithm==algo)&(rr.lift>=min_lift)].copy()
    rr['Product']=rr.a.map(names); rr['Bought with']=rr.b.map(names)
    if term: rr=rr[rr.Product.str.contains(term,case=False,regex=False)|rr['Bought with'].str.contains(term,case=False,regex=False)]
    if rr.empty: st.info('No rules match these filters. Lower the minimum lift or clear the search.')
    else:
        st.caption('Support ⓘ · Confidence ⓘ',help='Support: fraction of all historical baskets containing both products. Confidence: fraction of antecedent baskets that contain the consequent.')
        st.dataframe(rr[['Product','Bought with','support','confidence','lift']].sort_values('lift',ascending=False),hide_index=True,width='stretch')
        chart(px.scatter(rr,x='confidence',y='lift',size='support',hover_name='Product',hover_data=['Bought with'],title=f'{algo} · strength of co-purchase rules',labels={'confidence':'Confidence','lift':'Lift','support':'Support'}))
    mc=tables['mining_compare']
    a,b=st.columns(2)
    with a: chart(px.bar(mc,x='algorithm',y='seconds',title='Mining runtime (original computation)',labels={'algorithm':'Algorithm','seconds':'Seconds'}))
    with b: chart(px.bar(mc,x='algorithm',y='rules',title='Rules discovered',labels={'algorithm':'Algorithm','rules':'Directed rules'}))

elif page=='Model Performance':
    title('EVIDENCE, NOT GUESSWORK','A closer look at the match.','Weak-label classification and independent next-order ranking measure different things.')
    st.info('Scores below come from '+meta['source']+'. Weak labels are heuristic; the next-order benchmark is conditional on observed switches. These are offline results, not verified sales recovery.')
    comparison=tables['comparison']
    st.success('★ Deployed: '+meta['selected_model']+' · highest training-CV PR-AUC')
    st.caption('Proposed methods: Random Forest and Gradient Boosting. Comparators: Logistic Regression, XGBoost, MLPClassifier and soft voting (RF + GB + XGBoost).')
    st.caption('Selection criterion ⓘ',help='All six share the same product-disjoint train/test split and the same three CV folds. Deployment uses mean training-CV average precision, never held-out pair labels or future purchases. Exact ties keep the declared model order.')
    st.subheader('Six models, one evaluation protocol')
    def highlight_winner(row):
        return ['background-color:#EAF4EE;color:#084D39;font-weight:600' if row['Model']==meta['selected_model'] else '' for _ in row]
    st.dataframe(comparison.style.apply(highlight_winner,axis=1),hide_index=True,width='stretch',column_config={
        c:st.column_config.NumberColumn(c,format='%.2f' if c=='Training time (s)' else '%.6f')
        for c in ['ROC-AUC','PR-AUC','F1','Precision@5','Recall@5','NDCG@5','MAP@5','Training time (s)','CV PR-AUC']})
    chart(make_comparison_figure(comparison,meta['selected_model']),key='all_model_comparison')
    st.caption('Use the chart dropdown to compare metrics. ROC/PR/F1 use untouched weak-label pairs; Precision@5 and NDCG@5 use identical held-out next-order events. Training time includes search, refit and calibration; cache hits retain original times. The winning model need not win every held-out metric.')
    st.download_button('↓ Download six-model comparison',comparison.to_csv(index=False).encode(),file_name='model_comparison.csv',mime='text/csv')
    model_names=tables['model_metrics'].model.tolist()
    selected=st.selectbox('Model diagnostics',model_names,index=model_names.index(meta['selected_model']))
    m=tables['model_metrics'].set_index('model').loc[selected]
    cols=st.columns(4)
    definitions={'roc_auc':('ROC-AUC','Ability to rank positive weak-labelled pairs above negative pairs across thresholds.'),'pr_auc':('PR-AUC','Average precision: area summary of precision and recall under class imbalance.'),'f1':('F1','Harmonic mean of precision and recall at probability threshold 0.5.'),'brier':('Brier loss','Mean squared probability error on weak labels; lower is better.')}
    for col,(key,(label,tip)),icon in zip(cols,definitions.items(),['◷','↗','◎','◉']):
        metric_card(col,icon,label,f'{m[key]:.3f}','Lower is better' if key=='brier' else 'Untouched weak-label test',help_text=tip)
    c1,c2=st.columns(2)
    for container,kind in [(c1,'ROC'),(c2,'PR')]:
        with container:
            fig=go.Figure()
            for name,cur in curves['curves'].items():
                fig.add_trace(go.Scatter(x=cur['fpr' if kind=='ROC' else 'recall'],y=cur['tpr' if kind=='ROC' else 'precision'],mode='lines',name=name))
            fig.update_layout(title=f'{kind} · untouched weak-label test',xaxis_title='False positive rate' if kind=='ROC' else 'Recall',yaxis_title='True positive rate' if kind=='ROC' else 'Precision')
            chart(fig)
    c1,c2=st.columns(2)
    with c1:
        chart(px.bar(tables['importance'],x='importance',y='feature',orientation='h',title='Deployed model · permutation feature importance',labels={'importance':'Decrease in test PR-AUC','feature':'Feature'}))
        st.caption('Feature importance ⓘ',help='Permutation importance measures the decrease in test PR-AUC after shuffling each feature, averaged over three repeats. It is post-selection, descriptive and not causal. This panel shows the deployed model, '+meta['selected_model']+'.')
    with c2:
        chart(px.imshow(curves['confusion'][selected],text_auto=True,x=['Predicted no','Predicted yes'],y=['Actual no','Actual yes'],title=selected+' · confusion matrix',color_continuous_scale='Greens'))
        st.caption('Confusion matrix ⓘ',help='Counts of true/false positive/negative predictions at threshold 0.5 on held-out pair groups.')
    st.subheader('Will a shopper buy one of the alternatives next?')
    rm=tables['ranking_metrics']
    st.caption('Ranking metrics ⓘ',help='At K=5: Precision = hits/5; Recall = hits/all relevant next-order products; NDCG rewards higher positions; MAP averages precision at relevant ranks divided by all targets. Hit rate = events with any target in the top 5.')
    chart(px.bar(rm.melt(id_vars='model',value_vars=['precision_at_k','recall_at_k','ndcg_at_k','map_at_k']),x='variable',y='value',color='model',barmode='group',title='Next-order ranking vs identical-pool baselines',labels={'variable':'Metric @ 5','value':'Score'}))
    st.dataframe(rm,hide_index=True,width='stretch')
    row=rm[rm.model=='FreshMatch'].iloc[0]
    st.caption(f'{int(row.events):,} observed switching events · future target eligible in {row.target_coverage:.1%} of events · top-5 hit rate {row.hit_rate:.1%}, 95% household-bootstrap interval {row.hit_ci_low:.1%}–{row.hit_ci_high:.1%}.')
    with st.expander('Evaluation details and limitations'):
        for limitation in meta['limitations']: st.write('• '+limitation)
        st.write('Training and test pairs have disjoint unordered pair IDs. Products may occur in both. Feature construction uses only historical baskets; final orders are held out. Model selection uses training CV, not test scores. Future switching events need at least one observed alternative, so the measured hit rate should not be generalized to every stockout.')
        st.write('Prices are estimates; offline revenue is a proxy. All candidate products compete without inserting the future target. The same candidate policy is applied to all three ranking systems.')
    st.download_button('↓ Download ranking evaluation',rm.to_csv(index=False).encode(),file_name='ranking_metrics.csv',mime='text/csv')

elif page=='About':
    title('PURPOSE BUILT','A better alternative to an empty basket.','AI-Powered Product Substitution Discovery and Intelligent Alternative Recommendation Using Machine Learning')
    st.markdown('When a product is unavailable or too expensive, shoppers need something that fills the same need. FreshMatch combines product information with purchase patterns to offer useful alternatives and explain each choice.')
    st.subheader('From basket history to a better swap')
    st.graphviz_chart('digraph { rankdir=LR; node [shape=box,style="rounded,filled",fillcolor="#EDF4ED",fontname="Arial",color="#CFE0D2"]; A [label="History + products"]; B [label="Complement rules"]; C [label="Context + text + price"]; D [label="Weak pair labels"]; E [label="Tune + calibrate"]; F [label="Available alternatives"]; A -> B; A -> C; B -> C; C -> D; D -> E; E -> F; }')
    st.markdown('<div class="mobile-method" role="img" aria-label="Historical baskets and products feed complement rules and context, text and price features; weak pair labels train and calibrate models that rank available alternatives."><div class="method-step"><span>01</span>History + products</div><div class="method-arrow" aria-hidden="true">↓</div><div class="method-step"><span>02</span>Complement rules</div><div class="method-arrow" aria-hidden="true">↓</div><div class="method-step"><span>03</span>Context + text + price</div><div class="method-arrow" aria-hidden="true">↓</div><div class="method-step"><span>04</span>Weak pair labels</div><div class="method-arrow" aria-hidden="true">↓</div><div class="method-step"><span>05</span>Tune + calibrate</div><div class="method-arrow" aria-hidden="true">↓</div><div class="method-step"><span>06</span>Available alternatives</div></div>',unsafe_allow_html=True)
    st.caption('Association mining ⓘ · Calibration ⓘ',help='Association mining identifies frequent co-purchases. Calibration maps model outputs onto observed weak-label frequencies; it does not calibrate purchase acceptance.')
    a,b=st.columns(2)
    with a:
        st.subheader('What makes it different')
        st.write('Shared purpose and low co-purchase, rather than co-purchase alone. Price-aware filtering, plain-language reasons, multiple-stockout handling and transparent comparisons against simple baselines.')
        st.subheader('Built with')
        st.write('Python · pandas · SciPy · scikit-learn · MLxtend · Plotly · Streamlit · TF-IDF · Apriori · FP-Growth · Random Forest · Gradient Boosting · Logistic Regression · XGBoost · MLPClassifier · Soft Voting')
    with b:
        st.subheader('The team')
        st.write('**K. Darshan Sai**  \nRA2311027010002')
        st.write('**J. Ranga Mokshagna**  \nRA2311027010003')
        st.write('**P. Bharat Sai**  \nRA2311027010007')
        st.subheader('Dataset transparency')
        st.write(meta['source'])
        st.caption(f"{meta['history_baskets']:,} historical baskets · {meta['future_baskets']:,} future baskets · seed {meta['seed']}")
        st.caption(meta['price_note']+'. '+meta['brand_note']+'.')
    with st.expander('Responsible interpretation'):
        for limitation in meta['limitations']: st.write('• '+limitation)
        st.write('No nutritional, allergen or pack-size equivalence is guaranteed. Verify the product before buying. Ingredient data are outside this dataset.')

st.markdown('<div class="footnote">FreshMatch · K. Darshan Sai · J. Ranga Mokshagna · P. Bharat Sai</div>',unsafe_allow_html=True)
