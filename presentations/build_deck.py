"""Build an editable 10-slide PPTX and matching SVG/HTML preview from project evidence."""
from pathlib import Path
import base64
import html
import json
import textwrap
from PIL import Image, ImageFont
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).resolve().parent
SHOTS=OUT/'screenshots'
PREVIEW=OUT/'preview'
PREVIEW.mkdir(exist_ok=True)
REPORT=json.loads((ROOT/'artifacts/advanced_report.json').read_text())
META=json.loads((ROOT/'artifacts/manifest.json').read_text())
assert META['source']==REPORT['source']=='Instacart'
BG='F6F8F4'; INK='183B2D'; GREEN='0F7B5F'; MINT='E6F0E8'; MUTED='56675F'; LINE='D9E3DA'; WHITE='FFFFFF'; AMBER='A56C23'
W,H=1600,900
prs=Presentation();prs.slide_width=Inches(W/120);prs.slide_height=Inches(H/120)
prs.core_properties.title='FreshMatch — Real-data ML project'
prs.core_properties.subject='Explainable grocery substitution using real Instacart purchase records'
prs.core_properties.author='FreshMatch team'
prs.core_properties.keywords='Instacart, XGBoost, LambdaMART, Streamlit, real data'
FONT='/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
BOLD='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'
all_slides=[];content=[]


def rgb(value):return RGBColor.from_string(value)
def u(v):return Inches(v/120)
def wrap_lines(text,width,size,bold=False):
    font=ImageFont.truetype(BOLD if bold else FONT,int(size))
    lines=[]
    for raw in text.split('\n'):
        if not raw:lines.append('');continue
        line=''
        for word in raw.split():
            candidate=(line+' '+word).strip()
            if font.getlength(candidate)>width and line:
                lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    return lines

class Slide:
    def __init__(self,title,section,notes,dark=False):
        self.s=prs.slides.add_slide(prs.slide_layouts[6]);self.svg=[];self.index=len(prs.slides)
        self.dark=dark;self.bg=INK if dark else BG
        self.s.background.fill.solid();self.s.background.fill.fore_color.rgb=rgb(self.bg)
        self.svg.append(f'<rect width="{W}" height="{H}" fill="#{self.bg}"/>')
        self.s.notes_slide.notes_text_frame.text=notes
        content.append((self.index,title,notes))
        if not dark:
            self.text('FRESHMATCH  /  '+section.upper(),80,48,1400,20,GREEN,True)
            self.text(title,80,98,1440,52,INK,True)
            self.line(80,183,1520,183,LINE,1)
        self.text('FreshMatch · Real Instacart study',80,850,1000,16,'B8CDC0' if dark else MUTED)
        self.text(f'{self.index:02d} / 10',1400,850,120,16,'B8CDC0' if dark else MUTED,align='right')
        all_slides.append(self)
    def rect(self,x,y,w,h,fill=WHITE,stroke=None,r=18):
        assert x>=0 and y>=0 and x+w<=W+1 and y+h<=H+1,(x,y,w,h)
        shape=self.s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if r else MSO_SHAPE.RECTANGLE,u(x),u(y),u(w),u(h))
        if r:
            try:shape.adjustments[0]=min(.15,r/min(w,h))
            except Exception:pass
        shape.fill.solid();shape.fill.fore_color.rgb=rgb(fill)
        if stroke:shape.line.color.rgb=rgb(stroke);shape.line.width=Pt(.7)
        else:shape.line.fill.background()
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#{fill}" stroke="#{stroke or fill}"/>')
        return shape
    def line(self,x1,y1,x2,y2,color=LINE,width=1):
        from pptx.enum.shapes import MSO_CONNECTOR
        line=self.s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,u(x1),u(y1),u(x2),u(y2))
        line.line.color.rgb=rgb(color);line.line.width=Pt(width*.6)
        self.svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#{color}" stroke-width="{width}"/>')
    def text(self,text,x,y,w,fs=28,color=INK,bold=False,align='left',leading=None):
        leading=leading or fs*1.24
        lines=wrap_lines(text,w,fs,bold)
        height=len(lines)*leading+5
        assert y+height<=H+1,(text,y,height)
        font=ImageFont.truetype(BOLD if bold else FONT,int(fs))
        assert all(font.getlength(line)<=w+3 for line in lines),(text,w)
        box=self.s.shapes.add_textbox(u(x),u(y),u(w),u(height))
        tf=box.text_frame;tf.clear();tf.word_wrap=False
        tf.margin_left=tf.margin_right=tf.margin_top=tf.margin_bottom=0
        tf.vertical_anchor=MSO_ANCHOR.TOP
        for i,line in enumerate(lines):
            p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
            p.text=line;p.font.name='Arial';p.font.size=Pt(fs*.6);p.font.bold=bold;p.font.color.rgb=rgb(color)
            p.space_before=p.space_after=Pt(0);p.line_spacing=Pt(leading*.6)
            p.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}[align]
            tx=x if align=='left' else (x+w/2 if align=='center' else x+w)
            anchor={'left':'start','center':'middle','right':'end'}[align]
            self.svg.append(f'<text x="{tx}" y="{y+i*leading+fs*.89}" font-family="Arial, Liberation Sans, sans-serif" font-size="{fs}" font-weight="{700 if bold else 400}" fill="#{color}" text-anchor="{anchor}">{html.escape(line)}</text>')
        return height
    def image(self,name,x,y,w,h,border=True):
        path=SHOTS/name
        iw,ih=Image.open(path).size
        if border:self.rect(x-8,y-8,w+16,h+16,WHITE,LINE,12)
        scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
        px,py=x+(w-dw)/2,y+(h-dh)/2
        self.s.shapes.add_picture(str(path),u(px),u(py),width=u(dw),height=u(dh))
        encoded=base64.b64encode(path.read_bytes()).decode()
        self.svg.append(f'<image x="{px}" y="{py}" width="{dw}" height="{dh}" href="data:image/png;base64,{encoded}"/>')
    def bullet(self,label,body,x,y,w):
        self.rect(x,y+8,8,8,GREEN,r=4)
        self.text(label,x+26,y,w-26,30,INK,True)
        self.text(body,x+26,y+45,w-26,25,MUTED)
    def save_svg(self):
        return '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900">'+''.join(self.svg)+'</svg>'

# 01 — Title
s=Slide('FreshMatch','Title',
'''Introduce FreshMatch as an explainable grocery substitution workbench. The current demonstration uses real Instacart product and purchase records. Our experiment selects 320 products and 3,000 households; this is a bounded research sample, not the full retail universe. Prices are estimates and brand strings are name-token proxies. The screenshots in this presentation were freshly captured from the real-data app.''',True)
s.text('GROCERY SUBSTITUTION WORKBENCH',80,88,670,22,'A9D3BC',True)
s.text('FreshMatch',80,180,720,106,WHITE,True)
s.text('Explainable grocery swaps\nusing machine learning',84,320,665,44,WHITE)
s.text('Real purchase records. Clear comparisons.\nA working app you can inspect.',84,468,645,28,'D4E5D9')
s.line(84,586,695,586,'426453')
s.text('PROJECT TEAM',84,617,640,18,'A9D3BC',True)
s.text('K. Darshan Sai  ·  RA2311027010002\nJ. Ranga Mokshagna  ·  RA2311027010003\nP. Bharat Sai  ·  RA2311027010007',84,658,675,24,WHITE,leading=36)
s.rect(815,108,725,620,WHITE,r=20)
s.text('THE REAL-DATA APP',844,137,665,20,GREEN,True)
s.image('01-find-substitutes.png',835,190,685,475,False)
s.text('Python  ·  XGBoost  ·  LambdaMART  ·  Streamlit',835,691,680,19,MUTED)

# 02 — Problem
s=Slide('A missing item should not end the basket','Problem',
'''Example: a shopper wants organic milk and their preferred item is unavailable. We suggest same-aisle candidates, show an estimated price difference, and explain suitability. Products bought together are often complements, not replacements, so co-purchase alone is not our substitute rule. We do not promise nutritional equivalence, dietary safety or actual sales recovery.''')
for x,n,title,body in [(80,'01','A shopper needs milk','The preferred product is unavailable.'),(590,'02','Several choices exist','Names and prices alone are not enough.'),(1100,'03','A useful swap is needed','Show relevant, available alternatives.')]:
    s.rect(x,240,420,300,WHITE,LINE)
    s.text(n,x+28,266,360,26,GREEN,True)
    s.text(title,x+28,326,362,34,INK,True)
    s.text(body,x+28,425,355,27,MUTED)
s.text('→',517,351,52,48,GREEN,True);s.text('→',1027,351,52,48,GREEN,True)
s.rect(80,595,1440,165,MINT,r=18)
s.text('Our goal',112,620,250,28,GREEN,True)
s.text('Find plausible alternatives, explain the match, and let the user control price and availability.',112,668,1360,34,INK,True)

# 03 — Data
s=Slide('Real Instacart records, with a clear study sample','Dataset',
'''The source has 49,688 products across 134 aisles. We sample whole households, then select 320 products by historical purchase frequency. Each household’s last available prior order is held out; earlier prior orders form history. The experiment uses 49,760 historical baskets and 3,000 final baskets from 3,000 households. Source hashes are recorded. These are not Kaggle’s hidden competition test labels. Instacart does not contain observed prices or verified brands.''')
for x,y,value,label in [(80,235,'49,688','products in the source'),(435,235,'320','products in this study'),(80,420,'3,000','sampled households'),(435,420,'49,760','historical baskets')]:
    s.rect(x,y,325,150,WHITE,LINE)
    s.text(value,x+24,y+22,280,51,GREEN,True)
    s.text(label,x+24,y+99,280,24,MUTED)
s.text('3,000 final baskets are held out.\nThe selected catalogue spans 51 aisles.',80,617,670,28,INK)
s.rect(80,717,680,72,MINT,r=12);s.text('Real purchases; estimated prices and brand proxies.',101,737,640,22,INK)
s.image('03-products.png',820,237,685,476)
s.text('Product Explorer · current real-data catalogue',820,743,690,23,MUTED)

# 04 — Pipeline
s=Slide('From basket history to an explained recommendation','Pipeline',
'''Data validation checks schemas, identifiers, references and LFS content. Historical baskets feed Apriori and FP-Growth complement mining and pair-feature construction. Weak heuristic labels train suitability models; an independent behavioral ranking experiment learns historical switching. Eligibility, price and availability filters are applied when serving candidates. The notebook writes portable inference artifacts consumed by Streamlit. Historical features remain shared across households, so evaluation is transductive.''')
steps=[('01','Validate records','CSV schemas and\nsource hashes'),('02','Learn relationships','Names, shopping\ncontext and co-purchase'),('03','Train and compare','Six classifiers and\na behavioral ranker'),('04','Apply user filters','Same aisle, price cap\nand unavailable items'),('05','Explain the result','Ranked alternatives\nwith clear reasons')]
for i,(num,title,body) in enumerate(steps):
    x=80+i*294
    s.rect(x,260,263,290,WHITE,LINE)
    s.text(num,x+22,281,218,24,GREEN,True)
    s.text(title,x+22,335,218,32,INK,True)
    s.text(body,x+22,438,219,24,MUTED)
    if i<4:s.text('→',x+267,365,29,26,GREEN,True)
s.text('Signals used by the models',80,609,1440,31,INK,True)
for x,title,body in [(80,'Product information','Category and TF-IDF name similarity'),(580,'Shopping behavior','Context, lift and reorder patterns'),(1080,'Relative fit','Estimated price and popularity ratios')]:
    s.text(title,x,672,430,26,GREEN,True);s.text(body,x,715,430,24,MUTED)

# 05 — Models
s=Slide('Two learning tasks: suitability and behavior','Models',
'''The six classifiers are Random Forest, Gradient Boosting, Logistic Regression, XGBoost, MLPClassifier and RF/GB/XGB soft voting. Training-CV average precision chooses XGBoost for the main app; sigmoid calibration maps outputs to weak-label frequencies, not acceptance probabilities. LambdaMART uses XGBRanker with rank:ndcg on historical switches. Four configurations compete on validation NDCG@5; depth 2 and 160 trees are selected. No test scores choose either deployed classifier or ranker configuration.''')
s.rect(80,230,700,555,WHITE,LINE)
s.text('SUITABILITY',110,258,640,21,GREEN,True)
s.text('Six models, the same evaluation rules',110,303,630,35,INK,True)
s.text('Random Forest  ·  Gradient Boosting\nLogistic Regression  ·  XGBoost\nMLP  ·  Soft voting',110,376,630,27,MUTED,leading=42)
s.rect(109,557,640,87,MINT,r=12)
s.text('Main app: calibrated XGBoost',132,582,590,31,GREEN,True)
s.text('Selected by training-CV average precision.\nScores follow rule-based training labels.',110,676,624,26,MUTED)
s.rect(820,230,700,555,INK,r=18)
s.text('BEHAVIORAL RANKING',852,258,630,21,'A9D3BC',True)
s.text('LambdaMART',852,312,630,55,WHITE,True)
s.text('Learns which alternatives appear\nin later purchase records.',852,407,625,31,WHITE)
s.line(852,515,1487,515,'426453')
s.text('8,840 training groups\n147,340 candidate rows',852,550,625,30,'D4E5D9',leading=43)
s.text('Selected on validation NDCG@5:\ndepth 2, 160 trees.',852,676,625,26,'D4E5D9')

# 06 — Evaluation
s=Slide('Train, choose and test on separate groups','Evaluation',
'''Classifier partitions are product-disjoint at both endpoints and purge crossing pairs. Seeded category-balanced assignments use label counts only to guarantee at least five examples of each class per retained partition. The outer test has 266 pairs but only five positive weak labels, so classification scores are fragile. Behavioral households split 70/15/15: 2,100 train, 450 validation, 450 reserved test. There are 384 validation and 365 test switching events; only 163 reserved test households generate qualifying events. Historical features use all households: transductive rather than fully inductive evaluation.''')
s.text('Suitability models: keep products separate',80,228,1440,31,INK,True)
for x,w,label,body in [(80,450,'2,036 train pairs','Training with three validation folds'),(570,450,'266 test pairs','Train and test use different products'),(1060,460,'1,532 pairs removed','Pairs crossing the split are removed')]:
    s.rect(x,284,w,145,WHITE,LINE);s.text(label,x+24,308,w-48,32,GREEN,True);s.text(body,x+24,367,w-48,23,MUTED)
s.text('Behavioral ranker: keep households separate',80,480,1440,31,INK,True)
for x,w,label,body in [(80,450,'2,100 train households','Historical switches fit the ranker'),(570,450,'450 validation households','384 events choose the configuration'),(1060,460,'450 test households','365 events from 163 households')]:
    s.rect(x,538,w,145,MINT);s.text(label,x+24,561,w-48,30,INK,True);s.text(body,x+24,621,w-48,23,MUTED)
s.rect(80,728,1440,74,'F3E9D9',r=12)
s.text('Limits: only 5 test pairs labelled as good swaps; history features still use all households.',103,751,1390,24,'74501F')

# 07 — Shopper experience
s=Slide('Find a swap, then test a stockout scenario','App demo · shopper pages',
'''The screenshots are actual captures of the current real-data app. Find Substitutes searches Organic Milk, ranks eligible alternatives and shows model sensitivities, estimated price differences and exports. Out-of-Stock Simulator excludes multiple products and uses an explicitly chosen acceptance assumption to estimate units/revenue; it is not observed recovery. Product Explorer, shown on the data slide, adds category and purchase-frequency views. Main-card scores are suitability, not purchase probabilities.''')
s.image('01-find-substitutes.png',88,239,870,576)
s.image('02-stockout.png',1010,244,502,349)
s.text('Find Substitutes',1010,628,500,32,GREEN,True)
s.text('Search, filter and read the reason\nfor each suggested alternative.',1010,676,500,26,MUTED)
s.text('Stockout Simulator',1010,756,500,28,GREEN,True)
s.text('Explore an assumed recovery scenario.',1010,798,500,22,MUTED)

# 08 — Explainability
s=Slide('Show the relationship—and the evidence behind it','App demo · evidence pages',
'''Relationship Explorer separates complements (frequently purchased together) from predicted eligible alternatives. Main-card occlusion sensitivities compare one feature with its training median; they are not additive or causal explanations. Model Performance compares six models, ROC/PR, confusion matrices, permutation importance and future ranking baselines. These screenshots are genuine real-data app captures. ML Lab is shown on the next slide. About records the method, team and limitations.''')
s.image('04-relationships.png',88,242,870,576)
s.image('05-models.png',1010,245,502,349)
s.text('Different relationships',1010,630,500,31,GREEN,True)
s.text('Complements are bought together.\nSubstitutes are possible replacements.',1010,676,500,25,MUTED)
s.text('Model Performance',1010,759,500,28,GREEN,True)
s.text('Compare results, errors and feature influence.',1010,800,500,21,MUTED)

# 09 — Results
s=Slide('The ranker improves on suitability; popularity still leads','Real-data results',
'''All five methods below use the same 365 held-out switching events and eligible candidate pools. NDCG@5 rewards placing observed relevant products nearer the top; higher is better. Behavioral LambdaMART is 0.1294 and the weak-label classifier is 0.0647. Their paired household-bootstrap difference is +0.0647 with 95% interval [+0.0437,+0.0859]. Popularity is higher at 0.1409, so we do not claim the learned ranker is best. Only 36.7% of events have any relevant target inside eligibility; excluded targets remain in metric denominators. These are proxy switches, not confirmed substitutions or causal recovered sales.''')
s.text('Ranking quality (NDCG@5) · higher is better',80,225,760,27,GREEN,True)
metrics=REPORT['test_metrics']; short=['Behavioral ranker','Suitability model','Name similarity','Shopping context','Popularity']
for i,(r,label) in enumerate(zip(metrics,short)):
    y=294+i*83;value=r['ndcg_at_k'];color=GREEN if i==0 else (AMBER if i==4 else '8AA598')
    s.text(label,80,y+6,265,25,INK,i in [0,4]);s.rect(363,y+6,380,32,'E6ECE5',r=4)
    s.rect(363,y+6,380*value/.16,32,color,r=4);s.text(f'{value:.4f}',759,y+4,120,26,color,True)
s.text('Same 365 test events · observed purchase switches',80,746,775,22,MUTED)
s.image('06-ml-lab.png',940,240,570,396)
s.rect(940,668,570,126,MINT,r=12)
s.text('36.7% target coverage',961,688,525,30,INK,True)
s.text('Better candidate coverage is the next priority.',961,739,525,23,MUTED)

# 10 — Conclusion
s=Slide('A working research project, with clear next steps','Conclusion',
'''Conclude with evidence rather than an inflated success claim. All 23 local tests pass, covering all seven app pages plus splits, input data, scores and uncertainty. The project is reproducible and uses real purchase records. The next experiment should address candidate eligibility/coverage; additional expert substitute labels, observed price/pack-size/ingredient information and prospective acceptance testing are needed. Brand tokens and estimated prices are not verified retail data. The About page makes those boundaries visible. Invite questions.''')
s.rect(80,230,700,115,MINT,r=16)
s.text('23 tests passed',106,252,640,45,GREEN,True)
s.text('Seven working pages · reproducible real-data run',108,312,630,23,MUTED)
s.bullet('What works','Real purchase data, explained suggestions and transparent evaluation.',80,394,700)
s.bullet('What comes next','Wider candidate coverage, expert labels and real price / ingredient data.',80,531,700)
s.bullet('Limits to remember','Prices are estimates; dietary safety and actual sales recovery are unverified.',80,669,700)
s.image('07-about.png',848,243,660,458)
s.text('Thank you. Questions?',848,752,660,40,INK,True)

# Output: editable PPTX, matching vector preview, and concise speaker notes.
PPT=OUT/'FreshMatch_Project_Presentation.pptx'
prs.save(PPT)
for slide in all_slides:
    (PREVIEW/f'slide-{slide.index:02d}.svg').write_text(slide.save_svg())
html_doc='''<!doctype html><html><head><meta charset="utf-8"><title>FreshMatch presentation</title><style>
@page { size: 13.333333in 7.5in; margin:0; }
* { box-sizing:border-box; } html,body{margin:0;padding:0;background:#dce4dc;}
.slide{width:1600px;height:900px;break-after:page;overflow:hidden;margin:0;}
.slide svg{display:block;width:100%;height:100%;}
@media print{.slide{width:13.333333in;height:7.5in;}}
</style></head><body>'''+''.join('<section class="slide" id="slide-'+str(s.index)+'">'+s.save_svg()+'</section>' for s in all_slides)+'</body></html>'
(OUT/'FreshMatch_Presentation_Preview.html').write_text(html_doc)
(OUT/'Speaker_Notes.md').write_text('# FreshMatch — speaker notes\n\n'+''.join(f'## {i}. {title}\n\n{notes}\n\n' for i,title,notes in content))
(OUT/'README.md').write_text('''# FreshMatch presentation

- `FreshMatch_Project_Presentation.pptx`: editable, 10-slide 16:9 PowerPoint.
- `FreshMatch_Project_Presentation.pdf`: matching PDF preview.
- `Speaker_Notes.md`: plain-English presentation notes, also embedded in PowerPoint.
- `screenshots/`: fresh captures of all seven real-data app pages.
- `build_deck.py`: source for reproducible PowerPoint and preview generation.

To edit in Canva: open Canva, choose **Create a design → Import file**, and upload
the PPTX. If that option differs in your interface, use Canva's Upload/Import
control. Text, diagrams and chart bars are editable PowerPoint objects;
screenshots remain images. Check fonts and spacing after import.

All numbers come from the project's current Instacart artifacts. Prices are
estimates, brand labels are proxies, and observed switches are not confirmed
substitutions. The popularity baseline leads on the reported real-data test.
''')
assert len(prs.slides)==10
print('Created',PPT,'with',len(prs.slides),'slides')
