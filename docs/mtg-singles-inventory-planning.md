# MTG Singles Business — Inventory Planning

**Goal:** How many booster boxes, bundles, and gift boxes to crack for decent singles inventory.

---

## The Math: What You Actually Get From Cracking

### Standard Booster Box (36 packs)
- **Rares:** 36 (1 per pack)
- **Mythics:** ~4.5 (1 in 8 packs)
- **Uncommons:** 108 (3 per pack)
- **Commons:** 360 (10 per pack)
- **Special/Box Toppers:** 1-3 (set-dependent)

### Per-Box Rarity Distribution
| Rarity | Per Pack | Per 36-Pack Box | Per 10 Boxes | Per 20 Boxes | Per 50 Boxes |
|--------|----------|----------------|--------------|--------------|--------------|
| Mythics | 1/8 packs | ~4.5 | ~45 | ~90 | ~225 |
| Rares | 1/pack | 36 | 360 | 720 | 1,800 |
| Uncommons | 3/pack | 108 | 1,080 | 2,160 | 5,400 |
| Commons | 10/pack | 360 | 3,600 | 7,200 | 18,000 |

---

## Expected Value (EV) — The Key Metric

**EV = Average dollar value of singles you can pull per box.**

### Rule of Thumb
- **Modern Standard Set:** EV ≈ $80-110/box at release, drops to $50-70 in 3-6 months
- **Premium/Deluxe Set:** EV ≈ $120-160/box at release
- **Vintage/Remastered Set:** EV ≈ $150-250/box at release

**Wholesale Price (approx):**
- Standard booster box: $70-90
- Collector booster box: $140-180
- Commander deck: $20-25
- Gift Bundle: $40-50

### Break-Even Threshold
- If **EV > wholesale**: you make money cracking
- If **EV ≈ wholesale**: you break even (inventory acquisition cost)
- If **EV < wholesale**: lose money on cracking; buy singles instead

---

## Recommended Starting Inventory Levels

### Minimal Viable Singles Business (MVP)
**Goal:** Cover the most-played cards in Standard + Pioneer/Modern staples

| Product | Quantity | Expected Singles Inventory | Approx Cost |
|---------|----------|----------------------------|-------------|
| Standard Booster Boxes | 10 | ~45 mythics + 360 rares | $800-900 |
| Collector Booster Boxes | 3 | ~15 mythics + premium foils | $450-550 |
| Commander Decks | 5 | ~100 commander singles (deck-focused) | $100-125 |
| Gift Bundles | 2 | ~8 mythics + special promos | $80-100 |
| **Total** | | | **~$1,450-1,700** |

**What this gives you:**
- **450+ rare/mythic unique cards** (with duplicates removed, likely 150-200 unique)
- **1,080+ uncommons** (good for bulk singles)
- **Specials/foils** from collector boosters and bundles (higher margin)
- **Commander staples** from the 5 decks (steady demand)

**Pros:** Low entry cost, test market demand, manageable inventory tracking
**Cons:** Limited inventory breadth, may run out of in-demand singles quickly

---

### Serious Reseller Inventory (Mid-Range)
**Goal:** Good coverage of meta singles + bulk options

| Product | Quantity | Expected Singles Inventory | Approx Cost |
|---------|----------|----------------------------|-------------|
| Standard Booster Boxes | 20 | ~90 mythics + 720 rares | $1,600-1,800 |
| Collector Booster Boxes | 5 | ~22 mythics + premium foils | $750-900 |
| Commander Decks | 8 | ~160 commander singles | $160-200 |
| Gift Bundles | 4 | ~16 mythics + special promos | $160-200 |
| Intro Packs / Bundles | 5 | ~40 uncommons + rares | $200-250 |
| **Total** | | | **~$2,870-3,350** |

**What this gives you:**
- **900+ rare/mythic cards** (~300-400 unique)
- **2,160+ uncommons**
- **Substantial foil inventory** from collector boosters
- **Gift bundle promos** (chase cards)

**Pros:** Deeper inventory, can fulfill more orders, better margin on premium singles
**Cons:** Higher upfront cost, more inventory management

---

### Full-Blown Store Inventory (Serious)
**Goal:** Cover entire set's meta + healthy bulk inventory

| Product | Quantity | Expected Singles Inventory | Approx Cost |
|---------|----------|----------------------------|-------------|
| Standard Booster Boxes | 50 | ~225 mythics + 1,800 rares | $4,000-4,500 |
| Collector Booster Boxes | 12 | ~54 mythics + premium foils | $1,800-2,200 |
| Commander Decks | 15 | ~300 commander singles | $300-375 |
| Gift Bundles | 8 | ~32 mythics + special promos | $320-400 |
| Intro Packs / Bundles | 10 | ~80 uncommons + rares | $400-500 |
| Bundle Boxes / Fat Packs | 5 | ~50 uncommons + rares + lands | $250-300 |
| **Total** | | | **~$7,070-8,275** |

**What this gives you:**
- **2,000+ rare/mythic cards** (~600-800 unique — near-complete set coverage)
- **5,400+ uncommons** — substantial bulk inventory
- **Heavy foil/special inventory** — high-margin items
- **Complete promo coverage** from bundles

**Pros:** Near-complete set coverage, high customer satisfaction, sustainable business
**Cons:** Major capital investment, requires proper storage + inventory system

---

## Product Mix Strategy

### The 60/30/10 Rule
- **60% of budget:** Standard booster boxes (bread-and-butter singles)
- **30% of budget:** Collector boosters + bundles (premium singles + promos)
- **10% of budget:** Commander decks + intro packs (niche demand + cross-sell)

### Why This Mix Works
1. **Standard boxes** give you the most cards per dollar — bulk uncommons are $0.05-0.10 each but move fast
2. **Collector boosters** give you foils and special treatments — these command 2-5x prices of regular versions
3. **Bundles** have exclusive promos — these are often $5-15 cards that you get for free
4. **Commander decks** give you commander staples (steady EDH demand) and bulk commons/lands

---

## Inventory Management & Tracking

### What to Track
- **Mythic inventory:** Most valuable, track each copy
- **Rare inventory:** Track high-value rares ($5+), bulk low-value rares (<$5)
- **Uncommons:** Bulk by type (pump spells, removal, lands) or just count
- **Foil inventory:** Separate tracking — higher prices
- **Special/promo inventory:** Highest priority — limited supply

### Simple System (Early Stage)
- Google Sheets with tabs for each rarity
- Card name, quantity, condition, price bought, price sold
- Update daily

### Better System (Scaling)
- Database (PostgreSQL/SQLite) with:
  - Cards table (card_id, name, set, rarity, foil)
  - Inventory table (inventory_id, card_id, quantity, condition, price_bought)
  - Sales table (sale_id, card_id, quantity, price_sold, date)
- Integrate with Twilio for phone order processing

---

## Twilio Integration for Phone Orders

### What Twilio Can Do
- **IVR (Interactive Voice Response):** "Press 1 for Standard singles, Press 2 for Commander"
- **SMS Order Confirmations:** Send order details to customers
- **Voicemail for Custom Requests:** "I'm looking for a foil Dori from HOB"
- **Two-way SMS:** Customers text orders, you confirm inventory

### Basic Architecture
1. **Customer calls** → Twilio receives call
2. **IVR menu** guides them to product type
3. **Speech-to-text** captures card name (use AssemblyAI/OpenAI Whisper)
4. **Database lookup** checks inventory + pricing
5. **Twilio speaks back** availability + price
6. **Customer confirms** → SMS confirmation sent

### Rough Implementation Steps
- **Step 1:** Sign up for Twilio ($1/number/month, usage-based)
- **Step 2:** Set up a simple Flask/Express server to handle Twilio webhooks
- **Step 3:** Connect webhook to your inventory database
- **Step 4:** Configure Twilio Studio (no-code IVR builder) or use TwiML
- **Step 5:** Test end-to-end with mock inventory

---

## Online Store Setup

### Platforms to Consider
| Platform | Pros | Cons |
|----------|------|------|
| Shopify | Easy, good apps | $29-299/mo, 2-4% fees |
| WooCommerce (WordPress) | Free, fully customizable | Requires hosting, technical |
| TCGplayer Pro | Built-in for MTG, large audience | 12-15% commission |
| Cardmarket (MKM) | EU-centric, huge MTG community | Commission + fees, EU focus |
| eBay | Huge reach, easy listing | 10-15% fees, chargebacks |

### Recommendation for Start
- **Phase 1:** **TCGplayer Pro** or **Cardmarket** — get the MTG audience immediately
- **Phase 2:** Add **Shopify** or **WooCommerce** for your own brand + Twilio integration
- **Phase 3:** Scale to multi-platform

---

## Summary

### For a "decent inventory" to start, I'd recommend:
- **20 standard booster boxes** — $1,600-1,800
- **5 collector booster boxes** — $750-900
- **8 commander decks** — $160-200
- **4 gift bundles** — $160-200

**Total: ~$2,670-3,100**

This gives you:
- **~112 mythics** (good coverage of meta cards)
- **~720 rares** (breadth of playable cards)
- **~2,160 uncommons** (bulk inventory)
- **~160 commander singles** (EDH demand)
- **Special foils/promos** from collectors + bundles

That's enough to fulfill most early orders without running out immediately, while keeping capital reasonable.

---

## References
- [MTG Expected Value Guide](https://mtgbulkcaster.com/blog/mtg-expected-value)
- [How Many Booster Packs per Box](https://draftsim.com/packs-per-box-mtg/)
- [Reddit: Average boxes to complete a set](https://www.reddit.com/r/magicTCG/comments/67pncg/is_there_an_average_number_of_booster_boxes_to/)
- [TCG Sync: Opening an MTG Store](https://tcgsync.com/how-to-open-a-magic-store)
- [Scryfall (Card Database & Prices)](https://scryfall.com/)