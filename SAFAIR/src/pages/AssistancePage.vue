<template>
  <div class="assistance-page">

    <!-- ── Intro Modal ──────────────────────────────────────── -->
    <transition name="modal-fade">
      <div v-if="showIntroModal" class="modal-backdrop" @click.self="dismissModal">
        <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <button class="modal-close" @click="dismissModal" aria-label="Close">✕</button>

          <p class="modal-eyebrow">ASSISTANCE</p>
          <div class="modal-breeze-wrap">
            <svg class="breeze-mascot breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
                <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
                <circle cx="60" cy="72" r="46" fill="none" stroke="#0d9488" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
                <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
                <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
                <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
                <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
                <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
                <circle cx="52" cy="67" r="3.8" fill="#1c1917"/><circle cx="70" cy="67" r="3.8" fill="#1c1917"/>
                <circle cx="53.5" cy="65.5" r="1.4" fill="white"/><circle cx="71.5" cy="65.5" r="1.4" fill="white"/>
                <path d="M49 81 Q60 91 71 81" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
                <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".85"/>
                <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".85"/>
                <circle cx="94" cy="45" r="2.5" fill="#0d9488" opacity=".7"/>
                <circle cx="100" cy="56" r="1.8" fill="#14b8a6" opacity=".6"/>
              </svg>
          </div>
          <h2 id="modal-title">Your three protection tools</h2>
          <p class="modal-desc">
            This page brings together three real-time tools to help you protect your child before
            and during any activity. Switch between them using the slider at the top of the map.
          </p>

          <div class="modal-tools">
            <div class="modal-tool-card">
              <div class="modal-tool-header">
                <span class="tool-dot dustwatch"></span>
                <strong>DustWatch</strong>
                <span class="tool-badge realtime">Real-time</span>
              </div>
              <p>Shows active construction sites near your suburb and their current dust levels. Select a suburb to see a live map and ranked site list.</p>
            </div>

            <div class="modal-tool-card">
              <div class="modal-tool-header">
                <span class="tool-dot safespots"></span>
                <strong>SafeSpots</strong>
                <span class="tool-badge ai">AI-assisted</span>
              </div>
              <p>Finds asthma-safe parks and outdoor spaces near you, scored using live traffic, dust, pollen, and microclimate data. Powered by AI to rank the safest options.</p>
            </div>

            <div class="modal-tool-card">
              <div class="modal-tool-header">
                <span class="tool-dot clearpath"></span>
                <strong>ClearPath</strong>
                <span class="tool-badge ai">AI-assisted</span>
              </div>
              <p>Plans the safest walking or cycling route to your destination, avoiding dust zones, pollen hotspots, and high-traffic roads. AI selects and scores the routes.</p>
            </div>
          </div>

          <div class="modal-safeshelf">
            <p class="modal-safeshelf-eyebrow">ALSO CHECK YOUR HOME</p>
            <p>Outdoor protection is only part of the picture. SafeShelf checks the products in your home for hidden asthma triggers.</p>
            <button class="btn-safeshelf" @click="dismissModal">Open SafeShelf</button>
          </div>

          <button class="btn-show-map" @click="dismissModal">
            Got it — show me the map
          </button>
        </div>
      </div>
    </transition>

    <!-- ── Main Layout: map fills viewport, panel overlaid ─── -->
    <div class="page-layout">

      <!-- Tab switcher — floats above map -->
      <div class="tab-switcher">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-btn"
          :class="{ active: activeTab === tab.id, [tab.id]: true }"
          @click="switchTab(tab.id)"
        >
          <span class="tab-icon" v-html="tab.icon"></span>
          {{ tab.label }}
        </button>
      </div>

      <!-- Location hint -->
      <div class="location-hint">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        Uses your location to show nearby results
      </div>

      <!-- Left floating panel -->
      <aside class="side-panel">
        <div class="side-panel-inner">

        <!-- ── DUSTWATCH PANEL ─────────────────────────── -->
        <template v-if="activeTab === 'dustwatch'">
          <p class="panel-desc">Real-time dust levels from active construction sites in your suburb. Check before heading out with your child.</p>

          <!-- Breeze loading -->
          <div v-if="dustLoading" class="breeze-loading-inline">
            <svg class="breeze-mascot-sm breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
              <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
              <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
              <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
              <circle cx="53" cy="64" r="3.8" fill="#1c1917"/><circle cx="71" cy="64" r="3.8" fill="#1c1917"/>
              <ellipse cx="60" cy="84" rx="4.5" ry="3" fill="#c2410c" opacity=".45"/>
              <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".75"/>
              <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".8"/>
            </svg>
            <p class="breeze-caption">Checking dust levels nearby…</p>
          </div>

          <div v-if="activeArea.riskLevel" class="overall-risk-block">
            <div class="risk-label-row">
              <span class="risk-eyebrow">OVERALL RISK</span>
              <span class="risk-site-count">{{ activeArea.activeSites.length }} active sites</span>
            </div>
            <p class="risk-level-text" :class="activeArea.riskLevel.toLowerCase()">
              {{ activeArea.riskLevel }} Dust
            </p>
          </div>

          <!-- Breeze reacts to risk level — always visible after risk block loads -->
          <div v-if="activeArea.riskLevel && !dustLoading" class="breeze-risk-inline" :class="'breeze-risk-' + activeArea.riskLevel.toLowerCase()">
            <!-- Happy: Low -->
            <svg v-if="activeArea.riskLevel === 'Low'" class="breeze-mascot-sm breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#0d9488" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
              <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
              <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
              <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
              <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
              <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
              <circle cx="52" cy="67" r="3.8" fill="#1c1917"/><circle cx="70" cy="67" r="3.8" fill="#1c1917"/>
              <circle cx="53.5" cy="65.5" r="1.4" fill="white"/><circle cx="71.5" cy="65.5" r="1.4" fill="white"/>
              <path d="M49 81 Q60 91 71 81" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
              <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".85"/>
              <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".85"/>
            </svg>
            <!-- Curious: Moderate -->
            <svg v-else-if="activeArea.riskLevel === 'Moderate'" class="breeze-mascot-sm breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#d97706" stroke-width="2" stroke-dasharray="5 4" opacity=".45" class="breeze-ring"/>
              <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
              <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
              <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
              <circle cx="53" cy="64" r="3.8" fill="#1c1917"/><circle cx="71" cy="64" r="3.8" fill="#1c1917"/>
              <circle cx="54.5" cy="62.5" r="1.4" fill="white"/><circle cx="72.5" cy="62.5" r="1.4" fill="white"/>
              <ellipse cx="60" cy="84" rx="4.5" ry="3" fill="#c2410c" opacity=".45"/>
              <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".75"/>
              <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".8"/>
            </svg>
            <!-- Worried: High -->
            <svg v-else class="breeze-mascot-sm breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#ea2951" stroke-width="2.5" stroke-dasharray="4 3" opacity=".5" class="breeze-ring"/>
              <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
              <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
              <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#ea2951" opacity=".22"/>
              <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#ea2951" opacity=".22"/>
              <path d="M46 57 Q52 53 58 57" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
              <path d="M62 57 Q68 53 74 57" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
              <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
              <circle cx="51" cy="67" r="3.8" fill="#1c1917"/><circle cx="69" cy="67" r="3.8" fill="#1c1917"/>
              <path d="M49 85 Q60 79 71 85" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
              <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".65"/>
              <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".65"/>
            </svg>
            <p class="breeze-caption breeze-risk-msg">
              <span v-if="activeArea.riskLevel === 'Low'">All clear — great time to head outside!</span>
              <span v-else-if="activeArea.riskLevel === 'Moderate'">Some dust around — keep an eye on it.</span>
              <span v-else>High dust today — better to stay indoors!</span>
            </p>
          </div>

          <!-- Suburb selector -->
          <div class="suburb-selector-row">
            <button class="suburb-current-btn" @click="showSuburbDropdown = !showSuburbDropdown">
              {{ selectedSuburb }}
            </button>
            <button class="check-suburb-btn" @click="showSuburbDropdown = !showSuburbDropdown">
              Check Another Suburb
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline :points="showSuburbDropdown ? '18 15 12 9 6 15' : '6 9 12 15 18 9'"/></svg>
            </button>
          </div>

          <transition name="dropdown">
            <div v-if="showSuburbDropdown" class="suburb-dropdown">
              <p class="suburb-dropdown-label">SELECT A SUBURB</p>
              <div class="suburb-pills-grid">
                <button
                  v-for="suburb in suburbs"
                  :key="suburb"
                  class="suburb-pill-btn"
                  :class="{ active: suburb === selectedSuburb && !outsideCoverage }"
                  @click="pickSuburb(suburb)"
                >
                  {{ suburb }}
                </button>
              </div>
            </div>
          </transition>

          <!-- Location button -->
          <button
            class="use-location-btn"
            :disabled="!locationEnabled || dustLoading"
            @click="useMyLocation"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
            {{ dustLoading ? 'Loading…' : 'Use My Location' }}
          </button>

          <!-- Out of coverage -->
          <div v-if="activeArea.inCoverage === false" class="coverage-notice">
            <strong>Outside coverage area</strong>
            <p>Construction dust data is only available for inner Melbourne suburbs.</p>
          </div>

          <!-- Sites list -->
          <template v-else>
            <p v-if="dustError" class="panel-error">{{ dustError }}</p>

            <div v-if="activeArea.activeSites.length" class="sites-label">
              SITES NEAR {{ selectedSuburb.toUpperCase() }}
            </div>

            <div class="sites-scroll-list">
              <article
                v-for="site in activeArea.activeSites"
                :key="site.siteId"
                class="site-row"
                :class="{ selected: selectedSiteId === site.siteId }"
                @click="handleSiteSelect(site)"
              >
                <div class="site-row-info">
                  <strong>{{ site.title }}</strong>
                  <span>{{ site.distance }}</span>
                </div>
                <span class="site-risk-chip" :class="site.riskTone">
                  <span class="risk-breath-dot" :class="site.riskTone"></span>
                  {{ riskBadgeLabel(site.riskLabel) }}
                </span>
              </article>
            </div>

            <div class="panel-updated">
              <span class="updated-dot"></span>
              Last updated: {{ activeArea.lastUpdated }}
            </div>
          </template>
        </template>

        <!-- ── SAFESPOTS PANEL ─────────────────────────── -->
        <template v-if="activeTab === 'safespots'">
          <p class="panel-desc">Discover asthma-safe parks and outdoor spaces, rated using real-time air quality and dust data.</p>

          <div class="autocomplete-wrap">
            <svg class="input-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input
              v-model="safeSpotSearch"
              type="text"
              placeholder="Enter suburb or address…"
              class="panel-input has-icon"
              autocomplete="off"
              @input="onSpotInput"
              @keydown.down.prevent="moveSpotActive(1)"
              @keydown.up.prevent="moveSpotActive(-1)"
              @keydown.enter.prevent="pickSpotActive"
              @keydown.escape="spotSuggestions = []"
              @blur="onSpotBlur"
            />
            <transition name="dropdown">
              <ul v-if="spotSuggestions.length" class="suggestions-list">
                <li
                  v-for="(s, i) in spotSuggestions"
                  :key="s.place_id"
                  class="suggestion-item"
                  :class="{ active: i === spotActiveIdx }"
                  @mousedown.prevent="pickSpotSuggestion(i)"
                >
                  <span class="sug-icon-wrap">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                  </span>
                  <span class="sug-text">
                    <strong>{{ s._primary }}</strong>
                    <small>{{ s._secondary }}</small>
                  </span>
                </li>
              </ul>
            </transition>
          </div>

          <button
            class="use-location-btn"
            :disabled="safeSpotLoading"
            @click="useLocationForSpots"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
            Use my location
          </button>

          <div class="radius-control">
            <div class="radius-header">
              <span>Search radius</span>
              <span class="radius-value">{{ safeSpotRadius }} <small>km</small></span>
              <button class="radius-info-btn" title="Larger radius finds more spots but may be less accurate">ⓘ</button>
            </div>
            <input
              v-model.number="safeSpotRadius"
              type="range"
              min="1" max="10" step="1"
              class="radius-slider"
            />
            <div class="radius-ticks">
              <span>1km</span><span>3km</span><span>5km</span><span>8km</span><span>10km</span>
            </div>
          </div>

          <button class="btn-find-spots" @click="findSafeSpots" :disabled="safeSpotLoading">
            <span v-if="safeSpotLoading" class="spinner"></span>
            {{ safeSpotLoading ? 'Finding spots…' : 'Find SafeSpots' }}
          </button>

          <transition name="fade">
            <div v-if="safeSpotError" class="panel-error">
              <span>⚠</span> {{ safeSpotError }}
              <button @click="safeSpotError = ''">✕</button>
            </div>
          </transition>

          <!-- Category filters — shown after results load -->
          <div v-if="allSafeSpots.length" class="category-filters">
            <button
              v-for="cat in SPOT_CATEGORIES"
              :key="cat.id"
              class="cat-filter-btn"
              :class="{ active: activeCategory === cat.id }"
              @click="filterByCategory(cat.id)"
            >{{ cat.label }}</button>
          </div>

          <template v-if="safeSpots.length">
          <div class="score-legend">
            <span class="score-legend-label">Safety score:</span>
            <span class="score-legend-item good">70–100 Great</span>
            <span class="score-legend-item moderate">40–69 OK</span>
            <span class="score-legend-item poor">0–39 Poor</span>
          </div>

          <div class="spots-list">
            <article
              v-for="(spot, i) in safeSpots"
              :key="spot.id"
              class="spot-row"
              :class="{ selected: selectedSpotId === spot.id }"
              @click="selectSpot(spot)"
            >
              <div class="spot-rank">{{ i + 1 }}</div>
              <div class="spot-info">
                <strong>{{ spot.name }}</strong>
                <span>{{ spot.suburb }} — {{ spot.distance }}</span>
                <div class="spot-tags">
                  <span
                    v-for="tag in spot.tags.slice(0, 3)"
                    :key="tag"
                    class="spot-tag"
                    :class="tagClass(tag)"
                  >{{ tag }}</span>
                </div>
              </div>
              <div class="spot-score-col">
                <div class="spot-score-wrap">
                  <span class="spot-score" :class="scoreClass(spot.score)">{{ spot.score }}</span>
                  <span class="spot-score-label" :class="scoreClass(spot.score)">
                    {{ spot.score >= 70 ? 'Great' : spot.score >= 40 ? 'OK' : 'Poor' }}
                  </span>
                </div>
                <div class="spot-score-bar-bg">
                  <div class="spot-score-bar" :class="scoreClass(spot.score)" :style="{ width: spot.score + '%' }"></div>
                </div>
                <button
                  class="spot-clearpath-btn"
                  @click.stop="goToClearPath(spot)"
                >Get directions</button>
              </div>
            </article>
          </div>
          </template>

          <p v-if="allSafeSpots.length && !safeSpots.length" class="no-filter-results">
            No {{ activeCategory }} spots found. <button @click="filterByCategory('all')">Show all</button>
          </p>

          <!-- Breeze empty state — shown before any search -->
          <div v-if="!allSafeSpots.length && !safeSpotLoading" class="breeze-empty">
            <svg class="breeze-mascot breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
                <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
                <circle cx="60" cy="72" r="46" fill="none" stroke="#0d9488" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
                <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
                <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
                <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
                <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#0d9488" opacity=".2"/>
                <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
                <circle cx="52" cy="67" r="3.8" fill="#1c1917"/><circle cx="70" cy="67" r="3.8" fill="#1c1917"/>
                <circle cx="53.5" cy="65.5" r="1.4" fill="white"/><circle cx="71.5" cy="65.5" r="1.4" fill="white"/>
                <path d="M49 81 Q60 91 71 81" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-linecap="round"/>
                <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".85"/>
                <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".85"/>
                <circle cx="94" cy="45" r="2.5" fill="#0d9488" opacity=".7"/>
                <circle cx="100" cy="56" r="1.8" fill="#14b8a6" opacity=".6"/>
              </svg>
            <p class="breeze-caption">Search a suburb to find safe spots nearby</p>
          </div>
        </template>

        <!-- ── CLEARPATH PANEL ─────────────────────────── -->
        <template v-if="activeTab === 'clearpath'">
          <p class="panel-desc">Find the safest route for your child — avoiding construction dust, pollen, and high-traffic roads.</p>

          <button
            class="use-location-btn"
            :disabled="routeLoading"
            @click="useLocationForRoute"
            style="margin-bottom:8px"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
            Use my location as start
          </button>

          <div class="autocomplete-wrap" style="margin-bottom:10px">
            <span class="route-dot start-dot"></span>
            <input
              v-model="startPoint"
              type="text"
              placeholder="Starting point…"
              class="panel-input has-dot"
              autocomplete="off"
              @input="onInput('start')"
              @keydown.down.prevent="moveActive('start', 1)"
              @keydown.up.prevent="moveActive('start', -1)"
              @keydown.enter.prevent="pickActive('start')"
              @keydown.escape="clearSuggestions('start')"
              @blur="onBlur('start')"
            />
            <transition name="dropdown">
              <ul v-if="startSuggestions.length" class="suggestions-list">
                <li
                  v-for="(s, i) in startSuggestions"
                  :key="s.place_id"
                  class="suggestion-item"
                  :class="{ active: i === startActiveIdx }"
                  @mousedown.prevent="pickSuggestion('start', i)"
                >
                  <span class="sug-icon-wrap">
                    <svg v-if="isTransit(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
                    <svg v-else-if="isBuilding(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                    <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                  </span>
                  <span class="sug-text">
                    <strong>{{ s._primary }}</strong>
                    <small>{{ s._secondary }}</small>
                  </span>
                </li>
              </ul>
            </transition>
          </div>

          <div class="autocomplete-wrap" style="margin-bottom:14px">
            <span class="route-dot end-dot"></span>
            <input
              v-model="destination"
              type="text"
              placeholder="Destination…"
              class="panel-input has-dot"
              autocomplete="off"
              @input="onInput('dest')"
              @keydown.down.prevent="moveActive('dest', 1)"
              @keydown.up.prevent="moveActive('dest', -1)"
              @keydown.enter.prevent="pickActive('dest')"
              @keydown.escape="clearSuggestions('dest')"
              @blur="onBlur('dest')"
            />
            <transition name="dropdown">
              <ul v-if="destSuggestions.length" class="suggestions-list">
                <li
                  v-for="(s, i) in destSuggestions"
                  :key="s.place_id"
                  class="suggestion-item"
                  :class="{ active: i === destActiveIdx }"
                  @mousedown.prevent="pickSuggestion('dest', i)"
                >
                  <span class="sug-icon-wrap">
                    <svg v-if="isTransit(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/></svg>
                    <svg v-else-if="isBuilding(s)" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
                    <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="10" r="3"/><path d="M12 2a8 8 0 0 0-8 8c0 5.4 7.05 11.5 7.35 11.76a1 1 0 0 0 1.3 0C13 21.5 20 15.4 20 10a8 8 0 0 0-8-8z"/></svg>
                  </span>
                  <span class="sug-text">
                    <strong>{{ s._primary }}</strong>
                    <small>{{ s._secondary }}</small>
                  </span>
                </li>
              </ul>
            </transition>
          </div>

          <transition name="fade">
            <div v-if="routeError" class="panel-error" role="alert">
              <span>⚠</span> {{ routeError }}
              <button @click="routeError = null">✕</button>
            </div>
          </transition>

          <button
            class="btn-find-routes"
            :disabled="routeLoading"
            @click="findRoutes"
          >
            <span v-if="routeLoading" class="spinner"></span>
            {{ routeLoading ? 'Finding routes…' : 'Find Safe Routes' }}
          </button>

          <!-- Breeze empty state — no routes yet -->
          <div v-if="!routes.length && !routeLoading" class="breeze-empty">
            <svg class="breeze-mascot breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
                <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
                <circle cx="60" cy="72" r="46" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring"/>
                <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
                <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
                <ellipse cx="47" cy="79" rx="7" ry="4.5" fill="#7c3aed" opacity=".18"/>
                <ellipse cx="73" cy="79" rx="7" ry="4.5" fill="#7c3aed" opacity=".18"/>
                <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
                <circle cx="53" cy="64" r="3.8" fill="#1c1917"/><circle cx="71" cy="64" r="3.8" fill="#1c1917"/>
                <circle cx="54.5" cy="62.5" r="1.4" fill="white"/><circle cx="72.5" cy="62.5" r="1.4" fill="white"/>
                <ellipse cx="60" cy="84" rx="4.5" ry="3" fill="#c2410c" opacity=".45"/>
                <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".75"/>
                <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".8"/>
                <circle cx="95" cy="43" r="2.5" fill="#7c3aed" opacity=".5"/>
              </svg>
            <p class="breeze-caption">Enter a start and destination to find the safest route</p>
          </div>

          <!-- Route mode toggle -->
          <div v-if="routes.length" class="route-mode-toggle">
            <button
              class="mode-btn"
              :class="{ active: routeMode === 'standard' }"
              @click="setRouteMode('standard')"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h18M13 5l7 7-7 7"/></svg>
              Standard
            </button>
            <button
              class="mode-btn"
              :class="{ active: routeMode === 'strict' }"
              @click="setRouteMode('strict')"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M4.93 4.93l14.14 14.14"/></svg>
              Avoid zones
            </button>
          </div>
          <p v-if="routes.length === 1 && routeMode === 'strict'" class="same-route-notice">
            No alternative path available — construction zones cannot be fully avoided on this route.
          </p>

          <!-- Route results -->
          <div v-if="routes.length" class="routes-list">
            <article
              class="route-row selected"
              :class="routes[selectedRouteIndex].tone"
            >
              <div class="route-row-top">
                <div class="route-name-wrap">
                  <strong>{{ routeMode === 'strict' && selectedRouteIndex === 1 ? 'Avoid zones' : routeMode === 'strict' && selectedRouteIndex === 0 ? 'Standard' : routes[selectedRouteIndex].name }}</strong>
                </div>
              </div>
              <div class="route-meta">{{ routes[selectedRouteIndex].time }} &nbsp;·&nbsp; {{ routes[selectedRouteIndex].distance }}</div>
              <div class="route-tags">
                <span v-for="note in routes[selectedRouteIndex].notes.slice(0,2)" :key="note" class="route-tag" :class="routes[selectedRouteIndex].tone">
                  {{ note.replace('✓ ', '').replace('⚠ ', '') }}
                </span>
              </div>
              <p v-if="routes[selectedRouteIndex].reason" class="route-reason">{{ routes[selectedRouteIndex].reason }}</p>
            </article>

            <!-- Avoidance stats — shown when in strict mode and comparison data available -->
            <div v-if="routeMode === 'strict' && routeComparison && routes.length > 1" class="avoidance-card">
              <p class="avoidance-title">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>
                What you're avoiding
              </p>
              <div class="avoidance-row">
                <div class="avoidance-stat">
                  <span class="avoidance-num avoidance-good">{{ Math.round(routeComparison.dust_reduction_pct) }}%</span>
                  <span class="avoidance-label">less dust</span>
                </div>
                <div class="avoidance-divider"/>
                <div class="avoidance-stat">
                  <span class="avoidance-num avoidance-good">{{ Math.round(routeComparison.pollen_reduction_pct) }}%</span>
                  <span class="avoidance-label">less pollen</span>
                </div>
                <div class="avoidance-divider"/>
                <div class="avoidance-stat">
                  <span class="avoidance-num avoidance-cost">+{{ Math.round(routeComparison.extra_duration_min * 10) / 10 }} min</span>
                  <span class="avoidance-label">extra time</span>
                </div>
              </div>
              <p class="avoidance-msg">{{ routeComparison.message }}</p>
            </div>
          </div>
        </template>

        </div>
      </aside>

      <!-- Map container — fills full page -->
      <div ref="mapContainer" class="map-container"></div>

      <!-- Right legend panel -->
      <div class="legend-panel">
        <template v-if="activeTab === 'dustwatch'">
          <div class="legend-item"><span class="legend-dot high"></span><span>High Dust</span></div>
          <div class="legend-item"><span class="legend-dot moderate"></span><span>Moderate</span></div>
          <div class="legend-item"><span class="legend-dot low"></span><span>Low</span></div>
          <div class="legend-item"><span class="legend-dot location"></span><span>Your location</span></div>
          
        </template>
        <template v-else-if="activeTab === 'safespots'">
          <div class="legend-item"><span class="legend-dot high-risk"></span><span>High risk (75+)</span></div>
          <div class="legend-item"><span class="legend-dot moderate-risk"></span><span>Moderate (25-75)</span></div>
          <div class="legend-item"><span class="legend-dot good"></span><span>Good (0-25)</span></div>
        </template>
        <template v-else>
          <div class="legend-item"><span class="legend-line recommended"></span><span>Recommended</span></div>
          <div class="legend-item"><span class="legend-line alternative"></span><span>Alternative</span></div>
          <div class="legend-item"><span class="legend-dot high"></span><span>Dust zone</span></div>
          <div class="legend-item"><span class="legend-dot pollen"></span><span>Pollen / trees</span></div>
        </template>
        <div class="legend-item">
  <span class="legend-dot wind"></span>
  <span>Wind: {{ dustWeather.wind_speed_ms ?? '--' }} m/s</span>
</div>

<div class="legend-item">
  <span class="legend-dot temp"></span>
  <span>Temp: {{ dustWeather.temperature ?? '--' }}°C</span>
</div>
      </div>

      <!-- Active alert card (DustWatch only) -->
      <transition name="fade">
        <div v-if="activeTab === 'dustwatch' && activeArea.riskLevel === 'High'" class="alert-card">
          <p class="alert-eyebrow">ACTIVE ALERT</p>
          <strong>High dust in {{ selectedSuburb }}</strong>
          <p>{{ activeArea.activeSites.length }} active sites within 2km reporting elevated dust. Avoid outdoor play 10am - 3pm.</p>
        </div>
      </transition>

      <!-- Disclaimer -->
      <div class="disclaimer-note">
        <strong>Note:</strong> Environmental guidance only. Always follow your child's asthma action plan.
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  requestNotificationPermission,
  subscribeToPush,
  unsubscribeFromPush,
} from '../utils/pushNotifications'

// ── Constants ────────────────────────────────────────────────────
const ROUTE_API_BASE    = 'https://d204zergykc1k6.cloudfront.net/safe-route'
const DUST_API_BASE     =  'https://d204zergykc1k6.cloudfront.net'
const SAFESPOTS_API_BASE = 'https://d204zergykc1k6.cloudfront.net/safe-route'
const USER_ID_KEY    = 'safair_user_id'
const VAPID_PUBLIC_KEY = 'BKQZlKonq6g7x2ocp8Z0z1Ay_CzkI832VCMDSMUbFgdkI9Px56qllIsB5qfZ1lajm7MmUJl6-30pv-ax4kI6f0o'

const FALLBACK_SUBURBS = [
  'Carlton', 'Docklands', 'East Melbourne', 'Kensington', 'Melbourne',
  'North Melbourne', 'Parkville', 'South Yarra', 'Southbank', 'West Melbourne',
]

const dustWeather = ref({
  temperature: null,
  wind_speed_ms: null
})

const SUBURB_COORDS = {
  Carlton:          { lat: -37.8008, lon: 144.9669 },
  Docklands:        { lat: -37.8147, lon: 144.9489 },
  'East Melbourne': { lat: -37.8167, lon: 144.9875 },
  Kensington:       { lat: -37.7942, lon: 144.9271 },
  Melbourne:        { lat: -37.8136, lon: 144.9631 },
  'North Melbourne':{ lat: -37.7994, lon: 144.9460 },
  Parkville:        { lat: -37.7873, lon: 144.9510 },
  'South Yarra':    { lat: -37.8380, lon: 144.9930 },
  Southbank:        { lat: -37.8250, lon: 144.9640 },
  'West Melbourne': { lat: -37.8098, lon: 144.9424 },
}

// ── City of Melbourne coverage bounds ────────────────────────────
const CITY_OF_MELB_BOUNDS = {
  minLat: -37.8600, maxLat: -37.7600,
  minLon: 144.9100, maxLon: 145.0100,
}
const MELB_SUGGEST_BOUNDS = {
  minLat: -37.8650, maxLat: -37.7550,
  minLon: 144.9050, maxLon: 145.0150,
}

function isInCityOfMelbourne(lat, lon) {
  return (
    lat >= CITY_OF_MELB_BOUNDS.minLat && lat <= CITY_OF_MELB_BOUNDS.maxLat &&
    lon >= CITY_OF_MELB_BOUNDS.minLon && lon <= CITY_OF_MELB_BOUNDS.maxLon
  )
}
function isInSuggestBounds(lat, lon) {
  return (
    lat >= MELB_SUGGEST_BOUNDS.minLat && lat <= MELB_SUGGEST_BOUNDS.maxLat &&
    lon >= MELB_SUGGEST_BOUNDS.minLon && lon <= MELB_SUGGEST_BOUNDS.maxLon
  )
}
function melbourneQuery(q) {
  const lower = q.toLowerCase()
  if (/\b(vic|victoria|nsw|qld|sa|wa|tas|nt|act)\b/.test(lower)) return q
  if (/\b3\d{3}\b/.test(q)) return q
  return `${q}, Melbourne VIC`
}

// Simple suburb name → address search term mapping
const SUBURB_SEARCH_TERM = {}

const tabs = [
  { id: 'dustwatch', label: 'DustWatch', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><circle cx="12" cy="13" r="3"/></svg>' },
  { id: 'safespots', label: 'SafeSpots', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 22s-8-4.5-8-11.8A8 8 0 0 1 12 2a8 8 0 0 1 8 8.2c0 7.3-8 11.8-8 11.8z"/><circle cx="12" cy="10" r="3"/></svg>' },
  { id: 'clearpath', label: 'ClearPath', icon: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 12h18M13 5l7 7-7 7"/></svg>' },
]


// ── Global state ─────────────────────────────────────────────────
const showIntroModal = ref(true)
const activeTab      = ref('dustwatch')
const mapContainer   = ref(null)

// ── DustWatch state (ported from ConstructionDustPage) ───────────
const selectedSuburb      = ref('Melbourne')
const suburbs             = ref([...FALLBACK_SUBURBS])
const areaBySuburb        = ref({})
const dustLoading         = ref(false)
const dustError           = ref('')
const locationEnabled     = ref(true)
const pushEnabled         = ref(false)
const selectedSiteId      = ref(null)
const outsideCoverage     = ref(false)
const showSuburbDropdown  = ref(false)
const currentLat          = ref(null)
const currentLon          = ref(null)
const usingPreciseLocation= ref(false)

const fallbackArea = {
  lastUpdated: '--:--',
  summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
  summaryTitle: 'No active construction sites nearby',
  summaryText: 'We could not find active sites near this location right now.',
  riskLevel: null,
  riskRecommendation: '',
  activeSites: [],
  inCoverage: true,
  tips: ['Carry your reliever inhaler when leaving home', 'Choose routes away from visible construction dust when possible', 'Shorten vigorous outdoor sessions if symptoms appear'],
}

const activeArea = computed(() => areaBySuburb.value[selectedSuburb.value] || fallbackArea)

const mapCenter = computed(() => {
  if (usingPreciseLocation.value && typeof currentLat.value === 'number' && typeof currentLon.value === 'number') {
    return { lat: currentLat.value, lon: currentLon.value, label: 'your current location' }
  }
  const c = SUBURB_COORDS[selectedSuburb.value] || SUBURB_COORDS.Melbourne
  return { lat: c.lat, lon: c.lon, label: `${selectedSuburb.value} center` }
})

// ── SafeSpots state (demo) ───────────────────────────────────────
const safeSpotSearch   = ref('')
const safeSpotRadius   = ref(2)
const safeSpotLoading  = ref(false)
const safeSpotError    = ref('')
const safeSpots        = ref([])
const allSafeSpots     = ref([])   // unfiltered full list
const selectedSpotId   = ref(null)
const activeCategory   = ref('all')
const spotSuggestions  = ref([])
const spotActiveIdx    = ref(-1)
let spotTimer = null
const safeSpotOriginLat = ref(null)
const safeSpotOriginLon = ref(null)

const SPOT_CATEGORIES = [
  { id: 'all',        label: 'All' },
  { id: 'park',       label: 'Parks' },
  { id: 'playground', label: 'Playgrounds' },
  { id: 'childcare',  label: 'Childcare' },
  { id: 'landmark',   label: 'Landmarks' },
]

function onSpotInput() {
  clearTimeout(spotTimer)
  const q = safeSpotSearch.value
  if (!q || q.length < 2) { spotSuggestions.value = []; return }
  spotTimer = setTimeout(async () => {
    const results = await fetchSuggestions(q)
    spotSuggestions.value = results
    spotActiveIdx.value = -1
  }, 300)
}

function moveSpotActive(dir) {
  const next = Math.max(-1, Math.min(spotSuggestions.value.length - 1, spotActiveIdx.value + dir))
  spotActiveIdx.value = next
}

function pickSpotActive() {
  if (spotActiveIdx.value >= 0) pickSpotSuggestion(spotActiveIdx.value)
  else findSafeSpots()
}

function pickSpotSuggestion(index) {
  const item = spotSuggestions.value[index]
  if (!item) return
  safeSpotSearch.value = item._secondary ? `${item._primary}, ${item._secondary}` : item._primary
  spotSuggestions.value = []
  spotActiveIdx.value = -1
  findSafeSpots()
}

function onSpotBlur() {
  setTimeout(() => { spotSuggestions.value = [] }, 150)
}

function filterByCategory(cat) {
  activeCategory.value = cat
  if (cat === 'all') {
    safeSpots.value = [...allSafeSpots.value]
  } else {
    safeSpots.value = allSafeSpots.value.filter(s => s.category === cat)
  }
}

// ── ClearPath state (ported from SafeRoutePlanning) ──────────────
const startPoint          = ref('')
const destination         = ref('')
const routeLoading        = ref(false)
const routeError          = ref(null)
const routes              = ref([])
const selectedRouteIndex  = ref(0)
const routeGeometries     = ref([])
const routeMode           = ref('standard') // 'standard' | 'strict'
const routeComparison     = ref(null)
const dustZones           = ref([])
const pollenZones         = ref([])
const startSuggestions    = ref([])
const destSuggestions     = ref([])
const startActiveIdx      = ref(-1)
const destActiveIdx       = ref(-1)
let startTimer = null
let destTimer  = null

// ── Leaflet (outside Vue reactivity) ────────────────────────────
let leafletMap     = null
let routeLayers    = []
let zoneLayers     = []
let dustMarkers    = []
let spotMarkers    = []

// ────────────────────────────────────────────────────────────────
// Utilities
// ────────────────────────────────────────────────────────────────
const getUserId = () => {
  let id = localStorage.getItem(USER_ID_KEY)
  if (!id) { id = crypto.randomUUID(); localStorage.setItem(USER_ID_KEY, id) }
  return id
}

const buildDustApiUrl = (path) => `${DUST_API_BASE.replace(/\/$/, '')}${path}`
const buildPreferencesUrl  = () => buildDustApiUrl('/user-preferences-api')
const buildCurrentRiskUrl  = (s) => buildDustApiUrl(`/api/current-risk?suburb=${encodeURIComponent(s)}`)

const riskBadgeLabel = (label = '') => label.replace('Risk', 'Dust')

const tagClass = (tag = '') => {
  const t = tag.toLowerCase()
  if (t.includes('no active') || t.includes('quiet') || t.includes('good') || t.includes('low dust') || t.includes('minimal pollen') || t.includes('outside')) return 'tag-good'
  if (t.includes('moderate') || t.includes('some') || t.includes('warn')) return 'tag-warn'
  if (t.includes('high') || t.includes('busy') || t.includes('heavy')) return 'tag-bad'
  return 'tag-neutral'
}

const scoreClass = (score) => {
  if (score >= 70) return 'score-good'
  if (score >= 40) return 'score-moderate'
  return 'score-poor'
}


// ────────────────────────────────────────────────────────────────
// Modal
// ────────────────────────────────────────────────────────────────
function dismissModal() {
  showIntroModal.value = false
}

// ────────────────────────────────────────────────────────────────
// Tab switching
// ────────────────────────────────────────────────────────────────
async function switchTab(tabId) {
  activeTab.value = tabId
  await nextTick()
  if (tabId === 'dustwatch') renderDustMap()
  else if (tabId === 'safespots') renderSafeSpotsMap()
  else if (tabId === 'clearpath') {
    clearLeafletMap()
    initBaseMap(SUBURB_COORDS.Melbourne.lat, SUBURB_COORDS.Melbourne.lon)
  }
}

// ────────────────────────────────────────────────────────────────
// Leaflet helpers
// ────────────────────────────────────────────────────────────────
function loadLeaflet() {
  return new Promise(resolve => {
    if (window.L) return resolve(window.L)
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    link.crossOrigin = 'anonymous'
    document.head.appendChild(link)
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    script.crossOrigin = 'anonymous'
    script.onload = () => resolve(window.L)
    document.head.appendChild(script)
  })
}

function clearLeafletMap() {
  if (!leafletMap) return
  // Remove EVERY layer except the base tile layer — guarantees nothing bleeds across tabs
  leafletMap.eachLayer(layer => {
    if (layer._url) return // keep tile layer
    try { leafletMap.removeLayer(layer) } catch {}
  })
  routeLayers  = []
  zoneLayers   = []
  dustMarkers  = []
  spotMarkers  = []
  leafletMap.closePopup()
}

async function initBaseMap(lat, lon) {
  const L = await loadLeaflet()
  if (!mapContainer.value) return
  if (leafletMap) {
    leafletMap.setView([lat, lon], 14)
    return L
  }
  leafletMap = L.map(mapContainer.value, { zoomControl: true, scrollWheelZoom: true })
    .setView([lat, lon], 14)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '© <a href="https://www.openstreetmap.org/copyright">OSM</a> © <a href="https://carto.com/">CARTO</a>',
    maxZoom: 19,
  }).addTo(leafletMap)
  return L
}

// ── DustWatch map ────────────────────────────────────────────────
async function renderDustMap() {
  const L = await initBaseMap(mapCenter.value.lat, mapCenter.value.lon)
  if (!L) return
  clearLeafletMap()

  const boundsPoints = []
  const getRiskColor = (tone) => tone === 'high' ? '#ea2951' : tone === 'moderate' ? '#d36c00' : '#11915d'

  // Centre marker — kid icon for current location
  const kidCenterIcon = L.divIcon({
    className: '',
    html: `<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">
      <div style="
        width:44px;height:44px;border-radius:50%;
        background:white;
        border:2.5px solid #1d4ed8;
        box-shadow:0 4px 14px rgba(0,0,0,0.18);
        display:flex;align-items:center;justify-content:center;
      ">
        <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="16" cy="9" r="5.5" fill="#fed7aa"/>
          <ellipse cx="16" cy="5" rx="5.5" ry="3" fill="#92400e"/>
          <rect x="11" y="15" width="10" height="8" rx="3" fill="#1d4ed8"/>
          <rect x="7" y="15" width="4.5" height="2.5" rx="1.2" fill="#1d4ed8" transform="rotate(-20 7 15)"/>
          <rect x="20.5" y="15" width="4.5" height="2.5" rx="1.2" fill="#1d4ed8" transform="rotate(20 20.5 15)"/>
          <rect x="11.5" y="22" width="3" height="7" rx="1.5" fill="#92400e" opacity=".8"/>
          <rect x="17.5" y="22" width="3" height="7" rx="1.5" fill="#92400e" opacity=".8"/>
          <circle cx="14" cy="9" r="1" fill="#1c1917"/>
          <circle cx="18" cy="9" r="1" fill="#1c1917"/>
          <path d="M13.5 11.5 Q16 13.5 18.5 11.5" fill="none" stroke="#c2410c" stroke-width="1" stroke-linecap="round"/>
        </svg>
      </div>
      <div style="
        background:#1d4ed8;color:white;
        font-size:9px;font-weight:700;
        padding:2px 7px;border-radius:8px;
        box-shadow:0 2px 6px rgba(0,0,0,0.15);
        white-space:nowrap;font-family:system-ui,sans-serif;
      ">You are here</div>
    </div>`,
    iconSize: [44, 72],
    iconAnchor: [22, 72],
  })
  const centerMarker = L.marker([mapCenter.value.lat, mapCenter.value.lon], { icon: kidCenterIcon })
    .bindPopup(`<strong>📍 ${mapCenter.value.label}</strong>`)
  centerMarker.addTo(leafletMap)
  dustMarkers.push(centerMarker)
  boundsPoints.push([mapCenter.value.lat, mapCenter.value.lon])

  activeArea.value.activeSites.forEach(site => {
    if (typeof site.lat !== 'number' || typeof site.lon !== 'number') return
    const color = getRiskColor(site.riskTone)
    const isSelected = selectedSiteId.value && String(selectedSiteId.value) === String(site.siteId)
    const size = isSelected ? 44 : 36

    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:${size}px;height:${size}px;border-radius:50%;
        background:white;
        border:${isSelected ? 3 : 2.5}px solid ${color};
        box-shadow:0 ${isSelected ? 6 : 3}px ${isSelected ? 18 : 10}px rgba(0,0,0,${isSelected ? 0.22 : 0.14});
        display:flex;align-items:center;justify-content:center;
        transition:all 0.2s;
      ">
        <svg width="${isSelected ? 24 : 19}" height="${isSelected ? 24 : 19}" viewBox="0 0 32 32" fill="none">
          <rect x="14" y="6" width="3" height="22" rx="1.5" fill="${color}"/>
          <rect x="6" y="6" width="22" height="3" rx="1.5" fill="${color}"/>
          <line x1="17" y1="9" x2="26" y2="20" stroke="${color}" stroke-width="1.8" stroke-linecap="round"/>
          <rect x="5" y="25" width="10" height="4" rx="1" fill="${color}" opacity=".7"/>
          <circle cx="7" cy="29" r="1.5" fill="${color}"/>
          <circle cx="13" cy="29" r="1.5" fill="${color}"/>
        </svg>
      </div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2],
    })

    const popup = `<div style="min-width:160px"><strong>${site.title}</strong><br/>${site.type}<br/>${site.distance}<br/><strong>${site.riskLabel}</strong></div>`
    const marker = L.marker([site.lat, site.lon], { icon })
    marker.bindPopup(popup)
    marker.addTo(leafletMap)
    dustMarkers.push(marker)
    boundsPoints.push([site.lat, site.lon])
  })

  if (boundsPoints.length > 1) {
    leafletMap.fitBounds(boundsPoints, { padding: [40, 40] })
  }

}

// ── SafeSpots map ────────────────────────────────────────────────
async function renderSafeSpotsMap() {
  const centerLat = safeSpotOriginLat.value ?? SUBURB_COORDS.Melbourne.lat
  const centerLon = safeSpotOriginLon.value ?? SUBURB_COORDS.Melbourne.lon
  const L = await initBaseMap(centerLat, centerLon)
  if (!L) return
  clearLeafletMap()

  const getColor = (score) => score >= 70 ? '#11915d' : score >= 40 ? '#d36c00' : '#ea2951'

  // Draw search radius circle around the origin
  if (safeSpots.value.length > 0 && safeSpotOriginLat.value) {
    const radiusM = safeSpotRadius.value * 1000
    const radiusCircle = L.circle([centerLat, centerLon], {
      radius: radiusM,
      color: '#1d4ed8',
      fillColor: '#1d4ed8',
      fillOpacity: 0.04,
      weight: 1.5,
      dashArray: '6 5',
      opacity: 0.5,
    })
    radiusCircle.addTo(leafletMap)
    spotMarkers.push(radiusCircle)

    // Origin pin
    const originIcon = L.divIcon({
      className: '',
      html: `<div style="width:12px;height:12px;border-radius:50%;background:#1d4ed8;border:3px solid white;box-shadow:0 2px 8px rgba(29,78,216,0.4);"></div>`,
      iconAnchor: [6, 6],
    })
    const originMarker = L.marker([centerLat, centerLon], { icon: originIcon })
    originMarker.bindTooltip(`Search origin · ${safeSpotRadius.value}km radius`, { className: 'zone-tip', permanent: false })
    originMarker.addTo(leafletMap)
    spotMarkers.push(originMarker)
  }

  safeSpots.value.forEach(spot => {
    const color = getColor(spot.score)
    const isSelected = selectedSpotId.value === spot.id

    const circle = L.circle([spot.lat, spot.lon], {
      color, fillColor: color,
      fillOpacity: isSelected ? 0.3 : 0.15,
      radius: isSelected ? 120 : 80,
      weight: isSelected ? 3 : 2,
    })

    const icon = L.divIcon({
      className: '',
      html: `<div style="width:32px;height:32px;border-radius:50%;background:${color};border:3px solid white;box-shadow:0 4px 12px rgba(0,0,0,0.2);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:11px;color:white;">${spot.score}</div>`,
      iconAnchor: [16, 16],
    })
    const marker = L.marker([spot.lat, spot.lon], { icon })
    marker.bindPopup(`<div style="min-width:150px"><strong>${spot.name}</strong><br/>${spot.suburb}<br/>Safety score: <strong>${spot.score}</strong></div>`)

    circle.addTo(leafletMap)
    marker.addTo(leafletMap)
    spotMarkers.push(circle, marker)
  })

  if (safeSpots.value.length > 0) {
    // Fit to radius circle bounds so user can see the full search area
    const radiusM = safeSpotRadius.value * 1000
    const radiusBounds = L.circle([centerLat, centerLon], { radius: radiusM }).getBounds()
    leafletMap.fitBounds(radiusBounds, { padding: [30, 30] })
  }
}

// ── Route map ────────────────────────────────────────────────────
const ROUTE_COLOURS = ['#0d9488', '#d97706', '#7c3aed', '#e24d32']

function drawZones() {
  if (!leafletMap) return
  const L = window.L
  zoneLayers.forEach(l => leafletMap.removeLayer(l))
  zoneLayers = []

  // 🏗 Dust zones — crane SVG icon
  const craneIcon = (color) => L.divIcon({
    className: '',
    html: `<div style="
      width:36px;height:36px;border-radius:50%;
      background:white;
      border:2.5px solid ${color};
      box-shadow:0 3px 10px rgba(0,0,0,0.15);
      display:flex;align-items:center;justify-content:center;
    ">
      <svg width="20" height="20" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="14" y="6" width="3" height="22" rx="1.5" fill="${color}"/>
        <rect x="6" y="6" width="22" height="3" rx="1.5" fill="${color}"/>
        <line x1="17" y1="9" x2="26" y2="20" stroke="${color}" stroke-width="1.8" stroke-linecap="round"/>
        <rect x="5" y="25" width="10" height="4" rx="1" fill="${color}" opacity=".7"/>
        <circle cx="7" cy="29" r="1.5" fill="${color}"/>
        <circle cx="13" cy="29" r="1.5" fill="${color}"/>
      </svg>
    </div>`,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  })

  dustZones.value.forEach(z => {
    const color = '#e45d3e'
    const m = L.marker([z.lat, z.lon], { icon: craneIcon(color) }).addTo(leafletMap)
    m.bindTooltip(`🏗 Dust zone — ${z.label}`, { sticky: true, className: 'zone-tip' })
    zoneLayers.push(m)
  })

  // 🌳 Pollen zones — tree SVG icon
  const treeIcon = (active) => {
    const color = active ? '#16a34a' : '#84cc16'
    return L.divIcon({
      className: '',
      html: `<div style="
        width:36px;height:36px;border-radius:50%;
        background:white;
        border:2.5px solid ${color};
        box-shadow:0 3px 10px rgba(0,0,0,0.15);
        display:flex;align-items:center;justify-content:center;
      ">
        <svg width="20" height="20" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <ellipse cx="16" cy="13" rx="9" ry="10" fill="${color}" opacity=".9"/>
          <ellipse cx="10" cy="17" rx="7" ry="8" fill="${color}"/>
          <ellipse cx="22" cy="17" rx="7" ry="8" fill="${color}"/>
          <rect x="14" y="22" width="4" height="7" rx="2" fill="#92400e"/>
        </svg>
      </div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
    })
  }

  pollenZones.value.forEach(z => {
    const label = z.inSeason ? '🌿 Pollen zone — currently in season' : '🌳 Trees nearby — low pollen risk now'
    const m = L.marker([z.lat, z.lon], { icon: treeIcon(z.inSeason) }).addTo(leafletMap)
    m.bindTooltip(label, { sticky: true, className: 'zone-tip' })
    zoneLayers.push(m)
  })
}

async function drawRoutes(selectedIdx) {
  if (!leafletMap || !routeGeometries.value.length) return
  const L = window.L
  routeLayers.forEach(l => leafletMap.removeLayer(l))
  routeLayers = []

  routeGeometries.value.forEach((geom, idx) => {
    if (idx === selectedIdx || !geom?.coordinates?.length) return
    const ll = geom.coordinates.map(([lon, lat]) => [lat, lon])
    const col = ROUTE_COLOURS[idx] ?? '#888'
    routeLayers.push(L.polyline(ll, { color: col, weight: 3, opacity: 0.45, dashArray: '8 10' }).addTo(leafletMap))
  })

  const sel = routeGeometries.value[selectedIdx]
  if (sel?.coordinates?.length) {
    const ll = sel.coordinates.map(([lon, lat]) => [lat, lon])
    // strict mode = amber/warning colour to signal "avoiding zones"
    const col = routeMode.value === 'strict' && selectedIdx === 1 ? '#d97706' : (ROUTE_COLOURS[selectedIdx] ?? '#0d9488')
    const glow = L.polyline(ll, { color: col, weight: 16, opacity: 0.08 }).addTo(leafletMap)
    const line = L.polyline(ll, { color: col, weight: 5, opacity: 1, lineJoin: 'round', lineCap: 'round' }).addTo(leafletMap)
    const kidIcon = L.divIcon({
      className: '',
      html: `<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">
        <div style="
          width:44px;height:44px;border-radius:50%;
          background:white;
          border:2.5px solid ${col};
          box-shadow:0 4px 14px rgba(0,0,0,0.18);
          display:flex;align-items:center;justify-content:center;
        ">
          <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Head -->
            <circle cx="16" cy="9" r="5.5" fill="#fed7aa"/>
            <!-- Hair -->
            <ellipse cx="16" cy="5" rx="5.5" ry="3" fill="#92400e"/>
            <!-- Body -->
            <rect x="11" y="15" width="10" height="8" rx="3" fill="${col}"/>
            <!-- Left arm -->
            <rect x="7" y="15" width="4.5" height="2.5" rx="1.2" fill="${col}" transform="rotate(-20 7 15)"/>
            <!-- Right arm -->
            <rect x="20.5" y="15" width="4.5" height="2.5" rx="1.2" fill="${col}" transform="rotate(20 20.5 15)"/>
            <!-- Left leg -->
            <rect x="11.5" y="22" width="3" height="7" rx="1.5" fill="#92400e" opacity=".8"/>
            <!-- Right leg -->
            <rect x="17.5" y="22" width="3" height="7" rx="1.5" fill="#92400e" opacity=".8"/>
            <!-- Face - eyes -->
            <circle cx="14" cy="9" r="1" fill="#1c1917"/>
            <circle cx="18" cy="9" r="1" fill="#1c1917"/>
            <!-- Smile -->
            <path d="M13.5 11.5 Q16 13.5 18.5 11.5" fill="none" stroke="#c2410c" stroke-width="1" stroke-linecap="round"/>
          </svg>
        </div>
        <div style="
          background:${col};color:white;
          font-size:9px;font-weight:700;
          padding:2px 7px;border-radius:8px;
          box-shadow:0 2px 6px rgba(0,0,0,0.15);
          white-space:nowrap;font-family:system-ui,sans-serif;
        ">We start here</div>
      </div>`,
      iconSize: [44, 72],
      iconAnchor: [22, 72],
    })

    const flagIcon = L.divIcon({
      className: '',
      html: `<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">
        <div style="
          width:44px;height:44px;border-radius:50%;
          background:#2b63bd;
          border:2.5px solid white;
          box-shadow:0 4px 14px rgba(0,0,0,0.2);
          display:flex;align-items:center;justify-content:center;
        ">
          <svg width="24" height="24" viewBox="0 0 32 32" fill="none">
            <!-- Flagpole -->
            <rect x="10" y="5" width="2.5" height="22" rx="1.25" fill="white"/>
            <!-- Flag -->
            <path d="M12.5 5 L26 10 L12.5 15 Z" fill="white" opacity=".9"/>
            <!-- Star on flag -->
            <polygon points="19,9 19.7,11.1 22,11.1 20.3,12.4 20.9,14.5 19,13.2 17.1,14.5 17.7,12.4 16,11.1 18.3,11.1" fill="#2b63bd"/>
          </svg>
        </div>
        <div style="
          background:#2b63bd;color:white;
          font-size:9px;font-weight:700;
          padding:2px 7px;border-radius:8px;
          box-shadow:0 2px 6px rgba(0,0,0,0.15);
          white-space:nowrap;font-family:system-ui,sans-serif;
        ">Safe destination</div>
      </div>`,
      iconSize: [44, 72],
      iconAnchor: [22, 72],
    })

    const sm = L.marker(ll[0], { icon: kidIcon }).addTo(leafletMap).bindPopup(`<div class="map-popup"><strong>🧒 Starting point</strong><br>${startPoint.value}</div>`)
    const em = L.marker(ll[ll.length - 1], { icon: flagIcon }).addTo(leafletMap).bindPopup(`<div class="map-popup"><strong>🏁 Safe destination</strong><br>${destination.value}</div>`)
    routeLayers.push(glow, line, sm, em)
    leafletMap.fitBounds(line.getBounds(), { padding: [48, 48] })
  }
}

function selectRoute(index) {
  selectedRouteIndex.value = index
  drawRoutes(index)
  drawConstructionSitesOnRoute()
}

function setRouteMode(mode) {
  routeMode.value = mode
  // standard = recommended (index 0), strict = avoid_irritants (index 1 if different route exists)
  const idx = mode === 'strict' && routeGeometries.value.length > 1 ? 1 : 0
  selectedRouteIndex.value = idx
  drawRoutes(idx)
  drawConstructionSitesOnRoute()
}

async function drawConstructionSitesOnRoute() {
  if (!leafletMap || !routeGeometries.value.length) return
  const L = window.L
  const getRiskColor  = (tone) => tone === 'high' ? '#ea2951' : tone === 'moderate' ? '#d36c00' : '#11915d'
  const getRiskTone   = (distM) => distM <= 250 ? 'high' : distM <= 500 ? 'moderate' : 'low'
  const getRiskLabel  = (distM) => distM <= 250 ? 'High Risk' : distM <= 500 ? 'Moderate Risk' : 'Low Risk'

  // Sample points evenly along the recommended route
  const coords = routeGeometries.value[0]?.coordinates ?? []
  if (!coords.length) return

  // Pick ~5 sample points spread along the route
  const sampleCount = Math.min(5, coords.length)
  const step = Math.floor(coords.length / sampleCount)
  const samplePoints = Array.from({ length: sampleCount }, (_, i) => {
    const pt = coords[Math.min(i * step, coords.length - 1)]
    return { lat: pt[1], lon: pt[0] }
  })

  // Fetch construction sites near each sample point (500m radius)
  const allSites = new Map() // siteId → site, deduplicated
  await Promise.allSettled(samplePoints.map(async ({ lat, lon }) => {
    try {
      const res  = await fetch(buildDustApiUrl(`/v1/construction/nearby?lat=${lat}&lon=${lon}&radius=500`))
      const data = await res.json()
      if (data.ok && data.sites) {
        data.sites.forEach(s => {
          if (!allSites.has(s.siteId) && typeof s.lat === 'number' && typeof s.lon === 'number') {
            allSites.set(s.siteId, s)
          }
        })
      }
    } catch {}
  }))

  // Draw all deduplicated sites — crane icon, no circles
  allSites.forEach(site => {
    const distM = Number(site.distanceM)
    const tone  = getRiskTone(distM)
    const color = getRiskColor(tone)

    const icon = L.divIcon({
      className: '',
      html: `<div style="
        width:32px;height:32px;border-radius:50%;
        background:white;
        border:2.5px solid ${color};
        box-shadow:0 3px 10px rgba(0,0,0,0.15);
        display:flex;align-items:center;justify-content:center;
      ">
        <svg width="18" height="18" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="14" y="6" width="3" height="22" rx="1.5" fill="${color}"/>
          <rect x="6" y="6" width="22" height="3" rx="1.5" fill="${color}"/>
          <line x1="17" y1="9" x2="26" y2="20" stroke="${color}" stroke-width="1.8" stroke-linecap="round"/>
          <rect x="5" y="25" width="10" height="4" rx="1" fill="${color}" opacity=".7"/>
          <circle cx="7" cy="29" r="1.5" fill="${color}"/>
          <circle cx="13" cy="29" r="1.5" fill="${color}"/>
        </svg>
      </div>`,
      iconSize: [32, 32],
      iconAnchor: [16, 16],
    })

    const tooltip = `🏗 ${site.address || 'Construction site'} — ${getRiskLabel(distM)}`
    const marker = L.marker([site.lat, site.lon], { icon })
    marker.bindTooltip(tooltip, { sticky: true, className: 'zone-tip' })
    marker.addTo(leafletMap)
    zoneLayers.push(marker)
  })
}

// ────────────────────────────────────────────────────────────────
// DustWatch logic (ported from ConstructionDustPage)
// ────────────────────────────────────────────────────────────────
const normalizeSuburbName = (v = '') =>
  v.toLowerCase().replace(/\([^)]*\)/g, '').replace(/\b(vic|victoria|melbourne city|city of melbourne)\b/g, '').replace(/[^a-z\s]/g, ' ').replace(/\s+/g, ' ').trim()

const matchSupportedSuburb = (detected = '') => {
  const nd = normalizeSuburbName(detected)
  if (!nd) return 'Melbourne'
  const exact = suburbs.value.find(s => normalizeSuburbName(s) === nd)
  if (exact) return exact
  const partial = suburbs.value.find(s => { const ns = normalizeSuburbName(s); return nd.includes(ns) || ns.includes(nd) })
  return partial || 'Melbourne'
}

const getSuburbFromCoordinates = async (lat, lon) => {
  const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&zoom=16&addressdetails=1`, { headers: { Accept: 'application/json' } })
  if (!res.ok) throw new Error(`Reverse geocoding failed (${res.status})`)
  const data = await res.json()
  const a = data?.address || {}
  return a.suburb || a.neighbourhood || a.city_district || a.town || a.city || a.municipality || 'Melbourne'
}

const loadCurrentRiskBySuburb = async (suburbName = 'Melbourne') => {
  try {
    const res = await fetch(buildCurrentRiskUrl(suburbName))
    const data = await res.json()

    console.log('Current risk API response:', data)

    if (!res.ok || !data.success) {
      throw new Error(data.error || `Current risk failed (${res.status})`)
    }

    dustWeather.value = {
      temperature: data.weather?.temperature ?? null,
      wind_speed_ms: data.weather?.wind_speed_ms ?? null
    }

    return {
      level: data?.overall_risk?.level || null,
      recommendation: data?.overall_risk?.recommendation || ''
    }
  } catch (err) {
    console.error('Current risk failed:', err)
    dustWeather.value = {
      temperature: null,
      wind_speed_ms: null
    }
    return null
  }
}

const toBlocksText = (distanceM, sourceLabel) => {
  if (!Number.isFinite(distanceM)) return `Distance from ${sourceLabel} unavailable`
  const blocks = Math.max(1, Math.round(distanceM / 100))
  return `${blocks} ${blocks === 1 ? 'block' : 'blocks'} from ${sourceLabel} (${Math.round(distanceM)} m)`
}

const getSiteRiskMeta = (distanceM) => {
  if (Number.isFinite(distanceM) && distanceM <= 250) return { riskLabel: 'High Risk',     riskTone: 'high' }
  if (Number.isFinite(distanceM) && distanceM <= 500) return { riskLabel: 'Moderate Risk', riskTone: 'moderate' }
  return { riskLabel: 'Low Risk', riskTone: 'low' }
}

const getSiteType = (site) => site.workType || site.permitType || site.category || site.description || 'Active construction work'

const mapNearbyPayloadToArea = (payload, suburbName = 'Melbourne', currentRisk = null) => {
  const queryMode  = payload?.queryMode || 'suburb'
  const sourceLabel = queryMode === 'coords' ? 'your current location' : `${suburbName || payload?.selectedSuburb || 'selected suburb'} center`
  const activeSites = (payload?.sites || []).map(site => {
    const distanceM = Number(site.distanceM)
    return { siteId: site.siteId || `${site.address}-${site.distanceM}`, title: site.address || 'Unknown address', type: getSiteType(site), distance: toBlocksText(distanceM, sourceLabel), distanceM, lat: typeof site.lat === 'number' ? site.lat : null, lon: typeof site.lon === 'number' ? site.lon : null, ...getSiteRiskMeta(distanceM) }
  })
  const inCoverage  = payload?.inCoverage !== false
  const hasSites    = activeSites.length > 0
  const resultCount = Number(payload?.count ?? activeSites.length)
  const cappedAtFive= resultCount >= 5
  return {
    lastUpdated: new Date().toLocaleTimeString('en-AU', { hour: 'numeric', minute: '2-digit' }),
    inCoverage,
    summaryEyebrow: 'NEARBY CONSTRUCTION SITES',
    summaryTitle: hasSites ? (cappedAtFive ? 'At least 5 active construction sites nearby' : `${activeSites.length} active construction sites nearby`) : 'No active construction sites nearby',
    summaryText: hasSites ? (queryMode === 'coords' ? 'Nearest active permits around your current location are shown below.' : `Nearest active permits around ${suburbName || 'this area'} center are shown below.`) : `No active permits were found near ${suburbName || 'this area'} within your search radius.`,
    riskLevel: inCoverage ? currentRisk?.level || null : null,
    riskRecommendation: inCoverage ? currentRisk?.recommendation || '' : '',
    activeSites,
    tips: fallbackArea.tips,
  }
}

const loadNearbyByCoords = async (lat, lon, suburbName = 'Melbourne') => {
  dustLoading.value = true
  dustError.value   = ''
  try {
    const nearbyRes = await fetch(buildDustApiUrl(`/v1/construction/nearby?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}&radius=800`))
    const data = await nearbyRes.json()
    if (!nearbyRes.ok || !data.ok) throw new Error(data.message || `Nearby sites failed (${nearbyRes.status})`)
    let currentRisk = null
    if (data.inCoverage !== false) currentRisk = await loadCurrentRiskBySuburb(suburbName)
    const mappedArea = mapNearbyPayloadToArea(data, suburbName, currentRisk)
    outsideCoverage.value = mappedArea.inCoverage === false
    // Use real API data always — only fall back if API completely fails
    areaBySuburb.value = { ...areaBySuburb.value, [suburbName]: mappedArea }
  } catch (err) {
    dustError.value = err.message || 'Could not load dust data right now.'
  } finally {
    dustLoading.value = false
  }
}

const loadNearbyBySuburb = async (suburbName = 'Melbourne') => {
  dustLoading.value = true
  dustError.value   = ''
  try {
    const centre = SUBURB_COORDS[suburbName] || SUBURB_COORDS.Melbourne
    const currentRisk = await loadCurrentRiskBySuburb(suburbName)

    // Same logic as ClearPath: sample 5 points around suburb centre,
    // fetch sites near each, deduplicate by siteId, filter by suburb name in address
    const offsets = [
      { dlat: 0,      dlon: 0 },
      { dlat:  0.004, dlon:  0.004 },
      { dlat: -0.004, dlon:  0.004 },
      { dlat:  0.004, dlon: -0.004 },
      { dlat: -0.004, dlon: -0.004 },
    ]

    const allSites = new Map()
    await Promise.allSettled(offsets.map(async ({ dlat, dlon }) => {
      try {
        const res  = await fetch(buildDustApiUrl(`/v1/construction/nearby?lat=${centre.lat + dlat}&lon=${centre.lon + dlon}&radius=800`))
        const data = await res.json()
        if (data.ok && data.sites) {
          data.sites.forEach(s => {
            if (!allSites.has(s.siteId) && typeof s.lat === 'number' && typeof s.lon === 'number') {
              allSites.set(s.siteId, s)
            }
          })
        }
      } catch {}
    }))

    // Filter by suburb name in address (case-insensitive)
    const searchTerm = (SUBURB_SEARCH_TERM[suburbName] || suburbName).toLowerCase()
    const matchedSites = [...allSites.values()].filter(s =>
      (s.address || s.siteAddress || '').toLowerCase().includes(searchTerm)
    )

    const payload = {
      ok: true,
      inCoverage: true,
      queryMode: 'suburb',
      selectedSuburb: suburbName,
      count: matchedSites.length,
      sites: matchedSites,
    }

    areaBySuburb.value = { ...areaBySuburb.value, [suburbName]: mapNearbyPayloadToArea(payload, suburbName, currentRisk) }
  } catch (err) {
    dustError.value = err.message || 'Could not load dust data right now.'
  } finally {
    dustLoading.value = false
  }
}

const savePreferences = async (pushSubscription = undefined) => {
  try {
    const body = { locationEnabled: locationEnabled.value, selectedSuburb: selectedSuburb.value, pushEnabled: pushEnabled.value }
    if (pushSubscription !== undefined) body.pushSubscription = pushSubscription
    await fetch(buildPreferencesUrl(), { method: 'PATCH', headers: { 'Content-Type': 'application/json', 'X-Anonymous-User-Id': getUserId() }, body: JSON.stringify(body) })
  } catch (err) { console.error('Failed to save preferences', err) }
}

const loadPreferences = async () => {
  try {
    const res  = await fetch(buildPreferencesUrl(), { headers: { 'X-Anonymous-User-Id': getUserId() } })
    const data = await res.json()
    if (data.ok && data.preferences) {
      locationEnabled.value = typeof data.preferences.locationEnabled === 'boolean' ? data.preferences.locationEnabled : true
      selectedSuburb.value  = typeof data.preferences.selectedSuburb  === 'string'  && data.preferences.selectedSuburb.trim() ? data.preferences.selectedSuburb.trim() : 'Melbourne'
      pushEnabled.value     = typeof data.preferences.pushEnabled     === 'boolean' ? data.preferences.pushEnabled : false
    }
  } catch (err) { console.error('Failed to load preferences', err) }
}

const selectSuburb = async (suburb) => {
  selectedSiteId.value       = null
  usingPreciseLocation.value = false
  currentLat.value           = null
  currentLon.value           = null
  outsideCoverage.value      = false
  selectedSuburb.value       = suburb
  await savePreferences()
  const cachedArea = areaBySuburb.value[suburb]
  if (cachedArea && cachedArea.lastUpdated !== '--:--') return
  await loadNearbyBySuburb(suburb)
}

const pickSuburb = async (suburb) => {
  showSuburbDropdown.value = false
  await selectSuburb(suburb)
  await nextTick()
  if (activeTab.value === 'dustwatch') renderDustMap()
}

const handleSiteSelect = async (site) => {
  selectedSiteId.value = null
  await nextTick()
  selectedSiteId.value = site.siteId
  // Fly to the site — same animation as SafeSpots
  if (leafletMap && typeof site.lat === 'number' && typeof site.lon === 'number') {
    leafletMap.flyTo([site.lat, site.lon], Math.max(leafletMap.getZoom(), 16), {
      duration: 0.7,
      easeLinearity: 0.25,
    })
  }
}

const useMyLocation = async () => {
  if (!locationEnabled.value || !navigator.geolocation) return
  dustLoading.value = true
  dustError.value   = ''
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude } = position.coords
        currentLat.value = latitude
        currentLon.value = longitude
        usingPreciseLocation.value = true

        // Fetch nearby sites first — API tells us the nearest supported suburb
        const nearbyRes = await fetch(buildDustApiUrl(`/v1/construction/nearby?lat=${latitude}&lon=${longitude}&radius=800`))
        const nearbyData = await nearbyRes.json()

        // Use nearestSupportedSuburb from API if available, else reverse geocode
        let matched = nearbyData?.nearestSupportedSuburb
        if (!matched) {
          const detected = await getSuburbFromCoordinates(latitude, longitude)
          matched = matchSupportedSuburb(detected)
        }
        selectedSuburb.value = matched || 'Melbourne'

        // Auto-fill SafeSpots search with the detected suburb
        if (matched && matched !== 'Melbourne') {
          safeSpotSearch.value = matched + ', Melbourne VIC'
        }

        // Auto-fill ClearPath start point with coordinates
        if (!startPoint.value) {
          startPoint.value = matched ? `${matched}, Melbourne VIC` : `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
        }

        const currentRisk = matched ? await loadCurrentRiskBySuburb(matched) : null
        const mappedArea = mapNearbyPayloadToArea(nearbyData, matched || 'your location', currentRisk)
        outsideCoverage.value = mappedArea.inCoverage === false
        areaBySuburb.value = { ...areaBySuburb.value, [selectedSuburb.value]: mappedArea }

        await savePreferences()
        if (activeTab.value === 'dustwatch') renderDustMap()
      } catch (err) {
        dustError.value = err.message || 'Could not load dust data for your location.'
      } finally {
        dustLoading.value = false
      }
    },
    () => { dustLoading.value = false; dustError.value = 'Location access failed — please select a suburb manually.' },
    { enableHighAccuracy: true, timeout: 12000 }
  )
}

// ────────────────────────────────────────────────────────────────
// SafeSpots logic (real API)
// ────────────────────────────────────────────────────────────────
async function findSafeSpots() {
  const query = safeSpotSearch.value.trim()
  if (!query) {
    safeSpotError.value = 'Enter a suburb or address first.'
    return
  }
  safeSpotLoading.value = true
  safeSpotError.value   = ''
  selectedSpotId.value  = null
  safeSpots.value       = []

  try {
    const radiusM = safeSpotRadius.value * 1000
    const url = `${SAFESPOTS_API_BASE}/api/safespots/by-address?q=${encodeURIComponent(query)}&radius=${radiusM}&sort=score&limit=20`
    const res  = await fetch(url)
    const data = await res.json()

    if (!data.success) throw new Error(data.error || 'Could not load SafeSpots.')

    // Normalise API response into the shape the map + list expect
    const mapped = (data.places || []).map(p => ({
      id:       p.id,
      name:     p.name,
      suburb:   p.address || p.category_label || '',
      distance: p.distance_m >= 1000
        ? `${(p.distance_m / 1000).toFixed(1)} km`
        : `${Math.round(p.distance_m)} m`,
      score:    p.safety_score,
      verdict:  p.verdict,
      tags:     (p.highlights || []).map(h => typeof h === 'object' ? h.text : h),
      category: p.category || 'landmark',
      lat:      p.lat,
      lon:      p.lon,
    }))

    allSafeSpots.value = mapped
    activeCategory.value = 'all'
    safeSpots.value = mapped
    // Store origin for map centering
    if (data.origin?.lat && data.origin?.lon) {
      safeSpotOriginLat.value = data.origin.lat
      safeSpotOriginLon.value = data.origin.lon
    }

    if (!safeSpots.value.length) {
      safeSpotError.value = `No safe spots found within ${safeSpotRadius.value} km of "${query}". Try a larger radius.`
    }

    await nextTick()
    renderSafeSpotsMap()

  } catch (err) {
    safeSpotError.value = err.message || 'Could not load SafeSpots right now.'
  } finally {
    safeSpotLoading.value = false
  }
}

function selectSpot(spot) {
  selectedSpotId.value = spot.id
  // Just fly to the spot — no full map re-render
  if (leafletMap && typeof spot.lat === 'number' && typeof spot.lon === 'number') {
    leafletMap.flyTo([spot.lat, spot.lon], Math.max(leafletMap.getZoom(), 16), {
      duration: 0.7,
      easeLinearity: 0.25,
    })
  }
}

function goToClearPath(spot) {
  destination.value = spot.suburb ? `${spot.name}, ${spot.suburb}` : spot.name
  activeTab.value   = 'clearpath'
  nextTick(() => {
    clearLeafletMap()  // clear SafeSpots markers before switching
    initBaseMap(spot.lat, spot.lon)
  })
}

// ────────────────────────────────────────────────────────────────
// ClearPath logic (ported from SafeRoutePlanning)
async function useLocationForSpots() {
  if (!navigator.geolocation) return
  safeSpotLoading.value = true
  safeSpotError.value = ''
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude } = position.coords
        const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}&zoom=16&addressdetails=1`, { headers: { Accept: 'application/json' } })
        const data = await res.json()
        const a = data?.address || {}
        const suburb = a.suburb || a.neighbourhood || a.city_district || ''
        const postcode = a.postcode || ''
        safeSpotSearch.value = suburb ? `${suburb}, Melbourne VIC ${postcode}`.trim() : `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`
        await findSafeSpots()
      } catch {
        safeSpotSearch.value = `${position.coords.latitude.toFixed(5)}, ${position.coords.longitude.toFixed(5)}`
        await findSafeSpots()
      }
    },
    () => {
      safeSpotLoading.value = false
      safeSpotError.value = 'Location access denied. Please enter an address manually.'
    },
    { enableHighAccuracy: true, timeout: 10000 }
  )
}

async function useLocationForRoute() {
  if (!navigator.geolocation) {
    routeError.value = 'Geolocation is not supported by your browser. Please enter a start address manually.'
    return
  }
  routeLoading.value = true
  routeError.value = null

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const { latitude, longitude } = position.coords

        if (!isInCityOfMelbourne(latitude, longitude)) {
          routeError.value = 'Your current location is outside the City of Melbourne. ClearPath only covers the City of Melbourne — please enter a start address manually (e.g. Melbourne CBD, Carlton, Docklands, Southbank).'
          return
        }

        const res = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}&zoom=16&addressdetails=1`,
          { headers: { Accept: 'application/json' } }
        )
        const data = await res.json()
        const a = data?.address || {}
        const suburb = a.suburb || a.neighbourhood || a.city_district || ''
        const postcode = a.postcode || ''
        startPoint.value = suburb
          ? `${suburb}, Melbourne VIC ${postcode}`.trim()
          : `${latitude.toFixed(5)}, ${longitude.toFixed(5)}`
      } catch {
        startPoint.value = `${position.coords.latitude.toFixed(5)}, ${position.coords.longitude.toFixed(5)}`
      } finally {
        routeLoading.value = false
      }
    },
    (err) => {
      routeLoading.value = false
      if (err.code === 1) {
        // PERMISSION_DENIED
        routeError.value = 'Location permission was denied. Please allow location access in your browser settings, or enter a start address manually.'
      } else if (err.code === 2) {
        // POSITION_UNAVAILABLE
        routeError.value = 'Your location could not be determined right now. Please enter a start address manually.'
      } else if (err.code === 3) {
        // TIMEOUT
        routeError.value = 'Location request timed out. Please enter a start address manually.'
      } else {
        routeError.value = 'Could not get your location. Please enter a start address manually.'
      }
    },
    { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 }
  )
}


// ────────────────────────────────────────────────────────────────
async function fetchSuggestions(query) {
  if (!query || query.length < 2) return []
  try {
    const url = new URL(`${ROUTE_API_BASE}/api/geocode`)
    url.searchParams.set('q', melbourneQuery(query))
    url.searchParams.set('bounded', '1')
    url.searchParams.set('viewbox', `${MELB_SUGGEST_BOUNDS.minLon},${MELB_SUGGEST_BOUNDS.maxLat},${MELB_SUGGEST_BOUNDS.maxLon},${MELB_SUGGEST_BOUNDS.minLat}`)
    const res  = await fetch(url.toString())
    const data = await res.json()
    if (!Array.isArray(data)) return []
    return data
      .filter(r => {
        const lat = parseFloat(r.lat); const lon = parseFloat(r.lon)
        return !isNaN(lat) && !isNaN(lon) && isInSuggestBounds(lat, lon)
      })
      .map(r => {
        const a = r.address || {}
        const primary = a.amenity || a.building || a.shop || a.tourism || a.leisure || a.office || a.stadium || (a.house_number && a.road ? `${a.house_number} ${a.road}` : null) || a.road || a.suburb || a.city_district || r.display_name.split(',')[0]
        const suburb   = a.suburb || a.city_district || a.neighbourhood || ''
        const postcode = a.postcode || ''
        const secondary = [suburb, 'VIC', postcode].filter(Boolean).join(', ')
        return { ...r, _primary: primary, _secondary: secondary }
      })
  } catch { return [] }
}

function isTransit(s) { const t = s.type || ''; const c = s.class || ''; return ['station', 'stop', 'tram_stop', 'bus_stop', 'subway'].includes(t) || c === 'railway' || c === 'public_transport' }
function isBuilding(s) { const t = s.type || ''; const c = s.class || ''; return ['university', 'school', 'hospital', 'hotel', 'restaurant', 'cafe', 'shop', 'building', 'amenity'].includes(t) || c === 'amenity' || c === 'building' || c === 'tourism' }

function onInput(field) {
  const isStart = field === 'start'
  const query   = isStart ? startPoint.value : destination.value
  clearTimeout(isStart ? startTimer : destTimer)
  if (!query || query.length < 2) { isStart ? (startSuggestions.value = []) : (destSuggestions.value = []); return }
  const t = setTimeout(async () => {
    const results = await fetchSuggestions(query)
    if (isStart) { startSuggestions.value = results; startActiveIdx.value = -1 }
    else         { destSuggestions.value  = results; destActiveIdx.value  = -1 }
  }, 300)
  isStart ? (startTimer = t) : (destTimer = t)
}

function moveActive(field, dir) {
  const isStart = field === 'start'
  const list    = isStart ? startSuggestions.value : destSuggestions.value
  const cur     = isStart ? startActiveIdx.value   : destActiveIdx.value
  const next    = Math.max(-1, Math.min(list.length - 1, cur + dir))
  isStart ? (startActiveIdx.value = next) : (destActiveIdx.value = next)
}

function pickActive(field) { const idx = field === 'start' ? startActiveIdx.value : destActiveIdx.value; if (idx >= 0) pickSuggestion(field, idx) }

function pickSuggestion(field, index) {
  const isStart = field === 'start'
  const item    = (isStart ? startSuggestions.value : destSuggestions.value)[index]
  if (!item) return
  const name = item._secondary ? `${item._primary}, ${item._secondary}` : item._primary
  if (isStart) { startPoint.value = name;   startSuggestions.value = []; startActiveIdx.value = -1 }
  else         { destination.value = name;  destSuggestions.value  = []; destActiveIdx.value  = -1 }
}

function clearSuggestions(field) {
  if (field === 'start') { startSuggestions.value = []; startActiveIdx.value = -1 }
  else                   { destSuggestions.value  = []; destActiveIdx.value  = -1 }
}

function onBlur(field) { setTimeout(() => clearSuggestions(field), 150) }

async function geocode(address) {
  try {
    const url = new URL(`${ROUTE_API_BASE}/api/geocode`)
    url.searchParams.set('q', melbourneQuery(address))
    url.searchParams.set('bounded', '1')
    url.searchParams.set('viewbox', `${MELB_SUGGEST_BOUNDS.minLon},${MELB_SUGGEST_BOUNDS.maxLat},${MELB_SUGGEST_BOUNDS.maxLon},${MELB_SUGGEST_BOUNDS.minLat}`)
    const res  = await fetch(url.toString())
    const data = await res.json()
    if (Array.isArray(data) && data.length > 0) {
      const melb = data.find(r => {
        const lat = parseFloat(r.lat); const lon = parseFloat(r.lon)
        return !isNaN(lat) && !isNaN(lon) && isInSuggestBounds(lat, lon)
      })
      const best = melb || data[0]
      return { lat: parseFloat(best.lat), lon: parseFloat(best.lon) }
    }
  } catch {}
  return null
}

function scoreToTone(score) { return score <= 35 ? 'best' : score <= 65 ? 'moderate' : 'avoid' }

function shapeRoute(raw, index, isRec) {
  const tone = isRec ? 'best' : scoreToTone(raw.composite_score ?? 50)
  const safetyDisplay = raw.safety_score != null ? `${Math.round(raw.safety_score * 10) / 10}/10` : `${Math.round(100 - (raw.composite_score ?? 50))}/100`
  const notes = []
  if (raw.scores?.raw_dust   != null) notes.push(raw.scores.raw_dust   < 30 ? '✓ Low dust exposure'   : '⚠ Elevated dust along route')
  if (raw.scores?.raw_pollen != null) notes.push(raw.scores.raw_pollen < 30 ? '✓ Low pollen exposure' : '⚠ Elevated pollen along route')
  return {
    name: ['Route A', 'Route B', 'Route C', 'Route D'][index] ?? `Route ${index + 1}`,
    tag:  { best: 'Best', moderate: 'Moderate', avoid: 'Avoid' }[tone] ?? 'Moderate',
    tone, time: `${Math.round(raw.duration_min ?? 0)} min`,
    distance: raw.distance_m >= 1000 ? `${(raw.distance_m / 1000).toFixed(1)} km` : `${Math.round(raw.distance_m ?? 0)} m`,
    score: safetyDisplay, notes,
    reason: raw.reason ?? null,
  }
}

function buildZones(allRaw, metadata) {
  const dust = []; const pollen = []
  const allCoords = allRaw.flatMap(r => (r?.geometry?.coordinates ?? []).map(([lon, lat]) => ({ lat, lon })))
  if (!allCoords.length) return { dust, pollen }
  const lats = allCoords.map(c => c.lat); const lons = allCoords.map(c => c.lon)
  const minLat = Math.min(...lats) - 0.015; const maxLat = Math.max(...lats) + 0.015
  const minLon = Math.min(...lons) - 0.015; const maxLon = Math.max(...lons) + 0.015
  const rawDust = allRaw[0]?.scores?.raw_dust ?? 0

  // Dust zones: one per suburb that overlaps the route bounding box
  for (const [name, coords] of Object.entries(SUBURB_COORDS)) {
    if (coords.lat >= minLat && coords.lat <= maxLat && coords.lon >= minLon && coords.lon <= maxLon) {
      const intensity = rawDust > 0 ? Math.min(rawDust / 500000, 1) : 0.3
      dust.push({ lat: coords.lat, lon: coords.lon, radius: 180 + intensity * 220, label: name })
    }
  }

  // Pollen zones: always sample points along the route and show tree/pollen zones
  // Use style to indicate whether currently in season or not
  const inSeason  = (metadata?.pollen_season ?? []).length > 0
  const treesFound = (metadata?.trees_found ?? 0) > 0

  const mainRoute = allRaw[0]?.geometry?.coordinates ?? []
  if (mainRoute.length >= 2) {
    // Sample 4 points along the route
    const sampleIdxs = [
      Math.floor(mainRoute.length * 0.2),
      Math.floor(mainRoute.length * 0.4),
      Math.floor(mainRoute.length * 0.6),
      Math.floor(mainRoute.length * 0.8),
    ]
    sampleIdxs.forEach(idx => {
      const pt = mainRoute[Math.min(idx, mainRoute.length - 1)]
      if (!pt) return
      const [lon, lat] = pt
      const rawPollen = allRaw[0]?.scores?.raw_pollen ?? 0
      const radius = inSeason
        ? 200 + Math.min(rawPollen * 1.0, 100)
        : 150
      pollen.push({ lat, lon, radius, inSeason })
    })
  }

  return { dust, pollen }
}

async function findRoutes() {
  routeError.value = null
  routeLoading.value = true
  routeMode.value = 'standard'
  try {
    const [sc, ec] = await Promise.all([geocode(startPoint.value), geocode(destination.value)])
    if (!sc) throw new Error(`Could not locate "${startPoint.value}". Try a more specific address.`)
    if (!ec) throw new Error(`Could not locate "${destination.value}". Try a more specific address.`)

    if (!isInCityOfMelbourne(sc.lat, sc.lon)) {
      throw new Error(`"${startPoint.value}" is outside the City of Melbourne. ClearPath only covers suburbs like Melbourne CBD, Carlton, Docklands, Southbank, and North Melbourne.`)
    }
    if (!isInCityOfMelbourne(ec.lat, ec.lon)) {
      throw new Error(`"${destination.value}" is outside the City of Melbourne. ClearPath only covers suburbs like Melbourne CBD, Carlton, Docklands, Southbank, and North Melbourne.`)
    }

    const params = new URLSearchParams({ start_lat: sc.lat, start_lon: sc.lon, end_lat: ec.lat, end_lon: ec.lon, profile: 'walking' })
    const res  = await fetch(`${ROUTE_API_BASE}/api/safe-route-dual?${params}`)
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error ?? `API error ${res.status}`)
    const data = await res.json()
    if (!data.success) throw new Error(data.error ?? 'Unknown error')

    const recommended    = data.routes?.recommended
    const avoidIrritants = data.routes?.avoid_irritants
    routeComparison.value = data.comparison ?? null

    if (!recommended?.geometry?.coordinates?.length) throw new Error('No route found between these locations.')

    // Check if routes are actually different
    const sameRoute = !avoidIrritants?.geometry?.coordinates?.length ||
      JSON.stringify(avoidIrritants.geometry.coordinates) === JSON.stringify(recommended.geometry.coordinates)

    const allRaw = sameRoute ? [recommended] : [recommended, avoidIrritants]

    routeGeometries.value = allRaw.map(r => r.geometry)
    routes.value          = allRaw.map((r, i) => shapeRoute(r, i, i === 0))
    selectedRouteIndex.value = 0

    const zones = buildZones(allRaw, data.metadata ?? {})
    dustZones.value   = zones.dust
    pollenZones.value = zones.pollen

    const coords = routeGeometries.value[0]?.coordinates ?? []
    const mid    = coords[Math.floor(coords.length / 2)]
    await initBaseMap(mid ? mid[1] : sc.lat, mid ? mid[0] : sc.lon)
    drawZones()
    await drawRoutes(0)
    drawConstructionSitesOnRoute()
  } catch (err) {
    routeError.value = err.message ?? 'Something went wrong. Please try again.'
  } finally {
    routeLoading.value = false
  }
}

// ────────────────────────────────────────────────────────────────
// Lifecycle
// ────────────────────────────────────────────────────────────────
onMounted(async () => {
  const route = useRoute()
  await loadPreferences()
  await selectSuburb(selectedSuburb.value)
  await nextTick()

  // If navigated with ?tab=safespots etc, switch to that tab
  const tabParam = route.query.tab
  if (tabParam && ['dustwatch', 'safespots', 'clearpath'].includes(tabParam)) {
    await switchTab(tabParam)
  } else {
    renderDustMap()
  }
})

onUnmounted(() => {
  if (leafletMap) { leafletMap.remove(); leafletMap = null }
})
</script>

<style scoped>
/* ── Page shell ─────────────────────────────────────────────── */
.assistance-page {
  position: relative;
  width: 100%;
  /* Fill the space below the navbar regardless of how the router mounts this */
  height: calc(100vh - var(--navbar-height, 80px));
  min-height: 500px;
  overflow: hidden;
  background: var(--bg-page, #f5f4f0);
}

.page-layout {
  position: relative;
  width: 100%;
  height: 100%;
}

/* ── Map fills the entire viewport ──────────────────────────── */
.map-container {
  position: absolute;
  inset: 0;
  z-index: 0;
}

/* ── Tab switcher ────────────────────────────────────────────── */
.tab-switcher {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  background: white;
  border-radius: 999px;
  padding: 4px;
  box-shadow: 0 2px 12px rgba(10,40,30,0.1), 0 0 0 1px rgba(10,40,30,0.06);
  gap: 2px;
}

.tab-btn {
  padding: 8px 18px;
  border-radius: 999px;
  border: none;
  background: transparent;
  font-size: 13.5px;
  font-weight: 600;
  color: #6b7a90;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
  white-space: nowrap;
  letter-spacing: 0.01em;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.tab-btn:hover { color: var(--text-dark, #0f172a); background: #f5f4f0; }
.tab-icon { display: inline-flex; align-items: center; opacity: 0.8; }
.tab-btn.active .tab-icon { opacity: 1; }
.tab-btn.active.dustwatch { background: #d97706; color: white; }
.tab-btn.active.safespots { background: #1d4ed8; color: white; }
.tab-btn.active.clearpath { background: var(--primary, #0d6b5e); color: white; }

/* ── Location hint ──────────────────────────────────────────── */
.location-hint {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid rgba(10,40,30,0.08);
  box-shadow: 0 2px 8px rgba(10,40,30,0.08);
  white-space: nowrap;
}

/* ── Left side panel ────────────────────────────────────────── */
.side-panel {
  position: absolute;
  top: 96px;
  left: 20px;
  /* Explicit height so it never relies on bottom: 20px alone */
  height: calc(100% - 96px - 20px);
  width: 380px;
  z-index: 10;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 40px rgba(10,40,30,0.14);
  padding: 0;
  overflow: visible;
  display: flex;
  flex-direction: column;
}

.side-panel::-webkit-scrollbar { width: 4px; }
.side-panel::-webkit-scrollbar-thumb { background: rgba(10,40,30,0.12); border-radius: 999px; }

.side-panel-inner {
  flex: 1;
  overflow-y: auto;
  overflow-x: visible;
  padding: 20px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  border-radius: 20px;
  scrollbar-width: thin;
  scrollbar-color: rgba(10,40,30,0.1) transparent;
}

.side-panel-inner::-webkit-scrollbar { width: 4px; }
.side-panel-inner::-webkit-scrollbar-thumb { background: rgba(10,40,30,0.12); border-radius: 999px; }

.panel-desc {
  font-size: 13px;
  color: #6b7a90;
  line-height: 1.6;
  margin: 0;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(10,40,30,0.06);
}

/* ── DustWatch panel ────────────────────────────────────────── */
.overall-risk-block {
  background: #fdf8f2;
  border-radius: 14px;
  padding: 16px 18px;
  border: 1px solid rgba(217,119,6,0.12);
}

.risk-label-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}

.risk-eyebrow {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #d97706;
  text-transform: uppercase;
}

.risk-site-count {
  font-size: 13px;
  font-weight: 600;
  color: #8a9ab0;
  line-height: 1;
}
.risk-site-count small { display: none; }

.risk-level-text {
  font-size: 22px;
  font-weight: 800;
  margin: 0;
  line-height: 1;
  letter-spacing: -0.02em;
}
.risk-level-text.high     { color: #ea2951; }
.risk-level-text.moderate { color: #d97706; }
.risk-level-text.low      { color: #11915d; }

/* ── Suburb selector ─────────────────────────────────────────── */
.suburb-selector-row {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.suburb-current-btn {
  background: #d97706;
  color: white;
  border: none;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.suburb-current-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(217,119,6,0.3); }

.check-suburb-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: white;
  border: 1.5px solid rgba(10,40,30,0.12);
  border-radius: 999px;
  padding: 7px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #5a6b7a;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease;
}
.check-suburb-btn:hover { border-color: #d97706; color: #d97706; }

.suburb-dropdown {
  background: white;
  border: 1px solid rgba(10,40,30,0.1);
  border-radius: 14px;
  padding: 14px;
  box-shadow: 0 8px 32px rgba(10,40,30,0.1);
}

.suburb-dropdown-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #8a9ab0;
  margin: 0 0 10px;
}

.suburb-pills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.suburb-pill-btn {
  background: #f5f4f0;
  border: 1.5px solid transparent;
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #3d4a63;
  cursor: pointer;
  transition: all 0.2s ease;
}
.suburb-pill-btn:hover  { background: #fdf8f2; border-color: #d97706; color: #d97706; }
.suburb-pill-btn.active { background: #fef3c7; border-color: #d97706; color: #92400e; }

.use-location-btn {
  display: flex;
  align-items: center;
  gap: 7px;
  background: white;
  border: 1.5px solid rgba(10,40,30,0.12);
  border-radius: 999px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #3d4a63;
  cursor: pointer;
  width: fit-content;
  transition: border-color 0.2s, color 0.2s;
}
.use-location-btn:hover:not(:disabled) { border-color: #1d4ed8; color: #1d4ed8; }
.use-location-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.coverage-notice {
  background: #fafafa;
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 12px;
  padding: 14px;
  font-size: 13px;
  color: #5a6b7a;
}
.coverage-notice strong { display: block; color: var(--text-dark); margin-bottom: 4px; }

.sites-label {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #a0aaba;
  margin-top: 2px;
  padding-bottom: 2px;
}

.sites-scroll-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.site-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: #fafafa;
  border: 1.5px solid transparent;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  transition: background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}
.site-row:hover    { background: white; border-color: rgba(10,40,30,0.09); transform: translateX(3px); box-shadow: 0 2px 12px rgba(10,40,30,0.06); }
.site-row.selected { background: white; border-color: #ea2951; box-shadow: 0 4px 16px rgba(234,41,81,0.1); transform: translateX(3px); }

.site-row-info { min-width: 0; flex: 1; display: flex; flex-direction: column; gap: 3px; }
.site-row-info strong {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-dark, #0f172a);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.3;
}
.site-row-info span {
  font-size: 11px;
  color: #9aabb8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.site-risk-chip {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
  flex-shrink: 0;
  letter-spacing: 0.01em;
  display: inline-flex;
  align-items: center;
}
.site-risk-chip.high     { background: #fff0f3; color: #ea2951; }
.site-risk-chip.moderate { background: #fef3c7; color: #d97706; }
.site-risk-chip.low      { background: #ecfdf5; color: #11915d; }

.panel-updated {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 11px;
  color: #a0aaba;
  padding-top: 8px;
  border-top: 1px solid rgba(10,40,30,0.05);
  margin-top: auto;
}
.updated-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #11915d;
  box-shadow: 0 0 0 3px rgba(17,145,93,0.2);
  flex-shrink: 0;
}

/* ── SafeSpots panel ─────────────────────────────────────────── */
.panel-input {
  width: 100%;
  box-sizing: border-box;
  border: 1.5px solid rgba(10,40,30,0.1);
  background: #f7f4f0;
  border-radius: 12px;
  padding: 12px 14px;
  font: inherit;
  font-size: 14px;
  color: var(--text-dark);
  outline: none;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
}
.panel-input:focus { background: white; border-color: rgba(13,107,94,0.3); box-shadow: 0 0 0 3px rgba(13,148,136,0.1); }
.panel-input::placeholder { color: #9aabb8; }
.panel-input.has-icon { padding-left: 38px; }
.panel-input.has-dot  { padding-left: 36px; }

.autocomplete-wrap { position: relative; overflow: visible; }
.input-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #9aabb8; pointer-events: none; }
.route-dot { position: absolute; left: 14px; top: 50%; transform: translateY(-50%); width: 9px; height: 9px; border-radius: 50%; }
.start-dot { background: #0d9488; }
.end-dot   { background: #2b63bd; border-radius: 2px; }

.suggestions-list {
  position: absolute;
  top: calc(100% + 6px);
  left: 0; right: 0;
  background: white;
  border: 1px solid rgba(10,40,30,0.1);
  border-radius: 12px;
  box-shadow: 0 16px 48px rgba(10,40,30,0.14);
  list-style: none;
  margin: 0;
  padding: 5px;
  z-index: 99999;
  max-height: 220px;
  overflow-y: auto;
}
.suggestion-item { display: flex; align-items: center; gap: 10px; padding: 7px 9px; border-radius: 8px; cursor: pointer; transition: background 0.14s; }
.suggestion-item:hover, .suggestion-item.active { background: #e6f7f5; }
.sug-icon-wrap { width: 28px; height: 28px; border-radius: 50%; background: #f0f4f8; flex-shrink: 0; display: flex; align-items: center; justify-content: center; color: #546e8a; }
.suggestion-item.active .sug-icon-wrap, .suggestion-item:hover .sug-icon-wrap { background: #e6f7f5; color: #0d6b5e; }
.sug-text { display: flex; flex-direction: column; gap: 1px; min-width: 0; }
.sug-text strong { font-size: 13px; font-weight: 600; color: var(--text-dark); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sug-text small  { font-size: 11px; color: #8a9ab0; }

.radius-control { display: flex; flex-direction: column; gap: 8px; }
.radius-header { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #3d4a63; }
.radius-value { margin-left: auto; font-size: 18px; font-weight: 800; color: #1d4ed8; }
.radius-value small { font-size: 12px; font-weight: 500; color: #8a9ab0; }
.radius-info-btn { background: none; border: none; cursor: pointer; color: #9aabb8; font-size: 14px; }

.radius-slider {
  width: 100%;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 999px;
  background: linear-gradient(to right, #1d4ed8 0%, #1d4ed8 calc((var(--v, 50) - 5) / 15 * 100%), #e2e8f0 calc((var(--v, 50) - 5) / 15 * 100%), #e2e8f0 100%);
  outline: none;
}
.radius-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #1d4ed8; border: 3px solid white; box-shadow: 0 2px 8px rgba(29,78,216,0.3); cursor: pointer; }

.radius-ticks { display: flex; justify-content: space-between; font-size: 11px; color: #9aabb8; padding: 0 2px; }

.btn-find-spots {
  width: 100%;
  padding: 13px;
  background: #1d4ed8;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, opacity 0.2s;
}
.btn-find-spots:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(29,78,216,0.3); }
.btn-find-spots:disabled { opacity: 0.65; cursor: not-allowed; }

.category-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding-bottom: 4px;
}

.cat-filter-btn {
  border: 1.5px solid rgba(10,40,30,0.1);
  border-radius: 999px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #5a6b7a;
  background: white;
  cursor: pointer;
  transition: all 0.18s ease;
}
.cat-filter-btn:hover { border-color: #1d4ed8; color: #1d4ed8; }
.cat-filter-btn.active { background: #1d4ed8; color: white; border-color: #1d4ed8; }

.no-filter-results {
  font-size: 13px;
  color: #8a9ab0;
  text-align: center;
  padding: 12px 0;
}
.no-filter-results button {
  background: none;
  border: none;
  color: #1d4ed8;
  font-weight: 600;
  cursor: pointer;
  font-size: 13px;
}

.spots-list { display: flex; flex-direction: column; gap: 6px; }
.spot-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #fafafa;
  border: 1.5px solid transparent;
  border-radius: 12px;
  padding: 11px 12px;
  cursor: pointer;
  transition: all 0.22s ease;
}
.spot-row:hover   { background: white; border-color: rgba(10,40,30,0.1); }
.spot-row.selected{ background: white; border-color: #1d4ed8; box-shadow: 0 4px 16px rgba(29,78,216,0.1); }

.spot-rank { width: 22px; height: 22px; border-radius: 50%; background: #f0f4f8; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; color: #5a6b7a; flex-shrink: 0; margin-top: 1px; }
.spot-info { flex: 1; min-width: 0; }
.spot-info strong { display: block; font-size: 13px; font-weight: 700; color: var(--text-dark); }
.spot-info span   { font-size: 11px; color: #8a9ab0; }
.spot-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.spot-tag  { border-radius: 999px; padding: 3px 9px; font-size: 11px; font-weight: 600; line-height: 1.4; }
.spot-tag.tag-good    { background: #ecfdf5; color: #0d6b5e; }
.spot-tag.tag-warn    { background: #fef3c7; color: #92400e; }
.spot-tag.tag-bad     { background: #fff0f3; color: #be123c; }
.spot-tag.tag-neutral { background: #f0f4f8; color: #546e8a; }

.spot-score-col { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
.spot-score { font-size: 20px; font-weight: 800; line-height: 1; }
.spot-score.score-good     { color: #11915d; }
.spot-score.score-moderate { color: #d97706; }
.spot-score.score-poor     { color: #ea2951; }

.spot-clearpath-btn {
  background: #1d4ed8;
  color: white;
  border: none;
  border-radius: 7px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.spot-clearpath-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(29,78,216,0.3); }

/* ── ClearPath panel ─────────────────────────────────────────── */
.btn-find-routes {
  width: 100%;
  padding: 13px;
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.22s ease, box-shadow 0.22s ease, opacity 0.2s;
}
.btn-find-routes:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(13,107,94,0.3); }
.btn-find-routes:disabled { opacity: 0.65; cursor: not-allowed; }

.route-mode-toggle {
  display: flex;
  background: #f0f4f8;
  border-radius: 12px;
  padding: 4px;
  gap: 4px;
  margin-bottom: 12px;
}

.mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 7px 10px;
  border-radius: 9px;
  border: none;
  background: transparent;
  font-size: 12px;
  font-weight: 500;
  color: #6b7a90;
  cursor: pointer;
  transition: all 0.18s ease;
  white-space: nowrap;
}

.mode-btn.active {
  background: white;
  color: #0d6b5e;
  font-weight: 700;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.mode-btn svg { flex-shrink: 0; }
.mode-btn.active svg { stroke: #0d6b5e; }

.same-route-notice {
  font-size: 11px;
  color: #92400e;
  background: #fef3c7;
  border: 1px solid #fde68a;
  border-radius: 8px;
  padding: 8px 12px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.routes-list { display: flex; flex-direction: column; gap: 8px; }

.route-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2px;
}

.route-nav-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7a90;
}

.route-nav-btn {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 1.5px solid #e2e1dc;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #3d4a63;
  transition: all 0.15s;
}

.route-nav-btn:hover:not(:disabled) {
  border-color: #0d9488;
  color: #0d9488;
  background: #f0fdf4;
}

.route-nav-btn:disabled { opacity: 0.35; cursor: default; }
.route-row {
  background: #fafafa;
  border: 1.5px solid transparent;
  border-radius: 14px;
  padding: 13px 14px;
  cursor: pointer;
  transition: all 0.22s ease;
}
.route-row:hover { background: white; border-color: rgba(10,40,30,0.1); transform: translateX(3px); }
.route-row.selected { background: white; border-color: #0d9488; box-shadow: 0 4px 16px rgba(13,148,136,0.12); }
.route-row.best.selected     { border-color: #0d9488; box-shadow: 0 4px 16px rgba(13,148,136,0.12); }
.route-row.moderate.selected { border-color: #d97706; box-shadow: 0 4px 16px rgba(217,119,6,0.12); }
.route-row.avoid.selected    { border-color: #e24d32; box-shadow: 0 4px 16px rgba(226,77,50,0.12); }

.route-row-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; margin-bottom: 4px; }
.route-name-wrap { display: flex; align-items: center; gap: 8px; }
.route-name-wrap strong { font-size: 14px; font-weight: 700; color: var(--text-dark); }
.best-badge { background: #ecfdf5; color: #0d6b5e; font-size: 10px; font-weight: 800; padding: 2px 7px; border-radius: 999px; }

.route-score-big { font-size: 18px; font-weight: 800; }
.route-score-big.best     { color: #0d9488; }
.route-score-big.moderate { color: #d97706; }
.route-score-big.avoid    { color: #e24d32; }

.route-meta { font-size: 12px; color: #8a9ab0; margin-bottom: 7px; }
.route-tags { display: flex; flex-wrap: wrap; gap: 5px; }
.route-tag { font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 999px; }
.route-tag.best     { background: #ecfdf5; color: #0d6b5e; }

.avoidance-card {
  background: #f0fdf4;
  border: 1.5px solid #a7f3d0;
  border-radius: 14px;
  padding: 14px 16px;
}

.avoidance-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 700;
  color: #0d6b5e;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 12px;
}

.avoidance-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.avoidance-stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.avoidance-num {
  font-family: Georgia, serif;
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.avoidance-good { color: #0d6b5e; }
.avoidance-cost { color: #d97706; }

.avoidance-label {
  font-size: 10px;
  color: #6b7a90;
  font-weight: 500;
}

.avoidance-divider {
  width: 1px;
  height: 32px;
  background: #a7f3d0;
  flex-shrink: 0;
}

.avoidance-msg {
  font-size: 11px;
  color: #0d6b5e;
  line-height: 1.55;
  margin: 0;
  font-style: italic;
}

.route-reason {
  font-size: 11px;
  color: #6b7a90;
  line-height: 1.55;
  margin: 5px 0 0;
  font-style: italic;
}

.route-row.selected .route-reason { color: #3d5a6e; }
.route-tag.moderate { background: #fef3c7; color: #92400e; }
.route-tag.avoid    { background: #fff0eb; color: #e24d32; }

/* ── Error / spinner ─────────────────────────────────────────── */
.panel-error {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #fff0eb;
  border: 1.5px solid #e24d32;
  border-radius: 10px;
  padding: 11px 13px;
  font-size: 12px;
  color: #b83215;
  flex: 1;
}
.panel-error button { margin-left: auto; background: none; border: none; cursor: pointer; color: #b83215; flex-shrink: 0; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  display: inline-block;
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* ── Right legend panel ──────────────────────────────────────── */
.legend-panel {
  position: absolute;
  top: 96px;
  right: 20px;
  z-index: 10;
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 14px;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  box-shadow: 0 4px 20px rgba(10,40,30,0.1);
  min-width: 150px;
}

.legend-item { display: flex; align-items: center; gap: 9px; font-size: 13px; font-weight: 600; color: #3d4a63; }
.legend-dot  { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
.legend-dot.high      { background: #ea2951; }
.legend-dot.moderate  { background: #d36c00; }
.legend-dot.low       { background: #11915d; }
.legend-dot.location  { background: #3b82f6; }
.legend-dot.high-risk { background: #ea2951; }
.legend-dot.moderate-risk { background: #d36c00; }
.legend-dot.good      { background: #11915d; }
.legend-dot.pollen    { background: #84cc16; }

.legend-line { display: inline-block; width: 20px; height: 3px; border-radius: 999px; flex-shrink: 0; }
.legend-line.recommended { background: #0d9488; }
.legend-line.alternative { background: transparent; border-top: 2.5px dashed #8a9ab0; }

.legend-weather-divider {
  width: 100%;
  height: 1px;
  background: rgba(10,40,30,0.08);
  margin: 2px 0;
}

.legend-dot.wind {
  background: #0ea5e9;
}

.legend-dot.temp {
  background: #f97316;
}

/* ── Alert card ──────────────────────────────────────────────── */
.alert-card {
  position: absolute;
  bottom: 80px;
  right: 20px;
  z-index: 10;
  background: white;
  border: 1px solid rgba(217,119,6,0.2);
  border-radius: 14px;
  padding: 14px 16px;
  max-width: 240px;
  box-shadow: 0 4px 20px rgba(217,119,6,0.12);
}
.alert-eyebrow { font-size: 10px; font-weight: 800; letter-spacing: 0.07em; color: #d97706; margin: 0 0 4px; }
.alert-card strong { display: block; font-size: 14px; color: var(--text-dark); margin-bottom: 4px; }
.alert-card p { margin: 0; font-size: 12px; color: #5a6b7a; line-height: 1.45; }

/* ── Disclaimer ──────────────────────────────────────────────── */
.disclaimer-note {
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 10;
  background: rgba(255,255,255,0.88);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(10,40,30,0.08);
  border-radius: 10px;
  padding: 8px 12px;
  font-size: 11px;
  color: #5a6b7a;
  max-width: 260px;
}

/* ── Intro modal ─────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(10,20,30,0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-box {
  background: white;
  border-radius: 24px;
  padding: 36px 32px 28px;
  max-width: 520px;
  width: 100%;
  position: relative;
  box-shadow: 0 24px 80px rgba(10,30,20,0.25);
  max-height: 90vh;
  overflow-y: auto;
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #f5f4f0;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  cursor: pointer;
  color: #5a6b7a;
  transition: background 0.2s;
}
.modal-close:hover { background: #e8e6e0; }

.modal-eyebrow { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; color: var(--primary, #0d6b5e); margin: 0 0 8px; }
.modal-box h2  { font-family: var(--font-serif, Georgia, serif); font-size: 28px; font-weight: 500; color: var(--text-dark, #0f172a); margin: 0 0 10px; }
.modal-desc    { font-size: 14px; color: #5a6b7a; line-height: 1.6; margin: 0 0 22px; }

.modal-tools { display: flex; flex-direction: column; gap: 10px; margin-bottom: 18px; }
.modal-tool-card {
  border: 1.5px solid rgba(10,40,30,0.08);
  border-radius: 14px;
  padding: 14px 16px;
  transition: border-color 0.2s;
}
.modal-tool-card:hover { border-color: rgba(10,40,30,0.16); }
.modal-tool-card p { margin: 0; font-size: 13px; color: #5a6b7a; line-height: 1.5; margin-top: 6px; }

.modal-tool-header { display: flex; align-items: center; gap: 9px; }
.modal-tool-header strong { font-size: 15px; font-weight: 700; color: var(--text-dark); }
.tool-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.tool-dot.dustwatch { background: #d97706; }
.tool-dot.safespots { background: #1d4ed8; }
.tool-dot.clearpath { background: #0d9488; }

.tool-badge { font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 999px; margin-left: auto; }
.tool-badge.realtime { background: #fef3c7; color: #92400e; }
.tool-badge.ai       { background: #ede9fe; color: #5b21b6; }

.modal-safeshelf {
  background: linear-gradient(135deg, #f0fdf8, #e8f9f3);
  border: 1.5px solid rgba(13,148,136,0.2);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
}
.modal-safeshelf-eyebrow { font-size: 10px; font-weight: 800; letter-spacing: 0.07em; color: var(--primary, #0d6b5e); margin: 0 0 4px; }
.modal-safeshelf p { font-size: 13px; color: #3d4a63; line-height: 1.5; margin: 0 0 12px; }

.btn-safeshelf {
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 999px;
  padding: 9px 20px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.btn-safeshelf:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(13,107,94,0.3); }

.btn-show-map {
  width: 100%;
  padding: 15px;
  background: var(--primary, #0d6b5e);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
}
.btn-show-map:hover { transform: translateY(-2px); box-shadow: 0 10px 32px rgba(13,107,94,0.32); }

/* ── Transitions ─────────────────────────────────────────────── */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-from,   .modal-fade-leave-to     { opacity: 0; }
.modal-fade-enter-active .modal-box,
.modal-fade-leave-active .modal-box { transition: transform 0.3s var(--ease-out-quart, cubic-bezier(0.16,1,0.3,1)); }
.modal-fade-enter-from .modal-box   { transform: translateY(20px) scale(0.97); }
.modal-fade-leave-to   .modal-box   { transform: translateY(10px) scale(0.98); }

.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
.dropdown-enter-from,   .dropdown-leave-to     { opacity: 0; transform: translateY(-6px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }

/* ── Breeze Mascot ───────────────────────────────────────────── */
.breeze-mascot {
  width: 130px;
  height: auto;
  filter: drop-shadow(0 12px 28px rgba(251,146,60,0.35)) drop-shadow(0 4px 10px rgba(251,146,60,0.2));
}

.breeze-mascot-sm {
  width: 70px;
  height: auto;
  filter: drop-shadow(0 6px 14px rgba(251,146,60,0.3));
}

.breeze-loading-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.breeze-warning-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff0f3;
  border-radius: 12px;
  padding: 10px 14px;
  border: 1px solid rgba(234,41,81,0.15);
  margin-top: 4px;
}

.breeze-warning-text {
  color: #be123c !important;
  font-weight: 700 !important;
  max-width: 180px;
}

.breeze-risk-inline {
  display: flex;
  align-items: center;
  gap: 12px;
  border-radius: 12px;
  padding: 10px 14px;
  border: 1px solid transparent;
}

.breeze-risk-low {
  background: #f0fdf4;
  border-color: rgba(17,145,93,0.15);
}

.breeze-risk-moderate {
  background: #fefce8;
  border-color: rgba(217,119,6,0.15);
}

.breeze-risk-high {
  background: #fff0f3;
  border-color: rgba(234,41,81,0.15);
}

.breeze-risk-msg {
  font-size: 12.5px;
  font-weight: 600;
  line-height: 1.4;
  margin: 0;
  max-width: 190px;
}

.breeze-risk-low    .breeze-risk-msg { color: #0d6b5e; }
.breeze-risk-moderate .breeze-risk-msg { color: #92400e; }
.breeze-risk-high   .breeze-risk-msg { color: #be123c; }

/* ── Score display ───────────────────────────────────────────── */
.spot-score-wrap {
  display: flex;
  align-items: baseline;
  gap: 4px;
  justify-content: flex-end;
}

.spot-score-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.spot-score-label.score-good     { color: #11915d; }
.spot-score-label.score-moderate { color: #d97706; }
.spot-score-label.score-poor     { color: #ea2951; }

.spot-score-bar-bg {
  width: 52px;
  height: 4px;
  background: #f0f4f8;
  border-radius: 999px;
  overflow: hidden;
  margin: 3px 0 6px;
}

.spot-score-bar {
  height: 100%;
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.16,1,0.3,1);
}
.spot-score-bar.score-good     { background: #11915d; }
.spot-score-bar.score-moderate { background: #d97706; }
.spot-score-bar.score-poor     { background: #ea2951; }

/* ── Score legend ────────────────────────────────────────────── */
.score-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 4px 0 2px;
}

.score-legend-label {
  font-size: 10px;
  font-weight: 700;
  color: #a0aaba;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.score-legend-item {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
}
.score-legend-item.good     { background: #ecfdf5; color: #0d6b5e; }
.score-legend-item.moderate { background: #fef3c7; color: #92400e; }
.score-legend-item.poor     { background: #fff0f3; color: #be123c; }

@keyframes breeze-float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-10px); }
}

@keyframes breeze-ring-spin {
  0%   { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -60; }
}

.breeze-float {
  animation: breeze-float 4s ease-in-out infinite;
}

.breeze-ring {
  animation: breeze-ring-spin 4s linear infinite;
}

.breeze-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 32px 0 12px;
  flex: 1;
}

.breeze-caption {
  font-size: 13px;
  font-weight: 600;
  color: #6b7a90;
  text-align: center;
  line-height: 1.5;
  margin: 0;
  max-width: 220px;
}

.modal-breeze-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
}

.modal-breeze-wrap .breeze-mascot {
  width: 100px;
}

/* ── Breathing risk dots ──────────────────────────────────────── */
@keyframes breathe-low {
  0%, 100% { box-shadow: 0 0 0 0px rgba(17,145,93,0.4); }
  50%       { box-shadow: 0 0 0 5px rgba(17,145,93,0); }
}
@keyframes breathe-moderate {
  0%, 100% { box-shadow: 0 0 0 0px rgba(217,119,6,0.45); }
  50%       { box-shadow: 0 0 0 6px rgba(217,119,6,0); }
}
@keyframes breathe-high {
  0%, 100% { box-shadow: 0 0 0 0px rgba(234,41,81,0.5); }
  50%       { box-shadow: 0 0 0 7px rgba(234,41,81,0); }
}

.risk-breath-dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  margin-right: 5px;
  flex-shrink: 0;
  vertical-align: middle;
}

.risk-breath-dot.high {
  background: #ea2951;
  animation: breathe-high 1s ease-in-out infinite;
}

.risk-breath-dot.moderate {
  background: #d97706;
  animation: breathe-moderate 2.2s ease-in-out infinite;
}

.risk-breath-dot.low {
  background: #11915d;
  animation: breathe-low 3.8s ease-in-out infinite;
}

/* ── Responsive ──────────────────────────────────────────────── */
@media (max-width: 960px) {
  .side-panel { position: absolute; width: 100%; top: auto; bottom: 0; left: 0; right: 0; border-radius: 20px 20px 0 0; max-height: 55vh; }
  .legend-panel { display: none; }
  .alert-card   { right: 10px; bottom: calc(55vh + 10px); max-width: 200px; }
  .disclaimer-note { display: none; }
}

@media (max-width: 520px) {
  .tab-btn { padding: 8px 14px; font-size: 13px; }
  .modal-box { padding: 28px 22px 22px; }
  .modal-box h2 { font-size: 24px; }
}
</style>

<!-- Global Leaflet overrides (unscoped) -->
<style>
.zone-tip {
  background: white !important;
  border: 1px solid rgba(10,40,30,0.12) !important;
  border-radius: 8px !important;
  font-size: 12px !important;
  color: #334155 !important;
  box-shadow: 0 8px 24px rgba(10,40,30,0.12) !important;
  padding: 5px 10px !important;
}
.zone-tip::before { display: none !important; }
.map-popup { font-size: 13px; line-height: 1.5; color: #334155; }
.map-popup strong { display: block; color: #0f172a; margin-bottom: 2px; }
.leaflet-popup-content-wrapper { border-radius: 12px !important; box-shadow: 0 8px 32px rgba(10,40,30,0.16) !important; }
.leaflet-popup-tip-container { display: none !important; }
</style>