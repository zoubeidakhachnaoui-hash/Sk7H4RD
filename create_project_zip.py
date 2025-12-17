
#!/usr/bin/env python3
"""
Script to create a ZIP file of the project excluding Replit files
"""
import zipfile
import os
from datetime import datetime

def create_project_zip():
    # قائمة الملفات والمجلدات المستبعدة
    excluded_files = {
        '.replit',
        'replit.nix',
        '.upm',
        '.config',
        '.cache',
        '__pycache__',
        '.git',
        'venv',
        '.env'
    }
    
    # اسم ملف ZIP مع التاريخ والوقت
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'project_backup_{timestamp}.zip'
    
    print(f"🗜️  Creating ZIP file: {zip_filename}")
    print("=" * 50)
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        file_count = 0
        
        # المرور على جميع الملفات في المجلد الحالي
        for root, dirs, files in os.walk('.'):
            # إزالة المجلدات المستبعدة من البحث
            dirs[:] = [d for d in dirs if d not in excluded_files]
            
            for file in files:
                # تجاهل الملفات المستبعدة وملفات ZIP
                if file in excluded_files or file.endswith('.zip'):
                    continue
                
                file_path = os.path.join(root, file)
                # إزالة ./ من بداية المسار
                arcname = file_path[2:] if file_path.startswith('./') else file_path
                
                try:
                    zipf.write(file_path, arcname)
                    file_count += 1
                    print(f"✅ Added: {arcname}")
                except Exception as e:
                    print(f"❌ Error adding {arcname}: {e}")
        
        print("=" * 50)
        print(f"✅ ZIP file created successfully!")
        print(f"📦 Total files: {file_count}")
        print(f"📁 File name: {zip_filename}")
        print(f"📊 File size: {os.path.getsize(zip_filename) / 1024:.2f} KB")

if __name__ == '__main__':
    try:
        create_project_zip()
    except Exception as e:
        print(f"❌ Error creating ZIP: {e}")
