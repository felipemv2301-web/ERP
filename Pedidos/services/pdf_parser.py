from decimal import Decimal
import pdfplumber
from dateutil import parser
from pdf2image import convert_from_bytes
from PIL import Image
import pytesseract
import re

def procesar_archivo_pdf(file):
    pedido_data = {}
    productos = []

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            # -----------------------------
            # Extraer datos del pedido/orden
            # -----------------------------
            if "Cliente:" in text:
                try:
                    pedido_data["cliente"] = text.split("Cliente:")[1].split("\n")[0].strip()
                except:
                    pedido_data["cliente"] = ""

            if "Fecha:" in text:
                try:
                    fecha_str = text.split("Fecha:")[1].split("\n")[0].strip()
                    # Convertimos automáticamente a YYYY-MM-DD
                    fecha_obj = parser.parse(fecha_str, dayfirst=False)  # Ajusta dayfirst según tu PDF
                    pedido_data["fecha_pedido"] = fecha_obj.strftime("%Y-%m-%d")
                except Exception as e:
                    print("Error procesando fecha:", fecha_str, e)
                    pedido_data["fecha_pedido"] = ""

            if "Orden de Compra:" in text:
                try:
                    pedido_data["cod_orden_compra"] = text.split("Orden de Compra:")[1].split("\n")[0].strip()
                except:
                    pedido_data["cod_orden_compra"] = ""

            if "Total Neto:" in text:
                try:
                    neto = text.split("Total Neto:")[1].split("\n")[0].replace(".", "").replace(",", ".").strip()
                    pedido_data["total_neto_pedido"] = Decimal(neto)
                except:
                    pedido_data["total_neto_pedido"] = Decimal("0.0")

            if "IVA:" in text:
                try:
                    iva = text.split("IVA:")[1].split("\n")[0].replace("%", "").replace(",", ".").strip()
                    pedido_data["iva_pedido"] = Decimal(iva) / 100
                except:
                    pedido_data["iva_pedido"] = Decimal("0.19")

            if "Total:" in text:
                try:
                    total = text.split("Total:")[1].split("\n")[0].replace(".", "").replace(",", ".").strip()
                    pedido_data["total_pedido"] = Decimal(total)
                except:
                    pedido_data["total_pedido"] = Decimal("0.0")

            # -----------------------------
            # Extraer productos (igual que antes)
            # -----------------------------
            table = page.extract_table()
            if table:
                for row in table:
                    if not row or "Nombre" in row[0] or "Subtotal" in row[0]:
                        continue
                    try:
                        productos.append({
                            "nombre_producto": (row[0] or "").strip(),
                            "tipo_producto": (row[1] or "").strip(),
                            "tamano_producto": (row[2] or "").strip(),
                            "observacion_producto": (row[3] or "").strip(),
                            "cantidad_producto": int(row[4].replace(",", "")) if row[4] else 0,
                            "precio_unitario_producto": Decimal(row[5].replace(",", "")) if row[5] else Decimal("0.0")
                        })
                    except Exception as e:
                        print("Error procesando fila tabla:", row, e)
            else:  # Fallback texto corrido
                for line in text.splitlines():
                    if "Subtotal" in line or "Nombre" in line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            cantidad = int(parts[-2].replace(",", ""))
                            precio = Decimal(parts[-1].replace(",", ""))
                            nombre = " ".join(parts[:-2])
                            productos.append({
                                "nombre_producto": nombre,
                                "tipo_producto": "",
                                "tamano_producto": "",
                                "observacion_producto": "",
                                "cantidad_producto": cantidad,
                                "precio_unitario_producto": precio
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
