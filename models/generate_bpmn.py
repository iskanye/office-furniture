"""Generate BPMN XML and PNG using identical geometry."""
from pathlib import Path
from xml.etree import ElementTree as E
import math
from PIL import Image, ImageDraw, ImageFont
OUT=Path(__file__).parent
B='http://www.omg.org/spec/BPMN/20100524/MODEL'; D='http://www.omg.org/spec/BPMN/20100524/DI'; C='http://www.omg.org/spec/DD/20100524/DC'; I='http://www.omg.org/spec/DD/20100524/DI'
N={
 'start':('Заявка получена','startEvent','manager',150,250,36,36),
 'register':('Зарегистрировать\nзаявку','task','manager',230,230,160,70),
 'validate':('Проверить\nкорректность заявки','task','manager',440,230,185,70),
 'valid':('Заявка корректна?','exclusiveGateway','manager',680,241,54,54),
 'endbad':('Ошибка заявки','endEvent','manager',850,250,36,36),
 'notify':('Сообщить\nо дефиците','task','manager',1020,230,170,70),
 'endshort':('Отказ по дефициту','endEvent','manager',1290,250,36,36),
 'availability':('Проверить\nдоступность товаров','task','system',440,560,185,70),
 'available':('Товары доступны?','exclusiveGateway','system',680,568,54,54),
 'price':('Рассчитать\nстоимость заказа','task','system',850,560,170,70),
 'send':('Отправить\nусловия заказа','sendTask','manager',850,370,170,70),
 'confirm':('Подтвердить\nусловия заказа','receiveTask','manager',1100,370,170,70),
 'confirmed':('Условия приняты?','exclusiveGateway','manager',1330,378,54,54),
 'endcancel':('Отказ покупателя','endEvent','manager',1480,387,36,36),
 'reserve':('Зарезервировать\nвсе позиции','task','system',1100,560,190,70),
 'receive':('Принять заказ\nк комплектации','task','warehouse',1100,790,190,70),
 'endok':('Заказ с резервом','endEvent','warehouse',1430,807,36,36),
}
F=[('start','register','',[(186,268),(230,268)]),('register','validate','',[(390,265),(440,265)]),('validate','valid','',[(625,265),(680,268)]),('valid','endbad','нет',[(734,268),(850,268)]),('valid','availability','да',[(707,295),(707,330),(532,330),(532,560)]),('availability','available','',[(625,595),(680,595)]),('available','notify','нет',[(707,568),(707,515),(800,515),(800,335),(1105,335),(1105,300)]),('notify','endshort','',[(1190,265),(1290,268)]),('available','price','да',[(734,595),(850,595)]),('price','send','',[(935,560),(935,440)]),('send','confirm','',[(1020,405),(1100,405)]),('confirm','confirmed','',[(1270,405),(1330,405)]),('confirmed','endcancel','нет',[(1384,405),(1480,405)]),('confirmed','reserve','да',[(1357,432),(1357,535),(1195,535),(1195,560)]),('reserve','receive','',[(1195,630),(1195,790)]),('receive','endok','',[(1290,825),(1430,825)])]
M=[('Buyer','start','Заявка',[(168,120),(168,250)]),('send','Buyer','Условия',[(935,370),(935,120)]),('Buyer','confirm','Решение',[(1185,120),(1185,370)])]

def generate():
 for p,u in [('bpmn',B),('bpmndi',D),('dc',C),('di',I)]: E.register_namespace(p,u)
 root=E.Element(f'{{{B}}}definitions',id='Definitions_1',targetNamespace='https://example.org/furniture')
 coll=E.SubElement(root,f'{{{B}}}collaboration',id='Collaboration_1')
 E.SubElement(coll,f'{{{B}}}participant',id='Supplier',name='Поставщик офисной мебели',processRef='Process_1')
 E.SubElement(coll,f'{{{B}}}participant',id='Buyer',name='Покупатель')
 proc=E.SubElement(root,f'{{{B}}}process',id='Process_1',isExecutable='false')
 lanes=E.SubElement(proc,f'{{{B}}}laneSet',id='LaneSet_1')
 for lid,title in [('manager','Менеджер'),('system','Система'),('warehouse','Склад')]:
  lane=E.SubElement(lanes,f'{{{B}}}lane',id=f'Lane_{lid}',name=title)
  for key,n in N.items():
   if n[2]==lid: E.SubElement(lane,f'{{{B}}}flowNodeRef').text=key
 for key,(name,kind,*_) in N.items():
  attrs={'id':key,'name':name.replace('\n',' ')}
  if kind=='exclusiveGateway': attrs['gatewayDirection']='Diverging'
  node=E.SubElement(proc,f'{{{B}}}{kind}',**attrs)
  if key=='start': E.SubElement(node,f'{{{B}}}messageEventDefinition',id='MessageStart')
  if key in ('valid','available','confirmed'): node.set('default',next(f'Flow_{i}' for i,f in enumerate(F) if f[0]==key and f[2]=='нет'))
  for i,(a,b,*_) in enumerate(F):
   if key==b: E.SubElement(node,f'{{{B}}}incoming').text=f'Flow_{i}'
   if key==a: E.SubElement(node,f'{{{B}}}outgoing').text=f'Flow_{i}'
 for i,(a,b,label,_) in enumerate(F):
  flow=E.SubElement(proc,f'{{{B}}}sequenceFlow',id=f'Flow_{i}',sourceRef=a,targetRef=b,**({'name':label} if label else {}))
  if label=='да': E.SubElement(flow,f'{{{B}}}conditionExpression',{'{http://www.w3.org/2001/XMLSchema-instance}type':'bpmn:tFormalExpression'}).text={'valid':'request_valid','available':'all_available','confirmed':'customer_confirmed'}[a]
 for i,(a,b,label,_) in enumerate(M): E.SubElement(coll,f'{{{B}}}messageFlow',id=f'Message_{i}',sourceRef=a,targetRef=b,name=label)
 plane=E.SubElement(E.SubElement(root,f'{{{D}}}BPMNDiagram',id='Diagram_1'),f'{{{D}}}BPMNPlane',id='Plane_1',bpmnElement='Collaboration_1')
 def shape(key,x,y,w,h,**attrs):
  s=E.SubElement(plane,f'{{{D}}}BPMNShape',id=key+'_di',bpmnElement=key,**attrs)
  E.SubElement(s,f'{{{C}}}Bounds',x=str(x),y=str(y),width=str(w),height=str(h))
 shape('Buyer',20,20,1560,100,isHorizontal='true'); shape('Supplier',20,180,1560,730,isHorizontal='true')
 for lid,y,h in [('manager',180,310),('system',490,240),('warehouse',730,180)]: shape('Lane_'+lid,50,y,1530,h,isHorizontal='true')
 for key,n in N.items(): shape(key,*n[3:])
 for prefix,flows in [('Flow',F),('Message',M)]:
  for i,(source,target,label,points) in enumerate(flows):
   e=E.SubElement(plane,f'{{{D}}}BPMNEdge',id=f'{prefix}_{i}_di',bpmnElement=f'{prefix}_{i}')
   for x,y in points: E.SubElement(e,f'{{{I}}}waypoint',x=str(x),y=str(y))
   if label:
    x,y={('valid','нет'):(760,238),('valid','да'):(590,315),('available','нет'):(735,485),('available','да'):(760,565),('confirmed','нет'):(1400,375),('confirmed','да'):(1360,470)}.get((source,label),points[0]); lab=E.SubElement(e,f'{{{D}}}BPMNLabel'); E.SubElement(lab,f'{{{C}}}Bounds',x=str(x+9),y=str(y+8),width='100',height='20')
 E.ElementTree(root).write(OUT/'bpmn.bpmn',encoding='utf-8',xml_declaration=True)
 render()

def render():
 s=2; im=Image.new('RGB',(3200,1880),'white'); d=ImageDraw.Draw(im)
 def rect(box,**kw): d.rectangle(tuple(int(v*s) for v in box),**kw)
 def text(t,x,y,size=17):
  ft=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',size*s)
  d.multiline_text((x*s,y*s),t,font=ft,fill='#182c3e',anchor='mm',align='center',spacing=4)
 rect((20,20,1580,120),outline='#435c70',width=3);text('Покупатель',760,70,22)
 rect((20,180,1580,910),outline='#435c70',width=4)
 for title,y,h in [('Менеджер',180,310),('Система',490,240),('Склад',730,180)]:
  rect((50,y,1580,y+h),outline='#bac6d0',width=2); text(title,110,y+h/2,18)
 for key,(label,kind,_,x,y,w,h) in N.items():
  box=(x*s,y*s,(x+w)*s,(y+h)*s)
  if kind in ('startEvent','endEvent'):
   d.ellipse(box,fill='white',outline='#263f53',width=(7 if kind=='endEvent' else 3));text(label,x+w/2,y+h+22,14)
   if key=='start': rect((x+8,y+11,x+w-8,y+h-11),outline='#263f53',width=2)
  elif kind=='exclusiveGateway':
   d.polygon([(int(a*s),int(b*s)) for a,b in [(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]],fill='#fff6df',outline='#263f53',width=3)
   text('×',x+w/2,y+h/2,30);text(label,x+w/2,y-20,14)
  else:
   d.rounded_rectangle(box,radius=15,fill='#eef5fa',outline='#263f53',width=3);text(label,x+w/2,y+h/2,17)
 for dashed,flows in [(False,F),(True,M)]:
  for a,b,label,points in flows:
   pp=[(x*s,y*s) for x,y in points]
   for p,q in zip(pp,pp[1:]):
    if not dashed: d.line([p,q],fill='#263f53',width=3)
    else:
     length=math.dist(p,q)
     for t in range(0,int(length),16):
      d.line([(p[0]+(q[0]-p[0])*t/length,p[1]+(q[1]-p[1])*t/length),(p[0]+(q[0]-p[0])*min(t+8,length)/length,p[1]+(q[1]-p[1])*min(t+8,length)/length)],fill='#263f53',width=3)
   x,y=pp[-1]; px,py=pp[-2]; angle=math.atan2(y-py,x-px)
   wings=[(x-18*math.cos(angle-.45),y-18*math.sin(angle-.45)),(x-18*math.cos(angle+.45),y-18*math.sin(angle+.45))]
   if dashed: d.line([wings[0],(x,y),wings[1]],fill='#263f53',width=3);px,py=pp[0];d.ellipse((px-5,py-5,px+5,py+5),fill='white',outline='#263f53',width=2)
   else: d.polygon([(x,y),*wings],fill='#263f53')
   if label: x,y=points[0];text(label,x+40,y+21,14)
 im.save(OUT/'bpmn.png')
if __name__=='__main__': generate()
