from decimal import Decimal
import pdfplumber
from dateutil import parser
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import re

import pdfplumber
import re
from decimal import Decimal
from dateutil import parser

def parse_precio(valor):
    """
    Convierte un string de precio a float, manejando diferentes formatos:
    - 1.234,56 -> 1234.56
    - 1234,56  -> 1234.56
    - 1234.56  -> 1234.56
    Ignora espacios y símbolos de moneda.
    """
    if not valor:
        return 0.0
    val = str(valor).strip().replace(" ", "").replace("$", "")
    # Formato 1.234,56
    if val.count(",") == 1 and val.count(".") > 1:
        val = val.replace(".", "").replace(",", ".")
    # Formato 1234,56
    elif val.count(",") == 1 and val.count(".") == 0:
        val = val.replace(",", ".")
    # ya está en formato 1234.56
    try:
        return float(val)
    except:
        return 0.0

def procesar_archivo_pdf(file):
    pedido_data = {}
    productos = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""

            # -----------------------------
            # Datos principales del pedido
            # -----------------------------
            pedido_data["cliente"] = (re.search(r"Cliente:\s*(.+)", text).group(1).strip()
                                      if re.search(r"Cliente:\s*(.+)", text) else "")

            match_fecha = re.search(r"Fecha Pedido:\s*(.+)", text)
            if match_fecha:
                try:
                    fecha_obj = parser.parse(match_fecha.group(1).strip(), dayfirst=True)
                    pedido_data["fecha_pedido"] = fecha_obj.strftime("%Y-%m-%d")
                except Exception:
                    pedido_data["fecha_pedido"] = ""
            else:
                pedido_data["fecha_pedido"] = ""

            pedido_data["cod_orden_compra"] = (re.search(r"ORDEN DE COMPRA N°\s*(\S+)", text).group(1).strip()
                                               if re.search(r"ORDEN DE COMPRA N°\s*(\S+)", text) else "")

            match_neto = re.search(r"Neto:\s*([\d\.,]+)", text)
            pedido_data["total_neto_pedido"] = parse_precio(match_neto.group(1)) if match_neto else 0.0

            match_iva = re.search(r"IVA\s*\(([\d\.]+)%\):", text)
            pedido_data["iva_pedido"] = float(match_iva.group(1))/100 if match_iva else 0.19

            match_total = re.search(r"TOTAL:\s*([\d\.,]+)", text)
            pedido_data["total_pedido"] = parse_precio(match_total.group(1)) if match_total else 0.0

            # -----------------------------
            # Productos
            # -----------------------------
            table = page.extract_table()
            if table:
                header = table[0]

                def buscar_indice(lista, nombres):
                    for n in nombres:
                        for i, val in enumerate(lista):
                            if val and n.lower() in val.lower():
                                return i
                    return None

                idx_nombre = buscar_indice(header, ["Tipo"])
                idx_tipo = buscar_indice(header, ["Material"])
                idx_tamano = buscar_indice(header, ["Tamaño"])
                idx_obs = buscar_indice(header, ["Observación"])
                idx_cantidad = buscar_indice(header, ["Cantidad", "Stock"])
                idx_precio_unit = buscar_indice(header, ["Precio Unitario", "Precio"])

                if idx_precio_unit is None:
                    print("Advertencia: no se encontró columna 'Precio Unitario' en la tabla del PDF")

                for row in table[1:]:
                    if not row or all(cell is None for cell in row):
                        continue
                    try:
                        cantidad = int((row[idx_cantidad] or "0").replace(".", "").replace(",", "").strip()) \
                            if idx_cantidad is not None else 0
                        precio_unitario = parse_precio(row[idx_precio_unit] if idx_precio_unit is not None else "0")

                        productos.append({
                            "nombre_producto": (row[idx_nombre] or "").strip() if idx_nombre is not None else "",
                            "tipo_producto": (row[idx_tipo] or "").strip() if idx_tipo is not None else "",
                            "tamano_producto": (row[idx_tamano] or "No definido").strip() if idx_tamano is not None else "No definido",
                            "observacion_producto": (row[idx_obs] or "").strip() if idx_obs is not None else "",
                            "cantidad_producto": cantidad,
                            "precio_unitario_producto": precio_unitario
                        })
                    except Exception as e:
                        print("Error procesando fila tabla:", row, e)
            else:
                # Fallback línea a línea
                for line in text.splitlines():
                    if "Subtotal" in line or "Nombre" in line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            cantidad = int(parts[-2].replace(".", "").replace(",", ""))
                            precio_unitario = parse_precio(parts[-1])
                            nombre = " ".join(parts[:-2])
                            productos.append({
                                "nombre_producto": nombre,
                                "tipo_producto": "",
                                "tamano_producto": "No definido",
                                "observacion_producto": "",
                                "cantidad_producto": cantidad,
                                "precio_unitario_producto": precio_unitario
                            })
                        except Exception as e:
                            print("Error procesando línea:", line, e)

    return pedido_data, productos


def procesar_archivo_ocr(file):
    # Datos principales del pedido
    pedido_data = {
        "cliente": "",
        "fecha_pedido": "",
        "cod_orden_compra": "",
    }
    productos = []

    # Convertir PDF a imágenes o usar la imagen directamente
    try:
        paginas = convert_from_bytes(file.read())
    except:
        file.seek(0)
        paginas = [Image.open(file)]

    encabezados = {"nombre", "tipo", "tamaño", "observación", "cantidad", "precio unitario"}

    for pagina in paginas:
        text = pytesseract.image_to_string(pagina, lang='spa')
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # -----------------------------
        # Extraer datos del pedido
        # -----------------------------
        for line in lines:
            if "Cliente:" in line:
                pedido_data["cliente"] = line.split("Cliente:")[1].strip()
            elif "Fecha:" in line:
                try:
                    fecha_str = line.split("Fecha:")[1].strip()
                    fecha_obj = parser.parse(fecha_str, dayfirst=True)
                    pedido_data["fecha_pedido"] = fecha_obj.strftime("%Y-%m-%d")
                except:
                    pedido_data["fecha_pedido"] = ""
            elif "Orden de Compra:" in line:
                pedido_data["cod_orden_compra"] = line.split("Orden de Compra:")[1].strip()

        # -----------------------------
        # Extraer productos
        # -----------------------------
        current_producto = {}
        seccion_productos = False

        for line in lines:
            line_lower = line.lower()

            # Detectar inicio de sección de productos
            if "productos" in line_lower:
                seccion_productos = True
                continue

            if not seccion_productos:
                continue  # Ignorar líneas fuera de la sección de productos

            # Ignorar encabezados de tabla
            if line_lower in encabezados:
                continue

            # Detectar precio unitario: contiene solo números
            line_clean = line.replace(",", ".")
            try:
                precio = Decimal(line_clean)
                current_producto["precio_unitario_producto"] = precio
                current_producto.setdefault("cantidad_producto", 1)
                continue
            except:
                pass  # No es precio

            # Detectar nombre (texto largo, varias palabras)
            if all(c.isalpha() or c.isspace() for c in line) and len(line.split()) >= 2:
                if current_producto:
                    productos.append({
                        "nombre_producto": current_producto.get("nombre_producto", ""),
                        "tipo_producto": current_producto.get("tipo_producto", ""),
                        "tamano_producto": current_producto.get("tamano_producto", ""),
                        "observacion_producto": current_producto.get("observacion_producto", ""),
                        "cantidad_producto": current_producto.get("cantidad_producto", 1),
                        "precio_unitario_producto": current_producto.get("precio_unitario_producto", Decimal("0.0"))
                    })
                    current_producto = {}
                current_producto["nombre_producto"] = line
            # Detectar tipo
            elif line_lower in ["metal", "pvc", "madera", "plastico"]:
                current_producto["tipo_producto"] = line
            # Detectar tamaño
            elif line.upper() in ["XL","L","M","S"]:
                current_producto["tamano_producto"] = line
            # Observación: cualquier texto restante
            else:
                current_producto["observacion_producto"] = line

        # Guardar último producto
        if current_producto:
            productos.append({
                "nombre_producto": current_producto.get("nombre_producto", ""),
                "tipo_producto": current_producto.get("tipo_producto", ""),
                "tamano_producto": current_producto.get("tamano_producto", ""),
                "observacion_producto": current_producto.get("observacion_producto", ""),
                "cantidad_producto": current_producto.get("cantidad_producto", 1),
                "precio_unitario_producto": current_producto.get("precio_unitario_producto", Decimal("0.0"))
            })

    # Debug
    print("===== RESULTADO OCR =====")
    print("Pedido:", pedido_data)
    print("Productos:", productos)

    return pedido_data, productos
