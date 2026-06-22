import { useMemo, useState } from "react";
import {
  ArrowDown,
  CheckCircle2,
  Clock,
  Database,
  PlayCircle,
  ShieldAlert,
  Sparkles,
  TrendingUp,
} from "lucide-react";

const alerts = [
  {
    id: "ALRT-240621-001",
    risk: "고위험",
    title: "가격 오입력 의심",
    productId: "PB-48291",
    productName: "PB USB-C Fast Charging Cable 2-Pack",
    baselinePrice: 49900,
    currentPrice: 4990,
    dropRate: -90,
    purchaseMultiple: 8.4,
    detectedAt: "2026-06-22 10:35 KST",
    freshness: "Gold table + 실시간 구간, 12초 전",
  },
  {
    id: "ALRT-240621-002",
    risk: "주의",
    title: "비정상 쿠폰 중복 적용",
    productId: "ACC-CASE-MAGSAFE-BLK",
    productName: "MagSafe Protective Case",
    baselinePrice: 31900,
    currentPrice: 21500,
    dropRate: -33,
    purchaseMultiple: 2.8,
    detectedAt: "2026-06-22 10:32 KST",
    freshness: "Gold table + 실시간 구간, 52초 전",
  },
];

const priceWindow = [
  { label: "10:31", price: 50100, orders: 22 },
  { label: "10:32", price: 49900, orders: 24 },
  { label: "10:33", price: 49800, orders: 23 },
  { label: "10:34", price: 4990, orders: 126 },
  { label: "10:35", price: 4990, orders: 185 },
];

const formatKRW = (value) =>
  new Intl.NumberFormat("ko-KR", {
    style: "currency",
    currency: "KRW",
    maximumFractionDigits: 0,
  }).format(value);

function MetricCard({ label, value, detail, tone = "slate", icon: Icon }) {
  const toneClasses = {
    red: "border-red-200 bg-red-50 text-red-800",
    blue: "border-blue-200 bg-blue-50 text-blue-800",
    green: "border-emerald-200 bg-emerald-50 text-emerald-800",
    amber: "border-amber-200 bg-amber-50 text-amber-800",
    slate: "border-slate-200 bg-white text-slate-800",
  };

  return (
    <div className={`min-w-0 rounded-lg border p-4 ${toneClasses[tone]}`}>
      <div className="flex min-w-0 items-center justify-between gap-3">
        <p className="min-w-0 text-xs font-semibold uppercase tracking-wide opacity-70">
          {label}
        </p>
        {Icon && <Icon className="h-4 w-4 shrink-0 opacity-70" />}
      </div>
      <p className="mt-3 whitespace-nowrap text-lg font-semibold tracking-normal tabular-nums 2xl:text-xl">
        {value}
      </p>
      <p className="mt-1 text-xs leading-5 opacity-75">{detail}</p>
    </div>
  );
}

function PriceWindowChart() {
  const maxOrders = Math.max(...priceWindow.map((point) => point.orders));
  const maxPrice = Math.max(...priceWindow.map((point) => point.price));

  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">
            최근 5분 실시간 구간
          </h3>
          <p className="text-xs text-slate-500">
            가격 급락과 구매량 급증을 같은 구간에서 비교합니다.
          </p>
        </div>
        <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
          실시간
        </span>
      </div>

      <div className="grid grid-cols-5 items-end gap-3">
        {priceWindow.map((point) => (
          <div key={point.label} className="space-y-2">
            <div className="flex h-40 items-end gap-1 rounded-md bg-slate-50 px-2 py-2">
              <div
                className="w-1/2 rounded-t bg-blue-500"
                style={{ height: `${Math.max(12, (point.price / maxPrice) * 100)}%` }}
                title={`가격 ${point.price}`}
              />
              <div
                className="w-1/2 rounded-t bg-red-400"
                style={{ height: `${Math.max(12, (point.orders / maxOrders) * 100)}%` }}
                title={`구매량 ${point.orders}`}
              />
            </div>
            <div className="text-center">
              <p className="text-xs font-medium text-slate-700">{point.label}</p>
              <p className="text-[11px] text-slate-500">{point.orders}건</p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-blue-500" />
          가격
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-red-400" />
          구매량
        </span>
      </div>
    </div>
  );
}

export default function RealtimeAlertsDemo() {
  const [selectedAlert, setSelectedAlert] = useState(alerts[0]);
  const [copilotMode, setCopilotMode] = useState(null);

  const lossEstimate = useMemo(() => {
    const gap = selectedAlert.baselinePrice - selectedAlert.currentPrice;
    return gap * 186;
  }, [selectedAlert]);

  const copilotCopy = {
    risk: {
      title: "왜 위험해?",
      body: [
        `최근 5분 최저 가격이 ${formatKRW(
          selectedAlert.currentPrice,
        )}로 관측되었습니다.`,
        `최근 30일 median 기준 가격 ${formatKRW(
          selectedAlert.baselinePrice,
        )} 대비 가격 하락률은 ${selectedAlert.dropRate}%입니다.`,
        `동시에 최근 5분 구매 이벤트가 기준선 대비 ${selectedAlert.purchaseMultiple}배 증가했습니다.`,
        "현재 프로모션 캘린더와 연결된 이벤트가 없어 프로모션 여부 확인이 필요한 가격 급락 이상징후입니다.",
        "가격 오입력 확정이 아니라, 운영자가 즉시 확인해야 할 고위험 알림으로 분류했습니다.",
      ],
    },
    sql: {
      title: "사용 SQL",
      body: [
        "live_price_window와 gold_product_price_baseline Gold table을 product_id 기준으로 비교했습니다.",
        "median_price, current_observed_price, price_drop_rate, orders_5m, baseline_orders_5m를 계산한 뒤 risk_score가 0.8 이상인 상품만 알림으로 올립니다.",
        "Copilot은 이 계산을 대신하지 않고 운영자가 볼 수 있게 설명합니다.",
      ],
    },
    lineage: {
      title: "관련 lineage",
      body: [
        "Kafka purchase_events와 price_observed_events가 Spark Streaming 실시간 구간으로 집계됩니다.",
        "최근 30일 중앙 가격 기준선은 gold_product_price_baseline에서 batch로 계산됩니다.",
        "알림 결과는 alert_price_risk_gold에 저장되고 Copilot answer_trace에 설명 근거가 남습니다.",
      ],
    },
    freshness: {
      title: "데이터 freshness",
      body: [
        selectedAlert.freshness,
        "Kafka 이벤트는 Spark Streaming으로 집계되고, 기준선은 과거 Gold table에서 batch로 계산됩니다.",
        "권한 정책상 지민 매니저는 모바일 액세서리 카테고리 알림만 조회합니다.",
      ],
    },
  };

  return (
    <div className="text-responsive-safe min-h-screen w-full max-w-full overflow-x-hidden bg-slate-50 px-4 py-4 sm:px-6 sm:py-6">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">
            시나리오 1 · MarketplaceCo
          </p>
          <h1 className="mt-1 text-xl font-bold text-slate-950 sm:text-2xl">
            실시간 가격 리스크 모니터
          </h1>
          <p className="mt-2 max-w-3xl text-sm text-slate-600">
            지민 매니저가 SQL을 직접 치기 전에, 시스템이 먼저 가격 오입력 의심
            alert를 띄우고 Copilot이 판단 근거를 설명합니다.
          </p>
        </div>
      </div>

      <div className="grid min-w-0 grid-cols-12 gap-5">
        <section className="col-span-12 xl:col-span-3">
          <div className="rounded-lg border border-slate-200 bg-white">
            <div className="border-b border-slate-100 px-4 py-3">
              <h2 className="text-sm font-semibold text-slate-900">
                실시간 알림
              </h2>
              <p className="text-xs text-slate-500">실시간 위험 알림 목록</p>
            </div>
            <div className="space-y-3 p-3">
              {alerts.map((alert) => {
                const active = selectedAlert.id === alert.id;
                const high = alert.risk === "고위험";
                return (
                  <button
                    key={alert.id}
                    onClick={() => {
                      setSelectedAlert(alert);
                    }}
                    className={`w-full rounded-lg border p-4 text-left transition ${
                      active
                        ? "border-blue-300 bg-blue-50"
                        : "border-slate-200 bg-white hover:border-slate-300"
                    }`}
                  >
                    <div className="mb-3 flex items-center justify-between gap-2">
                      <span
                        className={`rounded-full px-2.5 py-1 text-xs font-bold ${
                          high
                            ? "bg-red-100 text-red-700"
                            : "bg-amber-100 text-amber-700"
                        }`}
                      >
                        {alert.risk}
                      </span>
                      <span className="text-[11px] text-slate-500">{alert.id}</span>
                    </div>
                    <p className="font-semibold text-slate-950">{alert.title}</p>
                    <p className="mt-1 text-xs text-slate-500">{alert.productName}</p>
                    <div className="mt-4 grid grid-cols-1 gap-2 text-xs sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                      <div className="min-w-0 rounded-md bg-slate-50 p-2">
                        <p className="text-slate-500">현재 가격</p>
                        <p className="whitespace-nowrap font-semibold tabular-nums text-red-700">
                          {formatKRW(alert.currentPrice)}
                        </p>
                      </div>
                      <div className="min-w-0 rounded-md bg-slate-50 p-2">
                        <p className="text-slate-500">최근 5분 구매량</p>
                        <p className="whitespace-nowrap font-semibold tabular-nums text-slate-900">
                          {alert.purchaseMultiple}배
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        <section className="col-span-12 space-y-5 xl:col-span-6">
          <div className="rounded-lg border border-red-200 bg-white p-4 sm:p-5">
            <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="flex min-w-0 items-center gap-2">
                  <ShieldAlert className="h-5 w-5 shrink-0 text-red-600" />
                  <h2 className="min-w-0 text-base font-bold text-slate-950 sm:text-lg">
                    알림 상세 · {selectedAlert.title}
                  </h2>
                </div>
                <p className="mt-1 text-sm text-slate-500">
                  상품 ID {selectedAlert.productId}
                </p>
              </div>
              <div className="w-full rounded-lg bg-red-50 px-3 py-2 text-left sm:w-auto sm:text-right">
                <p className="text-xs font-semibold uppercase tracking-wide text-red-600">
                  예상 손실
                </p>
                <p className="whitespace-nowrap text-base font-bold tabular-nums text-red-700 sm:text-lg">
                  {formatKRW(lossEstimate)}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5">
              <MetricCard
                label="기준 가격"
                value={formatKRW(selectedAlert.baselinePrice)}
                detail="최근 30일 중앙 가격"
                tone="blue"
                icon={Database}
              />
              <MetricCard
                label="현재 가격"
                value={formatKRW(selectedAlert.currentPrice)}
                detail="최근 5분 현재 구간"
                tone="red"
                icon={ArrowDown}
              />
              <MetricCard
                label="가격 하락률"
                value={`${selectedAlert.dropRate}%`}
                detail="기준 가격 대비"
                tone="red"
                icon={ArrowDown}
              />
              <MetricCard
                label="최근 5분 구매량"
                value={`${selectedAlert.purchaseMultiple}배`}
                detail="평소 기준선 대비"
                tone="amber"
                icon={TrendingUp}
              />
              <MetricCard
                label="데이터 시각"
                value="10:35"
                detail={selectedAlert.detectedAt}
                tone="slate"
                icon={Clock}
              />
            </div>
          </div>

          <PriceWindowChart />

        </section>

        <aside className="col-span-12 xl:col-span-3">
          <div className="sticky top-24 rounded-lg border border-slate-200 bg-white">
            <div className="border-b border-slate-100 p-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-600" />
                <h2 className="text-sm font-bold text-slate-950">
                  Copilot 설명
                </h2>
              </div>
              <p className="mt-1 text-xs text-slate-500">
                계산된 지표를 운영자 언어로 설명합니다.
              </p>
            </div>
            <div className="space-y-3 p-4">
              <div className="grid grid-cols-4 gap-2">
                {[
                  ["risk", "왜 위험해?"],
                  ["sql", "SQL"],
                  ["lineage", "데이터 흐름"],
                  ["freshness", "데이터 기준 시각"],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    onClick={() => setCopilotMode(key)}
                    className={`rounded-md px-2 py-2 text-xs font-semibold ${
                      copilotMode === key
                        ? "bg-blue-600 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>

              {copilotMode ? (
                <div className="rounded-lg bg-slate-50 p-4">
                  <h3 className="font-semibold text-slate-950">
                    {copilotCopy[copilotMode].title}
                  </h3>
                  <div className="mt-3 space-y-3 text-sm leading-6 text-slate-700">
                    {copilotCopy[copilotMode].body.map((line) => (
                      <p key={line}>{line}</p>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4">
                  <h3 className="font-semibold text-slate-950">
                    Copilot 설명 대기
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    `왜 위험해?` 버튼을 누르면 기준 가격, 현재 가격, 구매 급증,
                    SQL, freshness 근거가 표시됩니다.
                  </p>
                </div>
              )}

              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" />
                  <p className="text-xs leading-5 text-emerald-800">
                    Copilot은 이상치를 직접 생성하지 않습니다. Spark Streaming과
                    Gold table의 수치 계산 결과, SQL, 기준선, 데이터 기준 시각,
                    데이터 흐름을
                    운영자 언어로 설명합니다.
                  </p>
                </div>
              </div>

              <button className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-3 text-sm font-semibold text-white hover:bg-slate-800">
                <PlayCircle className="h-4 w-4" />
                MD팀에 전달
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
