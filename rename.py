import os
import codecs

dir_path = r'c:\KLTNN\KLTNN'
files_to_check = ['ai_engine.py', 'vquant_telegram.py', 'V Capital.mq5', 'HUONG_DAN_CAI_DAT_VCAPITAL.md', 'VCapital_Guide.html', 'VCapital_User_Guide_EN.md']

replacements = {
    'Tạ Việt Anh - DH12C2': 'Nguyễn Mạnh Cường_B22DCCN099',
    'Tạ Việt Anh': 'Nguyễn Mạnh Cường',
    'Việt Anh': 'Mạnh Cường',
    'William': 'Nguyễn Mạnh Cường',
    '@williamsug68': 'Nguyễn Mạnh Cường_B22DCCN099'
}

for filename in files_to_check:
    filepath = os.path.join(dir_path, filename)
    if not os.path.exists(filepath):
        continue
    
    enc = 'utf-8'
    if filename.endswith('.mq5'):
        enc = 'utf-16-le'
        
    try:
        with codecs.open(filepath, 'r', encoding=enc) as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        continue
        
    has_bom = False
    if content.startswith('\ufeff'):
        has_bom = True
        content = content[1:]
        
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with codecs.open(filepath, 'w', encoding=enc) as f:
        if has_bom:
            f.write('\ufeff')
        f.write(content)
    print(f"Processed {filename}")
