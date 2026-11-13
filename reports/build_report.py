"""Create a reference-style A4 academic PDF and editable DOCX for FreshMatch."""
from pathlib import Path
import json,html,re,math,hashlib
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import Paragraph,Table,TableStyle,Image as RLImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from docx.shared import Pt,Inches,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from html.parser import HTMLParser
from PIL import Image
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from report_content import PAGES,AUTHORS,TITLE,FRESH,HYBRID,META
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent;ASSETS=OUT/'assets'
ASSETS.mkdir(exist_ok=True)
PROFILE_PATH=OUT/'report_profile.json'
if not PROFILE_PATH.exists():
    PROFILE_PATH.write_text(json.dumps({'guide_name':'','guide_title':'','head_name':'','department':'Department of Data Science and Business Systems','institution':'SRM Institute of Science and Technology','college':'College of Engineering and Technology','location':'Kattankulathur - 603 203','degree':'Bachelor of Technology','programme':'Computer Science and Engineering','specialisation':'Big Data Analytics','month_year':'November 2026'},indent=2)+'\n')
PROFILE=json.loads(PROFILE_PATH.read_text())
FONTS=Path('/usr/share/fonts/truetype/liberation')
for name,file in [('TNR','LiberationSerif-Regular.ttf'),('TNR-B','LiberationSerif-Bold.ttf'),('TNR-I','LiberationSerif-Italic.ttf'),('TNR-BI','LiberationSerif-BoldItalic.ttf'),('Mono','LiberationMono-Regular.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(FONTS/file)))
pdfmetrics.registerFontFamily('TNR',normal='TNR',bold='TNR-B',italic='TNR-I',boldItalic='TNR-BI')
W,H=A4;LEFT=56;RIGHT=54;CW=W-LEFT-RIGHT;TOP=H-86;BOTTOM=92
STYLE={
 'p':ParagraphStyle('Body',fontName='TNR',fontSize=11.7,leading=19.2,alignment=TA_JUSTIFY,spaceAfter=8),
 'h':ParagraphStyle('Section',fontName='TNR-B',fontSize=13.2,leading=17.4,alignment=TA_LEFT,spaceAfter=7,spaceBefore=6),
 'title':ParagraphStyle('Title',fontName='TNR-B',fontSize=15.8,leading=20,alignment=TA_LEFT,spaceAfter=14),
 'caption':ParagraphStyle('Caption',fontName='TNR-I',fontSize=10.5,leading=14,alignment=TA_LEFT,spaceAfter=10),
 'cell':ParagraphStyle('Cell',fontName='TNR',fontSize=10.1,leading=12.8,alignment=TA_LEFT),
 'cellhead':ParagraphStyle('Head',fontName='TNR-B',fontSize=10.1,leading=12.8,alignment=TA_LEFT),
 'reference':ParagraphStyle('Reference',fontName='TNR',fontSize=10.7,leading=15.3,alignment=TA_LEFT,spaceAfter=8),
 'equation':ParagraphStyle('Equation',fontName='TNR',fontSize=11.4,leading=17,alignment=TA_CENTER,spaceAfter=9),
 'code':ParagraphStyle('Code',fontName='Mono',fontSize=9.0,leading=12.4,alignment=TA_LEFT,spaceAfter=8)}

def markup(text):
    text=html.escape(str(text),quote=False)
    for tag in ['b','/b','i','/i','sub','/sub','sup','/sup','br','br/']:
        text=text.replace('&lt;'+tag+'&gt;','<'+tag+'>')
    return text

def generate_figures():
    plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif'],'font.size':11})
    green='#0f7b5f';gray='#53645c'
    fig,ax=plt.subplots(figsize=(11.5,3.45));ax.set_xlim(0,11.5);ax.set_ylim(0,3.45);ax.axis('off')
    labels=[('Real CSVs','Schema and source audit'),('History features','Names, context, transitions'),('Learn and blend','Validation-only selection'),('Apply restrictions','Same aisle, price, outages'),('Explain results','Rank + suitability signal')]
    for i,(a,b) in enumerate(labels):
        x=.08+i*2.3
        ax.add_patch(FancyBboxPatch((x,1.3),2.1,1.35,boxstyle='round,pad=0.03',facecolor='#edf4ef',edgecolor=green,lw=1))
        ax.text(x+1.05,2.23,a,ha='center',va='center',fontweight='bold',fontsize=12)
        ax.text(x+1.05,1.7,b.replace(', ','\n').replace(' and ','\nand ') if i in [0,3] else b.replace(', ','\n'),ha='center',va='center',fontsize=9)
        if i<4:ax.annotate('',xy=(x+2.28,1.98),xytext=(x+2.1,1.98),arrowprops={'arrowstyle':'->','color':gray,'lw':1.5})
    ax.text(5.75,.64,'Recorded artifacts and fixed evaluation protocol support every stage.',ha='center',fontsize=11,color=gray)
    fig.savefig(ASSETS/'workflow.png',dpi=200,bbox_inches='tight',facecolor='white');plt.close(fig)
    fig,ax=plt.subplots(figsize=(11,4.1));ax.set_xlim(0,11);ax.set_ylim(0,4.1);ax.axis('off')
    data=[(.15,2.65,3.3,'TRAIN','2,100 accounts\nHistorical transitions'),(3.85,2.65,3.3,'VALIDATE','450 accounts / 384 events\nChoose tree and blend settings'),(7.55,2.65,3.3,'REFERENCE TEST','450 accounts / 365 events\nRetrospective development evidence')]
    for x,y,w,label,body in data:
        ax.add_patch(FancyBboxPatch((x,y),w,1.15,boxstyle='round,pad=0.03',facecolor='#edf4ef',edgecolor=green,lw=1))
        ax.text(x+w/2,y+.87,label,ha='center',fontweight='bold',fontsize=10)
        ax.text(x+w/2,y+.38,body,ha='center',fontsize=10,va='center')
    ax.text(5.5,2.12,'Freeze selected weights, score hashes and the new-household protocol',ha='center',fontweight='bold',fontsize=11)
    ax.annotate('',xy=(5.5,1.52),xytext=(5.5,1.94),arrowprops={'arrowstyle':'->','color':green,'lw':1.5})
    ax.add_patch(FancyBboxPatch((1.0,.15),9,1.3,boxstyle='round,pad=0.03',facecolor='#f7f7f3',edgecolor=green,lw=1))
    ax.text(5.5,1.12,'NEW, DISJOINT HOUSEHOLDS',ha='center',fontweight='bold',fontsize=12)
    ax.text(5.5,.67,'5,000 sampled accounts  →  1,888 qualifying accounts  →  4,594 events',ha='center',fontsize=11)
    ax.text(5.5,.32,'Same candidate pool for every compared method; no fitting on these outcomes.',ha='center',fontsize=10)
    fig.savefig(ASSETS/'evaluation.png',dpi=200,bbox_inches='tight',facecolor='white');plt.close(fig)
    rows=FRESH['test_metrics'];names=[r['model'].replace('Content similarity','Name similarity') for r in rows]
    values=[r['ndcg_at_k'] for r in rows]
    fig,ax=plt.subplots(figsize=(10.8,4.4))
    y=list(range(len(rows)));cs=[green if i==0 else '#a56c23' if r['model']=='Popularity' else '#8aa598' for i,r in enumerate(rows)]
    ax.barh(y,values,color=cs,height=.56)
    ax.errorbar(values,y,xerr=[[r['ndcg_at_k']-r['ndcg_ci_low'] for r in rows],[r['ndcg_ci_high']-r['ndcg_at_k'] for r in rows]],fmt='none',ecolor='#323d37',capsize=3,lw=1)
    ax.set_yticks(y,names);ax.invert_yaxis();ax.set_xlim(0,.17)
    ax.set_xlabel('NDCG@5 (higher is better)');ax.grid(axis='x',color='#e3e7e3',lw=.6);ax.set_axisbelow(True)
    ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
    fig.tight_layout();fig.savefig(ASSETS/'ranking-results.png',dpi=220,facecolor='white');plt.close(fig)

def cover_blocks():
    guide=PROFILE['guide_name'] or '____________________________'
    designation=PROFILE['guide_title'] or 'Project Supervisor'
    def c(t,size=12,bold=False,after=0):return {'type':'center','text':t,'size':size,'bold':bold,'after':after}
    return [c('FRESHMATCH\nAI-POWERED PRODUCT SUBSTITUTION DISCOVERY\nAND INTELLIGENT ALTERNATIVE RECOMMENDATION\nUSING MACHINE LEARNING',14,True,14),
      c('ADVANCED MACHINE LEARNING - PROJECT REPORT',14,True,16),c('Submitted by',12,False,8),
      c('\n'.join(n+' ('+r+')' for n,r in AUTHORS),12.8,True,12),c('Under the Guidance of',11,False,0),c(guide,12.5,True,0),
      c(designation,10.5,False,0),c(PROFILE['department'],9.8,False,18),
      c('in partial fulfilment of the requirements for the degree of',12,False,7),c(PROFILE['degree'].upper(),15,True,0),
      c('in',12,False,0),c(PROFILE['programme'].upper(),14,True,0),c('with specialization in '+PROFILE['specialisation'],12,False,10),
      {'type':'logo','height':50,'after':15},c(PROFILE['department'].upper(),11.3,True,12),
      c(PROFILE['college'].upper(),12,True,10),c(PROFILE['institution'].upper(),12,True,8),
      c(PROFILE['location'].upper(),11.5,False,10)]

def front_blocks(kind):
    if kind=='cover':return cover_blocks()
    if kind=='declaration':
        return [{'type':'logo','height':35,'after':5},
          {'type':'center','text':PROFILE['department'],'size':11.5,'after':0},
          {'type':'center','text':PROFILE['institution'],'size':12.5,'bold':True,'after':2},
          {'type':'center','text':'Own Work Declaration Form','size':13,'bold':True,'after':10},
          {'type':'fields','rows':[['Degree / Course','B.Tech. - Computer Science and Engineering with Big Data Analytics'],['Student Names',', '.join(n for n,r in AUTHORS)],['Registration Numbers',', '.join(r for n,r in AUTHORS)],['Title of Work',TITLE]]},
          {'type':'p','text':'By signing below, we confirm that this assessment is our own work, except where sources and assistance are acknowledged. We have met the following conditions:'},
          {'type':'declaration_bullets','items':['Clearly referenced and listed all sources as appropriate.','Referenced all quoted text and placed it within quotation marks.','Given the sources of pictures, data and other material that are not our own.','Not used the reports or essays of other students, either past or present, as our own work.','Acknowledged help received from others, including fellow students, technicians, statisticians and external sources.','Complied with the academic integrity criteria specified in the course handbook and University policies.']},
          {'type':'p','text':'We understand that any false claim about this work may be penalised in accordance with University policies and regulations.'},
          {'type':'declaration_table'}]
    if kind=='certificate':
        guide=PROFILE['guide_name'] or '____________________________'
        head=PROFILE['head_name'] or '____________________________'
        return [{'type':'logo','height':44,'align':'left','after':10},
         {'type':'center','text':PROFILE['institution'].upper(),'size':15.5,'bold':True,'after':5},
         {'type':'center','text':PROFILE['location'].upper(),'size':13,'bold':True,'after':32},
         {'type':'center','text':'BONAFIDE CERTIFICATE','size':16,'bold':True,'after':28},
         {'type':'p','text':'Certified that the Advanced Machine Learning project report entitled <b>“'+TITLE+'”</b> is a record of the project work submitted by <b>'+', '.join(n+' ('+r+')' for n,r in AUTHORS)+'</b>, in partial fulfilment of the requirements for the degree of Bachelor of Technology in Computer Science and Engineering with specialization in Big Data Analytics.'},
         {'type':'p','text':'The report is presented for departmental review and certification of the project work carried out under the guidance of <b>'+guide+'</b>. The faculty signatures below are to be completed by the authorised signatories after verification.'},
         {'type':'spacer','height':78},
         {'type':'faculty_signatures','guide':guide,'head':head}]
    if kind=='acknowledgements':
        guide=(' <b>'+PROFILE['guide_name']+'</b>') if PROFILE['guide_name'] else ' our project supervisor'
        head=(' <b>'+PROFILE['head_name']+'</b>') if PROFILE['head_name'] else ' the Head of the Department'
        return [{'type':'center','text':'ACKNOWLEDGEMENTS','size':15.8,'bold':True,'after':18},
         {'type':'p','text':'We express our sincere gratitude to SRM Institute of Science and Technology for the academic environment and facilities that supported this Advanced Machine Learning project. The opportunity to develop a complete application helped us connect classroom ideas with a practical data and modelling problem.'},
         {'type':'p','text':'We thank'+head+' and the faculty of the '+PROFILE['department']+' for their academic support. We also appreciate the project coordinators and review panel for encouraging clear explanations, reproducible experiments and a careful interpretation of results.'},
         {'type':'p','text':'We are grateful to'+guide+' for guidance during the project. Discussing the workflow and its limitations helped us look beyond model scores and consider the quality of the data, the meaning of the labels and the usefulness of the interface.'},
         {'type':'p','text':'We acknowledge Instacart and the dataset community for the purchase records used in the study, and the developers of the open-source Python tools used to build and evaluate FreshMatch. The report cites these sources and distinguishes recorded purchases from estimates and assumptions.'},
         {'type':'p','text':'Finally, we thank our families, friends and classmates for their encouragement and feedback. Working together on data preparation, model development, interface review and presentation strengthened both the project and our understanding of responsible machine learning.'},
         {'type':'spacer','height':24},{'type':'right','text':'\n'.join(n for n,r in AUTHORS),'size':11.7}]
    raise ValueError(kind)

# Build accurate contents and lists from this edition's real page plan.
FIGURES=[];TABLES=[];CONTENTS=[('OWN WORK DECLARATION FORM',2),('BONAFIDE CERTIFICATE',3),('ACKNOWLEDGEMENTS',4),('ABSTRACT',5)]
for i,page in enumerate(PAGES,1):
    if page['chapter']:CONTENTS.append((f"CHAPTER {page['chapter']} - {page['title']}",i))
    if page['title']=='REFERENCES':CONTENTS.append(('REFERENCES',i))
    for b in page['blocks']:
        if b['type']=='figure':FIGURES.append((b['id'],b['title'],i))
        if b['type']=='table':TABLES.append((b['id'],b['title'],i))
ABBR=[('AI','Artificial Intelligence'),('AML','Advanced Machine Learning'),('AP','Average Precision'),('AUC','Area Under the Curve'),('BDA','Big Data Analytics'),('CI','Confidence Interval'),('CSV','Comma-Separated Values'),('CV','Cross-Validation'),('DCG','Discounted Cumulative Gain'),('ECE','Expected Calibration Error'),('EDA','Exploratory Data Analysis'),('FP-Growth','Frequent Pattern Growth'),('GB','Gradient Boosting'),('IDCG','Ideal Discounted Cumulative Gain'),('LFS','Large File Storage'),('LR','Logistic Regression'),('LTR','Learning to Rank'),('MAP','Mean Average Precision'),('MLP','Multilayer Perceptron'),('NDCG','Normalized Discounted Cumulative Gain'),('PR-AUC','Precision-Recall Area Under the Curve (AP here)'),('RF','Random Forest'),('TF-IDF','Term Frequency-Inverse Document Frequency'),('XGBoost','Extreme Gradient Boosting')]

def expand(page):
    out=[]
    for b in page['blocks']:
        kind=b['type']
        if kind in ['cover','declaration','certificate','acknowledgements']:out+=front_blocks(kind)
        elif kind=='contents':out+=[{'type':'simple_table','headers':['CONTENTS','PAGE'],'rows':[[a,str(c)] for a,c in CONTENTS],'widths':[425,59]}]
        elif kind in ['figures','tables']:
            rows=FIGURES if kind=='figures' else TABLES
            out+=[{'type':'simple_table','headers':['FIGURE' if kind=='figures' else 'TABLE','DESCRIPTION','PAGE'],'rows':[[('Figure ' if kind=='figures' else 'Table ')+a,b,str(c)] for a,b,c in rows],'widths':[79,356,49]}]
        elif kind=='abbreviations':out+=[{'type':'simple_table','headers':['ABBREVIATION','MEANING'],'rows':ABBR,'widths':[113,371]}]
        else:out.append(b)
    return out

DECLARATION_TEXT = "We are aware of and understand the University's policy on academic misconduct and plagiarism. We certify that this assessment is our own work, except where indicated by referencing, and that we have followed the good academic practices noted above."
DECLARATION_NOTE = "For group work, each student should check the registration number shown above and sign beside their name."

def paragraph(text,style):return Paragraph(markup(text).replace('\n','<br/>'),style)
def make_table(headers,rows,widths,grid=True,fields=False):
    rows=([headers]+list(rows)) if headers else list(rows)
    cell_size=STYLE['cell'];head=STYLE['cellhead']
    paras=[[paragraph(v,head if (headers and j==0) or (fields and k==0) else cell_size) for k,v in enumerate(row)] for j,row in enumerate(rows)]
    t=Table(paras,colWidths=widths or [CW/len(rows[0])]*len(rows[0]),hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    if headers:commands += [('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5e5e5'))]
    if grid:commands += [('GRID',(0,0),(-1,-1),.4,colors.HexColor('#9a9a9a'))]
    t.setStyle(TableStyle(commands));return t

class PDF:
    def __init__(self):
        self.path=OUT/'FreshMatch_Project_Report.pdf';self.c=canvas.Canvas(str(self.path),pagesize=A4)
        self.c.setTitle(TITLE);self.c.setAuthor('; '.join(n for n,r in AUTHORS));self.c.setSubject('Advanced Machine Learning project report — current real-data hybrid study')
        self.positions=[];self.page=0;self.lowest={}
    def draw(self,obj,y,gap=8,x=LEFT,width=CW):
        w,h=obj.wrap(width,max(1,y-BOTTOM))
        if y-h<BOTTOM-1:raise RuntimeError(f'Page {self.page} overflow: {type(obj).__name__}, y={y:.1f}, h={h:.1f}')
        obj.drawOn(self.c,x,y-h)
        self.lowest[self.page]=min(self.lowest.get(self.page,y-h),y-h)
        return y-h-gap
    def draw_block(self,b,y):
        kind=b['type']
        if kind in ['p','h','reference','equation']:
            st=STYLE[kind];y-=st.spaceBefore
            if kind=='equation':
                para=paragraph(b['text'],st);w,hh=para.wrap(CW-16,800)
                self.c.setFillColor(colors.HexColor('#f1f4f6'));self.c.rect(LEFT,y-hh-10,CW,hh+10,fill=1,stroke=0)
                return self.draw(para,y-5,st.spaceAfter+5,x=LEFT+8,width=CW-16)
            return self.draw(paragraph(b['text'],st),y,st.spaceAfter)
        if kind in ['center','right']:
            fs=b.get('size',12);st=ParagraphStyle('special',fontName='TNR-B' if b.get('bold') else 'TNR',fontSize=fs,leading=fs*1.26,alignment=TA_CENTER if kind=='center' else TA_RIGHT)
            return self.draw(paragraph(b['text'],st),y,b.get('after',5))
        if kind=='spacer':return y-b['height']
        if kind=='logo':
            path=ASSETS/'srm-logo.png';im=Image.open(path);hh=b['height'];ww=hh*im.width/im.height
            x=LEFT if b.get('align')=='left' else (W-ww)/2
            self.c.drawImage(str(path),x,y-hh,width=ww,height=hh,mask='auto')
            return y-hh-b.get('after',8)
        if kind=='bullets':
            for item in b['items']:
                st=ParagraphStyle('bullet',parent=STYLE['p'],leftIndent=14,firstLineIndent=0,bulletIndent=0,spaceAfter=5)
                para=Paragraph(markup(item),st,bulletText='•');y=self.draw(para,y,5)
            return y+1
        if kind=='declaration_bullets':
            for item in b['items']:
                st=ParagraphStyle('declaration_bullet',parent=STYLE['p'],fontSize=11.2,leading=16,leftIndent=16,bulletIndent=2,alignment=TA_LEFT)
                y=self.draw(Paragraph(markup(item),st,bulletText='•'),y,4)
            return y-3
        if kind=='declaration_table':
            st=ParagraphStyle('declaration_cell',parent=STYLE['p'],fontSize=11.2,leading=16,alignment=TA_LEFT)
            rows=[[paragraph('<b>DECLARATION:</b>',st),'',''],[paragraph(DECLARATION_TEXT,st),'',''],[paragraph(n+'\n'+r+'\nSignature: __________________',ParagraphStyle('student_cell',parent=st,fontSize=10,leading=14)) for n,r in AUTHORS],[paragraph(DECLARATION_NOTE,st),'','']]
            t=Table(rows,colWidths=[CW/3]*3,hAlign='LEFT')
            t.setStyle(TableStyle([('SPAN',(0,0),(-1,0)),('SPAN',(0,1),(-1,1)),('SPAN',(0,3),(-1,3)),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dedcde')),('BOX',(0,0),(-1,-1),.4,colors.HexColor('#bbbbbb')),('LINEBELOW',(0,0),(-1,0),.4,colors.HexColor('#bbbbbb')),('LINEABOVE',(0,3),(-1,3),.4,colors.HexColor('#bbbbbb')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
            return self.draw(t,y,8)
        if kind=='checklist':
            for item in b['items']:
                self.c.setStrokeColor(colors.black);self.c.setLineWidth(.5);self.c.rect(LEFT+1,y-11,7,7)
                st=ParagraphStyle('check',parent=STYLE['p'],fontSize=10.9,leading=16,alignment=TA_LEFT)
                y=self.draw(paragraph(item,st),y,5,x=LEFT+17,width=CW-17)
            return y+1
        if kind in ['table','simple_table','fields']:
            if kind=='table':y=self.draw(paragraph('Table '+b['id']+': '+b['title'],STYLE['caption']),y,5)
            t=make_table(b.get('headers'),b['rows'],b.get('widths') or ([130,CW-130] if kind=='fields' else None),grid=kind!='fields',fields=kind=='fields')
            return self.draw(t,y,12)
        if kind=='figure':
            path=ROOT/b['path'];im=Image.open(path);hh=min(b['height'],CW*im.height/im.width);ww=hh*im.width/im.height
            if y-hh<BOTTOM:raise RuntimeError(f'Page {self.page} figure overflow')
            self.c.drawImage(str(path),(W-ww)/2,y-hh,width=ww,height=hh,mask='auto')
            y-=hh+8
            return self.draw(paragraph('Figure '+b['id']+': '+b['title'],STYLE['caption']),y,10)
        if kind=='code':
            fs=9;lead=12.4;lines=b['text'].splitlines();hh=len(lines)*lead+16
            if y-hh<BOTTOM:raise RuntimeError(f'Page {self.page} code overflow')
            self.c.setFillColor(colors.HexColor('#f1f4f6'));self.c.rect(LEFT,y-hh,CW,hh,fill=1,stroke=0)
            self.c.setFillColor(colors.black);self.c.setFont('Mono',fs)
            for i,line in enumerate(lines):
                if pdfmetrics.stringWidth(line,'Mono',fs)>CW-16:raise RuntimeError('Long code line '+line)
                self.c.drawString(LEFT+8,y-12-i*lead,line)
            return y-hh-10
        if kind=='student_signatures':
            y-=16;col=CW/3
            for i,(name,reg) in enumerate(AUTHORS):
                x=LEFT+i*col;self.c.setStrokeColor(colors.black);self.c.setLineWidth(.5);self.c.line(x,y-20,x+col-14,y-20)
                st=ParagraphStyle('sig',fontName='TNR',fontSize=9.5,leading=12)
                para=paragraph(name+'\n'+reg+'',st);para.wrap(col-12,100);para.drawOn(self.c,x,y-72)
            return y-85
        if kind=='faculty_signatures':
            col=CW/2
            for i,(name,role) in enumerate([(b['guide'],'PROJECT GUIDE'),(b['head'],'PROFESSOR & HEAD')]):
                x=LEFT+i*col
                st=ParagraphStyle('faculty',fontName='TNR-B',fontSize=11,leading=15)
                para=paragraph('SIGNATURE\n\n'+name+'\n\n'+role,st);ww,hh=para.wrap(col-22,180);para.drawOn(self.c,x,y-hh)
                st2=ParagraphStyle('dept',fontName='TNR',fontSize=9.5,leading=12)
                para=paragraph(PROFILE['department'],st2);ww,hh2=para.wrap(col-22,90);para.drawOn(self.c,x,y-hh-hh2-8)
            return y-170
        raise ValueError(kind)
    def build(self):
        for i,page in enumerate(PAGES,1):
            self.page=i;self.c.setStrokeColor(colors.HexColor('#777777'));self.c.setLineWidth(.6)
            self.c.rect(18,52,W-36,H-104,fill=0,stroke=1)
            if i!=1:
                self.c.setFillColor(colors.black);self.c.setFont('TNR',11.5);self.c.drawCentredString(W/2,64,str(i))
            y=TOP
            if page['chapter']:
                anchor='chapter'+str(page['chapter']);self.c.bookmarkPage(anchor);self.c.addOutlineEntry('Chapter '+str(page['chapter'])+' — '+page['title'],anchor,0)
                y=self.draw(paragraph('CHAPTER '+str(page['chapter'])+'\n'+page['title'],STYLE['title']),y,14)
            elif page['title'] and i>=5:
                st=ParagraphStyle('fronttitle',parent=STYLE['title'],alignment=TA_CENTER if page['title']=='ABSTRACT' else TA_LEFT)
                y=self.draw(paragraph(page['title'],st),y,15)
            for b in expand(page):y=self.draw_block(b,y)
            if y<78:raise RuntimeError(f'Page {i} ends below safe area ({y})')
            self.positions.append({'page':i,'title':page['title'],'end_y':round(y,1),'remaining_body_pt':round(y-BOTTOM,1)})
            self.c.showPage()
        self.c.save()
        (OUT/'layout_audit.json').write_text(json.dumps(self.positions,indent=2)+'\n')
        print('PDF:',self.path,'pages',len(PAGES),'minimum end-y',min(p['end_y'] for p in self.positions))

# Editable Word document from the same content and page plan.
class RichParser(HTMLParser):
    def __init__(self,paragraph):super().__init__(convert_charrefs=True);self.p=paragraph;self.tags=[]
    def handle_starttag(self,tag,attrs):
        if tag=='br':self.p.add_run().add_break()
        else:self.tags.append(tag)
    def handle_endtag(self,tag):
        if tag in self.tags:self.tags.remove(tag)
    def handle_data(self,data):
        run=self.p.add_run(data);run.bold='b' in self.tags;run.italic='i' in self.tags
        run.font.subscript='sub' in self.tags;run.font.superscript='sup' in self.tags

def shade(cell,color):
    tcPr=cell._tc.get_or_add_tcPr();el=OxmlElement('w:shd');el.set(qn('w:fill'),color);tcPr.append(el)

def set_cell_margins(cell,top=70,start=90,bottom=70,end=90):
    pr=cell._tc.get_or_add_tcPr();m=OxmlElement('w:tcMar')
    for k,v in [('top',top),('start',start),('bottom',bottom),('end',end)]:
        el=OxmlElement('w:'+k);el.set(qn('w:w'),str(v));el.set(qn('w:type'),'dxa');m.append(el)
    pr.append(m)

class Word:
    def __init__(self):
        self.doc=Document();sec=self.doc.sections[0]
        sec.page_width=Pt(W);sec.page_height=Pt(H)
        sec.left_margin=Pt(LEFT);sec.right_margin=Pt(RIGHT);sec.top_margin=Pt(86);sec.bottom_margin=Pt(92)
        sec.header_distance=Pt(36);sec.footer_distance=Pt(53);sec.different_first_page_header_footer=True
        pr=sec._sectPr;b=OxmlElement('w:pgBorders');b.set(qn('w:offsetFrom'),'page')
        for edge in ['top','left','bottom','right']:
            el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:space'),'18');el.set(qn('w:color'),'777777');b.append(el)
        pr.append(b)
        normal=self.doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(11.7)
        normal.paragraph_format.line_spacing=Pt(19.2);normal.paragraph_format.space_after=Pt(8)
        for name,fs,lead in [('Heading 1',15.8,20),('Heading 2',13.2,17.4)]:
            st=self.doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(fs);st.font.bold=True;st.font.color.rgb=RGBColor(0,0,0)
            st.paragraph_format.line_spacing=Pt(lead);st.paragraph_format.space_before=Pt(0 if name=='Heading 1' else 6);st.paragraph_format.space_after=Pt(14 if name=='Heading 1' else 7)
        footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
        fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)
        self.doc.core_properties.title=TITLE;self.doc.core_properties.author='; '.join(n for n,r in AUTHORS)
        self.doc.core_properties.subject='Advanced Machine Learning project report'
    def para(self,text='',style=None,align=None,fs=None,bold=False,after=None,leading=None):
        p=self.doc.add_paragraph(style=style)
        if getattr(self,'start_new_page',False):
            p.paragraph_format.page_break_before=True
            self.start_new_page=False
        RichParser(p).feed(str(text))
        p.alignment=align if align is not None else WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.widow_control=True
        if after is not None:p.paragraph_format.space_after=Pt(after)
        if leading is not None:p.paragraph_format.line_spacing=Pt(leading)
        if fs is not None:
            for run in p.runs:run.font.size=Pt(fs);run.bold=bold
        return p
    def table(self,headers,rows,widths,grid=True,fields=False):
        data=([headers]+list(rows)) if headers else list(rows);widths=widths or [CW/len(data[0])]*len(data[0])
        t=self.doc.add_table(rows=0,cols=len(data[0]));t.autofit=False
        if grid:t.style='Table Grid'
        for col,width in zip(t.columns,widths):col.width=Pt(width)
        for j,row in enumerate(data):
            cells=t.add_row().cells
            cant=OxmlElement('w:cantSplit');t.rows[-1]._tr.get_or_add_trPr().append(cant)
            if j==0 and headers:
                t.rows[-1]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
            for k,value in enumerate(row):
                cell=cells[k];cell.width=Pt(widths[k]);set_cell_margins(cell)
                p=cell.paragraphs[0];p.paragraph_format.line_spacing=Pt(12.8);p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0)
                RichParser(p).feed(str(value))
                for run in p.runs:run.font.name='Times New Roman';run.font.size=Pt(10.1);run.bold=(j==0 and bool(headers)) or (fields and k==0)
                if j==0 and headers:shade(cell,'E5E5E5')
        self.para('',fs=1,after=4,leading=1)
    def block(self,b):
        kind=b['type']
        if kind=='p':self.para(b['text'])
        elif kind=='h':self.para(b['text'],'Heading 2',WD_ALIGN_PARAGRAPH.LEFT)
        elif kind=='reference':self.para(b['text'],align=WD_ALIGN_PARAGRAPH.LEFT,fs=10.7,after=8,leading=15.3)
        elif kind in ['center','right']:
            fs=b.get('size',12);self.para(b['text'],align=WD_ALIGN_PARAGRAPH.CENTER if kind=='center' else WD_ALIGN_PARAGRAPH.RIGHT,fs=fs,bold=b.get('bold',False),after=b.get('after',5),leading=fs*1.26)
        elif kind=='spacer':self.para('',fs=1,after=0,leading=b['height'])
        elif kind=='logo':
            p=self.para('',align=WD_ALIGN_PARAGRAPH.LEFT if b.get('align')=='left' else WD_ALIGN_PARAGRAPH.CENTER,after=b.get('after',8),leading=1)
            p.paragraph_format.line_spacing=1.0
            p.add_run().add_picture(str(ASSETS/'srm-logo.png'),height=Pt(b['height']))
        elif kind=='declaration_bullets':
            for item in b['items']:
                p=self.para('•  '+item,align=WD_ALIGN_PARAGRAPH.LEFT,fs=11.2,after=4,leading=16)
                p.paragraph_format.left_indent=Pt(16);p.paragraph_format.first_line_indent=Pt(-14)
        elif kind=='declaration_table':
            t=self.doc.add_table(rows=4,cols=3);t.autofit=False
            for col in t.columns:col.width=Pt(CW/3)
            for i in [0,1,3]:t.cell(i,0).merge(t.cell(i,2))
            values=[['DECLARATION:'],[DECLARATION_TEXT],[n+'\n'+r+'\nSignature: __________________' for n,r in AUTHORS],[DECLARATION_NOTE]]
            for i,row in enumerate(values):
                for j,value in enumerate(row):
                    cell=t.cell(i,j);set_cell_margins(cell);p=cell.paragraphs[0];p.paragraph_format.line_spacing=Pt(14 if i==2 else 16);p.paragraph_format.space_after=Pt(5)
                    run=p.add_run(value);run.font.name='Times New Roman';run.font.size=Pt(10 if i==2 else 11.2);run.bold=(i==0)
                    if i==0:shade(cell,'DEDCDE')
            pr=t._tbl.tblPr;borders=OxmlElement('w:tblBorders')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'BBBBBB');borders.append(el)
            pr.append(borders)
        elif kind in ['bullets','checklist']:
            for item in b['items']:
                p=self.para(('☐  ' if kind=='checklist' else '•  ')+item,align=WD_ALIGN_PARAGRAPH.LEFT,fs=10.9 if kind=='checklist' else 11.7,after=5,leading=16 if kind=='checklist' else 19.2)
                p.paragraph_format.left_indent=Pt(14);p.paragraph_format.first_line_indent=Pt(-14)
        elif kind in ['table','simple_table','fields']:
            if kind=='table':self.para('Table '+b['id']+': '+b['title'],align=WD_ALIGN_PARAGRAPH.LEFT,fs=10.5,after=5,leading=14).runs[0].italic=True
            self.table(b.get('headers'),b['rows'],b.get('widths') or ([130,CW-130] if kind=='fields' else None),grid=kind!='fields',fields=kind=='fields')
        elif kind=='equation':
            p=self.para(b['text'],align=WD_ALIGN_PARAGRAPH.CENTER,fs=11.4,leading=17,after=9)
            pr=p._p.get_or_add_pPr();el=OxmlElement('w:shd');el.set(qn('w:fill'),'F1F4F6');pr.append(el)
        elif kind=='figure':
            path=ROOT/b['path'];im=Image.open(path);hh=min(b['height'],CW*im.height/im.width)
            p=self.para('',align=WD_ALIGN_PARAGRAPH.CENTER,after=8,leading=1);p.paragraph_format.line_spacing=1.0;p.add_run().add_picture(str(path),height=Pt(hh))
            p=self.para('Figure '+b['id']+': '+b['title'],align=WD_ALIGN_PARAGRAPH.LEFT,fs=10.5,after=10,leading=14)
            for run in p.runs:run.italic=True
        elif kind=='code':
            p=self.para(b['text'],align=WD_ALIGN_PARAGRAPH.LEFT,fs=9,after=10,leading=12.4)
            for run in p.runs:run.font.name='Courier New'
            pr=p._p.get_or_add_pPr();sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F1F4F6');pr.append(sh)
        elif kind=='student_signatures':
            self.para('',fs=1,after=12,leading=1)
            self.table(None,[[f'_____________________\n{n}\n{r}' for n,r in AUTHORS]],[CW/3]*3,grid=False)
        elif kind=='faculty_signatures':
            self.table(None,[[f"SIGNATURE\n\n{b['guide']}\n\nPROJECT GUIDE\n{PROFILE['department']}",f"SIGNATURE\n\n{b['head']}\n\nPROFESSOR & HEAD\n{PROFILE['department']}"]],[CW/2]*2,grid=False)
        else:raise ValueError(kind)
    def build(self):
        for i,page in enumerate(PAGES,1):
            self.start_new_page=(i>1)
            if page['chapter']:self.para('CHAPTER '+str(page['chapter'])+'\n'+page['title'],'Heading 1',WD_ALIGN_PARAGRAPH.LEFT)
            elif page['title'] and i>=5:self.para(page['title'],'Heading 1',WD_ALIGN_PARAGRAPH.CENTER if page['title']=='ABSTRACT' else WD_ALIGN_PARAGRAPH.LEFT)
            for b in expand(page):self.block(b)
        path=OUT/'FreshMatch_Project_Report.docx';self.doc.save(path);print('DOCX:',path)

if __name__=='__main__':
    generate_figures();PDF().build();Word().build()
    (OUT/'report_structure.json').write_text(json.dumps({'pages':len(PAGES),'contents':CONTENTS,'figures':FIGURES,'tables':TABLES,'authors':AUTHORS,'faculty_names_confirmed':bool(PROFILE['guide_name'] and PROFILE['head_name'])},indent=2)+'\n')
