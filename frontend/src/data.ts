export type Detail = {
  eyebrow: string;
  title: string;
  value?: string;
  summary: string;
  facts: string[];
  tone?: "violet" | "cyan" | "mint" | "coral" | "amber";
};

export const datasetMetrics: Array<Detail & { id: string }> = [
  {
    id: "total",
    eyebrow: "Corpus size",
    title: "Messages",
    value: "5,572",
    summary: "The public SMS Spam Collection used by the model notebooks.",
    facts: ["4,825 ham messages", "747 spam messages", "Binary English classification"],
    tone: "violet",
  },
  {
    id: "ham",
    eyebrow: "Majority class",
    title: "Ham",
    value: "86.6%",
    summary: "Legitimate messages form the majority of the corpus.",
    facts: ["4,825 examples", "71 average characters", "Class weight: 0.577"],
    tone: "mint",
  },
  {
    id: "spam",
    eyebrow: "Minority class",
    title: "Spam",
    value: "13.4%",
    summary: "Class weighting compensates for the smaller spam sample.",
    facts: ["747 examples", "139 average characters", "Class weight: 3.730"],
    tone: "coral",
  },
  {
    id: "vocab",
    eyebrow: "Text representation",
    title: "Vocabulary",
    value: "8,439",
    summary: "The vocabulary learned from the stratified training split.",
    facts: ["100-token sequences", "Lowercase normalization", "Punctuation removed"],
    tone: "cyan",
  },
];

export const signalInsights: Array<Detail & { id: string; stat: string }> = [
  {
    id: "urls",
    eyebrow: "Strong signal",
    title: "URLs concentrate in spam",
    stat: "104 / 106",
    summary: "Nearly every message containing a URL in the corpus is labeled spam.",
    facts: ["104 spam URL messages", "2 ham URL messages", "Pattern detected during EDA"],
    tone: "coral",
  },
  {
    id: "length",
    eyebrow: "Structural signal",
    title: "Spam runs longer",
    stat: "+68 chars",
    summary: "Spam messages average almost twice the length of ham messages.",
    facts: ["Ham mean: 71 characters", "Spam mean: 139 characters", "Overall median: 61 characters"],
    tone: "amber",
  },
  {
    id: "emails",
    eyebrow: "Sparse signal",
    title: "Emails skew toward spam",
    stat: "18 / 20",
    summary: "Email addresses are uncommon, but strongly associated with spam.",
    facts: ["18 spam email messages", "2 ham email messages", "Useful supporting feature"],
    tone: "cyan",
  },
];

export const trainingMetrics: Array<Detail & { id: string }> = [
  {
    id: "accuracy",
    eyebrow: "Validation",
    title: "Accuracy",
    value: "98.8%",
    summary: "Notebook-reported peak generalization at the champion epoch.",
    facts: ["Best state near epoch 11", "Measured on stratified validation data", "Not live production telemetry"],
    tone: "violet",
  },
  {
    id: "precision",
    eyebrow: "Validation",
    title: "Precision",
    value: "97.3%",
    summary: "Most messages labeled spam were truly spam in validation.",
    facts: ["Reduces false alarms", "Threshold used in production: 0.5", "Notebook-reported metric"],
    tone: "mint",
  },
  {
    id: "recall",
    eyebrow: "Validation",
    title: "Recall",
    value: "93.5%",
    summary: "The class-weighted model catches most validation spam messages.",
    facts: ["Spam class weight: 3.730", "Ham class weight: 0.577", "Notebook-reported metric"],
    tone: "cyan",
  },
  {
    id: "params",
    eyebrow: "Model footprint",
    title: "Parameters",
    value: "143,601",
    summary: "A deliberately compact architecture selected through tuning.",
    facts: ["16-dimensional embedding", "16 Bi-LSTM units", "128-unit dense layer"],
    tone: "amber",
  },
];

export const architectureSteps: Array<Detail & { id: string; short: string }> = [
  {
    id: "vectorize",
    short: "01",
    eyebrow: "Preprocessing",
    title: "Vectorize",
    summary: "Normalize and map raw text into fixed integer sequences.",
    facts: ["Lowercase", "Strip punctuation", "Pad or truncate to 100 tokens"],
    tone: "cyan",
  },
  {
    id: "embed",
    short: "02",
    eyebrow: "Representation",
    title: "Embed",
    summary: "Learn a compact semantic representation for each vocabulary token.",
    facts: ["8,439 vocabulary entries", "16 embedding dimensions", "Trainable representation"],
    tone: "violet",
  },
  {
    id: "bilstm",
    short: "03",
    eyebrow: "Sequence model",
    title: "Bi-LSTM",
    summary: "Read message context in both forward and backward directions.",
    facts: ["16 units per direction", "32-value combined output", "44.4% dropout"],
    tone: "amber",
  },
  {
    id: "classify",
    short: "04",
    eyebrow: "Output",
    title: "Classify",
    summary: "Convert the learned representation into a spam probability.",
    facts: ["128-unit ReLU layer", "Single sigmoid output", "50% decision threshold"],
    tone: "mint",
  },
];

export const smsExamples = [
  {
    label: "Prize offer",
    text: "Congratulations! You have won a free cash prize. Call now to claim your reward.",
  },
  {
    label: "Friendly note",
    text: "Hey, are we still meeting near the station at 6 tonight?",
  },
  {
    label: "Urgent action",
    text: "URGENT! Your mobile number has been selected. Reply WIN to collect your prize.",
  },
];
