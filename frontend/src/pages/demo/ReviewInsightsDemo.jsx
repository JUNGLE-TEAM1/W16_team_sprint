import { useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Clock,
  Database,
  FileText,
  Layers,
  MessageSquare,
  Search,
  Send,
  ShieldCheck,
  Sparkles,
  Star,
  TrendingDown,
  Users,
} from "lucide-react";

const questionText = `최근 6개월 동안 Cell Phones & Accessories 카테고리에서
평점이 급락한 상품군을 찾고,
구매 인증 리뷰에서 반복되는 주요 불만 원인을
대표 리뷰 근거와 함께 정리해줘.

상품 상세 설명과 충돌하는 부분도 찾아줘.`;

const riskProducts = [
  {
    id: "B0C-USB-C-2P",
    name: "USB-C Fast Charging Cable 2-Pack",
    before: 4.3,
    after: 3.1,
    lowBefore: 12,
    lowAfter: 31,
    reviews: "18,420",
    verified: "91%",
    issues: ["compatibility", "charging failure", "durability"],
    owner: "QA/MD",
  },
  {
    id: "B0C-MAG-CASE",
    name: "MagSafe Protective Case",
    before: 4.5,
    after: 3.6,
    lowBefore: 8,
    lowAfter: 24,
    reviews: "11,982",
    verified: "88%",
    issues: ["weak magnet", "yellowing", "fit"],
    owner: "셀러 운영",
  },
  {
    id: "B0C-20W-CHG",
    name: "20W Compact Wall Charger",
    before: 4.2,
    after: 3.4,
    lowBefore: 13,
    lowAfter: 28,
    reviews: "9,734",
    verified: "93%",
    issues: ["overheating", "noise", "slow charging"],
    owner: "QA",
  },
  {
    id: "B0C-CAR-MNT",
    name: "Vent Clip Car Phone Mount",
    before: 4.1,
    after: 3.2,
    lowBefore: 15,
    lowAfter: 33,
    reviews: "8,421",
    verified: "86%",
    issues: ["clip breakage", "vibration", "loose hinge"],
    owner: "MD",
  },
  {
    id: "B0C-BT-EARB",
    name: "Wireless Earbuds Charging Case",
    before: 4.4,
    after: 3.7,
    lowBefore: 10,
    lowAfter: 22,
    reviews: "7,318",
    verified: "90%",
    issues: ["battery drain", "pairing", "case heat"],
    owner: "CS",
  },
  {
    id: "B0C-SCRN-GLS",
    name: "Tempered Glass Screen Protector",
    before: 4.6,
    after: 3.9,
    lowBefore: 7,
    lowAfter: 20,
    reviews: "6,904",
    verified: "84%",
    issues: ["bubble", "edge lift", "size mismatch"],
    owner: "셀러 운영",
  },
  {
    id: "B0C-HUB-7IN1",
    name: "7-in-1 USB-C Travel Hub",
    before: 4.0,
    after: 3.3,
    lowBefore: 16,
    lowAfter: 30,
    reviews: "5,640",
    verified: "95%",
    issues: ["HDMI failure", "heat", "disconnect"],
    owner: "QA",
  },
  {
    id: "B0C-FAST-PAD",
    name: "Qi Fast Wireless Charging Pad",
    before: 4.2,
    after: 3.5,
    lowBefore: 11,
    lowAfter: 26,
    reviews: "4,982",
    verified: "89%",
    issues: ["charging stop", "LED", "case compatibility"],
    owner: "CS",
  },
  {
    id: "B0C-LENS-KIT",
    name: "Phone Camera Lens Kit",
    before: 4.1,
    after: 3.6,
    lowBefore: 14,
    lowAfter: 25,
    reviews: "3,812",
    verified: "82%",
    issues: ["blur", "clip fit", "scratches"],
    owner: "MD",
  },
  {
    id: "B0C-POW-10K",
    name: "10,000mAh Pocket Power Bank",
    before: 4.3,
    after: 3.8,
    lowBefore: 9,
    lowAfter: 21,
    reviews: "3,206",
    verified: "92%",
    issues: ["capacity", "slow recharge", "weight"],
    owner: "QA",
  },
];

const productDetails = {
  "B0C-USB-C-2P": {
    summary:
      "이 상품은 최근 6개월 동안 평균 평점이 4.3에서 3.1로 하락했습니다. 저평점 리뷰에서 compatibility와 charging failure가 반복적으로 관측됩니다.",
    aspects: [
      { name: "compatibility", share: 38, trend: "+19pp" },
      { name: "charging failure", share: 34, trend: "+17pp" },
      { name: "durability", share: 21, trend: "+8pp" },
    ],
    quotes: [
      {
        rating: 1,
        text: "iPhone 15에서 fast charging 표시가 뜨지 않고 일반 충전만 됩니다.",
        meta: "구매 인증 리뷰 · 2026-06-12",
      },
      {
        rating: 2,
        text: "2주 만에 케이블 연결부가 헐거워졌고 충전이 끊깁니다.",
        meta: "구매 인증 리뷰 · 2026-06-09",
      },
      {
        rating: 1,
        text: "상세 설명에는 모든 USB-C 기기 호환이라고 되어 있지만 제 태블릿에서는 인식되지 않습니다.",
        meta: "구매 인증 리뷰 · 2026-05-27",
      },
    ],
    conflict:
      '상품 설명의 "fast charging compatible" 및 "works with all USB-C devices" 문구와 구매 인증 리뷰의 고속 충전 실패, 특정 모델 미호환 경험이 충돌합니다.',
    actions: [
      "상세페이지의 호환 모델 문구를 iPhone 15 계열 기준으로 재검증",
      "공급사/셀러에 최근 생산 lot 샘플링 요청",
      "CS FAQ에 고속 충전 조건과 어댑터 조합 안내 추가",
      "고위험 상품 프로모션 일시 제한 검토",
    ],
  },
};

function RatingStars({ rating }) {
  return (
    <span className="inline-flex items-center gap-0.5 text-amber-500">
      {Array.from({ length: 5 }).map((_, index) => (
        <Star
          key={index}
          className={`h-3.5 w-3.5 ${index < rating ? "fill-current" : ""}`}
        />
      ))}
    </span>
  );
}

function EvidencePanel({ activeTab, setActiveTab }) {
  const tabs = [
    { id: "sql", label: "SQL", icon: Database },
    { id: "datasets", label: "사용 데이터셋", icon: Database },
    { id: "reviews", label: "대표 리뷰", icon: MessageSquare },
    { id: "freshness", label: "데이터 기준 시각", icon: Clock },
    { id: "lineage", label: "데이터 흐름", icon: Layers },
    { id: "policy", label: "권한 정책", icon: ShieldCheck },
  ];

  const content = {
    sql: (
      <pre className="max-w-full overflow-x-auto whitespace-pre-wrap rounded-lg bg-slate-950 p-3 text-xs leading-5 text-slate-100 sm:p-4">
{`WITH rating_window AS (
  SELECT product_id,
         baseline_rating,
         current_rating,
         low_rating_ratio,
         verified_review_ratio,
         review_count
  FROM gold_product_rating_period
  WHERE category = 'Cell Phones & Accessories'
    AND period = 'last_6_months'
)
SELECT p.product_name,
       r.baseline_rating,
       r.current_rating,
       r.low_rating_ratio,
       a.top_aspects,
       v.representative_review_ids
FROM rating_window r
JOIN gold_product_aspect_summary a USING (product_id)
JOIN representative_review_index v USING (product_id)
JOIN silver_amazon_products p USING (product_id)
WHERE r.baseline_rating - r.current_rating >= 0.7
ORDER BY baseline_rating - current_rating DESC
LIMIT 10;`}
      </pre>
    ),
    datasets: (
      <div className="grid gap-2 text-sm text-slate-700">
        {[
          ["gold_product_rating_period", "평점 하락폭, 현재 평균 평점, 저평점 비율"],
          ["gold_product_aspect_summary", "반복 불만 aspect와 언급 비중"],
          ["representative_review_index", "구매 인증 대표 리뷰 검색 인덱스"],
          ["silver_amazon_products", "상품명, 상세 설명, 카테고리 메타데이터"],
        ].map(([name, description]) => (
          <div
            key={name}
            className="rounded-lg border border-slate-200 bg-slate-50 p-3"
          >
            <p className="break-words font-semibold text-slate-950">{name}</p>
            <p className="mt-1 text-xs leading-5 text-slate-500">{description}</p>
          </div>
        ))}
      </div>
    ),
    lineage: (
      <div className="space-y-3 text-sm text-slate-700">
        {[
          "bronze.amazon_reviews_raw",
          "silver_amazon_products",
          "gold_product_rating_period",
          "gold_product_aspect_summary",
          "representative_review_index",
          "gold.product_rating_trend",
          "copilot.answer_trace",
        ].map((item, index) => (
          <div key={item} className="flex min-w-0 items-center gap-2">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-bold text-blue-700">
              {index + 1}
            </span>
            <span className="min-w-0 break-words">{item}</span>
          </div>
        ))}
      </div>
    ),
    reviews: (
      <div className="space-y-3 text-sm leading-6 text-slate-700">
        <p>
          대표 리뷰는 후보 상품으로 좁힌 뒤, 구매 인증 리뷰 중 aspect score가 높은
          문장만 검색합니다.
        </p>
        <p>
          원문 전체를 LLM에 던지지 않고, 수치 후보와 텍스트 근거를 분리해서
          답변합니다.
        </p>
      </div>
    ),
    freshness: (
      <div className="space-y-3 text-sm leading-6 text-slate-700">
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
          <p className="font-semibold text-emerald-900">
            데이터 기준 시각: 2026-06-22 10:38 KST
          </p>
          <p className="mt-1 text-xs text-emerald-700">
            리뷰 RAG 인덱스 v42 · 평점 배치 테이블 4분 전 갱신
          </p>
        </div>
        <p>
          평점 하락 후보는 Gold table 갱신 기준으로, 대표 리뷰는 최신 RAG
          인덱스 기준으로 조회합니다.
        </p>
      </div>
    ),
    policy: (
      <div className="space-y-3 text-sm leading-6 text-slate-700">
        <p>역할: 카테고리 품질/VOC 매니저</p>
        <p>조회 범위: Cell Phones & Accessories 한정</p>
        <p>제한 항목: 구매자 PII, 셀러 비공개 메모, 결제 필드</p>
      </div>
    ),
  };

  return (
    <div className="rounded-lg border border-slate-200 bg-white">
      <div className="border-b border-slate-100 p-4">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-950">근거 패널</h2>
        </div>
        <p className="mt-1 text-xs text-slate-500">
          사용 SQL, 데이터셋, lineage, 대표 리뷰, 권한 정책을 함께 보여줍니다.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-2 p-3 sm:grid-cols-3 xl:grid-cols-6">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex min-w-0 items-center justify-center gap-1.5 whitespace-normal rounded-md px-2 py-2 text-center text-xs font-semibold leading-4 ${
              activeTab === tab.id
                ? "bg-blue-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            <tab.icon className="h-3.5 w-3.5 shrink-0" />
            {tab.label}
          </button>
        ))}
      </div>
      <div className="p-4 pt-1">{content[activeTab]}</div>
    </div>
  );
}

function AnalysisAnswer({
  selectedProduct,
  selectedRank,
  details,
  riskProducts,
  selectedId,
  setSelectedId,
  evidenceTab,
  setEvidenceTab,
}) {
  return (
    <div className="mt-4 space-y-5">
      <section className="rounded-xl border border-blue-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex min-w-0 flex-1 items-start gap-3">
            <div className="shrink-0 rounded-lg bg-blue-600 p-2 text-white">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-base font-bold text-slate-950 sm:text-lg">
                  Copilot 답변 요약
                </h2>
                <span className="max-w-full whitespace-normal rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-bold leading-5 text-emerald-700">
                  분석 완료
                </span>
              </div>
              <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-700">
                SQL로 평점 하락 후보를 먼저 좁힌 결과, {selectedRank}순위 위험
                상품은 <strong>{selectedProduct.name}</strong>입니다. 구매 인증
                리뷰에서는 {selectedProduct.issues.join(", ")} 불만이 반복되고,
                상품 설명 문구와 실제 고객 경험 사이의 충돌 가능성이 확인됩니다.
              </p>
            </div>
          </div>
          <div className="max-w-full rounded-lg bg-blue-50 px-3 py-2 text-xs font-semibold leading-5 text-blue-700">
            데이터 기준 시각: 2026-06-22 10:38 KST
          </div>
        </div>

        <div className="mt-5 grid gap-3 md:grid-cols-4">
          <div className="min-w-0 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <p className="text-xs font-semibold text-slate-500">최우선 후보</p>
            <p className="mt-2 text-sm font-bold text-slate-950">
              {selectedProduct.name}
            </p>
          </div>
          <div className="min-w-0 rounded-lg border border-red-200 bg-red-50 p-4">
            <p className="text-xs font-semibold text-red-600">평점 하락</p>
            <p className="mt-2 text-lg font-bold text-red-700 sm:text-xl">
              {selectedProduct.before} → {selectedProduct.after}
            </p>
          </div>
          <div className="min-w-0 rounded-lg border border-amber-200 bg-amber-50 p-4">
            <p className="text-xs font-semibold text-amber-700">저평점 비율</p>
            <p className="mt-2 text-lg font-bold text-amber-800 sm:text-xl">
              {selectedProduct.lowBefore}% → {selectedProduct.lowAfter}%
            </p>
          </div>
          <div className="min-w-0 rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <p className="text-xs font-semibold text-emerald-700">권장 전달팀</p>
            <div className="mt-2 flex min-w-0 items-center gap-2 text-sm font-bold text-emerald-800">
              <Users className="h-4 w-4 shrink-0" />
              {selectedProduct.owner}
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 p-4">
          <div className="min-w-0">
            <h2 className="text-sm font-bold text-slate-950">
              위험 상품 상위 10개
            </h2>
            <p className="text-xs text-slate-500">
              최근 6개월 평점 급락, 저평점 비율, 구매 인증 리뷰 비율 기준
            </p>
          </div>
          <div className="flex max-w-full items-center gap-2 rounded-lg bg-blue-50 px-3 py-2 text-xs font-semibold leading-5 text-blue-700">
            <Search className="h-4 w-4 shrink-0" />
            Cell Phones & Accessories
          </div>
        </div>

        <div className="space-y-3 p-4 md:hidden">
          {riskProducts.map((product, index) => {
            const active = product.id === selectedId;
            return (
              <button
                key={product.id}
                onClick={() => setSelectedId(product.id)}
                className={`w-full rounded-xl border p-4 text-left ${
                  active
                    ? "border-blue-300 bg-blue-50"
                    : "border-slate-200 bg-white"
                }`}
              >
                <div className="flex min-w-0 flex-wrap items-center gap-2">
                  <p className="min-w-0 flex-1 text-sm font-bold text-slate-950">
                    {index + 1}. {product.name}
                  </p>
                  {active && (
                    <span className="max-w-full whitespace-normal rounded-full bg-blue-600 px-2 py-0.5 text-[11px] font-bold leading-5 text-white">
                      선택됨
                    </span>
                  )}
                </div>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {product.id} · 담당 {product.owner}
                </p>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div className="rounded-lg bg-red-50 p-2 text-red-700">
                    <p className="font-semibold">평점</p>
                    <p className="mt-1 font-bold">
                      {product.before} → {product.after}
                    </p>
                  </div>
                  <div className="rounded-lg bg-amber-50 p-2 text-amber-800">
                    <p className="font-semibold">저평점</p>
                    <p className="mt-1 font-bold">
                      {product.lowBefore}% → {product.lowAfter}%
                    </p>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-2 text-slate-700">
                    <p className="font-semibold">리뷰 수</p>
                    <p className="mt-1 font-bold">{product.reviews}</p>
                  </div>
                  <div className="rounded-lg bg-emerald-50 p-2 text-emerald-800">
                    <p className="font-semibold">구매 인증</p>
                    <p className="mt-1 font-bold">{product.verified}</p>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {product.issues.map((issue) => (
                    <span
                      key={issue}
                      className="max-w-full whitespace-normal rounded-full bg-slate-100 px-2 py-1 text-xs font-medium leading-5 text-slate-600"
                    >
                      {issue}
                    </span>
                  ))}
                </div>
              </button>
            );
          })}
        </div>

        <div className="hidden overflow-x-auto md:block">
          <table className="min-w-full divide-y divide-slate-100 text-sm">
            <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">상품</th>
                <th className="px-4 py-3">평점 하락</th>
                <th className="px-4 py-3">저평점 비율</th>
                <th className="px-4 py-3">리뷰 수</th>
                <th className="px-4 py-3">구매 인증</th>
                <th className="px-4 py-3">주요 불만</th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {riskProducts.map((product, index) => {
                const active = product.id === selectedId;
                return (
                  <tr
                    key={product.id}
                    className={active ? "bg-blue-50/70" : "hover:bg-slate-50"}
                  >
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setSelectedId(product.id)}
                        className="min-w-0 text-left"
                      >
                        <div className="flex min-w-0 flex-wrap items-center gap-2">
                          <p className="min-w-0 break-words font-semibold text-slate-950">
                            {index + 1}. {product.name}
                          </p>
                          {active && (
                            <span className="rounded-full bg-blue-600 px-2 py-0.5 text-[11px] font-bold text-white">
                              선택됨
                            </span>
                          )}
                        </div>
                        <p className="mt-1 break-words text-xs text-slate-500">
                          {product.id} · 담당 {product.owner}
                        </p>
                      </button>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2 font-semibold text-red-700">
                        <TrendingDown className="h-4 w-4 shrink-0" />
                        {product.before} → {product.after}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-700">
                      {product.lowBefore}% → {product.lowAfter}%
                    </td>
                    <td className="px-4 py-3 text-slate-700">{product.reviews}</td>
                    <td className="px-4 py-3 text-slate-700">{product.verified}</td>
                    <td className="px-4 py-3">
                      <div className="flex max-w-sm flex-wrap gap-1.5">
                        {product.issues.map((issue) => (
                          <span
                            key={issue}
                            className="max-w-full whitespace-normal rounded-full bg-slate-100 px-2 py-1 text-xs font-medium leading-5 text-slate-600"
                          >
                            {issue}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setSelectedId(product.id)}
                        className="rounded-md p-2 text-slate-400 hover:bg-white hover:text-blue-600"
                        title="상세 분석 보기"
                      >
                        <ChevronRight className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid grid-cols-12 gap-5">
        <div className="col-span-12 min-w-0 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5 lg:col-span-7">
          <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">
                선택 상품 분석
              </p>
              <h2 className="mt-1 text-lg font-bold text-slate-950">
                {selectedProduct.name}
              </h2>
            </div>
            <span className="max-w-full whitespace-normal rounded-full bg-red-100 px-3 py-1 text-xs font-bold leading-5 text-red-700">
              고위험
            </span>
          </div>
          <p className="text-sm leading-6 text-slate-700">{details.summary}</p>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {details.aspects.map((aspect) => (
              <div
                key={aspect.name}
                className="min-w-0 rounded-lg border border-slate-200 bg-slate-50 p-4"
              >
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {aspect.name}
                </p>
                <div className="mt-3 h-2 rounded-full bg-white">
                  <div
                    className="h-2 rounded-full bg-blue-600"
                    style={{ width: `${aspect.share}%` }}
                  />
                </div>
                <div className="mt-2 flex min-w-0 flex-wrap items-center justify-between gap-2 text-xs">
                  <span className="font-semibold text-slate-900">
                    {aspect.share}% 언급
                  </span>
                  <span className="text-red-600">{aspect.trend}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <aside className="col-span-12 min-w-0 space-y-5 lg:col-span-5">
          <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 sm:p-5">
            <div className="mb-3 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600" />
              <h2 className="text-sm font-bold text-amber-950">
                상품 설명과 충돌 지점
              </h2>
            </div>
            <p className="text-sm leading-6 text-amber-900">{details.conflict}</p>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5">
            <div className="mb-4 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />
              <h2 className="text-sm font-bold text-slate-950">추천 조치</h2>
            </div>
            <div className="space-y-3">
              {details.actions.map((action) => (
                <div key={action} className="flex items-start gap-3">
                  <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-emerald-500" />
                  <p className="text-sm leading-6 text-slate-700">{action}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>

      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
        <div className="mb-4 flex items-center gap-2">
          <MessageSquare className="h-5 w-5 shrink-0 text-blue-600" />
          <h2 className="text-sm font-bold text-slate-950">대표 리뷰 근거</h2>
        </div>
        <div className="grid gap-3 lg:grid-cols-3">
          {details.quotes.map((quote) => (
            <div
              key={quote.text}
              className="min-w-0 rounded-lg border border-slate-200 bg-slate-50 p-4"
            >
              <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
                <RatingStars rating={quote.rating} />
                <span className="text-xs text-slate-500">{quote.meta}</span>
              </div>
              <p className="text-sm leading-6 text-slate-700">"{quote.text}"</p>
            </div>
          ))}
        </div>
      </section>

      <EvidencePanel activeTab={evidenceTab} setActiveTab={setEvidenceTab} />
    </div>
  );
}

function FollowupAnswer({ type, selectedProduct }) {
  const answerMap = {
    followup_qa: {
      title: "QA팀 전달 요약",
      badge: "QA",
      intro: `앞선 분석 결과 기준으로 ${selectedProduct.name}은 QA팀에서 먼저 재현 여부를 확인해야 합니다.`,
      sections: [
        {
          title: "우선 확인 항목",
          items: [
            "iPhone 15 계열에서 고속 충전 실패가 재현되는지 확인",
            "최근 생산 lot의 케이블 연결부 내구성 샘플링",
            "USB-C 호환성 문구와 실제 지원 모델 불일치 검증",
          ],
        },
        {
          title: "우선순위",
          items: ["charging failure", "compatibility", "durability"],
        },
      ],
    },
    followup_cs: {
      title: "CS FAQ 초안",
      badge: "CS",
      intro: "고객 문의에 바로 활용할 수 있는 FAQ 문구 초안입니다.",
      sections: [
        {
          title: "고객 안내 문구",
          items: [
            "Q. iPhone 15에서 고속 충전이 되지 않아요.",
            "A. 사용 중인 어댑터 출력과 케이블 연결 상태를 먼저 확인해주세요. 문제가 지속되면 주문번호와 기기 모델명을 함께 전달해주세요.",
          ],
        },
        {
          title: "상담원 체크리스트",
          items: ["기기 모델명", "어댑터 출력", "구매 lot 또는 주문일", "충전 실패 재현 영상 여부"],
        },
      ],
    },
    followup_md: {
      title: "MD/셀러 운영 조치",
      badge: "MD",
      intro: "상세페이지와 프로모션 운영 관점에서 바로 실행할 조치입니다.",
      sections: [
        {
          title: "상세페이지 수정",
          items: [
            '"works with all USB-C devices" 문구를 지원 모델 기준으로 수정',
            '"fast charging compatible" 문구에 어댑터 조건 안내 추가',
          ],
        },
        {
          title: "운영 조치",
          items: [
            "QA 확인 전까지 해당 상품 프로모션 일시 제한",
            "셀러에게 최근 lot 품질 확인 요청",
          ],
        },
      ],
    },
    followup_general: {
      title: "후속 답변",
      badge: "Copilot",
      intro: "앞선 분석 결과를 기준으로 운영자가 바로 판단할 수 있게 정리했습니다.",
      sections: [
        {
          title: "핵심 요약",
          items: [
            `${selectedProduct.name}은 평점 하락과 저평점 비율 증가가 동시에 나타납니다.`,
            "호환성, 충전 실패, 내구성 불만이 반복되어 QA/MD/CS 동시 공유가 필요합니다.",
          ],
        },
      ],
    },
  };

  const answer = answerMap[type] || answerMap.followup_general;

  return (
    <div className="mt-4 min-w-0 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <h2 className="min-w-0 text-base font-bold text-slate-950">{answer.title}</h2>
        <span className="max-w-full whitespace-normal rounded-full bg-blue-100 px-2.5 py-1 text-xs font-bold leading-5 text-blue-700">
          {answer.badge}
        </span>
      </div>
      <p className="text-sm leading-6 text-slate-700">{answer.intro}</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {answer.sections.map((section) => (
          <div
            key={section.title}
            className="min-w-0 rounded-lg border border-slate-200 bg-slate-50 p-4"
          >
            <p className="text-sm font-bold text-slate-950">{section.title}</p>
            <div className="mt-3 space-y-2">
              {section.items.map((item) => (
                <div key={item} className="flex items-start gap-2">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500" />
                  <p className="text-sm leading-6 text-slate-700">{item}</p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function getFollowupType(rawQuestion) {
  const text = rawQuestion.toLowerCase();
  if (text.includes("qa") || text.includes("품질") || text.includes("샘플")) {
    return "followup_qa";
  }
  if (text.includes("cs") || text.includes("faq") || text.includes("고객") || text.includes("상담")) {
    return "followup_cs";
  }
  if (text.includes("md") || text.includes("프로모션") || text.includes("상세페이지") || text.includes("셀러")) {
    return "followup_md";
  }
  return "followup_general";
}

const thinkingStepsByType = {
  analysis: [
    "SQL로 평점 급락 후보를 찾는 중...",
    "구매 인증 리뷰에서 반복 불만을 검색하는 중...",
    "상품 설명과 리뷰 충돌 지점을 검토하는 중...",
  ],
  followup_qa: [
    "앞선 분석 결과를 QA 전달 항목으로 정리하는 중...",
    "재현 확인 항목과 샘플링 우선순위를 구성하는 중...",
  ],
  followup_cs: [
    "앞선 리뷰 근거를 고객 안내 문구로 바꾸는 중...",
    "상담원 체크리스트를 구성하는 중...",
  ],
  followup_md: [
    "상세페이지와 프로모션 조치 항목을 정리하는 중...",
    "셀러 운영 전달 문구를 구성하는 중...",
  ],
  followup_general: [
    "앞선 분석 맥락을 다시 확인하는 중...",
    "운영자가 바로 쓸 수 있는 답변으로 정리하는 중...",
  ],
};

export default function ReviewInsightsDemo() {
  const [question, setQuestion] = useState(questionText);
  const [selectedId, setSelectedId] = useState(riskProducts[0].id);
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("idle");
  const [thinkingStep, setThinkingStep] = useState("");
  const [evidenceTab, setEvidenceTab] = useState("sql");
  const chatEndRef = useRef(null);
  const timerRef = useRef([]);

  const selectedProduct = useMemo(
    () => riskProducts.find((product) => product.id === selectedId) || riskProducts[0],
    [selectedId],
  );

  const selectedRank = riskProducts.findIndex((product) => product.id === selectedId) + 1;

  const details = productDetails[selectedProduct.id] || {
    summary: `${selectedProduct.name}에서 ${selectedProduct.issues.join(
      ", ",
    )} 불만이 반복됩니다. 후보 상품 분석 결과를 기준으로 QA 검토가 필요합니다.`,
    aspects: selectedProduct.issues.map((issue, index) => ({
      name: issue,
      share: 30 - index * 5,
      trend: `+${12 - index * 2}pp`,
    })),
    quotes: [
      {
        rating: 2,
        text: `${selectedProduct.issues[0]} 문제가 반복되어 재구매하기 어렵다는 의견입니다.`,
        meta: "구매 인증 리뷰 · 2026-06-03",
      },
      {
        rating: 1,
        text: "상세 설명과 실제 사용 경험이 다르다는 리뷰가 확인됩니다.",
        meta: "구매 인증 리뷰 · 2026-05-26",
      },
    ],
    conflict:
      "상품 상세의 성능/호환성 문구와 구매 인증 리뷰에서 반복되는 불만 사이에 충돌 가능성이 있습니다.",
    actions: [
      "상세페이지 문구와 실제 고객 경험의 차이를 QA에 전달",
      "최근 입고 lot 샘플링 및 셀러 소명 요청",
      "CS 스크립트와 FAQ에 반복 불만 대응 문구 추가",
    ],
  };

  const hasMainAnalysis = messages.some((message) => message.type === "analysis");

  const clearTimers = () => {
    timerRef.current.forEach((timer) => clearTimeout(timer));
    timerRef.current = [];
  };

  useEffect(() => () => clearTimers(), []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, status, thinkingStep]);

  const submitQuestion = (rawQuestion = question) => {
    const trimmedQuestion = rawQuestion.trim();
    if (!trimmedQuestion || status === "thinking") return;

    clearTimers();
    const answerType = hasMainAnalysis ? getFollowupType(trimmedQuestion) : "analysis";
    const steps = thinkingStepsByType[answerType] || thinkingStepsByType.followup_general;
    const now = Date.now();

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: `user-${now}`,
        role: "user",
        content: trimmedQuestion,
      },
    ]);
    setQuestion("");
    setStatus("thinking");
    setThinkingStep(steps[0]);

    steps.slice(1).forEach((step, index) => {
      const timer = setTimeout(() => setThinkingStep(step), (index + 1) * 650);
      timerRef.current.push(timer);
    });

    const doneTimer = setTimeout(() => {
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          type: answerType,
        },
      ]);
      setStatus("answered");
      setThinkingStep("");
    }, steps.length * 650 + 350);

    timerRef.current.push(doneTimer);
  };

  const handleQuestionKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submitQuestion();
    }
  };

  const followupSuggestions = [
    "QA팀 전달용으로 요약해줘",
    "CS FAQ 문구를 만들어줘",
    "MD가 바로 할 조치를 정리해줘",
  ];

  return (
    <div className="text-responsive-safe min-h-screen w-full max-w-full overflow-x-hidden bg-slate-50 px-4 pt-4 pb-0 sm:px-6 sm:pt-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">
            시나리오 2 · Amazon Reviews
          </p>
          <h1 className="mt-1 text-xl font-bold text-slate-950 sm:text-2xl">
            고객 품질/VOC 인사이트
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            지민 매니저가 BI 대시보드에서 보이지 않는 “왜 나빠졌는지”를 리뷰
            근거와 상품 설명 충돌까지 함께 확인합니다.
          </p>
        </div>
        <Link
          to="/demo/realtime-alerts"
          className="inline-flex w-full items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 sm:w-auto"
        >
          실시간 알림으로 돌아가기
        </Link>
      </div>

      <section className="mx-auto w-full max-w-7xl space-y-5 pb-5">
        {messages.length === 0 && status === "idle" && (
          <div className="flex min-h-[62vh] items-center justify-center sm:min-h-[70vh]">
            <div className="w-full max-w-6xl">
              <div className="mb-7 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-100">
                  <Sparkles className="h-8 w-8" />
                </div>
                <h2 className="mt-5 text-2xl font-bold text-slate-950 sm:text-3xl">
                  무엇을 분석할까요?
                </h2>
                <p className="mx-auto mt-3 max-w-3xl text-sm leading-6 text-slate-500 sm:text-base sm:leading-7">
                  Amazon 리뷰 고객 인사이트 워크스페이스에 질문하면, Copilot이
                  SQL 후보 탐색과 리뷰 근거를 이어서 정리합니다.
                </p>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-2xl shadow-slate-200/70 focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100 sm:p-6">
                <textarea
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  onKeyDown={handleQuestionKeyDown}
                  className="h-48 w-full resize-none border-0 bg-transparent p-2 text-base leading-7 text-slate-800 outline-none placeholder:text-slate-400 sm:h-56 sm:p-3 sm:text-lg sm:leading-8 md:h-72"
                  placeholder="Amazon 리뷰 데이터에 대해 질문하세요."
                />
                <div className="flex flex-wrap items-stretch justify-between gap-3 border-t border-slate-100 px-2 pt-3 sm:items-center sm:px-3">
                  <div className="flex min-w-0 flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span className="max-w-full whitespace-normal rounded-full bg-slate-50 px-2.5 py-1 font-medium leading-5 text-slate-600">
                      Enter 실행
                    </span>
                    <span className="max-w-full whitespace-normal rounded-full bg-slate-50 px-2.5 py-1 font-medium leading-5 text-slate-600">
                      Shift + Enter 줄바꿈
                    </span>
                    <span className="max-w-full whitespace-normal rounded-full bg-blue-50 px-2.5 py-1 font-medium leading-5 text-blue-700">
                      Cell Phones & Accessories
                    </span>
                  </div>
                  <button
                    onClick={() => submitQuestion()}
                    className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
                    disabled={!question.trim()}
                  >
                    <Send className="h-4 w-4" />
                    질문하기
                  </button>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {[
                  "평점 급락 상품을 찾아줘",
                  "구매 인증 리뷰의 반복 불만을 요약해줘",
                  "상품 설명과 충돌하는 리뷰를 찾아줘",
                ].map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => setQuestion(suggestion)}
                    className="max-w-full whitespace-normal rounded-full border border-slate-200 bg-white px-3 py-2 text-left text-xs font-semibold leading-5 text-slate-600 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((message) =>
          message.role === "user" ? (
            <div key={message.id} className="flex justify-end">
              <div className="min-w-0 max-w-full rounded-2xl rounded-tr-md bg-blue-600 px-4 py-3 text-sm leading-6 text-white shadow-sm sm:max-w-3xl sm:px-5 sm:py-4">
                <p className="whitespace-pre-wrap break-words">{message.content}</p>
              </div>
            </div>
          ) : (
            <div key={message.id} className="flex min-w-0 items-start gap-2 sm:gap-3">
              <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-950 text-white">
                <Sparkles className="h-4 w-4" />
              </div>
              <div className="min-w-0 flex-1 rounded-2xl rounded-tl-md border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
                <p className="text-xs font-bold uppercase tracking-wide text-blue-600">
                  AskLake Copilot
                </p>
                {message.type === "analysis" ? (
                  <AnalysisAnswer
                    selectedProduct={selectedProduct}
                    selectedRank={selectedRank}
                    details={details}
                    riskProducts={riskProducts}
                    selectedId={selectedId}
                    setSelectedId={setSelectedId}
                    evidenceTab={evidenceTab}
                    setEvidenceTab={setEvidenceTab}
                  />
                ) : (
                  <FollowupAnswer type={message.type} selectedProduct={selectedProduct} />
                )}
              </div>
            </div>
          ),
        )}

        {status === "thinking" && (
          <div className="flex min-w-0 items-start gap-2 sm:gap-3">
            <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-slate-950 text-white">
              <Sparkles className="h-4 w-4 animate-pulse" />
            </div>
            <div className="min-w-0 rounded-2xl rounded-tl-md border border-slate-200 bg-white px-4 py-4 shadow-sm sm:px-5">
              <p className="text-xs font-bold uppercase tracking-wide text-blue-600">
                AskLake Copilot
              </p>
              <div className="mt-2 flex min-w-0 items-center gap-2 text-sm text-slate-700">
                <span className="h-2 w-2 shrink-0 animate-pulse rounded-full bg-blue-600" />
                {thinkingStep}
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </section>

      {(messages.length > 0 || status === "thinking") && (
      <section className="sticky bottom-0 -mx-4 border-t border-slate-200 bg-slate-50/95 px-4 py-4 backdrop-blur sm:-mx-6 sm:px-6">
        <div className="mx-auto max-w-6xl">
          {hasMainAnalysis && (
            <div className="mb-3 flex flex-wrap gap-2">
              {followupSuggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => submitQuestion(suggestion)}
                  disabled={status === "thinking"}
                  className="max-w-full whitespace-normal rounded-full border border-slate-200 bg-white px-3 py-1.5 text-left text-xs font-semibold leading-5 text-slate-600 hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}
          <div className="rounded-xl border border-slate-200 bg-white p-3 shadow-lg focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100">
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              onKeyDown={handleQuestionKeyDown}
              className="h-24 w-full resize-none border-0 bg-transparent p-2 text-sm leading-6 text-slate-800 outline-none placeholder:text-slate-400"
              placeholder={
                hasMainAnalysis
                  ? "분석 결과에 대해 후속 질문을 입력하세요."
                  : "Amazon 리뷰 고객 인사이트 워크스페이스에 질문하세요."
              }
              disabled={status === "thinking"}
            />
            <div className="flex flex-wrap items-stretch justify-between gap-3 border-t border-slate-100 px-2 pt-3 sm:items-center">
              <div className="flex min-w-0 flex-wrap items-center gap-2 text-xs text-slate-500">
                <span className="max-w-full whitespace-normal rounded-full bg-slate-50 px-2.5 py-1 font-medium leading-5 text-slate-600">
                  Enter 실행
                </span>
                <span className="max-w-full whitespace-normal rounded-full bg-slate-50 px-2.5 py-1 font-medium leading-5 text-slate-600">
                  Shift + Enter 줄바꿈
                </span>
                {hasMainAnalysis && (
                  <span className="max-w-full whitespace-normal rounded-full bg-blue-50 px-2.5 py-1 font-medium leading-5 text-blue-700">
                    이전 답변 맥락 유지
                  </span>
                )}
              </div>
              <button
                onClick={() => submitQuestion()}
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-300 sm:w-auto"
                disabled={!question.trim() || status === "thinking"}
              >
                <Send className="h-4 w-4" />
                {hasMainAnalysis ? "후속 질문" : "질문하기"}
              </button>
            </div>
          </div>
        </div>
      </section>
      )}
    </div>
  );
}
