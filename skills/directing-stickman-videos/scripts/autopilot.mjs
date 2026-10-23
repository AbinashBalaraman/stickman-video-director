#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import {ROOT, FFMPEG, FFPROBE, run, probe, loadProject, outputDir, save, json, hashFile, groupWords} from './autopilot-core.mjs';

const [command, ...args] = process.argv.slice(2);
const option = (flag, fallback) => args.includes(flag) ? args[args.indexOf(flag) + 1] : fallback;
async function main() {
  if (command === 'doctor') {
    const checks = {node: Number(process.versions.node.split('.')[0]) >= 20};
    for (const [name, exe] of [['ffmpeg', FFMPEG], ['ffprobe', FFPROBE]]) try { run(exe, ['-version']); checks[name] = true; } catch { checks[name] = false; }
    try { await import('@napi-rs/canvas'); checks.canvas = true; } catch { checks.canvas = false; }
    checks.fonts = ['Caveat.ttf', 'NotoSans.ttf'].every(f => { const file = path.join(ROOT, 'assets/fonts', f); return fs.existsSync(file) && fs.statSync(file).size > 10000; });
    console.log(JSON.stringify({checks, gemini_key_present: Boolean(process.env.GEMINI_API_KEY), network_checked: false, note: 'Key presence is not quota/billing verification'}, null, 2));
    if (Object.values(checks).some(v => !v)) process.exitCode = 1;
  } else if (command === 'probe') console.log(JSON.stringify(probe(path.resolve(args[0])), null, 2));
  else if (command === 'init') {
    if (!args[0]) throw new Error('Project directory required');
    const dir = path.resolve(args[0]); if (fs.existsSync(dir)) throw new Error('Project directory already exists; will not overwrite');
    if (dir.startsWith(ROOT + path.sep)) throw new Error('Create projects outside the installed Skill');
    fs.mkdirSync(dir, {recursive: true});
    save(path.join(dir, 'project.json'), {version: 1, style: 'B1', width: 1280, height: 720, fps: 30, voice: {path: 'narration.wav', lead: 0, tail: 0}, captions: [], shots: [], sfx: []});
    console.log(JSON.stringify({project: path.join(dir, 'project.json'), stage: 'scaffold; add approved narration, aligned captions and authored scenes before rendering'}));
  } else if (command === 'captions') {
    if (!args[0] || !args[1]) throw new Error('Aligned word input and output file required');
    if (fs.existsSync(args[1])) throw new Error('Caption output exists; will not overwrite');
    save(args[1], groupWords(json(args[0]), Number(option('--lead', 0))));
    console.log(JSON.stringify({output: path.resolve(args[1])}));
  } else if (['validate', 'preview', 'approve', 'render'].includes(command)) {
    const p = loadProject(args[0]);
    if (command === 'validate') { const {painter} = await import('./autopilot-render.mjs'); const draw = await painter(p); for (const cue of p.captions) draw((cue.start + cue.end) / 2); console.log(JSON.stringify({valid: true, fingerprint: p.fingerprint, duration: p.duration, shots: p.shots.length})); return; }
    const out = outputDir(p), approvalPath = path.join(out, 'approval.json'), reportPath = path.join(out, 'preview-report.json');
    if (command === 'approve') {
      const note = option('--note', ''); if (!note.trim()) throw new Error('A note recording genuine user approval is required');
      if (!fs.existsSync(reportPath)) throw new Error('Render and review a preview first');
      const report = json(reportPath);
      if (report.fingerprint !== p.fingerprint || !fs.existsSync(report.output) || hashFile(report.output) !== report.output_sha256) throw new Error('Preview changed; render/review it again');
      save(approvalPath, {fingerprint: p.fingerprint, preview_sha256: report.output_sha256, note, approved_at: new Date().toISOString()});
      console.log(JSON.stringify({approval: approvalPath})); return;
    }
    if (command === 'render') {
      if (!fs.existsSync(approvalPath) || !fs.existsSync(reportPath)) throw new Error('Full production requires user-approved preview');
      const a = json(approvalPath), r = json(reportPath);
      if (a.fingerprint !== p.fingerprint || r.fingerprint !== p.fingerprint || a.preview_sha256 !== r.output_sha256 || !fs.existsSync(r.output) || hashFile(r.output) !== a.preview_sha256) throw new Error('Approval invalidated; preview and user approval required again');
    }
    const seconds = Number(option('--seconds', 20)); if (!Number.isFinite(seconds) || seconds <= 0 || seconds > 60) throw new Error('Preview length must be 0–60 seconds');
    const {render} = await import('./autopilot-render.mjs'); console.log(JSON.stringify(await render(p, {full: command === 'render', seconds, replace: args.includes('--replace')}), null, 2));
  } else throw new Error('Commands: doctor | probe FILE | init DIR | captions WORDS OUTPUT [--lead N] | validate PROJECT | preview PROJECT [--seconds N] [--replace] | approve PROJECT --note TEXT | render PROJECT [--replace]');
}
main().catch(e => { console.error(e.message); process.exitCode = 1; });
