/**
 * Munira Mohammed's filmmaker profile and portfolio.
 *
 * Single source of truth for the landing page "Sample works" gallery and the
 * workspace Profile page defaults. Portfolio .mp4 files live in
 * `frontend/public/media/` (same folder as the hero video).
 */

export type Work = {
  title: string;
  file: string;
  genre: string;
  format: string;
  year?: string;
  runtime?: string;
  logline?: string;
  poster?: string;
  script?: string;
};

export type FilmmakerProfile = {
  name: string;
  location: string;
  level: string;
  genres: string;
  budget: string;
  scripts: string;
  production: string;
  keywords: string;
};

export const FILMMAKER = "Munira Mohammed";
export const FILMMAKER_EMAIL = "muniramohammed1256@gmail.com";
export const MEMBER_SINCE = "2024";

export const works: Work[] = [
  {
    title: "Bills & Records",
    file: "Bills-Records-Short-Documentary.mp4",
    genre: "Documentary",
    format: "Short documentary",
  },
  {
    title: "Prodigy",
    file: "Indie-Sci-Fi-Gem-Prodigy-2017.mp4",
    genre: "Sci-Fi",
    format: "Indie short",
    year: "2017",
  },
  {
    title: "Late Night Convenience",
    file: "Late-Night-Convenience-Indie-Short.mp4",
    genre: "Indie drama",
    format: "Indie short",
  },
  {
    title: "MANSPREAD",
    file: "MANSPREAD.mp4",
    genre: "Short film",
    format: "Narrative short",
  },
];

export const scriptsInDevelopment = [
  { title: "Juno", genre: "Comedy-Drama", budget: "$7–8M", file: "/media/juno-script.pdf" },
  { title: "Moonlight", genre: "Drama", budget: "$1.5–2M", file: "/media/moonlight-script.pdf" },
  { title: "Whiplash", genre: "Drama-Thriller", budget: "$3.2M", file: "/media/whiplash-script.pdf" },
];

export const defaultProfile: FilmmakerProfile = {
  name: FILMMAKER,
  location: "Ghana",
  level: "Professional",
  genres: "Drama, Indie, Documentary",
  budget: "$100,000",
  scripts: scriptsInDevelopment
    .map((script) => `${script.title} — ${script.genre}, ${script.budget} budget`)
    .join("; "),
  production: [
    `Email: ${FILMMAKER_EMAIL}`,
    `Portfolio videos: ${works.map((work) => work.file).join(", ")}`,
    "Experience level: Professional",
    `Member since: ${MEMBER_SINCE}`,
  ].join("\n"),
  keywords: "drama, indie, documentary, short film, Ghana",
};

/** Treat blank strings as missing so stored/intake values fall back to defaults. */
export function withProfileDefaults(
  partial: Partial<Record<keyof FilmmakerProfile, string | undefined>>,
): FilmmakerProfile {
  const merged = { ...defaultProfile };
  for (const key of Object.keys(defaultProfile) as (keyof FilmmakerProfile)[]) {
    const value = partial[key];
    if (typeof value === "string" && value.trim()) {
      merged[key] = value;
    }
  }
  return merged;
}
