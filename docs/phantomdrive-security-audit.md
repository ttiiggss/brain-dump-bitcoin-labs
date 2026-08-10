# 🔒 PhantomDrive Security Audit

**Product:** [PhantomDrive](https://shop.rootkitlabs.com/products/phantomdrive) by Rootkit Labs
**Creator:** Ryan Walker ([o7-machinehum](https://github.com/o7-machinehum))
**Price:** $65 CAD (~$48 USD)
**Source:** [github.com/o7-machinehum/phantomdrive](https://github.com/o7-machinehum/phantomdrive) (MIT License)
**Audit Date:** August 2026
**Auditor:** Brain Dump / m3rkle_tree

---

## 📋 Product Overview

PhantomDrive is an open-source encrypted USB drive with a stealth mechanism. It appears as an ordinary 8GB flash drive, but hides a second encrypted partition. To unlock, you write a file containing `password:YourPassword` to the visible partition — the firmware intercepts USB writes, detects the password string, derives an AES key, and reveals the hidden storage.

### Hardware
- **SoC:** WCH CH569W (RISC-V microcontroller, ~$4.80 from LCSC)
- **Features:** USB 3.0, SDIO (connects to microSD card), hardware AES acceleration block
- **Storage:** User-provided microSD card (not included)
- **Programmable:** Over USB via `wch-ch56x-isp` library

### Cryptography Stack
- **Hash:** SHA-256 (custom implementation, FIPS 180-4 compliant)
- **KDF:** PBKDF2-HMAC-SHA256 (100,000 or 600,000 iterations, configurable at build time)
- **Cipher:** AES-256-CTR or AES-256-XTS (selectable at build time)
- **Salt:** 8 bytes derived from chip unique ID
- **Key:** Derived per-device, stored in RAM only after unlock

---

## 🔍 Source Code Analysis

### Files Reviewed
| File | Purpose | Assessment |
|---|---|---|
| `src/crypto.c` | SHA-256, PBKDF2, HMAC implementation | ✅ Clean, follows standards |
| `src/crypto.h` | Crypto constants & prototypes | ✅ Standard |
| `src/phantomdrive.c` | Lock/unlock state machine, password snoop | ⚠️ See findings below |
| `src/phantomdrive_aes_xts.c` | XTS encryption/decryption via hardware | ⚠️ See findings below |
| `src/msc_write.c` | USB Mass Storage write handler | ⚠️ See findings below |
| `src/phantomdrive_crypto.h` | Crypto unlock interface | ✅ Minimal, clean |
| `test/` | SHA256, PBKDF2, AES-CTR, AES-XTS test vectors | ✅ Verified against OpenSSL |

### What's Done Right ✅

1. **Standards-based cryptography.** SHA-256 implementation matches FIPS 180-4 exactly. PBKDF2 follows RFC 8018. AES-XTS is the correct mode for disk encryption (same as BitLocker, FileVault, LUKS).

2. **Hardware AES acceleration.** The CH569W's ECDC block performs AES in silicon, which is faster and avoids software timing side-channels. The firmware uses `ECDC_Excute()` and `ECDC_SelfDMA()` for in-place encrypt/decrypt.

3. **Password buffer zeroing.** After deriving the key, `memset(pending_pw, 0, sizeof(pending_pw))` clears the plaintext password from RAM. The snoop buffer is also zeroed after extracting the password.

4. **Test vectors against OpenSSL.** The test suite (`test/ctr_test.c`, `test/xts_test.c`) writes data through the device, removes the SD card, and decrypts it independently using OpenSSL AES-256-CTR/XTS with the same PBKDF2-derived key. This is proper cryptographic verification.

5. **Per-device salt.** The salt is derived from the chip's unique ID (`unique_id`), not hardcoded. This means two devices with the same password produce different keys.

6. **Configurable KDF iterations.** Build-time selection between 100K and 600K PBKDF2 iterations. 600K is strong for a hardware-accelerated KDF.

7. **Full open source.** MIT licensed, all firmware source available, hardware design files included (`ee/` directory). Reproducible builds via Makefile with configurable AES mode and KDF rounds.

8. **Genuinely stealthy.** The hidden partition is invisible to disk utilities — no encrypted headers, no extra capacity visible, no suspicious partitions. The OS sees a normal 8GB FAT drive.

---

## ⚠️ Security Findings

### CRITICAL 🔴

#### 1. No Data Integrity / Authentication
**Severity:** Critical
**Status:** Architectural limitation

Neither AES-CTR nor AES-XTS provides authentication. There is no HMAC, no AEAD mode, no checksum on the encrypted data. An attacker with physical access to the SD card can:
- **Bit-flip attacks:** In CTR mode, flipping a ciphertext bit flips the corresponding plaintext bit predictably. This allows targeted corruption of files.
- **XTS is better** but still provides no integrity guarantee. Modified ciphertext produces modified plaintext with no detection.

**Recommendation:** This is a fundamental design trade-off for in-line hardware encryption. Adding a HMAC layer would halve throughput and require a format change. For seed phrase storage (read-heavy, write-once), this is acceptable. For executable code storage, it's dangerous.

#### 2. No Firmware Signature Verification / Secure Boot
**Severity:** Critical
**Status:** Architectural limitation

The CH569W is programmable over USB via the `wch-ch56x-isp` library. The boot button + USB insertion puts it in ISP mode. There is:
- No secure boot
- No firmware signing
- No anti-rollback protection

An attacker with brief physical access could:
1. Hold the boot button, plug in USB
2. Flash malicious firmware that logs passwords
3. Return the device — the user would never know

**Recommendation:** This is the most serious threat for a device meant to protect secrets. The CH569W may not support secure boot at all (it's a general-purpose MCU, not a secure element). This is an inherent limitation of the hardware platform. **Do not use PhantomDrive in scenarios where an adversary may have unsupervised physical access.**

---

### HIGH 🟠

#### 3. Password Transmitted in Plaintext Over USB
**Severity:** High
**Status:** By design (platform-agnostic requirement)

The unlock mechanism writes `password:YourPassword` as a file to the drive. This means:
- **Host keyloggers** capture the password if typed
- **USB bus sniffers** capture the bulk transfer data
- **Filesystem monitoring** on the host sees the file content
- **Forensic tools** may recover the file from the decoy partition

The firmware does zero the buffer after snooping, but the data still travels through the host OS, USB controller, and USB cable in plaintext.

**Mitigation:** The creator explicitly designed this for platform-agnostic operation (no special software needed). This is the trade-off. If you use it, unlock on a trusted machine only.

#### 4. Content-Based Unlock Detection
**Severity:** High
**Status:** Documented in README

The firmware monitors ALL write data for the string `password:`. Any write containing this prefix — not just a file named `unlock.txt` — triggers password processing. This means:
- Accidental writes containing "password:" trigger unlock attempts
- A malicious host could probe the device by writing test passwords
- No rate limiting on failed attempts

The README explicitly warns: *"While the device is locked, any write data containing the string `password:` can be interpreted as an unlock attempt."*

**Recommendation:** Change the trigger string in a custom firmware build to something unique (e.g., `xk7q:` or a UUID) to reduce accidental triggers and make automated probing harder.

#### 5. WCH CH569W Hardware AES — Unvalidated
**Severity:** High (uncertainty)
**Status:** Hardware limitation

The AES operations use the CH569W's on-chip ECDC hardware block. This is a WCH (Nanjing Qinheng Microelectronics) chip — a Chinese IC vendor. The AES hardware block:
- Has **no known independent security validation** (no FIPS 140-2/3 certification, no Common Criteria)
- Has **no published side-channel analysis**
- Is from a vendor with **no track record in security-critical ICs**

If the AES hardware has implementation flaws (e.g., weak key scheduling, predictable output, side-channel leakage), the encryption could be weaker than expected. This is unknown — not confirmed vulnerable, but unvalidated.

**Recommendation:** For high-value secrets, layer additional encryption (e.g., VeraCrypt volume on the hidden partition) so you're not solely dependent on the CH569W's AES.

---

### MEDIUM 🟡

#### 6. Default PBKDF2 Iterations Too Low
**Severity:** Medium
**Status:** Configurable

The default build uses **100,000 PBKDF2 iterations**. For comparison:
- VeraCrypt: 500,000+ iterations
- 1Password: 650,000 iterations
- OWASP recommendation (2023+): 600,000 iterations

With hardware AES acceleration on the CH569W, the KDF runs fast — which means an attacker's brute-force also runs fast per guess. The 600K option is better, but 100K is the default.

**Recommendation:** **Always build with `KDF_ROUNDS=600000`.** Use a long, random password (20+ characters) to compensate for the relatively low iteration count.

#### 7. Salt Limited to 8 Bytes
**Severity:** Medium
**Status:** Architectural

The salt is 8 bytes derived from the chip's unique ID. This is:
- Predictable (tied to the chip, not random)
- Shorter than recommended (16+ bytes is standard for PBKDF2 salts)
- The same for every encryption on the same device

Since the salt is derived from `unique_id`, and `unique_id` is readable via `udevadm`, an attacker with the device knows the salt. This is acceptable (salts don't need to be secret), but the short length means rainbow table precomputation across devices is marginally easier.

#### 8. XTS Key Derivation — Same Password, Incremented Salt
**Severity:** Low-Medium
**Status:** By design

For AES-XTS mode, two keys are needed (data key + tweak key). The code derives them as:
```c
derive_key(password, pw_len, salt, xts_data_key);    // salt = device_id
salt[0]++;                                             // increment first byte
derive_key(password, pw_len, salt, xts_tweak_key);    // salt = device_id + 1
```

This is a reasonable approach, but both keys are derived from the same password with trivially different salts. A dedicated KDF (like HKDF with different info strings) would be more principled.

---

### LOW 🟢

#### 9. No Anti-Hammering / Lockout
**Severity:** Low
**Status:** Architectural

There is no attempt counter, no lockout, no delay between failed unlock attempts. An automated script could write thousands of passwords per second to the decoy partition. The KDF cost (100K-600K iterations) is the only brake, and at hardware speed that's still fast.

#### 10. `memset` Could Be Optimized Away
**Severity:** Low
**Status:** Code-level

The password clearing uses `memset(pending_pw, 0, sizeof(pending_pw))`. Compilers can optimize away dead-store `memset` calls. In practice, the `volatile` qualifier isn't used on `pending_pw`, and the code does access the buffer after clearing (length check), so the compiler likely keeps the `memset`. But `memset_s()` or a volatile sink would be more robust.

#### 11. No Tamper Evidence
**Severity:** Low
**Status:** Hardware limitation

The device has no tamper-evident seals, no epoxy, no intrusion detection. The PCB is accessible by removing the USB shell. Physical inspection reveals the CH569W (not a standard USB controller), which could tip off a sophisticated examiner.

---

## 🏗️ Architecture Assessment

```
┌──────────────────────────────────────────────────────┐
│                    HOST COMPUTER                      │
│  ┌─────────┐    ┌──────────────┐                      │
│  │  File    │───▶│  USB Stack   │                      │
│  │  Write   │    │  (Bulk Xfer) │                      │
│  └─────────┘    └──────┬───────┘                      │
└─────────────────────────┼────────────────────────────┘
                          │ USB 3.0
┌─────────────────────────┼────────────────────────────┐
│           PHANTOMDRIVE (CH569W)                       │
│                         │                              │
│  ┌──────────────────────▼─────────────────────┐       │
│  │        USB Mass Storage Controller          │       │
│  │            (MSC WRITE10)                    │       │
│  └──────────────────────┬─────────────────────┘       │
│                         │                              │
│  ┌──────────────────────▼─────────────────────┐       │
│  │     Password Snoop Engine                   │       │
│  │  (scans all writes for "password:" prefix)  │       │
│  └──────┬──────────────────┬──────────────────┘       │
│         │ LOCKED           │ UNLOCKED                  │
│         ▼                  ▼                           │
│  ┌────────────┐   ┌────────────────────┐              │
│  │ Decoy Only │   │ AES-XTS/CTR        │              │
│  │ (8GB FAT)  │   │ Encrypt/Decrypt    │              │
│  └────────────┘   │ (Hardware ECDC)    │              │
│                   └─────────┬──────────┘              │
│                             │                          │
│  ┌──────────────────────────▼────────────────┐        │
│  │         microSD Card (SDIO)               │        │
│  │  ┌──────────┐  ┌──────────────────────┐  │        │
│  │  │ Decoy    │  │ Encrypted Partition  │  │        │
│  │  │ (FAT32)  │  │ (AES-256 Ciphertext) │  │        │
│  │  └──────────┘  └──────────────────────┘  │        │
│  └───────────────────────────────────────────┘        │
└───────────────────────────────────────────────────────┘
```

---

## ⚖️ Threat Model Assessment

| Threat | Risk Level | PhantomDrive Resists? | Notes |
|---|---|---|---|
| Casual inspection (border, coworker) | ✅ Low | **Yes** | Appears as normal 8GB USB drive |
| Disk utility / forensics (software) | 🟡 Medium | **Yes** | No visible encrypted headers or extra partitions |
| Software keylogger on host | 🔴 High | **No** | Password written as plaintext file |
| USB hardware keylogger | 🔴 High | **No** | Bulk transfer data is plaintext |
| Physical access ( Evil Maid ) | 🔴 Critical | **No** | No secure boot, firmware replaceable |
| Offline SD card extraction | 🟡 Medium | **Partial** | Data is encrypted, but brute-force possible |
| Compelled disclosure (rubber-hose) | 🟡 Medium | **Partial** | Decoy partition provides plausible deniability |
| $5 wrench attack | 🔴 High | **No** | Like all crypto, social engineering defeats it |
| Supply chain (pre-shipped malware) | 🟡 Medium | **Partial** | Open source allows self-build & verification |

---

## 📊 Comparison to Alternatives

| Feature | PhantomDrive | VeraCrypt (Software) | Ledger Nano S | Standard USB + LUKS |
|---|---|---|---|---|
| Stealth / hidden volume | ✅ Yes | ✅ Yes (hidden volume) | ❌ No | ❌ No |
| Hardware encryption | ✅ Yes (CH569W) | ❌ No (CPU) | ✅ Yes (secure element) | ❌ No (CPU) |
| Platform-agnostic unlock | ✅ Yes | ❌ No (needs software) | ❌ No (needs app) | ❌ No (needs software) |
| Secure element | ❌ No | ❌ No | ✅ Yes (EAL5+) | ❌ No |
| Secure boot / firmware signing | ❌ No | N/A | ✅ Yes | ❌ No |
| Professional audit | ❌ No | ✅ Yes (multiple) | ✅ Yes (multiple) | ✅ Yes (LUKS) |
| Open source | ✅ Yes | ✅ Yes | ✅ Partial | ✅ Yes |
| Price | $65 CAD | Free | $79+ | Free |
| Anti-tamper | ❌ No | N/A | ✅ Yes | ❌ No |

---

## 🎯 Verdict: Is It Worth Adopting?

### For Brain Dump / m3rkle_tree's Use Case

**Use case:** Storing Bitcoin seed phrases, cold storage backups, sensitive documents.

### Recommendation: ⚠️ **Adopt with caveats — NOT for high-value single points of failure**

**Good for:**
- ✅ Stealth transport of non-critical encrypted data
- ✅ Plausible deniability (decoy partition)
- ✅ Educational tool for the Brain Dump labs (teaching hardware encryption concepts)
- ✅ Secondary backup layer (not your only copy)
- ✅ Demo/unit for learning about USB mass storage security

**Do NOT use for:**
- ❌ Your only copy of a seed phrase (use steel + multisig instead)
- ❌ Storage of funds you can't afford to lose
- ❌ Scenarios where an adversary may have unsupervised physical access
- ❌ High-security opsec where firmware integrity matters

### Scoring

| Category | Score | Notes |
|---|---|---|
| **Cryptography** | 7/10 | Standards-based, hardware AES. No integrity, unvalidated chip. |
| **Stealth** | 9/10 | Genuinely invisible hidden partition. Clever unlock mechanism. |
| **Physical Security** | 2/10 | No secure boot, no tamper evidence, firmware replaceable. |
| **Openness** | 10/10 | Fully open source, MIT licensed, hardware designs included. |
| **Maturity** | 4/10 | 67 commits, no professional audit, small community. |
| **Value** | 8/10 | $65 CAD is cheap for what it does. |
| **Overall** | **5.5/10** | Clever concept, well-executed for a hobby project, but not production-grade security. |

### Bottom Line

PhantomDrive is a **brilliant proof-of-concept** that solves a real problem (platform-agnostic stealth storage) with elegant engineering. The crypto implementation is solid and properly tested. But it has fundamental security gaps — no secure boot, no firmware signing, no data integrity — that make it unsuitable as a primary security device.

**For Brain Dump's curriculum:** Excellent teaching tool. Students can flash custom firmware, modify the crypto, test attack vectors, and learn about hardware security trade-offs. This is exactly the kind of project that makes Hack-the-Box-style labs compelling.

**For personal Bitcoin storage:** Layer it. Use PhantomDrive as one factor in a broader scheme — e.g., store a VeraCrypt volume inside the hidden partition for double encryption, and never rely on it as your only backup. Your seed phrase should be on steel, in a multisig, with geographically distributed backups.

---

## 🔗 References

- [PhantomDrive Shop](https://shop.rootkitlabs.com/products/phantomdrive)
- [GitHub Source](https://github.com/o7-machinehum/phantomdrive)
- [Hackaday Coverage](https://hackaday.com/2026/08/06/phantomdrive-keeps-your-secrets-out-of-sight/)
- [Tom's Hardware Coverage](https://www.tomshardware.com/pc-components/usb-flash-drives/open-source-stealth-usb-hides-an-encrypted-partition-behind-an-8gb-decoy-drive-phantom-drive-appears-as-a-regular-usb-stick-until-you-create-a-text-file-to-unlock-the-hidden-data)
- [CH569W Datasheet (WCH)](https://www.wch-ic.com/products/CH569.html)
- [NIST FIPS 180-4 (SHA-256)](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf)
- [RFC 8018 (PBKDF2)](https://datatracker.ietf.org/doc/html/rfc8018)
- [IEEE 1619 (AES-XTS)](https://en.wikipedia.org/wiki/Disk_encryption_theory#XTS)

---

*This audit was conducted via source code review and public documentation analysis. No physical device was tested. This is not a professional security audit — PhantomDrive's own README states the code "has not been professionally audited." Treat this assessment as informed opinion, not certification.*
