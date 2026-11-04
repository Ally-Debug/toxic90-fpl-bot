import subprocess, os, json, shutil

def escape_pdf(text):
    text = str(text)
    replacements = {
        '▲': '^', '▼': 'v', '—': '-', '–': '-', '‘': "'", '’': "'",
        '“': '"', '”': '"', 'ø': 'o', 'Ø': 'O', 'ņ': 'n', 'ö': 'o',
        'ᴾ': 'P', 'ᴱ': 'E', 'ᴿ': 'R', '☢': '', '️': '', '🔥': '', '🏆': '',
        '⚔': '', '👑': ''
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    return "".join(c if 32 <= ord(c) <= 126 else '?' for c in text)

def make_table_pdf(pdf_path, title, headers, rows, col_widths, alignments, row_colors=None):
    total_w = sum(col_widths) + 40
    header_h = 32
    row_h = 24
    title_h = 42
    total_h = title_h + header_h + len(rows) * row_h + 30
    
    ops = []
    
    # White Background
    ops.append("1.0 1.0 1.0 rg")
    ops.append(f"0 0 {total_w} {total_h} re f")
    
    card_x = 20
    card_y = 15
    card_w = total_w - 40
    card_h = total_h - 30
    
    # Card outer border
    ops.append("0.88 0.90 0.94 RG")
    ops.append("1 w")
    ops.append(f"{card_x} {card_y} {card_w} {card_h} re s")
    
    # Title bar
    ops.append("0.98 0.98 0.99 rg")
    ops.append(f"{card_x} {card_y + card_h - title_h} {card_w} {title_h} re f")
    ops.append("0.88 0.90 0.94 RG")
    ops.append(f"{card_x} {card_y + card_h - title_h} m {card_x + card_w} {card_y + card_h - title_h} l S")
    
    # Title text
    ops.append("0.08 0.12 0.20 rg")
    safe_title = escape_pdf(title)
    ops.append(f"BT /F1 13 Tf {card_x + 14} {card_y + card_h - 26} Td ({safe_title}) Tj ET")
    
    # Header bar
    curr_y = card_y + card_h - title_h - header_h
    ops.append("0.95 0.96 0.98 rg")
    ops.append(f"{card_x} {curr_y} {card_w} {header_h} re f")
    ops.append("0.85 0.88 0.92 RG")
    ops.append(f"{card_x} {curr_y} m {card_x + card_w} {curr_y} l S")
    
    # Header text
    ops.append("0.25 0.30 0.38 rg")
    curr_x = card_x
    for i, h in enumerate(headers):
        w = col_widths[i]
        align = alignments[i]
        safe_h = escape_pdf(h)
        approx_w = len(safe_h) * 5.5
        if align == 'C':
            tx = curr_x + (w - approx_w) / 2
        elif align == 'R':
            tx = curr_x + w - approx_w - 8
        else:
            tx = curr_x + 10
        ops.append(f"BT /F1 9 Tf {tx:.1f} {curr_y + 11} Td ({safe_h}) Tj ET")
        curr_x += w
    
    # Data Rows
    for r_idx, row in enumerate(rows):
        curr_y -= row_h
        bg_rgb = row_colors[r_idx] if row_colors and r_idx < len(row_colors) else None
        if bg_rgb:
            ops.append(f"{bg_rgb[0]} {bg_rgb[1]} {bg_rgb[2]} rg")
            ops.append(f"{card_x + 1} {curr_y} {card_w - 2} {row_h} re f")
        elif r_idx % 2 == 1:
            ops.append("0.985 0.988 0.992 rg")
            ops.append(f"{card_x + 1} {curr_y} {card_w - 2} {row_h} re f")
            
        # Dividing line
        ops.append("0.92 0.94 0.96 RG")
        ops.append(f"{card_x} {curr_y} m {card_x + card_w} {curr_y} l S")
        
        # Cells
        curr_x = card_x
        for c_idx, val in enumerate(row):
            w = col_widths[c_idx]
            align = alignments[c_idx]
            safe_v = escape_pdf(val)
            approx_w = len(safe_v) * 5.2
            if align == 'C':
                tx = curr_x + (w - approx_w) / 2
            elif align == 'R':
                tx = curr_x + w - approx_w - 8
            else:
                tx = curr_x + 10
                
            # Text styling
            is_bold = (c_idx == 0 or (r_idx == 0 and row_colors and row_colors[0]))
            font = "/F1" if is_bold else "/F2"
            
            # Color
            if row_colors and row_colors[r_idx] and r_idx == 0:
                ops.append("0.55 0.40 0.05 rg") # Gold theme for leader
            else:
                ops.append("0.12 0.16 0.24 rg")
                
            ops.append(f"BT {font} 8.5 Tf {tx:.1f} {curr_y + 8} Td ({safe_v}) Tj ET")
            curr_x += w

    content_stream = "\n".join(ops)
    stream_bytes = content_stream.encode('latin1')
    
    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = []
    
    def add_obj(body):
        offsets.append(len(pdf))
        pdf.extend(f"{len(offsets)} 0 obj\n".encode())
        pdf.extend(body)
        pdf.extend(b"\nendobj\n")
        
    add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    add_obj(f"<< /Type /Pages /Kids [3 0 R] /Count 1 >>".encode())
    add_obj(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {total_w} {total_h}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>".encode())
    add_obj(f"<< /Length {len(stream_bytes)} >>\nstream\n".encode() + stream_bytes + b"\nendstream")
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets) + 1}\n0000000000 65535 f \n".encode())
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode())
    
    with open(pdf_path, "wb") as f:
        f.write(pdf)
        
    # Convert PDF to high-res PNG
    png_path = pdf_path.replace(".pdf", ".png")
    
    # 1. Try Linux pdftoppm (Standard in GitHub Actions)
    if shutil.which("pdftoppm"):
        cmd = ["pdftoppm", "-png", "-r", "160", "-singlefile", pdf_path, png_path.replace(".png", "")]
        subprocess.run(cmd, check=True)
    # 2. Try macOS sips or native tools
    elif shutil.which("sips"):
        cmd = ["sips", "-s", "format", "png", pdf_path, "--out", png_path]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    return png_path
