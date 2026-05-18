<template>
  <div class="learn-page">

    <!-- ── Hero ──────────────────────────────────────────────── -->
    <section class="learn-hero">
      <div class="hero-inner">
        <!-- Left: text -->
        <div class="hero-text">
          <div class="hero-eyebrow">
            <svg width="14" height="14" viewBox="0 0 32 32" fill="none">
              <path d="M16 4 C16 4 14 6 14 10 L14 22 C14 22 10 24 8 22 C6 20 6 16 8 14 C10 12 12 14 12 14 L12 10 C12 6 14 4 16 4 Z" fill="currentColor" opacity="0.85"/>
              <path d="M16 4 C16 4 18 6 18 10 L18 22 C18 22 22 24 24 22 C26 20 26 16 24 14 C22 12 20 14 20 14 L20 10 C20 6 18 4 16 4 Z" fill="currentColor" opacity="0.65"/>
              <rect x="15" y="4" width="2" height="18" rx="1" fill="currentColor"/>
            </svg>
            Learn with BRTHEZ
          </div>
          <h1 class="hero-title">
            Understanding asthma<br/>
            <em>starts here.</em>
          </h1>
          <p class="hero-sub">Built from trusted Australian and global sources — written in plain English so parents and children can learn together.</p>
        </div>

        <!-- Right: Breeze -->
        <div class="hero-breeze-wrap" :class="{ 'breeze-clicked': breezeClicked }" @click="onHeroBreezeClick" role="button" tabindex="0" aria-label="Say hi to Breeze">
        <svg class="learn-breeze breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#0d9488" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring-learn"/>
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
          <p class="hero-breeze-label">{{ breezeMsg }}</p>
        </div>
      </div>
    </section>

    <!-- ── Section nav ───────────────────────────────────────── -->
    <nav class="section-nav" role="tablist">
      <button
        v-for="s in sections" :key="s.id"
        class="sec-tab"
        :class="{ active: activeSection === s.id }"
        role="tab"
        :aria-selected="activeSection === s.id"
        @click="activeSection = s.id"
      >{{ s.label }}</button>
    </nav>

    <!-- ══════════════════════════════════════════════════════════
         SECTION 1: BY THE NUMBERS
    ═══════════════════════════════════════════════════════════════ -->
    <div v-if="activeSection === 'analytics'" class="section-wrap">
      <div class="sec-header">
        <p class="sec-eyebrow">* By the numbers</p>
        <h2 class="sec-title">Asthma in Australia — the real picture</h2>
        <p class="sec-desc">These are not just statistics. Each number represents a family navigating the same worries you face. Hover any stat card to see how it connects to the charts below.</p>
      </div>

      <!-- Stat cards -->
      <div class="stat-grid">
        <div
          v-for="s in statCards" :key="s.id"
          class="stat-card"
          :class="{ hovered: hovStat === s.id }"
          :style="{ '--accent': s.color }"
          @mouseenter="hovStat = s.id"
          @mouseleave="hovStat = null"
        >
          <div class="stat-bubble"/>
          <div class="stat-num">{{ s.n }}</div>
          <div class="stat-label">{{ s.label }}</div>
          <div class="stat-sub">{{ s.sub }}</div>
          <transition name="fade">
            <div v-if="hovStat === s.id" class="stat-cross">
              <span class="stat-cross-dot"/>
              {{ s.cross }}
            </div>
          </transition>
          <div class="stat-src">{{ s.src }}</div>
        </div>
      </div>

      <!-- Charts row 1 -->
      <div class="chart-row">
        <!-- Age bar chart -->
        <div class="chart-card" :class="{ connected: hovStat==='prev' || hovStat==='children' }" id="age-chart">
          <div class="chart-card-header">
            <div>
              <p class="chart-eyebrow">Asthma prevalence by age</p>
              <h3 class="chart-title">Who is most affected?</h3>
            </div>
            <span v-if="hovStat==='prev' || hovStat==='children'" class="connected-badge">Connected</span>
          </div>
          <div class="bar-chart-wrap">
            <div
              v-for="d in ageData" :key="d.age"
              class="bar-col"
              @mouseenter="hovBar = d.age"
              @mouseleave="hovBar = null"
            >
              <transition name="tooltip-fade">
                <div v-if="hovBar === d.age" class="bar-tooltip">{{ d.note }}</div>
              </transition>
              <div
                class="bar-fill"
                :class="{ target: d.age==='5-9' || d.age==='10-14', barHov: hovBar===d.age }"
                :style="{ height: (d.pct/15*100) + 'px' }"
              />
              <div class="bar-label" :class="{ 'target-lbl': d.age==='5-9' || d.age==='10-14' }">{{ d.age }}</div>
            </div>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><span class="leg-dot target-col"></span>BRTHEZ target age (5-14)</span>
            <span class="legend-item"><span class="leg-dot other-col"></span>Other age groups</span>
          </div>
          <p class="chart-src">Source: AIHW 2023</p>
        </div>

        <!-- Trigger breakdown -->
        <div class="chart-card" :class="{ connected: hovStat==='hosp' || hovStat==='trigger' }">
          <div class="chart-card-header">
            <div>
              <p class="chart-eyebrow">What triggers episodes?</p>
              <h3 class="chart-title">Cause breakdown</h3>
            </div>
            <span v-if="hovStat==='hosp' || hovStat==='trigger'" class="connected-badge amber">Connected</span>
          </div>
          <div class="trigger-bars">
            <div
              v-for="t in triggerData" :key="t.label"
              class="trigger-row"
              @mouseenter="hovTrigger = t.label"
              @mouseleave="hovTrigger = null"
            >
              <div class="trigger-labels">
                <span class="trigger-name" :class="{ active: hovTrigger===t.label }">{{ t.label }}</span>
                <span class="trigger-pct" :style="{ color: t.color }">{{ t.pct }}%</span>
              </div>
              <div class="trigger-track">
                <div class="trigger-fill" :style="{ width: t.pct+'%', background: t.color, opacity: hovTrigger===t.label ? 1 : 0.7 }"/>
              </div>
            </div>
          </div>
          <p class="chart-src">Source: AIHW / Asthma Australia</p>
        </div>
      </div>

      <!-- Charts row 2 -->
      <div class="chart-row chart-row--wide">
        <!-- Seasonal bar chart -->
        <div class="chart-card" id="season-chart" :class="{ 'connected-red': hovStat==='hosp' || hovStat==='visits' }">
          <div class="chart-card-header">
            <div>
              <p class="chart-eyebrow">Melbourne hospital visits by month</p>
              <h3 class="chart-title">When is risk highest?</h3>
            </div>
            <span v-if="hovStat==='hosp' || hovStat==='visits'" class="connected-badge red">Connected</span>
          </div>
          <div class="season-bars">
            <div
              v-for="d in seasonData" :key="d.m"
              class="season-col"
              @mouseenter="hovBar = d.m"
              @mouseleave="hovBar = null"
            >
              <transition name="tooltip-fade">
                <div v-if="hovBar === d.m" class="bar-tooltip season-tip">{{ d.v }}</div>
              </transition>
              <div
                class="season-bar"
                :class="{ peak: d.v >= 80, barHov: hovBar === d.m }"
                :style="{ height: (d.v/95*88) + 'px' }"
              />
              <div class="season-label" :class="{ 'peak-lbl': d.v >= 80 }">{{ d.m }}</div>
            </div>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><span class="leg-dot peak-col"></span>Peak season (Sep-Nov)</span>
            <span class="legend-item"><span class="leg-dot other-col"></span>Other months</span>
          </div>
          <p class="chart-src">Source: AIHW 2023 / Melbourne Health</p>
        </div>

        <!-- Melbourne context -->
        <div class="melbourne-card">
          <p class="melb-eyebrow">Melbourne context</p>
          <h3 class="melb-title">Why Melbourne is a high-risk city for asthma</h3>
          <div v-for="m in melbContext" :key="m.label" class="melb-row" :style="{ '--mc': m.color }">
            <div class="melb-label">{{ m.label }}</div>
            <div class="melb-val">{{ m.val }}</div>
            <div class="melb-src">{{ m.src }}</div>
          </div>
        </div>
      </div>

      <!-- Cross-connection hint -->
      <div class="cross-hint">
        <span class="cross-dot"/>
        <span><strong>Cross-connections:</strong> Hover any stat card above to highlight the chart it relates to. Cards glow and charts show a coloured border when connected.</span>
      </div>

      <!-- Sources -->
      <div class="sources-row">
        <span class="sources-label">Sources:</span>
        <span v-for="s in sources" :key="s" class="source-chip">{{ s }}</span>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         SECTION 2: UNDERSTAND ASTHMA
    ═══════════════════════════════════════════════════════════════ -->
    <div v-if="activeSection === 'understand'" class="section-wrap">
      <p class="sec-eyebrow">* Understand asthma</p>
      <h2 class="sec-title">What is asthma?</h2>

      <div class="breeze-inline-wrap">
        <svg class="learn-breeze breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring-learn"/>
              <ellipse cx="60" cy="74" rx="36" ry="40" fill="#fb923c"/>
              <ellipse cx="60" cy="80" rx="25" ry="27" fill="#fed7aa"/>
              <circle cx="51" cy="66" r="6.5" fill="white"/><circle cx="69" cy="66" r="6.5" fill="white"/>
              <circle cx="53" cy="64" r="3.8" fill="#1c1917"/><circle cx="71" cy="64" r="3.8" fill="#1c1917"/>
              <circle cx="54.5" cy="62.5" r="1.4" fill="white"/><circle cx="72.5" cy="62.5" r="1.4" fill="white"/>
              <ellipse cx="60" cy="84" rx="4.5" ry="3" fill="#c2410c" opacity=".45"/>
              <ellipse cx="56" cy="35" rx="5.5" ry="12" transform="rotate(-18 56 35)" fill="#16a34a" opacity=".75"/>
              <ellipse cx="65" cy="34" rx="5.5" ry="12" transform="rotate(18 65 34)" fill="#22c55e" opacity=".8"/>
            </svg>
        <p class="breeze-inline-msg">Asthma makes it harder to breathe — but with the right knowledge, you can manage it really well.</p>
      </div>

      <div class="understand-top">
        <div class="understand-text">
          <p>Asthma makes the airways inside your lungs get swollen and narrow. When that happens, air has to squeeze through a smaller space — which causes the tight feeling in your chest, the wheezing sound, and the coughing.</p>
          <p>Think of it like trying to breathe through a straw instead of a pipe. The pipe is still there — it is just narrower than it should be. With the right management, you can keep that pipe as wide and clear as possible.</p>
          <p class="src-note">Sources: Asthma Australia, GINA 2024, AIHW</p>
        </div>

        <!-- Airway diagram -->
        <div class="airway-card" :class="airwayOpen ? 'airway-open' : 'airway-closed'">
          <p class="airway-label">{{ airwayOpen ? 'Normal airway' : 'During asthma' }}</p>
          <div class="airway-tube">
            <div class="airway-inner" :class="airwayOpen ? 'airway-wide' : 'airway-narrow'"/>
          </div>
          <div class="airway-btns">
            <button class="airway-btn" :class="{ 'airway-btn--active-open': airwayOpen }" @click="airwayOpen = true">Open</button>
            <button class="airway-btn" :class="{ 'airway-btn--active-closed': !airwayOpen }" @click="airwayOpen = false">Asthma</button>
          </div>
          <p class="airway-desc">{{ airwayOpen ? 'Air flows freely. No symptoms.' : 'Mucus builds up. Breathing takes effort.' }}</p>
        </div>
      </div>

      <!-- Triggers -->
      <div class="subsec-gap">
        <p class="sec-eyebrow">* What triggers asthma</p>
        <h2 class="sec-title">Common triggers — tap to learn more</h2>
        <div class="trigger-grid">
          <div
            v-for="t in triggers" :key="t.id"
            class="trigger-card"
            :class="{ 'trigger-card--active': activeTrigger === t.id }"
            :style="{ '--tc': t.color }"
            @click="activeTrigger = activeTrigger===t.id ? null : t.id"
          >
            <div class="trigger-icon-wrap">
              <span class="trigger-icon-lbl">{{ t.icon }}</span>
            </div>
            <div class="trigger-card-name">{{ t.label }}</div>
            <transition name="expand">
              <div v-if="activeTrigger === t.id" class="trigger-expand">
                <p>{{ t.desc }}</p>
                <span class="trigger-expand-src">{{ t.source }}</span>
              </div>
            </transition>
          </div>
        </div>
      </div>

      <!-- Symptoms -->
      <div class="subsec-gap">
        <p class="sec-eyebrow">* Symptoms to know</p>
        <h2 class="sec-title">How do you know it is happening?</h2>
        <div class="symptom-grid">
          <div
            v-for="s in symptoms" :key="s.id"
            class="symptom-card"
            :class="{ 'symptom-card--active': activeSymptom === s.id }"
            :style="{ '--sc': s.color }"
            @click="activeSymptom = activeSymptom===s.id ? null : s.id"
          >
            <div class="symptom-name">{{ s.label }}</div>
            <div class="symptom-sub">{{ s.sub }}</div>
            <transition name="expand">
              <div v-if="activeSymptom === s.id" class="symptom-stat">{{ s.stat }}</div>
            </transition>
          </div>
        </div>
      </div>

      <!-- FAQ -->
      <div class="subsec-gap">
        <p class="sec-eyebrow">* FAQ</p>
        <h2 class="sec-title">Questions parents ask most</h2>
        <div class="faq-list">
          <div
            v-for="f in faqs" :key="f.q"
            class="faq-item"
            :class="{ 'faq-item--open': activeFaq === f.q }"
            @click="activeFaq = activeFaq===f.q ? null : f.q"
          >
            <div class="faq-row">
              <span class="faq-q">{{ f.q }}</span>
              <span class="faq-toggle">{{ activeFaq===f.q ? '−' : '+' }}</span>
            </div>
            <transition name="expand">
              <div v-if="activeFaq === f.q" class="faq-body">
                <p>{{ f.a }}</p>
                <span class="faq-src">Source: {{ f.src }}</span>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         SECTION 3: INHALER GUIDE
    ═══════════════════════════════════════════════════════════════ -->
    <div v-if="activeSection === 'inhaler'" class="section-wrap">
      <p class="sec-eyebrow">* Inhaler guide</p>
      <h2 class="sec-title">Using a reliever inhaler correctly</h2>
      <p class="sec-desc">Correct technique means up to 3× more medicine reaches the lungs. Many children use their inhaler incorrectly — and parents often do not realise. Walk through these steps together.</p>

      <div class="inhaler-layout">
        <!-- Step list -->
        <div class="inhaler-steps">
          <div
            v-for="(s, i) in inhalerSteps" :key="s.n"
            class="inhaler-step"
            :class="{ 'inhaler-step--active': inhalerStep === i }"
            @click="inhalerStep = i"
          >
            <div class="step-num">{{ s.n }}</div>
            <span class="step-name">{{ s.title }}</span>
          </div>
        </div>

        <!-- Step detail -->
        <div class="inhaler-detail">
          <div class="inhaler-detail-header">
            <div class="step-num-big">{{ inhalerSteps[inhalerStep].n }}</div>
            <h3 class="inhaler-step-title">{{ inhalerSteps[inhalerStep].title }}</h3>
          </div>
          <div class="inhaler-visual">
            <!-- Inhaler illustration -->
            <svg width="80" height="100" viewBox="0 0 80 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <!-- Spacer body -->
              <rect x="8" y="35" width="64" height="28" rx="8" fill="#e0e7ff" stroke="#0d9488" stroke-width="1.5"/>
              <!-- Inhaler canister -->
              <rect x="28" y="18" width="24" height="26" rx="6" fill="#0d9488" opacity="0.85"/>
              <rect x="34" y="12" width="12" height="8" rx="3" fill="#0d6b5e"/>
              <!-- Mouthpiece -->
              <rect x="52" y="41" width="18" height="16" rx="5" fill="#a7f3d0" stroke="#0d9488" stroke-width="1"/>
              <!-- Step number badge -->
              <circle cx="18" cy="22" r="12" fill="#0d9488"/>
              <text x="18" y="27" text-anchor="middle" font-size="12" font-weight="700" fill="white" font-family="Georgia,serif">{{ inhalerSteps[inhalerStep].n }}</text>
            </svg>
            <span class="inhaler-visual-name">{{ inhalerSteps[inhalerStep].title }}</span>
          </div>
          <p class="inhaler-desc">{{ inhalerSteps[inhalerStep].desc }}</p>
          <div class="inhaler-note">
            <strong>Note: </strong>{{ inhalerSteps[inhalerStep].note }}
          </div>
          <div class="inhaler-nav">
            <button class="inhaler-prev" :disabled="inhalerStep === 0" @click="inhalerStep = Math.max(0, inhalerStep-1)">Previous</button>
            <button class="inhaler-next" :disabled="inhalerStep === inhalerSteps.length-1" @click="inhalerStep = Math.min(inhalerSteps.length-1, inhalerStep+1)">Next step</button>
          </div>
        </div>
      </div>

      <!-- Videos -->
      <div class="video-section">
        <p class="sec-eyebrow">* Watch it in action</p>
        <h3 class="sec-title" style="font-size:22px">Trusted video guides</h3>
        <p class="sec-desc">Watch the correct technique from Asthma Australia and the National Asthma Council. Watching once makes a real difference to how well the medicine works.</p>
        <div class="video-grid">
          <div v-for="v in videos" :key="v.id" class="video-card">
            <iframe :src="'https://www.youtube.com/embed/'+v.id" :title="v.title" width="100%" height="200" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen/>
            <div class="video-meta">
              <div class="video-title">{{ v.title }}</div>
              <div class="video-org">{{ v.org }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════════════
         SECTION 4: NEXT STEPS
    ═══════════════════════════════════════════════════════════════ -->
    <div v-if="activeSection === 'extend'" class="section-wrap">
      <p class="sec-eyebrow">* Next steps</p>
      <h2 class="sec-title">Knowledge is the first step.<br/>Action is what changes things.</h2>
      <p class="sec-desc" style="max-width:580px;margin-bottom:40px">Now that you understand asthma better, here is how to put that knowledge to work — starting today.</p>

      <!-- Action plan card -->
      <div class="action-plan-card">
        <div class="action-plan-text">
          <p class="sec-eyebrow" style="color:#7ae0d4">* Most important step</p>
          <h3 class="action-plan-title">Get your child's Asthma Action Plan</h3>
          <p class="action-plan-desc">A written plan from your doctor that tells you exactly what to do when symptoms appear. Every child with asthma needs one — at home, at school, and at any regular activity.</p>
          <p class="action-plan-src">Asthma Australia / Royal Melbourne Hospital</p>
        </div>
        <div class="action-plan-icon">
          <svg width="44" height="44" viewBox="0 0 32 32" fill="none">
            <path d="M16 4 L26 8 L26 18 C26 23 16 28 16 28 C16 28 6 23 6 18 L6 8 Z" fill="#7ae0d4" opacity="0.85"/>
            <path d="M11 16 L14 19 L21 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>

      <!-- Tool cards -->
      <h3 class="tools-heading">Use BRTHEZ every day</h3>
      <p class="sec-desc" style="margin-bottom:20px">Each tool targets a specific risk. Used together, they give you a complete picture of what your child is breathing — indoors and out.</p>
      <div class="tools-grid">
        <router-link
          v-for="t in tools" :key="t.title"
          :to="t.to"
          class="tool-card"
          :style="{ '--ta': t.accent, '--tb': t.bg, '--tbr': t.border }"
        >
          <div class="tool-icon-wrap" v-html="t.icon"/>
          <div class="tool-body">
            <div class="tool-title">{{ t.title }}</div>
            <div class="tool-desc">{{ t.desc }}</div>
            <div class="tool-cta">{{ t.cta }} →</div>
          </div>
        </router-link>
      </div>

      <!-- Closing -->
      <div class="breeze-closing-wrap" aria-hidden="true">
        <svg class="learn-breeze breeze-float" viewBox="0 0 120 140" xmlns="http://www.w3.org/2000/svg">
              <ellipse cx="35" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <ellipse cx="85" cy="68" rx="15" ry="18" fill="#f97316" opacity=".5"/>
              <circle cx="60" cy="72" r="46" fill="none" stroke="#0d9488" stroke-width="2" stroke-dasharray="5 4" opacity=".4" class="breeze-ring-learn"/>
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
      </div>

      <div class="closing-card">
        <h3>You are doing something important.</h3>
        <p>Most asthma episodes are preventable with the right information and tools. By being here and learning, you are already ahead.</p>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const activeSection = ref('analytics')
const airwayOpen    = ref(true)
const activeTrigger = ref(null)
const activeSymptom = ref(null)
const activeFaq     = ref(null)
const inhalerStep   = ref(0)
const hovStat       = ref(null)
const breezeClicked = ref(false)
const breezeMsgIdx  = ref(0)
const breezeMsgs = [
  "Hi! I'm Breeze. Let's learn together! 👋",
  "Did you know? 1 in 9 Australians have asthma! 😮",
  "Correct inhaler technique matters more than you think! 💨",
  "Most asthma episodes are preventable — you're in the right place! 🌿",
  "Check the charts below — hover them to see connections! ✨",
]

const breezeMsg = computed(() => breezeMsgs[breezeMsgIdx.value])

function onHeroBreezeClick() {
  breezeClicked.value = true
  breezeMsgIdx.value = (breezeMsgIdx.value + 1) % breezeMsgs.length
  setTimeout(() => { breezeClicked.value = false }, 500)
}
const hovBar        = ref(null)
const hovTrigger    = ref(null)

const sections = [
  { id: 'analytics', label: 'By the numbers' },
  { id: 'understand', label: 'Understand asthma' },
  { id: 'inhaler',    label: 'Inhaler guide' },
  { id: 'extend',     label: 'Next steps' },
]

// ── By the numbers ───────────────────────────────────────────
const statCards = [
  { id:'prev',     n:'1 in 9',  label:'Australians',      sub:'have asthma',                   src:'AIHW 2023',        color:'#0d6b5e', cross:'Shown in age chart below' },
  { id:'children', n:'386K',    label:'children',          sub:'in Victoria under 15',           src:'Lung Foundation',  color:'#fb923c', cross:'See age 5-14 bars' },
  { id:'hosp',     n:'42%',     label:'hospitalisations',  sub:'from preventable triggers',      src:'AIHW / EPA Vic',   color:'#e11d48', cross:'See trigger breakdown' },
  { id:'visits',   n:'26.5K',   label:'hospital visits',   sub:'Melbourne per year',             src:'AIHW 2023',        color:'#dc2626', cross:'See seasonal pattern' },
  { id:'trigger',  n:'3 in 4',  label:'episodes',          sub:'triggered by environment',       src:'AAH / GINA 2024',  color:'#0d6b5e', cross:'See trigger chart' },
  { id:'inhaler',  n:'80%',     label:'users',             sub:'incorrect inhaler technique',    src:'NAS',              color:'#0ea5e9', cross:'See inhaler guide section' },
]

const ageData = [
  { age:'0-4',   pct:8,  note:'Diagnosis often begins here. Symptoms frequently mistaken for repeated colds.' },
  { age:'5-9',   pct:15, note:'Peak prevalence in children. School environments increase exposure to triggers.' },
  { age:'10-14', pct:13, note:'Many children in this group are the BRTHEZ target audience.' },
  { age:'15-24', pct:9,  note:'Symptoms may reduce but the condition rarely disappears entirely.' },
  { age:'25-34', pct:8,  note:'Workplace exposures become a new trigger factor.' },
  { age:'35-44', pct:10, note:'Recurrence common in adults who had childhood asthma.' },
  { age:'45-54', pct:11, note:'Comorbidities such as allergic rhinitis increase severity.' },
  { age:'55+',   pct:12, note:'Underdiagnosed in older adults — often attributed to age or fitness.' },
]

const triggerData = [
  { label:'Respiratory infection',   pct:45, color:'#e11d48' },
  { label:'Air quality / pollution', pct:22, color:'#fb923c' },
  { label:'Allergens (pollen/dust)', pct:16, color:'#7c3aed' },
  { label:'Exercise',                pct:9,  color:'#0ea5e9' },
  { label:'Other / unknown',         pct:8,  color:'#94a3b8' },
]

const seasonData = [
  { m:'Jan',v:42},{m:'Feb',v:38},{m:'Mar',v:55},
  { m:'Apr',v:61},{m:'May',v:58},{m:'Jun',v:52},
  { m:'Jul',v:49},{m:'Aug',v:63},{m:'Sep',v:88},
  { m:'Oct',v:95},{m:'Nov',v:82},{m:'Dec',v:51},
]

const melbContext = [
  { label:'Thunderstorm asthma', val:'3+ major events last decade',   src:'EPA Victoria',      color:'#c4b5fd' },
  { label:'Active construction', val:'26,500+ permits city-wide',     src:'City of Melbourne', color:'#fdba74' },
  { label:'Ryegrass pollen',     val:'Among highest counts globally', src:'Melbourne Pollen',  color:'#86efac' },
]

const sources = ['AIHW 2023','Lung Foundation Australia','EPA Victoria','City of Melbourne','AAH','GINA 2024','NAS','Melbourne Pollen','Better Health Channel VIC']

// ── Understand asthma ────────────────────────────────────────
const triggers = [
  { id:'dust',     icon:'T1', label:'Dust & Pollen',       color:'#fb923c', desc:'Tiny particles that float in the air and irritate the airways. Pollen season in Melbourne peaks in spring — a common time for flare-ups.',                                                          source:'AAH / EPA Victoria' },
  { id:'const',   icon:'T2', label:'Construction dust',    color:'#e11d48', desc:'Fine silica dust from building sites is particularly harsh on young lungs. Melbourne has over 26,000 active permits. This is why DustWatch exists.',                                                 source:'AAH / City of Melbourne' },
  { id:'cold',    icon:'T3', label:'Cold & dry air',       color:'#0ea5e9', desc:'Sudden temperature drops can cause airways to tighten quickly. Breathing through your nose (not mouth) helps warm the air before it reaches the lungs.',                                            source:'GINA 2024' },
  { id:'exercise',icon:'T4', label:'Exercise',             color:'#0d9488', desc:'Running in cold or polluted air can trigger symptoms. But exercise is still important — the right preparation (reliever before sport) makes it safe.',                                              source:'GINA 2024 / Better Health VIC' },
  { id:'pets',    icon:'T5', label:'Pet hair & mould',     color:'#7c3aed', desc:'Common indoor triggers many families overlook. Pet dander stays airborne for hours, and mould spores thrive in bathrooms and under carpet.',                                                       source:'Asthma Australia' },
  { id:'smoke',   icon:'T6', label:'Smoke',                color:'#78350f', desc:'Cigarette smoke and bushfire smoke are two of the strongest known asthma triggers. Even brief exposure can cause a significant flare-up.',                                                          source:'AIHW / GINA 2024' },
  { id:'chemical',icon:'T7', label:'Cleaning products',    color:'#c2410c', desc:'Many everyday sprays and detergents contain VOCs and fragrances that directly irritate airways. This is exactly what SafeShelf screens for.',                                                      source:'NPS MedicineWise / NAS' },
  { id:'illness', icon:'T8', label:'Colds & flu',          color:'#475569', desc:'Viral respiratory infections are the most common trigger for asthma flare-ups in children. Flu vaccination is strongly recommended.',                                                              source:'RMH / Better Health VIC' },
]

const symptoms = [
  { id:'cough',  label:'Coughing',             sub:'Especially at night or early morning — often the first sign parents miss',           color:'#e11d48', stat:'Night-time cough is the most underdiagnosed asthma symptom in children (RMH)' },
  { id:'wheeze', label:'Wheezing',             sub:'A whistling or squeaky sound when breathing out',                                    color:'#fb923c', stat:'Heard in around 70% of asthma episodes (Asthma Australia)' },
  { id:'tight',  label:'Chest tightness',      sub:'A heavy squeezing feeling — kids often describe it as something sitting on my chest',color:'#0d9488', stat:'Common in children over 8 who can better describe their symptoms (GINA 2024)' },
  { id:'breath', label:'Shortness of breath',  sub:'Feeling like you cannot get enough air, even at rest',                              color:'#0ea5e9', stat:'Occurs in moderate to severe episodes — always seek medical attention if this is sudden (Better Health VIC)' },
]

const faqs = [
  { q:'Can asthma be cured?',                           a:'No — but it can be very well controlled. Most children with asthma live completely normal, active lives with the right management plan. The goal is zero symptoms, not just fewer symptoms.', src:'GINA 2024' },
  { q:'Is asthma contagious?',                          a:'Not at all. You cannot catch asthma from someone else. It develops from a combination of genetic factors and environmental exposures — particularly in early childhood.', src:'Asthma Australia' },
  { q:'Can kids outgrow asthma?',                       a:'Some do — AIHW data shows symptoms often reduce during teenage years. However, the tendency can return in adulthood, particularly if exposed to smoking or occupational dust. It is never truly gone, just quieter.', src:'AIHW / Lung Foundation Australia' },
  { q:'Is it safe to exercise with asthma?',            a:'Yes — with preparation. Many elite athletes have asthma. The key is taking a reliever inhaler 10–15 minutes before exercise if prescribed, knowing your triggers, and warming up gradually.', src:'GINA 2024 / Better Health VIC' },
  { q:'Reliever vs preventer — what is the difference?',a:'A reliever (usually blue) opens airways fast during an episode. A preventer (usually brown or purple) is taken daily to reduce underlying inflammation so flare-ups happen less often. Both serve different purposes.', src:'NPS MedicineWise / NAS' },
  { q:'What is an Asthma Action Plan?',                 a:'A written plan from your doctor that tells you exactly what to do at each stage of a flare-up — green, yellow, and red zones. Every child with asthma should have one and carry it to school.', src:'Asthma Australia / RMH' },
  { q:'How common is asthma in Melbourne?',             a:'Australia has one of the highest asthma rates in the world. AIHW data shows 1 in 9 Australians have asthma — around 2.8 million people. In children it is the most common chronic condition.', src:'AIHW 2023' },
]

// ── Inhaler guide ────────────────────────────────────────────
const inhalerSteps = [
  { n:1, title:'Shake well',           desc:'Shake the inhaler firmly for 5 seconds. This mixes the medicine properly.',                                                               note:'Always shake before each puff, even if you just used it.' },
  { n:2, title:'Attach spacer',        desc:'Connect the inhaler to the spacer. Children under 12 should always use a spacer — it makes sure more medicine reaches the lungs.',       note:'Children under 12: spacer is essential, not optional (NAS)' },
  { n:3, title:'Breathe out',          desc:'Breathe out gently and fully — away from the spacer mouthpiece. Empty your lungs first so the medicine can get in.',                     note:'Breathe away from the device so you do not blow into it.' },
  { n:4, title:'Seal and press',       desc:'Put the spacer mouthpiece in your mouth, seal your lips around it, and press the inhaler once while breathing in slowly and steadily.',   note:'Breathe in slowly — not a big fast gasp. Slow and steady.' },
  { n:5, title:'Hold for 10 seconds', desc:'Hold your breath for 10 seconds, or as long as comfortably possible. This lets the medicine settle deep in the airways.',                note:'Young children: count to 10 together to make it easier.' },
  { n:6, title:'Breathe out slowly',  desc:'Breathe out slowly and gently through your mouth. No need to rush.',                                                                      note:'Stay calm and relaxed throughout.' },
  { n:7, title:'Wait, then repeat',   desc:'If a second puff is prescribed, wait 30 seconds before repeating from step 3. Never double-puff immediately.',                            note:'30 second wait is important — do not skip it.' },
]

const videos = ref([
  { id:'ozL0yX45SUw', title:'Loading…', org:'Loading…' },
  { id:'gssopolLjnU', title:'Loading…', org:'Loading…' },
  { id:'TuxTu3Q-rk8', title:'Loading…', org:'Loading…' },
])

onMounted(async () => {
  const updated = await Promise.all(videos.value.map(async v => {
    try {
      const res  = await fetch(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${v.id}&format=json`)
      const data = await res.json()
      return { ...v, title: data.title, org: data.author_name }
    } catch {
      return v
    }
  }))
  videos.value = updated
})

// ── Next steps ───────────────────────────────────────────────
const tools = [
  { title:'DustWatch', desc:'Check construction dust near your suburb before any outdoor activity.', cta:'Open DustWatch',   to:{ path:'/assistance', query:{ tab:'dustwatch' } }, accent:'#c2410c', bg:'#fff7ed', border:'#fed7aa', icon:'<svg width="24" height="24" viewBox="0 0 32 32" fill="none"><path d="M16 4 L26 8 L26 18 C26 23 16 28 16 28 C16 28 6 23 6 18 L6 8 Z" fill="#c2410c" opacity="0.85"/><path d="M11 16 L14 19 L21 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>' },
  { title:'ClearPath',  desc:'Plan the safest walking route to school or the park.',                  cta:'Find a ClearPath', to:{ path:'/assistance', query:{ tab:'clearpath' } },  accent:'#7c3aed', bg:'#faf5ff', border:'#e9d5ff', icon:'<svg width="24" height="24" viewBox="0 0 32 32" fill="none"><path d="M6 26 Q10 18 16 16 Q22 14 26 8" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round" fill="none"/><circle cx="6" cy="26" r="3" fill="#7c3aed" opacity="0.85"/><circle cx="26" cy="8" r="3" fill="#7c3aed"/></svg>' },
  { title:'SafeShelf',  desc:'Scan cleaning products at home for asthma-triggering ingredients.',    cta:'Open SafeShelf',   to:'/housing-scanner',                                   accent:'#0ea5e9', bg:'#f0f9ff', border:'#bae6fd', icon:'<svg width="24" height="24" viewBox="0 0 32 32" fill="none"><rect x="3" y="10" width="26" height="3" rx="1.5" fill="#0ea5e9"/><rect x="3" y="18" width="26" height="3" rx="1.5" fill="#0ea5e9" opacity="0.6"/><rect x="3" y="26" width="26" height="3" rx="1.5" fill="#0ea5e9" opacity="0.35"/></svg>' },
  { title:'SafeSpots',  desc:'Find child-friendly parks rated safe for asthma today.',               cta:'Find SafeSpots',   to:{ path:'/assistance', query:{ tab:'safespots' } },   accent:'#16a34a', bg:'#f0fdf4', border:'#bbf7d0', icon:'<svg width="24" height="24" viewBox="0 0 32 32" fill="none"><path d="M8 26 C8 26 10 14 20 8 C26 5 28 6 28 6 C28 6 26 14 18 20 C14 23 8 26 8 26Z" fill="#16a34a" opacity="0.85"/><path d="M8 26 L18 16" stroke="white" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="26" r="2" fill="#16a34a"/></svg>' },
]
</script>

<style scoped>
/* ── Palette (purple-coral) ─────────────────────────────────── */
:root {
  --lp-purple:     #4f46e5;
  --lp-purple-lt:  #eef2ff;
  --lp-coral:      #fb923c;
  --lp-coral-lt:   #fff7ed;
  --lp-cream:      #faf9f7;
  --lp-warm:       #fefcf9;
  --lp-sand:       #e5e0d8;
  --lp-charcoal:   #1c1917;
  --lp-ink:        #292524;
  --lp-muted:      #78716c;
  --lp-faint:      #a8a29e;
  --font-serif: Georgia, 'Times New Roman', serif;
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
}

/* ── Page shell ─────────────────────────────────────────────── */
.learn-page {
  background: #f5f4f0;
  min-height: 100vh;
  font-family: var(--font-sans);
  font-family: var(--font-sans);
}

/* ── Hero ───────────────────────────────────────────────────── */
.learn-hero {
  background: linear-gradient(135deg, #0c2a26 0%, #0d4a42 45%, #0f6b5e 100%);
  padding: 72px 3rem 60px;
  position: relative;
  overflow: hidden;
}

.hero-inner {
  max-width: 1160px;
  margin: 0 auto;
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 48px;
  justify-content: space-between;
}

.hero-text {
  flex: 1;
  min-width: 0;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 5px 14px;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.7);
  margin-bottom: 20px;
}

.hero-title {
  font-family: var(--font-serif);
  font-size: clamp(32px, 4vw, 48px);
  font-weight: 500;
  color: white;
  line-height: 1.12;
  letter-spacing: -0.015em;
  margin-bottom: 16px;
}

.hero-title em {
  font-style: italic;
  color: #7ae0d4;
  font-weight: 400;
}

.hero-sub {
  font-size: 15px;
  color: rgba(255,255,255,0.65);
  line-height: 1.75;
  max-width: 520px;
  margin: 0;
}

/* ── Section nav ─────────────────────────────────────────────── */
.section-nav {
  background: white;
  border-bottom: 1.5px solid #e5e3de;
  display: flex;
  max-width: 100%;
  padding: 0 calc((100% - 1160px) / 2);
  position: sticky;
  top: 0;
  z-index: 90;
  gap: 0;
}

.sec-tab {
  padding: 16px 22px;
  border: none;
  border-bottom: 2.5px solid transparent;
  background: transparent;
  font-size: 13px;
  font-weight: 400;
  color: var(--lp-muted);
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.sec-tab:hover { color: var(--lp-charcoal); }
.sec-tab.active {
  border-bottom-color: #0d6b5e;
  color: #0d6b5e;
  font-weight: 600;
}

/* ── Section wrapper ─────────────────────────────────────────── */
.section-wrap {
  max-width: 1160px;
  margin: 0 auto;
  padding: 48px 3rem 72px;
}

.sec-eyebrow {
  font-size: 11px;
  color: #0d6b5e;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.sec-title {
  font-family: var(--font-serif);
  font-size: 28px;
  font-weight: 700;
  color: #1c1917;
  line-height: 1.2;
  margin-bottom: 10px;
  letter-spacing: -0.02em;
}

.sec-desc {
  font-size: 14px;
  color: var(--lp-muted);
  line-height: 1.75;
}

/* ── Stat cards ─────────────────────────────────────────────── */
.sec-header { margin-bottom: 36px; }

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 28px;
}

.stat-card {
  background: white;
  border-radius: 18px;
  border: 1.5px solid #e2e1dc;
  padding: 22px 20px;
  position: relative;
  overflow: hidden;
  cursor: default;
  transition: all 0.18s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stat-card.hovered {
  background: color-mix(in srgb, var(--accent) 10%, white);
  border-color: var(--accent);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 15%, transparent);
}

.stat-bubble {
  position: absolute;
  top: -18px; right: -18px;
  width: 90px; height: 90px;
  border-radius: 50%;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  transition: transform 0.18s;
}

.stat-card.hovered .stat-bubble { transform: scale(1.3); }

.stat-num {
  font-family: var(--font-serif);
  font-size: 34px;
  font-weight: 700;
  color: var(--accent);
  line-height: 1;
  margin-bottom: 4px;
  letter-spacing: -0.02em;
}

.stat-label { font-size: 13px; font-weight: 600; color: var(--lp-charcoal); margin-bottom: 3px; }
.stat-sub   { font-size: 12px; color: var(--lp-muted); line-height: 1.5; }
.stat-src   { font-size: 9px;  color: var(--lp-faint); margin-top: 8px; letter-spacing: 0.04em; }

.stat-cross {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid color-mix(in srgb, var(--accent) 25%, transparent);
  font-size: 11px;
  color: var(--accent);
  font-weight: 500;
}

.stat-cross-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
}

/* ── Charts ──────────────────────────────────────────────────── */
.chart-row {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

.chart-row--wide {
  grid-template-columns: 1.55fr 1fr;
}

.chart-card {
  background: white;
  border-radius: 20px;
  border: 1.5px solid #e2e1dc;
  padding: 24px;
  transition: border 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.chart-card.connected {
  border-color: #0d9488;
  box-shadow: 0 0 0 2px rgba(13,148,136,0.15);
}

.chart-card.connected-red {
  border-color: #e11d48;
  box-shadow: 0 0 0 2px rgba(225,29,72,0.12);
}

.chart-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 20px;
}

.chart-eyebrow { font-size: 11px; color: #0d6b5e; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 4px; }
.chart-title   { font-family: var(--font-serif); font-size: 17px; font-weight: 700; color: var(--lp-charcoal); }
.chart-src     { font-size: 10px; color: var(--lp-faint); margin-top: 8px; }

.chart-legend {
  display: flex;
  gap: 14px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 10px;
  color: var(--lp-muted);
}

.leg-dot {
  width: 10px; height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}

.target-col { background: #fb923c; }
.other-col  { background: #5eead4; }
.peak-col   { background: #e11d48; }

.connected-badge {
  font-size: 10px;
  background: #f0fdf4;
  color: #0d6b5e;
  border-radius: 8px;
  padding: 3px 9px;
  font-weight: 600;
  flex-shrink: 0;
}

.connected-badge.amber { background: #fff7ed; color: #c2410c; }
.connected-badge.red   { background: #fff1f2; color: #e11d48; }

/* Age bar chart */
.bar-chart-wrap {
  display: flex;
  align-items: flex-end;
  gap: 6px;
  height: 120px;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  position: relative;
}

.bar-fill {
  width: 100%;
  background: #5eead4;
  border-radius: 4px 4px 0 0;
  transition: all 0.18s;
}

.bar-fill.target { background: #fb923c; }
.bar-fill.barHov { background: #0d6b5e; }

.bar-label { font-size: 9px; color: var(--lp-muted); font-weight: 400; }
.target-lbl { color: #fb923c; font-weight: 600; }

.bar-tooltip {
  position: absolute;
  bottom: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--lp-charcoal);
  color: white;
  font-size: 9px;
  border-radius: 6px;
  padding: 4px 8px;
  white-space: nowrap;
  max-width: 140px;
  text-align: center;
  line-height: 1.4;
  z-index: 20;
  white-space: normal;
}

.season-tip { white-space: nowrap; }

/* Trigger breakdown */
.trigger-bars { display: flex; flex-direction: column; gap: 8px; }

.trigger-row { cursor: pointer; }

.trigger-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.trigger-name { font-size: 11px; color: var(--lp-muted); transition: all 0.15s; }
.trigger-name.active { color: var(--lp-charcoal); font-weight: 600; }
.trigger-pct  { font-size: 11px; font-weight: 600; }

.trigger-track {
  height: 8px;
  background: var(--lp-cream);
  border-radius: 4px;
  overflow: hidden;
}

.trigger-fill {
  height: 100%;
  border-radius: 4px;
  transition: all 0.2s;
}

/* Seasonal chart */
.season-bars {
  display: flex;
  align-items: flex-end;
  gap: 5px;
  height: 100px;
}

.season-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  position: relative;
}

.season-bar {
  width: 100%;
  border-radius: 4px 4px 0 0;
  background: #5eead4;
  transition: all 0.18s;
}

.season-bar.peak   { background: #e11d48; }
.season-bar.barHov { background: #0d6b5e; }

.season-label { font-size: 9px; color: var(--lp-muted); }
.peak-lbl     { color: #e11d48; font-weight: 600; }

/* Melbourne context card */
.melbourne-card {
  background: #0c2a26;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.melb-eyebrow { font-size: 11px; color: #7ae0d4; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.melb-title   { font-family: var(--font-serif); font-size: 17px; font-weight: 700; color: white; line-height: 1.3; }

.melb-row {
  border-left: 2px solid color-mix(in srgb, var(--mc) 50%, transparent);
  padding-left: 12px;
}

.melb-label { font-size: 12px; font-weight: 600; color: white; margin-bottom: 2px; }
.melb-val   { font-size: 11px; color: rgba(255,255,255,0.55); margin-bottom: 2px; }
.melb-src   { font-size: 9px;  color: rgba(255,255,255,0.3); }

/* Cross-connection hint */
.cross-hint {
  background: #f0fdf4;
  border: 1px solid rgba(13,107,94,0.18);
  border-radius: 14px;
  padding: 14px 20px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  color: #0d6b5e;
  line-height: 1.6;
}

.cross-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #0d6b5e;
  flex-shrink: 0;
}

/* Sources */
.sources-row {
  background: white;
  border: 1px solid var(--lp-sand);
  border-radius: 14px;
  padding: 12px 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.sources-label { font-size: 11px; color: var(--lp-faint); margin-right: 4px; }

.source-chip {
  font-size: 11px;
  color: var(--lp-muted);
  background: var(--lp-cream);
  border-radius: 8px;
  padding: 2px 8px;
}

/* ── Understand Asthma ───────────────────────────────────────── */
.understand-top {
  display: flex;
  gap: 32px;
  align-items: flex-start;
  margin-bottom: 40px;
}

.understand-text {
  flex: 1;
  font-size: 14px;
  color: #292524;
  line-height: 1.85;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.understand-text p { margin: 0; }
.src-note { font-size: 11px; color: var(--lp-faint); }

/* Airway card */
.airway-card {
  flex-shrink: 0;
  width: 240px;
  border-radius: 22px;
  border: 2px solid;
  padding: 24px 20px;
  text-align: center;
  transition: all 0.4s ease;
}

.airway-open   { background: #f0fdf4; border-color: #0d9488; }
.airway-closed { background: #fff1f2; border-color: #e11d48; }

.airway-label {
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 14px;
}

.airway-open   .airway-label { color: #0d9488; }
.airway-closed .airway-label { color: #e11d48; }

.airway-tube {
  width: 80px;
  height: 120px;
  margin: 0 auto 16px;
  border-radius: 40px;
  border: 3px solid;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.4s ease;
}

.airway-open   .airway-tube { background: #f0fdf4; border-color: #0d9488; }
.airway-closed .airway-tube { background: #fff1f2; border-color: #e11d48; }

.airway-inner {
  border-radius: 20px;
  border: 2px solid;
  height: 80px;
  transition: all 0.4s ease;
}

.airway-wide   { width: 40px; background: #ecfdf5; border-color: #0d9488; }
.airway-narrow { width: 12px; background: #fff1f2; border-color: #e11d48; }

.airway-btns {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 14px;
}

.airway-btn {
  padding: 5px 14px;
  border-radius: 16px;
  border: 1px solid var(--lp-sand);
  background: transparent;
  font-size: 11px;
  font-weight: 600;
  color: var(--lp-muted);
  cursor: pointer;
  transition: all 0.2s;
}

.airway-btn--active-open   { background: #0d6b5e; border-color: #0d6b5e; color: white; }
.airway-btn--active-closed { background: #e11d48; border-color: #e11d48; color: white; }

.airway-desc { font-size: 11px; }
.airway-open   .airway-desc { color: var(--lp-muted); }
.airway-closed .airway-desc { color: #e11d48; }

/* Triggers */
.subsec-gap { margin-top: 52px; }

.trigger-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-top: 14px;
}

.trigger-card {
  background: white;
  border: 1.5px solid #e2e1dc;
  border-radius: 14px;
  padding: 14px 12px;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.trigger-card:hover {
  border-color: var(--tc);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.trigger-card--active {
  background: color-mix(in srgb, var(--tc) 8%, white);
  border-color: var(--tc);
}

.trigger-icon-wrap {
  width: 32px; height: 32px;
  border-radius: 10px;
  background: color-mix(in srgb, var(--tc) 15%, white);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
}

.trigger-icon-lbl { font-size: 12px; font-weight: 700; color: var(--tc); }

.trigger-card-name { font-size: 12px; font-weight: 600; color: var(--lp-charcoal); }

.trigger-expand {
  margin-top: 8px;
  font-size: 11px;
  color: var(--lp-ink);
  line-height: 1.65;
}

.trigger-expand p { margin: 0 0 4px; }
.trigger-expand-src { font-size: 9px; color: var(--lp-faint); }

/* Symptoms */
.symptom-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 16px;
}

.symptom-card {
  background: white;
  border: 1.5px solid #e2e1dc;
  border-left: 5px solid var(--sc);
  border-radius: 0 14px 14px 0;
  padding: 16px 18px;
  cursor: pointer;
  transition: border-color 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.symptom-card--active { border-color: var(--sc); }

.symptom-name { font-size: 14px; font-weight: 600; color: var(--lp-charcoal); }
.symptom-sub  { font-size: 12px; color: var(--lp-muted); margin-top: 4px; }
.symptom-stat {
  font-size: 12px;
  color: var(--lp-ink);
  line-height: 1.7;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid color-mix(in srgb, var(--sc) 20%, transparent);
}

/* FAQ */
.faq-list { display: flex; flex-direction: column; gap: 8px; margin-top: 16px; }

.faq-item {
  background: white;
  border: 1.5px solid #e2e1dc;
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}

.faq-item--open { border-color: #0d9488; }

.faq-row {
  padding: 16px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.faq-q { font-size: 14px; font-weight: 500; color: var(--lp-charcoal); }

.faq-toggle {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: #f0fdf4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: var(--lp-purple);
  flex-shrink: 0;
  line-height: 1;
}

.faq-item--open .faq-toggle { background: #0d9488; color: white; }

.faq-body {
  padding: 0 18px 16px;
  border-top: 1px solid #ecfdf5;
}

.faq-body p { font-size: 13px; color: var(--lp-ink); line-height: 1.8; padding-top: 12px; margin-bottom: 6px; }
.faq-src    { font-size: 10px; color: var(--lp-faint); }

/* ── Inhaler guide ───────────────────────────────────────────── */
.inhaler-layout {
  display: flex;
  gap: 24px;
  margin-bottom: 40px;
}

.inhaler-steps {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 200px;
  flex-shrink: 0;
}

.inhaler-step {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 12px;
  background: white;
  border: 1.5px solid #e2e1dc;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.inhaler-step--active {
  background: #0d6b5e;
  border-color: #0d6b5e;
  box-shadow: 0 4px 12px rgba(13,107,94,0.3);
}

.step-num {
  width: 22px; height: 22px;
  border-radius: 50%;
  background: var(--lp-purple-lt);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: #0d6b5e;
  flex-shrink: 0;
}

.inhaler-step--active .step-num { background: rgba(255,255,255,0.22); color: #fff; font-weight:800; }

.step-name { font-size: 13px; color: #374151; font-weight: 500; letter-spacing: -0.01em; }
.inhaler-step--active .step-name { color: #ffffff !important; font-weight: 600; text-shadow: none; }

.inhaler-detail {
  flex: 1;
  background: white;
  border-radius: 20px;
  border: 1.5px solid #e2e1dc;
  padding: 28px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.inhaler-detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.step-num-big {
  width: 44px; height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0d9488, #0d6b5e);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.inhaler-step-title {
  font-family: var(--font-serif);
  font-size: 22px;
  font-weight: 700;
  color: var(--lp-charcoal);
}

.inhaler-visual {
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
  border-radius: 14px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 18px;
  border: 1px solid #a7f3d0;
}

.inhaler-visual-name { font-size: 12px; color: var(--lp-muted); font-weight: 500; }

.inhaler-desc {
  font-size: 14px;
  color: var(--lp-ink);
  line-height: 1.8;
  margin-bottom: 14px;
}

.inhaler-note {
  background: #fffbeb;
  border: 1px solid #fde68a;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 12px;
  color: var(--lp-ink);
  margin-bottom: 20px;
}

.inhaler-note strong { color: #92400e; }

.inhaler-nav {
  display: flex;
  justify-content: space-between;
}

.inhaler-prev {
  background: transparent;
  border: 1px solid var(--lp-sand);
  border-radius: 12px;
  padding: 9px 18px;
  font-size: 13px;
  color: var(--lp-muted);
  cursor: pointer;
  transition: all 0.15s;
}

.inhaler-prev:disabled { opacity: 0.4; cursor: default; }
.inhaler-prev:not(:disabled):hover { background: var(--lp-purple-lt); border-color: var(--lp-purple); color: var(--lp-purple); }

.inhaler-next {
  background: linear-gradient(135deg, #0d9488, #0d6b5e);
  border: none;
  border-radius: 12px;
  padding: 9px 18px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: opacity 0.15s;
}

.inhaler-next:disabled { background: var(--lp-sand); cursor: default; }

/* Videos */
.video-section {
  background: white;
  border-radius: 20px;
  border: 1px solid var(--lp-sand);
  padding: 28px;
  margin-bottom: 20px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.video-card {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid var(--lp-sand);
}

.video-meta  { padding: 10px 14px; background: white; }
.video-title { font-size: 12px; font-weight: 600; color: var(--lp-charcoal); margin-bottom: 2px; }
.video-org   { font-size: 11px; color: var(--lp-muted); }

.disclaimer {
  background: var(--lp-warm);
  border: 1px solid var(--lp-sand);
  border-radius: 12px;
  padding: 12px 18px;
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 12px;
  color: var(--lp-muted);
  line-height: 1.65;
}

.disclaimer svg { flex-shrink: 0; margin-top: 1px; color: #a78bfa; }
.disclaimer strong { color: var(--lp-ink); }

/* ── Next steps ──────────────────────────────────────────────── */
.action-plan-card {
  background: linear-gradient(135deg, #0c2a26, #0d3d5c);
  border-radius: 20px;
  padding: 32px 36px;
  margin-bottom: 40px;
  display: flex;
  gap: 28px;
  align-items: center;
}

.action-plan-text { flex: 1; }
.action-plan-title { font-family: var(--font-serif); font-size: 24px; font-weight: 700; color: white; line-height: 1.25; margin-bottom: 10px; }
.action-plan-desc  { font-size: 13px; color: rgba(255,255,255,0.65); line-height: 1.75; margin-bottom: 8px; }
.action-plan-src   { font-size: 11px; color: rgba(255,255,255,0.35); }

.action-plan-icon {
  flex-shrink: 0;
  width: 90px; height: 90px;
  background: rgba(255,255,255,0.08);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tools-heading { font-family: var(--font-serif); font-size: 20px; font-weight: 700; color: var(--lp-charcoal); margin-bottom: 8px; }

.tools-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 28px;
}

.tool-card {
  background: var(--tb);
  border: 1px solid var(--tbr);
  border-radius: 18px;
  padding: 20px;
  cursor: pointer;
  display: flex;
  gap: 14px;
  align-items: flex-start;
  transition: transform 0.15s, box-shadow 0.15s;
  text-decoration: none;
}

.tool-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.08); }

.tool-icon-wrap {
  width: 42px; height: 42px;
  border-radius: 11px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.tool-body { flex: 1; }
.tool-title { font-size: 14px; font-weight: 700; color: var(--lp-charcoal); margin-bottom: 4px; }
.tool-desc  { font-size: 12px; color: var(--lp-muted); line-height: 1.6; margin-bottom: 10px; }
.tool-cta   { font-size: 12px; color: var(--ta); font-weight: 600; }

.closing-card {
  background: linear-gradient(135deg, #0c2a26, #0d4a42);
  border-radius: 20px;
  padding: 32px 36px;
  text-align: center;
}

.closing-card h3 { font-family: var(--font-serif); font-size: 24px; font-weight: 700; color: white; margin-bottom: 10px; }
.closing-card p  { font-size: 14px; color: rgba(255,255,255,0.75); line-height: 1.8; max-width: 480px; margin: 0 auto; }

/* ── Breeze mascot (learn page) ─────────────────────────────── */
.learn-breeze {
  width: 110px;
  height: auto;
  filter: drop-shadow(0 8px 20px rgba(251,146,60,0.25));
}

@keyframes breeze-float-learn {
  0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)}
}

@keyframes breeze-ring-spin-learn {
  0%{stroke-dashoffset:0} 100%{stroke-dashoffset:-60}
}

.breeze-float { animation: breeze-float-learn 4s ease-in-out infinite; }
.breeze-ring-learn { animation: breeze-ring-spin-learn 4s linear infinite; }

.hero-breeze-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.hero-breeze-wrap:hover {
  transform: scale(1.05);
}

.hero-breeze-wrap.breeze-clicked {
  animation: breeze-bounce 0.4s ease;
}

@keyframes breeze-bounce {
  0%   { transform: scale(1); }
  30%  { transform: scale(1.18) rotate(-8deg); }
  60%  { transform: scale(1.12) rotate(6deg); }
  100% { transform: scale(1); }
}

.hero-breeze-label {
  font-size: 12px;
  color: rgba(255,255,255,0.75);
  text-align: center;
  line-height: 1.5;
  margin: 0;
  max-width: 160px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 12px;
  padding: 8px 12px;
  transition: all 0.3s ease;
}



.breeze-inline-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #f0fdf4;
  border: 1px solid #a7f3d0;
  border-radius: 16px;
  padding: 14px 20px;
  margin-bottom: 32px;
}

.breeze-inline-wrap .learn-breeze { width: 64px; flex-shrink: 0; }

.breeze-inline-msg {
  font-size: 14px;
  color: #0d4a42;
  line-height: 1.6;
  margin: 0;
  font-style: italic;
}

.breeze-closing-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

/* ── Animations ──────────────────────────────────────────────── */
@keyframes lp-float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-6px); }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.expand-enter-active { transition: all 0.22s ease; overflow: hidden; }
.expand-leave-active { transition: all 0.15s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0; }
.expand-enter-to, .expand-leave-from { max-height: 300px; opacity: 1; }

.tooltip-fade-enter-active, .tooltip-fade-leave-active { transition: opacity 0.15s; }
.tooltip-fade-enter-from, .tooltip-fade-leave-to { opacity: 0; }

/* ── Responsive ──────────────────────────────────────────────── */
@media (max-width: 768px) {
  .hero-title { font-size: 28px; }
  .stat-grid  { grid-template-columns: 1fr 1fr; }
  .chart-row, .chart-row--wide { grid-template-columns: 1fr; }
  .trigger-grid { grid-template-columns: repeat(2,1fr); }
  .understand-top { flex-direction: column; }
  .airway-card { width: 100%; }
  .inhaler-layout { flex-direction: column; }
  .inhaler-steps { width: 100%; }
  .video-grid { grid-template-columns: 1fr; }
  .tools-grid { grid-template-columns: 1fr; }
  .action-plan-card { flex-direction: column; }
}
</style>
