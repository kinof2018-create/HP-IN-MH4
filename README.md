# (주)삼화당피앤티 통합 대시보드 — 멀티파일(독립 대시보드) 구조

각 탭이 **독립된 대시보드 파일**로 분리되어 있습니다. `index.html` 은 이 파일들을
`<iframe src>` 로 불러오는 **런처(loader)** 이며, 탭끼리는 실행환경(스크립트·스타일·데이터)이
서로 완전히 격리되어 영향을 주지 않습니다.

## 파일 구성
```
index.html      ← 통합 런처 (상단 탭으로 5개 화면 전환 · 탭 드래그로 순서 변경)
facility.html   ← 시설관리 유지보수    (독립 실행 가능)   · ./data.xlsx 참조
hppk.html       ← HPPK 입출고·미수금   (독립 실행 가능)   · 엑셀 실시간 연동(클릭)
safety.html     ← 안전보건관리         (독립 실행 가능)   · GitHub SAFE/ 폴더 연동
express.html    ← 국제특송(UPS외)      (독립 실행 가능)   · 데이터 내장
esg.html        ← ESG 심층 보고서      (독립 실행 가능)   · GitHub ESG/ 폴더 연동
data.xlsx       ← 시설관리 데이터 원본 (기존 파일 그대로 유지)
SAFE/ , DOC/    ← 기존 증빙 폴더 (그대로 유지)
ESG/            ← ESG 증빙 폴더 뼈대 (E·S·G·공통)
```

## 두 가지 사용 방법
1. **통합 대시보드**: `index.html` 을 열면 5개 탭을 한 화면에서 전환하며 사용합니다(기존과 동일).
2. **개별 대시보드**: 각 파일(예: `hppk.html`)을 **단독 주소로 직접 열어** 그 탭만 독립적으로 사용/공유할 수 있습니다.
   예) `https://<계정>.github.io/<저장소>/hppk.html`

## GitHub 업로드 (GitHub Pages)
`index.html` 과 5개 탭 파일(`facility/hppk/safety/express/esg.html`)을 **같은 폴더(루트)** 에
올리면 됩니다. `data.xlsx` · `SAFE/` · `DOC/` · `ESG/` 도 같은 루트에 두어야 상대경로가 맞습니다.
(모든 파일이 루트 동일 폴더에 있으므로 각 탭의 `./data.xlsx` 등 상대경로가 그대로 동작합니다.)

## 향후 확장 (새 탭 추가)
1. 새 대시보드 파일 하나 추가 (예: `quality.html`)
2. `index.html` 의 `FILES` 에 한 줄 추가 → `quality: 'quality.html'`
3. `VIEWS` 배열과 상단 버튼·`<iframe>` 한 줄씩 추가

각 탭은 서로 격리되어 있어, 한 탭을 수정·교체·추가해도 다른 탭에 영향이 없습니다.
