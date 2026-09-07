import { useEffect, useRef, useState } from "react";
import { Check, Loader2, X } from "lucide-react";

import { BrandMark } from "@/components/brand-mark";
import { withProfileDefaults } from "@/lib/filmmaker";

export type Intake = {
  name: string;
  email: string;
  keywords: string;
  genres: string;
  production: string;
};

type OnboardingDialogProps = {
  open: boolean;
  initialName?: string;
  initialEmail?: string;
  onClose: () => void;
  onComplete: (intake: Intake) => void;
};

const SETUP_STEPS = [
  "Setting up your dashboard",
  "Getting the right funding opportunities",
  "Aligning them with your work",
] as const;

const SETUP_AT = [0, 1200, 2600, 4000] as const;

export function emptyProfileFromIntake(intake: Intake) {
  // Anything left blank during onboarding falls back to the filmmaker profile.
  return withProfileDefaults({
    name: intake.name,
    genres: intake.genres,
    production: intake.production,
    keywords: intake.keywords,
  });
}

export function OnboardingDialog({
  open,
  initialName = "",
  initialEmail = "",
  onClose,
  onComplete,
}: OnboardingDialogProps) {
  const [step, setStep] = useState<1 | 2>(1);
  const [name, setName] = useState(initialName);
  const [email, setEmail] = useState(initialEmail);
  const [keywords, setKeywords] = useState("");
  const [genres, setGenres] = useState("");
  const [production, setProduction] = useState("");
  const nameRef = useRef<HTMLInputElement>(null);
  const keywordsRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    setStep(1);
    setName(initialName);
    setEmail(initialEmail);
    setKeywords("");
    setGenres("");
    setProduction("");

    const timer = window.setTimeout(() => {
      nameRef.current?.focus();
    }, 40);

    return () => window.clearTimeout(timer);
  }, [open, initialName, initialEmail]);

  useEffect(() => {
    if (!open) {
      return;
    }

    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  const goWork = () => {
    if (!name.trim()) {
      nameRef.current?.focus();
      return;
    }

    setStep(2);
    window.setTimeout(() => keywordsRef.current?.focus(), 40);
  };

  const finish = () => {
    if (!name.trim()) {
      setStep(1);
      window.setTimeout(() => nameRef.current?.focus(), 40);
      return;
    }

    onComplete({
      name: name.trim(),
      email: email.trim(),
      keywords: keywords.trim(),
      genres: genres.trim(),
      production: production.trim(),
    });
  };

  return (
    <div className="fixed inset-0 z-[80] flex items-end justify-center p-4 sm:items-center">
      <button
        type="button"
        className="onboard-backdrop absolute inset-0 bg-[#1d1d16]/40 backdrop-blur-sm"
        aria-label="Close"
        onClick={onClose}
      />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="onboard-title"
        className="onboard-panel relative z-10 w-full max-w-[520px] rounded-[1.6rem] border border-border bg-card p-6 shadow-[0_24px_80px_rgba(29,29,22,0.18)] sm:p-8"
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 grid size-9 place-items-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground"
          aria-label="Close"
        >
          <X size={16} />
        </button>

        <p className="eyebrow text-xs">
          {step === 1 ? "01 / Your name" : "02 / Your work"}
        </p>

        {step === 1 ? (
          <form
            className="mt-3"
            onSubmit={(event) => {
              event.preventDefault();
              goWork();
            }}
          >
            <h2
              id="onboard-title"
              className="display text-3xl font-medium tracking-[-0.5px] sm:text-4xl"
            >
              Enter your name
            </h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              FILMFUND will use this on your room. Email is optional.
            </p>

            <label className="mt-6 block font-mono text-[11px] tracking-[0.5px] text-muted-foreground">
              Full name
              <input
                ref={nameRef}
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                autoComplete="name"
                placeholder="Ada DuVernay"
                data-testid="input-name"
                className="mt-2 h-12 w-full rounded-2xl border border-input bg-background px-4 font-sans text-sm text-foreground outline-none focus:border-ring"
              />
            </label>

            <label className="mt-4 block font-mono text-[11px] tracking-[0.5px] text-muted-foreground">
              Email (optional)
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                autoComplete="email"
                placeholder="you@studio.com"
                data-testid="input-email"
                className="mt-2 h-12 w-full rounded-2xl border border-input bg-background px-4 font-sans text-sm text-foreground outline-none focus:border-ring"
              />
            </label>

            <button
              type="submit"
              data-testid="button-onboarding-continue"
              className="mt-6 h-12 w-full rounded-2xl bg-foreground text-sm font-semibold text-background hover:opacity-90"
            >
              Continue
            </button>
          </form>
        ) : (
          <form
            className="mt-3"
            onSubmit={(event) => {
              event.preventDefault();
              finish();
            }}
          >
            <h2
              id="onboard-title"
              className="display text-3xl font-medium tracking-[-0.5px] sm:text-4xl"
            >
              Tell us about the work
            </h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Keywords to track, the films you make, and anything that helps
              match funds. You can edit this later.
            </p>

            <label className="mt-6 block font-mono text-[11px] tracking-[0.5px] text-muted-foreground">
              Keywords to track
              <input
                ref={keywordsRef}
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
                placeholder="documentary finishing fund, first feature, Ghana"
                data-testid="input-onboarding-keywords"
                className="mt-2 h-12 w-full rounded-2xl border border-input bg-background px-4 font-sans text-sm text-foreground outline-none focus:border-ring"
              />
            </label>

            <label className="mt-4 block font-mono text-[11px] tracking-[0.5px] text-muted-foreground">
              Type of movies you make
              <input
                value={genres}
                onChange={(event) => setGenres(event.target.value)}
                placeholder="Documentary, drama, short form"
                data-testid="input-onboarding-genres"
                className="mt-2 h-12 w-full rounded-2xl border border-input bg-background px-4 font-sans text-sm text-foreground outline-none focus:border-ring"
              />
            </label>

            <label className="mt-4 block font-mono text-[11px] tracking-[0.5px] text-muted-foreground">
              More about the film
              <textarea
                value={production}
                onChange={(event) => setProduction(event.target.value)}
                rows={4}
                placeholder="What you are making, where you are in the process, who it is for."
                data-testid="input-onboarding-details"
                className="mt-2 w-full resize-none rounded-2xl border border-input bg-background px-4 py-3 font-sans text-sm text-foreground outline-none focus:border-ring"
              />
            </label>

            <div className="mt-6 flex gap-3">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="h-12 flex-1 rounded-2xl border border-input text-sm font-medium hover:bg-muted/60"
              >
                Back
              </button>
              <button
                type="submit"
                data-testid="button-onboarding-start"
                className="h-12 flex-[1.4] rounded-2xl bg-foreground text-sm font-semibold text-background hover:opacity-90"
              >
                Enter
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export function SetupScreen({
  name,
  onDone,
}: {
  name: string;
  onDone: () => void;
}) {
  const [active, setActive] = useState(0);
  const doneRef = useRef(onDone);
  doneRef.current = onDone;
  const reduced =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    if (reduced) {
      const skip = window.setTimeout(() => doneRef.current(), 280);
      return () => window.clearTimeout(skip);
    }

    const timers = [
      window.setTimeout(() => setActive(1), SETUP_AT[1]),
      window.setTimeout(() => setActive(2), SETUP_AT[2]),
      window.setTimeout(() => doneRef.current(), SETUP_AT[3]),
    ];

    return () => timers.forEach((timer) => window.clearTimeout(timer));
  }, [reduced]);

  const progress = Math.min(100, ((active + 1) / SETUP_STEPS.length) * 100);
  const first = name.trim().split(/\s+/)[0] || "there";

  return (
    <div
      className="flex min-h-[100dvh] flex-col items-center justify-center bg-background px-6 text-foreground"
      data-testid="screen-setup"
    >
      <BrandMark />

      <div className="mt-10 w-full max-w-md">
        <div className="flex items-center gap-3">
          <Loader2
            className="size-5 animate-spin text-brand"
            aria-hidden="true"
          />
          <p className="text-sm text-muted-foreground">
            Setting up the dashboard for you, {first}.
          </p>
        </div>

        <div
          className="mt-5 h-1.5 overflow-hidden rounded-full bg-muted"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={Math.round(progress)}
          data-testid="status-setup-progress"
        >
          <div
            className="setup-bar h-full rounded-full bg-foreground"
            style={{ width: `${progress}%` }}
          />
        </div>

        <ol className="mt-8 space-y-3">
          {SETUP_STEPS.map((label, index) => {
            const done = index < active;
            const current = index === active;

            return (
              <li
                key={label}
                className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm transition-colors ${
                  current
                    ? "border-foreground/20 bg-card text-foreground"
                    : done
                      ? "border-transparent text-foreground/70"
                      : "border-transparent text-muted-foreground/70"
                }`}
              >
                <span
                  className={`grid size-6 place-items-center rounded-full ${
                    done
                      ? "bg-foreground text-background"
                      : current
                        ? "border border-foreground/30"
                        : "border border-border"
                  }`}
                >
                  {done ? (
                    <Check size={12} />
                  ) : current ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <span className="font-mono text-[10px]">{index + 1}</span>
                  )}
                </span>
                {label}
              </li>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
