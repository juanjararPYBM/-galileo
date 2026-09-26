from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation

OUT = "/home/user/-galileo/cotizaciones/dotacion_consultorio_medicina_general.xlsx"
F = "Arial"
# (categoría, implemento, especificación, cantidad, unidad, valor unitario COP, prioridad, observación)
items = [
 ("Equipos biomédicos","Tensiómetro aneroide adulto","Con brazalete adulto estándar, calibrado",1,"Unidad",150000,"Obligatorio","Requiere hoja de vida y plan de calibración anual"),
 ("Equipos biomédicos","Brazaletes adicionales","Pediátrico y adulto obeso",2,"Unidad",60000,"Obligatorio",""),
 ("Equipos biomédicos","Tensiómetro digital de brazo","Automático, validado clínicamente",1,"Unidad",250000,"Recomendado",""),
 ("Equipos biomédicos","Fonendoscopio","Doble campana, tipo Littmann Classic III o similar",1,"Unidad",650000,"Obligatorio","Marcas genéricas desde ~150.000"),
 ("Equipos biomédicos","Equipo de órganos de los sentidos","Otoscopio + oftalmoscopio portátil, halógeno/LED",1,"Kit",1500000,"Obligatorio","Welch Allyn/Riester; versión de pared ~3.500.000"),
 ("Equipos biomédicos","Termómetro digital de contacto","Punta flexible",2,"Unidad",20000,"Obligatorio",""),
 ("Equipos biomédicos","Termómetro infrarrojo","Frente, sin contacto",1,"Unidad",120000,"Recomendado",""),
 ("Equipos biomédicos","Pulsioxímetro","De dedo, adulto/pediátrico",1,"Unidad",120000,"Obligatorio",""),
 ("Equipos biomédicos","Glucómetro","Kit con lancetero",1,"Kit",90000,"Recomendado",""),
 ("Equipos biomédicos","Báscula de pie con tallímetro","Digital o mecánica, hasta 180 kg",1,"Unidad",950000,"Obligatorio",""),
 ("Equipos biomédicos","Báscula pesabebés","Digital, hasta 20 kg",1,"Unidad",450000,"Obligatorio","Si se atiende población pediátrica"),
 ("Equipos biomédicos","Infantómetro","Para medición en decúbito",1,"Unidad",180000,"Obligatorio","Si se atiende población pediátrica"),
 ("Equipos biomédicos","Cinta métrica","Inextensible, para perímetros",2,"Unidad",15000,"Obligatorio",""),
 ("Equipos biomédicos","Martillo de reflejos","Tipo Taylor",1,"Unidad",25000,"Obligatorio",""),
 ("Equipos biomédicos","Diapasón","128 Hz",1,"Unidad",60000,"Recomendado",""),
 ("Equipos biomédicos","Monofilamento 10 g","Tamizaje pie diabético",1,"Unidad",25000,"Recomendado",""),
 ("Equipos biomédicos","Linterna de diagnóstico","LED, tipo lápiz",1,"Unidad",40000,"Obligatorio",""),
 ("Equipos biomédicos","Tabla de Snellen","Optotipos adulto/infantil",1,"Unidad",30000,"Obligatorio",""),
 ("Equipos biomédicos","Negatoscopio","1 cuerpo, LED",1,"Unidad",350000,"Opcional",""),
 ("Equipos biomédicos","Electrocardiógrafo","3 canales, con interpretación",1,"Unidad",4500000,"Opcional",""),
 ("Mobiliario clínico","Camilla de examen","Tapizado sanitario, cabecera graduable",1,"Unidad",750000,"Obligatorio",""),
 ("Mobiliario clínico","Escalerilla","2 pasos, antideslizante",1,"Unidad",180000,"Obligatorio",""),
 ("Mobiliario clínico","Lámpara de examen","Cuello de cisne, LED, rodachinas",1,"Unidad",450000,"Obligatorio",""),
 ("Mobiliario clínico","Mesa auxiliar / de Mayo","Acero inoxidable",1,"Unidad",350000,"Recomendado",""),
 ("Mobiliario clínico","Biombo","2-3 cuerpos, lavable",1,"Unidad",450000,"Obligatorio","Privacidad del paciente"),
 ("Mobiliario clínico","Taburete giratorio","Altura graduable, rodachinas",1,"Unidad",250000,"Recomendado",""),
 ("Mobiliario clínico","Vitrina para insumos","Metálica, puertas de vidrio",1,"Unidad",800000,"Recomendado",""),
 ("Mobiliario de oficina","Escritorio","Superficie lavable",1,"Unidad",600000,"Obligatorio",""),
 ("Mobiliario de oficina","Silla ergonómica médico","Con rodachinas",1,"Unidad",450000,"Obligatorio",""),
 ("Mobiliario de oficina","Sillas paciente / acompañante","Tapizado lavable",2,"Unidad",150000,"Obligatorio",""),
 ("Mobiliario de oficina","Archivador","4 gavetas, con llave",1,"Unidad",700000,"Recomendado","Custodia de documentos"),
 ("Tecnología","Computador","Para historia clínica electrónica",1,"Unidad",2800000,"Obligatorio",""),
 ("Tecnología","Impresora multifuncional","Láser",1,"Unidad",700000,"Recomendado",""),
 ("Instrumental","Equipo de pequeña cirugía","Porta agujas, pinzas con/sin garra, tijeras, mango de bisturí",2,"Kit",250000,"Recomendado","Si se realizan procedimientos menores"),
 ("Instrumental","Pinza de Kelly","Recta/curva, 14 cm",2,"Unidad",30000,"Recomendado",""),
 ("Instrumental","Riñonera","Acero inoxidable",2,"Unidad",35000,"Obligatorio",""),
 ("Instrumental","Bandeja con tapa","Acero inoxidable",2,"Unidad",90000,"Recomendado",""),
 ("Emergencias","Resucitador manual adulto","Con mascarillas y reservorio",1,"Unidad",180000,"Obligatorio",""),
 ("Emergencias","Resucitador manual pediátrico","Con mascarillas y reservorio",1,"Unidad",180000,"Recomendado",""),
 ("Emergencias","Cánulas orofaríngeas","Juego de tallas",1,"Juego",40000,"Obligatorio",""),
 ("Emergencias","Desfibrilador externo automático (DEA)","Con parches adulto/pediátrico",1,"Unidad",6500000,"Opcional",""),
 ("Bioseguridad y residuos","Caneca roja de pedal","Residuos biosanitarios",1,"Unidad",90000,"Obligatorio","Gestión de residuos hospitalarios"),
 ("Bioseguridad y residuos","Canecas de pedal blanca / negra","Aprovechables / no aprovechables",2,"Unidad",80000,"Obligatorio",""),
 ("Bioseguridad y residuos","Guardián","Contenedor de cortopunzantes 1,5 L",3,"Unidad",12000,"Obligatorio",""),
 ("Bioseguridad y residuos","Bolsas rojas","Paquete x50",2,"Paquete",25000,"Obligatorio",""),
 ("Bioseguridad y residuos","Dispensadores jabón y toallas","Para lavamanos",1,"Juego",120000,"Obligatorio",""),
 ("Bioseguridad y residuos","Kit de derrames","Material absorbente, EPP, bolsas",1,"Kit",150000,"Obligatorio",""),
 ("Consumibles","Guantes de examen de nitrilo","Caja x100",5,"Caja",30000,"Obligatorio",""),
 ("Consumibles","Guantes estériles","Caja x50 pares",1,"Caja",90000,"Recomendado",""),
 ("Consumibles","Tapabocas quirúrgicos","Caja x50",3,"Caja",15000,"Obligatorio",""),
 ("Consumibles","Respiradores N95","Caja x20",1,"Caja",60000,"Recomendado",""),
 ("Consumibles","Papel para camilla","Rollo",6,"Rollo",25000,"Obligatorio",""),
 ("Consumibles","Bajalenguas","Caja x100",3,"Caja",8000,"Obligatorio",""),
 ("Consumibles","Gasas estériles","Paquete x100",2,"Paquete",30000,"Obligatorio",""),
 ("Consumibles","Algodón","500 g",1,"Unidad",15000,"Obligatorio",""),
 ("Consumibles","Alcohol antiséptico 70%","Litro",2,"Unidad",18000,"Obligatorio",""),
 ("Consumibles","Gel antibacterial","Litro",3,"Unidad",20000,"Obligatorio",""),
 ("Consumibles","Clorhexidina jabonosa 4%","Frasco 1 L",1,"Unidad",45000,"Recomendado",""),
 ("Consumibles","Desinfectante de superficies","Amonio cuaternario, galón",2,"Galón",60000,"Obligatorio",""),
 ("Consumibles","Jeringas desechables 5 ml","Caja x100",1,"Caja",45000,"Recomendado",""),
 ("Consumibles","Suturas nylon 3-0 / 4-0","Caja x12",2,"Caja",90000,"Recomendado",""),
 ("Consumibles","Hojas de bisturí","Caja x100",1,"Caja",45000,"Recomendado",""),
 ("Consumibles","Tiras de glucometría","Caja x50",2,"Caja",70000,"Recomendado",""),
 ("Consumibles","Espéculos vaginales desechables","Talla M, paquete x25",2,"Paquete",45000,"Recomendado","Si se toma citología"),
]
BOTH = {'Termómetro digital de contacto': "Dr. Durán: 'Termómetro' (botiquín)", 'Guantes de examen de nitrilo': "Dr. Durán: 'Guantes de examen' y 'Guantes desechables'", 'Gasas estériles': 'Dr. Durán: gasas para retiro de puntos y botiquín', 'Algodón': 'Dr. Durán: botiquín', 'Alcohol antiséptico 70%': 'Dr. Durán: botiquín', 'Dispensadores jabón y toallas': 'Dr. Durán pide el jabón y las toallas (ver Aseo)'}
duran = [
 ("Atención de pacientes","Caja menor con llave","Metálica, para guardar dinero de caja chica",1,"Unidad",80000,"Recomendado","Dr. Durán: 'Caja chica (para almacenamiento) – para guardar dinero'"),
 ("Instrumental","Kit para retiro de puntos","Tijera de retiro de puntos (Spencer) + pinza de disección",2,"Kit",60000,"Obligatorio","Gasas incluidas en Consumibles; según protocolo"),
 ("Papelería y oficina","Lapiceros, lápices y marcadores","Surtido (incluye resaltadores)",1,"Lote",50000,"Obligatorio",""),
 ("Papelería y oficina","Engrapadora (cosedora)","Con caja de ganchos",1,"Unidad",25000,"Obligatorio",""),
 ("Papelería y oficina","Clips para papel","Caja x100",2,"Caja",5000,"Obligatorio",""),
 ("Papelería y oficina","Sacaganchos","Metálico",1,"Unidad",5000,"Obligatorio",""),
 ("Papelería y oficina","Perforadora","2 huecos",1,"Unidad",25000,"Obligatorio",""),
 ("Papelería y oficina","Resma de papel tamaño carta","500 hojas, 75 g",5,"Resma",25000,"Obligatorio",""),
 ("Papelería y oficina","Mostrador de sobres y carpetas","Organizador de escritorio / revistero",1,"Unidad",60000,"Recomendado",""),
 ("Papelería y oficina","Formatos de informes","Impresión de formatos (lote)",1,"Lote",80000,"Obligatorio","Depende de cantidad y tipo de formato"),
 ("Papelería y oficina","Tinta para sello y almohadilla","Almohadilla + frasco de tinta",1,"Juego",20000,"Recomendado",""),
 ("Papelería y oficina","Tijeras de oficina","Punta roma",1,"Unidad",8000,"Obligatorio",""),
 ("Papelería y oficina","Cinta adhesiva","Rollo transparente",3,"Rollo",4000,"Obligatorio",""),
 ("Papelería y oficina","Pegamento","Barra 40 g",2,"Unidad",5000,"Obligatorio",""),
 ("Papelería y oficina","Calculadora","De escritorio, 12 dígitos",1,"Unidad",40000,"Recomendado",""),
 ("Papelería y oficina","Libretas","Cuaderno / libreta de notas",5,"Unidad",6000,"Obligatorio",""),
 ("Papelería y oficina","Repuestos (bolígrafos, etc.)","Minas, grapas, cartuchos varios",1,"Lote",20000,"Recomendado",""),
 ("Aseo y baño","Papel higiénico","Paquete x12 rollos institucional",2,"Paquete",40000,"Obligatorio",""),
 ("Aseo y baño","Jabón de manos","Líquido antibacterial, galón",2,"Galón",35000,"Obligatorio",""),
 ("Aseo y baño","Toallas de papel","Interfoliadas, paquete x150 (fardo)",2,"Fardo",60000,"Obligatorio","Se prefieren de papel sobre tela por bioseguridad"),
 ("Aseo y baño","Ambientador","Aerosol",2,"Unidad",15000,"Recomendado",""),
 ("Botiquín de primeros auxilios","Botiquín","Gabinete o maletín con compartimentos",1,"Unidad",60000,"Obligatorio",""),
 ("Botiquín de primeros auxilios","Curitas","Caja x100",1,"Caja",15000,"Obligatorio","Gasas, algodón, guantes, termómetro y alcohol ya están en la lista"),
 ("Botiquín de primeros auxilios","Medicamentos básicos","Acetaminofén, loratadina, sales de rehidratación, antiácido",1,"Lote",100000,"Recomendado","Definir listado con el Dr. Durán"),
 ("Botiquín de primeros auxilios","Ibuprofeno 400 mg","Caja x50 tabletas",2,"Caja",15000,"Recomendado",""),
]
N_DURAN = 10

wb = Workbook(); ws = wb.active; ws.title = "Lista Unificada"
thin = Side(style="thin", color="BFBFBF"); border = Border(left=thin,right=thin,top=thin,bottom=thin)
head_fill = PatternFill("solid", fgColor="1F4E78"); yellow = PatternFill("solid", fgColor="FFFF00")
sect_fill = PatternFill("solid", fgColor="DDEBF7")

ws["A1"] = "Dotación consultorio de medicina general — lista unificada para cotización"
ws["A1"].font = Font(name=F, size=14, bold=True)
ws["A2"] = "Valores aproximados en pesos colombianos (COP), mercado colombiano 2026. Incluye la lista del Dr. Sergio Durán (PDF “Dotación necesaria para los consultorios”). Celdas amarillas = ítems adicionales."
ws["A2"].font = Font(name=F, size=9, italic=True)

headers = ["#","Categoría","Implemento","Especificación","Cantidad","Unidad","Valor unitario aprox. (COP)","Valor total aprox. (COP)","Prioridad","Fuente","Observaciones"]
H = 4
for c,h in enumerate(headers,1):
    cell = ws.cell(H,c,h); cell.font = Font(name=F,bold=True,color="FFFFFF"); cell.fill = head_fill
    cell.alignment = Alignment(horizontal="center",vertical="center",wrap_text=True); cell.border = border
ws.row_dimensions[H].height = 32

money = '$#,##0;($#,##0);-'
def write_row(r, n, data, src, inp=False):
    vals = [n,*data[:5]]
    for c,v in enumerate(vals,1): ws.cell(r,c,v)
    ws.cell(r,7,data[5] if data[5] is not None else None)
    ws.cell(r,8,f'=IF(OR(E{r}="",G{r}=""),"",E{r}*G{r})')
    ws.cell(r,9,data[6]); ws.cell(r,10,src); ws.cell(r,11,data[7])
    for c in range(1,12):
        cell = ws.cell(r,c); cell.font = Font(name=F,size=10, color=("0000FF" if c in (5,7) and not inp else "000000"))
        cell.border = border; cell.alignment = Alignment(vertical="center",wrap_text=c in (3,4,11))
        if inp and c not in (1,8,10): cell.fill = yellow
    ws.cell(r,7).number_format = money; ws.cell(r,8).number_format = money

r = H+1
n = 0
for it in items:
    n += 1; src = "Dotación básica"; it = list(it)
    if it[1] in BOTH:
        src = "Ambas"; it[7] = (it[7] + "; " if it[7] else "") + BOTH[it[1]]
    write_row(r,n,it,src); r += 1
for it in duran:
    n += 1; write_row(r,n,it,"Dr. Sergio Durán"); r += 1
last_base = r-1
# sección Dr. Durán
ws.cell(r,1,"Filas libres para ítems adicionales").font = Font(name=F,bold=True)
for c in range(1,12): ws.cell(r,c).fill = sect_fill
ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=11); r += 1
first_d = r
for k in range(N_DURAN):
    write_row(r,n+k+1,("","","",None,"",None,"",""),"",inp=True); r += 1
last_d = r-1
# total
ws.cell(r,7,"TOTAL APROX.").font = Font(name=F,bold=True)
ws.cell(r,8,f"=SUM(H{H+1}:H{last_d})").font = Font(name=F,bold=True)
ws.cell(r,8).number_format = money
for c in (7,8): ws.cell(r,c).border = border; ws.cell(r,c).fill = sect_fill
total_row = r

ws.cell(H+1,7).comment = Comment("Precios aproximados de referencia (COP, 2026) a partir de rangos típicos de distribuidores de dispositivos médicos en Colombia, IVA incluido cuando aplica. Pueden variar ±20-30% según marca, proveedor y volumen. Validar con 2-3 cotizaciones formales.","Claude")

dv = DataValidation(type="list", formula1='"Obligatorio,Recomendado,Opcional"', allow_blank=True)
ws.add_data_validation(dv); dv.add(f"I{H+1}:I{last_d}")
widths = [5,22,34,40,10,10,18,18,13,17,36]
for i,w in enumerate(widths,1): ws.column_dimensions[chr(64+i)].width = w
ws.freeze_panes = f"C{H+1}"
ws.auto_filter.ref = f"A{H}:K{last_d}"

# Resumen
rs = wb.create_sheet("Resumen")
rs["A1"] = "Resumen de la cotización"; rs["A1"].font = Font(name=F,size=14,bold=True)
L = "'Lista Unificada'"
rng = lambda col: f"{L}!${col}${H+1}:${col}${last_d}"
def hdr(row, labels):
    for c,t in enumerate(labels,1):
        x = rs.cell(row,c,t); x.font = Font(name=F,bold=True,color="FFFFFF"); x.fill = head_fill; x.border = border
def line(row, label, formula, bold=False):
    a = rs.cell(row,1,label); b = rs.cell(row,2,formula)
    for x in (a,b): x.font = Font(name=F,bold=bold, color=("008000" if x is b and not bold else "000000")); x.border = border
    b.number_format = money
row = 3; hdr(row,["Por categoría","Valor aprox. (COP)"]); row += 1
cats = list(dict.fromkeys(i[0] for i in items+duran)); cstart = row
for cat in cats:
    line(row,cat,f'=SUMIFS({rng("H")},{rng("B")},A{row})'); row += 1
line(row,"Otras categorías / sin clasificar",f"={L}!H{total_row}-SUM(B{cstart}:B{row-1})"); row += 1
line(row,"TOTAL (1 consultorio)",f"={L}!H{total_row}",True); trow=row; row += 1
rs.cell(row,1,"Consultorios a dotar").font=Font(name=F); c=rs.cell(row,2,1); c.font=Font(name=F,color="0000FF"); c.fill=yellow
for x in (rs.cell(row,1),c): x.border=border
c.comment=Comment("Dato a confirmar: la lista del Dr. Durán indica que el consultorio 1104 necesita la misma dotación que el 1105-01. Ponga 2 si se cotizan ambos.","Claude"); nrow=row; row += 1
line(row,"TOTAL GENERAL",f"=B{trow}*B{nrow}",True); row += 2
hdr(row,["Por fuente","Valor aprox. (COP)"]); row += 1
for s in ["Dotación básica","Dr. Sergio Durán","Ambas"]:
    line(row,s,f'=SUMIFS({rng("H")},{rng("J")},A{row})'); row += 1
row += 1
hdr(row,["Por prioridad","Valor aprox. (COP)"]); row += 1
for p in ["Obligatorio","Recomendado","Opcional"]:
    line(row,p,f'=SUMIFS({rng("H")},{rng("I")},A{row})'); row += 1
row += 1
notes = [
 "Notas y supuestos:",
 "• Valores aproximados en COP (2026), referencia de distribuidores de dispositivos médicos en Colombia; variación esperada ±20-30%.",
 "• Prioridad orientativa según requisitos típicos de habilitación de consulta externa de medicina general (Resolución 3100 de 2019); verificar con la Secretaría de Salud.",
 "• Los equipos biomédicos requieren registro INVIMA, hoja de vida y plan de mantenimiento/calibración.",
 "• Cantidades pensadas para 1 consultorio y dotación inicial de consumibles (~1 mes).",
 "• Fuente 'Ambas' = ítem pedido por el Dr. Durán que ya estaba en la dotación básica (se unificó sin duplicar).",
 "• Según el Dr. Durán, el consultorio 1104 necesita la misma dotación que el 1105-01. Ajuste 'Consultorios a dotar' arriba.",
 "• Filas amarillas de 'Lista Unificada' = ítems adicionales; el total se actualiza solo.",
]
for n in notes:
    rs.cell(row,1,n).font = Font(name=F,size=9,bold=n.endswith(":")); row += 1
rs.column_dimensions["A"].width = 40; rs.column_dimensions["B"].width = 22
from openpyxl.workbook.properties import CalcProperties
wb.calculation = CalcProperties(fullCalcOnLoad=True)
wb.save(OUT); print(OUT, last_base, first_d, last_d, total_row)
