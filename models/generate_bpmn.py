"""Generate a readable BPMN 2.0 source and its matching PNG preview."""

from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
SCALE = 2
WIDTH, HEIGHT = 1290, 760
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"

LANES = {
    "manager": ("Менеджер", 30, 175),
    "system": ("Система", 205, 220),
    "customer": ("Покупатель", 425, 150),
    "warehouse": ("Склад", 575, 155),
}

# Coordinates are BPMN DI coordinates and PNG drawing coordinates alike.
NODES = {
    "start": ("Заявка получена", "start", "manager", 145, 82, 42, 42),
    "register": ("Зарегистрировать\nзаявку", "task", "manager", 235, 70, 160, 68),
    "validate": ("Проверить\nкорректность заявки", "task", "manager", 445, 70, 185, 68),
    "endbad": ("Ошибка заявки", "end", "manager", 692, 82, 42, 42),
    "notify": ("Сообщить\nо дефиците", "task", "manager", 845, 70, 170, 68),
    "endshort": ("Отказ: дефицит", "end", "manager", 1094, 82, 42, 42),
    "availability": ("Проверить\nдоступность товаров", "task", "system", 445, 250, 185, 68),
    "gateway": ("Товары доступны?", "gateway", "system", 692, 257, 54, 54),
    "price": ("Рассчитать\nстоимость заказа", "task", "system", 845, 250, 170, 68),
    "reserve": ("Зарезервировать\nвсе позиции", "task", "system", 1070, 250, 170, 68),
    "confirm": ("Подтвердить\nусловия заказа", "task", "customer", 845, 460, 170, 68),
    "endcancel": ("Отказ покупателя", "end", "customer", 760, 473, 42, 42),
    "receive": ("Принять заказ\nк комплектации", "task", "warehouse", 970, 615, 170, 68),
    "endok": ("Заказ с резервом", "end", "warehouse", 1185, 628, 42, 42),
    "data_request": ("Заявка", "data", "manager", 274, 151, 85, 46),
    "data_catalog": ("Каталог и\nостатки", "data", "system", 274, 340, 105, 55),
    "data_reserve": ("Резерв", "data", "system", 1070, 365, 94, 50),
}

# Each route includes all bends; connector endpoints touch shape boundaries.
FLOWS = [
    ("start", "register", "", [(187, 103), (235, 103)]),
    ("register", "validate", "", [(395, 104), (445, 104)]),
    ("validate", "endbad", "нет", [(630, 104), (692, 104)]),
    ("validate", "availability", "да", [(537, 138), (537, 250)]),
    ("availability", "gateway", "", [(630, 284), (692, 284)]),
    ("gateway", "notify", "нет", [(719, 257), (719, 179), (930, 179), (930, 138)]),
    ("notify", "endshort", "", [(1015, 104), (1094, 104)]),
    ("gateway", "price", "да", [(746, 284), (845, 284)]),
    ("price", "confirm", "", [(930, 318), (930, 460)]),
    ("confirm", "endcancel", "нет", [(845, 494), (802, 494)]),
    ("confirm", "reserve", "да", [(1015, 494), (1041, 494), (1041, 335), (1155, 335), (1155, 318)]),
    ("reserve", "receive", "", [(1240, 284), (1252, 284), (1252, 601), (1055, 601), (1055, 615)]),
    ("receive", "endok", "", [(1140, 649), (1185, 649)]),
]

ASSOCIATIONS = [
    ("data_request", "register", [(316, 151), (316, 138)]),
    ("data_catalog", "availability", [(379, 367), (411, 367), (411, 284), (445, 284)]),
    ("reserve", "data_reserve", [(1200, 318), (1200, 390), (1164, 390)]),
]


def generate_xml():
    b = "http://www.omg.org/spec/BPMN/20100524/MODEL"
    d = "http://www.omg.org/spec/BPMN/20100524/DI"
    dc = "http://www.omg.org/spec/DD/20100524/DC"
    di = "http://www.omg.org/spec/DD/20100524/DI"
    for prefix, uri in (("bpmn", b), ("bpmndi", d), ("dc", dc), ("di", di)):
        ET.register_namespace(prefix, uri)
    root = ET.Element(f"{{{b}}}definitions", id="Definitions_1", targetNamespace="https://example.org/office-furniture")
    collaboration = ET.SubElement(root, f"{{{b}}}collaboration", id="Collaboration_1")
    ET.SubElement(collaboration, f"{{{b}}}participant", id="Participant_1", name="Поставщик офисной мебели", processRef="Process_1")
    process = ET.SubElement(root, f"{{{b}}}process", id="Process_1", name="Обработка заявки и резервирование мебели", isExecutable="false")
    lane_set = ET.SubElement(process, f"{{{b}}}laneSet", id="LaneSet_1")
    for lane_id, (title, _, _) in LANES.items():
        lane = ET.SubElement(lane_set, f"{{{b}}}lane", id="Lane_{lane_id}", name=title)
        for node_id, node in NODES.items():
            if node[2] == lane_id and node[1] != "data":
                ET.SubElement(lane, f"{{{b}}}flowNodeRef").text = node_id
    tags = {"start": "startEvent", "end": "endEvent", "task": "task", "gateway": "exclusiveGateway"}
    for node_id, (label, kind, _, *_) in NODES.items():
        if kind == "data":
            ET.SubElement(process, f"{{{b}}}dataObject", id=f"{node_id}_object")
            ET.SubElement(process, f"{{{b}}}dataObjectReference", id=node_id, name=label.replace("\n", " "), dataObjectRef=f"{node_id}_object")
        else:
            ET.SubElement(process, f"{{{b}}}{tags[kind]}", id=node_id, name=label.replace("\n", " "))
    for i, (source, target, label, _) in enumerate(FLOWS):
        attrs = {"id": f"Flow_{i}", "sourceRef": source, "targetRef": target}
        if label:
            attrs["name"] = label
        ET.SubElement(process, f"{{{b}}}sequenceFlow", **attrs)
    for i, (source, target, _) in enumerate(ASSOCIATIONS):
        ET.SubElement(process, f"{{{b}}}association", id=f"Association_{i}", sourceRef=source, targetRef=target)
    diagram = ET.SubElement(root, f"{{{d}}}BPMNDiagram", id="Diagram_1")
    plane = ET.SubElement(diagram, f"{{{d}}}BPMNPlane", id="Plane_1", bpmnElement="Collaboration_1")

    def shape(element, x, y, width, height, **attrs):
        item = ET.SubElement(plane, f"{{{d}}}BPMNShape", id=f"{element}_di", bpmnElement=element, **attrs)
        ET.SubElement(item, f"{{{dc}}}Bounds", x=str(x), y=str(y), width=str(width), height=str(height))

    shape("Participant_1", 15, 30, 1260, 700, isHorizontal="true")
    for lane_id, (_, y, height) in LANES.items():
        shape(f"Lane_{lane_id}", 15, y, 1260, height, isHorizontal="true")
    for node_id, (_, _, _, x, y, width, height) in NODES.items():
        shape(node_id, x, y, width, height)
    for prefix, routes in (("Flow", FLOWS), ("Association", ASSOCIATIONS)):
        for i, route in enumerate(routes):
            edge_id = f"{prefix}_{i}"
            edge = ET.SubElement(plane, f"{{{d}}}BPMNEdge", id=f"{edge_id}_di", bpmnElement=edge_id)
            for x, y in route[-1]:
                ET.SubElement(edge, f"{{{di}}}waypoint", x=str(x), y=str(y))
    ET.ElementTree(root).write(OUT / "bpmn.bpmn", encoding="utf-8", xml_declaration=True)


def generate_png():
    image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), "white")
    draw = ImageDraw.Draw(image)
    def xy(points):
        return [(int(x * SCALE), int(y * SCALE)) for x, y in points]
    def box(x, y, w, h):
        return (x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE)
    def font(size, bold=False):
        path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else FONT
        return ImageFont.truetype(path, size * SCALE)
    def label(text, cx, cy, size=16, bold=False, color="#243647"):
        lines = text.split("\n")
        f = font(size, bold)
        line_height = (size + 5) * SCALE
        first = cy * SCALE - line_height * len(lines) / 2
        for i, line in enumerate(lines):
            bounds = draw.textbbox((0, 0), line, font=f)
            draw.text((cx * SCALE - (bounds[2] - bounds[0]) / 2, first + i * line_height), line, font=f, fill=color)

    draw.rectangle(box(15, 30, 1260, 700), outline="#637d93", width=3)
    for lane_id, (title, y, h) in LANES.items():
        draw.rectangle(box(15, y, 1260, h), outline="#b4c3cf", width=2)
        draw.rectangle(box(15, y, 105, h), fill="#eaf0f5", outline="#9badbc", width=2)
        label(title, 67, y + 30, 16, True)
    for node_id, (title, kind, _, x, y, w, h) in NODES.items():
        if kind == "task":
            draw.rounded_rectangle(box(x, y, w, h), radius=11 * SCALE, fill="#e8f4fa" if node_id in {"validate", "availability", "price", "reserve"} else "#fff", outline="#34536b", width=3)
            label(title, x + w / 2, y + h / 2, 16)
        elif kind in {"start", "end"}:
            draw.ellipse(box(x, y, w, h), fill="white", outline="#34536b", width=(5 if kind == "end" else 3))
            label(title, x + w / 2, y + h + 18, 13)
        elif kind == "gateway":
            draw.polygon(xy([(x + w/2,y), (x+w,y+h/2), (x+w/2,y+h), (x,y+h/2)]), fill="#fff5df", outline="#34536b", width=3)
            draw.line(xy([(x+20,y+20),(x+34,y+34)]), fill="#34536b", width=3)
            draw.line(xy([(x+34,y+20),(x+20,y+34)]), fill="#34536b", width=3)
            label(title, x + w/2, y + h + 17, 13)
        else:
            draw.polygon(xy([(x,y),(x+w-13,y),(x+w,y+13),(x+w,y+h),(x,y+h)]), fill="#fff", outline="#60798e", width=2)
            draw.line(xy([(x+w-13,y),(x+w-13,y+13),(x+w,y+13)]), fill="#60798e", width=2)
            label(title, x + w/2, y + h/2, 13)
    for i, (_, _, branch, points) in enumerate(FLOWS):
        draw.line(xy(points), fill="#36546d", width=3 * SCALE, joint="curve")
        x1, y1 = points[-2]; x2, y2 = points[-1]
        if x2 > x1:
            tip = [(x2,y2),(x2-10,y2-5),(x2-10,y2+5)]
        elif x2 < x1:
            tip = [(x2,y2),(x2+10,y2-5),(x2+10,y2+5)]
        elif y2 > y1:
            tip = [(x2,y2),(x2-5,y2-10),(x2+5,y2-10)]
        else:
            tip = [(x2,y2),(x2-5,y2+10),(x2+5,y2+10)]
        draw.polygon(xy(tip), fill="#36546d")
        branch_positions = {2:(662,89), 3:(544,193), 5:(746,167), 7:(796,270), 9:(821,476), 10:(1053,462)}
        if branch:
            bx, by = branch_positions[i]
            label(branch, bx, by, 13, True, "#8c4d21")
    for _, _, points in ASSOCIATIONS:
        for (x1,y1),(x2,y2) in zip(points, points[1:]):
            length = max(abs(x2-x1),abs(y2-y1))
            for start in range(0, length, 10):
                finish = min(start+5,length)
                a=(x1+(x2-x1)*start/length,y1+(y2-y1)*start/length)
                b=(x1+(x2-x1)*finish/length,y1+(y2-y1)*finish/length)
                draw.line(xy([a,b]),fill="#8599a9",width=2*SCALE)
    image.save(OUT / "bpmn.png")


def generate():
    generate_xml()
    generate_png()


if __name__ == "__main__":
    generate()
