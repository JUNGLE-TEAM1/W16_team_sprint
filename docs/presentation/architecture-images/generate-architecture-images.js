const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const OUT_DIR = __dirname;
const W = 1920;
const H = 1080;

const palette = {
  bg: "#f7f9fb",
  ink: "#122033",
  muted: "#5c6878",
  navy: "#17324d",
  teal: "#0f766e",
  teal2: "#14a3a0",
  gold: "#c98a1a",
  blue: "#2563eb",
  red: "#b94141",
  green: "#2f855a",
  line: "#8ba0b5",
  card: "#ffffff",
  softNavy: "#e8eef5",
  softTeal: "#e5f5f3",
  softGold: "#fff3d8",
  softBlue: "#e9f0ff",
  softRed: "#fdecec",
  softGreen: "#eaf6ef",
};

const font = `"Apple SD Gothic Neo", "Noto Sans CJK KR", "Malgun Gothic", "Arial", sans-serif`;

function esc(text) {
  return String(text).replace(/[&<>"]/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
  }[ch]));
}

function wrapText(text, maxChars) {
  const normalized = String(text).replace(/\\n/g, "\n");
  if (normalized.includes("\n")) {
    return normalized.split("\n").flatMap((part) => wrapText(part, maxChars));
  }
  const words = normalized.split(/\s+/);
  const lines = [];
  let line = "";

  for (const word of words) {
    const next = line ? `${line} ${word}` : word;
    if ([...next].length <= maxChars) {
      line = next;
    } else {
      if (line) lines.push(line);
      if ([...word].length > maxChars) {
        let chunk = "";
        for (const ch of word) {
          if ([...chunk].length >= maxChars) {
            lines.push(chunk);
            chunk = "";
          }
          chunk += ch;
        }
        line = chunk;
      } else {
        line = word;
      }
    }
  }
  if (line) lines.push(line);
  return lines;
}

function textBlock(x, y, text, opts = {}) {
  const {
    size = 38,
    weight = 700,
    fill = palette.ink,
    width = 20,
    lineHeight = Math.round(size * 1.28),
    anchor = "middle",
    maxLines = 3,
  } = opts;
  const lines = wrapText(text, width).slice(0, maxLines);
  const tspans = lines.map((line, i) => {
    const dy = i === 0 ? 0 : lineHeight;
    return `<tspan x="${x}" dy="${dy}">${esc(line)}</tspan>`;
  }).join("");
  return `<text x="${x}" y="${y}" text-anchor="${anchor}" font-family='${font}' font-size="${size}" font-weight="${weight}" fill="${fill}">${tspans}</text>`;
}

function title(titleText, subtitle) {
  return [
    `<rect x="0" y="0" width="${W}" height="${H}" fill="${palette.bg}"/>`,
    `<circle cx="1640" cy="-120" r="360" fill="${palette.softTeal}" opacity="0.55"/>`,
    `<circle cx="250" cy="1060" r="340" fill="${palette.softGold}" opacity="0.55"/>`,
    textBlock(120, 92, titleText, { anchor: "start", size: 52, width: 38 }),
    textBlock(122, 142, subtitle, { anchor: "start", size: 25, weight: 500, fill: palette.muted, width: 72, maxLines: 2 }),
  ].join("\n");
}

function defs() {
  return `
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="160%">
      <feDropShadow dx="0" dy="12" stdDeviation="14" flood-color="#102030" flood-opacity="0.14"/>
    </filter>
    <marker id="arrow" viewBox="0 0 10 10" refX="8.8" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="${palette.line}"/>
    </marker>
    <marker id="arrowTeal" viewBox="0 0 10 10" refX="8.8" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="${palette.teal}"/>
    </marker>
  </defs>`;
}

function card(x, y, w, h, heading, body, opts = {}) {
  const {
    fill = palette.card,
    stroke = "#d9e2ec",
    accent = palette.teal,
    headingSize = 31,
    bodySize = 22,
    headingWidth = Math.max(14, Math.floor(w / 18)),
    bodyWidth = Math.max(14, Math.floor(w / 18)),
    radius = 22,
  } = opts;
  const cx = x + w / 2;
  const headingLines = wrapText(heading, headingWidth);
  const bodyLines = body ? wrapText(body, bodyWidth) : [];
  const headingY = body ? y + h / 2 - (bodyLines.length * bodySize * 0.36) - 5 : y + h / 2 + 10;
  const bodyY = headingY + headingLines.length * headingSize * 1.02 + 12;
  return `
    <g filter="url(#shadow)">
      <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${radius}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
      <rect x="${x}" y="${y}" width="12" height="${h}" rx="${radius}" fill="${accent}"/>
      ${textBlock(cx, headingY, heading, { size: headingSize, width: headingWidth, maxLines: 3 })}
      ${body ? textBlock(cx, bodyY, body, { size: bodySize, weight: 500, fill: palette.muted, width: bodyWidth, maxLines: 3 }) : ""}
    </g>`;
}

function pill(x, y, w, h, text, opts = {}) {
  const fill = opts.fill || palette.softTeal;
  const stroke = opts.stroke || palette.teal;
  return `
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${h / 2}" fill="${fill}" stroke="${stroke}" stroke-width="2"/>
    ${textBlock(x + w / 2, y + h / 2 + 10, text, { size: opts.size || 25, width: Math.floor(w / 24), maxLines: 1 })}
  `;
}

function line(x1, y1, x2, y2, opts = {}) {
  const color = opts.color || palette.line;
  const width = opts.width || 5;
  const marker = opts.marker || "arrow";
  const dash = opts.dash ? `stroke-dasharray="${opts.dash}"` : "";
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${width}" ${dash} stroke-linecap="round" marker-end="url(#${marker})"/>`;
}

function curve(d, opts = {}) {
  const color = opts.color || palette.line;
  const width = opts.width || 5;
  const marker = opts.marker || "arrow";
  const dash = opts.dash ? `stroke-dasharray="${opts.dash}"` : "";
  return `<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" ${dash} stroke-linecap="round" stroke-linejoin="round" marker-end="url(#${marker})"/>`;
}

function svg(body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
${defs()}
<style>
  text { paint-order: stroke; stroke: transparent; }
</style>
${body}
</svg>`;
}

const diagrams = [
  {
    file: "01-system-overview",
    render: () => svg(`
      ${title("전체 시스템 구조", "게시판 UI, 백엔드 API, 원문 DB, AI API, MCP 도구가 연결된 근거 기반 AI 게시판")}
      ${card(105, 390, 260, 170, "사용자", "질문 작성·검색·토론", { accent: palette.gold, fill: palette.softGold })}
      ${card(475, 315, 300, 320, "React / Vite", "게시판 UI\\n상세 화면\\n음성 토론", { accent: palette.teal, fill: palette.softTeal })}
      ${card(895, 315, 330, 320, "FastAPI Backend", "Auth / Posts\\nAgent / Search\\nRealtime", { accent: palette.navy, fill: palette.softNavy })}
      ${card(1345, 250, 330, 170, "PostgreSQL + pgvector", "원문·게시글·벡터 색인", { accent: palette.green, fill: palette.softGreen })}
      ${card(1345, 505, 330, 170, "OpenAI APIs", "요약·임베딩·Realtime", { accent: palette.blue, fill: palette.softBlue })}
      ${card(895, 735, 330, 150, "MCP Article Tool", "article_id로 원문 조회", { accent: palette.gold, fill: palette.softGold })}
      ${line(365, 475, 475, 475)}
      ${line(775, 475, 895, 475)}
      ${line(1225, 405, 1345, 335)}
      ${line(1225, 520, 1345, 590)}
      ${line(1060, 635, 1060, 735)}
      ${curve("M 1225 810 C 1410 810 1460 720 1510 675", { color: palette.gold })}
      ${pill(760, 195, 400, 62, "근거 기반 AI 게시판", { fill: "#ffffff", stroke: palette.gold, size: 27 })}
    `),
  },
  {
    file: "02-rag-agent-flow",
    render: () => svg(`
      ${title("RAG / Agent 게시글 생성 흐름", "질문이 원문 근거 기반 AI 답변으로 변환되는 핵심 흐름")}
      ${card(85, 430, 205, 145, "질문 작성", "제목 + 역사 질문", { accent: palette.gold, fill: palette.softGold, headingSize: 28 })}
      ${card(360, 390, 245, 225, "Query 분석", "filter / rewrite", { accent: palette.teal, fill: palette.softTeal, headingSize: 28 })}
      ${card(675, 390, 245, 225, "Hybrid Search", "vector + keyword", { accent: palette.green, fill: palette.softGreen, headingSize: 28 })}
      ${card(990, 390, 245, 225, "MCP 원문 조회", "article_id 기반", { accent: palette.gold, fill: palette.softGold, headingSize: 28 })}
      ${card(1305, 335, 245, 150, "LLM Rerank", "근거 후보 선별", { accent: palette.blue, fill: palette.softBlue, headingSize: 28 })}
      ${card(1305, 540, 245, 150, "Draft 생성", "요약·해석·태그", { accent: palette.blue, fill: palette.softBlue, headingSize: 28 })}
      ${card(1620, 430, 205, 145, "Post 저장", "근거·trace 포함", { accent: palette.navy, fill: palette.softNavy, headingSize: 28 })}
      ${line(290, 502, 360, 502)}
      ${line(605, 502, 675, 502)}
      ${line(920, 502, 990, 502)}
      ${line(1235, 465, 1305, 415)}
      ${line(1235, 540, 1305, 615)}
      ${line(1550, 415, 1620, 475)}
      ${line(1550, 615, 1620, 530)}
      ${pill(420, 700, 335, 58, "검색 후보 확보", { fill: "#ffffff", stroke: palette.green })}
      ${pill(955, 700, 385, 58, "원문 근거 검증", { fill: "#ffffff", stroke: palette.gold })}
      ${pill(1360, 745, 360, 58, "AI 결과와 근거 저장", { fill: "#ffffff", stroke: palette.blue })}
      ${curve("M 1715 575 C 1715 805 450 840 205 575", { dash: "12 12", color: "#b8c2cf", width: 4 })}
      ${textBlock(960, 905, "게시글 상세 화면에서 요약, 해석, 추천 태그, 근거 기사를 함께 보여줌", { size: 30, weight: 600, fill: palette.muted, width: 48 })}
    `),
  },
  {
    file: "03-data-model-erd",
    render: () => svg(`
      ${title("데이터 모델 / ERD", "원문 데이터, 검색 색인, 게시글, 토론 로그가 분리되어 저장됨")}
      ${card(125, 330, 260, 145, "users", "계정·비밀번호 해시", { accent: palette.navy, fill: palette.softNavy })}
      ${card(540, 285, 310, 235, "posts", "질문\\nAI 결과\\n근거 article_id", { accent: palette.gold, fill: palette.softGold })}
      ${card(1000, 260, 330, 170, "annals_articles", "조선왕조실록 원문 보존", { accent: palette.green, fill: palette.softGreen })}
      ${card(1000, 545, 330, 170, "annals_chunks", "검색용 chunk + vector", { accent: palette.teal, fill: palette.softTeal })}
      ${card(540, 630, 310, 145, "comments", "게시글 토론 댓글", { accent: palette.blue, fill: palette.softBlue })}
      ${card(1445, 330, 310, 145, "voice_sessions", "음성 토론 세션", { accent: palette.red, fill: palette.softRed })}
      ${card(1445, 630, 310, 145, "voice_messages", "전사·라우팅·근거", { accent: palette.red, fill: palette.softRed })}
      ${line(385, 395, 540, 395)}
      ${line(695, 520, 695, 630)}
      ${line(850, 395, 1000, 345)}
      ${line(1165, 430, 1165, 545, { color: palette.teal, marker: "arrowTeal" })}
      ${line(385, 430, 540, 690, { dash: "10 10", width: 4 })}
      ${line(850, 700, 1445, 700, { dash: "10 10", width: 4 })}
      ${line(1330, 395, 1445, 395)}
      ${line(1600, 475, 1600, 630)}
      ${pill(965, 790, 400, 62, "원문 보존 vs 검색 색인 분리", { fill: "#ffffff", stroke: palette.green })}
      ${pill(500, 825, 390, 62, "posts가 AI 결과와 근거 연결", { fill: "#ffffff", stroke: palette.gold })}
      ${pill(1395, 825, 390, 62, "음성 토론 로그 별도 저장", { fill: "#ffffff", stroke: palette.red })}
    `),
  },
  {
    file: "04-hybrid-search",
    render: () => svg(`
      ${title("Hybrid Search 구조", "embedding 검색과 키워드 검색을 결합해 실록 기사 후보를 찾음")}
      ${card(120, 445, 255, 155, "사용자 질문", "역사 질문 원문", { accent: palette.gold, fill: palette.softGold })}
      ${card(510, 405, 295, 235, "Query rewrite / filter", "왕·연도·주제\\n검색 표현 정리", { accent: palette.navy, fill: palette.softNavy, headingSize: 29 })}
      ${card(975, 265, 310, 170, "Vector Search", "pgvector + embedding", { accent: palette.teal, fill: palette.softTeal })}
      ${card(975, 615, 310, 170, "Keyword Search", "title / content / subject", { accent: palette.green, fill: palette.softGreen })}
      ${card(1405, 405, 275, 235, "Score Merge", "article_id별 점수 병합", { accent: palette.blue, fill: palette.softBlue })}
      ${card(740, 795, 430, 115, "Article 후보", "LLM rerank와 MCP 조회로 전달", { accent: palette.gold, fill: palette.softGold })}
      ${line(375, 522, 510, 522)}
      ${curve("M 805 485 C 895 390 910 350 975 350", { color: palette.teal, marker: "arrowTeal" })}
      ${curve("M 805 560 C 895 660 910 700 975 700", { color: palette.green, marker: "arrowTeal" })}
      ${curve("M 1285 350 C 1360 365 1380 415 1405 475", { color: palette.teal, marker: "arrowTeal" })}
      ${curve("M 1285 700 C 1360 685 1380 635 1405 570", { color: palette.green, marker: "arrowTeal" })}
      ${curve("M 1545 640 C 1505 805 1260 850 1170 850", { color: palette.blue })}
      ${pill(930, 500, 410, 62, "두 검색 경로를 함께 사용", { fill: "#ffffff", stroke: palette.teal })}
      ${textBlock(960, 950, "API 키나 chunk가 부족하면 keyword 중심으로 fallback 가능", { size: 30, weight: 600, fill: palette.muted, width: 48 })}
    `),
  },
  {
    file: "05-realtime-discussion",
    render: () => svg(`
      ${title("AI 토론 + Realtime 음성 토론", "게시글 생성 후에도 근거 기반 텍스트/음성 토론이 이어짐")}
      ${card(110, 390, 275, 260, "Post Detail", "질문\\nAI 답변\\n근거 기사", { accent: palette.gold, fill: palette.softGold })}
      ${card(510, 250, 315, 160, "Comments / Evidence", "댓글과 원문 맥락", { accent: palette.green, fill: palette.softGreen })}
      ${card(510, 610, 315, 160, "WebRTC", "브라우저 음성 연결", { accent: palette.teal, fill: palette.softTeal })}
      ${card(980, 250, 315, 160, "AI Discussion SSE", "텍스트 답변 스트리밍", { accent: palette.blue, fill: palette.softBlue })}
      ${card(980, 610, 315, 160, "OpenAI Realtime", "음성 응답 + transcript", { accent: palette.blue, fill: palette.softBlue })}
      ${card(1430, 335, 320, 180, "Backend route / retrieve", "현재근거·추가검색 판단", { accent: palette.navy, fill: palette.softNavy })}
      ${card(1430, 650, 320, 145, "voice_messages 저장", "전사·라우팅·근거 기록", { accent: palette.red, fill: palette.softRed })}
      ${line(385, 450, 510, 330)}
      ${line(825, 330, 980, 330)}
      ${line(385, 585, 510, 690)}
      ${line(825, 690, 980, 690)}
      ${line(1295, 330, 1430, 410)}
      ${line(1295, 690, 1430, 430)}
      ${line(1590, 515, 1590, 650)}
      ${curve("M 1430 480 C 1240 555 1040 515 825 410", { dash: "11 11", width: 4 })}
      ${pill(965, 470, 450, 62, "필요할 때만 추가 근거 검색", { fill: "#ffffff", stroke: palette.gold })}
      ${pill(125, 735, 365, 62, "텍스트 토론과 음성 토론을 분리", { fill: "#ffffff", stroke: palette.teal })}
      ${pill(1325, 845, 430, 62, "토론 과정도 DB에 남김", { fill: "#ffffff", stroke: palette.red })}
    `),
  },
];

async function writeDiagram(diagram) {
  const svgText = diagram.render();
  const svgPath = path.join(OUT_DIR, `${diagram.file}.svg`);
  const pngPath = path.join(OUT_DIR, `${diagram.file}.png`);
  fs.writeFileSync(svgPath, svgText, "utf8");
  await sharp(Buffer.from(svgText)).png().toFile(pngPath);
  const meta = await sharp(pngPath).metadata();
  if (meta.width !== W || meta.height !== H) {
    throw new Error(`${diagram.file}.png has unexpected size ${meta.width}x${meta.height}`);
  }
  return { svgPath, pngPath };
}

async function contactSheet() {
  const thumbs = [];
  for (const diagram of diagrams) {
    const input = path.join(OUT_DIR, `${diagram.file}.png`);
    const buffer = await sharp(input).resize(640, 360).png().toBuffer();
    thumbs.push({ input: buffer });
  }

  const sheetW = 1920;
  const sheetH = 1200;
  const labelSvg = [`<svg width="${sheetW}" height="${sheetH}" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f7f9fb"/>`];
  const positions = [
    [0, 0], [640, 0], [1280, 0],
    [320, 420], [960, 420],
  ];
  diagrams.forEach((diagram, i) => {
    const [x, y] = positions[i];
    labelSvg.push(`<text x="${x + 24}" y="${y + 392}" font-family='${font}' font-size="24" font-weight="700" fill="${palette.ink}">${esc(diagram.file)}</text>`);
  });
  labelSvg.push("</svg>");

  await sharp(Buffer.from(labelSvg.join("\n")))
    .composite(thumbs.map((thumb, i) => ({ input: thumb.input, left: positions[i][0], top: positions[i][1] })))
    .png()
    .toFile(path.join(OUT_DIR, "architecture-images-contact-sheet.png"));
}

(async () => {
  const written = [];
  for (const diagram of diagrams) {
    written.push(await writeDiagram(diagram));
  }
  await contactSheet();
  console.log(`Generated ${written.length} SVG/PNG diagram pairs in ${OUT_DIR}`);
})();
