# inventory prompt:

기업용 판매재고관리시스템JK 프로그램 제작 프롬프트 v2.6, 
2025.10.26 주일 저녁 6시 30분 (제주도, Congratulations!)

1. 너는 기업용 판매재고관리 프로그램 전문가야. 
2.  국내와 국외무역을 하는 기업의 판매재고관리시스템을 만들고자 해. 
3.  파이썬 언어로 만들어줘. 
4.  데이터베이스로는 sqlite 3.0을 사용하되,
5.  판매재고관리 프로그램 안에서 sqlite가 작동되도록 해줘.  
6.  파이썬 실행 시에 자동으로 데이터베이스가 열리도록 하고 파이썬 종료시 자동으로 데이터베이스가 닫히도록 만들어줘.
7.  프로그램 UI와 메뉴가 선명하지 못해 보기가 불편하지 않도록, 전체 UI 메뉴가 깔끔하게 보이도록 sv 모듈을 이용해서 만들어줘.
8.  엑셀자료를 이용하여 상품등록과 거래처등록이 가능하도록 해주고, 상품과 거래처 검색도 가능하도록 한국어도 작동되게 만들어줘. 
9. 프로그램 사용을 위한 운영매뉴얼도 만들어줘.
10. 수량, 단가, 금액은 3자리마다 콤마(,)표시가 되도록 만들고, 최종적으로 한 개의 파이썬 파일로 만들어줘.

//


claude에서 판매재고관리시스템 프로그램을 단 한개의 파이썬 파일로 만들었고, sqlite내장형으로 db를 구성해서 파이썬 실행시 자동실행 자동종료되는 구조의 프로그램을 첨부파일처럼 만들었어. 이 프로그램을 github 레포지토리에 업로드 해 둔 상태야. 이것을 웹에서 vercel을 이용하여 실행하기 위한, vercel 업로드를 위한 html 파일 등의 필요한 파일들을 각각 만들어 주고, vercel에서 실행하기 위한 절차를 별도로 설명해줘. 

//

좋은 질문입니다! 📍
✅ 정답: 루트(Root) 폴더입니다!
Vercel은 저장소의 루트 디렉토리 전체를 연결합니다. 개별 파일이 아닙니다.

🎯 Vercel 배포 시 저장소 연결 방법
1단계: Vercel에서 저장소 선택
저장소 URL 형식:
https://github.com/사용자명/저장소명
예시:
https://github.com/jongki/inventory-system
➡️ 루트 URL을 연결하면 됩니다!

2단계: Vercel이 자동으로 찾는 것들
Vercel은 저장소를 연결하면 루트 폴더에서 다음을 자동으로 찾습니다:
📁 저장소 루트
├── 📄 vercel.json        ← Vercel 설정 파일
├── 📄 app.py             ← Python 진입점
├── 📄 requirements.txt   ← Python 패키지
└── 📁 templates
    └── 📄 index.html     ← Flask가 자동으로 찾음

📋 Vercel 배포 상세 절차
1️⃣ Vercel 로그인
• https://vercel.com 접속
• "Sign Up" 또는 "Login"
• "Continue with GitHub" 클릭
2️⃣ 새 프로젝트 생성
1. 대시보드에서 "Add New..." 버튼 클릭
2. "Project" 선택
3️⃣ 저장소 연결
화면에서 GitHub 저장소 목록이 보입니다:
Import Git Repository
┌─────────────────────────────────────┐
│ 🔍 Search...                        │
├─────────────────────────────────────┤
│ □ jongki/inventory-system           │  ← 이것 선택!
│   https://github.com/jongki/...     │
│                          [Import]    │
├─────────────────────────────────────┤
│ □ jongki/another-project            │
│                          [Import]    │
└─────────────────────────────────────┘
[Import] 버튼을 클릭하면 전체 저장소가 연결됩니다.
4️⃣ 프로젝트 설정 (중요!)
Configure Project
┌─────────────────────────────────────┐
│ Project Name                        │
│ ┌─────────────────────────────────┐ │
│ │ inventory-system                │ │
│ └─────────────────────────────────┘ │
│                                     │
│ Framework Preset                    │
│ ┌─────────────────────────────────┐ │
│ │ Other                      ▼    │ │  ← "Other" 선택
│ └─────────────────────────────────┘ │
│                                     │
│ Root Directory                      │
│ ┌─────────────────────────────────┐ │
│ │ ./                              │ │  ← 루트 그대로 ./
│ └─────────────────────────────────┘ │
│                                     │
│ Build Command (Optional)            │
│ ┌─────────────────────────────────┐ │
│ │                                 │ │  ← 비워둠
│ └─────────────────────────────────┘ │
│                                     │
│ Output Directory (Optional)         │
│ ┌─────────────────────────────────┐ │
│ │                                 │ │  ← 비워둠
│ └─────────────────────────────────┘ │
│                                     │
│ Install Command (Optional)          │
│ ┌─────────────────────────────────┐ │
│ │                                 │ │  ← 비워둠
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

           [Deploy] ← 이 버튼 클릭!
5️⃣ 배포 완료
• 자동으로 빌드 시작
• 1~2분 후 완료
• URL 제공: https://your-project.vercel.app

🔧 Root Directory 설정 핵심
✅ 올바른 설정
Root Directory: ./
• 저장소의 루트를 가리킴
• vercel.json, app.py가 루트에 있으면 이렇게 설정
❌ 잘못된 설정
Root Directory: templates/
• 이렇게 하면 안 됩니다!
• templates는 Flask가 내부적으로 찾는 폴더입니다

📂 저장소 구조 확인
배포 전에 GitHub에서 확인하세요:
github.com/사용자명/저장소명
├── app.py              ✅ 루트에 있어야 함
├── requirements.txt    ✅ 루트에 있어야 함
├── vercel.json        ✅ 루트에 있어야 함
├── templates/         ✅ 루트에 있어야 함
│   └── index.html
└── 판매재고관리시스템JK v2.1.py (기존 파일, 무시됨)
루트에 필수 파일 3개가 있는지 확인!
• ✅ app.py
• ✅ requirements.txt
• ✅ vercel.json

🎬 전체 흐름 요약
1. GitHub: 저장소 루트에 파일 4개 생성
o app.py
o requirements.txt
o vercel.json
o templates/index.html
2. Vercel: 저장소 URL 연결
o https://github.com/사용자명/저장소명 ← 이 주소!
3. 설정: Root Directory = ./ (기본값 유지)
4. 배포: Deploy 버튼 클릭
5. 완료: URL로 접속!

❓ 자주 하는 실수
실수 1: templates/index.html을 연결하려고 함
• ❌ 안 됩니다! 저장소 전체를 연결해야 합니다.
실수 2: 개별 파일 URL 복사
• ❌ https://github.com/.../blob/main/app.py (X)
• ✅ https://github.com/사용자명/저장소명 (O)
실수 3: Root Directory를 templates/로 설정
• Flask는 자동으로 templates/ 폴더를 찾습니다
• Root는 반드시 ./로 유지!

저장소 URL만 연결하면 Vercel이 알아서 다 찾아줍니다! 🚀
혹시 배포 중에 막히는 부분이 있으면 스크린샷과 함께 질문해주세요!
