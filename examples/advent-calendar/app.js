"use strict";

const STORAGE_KEY = "um-advent-calendar-v1";
const LIBRARY_KEY = "um-advent-calendars-v1";
const ACTIVE_CALENDAR_KEY = "um-advent-active-calendar-v1";
const CLOUD_CALENDARS_TABLE = "advent_creator_calendars";
const SUPABASE_CLIENT_MODULE = "https://esm.sh/@supabase/supabase-js@2.117.3";
const DOOR_COUNT = 24;
const DEFAULT_CAPTION = "Prépare 24 surprises et partage un joli moment pour Noël.";
const IMAGE_DATA_URL = /^data:image\/(?:png|jpeg|webp|gif);base64,[a-z\d+/]+=*$/i;
const DEFAULT_THEME = {
  backgroundColor: "#f5f1e8",
  coverImage: "",
  photoSide: "right",
  photoWidth: 42,
  photoZoom: 100,
  photoX: 50,
  photoY: 50,
  font: "classic",
  openingAnimation: "side",
  doorColor: "#fffefa",
  textColor: "#214c3d",
  decorationColor: "#bc9144",
  shape: "rounded",
  decoration: "individual"
};
const SHAPES = {
  rounded: "Coins arrondis",
  square: "Carrés",
  circle: "Ronds",
  arch: "Petites arches",
  oval: "Ovales",
  diamond: "Losanges",
  hexagon: "Hexagones",
  star: "Étoiles",
  heart: "Cœurs",
  triangle: "Triangles"
};
const FONTS = new Set(["classic", "modern", "playful", "handwritten"]);
const OPENING_ANIMATIONS = {
  side: "Porte qui pivote sur le côté",
  swing: "Grande porte qui s'ouvre",
  flip: "Trappe qui bascule",
  lift: "Porte qui s'envole",
  zoom: "Zoom magique",
  dissolve: "Disparition scintillante",
  slide: "Porte qui glisse",
  curtain: "Rideau qui s'écarte",
  bounce: "Ouverture rebondissante"
};
const DECORATIONS = {
  snow: { label: "Flocons de neige", symbols: ["❄", "❅", "❆", "✧"], accent: "#8ba9b2" },
  stars: { label: "Étoiles scintillantes", symbols: ["✦", "✧", "★", "⋆"], accent: "#bc9144" },
  hearts: { label: "Petits cœurs", symbols: ["♥", "♡", "❤", "ღ"], accent: "#bd5b66" },
  holly: { label: "Feuilles de houx", symbols: ["❧", "✿", "❋", "❧"], accent: "#43805d" },
  gifts: { label: "Cadeaux dorés", symbols: ["🎁", "✦", "🎀", "🎁"], accent: "#b4873e" },
  candy: { label: "Sucre d'orge", symbols: ["🍬", "🍭", "❋", "🍬"], accent: "#d56870" },
  bells: { label: "Cloches de Noël", symbols: ["🔔", "♫", "♪", "🔔"], accent: "#bf964d" },
  trees: { label: "Petits sapins", symbols: ["🎄", "✦", "🎄", "❄"], accent: "#43805d" },
  reindeer: { label: "Rennes malicieux", symbols: ["🦌", "✧", "❄", "🦌"], accent: "#a86f45" },
  baubles: { label: "Boules de Noël", symbols: ["🔴", "🟢", "🟡", "🔵"], accent: "#bd5b4c" },
  gingerbread: { label: "Pain d'épices", symbols: ["🍪", "♡", "✧", "🍪"], accent: "#b67b48" },
  stockings: { label: "Chaussettes de Noël", symbols: ["🧦", "🎁", "✦", "🧦"], accent: "#bd5b4c" },
  candles: { label: "Lumières de fête", symbols: ["🕯️", "✦", "✧", "🕯️"], accent: "#d19d3f" },
  sparkles: { label: "Paillettes colorées", symbols: ["✦", "❋", "✧", "✺"], accent: "#9d78b1" },
  spades: { label: "Piques", symbols: ["♠", "♠", "♠", "♠"], accent: "#315b49" }
};

const elements = {
  title: document.querySelector("#calendar-title"),
  grid: document.querySelector("#calendar-grid"),
  shuffleDoorsButton: document.querySelector("#shuffle-doors-button"),
  resetDoorsOrderButton: document.querySelector("#reset-doors-order-button"),
  caption: document.querySelector("#intro-caption"),
  introArt: document.querySelector("#intro-art"),
  introPhotoFrame: document.querySelector("#intro-photo-frame"),
  introPhoto: document.querySelector("#intro-photo"),
  hint: document.querySelector("#hint-text"),
  badge: document.querySelector("#mode-badge"),
  shareButton: document.querySelector("#share-button"),
  accountButton: document.querySelector("#account-button"),
  themeButton: document.querySelector("#theme-button"),
  exitReaderButton: document.querySelector("#exit-reader-button"),
  status: document.querySelector("#status-message"),
  themeDialog: document.querySelector("#theme-dialog"),
  themeForm: document.querySelector("#theme-form"),
  themeFont: document.querySelector("#theme-font"),
  themeOpeningAnimation: document.querySelector("#theme-opening-animation"),
  themeOpeningPreview: document.querySelector("#theme-opening-preview"),
  themeOpeningDoor: document.querySelector("#theme-opening-door"),
  themeOpeningBurst: document.querySelector("#theme-opening-burst"),
  themeOpeningSymbol: document.querySelector("#theme-opening-symbol"),
  themeOpeningPreviewButton: document.querySelector("#theme-opening-preview-button"),
  themeCaption: document.querySelector("#theme-caption"),
  themeCoverImage: document.querySelector("#theme-cover-image"),
  coverImagePreview: document.querySelector("#cover-image-preview"),
  coverPreviewImage: document.querySelector("#cover-preview-image"),
  photoPositionControls: document.querySelector("#photo-position-controls"),
  themePhotoSide: document.querySelector("#theme-photo-side"),
  themePhotoWidth: document.querySelector("#theme-photo-width"),
  themePhotoWidthValue: document.querySelector("#theme-photo-width-value"),
  themePhotoZoom: document.querySelector("#theme-photo-zoom"),
  themePhotoZoomValue: document.querySelector("#theme-photo-zoom-value"),
  themePhotoX: document.querySelector("#theme-photo-x"),
  themePhotoXValue: document.querySelector("#theme-photo-x-value"),
  themePhotoY: document.querySelector("#theme-photo-y"),
  themePhotoYValue: document.querySelector("#theme-photo-y-value"),
  removeCoverImageButton: document.querySelector("#remove-cover-image-button"),
  saveThemeButton: document.querySelector("#save-theme-button"),
  themeBackgroundColor: document.querySelector("#theme-background-color"),
  themeDoorColor: document.querySelector("#theme-door-color"),
  themeTextColor: document.querySelector("#theme-text-color"),
  themeDecorationColor: document.querySelector("#theme-decoration-color"),
  themeShape: document.querySelector("#theme-shape"),
  themeDecoration: document.querySelector("#theme-decoration"),
  themePreview: document.querySelector("#theme-preview"),
  editDialog: document.querySelector("#edit-dialog"),
  editForm: document.querySelector("#edit-form"),
  editHeading: document.querySelector("#edit-heading"),
  surpriseTitle: document.querySelector("#surprise-title"),
  surpriseMessage: document.querySelector("#surprise-message"),
  surpriseDecoration: document.querySelector("#surprise-decoration"),
  surpriseShape: document.querySelector("#surprise-shape"),
  surpriseOpeningAnimation: document.querySelector("#surprise-opening-animation"),
  surpriseDoorColor: document.querySelector("#surprise-door-color"),
  surpriseTextColor: document.querySelector("#surprise-text-color"),
  surpriseDecorationColor: document.querySelector("#surprise-decoration-color"),
  inheritDoorColor: document.querySelector("#inherit-door-color"),
  inheritTextColor: document.querySelector("#inherit-text-color"),
  inheritDecorationColor: document.querySelector("#inherit-decoration-color"),
  surpriseImage: document.querySelector("#surprise-image"),
  saveSurpriseButton: document.querySelector("#edit-form button[type=submit]"),
  imagePreview: document.querySelector("#image-preview"),
  previewImage: document.querySelector("#preview-image"),
  removeImageButton: document.querySelector("#remove-image-button"),
  previewDoor: document.querySelector("#decoration-preview-door"),
  previewDoorNumber: document.querySelector("#preview-door-number"),
  previewDoorSymbol: document.querySelector("#preview-door-symbol"),
  previewBurst: document.querySelector("#preview-burst"),
  previewAnimationButton: document.querySelector("#preview-animation-button"),
  revealDialog: document.querySelector("#reveal-dialog"),
  revealOpeningScene: document.querySelector("#reveal-opening-scene"),
  revealDoorNumber: document.querySelector("#reveal-door-number"),
  revealDoorSymbol: document.querySelector("#reveal-door-symbol"),
  revealDay: document.querySelector("#reveal-day"),
  revealTitle: document.querySelector("#reveal-title"),
  revealMessage: document.querySelector("#reveal-message"),
  revealEmpty: document.querySelector("#reveal-empty"),
  revealImage: document.querySelector("#reveal-image"),
  revealBurst: document.querySelector("#reveal-burst"),
  editFromReveal: document.querySelector("#edit-from-reveal"),
  shareDialog: document.querySelector("#share-dialog"),
  shareForm: document.querySelector("#share-form"),
  shareLink: document.querySelector("#share-link"),
  shareSize: document.querySelector("#share-size"),
  copyLinkButton: document.querySelector("#copy-link-button"),
  accountDialog: document.querySelector("#account-dialog"),
  accountForm: document.querySelector("#account-form"),
  accountSetupMessage: document.querySelector("#account-setup-message"),
  accountSetupLink: document.querySelector("#account-setup-link"),
  accountFields: document.querySelector("#account-fields"),
  accountEmail: document.querySelector("#account-email"),
  accountPassword: document.querySelector("#account-password"),
  accountSignInButton: document.querySelector("#account-sign-in"),
  accountSignUpButton: document.querySelector("#account-sign-up"),
  accountSignedIn: document.querySelector("#account-signed-in"),
  accountUserLabel: document.querySelector("#account-user-label"),
  accountSyncButton: document.querySelector("#account-sync-button"),
  accountSignOutButton: document.querySelector("#account-sign-out"),
  calendarLibraryButton: document.querySelector("#calendar-library-button"),
  calendarLibraryDialog: document.querySelector("#calendar-library-dialog"),
  calendarLibraryList: document.querySelector("#calendar-library-list"),
  newCalendarButton: document.querySelector("#new-calendar-button"),
  activeCalendarLabel: document.querySelector("#active-calendar-label")
};

function emptyCalendar() {
  return {
    title: "Mon calendrier de l'Avent",
    subtitle: DEFAULT_CAPTION,
    theme: { ...DEFAULT_THEME },
    doorOrder: Array.from({ length: DOOR_COUNT }, (_, index) => index),
    doors: Array.from({ length: DOOR_COUNT }, () => ({ title: "", message: "", image: "", decoration: "snow", shape: null }))
  };
}

function syncDoorColorForm() {
  const fields = [
    [elements.surpriseDoorColor, elements.inheritDoorColor, "doorColor"],
    [elements.surpriseTextColor, elements.inheritTextColor, "textColor"],
    [elements.surpriseDecorationColor, elements.inheritDecorationColor, "decorationColor"]
  ];
  for (const [input, inherit, key] of fields) {
    inherit.checked = pendingDoorColors[key] === null;
    input.disabled = inherit.checked;
    input.value = pendingDoorColors[key] || calendar.theme[key];
  }
  updateDoorColorPreview();
}

function updateDoorColorPreview() {
  const colors = {
    doorColor: pendingDoorColors.doorColor || calendar.theme.doorColor,
    textColor: pendingDoorColors.textColor || calendar.theme.textColor,
    decorationColor: pendingDoorColors.decorationColor || calendar.theme.decorationColor
  };
  elements.previewDoor.style.setProperty("--calendar-door-color", colors.doorColor);
  elements.previewDoor.style.setProperty("--calendar-text-color", colors.textColor);
  elements.previewDoor.style.setProperty("--calendar-decoration-color", colors.decorationColor);
  elements.previewDoor.style.setProperty("--decoration-color", colors.decorationColor);
  const button = getDoorButton(editingDay);
  if (button) {
    button.style.setProperty("--calendar-door-color", colors.doorColor);
    button.style.setProperty("--calendar-text-color", colors.textColor);
    button.style.setProperty("--calendar-decoration-color", colors.decorationColor);
  }
}

function decemberDayLabel(index) {
  return index === 0 ? "1er" : String(index + 1);
}

function getDoorButton(dayIndex) {
  return elements.grid.querySelector(`.door[data-day-index="${dayIndex}"]`);
}

function isDefaultDoorOrder(order) {
  return order.every((dayIndex, index) => dayIndex === index);
}

function validateCalendar(value) {
  if (!value || typeof value !== "object" || typeof value.title !== "string" || !Array.isArray(value.doors) || value.doors.length !== DOOR_COUNT) {
    throw new Error("Ce lien ne contient pas un calendrier valide.");
  }
  const doors = value.doors.map((door) => {
    if (!door || typeof door.title !== "string" || typeof door.message !== "string" || typeof door.image !== "string") {
      throw new Error("Une case de ce calendrier est illisible.");
    }
    const decoration = door.decoration === undefined ? "snow" : door.decoration;
    if (typeof decoration !== "string" || !Object.hasOwn(DECORATIONS, decoration)) {
      throw new Error("La décoration d'une case n'est pas reconnue.");
    }
    const shape = door.shape === undefined ? null : door.shape;
    if (shape !== null && (typeof shape !== "string" || !Object.hasOwn(SHAPES, shape))) {
      throw new Error("La forme d'une case n'est pas reconnue.");
    }
    const openingAnimation = door.openingAnimation === undefined ? null : door.openingAnimation;
    if (openingAnimation !== null && (typeof openingAnimation !== "string" || !Object.hasOwn(OPENING_ANIMATIONS, openingAnimation))) {
      throw new Error("L'animation d'ouverture d'une case n'est pas reconnue.");
    }
    const colors = {};
    for (const key of ["doorColor", "textColor", "decorationColor"]) {
      const color = door[key] === undefined ? null : door[key];
      if (color !== null && (typeof color !== "string" || !/^#[a-f\d]{6}$/i.test(color))) {
        throw new Error("Une couleur de case n'est pas valide.");
      }
      colors[key] = color === null ? null : color.toLowerCase();
    }
    if (door.image && !IMAGE_DATA_URL.test(door.image)) {
      throw new Error("Une image du calendrier n'est pas reconnue.");
    }
    return { title: door.title.slice(0, 80), message: door.message.slice(0, 1500), image: door.image, decoration, shape, openingAnimation, ...colors };
  });
  const doorOrder = value.doorOrder === undefined
    ? Array.from({ length: DOOR_COUNT }, (_, index) => index)
    : value.doorOrder;
  if (!Array.isArray(doorOrder) || doorOrder.length !== DOOR_COUNT
    || doorOrder.some((dayIndex) => !Number.isInteger(dayIndex) || dayIndex < 0 || dayIndex >= DOOR_COUNT)
    || new Set(doorOrder).size !== DOOR_COUNT) {
    throw new Error("L'ordre des cases du calendrier n'est pas valide.");
  }
  const theme = value.theme === undefined ? { ...DEFAULT_THEME } : value.theme;
  if (!theme || typeof theme !== "object") throw new Error("Le thème du calendrier n'est pas reconnu.");
  const colorPattern = /^#[a-f\d]{6}$/i;
  const backgroundColor = theme.backgroundColor === undefined ? DEFAULT_THEME.backgroundColor : theme.backgroundColor;
  if (typeof backgroundColor !== "string" || !colorPattern.test(backgroundColor)) {
    throw new Error("La couleur du fond du calendrier n'est pas valide.");
  }
  const coverImage = theme.coverImage === undefined ? "" : theme.coverImage;
  if (typeof coverImage !== "string" || (coverImage && !IMAGE_DATA_URL.test(coverImage))) {
    throw new Error("La photo du bandeau n'est pas reconnue.");
  }
  const font = theme.font === undefined ? "classic" : theme.font;
  if (typeof font !== "string" || !FONTS.has(font)) {
    throw new Error("L'écriture du calendrier n'est pas reconnue.");
  }
  const openingAnimation = theme.openingAnimation === undefined ? "side" : theme.openingAnimation;
  if (typeof openingAnimation !== "string" || !Object.hasOwn(OPENING_ANIMATIONS, openingAnimation)) {
    throw new Error("L'animation d'ouverture n'est pas reconnue.");
  }
  if (value.subtitle !== undefined && typeof value.subtitle !== "string") {
    throw new Error("La phrase du calendrier n'est pas valide.");
  }
  const photoSide = theme.photoSide === undefined ? "right" : theme.photoSide;
  const photoWidth = theme.photoWidth === undefined ? 42 : theme.photoWidth;
  const photoZoom = theme.photoZoom === undefined ? 100 : theme.photoZoom;
  const photoX = theme.photoX === undefined ? 50 : theme.photoX;
  const photoY = theme.photoY === undefined ? 50 : theme.photoY;
  if (photoSide !== "left" && photoSide !== "right") throw new Error("Le côté de la photo n'est pas reconnu.");
  if (!Number.isInteger(photoWidth) || photoWidth < 20 || photoWidth > 65) throw new Error("La largeur de la photo n'est pas valide.");
  if (!Number.isInteger(photoZoom) || photoZoom < 100 || photoZoom > 250) throw new Error("Le zoom de la photo n'est pas valide.");
  if (!Number.isInteger(photoX) || photoX < 0 || photoX > 100 || !Number.isInteger(photoY) || photoY < 0 || photoY > 100) {
    throw new Error("La position de la photo n'est pas valide.");
  }
  for (const key of ["doorColor", "textColor", "decorationColor"]) {
    if (typeof theme[key] !== "string" || !colorPattern.test(theme[key])) {
      throw new Error("Une couleur du calendrier n'est pas valide.");
    }
  }
  if (typeof theme.shape !== "string" || !Object.hasOwn(SHAPES, theme.shape)) {
    throw new Error("La forme des cases du calendrier n'est pas reconnue.");
  }
  if (typeof theme.decoration !== "string" || (theme.decoration !== "individual" && !Object.hasOwn(DECORATIONS, theme.decoration))) {
    throw new Error("La décoration globale du calendrier n'est pas reconnue.");
  }
  return {
    title: value.title.slice(0, 80),
    subtitle: (value.subtitle === undefined ? DEFAULT_CAPTION : value.subtitle).slice(0, 160),
    theme: {
      backgroundColor: backgroundColor.toLowerCase(),
      coverImage,
      photoSide,
      photoWidth,
      photoZoom,
      photoX,
      photoY,
      font,
      openingAnimation,
      doorColor: theme.doorColor.toLowerCase(),
      textColor: theme.textColor.toLowerCase(),
      decorationColor: theme.decorationColor.toLowerCase(),
      shape: theme.shape,
      decoration: theme.decoration
    },
    doors,
    doorOrder: doorOrder.slice()
  };
}

function bytesToBase64Url(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i += 0x8000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function base64UrlToBytes(encoded) {
  const normalized = encoded.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(normalized + "=".repeat((4 - normalized.length % 4) % 4));
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

function compactCalendar(value) {
  const normalized = validateCalendar(value);
  const theme = normalized.theme;
  return {
    v: 2,
    t: normalized.title,
    s: normalized.subtitle,
    h: [
      theme.backgroundColor, theme.coverImage, theme.photoSide, theme.photoWidth, theme.photoZoom,
      theme.photoX, theme.photoY, theme.font, theme.openingAnimation, theme.doorColor,
      theme.textColor, theme.decorationColor, theme.shape, theme.decoration
    ],
    o: normalized.doorOrder,
    d: normalized.doors.map((door) => [
      door.title, door.message, door.image, door.decoration, door.shape,
      door.openingAnimation, door.doorColor, door.textColor, door.decorationColor
    ])
  };
}

function expandCompactCalendar(value) {
  if (!value || value.v !== 2 || !Array.isArray(value.h) || !Array.isArray(value.d)) {
    throw new Error("Ce lien ne contient pas un calendrier valide.");
  }
  const [backgroundColor, coverImage, photoSide, photoWidth, photoZoom, photoX, photoY, font,
    openingAnimation, doorColor, textColor, decorationColor, shape, decoration] = value.h;
  return validateCalendar({
    title: value.t,
    subtitle: value.s,
    doorOrder: value.o,
    theme: { backgroundColor, coverImage, photoSide, photoWidth, photoZoom, photoX, photoY, font, openingAnimation, doorColor, textColor, decorationColor, shape, decoration },
    doors: value.d.map((door) => {
      if (!Array.isArray(door) || door.length !== 9) throw new Error("Une case de ce calendrier est illisible.");
      const [title, message, image, doorDecoration, doorShape, doorAnimation, doorColorOverride, textColorOverride, decorationColorOverride] = door;
      return { title, message, image, decoration: doorDecoration, shape: doorShape, openingAnimation: doorAnimation, doorColor: doorColorOverride, textColor: textColorOverride, decorationColor: decorationColorOverride };
    })
  });
}

async function encodeCalendar(calendar) {
  const bytes = new TextEncoder().encode(JSON.stringify(compactCalendar(calendar)));
  if (typeof CompressionStream === "function") {
    const stream = new Blob([bytes]).stream().pipeThrough(new CompressionStream("gzip"));
    return `AV2G.${bytesToBase64Url(new Uint8Array(await new Response(stream).arrayBuffer()))}`;
  }
  return `AV2.${bytesToBase64Url(bytes)}`;
}

async function decodeCalendar(code) {
  const trimmed = code.trim();
  const match = /^(AV2G|AV2|AV1G|AV1)\.([A-Za-z0-9_-]+)$/.exec(trimmed);
  if (!match) throw new Error("Le lien du calendrier semble incomplet.");
  let bytes = base64UrlToBytes(match[2]);
  if (match[1].endsWith("G")) {
    if (typeof DecompressionStream !== "function") {
      throw new Error("Ton navigateur ne peut pas ouvrir ces données de partage. Essaie une version récente de Chrome, Firefox ou Safari.");
    }
    const stream = new Blob([bytes]).stream().pipeThrough(new DecompressionStream("gzip"));
    bytes = new Uint8Array(await new Response(stream).arrayBuffer());
  }
  try {
    const value = JSON.parse(new TextDecoder().decode(bytes));
    return match[1].startsWith("AV2") ? expandCompactCalendar(value) : validateCalendar(value);
  } catch (error) {
    if (error instanceof SyntaxError) throw new Error("Le contenu du calendrier est abîmé ou incomplet.");
    throw error;
  }
}

function getSharePageUrl(currentUrl = window.location.href) {
  const pageUrl = new URL(currentUrl);
  const hostname = pageUrl.hostname.toLowerCase();
  const isPrivateIpv4 = /^(10|127)\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(hostname)
    || /^192\.168\.\d{1,3}\.\d{1,3}$/.test(hostname)
    || /^172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}$/.test(hostname);
  if (pageUrl.protocol === "file:" || !hostname || hostname === "localhost"
    || hostname.endsWith(".localhost") || hostname.endsWith(".local")
    || hostname === "::1" || hostname === "0.0.0.0" || isPrivateIpv4) {
    throw new Error("Cette page est ouverte depuis un fichier ou une adresse locale. Pour partager le calendrier, publie d'abord ce dossier sur un hébergement web public, puis crée le lien depuis cette adresse.");
  }
  pageUrl.hash = "";
  return pageUrl;
}

let supabaseClient = null;
let accountUser = null;
let accountReady = false;
let accountSetupError = "";
let pendingCloudCalendars = new Map();
let cloudSaveTimer = null;
let cloudSavePromise = null;

function setAccountMessage(message, isError = false) {
  elements.accountSetupMessage.textContent = message;
  elements.accountSetupMessage.classList.toggle("is-error", isError);
}

function setAccountUser(user) {
  accountUser = user;
  elements.accountFields.hidden = Boolean(user);
  elements.accountSignedIn.hidden = !user;
  elements.accountUserLabel.textContent = user
    ? `Connecté avec ${user.email}. Tes ${calendarLibrary.length} calendriers sont synchronisés avec ton compte.`
    : "";
  elements.accountButton.textContent = user ? "Mon compte ✓" : "Mon compte";
  elements.accountButton.title = user ? `Connecté avec ${user.email}` : "Créer un compte pour sauvegarder ton calendrier en ligne";
}

function hasSupabaseConfig() {
  const config = window.ADVENT_CALENDAR_SUPABASE;
  return Boolean(config && typeof config.url === "string" && config.url.trim()
    && typeof config.anonKey === "string" && config.anonKey.trim());
}

async function configureSupabaseClient() {
  if (supabaseClient) return supabaseClient;
  const config = window.ADVENT_CALENDAR_SUPABASE;
  if (!hasSupabaseConfig()) throw new Error("Les comptes ne sont pas encore activés sur ce site : le propriétaire doit configurer un projet Supabase et sa clé publique. Consulte les étapes d'activation.");
  let projectUrl;
  try {
    projectUrl = new URL(config.url);
  } catch {
    throw new Error("L’URL du projet Supabase dans account-config.js n’est pas valide.");
  }
  if (projectUrl.protocol !== "https:" && projectUrl.hostname !== "localhost") {
    throw new Error("L’URL de Supabase doit utiliser HTTPS.");
  }

  try {
    const { createClient } = await import(SUPABASE_CLIENT_MODULE);
    supabaseClient = createClient(projectUrl.origin, config.anonKey, {
      auth: { autoRefreshToken: true, persistSession: true, detectSessionInUrl: false }
    });
  } catch (error) {
    throw new Error(`Le service de comptes est inaccessible : ${error.message}`);
  }
  return supabaseClient;
}

async function writeCalendarToCloud(value, ownerId, calendarId) {
  const { error } = await supabaseClient
    .from(CLOUD_CALENDARS_TABLE)
    .upsert({
      owner_id: ownerId,
      calendar_id: calendarId,
      calendar: validateCalendar(value),
      updated_at: new Date().toISOString()
    }, { onConflict: "owner_id,calendar_id" });
  if (error) throw new Error(`La sauvegarde en ligne a échoué : ${error.message}`);
}

async function deleteCalendarFromCloud(calendarId) {
  if (!accountReady || !accountUser) return;
  const { error } = await supabaseClient
    .from(CLOUD_CALENDARS_TABLE)
    .delete()
    .eq("owner_id", accountUser.id)
    .eq("calendar_id", calendarId);
  if (error) throw new Error(`La suppression en ligne a échoué : ${error.message}`);
}

function persistCalendarLibrary() {
  localStorage.setItem(LIBRARY_KEY, JSON.stringify(calendarLibrary));
  localStorage.setItem(ACTIVE_CALENDAR_KEY, activeCalendarId);
  const activeEntry = calendarLibrary.find((entry) => entry.id === activeCalendarId);
  if (activeEntry) localStorage.setItem(STORAGE_KEY, JSON.stringify(activeEntry.calendar));
}

function createCalendarId() {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  bytes[6] = (bytes[6] & 0x0f) | 0x40;
  bytes[8] = (bytes[8] & 0x3f) | 0x80;
  const hex = [...bytes].map((byte) => byte.toString(16).padStart(2, "0")).join("");
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function makeCalendarEntry(value = emptyCalendar(), id = createCalendarId()) {
  return { id, calendar: validateCalendar(value) };
}

function saveCalendarLibrary() {
  try {
    persistCalendarLibrary();
  } catch (error) {
    showStatus(`Impossible d'enregistrer la bibliothèque de calendriers sur cet appareil : ${error.message}`, true);
    throw error;
  }
}

function loadCalendarLibrary() {
  const savedLibrary = localStorage.getItem(LIBRARY_KEY);
  if (savedLibrary !== null) {
    const parsed = JSON.parse(savedLibrary);
    if (!Array.isArray(parsed)) throw new Error("La bibliothèque de calendriers est illisible.");
    calendarLibrary = parsed.map((entry) => {
      if (!entry || typeof entry.id !== "string" || !entry.id) throw new Error("Un calendrier enregistré n'a pas d'identifiant valide.");
      return makeCalendarEntry(entry.calendar, entry.id);
    });
  }
  if (!calendarLibrary.length) {
    calendarLibrary = [makeCalendarEntry(loadDraft())];
  }
  const storedActiveId = localStorage.getItem(ACTIVE_CALENDAR_KEY);
  activeCalendarId = calendarLibrary.some((entry) => entry.id === storedActiveId)
    ? storedActiveId
    : calendarLibrary[0].id;
  calendar = calendarLibrary.find((entry) => entry.id === activeCalendarId).calendar;
  saveCalendarLibrary();
}

function selectCalendar(calendarId) {
  const selected = calendarLibrary.find((entry) => entry.id === calendarId);
  if (!selected) throw new Error("Ce calendrier n'existe plus dans ta bibliothèque.");
  activeCalendarId = selected.id;
  calendar = selected.calendar;
  saveCalendarLibrary();
  renderCalendar();
  elements.themeDecoration.value = calendar.theme.decoration;
}

async function loadCreatorCalendar(user) {
  accountReady = false;
  const { data, error } = await supabaseClient
    .from(CLOUD_CALENDARS_TABLE)
    .select("calendar_id,calendar,updated_at")
    .eq("owner_id", user.id)
    .order("updated_at", { ascending: false });
  if (error) throw new Error(`Impossible de charger ton calendrier : ${error.message}`);

  if (data.length) {
    calendarLibrary = data.map((row) => makeCalendarEntry(row.calendar, row.calendar_id));
  } else {
    calendarLibrary = calendarLibrary.length ? calendarLibrary : [makeCalendarEntry(calendar)];
    for (const entry of calendarLibrary) await writeCalendarToCloud(entry.calendar, user.id, entry.id);
  }
  const previousId = activeCalendarId;
  activeCalendarId = calendarLibrary.some((entry) => entry.id === previousId) ? previousId : calendarLibrary[0].id;
  calendar = calendarLibrary.find((entry) => entry.id === activeCalendarId).calendar;
  try {
    persistCalendarLibrary();
  } catch (error) {
    showStatus(`Les calendriers sont chargés depuis ton compte, mais la copie locale n’a pas pu être mise à jour : ${error.message}`, true);
  }
  accountReady = true;
  renderCalendar();
  elements.themeDecoration.value = calendar.theme.decoration;
  setAccountUser(user);
  renderCalendarLibrary();
  setAccountMessage(data.length
    ? `${data.length} calendrier${data.length > 1 ? "s" : ""} chargé${data.length > 1 ? "s" : ""} depuis ton compte.`
    : `${calendarLibrary.length} calendrier${calendarLibrary.length > 1 ? "s" : ""} enregistré${calendarLibrary.length > 1 ? "s" : ""} dans ton compte.`);
}

function scheduleCloudSave(value, calendarId) {
  if (!accountReady || !accountUser || isReader) return;
  pendingCloudCalendars.set(calendarId, value);
  window.clearTimeout(cloudSaveTimer);
  cloudSaveTimer = window.setTimeout(() => { void flushCloudCalendar(); }, 700);
}

async function flushCloudCalendar() {
  window.clearTimeout(cloudSaveTimer);
  if (cloudSavePromise) {
    const saveFailed = await cloudSavePromise;
    if (!saveFailed && accountReady && accountUser && pendingCloudCalendars.size) await flushCloudCalendar();
    return;
  }
  if (!accountReady || !accountUser || !pendingCloudCalendars.size) return;
  const saveOperation = (async () => {
    let saveFailed = false;
    while (accountReady && accountUser && pendingCloudCalendars.size) {
      const [calendarId, snapshot] = pendingCloudCalendars.entries().next().value;
      pendingCloudCalendars.delete(calendarId);
      try {
        await writeCalendarToCloud(snapshot, accountUser.id, calendarId);
        setAccountMessage("Tes calendriers sont synchronisés avec ton compte.");
      } catch (error) {
        if (!pendingCloudCalendars.has(calendarId)) pendingCloudCalendars.set(calendarId, snapshot);
        saveFailed = true;
        setAccountMessage(`${error.message} Réessaie la synchronisation avant de te déconnecter.`, true);
        showStatus(`${error.message} La dernière version reste enregistrée sur cet appareil.`, true);
        break;
      }
    }
    return saveFailed;
  })();
  cloudSavePromise = saveOperation;
  let saveFailed;
  try {
    saveFailed = await saveOperation;
  } finally {
    if (cloudSavePromise === saveOperation) cloudSavePromise = null;
  }
  if (!saveFailed && accountReady && accountUser && pendingCloudCalendars.size) await flushCloudCalendar();
}

async function initializeCreatorAccount() {
  if (isReader) return;
  const config = window.ADVENT_CALENDAR_SUPABASE;
  if (!config || !config.url || !config.anonKey) return;
  try {
    await configureSupabaseClient();
    const { data, error } = await supabaseClient.auth.getSession();
    if (error) throw error;
    if (data.session) {
      await loadCreatorCalendar(data.session.user);
      accountSetupError = "";
    }
  } catch (error) {
    accountSetupError = error.message;
    setAccountMessage(accountSetupError, true);
  }
}

function loadDraft() {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved === null ? emptyCalendar() : validateCalendar(JSON.parse(saved));
}

let calendar;
let calendarLibrary = [];
let activeCalendarId = null;
let isReader = false;
let openedDays = new Set();
let openedStorageKey = null;
let editingDay = null;
let revealedDay = null;
let pendingImage = "";
let pendingDecoration = "snow";
let pendingDoorShape = null;
let pendingDoorAnimation = null;
let pendingDoorColors = null;
let pendingTheme = null;
let coverImageRequestId = 0;
let imageRequestId = 0;
let imageBusy = false;
let statusTimer;
const burstTimers = new WeakMap();

function showStatus(message, isError) {
  window.clearTimeout(statusTimer);
  elements.status.textContent = message;
  elements.status.classList.toggle("is-error", Boolean(isError));
  statusTimer = window.setTimeout(() => { elements.status.textContent = ""; }, 5000);
}

function lastUnlockedDoor(date = new Date()) {
  if (date.getMonth() !== 11) return 0;
  return Math.min(date.getDate(), DOOR_COUNT);
}

function isDoorUnlocked(index, date = new Date()) {
  return index < lastUnlockedDoor(date);
}

function updateDoorAvailability(button, index) {
  const opened = isReader && openedDays.has(index);
  const unlocked = !isReader || opened || isDoorUnlocked(index);
  button.classList.toggle("is-opened", opened);
  button.classList.toggle("is-locked", !unlocked);
  button.disabled = !unlocked;
  button.setAttribute("aria-label", opened
    ? `Revoir la case ${index + 1}, déjà ouverte`
    : unlocked
      ? `Ouvrir la case ${index + 1}`
      : `Case ${index + 1} verrouillée jusqu'au ${decemberDayLabel(index)} décembre`);
  if (!unlocked) button.title = `S'ouvrira le ${decemberDayLabel(index)} décembre`;
  else button.removeAttribute("title");
}

function openedDaysKey(value) {
  const serialized = JSON.stringify(value);
  let firstHash = 2166136261;
  let secondHash = 5381;
  for (let index = 0; index < serialized.length; index++) {
    const code = serialized.charCodeAt(index);
    firstHash = Math.imul(firstHash ^ code, 16777619);
    secondHash = Math.imul(secondHash, 33) ^ code;
  }
  const suffix = `${(firstHash >>> 0).toString(16)}${(secondHash >>> 0).toString(16)}`;
  return `${STORAGE_KEY}-opened-${suffix}`;
}

function loadOpenedDays(value) {
  openedStorageKey = openedDaysKey(value);
  openedDays = new Set();
  try {
    const saved = localStorage.getItem(openedStorageKey);
    if (saved === null) return;
    const days = JSON.parse(saved);
    if (!Array.isArray(days) || days.some((day) => !Number.isInteger(day) || day < 0 || day >= DOOR_COUNT)) {
      throw new Error("La liste des cases ouvertes est illisible.");
    }
    openedDays = new Set(days);
  } catch (error) {
    openedDays.clear();
    showStatus(`La progression du calendrier n'a pas pu être chargée : ${error.message}`, true);
  }
}

function markDoorOpened(index) {
  if (openedDays.has(index)) return;
  openedDays.add(index);
  try {
    localStorage.setItem(openedStorageKey, JSON.stringify([...openedDays]));
  } catch (error) {
    showStatus("La case est ouverte, mais sa progression ne peut pas être enregistrée dans ce navigateur.", true);
  }
}

function saveCalendar(next) {
  const normalized = validateCalendar(next);
  const entryIndex = calendarLibrary.findIndex((entry) => entry.id === activeCalendarId);
  if (entryIndex === -1) throw new Error("Le calendrier actif n'existe plus dans ta bibliothèque.");
  const previous = calendarLibrary[entryIndex];
  calendarLibrary[entryIndex] = { ...previous, calendar: normalized };
  try {
    persistCalendarLibrary();
  } catch (error) {
    calendarLibrary[entryIndex] = previous;
    showStatus("Enregistrement impossible dans ce navigateur. L'image est peut-être trop volumineuse.", true);
    throw error;
  }
  calendar = normalized;
  renderCalendar();
  scheduleCloudSave(normalized, activeCalendarId);
}

function renderCalendarLibrary() {
  if (!elements.calendarLibraryList) return;
  elements.calendarLibraryList.replaceChildren();
  const active = calendarLibrary.find((entry) => entry.id === activeCalendarId);
  elements.activeCalendarLabel.textContent = active ? active.calendar.title : "";
  calendarLibrary.forEach((entry) => {
    const row = document.createElement("div");
    row.className = "calendar-library-item";
    row.classList.toggle("is-current", entry.id === activeCalendarId);
    const select = document.createElement("button");
    select.type = "button";
    select.className = "calendar-library-select";
    select.textContent = `${entry.calendar.title}${entry.id === activeCalendarId ? " · ouvert" : ""}`;
    select.setAttribute("aria-current", entry.id === activeCalendarId ? "true" : "false");
    select.addEventListener("click", () => {
      try {
        selectCalendar(entry.id);
        elements.calendarLibraryDialog.close();
        showStatus(`« ${calendar.title} » est ouvert.`);
      } catch (error) {
        showStatus(error.message, true);
      }
    });
    const remove = document.createElement("button");
    remove.type = "button";
    remove.className = "calendar-library-delete";
    remove.textContent = "Supprimer";
    remove.setAttribute("aria-label", `Supprimer le calendrier ${entry.calendar.title}`);
    remove.addEventListener("click", () => { void removeCalendar(entry.id); });
    row.append(select, remove);
    elements.calendarLibraryList.append(row);
  });
}

async function removeCalendar(calendarId) {
  const entry = calendarLibrary.find((item) => item.id === calendarId);
  if (!entry) return;
  if (!window.confirm(`Supprimer définitivement « ${entry.calendar.title} » ?`)) return;
  const remaining = calendarLibrary.filter((item) => item.id !== calendarId);
  if (!remaining.length) remaining.push(makeCalendarEntry(emptyCalendar()));
  const previousLibrary = calendarLibrary;
  const previousActiveId = activeCalendarId;
  try {
    if (accountReady && accountUser) {
      await flushCloudCalendar();
      if (pendingCloudCalendars.has(calendarId)) throw new Error("Ce calendrier n'est pas encore synchronisé. Réessaie la suppression après la synchronisation.");
      await deleteCalendarFromCloud(calendarId);
      pendingCloudCalendars.delete(calendarId);
    }
    calendarLibrary = remaining;
    if (activeCalendarId === calendarId) activeCalendarId = remaining[0].id;
    calendar = calendarLibrary.find((item) => item.id === activeCalendarId).calendar;
    saveCalendarLibrary();
    renderCalendar();
    renderCalendarLibrary();
    showStatus(`« ${entry.calendar.title} » a été supprimé.`);
  } catch (error) {
    calendarLibrary = previousLibrary;
    activeCalendarId = previousActiveId;
    calendar = previousLibrary.find((item) => item.id === previousActiveId).calendar;
    renderCalendarLibrary();
    showStatus(error.message, true);
  }
}

function createCalendar() {
  let nextNumber = 2;
  while (calendarLibrary.some((entry) => entry.calendar.title === `Mon calendrier ${nextNumber}`)) nextNumber++;
  const entry = makeCalendarEntry({ ...emptyCalendar(), title: `Mon calendrier ${nextNumber}` });
  const previousId = activeCalendarId;
  const previousCalendar = calendar;
  calendarLibrary.push(entry);
  activeCalendarId = entry.id;
  calendar = entry.calendar;
  try {
    saveCalendarLibrary();
    renderCalendar();
    renderCalendarLibrary();
    elements.calendarLibraryDialog.close();
    scheduleCloudSave(calendar, entry.id);
    showStatus("Nouveau calendrier créé. Tu peux maintenant le personnaliser.");
  } catch (error) {
    calendarLibrary = calendarLibrary.filter((item) => item.id !== entry.id);
    activeCalendarId = previousId;
    calendar = previousCalendar;
    renderCalendar();
    renderCalendarLibrary();
    showStatus(`Impossible de créer ce calendrier : ${error.message}`, true);
  }
}

function renderCalendar() {
  const theme = calendar.theme;
  document.documentElement.style.setProperty("--canvas", theme.backgroundColor);
  document.documentElement.dataset.font = theme.font;
  document.querySelector('meta[name="theme-color"]').content = theme.backgroundColor;
  renderCoverPhoto(theme);
  elements.introArt.hidden = Boolean(theme.coverImage);
  elements.grid.dataset.shape = theme.shape;
  elements.grid.style.setProperty("--calendar-door-color", theme.doorColor);
  elements.grid.style.setProperty("--calendar-text-color", theme.textColor);
  elements.grid.style.setProperty("--calendar-decoration-color", theme.decorationColor);
  elements.grid.dataset.opening = theme.openingAnimation;
  elements.grid.replaceChildren();
  calendar.doorOrder.forEach((dayIndex) => {
    const door = calendar.doors[dayIndex];
    const decoration = theme.decoration === "individual" ? door.decoration || "snow" : theme.decoration;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "door";
    button.dataset.dayIndex = String(dayIndex);
    button.dataset.filled = String(Boolean(door.title.trim() || door.message.trim() || door.image));
    button.dataset.decoration = decoration;
    button.dataset.shape = door.shape || theme.shape;
    button.dataset.opening = door.openingAnimation || theme.openingAnimation;
    updateDoorAvailability(button, dayIndex);
    button.style.setProperty("--calendar-door-color", door.doorColor || theme.doorColor);
    button.style.setProperty("--calendar-text-color", door.textColor || theme.textColor);
    button.style.setProperty("--calendar-decoration-color", door.decorationColor || theme.decorationColor);
    const number = document.createElement("span");
    number.className = "door-number";
    number.textContent = String(dayIndex + 1);
    const sparkle = document.createElement("span");
    sparkle.className = "door-sparkle";
    sparkle.setAttribute("aria-hidden", "true");
    sparkle.className = "door-decoration";
    sparkle.textContent = DECORATIONS[decoration].symbols[dayIndex % DECORATIONS[decoration].symbols.length];
    button.append(number, sparkle);
    button.addEventListener("click", () => openDoor(dayIndex, button));
    elements.grid.append(button);
  });

  elements.title.value = calendar.title;
  elements.title.readOnly = isReader;
  elements.title.setAttribute("aria-label", isReader ? "Titre du calendrier partagé" : "Titre de votre calendrier");
  fitCalendarTitle();
  elements.badge.hidden = !isReader;
  elements.shareButton.hidden = isReader;
  elements.accountButton.hidden = isReader;
  elements.calendarLibraryButton.hidden = isReader;
  elements.themeButton.hidden = isReader;
  elements.exitReaderButton.hidden = !isReader;
  elements.shuffleDoorsButton.hidden = isReader;
  elements.resetDoorsOrderButton.hidden = isReader || isDefaultDoorOrder(calendar.doorOrder);
  elements.caption.textContent = isReader
    ? calendar.subtitle || "Un calendrier préparé rien que pour toi. Ouvre une case chaque jour !"
    : calendar.subtitle;
  elements.hint.textContent = isReader
    ? "Une case se déverrouille chaque jour en décembre. Les cases déjà ouvertes restent accessibles."
    : "Choisis une case pour y glisser une surprise.";
  elements.editFromReveal.hidden = isReader;
  renderCalendarLibrary();
}

function fitCalendarTitle() {
  const input = elements.title;
  input.style.height = "auto";
  input.style.height = `${input.scrollHeight}px`;
}

function renderCoverPhoto(theme) {
  const hasImage = Boolean(theme.coverImage);
  elements.introPhotoFrame.hidden = !hasImage;
  elements.introArt.hidden = hasImage;
  const intro = elements.introPhotoFrame.closest(".intro");
  intro.classList.toggle("has-cover-image", hasImage);
  intro.classList.toggle("photo-left", theme.photoSide === "left");
  elements.introPhotoFrame.dataset.side = theme.photoSide;
  elements.introPhotoFrame.style.setProperty("--photo-width", `${theme.photoWidth}%`);
  elements.introPhotoFrame.style.setProperty("--photo-zoom", theme.photoZoom / 100);
  elements.introPhoto.style.setProperty("--photo-x", `${theme.photoX}%`);
  elements.introPhoto.style.setProperty("--photo-y", `${theme.photoY}%`);
  if (hasImage) elements.introPhoto.src = theme.coverImage;
  else elements.introPhoto.removeAttribute("src");
}

function openDoor(index, button) {
  if (isReader) {
    if (!openedDays.has(index) && !isDoorUnlocked(index)) {
      showStatus(`Cette case s'ouvrira le ${decemberDayLabel(index)} décembre.`);
      return;
    }
    markDoorOpened(index);
    button.classList.add("is-opened");
    button.classList.remove("is-opening");
    void button.offsetWidth;
    button.classList.add("is-opening");
    showReveal(index);
  }
  else {
    button.classList.remove("is-opening");
    void button.offsetWidth;
    button.classList.add("is-opening");
    editingDay = index;
    imageRequestId++;
    imageBusy = false;
    elements.saveSurpriseButton.disabled = false;
    pendingImage = calendar.doors[index].image;
    pendingDecoration = calendar.doors[index].decoration || "snow";
    pendingDoorAnimation = calendar.doors[index].openingAnimation || "calendar";
    elements.editHeading.textContent = `Case du ${decemberDayLabel(index)} décembre`;
    elements.surpriseTitle.value = calendar.doors[index].title;
    elements.surpriseMessage.value = calendar.doors[index].message;
    elements.surpriseDecoration.value = pendingDecoration;
    elements.surpriseOpeningAnimation.value = pendingDoorAnimation;
    pendingDoorShape = calendar.doors[index].shape || "calendar";
    elements.surpriseShape.value = pendingDoorShape;
    pendingDoorColors = {
      doorColor: calendar.doors[index].doorColor,
      textColor: calendar.doors[index].textColor,
      decorationColor: calendar.doors[index].decorationColor
    };
    syncDoorColorForm();
    updateDecorationPreview();
    updateDoorShapePreview();
    updateDoorColorPreview();
    elements.surpriseImage.value = "";
    updateImagePreview();
    elements.editDialog.showModal();
  }
}

function showReveal(index) {
  revealedDay = index;
  const door = calendar.doors[index];
  const theme = calendar.theme;
  const decoration = theme.decoration === "individual" ? door.decoration || "snow" : theme.decoration;
  const doorColor = door.doorColor || theme.doorColor;
  const textColor = door.textColor || theme.textColor;
  const decorationColor = door.decorationColor || theme.decorationColor;
  const openingAnimation = door.openingAnimation || theme.openingAnimation;
  const hasText = Boolean(door.title.trim() || door.message.trim());
  elements.revealDay.textContent = decemberDayLabel(index);
  elements.revealTitle.textContent = door.title || (hasText ? "Une pensée pour toi" : "");
  elements.revealMessage.textContent = door.message;
  elements.revealMessage.hidden = !door.message;
  elements.revealEmpty.hidden = hasText || Boolean(door.image);
  elements.revealImage.hidden = !door.image;
  elements.revealImage.classList.remove("is-emerging");
  elements.revealImage.src = door.image;
  elements.revealImage.alt = `Image de la surprise du ${decemberDayLabel(index)} décembre`;
  elements.revealOpeningScene.dataset.decoration = decoration;
  elements.revealOpeningScene.dataset.shape = door.shape || theme.shape;
  elements.revealOpeningScene.dataset.opening = openingAnimation;
  elements.revealOpeningScene.style.setProperty("--calendar-door-color", doorColor);
  elements.revealOpeningScene.style.setProperty("--calendar-text-color", textColor);
  elements.revealOpeningScene.style.setProperty("--calendar-decoration-color", decorationColor);
  elements.revealOpeningScene.style.setProperty("--decoration-color", decorationColor);
  elements.revealDoorNumber.textContent = String(index + 1);
  elements.revealDoorSymbol.textContent = DECORATIONS[decoration].symbols[index % DECORATIONS[decoration].symbols.length];
  emitDecorations(elements.revealBurst, decoration);
  elements.revealBurst.style.setProperty("--decoration-color", decorationColor);
  elements.revealDialog.showModal();
  restartDoorAnimation(elements.revealOpeningScene);
  if (door.image) requestAnimationFrame(() => elements.revealImage.classList.add("is-emerging"));
}

function updateDecorationPreview() {
  const decoration = DECORATIONS[pendingDecoration] || DECORATIONS.snow;
  elements.previewDoor.dataset.decoration = pendingDecoration;
  const openingAnimation = pendingDoorAnimation === "calendar" ? calendar.theme.openingAnimation : pendingDoorAnimation;
  elements.previewDoor.dataset.opening = openingAnimation;
  const decorationColor = pendingDoorColors?.decorationColor || calendar.theme.decorationColor;
  elements.previewDoor.style.setProperty("--decoration-color", decorationColor || decoration.accent);
  elements.previewDoorNumber.textContent = String((editingDay ?? 0) + 1);
  elements.previewDoorSymbol.textContent = decoration.symbols[0];
  const button = getDoorButton(editingDay);
  if (button) {
    const displayedDecoration = calendar.theme.decoration === "individual" ? pendingDecoration : calendar.theme.decoration;
    button.dataset.decoration = displayedDecoration;
    button.dataset.opening = openingAnimation;
    button.style.setProperty("--calendar-decoration-color", decorationColor || decoration.accent);
    button.querySelector(".door-decoration").textContent = DECORATIONS[displayedDecoration].symbols[(editingDay + 1) % DECORATIONS[displayedDecoration].symbols.length];
  }
}

function updateDoorShapePreview() {
  const shape = pendingDoorShape === "calendar" ? calendar.theme.shape : pendingDoorShape;
  elements.previewDoor.dataset.shape = shape;
  const button = getDoorButton(editingDay);
  if (button) button.dataset.shape = shape;
}

function renderThemePreview(theme) {
  elements.themePreview.dataset.shape = theme.shape;
  elements.themePreview.replaceChildren();
  for (let index = 0; index < 4; index++) {
    const door = document.createElement("div");
    door.className = "theme-preview-door";
    door.dataset.shape = calendar.doors[index].shape || theme.shape;
    door.style.setProperty("--calendar-door-color", calendar.doors[index].doorColor || theme.doorColor);
    door.style.setProperty("--calendar-text-color", calendar.doors[index].textColor || theme.textColor);
    door.style.setProperty("--calendar-decoration-color", calendar.doors[index].decorationColor || theme.decorationColor);
    const decoration = theme.decoration === "individual"
      ? calendar.doors[index].decoration || "snow"
      : theme.decoration;
    const number = document.createElement("span");
    number.textContent = String(index + 1);
    const motif = document.createElement("span");
    motif.textContent = DECORATIONS[decoration].symbols[index % DECORATIONS[decoration].symbols.length];
    door.append(number, motif);
    elements.themePreview.append(door);
  }
}

function readThemeForm() {
  return {
    backgroundColor: elements.themeBackgroundColor.value,
    coverImage: pendingTheme.coverImage,
    photoSide: elements.themePhotoSide.value,
    photoWidth: Number(elements.themePhotoWidth.value),
    photoZoom: Number(elements.themePhotoZoom.value),
    photoX: Number(elements.themePhotoX.value),
    photoY: Number(elements.themePhotoY.value),
    font: elements.themeFont.value,
    openingAnimation: elements.themeOpeningAnimation.value,
    doorColor: elements.themeDoorColor.value,
    textColor: elements.themeTextColor.value,
    decorationColor: elements.themeDecorationColor.value,
    shape: elements.themeShape.value,
    decoration: elements.themeDecoration.value
  };
}

function updatePendingTheme() {
  if (!pendingTheme) return;
  pendingTheme = { ...readThemeForm(), coverImage: pendingTheme.coverImage };
  document.documentElement.style.setProperty("--canvas", pendingTheme.backgroundColor);
  document.documentElement.dataset.font = pendingTheme.font;
  renderCoverPhoto(pendingTheme);
  elements.photoPositionControls.hidden = !pendingTheme.coverImage;
  elements.caption.textContent = elements.themeCaption.value.trim();
  updatePhotoPositionLabels(pendingTheme);
  elements.grid.dataset.shape = pendingTheme.shape;
  elements.grid.dataset.opening = pendingTheme.openingAnimation;
  elements.grid.style.setProperty("--calendar-door-color", pendingTheme.doorColor);
  elements.grid.style.setProperty("--calendar-text-color", pendingTheme.textColor);
  elements.grid.style.setProperty("--calendar-decoration-color", pendingTheme.decorationColor);
  elements.grid.querySelectorAll(".door").forEach((button) => {
    const dayIndex = Number(button.dataset.dayIndex);
    const door = calendar.doors[dayIndex];
    const decoration = pendingTheme.decoration === "individual" ? door.decoration || "snow" : pendingTheme.decoration;
    button.dataset.decoration = decoration;
    button.style.setProperty("--calendar-door-color", door.doorColor || pendingTheme.doorColor);
    button.style.setProperty("--calendar-text-color", door.textColor || pendingTheme.textColor);
    button.style.setProperty("--calendar-decoration-color", door.decorationColor || pendingTheme.decorationColor);
    button.dataset.shape = door.shape || pendingTheme.shape;
    button.dataset.opening = door.openingAnimation || pendingTheme.openingAnimation;
    button.querySelector(".door-decoration").textContent = DECORATIONS[decoration].symbols[dayIndex % DECORATIONS[decoration].symbols.length];
  });
  renderThemePreview(pendingTheme);
  elements.themeOpeningPreview.dataset.opening = pendingTheme.openingAnimation;
  elements.themeOpeningPreview.dataset.shape = pendingTheme.shape;
  elements.themeOpeningPreview.dataset.decoration = pendingTheme.decoration === "individual" ? "snow" : pendingTheme.decoration;
  elements.themeOpeningPreview.style.setProperty("--calendar-door-color", pendingTheme.doorColor);
  elements.themeOpeningPreview.style.setProperty("--calendar-text-color", pendingTheme.textColor);
  elements.themeOpeningPreview.style.setProperty("--calendar-decoration-color", pendingTheme.decorationColor);
  elements.themeOpeningBurst.style.setProperty("--decoration-color", pendingTheme.decorationColor);
  elements.themeOpeningSymbol.textContent = DECORATIONS[pendingTheme.decoration === "individual" ? "snow" : pendingTheme.decoration].symbols[0];
}

function updatePhotoPositionLabels(theme) {
  elements.themePhotoWidthValue.value = `${theme.photoWidth} %`;
  elements.themePhotoZoomValue.value = `${theme.photoZoom} %`;
  elements.themePhotoXValue.value = `${theme.photoX} %`;
  elements.themePhotoYValue.value = `${theme.photoY} %`;
}

function updateCoverImagePreview(image) {
  pendingTheme.coverImage = image;
  elements.coverImagePreview.hidden = !image;
  elements.photoPositionControls.hidden = !image;
  elements.coverPreviewImage.src = image;
  updatePendingTheme();
}

function openThemeEditor() {
  pendingTheme = { ...calendar.theme };
  elements.themeBackgroundColor.value = pendingTheme.backgroundColor;
  elements.themeFont.value = pendingTheme.font;
  elements.themeOpeningAnimation.value = pendingTheme.openingAnimation;
  elements.themeOpeningPreview.dataset.opening = pendingTheme.openingAnimation;
  elements.themeOpeningPreview.dataset.shape = pendingTheme.shape;
  elements.themeOpeningPreview.style.setProperty("--calendar-door-color", pendingTheme.doorColor);
  elements.themeOpeningPreview.style.setProperty("--calendar-text-color", pendingTheme.textColor);
  elements.themeOpeningPreview.style.setProperty("--calendar-decoration-color", pendingTheme.decorationColor);
  elements.themeOpeningSymbol.textContent = DECORATIONS[pendingTheme.decoration === "individual" ? "snow" : pendingTheme.decoration].symbols[0];
  elements.themeCaption.value = calendar.subtitle;
  elements.coverImagePreview.hidden = !pendingTheme.coverImage;
  elements.coverPreviewImage.src = pendingTheme.coverImage;
  elements.photoPositionControls.hidden = !pendingTheme.coverImage;
  elements.themeCoverImage.value = "";
  elements.themePhotoSide.value = pendingTheme.photoSide;
  elements.themePhotoWidth.value = String(pendingTheme.photoWidth);
  elements.themePhotoZoom.value = String(pendingTheme.photoZoom);
  elements.themePhotoX.value = String(pendingTheme.photoX);
  elements.themePhotoY.value = String(pendingTheme.photoY);
  updatePhotoPositionLabels(pendingTheme);
  elements.themeDoorColor.value = pendingTheme.doorColor;
  elements.themeTextColor.value = pendingTheme.textColor;
  elements.themeDecorationColor.value = pendingTheme.decorationColor;
  elements.themeShape.value = pendingTheme.shape;
  elements.themeDecoration.value = pendingTheme.decoration;
  updatePendingTheme();
  elements.themeDialog.showModal();
}

function emitDecorations(container, decorationName) {
  const decoration = DECORATIONS[decorationName] || DECORATIONS.snow;
  const previousTimer = burstTimers.get(container);
  if (previousTimer) window.clearTimeout(previousTimer);
  container.dataset.decoration = decorationName;
  container.style.setProperty("--decoration-color", decoration.accent);
  container.replaceChildren();
  const glow = document.createElement("span");
  glow.className = "magic-glow";
  container.append(glow);
  for (let index = 0; index < 14; index++) {
    const symbol = decoration.symbols[index % decoration.symbols.length];
    const particle = document.createElement("span");
    particle.className = `magic-particle magic-particle-${index % 4}`;
    particle.textContent = symbol;
    const angle = (index / 14) * Math.PI * 2 - Math.PI / 2;
    const radius = container === elements.previewBurst ? 44 + (index % 3) * 5 : 92 + (index % 3) * 27;
    particle.style.setProperty("--particle-x", `${Math.cos(angle) * radius}px`);
    particle.style.setProperty("--particle-y", `${Math.sin(angle) * radius - (container === elements.previewBurst ? 6 : 14)}px`);
    particle.style.setProperty("--particle-delay", `${index * 32}ms`);
    particle.style.setProperty("--particle-rotation", `${(index % 2 ? 1 : -1) * (28 + index * 8)}deg`);
    particle.style.setProperty("--particle-duration", `${780 + (index % 4) * 130}ms`);
    container.append(particle);
  }
  for (let index = 0; index < 9; index++) {
    const angle = (index / 9) * Math.PI * 2;
    const radius = container === elements.previewBurst ? 38 : 78;
    const bubble = document.createElement("span");
    bubble.className = "magic-bubble";
    bubble.style.setProperty("--particle-x", `${Math.cos(angle) * radius}px`);
    bubble.style.setProperty("--particle-y", `${Math.sin(angle) * radius}px`);
    bubble.style.setProperty("--particle-delay", `${120 + index * 48}ms`);
    bubble.style.setProperty("--bubble-size", `${6 + (index % 4) * 3}px`);
    container.append(bubble);
  }
  const duration = container === elements.previewBurst ? 1650 : 1850;
  burstTimers.set(container, window.setTimeout(() => container.replaceChildren(), duration));
}

function restartDoorAnimation(scene) {
  scene.classList.remove("is-opening");
  void scene.offsetWidth;
  scene.classList.add("is-opening");
}

function updateImagePreview() {
  elements.imagePreview.hidden = !pendingImage;
  elements.previewImage.src = pendingImage;
}

async function imageFileToDataUrl(file) {
  if (!["image/png", "image/jpeg", "image/webp", "image/gif"].includes(file.type)) {
    throw new Error("Choisis une image PNG, JPG, WebP ou GIF.");
  }
  if (file.type === "image/gif") {
    return await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(new Error("Impossible de lire cette image."));
      reader.onload = () => resolve(String(reader.result));
      reader.readAsDataURL(file);
    });
  }

  const objectUrl = URL.createObjectURL(file);
  try {
    const image = await new Promise((resolve, reject) => {
      const loaded = new Image();
      loaded.onload = () => resolve(loaded);
      loaded.onerror = () => reject(new Error("Cette image ne peut pas être ouverte."));
      loaded.src = objectUrl;
    });
    const scale = Math.min(1, 1400 / Math.max(image.naturalWidth, image.naturalHeight));
    const canvas = document.createElement("canvas");
    canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
    canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
    canvas.getContext("2d").drawImage(image, 0, 0, canvas.width, canvas.height);
    const mime = file.type === "image/png" ? "image/png" : "image/jpeg";
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, mime, .84));
    if (!blob) throw new Error("Impossible de préparer cette image.");
    return await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(new Error("Impossible de lire cette image."));
      reader.onload = () => resolve(String(reader.result));
      reader.readAsDataURL(blob);
    });
  } finally {
    URL.revokeObjectURL(objectUrl);
  }
}

elements.shuffleDoorsButton.addEventListener("click", () => {
  if (isReader) return;
  const doorOrder = calendar.doorOrder.slice();
  for (let index = doorOrder.length - 1; index > 0; index--) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [doorOrder[index], doorOrder[swapIndex]] = [doorOrder[swapIndex], doorOrder[index]];
  }
  if (doorOrder.every((dayIndex, index) => dayIndex === calendar.doorOrder[index])) {
    [doorOrder[0], doorOrder[1]] = [doorOrder[1], doorOrder[0]];
  }
  try {
    saveCalendar({ ...calendar, doorOrder });
    showStatus("Les cases ont été mélangées. Leurs numéros et leurs surprises restent associés.");
  } catch (error) {
    // saveCalendar already shows the storage error and keeps the current order.
  }
});

elements.resetDoorsOrderButton.addEventListener("click", () => {
  if (isReader) return;
  try {
    saveCalendar({ ...calendar, doorOrder: Array.from({ length: DOOR_COUNT }, (_, index) => index) });
    showStatus("Les cases sont remises dans l'ordre des dates.");
  } catch (error) {
    // saveCalendar already shows the storage error and keeps the current order.
  }
});

elements.title.addEventListener("change", () => {
  if (isReader) return;
  try {
    saveCalendar({ ...calendar, title: elements.title.value.trim() || emptyCalendar().title });
  } catch (error) {
    elements.title.value = calendar.title;
  }
});
elements.title.addEventListener("input", fitCalendarTitle);
window.addEventListener("resize", fitCalendarTitle);

elements.surpriseImage.addEventListener("change", async () => {
  const file = elements.surpriseImage.files[0];
  if (!file) return;
  const requestId = ++imageRequestId;
  imageBusy = true;
  elements.saveSurpriseButton.disabled = true;
  try {
    const image = await imageFileToDataUrl(file);
    if (requestId !== imageRequestId) return;
    pendingImage = image;
    updateImagePreview();
  } catch (error) {
    if (requestId === imageRequestId) {
      showStatus(error.message, true);
      elements.surpriseImage.value = "";
    }
  } finally {
    if (requestId === imageRequestId) {
      imageBusy = false;
      elements.saveSurpriseButton.disabled = false;
    }
  }
});

elements.removeImageButton.addEventListener("click", () => {
  imageRequestId++;
  imageBusy = false;
  elements.saveSurpriseButton.disabled = false;
  pendingImage = "";
  elements.surpriseImage.value = "";
  updateImagePreview();
});

elements.surpriseDecoration.addEventListener("change", () => {
  pendingDecoration = elements.surpriseDecoration.value;
  updateDecorationPreview();
});

elements.surpriseOpeningAnimation.addEventListener("change", () => {
  pendingDoorAnimation = elements.surpriseOpeningAnimation.value;
  updateDecorationPreview();
});

elements.surpriseShape.addEventListener("change", () => {
  pendingDoorShape = elements.surpriseShape.value;
  updateDoorShapePreview();
});

[
  [elements.surpriseDoorColor, elements.inheritDoorColor, "doorColor"],
  [elements.surpriseTextColor, elements.inheritTextColor, "textColor"],
  [elements.surpriseDecorationColor, elements.inheritDecorationColor, "decorationColor"]
].forEach(([input, inherit, key]) => {
  input.addEventListener("input", () => {
    pendingDoorColors[key] = input.value;
    inherit.checked = false;
    input.disabled = false;
    updateDoorColorPreview();
    updateDecorationPreview();
  });
  inherit.addEventListener("change", () => {
    pendingDoorColors[key] = inherit.checked ? null : input.value;
    input.disabled = inherit.checked;
    updateDoorColorPreview();
    updateDecorationPreview();
  });
});

elements.previewAnimationButton.addEventListener("click", () => {
  emitDecorations(elements.previewBurst, pendingDecoration);
  const animation = pendingDoorAnimation === "calendar" ? calendar.theme.openingAnimation : pendingDoorAnimation;
  elements.previewDoor.dataset.opening = animation;
  restartDoorAnimation(elements.previewDoor);
});

elements.themeOpeningPreviewButton.addEventListener("click", () => {
  const decoration = pendingTheme.decoration === "individual" ? "snow" : pendingTheme.decoration;
  emitDecorations(elements.themeOpeningBurst, decoration);
  elements.themeOpeningBurst.style.setProperty("--decoration-color", pendingTheme.decorationColor);
  restartDoorAnimation(elements.themeOpeningPreview);
});

elements.themeDecoration.replaceChildren();
const individualDecorationOption = document.createElement("option");
individualDecorationOption.value = "individual";
individualDecorationOption.textContent = "Garder les décorations choisies par case";
elements.themeDecoration.append(individualDecorationOption);
Object.entries(DECORATIONS).forEach(([name, decoration]) => {
  const option = document.createElement("option");
  option.value = name;
  option.textContent = decoration.label;
  elements.themeDecoration.append(option);
});
Object.entries(OPENING_ANIMATIONS).forEach(([name, label]) => {
  const option = document.createElement("option");
  option.value = name;
  option.textContent = label;
  elements.themeOpeningAnimation.append(option);
});
const inheritOpeningAnimationOption = document.createElement("option");
inheritOpeningAnimationOption.value = "calendar";
inheritOpeningAnimationOption.textContent = "Suivre l'animation générale du calendrier";
elements.surpriseOpeningAnimation.append(inheritOpeningAnimationOption);
Object.entries(OPENING_ANIMATIONS).forEach(([name, label]) => {
  const option = document.createElement("option");
  option.value = name;
  option.textContent = label;
  elements.surpriseOpeningAnimation.append(option);
});

function fillShapeSelect(select, includeCalendarShape) {
  select.replaceChildren();
  if (includeCalendarShape) {
    const inheritedOption = document.createElement("option");
    inheritedOption.value = "calendar";
    inheritedOption.textContent = "Suivre la forme générale du calendrier";
    select.append(inheritedOption);
  }
  Object.entries(SHAPES).forEach(([name, label]) => {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = label;
    select.append(option);
  });
}

fillShapeSelect(elements.themeShape, false);
fillShapeSelect(elements.surpriseShape, true);

elements.themeButton.addEventListener("click", openThemeEditor);
[elements.themeBackgroundColor, elements.themeDoorColor, elements.themeTextColor, elements.themeDecorationColor, elements.themeShape, elements.themeDecoration, elements.themeFont, elements.themeOpeningAnimation, elements.themePhotoSide, elements.themePhotoWidth, elements.themePhotoZoom, elements.themePhotoX, elements.themePhotoY]
  .forEach((input) => {
    input.addEventListener("input", updatePendingTheme);
    input.addEventListener("change", updatePendingTheme);
  });
elements.themeCaption.addEventListener("input", updatePendingTheme);

elements.themeCoverImage.addEventListener("change", async () => {
  const file = elements.themeCoverImage.files[0];
  if (!file) return;
  const requestId = ++coverImageRequestId;
  elements.saveThemeButton.disabled = true;
  try {
    const image = await imageFileToDataUrl(file);
    if (requestId === coverImageRequestId && pendingTheme) updateCoverImagePreview(image);
  } catch (error) {
    if (requestId === coverImageRequestId) showStatus(error.message, true);
  } finally {
    if (requestId === coverImageRequestId) elements.saveThemeButton.disabled = false;
  }
});

elements.removeCoverImageButton.addEventListener("click", () => {
  coverImageRequestId++;
  elements.themeCoverImage.value = "";
  updateCoverImagePreview("");
});

elements.themeForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (!pendingTheme || isReader) return;
  try {
    saveCalendar({ ...calendar, subtitle: elements.themeCaption.value.trim(), theme: readThemeForm() });
    pendingTheme = null;
    elements.themeDialog.close();
    showStatus("Le nouveau style est appliqué à tout ton calendrier.");
  } catch (error) {
    // saveCalendar already shows the storage error and leaves the theme editor open.
  }
});

elements.themeDialog.addEventListener("close", () => {
  coverImageRequestId++;
  elements.saveThemeButton.disabled = false;
  if (pendingTheme) {
    pendingTheme = null;
    renderCalendar();
  }
});

elements.editDialog.addEventListener("close", () => {
  imageRequestId++;
  imageBusy = false;
  elements.saveSurpriseButton.disabled = false;
  if (!isReader) renderCalendar();
});

elements.revealDialog.addEventListener("close", () => {
  elements.revealImage.classList.remove("is-emerging");
  if (revealedDay !== null) getDoorButton(revealedDay)?.classList.remove("is-opening");
});

elements.editForm.addEventListener("submit", (event) => {
  event.preventDefault();
  if (editingDay === null || isReader || imageBusy) return;
  const doors = calendar.doors.slice();
  doors[editingDay] = {
    title: elements.surpriseTitle.value.trim(),
    message: elements.surpriseMessage.value.trim(),
    image: pendingImage,
    decoration: pendingDecoration,
    shape: pendingDoorShape === "calendar" ? null : pendingDoorShape,
    openingAnimation: pendingDoorAnimation === "calendar" ? null : pendingDoorAnimation,
    doorColor: pendingDoorColors.doorColor,
    textColor: pendingDoorColors.textColor,
    decorationColor: pendingDoorColors.decorationColor
  };
  try {
    saveCalendar({ ...calendar, doors });
    elements.editDialog.close();
    showStatus(`La surprise du ${decemberDayLabel(editingDay)} décembre est enregistrée.`);
  } catch (error) {
    // saveCalendar already shows the storage error and keeps the editor open.
  }
});

elements.editFromReveal.addEventListener("click", () => {
  if (isReader || revealedDay === null) return;
  elements.revealDialog.close();
  const button = getDoorButton(revealedDay);
  openDoor(revealedDay, button);
});

elements.shareButton.addEventListener("click", async () => {
  elements.shareLink.value = "Création du lien en cours...";
  elements.shareSize.textContent = "";
  elements.copyLinkButton.disabled = true;
  elements.shareDialog.showModal();
  try {
    const shareUrl = getSharePageUrl();
    const code = await encodeCalendar(calendar);
    shareUrl.hash = new URLSearchParams({ c: code }).toString();
    elements.shareLink.value = shareUrl.href;
    elements.shareSize.textContent = `Lien compact prêt à copier · ${(new Blob([elements.shareLink.value]).size / 1024).toFixed(1)} Ko`;
    elements.copyLinkButton.disabled = false;
  } catch (error) {
    elements.shareLink.value = "";
    elements.shareSize.textContent = error.message;
    showStatus(`Impossible de créer le lien : ${error.message}`, true);
  }
});

elements.copyLinkButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(elements.shareLink.value);
    showStatus("Lien copié. Tu peux l'envoyer !");
  } catch (error) {
    elements.shareLink.focus();
    elements.shareLink.select();
    showStatus("Sélectionne le lien puis copie-le avec Ctrl+C ou ⌘C.");
  }
});

elements.calendarLibraryButton.addEventListener("click", () => {
  renderCalendarLibrary();
  elements.calendarLibraryDialog.showModal();
});

elements.newCalendarButton.addEventListener("click", createCalendar);

elements.accountButton.addEventListener("click", async () => {
  elements.accountDialog.showModal();
  if (!hasSupabaseConfig()) {
    elements.accountFields.hidden = true;
    elements.accountSignedIn.hidden = true;
    elements.accountSetupLink.hidden = false;
    accountSetupError = "La création de comptes n'est pas activée sur ce site. L'inscription et la connexion resteront indisponibles jusqu'à ce que le propriétaire configure le service Supabase.";
    setAccountMessage(accountSetupError, true);
    return;
  }
  elements.accountSetupLink.hidden = true;
  elements.accountFields.hidden = Boolean(accountUser);
  if (!supabaseClient) {
    try {
      await configureSupabaseClient();
      accountSetupError = "";
      const { data, error } = await supabaseClient.auth.getSession();
      if (error) throw error;
      if (data.session) {
        await loadCreatorCalendar(data.session.user);
        accountSetupError = "";
      }
      else setAccountMessage("Connecte-toi ou crée un compte pour synchroniser tous tes calendriers entre tes appareils.");
    } catch (error) {
      accountSetupError = error.message;
      setAccountMessage(accountSetupError, true);
    }
  } else if (!accountUser && !accountSetupError) {
    setAccountMessage("Connecte-toi ou crée un compte pour synchroniser tous tes calendriers entre tes appareils.");
  } else if (accountSetupError) {
    setAccountMessage(accountSetupError, true);
  }
});

elements.accountSignUpButton.addEventListener("click", async () => {
  if (!elements.accountForm.reportValidity()) return;
  elements.accountSignUpButton.disabled = true;
  try {
    await configureSupabaseClient();
    const { data, error } = await supabaseClient.auth.signUp({
      email: elements.accountEmail.value.trim().toLowerCase(),
      password: elements.accountPassword.value
    });
    if (error) throw error;
    if (data.session) {
      await loadCreatorCalendar(data.session.user);
      accountSetupError = "";
      elements.accountPassword.value = "";
    } else {
      setAccountMessage("Compte créé. Confirme ton adresse avec le courriel reçu, puis connecte-toi.");
      elements.accountPassword.value = "";
    }
  } catch (error) {
    setAccountMessage(error.message, true);
  } finally {
    elements.accountSignUpButton.disabled = false;
  }
});

elements.accountSignInButton.addEventListener("click", async () => {
  if (!elements.accountForm.reportValidity()) return;
  elements.accountSignInButton.disabled = true;
  try {
    await configureSupabaseClient();
    const { data, error } = await supabaseClient.auth.signInWithPassword({
      email: elements.accountEmail.value.trim().toLowerCase(),
      password: elements.accountPassword.value
    });
    if (error) throw error;
    await loadCreatorCalendar(data.user);
    accountSetupError = "";
    elements.accountPassword.value = "";
  } catch (error) {
    setAccountMessage(error.message, true);
  } finally {
    elements.accountSignInButton.disabled = false;
  }
});

elements.accountSyncButton.addEventListener("click", async () => {
  if (!accountUser) return;
  elements.accountSyncButton.disabled = true;
  try {
    if (pendingCloudCalendars.size) {
      await flushCloudCalendar();
      if (pendingCloudCalendars.size) throw new Error("La sauvegarde en ligne a échoué. Vérifie ta connexion avant de réessayer.");
    } else {
      await loadCreatorCalendar(accountUser);
    }
  } catch (error) {
    setAccountMessage(error.message, true);
  } finally {
    elements.accountSyncButton.disabled = false;
  }
});

elements.accountSignOutButton.addEventListener("click", async () => {
  elements.accountSignOutButton.disabled = true;
  try {
    await flushCloudCalendar();
    if (pendingCloudCalendars.size) throw new Error("Tes calendriers n’ont pas pu être synchronisés. Réessaie avant de te déconnecter.");
    const { error } = await supabaseClient.auth.signOut();
    if (error) throw error;
    accountReady = false;
    accountUser = null;
    pendingCloudCalendars.clear();
    setAccountUser(null);
    calendar = calendarLibrary.find((entry) => entry.id === activeCalendarId)?.calendar || loadDraft();
    renderCalendar();
    setAccountMessage("Tu es déconnecté. La bibliothèque conservée sur cet appareil reste disponible.");
  } catch (error) {
    setAccountMessage(error.message, true);
  } finally {
    elements.accountSignOutButton.disabled = false;
  }
});

elements.exitReaderButton.addEventListener("click", () => {
  isReader = false;
  window.history.replaceState(null, "", window.location.href.split("#")[0]);
  try {
    calendar = calendarLibrary.find((entry) => entry.id === activeCalendarId)?.calendar || loadDraft();
    renderCalendar();
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (error) {
    isReader = true;
    showStatus(`Impossible de recharger ton calendrier : ${error.message}`, true);
  }
});

function refreshDoorLocks() {
  if (!isReader) return;
  elements.grid.querySelectorAll(".door").forEach((button) => updateDoorAvailability(button, Number(button.dataset.dayIndex)));
}

window.addEventListener("focus", refreshDoorLocks);
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") refreshDoorLocks();
});
window.setInterval(refreshDoorLocks, 60_000);

document.querySelectorAll("[data-close]").forEach((button) => {
  button.addEventListener("click", () => document.getElementById(button.dataset.close).close());
});

for (const dialog of document.querySelectorAll("dialog")) {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
}

async function initializeCalendar() {
  try {
    loadCalendarLibrary();
  } catch (error) {
    calendarLibrary = [makeCalendarEntry(emptyCalendar())];
    activeCalendarId = calendarLibrary[0].id;
    calendar = calendarLibrary[0].calendar;
    showStatus(`La bibliothèque n'a pas pu être chargée : ${error.message}`, true);
  }

  const shareParameters = new URLSearchParams(window.location.hash.slice(1));
  const sharedCode = shareParameters.get("c") || shareParameters.get("calendar");
  if (sharedCode) {
    try {
      calendar = await decodeCalendar(sharedCode);
      isReader = true;
      loadOpenedDays(calendar);
    } catch (error) {
      window.history.replaceState(null, "", window.location.href.split("#")[0]);
      showStatus(`Impossible d'ouvrir ce lien : ${error.message}`, true);
    }
  }
  elements.themeDecoration.value = calendar.theme.decoration;
  renderCalendar();
  await initializeCreatorAccount();
}

void initializeCalendar();
