import os
import sys
from datetime import datetime

def create_project(project_name):
    # 1. projects 폴더가 없으면 생성
    base_dir = "projects"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # 2. 전체 경로 설정 (예: projects/01_project)
    project_path = os.path.join(base_dir, project_name)

    if os.path.exists(project_path):
        print(f"❌ '{project_path}' 폴더가 이미 존재합니다.")
        return

    os.makedirs(project_path)
    
    # 3. 템플릿 설정
    log_template = f"# 📅 Project Log: {project_name}\n\n## 📝 데일리 기록\n\n### {datetime.now().strftime('%Y-%m-%d')} (Day 1)\n- **오늘의 목표:** \n- **진행 상황:** \n- **오늘의 도전 & 해결 (TIL):** \n- **내일의 할 일:** \n---\n"
    
    # 4. 파일 생성
    files = {
        "log.md": log_template,
        "main.py": "# 코드를 작성하세요\n",
        "README.md": f"# {project_name}\n\n프로젝트 설명을 적어주세요."
    }

    for filename, content in files.items():
        with open(os.path.join(project_path, filename), "w", encoding="utf-8") as f:
            f.write(content)

    print(f"✅ 프로젝트 생성 완료: {project_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python make_project.py [프로젝트명]")
    else:
        create_project(sys.argv[1])
