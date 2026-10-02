import os
import re

directories = [
    r"f:\spam_new\frontend\src\pages",
    r"f:\spam_new\frontend\src\components"
]

replacements = {
    # Typography
    r"text-slate-400": "text-[#94a3b8]",
    r"text-slate-500": "text-[#64748b]",
    r"text-slate-200": "text-white",
    r"text-slate-300": "text-[#94a3b8]",
    r"text-slate-600": "text-[#64748b]",
    
    # Backgrounds
    r"bg-slate-900/40": "bg-[#0d1424]",
    r"bg-slate-950/40": "bg-[#080c14]",
    r"bg-slate-900/50": "bg-[#0d1424]",
    r"bg-slate-900": "bg-[#0d1424]",
    r"bg-slate-950": "bg-[#080c14]",
    
    # Borders
    r"border-slate-800": "border-white/10",
    r"border-slate-900/60": "border-white/5",
    r"border-slate-900/20": "border-white/5",
    r"border-slate-900": "border-white/5",
    
    # Accents
    r"text-emerald-400": "text-[#00f5a0]",
    r"bg-emerald-500": "bg-[#00f5a0]",
    r"hover:bg-emerald-600": "hover:bg-[#00f5a0]/80",
    r"shadow-emerald-500/15": "emerald-glow",
    
    # Border Radii
    r"rounded-2xl": "rounded-xl",
}

def process_file(filepath):
    # skip DashboardPage, Sidebar, Navbar because we already rewrote them manually
    if "DashboardPage.tsx" in filepath or "Sidebar.tsx" in filepath or "Navbar.tsx" in filepath:
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for pattern, replacement in replacements.items():
        content = content.replace(pattern, replacement)
    
    # Specific fix for buttons that were solid emerald, they should have dark text
    content = content.replace("text-slate-950", "text-[#080c14]")
    
    # Inject font-mono into some headings
    content = content.replace('text-xs font-bold text-[#94a3b8] uppercase', 'text-[10px] font-bold text-[#64748b] uppercase font-mono')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for d in directories:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                process_file(os.path.join(root, file))

print("Theme update complete.")
