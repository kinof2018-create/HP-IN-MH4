#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카톡 미리보기 자동 생성기
- share/미리보기문구.txt 를 읽어
  1) share/og-image.png (미리보기 이미지, 아래로 갈수록 페이드) 를 다시 만들고
  2) index.html 의 og:title / og:description 을 갱신합니다.
GitHub Actions 에서 Push 시 자동 실행됩니다.
"""
import os, re, glob, html, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TXT    = os.path.join(ROOT, "share", "미리보기문구.txt")
OUT    = os.path.join(ROOT, "share", "og-image.png")
INDEX  = os.path.join(ROOT, "index.html")
LOGO   = os.path.join(ROOT, "og", "logo-source.png")

CAT_COLOR = {"안전":"#D64545","총무":"#1B63D6","교육":"#2E9E5B","인사":"#8A5AD6","일반":"#5A5F6E"}

def find_font():
    cands = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    ]
    for p in cands:
        if os.path.exists(p): return p
    for pat in ["/usr/share/fonts/**/NotoSansCJK*Bold*.*",
                "/usr/share/fonts/**/NotoSansCJK*.*",
                "/usr/share/fonts/**/NanumGothic*.*",
                "/usr/share/fonts/**/*CJK*.*"]:
        g = glob.glob(pat, recursive=True)
        if g: return sorted(g)[0]
    raise RuntimeError("한글 폰트를 찾지 못했습니다 (fonts-noto-cjk 설치 필요)")

FONT = find_font()
def F(sz):
    try:    return ImageFont.truetype(FONT, sz, index=0)
    except: return ImageFont.truetype(FONT, sz)

def parse_txt():
    cat, title, body = "안전", "", []
    mode_body = False
    with open(TXT, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            s = line.strip()
            if s.startswith("#"): continue
            if not mode_body:
                m = re.match(r"^\s*(카테고리|분류)\s*[:：]\s*(.*)$", line)
                if m: cat = m.group(2).strip() or cat; continue
                m = re.match(r"^\s*(제목|title)\s*[:：]\s*(.*)$", line, re.I)
                if m: title = m.group(2).strip(); continue
                m = re.match(r"^\s*(내용|본문|content)\s*[:：]\s*(.*)$", line, re.I)
                if m:
                    mode_body = True
                    if m.group(2).strip(): body.append(m.group(2).strip())
                    continue
                if title and s: body.append(s)
            else:
                if s: body.append(s)
    if cat not in CAT_COLOR: cat = "일반"
    return cat, (title or "사내 공지"), body

def make_white_logo():
    im = Image.open(LOGO).convert("RGB")
    a = np.asarray(im).astype(np.int16); r,g,b = a[...,0],a[...,1],a[...,2]
    bright = np.maximum(np.maximum(r,g),b); minc = np.minimum(np.minimum(r,g),b); sat = bright-minc
    o = np.zeros((a.shape[0],a.shape[1],4), dtype=np.uint8); colored = sat>=45
    o[...,0]=np.where(colored,r,255); o[...,1]=np.where(colored,g,255); o[...,2]=np.where(colored,b,255)
    o[...,3]=np.where(colored,np.clip(sat*4,0,255),np.clip(255-bright,0,255)).astype(np.uint8)
    lg = Image.fromarray(o,"RGBA"); return lg.crop(lg.getbbox())

def draw_image(cat, title, body):
    SS=2; W,H=1200*SS,630*SS
    top=(10,23,88); bot=(20,40,160)
    def bgcol(y):
        t=y/H; return (int(top[0]+(bot[0]-top[0])*t),int(top[1]+(bot[1]-top[1])*t),int(top[2]+(bot[2]-top[2])*t))
    img=Image.new("RGB",(W,H),"#0A1758"); d=ImageDraw.Draw(img)
    for y in range(H): d.line([(0,y),(W,y)],fill=bgcol(y))
    d.ellipse([W-240*SS,-260*SS,W+220*SS,200*SS],fill=(38,69,176))
    logo=make_white_logo(); lh=104*SS; lw=int(logo.size[0]*lh/logo.size[1])
    L=logo.resize((lw,lh),Image.LANCZOS); img.paste(L,(80*SS,74*SS),L)
    d.rounded_rectangle([84*SS,198*SS,150*SS,214*SS],radius=8*SS,fill="#4ADE80")
    d.text((166*SS,182*SS),"클라우드 통합 대시보드 업데이트",font=F(48*SS),fill=(205,214,240))
    # ── 제목 + 본문 ──
    #  · 카테고리 칩 없음(요청)  · 긴 줄은 자동 줄바꿈(끝이 잘리지 않음)
    #  · 페이드 없음(하단 내용까지 모두 보임)  · 전체 텍스트 블록을 세로 중앙 배치
    LM = 84*SS                 # 좌측 여백
    MAXW = W - LM - 96*SS       # 우측 여백(우상단 원 장식을 피해 안전 폭 확보)
    def wrap_lines(text, font):
        out=[]
        for para in str(text or "").split("\n"):
            cur=""
            for w in para.split(" "):
                trial=(cur+" "+w).strip()
                if not cur or d.textlength(trial,font=font)<=MAXW:
                    if not cur or d.textlength(trial,font=font)<=MAXW:
                        cur=trial
                    else:
                        out.append(cur); cur=w
                else:
                    out.append(cur); cur=w
                # 한 단어(공백 없는 긴 문자열)가 폭을 넘으면 글자 단위로 분해
                if d.textlength(cur,font=font)>MAXW:
                    piece=""
                    for ch in cur:
                        if not piece or d.textlength(piece+ch,font=font)<=MAXW:
                            piece+=ch
                        else:
                            out.append(piece); piece=ch
                    cur=piece
            out.append(cur)
        return out
    # 내용이 길어도 카드(630) 안에 모두 들어오도록 줄바꿈 후 높이를 재어 폰트를 자동 축소
    top_area, bot_area = 248*SS, 606*SS
    avail = bot_area - top_area
    tsz, bsz = 44, 36
    tf=bf=None; tlines=blines=[]; tlh=blh=gap=0; total=0
    for _ in range(11):
        tf=F(tsz*SS); bf=F(bsz*SS)
        tlh=int(tsz*1.30*SS); blh=int(bsz*1.34*SS); gap=int(14*SS)
        tlines=wrap_lines(title, tf)
        blines=[]
        for ln in body[:8]: blines+=wrap_lines(ln, bf)
        total=len(tlines)*tlh + (gap if blines else 0) + len(blines)*blh
        if total<=avail or tsz<=22: break
        tsz-=2; bsz-=2
    y = top_area + max(0, (avail-total)//2)
    for ln in tlines:
        d.text((LM,y), ln, font=tf, fill="#FFFFFF"); y+=tlh
    if blines: y+=gap
    for ln in blines:
        d.text((LM,y), ln, font=bf, fill=(223,231,247)); y+=blh
    img=img.resize((1200,630),Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.4,percent=115,threshold=2))
    img.save(OUT,"PNG")

def update_index(title, body):
    # index.html 의 og 태그(제목/설명/이미지주소)는 사람이 직접 관리한다.
    #  → 자동생성은 '이미지(og-image.png)'만 다시 만들고, index.html 은 절대 건드리지 않는다.
    #  (그래야 자동 커밋과 사용자 Push 사이의 병합 충돌이 생기지 않고,
    #   카톡 제목을 없애려고 넣어둔 공백문자(og:title)가 지워지지 않는다.)
    return

if __name__ == "__main__":
    cat,title,body = parse_txt()
    draw_image(cat,title,body)
    update_index(title,body)   # no-op (index.html 미변경)
    print("OG 미리보기 생성 완료:", title)
