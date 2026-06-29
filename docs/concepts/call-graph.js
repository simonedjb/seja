// SEJA harness call graph -- interactive viewer.
// Generated 2026-06-18T11:41:13Z by .claude/skills/scripts/priv/generate_call_graph.py.
// Do not edit by hand.
//
// Step 4 wires the sidebar controls scaffolded in Step 3: per-type filter
// checkboxes (with select-all / deselect-all and a "missing designer copy"
// filter), edge-label toggle, layout switcher (cose/dagre/concentric),
// manual drag + position persistence, reset-layout, save-layout JSON
// download, SVG export (via cytoscape-svg) and PNG export (via cy.png).
// State persists across reloads via localStorage. No global pollution
// beyond window.__cy (already exposed in Step 3).

(async function () {
  if (window.cytoscapeFcose) cytoscape.use(window.cytoscapeFcose);
  if (window.cytoscapeCola) cytoscape.use(window.cytoscapeCola);
  if (window.cytoscapeSvg) cytoscape.use(window.cytoscapeSvg);

  // -----------------------------------------------------------------
  // localStorage key helpers
  // -----------------------------------------------------------------
  const LS_FILTER_PREFIX = 'callGraph:filter:';
  const LS_LAYOUT = 'callGraph:layout';
  const LS_POS_PREFIX = 'callGraph:pos:';
  const LS_HIDE_DISCONNECTED = 'callGraph:filter-hide-disconnected';
  const LS_HIDE_INTERNAL_SKILLS = 'callGraph:filter-hide-internal-skills';
  const LS_EDGE_FILTER_PREFIX = 'callGraph:edge-filter:';
  // New key (callGraph:filter-conditional-show) replaces the legacy
  // callGraph:filter-conditional-only key from the inverted-semantics filter.
  // Default semantic: checked = show conditional edges (matches every other
  // edge-type checkbox in the filter group). Fresh key bypasses any stuck
  // 'true' from the legacy filter that would have hidden conditional edges.
  const LS_CONDITIONAL_SHOW = 'callGraph:filter-conditional-show';

  function lsGet(key, fallback) {
    try {
      const v = window.localStorage.getItem(key);
      return v === null ? fallback : v;
    } catch (_e) {
      return fallback;
    }
  }

  function lsSet(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch (_e) {
      /* quota or disabled storage -- ignore */
    }
  }

  function lsRemove(key) {
    try {
      window.localStorage.removeItem(key);
    } catch (_e) {
      /* ignore */
    }
  }

  function lsListKeys(prefix) {
    const keys = [];
    try {
      for (let i = 0; i < window.localStorage.length; i++) {
        const k = window.localStorage.key(i);
        if (k && k.indexOf(prefix) === 0) keys.push(k);
      }
    } catch (_e) {
      /* ignore */
    }
    return keys;
  }

  // -----------------------------------------------------------------
  // Load graph data
  // -----------------------------------------------------------------
  const data = window.__CALL_GRAPH_DATA__;
  if (!data) {
    document.getElementById('cy').textContent =
      'Call graph data unavailable.';
    return;
  }

  const elements = [
    ...data.nodes.map(function (n) {
      return {
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          path: n.path,
          user_invocable: n.user_invocable,
          description_source: n.description_source || 'developer-fallback'
        }
      };
    }),
    ...data.edges.map(function (e) {
      // Populate `when` (flag label) and `conditional` only on edges that are
      // actually conditional -- when omitted entirely, the `[conditional]`
      // attribute-defined selector in the style array cleanly discriminates.
      // Earlier versions set `conditional: false` on every edge and relied on
      // the `[?conditional]` truthy selector, which proved unreliable in
      // Cytoscape 3.30.4 for boolean-typed data. Attribute-presence is a
      // stronger contract.
      const when = e.when || '';
      const isConditional = !!(e.conditional || when);
      const data = {
        id: e.source + '|' + e.type + '|' + e.target,
        source: e.source,
        target: e.target,
        type: e.type,
        label: e.label || ''
      };
      if (isConditional) {
        data.when = when;
        data.conditional = true;
      }
      if (e.primary) { data.primary = true; }
      return { data: data };
    })
  ];

  const typeColors = {
    'skill':          { bg: '#b8d5f2', border: '#6da3d4', color: '#1e3a5f' },
    // Internal (Dispatch B) worker skills -- lighter tint, dashed border.
    'skill-internal': { bg: '#e8f0f9', border: '#6da3d4', color: '#1e3a5f' },
    'agent':          { bg: '#e6d5ed', border: '#a082b5', color: '#3e2852' },
    'script':         { bg: '#d5e3ef', border: '#7c9ab3', color: '#2a3e52' },
    'rule':           { bg: '#f8e6a8', border: '#c9aa4d', color: '#5c4617' },
    'ref-general':    { bg: '#cfe3cf', border: '#7fa87f', color: '#2d4a2d' },
    'ref-template':   { bg: '#d7cce8', border: '#9687b5', color: '#3e3566' },
    'ref-project':    { bg: '#efcccc', border: '#b58282', color: '#663535' }
  };

  const nodeStyle = Object.entries(typeColors).map(function (entry) {
    const type = entry[0];
    const c = entry[1];
    const style = {
      'background-color': c.bg,
      'border-color': c.border,
      'border-width': 1.5,
      'color': c.color,
      'label': 'data(label)',
      'font-size': 10,
      'text-valign': 'center',
      'text-halign': 'center',
      'width': 'label',
      'height': 'label',
      'padding': 8,
      'shape': 'round-rectangle'
    };
    // Dashed border on internal-worker skill nodes so they stand apart
    // from user-facing skills at a glance (Cytoscape borders default to solid).
    if (type === 'skill-internal') {
      style['border-style'] = 'dashed';
    }
    return {
      selector: 'node[type = "' + type + '"]',
      style: style
    };
  });

  // -----------------------------------------------------------------
  // Layout options
  // -----------------------------------------------------------------
  const layoutOptions = {
    'fcose': {
      // Successor to cose-bilkent, same author (Bilkent). Better quality
      // and faster than cose-bilkent at 200+ nodes; handles hub-and-spoke
      // topologies more cleanly. Falls back to built-in cose if the
      // extension did not register.
      name: (window.cytoscapeFcose ? 'fcose' : 'cose'),
      animate: 'end',
      animationDuration: 400,
      fit: true,
      padding: 40,
      quality: 'default',
      nodeRepulsion: 4500,
      idealEdgeLength: 100,
      edgeElasticity: 0.45,
      nestingFactor: 0.1,
      gravity: 0.25,
      numIter: 2500,
      randomize: false
    },
    'cola': {
      // Constraint-based force layout (WebCola). With `flow: {axis: 'y'}`
      // it produces a soft downward hierarchy -- the top-to-bottom
      // readability that dagre promised but without dagre's cluttered
      // rendering on dense graphs. Falls back to built-in cose if the
      // extension did not register.
      name: (window.cytoscapeCola ? 'cola' : 'cose'),
      animate: true,
      animationDuration: 400,
      fit: true,
      padding: 40,
      maxSimulationTime: 3000,
      nodeSpacing: 20,
      edgeLength: 100,
      flow: { axis: 'y', minSeparation: 40 },
      avoidOverlap: true
    },
    'concentric': {
      name: 'concentric',
      animate: 'end',
      animationDuration: 400,
      fit: true,
      padding: 40,
      concentric: function (node) {
        // Outer rings = lower priority; skills are innermost.
        const typeOrder = {
          'skill': 5,
          'skill-internal': 5,
          'agent': 4,
          'script': 3,
          'rule': 2,
          'ref-general': 1,
          'ref-template': 1,
          'ref-project': 1
        };
        return typeOrder[node.data('type')] || 0;
      },
      levelWidth: function () { return 1; },
      minNodeSpacing: 12,
      spacingFactor: 0.6,
      avoidOverlap: true
    }
  };

  // Restore last layout choice (default 'fcose'). Legacy `cose` / `dagre`
  // values from pre-swap localStorage fall back to 'fcose'.
  const initialLayout = lsGet(LS_LAYOUT, 'fcose');
  const validLayout = layoutOptions[initialLayout] ? initialLayout : 'fcose';

  const cy = cytoscape({
    container: document.getElementById('cy'),
    boxSelectionEnabled: true,
    elements: elements,
    style: [
      ...nodeStyle,
      {
        selector: 'edge',
        style: {
          'width': 1,
          'line-color': '#b0b0b0',
          'target-arrow-color': '#b0b0b0',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'arrow-scale': 0.8,
          'font-size': 8,
          'color': '#555',
          'text-background-color': '#ffffff',
          'text-background-opacity': 0.8,
          'text-background-padding': 2
        }
      },
      {
        // Secondary suggests edges (post-completion hints, non-first per source)
        // render dotted so they read as background context behind the primary hint.
        selector: 'edge[type = "suggests"]',
        style: {
          'line-style': 'dotted',
          'line-color': '#9a9a9a',
          'target-arrow-color': '#9a9a9a',
          'opacity': 0.65
        }
      },
      {
        // Primary suggests edge (first in reading order from skill-graph.json
        // for each source skill) renders dashed — more prominent than secondary.
        selector: 'edge[type = "suggests"][?primary]',
        style: {
          'line-style': 'dashed',
          'opacity': 0.80
        }
      },
      {
        // Dispatches-inline edges (wrapper -> internal worker -- Dispatch B
        // per the mode factoring pattern) are dashed and tinted with the
        // skill-family border color so the wrapper->internal relationship
        // reads as a skill relationship rather than a suggestion. Distinct
        // from the generic `suggests` gray and the `dynamic-load` purple.
        selector: 'edge[type = "dispatches-inline"]',
        style: {
          'line-style': 'dashed',
          'line-color': '#6da3d4',
          'target-arrow-color': '#6da3d4',
          'opacity': 0.85
        }
      },
      {
        // Dynamic-load edges (refs loaded by skill/agent at runtime based
        // on an argument, e.g. role, audience, perspective) are dotted and
        // tinted soft purple so they are distinct from dashed suggests.
        selector: 'edge[type = "dynamic-load"]',
        style: {
          'line-style': 'dotted',
          'line-color': '#8a7fb5',
          'target-arrow-color': '#8a7fb5',
          'opacity': 0.8
        }
      },
      {
        // Reads edges (explicit _references/ path mentioned in prose or code)
        // are solid and tinted teal-green so they are clearly distinct from
        // the skill-orchestration navy/gray, the ref-load purple, and
        // the conditional amber.
        selector: 'edge[type = "reads"]',
        style: {
          'line-style': 'solid',
          'line-color': '#5aaa82',
          'target-arrow-color': '#5aaa82',
          'opacity': 0.7
        }
      },
      {
        // Conditional edges (fire only under a named flag) are dashed with a
        // tighter dash pattern, a bolder width, an amber stroke, and an
        // always-visible flag pill. The amber/orange palette is unique among
        // edge classes (suggests = pale gray, dynamic-load = soft purple, all
        // others = neutral gray) so the reader can spot the 1-2 conditional
        // edges among 300+ without hunting. Uses `[conditional]` attribute-
        // defined selector rather than `[?conditional]` truthy selector
        // because the data mapping only sets the attribute on actually-
        // conditional edges -- attribute-presence is a stronger contract than
        // truthiness on boolean-typed data in Cytoscape 3.30.4.
        selector: 'edge[conditional]',
        style: {
          'line-style': 'dashed',
          'line-dash-pattern': [6, 2],
          'line-color': '#d97706',
          'target-arrow-color': '#d97706',
          'width': 2.5,
          'label': 'data(when)',
          'font-size': 11,
          'font-weight': 'bold',
          'color': '#7c2d12',
          'text-background-color': '#fef3c7',
          'text-background-opacity': 1,
          'text-background-padding': 3,
          'text-background-shape': 'roundrectangle',
          'text-border-color': '#d97706',
          'text-border-width': 1,
          'text-border-opacity': 1
        }
      },
      {
        // Focus mode: nodes/edges outside the clicked node's 1-hop
        // neighborhood are faded. Opacity is set to keep non-neighbors
        // clearly secondary but still legible (text-opacity higher than
        // node-opacity so labels read against the fainter shapes).
        selector: '.faded',
        style: {
          'opacity': 0.40,
          'text-opacity': 0.55
        }
      },
      {
        // Search matches are ring-highlighted so they remain readable
        // while still standing out from non-matches.
        selector: 'node.search-match',
        style: {
          'border-width': 3,
          'border-color': '#2a9d8f',
          'overlay-color': '#2a9d8f',
          'overlay-opacity': 0.1,
          'overlay-padding': 4
        }
      },
      {
        // Hover sync between sidebar list rows and canvas nodes.
        selector: 'node.search-hovered',
        style: {
          'border-width': 4,
          'border-color': '#e76f51',
          'overlay-color': '#e76f51',
          'overlay-opacity': 0.14,
          'overlay-padding': 6
        }
      },
      {
        // Selected nodes get a thicker, distinctly-coloured border so the
        // selection is unambiguous regardless of node type or background.
        selector: 'node:selected',
        style: {
          'border-width': 3.5,
          'border-color': '#1e6fb5',
          'overlay-color': '#1e6fb5',
          'overlay-opacity': 0.12,
          'overlay-padding': 4
        }
      }
    ],
    wheelSensitivity: 0.25
  });

  window.__cy = cy;

  const searchInput = document.getElementById('node-search-input');
  const searchClearBtn = document.getElementById('node-search-clear');
  const matchPanel = document.getElementById('match-panel');
  const matchPanelEmpty = document.getElementById('match-panel-empty');
  const matchList = document.getElementById('match-list');
  const matchCount = document.getElementById('match-count');

  let searchTerm = '';
  let matchedNodeIds = new Set();
  let hoveredMatchNodeId = null;
  const matchListItemByNodeId = {};

  function setMatchPanelOpen(isOpen) {
    if (!matchPanel) return;
    matchPanel.hidden = !isOpen;
    matchPanel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
  }

  // Track the currently active layout name (logical key, not the
  // cytoscape-extension name). Needed for position persistence keys.
  let currentLayout = validLayout;

  // -----------------------------------------------------------------
  // Position persistence
  // -----------------------------------------------------------------
  function posKey(layoutName, nodeId) {
    return LS_POS_PREFIX + layoutName + ':' + nodeId;
  }

  function applySavedPositions(layoutName) {
    cy.nodes().forEach(function (node) {
      const raw = lsGet(posKey(layoutName, node.id()), null);
      if (!raw) return;
      try {
        const pos = JSON.parse(raw);
        if (typeof pos.x === 'number' && typeof pos.y === 'number') {
          node.position({ x: pos.x, y: pos.y });
        }
      } catch (_e) {
        /* bad JSON -- ignore */
      }
    });
  }

  function clearSavedPositions(layoutName) {
    const prefix = LS_POS_PREFIX + layoutName + ':';
    lsListKeys(prefix).forEach(function (k) { lsRemove(k); });
  }

  function runLayout(layoutName) {
    const opts = layoutOptions[layoutName];
    if (!opts) return;
    currentLayout = layoutName;
    const layout = cy.layout(opts);
    layout.one('layoutstop', function () {
      applySavedPositions(layoutName);
      cy.fit(undefined, 40);
    });
    layout.run();
  }

  // Persist node positions on drag end.
  cy.on('dragfreeon', 'node', function (evt) {
    const node = evt.target;
    const pos = node.position();
    lsSet(
      posKey(currentLayout, node.id()),
      JSON.stringify({ x: pos.x, y: pos.y })
    );
  });

  function setHoveredMatchNode(nodeId) {
    if (hoveredMatchNodeId === nodeId) return;

    if (hoveredMatchNodeId) {
      const prevEl = cy.getElementById(hoveredMatchNodeId);
      if (prevEl && !prevEl.empty()) prevEl.removeClass('search-hovered');
      const prevRow = matchListItemByNodeId[hoveredMatchNodeId];
      if (prevRow) prevRow.classList.remove('match-hovered');
    }

    hoveredMatchNodeId = null;

    if (!nodeId || !matchedNodeIds.has(nodeId)) return;

    const nodeEl = cy.getElementById(nodeId);
    if (nodeEl && !nodeEl.empty()) nodeEl.addClass('search-hovered');
    const row = matchListItemByNodeId[nodeId];
    if (row) row.classList.add('match-hovered');
    hoveredMatchNodeId = nodeId;
  }

  function updateMatchSelection() {
    Object.keys(matchListItemByNodeId).forEach(function (nodeId) {
      const row = matchListItemByNodeId[nodeId];
      if (!row) return;
      row.classList.toggle('match-selected', nodeId === currentPanelNodeId);
    });
  }

  function applyNodeSearch() {
    const query = String(searchTerm || '').trim().toLowerCase();

    matchedNodeIds = new Set();
    cy.nodes().removeClass('search-match search-hovered');

    Object.keys(matchListItemByNodeId).forEach(function (k) {
      delete matchListItemByNodeId[k];
    });
    matchList.innerHTML = '';

    if (!query) {
      setMatchPanelOpen(false);
      matchCount.textContent = '0';
      matchPanelEmpty.textContent = 'Type in "Search nodes" to highlight matching labels.';
      matchPanelEmpty.hidden = false;
      setHoveredMatchNode(null);
      return;
    }

    setMatchPanelOpen(true);

    const matchedNodes = [];
    sortedNodes.forEach(function (node) {
      const nodeEl = cy.getElementById(node.id);
      if (!nodeEl || nodeEl.empty()) return;
      if (nodeEl.style('display') === 'none') return;
      const hay = ((node.label || '') + ' ' + node.id).toLowerCase();
      if (hay.indexOf(query) === -1) return;
      matchedNodes.push(node);
      matchedNodeIds.add(node.id);
      nodeEl.addClass('search-match');
    });

    matchCount.textContent = String(matchedNodes.length);
    if (!matchedNodes.length) {
      matchPanelEmpty.textContent = 'No visible nodes match "' + query + '".';
      matchPanelEmpty.hidden = false;
      setHoveredMatchNode(null);
      return;
    }

    matchPanelEmpty.hidden = true;

    matchedNodes.forEach(function (node) {
      const item = document.createElement('li');
      item.className = 'match-item';
      item.setAttribute('role', 'button');
      item.setAttribute('tabindex', '0');
      item.dataset.nodeId = node.id;

      const swatch = document.createElement('span');
      swatch.className = 'match-node-swatch swatch swatch-' + node.type;

      const label = document.createElement('span');
      label.className = 'match-node-label';
      label.textContent = node.label || node.id;

      const type = document.createElement('span');
      type.className = 'match-node-type';
      type.textContent = (TYPE_LABELS[node.type] || node.type);

      item.appendChild(swatch);
      item.appendChild(label);
      item.appendChild(type);

      item.addEventListener('mouseenter', function () {
        setHoveredMatchNode(node.id);
      });
      item.addEventListener('mouseleave', function () {
        setHoveredMatchNode(null);
      });
      item.addEventListener('click', function () {
        openPanel(node.id);
        focusNeighborhood(node.id);
      });
      item.addEventListener('keydown', function (evt) {
        if (evt.key === 'Enter' || evt.key === ' ') {
          evt.preventDefault();
          openPanel(node.id);
          focusNeighborhood(node.id);
        }
      });

      matchList.appendChild(item);
      matchListItemByNodeId[node.id] = item;
    });

    updateMatchSelection();
    setHoveredMatchNode(null);
  }

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      searchTerm = searchInput.value || '';
      applyNodeSearch();
    });
  }

  if (searchClearBtn) {
    searchClearBtn.addEventListener('click', function () {
      searchTerm = '';
      if (searchInput) searchInput.value = '';
      applyNodeSearch();
      if (searchInput) searchInput.focus();
    });
  }

  cy.on('mouseover', 'node', function (evt) {
    const nodeId = evt.target.id();
    if (matchedNodeIds.has(nodeId)) {
      setHoveredMatchNode(nodeId);
    }
  });

  cy.on('mouseout', 'node', function (evt) {
    const nodeId = evt.target.id();
    if (hoveredMatchNodeId === nodeId) {
      setHoveredMatchNode(null);
    }
  });

  // -----------------------------------------------------------------
  // Filter checkboxes per node type
  // -----------------------------------------------------------------
  const filterCheckboxes = Array.from(
    document.querySelectorAll('input.filter-type')
  );

  function isPrimaryEdgeTypeCheckbox(cb) {
    // Keep conditional visibility independent from edge-type bulk toggles.
    return cb && cb.id !== 'filter-conditional-show';
  }

  function updateNodeVisibility() {
    const enabledTypes = new Set(
      filterCheckboxes
        .filter(function (cb) { return cb.checked; })
        .map(function (cb) { return cb.value; })
    );
    const enabledEdgeTypes = new Set(
      Array.prototype.slice.call(
        document.querySelectorAll('input.filter-edge-type')
      ).filter(function (cb) {
        return isPrimaryEdgeTypeCheckbox(cb) && cb.checked;
      })
       .map(function (cb) { return cb.value; })
    );
    const hideDisconnected = document.getElementById('filter-hide-disconnected');
    const hideDisconnectedActive = hideDisconnected && hideDisconnected.checked;
    const hideInternalSkills = document.getElementById('filter-hide-internal-skills');
    const hideInternalSkillsActive = hideInternalSkills && hideInternalSkills.checked;
    // Positive-semantics conditional filter: checkbox lives in the "Other"
    // subgroup of "Filter by edge type" and reads "show conditional edges".
    // Default checked. Hide condition: !shown && edge has `conditional`.
    const conditionalShow = document.getElementById('filter-conditional-show');
    const conditionalEdgesShown = !conditionalShow || conditionalShow.checked;

    cy.batch(function () {
      const visibleByType = new Map();
      cy.nodes().forEach(function (node) {
        const type = node.data('type');
        let visible = enabledTypes.has(type);
        if (
          visible &&
          hideInternalSkillsActive &&
          type === 'skill' &&
          node.data('user_invocable') === false
        ) {
          visible = false;
        }
        visibleByType.set(node.id(), visible);
      });

      if (hideDisconnectedActive) {
        // A node is "disconnected" relative to the current filter set when
        // none of its incident edges (of an enabled edge type) have both
        // endpoints in the provisionally-visible set. Hide those.
        const degree = new Map();
        cy.edges().forEach(function (edge) {
          const effectiveType = edge.data('type') === 'suggests'
            ? (edge.data('primary') ? 'suggests-primary' : 'suggests-secondary')
            : edge.data('type');
          if (!enabledEdgeTypes.has(effectiveType)) return;
          if (!conditionalEdgesShown && edge.data('conditional')) return;
          const s = edge.source().id();
          const t = edge.target().id();
          if (visibleByType.get(s) && visibleByType.get(t)) {
            degree.set(s, (degree.get(s) || 0) + 1);
            degree.set(t, (degree.get(t) || 0) + 1);
          }
        });
        cy.nodes().forEach(function (node) {
          if (visibleByType.get(node.id()) && !degree.get(node.id())) {
            visibleByType.set(node.id(), false);
          }
        });
      }

      cy.nodes().forEach(function (node) {
        node.style(
          'display',
          visibleByType.get(node.id()) ? 'element' : 'none'
        );
      });

      cy.edges().forEach(function (edge) {
        const srcHidden = edge.source().style('display') === 'none';
        const tgtHidden = edge.target().style('display') === 'none';
        const effectiveType = edge.data('type') === 'suggests'
          ? (edge.data('primary') ? 'suggests-primary' : 'suggests-secondary')
          : edge.data('type');
        const typeDisabled = !enabledEdgeTypes.has(effectiveType);
        const conditionalHidden = !conditionalEdgesShown && edge.data('conditional');
        edge.style(
          'display',
          (srcHidden || tgtHidden || typeDisabled || conditionalHidden) ? 'none' : 'element'
        );
      });
    });

    applyNodeSearch();
  }

  function fitToVisible() {
    const visible = cy.elements().filter(function (el) {
      return el.style('display') !== 'none';
    });
    if (visible.length === 0) return;
    cy.animate(
      { fit: { eles: visible, padding: 40 } },
      { duration: 300, easing: 'ease-in-out-quad' }
    );
  }

  function restoreFilterState() {
    filterCheckboxes.forEach(function (cb) {
      const stored = lsGet(LS_FILTER_PREFIX + cb.value, null);
      if (stored !== null) {
        cb.checked = stored === 'true';
      }
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
    });
    const hideDisc = document.getElementById('filter-hide-disconnected');
    if (hideDisc) {
      const stored = lsGet(LS_HIDE_DISCONNECTED, 'false');
      hideDisc.checked = stored === 'true';
      hideDisc.setAttribute('aria-checked', hideDisc.checked ? 'true' : 'false');
    }
    const hideInternal = document.getElementById('filter-hide-internal-skills');
    if (hideInternal) {
      const stored = lsGet(LS_HIDE_INTERNAL_SKILLS, 'false');
      hideInternal.checked = stored === 'true';
      hideInternal.setAttribute(
        'aria-checked',
        hideInternal.checked ? 'true' : 'false'
      );
    }
    const condShow = document.getElementById('filter-conditional-show');
    if (condShow) {
      // Default 'true' (checked, conditional edges visible) when the key is
      // absent. The legacy LS_CONDITIONAL_ONLY key is intentionally NOT read
      // so a stuck 'true' from the inverted-semantics filter cannot bleed
      // through and silently hide conditional edges on first load.
      const stored = lsGet(LS_CONDITIONAL_SHOW, 'true');
      condShow.checked = stored === 'true';
      condShow.setAttribute('aria-checked', condShow.checked ? 'true' : 'false');
    }
    Array.prototype.slice.call(
      document.querySelectorAll('input.filter-edge-type')
    ).forEach(function (cb) {
      if (!isPrimaryEdgeTypeCheckbox(cb)) return;
      const stored = lsGet(LS_EDGE_FILTER_PREFIX + cb.value, null);
      if (stored !== null) {
        cb.checked = stored === 'true';
      }
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
    });
  }

  filterCheckboxes.forEach(function (cb) {
    cb.addEventListener('change', function () {
      lsSet(LS_FILTER_PREFIX + cb.value, cb.checked ? 'true' : 'false');
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
      updateNodeVisibility();
    });
  });

  const filterAllBtn = document.getElementById('filter-all');
  if (filterAllBtn) {
    filterAllBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        cb.checked = true;
        cb.setAttribute('aria-checked', 'true');
        lsSet(LS_FILTER_PREFIX + cb.value, 'true');
      });
      updateNodeVisibility();
    });
  }

  const filterNoneBtn = document.getElementById('filter-none');
  if (filterNoneBtn) {
    filterNoneBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        cb.checked = false;
        cb.setAttribute('aria-checked', 'false');
        lsSet(LS_FILTER_PREFIX + cb.value, 'false');
      });
      updateNodeVisibility();
    });
  }

  const hideDisconnectedCheckbox = document.getElementById('filter-hide-disconnected');
  if (hideDisconnectedCheckbox) {
    hideDisconnectedCheckbox.addEventListener('change', function () {
      lsSet(LS_HIDE_DISCONNECTED, hideDisconnectedCheckbox.checked ? 'true' : 'false');
      hideDisconnectedCheckbox.setAttribute(
        'aria-checked',
        hideDisconnectedCheckbox.checked ? 'true' : 'false'
      );
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const hideInternalSkillsCheckbox = document.getElementById('filter-hide-internal-skills');
  if (hideInternalSkillsCheckbox) {
    hideInternalSkillsCheckbox.addEventListener('change', function () {
      lsSet(
        LS_HIDE_INTERNAL_SKILLS,
        hideInternalSkillsCheckbox.checked ? 'true' : 'false'
      );
      hideInternalSkillsCheckbox.setAttribute(
        'aria-checked',
        hideInternalSkillsCheckbox.checked ? 'true' : 'false'
      );
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const userFacingPresetBtn = document.getElementById('filter-preset-user-facing');
  if (userFacingPresetBtn) {
    userFacingPresetBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        const checked = cb.value === 'skill';
        cb.checked = checked;
        cb.setAttribute('aria-checked', checked ? 'true' : 'false');
        lsSet(LS_FILTER_PREFIX + cb.value, checked ? 'true' : 'false');
      });
      if (hideInternalSkillsCheckbox) {
        hideInternalSkillsCheckbox.checked = true;
        hideInternalSkillsCheckbox.setAttribute('aria-checked', 'true');
        lsSet(LS_HIDE_INTERNAL_SKILLS, 'true');
      }
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const fullPresetBtn = document.getElementById('filter-preset-full');
  if (fullPresetBtn) {
    fullPresetBtn.addEventListener('click', function () {
      filterCheckboxes.forEach(function (cb) {
        cb.checked = true;
        cb.setAttribute('aria-checked', 'true');
        lsSet(LS_FILTER_PREFIX + cb.value, 'true');
      });
      if (hideInternalSkillsCheckbox) {
        hideInternalSkillsCheckbox.checked = false;
        hideInternalSkillsCheckbox.setAttribute('aria-checked', 'false');
        lsSet(LS_HIDE_INTERNAL_SKILLS, 'false');
      }
      updateNodeVisibility();
      fitToVisible();
    });
  }

  const conditionalShowCheckbox = document.getElementById('filter-conditional-show');
  if (conditionalShowCheckbox) {
    conditionalShowCheckbox.addEventListener('change', function () {
      lsSet(LS_CONDITIONAL_SHOW, conditionalShowCheckbox.checked ? 'true' : 'false');
      conditionalShowCheckbox.setAttribute(
        'aria-checked',
        conditionalShowCheckbox.checked ? 'true' : 'false'
      );
      updateNodeVisibility();
    });
  }

  // Edge-type filter checkboxes + select-all / deselect-all buttons.
  const edgeTypeCheckboxes = Array.prototype.slice.call(
    document.querySelectorAll('input.filter-edge-type')
  ).filter(function (cb) {
    return isPrimaryEdgeTypeCheckbox(cb);
  });
  edgeTypeCheckboxes.forEach(function (cb) {
    cb.addEventListener('change', function () {
      lsSet(LS_EDGE_FILTER_PREFIX + cb.value, cb.checked ? 'true' : 'false');
      cb.setAttribute('aria-checked', cb.checked ? 'true' : 'false');
      updateNodeVisibility();
    });
  });

  const edgeFilterAllBtn = document.getElementById('edge-filter-all');
  if (edgeFilterAllBtn) {
    edgeFilterAllBtn.addEventListener('click', function () {
      edgeTypeCheckboxes.forEach(function (cb) {
        cb.checked = true;
        cb.setAttribute('aria-checked', 'true');
        lsSet(LS_EDGE_FILTER_PREFIX + cb.value, 'true');
      });
      if (conditionalShowCheckbox) {
        conditionalShowCheckbox.checked = true;
        conditionalShowCheckbox.setAttribute('aria-checked', 'true');
        lsSet(LS_CONDITIONAL_SHOW, 'true');
      }
      updateNodeVisibility();
    });
  }
  const edgeFilterNoneBtn = document.getElementById('edge-filter-none');
  if (edgeFilterNoneBtn) {
    edgeFilterNoneBtn.addEventListener('click', function () {
      edgeTypeCheckboxes.forEach(function (cb) {
        cb.checked = false;
        cb.setAttribute('aria-checked', 'false');
        lsSet(LS_EDGE_FILTER_PREFIX + cb.value, 'false');
      });
      if (conditionalShowCheckbox) {
        conditionalShowCheckbox.checked = false;
        conditionalShowCheckbox.setAttribute('aria-checked', 'false');
        lsSet(LS_CONDITIONAL_SHOW, 'false');
      }
      updateNodeVisibility();
    });
  }

  // -----------------------------------------------------------------
  // Layout switcher
  // -----------------------------------------------------------------
  const layoutRadios = Array.from(
    document.querySelectorAll('input[name="layout"]')
  );

  function syncLayoutRadioAria() {
    layoutRadios.forEach(function (radio) {
      radio.setAttribute('aria-checked', radio.checked ? 'true' : 'false');
    });
  }

  // Restore last layout selection in the radios.
  layoutRadios.forEach(function (radio) {
    radio.checked = (radio.value === currentLayout);
  });
  syncLayoutRadioAria();

  layoutRadios.forEach(function (radio) {
    radio.addEventListener('change', function () {
      if (!radio.checked) return;
      lsSet(LS_LAYOUT, radio.value);
      syncLayoutRadioAria();
      runLayout(radio.value);
    });
  });

  const layoutFitBtn = document.getElementById('layout-fit');
  if (layoutFitBtn) {
    layoutFitBtn.addEventListener('click', function () {
      fitToVisible();
    });
  }

  // Reset-layout: clear saved positions for current layout, re-run.
  const layoutResetBtn = document.getElementById('layout-reset');
  if (layoutResetBtn) {
    layoutResetBtn.addEventListener('click', function () {
      clearSavedPositions(currentLayout);
      runLayout(currentLayout);
    });
  }

  // -----------------------------------------------------------------
  // Save layout (download JSON)
  // -----------------------------------------------------------------
  function formatDateForFilename(d) {
    const yyyy = d.getUTCFullYear();
    const mm = String(d.getUTCMonth() + 1).padStart(2, '0');
    const dd = String(d.getUTCDate()).padStart(2, '0');
    return yyyy + '-' + mm + '-' + dd;
  }

  function triggerDownload(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 0);
  }

  const layoutSaveBtn = document.getElementById('layout-save');
  if (layoutSaveBtn) {
    layoutSaveBtn.addEventListener('click', function () {
      const positions = {};
      cy.nodes().forEach(function (node) {
        const p = node.position();
        positions[node.id()] = { x: p.x, y: p.y };
      });
      const payload = {
        layout: currentLayout,
        saved: new Date().toISOString(),
        positions: positions
      };
      const blob = new Blob(
        [JSON.stringify(payload, null, 2)],
        { type: 'application/json' }
      );
      const filename = 'call-graph-layout-' + currentLayout + '-' +
        formatDateForFilename(new Date()) + '.json';
      triggerDownload(blob, filename);
    });
  }

  // -----------------------------------------------------------------
  // Load layout (upload JSON)
  // -----------------------------------------------------------------
  const layoutLoadBtn = document.getElementById('layout-load');
  const layoutLoadInput = document.getElementById('layout-load-input');
  if (layoutLoadBtn && layoutLoadInput) {
    layoutLoadBtn.addEventListener('click', function () {
      layoutLoadInput.value = '';  // allow re-selecting the same file
      layoutLoadInput.click();
    });
    layoutLoadInput.addEventListener('change', function () {
      const file = layoutLoadInput.files && layoutLoadInput.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function () {
        let payload;
        try {
          payload = JSON.parse(reader.result);
        } catch (err) {
          window.alert('Could not parse layout file as JSON: ' + err.message);
          return;
        }
        const positions = payload && payload.positions;
        if (!positions || typeof positions !== 'object') {
          window.alert('Layout file is missing a "positions" object.');
          return;
        }
        let applied = 0;
        let missing = 0;
        cy.batch(function () {
          Object.keys(positions).forEach(function (nodeId) {
            const node = cy.getElementById(nodeId);
            if (node && !node.empty()) {
              const p = positions[nodeId];
              if (p && typeof p.x === 'number' && typeof p.y === 'number') {
                node.position({ x: p.x, y: p.y });
                // Persist to localStorage under the CURRENT layout key so
                // the loaded arrangement survives a reload even if the
                // user later re-runs or switches layouts.
                lsSet(posKey(currentLayout, nodeId), JSON.stringify(p));
                applied += 1;
              }
            } else {
              missing += 1;
            }
          });
        });
        cy.fit(undefined, 40);
        let msg = 'Loaded ' + applied + ' node position' +
          (applied === 1 ? '' : 's') + ' from ' + file.name + '.';
        if (missing > 0) {
          msg += ' ' + missing + ' node id' +
            (missing === 1 ? '' : 's') +
            ' in the file did not match the current graph (skipped).';
        }
        if (payload.layout && payload.layout !== currentLayout) {
          msg += ' Note: the file was saved under the "' + payload.layout +
            '" layout; positions have been applied on top of the current "' +
            currentLayout + '" layout.';
        }
        if (window.console) console.info(msg);
      };
      reader.onerror = function () {
        window.alert('Could not read layout file.');
      };
      reader.readAsText(file);
    });
  }

  // -----------------------------------------------------------------
  // Export SVG / PNG
  // -----------------------------------------------------------------
  const exportSvgBtn = document.getElementById('export-svg');
  if (exportSvgBtn) {
    exportSvgBtn.addEventListener('click', function () {
      if (typeof cy.svg !== 'function') {
        window.alert('SVG export requires the cytoscape-svg extension.');
        return;
      }
      const svgStr = cy.svg({ full: true, scale: 2 });
      const blob = new Blob([svgStr], { type: 'image/svg+xml' });
      triggerDownload(blob, 'call-graph-' + currentLayout + '.svg');
    });
  }

  const exportPngBtn = document.getElementById('export-png');
  if (exportPngBtn) {
    exportPngBtn.addEventListener('click', function () {
      const dataUrl = cy.png({ full: true, scale: 2, bg: '#ffffff' });
      const a = document.createElement('a');
      a.href = dataUrl;
      a.download = 'call-graph-' + currentLayout + '.png';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  }

  // -----------------------------------------------------------------
  // Side panel (Step 5) -- node descriptions, edges, pin/close/esc/arrows.
  // -----------------------------------------------------------------
  const LS_PANEL_OPEN = 'callGraph:panel:open';
  const LS_PANEL_PINNED = 'callGraph:panel:pinned';
  const LS_PANEL_LAST_NODE = 'callGraph:panel:lastNode';

  // Cache: id -> node data (faster than Array.find on every click).
  const nodeById = {};
  data.nodes.forEach(function (n) { nodeById[n.id] = n; });

  // Index edges by source / target id for O(1) lookup.
  const incomingByTarget = {};
  const outgoingBySource = {};
  data.edges.forEach(function (e) {
    (incomingByTarget[e.target] = incomingByTarget[e.target] || []).push(e);
    (outgoingBySource[e.source] = outgoingBySource[e.source] || []).push(e);
  });

  // Nodes sorted alphabetically by (type, label) for arrow-key cycling.
  const sortedNodes = data.nodes.slice().sort(function (a, b) {
    if (a.type !== b.type) return a.type < b.type ? -1 : 1;
    const al = (a.label || a.id).toLowerCase();
    const bl = (b.label || b.id).toLowerCase();
    if (al !== bl) return al < bl ? -1 : 1;
    return 0;
  });

  const TYPE_LABELS = {
    'skill': 'Skill',
    'skill-internal': 'Skill (internal)',
    'agent': 'Agent',
    'script': 'Script',
    'rule': 'Rule',
    'ref-general': 'Ref (general)',
    'ref-template': 'Ref (template)',
    'ref-project': 'Ref (project)'
  };

  const EDGE_GROUP_ORDER = [
    'invokes', 'delegates', 'orchestrates', 'dispatches-inline',
    'eager-load', 'lazy-load', 'imports'
  ];

  const EDGE_GROUP_LABELS = {
    'invokes': 'Calls scripts',
    'delegates': 'Delegates to agents',
    'orchestrates': 'Orchestrates skills',
    'dispatches-inline': 'Dispatches to internal workers',
    'eager-load': 'Eager-loads refs',
    'lazy-load': 'Lazy-loads refs',
    'imports': 'Imports modules'
  };

  const panel = document.getElementById('side-panel');
  const panelTitle = document.getElementById('side-panel-title');
  const panelBadge = document.getElementById('side-panel-type-badge');
  const panelPath = document.getElementById('side-panel-path');
  const panelDesc = document.getElementById('side-panel-description');
  const panelFallback = document.getElementById('side-panel-fallback-badge');
  const panelIncomingList = document.getElementById('side-panel-incoming-list');
  const panelOutgoingGroups = document.getElementById('side-panel-outgoing-groups');
  const pinBtn = document.getElementById('side-panel-pin');
  const closeBtn = document.getElementById('side-panel-close');

  let pinned = lsGet(LS_PANEL_PINNED, 'false') === 'true';
  let currentPanelNodeId = null;

  function escapeHtml(s) {
    return String(s || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // -----------------------------------------------------------------
  // Minimal Markdown renderer (~40 LOC).
  //
  // Handles: paragraphs, **bold**, *italic*, `inline code`, fenced
  // ```code``` blocks, blockquotes (`> text`), lists (`- item`).
  // Intentionally small; it is not meant to be CommonMark-compliant.
  // -----------------------------------------------------------------
  function renderInline(s) {
    // Escape first; then re-insert formatting spans.
    let out = escapeHtml(s);
    // Inline code backticks first to avoid interfering with bold/italic.
    out = out.replace(/`([^`]+)`/g, function (_m, code) {
      return '<code>' + code + '</code>';
    });
    out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    out = out.replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g,
      function (_m, pre, txt) { return pre + '<em>' + txt + '</em>'; });
    return out;
  }

  function renderMarkdown(md) {
    if (!md) return '';
    const src = String(md).replace(/\r\n/g, '\n');
    const html = [];
    const lines = src.split('\n');
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      // Fenced code block
      if (/^\s*```/.test(line)) {
        const buf = [];
        i++;
        while (i < lines.length && !/^\s*```/.test(lines[i])) {
          buf.push(escapeHtml(lines[i]));
          i++;
        }
        if (i < lines.length) i++; // consume closing fence
        html.push('<pre><code>' + buf.join('\n') + '</code></pre>');
        continue;
      }
      // Blank line separates blocks
      if (!line.trim()) { i++; continue; }
      // Blockquote run
      if (/^\s*>/.test(line)) {
        const buf = [];
        while (i < lines.length && /^\s*>/.test(lines[i])) {
          buf.push(lines[i].replace(/^\s*>\s?/, ''));
          i++;
        }
        html.push('<blockquote>' + renderInline(buf.join('\n').trim())
          .replace(/\n/g, '<br>') + '</blockquote>');
        continue;
      }
      // List run
      if (/^\s*-\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^\s*-\s+/.test(lines[i])) {
          items.push('<li>' + renderInline(lines[i].replace(/^\s*-\s+/, '')) + '</li>');
          i++;
        }
        html.push('<ul>' + items.join('') + '</ul>');
        continue;
      }
      // Paragraph run: consume until blank line.
      const buf = [line];
      i++;
      while (i < lines.length && lines[i].trim() &&
             !/^\s*```/.test(lines[i]) && !/^\s*>/.test(lines[i]) &&
             !/^\s*-\s+/.test(lines[i])) {
        buf.push(lines[i]);
        i++;
      }
      html.push('<p>' + renderInline(buf.join(' ')) + '</p>');
    }
    return html.join('\n');
  }

  // -----------------------------------------------------------------
  // Quick Guide parser: split a skill description into What/Example/When.
  // Uses heuristic matching on the inline bold markers. Returns null if
  // the structure does not match; caller falls back to raw rendering.
  // -----------------------------------------------------------------
  function parseQuickGuide(text) {
    if (!text) return null;
    const src = String(text).replace(/\r\n/g, '\n');
    const re = /\*\*([^*]+?)\*\*\s*:?/g;
    const markers = [];
    let m;
    while ((m = re.exec(src)) !== null) {
      markers.push({ label: m[1].trim(), start: m.index, afterLabel: m.index + m[0].length });
    }
    if (markers.length < 2) return null;
    function labelMatches(lbl, expected) {
      return lbl.toLowerCase().indexOf(expected) !== -1;
    }
    const findIdx = function (expected) {
      for (let k = 0; k < markers.length; k++) {
        if (labelMatches(markers[k].label, expected)) return k;
      }
      return -1;
    };
    const whatIdx = findIdx('what');
    const exampleIdx = findIdx('example');
    const whenIdx = findIdx('when');
    if (whatIdx < 0 || whenIdx < 0) return null;
    const sliceBetween = function (startMarker, endIdx) {
      const end = endIdx >= 0 ? markers[endIdx].start : src.length;
      return src.slice(startMarker.afterLabel, end).trim();
    };
    const what = sliceBetween(markers[whatIdx],
      exampleIdx >= 0 ? exampleIdx : whenIdx);
    const example = exampleIdx >= 0
      ? sliceBetween(markers[exampleIdx], whenIdx) : '';
    const when = sliceBetween(markers[whenIdx], -1);
    if (!what && !when) return null;
    return { what: what, example: example, when: when };
  }

  // -----------------------------------------------------------------
  // Panel population
  // -----------------------------------------------------------------
  function renderEdgeListItem(edge, otherEndId, label) {
    const li = document.createElement('li');
    const tag = document.createElement('span');
    tag.className = 'edge-type-tag';
    tag.textContent = edge.type;
    const text = document.createElement('span');
    text.textContent = label;
    li.appendChild(tag);
    li.appendChild(text);
    li.setAttribute('role', 'button');
    li.setAttribute('tabindex', '0');
    li.addEventListener('click', function () { openPanel(otherEndId); });
    li.addEventListener('keydown', function (evt) {
      if (evt.key === 'Enter' || evt.key === ' ') {
        evt.preventDefault();
        openPanel(otherEndId);
      }
    });
    return li;
  }

  function populateIncoming(nodeId) {
    panelIncomingList.innerHTML = '';
    const edges = incomingByTarget[nodeId] || [];
    if (!edges.length) {
      const li = document.createElement('li');
      li.className = 'edge-empty';
      li.textContent = 'No incoming edges.';
      panelIncomingList.appendChild(li);
      return;
    }
    edges.slice().sort(function (a, b) {
      const al = (nodeById[a.source] && nodeById[a.source].label) || a.source;
      const bl = (nodeById[b.source] && nodeById[b.source].label) || b.source;
      return al < bl ? -1 : al > bl ? 1 : 0;
    }).forEach(function (e) {
      const src = nodeById[e.source];
      const label = src ? src.label : e.source;
      panelIncomingList.appendChild(renderEdgeListItem(e, e.source, label));
    });
  }

  function populateOutgoing(nodeId) {
    panelOutgoingGroups.innerHTML = '';
    const edges = outgoingBySource[nodeId] || [];
    if (!edges.length) {
      const empty = document.createElement('p');
      empty.className = 'edge-empty';
      empty.style.cssText = 'color:#999;font-style:italic;font-size:12px;margin:4px 0;';
      empty.textContent = 'No outgoing edges.';
      panelOutgoingGroups.appendChild(empty);
      return;
    }
    const grouped = {};
    edges.forEach(function (e) {
      (grouped[e.type] = grouped[e.type] || []).push(e);
    });
    EDGE_GROUP_ORDER.forEach(function (type) {
      const group = grouped[type];
      if (!group || !group.length) return;
      const details = document.createElement('details');
      details.open = true;
      const summary = document.createElement('summary');
      summary.textContent = (EDGE_GROUP_LABELS[type] || type) +
        ' (' + group.length + ')';
      details.appendChild(summary);
      const ul = document.createElement('ul');
      ul.className = 'edge-list';
      group.slice().sort(function (a, b) {
        const al = (nodeById[a.target] && nodeById[a.target].label) || a.target;
        const bl = (nodeById[b.target] && nodeById[b.target].label) || b.target;
        return al < bl ? -1 : al > bl ? 1 : 0;
      }).forEach(function (e) {
        const tgt = nodeById[e.target];
        const label = tgt ? tgt.label : e.target;
        ul.appendChild(renderEdgeListItem(e, e.target, label));
      });
      details.appendChild(ul);
      panelOutgoingGroups.appendChild(details);
    });
  }

  function renderDescription(node) {
    panelDesc.innerHTML = '';
    const source = node.description_source || 'none';
    const text = node.description || '';

    if (source === 'none' || !text) {
      const p = document.createElement('p');
      p.className = 'edge-empty';
      p.style.cssText = 'color:#999;font-style:italic;';
      p.textContent = 'No description available for this node.';
      panelDesc.appendChild(p);
      return;
    }

    let htmlStr;
    if (source === 'quick-guide' && node.type === 'skill') {
      const parts = parseQuickGuide(text);
      if (parts) {
        const pieces = [];
        if (parts.what) {
          pieces.push('<h4>What this skill does for you</h4>' +
            renderMarkdown(parts.what));
        }
        if (parts.example) {
          pieces.push('<h4>Example</h4>' + renderMarkdown(parts.example));
        }
        if (parts.when) {
          pieces.push('<h4>When to use</h4>' + renderMarkdown(parts.when));
        }
        htmlStr = pieces.join('\n');
      } else {
        htmlStr = renderMarkdown(text);
      }
    } else {
      htmlStr = renderMarkdown(text);
    }

    // "Show more" collapser: if the HTML string is large, split after the
    // first <p>/<h4>+<p> block. Threshold = char length or line count.
    const approxLines = text.split('\n').length;
    if (approxLines > 12 || text.length > 600) {
      // Find first closing </p> or </blockquote> to split on.
      const container = document.createElement('div');
      container.innerHTML = htmlStr;
      const children = Array.from(container.children);
      if (children.length > 2) {
        const firstTwo = children.slice(0, 2);
        const rest = children.slice(2);
        firstTwo.forEach(function (el) { panelDesc.appendChild(el); });
        const details = document.createElement('details');
        const summary = document.createElement('summary');
        summary.textContent = 'Show more';
        details.appendChild(summary);
        rest.forEach(function (el) { details.appendChild(el); });
        panelDesc.appendChild(details);
        return;
      }
    }
    panelDesc.innerHTML = htmlStr;
  }

  function openPanel(nodeId) {
    const node = nodeById[nodeId];
    if (!node) return;
    currentPanelNodeId = nodeId;
    updateMatchSelection();

    // Type badge.
    const typeClass = 'type-' + node.type;
    panelBadge.className = 'type-badge ' + typeClass;
    panelBadge.textContent = TYPE_LABELS[node.type] || node.type;

    // Title.
    panelTitle.textContent = node.label || node.id;

    // Clickable path.
    const href = '../../../' + (node.path || '');
    panelPath.setAttribute('href', href);
    panelPath.textContent = node.path || '';

    // Description.
    renderDescription(node);

    // Fallback badge: "Developer-oriented -- awaiting designer rewrite".
    // Shown only when the description was extracted via the developer
    // fallback (first H1 + lead / docstring) rather than designer copy.
    if ((node.description_source || 'none') === 'developer-fallback') {
      panelFallback.textContent =
        'Developer-oriented \u2014 awaiting designer rewrite';
      panelFallback.hidden = false;
    } else {
      panelFallback.hidden = true;
    }

    // Edges.
    populateIncoming(nodeId);
    populateOutgoing(nodeId);

    // Open.
    panel.hidden = false;
    panel.setAttribute('aria-hidden', 'false');
    lsSet(LS_PANEL_OPEN, 'true');
    lsSet(LS_PANEL_LAST_NODE, nodeId);

    // Select in cytoscape (visually) without triggering another tap.
    try {
      cy.nodes().unselect();
      const target = cy.getElementById(nodeId);
      if (target && target.length) target.select();
    } catch (_e) { /* ignore */ }
  }

  function closePanel(keepSelection) {
    panel.hidden = true;
    panel.setAttribute('aria-hidden', 'true');
    lsSet(LS_PANEL_OPEN, 'false');
    currentPanelNodeId = null;
    updateMatchSelection();
    if (!pinned) {
      if (!keepSelection) {
        try { cy.nodes().unselect(); } catch (_e) { /* ignore */ }
      }
      clearFocus();
    }
  }

  function setPinned(value) {
    pinned = Boolean(value);
    lsSet(LS_PANEL_PINNED, pinned ? 'true' : 'false');
    if (pinBtn) {
      pinBtn.setAttribute('aria-pressed', pinned ? 'true' : 'false');
      pinBtn.textContent = pinned ? 'Pinned' : 'Pin';
    }
  }

  function focusNeighborhood(nodeId) {
    const focused = cy.getElementById(nodeId);
    if (!focused || focused.empty()) return;
    // closedNeighborhood returns the node itself, all connected edges,
    // and all 1-hop neighbor nodes.
    const neighborhood = focused.closedNeighborhood();
    cy.batch(function () {
      cy.elements().removeClass('faded');
      cy.elements().difference(neighborhood).addClass('faded');
    });
  }

  function clearFocus() {
    cy.batch(function () { cy.elements().removeClass('faded'); });
  }

  // Track Ctrl/Cmd key state independently — reading ctrlKey from
  // Cytoscape's synthetic evt.originalEvent is unreliable in Firefox.
  let _multiSelectActive = false;
  function _setMultiSelect(on) {
    _multiSelectActive = on;
    // Switch Cytoscape's selection model so it doesn't deselect everything
    // on the next tap while the modifier is held.
    cy.selectionType(on ? 'additive' : 'single');
    // selectionType('single') can reset boxSelectionEnabled to false in some
    // Cytoscape builds — re-assert it so Shift+drag always works.
    cy.boxSelectionEnabled(true);
  }
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Control' || e.key === 'Meta') _setMultiSelect(true);
  });
  document.addEventListener('keyup', function (e) {
    if (e.key === 'Control' || e.key === 'Meta') _setMultiSelect(false);
  });
  window.addEventListener('blur', function () { _setMultiSelect(false); });

  cy.on('tap', 'node', function (evt) {
    const node = evt.target;
    if (_multiSelectActive) {
      // Selection is handled by Cytoscape's additive mode; just skip the
      // panel / focus changes so the multi-selection stays intact.
      return;
    }
    const nodeId = node.data('id');
    openPanel(nodeId);
    focusNeighborhood(nodeId);
  });

  // When multiple nodes are selected, close the details pane and clear all
  // dimming — neither applies to a set of nodes.
  // keepSelection=true prevents closePanel from calling cy.nodes().unselect(),
  // which would immediately wipe the multi-selection we're building.
  cy.on('select unselect', 'node', function () {
    if (cy.$('node:selected').length > 1) {
      clearFocus();
      if (!pinned) closePanel(true);
    }
  });

  // Background tap (empty canvas) clears focus and, if not pinned, closes
  // the panel. Distinguish from node taps by checking evt.target === cy.
  cy.on('tap', function (evt) {
    if (evt.target === cy) {
      clearFocus();
      if (!pinned) closePanel();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', function () { closePanel(); });
  }
  if (pinBtn) {
    pinBtn.addEventListener('click', function () { setPinned(!pinned); });
  }

  document.addEventListener('keydown', function (evt) {
    if (evt.key === 'Escape') {
      if (pinned) {
        try { cy.nodes().unselect(); } catch (_e) { /* ignore */ }
      } else {
        closePanel();
      }
      return;
    }
    if (!pinned || panel.hidden) return;
    if (evt.key !== 'ArrowUp' && evt.key !== 'ArrowDown') return;
    if (!currentPanelNodeId) return;
    const cur = nodeById[currentPanelNodeId];
    if (!cur) return;
    const sameType = sortedNodes.filter(function (n) {
      return n.type === cur.type;
    });
    const idx = sameType.findIndex(function (n) {
      return n.id === currentPanelNodeId;
    });
    if (idx < 0) return;
    const delta = evt.key === 'ArrowDown' ? 1 : -1;
    const nextIdx = (idx + delta + sameType.length) % sameType.length;
    evt.preventDefault();
    openPanel(sameType[nextIdx].id);
    focusNeighborhood(sameType[nextIdx].id);
  });

  // Restore panel state on load.
  setPinned(pinned);
  const panelWasOpen = lsGet(LS_PANEL_OPEN, 'false') === 'true';
  const lastNode = lsGet(LS_PANEL_LAST_NODE, null);
  if (panelWasOpen && lastNode && nodeById[lastNode]) {
    openPanel(lastNode);
    focusNeighborhood(lastNode);
  }

  // -----------------------------------------------------------------
  // Initial render
  // -----------------------------------------------------------------
  restoreFilterState();
  updateNodeVisibility();
  runLayout(currentLayout);
})();
