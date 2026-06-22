import { API_BASE_URL } from "../config/api";

const STORAGE_KEY = "xflow.demoApi.state.v1";

const now = () => new Date().toISOString();
const daysAgo = (days) =>
  new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

const makeId = (prefix) =>
  `${prefix}-${Math.random().toString(36).slice(2, 8)}-${Date.now()
    .toString(36)
    .slice(-4)}`;

const userSession = {
  user_id: "demo-user",
  email: "demo@xflow.local",
  name: "Demo User",
  is_admin: true,
  role_id: null,
  etl_access: true,
  domain_edit_access: true,
  dataset_access: [],
  all_datasets: true,
  role_dataset_etl_access: true,
  role_query_ai_access: true,
};

const orderColumns = [
  { name: "order_id", key: "order_id", type: "BIGINT", nullable: false },
  { name: "customer_id", key: "customer_id", type: "BIGINT", nullable: false },
  { name: "order_status", key: "order_status", type: "VARCHAR", nullable: false },
  { name: "order_total", key: "order_total", type: "DECIMAL", nullable: false },
  { name: "ordered_at", key: "ordered_at", type: "TIMESTAMP", nullable: false },
];

const paymentColumns = [
  { name: "payment_id", key: "payment_id", type: "BIGINT", nullable: false },
  { name: "order_id", key: "order_id", type: "BIGINT", nullable: false },
  { name: "method", key: "method", type: "VARCHAR", nullable: false },
  { name: "amount", key: "amount", type: "DECIMAL", nullable: false },
  { name: "paid_at", key: "paid_at", type: "TIMESTAMP", nullable: false },
];

const revenueColumns = [
  { name: "date", key: "date", type: "DATE", nullable: false },
  { name: "gross_revenue", key: "gross_revenue", type: "DECIMAL", nullable: false },
  { name: "paid_orders", key: "paid_orders", type: "INTEGER", nullable: false },
  { name: "avg_order_value", key: "avg_order_value", type: "DECIMAL", nullable: false },
];

const customerColumns = [
  { name: "customer_id", key: "customer_id", type: "BIGINT", nullable: false },
  { name: "segment", key: "segment", type: "VARCHAR", nullable: false },
  { name: "lifetime_value", key: "lifetime_value", type: "DECIMAL", nullable: false },
  { name: "last_seen_at", key: "last_seen_at", type: "TIMESTAMP", nullable: true },
];

const sourceNode = (id, label, platform, columns, position) => ({
  id,
  type: "custom",
  position,
  data: {
    label,
    name: label,
    platform,
    columns,
    nodeCategory: "source",
  },
});

const transformNode = (id, label, columns, position) => ({
  id,
  type: "custom",
  position,
  data: {
    label,
    name: label,
    platform: "Transform",
    columns,
    nodeCategory: "transform",
  },
});

const targetNode = (id, label, columns, position) => ({
  id,
  type: "custom",
  position,
  data: {
    label,
    name: label,
    platform: "S3",
    columns,
    nodeCategory: "target",
    isFinalTarget: true,
  },
});

const makeExecution = (dataset) => ({
  id: dataset.id,
  job_id: dataset.id,
  name: dataset.name,
  sources: [
    {
      nodeId: "source-orders",
      type: "postgres",
      schema: orderColumns,
      config: { tableName: "orders", platform: "PostgreSQL" },
    },
    {
      nodeId: "source-payments",
      type: "postgres",
      schema: paymentColumns,
      config: { tableName: "payments", platform: "PostgreSQL" },
    },
  ],
  transforms: [
    {
      nodeId: "transform-aggregate",
      type: "Aggregate",
      schema: dataset.columns || revenueColumns,
      config: { name: "daily revenue aggregate" },
      inputNodeIds: ["source-orders", "source-payments"],
    },
  ],
  targets: [
    {
      nodeId: "target-s3",
      type: "s3",
      schema: dataset.columns || revenueColumns,
      config: {
        s3Location: dataset.destination?.path || "s3://xflow-lakehouse/marts",
        path: dataset.destination?.path || "s3://xflow-lakehouse/marts",
      },
      inputNodeIds: ["transform-aggregate"],
    },
  ],
});

const seedState = () => {
  const datasets = [
    {
      id: "ds-revenue-mart",
      name: "mart_daily_revenue",
      description: "Daily revenue mart built from orders and payments.",
      owner: "Analytics",
      dataset_type: "target",
      job_type: "batch",
      status: "active",
      is_active: true,
      schedule: "0 9 * * *",
      schedule_frequency: "daily",
      format: "parquet",
      row_count: 128940,
      size_bytes: 384000000,
      tags: ["finance", "official", "daily"],
      sources: ["raw.orders", "raw.payments"],
      target: { path: "s3://xflow-lakehouse/marts/mart_daily_revenue" },
      destination: {
        type: "s3",
        path: "s3://xflow-lakehouse/marts/mart_daily_revenue",
        format: "parquet",
      },
      columns: revenueColumns,
      targets: [
        {
          type: "s3",
          config: {
            path: "s3://xflow-lakehouse/marts/mart_daily_revenue",
            format: "parquet",
          },
          schema: revenueColumns,
        },
      ],
      nodes: [
        sourceNode("source-orders", "raw.orders", "PostgreSQL", orderColumns, {
          x: 100,
          y: 120,
        }),
        sourceNode("source-payments", "raw.payments", "PostgreSQL", paymentColumns, {
          x: 100,
          y: 360,
        }),
        transformNode("transform-aggregate", "Aggregate Revenue", revenueColumns, {
          x: 460,
          y: 240,
        }),
        targetNode("target-s3", "mart_daily_revenue", revenueColumns, {
          x: 820,
          y: 240,
        }),
      ],
      edges: [
        {
          id: "edge-orders-aggregate",
          source: "source-orders",
          target: "transform-aggregate",
          animated: true,
        },
        {
          id: "edge-payments-aggregate",
          source: "source-payments",
          target: "transform-aggregate",
          animated: true,
        },
        {
          id: "edge-aggregate-target",
          source: "transform-aggregate",
          target: "target-s3",
          animated: true,
        },
      ],
      created_at: daysAgo(18),
      updated_at: daysAgo(1),
    },
    {
      id: "ds-customer360",
      name: "customer_360_snapshot",
      description: "Unified customer profile for support and growth teams.",
      owner: "Growth",
      dataset_type: "target",
      job_type: "streaming",
      status: "active",
      is_active: false,
      schedule: null,
      schedule_frequency: null,
      format: "parquet",
      row_count: 48210,
      size_bytes: 152000000,
      tags: ["customer", "streaming"],
      sources: ["raw.customers", "events.web_activity"],
      target: { path: "s3://xflow-lakehouse/marts/customer_360_snapshot" },
      destination: {
        type: "s3",
        path: "s3://xflow-lakehouse/marts/customer_360_snapshot",
        format: "parquet",
      },
      columns: customerColumns,
      targets: [
        {
          type: "s3",
          config: {
            path: "s3://xflow-lakehouse/marts/customer_360_snapshot",
            format: "parquet",
          },
          schema: customerColumns,
        },
      ],
      nodes: [
        sourceNode("source-customers", "raw.customers", "MongoDB", customerColumns, {
          x: 100,
          y: 220,
        }),
        transformNode("transform-score", "Enrich Segment", customerColumns, {
          x: 460,
          y: 220,
        }),
        targetNode("target-s3", "customer_360_snapshot", customerColumns, {
          x: 820,
          y: 220,
        }),
      ],
      edges: [
        {
          id: "edge-customers-score",
          source: "source-customers",
          target: "transform-score",
          animated: true,
        },
        {
          id: "edge-score-target",
          source: "transform-score",
          target: "target-s3",
          animated: true,
        },
      ],
      created_at: daysAgo(12),
      updated_at: daysAgo(2),
    },
  ];

  return {
    connections: [
      {
        id: "conn-postgres",
        name: "Orders PostgreSQL",
        description: "Transactional order database",
        type: "postgres",
        status: "connected",
        config: {
          host: "orders-db.internal",
          port: 5432,
          database_name: "commerce",
          user_name: "analytics",
        },
        created_at: daysAgo(35),
        updated_at: daysAgo(4),
      },
      {
        id: "conn-s3",
        name: "Lakehouse S3",
        description: "Curated analytics bucket",
        type: "s3",
        status: "connected",
        config: {
          bucket: "xflow-lakehouse",
          region: "ap-northeast-2",
          storageType: "s3",
        },
        created_at: daysAgo(30),
        updated_at: daysAgo(3),
      },
      {
        id: "conn-mongo",
        name: "Customer MongoDB",
        description: "Customer profile store",
        type: "mongodb",
        status: "connected",
        config: {
          uri: "mongodb://mongo:mongo@mongodb:27017",
          database: "customers",
        },
        created_at: daysAgo(26),
        updated_at: daysAgo(8),
      },
    ],
    sourceDatasets: [
      {
        id: "src-orders",
        name: "raw_orders_postgres",
        description: "Order table imported from PostgreSQL.",
        owner: "Data Eng",
        dataset_type: "source",
        job_type: "batch",
        status: "active",
        is_active: true,
        source_type: "postgres",
        tags: ["orders", "postgres"],
        columns: orderColumns,
        schema: orderColumns,
        sources: [
          {
            nodeId: "source-orders",
            type: "postgres",
            connection_id: "conn-postgres",
            table: "orders",
            schema: orderColumns,
          },
        ],
        updated_at: daysAgo(1),
        created_at: daysAgo(20),
      },
      {
        id: "src-payments",
        name: "raw_payments_postgres",
        description: "Payment facts from PostgreSQL.",
        owner: "Data Eng",
        dataset_type: "source",
        job_type: "batch",
        status: "active",
        is_active: true,
        source_type: "postgres",
        tags: ["payments", "postgres"],
        columns: paymentColumns,
        schema: paymentColumns,
        sources: [
          {
            nodeId: "source-payments",
            type: "postgres",
            connection_id: "conn-postgres",
            table: "payments",
            schema: paymentColumns,
          },
        ],
        updated_at: daysAgo(2),
        created_at: daysAgo(20),
      },
      {
        id: "src-customer-events",
        name: "events_customer_activity",
        description: "Clickstream and activity records from S3 logs.",
        owner: "Growth",
        dataset_type: "source",
        job_type: "streaming",
        status: "active",
        is_active: false,
        source_type: "s3",
        tags: ["events", "s3"],
        columns: [
          { name: "event_id", key: "event_id", type: "VARCHAR" },
          { name: "customer_id", key: "customer_id", type: "BIGINT" },
          { name: "event_name", key: "event_name", type: "VARCHAR" },
          { name: "event_at", key: "event_at", type: "TIMESTAMP" },
        ],
        schema: [
          { name: "event_id", key: "event_id", type: "VARCHAR" },
          { name: "customer_id", key: "customer_id", type: "BIGINT" },
          { name: "event_name", key: "event_name", type: "VARCHAR" },
          { name: "event_at", key: "event_at", type: "TIMESTAMP" },
        ],
        updated_at: daysAgo(3),
        created_at: daysAgo(14),
      },
    ],
    datasets,
    domains: [
      {
        id: "domain-finance",
        _id: "domain-finance",
        name: "Finance Data Products",
        description: "Revenue and settlement assets for reporting.",
        owner: "Analytics",
        type: "finance",
        tags: ["Official", "Finance"],
        job_ids: ["ds-revenue-mart"],
        nodes: datasets[0].nodes,
        edges: datasets[0].edges,
        created_at: daysAgo(8),
        updated_at: daysAgo(1),
      },
      {
        id: "domain-customer",
        _id: "domain-customer",
        name: "Customer Intelligence",
        description: "Customer and event assets for product teams.",
        owner: "Growth",
        type: "customer",
        tags: ["Internal", "Customer"],
        job_ids: ["ds-customer360"],
        nodes: datasets[1].nodes,
        edges: datasets[1].edges,
        created_at: daysAgo(6),
        updated_at: daysAgo(2),
      },
    ],
    users: [
      {
        id: "demo-user",
        email: "demo@xflow.local",
        name: "Demo User",
        is_admin: true,
        role_id: null,
        role_name: null,
        etl_access: true,
        domain_edit_access: true,
        dataset_access: [],
        all_datasets: true,
        created_at: daysAgo(10),
      },
      {
        id: "user-analyst",
        email: "analyst@xflow.local",
        name: "Analyst User",
        is_admin: false,
        role_id: "role-analyst",
        role_name: "Analyst",
        etl_access: false,
        domain_edit_access: false,
        dataset_access: ["ds-revenue-mart"],
        all_datasets: false,
        created_at: daysAgo(7),
      },
    ],
    roles: [
      {
        id: "role-admin",
        name: "Admin",
        description: "Full access to all demo surfaces.",
        dataset_etl_access: true,
        query_ai_access: true,
        dataset_access: [],
        all_datasets: true,
        created_at: daysAgo(10),
      },
      {
        id: "role-analyst",
        name: "Analyst",
        description: "Can browse catalog and run SQL.",
        dataset_etl_access: false,
        query_ai_access: true,
        dataset_access: ["ds-revenue-mart"],
        all_datasets: false,
        created_at: daysAgo(7),
      },
    ],
    runs: {
      "ds-revenue-mart": [
        {
          id: "run-revenue-1",
          dataset_id: "ds-revenue-mart",
          status: "success",
          started_at: daysAgo(1),
          finished_at: daysAgo(1),
          duration_seconds: 86,
          rows_processed: 128940,
          message: "Demo run completed",
        },
      ],
      "ds-customer360": [
        {
          id: "run-customer-1",
          dataset_id: "ds-customer360",
          status: "running",
          started_at: daysAgo(0.05),
          finished_at: null,
          duration_seconds: 312,
          rows_processed: 48210,
          message: "Demo stream active",
        },
      ],
    },
    layouts: {},
    streaming: {
      "ds-customer360": false,
    },
    quality: {
      "ds-revenue-mart": [
        {
          id: "quality-revenue-1",
          dataset_id: "ds-revenue-mart",
          job_name: "mart_daily_revenue",
          s3_path: "s3://xflow-lakehouse/marts/mart_daily_revenue",
          overall_score: 94,
          status: "healthy",
          run_at: daysAgo(1),
          checks: [
            { name: "Null check", status: "passed", score: 98 },
            { name: "Duplicate check", status: "passed", score: 93 },
          ],
        },
      ],
      "ds-customer360": [
        {
          id: "quality-customer-1",
          dataset_id: "ds-customer360",
          job_name: "customer_360_snapshot",
          s3_path: "s3://xflow-lakehouse/marts/customer_360_snapshot",
          overall_score: 82,
          status: "warning",
          run_at: daysAgo(2),
          checks: [
            { name: "Null check", status: "warning", score: 79 },
            { name: "Freshness", status: "passed", score: 88 },
          ],
        },
      ],
    },
  };
};

const readState = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch (error) {
    console.warn("[demo-api] Failed to read state, resetting.", error);
  }
  const state = seedState();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  return state;
};

const saveState = (state) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
};

const jsonResponse = (data, init = {}) =>
  new Response(data === undefined ? "" : JSON.stringify(data), {
    status: init.status || 200,
    statusText: init.statusText || "OK",
    headers:
      data === undefined
        ? init.headers || {}
        : { "Content-Type": "application/json", ...(init.headers || {}) },
  });

const blobResponse = (text, type = "text/plain") =>
  new Response(new Blob([text], { type }), { status: 200 });

const readJsonBody = async (request) => {
  try {
    return await request.clone().json();
  } catch {
    return {};
  }
};

const shouldMock = (url) => {
  const api = new URL(API_BASE_URL, window.location.origin);
  return (
    url.origin === api.origin ||
    (url.hostname === "localhost" && url.port === "8000") ||
    (url.hostname === "127.0.0.1" && url.port === "8000")
  );
};

const normalizePath = (url) => url.pathname.replace(/\/+$/, "") || "/";

const withDelay = (response) =>
  new Promise((resolve) => {
    window.setTimeout(() => resolve(response), 120);
  });

const getAllDatasets = (state) => [...state.datasets, ...state.sourceDatasets];
const getCatalogItems = (state) =>
  state.datasets.map((dataset) => ({
    ...dataset,
    size_bytes: dataset.size_bytes || 0,
    row_count: dataset.row_count || 0,
    format: dataset.format || dataset.destination?.format || "parquet",
  }));

const qualitySummary = (state) => {
  const results = Object.values(state.quality).flat().sort(
    (a, b) => new Date(b.run_at) - new Date(a.run_at),
  );
  const total = results.length;
  const avg =
    total === 0
      ? 0
      : Math.round(
          results.reduce((sum, item) => sum + (item.overall_score || 0), 0) /
            total,
        );
  return {
    summary: {
      total_count: total,
      healthy_count: results.filter((r) => (r.overall_score || 0) >= 90).length,
      warning_count: results.filter(
        (r) => (r.overall_score || 0) >= 70 && (r.overall_score || 0) < 90,
      ).length,
      critical_count: results.filter((r) => (r.overall_score || 0) < 70).length,
      avg_score: avg,
    },
    results,
  };
};

const queryRows = [
  {
    date: "2026-06-17",
    gross_revenue: 184200,
    paid_orders: 918,
    avg_order_value: 200.65,
  },
  {
    date: "2026-06-18",
    gross_revenue: 193810,
    paid_orders: 947,
    avg_order_value: 204.66,
  },
  {
    date: "2026-06-19",
    gross_revenue: 176540,
    paid_orders: 881,
    avg_order_value: 200.39,
  },
  {
    date: "2026-06-20",
    gross_revenue: 214900,
    paid_orders: 1022,
    avg_order_value: 210.27,
  },
];

const handleCollection = async ({ state, collection, request, path, idPrefix }) => {
  const method = request.method.toUpperCase();
  const parts = path.split("/").filter(Boolean);
  const id = parts[2];

  if (method === "GET" && !id) return jsonResponse(state[collection]);

  if (method === "GET" && id) {
    const item = state[collection].find((entry) => entry.id === id || entry._id === id);
    return item
      ? jsonResponse(item)
      : jsonResponse({ detail: "Not found" }, { status: 404 });
  }

  if (method === "POST") {
    const body = await readJsonBody(request);
    const item = {
      id: makeId(idPrefix),
      ...body,
      status: body.status || "active",
      created_at: now(),
      updated_at: now(),
    };
    state[collection].unshift(item);
    saveState(state);
    return jsonResponse(item, { status: 201 });
  }

  if ((method === "PUT" || method === "PATCH") && id) {
    const body = await readJsonBody(request);
    const index = state[collection].findIndex(
      (entry) => entry.id === id || entry._id === id,
    );
    if (index === -1) return jsonResponse({ detail: "Not found" }, { status: 404 });
    state[collection][index] = {
      ...state[collection][index],
      ...body,
      updated_at: now(),
    };
    saveState(state);
    return jsonResponse(state[collection][index]);
  }

  if (method === "DELETE" && id) {
    state[collection] = state[collection].filter(
      (entry) => entry.id !== id && entry._id !== id,
    );
    saveState(state);
    return jsonResponse(undefined, { status: 204 });
  }

  return null;
};

const handleRequest = async (request) => {
  const url = new URL(request.url);
  const path = normalizePath(url);
  const method = request.method.toUpperCase();
  const state = readState();

  if (method === "OPTIONS") return jsonResponse({});

  if (path === "/api/login" && method === "POST") {
    return jsonResponse({
      session_id: `demo-session-${Date.now()}`,
      user: userSession,
    });
  }

  if (path === "/api/me" && method === "GET") return jsonResponse(userSession);

  if (path === "/api/connections/test" && method === "POST") {
    return jsonResponse({
      success: true,
      message: "Demo connection test passed.",
    });
  }

  if (path.startsWith("/api/connections")) {
    const response = await handleCollection({
      state,
      collection: "connections",
      request,
      path,
      idPrefix: "conn",
    });
    if (response) return response;
  }

  if (path.match(/^\/api\/metadata\/[^/]+\/tables$/)) {
    return jsonResponse({
      source_id: path.split("/")[3],
      tables: ["orders", "payments", "customers", "products"],
    });
  }

  if (path.match(/^\/api\/metadata\/[^/]+\/tables\/[^/]+\/columns$/)) {
    const table = path.split("/").pop();
    const columns =
      table === "payments"
        ? paymentColumns
        : table === "customers"
          ? customerColumns
          : orderColumns;
    return jsonResponse(columns);
  }

  if (path.match(/^\/api\/metadata\/[^/]+\/collections$/)) {
    return jsonResponse({ collections: ["customers", "sessions", "events"] });
  }

  if (path.match(/^\/api\/metadata\/[^/]+\/collections\/[^/]+\/schema$/)) {
    return jsonResponse(customerColumns);
  }

  if (path === "/api/source-datasets/kafka/topics") {
    return jsonResponse(["commerce.orders", "commerce.payments", "web.events"]);
  }

  if (path === "/api/source-datasets/kafka/schema") {
    return jsonResponse([
      { name: "event_id", type: "string" },
      { name: "customer_id", type: "long" },
      { name: "event_at", type: "timestamp" },
    ]);
  }

  if (path.match(/^\/api\/source-datasets\/[^/]+\/preview$/)) {
    return jsonResponse({
      data: [
        { order_id: 1001, customer_id: 8801, order_total: 230.4 },
        { order_id: 1002, customer_id: 8802, order_total: 94.1 },
      ],
      columns: orderColumns,
      row_count: 2,
    });
  }

  if (path.startsWith("/api/source-datasets")) {
    const response = await handleCollection({
      state,
      collection: "sourceDatasets",
      request,
      path,
      idPrefix: "src",
    });
    if (response) return response;
  }

  if (path.match(/^\/api\/datasets\/[^/]+\/(activate|deactivate)$/) && method === "POST") {
    const [, , , id, action] = path.split("/");
    const dataset = state.datasets.find((item) => item.id === id);
    if (dataset) {
      dataset.is_active = action === "activate";
      dataset.updated_at = now();
      saveState(state);
      return jsonResponse(dataset);
    }
  }

  if (path.match(/^\/api\/datasets\/[^/]+\/run$/) && method === "POST") {
    const id = path.split("/")[3];
    const run = {
      id: makeId("run"),
      dataset_id: id,
      status: "running",
      started_at: now(),
      finished_at: null,
      duration_seconds: 0,
      rows_processed: 0,
      message: "Demo run started",
    };
    state.runs[id] = [run, ...(state.runs[id] || [])];
    saveState(state);
    return jsonResponse({ message: "Demo job started", run_id: run.id, run });
  }

  if (path.match(/^\/api\/datasets\/[^/]+\/nodes\/[^/]+\/metadata$/)) {
    return jsonResponse({ ok: true, updated_at: now() });
  }

  if (path.startsWith("/api/datasets")) {
    if (method === "POST") {
      const body = await readJsonBody(request);
      const item = {
        id: makeId("ds"),
        name: body.name || body.dataset_name || "new_target_dataset",
        description: body.description || "",
        owner: body.owner || "Demo User",
        dataset_type: "target",
        job_type: body.job_type || body.jobType || "batch",
        status: "active",
        is_active: false,
        tags: body.tags || [],
        columns: body.columns || body.schema || revenueColumns,
        sources: body.sources || ["raw.orders"],
        destination: body.destination || {
          type: "s3",
          path: `s3://xflow-lakehouse/marts/${body.name || "new_target_dataset"}`,
          format: "parquet",
        },
        target: body.target || {
          path: `s3://xflow-lakehouse/marts/${body.name || "new_target_dataset"}`,
        },
        nodes: body.nodes || seedState().datasets[0].nodes,
        edges: body.edges || seedState().datasets[0].edges,
        created_at: now(),
        updated_at: now(),
        ...body,
      };
      state.datasets.unshift(item);
      saveState(state);
      return jsonResponse(item, { status: 201 });
    }

    const response = await handleCollection({
      state,
      collection: "datasets",
      request,
      path,
      idPrefix: "ds",
    });
    if (response) return response;
  }

  if (path === "/api/catalog" && method === "GET") {
    return jsonResponse(getCatalogItems(state));
  }

  if (path === "/api/catalog" && method === "POST") {
    const body = await readJsonBody(request);
    const item = {
      id: makeId("cat"),
      dataset_type: "target",
      status: "active",
      is_active: false,
      columns: body.columns || revenueColumns,
      sources: body.sources || ["raw.orders"],
      destination: body.destination || {
        type: "s3",
        path: `s3://xflow-lakehouse/marts/${body.name || "catalog_dataset"}`,
      },
      created_at: now(),
      updated_at: now(),
      ...body,
    };
    state.datasets.unshift(item);
    saveState(state);
    return jsonResponse(item, { status: 201 });
  }

  if (path.match(/^\/api\/catalog\/[^/]+\/lineage$/)) {
    const id = path.split("/")[3];
    const dataset = state.datasets.find((item) => item.id === id);
    return jsonResponse({
      nodes: dataset?.nodes || [],
      edges: dataset?.edges || [],
    });
  }

  if (path.match(/^\/api\/catalog\/[^/]+\/layout$/)) {
    const id = path.split("/")[3];
    if (method === "PUT") {
      state.layouts[id] = await readJsonBody(request);
      saveState(state);
      return jsonResponse({ ok: true, layout: state.layouts[id] });
    }
    return jsonResponse(state.layouts[id] || {});
  }

  if (path.startsWith("/api/catalog/")) {
    const id = path.split("/")[3];
    const dataset = state.datasets.find((item) => item.id === id);
    if (!dataset) return jsonResponse({ detail: "Not found" }, { status: 404 });
    if (method === "PATCH" || method === "PUT") {
      Object.assign(dataset, await readJsonBody(request), { updated_at: now() });
      saveState(state);
    }
    if (method === "DELETE") {
      state.datasets = state.datasets.filter((item) => item.id !== id);
      saveState(state);
      return jsonResponse(undefined, { status: 204 });
    }
    return jsonResponse(dataset);
  }

  if (path === "/api/job-runs/bulk") {
    const ids = (url.searchParams.get("dataset_ids") || "").split(",").filter(Boolean);
    const grouped = {};
    ids.forEach((id) => {
      grouped[id] = state.runs[id] || [];
    });
    return jsonResponse(grouped);
  }

  if (path === "/api/job-runs") {
    const datasetId = url.searchParams.get("dataset_id");
    return jsonResponse(datasetId ? state.runs[datasetId] || [] : Object.values(state.runs).flat());
  }

  if (path.match(/^\/api\/streaming\/jobs\/[^/]+\/status$/)) {
    const id = path.split("/")[4];
    return jsonResponse({
      status: state.streaming[id] ? "running" : "stopped",
      group_id: state.streaming[id] ? `demo-stream-${id}` : null,
    });
  }

  if (path.match(/^\/api\/streaming\/jobs\/[^/]+\/(start|stop)$/)) {
    const [, , , , id, action] = path.split("/");
    state.streaming[id] = action === "start";
    saveState(state);
    return jsonResponse({
      status: state.streaming[id] ? "running" : "stopped",
      group_id: state.streaming[id] ? `demo-stream-${id}` : null,
    });
  }

  if (path.match(/^\/api\/cdc\/job\/[^/]+\/(activate|deactivate)$/)) {
    return jsonResponse({ ok: true, status: path.endsWith("activate") ? "active" : "paused" });
  }

  if (path.match(/^\/api\/cdc\/job\/[^/]+\/status$/)) {
    return jsonResponse({ status: "ready" });
  }

  if (path === "/api/domains/jobs") {
    return jsonResponse(state.datasets);
  }

  if (path.match(/^\/api\/domains\/jobs\/[^/]+\/execution$/)) {
    const id = path.split("/")[4];
    const dataset = state.datasets.find((item) => item.id === id) || state.datasets[0];
    return jsonResponse(makeExecution(dataset));
  }

  if (path.match(/^\/api\/domains\/[^/]+\/graph$/)) {
    const id = path.split("/")[3];
    const domain = state.domains.find((item) => item.id === id || item._id === id);
    if (method === "POST" && domain) {
      const body = await readJsonBody(request);
      domain.nodes = body.nodes || domain.nodes || [];
      domain.edges = body.edges || domain.edges || [];
      domain.updated_at = now();
      saveState(state);
    }
    return jsonResponse({
      nodes: domain?.nodes || [],
      edges: domain?.edges || [],
    });
  }

  if (path.match(/^\/api\/domains\/[^/]+\/files(\/[^/]+)?(\/download)?$/)) {
    if (path.endsWith("/download")) return blobResponse("Demo file content");
    if (method === "POST") {
      return jsonResponse({
        id: makeId("file"),
        name: "demo-attachment.txt",
        uploaded_at: now(),
      });
    }
    if (method === "DELETE") return jsonResponse({ ok: true });
  }

  if (path === "/api/domains" && method === "GET") {
    const search = (url.searchParams.get("search") || "").toLowerCase();
    const owner = (url.searchParams.get("owner") || "").toLowerCase();
    const tag = (url.searchParams.get("tag") || "").toLowerCase();
    const page = Number(url.searchParams.get("page") || "1");
    const limit = Number(url.searchParams.get("limit") || "10");
    let items = state.domains;
    if (search) {
      items = items.filter(
        (item) =>
          item.name.toLowerCase().includes(search) ||
          (item.description || "").toLowerCase().includes(search),
      );
    }
    if (owner) {
      items = items.filter((item) => (item.owner || "").toLowerCase().includes(owner));
    }
    if (tag) {
      items = items.filter((item) =>
        (item.tags || []).some((value) => value.toLowerCase().includes(tag)),
      );
    }
    const total = items.length;
    const start = (page - 1) * limit;
    return jsonResponse({
      items: items.slice(start, start + limit),
      total,
      total_pages: Math.max(1, Math.ceil(total / limit)),
      page,
    });
  }

  if (path === "/api/domains" && method === "POST") {
    const body = await readJsonBody(request);
    const item = {
      id: makeId("domain"),
      _id: makeId("domain"),
      nodes: [],
      edges: [],
      created_at: now(),
      updated_at: now(),
      ...body,
    };
    item._id = item.id;
    state.domains.unshift(item);
    saveState(state);
    return jsonResponse(item, { status: 201 });
  }

  if (path.startsWith("/api/domains/")) {
    const id = path.split("/")[3];
    const domain = state.domains.find((item) => item.id === id || item._id === id);
    if (!domain) return jsonResponse({ detail: "Not found" }, { status: 404 });
    if (method === "PUT" || method === "PATCH") {
      Object.assign(domain, await readJsonBody(request), { updated_at: now() });
      saveState(state);
    }
    if (method === "DELETE") {
      state.domains = state.domains.filter((item) => item.id !== id && item._id !== id);
      saveState(state);
      return jsonResponse(undefined, { status: 204 });
    }
    return jsonResponse(domain);
  }

  if (path === "/api/admin/users") {
    if (method === "GET") return jsonResponse(state.users);
    if (method === "POST") {
      const body = await readJsonBody(request);
      const item = {
        id: makeId("user"),
        role_name:
          state.roles.find((role) => role.id === body.role_id)?.name || null,
        created_at: now(),
        ...body,
      };
      delete item.password;
      state.users.unshift(item);
      saveState(state);
      return jsonResponse(item, { status: 201 });
    }
  }

  if (path.startsWith("/api/admin/users/")) {
    const id = path.split("/")[3];
    if (method === "DELETE") {
      state.users = state.users.filter((item) => item.id !== id);
      saveState(state);
      return jsonResponse(undefined, { status: 204 });
    }
    const body = await readJsonBody(request);
    const index = state.users.findIndex((item) => item.id === id);
    if (index >= 0) {
      delete body.password;
      state.users[index] = { ...state.users[index], ...body };
      saveState(state);
      return jsonResponse(state.users[index]);
    }
  }

  if (path === "/api/admin/roles") {
    if (method === "GET") return jsonResponse(state.roles);
    if (method === "POST") {
      const body = await readJsonBody(request);
      const item = { id: makeId("role"), created_at: now(), ...body };
      state.roles.unshift(item);
      saveState(state);
      return jsonResponse(item, { status: 201 });
    }
  }

  if (path.startsWith("/api/admin/roles/bulk-add-dataset")) {
    return jsonResponse({ ok: true });
  }

  if (path.startsWith("/api/admin/roles/")) {
    const id = path.split("/")[3];
    if (method === "DELETE") {
      state.roles = state.roles.filter((item) => item.id !== id);
      saveState(state);
      return jsonResponse(undefined, { status: 204 });
    }
    const index = state.roles.findIndex((item) => item.id === id);
    if (index >= 0) {
      state.roles[index] = { ...state.roles[index], ...(await readJsonBody(request)) };
      saveState(state);
      return jsonResponse(state.roles[index]);
    }
  }

  if (path === "/api/quality/dashboard/summary") {
    return jsonResponse(qualitySummary(state));
  }

  if (path.match(/^\/api\/quality\/[^/]+\/run$/)) {
    const id = path.split("/")[3];
    const dataset = state.datasets.find((item) => item.id === id);
    const result = {
      id: makeId("quality"),
      dataset_id: id,
      job_name: dataset?.name || id,
      s3_path: dataset?.destination?.path || "s3://xflow-lakehouse/demo",
      overall_score: 91,
      status: "healthy",
      run_at: now(),
      checks: [
        { name: "Null check", status: "passed", score: 96 },
        { name: "Duplicate check", status: "passed", score: 89 },
      ],
    };
    state.quality[id] = [result, ...(state.quality[id] || [])];
    saveState(state);
    return jsonResponse(result);
  }

  if (path.match(/^\/api\/quality\/[^/]+\/latest$/)) {
    const id = path.split("/")[3];
    return jsonResponse((state.quality[id] || [])[0] || null);
  }

  if (path.match(/^\/api\/quality\/[^/]+\/history$/)) {
    const id = path.split("/")[3];
    return jsonResponse(state.quality[id] || []);
  }

  if (path.startsWith("/api/trino/query") || path.startsWith("/api/duckdb/query")) {
    return jsonResponse({
      data: queryRows,
      row_count: queryRows.length,
      has_more: false,
      query_id: makeId("query"),
    });
  }

  if (path === "/api/trino/catalogs") return jsonResponse(["lakehouse", "memory"]);
  if (path.match(/^\/api\/trino\/catalogs\/[^/]+\/schemas$/)) {
    return jsonResponse(["default", "analytics", "raw"]);
  }
  if (path.match(/^\/api\/trino\/catalogs\/[^/]+\/schemas\/[^/]+\/tables$/)) {
    return jsonResponse(["mart_daily_revenue", "customer_360_snapshot", "raw_orders"]);
  }
  if (path.match(/^\/api\/trino\/catalogs\/[^/]+\/schemas\/[^/]+\/tables\/[^/]+\/schema$/)) {
    return jsonResponse(revenueColumns);
  }
  if (path.match(/^\/api\/trino\/catalogs\/[^/]+\/schemas\/[^/]+\/tables\/[^/]+\/preview$/)) {
    return jsonResponse({ data: queryRows, columns: Object.keys(queryRows[0]) });
  }

  if (path === "/api/duckdb/buckets") return jsonResponse(["xflow-lakehouse"]);
  if (path.match(/^\/api\/duckdb\/buckets\/[^/]+\/files$/)) {
    return jsonResponse([
      "marts/mart_daily_revenue/part-000.parquet",
      "marts/customer_360_snapshot/part-000.parquet",
    ]);
  }
  if (path === "/api/duckdb/schema") return jsonResponse(revenueColumns);

  if (path === "/api/ai/generate-sql") {
    return jsonResponse({
      sql: "SELECT date, gross_revenue, paid_orders FROM lakehouse.analytics.mart_daily_revenue ORDER BY date DESC LIMIT 30;",
      explanation: "Demo SQL generated locally.",
    });
  }
  if (path === "/api/ai/search-schema") {
    return jsonResponse({
      matches: getCatalogItems(state).map((item) => ({
        dataset_id: item.id,
        name: item.name,
        columns: item.columns,
      })),
    });
  }
  if (path === "/api/ai/health") return jsonResponse({ status: "ok" });

  if (path === "/api/sql/test") {
    const body = await readJsonBody(request);
    const schema = revenueColumns.map((column) => ({
      name: column.name,
      type: column.type,
      nullable: column.nullable !== false,
    }));
    const sourceSamples = (body.sources || []).map((source, index) => ({
      source_id: source.source_dataset_id,
      rows: [
        {
          order_id: 1001 + index,
          customer_id: 8801 + index,
          order_status: "paid",
          order_total: 230.4 + index * 12,
          ordered_at: "2026-06-20T10:15:00",
        },
        {
          order_id: 1002 + index,
          customer_id: 8802 + index,
          order_status: "paid",
          order_total: 94.1 + index * 8,
          ordered_at: "2026-06-20T11:40:00",
        },
      ],
    }));

    return jsonResponse({
      valid: true,
      success: true,
      sample_rows: queryRows,
      before_rows: sourceSamples[0]?.rows || queryRows,
      source_samples: sourceSamples,
      schema,
      data: queryRows,
      columns: Object.keys(queryRows[0]),
      sql: body.sql,
      message: "Demo SQL validated successfully.",
    });
  }

  if (path.startsWith("/api/opensearch/search")) {
    const query = (url.searchParams.get("q") || "").toLowerCase();
    const results = [
      ...state.domains.map((item) => ({
        doc_type: "domain",
        doc_id: item.id,
        name: item.name,
        description: item.description,
        tags: item.tags,
        status: "active",
      })),
      ...state.datasets.map((item) => ({
        doc_type: "etl_job",
        doc_id: item.id,
        dataset_type: item.dataset_type,
        name: item.name,
        description: item.description,
        tags: item.tags,
        status: item.status,
      })),
    ].filter((item) => !query || item.name.toLowerCase().includes(query));
    return jsonResponse({ results, total: results.length });
  }
  if (path.startsWith("/api/opensearch")) {
    return jsonResponse({ status: "ok", indexed: getAllDatasets(state).length });
  }

  if (
    path.startsWith("/api/logs") ||
    path.startsWith("/api/s3-logs") ||
    path.startsWith("/api/s3-csv") ||
    path.startsWith("/api/s3-json") ||
    path.startsWith("/api/s3-parquet")
  ) {
    return jsonResponse({
      success: true,
      message: "Demo preview generated.",
      columns: orderColumns,
      data: [
        { order_id: 1001, customer_id: 8801, order_total: 230.4 },
        { order_id: 1002, customer_id: 8802, order_total: 94.1 },
      ],
      regex: "^(?<ip>\\S+) (?<timestamp>\\[[^\\]]+\\]) (?<method>\\S+) (?<path>\\S+)$",
    });
  }

  if (path.startsWith("/api/rdb-transform/select-fields")) {
    return jsonResponse({
      id: makeId("transform"),
      status: "ok",
      output_schema: revenueColumns,
    });
  }

  return jsonResponse({ ok: true, message: "Demo API response" });
};

export function installDevApiMock() {
  if (!import.meta.env.DEV) return;

  window.__xflowDemoApiHandler = handleRequest;

  if (window.__xflowDemoApiInstalled) return;
  window.__xflowDemoApiInstalled = true;
  const originalFetch = window.fetch.bind(window);

  window.fetch = async (input, init) => {
    const request = input instanceof Request ? input : new Request(input, init);
    const url = new URL(request.url, window.location.origin);

    if (!shouldMock(url)) {
      return originalFetch(input, init);
    }

    try {
      return await withDelay(await window.__xflowDemoApiHandler(request));
    } catch (error) {
      console.error("[demo-api] Mock request failed", request.method, url.href, error);
      return jsonResponse(
        { detail: "Demo API error", message: error.message },
        { status: 500, statusText: "Demo API Error" },
      );
    }
  };

  window.xflowDemoApi = {
    reset() {
      localStorage.removeItem(STORAGE_KEY);
      return readState();
    },
    state: readState,
  };
}
