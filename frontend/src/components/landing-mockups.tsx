import { type ReactNode, useEffect, useState } from "react";

function Chrome({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="mockup-shell relative mx-auto w-full max-w-[540px]">
      <div className="flex items-center gap-2 border-b border-preview-border px-3 py-2">
        <span className="mockup-dot bg-[#ff5f57]" />
        <span className="mockup-dot bg-[#febc2e]" />
        <span className="mockup-dot bg-[#28c840]" />
        <span className="ml-2 font-mono text-[11px] tracking-[0.5px] text-preview-muted-foreground">
          {title}
        </span>
      </div>
      {children}
    </div>
  );
}

function StatusDot({ color }: { color: string }) {
  return (
    <span
      className="inline-block h-1.5 w-1.5 rounded-full"
      style={{ background: color }}
    />
  );
}

const boardColumns = [
  {
    name: "Pending",
    color: "#1447e6",
    cards: [
      {
        title: "Feature development fund",
        org: "Sundance Institute",
        branch: "drama / juno",
        meta: "Deadline Sep 28",
      },
    ],
  },
  {
    name: "Fitting",
    color: "#7c5cbf",
    cards: [
      {
        title: "New Voices Fellowship",
        org: "Film Independent",
        branch: "drama-thriller / moonlight",
        meta: "Review in progress",
      },
    ],
  },
  {
    name: "Applied",
    color: "#c9a227",
    cards: [
      {
        title: "Documentary grant",
        org: "Chicken & Egg",
        branch: "docs / bills-records",
        meta: "Awaiting review",
      },
    ],
  },
  {
    name: "Ready",
    color: "#3d9a5f",
    cards: [
      {
        title: "Artist Support Grant",
        org: "Creative Capital",
        branch: "experimental / whiplash",
        meta: "Merge packet",
      },
    ],
  },
];

export function GrantBoardMockup({
  title = "Grant board",
}: {
  title?: string;
}) {
  const [passed, setPassed] = useState(74);

  useEffect(() => {
    const id = window.setInterval(() => {
      setPassed((value) => (value >= 96 ? 74 : value + 1));
    }, 900);

    return () => window.clearInterval(id);
  }, []);

  return (
    <Chrome title={title}>
      <div className="grid grid-cols-4 gap-px bg-preview-divider">
        {boardColumns.map((column, index) => (
          <div key={column.name} className="bg-preview-card p-2">
            <div className="mb-2 flex items-center gap-1.5 px-1">
              <StatusDot color={column.color} />
              <span className="font-mono text-[10px] tracking-[0.5px] text-preview-muted-foreground">
                {column.name}
              </span>
              <span className="ml-auto font-mono text-[10px] text-preview-muted-foreground">
                {column.cards.length}
              </span>
            </div>
            {column.cards.map((card) => (
              <div
                key={card.title}
                className={`rounded-[var(--mockup-inner-radius)] border border-preview-border bg-preview-sidebar p-2 ${
                  index === 1 ? "mockup-card-live" : ""
                }`}
              >
                <p className="line-clamp-2 text-[11px] font-medium leading-4 text-foreground">
                  {card.title}
                </p>
                <p className="mt-1 truncate font-mono text-[10px] text-preview-muted-foreground">
                  {card.branch}
                </p>
                <div className="mt-2 flex items-center justify-between">
                  <span className="rounded-full border border-preview-border px-1.5 py-0.5 font-mono text-[9px] text-preview-muted-foreground">
                    {passed}% match
                  </span>
                  {column.name === "Ready" ? (
                    <span className="rounded-full bg-foreground px-1.5 py-0.5 font-mono text-[9px] text-background">
                      Submit
                    </span>
                  ) : (
                    <span className="font-mono text-[9px] text-brand">
                      {card.meta}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </Chrome>
  );
}

export function ProfileMockup() {
  const target = "Munira Mohammed";
  const [typed, setTyped] = useState("");

  useEffect(() => {
    let index = 0;
    let hold = 0;
    const id = window.setInterval(() => {
      if (index < target.length) {
        index += 1;
        hold = 0;
        setTyped(target.slice(0, index));
        return;
      }
      hold += 1;
      if (hold > 16) {
        index = 0;
        hold = 0;
        setTyped("");
      }
    }, 90);

    return () => window.clearInterval(id);
  }, []);

  return (
    <Chrome title="Who you are">
      <div className="grid grid-cols-[160px_1fr] bg-preview-sidebar">
        <aside className="border-r border-preview-border p-3">
          <p className="font-mono text-[10px] tracking-[0.5px] text-preview-muted-foreground">
            Profile
          </p>
          <div className="mt-3 space-y-1.5 text-[11px] text-preview-muted-foreground">
            <p className="text-foreground">Who you are</p>
            <p>Scripts</p>
            <p>Budget</p>
            <p>Eligibility</p>
          </div>
        </aside>
        <div className="p-4">
          <p className="font-mono text-[10px] tracking-[0.5px] text-preview-muted-foreground">
            Name
          </p>
          <p className="mt-2 border-b border-preview-border pb-2 font-mono text-sm text-foreground">
            {typed}
            <span className="caret-blink">|</span>
          </p>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div>
              <p className="font-mono text-[10px] text-preview-muted-foreground">
                Location
              </p>
              <p className="mt-1 text-xs">Ghana</p>
            </div>
            <div>
              <p className="font-mono text-[10px] text-preview-muted-foreground">
                Stage
              </p>
              <p className="mt-1 text-xs">Professional</p>
            </div>
          </div>
          <p className="mt-4 font-mono text-[10px] text-brand">
            Profile shapes every match
          </p>
        </div>
      </div>
    </Chrome>
  );
}

export function SessionMockup() {
  return (
    <Chrome title="Application">
      <div className="grid grid-cols-[1fr_180px] bg-preview-sidebar">
        <div className="border-r border-preview-border p-4">
          <p className="text-[13px] font-medium">New Voices Fellowship</p>
          <p className="mt-1 text-[11px] text-preview-muted-foreground">
            Film Independent
          </p>
          <p className="mt-3 text-xs leading-5 text-preview-muted-foreground">
            Add a one-page treatment, a realistic budget, and a sentence about
            why this story matters now.
          </p>
          <p className="mt-4 rounded-full border border-preview-border px-2 py-1 text-[11px] text-brand">
            Packet in progress
          </p>
        </div>
        <aside className="space-y-3 p-3">
          {[
            ["STATUS", "Submitted"],
            ["DEADLINE", "Oct 22"],
            ["UPDATED", "32m ago"],
          ].map(([label, value]) => (
            <div key={label}>
              <p className="font-mono text-[9px] tracking-[0.5px] text-preview-muted-foreground">
                {label}
              </p>
              <p className="mt-1 text-[11px]">{value}</p>
            </div>
          ))}
        </aside>
      </div>
    </Chrome>
  );
}

export function SearchMockup() {
  const query = "Fix the finishing-fund gap for a Ghana drama";
  const [typed, setTyped] = useState("");
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let index = 0;
    let hold = 0;
    const id = window.setInterval(() => {
      if (index < query.length) {
        index += 1;
        hold = 0;
        setTyped(query.slice(0, index));
        setOpen(false);
        return;
      }
      setOpen(true);
      hold += 1;
      if (hold > 18) {
        index = 0;
        hold = 0;
        setTyped("");
        setOpen(false);
      }
    }, 55);

    return () => window.clearInterval(id);
  }, []);

  return (
    <Chrome title="Search grants">
      <div className="bg-preview-card p-4">
        <p className="text-sm font-medium">Find matching funds</p>
        <p className="mt-1 text-[11px] text-preview-muted-foreground">
          Describe the film. FILMFUND ranks live grants against who you are.
        </p>
        <div className="mt-3 min-h-16 rounded-[var(--mockup-inner-radius)] border border-preview-border bg-preview-sidebar p-2 text-[11px]">
          {typed}
          <span className="caret-blink">|</span>
        </div>
        <p className="mt-2 font-mono text-[10px] text-preview-muted-foreground">
          Genre
        </p>
        <div className="relative mt-1">
          <div className="rounded-[var(--mockup-inner-radius)] border border-preview-border px-2 py-1.5 text-[11px]">
            Drama
          </div>
          {open ? (
            <div className="absolute left-0 right-0 top-full z-10 mt-1 rounded-[var(--mockup-inner-radius)] border border-preview-border bg-preview-sidebar p-1 text-[11px]">
              {["Drama", "Documentary", "Experimental"].map((item) => (
                <p key={item} className="rounded px-2 py-1 hover:bg-muted">
                  {item}
                </p>
              ))}
            </div>
          ) : null}
        </div>
        <div className="mt-3 flex justify-end gap-2">
          <span className="rounded-2xl border border-preview-border px-3 py-1.5 text-[11px]">
            Clear
          </span>
          <span className="flex items-center gap-1 rounded-2xl bg-foreground px-3 py-1.5 text-[11px] font-semibold text-background">
            {open ? "5 matches" : "Search"}
          </span>
        </div>
      </div>
    </Chrome>
  );
}

export function PhoneMockup() {
  return (
    <div className="mx-auto w-[220px] rounded-[28px] border border-preview-border bg-preview-sidebar p-2 shadow-2xl">
      <div className="rounded-[22px] bg-preview-card px-3 pb-3 pt-2">
        <p className="text-center font-mono text-[10px] text-preview-muted-foreground">
          9:41
        </p>
        <div className="mt-2 flex items-center justify-between">
          <p className="text-sm font-medium">Grants</p>
          <p className="font-mono text-[10px] text-preview-muted-foreground">
            FILMFUND
          </p>
        </div>
        <div className="mt-3 grid grid-cols-3 gap-1">
          {[
            ["4", "searching"],
            ["1", "need you"],
            ["1", "ready"],
          ].map(([n, label]) => (
            <div
              key={label}
              className="rounded-lg border border-preview-border p-2 text-center"
            >
              <p className="text-sm font-medium">{n}</p>
              <p className="font-mono text-[8px] text-preview-muted-foreground">
                {label}
              </p>
            </div>
          ))}
        </div>
        <p className="mt-3 font-mono text-[9px] tracking-[0.5px] text-brand">
          NEEDS YOU
        </p>
        <div className="mt-1 rounded-lg border border-preview-border p-2">
          <p className="text-[11px]">Auth migration</p>
          <p className="font-mono text-[9px] text-preview-muted-foreground">
            Needs input · 4m
          </p>
        </div>
        <p className="mt-3 font-mono text-[9px] tracking-[0.5px] text-preview-muted-foreground">
          WORKING
        </p>
        <div className="mt-1 rounded-lg border border-preview-border p-2">
          <p className="text-[11px]">Landing copy pass</p>
          <p className="font-mono text-[9px] text-preview-muted-foreground">
            Juno · searching
          </p>
        </div>
      </div>
    </div>
  );
}

export function FeatureMedia({
  src,
  alt,
  children,
}: {
  src: string;
  alt: string;
  children: ReactNode;
}) {
  return (
    <div className="relative h-full min-h-[280px] w-full overflow-hidden lg:min-h-[420px]">
      <img
        src={src}
        alt={alt}
        className="absolute inset-0 h-full w-full object-cover"
      />
      <div className="absolute inset-0 bg-background/45" />
      <div className="relative flex h-full min-h-[280px] items-center justify-center p-4 lg:min-h-[420px]">
        {children}
      </div>
    </div>
  );
}
