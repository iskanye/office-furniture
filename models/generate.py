"""Generate editable BPMN/draw.io sources and matching PNG previews from code."""

from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def font(size):
    return ImageFont.truetype(FONT, size)


def picture(name, width, height, boxes, arrows, lanes=()):
    im = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(im)
    for label, y, h in lanes:
        d.rectangle((15, y, width - 15, y + h), outline="#8b98a6", width=2)
        d.rectangle((15, y, 110, y + h), fill="#e9eef3", outline="#8b98a6", width=2)
        d.text((31, y + 18), label, font=font(22), fill="#263746")
    for key, (label, kind, x, y, w, h) in boxes.items():
        fill = "#e8f4fa" if kind == "task" else "#fff8e8" if kind == "decision" else "#f3f7fa"
        if kind == "decision":
            d.polygon([(x + w//2,y),(x+w,y+h//2),(x+w//2,y+h),(x,y+h//2)], fill=fill, outline="#31485a", width=3)
        elif kind in ("start", "end"):
            d.ellipse((x,y,x+w,y+h), fill=fill, outline="#31485a", width=4 if kind == "end" else 2)
        elif kind == "data":
            d.polygon([(x+18,y),(x+w,y),(x+w-18,y+h),(x,y+h)], fill=fill, outline="#31485a", width=2)
        elif kind == "loop":
            d.polygon([(x+22,y),(x+w-22,y),(x+w,y+h/2),(x+w-22,y+h),(x+22,y+h),(x,y+h/2)],fill=fill,outline="#31485a",width=2)
        else:
            d.rounded_rectangle((x,y,x+w,y+h), radius=13 if kind == "task" else 0, fill=fill, outline="#31485a", width=2)
        lines = label.split("\n")
        fs = font(21 if width > 1100 else 20)
        line_h = 26
        for i,line in enumerate(lines):
            bb = d.textbbox((0,0),line,font=fs)
            d.text((x+(w-(bb[2]-bb[0]))/2, y+(h-line_h*len(lines))/2+i*line_h),line,font=fs,fill="#172b3a")
    for a,b,label in arrows:
        x1,y1=anchor(boxes[a],boxes[b]); x2,y2=anchor(boxes[b],boxes[a])
        if y2 < y1 - 100 and name.startswith("algo"):
            side = 95 if name == "algo_1" else width - 95
            x1 = boxes[a][2] if side < width/2 else boxes[a][2]+boxes[a][4]
            y1 = boxes[a][3]+boxes[a][5]/2
            x2 = boxes[b][2] if side < width/2 else boxes[b][2]+boxes[b][4]
            y2 = boxes[b][3]+boxes[b][5]/2
            d.line([(x1,y1),(side,y1),(side,y2),(x2,y2)],fill="#425b70",width=3)
            ang=0 if side < width/2 else 3.14159
        else:
            d.line((x1,y1,x2,y2),fill="#425b70",width=3)
            import math
            ang=math.atan2(y2-y1,x2-x1)
        import math
        p=[(x2,y2),(x2-13*math.cos(ang-.5),y2-13*math.sin(ang-.5)),(x2-13*math.cos(ang+.5),y2-13*math.sin(ang+.5))]
        d.polygon(p,fill="#425b70")
        if label:
            lx, ly = branch_label_position(name, boxes, a, b, (x1, y1), (x2, y2))
            d.text((lx, ly), label, font=font(18), fill="#9b4d24")
    im.save(OUT/(name+".png"))


def anchor(a,b):
    _,_,x,y,w,h=a; _,_,bx,by,bw,bh=b
    dx=(bx+bw/2)-(x+w/2); dy=(by+bh/2)-(y+h/2)
    if abs(dx)>abs(dy): return (x+w if dx>0 else x,y+h/2)
    return (x+w/2,y+h if dy>0 else y)


def branch_label_position(name, boxes, source, target, start, end):
    """Place each answer beside the segment leaving its decision diamond."""
    x1, y1 = start
    x2, y2 = end
    if name.startswith("algo") and boxes[target][3] < boxes[source][3] - 100:
        return (x1 - 34, y1 - 29) if name == "algo_1" else (x1 + 14, y1 - 29)
    if name.startswith("algo") and boxes[source][1] == "decision":
        return (x1 + 15, y1 - 29) if x2 > x1 + 30 else (x1 + 10, y1 + 6)
    return ((x1 + x2) / 2 + 5, (y1 + y2) / 2 - 24)


def drawio(name,boxes,arrows,width,height):
    root=ET.Element("mxfile",host="app.diagrams.net",modified="2026-11-01T00:00:00.000Z")
    diagram=ET.SubElement(root,"diagram",name=name,id="page-1")
    model=ET.SubElement(diagram,"mxGraphModel",dx=str(width),dy=str(height),grid="1",gridSize="10",page="1",pageWidth=str(width),pageHeight=str(height))
    graph=ET.SubElement(model,"root")
    ET.SubElement(graph,"mxCell",id="0")
    ET.SubElement(graph,"mxCell",id="1",parent="0")
    styles={"start":"ellipse;whiteSpace=wrap;html=1;fillColor=#f3f7fa;","end":"ellipse;whiteSpace=wrap;html=1;strokeWidth=3;fillColor=#f3f7fa;","task":"rounded=1;whiteSpace=wrap;html=1;fillColor=#e8f4fa;","decision":"rhombus;whiteSpace=wrap;html=1;fillColor=#fff8e8;","data":"shape=parallelogram;whiteSpace=wrap;html=1;fillColor=#f3f7fa;","process":"rounded=0;whiteSpace=wrap;html=1;fillColor=#f3f7fa;","loop":"shape=hexagon;whiteSpace=wrap;html=1;fillColor=#f3f7fa;"}
    for key,(label,kind,x,y,w,h) in boxes.items():
        cell=ET.SubElement(graph,"mxCell",id=key,value=label.replace("\n","<br>"),style=styles[kind]+"fontSize=16;",vertex="1",parent="1")
        ET.SubElement(cell,"mxGeometry",x=str(x),y=str(y),width=str(w),height=str(h),attrib={"as":"geometry"})
    for i,(a,b,label) in enumerate(arrows):
        cell=ET.SubElement(graph,"mxCell",id=f"edge{i}",value="" if name.startswith("algo") else label,style="endArrow=block;html=1;rounded=0;",edge="1",parent="1",source=a,target=b)
        geom=ET.SubElement(cell,"mxGeometry",relative="1",attrib={"as":"geometry"})
        if name.startswith("algo") and boxes[b][3] < boxes[a][3] - 100:
            side=95 if name=="algo_1" else width-95
            points=ET.SubElement(geom,"Array",attrib={"as":"points"})
            for y in (boxes[a][3]+boxes[a][5]//2,boxes[b][3]+boxes[b][5]//2):
                ET.SubElement(points,"mxPoint",x=str(side),y=str(y))
        if label and name.startswith("algo"):
            start = anchor(boxes[a], boxes[b])
            end = anchor(boxes[b], boxes[a])
            if boxes[b][3] < boxes[a][3] - 100:
                side = 95 if name == "algo_1" else width - 95
                start = (boxes[a][2] if side < width / 2 else boxes[a][2] + boxes[a][4],
                         boxes[a][3] + boxes[a][5] / 2)
                end = (boxes[b][2] if side < width / 2 else boxes[b][2] + boxes[b][4],
                       boxes[b][3] + boxes[b][5] / 2)
            lx, ly = branch_label_position(name, boxes, a, b, start, end)
            label_cell = ET.SubElement(graph,"mxCell",id=f"edge{i}_label",value=label,
                                       style="text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;"
                                             "fillColor=none;strokeColor=none;fontSize=16;fontColor=#9b4d24;",
                                       vertex="1",parent="1")
            ET.SubElement(label_cell,"mxGeometry",x=str(round(lx)),y=str(round(ly)),
                          width="45",height="24",attrib={"as":"geometry"})
    ET.ElementTree(root).write(OUT/(name+".drawio"),encoding="utf-8",xml_declaration=True)


def bpmn(boxes,arrows):
    B="http://www.omg.org/spec/BPMN/20100524/MODEL"
    D="http://www.omg.org/spec/BPMN/20100524/DI"
    C="http://www.omg.org/spec/DD/20100524/DC"
    I="http://www.omg.org/spec/DD/20100524/DI"
    ET.register_namespace("bpmn",B); ET.register_namespace("bpmndi",D);ET.register_namespace("dc",C);ET.register_namespace("di",I)
    root=ET.Element(f"{{{B}}}definitions",id="Definitions_1",targetNamespace="https://example.org/office-furniture")
    collaboration=ET.SubElement(root,f"{{{B}}}collaboration",id="Collaboration_1")
    ET.SubElement(collaboration,f"{{{B}}}participant",id="Participant_1",name="Поставщик офисной мебели",processRef="Process_1")
    process=ET.SubElement(root,f"{{{B}}}process",id="Process_1",name="Обработка заявки и резервирование мебели",isExecutable="false")
    lane_set=ET.SubElement(process,f"{{{B}}}laneSet",id="LaneSet_1")
    groups={"manager":["start","register","validate","notify","endbad","endshort"],"system":["availability","gateway","price","reserve"],"customer":["confirm","endcancel"],"warehouse":["receive","endok"]}
    for lane_id,ids in groups.items():
        lane=ET.SubElement(lane_set,f"{{{B}}}lane",id=f"Lane_{lane_id}",name={"manager":"Менеджер","system":"Система","customer":"Покупатель","warehouse":"Склад"}[lane_id])
        for item in ids: ET.SubElement(lane,f"{{{B}}}flowNodeRef").text=item
    tags={"start":"startEvent","end":"endEvent","task":"task","decision":"exclusiveGateway"}
    for key,(label,kind,*_) in boxes.items():
        if kind=="data": ET.SubElement(process,f"{{{B}}}dataObjectReference",id=key,name=label.replace("\n"," "),dataObjectRef=key+"_object"); ET.SubElement(process,f"{{{B}}}dataObject",id=key+"_object")
        else: ET.SubElement(process,f"{{{B}}}{tags[kind]}",id=key,name=label.replace("\n"," "))
    for i,(a,b,label) in enumerate(arrows):
        tag="association" if a.startswith("data") or b.startswith("data") else "sequenceFlow"
        kw={"id":f"Flow_{i}","sourceRef":a,"targetRef":b}
        if label:kw["name"]=label
        ET.SubElement(process,f"{{{B}}}{tag}",**kw)
    diagram=ET.SubElement(root,f"{{{D}}}BPMNDiagram",id="Diagram_1")
    plane=ET.SubElement(diagram,f"{{{D}}}BPMNPlane",id="Plane_1",bpmnElement="Collaboration_1")
    participant_shape=ET.SubElement(plane,f"{{{D}}}BPMNShape",id="Participant_1_di",bpmnElement="Participant_1",isHorizontal="true")
    ET.SubElement(participant_shape,f"{{{C}}}Bounds",x="15",y="40",width="1690",height="840")
    for lane_id,y,h in (("manager",40,205),("system",250,215),("customer",470,160),("warehouse",635,245)):
        lane_shape=ET.SubElement(plane,f"{{{D}}}BPMNShape",id=f"Lane_{lane_id}_di",bpmnElement=f"Lane_{lane_id}",isHorizontal="true")
        ET.SubElement(lane_shape,f"{{{C}}}Bounds",x="15",y=str(y),width="1690",height=str(h))
    for key,(_,_,x,y,w,h) in boxes.items():
        shape=ET.SubElement(plane,f"{{{D}}}BPMNShape",id=key+"_di",bpmnElement=key)
        ET.SubElement(shape,f"{{{C}}}Bounds",x=str(x),y=str(y),width=str(w),height=str(h))
    for i,(a,b,_) in enumerate(arrows):
        edge=ET.SubElement(plane,f"{{{D}}}BPMNEdge",id=f"Flow_{i}_di",bpmnElement=f"Flow_{i}")
        for x,y in (anchor(boxes[a],boxes[b]),anchor(boxes[b],boxes[a])):ET.SubElement(edge,f"{{{I}}}waypoint",x=str(x),y=str(y))
    ET.ElementTree(root).write(OUT/"bpmn.bpmn",encoding="utf-8",xml_declaration=True)


def main():
    process={
      "start":("Заявка\nполучена","start",130,80,105,80),"register":("Зарегистрировать\nзаявку","task",300,70,205,95),
      "validate":("Проверить\nкорректность заявки","task",570,70,225,95),"availability":("Проверить\nдоступность товаров","task",850,270,230,95),
      "gateway":("Товары\nдоступны?","decision",1130,255,180,125),"price":("Рассчитать\nстоимость заказа","task",1380,265,220,95),
      "confirm":("Подтвердить\nусловия заказа","task",1380,475,220,95),"reserve":("Зарезервировать\nвсе позиции","task",850,375,245,85),
      "notify":("Сообщить\nо дефиците","task",1120,75,220,95),"endok":("Заказ\nс резервом","end",1410,685,130,90),
      "endbad":("Ошибка\nзаявки","end",850,80,115,80),"endshort":("Отказ:\nдефицит","end",1450,80,115,80),"endcancel":("Отказ\nпокупателя","end",1500,570,130,60),
      "receive":("Принять заказ\nк комплектации","task",1120,680,230,90),"data_request":("Заявка","data",360,190,140,60),
      "data_product":("Каталог и\nостатки","data",580,320,180,65),"data_reservation":("Резерв","data",800,780,150,60)}
    flows=[("start","register",""),("register","validate",""),("validate","availability","корректна"),("validate","endbad","нет"),
      ("availability","gateway",""),("gateway","notify","нет"),("notify","endshort",""),("gateway","price","да"),
      ("price","confirm",""),("confirm","reserve","да"),("confirm","endcancel","нет"),("reserve","receive",""),("receive","endok",""),
      ("data_request","register",""),("data_product","availability",""),("reserve","data_reservation","")]
    from generate_bpmn import generate
    generate()
    er={
      "customer":("ПОКУПАТЕЛЬ\nid PK\nname","process",40,80,250,135),"request":("ЗАЯВКА\nid PK\ncustomer_id FK\nconfirmed; agreed_total\ncancelled\ncancellation_reason","process",390,70,270,190),
      "line":("ПОЗИЦИЯ ЗАЯВКИ\nrequest_id PK FK\nproduct_id PK FK\nquantity","process",780,80,300,160),
      "product":("ТОВАР\nid PK\nname; price","process",1220,80,250,135),"stock":("ОСТАТОК\nproduct_id PK FK\nquantity","process",1220,350,250,135),
      "reserve":("РЕЗЕРВ\nid PK\nrequest_id FK\nproduct_id FK\nquantity; active","process",780,350,300,180)}
    er_edges=[("customer","request","1:N"),("request","line","1:N"),("product","line","1:N"),("product","stock","1:1"),("request","reserve","1:N"),("product","reserve","1:N")]
    picture("er_logical",1530,600,er,er_edges);drawio("er_logical",er,er_edges,1530,600)
    from generate_availability import generate as generate_availability
    generate_availability()
    a2={"s":("Начало","start",420,25,150,65),"inp":("Ввод строк\nи цен","data",360,125,270,75),"zero":("Итог = 0","process",390,245,210,65),
        "loop":("Следующая\nстрока","loop",380,355,230,80),"add":("Итог += цена ×\nколичество","process",335,500,320,75),
        "more":("Есть ещё\nстроки?","decision",370,650,250,105),"out":("Вывод итога\nдо копеек","data",360,825,270,75),"e":("Конец","end",420,965,150,65)}
    e2=[("s","inp",""),("inp","zero",""),("zero","loop",""),("loop","add",""),("add","more",""),("more","loop","да"),("more","out","нет"),("out","e","")]
    picture("algo_2",1000,1070,a2,e2);drawio("algo_2",a2,e2,1000,1070)


if __name__ == "__main__": main()
