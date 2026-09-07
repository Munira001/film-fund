import {
  type ReactNode,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";

import { ErrorBoundary } from "@/components/error-boundary";
import { Toaster } from "@/components/ui/toaster";
import { toast } from "@/hooks/use-toast";
import { TooltipProvider } from "@/components/ui/tooltip";


import {
  ArrowUpRight,
  ArrowDownUp,
  Bell,
  Bookmark,
  BookmarkCheck,
  Calculator,
  Check,
  CircleHelp,
  ClipboardList,
  Download,
  ExternalLink,
  FileText,
  LayoutDashboard,
  Menu,
  Moon,
  Search,
  Send,
  Settings2,
  SlidersHorizontal,
  Sparkles,
  Sun,
  Trash2,
  UserRound,
  X,
} from "lucide-react";

const queryClient = new QueryClient();

/* =========================================================
   TYPES
========================================================= */

type Grant = {
  id: string;
  title: string;
  organization: string;
  description: string;
  url: string;
  funding: string;
  deadline: string;
  category: string;
  location: string;
  trustScore: number;
  matchScore: number;
  eligibility: string;
  matchedScripts: string[];
};

type Tab =
  | "search"
  | "profile"
  | "saved"
  | "tracker"
  | "budget"
  | "resources";

type Profile = {
  name: string;
  location: string;
  level: string;
  genres: string;
  budget: string;
  scripts: string;
  production: string;
};

type Application = {
  id: string;
  title: string;
  organization: string;
  status: "Submitted" | "Pending" | "Awarded";
  date: string;
  funding: string;
};

type LandingPanel = "form" | "how" | "resources" | "pricing" | null;

type SortBy = "match" | "deadline" | "funding";

/* =========================================================
   BACKEND API
========================================================= */

type SearchParams = {
  q: string;
  genre?: string;
  location?: string;
  budget?: number;
};

/*
 * The frontend talks to your own backend.
 *
 * If your Python backend is served through the same domain,
 * these relative URLs work directly.
 *
 * If your backend runs separately during development, Vite can
 * proxy these requests to it.
 */

async function fetchHealth() {
  const response = await fetch("/health");

  if (!response.ok) {
    throw new Error("Backend health check failed");
  }

  return response.json();
}

async function fetchGrants(params: SearchParams): Promise<Grant[]> {
  const searchParams = new URLSearchParams();

  searchParams.set("q", params.q);

  if (params.genre) {
    searchParams.set("genre", params.genre);
  }

  if (params.location) {
    searchParams.set("location", params.location);
  }

  if (params.budget !== undefined) {
    searchParams.set("budget", String(params.budget));
  }

  const response = await fetch(`/api/grants/search?${searchParams.toString()}`);

  if (!response.ok) {
    throw new Error("Grant search failed");
  }

  const data = await response.json();

  /*
   * Support either:
   *   [...]
   * or:
   *   { grants: [...] }
   */
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.grants)) {
    return data.grants;
  }

  return [];
}

function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
    refetchInterval: 30000,
  });
}

function useSearchGrants(
  params: SearchParams,
  enabled: boolean,
) {
  return useQuery({
    queryKey: ["grants-search", params],
    queryFn: () => fetchGrants(params),
    enabled,
    retry: 1,
  });
}

/* =========================================================
   FALLBACK GRANTS
========================================================= */

const fallbackGrants: Grant[] = [
  {
    id: "ff-01",
    title: "Feature Film Development Fund",
    organization: "Sundance Institute",
    description:
      "Support for bold, independent storytellers developing their next feature with a distinct point of view.",
    url: "https://www.sundance.org",
    funding: "$15,000–$35,000",
    deadline: "2026-09-28",
    category: "Narrative",
    location: "United States",
    trustScore: 94,
    matchScore: 96,
    eligibility: "Emerging and mid-career filmmakers",
    matchedScripts: ["Juno"],
  },
  {
    id: "ff-02",
    title: "Documentary Film Grant",
    organization: "Chicken & Egg Pictures",
    description:
      "Production and completion support for women and nonbinary documentary filmmakers telling urgent stories.",
    url: "https://chickeneggpics.org",
    funding: "Up to $50,000",
    deadline: "2026-10-07",
    category: "Documentary",
    location: "North America",
    trustScore: 91,
    matchScore: 88,
    eligibility: "Women and nonbinary directors",
    matchedScripts: [],
  },
  {
    id: "ff-03",
    title: "New Voices Fellowship",
    organization: "Film Independent",
    description:
      "An intensive fellowship pairing financial support with mentorship, workshops, and a community of peers.",
    url: "https://www.filmindependent.org",
    funding: "$10,000 + mentorship",
    deadline: "2026-10-22",
    category: "Narrative",
    location: "Los Angeles",
    trustScore: 89,
    matchScore: 84,
    eligibility: "First or second-time directors",
    matchedScripts: ["Moonlight"],
  },
  {
    id: "ff-04",
    title: "Global Cinema Fund",
    organization: "Hubert Bals Fund",
    description:
      "A production fund for filmmakers from countries with limited funding opportunities and a strong cinematic voice.",
    url: "https://iffr.com",
    funding: "€10,000–€60,000",
    deadline: "2026-11-11",
    category: "International",
    location: "Global",
    trustScore: 87,
    matchScore: 79,
    eligibility: "Filmmakers from eligible countries",
    matchedScripts: ["Juno", "Moonlight"],
  },
  {
    id: "ff-05",
    title: "Artist Support Grant",
    organization: "Creative Capital",
    description:
      "Flexible project funding for ambitious artists making work that expands the language of their medium.",
    url: "https://creative-capital.org",
    funding: "$15,000",
    deadline: "2026-12-03",
    category: "Experimental",
    location: "United States",
    trustScore: 93,
    matchScore: 74,
    eligibility: "US artists across disciplines",
    matchedScripts: ["Whiplash"],
  },
];

/* =========================================================
   CONSTANTS
========================================================= */

const tabs: {
  id: Tab;
  label: string;
  icon: typeof Search;
}[] = [
    { id: "search", label: "Search grants", icon: Search },
    { id: "profile", label: "Filmmaker profile", icon: UserRound },
    { id: "saved", label: "Saved grants", icon: Bookmark },
    { id: "tracker", label: "Application tracker", icon: ClipboardList },
    { id: "budget", label: "Budget calculator", icon: Calculator },
    { id: "resources", label: "Resources", icon: CircleHelp },
  ];

const profileDefaults: Profile = {
  name: "Munira Mohammed",
  location: "Ghana",
  level: "Professional",
  genres: "Drama, Comedy-Drama, Drama-Thriller",
  budget: "100000",
  scripts:
    "Juno (Drama, $100,000), Moonlight (Drama-Thriller, $100,000), Whiplash (Comedy-Drama, $100,000)",
  production:
    "Independent production company developing three original features for international audiences. Currently packaging a small creative team and building a funding plan across development and production.",
};

const projectList = [
  {
    title: "Juno",
    genre: "Drama",
    budget: "$100,000",
  },
  {
    title: "Moonlight",
    genre: "Drama-Thriller",
    budget: "$100,000",
  },
  {
    title: "Whiplash",
    genre: "Comedy-Drama",
    budget: "$100,000",
  },
];

const showcaseVideos = [
  {
    title: "Bills & Records",
    type: "Short documentary",
    source: "/media/bills-records.mp4",
    label: "Uploaded film",
  },
  {
    title: "Late Night Convenience",
    type: "Indie short",
    source: "/media/late-night-convenience.mp4",
    label: "Uploaded film",
  },
  {
    title: "Manspread",
    type: "Short film",
    source: "/media/manspread.mp4",
    label: "Uploaded film",
  },
];

const showcaseScripts = [
  {
    title: "Juno",
    type: "Drama screenplay",
    source: "/media/juno-script.pdf",
    meta: "Script in development",
  },
  {
    title: "Moonlight",
    type: "Drama-thriller screenplay",
    source: "/media/moonlight-script.pdf",
    meta: "Script in development",
  },
  {
    title: "Whiplash",
    type: "Comedy-drama screenplay",
    source: "/media/whiplash-script.pdf",
    meta: "Script in development",
  },
  {
    title: "A Mind For Strategy",
    type: "Short screenplay",
    source: "/media/a-mind-for-strategy.pdf",
    meta: "Uploaded script",
  },
];

/* =========================================================
   HELPERS
========================================================= */

function readStorage<T>(key: string, fallback: T): T {
  try {
    const value = localStorage.getItem(key);
    return value ? (JSON.parse(value) as T) : fallback;
  } catch {
    return fallback;
  }
}

function writeStorage(key: string, value: unknown) {
  localStorage.setItem(key, JSON.stringify(value));
}

function money(value: string | number) {
  return Number(value || 0).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

function downloadFile(
  filename: string,
  content: string,
  type: string,
) {
  const url = URL.createObjectURL(
    new Blob([content], { type }),
  );

  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;

  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();

  URL.revokeObjectURL(url);
}

function parseFundingValue(funding: string) {
  const values =
    funding
      .match(/[\d,]+/g)
      ?.map((value) =>
        Number(value.replace(/,/g, "")),
      ) ?? [];

  return values[values.length - 1] ?? 0;
}

/* =========================================================
   LANDING
========================================================= */

function Landing({
  onEnter,
}: {
  onEnter: (tab?: Tab) => void;
}) {
  const [email, setEmail] = useState("");
  const [panel, setPanel] =
    useState<LandingPanel>(null);

  const [faqOpen, setFaqOpen] =
    useState<number | null>(0);

  const emailRef =
    useRef<HTMLInputElement>(null);

  const panelRef =
    useRef<HTMLElement>(null);

  const openPanel = (
    nextPanel: Exclude<LandingPanel, null>,
  ) => {
    setPanel(nextPanel);

    window.setTimeout(() => {
      panelRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

      if (nextPanel === "form") {
        emailRef.current?.focus();
      }
    }, 50);
  };

  const enterFromEmail = () => {
    if (!email.trim()) {
      openPanel("form");

      toast({
        title: "Email required",
        description:
          "Add your email to open your FILMFUND workspace.",
      });

      return;
    }

    writeStorage(
      "filmfund-email",
      email.trim(),
    );

    toast({
      title: "Welcome to FILMFUND",
      description:
        "Opening your grant workspace.",
    });

    onEnter();
  };

  const scrollToFilmRoom = () => {
    document
      .getElementById("film-showcase")
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

    toast({
      title: "Film room opened",
      description:
        "Browse the uploaded films and scripts below.",
    });
  };

  const faqItems = [
    [
      "What should I prepare first?",
      "Start with a one-page treatment, a realistic budget, and a clear sentence about why the story matters now.",
    ],
    [
      "How does matching work?",
      "FILMFUND compares your profile, project details, budget, and eligibility against each opportunity.",
    ],
    [
      "Can I track applications?",
      "Yes. Apply from any grant card and the opportunity is added to your Application Tracker.",
    ],
  ];

  return (
    <main className="film-grain relative min-h-[100dvh] overflow-hidden bg-[#050608] text-white">
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute inset-0 h-full w-full object-cover opacity-45"
        data-testid="video-landing-film"
      >
        <source
          src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260809_012548_ef22562c-c0ae-4816-ad9d-f8922af4e6a7.mp4"
          type="video/mp4"
        />
      </video>

      <div
        className="absolute inset-0 bg-black/45"
        aria-hidden="true"
      />

      <header className="relative z-10 flex items-center justify-between px-5 py-5 md:px-12 md:py-7">
        <button
          onClick={() => onEnter("search")}
          data-testid="brand-landing"
          className="flex items-center gap-3 text-left"
        >
          <span className="grid h-9 w-9 place-items-center rounded-full border border-white/60 text-xs font-bold">
            FF
          </span>

          <span className="text-sm font-bold tracking-[0.24em]">
            FILMFUND
          </span>
        </button>

        <nav className="hidden items-center gap-7 text-xs text-white/75 lg:flex">
          <button
            onClick={() => onEnter("search")}
            data-testid="link-search-grants"
            className="hover:text-white"
          >
            Search Grants
          </button>

          <button
            onClick={() => openPanel("how")}
            data-testid="link-how-it-works"
            className="hover:text-white"
          >
            How It Works
          </button>

          <button
            onClick={() => openPanel("resources")}
            data-testid="link-resources"
            className="hover:text-white"
          >
            Resources
          </button>

          <button
            onClick={() => openPanel("pricing")}
            data-testid="link-pricing"
            className="hover:text-white"
          >
            Pricing
          </button>
        </nav>

        <button
          onClick={() => openPanel("form")}
          data-testid="button-enter-top"
          className="rounded-full bg-white px-4 py-2 text-[11px] font-bold uppercase tracking-[0.16em] text-black hover:bg-white/85"
        >
          Get Started
        </button>
      </header>

      <section className="relative z-10 mx-auto grid min-h-[calc(100dvh-86px)] max-w-[1440px] items-center gap-10 px-5 pb-12 pt-8 md:grid-cols-[1.08fr_0.92fr] md:px-12 md:pb-16">
        <div className="max-w-2xl">
          <p className="mono mb-6 text-[10px] uppercase tracking-[0.18em] text-white/60">
            The funding room for independent filmmakers
          </p>

          <h1 className="display max-w-2xl text-6xl leading-[0.92] tracking-[-0.045em] md:text-8xl">
            Discover film grants while you sleep
          </h1>

          <p className="mt-6 max-w-lg text-sm leading-6 text-white/70 md:text-base">
            Search smarter, match your scripts to real
            opportunities, and keep every application moving.
          </p>

          <form
            className="mt-8 flex max-w-lg flex-col gap-3 sm:flex-row"
            onSubmit={(event) => {
              event.preventDefault();
              enterFromEmail();
            }}
          >
            <input
              ref={emailRef}
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              type="email"
              placeholder="Your email address"
              data-testid="input-email"
              className="h-12 flex-1 rounded-full border border-white/20 bg-white/10 px-5 text-sm text-white outline-none placeholder:text-white/45 focus:border-white/60"
            />

            <button
              type="submit"
              data-testid="button-get-started-email"
              className="h-12 rounded-full bg-white px-6 text-sm font-bold text-black hover:bg-white/85"
            >
              Get Started
            </button>
          </form>

          <button
            type="button"
            onClick={scrollToFilmRoom}
            className="mt-5 flex items-center gap-2 text-left text-xs font-semibold text-white/65 transition hover:text-white"
            data-testid="button-film-room"
          >
            <Sparkles
              size={14}
              className="text-[#95c9a3]"
            />
            Explore the film room
            <ArrowDownUp size={13} />
          </button>
        </div>

        <div className="grid gap-4 md:justify-self-end">
          <div className="glass-card max-w-md rounded-3xl p-6 md:p-8">
            <p className="mono text-[10px] uppercase tracking-[0.16em] text-white/55">
              A growing signal
            </p>

            <p className="silkscreen mt-5 text-5xl text-white md:text-7xl">
              48,000+
            </p>

            <p className="mt-4 max-w-xs text-sm leading-6 text-white/70">
              Filmmakers discover real grants daily through
              FILMFUND
            </p>
          </div>

          <div className="glass-card max-w-md rounded-3xl p-6 md:p-8">
            <div className="flex items-center gap-3">
              <span className="grid h-10 w-10 place-items-center rounded-full bg-[#95c9a3] text-sm font-bold text-[#102016]">
                M
              </span>

              <div>
                <p className="text-sm font-semibold">
                  Munira Mohammed
                </p>

                <p className="text-xs text-white/55">
                  Independent Filmmaker, Ghana
                </p>
              </div>
            </div>

            <p className="mt-5 text-sm leading-6 text-white/80">
              “FILMFUND saved me weeks of searching. Found 15
              grants matching my drama scripts in minutes.”
            </p>
          </div>
        </div>
      </section>

      {panel && (
        <section
          ref={panelRef}
          id={`landing-${panel}`}
          className="relative z-10 mx-auto max-w-[1440px] px-5 pb-16 md:px-12"
          aria-live="polite"
        >
          <div className="rounded-3xl border border-white/20 bg-black/55 p-6 shadow-2xl backdrop-blur-2xl md:p-10">
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="mono text-[10px] uppercase tracking-[0.16em] text-white/55">
                  FILMFUND /{" "}
                  {panel === "form"
                    ? "Start here"
                    : panel === "how"
                      ? "The process"
                      : panel === "resources"
                        ? "Reading room"
                        : "Keep the thread"}
                </p>

                <h2 className="display mt-3 text-3xl text-white md:text-5xl">
                  {panel === "form"
                    ? "Open your funding room."
                    : panel === "how"
                      ? "A clearer path to yes."
                      : panel === "resources"
                        ? "Answers for the next step."
                        : "Keep every application moving."}
                </h2>
              </div>

              <button
                type="button"
                onClick={() => setPanel(null)}
                className="rounded-full border border-white/20 p-2 text-white/70 hover:bg-white/10 hover:text-white"
                aria-label="Close section"
              >
                <X size={18} />
              </button>
            </div>

            {panel === "form" && (
              <form
                className="mt-8 max-w-2xl"
                onSubmit={(event) => {
                  event.preventDefault();
                  enterFromEmail();
                }}
              >
                <p className="max-w-xl text-sm leading-6 text-white/70">
                  Start with your email and FILMFUND will open a
                  personal workspace for your grant search,
                  profile, saved opportunities, and application
                  tracker.
                </p>

                <div className="mt-5 flex flex-col gap-3 sm:flex-row">
                  <input
                    value={email}
                    onChange={(event) =>
                      setEmail(event.target.value)
                    }
                    type="email"
                    required
                    placeholder="Your email address"
                    className="h-12 flex-1 rounded-full border border-white/20 bg-white/10 px-5 text-sm text-white outline-none placeholder:text-white/45 focus:border-white/60"
                    data-testid="input-landing-form-email"
                  />

                  <button
                    type="submit"
                    className="h-12 rounded-full bg-white px-6 text-sm font-bold text-black hover:bg-white/85"
                    data-testid="button-landing-form-submit"
                  >
                    Open workspace
                  </button>
                </div>
              </form>
            )}

            {panel === "how" && (
              <div className="mt-8 grid gap-4 md:grid-cols-3">
                {[
                  [
                    "01",
                    "Tell us about the work",
                    "Your profile and project budgets sharpen every match.",
                  ],
                  [
                    "02",
                    "Search the live signal",
                    "Browse current grants, fellowships, and finishing funds in one room.",
                  ],
                  [
                    "03",
                    "Move from match to submit",
                    "Save, compare, apply, and track each opportunity without losing the thread.",
                  ],
                ].map(
                  ([number, title, description]) => (
                    <div
                      key={number}
                      className="rounded-2xl border border-white/15 bg-white/5 p-5"
                    >
                      <span className="mono text-sm text-[#95c9a3]">
                        {number}
                      </span>

                      <h3 className="mt-8 text-lg font-bold text-white">
                        {title}
                      </h3>

                      <p className="mt-2 text-sm leading-6 text-white/60">
                        {description}
                      </p>
                    </div>
                  ),
                )}

                <button
                  type="button"
                  onClick={() => onEnter("search")}
                  className="mt-2 w-fit rounded-full bg-white px-5 py-3 text-xs font-bold uppercase tracking-[0.12em] text-black hover:bg-white/85"
                  data-testid="button-how-it-works-search"
                >
                  Start searching
                </button>
              </div>
            )}

            {panel === "resources" && (
              <div className="mt-8 grid gap-8 md:grid-cols-[0.8fr_1.2fr]">
                <div>
                  <p className="text-sm leading-7 text-white/70">
                    Grant applications get lighter when the
                    process is visible. Browse the workspace
                    resources for practical guidance, trusted
                    links, and answers to common questions.
                  </p>

                  <button
                    type="button"
                    onClick={() => onEnter("resources")}
                    className="mt-6 rounded-full bg-white px-5 py-3 text-xs font-bold uppercase tracking-[0.12em] text-black hover:bg-white/85"
                    data-testid="button-resources-workspace"
                  >
                    Open resources
                  </button>
                </div>

                <div className="divide-y divide-white/15 rounded-2xl border border-white/15">
                  {faqItems.map(
                    ([question, answer], index) => (
                      <div
                        key={question}
                        className="p-4"
                      >
                        <button
                          type="button"
                          onClick={() =>
                            setFaqOpen(
                              faqOpen === index
                                ? null
                                : index,
                            )
                          }
                          className="flex w-full items-center justify-between gap-4 text-left text-sm font-semibold text-white"
                          data-testid={`button-landing-faq-${index}`}
                        >
                          {question}

                          <span className="text-white/50">
                            {faqOpen === index ? "−" : "+"}
                          </span>
                        </button>

                        {faqOpen === index && (
                          <p className="mt-3 text-sm leading-6 text-white/60">
                            {answer}
                          </p>
                        )}
                      </div>
                    ),
                  )}
                </div>
              </div>
            )}

            {panel === "pricing" && (
              <div className="mt-8 grid gap-6 md:grid-cols-[1fr_auto] md:items-end">
                <div>
                  <p className="max-w-2xl text-sm leading-7 text-white/70">
                    No complicated plans here. FILMFUND is built
                    around one focused workflow: discover
                    opportunities, make an informed decision,
                    then keep the application moving.
                  </p>

                  <div className="mt-6 grid gap-3 sm:grid-cols-3">
                    {[
                      "Submitted",
                      "Pending",
                      "Awarded",
                    ].map((status) => (
                      <div
                        key={status}
                        className="rounded-xl border border-white/15 bg-white/5 p-4"
                      >
                        <p className="text-xs font-bold text-white">
                          {status}
                        </p>

                        <p className="mt-2 text-[11px] text-white/55">
                          Tracked in your room
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => onEnter("tracker")}
                  className="rounded-full bg-white px-5 py-3 text-xs font-bold uppercase tracking-[0.12em] text-black hover:bg-white/85"
                  data-testid="button-pricing-tracker"
                >
                  Open application tracker
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      <section
        id="film-showcase"
        className="relative z-10 mx-auto max-w-[1440px] scroll-mt-8 px-5 pb-20 md:px-12"
        aria-labelledby="film-showcase-title"
      >
        <div className="mb-8 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="mono text-[10px] uppercase tracking-[0.16em] text-[#95c9a3]">
              The film room
            </p>

            <h2
              id="film-showcase-title"
              className="display mt-3 text-4xl text-white md:text-6xl"
            >
              Work worth backing.
            </h2>

            <p className="mt-4 max-w-xl text-sm leading-6 text-white/60">
              Watch the short films, then open the scripts
              behind the work. Everything stays in the same dark,
              quiet room.
            </p>
          </div>

          <span className="mono text-[10px] uppercase tracking-[0.14em] text-white/40">
            3 films / 4 scripts
          </span>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          {showcaseVideos.map((video) => (
            <article
              key={video.title}
              className="overflow-hidden rounded-2xl border border-white/15 bg-white/[0.06] shadow-2xl backdrop-blur-md"
              data-testid={`showcase-video-${video.title}`}
            >
              <video
                controls
                playsInline
                preload="metadata"
                className="aspect-video w-full bg-black object-cover"
                aria-label={`Play ${video.title}`}
              >
                <source
                  src={video.source}
                  type="video/mp4"
                />
                Your browser does not support embedded video.
              </video>

              <div className="p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-lg font-semibold text-white">
                      {video.title}
                    </p>

                    <p className="mt-1 text-xs text-white/50">
                      {video.type}
                    </p>
                  </div>

                  <span className="rounded-full border border-white/15 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-white/55">
                    {video.label}
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>

        <div className="mt-16 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="mono text-[10px] uppercase tracking-[0.16em] text-[#95c9a3]">
              The script shelf
            </p>

            <h2 className="display mt-3 text-4xl text-white md:text-5xl">
              Read the next frame.
            </h2>
          </div>

          <p className="max-w-md text-sm leading-6 text-white/55">
            Download a PDF to read offline, share with your team,
            or bring into your next funding conversation.
          </p>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {showcaseScripts.map((script) => (
            <article
              key={script.title}
              className="group rounded-2xl border border-white/15 bg-white/[0.06] p-5 transition hover:-translate-y-1 hover:border-[#95c9a3]/60"
              data-testid={`showcase-script-${script.title}`}
            >
              <div className="flex items-start justify-between gap-3">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#95c9a3]/15 text-[#95c9a3]">
                  <FileText size={18} />
                </span>

                <span className="mono text-[9px] uppercase text-white/35">
                  PDF
                </span>
              </div>

              <h3 className="display mt-8 text-2xl text-white">
                {script.title}
              </h3>

              <p className="mt-2 text-xs leading-5 text-white/50">
                {script.type}
              </p>

              <a
                href={script.source}
                download
                onClick={() =>
                  toast({
                    title: "Script download started",
                    description: `${script.title} is ready to read offline.`,
                  })
                }
                className="mt-7 flex items-center justify-between rounded-lg border border-white/15 px-3 py-3 text-xs font-bold text-white transition hover:border-[#95c9a3]/60 hover:bg-white/10"
                data-testid={`download-script-${script.title}`}
              >
                Download script
                <Download size={14} />
              </a>

              <p className="mt-3 text-[10px] uppercase tracking-[0.08em] text-white/35">
                {script.meta}
              </p>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}

/* =========================================================
   SHELL
========================================================= */

function Shell({
  active,
  setActive,
  profile,
  savedCount,
  children,
  onTheme,
  dark,
  onLanding,
}: {
  active: Tab;
  setActive: (tab: Tab) => void;
  profile: Profile;
  savedCount: number;
  children: ReactNode;
  onTheme: () => void;
  dark: boolean;
  onLanding: () => void;
}) {
  const [mobileNav, setMobileNav] =
    useState(false);

  return (
    <div className="film-grain min-h-[100dvh] bg-background text-foreground">
      <aside
        className={`fixed inset-y-0 left-0 z-30 flex w-[254px] flex-col border-r border-sidebar-border bg-sidebar px-5 py-6 text-sidebar-foreground transition-transform md:translate-x-0 ${mobileNav
          ? "translate-x-0"
          : "-translate-x-full"
          }`}
      >
        <div className="flex items-center justify-between">
          <button
            onClick={onLanding}
            data-testid="button-brand-home"
            className="flex items-center gap-3"
          >
            <span className="grid h-8 w-8 place-items-center rounded-full border border-sidebar-primary/50 text-xs font-bold text-sidebar-primary">
              FF
            </span>

            <span className="text-sm font-bold tracking-[0.22em]">
              FILMFUND
            </span>
          </button>

          <button
            onClick={() => setMobileNav(false)}
            className="md:hidden"
            data-testid="button-close-mobile-nav"
          >
            <X size={18} />
          </button>
        </div>

        <p className="mono mt-12 text-[9px] uppercase tracking-[0.18em] text-sidebar-foreground/45">
          Your room
        </p>

        <nav className="mt-3 space-y-1">
          {tabs.map(
            ({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => {
                  setActive(id);
                  setMobileNav(false);
                }}
                data-testid={`nav-${id}`}
                className={`flex w-full items-center gap-3 rounded-lg px-3 py-3 text-left text-sm transition ${active === id
                  ? "bg-sidebar-accent text-sidebar-primary"
                  : "text-sidebar-foreground/65 hover:bg-sidebar-accent/70 hover:text-sidebar-foreground"
                  }`}
              >
                <Icon
                  size={17}
                  strokeWidth={1.7}
                />

                <span>{label}</span>

                {id === "saved" && (
                  <span className="ml-auto rounded-full bg-sidebar-primary/15 px-2 py-0.5 text-[10px] text-sidebar-primary">
                    {savedCount}
                  </span>
                )}
              </button>
            ),
          )}
        </nav>

        <div className="mt-auto border-t border-sidebar-border pt-5">
          <button
            onClick={() => setActive("profile")}
            data-testid="button-profile-card"
            className="flex w-full items-center gap-3 rounded-lg p-2 text-left hover:bg-sidebar-accent"
          >
            <span className="grid h-9 w-9 place-items-center rounded-full bg-sidebar-primary text-sm font-bold text-sidebar-primary-foreground">
              {profile.name
                .split(" ")
                .map((n) => n[0])
                .join("")
                .slice(0, 2)}
            </span>

            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold">
                {profile.name}
              </span>

              <span className="mono block text-[9px] uppercase text-sidebar-foreground/45">
                {profile.location}
              </span>
            </span>

            <Settings2
              className="ml-auto shrink-0 text-sidebar-foreground/45"
              size={15}
            />
          </button>
        </div>
      </aside>

      {mobileNav && (
        <button
          aria-label="Close navigation"
          onClick={() => setMobileNav(false)}
          className="fixed inset-0 z-20 bg-black/30 md:hidden"
          data-testid="button-overlay-close"
        />
      )}

      <div className="md:pl-[254px]">
        <header className="sticky top-0 z-10 flex h-[70px] items-center justify-between border-b border-border/80 bg-background/90 px-5 backdrop-blur-md md:px-10">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileNav(true)}
              className="md:hidden"
              data-testid="button-open-mobile-nav"
            >
              <Menu size={20} />
            </button>

            <div>
              <p className="mono text-[9px] uppercase tracking-[0.17em] text-muted-foreground">
                Good morning,{" "}
                {profile.name.split(" ")[0]}
              </p>

              <p className="display mt-0.5 text-xl">
                {
                  tabs.find(
                    (tab) => tab.id === active,
                  )?.label
                }
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onTheme}
              title="Toggle theme"
              data-testid="button-toggle-theme"
              className="rounded-full p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              {dark ? (
                <Sun size={17} />
              ) : (
                <Moon size={17} />
              )}
            </button>

            <button
              onClick={() =>
                window.alert(
                  "You’re all caught up. FILMFUND will flag new matches after your next search.",
                )
              }
              data-testid="button-notifications"
              className="relative rounded-full p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              <Bell size={17} />

              <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-accent" />
            </button>
          </div>
        </header>

        <main className="mx-auto max-w-[1480px] px-5 py-7 md:px-10 md:py-10">
          {children}
        </main>
      </div>
    </div>
  );
}

/* =========================================================
   SEARCH PAGE
========================================================= */

function SearchPage({
  saved,
  setSaved,
  applications,
  setApplications,
}: {
  saved: Grant[];
  setSaved: (grants: Grant[]) => void;
  applications: Application[];
  setApplications: (
    applications: Application[],
  ) => void;
}) {
  const [query, setQuery] =
    useState("independent film");

  const [submitted, setSubmitted] =
    useState("independent film");

  const [genre, setGenre] = useState("");
  const [location, setLocation] =
    useState("");
  const [budget, setBudget] =
    useState("");

  const [eligibility, setEligibility] =
    useState("");

  const [compare, setCompare] =
    useState<string[]>([]);

  const [showFilters, setShowFilters] =
    useState(false);

  const [notice, setNotice] =
    useState("");

  const [sortBy, setSortBy] =
    useState<SortBy>("match");

  const [applicationGrant, setApplicationGrant] =
    useState<Grant | null>(null);

  const [applicationNote, setApplicationNote] =
    useState("");

  const [detailsGrant, setDetailsGrant] =
    useState<Grant | null>(null);

  const params = useMemo(
    () => ({
      q: submitted,
      genre:
        genre || undefined,
      location:
        location || undefined,
      budget:
        budget
          ? Number(budget)
          : undefined,
    }),
    [
      submitted,
      genre,
      location,
      budget,
    ],
  );

  const search = useSearchGrants(
    params,
    submitted.length >= 2,
  );

  const live = search.data;

  const allGrants =
    live && live.length > 0
      ? live
      : fallbackGrants;

  const grants = useMemo(() => {
    const filtered =
      allGrants.filter((grant) => {
        if (!eligibility) {
          return true;
        }

        return eligibility === "women"
          ? grant.eligibility
            .toLowerCase()
            .includes("women")
          : grant.eligibility
            .toLowerCase()
            .includes("emerging") ||
          grant.eligibility
            .toLowerCase()
            .includes("first");
      });

    return filtered.sort(
      (left, right) => {
        if (sortBy === "deadline") {
          if (
            left.deadline === "Rolling"
          ) {
            return 1;
          }

          if (
            right.deadline === "Rolling"
          ) {
            return -1;
          }

          return (
            new Date(
              left.deadline,
            ).getTime() -
            new Date(
              right.deadline,
            ).getTime()
          );
        }

        if (sortBy === "funding") {
          return (
            parseFundingValue(
              right.funding,
            ) -
            parseFundingValue(
              left.funding,
            )
          );
        }

        return (
          right.matchScore -
          left.matchScore
        );
      },
    );
  }, [
    allGrants,
    eligibility,
    sortBy,
  ]);

  const history = readStorage<string[]>(
    "filmfund-history",
    [],
  );

  const isFallback =
    !live || live.length === 0;

  const showNotice = (
    message: string,
  ) => {
    setNotice(message);

    window.setTimeout(
      () => setNotice(""),
      2600,
    );
  };

  const runSearch = () => {
    const nextQuery =
      query.trim();

    if (nextQuery.length < 2) {
      showNotice(
        "Enter at least two characters to search.",
      );

      toast({
        title:
          "Search needs more detail",
        description:
          "Try a grant type, genre, or funding stage.",
      });

      return;
    }

    setSubmitted(nextQuery);

    writeStorage(
      "filmfund-history",
      [
        nextQuery,
        ...history.filter(
          (item) =>
            item !== nextQuery,
        ),
      ].slice(0, 5),
    );

    showNotice(
      `Searching for “${nextQuery}”…`,
    );

    toast({
      title:
        "Grant search submitted",
      description: `Looking for opportunities matching “${nextQuery}”.`,
    });
  };

  const toggleSaved = (
    grant: Grant,
  ) => {
    const isSaved =
      saved.some(
        (item) =>
          item.id === grant.id,
      );

    setSaved(
      isSaved
        ? saved.filter(
          (item) =>
            item.id !== grant.id,
        )
        : [...saved, grant],
    );

    showNotice(
      isSaved
        ? "Removed from saved grants."
        : "Saved to your shortlist.",
    );

    toast({
      title: isSaved
        ? "Removed from shortlist"
        : "Saved to shortlist",
      description:
        grant.title,
    });
  };

  const apply = (
    grant: Grant,
  ) => {
    setApplicationGrant(
      grant,
    );

    setApplicationNote("");

    showNotice(
      `Application form ready for ${grant.title}.`,
    );

    toast({
      title:
        "Application form opened",
      description: `${grant.organization} details are pre-filled.`,
    });
  };

  const submitApplication =
    () => {
      if (!applicationGrant) {
        return;
      }

      if (
        !applications.some(
          (application) =>
            application.id ===
            applicationGrant.id,
        )
      ) {
        setApplications([
          ...applications,
          {
            id: applicationGrant.id,
            title:
              applicationGrant.title,
            organization:
              applicationGrant.organization,
            funding:
              applicationGrant.funding,
            status: "Submitted",
            date: new Date()
              .toISOString()
              .slice(0, 10),
          },
        ]);
      }

      setApplicationGrant(
        null,
      );

      showNotice(
        "Application added to your tracker.",
      );

      toast({
        title:
          "Application tracked",
        description:
          applicationNote
            ? "Your note was saved for this session."
            : "You can update its status from the tracker.",
      });
    };

  const exportResults = (
    format: "csv" | "json",
  ) => {
    if (format === "json") {
      downloadFile(
        "filmfund-grants.json",
        JSON.stringify(
          grants,
          null,
          2,
        ),
        "application/json",
      );
    } else {
      downloadFile(
        "filmfund-grants.csv",
        [
          "Title,Organization,Funding,Deadline,Category,Match Score,Details",
          ...grants.map(
            (grant) =>
              `"${grant.title}","${grant.organization}","${grant.funding}","${grant.deadline}","${grant.category}",${grant.matchScore},"${grant.url}"`,
          ),
        ].join("\n"),
        "text/csv",
      );
    }

    showNotice(
      `Results exported as ${format.toUpperCase()}.`,
    );

    toast({
      title:
        "Export ready",
      description: `Your ${format.toUpperCase()} grant list was downloaded.`,
    });
  };

  const cycleSort = () => {
    const nextSort: SortBy =
      sortBy === "match"
        ? "deadline"
        : sortBy === "deadline"
          ? "funding"
          : "match";

    setSortBy(nextSort);

    const label =
      nextSort === "match"
        ? "profile match"
        : nextSort;

    showNotice(
      `Sorted by ${label}.`,
    );

    toast({
      title:
        "Results sorted",
      description: `Showing the strongest results by ${label}.`,
    });
  };

  const toggleCompare = (
    grant: Grant,
  ) => {
    if (
      compare.includes(
        grant.id,
      )
    ) {
      setCompare(
        compare.filter(
          (item) =>
            item !== grant.id,
        ),
      );

      showNotice(
        `${grant.title} removed from comparison.`,
      );

      toast({
        title:
          "Comparison updated",
        description: `${grant.title} was removed.`,
      });

      return;
    }

    if (compare.length >= 3) {
      showNotice(
        "Compare up to three grants at a time.",
      );

      toast({
        title:
          "Comparison is full",
        description:
          "Remove a grant before adding another.",
      });

      return;
    }

    setCompare([
      ...compare,
      grant.id,
    ]);

    showNotice(
      `${grant.title} added to comparison.`,
    );

    toast({
      title:
        "Comparison updated",
      description: `${compare.length + 1
        } grant${compare.length === 0
          ? ""
          : "s"
        } selected.`,
    });
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
            The room is open
          </p>

          <h1 className="display mt-2 text-4xl tracking-[-0.025em] md:text-5xl">
            Find your next yes.
          </h1>

          <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">
            Search current film grants,
            fellowships, and finishing
            funds. Your profile shapes the
            signal.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="h-2 w-2 rounded-full bg-primary" />
          {search.isError
            ? "Using curated results"
            : "Live search connected"}
        </div>
      </div>

      <form
        className="rounded-2xl border border-border bg-card p-3 shadow-sm md:p-4"
        onSubmit={(event) => {
          event.preventDefault();
          runSearch();
        }}
      >
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="relative flex-1">
            <Search
              className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground"
              size={18}
            />

            <input
              value={query}
              onChange={(event) =>
                setQuery(
                  event.target.value,
                )
              }
              data-testid="input-grant-search"
              className="h-12 w-full rounded-xl border border-input bg-background pl-11 pr-4 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/15"
              placeholder="Try “documentary finishing fund”"
            />
          </div>

          <button
            type="submit"
            data-testid="button-search-grants"
            className="h-12 rounded-xl bg-primary px-6 text-sm font-bold text-primary-foreground transition hover:opacity-90"
          >
            Search grants
          </button>

          <button
            type="button"
            onClick={() =>
              setShowFilters(
                !showFilters,
              )
            }
            data-testid="button-toggle-filters"
            className="flex h-12 items-center justify-center gap-2 rounded-xl border border-input px-4 text-sm font-semibold transition hover:bg-muted"
          >
            <SlidersHorizontal
              size={16}
            />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="mt-3 grid gap-3 border-t border-border pt-3 md:grid-cols-4">
            <label className="text-xs font-semibold">
              Genre

              <select
                value={genre}
                onChange={(event) =>
                  setGenre(
                    event.target.value,
                  )
                }
                data-testid="select-genre"
                className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm font-normal"
              >
                <option value="">
                  Any genre
                </option>
                <option>
                  Narrative
                </option>
                <option>
                  Documentary
                </option>
                <option>
                  Experimental
                </option>
                <option>
                  International
                </option>
              </select>
            </label>

            <label className="text-xs font-semibold">
              Location

              <select
                value={location}
                onChange={(event) =>
                  setLocation(
                    event.target.value,
                  )
                }
                data-testid="select-location"
                className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm font-normal"
              >
                <option value="">
                  Any location
                </option>
                <option>Ghana</option>
                <option>
                  United States
                </option>
                <option>
                  North America
                </option>
                <option>
                  Global
                </option>
                <option>
                  Los Angeles
                </option>
              </select>
            </label>

            <label className="text-xs font-semibold">
              Maximum budget

              <select
                value={budget}
                onChange={(event) =>
                  setBudget(
                    event.target.value,
                  )
                }
                data-testid="select-budget"
                className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm font-normal"
              >
                <option value="">
                  Any budget
                </option>
                <option value="25000">
                  $25,000
                </option>
                <option value="50000">
                  $50,000
                </option>
                <option value="100000">
                  $100,000
                </option>
              </select>
            </label>

            <label className="text-xs font-semibold">
              Eligibility

              <select
                value={eligibility}
                onChange={(event) =>
                  setEligibility(
                    event.target.value,
                  )
                }
                data-testid="select-eligibility"
                className="mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm font-normal"
              >
                <option value="">
                  Any requirements
                </option>

                <option value="women">
                  Women-led projects
                </option>

                <option value="emerging">
                  Emerging / first-time
                </option>
              </select>
            </label>
          </div>
        )}
      </form>

      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">
              {grants.length} opportunities
            </span>

            <span>·</span>

            <span>
              Sorted by{" "}
              {sortBy === "match"
                ? "profile match"
                : sortBy}
            </span>

            {isFallback && (
              <span className="rounded-full bg-accent/10 px-2 py-1 text-accent">
                Curated preview
              </span>
            )}
          </div>

          <div
            className="mt-3 flex flex-wrap items-center gap-2"
            data-testid="list-search-history"
          >
            <span className="mono text-[9px] uppercase text-muted-foreground">
              Recent:
            </span>

            {history.length ? (
              history.map(
                (item) => (
                  <button
                    key={item}
                    onClick={() => {
                      setQuery(item);
                      setSubmitted(item);
                    }}
                    data-testid={`history-${item}`}
                    className="rounded-full border border-border px-2.5 py-1 text-[11px] hover:border-primary"
                  >
                    {item}
                  </button>
                ),
              )
            ) : (
              <span className="text-xs text-muted-foreground">
                Your last five searches
                will appear here.
              </span>
            )}
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={cycleSort}
            data-testid="button-sort-grants"
            className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
          >
            <ArrowDownUp size={14} />
            Sort:{" "}
            {sortBy === "match"
              ? "Match"
              : sortBy === "deadline"
                ? "Deadline"
                : "Funding"}
          </button>

          <button
            type="button"
            onClick={() =>
              exportResults("csv")
            }
            data-testid="button-export-csv"
            className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
          >
            <Download size={14} />
            CSV
          </button>

          <button
            type="button"
            onClick={() =>
              exportResults("json")
            }
            data-testid="button-export-json"
            className="flex items-center gap-2 rounded-lg border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
          >
            <Download size={14} />
            JSON
          </button>

          <button
            type="button"
            onClick={() => {
              setCompare([]);

              showNotice(
                "Comparison cleared.",
              );

              toast({
                title:
                  "Comparison cleared",
                description:
                  "You can start a new comparison anytime.",
              });
            }}
            disabled={!compare.length}
            data-testid="button-clear-comparison"
            className="rounded-lg px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted disabled:opacity-40"
          >
            Clear compare
          </button>
        </div>
      </div>

      {notice && (
        <div
          role="status"
          aria-live="polite"
          className="rounded-xl border border-primary/30 bg-primary/10 px-4 py-3 text-sm font-semibold text-primary"
          data-testid="status-action-notice"
        >
          {notice}
        </div>
      )}

      {search.isLoading && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="skeleton h-64 rounded-2xl" />
          <div className="skeleton h-64 rounded-2xl" />
        </div>
      )}

      {search.isError && (
        <div
          className="rounded-2xl border border-accent/30 bg-accent/5 p-6"
          data-testid="status-search-error"
        >
          <p className="font-semibold">
            The live search is taking a pause.
          </p>

          <p className="mt-1 text-sm text-muted-foreground">
            Here is a curated set while we
            reconnect. Try your search again
            in a moment.
          </p>

          <button
            onClick={() =>
              search.refetch()
            }
            data-testid="button-retry-search"
            className="mt-4 rounded-lg bg-primary px-4 py-2 text-xs font-bold text-primary-foreground"
          >
            Retry live search
          </button>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        {grants.map(
          (grant, index) => (
            <GrantCard
              key={grant.id}
              grant={grant}
              saved={saved.some(
                (item) =>
                  item.id === grant.id,
              )}
              comparing={compare.includes(
                grant.id,
              )}
              onSave={() =>
                toggleSaved(grant)
              }
              onCompare={() =>
                toggleCompare(grant)
              }
              onApply={() =>
                apply(grant)
              }
              onDetails={() =>
                setDetailsGrant(
                  grant,
                )
              }
              delay={index}
            />
          ),
        )}
      </div>

      {compare.length > 1 && (
        <div
          className="sticky bottom-4 z-10 rounded-2xl border border-primary/30 bg-card/95 p-4 shadow-lg backdrop-blur"
          data-testid="panel-comparison"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-bold">
                Comparison tray
              </p>

              <p className="text-xs text-muted-foreground">
                Up to three opportunities,
                side by side.
              </p>
            </div>

            <button
              onClick={() =>
                setCompare([])
              }
              data-testid="button-close-comparison"
            >
              <X size={16} />
            </button>
          </div>

          <div className="mt-3 grid gap-2 md:grid-cols-3">
            {grants
              .filter((grant) =>
                compare.includes(
                  grant.id,
                ),
              )
              .map((grant) => (
                <div
                  key={grant.id}
                  className="rounded-lg bg-muted p-3"
                >
                  <p className="truncate text-xs font-bold">
                    {grant.title}
                  </p>

                  <p className="mt-1 text-[11px] text-muted-foreground">
                    {grant.funding} ·{" "}
                    {grant.matchScore}%
                    match
                  </p>
                </div>
              ))}
          </div>
        </div>
      )}

      {applicationGrant && (
        <div
          className="fixed inset-0 z-40 grid place-items-center bg-black/55 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="application-form-title"
        >
          <form
            onSubmit={(event) => {
              event.preventDefault();
              submitApplication();
            }}
            className="w-full max-w-xl rounded-2xl border border-border bg-card p-6 shadow-2xl md:p-8"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
                  Application form
                </p>

                <h2
                  id="application-form-title"
                  className="display mt-2 text-3xl"
                >
                  Ready to apply.
                </h2>

                <p className="mt-2 text-sm text-muted-foreground">
                  Review the pre-filled grant
                  details, add an optional note,
                  and send it to your tracker.
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  setApplicationGrant(
                    null,
                  )
                }
                className="rounded-full p-2 text-muted-foreground hover:bg-muted"
                aria-label="Close application form"
              >
                <X size={18} />
              </button>
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <label className="text-xs font-bold sm:col-span-2">
                Grant

                <input
                  value={
                    applicationGrant.title
                  }
                  readOnly
                  className="mt-2 h-11 w-full rounded-lg border border-input bg-muted px-3 text-sm font-normal"
                />
              </label>

              <label className="text-xs font-bold">
                Organization

                <input
                  value={
                    applicationGrant.organization
                  }
                  readOnly
                  className="mt-2 h-11 w-full rounded-lg border border-input bg-muted px-3 text-sm font-normal"
                />
              </label>

              <label className="text-xs font-bold">
                Funding

                <input
                  value={
                    applicationGrant.funding
                  }
                  readOnly
                  className="mt-2 h-11 w-full rounded-lg border border-input bg-muted px-3 text-sm font-normal"
                />
              </label>

              <label className="text-xs font-bold sm:col-span-2">
                Application note

                <textarea
                  value={applicationNote}
                  onChange={(event) =>
                    setApplicationNote(
                      event.target.value,
                    )
                  }
                  placeholder="What will you remember about this opportunity?"
                  className="mt-2 min-h-24 w-full rounded-lg border border-input bg-background p-3 text-sm font-normal outline-none focus:border-primary"
                  data-testid="input-application-note"
                />
              </label>
            </div>

            <div className="mt-7 flex justify-end gap-3 border-t border-border pt-5">
              <button
                type="button"
                onClick={() =>
                  setApplicationGrant(
                    null,
                  )
                }
                className="rounded-lg px-4 py-2 text-sm font-semibold hover:bg-muted"
              >
                Cancel
              </button>

              <button
                type="submit"
                className="rounded-lg bg-primary px-5 py-2 text-sm font-bold text-primary-foreground hover:opacity-90"
                data-testid="button-submit-application"
              >
                Add to tracker
              </button>
            </div>
          </form>
        </div>
      )}

      {detailsGrant && (
        <GrantDetailsModal
          grant={detailsGrant}
          onClose={() =>
            setDetailsGrant(null)
          }
        />
      )}
    </div>
  );
}

/* =========================================================
   GRANT DETAILS
========================================================= */

function GrantDetailsModal({
  grant,
  onClose,
}: {
  grant: Grant;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-40 grid place-items-center bg-black/55 p-4 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="grant-details-title"
    >
      <div className="w-full max-w-2xl rounded-2xl border border-border bg-card p-6 shadow-2xl md:p-8">
        <div className="flex items-start justify-between gap-5">
          <div>
            <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
              Grant details
            </p>

            <h2
              id="grant-details-title"
              className="display mt-2 text-3xl"
            >
              {grant.title}
            </h2>

            <p className="mt-1 text-sm font-bold text-muted-foreground">
              {grant.organization}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-2 text-muted-foreground hover:bg-muted"
            aria-label="Close grant details"
          >
            <X size={18} />
          </button>
        </div>

        <p className="mt-6 text-sm leading-7 text-muted-foreground">
          {grant.description}
        </p>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          <div className="rounded-xl bg-muted p-4">
            <p className="mono text-[9px] uppercase text-muted-foreground">
              Funding
            </p>

            <p className="mt-2 text-sm font-bold">
              {grant.funding}
            </p>
          </div>

          <div className="rounded-xl bg-muted p-4">
            <p className="mono text-[9px] uppercase text-muted-foreground">
              Deadline
            </p>

            <p className="mt-2 text-sm font-bold">
              {grant.deadline ===
                "Rolling"
                ? "Rolling"
                : new Date(
                  grant.deadline,
                ).toLocaleDateString(
                  "en-US",
                  {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  },
                )}
            </p>
          </div>

          <div className="rounded-xl bg-muted p-4">
            <p className="mono text-[9px] uppercase text-muted-foreground">
              Trust score
            </p>

            <p className="mt-2 text-sm font-bold">
              {grant.trustScore} / 100
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-xl border border-primary/20 bg-primary/5 p-4">
          <p className="text-xs font-bold text-primary">
            Eligibility
          </p>

          <p className="mt-1 text-sm text-muted-foreground">
            {grant.eligibility}
          </p>
        </div>

        <div className="mt-7 flex flex-wrap justify-end gap-3 border-t border-border pt-5">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-semibold hover:bg-muted"
          >
            Close
          </button>

          <a
            href={grant.url}
            target="_blank"
            rel="noreferrer"
            onClick={() =>
              toast({
                title:
                  "Opening grant source",
                description:
                  "The official opportunity page opened in a new tab.",
              })
            }
            className="flex items-center gap-2 rounded-lg bg-primary px-5 py-2 text-sm font-bold text-primary-foreground hover:opacity-90"
            data-testid={`link-details-source-${grant.id}`}
          >
            Open official page
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   GRANT CARD
========================================================= */

function GrantCard({
  grant,
  saved,
  comparing,
  onSave,
  onCompare,
  onApply,
  onDetails,
  delay,
}: {
  grant: Grant;
  saved: boolean;
  comparing: boolean;
  onSave: () => void;
  onCompare: () => void;
  onApply: () => void;
  onDetails: () => void;
  delay: number;
}) {
  return (
    <article
      className="reveal group relative overflow-hidden rounded-2xl border border-border bg-card p-5 transition hover:-translate-y-0.5 hover:border-primary/50 hover:shadow-md md:p-6"
      style={{
        animationDelay: `${delay * 70}ms`,
      }}
      data-testid={`card-grant-${grant.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-primary/10 px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.08em] text-primary">
            {grant.category}
          </span>

          <span className="text-[11px] text-muted-foreground">
            {grant.location}
          </span>
        </div>

        <button
          onClick={onSave}
          data-testid={`button-save-${grant.id}`}
          className="rounded-full p-2 text-muted-foreground transition hover:bg-muted hover:text-primary"
          aria-label={
            saved
              ? `Remove ${grant.title} from saved grants`
              : `Save ${grant.title}`
          }
        >
          {saved ? (
            <BookmarkCheck
              size={18}
              className="text-primary"
            />
          ) : (
            <Bookmark size={18} />
          )}
        </button>
      </div>

      <h2 className="display mt-5 max-w-md text-2xl leading-tight">
        {grant.title}
      </h2>

      <p className="mt-1 text-xs font-bold text-muted-foreground">
        {grant.organization}
      </p>

      <p className="mt-4 line-clamp-2 text-sm leading-6 text-muted-foreground">
        {grant.description}
      </p>

      <div className="mt-5 grid grid-cols-2 gap-4 border-y border-border py-4">
        <div>
          <p className="mono text-[9px] uppercase text-muted-foreground">
            Funding
          </p>

          <p className="mt-1 text-sm font-bold">
            {grant.funding}
          </p>
        </div>

        <div>
          <p className="mono text-[9px] uppercase text-muted-foreground">
            Deadline
          </p>

          <p className="mt-1 text-sm font-bold">
            {grant.deadline ===
              "Rolling"
              ? "Rolling"
              : new Date(
                grant.deadline,
              ).toLocaleDateString(
                "en-US",
                {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                },
              )}
          </p>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="grid h-9 w-9 place-items-center rounded-full bg-accent/10 text-xs font-bold text-accent">
            {grant.matchScore}%
          </span>

          <div>
            <p className="text-xs font-bold">
              Budget match score
            </p>

            <p className="text-[10px] text-muted-foreground">
              Trust score{" "}
              {grant.trustScore} / 100
            </p>
          </div>
        </div>

        <span className="rounded-full bg-muted px-2.5 py-1 text-[10px] font-semibold text-muted-foreground">
          {grant.eligibility}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
        {grant.matchedScripts.length ? (
          <>
            <span className="font-semibold text-primary">
              Fits:
            </span>

            {grant.matchedScripts.map(
              (script) => (
                <span
                  key={script}
                  className="rounded-full border border-primary/20 px-2 py-1"
                >
                  {script}
                </span>
              ),
            )}
          </>
        ) : (
          <span>
            Script match pending profile review
          </span>
        )}
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-end gap-1 border-t border-border pt-4">
        <button
          type="button"
          onClick={onDetails}
          data-testid={`button-details-${grant.id}`}
          className="flex items-center gap-1 rounded-lg px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          Details
          <ExternalLink size={13} />
        </button>

        <button
          type="button"
          onClick={onCompare}
          data-testid={`button-compare-${grant.id}`}
          className={`rounded-lg px-3 py-2 text-xs font-semibold transition ${comparing
            ? "bg-primary text-primary-foreground"
            : "hover:bg-muted"
            }`}
        >
          {comparing ? (
            <Check
              size={14}
              className="mr-1 inline"
            />
          ) : null}
          Compare
        </button>

        <button
          type="button"
          onClick={onApply}
          data-testid={`button-apply-${grant.id}`}
          className="flex items-center gap-1 rounded-lg bg-secondary px-3 py-2 text-xs font-bold text-secondary-foreground transition hover:opacity-90"
        >
          <Send size={14} />
          Apply
        </button>
      </div>
    </article>
  );
}

/* =========================================================
   PROFILE
========================================================= */

function ProfilePage({
  profile,
  setProfile,
}: {
  profile: Profile;
  setProfile: (
    profile: Profile,
  ) => void;
}) {
  const [draft, setDraft] =
    useState(profile);

  const [savedNotice, setSavedNotice] =
    useState(false);

  const update = (
    key: keyof Profile,
    value: string,
  ) => {
    setDraft({
      ...draft,
      [key]: value,
    });
  };

  const save = () => {
    setProfile(draft);
    setSavedNotice(true);

    window.setTimeout(
      () => setSavedNotice(false),
      2200,
    );
  };

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
          Your point of view
        </p>

        <h1 className="display mt-2 text-4xl">
          Make the match sharper.
        </h1>

        <p className="mt-3 max-w-xl text-sm leading-6 text-muted-foreground">
          Keep your creative profile current so
          FILMFUND can connect the right room to
          the right project.
        </p>
      </div>

      <section className="rounded-2xl border border-border bg-card p-6 md:p-8">
        <div className="flex items-center gap-4 border-b border-border pb-6">
          <span className="grid h-14 w-14 place-items-center rounded-full bg-primary text-lg font-bold text-primary-foreground">
            MM
          </span>

          <div>
            <h2 className="display text-2xl">
              {draft.name}
            </h2>

            <p className="text-sm text-muted-foreground">
              {draft.level} filmmaker ·{" "}
              {draft.location}
            </p>
          </div>
        </div>

        <div className="mt-7 grid gap-5 md:grid-cols-2">
          {[
            ["name", "Name"],
            ["location", "Location"],
            ["level", "Career stage"],
            ["genres", "Genres"],
            [
              "budget",
              "Typical production budget",
            ],
            [
              "scripts",
              "Scripts in development",
            ],
          ].map(
            ([key, label]) => (
              <label
                key={key}
                className="text-xs font-bold"
              >
                {label}

                <input
                  value={
                    draft[
                    key as keyof Profile
                    ]
                  }
                  onChange={(event) =>
                    update(
                      key as keyof Profile,
                      event.target.value,
                    )
                  }
                  data-testid={`input-profile-${key}`}
                  className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm font-normal outline-none focus:border-primary"
                />
              </label>
            ),
          )}

          <label className="text-xs font-bold md:col-span-2">
            Production information

            <textarea
              value={draft.production}
              onChange={(event) =>
                update(
                  "production",
                  event.target.value,
                )
              }
              data-testid="input-profile-production"
              className="mt-2 min-h-24 w-full rounded-lg border border-input bg-background p-3 text-sm font-normal outline-none focus:border-primary"
            />
          </label>
        </div>

        <div className="mt-7 flex items-center justify-end gap-4 border-t border-border pt-5">
          {savedNotice && (
            <span className="flex items-center gap-1 text-xs font-bold text-primary">
              <Check size={14} />
              Profile saved
            </span>
          )}

          <button
            onClick={save}
            data-testid="button-save-profile"
            className="rounded-lg bg-primary px-5 py-3 text-sm font-bold text-primary-foreground transition hover:opacity-90"
          >
            Save profile
          </button>
        </div>
      </section>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="display text-2xl">
            Projects in the room
          </h2>

          <span className="mono text-[10px] uppercase text-muted-foreground">
            3 active scripts
          </span>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          {projectList.map(
            (project) => (
              <div
                key={project.title}
                className="rounded-xl border border-border bg-card p-5"
                data-testid={`card-script-${project.title}`}
              >
                <FileText
                  size={18}
                  className="text-primary"
                />

                <h3 className="display mt-5 text-2xl">
                  {project.title}
                </h3>

                <p className="mt-1 text-xs text-muted-foreground">
                  {project.genre}
                </p>

                <p className="mono mt-5 text-[10px] uppercase text-muted-foreground">
                  {project.budget} production budget
                </p>
              </div>
            ),
          )}
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   SAVED
========================================================= */

function SavedPage({
  saved,
  setSaved,
  setActive,
}: {
  saved: Grant[];
  setSaved: (
    grants: Grant[],
  ) => void;
  setActive: (tab: Tab) => void;
}) {
  const [detailsGrant, setDetailsGrant] =
    useState<Grant | null>(null);

  return (
    <div className="space-y-8">
      <div className="flex items-end justify-between">
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
            The shortlist
          </p>

          <h1 className="display mt-2 text-4xl">
            Saved grants.
          </h1>

          <p className="mt-3 text-sm text-muted-foreground">
            The opportunities worth a second
            look.
          </p>
        </div>

        <span className="mono text-xs text-muted-foreground">
          {saved.length
            .toString()
            .padStart(2, "0")}{" "}
          SAVED
        </span>
      </div>

      {saved.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border bg-card px-6 py-16 text-center">
          <Bookmark
            size={24}
            className="mx-auto text-primary"
          />

          <h2 className="display mt-4 text-2xl">
            No saved grants yet
          </h2>

          <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
            Save a grant from Search Grants when
            you find one worth pursuing.
          </p>

          <button
            onClick={() =>
              setActive("search")
            }
            data-testid="button-browse-grants"
            className="mt-6 rounded-lg bg-primary px-5 py-3 text-xs font-bold text-primary-foreground"
          >
            Browse grants
          </button>
        </div>
      ) : (
        <div className="grid gap-4 lg:grid-cols-2">
          {saved.map((grant) => (
            <GrantCard
              key={grant.id}
              grant={grant}
              saved
              comparing={false}
              onSave={() => {
                setSaved(
                  saved.filter(
                    (item) =>
                      item.id !==
                      grant.id,
                  ),
                );

                toast({
                  title:
                    "Grant removed",
                  description:
                    "The opportunity was removed from your shortlist.",
                });
              }}
              onCompare={() =>
                toast({
                  title:
                    "Open Search Grants to compare",
                  description:
                    "Comparison works from the live search results.",
                })
              }
              onApply={() => {
                setActive("tracker");

                toast({
                  title:
                    "Application tracker opened",
                  description:
                    "Open this opportunity from Search Grants to start a pre-filled application.",
                });
              }}
              onDetails={() =>
                setDetailsGrant(
                  grant,
                )
              }
              delay={0}
            />
          ))}
        </div>
      )}

      {detailsGrant && (
        <GrantDetailsModal
          grant={detailsGrant}
          onClose={() =>
            setDetailsGrant(null)
          }
        />
      )}
    </div>
  );
}

/* =========================================================
   TRACKER
========================================================= */

function TrackerPage({
  applications,
  setApplications,
}: {
  applications: Application[];
  setApplications: (
    applications: Application[],
  ) => void;
}) {
  const update = (
    id: string,
    status: Application["status"],
  ) => {
    setApplications(
      applications.map(
        (application) =>
          application.id === id
            ? {
              ...application,
              status,
            }
            : application,
      ),
    );
  };

  const exportTracker = () =>
    downloadFile(
      "filmfund-tracker.csv",
      [
        "Grant,Organization,Status,Date Applied",
        ...applications.map(
          (application) =>
            `"${application.title}","${application.organization}","${application.status}","${application.date}"`,
        ),
      ].join("\n"),
      "text/csv",
    );

  return (
    <div className="space-y-8">
      <div className="flex items-end justify-between">
        <div>
          <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
            Keep the thread
          </p>

          <h1 className="display mt-2 text-4xl">
            Application tracker.
          </h1>

          <p className="mt-3 text-sm text-muted-foreground">
            Track submitted, pending, and awarded
            opportunities in one place.
          </p>
        </div>

        <button
          onClick={exportTracker}
          data-testid="button-export-tracker"
          className="hidden items-center gap-2 rounded-lg border border-border px-3 py-2 text-xs font-bold hover:bg-muted md:flex"
        >
          <Download size={15} />
          Export
        </button>
      </div>

      {applications.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-border bg-card px-6 py-16 text-center">
          <ClipboardList
            size={24}
            className="mx-auto text-primary"
          />

          <h2 className="display mt-4 text-2xl">
            No applications tracked
          </h2>

          <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
            Apply to a grant from Search Grants and
            it will land here.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {applications.map(
            (application) => (
              <div
                key={application.id}
                className="rounded-2xl border border-border bg-card p-5"
                data-testid={`card-application-${application.id}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="display text-xl">
                      {application.title}
                    </h2>

                    <p className="mt-1 text-xs font-bold text-muted-foreground">
                      {application.organization}
                    </p>
                  </div>

                  <button
                    onClick={() =>
                      setApplications(
                        applications.filter(
                          (item) =>
                            item.id !==
                            application.id,
                        ),
                      )
                    }
                    data-testid={`button-delete-application-${application.id}`}
                    className="rounded-full p-2 text-muted-foreground hover:bg-muted hover:text-destructive"
                  >
                    <Trash2 size={15} />
                  </button>
                </div>

                <div className="mt-5 flex items-center justify-between border-t border-border pt-4">
                  <div>
                    <p className="mono text-[9px] uppercase text-muted-foreground">
                      Funding
                    </p>

                    <p className="mt-1 text-sm font-bold">
                      {application.funding}
                    </p>
                  </div>

                  <label className="text-right text-[10px] font-bold text-muted-foreground">
                    STATUS

                    <select
                      value={
                        application.status
                      }
                      onChange={(event) =>
                        update(
                          application.id,
                          event.target
                            .value as Application["status"],
                        )
                      }
                      data-testid={`select-status-${application.id}`}
                      className="mt-1 block rounded-lg border border-input bg-background px-2 py-2 text-xs font-bold text-foreground"
                    >
                      <option>
                        Submitted
                      </option>
                      <option>
                        Pending
                      </option>
                      <option>
                        Awarded
                      </option>
                    </select>
                  </label>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{
                        width: `${application.status ===
                          "Awarded"
                          ? 100
                          : application.status ===
                            "Pending"
                            ? 66
                            : 33
                          }%`,
                      }}
                    />
                  </div>

                  <span className="text-[10px] text-muted-foreground">
                    {application.date}
                  </span>
                </div>
              </div>
            ),
          )}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   BUDGET
========================================================= */

function BudgetPage() {
  const [values, setValues] =
    useState({
      production: "68000",
      crew: "18000",
      equipment: "14000",
    });

  const total =
    Object.values(values).reduce(
      (sum, value) =>
        sum + Number(value || 0),
      0,
    );

  const range =
    total <= 50000
      ? "Good match"
      : total <= 100000
        ? "Mid-range"
        : "Large grants needed";

  const matchedRanges =
    total <= 50000
      ? ["$10k–$50k"]
      : total <= 100000
        ? [
          "$50k–$100k",
          "$10k–$50k",
        ]
        : ["$100k+"];

  return (
    <div className="max-w-5xl space-y-8">
      <div>
        <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
          Know your number
        </p>

        <h1 className="display mt-2 text-4xl">
          Budget calculator.
        </h1>

        <p className="mt-3 text-sm text-muted-foreground">
          See which grant ranges can realistically
          move your film forward.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-[1.25fr_0.75fr]">
        <section className="rounded-2xl border border-border bg-card p-6 md:p-8">
          <div className="flex items-center justify-between border-b border-border pb-5">
            <div>
              <h2 className="font-bold">
                Working budget
              </h2>

              <p className="mt-1 text-xs text-muted-foreground">
                Adjust production cost, crew
                salaries, and equipment.
              </p>
            </div>

            <Calculator
              size={20}
              className="text-primary"
            />
          </div>

          <div className="mt-3">
            {[
              [
                "production",
                "Production cost",
              ],
              ["crew", "Crew salaries"],
              ["equipment", "Equipment"],
            ].map(
              ([key, label]) => (
                <label
                  key={key}
                  className="flex items-center justify-between gap-5 border-b border-border py-5 text-sm"
                >
                  <span className="font-semibold">
                    {label}
                  </span>

                  <div className="relative w-40">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                      $
                    </span>

                    <input
                      value={
                        values[
                        key as keyof typeof values
                        ]
                      }
                      onChange={(event) =>
                        setValues({
                          ...values,
                          [key]: event.target
                            .value,
                        })
                      }
                      data-testid={`input-budget-${key}`}
                      className="h-10 w-full rounded-lg border border-input bg-background pl-7 pr-3 text-right text-sm font-bold outline-none focus:border-primary"
                    />
                  </div>
                </label>
              ),
            )}
          </div>
        </section>

        <aside className="rounded-2xl bg-secondary p-6 text-secondary-foreground md:p-8">
          <p className="mono text-[9px] uppercase tracking-[0.15em] text-secondary-foreground/55">
            Estimated total
          </p>

          <p className="display mt-4 text-5xl">
            {money(total)}
          </p>

          <div className="mt-8 border-t border-secondary-foreground/15 pt-5">
            <p className="text-sm font-semibold">
              Grant range match
            </p>

            <p className="mt-2 text-2xl font-bold">
              {range}
            </p>

            <p className="mt-2 text-sm leading-6 text-secondary-foreground/65">
              Best ranges for this plan:{" "}
              {matchedRanges.join(
                " and ",
              )}
              .
            </p>
          </div>

          <button
            data-testid="button-copy-budget"
            onClick={() =>
              navigator.clipboard?.writeText(
                `FILMFUND working budget: ${money(total)}`,
              )
            }
            className="mt-7 flex items-center gap-2 rounded-lg bg-secondary-foreground/10 px-4 py-3 text-xs font-bold transition hover:bg-secondary-foreground/20"
          >
            <ClipboardList size={14} />
            Copy estimate
          </button>
        </aside>
      </div>
    </div>
  );
}

/* =========================================================
   RESOURCES
========================================================= */

function ResourcesPage() {
  const [selected, setSelected] =
    useState<number | null>(null);

  const tips = [
    "Lead with the film, not the funding gap.",
    "Name the audience and why this story matters now.",
    "Match your ask to the fund’s stage: development, production, or completion.",
    "Use a clean one-page treatment before attaching a longer deck.",
    "Submit early enough to recover from one missing document.",
  ];

  const links = [
    {
      name: "Film Independent",
      url: "https://www.filmindependent.org",
    },
    {
      name: "The Film Collaborative",
      url: "https://thefilmcollaborative.org",
    },
    {
      name: "No Film School",
      url: "https://nofilmschool.com",
    },
    {
      name: "Sundance Institute",
      url: "https://www.sundance.org",
    },
  ];

  const stories = [
    {
      name: "Amina Owusu",
      result:
        "Found a development fund in 2 days.",
    },
    {
      name: "Kwame Mensah",
      result:
        "Moved from shortlist to award in one cycle.",
    },
    {
      name: "Lena Boateng",
      result:
        "Closed a $50,000 production gap.",
    },
  ];

  return (
    <div className="space-y-8">
      <div>
        <p className="mono text-[10px] uppercase tracking-[0.15em] text-primary">
          The reading room
        </p>

        <h1 className="display mt-2 text-4xl">
          Resources for the next yes.
        </h1>

        <p className="mt-3 text-sm text-muted-foreground">
          Practical guidance, trusted industry links,
          and stories from the room.
        </p>
      </div>

      <section className="rounded-2xl border border-border bg-card p-6 md:p-8">
        <h2 className="display text-2xl">
          Five application tips
        </h2>

        <ol className="mt-5 grid gap-3 md:grid-cols-2">
          {tips.map(
            (tip, index) => (
              <li
                key={tip}
                className="flex gap-3 text-sm leading-6"
              >
                <span className="mono text-primary">
                  0{index + 1}
                </span>

                <span>{tip}</span>
              </li>
            ),
          )}
        </ol>
      </section>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="display text-2xl">
            Industry resources
          </h2>

          <div className="mt-5 space-y-2">
            {links.map(
              (link) => (
                <a
                  key={link.name}
                  href={link.url}
                  target="_blank"
                  rel="noreferrer"
                  data-testid={`link-resource-${link.name}`}
                  className="flex items-center justify-between rounded-lg border border-border px-4 py-3 text-sm font-semibold hover:border-primary"
                >
                  {link.name}
                  <ExternalLink size={14} />
                </a>
              ),
            )}
          </div>
        </section>

        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="display text-2xl">
            Success stories
          </h2>

          <div className="mt-5 space-y-2">
            {stories.map(
              (story, index) => (
                <button
                  key={story.name}
                  onClick={() =>
                    setSelected(
                      selected === index
                        ? null
                        : index,
                    )
                  }
                  data-testid={`story-${index}`}
                  className="w-full rounded-lg border border-border p-4 text-left hover:border-primary"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold">
                      {story.name}
                    </span>

                    <ArrowUpRight
                      size={14}
                    />
                  </div>

                  <p className="mt-1 text-sm text-muted-foreground">
                    {story.result}
                  </p>
                </button>
              ),
            )}
          </div>
        </section>
      </div>

      {selected !== null && (
        <div
          className="rounded-2xl border border-primary/20 bg-primary/5 p-6"
          data-testid="success-story-detail"
        >
          <p className="mono text-[9px] uppercase text-primary">
            A room note
          </p>

          <p className="mt-3 text-sm leading-7 text-muted-foreground">
            A clear story, an honest budget, and a
            fund that understood the stage of the work
            turned this from a cold application into a
            real conversation.
          </p>
        </div>
      )}

      <section className="rounded-2xl border border-primary/20 bg-primary/5 p-6 md:p-8">
        <div className="flex items-start gap-4">
          <Send
            className="mt-1 text-primary"
            size={20}
          />

          <div>
            <h2 className="display text-2xl">
              Need a second set of eyes?
            </h2>

            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Reach the FILMFUND support desk at{" "}
              <a
                className="font-bold text-primary underline"
                href="mailto:support@filmfund.example"
                data-testid="link-contact-support"
              >
                support@filmfund.example
              </a>
              .
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

/* =========================================================
   WORKSPACE
========================================================= */

function Workspace({
  onExit,
  initialTab = "search",
}: {
  onExit: () => void;
  initialTab?: Tab;
}) {
  const [active, setActive] =
    useState<Tab>(initialTab);

  const [profile, setProfile] =
    useState<Profile>(() =>
      readStorage(
        "filmfund-profile",
        profileDefaults,
      ),
    );

  const [saved, setSaved] =
    useState<Grant[]>(() =>
      readStorage(
        "filmfund-saved",
        [],
      ),
    );

  const [applications, setApplications] =
    useState<Application[]>(() =>
      readStorage(
        "filmfund-applications",
        [],
      ),
    );

  const [dark, setDark] =
    useState(() =>
      readStorage(
        "filmfund-dark",
        false,
      ),
    );

  useEffect(() => {
    writeStorage(
      "filmfund-profile",
      profile,
    );
  }, [profile]);

  useEffect(() => {
    writeStorage(
      "filmfund-saved",
      saved,
    );
  }, [saved]);

  useEffect(() => {
    writeStorage(
      "filmfund-applications",
      applications,
    );
  }, [applications]);

  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      dark,
    );

    writeStorage(
      "filmfund-dark",
      dark,
    );
  }, [dark]);

  const health =
    useHealthCheck();

  const backendIsHealthy =
    health.data?.status === "ok" ||
    health.data?.status ===
    "healthy";

  return (
    <Shell
      active={active}
      setActive={setActive}
      profile={profile}
      savedCount={saved.length}
      onTheme={() =>
        setDark(!dark)
      }
      dark={dark}
      onLanding={onExit}
    >
      <div className="mb-7 flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <LayoutDashboard
            size={14}
            className="text-primary"
          />

          <span data-testid="status-workspace-health">
            {backendIsHealthy
              ? "Live workspace"
              : "Research workspace"}
          </span>
        </div>

        <div className="hidden items-center gap-2 text-xs text-muted-foreground md:flex">
          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
          Changes save automatically
        </div>
      </div>

      {active === "search" && (
        <SearchPage
          saved={saved}
          setSaved={setSaved}
          applications={applications}
          setApplications={
            setApplications
          }
        />
      )}

      {active === "profile" && (
        <ProfilePage
          profile={profile}
          setProfile={setProfile}
        />
      )}

      {active === "saved" && (
        <SavedPage
          saved={saved}
          setSaved={setSaved}
          setActive={setActive}
        />
      )}

      {active === "tracker" && (
        <TrackerPage
          applications={
            applications
          }
          setApplications={
            setApplications
          }
        />
      )}

      {active === "budget" && (
        <BudgetPage />
      )}

      {active === "resources" && (
        <ResourcesPage />
      )}
    </Shell>
  );
}

/* =========================================================
   HOME
========================================================= */

function Home() {
  const [entered, setEntered] =
    useState(() =>
      readStorage(
        "filmfund-entered",
        true,
      ),
    );

  const [initialTab, setInitialTab] =
    useState<Tab>("search");

  const enter = (
    tab: Tab = "search",
  ) => {
    setInitialTab(tab);
    setEntered(true);

    writeStorage(
      "filmfund-entered",
      true,
    );
  };

  return entered ? (
    <Workspace
      initialTab={initialTab}
      onExit={() => {
        setEntered(false);

        writeStorage(
          "filmfund-entered",
          false,
        );
      }}
    />
  ) : (
    <Landing
      onEnter={enter}
    />
  );
}

/* =========================================================
   ROUTER
========================================================= */

function Router() {
  const location = window.location.pathname;

  return (
    <ErrorBoundary resetKey={location}>
      <Home />
    </ErrorBoundary>
  );

}

/* =========================================================
   APP
========================================================= */

function App() {
  return (
    <QueryClientProvider
      client={queryClient}
    >
      <TooltipProvider>
        <Router />
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;