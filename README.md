# 한샘 신이천대리점 인스타 캐러셀 양식

- `tools/make_carousel.py` : 캐러셀(4:5, 1080x1350) 생성기. 표지 → 공간별 사진 슬라이드 → MATERIAL GUIDE → 상담 안내 순서 고정.
- `sites/<현장>.json` : 현장별 제목·사진·자재 문구. 새 현장은 `sites/dusan.json`을 복사해서 수정.
- `python3 tools/make_carousel.py sites/<현장>.json` → `<현장>_slides/` 폴더에 01~NN.jpg 생성.
- 게시 규칙: 캡션 = 제목 → 컨셉 2줄 → 공간별 요약 → 블로그/DM 안내 → 매장 주소 → 해시태그. 게시 전 승인 필수.
- 기존 현장 사진 폴더: cheongu/, seongyeong/, dusan_slides/ (게시용), dusan/ (원본 크롭)
