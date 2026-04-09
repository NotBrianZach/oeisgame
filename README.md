# oeisgame
vibe coding a roguelikedeckbuilder based on the oeis



# 🎮 Game Concept: **“Sequencebreaker”**

### Core idea

You don’t play attack cards — you play **rules that generate integer sequences**.

Combat =

> build a sequence that satisfies constraints or “overpowers” an enemy’s sequence.

---

# 🧠 Core Mechanics

## 1. Your “deck” = sequence operators

Each card transforms or generates sequences.

Examples:

* +1 → add 1 to each term
* ×2 → multiply sequence
* Shift → drop first term
* Concat → join two sequences
* Recurrence → define next term based on previous

You start with something like:

[1, 1, 1, 1, ...]


and build from there.

---

## 2. Combat = sequence vs sequence

Enemies have rules like:

> “Match or exceed my growth rate by turn 6”

or

> “Produce a sequence containing primes”

or

> “Your sequence must avoid repeats”

So instead of HP bars, you’re solving constraints under pressure.

---

## 3. Turns

Each turn:

* Play cards (modify your sequence)
* Sequence grows by 1 term
* Enemy evaluates your sequence

---

# 🔢 Example Run

## Starting sequence

[1]


## Deck (starter)

* +1
* +1
* ×2
* Duplicate Last
* Stabilize (prevent explosion)

---

# 🃏 Example Cards

## Basic cards

* **Increment**

  * Add 1 to all terms
* **Double**

  * Multiply all terms by 2
* **Append Sum**

  * Next term = sum of all previous

---

## Intermediate cards

* **Fibonacci Kernel**

  * Next term = sum of last 2 terms
    → pushes toward A000045

* **Prime Filter**

  * Remove non-prime terms

* **Difference**

  * Replace sequence with first differences
    → [a,b,c] → [b-a, c-b]

---

## Advanced / weird cards

* **Recamán Step**

  * Apply Recamán rule for next term
* **Collatz Burst**

  * Apply Collatz transform to last term
* **Modulator (mod n)**

  * Reduce all terms mod n

---

# 🧟 Enemy Design

## Enemy: “The Exponential Beast”

* Wants:

  * growth ≥ exponential
* Punishes:

  * linear sequences

👉 Forces you into:

* doubling
* recurrence stacking

---

## Enemy: “Prime Oracle”

* Wants:

  * at least 3 primes in first 6 terms
* Blocks:

  * even-heavy sequences

👉 Encourages:

* filters
* clever generation

---

## Enemy: “Entropy Warden”

* Wants:

  * no repeated values
* Punishes:

  * loops / cycles

---

# 🧱 Example Deck Builds

---

## 🧮 Deck 1: Fibonacci Engine (A000045 vibes)

### Core cards

* Fibonacci Kernel
* Duplicate Last
* Stabilize
* Minor scaling (+1)

### Strategy

* Build:

  
[1, 1, 2, 3, 5, 8, 13...]

* Wins:

  * steady growth
  * predictable structure

### Weakness

* slow early game
* vulnerable to “non-linear spike” enemies

---

## 🔥 Deck 2: Exponential Ramp

### Core cards

* ×2
* ×2
* Append Sum
* Amplify (multiply last term)

### Output

[1, 2, 4, 8, 16, ...]


### Strategy

* brute-force growth
* beat scaling enemies

### Weakness

* fails constraints like:

  * “must include primes”
  * “avoid repetition patterns”

---

## 🌀 Deck 3: Chaos / Collatz

### Core cards

* Collatz Burst
* Random Offset
* Modulator
* Duplicate Last

### Output

Wild, unstable sequences

### Strategy

* adapt to weird constraints
* exploit unpredictable enemies

### Weakness

* unreliable
* hard to optimize

---

## 🧪 Deck 4: Prime Hunter

### Core cards

* Prime Generator (biased RNG)
* Prime Filter
* Increment
* Difference

### Strategy

* sculpt sequence to maximize primes

Example:

[2, 3, 5, 7, 11]


---

## 🧱 Deck 5: Structural / Meta Deck

### Core cards

* Difference
* Difference
* Integrate (reverse difference)
* Normalize

### Strategy

* reshape sequences dynamically
* counter enemy conditions

---

# 🧭 Roguelike Structure

* Map nodes = different “math challenges”
* Rewards:

  * new operators
  * new axioms (starting rules)
* Bosses:

  * enforce multiple constraints simultaneously

---

# 🧩 Boss Example

## “The Archivist”

Demands:

* Sequence must:

  * contain primes
  * grow faster than linear
  * avoid duplicates

👉 Forces hybrid deck:

* recurrence + filtering + scaling

---

# 💡 Why this works

This hits:

* **OEIS vibe** → discovering patterns
* **deckbuilder loop** → synergy + combos
* **roguelike tension** → constraints + randomness

And importantly:

> You’re not memorizing sequences — you’re *inventing them*

---

# 🚀 If you want to push this further

We could:

* design **actual card list (like 50+ cards)**
* add **UI ideas (sequence visualizations)**
* or make a **minimal playable prototype spec (React + Supabase 👀)**

This honestly feels like something you'd enjoy building given your stack + math curiosity.

Yeah this is *extremely* strong. It’s one of those ideas where the core loop is already doing real intellectual work, not just reskinned combat.

Let me push it further in a way that makes it actually *implementable* as a game (and not just a clever concept), because that’s where these ideas usually break.

---

# ⚙️ The Missing Piece: **Scoring Function (a.k.a. “Damage”)**

Right now everything is constraints, which is cool—but you also need a **continuous reward signal** so turns feel impactful.

## 🔥 Proposal: Dual System

Each enemy has:

### 1. **Hard Constraints (lose condition)**

* “Must contain ≥ 2 primes”
* “No duplicates”
* “Growth ≥ quadratic”

Fail → take damage

---

### 2. **Soft Objective (damage dealt)**

You deal damage based on a **scoring function over your sequence**

Examples:

### Against Exponential Beast

```
score = growth_rate(sequence)
```

### Against Prime Oracle

```
score = (# of primes in first N terms)
```

### Against Entropy Warden

```
score = entropy(sequence)
```

---

👉 This gives you:

* constant feedback per turn
* optimization pressure
* reason to go beyond “just barely passing constraints”

---

# 🧠 Key Design Insight: **Local vs Global Cards**

You’ll want to formalize cards into two categories:

---

## 🟦 Local (term-level)

Affect only last / next term

* Collatz Burst
* Fibonacci Kernel
* Append Sum

👉 Easier to reason about, more tactical

---

## 🟥 Global (sequence-level)

Rewrite entire sequence

* Difference
* Normalize
* Prime Filter
* Modulator

👉 High power, high chaos

---

## 💡 Why this matters

This creates:

* **combo structure**
* **risk/reward tension**
* “do I rewrite everything or build forward?”

---

# 🧱 Important: **Sequence Length Cap**

You *must* cap or compress sequences, or the game becomes:

> “simulate 500 terms and wait”

## Options:

### Option A: Fixed window

Keep last N terms (e.g. 6–10)

### Option B: Decay

Older terms lose influence

### Option C: Projection

Only evaluate on:

```
[aₙ₋5, ..., aₙ]
```

👉 I strongly recommend **windowed sequences (like hand size)**

---

# 🧬 Archetype System (this is where it becomes Slay the Spire)

You already hinted at it—formalize it:

---

## 🌿 Archetype 1: Recurrence Engine

Cards:

* Fibonacci Kernel
* Linear Recurrence (customizable)
* Memory Boost (increase dependency depth)

Playstyle:

* deterministic growth
* scaling consistency

---

## ⚡ Archetype 2: Amplification

Cards:

* ×2
* Power (square last term)
* Exponential Push

Playstyle:

* raw scaling
* fragile to constraints

---

## 🧹 Archetype 3: Filtering / Sculpting

Cards:

* Prime Filter
* Deduplicate
* Threshold Cutoff

Playstyle:

* shape sequence to satisfy constraints

---

## 🌀 Archetype 4: Transform Algebra

Cards:

* Difference
* Integrate
* Reverse
* Convolution

Playstyle:

* meta-manipulation
* high skill ceiling

---

## 🎲 Archetype 5: Chaos / Probabilistic

Cards:

* Random Offset
* Prime Bias RNG
* Noise Injection

Playstyle:

* adaptability
* gambling

---

# 🧟 Enemy Upgrade: **Adversarial Sequences**

Right now enemies are passive evaluators.

Make them *active*.

---

## Enemy plays “anti-cards”

Example:

* **Noise Injection**

  * adds random perturbation to your sequence

* **Modulo Curse**

  * forces mod n for 1 turn

* **Truncation**

  * removes last term

---

👉 This creates:

* disruption
* counterplay
* real “combat feel”

---

# 🧩 Boss Design Upgrade: Multi-Phase Math

## Boss: “The Archivist” (expanded)

### Phase 1

* enforce primes

### Phase 2

* enforce growth

### Phase 3

* enforce structure (no repeats, low variance)

---

👉 Forces deck flexibility, not just specialization

---

# 🎮 UI Idea (this is important for feasibility)

You need to make sequences *visceral*.

---

## Visualizations

### 1. Number Line Animation

* terms appear one by one
* growth visually obvious

---

### 2. Graph View

Plot:

```
x = index
y = value
```

👉 exponential vs linear becomes *instantly readable*

---

### 3. Pattern Highlights

* primes glow
* repeats pulse red
* monotonicity arrows

---

---

# 🧪 Minimal Prototype (your stack)

Given your setup (React + Supabase), here’s a realistic MVP:

---

## Core loop

* sequence = array<number>
* deck = array<card>
* play card → pure function:

```ts
type Card = (seq: number[]) => number[];
```

---

## Enemy

```ts
type Enemy = {
  constraint: (seq: number[]) => boolean;
  score: (seq: number[]) => number;
};
```

---

## Turn loop

```ts
seq = applyCard(seq, card);
seq = advance(seq); // add next term
score = enemy.score(seq);
```

---

## No backend needed initially

Supabase only for:

* run persistence
* leaderboard of “best sequences” 👀 (this is VERY cool)

---

# 🚀 Killer Feature Idea (this is *big*)

## 🔎 “OEIS Discovery Mode”

After a run:

> “Your sequence resembles A000045 (Fibonacci) with 82% similarity”

Or:

> “New sequence discovered”

---

This gives:

* replayability
* educational hook
* *insane nerd appeal*

---

# 🧠 Final Thought

The real magic here is:

> You're not playing cards — you're **programming under constraints**

If you lean into that (without making it feel like coding), you get something genuinely novel.

---

If you want, next step I’d suggest:

👉 I can design a **tight 30-card starter set + 3 enemies + progression curve**

That’s enough to actually build and playtest.
