content = open('gen_pdf.py', encoding='utf-8').read()
content = content.replace("p.set_font('Helvetdf', '', 10)", "p.set_font('Helvetica', '', 10)")
old = "        p.multi_cell(0, 6, f'  - {it}')\n"
new = "        p.multi_cell(0, 6, f'  - {it}'); p.set_x(15)\n"
content = content.replace(old, new)
open('gen_pdf.py', 'w', encoding='utf-8').write(content)
print('patched ok')
