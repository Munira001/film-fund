import {
  type ReactNode,
  useEffect,
  useMemo,
  useState,
} from "react";
import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";

import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  useLocation,
  useNavigate,
  useParams,
} from "react-router-dom";

import { ErrorBoundary } from "@/components/error-boundary";
import { BrandMark } from "@/components/brand-mark";
import { Landing } from "@/pages/landing";
import NotFound from "@/pages/not-found";
import {
  emptyProfileFromIntake,
  SetupScreen,
  type Intake,
} from "@/components/onboarding";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/toaster";
import { toast } from "@/hooks/use-toast";
import { TooltipProvider } from "@/components/ui/tooltip";
import {
  defaultProfile,
  FILMMAKER_EMAIL,
  MEMBER_SINCE,
  scriptsInDevelopment,
  withProfileDefaults,
  works,
} from "@/lib/filmmaker";


import {
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
  Search,
  Send,
  Settings2,
  SlidersHorizontal,
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
  keywords: string;
};

type Application = {
  id: string;
  title: string;
  organization: string;
  status: "Submitted" | "Pending" | "Awarded";
  date: string;
  funding: string;
};


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

  const response = await fetch(`https://film-fund.onrender.com/api/grants/search?${searchParams.toString()}`);

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
   CONSTANTS
========================================================= */

const tabs: {
  id: Tab;
  label: string;
  icon: typeof Search;
}[] = [
    { id: "search", label: "Search", icon: Search },
    { id: "profile", label: "Profile", icon: UserRound },
    { id: "saved", label: "Saved", icon: Bookmark },
    { id: "tracker", label: "Tracker", icon: ClipboardList },
    { id: "budget", label: "Budget", icon: Calculator },
    { id: "resources", label: "Resources", icon: CircleHelp },
  ];

function isTab(value: string | undefined): value is Tab {
  return tabs.some((tab) => tab.id === value);
}

const profileDefaults: Profile = defaultProfile;

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

function parseMoney(value: string) {
  const amount = Number(String(value).replace(/[^0-9.]/g, ""));
  return Number.isFinite(amount) && amount > 0
    ? String(Math.round(amount))
    : "";
}

/**
 * Open the funder's application website in a new tab.
 * Returns false (with a toast) when the grant has no usable link.
 */
function openApplicationSite(grant: Grant) {
  const url = grant.url?.trim();

  if (!url || !/^https?:\/\//i.test(url)) {
    toast({
      title: "No application link",
      description: `${grant.organization} did not publish an application URL for this opportunity.`,
    });
    return false;
  }

  window.open(url, "_blank", "noopener,noreferrer");

  toast({
    title: "Application page opened",
    description: `${grant.organization} opened in a new tab.`,
  });
  return true;
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

function initials(name: string) {
  const parts = name
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (!parts.length) {
    return "FF";
  }

  return parts
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

/* =========================================================
   SHELL
========================================================= */

function AppSidebar({
  active,
  setActive,
  profile,
  savedCount,
  onLanding,
}: {
  active: Tab;
  setActive: (tab: Tab) => void;
  profile: Profile;
  savedCount: number;
  onLanding: () => void;
}) {
  const { setOpenMobile } = useSidebar();

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div className="flex items-center gap-1">
          <button
            onClick={onLanding}
            data-testid="button-brand-home"
            className="flex min-w-0 flex-1 items-center gap-2 overflow-hidden rounded-md p-1.5 text-left hover:bg-sidebar-accent group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0"
          >
            <BrandMark className="group-data-[collapsible=icon]:[&>span:last-child]:hidden" />
          </button>
          <button
            type="button"
            onClick={() => setOpenMobile(false)}
            className="grid size-9 place-items-center rounded-md text-muted-foreground hover:bg-sidebar-accent md:hidden"
            data-testid="button-close-mobile-nav"
          >
            <X size={16} />
          </button>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Workspace</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {tabs.map(({ id, label, icon: Icon }) => (
                <SidebarMenuItem key={id}>
                  <SidebarMenuButton
                    isActive={active === id}
                    tooltip={label}
                    onClick={() => {
                      setActive(id);
                      setOpenMobile(false);
                    }}
                    data-testid={`nav-${id}`}
                    className={
                      active === id
                        ? "bg-brand/15 text-foreground hover:bg-brand/20 data-[active=true]:bg-brand/15"
                        : undefined
                    }
                  >
                    <Icon
                      className={active === id ? "text-brand" : undefined}
                    />
                    <span>{label}</span>
                  </SidebarMenuButton>
                  {id === "saved" ? (
                    <SidebarMenuBadge>{savedCount}</SidebarMenuBadge>
                  ) : null}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              size="lg"
              tooltip={profile.name || "Profile"}
              onClick={() => {
                setActive("profile");
                setOpenMobile(false);
              }}
              data-testid="button-profile-card"
            >
              <span className="grid size-8 shrink-0 place-items-center rounded-md bg-brand text-xs font-semibold text-white">
                {initials(profile.name)}
              </span>
              <span className="min-w-0 text-left">
                <span className="block truncate text-sm font-medium">
                  {profile.name || "Add your name"}
                </span>
                <span className="block truncate text-xs text-muted-foreground">
                  {profile.location || "Add a location"}
                </span>
              </span>
              <Settings2 className="ml-auto" />
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}

function Shell({
  active,
  setActive,
  profile,
  savedCount,
  children,
  onLanding,
}: {
  active: Tab;
  setActive: (tab: Tab) => void;
  profile: Profile;
  savedCount: number;
  children: ReactNode;
  onLanding: () => void;
}) {
  const activeTab = tabs.find((tab) => tab.id === active);

  return (
    <SidebarProvider className="h-svh overflow-hidden">
      <AppSidebar
        active={active}
        setActive={setActive}
        profile={profile}
        savedCount={savedCount}
        onLanding={onLanding}
      />
      <SidebarInset className="min-h-0 overflow-hidden">
        <header className="flex h-14 shrink-0 items-center gap-2 border-b border-border bg-background px-3">
          <SidebarTrigger
            className="size-9"
            data-testid="button-open-mobile-nav"
          />
          <Separator orientation="vertical" className="mr-1 h-4" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{activeTab?.label}</p>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="relative"
            onClick={() =>
              window.alert(
                "You are all caught up. FILMFUND will flag new matches after your next search.",
              )
            }
            data-testid="button-notifications"
          >
            <Bell />
            <span className="motion-badge absolute right-2 top-2 size-1.5 rounded-full bg-brand" />
          </Button>
        </header>
        <div className="flex-1 overflow-y-auto">
          <div
            key={active}
            className="page-enter mx-auto max-w-7xl px-4 py-6 sm:px-8 md:py-8"
          >
            {children}
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
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
  initialQuery = "",
}: {
  saved: Grant[];
  setSaved: (grants: Grant[]) => void;
  applications: Application[];
  setApplications: (
    applications: Application[],
  ) => void;
  initialQuery?: string;
}) {
  const [query, setQuery] =
    useState(initialQuery);

  const [submitted, setSubmitted] =
    useState(initialQuery);

  const [genre, setGenre] = useState("");
  const [location, setLocation] =
    useState("");
  const [budget, setBudget] =
    useState("10000");

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
    submitted.trim().length < 2
      ? []
      : live && live.length > 0
        ? live
        : [];

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
    // Send the filmmaker straight to the funder's application page and
    // record the opportunity in the tracker.
    if (!openApplicationSite(grant)) {
      return;
    }

    if (
      !applications.some(
        (application) =>
          application.id === grant.id,
      )
    ) {
      setApplications([
        ...applications,
        {
          id: grant.id,
          title: grant.title,
          organization: grant.organization,
          funding: grant.funding,
          status: "Submitted",
          date: new Date()
            .toISOString()
            .slice(0, 10),
        },
      ]);
    }

    showNotice(
      `Opened ${grant.organization} application page. Added to your tracker.`,
    );
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
    <div className="space-y-5">
      <form
        className="rounded-[10px] border border-border bg-card p-3 md:p-4"
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
              className="h-12 w-full rounded-2xl border border-input bg-background pl-11 pr-4 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-primary/15"
              placeholder='Try "documentary finishing fund"'
            />
          </div>

          <button
            type="submit"
            data-testid="button-search-grants"
            className="h-12 rounded-2xl bg-foreground px-6 text-sm font-semibold tracking-[-0.5px] text-background transition-colors hover:opacity-90"
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
            className="flex h-12 items-center justify-center gap-2 rounded-2xl border border-input px-4 text-sm font-semibold transition hover:bg-muted"
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
                className="mt-2 h-10 w-full rounded-2xl border border-input bg-background px-3 text-sm font-normal"
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
                className="mt-2 h-10 w-full rounded-2xl border border-input bg-background px-3 text-sm font-normal"
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
                className="mt-2 h-10 w-full rounded-2xl border border-input bg-background px-3 text-sm font-normal"
              >
                <option value="">
                  Any budget
                </option>
                <option value="10000">
                  $10,000
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
                className="mt-2 h-10 w-full rounded-2xl border border-input bg-background px-3 text-sm font-normal"
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
                    className="rounded-full border border-border px-2.5 py-1 text-[11px] hover:bg-muted/60"
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
            className="flex items-center gap-2 rounded-2xl border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
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
            className="flex items-center gap-2 rounded-2xl border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
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
            className="flex items-center gap-2 rounded-2xl border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
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
            className="rounded-2xl px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted disabled:opacity-40"
          >
            Clear compare
          </button>
        </div>
      </div>

      {notice && (
        <div
          role="status"
          aria-live="polite"
          className="rounded-xl border border-border bg-muted/60 px-4 py-3 text-sm font-semibold text-foreground"
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
            Could not reach the grant index.
          </p>

          <p className="mt-1 text-sm text-muted-foreground">
            Retry in a moment. Nothing here is filled in for you.
          </p>

          <button
            onClick={() =>
              search.refetch()
            }
            data-testid="button-retry-search"
            className="mt-4 rounded-2xl bg-foreground px-4 py-2 text-xs font-semibold text-background hover:opacity-90"
          >
            Retry live search
          </button>
        </div>
      )}

      {!search.isLoading && grants.length === 0 && (
        <p
          className="rounded-[10px] border border-dashed border-border bg-card px-5 py-10 text-sm text-muted-foreground"
          data-testid="status-grants-empty"
        >
          {submitted.trim().length < 2
            ? "Search to see matching funds."
            : "No funds matched this search yet."}
        </p>
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
                  className="rounded-[10px] bg-muted p-3"
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
      <div className="w-full max-w-2xl rounded-[10px] border border-border bg-card p-6 shadow-2xl md:p-8">
        <div className="flex items-start justify-between gap-5">
          <div>
            <h2
              id="grant-details-title"
              className="text-lg font-semibold"
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
          <div className="rounded-[10px] bg-muted p-4">
            <p className="mono text-[9px] uppercase text-muted-foreground">
              Funding
            </p>

            <p className="mt-2 text-sm font-bold">
              {grant.funding}
            </p>
          </div>

          <div className="rounded-[10px] bg-muted p-4">
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

          <div className="rounded-[10px] bg-muted p-4">
            <p className="mono text-[9px] uppercase text-muted-foreground">
              Trust score
            </p>

            <p className="mt-2 text-sm font-bold">
              {grant.trustScore} / 100
            </p>
          </div>
        </div>

        <div className="mt-5 rounded-xl border border-border bg-muted/60 p-4">
          <p className="font-mono text-xs tracking-[0.5px] text-brand">
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
            className="rounded-2xl px-4 py-2 text-sm font-semibold hover:bg-muted"
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
            className="flex items-center gap-2 rounded-2xl bg-foreground px-5 py-2 text-sm font-semibold text-background hover:opacity-90"
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
      className="reveal group relative overflow-hidden rounded-[10px] border border-border bg-card p-5 transition hover:bg-muted/60 md:p-6"
      style={{
        animationDelay: `${delay * 70}ms`,
      }}
      data-testid={`card-grant-${grant.id}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-muted px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.5px] text-muted-foreground">
            {grant.category}
          </span>

          <span className="text-[11px] text-muted-foreground">
            {grant.location}
          </span>
        </div>

        <button
          onClick={onSave}
          data-testid={`button-save-${grant.id}`}
          className="rounded-full p-2 text-muted-foreground transition hover:bg-muted hover:text-brand"
          aria-label={
            saved
              ? `Remove ${grant.title} from saved grants`
              : `Save ${grant.title}`
          }
        >
          {saved ? (
            <BookmarkCheck
              size={18}
              className="text-brand"
            />
          ) : (
            <Bookmark size={18} />
          )}
        </button>
      </div>

      <h2 className="mt-5 max-w-md text-base font-semibold leading-tight">
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
          <span className="grid h-9 w-9 place-items-center rounded-full bg-brand/15 text-xs font-semibold text-brand">
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
        {(grant.matchedScripts ?? []).length ? (
          <>
            <span className="font-semibold text-brand">
              Fits:
            </span>

            {(grant.matchedScripts ?? []).map(
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
          className="flex items-center gap-1 rounded-2xl px-3 py-2 text-xs font-semibold text-muted-foreground hover:bg-muted hover:text-foreground"
        >
          Details
          <ExternalLink size={13} />
        </button>

        <button
          type="button"
          onClick={onCompare}
          data-testid={`button-compare-${grant.id}`}
          className={`rounded-2xl px-3 py-2 text-xs font-semibold transition ${comparing
            ? "bg-foreground text-background"
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
          className="flex items-center gap-1 rounded-2xl bg-foreground px-3 py-2 text-xs font-semibold text-background transition-colors hover:opacity-90"
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
    <div className="max-w-5xl">
      <section className="rounded-[10px] border border-border bg-card p-6 md:p-8">
        <div className="flex items-center gap-4 border-b border-border pb-6">
          <span className="grid h-14 w-14 place-items-center rounded-full bg-brand text-lg font-semibold text-foreground">
            {initials(draft.name)}
          </span>

          <div>
            <h2 className="text-lg font-semibold">
              {draft.name || "Add your name"}
            </h2>

            <p className="font-mono text-sm tracking-[0.5px] text-muted-foreground">
              {[
                draft.level || null,
                draft.location || null,
              ]
                .filter(Boolean)
                .join(" · ") || "Add stage and location"}
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
            [
              "keywords",
              "Keywords to track",
            ],
          ].map(
            ([key, label]) => (
              <label
                key={key}
                className="font-mono text-xs tracking-[0.5px] text-muted-foreground"
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
                  className="mt-2 h-11 w-full rounded-2xl border border-input bg-background px-3 font-sans text-sm font-normal text-foreground outline-none focus:border-ring"
                />
              </label>
            ),
          )}

          <label className="font-mono text-xs tracking-[0.5px] text-muted-foreground md:col-span-2">
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
              className="mt-2 min-h-24 w-full rounded-2xl border border-input bg-background p-3 font-sans text-sm font-normal text-foreground outline-none focus:border-ring"
            />
          </label>
        </div>

        <div className="mt-7 flex items-center justify-end gap-4 border-t border-border pt-5">
          {savedNotice && (
            <span className="flex items-center gap-1 font-mono text-xs tracking-[0.5px] text-brand">
              <Check size={14} />
              Profile saved
            </span>
          )}

          <button
            onClick={save}
            data-testid="button-save-profile"
            className="rounded-2xl bg-foreground px-5 py-3 text-sm font-semibold tracking-[-0.5px] text-background transition-colors hover:opacity-90"
          >
            Save profile
          </button>
        </div>
      </section>

      {draft.scripts.trim() ? (
        <div
          className="mt-5 rounded-[10px] border border-border bg-card p-5"
          data-testid="card-scripts-live"
        >
          <p className="text-sm font-medium">Scripts</p>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-foreground">
            {draft.scripts}
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {scriptsInDevelopment.map((script) => (
              <a
                key={script.title}
                href={script.file}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 font-mono text-xs text-muted-foreground hover:bg-muted/60 hover:text-foreground"
              >
                {script.title} script
                <ExternalLink size={12} />
              </a>
            ))}
          </div>
        </div>
      ) : (
        <span data-testid="status-scripts-empty" className="sr-only">
          No scripts listed yet.
        </span>
      )}

      <div
        className="mt-5 rounded-[10px] border border-border bg-card p-5"
        data-testid="card-portfolio"
      >
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <p className="text-sm font-medium">Portfolio</p>
          <p className="font-mono text-xs tracking-[0.5px] text-muted-foreground">
            {FILMMAKER_EMAIL} · Member since {MEMBER_SINCE}
          </p>
        </div>
        <ul className="mt-3 divide-y divide-border">
          {works.map((work) => (
            <li
              key={work.file}
              className="flex flex-wrap items-center justify-between gap-3 py-3"
            >
              <div>
                <p className="text-sm font-medium">{work.title}</p>
                <p className="mt-0.5 font-mono text-xs tracking-[0.5px] text-muted-foreground">
                  {[work.genre, work.format, work.year]
                    .filter(Boolean)
                    .join(" · ")}
                </p>
              </div>
              <a
                href={`/media/${work.file}`}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-xs hover:bg-muted/60"
              >
                Watch
                <ExternalLink size={12} />
              </a>
            </li>
          ))}
        </ul>
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
    <div className="space-y-5">
      {saved.length === 0 ? (
        <div className="rounded-[10px] border border-dashed border-border bg-card px-6 py-16 text-center">
          <Bookmark
            size={24}
            className="mx-auto text-brand"
          />

          <h2 className="mt-4 text-base font-medium">
            No saved grants yet
          </h2>

          <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
            Save a grant from Search when you find
            one worth pursuing.
          </p>

          <button
            onClick={() =>
              setActive("search")
            }
            data-testid="button-browse-grants"
            className="mt-6 rounded-2xl bg-foreground px-5 py-3 text-xs font-semibold text-background hover:opacity-90"
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
              onApply={() =>
                openApplicationSite(grant)
              }
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
    <div className="space-y-5">
      <div className="flex justify-end">
        <button
          onClick={exportTracker}
          data-testid="button-export-tracker"
          disabled={applications.length === 0}
          className="inline-flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm hover:bg-muted disabled:opacity-40"
        >
          <Download size={15} />
          Export
        </button>
      </div>

      {applications.length === 0 ? (
        <div className="rounded-[10px] border border-dashed border-border bg-card px-6 py-16 text-center">
          <ClipboardList
            size={24}
            className="mx-auto text-brand"
          />

          <h2 className="mt-4 text-base font-medium">
            No applications yet
          </h2>

          <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
            Apply from Search and the grant lands here.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {applications.map(
            (application) => (
              <div
                key={application.id}
                className="rounded-[10px] border border-border bg-card p-5"
                data-testid={`card-application-${application.id}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-base font-semibold">
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
                      className="h-full rounded-full bg-brand transition-all"
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

function BudgetPage({
  profileBudget = "",
}: {
  profileBudget?: string;
}) {
  const [values, setValues] = useState({
    production: parseMoney(profileBudget),
    crew: "",
    equipment: "",
  });

  const total = Object.values(values).reduce(
    (sum, value) => sum + Number(value || 0),
    0,
  );

  const range =
    total <= 0
      ? "Enter costs to see a range"
      : total <= 10000
        ? "Under $10k"
        : total <= 50000
          ? "$10k–$50k"
          : total <= 100000
            ? "$50k–$100k"
            : "$100k+";

  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1.4fr)_minmax(16rem,0.8fr)]">
      <Card>
        <CardHeader>
          <CardTitle>Line items</CardTitle>
          <CardDescription>
            Production, crew, and equipment. Totals update as you type.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {(
            [
              ["production", "Production"],
              ["crew", "Crew"],
              ["equipment", "Equipment"],
            ] as const
          ).map(([key, label]) => (
            <label key={key} className="grid gap-1.5 text-sm">
              <span className="font-medium">{label}</span>
              <div className="relative">
                <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">
                  $
                </span>
                <Input
                  inputMode="numeric"
                  value={values[key]}
                  onChange={(event) =>
                    setValues({
                      ...values,
                      [key]: event.target.value.replace(/[^0-9]/g, ""),
                    })
                  }
                  placeholder="0"
                  data-testid={`input-budget-${key}`}
                  className="pl-7 tabular-nums"
                />
              </div>
            </label>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Total</CardTitle>
          <CardDescription>Working budget for grant range.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-4xl font-semibold tracking-tight tabular-nums">
            {total > 0 ? money(total) : "$0"}
          </p>
          <div className="rounded-md bg-brand/10 px-3 py-2 text-sm">
            <p className="text-muted-foreground">Grant range</p>
            <p className="font-medium text-brand-dark">{range}</p>
          </div>
          <Button
            type="button"
            variant="outline"
            className="w-full"
            disabled={total <= 0}
            data-testid="button-copy-budget"
            onClick={() =>
              navigator.clipboard?.writeText(
                `FILMFUND working budget: ${money(total)}`,
              )
            }
          >
            Copy estimate
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

/* =========================================================
   RESOURCES
========================================================= */

function ResourcesPage() {
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

  return (
    <div className="space-y-5">
      <section className="rounded-[10px] border border-border bg-card p-6 md:p-8">
        <h2 className="text-base font-semibold">
          Application tips
        </h2>

        <ol className="mt-5 grid gap-3 md:grid-cols-2">
          {tips.map(
            (tip, index) => (
              <li
                key={tip}
                className="flex gap-3 text-sm leading-6"
              >
                <span className="font-mono text-brand">
                  0{index + 1}
                </span>

                <span>{tip}</span>
              </li>
            ),
          )}
        </ol>
      </section>

      <section className="rounded-[10px] border border-border bg-card p-6">
        <h2 className="text-base font-semibold">
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
                className="flex items-center justify-between rounded-lg border border-border px-4 py-3 text-sm font-semibold hover:bg-muted/60"
              >
                {link.name}
                <ExternalLink size={14} />
              </a>
            ),
          )}
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
  active,
  setActive,
}: {
  onExit: () => void;
  active: Tab;
  setActive: (tab: Tab) => void;
}) {

  const [profile, setProfile] =
    useState<Profile>(() => {
      const stored = readStorage<Partial<Profile>>(
        "filmfund-profile",
        profileDefaults,
      );

      // Blank fields in an older saved profile fall back to the defaults.
      return withProfileDefaults(stored);
    });

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
    document.documentElement.classList.remove("dark");
  }, []);

  return (
    <Shell
      active={active}
      setActive={setActive}
      profile={profile}
      savedCount={saved.length}
      onLanding={onExit}
    >
      {active === "search" && (
        <SearchPage
          saved={saved}
          setSaved={setSaved}
          applications={applications}
          setApplications={
            setApplications
          }
          initialQuery={
            profile.keywords ||
            profile.genres
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
        <BudgetPage profileBudget={profile.budget} />
      )}

      {active === "resources" && (
        <ResourcesPage />
      )}
    </Shell>
  );
}

/* =========================================================
   ROUTES
========================================================= */

function LandingRoute() {
  const navigate = useNavigate();
  const [setup, setSetup] = useState(false);
  const [setupName, setSetupName] = useState("");

  const goApp = (tab: Tab = "search") => {
    navigate(`/app/${tab}`);
  };

  const startFromIntake = (intake: Intake) => {
    const profile = emptyProfileFromIntake(intake);
    writeStorage("filmfund-profile", profile);

    if (intake.email) {
      writeStorage("filmfund-email", intake.email);
    }

    setSetupName(intake.name);
    setSetup(true);
  };

  if (setup) {
    return (
      <SetupScreen
        name={setupName}
        onDone={() => {
          setSetup(false);
          goApp("search");
        }}
      />
    );
  }

  return (
    <Landing onEnter={goApp} onGetStarted={startFromIntake} />
  );
}

function WorkspaceRoute() {
  const { tab } = useParams();
  const navigate = useNavigate();

  if (!isTab(tab)) {
    return <Navigate to="/app/search" replace />;
  }

  return (
    <Workspace
      active={tab}
      setActive={(next) => navigate(`/app/${next}`)}
      onExit={() => navigate("/")}
    />
  );
}

function AppRoutes() {
  const location = useLocation();

  return (
    <ErrorBoundary resetKey={location.pathname}>
      <Routes>
        <Route path="/" element={<LandingRoute />} />
        <Route path="/app" element={<Navigate to="/app/search" replace />} />
        <Route path="/app/:tab" element={<WorkspaceRoute />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
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
        <BrowserRouter>
          <AppRoutes />
          <Toaster />
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;