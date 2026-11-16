"""Generate a flow chart with separate inner and outer loop routes."""
from pathlib import Path
from xml.etree import ElementTree as E
import math
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).parent
N={
's':('Начало','ellipse',360,20,200,55),
'input':('Ввод строк, остатков и резервов\nДефицит = []','parallelogram',260,110,400,65),
'lines':('Есть ещё строки?','rhombus',320,220,280,90),
'line':('Взять следующую строку','rectangle',280,350,360,55),
'zero':('Резерв = 0\nНачать просмотр резервов','rectangle',280,450,360,55),
'more':('Есть ещё резервы?','rhombus',320,550,280,90),
'next':('Взять следующий резерв','rectangle',280,690,360,55),
'match':('Тот же товар\nи активен?','rhombus',320,790,280,100),
'add':('Резерв += количество\nтекущего резерва','rectangle',710,800,310,75),
'avail':('Доступно = остаток − резерв','rectangle',280,1020,360,65),
'short':('Запрошено > доступно?','rhombus',320,1140,280,100),
'append':('Добавить товар и\nнедостающее количество','rectangle',710,1150,310,75),
'output':('Вывод списка дефицита','parallelogram',710,230,310,65),
'end':('Конец','ellipse',760,350,200,55),
}
A=[('s','input','',[(460,75),(460,110)]),('input','lines','',[(460,175),(460,220)]),('lines','line','да',[(460,310),(460,350)]),('lines','output','нет',[(600,265),(710,265)]),('output','end','',[(865,295),(865,350)]),('line','zero','',[(460,405),(460,450)]),('zero','more','',[(460,505),(460,550)]),('more','next','да',[(460,640),(460,690)]),('next','match','',[(460,745),(460,790)]),('match','add','да',[(600,840),(710,840)]),('match','more','нет',[(460,890),(460,950),(180,950),(180,595),(320,595)]),('add','more','',[(865,875),(865,975),(150,975),(150,595),(320,595)]),('more','avail','нет',[(600,595),(675,595),(675,1000),(460,1000),(460,1020)]),('avail','short','',[(460,1085),(460,1140)]),('short','append','да',[(600,1190),(710,1190)]),('short','lines','нет',[(460,1240),(460,1340),(65,1340),(65,265),(320,265)]),('append','lines','',[(865,1225),(865,1390),(35,1390),(35,265),(320,265)])]
def generate():
 root=E.Element('mxfile',host='app.diagrams.net'); diag=E.SubElement(root,'diagram',name='Проверка доступности'); model=E.SubElement(diag,'mxGraphModel',page='1',pageWidth='1060',pageHeight='1440'); g=E.SubElement(model,'root');E.SubElement(g,'mxCell',id='0');E.SubElement(g,'mxCell',id='1',parent='0')
 im=Image.new('RGB',(2120,2880),'white'); d=ImageDraw.Draw(im); f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',34)
 for key,(label,shape,x,y,w,h) in N.items():
  cell=E.SubElement(g,'mxCell',id=key,value=label.replace('\n','<br>'),style=f'shape={shape};whiteSpace=wrap;html=1;fontSize=17;fillColor=#ffffff;strokeColor=#233e52;',vertex='1',parent='1');E.SubElement(cell,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
  box=(x*2,y*2,(x+w)*2,(y+h)*2)
  if shape=='rhombus': d.polygon([(2*x+w,2*y),(2*(x+w),2*y+h),(2*x+w,2*(y+h)),(2*x,2*y+h)],outline='#233e52',fill='#fff6df',width=3)
  elif shape=='ellipse':d.ellipse(box,outline='#233e52',width=3)
  elif shape=='parallelogram':d.polygon([(2*x+25,2*y),(2*(x+w),2*y),(2*(x+w)-25,2*(y+h)),(2*x,2*(y+h))],outline='#233e52',width=3)
  else:d.rectangle(box,outline='#233e52',width=3)
  d.multiline_text((2*x+w,2*y+h),label,font=f,anchor='mm',align='center',fill='#233e52')
 for i,(a,b,label,points) in enumerate(A):
  c=E.SubElement(g,'mxCell',id=f'edge{i}',value=label,edge='1',parent='1',source=a,target=b,style='endArrow=block;html=1;rounded=0;fontSize=17;');geo=E.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=E.SubElement(geo,'Array',attrib={'as':'points'})
  for x,y in points[1:-1]:E.SubElement(arr,'mxPoint',x=str(x),y=str(y))
  pp=[(x*2,y*2) for x,y in points];d.line(pp,fill='#233e52',width=3);x,y=pp[-1];px,py=pp[-2];ang=math.atan2(y-py,x-px);d.polygon([(x,y),(x-15*math.cos(ang-.4),y-15*math.sin(ang-.4)),(x-15*math.cos(ang+.4),y-15*math.sin(ang+.4))],fill='#233e52')
  if label:x,y=pp[0];d.text((x+10,y+8),label,font=f,fill='#833e15')
 E.ElementTree(root).write(OUT/'algo_1.drawio',encoding='utf-8',xml_declaration=True);im.save(OUT/'algo_1.png')
if __name__=='__main__':generate()
