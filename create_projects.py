import os
import sys

def create_project(project_name):
    # 1. 폴더 생성
    if os.path.exists(project_name):
        print(f"❌ '{project_name}' 폴더가 이미 존재합니다.")
        return

    os.makedirs(project_name)
    
    # 2. log.md 템플릿 내용
    log_template = f"""# 📅 Project Log: {project_name}

## 📝 데일리 기록

### {import_date()} (Day 1)
- **오늘의 목표:** - **진행 상황:** - **오늘의 도전 & 해결 (TIL):** - **내일의 할 일:** ---
"""
    
    # 3. 파일 생성 (log.md, main.py, README.md)
    with open(os.path.join(project_name, "log.md"), "w", encoding="utf-8") as f:
        f.write(log_template)
    
    with open(os.path.join(project_name, "main.py"), "w", encoding="utf-8") as f:
        f.write("# 코드를 작성하세요\n")
        
    with open(os.path.join(project_name, "README.md"), "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n\n프로젝트 설명을 적어주세요.")

    print(f"✅ 프로젝트 '{project_name}' 생성 완료!")
    print(f"📂 구조: {project_name}/ (log.md, main.py, README.md)")

def import_date():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python make_project.py [프로젝트명]")
    else:
        create_project(sys.argv[1])
