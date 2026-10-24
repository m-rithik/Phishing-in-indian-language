/**
 * Performance benchmarking for Fisher engine.
 *
 * Measures analysis latency for various input sizes and patterns.
 * Run: node tests/test_performance.mjs
 */

import { analyzeContent } from "../browser_extension/analyzer.mjs";
import assert from "node:assert/strict";

// Utility: Generate test message of target character count
function generateMessage(targetChars, pattern = "normal") {
  const templates = {
    normal: "This is a normal message about meeting tomorrow. ",
    phishing: "Your account is suspended! Click [URL] to verify. Send OTP. ",
    mixed: "Hi friend, can you help? Check out [URL] and let me know. ",
    urls: "Check these out: [URL1] and [URL2] and [URL3] and [URL4] ",
    repeated: "send otp send otp send otp send otp send otp ",
  };

  const template = templates[pattern] || templates.normal;
  const repetitions = Math.ceil(targetChars / template.length);
  return (template.repeat(repetitions)).substring(0, targetChars);
}

// Utility: Measure execution time
function benchmark(name, fn, iterations = 1) {
  const times = [];
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    fn();
    const end = performance.now();
    times.push(end - start);
  }

  const avg = times.reduce((a, b) => a + b, 0) / times.length;
  const min = Math.min(...times);
  const max = Math.max(...times);
  const median = times.sort((a, b) => a - b)[Math.floor(times.length / 2)];

  return { name, avg, min, max, median, iterations };
}

// Test suites
const tests = [
  {
    name: "Small message (100 chars)",
    fn: () => analyzeContent(generateMessage(100, "normal")),
    iterations: 10,
  },
  {
    name: "Medium message (1KB)",
    fn: () => analyzeContent(generateMessage(1024, "normal")),
    iterations: 10,
  },
  {
    name: "Large message (10KB)",
    fn: () => analyzeContent(generateMessage(10240, "normal")),
    iterations: 5,
  },
  {
    name: "Max message (20KB)",
    fn: () => analyzeContent(generateMessage(20000, "normal")),
    iterations: 3,
  },
  {
    name: "Phishing pattern (1KB)",
    fn: () => analyzeContent(generateMessage(1024, "phishing")),
    iterations: 10,
  },
  {
    name: "Multiple URLs (1KB, 32 URLs)",
    fn: () => analyzeContent(generateMessage(1024, "urls")),
    iterations: 10,
  },
  {
    name: "Repeated pattern (1KB)",
    fn: () => analyzeContent(generateMessage(1024, "repeated")),
    iterations: 10,
  },
  {
    name: "URL analysis (2KB link)",
    fn: () => analyzeContent(generateMessage(2048, "normal"), { mode: "url" }),
    iterations: 10,
  },
];

// Run benchmarks
console.log("Fisher Performance Benchmarks (v0.5.2)");
console.log("=====================================\n");

const results = [];
for (const test of tests) {
  try {
    const result = benchmark(test.name, test.fn, test.iterations);
    results.push(result);

    const avgMs = result.avg.toFixed(2);
    const minMs = result.min.toFixed(2);
    const maxMs = result.max.toFixed(2);
    console.log(`✓ ${result.name}`);
    console.log(`  avg=${avgMs}ms  min=${minMs}ms  max=${maxMs}ms (${result.iterations} runs)`);
  } catch (error) {
    console.error(`✗ ${test.name}: ${error.message}`);
  }
}

// Summary statistics
console.log("\n=====================================");
console.log("Summary");
console.log("=====================================");

const avgAll = results.reduce((sum, r) => sum + r.avg, 0) / results.length;
const maxAll = Math.max(...results.map(r => r.max));
const minAll = Math.min(...results.map(r => r.min));

console.log(`Total benchmarks: ${results.length}`);
console.log(`Average latency: ${avgAll.toFixed(2)}ms`);
console.log(`Min latency: ${minAll.toFixed(2)}ms`);
console.log(`Max latency: ${maxAll.toFixed(2)}ms`);

// Performance gates
console.log("\nPerformance Goals");
console.log("=====================================");

const gates = [
  { desc: "Typical message (<1KB)", target: 50, current: results[1]?.avg },
  { desc: "Large message (20KB)", target: 200, current: results[3]?.avg },
  { desc: "URL analysis (2KB)", target: 100, current: results[7]?.avg },
];

let passed = 0;
let total = 0;
for (const gate of gates) {
  if (gate.current === undefined) continue;
  total++;
  const status = gate.current <= gate.target ? "✓" : "✗";
  const ms = gate.current.toFixed(2);
  console.log(`${status} ${gate.desc}: ${ms}ms (target: ${gate.target}ms)`);
  if (gate.current <= gate.target) passed++;
}

console.log(`\nGate status: ${passed}/${total} passed`);

if (passed === total && total > 0) {
  console.log("✓ All performance gates passed!");
  process.exit(0);
} else {
  console.log("⚠ Some performance gates failed. Investigate optimizations.");
  process.exit(1);
}
