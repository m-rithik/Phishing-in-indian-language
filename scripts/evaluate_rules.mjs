#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { analyzeContent, ENGINE_VERSION } from "../browser_extension/analyzer.mjs";

const EVAL_PATH = path.resolve("eval/messages.jsonl");
const RESULTS_DIR = path.resolve("eval/results");
const METRICS_OUT = path.join(RESULTS_DIR, "rules_metrics.json");
const ERRORS_OUT = path.join(RESULTS_DIR, "rules_errors.jsonl");

function loadMessages(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }
  const content = fs.readFileSync(filePath, "utf-8").trim();
  if (!content) return [];
  return content.split("\n").map((line, idx) => {
    try {
      return JSON.parse(line.trim());
    } catch (err) {
      throw new Error(`Invalid JSON on line ${idx + 1}: ${err.message}`);
    }
  });
}

function computeMetrics(items, isPositive) {
  let tp = 0;
  let fp = 0;
  let tn = 0;
  let fn = 0;

  for (const item of items) {
    const isScam = item.label === "scam";
    const predPos = isPositive(item.analysis.risk);
    if (isScam && predPos) tp += 1;
    else if (!isScam && predPos) fp += 1;
    else if (!isScam && !predPos) tn += 1;
    else if (isScam && !predPos) fn += 1;
  }

  const precision = tp + fp > 0 ? tp / (tp + fp) : null;
  const recall = tp + fn > 0 ? tp / (tp + fn) : null;
  const f1 =
    precision !== null && recall !== null && precision + recall > 0
      ? (2 * precision * recall) / (precision + recall)
      : null;
  const fpr = fp + tn > 0 ? fp / (fp + tn) : null;

  return {
    n: items.length,
    TP: tp,
    FP: fp,
    TN: tn,
    FN: fn,
    precision: precision !== null ? Number(precision.toFixed(4)) : null,
    recall: recall !== null ? Number(recall.toFixed(4)) : null,
    f1: f1 !== null ? Number(f1.toFixed(4)) : null,
    false_positive_rate: fpr !== null ? Number(fpr.toFixed(4)) : null,
  };
}

function formatTable(name, metricsObj) {
  console.log(`\n=== ${name} ===`);
  const rows = [];
  for (const [key, m] of Object.entries(metricsObj)) {
    rows.push({
      Group: key,
      N: m.n,
      TP: m.TP,
      FP: m.FP,
      TN: m.TN,
      FN: m.FN,
      Prec: m.precision !== null ? m.precision : "N/A",
      Rec: m.recall !== null ? m.recall : "N/A",
      F1: m.f1 !== null ? m.f1 : "N/A",
      FPR: m.false_positive_rate !== null ? m.false_positive_rate : "N/A",
    });
  }
  console.table(rows);
}

function main() {
  const messages = loadMessages(EVAL_PATH);
  if (!messages.length) {
    console.error("No messages found in eval/messages.jsonl");
    process.exit(1);
  }

  let cannotAnalyzeCount = 0;
  const evaluated = messages.map((m) => {
    const analysis = analyzeContent(m.text, { mode: "message" });
    if (analysis.risk === "cannot_analyze") cannotAnalyzeCount += 1;
    return { ...m, analysis };
  });

  const settingsConfig = [
    {
      id: "high_or_review",
      label: "Positive = High or Review",
      positiveRisks: ["high", "review"],
      isPositive: (risk) => risk === "high" || risk === "review",
    },
    {
      id: "high_only",
      label: "Positive = High Only",
      positiveRisks: ["high"],
      isPositive: (risk) => risk === "high",
    },
  ];

  const results = {
    engine_version: ENGINE_VERSION,
    total_messages: evaluated.length,
    cannot_analyze: cannotAnalyzeCount,
    note: "Rule-based detector; cannot_analyze counts as not positive. Small or synthetic data gives no real-world accuracy claim.",
    settings: {},
  };

  const errors = [];

  for (const setting of settingsConfig) {
    console.log(`\n################################################`);
    console.log(`Setting: ${setting.label}`);
    console.log(`################################################`);

    // Overall
    const overall = computeMetrics(evaluated, setting.isPositive);

    // Per Language
    const byLang = {};
    const languages = [...new Set(evaluated.map((m) => m.language))].sort();
    for (const lang of languages) {
      byLang[lang] = computeMetrics(
        evaluated.filter((m) => m.language === lang),
        setting.isPositive
      );
    }

    // Per Script
    const byScript = {};
    const scripts = [...new Set(evaluated.map((m) => m.script))].sort();
    for (const script of scripts) {
      byScript[script] = computeMetrics(
        evaluated.filter((m) => m.script === script),
        setting.isPositive
      );
    }

    formatTable("Overall", { overall });
    formatTable("Per Language", byLang);
    formatTable("Per Script", byScript);

    results.settings[setting.id] = {
      positive_risks: setting.positiveRisks,
      overall,
      per_language: byLang,
      per_script: byScript,
    };

    for (const item of evaluated) {
      const isScam = item.label === "scam";
      const predPos = setting.isPositive(item.analysis.risk);
      const isError = (isScam && !predPos) || (!isScam && predPos);
      if (isError) {
        errors.push({
          setting: setting.id,
          id: item.id,
          label: item.label,
          predicted_risk: item.analysis.risk,
          reasons: item.analysis.reasons,
        });
      }
    }
  }

  if (!fs.existsSync(RESULTS_DIR)) {
    fs.mkdirSync(RESULTS_DIR, { recursive: true });
  }

  fs.writeFileSync(METRICS_OUT, JSON.stringify(results, null, 2) + "\n", "utf-8");
  fs.writeFileSync(
    ERRORS_OUT,
    errors.map((e) => JSON.stringify(e)).join("\n") + (errors.length ? "\n" : ""),
    "utf-8"
  );

  console.log(`\nWrote metrics to ${METRICS_OUT}`);
  console.log(`Wrote ${errors.length} error(s) to ${ERRORS_OUT}`);
}

main();
