# Neighborhood WISP — Technical Implementation Plan

**Step-by-step guide for building a neighborhood wireless internet service provider. Hardware selection, network architecture, router configuration, antenna installation, client onboarding, monitoring, and support.**

---

## Phase 0: Pre-Installation Checklist

### Before You Buy Anything

- [ ] **Review ISP Terms of Service** — Check for sharing/reselling clauses
- [ ] **Upgrade to business account** (if ToS prohibits residential sharing)
- [ ] **Survey 10-20 neighbors** — Gauge interest, confirm line-of-sight
- [ ] **Calculate breakeven** — 3-5 neighbors minimum for viability
- [ ] **Check local regulations** — HOA, city ordinances, antenna restrictions
- [ ] **Confirm your connection** — Minimum 500 Mbps down, 100 Mbps up (1 Gbps down recommended)

---

## Phase 1: Hardware Procurement

### Recommended Hardware for 3-5 Neighbors

| Component | Recommendation | Quantity | Approx Cost |
|-----------|----------------|----------|-------------|
| **Main Router** | Ubiquiti EdgeRouter 4 | 1 | $200 |
| **PtP Antennas** | Ubiquiti NanoStation 5AC Loco | 3-5 | $300-500 |
| **PoE Switch** | Ubiquiti UniFi USW Flex Mini | 1 | $80 |
| **Roof Mounts** | Ubiquiti Wall/Pole Mount | 3-5 | $45-75 |
| **Ethernet Cables** | Cat6 outdoor, 50ft each | 3-5 | $60-100 |
| **Lightning Arrestors** | Ubiquiti ETH-SP-G2 | 3-5 | $60-100 |
| **Cable Management** | Zip ties, cable clips, conduit | 1 set | $30-50 |
| **Optional** | Gl.iNet Beryl (mesh nodes) | 3-5 | $240-400 |

**Total:** ~$775-1,405 for 3-5 neighbors

### Alternative: MikroTik Stack

| Component | Recommendation | Quantity | Approx Cost |
|-----------|----------------|----------|-------------|
| **Main Router** | MikroTik CCR1009-8G-1S-1S+ | 1 | $350 |
| **PtP Antennas** | MikroTik LHG XL 5 ac | 3-5 | $450-750 |
| **PoE Switch** | MikroTik CRS305-1G-4S+IN | 1 | $120 |
| **Mounts/Cables** | Same as above | - | $135-225 |
| **Total** | | | ~$1,055-1,445 |

### Where to Buy

- **USA:** Amazon, Ubiquiti Direct Store, Micro Center
- **Australia:** Mwave, PLE Computers, Ubiquiti Australia
- **UK:** Amazon UK, Ebuyer, Scan Computers
- **Canada:** Amazon Canada, Newegg Canada, Memory Express

---

## Phase 2: Network Architecture Design

### Network Topology

```
                    Your Home (Main Router)
                              │
                    ┌─────────┴─────────┐
                    │                   │
              VLAN 10 (Your LAN)   VLAN 20 (WISP)
                    │                   │
              Your Devices      ┌──────┴──────┐
                               │             │
                         Neighbor A     Neighbor B
                               │             │
                         PtP Antenna    PtP Antenna
```

### VLAN Design

| VLAN ID | Name | Purpose | Bandwidth Allocation |
|---------|------|---------|---------------------|
| 10 | Your LAN | Your devices (personal use) | 70% |
| 20 | WISP Network | Neighbor access (shared) | 30% |
| 30 | Management | Router/AP management access only | Admin only |

### IP Addressing Plan

| Subnet | Range | Devices |
|--------|-------|---------|
| 192.168.1.0/24 | 192.168.1.1-255 | Your LAN (VLAN 10) |
| 192.168.20.0/24 | 192.168.20.1-255 | WISP Network (VLAN 20) |
| 192.168.30.0/24 | 192.168.30.1-255 | Management (VLAN 30) |

---

## Phase 3: Router Configuration (Ubiquiti EdgeRouter 4)

### Step 3.1: Access the Router

1. Connect your computer to the router via Ethernet
2. Navigate to `https://192.168.1.1` (default EdgeRouter address)
3. Login (default: ubnt/ubnt)
4. **Immediately change the password**

### Step 3.2: Configure VLANs

**Via CLI:**

```bash
configure

# Create VLAN 10 (Your LAN)
set interfaces ethernet eth0 vif 10 description "Your LAN"
set interfaces ethernet eth0 vif 10 address 192.168.1.1/24

# Create VLAN 20 (WISP Network)
set interfaces ethernet eth0 vif 20 description "WISP Network"
set interfaces ethernet eth0 vif 20 address 192.168.20.1/24

# Create VLAN 30 (Management)
set interfaces ethernet eth0 vif 30 description "Management"
set interfaces ethernet eth0 vif 30 address 192.168.30.1/24

commit
save
exit
```

**Via Web UI:**
1. Dashboard → Wizards → VLAN
2. Add VLAN 10, 20, 30 with above details
3. Apply

### Step 3.3: Configure DHCP

**VLAN 10 (Your LAN):**

```bash
configure

set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 default-router 192.168.1.1
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 dns-server 8.8.8.8
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 dns-server 8.8.4.4
set service dhcp-server shared-network-name LAN subnet 192.168.1.0/24 start 192.168.1.38 stop 192.168.1.243

commit
save
exit
```

**VLAN 20 (WISP Network):**

```bash
configure

set service dhcp-server shared-network-name WISP subnet 192.168.20.0/24
set service dhcp-server shared-network-name WISP subnet 192.168.20.0/24 default-router 192.168.20.1
set service dhcp-server shared-network-name WISP subnet 192.168.20.0/24 dns-server 8.8.8.8
set service dhcp-server shared-network-name WISP subnet 192.168.20.0/24 start 192.168.20.38 stop 192.168.20.243

commit
save
exit
```

**VLAN 30 (Management):**

```bash
configure

set service dhcp-server shared-network-name MGMT subnet 192.168.30.0/24
set service dhcp-server shared-network-name MGMT subnet 192.168.30.0/24 default-router 192.168.30.1
set service dhcp-server shared-network-name MGMT subnet 192.168.30.0/24 dns-server 8.8.8.8
set service dhcp-server shared-network-name MGMT subnet 192.168.30.0/24 start 192.168.30.38 stop 192.168.30.243

commit
save
exit
```

### Step 3.4: Configure QoS (Quality of Service)

**Policy: 70% to your LAN, 30% to WISP**

```bash
configure

# Create traffic shaper
set traffic-policy shaper WAN_IN description "Limit WISP traffic to 30%"
set traffic-policy shaper WAN_IN bandwidth 100mbit
set traffic-policy shaper WAN_IN class 10 bandwidth 70mbit
set traffic-policy shaper WAN_IN class 10 match VLAN10
set traffic-policy shaper WAN_IN match VLAN10 ip protocol vlan
set traffic-policy shaper WAN_IN match VLAN10 vlan 10
set traffic-policy shaper WAN_IN class 20 bandwidth 30mbit
set traffic-policy shaper WAN_IN class 20 match VLAN20
set traffic-policy shaper WAN_IN match VLAN20 ip protocol vlan
set traffic-policy shaper WAN_IN match VLAN20 vlan 20

# Apply to WAN interface
set interfaces ethernet eth1 traffic-policy out WAN_IN

commit
save
exit
```

### Step 3.5: Configure Firewall Rules

**Block inter-VLAN communication (neighbors can't see each other):**

```bash
configure

# Block VLAN 20 from accessing VLAN 10 and 30
set firewall name VLAN20_TO_VLAN10 default-action accept
set firewall name VLAN20_TO_VLAN10 rule 10 action drop
set firewall name VLAN20_TO_VLAN10 rule 10 description "Block access to your LAN"
set firewall name VLAN20_TO_VLAN10 rule 10 destination address 192.168.1.0/24

set firewall name VLAN20_TO_VLAN30 default-action accept
set firewall name VLAN20_TO_VLAN30 rule 10 action drop
set firewall name VLAN20_TO_VLAN30 rule 10 description "Block access to management"
set firewall name VLAN20_TO_VLAN30 rule 10 destination address 192.168.30.0/24

# Apply rules
set interfaces ethernet eth0 vif 20 firewall in name VLAN20_TO_VLAN10
set interfaces ethernet eth0 vif 20 firewall in name VLAN20_TO_VLAN30

commit
save
exit
```

**Block specific ports (P2P):**

```bash
configure

set firewall name WISP_BLOCK default-action accept
set firewall name WISP_BLOCK rule 10 action drop
set firewall name WISP_BLOCK rule 10 description "Block BitTorrent"
set firewall name WISP_BLOCK rule 10 destination port 6881-6889
set firewall name WISP_BLOCK rule 10 protocol tcp_udp

set interfaces ethernet eth0 vif 20 firewall in name WISP_BLOCK

commit
save
exit
```

---

## Phase 4: Antenna Installation

### Step 4.1: Site Survey

**For each neighbor:**

1. **Check line-of-sight** — Can you see their roof from yours?
2. **Measure distance** — Use Google Maps (distance measurement tool) or laser rangefinder
3. **Identify obstacles** — Trees, buildings, hills (signal degrades with obstacles)
4. **Choose mounting location** — Chimney, roof peak, or pole mount (highest point)
5. **Mark cable route** — Where will Ethernet cable run from antenna to router?

### Step 4.2: Mount the Antenna

**Tools needed:**
- Drill with masonry bit (for brick/concrete)
- Mounting bracket (included with NanoStation)
- Weatherproof sealant (silicone)
- Cable clips or conduit
- Wire fish tape (for running cable through walls)

**Steps:**

1. **Mark mounting holes** — Hold antenna bracket in desired location
2. **Drill pilot holes** — Use appropriate bit for mounting surface
3. **Insert wall anchors** — If mounting to brick/concrete
4. **Mount the bracket** — Secure with included screws
5. **Attach antenna** — Slide NanoStation onto bracket, tighten set screws
6. **Apply sealant** — Around mounting holes to prevent water ingress

### Step 4.3: Run Ethernet Cable

**Option A: Through the roof (most secure)**

1. **Drill entry hole** — Near antenna mounting location
2. **Install wall passthrough** — Weatherproof cable gland
3. **Run cable** — From antenna, through passthrough, to attic/inside
4. **Seal hole** — Apply silicone around passthrough

**Option B: Down the wall (easier, less secure)**

1. **Drill exit hole** — Near roofline
2. **Install cable clips** — Every 2-3 feet along the wall
3. **Run cable** — From antenna, down the wall, to entry point
4. **Seal entry hole** — Apply silicone

### Step 4.4: Connect to PoE Switch

**PoE setup:**

1. **Plug antenna Ethernet cable** → PoE switch port (labeled POE)
2. **Plug PoE switch** → Router VLAN 20 port
3. **Power on** — PoE switch injects power to antenna (12-48V, 802.3af/at)

**Test connectivity:**

1. **Access antenna UI** — Default: `192.168.1.20` (check NanoStation sticker)
2. **Login** — Default: ubnt/ubnt
3. **Signal strength check** — Should be -50 to -70 dBm for good connection
4. **Alignment adjustments** — Fine-tune antenna direction for maximum signal

### Step 4.5: Neighbor-Side Installation

**Repeat steps 4.1-4.4** at each neighbor's house.

**Neighbor receives:**
- NanoStation antenna
- Ethernet cable (50ft outdoor Cat6)
- PoE injector (if not using PoE switch at their end)
- Mounting hardware

**You provide:**
- Installation assistance (optional)
- Pre-configured antenna settings

---

## Phase 5: Neighbor Onboarding

### Step 5.1: Authentication Options

**Option A: WPA2-Enterprise (RADIUS)** — Most secure, but requires RADIUS server

**Option B: Pre-shared keys per neighbor** — Simpler, less secure

**Option C: Captive portal** — Neighbors log in via web page (more user-friendly)

### Step 5.2: Pre-Shared Key Setup (Recommended for MVP)

**Generate unique password for each neighbor:**

```bash
# Use a password manager or random password generator
# Example: openssl rand -base64 12
# Output: X7kL9mN3pQ2rW8
```

**Configure on EdgeRouter:**

```bash
configure

# Set Wi-Fi SSID and password (if using Ubiquiti UniFi AP)
set wireless-access-point profile WISP ssid "NeighborhoodWISP"
set wireless-access-point profile WISP security wpa2 psk "X7kL9mN3pQ2rW8"

# Apply to VLAN 20
set wireless-access-point ap-group WISP ap-profile WISP
set wireless-access-point ap-group WISP vlan 20

commit
save
exit
```

### Step 5.3: Rate Limiting Per Client

**Limit each neighbor to 100 Mbps down, 50 Mbps up:**

```bash
configure

# Create traffic shaper for client rate limiting
set traffic-policy shaper CLIENT_IN bandwidth 100mbit
set traffic-policy shaper CLIENT_OUT bandwidth 50mbit

# Apply to each client (example: client at 192.168.20.50)
set traffic-policy shaper CLIENT_IN class 10 match CLIENT1 source address 192.168.20.50
set traffic-policy shaper CLIENT_OUT class 10 match CLIENT1 destination address 192.168.20.50

# Apply to VLAN 20
set interfaces ethernet eth0 vif 20 traffic-policy in CLIENT_IN
set interfaces ethernet eth0 vif 20 traffic-policy out CLIENT_OUT

commit
save
exit
```

### Step 5.4: Acceptable Use Policy (AUP)

**Create and share AUP document:**

```markdown
# Neighborhood WISP Acceptable Use Policy

## Allowed Activities
- General web browsing
- Streaming video/music
- Email and messaging
- Online gaming
- Remote work

## Prohibited Activities
- Illegal downloading/sharing
- Bandwidth-intensive P2P (BitTorrent, etc.)
- Hacking, malware distribution
- Spam, phishing, fraud
- Any activity violating local law

## Consequences
- First violation: Warning
- Second violation: Temporary suspension (24 hours)
- Third violation: Permanent termination

## Contact
For support: [Your phone/email]
Business hours: [Your hours]
Response SLA: [Your SLA, e.g., 4 hours]

## By using this service, you agree to these terms.
```

**Share AUP:**
- Email PDF to each neighbor
- Include in welcome packet
- Post on community board (if applicable)

---

## Phase 6: Monitoring & Support

### Step 6.1: Bandwidth Monitoring

**Tools:**

| Tool | Cost | Features |
|------|------|----------|
| **Ubiquiti UNMS** | Free | Device management, bandwidth graphs, alerts |
| **MikroTik The Dude** | Free | Network monitoring, custom dashboards |
| **PRTG Network Monitor** | Free (100 sensors) | Comprehensive monitoring, alerting |
| **Grafana + Prometheus** | Free | Custom dashboards, metric collection |

**Recommended: Ubiquiti UNMS (free)**

1. **Create UNMS account** — https://unms.ui.com
2. **Add devices** — EdgeRouter, NanoStations
3. **Set up bandwidth graphs** — Per client, per VLAN
4. **Configure alerts** — High bandwidth usage, offline devices, congestion

### Step 6.2: Alerting Setup

**Alert on:**

- **High bandwidth usage** — > 80% of allocated limit for > 15 minutes
- **Offline devices** — Antenna/router down for > 5 minutes
- **Congestion** — Average latency > 100ms for > 10 minutes
- **Abuse detection** — Sudden traffic spikes (possible P2P)

**Alert methods:**
- Email
- SMS (via Twilio or similar)
- Push notification (UNMS mobile app)

### Step 6.3: Support Protocol

**Contact information:**
- Phone: [Your number]
- Email: [Your email]
- Preferred method: [SMS/call/email]

**Response SLA:**
- **Urgent** (no internet): 4 hours
- **Non-urgent** (slow speeds): 24 hours
- **Planned maintenance**: 48 hours notice

**Support workflow:**
1. Neighbor reports issue → You receive alert/contact
2. Diagnose (check UNMS, ping test, signal strength)
3. Fix (reset device, adjust alignment, rate limit adjustment)
4. Follow up (confirm resolution, ask for feedback)

### Step 6.4: Troubleshooting Guide

**Common Issues:**

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| **No internet** | Router offline, ISP outage | Check router status, verify ISP connection |
| **Slow speeds** | Congestion, rate limiting too aggressive | Check UNMS bandwidth graphs, adjust QoS |
| **Intermittent connection** | Poor signal, antenna misalignment | Check signal strength, realign antenna |
| **Can't connect to Wi-Fi** | Wrong password, AP offline | Verify password, check AP status |
| **Can see other neighbors' devices** | Firewall rules not applied | Verify VLAN isolation rules |

**Diagnostic commands (EdgeRouter CLI):**

```bash
# Check interface status
show interfaces ethernet

# Check DHCP leases
show dhcp server leases

# Check NAT translations
show nat translations

# Ping test
ping 8.8.8.8

# Traceroute
traceroute google.com
```

---

## Phase 7: Security Hardening

### Step 7.1: Router Security

**Change default credentials:**
- [ ] Change router admin password (use strong password: 16+ characters, mixed case, numbers, symbols)
- [ ] Disable remote admin (only allow LAN management)
- [ ] Enable two-factor authentication (if supported)

**Disable unused services:**
```bash
configure
set system services ssh disable
set system services telnet disable
set system services https disable
set system services http disable
commit
save
exit
```

**Enable firewall:**
```bash
configure
set firewall all-ping enable
set firewall broadcast-ping disable
set firewall ipv6-receive-redirects disable
set firewall ipv6-src-route disable
set firewall ip-src-route disable
set firewall log-martians enable
commit
save
exit
```

### Step 7.2: Antenna Security

**Update firmware:**
- [ ] Update EdgeRouter to latest firmware
- [ ] Update NanoStations to latest firmware
- [ ] Enable auto-update (if supported)

**Secure antenna access:**
- [ ] Change NanoStation admin password
- [ ] Disable remote management on NanoStations
- [ ] Enable only management from LAN (VLAN 30)

### Step 7.3: Network Security

**Enable intrusion detection:**
- Consider implementing SNORT or Suricata (advanced)
- Monitor for suspicious traffic patterns

**Regular audits:**
- Monthly bandwidth review per client
- Quarterly security audit (firewall rules, access logs)
- Annual hardware review (antenna condition, cable integrity)

---

## Phase 8: Testing & Validation

### Step 8.1: Network Performance Testing

**Speed tests:**
- Use Speedtest.net from your LAN (should match ISP speed)
- Use Speedtest.net from neighbor connection (should match rate limit)
- Test multiple times throughout the day (peak vs off-peak)

**Latency tests:**
```bash
# From your LAN
ping 8.8.8.8

# From neighbor connection
ping 8.8.8.8

# Target: < 50ms average latency
```

### Step 8.2: VLAN Isolation Test

**Test that neighbors can't see each other:**

1. **Neighbor A** tries to ping Neighbor B: `ping 192.168.20.X`
2. **Should fail** (request timeout)
3. **If succeeds** → Firewall rules not applied correctly

### Step 8.3: QoS Validation

**Test bandwidth allocation:**

1. **Run speed test from your LAN** → Should get 70% of total bandwidth
2. **Run speed test from neighbor** → Should get 30% of total bandwidth
3. **Run concurrent tests** → Verify priorities are respected

### Step 8.4: Disaster Recovery Test

**Simulate outage:**
1. **Unplug main router** → Test failover (if redundant)
2. **Unplug PoE switch** → Test antenna power recovery
3. **Reboot router** → Verify auto-recovery

---

## Phase 9: Documentation & Handoff

### Step 9.1: Create Network Diagram

**Example:**

```
                    Internet (1 Gbps)
                           │
                    EdgeRouter 4
                    192.168.1.1 (VLAN 10)
                    192.168.20.1 (VLAN 20)
                    192.168.30.1 (VLAN 30)
                           │
                    PoE Switch
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    Neighbor A        Neighbor B        Neighbor C
    192.168.20.50    192.168.20.51    192.168.20.52
          │                │                │
    NanoStation       NanoStation       NanoStation
          │                │                │
    PtP Link         PtP Link          PtP Link
          │                │                │
    Your Roof        Your Roof         Your Roof
```

### Step 9.2: Configuration Backup

**Save EdgeRouter configuration:**

```bash
configure
# Export configuration
export file backup-config.edge
exit

# Download from router:
# Dashboard → System → Backup Configuration
```

**Save NanoStation configurations:**

```bash
# From NanoStation UI:
# System → Backup Configuration → Download
```

**Store backups:**
- Local USB drive
- Cloud storage (Google Drive, Dropbox)
- Print hardcopy for reference

### Step 9.3: Create Support Documentation

**Create neighbor welcome packet:**

```markdown
# Welcome to Neighborhood WISP

## Getting Connected

1. Connect your device to Wi-Fi:
   - SSID: NeighborhoodWISP
   - Password: [Your password]

2. Your internet is active!

## Troubleshooting

**Can't connect to Wi-Fi?**
- Check that your device Wi-Fi is turned on
- Verify password (case-sensitive)
- Restart your device

**Slow speeds?**
- Check your signal strength (should be -50 to -70 dBm)
- Restart your router (if you have one)
- Contact support: [Your phone/email]

**No internet?**
- Check if you can reach the router at 192.168.20.1
- Restart your device
- Contact support: [Your phone/email]

## Support

- Phone: [Your number]
- Email: [Your email]
- Response SLA: [Your SLA]
- Business hours: [Your hours]

## Acceptable Use Policy

[Include AUP from Phase 5.4]

## Your Details

- Your IP address: [Assign IP, e.g., 192.168.20.50]
- Rate limit: [Your limit, e.g., 100 Mbps down / 50 Mbps up]
- Assigned date: [Date]

## Thank you for joining Neighborhood WISP!
```

---

## Phase 10: Scaling Up

### When to Scale

**Signs it's time to expand:**

- **Consistent demand** — 5+ neighbors interested
- **Revenue > costs** — You're consistently profitable
- **Capacity available** — Your connection has bandwidth headroom
- **Support manageable** — You can handle support within SLA

### Scaling Options

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **Add more PtP links** | Direct connections, reliable | Limited by line-of-sight | $100-150 per link |
| **Upgrade to PtMP** | Serve many neighbors with one antenna | More complex, alignment critical | $300-500 for sector antenna |
| **Deploy mesh network** | Good for scattered houses | Bandwidth degrades with hops | $60-80 per node |
| **Upgrade ISP connection** | More bandwidth available | Higher monthly cost | +$50-100/mo |

### PtMP Implementation (Serving 10-20 Neighbors)

**Hardware:**
- Ubiquiti airMAX Sector Antenna (120° coverage)
- Multiple NanoStations (one per neighbor)
- More powerful PoE switch (16-24 ports)

**Configuration:**
- Same VLAN architecture
- Increase bandwidth allocation (e.g., 60/40 split)
- Implement per-client rate limiting (as in Phase 5.3)

---

## Summary Timeline

| Phase | Duration | Effort |
|-------|----------|--------|
| Phase 0: Pre-Installation | 1-2 weeks | Low |
| Phase 1: Hardware Procurement | 1-2 weeks (delivery) | Low |
| Phase 2: Network Architecture Design | 2-3 days | Medium |
| Phase 3: Router Configuration | 1-2 days | Medium |
| Phase 4: Antenna Installation | 1-2 days (per neighbor) | High |
| Phase 5: Neighbor Onboarding | 1 day (per neighbor) | Low |
| Phase 6: Monitoring & Support | Ongoing | Medium |
| Phase 7: Security Hardening | 1 day | Medium |
| Phase 8: Testing & Validation | 2-3 days | Medium |
| Phase 9: Documentation & Handoff | 1-2 days | Low |

**Total time to launch:** 3-5 weeks (for 3-5 neighbors)

---

## References

- [Ubiquiti EdgeRouter Documentation](https://help.ui.com/hc/en-us/articles/205227500-EdgeRouter-Configuration-Examples)
- [Ubiquiti airMAX PtP Setup Guide](https://help.ui.com/hc/en-us/articles/204976094-airMAX-Point-to-Point-Link)
- [MikroTik RouterOS Documentation](https://wiki.mikrotik.com/wiki/Manual:TOC)
- [WISP Tech Support Forum](https://wispforums.com/)
- [OpenWRT Documentation](https://openwrt.org/)

---

## Next Steps

1. **Phase 0** — Review ISP ToS, survey neighbors (This week)
2. **Phase 1** — Order hardware (Next week)
3. **Phase 2-3** — Design architecture, configure router (Weeks 2-3)
4. **Phase 4** — Install antennas (Weeks 3-4)
5. **Phase 5-8** — Onboard neighbors, test, validate (Weeks 4-5)
6. **Phase 9-10** — Document, support, scale (Ongoing)

---

**Appendix: Quick Reference Commands**

```bash
# EdgeRouter CLI

# View system status
show system

# View interfaces
show interfaces

# View DHCP leases
show dhcp server leases

# View NAT translations
show nat translations

# View firewall rules
show firewall name all

# View traffic policies
show traffic-policy shaper all

# View bandwidth graphs (UNMS)
# Navigate to https://unms.ui.com

# Reboot router
reboot

# Reset to factory defaults
default-configuration write
```

**NanoStation CLI Commands:**

```bash
# View signal strength
iwconfig

# View wireless statistics
iwlist wlan0 scan

# Reboot
reboot

# Reset to factory defaults
cfgmtd -f /etc/default/origin.cfg -w /etc/config/ -n
reboot
```