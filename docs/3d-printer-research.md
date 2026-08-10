# 🖨️ 3D Printer Research — Entropia Seed Tablet Replica

Research into the best 3D printer for producing a replica of the [Entropia Seed Tablets](https://shopbitcoin.com.au/products/entropia-seed-tablets-aussie-edition) — a BIP39 lottery system by SeedSigner.

---

## 📋 What We're Replicating

The Entropia seed tablets are a **3D-printed BIP39 lottery system** by SeedSigner. Key specs from their open-source repo ([github.com/SeedSigner/SeedPills](https://github.com/SeedSigner/SeedPills)):

- **1,024 pills** (2,048 words, printed double-sided)
- Each pill is **~11mm × 7.5mm × 3mm** with **3.5pt raised text** on both sides
- Pills are printed in **interconnected sheets** (8×16 grids) for bed adhesion
- **24+ hours** to print a full set
- Generated via Python → OpenSCAD → STL
- Retail: **$150 AUD** for the full set + apothecary jar
- Printed in **Bitcoin orange PLA**

### The Challenge

The critical requirement for replicating this product:
- **Tiny text detail** at 3.5pt on pill-shaped objects
- **Reliable printing** for 24+ hours straight
- **Perfect bed adhesion** for interconnected grid sheets
- **Consistent quality** across 1,024 individual pieces

---

## 🏆 Recommendation: Bambu Lab P1S

**~$699 USD** | [bambulab.com](https://bambulab.com)

This is the sweet spot for this project.

| Requirement | Why P1S Delivers |
|---|---|
| **Tiny text detail** | CoreXY kinematics + input shaping = crisp 3.5pt text on 11mm pills |
| **24+ hour reliability** | Enclosed chamber keeps temps stable; 2.1% failure rate in 240+ hour testing |
| **Bed adhesion for grids** | Lidar-assisted first layer on PEI plate = sheets stick perfectly |
| **Large enough bed** | 256×256mm fits all 8 sheets of 16×8 pills with room to spare |
| **Multi-color option** | Add AMS ($359) for dual-color pills (orange body + contrasting text) — no manual swaps |
| **Auto-calibration** | Set it and walk away — critical for a 24hr print |
| **PLA is its sweet spot** | The pills are PLA — this printer excels at exactly that |

### What to Buy

| Item | Price |
|---|---|
| Bambu Lab P1S | $699 |
| Bambu AMS (optional, for 2-color pills) | $359 |
| Bambu PLA filament in orange | ~$25/spool |
| **Total** | **$699 (single-color) or $1,058 (multi-color)** |

---

## 📊 Full Printer Lineup Considered

| Printer | Price | Verdict for Seed Pills |
|---|---|---|
| **Bambu Lab P1S** ✅ | $699 | **Best pick.** Enclosed CoreXY, reliable, AMS-ready, proven track record |
| Bambu Lab X2D | $699 | Interesting — dual nozzle means zero-waste 2-color pills. New though, less proven |
| Bambu Lab A2L | $399 | Open-frame bed-slinger. Cheaper but less stable for 24hr prints. Risky for detail |
| Bambu Lab H2C | $2,199 | Overkill. Multi-material flagship, way more than needed |
| Prusa Core One+ | $1,203 | Excellent printer, open-source, heated chamber. But 2× the price for same result on PLA |
| Prusa MK4S | $629+ | Great but bed-slinger + no enclosure = worse for long detail prints |

---

## 🖨️ P1S Specs

| Spec | Detail |
|---|---|
| **Price** | $699 USD |
| **Chassis** | CoreXY |
| **Build volume** | 256 × 256 × 256mm |
| **Enclosed** | Yes (passive) |
| **Hotend max temp** | 300°C |
| **Bed leveling** | Lidar |
| **Multicolor** | AMS (4 spools, chainable to 16) |
| **Built-in camera** | 720p |
| **WiFi** | 2.4GHz |
| **Max speed** | 500 mm/s |
| **Best for** | ABS-capable enthusiast, PLA/PETG production |
| **Materials** | PLA ✓, PETG ✓, TPU ✓, ABS ✓, ASA ✓ (small), PC-blend △ |

### P1S Strengths
- CoreXY chassis means high-speed prints stay accurate
- Passive enclosure handles ABS, ASA, and PC-blends without delamination
- Lidar leveling adapts first layer to PEI plate texture automatically
- 720p camera streams to Bambu Handy app for remote monitoring
- Passive enclosure reaches 50-55°C chamber after 30 min preheat (bed at 110°C)
- Sufficient for ABS at 100°C bed / 240°C hotend with door closed
- 2.1% failure rate across 240+ hours of testing

### P1S Limitations
- Passive enclosure (not actively heated) — parts over 100mm tall on ABS may warp
- No active chamber heating (X1C/X2D have this)
- 720p camera (not 1080p)
- 2.4GHz WiFi only (no 5GHz)

---

## 🔄 Alternative: Bambu X2D for Dual-Color

The **X2D ($699)** has two nozzles and could print two-color pills with **zero purge waste**. The AMS system wastes filament on every color swap (adds up fast on 1,024 tiny parts). If dual-color is a priority, the X2D eliminates that waste entirely.

**Trade-off:** Brand new with less community validation than the P1S.

---

## 🎯 Production Workflow for Seed Pills

The SeedPills repo gives you everything — the Python generator, the OpenSCAD scripts, the STL workflow. With a P1S:

### Step-by-Step

1. **Clone** `github.com/SeedSigner/SeedPills`
2. Run `seedpills.py` to generate OpenSCAD code for each 8×16 sheet
3. Render in OpenSCAD → export STL
4. Slice in **Bambu Studio** (free) with these settings:

### Recommended Print Settings

| Setting | Value | Reason |
|---|---|---|
| Layer height | 0.2mm | Good text detail without 48hr print times |
| Hotend temp | 210°C | Optimal for PLA text clarity |
| Bed temp | 60°C | Standard PLA adhesion |
| Filament | Orange PLA | Bitcoin orange (Bambu sells matching spools) |
| Adhesion | Brim or mouse-ears | Extra grip on sheet corners |

5. **Print** — ~3hrs per sheet, 8 sheets = ~24hrs total
6. Break pills apart from the interconnecting tabs

### Dual-Color Upgrade (with AMS)

If you get the AMS, you can print the pill body in orange and the text in white/black simultaneously. Each pill would have a contrasting letter that pops — a premium upgrade over the original single-color Entropia.

---

## 📦 BOM (Bill of Materials)

| Item | Qty | Price | Notes |
|---|---|---|---|
| Bambu Lab P1S | 1 | $699 | Core printer |
| Bambu AMS (optional) | 1 | $359 | For dual-color pills |
| PLA Filament — Orange | 2-3 spools | ~$25/each | Bitcoin orange |
| PLA Filament — White/Black (optional) | 1 spool | ~$25 | For contrasting text with AMS |
| Apothecary jar (display) | 1 | ~$15-30 | For the finished product presentation |
| PEI build plate | 1 spare | ~$30 | In case of wear |

---

## 🔗 References

- [Entropia Product Page (Shop Bitcoin AU)](https://shopbitcoin.com.au/products/entropia-seed-tablets-aussie-edition)
- [SeedPills Open Source Repo](https://github.com/SeedSigner/SeedPills)
- [BIP39 Word List](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt)
- [Bambu Lab P1S](https://bambulab.com)
- [Bambu Lab Compare All Printers](https://bambulab.com/en/compare)

---

*Research conducted August 2026. Prices and availability subject to change.*
