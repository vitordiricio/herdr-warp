import fs from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';

const source = name => fs.readFileSync(new URL(`../customizations/mods/${name}`, import.meta.url), 'utf8');
const moduleURL = text => 'data:text/javascript;base64,' + Buffer.from(text).toString('base64');
const names = source('warp-spaces/session-name.js');
const namesURL = moduleURL(names);
const { sessionName } = await import(namesURL);
const { tabGroups, panelLabel, focusPanel } = await import(moduleURL(
  source('warp-spaces/details.js').replace('"./session-name.js"', JSON.stringify(namesURL))));

test('agent and detail helpers share session name rules', () => {
  assert.equal(names, source('warp-agents/session-name.js'));
  const agent = { address: 't1b', terminal: 't1b', program: { key: 'claude', name: 'Claude Code', agent: true } };
  for (const title of ['', '1', '3', 't1b', 'Claude Code', 'claude', '~/project', '/work/project', 'user@host']) {
    assert.equal(sessionName({ named: false, name: '1' }, { ...agent, title }), '', title);
  }
  assert.equal(sessionName(null, { ...agent, title: 'Refinar layout' }), 'Refinar layout');
  assert.equal(sessionName({ named: true, name: 'Manual' }, agent), 'Manual');
  assert.equal(sessionName({ named: true, name: '123' }, agent), '123');
  assert.equal(sessionName(null, { ...agent, title: '✨ Renomeada' }), 'Renomeada');
});

test('panels retain real tab boundaries, split order and remote ids', () => {
  const space = { tabs: [{ id: 'a' }, { id: 'b' }, { id: 'remote/c' }] };
  const panels = [
    { pane: 'shell', tab: 'a' }, { pane: 'agent', tab: 'a' },
    { pane: 'other', tab: 'b' }, { pane: 'remote/p', tab: 'remote/c' },
    { pane: 'elsewhere', tab: 'unrelated' },
  ];
  assert.deepEqual(tabGroups(space, panels).map(g => g.panes.map(p => p.pane)),
                   [['shell', 'agent'], ['other'], ['remote/p']]);
  assert.deepEqual(tabGroups({ tabs: [] }, panels), []);
});

test('detail labels use session names, program fallback and mod names', () => {
  const shell = { terminal: 't1', title: 'old title', program: { name: 'bash', shell: true } };
  const agent = { terminal: 't2', title: 'Refinar layout', program: { name: 'Codex', agent: true } };
  assert.equal(panelLabel(shell, {}, 2), 'bash');
  assert.equal(panelLabel(agent, {}, 2), 'Refinar layout');
  assert.equal(panelLabel({ ...agent, title: 't2' }, {}, 2), 'Codex');
  assert.equal(panelLabel(agent, { named: true, name: 'Manual' }, 1), 'Manual');
  assert.equal(panelLabel({ terminal: null, title: 'Files' }, {}, 1), 'Files');
});

test('navigation focuses the chosen panel and reveals a zoomed composition', () => {
  const pane = { pane: 'agent', tab: 'a' };
  const calls = [];
  focusPanel(pane, [{ pane: 'shell', tab: 'a', zoomed: true }, pane], (...args) => calls.push(args));
  assert.deepEqual(calls, [['pane.zoom', { pane: 'shell' }], ['pane.focus', { pane: 'agent' }]]);
});
