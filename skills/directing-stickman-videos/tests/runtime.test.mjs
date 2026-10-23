import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {ROOT, FFMPEG, run, save, loadProject, groupWords, hashFile, probe, designPlane} from '../scripts/autopilot-core.mjs';
import {keyState, render, painter} from '../scripts/autopilot-render.mjs';

const cli = path.join(ROOT, 'scripts/autopilot.mjs');
const command = args => spawnSync(process.execPath, [cli, ...args], {encoding: 'utf8', timeout: 120000});
function fixture(t) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'stickman-runtime-test-'));
  // Each test owns this exact temporary directory, never a user project.
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  run(FFMPEG, ['-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=310:duration=0.85', '-y', path.join(dir, 'voice.wav')]);
  const project = {version: 1, style: 'B1', width: 640, height: 360, fps: 12, voice: {path: 'voice.wav'}, captions: [{start: 0.1, end: 0.7, text: 'Offline test.'}], shots: [{start: 0, end: 0.4, layers: [{type: 'text', text: 'A GOOD IDEA', x: 80, y: 110, size: 60, bold: true}, {type: 'image', path: '@b1/idea-bulb-crayon.png', x: 400, y: 280, w: 180, keys: [{t: 0, x: 400}, {t: 0.3, x: 450}]}]}, {start: 0.4, end: 0.85, layers: [{type: 'pose', pose: 1, x: 650, y: 40, w: 400}, {type: 'text', text: 'BECOMES A VIDEO.', x: 60, y: 200, w: 550, size: 54}]}], sfx: [{time: 0.2, kind: 'tap', gain: 0.02}]};
  const file = path.join(dir, 'project.json'); save(file, project);
  return {dir, project, file};
}
test('doctor checks local dependencies without network or revealing keys', () => {
  const r = command(['doctor']); assert.equal(r.status, 0, r.stderr); const data = JSON.parse(r.stdout); assert.equal(data.network_checked, false); assert.ok(data.checks.fonts);
});
test('aligned words are grouped without invented word timings', () => {
  const words = {words: [{start: 0.2, end: 0.5, word: 'Hello'}, {start: 0.6, end: 1, word: 'world.'}, {start: 1.7, end: 2, word: 'Next.'}]};
  assert.deepEqual(groupWords(words, 0.1), [{start: 0.30000000000000004, end: 1.1, text: 'Hello world.'}, {start: 1.8, end: 2.1, text: 'Next.'}]);
  assert.throws(() => groupWords({words: [{start: 1, end: 0.5, word: 'bad'}]}));
});
test('keyframes interpolate locally and hold before/after endpoints', () => {
  const l = {keys: [{t: 0, x: 10}, {t: 1, x: 30}]}; assert.equal(keyState(l, 0.5).x, 20); assert.equal(keyState(l, 2).x, 30);
});
test('portrait uses a taller design plane without stretching local shapes', async t => {
  const f = fixture(t); f.project.width = 360; f.project.height = 640; f.project.grid = false;
  f.project.shots[0].layers = [{type: 'line', points: [[0, 0], [200, 0], [200, 200], [0, 200], [0, 0]], x: 100, y: 200, lineWidth: 4}];
  save(f.file, f.project); const p = loadProject(f.file), plane = designPlane(p);
  assert.equal(plane.width, 1280); assert.ok(plane.height > 2200);
  const draw = await painter(p), pixels = draw(0.02).getContext('2d').getImageData(0, 0, 360, 640).data;
  let x0 = 360, y0 = 640, x1 = 0, y1 = 0;
  for (let y = 0; y < 180; y++) for (let x = 0; x < 160; x++) if (pixels[(y * 360 + x) * 4] < 100) { x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  assert.ok(x1 > x0); assert.ok(Math.abs((x1 - x0) - (y1 - y0)) <= 1, 'A square must stay square in portrait');
});
test('validation rejects speech stretching, external paths and timeline gaps', t => {
  const f = fixture(t); assert.ok(loadProject(f.file).voiceDuration > 0.8);
  f.project.voice.speed = 0.7; save(f.file, f.project); assert.throws(() => loadProject(f.file), /speech speed/); delete f.project.voice.speed;
  f.project.voice.path = 'https://example.com/voice.wav'; save(f.file, f.project); assert.throws(() => loadProject(f.file), /local path/); f.project.voice.path = 'voice.wav';
  f.project.shots[1].start = 0.45; save(f.file, f.project); assert.throws(() => loadProject(f.file), /gap\/overlap/);
});
test('render is resumable, produces captioned A/V and requires exact preview approval', async t => {
  const f = fixture(t), source = hashFile(path.join(f.dir, 'voice.wav'));
  let r = command(['render', f.file]); assert.notEqual(r.status, 0); assert.match(r.stderr, /user-approved/);
  const p = loadProject(f.file), first = await render(p), second = await render(p, {replace: true});
  assert.equal(second.cache_hits, 2); assert.equal(first.frames, Math.ceil(0.85 * 12)); assert.equal(hashFile(path.join(f.dir, 'voice.wav')), source);
  const info = probe(first.output); assert.ok(info.streams.some(s => s.codec_type === 'audio')); assert.ok(info.streams.some(s => s.codec_type === 'video')); assert.equal(Number(info.streams.find(s => s.codec_type === 'video').nb_frames), first.frames);
  assert.ok(fs.existsSync(path.join(f.dir, 'output/preview.srt'))); assert.ok(fs.existsSync(path.join(f.dir, 'output/preview-contact-sheet.png')));
  r = command(['approve', f.file, '--note', 'Synthetic engineering fixture approval only; not a real user video']); assert.equal(r.status, 0, r.stderr);
  r = command(['render', f.file]); assert.equal(r.status, 0, r.stderr);
  f.project.shots[0].layers[0].text = 'CHANGED'; save(f.file, f.project);
  r = command(['render', f.file]); assert.notEqual(r.status, 0); assert.match(r.stderr, /invalidated/);
});
test('caption overflow fails rather than silently clipping', async t => {
  const f = fixture(t); f.project.captions[0].text = 'A very long caption phrase. '.repeat(8); save(f.file, f.project);
  const r = command(['validate', f.file]); assert.notEqual(r.status, 0); assert.match(r.stderr, /two lines/);
});
test('output symlink cannot redirect writes to another directory', async t => {
  const f = fixture(t); fs.symlinkSync(os.tmpdir(), path.join(f.dir, 'output'), 'dir'); await assert.rejects(render(loadProject(f.file)), /real project-local/);
});
test('nested cache symlink cannot redirect renderer-owned writes', async t => {
  const f = fixture(t), external = path.join(f.dir, 'keep');
  fs.mkdirSync(external); fs.mkdirSync(path.join(f.dir, 'output'));
  fs.writeFileSync(path.join(external, 'sentinel'), 'unchanged');
  fs.symlinkSync(external, path.join(f.dir, 'output/cache'), 'dir');
  await assert.rejects(render(loadProject(f.file)), /must not contain symlinks/);
  assert.equal(fs.readFileSync(path.join(external, 'sentinel'), 'utf8'), 'unchanged');
  assert.deepEqual(fs.readdirSync(external), ['sentinel']);
});
test('media adapter cannot generate without network opt-in', () => {
  const r = spawnSync(process.execPath, [path.join(ROOT, 'scripts/gemini-media.mjs'), 'speech'], {encoding: 'utf8'}); assert.notEqual(r.status, 0); assert.match(r.stderr, /Network disabled/);
});
