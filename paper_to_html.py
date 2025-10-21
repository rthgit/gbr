#!/usr/bin/env python3
"""
PAPER TO HTML CONVERTER
Converts the quantum gravity discovery paper to HTML format
"""

import re
import os
from datetime import datetime

def markdown_to_html(markdown_content):
    """Convert markdown content to HTML"""
    
    # Convert headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', markdown_content, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Convert bold text
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert italic text
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert inline code
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
    
    # Convert lists
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(\n<li>.*</li>\n)+', lambda m: f'<ul>{m.group(0)}</ul>', html)
    
    # Convert numbered lists
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Convert tables
    lines = html.split('\n')
    in_table = False
    table_html = []
    
    for line in lines:
        if '|' in line and line.strip():
            if not in_table:
                in_table = True
                table_html.append('<table class="table">')
            
            # Parse table row
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                if '---' in line:  # Header separator
                    continue
                else:
                    cell_tags = '<td>' + '</td><td>'.join(cells) + '</td>'
                    table_html.append(f'<tr>{cell_tags}</tr>')
        else:
            if in_table:
                in_table = False
                table_html.append('</table>')
            table_html.append(line)
    
    html = '\n'.join(table_html)
    
    # Convert paragraphs
    paragraphs = html.split('\n\n')
    html_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para and not para.startswith('<') and not para.startswith('#'):
            html_paragraphs.append(f'<p>{para}</p>')
        else:
            html_paragraphs.append(para)
    
    html = '\n\n'.join(html_paragraphs)
    
    return html

def create_html_paper():
    """Create complete HTML paper"""
    
    # Read the markdown paper
    with open('QUANTUM_GRAVITY_DISCOVERY_PAPER_COMPLETE.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convert to HTML
    html_content = markdown_to_html(markdown_content)
    
    # Create complete HTML document
    html_document = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quantum Gravity Effects in Gamma-Ray Bursts: Evidence for GRB-Specific Phenomena</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            color: #333333;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            text-align: center;
            font-size: 2.2em;
            margin-bottom: 30px;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 5px;
            margin-top: 30px;
            font-size: 1.5em;
        }}
        
        h3 {{
            color: #2c3e50;
            margin-top: 25px;
            font-size: 1.2em;
        }}
        
        h4 {{
            color: #34495e;
            margin-top: 20px;
            font-size: 1.1em;
        }}
        
        p {{
            text-align: justify;
            margin-bottom: 15px;
            text-indent: 0;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}
        
        em {{
            font-style: italic;
            color: #7f8c8d;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }}
        
        ul {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        
        .abstract {{
            background-color: #ecf0f1;
            padding: 20px;
            border-left: 5px solid #3498db;
            margin: 20px 0;
            font-style: italic;
        }}
        
        .keywords {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        
        .keywords strong {{
            color: #2c3e50;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 5px solid #ffc107;
            margin: 20px 0;
        }}
        
        .significance {{
            background-color: #d4edda;
            padding: 15px;
            border-left: 5px solid #28a745;
            margin: 20px 0;
        }}
        
        @media print {{
            body {{
                max-width: none;
                margin: 0;
                padding: 20px;
            }}
            
            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}
            
            table {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="abstract">
        {html_content.split('<h2>1. Introduction</h2>')[0]}
    </div>
    
    <div class="keywords">
        <strong>Keywords:</strong> Quantum Gravity, Gamma-Ray Bursts, Lorentz Invariance Violation, GRB090902B, GRB221009A
    </div>
    
    {html_content.split('<h2>1. Introduction</h2>')[1] if '<h2>1. Introduction</h2>' in html_content else html_content}
    
    <div class="footer">
        <p><strong>Quantum Gravity Effects in Gamma-Ray Bursts: Evidence for GRB-Specific Phenomena</strong></p>
        <p>Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
        <p>This paper represents the first evidence for quantum gravity effects in gamma-ray bursts.</p>
    </div>
</body>
</html>"""
    
    # Save HTML file
    with open('QUANTUM_GRAVITY_DISCOVERY_PAPER.html', 'w', encoding='utf-8') as f:
        f.write(html_document)
    
    print("✅ HTML paper created: QUANTUM_GRAVITY_DISCOVERY_PAPER.html")

def create_pdf_paper():
    """Create PDF paper using weasyprint or similar"""
    try:
        import weasyprint
        
        # Read HTML content
        with open('QUANTUM_GRAVITY_DISCOVERY_PAPER.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Convert to PDF
        weasyprint.HTML(string=html_content).write_pdf('QUANTUM_GRAVITY_DISCOVERY_PAPER.pdf')
        
        print("✅ PDF paper created: QUANTUM_GRAVITY_DISCOVERY_PAPER.pdf")
        
    except ImportError:
        print("⚠️  WeasyPrint not available. Creating PDF using alternative method...")
        create_pdf_alternative()

def create_pdf_alternative():
    """Create PDF using alternative method"""
    
    # Create a simple HTML to PDF conversion script
    pdf_script = '''
import subprocess
import sys

def create_pdf():
    try:
        # Try using wkhtmltopdf if available
        subprocess.run(['wkhtmltopdf', 'QUANTUM_GRAVITY_DISCOVERY_PAPER.html', 'QUANTUM_GRAVITY_DISCOVERY_PAPER.pdf'], 
                      check=True)
        print("✅ PDF created using wkhtmltopdf")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  wkhtmltopdf not available. Please install it or use browser print to PDF.")
        print("   Alternative: Open QUANTUM_GRAVITY_DISCOVERY_PAPER.html in browser and print to PDF")

if __name__ == "__main__":
    create_pdf()
'''
    
    with open('create_pdf.py', 'w') as f:
        f.write(pdf_script)
    
    print("📝 PDF creation script created: create_pdf.py")
    print("   Run: python create_pdf.py")

def main():
    """Main function"""
    print("🚀 Converting Quantum Gravity Discovery Paper to HTML and PDF...")
    
    # Create HTML version
    create_html_paper()
    
    # Create PDF version
    create_pdf_paper()
    
    print("\n🎉 Paper conversion complete!")
    print("📄 Files created:")
    print("   - QUANTUM_GRAVITY_DISCOVERY_PAPER.html")
    print("   - QUANTUM_GRAVITY_DISCOVERY_PAPER.pdf (if possible)")
    print("\n🌐 Open the HTML file in your browser to view the paper!")
    print("📖 Use browser 'Print to PDF' if PDF creation failed.")

if __name__ == "__main__":
    main()

