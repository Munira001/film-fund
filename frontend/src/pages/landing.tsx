import { useEffect, useRef, useState } from "react";
import {
  Menu,
  X,
} from "lucide-react";

import { BrandMark } from "@/components/brand-mark";
import {
  type Intake,
  OnboardingDialog,
} from "@/components/onboarding";

type Tab =
  | "search"
  | "profile"
  | "saved"
  | "tracker"
  | "budget"
  | "resources";

type LandingPanel = "form" | "how" | "pricing" | null;

const funders = [
  "Sundance Institute",
  "Chicken & Egg Pictures",
  "Film Independent",
  "Hubert Bals Fund",
  "Creative Capital",
  "The Film Collaborative",
];

const faqItems: [string, string][] = [
  [
    "I already use festival directories. Is this for me?",
    "Yes. FILMFUND sits above scattered lists. It reads who you are, ranks live grants against your scripts and budget, and keeps applications in one tracker.",
  ],
  [
    "What should I prepare first?",
    "Start with a one-page treatment, a realistic budget, and a clear sentence about why the story matters now.",
  ],
  [
    "How does matching work?",
    "FILMFUND compares your profile, project details, budget, and eligibility against each opportunity, then sorts by fit.",
  ],
  [
    "Can I track applications?",
    "Yes. Apply from any grant card and the opportunity is added to your Application Tracker.",
  ],
  [
    "Does my work leave this machine?",
    "Search talks to the FILMFUND research backend. Scripts you upload stay in this workspace unless you download or share them.",
  ],
];

const features = [
  {
    eyebrow: "Who you are",
    title: "Tell FILMFUND about the work",
    body: "Every project starts from a real filmmaker profile. Location, career stage, genres, budget, and scripts in development. Matches use that, not a generic grant dump.",
    src: "/optimized/feature3.jpg",
    alt: "Coastal dunes behind the profile mockup",
    media: "profile" as const,
  },
  {
    eyebrow: "Visibility",
    title: "The whole slate, at a glance",
    body: "Every opportunity moves across one board: pending, fitting, applied, ready to submit. Deadline and match sit on the card so you see what needs you.",
    src: "/optimized/hero-background.jpg",
    alt: "Golden clouds behind the grant board mockup",
    media: "board" as const,
  },
  {
    eyebrow: "Feedback loop",
    title: "A missed check goes back to the session",
    body: "FILMFUND watches the opportunities you open. Missing documents and review notes route back to the project that owns them until the packet is ready.",
    src: "/optimized/feature2.jpg",
    alt: "Forest behind the application session mockup",
    media: "session" as const,
  },
  {
    eyebrow: "Coverage",
    title: "Search the funds you already trust",
    body: "Sundance, Film Independent, Hubert Bals, Creative Capital, and the rest of the field. Describe the outcome. FILMFUND plans the search and ranks what fits.",
    src: "/optimized/feature4.jpg",
    alt: "Clouds behind the new-search mockup",
    media: "search" as const,
  },
  {
    eyebrow: "The film room",
    title: "Your slate goes where you go",
    body: "Keep the films and scripts beside the funding board. Watch a cut, open a PDF, and jump back to the grant that can move it.",
    src: "/optimized/feature3.jpg",
    alt: "Dunes behind the mobile companion mockup",
    media: "phone" as const,
  },
];

const CTA_TICKS = 20;

function CtaOrbit() {
  return (
    <div className="cta-orbit" aria-hidden="true">
      {Array.from({ length: CTA_TICKS }, (_, index) => (
        <span
          key={index}
          className="cta-tick"
          style={
            {
              "--tick-start": `${(index / CTA_TICKS) * 100}%`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  );
}

function OverlayPanel({
  title,
  rows,
}: {
  title: string;
  rows: { label: string; value: string }[];
}) {
  return (
    <div className="w-[min(88%,21rem)] rounded-[1.4rem] bg-white p-4 shadow-[0_18px_50px_rgba(29,29,22,0.14)]">
      <div className="mb-3 flex items-center gap-2">
        <img src="/ff-logo.svg" alt="" className="h-5 w-5" />
        <p className="text-sm font-medium">{title}</p>
      </div>
      <div className="space-y-1.5">
        {rows.map((row) => (
          <div
            key={row.label}
            className="flex items-center justify-between rounded-xl bg-[#f4f3ef] px-3 py-2.5 text-[13px]"
          >
            <span className="text-foreground/80">{row.label}</span>
            <span className="text-foreground/55">{row.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function FeatureOverlay({
  kind,
}: {
  kind: (typeof features)[number]["media"];
}) {
  if (kind === "profile") {
    return (
      <OverlayPanel
        title="Who you are"
        rows={[
          { label: "Name", value: "Munira Mohammed" },
          { label: "Location", value: "Ghana" },
          { label: "Stage", value: "Professional" },
        ]}
      />
    );
  }
  if (kind === "board") {
    return (
      <OverlayPanel
        title="Grant board"
        rows={[
          { label: "Sundance Institute", value: "96% match" },
          { label: "Film Independent", value: "In review" },
          { label: "Creative Capital", value: "Ready" },
        ]}
      />
    );
  }
  if (kind === "session") {
    return (
      <OverlayPanel
        title="Application"
        rows={[
          { label: "New Voices Fellowship", value: "Submitted" },
          { label: "Deadline", value: "Oct 22" },
          { label: "Missing", value: "Treatment" },
        ]}
      />
    );
  }
  if (kind === "search") {
    return (
      <OverlayPanel
        title="Search"
        rows={[
          { label: "Drama · Ghana", value: "5 funds" },
          { label: "Hubert Bals Fund", value: "Fits" },
          { label: "Chicken & Egg", value: "Fits" },
        ]}
      />
    );
  }
  return (
    <OverlayPanel
      title="Film room"
      rows={[
        { label: "Bills & Records", value: "Watch" },
        { label: "Juno", value: "Script" },
        { label: "Moonlight", value: "Script" },
      ]}
    />
  );
}

function FeatureStack() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [progress, setProgress] = useState(0);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(media.matches);
    const onChange = () => setReduced(media.matches);
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  useEffect(() => {
    if (reduced) return;

    const onScroll = () => {
      const el = wrapRef.current;
      if (!el) return;
      const total = el.offsetHeight - window.innerHeight;
      const scrolled = window.scrollY - el.offsetTop;
      setProgress(Math.min(1, Math.max(0, scrolled / Math.max(total, 1))));
    };

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [reduced]);

  const p = progress * (features.length - 1);
  const active = Math.min(
    features.length - 1,
    Math.max(0, Math.round(p)),
  );
  const feature = features[active];

  if (reduced) {
    return (
      <section id="features" className="feature-pin-stage px-4 py-20">
        {features.map((item) => (
          <article key={item.eyebrow} className="mx-auto w-full max-w-4xl">
            <div className="feature-photo relative mx-auto aspect-[1100/693] w-full max-w-[60rem]">
              <img
                src={item.src}
                alt=""
                className="h-full w-full object-cover"
              />
              <div className="absolute inset-0 flex items-center justify-center">
                <FeatureOverlay kind={item.media} />
              </div>
            </div>
            <div className="mx-auto mt-6 max-w-md text-center">
              <h3 className="hero-display text-3xl">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-foreground/65">
                {item.body}
              </p>
            </div>
          </article>
        ))}
      </section>
    );
  }

  return (
    <section id="features" ref={wrapRef} className="feature-pin">
      <div className="feature-pin-stage">
        <div className="mx-auto grid w-full max-w-[88rem] items-center gap-10 px-6 lg:grid-cols-[minmax(16rem,22rem)_minmax(0,1fr)]">
        <div className="relative z-20 hidden text-left lg:block">
          <p className="eyebrow mb-3">{feature.eyebrow}</p>
          <h3 className="hero-display text-4xl leading-[1.05] text-balance">
            {feature.title}
          </h3>
          <p className="mt-4 text-sm leading-6 text-foreground/70">
            {feature.body}
          </p>
        </div>

        <div className="feature-deck relative z-10 w-full min-w-0">
          {features.map((item, index) => {
            const d = index - p;
            const behind = Math.max(0, d);
            const leaving = Math.max(0, -d);
            const scale = 1 - Math.min(behind, 3) * 0.13;
            const y = behind * 56 - leaving * 170;
            const opacity =
              behind > 2.3 || leaving > 1.05 ? 0 : 1;
            const zIndex = Math.round((features.length - behind) * 10);

            return (
              <div
                key={item.eyebrow}
                className="feature-photo"
                style={{
                  transform: `translateY(${y}px) scale(${scale})`,
                  opacity,
                  zIndex,
                }}
              >
                <img
                  src={item.src}
                  alt=""
                  className="h-full w-full object-cover"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                  {index === active ? (
                    <FeatureOverlay kind={item.media} />
                  ) : null}
                </div>
              </div>
            );
          })}
        </div>
        </div>

        <div className="absolute inset-x-6 bottom-6 z-30 mx-auto max-w-md text-center lg:hidden">
          <p className="eyebrow mb-2">{feature.eyebrow}</p>
          <h3 className="hero-display text-3xl leading-[1.05]">
            {feature.title}
          </h3>
          <p className="mt-3 text-sm leading-6 text-foreground/65">
            {feature.body}
          </p>
        </div>

        <div className="feature-dots">
          {features.map((item, index) => (
            <button
              key={item.eyebrow}
              type="button"
              aria-label={item.title}
              aria-current={index === active ? "true" : undefined}
              className={`feature-dot${index === active ? " is-active" : ""}`}
              onClick={() => {
                const el = wrapRef.current;
                if (!el) return;
                const total = el.offsetHeight - window.innerHeight;
                const y =
                  el.offsetTop +
                  (index / Math.max(features.length - 1, 1)) * total;
                window.scrollTo({ top: y, behavior: "smooth" });
              }}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

export function Landing({
  onEnter,
  onGetStarted,
}: {
  onEnter: (tab?: Tab) => void;
  onGetStarted: (intake: Intake) => void;
}) {
  const [heroName, setHeroName] = useState("");
  const [onboarding, setOnboarding] = useState(false);
  const [panel, setPanel] = useState<LandingPanel>(null);
  const [faqOpen, setFaqOpen] = useState<number | null>(0);
  const [mobileNav, setMobileNav] = useState(false);
  const panelRef = useRef<HTMLElement>(null);

  const openOnboarding = () => {
    setOnboarding(true);
    setMobileNav(false);
  };

  const openPanel = (nextPanel: Exclude<LandingPanel, null>) => {
    if (nextPanel === "form") {
      openOnboarding();
      return;
    }

    setPanel(nextPanel);
    setMobileNav(false);

    window.setTimeout(() => {
      panelRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 50);
  };

  const looksLikeEmail = heroName.includes("@");
  const initialName = looksLikeEmail ? "" : heroName.trim();
  const initialEmail = looksLikeEmail ? heroName.trim() : "";

  return (
    <div className="relative min-h-[100dvh] bg-background text-foreground">
      <main className="flex flex-col bg-background">
        <section className="relative min-h-[100dvh] overflow-hidden">
          <video
            autoPlay
            muted
            loop
            playsInline
            preload="auto"
            poster="/optimized/hero-makers.jpg"
            className="pointer-events-none absolute inset-0 h-full w-full object-cover"
            data-testid="video-landing-film"
          >
            <source src="/media/hero-makers.mp4" type="video/mp4" />
          </video>
          <div className="absolute inset-0 bg-gradient-to-b from-[#f9f8f5]/50 via-[#f9f8f5]/25 to-[#f9f8f5]/55" />

          <header className="absolute inset-x-0 top-5 z-30 flex justify-center px-4 sm:top-7">
            <div className="flex items-center gap-0.5 rounded-[8px] border border-[#1d1d16]/18 bg-white/95 p-1 shadow-[0_8px_30px_rgba(29,29,22,0.08)] backdrop-blur-md">
              <button
                onClick={() => onEnter("search")}
                data-testid="brand-landing"
                className="flex h-10 items-center gap-2 rounded-[6px] bg-white px-3.5 text-left shadow-sm"
              >
                <BrandMark />
              </button>
              <nav className="hidden items-center lg:flex">
                <button
                  onClick={() => openPanel("how")}
                  data-testid="link-how-it-works"
                  className="h-10 rounded-[6px] px-4 text-sm text-foreground/80 hover:bg-white hover:text-foreground"
                >
                  How it works
                </button>
                <button
                  onClick={() => onEnter("search")}
                  data-testid="link-search-grants"
                  className="h-10 rounded-[6px] px-4 text-sm text-foreground/80 hover:bg-white hover:text-foreground"
                >
                  Demo
                </button>
                <button
                  onClick={() => openPanel("pricing")}
                  data-testid="link-pricing"
                  className="h-10 rounded-[6px] px-4 text-sm text-foreground/80 hover:bg-white hover:text-foreground"
                >
                  Pricing
                </button>
              </nav>
              <button
                onClick={() => openPanel("form")}
                data-testid="button-enter-top"
                className="pressable hidden h-10 rounded-[6px] bg-foreground px-4 text-sm font-medium text-background hover:opacity-90 lg:inline-flex lg:items-center"
              >
                Get started
              </button>
              <button
                type="button"
                className="grid size-10 place-items-center rounded-[6px] text-muted-foreground lg:hidden"
                aria-controls="mobile-nav"
                aria-expanded={mobileNav}
                onClick={() => setMobileNav((open) => !open)}
              >
                {mobileNav ? <X size={18} /> : <Menu size={18} />}
              </button>
            </div>
          </header>

          {mobileNav ? (
            <div
              id="mobile-nav"
              className="absolute inset-x-4 top-[4.75rem] z-30 rounded-[8px] border border-[#1d1d16]/18 bg-white/95 p-1.5 shadow-lg backdrop-blur-md lg:hidden"
            >
              <button
                onClick={() => openPanel("how")}
                className="w-full rounded-lg px-3 py-2.5 text-left text-sm hover:bg-muted/60"
              >
                How it works
              </button>
              <button
                onClick={() => onEnter("search")}
                className="w-full rounded-lg px-3 py-2.5 text-left text-sm hover:bg-muted/60"
              >
                Demo
              </button>
              <button
                onClick={() => openPanel("pricing")}
                className="w-full rounded-lg px-3 py-2.5 text-left text-sm hover:bg-muted/60"
              >
                Pricing
              </button>
              <button
                onClick={() => openPanel("form")}
                className="w-full rounded-lg bg-foreground px-3 py-2.5 text-left text-sm font-medium text-background"
              >
                Get started
              </button>
            </div>
          ) : null}

          <div className="relative z-10 flex min-h-[100dvh] flex-col items-center justify-center px-5 pb-28 pt-24 text-center">
            <h1 className="hero-display max-w-5xl text-5xl leading-[0.95] text-balance text-foreground sm:text-7xl lg:text-8xl [text-shadow:0_0_24px_#f9f8f5,0_0_48px_#f9f8f5]">
              Focus on your craft.
              <span className="mt-1 block italic">We'll find the grants.</span>
            </h1>
            <p className="mt-6 max-w-xl text-base leading-7 text-foreground sm:text-lg [text-shadow:0_0_16px_#f9f8f5,0_0_32px_#f9f8f5]">
              Stay on the filmmaking. FILMFUND matches live funds to your
              scripts, budget, and eligibility.
            </p>
          </div>

          <div className="cta-wrap">
            <CtaOrbit />
            <form
              className="relative z-10 flex w-full items-center gap-1 rounded-full border border-white/80 bg-[#f9f8f5]/88 p-1.5 shadow-[0_12px_40px_rgba(29,29,22,0.12)] backdrop-blur-md"
              onSubmit={(event) => {
                event.preventDefault();
                openOnboarding();
              }}
            >
              <input
                value={heroName}
                onChange={(event) => setHeroName(event.target.value)}
                type="text"
                autoComplete="name"
                placeholder="Enter your name"
                data-testid="input-hero-name"
                className="h-11 min-w-0 flex-1 rounded-full bg-transparent px-4 text-sm outline-none placeholder:text-foreground/45"
              />
              <button
                type="submit"
                data-testid="button-get-started-email"
                className="pressable h-11 shrink-0 rounded-full bg-foreground px-5 text-sm font-medium text-background hover:opacity-90"
              >
                Get started
              </button>
            </form>
          </div>
        </section>

        {panel ? (
          <section
            ref={panelRef}
            id={`landing-${panel}`}
            className="section-shell pt-0"
            aria-live="polite"
          >
            <div className="mx-auto max-w-7xl rounded-[10px] border border-border bg-card p-6 md:p-10">
              <div className="flex items-start justify-between gap-6">
                <div>
                  <h2 className="text-2xl font-semibold tracking-[-0.5px] md:text-3xl">
                    {panel === "how" ? "How it works" : "Pricing"}
                  </h2>
                </div>
                <button
                  type="button"
                  onClick={() => setPanel(null)}
                  className="grid size-11 place-items-center rounded-2xl border border-border text-muted-foreground hover:bg-muted/60 hover:text-foreground"
                  aria-label="Close section"
                >
                  <X size={18} />
                </button>
              </div>

              {panel === "how" && (
                <div className="mt-8 grid gap-4 md:grid-cols-3">
                  {(
                    [
                      [
                        "01",
                        "Tell us about the work",
                        "Who you are and the project budgets sharpen every match.",
                      ],
                      [
                        "02",
                        "Search live grants",
                        "Browse current grants, fellowships, and finishing funds.",
                      ],
                      [
                        "03",
                        "Move from match to submit",
                        "Save, compare, apply, and track each opportunity without losing the thread.",
                      ],
                    ] as const
                  ).map(([number, title, description]) => (
                    <div
                      key={number}
                      className="rounded-[10px] border border-border bg-background p-5"
                    >
                      <span className="font-mono text-sm text-muted-foreground">
                        {number}
                      </span>
                      <h3 className="mt-8 text-lg font-medium tracking-[-0.5px]">
                        {title}
                      </h3>
                      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                        {description}
                      </p>
                    </div>
                  ))}
                  <button
                    type="button"
                    onClick={() => onEnter("search")}
                    className="mt-2 w-fit rounded-2xl bg-foreground px-5 py-3 text-sm font-semibold text-background hover:opacity-90"
                    data-testid="button-how-it-works-search"
                  >
                    Start searching
                  </button>
                </div>
              )}

              {panel === "pricing" && (
                <div className="mt-8 grid gap-6 md:grid-cols-[1fr_auto] md:items-end">
                  <div>
                    <p className="max-w-2xl text-sm leading-7 text-muted-foreground">
                      No complicated plans here. FILMFUND is built around one
                      focused workflow: discover opportunities, make an informed
                      decision, then keep the application moving.
                    </p>
                    <div className="mt-6 grid gap-px bg-border sm:grid-cols-3">
                      {["Submitted", "Pending", "Awarded"].map((status) => (
                        <div key={status} className="bg-card p-4">
                          <p className="text-sm font-medium">{status}</p>
                          <p className="mt-2 font-mono text-[11px] text-muted-foreground">
                            In your tracker
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => onEnter("tracker")}
                    className="rounded-2xl bg-foreground px-5 py-3 text-sm font-semibold text-background hover:opacity-90"
                    data-testid="button-pricing-tracker"
                  >
                    Open application tracker
                  </button>
                </div>
              )}
            </div>
          </section>
        ) : null}

        <section className="overflow-hidden bg-background py-16 sm:py-24">
          <h2 className="mx-auto mb-12 max-w-3xl px-4 text-center text-3xl font-semibold tracking-[-0.5px]">
            Use the funds you already trust.
          </h2>
          <div className="funder-marquee group relative mx-auto max-w-2xl">
            <div className="funder-marquee__track flex w-max">
              {[0, 1].map((copy) => (
                <ul
                  key={copy}
                  className="flex shrink-0 items-center gap-8 pr-8"
                >
                  {funders.map((funder) => (
                    <li
                      key={`${copy}-${funder}`}
                      className="font-mono text-sm tracking-[0.5px] text-muted-foreground"
                    >
                      {funder}
                    </li>
                  ))}
                </ul>
              ))}
            </div>
          </div>
        </section>

        <FeatureStack />

        <section id="faq" className="section-shell">
          <div className="mx-auto max-w-7xl">
            <h2 className="text-3xl font-medium tracking-[-0.5px] whitespace-pre-line">
              {"Frequently\nasked questions"}
            </h2>
            <div className="mt-8 divide-y divide-border border-y border-border">
              {faqItems.map(([question, answer], index) => {
                const open = faqOpen === index;
                return (
                  <div key={question}>
                    <button
                      type="button"
                      onClick={() => setFaqOpen(open ? null : index)}
                      className="flex min-h-[77px] w-full items-center justify-between gap-4 py-5 text-left text-lg"
                    >
                      {question}
                      <span className="text-muted-foreground">
                        {open ? "×" : "+"}
                      </span>
                    </button>
                    {open ? (
                      <p className="max-w-3xl pb-6 text-sm leading-relaxed text-muted-foreground sm:text-base">
                        {answer}
                      </p>
                    ) : null}
                  </div>
                );
              })}
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-card">
        <div className="mx-auto max-w-7xl px-4 py-14 sm:px-8 sm:py-20 lg:px-[30px]">
          <div className="grid gap-10 lg:grid-cols-[minmax(0,1fr)_minmax(0,0.75fr)]">
            <p className="hidden text-4xl font-semibold leading-[1.08] tracking-[-0.04em] sm:block">
              Find grants
              <br />
              Match the work
              <br />
              Submit on time
            </p>
            <div className="grid grid-cols-2 gap-6 sm:grid-cols-3 sm:gap-8">
              <div>
                <p className="text-sm">Product</p>
                <div className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <button
                    className="block hover:text-foreground"
                    onClick={() =>
                      document
                        .getElementById("features")
                        ?.scrollIntoView({ behavior: "smooth" })
                    }
                  >
                    Features
                  </button>
                  <button
                    className="block hover:text-foreground"
                    onClick={() => onEnter("search")}
                  >
                    Search
                  </button>
                  <button
                    className="block hover:text-foreground"
                    onClick={() => onEnter("tracker")}
                  >
                    Tracker
                  </button>
                </div>
              </div>
              <div>
                <p className="text-sm">Help</p>
                <div className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <button
                    className="block hover:text-foreground"
                    onClick={() => openPanel("how")}
                  >
                    How it works
                  </button>
                  <button
                    className="block hover:text-foreground"
                    onClick={() =>
                      document
                        .getElementById("faq")
                        ?.scrollIntoView({ behavior: "smooth" })
                    }
                  >
                    FAQ
                  </button>
                </div>
              </div>
              <div>
                <p className="text-sm">Workspace</p>
                <div className="mt-3 space-y-2 text-sm text-muted-foreground">
                  <button
                    className="block hover:text-foreground"
                    onClick={() => onEnter("profile")}
                  >
                    Who you are
                  </button>
                  <button
                    className="block hover:text-foreground"
                    onClick={() => onEnter("budget")}
                  >
                    Budget
                  </button>
                  <button
                    className="block hover:text-foreground"
                    onClick={() => onEnter("saved")}
                  >
                    Saved grants
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>

      <OnboardingDialog
        open={onboarding}
        initialName={initialName}
        initialEmail={initialEmail}
        onClose={() => setOnboarding(false)}
        onComplete={(intake) => {
          setOnboarding(false);
          onGetStarted(intake);
        }}
      />
    </div>
  );
}
