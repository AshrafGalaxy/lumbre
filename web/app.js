// Browser scribe. Offerings are taken from the form, never from the model.
// The prompt matches lumbre/prompts.py.

import { pipeline } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1";

const MODEL = "onnx-community/gemma-3-270m-it-ONNX";

const SYSTEM = `You letter a card for a Día de los Muertos altar.
Use only the facts in the visitor's note.
Do not invent memories, places, foods, songs, objects, dates, relatives, or a cause of death.
If a line says "not given", do not mention that detail.
Write warm, plain English. No markdown and no bullet list.
Use exactly these two labels:

INSCRIPTION:
One or two sentences for the card. Use the person's name.

REMEMBRANCE:
One paragraph under 90 words about the memory in the note.
Mention a food, song, phrase, or object only when the note gives it.`;

const EXAMPLE = {
  name: "Rosa Mendoza",
  relationship: "a fictional grandmother for this demo",
  years: "1936-2014",
  memory:
    "On Sundays she dried marigolds on the kitchen table and kept the blue cup for whoever came home late.",
  food: "pan dulce",
  song: "a lullaby she hummed without a name",
  object: "a blue cup",
};

const OPTIONAL = [
  ["relationship", "how you knew them"],
  ["years", "the years"],
  ["food", "a favorite food"],
  ["song", "a song or phrase"],
  ["object", "an object"],
];

const fields = Object.fromEntries(
  ["name", "relationship", "years", "memory", "food", "song", "object"].map((id) => [
    id,
    document.querySelector(`#${id}`),
  ]),
);

const status = document.querySelector("#status");
const card = document.querySelector("#card");
const exampleNote = document.querySelector("#example-note");
const light = document.querySelector("#light");
let generator = null;

document.querySelector("#example").addEventListener("click", () => {
  for (const [key, value] of Object.entries(EXAMPLE)) fields[key].value = value;
  exampleNote.hidden = false;
  card.replaceChildren(paragraph("The card will appear here.", "waiting"));
});

document.querySelector("#altar-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const altar = readAltar();
  exampleNote.hidden = altar.name !== EXAMPLE.name;
  if (!altar.name) {
    status.textContent = "Write the name that should stand on the altar.";
    return;
  }
  if (altar.memory.length < 20) {
    status.textContent = "Write a memory of at least one sentence.";
    return;
  }
  light.disabled = true;
  try {
    const model = await loadModel();
    status.textContent = "Lettering the card. On this computer that can take a minute.";
    const raw = await letter(model, altar);
    const [inscription, remembrance] = parseCard(raw);
    showCard(altar, inscription, remembrance);
    status.textContent = `Lettered by ${MODEL}. Nothing was stored.`;
  } catch (error) {
    status.textContent = error instanceof Error ? error.message : "The card was not lettered.";
  } finally {
    light.disabled = false;
  }
});

function readAltar() {
  const altar = {};
  for (const [key, input] of Object.entries(fields)) {
    altar[key] = input.value.replace(/\s+/g, " ").trim();
  }
  return altar;
}

async function loadModel() {
  if (generator) return generator;
  status.textContent = "Loading Gemma 3 into this browser.";
  generator = await pipeline("text-generation", MODEL, {
    dtype: "q4f16",
    device: "wasm",
    progress_callback: (info) => {
      if (info.status === "progress" && Number.isFinite(info.progress)) {
        status.textContent = `Loading Gemma 3… ${Math.round(info.progress)}%`;
      }
    },
  });
  return generator;
}

async function letter(model, altar) {
  const output = await model(
    [
      { role: "user", content: `${SYSTEM}\n\nLetter the card from this note.\n\n${note(altar)}` },
    ],
    { max_new_tokens: 160, do_sample: false },
  );
  return replyText(output);
}

function note(altar) {
  return [
    `Name: ${altar.name}`,
    `Relationship: ${altar.relationship || "not given"}`,
    `Years: ${altar.years || "not given"}`,
    `Memory: ${altar.memory}`,
    `Food: ${altar.food || "not given"}`,
    `Song or phrase: ${altar.song || "not given"}`,
    `Object: ${altar.object || "not given"}`,
  ].join("\n");
}

function replyText(output) {
  const generated = output?.[0]?.generated_text;
  if (typeof generated === "string") return generated;
  if (Array.isArray(generated)) {
    const last = generated[generated.length - 1];
    return typeof last?.content === "string" ? last.content : "";
  }
  return "";
}

function parseCard(raw) {
  const buckets = { INSCRIPTION: [], REMEMBRANCE: [] };
  let current = null;
  for (const line of raw.split(/\r?\n/)) {
    const match = line
      .trim()
      .replace(/^#+\s*/, "")
      .match(/^(INSCRIPTION|REMEMBRANCE)\s*[:\-]\s*(.*)$/i);
    if (match) {
      current = match[1].toUpperCase();
      if (match[2].trim()) buckets[current].push(match[2].trim());
      continue;
    }
    if (current && line.trim()) buckets[current].push(line.trim());
  }
  const inscription = buckets.INSCRIPTION.join(" ").trim();
  const remembrance = buckets.REMEMBRANCE.join(" ").trim();
  if (inscription && remembrance) return [clip(inscription, 400), clip(remembrance, 1200)];
  const text = raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .join(" ");
  if (!text) throw new Error("The model returned an empty card.");
  const dot = text.indexOf(". ");
  if (dot !== -1) return [clip(text.slice(0, dot + 1), 400), clip(text.slice(dot + 2), 1200)];
  return [clip(text, 400), clip(text, 1200)];
}

function showCard(altar, inscription, remembrance) {
  const offerings = [altar.food, altar.song, altar.object].filter(Boolean);
  const gaps = OPTIONAL.filter(([key]) => !altar[key]).map(([, label]) => label);
  const root = document.createElement("div");
  root.className = "card";
  root.append(heading(altar.name));
  const meta = [altar.relationship, altar.years].filter(Boolean).join(" · ");
  if (meta) root.append(paragraph(meta, "meta"));
  root.append(paragraph(inscription, "inscription"));
  root.append(paragraph(remembrance));
  root.append(heading("As told", "h3"));
  root.append(paragraph(altar.memory));
  root.append(heading("Brought to the altar", "h3"));
  if (offerings.length) {
    const list = document.createElement("ul");
    for (const item of offerings) {
      const li = document.createElement("li");
      li.textContent = item;
      list.append(li);
    }
    root.append(list);
  } else {
    root.append(paragraph("Nothing named beyond the flowers and the flame."));
  }
  root.append(
    paragraph(
      gaps.length ? `Left unsaid: ${gaps.join(", ")}.` : "Every place we asked about was filled.",
      "small",
    ),
  );
  const save = document.createElement("button");
  save.type = "button";
  save.textContent = "Save this altar";
  save.addEventListener("click", () => downloadAltar(altar, inscription, remembrance, offerings, gaps));
  root.append(save);
  card.replaceChildren(root);
}

function downloadAltar(altar, inscription, remembrance, offerings, gaps) {
  const payload = {
    name: altar.name,
    years: altar.years,
    relationship: altar.relationship,
    memory: altar.memory,
    inscription,
    remembrance,
    offerings,
    gaps,
    model: MODEL,
  };
  const file = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(file);
  link.download = downloadName(altar.name);
  link.click();
  URL.revokeObjectURL(link.href);
}

function downloadName(name) {
  const stem = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  return `${stem || "altar"}.json`;
}

function heading(text, tag = "h2") {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}

function paragraph(text, className) {
  const node = document.createElement("p");
  if (className) node.className = className;
  node.textContent = text;
  return node;
}

function clip(text, limit) {
  return text.replace(/\s+/g, " ").trim().slice(0, limit);
}
