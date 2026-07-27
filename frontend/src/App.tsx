import {
  Activity,
  ArrowRight,
  BookOpen,
  Braces,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleAlert,
  Clock3,
  Contrast,
  Database,
  ExternalLink,
  Github,
  Grid2X2,
  Info,
  Layers3,
  List,
  LockKeyhole,
  MessageSquareText,
  Moon,
  Search,
  Server,
  ShieldCheck,
  Sparkles,
  Sun,
  X,
} from "lucide-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  FaApple,
  FaGithub,
  FaGoogle,
  FaKaggle,
  FaLinkedin,
  FaPhone,
} from "react-icons/fa";
import {
  type CSSProperties,
  type FormEvent,
  type ReactNode,
  useEffect,
  useRef,
  useState,
} from "react";
import { createPrediction, getHealth, type Prediction } from "./api";
import {
  architectureSteps,
  datasetMetrics,
  type Detail,
  signalInsights,
  smsExamples,
  trainingMetrics,
} from "./data";

type Section = "app" | "datasets" | "training";
type ThemeMode = "dark" | "light" | "contrast";

type SessionPrediction = Prediction & {
  id: string;
  createdAt: Date;
};

const navItems = [
  { id: "app" as const, path: "/app", label: "App", icon: MessageSquareText },
  { id: "datasets" as const, path: "/datasets", label: "Datasets", icon: Database },
  { id: "training" as const, path: "/training", label: "Training", icon: Activity },
];

const defaultDetails: Record<Section, Detail> = {
  datasets: {
    eyebrow: "Dataset snapshot",
    title: "SMS Spam Collection",
    value: "5,572",
    summary:
      "A compact public corpus of labeled English SMS messages used for exploration and model training.",
    facts: ["86.6% ham · 13.4% spam", "Stratified 80/20 training split", "Source: UCI / Kaggle collection"],
    tone: "violet",
  },
  training: {
    eyebrow: "Champion architecture",
    title: "Bidirectional LSTM",
    value: "98.8%",
    summary:
      "A lean sequence model selected through a 30-trial Optuna study and exported for ONNX inference.",
    facts: ["143,601 trainable parameters", "8,439-token vocabulary", "Notebook-reported validation accuracy"],
    tone: "cyan",
  },
  app: {
    eyebrow: "Live workspace",
    title: "Prediction console",
    summary:
      "Send an SMS to the production classifier. The response is immediate once the free service is awake.",
    facts: ["POST /predict", "50% spam threshold", "Message persisted as Fernet ciphertext"],
    tone: "mint",
  },
};

const globalSearchItems = [
  ...datasetMetrics.map((item) => ({ ...item, section: "datasets" as const })),
  ...signalInsights.map((item) => ({ ...item, section: "datasets" as const })),
  ...trainingMetrics.map((item) => ({ ...item, section: "training" as const })),
  ...architectureSteps.map((item) => ({ ...item, section: "training" as const })),
  { ...defaultDetails.app, id: "application", section: "app" as const },
];

function currentSection(pathname: string): Section {
  if (pathname.startsWith("/training")) return "training";
  if (pathname.startsWith("/datasets")) return "datasets";
  return "app";
}

function App() {
  const [section, setSection] = useState<Section>(() => currentSection(window.location.pathname));
  const [railCollapsed, setRailCollapsed] = useState(false);
  const [theme, setTheme] = useState<ThemeMode>(() => {
    const savedTheme = window.localStorage.getItem("signal-studio-theme");
    return savedTheme === "light" || savedTheme === "contrast" ? savedTheme : "dark";
  });
  const [detail, setDetail] = useState<Detail>(defaultDetails[section]);
  const [detailOpen, setDetailOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);

  const health = useQuery({
    queryKey: ["api-health"],
    queryFn: getHealth,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  useEffect(() => {
    if (!navItems.some((item) => window.location.pathname.startsWith(item.path))) {
      window.history.replaceState(null, "", "/app");
    }

    const handleNavigation = () => setSection(currentSection(window.location.pathname));
    window.addEventListener("popstate", handleNavigation);
    return () => window.removeEventListener("popstate", handleNavigation);
  }, []);

  useEffect(() => {
    const focusSearch = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      const isTyping =
        target?.isContentEditable ||
        target?.tagName === "INPUT" ||
        target?.tagName === "TEXTAREA" ||
        target?.tagName === "SELECT";

      if (event.key.toLowerCase() === "k" && !isTyping && !event.ctrlKey && !event.metaKey && !event.altKey) {
        event.preventDefault();
        searchInputRef.current?.focus();
      }
    };

    window.addEventListener("keydown", focusSearch);
    return () => window.removeEventListener("keydown", focusSearch);
  }, []);

  useEffect(() => {
    setDetail(defaultDetails[section]);
    setDetailOpen(false);
    setSearchQuery("");
  }, [section]);

  useEffect(() => {
    window.localStorage.setItem("signal-studio-theme", theme);
  }, [theme]);

  const searchResults = searchQuery.trim()
    ? globalSearchItems
        .filter((item) =>
          `${item.title} ${item.eyebrow} ${item.summary}`
            .toLowerCase()
            .includes(searchQuery.trim().toLowerCase()),
        )
        .slice(0, 5)
    : [];

  function showDetail(nextDetail: Detail) {
    setDetail(nextDetail);
    setDetailOpen(true);
  }

  function navigateTo(nextSection: Section) {
    const path = navItems.find((item) => item.id === nextSection)?.path ?? "/app";
    if (window.location.pathname !== path) window.history.pushState(null, "", path);
    setSection(nextSection);
  }

  function selectSearchResult(item: (typeof globalSearchItems)[number]) {
    navigateTo(item.section);
    setDetail(item);
    setDetailOpen(true);
    setSearchQuery("");
  }

  function cycleTheme() {
    setTheme((current) => {
      if (current === "dark") return "light";
      if (current === "light") return "contrast";
      return "dark";
    });
  }

  const healthState = health.isPending
    ? "checking"
    : health.isSuccess
      ? "online"
      : "offline";

  return (
    <div
      className={`app ${railCollapsed ? "rail-collapsed" : ""}`}
      data-theme={theme}
    >
      <a className="skip-link" href="#workspace">
        Skip to workspace
      </a>

      <aside className="icon-rail" aria-label="Primary navigation">
        <a
          className="brand"
          href="/app"
          aria-label="SMS Spam Classifier home"
          onClick={(event) => {
            event.preventDefault();
            navigateTo("app");
          }}
        >
          <span className="brand-mark" aria-hidden="true">
            <MessageSquareText size={20} strokeWidth={2.2} />
          </span>
          <span className="brand-copy">
            <strong>SMS Spam</strong>
            <small>Classifier</small>
          </span>
        </a>

        <nav className="rail-nav">
          {navItems.map(({ id, path, label, icon: Icon }) => (
            <a
              key={path}
              href={path}
              className={`rail-link ${section === id ? "active" : ""}`}
              aria-label={label}
              aria-current={section === id ? "page" : undefined}
              onClick={(event) => {
                event.preventDefault();
                navigateTo(id);
              }}
            >
              <Icon size={20} aria-hidden="true" />
              <span className="rail-label">{label}</span>
              <span className="tooltip" role="tooltip">
                {label}
              </span>
            </a>
          ))}
        </nav>

        <button
          className="rail-collapse"
          type="button"
          onClick={() => setRailCollapsed((value) => !value)}
          aria-label={railCollapsed ? "Show sidebar" : "Hide sidebar"}
          aria-expanded={!railCollapsed}
        >
          {railCollapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}
          <span>{railCollapsed ? "Show sidebar" : "Hide sidebar"}</span>
        </button>
      </aside>

      <div className="app-frame">
        <header className="top-header">
          <div className="mobile-brand">
            <MessageSquareText size={18} />
            <strong>SMS Spam</strong>
          </div>

          <div className="header-title">
            <span>Workspace</span>
            <strong>{navItems.find((item) => item.id === section)?.label}</strong>
          </div>

          <div className="global-search" role="search">
            <Search size={17} aria-hidden="true" />
            <label className="sr-only" htmlFor="global-search">
              Search datasets, metrics, and model details
            </label>
            <input
              ref={searchInputRef}
              id="global-search"
              type="search"
              placeholder="Search signals, metrics, layers…"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && searchResults[0]) {
                  event.preventDefault();
                  selectSearchResult(searchResults[0]);
                }
                if (event.key === "Escape") {
                  setSearchQuery("");
                  event.currentTarget.blur();
                }
              }}
              autoComplete="off"
            />
            <kbd aria-label="Press K to focus search">K</kbd>
            {searchQuery && (
              <div className="search-results" aria-live="polite">
                {searchResults.length ? (
                  searchResults.map((item) => (
                    <button
                      type="button"
                      key={`${item.section}-${item.id}`}
                      onClick={() => selectSearchResult(item)}
                    >
                      <span>{item.title}</span>
                      <small>{navItems.find((navItem) => navItem.id === item.section)?.label}</small>
                    </button>
                  ))
                ) : (
                  <p>No matching items</p>
                )}
              </div>
            )}
          </div>

          <div className="header-actions">
            <HealthPill state={healthState} />
            <HeaderLink
              href="https://github.com/a1mohamad/sms-spam-app"
              label="Source code"
              icon={<Github size={18} />}
            />
            <HeaderLink
              href="https://github.com/a1mohamad/machine-learning-portfolio/tree/main/SMS%20Spam"
              label="Training notebooks"
              icon={<Github size={18} />}
              marker="N"
            />
            <HeaderLink
              href="https://a1mohamad.github.io/research/sms-spam/index.html"
              label="Research article"
              icon={<BookOpen size={18} />}
            />
            <button
              className="icon-button theme-button"
              type="button"
              aria-label={`Current theme: ${theme}. Change theme.`}
              title={`Theme: ${theme}. Click for ${theme === "dark" ? "light" : theme === "light" ? "high contrast" : "dark"}.`}
              onClick={cycleTheme}
            >
              {theme === "dark" && <Moon size={18} />}
              {theme === "light" && <Sun size={18} />}
              {theme === "contrast" && <Contrast size={18} />}
            </button>
          </div>
        </header>

        <div className="workspace-grid">
          <main id="workspace" className="workspace" tabIndex={-1}>
            {section === "app" && (
              <ApiView healthState={healthState} onSelect={showDetail} />
            )}
            {section === "datasets" && <DatasetsView onSelect={showDetail} />}
            {section === "training" && <TrainingView onSelect={showDetail} />}
            <SiteFooter />
          </main>

          <DetailPanel
            detail={detail}
            section={section}
            open={detailOpen}
            onClose={() => setDetailOpen(false)}
          />
        </div>
      </div>

      <nav className="bottom-nav" aria-label="Mobile primary navigation">
        {navItems.map(({ id, path, label, icon: Icon }) => (
          <a
            key={path}
            href={path}
            className={section === id ? "active" : ""}
            aria-label={label}
            aria-current={section === id ? "page" : undefined}
            onClick={(event) => {
              event.preventDefault();
              navigateTo(id);
            }}
          >
            <Icon size={20} aria-hidden="true" />
            <span>{label}</span>
          </a>
        ))}
      </nav>
    </div>
  );
}

function HeaderLink({
  href,
  label,
  icon,
  marker,
}: {
  href: string;
  label: string;
  icon: ReactNode;
  marker?: string;
}) {
  return (
    <a
      className="icon-button header-link"
      href={href}
      target="_blank"
      rel="noreferrer"
      aria-label={label}
    >
      {icon}
      {marker && <span className="link-marker" aria-hidden="true">{marker}</span>}
      <span className="tooltip" role="tooltip">{label}</span>
    </a>
  );
}

function HealthPill({ state }: { state: "checking" | "online" | "offline" }) {
  const label =
    state === "checking" ? "Checking API" : state === "online" ? "API online" : "API sleeping";

  return (
    <span className={`health-pill ${state}`} title={label}>
      <span className="health-dot" aria-hidden="true" />
      {label}
    </span>
  );
}

function PageHeading({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow: string;
  title: string;
  description: string;
  actions?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="page-description">{description}</p>
      </div>
      {actions && <div className="page-actions">{actions}</div>}
    </div>
  );
}

function DatasetsView({ onSelect }: { onSelect: (detail: Detail) => void }) {
  const [layout, setLayout] = useState<"grid" | "list">("grid");

  return (
    <div className="page-stack">
      <PageHeading
        eyebrow="Dataset intelligence"
        title="Know the signal before the model"
        description="A compact view of class balance, message structure, and the strongest patterns found during exploration."
        actions={
          <div className="segmented-control" aria-label="Dataset layout">
            <button
              type="button"
              className={layout === "grid" ? "active" : ""}
              onClick={() => setLayout("grid")}
              aria-label="Grid view"
              aria-pressed={layout === "grid"}
            >
              <Grid2X2 size={16} />
            </button>
            <button
              type="button"
              className={layout === "list" ? "active" : ""}
              onClick={() => setLayout("list")}
              aria-label="List view"
              aria-pressed={layout === "list"}
            >
              <List size={17} />
            </button>
          </div>
        }
      />

      <section className="dataset-hero surface-card" aria-labelledby="dataset-name">
        <div className="dataset-identity">
          <span className="hero-icon violet"><Database size={24} /></span>
          <div>
            <div className="title-row">
              <h2 id="dataset-name">SMS Spam Collection</h2>
              <span className="soft-badge">Notebook snapshot</span>
            </div>
            <p>Public labeled messages · English · Binary classification</p>
          </div>
        </div>
        <div className="distribution-block" aria-label="Class distribution: 86.6% ham and 13.4% spam">
          <div className="distribution-labels">
            <span><i className="ham-dot" />Ham <strong>4,825</strong></span>
            <span><i className="spam-dot" />Spam <strong>747</strong></span>
          </div>
          <div className="distribution-bar" aria-hidden="true">
            <span className="ham-bar" />
            <span className="spam-bar" />
          </div>
        </div>
      </section>

      <section className={`metric-grid ${layout}`} aria-label="Dataset metrics">
        {datasetMetrics.map((metric) => (
          <MetricCard key={metric.id} detail={metric} onSelect={onSelect} />
        ))}
      </section>

      <section>
        <SectionHeading
          eyebrow="Pattern scan"
          title="Signals hiding in the corpus"
          description="Select an insight to inspect its evidence."
        />
        <div className="insight-grid">
          {signalInsights.map((insight) => (
            <button
              className="insight-card surface-card"
              type="button"
              key={insight.id}
              onClick={() => onSelect(insight)}
            >
              <span className={`tone-orb ${insight.tone}`} aria-hidden="true" />
              <span className="eyebrow">{insight.eyebrow}</span>
              <strong className="insight-stat">{insight.stat}</strong>
              <h3>{insight.title}</h3>
              <p>{insight.summary}</p>
              <span className="card-link">Inspect signal <ArrowRight size={15} /></span>
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

function TrainingView({ onSelect }: { onSelect: (detail: Detail) => void }) {
  return (
    <div className="page-stack">
      <PageHeading
        eyebrow="Training snapshot"
        title="A small model with a sharp signal"
        description="The champion Bi-LSTM configuration and validation story captured from the modeling notebook."
        actions={<span className="status-badge"><Check size={14} />Production artifact</span>}
      />

      <section className="training-banner surface-card">
        <div>
          <p className="eyebrow">Champion run</p>
          <h2>Trial 04 <span>of 30</span></h2>
          <p>Bayesian optimization selected a compact network that generalizes without unnecessary depth.</p>
        </div>
        <div className="trial-score">
          <span>Best validation</span>
          <strong>98.87%</strong>
          <small>accuracy</small>
        </div>
        <div className="banner-glow" aria-hidden="true" />
      </section>

      <section className="metric-grid grid" aria-label="Training metrics">
        {trainingMetrics.map((metric) => (
          <MetricCard key={metric.id} detail={metric} onSelect={onSelect} />
        ))}
      </section>

      <section>
        <SectionHeading
          eyebrow="Architecture"
          title="From raw SMS to probability"
          description="Four purposeful stages, optimized for fast production inference."
        />
        <div className="architecture-flow">
          {architectureSteps.map((step, index) => (
            <button
              key={step.id}
              type="button"
              className="architecture-step"
              onClick={() => onSelect(step)}
            >
              <span className={`step-number ${step.tone}`}>{step.short}</span>
              <span>
                <small>{step.eyebrow}</small>
                <strong>{step.title}</strong>
              </span>
              {index < architectureSteps.length - 1 && <ChevronRight className="step-arrow" size={17} />}
            </button>
          ))}
        </div>
      </section>

      <section className="training-notes">
        <article className="surface-card note-card">
          <span className="hero-icon cyan"><Layers3 size={21} /></span>
          <div>
            <p className="eyebrow">Training recipe</p>
            <h3>Stratified and class-aware</h3>
            <p>An 80/20 split and balanced class weights keep the minority spam class visible during learning.</p>
          </div>
        </article>
        <article className="surface-card note-card">
          <span className="hero-icon amber"><Clock3 size={21} /></span>
          <div>
            <p className="eyebrow">Convergence</p>
            <h3>Guarded against overfitting</h3>
            <p>Early stopping, checkpointing, and learning-rate decay preserve the strongest validation state.</p>
          </div>
        </article>
      </section>
    </div>
  );
}

function ApiView({
  healthState,
  onSelect,
}: {
  healthState: "checking" | "online" | "offline";
  onSelect: (detail: Detail) => void;
}) {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<SessionPrediction[]>([]);

  const prediction = useMutation({
    mutationFn: createPrediction,
    onSuccess: (result) => {
      const record: SessionPrediction = {
        ...result,
        id: crypto.randomUUID(),
        createdAt: new Date(),
      };
      setHistory((items) => [record, ...items].slice(0, 5));
      onSelect(predictionDetail(record));
    },
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    const text = message.trim();
    if (!text || prediction.isPending) return;
    prediction.mutate(text);
  }

  const result = prediction.data;
  const probability = result ? result.spam_probability * 100 : 0;

  return (
    <div className="page-stack api-page">
      <PageHeading
        eyebrow="Live classifier"
        title="Read the signal in any message"
        description="Test the production ONNX model and see exactly how its probability compares with the classification threshold."
        actions={<HealthPill state={healthState} />}
      />

      {healthState !== "online" && (
        <div className="wake-notice" role="status">
          <Info size={18} />
          <span>
            <strong>The free API may be waking up.</strong>
            The first request can take about a minute; later requests are fast.
          </span>
        </div>
      )}

      <div className="api-layout">
        <form className="composer surface-card" onSubmit={submit}>
          <div className="composer-heading">
            <div>
              <p className="eyebrow">Message input</p>
              <h2>Paste an SMS</h2>
            </div>
            <span className="privacy-chip"><LockKeyhole size={13} />Encrypted at rest</span>
          </div>

          <label htmlFor="sms-message">SMS message</label>
          <div className="textarea-wrap">
            <textarea
              id="sms-message"
              value={message}
              onChange={(event) => {
                setMessage(event.target.value);
                if (!prediction.isIdle) prediction.reset();
              }}
              placeholder="Type or paste the message you want to inspect…"
              maxLength={1000}
              rows={8}
              onKeyDown={(event) => {
                if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                  event.currentTarget.form?.requestSubmit();
                }
              }}
            />
            <span className="char-count">{message.length} / 1,000</span>
          </div>

          <div className="example-row">
            <span>Try an example</span>
            <div>
              {smsExamples.map((example) => (
                <button
                  type="button"
                  key={example.label}
                  onClick={() => {
                    setMessage(example.text);
                    prediction.reset();
                  }}
                >
                  {example.label}
                </button>
              ))}
            </div>
          </div>

          {prediction.isError && (
            <div className="inline-error" role="alert">
              <CircleAlert size={17} />
              {prediction.error.message}
            </div>
          )}

          <button className="primary-button" type="submit" disabled={!message.trim() || prediction.isPending}>
            {prediction.isPending ? (
              <><span className="spinner" />Analyzing signal…</>
            ) : (
              <><Sparkles size={17} />Analyze message<span className="shortcut">⌘ ↵</span></>
            )}
          </button>
        </form>

        <section className={`result-card surface-card ${result ? result.label : "empty"}`} aria-live="polite">
          {result ? (
            <>
              <div className="result-heading">
                <div>
                  <p className="eyebrow">Classification</p>
                  <h2>{result.label === "spam" ? "Spam detected" : "Looks like ham"}</h2>
                </div>
                <span className={`result-label ${result.label}`}>
                  {result.label === "spam" ? <CircleAlert size={16} /> : <ShieldCheck size={16} />}
                  {result.label}
                </span>
              </div>

              <div
                className="probability-ring"
                style={{ "--probability": `${probability * 3.6}deg` } as CSSProperties}
                aria-label={`${probability.toFixed(1)} percent spam probability`}
              >
                <div>
                  <strong>{probability.toFixed(1)}%</strong>
                  <span>spam probability</span>
                </div>
              </div>

              <div className="threshold-block">
                <div><span>Ham</span><span>Threshold 50%</span><span>Spam</span></div>
                <div className="threshold-track">
                  <span className="threshold-marker" />
                  <span className="probability-marker" style={{ left: `${probability}%` }} />
                </div>
              </div>

              <div className="result-footer">
                <span><LockKeyhole size={14} />Encrypted record saved</span>
                {result.requestId && <code title={result.requestId}>{result.requestId.slice(0, 8)}</code>}
              </div>
            </>
          ) : (
            <div className="empty-result">
              <span className="empty-orbit"><Braces size={28} /></span>
              <p className="eyebrow">Awaiting message</p>
              <h2>Your result will appear here</h2>
              <p>The API returns a label and spam probability, then stores the message as encrypted ciphertext.</p>
            </div>
          )}
        </section>
      </div>

      <section className="session-section">
        <SectionHeading
          eyebrow="Local activity"
          title="This session"
          description="Only response metadata is kept here; message text is not stored in the browser."
        />
        {history.length ? (
          <div className="session-list">
            {history.map((item) => (
              <button type="button" key={item.id} onClick={() => onSelect(predictionDetail(item))}>
                <span className={`session-icon ${item.label}`}>
                  {item.label === "spam" ? <CircleAlert size={16} /> : <ShieldCheck size={16} />}
                </span>
                <span><strong>{item.label}</strong><small>{item.createdAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</small></span>
                <strong>{(item.spam_probability * 100).toFixed(1)}%</strong>
                <ChevronRight size={17} />
              </button>
            ))}
          </div>
        ) : (
          <div className="empty-session"><Clock3 size={18} />Predictions made in this tab will appear here.</div>
        )}
      </section>
    </div>
  );
}

function predictionDetail(result: Prediction): Detail {
  const percentage = `${(result.spam_probability * 100).toFixed(2)}%`;
  return {
    eyebrow: "Prediction result",
    title: result.label === "spam" ? "Spam detected" : "Ham message",
    value: percentage,
    summary: `The model assigned a ${percentage} spam probability against its 50% decision threshold.`,
    facts: [
      `Public label: ${result.label}`,
      "Encrypted message persisted to PostgreSQL",
      result.requestId ? `Request: ${result.requestId}` : "Request ID unavailable",
    ],
    tone: result.label === "spam" ? "coral" : "mint",
  };
}

function MetricCard({ detail, onSelect }: { detail: Detail; onSelect: (detail: Detail) => void }) {
  return (
    <button className="metric-card surface-card" type="button" onClick={() => onSelect(detail)}>
      <span className={`metric-accent ${detail.tone}`} aria-hidden="true" />
      <span className="eyebrow">{detail.eyebrow}</span>
      <strong className="metric-value">{detail.value}</strong>
      <span className="metric-title">{detail.title}</span>
      <span className="metric-summary">{detail.summary}</span>
      <ArrowRight className="metric-arrow" size={16} aria-hidden="true" />
    </button>
  );
}

function SectionHeading({
  eyebrow,
  title,
  description,
}: {
  eyebrow: string;
  title: string;
  description: string;
}) {
  return (
    <div className="section-heading">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}

const contactLinks = [
  { href: "mailto:a1.mohamad.askari@gmail.com", label: "Gmail", icon: FaGoogle },
  { href: "mailto:amirmohmdaskari@gmail.com", label: "iCloud", icon: FaApple },
  { href: "tel:+989012223122", label: "Phone", icon: FaPhone },
  { href: "https://github.com/a1mohamad", label: "GitHub", icon: FaGithub },
  { href: "https://www.linkedin.com/in/amirmohammad-askari/", label: "LinkedIn", icon: FaLinkedin },
  { href: "https://www.kaggle.com/amirmohamadaskari", label: "Kaggle", icon: FaKaggle },
];

function SiteFooter() {
  return (
    <footer className="site-footer">
      <nav className="footer-links" aria-label="Contact links">
        {contactLinks.map(({ href, label, icon: Icon }) => (
          <a
            key={label}
            href={href}
            target={href.startsWith("http") ? "_blank" : undefined}
            rel={href.startsWith("http") ? "noreferrer" : undefined}
            aria-label={label}
            title={label}
          >
            <Icon size={22} aria-hidden="true" />
          </a>
        ))}
      </nav>
      <p>© 2026 Amir Mohamad Askari · All rights reserved.</p>
      <small>Research and source code are shared under the Apache License 2.0.</small>
    </footer>
  );
}

function DetailPanel({
  detail,
  section,
  open,
  onClose,
}: {
  detail: Detail;
  section: Section;
  open: boolean;
  onClose: () => void;
}) {
  const source = section === "training"
    ? {
        href: "https://github.com/a1mohamad/machine-learning-portfolio/tree/main/SMS%20Spam",
        label: "Training notebooks",
      }
    : {
        href: "https://github.com/a1mohamad/sms-spam-app",
        label: "Application repository",
      };

  return (
    <>
      <button
        className={`detail-backdrop ${open ? "open" : ""}`}
        type="button"
        aria-label="Close detail panel"
        onClick={onClose}
      />
      <aside className={`detail-panel ${open ? "open" : ""}`} aria-label="Selected item details">
        <div className="detail-mobile-handle" aria-hidden="true" />
        <div className="detail-topbar">
          <span>Inspector</span>
          <button className="icon-button detail-close" type="button" aria-label="Close details" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className={`detail-visual ${detail.tone ?? "violet"}`}>
          <span className="detail-grid" aria-hidden="true" />
          <Sparkles size={24} />
          {detail.value && <strong>{detail.value}</strong>}
        </div>

        <div className="detail-copy">
          <p className="eyebrow">{detail.eyebrow}</p>
          <h2>{detail.title}</h2>
          <p>{detail.summary}</p>
        </div>

        <div className="detail-facts">
          <span>Key facts</span>
          <ul>
            {detail.facts.map((fact) => (
              <li key={fact}><Check size={15} />{fact}</li>
            ))}
          </ul>
        </div>

        <a className="detail-source" href={source.href} target="_blank" rel="noreferrer">
          <Server size={16} />
          <span><strong>Source of truth</strong>{source.label}</span>
          <ExternalLink size={14} />
        </a>
      </aside>
    </>
  );
}

export default App;
