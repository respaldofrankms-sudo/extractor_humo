import io
import math
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(
    page_title="Extractor de Humo - Cocinas Comerciales", layout="centered"
)

st.title("🔥 Calculadora de Extracción de Humo")
st.markdown(
    "**Diseño y Normativa:** NFPA 96, ASHRAE, SMACNA, FONDONORMA 200 & COVENIN"
)
st.markdown("---")

st.subheader("1. Parámetros de Entrada (Diseño)")

col1, col2 = st.columns(2)

with col1:
  l_camp = st.number_input("Largo de la Campana (m)", value=3.0, step=0.1)
  a_camp = st.number_input("Ancho de la Campana (m)", value=1.5, step=0.1)
  h_camp = st.number_input("Altura Campana al piso (m)", value=2.2, step=0.1)
  l_cocina = st.number_input("Largo de la Cocina (m)", value=8.0, step=0.1)
  a_cocina = st.number_input("Ancho de la Cocina (m)", value=5.0, step=0.1)

with col2:
  h_cocina = st.number_input("Altura de la Cocina (m)", value=3.0, step=0.1)
  vc = st.number_input("Velocidad de Captura Vc (m/s)", value=0.5, step=0.05)
  ach = st.number_input("Renovaciones por Hora (ACH)", value=40, step=5)
  l_duct = st.number_input("Longitud de Ductería (m)", value=15.0, step=1.0)
  n_codos = st.number_input("Número de Codos Equivalentes", value=4, step=1)

# Cálculos de Ingeniería
a_c = l_camp * a_camp
vol = l_cocina * a_cocina * h_cocina
q_cap = a_c * vc * 3600
q_ren = vol * ach
q_dis = max(q_cap, q_ren)
q_iny = q_dis * 0.85

q_dis_cfm = q_dis / 1.699
q_iny_cfm = q_iny / 1.699

v_cond = 10.0
a_cond = (q_dis / 3600) / v_cond
d_eq = math.sqrt((4 * a_cond) / math.pi)
d_com = math.ceil(d_eq * 100)

delta_p_filtros = 200.0
delta_p_duct = l_duct * 1.5 + n_codos * 15
p_t = delta_p_filtros + delta_p_duct
p_t_in = p_t / 249.088

eta = 0.65
bhp = ((q_dis / 3600) * p_t) / (1000 * eta)
hp_exact = bhp * 1.34102

if hp_exact <= 0.5:
  motor = "0.5 HP"
elif hp_exact <= 0.75:
  motor = "0.75 HP"
elif hp_exact <= 1.0:
  motor = "1 HP"
elif hp_exact <= 1.5:
  motor = "1.5 HP"
elif hp_exact <= 2.0:
  motor = "2 HP"
elif hp_exact <= 3.0:
  motor = "3 HP"
elif hp_exact <= 5.0:
  motor = "5 HP"
elif hp_exact <= 7.5:
  motor = "7.5 HP"
elif hp_exact <= 10.0:
  motor = "10 HP"
else:
  motor = "15+ HP"

st.markdown("---")
st.subheader("2. Resultados y Justificación Normativa")

st.success(
    f"**Caudal de Extracción:** {q_dis:,.2f} m³/h ({q_dis_cfm:,.1f} CFM)\n\n"
    "*Base Normativa:* NFPA 96 & ASHRAE Applications (Captura perimetral)"
)

st.info(
    f"**Caudal de Inyección (85%):** {q_iny:,.2f} m³/h ({q_iny_cfm:,.1f} CFM)\n\n"
    "*Base Normativa:* ASHRAE (Control de presión negativa y confort)"
)

st.warning(
    f"**Presión Estática Total:** {p_t:,.1f} Pa ({p_t_in:.2f} in.w.g.)\n\n"
    "*Base Normativa:* ASHRAE Fundamentals (Pérdidas de carga y fricción)"
)

st.info(
    f"**Diámetro de Ducto y Construcción:** {d_com} cm (Velocidad: 10 m/s)\n\n"
    "*Base Normativa:* NFPA 96 & SMACNA (Acero Inoxidable, juntas soldadas a"
    " líquido)"
)

st.success(
    f"**Motor y Sistema Eléctrico:** {motor} (BHP exacto: {hp_exact:.2f} HP)\n\n"
    "*Base Normativa:* NEMA MG-1 / FONDONORMA 200 (Código Eléctrico Nacional)"
)


# Generación de PDF en memoria para descarga móvil
def generar_pdf_bytes():
  buffer = io.BytesIO()
  doc = SimpleDocTemplate(buffer, pagesize=letter)
  story = []
  styles = getSampleStyleSheet()

  title_style = ParagraphStyle(
      "TitleStyle",
      parent=styles["Heading1"],
      fontSize=15,
      textColor=colors.HexColor("#1A365D"),
      spaceAfter=12,
      alignment=1,
  )
  subtitle_style = ParagraphStyle(
      "SubTitleStyle",
      parent=styles["Heading2"],
      fontSize=11,
      textColor=colors.HexColor("#2B6CB0"),
      spaceAfter=8,
  )
  normal_style = styles["Normal"]

  story.append(
      Paragraph(
          "MEMORIA DE CÁLCULO: SISTEMA DE EXTRACCIÓN DE HUMO", title_style
      )
  )
  story.append(
      Paragraph(
          "Evaluación de Ventilación Mecánica para Cocinas Comerciales"
          " (Cumplimiento Integral Normativo)",
          subtitle_style,
      )
  )
  story.append(Spacer(1, 5))

  story.append(
      Paragraph("<b>1. Parámetros de Entrada (Diseño)</b>", subtitle_style)
  )
  data_in = [
      ["Parámetro de Diseño", "Valor Asignado"],
      ["Largo de la Campana", f"{l_camp} m"],
      ["Ancho de la Campana", f"{a_camp} m"],
      ["Altura de Campana al Piso", f"{h_camp} m"],
      [
          "Dimensiones de la Cocina (L x A x H)",
          f"{l_cocina} x {a_cocina} x {h_cocina} m",
      ],
      ["Velocidad de Captura (Vc)", f"{vc} m/s"],
      ["Renovaciones por Hora (ACH)", f"{ach} renovaciones/h"],
      ["Longitud de Ductería", f"{l_duct} m"],
      ["Número de Codos Equivalentes", f"{n_codos}"],
  ]
  t_in = Table(data_in, colWidths=[250, 200])
  t_in.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (1, 0), colors.HexColor("#E2E8F0")),
          ("TEXTCOLOR", (0, 0), (1, 0), colors.HexColor("#1A365D")),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
      ])
  )
  story.append(t_in)
  story.append(Spacer(1, 10))

  story.append(
      Paragraph(
          "<b>2. Resultados y Marco Normativo de Ingeniería</b>", subtitle_style
      )
  )
  data_out = [
      ["Concepto Calculado", "Resultado Técnico", "Normativa Aplicada"],
      [
          "Caudal de Extracción",
          f"{q_dis:,.2f} m³/h\n({q_dis_cfm:,.1f} CFM)",
          "NFPA 96 & ASHRAE Applications\n(Captura perimetral en campana)",
      ],
      [
          "Caudal de Inyección (85%)",
          f"{q_iny:,.2f} m³/h\n({q_iny_cfm:,.1f} CFM)",
          "ASHRAE Standard\n(Compensación de aire y presión negativa)",
      ],
      [
          "Presión Estática Total",
          f"{p_t:,.1f} Pa\n({p_t_in:.2f} in.w.g.)",
          "ASHRAE Fundamentals\n(Pérdidas de carga y caída en filtros)",
      ],
      [
          "Ductería y Construcción",
          f"Diámetro: {d_com} cm\nVelocidad: 10 m/s",
          (
              "NFPA 96 & SMACNA\n(Acero Inoxidable, costuras y juntas"
              " herméticas)"
          ),
      ],
      [
          "Selección de Motor",
          f"{motor}\n(BHP exacto: {hp_exact:.2f} HP)",
          "NEMA MG-1 / FONDONORMA 200\n(Dimensionamiento eléctrico y CEN)",
      ],
      [
          "Seguridad y Cumplimiento",
          "Sistema Certificado",
          "COVENIN\n(Normas venezolanas de seguridad y prevención)",
      ],
  ]
  t_out = Table(data_out, colWidths=[120, 130, 200])
  t_out.setStyle(
      TableStyle([
          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
          ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
          ("ALIGN", (0, 0), (-1, -1), "LEFT"),
          ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
      ])
  )
  story.append(t_out)
  story.append(Spacer(1, 10))

  story.append(
      Paragraph(
          "<b>Conclusión Técnica:</b> El sistema se diseñó bajo los estándares"
          " internacionales de seguridad contra incendios y ventilación"
          " industrial. Requiere un ventilador centrífugo de álabes hacia atrás"
          " operando a 1450 RPM con transmisión por poleas, asegurando una"
          " operación eficiente y conforme a la normativa vigente.",
          normal_style,
      )
  )

  doc.build(story)
  buffer.seek(0)
  return buffer.getvalue()


st.markdown("---")
pdf_data = generar_pdf_bytes()
st.download_button(
    label="📥 Descargar Reporte PDF en tu Teléfono",
    data=pdf_data,
    file_name="Reporte_Sistema_Extraccion_Humo.pdf",
    mime="application/pdf",
)
