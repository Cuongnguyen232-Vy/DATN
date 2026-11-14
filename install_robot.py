import os
import shutil
import glob

def find_mql5_folders():
    paths = []
    
    # 1. Check AppData (Standard Installation)
    appdata = os.getenv('APPDATA')
    if appdata:
        terminal_path = os.path.join(appdata, 'MetaQuotes', 'Terminal')
        if os.path.exists(terminal_path):
            # Look for 32-character hash folders
            for folder in os.listdir(terminal_path):
                if len(folder) == 32:
                    mql5_dir = os.path.join(terminal_path, folder, 'MQL5')
                    if os.path.exists(mql5_dir):
                        paths.append(mql5_dir)
                        
    # 2. Check Program Files (Portable Mode)
    program_files = os.getenv('ProgramFiles')
    if program_files:
        for pf_folder in os.listdir(program_files):
            if 'MetaTrader' in pf_folder:
                mql5_dir = os.path.join(program_files, pf_folder, 'MQL5')
                if os.path.exists(mql5_dir):
                    paths.append(mql5_dir)
                    
    return paths

def install_bot():
    print("BAT DAU CAI DAT ROBOT VAO METATRADER 5...\n")
    
    mql5_paths = find_mql5_folders()
    if not mql5_paths:
        print("[Loi] Khong tim thay thu muc cai dat MetaTrader 5!")
        print("Hay kiem tra lai xem ban da cai dat MT5 chua.")
        return
        
    source_mql5 = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mql5'))
    
    for dest_mql5 in mql5_paths:
        print(f"-> Dang cai dat vao: {dest_mql5}")
        
        # 1. Copy Include files
        src_include = os.path.join(source_mql5, 'Include', 'VQuant')
        dst_include = os.path.join(dest_mql5, 'Include', 'VQuant')
        
        if os.path.exists(src_include):
            if os.path.exists(dst_include):
                shutil.rmtree(dst_include)
            shutil.copytree(src_include, dst_include)
            print("  [OK] Da copy thu muc Include/VQuant")
            
        # 2. Copy Expert file (Main Bot)
        src_expert = os.path.join(source_mql5, 'V_Capital_OOP.mq5')
        dst_expert = os.path.join(dest_mql5, 'Experts', 'V Capital OOP.mq5') # Giu ten moi
        
        if os.path.exists(src_expert):
            shutil.copy2(src_expert, dst_expert)
            print("  [OK] Da copy file Experts/V Capital OOP.mq5")
            
    print("\n[CAI DAT HOAN TAT] Ban co the mo MetaEditor (F4 trong MT5) va an Compile (F7) de chay!")

if __name__ == "__main__":
    install_bot()
