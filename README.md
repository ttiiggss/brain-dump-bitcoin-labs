# Brain Dump — Bitcoin Learning Labs

A kanban board for **Brain Dump**, a Bitcoin self-custody education project by **m3rkle_tree**.

Built around the concept of [Hack The Box](https://www.hackthebox.com/)-style interactive learning labs, focused on Bitcoin security, privacy, and self-custody.

## 🧩 Module Tracks

| Track | Topics |
|-------|--------|
| 🟠 **Learning Labs** | Hack-the-box style Bitcoin attack & defense challenges (seed theft, fee sniping, dust attacks, RBF double-spend, PSBT tampering) |
| 🟣 **Privacy** | Coinjoin & UTXO hygiene, address reuse detection |
| 🟢 **Storage** | Paper seed backups ("seed pills"), steel punch & metal backup durability testing |
| 🟡 **Signing** | Secure-element signers (Coldcard, SeedSigner, Krux, Jade), multisig quorum setups |
| 🔵 **Infra** | Run your own node (Bitcoin Core + Electrs + mempool.space), Lightning |

## 🚀 Usage

Open `index.html` in any browser — no build step, no dependencies.

```bash
# Option 1: Just open the file
open index.html

# Option 2: Serve locally
python3 -m http.server 8000
# Then visit http://localhost:8000
```

## ✨ Features

- **Drag & drop** kanban board (Brain Dump → Design → In Progress → QA → Shipped)
- **Auto-saves** to browser localStorage
- **Search & filter** by module track
- **Priority indicators** on each card
- **Fully responsive** — works on desktop and mobile
- **Zero dependencies** — vanilla HTML/CSS/JS

## 📋 Board Structure

| Column | Purpose |
|--------|---------|
| Brain Dump | Raw ideas, future modules, unsorted concepts |
| Design / Spec | Architecture, curriculum mapping, planning |
| In Progress | Currently being built or written |
| Testing / QA | Review, peer feedback, testing |
| Shipped | Done and published |

## 🔑 About

**Brain Dump** is curated by **m3rkle_tree** — a hands-on Bitcoin learning project that teaches self-custody through practical labs rather than theory alone.

---

*Not financial advice. Educational content only.*
